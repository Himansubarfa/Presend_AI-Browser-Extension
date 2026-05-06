# import logging
# import sys
# import base64
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

# from backend.detector import detect_entities
# from backend.ocr.image_processor import ocr_bboxes, redact_image, detect_faces
# from backend.document.pdf_processor import extract_text_from_pdf, redact_pdf
# from backend.document.docx_processor import extract_text_from_docx, redact_docx

# logging.basicConfig(
#     level=getattr(logging, Config.LOG_LEVEL),
#     format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
#     handlers=[logging.StreamHandler(sys.stdout)]
# )
# logger = logging.getLogger(__name__)

# # ---------------------------------------------------------------------------
# # Sensitive PII labels – only these will be redacted
# # ---------------------------------------------------------------------------
# SENSITIVE_LABELS = {
#     "PERSON", "EMAIL", "PHONE", "AADHAAR", "PAN", "PASSPORT",
#     "DRIVING_LICENCE", "DOB", "ADDRESS", "CARD", "GST", "IFSC",
#     "UPI", "VEHICLE_REG", "SALARY", "ID", "API_KEY", "PASSWORD"
# }

# def _is_garbled(text: str, threshold: float = 0.3) -> bool:
#     """Heuristic to detect OCR junk."""
#     if not text.strip():
#         return True
#     alpha = sum(c.isalpha() for c in text)
#     return (alpha / max(len(text), 1)) < threshold

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     Talisman(app, content_security_policy=None)
#     CORS(app, origins=app.config['CORS_ORIGINS'])
#     app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

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

#     @app.route('/health', methods=['GET'])
#     def health():
#         return jsonify({"status": "healthy"})

#     # --------------------------- TEXT ------------------------------------
#     @app.route('/scan', methods=['POST'])
#     def scan():
#         if not request.is_json:
#             raise InvalidJSONError()

#         data = request.get_json(silent=True)
#         if data is None:
#             raise InvalidJSONError()

#         if 'text' not in data:
#             raise MissingTextFieldError()

#         text = data['text']
#         if not isinstance(text, str):
#             text = str(text)

#         if len(text) > app.config['MAX_TEXT_LENGTH']:
#             raise TextTooLongError(app.config['MAX_TEXT_LENGTH'])

#         try:
#             result = process_text(text)
#         except Exception as e:
#             logger.exception("Processing error")
#             raise ProcessingError(str(e)) from e

#         if result.get("error"):
#             return jsonify({
#                 "masked": result.get("masked", text),
#                 "entities": result.get("entities", []),
#                 "status": "error",
#                 "message": result["error"]
#             }), 422

#         return jsonify({
#             "masked": result["masked"],
#             "entities": result["entities"],
#             "status": "ok"
#         }), 200

#     # --------------------------- IMAGE ----------------------------------
#     @app.route('/scan/image', methods=['POST'])
#     def scan_image():
#         if 'image' not in request.files:
#             return jsonify({"error": "No image file provided. Use form-data key 'image'."}), 400

#         file = request.files['image']
#         if file.filename == '':
#             return jsonify({"error": "Empty filename."}), 400

#         try:
#             image_bytes = file.read()
#         except Exception as e:
#             logger.exception("Failed to read image file")
#             return jsonify({"error": f"Failed to read image file: {str(e)}"}), 400

#         logger.info("Image received: %s (%d bytes)", file.filename, len(image_bytes))

#         # OCR with fallback if preprocessing produces garbage
#         try:
#             ocr_result = ocr_bboxes(image_bytes, preprocess=True)
#             if _is_garbled(ocr_result["full_text"]):
#                 logger.info("Preprocessed OCR appears garbled, retrying without preprocessing")
#                 ocr_result = ocr_bboxes(image_bytes, preprocess=False)
#         except MemoryError:
#             return jsonify({"error": "Image too large (out of memory)."}), 413
#         except Exception as e:
#             logger.exception("OCR failed")
#             return jsonify({"error": f"OCR error: {str(e)}"}), 422

#         full_text = ocr_result["full_text"]
#         words = ocr_result["words"]
#         logger.info("OCR extracted %d words", len(words))

#         if not full_text.strip():
#             return jsonify({"status": "ok", "redacted_image_base64": None,
#                             "entities": [], "message": "No text found in image."}), 200

#         # PII detection – only sensitive labels
#         try:
#             entities = detect_entities(full_text)
#             entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
#         except Exception as e:
#             logger.exception("PII detection failed")
#             return jsonify({"error": f"Detection error: {str(e)}"}), 422

#         logger.info("Detected %d sensitive entities", len(entities))

#         # Map entities to OCR word bounding boxes (word-overlap)
#         redaction_boxes = []
#         for ent in entities:
#             ent_start, ent_end = ent["start"], ent["end"]
#             for w in words:
#                 idx = full_text.find(w["text"])
#                 if idx == -1:
#                     continue
#                 word_end = idx + len(w["text"])
#                 if idx < ent_end and word_end > ent_start:
#                     redaction_boxes.append({"bbox": w["bbox"]})

#         # Face detection
#         try:
#             face_boxes = detect_faces(image_bytes)
#             redaction_boxes.extend(face_boxes)
#             logger.info("Detected %d faces", len(face_boxes))
#         except Exception as e:
#             logger.warning("Face detection skipped: %s", e)

#         # Redact and encode
#         try:
#             redacted_bytes = redact_image(image_bytes, redaction_boxes)
#         except Exception as e:
#             logger.exception("Redaction failed")
#             return jsonify({"error": f"Redaction error: {str(e)}"}), 422

#         b64 = base64.b64encode(redacted_bytes).decode('utf-8')
#         return jsonify({
#             "status": "ok",
#             "redacted_image_base64": b64,
#             "entities": entities,
#             "full_text": full_text            # useful for debugging
#         }), 200

#     # --------------------------- DOCUMENT --------------------------------
#     ALLOWED_EXTENSIONS = {'pdf', 'docx'}

#     @app.route('/scan/document', methods=['POST'])
#     def scan_document():
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided. Use form-data key 'file'."}), 400

#         file = request.files['file']
#         filename = file.filename or ''
#         if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
#             return jsonify({"error": "Invalid or missing file. Only PDF and DOCX files are allowed."}), 400

#         try:
#             file_bytes = file.read()
#         except Exception:
#             return jsonify({"error": "Failed to read file."}), 400

#         ext = filename.rsplit('.', 1)[1].lower()

#         if ext == 'pdf':
#             try:
#                 doc_data = extract_text_from_pdf(file_bytes)
#             except Exception as e:
#                 logger.exception("PDF extraction failed")
#                 return jsonify({"error": f"PDF extraction error: {str(e)}"}), 422

#             words = doc_data["words"]
#             full_text = doc_data["full_text"]

#             if not full_text.strip():
#                 logger.info("No embedded text, forcing OCR on PDF")
#                 try:
#                     doc_data = extract_text_from_pdf(file_bytes, force_ocr=True)
#                     words = doc_data["words"]
#                     full_text = doc_data["full_text"]
#                 except Exception as e:
#                     logger.exception("OCR fallback failed")
#                     return jsonify({"error": f"OCR fallback error: {str(e)}"}), 422

#             entities = detect_entities(full_text)
#             entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
#             logger.info("Detected %d sensitive entities in PDF", len(entities))

#             # Word‑overlap mapping
#             redactions = []
#             for ent in entities:
#                 ent_start, ent_end = ent["start"], ent["end"]
#                 for w in words:
#                     word_text = w["text"]
#                     idx = full_text.find(word_text)
#                     if idx == -1:
#                         continue
#                     word_end = idx + len(word_text)
#                     if idx < ent_end and word_end > ent_start:
#                         redactions.append({
#                             "page": w["page"],
#                             "bbox": w["bbox"]
#                         })

#             try:
#                 redacted_bytes = redact_pdf(file_bytes, redactions)
#                 if redacted_bytes[:4] != b'%PDF':
#                     raise ValueError("Invalid PDF output")
#             except Exception as e:
#                 logger.exception("PDF redaction failed")
#                 return jsonify({"error": f"PDF redaction error: {str(e)}"}), 422

#         else:  # docx
#             try:
#                 doc_data = extract_text_from_docx(file_bytes)
#             except Exception as e:
#                 logger.exception("DOCX extraction failed")
#                 return jsonify({"error": f"DOCX extraction error: {str(e)}"}), 422

#             full_text = doc_data["full_text"]
#             para_info = doc_data["paragraphs"]
#             doc_object = doc_data["doc_object"]

#             entities = detect_entities(full_text)
#             entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
#             logger.info("Detected %d sensitive entities in DOCX", len(entities))

#             # In‑place run redaction
#             char_offset = 0
#             for para in para_info:
#                 para_text = para["text"]
#                 for ent in entities:
#                     ent_start = ent["start"]
#                     ent_end = ent["end"]
#                     if ent_start >= char_offset and ent_end <= char_offset + len(para_text):
#                         local_start = ent_start - char_offset
#                         local_end = ent_end - char_offset
#                         for run_info in para["runs"]:
#                             r_start = run_info["start"]
#                             r_end = run_info["end"]
#                             if r_end > local_start and r_start < local_end:
#                                 run = run_info["run_obj"]
#                                 text_chars = list(run.text)
#                                 overlap_start = max(r_start, local_start) - r_start
#                                 overlap_end = min(r_end, local_end) - r_start
#                                 for j in range(overlap_start, overlap_end):
#                                     if j < len(text_chars):
#                                         text_chars[j] = '\u2588'
#                                 run.text = ''.join(text_chars)
#                 char_offset += len(para_text) + 1

#             try:
#                 redacted_bytes = redact_docx(doc_object)
#             except Exception as e:
#                 logger.exception("DOCX redaction failed")
#                 return jsonify({"error": f"DOCX redaction error: {str(e)}"}), 422

#         b64 = base64.b64encode(redacted_bytes).decode('utf-8')
#         return jsonify({
#             "status": "ok",
#             "redacted_file_base64": b64,
#             "entities": entities,
#             "original_filename": filename,
#             "redacted_filename": "redacted_" + filename
#         }), 200

#     print("Registered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"  {rule.endpoint}: {rule.rule}")

#     return app



# day 28 update – now with image & document masking, dashboard, and source tracking
import logging
import sys
import base64
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.config import Config
from backend.utils import process_text
from backend.errors import (
    APIError, InvalidJSONError, MissingTextFieldError,
    TextTooLongError, ProcessingError
)

from backend.detector import detect_entities
from backend.ocr.image_processor import ocr_bboxes, redact_image, detect_faces
from backend.document.pdf_processor import extract_text_from_pdf, redact_pdf
from backend.document.docx_processor import extract_text_from_docx, redact_docx

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sensitive PII labels – only these will be redacted
# ---------------------------------------------------------------------------
SENSITIVE_LABELS = {
    "PERSON", "EMAIL", "PHONE", "AADHAAR", "PAN", "PASSPORT",
    "DRIVING_LICENCE", "DOB", "ADDRESS", "CARD", "GST", "IFSC",
    "UPI", "VEHICLE_REG", "SALARY", "ID", "API_KEY", "PASSWORD"
}

# ---------------------------------------------------------------------------
# Live masking statistics (in‑memory – resets on restart)
# ---------------------------------------------------------------------------
STATS = {
    "text":     {"requests": 0, "entities": 0, "labels": {}, "sources": {}},
    "image":    {"requests": 0, "entities": 0, "labels": {}, "sources": {}},
    "document": {"requests": 0, "entities": 0, "labels": {}, "sources": {}}
}

def _record_stats(mode: str, entities: list, source: str = "unknown"):
    """Update global STATS after a successful mask operation."""
    if mode not in STATS:
        return
    STATS[mode]["requests"] += 1
    STATS[mode]["entities"] += len(entities)
    for ent in entities:
        label = ent["label"]
        STATS[mode]["labels"][label] = STATS[mode]["labels"].get(label, 0) + 1
    STATS[mode]["sources"][source] = STATS[mode]["sources"].get(source, 0) + 1

def _is_garbled(text: str, threshold: float = 0.3) -> bool:
    """Heuristic to detect OCR junk."""
    if not text.strip():
        return True
    alpha = sum(c.isalpha() for c in text)
    return (alpha / max(len(text), 1)) < threshold

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
    # Stats API (for dashboard)
    # ------------------------------------------------------------------
    @app.route('/stats')
    def stats():
        return jsonify(STATS)

    # ------------------------------------------------------------------
    # Dashboard page (live masking stats)
    # ------------------------------------------------------------------
    @app.route('/dashboard')
    def dashboard():
        return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PreSendAI – Live Masking Stats</title>
  <style>
    body {
      font-family: "Segoe UI", sans-serif;
      margin: 40px;
      background: #f5f7fa;
      color: #333;
    }
    h1 {
      color: #2c3e50;
      border-bottom: 3px solid #2980b9;
      padding-bottom: 10px;
    }
    .cards {
      display: flex;
      gap: 20px;
      margin: 20px 0;
      flex-wrap: wrap;
    }
    .card {
      background: white;
      border-radius: 12px;
      padding: 20px;
      flex: 1;
      min-width: 260px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: 0.2s;
    }
    .card:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .card h3 {
      margin: 0 0 10px;
      color: #2980b9;
    }
    .number {
      font-size: 1.8em;
      font-weight: bold;
      color: #2c3e50;
    }
    .subtitle {
      font-size: 0.9em;
      color: #7f8c8d;
      margin: 5px 0 10px;
    }
    .list-section {
      margin-top: 15px;
    }
    .list-title {
      font-weight: 600;
      margin-bottom: 5px;
      color: #555;
    }
    .item {
      display: flex;
      justify-content: space-between;
      border-bottom: 1px solid #ecf0f1;
      padding: 4px 0;
      font-size: 14px;
    }
    .item span:last-child {
      font-weight: bold;
      color: #e67e22;
    }
    .refresh {
      margin: 20px 0;
      font-size: 14px;
      color: #888;
    }
  </style>
</head>
<body>
  <h1>🛡️ PreSendAI – Real‑time Masking Dashboard</h1>
  <div class="cards" id="cards">
    <div class="card">
      <h3>📝 Text Masks</h3>
      <div class="number" id="textReq">0 requests</div>
      <div class="subtitle" id="textEntities">0 entities</div>
      <div class="list-section">
        <div class="list-title">Top PII Types</div>
        <div id="textLabels"></div>
      </div>
      <div class="list-section">
        <div class="list-title">Websites</div>
        <div id="textSources"></div>
      </div>
    </div>
    <div class="card">
      <h3>🖼️ Image Masks</h3>
      <div class="number" id="imgReq">0 requests</div>
      <div class="subtitle" id="imgEntities">0 entities</div>
      <div class="list-section">
        <div class="list-title">Top PII Types</div>
        <div id="imgLabels"></div>
      </div>
      <div class="list-section">
        <div class="list-title">Sources</div>
        <div id="imgSources"></div>
      </div>
    </div>
    <div class="card">
      <h3>📄 Document Masks</h3>
      <div class="number" id="docReq">0 requests</div>
      <div class="subtitle" id="docEntities">0 entities</div>
      <div class="list-section">
        <div class="list-title">Top PII Types</div>
        <div id="docLabels"></div>
      </div>
      <div class="list-section">
        <div class="list-title">Sources</div>
        <div id="docSources"></div>
      </div>
    </div>
  </div>
  <div class="refresh">Auto‑refreshes every 3 seconds</div>

  <script>
    function renderList(containerId, data) {
      const container = document.getElementById(containerId);
      if (!data || Object.keys(data).length === 0) {
        container.innerHTML = '<div class="item"><span>None yet</span></div>';
        return;
      }
      let html = '';
      for (const [key, value] of Object.entries(data).sort((a,b) => b[1] - a[1])) {
        html += `<div class="item"><span>${key}</span><span>${value}</span></div>`;
      }
      container.innerHTML = html;
    }

    async function fetchStats() {
      try {
        const res = await fetch('/stats');
        const data = await res.json();

        // Text card
        document.getElementById('textReq').textContent = data.text.requests + ' requests';
        document.getElementById('textEntities').textContent = data.text.entities + ' entities';
        renderList('textLabels', data.text.labels);
        renderList('textSources', data.text.sources || {});

        // Image card
        document.getElementById('imgReq').textContent = data.image.requests + ' requests';
        document.getElementById('imgEntities').textContent = data.image.entities + ' entities';
        renderList('imgLabels', data.image.labels);
        renderList('imgSources', data.image.sources || {});

        // Document card
        document.getElementById('docReq').textContent = data.document.requests + ' requests';
        document.getElementById('docEntities').textContent = data.document.entities + ' entities';
        renderList('docLabels', data.document.labels);
        renderList('docSources', data.document.sources || {});
      } catch (err) {
        console.error(err);
      }
    }

    fetchStats();
    setInterval(fetchStats, 3000);
  </script>
</body>
</html>'''
    # ------------------------------------------------------------------
    # Demo page (side‑by‑side original vs redacted)
    # ------------------------------------------------------------------
    @app.route('/demo')
    def demo_page():
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>PreSendAI – Live Redaction Demo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f5f7fa; color: #333; }
    h2 { color: #2c3e50; border-bottom: 3px solid #2980b9; padding-bottom: 10px; }
    .drop-zone { border: 3px dashed #aaa; border-radius: 12px; padding: 50px; text-align: center; background: #fff; cursor: pointer; margin: 30px 0; transition: 0.2s; }
    .drop-zone:hover { border-color: #2980b9; background: #eef2ff; }
    .result { display: flex; gap: 30px; flex-wrap: wrap; }
    .card { flex: 1; min-width: 280px; background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .card h3 { margin-top: 0; color: #2980b9; }
    img, iframe { max-width: 100%; border: 1px solid #ddd; border-radius: 6px; }
    .entities { margin-top: 20px; font-size: 14px; color: #555; }
    .entity-item { display: inline-block; background: #e3f2fd; color: #1565c0; padding: 2px 8px; border-radius: 4px; margin: 3px; font-size: 13px; }
    .status { color: #888; margin: 10px 0; }
  </style>
</head>
<body>
  <h2>🛡️ PreSendAI – Live PII Redaction Demo</h2>
  <p>Select a PDF, DOCX, or image file. Sensitive information will be automatically detected and redacted.</p>

  <div class="drop-zone" id="dropZone">
    <p><strong>Click or drag a file here</strong><br><small>Supports: PDF, DOCX, JPG, PNG</small></p>
    <input type="file" id="fileInput" accept=".pdf,.docx,.jpg,.jpeg,.png" style="display:none">
  </div>

  <div class="status" id="status"></div>
  <div class="result" id="result" style="display:none">
    <div class="card">
      <h3>Original</h3>
      <div id="originalPreview"></div>
    </div>
    <div class="card">
      <h3>Redacted</h3>
      <div id="redactedPreview"></div>
    </div>
  </div>
  <div class="entities" id="entities"></div>

  <script>
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const status = document.getElementById('status');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.style.background = '#eef2ff'; });
    dropZone.addEventListener('dragleave', () => dropZone.style.background = '#fff');
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.background = '#fff';
      const files = e.dataTransfer.files;
      if (files.length) handleFile(files[0]);
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    async function handleFile(file) {
      status.textContent = 'Processing...';
      const form = new FormData();
      const isImage = file.type.startsWith('image/');
      form.append(isImage ? 'image' : 'file', file);

      const endpoint = isImage ? '/scan/image' : '/scan/document';

      try {
        const res = await fetch(endpoint, { method: 'POST', body: form });
        const data = await res.json();

        if (data.status !== 'ok') {
          status.textContent = 'Redaction failed: ' + (data.error || 'unknown');
          return;
        }

        const b64 = data.redacted_image_base64 || data.redacted_file_base64;
        if (!b64) {
          status.textContent = 'No redacted data returned.';
          return;
        }

        document.getElementById('result').style.display = 'flex';
        displayOriginal(file);
        displayRedacted(b64, file.type || (file.name.endsWith('.pdf') ? 'application/pdf' : 'image/png'), file.name);

        const entDiv = document.getElementById('entities');
        if (data.entities.length) {
          entDiv.innerHTML = '<h3>Detected PII (' + data.entities.length + ' items):</h3>' +
            data.entities.map(e => `<span class="entity-item">${e.label}: ${e.text}</span>`).join('');
        } else {
          entDiv.innerHTML = '';
        }
        status.textContent = 'Redaction complete.';
      } catch (err) {
        status.textContent = 'Error: ' + err.message;
        console.error(err);
      }
    }

    function displayOriginal(file) {
      const div = document.getElementById('originalPreview');
      if (file.type.startsWith('image/')) {
        div.innerHTML = `<img src="${URL.createObjectURL(file)}" alt="original">`;
      } else if (file.type === 'application/pdf') {
        div.innerHTML = `<iframe src="${URL.createObjectURL(file)}" width="100%" height="400"></iframe>`;
      } else {
        div.innerHTML = `<p>${file.name} (${file.type})</p>`;
      }
    }

    function displayRedacted(b64, mimeType, originalName) {
      const div = document.getElementById('redactedPreview');
      const blob = b64toBlob(b64, mimeType);
      const url = URL.createObjectURL(blob);
      if (mimeType.startsWith('image/')) {
        div.innerHTML = `<img src="${url}" alt="redacted">`;
      } else if (mimeType === 'application/pdf') {
        div.innerHTML = `<iframe src="${url}" width="100%" height="400"></iframe>`;
      } else {
        div.innerHTML = `<a href="${url}" download="redacted_${originalName}">Download redacted file</a>`;
      }
    }

    function b64toBlob(b64, mime) {
      const byteChars = atob(b64);
      const byteArrays = [];
      for (let offset = 0; offset < byteChars.length; offset += 512) {
        const slice = byteChars.slice(offset, offset + 512);
        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
          byteNumbers[i] = slice.charCodeAt(i);
        }
        byteArrays.push(new Uint8Array(byteNumbers));
      }
      return new Blob(byteArrays, { type: mime });
    }
  </script>
</body>
</html>'''

    # ------------------------------------------------------------------
    # Text‑only scan
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

        source = data.get("source", "unknown") if data else "unknown"

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

        entities = result.get("entities", [])
        _record_stats("text", entities, source)

        return jsonify({
            "masked": result["masked"],
            "entities": entities,
            "status": "ok"
        }), 200

    # ------------------------------------------------------------------
    # IMAGE scan
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
        except Exception as e:
            logger.exception("Failed to read image file")
            return jsonify({"error": f"Failed to read image file: {str(e)}"}), 400

        logger.info("Image received: %s (%d bytes)", file.filename, len(image_bytes))

        # OCR with fallback
        try:
            ocr_result = ocr_bboxes(image_bytes, preprocess=True)
            if _is_garbled(ocr_result["full_text"]):
                logger.info("Preprocessed OCR appears garbled, retrying without preprocessing")
                ocr_result = ocr_bboxes(image_bytes, preprocess=False)
        except MemoryError:
            return jsonify({"error": "Image too large (out of memory)."}), 413
        except Exception as e:
            logger.exception("OCR failed")
            return jsonify({"error": f"OCR error: {str(e)}"}), 422

        full_text = ocr_result["full_text"]
        words = ocr_result["words"]
        logger.info("OCR extracted %d words", len(words))

        if not full_text.strip():
            return jsonify({"status": "ok", "redacted_image_base64": None,
                            "entities": [], "message": "No text found in image."}), 200

        # PII detection – only sensitive labels
        try:
            entities = detect_entities(full_text)
            entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
        except Exception as e:
            logger.exception("PII detection failed")
            return jsonify({"error": f"Detection error: {str(e)}"}), 422

        logger.info("Detected %d sensitive entities", len(entities))

        source = request.form.get("source", "Demo Page")
        _record_stats("image", entities, source)

        # Map entities to OCR word bounding boxes (word-overlap)
        redaction_boxes = []
        for ent in entities:
            ent_start, ent_end = ent["start"], ent["end"]
            for w in words:
                idx = full_text.find(w["text"])
                if idx == -1:
                    continue
                word_end = idx + len(w["text"])
                if idx < ent_end and word_end > ent_start:
                    redaction_boxes.append({"bbox": w["bbox"]})

        # Face detection
        try:
            face_boxes = detect_faces(image_bytes)
            redaction_boxes.extend(face_boxes)
            logger.info("Detected %d faces", len(face_boxes))
        except Exception as e:
            logger.warning("Face detection skipped: %s", e)

        # Redact and encode
        try:
            redacted_bytes = redact_image(image_bytes, redaction_boxes)
        except Exception as e:
            logger.exception("Redaction failed")
            return jsonify({"error": f"Redaction error: {str(e)}"}), 422

        b64 = base64.b64encode(redacted_bytes).decode('utf-8')
        return jsonify({
            "status": "ok",
            "redacted_image_base64": b64,
            "entities": entities,
            "full_text": full_text
        }), 200

    # ------------------------------------------------------------------
    # DOCUMENT scan – PDF/DOCX
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
        source = request.form.get("source", "Demo Page")

        if ext == 'pdf':
            try:
                doc_data = extract_text_from_pdf(file_bytes)
            except Exception as e:
                logger.exception("PDF extraction failed")
                return jsonify({"error": f"PDF extraction error: {str(e)}"}), 422

            words = doc_data["words"]
            full_text = doc_data["full_text"]

            if not full_text.strip():
                logger.info("No embedded text, forcing OCR on PDF")
                try:
                    doc_data = extract_text_from_pdf(file_bytes, force_ocr=True)
                    words = doc_data["words"]
                    full_text = doc_data["full_text"]
                except Exception as e:
                    logger.exception("OCR fallback failed")
                    return jsonify({"error": f"OCR fallback error: {str(e)}"}), 422

            entities = detect_entities(full_text)
            entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
            logger.info("Detected %d sensitive entities in PDF", len(entities))
            _record_stats("document", entities, source)

            # Word‑overlap mapping
            redactions = []
            for ent in entities:
                ent_start, ent_end = ent["start"], ent["end"]
                for w in words:
                    word_text = w["text"]
                    idx = full_text.find(word_text)
                    if idx == -1:
                        continue
                    word_end = idx + len(word_text)
                    if idx < ent_end and word_end > ent_start:
                        redactions.append({
                            "page": w["page"],
                            "bbox": w["bbox"]
                        })

            try:
                redacted_bytes = redact_pdf(file_bytes, redactions)
                if redacted_bytes[:4] != b'%PDF':
                    raise ValueError("Invalid PDF output")
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

            entities = detect_entities(full_text)
            entities = [e for e in entities if e["label"] in SENSITIVE_LABELS]
            logger.info("Detected %d sensitive entities in DOCX", len(entities))
            _record_stats("document", entities, source)

            # In‑place run redaction
            char_offset = 0
            for para in para_info:
                para_text = para["text"]
                for ent in entities:
                    ent_start = ent["start"]
                    ent_end = ent["end"]
                    if ent_start >= char_offset and ent_end <= char_offset + len(para_text):
                        local_start = ent_start - char_offset
                        local_end = ent_end - char_offset
                        for run_info in para["runs"]:
                            r_start = run_info["start"]
                            r_end = run_info["end"]
                            if r_end > local_start and r_start < local_end:
                                run = run_info["run_obj"]
                                text_chars = list(run.text)
                                overlap_start = max(r_start, local_start) - r_start
                                overlap_end = min(r_end, local_end) - r_start
                                for j in range(overlap_start, overlap_end):
                                    if j < len(text_chars):
                                        text_chars[j] = '\u2588'
                                run.text = ''.join(text_chars)
                char_offset += len(para_text) + 1

            try:
                redacted_bytes = redact_docx(doc_object)
            except Exception as e:
                logger.exception("DOCX redaction failed")
                return jsonify({"error": f"DOCX redaction error: {str(e)}"}), 422

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