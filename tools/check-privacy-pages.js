/* 개인정보 도구 페이지 점검 — 언어 토글 링크 소실 함정 + 인라인 JS 문법.
 *
 * bilingual.js 는 data-en 요소의 innerHTML 을 통째로 갈아끼운다. 그 안에 <a> 를 두면
 * 영어로 바꾸는 순간 링크가 사라진다(복귀해도 data-ko 에 저장된 원본으로만 돌아옴).
 * 새 페이지를 추가할 때마다 눈으로 확인하는 대신 이 스크립트를 돌린다.
 *
 * 사용: node tools/check-privacy-pages.js [파일...]   (인자 없으면 public/privacy-*.html 전부)
 */
const fs = require('fs');
const path = require('path');

const PUB = path.join(__dirname, '..', 'public');

function targets(argv) {
  if (argv.length) return argv;
  return fs.readdirSync(PUB).filter(f => /^(privacy-|pia-|pseudonym-)/.test(f) && f.endsWith('.html'));
}

let risky = 0, syntax = 0, scanned = 0;

for (const f of targets(process.argv.slice(2))) {
  const html = fs.readFileSync(path.join(PUB, path.basename(f)), 'utf8');
  scanned++;

  // data-en 속성값 자체에 <a> 가 들어간 경우 (영어로 바꾸면 링크가 생겼다 사라졌다 한다)
  const attrRe = /\sdata-en\s*=\s*"([^"]*)"/gi;
  let m;
  while ((m = attrRe.exec(html))) {
    if (/<a[\s>]/i.test(m[1])) {
      risky++;
      console.log(`${f}: data-en 속성값에 <a> — ${m[1].slice(0, 80)}`);
    }
  }

  // data-en 요소의 본문에 <a> 가 들어간 경우
  const elRe = /<([a-z][a-z0-9]*)\b[^>]*\sdata-en\s*=[^>]*>([\s\S]*?)<\/\1>/gi;
  while ((m = elRe.exec(html))) {
    if (/<a[\s>]/i.test(m[2])) {
      risky++;
      console.log(`${f}: data-en 요소 안에 <a> — ${m[0].slice(0, 90).replace(/\s+/g, ' ')}`);
    }
  }

  // 인라인 스크립트 문법 (배포 후 백지 페이지가 되는 가장 흔한 원인)
  const scripts = [...html.matchAll(/<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/gi)];
  scripts.forEach((s, i) => {
    try { new Function(s[1]); }
    catch (e) { syntax++; console.log(`${f}: 인라인 스크립트 #${i} 문법 오류 — ${e.message}`); }
  });
}

console.log(`\n검사 ${scanned}개 파일 · data-en 링크 위험 ${risky}건 · 문법 오류 ${syntax}건`);
process.exit(risky || syntax ? 1 : 0);
