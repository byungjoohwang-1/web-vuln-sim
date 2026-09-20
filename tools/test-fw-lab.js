/**
 * 펌웨어·IoT 진단 실습(17_fw-*) 미션 자체 검증.
 *
 * 왜 필요한가 — srv-lab 과 같다: 판정 함수가 취약이라는데 조치를 적용해도 여전히 취약이거나,
 * 근거 보기에 정답이 아예 없는 실수를 브라우저로 일일이 눌러 보지 않고 잡는다.
 *
 * 검사 내용
 *   1) 초기 상태에서 판정이 'vuln' 이다 (점검할 거리가 실제로 있어야 미션이 성립)
 *   2) fix 를 적용하면 같은 함수가 'good' 을 돌려준다 (조치가 판정을 실제로 바꾼다)
 *   3) 정답 근거(evidence)가 보기(options) 안에 있다 (고를 수 없는 정답이면 안 된다)
 *   4) cmds 가 셸에서 실제로 동작한다 (지원하지 않는 명령을 안내하고 있지 않다)
 *   5) 근거로 지목한 문자열이 실제 명령 출력 안에 나타난다 (지어낸 근거가 아니다)
 *
 * 실행: node tools/test-fw-lab.js
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const PUB = path.join(__dirname, '..', 'public');

let pass = 0;
const fails = [];
function check(name, fn) {
  let d;
  try { d = fn(); } catch (e) { d = e.message; }
  if (d === true || d === undefined) { pass++; }
  else { fails.push(name + ' — ' + d); console.log('  FAIL  ' + name + ' — ' + d); }
}

function loadLab(dataFile) {
  const sandbox = { window: {}, console: console };
  sandbox.window.window = sandbox.window;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(PUB, 'js', 'fw-lab.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(PUB, 'js', dataFile), 'utf8'), sandbox);
  return { L: sandbox.window.WVS_FW_LAB, D: sandbox.window.FW_LAB_DATA };
}

const dataFiles = fs.readdirSync(path.join(PUB, 'js'))
  .filter((f) => /^fw-lab-.+\.js$/.test(f)).sort();

if (!dataFiles.length) {
  console.error('fw-lab 데이터 파일이 없습니다. python _gen/gen_fw_lab.py 를 먼저 실행하세요.');
  process.exit(1);
}

console.log('\n펌웨어·IoT 진단 실습 미션 검증');

let totalMissions = 0;
for (const df of dataFiles) {
  const { L, D } = loadLab(df);
  console.log('\n[' + df + '] ' + D.missions.length + '개 미션 · ' + (D.host.device || D.host.name));
  totalMissions += D.missions.length;

  const ids = D.missions.map((m) => m.id);
  check(df + ': 미션 ID 중복 없음', () => {
    const dup = ids.filter((x, i) => ids.indexOf(x) !== i);
    return dup.length === 0 || '중복: ' + dup.join(', ');
  });

  for (const m of D.missions) {
    /* 미션마다 파일시스템과 호스트 상태를 새로 만든다. 이미지 암호화·nvram 을 바꾸는
       미션이 있어 원본을 공유하면 앞 미션의 조치가 뒤 미션 판정을 조용히 바꾼다. */
    const mkFs = () => new L.FileSystem(
      JSON.parse(JSON.stringify(D.fs)), JSON.parse(JSON.stringify(D.host)));

    check(m.id + ' 초기 상태가 취약이다', () => {
      const v = m.verdict(mkFs());
      return v === 'vuln' || '초기 판정이 ' + v + ' — 점검할 거리가 없는 미션';
    });

    check(m.id + ' 정답 근거가 보기 안에 있다', () => {
      const missing = (m.evidence || []).filter((e) => m.options.indexOf(e) < 0);
      return missing.length === 0 || '보기에 없는 정답: ' + missing.join(' / ');
    });

    check(m.id + ' 보기가 2개 이상이다', () => (m.options || []).length >= 2 || '보기 부족');

    if (m.fix) {
      check(m.id + ' 조치를 적용하면 양호로 바뀐다', () => {
        const f = mkFs();
        m.fix(f);
        const v = m.verdict(f);
        return v === 'good' || '조치 후에도 ' + v + ' — 조치가 판정을 바꾸지 못함';
      });
      check(m.id + ' 조치 설명이 있다', () => (m.fixNote || '').length > 5 || 'fixNote 비어 있음');
    }

    check(m.id + ' 권장 명령이 셸에서 동작한다', () => {
      const f = mkFs();
      const sh = new L.Shell(f, f.host);
      const bad = (m.cmds || []).filter((c) => {
        const out = sh.run(c);
        return /지원하지 않는 명령|잘못된 패턴/.test(out);
      });
      return bad.length === 0 || '동작하지 않는 명령: ' + bad.join(' | ');
    });

    /* 근거로 고르게 한 문자열이 권장 명령들의 출력 어딘가에 실제로 나타나야 한다.
       (출력에 없는 근거를 정답이라고 하면 학습자가 찾을 수 없다) */
    check(m.id + ' 정답 근거가 명령 출력에 나타난다', () => {
      const f = mkFs();
      const sh = new L.Shell(f, f.host);
      const combined = (m.cmds || []).map((c) => sh.run(c)).join('\n');
      // 근거 보기는 "출력 줄 + 설명" 형태일 수 있으므로, 앞부분 핵심 토큰이 출력에 있으면 인정
      const missing = (m.evidence || []).filter((e) => {
        const key = String(e).split(' — ')[0].split(' (')[0].trim();
        return combined.indexOf(key) < 0;
      });
      return missing.length === 0 || '출력에 없는 근거: ' + missing.join(' / ');
    });

    check(m.id + ' 해설·브리핑이 비어 있지 않다', () =>
      ((m.why || '').length > 20 && (m.brief || '').length > 20) || '설명이 너무 짧음');
  }
}

console.log('\n' + (fails.length
  ? 'FAILED ' + fails.length + ' / ' + (pass + fails.length)
  : 'ALL ' + pass + ' CHECKS PASSED  (' + totalMissions + '개 미션)') + '\n');
process.exit(fails.length ? 1 : 0);
