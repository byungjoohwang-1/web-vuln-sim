// 검증 하니스: secure-dev-academy.html 의 JS를 DOM shim 위에서 실행하고
// 데이터 정합성 / gradeOne 채점(감점 포함) / lineDiff / exCorrect 단위검증.
const fs = require('fs'), vm = require('vm'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'public', 'secure-dev-academy.html'), 'utf8');
// 주입된 <script type="module" src="auth-widget.js"> 등에 휘둘리지 않도록
// CONCEPTS를 담은 인라인 스크립트 블록만 선택한다.
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(x => x[1]);
let code = blocks.find(b => b.includes('const CONCEPTS'));
if (!code) { console.error('academy script block not found'); process.exit(1); }

// ---- DOM shim ----
function htmlEscape(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function mkEl() {
  const el = {
    _html: '', _text: '', value: '', disabled: false,
    classList: { _s: new Set(), add(){[].forEach.call(arguments,a=>this._s.add(a));}, remove(){[].forEach.call(arguments,a=>this._s.delete(a));}, toggle(c,f){if(f===undefined)f=!this._s.has(c);f?this._s.add(c):this._s.delete(c);return f;}, contains(c){return this._s.has(c);} },
    dataset: {}, style: {},
    setAttribute(){}, getAttribute(){return '';},
    querySelector(){return mkEl();}, querySelectorAll(){return [];},
    addEventListener(){}, scrollIntoView(){}, appendChild(){}, focus(){}
  };
  // 실제 DOM 모사: textContent 설정 시 innerHTML은 HTML-escape 된 값이 됨 (esc() 정확 동작)
  Object.defineProperty(el, 'textContent', { get(){return this._text;}, set(v){this._text=v==null?'':String(v);this._html=htmlEscape(this._text);} });
  Object.defineProperty(el, 'innerHTML', { get(){return this._html;}, set(v){this._html=v;this._text='';} });
  return el;
}
const elCache = {};
const document = {
  getElementById(id){ return elCache[id] || (elCache[id] = mkEl()); },
  createElement(){ return mkEl(); },
  querySelectorAll(){ return []; },
  querySelector(){ return mkEl(); }
};
const store = {};
const localStorage = {
  getItem(k){ return k in store ? store[k] : null; },
  setItem(k,v){ store[k] = String(v); },
  removeItem(k){ delete store[k]; }
};
const window = { scrollTo(){}, print(){}, };
const alert = () => {};
const confirm = () => true;
const setInterval = () => 0, clearInterval = () => {}, setTimeout = (f)=>{ if(typeof f==='function') {} return 0; };

// 캡처: const 바인딩은 context global 에 붙지 않으므로 명시적으로 끌어온다
code += '\n;Object.assign(this,{CONCEPTS,QUIZ,PRACTICAL,THEORY,CODE49,KISA49,CATS,CATEGORY_INFO,catInfoHtml,gradeOne,verifySecurePattern,exCorrect,exAnsText,lineDiff,diffHtml,gnorm,kwScore,kwHit,stripCode,diffBadge,pracPool,codeBlock,codePane,addWrong,srsUpdate,srsDue,dueCount,wrongs,printSummary,wrongStats,topWeakHtml});';

const sandbox = { document, localStorage, window, alert, confirm, setInterval, clearInterval, setTimeout, console, Math, JSON, Array, Object, String, Number, Date };
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
let runErr = null;
try { vm.runInContext(code, sandbox); } catch(e){ runErr = e; }

const E = sandbox;
let fail = 0;
function ok(cond, msg){ if(!cond){ fail++; console.log('  ✗ '+msg); } }

console.log('=== ACADEMY v3 VALIDATION ===');
console.log('flow runtime error:', runErr ? (runErr.message) : 'none');
ok(!runErr, 'no runtime error on load');

// 데이터
ok(E.CONCEPTS.length===49, 'CONCEPTS=49 (got '+E.CONCEPTS.length+')');
ok(E.PRACTICAL.length===59, 'PRACTICAL=59 (got '+E.PRACTICAL.length+')');
ok(E.THEORY.length>=26, 'THEORY>=26 (got '+E.THEORY.length+')');
console.log('CONCEPTS',E.CONCEPTS.length,'QUIZ',E.QUIZ.length,'PRACTICAL',E.PRACTICAL.length,'THEORY',E.THEORY.length);

// PRACTICAL 스키마 무결성
let dErr=0;
const names = new Set(E.CONCEPTS.map(c=>c.name));
E.PRACTICAL.forEach(p=>{
  if(!['하','중','상'].includes(p.diff)){dErr++;console.log('  ✗ bad diff',p.id);}
  if(!Array.isArray(p.negKw)||!p.negKw.length){dErr++;console.log('  ✗ no negKw',p.id);}
  // 구두점만으로 이뤄진(정규화 시 빈 문자열) 키워드 금지 — '?' 처럼 항상매치되는 가짜 키워드 차단
  [].concat(p.safeCodeKeywords||[],p.reasonKeywords||[],p.negKw||[]).forEach(k=>{ if(E.gnorm(k)===''){dErr++;console.log('  ✗ keyword normalizes to empty (punctuation-only):',p.id,JSON.stringify(k));} });
  if(p.isTruePositive){
    if(!names.has(p.weaknessName)){dErr++;console.log('  ✗ weaknessName not in CONCEPTS:',p.id,p.weaknessName);}
    if(!p.safeCode){dErr++;console.log('  ✗ TP missing safeCode',p.id);}
    // safeCode 키워드 포함 확인 — 주석 제거 후에도 남아야 함(주석 전용 키워드 금지)
    (p.safeCodeKeywords||[]).forEach(k=>{ if(!E.kwHit(E.stripCode(p.safeCode),k)){dErr++;console.log('  ✗ safeCode kw only-in-comment or missing',p.id,k);} });
  } else {
    if(p.weaknessName||p.cwe||p.safeCode){dErr++;console.log('  ✗ FP should have empty name/cwe/safe',p.id);}
  }
});
console.log('data schema errors:', dErr); ok(dErr===0,'practical schema clean');

// gradeOne 채점 단위검증
const byId = id => E.PRACTICAL.find(p=>p.id===id);
let g=0,gf=0;
function chk(cond,msg){ g++; if(!cond){gf++;console.log('  ✗ grade:',msg);} }

E.PRACTICAL.forEach(p=>{
  if(p.isTruePositive){
    // 만점 답안
    const perfect=E.gradeOne(p,{tp:true,name:p.weaknessName,reason:p.reasonKeywords.join(' '),fix:p.safeCode});
    chk(perfect.score===100, p.id+' TP perfect should be 100 (got '+perfect.score+')');
    chk(perfect.tpOK, p.id+' TP perfect tpOK');
    chk(perfect.penalty===0, p.id+' TP perfect no penalty (got '+perfect.penalty+')');
    // 정·오탐 반대로 + 빈서술 => 낮은 점수
    const wrong=E.gradeOne(p,{tp:false,name:'',reason:'',fix:''});
    chk(wrong.score===0, p.id+' TP-as-FP empty => 0 (got '+wrong.score+')');
    // 부정키워드 감점: 정탐인데 "안전한 코드"라 서술
    const neg=E.gradeOne(p,{tp:true,name:p.weaknessName,reason:p.reasonKeywords.join(' ')+' 안전한 코드 오탐',fix:p.safeCode});
    chk(neg.penalty>0, p.id+' TP negKw penalty applied (got '+neg.penalty+')');
    chk(neg.score<perfect.score, p.id+' TP negKw lowers score');
  } else {
    const perfect=E.gradeOne(p,{tp:false,name:'',reason:p.reasonKeywords.join(' '),fix:''});
    chk(perfect.score===100, p.id+' FP perfect should be 100 (got '+perfect.score+')');
    chk(perfect.penalty===0, p.id+' FP perfect no penalty (got '+perfect.penalty+' hits '+JSON.stringify(perfect.negHits)+')');
    // 오탐인데 정탐이라 판별 => 판별 50 날아감
    const wrong=E.gradeOne(p,{tp:true,name:'SQL 삽입',reason:'',fix:''});
    chk(wrong.score<=50, p.id+' FP-as-TP <=50 (got '+wrong.score+')');
    // 부정키워드: 오탐인데 "취약/공격 가능"이라 서술 => 감점
    const neg=E.gradeOne(p,{tp:false,name:'',reason:p.reasonKeywords.join(' ')+' '+p.negKw[0],fix:''});
    chk(neg.penalty>0, p.id+' FP negKw penalty applied (got '+neg.penalty+' on '+p.negKw[0]+')');
  }
});
console.log('grading checks:', g, 'pass', g-gf, 'fail', gf);
ok(gf===0,'all grading checks pass');

// 정답 서술이 negKw에 걸리지 않는지 (오감점 방지) — 모든 문항 만점답안 penalty=0 위에서 검증됨. 추가로 reason 전체 점검:
let falsePen=0;
E.PRACTICAL.forEach(p=>{
  const r=E.gradeOne(p, p.isTruePositive?{tp:true,name:p.weaknessName,reason:p.explanation,fix:p.safeCode}:{tp:false,name:'',reason:p.explanation,fix:''});
  if(r.penalty>0){falsePen++;console.log('  ✗ explanation triggers penalty',p.id,JSON.stringify(r.negHits));}
});
console.log('explanation false-penalty:', falsePen); ok(falsePen===0,'no false penalty on model explanation');

// 인쇄/요약(PDF): printSummary가 49행 요약표를 printArea에 구성
E.printSummary();
const pa = document.getElementById('printArea').innerHTML;
ok(/ptbl/.test(pa), 'printSummary builds summary table');
ok((pa.match(/<tr>/g)||[]).length>=49, 'printSummary has >=49 rows (got '+((pa.match(/<tr>/g)||[]).length)+')');

// 7대 유형 개요(CATEGORY_INFO): 모든 카테고리에 정의/대표/진단 존재 + 배너 렌더
E.CATS.forEach(c=>{ const i=E.CATEGORY_INFO[c]; ok(i&&i.def&&i.ex&&i.diag, 'CATEGORY_INFO complete for '+c); });
ok(/진단 핵심/.test(E.catInfoHtml('입력검증')), 'catInfoHtml renders banner for a category');
ok(E.catInfoHtml('전체')==='', 'catInfoHtml empty for 전체');

// lineDiff
const d = E.lineDiff('a\nb\nc', 'a\nX\nc');
ok(d.some(x=>x[0]==='del') && d.some(x=>x[0]==='add') && d.some(x=>x[0]==='ctx'), 'lineDiff yields del/add/ctx');
const dh = E.diffHtml('a\nb','a\nc');
ok(/d-add/.test(dh) && /d-del/.test(dh), 'diffHtml has add/del spans');

// exCorrect 전수
const exItems = E.QUIZ.map(x=>Object.assign({type:'MC'},x)).concat(E.THEORY);
let exPass=0;
exItems.forEach(q=>{
  let correctAns;
  if(q.type==='MC') correctAns=q.a;
  else if(q.type==='OX') correctAns=q.a;
  else correctAns=(q.answers||[''])[0];
  if(E.exCorrect(q,correctAns)) exPass++;
  else console.log('  ✗ exCorrect failed:', q.type, (q.q||'').slice(0,30));
});
console.log('exCorrect:', exPass+'/'+exItems.length);
ok(exPass===exItems.length, 'exCorrect all pass');

// diffBadge
ok(/난이도 상/.test(E.diffBadge('상')), 'diffBadge renders');

// CODE49: 49개 약점 전부 코드 보유 + 카드 렌더 검증
const cnames = E.CONCEPTS.map(c=>c.name);
ok(Object.keys(E.CODE49).length===49, 'CODE49 has 49 entries (got '+Object.keys(E.CODE49).length+')');
let noCode=cnames.filter(n=>!E.CODE49[n]);
ok(noCode.length===0, 'every concept has CODE49 entry; missing: '+noCode.join(','));
let badJava=cnames.filter(n=>{const c=E.CODE49[n];return !c||!c.javaVuln||!c.javaSafe;});
ok(badJava.length===0, 'every concept has java vuln+safe; missing: '+badJava.join(','));
const pyMissing=cnames.filter(n=>{const c=E.CODE49[n];return !(c.pyVuln&&c.pySafe);});
console.log('python-missing (expected 4):', pyMissing.length, pyMissing.join(', '));
ok(pyMissing.length<=4, 'python missing within expected set');
// codeBlock 렌더: java 약점은 탭/코드/출처 포함, python 미수록은 note 포함
const hbJava=E.codeBlock(0, 'SQL 삽입');
ok(/진단가이드/.test(hbJava)&&/시큐어코딩/.test(hbJava)&&/안전하지 않은 코드/.test(hbJava)&&/안전한 코드/.test(hbJava), 'codeBlock(SQL) has java+python tabs and code panes');
const hbNoPy=E.codeBlock(1, '메모리 버퍼 오버플로우');
ok(/수록되어 있지 않|미수록/.test(hbNoPy) && !/Python · 시큐어코딩/.test(hbNoPy), 'codeBlock(memory) shows note, no python tab');
// javaLang 라벨 반영 (C 항목)
ok(/C · 진단가이드|C\/Java · 진단가이드/.test(E.codeBlock(2,'메모리 버퍼 오버플로우')), 'C javaLang label rendered');

// 오답노트 SRS(Leitner) 단위검증
(function(){
  E.wrongs.length = 0;                                  // 초기화
  E.addWrong({q:'[테스트] Q1', a:'A', e:'설명', tag:'1교시', code:''});
  ok(E.wrongs.length===1, 'SRS: addWrong adds new item');
  ok(E.wrongs[0].box===1, 'SRS: new item starts at box 1');
  ok(E.dueCount()===1, 'SRS: new item is immediately due');
  E.addWrong({q:'[테스트] Q1', a:'A', e:'설명', tag:'1교시', code:''});
  ok(E.wrongs.length===1, 'SRS: duplicate q does not duplicate entry');
  const w = E.wrongs[0];
  E.srsUpdate(w, true);
  ok(w.box===2, 'SRS: correct raises box to 2');
  ok(!E.srsDue(w), 'SRS: box 2 is not due immediately (scheduled ahead)');
  E.srsUpdate(w, false);
  ok(w.box===1, 'SRS: wrong resets box to 1');
  // 졸업: box5 정답 시 노트에서 제외 (wrongs는 filter로 재할당되므로 라이브 접근자 dueCount로 확인)
  w.box = 4; const grad = E.srsUpdate(w, true);
  ok(grad===true && E.dueCount()===0, 'SRS: box5 correct graduates (removed from notes)');
})();

// 7대 유형 오답 통계(wrongByCat) + 취약 유형 Top 3
(function(){
  Object.keys(E.wrongStats).forEach(k=>delete E.wrongStats[k]);
  E.addWrong({q:'[t] a',a:'',e:'',tag:'2교시',cat:'입력검증'});
  E.addWrong({q:'[t] b',a:'',e:'',tag:'2교시',cat:'입력검증'});
  E.addWrong({q:'[t] c',a:'',e:'',tag:'2교시',cat:'보안기능'});
  E.addWrong({q:'[t] d',a:'',e:'',tag:'1교시',cat:'법령'});  // 7대 유형 아님 → 미집계
  ok(E.wrongStats['입력검증']===2, 'wrongByCat counts 입력검증=2 (got '+E.wrongStats['입력검증']+')');
  ok(E.wrongStats['보안기능']===1, 'wrongByCat counts 보안기능=1');
  ok(!('법령' in E.wrongStats), 'wrongByCat ignores non-7-type cat (법령)');
  const tw=E.topWeakHtml();
  ok(/취약 유형 Top 3/.test(tw)&&/입력검증/.test(tw), 'topWeakHtml renders Top 3 (weakest first)');
})();

// LASHR 구조 검증: 매핑된 약점의 '모범답안'은 반드시 구조 통과해야 함(오탈락 0). 위반 시 만점 불가로 위 grading에서 이미 검출되나, 명시 검증:
(function(){
  const seen=new Set();
  E.PRACTICAL.filter(p=>p.isTruePositive).forEach(p=>{
    const v=E.verifySecurePattern(p.safeCode,p.lang,p.weaknessName);
    if(v.mapped){ seen.add(p.weaknessName); ok(v.ok, 'LASHR: model safeCode passes structure for '+p.id+' ('+p.weaknessName+')'); }
  });
  ok(seen.size>=5, 'LASHR maps at least 5 weakness types (got '+seen.size+')');
  // 키워드만 나열하고 구조가 없으면 개선코드는 상한(<=18)으로 캡 — SQL 삽입 예
  const sql=E.PRACTICAL.find(p=>p.isTruePositive&&p.weaknessName==='SQL 삽입');
  if(sql){
    const soup=E.gradeOne(sql,{tp:true,name:sql.weaknessName,reason:sql.reasonKeywords.join(' '),fix:(sql.safeCodeKeywords||[]).join(' ; ')});
    const cp=soup.parts.find(x=>x[0]==='개선 코드');
    ok(cp && cp[1]<=18, 'LASHR: keyword-soup-without-structure capped at <=18 (got '+(cp?cp[1]:'?')+')');
  }
})();

// 검증 연극 차단: 개선코드를 "주석으로만" 키워드를 써서 제출하면 코드 점수 0 이어야 함
(function(){
  const tp = E.PRACTICAL.find(p=>p.isTruePositive && (p.safeCodeKeywords||[]).length);
  if(!tp){ console.log('  (skip) no TP item with safeCodeKeywords'); return; }
  // 모든 키워드를 한 줄 주석(//)과 블록주석으로만 담은 가짜 답안
  const kws = tp.safeCodeKeywords.join(' ');
  const commentOnly = '// ' + kws + '\n/* ' + kws + ' */\n# ' + kws;
  const r = E.gradeOne(tp, {tp:true, name:tp.weaknessName, reason:tp.reasonKeywords.join(' '), fix: commentOnly});
  // 개선 코드 파트(만점 25) 점수가 0 이어야 한다
  const codePart = r.parts.find(pt=>pt[0]==='개선 코드');
  ok(codePart && codePart[1]===0, 'verification-theater: comment-only fix scores 0 on code ('+(codePart?codePart[1]:'?')+')');
  ok(r.score < 100, 'verification-theater: comment-only fix cannot reach 100 ('+r.score+')');
})();

console.log(fail===0 ? '\n✅ ACADEMY v3 VALIDATION PASS' : '\n❌ FAIL count='+fail);
process.exit(fail===0?0:1);
