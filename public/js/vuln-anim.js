/* WEB-VULN-SIM — 취약점 설명 페이지 프로그레시브 애니메이션 (재생성 불필요, 순수 얹기)
 * 대상: 넘버드 설명 페이지(03_code/04_design/05~12 인프라/07_fin/13_ai).
 *  (a) 공통: 주요 블록 스크롤 리빌(fade-up) — SOC 대시보드 등장감.
 *  (b) gen_infra 계열(#termBody + 전역 setState): 상태 토글 시 터미널을 라인별로
 *      스트리밍 + 취약(빨강)/안전(초록) 펄스 + 커서. "라이브 콘솔" 전문성.
 * 방어적: 훅 없으면 no-op. prefers-reduced-motion 시 모션 전부 생략(콘텐츠는 그대로).
 */
(function () {
  'use strict';
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}

  // 공용 스타일 1회 주입
  function injectStyle() {
    if (document.getElementById('va-style')) return;
    var css = [
      '@keyframes vaLine{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}',
      '@keyframes vaBlink{0%,49%{opacity:1}50%,100%{opacity:0}}',
      '@keyframes vaPulseBad{0%{box-shadow:0 0 0 rgba(239,68,68,.0)}30%{box-shadow:-3px 0 8px rgba(239,68,68,.35)}100%{box-shadow:none}}',
      '@keyframes vaPulseGood{0%{box-shadow:0 0 0 rgba(34,197,94,.0)}30%{box-shadow:-3px 0 8px rgba(34,197,94,.35)}100%{box-shadow:none}}',
      '.va-line{display:block}',
      '.va-line.bad,.va-line .bad{animation:vaPulseBad 1.1s ease}',
      '.va-line.good,.va-line .good{animation:vaPulseGood 1.1s ease}',
      '.va-cursor{display:inline-block;width:8px;height:1.05em;background:currentColor;margin-left:2px;vertical-align:-2px;animation:vaBlink 1s steps(1) infinite;opacity:.85}',
      '.va-reveal{opacity:0;transform:translateY(14px);transition:opacity .5s ease,transform .5s ease;will-change:opacity,transform}',
      '.va-reveal.va-in{opacity:1;transform:none}'
    ].join('');
    var st = document.createElement('style');
    st.id = 'va-style'; st.textContent = css;
    document.head.appendChild(st);
  }

  // ── (b) gen_infra 터미널 스트리밍 ─────────────────────────────
  function streamTerminal(body) {
    if (reduce || !body) return;
    var html = body.innerHTML;
    if (!html) return;
    var lines = html.split('\n');
    body.innerHTML = '';
    var frag = document.createDocumentFragment();
    lines.forEach(function (ln, i) {
      var div = document.createElement('div');
      div.className = 'va-line';
      div.innerHTML = (ln === '' ? '&nbsp;' : ln);
      // 라인 내부에 bad/good 스팬이 있으면 그 색 펄스를 라인에 반영
      if (div.querySelector('.bad')) div.classList.add('bad');
      else if (div.querySelector('.good')) div.classList.add('good');
      div.style.opacity = '0';
      div.style.animation = 'vaLine .26s ease forwards';
      div.style.animationDelay = Math.min(i * 85, 900) + 'ms';
      frag.appendChild(div);
    });
    body.appendChild(frag);
    // 마지막 줄에 커서
    var last = body.lastElementChild;
    if (last) {
      var cur = document.createElement('span');
      cur.className = 'va-cursor';
      var totalDelay = Math.min((lines.length - 1) * 85, 900) + 260;
      cur.style.opacity = '0';
      setTimeout(function () { if (cur && last) { cur.style.opacity = ''; last.appendChild(cur); } }, totalDelay);
    }
  }

  function enhanceTerminal() {
    var body = document.getElementById('termBody');
    if (!body || typeof window.setState !== 'function') return false;
    var orig = window.setState;
    window.setState = function (s) {
      try { orig(s); } catch (e) {}
      streamTerminal(document.getElementById('termBody'));
    };
    streamTerminal(body); // 초기 상태(취약) 스트리밍
    return true;
  }

  // ── (a) 스크롤 리빌 ──────────────────────────────────────────
  function scrollReveal() {
    if (reduce || !('IntersectionObserver' in window)) return;
    var sel = '.card, .section, .terminal, .code-display, .attack-controls, .fix-steps, .checklist, .kref';
    var els = [].slice.call(document.querySelectorAll(sel));
    if (!els.length) return;
    // 이미 화면 상단에 보이는 첫 요소는 즉시 노출(FOUC 최소화)
    els.forEach(function (el) { el.classList.add('va-reveal'); });
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('va-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { io.observe(el); });
    // 안전장치: 1.8s 후에도 안 켜진 요소는 강제 노출(관측 실패 대비)
    setTimeout(function () { els.forEach(function (el) { el.classList.add('va-in'); }); }, 1800);
  }

  function boot() {
    if (reduce) return;            // 모션 최소화 사용자는 원본 그대로
    injectStyle();
    enhanceTerminal();
    scrollReveal();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
