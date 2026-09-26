# utils/pdf_parser.py
import fitz  # PyMuPDF


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF given its raw bytes.
    If the PDF is a scanned image, falls back to OCR via EasyOCR.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    extracted_pages = []
    for page in doc:
        text = page.get_text("text").strip()
        if text:
            extracted_pages.append(text)
        else:
            # Fallback: render page to image for scanned PDF OCR
            try:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                from utils.image_parser import extract_image_text
                ocr_text = extract_image_text(img_bytes)
                if ocr_text:
                    extracted_pages.append(ocr_text)
            except Exception:
                pass
    doc.close()
    return "\n".join(extracted_pages).strip()

