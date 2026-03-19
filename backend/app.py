
# day 21 update 
import logging
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman
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

    # Security headers
    Talisman(app, content_security_policy=None)

    # CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Proxy fix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Error handlers
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

        # 5. Check for internal error flag
        if result.get("error"):
            return jsonify({
                "masked": result.get("masked", text),
                "entities": result.get("entities", []),
                "status": "error",
                "message": result["error"]
            }), 422

        # 6. Success response
        return jsonify({
            "masked": result["masked"],
            "entities": result["entities"],
            "status": "ok"
        }), 200

    # Print routes for debugging (moved before return)
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule}")

    return app