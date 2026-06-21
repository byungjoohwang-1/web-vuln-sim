# -*- coding: utf-8 -*-
"""보안약점 진단원 학습 센터(secure-dev-academy.html) 생성기.
6개 모드: 대시보드 / 개념학습(49) / 플래시카드 / 모의고사 / 코드진단(2교시형) / 오답노트.
진도·오답·최고점은 localStorage 저장. CONCEPTS·CODEPROBS는 specs_academy, QUIZ는 기존 퀴즈 BANK 재사용."""
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
<title>보안약점 진단원 학습 센터 | 개발보안 학습 포털</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lora:wght@600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--p:#6366f1;--p2:#8b5cf6;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0;--ok:#22c55e;--no:#ef4444;--bg:#f1f5f9}
body{font-family:'Lora',serif;background:var(--bg);color:var(--ink);line-height:1.6;min-height:100vh}
a{text-decoration:none;color:inherit}
.top{background:#0b1020;padding:9px 0}.top .wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.top a{color:#a5b4fc;font-family:'JetBrains Mono',monospace;font-size:13px}
.hero{background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;padding:34px 0 24px}
.hero .wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.hero h1{font-size:27px;margin-bottom:4px}.hero p{opacity:.9;font-size:14px}
/* tabs */
.tabs{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20;box-shadow:0 2px 10px rgba(2,6,23,.05)}
.tabs .wrap{max-width:1160px;margin:0 auto;padding:0 12px;display:flex;gap:4px;overflow-x:auto}
.tab{border:none;background:transparent;padding:15px 16px;font-family:'Lora',serif;font-weight:700;font-size:14.5px;color:var(--muted);cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap;transition:.15s}
.tab:hover{color:var(--p)}
.tab.on{color:var(--p);border-bottom-color:var(--p)}
.wrap{max-width:1160px;margin:0 auto;padding:0 20px}
.view{display:none;padding:30px 0 60px}.view.on{display:block}
h2.st{font-size:23px;margin-bottom:6px}.sub{color:var(--muted);font-size:14px;margin-bottom:22px}
/* dashboard */
.dgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:26px}
.dcard{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;text-align:center;box-shadow:0 6px 18px rgba(2,6,23,.05)}
.dcard b{display:block;font-size:34px;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.dcard span{font-size:13px;color:var(--muted)}
.prog-wrap{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 26px;margin-bottom:22px}
.prog-wrap h3{font-size:17px;margin-bottom:16px}
.prow{display:flex;align-items:center;gap:12px;margin-bottom:12px}
.prow .nm{width:130px;font-size:14px;font-weight:700}
.prow .bar{flex:1;height:12px;background:#eef2ff;border-radius:10px;overflow:hidden}
.prow .bar>i{display:block;height:100%;border-radius:10px}
.prow .vv{width:54px;text-align:right;font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--muted)}
.quick{display:flex;gap:10px;flex-wrap:wrap}
.qbtn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;padding:12px 22px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:14px;cursor:pointer;transition:.2s}
.qbtn:hover{transform:translateY(-2px)}
.qbtn.ghost{background:#fff;color:var(--p);border:1.5px solid var(--p)}
.reset{background:none;border:1px solid var(--line);color:var(--muted);padding:8px 16px;border-radius:20px;font-size:12.5px;cursor:pointer;margin-top:18px}
/* category chips */
.catbar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.cchip{border:1.5px solid var(--line);background:#fff;border-radius:20px;padding:7px 15px;font-family:'Lora',serif;font-size:13.5px;font-weight:700;cursor:pointer;transition:.15s}
.cchip:hover{border-color:var(--p)}
.cchip.on{background:var(--p);color:#fff;border-color:var(--p)}
/* concept cards */
.cgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
.ccard{background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;transition:.2s}
.ccard.done{border-color:#bbf7d0;box-shadow:0 0 0 2px #dcfce7 inset}
.ccard .ch{padding:15px 18px;cursor:pointer;display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.ccard .ch h4{font-size:15.5px;line-height:1.4}
.ccard .ch .cwe{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);margin-top:3px}
.ccard .badge{font-size:10.5px;color:#fff;border-radius:20px;padding:2px 9px;white-space:nowrap;font-family:'JetBrains Mono',monospace}
.ccard .detail{display:none;padding:0 18px 16px;border-top:1px solid var(--line)}
.ccard.open .detail{display:block}
.ccard .fld{margin-top:12px}
.ccard .fld .lb{font-size:12px;font-weight:700;color:var(--p);margin-bottom:3px}
.ccard .fld .tx{font-size:14px;color:#334155;line-height:1.65}
.ccard .done-btn{margin-top:14px;width:100%;border:1.5px solid var(--ok);background:#fff;color:#16a34a;padding:9px;border-radius:10px;font-family:'Lora',serif;font-weight:700;cursor:pointer;font-size:13.5px}
.ccard.done .done-btn{background:var(--ok);color:#fff}
/* flashcard */
.flash-stage{max-width:560px;margin:0 auto;text-align:center}
.fcard{background:#fff;border:1px solid var(--line);border-radius:20px;min-height:240px;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:34px;cursor:pointer;box-shadow:0 12px 34px rgba(2,6,23,.1);transition:.2s}
.fcard:hover{transform:translateY(-3px)}
.fcard .face-cat{font-size:12px;color:#fff;border-radius:20px;padding:3px 12px;margin-bottom:14px;font-family:'JetBrains Mono',monospace}
.fcard .fr{font-size:24px;font-weight:800}
.fcard .hint{margin-top:16px;font-size:12.5px;color:var(--muted)}
.fcard .bk{font-size:15px;color:#334155;line-height:1.7;text-align:left}
.fcard .bk b{color:var(--p)}
.frow{display:flex;gap:10px;justify-content:center;margin-top:18px}
.frow button{border:none;padding:13px 30px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:15px;cursor:pointer;transition:.2s}
.f-no{background:#fef2f2;color:#dc2626;border:1.5px solid #fecaca!important}
.f-ok{background:#f0fdf4;color:#16a34a;border:1.5px solid #bbf7d0!important}
.fmeta{text-align:center;color:var(--muted);font-size:13px;margin-bottom:14px;font-family:'JetBrains Mono',monospace}
/* exam + code */
.setbox{background:#fff;border:1px solid var(--line);border-radius:16px;padding:26px;max-width:620px;margin:0 auto;text-align:center}
.setbox h3{font-size:19px;margin-bottom:8px}.setbox p{color:var(--muted);font-size:14px;margin-bottom:18px}
.setrow{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:16px}
.opt{text-align:left;border:1.5px solid var(--line);border-radius:12px;padding:13px 16px;cursor:pointer;font-family:'Lora',serif;font-size:15px;background:#fff;transition:.15s;display:flex;gap:10px;width:100%;margin-bottom:9px}
.opt:hover:not(:disabled){border-color:var(--p);background:#f5f7ff}
.opt .lab{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--p)}
.opt:disabled{cursor:default}
.opt.correct{border-color:var(--ok);background:#f0fdf4}.opt.correct .lab{color:var(--ok)}
.opt.wrong{border-color:var(--no);background:#fef2f2}.opt.wrong .lab{color:var(--no)}
.qbox{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px 26px;max-width:760px;margin:0 auto}
.bar2{height:8px;background:#eef2ff;border-radius:10px;overflow:hidden;margin-bottom:6px}.bar2>i{display:block;height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6);width:0;transition:.3s}
.qmeta{display:flex;justify-content:space-between;font-size:13px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-bottom:14px}
.timer{font-weight:700}.timer.warn{color:var(--no)}
.qtext{font-size:17px;font-weight:700;line-height:1.55;margin-bottom:14px}
pre{background:#0b1020;color:#e2e8f0;padding:14px 16px;border-radius:10px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6;margin-bottom:16px;white-space:pre}
.cat-tag{display:inline-block;font-size:12px;color:#4338ca;background:#eef2ff;border:1px solid #c7d2fe;border-radius:20px;padding:3px 12px;margin-bottom:12px}
.exp{margin-top:14px;border-radius:12px;padding:14px 16px;font-size:14px;line-height:1.65;display:none}.exp.show{display:block}
.exp.ok{background:#f0fdf4;border-left:4px solid var(--ok)}.exp.no{background:#fef2f2;border-left:4px solid var(--no)}
.nav{margin-top:18px;text-align:right}
.btn{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;padding:12px 26px;border-radius:30px;font-family:'Lora',serif;font-weight:700;font-size:15px;cursor:pointer;transition:.2s}
.btn:hover{transform:translateY(-2px)}.btn.ghost{background:#fff;color:var(--p);border:1.5px solid var(--p)}
.res{text-align:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:34px;max-width:720px;margin:0 auto}
.res .big{font-size:58px;font-weight:800;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.res .pf{font-size:22px;font-weight:800;margin:4px 0}
.res .pass{color:#16a34a}.res .fail{color:#dc2626}
/* 오답노트 */
.wlist{display:flex;flex-direction:column;gap:12px}
.witem{background:#fff;border:1px solid var(--line);border-left:4px solid var(--no);border-radius:12px;padding:16px 18px}
.witem .wq{font-weight:700;margin-bottom:6px;font-size:14.5px}
.witem .wa{color:#16a34a;font-size:13.5px;margin-bottom:4px}
.witem .we{color:#475569;font-size:13.5px}
.witem .del{float:right;border:none;background:#fef2f2;color:#dc2626;border-radius:8px;padding:4px 10px;font-size:12px;cursor:pointer}
.empty{text-align:center;color:var(--muted);padding:50px 0;font-size:15px}
@media(max-width:760px){.dgrid{grid-template-columns:1fr 1fr}.cgrid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="top"><div class="wrap"><a href="secure-dev-portal.html">&larr; 개발보안 학습 포털</a> &nbsp;·&nbsp; <a href="index.html">메인 허브</a></div></div>
<div class="hero"><div class="wrap"><h1>🎓 보안약점 진단원 학습 센터</h1><p>개념 학습 · 플래시카드 · 모의고사 · 코드진단 실습 · 오답노트 — 진도는 자동 저장됩니다</p></div></div>
<div class="tabs"><div class="wrap">
  <button class="tab on" data-v="dash" onclick="tab('dash')">📊 대시보드</button>
  <button class="tab" data-v="learn" onclick="tab('learn')">📖 개념학습</button>
  <button class="tab" data-v="flash" onclick="tab('flash')">🃏 플래시카드</button>
  <button class="tab" data-v="exam" onclick="tab('exam')">📝 모의고사</button>
  <button class="tab" data-v="code" onclick="tab('code')">🔍 코드진단</button>
  <button class="tab" data-v="wrong" onclick="tab('wrong')">❌ 오답노트</button>
</div></div>
<div class="wrap">
  <div class="view on" id="v-dash"></div>
  <div class="view" id="v-learn"></div>
  <div class="view" id="v-flash"></div>
  <div class="view" id="v-exam"></div>
  <div class="view" id="v-code"></div>
  <div class="view" id="v-wrong"></div>
</div>

<script>
const CONCEPTS = __CONCEPTS__;
const CODEPROBS = __CODEPROBS__;
const QUIZ = __QUIZ__;
const CATS = ['입력검증','보안기능','시간상태','에러처리','코드오류','캡슐화','API오용'];
const CCOLOR = {'입력검증':'#6366f1','보안기능':'#0ea5e9','시간상태':'#14b8a6','에러처리':'#f59e0b','코드오류':'#ef4444','캡슐화':'#8b5cf6','API오용':'#64748b'};

// ===== storage =====
const NS='sda_';
function load(k,d){try{return JSON.parse(localStorage.getItem(NS+k))??d;}catch(e){return d;}}
function save(k,v){localStorage.setItem(NS+k,JSON.stringify(v));}
let learned=load('learned',{});      // {name:true}
let flashKnown=load('flash',{});     // {name:true}
let wrongs=load('wrong',[]);         // [{q,a,e,tag}]
let examBest=load('examBest',null);

function addWrong(item){
  if(!wrongs.some(w=>w.q===item.q)) {wrongs.push(item); save('wrong',wrongs);}
}

// ===== tabs =====
function tab(v){
  document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.dataset.v===v));
  document.querySelectorAll('.view').forEach(x=>x.classList.remove('on'));
  document.getElementById('v-'+v).classList.add('on');
  window.scrollTo(0,0);
  ({dash:rDash,learn:rLearn,flash:rFlash,exam:rExam,code:rCode,wrong:rWrong}[v])();
}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}

// ===== 대시보드 =====
function rDash(){
  const ln=Object.keys(learned).length, fk=Object.keys(flashKnown).length;
  const el=document.getElementById('v-dash');
  let rows='';
  CATS.forEach(c=>{
    const tot=CONCEPTS.filter(x=>x.cat===c).length;
    const dn=CONCEPTS.filter(x=>x.cat===c&&learned[x.name]).length;
    const pct=Math.round(dn/tot*100);
    rows+='<div class="prow"><div class="nm">'+c+'</div><div class="bar"><i style="width:'+pct+'%;background:'+CCOLOR[c]+'"></i></div><div class="vv">'+dn+'/'+tot+'</div></div>';
  });
  el.innerHTML=
   '<h2 class="st">📊 나의 학습 현황</h2><p class="sub">진도와 기록은 이 브라우저에 자동 저장됩니다.</p>'+
   '<div class="dgrid">'+
     dcard(ln+'/49','개념 학습 진도')+
     dcard(fk+'/49','플래시카드 숙련')+
     dcard(examBest!=null?examBest+'%':'-','모의고사 최고점')+
     dcard(wrongs.length,'오답노트')+
   '</div>'+
   '<div class="prog-wrap"><h3>유형별 개념 학습 숙련도</h3>'+rows+'</div>'+
   '<div class="quick">'+
     '<button class="qbtn" onclick="tab(\'learn\')">📖 개념 학습 시작</button>'+
     '<button class="qbtn ghost" onclick="tab(\'flash\')">🃏 플래시카드</button>'+
     '<button class="qbtn ghost" onclick="tab(\'exam\')">📝 모의고사</button>'+
     '<button class="qbtn ghost" onclick="tab(\'code\')">🔍 코드진단</button>'+
   '</div>'+
   '<button class="reset" onclick="resetAll()">↺ 학습 기록 초기화</button>';
}
function dcard(b,s){return '<div class="dcard"><b>'+b+'</b><span>'+s+'</span></div>';}
function resetAll(){if(confirm('모든 학습 기록(진도·플래시카드·오답노트·최고점)을 초기화할까요?')){['learned','flash','wrong','examBest'].forEach(k=>localStorage.removeItem(NS+k));learned={};flashKnown={};wrongs=[];examBest=null;rDash();}}

// ===== 개념학습 =====
let learnCat='전체';
function rLearn(){
  const el=document.getElementById('v-learn');
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===learnCat?' on':'')+'" onclick="setLearnCat(\''+c+'\')">'+c+(c==='전체'?'':' '+CONCEPTS.filter(x=>x.cat===c).length)+'</button>').join('');
  const list=CONCEPTS.filter(x=>learnCat==='전체'||x.cat===learnCat);
  const cards=list.map((x)=>{
    const gi=CONCEPTS.indexOf(x);
    const done=learned[x.name]?' done':'';
    return '<div class="ccard'+done+'" id="cc'+gi+'">'+
      '<div class="ch" onclick="toggleCard('+gi+')"><div><h4>'+esc(x.name)+'</h4><div class="cwe">'+esc(x.cwe)+'</div></div><span class="badge" style="background:'+CCOLOR[x.cat]+'">'+x.cat+'</span></div>'+
      '<div class="detail">'+
        fld('정의',x.desc)+fld('보안 위협',x.risk)+fld('안전한 코딩',x.safe)+fld('진단 방법',x.diag)+
        '<button class="done-btn" onclick="toggleDone('+gi+')">'+(learned[x.name]?'✓ 학습 완료':'학습 완료로 표시')+'</button>'+
      '</div></div>';
  }).join('');
  el.innerHTML='<h2 class="st">📖 개념 학습 — 49개 보안약점</h2><p class="sub">카드를 눌러 상세(정의·위협·안전코딩·진단)를 펼치고, 학습 완료를 표시하세요.</p><div class="catbar">'+chips+'</div><div class="cgrid">'+cards+'</div>';
}
function fld(l,t){return '<div class="fld"><div class="lb">'+l+'</div><div class="tx">'+esc(t)+'</div></div>';}
function setLearnCat(c){learnCat=c;rLearn();}
function toggleCard(i){document.getElementById('cc'+i).classList.toggle('open');}
function toggleDone(i){const n=CONCEPTS[i].name;if(learned[n])delete learned[n];else learned[n]=true;save('learned',learned);rLearn();}

// ===== 플래시카드 =====
let flashCat='전체',flashDeck=[],flashIdx=0,flashFlip=false;
function rFlash(){
  const el=document.getElementById('v-flash');
  const chips=['전체',...CATS].map(c=>'<button class="cchip'+(c===flashCat?' on':'')+'" onclick="setFlashCat(\''+c+'\')">'+c+'</button>').join('');
  if(!flashDeck.length) buildDeck();
  el.innerHTML='<h2 class="st">🃏 플래시카드</h2><p class="sub">약점명을 보고 핵심을 떠올린 뒤 카드를 눌러 확인하세요. "안다"로 표시하면 다음 회차 덱에서 제외됩니다.</p><div class="catbar">'+chips+'</div><div id="flashStage"></div>';
  drawFlash();
}
function setFlashCat(c){flashCat=c;flashDeck=[];flashIdx=0;flashFlip=false;rFlash();}
function buildDeck(){
  let pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);
  let unknown=pool.filter(x=>!flashKnown[x.name]);
  flashDeck=(unknown.length?unknown:pool).slice();
  for(let i=flashDeck.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[flashDeck[i],flashDeck[j]]=[flashDeck[j],flashDeck[i]];}
  flashIdx=0;flashFlip=false;
}
function drawFlash(){
  const stage=document.getElementById('flashStage');
  const pool=CONCEPTS.filter(x=>flashCat==='전체'||x.cat===flashCat);
  const known=pool.filter(x=>flashKnown[x.name]).length;
  if(flashIdx>=flashDeck.length){
    stage.innerHTML='<div class="flash-stage"><div class="fcard"><div class="fr">🎉 이번 덱 완료!</div><div class="hint">숙련 '+known+'/'+pool.length+'</div></div><div class="frow"><button class="btn" onclick="restartDeck()">다시 섞어 풀기</button></div></div>';
    return;
  }
  const c=flashDeck[flashIdx];
  const front='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+c.cat+'</div><div class="fr">'+esc(c.name)+'</div><div class="hint">탭하여 핵심 보기</div>';
  const back='<div class="face-cat" style="background:'+CCOLOR[c.cat]+'">'+esc(c.cwe)+'</div><div class="bk"><b>정의</b> '+esc(c.desc)+'<br><br><b>안전한 코딩</b> '+esc(c.safe)+'</div>';
  stage.innerHTML='<div class="fmeta">'+(flashIdx+1)+' / '+flashDeck.length+' · 숙련 '+known+'/'+pool.length+'</div>'+
    '<div class="flash-stage"><div class="fcard" onclick="flipFlash()">'+(flashFlip?back:front)+'</div>'+
    '<div class="frow"><button class="f-no" onclick="markFlash(false)">아직 모른다</button><button class="f-ok" onclick="markFlash(true)">안다 ✓</button></div></div>';
}
function flipFlash(){flashFlip=!flashFlip;drawFlash();}
function markFlash(ok){const n=flashDeck[flashIdx].name;if(ok)flashKnown[n]=true;else delete flashKnown[n];save('flash',flashKnown);flashIdx++;flashFlip=false;drawFlash();}
function restartDeck(){buildDeck();drawFlash();}

// ===== 모의고사 =====
let exN=20,exPool=[],exIdx=0,exAns=[],exTimer=null,exLeft=0;
function rExam(){
  const el=document.getElementById('v-exam');
  el.innerHTML='<h2 class="st">📝 모의고사 (시험 모드)</h2><p class="sub">실제 시험처럼 풀이 중에는 정답을 보여주지 않고, 제출 후 채점합니다. 합격선 70%.</p>'+
   '<div class="setbox"><h3>출제 설정</h3><p>문항 수를 고르면 무작위로 출제됩니다. (문항당 45초 타이머)</p>'+
   '<div class="setrow"><button class="qbtn ghost" onclick="startExam(10)">10문항</button><button class="qbtn ghost" onclick="startExam(20)">20문항</button><button class="qbtn" onclick="startExam(40)">40문항 (전체)</button></div>'+
   (examBest!=null?'<p>현재 최고 기록: <b>'+examBest+'%</b></p>':'<p>아직 응시 기록이 없습니다.</p>')+'</div>';
}
function startExam(n){
  exPool=QUIZ.slice();for(let i=exPool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[exPool[i],exPool[j]]=[exPool[j],exPool[i]];}
  exPool=exPool.slice(0,Math.min(n,QUIZ.length));exN=exPool.length;exIdx=0;exAns=[];
  exLeft=exN*45;startTimer();drawExam();
}
function startTimer(){clearInterval(exTimer);exTimer=setInterval(()=>{exLeft--;const t=document.getElementById('exTimer');if(t){const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');t.classList.toggle('warn',exLeft<=30);}if(exLeft<=0){clearInterval(exTimer);gradeExam();}},1000);}
function drawExam(){
  const el=document.getElementById('v-exam');const q=exPool[exIdx];const pct=Math.round(exIdx/exN*100);
  const opts=q.o.map((t,i)=>'<button class="opt'+(exAns[exIdx]===i?' on':'')+'" onclick="pickExam('+i+')" style="'+(exAns[exIdx]===i?'border-color:var(--p);background:#eef2ff':'')+'"><span class="lab">'+'ABCD'[i]+'</span><span class="ot"></span></button>').join('');
  el.innerHTML='<div class="qbox"><div class="bar2"><i style="width:'+pct+'%"></i></div>'+
    '<div class="qmeta"><span>문항 '+(exIdx+1)+' / '+exN+'</span><span class="timer" id="exTimer"></span></div>'+
    '<span class="cat-tag">'+q.c+'</span><div class="qtext"></div>'+(q.code?'<pre></pre>':'')+'<div>'+opts+'</div>'+
    '<div class="nav"><button class="btn ghost" onclick="prevExam()" '+(exIdx===0?'disabled style=opacity:.4':'')+'>← 이전</button> '+
    '<button class="btn" onclick="nextExam()">'+(exIdx===exN-1?'제출하고 채점':'다음 →')+'</button></div></div>';
  el.querySelector('.qtext').textContent=q.q;if(q.code)el.querySelector('pre').textContent=q.code;
  el.querySelectorAll('.opt').forEach((b,i)=>b.querySelector('.ot').textContent=q.o[i]);
  const t=document.getElementById('exTimer');const m=Math.floor(exLeft/60),s=exLeft%60;t.textContent='⏱ '+m+':'+String(s).padStart(2,'0');
}
function pickExam(i){exAns[exIdx]=i;drawExam();}
function prevExam(){if(exIdx>0){exIdx--;drawExam();}}
function nextExam(){if(exIdx<exN-1){exIdx++;drawExam();}else gradeExam();}
function gradeExam(){
  clearInterval(exTimer);let sc=0;
  exPool.forEach((q,i)=>{if(exAns[i]===q.a)sc++;else addWrong({q:q.q,a:'ABCD'[q.a]+'. '+q.o[q.a],e:q.e,tag:'모의고사'});});
  const pct=Math.round(sc/exN*100);const pass=pct>=70;
  if(examBest==null||pct>examBest){examBest=pct;save('examBest',pct);}
  const el=document.getElementById('v-exam');
  el.innerHTML='<div class="res"><div class="big">'+pct+'%</div><div class="pf '+(pass?'pass':'fail')+'">'+(pass?'✅ 합격 (70% 이상)':'❌ 불합격')+'</div>'+
    '<p class="sub">'+exN+'문항 중 '+sc+'문항 정답'+(examBest===pct?' · 최고 기록 갱신!':'')+'</p>'+
    '<div class="quick" style="justify-content:center"><button class="btn" onclick="rExam()">다시 응시</button><button class="btn ghost" onclick="tab(\'wrong\')">오답노트 보기 ('+wrongs.length+')</button></div></div>';
}

// ===== 코드진단 =====
let cdPool=[],cdIdx=0,cdScore=0;
function rCode(){
  const el=document.getElementById('v-code');
  el.innerHTML='<h2 class="st">🔍 코드 진단 실습 (2교시형)</h2><p class="sub">코드 스니펫에서 어떤 보안약점(유형/약점명)이 있는지 찾는 실습입니다.</p>'+
    '<div class="setbox"><h3>코드 진단 12문항</h3><p>실제 진단 업무처럼 소스코드에서 취약점을 식별합니다. 문항마다 즉시 해설을 봅니다.</p><button class="qbtn" onclick="startCode()">진단 시작</button></div>';
}
function startCode(){cdPool=CODEPROBS.slice();for(let i=cdPool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[cdPool[i],cdPool[j]]=[cdPool[j],cdPool[i]];}cdIdx=0;cdScore=0;drawCode();}
function drawCode(){
  const el=document.getElementById('v-code');const q=cdPool[cdIdx];const pct=Math.round(cdIdx/cdPool.length*100);
  const opts=q.opts.map((t,i)=>'<button class="opt" data-i="'+i+'" onclick="ansCode('+i+')"><span class="lab">'+'ABCD'[i]+'</span><span class="ot"></span></button>').join('');
  el.innerHTML='<div class="qbox"><div class="bar2"><i style="width:'+pct+'%"></i></div>'+
    '<div class="qmeta"><span>코드 '+(cdIdx+1)+' / '+cdPool.length+' ('+q.lang+')</span><span>점수 '+cdScore+'</span></div>'+
    '<div class="qtext"></div><pre></pre><div>'+opts+'</div><div class="exp" id="cexp"></div><div class="nav" id="cnav"></div></div>';
  el.querySelector('.qtext').textContent=q.q;el.querySelector('pre').textContent=q.code;
  el.querySelectorAll('.opt').forEach((b,i)=>b.querySelector('.ot').textContent=q.opts[i]);
}
function ansCode(i){
  const q=cdPool[cdIdx];const el=document.getElementById('v-code');const btns=el.querySelectorAll('.opt');
  btns.forEach(b=>b.disabled=true);btns[q.a].classList.add('correct');
  const ok=i===q.a;if(ok)cdScore++;else{btns[i].classList.add('wrong');addWrong({q:'[코드진단] '+q.q+' ('+q.lang+')',a:'ABCD'[q.a]+'. '+q.opts[q.a],e:q.exp,tag:'코드진단'});}
  const ex=document.getElementById('cexp');ex.className='exp show '+(ok?'ok':'no');ex.textContent=(ok?'✅ 정답! ':'❌ 오답. 정답: '+'ABCD'[q.a]+'. ')+q.exp;
  const nav=document.getElementById('cnav');const last=cdIdx===cdPool.length-1;
  const b=document.createElement('button');b.className='btn';b.textContent=last?'결과 보기':'다음 코드 →';
  b.onclick=()=>{if(last){const pct=Math.round(cdScore/cdPool.length*100);el.innerHTML='<div class="res"><div class="big">'+pct+'%</div><div class="pf">'+cdPool.length+'문항 중 '+cdScore+'문항 정답</div><div class="quick" style="justify-content:center"><button class="btn" onclick="startCode()">다시 풀기</button><button class="btn ghost" onclick="tab(\'wrong\')">오답노트 ('+wrongs.length+')</button></div></div>';}else{cdIdx++;drawCode();}};
  nav.appendChild(b);
}

// ===== 오답노트 =====
function rWrong(){
  const el=document.getElementById('v-wrong');
  if(!wrongs.length){el.innerHTML='<h2 class="st">❌ 오답노트</h2><div class="empty">아직 틀린 문제가 없습니다.<br>모의고사·코드진단을 풀면 틀린 문제가 자동으로 모입니다.</div>';return;}
  const items=wrongs.map((w,i)=>'<div class="witem"><button class="del" onclick="delWrong('+i+')">삭제</button><div class="wq">['+(w.tag||'')+'] '+esc(w.q)+'</div><div class="wa">정답: '+esc(w.a)+'</div><div class="we">해설: '+esc(w.e)+'</div></div>').join('');
  el.innerHTML='<h2 class="st">❌ 오답노트 ('+wrongs.length+')</h2><p class="sub">틀린 문제를 모아 복습하세요.</p><div style="margin-bottom:14px"><button class="reset" onclick="clearWrong()">전체 비우기</button></div><div class="wlist">'+items+'</div>';
}
function delWrong(i){wrongs.splice(i,1);save('wrong',wrongs);rWrong();}
function clearWrong(){if(confirm('오답노트를 전부 비울까요?')){wrongs=[];save('wrong',wrongs);rWrong();}}

rDash();
</script>
</body>
</html>'''


def main():
    mod = importlib.import_module('specs_academy')
    concepts = json.dumps(mod.CONCEPTS, ensure_ascii=False)
    codeprobs = json.dumps(mod.CODEPROBS, ensure_ascii=False)
    quiz = get_quiz_bank()
    html = (TPL.replace('__CONCEPTS__', concepts)
               .replace('__CODEPROBS__', codeprobs)
               .replace('__QUIZ__', quiz))
    out = os.path.join(OUT, 'secure-dev-academy.html')
    open(out, 'w', encoding='utf-8').write(html)
    print('wrote secure-dev-academy.html  | concepts=%d codeprobs=%d' % (len(mod.CONCEPTS), len(mod.CODEPROBS)))


if __name__ == '__main__':
    main()
