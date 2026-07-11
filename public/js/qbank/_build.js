// Rebuilds ../academy-data-ext.js from all part files + merge finalizer.
const fs = require('fs');
const path = require('path');
const dir = __dirname;
const parts = ['partA','partB','partC','partD','partE_time','partE_err','partE_encap','partE_api'];

const header = `// Auto-generated extended question bank (객관식/주관식 대량 추가) — Java/Python 중심
// 8개 파트 병합(입력검증/보안기능/코드결함/시간상태/에러처리/캡슐화/API오용/법령·개념·진단·설계) + 중복 제거
`;

let body = '';
for (const p of parts) {
  let src = fs.readFileSync(path.join(dir, p + '.js'), 'utf8').trim();
  body += `\n// ===== ${p} =====\n` + src + '\n';
}

const finalizer = `

(function(){
  var D = window.ACADEMY_DATA, Q = window.__QBANK;
  if(!D || !Q){ return; }
  var norm = function(s){ return (s||"").replace(/\\s+/g," ").trim(); };
  var seenQ = {}; D.QUIZ.forEach(function(x){ seenQ[norm(x.q)] = 1; });
  var addQ = 0;
  (Q.QUIZ||[]).forEach(function(x){ var k=norm(x.q); if(!seenQ[k]){ seenQ[k]=1; D.QUIZ.push(x); addQ++; } });
  var seenT = {}; D.THEORY.forEach(function(x){ seenT[norm(x.q)] = 1; });
  var addT = 0;
  (Q.THEORY||[]).forEach(function(x){ var k=norm(x.q); if(!seenT[k]){ seenT[k]=1; D.THEORY.push(x); addT++; } });
  try { if (typeof console!=="undefined" && console.debug) console.debug("[qbank] +"+addQ+" QUIZ, +"+addT+" THEORY"); } catch(e){}
})();
`;

const out = header + body + finalizer;
fs.writeFileSync(path.join(dir, '..', 'academy-data-ext.js'), out, 'utf8');

// Validate: load QBANK-only to count raw items
global.window = {};
require('../academy-data-ext.js');
console.log('RAW __QBANK QUIZ', window.__QBANK.QUIZ.length, 'THEORY', window.__QBANK.THEORY.length);
