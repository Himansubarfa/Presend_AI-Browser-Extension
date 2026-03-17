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


// // day 21 update 
// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔧 PreSendAI background worker started – script executed");

// const ports = new Set();

// browser.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 25000);

// browser.alarms.create('keepAlive', { periodInMinutes: 1 });
// browser.alarms.onAlarm.addListener((alarm) => {
//     if (alarm.name === 'keepAlive') {
//         console.log("Alarm triggered – worker staying alive");
//     }
// });

// browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
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

//         return true;
//     }
// });

//  day 21 upate

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔧 PreSendAI background worker started – script executed");

// const ports = new Set();

// browser.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 25000);

// browser.alarms.create('keepAlive', { periodInMinutes: 1 });
// browser.alarms.onAlarm.addListener((alarm) => {
//     if (alarm.name === 'keepAlive') {
//         console.log("Alarm triggered – worker staying alive");
//     }
// });

// browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
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

//         return true;
//     }
// });


// background.js – Day 22: cross‑browser stable worker with alarms and port keep‑alive

// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
// console.log("🔧 PreSendAI background worker started – script executed");

// const ports = new Set();

// browser.runtime.onConnect.addListener((port) => {
//     if (port.name === "presendai-keepalive") {
//         ports.add(port);
//         port.onDisconnect.addListener(() => ports.delete(port));
//     }
// });

// // Keep‑alive pings to connected ports (every 20 seconds)
// setInterval(() => {
//     ports.forEach(port => {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port);
//         }
//     });
// }, 20000);

// // Alarms to wake the service worker every minute (prevents idle sleep)
// browser.alarms.create('keepAlive', { periodInMinutes: 1 });
// browser.alarms.onAlarm.addListener((alarm) => {
//     if (alarm.name === 'keepAlive') {
//         console.log("⏰ Alarm triggered – worker staying alive");
//     }
// });

// // Message handler
// browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log("Background received message:", request);

//     if (request.action === "ping") {
//         // just a keep‑alive, no response needed
//         return false;
//     }

//     if (request.action === "maskText") {
//         const { text, url } = request;
//         console.log("Background: masking text:", text.substring(0, 100) + (text.length > 100 ? "…" : ""));

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

// day 23 claude 
// if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
//     var browser = chrome;
// }
const browser = (() => {
    if (typeof chrome !== 'undefined' && chrome.runtime) return chrome;
    if (typeof browser !== 'undefined' && browser.runtime) return browser;
    return null;
})();
console.log("🔧 PreSendAI background worker started");

// ==================== KEEP-ALIVE PORTS ====================
const ports = new Set();

browser.runtime.onConnect.addListener((port) => {
    if (port.name !== "presendai-keepalive") return;
    ports.add(port);
    port.onDisconnect.addListener(() => ports.delete(port));
});

// Ping connected ports every 20 s to prevent idle suspension
setInterval(() => {
    for (const port of ports) {
        try {
            port.postMessage({ type: "ping" });
        } catch (e) {
            ports.delete(port); // port disconnected
        }
    }
}, 20000);

// ==================== SERVICE WORKER ALARM ====================
browser.alarms.create('keepAlive', { periodInMinutes: 1 });
browser.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'keepAlive') {
        console.log("⏰ keepAlive alarm fired");
    }
});

// ==================== MESSAGE HANDLER ====================
browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Validate sender — only accept messages from our own extension tabs/frames
    if (sender.extensionId && sender.extensionId !== browser.runtime.id) {
        console.warn("⚠️ Message from unexpected sender:", sender.id);
        return false;
    }

    if (request.action === "ping") {
        // Keep-alive – no response needed
        return false;
    }   

    if (request.action === "maskText") {
        const { text, url } = request;

        // Basic guard: reject obviously bad payloads before hitting the network
        if (typeof text !== 'string' || !text.trim()) {
            sendResponse({ success: false, error: "Empty or invalid text payload" });
            return false;
        }
        // if (typeof url !== 'string' || !url.startsWith('https://')) {
        //     sendResponse({ success: false, error: "Invalid or non-HTTPS backend URL" });
        //     return false;
        // }
        const isValidUrl = typeof url === 'string' && url.startsWith('https://');
        if (!isValidUrl) {
        sendResponse({ success: false, error: "Invalid or non-HTTPS backend URL" });
        return false;
}

        console.log("Background: relaying text to backend (first 100 chars):",
            text.substring(0, 100) + (text.length > 100 ? "…" : ""));

        fetch(url, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ text }),
        })
        .then(async (response) => {
            if (!response.ok) {
                const errorBody = await response.text().catch(() => '');
                throw new Error(`HTTP ${response.status}: ${errorBody}`);
            }
            return response.json();
        })
        .then((data) => {
            sendResponse({ success: true, data });
        })
        .catch((error) => {
            console.error("Background fetch error:", error.message);
            sendResponse({ success: false, error: error.message });
        });

        // Must return true to keep the message channel open for the async sendResponse
        return true;
    }

    // Unknown action — don't leave the channel hanging
    console.warn("Background: unknown action:", request.action);
    sendResponse({ success: false, error: `Unknown action: ${request.action}` });
    return false;
});


