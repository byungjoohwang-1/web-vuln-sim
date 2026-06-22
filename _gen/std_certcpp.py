# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 모음 — 파트1~3 병합(DCL·OOP·EXP·CTR·STR·MEM·INT·ERR·CON·FIO·MSC).
각 룰: {id, cat, title, bad, good, why}. 규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성."""
from std_certcpp_p1 import RULES as _p1
from std_certcpp_p2 import RULES as _p2
from std_certcpp_p3 import RULES as _p3

RULES = _p1 + _p2 + _p3
