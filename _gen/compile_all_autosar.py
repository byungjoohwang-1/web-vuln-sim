# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
import time
import json
from _compile_verify import compile_one

sys.stdout.reconfigure(encoding='utf-8')

import std_autosar_extracted

print(f"Total extracted rules to compile: {len(std_autosar_extracted.RULES)}")
results = []

for i, r in enumerate(std_autosar_extracted.RULES):
    rid = r['id']
    code = r['bad']  # bad and good are identical for these rules
    
    # We only check one (bad) since good is identical
    ok, err = compile_one(code, 'cpp')
    results.append({'id': rid, 'ok': ok, 'error': err})
    
    status = "OK" if ok else "FAIL"
    print(f"[{i+1}/{len(std_autosar_extracted.RULES)}] {rid}: {status} {err[:80] if err else ''}")
    
    # Sleep to avoid rate limits
    time.sleep(0.4)

with open('autosar_compile_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

fails = [r for r in results if not r['ok']]
print(f"Compilation check complete. Success: {len(results)-len(fails)}, Failures: {len(fails)}")
