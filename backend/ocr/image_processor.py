# backend/ocr/image_processor.py
import logging
from typing import List, Dict, Any
import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)

_reader: easyocr.Reader | None = None

def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        logger.info("Initialising EasyOCR (this may download the model on first run)...")
        _reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR ready.")
    return _reader


def ocr_bboxes(image_bytes: bytes) -> dict:
    """Return {'full_text': str, 'words': [{text, bbox, conf}], 'image_shape': (h,w)}"""
    reader = _get_reader()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")

    # EasyOCR returns list of (bbox, text, confidence)
    raw = reader.readtext(img)
    words = []
    full_lines = []
    for bbox_points, text, conf in raw:
        xs = [p[0] for p in bbox_points]
        ys = [p[1] for p in bbox_points]
        x1, y1, x2, y2 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
        words.append({
            "text": text.strip(),
            "bbox": [x1, y1, x2, y2],
            "conf": round(float(conf), 4)
        })
        full_lines.append(text.strip())

    full_text = ' '.join(full_lines)
    return {"full_text": full_text, "words": words, "image_shape": img.shape[:2]}


def redact_image(image_bytes: bytes, redaction_boxes: List[Dict[str, Any]]) -> bytes:
    """redaction_boxes: list of {'bbox': [x1,y1,x2,y2]}"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")

    for item in redaction_boxes:
        x1, y1, x2, y2 = item["bbox"]
        x1 = max(0, x1 - 2)
        y1 = max(0, y1 - 2)
        x2 = min(img.shape[1], x2 + 2)
        y2 = min(img.shape[0], y2 + 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)

    success, buffer = cv2.imencode('.jpg', img)
    if not success:
        raise RuntimeError("Failed to encode redacted image")
    return buffer.tobytes()