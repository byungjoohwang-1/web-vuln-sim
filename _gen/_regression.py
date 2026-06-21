# -*- coding: utf-8 -*-
"""회귀 테스트: gen_fin.verifyCode / gen_securecode.passesChecks 의 검증 로직을
Python으로 동일 재현하여, 모든 스펙에 대해
  - 취약 코드(vuln)  => 검증 실패(취약 유지)   여야 하고
  - 안전 코드(secure_hint / 안전 변형) => 검증 통과   여야 함을 확인한다.
주석제거 도입이 어떤 페이지의 정답/오답을 깨뜨리지 않는지 보장한다."""
import re, importlib, sys

FIN_MODS = ['specs_fin', 'specs_fin_a', 'specs_fin_b', 'specs_fin_c', 'specs_fin_d',
            'specs_fin_e', 'specs_fin_f', 'specs_fin_g', 'specs_fin_h']
SC_MODS = ['specs_securecode']

OP = re.compile(r'\s*(==|!=|<=|>=|=)\s*')
def strip_comments(s):
    s = re.sub(r'/\*[\s\S]*?\*/', ' ', s)
    s = re.sub(r'//[^\n]*', ' ', s)
    s = re.sub(r'#[^\n]*', ' ', s)
    return s
def norm(s):
    s = strip_comments(s)
    s = re.sub(r'\s+', ' ', s)
    s = OP.sub(lambda m: m.group(1), s)
    return s

def passes_fin(code, checks):
    c = norm(code)
    for grp in checks:
        pos = [t for t in grp if not t.startswith('!')]
        neg = [t[1:] for t in grp if t.startswith('!')]
        pos_ok = (len(pos) == 0) or any(norm(t) in c for t in pos)
        neg_ok = all(norm(t) not in c for t in neg)
        if not (pos_ok and neg_ok):
            return False
    return True

def passes_sc(code, checks):
    c = norm(code)
    for grp in checks:
        pos = [t for t in grp if not t.startswith('NOT:')]
        neg = [t[4:] for t in grp if t.startswith('NOT:')]
        pos_ok = (len(pos) == 0) or any(norm(t) in c for t in pos)
        neg_ok = all(norm(t) not in c for t in neg)
        if not (pos_ok and neg_ok):
            return False
    return True

fails = []

# ---- 금융 ----
fin_n = 0
for m in FIN_MODS:
    try:
        specs = importlib.import_module(m).SPECS
    except ModuleNotFoundError:
        continue
    for s in specs:
        fin_n += 1
        f = s['file']
        if passes_fin(s['vuln_code'], s['checks']):
            fails.append('[FIN] %s : 취약 코드가 검증을 통과함(false pass)' % f)
        if not passes_fin(s['secure_hint'], s['checks']):
            fails.append('[FIN] %s : 안전 코드(secure_hint)가 검증을 통과하지 못함(false fail)' % f)
print('financial specs tested:', fin_n)

# ---- 시큐어코딩 ----
sc_n = 0
for m in SC_MODS:
    try:
        specs = importlib.import_module(m).SPECS
    except ModuleNotFoundError:
        continue
    for s in specs:
        for lang in ('java', 'python'):
            d = s.get(lang)
            if not d:
                continue
            sc_n += 1
            f = '%s[%s]' % (s['file'], lang)
            # 취약 원본은 실패해야 함
            if passes_sc(d['vuln'], d['checks']):
                fails.append('[SC] %s : 취약 코드가 검증을 통과함(false pass)' % f)
            # 안전 변형(있으면)은 통과해야 함
            secure = d.get('secure') or d.get('safe_code') or d.get('fixed')
            if secure and not passes_sc(secure, d['checks']):
                fails.append('[SC] %s : 안전 코드가 통과하지 못함(false fail)' % f)
print('securecode lang-specs tested:', sc_n)

print('-' * 50)
if fails:
    print('REGRESSION FAILURES:', len(fails))
    for x in fails:
        print(' -', x)
    sys.exit(1)
else:
    print('REGRESSION PASS - all vuln fail, all secure pass (vuln=fail, secure=pass)')
