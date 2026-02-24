"""
PDF Document Loader with Layout-Aware Extraction
=================================================
Extracts structured content from PDFs using Docling with OCR fallback.

STRATEGY:
    1. Try extracting with Docling (structure-aware: headings, paragraphs, tables)
    2. Convert Docling output to markdown format
    3. If extraction fails or text < 100 chars → Use OCR fallback
    4. Return markdown + metadata (page numbers, structure)

WHY DOCLING:
    - Preserves document structure (headings, paragraphs, tables)
    - Handles digital PDFs, scanned PDFs, and hybrid PDFs
    - Outputs structured elements (not just plain text)
    - Better for layout-aware chunking

WHERE USED: Called by pipeline.py during PDF ingestion
"""

import os
from typing import Dict, Any
from app.core.logger import get_logger

logger = get_logger(__name__)

# Configuration
OCR_MIN_TEXT_LENGTH = 50  # Threshold to decide if OCR is needed

# Docling imports with fallback
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    import PyPDF2
    DOCLING_AVAILABLE = True
    logger.info("Docling libraries available")
except ImportError:
    DOCLING_AVAILABLE = False
    logger.warning("Docling not available. Install: pip install docling docling-core")

# Configuration
OCR_MIN_TEXT_LENGTH = 50  # Threshold to decide if OCR is needed

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
    logger.warning("OCR libraries not available. Install: pip install pytesseract pdf2image Pillow opencv-python")

# Import OCR configuration
try:
    from .config import OCR_ENABLED, OCR_LANGUAGE, OCR_DPI
except ImportError:
    OCR_ENABLED = True
    OCR_LANGUAGE = "eng"
    OCR_DPI = 300

def _is_digital_pdf(file_path: str) -> bool:
    """
    Quick check if PDF is digital (has text layer) or scanned (images only).
    
    Returns:
        True if digital (fast extraction), False if scanned (needs OCR)
    """
    try:
        with open(file_path, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            # Check first 2 pages for text
            pages_to_check = min(2, len(pdf.pages))
            text = ''.join(pdf.pages[i].extract_text() for i in range(pages_to_check))
            is_digital = len(text.strip()) > 100
            logger.info(f"PDF type: {'Digital' if is_digital else 'Scanned'} ({len(text)} chars in first {pages_to_check} pages)")
            return is_digital
    except:
        logger.warning("Could not detect PDF type, assuming scanned")
        return False


def load_pdf(file_path: str) -> Dict[str, Any]:
    """
    Load and extract structured content from PDF (digital or scanned).
    
    OPTIMIZED LOGIC:
        1. Detect PDF type (digital vs scanned)
        2. Use Docling with optimized settings:
           - Digital: do_ocr=False (50-100x faster)
           - Scanned: do_ocr=True (full OCR)
        3. Fallback to OCR if extraction fails
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dict with:
            - markdown: Full document in markdown format
            - total_pages: Total page count
            - has_tables: Whether document contains tables
        
    Raises:
        ValueError: If no text could be extracted
    """
    logger.info(f"Loading PDF: {file_path}")
    
    if not DOCLING_AVAILABLE:
        logger.warning("Docling not available, falling back to OCR")
        return _extract_with_ocr_fallback(file_path)
    
    # STEP 1: Detect PDF type for optimal processing
    is_digital = _is_digital_pdf(file_path)
    
    # STEP 2: Extract with optimized Docling settings
    result = _extract_with_docling(file_path, use_ocr=not is_digital)
    
    # STEP 3: Check if we need OCR fallback
    markdown = result.get("markdown", "")
    if len(markdown) < OCR_MIN_TEXT_LENGTH:
        logger.info(f"Extracted only {len(markdown)} chars. Using OCR fallback")
        result = _extract_with_ocr_fallback(file_path)
    else:
        logger.info(f"Extracted {len(markdown)} chars with Docling (structure-aware)")
    
    # STEP 4: Validate
    if len(result.get("markdown", "")) < 10:
        raise ValueError("Could not extract meaningful text from PDF")
    
    logger.info(f"Successfully extracted document: {result['total_pages']} pages")
    return result


def _extract_with_docling(file_path: str, use_ocr: bool = False) -> Dict[str, Any]:
    """
    Extract structured content from PDF using Docling with optimized settings.
    
    Args:
        file_path: PDF file path
        use_ocr: Enable OCR for scanned PDFs (slower but accurate)
    
    Returns markdown format with preserved structure:
        - Headings: # ## ###
        - Paragraphs: Plain text blocks
        - Tables: Markdown tables
        - Lists: - or 1.
    
    Returns:
        Dict with markdown, total_pages, has_tables
    """
    try:
        logger.info(f"Extracting with Docling (OCR={'ON' if use_ocr else 'OFF'})...")
        
        # Initialize Docling converter with minimal configuration
        # NOTE: Avoid custom PdfPipelineOptions to prevent backend attribute error
        converter = DocumentConverter(allowed_formats=['pdf'])
        
        # Convert PDF to structured document
        result = converter.convert(file_path)
        
        # Export to markdown format
        markdown = result.document.export_to_markdown()
        
        # Clean and normalize markdown to ensure proper paragraph breaks
        markdown = _normalize_markdown(markdown)
        
        # Extract metadata
        total_pages = len(result.document.pages) if hasattr(result.document, 'pages') else 1
        has_tables = any('|' in line and '---' in markdown for line in markdown.split('\n'))
        
        logger.info(f"Docling extracted {len(markdown)} chars, {total_pages} pages, tables={has_tables}")
        
        return {
            "markdown": markdown,
            "total_pages": total_pages,
            "has_tables": has_tables
        }
        
    except Exception as e:
        logger.error(f"Docling extraction failed: {e}")
        return {"markdown": "", "total_pages": 0, "has_tables": False}


def _normalize_markdown(markdown: str) -> str:
    """
    Normalize markdown to ensure proper structure for chunking.
    
    - Add page markers if missing
    - Ensure proper paragraph breaks
    - Clean excessive whitespace while preserving structure
    """
    # Remove excessive blank lines (more than 2)
    import re
    markdown = re.sub(r'\n{4,}', '\n\n\n', markdown)
    
    # Ensure single space after headings
    markdown = re.sub(r'^(#{1,6})\s+', r'\1 ', markdown, flags=re.MULTILINE)
    
    return markdown.strip()


def _extract_with_ocr_fallback(file_path: str) -> Dict[str, Any]:
    """
    Extract text from scanned PDF using OCR (Tesseract fallback).
    
    WHY pytesseract.image_to_string:
        - Preserves layout naturally (tables stay aligned)
        - Works for scanned/hybrid PDFs
    
    Returns:
        Dict with markdown (plain text format), total_pages, has_tables
    """
    if not OCR_AVAILABLE or not OCR_ENABLED:
        raise Exception("OCR required but not available. Install: pip install pytesseract pdf2image")
    
    try:
        # Convert PDF to images
        poppler_path = _find_poppler_path()
        
        logger.info("Converting PDF pages to images...")
        if poppler_path:
            images = convert_from_path(file_path, dpi=OCR_DPI, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path, dpi=OCR_DPI)
        
        logger.info(f"Processing {len(images)} pages with OCR...")
        
        all_text = []
        
        for page_num, image in enumerate(images, 1):
            logger.debug(f"OCR on page {page_num}/{len(images)}")
            
            # Preprocess image for better accuracy
            processed_image = _preprocess_image(image)
            
            # Extract text with OCR (preserves layout)
            page_text = pytesseract.image_to_string(
                processed_image,
                lang=OCR_LANGUAGE
            )
            
            if page_text and page_text.strip():
                # Clean and structure the OCR text
                clean_text = _clean_ocr_text(page_text)
                
                if clean_text:
                    # Add page marker for tracking
                    all_text.append(f"<!-- page:{page_num} -->\n\n{clean_text}")
                    logger.debug(f"Page {page_num}: extracted {len(clean_text)} chars")
                else:
                    logger.debug(f"Page {page_num}: no text after cleaning")
        
        markdown = "\n\n".join(all_text)
        logger.info(f"OCR extracted {len(markdown)} total characters from {len(all_text)} pages with content")
        
        return {
            "markdown": markdown,
            "total_pages": len(images),
            "has_tables": False  # OCR doesn't detect table structure
        }
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise


def _clean_ocr_text(text: str) -> str:
    """
    Clean OCR text to improve chunking and remove noise.
    
    - Remove excessive whitespace
    - Normalize line breaks
    - Preserve paragraph structure
    - Remove very short noisy lines
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Strip whitespace
        line = line.strip()
        
        # Skip very short lines (likely OCR noise) unless they look like headings or numbers
        if len(line) < 3 and not line.isdigit():
            continue
        
        # Skip lines with only special characters or excessive spaces
        if line and not line.replace(' ', '').replace('-', '').replace('_', ''):
            continue
        
        cleaned_lines.append(line)
    
    # Join lines with proper spacing
    # Detect paragraph breaks (empty line or large spacing)
    result_paragraphs = []
    current_para = []
    
    for line in cleaned_lines:
        if line:
            current_para.append(line)
        elif current_para:  # Empty line after text = paragraph break
            result_paragraphs.append(' '.join(current_para))
            current_para = []
    
    # Add last paragraph
    if current_para:
        result_paragraphs.append(' '.join(current_para))
    
    # Join paragraphs with double newline
    return '\n\n'.join(result_paragraphs)


def _preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess image for better OCR accuracy.
    
    SIMPLE ENHANCEMENTS:
        - Convert to grayscale
        - Apply thresholding (black/white)
        - Light denoising
    
    Args:
        image: PIL Image
        
    Returns:
        Preprocessed PIL Image
    """
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive thresholding for better contrast
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Light denoising
        gray = cv2.medianBlur(gray, 3)
        
        # Convert back to PIL Image
        return Image.fromarray(gray)
        
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original image.")
        return image


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
