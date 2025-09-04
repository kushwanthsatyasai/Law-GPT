from typing import Iterator, Tuple
from pdfminer.high_level import extract_text
import os
from PIL import Image
import pytesseract


def extract_text_from_pdf(path: str) -> str:
    return extract_text(path) or ""


def extract_text_from_image(path: str) -> str:
    img = Image.open(path)
    return pytesseract.image_to_string(img) or ""


def enumerate_files(storage_dir: str) -> Iterator[Tuple[str, str]]:
    for root, _, files in os.walk(storage_dir):
        for f in files:
            full = os.path.join(root, f)
            yield full, f