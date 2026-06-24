# -*- coding: utf-8 -*-
"""전 public/*.html 에 favicon 링크를 멱등 주입.
브라우저 기본 /favicon.ico 404 방지 + 브랜딩. SVG favicon(모든 최신 브라우저 지원).
이미 rel=icon 이 있으면 건너뜀. <head> 직후에 삽입."""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
LINK = '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
HEAD_RE = re.compile(r'(<head[^>]*>)', re.IGNORECASE)


def main():
    changed = skipped = 0
    for name in os.listdir(PUB):
        if not name.endswith('.html'):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            html = f.read()
        if 'rel="icon"' in html or "rel='icon'" in html or '/favicon.svg' in html:
            skipped += 1
            continue
        new, n = HEAD_RE.subn(r'\1' + LINK, html, count=1)
        if n == 0:
            skipped += 1
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        changed += 1
    print('inject_favicon: injected=%d skipped=%d' % (changed, skipped))


if __name__ == '__main__':
    main()
