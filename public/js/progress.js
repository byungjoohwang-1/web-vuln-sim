/* WEB-VULN-SIM — 통합 진도·마스터리 엔진 (T1 앵커)
 * 사이트 전 학습 페이지(넘버드 + sim-*)에 주입되어 "탐색/완료/점수"를 기록한다.
 * 저장 키는 wvs_ 접두사 → 기존 Google 로그인 클라우드 동기화가 자동 반영.
 * 방어적: 어떤 테마/페이지에서도 콘솔 에러 0, 기존 UI 비간섭.
 * 공개 API: window.WVSProgress { get, summary, isComplete, markVisited, complete, toggle }
 */
(function () {
  'use strict';
  var KEY = 'wvs_progress';
  var XP_PER = 10; // 항목 최초 완료 시 XP

  function nowTs() { return Date.now(); }
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
    catch (e) { return {}; }
  }
  function normalize(o) {
    if (!o || typeof o !== 'object') o = {};
    if (!o.items || typeof o.items !== 'object') o.items = {};
    if (typeof o.xp !== 'number') o.xp = 0;
    if (!Array.isArray(o.days)) o.days = [];
    return o;
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }
  function touchDay(s) {
    var t = today();
    if (s.days[s.days.length - 1] !== t) { s.days.push(t); if (s.days.length > 120) s.days = s.days.slice(-120); }
  }
  // 연속 학습일(오늘 또는 어제부터 역순 연속)
  function calcStreak(days) {
    if (!days || !days.length) return 0;
    var set = {}; days.forEach(function (d) { set[d] = 1; });
    var cur = new Date(); var t = today();
    if (!set[t]) { cur.setDate(cur.getDate() - 1); } // 오늘 활동 없으면 어제부터
    var n = 0;
    for (var i = 0; i < 400; i++) {
      var key = cur.getFullYear() + '-' + ('0' + (cur.getMonth() + 1)).slice(-2) + '-' + ('0' + cur.getDate()).slice(-2);
      if (set[key]) { n++; cur.setDate(cur.getDate() - 1); } else break;
    }
    return n;
  }
  function save(o) {
    try { o.updated = nowTs(); localStorage.setItem(KEY, JSON.stringify(o)); }
    catch (e) { /* quota/private mode — 무시 */ }
  }
  function pageId() {
    var p = (location.pathname || '').split('/').pop();
    return p || 'index.html';
  }
  // 학습 항목(칩 노출 대상) 판별 — 넘버드 콘텐츠 + sim 실습
  var LEARNABLE = /^(03_code|04_design|05_linux|06_db|07_fin|08_win|09_net|10_sec|11_cloud|12_ics|13_ai)/;
  function isLearnable(id) { return LEARNABLE.test(id) || /^sim-/.test(id); }

  var API = {
    get: function () { return normalize(load()); },
    isComplete: function (id) {
      var it = this.get().items[id || pageId()];
      return !!(it && it.c);
    },
    // 마스터리 요약 { visited, completed, xp, level }
    summary: function () {
      var s = this.get(), v = 0, c = 0;
      for (var k in s.items) { if (s.items[k].v) v++; if (s.items[k].c) c++; }
      return { visited: v, completed: c, xp: s.xp, level: Math.floor(Math.sqrt(s.xp / 100)) + 1, streak: calcStreak(s.days) };
    },
    markVisited: function (id) {
      id = id || pageId();
      var s = this.get();
      var newV = !s.items[id] || !s.items[id].v;
      if (!s.items[id]) s.items[id] = {};
      if (newV) s.items[id].v = nowTs();
      var before = s.days.length;
      touchDay(s);
      if (newV || s.days.length !== before) save(s);
      return s.items[id];
    },
    // 완료 처리(선택적 점수 0~100). 최초 1회만 XP 지급.
    complete: function (score, id) {
      id = id || pageId();
      var s = this.get();
      var it = s.items[id] || (s.items[id] = {});
      if (!it.v) it.v = nowTs();
      it.c = nowTs();
      if (typeof score === 'number') it.s = Math.max(0, Math.min(100, Math.round(score)));
      var gained = 0;
      if (!it.x) { it.x = 1; s.xp += XP_PER; gained = XP_PER; } // 최초 완료만 XP
      touchDay(s);
      save(s);
      emit('wvs:progress', { id: id, completed: true, gained: gained, summary: this.summary() });
      return gained;
    },
    // 완료 해제(오클릭 대비). XP는 회수하지 않음(x 플래그 유지 → 재완료 시 중복 지급 방지)
    uncomplete: function (id) {
      id = id || pageId();
      var s = this.get(), it = s.items[id];
      if (it && it.c) { delete it.c; save(s); emit('wvs:progress', { id: id, completed: false, summary: this.summary() }); }
    },
    toggle: function (id) {
      id = id || pageId();
      if (this.isComplete(id)) { this.uncomplete(id); return false; }
      this.complete(undefined, id); return true;
    }
  };
  function emit(name, detail) {
    try { window.dispatchEvent(new CustomEvent(name, { detail: detail })); } catch (e) {}
  }
  window.WVSProgress = API;

  // ── 플로팅 완료 칩 (학습 페이지에만) ─────────────────────────────
  function injectChip() {
    var id = pageId();
    if (!isLearnable(id)) return;                 // 콘텐츠/실습 페이지만
    if (document.getElementById('wvs-progress-chip')) return;
    if (!document.body) return;

    var wrap = document.createElement('div');
    wrap.id = 'wvs-progress-chip';
    wrap.setAttribute('role', 'group');
    wrap.style.cssText = [
      'position:fixed', 'left:14px', 'bottom:14px', 'z-index:2147483000',
      'font-family:system-ui,-apple-system,"Segoe UI","Malgun Gothic",sans-serif',
      'display:flex', 'align-items:center', 'gap:8px'
    ].join(';');

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'wvs-progress-btn';
    btn.style.cssText = [
      'cursor:pointer', 'border:1px solid rgba(148,163,184,.5)',
      'background:rgba(15,23,42,.92)', 'color:#e2e8f0', 'border-radius:999px',
      'padding:9px 15px', 'font-size:13px', 'font-weight:700', 'line-height:1',
      'box-shadow:0 6px 20px rgba(0,0,0,.35)', 'backdrop-filter:blur(6px)',
      'display:inline-flex', 'align-items:center', 'gap:8px', 'transition:transform .12s ease'
    ].join(';');
    btn.addEventListener('mouseenter', function () { btn.style.transform = 'translateY(-2px)'; });
    btn.addEventListener('mouseleave', function () { btn.style.transform = 'none'; });

    function render() {
      var done = API.isComplete(id);
      btn.innerHTML = done
        ? '<span style="color:#22c55e;font-size:15px">✓</span><span data-en="Completed">완료됨</span>'
        : '<span style="width:13px;height:13px;border:2px solid #94a3b8;border-radius:50%;display:inline-block"></span><span data-en="Mark complete">이 항목 완료</span>';
      btn.setAttribute('aria-pressed', done ? 'true' : 'false');
      btn.title = done ? '완료 해제하려면 클릭' : '학습을 완료로 표시';
      // 언어 토글이 있는 페이지면 즉시 반영
      try {
        if (typeof window.isEn === 'function' && window.isEn()) {
          btn.querySelectorAll('[data-en]').forEach(function (el) { el.textContent = el.getAttribute('data-en'); });
        }
      } catch (e) {}
    }
    btn.addEventListener('click', function () {
      var nowDone = API.toggle(id);
      render();
      if (nowDone) flashXp();
    });

    wrap.appendChild(btn);
    document.body.appendChild(wrap);
    render();

    function flashXp() {
      var f = document.createElement('div');
      f.textContent = '+' + XP_PER + ' XP';
      f.style.cssText = 'color:#fbbf24;font-weight:800;font-size:13px;font-family:inherit;pointer-events:none;opacity:1;transition:transform .9s ease,opacity .9s ease';
      wrap.appendChild(f);
      requestAnimationFrame(function () { f.style.transform = 'translateY(-16px)'; f.style.opacity = '0'; });
      setTimeout(function () { if (f.parentNode) f.parentNode.removeChild(f); }, 950);
    }
  }

  // 탐색 기록: 이탈 방지 위해 4초 체류 후 visited 표시
  function boot() {
    var id = pageId();
    if (isLearnable(id)) {
      setTimeout(function () { try { API.markVisited(id); } catch (e) {} }, 4000);
    }
    injectChip();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
