# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
import importlib
import time
from _compile_verify import compile_one, lang_of

sys.stdout.reconfigure(encoding='utf-8')

modules = [
    'std_certc_p1', 'std_certc_p2', 'std_certc_p3', 'std_certc_p4',
    'std_certcpp_p1', 'std_certcpp_p2', 'std_certcpp_p3', 'std_certcpp_p4'
]

all_fails = []

for mod_name in modules:
    print(f"\nVerifying module: {mod_name}")
    mod = importlib.import_module(mod_name)
    lang = lang_of(mod_name)
    
    # Let's verify a subset or check if compiles=True is specified
    for r in mod.RULES:
        # Check if compiles is True (some rules like DCL36-C cannot compile in a single file)
        if not r.get('compiles', False):
            print(f"  [Skipping] {r['id']} (marked non-compilable)")
            continue
            
        for kind in ('bad', 'good'):
            code = r[kind]
            ok, err = compile_one(code, lang)
            if not ok:
                all_fails.append((mod_name, r['id'], kind, err))
                print(f"  FAIL: {r['id']} ({kind}) - {err}")
            else:
                print(f"  OK: {r['id']} ({kind})")
            time.sleep(0.2)

print("\n=== VERIFICATION SUMMARY ===")
print(f"Total compile failures: {len(all_fails)}")
for mod_name, rid, kind, err in all_fails:
    print(f"  - {mod_name} / {rid} ({kind}): {err}")
