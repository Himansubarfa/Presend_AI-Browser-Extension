
# # day 26 final update 
# from __future__ import annotations

# import logging
# from typing import Any, Dict, List, Optional

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # Label → placeholder mapping
# # ---------------------------------------------------------------------------
# MASK_LABELS: Dict[str, str] = {
#     # Core
#     "PERSON":           "[NAME]",
#     "EMAIL":            "[EMAIL]",
#     "PHONE":            "[PHONE]",
#     "ID":               "[ID]",
#     "AADHAAR":          "[AADHAAR]",
#     "CARD":             "[CARD]",
#     "ADDRESS":          "[ADDRESS]",
#     "ORG":              "[ORG]",
#     # India-specific
#     "PAN":              "[PAN]",
#     "PASSPORT":         "[PASSPORT]",
#     "DRIVING_LICENCE":  "[DRIVING_LICENCE]",
#     "PINCODE":          "[PINCODE]",
#     "VEHICLE_REG":      "[VEHICLE_REG]",
#     "GST":              "[GST]",
#     "IFSC":             "[IFSC]",
#     "UPI":              "[UPI]",
#     # General
#     "DOB":              "[DOB]",
#     "IP":               "[IP]",
#     "URL":              "[URL]",
#     "SALARY":           "[SALARY]",
#     "LOCATION":         "[LOCATION]",
#     # NEW – credentials
#     "API_KEY":          "[API_KEY]",
#     "PASSWORD":         "[PASSWORD]",
# }

# DEFAULT_MASK = "[REDACTED]"


# # ---------------------------------------------------------------------------
# # Public API
# # ---------------------------------------------------------------------------

# def mask_text(
#     text: str,
#     entities: List[Dict[str, Any]],
#     *,
#     strict: bool = False,
# ) -> str:
#     """
#     Replace entity spans in *text* with mask placeholders.

#     Parameters
#     ----------
#     text:
#         Original text — must be the identical object (or equal string) that
#         was fed to the detector so that span indices align.
#     entities:
#         List of dicts with at minimum the keys ``label``, ``start``, ``end``.
#         Additional keys (e.g. ``text``) are ignored.
#     strict:
#         If True, raise ValueError on any validation failure.
#         If False (default), log a warning and skip the offending entity so
#         the rest of the text is still processed.

#     Returns
#     -------
#     str
#         Text with every valid entity span replaced by its placeholder.
#         Returns the original *text* unchanged if *entities* is empty or None.
#     """
#     # --- type coercion ---
#     if text is None:
#         return ""
#     if not isinstance(text, str):
#         logger.warning("mask_text: non-str text argument coerced (%s).", type(text).__name__)
#         text = str(text)

#     if not entities:
#         return text

#     text_len = len(text)

#     # --- validate all entities up-front ---
#     valid_entities: List[Dict[str, Any]] = []
#     for idx, ent in enumerate(entities):
#         err = _validate_entity(ent, idx, text_len)
#         if err:
#             if strict:
#                 raise ValueError(err)
#             logger.warning("mask_text: skipping entity[%d] – %s", idx, err)
#             continue
#         valid_entities.append(ent)

#     if not valid_entities:
#         return text

#     # --- sort end-to-start to avoid index shifts ---
#     sorted_entities = sorted(
#         valid_entities,
#         key=lambda e: (e["start"], -(e["end"] - e["start"])),
#         reverse=True,
#     )

#     masked      = text
#     last_start  = len(masked)

#     for ent in sorted_entities:
#         start       = ent["start"]
#         end         = ent["end"]
#         label       = ent["label"]
#         replacement = MASK_LABELS.get(label, DEFAULT_MASK)

#         if end > last_start:
#             logger.warning(
#                 "mask_text: skipping overlapping span '%s' [%d:%d] (already replaced region starts at %d).",
#                 label, start, end, last_start,
#             )
#             continue

#         if masked[start:end] == replacement:
#             logger.debug("mask_text: span [%d:%d] already holds placeholder, skipping.", start, end)
#             last_start = start
#             continue

#         masked     = masked[:start] + replacement + masked[end:]
#         last_start = start

#     return masked


# # ---------------------------------------------------------------------------
# # Private helpers
# # ---------------------------------------------------------------------------

# def _validate_entity(
#     ent: Any,
#     idx: int,
#     text_len: int,
# ) -> Optional[str]:
#     """
#     Return an error string if *ent* is invalid, else None.
#     """
#     if not isinstance(ent, dict):
#         return f"not a dict (got {type(ent).__name__})"

#     missing = {"label", "start", "end"} - ent.keys()
#     if missing:
#         return f"missing required keys: {missing}"

#     start = ent["start"]
#     end   = ent["end"]

#     if not isinstance(start, int) or not isinstance(end, int):
#         return f"start/end must be int, got ({type(start).__name__}, {type(end).__name__})"

#     if start < 0:
#         return f"start ({start}) is negative"

#     if end > text_len:
#         return (
#             f"end ({end}) exceeds text length ({text_len}); "
#             "ensure entities were generated from the same (possibly truncated) text"
#         )

#     if start >= end:
#         return f"invalid span: start ({start}) >= end ({end})"

#     return None 


# day 28 update 

from __future__ import annotations

# day 27 update — international robustness pass
# Changes vs day 26:
#   MASK_LABELS — added POSTCODE placeholder (distinct from India-only PINCODE)
#   No logic changes — masker is already correct and robust

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Label → placeholder mapping
# ---------------------------------------------------------------------------
MASK_LABELS: Dict[str, str] = {
    # Core
    "PERSON":           "[NAME]",
    "EMAIL":            "[EMAIL]",
    "PHONE":            "[PHONE]",
    "ID":               "[ID]",
    "AADHAAR":          "[AADHAAR]",
    "CARD":             "[CARD]",
    "ADDRESS":          "[ADDRESS]",
    "ORG":              "[ORG]",
    # India-specific
    "PAN":              "[PAN]",
    "PASSPORT":         "[PASSPORT]",
    "DRIVING_LICENCE":  "[DRIVING_LICENCE]",
    "PINCODE":          "[PINCODE]",       # India 6-digit (backward compat)
    "POSTCODE":         "[POSTCODE]",      # NEW — international postcode
    "VEHICLE_REG":      "[VEHICLE_REG]",
    "GST":              "[GST]",
    "IFSC":             "[IFSC]",
    "UPI":              "[UPI]",
    # General
    "DOB":              "[DOB]",
    "IP":               "[IP]",
    "URL":              "[URL]",
    "SALARY":           "[SALARY]",
    "LOCATION":         "[LOCATION]",
    # Credentials
    "API_KEY":          "[API_KEY]",
    "PASSWORD":         "[PASSWORD]",
}

DEFAULT_MASK = "[REDACTED]"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def mask_text(
    text: str,
    entities: List[Dict[str, Any]],
    *,
    strict: bool = False,
) -> str:
    """
    Replace entity spans in *text* with mask placeholders.

    Parameters
    ----------
    text:
        Original text — must be the identical object (or equal string) that
        was fed to the detector so that span indices align.
    entities:
        List of dicts with at minimum the keys ``label``, ``start``, ``end``.
        Additional keys (e.g. ``text``) are ignored.
    strict:
        If True, raise ValueError on any validation failure.
        If False (default), log a warning and skip the offending entity so
        the rest of the text is still processed.

    Returns
    -------
    str
        Text with every valid entity span replaced by its placeholder.
        Returns the original *text* unchanged if *entities* is empty or None.
    """
    # --- type coercion ---
    if text is None:
        return ""
    if not isinstance(text, str):
        logger.warning("mask_text: non-str text argument coerced (%s).", type(text).__name__)
        text = str(text)

    if not entities:
        return text

    text_len = len(text)

    # --- validate all entities up-front ---
    valid_entities: List[Dict[str, Any]] = []
    for idx, ent in enumerate(entities):
        err = _validate_entity(ent, idx, text_len)
        if err:
            if strict:
                raise ValueError(err)
            logger.warning("mask_text: skipping entity[%d] – %s", idx, err)
            continue
        valid_entities.append(ent)

    if not valid_entities:
        return text

    # --- sort end-to-start to avoid index shifts during replacement ---
    sorted_entities = sorted(
        valid_entities,
        key=lambda e: (e["start"], -(e["end"] - e["start"])),
        reverse=True,
    )

    masked     = text
    last_start = len(masked)

    for ent in sorted_entities:
        start       = ent["start"]
        end         = ent["end"]
        label       = ent["label"]
        replacement = MASK_LABELS.get(label, DEFAULT_MASK)

        if end > last_start:
            logger.warning(
                "mask_text: skipping overlapping span '%s' [%d:%d] (already replaced region starts at %d).",
                label, start, end, last_start,
            )
            continue

        if masked[start:end] == replacement:
            logger.debug("mask_text: span [%d:%d] already holds placeholder, skipping.", start, end)
            last_start = start
            continue

        masked     = masked[:start] + replacement + masked[end:]
        last_start = start

    return masked


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validate_entity(
    ent: Any,
    idx: int,
    text_len: int,
) -> Optional[str]:
    """
    Return an error string if *ent* is invalid, else None.
    """
    if not isinstance(ent, dict):
        return f"not a dict (got {type(ent).__name__})"

    missing = {"label", "start", "end"} - ent.keys()
    if missing:
        return f"missing required keys: {missing}"

    start = ent["start"]
    end   = ent["end"]

    if not isinstance(start, int) or not isinstance(end, int):
        return f"start/end must be int, got ({type(start).__name__}, {type(end).__name__})"

    if start < 0:
        return f"start ({start}) is negative"

    if end > text_len:
        return (
            f"end ({end}) exceeds text length ({text_len}); "
            "ensure entities were generated from the same (possibly truncated) text"
        )

    if start >= end:
        return f"invalid span: start ({start}) >= end ({end})"

    return None