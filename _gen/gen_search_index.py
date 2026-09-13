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
    ('sim-', 'sim'), ('guide-', 'guide'),
]

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
        kw = (k + ' ' + fn_kw).strip()
        pages.append({'t': t[:80], 'u': fn, 'g': g, 'k': kw[:120]})

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
