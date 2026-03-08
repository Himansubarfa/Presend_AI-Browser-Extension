# from flask import Flask, jsonify

# # Initialize the Flask application
# app = Flask(__name__)

# # Create the /health route
# @app.route('/health', methods=['GET'])
# def health_check():
#     # Return the simple JSON response
#     return jsonify({"status": "running"})

# # Run the server on port 5000 when the script is executed
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)




# final code 1

# from flask import Flask, jsonify, request
# from backend.utils import process_text, ProcessingError
# import logging

# logging.basicConfig(level=logging.INFO)
# app = Flask(__name__)

# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "running"})

# @app.route('/mask', methods=['POST'])
# def mask_text_endpoint():
#     data = request.get_json()
#     if not data or 'text' not in data:
#         return jsonify({"error": "Missing 'text' field"}), 400

#     try:
#         result = process_text(data['text'])
#         return jsonify(result), 200
#     except ProcessingError as e:
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         logging.exception("Unexpected error")
#         return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)




# final code for production


# from flask import Flask, jsonify, request
# from backend.utils import process_text
# import logging

# logging.basicConfig(level=logging.INFO)
# app = Flask(__name__)


# @app.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({"status": "running"})


# @app.route('/mask', methods=['POST'])
# def mask_text_endpoint():
#     data = request.get_json()
#     if not data or 'text' not in data:
#         return jsonify({"error": "Missing 'text' field"}), 400

#     result = process_text(data['text'])

#     # If there was an error, you may decide to return 200 with error field, or 400.
#     # Here we return 200 with the error field included.
#     return jsonify(result), 200


# if __name__ == '__main__':
#     app.run(debug=True, port=5000)


# updated day 8 code 

# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from backend.utils import process_text
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)
# # Enable CORS for all routes (adjust origins in production)
# CORS(app)

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Simple health check endpoint."""
#     return jsonify({"status": "running"})

# @app.route('/scan', methods=['POST'])
# def scan_text():
#     """
#     Accepts JSON with a 'text' field, runs the PII masking pipeline,
#     and returns the masked text and detected entities.
#     """
#     # Ensure request has JSON content type
#     if not request.is_json:
#         return jsonify({
#             "masked": None,
#             "entities": [],
#             "status": "error",
#             "message": "Request must be JSON"
#         }), 400

#     data = request.get_json()
#     if data is None or 'text' not in data:
#         return jsonify({
#             "masked": None,
#             "entities": [],
#             "status": "error",
#             "message": "Missing 'text' field in JSON"
#         }), 400

#     input_text = data['text']
#     logger.info(f"Received text (length {len(input_text)})")

#     # Process the text using the unified pipeline
#     result = process_text(input_text)

#     # If the pipeline returned an error, return a 400 with status 'error'
#     if result.get("error"):
#         return jsonify({
#             "masked": result.get("masked", input_text),
#             "entities": result.get("entities", []),
#             "status": "error",
#             "message": result["error"]
#         }), 400

#     # Successful response
#     return jsonify({
#         "masked": result["masked"],
#         "entities": result["entities"],
#         "status": "ok"
#     }), 200

# # Optional: keep the old /mask endpoint for backward compatibility (not required)
# @app.route('/mask', methods=['POST'])
# def mask_text_legacy():
#     """Legacy endpoint  same as /scan."""
#     return scan_text()

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)



# day 9 updated code for robustness 

import logging
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman  # for security headers
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.config import Config
from backend.utils import process_text
from backend.errors import (
    APIError, InvalidJSONError, MissingTextFieldError,
    TextTooLongError, ProcessingError
)

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Security headers (CSP, HSTS, etc.)
    Talisman(app, content_security_policy=None)  # Customise CSP as needed

    # CORS – restrict to specific origins in production
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Fix for proxies (if behind nginx, etc.)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Register error handlers
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Unhandled exception")
        return jsonify({"message": "Internal server error"}), 500

    # Routes
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"})

    @app.route('/scan', methods=['POST'])
    def scan():
        # 1. Validate JSON content type
        if not request.is_json:
            raise InvalidJSONError()

        data = request.get_json(silent=True)
        if data is None:
            raise InvalidJSONError()

        # 2. Validate presence of 'text' field
        if 'text' not in data:
            raise MissingTextFieldError()

        text = data['text']
        if not isinstance(text, str):
            # Convert non-string to string (e.g., numbers)
            text = str(text)

        # 3. Enforce length limit
        if len(text) > app.config['MAX_TEXT_LENGTH']:
            raise TextTooLongError(app.config['MAX_TEXT_LENGTH'])

        # 4. Process text
        try:
            result = process_text(text)
        except Exception as e:
            logger.exception("Processing error")
            raise ProcessingError(str(e)) from e

        # 5. Check for internal error flag (from utils)
        if result.get("error"):
            # This indicates a recoverable error (e.g., detector failure)
            return jsonify({
                "masked": result.get("masked", text),
                "entities": result.get("entities", []),
                "status": "error",
                "message": result["error"]
            }), 422  # Unprocessable Entity

        # 6. Success response
        return jsonify({
            "masked": result["masked"],
            "entities": result["entities"],
            "status": "ok"
        }), 200
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
     print(f"  {rule.endpoint}: {rule}")
    
    return app