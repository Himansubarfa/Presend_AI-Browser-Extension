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


from flask import Flask, jsonify, request
from backend.utils import process_text
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running"})


@app.route('/mask', methods=['POST'])
def mask_text_endpoint():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    result = process_text(data['text'])

    # If there was an error, you may decide to return 200 with error field, or 400.
    # Here we return 200 with the error field included.
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)