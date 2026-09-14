# -*- coding: utf-8 -*-
"""통합 진도 엔진(js/progress.js)을 학습 페이지에 멱등 주입.
대상: 넘버드 콘텐츠(03_code/04_design/05_linux/06_db/07_fin/08_win/09_net/
10_sec/11_cloud/12_ics/13_ai/14_auto/15_privacy/16_zt) + sim-*.html / sim_*.html.
문서 마지막 </body> 직전에 삽입. 이미 주입돼 있으면 건너뜀.
도구/관리/랜딩 페이지는 대상 아님(엔진 칩은 학습 페이지에만).

QA N-05/I-04: 예전에는 정규식 sub(count=1) 으로 '첫 번째' </body> 를 치환했다.
시뮬레이터들은 자바스크립트 문자열 안에 mock HTML 을 담고 있어 첫 </body> 가
문자열 내부인 경우가 있고, 그러면 주입 태그의 </script> 가 스크립트 블록을
조기에 끝내 페이지가 통째로 죽는다. 반드시 rfind 로 문서 마지막을 찾는다.

QA N-12: 파일명 구분자가 섞여 있어(sim_insufficient_session.html) 밑줄 페이지가
누락됐다. 'sim_' 도 함께 받는다.
"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
TAG = '<script src="/js/progress.js" defer></script>'
LEARNABLE = re.compile(r'^(03_code|04_design|05_linux|06_db|07_fin|07_iss|07_srv|08_win|09_net|10_sec|11_cloud|12_ics|13_ai|14_auto|15_privacy|16_zt)')
CLOSE_BODY = '</body>'


def is_learnable(name):
    return bool(LEARNABLE.match(name)) or name.startswith(('sim-', 'sim_'))


def main():
    injected = skipped = nobody = 0
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html') or not is_learnable(name):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        if '/js/progress.js' in doc:
            skipped += 1
            continue
        idx = doc.rfind(CLOSE_BODY)   # 문서 '마지막' </body> — 문자열 안의 것을 피한다
        if idx < 0:
            nobody += 1
            continue
        new = doc[:idx] + TAG + '\n' + doc[idx:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        injected += 1
    print('inject_progress: injected=%d skipped=%d no_body=%d' % (injected, skipped, nobody))


if __name__ == '__main__':
    main()
