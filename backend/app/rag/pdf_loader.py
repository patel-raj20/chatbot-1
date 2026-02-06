"""
PDF Text Loader
===============
Extracts text from PDF files with automatic digital/scanned detection.

STRATEGY:
    1. Try extracting text with pdfplumber
    2. If extracted text < 100 chars → Use OCR (scanned PDF)
    3. If extracted text >= 100 chars → Use that text (digital PDF)

WHY THIS WORKS:
    - Digital PDFs have extractable text
    - Scanned PDFs appear as images (little/no text)
    - OCR preserves layout (tables stay aligned naturally)

WHERE USED: Called by pipeline.py during PDF ingestion
"""

import pdfplumber
import os
from app.core.logger import get_logger

logger = get_logger(__name__)

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


def load_pdf(file_path: str) -> str:
    """
    Load and extract text from PDF (digital or scanned).
    
    SIMPLE LOGIC:
        1. Try pdfplumber first
        2. If text < 100 chars → Use OCR
        3. Return full text as single string
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Full text extracted from PDF
        
    Raises:
        ValueError: If no text could be extracted
    """
    logger.info(f"Loading PDF: {file_path}")
    
    # STEP 1: Try extracting text with pdfplumber
    text = _extract_with_pdfplumber(file_path)
    
    # STEP 2: Check if we need OCR
    if len(text) < OCR_MIN_TEXT_LENGTH:
        logger.info(f"Extracted only {len(text)} chars. Using OCR (scanned PDF)")
        
        if not OCR_AVAILABLE or not OCR_ENABLED:
            raise Exception("OCR required but not available. Install: pip install pytesseract pdf2image")
        
        text = _extract_with_ocr(file_path)
    else:
        logger.info(f"Extracted {len(text)} chars. Using pdfplumber text (digital PDF)")
    
    # STEP 3: Validate
    if len(text) < 10:
        raise ValueError("Could not extract meaningful text from PDF")
    
    logger.info(f"Successfully extracted {len(text)} characters from PDF")
    return text


def _extract_with_pdfplumber(file_path: str) -> str:
    """
    Extract text from PDF using pdfplumber.
    
    Returns:
        All text from all pages concatenated
    """
    try:
        all_text = []
        
        with pdfplumber.open(file_path) as pdf:
            logger.debug(f"PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                
                if page_text:
                    all_text.append(page_text)
                    logger.debug(f"Page {page_num}: extracted {len(page_text)} chars")
        
        full_text = "\n\n".join(all_text)
        logger.info(f"pdfplumber extracted {len(full_text)} total characters")
        
        return full_text
        
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
        return ""  # Return empty to trigger OCR


def _extract_with_ocr(file_path: str) -> str:
    """
    Extract text from scanned PDF using OCR.
    
    WHY pytesseract.image_to_string:
        - Preserves layout naturally (tables stay aligned)
        - No custom table detection needed
        - Works for both tables and paragraphs
    
    Returns:
        All OCR text from all pages concatenated
    """
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
                all_text.append(page_text.strip())
                logger.debug(f"Page {page_num}: extracted {len(page_text)} chars")
        
        full_text = "\n\n".join(all_text)
        logger.info(f"OCR extracted {len(full_text)} total characters")
        
        return full_text
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise


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
