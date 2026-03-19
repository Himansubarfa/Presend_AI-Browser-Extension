
# day 23 update by claude

"""
detector.py – PII / entity detection pipeline.

Detection sources (in merge order):
  1. Presidio (optional HTTP sidecar)
  2. spaCy NER  (PERSON, ORG)
  3. Regex rules (EMAIL, PHONE, CARD, AADHAAR, ID, ADDRESS, PERSON, ORG)

Overlap resolution: higher-priority label wins; ties broken by span length.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional

import requests

from .config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy – loaded once at import time
# ---------------------------------------------------------------------------
try:
    import spacy as _spacy_mod

    _nlp: Optional[_spacy_mod.Language] = _spacy_mod.load(
        "en_core_web_sm",
        disable=["tagger", "parser", "attribute_ruler", "lemmatizer"],
    )
    logger.info("spaCy model 'en_core_web_sm' loaded (NER only).")
except OSError:
    _nlp = None
    logger.error(
        "spaCy model 'en_core_web_sm' not found. "
        "Run: python -m spacy download en_core_web_sm"
    )
except Exception:  # noqa: BLE001
    _nlp = None
    logger.exception("Unexpected error while loading spaCy model.")


def _get_spacy_model() -> Optional[Any]:
    return _nlp


# ---------------------------------------------------------------------------
# Priority map  (higher = wins overlap resolution)
# ---------------------------------------------------------------------------
PRIORITY_MAP: Dict[str, int] = {
    "EMAIL":   5,
    "PHONE":   4,
    "ADDRESS": 3,
    "AADHAAR": 2,
    "CARD":    2,
    "ID":      2,
    "ORG":     1,
    "PERSON":  1,
}

# ---------------------------------------------------------------------------
# Common names (de-duplicated)
# ---------------------------------------------------------------------------
COMMON_NAMES: frozenset[str] = frozenset({
    # Indian
    "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
    "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
    "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
    "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
    "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
    "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
    "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
    "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
    "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
    "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
    "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
    "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
    "sneha", "sejal",
    # Surnames / family names
    "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
    "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
    "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
    "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
    "chavan", "nikam", "kadam", "bhosle", "kohli",
    # Western
    "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
    "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
    "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
    "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
    "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
    "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
    "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
    "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
    "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
    "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
    "larry", "catherine", "justin", "christine", "scott", "heather",
    "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
    "victoria", "alexander", "kelly", "patrick", "christina", "frank",
    "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
    "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "tiffany",
    "amber", "danielle", "abigail", "russell", "bobby", "phillip",
    # Arabic / Middle-Eastern
    "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
    # Chinese / East Asian
    "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
    # Spanish / Latin
    "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
    # Russian / Eastern European
    "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
    # Japanese
    "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
    "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
    # Korean
    "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
    "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
    # Extra
    "jacky",
})

# ---------------------------------------------------------------------------
# Organisation word lists
# ---------------------------------------------------------------------------
SINGLE_WORD_ORGS: frozenset[str] = frozenset({
    "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
    "spotify", "twitter", "linkedin", "whatsapp", "youtube", "instagram",
    "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
    "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
    "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "philips",
    "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
    "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
    "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
    "adidas", "nike", "puma", "reebok", "zara", "gucci", "prada",
    "chanel", "hermes", "cartier", "rolex", "omega",
    "ebay", "paypal", "visa", "mastercard", "discover", "jpmorgan",
    "starbucks", "subway", "kfc",
})

MULTI_WORD_ORGS: frozenset[str] = frozenset({
    "american express",
    "jp morgan chase",
    "goldman sachs",
    "morgan stanley",
    "bank of america",
    "wells fargo",
    "new york times",
    "wall street journal",
    "los angeles times",
    "united nations",
    "world health organization",
    "international monetary fund",
    "burger king",
    "domino's pizza",
    "starbucks coffee",
    "coca cola",
    "pizza hut",
    "louis vuitton",
})

# All-caps tokens that are NOT organisations (noise filter)
_ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
    "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
    "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
    "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
    "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
    "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
    "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
    "PNG", "JPG", "ZIP", "ETA", "OTP", "PIN",
})

# ---------------------------------------------------------------------------
# Pre-compiled regexes
# ---------------------------------------------------------------------------

# Email
_EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# Phone – international-friendly, requires ≥10 digits
_PHONE_RE = re.compile(
    r'(?<!\d)'                             # not preceded by a digit
    r'(?:\+\d{1,3}[\s\-.]?)?'             # optional country code
    r'(?:\(?\d{3}\)?[\s\-.]?)'            # area code
    r'\d{3}[\s\-.]?\d{4}'                 # local number
    r'(?!\d)',                             # not followed by a digit
    re.ASCII,
)

# Credit card – exactly 16 digits in groups of 4
_CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')

# Aadhaar – exactly 12 digits in groups of 4 (must NOT be part of a 16-digit card)
_AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# Generic numeric ID – 9 to 15 pure digits (avoid overlapping with card above)
_ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# Address – anchored with number + known suffix, capped at 80 chars
_ADDRESS_SUFFIX = (
    r'(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|'
    r'court|ct|plaza|way|apt|bldg|suite|ste|nagar|colony|sector)'
)
_ADDRESS_RE = re.compile(
    r'\b\d{1,5}[ \t]+[A-Za-z]{2,}(?:[ \t]+[A-Za-z]{2,}){0,4}'
    r'(?:[ \t]+' + _ADDRESS_SUFFIX + r')?\b',
    re.IGNORECASE,
)

# Common names
_COMMON_NAMES_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(n) for n in sorted(COMMON_NAMES, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# Single-word orgs  (sorted longest-first to prefer longer matches)
_SINGLE_WORD_ORGS_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(o) for o in sorted(SINGLE_WORD_ORGS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# Multi-word orgs
_MULTI_WORD_ORGS_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(p) for p in sorted(MULTI_WORD_ORGS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# All-caps orgs: 3–10 letters, not in stop-word list
_ALLCAPS_ORG_RE = re.compile(r'\b[A-Z]{3,10}\b')

# ---------------------------------------------------------------------------
# Input sanitisation
# ---------------------------------------------------------------------------

def _sanitise(text: str) -> str:
    """
    Remove or replace characters that can crash spaCy or regex engines:
      - Null bytes
      - C0/C1 control characters (keep newline, tab, carriage return)
      - Lone surrogates
    Then normalise to NFC.
    """
    # Replace null bytes
    text = text.replace("\x00", " ")
    # Remove C0 control chars except \t \n \r; remove C1 range
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
    # Replace lone surrogates (can appear in Python strings decoded from surrogatepass)
    text = re.sub(r'[\ud800-\udfff]', '\ufffd', text)
    # Unicode NFC normalisation (collapses composed forms)
    try:
        text = unicodedata.normalize("NFC", text)
    except Exception:  # noqa: BLE001
        pass
    return text


# ---------------------------------------------------------------------------
# Presidio client (optional)
# ---------------------------------------------------------------------------

_PRESIDIO_LABEL_MAP: Dict[str, Optional[str]] = {
    "PERSON":         "PERSON",
    "EMAIL_ADDRESS":  "EMAIL",
    "PHONE_NUMBER":   "PHONE",
    "CREDIT_CARD":    "CARD",
    "ORGANIZATION":   "ORG",
    "ADDRESS":        "ADDRESS",
    "ID":             "ID",
    # deliberately unmapped
    "LOCATION":       None,
    "DATE_TIME":      None,
}


def _detect_with_presidio(text: str) -> List[Dict[str, Any]]:
    url = getattr(Config, "PRESIDIO_ANALYZER_URL", None)
    if not url:
        return []
    try:
        response = requests.post(
            url,
            json={"text": text, "language": "en"},
            timeout=2.0,
        )
        if response.status_code != 200:
            logger.warning(
                "Presidio returned HTTP %d: %s",
                response.status_code,
                response.text[:200],
            )
            return []
        converted: List[Dict[str, Any]] = []
        for e in response.json():
            mapped = _PRESIDIO_LABEL_MAP.get(e.get("entity_type", ""))
            if mapped:
                converted.append({
                    "label": mapped,
                    "text":  e.get("text", ""),
                    "start": int(e["start"]),
                    "end":   int(e["end"]),
                })
        return converted
    except requests.exceptions.Timeout:
        logger.warning("Presidio request timed out.")
    except Exception:  # noqa: BLE001
        logger.warning("Presidio detection failed.", exc_info=True)
    return []


# ---------------------------------------------------------------------------
# Individual regex detectors
# ---------------------------------------------------------------------------

def _spans(label: str, pattern: re.Pattern, text: str) -> List[Dict[str, Any]]:
    """Generic helper: collect all non-overlapping regex matches."""
    return [
        {"label": label, "text": m.group(), "start": m.start(), "end": m.end()}
        for m in pattern.finditer(text)
    ]


def _detect_emails(text: str) -> List[Dict[str, Any]]:
    return _spans("EMAIL", _EMAIL_RE, text)


def _detect_phones(text: str) -> List[Dict[str, Any]]:
    return _spans("PHONE", _PHONE_RE, text)


def _detect_cards(text: str) -> List[Dict[str, Any]]:
    return _spans("CARD", _CARD_RE, text)


def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
    """
    Match 12-digit Aadhaar numbers.  Reject matches whose raw digit run
    is exactly 16 (those are credit card numbers caught by _CARD_RE).
    """
    result = []
    for m in _AADHAAR_RE.finditer(text):
    # Count actual digits only
        digits = re.sub(r'\D', '', m.group())
        if len(digits) == 12:
            result.append({"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()})
    return result


def _detect_ids(text: str) -> List[Dict[str, Any]]:
    """
    Generic numeric ID (9–15 digits).
    Skip if it matches a card or Aadhaar pattern (handled by dedicated detectors).
    """
    result = []
    for m in _ID_RE.finditer(text):
        raw = re.sub(r'\D', '', m.group())
        if len(raw) in (12, 16):
            # Let AADHAAR / CARD detectors handle these
            continue
        result.append({"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()})
    return result


def _detect_addresses(text: str) -> List[Dict[str, Any]]:
    suffix_pat = re.compile(_ADDRESS_SUFFIX, re.IGNORECASE)
    result = []
    for m in _ADDRESS_RE.finditer(text):
        span = m.group()
        if not (10 < len(span) < 80):
            continue
        if not re.search(r'\b\d+\b', span):
            continue
        if not suffix_pat.search(span):
            continue
        result.append({"label": "ADDRESS", "text": span, "start": m.start(), "end": m.end()})
    return result


def _detect_common_names(text: str) -> List[Dict[str, Any]]:
    return _spans("PERSON", _COMMON_NAMES_RE, text)


def _detect_single_word_orgs(text: str) -> List[Dict[str, Any]]:
    return _spans("ORG", _SINGLE_WORD_ORGS_RE, text)


def _detect_multi_word_orgs(text: str) -> List[Dict[str, Any]]:
    return _spans("ORG", _MULTI_WORD_ORGS_RE, text)


def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _ALLCAPS_ORG_RE.finditer(text):
        token = m.group()
        if token not in _ALLCAPS_ORG_STOPWORDS:
            result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
    return result


# ---------------------------------------------------------------------------
# Public spaCy wrapper
# ---------------------------------------------------------------------------

def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
    if not text or _nlp is None:
        return []
    detected: List[Dict[str, Any]] = []
    try:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG"}:
                detected.append({
                    "label": ent.label_,
                    "text":  ent.text,
                    "start": ent.start_char,
                    "end":   ent.end_char,
                })
    except Exception:  # noqa: BLE001
        logger.exception("spaCy processing failed.")
    return detected


# ---------------------------------------------------------------------------
# Public regex wrapper
# ---------------------------------------------------------------------------

def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    entities: List[Dict[str, Any]] = []
    try:
        entities.extend(_detect_emails(text))
        entities.extend(_detect_phones(text))
        entities.extend(_detect_cards(text))
        entities.extend(_detect_aadhaar(text))
        entities.extend(_detect_ids(text))
        entities.extend(_detect_addresses(text))
        entities.extend(_detect_common_names(text))
        entities.extend(_detect_single_word_orgs(text))
        entities.extend(_detect_multi_word_orgs(text))
        entities.extend(_detect_allcaps_orgs(text))
    except Exception:  # noqa: BLE001
        logger.exception("Regex detection failed.")
    return entities


# ---------------------------------------------------------------------------
# Post-processing helpers
# ---------------------------------------------------------------------------

def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove exact (start, end, label) duplicates."""
    seen: set[tuple] = set()
    unique: List[Dict[str, Any]] = []
    for span in spans:
        key = (span["start"], span["end"], span["label"])
        if key not in seen:
            seen.add(key)
            unique.append(span)
    return unique


def _validate_entities(entities: List[Dict[str, Any]]) -> None:
    """Raise ValueError on malformed entity dicts (fail-fast, called once)."""
    required = {"label", "start", "end"}
    for idx, ent in enumerate(entities):
        missing = required - ent.keys()
        if missing:
            raise ValueError(f"Entity[{idx}] missing keys {missing}: {ent!r}")
        if not isinstance(ent["start"], int) or not isinstance(ent["end"], int):
            raise ValueError(f"Entity[{idx}] start/end must be int: {ent!r}")
        if ent["start"] < 0 or ent["end"] <= ent["start"]:
            raise ValueError(f"Entity[{idx}] invalid span [{ent['start']}, {ent['end']}): {ent!r}")


def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Given a list of entities (each with label/start/end), return a subset
    with no overlapping spans.  When two spans overlap the higher-priority
    label wins; ties are broken by span length (longer wins).
    """
    if not entities:
        return []

    _validate_entities(entities)

    sorted_ents = sorted(
        entities,
        key=lambda e: (
            e["start"],
            -PRIORITY_MAP.get(e["label"], 0),
            -(e["end"] - e["start"]),
        ),
    )

    resolved: List[Dict[str, Any]] = []
    current = sorted_ents[0]

    for nxt in sorted_ents[1:]:
        if nxt["start"] < current["end"]:          # overlapping
            cur_prio = PRIORITY_MAP.get(current["label"], 0)
            nxt_prio = PRIORITY_MAP.get(nxt["label"], 0)
            cur_len  = current["end"] - current["start"]
            nxt_len  = nxt["end"]     - nxt["start"]
            if nxt_prio > cur_prio or (nxt_prio == cur_prio and nxt_len > cur_len):
                current = nxt
        else:
            resolved.append(current)
            current = nxt

    resolved.append(current)
    logger.debug("resolve_overlaps: %d → %d entities", len(entities), len(resolved))
    return resolved


# ---------------------------------------------------------------------------
# Main public entry point
# ---------------------------------------------------------------------------

def detect_entities(raw_text: Any) -> List[Dict[str, Any]]:
    """
    Detect PII / named entities in *raw_text*.

    Accepts any input; non-string values are coerced to str.
    Returns an empty list for None, empty, or oversized input.
    """
    # --- type coercion ---
    if raw_text is None:
        return []
    if not isinstance(raw_text, str):
        try:
            raw_text = str(raw_text)
        except Exception:  # noqa: BLE001
            logger.warning("Could not coerce input to str; returning empty.")
            return []

    # --- empty check ---
    raw_text = raw_text.strip()
    if not raw_text:
        return []

    # --- length guard (process truncated chunk rather than returning nothing) ---
    max_len: int = getattr(Config, "MAX_TEXT_LENGTH", 100_000)
    if len(raw_text) > max_len:
        logger.warning(
            "Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.",
            len(raw_text),
            max_len,
        )
        raw_text = raw_text[:max_len]

    # --- sanitise (remove nulls, surrogates, control chars) ---
    raw_text = _sanitise(raw_text)
    if not raw_text.strip():
        return []

    # --- detection ---
    presidio_spans = _detect_with_presidio(raw_text)
    spacy_spans    = detect_spacy_entities(raw_text)
    regex_spans    = detect_regex_entities(raw_text)

    all_spans = presidio_spans + spacy_spans + regex_spans
    if not all_spans:
        return []

    all_spans = deduplicate_spans(all_spans)

    try:
        return resolve_overlaps(all_spans)
    except ValueError:
        logger.exception("resolve_overlaps encountered invalid entities; returning raw deduplicated spans.")
        return all_spans