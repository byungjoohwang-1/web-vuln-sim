/* WEB-VULN-SIM 공통 셸 (QA I-05, I-08, I-12 대응)
 *
 * 이 사이트는 404개의 정적 HTML을 생성기로 찍어 내는 구조라 공통 템플릿이 없었다.
 * 그 결과 랜드마크(main, nav, footer)와 skip link가 사실상 전 페이지에 없었고,
 * 언어를 바꿔도 절반이 넘는 페이지가 html lang="ko" 로 남았다.
 *
 * 이 스크립트는 기존 레이아웃을 재배치하지 않는다.
 * DOM 구조를 바꾸면 페이지마다 손으로 맞춘 flex/grid 레이아웃이 깨지기 때문에,
 * 이미 있는 요소에 역할(role)과 id 를 부여하는 방식으로 랜드마크를 만든다.
 * 보조기술은 정적 태그와 role 을 동일하게 취급한다.
 *
 * 하는 일
 *   1. 본문 랜드마크 지정 + skip link 연결
 *   2. 상단 링크 바를 내비게이션 랜드마크로 지정
 *   3. 공통 푸터(버전, 개인정보 처리방침, 이용약관) 추가
 *   4. 언어 전환 시 html lang, title 동기화
 *   5. 학습 페이지 이전/다음 이동
 *   6. 장식용 아이콘을 보조기술에서 숨김
 */
(function () {
  'use strict';

  var VERSION = '2026.09.13';
  var SKIP_ID = 'wvs-main';
  var page = (location.pathname.split('/').pop() || 'index.html');

  // 푸터와 내비게이션을 붙이지 않는 페이지
  var BARE = ['404.html', 'offline.html', ''];
  var isBare = BARE.indexOf(page) >= 0 || document.body.hasAttribute('data-wvs-bare');

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  /* ---------- 1. 본문 랜드마크 ---------- */
  function markMain() {
    if (document.getElementById(SKIP_ID)) return;
    var el = document.querySelector('main');
    if (!el) {
      // 페이지마다 본문 컨테이너 이름이 다르다. 가장 그럴듯한 것을 고른다.
      var sel = ['.wrap > :not(.topbar):not(.langbar)', '.container', '.wrap', '.content', '#content', '.page', '.main'];
      for (var i = 0; i < sel.length && !el; i++) el = document.querySelector(sel[i]);
    }
    if (!el) {
      // 후보가 없으면 body 의 자식 중 가장 내용이 많은 블록을 본문으로 본다.
      var best = null, bestLen = 0;
      Array.prototype.forEach.call(document.body.children, function (c) {
        if (/^(SCRIPT|STYLE|LINK|NOSCRIPT)$/.test(c.tagName)) return;
        var len = (c.textContent || '').length;
        if (len > bestLen) { bestLen = len; best = c; }
      });
      el = best;
    }
    if (!el) return;
    if (el.id && el.id !== SKIP_ID) {
      // 페이지가 이미 자기 id 를 쓰고 있으면 건드리지 않고 skip link 목적지만 맞춘다.
      var sk = document.querySelector('.wvs-skip');
      if (sk) sk.setAttribute('href', '#' + el.id);
    } else {
      el.id = SKIP_ID;
    }
    if (!el.hasAttribute('role') && el.tagName !== 'MAIN') el.setAttribute('role', 'main');
    el.setAttribute('tabindex', '-1');
  }

  /* ---------- 2. 내비게이션 랜드마크 ---------- */
  function markNav() {
    if (document.querySelector('nav, [role="navigation"]')) return;
    var bar = document.querySelector('.topbar, .navbar, .nav, .langbar, .topnav');
    if (!bar) return;
    if (bar.tagName !== 'NAV') bar.setAttribute('role', 'navigation');
    bar.setAttribute('aria-label', L('주요 메뉴', 'Main navigation'));
  }

  /* ---------- 3. 공통 푸터 ---------- */
  function addFooter() {
    if (isBare || document.getElementById('wvs-footer')) return;
    if (document.querySelector('footer[data-wvs]')) return;
    var f = document.createElement('footer');
    f.id = 'wvs-footer';
    f.setAttribute('data-wvs', '1');
    f.setAttribute('role', 'contentinfo');
    f.innerHTML =
      '<div class="wvs-foot-inner">' +
      '<p class="wvs-foot-note">' +
      L('행정안전부, 한국인터넷진흥원(KISA), 금융보안원 공개 가이드라인을 개념적으로 재구성한 교육용 콘텐츠입니다. 저작권은 각 기관에 있습니다.',
        'Educational content conceptually reconstructed from public guidelines of MOIS, KISA and FSI. Copyright belongs to each institution.') +
      '</p>' +
      '<p class="wvs-foot-links">' +
      '<a href="/index.html">' + L('홈', 'Home') + '</a>' +
      '<a href="/content-map.html">' + L('전체 콘텐츠', 'Content map') + '</a>' +
      '<a href="/privacy-policy.html">' + L('개인정보 처리방침', 'Privacy') + '</a>' +
      '<a href="/terms.html">' + L('이용약관', 'Terms') + '</a>' +
      '</p>' +
      '<p class="wvs-foot-ver">WEB-VULN-SIM ' + VERSION + ' · ' +
      L('교육용 모의 환경입니다. 권한 없는 시스템에 사용하지 마세요.',
        'Simulated training environment. Do not use against systems you are not authorized to test.') +
      '</p></div>';
    document.body.appendChild(f);
  }

  /* ---------- 4. 언어 동기화 ---------- */
  function syncLang() {
    var en = isEn();
    document.documentElement.lang = en ? 'en' : 'ko';
    var skip = document.querySelector('.wvs-skip');
    if (skip) skip.textContent = L('본문 바로가기', 'Skip to content');
    var f = document.getElementById('wvs-footer');
    if (f) { f.remove(); addFooter(); }
    var n = document.getElementById('wvs-pager');
    if (n) { n.remove(); addPager(); }
  }

  /* ---------- 5. 이전/다음 이동 ---------- */
  /* 기둥 이름을 하나하나 적으면 기둥이 늘 때마다 낡는다. 실제로 14_auto(61),
     15_privacy(34), 16_zt(8) 이 빠져 103개 페이지에서 이전-다음이 뜨지 않았다.
     번호 접두사 규칙으로 바꿔 새 기둥이 자동으로 포함되게 한다.
     최종 판정은 renderPager 의 indexOf 가 하므로, 여기서는 카탈로그를
     불러올 가치가 있는 페이지인지만 거른다. */
  var ORDER_PREFIX = /^(\d{2}_|ai-hub\.html|ai-guardrail-lab\.html)/;
  function addPager() {
    if (isBare || !ORDER_PREFIX.test(page)) return;
    if (window.WVS_PAGE_ORDER) return renderPager(window.WVS_PAGE_ORDER);
    // 카탈로그는 학습 페이지에서만 필요하므로 그때 한 번만 불러온다.
    fetch('/js/page-order.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (list) { if (list) { window.WVS_PAGE_ORDER = list; renderPager(list); } })
      .catch(function () { /* 이전-다음은 보조 기능이라 실패해도 본문에 영향 없음 */ });
  }
  function renderPager(list) {
    if (document.getElementById('wvs-pager')) return;
    var i = list.indexOf(page);
    if (i < 0) return;
    var prev = i > 0 ? list[i - 1] : null;
    var next = i < list.length - 1 ? list[i + 1] : null;
    var nav = document.createElement('nav');
    nav.id = 'wvs-pager';
    nav.setAttribute('aria-label', L('학습 순서 이동', 'Lesson navigation'));
    nav.innerHTML =
      (prev ? '<a class="wvs-pg prev" href="' + prev + '"><span aria-hidden="true">←</span> ' + L('이전', 'Previous') + '</a>' : '<span class="wvs-pg off"></span>') +
      '<span class="wvs-pg pos">' + (i + 1) + ' / ' + list.length + '</span>' +
      (next ? '<a class="wvs-pg next" href="' + next + '">' + L('다음', 'Next') + ' <span aria-hidden="true">→</span></a>' : '<span class="wvs-pg off"></span>');
    var main = document.querySelector('main, [role="main"], #' + SKIP_ID);
    (main && main.parentNode ? main.parentNode : document.body).insertBefore(nav, main ? main.nextSibling : null);
  }

  /* ---------- 6. 장식 아이콘 숨김 ---------- */
  function hideDecorativeIcons() {
    // 아이콘 폰트는 보조기술에서 의미 없는 문자로 읽힌다.
    document.querySelectorAll('i.fa, i.fas, i.far, i.fab, i[class^="fa-"], i[class*=" fa-"], .icon:empty')
      .forEach(function (el) {
        if (!el.hasAttribute('aria-label') && !el.hasAttribute('aria-hidden') && !(el.textContent || '').trim()) {
          el.setAttribute('aria-hidden', 'true');
        }
      });
  }

  /* ---------- 0. 비차단으로 내려받은 웹폰트 적용 ---------- */
  function applyDeferredFonts() {
    // [QA I-02] 폰트 링크는 media="print" 로 내려받아 렌더링과 부팅을 막지 않게 해 두었다.
    // DOM 이 준비된 뒤 화면에 적용한다.
    document.querySelectorAll('link[data-wvs-font="1"]').forEach(function (l) { l.media = 'all'; });
  }

  function boot() {
    try { applyDeferredFonts(); } catch (e) {}
    try { markMain(); } catch (e) {}
    try { markNav(); } catch (e) {}
    try { addFooter(); } catch (e) {}
    try { addPager(); } catch (e) {}
    try { hideDecorativeIcons(); } catch (e) {}
    try { document.documentElement.lang = isEn() ? 'en' : 'ko'; } catch (e) {}

    // skip link 로 이동했을 때 실제로 포커스가 본문으로 가도록 한다.
    var skip = document.querySelector('.wvs-skip');
    if (skip) skip.addEventListener('click', function () {
      var m = document.querySelector('#' + (skip.getAttribute('href')||'#'+SKIP_ID).slice(1));
      if (m) setTimeout(function () { m.focus(); }, 0);
    });

    // 다른 탭에서 언어를 바꾼 경우도 따라간다.
    window.addEventListener('storage', function (e) {
      if (e.key === 'wvs_lang' || e.key === 'lang') syncLang();
    });
    // 같은 탭의 언어 전환 버튼을 감지한다.
    document.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target.closest('.langbtn, .langtoggle button, [data-lang]') : null;
      if (t) setTimeout(syncLang, 0);
    }, true);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
