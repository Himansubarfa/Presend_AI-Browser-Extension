// final update for day 27

// ==================== CROSS-BROWSER POLYFILL ====================
// Normalise to a single `browserAPI` variable that works on:
//   Chrome / Edge / Opera  → chrome.* APIs
//   Firefox                → browser.* APIs (already Promise-based)
//   Any other context      → null (extension APIs unavailable)
const browserAPI = (() => {
    if (typeof chrome !== 'undefined' && chrome.runtime) return chrome;
    if (typeof browser !== 'undefined' && browser.runtime) return browser;
    return null;
})();

const runtime = browserAPI ? browserAPI.runtime : null;
if (!runtime) console.warn("⚠️ No extension runtime API found.");

// ==================== CONFIGURATION ====================
// Single source of truth for ALL constants shared across modules.
// dom.js, highlight.js, and api.js read these as globals — do NOT
// re-declare any of these in those files.
const BACKEND_URL           = "https://localhost:5000/scan";
const HEALTH_URL            = "https://localhost:5000/health";
const DEBOUNCE_DELAY        = 300;
const OBSERVER_DEBOUNCE     = 300;
const HIGHLIGHT_DURATION    = 600;   // FIXED: Match highlight.js (was 300)
const MESSAGE_TIMEOUT       = 10000;
const MAX_TEXT_LENGTH       = 20000;
const HEALTH_CHECK_INTERVAL = 30000;
const HEALTH_CHECK_TIMEOUT  = 2000;

const MASK_PLACEHOLDERS = [
    // Core
    "[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]",
    // India-specific
    "[PAN]", "[PASSPORT]", "[DRIVING_LICENCE]", "[PINCODE]", "[VEHICLE_REG]",
    "[GST]", "[IFSC]", "[UPI]",
    // General
    "[DOB]", "[IP]", "[URL]", "[SALARY]", "[LOCATION]",
    "[REDACTED]"
];

// ==================== SHARED STATE ====================
// Intentional globals – dom.js (attachListener) reads trackedFields.
let extensionEnabled  = true;
const trackedFields   = new WeakSet();
const lastSentText    = new WeakMap();
const isProcessing    = new WeakMap();
const pendingTimeouts = new WeakMap();

// ==================== ENABLED STATE FROM STORAGE ====================
if (browserAPI) {
    // browserAPI.storage works on both Chrome (chrome.storage) and Firefox (browser.storage)
    browserAPI.storage.local.get('enabled', (data) => {
        extensionEnabled = data.enabled !== false;
        console.log(`Extension enabled: ${extensionEnabled}`);
    });
    browserAPI.storage.onChanged.addListener((changes, area) => {
        if (area === 'local' && changes.enabled) {
            extensionEnabled = changes.enabled.newValue !== false;
            console.log(`Extension enabled changed to: ${extensionEnabled}`);
        }
    });
}

// ==================== KEEP-ALIVE ====================
if (runtime) {
    try {
        const port = runtime.connect({ name: "presendai-keepalive" });
        port.onMessage.addListener((msg) => { if (msg.type === "ping") { /* alive */ } });
    } catch (e) {
        console.warn("⚠️ Could not establish keep-alive port:", e);
    }
    // Use runtime.lastError (not hardcoded chrome.runtime) – Firefox compatible
    setInterval(() => {
        try {
            runtime.sendMessage({ action: "ping" }, () => { void runtime.lastError; });
        } catch (_) { /* context invalidated – ignore */ }
    }, 20000);
}

// ==================== HELPERS ====================
function isAlreadyMasked(text) {
    return MASK_PLACEHOLDERS.some(p => text.includes(p));
}

function debounce(fn, wait) {
    let t;
    return function(...args) {
        clearTimeout(t);
        t = setTimeout(() => fn(...args), wait);
    };
}

// ==================== INPUT HANDLER ====================
function onInput(event) {
    if (!extensionEnabled) return;

    // resolveEditableTarget defined in dom.js – handles ql-clipboard remapping
    const field = resolveEditableTarget(event.target);
    if (!field) return;

    const currentText = getFieldText(field);
    if (currentText === lastSentText.get(field)) return;

    if (!field._debouncedMask) {
        field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
    }
    field._debouncedMask(field, currentText);
}

// ==================== PASTE HANDLER ====================
function onPaste(event) {
    setTimeout(() => {
        // Same ql-clipboard remapping as onInput – both now go through resolveEditableTarget
        const field = resolveEditableTarget(event.target);
        if (!field) return;
        const currentText = getFieldText(field);
        if (currentText && !isAlreadyMasked(currentText)) {
            maskAndReplace(field, currentText);
        }
    }, 50);
}

// ==================== CORE MASKING ====================
async function maskAndReplace(field, text) {
    if (!extensionEnabled) return;
    if (!text || !text.trim()) return;
    if (isAlreadyMasked(text)) { 
        console.log("⏭️ Already masked."); 
        return; 
    }
    if (text.length > MAX_TEXT_LENGTH) {
        console.warn(`⚠️ Text too long (${text.length}), skipping.`);
        return;
    }
    if (isProcessing.get(field)) {
        console.log("⏳ Already processing, skipping.");
        return;
    }

    // Clear any pending replacement for this field before starting a fresh one
    if (pendingTimeouts.has(field)) {
        clearTimeout(pendingTimeouts.get(field));
        pendingTimeouts.delete(field);
    }

    // Save cursor position BEFORE any changes
    const cursorSaved = saveCursorPosition(field);  // dom.js
    isProcessing.set(field, true);

    try {
        // sendToBackend defined in api.js – no arguments needed, uses globals
        const result = await sendToBackend(text);

        if (!result.success) {
            console.error("❌ Backend error:", result.error);
            isProcessing.set(field, false);
            return;
        }

        const data = result.data;
        if (!data || typeof data !== 'object') {
            console.error("❌ Invalid data from backend:", data);
            isProcessing.set(field, false);
            return;
        }

        // CRITICAL FIX: First update text, THEN highlight
        if (data.status === 'ok' && data.masked && data.masked !== text) {
            try {
                // Step 1: Update the field text and WAIT for DOM to settle
                await setFieldText(field, data.masked);  // dom.js (now async)
                
                // Step 2: Wait one more frame for DOM to fully update
                await new Promise(resolve => requestAnimationFrame(resolve));
                
                // Step 3: NOW highlight (DOM is ready, no null errors)
                if (Array.isArray(data.entities) && data.entities.length > 0) {
                    highlightField(field, data.entities);  // highlight.js
                }
                
                // Step 4: Restore cursor AFTER highlight (avoid offset errors)
                setTimeout(() => {
                    try {
                        restoreCursorPosition(field, cursorSaved, data.masked); // dom.js
                    } catch (e) {
                        console.debug("Cursor restore skipped (non-fatal):", e);
                    }
                }, 100);
                
                // Update last sent text
                lastSentText.set(field, data.masked);
                
            } catch (e) {
                console.error("❌ Text replacement error:", e);
            }
        } else {
            // No masking needed, just highlight
            if (Array.isArray(data.entities) && data.entities.length > 0) {
                highlightField(field, data.entities);  // highlight.js
            }
            lastSentText.set(field, data.masked || text);
        }

    } catch (e) {
        console.error("❌ Fatal maskAndReplace error:", e);
    } finally {
        // Always release the processing lock
        isProcessing.set(field, false);
        pendingTimeouts.delete(field);
    }
}

// ==================== FIELD SELECTORS ====================
const FIELD_SELECTORS = [
    'input[type="text"]',  'input[type="search"]', 'input[type="tel"]',
    'input[type="url"]',   'input[type="email"]',  'input[type="password"]',
    'input[type="number"]','textarea',              '[contenteditable="true"]'
];

// ==================== MUTATION OBSERVER ====================
let observerTimeout;
function handleMutations() {
    clearTimeout(observerTimeout);
    observerTimeout = setTimeout(() => {
        scanAndAttach(FIELD_SELECTORS, onInput, onPaste); // dom.js
    }, OBSERVER_DEBOUNCE);
}

function observeDynamicFields() {
    if (!document.body) return;
    new MutationObserver(handleMutations).observe(document.body, {
        childList: true,
        subtree:   true,
    });
    console.log("👁️ MutationObserver active");
}

// ==================== INITIALISATION ====================
function init() {
    injectHighlightStyles();                              // highlight.js
    scanAndAttach(FIELD_SELECTORS, onInput, onPaste);    // dom.js
    observeDynamicFields();
    checkBackendHealth(true);                             // api.js – eager first check
    setInterval(() => checkBackendHealth(), HEALTH_CHECK_INTERVAL);
    console.log("🔒 PreSendAI initialised");
}

// Content scripts default to document_idle, but guard anyway
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}