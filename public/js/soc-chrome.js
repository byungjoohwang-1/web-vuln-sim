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
    { t: '홈', en: 'Home', u: '/index.html' },
    { t: '카탈로그', en: 'Catalog', u: '/vuln-hub.html' },
    { t: '취약점 실습장', en: 'Vuln Lab', u: '/vulnlab.html' },
    { t: '레드팀 아레나', en: 'Red Team Arena', u: '/redteam.html' },
    { t: 'AI 문제 포지', en: 'AI Quiz Forge', u: '/quiz-forge.html' },
    { t: '내 기록', en: 'My Progress', u: '/my-progress.html' }
  ];

  var BNAV = [
    { t: '홈', en: 'Home', ic: '🏠', u: '/index.html' },
    { t: '카탈로그', en: 'Catalog', ic: '🛡️', u: '/vuln-hub.html' },
    { t: '취약점랩', en: 'Vuln Lab', ic: '🧪', u: '/vulnlab.html' },
    { t: '레드팀', en: 'Red Team', ic: '🦹', u: '/redteam.html' },
    { t: '내 기록', en: 'Progress', ic: '📊', u: '/my-progress.html' }
  ];

  /* 모바일(≤768px)에서는 우상단 고정 언어 바가 본문 제목을 가려 숨긴다(bilingual.js).
     그렇다고 전환 수단 자체가 사라지면 영어 사용자는 폰에서 언어를 못 바꾼다.
     그래서 하단 탭바에 전환 버튼을 둔다 — 단, 본문 번역을 실제로 적용할 수 있는
     bilingual.js 가 있는 페이지에서만. 없으면 크롬만 바뀌어 사용자를 속인다. */
  function bilingualReady() {
    return !!(window.WVS_BILINGUAL && typeof window.WVS_BILINGUAL.setLang === 'function');
  }
  /* 59개 페이지는 본문 안에 자체 언어 버튼(.langbtn)을 갖고 있다.
     거기에 탭바 버튼까지 붙이면 같은 기능이 두 개 보여 어느 쪽이 진짜인지 헷갈린다.
     화면에 실제로 보이는(offsetParent 가 있는) 자체 버튼이 있으면 탭바에는 넣지 않는다. */
  function hasOwnLangToggle() {
    var el = document.querySelector('.langbtn, [data-wvs-langtoggle]');
    return !!(el && el.offsetParent !== null);
  }
  function switchLang() {
    var next = lang() === 'en' ? 'ko' : 'en';
    if (bilingualReady()) { window.WVS_BILINGUAL.setLang(next); return; }
    try { localStorage.setItem('wvs_lang', next); } catch (e) { /* no-op */ }
    document.dispatchEvent(new CustomEvent('wvs:lang', { detail: { lang: next } }));
  }


  var GROUP_STYLE = {
    code: ['#38bdf8', 'CODE'], design: ['#38bdf8', 'CODE'], sim: ['#f87171', 'SIM'],
    guide: ['#94a3b8', 'GUIDE'], unix: ['#4ade80', 'UNIX'], db: ['#fbbf24', 'DB'],
    fin: ['#fbbf24', 'FIN'], win: ['#60a5fa', 'WIN'], net: ['#a78bfa', 'NET'],
    sec: ['#f472b6', 'SEC'], cloud: ['#7dd3fc', 'CLD'], ics: ['#fb923c', 'ICS'],
    ai: ['#c4b5fd', 'AI'], auto: ['#fb7185', 'AUTO'], tools: ['#e2e8f0', 'TOOL'],
    zt: ['#5eead4', 'ZT'], privacy: ['#a5b4fc', 'PRIV'], governance: ['#fcd34d', 'GOV'],
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
    /* 좁은 화면에서는 상단 내비를 숨긴다.
       로고와 검색 버튼 사이에 남는 폭이 360px 기준 113px 뿐인데 링크 6개(411px)를 넣어
       두었더니 "홈 카탈로그 취" 처럼 글자 중간에서 잘리고, 나머지는 가로로 밀어야 보였다.
       같은 링크를 아래 .wvsx-bnav(하단 탭바)가 ≤640px 에서 이미 제공하고(buildTopbar 와
       buildBottomNav 는 항상 같이 호출된다), 탭바에 없는 quiz-forge 는 카탈로그와
       검색 팔레트로 닿는다. 숨기는 대신 검색 버튼을 오른쪽 끝으로 민다. */
    '@media(max-width:640px){.wvsx-top{gap:10px;padding:0 12px}.wvsx-top .wvsx-kbtn .kb{display:none}',
    '.wvsx-top .wvsx-nav{display:none}.wvsx-top .wvsx-kbtn{margin-left:auto}}',
    /* 모바일 하단 탭바 (Bottom Navigation) */
    '.wvsx-bnav{position:fixed;left:0;right:0;bottom:0;z-index:var(--wvs-z-sticky,100);display:none;',
    'background:rgba(8,14,26,.95);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);',
    'border-top:1px solid #1e293b;padding:5px 4px max(6px,env(safe-area-inset-bottom,6px));',
    'justify-content:space-around;align-items:center;box-shadow:0 -4px 20px rgba(0,0,0,.45);',
    "font-family:'Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif;box-sizing:border-box}",
    '@media(max-width:640px){.wvsx-bnav{display:flex}}',
    '.wvsx-bnav a{display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;',
    'min-width:0;padding:4px 2px;color:#8fa0ba;text-decoration:none;font-size:.67rem;font-weight:600;',
    'border-radius:8px;transition:color .15s,background .15s;-webkit-tap-highlight-color:transparent}',
    '.wvsx-bnav a:active{background:rgba(56,189,248,.12)}',
    '.wvsx-bnav a.on{color:#38bdf8;font-weight:800}',
    '.wvsx-bnav .ic{font-size:1.15rem;line-height:1.2;margin-bottom:1px}',
    /* 건너뛰기 링크 — 포커스를 받기 전까지는 보이지 않는다 */
    '.wvsx-skip{position:fixed;left:8px;top:-60px;z-index:var(--wvs-z-toast,1000);background:#0e1626;',
    'color:#7dd3fc;border:1px solid #38bdf8;border-radius:8px;padding:9px 16px;font-size:.82rem;',
    "font-weight:700;text-decoration:none;transition:top .15s;font-family:'Segoe UI','Noto Sans KR',sans-serif}",
    '.wvsx-skip:focus{top:8px;outline:2px solid var(--wvs-focus,#38bdf8);outline-offset:2px}',
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
      lk.href = '/css/platform-tokens.css?v=20260913_fix4';
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
    if (f === 'index.html' && (p === '/' || p === '' || p.endsWith('/index.html'))) return true;
    if (!f) return false;
    return p === '/' + f || p.slice(-1 - f.length) === '/' + f;
  }
  function buildTopbar() {
    if (TOPBAR_OFF) return;
    var bar = document.createElement('div');
    bar.className = 'wvsx-top';
    bar.id = 'wvsx-topbar';
    var html = '<a class="wvsx-logo" href="/index.html"><span class="mk">⛨</span>WEB-VULN-SIM</a>';
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
    /* 다른 고정 요소가 이 바를 피해 갈 수 있도록 실제 높이를 변수로 내보낸다.
       auth-widget.js 의 #authWidget 이 top:12px 로 붙어 있어 이 바의 검색 버튼을
       z-index 100000 으로 덮고 있었다(17개 페이지 전부, 폭 무관). 상수 42px 를
       양쪽에 하드코딩하면 한쪽만 바뀔 때 다시 어긋나므로 잰 값을 쓴다. */
    syncTopbarOffset();
    window.addEventListener('load', syncTopbarOffset);
    window.addEventListener('resize', syncTopbarOffset);
    document.documentElement.classList.add('wvs-has-topbar');
  }

  /* 이 바를 피해야 하는 고정 오버레이(auth-widget 의 #authWidget, bilingual 의 .wvs-langbar)가
     쓸 세로 여유를 --wvs-topbar-h 로 내보낸다.

     바는 sticky(top:0) 이므로 스크롤하면 0..42 로 올라붙지만, body 에 padding-top 이 있는
     페이지(certificate.html 40px)에서는 스크롤 전에 그만큼 내려와 있다. 그래서
     '문서 기준 바 윗변 + 높이' 를 쓴다.
     build 시점에 한 번만 재면 폰트·비동기 콘텐츠 때문에 엉뚱한 값이 잡힌다(실제로 82 대신
     클램프 상한 160 이 나왔다). load/resize 에서 다시 잰다. */
  function syncTopbarOffset() {
    var bar = document.getElementById('wvsx-topbar');
    if (!bar) return;
    var h = bar.offsetHeight || 42;
    var topInDoc = bar.getBoundingClientRect().top + (window.pageYOffset || 0);
    var v = Math.round(h + Math.max(0, topInDoc));
    if (!(v > 0) || v > 160) v = Math.min(160, h);
    document.documentElement.style.setProperty('--wvs-topbar-h', v + 'px');
  }

  /* ── 본문 랜드마크 + 건너뛰기 링크 (QA-P2-03 / P1-06) ──
     519개 페이지에 <main> 이 없어 스크린리더가 "본문"으로 바로 갈 수 없었다.
     페이지마다 구조가 제각각이라 HTML 을 일괄 수정하면 레이아웃이 깨질 위험이 크다.
     접근성 트리에만 필요한 정보이므로 런타임에 role="main" 을 붙인다.
     고르는 기준은 "h1 을 담고 있는, body 바로 아래 블록" — 사람이 본문이라고 부르는 것. */
  function markMainLandmark() {
    if (document.querySelector('main, [role="main"]')) return null;
    var h1 = document.querySelector('h1');
    var el = null;
    if (h1) {
      el = h1;
      while (el.parentElement && el.parentElement !== document.body) el = el.parentElement;
      if (el === h1) el = null;                       /* h1 이 body 직계면 감쌀 블록이 없다 */
    }
    if (!el) {
      var kids = document.body.children;
      for (var i = 0; i < kids.length; i++) {
        var k = kids[i];
        if (/^(SCRIPT|STYLE|LINK|NAV|HEADER|FOOTER)$/.test(k.tagName)) continue;
        if (/wvsx-|wvs-/.test(k.id || '') || /wvsx-|wvs-langbar/.test(k.className || '')) continue;
        el = k; break;
      }
    }
    if (!el || el === document.body) return null;
    el.setAttribute('role', 'main');
    if (!el.id) el.id = 'wvs-main';
    return el.id;
  }
  function addSkipLink(mainId) {
    if (!mainId || document.getElementById('wvsx-skip')) return;
    var a = document.createElement('a');
    a.id = 'wvsx-skip';
    a.className = 'wvsx-skip';
    a.href = '#' + mainId;
    a.textContent = lang() === 'en' ? 'Skip to content' : '본문 바로가기';
    a.addEventListener('click', function () {
      var m = document.getElementById(mainId);
      if (!m) return;
      if (!m.hasAttribute('tabindex')) m.setAttribute('tabindex', '-1');
      setTimeout(function () { m.focus(); }, 0);
    });
    document.body.insertBefore(a, document.body.firstChild);
  }

  function buildBottomNav() {
    if (document.getElementById('wvsx-bnav')) return;
    var bnav = document.createElement('nav');
    bnav.className = 'wvsx-bnav';
    bnav.id = 'wvsx-bnav';
    bnav.setAttribute('aria-label', lang() === 'en' ? 'Mobile navigation' : '모바일 빠른 이동');
    var en = lang() === 'en';
    var html = '';
    for (var i = 0; i < BNAV.length; i++) {
      var b = BNAV[i];
      var on = isCurrent(b.u);
      html += '<a href="' + b.u + '"' + (on ? ' class="on" aria-current="page"' : '') + '>' +
        '<span class="ic">' + b.ic + '</span>' +
        '<span>' + (en ? b.en : b.t) + '</span></a>';
    }
    if (bilingualReady() && !hasOwnLangToggle()) {
      html += '<a href="#" id="wvsx-bnav-lang" role="button" aria-label="' +
        (en ? 'Switch to Korean' : '영어로 전환') + '">' +
        '<span class="ic">🌐</span><span>' + (en ? '한국어' : 'EN') + '</span></a>';
    }
    bnav.innerHTML = html;
    document.body.appendChild(bnav);
    var lb = document.getElementById('wvsx-bnav-lang');
    if (lb) lb.addEventListener('click', function (e) { e.preventDefault(); switchLang(); });
    /* 하단 탭바가 본문 끝을 가리지 않도록 여백 규칙을 켠다(platform-tokens.css).
       탭바가 없는 페이지까지 여백이 생기지 않게 클래스로 한정한다. */
    document.documentElement.classList.add('wvs-has-bnav');
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

  /* 떠 있는 보조 컨트롤(언어바·진도 칩) 숨김.
     CSS 규칙(body.wvs-modal-open …)만으로는 opacity 가 적용되지 않는 사례가 있어
     — pointer-events 는 먹는데 opacity 만 무시되는 현상을 라이브에서도 확인 —
     인라인 스타일로 직접 지정한다. 인라인은 캐스케이드 논쟁 없이 확실하다. */
  function setFloatingHidden(hide) {
    var els = document.querySelectorAll('.wvs-langbar, #wvs-progress-chip, .wvsx-bnav');
    for (var i = 0; i < els.length; i++) {
      els[i].style.opacity = hide ? '0' : '';
      els[i].style.pointerEvents = hide ? 'none' : '';
    }
  }

  var lastFocus = null;
  function openPalette() {
    buildPalette();
    lastFocus = document.activeElement;
    palEl.classList.add('show');
    document.body.classList.add('wvs-modal-open');
    setFloatingHidden(true);
    inpEl.value = '';
    refresh();
    setTimeout(function () { inpEl.focus(); }, 30);
  }
  function closePalette() {
    if (!palEl || !palEl.classList.contains('show')) return;
    palEl.classList.remove('show');
    document.body.classList.remove('wvs-modal-open');
    setFloatingHidden(false);
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
    try { injectCss(); buildTopbar(); buildBottomNav(); } catch (e) { /* 어떤 페이지에서도 크래시 없이 */ }
    try { addSkipLink(markMainLandmark()); } catch (eM) { /* no-op */ }
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
    /* bilingual.js 가 이 스크립트보다 늦게 실행되는 페이지가 있어(로딩 순서가 제각각),
       boot 시점엔 언어 버튼 조건이 거짓일 수 있다. load 후 한 번만 다시 확인한다. */
    window.addEventListener('load', function () {
      try {
        if (!bilingualReady() || hasOwnLangToggle()) return;
        if (document.getElementById('wvsx-bnav-lang')) return;
        var oldB = document.getElementById('wvsx-bnav');
        if (oldB) { oldB.remove(); buildBottomNav(); }
      } catch (eL) { /* no-op */ }
    });
    /* 언어를 바꾸면 크롬은 이미 그려진 상태이므로 직접 다시 그린다(bilingual.js 가 알림). */
    document.addEventListener('wvs:lang', function () {
      try {
        var old = document.getElementById('wvsx-topbar');
        if (old) { old.remove(); buildTopbar(); }
        var oldB = document.getElementById('wvsx-bnav');
        if (oldB) { oldB.remove(); buildBottomNav(); }
        if (palEl) { palEl.remove(); palEl = null; inpEl = null; listEl = null; }
      } catch (e3) { /* no-op */ }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();

