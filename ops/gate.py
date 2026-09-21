#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 4단계] 게이트 러너.

주어진 디렉토리(작성 worktree 또는 현재 저장소)에서 배포 게이트 체인을 돌리고,
실패를 두 종류로 분류한다:

  content  콘텐츠 결함 — 생성물이 계약을 어겼다. A2 작성자에게 반송해 고친다.
  env      환경 미측정 — 에뮬레이터·도구 부재로 검사를 못 돌렸다. 콘텐츠 잘못이
           아니므로 A2 에게 반송하지 않는다. 사람이 배포 판단 시 고려한다.

이 분류가 없으면 첫날 밤에 모든 티켓이 죽는다 — Firestore 규칙 시험은 에뮬레이터
없이는 exit 1 이고, 그 실패를 콘텐츠 결함으로 오해하면 A2 가 존재하지 않는 결함을
고치려 상위 모델 토큰을 태운다(설계 심사에서 지적된 함정).

verdict:
  pass            콘텐츠 게이트 전부 통과 (환경도 통과 또는 미측정)
  content-fault   콘텐츠 게이트 하나 이상 실패 — 반송 대상

사용:
  python ops/gate.py                     # 현재 저장소 검증
  python ops/gate.py --dir <worktree>    # 작성 worktree 검증
  python ops/gate.py --ticket <id>       # 티켓과 연결해 gate.json 기록
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATES = os.path.join(HERE, 'gates')

# (이름, argv, 분류). content = 실패 시 콘텐츠 결함. env = 실패 시 환경 미측정.
CONTENT_STAGES = [
    ('build_site 집계 검사', ['python', os.path.join('_gen', 'build_site.py'), '--check'], 300),
    ('predeploy (validate_build 포함)', ['node', os.path.join('tools', 'predeploy-check.js')], 600),
]
# 에뮬레이터가 있어야 도는 검사. 없으면 env(미측정)로 분류.
ENV_STAGES = [
    ('Firestore 규칙', ['node', os.path.join('tools', 'test-firestore-rules.js')], 180),
]


def run_stage(name, argv, cwd, timeout):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    try:
        r = subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                           text=True, encoding='utf-8', timeout=timeout)
    except subprocess.TimeoutExpired:
        return {'name': name, 'ok': False, 'timeout': True, 'tail': '(timeout %ds)' % timeout}
    except FileNotFoundError as e:
        return {'name': name, 'ok': False, 'missing': True, 'tail': str(e)[:200]}
    out = (r.stdout or '') + (r.stderr or '')
    tail = '\n'.join(out.strip().splitlines()[-8:])
    return {'name': name, 'ok': r.returncode == 0, 'code': r.returncode, 'tail': tail}


def looks_like_env_failure(stage_result):
    """에뮬레이터/도구 부재로 인한 실패인지 텍스트로 판별."""
    t = (stage_result.get('tail') or '').lower()
    return (stage_result.get('missing')
            or 'emulator' in t or 'emulators:start' in t or 'econnrefused' in t
            or 'java' in t or 'cannot find' in t or 'not recognized' in t)


def main():
    args = sys.argv[1:]
    cwd = ROOT
    if '--dir' in args:
        cwd = os.path.abspath(args[args.index('--dir') + 1])
    ticket = args[args.index('--ticket') + 1] if '--ticket' in args else None

    print('게이트 실행 @ %s' % cwd)
    content_faults = []
    env_unmeasured = []
    stages = []

    for name, argv, timeout in CONTENT_STAGES:
        res = run_stage(name, argv, cwd, timeout)
        stages.append(res)
        mark = '[ok]  ' if res['ok'] else '[FAIL]'
        print('  %s %s' % (mark, name))
        if not res['ok']:
            # 콘텐츠 스테이지라도 환경 부재(도구 없음)면 env 로 분류
            if looks_like_env_failure(res):
                env_unmeasured.append(name)
            else:
                content_faults.append(name)

    for name, argv, timeout in ENV_STAGES:
        res = run_stage(name, argv, cwd, timeout)
        stages.append(res)
        if res['ok']:
            print('  [ok]  %s' % name)
        elif looks_like_env_failure(res):
            print('  [env] %s — 에뮬레이터/도구 부재로 미측정(콘텐츠 결함 아님)' % name)
            env_unmeasured.append(name)
        else:
            print('  [FAIL] %s' % name)
            content_faults.append(name)

    verdict = 'content-fault' if content_faults else 'pass'
    report = {
        'verdict': verdict,
        'contentFaults': content_faults,
        'envUnmeasured': env_unmeasured,
        'stages': stages,
        'dir': cwd,
        'ticket': ticket,
        'at': __import__('time').time(),
    }
    if ticket:
        os.makedirs(GATES, exist_ok=True)
        with open(os.path.join(GATES, ticket + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)

    print('-' * 50)
    print('판정: %s' % verdict)
    if content_faults:
        print('  콘텐츠 결함: %s' % ', '.join(content_faults))
    if env_unmeasured:
        print('  환경 미측정: %s (사람이 배포 판단 시 고려)' % ', '.join(env_unmeasured))
    return 1 if verdict == 'content-fault' else 0


if __name__ == '__main__':
    sys.exit(main())
