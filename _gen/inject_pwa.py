# -*- coding: utf-8 -*-
"""모바일/성능 메타 멱등 주입: theme-color + PWA manifest + 사용 origin preconnect.
preconnect 는 그 페이지가 실제로 참조하는 CDN/폰트 origin 에만 추가(렌더 블로킹 단축).
사용자가 동시 편집 중인 coding-standards.html 은 제외(레이스 회피)."""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
EXCLUDE = {'coding-standards.html'}
HEAD_RE = re.compile(r'(<head[^>]*>)', re.IGNORECASE)

PRE = {
    'fonts.googleapis.com': ['<link rel="preconnect" href="https://fonts.googleapis.com">',
                             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'],
    'cdnjs.cloudflare.com': ['<link rel="preconnect" href="https://cdnjs.cloudflare.com">'],
    'cdn.jsdelivr.net': ['<link rel="preconnect" href="https://cdn.jsdelivr.net">'],
}


def main():
    changed = 0
    for name in os.listdir(PUB):
        if not name.endswith('.html') or name in EXCLUDE:
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        add = []
        if 'name="theme-color"' not in doc:
            add.append('<meta name="theme-color" content="#0ea5e9">')
        if 'rel="manifest"' not in doc:
            add.append('<link rel="manifest" href="/manifest.json">')
        if 'rel="preconnect"' not in doc:
            for host, tags in PRE.items():
                if host in doc:
                    add += tags
        if not add:
            continue
        new, n = HEAD_RE.subn(r'\1' + ''.join(add), doc, count=1)
        if n == 0:
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        changed += 1
    print('inject_pwa: pages_updated=%d' % changed)


if __name__ == '__main__':
    main()
