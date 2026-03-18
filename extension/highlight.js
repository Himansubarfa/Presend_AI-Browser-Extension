// // highlight.js – visual highlight engine
// // NOTE: HIGHLIGHT_DURATION is declared as a constant in content.js.
// // Do NOT re-declare it here to avoid the duplicate-variable shadowing bug
// // that caused content.js to use an undefined value at runtime.

// function injectHighlightStyles() {
//     const id = 'presendai-highlight-styles';
//     if (document.getElementById(id)) return;
//     const style = document.createElement('style');
//     style.id = id;
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
//             0%   { background-color: inherit; }
//             50%  { background-color: #fff2b0; }
//             100% { background-color: inherit; }
//         }
//     `;
//     document.head.appendChild(style);
// }

// function removeHighlights(field) {
//     if (!field.isContentEditable) return;
//     field.querySelectorAll('.presendai-highlight').forEach(span => {
//         const parent = span.parentNode;
//         if (parent) {
//             parent.replaceChild(document.createTextNode(span.textContent), span);
//             parent.normalize();
//         }
//     });
// }

// function highlightContentEditablePlain(field, entities) {
//     if (/<[^>]*>/.test(field.innerHTML) &&
//         !field.innerHTML.includes('<span class="presendai-highlight">')) {
//         console.warn("⚠️ Field contains HTML – falling back to flash");
//         return false;
//     }

//     removeHighlights(field);

//     const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
//     const textNodes = [];
//     let node;
//     while ((node = walker.nextNode())) textNodes.push(node);

//     let pos = 0;
//     const nodeMap = textNodes.map(n => {
//         const start = pos;
//         pos += n.nodeValue.length;
//         return { node: n, start, end: pos };
//     });

//     const sorted = [...entities].sort((a, b) => b.start - a.start);

//     for (const ent of sorted) {
//         for (const item of nodeMap) {
//             if (ent.start >= item.end || ent.end <= item.start) continue;

//             const oStart = Math.max(ent.start, item.start);
//             const oEnd   = Math.min(ent.end,   item.end);
//             if (oStart >= oEnd) continue;

//             const text   = item.node.nodeValue;
//             const before = text.substring(0, oStart - item.start);
//             const middle = text.substring(oStart - item.start, oEnd - item.start);
//             const after  = text.substring(oEnd - item.start);

//             const span = document.createElement('span');
//             span.className = 'presendai-highlight';
//             span.textContent = middle;

//             const frag = document.createDocumentFragment();
//             if (before) frag.appendChild(document.createTextNode(before));
//             frag.appendChild(span);
//             if (after)  frag.appendChild(document.createTextNode(after));

//             item.node.parentNode.replaceChild(frag, item.node);
//             break;
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
//             if (!highlightContentEditablePlain(field, entities)) highlightFieldFlash(field);
//         } else {
//             highlightFieldFlash(field);
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field);
//     }
// }


// ////////////////////////////////////////////
// // day 27 update 

// // highlight.js – visual highlight engine with platform-specific styling

// // ==================== CONFIGURATION ====================
// const HIGHLIGHT_DURATION = 600; // ms
// const HIGHLIGHT_CLASS = 'presendai-highlight';
// const FLASH_CLASS = 'presendai-flash';

// // Color schemes for different platforms
// const COLORS = {
//     TEXTAREA: {
//         background: '#4A9EBD',  // Moderate ocean blue
//         color: '#FFFFFF',
//         name: 'Ocean'
//     },
//     CHATGPT: {
//         background: '#10A37F',  // Emerald green (works on dark)
//         color: '#FFFFFF',
//         name: 'Emerald'
//     },
//     GEMINI: {
//         background: '#8E4EF5',  // Vibrant purple (Google-ish)
//         color: '#FFFFFF',
//         name: 'Gemini Purple'
//     },
//     DEFAULT: {
//         background: '#FFD700',  // Gold
//         color: '#000000',
//         name: 'Gold'
//     }
// };

// // ==================== PLATFORM DETECTION ====================
// function detectPlatform(field) {
//     if (!field) return 'DEFAULT';
    
//     // Check for textarea or input
//     const tag = field.tagName?.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return 'TEXTAREA';
//     }
    
//     // Check for ChatGPT (OpenAI)
//     if (field.closest('#prompt-textarea') || 
//         field.closest('[data-testid="chat-input"]') ||
//         window.location.hostname.includes('openai.com') ||
//         window.location.hostname.includes('chatgpt.com')) {
//         return 'CHATGPT';
//     }
    
//     // Check for Gemini (Google)
//     if (field.closest('.ql-container') || 
//         field.classList?.contains('ql-editor') ||
//         window.location.hostname.includes('gemini.google.com') ||
//         document.querySelector('[data-app-id*="gemini"]')) {
//         return 'GEMINI';
//     }
    
//     return 'DEFAULT';
// }

// // ==================== STYLES ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
    
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         /* Base highlight styles */
//         .${HIGHLIGHT_CLASS} {
//             border-radius: 4px;
//             padding: 2px 4px;
//             margin: 0 -2px;
//             display: inline;
//             font-weight: 500;
//             transition: all 0.3s ease;
//             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
//         }
        
//         /* Platform-specific colors */
//         .${HIGHLIGHT_CLASS}[data-platform="TEXTAREA"] {
//             background-color: ${COLORS.TEXTAREA.background} !important;
//             color: ${COLORS.TEXTAREA.color} !important;
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
//             background-color: ${COLORS.CHATGPT.background} !important;
//             color: ${COLORS.CHATGPT.color} !important;
//             box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="GEMINI"] {
//             background-color: ${COLORS.GEMINI.background} !important;
//             color: ${COLORS.GEMINI.color} !important;
//             box-shadow: 0 0 0 2px rgba(142, 78, 245, 0.2);
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="DEFAULT"] {
//             background-color: ${COLORS.DEFAULT.background} !important;
//             color: ${COLORS.DEFAULT.color} !important;
//         }
        
//         /* Flash animation */
//         .${FLASH_CLASS} {
//             animation: presendai-flash-bg ${HIGHLIGHT_DURATION}ms ease;
//         }
        
//         /* Platform-specific flash animations */
//         @keyframes presendai-flash-bg {
//             0% { 
//                 background-color: transparent; 
//                 box-shadow: none;
//             }
//             50% { 
//                 background-color: var(--flash-color, #FFD700);
//                 box-shadow: 0 0 20px var(--flash-color, #FFD700);
//             }
//             100% { 
//                 background-color: transparent;
//                 box-shadow: none;
//             }
//         }
        
//         /* Flash variants for different platforms */
//         .${FLASH_CLASS}[data-platform="TEXTAREA"] {
//             --flash-color: ${COLORS.TEXTAREA.background};
//         }
        
//         .${FLASH_CLASS}[data-platform="CHATGPT"] {
//             --flash-color: ${COLORS.CHATGPT.background};
//         }
        
//         .${FLASH_CLASS}[data-platform="GEMINI"] {
//             --flash-color: ${COLORS.GEMINI.background};
//         }
        
//         /* Hover effects */
//         .${HIGHLIGHT_CLASS}:hover {
//             transform: translateY(-1px);
//             box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
//         }
        
//         /* Ensure highlights work in various editors */
//         .ql-editor .${HIGHLIGHT_CLASS},
//         .ProseMirror .${HIGHLIGHT_CLASS},
//         [contenteditable] .${HIGHLIGHT_CLASS} {
//             display: inline;
//             line-height: inherit;
//         }
        
//         /* Dark mode adjustments for ChatGPT */
//         .dark .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"],
//         [data-theme="dark"] .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
//             box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.4);
//         }
//     `;
//     document.head.appendChild(style);
// }

// // ==================== CLEANUP ====================
// function removeHighlights(field) {
//     if (!field) return;
    
//     try {
//         // For contenteditable fields
//         if (field.isContentEditable) {
//             const highlights = field.querySelectorAll(`.${HIGHLIGHT_CLASS}`);
            
//             // Process in reverse to avoid index issues
//             Array.from(highlights).reverse().forEach(span => {
//                 const parent = span.parentNode;
//                 if (parent && parent.contains(span)) {
//                     // Replace span with its text content
//                     const textNode = document.createTextNode(span.textContent);
//                     parent.replaceChild(textNode, span);
//                 }
//             });
            
//             // Normalize to merge adjacent text nodes
//             field.normalize();
//         }
        
//         // Remove flash class
//         field.classList?.remove(FLASH_CLASS);
//         field.removeAttribute?.('data-platform');
        
//         console.log("✨ Highlights removed");
//     } catch (e) {
//         console.error("❌ Error removing highlights:", e);
//     }
// }

// // ==================== EDITOR DETECTION ====================
// /**
//  * Detect if field is a rich text editor (Quill/ProseMirror/etc)
//  * Uses enhanced detection from dom.js if available
//  */
// function isRichEditor(field) {
//     if (!field || !field.isContentEditable) return false;
    
//     // Use dom.js functions if available
//     if (typeof findQuillInstance === 'function') {
//         if (findQuillInstance(field)) return true;
//     }
//     if (typeof findProseMirrorView === 'function') {
//         if (findProseMirrorView(field)) return true;
//     }
    
//     // Fallback detection for Quill (Gemini)
//     if (field.__quill || field._quill || field.quill) return true;
//     if (field.classList?.contains('ql-editor')) return true;
//     if (field.closest?.('.ql-container')) return true;
    
//     // Check parent chain for Quill
//     let parent = field.parentElement;
//     for (let i = 0; i < 3 && parent; i++) {
//         if (parent.__quill || parent._quill) return true;
//         parent = parent.parentElement;
//     }
    
//     // Fallback detection for ProseMirror (ChatGPT)
//     if (field._view || field.view || field.pmViewDesc) return true;
//     if (field.classList?.contains('ProseMirror')) return true;
//     if (field.closest?.('.ProseMirror')) return true;
    
//     // Check for other rich editors
//     if (field.classList?.contains('tox-edit-area')) return true; // TinyMCE
//     if (field.closest?.('.DraftEditor-root')) return true; // Draft.js
//     if (field.getAttribute?.('data-lexical-editor') === 'true') return true; // Lexical
//     if (field.querySelector?.('[data-slate-node], .slate-node')) return true; // Slate
    
//     return false;
// }

// // ==================== PLAIN CONTENTEDITABLE HIGHLIGHTING ====================
// /**
//  * Highlight specific text spans in plain contenteditable fields
//  * @param {HTMLElement} field - The contenteditable element
//  * @param {Array} entities - Array of {start, end, type} objects
//  * @param {string} platform - Platform identifier for color scheme
//  * @returns {boolean} - Success status
//  */
// function highlightContentEditablePlain(field, entities, platform) {
//     // Safety checks
//     if (!field || !field.isContentEditable) {
//         console.log("🎨 Field is not contenteditable");
//         return false;
//     }
    
//     // Skip rich editors
//     if (isRichEditor(field)) {
//         console.log("🎨 Rich editor detected, skipping per-word highlight");
//         return false;
//     }
    
//     // Check if field has complex HTML (but not our highlights)
//     const hasComplexHTML = /<(?!span\s+class="presendai-highlight")[^>]*>/.test(field.innerHTML);
//     if (hasComplexHTML) {
//         console.log("🎨 Complex HTML detected, using flash fallback");
//         return false;
//     }
    
//     try {
//         // Remove existing highlights
//         removeHighlights(field);
        
//         // Collect all text nodes
//         const walker = document.createTreeWalker(
//             field, 
//             NodeFilter.SHOW_TEXT, 
//             null
//         );
        
//         const textNodes = [];
//         let node;
//         while (node = walker.nextNode()) {
//             textNodes.push(node);
//         }
        
//         if (textNodes.length === 0) {
//             console.log("🎨 No text nodes found");
//             return false;
//         }
        
//         // Build node map with positions
//         let currentPos = 0;
//         const nodeMap = textNodes.map(node => {
//             const start = currentPos;
//             const length = node.nodeValue?.length || 0;
//             const end = currentPos + length;
//             currentPos = end;
//             return { node, start, end, length };
//         });
        
//         // Sort entities by position (reverse order for easier processing)
//         const sorted = [...entities].sort((a, b) => b.start - a.start);
        
//         // Apply highlights
//         for (const entity of sorted) {
//             const { start, end } = entity;
            
//             if (start >= end) continue; // Invalid range
            
//             // Find overlapping nodes
//             for (const item of nodeMap) {
//                 // Skip if no overlap
//                 if (start >= item.end || end <= item.start) continue;
                
//                 const node = item.node;
                
//                 // Skip if node was already removed
//                 if (!node.parentNode) continue;
                
//                 // Calculate overlap within this node
//                 const overlapStart = Math.max(start, item.start) - item.start;
//                 const overlapEnd = Math.min(end, item.end) - item.start;
                
//                 if (overlapStart >= overlapEnd) continue;
                
//                 const text = node.nodeValue || '';
//                 const before = text.substring(0, overlapStart);
//                 const middle = text.substring(overlapStart, overlapEnd);
//                 const after = text.substring(overlapEnd);
                
//                 // Create highlight span with platform color
//                 const span = document.createElement('span');
//                 span.className = HIGHLIGHT_CLASS;
//                 span.textContent = middle;
//                 span.setAttribute('data-platform', platform);
//                 span.setAttribute('data-entity-type', entity.type || 'unknown');
                
//                 // Build replacement fragment
//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));
                
//                 // Replace in DOM
//                 const parent = node.parentNode;
//                 if (parent) {
//                     parent.replaceChild(fragment, node);
//                     item.node = null; // Mark as processed
//                 }
                
//                 // Break out of inner loop after replacement
//                 break;
//             }
//         }
        
//         // Normalize to clean up
//         field.normalize();
        
//         const colorName = COLORS[platform]?.name || 'default';
//         console.log(`🎨 Successfully highlighted ${sorted.length} entities with ${colorName} color`);
//         return true;
        
//     } catch (e) {
//         console.error("❌ Error in highlightContentEditablePlain:", e);
//         return false;
//     }
// }

// // ==================== FLASH HIGHLIGHT ====================
// /**
//  * Apply a flash animation to the entire field
//  * Used for rich editors where we can't safely manipulate DOM
//  */
// function highlightFieldFlash(field, platform) {
//     if (!field) return;
    
//     try {
//         // Set platform for color
//         field.setAttribute('data-platform', platform);
        
//         // Add flash class
//         field.classList.add(FLASH_CLASS);
        
//         // Remove after animation completes
//         setTimeout(() => {
//             field.classList.remove(FLASH_CLASS);
//             field.removeAttribute('data-platform');
//         }, HIGHLIGHT_DURATION);
        
//         const colorName = COLORS[platform]?.name || 'default';
//         console.log(`🎨 Applied ${colorName} flash highlight`);
//     } catch (e) {
//         console.error("❌ Error in highlightFieldFlash:", e);
//     }
// }

// // ==================== MAIN HIGHLIGHT FUNCTION ====================
// /**
//  * Highlight entities in a field with platform-specific colors
//  * Automatically detects platform and chooses the best highlighting method
//  * @param {HTMLElement} field - The field to highlight
//  * @param {Array} entities - Array of {start, end, type?} objects
//  */
// function highlightField(field, entities) {
//     if (!field) {
//         console.log("🎨 No field provided");
//         return;
//     }
    
//     if (!entities || entities.length === 0) {
//         console.log("🎨 No entities to highlight");
//         return;
//     }
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     // Detect platform for appropriate color scheme
//     const platform = detectPlatform(field);
//     console.log(`🎨 Platform detected: ${platform}`);
    
//     try {
//         // For standard inputs and textareas, use flash with ocean color
//         const tag = field.tagName?.toLowerCase();
//         if (tag === 'input' || tag === 'textarea') {
//             highlightFieldFlash(field, 'TEXTAREA');
//             return;
//         }
        
//         // For contenteditable fields
//         if (field.isContentEditable) {
//             // Try per-word highlighting for plain contenteditable
//             const success = highlightContentEditablePlain(field, entities, platform);
            
//             // Fall back to flash if per-word failed (rich editors)
//             if (!success) {
//                 highlightFieldFlash(field, platform);
//             }
//         } else {
//             console.log("🎨 Field is not editable, skipping highlight");
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field, platform);
//     }
// }

// // ==================== CHATGPT-SPECIFIC HIGHLIGHTING ====================
// /**
//  * Highlight entities specifically in ChatGPT editor
//  * Uses emerald green color optimized for dark background
//  */
// function highlightChatGPT(field, entities) {
//     if (!field) return;
    
//     console.log("🤖 ChatGPT-specific highlighting");
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     try {
//         // ChatGPT uses ProseMirror - always use flash
//         highlightFieldFlash(field, 'CHATGPT');
        
//         // Auto-cleanup after duration
//         setTimeout(() => {
//             removeHighlights(field);
//         }, HIGHLIGHT_DURATION);
//     } catch (e) {
//         console.error("❌ ChatGPT highlight error:", e);
//     }
// }

// // ==================== GEMINI-SPECIFIC HIGHLIGHTING ====================
// /**
//  * Highlight entities specifically in Gemini editor
//  * Uses purple color matching Google's design
//  */
// function highlightGemini(field, entities) {
//     if (!field) return;
    
//     console.log("✨ Gemini-specific highlighting");
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     try {
//         // Gemini uses Quill - always use flash
//         highlightFieldFlash(field, 'GEMINI');
        
//         // Auto-cleanup after duration
//         setTimeout(() => {
//             removeHighlights(field);
//         }, HIGHLIGHT_DURATION);
//     } catch (e) {
//         console.error("❌ Gemini highlight error:", e);
//     }
// }

// // ==================== AUTO-CLEANUP ====================
// /**
//  * Set up automatic highlight removal when field content changes
//  */
// function setupHighlightCleanup(field, debounceMs = 2000) {
//     if (!field) return null;
    
//     let timeout;
//     let observer;
    
//     const cleanup = () => {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => {
//             removeHighlights(field);
//         }, debounceMs);
//     };
    
//     // Listen to input events
//     field.addEventListener('input', cleanup);
//     field.addEventListener('paste', cleanup);
//     field.addEventListener('cut', cleanup);
    
//     // Also observe DOM changes
//     if (field.isContentEditable) {
//         observer = new MutationObserver(cleanup);
//         observer.observe(field, {
//             characterData: true,
//             childList: true,
//             subtree: true
//         });
//     }
    
//     // Return cleanup function
//     return () => {
//         clearTimeout(timeout);
//         field.removeEventListener('input', cleanup);
//         field.removeEventListener('paste', cleanup);
//         field.removeEventListener('cut', cleanup);
//         if (observer) observer.disconnect();
//     };
// }

// // ==================== EXPORTS ====================
// if (typeof module !== 'undefined' && module.exports) {
//     module.exports = {
//         injectHighlightStyles,
//         removeHighlights,
//         isRichEditor,
//         highlightField,
//         highlightFieldFlash,
//         highlightContentEditablePlain,
//         highlightChatGPT,
//         highlightGemini,
//         setupHighlightCleanup,
//         detectPlatform,
//         HIGHLIGHT_DURATION,
//         HIGHLIGHT_CLASS,
//         FLASH_CLASS,
//         COLORS
//     };
// }


// // day 27 final update

// // highlight.js – visual highlight engine with platform-specific styling

// // ==================== CONFIGURATION ====================
// const HIGHLIGHT_DURATION = 600; // ms
// const HIGHLIGHT_CLASS = 'presendai-highlight';
// const FLASH_CLASS = 'presendai-flash';

// // Color schemes for different platforms
// const COLORS = {
//     TEXTAREA: {
//         background: '#4A9EBD',  // Moderate ocean blue
//         color: '#FFFFFF',
//         name: 'Ocean'
//     },
//     CHATGPT: {
//         background: '#10A37F',  // Emerald green (works on dark)
//         color: '#FFFFFF',
//         name: 'Emerald'
//     },
//     GEMINI: {
//         background: '#8E4EF5',  // Vibrant purple (Google-ish)
//         color: '#FFFFFF',
//         name: 'Gemini Purple'
//     },
//     DEFAULT: {
//         background: '#FFD700',  // Gold
//         color: '#000000',
//         name: 'Gold'
//     }
// };

// // ==================== PLATFORM DETECTION ====================
// function detectPlatform(field) {
//     if (!field) return 'DEFAULT';
    
//     // Check for textarea or input
//     const tag = field.tagName?.toLowerCase();
//     if (tag === 'input' || tag === 'textarea') {
//         return 'TEXTAREA';
//     }
    
//     // Check for ChatGPT (OpenAI)
//     if (field.closest('#prompt-textarea') || 
//         field.closest('[data-testid="chat-input"]') ||
//         window.location.hostname.includes('openai.com') ||
//         window.location.hostname.includes('chatgpt.com')) {
//         return 'CHATGPT';
//     }
    
//     // Check for Gemini (Google)
//     if (field.closest('.ql-container') || 
//         field.classList?.contains('ql-editor') ||
//         window.location.hostname.includes('gemini.google.com') ||
//         document.querySelector('[data-app-id*="gemini"]')) {
//         return 'GEMINI';
//     }
    
//     return 'DEFAULT';
// }

// // ==================== STYLES ====================
// function injectHighlightStyles() {
//     const styleId = 'presendai-highlight-styles';
//     if (document.getElementById(styleId)) return;
    
//     const style = document.createElement('style');
//     style.id = styleId;
//     style.textContent = `
//         /* Base highlight styles */
//         .${HIGHLIGHT_CLASS} {
//             border-radius: 4px;
//             padding: 2px 4px;
//             margin: 0 -2px;
//             display: inline;
//             font-weight: 500;
//             transition: all 0.3s ease;
//             box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
//         }
        
//         /* Platform-specific colors */
//         .${HIGHLIGHT_CLASS}[data-platform="TEXTAREA"] {
//             background-color: ${COLORS.TEXTAREA.background} !important;
//             color: ${COLORS.TEXTAREA.color} !important;
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
//             background-color: ${COLORS.CHATGPT.background} !important;
//             color: ${COLORS.CHATGPT.color} !important;
//             box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="GEMINI"] {
//             background-color: ${COLORS.GEMINI.background} !important;
//             color: ${COLORS.GEMINI.color} !important;
//             box-shadow: 0 0 0 2px rgba(142, 78, 245, 0.2);
//         }
        
//         .${HIGHLIGHT_CLASS}[data-platform="DEFAULT"] {
//             background-color: ${COLORS.DEFAULT.background} !important;
//             color: ${COLORS.DEFAULT.color} !important;
//         }
        
//         /* Flash animation */
//         .${FLASH_CLASS} {
//             animation: presendai-flash-bg ${HIGHLIGHT_DURATION}ms ease;
//         }
        
//         /* Platform-specific flash animations */
//         @keyframes presendai-flash-bg {
//             0% { 
//                 background-color: transparent; 
//                 box-shadow: none;
//             }
//             50% { 
//                 background-color: var(--flash-color, #FFD700);
//                 box-shadow: 0 0 20px var(--flash-color, #FFD700);
//             }
//             100% { 
//                 background-color: transparent;
//                 box-shadow: none;
//             }
//         }
        
//         /* Flash variants for different platforms */
//         .${FLASH_CLASS}[data-platform="TEXTAREA"] {
//             --flash-color: ${COLORS.TEXTAREA.background};
//         }
        
//         .${FLASH_CLASS}[data-platform="CHATGPT"] {
//             --flash-color: ${COLORS.CHATGPT.background};
//         }
        
//         .${FLASH_CLASS}[data-platform="GEMINI"] {
//             --flash-color: ${COLORS.GEMINI.background};
//         }
        
//         /* Hover effects */
//         .${HIGHLIGHT_CLASS}:hover {
//             transform: translateY(-1px);
//             box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
//         }
        
//         /* Ensure highlights work in various editors */
//         .ql-editor .${HIGHLIGHT_CLASS},
//         .ProseMirror .${HIGHLIGHT_CLASS},
//         [contenteditable] .${HIGHLIGHT_CLASS} {
//             display: inline;
//             line-height: inherit;
//         }
        
//         /* Dark mode adjustments for ChatGPT */
//         .dark .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"],
//         [data-theme="dark"] .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
//             box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.4);
//         }
//     `;
//     document.head.appendChild(style);
// }

// // ==================== CLEANUP ====================
// function removeHighlights(field) {
//     if (!field) return;
    
//     try {
//         // For contenteditable fields
//         if (field.isContentEditable) {
//             const highlights = field.querySelectorAll(`.${HIGHLIGHT_CLASS}`);
            
//             // Process in reverse to avoid index issues
//             Array.from(highlights).reverse().forEach(span => {
//                 const parent = span.parentNode;
//                 if (parent && parent.contains(span)) {
//                     // Replace span with its text content
//                     const textNode = document.createTextNode(span.textContent);
//                     parent.replaceChild(textNode, span);
//                 }
//             });
            
//             // Normalize to merge adjacent text nodes
//             field.normalize();
//         }
        
//         // Remove flash class
//         field.classList?.remove(FLASH_CLASS);
//         field.removeAttribute?.('data-platform');
        
//         console.log("✨ Highlights removed");
//     } catch (e) {
//         console.error("❌ Error removing highlights:", e);
//     }
// }

// // ==================== EDITOR DETECTION ====================
// /**
//  * Detect if field is a rich text editor (Quill/ProseMirror/etc)
//  * Uses enhanced detection from dom.js if available
//  */
// function isRichEditor(field) {
//     if (!field || !field.isContentEditable) return false;
    
//     // Use dom.js functions if available
//     if (typeof findQuillInstance === 'function') {
//         if (findQuillInstance(field)) return true;
//     }
//     if (typeof findProseMirrorView === 'function') {
//         if (findProseMirrorView(field)) return true;
//     }
    
//     // Fallback detection for Quill (Gemini)
//     if (field.__quill || field._quill || field.quill) return true;
//     if (field.classList?.contains('ql-editor')) return true;
//     if (field.closest?.('.ql-container')) return true;
    
//     // Check parent chain for Quill
//     let parent = field.parentElement;
//     for (let i = 0; i < 3 && parent; i++) {
//         if (parent.__quill || parent._quill) return true;
//         parent = parent.parentElement;
//     }
    
//     // Fallback detection for ProseMirror (ChatGPT)
//     if (field._view || field.view || field.pmViewDesc) return true;
//     if (field.classList?.contains('ProseMirror')) return true;
//     if (field.closest?.('.ProseMirror')) return true;
    
//     // Check for other rich editors
//     if (field.classList?.contains('tox-edit-area')) return true; // TinyMCE
//     if (field.closest?.('.DraftEditor-root')) return true; // Draft.js
//     if (field.getAttribute?.('data-lexical-editor') === 'true') return true; // Lexical
//     if (field.querySelector?.('[data-slate-node], .slate-node')) return true; // Slate
    
//     return false;
// }

// // ==================== PLAIN CONTENTEDITABLE HIGHLIGHTING ====================
// /**
//  * Highlight specific text spans in plain contenteditable fields
//  * @param {HTMLElement} field - The contenteditable element
//  * @param {Array} entities - Array of {start, end, type} objects
//  * @param {string} platform - Platform identifier for color scheme
//  * @returns {boolean} - Success status
//  */
// function highlightContentEditablePlain(field, entities, platform) {
//     // Safety checks
//     if (!field || !field.isContentEditable) {
//         console.log("🎨 Field is not contenteditable");
//         return false;
//     }
    
//     // Skip rich editors
//     if (isRichEditor(field)) {
//         console.log("🎨 Rich editor detected, skipping per-word highlight");
//         return false;
//     }
    
//     // Check if field has complex HTML (but not our highlights)
//     const hasComplexHTML = /<(?!span\s+class="presendai-highlight")[^>]*>/.test(field.innerHTML);
//     if (hasComplexHTML) {
//         console.log("🎨 Complex HTML detected, using flash fallback");
//         return false;
//     }
    
//     try {
//         // Remove existing highlights
//         removeHighlights(field);
        
//         // Collect all text nodes
//         const walker = document.createTreeWalker(
//             field, 
//             NodeFilter.SHOW_TEXT, 
//             null
//         );
        
//         const textNodes = [];
//         let node;
//         while (node = walker.nextNode()) {
//             textNodes.push(node);
//         }
        
//         if (textNodes.length === 0) {
//             console.log("🎨 No text nodes found");
//             return false;
//         }
        
//         // Build node map with positions
//         let currentPos = 0;
//         const nodeMap = textNodes.map(node => {
//             const start = currentPos;
//             const length = node.nodeValue?.length || 0;
//             const end = currentPos + length;
//             currentPos = end;
//             return { node, start, end, length };
//         });
        
//         // Sort entities by position (reverse order for easier processing)
//         const sorted = [...entities].sort((a, b) => b.start - a.start);
        
//         // Apply highlights
//         for (const entity of sorted) {
//             const { start, end } = entity;
            
//             if (start >= end) continue; // Invalid range
            
//             // Find overlapping nodes
//             for (const item of nodeMap) {
//                 // Skip if no overlap
//                 if (start >= item.end || end <= item.start) continue;
                
//                 const node = item.node;
                
//                 // Skip if node was already removed
//                 if (!node.parentNode) continue;
                
//                 // Calculate overlap within this node
//                 const overlapStart = Math.max(start, item.start) - item.start;
//                 const overlapEnd = Math.min(end, item.end) - item.start;
                
//                 if (overlapStart >= overlapEnd) continue;
                
//                 const text = node.nodeValue || '';
//                 const before = text.substring(0, overlapStart);
//                 const middle = text.substring(overlapStart, overlapEnd);
//                 const after = text.substring(overlapEnd);
                
//                 // Create highlight span with platform color
//                 const span = document.createElement('span');
//                 span.className = HIGHLIGHT_CLASS;
//                 span.textContent = middle;
//                 span.setAttribute('data-platform', platform);
//                 span.setAttribute('data-entity-type', entity.type || 'unknown');
                
//                 // Build replacement fragment
//                 const fragment = document.createDocumentFragment();
//                 if (before) fragment.appendChild(document.createTextNode(before));
//                 fragment.appendChild(span);
//                 if (after) fragment.appendChild(document.createTextNode(after));
                
//                 // Replace in DOM
//                 const parent = node.parentNode;
//                 if (parent) {
//                     parent.replaceChild(fragment, node);
//                     item.node = null; // Mark as processed
//                 }
                
//                 // Break out of inner loop after replacement
//                 break;
//             }
//         }
        
//         // Normalize to clean up
//         field.normalize();
        
//         const colorName = COLORS[platform]?.name || 'default';
//         console.log(`🎨 Successfully highlighted ${sorted.length} entities with ${colorName} color`);
//         return true;
        
//     } catch (e) {
//         console.error("❌ Error in highlightContentEditablePlain:", e);
//         return false;
//     }
// }

// // ==================== FLASH HIGHLIGHT ====================
// /**
//  * Apply a flash animation to the entire field
//  * Used for rich editors where we can't safely manipulate DOM
//  */
// function highlightFieldFlash(field, platform) {
//     if (!field) return;
    
//     try {
//         // Set platform for color
//         field.setAttribute('data-platform', platform);
        
//         // Add flash class
//         field.classList.add(FLASH_CLASS);
        
//         // Remove after animation completes
//         setTimeout(() => {
//             field.classList.remove(FLASH_CLASS);
//             field.removeAttribute('data-platform');
//         }, HIGHLIGHT_DURATION);
        
//         const colorName = COLORS[platform]?.name || 'default';
//         console.log(`🎨 Applied ${colorName} flash highlight`);
//     } catch (e) {
//         console.error("❌ Error in highlightFieldFlash:", e);
//     }
// }

// // ==================== MAIN HIGHLIGHT FUNCTION ====================
// /**
//  * Highlight entities in a field with platform-specific colors
//  * Automatically detects platform and chooses the best highlighting method
//  * @param {HTMLElement} field - The field to highlight
//  * @param {Array} entities - Array of {start, end, type?} objects
//  */
// function highlightField(field, entities) {
//     if (!field) {
//         console.log("🎨 No field provided");
//         return;
//     }
    
//     if (!entities || entities.length === 0) {
//         console.log("🎨 No entities to highlight");
//         return;
//     }
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     // Detect platform for appropriate color scheme
//     const platform = detectPlatform(field);
//     console.log(`🎨 Platform detected: ${platform}`);
    
//     try {
//         // For standard inputs and textareas, use flash with ocean color
//         const tag = field.tagName?.toLowerCase();
//         if (tag === 'input' || tag === 'textarea') {
//             highlightFieldFlash(field, 'TEXTAREA');
//             return;
//         }
        
//         // For contenteditable fields
//         if (field.isContentEditable) {
//             // Try per-word highlighting for plain contenteditable
//             const success = highlightContentEditablePlain(field, entities, platform);
            
//             // Fall back to flash if per-word failed (rich editors)
//             if (!success) {
//                 highlightFieldFlash(field, platform);
//             }
//         } else {
//             console.log("🎨 Field is not editable, skipping highlight");
//         }
//     } catch (e) {
//         console.error("❌ Highlight error, falling back to flash:", e);
//         highlightFieldFlash(field, platform);
//     }
// }

// // ==================== CHATGPT-SPECIFIC HIGHLIGHTING ====================
// /**
//  * Highlight entities specifically in ChatGPT editor
//  * Uses emerald green color optimized for dark background
//  */
// function highlightChatGPT(field, entities) {
//     if (!field) return;
    
//     console.log("🤖 ChatGPT-specific highlighting");
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     try {
//         // ChatGPT uses ProseMirror - always use flash
//         highlightFieldFlash(field, 'CHATGPT');
        
//         // Auto-cleanup after duration
//         setTimeout(() => {
//             removeHighlights(field);
//         }, HIGHLIGHT_DURATION);
//     } catch (e) {
//         console.error("❌ ChatGPT highlight error:", e);
//     }
// }

// // ==================== GEMINI-SPECIFIC HIGHLIGHTING ====================
// /**
//  * Highlight entities specifically in Gemini editor
//  * Uses purple color matching Google's design
//  */
// function highlightGemini(field, entities) {
//     if (!field) return;
    
//     console.log("✨ Gemini-specific highlighting");
    
//     // Ensure styles are injected
//     injectHighlightStyles();
    
//     try {
//         // Gemini uses Quill - always use flash
//         highlightFieldFlash(field, 'GEMINI');
        
//         // Auto-cleanup after duration
//         setTimeout(() => {
//             removeHighlights(field);
//         }, HIGHLIGHT_DURATION);
//     } catch (e) {
//         console.error("❌ Gemini highlight error:", e);
//     }
// }

// // ==================== AUTO-CLEANUP ====================
// /**
//  * Set up automatic highlight removal when field content changes
//  */
// function setupHighlightCleanup(field, debounceMs = 2000) {
//     if (!field) return null;
    
//     let timeout;
//     let observer;
    
//     const cleanup = () => {
//         clearTimeout(timeout);
//         timeout = setTimeout(() => {
//             removeHighlights(field);
//         }, debounceMs);
//     };
    
//     // Listen to input events
//     field.addEventListener('input', cleanup);
//     field.addEventListener('paste', cleanup);
//     field.addEventListener('cut', cleanup);
    
//     // Also observe DOM changes
//     if (field.isContentEditable) {
//         observer = new MutationObserver(cleanup);
//         observer.observe(field, {
//             characterData: true,
//             childList: true,
//             subtree: true
//         });
//     }
    
//     // Return cleanup function
//     return () => {
//         clearTimeout(timeout);
//         field.removeEventListener('input', cleanup);
//         field.removeEventListener('paste', cleanup);
//         field.removeEventListener('cut', cleanup);
//         if (observer) observer.disconnect();
//     };
// }

// // ==================== EXPORTS ====================
// if (typeof module !== 'undefined' && module.exports) {
//     module.exports = {
//         injectHighlightStyles,
//         removeHighlights,
//         isRichEditor,
//         highlightField,
//         highlightFieldFlash,
//         highlightContentEditablePlain,
//         highlightChatGPT,
//         highlightGemini,
//         setupHighlightCleanup,
//         detectPlatform,
//         HIGHLIGHT_DURATION,
//         HIGHLIGHT_CLASS,
//         FLASH_CLASS,
//         COLORS
//     };
// }




// day 27 final update 

// highlight.js – visual highlight engine with platform-specific styling (PRODUCTION)

// ==================== CONFIGURATION ====================
const HIGHLIGHT_DURATION = 600; // ms
const HIGHLIGHT_CLASS = 'presendai-highlight';
const FLASH_CLASS = 'presendai-flash';

// Color schemes for different platforms
const COLORS = {
    TEXTAREA: {
        background: '#4A9EBD',  // Moderate ocean blue
        color: '#FFFFFF',
        name: 'Ocean'
    },
    CHATGPT: {
        background: '#10A37F',  // Emerald green (works on dark)
        color: '#FFFFFF',
        name: 'Emerald'
    },
    GEMINI: {
        background: '#8E4EF5',  // Vibrant purple (Google-ish)
        color: '#FFFFFF',
        name: 'Gemini Purple'
    },
    DEFAULT: {
        background: '#FFD700',  // Gold
        color: '#000000',
        name: 'Gold'
    }
};

// ==================== PLATFORM DETECTION ====================
function detectPlatform(field) {
    if (!field) return 'DEFAULT';
    
    // Check for textarea or input
    const tag = field.tagName?.toLowerCase();
    if (tag === 'input' || tag === 'textarea') {
        return 'TEXTAREA';
    }
    
    // Check for ChatGPT (OpenAI)
    if (field.closest('#prompt-textarea') || 
        field.closest('[data-testid="chat-input"]') ||
        field.id === 'prompt-textarea' ||
        window.location.hostname.includes('openai.com') ||
        window.location.hostname.includes('chatgpt.com')) {
        return 'CHATGPT';
    }
    
    // Check for Gemini (Google)
    if (field.closest('.ql-container') || 
        field.classList?.contains('ql-editor') ||
        window.location.hostname.includes('gemini.google.com') ||
        document.querySelector('[data-app-id*="gemini"]')) {
        return 'GEMINI';
    }
    
    return 'DEFAULT';
}

// ==================== STYLES ====================
function injectHighlightStyles() {
    const styleId = 'presendai-highlight-styles';
    if (document.getElementById(styleId)) return;
    
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
        /* Base highlight styles */
        .${HIGHLIGHT_CLASS} {
            border-radius: 4px;
            padding: 2px 4px;
            margin: 0 -2px;
            display: inline;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }
        
        /* Platform-specific colors */
        .${HIGHLIGHT_CLASS}[data-platform="TEXTAREA"] {
            background-color: ${COLORS.TEXTAREA.background} !important;
            color: ${COLORS.TEXTAREA.color} !important;
        }
        
        .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
            background-color: ${COLORS.CHATGPT.background} !important;
            color: ${COLORS.CHATGPT.color} !important;
            box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
        }
        
        .${HIGHLIGHT_CLASS}[data-platform="GEMINI"] {
            background-color: ${COLORS.GEMINI.background} !important;
            color: ${COLORS.GEMINI.color} !important;
            box-shadow: 0 0 0 2px rgba(142, 78, 245, 0.2);
        }
        
        .${HIGHLIGHT_CLASS}[data-platform="DEFAULT"] {
            background-color: ${COLORS.DEFAULT.background} !important;
            color: ${COLORS.DEFAULT.color} !important;
        }
        
        /* Flash animation */
        .${FLASH_CLASS} {
            animation: presendai-flash-bg ${HIGHLIGHT_DURATION}ms ease;
        }
        
        /* Platform-specific flash animations */
        @keyframes presendai-flash-bg {
            0% { 
                background-color: transparent; 
                box-shadow: none;
            }
            50% { 
                background-color: var(--flash-color, #FFD700);
                box-shadow: 0 0 20px var(--flash-color, #FFD700);
            }
            100% { 
                background-color: transparent;
                box-shadow: none;
            }
        }
        
        /* Flash variants for different platforms */
        .${FLASH_CLASS}[data-platform="TEXTAREA"] {
            --flash-color: ${COLORS.TEXTAREA.background};
        }
        
        .${FLASH_CLASS}[data-platform="CHATGPT"] {
            --flash-color: ${COLORS.CHATGPT.background};
        }
        
        .${FLASH_CLASS}[data-platform="GEMINI"] {
            --flash-color: ${COLORS.GEMINI.background};
        }
        
        /* Hover effects */
        .${HIGHLIGHT_CLASS}:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        
        /* Ensure highlights work in various editors */
        .ql-editor .${HIGHLIGHT_CLASS},
        .ProseMirror .${HIGHLIGHT_CLASS},
        [contenteditable] .${HIGHLIGHT_CLASS} {
            display: inline;
            line-height: inherit;
        }
        
        /* Dark mode adjustments for ChatGPT */
        .dark .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"],
        [data-theme="dark"] .${HIGHLIGHT_CLASS}[data-platform="CHATGPT"] {
            box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.4);
        }
    `;
    document.head.appendChild(style);
    console.log("🎨 Highlight styles injected");
}

// ==================== CLEANUP ====================
function removeHighlights(field) {
    if (!field) return;
    
    try {
        // For contenteditable fields
        if (field.isContentEditable) {
            const highlights = field.querySelectorAll(`.${HIGHLIGHT_CLASS}`);
            
            // Process in reverse to avoid index issues
            Array.from(highlights).reverse().forEach(span => {
                const parent = span.parentNode;
                if (parent && parent.contains(span)) {
                    const textNode = document.createTextNode(span.textContent);
                    parent.replaceChild(textNode, span);
                }
            });
            
            // Normalize to merge adjacent text nodes
            field.normalize();
        }
        
        // Remove flash class
        field.classList?.remove(FLASH_CLASS);
        field.removeAttribute?.('data-platform');
        
    } catch (e) {
        console.debug("Highlight cleanup error (non-fatal):", e);
    }
}

// ==================== EDITOR DETECTION ====================
function isRichEditor(field) {
    if (!field || !field.isContentEditable) return false;
    
    // Use dom.js functions if available
    if (typeof findQuillInstance === 'function') {
        if (findQuillInstance(field)) return true;
    }
    if (typeof findProseMirrorView === 'function') {
        if (findProseMirrorView(field)) return true;
    }
    
    // Fallback detection for Quill (Gemini)
    if (field.__quill || field._quill || field.quill) return true;
    if (field.classList?.contains('ql-editor')) return true;
    if (field.closest?.('.ql-container')) return true;
    
    // Check parent chain
    let parent = field.parentElement;
    for (let i = 0; i < 3 && parent; i++) {
        if (parent.__quill || parent._quill) return true;
        parent = parent.parentElement;
    }
    
    // Fallback detection for ProseMirror (ChatGPT)
    if (field._view || field.view || field.pmViewDesc) return true;
    if (field.classList?.contains('ProseMirror')) return true;
    if (field.closest?.('.ProseMirror')) return true;
    
    // Check for other rich editors
    if (field.classList?.contains('tox-edit-area')) return true;
    if (field.closest?.('.DraftEditor-root')) return true;
    if (field.getAttribute?.('data-lexical-editor') === 'true') return true;
    if (field.querySelector?.('[data-slate-node], .slate-node')) return true;
    
    return false;
}

// ==================== PLAIN CONTENTEDITABLE HIGHLIGHTING ====================
function highlightContentEditablePlain(field, entities, platform) {
    // Safety checks
    if (!field || !field.isContentEditable) {
        return false;
    }
    
    // Skip rich editors - they need flash
    if (isRichEditor(field)) {
        return false;
    }
    
    // Check if field has complex HTML (not just text and our spans)
    const innerHTML = field.innerHTML;
    if (/<(?!span\s+class="presendai-highlight"|\/span>)[^>]+>/.test(innerHTML)) {
        console.log("⚠️ Field contains HTML – falling back to flash");
        return false;
    }
    
    try {
        // Remove existing highlights first
        removeHighlights(field);
        
        // Wait a tick for DOM to settle after cleanup
        // This prevents the "reading properties of null" error
        
        // Collect all text nodes AFTER cleanup
        const walker = document.createTreeWalker(
            field, 
            NodeFilter.SHOW_TEXT, 
            null
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            // Only add if node is still in the document
            if (node.parentNode && field.contains(node)) {
                textNodes.push(node);
            }
        }
        
        if (textNodes.length === 0) {
            return false;
        }
        
        // Build node map with positions
        let currentPos = 0;
        const nodeMap = [];
        
        for (const node of textNodes) {
            const start = currentPos;
            const length = node.nodeValue?.length || 0;
            const end = currentPos + length;
            currentPos = end;
            nodeMap.push({ node, start, end, length, processed: false });
        }
        
        // Sort entities by position (reverse for easier processing)
        const sorted = [...entities].sort((a, b) => b.start - a.start);
        
        let highlightCount = 0;
        
        // Apply highlights
        for (const entity of sorted) {
            const { start, end } = entity;
            
            if (start >= end || start < 0) continue; // Invalid range
            
            // Find overlapping nodes
            for (const item of nodeMap) {
                if (item.processed) continue; // Skip already processed nodes
                
                // Skip if no overlap
                if (start >= item.end || end <= item.start) continue;
                
                const node = item.node;
                
                // Critical: Check if node is still valid and in DOM
                if (!node || !node.parentNode || !field.contains(node)) {
                    item.processed = true;
                    continue;
                }
                
                // Calculate overlap within this node
                const overlapStart = Math.max(start, item.start) - item.start;
                const overlapEnd = Math.min(end, item.end) - item.start;
                
                if (overlapStart >= overlapEnd) continue;
                
                const text = node.nodeValue || '';
                if (overlapStart > text.length || overlapEnd > text.length) {
                    item.processed = true;
                    continue;
                }
                
                const before = text.substring(0, overlapStart);
                const middle = text.substring(overlapStart, overlapEnd);
                const after = text.substring(overlapEnd);
                
                // Create highlight span with platform color
                const span = document.createElement('span');
                span.className = HIGHLIGHT_CLASS;
                span.textContent = middle;
                span.setAttribute('data-platform', platform);
                span.setAttribute('data-entity-type', entity.type || 'unknown');
                
                // Build replacement fragment
                const fragment = document.createDocumentFragment();
                if (before) fragment.appendChild(document.createTextNode(before));
                fragment.appendChild(span);
                if (after) fragment.appendChild(document.createTextNode(after));
                
                // Store parent before replacement
                const parent = node.parentNode;
                
                // Double-check parent is valid
                if (!parent || !field.contains(parent)) {
                    item.processed = true;
                    continue;
                }
                
                try {
                    // Replace in DOM
                    parent.replaceChild(fragment, node);
                    item.processed = true;
                    highlightCount++;
                } catch (replaceError) {
                    console.debug("Node replacement failed (non-fatal):", replaceError);
                    item.processed = true;
                }
                
                // Break after successful replacement
                break;
            }
        }
        
        // Normalize to clean up
        try {
            field.normalize();
        } catch (e) {
            console.debug("Normalize failed (non-fatal):", e);
        }
        
        if (highlightCount > 0) {
            const colorName = COLORS[platform]?.name || 'default';
            console.log(`🎨 Highlighted ${highlightCount} entities with ${colorName} color`);
            return true;
        }
        
        return false;
        
    } catch (e) {
        console.debug("Highlight error (falling back to flash):", e);
        return false;
    }
}

// ==================== FLASH HIGHLIGHT ====================
function highlightFieldFlash(field, platform) {
    if (!field) return;
    
    try {
        // Remove any existing highlights first
        removeHighlights(field);
        
        // Set platform for color
        field.setAttribute('data-platform', platform);
        
        // Add flash class
        field.classList.add(FLASH_CLASS);
        
        // Remove after animation completes
        setTimeout(() => {
            field.classList.remove(FLASH_CLASS);
            field.removeAttribute('data-platform');
        }, HIGHLIGHT_DURATION);
        
        const colorName = COLORS[platform]?.name || 'default';
        console.log(`🎨 Applied ${colorName} flash highlight`);
    } catch (e) {
        console.error("❌ Flash highlight error:", e);
    }
}

// ==================== MAIN HIGHLIGHT FUNCTION ====================
function highlightField(field, entities) {
    if (!field) {
        console.log("🎨 No field provided");
        return;
    }
    
    if (!entities || entities.length === 0) {
        console.log("🎨 No entities to highlight");
        return;
    }
    
    // Ensure styles are injected
    injectHighlightStyles();
    
    // Detect platform for appropriate color scheme
    const platform = detectPlatform(field);
    console.log(`🎨 Platform detected: ${platform}`);
    
    try {
        // For standard inputs and textareas
        const tag = field.tagName?.toLowerCase();
        if (tag === 'input' || tag === 'textarea') {
            highlightFieldFlash(field, 'TEXTAREA');
            return;
        }
        
        // For contenteditable fields
        if (field.isContentEditable) {
            // Try per-word highlighting for plain contenteditable
            const success = highlightContentEditablePlain(field, entities, platform);
            
            // Fall back to flash if per-word failed
            if (!success) {
                highlightFieldFlash(field, platform);
            }
        } else {
            console.log("🎨 Field is not editable, skipping");
        }
    } catch (e) {
        console.error("❌ Highlight error, using flash fallback:", e);
        try {
            highlightFieldFlash(field, platform);
        } catch (flashError) {
            console.error("❌ Flash fallback also failed:", flashError);
        }
    }
}

// ==================== CHATGPT-SPECIFIC ====================
function highlightChatGPT(field, entities) {
    if (!field) return;
    injectHighlightStyles();
    highlightFieldFlash(field, 'CHATGPT');
}

// ==================== GEMINI-SPECIFIC ====================
function highlightGemini(field, entities) {
    if (!field) return;
    injectHighlightStyles();
    highlightFieldFlash(field, 'GEMINI');
}

// ==================== AUTO-CLEANUP ====================
function setupHighlightCleanup(field, debounceMs = 2000) {
    if (!field) return null;
    
    let timeout;
    let observer;
    
    const cleanup = () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            removeHighlights(field);
        }, debounceMs);
    };
    
    field.addEventListener('input', cleanup);
    field.addEventListener('paste', cleanup);
    field.addEventListener('cut', cleanup);
    
    if (field.isContentEditable) {
        observer = new MutationObserver(cleanup);
        observer.observe(field, {
            characterData: true,
            childList: true,
            subtree: true
        });
    }
    
    return () => {
        clearTimeout(timeout);
        field.removeEventListener('input', cleanup);
        field.removeEventListener('paste', cleanup);
        field.removeEventListener('cut', cleanup);
        if (observer) observer.disconnect();
    };
}

// ==================== EXPORTS ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        injectHighlightStyles,
        removeHighlights,
        isRichEditor,
        highlightField,
        highlightFieldFlash,
        highlightContentEditablePlain,
        highlightChatGPT,
        highlightGemini,
        setupHighlightCleanup,
        detectPlatform,
        HIGHLIGHT_DURATION,
        HIGHLIGHT_CLASS,
        FLASH_CLASS,
        COLORS
    };
}