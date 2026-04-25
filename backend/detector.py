
# # day 26 final update 
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
#     "API_KEY":          5,   # NEW – AWS/generic API keys are high-confidence
#     "PASSWORD":         5,   # NEW – passwords are high-confidence
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

# # ---------------------------------------------------------------------------
# # FIX 1: Expanded ALLCAPS stopwords — prevent structural labels being masked
# # ---------------------------------------------------------------------------
# _ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
#     # Grammar / connectors
#     "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
#     "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
#     "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
#     "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
#     "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
#     "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
#     "PNG", "JPG", "ZIP", "OTP", "PIN", "DOB", "PAN", "GST", "UPI",
#     "EMI", "KYC", "NRI", "PF", "EPF", "TDS", "ITR",
#     # FIX: document/profile structural labels that were being wrongly masked
#     "NAME", "EMAIL", "PHONE", "MOBILE", "ADDRESS", "DOB", "AGE", "SEX",
#     "GENDER", "PROFILE", "CANDIDATE", "REFERENCE", "CONTACT", "ALTERNATE",
#     "PRIMARY", "SECONDARY", "TECHNICAL", "ENVIRONMENT", "LOCAL", "REMOTE",
#     "FULL", "FIRST", "LAST", "MIDDLE", "MASKED", "REDACTED",
#     "EDUCATION", "OCCUPATION", "INTERNSHIP", "PROJECT", "REPOSITORY",
#     "TRAVEL", "PASSPORT", "VISA", "FLIGHT", "CURRENT", "FOCUS",
#     "RESIDENTIAL", "PERMANENT", "OFFICIAL", "PERSONAL",
#     "DB", "AWS", "GCP", "S3", "EC2", "VPC", "IAM", "ARN",
#     "JWT", "SSH", "SSL", "TLS", "HTTP", "HTTPS", "TCP", "UDP",
#     "VTU", "SEAT", "USN", "REG", "DEPT", "SEM", "BATCH",
#     "BE", "ME", "BTech", "MTech", "BCA", "MCA", "BSC", "MSC",
# })

# # ---------------------------------------------------------------------------
# # FIX 2: spaCy ORG false-positive filter
# # Words that spaCy commonly mis-tags as ORG but are structural labels
# # ---------------------------------------------------------------------------
# _SPACY_ORG_FALSE_POSITIVES: frozenset[str] = frozenset({
#     "candidate", "profile", "reference", "internal", "contact",
#     "education", "technical", "environment", "local", "remote",
#     "full name", "primary", "secondary", "alternate", "residential",
#     "permanent", "official", "personal", "masked", "redacted",
#     "b.e", "m.tech", "b.tech", "bca", "mca", "internship",
#     "project", "repository", "travel", "flight", "current", "focus",
#     "university seat", "seat number",
# })

# # ---------------------------------------------------------------------------
# # Pre-compiled regexes
# # ---------------------------------------------------------------------------

# # Email
# _EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# # FIX 3: Improved phone regex — now correctly catches Indian formats
# # +91 98450 12345  |  +91-98450-12345  |  080-2345-6789  |  9845012345
# _PHONE_RE = re.compile(
#     r'(?<!\d)'
#     r'(?:'
#     # +91 with space/dash then 10 digits (possibly spaced)
#     r'\+91[\s\-]?\d{5}[\s\-]?\d{5}'
#     r'|'
#     # STD code (3-5 digits starting with 0) + number
#     r'0\d{2,4}[\s\-]?\d{6,8}'
#     r'|'
#     # Plain 10-digit Indian mobile (starts 6-9)
#     r'[6-9]\d{9}'
#     r'|'
#     # International: +country_code + number
#     r'\+\d{1,3}[\s\-.]?\(?\d{3,5}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
#     r')'
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

# # PAN card: 5 uppercase letters + 4 digits + 1 uppercase letter
# _PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# # Indian Passport: letter + 7 digits  e.g. Z1234567
# _PASSPORT_RE = re.compile(r'\b[A-PR-WYa-pr-wy][0-9]{7}\b')

# # Indian Driving Licence
# _DRIVING_LICENCE_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{7}\b',
#     re.IGNORECASE,
# )

# # Indian Pincode: 6 digits starting with 1–9
# _PINCODE_RE = re.compile(r'\b[1-9]\d{5}\b')

# # Indian Vehicle Registration
# _VEHICLE_REG_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b',
#     re.IGNORECASE,
# )

# # GST Number
# _GST_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')

# # IFSC Code
# _IFSC_RE = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# # UPI ID
# _UPI_RE = re.compile(
#     r'\b[\w.\-+]+@(?:upi|paytm|gpay|phonepe|ybl|okaxis|okicici|okhdfcbank|'
#     r'oksbi|apl|ibl|axl|aubank|barodampay|cnrb|csbpay|dbs|dlb|'
#     r'equitas|fbl|federal|finobank|hdfcbank|icici|idbi|idfc|'
#     r'indus|iob|jkb|jsb|karb|kbl|kotak|kvb|lvb|mahb|'
#     r'niyobank|postbank|rbl|sbi|scb|tjsb|ubi|ucb|unionbank|'
#     r'utib|vijb|yapl)\b',
#     re.IGNORECASE,
# )

# # Date of Birth
# _DOB_RE = re.compile(
#     r'(?:'
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\/\-\.\ ](?:0?[1-9]|1[0-2])[\/\-\.\ ](?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:19|20)\d{2}[\/\-\.](?:0?[1-9]|1[0-2])[\/\-\.](?:0?[1-9]|[12]\d|3[01])\b'
#     r'|'
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\s]+(?:january|february|march|april|may|june|'
#     r'july|august|september|october|november|december)[\s,]+(?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:january|february|march|april|may|june|july|august|september|'
#     r'october|november|december)[\s]+(?:0?[1-9]|[12]\d|3[01])[\s,]+(?:19|20)\d{2}\b'
#     r')',
#     re.IGNORECASE,
# )

# # IP address: IPv4
# _IP_RE = re.compile(
#     r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
# )

# # URLs with non-trivial paths
# _URL_RE = re.compile(
#     r'\bhttps?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]{10,}\b',
#     re.IGNORECASE,
# )

# # Salary / financial figures
# _SALARY_RE = re.compile(
#     r'(?:'
#     r'(?:₹|rs\.?|inr|usd|\$|£|€)[\s]?\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?'
#     r'|'
#     r'\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?[\s]?(?:rupees?|lakh|lakhs|crore|crores|k|thousand)'
#     r')',
#     re.IGNORECASE,
# )

# # FIX 4: AWS Access Key  e.g. AKIAIOSFODNN7EXAMPL
# _AWS_KEY_RE = re.compile(r'\bAKIA[0-9A-Z]{16}\b')

# # FIX 5: Generic API key / secret / token (context-based)
# # Matches:  api_key=abc123...  |  secret: xyz...  |  token = "..."
# _API_KEY_RE = re.compile(
#     r'(?i)(?:api[_\-]?key|secret[_\-]?key|access[_\-]?token|auth[_\-]?token'
#     r'|bearer|private[_\-]?key)\s*[:=]\s*["\']?([A-Za-z0-9\-_.+/]{8,})["\']?'
# )

# # FIX 6: Password / credential (context-based)
# # Matches:  password=abc123  |  DB_PASSWORD: xyz  |  passwd = "..."
# _PASSWORD_RE = re.compile(
#     r'(?i)(?:password|passwd|pwd|db_password|db_pass|secret_pass)\s*[:=]\s*["\']?(\S+)["\']?'
# )

# # Common names regex
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

# # FIX 7: Structural label pattern — lines that are field headers, never mask these
# # e.g. "Full Name:", "Primary Email:", "1. Education Details"
# _STRUCTURAL_LABEL_RE = re.compile(
#     r'^(?:\d+\.\s*)?'   # optional section number like "1. " or "2."
#     r'(?:full\s+)?'
#     r'(?:name|email|phone|mobile|address|contact|alternate|primary|secondary|'
#     r'occupation|education|candidate|profile|reference|technical|environment|'
#     r'travel|internship|project|repository|current|focus|residential|'
#     r'emergency|passport|visa|local|api|db|database)\b',
#     re.IGNORECASE,
# )


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
#     min_len = getattr(Config.Detectors, "MIN_ADDRESS_LENGTH", 10)
#     max_len = getattr(Config.Detectors, "MAX_ADDRESS_LENGTH", 100)
#     suffix_pat = re.compile(_ADDRESS_SUFFIX, re.IGNORECASE)
#     result = []
#     for m in _ADDRESS_RE.finditer(text):
#         span = m.group()
#         if not (min_len < len(span) < max_len):
#             continue
#         if not re.search(r'\b\d+\b', span):
#             continue
#         if not suffix_pat.search(span):
#             continue
#         result.append({"label": "ADDRESS", "text": span, "start": m.start(), "end": m.end()})
#     return result


# def _detect_pan(text: str) -> List[Dict[str, Any]]:
#     return _spans("PAN", _PAN_RE, text)


# def _detect_passport(text: str) -> List[Dict[str, Any]]:
#     return _spans("PASSPORT", _PASSPORT_RE, text)


# def _detect_driving_licence(text: str) -> List[Dict[str, Any]]:
#     return _spans("DRIVING_LICENCE", _DRIVING_LICENCE_RE, text)


# def _detect_pincode(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _PINCODE_RE.finditer(text):
#         start, end = m.start(), m.end()
#         before = text[start - 1] if start > 0 else ' '
#         after  = text[end]       if end < len(text) else ' '
#         if before.isdigit() or after.isdigit():
#             continue
#         result.append({"label": "PINCODE", "text": m.group(), "start": start, "end": end})
#     return result


# def _detect_vehicle_reg(text: str) -> List[Dict[str, Any]]:
#     return _spans("VEHICLE_REG", _VEHICLE_REG_RE, text)


# def _detect_gst(text: str) -> List[Dict[str, Any]]:
#     return _spans("GST", _GST_RE, text)


# def _detect_ifsc(text: str) -> List[Dict[str, Any]]:
#     return _spans("IFSC", _IFSC_RE, text)


# def _detect_upi(text: str) -> List[Dict[str, Any]]:
#     return _spans("UPI", _UPI_RE, text)


# def _detect_dob(text: str) -> List[Dict[str, Any]]:
#     return _spans("DOB", _DOB_RE, text)


# def _detect_ip(text: str) -> List[Dict[str, Any]]:
#     return _spans("IP", _IP_RE, text)


# def _detect_urls(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _URL_RE.finditer(text):
#         url = m.group()
#         if url.count('/') <= 2 and '?' not in url and '#' not in url:
#             continue
#         result.append({"label": "URL", "text": url, "start": m.start(), "end": m.end()})
#     return result


# def _detect_salary(text: str) -> List[Dict[str, Any]]:
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
#     """
#     FIX: Only flag ALL-CAPS tokens as ORG when they are NOT in the expanded
#     stopword list AND are not structural field labels (e.g. 'FULL NAME:').
#     """
#     result = []
#     for m in _ALLCAPS_ORG_RE.finditer(text):
#         token = m.group()
#         if token in _ALLCAPS_ORG_STOPWORDS:
#             continue
#         # FIX: skip if the token appears immediately before a colon (field label pattern)
#         end = m.end()
#         suffix = text[end:end + 2].strip()
#         if suffix.startswith(':'):
#             continue
#         result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
#     return result


# # FIX 4 & 5: New detectors for API keys, passwords
# def _detect_aws_keys(text: str) -> List[Dict[str, Any]]:
#     """AWS Access Keys: AKIAIOSFODNN7EXAMPL"""
#     return _spans("API_KEY", _AWS_KEY_RE, text)


# def _detect_api_keys(text: str) -> List[Dict[str, Any]]:
#     """Generic API key / secret / token values (context-based)."""
#     result = []
#     for m in _API_KEY_RE.finditer(text):
#         # Mask the entire match (key name + value) so nothing leaks
#         result.append({
#             "label": "API_KEY",
#             "text":  m.group(),
#             "start": m.start(),
#             "end":   m.end(),
#         })
#     return result


# def _detect_passwords(text: str) -> List[Dict[str, Any]]:
#     """Password / credential fields (context-based)."""
#     result = []
#     for m in _PASSWORD_RE.finditer(text):
#         result.append({
#             "label": "PASSWORD",
#             "text":  m.group(),
#             "start": m.start(),
#             "end":   m.end(),
#         })
#     return result


# # ---------------------------------------------------------------------------
# # Public spaCy wrapper
# # FIX 2: Filter out structural false-positives from spaCy ORG detection
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

#                 # FIX: skip spaCy ORG tags that are structural document labels
#                 if label == "ORG":
#                     ent_lower = ent.text.strip().lower()
#                     if ent_lower in _SPACY_ORG_FALSE_POSITIVES:
#                         logger.debug("spaCy ORG false-positive skipped: '%s'", ent.text)
#                         continue
#                     # FIX: skip if the matched text is followed by a colon (field label)
#                     end_char = ent.end_char
#                     suffix = text[end_char:end_char + 2].strip()
#                     if suffix.startswith(':'):
#                         logger.debug("spaCy ORG label (before colon) skipped: '%s'", ent.text)
#                         continue

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
#     d = Config.Detectors
#     entities: List[Dict[str, Any]] = []
#     try:
#         # ── Highest confidence: credentials & keys (run first) ────────────────
#         if getattr(d, 'ENABLE_API_KEYS', True):
#             entities.extend(_detect_aws_keys(text))
#             entities.extend(_detect_api_keys(text))
#         if getattr(d, 'ENABLE_PASSWORDS', True):
#             entities.extend(_detect_passwords(text))
#         # ── Core structured patterns ──────────────────────────────────────────
#         if d.ENABLE_EMAIL:            entities.extend(_detect_emails(text))
#         if d.ENABLE_PHONE:            entities.extend(_detect_phones(text))
#         if d.ENABLE_CARD:             entities.extend(_detect_cards(text))
#         if d.ENABLE_AADHAAR:          entities.extend(_detect_aadhaar(text))
#         # ── India-specific structured patterns ─────────────────────────────────
#         if d.ENABLE_PAN:              entities.extend(_detect_pan(text))
#         if d.ENABLE_PASSPORT:         entities.extend(_detect_passport(text))
#         if d.ENABLE_DRIVING_LICENCE:  entities.extend(_detect_driving_licence(text))
#         if d.ENABLE_GST:              entities.extend(_detect_gst(text))
#         if d.ENABLE_IFSC:             entities.extend(_detect_ifsc(text))
#         if d.ENABLE_UPI:              entities.extend(_detect_upi(text))
#         if d.ENABLE_VEHICLE_REG:      entities.extend(_detect_vehicle_reg(text))
#         if d.ENABLE_PINCODE:          entities.extend(_detect_pincode(text))
#         if d.ENABLE_ID:               entities.extend(_detect_ids(text))
#         # ── Context-dependent patterns ─────────────────────────────────────────
#         if d.ENABLE_DOB:              entities.extend(_detect_dob(text))
#         if d.ENABLE_IP:               entities.extend(_detect_ip(text))
#         if d.ENABLE_URL:              entities.extend(_detect_urls(text))
#         if d.ENABLE_SALARY:           entities.extend(_detect_salary(text))
#         if d.ENABLE_ADDRESS:          entities.extend(_detect_addresses(text))
#         # ── Name / location / org patterns (lower precision) ──────────────────
#         if d.ENABLE_COMMON_NAMES:     entities.extend(_detect_common_names(text))
#         if d.ENABLE_INDIAN_CITIES:    entities.extend(_detect_indian_cities(text))
#         if d.ENABLE_SINGLE_ORGS:      entities.extend(_detect_single_word_orgs(text))
#         if d.ENABLE_MULTI_ORGS:       entities.extend(_detect_multi_word_orgs(text))
#         if d.ENABLE_ALLCAPS_ORGS:     entities.extend(_detect_allcaps_orgs(text))
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
#         logger.warning(
#             "Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.",
#             len(raw_text), max_len,
#         )
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



# # day 28 upadte 
# from __future__ import annotations

# # day 27 update — international robustness pass
# # Changes vs day 26:
# #   PHONE    — full international coverage (UK, DE, CN, BR, NG, RU, AU, FR, US bare)
# #   ADDRESS  — 3-pattern global regex (number-first, suffix-first, flat/plot prefix)
# #   POSTCODE — new detector replacing India-only PINCODE with global postcode regex
# #   NAMES    — +97 names: South Indian, Bengali, modern Western, global surnames
# #   CARD     — Luhn check post-filter (eliminates false positives on numeric IDs)
# #   PASSPORT — fixed character class to include Z (Indian series uses A-Z)
# #   CONFIG   — MAX_ADDRESS_LENGTH raised 100→200; ENABLE_POSTCODE flag added

# import logging
# import re
# import unicodedata
# from typing import Any, Dict, List, Optional

# import requests

# from .config import Config

# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # spaCy — loaded once at import time
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
#     "API_KEY":          5,
#     "PASSWORD":         5,
#     "VEHICLE_REG":      4,
#     "IP":               4,
#     "URL":              4,
#     "POSTCODE":         3,  # NEW (replaces India-only PINCODE in priority)
#     "ADDRESS":          3,
#     "PINCODE":          3,  # kept for backward compat with existing masker labels
#     "DOB":              3,
#     "SALARY":           3,
#     "ID":               2,
#     "ORG":              1,
#     "PERSON":           1,
#     "LOCATION":         1,
# }

# # ---------------------------------------------------------------------------
# # Common names — expanded with South Indian, Bengali, modern Western,
# # global surnames. All lowercase for case-insensitive matching.
# # ---------------------------------------------------------------------------
# COMMON_NAMES: frozenset[str] = frozenset({
#     # ── Indian first names (original) ─────────────────────────────────────
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
#     "harish", "naresh", "prakash", "rajesh", "umesh", "vinod",
#     "ashok", "devesh", "ganesh", "jagdish", "kamlesh", "lokesh", "mukesh",
#     "omkar", "pramod", "ritesh", "santosh", "tapan", "vaibhav",
#     # ── South Indian first names (NEW) ────────────────────────────────────
#     "karthik", "karthikeyan", "nithya", "sowmya", "balaji", "venkatesan",
#     "preethi", "anand", "bharathi", "meena", "sathish", "senthil", "murugan",
#     "selvam", "thenmozhi", "kavitha", "nalini", "rajendran", "sundaram",
#     "shankar", "srinivasan", "venkat", "balasubramanian", "rajagopal",
#     "subramanian", "krishnamurthy", "sivasubramanian", "raghunathan",
#     "meenakshi", "saraswathi", "devi", "amudha", "saranya", "surya",
#     "aarthi", "revathi", "padmavathi", "suganya", "vijayalakshmi",
#     "nandhini", "abhinaya", "pavithra", "vaishnavi", "nithyashree",
#     "arumugam", "palaniswamy", "kumarasamy", "duraisamy", "mariappan",
#     "chellapan", "pazhanisamy", "tamilarasan", "ilayaraja", "ganesan",
#     "natarajan", "saravanan", "muthukumar", "periasamy", "velusamy",
#     "soundararajan", "subramaniam", "venkataraman", "sivaramakrishnan",
#     # ── Bengali first names (NEW) ──────────────────────────────────────────
#     "arnab", "subha", "suman", "dibyendu", "sourav", "sandip", "sutapa",
#     "mrinmoy", "suparna", "debashis", "tapas", "rima", "mousumi", "ipsita",
#     "abhijit", "indrani", "swapna", "debasish", "prasenjit", "sunanda",
#     "paramita", "saswata", "shyamal", "bidyut", "anindita", "soumyajit",
#     "arunava", "srabanti", "rituparno", "priyanka", "debjani", "bappaditya",
#     # ── Indian surnames (original + expanded) ─────────────────────────────
#     "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
#     "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
#     "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
#     "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
#     "chavan", "nikam", "kadam", "bhosle", "kohli", "malhotra", "kapoor",
#     "khanna", "chopra", "bose", "mukherjee", "chatterjee", "banerjee",
#     "chakraborty", "iyer", "nair", "menon", "pillai", "krishnan", "narayanan",
#     "venkatesh", "rajan", "swaminathan",
#     # South Indian surnames (NEW)
#     "arumugam", "ramasamy", "govindasamy", "annamalai", "subbiah",
#     "muthuswamy", "theagarajan", "balakrishnan", "krishnaswamy",
#     "parthasarathy", "sivaraman", "sundaresan", "thyagarajan",
#     # Bengali surnames (NEW)
#     "ghosh", "das", "dey", "roy", "sen", "datta", "mitra", "paul",
#     "sarkar", "mandal", "mondal", "chakravarti", "biswas", "haldar",
#     "bhattacharya", "bhattacharyya", "ganguly", "goswami",
#     # ── Western first names (original) ────────────────────────────────────
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
#     # Modern Western first names (NEW — popular 2000-2020)
#     "liam", "noah", "oliver", "elijah", "aiden", "lucas", "mason", "ethan",
#     "logan", "caden", "jackson", "sebastian", "mateo", "owen", "wyatt",
#     "isabella", "sophia", "mia", "charlotte", "amelia", "harper", "evelyn",
#     "avery", "sofia", "camila", "aria", "scarlett", "penelope", "riley",
#     "zoe", "ella", "madison", "grace", "layla", "natalie", "luna", "zoey",
#     "hannah", "lily", "ellie", "aubrey", "addison", "leah", "paisley",
#     "nora", "skylar", "stella", "savannah", "isla", "claire", "violet",
#     "aurora", "chloe", "hazel", "brooklyn", "bella", "alice", "quinn",
#     # ── Common Western surnames (NEW) ─────────────────────────────────────
#     "smith", "jones", "williams", "taylor", "brown", "davies", "evans",
#     "wilson", "thomas", "johnson", "martin", "garcia", "martinez",
#     "rodriguez", "hernandez", "lopez", "gonzalez", "perez", "sanchez",
#     "ramirez", "torres", "flores", "rivera", "gomez", "diaz", "reyes",
#     "miller", "davis", "moore", "anderson", "jackson", "harris", "martin",
#     "thompson", "white", "robinson", "clark", "walker", "lewis", "hall",
#     "allen", "young", "king", "scott", "green", "baker", "adams", "nelson",
#     "carter", "mitchell", "campbell", "turner", "phillips", "parker",
#     # UK/Irish surnames (NEW)
#     "murphy", "kelly", "o'brien", "ryan", "walsh", "kennedy", "o'sullivan",
#     "byrne", "o'connor", "mccarthy", "o'neill", "gallagher", "doyle",
#     # German surnames (NEW)
#     "mueller", "schmidt", "schneider", "fischer", "weber", "meyer", "wagner",
#     "becker", "schulz", "hoffmann", "braun", "richter", "klein", "wolf",
#     # French surnames (NEW)
#     "dubois", "bernard", "moreau", "petit", "leroy", "roux", "david",
#     "bertrand", "dumont", "lambert", "fontaine", "rousseau", "vincent",
#     # ── Arabic / Middle-Eastern ────────────────────────────────────────────
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     "ibrahim", "ismail", "yusuf", "mustafa", "hamza", "bilal", "tariq",
#     "aisha", "zainab", "maryam", "nour", "hana", "sara", "rania", "dina",
#     # ── Chinese / East Asian ───────────────────────────────────────────────
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     "wu", "zhao", "zhou", "xu", "sun", "ma", "zhu", "guo", "he", "lin",
#     # ── Spanish / Latin ───────────────────────────────────────────────────
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     "andres", "alejandro", "camilo", "valentina", "isabella", "luciana",
#     # ── Russian / Eastern European ────────────────────────────────────────
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     "aleksei", "mikhail", "elena", "irina", "anastasia", "ekaterina",
#     "nikolai", "andrei", "viktor", "yulia", "larisa", "svetlana",
#     # ── Japanese ──────────────────────────────────────────────────────────
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     "riku", "kaito", "hana", "yui", "aoi", "koharu", "nana", "rina",
#     # ── Korean ────────────────────────────────────────────────────────────
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
#     "jiyeon", "minjun", "seoyeon", "jisoo", "taehyung", "jimin", "sujin",
#     # ── Extra ─────────────────────────────────────────────────────────────
#     "jacky",
# })

# # ---------------------------------------------------------------------------
# # Indian cities / locations (unchanged from day 26)
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
#     "maharashtra", "karnataka", "gujarat", "rajasthan", "uttar pradesh",
#     "madhya pradesh", "tamil nadu", "andhra pradesh", "telangana",
#     "west bengal", "kerala", "punjab", "haryana", "bihar", "jharkhand",
#     "odisha", "assam", "chhattisgarh", "uttarakhand", "himachal pradesh",
#     "manipur", "meghalaya", "mizoram", "nagaland", "sikkim",
#     "arunachal pradesh", "tripura",
# })

# # ---------------------------------------------------------------------------
# # Organisation word lists (unchanged from day 26)
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
#     "state bank of india", "reserve bank of india", "bank of baroda",
#     "punjab national bank", "union bank", "canara bank", "indian bank",
#     "hdfc bank", "icici bank", "axis bank", "kotak mahindra",
#     "tata consultancy services", "tata motors", "tata steel",
#     "infosys technologies", "wipro technologies", "hcl technologies",
#     "reliance industries", "reliance jio", "mahindra mahindra",
#     "bajaj auto", "bajaj finance", "hero motocorp", "maruti suzuki",
#     "ola cabs", "air india", "indigo airlines", "spicejet",
# })

# # ---------------------------------------------------------------------------
# # ALLCAPS stopwords (unchanged from day 26)
# # ---------------------------------------------------------------------------
# _ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
#     "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
#     "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
#     "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
#     "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
#     "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
#     "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
#     "PNG", "JPG", "ZIP", "OTP", "PIN", "DOB", "PAN", "GST", "UPI",
#     "EMI", "KYC", "NRI", "PF", "EPF", "TDS", "ITR",
#     "NAME", "EMAIL", "PHONE", "MOBILE", "ADDRESS", "DOB", "AGE", "SEX",
#     "GENDER", "PROFILE", "CANDIDATE", "REFERENCE", "CONTACT", "ALTERNATE",
#     "PRIMARY", "SECONDARY", "TECHNICAL", "ENVIRONMENT", "LOCAL", "REMOTE",
#     "FULL", "FIRST", "LAST", "MIDDLE", "MASKED", "REDACTED",
#     "EDUCATION", "OCCUPATION", "INTERNSHIP", "PROJECT", "REPOSITORY",
#     "TRAVEL", "PASSPORT", "VISA", "FLIGHT", "CURRENT", "FOCUS",
#     "RESIDENTIAL", "PERMANENT", "OFFICIAL", "PERSONAL",
#     "DB", "AWS", "GCP", "S3", "EC2", "VPC", "IAM", "ARN",
#     "JWT", "SSH", "SSL", "TLS", "HTTP", "HTTPS", "TCP", "UDP",
#     "VTU", "SEAT", "USN", "REG", "DEPT", "SEM", "BATCH",
#     "BE", "ME", "BTech", "MTech", "BCA", "MCA", "BSC", "MSC",
# })

# _SPACY_ORG_FALSE_POSITIVES: frozenset[str] = frozenset({
#     "candidate", "profile", "reference", "internal", "contact",
#     "education", "technical", "environment", "local", "remote",
#     "full name", "primary", "secondary", "alternate", "residential",
#     "permanent", "official", "personal", "masked", "redacted",
#     "b.e", "m.tech", "b.tech", "bca", "mca", "internship",
#     "project", "repository", "travel", "flight", "current", "focus",
#     "university seat", "seat number",
# })

# _STRUCTURAL_LABEL_RE = re.compile(
#     r'^(?:\d+\.\s*)?'
#     r'(?:full\s+)?'
#     r'(?:name|email|phone|mobile|address|contact|alternate|primary|secondary|'
#     r'occupation|education|candidate|profile|reference|technical|environment|'
#     r'travel|internship|project|repository|current|focus|residential|'
#     r'emergency|passport|visa|local|api|db|database)\b',
#     re.IGNORECASE,
# )

# # ---------------------------------------------------------------------------
# # Pre-compiled regexes
# # ---------------------------------------------------------------------------

# _EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# # ---------------------------------------------------------------------------
# # PHONE — full international coverage
# #
# # Branch order (first match wins via alternation):
# #   1. India +91 explicit          → +91 98450 12345
# #   2. India STD code              → 080-2345-6789
# #   3. India bare 10-digit mobile  → 9845012345
# #   4. US/Canada with/without +1   → (415) 555-1234 | +1 415 555 1234
# #   5. Generic international       → +44 20 7946 0958 | +86 138 0013 8000
# #
# # Total digit length guard on branch 5 (7-15 E.164 digits after country code)
# # prevents matching plain 6-digit numbers or version strings.
# # ---------------------------------------------------------------------------
# _PHONE_RE = re.compile(
#     r'(?<!\d)'
#     r'(?:'
#     # Branch 1: India +91 with space/dash then 10 digits (possibly spaced)
#     r'\+91[\s\-]?\d{5}[\s\-]?\d{5}'
#     r'|'
#     # Branch 2: India STD (0 + 2-4 digit area code + 6-8 digit number)
#     r'0\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}'
#     r'|'
#     # Branch 3: Plain 10-digit Indian mobile (starts 6-9)
#     r'[6-9]\d{9}'
#     r'|'
#     # Branch 4: US/Canada — optional +1 then (DDD) DDD-DDDD or DDD-DDD-DDDD
#     r'(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
#     r'|'
#     # Branch 5: Generic international — +CC then digits/separators, 7-15 total digits
#     # Negative lookahead excludes +1 and +91 (already handled above)
#     r'\+(?!1[\s\-.(]|91[\s\-])'
#     r'\d{1,3}'                              # country code 1-3 digits
#     r'[\s\-.]?'
#     r'(?:\(?\d{1,4}\)?[\s\-.]?)?'          # optional area code in parens
#     r'\d{2,4}[\s\-.]?\d{2,4}'             # main number blocks
#     r'(?:[\s\-.]?\d{2,4})?'               # optional trailing block
#     r')'
#     r'(?!\d)',
#     re.ASCII,
# )

# # ---------------------------------------------------------------------------
# # Credit card — Luhn-validated in the detector function below
# # ---------------------------------------------------------------------------
# _CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')


# def _luhn_check(number: str) -> bool:
#     """Return True if the digit string passes the Luhn algorithm."""
#     digits = [int(d) for d in number if d.isdigit()]
#     if not (13 <= len(digits) <= 19):
#         return False
#     total = 0
#     for i, d in enumerate(reversed(digits)):
#         if i % 2 == 1:
#             d *= 2
#             if d > 9:
#                 d -= 9
#         total += d
#     return total % 10 == 0


# # Aadhaar — exactly 12 digits in groups of 4
# _AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# # Generic numeric ID — 9 to 15 digits (skips 12-digit Aadhaar and 16-digit card)
# _ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# # ---------------------------------------------------------------------------
# # ADDRESS — three-pattern global regex
# #
# # Pattern 1: Number-first (most common globally)
# #   123 Main Street | 1600 Pennsylvania Avenue NW
# # Pattern 2: Suffix-first (Indian, German)
# #   MG Road, Bangalore | Unter den Linden 6
# # Pattern 3: Flat/Plot/Unit prefix (Indian apartment addressing)
# #   Flat 4B, Sunshine Apartments | Plot 23, Electronic City
# # ---------------------------------------------------------------------------
# _ADDRESS_SUFFIX_GLOBAL = (
#     r'(?:'
#     # English / global
#     r'road|rd|street|st|avenue|ave|lane|ln|drive|dr|'
#     r'court|ct|plaza|way|boulevard|blvd|crescent|cres|'
#     r'place|pl|terrace|ter|close|grove|gardens|park|'
#     r'highway|hwy|freeway|expressway|'
#     # Apartment / unit indicators
#     r'apt|apartment|flat|suite|ste|unit|floor|fl|bldg|building|'
#     # Indian
#     r'nagar|colony|sector|vihar|enclave|marg|chowk|bazaar|'
#     r'cross|main|layout|extension|phase|block|puram|ganj|'
#     r'pur|wadi|pada|wala|katte|halli|palya|'
#     # German
#     r'strasse|stra\xdfe|str\.|allee|gasse|weg|platz|'
#     # French
#     r'rue|allée|impasse|'
#     # Spanish / Portuguese
#     r'calle|carrera|avenida|paseo|'
#     r')'
# )

# _ADDRESS_RE = re.compile(
#     r'(?:'
#     # Pattern 1: Number-first (123 Main St, 221B Baker Street)
#     r'\b\d{1,5}[A-Za-z]?(?:[\-/]\d{1,4})?'
#     r'(?:[\s,]+[A-Za-z]{2,}){1,5}'
#     r'(?:[\s,]+' + _ADDRESS_SUFFIX_GLOBAL + r')?'
#     r'|'
#     # Pattern 2: Suffix-first (MG Road, Unter den Linden 6)
#     r'\b[A-Za-z]{2,}(?:[\s]+[A-Za-z]{2,}){0,4}[\s,]+'
#     r'(?:' + _ADDRESS_SUFFIX_GLOBAL + r')'
#     r'(?:[\s]+\d{1,5})?'
#     r'|'
#     # Pattern 3: Flat/Plot/Unit/House prefix
#     r'\b(?:flat|plot|house|door|unit|apt|apartment|block|no\.?|#)'
#     r'\s*\d{1,4}[A-Za-z]?'
#     r'(?:[\s,]+[A-Za-z0-9]{2,}){1,6}'
#     r')',
#     re.IGNORECASE,
# )

# # ---------------------------------------------------------------------------
# # POSTCODE — global multi-country postcode detector
# #
# # Covers: India (6-digit), UK (SW1A 2AA), US ZIP (90210 / 90210-1234),
# # Canada (M5V 3L9), Germany/France/Italy/Spain (5-digit), Australia (4-digit),
# # Netherlands (1234 AB), Brazil (01310-100), Japan (106-0032),
# # South Korea (5-digit handled by US branch), Singapore (6-digit).
# #
# # Note: keeps the original PINCODE detector active for backward compatibility
# # with existing placeholder labels. POSTCODE detector uses a new label.
# # ---------------------------------------------------------------------------
# _POSTCODE_RE = re.compile(
#     r'(?<![A-Za-z\d])'
#     r'(?:'
#     # UK: A9 9AA | A99 9AA | AA9 9AA | AA99 9AA | A9A 9AA | AA9A 9AA
#     r'[A-Z]{1,2}\d[A-Z\d]?[ ]?\d[A-Z]{2}'
#     r'|'
#     # Canada: A1A 1A1
#     r'[A-Z]\d[A-Z][ ]?\d[A-Z]\d'
#     r'|'
#     # Netherlands: 1234 AB (must come before bare 4-digit to avoid collision)
#     r'\d{4}[ ]?[A-Z]{2}'
#     r'|'
#     # Brazil: 01310-100
#     r'\d{5}-\d{3}'
#     r'|'
#     # Japan: 106-0032
#     r'\d{3}-\d{4}'
#     r'|'
#     # US ZIP+4: 90210-1234
#     r'\d{5}-\d{4}'
#     r'|'
#     # India 6-digit (starts 1-9), Singapore 6-digit, US 5-digit ZIP
#     # All caught by generic 5-6 digit rule — disambiguated by context in detector
#     r'[1-9]\d{5}'
#     r'|'
#     r'\d{5}'
#     r'|'
#     # Australia: 4-digit (only flag if surrounded by whitespace/comma to reduce FP)
#     r'(?<=[\s,])\d{4}(?=[\s,\.]|$)'
#     r')'
#     r'(?![A-Za-z\d])',
#     re.IGNORECASE,
# )

# # India-only pincode kept for label backward compatibility
# _PINCODE_RE = re.compile(r'\b[1-9]\d{5}\b')

# # PAN card
# _PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# # Indian Passport — FIX: original regex excluded Z; Indian passports use A-Z
# # Old: [A-PR-WYa-pr-wy]  ← missed X and Z series
# # New: [A-Z]             ← all uppercase letters, 7 digits
# _PASSPORT_RE = re.compile(r'\b[A-Z][0-9]{7}\b')

# # Indian Driving Licence
# _DRIVING_LICENCE_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{7}\b',
#     re.IGNORECASE,
# )

# # Indian Vehicle Registration
# _VEHICLE_REG_RE = re.compile(
#     r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b',
#     re.IGNORECASE,
# )

# # GST Number
# _GST_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')

# # IFSC Code
# _IFSC_RE = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# # UPI ID
# _UPI_RE = re.compile(
#     r'\b[\w.\-+]+@(?:upi|paytm|gpay|phonepe|ybl|okaxis|okicici|okhdfcbank|'
#     r'oksbi|apl|ibl|axl|aubank|barodampay|cnrb|csbpay|dbs|dlb|'
#     r'equitas|fbl|federal|finobank|hdfcbank|icici|idbi|idfc|'
#     r'indus|iob|jkb|jsb|karb|kbl|kotak|kvb|lvb|mahb|'
#     r'niyobank|postbank|rbl|sbi|scb|tjsb|ubi|ucb|unionbank|'
#     r'utib|vijb|yapl)\b',
#     re.IGNORECASE,
# )

# # Date of Birth
# _DOB_RE = re.compile(
#     r'(?:'
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\/\-\.\ ](?:0?[1-9]|1[0-2])[\/\-\.\ ](?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:19|20)\d{2}[\/\-\.](?:0?[1-9]|1[0-2])[\/\-\.](?:0?[1-9]|[12]\d|3[01])\b'
#     r'|'
#     r'\b(?:0?[1-9]|[12]\d|3[01])[\s]+(?:january|february|march|april|may|june|'
#     r'july|august|september|october|november|december)[\s,]+(?:19|20)\d{2}\b'
#     r'|'
#     r'\b(?:january|february|march|april|may|june|july|august|september|'
#     r'october|november|december)[\s]+(?:0?[1-9]|[12]\d|3[01])[\s,]+(?:19|20)\d{2}\b'
#     r')',
#     re.IGNORECASE,
# )

# # IP address: IPv4
# _IP_RE = re.compile(
#     r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
# )

# # URLs with non-trivial paths
# _URL_RE = re.compile(
#     r'\bhttps?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]{10,}\b',
#     re.IGNORECASE,
# )

# # Salary / financial figures
# _SALARY_RE = re.compile(
#     r'(?:'
#     r'(?:₹|rs\.?|inr|usd|\$|£|€)[\s]?\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?'
#     r'|'
#     r'\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?[\s]?(?:rupees?|lakh|lakhs|crore|crores|k|thousand)'
#     r')',
#     re.IGNORECASE,
# )

# # AWS Access Key
# _AWS_KEY_RE = re.compile(r'\bAKIA[0-9A-Z]{16}\b')

# # Generic API key / secret / token (context-based)
# _API_KEY_RE = re.compile(
#     r'(?i)(?:api[_\-]?key|secret[_\-]?key|access[_\-]?token|auth[_\-]?token'
#     r'|bearer|private[_\-]?key)\s*[:=]\s*["\']?([A-Za-z0-9\-_.+/]{8,})["\']?'
# )

# # Password / credential (context-based)
# _PASSWORD_RE = re.compile(
#     r'(?i)(?:password|passwd|pwd|db_password|db_pass|secret_pass)\s*[:=]\s*["\']?(\S+)["\']?'
# )

# # Common names regex (sorted longest-first to prefer longer matches)
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

# # All-caps orgs: 3-10 letters
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
#     """Credit card detection with Luhn post-filter to eliminate false positives."""
#     result = []
#     for m in _CARD_RE.finditer(text):
#         if _luhn_check(m.group()):
#             result.append({"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()})
#         else:
#             logger.debug("Card-pattern match failed Luhn check, skipping: %s", m.group())
#     return result


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
#     """
#     Global address detection using 3-pattern regex.
#     Guards: length bounds from config, must contain at least one word of 3+ chars.
#     MAX_ADDRESS_LENGTH raised to 200 in config to handle full international addresses.
#     """
#     min_len = getattr(Config.Detectors, "MIN_ADDRESS_LENGTH", 10)
#     max_len = getattr(Config.Detectors, "MAX_ADDRESS_LENGTH", 200)
#     result = []
#     for m in _ADDRESS_RE.finditer(text):
#         span = m.group()
#         span_stripped = span.strip()
#         if not (min_len < len(span_stripped) < max_len):
#             continue
#         # Must contain at least one alphabetic word of 3+ characters
#         if not re.search(r'[A-Za-z]{3,}', span_stripped):
#             continue
#         result.append({
#             "label": "ADDRESS",
#             "text":  span_stripped,
#             "start": m.start(),
#             "end":   m.end(),
#         })
#     return result


# def _detect_postcode(text: str) -> List[Dict[str, Any]]:
#     """
#     International postcode detector.
#     Labels as POSTCODE (distinct from India-only PINCODE) so masker can
#     use a separate placeholder if desired.
#     """
#     result = []
#     for m in _POSTCODE_RE.finditer(text):
#         raw = m.group().strip()
#         # Skip standalone 4-5 digit numbers that are more likely IDs than postcodes
#         # unless they look like a real ZIP (e.g. preceded by a state abbreviation or comma)
#         if re.fullmatch(r'\d{4,5}', raw):
#             before = text[max(0, m.start() - 5):m.start()]
#             # Only accept bare 4-5 digit codes if preceded by a comma, space+2-letter abbrev, or newline
#             if not re.search(r'(?:,\s*|[A-Z]{2}\s+)$', before):
#                 continue
#         result.append({"label": "POSTCODE", "text": raw, "start": m.start(), "end": m.end()})
#     return result


# def _detect_pincode(text: str) -> List[Dict[str, Any]]:
#     """India-only 6-digit pincode. Kept for label backward compatibility."""
#     result = []
#     for m in _PINCODE_RE.finditer(text):
#         start, end = m.start(), m.end()
#         before = text[start - 1] if start > 0 else ' '
#         after  = text[end]       if end < len(text) else ' '
#         if before.isdigit() or after.isdigit():
#             continue
#         result.append({"label": "PINCODE", "text": m.group(), "start": start, "end": end})
#     return result


# def _detect_pan(text: str) -> List[Dict[str, Any]]:
#     return _spans("PAN", _PAN_RE, text)


# def _detect_passport(text: str) -> List[Dict[str, Any]]:
#     return _spans("PASSPORT", _PASSPORT_RE, text)


# def _detect_driving_licence(text: str) -> List[Dict[str, Any]]:
#     return _spans("DRIVING_LICENCE", _DRIVING_LICENCE_RE, text)


# def _detect_vehicle_reg(text: str) -> List[Dict[str, Any]]:
#     return _spans("VEHICLE_REG", _VEHICLE_REG_RE, text)


# def _detect_gst(text: str) -> List[Dict[str, Any]]:
#     return _spans("GST", _GST_RE, text)


# def _detect_ifsc(text: str) -> List[Dict[str, Any]]:
#     return _spans("IFSC", _IFSC_RE, text)


# def _detect_upi(text: str) -> List[Dict[str, Any]]:
#     return _spans("UPI", _UPI_RE, text)


# def _detect_dob(text: str) -> List[Dict[str, Any]]:
#     return _spans("DOB", _DOB_RE, text)


# def _detect_ip(text: str) -> List[Dict[str, Any]]:
#     return _spans("IP", _IP_RE, text)


# def _detect_urls(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _URL_RE.finditer(text):
#         url = m.group()
#         if url.count('/') <= 2 and '?' not in url and '#' not in url:
#             continue
#         result.append({"label": "URL", "text": url, "start": m.start(), "end": m.end()})
#     return result


# def _detect_salary(text: str) -> List[Dict[str, Any]]:
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
#         if token in _ALLCAPS_ORG_STOPWORDS:
#             continue
#         end = m.end()
#         suffix = text[end:end + 2].strip()
#         if suffix.startswith(':'):
#             continue
#         result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
#     return result


# def _detect_aws_keys(text: str) -> List[Dict[str, Any]]:
#     return _spans("API_KEY", _AWS_KEY_RE, text)


# def _detect_api_keys(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _API_KEY_RE.finditer(text):
#         result.append({"label": "API_KEY", "text": m.group(), "start": m.start(), "end": m.end()})
#     return result


# def _detect_passwords(text: str) -> List[Dict[str, Any]]:
#     result = []
#     for m in _PASSWORD_RE.finditer(text):
#         result.append({"label": "PASSWORD", "text": m.group(), "start": m.start(), "end": m.end()})
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

#                 if label == "ORG":
#                     ent_lower = ent.text.strip().lower()
#                     if ent_lower in _SPACY_ORG_FALSE_POSITIVES:
#                         logger.debug("spaCy ORG false-positive skipped: '%s'", ent.text)
#                         continue
#                     end_char = ent.end_char
#                     suffix = text[end_char:end_char + 2].strip()
#                     if suffix.startswith(':'):
#                         logger.debug("spaCy ORG label (before colon) skipped: '%s'", ent.text)
#                         continue

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
#     d = Config.Detectors
#     entities: List[Dict[str, Any]] = []
#     try:
#         # ── Highest confidence: credentials & keys ─────────────────────────
#         if getattr(d, 'ENABLE_API_KEYS', True):
#             entities.extend(_detect_aws_keys(text))
#             entities.extend(_detect_api_keys(text))
#         if getattr(d, 'ENABLE_PASSWORDS', True):
#             entities.extend(_detect_passwords(text))
#         # ── Core structured patterns ───────────────────────────────────────
#         if d.ENABLE_EMAIL:           entities.extend(_detect_emails(text))
#         if d.ENABLE_PHONE:           entities.extend(_detect_phones(text))
#         if d.ENABLE_CARD:            entities.extend(_detect_cards(text))
#         if d.ENABLE_AADHAAR:         entities.extend(_detect_aadhaar(text))
#         # ── India-specific structured patterns ─────────────────────────────
#         if d.ENABLE_PAN:             entities.extend(_detect_pan(text))
#         if d.ENABLE_PASSPORT:        entities.extend(_detect_passport(text))
#         if d.ENABLE_DRIVING_LICENCE: entities.extend(_detect_driving_licence(text))
#         if d.ENABLE_GST:             entities.extend(_detect_gst(text))
#         if d.ENABLE_IFSC:            entities.extend(_detect_ifsc(text))
#         if d.ENABLE_UPI:             entities.extend(_detect_upi(text))
#         if d.ENABLE_VEHICLE_REG:     entities.extend(_detect_vehicle_reg(text))
#         if d.ENABLE_PINCODE:         entities.extend(_detect_pincode(text))
#         if d.ENABLE_ID:              entities.extend(_detect_ids(text))
#         # ── Global postcode (NEW) ──────────────────────────────────────────
#         if getattr(d, 'ENABLE_POSTCODE', True):
#             entities.extend(_detect_postcode(text))
#         # ── Context-dependent patterns ─────────────────────────────────────
#         if d.ENABLE_DOB:             entities.extend(_detect_dob(text))
#         if d.ENABLE_IP:              entities.extend(_detect_ip(text))
#         if d.ENABLE_URL:             entities.extend(_detect_urls(text))
#         if d.ENABLE_SALARY:          entities.extend(_detect_salary(text))
#         if d.ENABLE_ADDRESS:         entities.extend(_detect_addresses(text))
#         # ── Name / location / org patterns (lower precision) ───────────────
#         if d.ENABLE_COMMON_NAMES:    entities.extend(_detect_common_names(text))
#         if d.ENABLE_INDIAN_CITIES:   entities.extend(_detect_indian_cities(text))
#         if d.ENABLE_SINGLE_ORGS:     entities.extend(_detect_single_word_orgs(text))
#         if d.ENABLE_MULTI_ORGS:      entities.extend(_detect_multi_word_orgs(text))
#         if d.ENABLE_ALLCAPS_ORGS:    entities.extend(_detect_allcaps_orgs(text))
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
#         logger.warning(
#             "Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.",
#             len(raw_text), max_len,
#         )
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


# day 28 final update 
from __future__ import annotations

# day 27 update — international robustness pass
# Changes vs day 26:
#   PHONE    — full international coverage (UK, DE, CN, BR, NG, RU, AU, FR, US bare)
#   ADDRESS  — 3-pattern global regex (number-first, suffix-first, flat/plot prefix)
#   POSTCODE — new detector replacing India-only PINCODE with global postcode regex
#   NAMES    — +97 names: South Indian, Bengali, modern Western, global surnames
#   CARD     — Luhn check post-filter (eliminates false positives on numeric IDs)
#   PASSPORT — fixed character class to include Z (Indian series uses A-Z)
#   CONFIG   — MAX_ADDRESS_LENGTH raised 100→200; ENABLE_POSTCODE flag added

import logging
import re
import unicodedata
from typing import Any, Dict, List, Optional

import requests
from transformers import pipeline
import os

from .config import Config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# spaCy — loaded once at import time
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
    # Structured — regex wins
    "EMAIL":            7,
    "PHONE":            6,
    "CARD":             5,
    "AADHAAR":          5,
    "PAN":              6,
    "PASSPORT":         5,
    "DRIVING_LICENCE":  5,
    "GST":              5,
    "IFSC":             5,
    "UPI":              5,
    "API_KEY":          5,
    "PASSWORD":         5,
    "VEHICLE_REG":      4,
    "IP":               4,
    "URL":              4,
    "POSTCODE":         4,
    "PINCODE":          4,
    "DOB":              4,
    "SALARY":           4,
    "ID":               2,
    # Free-text — transformer wins
    "ADDRESS":          5,
    "ORG":              5,
    "PERSON":           5,
    "LOCATION":         5,
    # Transformer structured — lower than regex
    "EMAIL_TRANS":      4,
    "PHONE_TRANS":      4,
    "AADHAAR_TRANS":    4,
    "PAN_TRANS":        4,
    "PASSPORT_TRANS":   4,
    "DRIVING_LICENCE_TRANS": 4,
    "GST_TRANS":        4,
    "IFSC_TRANS":       4,
    "UPI_TRANS":        4,
    "CARD_TRANS":       4,
    "VEHICLE_REG_TRANS":3,
    "IP_TRANS":         3,
    "URL_TRANS":        3,
    "DOB_TRANS":        3,
    "SALARY_TRANS":     3,
    "ID_TRANS":         2,
    "API_KEY_TRANS":    4,
    "PASSWORD_TRANS":   4,
    "PINCODE_TRANS":    3,
    "POSTCODE_TRANS":   3,
    "ADDRESS_TRANS":    4,
}

# ---------------------------------------------------------------------------
# Common names — expanded with South Indian, Bengali, modern Western,
# global surnames. All lowercase for case-insensitive matching.
# ---------------------------------------------------------------------------
COMMON_NAMES: frozenset[str] = frozenset({
    # ── Indian first names (original) ─────────────────────────────────────
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
    "harish", "naresh", "prakash", "rajesh", "umesh", "vinod",
    "ashok", "devesh", "ganesh", "jagdish", "kamlesh", "lokesh", "mukesh",
    "omkar", "pramod", "ritesh", "santosh", "tapan", "vaibhav",
    # ── South Indian first names (NEW) ────────────────────────────────────
    "karthik", "karthikeyan", "nithya", "sowmya", "balaji", "venkatesan",
    "preethi", "anand", "bharathi", "meena", "sathish", "senthil", "murugan",
    "selvam", "thenmozhi", "kavitha", "nalini", "rajendran", "sundaram",
    "shankar", "srinivasan", "venkat", "balasubramanian", "rajagopal",
    "subramanian", "krishnamurthy", "sivasubramanian", "raghunathan",
    "meenakshi", "saraswathi", "devi", "amudha", "saranya", "surya",
    "aarthi", "revathi", "padmavathi", "suganya", "vijayalakshmi",
    "nandhini", "abhinaya", "pavithra", "vaishnavi", "nithyashree",
    "arumugam", "palaniswamy", "kumarasamy", "duraisamy", "mariappan",
    "chellapan", "pazhanisamy", "tamilarasan", "ilayaraja", "ganesan",
    "natarajan", "saravanan", "muthukumar", "periasamy", "velusamy",
    "soundararajan", "subramaniam", "venkataraman", "sivaramakrishnan",
    # ── Bengali first names (NEW) ──────────────────────────────────────────
    "arnab", "subha", "suman", "dibyendu", "sourav", "sandip", "sutapa",
    "mrinmoy", "suparna", "debashis", "tapas", "rima", "mousumi", "ipsita",
    "abhijit", "indrani", "swapna", "debasish", "prasenjit", "sunanda",
    "paramita", "saswata", "shyamal", "bidyut", "anindita", "soumyajit",
    "arunava", "srabanti", "rituparno", "priyanka", "debjani", "bappaditya",
    # ── Indian surnames (original + expanded) ─────────────────────────────
    "verma", "gupta", "singh", "patel", "reddy", "rao", "yadav", "jha",
    "ojha", "mishra", "dubey", "tripathi", "chaturvedi", "shukla", "pandey",
    "thakur", "mehta", "shah", "modi", "gandhi", "desai", "joshi", "kulkarni",
    "patil", "pawar", "more", "jadhav", "gaikwad", "ingale", "bhosale",
    "chavan", "nikam", "kadam", "bhosle", "kohli", "malhotra", "kapoor",
    "khanna", "chopra", "bose", "mukherjee", "chatterjee", "banerjee",
    "chakraborty", "iyer", "nair", "menon", "pillai", "krishnan", "narayanan",
    "venkatesh", "rajan", "swaminathan",
    # South Indian surnames (NEW)
    "arumugam", "ramasamy", "govindasamy", "annamalai", "subbiah",
    "muthuswamy", "theagarajan", "balakrishnan", "krishnaswamy",
    "parthasarathy", "sivaraman", "sundaresan", "thyagarajan",
    # Bengali surnames (NEW)
    "ghosh", "das", "dey", "roy", "sen", "datta", "mitra", "paul",
    "sarkar", "mandal", "mondal", "chakravarti", "biswas", "haldar",
    "bhattacharya", "bhattacharyya", "ganguly", "goswami",
    # ── Western first names (original) ────────────────────────────────────
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
    # Modern Western first names (NEW — popular 2000-2020)
    "liam", "noah", "oliver", "elijah", "aiden", "lucas", "mason", "ethan",
    "logan", "caden", "jackson", "sebastian", "mateo", "owen", "wyatt",
    "isabella", "sophia", "mia", "charlotte", "amelia", "harper", "evelyn",
    "avery", "sofia", "camila", "aria", "scarlett", "penelope", "riley",
    "zoe", "ella", "madison", "grace", "layla", "natalie", "luna", "zoey",
    "hannah", "lily", "ellie", "aubrey", "addison", "leah", "paisley",
    "nora", "skylar", "stella", "savannah", "isla", "claire", "violet",
    "aurora", "chloe", "hazel", "brooklyn", "bella", "alice", "quinn",
    # ── Common Western surnames (NEW) ─────────────────────────────────────
    "smith", "jones", "williams", "taylor", "brown", "davies", "evans",
    "wilson", "thomas", "johnson", "martin", "garcia", "martinez",
    "rodriguez", "hernandez", "lopez", "gonzalez", "perez", "sanchez",
    "ramirez", "torres", "flores", "rivera", "gomez", "diaz", "reyes",
    "miller", "davis", "moore", "anderson", "jackson", "harris", "martin",
    "thompson", "white", "robinson", "clark", "walker", "lewis", "hall",
    "allen", "young", "king", "scott", "green", "baker", "adams", "nelson",
    "carter", "mitchell", "campbell", "turner", "phillips", "parker",
    # UK/Irish surnames (NEW)
    "murphy", "kelly", "o'brien", "ryan", "walsh", "kennedy", "o'sullivan",
    "byrne", "o'connor", "mccarthy", "o'neill", "gallagher", "doyle",
    # German surnames (NEW)
    "mueller", "schmidt", "schneider", "fischer", "weber", "meyer", "wagner",
    "becker", "schulz", "hoffmann", "braun", "richter", "klein", "wolf",
    # French surnames (NEW)
    "dubois", "bernard", "moreau", "petit", "leroy", "roux", "david",
    "bertrand", "dumont", "lambert", "fontaine", "rousseau", "vincent",
    # ── Arabic / Middle-Eastern ────────────────────────────────────────────
    "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
    "ibrahim", "ismail", "yusuf", "mustafa", "hamza", "bilal", "tariq",
    "aisha", "zainab", "maryam", "nour", "hana", "sara", "rania", "dina",
    # ── Chinese / East Asian ───────────────────────────────────────────────
    "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
    "wu", "zhao", "zhou", "xu", "sun", "ma", "zhu", "guo", "he", "lin",
    # ── Spanish / Latin ───────────────────────────────────────────────────
    "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
    "andres", "alejandro", "camilo", "valentina", "isabella", "luciana",
    # ── Russian / Eastern European ────────────────────────────────────────
    "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
    "aleksei", "mikhail", "elena", "irina", "anastasia", "ekaterina",
    "nikolai", "andrei", "viktor", "yulia", "larisa", "svetlana",
    # ── Japanese ──────────────────────────────────────────────────────────
    "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
    "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
    "riku", "kaito", "hana", "yui", "aoi", "koharu", "nana", "rina",
    # ── Korean ────────────────────────────────────────────────────────────
    "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
    "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
    "jiyeon", "minjun", "seoyeon", "jisoo", "taehyung", "jimin", "sujin",
    # ── Extra ─────────────────────────────────────────────────────────────
    "jacky",
})

# Words that are commonly false-positive PERSON detections
PERSON_FALSE_POSITIVES: frozenset[str] = frozenset({
    "email", "phone", "address", "total", "version", "summary", "fax",
    "mobile", "contact", "reference", "client", "customer", "patient",
    "student", "teacher", "manager", "director", "officer", "mr", "mrs",
    "ms", "miss", "dr", "prof", "shri", "smt", "sri",
    "hello", "dear", "thanks", "regards", "sincerely",
})

# ---------------------------------------------------------------------------
# Indian cities / locations (unchanged from day 26)
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
    "maharashtra", "karnataka", "gujarat", "rajasthan", "uttar pradesh",
    "madhya pradesh", "tamil nadu", "andhra pradesh", "telangana",
    "west bengal", "kerala", "punjab", "haryana", "bihar", "jharkhand",
    "odisha", "assam", "chhattisgarh", "uttarakhand", "himachal pradesh",
    "manipur", "meghalaya", "mizoram", "nagaland", "sikkim",
    "arunachal pradesh", "tripura",
})

# ---------------------------------------------------------------------------
# Organisation word lists (unchanged from day 26)
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
    "state bank of india", "reserve bank of india", "bank of baroda",
    "punjab national bank", "union bank", "canara bank", "indian bank",
    "hdfc bank", "icici bank", "axis bank", "kotak mahindra",
    "tata consultancy services", "tata motors", "tata steel",
    "infosys technologies", "wipro technologies", "hcl technologies",
    "reliance industries", "reliance jio", "mahindra mahindra",
    "bajaj auto", "bajaj finance", "hero motocorp", "maruti suzuki",
    "ola cabs", "air india", "indigo airlines", "spicejet",
})

# ---------------------------------------------------------------------------
# ALLCAPS stopwords (unchanged from day 26)
# ---------------------------------------------------------------------------
_ALLCAPS_ORG_STOPWORDS: frozenset[str] = frozenset({
    "I", "A", "AN", "THE", "AND", "OR", "BUT", "IN", "ON", "AT", "TO",
    "OF", "FOR", "BY", "AS", "IS", "IT", "BE", "DO", "GO", "OK", "NO",
    "YES", "SO", "IF", "UP", "AM", "WE", "ME", "MY", "US", "HE", "SHE",
    "HI", "ID", "PM", "AM", "ETA", "FYI", "TBD", "TBA", "AKA", "ASAP",
    "NB", "PS", "RE", "CC", "BCC", "CV", "HR", "PR", "IT", "AI", "ML",
    "UI", "UX", "API", "URL", "URI", "SQL", "CSV", "XML", "PDF", "DOC",
    "PNG", "JPG", "ZIP", "OTP", "PIN", "DOB", "PAN", "GST", "UPI",
    "EMI", "KYC", "NRI", "PF", "EPF", "TDS", "ITR",
    "NAME", "EMAIL", "PHONE", "MOBILE", "ADDRESS", "DOB", "AGE", "SEX",
    "GENDER", "PROFILE", "CANDIDATE", "REFERENCE", "CONTACT", "ALTERNATE",
    "PRIMARY", "SECONDARY", "TECHNICAL", "ENVIRONMENT", "LOCAL", "REMOTE",
    "FULL", "FIRST", "LAST", "MIDDLE", "MASKED", "REDACTED",
    "EDUCATION", "OCCUPATION", "INTERNSHIP", "PROJECT", "REPOSITORY",
    "TRAVEL", "PASSPORT", "VISA", "FLIGHT", "CURRENT", "FOCUS",
    "RESIDENTIAL", "PERMANENT", "OFFICIAL", "PERSONAL",
    "DB", "AWS", "GCP", "S3", "EC2", "VPC", "IAM", "ARN",
    "JWT", "SSH", "SSL", "TLS", "HTTP", "HTTPS", "TCP", "UDP",
    "VTU", "SEAT", "USN", "REG", "DEPT", "SEM", "BATCH",
    "BE", "ME", "BTech", "MTech", "BCA", "MCA", "BSC", "MSC",
    # Indian document field labels — never organisations
    "AADHAAR", "IFSC", "UPI", "UAN", "ESIC", "GSTIN",
})

_SPACY_ORG_FALSE_POSITIVES: frozenset[str] = frozenset({
    "candidate", "profile", "reference", "internal", "contact",
    "education", "technical", "environment", "local", "remote",
    "full name", "primary", "secondary", "alternate", "residential",
    "permanent", "official", "personal", "masked", "redacted",
    "b.e", "m.tech", "b.tech", "bca", "mca", "internship",
    "project", "repository", "travel", "flight", "current", "focus",
    "university seat", "seat number",
    # Indian document field labels that spaCy wrongly tags as ORG
    "aadhaar", "pan", "gst", "gstin", "ifsc", "upi", "uan", "esic",
})

_STRUCTURAL_LABEL_RE = re.compile(
    r'^(?:\d+\.\s*)?'
    r'(?:full\s+)?'
    r'(?:name|email|phone|mobile|address|contact|alternate|primary|secondary|'
    r'occupation|education|candidate|profile|reference|technical|environment|'
    r'travel|internship|project|repository|current|focus|residential|'
    r'emergency|passport|visa|local|api|db|database)\b',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Pre-compiled regexes
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

# ---------------------------------------------------------------------------
# PHONE — full international coverage
#
# Branch order (first match wins via alternation):
#   1. India +91 explicit          → +91 98450 12345
#   2. India STD code              → 080-2345-6789
#   3. India bare 10-digit mobile  → 9845012345
#   4. US/Canada with/without +1   → (415) 555-1234 | +1 415 555 1234
#   5. Generic international       → +44 20 7946 0958 | +86 138 0013 8000
#
# Total digit length guard on branch 5 (7-15 E.164 digits after country code)
# prevents matching plain 6-digit numbers or version strings.
# ---------------------------------------------------------------------------
_PHONE_RE = re.compile(
    r'(?<!\d)'
    r'(?:'
    # Branch 1: India +91 with space/dash then 10 digits (possibly spaced)
    r'\+91[\s\-]?\d{5}[\s\-]?\d{5}'
    r'|'
    # Branch 2: India STD (0 + 2-4 digit area code + 6-8 digit number)
    r'0\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}'
    r'|'
    # Branch 3: Plain 10-digit Indian mobile (starts 6-9)
    r'[6-9]\d{9}'
    r'|'
    # Branch 4: US/Canada — optional +1 then (DDD) DDD-DDDD or DDD-DDD-DDDD
    r'(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}'
    r'|'
    # Branch 5: Generic international — +CC then digits/separators, 7-15 total digits
    # Negative lookahead excludes +1 and +91 (already handled above)
    r'\+(?!1[\s\-.(]|91[\s\-])'
    r'\d{1,3}'                              # country code 1-3 digits
    r'[\s\-.]?'
    r'(?:\(?\d{1,4}\)?[\s\-.]?)?'          # optional area code in parens
    r'\d{2,4}[\s\-.]?\d{2,4}'             # main number blocks
    r'(?:[\s\-.]?\d{2,4})?'               # optional trailing block
    r')'
    r'(?!\d)',
    re.ASCII,
)

# ---------------------------------------------------------------------------
# Credit card — Luhn-validated in the detector function below
# ---------------------------------------------------------------------------
_CARD_RE = re.compile(r'\b\d{4}[\ \-]?\d{4}[\ \-]?\d{4}[\ \-]?\d{4}\b')


def _luhn_check(number: str) -> bool:
    """Return True if the digit string passes the Luhn algorithm."""
    digits = [int(d) for d in number if d.isdigit()]
    if not (13 <= len(digits) <= 19):
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


# Aadhaar — exactly 12 digits in groups of 4
_AADHAAR_RE = re.compile(r'(?<!\d)\d{4}[\ \-]?\d{4}[\ \-]?\d{4}(?!\d)')

# Generic numeric ID — 9 to 15 digits (skips 12-digit Aadhaar and 16-digit card)
_ID_RE = re.compile(r'(?<!\d)\d{9,15}(?!\d)')

# ---------------------------------------------------------------------------
# ADDRESS — four-pattern global regex
#
# DAY 27 BUG FIXED: The suffix group previously ended every category line
# with a trailing pipe (r'...paseo|') making the alternation (?:...|paseo|)
# match an EMPTY STRING. This caused PAT2 to fire on any "words + space"
# sequence including "Rahul Sharma email ", "My name is Rajesh Kumar, ",
# and "App version ". All trailing pipes removed.
#
# Additional fixes:
#   PAT1 suffix made REQUIRED (was optional) — stops "1500 units, total" matching
#   PAT3 keyword list tightened — removed 'block','unit','apt','#' (too generic)
#   PAT4 added — street-type-FIRST languages (French rue, Italian via)
#   Removed from suffix: cross, main, block, phase, extension, pur, pada,
#     wala, flat, unit, floor, fl, place, pl, ter, close, park, way, ct,
#     st, dr, ln — all common English words causing false positives
# ---------------------------------------------------------------------------
_ADDRESS_SUFFIX_GLOBAL = (
    r'(?:'
    r'road|street|avenue|boulevard|crescent|terrace|expressway|freeway|highway|'
    r'drive|lane|court|plaza|grove|gardens|'
    r'rd|ave|blvd|cres|hwy|'
    r'apartment|building|apt|bldg|ste|'
    r'nagar|colony|sector|vihar|enclave|marg|chowk|bazaar|layout|puram|ganj|'
    r'wadi|katte|halli|palya|'
    r'strasse|allee|gasse|weg|platz|rue|impasse|'
    r'carrera|avenida|paseo'
    r')'
)

_ADDRESS_RE = re.compile(
    r'(?:'
    # PAT1: Number-first WITH mandatory suffix
    r'\b\d{1,5}[A-Za-z]?(?:[\-/]\d{1,4})?\s+[A-Za-z]{2,}(?:\s+[A-Za-z]{2,}){0,3}\s+' + _ADDRESS_SUFFIX_GLOBAL + r'\b'
    r'|'
    # PAT2: Suffix-first
    r'\b[A-Za-z]{2,}(?:\s+[A-Za-z]{2,}){0,4}\s+' + _ADDRESS_SUFFIX_GLOBAL + r'\b(?:\s+\d{1,5})?'
    r'|'
    # PAT3: Flat/Plot/House/Door/No. prefix
    r'\b(?:flat|plot|house|door|apartment|no\.?)\s*(?:\d{1,4}[A-Za-z]?|[A-Za-z]\d{1,4})'
    r'(?:[\s,]+[A-Za-z0-9]{1,}){1,8}'
    r'|'
    # PAT4: Street-type-FIRST languages
    r'\b(?:rue|via|calle)\s+[A-Za-z]{2,}(?:\s+[A-Za-z]{2,}){0,4}(?:\s*,\s*\d{1,5})?'
    r'|'
    # PAT5 (NEW): number + block/phase/stage (e.g. "Sector 21", "Phase 2", "Block A")
    # The keyword MUST be preceded by a digit to avoid false matches on plain "block".
    r'\b\d{1,4}[A-Za-z]?\s+(?:block|phase|stage)\b'
    r'(?:\s*[A-Za-z0-9]{1,}(?:[\s,]+[A-Za-z0-9]{1,}){0,4})?'
    r')',
    re.IGNORECASE,
)
# ---------------------------------------------------------------------------
# POSTCODE — global multi-country postcode detector
#
# Covers: India (6-digit), UK (SW1A 2AA), US ZIP (90210 / 90210-1234),
# Canada (M5V 3L9), Germany/France/Italy/Spain (5-digit), Brazil (01310-100),
# Japan (106-0032), South Korea / Singapore (via 5-6 digit branches).
#
# REMOVED: Netherlands (1234 AB) and Australia (4-digit (?<=[\s,])\d{4}) branches.
# Both caused false positives — the Netherlands 4+2 pattern fired on Aadhaar
# digit groups ('5678 90' → '5678' + 'AB'-lookalike), and the Australia 4-digit
# lookbehind fired on any space-separated 4-digit number including Aadhaar chunks,
# years, and amounts. Coverage loss is minimal vs false-positive elimination.
#
# Note: keeps the original PINCODE detector active for backward compatibility
# with existing placeholder labels. POSTCODE detector uses a new label.
# ---------------------------------------------------------------------------
_POSTCODE_RE = re.compile(
    r'(?<![A-Za-z\d])'
    r'(?:'
    # UK: A9 9AA | A99 9AA | AA9 9AA | AA99 9AA | A9A 9AA | AA9A 9AA
    r'[A-Z]{1,2}\d[A-Z\d]?[ ]?\d[A-Z]{2}'
    r'|'
    # Canada: A1A 1A1
    r'[A-Z]\d[A-Z][ ]?\d[A-Z]\d'
    r'|'
    # Brazil: 01310-100
    r'\d{5}-\d{3}'
    r'|'
    # Japan: 106-0032 (never starts with 0 — range 100-0001 to 999-9999)
    # Old: \d{3}-\d{4} — incorrectly fired on '012-3456' inside phone numbers
    r'[1-9]\d{2}-\d{4}'
    r'|'
    # US ZIP+4: 90210-1234
    r'\d{5}-\d{4}'
    r'|'
    # India 6-digit (starts 1-9), Singapore 6-digit
    r'[1-9]\d{5}'
    r'|'
    # US 5-digit ZIP / Germany / France / South Korea (generic 5-digit)
    r'\d{5}'
    r')'
    r'(?![A-Za-z\d])',
    re.IGNORECASE,
)

# India-only pincode kept for label backward compatibility
_PINCODE_RE = re.compile(r'\b[1-9]\d{5}\b')

# PAN card
_PAN_RE = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

# Indian Passport — FIX: original regex excluded Z; Indian passports use A-Z
# Old: [A-PR-WYa-pr-wy]  ← missed X and Z series
# New: [A-Z]             ← all uppercase letters, 7 digits
_PASSPORT_RE = re.compile(r'\b[A-Z][0-9]{7}\b')

# Indian Driving Licence
_DRIVING_LICENCE_RE = re.compile(
    r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?\d{4}[\s\-]?\d{7}\b',
    re.IGNORECASE,
)

# Indian Vehicle Registration
_VEHICLE_REG_RE = re.compile(
    r'\b[A-Z]{2}[\s\-]?\d{2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b',
    re.IGNORECASE,
)

# GST Number
_GST_RE = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b')

# IFSC Code
_IFSC_RE = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b')

# UPI ID
_UPI_RE = re.compile(
    r'\b[\w.\-+]+@(?:upi|paytm|gpay|phonepe|ybl|okaxis|okicici|okhdfcbank|'
    r'oksbi|apl|ibl|axl|aubank|barodampay|cnrb|csbpay|dbs|dlb|'
    r'equitas|fbl|federal|finobank|hdfcbank|icici|idbi|idfc|'
    r'indus|iob|jkb|jsb|karb|kbl|kotak|kvb|lvb|mahb|'
    r'niyobank|postbank|rbl|sbi|scb|tjsb|ubi|ucb|unionbank|'
    r'utib|vijb|yapl)\b',
    re.IGNORECASE,
)

# Date of Birth
_DOB_RE = re.compile(
    r'(?:'
    r'\b(?:0?[1-9]|[12]\d|3[01])[\/\-\.\ ](?:0?[1-9]|1[0-2])[\/\-\.\ ](?:19|20)\d{2}\b'
    r'|'
    r'\b(?:19|20)\d{2}[\/\-\.](?:0?[1-9]|1[0-2])[\/\-\.](?:0?[1-9]|[12]\d|3[01])\b'
    r'|'
    r'\b(?:0?[1-9]|[12]\d|3[01])[\s]+(?:january|february|march|april|may|june|'
    r'july|august|september|october|november|december)[\s,]+(?:19|20)\d{2}\b'
    r'|'
    r'\b(?:january|february|march|april|may|june|july|august|september|'
    r'october|november|december)[\s]+(?:0?[1-9]|[12]\d|3[01])[\s,]+(?:19|20)\d{2}\b'
    r')',
    re.IGNORECASE,
)

# IP address: IPv4
_IP_RE = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b'
)

# URLs with non-trivial paths
_URL_RE = re.compile(
    r'\bhttps?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]{10,}\b',
    re.IGNORECASE,
)

# Salary / financial figures
_SALARY_RE = re.compile(
    r'(?:'
    r'(?:₹|rs\.?|inr|usd|\$|£|€)[\s]?\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?'
    r'|'
    r'\d{1,3}(?:[,\s]\d{2,3})*(?:\.\d{1,2})?[\s]?(?:rupees?|lakh|lakhs|crore|crores|k|thousand)'
    r')',
    re.IGNORECASE,
)

# AWS Access Key
# Real AWS Access Key ID is always 20 chars: AKIA + 16 uppercase alphanumeric.
# Allow {16,20} to tolerate minor variations seen in example/test keys.
_AWS_KEY_RE = re.compile(r'\bAKIA[0-9A-Z]{16,20}\b')

# Generic API key / secret / token (context-based)
_API_KEY_RE = re.compile(
    r'(?i)(?:api[_\-]?key|secret[_\-]?key|access[_\-]?token|auth[_\-]?token'
    r'|bearer|private[_\-]?key)\s*[:=]\s*["\']?([A-Za-z0-9\-_.+/]{8,})["\']?'
)

# Password / credential (context-based)
_PASSWORD_RE = re.compile(
    r'(?i)(?:password|passwd|pwd|db_password|db_pass|secret_pass)\s*[:=]\s*["\']?(\S+)["\']?'
)

# Common names regex (sorted longest-first to prefer longer matches)
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

# All-caps orgs: 3-10 letters
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
            timeout=0.5,
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
    """Credit card detection with Luhn post-filter to eliminate false positives."""
    result = []
    for m in _CARD_RE.finditer(text):
        if _luhn_check(m.group()):
            result.append({"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()})
        else:
            logger.debug("Card-pattern match failed Luhn check, skipping: %s", m.group())
    return result


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
    """
    Global address detection using 3-pattern regex.
    Guards: length bounds from config, must contain at least one word of 3+ chars.
    MAX_ADDRESS_LENGTH raised to 200 in config to handle full international addresses.
    """
    min_len = getattr(Config.Detectors, "MIN_ADDRESS_LENGTH", 10)
    max_len = getattr(Config.Detectors, "MAX_ADDRESS_LENGTH", 200)
    result = []
    for m in _ADDRESS_RE.finditer(text):
        span = m.group()
        span_stripped = span.strip()
        if not (min_len < len(span_stripped) < max_len):
            continue
        # Must contain at least one alphabetic word of 3+ characters
        if not re.search(r'[A-Za-z]{3,}', span_stripped):
            continue
        result.append({
            "label": "ADDRESS",
            "text":  span_stripped,
            "start": m.start(),
            "end":   m.end(),
        })
    return result


def _detect_postcode(text: str) -> List[Dict[str, Any]]:
    """
    International postcode detector.
    Labels as POSTCODE (distinct from India-only PINCODE) so masker can
    use a separate placeholder if desired.
    """
    result = []
    for m in _POSTCODE_RE.finditer(text):
        raw = m.group().strip()
        # Skip standalone 4-5 digit numbers that are more likely IDs than postcodes
        # unless they look like a real ZIP (e.g. preceded by a state abbreviation or comma)
        if re.fullmatch(r'\d{4,5}', raw):
            before = text[max(0, m.start() - 5):m.start()]
            # Only accept bare 4-5 digit codes if preceded by a comma, space+2-letter abbrev, or newline
            if not re.search(r'(?:,\s*|[A-Z]{2}\s+)$', before):
                continue
        result.append({"label": "POSTCODE", "text": raw, "start": m.start(), "end": m.end()})
    return result


def _detect_pincode(text: str) -> List[Dict[str, Any]]:
    """India-only 6-digit pincode. Kept for label backward compatibility."""
    result = []
    for m in _PINCODE_RE.finditer(text):
        start, end = m.start(), m.end()
        before = text[start - 1] if start > 0 else ' '
        after  = text[end]       if end < len(text) else ' '
        if before.isdigit() or after.isdigit():
            continue
        result.append({"label": "PINCODE", "text": m.group(), "start": start, "end": end})
    return result


def _detect_pan(text: str) -> List[Dict[str, Any]]:
    return _spans("PAN", _PAN_RE, text)


def _detect_passport(text: str) -> List[Dict[str, Any]]:
    return _spans("PASSPORT", _PASSPORT_RE, text)


def _detect_driving_licence(text: str) -> List[Dict[str, Any]]:
    return _spans("DRIVING_LICENCE", _DRIVING_LICENCE_RE, text)


def _detect_vehicle_reg(text: str) -> List[Dict[str, Any]]:
    return _spans("VEHICLE_REG", _VEHICLE_REG_RE, text)


def _detect_gst(text: str) -> List[Dict[str, Any]]:
    return _spans("GST", _GST_RE, text)


def _detect_ifsc(text: str) -> List[Dict[str, Any]]:
    return _spans("IFSC", _IFSC_RE, text)


def _detect_upi(text: str) -> List[Dict[str, Any]]:
    return _spans("UPI", _UPI_RE, text)


def _detect_dob(text: str) -> List[Dict[str, Any]]:
    return _spans("DOB", _DOB_RE, text)


def _detect_ip(text: str) -> List[Dict[str, Any]]:
    return _spans("IP", _IP_RE, text)


def _detect_urls(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _URL_RE.finditer(text):
        url = m.group()
        if url.count('/') <= 2 and '?' not in url and '#' not in url:
            continue
        result.append({"label": "URL", "text": url, "start": m.start(), "end": m.end()})
    return result


def _detect_salary(text: str) -> List[Dict[str, Any]]:
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
        if token in _ALLCAPS_ORG_STOPWORDS:
            continue
        end = m.end()
        suffix = text[end:end + 2].strip()
        if suffix.startswith(':'):
            continue
        result.append({"label": "ORG", "text": token, "start": m.start(), "end": m.end()})
    return result


def _detect_aws_keys(text: str) -> List[Dict[str, Any]]:
    return _spans("API_KEY", _AWS_KEY_RE, text)


def _detect_api_keys(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _API_KEY_RE.finditer(text):
        result.append({"label": "API_KEY", "text": m.group(), "start": m.start(), "end": m.end()})
    return result


def _detect_passwords(text: str) -> List[Dict[str, Any]]:
    result = []
    for m in _PASSWORD_RE.finditer(text):
        result.append({"label": "PASSWORD", "text": m.group(), "start": m.start(), "end": m.end()})
    return result
# ---------------------------------------------------------------------------
# Transformer NER pipeline (fine‑tuned model)
# ---------------------------------------------------------------------------
_transformer_pipe = None

def _load_transformer_pipeline():
    """Load the fine‑tuned NER model once and cache it."""
    global _transformer_pipe
    if _transformer_pipe is None:
        model_dir = os.path.join(os.path.dirname(__file__), "..", "fine-tuned-ner-model")
        logger.info("Loading fine-tuned NER model from %s", model_dir)
        _transformer_pipe = pipeline(
            "token-classification",
            model=model_dir,
            tokenizer=model_dir,
            aggregation_strategy="simple",
            device=-1  # CPU
        )
        logger.info("NER model loaded.")
    return _transformer_pipe

def _detect_with_transformer(text: str) -> List[Dict[str, Any]]:
    """Run the fine‑tuned transformer and return entity spans."""
    try:
        pipe = _load_transformer_pipeline()
        results = pipe(text)
        entities = []
        for r in results:
            label = r["entity_group"]
            if label in ("O",):
                continue
            start = r["start"]
            end = r["end"]
            span_text = text[start:end]
            # Basic validation: EMAIL must contain '@'
            if label == "EMAIL" and "@" not in span_text:
                continue
            entities.append({
                "label": label,
                "text": span_text,
                "start": start,
                "end": end,
                "score": float(r["score"])
            })
        return entities
    except Exception:
        logger.exception("Transformer detection failed.")
        return []

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

                if label == "ORG":
                    ent_lower = ent.text.strip().lower()
                    if ent_lower in _SPACY_ORG_FALSE_POSITIVES:
                        logger.debug("spaCy ORG false-positive skipped: '%s'", ent.text)
                        continue
                    end_char = ent.end_char
                    suffix = text[end_char:end_char + 2].strip()
                    if suffix.startswith(':'):
                        logger.debug("spaCy ORG label (before colon) skipped: '%s'", ent.text)
                        continue

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
    d = Config.Detectors
    entities: List[Dict[str, Any]] = []
    try:
        # ── Highest confidence: credentials & keys ─────────────────────────
        if getattr(d, 'ENABLE_API_KEYS', True):
            entities.extend(_detect_aws_keys(text))
            entities.extend(_detect_api_keys(text))
        if getattr(d, 'ENABLE_PASSWORDS', True):
            entities.extend(_detect_passwords(text))
        # ── Core structured patterns ───────────────────────────────────────
        if d.ENABLE_EMAIL:           entities.extend(_detect_emails(text))
        if d.ENABLE_PHONE:           entities.extend(_detect_phones(text))
        if d.ENABLE_CARD:            entities.extend(_detect_cards(text))
        if d.ENABLE_AADHAAR:         entities.extend(_detect_aadhaar(text))
        # ── India-specific structured patterns ─────────────────────────────
        if d.ENABLE_PAN:             entities.extend(_detect_pan(text))
        if d.ENABLE_PASSPORT:        entities.extend(_detect_passport(text))
        if d.ENABLE_DRIVING_LICENCE: entities.extend(_detect_driving_licence(text))
        if d.ENABLE_GST:             entities.extend(_detect_gst(text))
        if d.ENABLE_IFSC:            entities.extend(_detect_ifsc(text))
        if d.ENABLE_UPI:             entities.extend(_detect_upi(text))
        if d.ENABLE_VEHICLE_REG:     entities.extend(_detect_vehicle_reg(text))
        if d.ENABLE_PINCODE:         entities.extend(_detect_pincode(text))
        if d.ENABLE_ID:              entities.extend(_detect_ids(text))
        # ── Global postcode (NEW) ──────────────────────────────────────────
        if getattr(d, 'ENABLE_POSTCODE', True):
            entities.extend(_detect_postcode(text))
        # ── Context-dependent patterns ─────────────────────────────────────
        if d.ENABLE_DOB:             entities.extend(_detect_dob(text))
        if d.ENABLE_IP:              entities.extend(_detect_ip(text))
        if d.ENABLE_URL:             entities.extend(_detect_urls(text))
        if d.ENABLE_SALARY:          entities.extend(_detect_salary(text))
        if d.ENABLE_ADDRESS:         entities.extend(_detect_addresses(text))
        # ── Name / location / org patterns (lower precision) ───────────────
        if d.ENABLE_COMMON_NAMES:    entities.extend(_detect_common_names(text))
        if d.ENABLE_INDIAN_CITIES:   entities.extend(_detect_indian_cities(text))
        if d.ENABLE_SINGLE_ORGS:     entities.extend(_detect_single_word_orgs(text))
        if d.ENABLE_MULTI_ORGS:      entities.extend(_detect_multi_word_orgs(text))
        if d.ENABLE_ALLCAPS_ORGS:    entities.extend(_detect_allcaps_orgs(text))
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
        
def _validate_entity(ent: Dict[str, Any], text: str) -> bool:
    """Reject clearly invalid detected entities."""
    label = ent["label"]
    # Strip _TRANS suffix for validation
    if label.endswith("_TRANS"):
        label = label[:-6]
    span = text[ent["start"]:ent["end"]]
    
    if label == "EMAIL" and "@" not in span:
        return False
    if label == "AADHAAR":
        digits = re.sub(r"\D", "", span)
        if len(digits) != 12:
            return False
    if label == "PAN" and not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", span, re.IGNORECASE):
        return False
    if label == "PHONE":
        digits = re.sub(r"\D", "", span)
        if len(digits) < 7:
            return False
    if label == "PERSON":
        # Reject if it's only a single character
        if len(span.strip()) <= 1:
            return False
        # Reject single-word names that are not in the known list OR are in the blacklist
        words = span.split()
        if len(words) == 1:
            low = span.lower()
            if low not in COMMON_NAMES or low in PERSON_FALSE_POSITIVES:
                return False
        # Reject all-caps short tokens that look like abbreviations (e.g. "US", "AI")
        if len(words) == 1 and span.isupper() and len(span) <= 3:
            return False
    return True

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
        logger.warning(
            "Input text (%d chars) exceeds MAX_TEXT_LENGTH (%d); truncating.",
            len(raw_text), max_len,
        )
        raw_text = raw_text[:max_len]

    raw_text = _sanitise(raw_text)
    if not raw_text.strip():
        return []

    presidio_spans = _detect_with_presidio(raw_text)
    spacy_spans    = detect_spacy_entities(raw_text)
    regex_spans    = detect_regex_entities(raw_text)
    transformer_spans = _detect_with_transformer(raw_text)

    # Rename structured transformer labels to avoid conflict with regex priority
    structured_labels = {
        "EMAIL", "PHONE", "AADHAAR", "PAN", "PASSPORT", "DRIVING_LICENCE",
        "GST", "IFSC", "UPI", "CARD", "VEHICLE_REG", "IP", "URL",
        "DOB", "SALARY", "ID", "API_KEY", "PASSWORD", "PINCODE", "POSTCODE"
    }
    for ent in transformer_spans:
        if ent["label"] in structured_labels:
            ent["label"] = ent["label"] + "_TRANS"

    all_spans = presidio_spans + spacy_spans + regex_spans + transformer_spans
    if not all_spans:
        return []

        all_spans = deduplicate_spans(all_spans)

    try:
        resolved = resolve_overlaps(all_spans)
    except ValueError:
        logger.exception("resolve_overlaps encountered invalid entities; returning deduplicated spans.")
        resolved = all_spans

    # Rename _TRANS labels back and validate
    final = []
    for ent in resolved:
        if ent["label"].endswith("_TRANS"):
            ent["label"] = ent["label"][:-6]
        if _validate_entity(ent, raw_text):
            final.append(ent)

    return final