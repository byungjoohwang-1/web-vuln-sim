# -*- coding: utf-8 -*-
"""모든 public/*.html 에 공통 로그인 위젯 스크립트 태그를 주입(멱등).
마커 <!-- AUTH-WIDGET --> 로 중복 방지. </body> 직전에 삽입."""
import os, glob

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
MARK = '<!-- AUTH-WIDGET -->'
TAG = MARK + '\n<script type="module" src="auth-widget.js"></script>\n'

inj = skip = 0
for f in glob.glob(os.path.join(PUB, '*.html')):
    h = open(f, encoding='utf-8').read()
    if MARK in h:
        skip += 1; continue
    if '</body>' in h:
        h = h.replace('</body>', TAG + '</body>', 1)
    else:
        h = h + '\n' + TAG
    open(f, 'w', encoding='utf-8').write(h)
    inj += 1
print('injected=%d skipped=%d' % (inj, skip))
