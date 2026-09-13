# -*- coding: utf-8 -*-
"""공통 셸(skip link, 랜드마크, 푸터, 언어 동기화, 이전-다음)을 전 페이지에 멱등 주입한다.

QA 대응: I-05(다국어 상태 불일치), I-08(접근성 랜드마크 부재), I-12(공통 푸터와 학습 동선)

배경
    이 사이트는 HTML 404개를 생성기로 찍어 내는데 공통 템플릿이 없어서
    skip link 1/82, main 1/82, nav 0/82, footer 0/82 라는 상태였다.

방식
    1. <body ...> 바로 뒤에 skip link 와 공통 스타일을 넣는다(정적).
    2. 문서 마지막 </body> 직전에 js/shell.js 를 넣는다(런타임 랜드마크와 푸터).
    DOM 구조를 재배치하지 않는다. 페이지마다 손으로 맞춘 flex/grid 레이아웃이
    깨지는 쪽이 랜드마크를 정적 태그로 만드는 이득보다 크기 때문이다.

주의
    inject_progress.py 가 첫 번째 </body> 를 치환하다가 자바스크립트 문자열 안에
    </script> 를 박아 페이지 6개를 망가뜨린 적이 있다(QA N-05).
    그래서 이 스크립트는 항상 rfind 로 문서 마지막 </body> 만 대상으로 삼는다.
"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')

SHELL_JS = '<script src="/js/shell.js" defer></script>'
SKIP_MARK = 'class="wvs-skip"'

SKIP_HTML = (
    '\n<a class="wvs-skip" href="#wvs-main">본문 바로가기</a>\n'
    '<style id="wvs-shell-css">\n'
    '.wvs-skip{position:absolute;left:-9999px;top:0;z-index:100001;background:#0ea5e9;color:#04240f;'
    'font:700 14px/1 "Segoe UI","Malgun Gothic",sans-serif;padding:12px 18px;border-radius:0 0 10px 0;text-decoration:none}\n'
    '.wvs-skip:focus{left:0}\n'
    '#wvs-main:focus{outline:none}\n'
    ':focus-visible{outline:3px solid #38bdf8;outline-offset:2px}\n'
    '#wvs-footer{margin-top:36px;padding:22px 18px calc(22px + env(safe-area-inset-bottom));'
    'background:#0a101e;border-top:1px solid #1e293b;color:#94a3b8;'
    'font:13px/1.7 "Segoe UI","Malgun Gothic",sans-serif}\n'
    '#wvs-footer .wvs-foot-inner{max-width:1080px;margin:0 auto;text-align:center}\n'
    '#wvs-footer p{margin:0 0 8px}\n'
    '#wvs-footer a{color:#7dd3fc;text-decoration:none;margin:0 8px;white-space:nowrap}\n'
    '#wvs-footer a:hover{text-decoration:underline}\n'
    '#wvs-footer .wvs-foot-ver{color:#64748b;font-size:12px}\n'
    '#wvs-pager{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;'
    'max-width:1080px;margin:22px auto 0;padding:0 16px}\n'
    '#wvs-pager .wvs-pg{flex:0 0 auto;font:600 13.5px/1 "Segoe UI","Malgun Gothic",sans-serif;'
    'padding:10px 16px;border-radius:9px;text-decoration:none}\n'
    '#wvs-pager a.wvs-pg{background:#1e293b;color:#e2e8f0;border:1px solid #334155}\n'
    '#wvs-pager a.wvs-pg:hover{background:#334155}\n'
    '#wvs-pager .pos{color:#94a3b8;font-weight:400}\n'
    '#wvs-pager .off{visibility:hidden}\n'
    '</style>\n'
)

BODY_OPEN = re.compile(r'<body\b[^>]*>', re.IGNORECASE)


def inject(doc):
    changed = False
    if SKIP_MARK not in doc:
        m = BODY_OPEN.search(doc)
        if m:
            doc = doc[:m.end()] + SKIP_HTML + doc[m.end():]
            changed = True
    if SHELL_JS not in doc:
        i = doc.rfind('</body>')          # 반드시 문서 마지막 </body> (QA N-05)
        if i > 0:
            doc = doc[:i] + SHELL_JS + '\n' + doc[i:]
            changed = True
    return doc, changed


def main():
    done = skipped = nobody = 0
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html'):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        if '</body>' not in doc:
            nobody += 1
            continue
        new, changed = inject(doc)
        if not changed:
            skipped += 1
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        done += 1
    print('inject_shell: injected=%d skipped=%d no_body=%d' % (done, skipped, nobody))


if __name__ == '__main__':
    main()
