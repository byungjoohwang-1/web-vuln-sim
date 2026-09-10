# -*- coding: utf-8 -*-
"""통합 진도 엔진(js/progress.js)을 학습 페이지에 멱등 주입.
대상: 넘버드 콘텐츠(03_code/04_design/05_linux/06_db/07_fin/08_win/09_net/
10_sec/11_cloud/12_ics/13_ai) + sim-*.html. </body> 직전에 삽입.
이미 주입돼 있으면 건너뜀. 도구/관리/랜딩 페이지는 대상 아님(엔진 칩은 학습 페이지에만).
"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
TAG = '<script src="/js/progress.js" defer></script>'
LEARNABLE = re.compile(r'^(03_code|04_design|05_linux|06_db|07_fin|08_win|09_net|10_sec|11_cloud|12_ics|13_ai)')
BODY_RE = re.compile(r'</body>', re.IGNORECASE)


def is_learnable(name):
    return bool(LEARNABLE.match(name)) or name.startswith('sim-')


def main():
    injected = skipped = nobody = 0
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html') or not is_learnable(name):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        if '/js/progress.js' in doc:
            skipped += 1
            continue
        if not BODY_RE.search(doc):
            nobody += 1
            continue
        new = BODY_RE.sub(TAG + '\n</body>', doc, count=1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        injected += 1
    print('inject_progress: injected=%d skipped=%d no_body=%d' % (injected, skipped, nobody))


if __name__ == '__main__':
    main()
