/* safety-notice.js - 실습 시작 안전 고지 (QA W-08, AI 개편안 A-03)
 *
 * 공격형 실습(시뮬레이터, 브리치 캠페인, DAST 콘솔, AI 가드레일 연습장)에
 * 처음 들어올 때 한 번 고지를 띄운다. 확인하면 다시 뜨지 않고,
 * 푸터의 "안전 고지 다시 보기" 로 언제든 다시 열 수 있다.
 *
 * 고지 문구는 이 사이트의 전제를 그대로 적은 것이다.
 * 모든 시연은 페이지 안에서 끝나는 모의 환경이고, 외부 시스템을 향하지 않는다.
 */
(function () {
  'use strict';

  var KEY = 'wvs_safety_ack_v1';

  function isEn() {
    try {
      return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en';
    } catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  function acked() {
    try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; }
  }
  function ack() {
    try { localStorage.setItem(KEY, '1'); } catch (e) { /* 저장 못 해도 진행은 막지 않는다 */ }
  }
  function reset() {
    try { localStorage.removeItem(KEY); } catch (e) {}
  }

  function style() {
    if (document.getElementById('wvs-safety-css')) return;
    var st = document.createElement('style');
    st.id = 'wvs-safety-css';
    st.textContent = [
      '#wvs-safety-back{position:fixed;inset:0;z-index:100050;background:rgba(2,6,23,.74);',
      'display:flex;align-items:center;justify-content:center;padding:20px;',
      'font:14px/1.65 "Segoe UI","Malgun Gothic",sans-serif}',
      '#wvs-safety{background:#0f172a;color:#e2e8f0;border:1px solid #1e3a5f;border-radius:16px;',
      'max-width:560px;width:100%;max-height:86vh;overflow:auto;padding:26px 26px 20px;',
      'box-shadow:0 30px 70px rgba(0,0,0,.55)}',
      '#wvs-safety h2{margin:0 0 12px;font-size:19px;font-weight:800;color:#fff}',
      '#wvs-safety p{margin:0 0 12px}',
      '#wvs-safety ul{margin:0 0 14px;padding-left:20px}',
      '#wvs-safety li{margin:0 0 7px}',
      '#wvs-safety b{color:#fbbf24}',
      '#wvs-safety .wvs-sf-foot{display:flex;gap:10px;flex-wrap:wrap;align-items:center;',
      'justify-content:flex-end;border-top:1px solid #1e293b;padding-top:14px;margin-top:4px}',
      '#wvs-safety button{font:700 14px/1 inherit;border-radius:9px;padding:11px 20px;cursor:pointer;border:1px solid transparent}',
      '#wvs-safety .ok{background:#0ea5e9;color:#04240f;border-color:#0ea5e9}',
      '#wvs-safety .ok:hover{background:#38bdf8}',
      '#wvs-safety .back{background:transparent;color:#94a3b8;border-color:#334155}',
      '#wvs-safety .back:hover{color:#e2e8f0}',
      '#wvs-safety .wvs-sf-note{flex:1;min-width:180px;font-size:12px;color:#64748b}',
      '.wvs-safety-relink{background:none;border:0;color:inherit;font:inherit;text-decoration:underline;cursor:pointer;padding:0}'
    ].join('');
    document.head.appendChild(st);
  }

  var lastFocus = null;

  function close(back) {
    var el = document.getElementById('wvs-safety-back');
    if (el) el.remove();
    document.removeEventListener('keydown', onKey, true);
    if (back) { history.back(); return; }
    if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) {} }
  }

  function onKey(e) {
    if (e.key === 'Escape') { e.preventDefault(); return; }  /* 확인 없이 닫히지 않게 한다 */
    if (e.key !== 'Tab') return;
    var box = document.getElementById('wvs-safety');
    if (!box) return;
    var f = box.querySelectorAll('button');
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  function open(opts) {
    opts = opts || {};
    if (document.getElementById('wvs-safety-back')) return;
    style();
    lastFocus = document.activeElement;

    var back = document.createElement('div');
    back.id = 'wvs-safety-back';

    var box = document.createElement('div');
    box.id = 'wvs-safety';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.setAttribute('aria-labelledby', 'wvs-safety-h');

    var h = document.createElement('h2');
    h.id = 'wvs-safety-h';
    h.textContent = L('실습을 시작하기 전에', 'Before you start this lab');
    box.appendChild(h);

    var p1 = document.createElement('p');
    p1.innerHTML = L(
      '이 실습은 <b>이 페이지 안에서만 동작하는 모의 환경</b>입니다. ' +
      '입력한 값은 브라우저를 벗어나지 않고, 어떤 외부 시스템에도 요청을 보내지 않습니다.',
      'This lab is a <b>mock that runs entirely inside this page</b>. ' +
      'What you type never leaves your browser, and no request goes to any external system.');
    box.appendChild(p1);

    var ul = document.createElement('ul');
    [
      L('여기서 배운 방법을 <b>내 것이 아닌 시스템</b>에 시도하지 마세요. 권한 없는 접근은 정보통신망법 위반입니다.',
        'Do not try what you learn here on <b>systems you do not own</b>. Unauthorized access is a crime in most jurisdictions.'),
      L('화면에 나오는 회사명, 계정, 카드번호는 <b>전부 가상</b>입니다.',
        'Every company name, account, and card number on screen is <b>fictional</b>.'),
      L('목표는 공격 기술 습득이 아니라 <b>왜 막아야 하는지</b> 이해하는 것입니다. 시연 옆에는 항상 방어 코드가 함께 있습니다.',
        'The goal is understanding <b>why this must be prevented</b>, not acquiring attack skills. Every demo is paired with defensive code.'),
      L('AI 튜터는 실제 공격 대행, 악성코드 제작, 우회 페이로드 생성 요청을 <b>거부</b>합니다.',
        'The AI tutor <b>refuses</b> requests to attack real targets, build malware, or generate bypass payloads.')
    ].forEach(function (t) {
      var li = document.createElement('li');
      li.innerHTML = t;
      ul.appendChild(li);
    });
    box.appendChild(ul);

    var foot = document.createElement('div');
    foot.className = 'wvs-sf-foot';
    var note = document.createElement('span');
    note.className = 'wvs-sf-note';
    note.textContent = L('이 고지는 처음 한 번만 표시됩니다. 푸터에서 다시 볼 수 있습니다.',
                         'Shown once. You can reopen it from the footer.');
    foot.appendChild(note);

    if (!opts.manual) {
      var b = document.createElement('button');
      b.className = 'back';
      b.type = 'button';
      b.textContent = L('돌아가기', 'Go back');
      b.onclick = function () { close(true); };
      foot.appendChild(b);
    }

    var ok = document.createElement('button');
    ok.className = 'ok';
    ok.type = 'button';
    ok.textContent = opts.manual ? L('닫기', 'Close') : L('이해했습니다, 시작하기', 'I understand, start');
    ok.onclick = function () { if (!opts.manual) ack(); close(false); };
    foot.appendChild(ok);

    box.appendChild(foot);
    back.appendChild(box);
    document.body.appendChild(back);
    document.addEventListener('keydown', onKey, true);
    ok.focus();
  }

  /* 푸터에 "안전 고지 다시 보기" 를 단다. shell.js 가 푸터를 만든 뒤에 호출된다. */
  function addFooterLink() {
    var f = document.getElementById('wvs-footer');
    if (!f || f.querySelector('.wvs-safety-relink')) return;
    var inner = f.querySelector('.wvs-foot-inner') || f;
    var holder = inner.querySelector('p') || inner;
    var sep = document.createTextNode(' ');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'wvs-safety-relink';
    btn.textContent = L('안전 고지 다시 보기', 'Show the safety notice');
    btn.onclick = function () { open({ manual: true }); };
    holder.appendChild(sep);
    holder.appendChild(btn);
  }

  function boot() {
    if (!acked()) open({});
    /* shell.js 가 푸터를 만들기까지 잠깐 걸린다. */
    var tries = 0;
    var t = setInterval(function () {
      addFooterLink();
      if (++tries > 20 || document.querySelector('.wvs-safety-relink')) clearInterval(t);
    }, 250);
  }

  window.wvsSafety = { open: open, acked: acked, reset: reset };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
