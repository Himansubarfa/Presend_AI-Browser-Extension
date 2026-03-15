// dom.js – DOM utilities for editable fields
// Depends on: trackedFields (WeakSet declared in content.js, loaded before this)

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

// ==================== SET TEXT (with editor detection) ====================
function setFieldText(field, newText) {
    const tag = field.tagName.toLowerCase();

    if (tag === 'input' || tag === 'textarea') {
        field.value = newText;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        return;
    }

    if (!field.isContentEditable) return;

    try {
        // Quill (used by Gemini, some Gmail editors)
        const quill = field.__quill || field._quill
            || field.closest?.('.ql-container')?.__quill
            || field.closest?.('.ql-container')?._quill;
        if (quill) {
            quill.setText(newText);
            return;
        }

        // ProseMirror (used by ChatGPT, Notion, Linear)
        const isPM = field.classList?.contains('ProseMirror') || !!field.closest?.('.ProseMirror');
        if (isPM) {
            const view = field._view || field.view
                || field.parentElement?._view || field.parentElement?.view;
            if (view) {
                const { state } = view;
                const tr = state.tr.replaceWith(
                    0,
                    state.doc.content.size,
                    state.schema.text(newText)
                );
                view.dispatch(tr);
                return;
            }
        }

        // Generic contenteditable fallback
        // NOTE: deliberately NOT dispatching blur() — it steals focus and can
        // cause React/Vue/Angular to commit/reset form state mid-edit.
        field.innerText = newText;
        field.dispatchEvent(new Event('input',  { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));

    } catch (e) {
        console.error("❌ setFieldText error:", e);
        // Last-resort: bare assignment
        try {
            field.innerText = newText;
            field.dispatchEvent(new Event('input', { bubbles: true }));
        } catch (_) { /* nothing left to try */ }
    }
}

// ==================== CURSOR PRESERVATION ====================
function saveCursorPosition(field) {
    const tag = field.tagName.toLowerCase();
    if (tag === 'input' || tag === 'textarea') {
        return { type: 'input', start: field.selectionStart, end: field.selectionEnd };
    }
    if (field.isContentEditable) {
        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0) return null;
        const range = sel.getRangeAt(0);
        if (!field.contains(range.startContainer)) return null;
        const pre = range.cloneRange();
        pre.selectNodeContents(field);
        pre.setEnd(range.startContainer, range.startOffset);
        return { type: 'contenteditable', offset: pre.toString().length };
    }
    return null;
}

function restoreCursorPosition(field, saved, newText) {
    if (!saved) return;
    try {
        const tag = field.tagName.toLowerCase();
        if (saved.type === 'input' && (tag === 'input' || tag === 'textarea')) {
            const len = newText.length;
            field.setSelectionRange(
                Math.min(saved.start, len),
                Math.min(saved.end,   len)
            );
        } else if (saved.type === 'contenteditable' && field.isContentEditable) {
            const offset   = Math.min(saved.offset, newText.length);
            const textNode = field.firstChild;
            if (textNode && textNode.nodeType === Node.TEXT_NODE) {
                const range = document.createRange();
                range.setStart(textNode, offset);
                range.collapse(true);
                const sel = window.getSelection();
                if (sel) { sel.removeAllRanges(); sel.addRange(range); }
            }
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
        return getEditorFromClipboard(target) || null; // null = skip
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