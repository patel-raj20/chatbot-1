"""
PDF Text Loader
===============
Extracts text from PDF files with optional OCR support.

FEATURES:
    1. Standard text extraction (PyPDF)
    2. OCR for scanned documents (Tesseract + pdf2image)
    3. Image preprocessing for better OCR accuracy
    
WHY TWO METHODS:
    - Digital PDFs: Fast extraction with PyPDF
    - Scanned PDFs: Need OCR to recognize text from images
    
WHERE USED: Called by pipeline.py during PDF ingestion
"""

from pypdf import PdfReader
import os
import sys
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
    from .config import OCR_ENABLED, OCR_LANGUAGE, OCR_DPI, OCR_MIN_TEXT_LENGTH
except ImportError:
    OCR_ENABLED = True
    OCR_LANGUAGE = "eng"
    OCR_DPI = 300
    OCR_MIN_TEXT_LENGTH = 100


def preprocess_image_for_ocr(image):
    """
    Enhance image quality for better OCR accuracy.
    
    WHY: Raw images often have noise, varying contrast
    WHERE: Called before OCR processing
    HOW: Applies grayscale, thresholding, and denoising
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image
        
    TECHNIQUES:
        - Grayscale: Removes color complexity
        - OTSU thresholding: Automatic contrast optimization
        - Median blur: Removes noise while preserving edges
    """
    try:
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding (OTSU automatic)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply denoising
        gray = cv2.medianBlur(gray, 3)
        
        return Image.fromarray(gray)
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}. Using original image.")
        return image


def extract_text_with_ocr(file_path: str) -> str:
    """
    Extract text from scanned PDF using OCR.
    
    WHY: Scanned PDFs contain images, not text - need OCR
    WHERE: Called by load_pdf() when text extraction yields minimal content
    HOW: Converts PDF pages to images → OCR → text
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text from all pages
        
    Raises:
        Exception: If OCR libraries not installed
        FileNotFoundError: If Poppler not found
        
    DEPENDENCIES:
        - Tesseract: OCR engine
        - Poppler: PDF to image converter
        - pdf2image: Python wrapper for Poppler
    """
    if not OCR_AVAILABLE:
        raise Exception("OCR libraries not installed. Install: pip install pytesseract pdf2image Pillow opencv-python")
    
    logger.info(f"Starting OCR extraction for {file_path}")
    try:
        # Auto-detect Poppler on Windows or via environment variable POPPLER_PATH
        poppler_path = os.getenv('POPPLER_PATH')
        if poppler_path and os.path.exists(poppler_path):
            logger.info(f"Using Poppler from POPPLER_PATH: {poppler_path}")
        elif os.name == 'nt':  # Windows
            # Try default extracted location first (user home)
            default_poppler = os.path.expanduser(r"~\poppler\poppler-24.02.0\Library\bin")
            if os.path.exists(default_poppler):
                poppler_path = default_poppler
                logger.info(f"Found Poppler at default location: {poppler_path}")
            else:
                poppler_path = None
                possible_poppler_paths = [
                    r'C:\Users\stadmin\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin',
                    r'C:\Program Files\poppler\Library\bin',
                    r'C:\Program Files (x86)\poppler\Library\bin',
                    r'C:\poppler\Library\bin',
                    r'C:\Users\stadmin\AppData\Local\poppler\Library\bin',
                    r'C:\Program Files\poppler-0.68.0\bin',
                    r'C:\Program Files\poppler-21.03.0\Library\bin',
                ]
                for path in possible_poppler_paths:
                    if os.path.exists(path):
                        poppler_path = path
                        logger.info(f"Found Poppler at: {path}")
                        break
                if not poppler_path:
                    logger.error("Poppler not found at any expected location. Set POPPLER_PATH env var or download Poppler.")
                    raise FileNotFoundError("Poppler executable not found. Install from https://github.com/oschwartz10612/poppler-windows/releases")
        
        # Convert PDF pages to images
        logger.debug(f"Converting PDF to images with Poppler: {poppler_path}")
        if poppler_path:
            images = convert_from_path(file_path, dpi=OCR_DPI, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path, dpi=OCR_DPI)
        
        logger.info(f"Generated {len(images)} images from PDF")
        text = ""
        for i, image in enumerate(images):
            logger.debug(f"Processing page {i+1}/{len(images)} with OCR...")
            
            # Preprocess image for better OCR
            processed_image = preprocess_image_for_ocr(image)
            
            # Perform OCR
            page_text = pytesseract.image_to_string(processed_image, lang=OCR_LANGUAGE)
            text += page_text + "\n"
        
        logger.info(f"Successfully extracted {len(text)} characters using OCR")
        return text
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {type(e).__name__}: {e}")
        raise


def load_pdf(file_path: str) -> str:
    """
    Load and extract text from PDF with hybrid OCR support.
    
    WHY: Handles both digital and scanned PDFs
    WHERE: Called by pipeline.py during PDF ingestion
    HOW: Try standard extraction first → OCR fallback if needed
    
    Args:
        file_path: Absolute path to PDF file
        
    Returns:
        Extracted text content
        
    STRATEGY:
        1. Extract standard text (PyPDF)
        2. If minimal text AND OCR available → full OCR
        3. Return combined text
        
    CONFIGURATION:
        - OCR_ENABLED: Enable/disable OCR (config.py)
        - OCR_MIN_TEXT_LENGTH: Threshold for triggering OCR (default 100)
        - OCR_LANGUAGE: Tesseract language (default 'eng')
        - OCR_DPI: Image resolution for OCR (default 300)
    """
    logger.info(f"Loading PDF: {file_path}")
    
    # Step 1: Extract text with pdfplumber (better for tables)
    text = ""
    text_length = 0
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(layout=True)  # layout=True preserves table structure
                if page_text:
                    text += page_text + "\n"
        text_length = len(text.strip())
        logger.info(f"pdfplumber extraction yielded {text_length} characters")
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}. Falling back to pypdf...")
        # Fallback to pypdf if pdfplumber fails
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        text_length = len(text.strip())
        logger.info(f"pypdf fallback extraction yielded {text_length} characters")
    
    # Step 2: Check if OCR enhancement is needed
    if OCR_ENABLED and OCR_AVAILABLE:
        # If very little text was extracted, the PDF might be scanned
        if text_length < OCR_MIN_TEXT_LENGTH:
            logger.info(f"Minimal text ({text_length} < {OCR_MIN_TEXT_LENGTH}). Attempting full-page OCR...")
            try:
                ocr_text = extract_text_with_ocr(file_path)
                ocr_length = len(ocr_text.strip())
                logger.info(f"OCR yielded {ocr_length} characters")
                # Use OCR text if it's significantly longer
                if ocr_length > text_length:
                    logger.info("Using OCR-extracted text (more comprehensive)")
                    text = ocr_text
                    text_length = ocr_length
            except Exception as e:
                logger.warning(f"Full-page OCR failed: {type(e).__name__}: {e}")
        else:
            logger.info(f"Sufficient text extracted ({text_length} >= {OCR_MIN_TEXT_LENGTH})")
    else:
        logger.debug(f"OCR disabled or unavailable (OCR_ENABLED={OCR_ENABLED}, OCR_AVAILABLE={OCR_AVAILABLE})")
    
    # Fallback: If still no text, return error message
    if text_length < 10:
        msg = "Could not extract text from PDF. Ensure it's a valid PDF or install OCR for scanned documents."
        logger.error(msg)
        return f"[ERROR] {msg}"
    
    logger.info(f"Returning {text_length} characters from {file_path}")
    return text
