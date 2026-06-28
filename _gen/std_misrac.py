# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 모음 — 파트1~3 병합(Dir + Rule 1~23).
각 룰: {id, cat, title, bad, good, why}. 규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성."""
from std_misrac_p1 import RULES as _p1
from std_misrac_p2 import RULES as _p2
from std_misrac_p3 import RULES as _p3
try:
    from std_misrac_manual import RULES as _pm  # PDF에 예제 없던 룰의 수기 보강
except Exception:
    _pm = []

RULES = _p1 + _p2 + _p3 + _pm
