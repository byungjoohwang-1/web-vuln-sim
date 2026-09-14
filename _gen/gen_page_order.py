#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""학습 페이지 순서 카탈로그 생성기 (js/shell.js 의 이전-다음 내비게이션 자료)

왜 생성기인가
    `public/js/page-order.json` 은 원래 손으로 만든 정적 파일이었다. 그래서 기둥이
    늘어나도 갱신되지 않았고, 자동차 61종·개인정보 34종·제로트러스트 8종이
    통째로 빠져 103개 페이지에서 이전-다음이 뜨지 않았다.
    (shell.js 는 목록에 없는 페이지면 페이저를 그리지 않고 조용히 지나간다.)

순서 규칙
    기둥 순서는 아래 PILLARS 고정, 기둥 안에서는 파일명 사전순.
    기존 307개 카탈로그가 정확히 이 규칙으로 만들어져 있음을 확인하고 맞췄으므로,
    재생성해도 기존 페이지의 앞뒤 관계는 바뀌지 않는다.

    시뮬레이터(sim-*, sim_*)는 넣지 않는다. 순서대로 훑는 읽을거리가 아니라
    개별 실습이고, 기존 카탈로그도 같은 기준이었다.

사용법
    python _gen/gen_page_order.py
    python _gen/gen_page_order.py --check   # 파일을 고치지 않고 최신인지만 본다
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, 'public')
OUT = os.path.join(PUBLIC, 'js', 'page-order.json')

# 학습 동선 순서. 앞의 것부터 이전-다음으로 이어진다.
PILLARS = [
    '03_code', '04_design',
    '05_linux', '06_db', '07_fin', '07_srv', '08_win', '09_net', '10_sec', '11_cloud', '12_ics',
    '13_ai',
    '14_auto', '15_privacy', '16_zt',
]

# 기둥에 속하지 않지만 동선에 포함하는 페이지. (기둥 접두사, 그 뒤에 붙일 파일들)
APPEND_AFTER = {
    '13_ai': ['ai-hub.html', 'ai-guardrail-lab.html'],
}


def build():
    names = set(n for n in os.listdir(PUBLIC) if n.endswith('.html'))
    order = []
    for p in PILLARS:
        order += sorted(n for n in names if n.startswith(p))
        for extra in APPEND_AFTER.get(p, []):
            if extra in names:
                order.append(extra)
    return order


def main():
    order = build()
    check = '--check' in sys.argv

    old = []
    if os.path.exists(OUT):
        try:
            with open(OUT, encoding='utf-8') as fh:
                old = json.load(fh)
        except (OSError, ValueError):
            old = []

    if check:
        if old == order:
            print('page-order OK  %d개' % len(order))
            return 0
        missing = [n for n in order if n not in old]
        stale = [n for n in old if n not in order]
        print('page-order 최신이 아니다: 누락 %d, 잔존 %d' % (len(missing), len(stale)))
        if missing:
            print('  누락 예: %s' % ', '.join(missing[:6]))
        if stale:
            print('  잔존 예: %s' % ', '.join(stale[:6]))
        print('  python _gen/gen_page_order.py 로 다시 만든다.')
        return 1

    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(order, fh, ensure_ascii=False, indent=0)
        fh.write('\n')

    added = len([n for n in order if n not in old])
    print('생성: js/page-order.json  %d개 (신규 %d)' % (len(order), added))
    for p in PILLARS:
        c = len([n for n in order if n.startswith(p)])
        if c:
            print('  %-12s %3d' % (p, c))
    return 0


if __name__ == '__main__':
    sys.exit(main())
