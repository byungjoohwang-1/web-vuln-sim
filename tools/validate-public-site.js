#!/usr/bin/env node
/*
 * Static smoke validation for the Firebase-hosted training portal.
 *
 * This is intentionally dependency-free so it can run in CI before a browser
 * E2E stage. It checks the things that most often break a static portal:
 * required top-level pages, local href/src targets, and local JS syntax.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const publicDir = path.join(root, 'public');

const requiredPages = [
  'vuln-hub.html',
  'training-dashboard.html',
  'secure-dev-academy.html',
  'exam-runner.html',
  'wrong-note.html',
  'certificate.html',
  'classroom.html',
  'instructor-dashboard.html',
  'coding-standards.html',
];

const ignoreSchemes = /^(?:https?:|mailto:|tel:|javascript:|data:|#)/i;
const attrRe = /\b(?:href|src)=["']([^"']+)["']/gi;
const inlineLocationRe = /location\.href\s*=\s*['"]([^'"]+)['"]/g;

function walk(dir, predicate, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, predicate, out);
    else if (predicate(p)) out.push(p);
  }
  return out;
}

function stripUrl(raw) {
  return raw.split('#')[0].split('?')[0].trim();
}

function isLocalTarget(raw) {
  const u = stripUrl(raw);
  return u && !ignoreSchemes.test(u) && !u.startsWith('//') &&
    !u.includes('${') && !u.includes('`') && !/\s/.test(u);
}

function resolveTarget(fromFile, raw) {
  const clean = stripUrl(raw);
  if (clean.startsWith('/')) return path.join(publicDir, clean.slice(1));
  return path.resolve(path.dirname(fromFile), clean);
}

const failures = [];

for (const page of requiredPages) {
  const p = path.join(publicDir, page);
  if (!fs.existsSync(p)) failures.push(`required page missing: ${page}`);
}

const htmlFiles = walk(publicDir, p => p.endsWith('.html'));
for (const file of htmlFiles) {
  const rel = path.relative(publicDir, file).replace(/\\/g, '/');
  const text = fs.readFileSync(file, 'utf8');
  // 인라인 <script> 내부의 href/src(시뮬레이터 가상 라우트 등)는 정적 검사에서 제외 —
  // 스크립트가 생성하는 링크는 각 페이지의 스모크 테스트가 담당한다.
  const noScript = text.replace(/<script[\s\S]*?<\/script>/gi, '');
  const refs = [];
  for (const re of [attrRe]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(noScript))) refs.push(m[1]);
  }
  inlineLocationRe.lastIndex = 0;
  let lm;
  while ((lm = inlineLocationRe.exec(text))) refs.push(lm[1]);
  for (const ref of refs) {
    if (!isLocalTarget(ref)) continue;
    const target = resolveTarget(file, ref);
    if (!target.startsWith(publicDir)) {
      failures.push(`${rel}: local reference escapes public/: ${ref}`);
      continue;
    }
    if (!fs.existsSync(target)) {
      failures.push(`${rel}: missing local target ${ref}`);
    }
  }
}

/*
 * 배포 차단 가드 A — 속성이 URL 안으로 섞여 들어간 깨진 src/href.
 * 실제 사고: <script src="/js/soc-chrome.js data-topbar="off"" defer>
 *   → 브라우저가 "/js/soc-chrome.js%20data-topbar=" 를 요청해 404, 공통 탑바/검색이 죽음.
 * 기존 isLocalTarget() 은 값에 공백이 있으면 "로컬 대상 아님"으로 보고 조용히 건너뛰어
 * 이 부류를 영원히 놓친다. 그래서 별도 검사로 명시적으로 잡는다.
 */
const ASSET_EXT = /\.(?:js|css|html|json|svg|png|jpe?g|gif|webp|ico|woff2?|xml|txt)$/i;
let malformedRefs = 0;
for (const file of htmlFiles) {
  const rel = path.relative(publicDir, file).replace(/\\/g, '/');
  const text = fs.readFileSync(file, 'utf8');
  const re = /\b(href|src)=["']([^"']+)["']/gi;
  let m;
  while ((m = re.exec(text))) {
    const attr = m[1];
    const val = m[2];
    if (!/\s/.test(val)) continue;            // 공백 없으면 정상
    if (ignoreSchemes.test(val.trim())) continue;
    const first = val.trim().split(/\s+/)[0];
    // 첫 토큰이 자산 경로처럼 생겼는데 뒤에 무언가 더 붙어 있으면 태그가 깨진 것
    if (ASSET_EXT.test(stripUrl(first)) || first.startsWith('/') || first.startsWith('./')) {
      malformedRefs++;
      failures.push(`${rel}: malformed ${attr} (attribute leaked into URL): ${JSON.stringify(val)}`);
    }
  }
}

/*
 * 배포 차단 가드 B — Subresource Integrity 해시 형식 검증.
 * 실제 사고: bootstrap.bundle.min.js 의 sha384 값에서 '/' 한 글자가 빠져(64→63자)
 *   브라우저가 스크립트를 차단 → 허브 카탈로그 전체가 클릭 불가.
 * 네트워크 없이도 base64 디코딩 길이로 손상을 잡을 수 있다(sha384 = 48바이트).
 * --online 을 주면 실제 리소스를 받아 digest 까지 대조한다.
 */
const DIGEST_BYTES = { sha256: 32, sha384: 48, sha512: 64 };
const sriTargets = [];
let sriChecked = 0;
for (const file of htmlFiles) {
  const rel = path.relative(publicDir, file).replace(/\\/g, '/');
  const text = fs.readFileSync(file, 'utf8');
  const tagRe = /<(?:script|link)\b[^>]*\bintegrity=["']([^"']+)["'][^>]*>/gi;
  let m;
  while ((m = tagRe.exec(text))) {
    const tag = m[0];
    const srcM = /\b(?:src|href)=["']([^"']+)["']/i.exec(tag);
    const url = srcM ? srcM[1] : null;
    for (const token of m[1].trim().split(/\s+/)) {
      sriChecked++;
      const dash = token.indexOf('-');
      const algo = dash > 0 ? token.slice(0, dash) : '';
      const b64 = dash > 0 ? token.slice(dash + 1) : '';
      const want = DIGEST_BYTES[algo];
      if (!want) {
        failures.push(`${rel}: unsupported SRI algorithm ${JSON.stringify(token.slice(0, 12))}`);
        continue;
      }
      if (!/^[A-Za-z0-9+/]+={0,2}$/.test(b64)) {
        failures.push(`${rel}: SRI digest is not valid base64 (${algo}) for ${url || 'unknown'}`);
        continue;
      }
      const bytes = Buffer.from(b64, 'base64').length;
      if (bytes !== want) {
        failures.push(
          `${rel}: corrupted SRI digest for ${url || 'unknown'} — ${algo} expects ${want} bytes, got ${bytes} (base64 len ${b64.length})`);
        continue;
      }
      if (url && /^https?:/i.test(url)) sriTargets.push({ rel, url, algo, b64 });
    }
  }
}

const jsFiles = walk(publicDir, p => p.endsWith('.js'));
for (const file of jsFiles) {
  const rel = path.relative(publicDir, file).replace(/\\/g, '/');
  try {
    execFileSync(process.execPath, ['--check', file], { stdio: 'pipe' });
  } catch (err) {
    const msg = Buffer.isBuffer(err.stderr) ? err.stderr.toString('utf8') : err.message;
    failures.push(`${rel}: JS syntax error: ${msg.trim().split(/\r?\n/)[0]}`);
  }
}

function report() {
  const summary = {
    publicDir,
    htmlFiles: htmlFiles.length,
    jsFiles: jsFiles.length,
    requiredPages: requiredPages.length,
    malformedRefs,
    sriDigestsChecked: sriChecked,
    sriRemoteVerified: remoteVerified,
    failures,
    ok: failures.length === 0,
  };
  console.log(JSON.stringify(summary, null, 2));
  process.exit(summary.ok ? 0 : 1);
}

let remoteVerified = 0;

// --online: CDN 리소스를 실제로 받아 digest 를 대조한다(네트워크 필요).
if (process.argv.includes('--online') && sriTargets.length) {
  const crypto = require('crypto');
  (async () => {
    const seen = new Map();
    for (const t of sriTargets) {
      const key = t.url + '|' + t.algo;
      if (seen.has(key)) {
        if (seen.get(key) !== t.b64) failures.push(`${t.rel}: SRI digest disagrees with another page for ${t.url}`);
        continue;
      }
      try {
        const res = await fetch(t.url);
        if (!res.ok) { failures.push(`${t.rel}: SRI target unreachable (${res.status}) ${t.url}`); continue; }
        const buf = Buffer.from(await res.arrayBuffer());
        const actual = crypto.createHash(t.algo).update(buf).digest('base64');
        if (actual !== t.b64) {
          failures.push(`${t.rel}: SRI digest MISMATCH for ${t.url}\n    expected-in-html: ${t.b64}\n    actual-from-cdn : ${actual}`);
        } else {
          remoteVerified++;
        }
        seen.set(key, t.b64);
      } catch (e) {
        failures.push(`${t.rel}: SRI fetch failed for ${t.url} (${e && e.message})`);
      }
    }
    report();
  })();
} else {
  report();
}
