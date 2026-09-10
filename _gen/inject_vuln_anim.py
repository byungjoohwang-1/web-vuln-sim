# -*- coding: utf-8 -*-
"""취약점 설명 애니메이션(js/vuln-anim.js)을 넘버드 설명 페이지에 멱등 주입.
대상: 03_code/04_design/05_linux/06_db/07_fin/08_win/09_net/10_sec/11_cloud/12_ics/13_ai.
(sim-*는 이미 자체 인터랙션이 풍부하여 제외.) </body> 직전 삽입, 이미 있으면 skip.
"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
TAG = '<script src="/js/vuln-anim.js" defer></script>'
TARGET = re.compile(r'^(03_code|04_design|05_linux|06_db|07_fin|08_win|09_net|10_sec|11_cloud|12_ics|13_ai)')
BODY_RE = re.compile(r'</body>', re.IGNORECASE)


def main():
    injected = skipped = nobody = 0
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html') or not TARGET.match(name):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        if '/js/vuln-anim.js' in doc:
            skipped += 1
            continue
        if not BODY_RE.search(doc):
            nobody += 1
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(BODY_RE.sub(TAG + '\n</body>', doc, count=1))
        injected += 1
    print('inject_vuln_anim: injected=%d skipped=%d no_body=%d' % (injected, skipped, nobody))


if __name__ == '__main__':
    main()
