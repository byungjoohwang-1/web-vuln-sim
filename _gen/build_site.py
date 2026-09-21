#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 1단계] 사이트 집계 산출물 단일 진입점.

새 콘텐츠(페이지)가 public/ 에 추가된 뒤, 그 페이지를 사이트에 편입하는 데
필요한 집계 산출물을 고정 순서로 재생성하고 빌드 스탬프를 찍는다. 지금까지는
이 순서를 사람이 기억해 손으로 하나씩 돌렸고, 한 단계라도 빠지면 화면 수치나
이전-다음 이동이 조용히 어긋났다(기둥 목록 드리프트).

무엇을 하는가 (집계만):
  page-order -> registry -> progress-catalog -> search-index -> content-catalog
  -> sitemap -> sources -> 체크리스트 연결 -> 출처 꼬리말 -> 빌드 스탬프

무엇을 하지 않는가 (페이지 HTML 주입):
  inject_shell / inject_progress / inject_pwa / inject_favicon / inject_soc_chrome
  등은 각 콘텐츠 생성기 템플릿이 직접 넣는다. 그 편이 재생성에 안전하다 —
  후처리로만 붙인 주입은 다음 재생성 때 날아간다(fincloud 43종 회귀 사례).
  손으로 만든 페이지에 주입이 필요하면 해당 inject_*.py 를 개별로 실행한다.
  이 스크립트는 페이지 HTML 을 건드리지 않으므로 603개 페이지를 한 번에
  망가뜨릴 위험이 없다. 예외는 fix_guide_attribution(꼬리말 표준화, 멱등).

사용:
  python _gen/build_site.py          # 집계 재생성 + 스탬프
  python _gen/build_site.py --check  # 파일을 고치지 않고 드리프트만 검사(지원 단계만)

의존 순서 근거(실측):
  gen_registry 는 page-order.json 을 읽는다            -> page-order 가 먼저
  gen_content_catalog 는 progress-catalog.json 과
    search-index.json 을 읽는다                        -> 그 둘이 먼저
  나머지는 public/*.html 을 독립적으로 스캔한다
  stamp-build 는 모든 산출물이 확정된 뒤 맨 마지막
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECK = '--check' in sys.argv

# 자식 파이썬의 출력 인코딩을 UTF-8 로 고정한다. Windows 콘솔 기본 cp949 에서
# 생성기 로그의 특수문자가 UnicodeEncodeError 로 죽는 사례가 있었다.
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')

# (표시이름, argv, --check 지원 여부). --check 미지원 단계는 검사 모드에서
# 건너뛴다 — 그 드리프트는 validate_build.py --strict 가 별도로 잡는다
# (REGISTRY-DOMAIN-STALE / PAGE-ORDER-STALE / SITEMAP-STALE 등).
STEPS = [
    ('페이지 순서',     ['python', 'gen_page_order.py'],        True),
    ('레지스트리 수치',  ['python', 'gen_registry.py'],          False),
    ('진도 카탈로그',   ['python', 'gen_progress_catalog.py'],  False),
    ('검색 인덱스',     ['python', 'gen_search_index.py'],      False),
    ('콘텐츠 카탈로그',  ['python', 'gen_content_catalog.py'],   True),
    ('사이트맵',        ['python', 'gen_sitemap.py'],           False),
    ('출처 등록부',     ['python', 'gen_sources.py'],           True),
    ('체크리스트 연결',  ['python', 'link_checklist_sims.py'],   True),
    ('출처 꼬리말',     ['python', 'fix_guide_attribution.py'], True),
]
# stamp-build 는 node 이고 tools/ 에 있어 별도 처리. cwd=ROOT.
STAMP = ('빌드 스탬프', ['node', os.path.join('tools', 'stamp-build.js')], True)


def run(name, argv, supports_check, cwd):
    args = list(argv)
    if CHECK:
        if not supports_check:
            print('  [skip]  %s (--check 미지원 — validate_build --strict 가 검증)' % name)
            return True
        args.append('--check')
    r = subprocess.run(args, cwd=cwd, env=ENV)
    ok = r.returncode == 0
    print(('  [ok]    ' if ok else '  [FAIL]  ') + name)
    return ok


def main():
    print('=' * 58)
    print('build_site  (%s 모드)' % ('검사' if CHECK else '재생성'))
    print('=' * 58)
    failed = []
    for name, argv, supports in STEPS:
        if not run(name, argv, supports, HERE):
            failed.append(name)
            if not CHECK:
                # 생성 모드에서 한 단계가 실패하면 이후 집계가 오염되므로 즉시 중단.
                print('\n중단: "%s" 단계 실패. 위 오류를 고친 뒤 다시 실행하라.' % name)
                return 1

    # 빌드 스탬프는 모든 집계가 끝난 뒤.
    sname, sargv, ssup = STAMP
    if not run(sname, sargv, ssup, ROOT):
        failed.append(sname)

    print('-' * 58)
    if failed:
        print('실패 %d단계: %s' % (len(failed), ', '.join(failed)))
        if CHECK:
            print('재생성이 필요하다: python _gen/build_site.py')
        return 1
    print('완료: 집계 %d단계 + 빌드 스탬프' % len(STEPS))
    if not CHECK:
        print('다음: node tools/predeploy-check.js 로 배포 게이트를 확인하라.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
