#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_ai-* 개념 카드에 학습 경로 스크립트를 주입한다 (AI 개편안 A-05).

난이도, 예상 시간, 선수 개념, 이전-다음은 js/ai-track.js 한 곳에 있고
js/ai-card.js 가 그것을 읽어 화면에 얹는다. 페이지 구조는 건드리지 않는다.

멱등이다.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(os.path.dirname(HERE), 'public')

TAGS = ('<script src="/js/ai-track.js" defer></script>\n'
        '<script src="/js/ai-card.js" defer></script>')

PAT = re.compile(r'^13_ai-ai\d+\.html$')


def main():
    names = sorted(n for n in os.listdir(PUB) if PAT.match(n))
    added = kept = nobody = 0
    for name in names:
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8', errors='replace') as f:
            doc = f.read()
        if 'js/ai-card.js' in doc:
            kept += 1
            continue
        idx = doc.rfind('</body>')      # 정규식 치환 금지 (QA N-05)
        if idx < 0:
            nobody += 1
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc[:idx] + TAGS + '\n' + doc[idx:])
        added += 1
    print('AI 학습 경로 주입: 추가 %d, 이미 있음 %d, </body> 없음 %d (대상 %d)'
          % (added, kept, nobody, len(names)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
