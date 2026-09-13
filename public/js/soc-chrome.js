/**
 * WVS SOC-Chrome — 사이트 전역 플랫폼 크롬 (통일 탑바 + Ctrl+K 커맨드 팔레트)
 *
 * 역할:
 *  1) 어떤 페이지에 있든 동일한 다크 SOC 탑바(홈·훈련·출제·카탈로그·내 기록)를 제공
 *  2) Ctrl+K / Cmd+K 로 전체 사이트(400+ 페이지) 검색 팔레트를 띄운다
 *
 * 사용:
 *  <script src="/js/soc-chrome.js" defer></script>                    ← 탑바 + 팔레트
 *  <script src="/js/soc-chrome.js" data-topbar="off" defer></script>  ← 팔레트만 (자체 헤더를 쓰는 대표 페이지)
 *
 * 검색 인덱스: /data/search-index.json (gen_search_index.py가 생성)
 * 방어적으로 작성: 인덱스 로드 실패 시 탑바만 동작, 콘솔 에러 없음.
 */
(function () {
  'use strict';

  var scriptEl = (function () {
    var all = document.getElementsByTagName('script');
    for (var i = all.length - 1; i >= 0; i--) {
      if (/soc-chrome\.js/.test(all[i].src || '')) return all[i];
    }
    return null;
  })();
  var TOPBAR_OFF = scriptEl && scriptEl.getAttribute('data-topbar') === 'off';

  var INDEX_URL = '/data/search-index.json';

  /* ── 언어 ──
     공용 크롬은 모든 페이지에 뜨므로, 본문이 한국어만 있는 페이지에서도
     내비게이션만큼은 영어로 동작해야 한다. bilingual.js 와 같은 저장키를 쓴다. */
  function lang() {
    try {
      var v = localStorage.getItem('wvs_lang') || localStorage.getItem('lang');
      return v === 'en' ? 'en' : 'ko';
    } catch (e) { return 'ko'; }
  }
  var T = {
    ko: {
      search: '검색', searchAria: '사이트 검색',
      placeholder: '페이지·시나리오·도구 검색 (예: SQL, U-01, 레드팀)',
      move: '이동', open: '열기', close: '닫기',
      quick: '빠른 실행', noResult: '검색 결과가 없습니다',
      loadFail: '검색 인덱스를 불러올 수 없습니다.', loadFail2: '검색 인덱스 로드 실패',
      loading: '검색 인덱스를 불러오는 중…', retry: '다시 시도'
    },
    en: {
      search: 'Search', searchAria: 'Site search',
      placeholder: 'Search pages, scenarios, tools (e.g. SQL, U-01, red team)',
      move: 'Move', open: 'Open', close: 'Close',
      quick: 'Quick actions', noResult: 'No results',
      loadFail: 'Could not load the search index.', loadFail2: 'Search index failed to load',
      loading: 'Loading search index…', retry: 'Retry'
    }
  };
  function t(k) { return (T[lang()] || T.ko)[k]; }

  var NAV = [
    { t: '홈', en: 'Home', u: '/vuln-hub.html' },
    { t: '레드팀 아레나', en: 'Red Team Arena', u: '/redteam.html' },
    { t: '취약점 실습장', en: 'Vuln Lab', u: '/vulnlab.html' },
    { t: 'AI 문제 포지', en: 'AI Quiz Forge', u: '/quiz-forge.html' },
    { t: '카탈로그', en: 'Catalog', u: '/vuln-hub.html#catalog' },
    { t: '내 기록', en: 'My Progress', u: '/my-progress.html' }
  ];

  var GROUP_STYLE = {
    code: ['#38bdf8', 'CODE'], design: ['#38bdf8', 'CODE'], sim: ['#f87171', 'SIM'],
    guide: ['#94a3b8', 'GUIDE'], unix: ['#4ade80', 'UNIX'], db: ['#fbbf24', 'DB'],
    fin: ['#fbbf24', 'FIN'], win: ['#60a5fa', 'WIN'], net: ['#a78bfa', 'NET'],
    sec: ['#f472b6', 'SEC'], cloud: ['#7dd3fc', 'CLD'], ics: ['#fb923c', 'ICS'],
    ai: ['#c4b5fd', 'AI'], auto: ['#fb7185', 'AUTO'], tools: ['#e2e8f0', 'TOOL'],
    hub: ['#e2e8f0', 'MAIN']
  };

  /* ── 공통 CSS (wvsx- 접두사로 스코프 격리) ── */
  var CSS = [
    '.wvsx-top{position:sticky;top:0;z-index:var(--wvs-z-sticky,100);display:flex;align-items:center;gap:18px;',
    'height:42px;padding:0 18px;background:#080e1a;border-bottom:1px solid #1e293b;',
    "font-family:'Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif;direction:ltr}",
    '.wvsx-top .wvsx-logo{display:flex;align-items:center;gap:8px;color:#e2e8f0;',
    'text-decoration:none;font-weight:800;font-size:.86rem;letter-spacing:.3px;white-space:nowrap}',
    '.wvsx-top .wvsx-logo .mk{color:#38bdf8;font-size:1rem}',
    '.wvsx-top .wvsx-nav{display:flex;gap:2px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none}',
    '.wvsx-top .wvsx-nav::-webkit-scrollbar{display:none}',
    '.wvsx-top .wvsx-nav a{color:#8fa0ba;text-decoration:none;font-size:.78rem;font-weight:600;',
    'padding:5px 11px;border-radius:8px;white-space:nowrap}',
    '.wvsx-top .wvsx-nav a:hover{color:#e2e8f0;background:rgba(56,189,248,.08)}',
    '.wvsx-top .wvsx-nav a.on{color:#7dd3fc;background:rgba(56,189,248,.12)}',
    '.wvsx-top .wvsx-kbtn{display:flex;align-items:center;gap:8px;background:#0e1626;border:1px solid #26334d;',
    'color:#8fa0ba;border-radius:8px;padding:5px 12px;font-size:.75rem;cursor:pointer;white-space:nowrap;',
    "font-family:inherit}",
    '.wvsx-top .wvsx-kbtn:hover{border-color:#38bdf8;color:#7dd3fc}',
    '.wvsx-top .wvsx-kbtn .kb{font-size:.65rem;border:1px solid #334155;border-radius:5px;padding:1px 6px;color:#64748b}',
    '@media(max-width:640px){.wvsx-top{gap:10px;padding:0 12px}.wvsx-top .wvsx-kbtn .kb{display:none}',
    '.wvsx-top .wvsx-nav a{padding:5px 8px}}',
    /* 팔레트 */
    '.wvsx-pal{position:fixed;inset:0;z-index:var(--wvs-z-modal,900);display:none;align-items:flex-start;',
    'justify-content:center;padding:12vh 16px 16px;background:rgba(4,8,16,.72);',
    "backdrop-filter:blur(4px);font-family:'Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif}",
    '.wvsx-pal.show{display:flex}',
    '.wvsx-pal .box{width:100%;max-width:640px;background:#0e1626;border:1px solid #26334d;',
    'border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.6);overflow:hidden}',
    '.wvsx-pal .inp{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #1e293b}',
    '.wvsx-pal .inp .ic{color:#38bdf8;font-weight:800}',
    '.wvsx-pal .inp input{flex:1;min-width:0;background:transparent;border:0;outline:0;color:#e2e8f0;',
    "font-size:1rem;font-family:inherit}",
    '.wvsx-pal .inp input::placeholder{color:#475569}',
    '.wvsx-pal .inp .esc{font-size:.65rem;border:1px solid #334155;border-radius:5px;padding:2px 7px;color:#64748b}',
    '.wvsx-pal .list{max-height:52vh;overflow-y:auto;padding:8px}',
    '.wvsx-pal .row{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:9px;',
    'cursor:pointer;color:#dbe4f0;font-size:.86rem}',
    '.wvsx-pal .row .g{font-size:.6rem;font-weight:800;letter-spacing:.5px;border-radius:5px;',
    'padding:2px 7px;border:1px solid;flex-shrink:0;min-width:44px;text-align:center}',
    '.wvsx-pal .row .tt{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.wvsx-pal .row .uu{font-size:.66rem;color:#475569;white-space:nowrap}',
    '.wvsx-pal .row.sel{background:rgba(56,189,248,.12)}',
    '.wvsx-pal .row.sel .tt{color:#7dd3fc}',
    '.wvsx-pal .empty{padding:28px;text-align:center;color:#64748b;font-size:.82rem}',
    '.wvsx-pal .hd{padding:6px 12px 4px;color:#64748b;font-size:.66rem;font-weight:700;letter-spacing:.4px}',
    '.wvsx-pal .row{text-decoration:none}',
    '.wvsx-pal .row:focus-visible{outline:2px solid #38bdf8;outline-offset:-2px}',
    '.wvsx-retry{background:#1e293b;border:1px solid #334155;color:#cbd5e1;border-radius:8px;',
    'padding:6px 14px;cursor:pointer;font:inherit;font-size:.78rem}',
    '.wvsx-retry:hover{border-color:#38bdf8;color:#7dd3fc}',
    '.wvsx-pal .ft{display:flex;gap:14px;padding:9px 16px;border-top:1px solid #1e293b;',
    'color:#475569;font-size:.66rem}',
    '.wvsx-pal .ft b{color:#64748b;font-weight:600}'
  ].join('');

  function injectCss() {
    /* [G05] 공통 토큰(레이어·간격·포커스 링)은 별도 파일 한 곳에서 관리한다.
       모듈마다 z-index 를 키우다 진도 칩이 검색 모달 위로 올라가는 일이 있었다. */
    if (!document.getElementById('wvs-tokens')) {
      var lk = document.createElement('link');
      lk.id = 'wvs-tokens';
      lk.rel = 'stylesheet';
      lk.href = '/css/platform-tokens.css';
      document.head.appendChild(lk);
    }
    var st = document.createElement('style');
    st.id = 'wvsx-style';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  /* ── 탑바 ── */
  function currentPath() {
    try { return decodeURIComponent(location.pathname || ''); } catch (e) { return location.pathname || ''; }
  }
  function isCurrent(u) {
    var p = currentPath();
    var f = (u.split('/').pop() || '').split('#')[0];
    if (!f) return false;
    return p === '/' + f || p.slice(-1 - f.length) === '/' + f;
  }
  function buildTopbar() {
    if (TOPBAR_OFF) return;
    var bar = document.createElement('div');
    bar.className = 'wvsx-top';
    bar.id = 'wvsx-topbar';
    var html = '<a class="wvsx-logo" href="/vuln-hub.html"><span class="mk">⛨</span>WEB-VULN-SIM</a>';
    html += '<nav class="wvsx-nav">';
    var en = lang() === 'en';
    for (var i = 0; i < NAV.length; i++) {
      var n = NAV[i];
      html += '<a href="' + n.u + '"' + (isCurrent(n.u) ? ' class="on"' : '') + '>' + (en ? n.en : n.t) + '</a>';
    }
    html += '</nav>';
    html += '<button type="button" class="wvsx-kbtn" id="wvsx-kbtn">🔍 ' + t('search') + ' <span class="kb">Ctrl K</span></button>';
    bar.innerHTML = html;
    if (document.body.firstChild) document.body.insertBefore(bar, document.body.firstChild);
    else document.body.appendChild(bar);
    document.getElementById('wvsx-kbtn').addEventListener('click', function () { openPalette(); });
  }

  /* ── 커맨드 팔레트 ── */
  /* [G03] 예전에는 INDEX_TRIED 를 세우고 실패해도 되돌리지 않아 같은 페이지에서
     영영 재시도할 수 없었다. 상태를 명시적으로 나눠 error 에서 다시 시도할 수 있게 한다. */
  var INDEX = null, INDEX_STATE = 'idle';   // idle | loading | ready | error
  var palEl = null, inpEl = null, listEl = null;
  var results = [], sel = 0;

  function loadIndex(cb) {
    if (INDEX_STATE === 'ready') return cb(true);
    if (INDEX_STATE === 'loading') return;        /* 진행 중이면 기존 완료 콜백이 화면을 갱신한다 */
    INDEX_STATE = 'loading';
    try {
      fetch(INDEX_URL).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        INDEX = (d && d.pages) ? d.pages : null;
        INDEX_STATE = INDEX ? 'ready' : 'error';
        cb(INDEX_STATE === 'ready');
      }).catch(function () { INDEX_STATE = 'error'; cb(false); });
    } catch (e) { INDEX_STATE = 'error'; cb(false); }
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function buildPalette() {
    if (palEl) return;
    palEl = document.createElement('div');
    palEl.className = 'wvsx-pal';
    palEl.id = 'wvsx-palette';
    palEl.innerHTML =
      '<div class="box" role="dialog" aria-modal="true" aria-label="' + t('searchAria') + '">' +
      '<div class="inp"><span class="ic">⌕</span>' +
      '<input id="wvsx-pal-inp" type="text" placeholder="' + t('placeholder') + '" autocomplete="off">' +
      '<span class="esc">ESC</span></div>' +
      '<div class="list" id="wvsx-pal-list" role="listbox" aria-label="' + t('searchAria') + '"></div>' +
      '<div class="ft"><span><b>↑↓</b> ' + t('move') + '</span><span><b>↵</b> ' + t('open') + '</span><span><b>ESC</b> ' + t('close') + '</span></div>' +
      '</div>';
    document.body.appendChild(palEl);
    inpEl = palEl.querySelector('#wvsx-pal-inp');
    listEl = palEl.querySelector('#wvsx-pal-list');
    /* 인덱스가 아직 안 왔어도 입력은 받는다. 도착하면 refresh 가 현재 값으로 검색한다. */
    inpEl.addEventListener('input', function () {
      if (INDEX_STATE === 'ready') runSearch(inpEl.value); else refresh();
    });
    inpEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') { e.preventDefault(); go(sel); }
      else if (e.key === 'Escape') { closePalette(); }
    });
    palEl.addEventListener('click', function (e) {
      if (e.target === palEl) { closePalette(); return; }
      var row = e.target.closest ? e.target.closest('.wvsx-pal .row') : null;
      if (!row || row.getAttribute('data-i') == null) return;
      /* 새 탭/새 창 열기는 브라우저 기본 동작에 맡긴다(결과가 진짜 링크이므로) */
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) { closePalette(); return; }
      e.preventDefault();
      go(+row.getAttribute('data-i'));
    });
    /* [G03] 모달 안에 포커스를 가둔다 — Tab 이 뒤 페이지로 새어 나가면 스크린리더가 길을 잃는다. */
    palEl.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = palEl.querySelectorAll('input, button, a[href], [tabindex]:not([tabindex="-1"])');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  function norm(s) { return String(s || '').toLowerCase().replace(/\s+/g, ' ').trim(); }

  function score(page, q) {
    if (!q) return 0;
    var t = norm(page.t), u = norm(page.u), k = norm(page.k);
    if (t === q || u === q) return 1000;
    if (t.indexOf(q) === 0) return 500;
    if (t.indexOf(q) >= 0) return 300 - t.indexOf(q);
    if (u.indexOf(q) >= 0) return 250;
    if (k && k.indexOf(q) >= 0) return 150;
    // 단어 단위 부분 일치
    var words = q.split(' '), hit = 0;
    for (var i = 0; i < words.length; i++) {
      if (words[i] && (t.indexOf(words[i]) >= 0 || (k && k.indexOf(words[i]) >= 0))) hit++;
    }
    return hit === words.length ? 100 : 0;
  }

  function runSearch(q) {
    if (!INDEX) { render({ emptyMsg: t('loadFail'), retry: t('retry') }); return; }
    var nq = norm(q);
    if (!nq) {
      // 기본: 대표 페이지 추천
      var quick = ['vuln-hub.html', 'redteam.html', 'vulnlab.html', 'quiz-forge.html', 'my-progress.html', 'labs-live.html', 'ai-tutor.html'];
      results = INDEX.filter(function (p) { return quick.indexOf(p.u) >= 0; });
      sel = 0; render({ heading: t('quick') }); return;
    }
    var scored = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], nq);
      if (s > 0) scored.push({ p: INDEX[i], s: s });
    }
    scored.sort(function (a, b) { return b.s - a.s; });
    results = scored.slice(0, 30).map(function (x) { return x.p; });
    sel = 0;
    render(results.length ? {} : { emptyMsg: t('noResult') });
  }

  /**
   * [G03] 예전 render(msg) 는 메시지가 있으면 결과를 아예 안 그렸다.
   * 그래서 팔레트를 처음 열 때 render('빠른 실행') 이 호출되며 추천 항목이 계산돼도
   * 화면에는 문구만 남았다. 제목(heading)과 빈 상태(emptyMsg)를 분리한다.
   * 결과는 실제 <a> 링크로 만들어 새 탭 열기·스크린리더 탐색이 가능하게 한다.
   */
  function render(opts) {
    opts = opts || {};
    var html = '';
    if (opts.heading) html += '<div class="hd">' + esc(opts.heading) + '</div>';
    if (opts.emptyMsg) {
      html += '<div class="empty">' + esc(opts.emptyMsg) + '</div>';
      if (opts.retry) html += '<div class="empty"><button type="button" id="wvsx-pal-retry" class="wvsx-retry">' + esc(opts.retry) + '</button></div>';
    } else {
      for (var i = 0; i < results.length; i++) {
        var p = results[i];
        var gs = GROUP_STYLE[p.g] || GROUP_STYLE.tools;
        var href = p.u.charAt(0) === '/' ? p.u : '/' + p.u;
        html += '<a class="row' + (i === sel ? ' sel' : '') + '" data-i="' + i + '" href="' + esc(href) + '"' +
          ' role="option" aria-selected="' + (i === sel ? 'true' : 'false') + '" tabindex="-1">' +
          '<span class="g" style="color:' + gs[0] + ';border-color:' + gs[0] + '55">' + gs[1] + '</span>' +
          '<span class="tt">' + esc(p.t) + '</span>' +
          '<span class="uu">' + esc(p.u) + '</span></a>';
      }
    }
    listEl.innerHTML = html;
    var rb = listEl.querySelector('#wvsx-pal-retry');
    if (rb) rb.addEventListener('click', function () { INDEX_STATE = 'idle'; refresh(); });
  }

  /** 현재 입력값 기준으로 인덱스를 확보하고 결과를 갱신한다(로딩/실패 상태 표시 포함). */
  function refresh() {
    if (INDEX_STATE === 'ready') { runSearch(inpEl.value); return; }
    if (INDEX_STATE === 'error') { render({ emptyMsg: t('loadFail'), retry: t('retry') }); return; }
    render({ emptyMsg: t('loading') });
    loadIndex(function (ok) {
      if (!palEl || !palEl.classList.contains('show')) return;
      if (ok) runSearch(inpEl.value);                    /* 로딩 중 입력한 검색어를 그대로 쓴다 */
      else render({ emptyMsg: t('loadFail'), retry: t('retry') });
    });
  }

  function move(d) {
    if (!results.length) return;
    sel = (sel + d + results.length) % results.length;
    render({});
    var el = listEl.querySelector('.row.sel');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
  }

  function go(i) {
    if (!results[i]) return;
    var u = results[i].u;
    closePalette();
    location.href = u.charAt(0) === '/' ? u : '/' + u;
  }

  var lastFocus = null;
  function openPalette() {
    buildPalette();
    lastFocus = document.activeElement;
    palEl.classList.add('show');
    document.body.classList.add('wvs-modal-open');
    inpEl.value = '';
    refresh();
    setTimeout(function () { inpEl.focus(); }, 30);
  }
  function closePalette() {
    if (!palEl || !palEl.classList.contains('show')) return;
    palEl.classList.remove('show');
    document.body.classList.remove('wvs-modal-open');
    /* 팔레트를 열기 전 요소로 포커스를 돌려준다(키보드 사용자가 위치를 잃지 않도록) */
    try { if (lastFocus && lastFocus.focus) lastFocus.focus(); } catch (e) {}
    lastFocus = null;
  }

  /* ── 접근성: div 기반 collapse 토글의 키보드 조작 ──
     <div role="button" tabindex="0" data-bs-toggle="collapse"> 는 포커스는 받지만
     Enter/Space 로 click 이 발생하지 않는다(진짜 button/a 만 자동 발생).
     Bootstrap 은 click 위임만 하므로 키 입력을 click 으로 이어준다. */
  function bindCollapseKeys() {
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
      var t = e.target;
      if (!t || !t.closest) return;
      var tog = t.closest('[data-bs-toggle="collapse"]');
      if (!tog || tog !== t) return;                 /* 내부 입력 요소는 건드리지 않는다 */
      if (/^(BUTTON|A|INPUT|SELECT|TEXTAREA)$/.test(tog.tagName)) return;
      e.preventDefault();                            /* Space 로 페이지가 스크롤되지 않게 */
      tog.click();
    });
  }

  /* ── 부트 ── */
  function boot() {
    try { injectCss(); buildTopbar(); } catch (e) { /* 어떤 페이지에서도 크래시 없이 */ }
    try { bindCollapseKeys(); } catch (eK) { /* no-op */ }
    try { /* 자체 헤더(data-topbar=off) 페이지의 검색 버튼도 팔레트에 연결 */
      var pb = document.getElementById('palBtn');
      if (pb) pb.addEventListener('click', function () { openPalette(); });
    } catch (e2) { /* no-op */ }
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        if (palEl && palEl.classList.contains('show')) closePalette(); else openPalette();
      } else if (e.key === 'Escape') {
        closePalette();
      }
    });
    /* 언어를 바꾸면 크롬은 이미 그려진 상태이므로 직접 다시 그린다(bilingual.js 가 알림). */
    document.addEventListener('wvs:lang', function () {
      try {
        var old = document.getElementById('wvsx-topbar');
        if (old) { old.remove(); buildTopbar(); }
        if (palEl) { palEl.remove(); palEl = null; inpEl = null; listEl = null; }
      } catch (e3) { /* no-op */ }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
