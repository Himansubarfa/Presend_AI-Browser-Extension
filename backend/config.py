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
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Config:
    # Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))

    # Text limits
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', 200000))

    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Presidio service URL (if used)
    PRESIDIO_ANALYZER_URL = None
    # os.getenv('PRESIDIO_ANALYZER_URL', 'http://localhost:5002/analyze')