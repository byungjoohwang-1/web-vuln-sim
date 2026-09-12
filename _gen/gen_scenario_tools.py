# -*- coding: utf-8 -*-
"""AI 레드팀 에이전트의 '도구' 인터페이스: 전 도메인 스펙+DYN을 병합해
public/data/scenarios.json 으로 내보낸다. (redteam.html / quiz-forge.html이 사용)

항목: code, file(페이지 링크), title, cat, sev, attack_label, easy(비유),
      av(공격 터미널 라인), as(방어 터미널 라인), ov/os(결과), fix(조치)
"""
import importlib
import json
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAIRS = {
    'unix': ('specs_unix', 'specs_unix_dyn'),
    'dbms': ('specs_dbms', 'specs_dbms_dyn'),
    'windows': ('specs_windows', 'specs_windows_dyn'),
    'network': ('specs_network', 'specs_network_dyn'),
    'security': ('specs_security', 'specs_security_dyn'),
    'cloud': ('specs_cloud', 'specs_cloud_dyn'),
    'ics': ('specs_ics', 'specs_ics_dyn'),
    'design': ('specs_design', 'specs_design_dyn'),
    'ai': ('specs_ai', 'specs_ai_dyn'),
    'auto': ('specs_auto', 'specs_auto_dyn'),
}

DOMAIN_META = {
    'unix': {'name': 'UNIX·리눅스', 'icon': '🐧'},
    'dbms': {'name': '데이터베이스', 'icon': '🗄️'},
    'windows': {'name': 'Windows', 'icon': '🪟'},
    'network': {'name': '네트워크', 'icon': '🌐'},
    'security': {'name': '보안 관리', 'icon': '🛡️'},
    'cloud': {'name': '클라우드', 'icon': '☁️'},
    'ics': {'name': '제어시스템', 'icon': '🏭'},
    'design': {'name': '아키텍처', 'icon': '🏗️'},
    'ai': {'name': 'AI 보안', 'icon': '🤖'},
    'auto': {'name': '자동차 보안', 'icon': '🚗'},
}


def strip_tags(t, cap=None):
    t = re.sub(r'<[^>]+>', '', t or '').strip()
    t = re.sub(r'\s+', ' ', t)
    if cap and len(t) > cap:
        t = t[:cap - 1] + '…'
    return t


def lines(arr, cap_n, cap_t=95):
    out = []
    for cls, txt in (arr or [])[:cap_n]:
        txt = strip_tags(txt, cap_t)
        if txt:
            out.append([cls, txt])
    return out


def outcome(o):
    if not isinstance(o, dict):
        return None
    return {'e': o.get('emoji', ''), 't': o.get('title', ''), 'd': strip_tags(o.get('desc', ''), 130)}


def main():
    db = {'_meta': {'domains': {}, 'total': 0, 'gen': 'v1'}}
    for dom, (s_mod, d_mod) in PAIRS.items():
        try:
            static = importlib.import_module(s_mod).SPECS
            dyn = importlib.import_module(d_mod).DYN
        except Exception as e:
            print('skip', dom, e)
            continue
        items = []
        for s in static:
            d = dyn.get(s['code'])
            if not d:
                continue
            item = {
                'c': s['code'], 'f': s.get('file', ''), 't': strip_tags(s['title'], 80),
                'cat': strip_tags(s.get('category', ''), 40), 'sev': s.get('severity', ''),
                'al': strip_tags(d.get('attack_label', ''), 120),
                'ez': strip_tags(d.get('easy', ''), 200),
                'av': lines(d.get('attack_vuln'), 4),
                'as': lines(d.get('attack_secure'), 3),
                'ov': outcome(d.get('outcome_vuln')),
                'os': outcome(d.get('outcome_secure')),
                'fix': [strip_tags(x, 90) for x in (s.get('fix_steps') or [])[:3]],
            }
            items.append(item)
        db[dom] = items
        db['_meta']['domains'][dom] = {'name': DOMAIN_META[dom]['name'], 'icon': DOMAIN_META[dom]['icon'], 'n': len(items)}
        db['_meta']['total'] += len(items)
        print('%-8s %3d종' % (dom, len(items)))

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'data', 'scenarios.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(out_path)
    print('TOTAL %d종 -> %s (%.0f KB)' % (db['_meta']['total'], out_path, size / 1024))


if __name__ == '__main__':
    main()
