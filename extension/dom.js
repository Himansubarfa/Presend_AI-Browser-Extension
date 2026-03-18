// // dom.js – DOM utilities for editable fields
// // Depends on: trackedFields (WeakSet declared in content.js, loaded before this)

// // ==================== FIELD DETECTION ====================
// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = (element.type || 'text').toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value || '';
//     if (field.isContentEditable) return field.innerText || '';
//     return '';
// }

// // ==================== SET TEXT (with editor detection) ====================
// function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();

//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         return;
//     }

//     if (!field.isContentEditable) return;

//     try {
//         // Quill (used by Gemini, some Gmail editors)
//         const quill = field.__quill || field._quill
//             || field.closest?.('.ql-container')?.__quill
//             || field.closest?.('.ql-container')?._quill;
//         if (quill) {
//             quill.setText(newText);
//             return;
//         }

//         // ProseMirror (used by ChatGPT, Notion, Linear)
//         const isPM = field.classList?.contains('ProseMirror') || !!field.closest?.('.ProseMirror');
//         if (isPM) {
//             const view = field._view || field.view
//                 || field.parentElement?._view || field.parentElement?.view;
//             if (view) {
//                 const { state } = view;
//                 const tr = state.tr.replaceWith(
//                     0,
//                     state.doc.content.size,
//                     state.schema.text(newText)
//                 );
//                 view.dispatch(tr);
//                 return;
//             }
//         }

//         // Generic contenteditable fallback
//         // NOTE: deliberately NOT dispatching blur() — it steals focus and can
//         // cause React/Vue/Angular to commit/reset form state mid-edit.
//         field.innerText = newText;
//         field.dispatchEvent(new Event('input',  { bubbles: true }));
//         field.dispatchEvent(new Event('change', { bubbles: true }));

//     } catch (e) {
//         console.error("❌ setFieldText error:", e);
//         // Last-resort: bare assignment
//         try {
//             field.innerText = newText;
//             field.dispatchEvent(new Event('input', { bubbles: true }));
//         } catch (_) { /* nothing left to try */ }
//     }
// }

// // ==================== CURSOR PRESERVATION ====================
// function saveCursorPosition(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
//     }
//     if (field.isContentEditable) {
//         const sel = window.getSelection();
//         if (!sel || sel.rangeCount === 0) return null;
//         const range = sel.getRangeAt(0);
//         if (!field.contains(range.startContainer)) return null;
//         const pre = range.cloneRange();
//         pre.selectNodeContents(field);
//         pre.setEnd(range.startContainer, range.startOffset);
//         return { type: 'contenteditable', offset: pre.toString().length };
//     }
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
//     try {
//         const tag = field.tagName.toLowerCase();
//         if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//             const len = newText.length;
//             field.setSelectionRange(
//                 Math.min(saved.start, len),
//                 Math.min(saved.end,   len)
//             );
//         } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//             const offset   = Math.min(saved.offset, newText.length);
//             const textNode = field.firstChild;
//             if (textNode && textNode.nodeType === Node.TEXT_NODE) {
//                 const range = document.createRange();
//                 range.setStart(textNode, offset);
//                 range.collapse(true);
//                 const sel = window.getSelection();
//                 if (sel) { sel.removeAllRanges(); sel.addRange(range); }
//             }
//         }
//     } catch (e) {
//         console.warn("⚠️ restoreCursorPosition failed (non-fatal):", e.message);
//     }
// }

// // ==================== QUILL CLIPBOARD MAPPING ====================
// function getEditorFromClipboard(clipboard) {
//     const container = clipboard.closest?.('.ql-container');
//     return container ? container.querySelector('.ql-editor') : null;
// }

// // Unified resolver used by both onInput and onPaste
// function resolveEditableTarget(target) {
//     if (target.classList?.contains('ql-clipboard')) {
//         return getEditorFromClipboard(target) || null; // null = skip
//     }
//     return target;
// }

// // ==================== ATTACH LISTENERS ====================
// function attachListener(field, onInputCallback, onPasteCallback) {
//     // trackedFields is declared in content.js and shared as a global
//     if (!trackedFields.has(field) && isEditableField(field)) {
//         field.addEventListener('input', onInputCallback);
//         field.addEventListener('paste', onPasteCallback);
//         trackedFields.add(field);
//     }
// }

// function scanAndAttach(selectors, onInputCallback, onPasteCallback) {
//     document.querySelectorAll(selectors.join(',')).forEach(field => {
//         attachListener(field, onInputCallback, onPasteCallback);
//     });
// }


// // day 27 update 

// // dom.js – DOM utilities for editable fields (PRODUCTION)

// // ==================== FIELD DETECTION ====================
// function isEditableField(element) {
//     if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
//     const tag = element.tagName.toLowerCase();
//     if (tag === 'input') {
//         const type = (element.type || 'text').toLowerCase();
//         return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
//     }
//     if (tag === 'textarea') return true;
//     if (element.isContentEditable) return true;
//     return false;
// }

// function getFieldText(field) {
//     const tag = field.tagName.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') return field.value || '';
//     if (field.isContentEditable) return field.innerText || '';
//     return '';
// }

// // ==================== ENHANCED EDITOR DETECTION ====================

// /**
//  * Detect and return Quill instance if present
//  * More robust than simple property checks
//  */
// function findQuillInstance(field) {
//     if (!field) return null;
    
//     // Direct property checks
//     if (field.__quill) return field.__quill;
//     if (field._quill) return field._quill;
//     if (field.quill) return field.quill;

//     // Check parent chain (up to 3 levels)
//     let current = field.parentElement;
//     for (let i = 0; i < 3 && current; i++) {
//         if (current.__quill) return current.__quill;
//         if (current._quill) return current._quill;
//         if (current.quill) return current.quill;
//         current = current.parentElement;
//     }

//     // Check .ql-container
//     const container = field.closest?.('.ql-container');
//     if (container) {
//         if (container.__quill) return container.__quill;
//         if (container._quill) return container._quill;
//         if (container.quill) return container.quill;
//     }

//     // Global Quill.find() if available (Gemini uses this)
//     if (typeof window !== 'undefined' && window.Quill?.find) {
//         try {
//             const instance = window.Quill.find(field);
//             if (instance) return instance;
//             if (container) {
//                 const containerInstance = window.Quill.find(container);
//                 if (containerInstance) return containerInstance;
//             }
//         } catch (e) {
//             console.debug("Quill.find() failed:", e);
//         }
//     }

//     return null;
// }

// /**
//  * Detect and return ProseMirror view if present
//  * More robust than simple property checks
//  */
// function findProseMirrorView(field) {
//     if (!field) return null;
    
//     // Direct property checks with validation
//     if (field._view?.state?.schema) return field._view;
//     if (field.view?.state?.schema) return field.view;
//     if (field.pmViewDesc?.view?.state?.schema) return field.pmViewDesc.view;

//     // Check parent chain (up to 3 levels)
//     let current = field.parentElement;
//     for (let i = 0; i < 3 && current; i++) {
//         if (current._view?.state?.schema) return current._view;
//         if (current.view?.state?.schema) return current.view;
//         if (current.pmViewDesc?.view?.state?.schema) return current.pmViewDesc.view;
//         current = current.parentElement;
//     }

//     // Check .ProseMirror element
//     const pmElement = field.closest?.('.ProseMirror');
//     if (pmElement) {
//         if (pmElement._view?.state?.schema) return pmElement._view;
//         if (pmElement.view?.state?.schema) return pmElement.view;
//         if (pmElement.pmViewDesc?.view?.state?.schema) return pmElement.pmViewDesc.view;
//     }

//     return null;
// }

// // ==================== SET TEXT (ASYNC WITH DOM WAIT) ====================

// /**
//  * Set text in a field with proper editor API handling
//  * Now ASYNC - waits for DOM to update before resolving
//  * @param {HTMLElement} field - The input field
//  * @param {string} newText - The text to set
//  * @returns {Promise} Resolves when text is set and DOM is updated
//  */
// async function setFieldText(field, newText) {
//     const tag = field.tagName.toLowerCase();

//     // ==================== STANDARD INPUTS ====================
//     if (tag === 'input' || tag === 'textarea') {
//         field.value = newText;
//         field.dispatchEvent(new Event('input', { bubbles: true }));
//         field.dispatchEvent(new Event('change', { bubbles: true }));
        
//         // Wait for next frame to ensure DOM updated
//         await new Promise(resolve => requestAnimationFrame(resolve));
//         return;
//     }

//     // ==================== CONTENTEDITABLE FIELDS ====================
//     if (!field.isContentEditable) {
//         console.warn("⚠️ Field is not editable");
//         return;
//     }

//     try {
//         let success = false;

//         // ---------- QUILL (Gemini) ----------
//         const quillInstance = findQuillInstance(field);
//         if (quillInstance) {
//             console.log("🖋️ Using Quill API");
//             try {
//                 // Quill's setText method
//                 quillInstance.setText(newText);
                
//                 // Also try setContents as backup
//                 if (quillInstance.getLength() === 1 && quillInstance.getText().trim() === '') {
//                     quillInstance.setContents([{ insert: newText }]);
//                 }
                
//                 // Trigger change events
//                 quillInstance.root.dispatchEvent(new Event('input', { bubbles: true }));
//                 quillInstance.root.dispatchEvent(new Event('text-change', { bubbles: true }));
                
//                 success = true;
                
//                 // Wait for Quill to update DOM
//                 await waitForTextUpdate(field, newText, 500);
//                 return;
                
//             } catch (e) {
//                 console.error("❌ Quill setText failed:", e);
//                 success = false;
//             }
//         }

//         // ---------- PROSEMIRROR (ChatGPT) ----------
//         if (!success) {
//             const pmView = findProseMirrorView(field);
//             if (pmView) {
//                 console.log("📝 Using ProseMirror API");
//                 try {
//                     const { state } = pmView;
                    
//                     // Validate state
//                     if (!state || !state.schema) {
//                         throw new Error("Invalid ProseMirror state");
//                     }
                    
//                     const tr = state.tr;
//                     const textNode = state.schema.text(newText);
                    
//                     // Replace entire document content
//                     tr.replaceWith(0, state.doc.content.size, textNode);
                    
//                     // Dispatch transaction
//                     pmView.dispatch(tr);
                    
//                     // Trigger events
//                     pmView.dom.dispatchEvent(new Event('input', { bubbles: true }));
                    
//                     success = true;
                    
//                     // Wait for ProseMirror to update DOM
//                     await waitForTextUpdate(field, newText, 500);
//                     return;
                    
//                 } catch (e) {
//                     console.error("❌ ProseMirror transaction failed:", e);
//                     success = false;
//                 }
//             }
//         }

//         // ---------- FALLBACK (Generic contenteditable) ----------
//         if (!success) {
//             console.log("🔧 Using fallback DOM update");
            
//             // Store focus state
//             const hadFocus = document.activeElement === field;
            
//             // Set text
//             field.innerText = newText;
            
//             // Dispatch events
//             field.dispatchEvent(new Event('input', { bubbles: true }));
//             field.dispatchEvent(new Event('change', { bubbles: true }));
            
//             // Restore focus if needed
//             if (hadFocus) {
//                 setTimeout(() => {
//                     field.focus();
//                     // Move cursor to end
//                     try {
//                         const range = document.createRange();
//                         const sel = window.getSelection();
//                         if (field.firstChild) {
//                             const offset = Math.min(newText.length, field.firstChild.length || 0);
//                             range.setStart(field.firstChild, offset);
//                             range.collapse(true);
//                             sel.removeAllRanges();
//                             sel.addRange(range);
//                         }
//                     } catch (e) {
//                         console.debug("Cursor positioning failed:", e);
//                     }
//                 }, 10);
//             }
            
//             // Wait for DOM update
//             await waitForTextUpdate(field, newText, 300);
//         }

//     } catch (e) {
//         console.error("❌ Critical error in setFieldText:", e);
        
//         // Ultimate fallback
//         try {
//             field.innerText = newText;
//             field.dispatchEvent(new Event('input', { bubbles: true }));
//             await new Promise(resolve => setTimeout(resolve, 100));
//         } catch (finalError) {
//             console.error("❌ Ultimate fallback failed:", finalError);
//         }
//     }
// }

// /**
//  * Wait for text to actually appear in the DOM
//  * Critical for highlighting to work properly
//  */
// function waitForTextUpdate(field, expectedText, maxWait = 500) {
//     return new Promise((resolve) => {
//         const startTime = Date.now();
        
//         const checkText = () => {
//             const currentText = getFieldText(field);
//             const matches = currentText === expectedText || 
//                            currentText.includes(expectedText) ||
//                            expectedText.includes(currentText);
            
//             const elapsed = Date.now() - startTime;
            
//             if (matches || elapsed > maxWait) {
//                 console.log(`⏱️ Text update confirmed after ${elapsed}ms`);
//                 resolve();
//             } else {
//                 requestAnimationFrame(checkText);
//             }
//         };
        
//         // Start checking on next frame
//         requestAnimationFrame(checkText);
//     });
// }

// // ==================== CURSOR PRESERVATION (ENHANCED) ====================

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
//         try {
//             const sel = window.getSelection();
//             if (!sel || sel.rangeCount === 0) return null;
            
//             const range = sel.getRangeAt(0);
//             if (!field.contains(range.startContainer)) return null;
            
//             const pre = range.cloneRange();
//             pre.selectNodeContents(field);
//             pre.setEnd(range.startContainer, range.startOffset);
            
//             return { 
//                 type: 'contenteditable', 
//                 offset: pre.toString().length,
//                 collapsed: range.collapsed
//             };
//         } catch (e) {
//             console.debug("Cursor save failed:", e);
//             return null;
//         }
//     }
    
//     return null;
// }

// function restoreCursorPosition(field, saved, newText) {
//     if (!saved) return;
    
//     try {
//         const tag = field.tagName.toLowerCase();
        
//         if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
//             const len = newText.length;
//             const start = Math.min(saved.start, len);
//             const end = Math.min(saved.end, len);
            
//             // Use timeout to ensure value is set first
//             setTimeout(() => {
//                 try {
//                     field.setSelectionRange(start, end);
//                 } catch (e) {
//                     console.debug("Selection range restore failed:", e);
//                 }
//             }, 0);
            
//         } else if (saved.type === 'contenteditable' && field.isContentEditable) {
//             // Wait for DOM to stabilize
//             setTimeout(() => {
//                 try {
//                     const newOffset = Math.min(saved.offset, newText.length);
                    
//                     // Use TreeWalker for more robust text node finding
//                     const walker = document.createTreeWalker(
//                         field,
//                         NodeFilter.SHOW_TEXT,
//                         null
//                     );
                    
//                     let currentOffset = 0;
//                     let targetNode = null;
//                     let targetOffset = 0;
                    
//                     while (walker.nextNode()) {
//                         const node = walker.currentNode;
//                         const nodeLength = node.textContent?.length || 0;
                        
//                         if (currentOffset + nodeLength >= newOffset) {
//                             targetNode = node;
//                             targetOffset = newOffset - currentOffset;
//                             break;
//                         }
                        
//                         currentOffset += nodeLength;
//                     }
                    
//                     if (targetNode) {
//                         const range = document.createRange();
//                         const safeOffset = Math.min(targetOffset, targetNode.length || 0);
//                         range.setStart(targetNode, safeOffset);
//                         range.collapse(true);
                        
//                         const sel = window.getSelection();
//                         if (sel) {
//                             sel.removeAllRanges();
//                             sel.addRange(range);
//                         }
//                     }
//                 } catch (e) {
//                     console.debug("Contenteditable cursor restore failed:", e);
//                 }
//             }, 10);
//         }
//     } catch (e) {
//         console.warn("⚠️ restoreCursorPosition failed (non-fatal):", e.message);
//     }
// }

// // ==================== QUILL CLIPBOARD MAPPING ====================

// function getEditorFromClipboard(clipboard) {
//     const container = clipboard.closest?.('.ql-container');
//     return container ? container.querySelector('.ql-editor') : null;
// }

// // Unified resolver used by both onInput and onPaste
// function resolveEditableTarget(target) {
//     if (target.classList?.contains('ql-clipboard')) {
//         return getEditorFromClipboard(target) || null;
//     }
//     return target;
// }

// // ==================== ATTACH LISTENERS ====================

// function attachListener(field, onInputCallback, onPasteCallback) {
//     // trackedFields is declared in content.js and shared as a global
//     if (!trackedFields.has(field) && isEditableField(field)) {
//         field.addEventListener('input', onInputCallback);
//         field.addEventListener('paste', onPasteCallback);
//         trackedFields.add(field);
//     }
// }

// function scanAndAttach(selectors, onInputCallback, onPasteCallback) {
//     document.querySelectorAll(selectors.join(',')).forEach(field => {
//         attachListener(field, onInputCallback, onPasteCallback);
//     });
// }

// // ==================== EXPORTS (if needed) ====================
// if (typeof module !== 'undefined' && module.exports) {
//     module.exports = {
//         isEditableField,
//         getFieldText,
//         setFieldText,
//         saveCursorPosition,
//         restoreCursorPosition,
//         getEditorFromClipboard,
//         resolveEditableTarget,
//         attachListener,
//         scanAndAttach,
//         findQuillInstance,
//         findProseMirrorView,
//         waitForTextUpdate
//     };
// }


// final update for day 27


// dom.js – DOM utilities for editable fields (PRODUCTION)

// ==================== FIELD DETECTION ====================
function isEditableField(element) {
    if (!element || !element.nodeType || element.nodeType !== Node.ELEMENT_NODE) return false;
    const tag = element.tagName.toLowerCase();
    if (tag === 'input') {
        const type = (element.type || 'text').toLowerCase();
        return ['text', 'search', 'tel', 'url', 'email', 'password', 'number'].includes(type);
    }
    if (tag === 'textarea') return true;
    if (element.isContentEditable) return true;
    return false;
}

function getFieldText(field) {
    const tag = field.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') return field.value || '';
    if (field.isContentEditable) return field.innerText || '';
    return '';
}

// ==================== ENHANCED EDITOR DETECTION ====================

/**
 * Detect and return Quill instance if present
 * More robust than simple property checks
 */
function findQuillInstance(field) {
    if (!field) return null;
    
    // Direct property checks
    if (field.__quill) return field.__quill;
    if (field._quill) return field._quill;
    if (field.quill) return field.quill;

    // Check parent chain (up to 3 levels)
    let current = field.parentElement;
    for (let i = 0; i < 3 && current; i++) {
        if (current.__quill) return current.__quill;
        if (current._quill) return current._quill;
        if (current.quill) return current.quill;
        current = current.parentElement;
    }

    // Check .ql-container
    const container = field.closest?.('.ql-container');
    if (container) {
        if (container.__quill) return container.__quill;
        if (container._quill) return container._quill;
        if (container.quill) return container.quill;
    }

    // Global Quill.find() if available (Gemini uses this)
    if (typeof window !== 'undefined' && window.Quill?.find) {
        try {
            const instance = window.Quill.find(field);
            if (instance) return instance;
            if (container) {
                const containerInstance = window.Quill.find(container);
                if (containerInstance) return containerInstance;
            }
        } catch (e) {
            console.debug("Quill.find() failed:", e);
        }
    }

    return null;
}

/**
 * Detect and return ProseMirror view if present
 * More robust than simple property checks
 */
function findProseMirrorView(field) {
    if (!field) return null;
    
    // Direct property checks with validation
    if (field._view?.state?.schema) return field._view;
    if (field.view?.state?.schema) return field.view;
    if (field.pmViewDesc?.view?.state?.schema) return field.pmViewDesc.view;

    // Check parent chain (up to 3 levels)
    let current = field.parentElement;
    for (let i = 0; i < 3 && current; i++) {
        if (current._view?.state?.schema) return current._view;
        if (current.view?.state?.schema) return current.view;
        if (current.pmViewDesc?.view?.state?.schema) return current.pmViewDesc.view;
        current = current.parentElement;
    }

    // Check .ProseMirror element
    const pmElement = field.closest?.('.ProseMirror');
    if (pmElement) {
        if (pmElement._view?.state?.schema) return pmElement._view;
        if (pmElement.view?.state?.schema) return pmElement.view;
        if (pmElement.pmViewDesc?.view?.state?.schema) return pmElement.pmViewDesc.view;
    }

    return null;
}

// ==================== SET TEXT (ASYNC WITH DOM WAIT) ====================

/**
 * Set text in a field with proper editor API handling
 * Now ASYNC - waits for DOM to update before resolving
 * @param {HTMLElement} field - The input field
 * @param {string} newText - The text to set
 * @returns {Promise} Resolves when text is set and DOM is updated
 */
async function setFieldText(field, newText) {
    const tag = field.tagName.toLowerCase();

    // ==================== STANDARD INPUTS ====================
    if (tag === 'input' || tag === 'textarea') {
        field.value = newText;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Wait for next frame to ensure DOM updated
        await new Promise(resolve => requestAnimationFrame(resolve));
        return;
    }

    // ==================== CONTENTEDITABLE FIELDS ====================
    if (!field.isContentEditable) {
        console.warn("⚠️ Field is not editable");
        return;
    }

    try {
        let success = false;

        // ---------- QUILL (Gemini) ----------
        const quillInstance = findQuillInstance(field);
        if (quillInstance) {
            console.log("🖋️ Using Quill API");
            try {
                // Quill's setText method
                quillInstance.setText(newText);
                
                // Also try setContents as backup
                if (quillInstance.getLength() === 1 && quillInstance.getText().trim() === '') {
                    quillInstance.setContents([{ insert: newText }]);
                }
                
                // Trigger change events
                quillInstance.root.dispatchEvent(new Event('input', { bubbles: true }));
                quillInstance.root.dispatchEvent(new Event('text-change', { bubbles: true }));
                
                success = true;
                
                // Wait for Quill to update DOM
                await waitForTextUpdate(field, newText, 500);
                return;
                
            } catch (e) {
                console.error("❌ Quill setText failed:", e);
                success = false;
            }
        }

        // ---------- PROSEMIRROR (ChatGPT) ----------
        if (!success) {
            const pmView = findProseMirrorView(field);
            if (pmView) {
                console.log("📝 Using ProseMirror API");
                try {
                    const { state } = pmView;
                    
                    // Validate state
                    if (!state || !state.schema) {
                        throw new Error("Invalid ProseMirror state");
                    }
                    
                    const tr = state.tr;
                    const textNode = state.schema.text(newText);
                    
                    // Replace entire document content
                    tr.replaceWith(0, state.doc.content.size, textNode);
                    
                    // Dispatch transaction
                    pmView.dispatch(tr);
                    
                    // Trigger events
                    pmView.dom.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    success = true;
                    
                    // Wait for ProseMirror to update DOM
                    await waitForTextUpdate(field, newText, 500);
                    return;
                    
                } catch (e) {
                    console.error("❌ ProseMirror transaction failed:", e);
                    success = false;
                }
            }
        }

        // ---------- FALLBACK (Generic contenteditable) ----------
        if (!success) {
            console.log("🔧 Using fallback DOM update");
            
            // Store focus state
            const hadFocus = document.activeElement === field;
            
            // Set text
            field.innerText = newText;
            
            // Dispatch events
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Restore focus if needed
            if (hadFocus) {
                setTimeout(() => {
                    field.focus();
                    // Move cursor to end
                    try {
                        const range = document.createRange();
                        const sel = window.getSelection();
                        if (field.firstChild) {
                            const offset = Math.min(newText.length, field.firstChild.length || 0);
                            range.setStart(field.firstChild, offset);
                            range.collapse(true);
                            sel.removeAllRanges();
                            sel.addRange(range);
                        }
                    } catch (e) {
                        console.debug("Cursor positioning failed:", e);
                    }
                }, 10);
            }
            
            // Wait for DOM update
            await waitForTextUpdate(field, newText, 300);
        }

    } catch (e) {
        console.error("❌ Critical error in setFieldText:", e);
        
        // Ultimate fallback
        try {
            field.innerText = newText;
            field.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(resolve => setTimeout(resolve, 100));
        } catch (finalError) {
            console.error("❌ Ultimate fallback failed:", finalError);
        }
    }
}

/**
 * Wait for text to actually appear in the DOM
 * Critical for highlighting to work properly
 */
function waitForTextUpdate(field, expectedText, maxWait = 500) {
    return new Promise((resolve) => {
        const startTime = Date.now();
        
        const checkText = () => {
            const currentText = getFieldText(field);
            const matches = currentText === expectedText || 
                           currentText.includes(expectedText) ||
                           expectedText.includes(currentText);
            
            const elapsed = Date.now() - startTime;
            
            if (matches || elapsed > maxWait) {
                console.log(`⏱️ Text update confirmed after ${elapsed}ms`);
                resolve();
            } else {
                requestAnimationFrame(checkText);
            }
        };
        
        // Start checking on next frame
        requestAnimationFrame(checkText);
    });
}

// ==================== CURSOR PRESERVATION (ENHANCED) ====================

function saveCursorPosition(field) {
    const tag = field.tagName.toLowerCase();
    
    if (tag === 'input' || tag === 'textarea') {
        return { 
            type: 'input', 
            start: field.selectionStart, 
            end: field.selectionEnd 
        };
    }
    
    if (field.isContentEditable) {
        try {
            const sel = window.getSelection();
            if (!sel || sel.rangeCount === 0) return null;
            
            const range = sel.getRangeAt(0);
            if (!field.contains(range.startContainer)) return null;
            
            const pre = range.cloneRange();
            pre.selectNodeContents(field);
            pre.setEnd(range.startContainer, range.startOffset);
            
            return { 
                type: 'contenteditable', 
                offset: pre.toString().length,
                collapsed: range.collapsed
            };
        } catch (e) {
            console.debug("Cursor save failed:", e);
            return null;
        }
    }
    
    return null;
}

function restoreCursorPosition(field, saved, newText) {
    if (!saved) return;
    
    try {
        const tag = field.tagName.toLowerCase();
        
        if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
            const len = newText.length;
            const start = Math.min(saved.start, len);
            const end = Math.min(saved.end, len);
            
            // Use timeout to ensure value is set first
            setTimeout(() => {
                try {
                    field.setSelectionRange(start, end);
                } catch (e) {
                    console.debug("Selection range restore failed:", e);
                }
            }, 0);
            
        } else if (saved.type === 'contenteditable' && field.isContentEditable) {
            // Wait for DOM to stabilize
            setTimeout(() => {
                try {
                    const newOffset = Math.min(saved.offset, newText.length);
                    
                    // Use TreeWalker for more robust text node finding
                    const walker = document.createTreeWalker(
                        field,
                        NodeFilter.SHOW_TEXT,
                        null
                    );
                    
                    let currentOffset = 0;
                    let targetNode = null;
                    let targetOffset = 0;
                    
                    while (walker.nextNode()) {
                        const node = walker.currentNode;
                        const nodeLength = node.textContent?.length || 0;
                        
                        if (currentOffset + nodeLength >= newOffset) {
                            targetNode = node;
                            targetOffset = newOffset - currentOffset;
                            break;
                        }
                        
                        currentOffset += nodeLength;
                    }
                    
                    if (targetNode) {
                        const range = document.createRange();
                        const safeOffset = Math.min(targetOffset, targetNode.length || 0);
                        range.setStart(targetNode, safeOffset);
                        range.collapse(true);
                        
                        const sel = window.getSelection();
                        if (sel) {
                            sel.removeAllRanges();
                            sel.addRange(range);
                        }
                    }
                } catch (e) {
                    console.debug("Contenteditable cursor restore failed:", e);
                }
            }, 10);
        }
    } catch (e) {
        console.warn("⚠️ restoreCursorPosition failed (non-fatal):", e.message);
    }
}

// ==================== QUILL CLIPBOARD MAPPING ====================

function getEditorFromClipboard(clipboard) {
    const container = clipboard.closest?.('.ql-container');
    return container ? container.querySelector('.ql-editor') : null;
}

// Unified resolver used by both onInput and onPaste
function resolveEditableTarget(target) {
    if (target.classList?.contains('ql-clipboard')) {
        return getEditorFromClipboard(target) || null;
    }
    return target;
}

// ==================== ATTACH LISTENERS ====================

function attachListener(field, onInputCallback, onPasteCallback) {
    // trackedFields is declared in content.js and shared as a global
    if (!trackedFields.has(field) && isEditableField(field)) {
        field.addEventListener('input', onInputCallback);
        field.addEventListener('paste', onPasteCallback);
        trackedFields.add(field);
    }
}

function scanAndAttach(selectors, onInputCallback, onPasteCallback) {
    document.querySelectorAll(selectors.join(',')).forEach(field => {
        attachListener(field, onInputCallback, onPasteCallback);
    });
}

// ==================== EXPORTS (if needed) ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        isEditableField,
        getFieldText,
        setFieldText,
        saveCursorPosition,
        restoreCursorPosition,
        getEditorFromClipboard,
        resolveEditableTarget,
        attachListener,
        scanAndAttach,
        findQuillInstance,
        findProseMirrorView,
        waitForTextUpdate
    };
}