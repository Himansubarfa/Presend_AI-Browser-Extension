# backend/document/pdf_processor.py
import io
import logging
from typing import List, Dict, Any
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Extract text from a PDF, returning:
      - full_text: complete text (with newlines)
      - words: list of {text, bbox:[x0,y0,x1,y1], page, block...}
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    words_out = []
    for page_num, page in enumerate(doc):
        # Get words with coordinates
        word_list = page.get_text("words")
        for w in word_list:
            x0, y0, x1, y1, word_text, block_no, line_no, word_no = w
            # Add word only if it's actual text (skip empty glyphs)
            if word_text.strip():
                words_out.append({
                    "text": word_text,
                    "bbox": [x0, y0, x1, y1],
                    "page": page_num,
                })
        # Build page text: actually we'll concatenate lines extracted from page
        page_text = page.get_text("text")
        if full_text:
            full_text += "\n" + page_text
        else:
            full_text = page_text
    doc.close()
    return {"full_text": full_text, "words": words_out}


def redact_pdf(file_bytes: bytes, redactions: List[Dict[str, Any]]) -> bytes:
    """
    Apply redactions to a PDF. Each redaction entry should have:
      - page: int
      - bbox: [x0,y0,x1,y1]
    We'll add redact annotations and apply them.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for r in redactions:
        page_num = r["page"]
        x0, y0, x1, y1 = r["bbox"]
        # Convert from PyMuPDF coordinates (top-left origin) to fitz.Rect
        rect = fitz.Rect(x0, y0, x1, y1)
        page = doc[page_num]
        # Add a redaction annotation (black fill)
        page.add_redact_annot(rect, fill=(0, 0, 0))
    # Apply all redactions now
    for page in doc:
        page.apply_redactions()
    # Save to bytes
    out = io.BytesIO()
    doc.save(out)
    doc.close()
    return out.getvalue()