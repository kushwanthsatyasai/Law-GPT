from typing import Iterator, Tuple
from pdfminer.high_level import extract_text
import os
import io
from PIL import Image
import pytesseract
import easyocr
import cv2
import numpy as np


def extract_text_from_pdf(path: str) -> str:
    """Enhanced PDF text extraction using multiple methods"""
    text = ""
    
    # Method 1: PDFMiner (good for text-based PDFs)
    try:
        text = extract_text(path) or ""
        print(f"PDFMiner extracted {len(text)} characters")
    except Exception as e:
        print(f"PDFMiner extraction failed: {e}")
    
    # Method 2: Fallback to Tesseract OCR for scanned PDFs
    if not text or len(text.strip()) < 50:
        try:
            # Use pdf2image to convert PDF to images, then OCR
            from pdf2image import convert_from_path
            pages = convert_from_path(path, dpi=200)
            for i, page in enumerate(pages):
                ocr_text = extract_text_from_image_with_easyocr(page)
                text += f"\n\n--- Page {i + 1} ---\n{ocr_text}"
            print(f"OCR extraction completed for {len(pages)} pages")
        except Exception as e:
            print(f"PDF OCR extraction failed: {e}")
            # Final fallback - try to extract with basic PDFMiner settings
            try:
                from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
                from pdfminer.converter import TextConverter
                from pdfminer.layout import LAParams
                from pdfminer.pdfpage import PDFPage
                
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                
                with open(path, 'rb') as fh:
                    for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                        page_interpreter.process_page(page)
                
                text = fake_file_handle.getvalue()
                converter.close()
                fake_file_handle.close()
                print(f"Fallback PDFMiner extraction completed")
            except Exception as e2:
                print(f"Fallback PDFMiner extraction failed: {e2}")
    
    return text.strip()


def extract_text_from_image(path: str) -> str:
    """Enhanced image text extraction using multiple OCR engines"""
    img = Image.open(path)
    return extract_text_from_image_with_easyocr(img)


def extract_text_from_image_with_easyocr(img: Image.Image) -> str:
    """Extract text from PIL Image using EasyOCR"""
    try:
        # Convert PIL Image to numpy array
        img_array = np.array(img)
        
        # Convert to RGB if needed
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_rgb = img_array
        
        # Initialize EasyOCR reader (English)
        reader = easyocr.Reader(['en'])
        
        # Perform OCR
        results = reader.readtext(img_rgb)
        
        # Extract text from results
        text_parts = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Only include high-confidence text
                text_parts.append(text)
        
        return " ".join(text_parts)
    except Exception as e:
        print(f"EasyOCR extraction failed: {e}")
        # Fallback to Tesseract
        return pytesseract.image_to_string(img) or ""


def enumerate_files(storage_dir: str) -> Iterator[Tuple[str, str]]:
    for root, _, files in os.walk(storage_dir):
        for f in files:
            full = os.path.join(root, f)
            yield full, f