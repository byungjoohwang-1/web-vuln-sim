# -*- coding: utf-8 -*-
"""14_auto 필러(개념 카드 77종)에서 자동차 모의 해킹 실습(sim-auto-*)으로 가는
상호링크를 각 페이지의 '아키텍처·규제 맥락' 패널(.ctxp) 안에 넣는다.

왜:
  14_auto-* 는 "왜 위험한지 이해시키는" 개념 카드이고, sim-auto-* 는 "직접 공격·
  방어해 보는" 핸즈온 랩이다. 둘 사이에 링크가 없어 학습자가 개념을 읽고 나서
  실습으로 넘어갈 길이 없었다. 이 스크립트가 그 다리를 놓는다.

설계:
  - 멱등이다. <!-- wvs-auto-lab-link --> 마커가 있으면 건너뛴다. 여러 번 돌려도 안전.
  - 14_auto-*.html 만 건드린다(격리). 다른 생성기·렌더러를 손대지 않는다.
  - 항목의 R155 위협 분류 + 아키텍처/접근 경로 칩 텍스트를 읽어 5개 랩 중 하나로
    매핑한다. 확신이 없으면 개요 페이지(sim-auto-pentest.html)로 보낸다.
  - 링크 문구는 bilingual.js 의 exact 사전에 들어 있어 KO/EN 토글에 따라 번역된다.

주의: 14_auto 페이지는 gen_v2_build.py 로 통째로 재생성되면 이 링크가 사라진다.
  다른 inject_*.py 들과 마찬가지로 재생성 뒤에는 이 스크립트를 다시 돌려야 한다.

사용:
  python _gen/inject_auto_lab_link.py          # 주입
  python _gen/inject_auto_lab_link.py --check   # 링크가 빠진 페이지가 있으면 실패(배포 게이트용)
"""
from __future__ import print_function
import glob
import os
import re
import sys

PUB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
MARKER = '<!-- wvs-auto-lab-link -->'

# (URL, 링크 문구) — 문구는 bilingual.js exact 사전에 등록돼 있어야 EN 토글에 번역된다.
LABS = {
    'can':      ('sim-auto-can.html',      'CAN 버스 공격 실습 →'),
    'uds':      ('sim-auto-uds.html',      '진단(UDS) 공격 실습 →'),
    'rf':       ('sim-auto-rf.html',       '무선·원격 공격 실습 →'),
    'ecu':      ('sim-auto-ecu.html',      'ECU 물리·펌웨어 공격 실습 →'),
    'backend':  ('sim-auto-backend.html',  '백엔드·OTA·개인정보 실습 →'),
    'overview': ('sim-auto-pentest.html',  '자동차 모의 해킹 실습장 →'),
}


def pick_lab(arch, access, r155, title):
    """항목의 맥락 텍스트로 가장 알맞은 실습 랩을 고른다. 확신 없으면 개요.

    우선순위가 핵심이다. '근거리 무선' 같은 접근 경로는 CAN 공격에도 흔히 붙으므로,
    아키텍처(CAN 버스/게이트웨이)를 무선보다 먼저 본다. 순서를 바꾸면 CAN 항목이
    전부 무선으로 잘못 매핑된다(실제로 처음에 그랬다)."""
    blob = ' '.join([arch, access, r155, title]).lower()

    def has(*ks):
        return any(k in blob for k in ks)

    # 1) 진단(UDS) — 데이터/코드 추출·조작, ECU 진단 서비스
    if has('진단', 'uds', '주행거리', 'vin', '이모빌', 'dtc', '메모리', 'securityaccess',
           '보안 접근', '데이터/코드', '데이터 추출', '데이터 조작'):
        return 'uds'
    # 2) 백엔드·OTA·앱·클라우드·충전관리 서버
    if has('백엔드', '서버', '클라우드', ' api', 'sqli', 'ota', '업데이트', '앱/클라우드',
           'ocpp', 'v2g', 'plug&charge', 'plug and charge', '관리 서버', '관리면',
           '충전 관리', '충전기 관리', '텔레매틱스 서버', '구독'):
        return 'backend'
    # 3) CAN/통신 채널 — 아키텍처가 버스/게이트웨이거나 통신 채널 분류이면 CAN (무선보다 먼저)
    if has('can', '버스', '게이트웨이', 'secoc', '메시지', '프레임', '통신 채널', '통신채널',
           '내부망', '이더넷', 'someip', '존 아키텍처', '존 간', '횡적'):
        return 'can'
    # 4) 무선·원격 — 키/텔레매틱스/GPS/근거리 무선/디지털 키
    if has('무선', '원격', '텔레매틱스', 'gps', '스마트키', '리모컨', '이모빌라이저', 'pke',
           '릴레이', '블루투스', 'bluetooth', 'wi-fi', 'wifi', 'nfc', 'uwb', '디지털 키',
           '디지털키', 'rf', '근거리'):
        return 'rf'
    # 5) 물리·펌웨어 — JTAG/OBD/USB/부트/플래시/하드웨어
    if has('펌웨어', 'jtag', 'obd', 'usb', '부트', 'flash', '플래시', '물리', '디버그',
           '하드웨어', '부품', '공급', '섀시', '센서'):
        return 'ecu'
    # 6) 그 외(규제·거버넌스·아키텍처 일반) → 개요 페이지
    return 'overview'


def chip(html, label):
    m = re.search(r'<i>' + re.escape(label) + r'</i>\s*([^<]+)</span>', html)
    return (m.group(1).strip() if m else '')


def block_for(key):
    url, label = LABS[key]
    return (
        '\n        <div class="ctxp-lab" style="margin-top:16px;background:#eefaf1;'
        'border:1px solid #a7e3bd;border-left:4px solid #22a565;border-radius:0 10px 10px 0;'
        'padding:12px 16px">' + MARKER + '\n'
        '          <b style="color:#137a45">\U0001F697 이 위협을 직접 공격·방어해 보기</b>\n'
        '          <a href="' + url + '" style="display:inline-block;margin:6px 10px 0 0;'
        'font-weight:700;color:#0e7a3c;text-decoration:none">' + label + '</a>\n'
        '          <span style="display:block;margin-top:4px;color:#3a5a45;font-size:13px">'
        '모의 침투 콘솔에서 실제로 공격을 실행하고, '
        '방어를 적용해 다시 확인합니다.</span>\n'
        '        </div>')


def process(path, check):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        return 'ok'
    i = html.find('<div class="ctxp">')
    if i < 0:
        return 'no-panel'
    # .ctxp-in 닫힘( 6칸 </div> ) + .ctxp 닫힘( 4칸 </div> ) 앞에 넣는다 = 패널 마지막 자식.
    anchor = html.find('      </div>\n    </div>', i)
    if anchor < 0:
        return 'no-anchor'
    if check:
        return 'missing'
    arch = chip(html, '아키텍처')          # 아키텍처
    access = chip(html, '접근 경로')        # 접근 경로
    r155 = chip(html, 'R155 위협 분류')     # R155 위협 분류
    tm = re.search(r'<title>([^<]*)</title>', html)
    title = tm.group(1) if tm else ''
    key = pick_lab(arch, access, r155, title)
    html = html[:anchor] + block_for(key) + '\n' + html[anchor:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return key


def undo(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER not in html:
        return False
    new = re.sub(r'\n        <div class="ctxp-lab".*?</div>', '', html, flags=re.S)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    return True


def main():
    check = '--check' in sys.argv
    pages = sorted(glob.glob(os.path.join(PUB, '14_auto-*.html')))
    if '--undo' in sys.argv:
        n = sum(1 for p in pages if undo(p))
        print('자동차 랩 링크 제거: %d개 페이지' % n)
        return
    counts, missing, nopanel = {}, [], []
    for p in pages:
        r = process(p, check)
        if r == 'missing':
            missing.append(os.path.basename(p))
        elif r == 'no-panel':
            nopanel.append(os.path.basename(p))
        elif r != 'ok':
            counts[r] = counts.get(r, 0) + 1
    if check:
        if missing:
            print('FAIL 자동차 랩 링크 누락 %d개: %s' % (len(missing), ', '.join(missing[:6])))
            sys.exit(1)
        print('auto-lab-link OK (%d개 페이지 모두 링크 있음)' % len(pages))
        return
    if nopanel:
        print('경고: 맥락 패널이 없어 건너뛴 페이지 %d개: %s' % (len(nopanel), ', '.join(nopanel[:6])))
    total = sum(counts.values())
    print('자동차 랩 상호링크 주입: %d개 페이지 (매핑 %s), 전체 %d개' % (total, counts, len(pages)))


if __name__ == '__main__':
    main()
