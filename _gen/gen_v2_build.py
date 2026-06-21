# -*- coding: utf-8 -*-
"""정적 스펙(specs_<domain>) + 동적 필드(specs_<domain>_dyn.DYN)를 병합해 v2 페이지 렌더."""
import importlib, os, sys
import gen_infra2

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
DYN_KEYS = ['easy', 'attack_label', 'attack_vuln', 'outcome_vuln', 'attack_secure', 'outcome_secure']

PAIRS = {
    'unix': ('specs_unix', 'specs_unix_dyn'),
    'dbms': ('specs_dbms', 'specs_dbms_dyn'),
    'windows': ('specs_windows', 'specs_windows_dyn'),
    'network': ('specs_network', 'specs_network_dyn'),
    'security': ('specs_security', 'specs_security_dyn'),
    'cloud': ('specs_cloud', 'specs_cloud_dyn'),
    'ics': ('specs_ics', 'specs_ics_dyn'),
    'design': ('specs_design', 'specs_design_dyn'),
}


def build(domain):
    static_mod, dyn_mod = PAIRS[domain]
    static = importlib.import_module(static_mod).SPECS
    dyn = importlib.import_module(dyn_mod).DYN
    n = 0
    missing = []
    for s in static:
        d = dyn.get(s['code'])
        if not d:
            missing.append(s['code']); continue
        miss = [k for k in DYN_KEYS if k not in d]
        if miss:
            print('  [%s] missing keys %s' % (s['code'], miss)); continue
        full = {**s, **d}
        with open(os.path.join(OUT_DIR, s['file']), 'w', encoding='utf-8') as f:
            f.write(gen_infra2.render(full))
        n += 1
    print('%s: wrote %d / %d' % (domain, n, len(static)), ('MISSING ' + ','.join(missing)) if missing else '')
    return n


if __name__ == '__main__':
    doms = sys.argv[1:] or list(PAIRS)
    total = sum(build(d) for d in doms)
    print('TOTAL', total)
