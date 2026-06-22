# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 모음 — 파트1~3 병합(섹션 0~30+).
각 룰: {id, cat, title, bad, good, why}. 규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성.
ID 중복은 자동 제거(파트 간 우연한 겹침 방지)."""
from std_misracpp_p1 import RULES as _p1
from std_misracpp_p2 import RULES as _p2
from std_misracpp_p3 import RULES as _p3

_seen = set()
RULES = []
for _r in _p1 + _p2 + _p3:
    if _r['id'] not in _seen:
        _seen.add(_r['id'])
        RULES.append(_r)
