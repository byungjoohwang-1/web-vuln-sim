# -*- coding: utf-8 -*-
"""[G06] 공통 콘텐츠 카탈로그 생성기 → public/data/content-catalog.json

왜 필요한가
-----------
검색(search-index) · 진도(progress-catalog) · AI 시나리오(scenarios) 가 서로 다른 목록을
따로 들고 있어서, 콘텐츠를 추가해도 학습 경험 전체로 연결되지 않았다.
여기서 **한 곳**으로 모아 두고, 기존 세 JSON 은 그대로 호환 출력으로 유지한다
(호환을 깨면 515개 페이지와 도구가 한꺼번에 영향을 받는다).

정직성 규칙 (재평가 문서 §8.1)
------------------------------
생성기는 **모르는 값을 지어내지 않는다.**
  - estimatedMinutes : 측정한 적이 없다 → null
  - reviewStatus     : 사람이 검토한 적이 없다 → "unreviewed"
  - validationKinds  : 서버가 실제로 채점하는 것만 넣는다 → 지금은 빈 배열
  - sourceIds        : 출처 대조를 안 했다 → 빈 배열
  - skills           : 근거가 있는 것(CWE)만 넣고 나머지는 비운다
추정으로 채우면 "검토 완료"처럼 보이는 가짜 신호가 생긴다.

사용: python _gen/gen_content_catalog.py [--check]
  --check 는 파일을 쓰지 않고 현재 산출물과 달라지는지만 본다(배포 게이트용).
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(BASE, '..', 'public')
OUT = os.path.join(PUB, 'data', 'content-catalog.json')

CHECK = '--check' in sys.argv

# 파일명 접두사 → (도메인, 학습 형태)
#   learningMode 는 페이지 계열에서 관찰 가능한 사실만 쓴다.
#     concept_simulation : 상태 전환·설명 위주의 개념 시뮬레이션
#     practice_tool      : 사용자가 직접 입력·조작하는 도구
DOMAIN_RULES = [
    ('03_code', 'appsec', 'concept_simulation'),
    ('04_design', 'appsec', 'concept_simulation'),
    ('05_linux', 'infra', 'concept_simulation'),
    ('06_db', 'infra', 'concept_simulation'),
    ('07_fin', 'financial', 'concept_simulation'),
    ('07_iss', 'financial', 'practice_tool'),
    ('07_srv', 'financial', 'practice_tool'),
    ('08_win', 'infra', 'concept_simulation'),
    ('09_net', 'infra', 'concept_simulation'),
    ('10_sec', 'infra', 'concept_simulation'),
    ('11_cloud', 'infra', 'concept_simulation'),
    ('12_ics', 'ot', 'concept_simulation'),
    ('13_ai', 'ai', 'concept_simulation'),
    ('14_auto', 'automotive', 'concept_simulation'),
    ('15_privacy', 'privacy', 'concept_simulation'),
    ('16_zt', 'zerotrust', 'concept_simulation'),
    ('sim-', 'appsec', 'concept_simulation'),
]
TOOL_PAGES = {
    'vulnlab.html': ('appsec', 'practice_tool'),
    'redteam.html': ('appsec', 'practice_tool'),
    'quiz-forge.html': ('appsec', 'practice_tool'),
    'incident.html': ('automotive', 'guided_incident'),
    'privacy-data-transfer.html': ('privacy', 'practice_tool'),
    'privacy-rights-desk.html': ('privacy', 'practice_tool'),
    'privacy-breach-72h.html': ('privacy', 'guided_incident'),
    'audit-ismsp-lab.html': ('governance', 'practice_tool'),
    'industry-tech-protect.html': ('governance', 'practice_tool'),
    # [G02 후속] 완료를 기록하면서도 카탈로그에 없던 도구들
    'ai-grader.html': ('appsec', 'practice_tool'),
    'lab-generator.html': ('appsec', 'practice_tool'),
    'skill-assess.html': ('appsec', 'practice_tool'),
    'fin-eval.html': ('financial', 'practice_tool'),
    'mp-assessment.html': ('governance', 'practice_tool'),
    'pia-assessment.html': ('privacy', 'practice_tool'),
    'privacy-breach-drill.html': ('privacy', 'guided_incident'),
    'privacy-consent-designer.html': ('privacy', 'practice_tool'),
    'privacy-policy-builder.html': ('privacy', 'practice_tool'),
    'privacy-policy-eval.html': ('privacy', 'practice_tool'),
    'privacy-processor-check.html': ('privacy', 'practice_tool'),
    'privacy-quiz.html': ('privacy', 'practice_tool'),
}


def load(rel):
    with open(os.path.join(PUB, rel), encoding='utf-8') as f:
        return json.load(f)


def classify(page):
    if page in TOOL_PAGES:
        return TOOL_PAGES[page]
    for pfx, dom, mode in DOMAIN_RULES:
        if page.startswith(pfx):
            return dom, mode
    return None, None


def slug(page):
    """안정적인 항목 ID. 의미 기반 ID(auto.ota.integrity)는 사람이 붙여야 하므로
    여기서는 파일명에서 기계적으로 만든다(추측하지 않는다)."""
    base = page[:-5] if page.endswith('.html') else page
    return base.replace('_', '-').replace('.', '-')


PRESERVE_FIELDS = ('sourceIds', 'reviewStatus')


def _keep_reviewed(items):
    """기존 카탈로그에 사람이 넣은 값이 있으면 그대로 살린다.

    생성기는 파일을 통째로 다시 쓴다. 그래서 손으로 검토해 넣은 출처 연결이
    다음 생성에서 조용히 사라졌다(배포 게이트가 drift 로 잡아냈다).
    기본값(빈 배열 / 'unreviewed')이 아닌 값만 보존한다.
    """
    path = OUT
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding='utf-8') as fh:
            prev = {x['id']: x for x in json.load(fh).get('items', [])}
    except (OSError, ValueError, KeyError):
        return
    for it in items:
        old = prev.get(it['id'])
        if not old:
            continue
        if old.get('sourceIds'):
            it['sourceIds'] = old['sourceIds']
        if old.get('reviewStatus') and old['reviewStatus'] != 'unreviewed':
            it['reviewStatus'] = old['reviewStatus']


def main():
    progress = load(os.path.join('js', 'progress-catalog.json'))
    search = load(os.path.join('data', 'search-index.json'))
    scenarios = load(os.path.join('data', 'scenarios.json'))

    kw_by_page = {p['u']: p.get('k', '') for p in search['pages']}
    title_by_page = {p['u']: p.get('t', '') for p in search['pages']}
    # AI 시나리오가 실제로 다루는 페이지만 aiEligible=true
    ai_pages = set()
    for dom, arr in scenarios.items():
        if dom.startswith('_') or not isinstance(arr, list):
            continue
        for sc in arr:
            if isinstance(sc, dict) and sc.get('f'):
                ai_pages.add(sc['f'])

    items = []
    skipped = []
    for it in progress['items']:
        page = it['id']
        dom, mode = classify(page)
        if not dom:
            skipped.append(page)
            continue
        skills = []
        if it.get('cwe'):
            skills.append(it['cwe'])          # 근거 있는 것만
        items.append({
            'id': slug(page),
            'page': page,
            'title': it.get('title') or title_by_page.get(page, ''),
            'domains': [dom],
            'skills': skills,
            'keywords': sorted(set(kw_by_page.get(page, '').split())),
            'category': it.get('cat', ''),
            'hubGroup': it.get('group', ''),
            'level': None,                     # 난이도를 정한 적이 없다
            'estimatedMinutes': None,          # 측정한 적이 없다
            'learningMode': mode,
            'progressEnabled': True,           # progress-catalog 에 있으므로 사실
            'aiEligible': page in ai_pages,    # 시나리오 DB 에 실제로 있는 경우만
            'validationKinds': [],             # 서버 채점 대상이 아직 없다
            'contentVersion': '1',
            'reviewStatus': 'unreviewed',      # 사람이 검토한 적 없음
            'sourceIds': [],
        })

    # 사람이 검토해 넣은 값은 생성기가 덮어쓰지 않는다.
    # sourceIds/reviewStatus 는 _gen/source-links.json 에서 사람이 정하고
    # gen_sources.py 가 반영한다. 여기서 매번 비우면 그 작업이 사라진다.
    _keep_reviewed(items)

    items.sort(key=lambda x: x['id'])
    payload = {
        'version': 1,
        'generatedBy': '_gen/gen_content_catalog.py',
        'note': ('검색·진도·AI 시나리오의 공통 상위 카탈로그. level/estimatedMinutes 는 정한 적이 없어 null, '
                 'reviewStatus 는 사람이 검토하기 전까지 unreviewed, validationKinds 는 서버가 실제로 '
                 '채점하는 항목이 생길 때만 채운다. 생성기가 추정으로 채우지 않는다.'),
        'count': len(items),
        'items': items,
    }
    text = json.dumps(payload, ensure_ascii=False, indent=1) + '\n'

    if CHECK:
        try:
            cur = open(OUT, encoding='utf-8').read()
        except OSError:
            cur = ''
        if cur != text:
            print('content-catalog drift: node/python 으로 재생성이 필요합니다.')
            print('  → python _gen/gen_content_catalog.py')
            sys.exit(1)
        print('content-catalog OK  items=%d' % len(items))
        return

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)

    ai_n = sum(1 for x in items if x['aiEligible'])
    by_dom = {}
    for x in items:
        by_dom[x['domains'][0]] = by_dom.get(x['domains'][0], 0) + 1
    print('content-catalog: %d items -> public/data/content-catalog.json' % len(items))
    for d in sorted(by_dom):
        print('  %-12s %3d' % (d, by_dom[d]))
    print('  aiEligible   %3d  (scenarios.json 에 실제로 있는 페이지만)' % ai_n)
    print('  level/estimatedMinutes = null, reviewStatus = unreviewed (추정 금지)')
    if skipped:
        print('  분류 규칙 없어 제외: %d개 (예: %s)' % (len(skipped), ', '.join(skipped[:3])))


if __name__ == '__main__':
    main()
