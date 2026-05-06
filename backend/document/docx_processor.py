# backend/document/docx_processor.py
import io
import logging
from typing import List, Dict, Any
import docx

logger = logging.getLogger(__name__)

def extract_text_from_docx(file_bytes: bytes) -> dict:
    """Return {'full_text': str, 'paragraphs': list, 'doc_object': doc}"""
    doc = docx.Document(io.BytesIO(file_bytes))
    full_text_parts = []
    para_data = []
    for para in doc.paragraphs:
        runs_info = []
        text_so_far = 0
        for run in para.runs:
            if run.text:
                runs_info.append({
                    "text": run.text,
                    "start": text_so_far,
                    "end": text_so_far + len(run.text),
                    "run_obj": run,
                })
                text_so_far += len(run.text)
        para_text = para.text
        full_text_parts.append(para_text)
        para_data.append({"text": para_text, "runs": runs_info})
    full_text = "\n".join(full_text_parts)
    return {"full_text": full_text, "paragraphs": para_data, "doc_object": doc}


def redact_docx(doc_object) -> bytes:
    """Save the already‑modified document to bytes."""
    out = io.BytesIO()
    doc_object.save(out)
    return out.getvalue()