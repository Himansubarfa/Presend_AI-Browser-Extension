// content.js – injected into every page
console.log("🔒 PreSendAI content script loaded");

// You can add a simple listener to test later
document.addEventListener("input", (e) => {
  const target = e.target;
  if (target.tagName === "TEXTAREA" || target.tagName === "INPUT" || target.isContentEditable) {
    console.log("Typing detected in editable field:", target.value || target.innerText);
  }
});