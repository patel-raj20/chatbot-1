"""
RAG Pipeline
============
Main pipeline for PDF ingestion and question answering using RAG.

RAG (Retrieval-Augmented Generation) FLOW:
    1. INGEST: PDF → Markdown → Structure-Aware Chunks → Embeddings → Vector DB (Milvus)
    2. QUERY: Question → Embedding → Similar Chunks → LLM → Answer

WHY RAG:
    - Allows chatbot to answer from custom documents
    - More accurate than fine-tuning for specific content
    - Can update knowledge by uploading new PDFs
    
WHERE USED: Called by RAG routes for upload and ask operations
"""

from .pdf_loader import load_pdf
from .chunker import chunk_markdown
from .embedder import embed
from .collection import get_collection
from .retriever import retrieve
from .reranker import rerank
from .config import RETRIEVAL_TOP_K, RERANKER_TOP_N
from app.core.logger import get_logger

logger = get_logger(__name__)


def ingest_pdf(pdf_path: str, source_file: str = "unknown", original_filename: str = "unknown") -> int:
    """
    Ingest PDF and store in vector database for semantic search.
    
    WHY: Converts PDF into searchable vector embeddings with structural metadata
    WHERE: Called when user uploads PDF via /rag/upload-pdf
    HOW:
        1. Extract structured content from PDF (Docling → Markdown)
        2. Split markdown into structure-aware chunks (sections, paragraphs, tables)
        3. Generate embeddings for each chunk (768-dim vectors)
        4. Store in Milvus with metadata (chunk_type, heading, pages)
    
    Args:
        pdf_path: Local path to PDF file
        source_file: MinIO object name for tracking
        original_filename: Original filename from user
        
    Returns:
        Number of chunks created
        
    Raises:
        ValueError: If PDF has no extractable text
    """
    try:
        logger.info(f"Starting PDF ingestion: {original_filename} (MinIO: {source_file})")
        
        # STEP 1: Extract structured content from PDF
        pdf_result = load_pdf(pdf_path)
        markdown = pdf_result['markdown']
        total_pages = pdf_result['total_pages']
        logger.info(f"Extracted {len(markdown)} characters from {total_pages} pages")
        
        # STEP 2: Split into structure-aware chunks
        chunk_data = chunk_markdown(markdown, total_pages)
        if not chunk_data:
            raise ValueError("No text extracted from PDF; ingestion skipped.")
        logger.info(f"Created {len(chunk_data)} structure-aware chunks")
        
        # STEP 3: Extract content for embeddings
        chunk_contents = [chunk['content'] for chunk in chunk_data]
        
        # STEP 4: Generate embeddings
        embeddings = embed(chunk_contents)
        if not embeddings:
            raise ValueError("No embeddings generated from PDF text; ingestion skipped.")
        logger.debug(f"Generated {len(embeddings)} embeddings (768 dimensions each)")
        
        # STEP 5: Store in Milvus with metadata
        col = get_collection()
        # NOTE: Appending to collection, not clearing old data
        # This preserves all previously uploaded PDFs
        
        # Prepare data for insertion
        contents = [chunk['content'] for chunk in chunk_data]
        source_files = [source_file] * len(chunk_data)
        original_filenames = [original_filename] * len(chunk_data)
        chunk_types = [chunk['chunk_type'] for chunk in chunk_data]
        headings = [chunk['heading'] for chunk in chunk_data]
        page_starts = [chunk['page_start'] for chunk in chunk_data]
        page_ends = [chunk['page_end'] for chunk in chunk_data]
        
        # Insert with all metadata fields
        col.insert([
            contents,
            embeddings,
            source_files,
            original_filenames,
            chunk_types,
            headings,
            page_starts,
            page_ends
        ])
        col.flush()
        logger.info(f"Successfully inserted {len(chunk_data)} chunks from {original_filename}")
        
        return len(chunk_data)
        
    except Exception as e:
        logger.error(f"PDF ingestion failed: {type(e).__name__}: {str(e)}")
        raise


def ask_question(query: str) -> str:
    """
    Answer question using RAG (Retrieval-Augmented Generation).
    
    WHY: Provides accurate answers from uploaded documents
    WHERE: Called by /rag/ask endpoint when user asks question
    HOW:
        1. Retrieve relevant chunks from vector database
        2. Pass chunks as context to LLM (Groq)
        3. LLM generates answer based on context
    
    Args:
        query: User's question
        
    Returns:
        Generated answer from LLM or fallback message
        
    FALLBACKS:
        - No chunks found → "No relevant information found"
        - Groq unavailable → Return raw context chunks
    """
    # STEP 1: Retrieve relevant chunks (over-fetch for reranking)
    chunks = retrieve(query, top_k=RETRIEVAL_TOP_K)
    
    if not chunks:
        logger.warning(f"No relevant chunks found for query: '{query}'")
        return "I couldn't find relevant information in the uploaded documents. Please make sure you've uploaded a document first."
    
    # STEP 1b: Rerank to keep the most relevant chunks
    chunks = rerank(query, chunks, top_n=RERANKER_TOP_N)
    
    # STEP 2: Combine chunks into context
    context = "\n\n".join(chunks)
    logger.debug(f"Combined {len(chunks)} chunks into context ({len(context)} chars)")
    
    # STEP 3: Generate answer using LLM
    try:
        from .ollama_client import generate_answer
        answer = generate_answer(context, query)
        return answer
    except Exception as e:
        logger.warning(f"Groq LLM failed: {e}. Returning raw context.")
        # Fallback: Return context without LLM processing
        return f"Based on the documents:\n\n{context}\n\n(Note: Groq LLM is not available. Please check your GROQ_API_KEY in .env file)"
