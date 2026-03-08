// // background.js – service worker
// console.log("🔧 PreSendAI background worker started");

// // Placeholder for future messaging or state management



// new update from day 13 

// background.js – handles fetch requests from content scripts

// console.log("🔧 PreSendAI background worker started");

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   if (request.action === "maskText") {
//     const { text, url } = request;
//     console.log("Background: masking text:", text);

//     fetch(url, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ text })
//     })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error(`HTTP ${response.status}`);
//         }
//         return response.json();
//       })
//       .then(data => {
//         sendResponse({ success: true, data });
//       })
//       .catch(error => {
//         console.error("Background fetch error:", error);
//         sendResponse({ success: false, error: error.message });
//       });

//     // Return true to indicate we'll respond asynchronously
//     return true;
//   }
// });


// New update from day 13

// background.js – handles fetch requests from content scripts

// console.log("🔧 PreSendAI background worker started");

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   if (request.action === "maskText") {
//     const { text, url } = request;
//     console.log("Background: masking text:", text);

//     fetch(url, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ text })
//     })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error(`HTTP ${response.status}`);
//         }
//         return response.json();
//       })
//       .then(data => {
//         sendResponse({ success: true, data });
//       })
//       .catch(error => {
//         console.error("Background fetch error:", error);
//         sendResponse({ success: false, error: error.message });
//       });

//     // Return true to indicate we'll respond asynchronously
//     return true;
//   }
// });


// New update day 13 
// background.js
console.log("🔧 PreSendAI background worker started – script executed");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Background received message:", request);
  if (request.action === "maskText") {
    const { text, url } = request;
    console.log("Background: masking text:", text);

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    })
      .then(response => {
        console.log("Background fetch response status:", response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Background fetch success, sending response");
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error("Background fetch error:", error);
        sendResponse({ success: false, error: error.message });
      });

    return true; // indicates async response
  }
});