# -*- coding: utf-8 -*-
"""49개 보안약점별 가이드 코드 예제(안전하지 않은/안전한 코드).
출처: Java/C = 「소프트웨어 보안약점 진단가이드(2021)」, Python = 「Python 시큐어코딩 가이드(2023)」.
_code49_part1~7.py(서브에이전트 추출본)를 병합하여 CODE49[약점명]={javaLang,javaVuln,javaSafe,pyVuln,pySafe,note} 제공."""
import re as _re
import importlib as _il

CODE49 = {}
for _i in range(1, 8):
    _m = _il.import_module('_code49_part%d' % _i)
    for _k, _v in _m.PART.items():
        _key = _re.sub(r'\s*\(CWE-\d+\)\s*$', '', _k).strip()
        CODE49[_key] = _v
