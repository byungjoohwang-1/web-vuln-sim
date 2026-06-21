# -*- coding: utf-8 -*-
"""상용/오픈 SAST 도구 비교 — 이 교육 포털의 채점 엔진(LASHR)을 실제 정적분석 도구와 견주어
'우리가 어디에 위치하는가'를 정직하게 보여 준다. academy 대시보드의 '도구 비교' 섹션에서 렌더.
"""

# 분석 방식 등급: 'pattern'(구문 패턴), 'dataflow'(데이터플로우/택트), 'pathsens'(경로 민감 인터프로시저)
TOOLS = [
    {'name':'Fortify SCA','vendor':'OpenText (구 Micro Focus/HP)','license':'상용',
     'method':'데이터플로우/택트 분석(다언어)','strong':'엔터프라이즈 규모·규정(OWASP/CWE/PCI) 매핑·광범위한 룰',
     'limit':'고가, 오탐 다수로 트리아지·튜닝 부담'},
    {'name':'Checkmarx CxSAST','vendor':'Checkmarx','license':'상용',
     'method':'쿼리 기반 AST/그래프 데이터플로우','strong':'정밀 데이터플로우·증분 스캔·IDE/CI 통합',
     'limit':'고가, 커스텀 쿼리 학습곡선'},
    {'name':'Coverity','vendor':'Synopsys (Black Duck)','license':'상용',
     'method':'경로 민감 인터프로시저 분석','strong':'낮은 오탐·대규모 C/C++/Java에 강함',
     'limit':'고가, 셋업·빌드 통합 복잡'},
    {'name':'Snyk Code','vendor':'Snyk','license':'상용(무료 티어)',
     'method':'ML 기반 시맨틱 분석','strong':'빠른 속도·개발자 친화·IDE/PR 통합',
     'limit':'커스텀 룰·온프렘에 제약'},
    {'name':'SonarQube','vendor':'SonarSource','license':'오픈코어(CE 무료)',
     'method':'규칙 기반 + 일부 택트','strong':'코드품질+보안 통합·CI 친화·무료 CE',
     'limit':'심층 보안(택트)은 상용 에디션 필요'},
    {'name':'Semgrep','vendor':'Semgrep (오픈)','license':'오픈(상용 티어)',
     'method':'구문 패턴 매칭(AST 기반)','strong':'경량·고속·룰 작성 쉬움·무료',
     'limit':'데이터플로우(택트)는 상용 한정, 구문 의존'},
    {'name':'이 포털 (LASHR)','vendor':'KISA 진단원 교육 포털','license':'교육용',
     'method':'경량 구문 휴리스틱(주석 제거 + 정규식 패턴)','strong':'정·오탐 판별 학습·즉시 피드백·49개 약점 매핑·무설치',
     'limit':'생산용 스캐너 아님 — 데이터플로우/경로분석 없음, 6대 핵심 외엔 키워드 보조'},
]

# 포털의 정직한 위치 설명 (대시보드 안내문)
POSITION = ('이 포털은 코드를 자동 스캔하는 <b>생산용 SAST 도구가 아니라</b>, '
            'KISA 소프트웨어 보안약점 <b>진단원을 양성하는 교육 도구</b>입니다. '
            '채점 엔진 LASHR은 Semgrep과 같은 <b>구문 패턴 매칭(휴리스틱) 계열</b>로, '
            'Coverity·Fortify의 <b>경로 민감 데이터플로우(택트) 분석</b>과는 깊이가 다릅니다. '
            '목적은 자동 탐지가 아니라, <b>사람이 정·오탐을 직접 판별·학습</b>하도록 돕는 것입니다. '
            '실무에서는 상용 도구의 결과도 오탐·미탐이 있어 진단원의 수동 검증이 반드시 필요합니다.')
