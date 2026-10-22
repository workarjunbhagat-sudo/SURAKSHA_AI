from pathlib import Path
from PIL import Image
import pytesseract

# Common Windows installation locations.
COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

def _configure_tesseract():
    if Path(pytesseract.pytesseract.tesseract_cmd).exists():
        return True
    for path in COMMON_TESSERACT_PATHS:
        if Path(path).exists():
            pytesseract.pytesseract.tesseract_cmd = path
            return True
    return False

def ocr_available():
    if _configure_tesseract():
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    return False

def extract_text_from_image(uploaded_file):
    if not _configure_tesseract():
        raise RuntimeError(
            "Tesseract OCR is not installed or not found on this PC. "
            "Install Tesseract OCR, restart Streamlit, and try again. "
            "See README.md → Screenshot OCR setup."
        )
    image = Image.open(uploaded_file).convert("RGB")
    text = pytesseract.image_to_string(image, config="--psm 6")
    return text.strip()
