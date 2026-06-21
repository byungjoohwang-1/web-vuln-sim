# -*- coding: utf-8 -*-
"""보안약점 진단원 학습 센터(secure-dev-academy.html) 생성기 — 실무 대비 고도화판.
모드: 대시보드 / 개념학습(49) / 플래시카드 / 1교시 이론(MC·OX·단답) / 2교시 실무(정·오탐 판별+서술형 채점) / 오답노트.
진도·오답·최고점 localStorage 저장.
데이터: CONCEPTS·CODEPROBS=specs_academy, QUIZ=기존 BANK, PRACTICAL·THEORY=specs_academy_practical."""
import json, os, re, importlib

OUT = os.path.join(os.path.dirname(__file__), '..', 'public')


def get_quiz_bank():
    h = open(os.path.join(OUT, 'secure-dev-quiz.html'), encoding='utf-8').read()
    m = re.search(r'const BANK\s*=\s*(\[.*?\n\]);', h, re.S)
    return m.group(1)


TPL = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="KISA 소프트웨어 보안약점 진단원 이수시험(1교시 이론·2교시 실무) 대비 학습 센터 — 49개 보안약점 개념, 정·오탐 판별 서술형 실무, OX·단답 이론, 모의고사, 오답노트.">
<title>보안약점 진단원 학습 센터 | 1교시 이론 · 2교시 실무</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lora:wght@600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--p:#6366f1;--p2:#8b5cf6;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0;--ok:#22c55e;--no:#ef4444;--warn:#f59e0b;--bg:#f1f5f9}
body{font-family:'Lora',serif;background:var(--bg);color:var(--ink);line-height:1.6;min-height:100vh}
a{text-decoration:none;color:inherit}
.top{background:#0b1020;padding:9px 0}.top .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.top a{color:#a5b4fc;font-family:'JetBrains Mono',monospace;font-size:13px}
.hero{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:34px 0 24px}
.hero .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.hero h1{font-size:27px;margin-bottom:4px}.hero p{opacity:.9;font-size:14px}
.tabs{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20;box-shadow:0 2px 10px rgba(2,6,23,.05)}
.tabs .wrap{max-width:1180px;margin:0 auto;padding:0 12px;display:flex;gap:4px;overflow-x:auto}
.tab{border:none;background:transparent;padding:15px 14px;font-family:'Lora',serif;font-weight:700;font-size:14px;color:var(--muted);cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap;transition:.15s}
.tab:hover{color:var(--p)} .tab.on{color:var(--p);border-bottom-color:var(--p)}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.view{display:none;padding:30px 0 60px}.view.on{display:block}
h2.st{font-size:23px;margin-bottom:6px}.sub{color:var(--muted);font-size:14px;margin-bottom:22px}
.dgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-bottom:26px}
.dcard{background:#fff;border:1px solid var(--line);border-radius:16px;padding:20px;text-align:center;box-shadow:0 6px 18px rgba(2,6,23,.05)}
.dcard b{display:block;font-size:30px;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.dcard span{font-size:12.5px;color:var(--muted)}
.prog-wrap{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 26px;margin-bottom:22px}
.prog-wrap h3{font-size:17px;margin-bottom:16px}
.prow{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.prow .nm{width:130px;font-size:14px;font-weight:700}
.prow .bar{flex:1;height:12px;background:#eef2ff;border-radius:10px;overflow:hidden}.prow .bar>i{display:block;height:100%;border-radius:10px}
.prow .vv{width:54px;text-align:right;font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--muted)}
.quick{display:flex;gap:10px;flex-wrap:wrap}
.qbtn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;padding:12px 20px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:14px;cursor:pointer;transition:.2s}
.qbtn:hover{transform:translateY(-2px)} .qbtn.ghost{background:#fff;color:var(--p);border:1.5px solid var(--p)}
.reset{background:none;border:1px solid var(--line);color:var(--muted);padding:8px 16px;border-radius:20px;font-size:12.5px;cursor:pointer;margin-top:18px}
.catbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.cchip{border:1.5px solid var(--line);background:#fff;border-radius:20px;padding:7px 15px;font-family:'Lora',serif;font-size:13.5px;font-weight:700;cursor:pointer;transition:.15s}
.cchip:hover{border-color:var(--p)} .cchip.on{background:var(--p);color:#fff;border-color:var(--p)}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.ccard{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;transition:.2s}
.ccard.done{border-color:#bbf7d0;box-shadow:0 0 0 2px #dcfce7 inset}
.ccard .ch{padding:15px 18px;cursor:pointer;display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.ccard .ch h4{font-size:15.5px;line-height:1.4}.ccard .ch .cwe{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);margin-top:3px}
.ccard .badge{font-size:10.5px;color:#fff;border-radius:20px;padding:2px 9px;white-space:nowrap;font-family:'JetBrains Mono',monospace}
.ccard .detail{display:none;padding:0 18px 16px;border-top:1px solid var(--line)}.ccard.open .detail{display:block}
.ccard.open{grid-column:1/-1}
.ccard .fld{margin-top:12px}.ccard .fld .lb{font-size:12px;font-weight:700;color:var(--p);margin-bottom:3px}.ccard .fld .tx{font-size:14px;color:#334155;line-height:1.65}
.ccard .done-btn{margin-top:14px;width:100%;border:1.5px solid var(--ok);background:#fff;color:#16a34a;padding:9px;border-radius:10px;font-family:'Lora',serif;font-weight:700;cursor:pointer;font-size:13.5px}
.ccard.done .done-btn{background:var(--ok);color:#fff}
.ccard .simlink{display:inline-block;margin-top:10px;font-size:12.5px;color:var(--p);font-weight:700}
.lgtabs{display:flex;gap:6px;margin:8px 0 0}
.lgtab{border:1.5px solid var(--line);border-bottom:none;background:#fff;border-radius:9px 9px 0 0;padding:7px 13px;font-family:'Lora',serif;font-weight:700;font-size:12.5px;cursor:pointer;color:var(--muted)}
.lgtab.on{background:var(--p);color:#fff;border-color:var(--p)}
.codepair{display:grid;grid-template-columns:1fr 1fr;gap:10px;border:1px solid var(--line);border-radius:0 10px 10px 10px;padding:10px;min-width:0}
@media(max-width:820px){.codepair{grid-template-columns:1fr}}
.cp{min-width:0;display:flex;flex-direction:column}
.cp .cph{font-size:12px;font-weight:700;padding:5px 9px;border-radius:7px 7px 0 0}
.cph.bad{background:#fef2f2;color:#b91c1c}.cph.good{background:#f0fdf4;color:#15803d}
.cpre{background:#0b1020;color:#e2e8f0;padding:11px 13px;border-radius:0 0 8px 8px;overflow-x:auto;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:12px;line-height:1.6;white-space:pre;margin:0;max-height:360px;min-width:0;max-width:100%}
.cnote{font-size:12px;color:var(--muted);margin-top:8px;background:#f8fafc;border:1px dashed var(--line);border-radius:8px;padding:8px 10px}
.csrc{font-size:11px;color:var(--muted);margin-top:4px}
.flash-stage{max-width:560px;margin:0 auto;text-align:center}
.fcard{background:#fff;border:1px solid var(--line);border-radius:20px;min-height:240px;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:34px;cursor:pointer;box-shadow:0 12px 34px rgba(2,6,23,.1);transition:.2s}
.fcard:hover{transform:translateY(-3px)} .fcard .face-cat{font-size:12px;color:#fff;border-radius:20px;padding:3px 12px;margin-bottom:14px;font-family:'JetBrains Mono',monospace}
.fcard .fr{font-size:24px;font-weight:800}.fcard .hint{margin-top:16px;font-size:12.5px;color:var(--muted)}
.fcard .bk{font-size:15px;color:#334155;line-height:1.7;text-align:left}.fcard .bk b{color:var(--p)}
.frow{display:flex;gap:10px;justify-content:center;margin-top:18px}
.frow button{border:none;padding:13px 30px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:15px;cursor:pointer;transition:.2s}
.f-no{background:#fef2f2;color:#dc2626;border:1.5px solid #fecaca!important}.f-ok{background:#f0fdf4;color:#16a34a;border:1.5px solid #bbf7d0!important}
.fmeta{text-align:center;color:var(--muted);font-size:13px;margin-bottom:14px;font-family:'JetBrains Mono',monospace}
.setbox{background:#fff;border:1px solid var(--line);border-radius:16px;padding:26px;max-width:640px;margin:0 auto;text-align:center}
.setbox h3{font-size:19px;margin-bottom:8px}.setbox p{color:var(--muted);font-size:14px;margin-bottom:18px}
.setrow{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:16px}
.opt{text-align:left;border:1.5px solid var(--line);border-radius:12px;padding:13px 16px;cursor:pointer;font-family:'Lora',serif;font-size:15px;background:#fff;transition:.15s;display:flex;gap:10px;width:100%;margin-bottom:9px}
.opt:hover:not(:disabled){border-color:var(--p);background:#f5f7ff}.opt .lab{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--p)}
.opt.sel{border-color:var(--p);background:#eef2ff}.opt:disabled{cursor:default}
.opt.correct{border-color:var(--ok);background:#f0fdf4}.opt.correct .lab{color:var(--ok)}
.opt.wrong{border-color:var(--no);background:#fef2f2}.opt.wrong .lab{color:var(--no)}
.qbox{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 26px;max-width:820px;margin:0 auto}
.bar2{height:8px;background:#eef2ff;border-radius:10px;overflow:hidden;margin-bottom:6px}.bar2>i{display:block;height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6);width:0;transition:.3s}
.qmeta{display:flex;justify-content:space-between;font-size:13px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-bottom:14px}
.timer{font-weight:700}.timer.warn{color:var(--no)}
.qtext{font-size:17px;font-weight:700;line-height:1.55;margin-bottom:14px}
.typetag{display:inline-block;font-size:11px;font-weight:700;color:#fff;border-radius:6px;padding:2px 8px;margin-right:8px;font-family:'JetBrains Mono',monospace}
.t-MC{background:#6366f1}.t-OX{background:#0ea5e9}.t-SHORT{background:#f59e0b}.t-PRAC{background:#7c3aed}
pre{background:#0b1020;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.7;margin-bottom:14px;white-space:pre}
.ln{color:#475569;user-select:none}
.cat-tag{display:inline-block;font-size:12px;color:#4338ca;background:#eef2ff;border:1px solid #c7d2fe;border-radius:20px;padding:3px 12px;margin-bottom:12px}
.exp{margin-top:14px;border-radius:12px;padding:14px 16px;font-size:14px;line-height:1.65;display:none}.exp.show{display:block}
.exp.ok{background:#f0fdf4;border-left:4px solid var(--ok)}.exp.no{background:#fef2f2;border-left:4px solid var(--no)}
.nav{margin-top:18px;text-align:right}
.btn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;padding:12px 26px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:15px;cursor:pointer;transition:.2s}
.btn:hover{transform:translateY(-2px)} .btn.ghost{background:#fff;color:var(--p);border:1.5px solid var(--p)}
.shortin{width:100%;border:1.5px solid var(--line);border-radius:10px;padding:13px 15px;font-family:'Lora',serif;font-size:15px}
.shortin:focus{outline:none;border-color:var(--p)}
/* 실무(2교시) */
.tfrow{display:flex;gap:12px;margin-bottom:16px;flex-wrap:wrap}
.tf{flex:1;min-width:200px;border:2px solid var(--line);border-radius:12px;padding:14px 16px;cursor:pointer;font-weight:700;transition:.15s;display:flex;align-items:center;gap:10px}
.tf:hover{border-color:var(--p)} .tf.sel.tp{border-color:var(--no);background:#fef2f2;color:#b91c1c} .tf.sel.fp{border-color:var(--ok);background:#f0fdf4;color:#15803d}
.tf .rd{width:18px;height:18px;border-radius:50%;border:2px solid currentColor;flex-shrink:0}
.flbl{font-size:13px;font-weight:700;color:var(--p);margin:14px 0 6px}
.parea{width:100%;border:1.5px solid var(--line);border-radius:10px;padding:12px 14px;font-family:'Lora',serif;font-size:14px;line-height:1.6;resize:vertical;min-height:74px}
.parea:focus{outline:none;border-color:var(--p)}
.parea:disabled,.pin:disabled{background:#f8fafc;color:#94a3b8}
.pin{width:100%;border:1.5px solid var(--line);border-radius:10px;padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:14px}
.pin:focus{outline:none;border-color:var(--p)}
.codearea{width:100%;border:1.5px solid var(--line);border-radius:10px;padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;resize:vertical;min-height:120px;background:#0b1020;color:#e2e8f0}
.codearea:focus{outline:none;border-color:var(--p)}
.report{margin-top:16px;background:#fafbff;border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.scoreline{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.scoreline .num{font-size:38px;font-weight:800;font-family:'JetBrains Mono',monospace}
.pass{color:#16a34a}.fail{color:#dc2626}
.prow2{display:flex;align-items:center;gap:10px;margin-bottom:8px;font-size:13.5px}
.prow2 .l{width:120px;font-weight:700}.prow2 .bar{flex:1;height:9px;background:#eef2ff;border-radius:8px;overflow:hidden}.prow2 .bar>i{display:block;height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6)}
.prow2 .g{width:60px;text-align:right;font-family:'JetBrains Mono',monospace;color:var(--muted)}
.model{margin-top:14px;border-top:1px dashed var(--line);padding-top:14px}
.model h4{font-size:14px;color:var(--p2);margin-bottom:8px}
.kw{display:inline-block;background:#eef2ff;color:#4338ca;border:1px solid #c7d2fe;border-radius:14px;padding:2px 10px;font-size:12px;margin:2px 3px;font-family:'JetBrains Mono',monospace}
.kw.hit{background:#dcfce7;color:#15803d;border-color:#bbf7d0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:10px;min-width:0}@media(max-width:740px){.two{grid-template-columns:1fr}}
.two .pane{min-width:0}.two .pane pre{overflow-x:auto;max-width:100%;white-space:pre}
.two .pane h5{font-size:12px;color:var(--muted);margin-bottom:5px;font-family:'JetBrains Mono',monospace}
.diffpre{background:#0b1020;border-radius:10px;padding:12px 14px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.7;margin:0;white-space:pre}
.diffpre .d-del{display:block;background:rgba(239,68,68,.16);color:#fca5a5}
.diffpre .d-add{display:block;background:rgba(34,197,94,.16);color:#86efac}
.diffpre .d-ctx{display:block;color:#94a3b8}
.penline{color:#dc2626;font-weight:700}
.neg-kw{display:inline-block;background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;border-radius:14px;padding:2px 10px;font-size:12px;margin:2px 3px;font-family:'JetBrains Mono',monospace}
.res{text-align:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:34px;max-width:740px;margin:0 auto}
.res .big{font-size:56px;font-weight:800;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.res .pf{font-size:22px;font-weight:800;margin:4px 0}
.wlist{display:flex;flex-direction:column;gap:12px}
.witem{background:#fff;border:1px solid var(--line);border-left:4px solid var(--no);border-radius:12px;padding:16px 18px}
.witem .wq{font-weight:700;margin-bottom:6px;font-size:14.5px}.witem .wa{color:#16a34a;font-size:13.5px;margin-bottom:4px}.witem .we{color:#475569;font-size:13.5px}
.witem .del{float:right;border:none;background:#fef2f2;color:#dc2626;border-radius:8px;padding:4px 10px;font-size:12px;cursor:pointer}
.empty{text-align:center;color:var(--muted);padding:50px 0;font-size:15px}
@media(max-width:760px){.cgrid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="top"><div class="wrap"><a href="secure-dev-portal.html">&larr; 개발보안 학습 포털</a> &nbsp;·&nbsp; <a href="index.html">홈</a></div></div>
<div class="hero"><div class="wrap"><h1>🎓 보안약점 진단원 학습 센터</h1><p>개념 학습 · 플래시카드 · 1교시 이론(객관식·OX·단답) · 2교시 실무(정·오탐 판별 + 서술형 채점) · 오답노트 — 진도 자동 저장</p></div></div>
<div class="tabs"><div class="wrap">
  <button class="tab on" data-v="dash" onclick="tab('dash')">📊 대시보드</button>
  <button class="tab" data-v="learn" onclick="tab('learn')">📖 개념학습</button>
  <button class="tab" data-v="flash" onclick="tab('flash')">🃏 플래시카드</button>
  <button class="tab" data-v="exam" onclick="tab('exam')">📝 1교시 이론</button>
  <button class="tab" data-v="prac" onclick="tab('prac')">🧪 2교시 실무</button>
  <button class="tab" data-v="wrong" onclick="tab('wrong')">❌ 오답노트</button>
</div></div>
<div class="wrap">
  <div class="view on" id="v-dash"></div>
  <div class="view" id="v-learn"></div>
  <div class="view" id="v-flash"></div>
  <div class="view" id="v-exam"></div>
  <div class="view" id="v-prac"></div>
  <div class="view" id="v-wrong"></div>
</div>
<datalist id="kisa49"></datalist>

<script>
const CONCEPTS = __CONCEPTS__;
const QUIZ = __QUIZ__;
const PRACTICAL = __PRACTICAL__;
const THEORY = __THEORY__;
const CODE49 = __CODE49__;
const KISA49 = CONCEPTS.map(c=>c.name);
const CATS = ['입력검증','보안기능','시간상태','에러처리','코드오류','캡슐화','API오용'];
const CCOLOR = {'입력검증':'#6366f1','보안기능':'#0ea5e9','시간상태':'#14b8a6','에러처리':'#f59e0b','코드오류':'#ef4444','캡슐화':'#8b5cf6','API오용':'#64748b'};
// 개념→대표 시뮬레이터 매핑(있으면 링크)
const SIMMAP={'SQL 삽입':'03_code_sql_injection.html','코드 삽입':'03_code_codeinjection.html','경로 조작 및 자원 삽입':'03_code_path_traversal.html','크로스사이트 스크립트(XSS)':'03_code_xss.html','운영체제 명령어 삽입':'03_code_os_command.html','위험한 형식 파일 업로드':'03_code_dangerous_file_upload.html','신뢰되지 않는 URL 주소로 자동접속 연결':'03_code_open_redirect.html','XML 외부 개체(XXE)':'03_code_xxe.html','XML 삽입':'03_code_xml.html','LDAP 삽입':'03_code_ldap_injection.html','크로스사이트 요청 위조(CSRF)':'03_code_csrf.html','서버사이드 요청 위조(SSRF)':'03_code_ssrf.html','HTTP 응답 분할':'03_code_http_split.html','정수형 오버플로우':'03_code_integer_overflow.html','메모리 버퍼 오버플로우':'03_code_bufferoverflow.html','적절한 인증 없는 중요기능 허용':'03_code_missing_auth.html','부적절한 인가':'03_code_inapporiate_auth.html','취약한 암호화 알고리즘 사용':'03_code_risky_crypto.html','하드코드된 중요정보':'03_code_hardedcode.html','적절하지 않은 난수값 사용':'03_code_useofinsufficient_random.html','취약한 비밀번호 허용':'03_code_weakpassword.html','솔트 없이 일방향 해시함수 사용':'03_code_nosalthash.html','경쟁조건: 검사시점과 사용시점(TOCTOU)':'03_code_race_condition.html','오류 메시지 정보 노출':'03_code_error_message.html','부적절한 예외 처리':'03_code_improper_exception.html','Null Pointer 역참조':'03_code_null_pointer.html','부적절한 자원 해제':'03_code_improper_resource_release.html','해제된 자원 사용':'03_code_use_after_free.html','초기화되지 않은 변수 사용':'03_code_uninitialized_variable.html','신뢰할 수 없는 데이터의 역직렬화':'03_code_deserialization.html','제거되지 않고 남은 디버그 코드':'03_code_debug_code.html','DNS lookup에 의존한 보안 결정':'03_code_dns_security_decision.html','취약한 API 사용':'03_code_vulnerable_api.html'};

const NS='sda_';
function load(k,d){try{return JSON.parse(localStorage.getItem(NS+k))??d;}catch(e){return d;}}
function save(k,v){localStorage.setItem(NS+k,JSON.stringify(v));}
let learned=load('learned',{}),flashKnown=load('flash',{}),wrongs=load('wrong',[]);
let examBest=load('examBest',null),pracBest=load('pracBest',null);
function addWrong(it){if(!wrongs.some(w=>w.q===it.q)){wrongs.push(it);save('wrong',wrongs);}}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function gnorm(s){return (s||'').toString().toLowerCase().replace(/[\s.,;:!?()\[\]{}"'`]/g,'');}
function kwHit(t,k){return gnorm(t).includes(gnorm(k));}
function kwScore(t,kws,max){if(!kws||!kws.length)return 0;const h=kws.filter(k=>kwHit(t,k)).length;return Math.round(h/kws.length*max);}
function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function diffBadge(d){const c={'하':['#dcfce7','#15803d'],'중':['#fef9c3','#a16207'],'상':['#fee2e2','#b91c1c']}[d]||['#eef2ff','#4338ca'];return '<span style="display:inline-block;font-size:11px;font-weight:700;border-radius:6px;padding:2px 9px;font-family:JetBrains Mono,monospace;background:'+c[0]+';color:'+c[1]+'">난이도 '+d+'</span>';}
// 취약 코드 → 안전 코드 라인 단위 diff (LCS)
function lineDiff(a,b){const A=(a||'').split('\n'),B=(b||'').split('\n'),n=A.length,m=B.length;
  const dp=Array.from({length:n+1},()=>new Array(m+1).fill(0));
  for(let i=n-1;i>=0;i--)for(let j=m-1;j>=0;j--)dp[i][j]=A[i]===B[j]?dp[i+1][j+1]+1:Math.max(dp[i+1][j],dp[i][j+1]);
  let i=0,j=0;const out=[];
  while(i<n&&j<m){if(A[i]===B[j]){out.push(['ctx',A[i]]);i++;j++;}else if(dp[i+1][j]>=dp[i][j+1]){out.push(['del',A[i]]);i++;}else{out.push(['add',B[j]]);j++;}}
  while(i<n){out.push(['del',A[i]]);i++;}while(j<m){out.push(['add',B[j]]);j++;}
  return out;}
function diffHtml(a,b){return lineDiff(a,b).map(p=>{const s=p[0]==='del'?'- ':p[0]==='add'?'+ ':'  ';return '<span class="d-'+p[0]+'">'+esc(s+p[1])+'</span>';}).join('\n');}

document.getElementById('kisa49').innerHTML = KISA49.map(n=>'<option value="'+esc(n)+'">').join('');

function tab(v){
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.dataset.v===v));
  document.querySelectorAll('.view').forEach(x=>x.classList.remove('on'));
  document.getElementById('v-'+v).classList.add('on');window.scrollTo(0,0);
  ({dash:rDash,learn:rLearn,flash:rFlash,exam:rExam,prac:rPrac,wrong:rWrong}[v])();
}

// ===== 대시보드 =====
function rDash(){
  const ln=Object.keys(learned).length,fk=Object.keys(flashKnown).length;
  let rows='';
  CATS.forEach(c=>{const tot=CONCEPTS.filter(x=>x.cat===c).length,dn=CONCEPTS.filter(x=>x.cat===c&&learned[x.name]).length,pct=Math.round(dn/tot*100);
    rows+='<div class="prow"><div class="nm">'+c+'</div><div class="bar"><i style="width:'+pct+'%;background:'+CCOLOR[c]+'"></i></div><div class="vv">'+dn+'/'+tot+'</div></div>';});
  document.getElementById('v-dash').innerHTML=
   '<h2 class="st">📊 나의 학습 현황</h2><p class="sub">진도·기록은 이 브라우저에 자동 저장됩니다.</p>'+
   '<div class="dgrid">'+dc(ln+'/49','개념 학습')+dc(fk+'/49','플래시 숙련')+dc(examBest!=null?examBest+'%':'-','1교시 최고점')+dc(pracBest!=null?pracBest+'%':'-','2교시 최고점')+dc(wrongs.length,'오답노트')+'</div>'+
   '<div class="prog-wrap"><h3>유형별 개념 학습 숙련도</h3>'+rows+'</div>'+
   '<div class="quick"><button class="qbtn" onclick="tab(\'learn\')">📖 개념 학습</button><button class="qbtn ghost" onclick="tab(\'flash\')">🃏 플래시카드</button><button class="qbtn ghost" onclick="tab(\'exam\')">📝 1교시 이론</button><button class="qbtn ghost" onclick="tab(\'prac\')">🧪 2교시 실무</button></div>'+
   '<button class="reset" onclick="resetAll()">↺ 학습 기록 초기화</button>';
}
function dc(b,s){return '<div class="dcard"><b>'+b+'</b><span>'+s+'</span></div>';}
function resetAll(){if(confirm('모든 학습 기록을 초기화할까요?')){['learned','flash','wrong','examBest','pracBest'].forEach(k=>localStorage.removeItem(NS+k));learned={};flashKnown={};wrongs=[];examBest=null;pracBest=null;rDash();}}

// ===== 개념학습 =====
let learnCat='전체';
function rLearn(){
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===learnCat?' on':'')+'" onclick="setLearnCat(\''+c+'\')">'+c+(c==='전체'?'':' '+CONCEPTS.filter(x=>x.cat===c).length)+'</button>').join('');
  const list=CONCEPTS.filter(x=>learnCat==='전체'||x.cat===learnCat);
  const cards=list.map(x=>{const gi=CONCEPTS.indexOf(x),done=learned[x.name]?' done':'';
    const sim=SIMMAP[x.name]?'<a class="simlink" href="'+SIMMAP[x.name]+'">🔗 관련 시뮬레이터로 →</a>':'';
    return '<div class="ccard'+done+'" id="cc'+gi+'"><div class="ch" onclick="toggleCard('+gi+')"><div><h4>'+esc(x.name)+'</h4><div class="cwe">'+esc(x.cwe)+'</div></div><span class="badge" style="background:'+CCOLOR[x.cat]+'">'+x.cat+'</span></div>'+
      '<div class="detail">'+fld('정의',x.desc)+fld('보안 위협',x.risk)+fld('안전한 코딩',x.safe)+fld('진단 방법',x.diag)+codeBlock(gi,x.name)+sim+'<button class="done-btn" onclick="toggleDone('+gi+')">'+(learned[x.name]?'✓ 학습 완료':'학습 완료로 표시')+'</button></div></div>';}).join('');
  document.getElementById('v-learn').innerHTML='<h2 class="st">📖 개념 학습 — 49개 보안약점</h2><p class="sub">카드를 펼치면 정의·위협·진단법과 함께 <b>KISA 가이드의 Java·Python 안전하지 않은/안전한 코드 예제</b>를 확인할 수 있습니다. (Java=진단가이드, Python=시큐어코딩 가이드)</p><div class="catbar">'+chips+'</div><div class="cgrid">'+cards+'</div>';
}
function fld(l,t){return '<div class="fld"><div class="lb">'+l+'</div><div class="tx">'+esc(t)+'</div></div>';}
function codePane(vuln,safe){
  return '<div class="codepair"><div class="cp"><div class="cph bad">🚫 안전하지 않은 코드</div><pre class="cpre">'+esc(vuln||'(예제 없음)')+'</pre></div>'+
         '<div class="cp"><div class="cph good">✅ 안전한 코드</div><pre class="cpre">'+esc(safe||'(예제 없음)')+'</pre></div></div>';
}
function codeBlock(gi,name){
  const cd=CODE49[name]; if(!cd) return '';
  const hasPy=!!(cd.pyVuln&&cd.pySafe), jl=cd.javaLang||'Java';
  let tabs='<div class="lgtabs"><button class="lgtab on" id="lgj'+gi+'" onclick="setLang(event,'+gi+',\'j\')">'+esc(jl)+' · 진단가이드</button>'+
    (hasPy?'<button class="lgtab" id="lgp'+gi+'" onclick="setLang(event,'+gi+',\'p\')">Python · 시큐어코딩</button>':'')+'</div>';
  let jpane='<div id="lgjp'+gi+'">'+codePane(cd.javaVuln,cd.javaSafe)+'</div>';
  let ppane=hasPy?'<div id="lgpp'+gi+'" style="display:none">'+codePane(cd.pyVuln,cd.pySafe)+'</div>':'';
  let note=(!hasPy)?'<div class="cnote">※ '+esc(cd.note||'해당 약점은 Python 시큐어코딩 가이드에 코드 예제가 수록되어 있지 않습니다.')+'</div>':'';
  return '<div class="fld"><div class="lb">📑 가이드 코드 예제</div>'+tabs+jpane+ppane+note+
    '<div class="csrc">출처: 「소프트웨어 보안약점 진단가이드(2021)」(Java/C) · 「Python 시큐어코딩 가이드(2023)」 — KISA</div></div>';
}
function setLang(e,gi,which){
  if(e&&e.stopPropagation)e.stopPropagation();
  document.getElementById('lgjp'+gi).style.display=which==='j'?'block':'none';
  const pp=document.getElementById('lgpp'+gi); if(pp)pp.style.display=which==='p'?'block':'none';
  document.getElementById('lgj'+gi).classList.toggle('on',which==='j');
  const pb=document.getElementById('lgp'+gi); if(pb)pb.classList.toggle('on',which==='p');
}
function setLearnCat(c){learnCat=c;rLearn();}
function toggleCard(i){document.getElementById('cc'+i).classList.toggle('open');}
function toggleDone(i){const n=CONCEPTS[i].name;if(learned[n])delete learned[n];else learned[n]=true;save('learned',learned);rLearn();}

// ===== 플래시카드 =====
let flashCat='전체',flashDeck=[],flashIdx=0,flashFlip=false;
function rFlash(){
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===flashCat?' on':'')+'" onclick="setFlashCat(\''+c+'\')">'+c+'</button>').join('');
  if(!flashDeck.length)buildDeck();
  document.getElementById('v-flash').innerHTML='<h2 class="st">🃏 플래시카드</h2><p class="sub">약점명을 보고 핵심을 떠올린 뒤 카드를 눌러 확인하세요. "안다"는 다음 회차 덱에서 제외됩니다.</p><div class="catbar">'+chips+'</div><div id="flashStage"></div>';
  drawFlash();
}
function setFlashCat(c){flashCat=c;flashDeck=[];flashIdx=0;flashFlip=false;rFlash();}
function buildDeck(){let pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);let un=pool.filter(x=>!flashKnown[x.name]);flashDeck=shuffle(un.length?un:pool);flashIdx=0;flashFlip=false;}
function drawFlash(){
  const stage=document.getElementById('flashStage');const pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);const known=pool.filter(x=>flashKnown[x.name]).length;
  if(flashIdx>=flashDeck.length){stage.innerHTML='<div class="flash-stage"><div class="fcard"><div class="fr">🎉 이번 덱 완료!</div><div class="hint">숙련 '+known+'/'+pool.length+'</div></div><div class="frow"><button class="btn" onclick="restartDeck()">다시 섞어 풀기</button></div></div>';return;}
  const c=flashDeck[flashIdx];
  const front='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+c.cat+'</div><div class="fr">'+esc(c.name)+'</div><div class="hint">탭하여 핵심 보기</div>';
  const back='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+esc(c.cwe)+'</div><div class="bk"><b>정의</b> '+esc(c.desc)+'<br><br><b>안전한 코딩</b> '+esc(c.safe)+'</div>';
  stage.innerHTML='<div class="fmeta">'+(flashIdx+1)+' / '+flashDeck.length+' · 숙련 '+known+'/'+pool.length+'</div><div class="flash-stage"><div class="fcard" onclick="flipFlash()">'+(flashFlip?back:front)+'</div><div class="frow"><button class="f-no" onclick="markFlash(false)">아직 모른다</button><button class="f-ok" onclick="markFlash(true)">안다 ✓</button></div></div>';
}
function flipFlash(){flashFlip=!flashFlip;drawFlash();}
function markFlash(ok){const n=flashDeck[flashIdx].name;if(ok)flashKnown[n]=true;else delete flashKnown[n];save('flash',flashKnown);flashIdx++;flashFlip=false;drawFlash();}
function restartDeck(){buildDeck();drawFlash();}

// ===== 1교시 이론 (MC·OX·SHORT) =====
let exPool=[],exIdx=0,exN=0,exAns=[],exTimer=null,exLeft=0;
function examItems(){return QUIZ.map(x=>Object.assign({type:'MC'},x)).concat(THEORY);}
function rExam(){
  const all=examItems();
  document.getElementById('v-exam').innerHTML='<h2 class="st">📝 1교시 이론 (필기)</h2><p class="sub">객관식·OX·단답 혼합. 풀이 중 정답은 비공개, 제출 후 채점합니다. 합격선 70%. (총 문제은행 '+all.length+'문항)</p>'+
   '<div class="setbox"><h3>출제 설정</h3><p>문항 수를 고르면 무작위 출제됩니다. (문항당 40초 타이머)</p><div class="setrow"><button class="qbtn ghost" onclick="startExam(15)">15문항</button><button class="qbtn ghost" onclick="startExam(30)">30문항</button><button class="qbtn" onclick="startExam(999)">전체</button></div>'+(examBest!=null?'<p>최고 기록: <b>'+examBest+'%</b></p>':'<p>아직 기록이 없습니다.</p>')+'</div>';
}
function startExam(n){exPool=shuffle(examItems());exPool=exPool.slice(0,Math.min(n,exPool.length));exN=exPool.length;exIdx=0;exAns=[];exLeft=exN*40;startExTimer();drawExam();}
function startExTimer(){clearInterval(exTimer);exTimer=setInterval(()=>{exLeft--;const t=document.getElementById('exTimer');if(t){const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');t.classList.toggle('warn',exLeft<=30);}if(exLeft<=0){clearInterval(exTimer);gradeExam();}},1000);}
function drawExam(){
  const q=exPool[exIdx],pct=Math.round(exIdx/exN*100);const cat=q.c||q.cat||'';let body='';
  if(q.type==='MC'){body='<div>'+q.o.map((t,i)=>'<button class="opt'+(exAns[exIdx]===i?' sel':'')+'" onclick="pickEx('+i+')"><span class="lab">'+'ABCD'[i]+'</span><span class="ot"></span></button>').join('')+'</div>';}
  else if(q.type==='OX'){body='<div class="tfrow"><div class="tf'+(exAns[exIdx]===true?' sel tp':'')+'" onclick="pickEx(true)"><span class="rd"></span>⭕ 맞다 (O)</div><div class="tf'+(exAns[exIdx]===false?' sel fp':'')+'" onclick="pickEx(false)"><span class="rd"></span>❌ 아니다 (X)</div></div>';}
  else{body='<input class="shortin" id="shortIn" placeholder="정답을 입력하세요" value="'+esc(exAns[exIdx]||'')+'" oninput="exAns['+exIdx+']=this.value">';}
  document.getElementById('v-exam').innerHTML='<div class="qbox"><div class="bar2"><i style="width:'+pct+'%"></i></div><div class="qmeta"><span>문항 '+(exIdx+1)+' / '+exN+'</span><span class="timer" id="exTimer"></span></div><span class="typetag t-'+q.type+'">'+({MC:'객관식',OX:'OX',SHORT:'단답형'}[q.type])+'</span><span class="cat-tag">'+esc(cat)+'</span><div class="qtext"></div>'+(q.code?'<pre></pre>':'')+body+'<div class="nav"><button class="btn ghost" onclick="prevEx()" '+(exIdx===0?'disabled style=opacity:.4':'')+'>← 이전</button> <button class="btn" onclick="nextEx()">'+(exIdx===exN-1?'제출하고 채점':'다음 →')+'</button></div></div>';
  document.querySelector('#v-exam .qtext').textContent=q.q;if(q.code)document.querySelector('#v-exam pre').textContent=q.code;
  if(q.type==='MC')document.querySelectorAll('#v-exam .opt').forEach((b,i)=>b.querySelector('.ot').textContent=q.o[i]);
  const t=document.getElementById('exTimer');const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');
}
function pickEx(v){exAns[exIdx]=v;drawExam();}
function prevEx(){if(exIdx>0){exIdx--;drawExam();}}
function nextEx(){if(exIdx<exN-1){exIdx++;drawExam();}else gradeExam();}
function exCorrect(q,a){if(a==null||a==='')return false;if(q.type==='MC')return a===q.a;if(q.type==='OX')return a===q.a;return (q.answers||[]).some(x=>{const u=gnorm(a),g=gnorm(x);return u&&(u===g||u.includes(g)||g.includes(u));});}
function exAnsText(q){if(q.type==='MC')return 'ABCD'[q.a]+'. '+q.o[q.a];if(q.type==='OX')return q.a?'O (맞다)':'X (아니다)';return (q.answers||[]).join(' / ');}
function gradeExam(){
  clearInterval(exTimer);let sc=0;
  exPool.forEach((q,i)=>{if(exCorrect(q,exAns[i]))sc++;else addWrong({q:'['+({MC:'객관식',OX:'OX',SHORT:'단답'}[q.type])+'] '+q.q,a:exAnsText(q),e:q.e,tag:'1교시'});});
  const pct=Math.round(sc/exN*100),pass=pct>=70;if(examBest==null||pct>examBest){examBest=pct;save('examBest',pct);}
  document.getElementById('v-exam').innerHTML='<div class="res"><div class="big">'+pct+'%</div><div class="pf '+(pass?'pass':'fail')+'">'+(pass?'✅ 합격 (70%+)':'❌ 불합격')+'</div><p class="sub">'+exN+'문항 중 '+sc+'문항 정답</p><div class="quick" style="justify-content:center"><button class="btn" onclick="rExam()">다시 응시</button><button class="btn ghost" onclick="tab(\'wrong\')">오답노트 ('+wrongs.length+')</button></div></div>';
}

// ===== 2교시 실무 (정·오탐 판별 + 서술형 채점) =====
let prPool=[],prIdx=0,prN=0,prScores=[],prTP=null,prTimer=null,prLeft=0,prDiff='전체';
function pracPool(){return prDiff==='전체'?PRACTICAL:PRACTICAL.filter(p=>p.diff===prDiff);}
function setPrDiff(d){prDiff=d;rPrac();}
function rPrac(){
  const chips=['전체','하','중','상'].map(d=>{const cnt=d==='전체'?PRACTICAL.length:PRACTICAL.filter(p=>p.diff===d).length;return '<button class="cchip'+(d===prDiff?' on':'')+'" onclick="setPrDiff(\''+d+'\')">'+(d==='전체'?'전체':'난이도 '+d)+' '+cnt+'</button>';}).join('');
  const pool=pracPool();const tp=pool.filter(p=>p.isTruePositive).length;
  document.getElementById('v-prac').innerHTML='<h2 class="st">🧪 2교시 실무 (코드 진단)</h2><p class="sub">코드가 <b>정탐(보안약점 존재)</b>인지 <b>오탐(안전한 코드)</b>인지 판별하고, 약점 명칭·진단 근거·개선 코드를 직접 작성합니다. 모범답안 키워드 기반 채점이며, 틀린 진단(예: 안전한 코드를 취약하다고 서술)은 감점됩니다. 합격선 70%.</p>'+
   '<div class="catbar">'+chips+'</div>'+
   '<div class="setbox"><h3>실무 평가</h3><p>실제 2교시처럼 서술형으로 진단합니다. (문항당 3분 권장 타이머)<br>현재 출제풀: <b>'+pool.length+'문항</b> (정탐 '+tp+' · 오탐 '+(pool.length-tp)+')</p><div class="setrow"><button class="qbtn ghost" onclick="startPrac(6)">6문항 무작위</button><button class="qbtn" onclick="startPrac(999)">전체 풀이 ('+pool.length+')</button></div>'+(pracBest!=null?'<p>최고 기록: <b>'+pracBest+'%</b></p>':'<p>아직 기록이 없습니다.</p>')+'</div>';
}
function startPrac(n){const pool=pracPool();if(!pool.length){alert('해당 난이도 문항이 없습니다.');return;}prPool=shuffle(pool);prPool=prPool.slice(0,Math.min(n,prPool.length));prN=prPool.length;prIdx=0;prScores=[];prLeft=prN*180;startPrTimer();drawPrac();}
function startPrTimer(){clearInterval(prTimer);prTimer=setInterval(()=>{prLeft--;const t=document.getElementById('prTimer');if(t){const m=Math.floor(prLeft/60),s=prLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');t.classList.toggle('warn',prLeft<=60);}if(prLeft<=0){clearInterval(prTimer);prResult();}},1000);}
function codeWithLines(code){return code.split('\n').map((l,i)=>'<span class="ln">'+String(i+1).padStart(2,' ')+': </span>'+esc(l)).join('\n');}
function drawPrac(){
  prTP=null;const p=prPool[prIdx],pct=Math.round(prIdx/prN*100);
  document.getElementById('v-prac').innerHTML='<div class="qbox"><div class="bar2"><i style="width:'+pct+'%"></i></div><div class="qmeta"><span>실무 '+(prIdx+1)+' / '+prN+' · '+esc(p.lang)+'</span><span class="timer" id="prTimer"></span></div>'+
    '<span class="typetag t-PRAC">코드 진단</span><span class="cat-tag">'+esc(p.title)+'</span> '+diffBadge(p.diff)+
    '<pre id="prCode"></pre>'+
    '<div class="flbl">1) 정·오탐 판별</div><div class="tfrow"><div class="tf tp" id="tfTP" onclick="setTP(true)"><span class="rd"></span>🚨 정탐 — 보안약점 존재</div><div class="tf fp" id="tfFP" onclick="setTP(false)"><span class="rd"></span>🛡️ 오탐 — 안전한 코드</div></div>'+
    '<div class="flbl">2) 보안약점 표준 명칭 <span style="font-weight:400;color:#94a3b8">(정탐 시, KISA 49개 자동완성)</span></div><input class="pin" id="prName" list="kisa49" placeholder="예) SQL 삽입" disabled>'+
    '<div class="flbl">3) 진단 및 판별 근거 서술</div><textarea class="parea" id="prReason" placeholder="왜 정탐/오탐인지 근거를 서술하세요 (예: Statement로 외부 입력을 문자열 결합하여 SQL 삽입 가능 / 정규식 화이트리스트 검증으로 차단됨)"></textarea>'+
    '<div class="flbl">4) 보안 대책 — 안전한 코드 작성 <span style="font-weight:400;color:#94a3b8">(정탐 시)</span></div><textarea class="codearea" id="prFix" disabled></textarea>'+
    '<div class="nav"><button class="btn" onclick="submitPrac()">제출 및 채점</button></div><div id="prReport"></div></div>';
  document.getElementById('prCode').innerHTML=codeWithLines(p.code);
  document.getElementById('prFix').value=p.code;
  const t=document.getElementById('prTimer');const m=Math.floor(prLeft/60),s=prLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');
}
function setTP(v){prTP=v;document.getElementById('tfTP').classList.toggle('sel',v===true);document.getElementById('tfFP').classList.toggle('sel',v===false);
  document.getElementById('prName').disabled=!(v===true);document.getElementById('prFix').disabled=!(v===true);}
function gradeOne(p,ans){
  let parts=[],score=0;const tpOK=(ans.tp===p.isTruePositive);
  if(p.isTruePositive){
    parts.push(['정·오탐 판별',tpOK?30:0,30]);score+=tpOK?30:0;
    let nm=0;if(ans.tp){const u=gnorm(ans.name),g=gnorm(p.weaknessName);if(u&&u===g)nm=20;else if(u&&(g.includes(u)||u.includes(g))&&u.length>=2)nm=10;}parts.push(['보안약점 명칭',nm,20]);score+=nm;
    const rk=kwScore(ans.reason,p.reasonKeywords,25);parts.push(['진단 근거',rk,25]);score+=rk;
    const ck=ans.tp?kwScore(ans.fix,p.safeCodeKeywords,25):0;parts.push(['개선 코드',ck,25]);score+=ck;
  }else{
    parts.push(['정·오탐 판별',tpOK?50:0,50]);score+=tpOK?50:0;
    const rk=kwScore(ans.reason,p.reasonKeywords,50);parts.push(['판별 근거',rk,50]);score+=rk;
  }
  // 틀린/부적절한 진단 서술 감점 (예: 안전한 코드를 취약하다고 단정)
  const negHits=(p.negKw||[]).filter(k=>kwHit(ans.reason,k)||(ans.tp&&p.isTruePositive&&kwHit(ans.name,k)));
  const penalty=Math.min(negHits.length*8, p.isTruePositive?24:30);
  if(penalty){score-=penalty;parts.push(['오류 서술 감점',-penalty,0,true]);}
  return {score:Math.max(0,Math.round(score)),parts,tpOK,negHits,penalty};
}
function submitPrac(){
  if(prTP===null){alert('먼저 정·오탐을 판별하세요.');return;}
  const p=prPool[prIdx];
  const ans={tp:prTP,name:document.getElementById('prName').value,reason:document.getElementById('prReason').value,fix:document.getElementById('prFix').value};
  const r=gradeOne(p,ans);prScores.push(r.score);
  if(r.score<60)addWrong({q:'[2교시 실무] '+p.title+' ('+p.lang+')',a:(p.isTruePositive?('정탐 · '+p.weaknessName+(p.cwe?' ('+p.cwe+')':'')):'오탐(안전한 코드)'),e:p.explanation,tag:'2교시'});
  // 잠금
  ['tfTP','tfFP'].forEach(id=>document.getElementById(id).setAttribute('onclick',''));
  document.getElementById('prName').disabled=true;document.getElementById('prReason').disabled=true;document.getElementById('prFix').disabled=true;
  document.querySelector('#v-prac .nav').style.display='none';
  let kwhtml=p.reasonKeywords.map(k=>'<span class="kw'+(kwHit(ans.reason,k)?' hit':'')+'">'+esc(k)+'</span>').join('');
  let bars=r.parts.map(pt=>pt[3]
    ?'<div class="prow2"><div class="l penline">'+pt[0]+'</div><div class="bar"></div><div class="g penline">'+pt[1]+'점</div></div>'
    :'<div class="prow2"><div class="l">'+pt[0]+'</div><div class="bar"><i style="width:'+Math.round(pt[1]/pt[2]*100)+'%"></i></div><div class="g">'+pt[1]+'/'+pt[2]+'</div></div>').join('');
  let negBlock=(r.negHits&&r.negHits.length)?'<div style="margin-top:6px;font-size:13px;color:#b91c1c">⚠ 부적절·틀린 진단 서술 감지 (−'+r.penalty+'점): '+r.negHits.map(k=>'<span class="neg-kw">'+esc(k)+'</span>').join('')+'</div>':'';
  let model='<div class="model"><h4>📋 모범답안</h4>'+
    '<div style="font-size:14px;margin-bottom:8px"><b>정답 판별:</b> '+(p.isTruePositive?'🚨 정탐 (보안약점 존재)':'🛡️ 오탐 (안전한 코드)')+(p.isTruePositive?' &nbsp; <b>명칭:</b> '+esc(p.weaknessName)+(p.cwe?' ('+esc(p.cwe)+')':''):'')+'</div>'+
    '<div style="font-size:13.5px;margin-bottom:8px"><b>근거 핵심 키워드:</b><br>'+kwhtml+'</div>'+
    '<div style="font-size:14px;line-height:1.7;margin-bottom:10px"><b>해설:</b> '+esc(p.explanation)+'</div>';
  if(p.isTruePositive&&p.safeCode){
    model+='<div style="margin-top:12px"><h5 style="font-size:12px;color:var(--muted);margin-bottom:5px;font-family:JetBrains Mono,monospace">🔧 취약 → 안전 변경점 (diff) <span style="color:#fca5a5">- 제거</span> / <span style="color:#86efac">+ 추가</span></h5><pre class="diffpre">'+diffHtml(p.code,p.safeCode)+'</pre></div>';
    model+='<div class="two" style="margin-top:10px"><div class="pane"><h5>내 작성 코드</h5><pre style="margin:0">'+esc(ans.fix)+'</pre></div><div class="pane"><h5>모범 안전 코드</h5><pre style="margin:0">'+esc(p.safeCode)+'</pre></div></div>';
  }
  model+='</div>';
  const pass=r.score>=70;
  document.getElementById('prReport').innerHTML='<div class="report"><div class="scoreline"><div class="num '+(pass?'pass':'fail')+'">'+r.score+'점</div><div>'+(r.tpOK?'<span class="pass">✔ 정·오탐 정확</span>':'<span class="fail">✗ 정·오탐 오답</span>')+'</div></div>'+bars+negBlock+model+
    '<div class="nav" style="display:block"><button class="btn" onclick="'+(prIdx===prN-1?'prResult()':'nextPrac()')+'">'+(prIdx===prN-1?'결과 보기':'다음 문항 →')+'</button></div></div>';
  document.getElementById('prReport').scrollIntoView({behavior:'smooth',block:'nearest'});
}
function nextPrac(){prIdx++;drawPrac();}
function prResult(){
  clearInterval(prTimer);const avg=prScores.length?Math.round(prScores.reduce((a,b)=>a+b,0)/prScores.length):0;const pass=avg>=70;
  if(pracBest==null||avg>pracBest){pracBest=avg;save('pracBest',avg);}
  document.getElementById('v-prac').innerHTML='<div class="res"><div class="big">'+avg+'%</div><div class="pf '+(pass?'pass':'fail')+'">'+(pass?'✅ 합격 (평균 70%+)':'❌ 불합격')+'</div><p class="sub">'+prScores.length+'문항 평균 점수</p><div class="quick" style="justify-content:center"><button class="btn" onclick="rPrac()">다시 응시</button><button class="btn ghost" onclick="tab(\'wrong\')">오답노트 ('+wrongs.length+')</button></div></div>';
}

// ===== 오답노트 =====
function rWrong(){
  if(!wrongs.length){document.getElementById('v-wrong').innerHTML='<h2 class="st">❌ 오답노트</h2><div class="empty">아직 틀린 문제가 없습니다.<br>1교시·2교시를 풀면 틀린 문제가 자동으로 모입니다.</div>';return;}
  const items=wrongs.map((w,i)=>'<div class="witem"><button class="del" onclick="delWrong('+i+')">삭제</button><div class="wq">['+(w.tag||'')+'] '+esc(w.q)+'</div><div class="wa">정답: '+esc(w.a)+'</div><div class="we">해설: '+esc(w.e)+'</div></div>').join('');
  document.getElementById('v-wrong').innerHTML='<h2 class="st">❌ 오답노트 ('+wrongs.length+')</h2><p class="sub">틀린 문제를 모아 복습하세요.</p><div style="margin-bottom:14px"><button class="reset" onclick="clearWrong()">전체 비우기</button></div><div class="wlist">'+items+'</div>';
}
function delWrong(i){wrongs.splice(i,1);save('wrong',wrongs);rWrong();}
function clearWrong(){if(confirm('오답노트를 전부 비울까요?')){wrongs=[];save('wrong',wrongs);rWrong();}}

rDash();
</script>
</body>
</html>'''


def main():
    a = importlib.import_module('specs_academy')
    pr = importlib.import_module('specs_academy_practical')
    cc = importlib.import_module('specs_code49')
    # <script> 조기 종료 방지: 임베드 데이터의 </ 를 <\/ 로 이스케이프(런타임 JS 파싱 동일)
    def jdump(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    html = (TPL.replace('__CONCEPTS__', jdump(a.CONCEPTS))
               .replace('__QUIZ__', get_quiz_bank().replace('</', '<\\/'))
               .replace('__PRACTICAL__', jdump(pr.PRACTICAL))
               .replace('__THEORY__', jdump(pr.THEORY))
               .replace('__CODE49__', jdump(cc.CODE49)))
    open(os.path.join(OUT, 'secure-dev-academy.html'), 'w', encoding='utf-8').write(html)
    print('wrote secure-dev-academy.html | concepts=%d quiz(BANK) practical=%d theory=%d'
          % (len(a.CONCEPTS), len(pr.PRACTICAL), len(pr.THEORY)))


if __name__ == '__main__':
    main()
