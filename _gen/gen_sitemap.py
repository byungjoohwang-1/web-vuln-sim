# -*- coding: utf-8 -*-
"""public/*.html 로 sitemap.xml + robots.txt 생성."""
import os

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
BASE = 'https://vuln-sim.web.app'
# 진입 우선순위가 높은 허브 페이지
PRIORITY = {'index.html': '1.0', 'vuln-hub.html': '0.9',
            'secure-dev-portal.html': '0.9', 'secure-dev-academy.html': '0.9',
            'coding-standards.html': '0.8'}


def main():
    pages = sorted(f for f in os.listdir(PUB)
                   if f.endswith('.html') and f != '404.html')
    rows = []
    for f in pages:
        loc = BASE + '/' + ('' if f == 'index.html' else f)
        pr = PRIORITY.get(f, '0.5')
        rows.append('  <url><loc>%s</loc><priority>%s</priority></url>' % (loc, pr))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    with open(os.path.join(PUB, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(xml)
    robots = ('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE)
    with open(os.path.join(PUB, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots)
    print('gen_sitemap: %d urls -> sitemap.xml + robots.txt' % len(pages))


if __name__ == '__main__':
    main()
