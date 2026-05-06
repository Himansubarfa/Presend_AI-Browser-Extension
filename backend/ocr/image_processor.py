import logging
from typing import List, Dict, Any
import cv2
import numpy as np
import easyocr

logger = logging.getLogger(__name__)

_reader = None
_face_cascade = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        logger.info("Initialising EasyOCR (model download if needed)...")
        _reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR ready.")
    return _reader


def _get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _face_cascade = cv2.CascadeClassifier(cascade_path)
    return _face_cascade


def preprocess_image(image_bytes: bytes, method: str = "clahe") -> bytes:
    """
    Apply a specific preprocessing method.
    Methods: 'clahe', 'binary', 'none'
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image")

    if method == "clahe":
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    elif method == "binary":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 11, 2)
    # else method == 'none' – leave as is

    success, buf = cv2.imencode('.png', img)
    if not success:
        raise RuntimeError("Failed to encode preprocessed image")
    return buf.tobytes()


def ocr_bboxes(image_bytes: bytes, preprocess: bool = True) -> dict:
    """
    Return OCR result using the best preprocessing method.
    Tries CLAHE, binary, and no preprocessing, picks the one with highest alphabetic ratio.
    Returns {'full_text': str, 'words': [{text, bbox, conf}], 'image_shape': (h,w)}
    """
    reader = _get_reader()
    methods = ["clahe", "binary", "none"]
    best_result = None
    best_ratio = -1

    for method in methods:
        try:
            if preprocess and method != "none":
                clean_bytes = preprocess_image(image_bytes, method=method)
            else:
                clean_bytes = image_bytes

            nparr = np.frombuffer(clean_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            raw = reader.readtext(img)

            # Group words into lines for cleaner full_text (using the line‑grouping logic)
            words = []
            for bbox_points, text, conf in raw:
                xs = [p[0] for p in bbox_points]
                ys = [p[1] for p in bbox_points]
                x1, y1, x2, y2 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
                words.append({
                    "text": text.strip(),
                    "bbox": [x1, y1, x2, y2],
                    "conf": round(float(conf), 4)
                })

            # Reconstruct text line by line for readability
            lines = _words_to_lines(words)
            full_text = '\n'.join(' '.join(w['text'] for w in line) for line in lines)

            alpha = sum(c.isalpha() for c in full_text)
            ratio = alpha / max(len(full_text), 1)
            if ratio > best_ratio:
                best_ratio = ratio
                best_result = {
                    "full_text": full_text,
                    "words": words,
                    "image_shape": img.shape[:2]
                }
        except Exception as e:
            logger.debug("OCR method %s failed: %s", method, e)
            continue

    if best_result is None:
        raise RuntimeError("All OCR methods failed")
    return best_result


def _words_to_lines(words: list, y_tolerance: int = 10) -> list:
    """Group OCR words into lines based on vertical position."""
    if not words:
        return []
    sorted_words = sorted(words, key=lambda w: (w['bbox'][1], w['bbox'][0]))
    lines = []
    current_line = [sorted_words[0]]
    for w in sorted_words[1:]:
        prev_y_center = (current_line[-1]['bbox'][1] + current_line[-1]['bbox'][3]) / 2
        curr_y_center = (w['bbox'][1] + w['bbox'][3]) / 2
        if abs(curr_y_center - prev_y_center) <= y_tolerance:
            current_line.append(w)
        else:
            lines.append(current_line)
            current_line = [w]
    lines.append(current_line)
    return lines


def detect_faces(image_bytes: bytes):
    """Return list of {'bbox': [x1,y1,x2,y2]} for faces or ID photo region."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = _get_face_cascade()
    faces = []

    # Normal detection
    faces1 = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces1:
        faces.append((x, y, w, h))

    # Relaxed detection for small faces
    if not faces:
        faces2 = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
        for (x, y, w, h) in faces2:
            faces.append((x, y, w, h))

    # Contour search for square photo region
    if not faces:
        h_img, w_img = img.shape[:2]
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            img_area = h_img * w_img
            if 0.02 * img_area < area < 0.25 * img_area and 0.8 < w / h < 1.2:
                faces.append((x, y, w, h))
                break

    return [{"bbox": [int(x), int(y), int(x + w), int(y + h)]} for (x, y, w, h) in faces]


def redact_image(image_bytes: bytes, redaction_boxes: List[Dict[str, Any]]) -> bytes:
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