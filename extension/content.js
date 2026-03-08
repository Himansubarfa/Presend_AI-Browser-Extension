// // content.js – injected into every page
// console.log("🔒 PreSendAI content script loaded");

// // You can add a simple listener to test later
// document.addEventListener("input", (e) => {
//   const target = e.target;
//   if (target.tagName === "TEXTAREA" || target.tagName === "INPUT" || target.isContentEditable) {
//     console.log("Typing detected in editable field:", target.value || target.innerText);
//   }
// });


// Day 12 enhance the ui for the user 

// content.js – Detect and monitor editable fields

console.log("🔒 PreSendAI content script loaded – Day 12");

// Store attached fields to avoid duplicate listeners
const trackedFields = new WeakSet();

/**
 * Check if an element is an editable text field.
 * Returns true for <input> (excluding buttons, checkboxes, etc.), <textarea>, and contenteditable elements.
 */
function isEditableField(element) {
  if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
  const tag = element.tagName.toLowerCase();
  // Input elements (only text-like types)
  if (tag === 'input') {
    const type = element.type.toLowerCase();
    return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
  }
  // Textarea
  if (tag === 'textarea') return true;
  // Contenteditable (any element with contenteditable="true")
  if (element.isContentEditable) return true;
  return false;
}

/**
 * Handle input event on an editable field.
 * Logs the current value for now – later we'll send to backend and mask.
 */
function onInput(event) {
  const target = event.target;
  let content = '';
  if (target.tagName.toLowerCase() === 'input' || target.tagName.toLowerCase() === 'textarea') {
    content = target.value;
  } else if (target.isContentEditable) {
    content = target.innerText;
  }
  console.log(`✏️ Typing in ${target.tagName}:`, content);
  // TODO: Later we'll send to backend and replace with masked text
}

/**
 * Attach input listener to an editable field if not already tracked.
 */
function attachListener(field) {
  if (!trackedFields.has(field)) {
    field.addEventListener('input', onInput);
    trackedFields.add(field);
    console.log(`👂 Listening to`, field);
  }
}

/**
 * Find all editable fields on the current page and attach listeners.
 */
function scanAndAttach() {
  // Get all input, textarea, and any element with contenteditable
  const inputs = document.querySelectorAll('input[type="text"], input[type="search"], input[type="tel"], input[type="url"], input[type="email"], input[type="password"], input[type="number"], textarea, [contenteditable="true"]');
  inputs.forEach(attachListener);
}

// Run initial scan when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', scanAndAttach);
} else {
  scanAndAttach();
}

// Optional: Also handle dynamically added fields via MutationObserver (will be added in Day 16)
// For now, just initial scan.