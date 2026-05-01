
# # day 21 update 
# import logging
# import sys
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_talisman import Talisman
# from werkzeug.middleware.proxy_fix import ProxyFix

# from backend.config import Config
# from backend.utils import process_text
# from backend.errors import (
#     APIError, InvalidJSONError, MissingTextFieldError,
#     TextTooLongError, ProcessingError
# )

# # Configure structured logging
# logging.basicConfig(
#     level=getattr(logging, Config.LOG_LEVEL),
#     format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger(__name__)

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Security headers
#     Talisman(app, content_security_policy=None)

#     # CORS
#     CORS(app, origins=app.config['CORS_ORIGINS'])

#     # Proxy fix
#     app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

#     # Error handlers
#     @app.errorhandler(APIError)
#     def handle_api_error(error):
#         response = jsonify(error.to_dict())
#         response.status_code = error.status_code
#         return response

#     @app.errorhandler(404)
#     def not_found(error):
#         return jsonify({"message": "Endpoint not found"}), 404

#     @app.errorhandler(500)
#     def internal_error(error):
#         logger.exception("Unhandled exception")
#         return jsonify({"message": "Internal server error"}), 500

#     # Routes
#     @app.route('/health', methods=['GET'])
#     def health():
#         return jsonify({"status": "healthy"})

#     @app.route('/scan', methods=['POST'])
#     def scan():
#         # 1. Validate JSON content type
#         if not request.is_json:
#             raise InvalidJSONError()

#         data = request.get_json(silent=True)
#         if data is None:
#             raise InvalidJSONError()

#         # 2. Validate presence of 'text' field
#         if 'text' not in data:
#             raise MissingTextFieldError()

#         text = data['text']
#         if not isinstance(text, str):
#             text = str(text)

#         # 3. Enforce length limit
#         if len(text) > app.config['MAX_TEXT_LENGTH']:
#             raise TextTooLongError(app.config['MAX_TEXT_LENGTH'])

#         # 4. Process text
#         try:
#             result = process_text(text)
#         except Exception as e:
#             logger.exception("Processing error")
#             raise ProcessingError(str(e)) from e

#         # 5. Check for internal error flag
#         if result.get("error"):
#             return jsonify({
#                 "masked": result.get("masked", text),
#                 "entities": result.get("entities", []),
#                 "status": "error",
#                 "message": result["error"]
#             }), 422

#         # 6. Success response
#         return jsonify({
#             "masked": result["masked"],
#             "entities": result["entities"],
#             "status": "ok"
#         }), 200

#     # Print routes for debugging (moved before return)
#     print("Registered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"  {rule.endpoint}: {rule}")

#     return app


# new as per 26/04/2026
# day 28 update – now with image & document masking
import logging
import sys
import base64
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

# New imports for image/document processing
from backend.detector import detect_entities
from backend.ocr.image_processor import ocr_bboxes, redact_image
from backend.document.pdf_processor import extract_text_from_pdf, redact_pdf
from backend.document.docx_processor import extract_text_from_docx, redact_docx

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

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy"})

    # ------------------------------------------------------------------
    # Text‑only scan (unchanged)
    # ------------------------------------------------------------------
    @app.route('/scan', methods=['POST'])
    def scan():
        if not request.is_json:
            raise InvalidJSONError()

        data = request.get_json(silent=True)
        if data is None:
            raise InvalidJSONError()

        if 'text' not in data:
            raise MissingTextFieldError()

        text = data['text']
        if not isinstance(text, str):
            text = str(text)

        if len(text) > app.config['MAX_TEXT_LENGTH']:
            raise TextTooLongError(app.config['MAX_TEXT_LENGTH'])

        try:
            result = process_text(text)
        except Exception as e:
            logger.exception("Processing error")
            raise ProcessingError(str(e)) from e

        if result.get("error"):
            return jsonify({
                "masked": result.get("masked", text),
                "entities": result.get("entities", []),
                "status": "error",
                "message": result["error"]
            }), 422

        return jsonify({
            "masked": result["masked"],
            "entities": result["entities"],
            "status": "ok"
        }), 200

    # ------------------------------------------------------------------
    # IMAGE scan – accept JPEG/PNG, return redacted image as base64
    # ------------------------------------------------------------------
    @app.route('/scan/image', methods=['POST'])
    def scan_image():
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided. Use form-data key 'image'."}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        try:
            image_bytes = file.read()
        except Exception:
            return jsonify({"error": "Failed to read image file."}), 400

        # 1. OCR
        try:
            ocr_result = ocr_bboxes(image_bytes)
        except Exception as e:
            logger.exception("OCR failed")
            return jsonify({"error": f"OCR error: {str(e)}"}), 422

        full_text = ocr_result["full_text"]
        words = ocr_result["words"]

        # 2. Run PII detection on the extracted text
        entities = detect_entities(full_text)

        # 3. Map character offsets → image bounding boxes
        bbox_at_char = [None] * len(full_text)
        search_pos = 0
        for w in words:
            word_text = w["text"]
            # find next occurrence (handles punctuation better)
            idx = full_text.find(word_text, search_pos)
            if idx != -1:
                for i in range(idx, idx + len(word_text)):
                    bbox_at_char[i] = w["bbox"]
                search_pos = idx + len(word_text)

        # 4. For each entity, collect unique bounding boxes to redact
        redaction_boxes = []
        for ent in entities:
            start, end = ent["start"], ent["end"]
            boxes = set()
            for i in range(start, end):
                bbox = bbox_at_char[i]
                if bbox is not None:
                    boxes.add(tuple(bbox))
            for b in boxes:
                redaction_boxes.append({"bbox": list(b)})

        # 5. Redact the image
        try:
            redacted_bytes = redact_image(image_bytes, redaction_boxes)
        except Exception as e:
            logger.exception("Redaction failed")
            return jsonify({"error": f"Redaction error: {str(e)}"}), 422

        # 6. Return base64-encoded JPEG
        b64 = base64.b64encode(redacted_bytes).decode('utf-8')
        return jsonify({
            "status": "ok",
            "redacted_image_base64": b64,
            "entities": entities
        }), 200

    # ------------------------------------------------------------------
    # DOCUMENT scan – accept PDF/DOCX, return redacted file as base64
    # ------------------------------------------------------------------
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}

    @app.route('/scan/document', methods=['POST'])
    def scan_document():
        if 'file' not in request.files:
            return jsonify({"error": "No file provided. Use form-data key 'file'."}), 400

        file = request.files['file']
        filename = file.filename or ''
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "Invalid or missing file. Only PDF and DOCX files are allowed."}), 400

        try:
            file_bytes = file.read()
        except Exception:
            return jsonify({"error": "Failed to read file."}), 400

        ext = filename.rsplit('.', 1)[1].lower()

        if ext == 'pdf':
            try:
                doc_data = extract_text_from_pdf(file_bytes)
            except Exception as e:
                logger.exception("PDF extraction failed")
                return jsonify({"error": f"PDF extraction error: {str(e)}"}), 422

            words = doc_data["words"]
            full_text = doc_data["full_text"]

            # PII detection
            entities = detect_entities(full_text)

            # Map entities to page & bounding boxes
            bbox_at_char = [None] * len(full_text)
            search_pos = 0
            for w in words:
                word_text = w["text"]
                idx = full_text.find(word_text, search_pos)
                if idx != -1:
                    for i in range(idx, idx + len(word_text)):
                        # store bbox + page number
                        bbox_at_char[i] = (w["bbox"], w["page"])
                    search_pos = idx + len(word_text)

            redactions = []
            for ent in entities:
                start, end = ent["start"], ent["end"]
                boxes = set()
                for i in range(start, end):
                    info = bbox_at_char[i]
                    if info:
                        bbox, page = info
                        boxes.add((page, tuple(bbox)))
                for page, bbox in boxes:
                    redactions.append({"page": page, "bbox": list(bbox)})

            try:
                redacted_bytes = redact_pdf(file_bytes, redactions)
            except Exception as e:
                logger.exception("PDF redaction failed")
                return jsonify({"error": f"PDF redaction error: {str(e)}"}), 422

        else:  # docx
            try:
                doc_data = extract_text_from_docx(file_bytes)
            except Exception as e:
                logger.exception("DOCX extraction failed")
                return jsonify({"error": f"DOCX extraction error: {str(e)}"}), 422

            full_text = doc_data["full_text"]
            para_info = doc_data["paragraphs"]
            doc_object = doc_data["doc_object"]

            # PII detection
            entities = detect_entities(full_text)

            # -----------------------------------------------
            # DOCX redaction: replace PII text in runs
            # -----------------------------------------------
            char_offset = 0
            for para in para_info:
                para_text = para["text"]
                # for each entity, check if it falls within this paragraph
                for ent in entities:
                    ent_start = ent["start"]
                    ent_end = ent["end"]
                    if ent_start >= char_offset and ent_end <= char_offset + len(para_text):
                        local_start = ent_start - char_offset
                        local_end = ent_end - char_offset
                        # replace characters in runs that overlap
                        for run_info in para["runs"]:
                            r_start = run_info["start"]
                            r_end = run_info["end"]
                            if r_end > local_start and r_start < local_end:
                                run = run_info["run_obj"]
                                run_text = run.text
                                new_chars = list(run_text)
                                overlap_start = max(r_start, local_start) - r_start
                                overlap_end = min(r_end, local_end) - r_start
                                for j in range(overlap_start, overlap_end):
                                    if j < len(new_chars):
                                        new_chars[j] = '\u2588'  # full block character
                                run.text = ''.join(new_chars)
                char_offset += len(para_text) + 1  # +1 for the newline we joined with

            try:
                redacted_bytes = redact_docx(doc_object)
            except Exception as e:
                logger.exception("DOCX redaction failed")
                return jsonify({"error": f"DOCX redaction error: {str(e)}"}), 422

        # Return as downloadable base64 string
        b64 = base64.b64encode(redacted_bytes).decode('utf-8')
        return jsonify({
            "status": "ok",
            "redacted_file_base64": b64,
            "entities": entities,
            "original_filename": filename,
            "redacted_filename": "redacted_" + filename
        }), 200

    # Print routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")

    return app