// popup.js – Day 22 (unchanged, works in all browsers)

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('toggle');
  const indicator = document.getElementById('stateIndicator');

  chrome.storage.local.get('enabled', (data) => {
    const enabled = data.enabled !== false;
    toggle.checked = enabled;
    updateIndicator(enabled);
  });

  toggle.addEventListener('change', () => {
    const enabled = toggle.checked;
    chrome.storage.local.set({ enabled });
    updateIndicator(enabled);
  });

  function updateIndicator(enabled) {
    indicator.textContent = enabled ? '🟢 Active' : '🔴 Inactive';
    indicator.style.backgroundColor = enabled ? '#4CAF50' : '#f44336';
    indicator.style.color = 'white';
  }
});