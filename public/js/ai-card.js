/* ai-card.js - AI 개념 카드 상단 학습 정보 띠와 이전, 다음 (AI 개편안 A-05)
 *
 * 26개 카드에 난이도, 예상 시간, 선수 개념, 트랙 위치를 붙인다.
 * 각 페이지의 HTML 구조가 조금씩 달라서, 문서를 재배치하지 않고
 * body 첫머리와 끝에 요소를 얹는 방식을 쓴다.
 */
(function () {
  'use strict';

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  function style() {
    if (document.getElementById('wvs-aicard-css')) return;
    var st = document.createElement('style');
    st.id = 'wvs-aicard-css';
    st.textContent = [
      '#wvs-ai-meta{max-width:1000px;margin:14px auto 0;padding:13px 16px;border-radius:12px;',
      'background:#0f172a;border:1px solid #1e3a5f;color:#cbd5e1;',
      'font:13px/1.6 "Segoe UI","Malgun Gothic",sans-serif}',
      '#wvs-ai-meta .r1{display:flex;gap:9px;flex-wrap:wrap;align-items:center;margin-bottom:7px}',
      '#wvs-ai-meta .pill{display:inline-flex;align-items:center;gap:5px;border-radius:999px;',
      'padding:4px 11px;font-size:12px;font-weight:700;background:#1e293b;color:#e2e8f0;border:1px solid #334155}',
      '#wvs-ai-meta .pill.lv1{background:#052e1a;border-color:#14532d;color:#86efac}',
      '#wvs-ai-meta .pill.lv2{background:#0c2333;border-color:#155e75;color:#7dd3fc}',
      '#wvs-ai-meta .pill.lv3{background:#2e1065;border-color:#4c1d95;color:#c4b5fd}',
      '#wvs-ai-meta .mod{color:#94a3b8;font-size:12.5px}',
      '#wvs-ai-meta .pre{margin:0;font-size:12.5px;color:#94a3b8}',
      '#wvs-ai-meta .pre a{color:#7dd3fc;text-decoration:none;border-bottom:1px dotted #0e7490}',
      '#wvs-ai-meta .pre a:hover{border-bottom-style:solid}',
      '#wvs-ai-nav{max-width:1000px;margin:26px auto 0;padding:0 16px;display:flex;gap:10px;',
      'align-items:center;justify-content:space-between;flex-wrap:wrap;',
      'font:600 13px/1.4 "Segoe UI","Malgun Gothic",sans-serif}',
      '#wvs-ai-nav a{flex:0 0 auto;max-width:46%;background:#1e293b;color:#e2e8f0;border:1px solid #334155;',
      'border-radius:9px;padding:10px 15px;text-decoration:none;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
      '#wvs-ai-nav a:hover{background:#334155}',
      '#wvs-ai-nav .mid{color:#94a3b8;font-weight:400;font-size:12.5px;text-align:center;flex:1;min-width:120px}',
      '#wvs-ai-nav .mid a{background:none;border:0;padding:0;color:#7dd3fc;display:inline}',
      '@media(max-width:560px){#wvs-ai-nav a{max-width:100%;flex:1 1 100%;text-align:center}}'
    ].join('');
    document.head.appendChild(st);
  }

  function pill(cls, text) {
    var s = document.createElement('span');
    s.className = 'pill' + (cls ? ' ' + cls : '');
    s.textContent = text;
    return s;
  }

  function build(card, T) {
    var mod = T.moduleOf(card.module);
    var box = document.createElement('div');
    box.id = 'wvs-ai-meta';
    box.setAttribute('role', 'note');
    box.setAttribute('aria-label', L('학습 정보', 'Study info'));

    var r1 = document.createElement('div');
    r1.className = 'r1';
    r1.appendChild(pill('lv' + card.level,
      L('난이도 ', 'Level ') + (isEn() ? card.levelLabelEn : card.levelLabel)));
    r1.appendChild(pill('', L('예상 ' + card.minutes + '분', 'about ' + card.minutes + ' min')));
    r1.appendChild(pill('', L('트랙 ' + card.order + ' / ' + T.PATH.length,
                              'Step ' + card.order + ' of ' + T.PATH.length)));
    var m = document.createElement('span');
    m.className = 'mod';
    m.textContent = mod ? (T.T ? T.T(mod.label) : mod.label) : '';
    r1.appendChild(m);
    box.appendChild(r1);

    var p = document.createElement('p');
    p.className = 'pre';
    if (card.prereq.length) {
      p.appendChild(document.createTextNode(L('먼저 보면 좋은 것: ', 'Read first: ')));
      card.prereq.forEach(function (q, i) {
        if (i) p.appendChild(document.createTextNode(', '));
        var a = document.createElement('a');
        a.href = q.file; a.textContent = isEn() ? (q.labelEn || q.label) : q.label;
        p.appendChild(a);
      });
    } else {
      p.textContent = L('선수 개념 없이 바로 볼 수 있습니다.', 'No prerequisites: you can start here.');
    }
    var hub = document.createElement('a');
    hub.href = 'ai-hub.html';
    hub.textContent = L('AI 트랙 전체 보기', 'See the whole AI track');
    p.appendChild(document.createTextNode(' · '));
    p.appendChild(hub);
    box.appendChild(p);
    return box;
  }

  function nav(card, T) {
    var i = card.order - 1;
    var prev = T.PATH[i - 1], next = T.PATH[i + 1];
    var box = document.createElement('nav');
    box.id = 'wvs-ai-nav';
    box.setAttribute('aria-label', L('AI 트랙 이동', 'AI track navigation'));

    if (prev) {
      var a = document.createElement('a');
      a.href = prev.file;
      a.textContent = '← ' + prev.code;
      box.appendChild(a);
    } else {
      box.appendChild(document.createElement('span'));
    }

    var mid = document.createElement('span');
    mid.className = 'mid';
    mid.appendChild(document.createTextNode(card.code + ' · '));
    var h = document.createElement('a');
    h.href = 'ai-hub.html';
    h.textContent = L('AI 트랙 허브', 'AI track hub');
    mid.appendChild(h);
    box.appendChild(mid);

    if (next) {
      var b = document.createElement('a');
      b.href = next.file;
      b.textContent = next.code + ' →';
      box.appendChild(b);
    } else {
      var c = document.createElement('a');
      c.href = 'ai-guardrail-lab.html';
      c.textContent = L('가드레일 연습장 →', 'Guardrail lab →');
      box.appendChild(c);
    }
    return box;
  }

  function run() {
    var T = window.WvsAiTrack;
    if (!T) return;
    var file = (location.pathname.split('/').pop() || '').toLowerCase();
    var card = T.BY_FILE[file];
    if (!card) return;
    if (document.getElementById('wvs-ai-meta')) return;

    style();
    var main = document.getElementById('wvs-main') || document.body;
    main.insertBefore(build(card, T), main.firstChild);

    var footer = document.getElementById('wvs-footer');
    var navEl = nav(card, T);
    if (footer && footer.parentNode) footer.parentNode.insertBefore(navEl, footer);
    else document.body.appendChild(navEl);

    T.markVisited(file);
  }

  /* shell.js 가 #wvs-main 과 푸터를 만든 다음에 얹는다. */
  function boot() {
    var tries = 0;
    var t = setInterval(function () {
      if (document.getElementById('wvs-main') || ++tries > 12) {
        clearInterval(t);
        run();
      }
    }, 120);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
