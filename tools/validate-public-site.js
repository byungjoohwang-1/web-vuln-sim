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
  const refs = [];
  for (const re of [attrRe, inlineLocationRe]) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text))) refs.push(m[1]);
  }
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

const summary = {
  publicDir,
  htmlFiles: htmlFiles.length,
  jsFiles: jsFiles.length,
  requiredPages: requiredPages.length,
  failures,
  ok: failures.length === 0,
};

console.log(JSON.stringify(summary, null, 2));
process.exit(summary.ok ? 0 : 1);
