# backend/ocr/image_processor.py
import logging
from typing import List, Dict, Any
import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)

_reader: easyocr.Reader | None = None
_face_cascade = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        logger.info("Initialising EasyOCR (downloads model on first run)...")
        _reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR ready.")
    return _reader


def _get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def preprocess_image(image_bytes: bytes) -> bytes:
    """Convert to grayscale, deskew, and apply adaptive thresholding."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    success, buf = cv2.imencode('.png', thresh)
    if not success:
        raise RuntimeError("Failed to encode preprocessed image")
    return buf.tobytes()


def ocr_bboxes(image_bytes: bytes) -> dict:
    """Return {'full_text': str, 'words': [{text, bbox, conf}], 'image_shape': (h,w)}"""
    # Use preprocessed image for better OCR
    clean_bytes = preprocess_image(image_bytes)
    reader = _get_reader()
    nparr = np.frombuffer(clean_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")

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


def detect_faces(image_bytes: bytes):
    """Return list of {'bbox': [x1,y1,x2,y2]} for each detected face or ID photo."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = _get_face_cascade()
    faces = []

    # 1st attempt: normal detection
    faces_1 = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces_1:
        faces.append((x, y, w, h))

    # 2nd attempt: more relaxed for small faces
    if not faces:
        faces_2 = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
        for (x, y, w, h) in faces_2:
            faces.append((x, y, w, h))

    # 3rd attempt: contour search for square photo region
    if not faces:
        h_img, w_img = img.shape[:2]
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            img_area = h_img * w_img
            # typical ID photo is ~2-25% of image area and square-ish
            if 0.02 * img_area < area < 0.25 * img_area and 0.8 < w / h < 1.2:
                faces.append((x, y, w, h))
                break

    return [{"bbox": [int(x), int(y), int(x + w), int(y + h)]} for (x, y, w, h) in faces]


def redact_image(image_bytes: bytes, redaction_boxes: List[Dict[str, Any]]) -> bytes:
    """Apply black rectangles over each bbox and return JPEG bytes."""
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