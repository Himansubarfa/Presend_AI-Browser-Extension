// file_interceptor.js – direct fetch only for guaranteed demo
(async function() {
  'use strict';

  const REDACTABLE_TYPES = [
    'image/png', 'image/jpeg', 'image/jpg',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ];

  function isRedactable(file) {
    return REDACTABLE_TYPES.includes(file.type) ||
           file.name.endsWith('.pdf') ||
           file.name.endsWith('.docx') ||
           file.name.endsWith('.jpg') ||
           file.name.endsWith('.jpeg') ||
           file.name.endsWith('.png');
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

  async function redactFile(file) {
    const formData = new FormData();
    const endpoint = file.type.startsWith('image/') ?
      'https://localhost:5000/scan/image' :
      'https://localhost:5000/scan/document';
    formData.append(file.type.startsWith('image/') ? 'image' : 'file', file, file.name);

    try {
      const res = await fetch(endpoint, { method: 'POST', body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const b64 = data.redacted_image_base64 || data.redacted_file_base64;
      if (!b64) throw new Error('No redacted data');

      let mime = file.type;
      if (!mime || mime === 'application/octet-stream') {
        if (file.name.endsWith('.pdf')) mime = 'application/pdf';
        else if (file.name.match(/\.(jpg|jpeg)$/i)) mime = 'image/jpeg';
        else if (file.name.endsWith('.png')) mime = 'image/png';
        else if (file.name.endsWith('.docx')) mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      }

      const blob = b64toBlob(b64, mime);
      const newName = data.redacted_filename || ('redacted_' + file.name);
      console.log('PreSendAI: redacted file ready', newName, 'size:', blob.size);
      return new File([blob], newName, { type: mime, lastModified: Date.now() });
    } catch (e) {
      console.error('PreSendAI: direct fetch failed', e);
      return file; // fallback to original
    }
  }

  const processedFiles = new WeakSet();

  async function processFiles(input) {
    const files = Array.from(input.files || []);
    const redactedFiles = [];
    for (const file of files) {
      if (processedFiles.has(file)) {
        redactedFiles.push(file);
        continue;
      }
      if (isRedactable(file)) {
        const redacted = await redactFile(file);
        processedFiles.add(redacted);
        redactedFiles.push(redacted);
      } else {
        redactedFiles.push(file);
      }
    }
    const dt = new DataTransfer();
    redactedFiles.forEach(f => dt.items.add(f));
    input.files = dt.files;
  }

  function hookFileInputs() {
    document.querySelectorAll('input[type="file"]').forEach(input => {
      if (input.dataset.presendaiHooked) return;
      input.dataset.presendaiHooked = 'true';
      input.addEventListener('change', () => processFiles(input));
    });
  }

  hookFileInputs();
  new MutationObserver(() => hookFileInputs()).observe(document.body, { childList: true, subtree: true });
})();