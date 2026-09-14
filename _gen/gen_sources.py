#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""[C03] 공식 자료 등록부와 학습 항목 연결을 배포본으로 낸다.

왜 필요한가
    공통 카탈로그 491개의 sourceIds 가 전부 빈 배열이었다. 본문에 출처가 전혀
    없다는 뜻은 아니지만, **기계가 추적할 수 있는 연결이 없다**. 그래서
    "이 과제의 근거가 무엇인가" 를 화면에서도 검사에서도 말할 수 없었다.

무엇을 지키나
    1. 사람이 손으로 적은 _gen/sources.json · _gen/source-links.json 을
       생성기가 덮어쓰지 않는다. 이 스크립트는 읽어서 public 으로 옮기기만 한다.
    2. 확인한 범위를 구분해 싣는다. 게시문까지 본 것(listing-page)과 전문을
       대조한 것(full-text)은 다르다. 전자를 "검증 완료" 로 표시하지 않는다.
    3. 절·항목 번호는 대조했을 때만 쓴다. 추정해서 채우지 않는다.

사용: python _gen/gen_sources.py [--check]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, 'public')
SRC = os.path.join(HERE, 'sources.json')
LINKS = os.path.join(HERE, 'source-links.json')
OUT = os.path.join(PUBLIC, 'data', 'sources.json')
CATALOG = os.path.join(PUBLIC, 'data', 'content-catalog.json')

VALID_SCOPE = {'listing-page', 'full-text', 'not-verified'}
VALID_STATUS = {'document-identified', 'section-verified', 'unreviewed'}


def load(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def problems(reg, links):
    """사람이 적은 데이터가 스스로 모순되지 않는지 본다."""
    out = []
    by_id = {}
    for s in reg.get('sources', []):
        if s['id'] in by_id:
            out.append('출처 ID 중복: %s' % s['id'])
        by_id[s['id']] = s
        if s.get('verifiedScope') not in VALID_SCOPE:
            out.append('%s: verifiedScope 값이 이상하다(%s)' % (s['id'], s.get('verifiedScope')))
        for req in ('org', 'title', 'url', 'checkedAt', 'checkedBy'):
            if not s.get(req):
                out.append('%s: %s 가 비어 있다' % (s['id'], req))
        if s.get('verifiedScope') == 'not-verified':
            out.append('%s: 확인하지 않은 자료는 등록부에 두지 않는다' % s['id'])

    for l in links.get('links', []):
        sid = l.get('sourceId')
        if sid not in by_id:
            out.append('%s: 등록부에 없는 출처를 가리킨다(%s)' % (l.get('contentId'), sid))
            continue
        st = l.get('reviewStatus')
        if st not in VALID_STATUS:
            out.append('%s: reviewStatus 값이 이상하다(%s)' % (l.get('contentId'), st))
        # 핵심 규칙 — 절 번호는 대조했을 때만
        if l.get('section') and st != 'section-verified':
            out.append('%s: 절·항목을 적었는데 reviewStatus 가 section-verified 가 아니다. '
                       '대조하지 않은 절 번호를 쓰면 안 된다.' % l.get('contentId'))
        if st == 'section-verified':
            if not l.get('section'):
                out.append('%s: section-verified 인데 절·항목이 비어 있다' % l.get('contentId'))
            if by_id[sid].get('verifiedScope') != 'full-text':
                out.append('%s: 절까지 대조했다고 하는데 출처 %s 는 게시문까지만 확인돼 있다. '
                           '둘 중 하나가 틀렸다.' % (l.get('contentId'), sid))
        if not l.get('why'):
            out.append('%s: 왜 이 문서를 근거로 삼는지가 비어 있다' % l.get('contentId'))
    return out


def main():
    check = '--check' in sys.argv
    reg, links = load(SRC), load(LINKS)

    errs = problems(reg, links)
    if errs:
        print('출처 데이터에 문제가 있다:')
        for e in errs:
            print('  - ' + e)
        return 1

    by_content = {}
    for l in links['links']:
        by_content.setdefault(l['contentId'], []).append(l)

    payload = {
        'version': 1,
        'generatedBy': '_gen/gen_sources.py',
        'note': reg['note'],
        'scopeMeaning': reg['scopeMeaning'],
        'reviewStatusMeaning': links['reviewStatusMeaning'],
        'sources': reg['sources'],
        'links': links['links'],
        'counts': {
            'sources': len(reg['sources']),
            'links': len(links['links']),
            'sectionVerified': sum(1 for l in links['links'] if l['reviewStatus'] == 'section-verified'),
            'documentIdentified': sum(1 for l in links['links'] if l['reviewStatus'] == 'document-identified'),
        },
    }

    # 카탈로그의 sourceIds 를 채운다 — 연결이 있는 항목만. 없는 항목은 빈 배열 그대로 둔다.
    # 연결은 단계 단위('incident:api-authz')로 적고, 카탈로그는 페이지 단위('incident')다.
    # 페이지 항목에는 그 페이지에 속한 단계들의 출처를 합쳐서 올린다.
    rolled = {}
    for cid, ls in by_content.items():
        page_id = cid.split(':', 1)[0]
        for l in ls:
            rolled.setdefault(page_id, [])
            if l['sourceId'] not in rolled[page_id]:
                rolled[page_id].append(l['sourceId'])

    catalog_updated = 0
    if os.path.exists(CATALOG):
        cat = load(CATALOG)
        for item in cat.get('items', []):
            ids = rolled.get(item['id'], [])
            if ids and item.get('sourceIds') != ids:
                item['sourceIds'] = ids
                catalog_updated += 1
        if not check and catalog_updated:
            with open(CATALOG, 'w', encoding='utf-8') as fh:
                json.dump(cat, fh, ensure_ascii=False, indent=2)
                fh.write('\n')

    if check:
        print('출처 데이터 OK  자료 %d · 연결 %d (절 대조 %d · 문서 특정 %d)'
              % (payload['counts']['sources'], payload['counts']['links'],
                 payload['counts']['sectionVerified'], payload['counts']['documentIdentified']))
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    print('생성: data/sources.json')
    print('  등록 자료 %d개' % payload['counts']['sources'])
    for s in reg['sources']:
        print('    %-26s %s' % (s['id'], s['verifiedScope']))
    print('  학습 항목 연결 %d개 (절까지 대조 %d · 문서만 특정 %d)'
          % (payload['counts']['links'], payload['counts']['sectionVerified'],
             payload['counts']['documentIdentified']))
    print('  카탈로그 sourceIds 갱신 %d개' % catalog_updated)
    return 0


if __name__ == '__main__':
    sys.exit(main())
