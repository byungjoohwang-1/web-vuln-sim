# -*- coding: utf-8 -*-
"""C/C++ 코딩 표준 레퍼런스 페이지 생성기 → public/coding-standards.html
대상: MISRA C:2012 / MISRA C++:2023 / CERT C / CERT C++ / AUTOSAR C++14
규칙 데이터는 표준별 모듈(std_*.py)의 RULES 리스트에서 임포트한다.
원문(규범 텍스트) 비복제 — 룰 ID·제목·분류 체계는 인용하되, 설명/예제는 자체 작성.
rule 스키마: {id, cat(분류/레벨), title(요약), bad, good, why}
"""
import html, os, importlib

OUT = os.path.join(os.path.dirname(__file__), '..', 'public')


def esc(s):
    return html.escape(s, quote=False)


def _rules(mod):
    return importlib.import_module(mod).RULES


STANDARDS = [
 {'key':'misrac','name':'MISRA C:2012','full':'Guidelines for the use of the C language in critical systems',
  'org':'MISRA Consortium (영국 자동차산업 SW신뢰성 협회)','basis':'C90/C99 (임베디드·안전필수 C)',
  'classes':['Directive(Dir) + Rule','Mandatory / Required / Advisory','Decidable / Undecidable','Single Translation Unit / System'],
  'note':'안전필수 임베디드 C의 사실상 표준. 규칙은 의무도(Mandatory>Required>Advisory)와 정적분석 결정가능성(Decidable/Undecidable)으로 분류된다. Amendment로 동시성(Rule 22)·generic(Rule 23) 등이 추가되었다.',
  'mod':'std_misrac'},
 {'key':'misracpp','name':'MISRA C++:2023','full':'Guidelines for the use of C++17 in critical systems',
  'org':'MISRA Consortium','basis':'C++17 (구 MISRA C++:2008 + AUTOSAR C++14 통합)',
  'classes':['Mandatory / Required / Advisory','Decidable / Undecidable','Single Translation Unit / System'],
  'note':'AUTOSAR C++14 가이드라인을 흡수해 C++17 기준으로 재편한 최신 표준. 룰 번호는 "Rule 섹션.그룹.번호"(예: Rule 0.1.2) 형식이다.',
  'mod':'std_misracpp'},
 {'key':'certc','name':'CERT C','full':'SEI CERT C Coding Standard',
  'org':'SEI / Carnegie Mellon University','basis':'보안 중심 C (취약점 예방)',
  'classes':['Rules(규칙) / Recommendations(권고)','Severity × Likelihood × Remediation → Priority','Level L1 / L2 / L3','섹션: PRE·DCL·EXP·INT·FLP·ARR·STR·MEM·FIO·ENV·SIG·ERR·CON·MSC·POS·WIN'],
  'note':'보안 취약점 예방에 초점을 둔 코딩 표준. 각 규칙은 심각도·발생가능성·수정비용을 곱한 우선순위(1~27)와 레벨(L1~L3)을 가진다. 규칙 ID는 "섹션+번호-C"(예: INT30-C).',
  'mod':'std_certc'},
 {'key':'certcpp','name':'CERT C++','full':'SEI CERT C++ Coding Standard',
  'org':'SEI / Carnegie Mellon University','basis':'보안 중심 C++',
  'classes':['Rules / Recommendations','Severity × Likelihood × Remediation → Priority/Level','섹션: DCL·EXP·INT·CTR·STR·MEM·OOP·ERR·CON·OBJ'],
  'note':'CERT C의 C++ 판으로, RAII·예외·객체수명 등 C++ 고유 위험을 다룬다. 규칙 ID는 "섹션+번호-CPP"(예: MEM50-CPP).',
  'mod':'std_certcpp'},
 {'key':'autosar','name':'AUTOSAR C++14','full':'Guidelines for the use of the C++14 language in critical and safety-related systems',
  'org':'AUTOSAR (자동차 SW 아키텍처 컨소시엄)','basis':'C++14 (Adaptive Platform). MISRA C++:2023에 통합·승계됨',
  'classes':['Required / Advisory','Automated / Non-automated(정적분석 가능 여부)','A###(AUTOSAR 신규) / M###(MISRA C++:2008 유래)'],
  'note':'자동차 안전필수 C++14 가이드라인. 규칙 ID는 A0-1-1·M0-1-1 형식이며, A=AUTOSAR 신규·M=MISRA 유래다. 현재는 MISRA C++:2023이 이를 승계한다.',
  'mod':'std_autosar'},
]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0b1220;--card:#fff;--primary:#0ea5e9;--ink:#1e293b;--muted:#64748b;--border:#e2e8f0;--bad:#ef4444;--good:#22c55e}
body{font-family:'Segoe UI','Malgun Gothic',sans-serif;background:linear-gradient(135deg,#0f172a,#1e3a8a);min-height:100vh;color:var(--ink);padding:0 0 50px}
.top{background:#0b1220;padding:10px 22px}.top a{color:#7dd3fc;text-decoration:none;font-size:13px;font-family:'JetBrains Mono',monospace}
.hero{color:#fff;text-align:center;padding:34px 18px 26px}
.hero h1{font-size:27px;margin-bottom:8px}.hero p{opacity:.9;font-size:14px;max-width:760px;margin:0 auto;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
.tabs{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:8px 0 18px}
.tabs button{border:none;cursor:pointer;font-weight:700;font-size:13.5px;padding:10px 16px;border-radius:10px;background:rgba(255,255,255,.14);color:#e2e8f0;font-family:inherit}
.tabs button.on{background:#fff;color:#0c4a6e}
.panel{display:none}.panel.on{display:block}
.ov{background:#fff;border-radius:14px;padding:20px 22px;margin-bottom:16px;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.ov h2{font-size:20px;color:#0c4a6e}.ov .full{color:var(--muted);font-size:13px;margin:3px 0 12px;font-style:italic}
.ov .meta{font-size:13.5px;line-height:1.8}.ov .meta b{color:#0369a1}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0 6px}
.chip{background:#f0f9ff;border:1px solid #bae6fd;color:#075985;border-radius:20px;padding:5px 12px;font-size:12px;font-weight:600}
.ov .note{margin-top:12px;font-size:13.5px;line-height:1.7;color:#334155;background:#f8fafc;border-left:4px solid var(--primary);padding:12px 14px;border-radius:8px}
.cnt{font-size:12.5px;color:var(--muted);margin:2px 0 14px;font-weight:600}
.filter{margin:0 0 14px}.filter input{width:100%;max-width:420px;padding:10px 13px;border:1px solid var(--border);border-radius:10px;font-size:14px}
.card{background:#fff;border-radius:14px;padding:18px 20px;margin-bottom:14px;box-shadow:0 8px 24px rgba(0,0,0,.14)}
.card .rid{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-bottom:6px}
.rid .id{font-family:'JetBrains Mono',monospace;font-weight:700;background:#0b1220;color:#7dd3fc;padding:4px 11px;border-radius:8px;font-size:13px}
.rid .cat{font-size:11.5px;font-weight:700;color:#7c3aed;background:#f3e8ff;border-radius:20px;padding:3px 10px}
.card h3{font-size:15.5px;color:var(--ink);margin:2px 0 12px;line-height:1.5}
.sw{display:flex;gap:5px;background:#0b1220;border-radius:9px;padding:4px;width:fit-content;margin-bottom:10px}
.sw button{border:none;background:transparent;color:#94a3b8;font-weight:700;font-size:12.5px;padding:7px 14px;border-radius:7px;cursor:pointer;font-family:inherit}
.sw button.on.bad{background:var(--bad);color:#fff}.sw button.on.good{background:var(--good);color:#fff}
.pane{display:none}.pane.show{display:block}
.chdr{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:12px;padding:8px 13px;border-radius:9px 9px 0 0;color:#fff}
.chdr.bad{background:var(--bad)}.chdr.good{background:var(--good)}
pre{background:var(--bg);color:#e2e8f0;padding:15px 16px;border-radius:0 0 9px 9px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:12.5px;line-height:1.65;white-space:pre}
.why{margin-top:11px;background:#fffbeb;border-left:4px solid #f59e0b;border-radius:8px;padding:11px 14px;font-size:13.5px;line-height:1.7;color:#78350f}
.foot{text-align:center;color:#cbd5e1;font-size:12px;margin-top:18px;line-height:1.7}
.sw button.prac{background:transparent;color:#a5b4fc;font-weight:700}.sw button.prac:hover{color:#fff}
/* ===== 연습 IDE 패널 ===== */
.ide{position:fixed;left:0;right:0;bottom:0;height:72vh;background:#0b1220;border-top:2px solid #6366f1;box-shadow:0 -10px 40px rgba(0,0,0,.5);display:none;flex-direction:column;z-index:9999}
.ide.on{display:flex}
.ide-bar{display:flex;align-items:center;gap:8px;padding:8px 12px;background:#111a2e;border-bottom:1px solid #1e293b}
.ide-bar .ide-title{color:#c7d2fe;font-weight:700;font-size:13.5px;margin-right:auto}
.ide-bar select,.ide-bar button{font-family:'JetBrains Mono',monospace;font-size:12.5px;font-weight:700;border:none;border-radius:8px;padding:7px 12px;cursor:pointer;background:#1e293b;color:#cbd5e1}
.ide-bar button.run{background:#22c55e;color:#06210f}.ide-bar button.run:hover{background:#16a34a}
.ide-bar button.x{background:#334155}
.ide-body{flex:1;display:flex;min-height:0}
.ide-ed{flex:1;min-width:0}
.ide-out{width:38%;max-width:460px;display:flex;flex-direction:column;border-left:1px solid #1e293b;background:#0b1220}
.ide-outhdr{padding:7px 12px;font-size:11.5px;font-weight:700;color:#94a3b8;background:#111a2e;border-bottom:1px solid #1e293b}
.ide-out pre{flex:1;margin:0;border-radius:0;background:#0b1220;color:#e2e8f0;font-size:12px;white-space:pre-wrap;overflow:auto;padding:12px}
.ide-note{font-size:11px;color:#94a3b8;padding:6px 12px;background:#111a2e;border-top:1px solid #1e293b}
@media(max-width:768px){.hero h1{font-size:21px}.tabs button{font-size:12.5px;padding:9px 12px}.ov,.card{padding:15px 14px}pre{font-size:11.5px}
.ide{height:84vh}.ide-body{flex-direction:column}.ide-out{width:100%;max-width:none;border-left:none;border-top:1px solid #1e293b;height:34%}}
"""


def render_card(sk, i, r, lang):
    cid = sk + str(i)
    blob = esc((r['id'] + ' ' + r['title'] + ' ' + r.get('cat', '')))
    return (
      '<div class="card" data-s="' + blob + '">'
      '<div class="rid"><span class="id">' + esc(r['id']) + '</span><span class="cat">' + esc(r['cat']) + '</span></div>'
      '<h3>' + esc(r['title']) + '</h3>'
      '<div class="sw"><button class="on bad" onclick="sw(\'' + cid + '\',0)">❌ 위반(non-compliant)</button>'
      '<button class="good" onclick="sw(\'' + cid + '\',1)">✅ 준수(compliant)</button>'
      '<button class="prac" onclick="practice(\'' + cid + '\',\'' + lang + '\')">🧪 IDE에서 연습</button></div>'
      '<div class="pane show" id="' + cid + 'b"><div class="chdr bad">❌ 위반 예시</div><pre>' + esc(r['bad']) + '</pre></div>'
      '<div class="pane" id="' + cid + 'g"><div class="chdr good">✅ 준수 예시</div><pre>' + esc(r['good']) + '</pre></div>'
      '<div class="why">⚠️ ' + esc(r['why']) + '</div>'
      '</div>')


def render_panel(s, active):
    rules = s['rules']
    chips = ''.join('<span class="chip">' + esc(c) + '</span>' for c in s['classes'])
    cards = ''.join(render_card(s['key'], i, r, s['lang']) for i, r in enumerate(rules))
    return (
      '<div class="panel' + (' on' if active else '') + '" id="p_' + s['key'] + '">'
      '<div class="ov"><h2>' + esc(s['name']) + '</h2><div class="full">' + esc(s['full']) + '</div>'
      '<div class="meta"><b>제정/관리:</b> ' + esc(s['org']) + '<br><b>대상:</b> ' + esc(s['basis']) + '</div>'
      '<div class="chips">' + chips + '</div>'
      '<div class="note">' + esc(s['note']) + '</div></div>'
      '<div class="cnt">대표 규칙 ' + str(len(rules)) + '종</div>'
      '<div class="filter"><input type="text" placeholder="🔎 이 표준 내 규칙 검색 (ID·제목)" oninput="flt(\'' + s['key'] + '\',this.value)"></div>'
      + cards + '</div>')


LANG = {'misrac': 'c', 'certc': 'c', 'misracpp': 'cpp', 'certcpp': 'cpp', 'autosar': 'cpp'}


def build():
    for s in STANDARDS:
        s['rules'] = _rules(s['mod'])
        s['lang'] = LANG[s['key']]
    tabs = ''.join('<button class="' + ('on' if i == 0 else '') + '" onclick="tab(\'' + s['key'] + '\')">' + esc(s['name']) + ' (' + str(len(s['rules'])) + ')</button>'
                   for i, s in enumerate(STANDARDS))
    panels = ''.join(render_panel(s, i == 0) for i, s in enumerate(STANDARDS))
    total = sum(len(s['rules']) for s in STANDARDS)
    html_doc = (
      '<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">'
      '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
      '<title>C/C++ 코딩 표준 — MISRA · CERT · AUTOSAR</title>'
      '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">'
      '<style>' + CSS + '</style></head><body>'
      '<div class="top"><a href="index.html">← 홈</a> &nbsp;·&nbsp; <a href="vuln-hub.html">취약점 학습 허브</a></div>'
      '<div class="hero"><h1>🛠️ C/C++ 코딩 표준 레퍼런스</h1>'
      '<p>임베디드·안전필수·보안 C/C++ 5대 코딩 표준의 분류 체계와 규칙을 위반/준수 예제로 비교합니다. '
      '(규칙 ID·제목·분류는 각 표준 인용, 설명·예제는 교육용 자체 작성 — 규범 원문 비복제)</p></div>'
      '<div class="wrap"><div class="tabs">' + tabs + '</div>' + panels +
      '<div class="foot">MISRA C:2012 · MISRA C++:2023 · CERT C · CERT C++ · AUTOSAR C++14 &nbsp;|&nbsp; 대표 규칙 ' + str(total) + '종 · 사내 교육용<br>'
      '규칙 ID·제목·분류는 각 표준(및 CERT 공식 사이트) 대조 인용, 코드 예제와 해설은 직접 작성. '
      '🧪 연습 IDE는 Wandbox(원격 gcc 컴파일) 기반 — C/C++ 코드를 편집해 바로 실행해볼 수 있습니다.</div></div>'
      # ===== 연습 IDE 패널 =====
      '<div class="ide" id="ide">'
      '<div class="ide-bar"><span class="ide-title">🧪 연습 IDE</span>'
      '<select id="ideLang" onchange="setLang(this.value)"><option value="c">C</option><option value="cpp">C++</option></select>'
      '<button onclick="wrapMain()">main 스캐폴드</button>'
      '<button onclick="resetIde()">예제 다시 불러오기</button>'
      '<button class="run" onclick="runCode()">▶ 실행</button>'
      '<button class="x" onclick="closeIde()">✕ 닫기</button></div>'
      '<div class="ide-body"><div class="ide-ed" id="ideEd"></div>'
      '<div class="ide-out"><div class="ide-outhdr">실행 결과 (원격 컴파일·실행)</div><pre id="ideOut">▶ 실행을 눌러 컴파일·실행하세요.</pre></div></div>'
      '<div class="ide-note">⚠️ 예시는 규칙 설명용 스니펫이라 헤더·main·호출부 보완이 필요할 수 있습니다. \'main 스캐폴드\' 버튼으로 기본 골격을 감싼 뒤 편집해 실행하세요.</div>'
      '</div>'
      '<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>'
      '<script>'
      'function tab(k){document.querySelectorAll(".tabs button").forEach(b=>b.classList.toggle("on",b.getAttribute("onclick").indexOf("\'"+k+"\'")>=0));'
      'document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("on",p.id==="p_"+k));window.scrollTo(0,0);}'
      'function sw(id,good){document.getElementById(id+"b").classList.toggle("show",!good);'
      'document.getElementById(id+"g").classList.toggle("show",!!good);'
      'var bt=event.currentTarget.parentNode.children;bt[0].classList.toggle("on",!good);bt[1].classList.toggle("on",!!good);}'
      'function flt(k,q){q=q.toLowerCase();document.querySelectorAll("#p_"+k+" .card").forEach(c=>{'
      'c.style.display=(c.getAttribute("data-s")||"").toLowerCase().indexOf(q)>=0?"":"none";});}'
      # ===== IDE 로직 =====
      'var ed=null,curLang="c",seed="";'
      'function ensureMonaco(cb){if(window.monaco&&ed){cb();return;}'
      'require.config({paths:{vs:"https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"}});'
      'require(["vs/editor/editor.main"],function(){if(!ed){ed=monaco.editor.create(document.getElementById("ideEd"),'
      '{value:"",language:"cpp",theme:"vs-dark",fontSize:13,minimap:{enabled:false},automaticLayout:true,scrollBeyondLastLine:false});}cb();});}'
      'function practice(cid,lang){var pre=document.querySelector("#"+cid+"g pre")||document.querySelector("#"+cid+"b pre");'
      'seed=pre?pre.textContent:"";curLang=lang;document.getElementById("ideLang").value=lang;'
      'document.getElementById("ide").classList.add("on");document.getElementById("ideOut").textContent="▶ 실행을 눌러 컴파일·실행하세요.";'
      'ensureMonaco(function(){monaco.editor.setModelLanguage(ed.getModel(),lang==="c"?"c":"cpp");ed.setValue(seed);ed.layout();});}'
      'function setLang(v){curLang=v;if(ed)monaco.editor.setModelLanguage(ed.getModel(),v==="c"?"c":"cpp");}'
      'function resetIde(){if(ed)ed.setValue(seed);}'
      'function closeIde(){document.getElementById("ide").classList.remove("on");}'
      'function wrapMain(){if(!ed)return;var c=ed.getValue();if(c.indexOf("int main")>=0)return;'
      'var inc=curLang==="c"?"#include <stdio.h>\\n#include <stdlib.h>\\n#include <string.h>\\n":'
      '"#include <iostream>\\n#include <vector>\\n#include <string>\\n#include <memory>\\nusing namespace std;\\n";'
      'ed.setValue(inc+"\\n"+c+"\\n\\nint main(void){\\n    // TODO: 위 코드를 호출해보세요\\n    return 0;\\n}\\n");}'
      'function runCode(){if(!ed){return;}var code=ed.getValue();'
      'var comp=curLang==="c"?"gcc-13.2.0-c":"gcc-13.2.0";'
      'var out=document.getElementById("ideOut");out.textContent="⏳ 원격 컴파일·실행 중... (Wandbox)";'
      'fetch("https://wandbox.org/api/compile.json",{method:"POST",headers:{"Content-Type":"application/json"},'
      'body:JSON.stringify({code:code,compiler:comp,options:"warning",stdin:""})})'
      '.then(r=>r.json()).then(function(j){var t="";'
      'if(j.compiler_error)t+="[컴파일 오류]\\n"+j.compiler_error+"\\n";'
      'if(j.program_output)t+=j.program_output;'
      'if(j.program_error)t+="\\n[stderr]\\n"+j.program_error;'
      'out.textContent=t.trim()||"(출력 없음 · status "+(j.status||"?")+")";})'
      '.catch(function(e){out.textContent="🚫 실행 오류: "+e+"\\n(네트워크/CORS 문제일 수 있습니다)";});}'
      '</script></body></html>')
    open(os.path.join(OUT, 'coding-standards.html'), 'w', encoding='utf-8').write(html_doc)
    print('wrote coding-standards.html | standards=%d rules=%d' % (len(STANDARDS), total))


if __name__ == '__main__':
    build()
