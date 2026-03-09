// // popup.js – simple popup logic
// document.getElementById("toggle").addEventListener("click", () => {
//   // Placeholder: toggle enabled state
//   alert("Toggle feature coming soon!");
// });

// day 20 update 

// popup.js – controls enable/disable toggle

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('toggle');
  const indicator = document.getElementById('stateIndicator');

  // Load current state from storage
  chrome.storage.local.get('enabled', (data) => {
    const enabled = data.enabled !== false; // default to true
    toggle.checked = enabled;
    updateIndicator(enabled);
  });

  // Listen for toggle changes
  toggle.addEventListener('change', () => {
    const enabled = toggle.checked;
    chrome.storage.local.set({ enabled });
    updateIndicator(enabled);
    // Optionally notify content scripts (they listen to storage changes)
  });

  function updateIndicator(enabled) {
    indicator.textContent = enabled ? '🟢 Active' : '🔴 Inactive';
    indicator.style.backgroundColor = enabled ? '#4CAF50' : '#f44336';
    indicator.style.color = 'white';
  }
});