# -*- coding: utf-8 -*-
"""공개 가이드 출처 표기를 정확하게 바로잡는다 (멱등).

왜 필요한가
-----------
넘버드 학습 페이지의 꼬리말이 "주요정보통신기반시설 기술적 취약점 분석·평가
가이드(KISA) 기반"이라고만 적혀 있었다. 그런데 이 사이트의 항목 번호는
공식 고시의 항목 번호와 뜻이 다르다.

  확인된 사례 — 보안장비(10_sec-s*)
    이 사이트 S-03 = 계정 잠금 임계값
    공식     S-03 = 보안장비 계정별 권한 설정  (잠금 임계값은 공식 S-05)

  이 상태로 "KISA 가이드 기반"이라고만 써 두면, 학습자가 실제 점검 보고서에
  "S-03"을 인용했을 때 전혀 다른 항목을 대게 된다. 번호를 바꾸면 URL 과
  진도 기록이 깨지므로, 번호는 두고 **자체 번호임을 밝히는 쪽**으로 고친다.

  나머지 기둥(U/D/W/N/C/ICS/SD)도 같은 접두사 관례를 쓰지만 공식 목록과의
  일치 여부를 확인하지 않았다. 확인하지 않은 것을 맞다고 쓸 수 없으므로
  같은 문구를 적용한다.

전자금융 기준 실습은 07_iss-* 로 따로 있으므로 보안장비 페이지에서만 가리킨다.
"""
from __future__ import print_function
import io
import os
import sys

PUB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')

OLD = u'주요정보통신기반시설 기술적 취약점 분석·평가 가이드(KISA) 기반 · 교육용 재구성'
NEW = (u'KISA 공개 가이드의 점검 항목 구성을 참고한 교육용 재구성 · '
       u'항목 번호는 이 사이트의 자체 번호이며 공식 고시의 항목 번호와 다릅니다')
# 보안장비는 불일치를 실제로 확인했고, 전자금융 기준 실습이 따로 있다.
NEW_SEC = (u'KISA 공개 가이드의 보안장비 점검 구성을 참고한 교육용 재구성 · '
           u'항목 번호(S-xx)는 이 사이트의 자체 번호이며 공식 고시의 항목 번호와 다릅니다 · '
           u'전자금융 기준으로 장비를 점검하는 실습은 <a href="07_iss-account.html">'
           u'정보보호시스템 진단 실습</a> 참조')


def main():
    check = '--check' in sys.argv
    changed, already, stale = 0, 0, []
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html'):
            continue
        path = os.path.join(PUB, name)
        with io.open(path, encoding='utf-8') as f:
            doc = f.read()
        if OLD not in doc:
            if NEW in doc or NEW_SEC in doc:
                already += 1
            continue
        stale.append(name)
        if check:
            continue
        doc = doc.replace(OLD, NEW_SEC if name.startswith('10_sec') else NEW)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(doc)
        changed += 1

    if check:
        if stale:
            print('[GUIDE-ATTRIBUTION] 출처 표기가 옛 문구인 페이지 %d개 (예: %s). '
                  'python _gen/fix_guide_attribution.py'
                  % (len(stale), ', '.join(stale[:4])))
            return 1
        print('출처 표기 OK (갱신됨 %d개)' % already)
        return 0

    print('fix_guide_attribution: 갱신 %d · 이미 적용 %d' % (changed, already))
    return 0


if __name__ == '__main__':
    sys.exit(main())
