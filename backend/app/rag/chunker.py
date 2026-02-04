"""
Text Chunker - Table-Aware Edition
===================================
Splits text into semantically meaningful chunks.

WHY CHUNKING:
    - Embeddings work best on complete thoughts, not raw character slices
    - Sentence-aware chunks preserve semantic meaning
    - Tables require special handling (never mix with paragraphs)

HOW IT WORKS:
    - Paragraphs → sentence-aware chunking (existing logic)
    - Tables → row-based chunking (1-5 rows per chunk)
    - Main entry: chunk_text_blocks() accepts dict from load_pdf()

WHERE USED:
    - Called by pipeline.py during PDF ingestion
"""

from app.core.logger import get_logger
import re

logger = get_logger(__name__)


# ============================================
# HELPER: SENTENCE SPLITTING
# ============================================

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using regex.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]


# ============================================
# PARAGRAPH CHUNKER (EXISTING LOGIC)
# ============================================

def chunk_text(
    text: str,
    max_chunk_chars: int = 1000,
    sentence_overlap: int = 2
) -> list[str]:
    """
    Split paragraph text into semantically meaningful chunks.
    
    WHY: Preserves sentence boundaries for better embeddings
    HOW: Groups sentences up to max_chunk_chars with overlap
    
    Args:
        text: Paragraph text to chunk
        max_chunk_chars: Maximum characters per chunk
        sentence_overlap: Number of sentences to overlap between chunks
        
    Returns:
        List of text chunks
    """
    sentences = split_into_sentences(text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if current_length + sentence_length > max_chunk_chars:
            chunks.append(" ".join(current_chunk))

            overlap_sentences = (
                current_chunk[-sentence_overlap:]
                if sentence_overlap > 0 else []
            )
            current_chunk = overlap_sentences.copy()
            current_length = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    logger.debug(
        f"Split paragraph into {len(chunks)} chunks "
        f"(max_chunk_chars={max_chunk_chars}, overlap={sentence_overlap})"
    )

    return chunks


# ============================================
# TABLE CHUNKER (NEW)
# ============================================

def chunk_table_rows(table_text: str, rows_per_chunk: int = 3) -> list[str]:
    """
    Split table text into row-based chunks.
    
    WHY: Tables have structured data - keep rows together
    HOW: Group 1-5 rows per chunk, never mix with paragraphs
    
    Args:
        table_text: Descriptive table text (e.g., "Row 1: A=1, B=2")
        rows_per_chunk: Number of rows to group together (default 3)
        
    Returns:
        List of table chunks
        
    EXAMPLE INPUT:
        "Table on page 1:
         Row 1: Name=John, Age=30
         Row 2: Name=Jane, Age=25
         Row 3: Name=Bob, Age=35"
         
    EXAMPLE OUTPUT:
        ["Table on page 1:\nRow 1: Name=John, Age=30\nRow 2: Name=Jane, Age=25",
         "Table on page 1:\nRow 3: Name=Bob, Age=35"]
    """
    lines = table_text.split('\n')
    
    if not lines:
        return []
    
    # First line is usually "Table on page X:"
    header_line = lines[0] if lines[0].startswith("Table") else ""
    data_lines = lines[1:] if header_line else lines
    
    # Filter out empty lines
    data_lines = [line for line in data_lines if line.strip()]
    
    if not data_lines:
        return []
    
    chunks = []
    
    # Group rows into chunks
    for i in range(0, len(data_lines), rows_per_chunk):
        chunk_rows = data_lines[i:i + rows_per_chunk]
        
        # Reconstruct chunk with header
        if header_line:
            chunk = header_line + "\n" + "\n".join(chunk_rows)
        else:
            chunk = "\n".join(chunk_rows)
        
        chunks.append(chunk)
    
    logger.debug(f"Split table into {len(chunks)} chunks ({rows_per_chunk} rows per chunk)")
    
    return chunks


# ============================================
# MAIN ENTRY POINT (NEW)
# ============================================

def chunk_text_blocks(
    content: dict,
    max_chunk_chars: int = 1000,
    sentence_overlap: int = 2,
    table_rows_per_chunk: int = 3
) -> list[str]:
    """
    Chunk both paragraphs and tables from PDF extraction.
    
    WHY: New main entry point that handles structured PDF content
    HOW:
        - Paragraphs → sentence-aware chunking
        - Tables → row-based chunking
        - Never mix table text with paragraph text
    
    Args:
        content: Dict with "paragraphs" and "tables" keys
        max_chunk_chars: Max chars for paragraph chunks
        sentence_overlap: Sentence overlap for paragraphs
        table_rows_per_chunk: Rows per table chunk
        
    Returns:
        List of all chunks (paragraphs + tables)
    """
    all_chunks = []
    
    # Process paragraphs
    paragraphs = content.get("paragraphs", [])
    for para in paragraphs:
        if para and para.strip():
            para_chunks = chunk_text(
                para, 
                max_chunk_chars=max_chunk_chars,
                sentence_overlap=sentence_overlap
            )
            all_chunks.extend(para_chunks)
    
    logger.info(f"Chunked {len(paragraphs)} paragraphs into {len(all_chunks)} chunks")
    
    # Process tables
    tables = content.get("tables", [])
    table_chunk_count = 0
    for table in tables:
        if table and table.strip():
            table_chunks = chunk_table_rows(table, rows_per_chunk=table_rows_per_chunk)
            all_chunks.extend(table_chunks)
            table_chunk_count += len(table_chunks)
    
    logger.info(f"Chunked {len(tables)} tables into {table_chunk_count} chunks")
    logger.info(f"Total chunks created: {len(all_chunks)}")
    
    return all_chunks
