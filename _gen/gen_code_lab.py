# -*- coding: utf-8 -*-
"""보안약점 '현업 진단' 시나리오를 public/data/code-lab.json 으로 내보낸다.

사용법:
    python gen_code_lab.py                 # 전체 재생성
    python gen_code_lab.py --check         # 검증만 (파일 쓰지 않음)

생성물은 public/js/code-lab.js 가 fetch 로 읽는다.
페이지에 패널을 붙이는 것은 inject_code_lab.py 의 일이다.
"""
import importlib
import json
import os
import re
import sys

OUT = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'code-lab.json')
PUBLIC = os.path.join(os.path.dirname(__file__), '..', 'public')
MODULES = ['specs_code_lab', 'specs_code_lab_p2', 'specs_code_lab_p3']

VALID_VERDICT = ('true', 'false', 'more')


def load():
    all_s = {}
    dupes = []
    for m in MODULES:
        try:
            mod = importlib.import_module(m)
        except ImportError:
            print('  (skip) %s 없음' % m)
            continue
        for k, v in mod.SCENARIOS.items():
            if k in all_s:
                dupes.append(k)
            all_s[k] = v
    if dupes:
        raise SystemExit('중복 키: %s' % ', '.join(dupes))
    return all_s


def validate(scen):
    """생성기가 만든 결과를 반드시 검사한다 (CLAUDE.md 절대 원칙)."""
    errs = []
    for key, d in sorted(scen.items()):
        page = os.path.join(PUBLIC, '03_code_%s.html' % key)
        if not os.path.exists(page):
            errs.append('%s: 대상 페이지 없음 (03_code_%s.html)' % (key, key))

        t = d.get('ticket') or {}
        for f in ('source', 'id', 'severity', 'sevLevel', 'body'):
            if not t.get(f):
                errs.append('%s: ticket.%s 누락' % (key, f))
        if t.get('sevLevel') not in ('high', 'mid', 'low'):
            errs.append('%s: ticket.sevLevel 값 오류 (%r)' % (key, t.get('sevLevel')))

        ev = d.get('evidence') or []
        if len(ev) < 3:
            errs.append('%s: 증거가 %d개 (3개 이상 필요 — 판정 게이트가 2개를 요구한다)' % (key, len(ev)))
        for i, e in enumerate(ev):
            for f in ('icon', 'label', 'source', 'output'):
                if not e.get(f):
                    errs.append('%s: evidence[%d].%s 누락' % (key, i, f))

        v = d.get('verdict') or {}
        if v.get('answer') not in VALID_VERDICT:
            errs.append('%s: verdict.answer 오류 (%r)' % (key, v.get('answer')))
        if not v.get('why'):
            errs.append('%s: verdict.why 누락' % key)

        opts = (d.get('fix') or {}).get('options') or []
        if len(opts) < 3:
            errs.append('%s: 조치 선택지가 %d개 (3개 이상 필요)' % (key, len(opts)))
        oks = [o for o in opts if o.get('ok')]
        if len(oks) != 1:
            errs.append('%s: 정답 조치가 %d개 (정확히 1개여야 한다)' % (key, len(oks)))
        for i, o in enumerate(opts):
            for f in ('label', 'retest', 'why'):
                if not o.get(f):
                    errs.append('%s: fix.options[%d].%s 누락' % (key, i, f))

        # 전각문자가 섞이면 로그가 조용히 깨진다 (금융 클라우드에서 실제 발생)
        blob = json.dumps(d, ensure_ascii=False)
        fw = re.findall(r'[！-～]', blob)
        if fw:
            errs.append('%s: 전각문자 포함 %r' % (key, sorted(set(fw))))
    return errs


def stats(scen):
    c = {'true': 0, 'false': 0, 'more': 0}
    for d in scen.values():
        c[d['verdict']['answer']] += 1
    return c


def main():
    check_only = '--check' in sys.argv
    scen = load()
    errs = validate(scen)
    if errs:
        print('검증 실패 %d건:' % len(errs))
        for e in errs[:40]:
            print('  -', e)
        raise SystemExit(1)

    c = stats(scen)
    print('scenarios %d  (정탐 %d / 오탐 %d / 추가확인 %d)' % (len(scen), c['true'], c['false'], c['more']))

    if check_only:
        print('검증만 수행 - 파일을 쓰지 않았다.')
        return

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(scen, f, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(OUT) // 1024
    print('OK -> public/data/code-lab.json (%d KB)' % size)


if __name__ == '__main__':
    main()
