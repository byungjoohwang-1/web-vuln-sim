# -*- coding: utf-8 -*-
"""SEO 메타 멱등 주입: <title> 기반 description + Open Graph + Twitter Card.
이미 description/og:title 이 있으면 해당 항목은 건너뜀. </title> 직후 삽입."""
import os
import re
import html as _html

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
BASE = 'https://vuln-sim.web.app'
SITE = 'WEB-VULN-SIM 보안 학습 포털'
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)


def main():
    changed = 0
    for name in os.listdir(PUB):
        if not name.endswith('.html') or name == '404.html':
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        m = TITLE_RE.search(doc)
        if not m:
            continue
        title = re.sub(r'\s+', ' ', m.group(1)).strip()
        if not title:
            continue
        has_desc = bool(re.search(r'<meta[^>]+name="description"', doc, re.IGNORECASE))
        has_og = 'property="og:' in doc
        if has_desc and has_og:
            continue
        url = BASE + '/' + name
        t = _html.escape(title, quote=True)
        block = []
        if not has_desc:
            desc = _html.escape((title + ' · ' + SITE)[:300], quote=True)
            block.append('<meta name="description" content="' + desc + '">')
        if not has_og:
            desc_og = _html.escape((title + ' · ' + SITE)[:300], quote=True)
            block += [
                '<meta property="og:type" content="website">',
                '<meta property="og:site_name" content="' + _html.escape(SITE, quote=True) + '">',
                '<meta property="og:title" content="' + t + '">',
                '<meta property="og:description" content="' + desc_og + '">',
                '<meta property="og:url" content="' + url + '">',
                '<meta property="og:image" content="' + BASE + '/favicon.svg">',
                '<meta name="twitter:card" content="summary">',
            ]
        ins = '\n' + '\n'.join(block)
        doc = doc[:m.end()] + ins + doc[m.end():]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc)
        changed += 1
    print('inject_meta: pages_updated=%d' % changed)


if __name__ == '__main__':
    main()
