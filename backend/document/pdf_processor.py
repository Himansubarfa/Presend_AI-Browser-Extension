# backend/document/pdf_processor.py
import io, logging
from typing import List, Dict, Any
import fitz
from backend.ocr.image_processor import ocr_bboxes as image_ocr

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes, force_ocr: bool = False) -> dict:
    """Return {'full_text': str, 'words': [{text, bbox, page}]}."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    words_out = []
    for page_num, page in enumerate(doc):
        word_list = page.get_text("words")
        page_text = page.get_text("text")
        if len(word_list) < 3 or force_ocr:
            logger.info("Page %d – using OCR fallback.", page_num)
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes(output="png")
            ocr_result = image_ocr(img_bytes)
            for w in ocr_result["words"]:
                words_out.append({"text": w["text"], "bbox": w["bbox"], "page": page_num})
            full_text += ocr_result["full_text"] + "\n"
        else:
            for w in word_list:
                x0, y0, x1, y1, text, *_ = w
                if text.strip():
                    words_out.append({"text": text, "bbox": [x0, y0, x1, y1], "page": page_num})
            full_text += page_text + "\n"
    doc.close()
    return {"full_text": full_text.strip(), "words": words_out}

def redact_pdf(file_bytes: bytes, redactions: List[Dict[str, Any]]) -> bytes:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for r in redactions:
        page_num = r["page"]
        x0, y0, x1, y1 = r["bbox"]
        page = doc[page_num]
        page.add_redact_annot(fitz.Rect(x0, y0, x1, y1), fill=(0, 0, 0))
    for page in doc:
        page.apply_redactions()
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    return out.getvalue()