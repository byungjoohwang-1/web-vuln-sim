# -*- coding: utf-8 -*-
"""취약점 설명 애니메이션(js/vuln-anim.js)을 넘버드 설명 페이지에 멱등 주입.
대상: 03_code/04_design/05_linux/06_db/07_fin/08_win/09_net/10_sec/11_cloud/12_ics/13_ai.
(sim-*는 이미 자체 인터랙션이 풍부하여 제외.) 문서 '마지막' </body> 직전 삽입, 이미 있으면 skip.

[2026-09-14] 예전에는 `BODY_RE.sub(..., count=1)` 로 **첫 번째** </body> 를 치환했다.
설명 페이지들은 자바스크립트 문자열 안에 예제 HTML 을 담고 있어서(예: 07_fin-ssi.html 의
`String page = "<html><body>" + safe + "</body></html>";`) 첫 </body> 가 문자열 내부인 경우가 있고,
그 자리에 <script> 태그가 끼면 문자열이 깨지면서 인라인 스크립트 전체가 SyntaxError 로 죽는다.
실제로 07_fin-ssi.html 과 03_code_xss.html 이 이 방식으로 깨졌다(배포 게이트가 잡음).
inject_progress.py 와 동일하게 rfind 로 문서 끝을 찾는다. CLAUDE.md 의 '절대 원칙'이기도 하다.
"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
TAG = '<script src="/js/vuln-anim.js" defer></script>'
TARGET = re.compile(r'^(03_code|04_design|05_linux|06_db|07_fin|08_win|09_net|10_sec|11_cloud|12_ics|13_ai|14_auto)')
CLOSE_BODY = '</body>'


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
        idx = doc.rfind(CLOSE_BODY)   # 문서 '마지막' </body> — 문자열 안의 것을 피한다
        if idx < 0:
            nobody += 1
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc[:idx] + TAG + '\n' + doc[idx:])
        injected += 1
    print('inject_vuln_anim: injected=%d skipped=%d no_body=%d' % (injected, skipped, nobody))


if __name__ == '__main__':
    main()
