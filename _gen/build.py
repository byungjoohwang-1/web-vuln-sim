# -*- coding: utf-8 -*-
"""아카데미 빌드 파이프라인 일원화.

생성(gen_academy) → 주입(refcard·auth, 멱등) → 검증(node 하니스 + 회귀) 을 한 번에 실행한다.
중간 단계(예: auth 재주입)를 깜빡해 배포본이 깨지는 실수를 방지한다.

사용:
    python build.py            # 전체 파이프라인
    python build.py --no-check # 생성/주입만 (검증 생략)

주의: infra/fin/securecode 등 다른 도메인 생성기와 손으로 관리하는 페이지
(06_db-* 통합본, vuln-hub.html, Phase A 검증 페이지)는 이 스크립트가 건드리지 않는다.
"""
import os
import sys
import subprocess

# Windows 콘솔(cp949)에서도 한글/이모지 출력이 깨지지 않도록 UTF-8 강제
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))


def run(desc, cmd):
    print('\n=== %s ===' % desc, flush=True)
    r = subprocess.run(cmd, cwd=HERE)
    if r.returncode != 0:
        print('!! 실패: %s (exit %d)' % (desc, r.returncode))
        sys.exit(r.returncode)


def main():
    do_check = '--no-check' not in sys.argv

    # 1) 생성 — 아카데미 HTML 재생성(생성 시 주입물은 사라지므로 이후 재주입 필수)
    run('아카데미 생성 (gen_academy)', [sys.executable, 'gen_academy.py'])

    # 2) 주입 — 멱등(이미 있으면 skip), 전 public 페이지 대상
    run('레퍼런스 카드 주입 (inject_refcard)', [sys.executable, 'inject_refcard.py'])
    run('로그인 위젯 주입 (inject_auth)', [sys.executable, 'inject_auth.py'])

    if not do_check:
        print('\n빌드 완료 (검증 생략).')
        return

    # 3) 검증 — 데이터 정합성·채점·SRS 단위검증
    run('아카데미 검증 하니스 (node)', ['node', '_validate_academy.js'])
    # 4) 회귀 — 실습 검증기(vuln=fail, secure=pass)
    run('검증기 회귀 (_regression)', [sys.executable, '_regression.py'])

    print('\n✅ 빌드 + 전체 검증 통과. 배포 준비 완료.')
    print('   배포: firebase deploy --only hosting --project vuln-sim-test')


if __name__ == '__main__':
    main()
