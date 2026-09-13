/* 부팅 보호 (QA I-02 대응)
 *
 * 문제
 *   exam-runner, question-packs, training-dashboard 등 핵심 학습 화면이
 *   window.onload = function(){...} 로 초기화되고 있었다.
 *   window.onload 는 외부 자원이 전부 끝나야 발화한다. 이 페이지들은
 *   fonts.googleapis.com 스타일시트와 fonts.gstatic.com 폰트를 차단 방식으로 불러왔고,
 *   academy-data.js(380KB) + academy-data-ext.js(247KB) 도 차단 스크립트였다.
 *   폰트가 느리거나 막힌 환경(사내 프록시, 폐쇄망, 자동화 브라우저, 오프라인)에서는
 *   정적 화면만 그려지고 초기화가 영원히 오지 않는다.
 *   게다가 오류 표시가 없어서, 시작 버튼을 눌러도 아무 반응이 없는 것처럼 보였다.
 *
 * 대응
 *   1. DOM 이 준비되는 즉시 초기화한다. 외부 폰트를 기다리지 않는다.
 *   2. 그래도 못 돌면 5초 안전망으로 한 번 더 시도한다.
 *   3. 초기화가 예외로 죽으면 화면에 알린다. 조용히 실패하지 않는다.
 *
 * 이 파일은 window.onload 가 이미 대입된 뒤, 즉 </body> 직전에 놓여야 한다.
 */
(function () {
  'use strict';
  var ran = false;

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  function showError(err) {
    if (document.getElementById('wvs-boot-error')) return;
    var box = document.createElement('div');
    box.id = 'wvs-boot-error';
    box.setAttribute('role', 'alert');
    box.style.cssText =
      'position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:100002;max-width:min(560px,92vw);' +
      'background:#2a1015;border:1px solid #5b1a22;color:#fecaca;border-radius:12px;padding:13px 16px;' +
      'font:13.5px/1.6 "Segoe UI","Malgun Gothic",sans-serif;box-shadow:0 10px 30px rgba(0,0,0,.5)';
    box.innerHTML =
      '<b>⚠ ' + L('화면을 준비하지 못했습니다.', 'This screen failed to start.') + '</b><br>' +
      L('새로고침해도 같은 증상이면 네트워크 차단이나 확장 프로그램을 확인해 주세요.',
        'If refreshing does not help, check network filtering or browser extensions.') +
      '<br><span style="color:#fca5a5;font-size:12px;word-break:break-all">' +
      String((err && err.message) || err || '').slice(0, 200) + '</span>' +
      '<button type="button" style="margin-left:10px;background:#ef4444;border:0;color:#fff;' +
      'border-radius:8px;padding:6px 12px;font-weight:700;cursor:pointer" ' +
      'onclick="location.reload()">' + L('새로고침', 'Reload') + '</button>';
    (document.body || document.documentElement).appendChild(box);
  }

  function run() {
    if (ran) return;
    ran = true;
    var fn = window.onload;
    if (typeof fn !== 'function') return;
    window.onload = null;               // load 이벤트로 두 번 실행되지 않게 한다
    try {
      fn.call(window);
    } catch (e) {
      showError(e);
      if (window.console && console.error) console.error('[WVS boot]', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
  setTimeout(run, 5000);               // 안전망

  // 초기화 이후에 터지는 오류도 조용히 넘기지 않는다.
  window.addEventListener('error', function (e) {
    if (e && e.message && /Script error/i.test(e.message)) return;   // 교차 출처 잡음 제외
    showError(e && (e.error || e.message));
  });
})();
