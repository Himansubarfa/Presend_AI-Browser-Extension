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

from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.utils import process_text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes (adjust origins in production)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "running"})

@app.route('/scan', methods=['POST'])
def scan_text():
    """
    Accepts JSON with a 'text' field, runs the PII masking pipeline,
    and returns the masked text and detected entities.
    """
    # Ensure request has JSON content type
    if not request.is_json:
        return jsonify({
            "masked": None,
            "entities": [],
            "status": "error",
            "message": "Request must be JSON"
        }), 400

    data = request.get_json()
    if data is None or 'text' not in data:
        return jsonify({
            "masked": None,
            "entities": [],
            "status": "error",
            "message": "Missing 'text' field in JSON"
        }), 400

    input_text = data['text']
    logger.info(f"Received text (length {len(input_text)})")

    # Process the text using the unified pipeline
    result = process_text(input_text)

    # If the pipeline returned an error, return a 400 with status 'error'
    if result.get("error"):
        return jsonify({
            "masked": result.get("masked", input_text),
            "entities": result.get("entities", []),
            "status": "error",
            "message": result["error"]
        }), 400

    # Successful response
    return jsonify({
        "masked": result["masked"],
        "entities": result["entities"],
        "status": "ok"
    }), 200

# Optional: keep the old /mask endpoint for backward compatibility (not required)
@app.route('/mask', methods=['POST'])
def mask_text_legacy():
    """Legacy endpoint  same as /scan."""
    return scan_text()

if __name__ == '__main__':
    app.run(debug=True, port=5000)