# -*- coding: utf-8 -*-
"""03_code_*.html 에 '현업 진단 실습' 패널을 주입한다 (멱등).

주의 — CLAUDE.md 절대 원칙:
  문서 끝을 찾을 때는 반드시 rfind('</body>') 를 쓴다.
  이 페이지들은 자바스크립트 문자열 안에 예제 HTML(</body> 포함)을 담고 있어서,
  정규식 sub(count=1) 로 '첫 번째' </body> 를 치면 스크립트 한가운데가 갈라진다.
  실제로 그 버그로 페이지 6개가 죽은 적이 있다.

사용법:
    python inject_code_lab.py            # 주입
    python inject_code_lab.py --undo     # 제거 (되돌리기)
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
PUBLIC = os.path.join(HERE, '..', 'public')
DATA = os.path.join(PUBLIC, 'data', 'code-lab.json')

MARK = 'wvs-code-lab'
CLOSE_BODY = '</body>'

PANEL = (
    '\n<link rel="stylesheet" href="/css/code-lab.css">\n'
    '<section id="wvs-code-lab" data-lab-key="%s" aria-label="현업 진단 실습"></section>\n'
    '<script src="/js/code-lab.js" defer></script>\n'
)


def strip_panel(doc):
    """이전 주입분을 걷어낸다 (재주입 시 중복 방지)."""
    out = []
    for line in doc.split('\n'):
        if MARK in line or 'code-lab.css' in line or 'code-lab.js' in line:
            continue
        out.append(line)
    return '\n'.join(out)


def main():
    undo = '--undo' in sys.argv

    with open(DATA, encoding='utf-8') as f:
        keys = set(json.load(f).keys())

    injected = skipped = removed = nobody = 0
    for key in sorted(keys):
        path = os.path.join(PUBLIC, '03_code_%s.html' % key)
        if not os.path.exists(path):
            print('  MISSING 03_code_%s.html' % key)
            continue

        with open(path, encoding='utf-8') as f:
            doc = f.read()

        had = MARK in doc
        if undo:
            if not had:
                skipped += 1
                continue
            doc = strip_panel(doc)
            removed += 1
        else:
            if had:
                # 멱등: 기존 블록을 걷어내고 현재 형태로 다시 넣는다
                doc = strip_panel(doc)
            idx = doc.rfind(CLOSE_BODY)   # 문서 '마지막' </body> — 문자열 안의 것을 피한다
            if idx < 0:
                nobody += 1
                print('  NO BODY 03_code_%s.html' % key)
                continue
            doc = doc[:idx] + (PANEL % key) + doc[idx:]
            if had:
                skipped += 1
            else:
                injected += 1

        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc)

    if undo:
        print('inject_code_lab: removed=%d skipped=%d' % (removed, skipped))
    else:
        print('inject_code_lab: injected=%d refreshed=%d no_body=%d' % (injected, skipped, nobody))


if __name__ == '__main__':
    main()
