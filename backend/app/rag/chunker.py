"""
Structure-Aware Markdown Chunker
=================================
Splits markdown text into chunks based on document structure (sections, paragraphs, tables).

STRATEGY:
    - Structure-first chunking: Respects heading boundaries
    - Paragraph grouping: Combines paragraphs within token limits
    - Atomic tables: Never splits table rows
    - Metadata extraction: Tracks chunk type, heading, page numbers

WHY THIS WORKS:
    - Preserves document context and hierarchy
    - Tables remain complete and usable
    - Each chunk has meaningful boundaries
    - Better for semantic embeddings and RAG accuracy

WHERE USED: Called by pipeline.py during PDF ingestion
"""

from typing import List, Dict, Any
import re
from app.core.logger import get_logger

logger = get_logger(__name__)

# Import configuration
try:
    from .config import TARGET_CHUNK_TOKENS, MAX_CHUNK_TOKENS, MIN_CHUNK_TOKENS, ENABLE_TABLE_ATOMIC
except ImportError:
    TARGET_CHUNK_TOKENS = 500
    MAX_CHUNK_TOKENS = 800
    MIN_CHUNK_TOKENS = 30  # Reduced from 100 to preserve small but meaningful sections
    ENABLE_TABLE_ATOMIC = True


def chunk_markdown(markdown: str, total_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Structure-aware chunking: Split markdown by document structure.
    
    ALGORITHM:
        1. Parse markdown into elements (headings, paragraphs, tables)
        2. Start new chunk at each heading
        3. Accumulate paragraphs until token limit
        4. Keep tables as standalone chunks
        5. Extract metadata for each chunk
    
    Args:
        markdown: Full document in markdown format
        total_pages: Total page count from PDF
        
    Returns:
        List of dicts with:
            - content: Chunk text in markdown
            - chunk_type: 'paragraph', 'table', or 'mixed'
            - heading: Last heading before chunk
            - page_start: First page number
            - page_end: Last page number
    """
    logger.info(f"Starting structure-aware chunking for {len(markdown)} characters")
    
    # Parse markdown into structured elements
    elements = _parse_markdown_elements(markdown)
    logger.info(f"Parsed {len(elements)} markdown elements")
    
    # If no meaningful elements found (plain text), use paragraph-based chunking
    paragraph_elements = [e for e in elements if e['type'] == 'paragraph']
    if len(paragraph_elements) == 0 and len(elements) == 0:
        logger.warning("No structured elements found, using plain text chunking")
        return _chunk_plain_text(markdown, total_pages)
    
    # Create chunks from elements
    chunks = _create_chunks_from_elements(elements, total_pages)
    
    # If no chunks created (all content was too small), create at least one chunk
    if not chunks and markdown.strip():
        logger.warning("No chunks created from elements, creating single chunk from all content")
        chunks = [{
            'content': markdown.strip(),
            'chunk_type': 'paragraph',
            'heading': '',
            'page_start': 1,
            'page_end': total_pages
        }]
    
    logger.info(f"Created {len(chunks)} structure-aware chunks")
    
    # Log statistics
    if chunks:
        avg_tokens = sum(_estimate_tokens(c['content']) for c in chunks) / len(chunks)
        table_chunks = sum(1 for c in chunks if c['chunk_type'] == 'table')
        logger.info(f"Average tokens per chunk: {avg_tokens:.1f}, Table chunks: {table_chunks}")
    
    return chunks


def _chunk_plain_text(text: str, total_pages: int = 1) -> List[Dict[str, Any]]:
    """
    Fallback chunking for plain text without markdown structure.
    Used when OCR produces unstructured text.
    
    Strategy: Split by paragraphs (double newlines) and group by token limit.
    """
    logger.info(f"Using plain text chunking for {len(text)} characters")
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        return []
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = _estimate_tokens(para)
        
        # If single paragraph is too large, split it
        if para_tokens > MAX_CHUNK_TOKENS:
            # Save current chunk first
            if current_chunk:
                chunks.append({
                    'content': '\n\n'.join(current_chunk),
                    'chunk_type': 'paragraph',
                    'heading': '',
                    'page_start': 1,
                    'page_end': total_pages
                })
                current_chunk = []
                current_tokens = 0
            
            # Split large paragraph by sentences
            sentences = re.split(r'([.!?]+\s+)', para)
            sentence_chunk = []
            sentence_tokens = 0
            
            for i in range(0, len(sentences), 2):
                sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
                sent_tokens = _estimate_tokens(sentence)
                
                if sentence_tokens + sent_tokens > MAX_CHUNK_TOKENS and sentence_chunk:
                    chunks.append({
                        'content': ''.join(sentence_chunk),
                        'chunk_type': 'paragraph',
                        'heading': '',
                        'page_start': 1,
                        'page_end': total_pages
                    })
                    sentence_chunk = [sentence]
                    sentence_tokens = sent_tokens
                else:
                    sentence_chunk.append(sentence)
                    sentence_tokens += sent_tokens
            
            if sentence_chunk:
                chunks.append({
                    'content': ''.join(sentence_chunk),
                    'chunk_type': 'paragraph',
                    'heading': '',
                    'page_start': 1,
                    'page_end': total_pages
                })
        
        elif current_tokens + para_tokens > MAX_CHUNK_TOKENS:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append({
                    'content': '\n\n'.join(current_chunk),
                    'chunk_type': 'paragraph',
                    'heading': '',
                    'page_start': 1,
                    'page_end': total_pages
                })
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            # Add to current chunk
            current_chunk.append(para)
            current_tokens += para_tokens
    
    # Save final chunk
    if current_chunk:
        chunks.append({
            'content': '\n\n'.join(current_chunk),
            'chunk_type': 'paragraph',
            'heading': '',
            'page_start': 1,
            'page_end': total_pages
        })
    
    logger.info(f"Created {len(chunks)} plain text chunks")
    return chunks


def _parse_markdown_elements(markdown: str) -> List[Dict[str, Any]]:
    """
    Parse markdown into structured elements with robust paragraph detection.
    Detects:
    - Markdown headings (# ## ###)
    - Numbered sections (1. 2. 3.) as pseudo-headings
    - Regular paragraphs
    - Tables
    
    Returns list of elements with:
        - type: 'heading', 'paragraph', 'table', 'page_marker'
        - content: The text content
        - level: Heading level (1-6) for headings
        - page: Page number (from markers)
    """
    elements = []
    lines = markdown.split('\n')
    
    current_paragraph = []
    current_table = []
    in_table = False
    current_page = 1
    empty_line_count = 0
    
    def save_paragraph():
        """Helper to save current paragraph if it has content."""
        if current_paragraph:
            content = '\n'.join(current_paragraph).strip()
            if content:  # Only save non-empty paragraphs
                elements.append({
                    'type': 'paragraph',
                    'content': content,
                    'page': current_page
                })
                logger.debug(f"Saved paragraph: {len(content)} chars on page {current_page}")
            current_paragraph.clear()
    
    def save_table():
        """Helper to save current table if it has content."""
        if current_table:
            content = '\n'.join(current_table).strip()
            if content:
                elements.append({
                    'type': 'table',
                    'content': content,
                    'page': current_page
                })
                logger.debug(f"Saved table: {len(content)} chars on page {current_page}")
            current_table.clear()
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check for page marker
        page_match = re.match(r'<!--\s*page:(\d+)\s*-->', line_stripped)
        if page_match:
            current_page = int(page_match.group(1))
            elements.append({
                'type': 'page_marker',
                'content': line_stripped,
                'page': current_page
            })
            continue
        
        # Check for markdown heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
        if heading_match:
            # Save any accumulated content
            save_paragraph()
            save_table()
            in_table = False
            empty_line_count = 0
            
            # Add heading
            level = len(heading_match.group(1))
            elements.append({
                'type': 'heading',
                'content': heading_match.group(2),
                'level': level,
                'page': current_page
            })
            logger.debug(f"Found heading level {level}: {heading_match.group(2)[:50]}")
            continue
        
        # Check for numbered section (e.g., "1. Engineering Knowledge")
        # This helps chunk documents that lack markdown formatting
        numbered_section_match = re.match(r'^(\d{1,2}\.\s+[A-Z][^\n]{10,80})$', line_stripped)
        if numbered_section_match:
            # Save any accumulated content
            save_paragraph()
            save_table()
            in_table = False
            empty_line_count = 0
            
            # Add as pseudo-heading (level 2)
            elements.append({
                'type': 'heading',
                'content': numbered_section_match.group(1),
                'level': 2,
                'page': current_page
            })
            logger.debug(f"Found numbered section: {numbered_section_match.group(1)[:50]}")
            continue
        
        # Check for table row (must have | and not be in code block)
        if '|' in line_stripped and line_stripped.count('|') >= 2:
            if not in_table:
                # Starting a table - save current paragraph
                save_paragraph()
                in_table = True
                empty_line_count = 0
            
            current_table.append(line)
            continue
        
        # End table if we were in one
        if in_table:
            save_table()
            in_table = False
            empty_line_count = 0
        
        # Handle paragraph text
        if line_stripped:  # Non-empty line
            # If we've seen empty line(s) before this, save the previous paragraph
            if empty_line_count >= 1 and current_paragraph:
                save_paragraph()
            # Add to current paragraph
            current_paragraph.append(line)
            empty_line_count = 0
        else:  # Empty line
            empty_line_count += 1
    
    # Save any remaining content
    save_paragraph()
    save_table()
    
    logger.info(f"Parsed elements: {len([e for e in elements if e['type']=='paragraph'])} paragraphs, "
                f"{len([e for e in elements if e['type']=='table'])} tables, "
                f"{len([e for e in elements if e['type']=='heading'])} headings")
    
    return elements


def _create_chunks_from_elements(elements: List[Dict[str, Any]], total_pages: int) -> List[Dict[str, Any]]:
    """
    Create chunks from parsed elements following structure-aware rules.
    
    Rules:
        1. Start new chunk at each heading
        2. Accumulate paragraphs until token limit
        3. Keep tables as standalone chunks
        4. Track metadata (heading, pages, chunk type)
    """
    chunks = []
    current_chunk_content = []
    current_heading = ""
    current_page_start = 1
    current_page_end = 1
    chunk_types = []
    
    def finalize_chunk():
        """Helper to save current chunk."""
        if not current_chunk_content:
            return
        
        content = '\n\n'.join(current_chunk_content).strip()
        if not content:  # Skip empty chunks
            current_chunk_content.clear()
            chunk_types.clear()
            return
        
        tokens = _estimate_tokens(content)
        
        # ALWAYS save chunks with content - never lose information
        # Only warn if it's smaller than ideal size
        if tokens < MIN_CHUNK_TOKENS:
            logger.debug(f"Small chunk created: {tokens} tokens (below recommended {MIN_CHUNK_TOKENS})")
        
        # Determine chunk type
        if 'table' in chunk_types and 'paragraph' in chunk_types:
            chunk_type = 'mixed'
        elif 'table' in chunk_types:
            chunk_type = 'table'
        else:
            chunk_type = 'paragraph'
        
        chunk_data = {
            'content': content,
            'chunk_type': chunk_type,
            'heading': current_heading,
            'page_start': current_page_start,
            'page_end': current_page_end
        }
        chunks.append(chunk_data)
        logger.debug(f"Created chunk #{len(chunks)}: {tokens} tokens, type={chunk_type}, "
                    f"pages={current_page_start}-{current_page_end}")
        
        current_chunk_content.clear()
        chunk_types.clear()
    
    for element in elements:
        elem_type = element['type']
        elem_page = element.get('page', 1)
        
        # Update page tracking
        if elem_type == 'page_marker':
            current_page_end = elem_page
            continue
        
        # Heading: finalize current chunk and start new section
        if elem_type == 'heading':
            finalize_chunk()
            current_heading = element['content']
            current_page_start = elem_page
            current_page_end = elem_page
            # Add heading to chunk content (use proper markdown)
            if element['level'] <= 6:
                current_chunk_content.append('#' * element['level'] + ' ' + element['content'])
            else:
                current_chunk_content.append('## ' + element['content'])  # Default to level 2
            continue
        
        # Table: handle based on atomic table setting
        if elem_type == 'table':
            table_content = element['content']
            
            if ENABLE_TABLE_ATOMIC:
                # Finalize current chunk before table
                finalize_chunk()
                
                # Add table with heading as context
                if current_heading:
                    table_content = f"## {current_heading}\n\n{table_content}"
                
                chunks.append({
                    'content': table_content,
                    'chunk_type': 'table',
                    'heading': current_heading,
                    'page_start': elem_page,
                    'page_end': elem_page
                })
                logger.debug(f"Created standalone table chunk on page {elem_page}")
                
                # Reset for next chunk
                current_page_start = elem_page
                current_page_end = elem_page
            else:
                # Add table to current chunk
                current_chunk_content.append(table_content)
                chunk_types.append('table')
                current_page_end = elem_page
            continue
        
        # Paragraph: accumulate until token limit
        if elem_type == 'paragraph':
            para_content = element['content']
            
            # Check if adding this paragraph exceeds limit
            test_content = '\n\n'.join(current_chunk_content + [para_content])
            test_tokens = _estimate_tokens(test_content)
            
            if test_tokens > MAX_CHUNK_TOKENS and current_chunk_content:
                # Finalize current chunk before adding this paragraph
                finalize_chunk()
                current_page_start = elem_page
            
            current_chunk_content.append(para_content)
            chunk_types.append('paragraph')
            current_page_end = elem_page
            
            # Check if we've reached target size (but allow continuing until MAX)
            current_tokens = _estimate_tokens('\n\n'.join(current_chunk_content))
            if current_tokens >= TARGET_CHUNK_TOKENS and current_tokens < MAX_CHUNK_TOKENS:
                # Can finalize here for optimal size, but continue if next para fits
                pass
    
    # IMPORTANT: Finalize any remaining chunk at the end
    finalize_chunk()
    
    # Log summary with coverage
    if chunks:
        total_tokens = sum(_estimate_tokens(c['content']) for c in chunks)
        logger.info(f"Chunk summary: {len(chunks)} chunks, {total_tokens} total tokens, "
                   f"avg {total_tokens/len(chunks):.0f} tokens/chunk")
    
    return chunks


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count (roughly 1 token ≈ 4 characters for English).
    
    This is a simple approximation. For exact token counts, use tiktoken or similar.
    """
    return len(text) // 4
