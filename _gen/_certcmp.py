# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
import std_certc, std_certcpp

def mk(d, suf):
    s = set()
    for sec, nums in d.items():
        for n in nums:
            s.add('%s%d-%s' % (sec, n, suf))
    return s

official_c = mk({'PRE':[30,31,32],'DCL':[30,31,36,37,38,39,40,41],
 'EXP':[30,32,33,34,35,36,37,39,40,42,43,44,45,46,47],'INT':[30,31,32,33,34,35,36],
 'FLP':[30,32,34,36,37],'ARR':[30,32,36,37,38,39],'STR':[30,31,32,34,37,38],
 'MEM':[30,31,33,34,35,36],'FIO':[30,32,34,37,38,39,40,41,42,44,45,46,47],
 'ENV':[30,31,32,33,34],'SIG':[30,31,34,35],'ERR':[30,32,33,34],
 'CON':[30,31,32,33,34,35,36,37,38,39,40,41,43],'MSC':[30,32,33,37,38,39,40,41],
 'POS':[30,34,35,36,37,38,39,44,47,48,49,50,51,52,53,54],'WIN':[30]}, 'C')
official_cpp = mk({'DCL':list(range(50,61)),'EXP':list(range(50,64)),'INT':[50],
 'CTR':list(range(50,59)),'STR':[50,51,52,53],'MEM':list(range(50,58)),'FIO':[50,51],
 'ERR':list(range(50,63)),'OOP':list(range(50,59)),'CON':list(range(50,57)),
 'MSC':list(range(50,55))}, 'CPP')

ours_c = {r['id'] for r in std_certc.RULES}
ours_cpp = {r['id'] for r in std_certcpp.RULES}

def isrule(i):
    m = re.search(r'(\d+)-C$', i)
    return bool(m) and int(m.group(1)) >= 30

ours_c_rules = {i for i in ours_c if isrule(i)}
print('CERT C suspect:', sorted(ours_c_rules - official_c))
print('CERT C MISSING rules:', sorted(official_c - ours_c))
print('CERT C recs kept:', sorted(ours_c - ours_c_rules))
print('CERT C off=%d ours=%d missing=%d' % (len(official_c), len(ours_c), len(official_c - ours_c)))
print('CERT C++ suspect:', sorted(ours_cpp - official_cpp))
print('CERT C++ MISSING:', sorted(official_cpp - ours_cpp))
print('CERT C++ off=%d ours=%d missing=%d' % (len(official_cpp), len(ours_cpp), len(official_cpp - ours_cpp)))
