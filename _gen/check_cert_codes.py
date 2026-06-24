# -*- coding: utf-8 -*-
import sys
sys.path.append('.')
import std_certc, std_certcpp

sys.stdout.reconfigure(encoding='utf-8')

print("Checking CERT C...")
empty_c = []
for r in std_certc.RULES:
    bad = r.get('bad', '').strip()
    good = r.get('good', '').strip()
    if not bad or not good or "TODO" in bad or "TODO" in good:
        empty_c.append(r['id'])

print("CERT C empty/placeholder count:", len(empty_c), empty_c)

print("\nChecking CERT C++...")
empty_cpp = []
for r in std_certcpp.RULES:
    bad = r.get('bad', '').strip()
    good = r.get('good', '').strip()
    if not bad or not good or "TODO" in bad or "TODO" in good:
        empty_cpp.append(r['id'])

print("CERT C++ empty/placeholder count:", len(empty_cpp), empty_cpp)
