/* WEB-VULN-SIM PWA bootstrap — registers the service worker, offers an
 * unobtrusive "install app" button, and prompts to refresh when an update
 * is ready. Self-contained; safe to load on every page. */
(function () {
  if (!('serviceWorker' in navigator)) return;

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  // ---- register ----
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').then(function (reg) {
      // Detect a waiting/updated worker and offer refresh.
      reg.addEventListener('updatefound', function () {
        var nw = reg.installing;
        if (!nw) return;
        nw.addEventListener('statechange', function () {
          if (nw.state === 'installed' && navigator.serviceWorker.controller) {
            showUpdate(reg);
          }
        });
      });
    }).catch(function () { /* offline-first is best-effort */ });
  });

  var reloaded = false;
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    if (reloaded) return; reloaded = true; location.reload();
  });

  // ---- install button ----
  var deferred = null;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferred = e;
    if (sessionStorage.getItem('wvs_install_dismissed')) return;
    showInstall();
  });
  window.addEventListener('appinstalled', function () { removeEl('wvs-install'); });

  function showInstall() {
    if (document.getElementById('wvs-install')) return;
    var b = document.createElement('div');
    b.id = 'wvs-install';
    b.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:9999;background:#0e1f17;border:1px solid #14532d;color:#bbf7d0;border-radius:12px;padding:11px 14px;font-family:Segoe UI,Malgun Gothic,sans-serif;font-size:13px;box-shadow:0 8px 24px rgba(0,0,0,.4);display:flex;gap:10px;align-items:center;max-width:280px';
    b.innerHTML = '<span style="font-size:20px">📲</span><span style="flex:1">' +
      L('이 포털을 앱으로 설치할 수 있어요.', 'Install this portal as an app.') + '</span>' +
      '<button id="wvs-install-yes" style="background:#22c55e;border:0;color:#04240f;font-weight:700;border-radius:8px;padding:6px 12px;cursor:pointer">' + L('설치', 'Install') + '</button>' +
      '<button id="wvs-install-no" style="background:transparent;border:0;color:#94a3b8;cursor:pointer;font-size:16px">✕</button>';
    document.body.appendChild(b);
    document.getElementById('wvs-install-yes').onclick = function () {
      if (!deferred) { removeEl('wvs-install'); return; }
      deferred.prompt();
      deferred.userChoice.finally(function () { deferred = null; removeEl('wvs-install'); });
    };
    document.getElementById('wvs-install-no').onclick = function () {
      try { sessionStorage.setItem('wvs_install_dismissed', '1'); } catch (e) {}
      removeEl('wvs-install');
    };
  }

  // ---- update toast ----
  function showUpdate(reg) {
    if (document.getElementById('wvs-update')) return;
    var b = document.createElement('div');
    b.id = 'wvs-update';
    b.style.cssText = 'position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:9999;background:#0a101e;border:1px solid #1e3a5f;color:#e2e8f0;border-radius:12px;padding:11px 14px;font-family:Segoe UI,Malgun Gothic,sans-serif;font-size:13px;box-shadow:0 8px 24px rgba(0,0,0,.4);display:flex;gap:10px;align-items:center';
    b.innerHTML = '<span>🔄 ' + L('새 버전이 준비됐어요.', 'A new version is ready.') + '</span>' +
      '<button id="wvs-update-yes" style="background:#0ea5e9;border:0;color:#04240f;font-weight:700;border-radius:8px;padding:6px 12px;cursor:pointer">' + L('새로고침', 'Refresh') + '</button>' +
      '<button id="wvs-update-no" style="background:transparent;border:0;color:#94a3b8;cursor:pointer;font-size:16px">✕</button>';
    document.body.appendChild(b);
    document.getElementById('wvs-update-yes').onclick = function () {
      if (reg.waiting) reg.waiting.postMessage('SKIP_WAITING'); else location.reload();
    };
    document.getElementById('wvs-update-no').onclick = function () { removeEl('wvs-update'); };
  }

  function removeEl(id) { var el = document.getElementById(id); if (el) el.remove(); }
})();
