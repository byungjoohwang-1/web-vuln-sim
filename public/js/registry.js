/* registry.js - 콘텐츠 레지스트리 클라이언트 (QA W-06, W-03)
 *
 * 화면에 보이는 콘텐츠 수치를 data/content-registry.json 한 곳에서 읽는다.
 * HTML 에 손으로 적은 숫자를 두지 않기 위한 장치다.
 *
 * 사용법
 *   <span data-wvs-count="totals.interactiveTotal">367</span>
 *   <span data-wvs-count="domains.linux.count">41</span>
 *   <span data-wvs-coverage="linux"></span>          커버리지 배지
 *   <div  data-wvs-missing="linux"></div>            미수록 번호 목록
 *
 * HTML 안의 값은 스크립트가 실패했을 때 보일 대비값이다.
 * 생성기(_gen/gen_registry.py)가 레지스트리를 만들고,
 * _gen/validate_build.py 가 대비값과 레지스트리가 어긋나면 배포를 막는다.
 */
(function () {
  'use strict';

  var URL = '/data/content-registry.json';

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }
  var cached = null;
  var waiting = null;

  function load() {
    if (cached) return Promise.resolve(cached);
    if (waiting) return waiting;
    waiting = fetch(URL, { cache: 'no-cache' })
      .then(function (r) {
        if (!r.ok) throw new Error('registry ' + r.status);
        return r.json();
      })
      .then(function (j) {
        cached = j;
        return j;
      });
    return waiting;
  }

  /* "domains.linux.count" 처럼 점으로 구분된 경로를 읽는다.
     domains 는 배열이므로 id 로 찾을 수 있게 한 단계 풀어 준다. */
  function pick(reg, path) {
    var parts = String(path).split('.');
    var cur = reg;
    for (var i = 0; i < parts.length; i++) {
      var key = parts[i];
      if (cur === null || cur === undefined) return undefined;
      if (Array.isArray(cur)) {
        var hit = null;
        for (var j = 0; j < cur.length; j++) {
          if (cur[j] && cur[j].id === key) { hit = cur[j]; break; }
        }
        cur = hit;
      } else {
        cur = cur[key];
      }
    }
    return cur;
  }

  function comma(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  function domain(reg, id) {
    var list = reg.domains || [];
    for (var i = 0; i < list.length; i++) {
      if (list[i].id === id) return list[i];
    }
    return null;
  }

  function pad(n) { return n < 10 ? '0' + n : String(n); }

  /* [7,8,9,11] -> "U-07 ~ U-13, U-29" 처럼 항목 번호 그대로 읽히게 만든다. */
  function ranges(nums, prefix) {
    if (!nums || !nums.length) return '';
    var p = prefix ? prefix + '-' : '';
    var out = [], start = nums[0], prev = nums[0];
    for (var i = 1; i <= nums.length; i++) {
      var n = nums[i];
      if (n === prev + 1) { prev = n; continue; }
      out.push(start === prev ? (p + pad(start)) : (p + pad(start) + ' ~ ' + p + pad(prev)));
      start = prev = n;
    }
    return out.join(', ');
  }

  var filling = false;

  function fill(reg) {
    if (filling) return;
    filling = true;
    try { fillInner(reg); } finally { setTimeout(function(){ filling = false; }, 0); }
  }

  function fillInner(reg) {
    var nodes = document.querySelectorAll('[data-wvs-count]');
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var v = pick(reg, el.getAttribute('data-wvs-count'));
      if (typeof v !== 'number') continue;
      el.textContent = el.getAttribute('data-wvs-count-format') === 'plain'
        ? String(v) : comma(v);
    }

    var covs = document.querySelectorAll('[data-wvs-coverage]');
    for (var k = 0; k < covs.length; k++) {
      var ce = covs[k];
      var d = domain(reg, ce.getAttribute('data-wvs-coverage'));
      if (!d || !d.numbering) continue;
      var nb = d.numbering;
      ce.textContent = nb.coveredCount + '/' + nb.plannedCount
        + L(' 수록 (', ' covered (') + nb.coveragePercent + '%)';
      ce.setAttribute('title',
        L(nb.itemPrefix + '-' + pad(nb.plannedFrom) + ' 부터 '
          + nb.itemPrefix + '-' + pad(nb.plannedTo) + ' 중 실제 수록된 항목 수',
          'Items actually published between ' + nb.itemPrefix + '-' + pad(nb.plannedFrom)
          + ' and ' + nb.itemPrefix + '-' + pad(nb.plannedTo)));
      if (nb.coveragePercent >= 100) ce.setAttribute('data-full', '1');
    }

    var miss = document.querySelectorAll('[data-wvs-missing]');
    for (var m = 0; m < miss.length; m++) {
      var me = miss[m];
      var md = domain(reg, me.getAttribute('data-wvs-missing'));
      if (!md || !md.numbering) continue;
      var list = md.numbering.missing || [];
      if (!list.length) { me.textContent = ''; me.hidden = true; continue; }
      me.hidden = false;
      me.textContent = L('미수록 항목 ' + list.length + '개: '
          + ranges(list, md.numbering.itemPrefix) + ' (준비 중)',
        'Not yet published, ' + list.length + ' items: '
          + ranges(list, md.numbering.itemPrefix) + ' (in preparation)');
    }
  }

  var SEL = '[data-wvs-count],[data-wvs-coverage],[data-wvs-missing]';

  function refresh() {
    if (!document.querySelector(SEL)) return;
    load().then(fill).catch(function () {
      /* 레지스트리를 못 읽으면 HTML 의 대비값을 그대로 둔다. */
    });
  }

  /* 언어 전환기(applyLang)가 innerHTML 을 다시 쓰면 채워 넣은 수치가 지워진다.
     페이지마다 전환기 구현이 달라서, 관련 노드가 바뀌면 다시 채우는 쪽을 택했다.
     레지스트리 표기가 있는 페이지에서만 관찰자를 붙인다. */
  function watch() {
    if (!window.MutationObserver || !document.body) return;
    var timer = null;
    var obs = new MutationObserver(function () {
      if (timer) return;
      timer = setTimeout(function () {
        timer = null;
        if (cached) fill(cached);
      }, 60);
    });
    obs.observe(document.body, { childList: true, subtree: true });
  }

  function run() {
    if (!document.querySelector(SEL)) return;
    refresh();
    watch();
  }

  window.wvsRegistry = {
    load: load, refresh: refresh, pick: pick, domain: domain, ranges: ranges
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
