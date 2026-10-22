
import os
import shutil
from pathlib import Path

from PIL import Image
import pytesseract


COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
]


def _configure_tesseract():
    # Allow a custom executable path through an environment variable.
    configured_path = os.getenv("TESSERACT_CMD")

    candidates = [
        configured_path,
        shutil.which("tesseract"),
        *COMMON_TESSERACT_PATHS,
    ]

    for path in candidates:
        if path and Path(path).is_file():
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
    if not ocr_available():
        raise RuntimeError(
            "Tesseract OCR engine is unavailable. On Streamlit Cloud, "
            "add 'tesseract-ocr' to packages.txt, commit the file beside "
            "app.py, and reboot the app."
        )

    try:
        image = Image.open(uploaded_file).convert("RGB")
        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )
        return text.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Could not extract text from this image: {exc}"
        ) from exc
