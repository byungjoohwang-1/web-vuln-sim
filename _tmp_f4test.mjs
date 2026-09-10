import { readFileSync } from 'fs';
import { webcrypto } from 'crypto';

const assess = readFileSync('public/skill-assess.html', 'utf-8');
const verify = readFileSync('public/verify.html', 'utf-8');

// 1) canonical 필드 순서 문자열 비교 (발급측 vs 검증측)
const mA = assess.match(/return \[CRED_PREFIX([^\]]+)\]\.join\('\|'\)/);
const mV = verify.match(/return \[SKILL_HASH_PREFIX([^\]]+)\]\.join\('\|'\)/);
if (!mA || !mV) { console.error('FAIL: canonical function not found'); process.exit(1); }
const norm = s => s.replace(/\s+/g, '').replace(/c\./g, '');
const fa = norm(mA[1]).split(',');
const fv = norm(mV[1]).split(',');
console.log('issuer fields :', fa.join(','));
console.log('verifier fields:', fv.join(','));
if (fa.join('|') !== fv.join('|')) { console.error('FAIL: canonical field mismatch'); process.exit(1); }
console.log('PASS canonical field order identical');

// 2) isSkill 판별 + 해시 왕복 (발급→URL 페이로드→검증 재계산)
const CRED_PREFIX = 'WVS-ASSESS-v1';
const credCanonical = c => [CRED_PREFIX, c.name, c.certId, c.date, c.score, c.pct, c.tier, c.axes, c.dur, c.flags].join('|');
const b64urlEncode = o => btoa(unescape(encodeURIComponent(JSON.stringify(o)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const b64urlDecode = s => { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return decodeURIComponent(escape(atob(s))); };
const sha256Hex = async str => { const buf = await webcrypto.subtle.digest('SHA-256', new TextEncoder().encode(str)); return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join(''); };

const cred = { t: 'WVS-SKILL', v: 1, name: '홍길동', certId: 'WVS-SKILL-2026-AB12CD', date: '2026-09-10', score: 73, pct: 78.4, tier: 2, axes: 'inj72,xss45,auth80,authz61,cry88,rob70,cfg55,ai40', dur: 512, flags: 1 };
const hash = await sha256Hex(credCanonical(cred));
cred.hash = hash;
const d = b64urlEncode(cred), h = hash;
// verify 측 재현
const parsed = JSON.parse(b64urlDecode(d));
const recomputed = await sha256Hex(credCanonical(parsed));
console.log('hash        :', hash.slice(0, 20) + '…');
console.log('integrity   :', recomputed === h && recomputed === parsed.hash ? 'OK' : 'BROKEN');
if (!(recomputed === h && recomputed === parsed.hash)) process.exit(1);

// 변조 감지: 점수 73→95
const tampered = { ...parsed, score: 95 };
const th = await sha256Hex(credCanonical(tampered));
console.log('tamper check:', th === h ? 'NOT DETECTED (FAIL)' : 'detected (OK)');
if (th === h) process.exit(1);
console.log('PASS issue→URL→verify roundtrip + tamper detection');

// 3) pctile 단조성/합리성 (페이지 코드에서 NORM 추출)
const nm = assess.match(/var NORM=(\[\[[\s\S]*?\]\]);/);
const NORM = JSON.parse(nm[1].replace(/\s+/g, ''));
function pctile(x) {
  if (x <= NORM[0][0]) return NORM[0][1];
  for (let i = 1; i < NORM.length; i++) if (x <= NORM[i][0]) { const a = NORM[i - 1], b = NORM[i]; return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); }
  return 99.7;
}
let mono = true;
for (let x = 0; x <= 100; x += 5) if (pctile(x) > pctile(x + 5) + 1e-9) mono = false;
console.log('pctile(50)=', pctile(50), 'pctile(80)=', pctile(80), 'monotonic:', mono);
if (!mono || pctile(50) < 30 || pctile(50) > 50 || pctile(80) < 80) process.exit(1);
console.log('PASS percentile monotonic & sane');

// 4) axes CSV 파싱 (slice(0,3)/slice(3))
function parseAxes(csv) { const m = {}; String(csv || '').split(',').forEach(p => { if (p.length > 3) m[p.slice(0, 3)] = parseInt(p.slice(3), 10) || 0; }); return m; }
const am = parseAxes(cred.axes);
const ids = ['inj', 'xss', 'auth', 'authz', 'cry', 'rob', 'cfg', 'ai'];
if (ids.some(i => am[i] === undefined)) { console.error('FAIL axes parse', am); process.exit(1); }
console.log('PASS axes CSV parse:', JSON.stringify(am));

// 5) 은행 무결성: 8축 × 5난이도, 각 문항 정답 1개·보기 4개
const bm = assess.match(/var BANK=(\{[\s\S]*?\n\};)/);
if (!bm) { console.error('FAIL: BANK not found'); process.exit(1); }
const sandbox = { Q: (cwe, q, opts, ex) => ({ cwe, q, opts, ex }), O: (t, ok) => ({ t, ok }) };
const BANK = (new Function('Q', 'O', 'return ' + bm[1].replace(/;$/, '')))(sandbox.Q, sandbox.O);
let nq = 0, bad = [];
for (const ax of Object.keys(BANK)) {
  for (const d of Object.keys(BANK[ax])) {
    const q = BANK[ax][d]; nq++;
    const oks = q.opts.filter(o => o.ok).length;
    if (oks !== 1 || q.opts.length !== 4 || !q.q.ko || !q.q.en || !q.ex.ko || !q.ex.en) bad.push(ax + ':' + d);
    q.opts.forEach(o => { if (!o.t.ko || !o.t.en) bad.push(ax + ':' + d + ':opt'); });
  }
}
console.log('bank items:', nq, 'axes:', Object.keys(BANK).length, 'bad:', bad.length ? bad.join(' ') : 'none');
if (nq !== 40 || Object.keys(BANK).length !== 8 || bad.length) process.exit(1);
console.log('PASS question bank 8 axes x 5 difficulty, 4 opts, exactly 1 correct, full KO/EN');

// 6) 스킬 자격 링크 대상 페이지 존재
import { existsSync } from 'fs';
const links = ['sim-sql-live.html', 'sim-xss-live.html', '03_code_weakpassword.html', '03_code_inapporiate_auth.html', 'sim-weak-crypto.html', '03_code_integer_overflow.html', 'sim-xxe.html', '13_ai-ai01.html'];
const missing = links.filter(f => !existsSync('public/' + f));
console.log('recommendation links missing:', missing.length ? missing.join(' ') : 'none');
if (missing.length) process.exit(1);
console.log('PASS recommendation links exist');
console.log('\nALL F4 CHECKS PASSED');
