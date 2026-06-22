# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 모음 — 파트1~4 병합. p4는 공식 사이트 대조로 보강한 누락 규칙.
각 룰: {id, cat, title, bad, good, why}. 규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성.
ID 중복은 자동 제거."""
from std_certcpp_p1 import RULES as _p1
from std_certcpp_p2 import RULES as _p2
from std_certcpp_p3 import RULES as _p3
from std_certcpp_p4 import RULES as _p4

_seen = set()
RULES = []
for _r in _p1 + _p2 + _p3 + _p4:
    if _r['id'] not in _seen:
        _seen.add(_r['id'])
        RULES.append(_r)
