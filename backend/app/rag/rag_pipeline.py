from .pdf_loader import load_pdf
from .chunker import chunk_text
from .embedder import embed
from .collection import get_collection
from .retriever import retrieve

def ingest_pdf(pdf_path: str):
    try:
        print(f"[INGEST] Starting ingestion of {pdf_path}")
        text = load_pdf(pdf_path)
        print(f"[INGEST] Loaded text: {len(text)} characters")
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text extracted from PDF; ingestion skipped.")
        print(f"[INGEST] Created {len(chunks)} chunks")
        embeddings = embed(chunks)
        if not embeddings:
            raise ValueError("No embeddings generated from PDF text; ingestion skipped.")
        print(f"[INGEST] Generated {len(embeddings)} embeddings")

        col = get_collection()
        col.delete(expr="id >= 0")  # clear old data
        print("[INGEST] Cleared collection")

        col.insert([chunks, embeddings])
        col.flush()
        print("[INGEST] Successfully inserted and flushed to Milvus")
    except Exception as e:
        print(f"[INGEST ERROR] {type(e).__name__}: {str(e)}")
        raise

def ask_question(query: str):
    chunks = retrieve(query)
    if not chunks:
        return "I couldn't find relevant information in the uploaded documents. Please make sure you've uploaded a document first."

    context = "\n\n".join(chunks)
    print(f"DEBUG - Retrieved {len(chunks)} chunks for query: {query}")
    print(f"DEBUG - Context preview: {context[:200]}...")
    
    # Try to use Ollama if available, otherwise return context
    try:
        from .ollama_client import generate_answer
        return generate_answer(context, query)
    except Exception as e:
        print(f"ERROR - Ollama failed: {e}")
        # If Ollama is not available, return the relevant chunks
        return f"Based on the documents:\n\n{context}\n\n(Note: Ollama LLM is not available for advanced answering. Install Ollama to enable AI-powered responses)"
