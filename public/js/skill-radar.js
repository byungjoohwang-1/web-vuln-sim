/* WEB-VULN-SIM — 스킬 레이더(SVG) 공용 렌더러 · F4
 * 사용: skill-assess.html(평가 결과), my-progress.html(임베드)
 * window.WVSRadar.svg(opts)  -> SVG 문자열
 * window.WVSRadar.mount(el, opts) -> 렌더(등장 애니메이션 포함, reduced-motion 준수)
 * opts: { axes:[{label, val(0-100), ref?(0-100)}], size, color }
 */
(function () {
  'use strict';
  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; });
  }
  function pt(cx, cy, r, val, ang) {
    var v = Math.max(0, Math.min(100, val)) / 100 * r;
    return [cx + v * Math.cos(ang), cy + v * Math.sin(ang)];
  }
  function svg(o) {
    o = o || {};
    var size = o.size || 340, pad = o.pad || 52, cx = size / 2, cy = size / 2, r = size / 2 - pad;
    var color = o.color || '#38bdf8';
    var axes = o.axes || []; var n = axes.length || 1;
    var angs = []; for (var i = 0; i < n; i++) angs.push(-Math.PI / 2 + i * 2 * Math.PI / n);

    var s = '<svg viewBox="0 0 ' + size + ' ' + size + '" role="img" aria-label="skill radar" style="max-width:100%;height:auto;display:block;margin:0 auto">';
    // 눈금 링(20~100)
    [20, 40, 60, 80, 100].forEach(function (rv) {
      var pts = angs.map(function (a) { var p = pt(cx, cy, r, rv, a); return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
      s += '<polygon points="' + pts + '" fill="none" stroke="#1e293b" stroke-width="' + (rv === 100 ? 1.5 : 1) + '"' +
        (rv === 100 ? '' : ' stroke-dasharray="3 4"') + '/>';
    });
    // 축선 + 라벨
    axes.forEach(function (ax, i) {
      var p = pt(cx, cy, r, 100, angs[i]);
      s += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p[0].toFixed(1) + '" y2="' + p[1].toFixed(1) + '" stroke="#334155" stroke-width="1"/>';
      var lp = pt(cx, cy, r, 126, angs[i]);
      var c = Math.cos(angs[i]);
      var anchor = Math.abs(c) < .3 ? 'middle' : (c > 0 ? 'start' : 'end');
      var dy = Math.sin(angs[i]) < -.5 ? -1 : (Math.abs(c) < .3 ? 4 : 10);
      s += '<text x="' + lp[0].toFixed(1) + '" y="' + lp[1].toFixed(1) + '" dy="' + dy + '" text-anchor="' + anchor +
        '" font-size="10.5" fill="#94a3b8" font-family="Segoe UI,Malgun Gothic,sans-serif">' + esc(ax.label) + '</text>';
    });
    // 참조 프로파일(점선)
    var hasRef = axes.some(function (a) { return typeof a.ref === 'number'; });
    if (hasRef) {
      var rp = axes.map(function (ax, i) { var p = pt(cx, cy, r, ax.ref || 0, angs[i]); return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
      s += '<polygon points="' + rp + '" fill="none" stroke="#64748b" stroke-width="1.2" stroke-dasharray="4 4" opacity=".85"/>';
    }
    // 내 값 폴리곤(등장 스케일 애니메이션) + 꼭짓점
    var vp = axes.map(function (ax, i) { var p = pt(cx, cy, r, ax.val || 0, angs[i]); return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ');
    s += '<polygon class="wvs-radar-main" points="' + vp + '" fill="' + color + '" fill-opacity=".22" stroke="' + color +
      '" stroke-width="2" stroke-linejoin="round" style="transform-origin:' + cx + 'px ' + cy + 'px;transform:scale(.6);opacity:.6;transition:transform .9s cubic-bezier(.2,.8,.2,1),opacity .9s ease"/>';
    axes.forEach(function (ax, i) {
      var p = pt(cx, cy, r, ax.val || 0, angs[i]);
      s += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3.2" fill="' + color + '" stroke="#0b1220" stroke-width="1.2"/>';
    });
    s += '</svg>';
    return s;
  }
  function mount(el, o) {
    if (typeof el === 'string') el = document.querySelector(el);
    if (!el) return;
    el.innerHTML = svg(o);
    var poly = el.querySelector('.wvs-radar-main');
    if (!poly) return;
    var reduce = false;
    try { reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
    if (reduce) { poly.style.transition = 'none'; poly.style.transform = 'scale(1)'; poly.style.opacity = '1'; return; }
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { poly.style.transform = 'scale(1)'; poly.style.opacity = '1'; });
    });
  }
  window.WVSRadar = { svg: svg, mount: mount };
})();
