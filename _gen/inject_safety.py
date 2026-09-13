#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""공격형 실습 페이지에 안전 고지 스크립트를 주입한다 (QA W-08, AI 개편안 A-03).

대상은 "공격을 직접 해 보는" 화면이다. 개념 해설 페이지에는 넣지 않는다.
고지는 브라우저에 한 번만 뜨고, 푸터의 "안전 고지 다시 보기" 로 다시 열린다.

멱등이다. 여러 번 돌려도 스크립트 태그는 한 개만 남는다.

사용법:
    python _gen/inject_safety.py          # 주입
    python _gen/inject_safety.py --list   # 대상 목록만 출력
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(os.path.dirname(HERE), 'public')

TAG = '<script src="/js/safety-notice.js" defer></script>'

# 공격을 직접 실행해 보는 화면
EXTRA = {
    'breach-campaign.html',
    'labs-live.html',
    'secure-code-lab.html',
    'ai-tutor.html',
    'ai-grader.html',
    'ai-guardrail-lab.html',
}


def targets():
    out = []
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html'):
            continue
        if name.startswith('sim-') or name.startswith('sim_') or name in EXTRA:
            out.append(name)
    return out


def main():
    names = targets()
    if '--list' in sys.argv:
        for n in names:
            print(n)
        print('대상 %d개' % len(names))
        return 0

    added = kept = nobody = 0
    for name in names:
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8', errors='replace') as f:
            doc = f.read()
        if 'js/safety-notice.js' in doc:
            kept += 1
            continue
        # 문서 마지막 </body> 를 기준으로 한다. 정규식 치환은 자바스크립트 문자열
        # 안의 </body> 를 잡아 페이지를 망가뜨린 전례가 있다 (QA N-05).
        idx = doc.rfind('</body>')
        if idx < 0:
            nobody += 1
            continue
        new = doc[:idx] + TAG + '\n' + doc[idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        added += 1

    print('안전 고지 주입: 추가 %d, 이미 있음 %d, </body> 없음 %d (대상 %d)'
          % (added, kept, nobody, len(names)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
