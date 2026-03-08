import time
import logging
from typing import Dict, Any

from .detector import detect_entities
from .masker import mask_text, MASK_LABELS

logger = logging.getLogger(__name__)

def process_text(text: str) -> Dict[str, Any]:
    """
    End‑to‑end PII processing with performance timing.
    """
    safe_response = {
        "original": text if text is not None else "",
        "masked": text if text is not None else "",
        "entities": [],
        "error": None
    }

    try:
        if text is None:
            raise ValueError("Input text cannot be None")
        if not isinstance(text, str):
            text = str(text)

        if not text.strip():
            logger.info("Empty input received")
            return safe_response

        logger.info("Processing text of length %d", len(text))
        total_start = time.perf_counter()

        # --- Detection timing ---
        detect_start = time.perf_counter()
        entities = detect_entities(text)
        detect_time = (time.perf_counter() - detect_start) * 1000  # ms
        if not isinstance(entities, list):
            raise TypeError("detect_entities must return a list")

        # --- Masking timing ---
        mask_start = time.perf_counter()
        masked = mask_text(text, entities)
        mask_time = (time.perf_counter() - mask_start) * 1000  # ms

        total_time = (time.perf_counter() - total_start) * 1000  # ms

        # Log performance
        logger.info(f"Detection: {detect_time:.2f}ms, Masking: {mask_time:.2f}ms, Total: {total_time:.2f}ms")

        # Optional: warn if total exceeds 50ms
        if total_time > 50:
            logger.warning(f"Processing time exceeded 50ms: {total_time:.2f}ms")

        return {
            "original": text,
            "masked": masked,
            "entities": entities,
            "error": None
        }

    except Exception as e:
        logger.exception("Processing failed")
        safe_response["error"] = str(e)
        return safe_response