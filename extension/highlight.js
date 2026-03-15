// highlight.js – visual highlight engine
// NOTE: HIGHLIGHT_DURATION is declared as a constant in content.js.
// Do NOT re-declare it here to avoid the duplicate-variable shadowing bug
// that caused content.js to use an undefined value at runtime.

function injectHighlightStyles() {
    const id = 'presendai-highlight-styles';
    if (document.getElementById(id)) return;
    const style = document.createElement('style');
    style.id = id;
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
            0%   { background-color: inherit; }
            50%  { background-color: #fff2b0; }
            100% { background-color: inherit; }
        }
    `;
    document.head.appendChild(style);
}

function removeHighlights(field) {
    if (!field.isContentEditable) return;
    field.querySelectorAll('.presendai-highlight').forEach(span => {
        const parent = span.parentNode;
        if (parent) {
            parent.replaceChild(document.createTextNode(span.textContent), span);
            parent.normalize();
        }
    });
}

function highlightContentEditablePlain(field, entities) {
    if (/<[^>]*>/.test(field.innerHTML) &&
        !field.innerHTML.includes('<span class="presendai-highlight">')) {
        console.warn("⚠️ Field contains HTML – falling back to flash");
        return false;
    }

    removeHighlights(field);

    const walker = document.createTreeWalker(field, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    let node;
    while ((node = walker.nextNode())) textNodes.push(node);

    let pos = 0;
    const nodeMap = textNodes.map(n => {
        const start = pos;
        pos += n.nodeValue.length;
        return { node: n, start, end: pos };
    });

    const sorted = [...entities].sort((a, b) => b.start - a.start);

    for (const ent of sorted) {
        for (const item of nodeMap) {
            if (ent.start >= item.end || ent.end <= item.start) continue;

            const oStart = Math.max(ent.start, item.start);
            const oEnd   = Math.min(ent.end,   item.end);
            if (oStart >= oEnd) continue;

            const text   = item.node.nodeValue;
            const before = text.substring(0, oStart - item.start);
            const middle = text.substring(oStart - item.start, oEnd - item.start);
            const after  = text.substring(oEnd - item.start);

            const span = document.createElement('span');
            span.className = 'presendai-highlight';
            span.textContent = middle;

            const frag = document.createDocumentFragment();
            if (before) frag.appendChild(document.createTextNode(before));
            frag.appendChild(span);
            if (after)  frag.appendChild(document.createTextNode(after));

            item.node.parentNode.replaceChild(frag, item.node);
            break;
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
            if (!highlightContentEditablePlain(field, entities)) highlightFieldFlash(field);
        } else {
            highlightFieldFlash(field);
        }
    } catch (e) {
        console.error("❌ Highlight error, falling back to flash:", e);
        highlightFieldFlash(field);
    }
}