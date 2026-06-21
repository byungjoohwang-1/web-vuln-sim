// 검증 하니스: secure-dev-academy.html 의 JS를 DOM shim 위에서 실행하고
// 데이터 정합성 / gradeOne 채점(감점 포함) / lineDiff / exCorrect 단위검증.
const fs = require('fs'), vm = require('vm'), path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'public', 'secure-dev-academy.html'), 'utf8');
const m = html.match(/<script>([\s\S]*)<\/script>\s*<\/body>/);
if (!m) { console.error('script block not found'); process.exit(1); }
let code = m[1];

// ---- DOM shim ----
function mkEl() {
  const el = {
    _html: '', textContent: '', value: '', disabled: false,
    classList: { _s: new Set(), add(){[].forEach.call(arguments,a=>this._s.add(a));}, remove(){[].forEach.call(arguments,a=>this._s.delete(a));}, toggle(c,f){if(f===undefined)f=!this._s.has(c);f?this._s.add(c):this._s.delete(c);return f;}, contains(c){return this._s.has(c);} },
    dataset: {}, style: {},
    setAttribute(){}, getAttribute(){return '';},
    querySelector(){return mkEl();}, querySelectorAll(){return [];},
    addEventListener(){}, scrollIntoView(){}, appendChild(){}, focus(){}
  };
  Object.defineProperty(el, 'innerHTML', { get(){return this._html;}, set(v){this._html=v;} });
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
const window = { scrollTo(){}, };
const alert = () => {};
const confirm = () => true;
const setInterval = () => 0, clearInterval = () => {}, setTimeout = (f)=>{ if(typeof f==='function') {} return 0; };

// 캡처: const 바인딩은 context global 에 붙지 않으므로 명시적으로 끌어온다
code += '\n;Object.assign(this,{CONCEPTS,QUIZ,PRACTICAL,THEORY,KISA49,gradeOne,exCorrect,exAnsText,lineDiff,diffHtml,gnorm,kwScore,kwHit,diffBadge,pracPool});';

const sandbox = { document, localStorage, window, alert, confirm, setInterval, clearInterval, setTimeout, console, Math, JSON, Array, Object, String, Number };
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
ok(E.PRACTICAL.length===30, 'PRACTICAL=30 (got '+E.PRACTICAL.length+')');
ok(E.THEORY.length===26, 'THEORY=26 (got '+E.THEORY.length+')');
console.log('CONCEPTS',E.CONCEPTS.length,'QUIZ',E.QUIZ.length,'PRACTICAL',E.PRACTICAL.length,'THEORY',E.THEORY.length);

// PRACTICAL 스키마 무결성
let dErr=0;
const names = new Set(E.CONCEPTS.map(c=>c.name));
E.PRACTICAL.forEach(p=>{
  if(!['하','중','상'].includes(p.diff)){dErr++;console.log('  ✗ bad diff',p.id);}
  if(!Array.isArray(p.negKw)||!p.negKw.length){dErr++;console.log('  ✗ no negKw',p.id);}
  if(p.isTruePositive){
    if(!names.has(p.weaknessName)){dErr++;console.log('  ✗ weaknessName not in CONCEPTS:',p.id,p.weaknessName);}
    if(!p.safeCode){dErr++;console.log('  ✗ TP missing safeCode',p.id);}
    // safeCode 키워드 포함 확인
    (p.safeCodeKeywords||[]).forEach(k=>{ if(!E.kwHit(p.safeCode,k)){dErr++;console.log('  ✗ safeCode missing kw',p.id,k);} });
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

console.log(fail===0 ? '\n✅ ACADEMY v3 VALIDATION PASS' : '\n❌ FAIL count='+fail);
process.exit(fail===0?0:1);
