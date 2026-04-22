/* Fire Compliance OS — minimal service worker.
   Strategy:
   - Cache-first for static shell (HTML + JS + CSS + icon/fonts).
   - Network-first for /api/* requests (never cache API). Falls back to cached offline page if app is cold-offline.
   - Versioned cache; stale caches purged on activate.
*/
const CACHE = "fos-shell-v2";
const SHELL = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Never cache API / auth / cross-origin
  if (url.pathname.startsWith("/api/") || req.method !== "GET") {
    return;
  }

  // App shell: network-first, fall back to cache, then to offline root
  event.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        if (res.status === 200 && url.origin === self.location.origin) {
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        }
        return res;
      })
      .catch(() =>
        caches.match(req).then((r) => r || caches.match("/index.html"))
      )
  );
});
