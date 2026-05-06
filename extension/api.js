// // api.js – backend communication
// //
// // BROWSER COMPATIBILITY
// // ─────────────────────
// // Chrome / Edge / Opera / Brave → browserAPI = chrome  (resolved in content.js)
// // Firefox                       → browserAPI = browser (resolved in content.js)
// //

// // Brave-specific note:
// //   Brave Shields can block page-context fetch() to localhost.
// //   PATH 1 (background relay) runs in the extension service-worker and is
// //   NOT subject to Shields — masking works on Brave via that path.
// //   PATH 2 (direct fetch) is a last-resort fallback and may be blocked by
// //   Shields; a clear console warning is shown if that happens.
// //
// // All globals (HEALTH_URL, BACKEND_URL, HEALTH_CHECK_INTERVAL,
// // HEALTH_CHECK_TIMEOUT, MESSAGE_TIMEOUT, runtime, extensionEnabled)
// // are declared in content.js which loads BEFORE this file.
// // Do NOT re-declare any of them here.

// // ==================== HEALTH STATE ====================
// // null = unknown, true = healthy, false = unreachable
// let backendHealthy  = null;
// let lastHealthCheck = 0;

// // ==================== HEALTH CHECK ====================
// async function checkBackendHealth(force = false) {
//     if (typeof extensionEnabled !== 'undefined' && !extensionEnabled) return backendHealthy;

//     const now = Date.now();
//     if (!force && now - lastHealthCheck < HEALTH_CHECK_INTERVAL) return backendHealthy;

//     lastHealthCheck = now;
//     try {
//         const controller = new AbortController();
//         const tid = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
//         // Runs in PAGE context — may be blocked by Brave Shields.
//         // Non-fatal: PATH 1 in sendToBackend() bypasses Shields anyway.
//         const res = await fetch(HEALTH_URL, { method: 'GET', signal: controller.signal });
//         clearTimeout(tid);
//         backendHealthy = res.ok;
//         if (!res.ok) console.warn("⚠️ Backend health check non-OK:", res.status);
//     } catch (e) {
//         backendHealthy = false;
//         console.warn(
//             "⚠️ Health check fetch failed.",
//             "On Brave this may be Shields blocking page-context requests — masking still works via the background relay.",
//             e.message
//         );
//     }
//     console.log(`Backend: ${backendHealthy ? '🟢 healthy' : '🔴 unreachable'}`);
//     return backendHealthy;
// }


// // ==================== SEND TO BACKEND ====================
// async function sendToBackend(text) {
//     // Re-check if last known state is unhealthy
//     if (backendHealthy === false) {
//         const healthy = await checkBackendHealth(true);
//         if (!healthy) {
//             console.log("⏸️ Backend unhealthy, skipping send.");
//             return { success: false, error: "Backend unreachable" };
//         }
//     }

//     // ── PATH 1: background.js relay (preferred for ALL browsers) ─────────────
//     // Runs in the extension service-worker context.
//     // • Bypasses Brave Shields                  ✅
//     // • No CORS issues                          ✅
//     // • Works on Chrome, Edge, Firefox, Brave   ✅
//     // • Uses runtime.lastError (not chrome.*)   ✅  Firefox safe
//     if (runtime) {
//         try {
//             if (!runtime.id) throw new Error("Extension context invalidated");

//             const result = await Promise.race([
//                 new Promise((resolve, reject) => {
//                     runtime.sendMessage(
//                         { action: "maskText", text, url: BACKEND_URL },
//                         (response) => {
//                             const err = runtime.lastError;
//                             if (err) {
//                                 reject(new Error(err.message));
//                             } else if (!response) {
//                                 reject(new Error("Empty response from background"));
//                             } else {
//                                 resolve(response);
//                             }
//                         }
//                     );
//                 }),
//                 new Promise((_, reject) =>
//                     setTimeout(() => reject(new Error("Runtime message timeout")), MESSAGE_TIMEOUT)
//                 )
//             ]);

//             if (!result.success) {
//                 return { success: false, error: result.error || "Background reported failure" };
//             }
//             if (result.data == null) {
//                 return { success: false, error: "Background returned no data" };
//             }
//             return { success: true, data: result.data };

//         } catch (e) {
//             console.warn("⚠️ Background relay failed, trying direct fetch:", e.message);
//         }
//     }

//     // ── PATH 2: direct fetch fallback ────────────────────────────────────────
//     // Runs in PAGE context — subject to Brave Shields on some settings.
//     // Reaching here means the background relay was unavailable (e.g. service
//     // worker not yet started). If this also fails on Brave, both paths are
//     // broken which indicates a genuine connectivity or install problem.
//     try {
//         const controller = new AbortController();
//         const tid = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
//         const res = await fetch(BACKEND_URL, {
//             method:  'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body:    JSON.stringify({ text }),
//             signal:  controller.signal,
//         });
//         clearTimeout(tid);

//         if (!res.ok) {
//             const errBody = await res.text().catch(() => '');
//             throw new Error(`HTTP ${res.status}: ${errBody}`);
//         }

//         const data = await res.json();
//         backendHealthy = true;
//         return { success: true, data };

//     } catch (e) {
//         backendHealthy = false;
//         lastHealthCheck = Date.now();
//         console.error(
//             "❌ Direct fetch also failed.",
//             "If you are on Brave: check that Shields are not blocking localhost,",
//             "or reinstall the extension so the background relay is available.",
//             "Error:", e.message
//         );
//         return { success: false, error: e.message };
//     }
// }


// api.js – backend communication
//
// BROWSER COMPATIBILITY
// ─────────────────────
// Chrome / Edge / Opera / Brave → browserAPI = chrome  (resolved in content.js)
// Firefox                       → browserAPI = browser (resolved in content.js)
//

// Brave-specific note:
//   Brave Shields can block page-context fetch() to localhost.
//   PATH 1 (background relay) runs in the extension service-worker and is
//   NOT subject to Shields — masking works on Brave via that path.
//   PATH 2 (direct fetch) is a last-resort fallback and may be blocked by
//   Shields; a clear console warning is shown if that happens.
//
// All globals (HEALTH_URL, BACKEND_URL, HEALTH_CHECK_INTERVAL,
// HEALTH_CHECK_TIMEOUT, MESSAGE_TIMEOUT, runtime, extensionEnabled)
// are declared in content.js which loads BEFORE this file.
// Do NOT re-declare any of them here.

// ==================== HEALTH STATE ====================
// null = unknown, true = healthy, false = unreachable
let backendHealthy  = null;
let lastHealthCheck = 0;

// ==================== HEALTH CHECK ====================
async function checkBackendHealth(force = false) {
    if (typeof extensionEnabled !== 'undefined' && !extensionEnabled) return backendHealthy;

    const now = Date.now();
    if (!force && now - lastHealthCheck < HEALTH_CHECK_INTERVAL) return backendHealthy;

    lastHealthCheck = now;
    try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT);
        // Runs in PAGE context — may be blocked by Brave Shields.
        // Non-fatal: PATH 1 in sendToBackend() bypasses Shields anyway.
        const res = await fetch(HEALTH_URL, { method: 'GET', signal: controller.signal });
        clearTimeout(tid);
        backendHealthy = res.ok;
        if (!res.ok) console.warn("⚠️ Backend health check non-OK:", res.status);
    } catch (e) {
        backendHealthy = false;
        console.warn(
            "⚠️ Health check fetch failed.",
            "On Brave this may be Shields blocking page-context requests — masking still works via the background relay.",
            e.message
        );
    }
    console.log(`Backend: ${backendHealthy ? '🟢 healthy' : '🔴 unreachable'}`);
    return backendHealthy;
}


// ==================== SEND TO BACKEND ====================
async function sendToBackend(text) {
    // Re-check if last known state is unhealthy
    if (backendHealthy === false) {
        const healthy = await checkBackendHealth(true);
        if (!healthy) {
            console.log("⏸️ Backend unhealthy, skipping send.");
            return { success: false, error: "Backend unreachable" };
        }
    }

    // Capture the current website hostname for per‑site stats
    const source = window.location.hostname;

    // ── PATH 1: background.js relay (preferred for ALL browsers) ─────────────
    if (runtime) {
        try {
            if (!runtime.id) throw new Error("Extension context invalidated");

            const result = await Promise.race([
                new Promise((resolve, reject) => {
                    runtime.sendMessage(
                        { action: "maskText", text, url: BACKEND_URL, source },
                        (response) => {
                            const err = runtime.lastError;
                            if (err) {
                                reject(new Error(err.message));
                            } else if (!response) {
                                reject(new Error("Empty response from background"));
                            } else {
                                resolve(response);
                            }
                        }
                    );
                }),
                new Promise((_, reject) =>
                    setTimeout(() => reject(new Error("Runtime message timeout")), MESSAGE_TIMEOUT)
                )
            ]);

            if (!result.success) {
                return { success: false, error: result.error || "Background reported failure" };
            }
            if (result.data == null) {
                return { success: false, error: "Background returned no data" };
            }
            return { success: true, data: result.data };

        } catch (e) {
            console.warn("⚠️ Background relay failed, trying direct fetch:", e.message);
        }
    }

    // ── PATH 2: direct fetch fallback ────────────────────────────────────────
    try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), MESSAGE_TIMEOUT);
        const res = await fetch(BACKEND_URL, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ text, source }),   // ← source added
            signal:  controller.signal,
        });
        clearTimeout(tid);

        if (!res.ok) {
            const errBody = await res.text().catch(() => '');
            throw new Error(`HTTP ${res.status}: ${errBody}`);
        }

        const data = await res.json();
        backendHealthy = true;
        return { success: true, data };

    } catch (e) {
        backendHealthy = false;
        lastHealthCheck = Date.now();
        console.error(
            "❌ Direct fetch also failed.",
            "If you are on Brave: check that Shields are not blocking localhost,",
            "or reinstall the extension so the background relay is available.",
            "Error:", e.message
        );
        return { success: false, error: e.message };
    }
}