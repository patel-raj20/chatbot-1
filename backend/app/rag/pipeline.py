"""
RAG Pipeline
============
Main pipeline for PDF ingestion and question answering using RAG.

RAG (Retrieval-Augmented Generation) FLOW:
    1. INGEST: PDF → Text → Chunks → Embeddings → Vector DB (Milvus)
    2. QUERY: Question → Embedding → Similar Chunks → LLM → Answer

WHY RAG:
    - Allows chatbot to answer from custom documents
    - More accurate than fine-tuning for specific content
    - Can update knowledge by uploading new PDFs
    
WHERE USED: Called by RAG routes for upload and ask operations
"""

from .pdf_loader import load_pdf
from .chunker import chunk_text
from .embedder import embed
from .collection import get_collection
from .retriever import retrieve
from app.core.logger import get_logger

logger = get_logger(__name__)


def ingest_pdf(pdf_path: str, source_file: str = "unknown", original_filename: str = "unknown") -> int:
    """
    Ingest PDF and store in vector database for semantic search.
    
    WHY: Converts PDF into searchable vector embeddings
    WHERE: Called when user uploads PDF via /rag/upload-pdf
    HOW:
        1. Extract text from PDF
        2. Split text into chunks (200 chars with 50 char overlap)
        3. Generate embeddings for each chunk (384-dim vectors)
        4. Store in Milvus vector database
    
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
        
        # STEP 1: Extract text from PDF
        text = load_pdf(pdf_path)
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # STEP 2: Split into chunks
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text extracted from PDF; ingestion skipped.")
        logger.info(f"Created {len(chunks)} text chunks")
        
        # STEP 3: Generate embeddings
        embeddings = embed(chunks)
        if not embeddings:
            raise ValueError("No embeddings generated from PDF text; ingestion skipped.")
        logger.debug(f"Generated {len(embeddings)} embeddings (384 dimensions each)")
        
        # STEP 4: Store in Milvus
        col = get_collection()
        # NOTE: Appending to collection, not clearing old data
        # This preserves all previously uploaded PDFs
        
        # Prepare metadata for each chunk
        source_files = [source_file] * len(chunks)
        original_filenames = [original_filename] * len(chunks)
        
        col.insert([chunks, embeddings, source_files, original_filenames])
        col.flush()
        logger.info(f"Successfully inserted {len(chunks)} chunks from {original_filename}")
        
        return len(chunks)
        
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
        2. Pass chunks as context to LLM (Ollama)
        3. LLM generates answer based on context
    
    Args:
        query: User's question
        
    Returns:
        Generated answer from LLM or fallback message
        
    FALLBACKS:
        - No chunks found → "No relevant information found"
        - Ollama unavailable → Return raw context chunks
    """
    # STEP 1: Retrieve relevant chunks
    chunks = retrieve(query)
    
    if not chunks:
        logger.warning(f"No relevant chunks found for query: '{query}'")
        return "I couldn't find relevant information in the uploaded documents. Please make sure you've uploaded a document first."
    
    # STEP 2: Combine chunks into context
    context = "\n\n".join(chunks)
    logger.debug(f"Combined {len(chunks)} chunks into context ({len(context)} chars)")
    
    # STEP 3: Generate answer using LLM
    try:
        from .ollama_client import generate_answer
        answer = generate_answer(context, query)
        return answer
    except Exception as e:
        logger.warning(f"Ollama LLM failed: {e}. Returning raw context.")
        # Fallback: Return context without LLM processing
        return f"Based on the documents:\n\n{context}\n\n(Note: Ollama LLM is not available for advanced answering. Install Ollama to enable AI-powered responses)"
