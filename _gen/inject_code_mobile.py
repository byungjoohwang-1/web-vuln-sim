# -*- coding: utf-8 -*-
"""03_code_*.html 50개에 모바일 교정 스타일시트를 붙인다 (멱등).

이 페이지들은 50개 중 16개만 gen_securecode.py 가 만들고 나머지 34개는 손으로 쓴 것이라
생성기 템플릿만으로는 전부를 덮을 수 없다. 그래서 공용 스타일시트 + 주입기 조합을 쓰고,
생성되는 16개는 gen_securecode.py 템플릿에도 같은 <link> 를 넣어 재생성 때 사라지지 않게 했다.

</head> 앞에 넣는다. 스타일은 문서 앞쪽에 있어야 본문 렌더 전에 적용된다.
(</body> 를 쓰지 않으므로 rfind 규칙과는 무관하지만, </head> 도 같은 이유로
 문자열 안의 것을 피하려고 find 가 아니라 '첫 번째 head 종료'만 신뢰하지 않고
 <head> 시작 이후를 기준으로 찾는다.)

사용법:
    python inject_code_mobile.py            # 주입
    python inject_code_mobile.py --undo     # 제거
"""
import glob
import os
import sys

PUBLIC = os.path.join(os.path.dirname(__file__), '..', 'public')
LINK = '<link rel="stylesheet" href="/css/code-page-mobile.css">'
MARK = 'code-page-mobile.css'


def main():
    undo = '--undo' in sys.argv
    injected = skipped = removed = nohead = 0

    for path in sorted(glob.glob(os.path.join(PUBLIC, '03_code_*.html'))):
        name = os.path.basename(path)
        with open(path, encoding='utf-8') as f:
            doc = f.read()

        if undo:
            if MARK not in doc:
                skipped += 1
                continue
            doc = '\n'.join(l for l in doc.split('\n') if MARK not in l)
            removed += 1
        else:
            if MARK in doc:
                skipped += 1
                continue
            head_start = doc.find('<head')
            if head_start < 0:
                nohead += 1
                print('  NO HEAD %s' % name)
                continue
            idx = doc.find('</head>', head_start)
            if idx < 0:
                nohead += 1
                print('  NO /HEAD %s' % name)
                continue
            doc = doc[:idx] + LINK + '\n' + doc[idx:]
            injected += 1

        with open(path, 'w', encoding='utf-8') as f:
            f.write(doc)

    if undo:
        print('inject_code_mobile: removed=%d skipped=%d' % (removed, skipped))
    else:
        print('inject_code_mobile: injected=%d skipped=%d no_head=%d' % (injected, skipped, nohead))


if __name__ == '__main__':
    main()
