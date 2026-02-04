"""
PDF Text Loader - Table-Aware Edition
======================================
Extracts text from PDF files with table detection support.

FEATURES:
    1. PDF type detection (digital vs scanned)
    2. Digital PDFs: Use pdfplumber for text + tables
    3. Scanned PDFs: Use OCR with layout-based table detection
    4. Unified output structure for both paths
    
ARCHITECTURE:
    - detect_pdf_type() → determines digital or scanned
    - extract_digital_pdf() → pdfplumber path
    - extract_scanned_pdf() → OCR + layout analysis path
    - load_pdf() → main entry point
    
WHERE USED: Called by pipeline.py during PDF ingestion
"""

import pdfplumber
import os
from app.core.logger import get_logger

logger = get_logger(__name__)

# OCR imports with fallback
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import cv2
    import numpy as np
    
    # Auto-detect Tesseract installation on Windows
    if os.name == 'nt':  # Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\stadmin\AppData\Local\Tesseract-OCR\tesseract.exe',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Found Tesseract at: {path}")
                break
    
    OCR_AVAILABLE = True
    logger.info("OCR libraries available")
except ImportError:
    OCR_AVAILABLE = False
    logger.info("OCR libraries not available. Install pytesseract, pdf2image, Pillow, opencv-python for OCR support.")

# Import OCR configuration
try:
    from .config import OCR_ENABLED, OCR_LANGUAGE, OCR_DPI
except ImportError:
    OCR_ENABLED = True
    OCR_LANGUAGE = "eng"
    OCR_DPI = 300


# ============================================
# STEP 1: PDF TYPE DETECTION
# ============================================

def detect_pdf_type(file_path: str) -> str:
    """
    Detect if PDF is digital (text-based) or scanned (image-based).
    
    WHY: Different extraction strategies for different PDF types
    HOW: Try extracting text from first page; if >50 chars → digital
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        "digital" or "scanned"
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                logger.warning("PDF has no pages, treating as scanned")
                return "scanned"
            
            # Test first page
            first_page_text = pdf.pages[0].extract_text()
            text_length = len(first_page_text) if first_page_text else 0
            
            if text_length > 50:
                logger.info(f"PDF type: DIGITAL (extracted {text_length} chars from page 1)")
                return "digital"
            else:
                logger.info(f"PDF type: SCANNED (only {text_length} chars from page 1)")
                return "scanned"
    except Exception as e:
        logger.warning(f"PDF type detection failed: {e}. Defaulting to scanned.")
        return "scanned"


# ============================================
# STEP 2: DIGITAL PDF PATH
# ============================================

def extract_digital_pdf(file_path: str) -> dict:
    """
    Extract text and tables from digital PDF using pdfplumber.
    
    WHY: pdfplumber has built-in table detection - no need for heuristics
    HOW: 
        - Extract paragraphs using extract_text()
        - Extract tables using extract_tables()
        - Convert tables to descriptive row-wise text
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        {
            "paragraphs": [text_block1, text_block2, ...],
            "tables": [table_desc1, table_desc2, ...]
        }
    """
    paragraphs = []
    tables = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logger.debug(f"Processing digital page {page_num}/{len(pdf.pages)}")
                
                # Extract paragraph text
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    paragraphs.append(page_text.strip())
                
                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    logger.debug(f"Found {len(page_tables)} tables on page {page_num}")
                    
                    for table_idx, table in enumerate(page_tables, 1):
                        if not table or len(table) < 2:  # Skip empty or single-row tables
                            continue
                        
                        # Convert table to descriptive text
                        table_text = _convert_table_to_text(table, page_num, table_idx)
                        if table_text:
                            tables.append(table_text)
        
        logger.info(f"Digital PDF: {len(paragraphs)} paragraph blocks, {len(tables)} tables")
        return {"paragraphs": paragraphs, "tables": tables}
        
    except Exception as e:
        logger.error(f"Digital PDF extraction failed: {e}")
        raise


def _convert_table_to_text(table: list, page_num: int, table_idx: int) -> str:
    """
    Convert pdfplumber table to descriptive row-wise text.
    
    Args:
        table: List of rows (each row is list of cells)
        page_num: Page number for reference
        table_idx: Table index on page
        
    Returns:
        Descriptive text like:
        "Table on page 1:
         Row 1: Name=John, Age=30, Dept=Sales
         Row 2: Name=Jane, Age=25, Dept=HR"
    """
    if not table or len(table) < 2:
        return ""
    
    # First row is usually header
    header = table[0]
    data_rows = table[1:]
    
    # Clean header (remove None values)
    header = [str(h).strip() if h else f"Col{i+1}" for i, h in enumerate(header)]
    
    # Build descriptive text
    lines = [f"Table on page {page_num}:"]
    
    for row_idx, row in enumerate(data_rows, 1):
        # Skip empty rows
        if not row or all(cell is None or str(cell).strip() == "" for cell in row):
            continue
        
        # Create "header=value" pairs
        row_parts = []
        for col_idx, (col_name, cell_value) in enumerate(zip(header, row)):
            if cell_value is not None and str(cell_value).strip():
                row_parts.append(f"{col_name}={str(cell_value).strip()}")
        
        if row_parts:
            lines.append(f"Row {row_idx}: {', '.join(row_parts)}")
    
    return "\n".join(lines) if len(lines) > 1 else ""


# ============================================
# STEP 3: SCANNED PDF PATH (OCR)
# ============================================


def preprocess_image_for_ocr(image):
    """
    Enhance image quality for better OCR accuracy.
    
    WHY: Raw images often have noise, varying contrast
    HOW: Applies grayscale, thresholding, and denoising
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image
    """
    try:
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        return Image.fromarray(gray)
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original image.")
        return image


def extract_scanned_pdf(file_path: str) -> dict:
    """
    Extract text and tables from scanned PDF using OCR + layout analysis.
    
    WHY: Scanned PDFs contain images, not extractable text
    HOW:
        1. Convert PDF pages to images
        2. Use pytesseract.image_to_data() for OCR with bounding boxes
        3. Group words by blocks
        4. Detect TABLE vs PARAGRAPH based on layout alignment
        5. Convert both to text
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        {
            "paragraphs": [text_block1, text_block2, ...],
            "tables": [table_desc1, table_desc2, ...]
        }
    """
    if not OCR_AVAILABLE:
        raise Exception("OCR libraries not installed. Install: pip install pytesseract pdf2image Pillow opencv-python")
    
    paragraphs = []
    tables = []
    
    try:
        # Convert PDF to images
        poppler_path = _find_poppler_path()
        logger.info(f"Converting PDF to images...")
        
        if poppler_path:
            images = convert_from_path(file_path, dpi=OCR_DPI, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path, dpi=OCR_DPI)
        
        logger.info(f"Processing {len(images)} pages with OCR...")
        
        for page_num, image in enumerate(images, 1):
            logger.debug(f"OCR on page {page_num}/{len(images)}")
            
            # Preprocess image
            processed_image = preprocess_image_for_ocr(image)
            
            # Perform OCR with layout data
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                lang=OCR_LANGUAGE,
                output_type=pytesseract.Output.DICT
            )
            
            # Group OCR data by blocks and detect type
            blocks = _group_ocr_by_blocks(ocr_data)
            
            for block in blocks:
                block_type = _detect_block_type(block)
                
                if block_type == "table":
                    table_text = _convert_ocr_table_to_text(block, page_num)
                    if table_text:
                        tables.append(table_text)
                else:  # paragraph
                    para_text = _convert_ocr_paragraph_to_text(block)
                    if para_text:
                        paragraphs.append(para_text)
        
        logger.info(f"Scanned PDF: {len(paragraphs)} paragraph blocks, {len(tables)} tables")
        return {"paragraphs": paragraphs, "tables": tables}
        
    except Exception as e:
        logger.error(f"Scanned PDF extraction failed: {e}")
        raise


def _find_poppler_path():
    """Find Poppler installation on Windows."""
    poppler_path = os.getenv('POPPLER_PATH')
    if poppler_path and os.path.exists(poppler_path):
        logger.info(f"Using Poppler from POPPLER_PATH: {poppler_path}")
        return poppler_path
    
    if os.name == 'nt':  # Windows
        possible_paths = [
            os.path.expanduser(r"~\poppler\poppler-24.02.0\Library\bin"),
            r'C:\Users\stadmin\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin',
            r'C:\Program Files\poppler\Library\bin',
            r'C:\poppler\Library\bin',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Poppler at: {path}")
                return path
    
    return None


def _group_ocr_by_blocks(ocr_data: dict) -> list:
    """
    Group OCR words by block numbers.
    
    Args:
        ocr_data: Output from pytesseract.image_to_data()
        
    Returns:
        List of blocks, each containing words with positions
    """
    blocks = {}
    
    for i in range(len(ocr_data['text'])):
        word = ocr_data['text'][i].strip()
        if not word:  # Skip empty words
            continue
        
        block_num = ocr_data['block_num'][i]
        
        if block_num not in blocks:
            blocks[block_num] = []
        
        blocks[block_num].append({
            'text': word,
            'left': ocr_data['left'][i],
            'top': ocr_data['top'][i],
            'width': ocr_data['width'][i],
            'height': ocr_data['height'][i],
            'line_num': ocr_data['line_num'][i]
        })
    
    return list(blocks.values())


def _detect_block_type(block: list) -> str:
    """
    Detect if block is a TABLE or PARAGRAPH based on layout.
    
    TABLE INDICATORS:
        - Multiple lines with similar X-start positions (alignment)
        - Similar word counts per line (columnar structure)
        
    Args:
        block: List of word dictionaries with position data
        
    Returns:
        "table" or "paragraph"
    """
    if len(block) < 6:  # Too small to be a table
        return "paragraph"
    
    # Group words by line
    lines = {}
    for word in block:
        line_num = word['line_num']
        if line_num not in lines:
            lines[line_num] = []
        lines[line_num].append(word)
    
    if len(lines) < 3:  # Tables need at least 3 rows
        return "paragraph"
    
    # Check for alignment (similar X-start positions)
    line_x_starts = []
    word_counts = []
    
    for line_words in lines.values():
        if len(line_words) >= 2:  # Need multiple columns
            # Get X positions of words in this line
            x_positions = sorted([w['left'] for w in line_words])
            line_x_starts.append(x_positions[0])  # Leftmost position
            word_counts.append(len(line_words))
    
    if len(line_x_starts) < 3:
        return "paragraph"
    
    # Check alignment: X-starts should be within ±15px
    x_variance = max(line_x_starts) - min(line_x_starts)
    
    # Check word count consistency: similar number of words per line
    avg_word_count = sum(word_counts) / len(word_counts)
    word_count_variance = sum(abs(c - avg_word_count) for c in word_counts) / len(word_counts)
    
    # Decision: aligned + consistent word counts = TABLE
    if x_variance < 15 and word_count_variance < 2.0:
        return "table"
    
    return "paragraph"


def _convert_ocr_table_to_text(block: list, page_num: int) -> str:
    """
    Convert OCR-detected table block to descriptive text.
    
    Args:
        block: List of word dictionaries
        page_num: Page number
        
    Returns:
        Descriptive text like "Row 1: word1, word2, word3"
    """
    # Group by lines
    lines = {}
    for word in block:
        line_num = word['line_num']
        if line_num not in lines:
            lines[line_num] = []
        lines[line_num].append(word)
    
    # Sort lines by line number
    sorted_lines = [lines[ln] for ln in sorted(lines.keys())]
    
    # Convert to text
    result = [f"Table on page {page_num}:"]
    
    for row_idx, line_words in enumerate(sorted_lines, 1):
        # Sort words by X position (left to right)
        line_words.sort(key=lambda w: w['left'])
        words = [w['text'] for w in line_words]
        result.append(f"Row {row_idx}: {', '.join(words)}")
    
    return "\n".join(result)


def _convert_ocr_paragraph_to_text(block: list) -> str:
    """
    Convert OCR-detected paragraph block to plain text.
    
    Args:
        block: List of word dictionaries
        
    Returns:
        Plain text with words joined by spaces
    """
    # Sort by line number, then by X position
    sorted_words = sorted(block, key=lambda w: (w['line_num'], w['left']))
    words = [w['text'] for w in sorted_words]
    text = ' '.join(words).strip()
    
    # Only return if meaningful (>20 chars)
    return text if len(text) > 20 else ""


# ============================================
# STEP 4: MAIN ENTRY POINT
# ============================================

def load_pdf(file_path: str) -> dict:
    """
    Load and extract text from PDF with table-aware processing.
    
    WHY: Handles both digital and scanned PDFs with table detection
    WHERE: Called by pipeline.py during PDF ingestion
    HOW: 
        1. Detect PDF type (digital or scanned)
        2. Route to appropriate extraction method
        3. Return unified structure
    
    Args:
        file_path: Absolute path to PDF file
        
    Returns:
        {
            "paragraphs": [text_block1, text_block2, ...],
            "tables": [table_desc1, table_desc2, ...]
        }
    """
    logger.info(f"Loading PDF: {file_path}")
    
    # Step 1: Detect PDF type
    pdf_type = detect_pdf_type(file_path)
    
    # Step 2: Extract based on type
    if pdf_type == "digital":
        result = extract_digital_pdf(file_path)
    else:  # scanned
        if not OCR_AVAILABLE or not OCR_ENABLED:
            logger.error("Cannot process scanned PDF: OCR not available or disabled")
            raise Exception("OCR libraries required for scanned PDFs. Install: pip install pytesseract pdf2image")
        result = extract_scanned_pdf(file_path)
    
    # Validation
    total_content = len(result["paragraphs"]) + len(result["tables"])
    if total_content == 0:
        logger.error("No content extracted from PDF")
        raise ValueError("Could not extract any text or tables from PDF")
    
    logger.info(f"Successfully extracted: {len(result['paragraphs'])} paragraphs, {len(result['tables'])} tables")
    return result
