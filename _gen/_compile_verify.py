# -*- coding: utf-8 -*-
"""Wandbox로 std_*.py 의 bad/good 코드가 실제 컴파일되는지 일괄 검증.
사용: python _compile_verify.py <module> [start] [count]
  예: python _compile_verify.py std_certc_p1 0 20
gcc/g++가 로컬에 없어 원격(Wandbox) 컴파일로 확인한다. 네트워크 필요.
컴파일만 확인(실행 X). 실패한 룰의 id와 컴파일러 오류 첫 줄을 출력한다."""
import sys, json, time, importlib, urllib.request

sys.stdout.reconfigure(encoding='utf-8')

LANG = {'misrac': 'c', 'certc': 'c', 'misracpp': 'cpp', 'certcpp': 'cpp', 'autosar': 'cpp'}
COMP = {'c': 'gcc-13.2.0-c', 'cpp': 'gcc-13.2.0'}


def lang_of(mod):
    for k, v in LANG.items():
        if mod.startswith('std_' + k):
            return v
    return 'cpp'


def compile_one(code, lang):
    body = json.dumps({'code': code, 'compiler': COMP[lang],
                       'options': 'warning' if lang == 'c' else 'warning',
                       'compiler-option-raw': '-std=c11' if lang == 'c' else '-std=c++17',
                       'stdin': ''}).encode('utf-8')
    req = urllib.request.Request('https://wandbox.org/api/compile.json', data=body,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as r:
        j = json.loads(r.read().decode('utf-8'))
    # status "0" == compile+run ok. compiler_error present == compile failed.
    err = (j.get('compiler_error') or '').strip()
    return (err == ''), err.splitlines()[0] if err else ''


def main():
    mod = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 999
    m = importlib.import_module(mod)
    lang = lang_of(mod)
    rules = m.RULES[start:start + count]
    fails = []
    for i, r in enumerate(rules):
        for kind in ('bad', 'good'):
            ok, e1 = compile_one(r[kind], lang)
            mark = 'OK ' if ok else 'FAIL'
            if not ok:
                fails.append((r['id'], kind, e1))
            print('%s %-14s %-4s %s' % (mark, r['id'], kind, '' if ok else '| ' + e1))
            time.sleep(0.3)
    print('\n=== %s: %d rules, %d compile failures ===' % (mod, len(rules), len(fails)))
    for fid, kind, e in fails:
        print('  FAIL %s/%s: %s' % (fid, kind, e))


if __name__ == '__main__':
    main()
