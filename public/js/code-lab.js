/* code-lab.js — 보안약점 '현업 진단' 실습 엔진
 *
 * 왜 만들었나:
 *   기존 03_code_* 페이지는 코드 에디터에 안전한 코드를 써 넣으면 통과하는 구조였다.
 *   현업의 진단은 그렇게 시작하지 않는다. 티켓이 먼저 오고, 로그를 뒤지고, 정탐인지
 *   오탐인지 판정한 다음, 조치가 실제로 막는지 재현해서 확인한다.
 *   이 엔진은 그 네 단계를 그대로 재현한다.
 *
 * 설계 원칙 (07_fincloud 판정 가드와 동일한 취지):
 *   - 증거를 보지 않고 내린 판정은 받지 않는다. 진단 보고서의 근거가 되지 못하기 때문이다.
 *   - 정답이 항상 '취약(정탐)'이 아니다. 실제 스캐너 리포트에는 오탐이 섞여 있고,
 *     그것을 걸러내는 것이 진단원의 핵심 역량이다.
 *   - 조치 선택지에는 '흔히들 하는 불완전한 조치'가 들어 있다. 고르면 왜 여전히 뚫리는지 보여준다.
 *   - 모든 출력은 mock 이다. 네트워크 호출도, 실제 실행도 없다.
 */
(function () {
  'use strict';

  var ROOT_SEL = '#wvs-code-lab';
  var DATA_URL = '/data/code-lab.json';
  var MIN_EVIDENCE = 2; // 판정 전에 최소한 열어봐야 하는 증거 수

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /* 로그 한 줄에 색을 입힌다. 형식은 건드리지 않고 분류만 한다. */
  function lineClass(line) {
    if (/^\s*[#$]|^\s*\$ /.test(line)) return 'cl-cmd';
    if (/\b(ERROR|FATAL|SEVERE|Exception|CRITICAL|DENIED|FAIL)\b/.test(line)) return 'cl-err';
    if (/\b(WARN|WARNING|BLOCKED|ALERT)\b/.test(line)) return 'cl-warn';
    if (/\b(INFO|OK|PASS|ALLOW|200)\b/.test(line)) return 'cl-ok';
    return '';
  }

  function renderLog(text) {
    return String(text).split('\n').map(function (l) {
      var c = lineClass(l);
      return c ? '<span class="' + c + '">' + esc(l) + '</span>' : esc(l);
    }).join('\n');
  }

  function el(tag, cls, html) {
    var d = document.createElement(tag);
    if (cls) d.className = cls;
    if (html != null) d.innerHTML = html;
    return d;
  }

  /* ---------------- 단계 렌더 ---------------- */

  function Lab(root, key, d) {
    this.root = root;
    this.key = key;
    this.d = d;
    this.opened = {};      // 열어 본 증거
    this.verdictDone = false;
    this.fixDone = false;
    this.render();
  }

  Lab.prototype.render = function () {
    var d = this.d;
    var self = this;
    this.root.innerHTML = '';

    var head = el('div', 'cl-head',
      '<h2>🏢 현업 진단 실습 — 티켓에서 조치까지</h2>' +
      '<p class="cl-sub">' + esc(d.intro || '실제 진단은 “이 약점을 고치세요”로 시작하지 않습니다. 티켓을 받고, 증거를 모으고, 정탐인지 판정한 뒤, 조치가 실제로 막는지 확인합니다.') + '</p>');
    this.root.appendChild(head);

    /* 진행 표시 */
    this.steps = el('ol', 'cl-steps',
      ['접수', '증거 수집', '판정', '조치·회귀'].map(function (s, i) {
        return '<li data-step="' + (i + 1) + '"><b>' + (i + 1) + '</b> ' + s + '</li>';
      }).join(''));
    this.root.appendChild(this.steps);

    this.root.appendChild(this.ticketBlock());
    this.root.appendChild(this.evidenceBlock());
    this.root.appendChild(this.verdictBlock());
    this.root.appendChild(this.fixBlock());

    this.mark(1);
    void self;
  };

  Lab.prototype.mark = function (n) {
    var lis = this.steps.querySelectorAll('li');
    for (var i = 0; i < lis.length; i++) {
      lis[i].classList.toggle('on', (i + 1) <= n);
    }
  };

  /* 1. 접수 */
  Lab.prototype.ticketBlock = function () {
    var t = this.d.ticket || {};
    var box = el('section', 'cl-sec cl-ticket');
    box.innerHTML =
      '<h3><span class="cl-n">1</span> 📨 접수 — 이렇게 들어옵니다</h3>' +
      '<div class="cl-card">' +
        '<div class="cl-tmeta">' +
          '<span class="cl-src">' + esc(t.source || '—') + '</span>' +
          (t.id ? '<span class="cl-id">' + esc(t.id) + '</span>' : '') +
          (t.severity ? '<span class="cl-sev cl-sev-' + esc(t.sevLevel || 'mid') + '">' + esc(t.severity) + '</span>' : '') +
        '</div>' +
        '<div class="cl-tbody">' + esc(t.body || '') + '</div>' +
        (t.note ? '<div class="cl-tnote">' + esc(t.note) + '</div>' : '') +
      '</div>';
    return box;
  };

  /* 2. 증거 수집 */
  Lab.prototype.evidenceBlock = function () {
    var self = this;
    var list = this.d.evidence || [];
    var box = el('section', 'cl-sec');
    box.innerHTML =
      '<h3><span class="cl-n">2</span> 🔎 증거 수집 — 무엇을 봐야 판정할 수 있나</h3>' +
      '<p class="cl-hint">아래 자료를 열어 보세요. <b>최소 ' + MIN_EVIDENCE + '개</b>를 확인해야 판정 단계가 열립니다.</p>';

    var grid = el('div', 'cl-evgrid');
    list.forEach(function (ev, i) {
      var btn = el('button', 'cl-evbtn');
      btn.type = 'button';
      btn.setAttribute('aria-expanded', 'false');
      btn.innerHTML = '<span class="cl-evic">' + esc(ev.icon || '📄') + '</span>' +
                      '<span class="cl-evt">' + esc(ev.label) + '</span>' +
                      '<span class="cl-evsrc">' + esc(ev.source || '') + '</span>';
      var pane = el('pre', 'cl-evout');
      pane.hidden = true;
      pane.innerHTML = renderLog(ev.output || '');

      btn.addEventListener('click', function () {
        var open = !pane.hidden;
        pane.hidden = open;
        btn.setAttribute('aria-expanded', String(!open));
        btn.classList.toggle('open', !open);
        if (!open) {
          self.opened[i] = true;
          self.refreshGate();
        }
      });
      grid.appendChild(btn);
      grid.appendChild(pane);
    });
    box.appendChild(grid);
    return box;
  };

  Lab.prototype.openedCount = function () {
    return Object.keys(this.opened).length;
  };

  Lab.prototype.refreshGate = function () {
    var n = this.openedCount();
    if (this.gateMsg) {
      this.gateMsg.textContent = n >= MIN_EVIDENCE
        ? '증거 ' + n + '건 확인 — 판정할 수 있습니다.'
        : '증거 ' + n + '/' + MIN_EVIDENCE + '건. 더 확인한 뒤 판정하세요.';
      this.gateMsg.classList.toggle('ready', n >= MIN_EVIDENCE);
    }
    if (n >= MIN_EVIDENCE) this.mark(2);
  };

  /* 3. 판정 */
  Lab.prototype.verdictBlock = function () {
    var self = this;
    var v = this.d.verdict || {};
    var box = el('section', 'cl-sec');
    box.innerHTML =
      '<h3><span class="cl-n">3</span> ⚖️ 판정 — 정탐입니까, 오탐입니까</h3>' +
      '<p class="cl-hint">스캐너가 올린 것이 전부 진짜 취약점은 아닙니다. 방금 본 증거만으로 판단하세요.</p>';

    this.gateMsg = el('div', 'cl-gate', '증거 0/' + MIN_EVIDENCE + '건. 더 확인한 뒤 판정하세요.');
    box.appendChild(this.gateMsg);

    var opts = [
      { k: 'true', t: '정탐 — 실제 취약점이다', d: '악용 가능하며 조치가 필요하다' },
      { k: 'false', t: '오탐 — 취약하지 않다', d: '이미 통제가 있거나 도달 불가능한 코드다' },
      { k: 'more', t: '추가 확인 필요', d: '증거만으로는 악용 가능성을 단정할 수 없다' }
    ];
    var wrap = el('div', 'cl-vopts');
    opts.forEach(function (o) {
      var b = el('button', 'cl-vbtn');
      b.type = 'button';
      b.dataset.k = o.k;
      b.innerHTML = '<b>' + esc(o.t) + '</b><small>' + esc(o.d) + '</small>';
      b.addEventListener('click', function () { self.judge(o.k, b); });
      wrap.appendChild(b);
    });
    box.appendChild(wrap);

    this.vfb = el('div', 'cl-fb');
    this.vfb.setAttribute('role', 'status');
    this.vfb.setAttribute('aria-live', 'polite');
    box.appendChild(this.vfb);
    void v;
    return box;
  };

  Lab.prototype.judge = function (choice, btn) {
    var v = this.d.verdict || {};
    if (this.openedCount() < MIN_EVIDENCE) {
      this.vfb.className = 'cl-fb show wrong';
      this.vfb.innerHTML = '<b>먼저 증거를 확인하세요.</b>' +
        '출력을 보지 않고 내린 판정은 진단 보고서의 근거가 되지 못합니다. ' +
        '현업에서 오탐을 정탐으로 올리면 개발팀의 신뢰를 잃고, 정탐을 오탐으로 닫으면 사고가 됩니다.';
      return;
    }
    var all = this.root.querySelectorAll('.cl-vbtn');
    for (var i = 0; i < all.length; i++) all[i].classList.remove('sel');
    btn.classList.add('sel');

    var ok = (choice === v.answer);
    this.vfb.className = 'cl-fb show ' + (ok ? 'right' : 'wrong');
    this.vfb.innerHTML =
      '<b>' + (ok ? '✅ 맞습니다' : '❌ 다시 보세요') + ' — 정답: ' + esc(labelOf(v.answer)) + '</b>' +
      esc(v.why || '') +
      (v.trap ? '<span class="cl-trap">⚠️ 자주 틀리는 지점 — ' + esc(v.trap) + '</span>' : '');
    this.verdictDone = true;
    this.verdictCorrect = ok;   // 완료 판정은 '맞게' 판정했을 때만 인정한다
    this.mark(3);
  };

  function labelOf(k) {
    return k === 'true' ? '정탐' : k === 'false' ? '오탐' : '추가 확인 필요';
  }

  /* 4. 조치·회귀 */
  Lab.prototype.fixBlock = function () {
    var self = this;
    var f = this.d.fix || {};
    var box = el('section', 'cl-sec');
    box.innerHTML =
      '<h3><span class="cl-n">4</span> 🛠️ 조치와 회귀 확인 — 정말 막혔습니까</h3>' +
      '<p class="cl-hint">조치안을 고르면 같은 공격을 다시 돌려 결과를 보여줍니다. 실무에서 가장 흔한 실패는 “고쳤다고 믿는 것”입니다.</p>';

    var wrap = el('div', 'cl-fixopts');
    (f.options || []).forEach(function (o, i) {
      var b = el('button', 'cl-fixbtn');
      b.type = 'button';
      b.innerHTML = '<span class="cl-fixk">' + String.fromCharCode(65 + i) + '</span>' + esc(o.label);
      b.addEventListener('click', function () { self.tryFix(o, b); });
      wrap.appendChild(b);
    });
    box.appendChild(wrap);

    this.ffb = el('div', 'cl-fb');
    this.ffb.setAttribute('role', 'status');
    this.ffb.setAttribute('aria-live', 'polite');
    box.appendChild(this.ffb);
    return box;
  };

  Lab.prototype.tryFix = function (o, btn) {
    var all = this.root.querySelectorAll('.cl-fixbtn');
    for (var i = 0; i < all.length; i++) all[i].classList.remove('sel');
    btn.classList.add('sel');

    var done = o.ok && this.verdictCorrect;
    this.ffb.className = 'cl-fb show ' + (o.ok ? 'right' : 'wrong');
    this.ffb.innerHTML =
      '<b>' + (o.ok ? '✅ 차단됨' : '❌ 여전히 통합니다') + '</b>' +
      '<pre class="cl-retest">' + renderLog(o.retest || '') + '</pre>' +
      esc(o.why || '') +
      (done ? '<span class="cl-done">🎓 4단계를 모두 마쳤습니다 — 이 항목이 완료로 기록됐습니다.</span>'
            : (o.ok && this.verdictDone
                ? '<span class="cl-trap">판정을 다시 맞혀야 완료로 기록됩니다. 3단계로 돌아가 보세요.</span>'
                : ''));
    if (o.ok) {
      this.fixDone = true;
      this.mark(4);
      this.complete();
    }
  };

  /* 진도 기록 — 엔진 API 경유(직접 localStorage 를 쓰지 않는다)
   *
   * markVisited 를 부르면 안 된다. progress.js 가 이미 4초 체류만으로 방문을 기록하므로,
   * 4단계를 다 끝낸 학습자와 페이지를 열어만 둔 학습자가 똑같이 취급된다.
   * 이 50개 페이지에는 원래 완료를 기록하는 경로가 아예 없었다(코드 에디터 채점은
   * 진도 엔진과 연결돼 있지 않다). 이 실습이 그 유일한 완료 조건이 된다.
   *
   * 인정 기준: 판정을 맞게 하고(verdictCorrect) + 올바른 조치를 고른 경우만.
   * 찍어서 통과하는 것을 막기 위해 둘 다 요구한다.
   */
  Lab.prototype.complete = function () {
    if (!this.verdictCorrect) return;
    try {
      if (window.WVSProgress && typeof window.WVSProgress.complete === 'function') {
        window.WVSProgress.complete(undefined, this.pageId());
      }
    } catch (e) { /* 진도 기록 실패가 실습을 막지 않는다 */ }
  };

  Lab.prototype.pageId = function () {
    return (location.pathname || '').split('/').pop() || undefined;
  };

  /* ---------------- 부팅 ---------------- */

  function boot() {
    var root = document.querySelector(ROOT_SEL);
    if (!root) return;
    var key = root.getAttribute('data-lab-key');
    if (!key) return;

    fetch(DATA_URL, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (all) {
        var d = all && all[key];
        if (!d) { root.hidden = true; return; }
        new Lab(root, key, d);
      })
      .catch(function () { root.hidden = true; });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
