# -*- coding: utf-8 -*-
"""점검 항목 → 실습 시뮬레이터 연결기.

왜 만드는가
-----------
전자금융(fin-eval)과 관리·물리(mp-assessment)는 "항목을 읽고 양호/취약을 고르는" 체크리스트다.
읽고 체크하는 것만으로는 왜 취약한지 몸으로 알기 어렵다.
사이트에는 이미 같은 주제를 다루는 시뮬레이터가 500개 넘게 있으므로,
항목마다 **관련 실습으로 바로 건너가는 링크**를 붙여 체크리스트를 실습의 입구로 만든다.

정직성 규칙
-----------
- 억지로 다 붙이지 않는다. 키워드가 충분히 겹칠 때만 연결하고, 없으면 비워 둔다.
- 연결 근거(일치한 키워드)를 산출물에 남겨 나중에 사람이 검증할 수 있게 한다.
- '관련 실습'이라고만 쓴다. 그 실습이 해당 항목을 대체·검증한다고 말하지 않는다.

사용: python _gen/link_checklist_sims.py [--check]
"""
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(BASE, '..', 'public')
CHECK = '--check' in sys.argv

# 주제어 → 그 주제를 실제로 다루는 페이지. 페이지 존재 여부는 아래에서 검증한다.
# (왼쪽 단어가 항목 제목·설명에 나타나면 후보로 잡는다)
TOPICS = [
    (['비밀번호', '패스워드', '암호 정책', '계정 잠금'], 'sim-brute.html', '비밀번호 추측 공격'),
    (['세션', '로그아웃', '세션 타임아웃'], 'sim-session_hijacking.html', '세션 탈취'),
    (['SQL', '질의문', '쿼리'], 'sim-sql.html', 'SQL 삽입'),
    (['크로스사이트', 'XSS', '스크립트 삽입'], 'sim-xss.html', '크로스사이트 스크립팅'),
    (['파일 업로드', '업로드'], 'sim-upload.html', '파일 업로드 취약점'),
    (['디렉터리', '디렉토리', '경로 조작', '경로 탐색'], 'sim-path.html', '경로 조작'),
    (['암호 알고리즘', '평문 저장', '평문 전송', '해시 함수', '암호키'], 'sim-weak-crypto.html', '취약한 암호화'),
    (['전송 구간', 'SSL', 'TLS', '인증서'], 'sim-unencrypted_data.html', '평문 전송 노출'),
    (['접근 통제', '권한 없는', '인가 우회', '타인 정보 조회'], 'sim-idor.html', '권한 없는 접근(IDOR)'),
    (['로그 관리', '로그 보관', '감사 추적', '기록 보존', '접속기록'], '12_ics-ics08.html', '로깅·모니터링'),
    (['오류 메시지', '에러', '예외 처리'], 'sim-error-msg.html', '오류 메시지 노출'),
    (['백업', '복구 절차', '소산'], '12_ics-ics11.html', '백업·복구 체계'),
    (['망 분리', '망분리', '네트워크 분리', '세분화'], '16_zt-microseg.html', '마이크로 세그멘테이션'),
    (['관리자 계정', '공용 계정', '특권', 'root', '관리자 권한'], '16_zt-pam.html', '특권 계정 관리'),
    (['다중인증', '이중 인증', 'OTP', '추가 인증', '2차 인증'], '16_zt-mfa.html', '다중인증'),
    (['퇴직', '전보', '휴직', '미사용 계정', '불필요한 계정'], '16_zt-identity-inventory.html', '유령 계정'),
    (['최소 권한', '권한 최소화', '직무 분리'], '16_zt-least-privilege.html', '최소 권한'),
    (['엔드포인트', '노트북', '개인 PC', '업무용 단말'], '16_zt-device-compliance.html', '기기 상태 검증'),
    (['반출', '유출 방지', '데이터 분류', '자료 등급'], '16_zt-data-dlp.html', '데이터 분류·DLP'),
    (['거래정보', '이체 요청', '거래 무결성', '전문 위변조'], '07_fin-transaction-integrity.html', '거래정보 무결성'),
    (['재사용', '재전송', '리플레이'], '07_fin-replay.html', '거래정보 재사용 방지'),
    (['출입통제', '출입 통제', '출입자', '통제구역', '잠금장치', 'CCTV', '전산실', '상면'], '12_ics-ics12.html', '물리 접근 통제'),
    (['이동식', 'USB', '보조기억매체'], '12_ics-ics06.html', '이동식 매체 통제'),
    (['클라우드', '가상화', '컨테이너'], '11_cloud-c01.html', '클라우드 보안'),
    (['패치', '취약점 점검', '보안 업데이트'], '05_linux-u42.html', '패치 관리'),
]

MIN_HITS = 1          # 최소 일치 키워드 수
MAX_LINKS = 2         # 항목당 최대 연결 수(너무 많으면 고르기가 더 어려워진다)


def existing(page):
    return os.path.exists(os.path.join(PUB, page))


def match(text):
    """항목 텍스트에 대해 (페이지, 라벨, 일치어) 목록을 점수 순으로 돌려준다."""
    out = []
    for words, page, label in TOPICS:
        hits = [w for w in words if w in text]
        if len(hits) >= MIN_HITS and existing(page):
            out.append((len(hits), page, label, hits))
    out.sort(key=lambda x: -x[0])
    return out[:MAX_LINKS]


def link_file(rel, text_fields):
    path = os.path.join(PUB, rel)
    with io.open(path, encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('items') or []
    linked = 0
    for it in items:
        text = ' '.join(str(it.get(k, '')) for k in text_fields)
        hits = match(text)
        if not hits:
            it.pop('sims', None)
            continue
        it['sims'] = [{'p': p, 'n': label, 'w': words} for _, p, label, words in hits]
        linked += 1
    data['simLinkNote'] = ('항목 본문의 주제어가 실습 페이지 주제와 겹칠 때만 연결한다. '
                           '연결은 참고용이며 해당 실습이 항목 점검을 대신하지 않는다.')
    text_out = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

    if CHECK:
        cur = io.open(path, encoding='utf-8').read()
        if cur != text_out:
            print('%s: 실습 연결이 최신이 아닙니다 → python _gen/link_checklist_sims.py' % rel)
            sys.exit(1)
        print('%s OK  연결 %d/%d' % (rel, linked, len(items)))
        return
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(text_out)
    print('%s: %d/%d 항목에 실습 연결' % (rel, linked, len(items)))


def main():
    missing = sorted({p for _, p, _ in TOPICS if not existing(p)})
    if missing:
        print('  (주의) 없는 페이지라 연결에서 제외: %s' % ', '.join(missing))
    link_file(os.path.join('js', 'fin-eval-items.json'), ['t', 'why', 'how', 'fix', 'area'])
    if os.path.exists(os.path.join(PUB, 'js', 'kisa-mp-items.json')):
        link_file(os.path.join('js', 'kisa-mp-items.json'),
              ['requirement', 'detail', 'consider'])


if __name__ == '__main__':
    main()
