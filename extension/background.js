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
// console.log("🔧 PreSendAI background worker started – script executed");

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   console.log("Background received message:", request);
//   if (request.action === "maskText") {
//     const { text, url } = request;
//     console.log("Background: masking text:", text);

//     fetch(url, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ text })
//     })
//       .then(response => {
//         console.log("Background fetch response status:", response.status);
//         if (!response.ok) {
//           throw new Error(`HTTP ${response.status}`);
//         }
//         return response.json();
//       })
//       .then(data => {
//         console.log("Background fetch success, sending response");
//         sendResponse({ success: true, data });
//       })
//       .catch(error => {
//         console.error("Background fetch error:", error);
//         sendResponse({ success: false, error: error.message });
//       });

//     return true; // indicates async response
//   }
// });


// DAY 17 FINAL CODE CHANGE 
// background.js – handles fetch requests from content scripts

// console.log("🔧 PreSendAI background worker started – script executed");

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//   console.log("Background received message:", request);
//   if (request.action === "maskText") {
//     const { text, url } = request;
//     console.log("Background: masking text:", text);

//     fetch(url, {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ text })
//     })
//       .then(response => {
//         console.log("Background fetch response status:", response.status);
//         if (!response.ok) {
//           return response.text().then(errorText => {
//             throw new Error(`HTTP ${response.status}: ${errorText}`);
//           });
//         }
//         return response.json();
//       })
//       .then(data => {
//         console.log("Background fetch success, sending response");
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


// DAY 18 FINAL CODE 
// background.js – with keep‑alive and robust error handling
// console.log("🔧 PreSendAI background worker started – script executed");

// // Keep‑alive: maintain a port with all active content scripts
// const ports = new Set();

// chrome.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// // Optional: ping every 25 seconds to keep worker alive
// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 25000);

// // Message handler
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log("Background received message:", request);
//     if (request.action === "maskText") {
//         const { text, url } = request;
//         console.log("Background: masking text:", text);

//         fetch(url, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         })
//             .then(async response => {
//                 console.log("Background fetch response status:", response.status);
//                 if (!response.ok) {
//                     const errorText = await response.text();
//                     throw new Error(`HTTP ${response.status}: ${errorText}`);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log("Background fetch success, sending response");
//                 sendResponse({ success: true, data });
//             })
//             .catch(error => {
//                 console.error("Background fetch error:", error);
//                 sendResponse({ success: false, error: error.message });
//             });

//         // Return true to indicate we'll respond asynchronously
//         return true;
//     }
// });



// day 19 update 

// background.js – with keep‑alive and message handling
// console.log("🔧 PreSendAI background worker started – script executed");

// // Keep‑alive: maintain a port with all active content scripts
// const ports = new Set();

// chrome.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// // Ping every 25 seconds to keep worker alive
// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 25000);

// // Message handler (unchanged)
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log("Background received message:", request);
//     if (request.action === "maskText") {
//         const { text, url } = request;
//         console.log("Background: masking text:", text);

//         fetch(url, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         })
//             .then(async response => {
//                 console.log("Background fetch response status:", response.status);
//                 if (!response.ok) {
//                     const errorText = await response.text();
//                     throw new Error(`HTTP ${response.status}: ${errorText}`);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log("Background fetch success, sending response");
//                 sendResponse({ success: true, data });
//             })
//             .catch(error => {
//                 console.error("Background fetch error:", error);
//                 sendResponse({ success: false, error: error.message });
//             });

//         // Return true to indicate we'll respond asynchronously
//         return true;
//     }
// });


// day 19 final update 

// background.js – with keep‑alive and message handling
// console.log("🔧 PreSendAI background worker started – script executed");

// // Keep‑alive: maintain a port with all active content scripts
// const ports = new Set();

// chrome.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// // Ping every 25 seconds to keep worker alive
// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 25000);

// // Message handler
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log("Background received message:", request);
//     if (request.action === "maskText") {
//         const { text, url } = request;
//         console.log("Background: masking text:", text);

//         fetch(url, {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({ text })
//         })
//             .then(async response => {
//                 console.log("Background fetch response status:", response.status);
//                 if (!response.ok) {
//                     const errorText = await response.text();
//                     throw new Error(`HTTP ${response.status}: ${errorText}`);
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log("Background fetch success, sending response");
//                 sendResponse({ success: true, data });
//             })
//             .catch(error => {
//                 console.error("Background fetch error:", error);
//                 sendResponse({ success: false, error: error.message });
//             });

//         // Return true to indicate we'll respond asynchronously
//         return true;
//     }
// });


// day 21 update 
if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
    var browser = chrome;
}
console.log("🔧 PreSendAI background worker started – script executed");

const ports = new Set();

browser.runtime.onConnect.addListener((port) => {
    if (port.name === "presendai-keepalive") {
        ports.add(port);
        port.onDisconnect.addListener(() => ports.delete(port));
    }
});

setInterval(() => {
    ports.forEach(port => {
        try {
            port.postMessage({ type: "ping" });
        } catch (e) {
            ports.delete(port);
        }
    });
}, 25000);

browser.alarms.create('keepAlive', { periodInMinutes: 1 });
browser.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'keepAlive') {
        console.log("Alarm triggered – worker staying alive");
    }
});

browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Background received message:", request);
    if (request.action === "maskText") {
        const { text, url } = request;
        console.log("Background: masking text:", text);

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        })
            .then(async response => {
                console.log("Background fetch response status:", response.status);
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP ${response.status}: ${errorText}`);
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

        return true;
    }
});