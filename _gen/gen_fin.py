# -*- coding: utf-8 -*-
"""
07_fin-*.html  전자금융 보안 특화 시뮬레이터 생성기
기존 sim-sql.html 의 뱅킹 네이비 테마/2탭(Red·Blue)/터미널 로그/컴플라이언스 분석 톤을 따른다.
출처: 금융보안원 「전자금융기반시설 보안 취약점 평가기준(제2026-1호)」 항목을 개념 재구성(원문 비복제).
모두 클라이언트 사이드 시뮬레이션(백엔드 없음).
"""
import html, os, json

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')

PAGE = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>전자금융 보안: {title}</title>
<style>
:root {{ --bank-primary:#003876; --bank-secondary:#005eb8; --bank-bg:#f3f4f6; --text-dark:#1a1a1a; --danger:#d32f2f; --success:#2e7d32; --warning:#ed6c02; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Pretendard',-apple-system,BlinkMacSystemFont,system-ui,Roboto,sans-serif; background:var(--bank-bg); color:var(--text-dark); padding:20px; line-height:1.5; }}
.container {{ max-width:1400px; margin:0 auto; }}
.top-nav {{ margin-bottom:15px; }}
.top-nav a {{ color:var(--bank-primary); text-decoration:none; font-weight:700; font-size:14px; }}
.header {{ background:white; padding:20px 30px; border-radius:12px; box-shadow:0 4px 6px -1px rgba(0,0,0,.1); margin-bottom:25px; border-left:6px solid var(--bank-primary); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }}
.header h1 {{ font-size:22px; color:var(--bank-primary); display:flex; align-items:center; gap:12px; }}
.badge {{ background:#e3f2fd; color:#1565c0; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:700; }}
.risk {{ padding:4px 10px; border-radius:6px; font-size:12px; font-weight:700; color:#fff; background:var(--danger); }}
.tabs {{ display:flex; gap:15px; margin-bottom:20px; }}
.tab {{ flex:1; padding:18px; background:white; border-radius:10px; cursor:pointer; font-weight:600; color:#666; transition:.3s; border:2px solid transparent; display:flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 2px 4px rgba(0,0,0,.05); }}
.tab:hover {{ transform:translateY(-2px); }}
.tab.active {{ border-color:var(--bank-primary); color:var(--bank-primary); background:#eef5ff; }}
.grid-container {{ display:grid; grid-template-columns:1fr 1fr; gap:25px; }}
.content-section {{ display:none; animation:fadeIn .4s ease; }}
.content-section.active {{ display:block; }}
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
.panel {{ background:white; border-radius:12px; padding:25px; box-shadow:0 4px 6px -1px rgba(0,0,0,.1); margin-bottom:25px; }}
.panel-title {{ font-size:18px; font-weight:700; color:#333; margin-bottom:20px; padding-bottom:12px; border-bottom:2px solid #f0f0f0; display:flex; justify-content:space-between; align-items:center; }}
.scenario {{ background:#f8fbff; border:1px solid #d6e6fb; border-radius:8px; padding:15px; font-size:14px; color:#33475b; margin-bottom:18px; }}
.scenario b {{ color:var(--bank-primary); }}
.attack-controls {{ background:#212121; color:#fff; padding:20px; border-radius:10px; margin-bottom:20px; border:1px solid #333; }}
.toggle-switch {{ display:flex; align-items:center; justify-content:space-between; cursor:pointer; }}
.toggle-status {{ font-family:'Consolas',monospace; color:#00ff00; font-weight:700; }}
.req-label {{ display:block; font-size:12px; font-weight:700; color:#555; margin:14px 0 6px; }}
.req-box {{ width:100%; background:#0d1b2a; color:#7ddcff; border:1px solid #1b3a5b; border-radius:8px; padding:14px; font-family:'Consolas',monospace; font-size:13px; line-height:1.6; resize:vertical; min-height:140px; }}
.btn-submit {{ width:100%; padding:15px; background:var(--bank-primary); color:white; border:none; border-radius:6px; font-size:15px; font-weight:700; cursor:pointer; transition:.3s; margin-top:16px; }}
.btn-submit:hover {{ background:#002a5c; }}
.btn-submit.hacked {{ background:var(--danger); }}
.terminal {{ background:#1e1e1e; color:#d4d4d4; padding:15px; border-radius:8px; font-family:'Consolas',monospace; font-size:13px; height:240px; overflow-y:auto; line-height:1.6; border:1px solid #333; }}
.log-time {{ color:#569cd6; margin-right:8px; }}
.result-card {{ display:none; margin-top:18px; border-radius:8px; padding:16px; animation:fadeIn .3s; }}
.result-breach {{ background:#fff5f5; border:1px solid #ffcdd2; color:#b71c1c; }}
.result-blocked {{ background:#e8f5e9; border:1px solid #c8e6c9; color:#1b5e20; }}
.data-table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:10px; }}
.data-table th {{ background:#f8f9fa; padding:10px; text-align:left; border-bottom:2px solid #ddd; color:#555; }}
.data-table td {{ padding:10px; border-bottom:1px solid #eee; }}
.amount {{ font-family:'Consolas',monospace; font-weight:700; color:var(--bank-primary); text-align:right; }}
.compliance-alert {{ background:#fff5f5; border:1px solid #ffcdd2; padding:15px; border-radius:8px; margin-top:15px; font-size:13px; color:#b71c1c; display:none; animation:fadeIn .3s; }}
.code-editor {{ width:100%; height:320px; background:#282c34; color:#abb2bf; padding:20px; border-radius:8px; border:none; font-family:'Consolas',monospace; font-size:13px; line-height:1.6; resize:vertical; }}
.kisa-ref {{ font-size:14px; line-height:1.7; color:#444; }}
.kisa-ref h4 {{ color:var(--bank-primary); margin:14px 0 6px; font-size:15px; }}
.kisa-ref ul {{ margin-left:18px; }}
@media (max-width:1000px) {{ .grid-container {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="top-nav"><a href="index.html">&larr; 메인으로</a></div>
  <div class="header">
    <h1><span>{icon}</span> 전자금융 보안 모의해킹 &middot; {title}</h1>
    <div style="text-align:right; font-size:13px; color:#555;">
      Target: <strong>{target}</strong><br>
      평가기준: <span class="risk">위험도 {risk}</span> <span class="badge">{item_code}</span>
    </div>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('attack')">🔓 공격 시뮬레이션 (Red Team)</div>
    <div class="tab" onclick="switchTab('defense')">🛡️ 대응 방안 (Blue Team)</div>
  </div>

  <div id="tab-attack" class="content-section active">
    <div class="grid-container">
      <div>
        <div class="panel">
          <div class="panel-title"><span>{attack_panel_title}</span><span style="font-size:12px; color:#666; font-weight:normal;">🔒 Secured Channel</span></div>
          <div class="scenario">{scenario_html}</div>
          <div class="attack-controls">
            <div class="toggle-switch" onclick="toggleAttack()">
              <div><strong>⚡ {attack_name}</strong><br><span style="font-size:12px; opacity:.7;">{attack_sub}</span></div>
              <div class="toggle-status" id="attackStatus">OFF</div>
            </div>
          </div>
          <label class="req-label">📡 거래/인증 요청 (가로채어 변조 가능)</label>
          <textarea class="req-box" id="reqBox" spellcheck="false">{normal_req}</textarea>
          <button class="btn-submit" id="sendBtn" onclick="sendRequest()">요청 전송</button>
          <div class="result-card" id="resultCard"></div>
        </div>
      </div>
      <div>
        <div class="panel">
          <div class="panel-title">🖥️ 금융 시스템 처리 로그</div>
          <div class="terminal" id="systemLog">
            <div><span class="log-time">[SYSTEM]</span> Core Banking Channel ready.</div>
            <div><span class="log-time">[INFO]</span> 거래 요청 대기 중...</div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-title">⚖️ 컴플라이언스 위반 분석</div>
          <div id="complianceReport" style="color:#666; font-size:14px; text-align:center; padding:20px;">공격 실행 후 분석 결과가 표시됩니다.</div>
          <div id="violationAlert" class="compliance-alert">
            <strong>[심각] 전자금융 보안 기준 위반 감지</strong>
            <ul style="margin-top:8px; margin-left:20px; list-style:circle;">{violations}</ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="tab-defense" class="content-section">
    <div class="grid-container">
      <div class="panel">
        <div class="panel-title">🛡️ 대응 코드/설정 실습</div>
        <p style="font-size:14px; color:#555; margin-bottom:15px;">{defense_intro}</p>
        <textarea id="codeEditor" class="code-editor">{vuln_code}</textarea>
        <div style="margin-top:15px; display:flex; gap:10px;">
          <button onclick="verifyCode()" class="btn-submit" style="width:auto; background:var(--success); margin-top:0;">코드 검증</button>
          <button onclick="showHint()" style="padding:15px; border:1px solid #ddd; background:white; border-radius:6px; cursor:pointer;">힌트(정답) 보기</button>
        </div>
        <div id="codeResult" style="margin-top:15px;"></div>
      </div>
      <div class="panel">
        <div class="panel-title">📚 금융보안원 평가기준 / 조치 가이드</div>
        <div class="kisa-ref">{kisa_ref}</div>
      </div>
    </div>
  </div>
</div>

<script>
const NORMAL_REQ = {normal_req_js};
const ATTACK_REQ = {attack_req_js};
const SECURE_HINT = {secure_hint_js};
const CHECKS = {checks_js};
let isAttackOn = false;

function switchTab(name){{
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.content-section').forEach(c=>c.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
}}
function addLog(msg,type='info'){{
  const box=document.getElementById('systemLog'); const time=new Date().toLocaleTimeString('ko-KR');
  let color='#d4d4d4'; if(type==='error')color='#f48771'; if(type==='warn')color='#cca700'; if(type==='success')color='#89d185';
  const d=document.createElement('div'); d.innerHTML=`<span class="log-time">[${{time}}]</span> <span style="color:${{color}}">${{msg}}</span>`;
  box.appendChild(d); box.scrollTop=box.scrollHeight;
}}
function toggleAttack(){{
  isAttackOn=!isAttackOn;
  const s=document.getElementById('attackStatus'), btn=document.getElementById('sendBtn'), req=document.getElementById('reqBox');
  if(isAttackOn){{
    s.innerText='ON (Tampering...)'; s.style.color='#ff4444';
    req.value=ATTACK_REQ; req.style.color='#ff6b6b';
    btn.innerText='변조 요청 전송 (Execute)'; btn.classList.add('hacked');
    addLog('[ATTACK] 요청 데이터 변조 활성화', 'warn');
  }} else {{
    s.innerText='OFF'; s.style.color='#00ff00';
    req.value=NORMAL_REQ; req.style.color='#7ddcff';
    btn.innerText='요청 전송'; btn.classList.remove('hacked');
    addLog('[INFO] 공격 모드 해제', 'success');
  }}
}}
function sendRequest(){{
  const btn=document.getElementById('sendBtn'); btn.innerText='처리 중...';
  addLog('[REQUEST] 금융 거래 요청 수신');
  setTimeout(()=>{{
    if(isAttackOn){{ {vuln_logs} showBreach(); showCompliance(); }}
    else {{ addLog('[OK] 정상 거래 처리 완료', 'success'); showNormal(); }}
    btn.innerText = isAttackOn ? '변조 요청 전송 (Execute)' : '요청 전송';
  }}, 900);
}}
function showBreach(){{
  const c=document.getElementById('resultCard'); c.className='result-card result-breach'; c.style.display='block';
  c.innerHTML = {breach_html_js};
}}
function showNormal(){{
  const c=document.getElementById('resultCard'); c.className='result-card result-blocked'; c.style.display='block';
  c.innerHTML = '<strong>✅ 정상 거래</strong><br>요청이 검증을 통과하여 정상 처리되었습니다. (공격 모드를 켜고 변조를 시도해 보세요)';
}}
function showCompliance(){{
  document.getElementById('complianceReport').style.display='none';
  document.getElementById('violationAlert').style.display='block';
}}
function verifyCode(){{
  const code=document.getElementById('codeEditor').value.replace(/\s+/g,' ');
  const r=document.getElementById('codeResult');
  const ok=CHECKS.every(grp=>{{
    const pos=grp.filter(t=>!t.startsWith('!')), neg=grp.filter(t=>t.startsWith('!')).map(t=>t.slice(1));
    return (pos.length===0||pos.some(t=>code.includes(t.replace(/\s+/g,' ')))) && neg.every(t=>!code.includes(t.replace(/\s+/g,' ')));
  }});
  if(ok){{ r.innerHTML='<div style="background:#e8f5e9; color:#2e7d32; padding:12px; border-radius:6px; font-weight:bold;">✅ 보안 조치 완료 (Secure)<br><span style="font-size:12px; font-weight:normal;">{success_msg}</span></div>'; }}
  else {{ r.innerHTML='<div style="background:#ffebee; color:#c62828; padding:12px; border-radius:6px; font-weight:bold;">❌ 여전히 취약함 (Vulnerable)<br><span style="font-size:12px; font-weight:normal;">{fail_msg}</span></div>'; }}
}}
function showHint(){{ document.getElementById('codeEditor').value=SECURE_HINT; }}
</script>
</body>
</html>
'''


def jss(s):
    return '`' + s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${') + '`'


def jschecks(checks):
    return '[' + ', '.join('[' + ', '.join(jss(t) for t in g) + ']' for g in checks) + ']'


def esc(s):
    return html.escape(s, quote=False)


def render(s):
    return PAGE.format(
        title=esc(s['title']), icon=s['icon'], target=esc(s['target']), risk=s['risk'],
        item_code=esc(s['item_code']),
        attack_panel_title=esc(s['attack_panel_title']),
        scenario_html=s['scenario_html'],
        attack_name=esc(s['attack_name']), attack_sub=esc(s['attack_sub']),
        normal_req=esc(s['normal_req']), normal_req_js=jss(s['normal_req']),
        attack_req_js=jss(s['attack_req']),
        violations=''.join('<li>%s</li>' % esc(v) for v in s['violations']),
        defense_intro=s['defense_intro'],
        vuln_code=esc(s['vuln_code']),
        secure_hint_js=jss(s['secure_hint']),
        checks_js=jschecks(s['checks']),
        kisa_ref=s['kisa_ref'],
        vuln_logs=s['vuln_logs_js'],
        breach_html_js=jss(s['breach_html']),
        success_msg=esc(s['success_msg']), fail_msg=esc(s['fail_msg']),
    )


def main():
    from specs_fin import SPECS
    for s in SPECS:
        with open(os.path.join(OUT_DIR, s['file']), 'w', encoding='utf-8') as f:
            f.write(render(s))
        print('wrote', s['file'])
    print('TOTAL', len(SPECS))


if __name__ == '__main__':
    main()
