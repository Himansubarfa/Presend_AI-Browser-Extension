# backend/ocr/image_processor.py
import io
import logging
from typing import List, Dict, Any
import cv2
import numpy as np
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

# PaddleOCR is loaded once (model downloads on first use)
_ocr: PaddleOCR | None = None

def _get_ocr() -> PaddleOCR:
    global _ocr
    if _ocr is None:
        _ocr = PaddleOCR(lang='en', use_angle_cls=False)
    return _ocr


def ocr_bboxes(image_bytes: bytes) -> dict:
    """
    Run OCR on image bytes and return:
      - full_text: concatenated text (words joined by spaces)
      - words: list of dicts, each {text, bbox:[x1,y1,x2,y2], conf}
    """
    ocr = _get_ocr()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image (maybe corrupt or unsupported format).")

    results = ocr.ocr(img, cls=False)
    words = []
    full_lines = []
    if results and results[0]:
        for line in results[0]:
            # Each line is [bbox, (text, confidence)]
            bbox_points, (text, confidence) = line
            xs = [p[0] for p in bbox_points]
            ys = [p[1] for p in bbox_points]
            x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            words.append({
                "text": text.strip(),
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "conf": float(confidence)
            })
            full_lines.append(text.strip())
    full_text = ' '.join(full_lines)
    return {"full_text": full_text, "words": words, "image_shape": img.shape[:2]}


def redact_image(image_bytes: bytes, entities: List[Dict[str, Any]]) -> bytes:
    """
    Given original image bytes and a list of entity spans (with 'bbox' keys),
    draw black rectangles over each entity's bounding box and return the
    resulting image as JPEG bytes.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image for redaction.")

    for ent in entities:
        x1, y1, x2, y2 = ent["bbox"]
        # Expand the box slightly to ensure full coverage
        x1 = max(0, x1 - 2)
        y1 = max(0, y1 - 2)
        x2 = min(img.shape[1], x2 + 2)
        y2 = min(img.shape[0], y2 + 2)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)

    # Encode as JPEG (smaller than PNG for transmission)
    success, buffer = cv2.imencode('.jpg', img)
    if not success:
        raise RuntimeError("Failed to encode redacted image.")
    return buffer.tobytes()