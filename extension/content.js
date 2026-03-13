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

// console.log("🔒 PreSendAI content script loaded – Day 12");

// // Store attached fields to avoid duplicate listeners
// const trackedFields = new WeakSet();

// /**
//  * Check if an element is an editable text field.
//  * Returns true for <input> (excluding buttons, checkboxes, etc.), <textarea>, and contenteditable elements.
//  */
// function isEditableField(element) {
//   if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//   const tag = element.tagName.toLowerCase();
//   // Input elements (only text-like types)
//   if (tag === 'input') {
//     const type = element.type.toLowerCase();
//     return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//   }
//   // Textarea
//   if (tag === 'textarea') return true;
//   // Contenteditable (any element with contenteditable="true")
//   if (element.isContentEditable) return true;
//   return false;
// }

// /**
//  * Handle input event on an editable field.
//  * Logs the current value for now – later we'll send to backend and mask.
//  */
// function onInput(event) {
//   const target = event.target;
//   let content = '';
//   if (target.tagName.toLowerCase() === 'input' || target.tagName.toLowerCase() === 'textarea') {
//     content = target.value;
//   } else if (target.isContentEditable) {
//     content = target.innerText;
//   }
//   console.log(`✏️ Typing in ${target.tagName}:`, content);
//   // TODO: Later we'll send to backend and replace with masked text
// }

// /**
//  * Attach input listener to an editable field if not already tracked.
//  */
// function attachListener(field) {
//   if (!trackedFields.has(field)) {
//     field.addEventListener('input', onInput);
//     trackedFields.add(field);
//     console.log(`👂 Listening to`, field);
//   }
// }

// /**
//  * Find all editable fields on the current page and attach listeners.
//  */
// function scanAndAttach() {
//   // Get all input, textarea, and any element with contenteditable
//   const inputs = document.querySelectorAll('input[type="text"], input[type="search"], input[type="tel"], input[type="url"], input[type="email"], input[type="password"], input[type="number"], textarea, [contenteditable="true"]');
//   inputs.forEach(attachListener);
// }

// // Run initial scan when DOM is ready
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//   scanAndAttach();
// }

// // Optional: Also handle dynamically added fields via MutationObserver (will be added in Day 16)
// // For now, just initial scan.




// Day 13 updating and connecting the forntend with the backend 
// content.js – Day 13: Connect to backend and replace text

// console.log("🔒 PreSendAI content script loaded – Day 13");

// // Configuration
// const BACKEND_URL = "http://localhost:5000/scan"; // Change in production
// const DEBOUNCE_DELAY = 600; // ms

// // Track fields to avoid duplicate listeners and store last sent text
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap(); // field -> last text sent to backend
// let isUpdating = false; // flag to ignore input events caused by our own replacement

// /**
//  * Check if an element is an editable text field.
//  */
// function isEditableField(element) {
//   if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//   const tag = element.tagName.toLowerCase();
//   if (tag === 'input') {
//     const type = element.type.toLowerCase();
//     return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//   }
//   if (tag === 'textarea') return true;
//   if (element.isContentEditable) return true;
//   return false;
// }

// /**
//  * Get the current text content from an editable field.
//  */
// function getFieldText(field) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     return field.value;
//   } else if (field.isContentEditable) {
//     return field.innerText; // or textContent; innerText respects line breaks
//   }
//   return '';
// }

// /**
//  * Set the text content of an editable field, preserving cursor if possible (basic).
//  * For contenteditable, we replace innerText – cursor will jump to end (to be fixed later).
//  */
// function setFieldText(field, newText) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     field.value = newText;
//   } else if (field.isContentEditable) {
//     field.innerText = newText;
//   }
// }

// /**
//  * Debounce helper: returns a function that delays invoking `func` until after `wait` ms.
//  */
// function debounce(func, wait) {
//   let timeout;
//   return function executedFunction(...args) {
//     const later = () => {
//       clearTimeout(timeout);
//       func(...args);
//     };
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//   };
// }

// /**
//  * Send text to backend and update the field with masked result.
//  */
// async function maskAndReplace(field, text) {
//   if (!text.trim()) return; // don't send empty text

//   try {
//     const response = await fetch(BACKEND_URL, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ text })
//     });

//     if (!response.ok) {
//       console.error('Backend error:', response.status, response.statusText);
//       return;
//     }

//     const data = await response.json();
//     if (data.status === 'ok' && data.masked && data.masked !== text) {
//       // Use flag to ignore the input event that will be triggered by our replacement
//       isUpdating = true;
//       setFieldText(field, data.masked);
//       isUpdating = false;
//       // Update last sent text to avoid re-sending the masked version
//       lastSentText.set(field, data.masked);
//     } else if (data.status === 'error') {
//       console.warn('Backend processing error:', data.message);
//     }
//   } catch (error) {
//     console.error('Failed to connect to backend:', error);
//   }
// }

// // Create a debounced version of maskAndReplace per field? Actually we can share a single debouncer
// // but we need to pass the field. We'll create a closure for each field inside the input handler.

// /**
//  * Handle input event on an editable field.
//  */
// function onInput(event) {
//   if (isUpdating) return; // ignore events triggered by our own replacement

//   const field = event.target;
//   const currentText = getFieldText(field);
//   const lastSent = lastSentText.get(field);

//   // Skip if text is unchanged since last sent
//   if (currentText === lastSent) return;

//   // Store as last sent optimistically? We'll store after successful replacement.
//   // Actually we want to avoid sending again until the user types more.
//   // We'll store after API call, but also avoid sending while debouncing.
//   // For now, we just call the debounced function.

//   // Create a debounced function for this field if not already created
//   if (!field._debouncedMask) {
//     field._debouncedMask = debounce((field, text) => {
//       maskAndReplace(field, text);
//     }, DEBOUNCE_DELAY);
//   }

//   // Cancel any pending call for this field and schedule new one
//   field._debouncedMask(field, currentText);
// }

// /**
//  * Attach input listener to an editable field if not already tracked.
//  */
// function attachListener(field) {
//   if (!trackedFields.has(field)) {
//     field.addEventListener('input', onInput);
//     trackedFields.add(field);
//     console.log('👂 Listening to', field);
//   }
// }

// /**
//  * Scan page for editable fields and attach listeners.
//  */
// function scanAndAttach() {
//   const selectors = [
//     'input[type="text"]',
//     'input[type="search"]',
//     'input[type="tel"]',
//     'input[type="url"]',
//     'input[type="email"]',
//     'input[type="password"]',
//     'input[type="number"]',
//     'textarea',
//     '[contenteditable="true"]'
//   ];
//   document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // Initial scan
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//   scanAndAttach();
// }

// // Optional: observe dynamically added fields (will be added in Day 16)



// DAY 13 new update for any browser extension 
// console.log("🔒 PreSendAI content script loaded – Day 13 (with background worker)");

// // Configuration
// const BACKEND_URL = "http://localhost:5000/scan"; // Change in production
// const DEBOUNCE_DELAY = 600; // ms

// // Track fields to avoid duplicate listeners and store last sent text
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap(); // field -> last text sent to backend
// let isUpdating = false; // flag to ignore input events caused by our own replacement

// /**
//  * Check if an element is an editable text field.
//  */
// function isEditableField(element) {
//   if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//   const tag = element.tagName.toLowerCase();
//   if (tag === 'input') {
//     const type = element.type.toLowerCase();
//     return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//   }
//   if (tag === 'textarea') return true;
//   if (element.isContentEditable) return true;
//   return false;
// }

// /**
//  * Get the current text content from an editable field.
//  */
// function getFieldText(field) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     return field.value;
//   } else if (field.isContentEditable) {
//     return field.innerText;
//   }
//   return '';
// }

// /**
//  * Set the text content of an editable field.
//  */
// function setFieldText(field, newText) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     field.value = newText;
//   } else if (field.isContentEditable) {
//     field.innerText = newText;
//   }
// }

// /**
//  * Debounce helper.
//  */
// function debounce(func, wait) {
//   let timeout;
//   return function executedFunction(...args) {
//     const later = () => {
//       clearTimeout(timeout);
//       func(...args);
//     };
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//   };
// }

// /**
//  * Send text to background worker and update field with masked result.
//  */
// // async function maskAndReplace(field, text) {
// //   if (!text.trim()) return;

// //   try {
// //     // Send message to background worker
// //     const response = await chrome.runtime.sendMessage({
// //       action: "maskText",
// //       text: text,
// //       url: BACKEND_URL
// //     });

// //     if (!response.success) {
// //       console.error("Background error:", response.error);
// //       return;
// //     }

// //     const data = response.data;
// //     if (data.status === 'ok' && data.masked && data.masked !== text) {
// //       isUpdating = true;
// //       setFieldText(field, data.masked);
// //       isUpdating = false;
// //       lastSentText.set(field, data.masked);
// //     } else if (data.status === 'error') {
// //       console.warn('Backend processing error:', data.message);
// //     }
// //   } catch (error) {
// //     console.error('Failed to communicate with background worker:', error);
// //   }
// // }


// async function maskAndReplace(field, text) {
//   console.log("maskAndReplace called with text:", text);
//   if (!text.trim()) return;

//   try {
//     console.log("Sending message to background...");
//     const response = await chrome.runtime.sendMessage({
//       action: "maskText",
//       text: text,
//       url: BACKEND_URL
//     });
//     console.log("Received response from background:", response);

//     if (!response.success) {
//       console.error("Background error:", response.error);
//       return;
//     }

//     const data = response.data;
//     if (data.status === 'ok' && data.masked && data.masked !== text) {
//       isUpdating = true;
//       setFieldText(field, data.masked);
//       isUpdating = false;
//       lastSentText.set(field, data.masked);
//     } else if (data.status === 'error') {
//       console.warn('Backend processing error:', data.message);
//     }
//   } catch (error) {
//     console.error('Failed to communicate with background worker:', error);
//   }
// }

// /**
//  * Handle input event on an editable field.
//  */
// function onInput(event) {
//   if (isUpdating) return;

//   const field = event.target;
//   const currentText = getFieldText(field);
//   const lastSent = lastSentText.get(field);

//   if (currentText === lastSent) return;

//   if (!field._debouncedMask) {
//     field._debouncedMask = debounce((field, text) => {
//       maskAndReplace(field, text);
//     }, DEBOUNCE_DELAY);
//   }

//   field._debouncedMask(field, currentText);
// }

// /**
//  * Attach input listener to an editable field if not already tracked.
//  */
// function attachListener(field) {
//   if (!trackedFields.has(field)) {
//     field.addEventListener('input', onInput);
//     trackedFields.add(field);
//     console.log('👂 Listening to', field);
//   }
// }

// /**
//  * Scan page for editable fields and attach listeners.
//  */
// function scanAndAttach() {
//   const selectors = [
//     'input[type="text"]',
//     'input[type="search"]',
//     'input[type="tel"]',
//     'input[type="url"]',
//     'input[type="email"]',
//     'input[type="password"]',
//     'input[type="number"]',
//     'textarea',
//     '[contenteditable="true"]'
//   ];
//   document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // Initial scan
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//   scanAndAttach();
// }


// Day 14 updated content.js

// console.log("🔒 PreSendAI content script loaded – Day 14");

// // Configuration
// const BACKEND_URL = "http://localhost:5000/scan"; // Change in production
// const DEBOUNCE_DELAY = 600; // ms

// // Track fields to avoid duplicate listeners and store last sent text
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap(); // field -> last text sent to backend
// let isUpdating = false; // flag to ignore input events caused by our own replacement

// // ---- Day 14: Placeholders to detect already masked text ----
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[REDACTED]"];

// function isAlreadyMasked(text) {
//   return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }
// // -------------------------------------------------------------

// /**
//  * Check if an element is an editable text field.
//  */
// function isEditableField(element) {
//   if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//   const tag = element.tagName.toLowerCase();
//   if (tag === 'input') {
//     const type = element.type.toLowerCase();
//     return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//   }
//   if (tag === 'textarea') return true;
//   if (element.isContentEditable) return true;
//   return false;
// }

// /**
//  * Get the current text content from an editable field.
//  */
// function getFieldText(field) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     return field.value;
//   } else if (field.isContentEditable) {
//     return field.innerText;
//   }
//   return '';
// }

// /**
//  * Set the text content of an editable field.
//  */
// function setFieldText(field, newText) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     field.value = newText;
//   } else if (field.isContentEditable) {
//     field.innerText = newText;
//   }
// }

// /**
//  * Debounce helper.
//  */
// function debounce(func, wait) {
//   let timeout;
//   return function executedFunction(...args) {
//     const later = () => {
//       clearTimeout(timeout);
//       func(...args);
//     };
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//   };
// }

// /**
//  * Send text to background worker and update field with masked result.
//  * (Day 14: skip if already masked)
//  */
// async function maskAndReplace(field, text) {
//   console.log("maskAndReplace called with text:", text);
//   if (!text.trim()) return;

//   // ---- Day 14: Skip if text already contains a placeholder ----
//   if (isAlreadyMasked(text)) {
//     console.log("Text already masked, skipping.");
//     return;
//   }
//   // -------------------------------------------------------------

//   try {
//     console.log("Sending message to background...");
//     const response = await chrome.runtime.sendMessage({
//       action: "maskText",
//       text: text,
//       url: BACKEND_URL
//     });
//     console.log("Received response from background:", response);

//     if (!response.success) {
//       console.error("Background error:", response.error);
//       return;
//     }

//     const data = response.data;
//     if (data.status === 'ok' && data.masked && data.masked !== text) {
//       isUpdating = true;
//       setFieldText(field, data.masked);
//       isUpdating = false;
//       lastSentText.set(field, data.masked);
//     } else if (data.status === 'error') {
//       console.warn('Backend processing error:', data.message);
//     }
//   } catch (error) {
//     console.error('Failed to communicate with background worker:', error);
//   }
// }

// /**
//  * Handle input event on an editable field.
//  */
// function onInput(event) {
//   if (isUpdating) return;

//   const field = event.target;
//   const currentText = getFieldText(field);
//   const lastSent = lastSentText.get(field);

//   if (currentText === lastSent) return;

//   if (!field._debouncedMask) {
//     field._debouncedMask = debounce((field, text) => {
//       maskAndReplace(field, text);
//     }, DEBOUNCE_DELAY);
//   }

//   field._debouncedMask(field, currentText);
// }

// /**
//  * Attach input listener to an editable field if not already tracked.
//  */
// function attachListener(field) {
//   if (!trackedFields.has(field)) {
//     field.addEventListener('input', onInput);
//     trackedFields.add(field);
//     console.log('👂 Listening to', field);
//   }
// }

// /**
//  * Scan page for editable fields and attach listeners.
//  */
// function scanAndAttach() {
//   const selectors = [
//     'input[type="text"]',
//     'input[type="search"]',
//     'input[type="tel"]',
//     'input[type="url"]',
//     'input[type="email"]',
//     'input[type="password"]',
//     'input[type="number"]',
//     'textarea',
//     '[contenteditable="true"]'
//   ];
//   document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // Initial scan
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//   scanAndAttach();
// }




// DAY 15 update 
// console.log("🔒 PreSendAI content script loaded – Day 15 (cursor preservation)");

// // Configuration
// const BACKEND_URL = "http://localhost:5000/scan"; // Change in production
// const DEBOUNCE_DELAY = 600; // ms

// // Track fields to avoid duplicate listeners and store last sent text
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap(); // field -> last text sent to backend
// let isUpdating = false; // flag to ignore input events caused by our own replacement

// // ---- Day 14: Placeholders to detect already masked text ----
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[REDACTED]"];

// function isAlreadyMasked(text) {
//   return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }
// // -------------------------------------------------------------

// /**
//  * Check if an element is an editable text field.
//  */
// function isEditableField(element) {
//   if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//   const tag = element.tagName.toLowerCase();
//   if (tag === 'input') {
//     const type = element.type.toLowerCase();
//     return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//   }
//   if (tag === 'textarea') return true;
//   if (element.isContentEditable) return true;
//   return false;
// }

// /**
//  * Get the current text content from an editable field.
//  */
// function getFieldText(field) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     return field.value;
//   } else if (field.isContentEditable) {
//     return field.innerText;
//   }
//   return '';
// }

// /**
//  * Set the text content of an editable field.
//  */
// function setFieldText(field, newText) {
//   const tag = field.tagName.toLowerCase();
//   if (tag === 'input' || tag === 'textarea') {
//     field.value = newText;
//   } else if (field.isContentEditable) {
//     field.innerText = newText;
//   }
// }

// /**
//  * Debounce helper.
//  */
// function debounce(func, wait) {
//   let timeout;
//   return function executedFunction(...args) {
//     const later = () => {
//       clearTimeout(timeout);
//       func(...args);
//     };
//     clearTimeout(timeout);
//     timeout = setTimeout(later, wait);
//   };
// }

/**
 * Send text to background worker and update field with masked result.
 * Day 15: cursor preservation for input/textarea.
 */
// async function maskAndReplace(field, text) {
//   console.log("maskAndReplace called with text:", text);
//   if (!text.trim()) return;

//   // ---- Day 14: Skip if text already contains a placeholder ----
//   if (isAlreadyMasked(text)) {
//     console.log("Text already masked, skipping.");
//     return;
//   }
//   // -------------------------------------------------------------

//   // ---- Day 15: Save cursor position (only for input/textarea) ----
//   let startPos = null, endPos = null;
//   const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
//   if (isInputOrTextarea) {
//     startPos = field.selectionStart;
//     endPos = field.selectionEnd;
//     console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
//   }
//   // -----------------------------------------------------------------

//   try {
//     console.log("Sending message to background...");
//     const response = await chrome.runtime.sendMessage({
//       action: "maskText",
//       text: text,
//       url: BACKEND_URL
//     });
//     console.log("Received response from background:", response);

//     if (!response.success) {
//       console.error("Background error:", response.error);
//       return;
//     }

//     const data = response.data;
//     if (data.status === 'ok' && data.masked && data.masked !== text) {
//       isUpdating = true;
//       setFieldText(field, data.masked);

//       // ---- Day 15: Restore cursor position (input/textarea) ----
//       if (isInputOrTextarea && startPos !== null && endPos !== null) {
//         // New text length might differ; clamp positions to new length
//         const newLength = data.masked.length;
//         const newStart = Math.min(startPos, newLength);
//         const newEnd = Math.min(endPos, newLength);
//         field.setSelectionRange(newStart, newEnd);
//         console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
//       }
//       // ---------------------------------------------------------

//       isUpdating = false;
//       lastSentText.set(field, data.masked);
//     } else if (data.status === 'error') {
//       console.warn('Backend processing error:', data.message);
//     }
//   } catch (error) {
//     console.error('Failed to communicate with background worker:', error);
//   }
// }

// /**
//  * Handle input event on an editable field.
//  */
// function onInput(event) {
//   if (isUpdating) return;

//   const field = event.target;
//   const currentText = getFieldText(field);
//   const lastSent = lastSentText.get(field);

//   if (currentText === lastSent) return;

//   if (!field._debouncedMask) {
//     field._debouncedMask = debounce((field, text) => {
//       maskAndReplace(field, text);
//     }, DEBOUNCE_DELAY);
//   }

//   field._debouncedMask(field, currentText);
// }

// /**
//  * Attach input listener to an editable field if not already tracked.
//  */
// function attachListener(field) {
//   if (!trackedFields.has(field)) {
//     field.addEventListener('input', onInput);
//     trackedFields.add(field);
//     console.log('👂 Listening to', field);
//   }
// }

// /**
//  * Scan page for editable fields and attach listeners.
//  */
// function scanAndAttach() {
//   const selectors = [
//     'input[type="text"]',
//     'input[type="search"]',
//     'input[type="tel"]',
//     'input[type="url"]',
//     'input[type="email"]',
//     'input[type="password"]',
//     'input[type="number"]',
//     'textarea',
//     '[contenteditable="true"]'
//   ];
//   document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // Initial scan
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//   scanAndAttach();
// }




// // Day 15  final update 


// console.log("🔒 PreSendAI content script loaded – Day 15 (cursor preservation)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";      // Change in production
// const DEBOUNCE_DELAY = 600;                            // ms

// // Placeholders to detect already‑masked text
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();        // fields that already have a listener
// const lastSentText = new WeakMap();          // field -> last text sent to backend
// let isUpdating = false;                      // flag to ignore self‑triggered input events

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;

//     // Day 14: skip if already masked
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }

//     // Save cursor position (only for input/textarea)
//     let startPos = null, endPos = null;
//     const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
//     if (isInputOrTextarea) {
//         startPos = field.selectionStart;
//         endPos = field.selectionEnd;
//         console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
//     }

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             // Day 15: restore cursor position (input/textarea)
//             if (isInputOrTextarea && startPos !== null && endPos !== null) {
//                 const newLength = data.masked.length;
//                 const newStart = Math.min(startPos, newLength);
//                 const newEnd = Math.min(endPos, newLength);
//                 field.setSelectionRange(newStart, newEnd);
//                 console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
//             }

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     // Create a debounced function for this field if not already created
//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // Initial scan when DOM is ready
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', scanAndAttach);
// } else {
//     scanAndAttach();
// }



// Update for day 16 

// console.log("🔒 PreSendAI content script loaded – Day 16 (MutationObserver)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";      // Change in production
// const DEBOUNCE_DELAY = 600;                            // ms
// const OBSERVER_DEBOUNCE = 300;                         // ms delay for processing DOM mutations

// // Placeholders to detect already‑masked text
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();        // fields that already have a listener
// const lastSentText = new WeakMap();          // field -> last text sent to backend
// let isUpdating = false;                      // flag to ignore self‑triggered input events

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;

//     // Day 14: skip if already masked
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }

//     // Save cursor position (only for input/textarea)
//     let startPos = null, endPos = null;
//     const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
//     if (isInputOrTextarea) {
//         startPos = field.selectionStart;
//         endPos = field.selectionEnd;
//         console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
//     }

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             // Day 15: restore cursor position (input/textarea)
//             if (isInputOrTextarea && startPos !== null && endPos !== null) {
//                 const newLength = data.masked.length;
//                 const newStart = Math.min(startPos, newLength);
//                 const newEnd = Math.min(endPos, newLength);
//                 field.setSelectionRange(newStart, newEnd);
//                 console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
//             }

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     // Create a debounced function for this field if not already created
//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// // ==================== SCANNER ====================
// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER (Day 16) ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     // Debounce processing to avoid excessive scans
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// updated day 16 

// console.log("🔒 PreSendAI content script loaded – Day 16 (MutationObserver + ORG)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 600;
// const OBSERVER_DEBOUNCE = 300;

// // Placeholders – added [ORG]
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// let isUpdating = false;

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;

//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }

//     let startPos = null, endPos = null;
//     const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
//     if (isInputOrTextarea) {
//         startPos = field.selectionStart;
//         endPos = field.selectionEnd;
//         console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
//     }

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             if (isInputOrTextarea && startPos !== null && endPos !== null) {
//                 const newLength = data.masked.length;
//                 const newStart = Math.min(startPos, newLength);
//                 const newEnd = Math.min(endPos, newLength);
//                 field.setSelectionRange(newStart, newEnd);
//                 console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
//             }

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }




// DAY 17 update 

// console.log("🔒 PreSendAI content script loaded – Day 17 (Duplicate Prevention)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 600;
// const OBSERVER_DEBOUNCE = 300;

// // Placeholders
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();          // fields with listeners
// const lastSentText = new WeakMap();            // field -> last text sent to backend
// const isProcessing = new WeakMap();             // field -> boolean (request in progress)
// let isUpdating = false;                          // flag to ignore self‑triggered input events

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);

//     // --- Duplicate prevention 1: empty text ---
//     if (!text.trim()) return;

//     // --- Duplicate prevention 2: already masked ---
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }

//     // --- Duplicate prevention 3: already processing this field ---
//     if (isProcessing.get(field)) {
//         console.log("Already processing this field, skipping duplicate.");
//         return;
//     }

//     // Save cursor position (only for input/textarea)
//     let startPos = null, endPos = null;
//     const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
//     if (isInputOrTextarea) {
//         startPos = field.selectionStart;
//         endPos = field.selectionEnd;
//         console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
//     }

//     // Mark as processing
//     isProcessing.set(field, true);

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             if (isInputOrTextarea && startPos !== null && endPos !== null) {
//                 const newLength = data.masked.length;
//                 const newStart = Math.min(startPos, newLength);
//                 const newEnd = Math.min(endPos, newLength);
//                 field.setSelectionRange(newStart, newEnd);
//                 console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
//             }

//             isUpdating = false;
//             // Remember this text so we don't send it again
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//             // Still remember the text to avoid re‑sending unchanged text
//             lastSentText.set(field, data.masked || text);
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     } finally {
//         // Always clear processing flag
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     // --- Duplicate prevention 4: text unchanged since last successful send ---
//     if (currentText === lastSent) return;

//     // Create a debounced function for this field if not already created
//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     // Cancel any pending call and schedule new one
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }




// DAY 17 FINAL UPATE 
// console.log("🔒 PreSendAI content script loaded – Day 17 (Duplicate Prevention + Full Cursor)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 800;
// const OBSERVER_DEBOUNCE = 300;

// // Placeholders
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();          // fields with listeners
// const lastSentText = new WeakMap();            // field -> last text sent to backend
// const isProcessing = new WeakMap();             // field -> boolean (request in progress)
// let isUpdating = false;                          // flag to ignore self‑triggered input events

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CURSOR PRESERVATION (unified) ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     // For input/textarea
//     if (tag === 'input' || tag === 'textarea') {
//         return {
//             type: 'input',
//             start: field.selectionStart,
//             end: field.selectionEnd
//         };
//     }
//     // For contenteditable
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         // If the cursor is inside this field
//         if (field.contains(range.startContainer)) {
//             // Simple approach: save the character offset from the start of the field's innerText
//             // This works if the field contains only text (no rich HTML). For Gemini, that's fine.
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             const startOffset = preCaretRange.toString().length;
//             return {
//                 type: 'contenteditable',
//                 offset: startOffset
//             };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         const newStart = Math.min(saved.start, newLength);
//         const newEnd = Math.min(saved.end, newLength);
//         field.setSelectionRange(newStart, newEnd);
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         // Find the first text node inside the field
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             const sel = window.getSelection();
//             sel.removeAllRanges();
//             sel.addRange(range);
//         }
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);

//     // Duplicate prevention
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("Already processing this field, skipping duplicate.");
//         return;
//     }

//     // Save cursor position
//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);

//     // Mark as processing
//     isProcessing.set(field, true);

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             // Restore cursor position
//             restoreCursorPosition(field, cursorSaved, data.masked);

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//             lastSentText.set(field, data.masked || text);
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     } finally {
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }



// DAY 17 final code update 

// content.js – Final version: robust PII masking with cursor preservation, duplicate prevention, and dynamic field support

// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";      // Change in production
// const DEBOUNCE_DELAY = 1000;                            // ms
// const OBSERVER_DEBOUNCE = 300;                         // ms for MutationObserver

// // All placeholders used by the backend (must match MASK_LABELS in masker.py)
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();          // fields with listeners
// const lastSentText = new WeakMap();            // field -> last text sent to backend
// const isProcessing = new WeakMap();             // field -> boolean (request in progress)
// let isUpdating = false;                          // flag to ignore self‑triggered input events

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return {
//             type: 'input',
//             start: field.selectionStart,
//             end: field.selectionEnd
//         };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             const startOffset = preCaretRange.toString().length;
//             return {
//                 type: 'contenteditable',
//                 offset: startOffset
//             };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         const newStart = Math.min(saved.start, newLength);
//         const newEnd = Math.min(saved.end, newLength);
//         field.setSelectionRange(newStart, newEnd);
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             const sel = window.getSelection();
//             sel.removeAllRanges();
//             sel.addRange(range);
//         }
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("Already processing this field, skipping duplicate.");
//         return;
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);

//     isProcessing.set(field, true);

//     try {
//         console.log("Sending message to background...");
//         const response = await chrome.runtime.sendMessage({
//             action: "maskText",
//             text: text,
//             url: BACKEND_URL
//         });
//         console.log("Received response from background:", response);

//         if (!response.success) {
//             console.error("Background error:", response.error);
//             return;
//         }

//         const data = response.data;
//         console.log("Backend data:", data);

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             restoreCursorPosition(field, cursorSaved, data.masked);

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//             lastSentText.set(field, data.masked || text);
//         }
//     } catch (error) {
//         console.error('Failed to communicate with background worker:', error);
//     } finally {
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }



// Day 17 final code replacement


// content.js – Final cross‑browser version
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";      // Change in production
// const DEBOUNCE_DELAY = 1000;                           // 1 second delay after typing stops
// const OBSERVER_DEBOUNCE = 300;                         // ms for MutationObserver

// // All placeholders used by the backend
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;

// if (!runtime) {
//     console.warn("No extension runtime API found. Direct fetch will be used (may be blocked by CORS/Shields).");
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return field.value;
//     } else if (field.isContentEditable) {
//         return field.innerText;
//     }
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//     } else if (field.isContentEditable) {
//         field.innerText = newText;
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function executedFunction(...args) {
//         const later = () => {
//             clearTimeout(timeout);
//             func(...args);
//         };
//         clearTimeout(timeout);
//         timeout = setTimeout(later, wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return {
//             type: 'input',
//             start: field.selectionStart,
//             end: field.selectionEnd
//         };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             const startOffset = preCaretRange.toString().length;
//             return {
//                 type: 'contenteditable',
//                 offset: startOffset
//             };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         const newStart = Math.min(saved.start, newLength);
//         const newEnd = Math.min(saved.end, newLength);
//         field.setSelectionRange(newStart, newEnd);
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             const sel = window.getSelection();
//             sel.removeAllRanges();
//             sel.addRange(range);
//         }
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     // Try using extension runtime API first (most reliable, bypasses CORS)
//     if (runtime) {
//         try {
//             const response = await new Promise((resolve, reject) => {
//                 runtime.sendMessage({ action: "maskText", text: text, url: BACKEND_URL }, (response) => {
//                     // In Chrome, runtime.lastError is set if there's an error
//                     if (chrome.runtime.lastError) {
//                         reject(new Error(chrome.runtime.lastError.message));
//                     } else {
//                         resolve(response);
//                     }
//                 });
//             });
//             return { success: true, data: response.data };
//         } catch (error) {
//             console.warn("Runtime messaging failed, falling back to direct fetch:", error);
//             // fall through to direct fetch
//         }
//     } else {
//         console.warn("No runtime API available, using direct fetch (may be blocked)");
//     }

//     // Fallback: direct fetch (may be blocked by CORS/Shields, but we try)
//     try {
//         const response = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         if (!response.ok) {
//             const errorText = await response.text();
//             throw new Error(`HTTP ${response.status}: ${errorText}`);
//         }
//         const data = await response.json();
//         return { success: true, data };
//     } catch (error) {
//         console.error("Direct fetch failed:", error);
//         return { success: false, error: error.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("Text already masked, skipping.");
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("Already processing this field, skipping duplicate.");
//         return;
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);

//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("Backend result:", result);

//         if (!result.success) {
//             console.error("Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing field text with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);

//             restoreCursorPosition(field, cursorSaved, data.masked);

//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else if (data.status === 'error') {
//             console.warn('Backend processing error:', data.message);
//         } else {
//             console.log("No change needed (masked text unchanged or empty)");
//             lastSentText.set(field, data.masked || text);
//         }
//     } catch (error) {
//         console.error('Failed to communicate:', error);
//     } finally {
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);

//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((field, text) => {
//             maskAndReplace(field, text);
//         }, DEBOUNCE_DELAY);
//     }

//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]',
//         'input[type="search"]',
//         'input[type="tel"]',
//         'input[type="url"]',
//         'input[type="email"]',
//         'input[type="password"]',
//         'input[type="number"]',
//         'textarea',
//         '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout = null;
// function handleMutations(mutations) {
//     if (observerTimeout) clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     const observer = new MutationObserver(handleMutations);
//     observer.observe(document.body, {
//         childList: true,
//         subtree: true
//     });
//     console.log("👁️ MutationObserver active – watching for new fields");
// }

// // ==================== INITIALISATION ====================
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => {
//         scanAndAttach();
//         observeDynamicFields();
//     });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }






















// day 17 final working 
// // content.js – Diagnostic version
// console.log("🔒 PreSendAI content script loaded – Diagnostic Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;
// const OBSERVER_DEBOUNCE = 300;
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("No extension runtime API found.");

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             const response = await new Promise((resolve, reject) => {
//                 runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                     if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
//                     else resolve(response);
//                 });
//             });
//             return { success: true, data: response.data };
//         } catch (e) {
//             console.warn("Runtime messaging failed, falling back to fetch:", e);
//         }
//     }
//     try {
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         if (!res.ok) throw new Error(`HTTP ${res.status}`);
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) { console.log("Text already masked, skipping."); return; }
//     if (isProcessing.get(field)) { console.log("Already processing, skipping."); return; }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("Backend result:", result);
//         if (!result.success) { console.error("Backend error:", result.error); return; }

//         const data = result.data;
//         if (data.status === 'ok' && data.masked && data.masked !== text) {
//             console.log("Replacing with:", data.masked);
//             isUpdating = true;
//             setFieldText(field, data.masked);
//             restoreCursorPosition(field, cursorSaved, data.masked);
//             isUpdating = false;
//             lastSentText.set(field, data.masked);
//         } else {
//             console.log("No change needed");
//             lastSentText.set(field, data.masked || text);
//         }
//     } catch (e) {
//         console.error("Error:", e);
//     } finally {
//         isProcessing.set(field, false);
//     }
// }

// function onInput(event) {
//     console.log("🟢 onInput triggered on", event.target.tagName, event.target);
//     if (isUpdating) { console.log("isUpdating true, ignoring"); return; }

//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     console.log("Current text:", currentText, "Last sent:", lastSent);

//     if (currentText === lastSent) { console.log("Text unchanged, ignoring"); return; }

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//         console.log("Created debouncer for field");
//     }
//     field._debouncedMask(field, currentText);
// }

// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }



// day 18 update 
// content.js – Day 18 with Highlight Engine
// console.log("🔒 PreSendAI content script loaded – Day 18 (Highlight Engine)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 800; // ms – how long highlights stay before replacement
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("No extension runtime API found.");

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE (Day 18) ====================

// // Inject highlight CSS into the page
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: yellow !important;
//             color: black !important;
//             border-radius: 2px;
//             transition: background-color 0.3s;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.5s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: rgba(255, 255, 0, 0.5); }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// // Highlight entities in a contenteditable field
// function highlightContentEditable(field, entities) {
//     // Save current selection
//     const sel = window.getSelection();
//     const savedRanges = [];
//     if (sel.rangeCount > 0) {
//         for (let i = 0; i < sel.rangeCount; i++) {
//             savedRanges.push(sel.getRangeAt(i).cloneRange());
//         }
//     }

//     // Get the HTML content and wrap each entity span
//     let html = field.innerHTML;
//     // Sort entities by start descending to avoid index shifts when inserting spans
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const text = ent.text;
//         // Simple search – this assumes text appears exactly once? Better to use index.
//         // But innerHTML may contain tags, so we'd need a more robust approach.
//         // For simplicity, we'll just use a global regex replace on the plain text version.
//         // This is a simplified highlight; a production version would need to map indices.
//         // We'll just do a simple replace on the innerText and set innerHTML accordingly.
//         // This may break formatting, but for Gemini it's usually plain.
//     }

//     // For demo, we'll just add a class to the field itself (flash) for any field type.
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);

//     // For contenteditable, a better approach would be to use a separate overlay.
//     // We'll implement a simple version: add a yellow background to the field and then revert.
//     field.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// // Highlight for input/textarea (flash background)
// function highlightInputField(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// // Main highlight function – decides based on field type
// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     if (field.isContentEditable) {
//         highlightContentEditable(field, entities);
//     } else {
//         highlightInputField(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             const response = await new Promise((resolve, reject) => {
//                 runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                     if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
//                     else resolve(response);
//                 });
//             });
//             return { success: true, data: response.data };
//         } catch (e) {
//             console.warn("Runtime messaging failed, falling back to fetch:", e);
//         }
//     }
//     try {
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         if (!res.ok) throw new Error(`HTTP ${res.status}`);
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) { console.log("Text already masked, skipping."); return; }
//     if (isProcessing.get(field)) { console.log("Already processing, skipping."); return; }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("Backend result:", result);
//         if (!result.success) { console.error("Backend error:", result.error); return; }

//         const data = result.data;
//         // If there are entities, highlight them
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait a bit for user to see highlight, then replace
//         setTimeout(async () => {
//             if (data.status === 'ok' && data.masked && data.masked !== text) {
//                 console.log("Replacing with:", data.masked);
//                 isUpdating = true;
//                 setFieldText(field, data.masked);
//                 restoreCursorPosition(field, cursorSaved, data.masked);
//                 isUpdating = false;
//                 lastSentText.set(field, data.masked);
//             } else {
//                 console.log("No change needed");
//                 lastSentText.set(field, data.masked || text);
//             }
//             isProcessing.set(field, false);
//         }, HIGHLIGHT_DURATION);

//     } catch (e) {
//         console.error("Error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// // ==================== HIGHLIGHT ENGINE (improved) ====================

// // Inject CSS (unchanged)
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: rgba(255, 255, 0, 0.4) !important;
//             color: inherit !important;
//             border-radius: 3px;
//             transition: background-color 0.2s;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.5s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: rgba(255, 255, 0, 0.3); }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// // Remove any existing highlights in the field
// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize(); // merge adjacent text nodes
//     });
// }

// // Wrap each entity in a highlight span (simple version for plain text content)
// // Assumes field contains only text nodes (no nested HTML). For rich editors, a more robust approach is needed.
// function highlightContentEditable(field, entities) {
//     removeHighlights(field);

//     // If the field has complex HTML, this simple version may break it.
//     // We'll assume it's plain text inside.
//     let html = field.innerHTML;
//     // Sort entities by start descending to avoid index shifts
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end, text } = ent;
//         // We need to find the position in the innerHTML? This is tricky because innerHTML may contain tags.
//         // A more reliable method is to work with the DOM directly.
//         // We'll use a TreeWalker to find text nodes and wrap them.
//         // This is complex – for brevity, we'll provide a simplified version that assumes the field's innerText matches the original text.
//         // For production, consider using a library like rangy or a more sophisticated algorithm.
//     }

//     // Simplified fallback: just add a class to the field itself (flash) for any field type.
//     // But we promised per-word highlight, so we need to do better.

//     // Instead, we'll implement a direct text node walker.
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) {
//         textNodes.push(node);
//     }

//     // Build a map of positions to nodes
//     let currentPos = 0;
//     const nodeMap = [];
//     for (const node of textNodes) {
//         const length = node.nodeValue.length;
//         nodeMap.push({ node, start: currentPos, end: currentPos + length });
//         currentPos += length;
//     }

//     // For each entity, find which node(s) it spans and wrap them
//     for (const ent of entities) {
//         const { start, end } = ent;
//         let remainingStart = start;
//         let remainingEnd = end;
//         for (const item of nodeMap) {
//             if (remainingStart >= item.end) continue;
//             if (remainingEnd <= item.start) break;

//             const overlapStart = Math.max(remainingStart, item.start);
//             const overlapEnd = Math.min(remainingEnd, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const parent = node.parentNode;
//                 if (parent) {
//                     // Replace the original text node with three nodes: before, span, after
//                     const fragment = document.createDocumentFragment();
//                     if (before) fragment.appendChild(document.createTextNode(before));
//                     fragment.appendChild(span);
//                     if (after) fragment.appendChild(document.createTextNode(after));
//                     parent.replaceChild(fragment, node);
//                 }
//                 // Update nodeMap and remaining positions (complex – we'll rebuild after each entity)
//                 // For simplicity, we'll break out and rebuild nodeMap after each entity.
//                 break; // rebuild needed
//             }
//         }
//         // After each entity, we should rebuild nodeMap because DOM changed.
//         // But to keep it simpler, we can re-run the whole function? Not efficient.
//         // For demo, we'll accept that this works only for non-overlapping simple cases.
//     }
// }

// // For input/textarea, keep a subtle flash (whole field)
// function highlightInputField(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     // Optionally set a light yellow background
//     field.style.backgroundColor = 'rgba(255, 255, 0, 0.2)';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// // Main highlight function
// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     if (field.isContentEditable) {
//         // For now, fallback to flash if per-word is too complex.
//         // We'll use the flash version but you can enable the advanced one later.
//         highlightInputField(field); // temporary – replace with per-word when ready
//     } else {
//         highlightInputField(field);
//     }
// }



// day 18 final code 

// content.js – Day 18 with robust per-word highlight (plain-text fallback)
// console.log("🔒 PreSendAI content script loaded – Day 18 (Robust Highlight)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 800; // ms
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("No extension runtime API found.");

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE (Robust) ====================

// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: rgba(255, 255, 0, 0.4) !important;
//             color: inherit !important;
//             border-radius: 3px;
//             transition: background-color 0.2s;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.5s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: rgba(255, 255, 0, 0.3); }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// // Remove existing highlights from a contenteditable field
// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize(); // merge adjacent text nodes
//     });
// }

// // Per-word highlight for plain-text contenteditable
// function highlightContentEditablePlain(field, entities) {
//     console.log("Applying per-word highlight to contenteditable");
//     // Check if field contains any HTML tags (simplified check)
//     if (/<[^>]*>/.test(field.innerHTML)) {
//         console.warn("Field contains HTML tags – falling back to field flash");
//         return false; // fallback to flash
//     }

//     removeHighlights(field); // clean previous

//     // Get all text nodes within the field
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     // Build a map of character positions to nodes
//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     // For each entity, wrap its text in a highlight span
//     // We need to modify the DOM – we'll do it from last to first to avoid shifting positions
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 // After replacing, the nodeMap is invalid – we'll rebuild after each entity? Too costly.
//                 // Instead, we'll just break and rely on the fact that we process in reverse order,
//                 // and we only need to wrap once per entity. But nodeMap is now outdated, but we won't use it again.
//                 // Since we sorted descending and process each entity once, it's okay.
//                 break;
//             }
//         }
//     }
//     return true; // success
// }

// // Fallback: flash the whole field (for input/textarea or when per-word fails)
// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = 'rgba(255, 255, 0, 0.2)';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// // Main highlight function with error handling
// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             const response = await new Promise((resolve, reject) => {
//                 runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                     if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
//                     else resolve(response);
//                 });
//             });
//             return { success: true, data: response.data };
//         } catch (e) {
//             console.warn("Runtime messaging failed, falling back to fetch:", e);
//         }
//     }
//     try {
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         if (!res.ok) throw new Error(`HTTP ${res.status}`);
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) { console.log("Text already masked, skipping."); return; }
//     if (isProcessing.get(field)) { console.log("Already processing, skipping."); return; }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("Backend result:", result);
//         if (!result.success) { console.error("Backend error:", result.error); return; }

//         const data = result.data;

//         // Highlight if there are entities
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait for highlight duration then replace
//         setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//             }
//         }, HIGHLIGHT_DURATION);

//     } catch (e) {
//         console.error("Error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// day 18 update 
// // content.js – Day 18 with robust per-word highlight (plain-text fallback)
// console.log("🔒 PreSendAI content script loaded – Day 18 (Robust Highlight)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 800; // ms
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("No extension runtime API found.");

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE (Robust) ====================

// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: rgba(255, 255, 0, 0.4) !important;
//             color: inherit !important;
//             border-radius: 3px;
//             transition: background-color 0.2s;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.5s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: rgba(255, 255, 0, 0.3); }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// // Remove existing highlights from a contenteditable field
// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize(); // merge adjacent text nodes
//     });
// }

// // Per-word highlight for plain-text contenteditable
// function highlightContentEditablePlain(field, entities) {
//     console.log("Applying per-word highlight to contenteditable");
//     // Check if field contains any HTML tags (simplified check)
//     if (/<[^>]*>/.test(field.innerHTML)) {
//         console.warn("Field contains HTML tags – falling back to field flash");
//         return false; // fallback to flash
//     }

//     removeHighlights(field); // clean previous

//     // Get all text nodes within the field
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     // Build a map of character positions to nodes
//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     // For each entity, wrap its text in a highlight span
//     // We need to modify the DOM – we'll do it from last to first to avoid shifting positions
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 // After replacing, the nodeMap is invalid – we'll rebuild after each entity? Too costly.
//                 // Instead, we'll just break and rely on the fact that we process in reverse order,
//                 // and we only need to wrap once per entity. But nodeMap is now outdated, but we won't use it again.
//                 // Since we sorted descending and process each entity once, it's okay.
//                 break;
//             }
//         }
//     }
//     return true; // success
// }

// // Fallback: flash the whole field (for input/textarea or when per-word fails)
// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = 'rgba(255, 255, 0, 0.2)';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// // Main highlight function with error handling
// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             const response = await new Promise((resolve, reject) => {
//                 runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                     if (chrome.runtime.lastError) reject(new Error(chrome.runtime.lastError.message));
//                     else resolve(response);
//                 });
//             });
//             return { success: true, data: response.data };
//         } catch (e) {
//             console.warn("Runtime messaging failed, falling back to fetch:", e);
//         }
//     }
//     try {
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         if (!res.ok) throw new Error(`HTTP ${res.status}`);
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("maskAndReplace called with text:", text);
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) { console.log("Text already masked, skipping."); return; }
//     if (isProcessing.get(field)) { console.log("Already processing, skipping."); return; }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("Backend result:", result);
//         if (!result.success) { console.error("Backend error:", result.error); return; }

//         const data = result.data;

//         // Highlight if there are entities
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait for highlight duration then replace
//         setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//             }
//         }, HIGHLIGHT_DURATION);

//     } catch (e) {
//         console.error("Error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// Day 18 final update 
// content.js – Adaptive UI Version
// console.log("🔒 PreSendAI: Adaptive Highlighting Active");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 900; 
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;

// // ==================== DYNAMIC CSS ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-adaptive-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: var(--ps-bg, rgba(128, 128, 128, 0.2)) !important;
//             border-bottom: 1.5px solid var(--ps-accent, #6495ED);
//             color: inherit !important;
//             border-radius: 2px;
//             transition: background-color 0.3s ease;
//         }

//         .presendai-flash-active {
//             transition: box-shadow 0.4s ease !important;
//             box-shadow: inset 0 0 4px 2px var(--ps-accent, rgba(100, 149, 237, 0.3)) !important;
//         }
//     `;
//     document.head.appendChild(style);
// }

// // ==================== SMART COLOR ENGINE ====================
// function applyAdaptiveColors(field) {
//     const style = window.getComputedStyle(field);
//     const bgColor = style.backgroundColor;
//     const textColor = style.color;

//     // Extract RGB values
//     const rgb = textColor.match(/\d+/g) || [0, 0, 0];
//     const brightness = (parseInt(rgb[0]) * 299 + parseInt(rgb[1]) * 587 + parseInt(rgb[2]) * 114) / 1000;

//     // If text is bright (Dark Mode), use a light frost highlight
//     // If text is dark (Light Mode), use a soft blue-grey tint
//     if (brightness > 125) {
//         field.style.setProperty('--ps-bg', 'rgba(255, 255, 255, 0.15)');
//         field.style.setProperty('--ps-accent', 'rgba(255, 255, 255, 0.5)');
//     } else {
//         field.style.setProperty('--ps-bg', 'rgba(100, 149, 237, 0.1)');
//         field.style.setProperty('--ps-accent', 'rgba(100, 149, 237, 0.6)');
//     }
// }

// function highlightField(field) {
//     applyAdaptiveColors(field);
//     field.classList.add('presendai-flash-active');
    
//     setTimeout(() => {
//         field.classList.remove('presendai-flash-active');
//     }, HIGHLIGHT_DURATION);
// }

// // ==================== DOM & LOGIC HELPERS ====================

// function getFieldText(field) {
//     return (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA') ? field.value : field.innerText;
// }

// function setFieldText(field, newText) {
//     if (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return (...args) => {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// function saveCursorPosition(field) {
//     if (field.tagName === 'INPUT' || field.tagName === 'TEXTAREA') {
//         return { start: field.selectionStart, end: field.selectionEnd };
//     }
//     const sel = window.getSelection();
//     if (sel.rangeCount > 0) {
//         const range = sel.getRangeAt(0);
//         const preRange = range.cloneRange();
//         preRange.selectNodeContents(field);
//         preRange.setEnd(range.startContainer, range.startOffset);
//         return { offset: preRange.toString().length };
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, text) {
//     if (!saved) return;
//     if (saved.offset !== undefined) {
//         const node = field.firstChild || field;
//         const range = document.createRange();
//         try {
//             range.setStart(node.nodeType === 3 ? node : field, Math.min(saved.offset, text.length));
//             range.collapse(true);
//             const sel = window.getSelection();
//             sel.removeAllRanges();
//             sel.addRange(range);
//         } catch(e) {}
//     } else {
//         field.setSelectionRange(Math.min(saved.start, text.length), Math.min(saved.end, text.length));
//     }
// }

// // ==================== CORE MASKING ENGINE ====================

// async function processField(field) {
//     const text = getFieldText(field);
//     if (!text.trim() || isUpdating || isProcessing.get(field)) return;
//     if (MASK_PLACEHOLDERS.some(p => text.includes(p))) return;

//     isProcessing.set(field, true);
    
//     try {
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         });
//         const data = await res.json();

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field);

//             setTimeout(() => {
//                 const cursor = saveCursorPosition(field);
//                 isUpdating = true;
//                 setFieldText(field, data.masked);
//                 restoreCursorPosition(field, cursor, data.masked);
//                 lastSentText.set(field, data.masked);
//                 isUpdating = false;
//                 isProcessing.set(field, false);
//             }, HIGHLIGHT_DURATION - 200);
//         } else {
//             isProcessing.set(field, false);
//         }
//     } catch (e) {
//         isProcessing.set(field, false);
//     }
// }

// // ==================== EVENT LISTENERS ====================

// function onInput(e) {
//     const field = e.target;
//     if (!field._debouncedProcess) {
//         field._debouncedProcess = debounce(processField, DEBOUNCE_DELAY);
//     }
//     field._debouncedProcess(field);
// }

// function init() {
//     injectHighlightStyles();
//     const attach = () => {
//         document.querySelectorAll('input:not([type="password"]), textarea, [contenteditable="true"]').forEach(f => {
//             if (!trackedFields.has(f)) {
//                 f.addEventListener('input', onInput);
//                 trackedFields.add(f);
//             }
//         });
//     };
//     attach();
//     new MutationObserver(debounce(attach, OBSERVER_DEBOUNCE)).observe(document.body, { childList: true, subtree: true });
// }

// init();




// day 18 code update 

// content.js – Final version with keep‑alive, timeouts, and beautiful highlights
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;                // 1 second pause after typing
// const OBSERVER_DEBOUNCE = 300;               // ms for MutationObserver
// const HIGHLIGHT_DURATION = 800;               // ms – how long highlights stay before replacement
// const MESSAGE_TIMEOUT = 5000;                  // ms – max wait for background response

// // Placeholders (must match MASK_LABELS in masker.py)
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive, no action needed
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;                        // true while we are programmatically updating a field

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;   /* soft yellow */
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     // If the field contains any HTML tags, fallback to flash
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     // Collect all text nodes
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     // Build character‑to‑node map
//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     // Sort entities in reverse order to avoid position shifts
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break; // move to next entity
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     // Also set a background that fades out
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     // Try runtime messaging first (most reliable, bypasses CORS)
//     if (runtime) {
//         try {
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     // Fallback: direct fetch (may be blocked by CORS/Shields, but we try)
//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("🔍 maskAndReplace called with text:", text);
//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         // Highlight if entities exist
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait a bit for user to see highlight, then replace
//         setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//             }
//         }, HIGHLIGHT_DURATION);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }



// day 19 update 

// // content.js – Day 19: Stability Guards
// console.log("🔒 PreSendAI content script loaded – Day 19 (Stability Guards)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;                // 1 second pause after typing
// const OBSERVER_DEBOUNCE = 300;               // ms for MutationObserver
// const HIGHLIGHT_DURATION = 800;               // ms – how long highlights stay before replacement
// const MESSAGE_TIMEOUT = 5000;                  // ms – max wait for background response
// const MAX_TEXT_LENGTH = 5000;                   // characters – don't send longer texts

// // Placeholders (must match MASK_LABELS in masker.py)
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive, no action needed
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;                        // true while we are programmatically updating a field

// // Map to store pending replacement timeouts per field (to cancel if new input arrives)
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;   /* soft yellow */
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     // If the field contains any HTML tags, fallback to flash
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     // Collect all text nodes
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     // Build character‑to‑node map
//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     // Sort entities in reverse order to avoid position shifts
//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break; // move to next entity
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     // Also set a background that fades out
//     field.style.backgroundColor = '#FFD700';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     // Try runtime messaging first (most reliable, bypasses CORS)
//     if (runtime) {
//         try {
//             // Check if runtime is still connected (extension not reloaded)
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     // Fallback: direct fetch (may be blocked by CORS/Shields, but we try)
//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("🔍 maskAndReplace called with text:", text);

//     // 1. Skip empty text
//     if (!text.trim()) return;

//     // 2. Skip already masked text
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }

//     // 3. Max length guard
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }

//     // 4. Skip if already processing
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     // 5. Cancel any pending replacement timeout for this field
//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         // Highlight if entities exist
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait a bit for user to see highlight, then replace
//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// day 19 final code 

// content.js – Day 19: Stability Guards
// console.log("🔒 PreSendAI content script loaded – Day 19 (Stability Guards)");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;                // 1 second pause after typing
// const OBSERVER_DEBOUNCE = 300;               // ms for MutationObserver
// const HIGHLIGHT_DURATION = 800;               // ms – how long highlights stay before replacement
// const MESSAGE_TIMEOUT = 5000;                  // ms – max wait for background response
// const MAX_TEXT_LENGTH = 5000;                   // characters – don't send longer texts

// // Placeholders (must match MASK_LABELS in masker.py)
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive, no action needed
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;                        // true while we are programmatically updating a field

// // Map to store pending replacement timeouts per field (to cancel if new input arrives)
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }



// day 20 update 
// // content.js – Final version with enable/disable toggle (Day 20)
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";
// const DEBOUNCE_DELAY = 1000;                // 1 second pause after typing
// const OBSERVER_DEBOUNCE = 300;               // ms for MutationObserver
// const HIGHLIGHT_DURATION = 800;               // ms – how long highlights stay before replacement
// const MESSAGE_TIMEOUT = 5000;                  // ms – max wait for background response
// const MAX_TEXT_LENGTH = 5000;                   // characters – don't send longer texts

// // Placeholders (must match MASK_LABELS in masker.py)
// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE (Day 20) ====================
// let extensionEnabled = true; // default

// if (runtime) {
//     // Load initial state from storage
//     chrome.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     // Listen for changes from popup
//     chrome.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive, no action needed
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;                        // true while we are programmatically updating a field

// // Map to store pending replacement timeouts per field (to cancel if new input arrives)
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     // Day 20: respect enabled flag
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     // Cancel any pending replacement for this field
//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         // Highlight if entities exist
//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Wait a bit for user to see highlight, then replace
//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     // Day 20: respect enabled flag
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// day 21 update 

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "https://localhost:5000/scan";
// const DEBOUNCE_DELAY = 300;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 300;
// const MESSAGE_TIMEOUT = 10000;
// const MAX_TEXT_LENGTH = 5000;

// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE (Day 20) ====================
// let extensionEnabled = true;

// if (runtime) {
//     browser.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     browser.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//      console.log("🟢 onInput triggered on", event.target);
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }

// day 21 final fix 
// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "https://localhost:5000/scan";
// const DEBOUNCE_DELAY = 300;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 300;
// const MESSAGE_TIMEOUT = 10000;
// const MAX_TEXT_LENGTH = 5000;

// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE ====================
// let extensionEnabled = true;

// if (runtime) {
//     browser.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     browser.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // Optional: periodic ping to keep worker awake
// if (runtime) {
//     setInterval(() => {
//         runtime.sendMessage({ action: "ping" }, () => {});
//     }, 20000);
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') field.value = newText;
//     else if (field.isContentEditable) field.innerText = newText;
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);

//                     // 🔥 CRITICAL: Dispatch input event to force editor update
//                     field.dispatchEvent(new Event('input', { bubbles: true }));

//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     console.log("🟢 onInput triggered on", event.target);
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// day 21 final update 

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "https://localhost:5000/scan";
// const DEBOUNCE_DELAY = 300;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 300;
// const MESSAGE_TIMEOUT = 10000;
// const MAX_TEXT_LENGTH = 1000000; // Increased to handle long documents

// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE ====================
// let extensionEnabled = true;

// if (runtime) {
//     browser.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     browser.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // Optional: periodic ping to keep worker awake
// if (runtime) {
//     setInterval(() => {
//         runtime.sendMessage({ action: "ping" }, () => {});
//     }, 20000);
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// // ==================== ENHANCED SETFIELDTEXT WITH EDITOR DETECTION ====================
// function setFieldText(field, newText) {
//     console.log("🛠️ setFieldText called on", field.tagName, field.className);
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         console.log("  → Set value on input/textarea, new value:", field.value);
//         return;
//     }

//     if (!field.isContentEditable) {
//         console.log("  → Not contenteditable, aborting");
//         return;
//     }

//     // Try to detect and use the editor's internal API
//     try {
//         // Quill (Gemini)
//         if (field.__quill) {
//             console.log("  → Found __quill, using quill.setText()");
//             field.__quill.setText(newText);
//             return;
//         }
//         if (field._quill) {
//             console.log("  → Found _quill, using quill.setText()");
//             field._quill.setText(newText);
//             return;
//         }
//         // Check for Quill container (sometimes instance is on parent)
//         let quillInstance = field.closest('.ql-container')?.__quill || field.closest('.ql-container')?._quill;
//         if (quillInstance) {
//             console.log("  → Found Quill instance on parent");
//             quillInstance.setText(newText);
//             return;
//         }

//         // ProseMirror (ChatGPT)
//         if (field.closest('.ProseMirror') || field.classList.contains('ProseMirror')) {
//             console.log("  → Detected ProseMirror");
//             // Try to get view from various locations
//             const view = field._view || field.view || field.parentElement?._view || field.parentElement?.view;
//             if (view) {
//                 console.log("  → Found ProseMirror view, using transaction");
//                 const { state } = view;
//                 const tr = state.tr;
//                 tr.replaceWith(0, state.doc.content.size, state.schema.text(newText));
//                 view.dispatch(tr);
//                 return;
//             } else {
//                 console.log("  → No view found, falling back to DOM");
//             }
//         }

//         // Fallback: replace innerText and dispatch multiple events
//         console.log("  → Using fallback: setting innerText and dispatching events");
//         field.innerText = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         field.dispatchEvent(new Event('change', { bubbles: true }));
//         field.dispatchEvent(new Event('blur')); // sometimes blur triggers a save
//         setTimeout(() => field.focus(), 10); // refocus to ensure cursor
//         console.log("  → After fallback, field.innerText =", field.innerText);
//     } catch (e) {
//         console.error("❌ Error in setFieldText:", e);
//         // Ultimate fallback
//         field.innerText = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     console.log("🟢 onInput triggered on", event.target);
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;
//     const field = event.target;
//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// day 22 update 

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔒 PreSendAI content script loaded – Final Version");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "https://localhost:5000/scan";
// const DEBOUNCE_DELAY = 300;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 300;
// const MESSAGE_TIMEOUT = 10000;
// const MAX_TEXT_LENGTH = 20000; // Increased to handle long documents

// const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[AADHAAR]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE ====================
// let extensionEnabled = true;

// if (runtime) {
//     browser.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     browser.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// // Optional: periodic ping to keep worker awake
// if (runtime) {
//     setInterval(() => {
//         runtime.sendMessage({ action: "ping" }, () => {});
//     }, 20000);
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// // ==================== ENHANCED SETFIELDTEXT WITH EDITOR DETECTION ====================
// function setFieldText(field, newText) {
//     console.log("🛠️ setFieldText called on", field.tagName, field.className);
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         console.log("  → Set value on input/textarea, new value:", field.value);
//         return;
//     }

//     if (!field.isContentEditable) {
//         console.log("  → Not contenteditable, aborting");
//         return;
//     }

//     // Try to detect and use the editor's internal API
//     try {
//         // Quill (Gemini)
//         if (field.__quill) {
//             console.log("  → Found __quill, using quill.setText()");
//             field.__quill.setText(newText);
//             return;
//         }
//         if (field._quill) {
//             console.log("  → Found _quill, using quill.setText()");
//             field._quill.setText(newText);
//             return;
//         }
//         // Check for Quill container (sometimes instance is on parent)
//         let quillInstance = field.closest('.ql-container')?.__quill || field.closest('.ql-container')?._quill;
//         if (quillInstance) {
//             console.log("  → Found Quill instance on parent");
//             quillInstance.setText(newText);
//             return;
//         }

//         // ProseMirror (ChatGPT)
//         if (field.closest('.ProseMirror') || field.classList.contains('ProseMirror')) {
//             console.log("  → Detected ProseMirror");
//             // Try to get view from various locations
//             const view = field._view || field.view || field.parentElement?._view || field.parentElement?.view;
//             if (view) {
//                 console.log("  → Found ProseMirror view, using transaction");
//                 const { state } = view;
//                 const tr = state.tr;
//                 tr.replaceWith(0, state.doc.content.size, state.schema.text(newText));
//                 view.dispatch(tr);
//                 return;
//             } else {
//                 console.log("  → No view found, falling back to DOM");
//             }
//         }

//         // Fallback: replace innerText and dispatch multiple events
//         console.log("  → Using fallback: setting innerText and dispatching events");
//         field.innerText = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         field.dispatchEvent(new Event('change', { bubbles: true }));
//         field.dispatchEvent(new Event('blur')); // sometimes blur triggers a save
//         setTimeout(() => field.focus(), 10); // refocus to ensure cursor
//         console.log("  → After fallback, field.innerText =", field.innerText);
//     } catch (e) {
//         console.error("❌ Error in setFieldText:", e);
//         // Ultimate fallback
//         field.innerText = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//     }
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Replacing with:", data.masked);
//                     isUpdating = true;
//                     setFieldText(field, data.masked);
//                     restoreCursorPosition(field, cursorSaved, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // Helper to find the actual editor element from a clipboard event
// function getEditorFromClipboard(clipboard) {
//     const container = clipboard.closest('.ql-container');
//     if (container) {
//         return container.querySelector('.ql-editor');
//     }
//     return null;
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     console.log("🟢 onInput triggered on", event.target);
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;

//     let field = event.target;
//     // If the event is from the clipboard, map to the actual editor
//     if (field.classList && field.classList.contains('ql-clipboard')) {
//         const editor = getEditorFromClipboard(field);
//         if (editor) {
//             console.log("  → Mapped clipboard to editor:", editor);
//             field = editor;
//         } else {
//             console.log("  → Could not find editor for clipboard, ignoring");
//             return;
//         }
//     }

//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// // day 22 final update 

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔒 PreSendAI content script loaded – Final Version with span‑based masking");

// // ==================== CONFIGURATION ====================
// const BACKEND_URL = "http://localhost:5000/scan";  // <-- FIXED: http, not https
// const DEBOUNCE_DELAY = 300;
// const OBSERVER_DEBOUNCE = 300;
// const HIGHLIGHT_DURATION = 300;
// const MESSAGE_TIMEOUT = 10000;
// const MAX_TEXT_LENGTH = 200000;

// // Mask labels (mirror of backend MASK_LABELS)
// const MASK_LABELS = {
//     PERSON: "[NAME]",
//     EMAIL: "[EMAIL]",
//     PHONE: "[PHONE]",
//     ID: "[ID]",
//     AADHAAR: "[AADHAAR]",
//     CARD: "[CARD]",
//     ADDRESS: "[ADDRESS]",
//     ORG: "[ORG]"
// };
// const MASK_PLACEHOLDERS = Object.values(MASK_LABELS);

// // ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
// const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
//                 (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
// if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// // ==================== ENABLED STATE ====================
// let extensionEnabled = true;

// if (runtime) {
//     browser.storage.local.get('enabled', (data) => {
//         extensionEnabled = data.enabled !== false;
//         console.log(`Extension enabled: ${extensionEnabled}`);
//     });

//     browser.storage.onChanged.addListener((changes, area) => {
//         if (area === 'local' && changes.enabled) {
//             extensionEnabled = changes.enabled.newValue !== false;
//             console.log(`Extension enabled changed to: ${extensionEnabled}`);
//         }
//     });
// }

// // ==================== KEEP‑ALIVE ====================
// if (runtime) {
//     try {
//         const port = runtime.connect({ name: "presendai-keepalive" });
//         port.onMessage.addListener((msg) => {
//             if (msg.type === "ping") {
//                 // Just a keep‑alive
//             }
//         });
//     } catch (e) {
//         console.warn("⚠️ Could not establish keep‑alive port:", e);
//     }
// }

// if (runtime) {
//     setInterval(() => {
//         runtime.sendMessage({ action: "ping" }, () => {});
//     }, 20000);
// }

// // ==================== STATE TRACKING ====================
// const trackedFields = new WeakSet();
// const lastSentText = new WeakMap();
// const isProcessing = new WeakMap();
// let isUpdating = false;
// const pendingTimeouts = new WeakMap();

// // ==================== HELPER FUNCTIONS ====================
// function isAlreadyMasked(text) {
//     return MASK_PLACEHOLDERS.some(p => text.includes(p));
// }

// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = element.type.toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value;
//     if (field.isContentEditable) return field.innerText;
//     return '';
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (field.contains(range.startContainer)) {
//             const preCaretRange = range.cloneRange();
//             preCaretRange.selectNodeContents(field);
//             preCaretRange.setEnd(range.startContainer, range.startOffset);
//             return { type: 'contenteditable', offset: preCaretRange.toString().length };
//         }
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     const tag = field.tagName.toLowerCase();
//     if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//         const newLength = newText.length;
//         field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
//     } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//         const newOffset = Math.min(saved.offset, newText.length);
//         const textNode = field.firstChild;
//         if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//             const range = document.createRange();
//             range.setStart(textNode, newOffset);
//             range.collapse(true);
//             window.getSelection().removeAllRanges();
//             window.getSelection().addRange(range);
//         }
//     }
// }

// // ==================== HIGHLIGHT ENGINE (unchanged) ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         .presendai-highlight {
//             background-color: #fff2b0 !important;
//             color: #000 !important;
//             border-radius: 4px;
//             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
//             transition: background-color 0.2s, box-shadow 0.2s;
//             padding: 0 2px;
//             margin: 0 -2px;
//         }
//         .presendai-flash {
//             animation: presendai-flash-bg 0.6s ease;
//         }
//         @keyframes presendai-flash-bg {
//             0% { background-color: inherit; }
//             50% { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     const highlights = field.querySelectorAll('.presendai-highlight');
//     highlights.forEach(span => {
//         const parent = span.parentNode;
//         parent.replaceChild(document.createTextNode(span.textContent), span);
//         parent.normalize();
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     console.log("🎨 Applying per‑word highlight to contenteditable");
//     if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
//         console.warn("⚠️ Field contains HTML tags – falling back to field flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);
//     for (const ent of sorted) {
//         const { start, end } = ent;
//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;
//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const span = document.createElement('span');
//                 span.className = 'presendai-highlight';
//                 span.textContent = middle;

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break;
//             }
//         }
//     }
//     return true;
// }

// function highlightFieldFlash(field) {
//     field.classList.add('presendai-flash');
//     setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
//     field.style.backgroundColor = '#fff2b0';
//     setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
// }

// function highlightField(field, entities) {
//     if (!entities || entities.length === 0) return;
//     try {
//         if (field.isContentEditable) {
//             const success = highlightContentEditablePlain(field, entities);
//             if (!success) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }

// // ==================== NEW: SPAN‑BASED MASKING FOR CONTENTEDITABLE ====================
// function replaceSpansInContentEditable(field, entities) {
//     // 1. Get all text nodes with global positions
//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while (node = walker.nextNode()) textNodes.push(node);

//     let currentPos = 0;
//     const nodeMap = textNodes.map(node => {
//         const start = currentPos;
//         const end = currentPos + node.nodeValue.length;
//         currentPos = end;
//         return { node, start, end };
//     });

//     // 2. Sort entities from end to start to avoid offset shifts
//     const sorted = [...entities].sort((a, b) => b.start - a.start);

//     for (const ent of sorted) {
//         const { start, end, label } = ent;
//         const replacement = MASK_LABELS[label] || "[REDACTED]";

//         for (const item of nodeMap) {
//             if (start >= item.end) continue;
//             if (end <= item.start) break;

//             const overlapStart = Math.max(start, item.start);
//             const overlapEnd = Math.min(end, item.end);
//             if (overlapStart < overlapEnd) {
//                 const node = item.node;
//                 const text = node.nodeValue;
//                 const before = text.substring(0, overlapStart - item.start);
//                 const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
//                 const after = text.substring(overlapEnd - item.start);

//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(document.createTextNode(replacement)); // plain text replacement
//                 if (after) fragment.appendChild(document.createTextNode(after));

//                 node.parentNode.replaceChild(fragment, node);
//                 break; // Move to next entity (spans are non‑overlapping after resolution)
//             }
//         }
//     }

//     // 3. Normalize to merge adjacent text nodes
//     field.normalize();
// }

// function applyMaskToField(field, originalText, entities, maskedText) {
//     const tag = field.tagName.toLowerCase();

//     // Simple case: input or textarea
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = maskedText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         return;
//     }

//     // Contenteditable: replace only entity spans
//     if (!field.isContentEditable) return;

//     const cursor = saveCursorPosition(field);
//     replaceSpansInContentEditable(field, entities);
//     if (cursor) restoreCursorPosition(field, cursor, field.innerText);

//     // Dispatch events to notify the editor
//     field.dispatchEvent(new Event('input', { bubbles: true }));
//     field.dispatchEvent(new Event('change', { bubbles: true }));
// }

// // ==================== BACKEND COMMUNICATION ====================
// async function sendToBackend(text) {
//     if (runtime) {
//         try {
//             if (!runtime.id) {
//                 throw new Error("Extension context invalidated");
//             }
//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
//                         if (chrome.runtime.lastError) {
//                             reject(new Error(chrome.runtime.lastError.message));
//                         } else {
//                             resolve(response);
//                         }
//                     });
//                 }),
//                 new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
//             ]);
//             return { success: true, data: result.data };
//         } catch (e) {
//             console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
//         }
//     }

//     try {
//         const controller = new AbortController();
//         const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text }),
//             signal: controller.signal
//         });
//         clearTimeout(timeoutId);
//         if (!res.ok) {
//             const errText = await res.text();
//             throw new Error(`HTTP ${res.status}: ${errText}`);
//         }
//         return { success: true, data: await res.json() };
//     } catch (e) {
//         return { success: false, error: e.message };
//     }
// }

// // ==================== CORE MASKING FUNCTION ====================
// async function maskAndReplace(field, text) {
//     if (!extensionEnabled) {
//         console.log("Extension disabled, not masking");
//         return;
//     }

//     console.log("🔍 maskAndReplace called with text:", text);

//     if (!text.trim()) return;
//     if (isAlreadyMasked(text)) {
//         console.log("⏭️ Text already masked, skipping.");
//         return;
//     }
//     if (text.length > MAX_TEXT_LENGTH) {
//         console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
//         return;
//     }
//     if (isProcessing.get(field)) {
//         console.log("⏳ Already processing this field, skipping duplicate.");
//         return;
//     }

//     if (pendingTimeouts.has(field)) {
//         clearTimeout(pendingTimeouts.get(field));
//         pendingTimeouts.delete(field);
//     }

//     const cursorSaved = saveCursorPosition(field);
//     console.log("📌 Cursor saved:", cursorSaved);
//     isProcessing.set(field, true);

//     try {
//         const result = await sendToBackend(text);
//         console.log("📦 Backend result:", result);
//         if (!result.success) {
//             console.error("❌ Backend error:", result.error);
//             return;
//         }

//         const data = result.data;

//         if (data.entities && data.entities.length > 0) {
//             highlightField(field, data.entities);
//         }

//         // Apply mask using span‑based replacement for contenteditable,
//         // and direct value for simple inputs
//         const timeoutId = setTimeout(() => {
//             try {
//                 if (data.status === 'ok' && data.masked && data.masked !== text) {
//                     console.log("✏️ Applying mask with:", data.masked);
//                     isUpdating = true;
//                     applyMaskToField(field, text, data.entities, data.masked);
//                     isUpdating = false;
//                     lastSentText.set(field, data.masked);
//                 } else {
//                     console.log("ℹ️ No change needed");
//                     lastSentText.set(field, data.masked || text);
//                 }
//             } catch (e) {
//                 console.error("❌ Error during replacement:", e);
//             } finally {
//                 isProcessing.set(field, false);
//                 pendingTimeouts.delete(field);
//             }
//         }, HIGHLIGHT_DURATION);

//         pendingTimeouts.set(field, timeoutId);

//     } catch (e) {
//         console.error("❌ Fatal error in maskAndReplace:", e);
//         isProcessing.set(field, false);
//     }
// }

// // Helper to find the actual editor element from a clipboard event
// function getEditorFromClipboard(clipboard) {
//     const container = clipboard.closest('.ql-container');
//     if (container) {
//         return container.querySelector('.ql-editor');
//     }
//     return null;
// }

// // ==================== INPUT HANDLER ====================
// function onInput(event) {
//     console.log("🟢 onInput triggered on", event.target);
//     if (!extensionEnabled) {
//         console.log("Extension disabled, ignoring input");
//         return;
//     }
//     if (isUpdating) return;

//     let field = event.target;
//     // If the event is from the clipboard, map to the actual editor
//     if (field.classList && field.classList.contains('ql-clipboard')) {
//         const editor = getEditorFromClipboard(field);
//         if (editor) {
//             console.log("  → Mapped clipboard to editor:", editor);
//             field = editor;
//         } else {
//             console.log("  → Could not find editor for clipboard, ignoring");
//             return;
//         }
//     }

//     const currentText = getFieldText(field);
//     const lastSent = lastSentText.get(field);
//     if (currentText === lastSent) return;

//     if (!field._debouncedMask) {
//         field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
//     }
//     field._debouncedMask(field, currentText);
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field) {
//     if (!trackedFields.has(field)) {
//         field.addEventListener('input', onInput);
//         trackedFields.add(field);
//         console.log('👂 Listening to', field);
//     }
// }

// function scanAndAttach() {
//     const selectors = [
//         'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
//         'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
//         'input[type="number"]', 'textarea', '[contenteditable="true"]'
//     ];
//     document.querySelectorAll(selectors.join(',')).forEach(attachListener);
// }

// // ==================== MUTATION OBSERVER ====================
// let observerTimeout;
// function handleMutations() {
//     clearTimeout(observerTimeout);
//     observerTimeout = setTimeout(() => {
//         console.log("🔍 Scanning for dynamically added fields...");
//         scanAndAttach();
//     }, OBSERVER_DEBOUNCE);
// }

// function observeDynamicFields() {
//     new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
//     console.log("👁️ MutationObserver active");
// }

// function debounce(func, wait) {
//     let timeout;
//     return function(...args) {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => func(...args), wait);
//     };
// }

// // ==================== INITIALISATION ====================
// injectHighlightStyles();
// if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
// } else {
//     scanAndAttach();
//     observeDynamicFields();
// }


// final code
if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
    var browser = chrome;
}
console.log("🔒 PreSendAI content script loaded – Final Version with span‑based masking");

// ==================== CONFIGURATION ====================
const BACKEND_URL = "http://localhost:5000/scan";  // Use HTTP, not HTTPS
const DEBOUNCE_DELAY = 300;
const OBSERVER_DEBOUNCE = 300;
const HIGHLIGHT_DURATION = 300;
const MESSAGE_TIMEOUT = 10000;
const MAX_TEXT_LENGTH = 200000;  // Must match backend limit (200000)

// Mask labels (mirror of backend MASK_LABELS)
const MASK_LABELS = {
    PERSON: "[NAME]",
    EMAIL: "[EMAIL]",
    PHONE: "[PHONE]",
    ID: "[ID]",
    AADHAAR: "[AADHAAR]",
    CARD: "[CARD]",
    ADDRESS: "[ADDRESS]",
    ORG: "[ORG]"
};
const MASK_PLACEHOLDERS = Object.values(MASK_LABELS);

// ==================== CROSS‑BROWSER RUNTIME DETECTION ====================
const runtime = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime :
                (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
if (!runtime) console.warn("⚠️ No extension runtime API found. Direct fetch will be used (may be blocked by CORS).");

// ==================== ENABLED STATE ====================
let extensionEnabled = true;

if (runtime) {
    browser.storage.local.get('enabled', (data) => {
        extensionEnabled = data.enabled !== false;
        console.log(`Extension enabled: ${extensionEnabled}`);
    });

    browser.storage.onChanged.addListener((changes, area) => {
        if (area === 'local' && changes.enabled) {
            extensionEnabled = changes.enabled.newValue !== false;
            console.log(`Extension enabled changed to: ${extensionEnabled}`);
        }
    });
}

// ==================== KEEP‑ALIVE ====================
if (runtime) {
    try {
        const port = runtime.connect({ name: "presendai-keepalive" });
        port.onMessage.addListener((msg) => {
            if (msg.type === "ping") {
                // Just a keep‑alive
            }
        });
    } catch (e) {
        console.warn("⚠️ Could not establish keep‑alive port:", e);
    }
}

if (runtime) {
    setInterval(() => {
        runtime.sendMessage({ action: "ping" }, () => {});
    }, 20000);
}

// ==================== STATE TRACKING ====================
const trackedFields = new WeakSet();
const lastSentText = new WeakMap();
const isProcessing = new WeakMap();
let isUpdating = false;
const pendingTimeouts = new WeakMap();

// ==================== HELPER FUNCTIONS ====================
function isAlreadyMasked(text) {
    return MASK_PLACEHOLDERS.some(p => text.includes(p));
}

function isEditableField(element) {
    if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
    const tag = element.tagName.toLowerCase();
    if (tag === 'input') {
        const type = element.type.toLowerCase();
        return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
    }
    if (tag === 'textarea') return true;
    if (element.isContentEditable) return true;
    return false;
}

function getFieldText(field) {
    const tag = field.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') return field.value;
    if (field.isContentEditable) return field.innerText;
    return '';
}

// ==================== CURSOR PRESERVATION ====================
function saveCursorPosition(field) {
    const tag = field.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') {
        return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
    }
    if (field.isContentEditable) {
        const sel = window.getSelection();
        if (sel.rangeCount === 0) return null;
        const range = sel.getRangeAt(0);
        if (field.contains(range.startContainer)) {
            const preCaretRange = range.cloneRange();
            preCaretRange.selectNodeContents(field);
            preCaretRange.setEnd(range.startContainer, range.startOffset);
            return { type: 'contenteditable', offset: preCaretRange.toString().length };
        }
    }
    return null;
}

function restoreCursorPosition(field, saved, newText) {
    if (!saved) return;
    const tag = field.tagName.toLowerCase();
    if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
        const newLength = newText.length;
        field.setSelectionRange(Math.min(saved.start, newLength), Math.min(saved.end, newLength));
    } else if (saved.type === 'contenteditable' && field.isContentEditable) {
        const newOffset = Math.min(saved.offset, newText.length);
        const textNode = field.firstChild;
        if (textNode && textNode.nodeType === Node.TEXT_NODE) {
            const range = document.createRange();
            range.setStart(textNode, newOffset);
            range.collapse(true);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
        }
    }
}

// ==================== HIGHLIGHT ENGINE ====================
function injectHighlightStyles() {
    const styleId = 'presendai-highlight-styles';
    if (document.getElementById(styleId)) return;
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
        .presendai-highlight {
            background-color: #fff2b0 !important;
            color: #000 !important;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: background-color 0.2s, box-shadow 0.2s;
            padding: 0 2px;
            margin: 0 -2px;
        }
        .presendai-flash {
            animation: presendai-flash-bg 0.6s ease;
        }
        @keyframes presendai-flash-bg {
            0% { background-color: inherit; }
            50% { background-color: #fff2b0; }
            100% { background-color: inherit; }
        }
    `;
    document.head.appendChild(style);
}

function removeHighlights(field) {
    if (!field.isContentEditable) return;
    const highlights = field.querySelectorAll('.presendai-highlight');
    highlights.forEach(span => {
        const parent = span.parentNode;
        parent.replaceChild(document.createTextNode(span.textContent), span);
        parent.normalize();
    });
}

function highlightContentEditablePlain(field, entities) {
    console.log("🎨 Applying per‑word highlight to contenteditable");
    if (/<[^>]*>/.test(field.innerHTML) && field.innerHTML.indexOf('<span class="presendai-highlight">') === -1) {
        console.warn("⚠️ Field contains HTML tags – falling back to field flash");
        return false;
    }

    removeHighlights(field);

    const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) textNodes.push(node);

    let currentPos = 0;
    const nodeMap = textNodes.map(node => {
        const start = currentPos;
        const end = currentPos + node.nodeValue.length;
        currentPos = end;
        return { node, start, end };
    });

    const sorted = [...entities].sort((a, b) => b.start - a.start);
    for (const ent of sorted) {
        const { start, end } = ent;
        for (const item of nodeMap) {
            if (start >= item.end) continue;
            if (end <= item.start) break;
            const overlapStart = Math.max(start, item.start);
            const overlapEnd = Math.min(end, item.end);
            if (overlapStart < overlapEnd) {
                const node = item.node;
                const text = node.nodeValue;
                const before = text.substring(0, overlapStart - item.start);
                const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
                const after = text.substring(overlapEnd - item.start);

                const span = document.createElement('span');
                span.className = 'presendai-highlight';
                span.textContent = middle;

                const fragment = document.createDocumentFragment();
                if (before) fragment.appendChild(document.createTextNode(before));
                fragment.appendChild(span);
                if (after) fragment.appendChild(document.createTextNode(after));

                node.parentNode.replaceChild(fragment, node);
                break;
            }
        }
    }
    return true;
}

function highlightFieldFlash(field) {
    field.classList.add('presendai-flash');
    setTimeout(() => field.classList.remove('presendai-flash'), HIGHLIGHT_DURATION);
    field.style.backgroundColor = '#fff2b0';
    setTimeout(() => field.style.backgroundColor = '', HIGHLIGHT_DURATION);
}

function highlightField(field, entities) {
    if (!entities || entities.length === 0) return;
    try {
        if (field.isContentEditable) {
            const success = highlightContentEditablePlain(field, entities);
            if (!success) highlightFieldFlash(field);
        } else {
            highlightFieldFlash(field);
        }
    } catch (e) {
        console.error("❌ Highlight error, falling back to flash:", e);
        highlightFieldFlash(field);
    }
}

// ==================== SPAN‑BASED MASKING FOR CONTENTEDITABLE ====================
function replaceSpansInContentEditable(field, entities) {
    // 1. Get all text nodes with global positions
    const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    let node;
    while (node = walker.nextNode()) textNodes.push(node);

    let currentPos = 0;
    const nodeMap = textNodes.map(node => {
        const start = currentPos;
        const end = currentPos + node.nodeValue.length;
        currentPos = end;
        return { node, start, end };
    });

    // 2. Sort entities from end to start to avoid offset shifts
    const sorted = [...entities].sort((a, b) => b.start - a.start);

    for (const ent of sorted) {
        const { start, end, label } = ent;
        const replacement = MASK_LABELS[label] || "[REDACTED]";

        for (const item of nodeMap) {
            if (start >= item.end) continue;
            if (end <= item.start) break;

            const overlapStart = Math.max(start, item.start);
            const overlapEnd = Math.min(end, item.end);
            if (overlapStart < overlapEnd) {
                const node = item.node;
                const text = node.nodeValue;
                const before = text.substring(0, overlapStart - item.start);
                const middle = text.substring(overlapStart - item.start, overlapEnd - item.start);
                const after = text.substring(overlapEnd - item.start);

                const fragment = document.createDocumentFragment();
                if (before) fragment.appendChild(document.createTextNode(before));
                fragment.appendChild(document.createTextNode(replacement)); // plain text replacement
                if (after) fragment.appendChild(document.createTextNode(after));

                node.parentNode.replaceChild(fragment, node);
                break; // Move to next entity (spans are non‑overlapping after resolution)
            }
        }
    }

    // 3. Normalize to merge adjacent text nodes
    field.normalize();
}

function applyMaskToField(field, originalText, entities, maskedText) {
    const tag = field.tagName.toLowerCase();

    // Simple case: input or textarea
    if (tag === 'input' || tag === 'textarea') {
        field.value = maskedText;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        return;
    }

    // Contenteditable: replace only entity spans
    if (!field.isContentEditable) return;

    const cursor = saveCursorPosition(field);
    replaceSpansInContentEditable(field, entities);
    if (cursor) restoreCursorPosition(field, cursor, field.innerText);

    // Dispatch events to notify the editor
    field.dispatchEvent(new Event('input', { bubbles: true }));
    field.dispatchEvent(new Event('change', { bubbles: true }));
}

// ==================== BACKEND COMMUNICATION ====================
async function sendToBackend(text) {
    if (runtime) {
        try {
            if (!runtime.id) {
                throw new Error("Extension context invalidated");
            }
            const result = await Promise.race([
                new Promise((resolve, reject) => {
                    runtime.sendMessage({ action: "maskText", text, url: BACKEND_URL }, (response) => {
                        if (chrome.runtime.lastError) {
                            reject(new Error(chrome.runtime.lastError.message));
                        } else {
                            resolve(response);
                        }
                    });
                }),
                new Promise((_, reject) => setTimeout(() => reject(new Error("⏱️ Runtime message timeout")), MESSAGE_TIMEOUT))
            ]);
            // result should be { success: true, data: {...} } or { success: false, error: ... }
            return { success: true, data: result.data };
        } catch (e) {
            console.warn("⚠️ Runtime messaging failed, falling back to fetch:", e);
        }
    }

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
        const res = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`HTTP ${res.status}: ${errText}`);
        }
        const data = await res.json();
        return { success: true, data };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

// ==================== CORE MASKING FUNCTION ====================
async function maskAndReplace(field, text) {
    if (!extensionEnabled) {
        console.log("Extension disabled, not masking");
        return;
    }

    console.log("🔍 maskAndReplace called with text:", text.substring(0, 100) + "...");

    if (!text.trim()) return;
    if (isAlreadyMasked(text)) {
        console.log("⏭️ Text already masked, skipping.");
        return;
    }
    if (text.length > MAX_TEXT_LENGTH) {
        console.warn(`⚠️ Text too long (${text.length} > ${MAX_TEXT_LENGTH}), skipping.`);
        return;
    }
    if (isProcessing.get(field)) {
        console.log("⏳ Already processing this field, skipping duplicate.");
        return;
    }

    if (pendingTimeouts.has(field)) {
        clearTimeout(pendingTimeouts.get(field));
        pendingTimeouts.delete(field);
    }

    const cursorSaved = saveCursorPosition(field);
    console.log("📌 Cursor saved:", cursorSaved);
    isProcessing.set(field, true);

    try {
        const result = await sendToBackend(text);
        console.log("📦 Backend result (raw):", result);

        // --- Enhanced validation ---
        if (!result || typeof result !== 'object') {
            console.error("❌ Invalid result from sendToBackend:", result);
            return;
        }
        if (!result.success) {
            console.error("❌ Backend error:", result.error);
            return;
        }
        if (!result.data || typeof result.data !== 'object') {
            console.error("❌ Backend returned no data or invalid data:", result.data);
            return;
        }

        const data = result.data;
        console.log("📦 Parsed data:", data);

        if (data.entities && data.entities.length > 0) {
            highlightField(field, data.entities);
        }

        const timeoutId = setTimeout(() => {
            try {
                if (data.status === 'ok' && data.masked && data.masked !== text) {
                    console.log("✏️ Applying mask with:", data.masked.substring(0, 100) + "...");
                    isUpdating = true;
                    applyMaskToField(field, text, data.entities, data.masked);
                    isUpdating = false;
                    lastSentText.set(field, data.masked);
                } else {
                    console.log("ℹ️ No change needed (masked same as original or status not ok)");
                    lastSentText.set(field, data.masked || text);
                }
            } catch (e) {
                console.error("❌ Error during replacement:", e);
            } finally {
                isProcessing.set(field, false);
                pendingTimeouts.delete(field);
            }
        }, HIGHLIGHT_DURATION);

        pendingTimeouts.set(field, timeoutId);

    } catch (e) {
        console.error("❌ Fatal error in maskAndReplace:", e);
        isProcessing.set(field, false);
    }
}

// Helper to find the actual editor element from a clipboard event
function getEditorFromClipboard(clipboard) {
    const container = clipboard.closest('.ql-container');
    if (container) {
        return container.querySelector('.ql-editor');
    }
    return null;
}

// ==================== INPUT HANDLER ====================
function onInput(event) {
    console.log("🟢 onInput triggered on", event.target);
    if (!extensionEnabled) {
        console.log("Extension disabled, ignoring input");
        return;
    }
    if (isUpdating) return;

    let field = event.target;
    // If the event is from the clipboard, map to the actual editor
    if (field.classList && field.classList.contains('ql-clipboard')) {
        const editor = getEditorFromClipboard(field);
        if (editor) {
            console.log("  → Mapped clipboard to editor:", editor);
            field = editor;
        } else {
            console.log("  → Could not find editor for clipboard, ignoring");
            return;
        }
    }

    const currentText = getFieldText(field);
    const lastSent = lastSentText.get(field);
    if (currentText === lastSent) return;

    if (!field._debouncedMask) {
        field._debouncedMask = debounce((f, t) => maskAndReplace(f, t), DEBOUNCE_DELAY);
    }
    field._debouncedMask(field, currentText);
}

// ==================== ATTACH LISTENERS ====================
function attachListener(field) {
    if (!trackedFields.has(field)) {
        field.addEventListener('input', onInput);
        trackedFields.add(field);
        console.log('👂 Listening to', field);
    }
}

function scanAndAttach() {
    const selectors = [
        'input[type="text"]', 'input[type="search"]', 'input[type="tel"]',
        'input[type="url"]', 'input[type="email"]', 'input[type="password"]',
        'input[type="number"]', 'textarea', '[contenteditable="true"]'
    ];
    document.querySelectorAll(selectors.join(',')).forEach(attachListener);
}

// ==================== MUTATION OBSERVER ====================
let observerTimeout;
function handleMutations() {
    clearTimeout(observerTimeout);
    observerTimeout = setTimeout(() => {
        console.log("🔍 Scanning for dynamically added fields...");
        scanAndAttach();
    }, OBSERVER_DEBOUNCE);
}

function observeDynamicFields() {
    new MutationObserver(handleMutations).observe(document.body, { childList: true, subtree: true });
    console.log("👁️ MutationObserver active");
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// ==================== INITIALISATION ====================
injectHighlightStyles();
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { scanAndAttach(); observeDynamicFields(); });
} else {
    scanAndAttach();
    observeDynamicFields();
}