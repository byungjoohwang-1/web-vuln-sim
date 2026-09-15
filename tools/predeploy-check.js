#!/usr/bin/env node
/* 배포 전 드리프트 검사 묶음.
 *
 * firebase-tools 의 Windows predeploy 는 따옴표로 감싼 경로 뒤에 인자가 붙으면
 * 명령줄을 잘못 쪼갠다(spawn ENOENT). 그래서 "인자 없는 스크립트 하나"로 모아
 * 각 도구를 --check 모드로 대신 실행한다.
 */
'use strict';
const path = require('path');
const { spawnSync } = require('child_process');

const TOOLS = ['stamp-build.js', 'enrich-hub-keywords.js', 'eval-coach.js',
  'test-experience-stability.js'];
/* 인자 없이 도는 검사기들. firebase predeploy 가 Windows 에서 명령줄을 제대로
   못 쪼개는 일이 있어(아래 NOARG 참고) 한 진입점으로 모아 둔다. */
const NOARG = ['validate-public-site.js', 'test-platform-integration.js', 'test-a11y.js',
  'test-srv-lab.js', 'test-code-lab.js'];
const PY = ['gen_content_catalog.py', 'link_checklist_sims.py', 'gen_sources.py',
  'fix_guide_attribution.py'];   // 파이썬 생성기 드리프트 검사
let failed = 0;

for (const t of TOOLS) {
  const p = path.join(__dirname, t);
  const r = spawnSync(process.execPath, [p, '--check'], { stdio: 'inherit' });
  if (r.status !== 0) failed++;
}

for (const t of NOARG) {
  const p = path.join(__dirname, t);
  const r = spawnSync(process.execPath, [p], { stdio: 'inherit' });
  if (r.status !== 0) failed++;
}

for (const t of PY) {
  const p2 = path.join(__dirname, '..', '_gen', t);
  const r = spawnSync('python', [p2, '--check'], { stdio: 'inherit' });
  if (r.status !== 0) failed++;
}

if (failed) {
  console.error('\n배포 중단: 위 검사를 통과하지 못했습니다.');
  process.exit(1);
}
console.log('predeploy 검사 통과');
