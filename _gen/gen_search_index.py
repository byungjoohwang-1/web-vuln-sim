# -*- coding: utf-8 -*-
"""전체 공개 페이지를 스캔해 커맨드 팔레트용 검색 인덱스를 생성한다.

출력: public/data/search-index.json
형식: {"pages":[{"t":"제목","u":"파일명","g":"그룹","k":"검색보조 키워드"}], "generated":"ISO날짜"}

멱등: 몇 번을 실행해도 같은 결과. 404/offline 등 유틸 제외.
"""
import os
import re
import sys
import io
import json
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
OUT = os.path.join(BASE, 'data', 'search-index.json')

EXCLUDE = {'404.html', 'offline.html'}

# 파일명 접두사 → 그룹
PREFIX_GROUP = [
    ('03_code_', 'code'), ('04_design', 'design'), ('05_linux', 'unix'),
    ('06_db', 'db'), ('07_fin', 'fin'), ('08_win', 'win'), ('09_net', 'net'),
    ('10_sec', 'sec'), ('11_cloud', 'cloud'), ('12_ics', 'ics'),
    ('13_ai', 'ai'), ('14_auto', 'auto'), ('15_privacy', 'privacy'),
    ('16_zt', 'zt'),
    ('sim-', 'sim'), ('guide-', 'guide'),
]

# [G03] 그룹별 검색 동의어 — 실무자가 실제로 칠 법한 한글/영문을 함께 심는다.
# 파일명·제목에만 의존하면 한국어 검색이 통째로 실패한다.
GROUP_SYNONYMS = {
    'code': '시큐어코딩 코드 구현 취약점 secure coding',
    'design': '설계 아키텍처 위협모델링 design',
    'unix': '유닉스 리눅스 서버 unix linux server',
    'db': '데이터베이스 디비 dbms database sql',
    'fin': '금융 전자금융 핀테크 financial',
    'win': '윈도우 서버 windows server',
    'net': '네트워크 라우터 스위치 장비 network',
    'sec': '보안장비 방화벽 침입탐지 firewall ips ids waf',
    'cloud': '클라우드 컨테이너 쿠버네티스 도커 cloud kubernetes k8s docker',
    'ics': '제어시스템 산업제어 ics scada ot plc',
    'ai': 'AI 인공지능 LLM 생성형 프롬프트 머신러닝 딥페이크',
    'auto': '자동차 차량 모빌리티 automotive vehicle can ecu uds ota misra',
    'privacy': '개인정보 프라이버시 가명처리 영향평가 privacy pia 보호법',
    'zt': '제로트러스트 zero trust 성숙도 maturity 암묵적신뢰 최소권한 마이크로세그멘테이션 지속인증 pam dlp',
    'sim': '시뮬레이터 실습 체험 simulator',
    'guide': '가이드 안내 개념 guide',
}

# 대표 도구 페이지: (파일, 제목, 키워드) — 우선 노출용 별칭
TOOL_ALIAS = {
    'vuln-hub.html': ('미션 컨트롤 (허브)', '홈 main 시작 대시보드 hub'),
    'redteam.html': ('AI 레드팀 아레나', '레드팀 redteam 공격 방어 대결 아레나 에이전트'),
    'vulnlab.html': ('취약점 실습장 (버프 스타일 시뮬레이터 · 51미션)', '실습장 vulnlab 버프 burp repeater 공격 sqli xss ssrf csrf xxe 금융 AI 실습 해킹'),
    'quiz-forge.html': ('AI 문제 포지 (생성-검증 출제기)', '출제 퀴즈 quiz forge 문제 생성 검증'),
    'my-progress.html': ('내 학습 현황 (대시보드)', '진도 기록 대시보드 마이페이지 progress'),
    'training-dashboard.html': ('훈련 대시보드', '훈련 dashboard 통계'),
    'labs-live.html': ('라이브 랩 (실제 실행 환경)', '랩 lab 실습 live 실행'),
    'ai-tutor.html': ('AI 튜터 (1:1 학습 코치)', '튜터 tutor 코치 학습 ai'),
    'ai-grader.html': ('AI 채점기', '채점 grader 평가'),
    'lab-generator.html': ('무한 문제 생성기', '무한 생성기 generator 문제'),
    'skill-assess.html': ('스킬 레이더 · 검증자격', '스킬 레이더 자격 assess 평가'),
    'skill-tree.html': ('스킬 트리', '스킬트리 tree 성장'),
    'certificate.html': ('수료증 발급', '수료증 certificate 자격'),
    'wrong-note.html': ('오답 노트', '오답 wrong note 틀린문제'),
    'mission-board.html': ('미션 보드', '미션 mission 보드 퀘스트'),
    'classroom.html': ('강의실 (클래스룸)', '강의 classroom 클래스 수업'),
    'class-report.html': ('클래스 리포트', '리포트 report 반 통계'),
    'instructor-dashboard.html': ('강사 대시보드', '강사 instructor 교사'),
    'exam-runner.html': ('시험 실행기', '시험 exam 테스트'),
    'question-admin.html': ('문제 은행 관리', '문제은행 admin 관리'),
    'question-packs.html': ('문제 팩', '팩 pack 문제모음'),
    'code-fix-lab.html': ('코드 수정 랩', '코드수정 fix 랩 실습'),
    'code-review-game.html': ('코드 리뷰 게임', '리뷰 게임 review game'),
    'secure-code-lab.html': ('시큐어 코딩 랩', '시큐어코딩 lab 실습'),
    'secure-dev-portal.html': ('개발보안 학습 포털', '개발보안 portal 포털 행안부 kisa'),
    'secure-dev-academy.html': ('개발보안 아카데미', '아카데미 academy 강좌'),
    'secure-dev-quiz.html': ('개발보안 퀴즈', '퀴즈 quiz 진단'),
    'coding-standards.html': ('코딩 표준', '표준 standards 컨벤션'),
    'content-map.html': ('콘텐츠 맵', '맵 map 목차 사이트맵'),
    'breach-campaign.html': ('침해 사고 캠페인 (스토리)', '침해 breach 사고 스토리 캠페인'),
    'security-incidents.html': ('보안 사고 사례', '사고 incidents 사례'),
    'report-builder.html': ('리포트 빌더', '리포트 builder 보고서'),
    'live-class.html': ('라이브 클래스', '라이브 live 클래스 수업'),
    'verify.html': ('검증 페이지', 'verify 검증'),
    'index.html': ('WEB-VULN-SIM 시작 페이지', '인덱스 index 첫화면'),
    'training-dashboard.html': ('훈련 대시보드', '훈련 dashboard'),
    'privacy-hub.html': ('개인정보보호 학습 허브', '개인정보 privacy 보호법 pipa 프라이버시 허브 트랙'),
    'pia-assessment.html': ('개인정보 영향평가(PIA) 자가진단 · 121항목',
                            '영향평가 pia 자가진단 평가항목 이행률 개선과제 개인정보 privacy impact assessment 보호책임자 접속기록 암호화 가명정보 자동화된결정 인공지능'),
    'privacy-policy-builder.html': ('개인정보 처리방침 작성·점검기 · 24개 기재사항',
                                    '처리방침 작성 점검 기재사항 privacy policy 라벨링 쿠키 행태정보 국외이전 위탁 보유기간 생성형 ai 부록'),
    'pseudonym-lab.html': ('가명처리 실습실 · k-익명성·재식별',
                           '가명처리 가명정보 k익명성 l다양성 재식별 연결공격 linkage 마스킹 범주화 라운딩 해시 토큰화 잡음 총계처리 순열 pseudonymization'),
    'privacy-policy-eval.html': ('개인정보 처리방침 평가 시뮬레이터 · 적정성·가독성·접근성',
                                 '처리방침 평가제 적정성 가독성 접근성 제30조의2 고시 2024-3 평가대상 개선권고 스크롤 클릭 실측 policy evaluation'),
    'privacy-penalty-calc.html': ('개인정보 과징금 산정 구조 시뮬레이터',
                                  '과징금 산정 부과기준 제64조의2 별표1의5 관련매출액 부과기준율 중대성 위반기간 가중 감경 절사 징벌적 매출액 10% penalty fine'),
    'fincloud-hub.html': ('금융 클라우드 보안 진단 시뮬레이터 · AWS CLI 실습 22종',
                          '금융 클라우드 aws 진단 평가기준 pism 퍼블릭 클라우드 관리체계 취약점 cli 콘솔 s3 ec2 rds iam lambda cloudtrail 보안그룹 kms 암호화 mfa 액세스키 imdsv2 ebs 스냅샷 ami 코드서명 cloudshell 최소권한 terraform iac fincloud'),
    'privacy-pseudonym-process.html': ('가명처리 5단계 절차 · 위험도 판정기 (2026.3 개정)',
                                       '가명처리 절차 5단계 사전준비 위험성 검토 적정성 검토 안전한 관리 위험도 저위험 중위험 고위험 판정 검토위원회 내부심의 담당자 검토 서식 10종 위험성 검토서 가명처리 계획서 결과서 관리대장 결합전문기관 데이터전문기관 이노베이션 존 비정형데이터 반복 유사 활용 통계작성 과학적 연구 공익적 기록보존 제28조의2 제28조의4 가명정보 가이드라인 pseudonymization risk tier'),
    'privacy-basis-check.html': ('개인정보 적법 처리근거 판단기 · 수집·제공·목적 외',
                                 '적법근거 처리근거 판단 제15조 제17조 제18조 제19조 수집 이용 제3자 제공 목적외 추가적 이용 시행령 14조의2 정당한 이익 계약 이행 법령상 의무 공공기관 소관업무 민감정보 고유식별정보 주민등록번호 24조의2 동의 불가 관보 게재 대장 lawful basis legal ground'),
    'privacy-consent-designer.html': ('개인정보 동의서 설계·점검기 · 다크패턴 7종',
                                      '동의서 설계 점검 별도 동의 제22조 시행령 17조 고시 4조 법정 고지사항 중요한 내용 표시 자유로운 의사 포괄동의 필수동의 선택동의 기본값 체크박스 1mm 스크롤 다크패턴 판례 2014두2638 2018도13694 consent dark pattern'),
    'privacy-processor-check.html': ('위탁·제3자 제공·영업양도 구분기 · 대법원 기준',
                                     '위탁 수탁자 위수탁 제3자 제공 영업양도 합병 구분 제26조 제27조 시행령 28조 29조 계약서 필수 기재사항 재위탁 동의 교육 감독 홈페이지 공개 홍보 판매 권유 개별 고지 손해배상 대법원 2016도13263 2020도13960 outsourcing processor controller'),
    'privacy-updates.html': ('개인정보 법·제도 업데이트 & 공식 포털 · 2026.9.11 개정',
                             '개정 2026 시행 변경점 위조 변조 훼손 유출 가능성 통지 피해구제 손해배상 분쟁조정 징벌적 과징금 cpo isms-p 포털 pipc privacy.go.kr 국가법령정보센터 털린 내 정보 찾기 e프라이버시'),
    'privacy-policy.html': ('WEB-VULN-SIM 개인정보 처리방침', '처리방침 개인정보 privacy policy 수집항목 국외이전 보유기간 보호책임자 이용약관'),
    'privacy-quiz.html': ('개인정보 법령 Q&A · 질의응답 99건',
                          '질의응답 모음집 법령해석 사례 조문 퀴즈 카드 오답 정의 영상정보 가명정보 공공서비스 민간사업자 민감 고유식별 위수탁 privacy qa quiz'),
    'privacy-scope-check.html': ('개인정보 영향평가 대상·적용범위 판단기',
                                 '영향평가 대상 판단 적용범위 5만 50만 100만 공공기관 공공시스템 안전성확보조치 10만명 암호키 재해재난 과태료 scope'),
    'privacy-breach-drill.html': ('개인정보 유출 72시간 대응 훈련',
                                  '유출 통지 신고 72시간 제34조 대응 훈련 인시던트 모의훈련 1천명 민감정보 외부 불법접근 breach drill incident'),
}

SITE_SUFFIX = re.compile(r'\s*[|·—–-]\s*(WEB-VULN-SIM|Web Security Simulator)[^<]{0,60}$', re.I)


def group_of(fn):
    for pre, g in PREFIX_GROUP:
        if fn.startswith(pre):
            return g
    return 'tools'


def title_of(html):
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    if not m:
        return None
    t = re.sub(r'\s+', ' ', m.group(1)).strip()
    t = SITE_SUFFIX.sub('', t)
    return t


def main():
    pages = []
    for fn in sorted(os.listdir(BASE)):
        if not fn.endswith('.html') or fn in EXCLUDE:
            continue
        path = os.path.join(BASE, fn)
        try:
            html = open(path, encoding='utf-8', errors='replace').read(20000)
        except OSError:
            continue
        g = group_of(fn)
        if fn in TOOL_ALIAS:
            t, k = TOOL_ALIAS[fn]
            g = 'tools' if g == 'tools' else g
        else:
            t = title_of(html)
            k = ''
            if not t:
                continue
        # 검색 보조: 파일명 토큰 (u-01, d-05, sql 등 코드 검색 지원)
        fn_kw = fn.replace('.html', '').replace('_', ' ').replace('-', ' ')
        # [G03] 그룹 동의어. 이게 없어서 '자동차'/'쿠버네티스' 검색이 0건이었다
        # (14_auto-* 61개가 있는데도 k 값이 '14 auto auto01' 뿐이라 한글로는 안 잡혔다).
        kw = ' '.join(x for x in (k, fn_kw, GROUP_SYNONYMS.get(g, '')) if x).strip()
        pages.append({'t': t[:80], 'u': fn, 'g': g, 'k': kw[:220]})

    # 대표 도구를 앞으로 정렬(동점 점수 시 안정적)
    order = {'hub': 0, 'tools': 1}
    pages.sort(key=lambda p: (order.get(p['g'], 2), p['u']))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = {
        'generated': datetime.date.today().isoformat(),
        'count': len(pages),
        'pages': pages,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    print('OK: %d페이지 → %s' % (len(pages), OUT))


if __name__ == '__main__':
    main()
