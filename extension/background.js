
// // day 23 claude 
// // if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
// //     var browser = chrome;
// // }
// const browser = (() => {
//     if (typeof chrome !== 'undefined' && chrome.runtime) return chrome;
//     if (typeof browser !== 'undefined' && browser.runtime) return browser;
//     return null;
// })();
// console.log("🔧 PreSendAI background worker started");

// // ==================== KEEP-ALIVE PORTS ====================
// const ports = new Set();

// browser.runtime.onConnect.addListener((port) => {
//     if (port.name !== "presendai-keepalive") return;
//     ports.add(port);
//     port.onDisconnect.addListener(() => ports.delete(port));
// });

// // Ping connected ports every 20 s to prevent idle suspension
// setInterval(() => {
//     for (const port of ports) {
//         try {
//             port.postMessage({ type: "ping" });
//         } catch (e) {
//             ports.delete(port); // port disconnected
//         }
//     }
// }, 20000);

// // ==================== SERVICE WORKER ALARM ====================
// browser.alarms.create('keepAlive', { periodInMinutes: 1 });
// browser.alarms.onAlarm.addListener((alarm) => {
//     if (alarm.name === 'keepAlive') {
//         console.log("⏰ keepAlive alarm fired");
//     }
// });

// // ==================== MESSAGE HANDLER ====================
// browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     // Validate sender — only accept messages from our own extension tabs/frames
//     if (sender.extensionId && sender.extensionId !== browser.runtime.id) {
//         console.warn("⚠️ Message from unexpected sender:", sender.id);
//         return false;
//     }

//     if (request.action === "ping") {
//         // Keep-alive – no response needed
//         return false;
//     }   

//     if (request.action === "maskText") {
//         const { text, url } = request;

//         // Basic guard: reject obviously bad payloads before hitting the network
//         if (typeof text !== 'string' || !text.trim()) {
//             sendResponse({ success: false, error: "Empty or invalid text payload" });
//             return false;
//         }
//         // if (typeof url !== 'string' || !url.startsWith('https://')) {
//         //     sendResponse({ success: false, error: "Invalid or non-HTTPS backend URL" });
//         //     return false;
//         // }
//         const isValidUrl = typeof url === 'string' && url.startsWith('https://');
//         if (!isValidUrl) {
//         sendResponse({ success: false, error: "Invalid or non-HTTPS backend URL" });
//         return false;
// }

//         console.log("Background: relaying text to backend (first 100 chars):",
//             text.substring(0, 100) + (text.length > 100 ? "…" : ""));

//         fetch(url, {
//             method:  'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body:    JSON.stringify({ text }),
//         })
//         .then(async (response) => {
//             if (!response.ok) {
//                 const errorBody = await response.text().catch(() => '');
//                 throw new Error(`HTTP ${response.status}: ${errorBody}`);
//             }
//             return response.json();
//         })
//         .then((data) => {
//             sendResponse({ success: true, data });
//         })
//         .catch((error) => {
//             console.error("Background fetch error:", error.message);
//             sendResponse({ success: false, error: error.message });
//         });

//         // Must return true to keep the message channel open for the async sendResponse
//         return true;
//     }

//     // Unknown action — don't leave the channel hanging
//     console.warn("Background: unknown action:", request.action);
//     sendResponse({ success: false, error: `Unknown action: ${request.action}` });
//     return false;
// });


// day 27 update 
// day 23 claude 
const browserAPI = (() => {
    if (typeof globalThis.chrome !== 'undefined' && globalThis.chrome.runtime) return globalThis.chrome;
    if (typeof globalThis.browser !== 'undefined' && globalThis.browser.runtime) return globalThis.browser;
    return null;
})();

console.log("🔧 PreSendAI background worker started");

// ==================== KEEP-ALIVE PORTS ====================
const ports = new Set();

browserAPI.runtime.onConnect.addListener((port) => {
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
browserAPI.alarms.create('keepAlive', { periodInMinutes: 1 });
browserAPI.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'keepAlive') {
        console.log("⏰ keepAlive alarm fired");
    }
});

// ==================== MESSAGE HANDLER ====================
browserAPI.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Validate sender — only accept messages from our own extension tabs/frames
    if (sender.extensionId && sender.extensionId !== browserAPI.runtime.id) {
        console.warn("⚠️ Message from unexpected sender:", sender.extensionId);
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