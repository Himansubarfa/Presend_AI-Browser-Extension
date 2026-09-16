[PreSendAI-README.md](https://github.com/user-attachments/files/32296090/PreSendAI-README.md)
# 🛡️ PreSendAI – Privacy Masking for AI Prompts

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green)](https://flask.palletsprojects.com/)
[![spaCy](https://img.shields.io/badge/spaCy-en__core__web__sm-09A3D5)](https://spacy.io/)
[![Presidio](https://img.shields.io/badge/Presidio-PII%20detection-orange)](https://microsoft.github.io/presidio/)
[![Manifest V3](https://img.shields.io/badge/Manifest-V3-purple)](https://developer.chrome.com/docs/extensions/mv3/)

**PreSendAI** is a browser extension backed by a Flask + spaCy + Presidio service that detects and masks personally identifiable information (PII) in real time — before it reaches an AI model, chatbot, or any third‑party website.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [How It Works](#-how-it-works)
- [Supported PII Types](#-supported-pii-types)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Extension Setup](#extension-setup)
- [Configuration](#️-configuration)
- [API Reference](#-api-reference)
- [Detection Logic](#-detection-logic)
- [Performance](#-performance)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Security & Privacy](#-security--privacy)
- [Roadmap](#-roadmap)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 🔍 Overview

Every time you paste a prompt into an AI model, you may be leaking sensitive information — full names, email addresses, phone numbers, credit cards, Aadhaar numbers, addresses, and more. **PreSendAI** intercepts that text *before* it is submitted and replaces the sensitive parts with safe placeholders.

Unlike naive masking tools that rewrite the entire input, PreSendAI uses **span‑based DOM replacement**, so:
- Formatting is preserved in rich editors (ProseMirror, Quill).
- Cursor position and user intent are not disrupted.
- Only the exact PII spans are replaced.

The result is a lightweight, transparent privacy layer that works on **ChatGPT, Google Gemini, Google Search, and any standard HTML input or textarea**.

---

## ✨ Key Features

| Feature | Description |
|--------|-------------|
| **Real‑time detection** | Masks PII as you type, using debounced input handling (~300 ms). |
| **Cross‑browser support** | Chrome, Edge, Brave, and any Chromium‑based browser (Manifest V3). |
| **Rich editor compatibility** | Handles ProseMirror (ChatGPT), Quill (Gemini), and plain `<input>` / `<textarea>`. |
| **Span‑based masking** | Replaces only sensitive spans — no whole‑field rewriting. |
| **Multiple detection engines** | spaCy NER + regex patterns + optional Microsoft Presidio. |
| **Toggle on/off** | Quick enable/disable via the extension popup. |
| **Configurable backend** | Environment‑driven config for limits, CORS, logging, and Presidio URL. |
| **Structured error handling** | Custom API errors with clear HTTP status codes and messages. |
| **Performance optimised** | Debouncing, client‑side length checks, and efficient DOM walks. |
| **Privacy‑first design** | No user data is logged or stored beyond the request lifetime. |

---

## 🏗️ Architecture

```

┌──────────────────────────┐ HTTP POST /scan ┌──────────────────────────┐
│ Browser Extension │ ──────────────────────────────► │ Flask Backend │
│ │ │ │
│ ┌────────────────────┐ │ │ ┌────────────────────┐ │
│ │ content.js │ │ │ │ app.py │ │
│ │ background.js │ │ ◄────────────────────────────── │ │ utils.py │ │
│ │ popup.html/js │ │ JSON response │ │ detector.py │ │
│ └────────────────────┘ │ │ │ masker.py │ │
│ │ │ │ config.py │ │
└──────────────────────────┘ │ │ errors.py │ │
│ └────────────────────┘ │
│ │ │
│ ▼ │
│ ┌────────────────────┐ │
│ │ spaCy + Presidio │ │
│ │ (PII detection) │ │
│ └────────────────────┘ │
└──────────────────────────┘

```
---

## ⚙️ How It Works

1. **User types or pastes text** into a supported field (input, textarea, or contenteditable).
2. **content.js** listens for `input` events with a debounce delay (~300 ms).
3. The text is sent to the backend via `background.js` using `runtime.sendMessage` (falls back to direct `fetch` if needed).
4. The **Flask backend** runs the detection pipeline:
   - **Presidio** (optional) for high‑precision detection.
   - **spaCy NER** for PERSON and ORG entities.
   - **Regex patterns** for emails, phones, cards, Aadhaar, IDs, addresses, orgs, and fallback names.
5. Overlapping entities are **deduplicated and resolved** using a priority map.
6. The backend returns `{ masked, entities, status }`.
7. **content.js** replaces only the detected spans in the DOM using a tree walker — preserving surrounding text and editor state.
8. A short highlight flashes to indicate which parts were masked.

---

## 🔐 Supported PII Types

| Label | Placeholder | Detection Method |
|-------|-------------|------------------|
| `PERSON` | `[NAME]` | spaCy NER, common‑names list, capitalised‑name fallback |
| `EMAIL` | `[EMAIL]` | Regex |
| `PHONE` | `[PHONE]` | Regex (international, US, Indian formats) |
| `CARD` | `[CARD]` | Regex (16‑digit card patterns) |
| `AADHAAR` | `[AADHAAR]` | Regex (12‑digit Indian Aadhaar) |
| `ID` | `[ID]` | Regex (9+ digit identifiers) |
| `ADDRESS` | `[ADDRESS]` | Regex (number + street + suffix) |
| `ORG` | `[ORG]` | spaCy NER, curated org lists, ALLCAPS fallback |

---

## 🧩 Project Structure

```

PreSendAI/
├── backend/
│ ├── **init**.py
│ ├── app.py # Flask application factory & routes
│ ├── config.py # Environment-driven configuration
│ ├── detector.py # spaCy + regex + Presidio detection pipeline
│ ├── errors.py # Custom API error classes
│ ├── masker.py # Span-based masking logic
│ └── utils.py # End-to-end processing orchestrator
│
├── extension/
│ ├── background.js # Service worker (message relay + keep-alive)
│ ├── content.js # DOM listener, debounce, span replacement
│ ├── manifest.json # Manifest V3 configuration
│ ├── popup.html # Extension popup UI
│ └── popup.js # Popup toggle logic
│
├── tests/
│ ├── test\_detector.py
│ ├── test\_masker.py
│ └── test\_api.py
│
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md

````
---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **pip** and **venv**
- A Chromium‑based browser (Chrome, Edge, Brave)
- Internet connection (only for the initial spaCy model download)

### Backend Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/PreSendAI.git
   cd PreSendAI
````

2. **Create and activate a virtual environment**

   bash
   ```
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   bash
   ```
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Create the** **`.env`** **file**

   Copy `.env.example` to `.env` and adjust as needed:

   env
   ```
   FLASK_DEBUG=True
   PORT=5000
   MAX_TEXT_LENGTH=200000
   CORS_ORIGINS=*
   LOG_LEVEL=INFO
   # PRESIDIO_ANALYZER_URL=http://localhost:5002/analyze
   ```

5. **Run the backend**

   bash
   ```
   python app.py
   ```

   The API should now be available at `http://localhost:5000`.
6. **Verify the backend**

   bash
   ```
   curl http://localhost:5000/health
   # → {"status": "healthy"}
   ```

### Extension Setup

1. Open `chrome://extensions` (or `edge://extensions`, `brave://extensions`).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `extension/` folder.
4. Pin the PreSendAI icon to your toolbar.

### Quick Test

1. Navigate to `https://chat.openai.com` or `https://gemini.google.com`.
2. Paste the following text into the prompt box:

   ```
   Hi, my name is John Doe and my email is john.doe@example.com.
   You can call me at +1 555 987 6543.
   ```

3. Within \~150 ms, the text should become:

   ```
   Hi, my name is [NAME] and my email is [EMAIL].
   You can call me at [PHONE].
   ```

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `FLASK_DEBUG` | Enable Flask debug mode | `False` |
| `PORT` | Backend port | `5000` |
| `MAX_TEXT_LENGTH` | Maximum text length | `200000` |
| `CORS_ORIGINS` | Allowed origins | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `PRESIDIO_ANALYZER_URL` | Optional Presidio analyzer endpoint | `None` |

---

## 📡 API Reference

### `GET /health`

Returns the service health status.

**Response**

json

```
{
  "status": "healthy"
}
```

---

### `POST /scan`

Masks PII in the supplied text.

**Headers**

```
Content-Type: application/json
```

**Request Body**

json

```
{
  "text": "Hi, my name is John Doe and my email is john.doe@example.com."
}
```

**Success Response (200)**

json

```
{
  "masked": "Hi, my name is [NAME] and my email is [EMAIL].",
  "entities": [
    { "label": "PERSON", "text": "John Doe", "start": 15, "end": 23 },
    { "label": "EMAIL", "text": "john.doe@example.com", "start": 41, "end": 61 }
  ],
  "status": "ok"
}
```

**Error Responses**

| Status | Cause | Example |
|---:|---|---|
| `400` | Missing or invalid JSON | `{"message": "Missing 'text' field in JSON"}` |
| `413` | Text exceeds maximum length | `{"message": "Text exceeds maximum length"}` |
| `422` | Processing error | `{"masked": "...", "entities": [], "status": "error"}` |
| `500` | Internal error | `{"message": "Internal server error"}` |

---

## 🧠 Detection Logic

The pipeline is intentionally layered — each layer covers gaps in the others:

1. **Presidio** *(optional)* – High‑precision detection for standard PII types when a Presidio analyzer is available.
2. **spaCy NER** – Extracts `PERSON` and `ORG` entities from natural language.
3. **Regex detectors** – Deterministic matches for emails, phones, cards, Aadhaar, IDs, and addresses.
4. **Curated lists** – Common first names, surnames, single‑word orgs, and multi‑word orgs.
5. **Heuristic fallbacks** – ALLCAPS tokens → `ORG`; `Firstname Lastname` patterns → `PERSON`.

### Overlap Resolution

When two entities overlap, the winner is chosen by:

1. **Longer span wins.**
2. On equal length, **higher priority wins** (`EMAIL > PHONE > ADDRESS > AADHAAR = CARD = ID > ORG = PERSON`).

This prevents double‑masking and keeps replacements consistent.

---

## 🧪 Testing

### Backend

bash

```
pytest tests/
```

### Manual API Test

bash

```
curl -X POST http://localhost:5000/scan \
  -H "Content-Type: application/json" \
  -d '{"text":"John Doe, john@example.com, +1 555 123 4567"}'
```

### Extension Test Cases

| Case | Expected Behaviour |
|---|---|
| Plain `<input>` with an email | Email replaced with `[EMAIL]` |
| `<textarea>` with a phone number | Phone replaced with `[PHONE]` |
| ChatGPT ProseMirror editor | Only PII spans replaced |
| Gemini Quill editor | Only PII spans replaced |
| Text over the configured limit | Skipped with a warning |
| Text with no PII | Returned unchanged |

---

## 🛠️ Troubleshooting

### Masking does not happen on a specific site

- Open DevTools → **Console** and look for `🔒 PreSendAI` logs.
- Ensure the field is in the tracked selectors list in `content.js`.
- Some editors (e.g., Monaco, CodeMirror) use virtualised DOMs — they may need a custom adapter.

### `Cannot read properties of undefined (reading 'entities')`

- The backend returned an empty or malformed response. Check DevTools → **Network** → the `/scan` request → **Response** tab.
- Verify the Flask server is running and reachable at `http://localhost:5000`.

### `ERR_BLOCKED_BY_CLIENT` or CORS errors

- The `CORS_ORIGINS` value in `.env` must include the site origin, or use `*` during development.
- The extension calls `http://localhost:5000`, not `https`. Using `https` on a local Flask server will fail.

### Masking only happens after deleting characters

- This is almost always a **length limit mismatch** between `content.js` (`MAX_TEXT_LENGTH`) and the backend (`MAX_TEXT_LENGTH`). Set them to the same value.

### `net::ERR_BLOCKED_BY_CLIENT` on `play.google.com`

- This is a Google Analytics beacon blocked by your ad blocker — it is unrelated to PreSendAI. Ignore it.

---

## 🔒 Security & Privacy

- **No persistence** – The backend does not store submitted text. It processes each request in memory and discards it.
- **No external calls** – Unless you explicitly set `PRESIDIO_ANALYZER_URL`, the backend never calls an external service.
- **Local‑only by default** – The backend binds to `localhost` and is intended to run on the user's machine.
- **CORS is configurable** – For production, restrict `CORS_ORIGINS` to known origins.
- **Talisman headers** – CSP, HSTS, and other security headers are applied via `flask-talisman`.

> ⚠️ PreSendAI is a **best‑effort** privacy tool. No PII detector is 100% accurate. Always review masked output before sending it to any external service.

---

## 🗺️ Roadmap

- □ 

  Manifest V3 service worker hardening (idle timeouts, reconnect logic)
- □ 

  In‑browser inference (e.g., ONNX‑based spaCy) to remove the backend dependency
- □ 

  Support for Firefox (WebExtensions API differences)
- □ 

  Custom user‑defined patterns (e.g., internal IDs, employee codes)
- □ 

  Settings page with granular PII category toggles
- □ 

  Localisation (i18n) for non‑English names and formats
- □ 

  Optional audit log (opt‑in, encrypted, local‑only)

---

## ❓ FAQ

**Q: Is my data sent anywhere?**
No. The backend runs locally and returns the masked text directly to your browser. Nothing is stored or forwarded.

**Q: Does it work on Firefox?**
Not yet. The current build targets Chromium‑based browsers (Manifest V3). Firefox support is on the roadmap.

**Q: Why does it need** **`<all_urls>`** **permission?**
Because PII can be entered on any site. You can narrow this by editing `manifest.json` `matches` to specific domains.

**Q: Can I use my own Presidio instance?**
Yes. Set `PRESIDIO_ANALYZER_URL` in `.env` to point to your analyzer endpoint.

**Q: What happens if the backend is offline?**
The extension logs an error and leaves the field untouched — it never blocks your typing.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Write tests where applicable.
4. Commit with clear messages: `git commit -m "feat: add ..."`.
5. Push and open a Pull Request.

Please read `CONTRIBUTING.md` for detailed guidelines.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](https://license/) file for details.

---

## 🙏 Acknowledgements

- [spaCy](https://spacy.io/) — industrial‑strength NLP
- [Microsoft Presidio](https://microsoft.github.io/presidio/) — PII detection framework
- [Flask](https://flask.palletsprojects.com/) — backend framework
- [Flask‑CORS](https://flask-cors.readthedocs.io/) and [Flask‑Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) — CORS and security headers

---

## 📬 Contact

For questions, feedback, or security disclosures:

- Open an issue on GitHub
- Or reach out to the maintainer directly

**Stay private. Stay safe.** 🛡️

```
