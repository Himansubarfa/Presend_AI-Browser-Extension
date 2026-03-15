# """
# detector.py – PII / entity detection pipeline.

# Detection sources (in merge order):
#   1. Presidio (optional HTTP sidecar)
#   2. spaCy NER  (PERSON, ORG)
#   3. Regex rules (EMAIL, PHONE, CARD, AADHAAR, ID, ADDRESS, PERSON, ORG)

# Overlap resolution: higher-priority label wins; ties broken by span length.
# """

# from __future__ import annotations

# import logging
# import re
# import unicodedata
# from typing import Any, Dict, List, Optional

# import requests

# from .config import Config

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # spaCy – loaded once at import time
# # ---------------------------------------------------------------------------
# try:
#     import spacy as _spacy_mod

#     _nlp: Optional[_spacy_mod.Language] = _spacy_mod.load(
#         "en_core_web_sm",
#         disable=["tagger", "parser", "attribute_ruler", "lemmatizer"],
#     )
#     logger.info("spaCy model 'en_core_web_sm' loaded (NER only).")
# except OSError:
#     _nlp = None
#     logger.error(
#         "spaCy model 'en_core_web_sm' not found. "
#         "Run: python -m spacy download en_core_web_sm"
#     )
# except Exception:  # noqa: BLE001
#     _nlp = None
#     logger.exception("Unexpected error while loading spaCy model.")


# def _get_spacy_model() -> Optional[Any]:
#     return _nlp


# # ---------------------------------------------------------------------------
# # Priority map  (higher = wins overlap resolution)
# # ---------------------------------------------------------------------------
# PRIORITY_MAP: Dict[str, int] = {
#     "EMAIL":   5,
#     "PHONE":   4,
#     "ADDRESS": 3,
#     "AADHAAR": 2,
#     "CARD":    2,
#     "ID":      2,
#     "ORG":     1,
#     "PERSON":  1,
# }

# # ---------------------------------------------------------------------------
# # Common names (de-duplicated)
# # ---------------------------------------------------------------------------
# COMMON_NAMES: frozenset[str] = frozenset({
#     # Indian
#     "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
#     "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
#     "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
#     "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
#     "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
#     "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
#     "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
#     "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
#     "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
#     "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
#     "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
#     "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
#     "sneha", "sejal",
#     # Surnames / family names
#     "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
#     "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
#     "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
#     "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
#     "chavan", "nikam", "kadam", "bhosle", "kohli",
#     # Western
#     "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
#     "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
#     "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
#     "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
#     "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
#     "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
#     "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
#     "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
#     "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
#     "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
#     "larry", "catherine", "justin", "christine", "scott", "heather",
#     "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
#     "victoria", "alexander", "kelly", "patrick", "christina", "frank",
#     "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
#     "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "tiffany",
#     "amber", "danielle", "abigail", "russell", "bobby", "phillip",
#     # Arabic / Middle-Eastern
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     # Chinese / East Asian
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     # Spanish / Latin
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     # Russian / Eastern European
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     # Japanese
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     # Korean
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
#     # Extra
#     "jacky",
# })

# # ---------------------------------------------------------------------------
# # Organisation word lists
# # ---------------------------------------------------------------------------
# SINGLE_WORD_ORGS: frozenset[str] = frozenset({
#     "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
#     "spotify", "twitter", "linkedin", "whatsapp", "youtube", "instagram",
#     "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
#     "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
#     "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "philips",
#     "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
#     "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
#     "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
#     "adidas", "nike", "puma", "reebok", "zara", "gucci", "prada",
#     "chanel", "hermes", "cartier", "rolex", "omega",
#     "ebay", "paypal", "visa", "mastercard", "discover", "jpmorgan",
#     "starbucks", "subway", "kfc",
# })

# MULTI_WORD_ORGS: frozenset[str] = frozenset({
#     "american express",
#     "jp morgan chase",
#     "goldman sachs",
#     "morgan stanley",
#     "bank of america",
#     "wells fargo",
#     "new york times",
#     "wall street journal",
#     "los angeles times",
#     "united nations",
#     "world health organization",
#     "international monetary fund",
#     "burger king",
#     "domino's pizza",
#     "starbucks coffee",
#     "coca cola",
#     "pizza hut",
#     "louis vuitton",
# })

# # All-caps tokens that are NOT organisations (noise filter)
# _ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
#     "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
#     "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
#     "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
#     "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
#     "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
#     "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
#     "PNG", "JPG", "ZIP", "ETA", "OTP", "PIN",
# })

# # ---------------------------------------------------------------------------
# # Pre-compiled regexes
# # ---------------------------------------------------------------------------

# # Email
# _EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# # Phone – international-friendly, requires ≥10 digits
# _PHONE_RE = re.compile(
#     r'(?<!\d)'                             # not preceded by a digit
#     r'(?:\+\d{1,3}[\s\-.]?)?'             # optional country code
#     r'(?:\(?\d{3}\)?[\s\-.]?)'            # area code
#     r'\d{3}[\s\-.]?\d{4}'                 # local number
#     r'(?!\d)',                             # not followed by a digit
#     re.ASCII,
# )

# # Credit card – exactly 16 digits in groups of 4
# _CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')

# # Aadhaar – exactly 12 digits in groups of 4 (must NOT be part of a 16-digit card)
# _AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# # Generic numeric ID – 9 to 15 pure digits (avoid overlapping with card above)
# _ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# # Address – anchored with number + known suffix, capped at 80 chars
# _ADDRESS_SUFFIX = (
#     r'(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|'
#     r'court|ct|plaza|way|apt|bldg|suite|ste|nagar|colony|sector)'
# )
# _ADDRESS_RE = re.compile(
#     r'\b\d{1,5}[ \t]+[A-Za-z]{2,}(?:[ \t]+[A-Za-z]{2,}){0,4}'
#     r'(?:[ \t]+' + _ADDRESS_SUFFIX + r')?\b',
#     re.IGNORECASE,
# )

# # Common names
# _COMMON_NAMES_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(n) for n in sorted(COMMON_NAMES, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # Single-word orgs  (sorted longest-first to prefer longer matches)
# _SINGLE_WORD_ORGS_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(o) for o in sorted(SINGLE_WORD_ORGS, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # Multi-word orgs
# _MULTI_WORD_ORGS_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(p) for p in sorted(MULTI_WORD_ORGS, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # All-caps orgs: 3–10 letters, not in stop-word list
# _ALLCAPS_ORG_RE = re.compile(r'\b[A-Z]{3,10}\b')

# # ---------------------------------------------------------------------------
# # Input sanitisation
# # ---------------------------------------------------------------------------

# def _sanitise(text: str) -> str:
#     """
#     Remove or replace characters that can crash spaCy or regex engines:
#       - Null bytes
#       - C0/C1 control characters (keep newline, tab, carriage return)
#       - Lone surrogates
#     Then normalise to NFC.
#     """
#     # Replace null bytes
#     text = text.replace("\x00", " ")
#     # Remove C0 control chars except \t \n \r; remove C1 range
#     text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
#     # Replace lone surrogates (can appear in Python strings decoded from surrogatepass)
#     text = re.sub(r'[\ud800-\udfff]', '\ufffd', text)
#     # Unicode NFC normalisation (collapses composed forms)
#     try:
#         text = unicodedata.normalize("NFC", text)
#     except Exception:  # noqa: BLE001
#         pass
#     return text


# # ---------------------------------------------------------------------------
# # Presidio client (optional)
# # ---------------------------------------------------------------------------

# _PRESIDIO_LABEL_MAP: Dict[str, Optional[str]] = {
#     "PERSON":         "PERSON",
#     "EMAIL_ADDRESS":  "EMAIL",
#     "PHONE_NUMBER":   "PHONE",
#     "CREDIT_CARD":    "CARD",
#     "ORGANIZATION":   "ORG",
#     "ADDRESS":        "ADDRESS",
#     "ID":             "ID",
#     # deliberately unmapped
#     "LOCATION":       None,
#     "DATE_TIME":      None,
# }


# def _detect_with_presidio(text: str) -> List[Dict[str, Any]]:
#     url = getattr(Config, "PRESIDIO_ANALYZER_URL", None)
#     if not url:
#         return []
#     try:
#         response = requests.post(
#             url,
#             json={"text": text, "language": "en"},
#             timeout=2.0,
#         )
#         if response.status_code != 200:
#             logger.warning(
#                 "Presidio returned HTTP %d: %s",
#                 response.status_code,
#                 response.text[:200],
#             )
#             return []
#         converted: List[Dict[str, Any]] = []
#         for e in response.json():
#             mapped = _PRESIDIO_LABEL_MAP.get(e.get("entity_type", ""))
#             if mapped:
#                 converted.append({
#                     "label": mapped,
#                     "text":  e.get("text", ""),
#                     "start": int(e["start"]),
#                     "end":   int(e["end"]),
#                 })
#         return converted
#     except requests.exceptions.Timeout:
#         logger.warning("Presidio request timed out.")
#     except Exception:  # noqa: BLE001
#         logger.warning("Presidio detection failed.", exc_info=True)
#     return []


# # ---------------------------------------------------------------------------
# # Individual regex detectors
# # ---------------------------------------------------------------------------

# def _spans(label: str, pattern: re.Pattern, text: str) -> List[Dict[str, Any]]:
#     """Generic helper: collect all non-overlapping regex matches."""
#     return [
#         {"label": label, "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in pattern.finditer(text)
#     ]


# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     return _spans("EMAIL", _EMAIL_RE, text)


# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     return _spans("PHONE", _PHONE_RE, text)


# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     return _spans("CARD", _CARD_RE, text)


# def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
#     """
#     Match 12-digit Aadhaar numbers.  Reject matches whose raw digit run
#     is exactly 16 (those are credit card numbers caught by _CARD_RE).
#     """
#     result = []
#     for m in _AADHAAR_RE.finditer(text):
#     # Count actual digits only
#         digits = re.sub(r'\D', '', m.group())
#         if len(digits) == 12:
#             result.append({"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()})
#     return result


# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     """
#     Generic numeric ID (9–15 digits).
#     Skip if it matches a card or Aadhaar pattern (handled by dedicated detectors).
#     """
#     result = []
#     for m in _ID_RE.finditer(text):
#         raw = re.sub(r'\D', '', m.group())
#         if len(raw) in (12, 16):
#             # Let AADHAAR / CARD detectors handle these
#             continue
#         result.append({"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()})
#     return result


# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     suffix_pat = re.compile(_ADDRESS_SUFFIX, re.IGNORECASE)
#     result = []
#     for m in _ADDRESS_RE.finditer(text):
#         span = m.group()
#         if not (10 < len(span) < 80):
#             continue
#         if not re.search(r'\b\d+\b', span):
#             continue
#         if not suffix_pat.search(span):
#             continue
#         result.append({"label": "ADDRESS", "text": span, "start": m.start(), "end": m.end()})
#     return result


# def _detect_common_names(text: str) -> List[Dict[str, Any]]:
#     return _spans("PERSON", _COMMON_NAMES_RE, text)


# def _detect_single_word_orgs(text: str) -> List[Dict[str, Any]]:
#     return _spans("ORG", _SINGLE_WORD_ORGS_RE, text)


# def _detect_multi_word_orgs(text: str) -> List[Dict[str, Any]]:
#     return _spans("ORG", _MULTI_WORD_ORGS_RE, text)


# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _ALLCAPS_ORG_RE.finditer(text):
#         token = m.group()
#         if token not in _ALLCAPS_ORG_STOPWORDS:
#             result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
#     return result


# # ---------------------------------------------------------------------------
# # Public spaCy wrapper
# # ---------------------------------------------------------------------------

# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     if not text or _nlp is None:
#         return []
#     detected: List[Dict[str, Any]] = []
#     try:
#         doc = _nlp(text)
#         for ent in doc.ents:
#             if ent.label_ in {"PERSON", "ORG"}:
#                 detected.append({
#                     "label": ent.label_,
#                     "text":  ent.text,
#                     "start": ent.start_char,
#                     "end":   ent.end_char,
#                 })
#     except Exception:  # noqa: BLE001
#         logger.exception("spaCy processing failed.")
#     return detected


# # ---------------------------------------------------------------------------
# # Public regex wrapper
# # ---------------------------------------------------------------------------

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities: List[Dict[str, Any]] = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_aadhaar(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_common_names(text))
#         entities.extend(_detect_single_word_orgs(text))
#         entities.extend(_detect_multi_word_orgs(text))
#         entities.extend(_detect_allcaps_orgs(text))
#     except Exception:  # noqa: BLE001
#         logger.exception("Regex detection failed.")
#     return entities


# # ---------------------------------------------------------------------------
# # Post-processing helpers
# # ---------------------------------------------------------------------------

# def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Remove exact (start, end, label) duplicates."""
#     seen: set[tuple] = set()
#     unique: List[Dict[str, Any]] = []
#     for span in spans:
#         key = (span["start"], span["end"], span["label"])
#         if key not in seen:
#             seen.add(key)
#             unique.append(span)
#     return unique


# def _validate_entities(entities: List[Dict[str, Any]]) -> None:
#     """Raise ValueError on malformed entity dicts (fail-fast, called once)."""
#     required = {"label", "start", "end"}
#     for idx, ent in enumerate(entities):
#         missing = required - ent.keys()
#         if missing:
#             raise ValueError(f"Entity[{idx}] missing keys {missing}: {ent!r}")
#         if not isinstance(ent["start"], int) or not isinstance(ent["end"], int):
#             raise ValueError(f"Entity[{idx}] start/end must be int: {ent!r}")
#         if ent["start"] < 0 or ent["end"] <= ent["start"]:
#             raise ValueError(f"Entity[{idx}] invalid span [{ent['start']}, {ent['end']}): {ent!r}")


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Given a list of entities (each with label/start/end), return a subset
#     with no overlapping spans.  When two spans overlap the higher-priority
#     label wins; ties are broken by span length (longer wins).
#     """
#     if not entities:
#         return []

#     _validate_entities(entities)

#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (
#             e["start"],
#             -PRIORITY_MAP.get(e["label"], 0),
#             -(e["end"] - e["start"]),
#         ),
#     )

#     resolved: List[Dict[str, Any]] = []
#     current = sorted_ents[0]

#     for nxt in sorted_ents[1:]:
#         if nxt["start"] < current["end"]:          # overlapping
#             cur_prio = PRIORITY_MAP.get(current["label"], 0)
#             nxt_prio = PRIORITY_MAP.get(nxt["label"], 0)
#             cur_len  = current["end"] - current["start"]
#             nxt_len  = nxt["end"]     - nxt["start"]
#             if nxt_prio > cur_prio or (nxt_prio == cur_prio and nxt_len > cur_len):
#                 current = nxt
#         else:
#             resolved.append(current)
#             current = nxt

#     resolved.append(current)
#     logger.debug("resolve_overlaps: %d → %d entities", len(entities), len(resolved))
#     return resolved


# # ---------------------------------------------------------------------------
# # Main public entry point
# # ---------------------------------------------------------------------------

# def detect_entities(raw_text: Any) -> List[Dict[str, Any]]:
#     """
#     Detect PII / named entities in *raw_text*.

#     Accepts any input; non-string values are coerced to str.
#     Returns an empty list for None, empty, or oversized input.
#     """
#     # --- type coercion ---
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         try:
#             raw_text = str(raw_text)
#         except Exception:  # noqa: BLE001
#             logger.warning("Could not coerce input to str; returning empty.")
#             return []

#     # --- empty check ---
#     raw_text = raw_text.strip()
#     if not raw_text:
#         return []

#     # --- length guard (process truncated chunk rather than returning nothing) ---
#     max_len: int = getattr(Config, "MAX_TEXT_LENGTH", 100_000)
#     if len(raw_text) > max_len:
#         logger.warning(
#             "Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.",
#             len(raw_text),
#             max_len,
#         )
#         raw_text = raw_text[:max_len]

#     # --- sanitise (remove nulls, surrogates, control chars) ---
#     raw_text = _sanitise(raw_text)
#     if not raw_text.strip():
#         return []

#     # --- detection ---
#     presidio_spans = _detect_with_presidio(raw_text)
#     spacy_spans    = detect_spacy_entities(raw_text)
#     regex_spans    = detect_regex_entities(raw_text)

#     all_spans = presidio_spans + spacy_spans + regex_spans
#     if not all_spans:
#         return []

#     all_spans = deduplicate_spans(all_spans)

#     try:
#         return resolve_overlaps(all_spans)
#     except ValueError:
#         logger.exception("resolve_overlaps encountered invalid entities; returning raw deduplicated spans.")
#         return all_spans

# day 24 final update 
# """
# detector.py – PII / entity detection pipeline.

# Detection sources (in merge order):
#   1. Presidio (optional HTTP sidecar)
#   2. spaCy NER  (PERSON, ORG, GPE)
#   3. Regex rules:
#        Core  : EMAIL, PHONE, CARD, AADHAAR, ID, ADDRESS
#        India : PAN, PASSPORT, DRIVING_LICENCE, PINCODE, VEHICLE_REG,
#                GST, IFSC, UPI
#        General: DOB, IP, URL, SALARY, PERSON, ORG

# Overlap resolution: higher-priority label wins; ties broken by span length.
# """

# from __future__ import annotations

# import logging
# import re
# import unicodedata
# from typing import Any, Dict, List, Optional

# import requests

# from .config import Config

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # spaCy – loaded once at import time
# # ---------------------------------------------------------------------------
# try:
#     import spacy as _spacy_mod

#     _nlp: Optional[_spacy_mod.Language] = _spacy_mod.load(
#         "en_core_web_sm",
#         disable=["tagger", "parser", "attribute_ruler", "lemmatizer"],
#     )
#     logger.info("spaCy model 'en_core_web_sm' loaded (NER only).")
# except OSError:
#     _nlp = None
#     logger.error(
#         "spaCy model 'en_core_web_sm' not found. "
#         "Run: python -m spacy download en_core_web_sm"
#     )
# except Exception:  # noqa: BLE001
#     _nlp = None
#     logger.exception("Unexpected error while loading spaCy model.")


# def _get_spacy_model() -> Optional[Any]:
#     return _nlp


# # ---------------------------------------------------------------------------
# # Priority map  (higher = wins overlap resolution)
# # ---------------------------------------------------------------------------
# PRIORITY_MAP: Dict[str, int] = {
#     "EMAIL":            7,
#     "PHONE":            6,
#     "CARD":             5,
#     "AADHAAR":          5,
#     "PAN":              5,
#     "PASSPORT":         5,
#     "DRIVING_LICENCE":  5,
#     "GST":              5,
#     "IFSC":             5,
#     "UPI":              5,
#     "VEHICLE_REG":      4,
#     "IP":               4,
#     "URL":              4,
#     "ADDRESS":          3,
#     "PINCODE":          3,
#     "DOB":              3,
#     "SALARY":           3,
#     "ID":               2,
#     "ORG":              1,
#     "PERSON":           1,
#     "LOCATION":         1,
# }

# # ---------------------------------------------------------------------------
# # Common names (de-duplicated)
# # ---------------------------------------------------------------------------
# COMMON_NAMES: frozenset[str] = frozenset({
#     # Indian first names
#     "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
#     "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
#     "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
#     "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
#     "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
#     "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
#     "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
#     "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
#     "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
#     "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
#     "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
#     "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
#     "sneha", "sejal", "rohan", "arun", "sudhir", "ramesh", "dinesh", "girish",
#     "harish", "naresh", "prakash", "rajesh", "suresh", "umesh", "vinod",
#     "ashok", "devesh", "ganesh", "jagdish", "kamlesh", "lokesh", "mukesh",
#     "nilesh", "omkar", "pramod", "ritesh", "santosh", "tapan", "vaibhav",
#     # Indian surnames
#     "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
#     "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
#     "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
#     "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
#     "chavan", "nikam", "kadam", "bhosle", "kohli", "malhotra", "kapoor",
#     "khanna", "chopra", "bose", "mukherjee", "chatterjee", "banerjee",
#     "chakraborty", "iyer", "nair", "menon", "pillai", "krishnan", "narayanan",
#     "venkatesh", "subramaniam", "rajan", "krishnamurthy", "swaminathan",
#     # Western first names
#     "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
#     "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
#     "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
#     "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
#     "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
#     "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
#     "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
#     "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
#     "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
#     "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
#     "larry", "catherine", "justin", "christine", "scott", "heather",
#     "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
#     "victoria", "alexander", "kelly", "patrick", "christina", "frank",
#     "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
#     "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "tiffany",
#     "amber", "danielle", "abigail", "russell", "bobby", "phillip",
#     # Arabic / Middle-Eastern
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     # Chinese / East Asian
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     # Spanish / Latin
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     # Russian / Eastern European
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     # Japanese
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     # Korean
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
#     # Extra
#     "jacky",
# })

# # ---------------------------------------------------------------------------
# # Indian cities / locations
# # ---------------------------------------------------------------------------
# INDIAN_CITIES: frozenset[str] = frozenset({
#     "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "ahmedabad",
#     "chennai", "kolkata", "surat", "pune", "jaipur", "lucknow", "kanpur",
#     "nagpur", "indore", "thane", "bhopal", "visakhapatnam", "patna",
#     "vadodara", "ghaziabad", "ludhiana", "agra", "nashik", "ranchi",
#     "faridabad", "meerut", "rajkot", "varanasi", "srinagar", "aurangabad",
#     "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj",
#     "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada", "jodhpur",
#     "madurai", "raipur", "kota", "chandigarh", "guwahati", "thiruvananthapuram",
#     "solapur", "hubli", "dharwad", "tiruchirappalli", "mysore", "mysuru",
#     "bareilly", "aligarh", "moradabad", "jalandhar", "bhubaneswar", "salem",
#     "warangal", "mira bhayandar", "jamshedpur", "noida", "gurugram",
#     "gurgaon", "noidaextension", "greater noida", "kochi", "ernakulam",
#     "dehradun", "shimla", "jammu", "leh", "panaji", "goa", "kolhapur",
#     "akola", "latur", "nanded", "sangli", "jalgaon", "amravati",
#     # States
#     "maharashtra", "karnataka", "gujarat", "rajasthan", "uttar pradesh",
#     "madhya pradesh", "tamil nadu", "andhra pradesh", "telangana",
#     "west bengal", "kerala", "punjab", "haryana", "bihar", "jharkhand",
#     "odisha", "assam", "chhattisgarh", "uttarakhand", "himachal pradesh",
#     "goa", "manipur", "meghalaya", "mizoram", "nagaland", "sikkim",
#     "arunachal pradesh", "tripura",
# })

# # ---------------------------------------------------------------------------
# # Organisation word lists
# # ---------------------------------------------------------------------------
# SINGLE_WORD_ORGS: frozenset[str] = frozenset({
#     "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
#     "spotify", "twitter", "linkedin", "whatsapp", "youtube", "instagram",
#     "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
#     "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
#     "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "philips",
#     "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
#     "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
#     "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
#     "adidas", "nike", "puma", "reebok", "zara", "gucci", "prada",
#     "chanel", "hermes", "cartier", "rolex", "omega",
#     "ebay", "paypal", "visa", "mastercard", "discover", "jpmorgan",
#     "starbucks", "subway", "kfc",
#     # Indian companies / banks
#     "infosys", "wipro", "tcs", "hcl", "reliance", "hdfc", "icici", "sbi",
#     "axis", "kotak", "bajaj", "tata", "mahindra", "birla", "adani",
#     "flipkart", "swiggy", "zomato", "paytm", "ola", "uber", "myntra",
#     "snapdeal", "meesho", "razorpay", "phonepe", "gpay", "nykaa", "zepto",
#     "blinkit", "dunzo", "lenskart", "byju", "unacademy", "vedantu",
# })

# MULTI_WORD_ORGS: frozenset[str] = frozenset({
#     "american express", "jp morgan chase", "goldman sachs", "morgan stanley",
#     "bank of america", "wells fargo", "new york times", "wall street journal",
#     "los angeles times", "united nations", "world health organization",
#     "international monetary fund", "burger king", "domino's pizza",
#     "starbucks coffee", "coca cola", "pizza hut", "louis vuitton",
#     # Indian multi-word
#     "state bank of india", "reserve bank of india", "bank of baroda",
#     "punjab national bank", "union bank", "canara bank", "indian bank",
#     "hdfc bank", "icici bank", "axis bank", "kotak mahindra",
#     "tata consultancy services", "tata motors", "tata steel",
#     "infosys technologies", "wipro technologies", "hcl technologies",
#     "reliance industries", "reliance jio", "mahindra mahindra",
#     "bajaj auto", "bajaj finance", "hero motocorp", "maruti suzuki",
#     "ola cabs", "air india", "indigo airlines", "spicejet",
# })

# # All-caps tokens that are NOT organisations (noise filter)
# _ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
#     "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
#     "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
#     "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
#     "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
#     "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
#     "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
#     "PNG", "JPG", "ZIP", "OTP", "PIN", "DOB", "PAN", "GST", "UPI",
#     "EMI", "KYC", "NRI", "PF", "EPF", "TDS", "ITR", "PAN",
# })

# # ---------------------------------------------------------------------------
# # Pre-compiled regexes
# # ---------------------------------------------------------------------------

# # ── Existing patterns ────────────────────────────────────────────────────────

# # Email
# _EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# # Phone – Indian (+91) and international, requires ≥10 digits
# _PHONE_RE = re.compile(
#     r'(?<!\d)'
#     r'(?:\+\d{1,3}[\s\-.]?)?'
#     r'(?:\(?\d{3,5}\)?[\s\-.]?)'
#     r'\d{3}[\s\-.]?\d{4}'
#     r'(?!\d)',
#     re.ASCII,
# )

# # Credit card – exactly 16 digits in groups of 4
# _CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')

# # Aadhaar – exactly 12 digits in groups of 4
# _AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# # Generic numeric ID – 9 to 15 digits (skips 12-digit Aadhaar and 16-digit card)
# _ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# # Address suffix list
# _ADDRESS_SUFFIX = (
#     r'(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|'
#     r'court|ct|plaza|way|apt|bldg|suite|ste|'
#     r'nagar|colony|sector|vihar|enclave|marg|chowk|bazaar|'
#     r'cross|main|layout|extension|phase|block)'
# )
# _ADDRESS_RE = re.compile(
#     r'\b\d{1,5}[ \t]+[A-Za-z]{2,}(?:[ \t]+[A-Za-z]{2,}){0,4}'
#     r'(?:[ \t]+' + _ADDRESS_SUFFIX + r')?\b',
#     re.IGNORECASE,
# )

# # ── New India-specific patterns ──────────────────────────────────────────────

# # PAN card: 5 uppercase letters + 4 digits + 1 uppercase letter
# # e.g. ABCDE1234F
# _PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# # Indian Passport: letter (A/B/C/F/G/H/J/K/L/M/N/P/R/S/T/Z) + 7 digits
# # e.g. P1234567 or N1234567
# _PASSPORT_RE = re.compile(r'\b[A-PR-WYa-pr-wy][0-9]{7}\b')

# # Indian Driving Licence: state code (2 letters) + RTO code (2 digits) +
# # year (4 digits) + sequence (7 digits), with optional hyphens/spaces
# # e.g. MH12 20110012345 or DL-04-2011-0012345
# _DRIVING_LICENCE_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{7}\b',
#     re.IGNORECASE,
# )

# # Indian Pincode: 6 digits starting with 1–9
# # e.g. 400053, 110001
# _PINCODE_RE = re.compile(r'\b[1-9]\d{5}\b')

# # Indian Vehicle Registration:
# # state code (2 letters) + district (2 digits) + series (1-3 letters) + number (4 digits)
# # e.g. MH12AB1234 or MH 12 AB 1234
# _VEHICLE_REG_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b',
#     re.IGNORECASE,
# )

# # GST Number: 2 digits + PAN (10 chars) + 1 digit + Z + 1 alphanumeric
# # e.g. 22AAAAA0000A1Z5
# _GST_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')

# # IFSC Code: 4 letters (bank code) + 0 + 6 alphanumeric (branch)
# # e.g. SBIN0001234 or HDFC0000001
# _IFSC_RE = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# # UPI ID: anything@upi-handle
# # e.g. rahul@upi, name@paytm, 9876543210@ybl
# _UPI_RE = re.compile(
#     r'\b[\w.\-+]+@(?:upi|paytm|gpay|phonepe|ybl|okaxis|okicici|okhdfcbank|'
#     r'oksbi|apl|ibl|axl|aubank|barodampay|cnrb|csbpay|dbs|dlb|'
#     r'equitas|fbl|federal|finobank|hdfcbank|icici|idbi|idfc|'
#     r'indus|iob|jkb|jsb|karb|kbl|kotak|kvb|lvb|mahb|'
#     r'niyobank|postbank|rbl|sbi|scb|tjsb|ubi|ucb|unionbank|'
#     r'utib|vijb|yapl)\b',
#     re.IGNORECASE,
# )

# # ── New general patterns ──────────────────────────────────────────────────────

# # Date of Birth: common formats
# # DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
# # MM/DD/YYYY, YYYY-MM-DD
# # "born on 15 August 1990", "born 15/08/1990"
# _DOB_RE = re.compile(
#     r'(?:'
#     # Numeric formats: DD/MM/YYYY or YYYY-MM-DD etc.
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\/\-\.\ ](?:0?[1-9]|1[0-2])[\/\-\.\ ](?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:19|20)\d{2}[\/\-\.](?:0?[1-9]|1[0-2])[\/\-\.](?:0?[1-9]|[12]\d|3[01])\b'
#     r'|'
#     # Written format: "15 August 1990" or "August 15, 1990"
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\s]+(?:january|february|march|april|may|june|'
#     r'july|august|september|october|november|december)[\s,]+(?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:january|february|march|april|may|june|july|august|september|'
#     r'october|november|december)[\s]+(?:0?[1-9]|[12]\d|3[01])[\s,]+(?:19|20)\d{2}\b'
#     r')',
#     re.IGNORECASE,
# )

# # IP address: IPv4 only (IPv6 is rarely PII in this context)
# # e.g. 192.168.1.1
# _IP_RE = re.compile(
#     r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
# )

# # URLs with personal paths (not just domains)
# # Matches http/https URLs that have a path beyond just the root
# _URL_RE = re.compile(
#     r'\bhttps?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]{10,}\b',
#     re.IGNORECASE,
# )

# # Salary / financial figures:
# # ₹85,000 or Rs 85000 or INR 85000 or $5000 or 85,000 rupees
# _SALARY_RE = re.compile(
#     r'(?:'
#     r'(?:₹|rs\.?|inr|usd|\$|£|€)[\s]?\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?'
#     r'|'
#     r'\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?[\s]?(?:rupees?|lakh|lakhs|crore|crores|k|thousand)'
#     r')',
#     re.IGNORECASE,
# )

# # Common names regex (built at module load)
# _COMMON_NAMES_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(n) for n in sorted(COMMON_NAMES, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # Indian cities regex
# _INDIAN_CITIES_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(c) for c in sorted(INDIAN_CITIES, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # Single-word orgs
# _SINGLE_WORD_ORGS_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(o) for o in sorted(SINGLE_WORD_ORGS, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # Multi-word orgs
# _MULTI_WORD_ORGS_RE = re.compile(
#     r'\b(?:' + '|'.join(re.escape(p) for p in sorted(MULTI_WORD_ORGS, key=len, reverse=True)) + r')\b',
#     re.IGNORECASE,
# )

# # All-caps orgs: 3–10 letters
# _ALLCAPS_ORG_RE = re.compile(r'\b[A-Z]{3,10}\b')


# # ---------------------------------------------------------------------------
# # Input sanitisation
# # ---------------------------------------------------------------------------

# def _sanitise(text: str) -> str:
#     """Remove null bytes, control chars, lone surrogates; NFC-normalise."""
#     text = text.replace("\x00", " ")
#     text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
#     text = re.sub(r'[\ud800-\udfff]', '\ufffd', text)
#     try:
#         text = unicodedata.normalize("NFC", text)
#     except Exception:  # noqa: BLE001
#         pass
#     return text


# # ---------------------------------------------------------------------------
# # Presidio client (optional)
# # ---------------------------------------------------------------------------

# _PRESIDIO_LABEL_MAP: Dict[str, Optional[str]] = {
#     "PERSON":         "PERSON",
#     "EMAIL_ADDRESS":  "EMAIL",
#     "PHONE_NUMBER":   "PHONE",
#     "CREDIT_CARD":    "CARD",
#     "ORGANIZATION":   "ORG",
#     "ADDRESS":        "ADDRESS",
#     "ID":             "ID",
#     "LOCATION":       "LOCATION",
#     "DATE_TIME":      None,
# }


# def _detect_with_presidio(text: str) -> List[Dict[str, Any]]:
#     url = getattr(Config, "PRESIDIO_ANALYZER_URL", None)
#     if not url:
#         return []
#     try:
#         response = requests.post(
#             url,
#             json={"text": text, "language": "en"},
#             timeout=2.0,
#         )
#         if response.status_code != 200:
#             logger.warning("Presidio returned HTTP %d: %s", response.status_code, response.text[:200])
#             return []
#         converted: List[Dict[str, Any]] = []
#         for e in response.json():
#             mapped = _PRESIDIO_LABEL_MAP.get(e.get("entity_type", ""))
#             if mapped:
#                 converted.append({
#                     "label": mapped,
#                     "text":  e.get("text", ""),
#                     "start": int(e["start"]),
#                     "end":   int(e["end"]),
#                 })
#         return converted
#     except requests.exceptions.Timeout:
#         logger.warning("Presidio request timed out.")
#     except Exception:  # noqa: BLE001
#         logger.warning("Presidio detection failed.", exc_info=True)
#     return []


# # ---------------------------------------------------------------------------
# # Generic span helper
# # ---------------------------------------------------------------------------

# def _spans(label: str, pattern: re.Pattern, text: str) -> List[Dict[str, Any]]:
#     return [
#         {"label": label, "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in pattern.finditer(text)
#     ]


# # ---------------------------------------------------------------------------
# # Individual detectors
# # ---------------------------------------------------------------------------

# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     return _spans("EMAIL", _EMAIL_RE, text)


# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     return _spans("PHONE", _PHONE_RE, text)


# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     return _spans("CARD", _CARD_RE, text)


# def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _AADHAAR_RE.finditer(text):
#         digits = re.sub(r'\D', '', m.group())
#         if len(digits) == 12:
#             result.append({"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()})
#     return result


# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _ID_RE.finditer(text):
#         raw = re.sub(r'\D', '', m.group())
#         if len(raw) in (12, 16):
#             continue  # handled by AADHAAR / CARD detectors
#         result.append({"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()})
#     return result


# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     suffix_pat = re.compile(_ADDRESS_SUFFIX, re.IGNORECASE)
#     result = []
#     for m in _ADDRESS_RE.finditer(text):
#         span = m.group()
#         if not (10 < len(span) < 100):
#             continue
#         if not re.search(r'\b\d+\b', span):
#             continue
#         if not suffix_pat.search(span):
#             continue
#         result.append({"label": "ADDRESS", "text": span, "start": m.start(), "end": m.end()})
#     return result


# # ── New India-specific detectors ─────────────────────────────────────────────

# def _detect_pan(text: str) -> List[Dict[str, Any]]:
#     """PAN card: ABCDE1234F"""
#     return _spans("PAN", _PAN_RE, text)


# def _detect_passport(text: str) -> List[Dict[str, Any]]:
#     """Indian passport: letter + 7 digits"""
#     return _spans("PASSPORT", _PASSPORT_RE, text)


# def _detect_driving_licence(text: str) -> List[Dict[str, Any]]:
#     """Indian DL: MH12 2011 0012345"""
#     return _spans("DRIVING_LICENCE", _DRIVING_LICENCE_RE, text)


# def _detect_pincode(text: str) -> List[Dict[str, Any]]:
#     """Indian 6-digit pincode — only if standalone (not part of phone/ID)"""
#     result = []
#     for m in _PINCODE_RE.finditer(text):
#         # Skip if it is part of a longer digit sequence (already caught as ID/PHONE)
#         start, end = m.start(), m.end()
#         before = text[start - 1] if start > 0 else ' '
#         after  = text[end]       if end < len(text) else ' '
#         if before.isdigit() or after.isdigit():
#             continue
#         result.append({"label": "PINCODE", "text": m.group(), "start": start, "end": end})
#     return result


# def _detect_vehicle_reg(text: str) -> List[Dict[str, Any]]:
#     """Indian vehicle registration: MH12AB1234"""
#     return _spans("VEHICLE_REG", _VEHICLE_REG_RE, text)


# def _detect_gst(text: str) -> List[Dict[str, Any]]:
#     """GST number: 22AAAAA0000A1Z5"""
#     return _spans("GST", _GST_RE, text)


# def _detect_ifsc(text: str) -> List[Dict[str, Any]]:
#     """IFSC code: SBIN0001234"""
#     return _spans("IFSC", _IFSC_RE, text)


# def _detect_upi(text: str) -> List[Dict[str, Any]]:
#     """UPI ID: name@paytm"""
#     return _spans("UPI", _UPI_RE, text)


# # ── New general detectors ────────────────────────────────────────────────────

# def _detect_dob(text: str) -> List[Dict[str, Any]]:
#     """Date of birth in numeric or written formats"""
#     return _spans("DOB", _DOB_RE, text)


# def _detect_ip(text: str) -> List[Dict[str, Any]]:
#     """IPv4 addresses"""
#     return _spans("IP", _IP_RE, text)


# def _detect_urls(text: str) -> List[Dict[str, Any]]:
#     """HTTP/HTTPS URLs — only those with non-trivial paths"""
#     result = []
#     for m in _URL_RE.finditer(text):
#         # Skip very generic homepage URLs like https://google.com
#         url = m.group()
#         if url.count('/') <= 2 and '?' not in url and '#' not in url:
#             continue
#         result.append({"label": "URL", "text": url, "start": m.start(), "end": m.end()})
#     return result


# def _detect_salary(text: str) -> List[Dict[str, Any]]:
#     """Salary / financial figures with currency context"""
#     return _spans("SALARY", _SALARY_RE, text)


# def _detect_common_names(text: str) -> List[Dict[str, Any]]:
#     return _spans("PERSON", _COMMON_NAMES_RE, text)


# def _detect_indian_cities(text: str) -> List[Dict[str, Any]]:
#     return _spans("LOCATION", _INDIAN_CITIES_RE, text)


# def _detect_single_word_orgs(text: str) -> List[Dict[str, Any]]:
#     return _spans("ORG", _SINGLE_WORD_ORGS_RE, text)


# def _detect_multi_word_orgs(text: str) -> List[Dict[str, Any]]:
#     return _spans("ORG", _MULTI_WORD_ORGS_RE, text)


# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _ALLCAPS_ORG_RE.finditer(text):
#         token = m.group()
#         if token not in _ALLCAPS_ORG_STOPWORDS:
#             result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
#     return result


# # ---------------------------------------------------------------------------
# # Public spaCy wrapper
# # ---------------------------------------------------------------------------

# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     if not text or _nlp is None:
#         return []
#     detected: List[Dict[str, Any]] = []
#     try:
#         doc = _nlp(text)
#         for ent in doc.ents:
#             if ent.label_ in {"PERSON", "ORG", "GPE"}:
#                 label = "LOCATION" if ent.label_ == "GPE" else ent.label_
#                 detected.append({
#                     "label": label,
#                     "text":  ent.text,
#                     "start": ent.start_char,
#                     "end":   ent.end_char,
#                 })
#     except Exception:  # noqa: BLE001
#         logger.exception("spaCy processing failed.")
#     return detected


# # ---------------------------------------------------------------------------
# # Public regex wrapper
# # ---------------------------------------------------------------------------

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities: List[Dict[str, Any]] = []
#     try:
#         # High-confidence structured patterns first
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_aadhaar(text))
#         entities.extend(_detect_pan(text))
#         entities.extend(_detect_passport(text))
#         entities.extend(_detect_driving_licence(text))
#         entities.extend(_detect_gst(text))
#         entities.extend(_detect_ifsc(text))
#         entities.extend(_detect_upi(text))
#         entities.extend(_detect_vehicle_reg(text))
#         entities.extend(_detect_pincode(text))
#         entities.extend(_detect_ids(text))
#         # Context-dependent patterns
#         entities.extend(_detect_dob(text))
#         entities.extend(_detect_ip(text))
#         entities.extend(_detect_urls(text))
#         entities.extend(_detect_salary(text))
#         entities.extend(_detect_addresses(text))
#         # Name / location / org patterns (lower precision, lower priority)
#         entities.extend(_detect_common_names(text))
#         entities.extend(_detect_indian_cities(text))
#         entities.extend(_detect_single_word_orgs(text))
#         entities.extend(_detect_multi_word_orgs(text))
#         entities.extend(_detect_allcaps_orgs(text))
#     except Exception:  # noqa: BLE001
#         logger.exception("Regex detection failed.")
#     return entities


# # ---------------------------------------------------------------------------
# # Post-processing helpers
# # ---------------------------------------------------------------------------

# def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Remove exact (start, end, label) duplicates."""
#     seen: set[tuple] = set()
#     unique: List[Dict[str, Any]] = []
#     for span in spans:
#         key = (span["start"], span["end"], span["label"])
#         if key not in seen:
#             seen.add(key)
#             unique.append(span)
#     return unique


# def _validate_entities(entities: List[Dict[str, Any]]) -> None:
#     required = {"label", "start", "end"}
#     for idx, ent in enumerate(entities):
#         missing = required - ent.keys()
#         if missing:
#             raise ValueError(f"Entity[{idx}] missing keys {missing}: {ent!r}")
#         if not isinstance(ent["start"], int) or not isinstance(ent["end"], int):
#             raise ValueError(f"Entity[{idx}] start/end must be int: {ent!r}")
#         if ent["start"] < 0 or ent["end"] <= ent["start"]:
#             raise ValueError(f"Entity[{idx}] invalid span [{ent['start']}, {ent['end']}): {ent!r}")


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     if not entities:
#         return []
#     _validate_entities(entities)
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (
#             e["start"],
#             -PRIORITY_MAP.get(e["label"], 0),
#             -(e["end"] - e["start"]),
#         ),
#     )
#     resolved: List[Dict[str, Any]] = []
#     current = sorted_ents[0]
#     for nxt in sorted_ents[1:]:
#         if nxt["start"] < current["end"]:
#             cur_prio = PRIORITY_MAP.get(current["label"], 0)
#             nxt_prio = PRIORITY_MAP.get(nxt["label"], 0)
#             cur_len  = current["end"] - current["start"]
#             nxt_len  = nxt["end"]     - nxt["start"]
#             if nxt_prio > cur_prio or (nxt_prio == cur_prio and nxt_len > cur_len):
#                 current = nxt
#         else:
#             resolved.append(current)
#             current = nxt
#     resolved.append(current)
#     logger.debug("resolve_overlaps: %d → %d entities", len(entities), len(resolved))
#     return resolved


# # ---------------------------------------------------------------------------
# # Main public entry point
# # ---------------------------------------------------------------------------

# def detect_entities(raw_text: Any) -> List[Dict[str, Any]]:
#     """
#     Detect PII / named entities in *raw_text*.
#     Accepts any input; non-string values are coerced to str.
#     """
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         try:
#             raw_text = str(raw_text)
#         except Exception:  # noqa: BLE001
#             logger.warning("Could not coerce input to str; returning empty.")
#             return []

#     raw_text = raw_text.strip()
#     if not raw_text:
#         return []

#     max_len: int = getattr(Config, "MAX_TEXT_LENGTH", 100_000)
#     if len(raw_text) > max_len:
#         logger.warning("Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.", len(raw_text), max_len)
#         raw_text = raw_text[:max_len]

#     raw_text = _sanitise(raw_text)
#     if not raw_text.strip():
#         return []

#     presidio_spans = _detect_with_presidio(raw_text)
#     spacy_spans    = detect_spacy_entities(raw_text)
#     regex_spans    = detect_regex_entities(raw_text)

#     all_spans = presidio_spans + spacy_spans + regex_spans
#     if not all_spans:
#         return []

#     all_spans = deduplicate_spans(all_spans)

#     try:
#         return resolve_overlaps(all_spans)
#     except ValueError:
#         logger.exception("resolve_overlaps encountered invalid entities; returning deduplicated spans.")
#         return all_spans


# day 25 update 
"""
detector.py – PII / entity detection pipeline.

Detection sources (in merge order):
  1. Presidio (optional HTTP sidecar)
  2. spaCy NER  (PERSON, ORG, GPE)
  3. Regex rules:
       Core  : EMAIL, PHONE, CARD, AADHAAR, ID, ADDRESS
       India : PAN, PASSPORT, DRIVING_LICENCE, PINCODE, VEHICLE_REG,
               GST, IFSC, UPI
       General: DOB, IP, URL, SALARY, PERSON, ORG

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
    "EMAIL":            7,
    "PHONE":            6,
    "CARD":             5,
    "AADHAAR":          5,
    "PAN":              5,
    "PASSPORT":         5,
    "DRIVING_LICENCE":  5,
    "GST":              5,
    "IFSC":             5,
    "UPI":              5,
    "VEHICLE_REG":      4,
    "IP":               4,
    "URL":              4,
    "ADDRESS":          3,
    "PINCODE":          3,
    "DOB":              3,
    "SALARY":           3,
    "ID":               2,
    "ORG":              1,
    "PERSON":           1,
    "LOCATION":         1,
}

# ---------------------------------------------------------------------------
# Common names (de-duplicated)
# ---------------------------------------------------------------------------
COMMON_NAMES: frozenset[str] = frozenset({
    # Indian first names
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
    "sneha", "sejal", "rohan", "arun", "sudhir", "ramesh", "dinesh", "girish",
    "harish", "naresh", "prakash", "rajesh", "suresh", "umesh", "vinod",
    "ashok", "devesh", "ganesh", "jagdish", "kamlesh", "lokesh", "mukesh",
    "nilesh", "omkar", "pramod", "ritesh", "santosh", "tapan", "vaibhav",
    # Indian surnames
    "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
    "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
    "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
    "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
    "chavan", "nikam", "kadam", "bhosle", "kohli", "malhotra", "kapoor",
    "khanna", "chopra", "bose", "mukherjee", "chatterjee", "banerjee",
    "chakraborty", "iyer", "nair", "menon", "pillai", "krishnan", "narayanan",
    "venkatesh", "subramaniam", "rajan", "krishnamurthy", "swaminathan",
    # Western first names
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
# Indian cities / locations
# ---------------------------------------------------------------------------
INDIAN_CITIES: frozenset[str] = frozenset({
    "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "ahmedabad",
    "chennai", "kolkata", "surat", "pune", "jaipur", "lucknow", "kanpur",
    "nagpur", "indore", "thane", "bhopal", "visakhapatnam", "patna",
    "vadodara", "ghaziabad", "ludhiana", "agra", "nashik", "ranchi",
    "faridabad", "meerut", "rajkot", "varanasi", "srinagar", "aurangabad",
    "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj",
    "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada", "jodhpur",
    "madurai", "raipur", "kota", "chandigarh", "guwahati", "thiruvananthapuram",
    "solapur", "hubli", "dharwad", "tiruchirappalli", "mysore", "mysuru",
    "bareilly", "aligarh", "moradabad", "jalandhar", "bhubaneswar", "salem",
    "warangal", "mira bhayandar", "jamshedpur", "noida", "gurugram",
    "gurgaon", "noidaextension", "greater noida", "kochi", "ernakulam",
    "dehradun", "shimla", "jammu", "leh", "panaji", "goa", "kolhapur",
    "akola", "latur", "nanded", "sangli", "jalgaon", "amravati",
    # States
    "maharashtra", "karnataka", "gujarat", "rajasthan", "uttar pradesh",
    "madhya pradesh", "tamil nadu", "andhra pradesh", "telangana",
    "west bengal", "kerala", "punjab", "haryana", "bihar", "jharkhand",
    "odisha", "assam", "chhattisgarh", "uttarakhand", "himachal pradesh",
    "goa", "manipur", "meghalaya", "mizoram", "nagaland", "sikkim",
    "arunachal pradesh", "tripura",
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
    # Indian companies / banks
    "infosys", "wipro", "tcs", "hcl", "reliance", "hdfc", "icici", "sbi",
    "axis", "kotak", "bajaj", "tata", "mahindra", "birla", "adani",
    "flipkart", "swiggy", "zomato", "paytm", "ola", "uber", "myntra",
    "snapdeal", "meesho", "razorpay", "phonepe", "gpay", "nykaa", "zepto",
    "blinkit", "dunzo", "lenskart", "byju", "unacademy", "vedantu",
})

MULTI_WORD_ORGS: frozenset[str] = frozenset({
    "american express", "jp morgan chase", "goldman sachs", "morgan stanley",
    "bank of america", "wells fargo", "new york times", "wall street journal",
    "los angeles times", "united nations", "world health organization",
    "international monetary fund", "burger king", "domino's pizza",
    "starbucks coffee", "coca cola", "pizza hut", "louis vuitton",
    # Indian multi-word
    "state bank of india", "reserve bank of india", "bank of baroda",
    "punjab national bank", "union bank", "canara bank", "indian bank",
    "hdfc bank", "icici bank", "axis bank", "kotak mahindra",
    "tata consultancy services", "tata motors", "tata steel",
    "infosys technologies", "wipro technologies", "hcl technologies",
    "reliance industries", "reliance jio", "mahindra mahindra",
    "bajaj auto", "bajaj finance", "hero motocorp", "maruti suzuki",
    "ola cabs", "air india", "indigo airlines", "spicejet",
})

# All-caps tokens that are NOT organisations (noise filter)
_ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
    "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
    "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
    "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
    "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
    "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
    "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
    "PNG", "JPG", "ZIP", "OTP", "PIN", "DOB", "PAN", "GST", "UPI",
    "EMI", "KYC", "NRI", "PF", "EPF", "TDS", "ITR", "PAN",
})

# ---------------------------------------------------------------------------
# Pre-compiled regexes
# ---------------------------------------------------------------------------

# ── Existing patterns ────────────────────────────────────────────────────────

# Email
_EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# Phone – Indian (+91) and international, requires ≥10 digits
_PHONE_RE = re.compile(
    r'(?<!\d)'
    r'(?:\+\d{1,3}[\s\-.]?)?'
    r'(?:\(?\d{3,5}\)?[\s\-.]?)'
    r'\d{3}[\s\-.]?\d{4}'
    r'(?!\d)',
    re.ASCII,
)

# Credit card – exactly 16 digits in groups of 4
_CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')

# Aadhaar – exactly 12 digits in groups of 4
_AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# Generic numeric ID – 9 to 15 digits (skips 12-digit Aadhaar and 16-digit card)
_ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# Address suffix list
_ADDRESS_SUFFIX = (
    r'(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|'
    r'court|ct|plaza|way|apt|bldg|suite|ste|'
    r'nagar|colony|sector|vihar|enclave|marg|chowk|bazaar|'
    r'cross|main|layout|extension|phase|block)'
)
_ADDRESS_RE = re.compile(
    r'\b\d{1,5}[ \t]+[A-Za-z]{2,}(?:[ \t]+[A-Za-z]{2,}){0,4}'
    r'(?:[ \t]+' + _ADDRESS_SUFFIX + r')?\b',
    re.IGNORECASE,
)

# ── New India-specific patterns ──────────────────────────────────────────────

# PAN card: 5 uppercase letters + 4 digits + 1 uppercase letter
# e.g. ABCDE1234F
_PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# Indian Passport: letter (A/B/C/F/G/H/J/K/L/M/N/P/R/S/T/Z) + 7 digits
# e.g. P1234567 or N1234567
_PASSPORT_RE = re.compile(r'\b[A-PR-WYa-pr-wy][0-9]{7}\b')

# Indian Driving Licence: state code (2 letters) + RTO code (2 digits) +
# year (4 digits) + sequence (7 digits), with optional hyphens/spaces
# e.g. MH12 20110012345 or DL-04-2011-0012345
_DRIVING_LICENCE_RE = re.compile(
    r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{7}\b',
    re.IGNORECASE,
)

# Indian Pincode: 6 digits starting with 1–9
# e.g. 400053, 110001
_PINCODE_RE = re.compile(r'\b[1-9]\d{5}\b')

# Indian Vehicle Registration:
# state code (2 letters) + district (2 digits) + series (1-3 letters) + number (4 digits)
# e.g. MH12AB1234 or MH 12 AB 1234
_VEHICLE_REG_RE = re.compile(
    r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b',
    re.IGNORECASE,
)

# GST Number: 2 digits + PAN (10 chars) + 1 digit + Z + 1 alphanumeric
# e.g. 22AAAAA0000A1Z5
_GST_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')

# IFSC Code: 4 letters (bank code) + 0 + 6 alphanumeric (branch)
# e.g. SBIN0001234 or HDFC0000001
_IFSC_RE = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# UPI ID: anything@upi-handle
# e.g. rahul@upi, name@paytm, 9876543210@ybl
_UPI_RE = re.compile(
    r'\b[\w.\-+]+@(?:upi|paytm|gpay|phonepe|ybl|okaxis|okicici|okhdfcbank|'
    r'oksbi|apl|ibl|axl|aubank|barodampay|cnrb|csbpay|dbs|dlb|'
    r'equitas|fbl|federal|finobank|hdfcbank|icici|idbi|idfc|'
    r'indus|iob|jkb|jsb|karb|kbl|kotak|kvb|lvb|mahb|'
    r'niyobank|postbank|rbl|sbi|scb|tjsb|ubi|ucb|unionbank|'
    r'utib|vijb|yapl)\b',
    re.IGNORECASE,
)

# ── New general patterns ──────────────────────────────────────────────────────

# Date of Birth: common formats
# DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
# MM/DD/YYYY, YYYY-MM-DD
# "born on 15 August 1990", "born 15/08/1990"
_DOB_RE = re.compile(
    r'(?:'
    # Numeric formats: DD/MM/YYYY or YYYY-MM-DD etc.
    r'\b(?:0?[1-9]|[12]\d|3[01])[\/\-\.\ ](?:0?[1-9]|1[0-2])[\/\-\.\ ](?:19|20)\d{2}\b'
    r'|'
    r'\b(?:19|20)\d{2}[\/\-\.](?:0?[1-9]|1[0-2])[\/\-\.](?:0?[1-9]|[12]\d|3[01])\b'
    r'|'
    # Written format: "15 August 1990" or "August 15, 1990"
    r'\b(?:0?[1-9]|[12]\d|3[01])[\s]+(?:january|february|march|april|may|june|'
    r'july|august|september|october|november|december)[\s,]+(?:19|20)\d{2}\b'
    r'|'
    r'\b(?:january|february|march|april|may|june|july|august|september|'
    r'october|november|december)[\s]+(?:0?[1-9]|[12]\d|3[01])[\s,]+(?:19|20)\d{2}\b'
    r')',
    re.IGNORECASE,
)

# IP address: IPv4 only (IPv6 is rarely PII in this context)
# e.g. 192.168.1.1
_IP_RE = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
)

# URLs with personal paths (not just domains)
# Matches http/https URLs that have a path beyond just the root
_URL_RE = re.compile(
    r'\bhttps?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]{10,}\b',
    re.IGNORECASE,
)

# Salary / financial figures:
# ₹85,000 or Rs 85000 or INR 85000 or $5000 or 85,000 rupees
_SALARY_RE = re.compile(
    r'(?:'
    r'(?:₹|rs\.?|inr|usd|\$|£|€)[\s]?\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?'
    r'|'
    r'\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?[\s]?(?:rupees?|lakh|lakhs|crore|crores|k|thousand)'
    r')',
    re.IGNORECASE,
)

# Common names regex (built at module load)
_COMMON_NAMES_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(n) for n in sorted(COMMON_NAMES, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# Indian cities regex
_INDIAN_CITIES_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(c) for c in sorted(INDIAN_CITIES, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# Single-word orgs
_SINGLE_WORD_ORGS_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(o) for o in sorted(SINGLE_WORD_ORGS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# Multi-word orgs
_MULTI_WORD_ORGS_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(p) for p in sorted(MULTI_WORD_ORGS, key=len, reverse=True)) + r')\b',
    re.IGNORECASE,
)

# All-caps orgs: 3–10 letters
_ALLCAPS_ORG_RE = re.compile(r'\b[A-Z]{3,10}\b')


# ---------------------------------------------------------------------------
# Input sanitisation
# ---------------------------------------------------------------------------

def _sanitise(text: str) -> str:
    """Remove null bytes, control chars, lone surrogates; NFC-normalise."""
    text = text.replace("\x00", " ")
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
    text = re.sub(r'[\ud800-\udfff]', '\ufffd', text)
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
    "LOCATION":       "LOCATION",
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
            logger.warning("Presidio returned HTTP %d: %s", response.status_code, response.text[:200])
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
# Generic span helper
# ---------------------------------------------------------------------------

def _spans(label: str, pattern: re.Pattern, text: str) -> List[Dict[str, Any]]:
    return [
        {"label": label, "text": m.group(), "start": m.start(), "end": m.end()}
        for m in pattern.finditer(text)
    ]


# ---------------------------------------------------------------------------
# Individual detectors
# ---------------------------------------------------------------------------

def _detect_emails(text: str) -> List[Dict[str, Any]]:
    return _spans("EMAIL", _EMAIL_RE, text)


def _detect_phones(text: str) -> List[Dict[str, Any]]:
    return _spans("PHONE", _PHONE_RE, text)


def _detect_cards(text: str) -> List[Dict[str, Any]]:
    return _spans("CARD", _CARD_RE, text)


def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _AADHAAR_RE.finditer(text):
        digits = re.sub(r'\D', '', m.group())
        if len(digits) == 12:
            result.append({"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()})
    return result


def _detect_ids(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _ID_RE.finditer(text):
        raw = re.sub(r'\D', '', m.group())
        if len(raw) in (12, 16):
            continue  # handled by AADHAAR / CARD detectors
        result.append({"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()})
    return result


def _detect_addresses(text: str) -> List[Dict[str, Any]]:
    min_len = getattr(Config.Detectors, "MIN_ADDRESS_LENGTH", 10)
    max_len = getattr(Config.Detectors, "MAX_ADDRESS_LENGTH", 100)
    suffix_pat = re.compile(_ADDRESS_SUFFIX, re.IGNORECASE)
    result = []
    for m in _ADDRESS_RE.finditer(text):
        span = m.group()
        if not (min_len < len(span) < max_len):
            continue
        if not re.search(r'\b\d+\b', span):
            continue
        if not suffix_pat.search(span):
            continue
        result.append({"label": "ADDRESS", "text": span, "start": m.start(), "end": m.end()})
    return result


# ── New India-specific detectors ─────────────────────────────────────────────

def _detect_pan(text: str) -> List[Dict[str, Any]]:
    """PAN card: ABCDE1234F"""
    return _spans("PAN", _PAN_RE, text)


def _detect_passport(text: str) -> List[Dict[str, Any]]:
    """Indian passport: letter + 7 digits"""
    return _spans("PASSPORT", _PASSPORT_RE, text)


def _detect_driving_licence(text: str) -> List[Dict[str, Any]]:
    """Indian DL: MH12 2011 0012345"""
    return _spans("DRIVING_LICENCE", _DRIVING_LICENCE_RE, text)


def _detect_pincode(text: str) -> List[Dict[str, Any]]:
    """Indian 6-digit pincode — only if standalone (not part of phone/ID)"""
    result = []
    for m in _PINCODE_RE.finditer(text):
        # Skip if it is part of a longer digit sequence (already caught as ID/PHONE)
        start, end = m.start(), m.end()
        before = text[start - 1] if start > 0 else ' '
        after  = text[end]       if end < len(text) else ' '
        if before.isdigit() or after.isdigit():
            continue
        result.append({"label": "PINCODE", "text": m.group(), "start": start, "end": end})
    return result


def _detect_vehicle_reg(text: str) -> List[Dict[str, Any]]:
    """Indian vehicle registration: MH12AB1234"""
    return _spans("VEHICLE_REG", _VEHICLE_REG_RE, text)


def _detect_gst(text: str) -> List[Dict[str, Any]]:
    """GST number: 22AAAAA0000A1Z5"""
    return _spans("GST", _GST_RE, text)


def _detect_ifsc(text: str) -> List[Dict[str, Any]]:
    """IFSC code: SBIN0001234"""
    return _spans("IFSC", _IFSC_RE, text)


def _detect_upi(text: str) -> List[Dict[str, Any]]:
    """UPI ID: name@paytm"""
    return _spans("UPI", _UPI_RE, text)


# ── New general detectors ────────────────────────────────────────────────────

def _detect_dob(text: str) -> List[Dict[str, Any]]:
    """Date of birth in numeric or written formats"""
    return _spans("DOB", _DOB_RE, text)


def _detect_ip(text: str) -> List[Dict[str, Any]]:
    """IPv4 addresses"""
    return _spans("IP", _IP_RE, text)


def _detect_urls(text: str) -> List[Dict[str, Any]]:
    """HTTP/HTTPS URLs — only those with non-trivial paths"""
    result = []
    for m in _URL_RE.finditer(text):
        # Skip very generic homepage URLs like https://google.com
        url = m.group()
        if url.count('/') <= 2 and '?' not in url and '#' not in url:
            continue
        result.append({"label": "URL", "text": url, "start": m.start(), "end": m.end()})
    return result


def _detect_salary(text: str) -> List[Dict[str, Any]]:
    """Salary / financial figures with currency context"""
    return _spans("SALARY", _SALARY_RE, text)


def _detect_common_names(text: str) -> List[Dict[str, Any]]:
    return _spans("PERSON", _COMMON_NAMES_RE, text)


def _detect_indian_cities(text: str) -> List[Dict[str, Any]]:
    return _spans("LOCATION", _INDIAN_CITIES_RE, text)


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
            if ent.label_ in {"PERSON", "ORG", "GPE"}:
                label = "LOCATION" if ent.label_ == "GPE" else ent.label_
                detected.append({
                    "label": label,
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
    d = Config.Detectors          # short alias for readability
    entities: List[Dict[str, Any]] = []
    try:
        # ── Core structured patterns (highest confidence) ──────────────────
        if d.ENABLE_EMAIL:            entities.extend(_detect_emails(text))
        if d.ENABLE_PHONE:            entities.extend(_detect_phones(text))
        if d.ENABLE_CARD:             entities.extend(_detect_cards(text))
        if d.ENABLE_AADHAAR:          entities.extend(_detect_aadhaar(text))
        # ── India-specific structured patterns ─────────────────────────────
        if d.ENABLE_PAN:              entities.extend(_detect_pan(text))
        if d.ENABLE_PASSPORT:         entities.extend(_detect_passport(text))
        if d.ENABLE_DRIVING_LICENCE:  entities.extend(_detect_driving_licence(text))
        if d.ENABLE_GST:              entities.extend(_detect_gst(text))
        if d.ENABLE_IFSC:             entities.extend(_detect_ifsc(text))
        if d.ENABLE_UPI:              entities.extend(_detect_upi(text))
        if d.ENABLE_VEHICLE_REG:      entities.extend(_detect_vehicle_reg(text))
        if d.ENABLE_PINCODE:          entities.extend(_detect_pincode(text))
        if d.ENABLE_ID:               entities.extend(_detect_ids(text))
        # ── Context-dependent patterns ─────────────────────────────────────
        if d.ENABLE_DOB:              entities.extend(_detect_dob(text))
        if d.ENABLE_IP:               entities.extend(_detect_ip(text))
        if d.ENABLE_URL:              entities.extend(_detect_urls(text))
        if d.ENABLE_SALARY:           entities.extend(_detect_salary(text))
        if d.ENABLE_ADDRESS:          entities.extend(_detect_addresses(text))
        # ── Name / location / org patterns (lower precision) ───────────────
        if d.ENABLE_COMMON_NAMES:     entities.extend(_detect_common_names(text))
        if d.ENABLE_INDIAN_CITIES:    entities.extend(_detect_indian_cities(text))
        if d.ENABLE_SINGLE_ORGS:      entities.extend(_detect_single_word_orgs(text))
        if d.ENABLE_MULTI_ORGS:       entities.extend(_detect_multi_word_orgs(text))
        if d.ENABLE_ALLCAPS_ORGS:     entities.extend(_detect_allcaps_orgs(text))
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
        if nxt["start"] < current["end"]:
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
    """
    if raw_text is None:
        return []
    if not isinstance(raw_text, str):
        try:
            raw_text = str(raw_text)
        except Exception:  # noqa: BLE001
            logger.warning("Could not coerce input to str; returning empty.")
            return []

    raw_text = raw_text.strip()
    if not raw_text:
        return []

    max_len: int = getattr(Config, "MAX_TEXT_LENGTH", 100_000)
    if len(raw_text) > max_len:
        logger.warning("Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.", len(raw_text), max_len)
        raw_text = raw_text[:max_len]

    raw_text = _sanitise(raw_text)
    if not raw_text.strip():
        return []

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
        logger.exception("resolve_overlaps encountered invalid entities; returning deduplicated spans.")
        return all_spans