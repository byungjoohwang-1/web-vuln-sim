# -*- coding: utf-8 -*-
"""전자금융기반시설 점검항목 → public/js/fin-eval-items.json 생성.

_gen/fin/spec_*.py 의 ITEMS 를 모두 모아 도메인 순서(원본 워크북 시트 순서)대로 출력한다.
스펙 파일을 추가하면 자동으로 포함된다.
"""
import importlib
import json
import os
import pkgutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from fin._common import DOMAINS  # noqa: E402

OUT = os.path.join(BASE, '..', 'public', 'js', 'fin-eval-items.json')

NOTICE = (
    "금융 분야 취약점 평가에서 다루는 '점검 영역의 구성'만 참고하여 본 프로젝트가 자체 재작성한 "
    "교육용 콘텐츠입니다. 외부 기준 문서의 문항·해설 문장을 옮기지 않았으며, 각 항목의 제목·위험 설명·"
    "점검 방법·조치 방안은 모두 자체 작성입니다. 인용한 법령 조항은 공개 법령입니다. "
    "실제 평가·인증은 공식 기준과 자격을 갖춘 평가자를 따라야 합니다."
)


def collect():
    items, seen = [], {}
    mods = []
    for m in pkgutil.iter_modules([os.path.join(BASE, 'fin')]):
        if m.name.startswith('spec_'):
            mods.append(m.name)
    for name in sorted(mods):
        mod = importlib.import_module(f'fin.{name}')
        for it in getattr(mod, 'ITEMS', []):
            if it['id'] in seen:
                raise SystemExit(f"duplicate id {it['id']} in {name} (first in {seen[it['id']]})")
            seen[it['id']] = name
            items.append(it)
    order = {k: i for i, (k, *_rest) in enumerate(DOMAINS)}
    items.sort(key=lambda x: (order.get(x['d'], 99), x['id']))
    return items


def main():
    items = collect()
    doms = [{'k': k, 'name': n, 'icon': ic, 'desc': d} for (k, n, ic, d) in DOMAINS]
    counts = {}
    for it in items:
        counts[it['d']] = counts.get(it['d'], 0) + 1
    for d in doms:
        d['count'] = counts.get(d['k'], 0)
    payload = {
        'title': '전자금융기반시설 보안 점검 학습',
        'notice': NOTICE,
        'version': '2026-edu',
        'count': len(items),
        'domains': doms,
        'items': items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f'fin-eval: {len(items)} items -> {os.path.relpath(OUT, BASE)}')
    for d in doms:
        # 콘솔 인코딩이 이모지를 못 받는 환경(cp949 등)이 있어 이름만 출력한다.
        print(f"  {d['k']:<4} {d['name']:<22} {d['count']:>4}")


if __name__ == '__main__':
    main()
