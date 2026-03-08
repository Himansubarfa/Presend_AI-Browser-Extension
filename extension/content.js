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

console.log("🔒 PreSendAI content script loaded – Day 16 (MutationObserver + ORG)");

// ==================== CONFIGURATION ====================
const BACKEND_URL = "http://localhost:5000/scan";
const DEBOUNCE_DELAY = 600;
const OBSERVER_DEBOUNCE = 300;

// Placeholders – added [ORG]
const MASK_PLACEHOLDERS = ["[NAME]", "[EMAIL]", "[PHONE]", "[ID]", "[CARD]", "[ADDRESS]", "[ORG]", "[REDACTED]"];

// ==================== STATE TRACKING ====================
const trackedFields = new WeakSet();
const lastSentText = new WeakMap();
let isUpdating = false;

// ==================== HELPER FUNCTIONS ====================
function isAlreadyMasked(text) {
    return MASK_PLACEHOLDERS.some(placeholder => text.includes(placeholder));
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
    if (tag === 'input' || tag === 'textarea') {
        return field.value;
    } else if (field.isContentEditable) {
        return field.innerText;
    }
    return '';
}

function setFieldText(field, newText) {
    const tag = field.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') {
        field.value = newText;
    } else if (field.isContentEditable) {
        field.innerText = newText;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== CORE MASKING FUNCTION ====================
async function maskAndReplace(field, text) {
    console.log("maskAndReplace called with text:", text);
    if (!text.trim()) return;

    if (isAlreadyMasked(text)) {
        console.log("Text already masked, skipping.");
        return;
    }

    let startPos = null, endPos = null;
    const isInputOrTextarea = field.tagName.toLowerCase() === 'input' || field.tagName.toLowerCase() === 'textarea';
    if (isInputOrTextarea) {
        startPos = field.selectionStart;
        endPos = field.selectionEnd;
        console.log(`Cursor saved: start=${startPos}, end=${endPos}`);
    }

    try {
        console.log("Sending message to background...");
        const response = await chrome.runtime.sendMessage({
            action: "maskText",
            text: text,
            url: BACKEND_URL
        });
        console.log("Received response from background:", response);

        if (!response.success) {
            console.error("Background error:", response.error);
            return;
        }

        const data = response.data;
        console.log("Backend data:", data);

        if (data.status === 'ok' && data.masked && data.masked !== text) {
            console.log("Replacing field text with:", data.masked);
            isUpdating = true;
            setFieldText(field, data.masked);

            if (isInputOrTextarea && startPos !== null && endPos !== null) {
                const newLength = data.masked.length;
                const newStart = Math.min(startPos, newLength);
                const newEnd = Math.min(endPos, newLength);
                field.setSelectionRange(newStart, newEnd);
                console.log(`Cursor restored to start=${newStart}, end=${newEnd}`);
            }

            isUpdating = false;
            lastSentText.set(field, data.masked);
        } else if (data.status === 'error') {
            console.warn('Backend processing error:', data.message);
        } else {
            console.log("No change needed (masked text unchanged or empty)");
        }
    } catch (error) {
        console.error('Failed to communicate with background worker:', error);
    }
}

// ==================== INPUT HANDLER ====================
function onInput(event) {
    if (isUpdating) return;

    const field = event.target;
    const currentText = getFieldText(field);
    const lastSent = lastSentText.get(field);

    if (currentText === lastSent) return;

    if (!field._debouncedMask) {
        field._debouncedMask = debounce((field, text) => {
            maskAndReplace(field, text);
        }, DEBOUNCE_DELAY);
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
        'input[type="text"]',
        'input[type="search"]',
        'input[type="tel"]',
        'input[type="url"]',
        'input[type="email"]',
        'input[type="password"]',
        'input[type="number"]',
        'textarea',
        '[contenteditable="true"]'
    ];
    document.querySelectorAll(selectors.join(',')).forEach(attachListener);
}

// ==================== MUTATION OBSERVER ====================
let observerTimeout = null;
function handleMutations(mutations) {
    if (observerTimeout) clearTimeout(observerTimeout);
    observerTimeout = setTimeout(() => {
        console.log("🔍 Scanning for dynamically added fields...");
        scanAndAttach();
    }, OBSERVER_DEBOUNCE);
}

function observeDynamicFields() {
    const observer = new MutationObserver(handleMutations);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    console.log("👁️ MutationObserver active – watching for new fields");
}

// ==================== INITIALISATION ====================
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        scanAndAttach();
        observeDynamicFields();
    });
} else {
    scanAndAttach();
    observeDynamicFields();
}