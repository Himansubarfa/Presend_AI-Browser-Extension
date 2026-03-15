# config.py
MAX_TEXT_LENGTH = 200000




# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load variables from .env file

# class Config:
#     # Flask
#     DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
#     PORT = int(os.getenv('PORT', 5000))

#     # Text limits
#     MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 10000))

#     # Security
#     CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
#     # Add more security settings as needed

#     # Logging
#     LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')



# day 21 update 

# import os
# from dotenv import load_dotenv

# load_dotenv()  # Load variables from .env file

# class Config:
#     # Flask
#     DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
#     PORT = int(os.getenv('PORT', 5000))

#     # Text limits
#     MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 200000))

#     # Security
#     CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

#     # Logging
#     LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

#     # Presidio service URL (if used)
#     PRESIDIO_ANALYZER_URL = None
#     # os.getenv('PRESIDIO_ANALYZER_URL', 'http://localhost:5002/analyze')

# day 25 update 
"""
config.py – Central configuration for PreSendAI backend.

All values can be overridden via environment variables or a .env file.
load_dotenv() is called here so this module can be imported anywhere safely.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Flask ──────────────────────────────────────────────────────────────────
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT  = int(os.getenv('PORT', 5000))

    # ── Text limits ────────────────────────────────────────────────────────────
    # Keep in sync with MAX_TEXT_LENGTH in content.js (currently 20000)
    # and the fallback in detector.py (100_000).
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 20000))

    # ── Security ───────────────────────────────────────────────────────────────
    # For local dev '*' is fine.  In production set to your extension origin,
    # e.g. CORS_ORIGINS=chrome-extension://abcdef1234567890
    # Flask-CORS accepts a list; ['*'] is equivalent to '*'.
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # ── Presidio (optional) ────────────────────────────────────────────────────
    # Set PRESIDIO_ANALYZER_URL=http://localhost:5002/analyze to enable.
    # Leave unset (None) to skip Presidio entirely.
    PRESIDIO_ANALYZER_URL = os.getenv('PRESIDIO_ANALYZER_URL') or None

    # ── Detector feature flags ─────────────────────────────────────────────────
    # Each flag can be toggled via its env var (true/false, case-insensitive).
    # Example .env line:  ENABLE_URL=false
    #
    # Implemented as a plain inner class so attributes are read at import time
    # from the already-loaded environment.  Do NOT add mutable state here.

    class Detectors:
        # ── Core ──────────────────────────────────────────────────────────────
        ENABLE_EMAIL        = os.getenv('ENABLE_EMAIL',        'true').lower() == 'true'
        ENABLE_PHONE        = os.getenv('ENABLE_PHONE',        'true').lower() == 'true'
        ENABLE_CARD         = os.getenv('ENABLE_CARD',         'true').lower() == 'true'
        ENABLE_AADHAAR      = os.getenv('ENABLE_AADHAAR',      'true').lower() == 'true'
        ENABLE_ID           = os.getenv('ENABLE_ID',           'true').lower() == 'true'
        ENABLE_ADDRESS      = os.getenv('ENABLE_ADDRESS',      'true').lower() == 'true'
        ENABLE_COMMON_NAMES = os.getenv('ENABLE_COMMON_NAMES', 'true').lower() == 'true'
        ENABLE_SINGLE_ORGS  = os.getenv('ENABLE_SINGLE_ORGS',  'true').lower() == 'true'
        ENABLE_MULTI_ORGS   = os.getenv('ENABLE_MULTI_ORGS',   'true').lower() == 'true'
        ENABLE_ALLCAPS_ORGS = os.getenv('ENABLE_ALLCAPS_ORGS', 'true').lower() == 'true'

        # ── India-specific ────────────────────────────────────────────────────
        ENABLE_PAN              = os.getenv('ENABLE_PAN',              'true').lower() == 'true'
        ENABLE_PASSPORT         = os.getenv('ENABLE_PASSPORT',         'true').lower() == 'true'
        ENABLE_DRIVING_LICENCE  = os.getenv('ENABLE_DRIVING_LICENCE',  'true').lower() == 'true'
        ENABLE_PINCODE          = os.getenv('ENABLE_PINCODE',          'true').lower() == 'true'
        ENABLE_VEHICLE_REG      = os.getenv('ENABLE_VEHICLE_REG',      'true').lower() == 'true'
        ENABLE_GST              = os.getenv('ENABLE_GST',              'true').lower() == 'true'
        ENABLE_IFSC             = os.getenv('ENABLE_IFSC',             'true').lower() == 'true'
        ENABLE_UPI              = os.getenv('ENABLE_UPI',              'true').lower() == 'true'
        ENABLE_INDIAN_CITIES    = os.getenv('ENABLE_INDIAN_CITIES',    'true').lower() == 'true'

        # ── General ───────────────────────────────────────────────────────────
        ENABLE_DOB    = os.getenv('ENABLE_DOB',    'true').lower() == 'true'
        ENABLE_IP     = os.getenv('ENABLE_IP',     'true').lower() == 'true'
        ENABLE_URL    = os.getenv('ENABLE_URL',    'true').lower() == 'true'
        ENABLE_SALARY = os.getenv('ENABLE_SALARY', 'true').lower() == 'true'

        # ── Address length bounds (used by _detect_addresses) ─────────────────
        MIN_ADDRESS_LENGTH = int(os.getenv('MIN_ADDRESS_LENGTH', 10))
        MAX_ADDRESS_LENGTH = int(os.getenv('MAX_ADDRESS_LENGTH', 100))  