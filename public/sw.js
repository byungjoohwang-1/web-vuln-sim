/* WEB-VULN-SIM service worker — offline + install support
 *
 * Strategy:
 *   - Navigations (HTML): network-first, fall back to cache, then offline page.
 *     (HTML changes on every deploy, so freshness wins; cache is the safety net.)
 *   - Static assets (js/css/img/fonts/svg): stale-while-revalidate (instant load,
 *     refresh in background).
 *   - Firebase / Google auth + Firestore + analytics: NEVER intercepted, so cloud
 *     sync, login and leaderboard keep working exactly as before.
 *   - POST / non-GET: never intercepted.
 */
var VERSION = 'wvs-v1';
var STATIC_CACHE = 'wvs-static-' + VERSION;
var PAGE_CACHE = 'wvs-pages-' + VERSION;

// Minimal app shell precached on install (kept small; the rest fills via runtime).
var PRECACHE = [
  '/index.html',
  '/vuln-hub.html',
  '/manifest.json',
  '/favicon.svg',
  '/offline.html'
];

// Hosts we must never touch — let the network handle them untouched.
var BYPASS_HOST = /(^|\.)(googleapis\.com|gstatic\.com|firebaseio\.com|firebaseapp\.com|identitytoolkit|google\.com|googletagmanager\.com|google-analytics\.com|fireb-settings|firestore\.googleapis\.com)/i;

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(STATIC_CACHE).then(function (c) {
      // Best-effort: don't fail install if one asset is missing.
      return Promise.allSettled(PRECACHE.map(function (u) { return c.add(u); }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== STATIC_CACHE && k !== PAGE_CACHE) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

function isStaticAsset(url) {
  return /\.(?:js|css|svg|png|jpg|jpeg|gif|webp|ico|woff2?|ttf|eot|otf)$/i.test(url.pathname);
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url;
  try { url = new URL(req.url); } catch (_) { return; }

  // Only handle same-origin; skip auth/Firebase/analytics hosts entirely.
  if (url.origin !== self.location.origin) return;
  if (BYPASS_HOST.test(url.hostname)) return;

  // Navigations / HTML documents → network-first.
  var isNav = req.mode === 'navigate' ||
    (req.headers.get('accept') || '').indexOf('text/html') !== -1;

  if (isNav) {
    e.respondWith(
      fetch(req).then(function (res) {
        var copy = res.clone();
        caches.open(PAGE_CACHE).then(function (c) { c.put(req, copy); });
        return res;
      }).catch(function () {
        return caches.match(req).then(function (hit) {
          return hit || caches.match('/offline.html');
        });
      })
    );
    return;
  }

  // Static assets → stale-while-revalidate.
  if (isStaticAsset(url)) {
    e.respondWith(
      caches.match(req).then(function (hit) {
        var net = fetch(req).then(function (res) {
          if (res && res.status === 200) {
            var copy = res.clone();
            caches.open(STATIC_CACHE).then(function (c) { c.put(req, copy); });
          }
          return res;
        }).catch(function () { return hit; });
        return hit || net;
      })
    );
  }
});

// Allow the page to trigger an immediate activation after an update.
self.addEventListener('message', function (e) {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
});
