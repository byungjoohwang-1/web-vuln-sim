/**
 * 외부 실행 서비스 전송 고지 (QA N-06)
 *
 * 왜 필요한가
 * -----------
 * 연습 IDE 의 "실행" 버튼은 편집기 내용을 **그대로 외부 서비스로 POST** 한다.
 * 화면 어디에도 그 사실이 적혀 있지 않아, 사용자가 사내 코드나 비공개 코드를
 * 붙여넣고 실행하면 의도치 않게 외부로 나간다.
 *
 * 두 페이지(coding-standards, secure-dev-academy)가 서로 다른 코드 경로로
 * 같은 서비스를 부르고 있어서, 고지 문구와 동의 기록을 한 곳에 모은다.
 * 문구가 갈라지면 한쪽만 고쳐지고 다른 쪽은 조용히 남는다.
 *
 * 동작
 * ----
 * - 탭 세션당 한 번만 묻는다(sessionStorage). 탭을 닫으면 다시 묻는다.
 * - 취소하면 호출자가 전송을 중단해야 한다(반환값 false).
 * - confirm() 을 쓰는 이유: 호출부가 동기 코드라 await 를 끼워 넣으면
 *   기존 실행 흐름을 바꿔야 한다. 차단형 확인이 이 자리에선 맞다.
 */
(function () {
  'use strict';

  var KEY = 'wvs_extrun_ack';

  function acked(service) {
    try {
      var raw = sessionStorage.getItem(KEY);
      if (!raw) return false;
      return JSON.parse(raw).indexOf(service) >= 0;
    } catch (e) { return false; }
  }

  function remember(service) {
    try {
      var raw = sessionStorage.getItem(KEY);
      var list = raw ? JSON.parse(raw) : [];
      if (list.indexOf(service) < 0) list.push(service);
      sessionStorage.setItem(KEY, JSON.stringify(list));
    } catch (e) { /* private mode — 다음에 또 묻는다. 조용히 통과시키지는 않는다 */ }
  }

  function isEn() {
    try {
      return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en';
    } catch (e) { return false; }
  }

  /**
   * @param {string} service  사용자에게 보일 서비스 이름 (예: 'Wandbox')
   * @param {string} host     실제 전송되는 호스트 (예: 'wandbox.org')
   * @returns {boolean} 계속 진행해도 되면 true
   */
  function confirmOnce(service, host) {
    if (acked(service)) return true;
    var msg = isEn()
      ? ('Running this code sends the full contents of the editor to an external service'
        + ' (' + host + ').\n\nDo not paste company-internal or otherwise private code.\n\nContinue?')
      : ('실행하면 편집기의 코드 전문이 외부 서비스(' + host + ')로 전송됩니다.\n\n'
        + '사내 코드나 비공개 코드는 붙여넣지 마세요.\n\n계속할까요?');
    if (!window.confirm(msg)) return false;
    remember(service);
    return true;
  }

  function cancelledText() {
    return isEn() ? '⏹ Run cancelled.' : '⏹ 실행을 취소했습니다.';
  }

  window.WVS_EXTERNAL_RUN = { confirmOnce: confirmOnce, cancelledText: cancelledText };
})();
