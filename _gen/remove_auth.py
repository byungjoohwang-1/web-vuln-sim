# -*- coding: utf-8 -*-
"""모든 public/*.html 에서 로그인 위젯 주입(<!-- AUTH-WIDGET -->) 제거(멱등)."""
import os, glob

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
MARK = '<!-- AUTH-WIDGET -->'
BLOCK = MARK + '\n<script type="module" src="auth-widget.js"></script>\n'

rem = skip = 0
for f in glob.glob(os.path.join(PUB, '*.html')):
    h = open(f, encoding='utf-8').read()
    if MARK not in h:
        skip += 1; continue
    if BLOCK in h:
        h = h.replace(BLOCK, '')
    else:
        # 변형(공백/줄바꿈) 대비: 마커 라인 + 위젯 스크립트 라인 개별 제거
        h = (h.replace(MARK + '\n', '')
               .replace(MARK, '')
               .replace('<script type="module" src="auth-widget.js"></script>\n', '')
               .replace('<script type="module" src="auth-widget.js"></script>', ''))
    open(f, 'w', encoding='utf-8').write(h)
    rem += 1
print('removed=%d skipped=%d' % (rem, skip))
