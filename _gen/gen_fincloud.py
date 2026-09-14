# -*- coding: utf-8 -*-
"""
07_fincloud-*.html  금융권 클라우드 관리체계 보안 취약점 진단 시뮬레이터 생성기

「클라우드 관리체계 보안 취약점 평가기준(퍼블릭 클라우드)」의 PISM 항목을 개념 재구성.
기존 11_cloud-c*.html 이 '개념 설명형' 이라면, 이쪽은 **실제 AWS 진단 절차를 그대로 따라가는
실습형**이다 — 평가기준의 '평가방법' 열에 적힌 AWS CLI 명령을 모의 터미널에서 직접 실행하고,
실제와 같은 형태의 JSON 응답을 읽어 양호/취약을 스스로 판정한 뒤 조치까지 수행한다.

설계 원칙
- 모든 출력은 **실제 AWS CLI 응답 형식**(JSON/table)을 따른다. 계정 ID·ARN·리전·리소스 ID 도
  실제 형식을 지킨다(값은 가상). 학습자가 현업에서 같은 화면을 보게 하기 위함이다.
- 네트워크 호출은 없다. 전부 페이지 안의 모의 응답이다.
- 판정을 도구가 대신해 주지 않는다. 명령을 실행해 **출력을 읽고 판단하는 것**이 이 실습의 핵심이다.
"""
import html
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')

PAGE = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta name="theme-color" content="#232f3e"><link rel="manifest" href="/manifest.json"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="/js/pwa.js" defer></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{pism}: {title} | 금융 클라우드 진단 시뮬레이터</title>
<meta name="description" content="{pism} {title} — 금융권 클라우드 관리체계 보안 취약점 평가기준 기반 AWS 진단 실습. 평가방법에 명시된 AWS CLI 명령을 모의 환경에서 실행하고 양호/취약을 판정한 뒤 조치까지 수행합니다.">
<style>
:root{{--aws-navy:#232f3e;--aws-navy2:#161e2d;--aws-orange:#ff9900;--aws-blue:#0972d3;--bg:#f2f3f3;--panel:#fff;--line:#d5dbdb;--ink:#16191f;--muted:#5f6b7a;--bad:#d13212;--good:#037f0c;--warn:#8d6605;--mono:'Consolas','Menlo','JetBrains Mono',monospace;}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Amazon Ember','Segoe UI','Malgun Gothic',sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}}
a{{color:var(--aws-blue)}}
/* 상단 AWS 콘솔 풍 바 */
.awsbar{{background:var(--aws-navy);color:#fff;display:flex;align-items:center;gap:16px;padding:9px 18px;flex-wrap:wrap;font-size:13px}}
.awsbar .logo{{font-weight:800;letter-spacing:.4px}}
.awsbar .logo i{{color:var(--aws-orange);font-style:normal}}
.awsbar a{{color:#d5dbdb;text-decoration:none;font-size:12.5px}}
.awsbar a:hover{{color:#fff}}
.awsbar .sp{{margin-left:auto}}
.awsbar .acct{{font-family:var(--mono);font-size:12px;color:#d5dbdb;background:rgba(255,255,255,.08);border-radius:4px;padding:3px 9px}}
.wrap{{max-width:1180px;margin:0 auto;padding:18px 16px 80px}}
/* 헤더 */
.head{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:16px}}
.head .crumb{{font-size:12px;color:var(--muted);font-family:var(--mono);margin-bottom:7px}}
.head h1{{font-size:21px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.head h1 .pid{{font-family:var(--mono);font-size:13px;background:var(--aws-navy);color:#fff;border-radius:5px;padding:3px 9px}}
.tags{{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}}
.tag{{font-size:11.5px;font-weight:700;border-radius:20px;padding:3px 11px;background:#eaeded;color:#414d5c}}
.tag.r5{{background:#fdecea;color:var(--bad)}} .tag.r4{{background:#fdf3e2;color:var(--warn)}}
.tag.r3{{background:#eef6ff;color:var(--aws-blue)}} .tag.r2,.tag.r1{{background:#eaeded;color:#414d5c}}
.desc{{font-size:13.5px;color:#414d5c;margin-top:11px;padding-top:11px;border-top:1px solid var(--line)}}
/* 탭 */
.tabs{{display:flex;gap:0;border-bottom:2px solid var(--line);margin-bottom:16px;flex-wrap:wrap}}
.tab{{padding:11px 18px;cursor:pointer;font-weight:700;font-size:14px;color:var(--muted);border-bottom:3px solid transparent;margin-bottom:-2px;background:none;border-top:0;border-left:0;border-right:0;font-family:inherit}}
.tab.active{{color:var(--aws-blue);border-bottom-color:var(--aws-blue)}}
.pane{{display:none}} .pane.active{{display:block}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:16px}}
.panel h2{{font-size:15px;margin-bottom:11px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.panel h2 .n{{font-family:var(--mono);font-size:11.5px;background:#eaeded;color:#414d5c;border-radius:4px;padding:2px 8px}}
.hint{{font-size:12.5px;color:var(--muted);margin-top:7px}}
/* 콘솔 경로 */
.cpath{{background:#fbfbfb;border:1px solid var(--line);border-left:4px solid var(--aws-orange);border-radius:7px;padding:11px 13px;font-size:13px;color:#414d5c;margin:9px 0}}
.cpath b{{color:var(--ink)}}
.cpath code{{font-family:var(--mono);font-size:12px;background:#eaeded;border-radius:3px;padding:1px 5px}}
/* 터미널 */
.term{{background:#0f1b2a;border-radius:9px;padding:14px 15px;font-family:var(--mono);font-size:12.5px;line-height:1.65;color:#d1e3f5;min-height:230px;max-height:430px;overflow:auto;white-space:pre-wrap;word-break:break-word}}
.term .ps{{color:#7ee787}} .term .cm{{color:#ffd479}} .term .er{{color:#ff7b72}}
.term .ok{{color:#7ee787}} .term .dim{{color:#7d8da1}} .term .hl{{color:#ff9900;font-weight:700}}
.cmds{{display:flex;flex-direction:column;gap:7px;margin-top:11px}}
.cmdbtn{{text-align:left;background:#fff;border:1px solid var(--line);border-radius:7px;padding:9px 12px;cursor:pointer;font-family:var(--mono);font-size:12px;color:#0f1b2a;transition:.15s;word-break:break-all}}
.cmdbtn:hover{{border-color:var(--aws-blue);background:#f2f8fd}}
.cmdbtn.done{{border-color:var(--good);background:#f2fbf3}}
.cmdbtn .lbl{{display:block;font-family:inherit;font-size:11.5px;color:var(--muted);font-weight:700;margin-bottom:3px}}
.cmdbtn.done .lbl::after{{content:' ✓ 실행함';color:var(--good)}}
.inputrow{{display:flex;gap:7px;margin-top:9px}}
.inputrow input{{flex:1;font-family:var(--mono);font-size:12.5px;padding:9px 11px;border:1px solid var(--line);border-radius:7px;background:#fff;color:var(--ink);min-width:0}}
/* 판정 */
.verdict{{display:flex;gap:9px;flex-wrap:wrap;margin-top:12px}}
.vbtn{{flex:1;min-width:150px;padding:13px;border-radius:8px;border:2px solid var(--line);background:#fff;cursor:pointer;font-weight:800;font-size:14px;font-family:inherit;transition:.15s}}
.vbtn:hover{{border-color:var(--aws-blue)}}
.vbtn.sel-ok{{border-color:var(--good);background:#f2fbf3;color:var(--good)}}
.vbtn.sel-bad{{border-color:var(--bad);background:#fdecea;color:var(--bad)}}
.fb{{margin-top:12px;border-radius:8px;padding:13px 15px;font-size:13.5px;display:none}}
.fb.show{{display:block}}
.fb.right{{background:#f2fbf3;border-left:4px solid var(--good);color:#0d4715}}
.fb.wrong{{background:#fdecea;border-left:4px solid var(--bad);color:#7d1a08}}
.fb b{{display:block;margin-bottom:5px;font-size:14px}}
.fb .ev{{font-family:var(--mono);font-size:11.5px;background:rgba(0,0,0,.05);border-radius:5px;padding:8px 10px;margin-top:8px;white-space:pre-wrap}}
/* 조치 */
.fixbox{{background:#0f1b2a;border-radius:9px;padding:13px 15px;font-family:var(--mono);font-size:12.5px;color:#d1e3f5;white-space:pre-wrap;line-height:1.65;overflow-x:auto}}
.iac{{background:#fbfbfb;border:1px solid var(--line);border-radius:8px;padding:12px 14px;font-family:var(--mono);font-size:12px;white-space:pre-wrap;color:#16191f;overflow-x:auto;line-height:1.6}}
.btn{{cursor:pointer;border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:7px;padding:9px 15px;font-size:13px;font-weight:700;font-family:inherit}}
.btn.pri{{background:var(--aws-orange);border-color:var(--aws-orange);color:#16191f}}
.btn.nav{{background:var(--aws-navy);border-color:var(--aws-navy);color:#fff}}
.acts{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}
/* 표 */
table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:9px}}
th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#f2f3f3;font-size:12.5px;white-space:nowrap}}
td.mono{{font-family:var(--mono);font-size:12px}}
ul.ref{{margin-left:19px;font-size:13.5px;line-height:1.8}}
ul.ref li{{margin:3px 0}}
.note{{background:#eef6ff;border-left:4px solid var(--aws-blue);border-radius:7px;padding:11px 13px;font-size:13px;color:#0b3c63;margin:11px 0}}
.warnbox{{background:#fdf3e2;border-left:4px solid var(--warn);border-radius:7px;padding:11px 13px;font-size:13px;color:#5c4405;margin:11px 0}}
.fin{{background:#f4f1fb;border-left:4px solid #7c3aed;border-radius:7px;padding:11px 13px;font-size:13px;color:#3b2a67;margin:11px 0}}
.disc{{font-size:12px;color:var(--muted);border-top:1px dashed var(--line);padding-top:11px;margin-top:18px}}
.sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
.stepbar{{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}}
.stepbar div{{flex:1;min-width:110px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 11px;font-size:12px;color:var(--muted)}}
.stepbar div.on{{border-color:var(--aws-blue);color:var(--aws-blue);font-weight:700}}
.stepbar div.ok{{border-color:var(--good);color:var(--good);font-weight:700}}
@media(max-width:760px){{.wrap{{padding:14px 12px 80px}}.head h1{{font-size:18px}}.term{{font-size:11.5px}}}}
</style>
</head>
<body>
<div class="awsbar">
  <span class="logo"><i>aws</i> &nbsp;금융 클라우드 진단</span>
  <a href="index.html">홈</a>
  <a href="vuln-hub.html">카탈로그</a>
  <a href="fincloud-hub.html">진단 항목 전체</a>
  <span class="sp"></span>
  <span class="acct">ap-northeast-2 · 3820-1174-9265</span>
</div>
<div class="wrap">

  <div class="head">
    <div class="crumb">클라우드 관리체계 보안 취약점 평가기준 (퍼블릭 클라우드) / {area} / {ctrl}</div>
    <h1><span class="pid">{pism}</span>{title}</h1>
    <div class="tags">
      <span class="tag r{risk}">위험도 {risk}</span>
      <span class="tag">{kind}</span>
      <span class="tag">{svc}</span>
      <span class="tag">평가 구분: {evaltype}</span>
    </div>
    <div class="desc">{detail}</div>
  </div>

  <div class="stepbar">
    <div id="st1" class="on">1. 점검 대상 확인</div>
    <div id="st2">2. CLI 진단</div>
    <div id="st3">3. 양호/취약 판정</div>
    <div id="st4">4. 조치 · 재확인</div>
  </div>

  <div class="tabs">
    <button class="tab active" data-pane="diag">🔍 진단</button>
    <button class="tab" data-pane="fix">🛠️ 조치</button>
    <button class="tab" data-pane="ref">📋 평가기준</button>
  </div>

  <!-- 진단 -->
  <div id="pane-diag" class="pane active">
    <div class="panel">
      <h2><span class="n">방법 1</span>AWS Management Console 경로</h2>
      <div class="cpath">{console_path}</div>
      <div class="hint">콘솔은 화면이 자주 바뀝니다. 실제 점검에서는 아래 <b>CLI(방법 2)</b> 로 증적을 남기는 편이 재현성이 높습니다.</div>
    </div>

    <div class="panel">
      <h2><span class="n">방법 2</span>AWS CLI 진단 <span style="margin-left:auto;font-size:12px;color:var(--muted);font-weight:400" id="ranCount"></span></h2>
      <div class="hint" style="margin-bottom:10px">아래 명령을 눌러 실행하거나, 직접 입력해 보세요. 응답은 실제 AWS CLI 출력 형식을 따릅니다.</div>
      <div class="term" id="term"><span class="dim">$ aws sts get-caller-identity</span>
{{
    "UserId": "AIDA4XQ7N2VZK3RJTPLWE",
    "Account": "382011749265",
    "Arn": "arn:aws:iam::382011749265:user/audit-readonly"
}}
<span class="dim">진단 계정으로 로그인되었습니다. 아래 명령을 실행해 점검을 시작하세요.</span></div>
      <div class="cmds" id="cmds"></div>
      <div class="inputrow">
        <!-- placeholder 는 접근 가능한 이름이 아니다. 스크린리더용으로 aria-label 을 따로 준다. -->
        <label for="cli" class="sr-only">AWS CLI 명령 직접 입력</label>
        <input id="cli" type="text" aria-label="AWS CLI 명령 직접 입력"
               placeholder="aws ... 명령을 직접 입력 후 Enter" autocomplete="off" spellcheck="false">
        <button class="btn nav" id="runBtn" aria-label="입력한 AWS CLI 명령 실행">실행</button>
      </div>
    </div>

    <div class="panel">
      <h2><span class="n">판정</span>이 환경은 양호합니까, 취약합니까?</h2>
      <div class="hint">평가기준의 판단 근거는 <b>명령 출력</b>입니다. 먼저 위에서 명령을 실행해 출력을 확인하세요.</div>
      <div class="verdict">
        <button class="vbtn" id="vOk">✅ 양호 (조치 불필요)</button>
        <button class="vbtn" id="vBad">⚠️ 취약 (조치 필요)</button>
      </div>
      <div class="fb" id="fb"></div>
    </div>
  </div>

  <!-- 조치 -->
  <div id="pane-fix" class="pane">
    <div class="panel">
      <h2>🛠️ 조치 방법</h2>
      <div style="font-size:13.5px;color:#414d5c;margin-bottom:11px">{fix_intro}</div>
      <div class="fixbox">{fix_cmd}</div>
      <div class="acts">
        <button class="btn pri" id="applyBtn">조치 적용 후 재점검</button>
      </div>
      <div class="fb" id="fixfb"></div>
    </div>
    <div class="panel">
      <h2>📐 IaC 로 고정하기</h2>
      <div class="hint" style="margin-bottom:9px">콘솔에서 한 번 고쳐도 다음 배포에서 되돌아갑니다. 코드로 고정해야 재발하지 않습니다.</div>
      <div class="iac">{iac}</div>
    </div>
    <div class="warnbox">{pitfall}</div>
  </div>

  <!-- 평가기준 -->
  <div id="pane-ref" class="pane">
    <div class="panel">
      <h2>📋 평가항목 정보</h2>
      <table>
        <tr><th>평가항목 ID</th><td class="mono">{pism}</td></tr>
        <tr><th>구분</th><td>{kind}</td></tr>
        <tr><th>통제분야</th><td>{area}</td></tr>
        <tr><th>통제구분(대)</th><td>{ctrl}</td></tr>
        <tr><th>평가항목</th><td>{title}</td></tr>
        <tr><th>위험도</th><td>{risk}</td></tr>
        <tr><th>평가 구분 (AWS)</th><td>{evaltype}</td></tr>
        <tr><th>상세설명</th><td>{detail}</td></tr>
      </table>
    </div>
    <div class="panel">
      <h2>📎 확인 자료 (증적)</h2>
      <ul class="ref">{evidence}</ul>
      <div class="note">평가에서는 <b>화면 캡처보다 CLI 출력</b>이 강한 증적입니다. 명령·실행시각·계정 ARN 이 함께 남기 때문입니다. 위 진단 탭의 출력을 그대로 보고서에 붙이면 됩니다.</div>
    </div>
    <div class="panel">
      <h2>🏦 금융 관점</h2>
      <div class="fin">{finance}</div>
    </div>
    <div class="disc">
      「클라우드 관리체계 보안 취약점 평가기준(퍼블릭 클라우드)」의 평가항목을 <b>교육용으로 재구성</b>한 시뮬레이터입니다.
      계정 ID·ARN·리소스 ID 는 형식만 실제와 같게 만든 <b>가상 값</b>이며, 어떤 AWS 환경에도 접속하지 않습니다.
      실제 평가에서는 기관의 최신 평가기준 원문과 AWS 공식 문서를 따르십시오.
    </div>
  </div>
</div>

<script src="/js/progress.js" defer></script>
<!-- 공통 셸은 싣되 상단 바는 끈다(data-topbar="off"). 이 페이지의 AWS 콘솔 바와 겹치기 때문이다.
     끄더라도 모바일 하단 탭바·Ctrl+K 검색 팔레트·건너뛰기 링크는 그대로 동작한다.
     ※ 속성을 src 따옴표 안에 넣으면 404 가 난다(QA P0-03). 반드시 바깥에 둘 것. -->
<script src="/js/soc-chrome.js" data-topbar="off" defer></script>
<script>
var CMDS = {cmds_js};
var ANSWER = "{answer}";
var WHY_BAD = {why_bad_js};
var WHY_OK  = {why_ok_js};
var FIX_OUT = {fix_out_js};
var PAGEID  = "{file}";

var ran = {{}}, judged = false, fixed = false;
function el(id){{ return document.getElementById(id); }}
function esc(s){{ return String(s).replace(/[&<>]/g, function(c){{ return {{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]; }}); }}

function write(html){{
  var t = el('term');
  t.insertAdjacentHTML('beforeend', '\n' + html);
  t.scrollTop = t.scrollHeight;
}}
function runCmd(i){{
  var c = CMDS[i];
  write('<span class="ps">$</span> <span class="cm">' + esc(c.cmd) + '</span>\n' + c.out);
  if (!ran[i]) {{
    ran[i] = true;
    var b = document.querySelector('[data-cmd="' + i + '"]');
    if (b) b.classList.add('done');
    updateRan();
  }}
}}
function updateRan(){{
  var n = Object.keys(ran).length;
  el('ranCount').textContent = n + ' / ' + CMDS.length + ' 실행';
  if (n > 0) {{ el('st2').className = 'ok'; el('st1').className = 'ok'; el('st3').className = 'on'; }}
}}
function judge(pick){{
  var f = el('fb');
  var right = (pick === ANSWER);
  el('vOk').className  = 'vbtn' + (pick === 'ok'  ? ' sel-ok'  : '');
  el('vBad').className = 'vbtn' + (pick === 'bad' ? ' sel-bad' : '');
  if (Object.keys(ran).length === 0) {{
    f.className = 'fb show wrong';
    f.innerHTML = '<b>먼저 명령을 실행하세요.</b>출력을 보지 않고 내린 판정은 평가 증적이 되지 않습니다. 위 진단 명령을 최소 1개 이상 실행한 뒤 판정하세요.';
    return;
  }}
  f.className = 'fb show ' + (right ? 'right' : 'wrong');
  f.innerHTML = (right ? '<b>✅ 정확합니다.</b>' : '<b>❌ 다시 보세요.</b>') + (ANSWER === 'bad' ? WHY_BAD : WHY_OK);
  if (right && !judged) {{
    judged = true;
    el('st3').className = 'ok'; el('st4').className = 'on';
    try {{ if (window.WVSProgress) window.WVSProgress.markVisited(PAGEID); }} catch (e) {{}}
  }}
}}
function applyFix(){{
  var f = el('fixfb');
  f.className = 'fb show right';
  f.innerHTML = '<b>조치 적용 후 재점검 결과</b>진단 명령을 다시 실행하면 아래와 같이 바뀝니다.<div class="ev">' + esc(FIX_OUT) + '</div>';
  if (!fixed) {{
    fixed = true;
    el('st4').className = 'ok';
    try {{ if (window.WVSProgress) window.WVSProgress.complete(undefined, PAGEID); }} catch (e) {{}}
  }}
}}

document.addEventListener('DOMContentLoaded', function () {{
  /* 명령 버튼 */
  var h = '';
  for (var i = 0; i < CMDS.length; i++) {{
    h += '<button class="cmdbtn" data-cmd="' + i + '"><span class="lbl">' + esc(CMDS[i].label) + '</span>' + esc(CMDS[i].cmd) + '</button>';
  }}
  el('cmds').innerHTML = h;
  updateRan();
  el('cmds').addEventListener('click', function (e) {{
    var b = e.target.closest('[data-cmd]');
    if (b) runCmd(+b.getAttribute('data-cmd'));
  }});

  /* 직접 입력 — 등록된 명령의 앞부분이 일치하면 그 응답을 낸다 */
  function submit(){{
    var v = el('cli').value.trim();
    if (!v) return;
    el('cli').value = '';
    if (!/^aws\s/.test(v)) {{
      write('<span class="ps">$</span> <span class="cm">' + esc(v) + '</span>\n<span class="er">command not found: ' + esc(v.split(/\s+/)[0]) + '</span>  <span class="dim">(이 시뮬레이터는 aws CLI 만 처리합니다)</span>');
      return;
    }}
    var key = v.replace(/\s+/g, ' ').toLowerCase();
    for (var i = 0; i < CMDS.length; i++) {{
      var c = CMDS[i].cmd.replace(/\s+/g, ' ').toLowerCase();
      var head = c.split(' ').slice(0, 3).join(' ');
      if (key === c || key.indexOf(head) === 0) {{ runCmd(i); return; }}
    }}
    write('<span class="ps">$</span> <span class="cm">' + esc(v) + '</span>\n<span class="er">\nAn error occurred (AccessDenied) when calling the operation: 이 실습 환경에서는 아래 등록된 진단 명령만 응답합니다.</span>');
  }}
  el('runBtn').addEventListener('click', submit);
  el('cli').addEventListener('keydown', function (e) {{ if (e.key === 'Enter') submit(); }});

  el('vOk').addEventListener('click', function () {{ judge('ok'); }});
  el('vBad').addEventListener('click', function () {{ judge('bad'); }});
  el('applyBtn').addEventListener('click', applyFix);

  /* 탭 */
  document.querySelector('.tabs').addEventListener('click', function (e) {{
    var t = e.target.closest('.tab');
    if (!t) return;
    document.querySelectorAll('.tab').forEach(function (x) {{ x.classList.remove('active'); }});
    document.querySelectorAll('.pane').forEach(function (x) {{ x.classList.remove('active'); }});
    t.classList.add('active');
    el('pane-' + t.getAttribute('data-pane')).classList.add('active');
  }});

  try {{ if (window.WVSProgress) window.WVSProgress.markVisited(PAGEID); }} catch (e) {{}}
}});
</script>
</body>
</html>
'''


def jss(s):
    """자바스크립트 템플릿 리터럴로 안전하게 감싼다."""
    return '`' + str(s).replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${') + '`'


def esc(s):
    return html.escape(str(s), quote=False)


def cmds_js(cmds):
    out = []
    for c in cmds:
        out.append('{label:%s, cmd:%s, out:%s}' % (jss(c['label']), jss(c['cmd']), jss(c['out'])))
    return '[' + ',\n'.join(out) + ']'


def render(s):
    return PAGE.format(
        file=s['file'], pism=s['pism'], title=esc(s['title']), risk=s['risk'],
        kind=esc(s.get('kind', '기술적 보안')), area=esc(s['area']), ctrl=esc(s['ctrl']),
        svc=esc(s.get('svc', 'AWS')), evaltype=esc(s.get('evaltype', '스크립트')),
        detail=s['detail'],
        console_path=s['console_path'],
        cmds_js=cmds_js(s['cmds']),
        answer=s.get('answer', 'bad'),
        why_bad_js=jss(s['why']),
        why_ok_js=jss(s['why']),
        fix_intro=s['fix_intro'],
        fix_cmd=esc(s['fix_cmd']),
        fix_out_js=jss(s['fix_out']),
        iac=esc(s['iac']),
        pitfall=s['pitfall'],
        evidence=''.join('<li>%s</li>' % e for e in s['evidence']),
        finance=s['finance'],
    )


def main():
    import importlib
    import sys
    mods = sys.argv[1:] or ['specs_fincloud']
    total = 0
    for m in mods:
        for s in importlib.import_module(m).SPECS:
            path = os.path.join(OUT_DIR, s['file'])
            with open(path, 'w', encoding='utf-8') as f:
                f.write(render(s))
            print('wrote', s['file'], '-', s['pism'], s['title'])
            total += 1
    print('TOTAL', total)


if __name__ == '__main__':
    main()
