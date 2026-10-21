from pathlib import Path
import shutil

from PIL import Image
import pytesseract


# Common Windows installation locations.
COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def _configure_tesseract():
    # First, find Tesseract through PATH.
    # This supports Linux/Streamlit Cloud and Windows.
    executable = shutil.which("tesseract")

    if executable:
        pytesseract.pytesseract.tesseract_cmd = executable
        return True

    # Fall back to common Windows installation locations.
    for path in COMMON_TESSERACT_PATHS:
        if Path(path).is_file():
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


def ocr_available():
    if not _configure_tesseract():
        return False

    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_image(uploaded_file):
    if not _configure_tesseract():
        raise RuntimeError(
            "Tesseract executable was not found. "
            "On Streamlit Cloud, check that packages.txt is in the "
            "repository root and contains: tesseract-ocr"
        )

    try:
        image = Image.open(uploaded_file).convert("RGB")
        text = pytesseract.image_to_string(image, config="--psm 6")
        return text.strip()
    except Exception as exc:
        raise RuntimeError(
            f"OCR failed: {exc}"
        ) from exc
