/**
 * 폼 컨트롤 접근 가능한 이름 부여 (QA-P1-06).
 *
 * tools/test-a11y.js 가 "이름 없음"으로 잡은 input/select/textarea 에만 aria-label 을 넣는다.
 * 이름을 정하는 순서 — 앞에 있는 것일수록 사람이 실제로 보는 것에 가깝다.
 *   1) 반복되는 주요 컨트롤은 손으로 정한 이름(NAMES)
 *   2) 바로 앞에 붙은 <label>(for 없음) 이나 짧은 텍스트 블록
 *   3) placeholder 문구
 *   4) 위 셋 다 실패하면 건드리지 않고 보고한다 (억지로 id 를 사람 말처럼 꾸미지 않는다)
 *
 * 실행: node tools/fix-a11y-labels.js [--dry]
 */
'use strict';
const fs = require('fs');
const path = require('path');

const PUB = path.join(__dirname, '..', 'public');
const DRY = process.argv.includes('--dry');

/* 여러 페이지에 반복되는 컨트롤 — 추론보다 정확한 이름을 쓴다. */
const NAMES = {
  codeEditor: '취약 코드 편집기',
  codeEditorPython: 'Python 코드 편집기',
  codeEditorJava: 'Java 코드 편집기',
  editPython: 'Python 코드 편집기',
  editJava: 'Java 코드 편집기',
  editor: '코드 편집기',
  reqBox: 'HTTP 요청 편집기',
  burpRequestArea: 'HTTP 요청 편집기',
  aiKeyInput: 'AI API 키 입력',
  apiKey: 'AI API 키 입력',
  aiModelSelect: 'AI 모델 선택',
  model: 'AI 모델 선택',
  aiQuestion: 'AI 에게 보낼 질문',
  'terminal-input': '터미널 명령 입력',
  'cmd-input': '명령 입력',
  'f-search': '카탈로그 검색어',
  searchInput: '검색어',
  q: '검색어',
  'f-cat': '분류 필터',
  'f-lang': '언어 필터',
  'f-diff': '난이도 필터',
  'f-status': '상태 필터',
  userId: '사용자 아이디 입력',
  userPwd: '비밀번호 입력',
  attackerUrl: '공격자 서버 주소 입력',
  verifyUrl: '검증할 주소 입력',
};

const CONTROL_RE = /<(input|select|textarea)(?=[\s/>])([^>]*?)(\/?)>/gi;
const TYPE_RE = /\\?\btype\s*=\s*\\?["']([^"'\\]*)/i;
const TAG_TEXT_RE = /<(label|div|span|h[1-6]|td|th|p|b|strong)\b[^>]*>([^<]{1,40})<\/\1>\s*$/i;

function stripTemplate(s) {
  /* JS 템플릿 조각('+L(...)+' 등)이 섞인 텍스트는 이름으로 쓰지 않는다. */
  return s.replace(/&[a-z]+;/gi, ' ').replace(/\s+/g, ' ').trim();
}
function usable(s) {
  if (!s) return null;
  const t = stripTemplate(s);
  if (!t || t.length < 2 || t.length > 40) return null;
  if (/[+'"`${}]|\bL\(|\bfunction\b/.test(t)) return null;   // 코드 조각
  return t;
}

let added = 0;
const unresolved = [];
const touched = new Set();

for (const f of fs.readdirSync(PUB).filter((x) => x.endsWith('.html'))) {
  const p = path.join(PUB, f);
  const html = fs.readFileSync(p, 'utf8');

  const labelFor = new Set((html.match(/<label[^>]*\bfor\s*=\s*["']([^"']+)["']/gi) || [])
    .map((s) => (s.match(/for\s*=\s*["']([^"']+)["']/i) || [])[1]));
  const wrapped = new Set();
  const wr = /<label\b[^>]*>([\s\S]*?)<\/label>/gi;
  let w;
  while ((w = wr.exec(html))) {
    (w[1].match(/\bid\s*=\s*["']([^"']+)["']/gi) || [])
      .forEach((s) => wrapped.add((s.match(/["']([^"']+)["']/) || [])[1]));
  }

  const edits = [];
  CONTROL_RE.lastIndex = 0;
  let m;
  while ((m = CONTROL_RE.exec(html))) {
    const attrs = m[2] || '';
    const type = (attrs.match(TYPE_RE) || [])[1] || 'text';
    if (/^(hidden|submit|reset|button|image)$/i.test(type)) continue;
    if (/\b(aria-label|aria-labelledby|title)\s*=/.test(attrs)) continue;
    const id = (attrs.match(/\bid\s*=\s*["']([^"']+)["']/i) || [])[1];
    if (id && (labelFor.has(id) || wrapped.has(id))) continue;
    const b = html.lastIndexOf('<label', m.index), c = html.lastIndexOf('</label>', m.index);
    if (b > c) continue;                                    // <label>로 감싼 경우
    /* 코드 예시가 JS 문자열/JSON 안에 들어가 있으면 따옴표가 \" 로 이스케이프돼 있다.
       거기에 따옴표 그대로인 aria-label 을 끼워 넣으면 그 문자열이 끊겨 페이지 전체가 죽는다
       (secure-dev-academy.html 에서 실제로 발생). 그런 자리는 손대지 않는다. */
    if (attrs.includes('\\"') || attrs.includes("\\'")) continue;

    let name = id && NAMES[id];
    if (!name) {
      const before = html.slice(Math.max(0, m.index - 220), m.index);
      const tm = before.match(TAG_TEXT_RE);
      name = usable(tm && tm[2]);
    }
    if (!name) name = usable((attrs.match(/\bplaceholder\s*=\s*["']([^"']*)["']/i) || [])[1]);
    if (!name) {
      /* 마지막 수단: 컨트롤 바로 앞의 "사람이 읽는 마지막 글자 덩어리".
         태그가 몇 겹 끼어 있어도 화면에서는 그게 그 입력란의 설명이다.
         코드 조각이 섞이면 usable() 이 걸러낸다. */
      const before = html.slice(Math.max(0, m.index - 260), m.index);
      const texts = before.split(/<[^>]*>/).map((s) => s.trim()).filter(Boolean);
      for (let i = texts.length - 1; i >= 0 && i >= texts.length - 3; i--) {
        const cand = usable(texts[i].replace(/[:：*]\s*$/, ''));
        if (cand) { name = cand; break; }
      }
    }
    if (!name) { unresolved.push(f + ': <' + m[1] + (id ? ' id=' + id : '') + '>'); continue; }

    const insertAt = m.index + m[0].length - (m[3] ? 2 : 1);
    edits.push({ at: insertAt, text: ' aria-label="' + name.replace(/"/g, '&quot;') + '"' });
  }

  if (!edits.length) continue;
  let out = html;
  for (let i = edits.length - 1; i >= 0; i--) {
    out = out.slice(0, edits[i].at) + edits[i].text + out.slice(edits[i].at);
  }
  added += edits.length;
  touched.add(f);
  if (!DRY) fs.writeFileSync(p, out);
}

console.log((DRY ? '[dry-run] ' : '') + 'aria-label 부여 ' + added + '건 / 파일 ' + touched.size + '개');
console.log('이름을 정하지 못해 남긴 것: ' + unresolved.length);
if (unresolved.length) {
  const byFile = {};
  unresolved.forEach((u) => { const k = u.split(':')[0]; byFile[k] = (byFile[k] || 0) + 1; });
  Object.entries(byFile).sort((a, b) => b[1] - a[1]).slice(0, 12)
    .forEach(([k, v]) => console.log('   ' + String(v).padStart(3) + '  ' + k));
}
