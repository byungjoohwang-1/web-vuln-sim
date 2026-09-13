# -*- coding: utf-8 -*-
"""
16_zt-*.html  제로트러스트 시뮬레이터 생성기

왜 별도 생성기인가
------------------
제로트러스트는 지금까지 사이트에 한 페이지도 없던 영역이다(검색 0건).
관련 자료가 '성숙도 체크리스트' 형태라 그대로 옮기면 또 하나의 체크리스트가 될 뿐이라,
07_fin 시뮬레이터 템플릿(공격 시연 → 통제 적용 → 차단 확인)을 그대로 쓰고
제목·배지·테마만 제로트러스트 맥락으로 바꾼다. 템플릿 중복을 만들지 않으려고
gen_fin 의 PAGE 를 문자열 치환해 재사용한다.

출처 문서의 구조(6대 핵심 요소 + 교차 기능, 4단계 성숙도)만 참고하고
본문 문장·코드·시나리오는 전부 새로 작성한다(원문 비복제).

사용: python _gen/gen_zt.py            (기본 specs_zt)
      python _gen/gen_zt.py specs_zt_ot
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_fin  # noqa: E402  — 템플릿과 렌더 헬퍼를 재사용한다

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')

# 금융 전용 문구 → 제로트러스트 문구. 템플릿 구조(2탭·터미널 로그·코드 채점)는 그대로 둔다.
_SWAP = [
    ('<title>전자금융 보안: {title}</title>',
     '<title>제로트러스트: {title} · WEB-VULN-SIM</title>'),
    ('전자금융 보안 모의해킹 &middot; {title}',
     '제로트러스트 실습 &middot; {title}'),
    ('평가기준: <span class="risk">위험도 {risk}</span>',
     '성숙도: <span class="risk">{risk}</span>'),
    ('<strong>[심각] 전자금융 보안 기준 위반 감지</strong>',
     '<strong>[심각] 암묵적 신뢰가 악용되었습니다</strong>'),
    ('📚 금융보안원 평가기준 / 조치 가이드',
     '📚 제로트러스트 성숙도 해설 / 적용 가이드'),
    # 은행 네이비 → 제로트러스트(청록·보라) 계열
    ('--bank-primary:#003876', '--bank-primary:#134e4a'),
    ('--bank-secondary:#005eb8', '--bank-secondary:#0f766e'),
    # 접근성: 두 편집 영역에 이름을 준다(07_fin 은 생성 후 일괄 보정했지만,
    # 새로 만드는 쪽은 처음부터 템플릿에 넣어 재생성해도 사라지지 않게 한다)
    ('<textarea class="req-box" id="reqBox" spellcheck="false">',
     '<textarea class="req-box" id="reqBox" spellcheck="false" aria-label="요청 전문 편집기">'),
    ('<textarea id="codeEditor" class="code-editor">',
     '<textarea id="codeEditor" class="code-editor" aria-label="취약 코드 편집기">'),
    # 공용 크롬·진도 엔진을 템플릿에서 직접 싣는다(사후 일괄 주입에 의존하지 않는다)
    ('</body>',
     '<script src="/js/progress.js" defer></script>\n'
     '<script src="/js/soc-chrome.js" data-topbar="off" defer></script>\n'
     '</body>'),
]

PAGE = gen_fin.PAGE
for _a, _b in _SWAP:
    if _a not in PAGE:
        raise SystemExit('gen_fin 템플릿이 바뀌어 치환 대상을 찾지 못했습니다: %r' % _a[:40])
    PAGE = PAGE.replace(_a, _b)


def render(spec):
    """gen_fin.render 와 같은 필드를 쓰되 치환된 템플릿으로 그린다."""
    original = gen_fin.PAGE
    try:
        gen_fin.PAGE = PAGE
        return gen_fin.render(spec)
    finally:
        gen_fin.PAGE = original


def main():
    mods = sys.argv[1:] or ['specs_zt']
    total = 0
    for m in mods:
        for s in importlib.import_module(m).SPECS:
            path = os.path.join(OUT_DIR, s['file'])
            with open(path, 'w', encoding='utf-8') as f:
                f.write(render(s))
            print('wrote', s['file'])
            total += 1
    print('TOTAL', total)


if __name__ == '__main__':
    main()
