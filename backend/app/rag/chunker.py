"""
Text Chunker
============
Splits long text into semantically meaningful chunks.

WHY CHUNKING:
    - Embeddings work best on complete thoughts, not raw character slices
    - Sentence-aware chunks preserve semantic meaning
    - Tables require special handling (row → sentence)

HOW IT WORKS:
    - Detects table-like text (OCR-safe)
    - Table text → fact-based sentence chunks
    - Paragraph text → sentence-aware chunking (original logic)

WHERE USED:
    - Called by pipeline.py during PDF ingestion
"""

from app.core.logger import get_logger
import re

logger = get_logger(__name__)


# -----------------------------
# Sentence splitting (UNCHANGED)
# -----------------------------
def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using regex (OCR-safe).
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 0]


# -----------------------------
# TABLE DETECTION (ROBUST)
# -----------------------------
def is_table_like(text: str) -> bool:
    """
    Detect table-like content even when OCR flattens rows.

    Heuristics:
        - High numeric token ratio
        - Low sentence punctuation
    """
    tokens = text.split()
    if len(tokens) < 15:
        return False

    numeric_tokens = sum(
        any(char.isdigit() for char in token)
        for token in tokens
    )

    punctuation_count = sum(text.count(p) for p in ".!?")

    # Table if many numbers, few sentence endings
    return (numeric_tokens / len(tokens) > 0.3) and punctuation_count < 3


# -----------------------------
# TABLE NORMALIZATION
# -----------------------------
def table_to_sentences(text: str) -> list[str]:
    """
    Convert table-like OCR text into sentence-like chunks.

    Strategy:
        - Normalize spacing
        - Split around numeric boundaries
        - Each output = one retrievable fact
    """
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Split where numbers usually end facts (very OCR-friendly)
    parts = re.split(r"(?<=\d)", text)

    sentences = [
        part.strip() + "."
        for part in parts
        if len(part.strip()) > 20
    ]

    return sentences


# -----------------------------
# MAIN CHUNK FUNCTION
# -----------------------------
def chunk_text(
    text: str,
    max_chunk_chars: int = 1000,
    sentence_overlap: int = 2
) -> list[str]:
    """
    Split text into semantically meaningful chunks.

    Adaptive behavior:
        - Table text → row/fact-based chunks
        - Paragraph text → sentence-aware chunks
    """

    # 🔥 TABLE PATH
    if is_table_like(text):
        logger.debug("Table-like text detected → using table normalization")
        return table_to_sentences(text)

    # ✅ PARAGRAPH PATH (ORIGINAL LOGIC)
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
        f"Split text into {len(chunks)} chunks "
        f"(max_chunk_chars={max_chunk_chars}, overlap={sentence_overlap})"
    )

    return chunks
