# -*- coding: utf-8 -*-
"""모든 공개 페이지에 SOC 크롬(통일 탑바 + Ctrl+K 팔레트) 스크립트를 주입한다.

규칙:
  - </body> 앞에 <script src="/js/soc-chrome.js" defer></script> 삽입
  - 자체 헤더를 쓰는 대표 페이지(vuln-hub/redteam/quiz-forge)는 data-topbar="off" (팔레트만)
  - 이미 soc-chrome.js가 참조된 페이지는 SKIP (멱등)

마커 없이 src 존재 여부로 판정하므로 재실행 안전.
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
MARK = 'soc-chrome.js'
TOPBAR_OFF = {'vuln-hub.html', 'redteam.html', 'quiz-forge.html'}
EXCLUDE = {'404.html', 'offline.html'}


def inject(path, fn):
    with open(path, encoding='utf-8', newline='') as f:
        h = f.read()
    if MARK in h:
        return 'skip'
    nl = '\r\n' if '\r\n' in h[:4000] else '\n'
    attrs = ' data-topbar="off"' if fn in TOPBAR_OFF else ''
    tag = ('<script src="/js/soc-chrome.js%s" defer></script>' % attrs)
    i = h.rfind('</body>')
    if i < 0:
        return 'nobody'
    h = h[:i] + tag + nl + h[i:]
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(h)
    return 'ok'


def main():
    stat = {'ok': 0, 'skip': 0, 'nobody': []}
    for fn in sorted(os.listdir(BASE)):
        if not fn.endswith('.html') or fn in EXCLUDE:
            continue
        r = inject(os.path.join(BASE, fn), fn)
        if r == 'ok':
            stat['ok'] += 1
        elif r == 'skip':
            stat['skip'] += 1
        else:
            stat['nobody'].append(fn)
    print('주입: %d · 스킵: %d · body없음: %s' % (stat['ok'], stat['skip'], stat['nobody'] or '없음'))


if __name__ == '__main__':
    main()
