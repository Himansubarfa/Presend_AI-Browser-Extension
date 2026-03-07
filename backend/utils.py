# # backend/processor.py

# from typing import List, Dict, Any
# from . import detector      # hypothetical detection module
# from .masker import mask_text, MASK_LABELS

# # ---------- Overlap Resolution (heuristic) ----------
# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Resolves overlapping entity spans.
#     Heuristic: keep the entity with the longest span when overlaps occur.
#     Entities are assumed to be sorted by start index.
#     Returns a new list with no overlaps.
#     """
#     if not entities:
#         return []

#     # Sort by start, then by end descending (longer spans first)
#     sorted_ents = sorted(entities, key=lambda e: (e['start'], -e['end']))
#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:
#             # Overlap: keep the longer span (or if equal, keep the first)
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#             # else keep current
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)
#     return resolved

# # ---------- Unified Processing Function ----------
# def process_text(text: str) -> Dict[str, Any]:
#     """
#     Main pipeline:
#         1. Normalize text (strip, ensure string)
#         2. Detect entities (using detector module)
#         3. Resolve overlaps
#         4. Mask text
#         5. Return structured result

#     Args:
#         text (str): Raw input text.

#     Returns:
#         dict: {
#             "original": original text,
#             "masked": masked text,
#             "entities": list of resolved entities (with labels, start, end)
#         }
#     """
#     if not isinstance(text, str):
#         text = str(text)

#     # Optional: minimal normalization (trimming) – does not affect indices
#     # because indices are relative to the original text. If we trim, indices become invalid.
#     # Therefore, we keep the original text as is for detection and masking.
#     # Normalization (e.g., lowercasing) would require index mapping; we skip it here.

#     # Step 2: Detect entities
#     raw_entities = detector.detect_entities(text)   # expects a list of dicts with label, start, end

#     # Step 3: Resolve overlaps
#     resolved_entities = resolve_overlaps(raw_entities)

#     # Step 4: Mask text
#     masked = mask_text(text, resolved_entities)

#     # Step 5: Return structured result
#     return {
#         "original": text,
#         "masked": masked,
#         "entities": resolved_entities
#     }

# # ---------- Quick Test (if run directly) ----------
# if __name__ == "__main__":
#     # Mock detector for demonstration (replace with actual import)
#     class MockDetector:
#         @staticmethod
#         def detect_entities(t):
#             # Simulate detection for a simple case
#             if "Rahul Sharma" in t:
#                 return [
#                     {"label": "PERSON", "start": 0, "end": 12},
#                     {"label": "EMAIL", "start": 19, "end": 34}
#                 ]
#             return []

#     # Replace the imported detector with our mock for this test
#     import sys
#     detector = MockDetector()

#     test_str = "Rahul Sharma email rahul@gmail.com"
#     result = process_text(test_str)
#     print("=== Unified Processor Test ===")
#     print(f"Original: {result['original']}")
#     print(f"Masked:   {result['masked']}")
#     print(f"Entities: {result['entities']}")



# # final code 1


# """
# Unified text processing pipeline.
# Orchestrates entity detection and masking.
# """

# import logging
# from typing import Dict, Any

# from .detector import detect_entities
# from .masker import mask_text, MASK_LABELS

# logger = logging.getLogger(__name__)


# class ProcessingError(Exception):
#     """Custom exception for processing failures."""
#     pass


# def process_text(text: str) -> Dict[str, Any]:
#     """
#     End‑to‑end PII processing.

#     Args:
#         text: Raw input text (may be None or non‑string).

#     Returns:
#         Dictionary with keys:
#             - original: the input text (as string)
#             - masked: text with PII replaced
#             - entities: list of resolved entities (label, start, end)

#     Raises:
#         ProcessingError: If input is invalid or a processing step fails.
#     """
#     # --- Input validation ---
#     if text is None:
#         raise ProcessingError("Input text cannot be None")
#     if not isinstance(text, str):
#         try:
#             text = str(text)
#         except Exception as e:
#             raise ProcessingError(f"Could not convert input to string: {e}") from e

#     # Empty input handling
#     if not text.strip():
#         logger.info("Empty input received, returning as is")
#         return {
#             "original": text,
#             "masked": text,
#             "entities": []
#         }

#     logger.info("Processing text of length %d", len(text))

#     # --- Entity detection ---
#     try:
#         entities = detect_entities(text)
#     except Exception as e:
#         logger.exception("Entity detection failed")
#         raise ProcessingError(f"Detection error: {e}") from e

#     if not isinstance(entities, list):
#         logger.error("detect_entities returned non-list: %s", type(entities))
#         raise ProcessingError("Detector must return a list")

#     # --- Masking ---
#     try:
#         masked = mask_text(text, entities)
#     except Exception as e:
#         logger.exception("Masking failed")
#         raise ProcessingError(f"Masking error: {e}") from e

#     # --- Return result ---
#     return {
#         "original": text,
#         "masked": masked,
#         "entities": entities
#     }


# # Expose mask labels if needed
# __all__ = ["process_text", "MASK_LABELS"]



# final code for production ready

"""
Unified text processing pipeline.
Orchestrates entity detection and masking with defensive error handling.
"""

import logging
from typing import Dict, Any

from .detector import detect_entities
from .masker import mask_text, MASK_LABELS

logger = logging.getLogger(__name__)


def process_text(text: str) -> Dict[str, Any]:
    """
    End‑to‑end PII processing with defensive error handling.

    Args:
        text: Raw input text (may be None or non‑string).

    Returns:
        Dictionary with keys:
            - original: the input text (as string)
            - masked: text with PII replaced
            - entities: list of resolved entities (label, start, end)
            - error: error message if any, otherwise None

    Even on failure, returns a safe structure with masked = original.
    """
    # Default safe response
    safe_response = {
        "original": text if text is not None else "",
        "masked": text if text is not None else "",
        "entities": [],
        "error": None
    }

    try:
        # --- Input validation ---
        if text is None:
            raise ValueError("Input text cannot be None")
        if not isinstance(text, str):
            text = str(text)

        if not text.strip():
            logger.info("Empty input received")
            return safe_response

        logger.info("Processing text of length %d", len(text))

        # --- Entity detection ---
        entities = detect_entities(text)
        if not isinstance(entities, list):
            raise TypeError("detect_entities must return a list")

        # --- Masking ---
        masked = mask_text(text, entities)

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


# Expose mask labels if needed
__all__ = ["process_text", "MASK_LABELS"]