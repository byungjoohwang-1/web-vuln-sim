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
  var NAV = [
    { t: '홈', u: '/vuln-hub.html' },
    { t: '레드팀 아레나', u: '/redteam.html' },
    { t: '취약점 실습장', u: '/vulnlab.html' },
    { t: 'AI 문제 포지', u: '/quiz-forge.html' },
    { t: '카탈로그', u: '/vuln-hub.html#catalog' },
    { t: '내 기록', u: '/my-progress.html' }
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
    '.wvsx-top{position:sticky;top:0;z-index:9000;display:flex;align-items:center;gap:18px;',
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
    '.wvsx-pal{position:fixed;inset:0;z-index:99999;display:none;align-items:flex-start;',
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
    '.wvsx-pal .ft{display:flex;gap:14px;padding:9px 16px;border-top:1px solid #1e293b;',
    'color:#475569;font-size:.66rem}',
    '.wvsx-pal .ft b{color:#64748b;font-weight:600}'
  ].join('');

  function injectCss() {
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
    for (var i = 0; i < NAV.length; i++) {
      var n = NAV[i];
      html += '<a href="' + n.u + '"' + (isCurrent(n.u) ? ' class="on"' : '') + '>' + n.t + '</a>';
    }
    html += '</nav>';
    html += '<button type="button" class="wvsx-kbtn" id="wvsx-kbtn">🔍 검색 <span class="kb">Ctrl K</span></button>';
    bar.innerHTML = html;
    if (document.body.firstChild) document.body.insertBefore(bar, document.body.firstChild);
    else document.body.appendChild(bar);
    document.getElementById('wvsx-kbtn').addEventListener('click', function () { openPalette(); });
  }

  /* ── 커맨드 팔레트 ── */
  var INDEX = null, INDEX_TRIED = false;
  var palEl = null, inpEl = null, listEl = null;
  var results = [], sel = 0;

  function loadIndex(cb) {
    if (INDEX || INDEX_TRIED) return cb(!!INDEX);
    INDEX_TRIED = true;
    try {
      fetch(INDEX_URL).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        INDEX = (d && d.pages) ? d.pages : [];
        if (INDEX.length && d.kw) { /* 키워드는 항목 내 u/t에 이미 병합됨 */ }
        cb(!!INDEX);
      }).catch(function () { cb(false); });
    } catch (e) { cb(false); }
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
      '<div class="box" role="dialog" aria-label="사이트 검색">' +
      '<div class="inp"><span class="ic">⌕</span>' +
      '<input id="wvsx-pal-inp" type="text" placeholder="페이지·시나리오·도구 검색 (예: SQL, U-01, 레드팀)" autocomplete="off">' +
      '<span class="esc">ESC</span></div>' +
      '<div class="list" id="wvsx-pal-list"></div>' +
      '<div class="ft"><span><b>↑↓</b> 이동</span><span><b>↵</b> 열기</span><span><b>ESC</b> 닫기</span></div>' +
      '</div>';
    document.body.appendChild(palEl);
    inpEl = palEl.querySelector('#wvsx-pal-inp');
    listEl = palEl.querySelector('#wvsx-pal-list');
    inpEl.addEventListener('input', function () { runSearch(inpEl.value); });
    inpEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Enter') { e.preventDefault(); go(sel); }
      else if (e.key === 'Escape') { closePalette(); }
    });
    palEl.addEventListener('click', function (e) {
      if (e.target === palEl) closePalette();
      var row = e.target.closest ? e.target.closest('.wvsx-pal .row') : null;
      if (row && row.getAttribute('data-i') != null) go(+row.getAttribute('data-i'));
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
    if (!INDEX) { listEl.innerHTML = '<div class="empty">검색 인덱스를 불러올 수 없습니다.</div>'; return; }
    var nq = norm(q);
    if (!nq) {
      // 기본: 대표 페이지 추천
      var quick = ['vuln-hub.html', 'redteam.html', 'vulnlab.html', 'quiz-forge.html', 'my-progress.html', 'labs-live.html', 'ai-tutor.html'];
      results = INDEX.filter(function (p) { return quick.indexOf(p.u) >= 0; });
      sel = 0; render('빠른 실행'); return;
    }
    var scored = [];
    for (var i = 0; i < INDEX.length; i++) {
      var s = score(INDEX[i], nq);
      if (s > 0) scored.push({ p: INDEX[i], s: s });
    }
    scored.sort(function (a, b) { return b.s - a.s; });
    results = scored.slice(0, 30).map(function (x) { return x.p; });
    sel = 0;
    render(results.length ? null : '검색 결과가 없습니다');
  }

  function render(emptyMsg) {
    var html = '';
    if (emptyMsg) { html = '<div class="empty">' + esc(emptyMsg) + '</div>'; }
    else {
      for (var i = 0; i < results.length; i++) {
        var p = results[i];
        var gs = GROUP_STYLE[p.g] || GROUP_STYLE.tools;
        html += '<div class="row' + (i === sel ? ' sel' : '') + '" data-i="' + i + '">' +
          '<span class="g" style="color:' + gs[0] + ';border-color:' + gs[0] + '55">' + gs[1] + '</span>' +
          '<span class="tt">' + esc(p.t) + '</span>' +
          '<span class="uu">' + esc(p.u) + '</span></div>';
      }
    }
    listEl.innerHTML = html;
  }

  function move(d) {
    if (!results.length) return;
    sel = (sel + d + results.length) % results.length;
    render(null);
    var el = listEl.querySelector('.row.sel');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
  }

  function go(i) {
    if (!results[i]) return;
    var u = results[i].u;
    closePalette();
    location.href = u.charAt(0) === '/' ? u : '/' + u;
  }

  function openPalette() {
    buildPalette();
    palEl.classList.add('show');
    inpEl.value = '';
    loadIndex(function (ok) { if (ok) runSearch(''); else listEl.innerHTML = '<div class="empty">검색 인덱스 로드 실패</div>'; });
    setTimeout(function () { inpEl.focus(); }, 30);
  }
  function closePalette() { if (palEl) palEl.classList.remove('show'); }

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
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
