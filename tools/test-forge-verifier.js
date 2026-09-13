#!/usr/bin/env node
/**
 * [G04] quiz-forge 형식 검사기 고정 평가 세트.
 *
 * 목적은 "검사기가 완벽하다"를 보이는 게 아니라, **무엇을 잡고 무엇을 못 잡는지**를
 * 수치로 남기는 것이다. 정답 모호·잘못된 해설·형식 오류를 각각 넣어
 * 검출(TP)·누락(FN)·오탐(FP)을 기록한다.
 *
 * 실행: node tools/test-forge-verifier.js
 */
'use strict';
const fs = require('fs');
const path = require('path');

/* quiz-forge.html 의 verify()/RISK_RE 를 그대로 꺼내 평가한다(복제하면 검사기와 어긋난다). */
const html = fs.readFileSync(path.resolve(__dirname, '..', 'public', 'quiz-forge.html'), 'utf8');
function extract(name, startRe) {
  const i = html.search(startRe);
  if (i < 0) throw new Error('not found: ' + name);
  let depth = 0, started = false, j = i;
  for (; j < html.length; j++) {
    const c = html[j];
    if (c === '{') { depth++; started = true; }
    else if (c === '}') { depth--; if (started && depth === 0) { j++; break; } }
  }
  return html.slice(i, j);
}
/* RISK_RE 는 정규식 리터럴 안에 {0,60} 같은 중괄호가 있어 중괄호 매칭으로는 못 자른다.
   줄 시작의 `];` 까지를 배열 리터럴로 본다. */
function extractArray(startRe) {
  const i = html.search(startRe);
  if (i < 0) throw new Error('RISK_RE not found');
  const end = html.indexOf('\n  ];', i);
  if (end < 0) throw new Error('RISK_RE end not found');
  return html.slice(html.indexOf('[', i), end + 4);
}
const riskSrc = extractArray(/var RISK_RE = \[/);
const verifySrc = extract('verify', /function verify\(q, ctx\)/);
// eslint-disable-next-line no-new-func
const verify = new Function('RISK_RE', verifySrc + '; return verify;')(eval(riskSrc));

const OK_MC = {
  title: '세션 고정 공격 방어',
  question: '로그인 성공 직후 세션 식별자를 재발급해야 하는 이유로 가장 적절한 것은 무엇인가?',
  options: ['공격자가 미리 심어둔 세션 식별자를 그대로 인증된 세션으로 쓸 수 있기 때문',
    '세션 저장소의 용량을 절약하기 위해서',
    '로그인 속도를 높이기 위해서',
    '쿠키 크기 제한을 지키기 위해서'],
  answer: 0,
  explanation: '로그인 전에 발급된 식별자를 그대로 유지하면 공격자가 피해자에게 자신이 아는 식별자를 심어둔 뒤 인증이 끝난 세션을 가로챌 수 있다. 인증 성공 시점에 새 식별자를 발급하면 이 경로가 끊긴다.',
  vuln_class: '세션 관리',
  snippet: 'app.post("/login", (req,res)=>{\n  if(check(req.body)) { req.session.user = req.body.id; }\n  res.redirect("/");\n});',
};
const CTX = { domain: '웹', type: 'mc' };

/* 각 케이스: [이름, 문항, 검사기가 잡아야 하는가] */
const CASES = [
  ['정상 문항', OK_MC, false],

  /* --- 형식 오류: 검사기가 잡아야 한다 --- */
  ['선택지 3개', { ...OK_MC, options: OK_MC.options.slice(0, 3) }, true],
  ['선택지 문자열 중복', { ...OK_MC, options: [OK_MC.options[0], OK_MC.options[0], OK_MC.options[2], OK_MC.options[3]] }, true],
  ['answer 인덱스 범위 초과', { ...OK_MC, answer: 7 }, true],
  ['answer 누락', { ...OK_MC, answer: undefined }, true],
  ['해설 지나치게 짧음', { ...OK_MC, explanation: '중요함.' }, true],
  ['title 없음', { ...OK_MC, title: '' }, true],
  ['vuln_class 없음', { ...OK_MC, vuln_class: '' }, true],
  ['question 지나치게 짧음', { ...OK_MC, question: '왜?' }, true],

  /* --- 리젝하지 않기로 한 것: 코드 위험 패턴 부재 ---
     세션 고정·권한 검사 누락처럼 어휘 패턴이 없는 취약점이 많아, 이걸 리젝 사유로 쓰면
     정상 문항까지 버린다(이 픽스처가 처음 실행됐을 때 '정상 문항'이 오탐으로 걸렸다).
     지금은 주의(note)로만 남기므로 여기서는 '통과'가 기대 동작이다. */
  ['코드에 위험 패턴 없음(주의만)', { ...OK_MC, snippet: 'const total = items.reduce((a,b)=>a+b.price,0);\nconsole.log("합계", total);\n// 단순 집계 로직이라 취약점과 무관하다\n// 여기에는 어떤 위험 패턴도 없다' }, false],

  /* --- 의미 오류: 형식 검사기로는 못 잡는다(한계를 기록한다) --- */
  ['정답이 둘 이상(의미상 모호)', {
    ...OK_MC,
    options: ['공격자가 심어둔 세션 식별자를 그대로 쓸 수 있기 때문',
      '인증 전후로 세션 식별자가 같으면 세션을 가로챌 수 있기 때문',   // 사실상 같은 뜻 = 정답 2개
      '로그인 속도를 높이기 위해서', '쿠키 크기 제한을 지키기 위해서'],
  }, false],
  ['해설 내용이 사실과 다름', {
    ...OK_MC,
    explanation: '세션 식별자는 로그인 후에도 절대 바꾸면 안 된다. 식별자를 바꾸면 서버가 사용자를 구분하지 못해 보안이 오히려 약해지기 때문이다. 따라서 고정된 값을 유지하는 것이 권장된다.',
  }, false],
  ['정답 인덱스가 틀린 보기를 가리킴', { ...OK_MC, answer: 2 }, false],
];

let tp = 0, fn = 0, fp = 0, tn = 0;
const rows = [];
for (const [name, q, shouldFlag] of CASES) {
  const errs = verify(q, CTX);
  const flagged = errs.length > 0;
  let verdict;
  if (shouldFlag && flagged) { tp++; verdict = '검출'; }
  else if (shouldFlag && !flagged) { fn++; verdict = '누락(FN)'; }
  else if (!shouldFlag && flagged) { fp++; verdict = '오탐(FP)'; }
  else { tn++; verdict = '통과'; }
  rows.push({ name, verdict, first: errs[0] ? errs[0].join(': ') : '' });
}

console.log('quiz-forge 형식 검사기 고정 평가\n');
for (const r of rows) console.log('  %s %s %s', r.verdict.padEnd(9), r.name.padEnd(26), r.first);
console.log('\n  검출 %d · 정상통과 %d · 누락 %d · 오탐 %d', tp, tn, fn, fp);

/* 형식 오류는 전부 잡아야 하고, 정상 문항을 잘못 걸러선 안 된다. */
const formatCases = CASES.filter(([, , f]) => f).length;
const okCase = rows.find((r) => r.name === '정상 문항');
let bad = 0;
if (tp !== formatCases) { console.error('\nFAIL 형식 오류 %d건 중 %d건만 검출', formatCases, tp); bad++; }
if (okCase.verdict !== '통과') { console.error('\nFAIL 정상 문항을 오탐'); bad++; }

/* 의미 오류는 이 검사기의 범위 밖이다 — 통과하는 것이 "정상"이며, 그 사실을 명시적으로 남긴다.
   나중에 의미 검사를 추가하면 이 목록이 회귀 기준이 된다. */
const semantic = rows.filter((r) => ['정답이 둘 이상(의미상 모호)', '해설 내용이 사실과 다름', '정답 인덱스가 틀린 보기를 가리킴', '코드에 위험 패턴 없음(주의만)'].includes(r.name));
console.log('\n  [알려진 한계] 형식 검사기가 통과시키는 의미 오류 %d건:', semantic.filter((r) => r.verdict === '통과').length);
for (const r of semantic) console.log('    - %s → %s', r.name, r.verdict);
console.log('  → 이래서 UI 배지를 "형식 검사 통과"로만 표기한다(내용 정확성은 미검증).');

process.exit(bad ? 1 : 0);
