#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
콘텐츠 레지스트리 생성기 (QA W-06, W-03 대응)

화면 배지에 손으로 적은 숫자를 쓰면 콘텐츠가 늘고 줄 때마다 어긋난다.
실제 파일을 세어 public/data/content-registry.json 을 만들고,
js/registry.js 가 그 값을 배지에 채워 넣는다.

번호 체계가 있는 도메인(u01~u61 등)은 실제로 존재하는 번호와 빠진 번호를
함께 기록한다. 허브에서 커버리지를 정직하게 표시하기 위한 자료다 (W-03).

사용법:
    python _gen/gen_registry.py
"""

import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, 'public')
OUT = os.path.join(PUBLIC, 'data', 'content-registry.json')

# id, 파일 접두사, 화면 표기, 번호 식별자 접두사, 공식 번호 범위(없으면 None)
DOMAINS = [
    ('code',   '03_code_',   '시큐어코딩 보안약점', 'Secure coding weaknesses', None,  None),
    ('design', '04_design-', '설계 단계 보안',       'Secure design',            'sd',  (1, 20)),
    ('linux',  '05_linux-',  'Linux 서버 점검',      'Linux server hardening',   'u',   (1, 61)),
    ('db',     '06_db-',     'DBMS 점검',            'DBMS hardening',           'd',   (1, 26)),
    ('fin',    '07_fin-',    '전자금융기반시설 점검', 'Financial infrastructure', None,  None),
    ('win',    '08_win-',    'Windows 서버 점검',    'Windows server hardening', 'w',   (1, 28)),
    ('net',    '09_net-',    '네트워크 장비 점검',    'Network device hardening', 'n',   (1, 21)),
    ('sec',    '10_sec-',    '보안장비 점검',         'Security appliance',       's',   (1, 23)),
    ('cloud',  '11_cloud-',  '클라우드, 컨테이너',    'Cloud and containers',     'c',   (1, 20)),
    ('ics',    '12_ics-',    '제어시스템 ICS/SCADA', 'ICS and SCADA',            'ics', (1, 14)),
    ('ai',     '13_ai-',     'AI 보안',              'AI security',              'ai',  (1, 26)),
    ('auto',   '14_auto-',   '자동차 보안',           'Automotive security',      'auto', (1, 61)),
    ('privacy', '15_privacy-', '개인정보보호',        'Privacy protection',       'p',   None),
    ('zt',     '16_zt-',     '제로트러스트',          'Zero trust',               None,  None),
]

# 시뮬레이터 파일명은 하이픈과 밑줄이 섞여 있다(sim_insufficient_session.html).
# 한쪽만 세면 실습 총계가 어긋난다(QA N-12 와 같은 원인).
SIM_PREFIXES = ('sim-', 'sim_')
SIM_PREFIX = 'sim-'


def html_files(prefix):
    """prefix 는 문자열 또는 문자열 튜플(구분자 혼용 대응)."""
    names = []
    for name in sorted(os.listdir(PUBLIC)):
        if name.startswith(prefix) and name.endswith('.html'):
            names.append(name)
    return names


def numbers_in(name, prefix, num_prefix):
    """05_linux-u25.html -> [25], 06_db-d25-d26.html -> [25, 26]"""
    stem = name[len(prefix):-len('.html')]
    found = re.findall(r'(?:^|-)%s(\d+)' % re.escape(num_prefix), stem)
    return [int(n) for n in found]


def build_domain(did, prefix, label_ko, label_en, num_prefix, rng):
    files = html_files(prefix)
    entry = {
        'id': did,
        'prefix': prefix,
        'label': label_ko,
        'labelEn': label_en,
        'count': len(files),
        'files': files,
    }
    if num_prefix and rng:
        lo, hi = rng
        present = set()
        for f in files:
            present.update(numbers_in(f, prefix, num_prefix))
        planned = list(range(lo, hi + 1))
        missing = [n for n in planned if n not in present]
        covered = [n for n in planned if n in present]
        entry['numbering'] = {
            'itemPrefix': num_prefix.upper(),
            'plannedFrom': lo,
            'plannedTo': hi,
            'plannedCount': len(planned),
            'coveredCount': len(covered),
            'missing': missing,
            'coveragePercent': round(len(covered) * 100.0 / len(planned)) if planned else 100,
        }
    return entry


def load_page_order():
    p = os.path.join(PUBLIC, 'js', 'page-order.json')
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8') as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        for key in ('pages', 'order', 'items'):
            if key in data:
                return data[key]
        return []
    return data


def count_coding_standard_rules():
    p = os.path.join(PUBLIC, 'coding-standards.html')
    if not os.path.exists(p):
        return 0
    with open(p, encoding='utf-8', errors='replace') as fh:
        s = fh.read()
    return len(re.findall(r'<h3\b', s, re.IGNORECASE))


def main():
    domains = [build_domain(*d) for d in DOMAINS]
    sims = html_files(SIM_PREFIXES)
    pages = load_page_order()

    total_learning = sum(d['count'] for d in domains)
    registry = {
        'generatedAt': date.today().isoformat(),
        'generator': '_gen/gen_registry.py',
        'note': '화면 배지와 소개 문구는 이 파일의 수치를 쓴다. 손으로 적지 않는다.',
        'totals': {
            'learningPages': total_learning,
            'simulators': len(sims),
            'interactiveTotal': total_learning + len(sims),
            'orderedPages': len(pages),
            'codeWeaknesses': next(d['count'] for d in domains if d['id'] == 'code'),
            'codingStandardRules': count_coding_standard_rules(),
        },
        # 기관이 정한 고정 숫자. 파일 수와 다를 수 있어서 따로 둔다.
        # 예: KISA 보안약점은 49종이지만 해설 페이지는 변형을 나눠 50개다.
        'curriculum': {
            'kisaWeaknesses': 49,
            'kisaWeaknessPages': next(d['count'] for d in domains if d['id'] == 'code'),
            'codingStandards': 5,
            'note': 'kisaWeaknesses 는 행정안전부, KISA 가 정의한 항목 수다. '
                    'kisaWeaknessPages 는 그것을 설명하는 실제 페이지 수다.',
        },
        'domains': domains,
        'simulators': {
            'prefix': SIM_PREFIX,
            'prefixes': list(SIM_PREFIXES),
            'count': len(sims),
            'files': sims,
        },
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(registry, fh, ensure_ascii=False, indent=2)
        fh.write('\n')

    print('생성: %s' % os.path.relpath(OUT, ROOT))
    for d in domains:
        cov = ''
        if 'numbering' in d:
            n = d['numbering']
            cov = '  커버리지 %d%% (%d/%d, 미수록 %d)' % (
                n['coveragePercent'], n['coveredCount'], n['plannedCount'], len(n['missing']))
        print('  %-8s %3d%s' % (d['id'], d['count'], cov))
    t = registry['totals']
    print('  %-8s %3d' % ('sim', t['simulators']))
    print('  합계 학습 %d, 시뮬 %d, 실습 총계 %d, 순서 카탈로그 %d, 코딩표준 규칙 %d'
          % (t['learningPages'], t['simulators'], t['interactiveTotal'],
             t['orderedPages'], t['codingStandardRules']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
