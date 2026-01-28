from pypdf import PdfReader
import os
import sys

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
                print(f"[OK] Found Tesseract at: {path}")
                break
    
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[INFO] OCR libraries not available. Install pytesseract, pdf2image, Pillow, opencv-python for OCR support.")

# Import OCR configuration
try:
    from .config import OCR_ENABLED, OCR_LANGUAGE, OCR_DPI, OCR_MIN_TEXT_LENGTH
except ImportError:
    OCR_ENABLED = True
    OCR_LANGUAGE = "eng"
    OCR_DPI = 300
    OCR_MIN_TEXT_LENGTH = 100


def preprocess_image_for_ocr(image):
    """Enhance image quality for better OCR accuracy"""
    try:
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply denoising
        gray = cv2.medianBlur(gray, 3)
        
        return Image.fromarray(gray)
    except Exception as e:
        print(f"[WARNING] Image preprocessing failed: {e}. Using original image.")
        return image


def extract_text_with_ocr(file_path: str) -> str:
    """Extract text from PDF using OCR (for scanned documents)"""
    if not OCR_AVAILABLE:
        raise Exception("OCR libraries not installed. Install: pip install pytesseract pdf2image Pillow opencv-python")
    
    print(f"[OCR] Starting OCR for {file_path}")
    try:
        # Auto-detect Poppler on Windows or via environment variable POPPLER_PATH
        poppler_path = os.getenv('POPPLER_PATH')
        if poppler_path and os.path.exists(poppler_path):
            print(f"[OCR] Using Poppler from POPPLER_PATH: {poppler_path}")
        elif os.name == 'nt':  # Windows
            # Try default extracted location first (user home)
            default_poppler = os.path.expanduser(r"~\poppler\poppler-24.02.0\Library\bin")
            if os.path.exists(default_poppler):
                poppler_path = default_poppler
                print(f"[OCR] Found Poppler at default location: {poppler_path}")
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
                        print(f"[OCR] Found Poppler at: {path}")
                        break
                if not poppler_path:
                    print("[OCR ERROR] Poppler not found at any expected location. Set POPPLER_PATH env var or download Poppler.")
                    raise FileNotFoundError("Poppler executable not found. Install from https://github.com/oschwartz10612/poppler-windows/releases")
        
        # Convert PDF pages to images
        print(f"[OCR] Converting PDF to images with Poppler: {poppler_path}")
        if poppler_path:
            images = convert_from_path(file_path, dpi=OCR_DPI, poppler_path=poppler_path)
        else:
            images = convert_from_path(file_path, dpi=OCR_DPI)
        
        print(f"[OCR] Generated {len(images)} images from PDF")
        text = ""
        for i, image in enumerate(images):
            print(f"[OCR] Processing page {i+1}/{len(images)}...")
            
            # Preprocess image for better OCR
            processed_image = preprocess_image_for_ocr(image)
            
            # Perform OCR
            page_text = pytesseract.image_to_string(processed_image, lang=OCR_LANGUAGE)
            text += page_text + "\n"
        
        print(f"[OCR] Successfully extracted {len(text)} characters using OCR")
        return text
        
    except Exception as e:
        print(f"[OCR ERROR] OCR extraction failed: {type(e).__name__}: {e}")
        raise


def load_pdf(file_path: str) -> str:
    """
    Load and extract text from PDF with hybrid OCR support.
    
    Strategy:
    1. First, extract regular text from PDF
    2. If OCR is enabled and available:
       - If extracted text is insufficient, use full-page OCR
       - Extract text from embedded images using OCR
    3. Combine all text sources
    
    This ensures backward compatibility while adding OCR capabilities.
    """
    print(f"[PDF_LOADER] Starting load_pdf for {file_path}")
    # Step 1: Extract regular text (existing functionality)
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    text_length = len(text.strip())
    print(f"[PDF_LOADER] Standard extraction yielded {text_length} characters")
    
    # Step 2: Check if OCR enhancement is needed
    if OCR_ENABLED and OCR_AVAILABLE:
        # If very little text was extracted, the PDF might be scanned
        if text_length < OCR_MIN_TEXT_LENGTH:
            print(f"[PDF_LOADER] Minimal text ({text_length} < {OCR_MIN_TEXT_LENGTH}). Attempting full-page OCR...")
            try:
                ocr_text = extract_text_with_ocr(file_path)
                ocr_length = len(ocr_text.strip())
                print(f"[PDF_LOADER] OCR yielded {ocr_length} characters")
                # Use OCR text if it's significantly longer
                if ocr_length > text_length:
                    print("[PDF_LOADER] Using OCR-extracted text (more comprehensive)")
                    text = ocr_text
                    text_length = ocr_length
            except Exception as e:
                print(f"[PDF_LOADER WARNING] Full-page OCR failed: {type(e).__name__}: {e}")
        else:
            print(f"[PDF_LOADER] Sufficient text extracted ({text_length} >= {OCR_MIN_TEXT_LENGTH})")
    else:
        print(f"[PDF_LOADER] OCR disabled or unavailable (OCR_ENABLED={OCR_ENABLED}, OCR_AVAILABLE={OCR_AVAILABLE})")
    
    # Fallback: If still no text, return error message
    if text_length < 10:
        msg = "[ERROR] Could not extract text from PDF. Ensure it's a valid PDF or install OCR for scanned documents."
        print(f"[PDF_LOADER] {msg}")
        return msg
    
    print(f"[PDF_LOADER] Returning {text_length} characters")
    return text
