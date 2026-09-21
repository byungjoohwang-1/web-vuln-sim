# -*- coding: utf-8 -*-
"""17_fw-*.html 펌웨어·IoT 임베디드 진단 실습 생성기.

배포 펌웨어 이미지를 binwalk 로 열고, 추출된 rootfs 의 설정·바이너리·키를 읽어 판정하는
실습으로 만든다. 기기·시나리오·설정 내용·해설은 전부 교육용으로 새로 작성한다(가상 브랜드).

사용: python _gen/gen_fw_lab.py
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT = os.path.join(os.path.dirname(__file__), '..', 'public')

PAGE = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta name="theme-color" content="#0b1220"><link rel="manifest" href="/manifest.json"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="/js/pwa.js" defer></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>펌웨어·IoT 진단 실습: {title} · WEB-VULN-SIM</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="WEB-VULN-SIM 보안 학습 포털">
<meta property="og:title" content="펌웨어·IoT 진단 실습: {title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://vuln-sim.web.app/{file}">
<meta property="og:image" content="https://vuln-sim.web.app/favicon.svg">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="/css/platform-tokens.css">
<style>
:root{{--bg:#0b1220;--panel:#111a2e;--panel2:#0f172a;--border:#1e293b;--ink:#e2e8f0;--muted:#94a3b8;
 --accent:#38bdf8;--good:#22c55e;--bad:#ef4444;--warn:#f59e0b;--mono:'JetBrains Mono','Consolas',monospace;}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI','Malgun Gothic',sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}}
a{{color:#7dd3fc;text-decoration:none}}
.topbar{{display:flex;align-items:center;gap:14px;background:#0b1220;border-bottom:1px solid var(--border);padding:10px 16px;position:sticky;top:0;z-index:50;flex-wrap:wrap}}
.topbar a{{font-size:13px;font-family:var(--mono)}}
.topbar .sp{{margin-left:auto}}
.wrap{{max-width:1400px;margin:0 auto;padding:18px 16px 90px}}
.hero h1{{font-size:21px;color:#fff;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.hero p{{font-size:13.5px;color:var(--muted);margin-top:6px;max-width:900px}}
.badge{{font-family:var(--mono);font-size:11.5px;font-weight:800;color:#0b1220;background:#5eead4;border-radius:6px;padding:2px 9px}}
.hostbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--panel2);border:1px solid var(--border);
 border-radius:10px;padding:9px 13px;margin:14px 0;font-family:var(--mono);font-size:12.5px;color:#cbd5e1}}
.hostbar b{{color:#7dd3fc}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}}
@media(max-width:1000px){{.cols{{grid-template-columns:1fr}}}}
@media(max-width:640px){{
  .wrap,.cols,.cols>*,.card,.term{{min-width:0}}
  .term,.term pre,.card pre{{max-width:100%;overflow-x:auto}}
  .card h2{{flex-wrap:wrap;word-break:keep-all}}
}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:15px 17px;margin-bottom:14px}}
.card h2{{font-size:14px;color:#7dd3fc;font-family:var(--mono);margin-bottom:10px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.term{{background:#05080f;border:1px solid var(--border);border-radius:10px;font-family:var(--mono);font-size:12.5px}}
.term .out{{padding:12px;height:340px;overflow:auto;white-space:pre-wrap;word-break:break-word;color:#cbd5e1}}
.term .out .cmd{{color:#7dd3fc}}
.term .out .err{{color:#fca5a5}}
.term .inp{{display:flex;align-items:center;gap:8px;border-top:1px solid var(--border);padding:9px 11px}}
.term .inp span{{color:#4ade80}}
.term .inp input{{flex:1;background:transparent;border:0;outline:0;color:#e2e8f0;font-family:var(--mono);font-size:12.5px;min-width:0}}
.quick{{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}}
.quick button{{cursor:pointer;background:#0e1626;border:1px solid #26334d;color:#9fb0ca;border-radius:7px;
 padding:5px 10px;font-size:11.5px;font-family:var(--mono);min-height:30px}}
.quick button:hover{{border-color:#38bdf8;color:#7dd3fc}}
.mlist{{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}}
.mchip{{cursor:pointer;border:1px solid #26334d;background:#0e1626;color:#9fb0ca;border-radius:999px;
 padding:5px 11px;font-size:11.5px;font-family:var(--mono);min-height:30px}}
.mchip.on{{background:#0c2a3a;border-color:#38bdf8;color:#7dd3fc;font-weight:800}}
.mchip.done{{border-color:#14532d;color:#86efac}}
.mchip.wrong{{border-color:#7f1d1d;color:#fca5a5}}
.brief{{background:#090f1d;border:1px solid #1e293b;border-radius:10px;padding:12px 14px;font-size:13px;line-height:1.7}}
.brief .rk{{font-family:var(--mono);font-size:11px;font-weight:800;border-radius:5px;padding:2px 7px;margin-right:7px}}
.r5{{background:#3b1418;color:#fca5a5}}.r4{{background:#3a2409;color:#fdba74}}.r3{{background:#3a3409;color:#fde047}}
.r2{{background:#0c2a3a;color:#7dd3fc}}.r1{{background:#1e293b;color:#94a3b8}}
label.fl{{display:block;font-size:12px;color:var(--muted);margin:12px 0 5px;font-family:var(--mono)}}
select,.ans{{width:100%;background:var(--panel2);border:1px solid #334155;color:var(--ink);border-radius:8px;
 padding:9px 11px;font-size:13px;font-family:inherit;min-height:42px}}
.acts{{display:flex;gap:9px;flex-wrap:wrap;margin-top:13px}}
button.act{{cursor:pointer;border:0;border-radius:9px;padding:10px 17px;font-weight:800;font-size:13px;font-family:var(--mono);min-height:42px}}
button.judge{{background:var(--accent);color:#04222e}}
button.fix{{background:var(--good);color:#06210f}}
button.ghost{{background:#1e293b;color:#cbd5e1;border:1px solid #334155}}
button:disabled{{opacity:.45;cursor:not-allowed}}
.res{{margin-top:13px;padding:13px 15px;border-radius:10px;font-size:13px;display:none;line-height:1.7}}
.res.ok{{background:#082819;border:1px solid #15803d;color:#bbf7d0}}
.res.no{{background:#351319;border:1px solid #b91c1c;color:#fecaca}}
.res h3{{font-size:14px;margin-bottom:6px}}
.res code{{background:#0b1220;border:1px solid #334155;border-radius:4px;padding:1px 6px;font-family:var(--mono);font-size:12px}}
.prog{{display:flex;align-items:center;gap:11px;margin:10px 0 0;font-size:12.5px;color:var(--muted);font-family:var(--mono)}}
.prog .bar{{flex:1;height:8px;background:#1e293b;border-radius:99px;overflow:hidden;min-width:120px}}
.prog .bar>i{{display:block;height:100%;background:var(--good);width:0}}
.disc{{margin-top:20px;font-size:12px;color:#64748b;border-top:1px dashed #334155;padding-top:10px}}
/* 가이드 사건 브리핑 */
.brief-inc{{background:#0e1a10;border:1px solid #1f5132;border-radius:12px;padding:13px 15px;margin:14px 0}}
.brief-inc h2{{font-size:14px;color:#86efac;font-family:var(--mono);margin-bottom:6px;display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}}
.brief-inc p{{font-size:13px;color:#cbd5e1;line-height:1.7}}
.stages{{display:flex;flex-direction:column;gap:7px;margin-top:11px}}
.stage b{{color:#7dd3fc;font-family:var(--mono);font-size:12.5px}}
.stage .ids{{display:inline-flex;gap:5px;flex-wrap:wrap;margin-left:6px}}
.stage .ids button{{cursor:pointer;background:#0e1626;border:1px solid #26334d;color:#9fb0ca;border-radius:6px;padding:2px 8px;font-size:11px;font-family:var(--mono);min-height:26px}}
.stage .ids button:hover{{border-color:#38bdf8;color:#7dd3fc}}
/* AI 코치 */
.coach{{margin-top:14px;border-top:1px dashed #334155;padding-top:12px}}
.coach h3{{font-size:13px;color:#a78bfa;font-family:var(--mono);margin-bottom:8px;display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}}
.coach .cbtns{{display:flex;gap:8px;flex-wrap:wrap}}
.coach button{{cursor:pointer;border-radius:8px;padding:8px 13px;font-size:12.5px;font-family:var(--mono);min-height:38px;border:0}}
.coach .cask{{background:#6d28d9;color:#ede9fe}}
.coach .cprev{{background:#1e293b;color:#cbd5e1;border:1px solid #334155}}
.coach .cout{{margin-top:10px;font-size:12.5px;line-height:1.7;color:#cbd5e1;white-space:pre-wrap;display:none}}
.coach .cout.on{{display:block}}
.coach .cout .lab{{color:#a78bfa;font-weight:800}}
.coach .cout pre{{background:#05080f;border:1px solid #334155;border-radius:8px;padding:10px;overflow:auto;font-size:11.5px;color:#9fb0ca;white-space:pre-wrap;word-break:break-word}}
</style>
<script src="/js/fw-lab.js"></script>
<script src="/js/{data}"></script>
<script src="/js/progress.js" defer></script>
<script src="/js/soc-chrome.js" data-topbar="off" defer></script>
<script src="/js/shell.js" defer></script>
</head>
<body>
<a class="wvs-skip" href="#wvs-main">본문 바로가기</a>
<div class="topbar">
  <a href="index.html">🏠 홈</a>
  <a href="vuln-hub.html">취약점 실습장</a>
  <a href="14_auto-auto01.html">자동차 보안</a>
  <a href="my-progress.html">내 학습 현황</a>
  <span class="sp"></span>
  <span style="font-size:12px;color:#94a3b8;font-family:var(--mono)">{code}</span>
</div>

<div class="wrap" id="wvs-main" tabindex="-1" role="main">
  <div class="hero">
    <h1>📟 펌웨어·IoT 진단 실습 <span>· {title}</span> <span class="badge">{count}개 점검</span></h1>
    <p>{desc}</p>
  </div>

  <div class="hostbar">
    <span>대상 기기 <b id="hostName">-</b></span>
    <span>· 펌웨어 이미지 <b id="hostImg">-</b></span>
    <span>· 아키텍처 <b id="hostArch">-</b></span>
    <span style="margin-left:auto">교육용 가상 펌웨어 (실제 기기 접속 아님)</span>
  </div>

  <div class="prog">
    <span>진행</span><span class="bar"><i id="pbar"></i></span><span id="ptext">0 / {count}</span>
  </div>

  <div class="brief-inc" id="incCard" style="display:none">
    <h2>🕵️ 사건 브리핑 <span style="font-weight:400;color:#64748b;font-size:11px">— 판정은 고정 검사기가, 막히면 AI 코치가 다음 행동을 제안합니다</span></h2>
    <p id="incStory"></p>
    <div class="stages" id="incStages"></div>
  </div>

  <div class="cols" style="margin-top:14px">
    <div>
      <div class="card">
        <h2>🔎 점검 항목</h2>
        <div class="mlist" id="mlist"></div>
        <div class="brief" id="brief"></div>

        <label class="fl" for="selVerdict">1) 판정</label>
        <select id="selVerdict" aria-label="판정 선택">
          <option value="">선택하세요</option>
          <option value="good">양호</option>
          <option value="vuln">취약</option>
        </select>

        <label class="fl" for="selEvidence">2) 그렇게 본 근거 (명령 출력에서 고르세요)</label>
        <select id="selEvidence" aria-label="판정 근거 선택"></select>

        <div class="acts">
          <button type="button" class="act judge" id="btnJudge">판정 제출</button>
          <button type="button" class="act fix" id="btnFix" disabled>조치 적용</button>
          <button type="button" class="act ghost" id="btnRecheck" disabled>재점검</button>
        </div>
        <div class="res" id="res"></div>

        <div class="coach" id="coach">
          <h3>🧭 AI 코치 <span style="font-weight:400;color:#64748b;font-size:11px">— 정답을 알려주지 않고, 다음 확인 행동 하나를 제안합니다</span></h3>
          <div class="cbtns">
            <button type="button" class="cask" id="btnCoach">코치에게 묻기</button>
            <button type="button" class="cprev" id="btnCoachPrev">전송 내용 보기</button>
          </div>
          <div class="cout" id="coachOut" role="status" aria-live="polite"></div>
        </div>
      </div>
    </div>

    <div>
      <div class="card">
        <h2>🧰 분석 워크벤치 <span style="font-weight:400;color:#64748b;font-size:11.5px">— 직접 명령을 쳐서 확인하세요</span></h2>
        <div class="term">
          <div class="out" id="termOut" aria-live="polite"></div>
          <div class="inp"><span id="prompt">analyst@fw-workbench:~$</span>
            <input id="termIn" autocomplete="off" spellcheck="false" aria-label="명령 입력" placeholder="명령을 입력하고 Enter (help 로 사용 가능한 명령 확인)">
          </div>
        </div>
        <div class="quick" id="quick"></div>
      </div>
    </div>
  </div>

  <div class="disc">
    ⚠️ 교육용 시뮬레이션입니다. 모든 명령은 이 페이지 안의 가상 펌웨어 이미지·파일시스템에 대해서만 동작하며 실제 기기에 접속하지 않습니다.<br>
    기기·브랜드·펌웨어 내용은 실존하지 않는 가상의 것이며, 임베디드 보안 점검의 구조만 참고해 교육용으로 새로 작성했습니다.
  </div>
</div>

<script>
(function(){{
  var L = window.WVS_FW_LAB, D = window.FW_LAB_DATA;
  var fs = new L.FileSystem(D.fs, D.host);
  var sh = new L.Shell(fs, fs.host);   // 같은 host 객체를 공유해야 조치가 출력에 반영된다
  var missions = D.missions, cur = 0;
  var state = missions.map(function(){{ return {{ tried:false, pass:false, fixed:false }}; }});

  var PROMPT = D.host.prompt || 'analyst@fw-workbench:~$';
  var out = document.getElementById('termOut');
  function print(text, cls){{
    var d = document.createElement('div');
    if (cls) d.className = cls;
    d.textContent = text;
    out.appendChild(d);
    out.scrollTop = out.scrollHeight;
  }}
  function exec(cmd){{
    print(PROMPT + ' ' + cmd, 'cmd');
    var r = sh.run(cmd);
    if (r) print(r, /No such file|지원하지 않는|찾을 수 없|잘못된/.test(r) ? 'err' : '');
  }}

  document.getElementById('hostName').textContent = D.host.device || D.host.name;
  document.getElementById('hostImg').textContent = (D.host.image && D.host.image.file) || '-';
  document.getElementById('hostArch').textContent = D.host.arch || '-';
  document.getElementById('prompt').textContent = PROMPT;

  var inp = document.getElementById('termIn');
  inp.addEventListener('keydown', function(e){{
    if (e.key !== 'Enter') return;
    var v = inp.value.trim();
    if (!v) return;
    inp.value = '';
    if (v === 'clear') {{ out.innerHTML = ''; return; }}
    exec(v);
  }});

  function renderList(){{
    var h = '';
    for (var i = 0; i < missions.length; i++) {{
      var c = 'mchip' + (i === cur ? ' on' : '') +
        (state[i].pass ? ' done' : (state[i].tried && !state[i].pass ? ' wrong' : ''));
      h += '<button type="button" class="' + c + '" data-i="' + i + '">' +
        L.esc(missions[i].id) + (state[i].pass ? ' ✓' : '') + '</button>';
    }}
    document.getElementById('mlist').innerHTML = h;
    var done = state.filter(function(s){{ return s.pass; }}).length;
    document.getElementById('pbar').style.width = Math.round(done / missions.length * 100) + '%';
    document.getElementById('ptext').textContent = done + ' / ' + missions.length;
    if (done === missions.length) {{
      try {{ window.WVSProgress && window.WVSProgress.complete(100, '{file}'); }} catch(e){{}}
    }}
  }}

  function renderMission(){{
    var m = missions[cur];
    document.getElementById('brief').innerHTML =
      '<span class="rk r' + m.risk + '">위험도 ' + m.risk + '</span>' +
      '<b>' + L.esc(m.id) + ' · ' + L.esc(m.title) + '</b><br>' + m.brief +
      '<div style="margin-top:9px;color:#8fa0ba;font-size:12.5px">확인할 곳: <code>' + L.esc(m.where) + '</code></div>';

    var ev = document.getElementById('selEvidence');
    ev.innerHTML = '<option value="">선택하세요</option>' +
      m.options.map(function(o){{ return '<option value="' + L.esc(o) + '">' + L.esc(o) + '</option>'; }}).join('');

    document.getElementById('selVerdict').value = '';
    document.getElementById('res').style.display = 'none';
    document.getElementById('btnFix').disabled = true;
    document.getElementById('btnRecheck').disabled = true;

    document.getElementById('quick').innerHTML = m.cmds.map(function(c){{
      return '<button type="button" data-cmd="' + L.esc(c) + '">' + L.esc(c) + '</button>';
    }}).join('');
    renderList();
  }}

  document.getElementById('mlist').addEventListener('click', function(e){{
    var b = e.target.closest('[data-i]');
    if (!b) return;
    cur = Number(b.getAttribute('data-i'));
    renderMission();
  }});
  document.getElementById('quick').addEventListener('click', function(e){{
    var b = e.target.closest('[data-cmd]');
    if (!b) return;
    exec(b.getAttribute('data-cmd'));
  }});

  document.getElementById('btnJudge').addEventListener('click', function(){{
    var m = missions[cur];
    var v = document.getElementById('selVerdict').value;
    var ev = document.getElementById('selEvidence').value;
    var box = document.getElementById('res');
    if (!v || !ev) {{
      box.className = 'res no'; box.style.display = 'block';
      box.innerHTML = '<h3>판정과 근거를 모두 고르세요</h3>근거까지 맞아야 통과입니다. 워크벤치에서 이미지를 직접 열어 보세요.';
      return;
    }}
    var g = L.grade(m, fs, v, ev);
    state[cur].tried = true;
    state[cur].pass = g.pass;
    if (g.pass) {{
      box.className = 'res ok'; box.style.display = 'block';
      box.innerHTML = '<h3>✅ 정확합니다 — ' + (g.actual === 'vuln' ? '취약' : '양호') + '</h3>' + m.why +
        (m.fix ? '<div style="margin-top:9px">아래 <b>조치 적용</b>을 누르면 재빌드된 펌웨어로 바뀝니다. 그 다음 <b>재점검</b>으로 같은 명령을 다시 실행해 보세요.</div>' : '');
      if (m.fix) document.getElementById('btnFix').disabled = false;
    }} else {{
      box.className = 'res no'; box.style.display = 'block';
      box.innerHTML = '<h3>❌ 다시 보세요</h3>' +
        (!g.verdictOk ? '판정이 다릅니다. ' : '판정은 맞았지만 <b>근거</b>가 다릅니다. ') +
        '이미지의 어느 파일·어느 줄이 이 판정을 만드는지 워크벤치에서 확인해 보세요.<br>' +
        '<div style="margin-top:7px;color:#fca5a5">힌트: ' + L.esc(m.hint) + '</div>' +
        '<div style="margin-top:6px;color:#a78bfa">막혔다면 아래 <b>🧭 AI 코치</b>에게 물어보세요.</div>';
    }}
    renderList();
  }});

  document.getElementById('btnFix').addEventListener('click', function(){{
    var m = missions[cur];
    if (!m.fix) return;
    m.fix(fs);
    state[cur].fixed = true;
    document.getElementById('btnFix').disabled = true;
    document.getElementById('btnRecheck').disabled = false;
    print('[조치] ' + m.fixNote, 'cmd');
    var box = document.getElementById('res');
    box.className = 'res ok'; box.style.display = 'block';
    box.innerHTML = '<h3>🔧 조치를 적용했습니다</h3>' + L.esc(m.fixNote) +
      '<div style="margin-top:9px"><b>재점검</b>을 눌러 같은 명령의 출력이 실제로 바뀌었는지 확인하세요.</div>';
  }});

  document.getElementById('btnRecheck').addEventListener('click', function(){{
    var m = missions[cur];
    m.cmds.forEach(exec);
    var now = m.verdict(fs);
    var box = document.getElementById('res');
    box.className = now === 'good' ? 'res ok' : 'res no';
    box.style.display = 'block';
    box.innerHTML = now === 'good'
      ? '<h3>✅ 재점검 결과: 양호</h3>같은 명령인데 출력이 달라졌습니다. 조치가 실제로 펌웨어를 바꿨다는 뜻입니다.'
      : '<h3>⚠️ 재점검 결과: 여전히 취약</h3>조치가 이 항목의 판정을 바꾸지 못했습니다.';
  }});

  print('펌웨어·IoT 진단 실습 — ' + (D.host.device || D.host.name) + ' (' + (D.host.arch || '') + ')');
  print('help 를 입력하면 쓸 수 있는 명령을 볼 수 있습니다.\n');

  var FILE = '{file}';
  function stripTags(s){{ return String(s == null ? '' : s).replace(/<[^>]+>/g, ''); }}

  /* ── 가이드 사건 브리핑 — 미션을 조사 단계로 엮는다(판정은 그대로 고정 검사기) ── */
  (function renderIncident(){{
    var inc = D.host.incident;
    if (!inc) return;
    document.getElementById('incStory').textContent = inc.story;
    var byId = {{}}; missions.forEach(function(m, i){{ byId[m.id] = i; }});
    var stagesEl = document.getElementById('incStages');
    stagesEl.innerHTML = (inc.stages || []).map(function(st){{
      var chips = (st.ids || []).filter(function(id){{ return byId[id] != null; }}).map(function(id){{
        return '<button type="button" data-go="' + byId[id] + '">' + L.esc(id) + '</button>';
      }}).join('');
      return '<div class="stage"><b>' + L.esc(st.label) + '</b><span class="ids">' + chips + '</span></div>';
    }}).join('');
    document.getElementById('incCard').style.display = 'block';
    stagesEl.addEventListener('click', function(e){{
      var b = e.target.closest('[data-go]'); if (!b) return;
      cur = Number(b.getAttribute('data-go')); renderMission();
      document.getElementById('brief').scrollIntoView({{ behavior:'smooth', block:'center' }});
    }});
  }})();

  /* ── AI 코치 — coach.js 계약 재사용. 화면에 이미 있는 것만 보내고 정답은 만들지 않는다 ── */
  var hintsUsed = 0, coachLoading = null;
  function loadCoach(){{
    if (window.WVS_COACH) return Promise.resolve(true);
    if (coachLoading) return coachLoading;
    coachLoading = new Promise(function(resolve){{
      var left = 2, done = false;
      function tick(){{ left--; if ((left <= 0 || window.WVS_COACH) && !done){{ done = true; resolve(!!window.WVS_COACH); }} }}
      ['/js/ai-client.js', '/js/coach.js'].forEach(function(src){{
        var s = document.createElement('script'); s.src = src; s.onload = tick; s.onerror = tick; document.head.appendChild(s);
      }});
      setTimeout(function(){{ if (!done){{ done = true; resolve(!!window.WVS_COACH); }} }}, 8000);
    }});
    return coachLoading;
  }}
  function coachCtx(){{
    var m = missions[cur];
    var v = document.getElementById('selVerdict').value;
    var ev = document.getElementById('selEvidence').value;
    return {{
      activityId: FILE, step: m.id,
      learningGoal: stripTags(m.title) + ' — 취약/양호를 판정하고 그 근거를 찾는다',
      givens: ['확인할 곳: ' + m.where, '쓸 수 있는 명령: ' + (m.cmds || []).join(', ')],
      successCondition: '판정과 근거가 모두 정확해야 통과합니다',
      evidence: (m.options || []).map(function(o, i){{ return {{ id:'opt-' + (i+1), label:String(o).slice(0,80) }}; }}),
      failedChecks: [{{ id:m.id, desc:stripTags(m.title), expected:'', actual:('제출 ' + (v||'-') + ' / ' + (ev||'-')).slice(0,40), meaning:stripTags(m.brief).slice(0,200) }}],
      hintsUsed: hintsUsed
    }};
  }}
  document.getElementById('btnCoachPrev').addEventListener('click', function(){{
    var out = document.getElementById('coachOut'); out.classList.add('on');
    out.innerHTML = '전송 내용을 준비 중…';
    loadCoach().then(function(){{
      out.innerHTML = window.WVS_COACH
        ? '<span class="lab">전송될 내용 (정답 조건식은 포함되지 않습니다)</span><pre>' + L.esc(window.WVS_COACH.preview(coachCtx())) + '</pre>'
        : '코치 모듈을 불러오지 못했습니다.';
    }});
  }});
  document.getElementById('btnCoach').addEventListener('click', function(){{
    var out = document.getElementById('coachOut'); out.classList.add('on');
    out.innerHTML = '코치가 지금 상태를 확인하는 중…';
    hintsUsed++;
    loadCoach().then(function(ok){{
      if (!ok || !window.WVS_COACH){{ out.innerHTML = '코치를 불러오지 못했습니다. 잠시 후 다시 시도하세요. (실습은 계속 진행됩니다)'; return; }}
      Promise.resolve(window.WVS_COACH.ask(coachCtx())).then(function(r){{
        var c = (r && r.coach) || {{}};
        var html = '';
        if (c.observation) html += '<div><span class="lab">관찰</span> ' + L.esc(c.observation) + '</div>';
        if (c.nextAction) html += '<div style="margin-top:5px"><span class="lab">다음 확인</span> ' + L.esc(c.nextAction) + '</div>';
        if (c.hint) html += '<div style="margin-top:5px"><span class="lab">힌트</span> ' + L.esc(c.hint) + '</div>';
        if (c.uncertainty) html += '<div style="margin-top:5px;color:#94a3b8">⚠ ' + L.esc(c.uncertainty) + '</div>';
        html += '<div style="margin-top:6px;color:#64748b">모드: ' + (c.mode === 'ai' ? 'AI' : 'AI 미연결 — 일반 지침') + '</div>';
        out.innerHTML = html || '응답을 받지 못했습니다.';
      }}).catch(function(){{ out.innerHTML = '코치 호출 중 오류가 발생했습니다. 실습은 계속하세요.'; }});
    }});
  }});

  renderMission();
}})();
</script>
</body>
</html>
'''


def build(lab):
    data_js = 'fw-lab-%s.js' % lab['key']
    html = PAGE.format(
        title=lab['title'], desc=lab['desc'], file=lab['file'],
        code=lab['code'], count=len(lab['missions']), data=data_js,
    )
    with io.open(os.path.join(OUT, lab['file']), 'w', encoding='utf-8') as f:
        f.write(html)

    ms = []
    for m in lab['missions']:
        ms.append(
            '{id:%s,risk:%d,title:%s,brief:%s,where:%s,hint:%s,why:%s,'
            'cmds:%s,options:%s,evidence:%s,verdict:%s,fix:%s,fixNote:%s}' % (
                json.dumps(m['id'], ensure_ascii=False), m['risk'],
                json.dumps(m['title'], ensure_ascii=False),
                json.dumps(m['brief'], ensure_ascii=False),
                json.dumps(m['where'], ensure_ascii=False),
                json.dumps(m['hint'], ensure_ascii=False),
                json.dumps(m['why'], ensure_ascii=False),
                json.dumps(m['cmds'], ensure_ascii=False),
                json.dumps(m['options'], ensure_ascii=False),
                json.dumps(m['evidence'], ensure_ascii=False),
                m['verdict'],
                m.get('fix', 'null'),
                json.dumps(m.get('fixNote', ''), ensure_ascii=False),
            )
        )
    js = ('/* 생성물 — _gen/gen_fw_lab.py 가 만든다. 직접 고치지 말 것. */\n'
          'window.FW_LAB_DATA = {\n'
          '  host: %s,\n'
          '  fs: %s,\n'
          '  missions: [\n    %s\n  ]\n};\n' % (
              json.dumps(lab['host'], ensure_ascii=False),
              json.dumps(lab['fs'], ensure_ascii=False, indent=1),
              ',\n    '.join(ms),
          ))
    with io.open(os.path.join(OUT, 'js', data_js), 'w', encoding='utf-8') as f:
        f.write(js)
    return lab['file'], len(lab['missions'])


def main():
    import importlib
    mods = sys.argv[1:] or ['specs_fw_router', 'specs_fw_iot']
    total = 0
    for name in mods:
        for lab in importlib.import_module(name).LABS:
            fn, n = build(lab)
            print('wrote %-30s %2d개 점검' % (fn, n))
            total += n
    print('TOTAL %d개 점검 항목' % total)


if __name__ == '__main__':
    main()
