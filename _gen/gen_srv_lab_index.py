# -*- coding: utf-8 -*-
"""_gen/srv-lab-index.json 생성 — SRV 점검 항목 ID → 전용 진단 실습 페이지.

왜 생성기로 두는가
------------------
link_checklist_sims.py 는 이 표를 읽어 fin-eval 의 SRV 항목을 실습 페이지로 연결한다.
표를 손으로 관리하면 실습을 추가·이동할 때마다 조용히 어긋난다. 실제로 이 파일은
한동안 손으로 만든 상태였고, 어느 스크립트가 만드는지도 남아 있지 않았다.
그래서 **스펙 모듈을 그대로 읽어** 만든다. 실습이 늘면 다시 돌리기만 하면 된다.

사용: python _gen/gen_srv_lab_index.py [--check]
  --check 는 쓰지 않고 현재 산출물과 달라지는지만 본다(배포 게이트용).
"""
import importlib
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
OUT = os.path.join(BASE, 'srv-lab-index.json')

SPEC_MODULES = ['specs_srv_lab', 'specs_srv_acct', 'specs_srv_perm',
                'specs_srv_svc', 'specs_srv_ops', 'specs_srv_daemon',
                'specs_srv_win']

CHECK = '--check' in sys.argv


def build():
    index = {}
    dupes = []
    for name in SPEC_MODULES:
        for lab in importlib.import_module(name).LABS:
            label = lab['title'] + ' 진단 실습'
            for m in lab['missions']:
                if m['id'] in index:
                    dupes.append('%s (%s ↔ %s)' % (m['id'], index[m['id']]['p'], lab['file']))
                    continue
                index[m['id']] = {'p': lab['file'], 'n': label}
    return index, dupes


def main():
    index, dupes = build()
    if dupes:
        # 항목 하나는 실습 하나에만 대응해야 한다. 중복이면 어느 쪽으로 보낼지 정할 수 없다.
        print('항목 ID 가 두 실습에 겹칩니다:')
        for d in dupes:
            print('  ' + d)
        sys.exit(1)

    text = json.dumps(index, ensure_ascii=False, indent=1) + '\n'
    if CHECK:
        cur = io.open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        if cur != text:
            print('srv-lab-index drift: python _gen/gen_srv_lab_index.py 를 다시 돌리세요.')
            sys.exit(1)
        print('srv-lab-index OK  %d개 항목' % len(index))
        return

    with io.open(OUT, 'w', encoding='utf-8') as f:
        f.write(text)
    by_page = {}
    for v in index.values():
        by_page[v['p']] = by_page.get(v['p'], 0) + 1
    print('srv-lab-index: %d개 항목 -> _gen/srv-lab-index.json' % len(index))
    for p in sorted(by_page):
        print('  %-24s %2d' % (p, by_page[p]))


if __name__ == '__main__':
    main()
