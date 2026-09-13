/**
 * WEB-VULN-SIM — 산업 분야별 맞춤 보안 학습 트랙 데이터 (Industry Tracks)
 *
 * 6대 산업 분야:
 * 1. 🏦 금융·핀테크 (Finance & Fintech)
 * 2. 🚗 모빌리티·자동차 (Automotive & Mobility)
 * 3. 🏭 스마트제조·OT (Smart Factory & ICS/SCADA)
 * 4. ☁️ 클라우드·AI (Cloud, SaaS & AI)
 * 5. 🏛️ 공공·인프라 (Public & Critical Infrastructure)
 * 6. 🔏 개인정보·거버넌스 (Privacy & Data Governance)
 */
window.WVS_INDUSTRY_TRACKS = [
  {
    id: 'fin',
    name: '금융 · 핀테크',
    enName: 'Finance & Fintech',
    icon: '🏦',
    badge: '전자금융 평가기준 전수 구현',
    enBadge: 'Full Fin-Sec Benchmark',
    standards: '「전자금융기반시설 보안 취약점 평가기준(제2026-1호)」 · 전자금융감독규정',
    enStandards: 'Electronic Financial Infrastructure Security Criteria #2026-1',
    desc: '송금·결제 무결성, 리플레이 방지, 금융형 IDOR(소유주 검증), 모바일 앱 위변조 방지 및 단말 보안 등 전자금융 전 영역을 아우르는 실무 실습입니다.',
    enDesc: 'Hands-on training covering transaction integrity, replay prevention, financial IDOR, anti-tampering, and mobile app protection.',
    hubGroup: 'groupC',
    filterTag: 'fin',
    totalLabs: '43+ 실습',
    threats: [
      { title: '거래정보 무결성 변조', page: '07_fin-transaction-integrity.html', desc: '이체 금액/수취 계좌 파라미터 조작 시도' },
      { title: '거래정보 재사용 (리플레이)', page: '07_fin-replay.html', desc: '정상 승인 패킷을 가로채 중복 인출 유도' },
      { title: '금융형 IDOR (소유주 검증)', page: '07_fin-idor-account.html', desc: '타인 계좌의 거래 내역 조회 및 임의 인출' },
      { title: '루팅·탈옥 단말 탐지', page: '07_fin-device-rooting.html', desc: '루팅된 기기에서의 전자금융 앱 구동 차단' }
    ],
    role: '금융 서비스 개발자, 핀테크 보안 엔지니어, 전자금융 취약점 진단원'
  },
  {
    id: 'auto',
    name: '모빌리티 · 자동차',
    enName: 'Automotive & Mobility',
    icon: '🚗',
    badge: 'ISO/SAE 21434 & R155/156',
    enBadge: 'UN R155/R156 Compliant',
    standards: 'ISO/SAE 21434 · UNECE R155/R156 · AUTOSAR C++14 · MISRA C:2012',
    enStandards: 'ISO/SAE 21434 · UNECE R155/R156 · AUTOSAR C++14',
    desc: 'CAN 버스 제어 명령 스푸핑부터 TARA 위협 분석, 커넥티드카 IVI 침투, OTA 펌웨어 서명 검증 및 롤백 방지까지 차량 전주기 보안을 다룹니다.',
    enDesc: 'Comprehensive vehicular security: CAN bus spoofing, TARA, OTA firmware integrity, and vehicle telematics defense.',
    hubGroup: 'groupE',
    filterTag: 'auto',
    totalLabs: '61+ 실습',
    threats: [
      { title: 'CAN 메시지 스푸핑', page: '14_auto-auto01.html', desc: '차량 내부 CAN 버스에 가짜 가속/조향 명령 주입' },
      { title: 'UDS 진단 서비스 우회', page: '14_auto-auto04.html', desc: 'SecurityAccess(0x27) 취약점을 이용한 진단망 탈취' },
      { title: 'OTA 서명 검증 부재', page: '14_auto-auto11.html', desc: '변조된 악성 펌웨어 패키지 무검증 업데이트 차단' },
      { title: 'TARA 위협 분석 실습', page: '14_auto-auto17.html', desc: 'ISO/SAE 21434 기반 위협 시나리오 도출 및 위험도 산정' }
    ],
    role: '차량 임베디드 SW 개발자, 커넥티드카 보안 담당자, 전장 ECU 연구원'
  },
  {
    id: 'ics',
    name: '스마트제조 · 산업제어(OT)',
    enName: 'Smart Factory & ICS/SCADA',
    icon: '🏭',
    badge: 'NIST SP 800-82 & IEC 62443',
    enBadge: 'OT/ICS Industrial Defense',
    standards: 'NIST SP 800-82 Rev.3 · IEC 62443 · 주요정보통신기반시설(제어시스템) 평가기준',
    enStandards: 'NIST SP 800-82 Rev.3 · IEC 62443 · Critical Infrastructure OT',
    desc: '스마트 팩토리 공정 제어망(OT)의 IT/OT 망분리 경계 보호, Modbus/DNP3 제어 프로토콜 보안, PLC 로직 무결성 검증을 직접 시뮬레이션합니다.',
    enDesc: 'Simulate industrial OT boundary defense, Modbus/DNP3 plaintext sniffing, and PLC logic manipulation.',
    hubGroup: 'groupB',
    filterTag: 'ics',
    totalLabs: '14+ 실습',
    threats: [
      { title: 'IT/OT 망 분리 미흡', page: '12_ics-ics02.html', desc: '사내망에서 공장 공정망으로의 비인가 접근 차단' },
      { title: 'Modbus/DNP3 평문 프로토콜', page: '12_ics-ics03.html', desc: '발신자 확인 없는 제어 명령 패킷 변조 및 탈취' },
      { title: 'PLC 로직/펌웨어 무결성', page: '12_ics-ics07.html', desc: '승인되지 않은 사다리꼴 로직(Ladder) 주입 방어' },
      { title: 'PLC 쓰기보호 및 운영모드', page: '12_ics-ics14.html', desc: '원격 쓰기 방지(Run 모드 전환) 및 물리 잠금' }
    ],
    role: '스마트공장 운영 관리자, 제어망(OT) 엔지니어, 산업보안 진단원'
  },
  {
    id: 'cloud_ai',
    name: '클라우드 · AI 신기술',
    enName: 'Cloud & AI Security',
    icon: '☁️',
    badge: 'OWASP LLM Top 10 & CSAP',
    enBadge: 'Cloud & GenAI Protection',
    standards: 'OWASP Top 10 for LLM · KISA 클라우드 보안인증(CSAP) · CIS K8s Benchmarks',
    enStandards: 'OWASP LLM Top 10 · KISA CSAP · CIS Kubernetes',
    desc: '클라우드 IAM 최소권한, S3 버킷 노출, K8s RBAC/특권 컨테이너 격리부터 생성형 AI 프롬프트 인젝션, RAG 포이즈닝, 모델 도용 방어까지 최신 신기술 위협을 다룹니다.',
    enDesc: 'Defense against cloud misconfigurations (IAM, K8s) and Generative AI attacks (Prompt Injection, RAG poisoning).',
    hubGroup: 'groupD',
    filterTag: 'cloud_ai',
    totalLabs: '46+ 실습',
    threats: [
      { title: '직접 프롬프트 인젝션', page: '13_ai-ai01.html', desc: '시스템 지시사항을 무시하고 기밀을 출력하도록 우회' },
      { title: '간접 프롬프트 인젝션 (RAG)', page: '13_ai-ai02.html', desc: '외부 문서에 악의적 프롬프트를 삽입해 에이전트 탈취' },
      { title: '과도한 IAM 권한 (Admin)', page: '11_cloud-c02.html', desc: '최소권한 원칙 위반으로 인한 전체 클라우드 자원 장악' },
      { title: '특권(Privileged) 컨테이너', page: '11_cloud-c13.html', desc: '컨테이너 탈옥을 통한 호스트 노드 루트 권한 탈취' }
    ],
    role: '클라우드/DevSecOps 엔지니어, AI/ML 서비스 개발자, 프롬프트 엔지니어'
  },
  {
    id: 'infra',
    name: '공공 · 인프라 · 시스템',
    enName: 'Public & Infrastructure',
    icon: '🏛️',
    badge: '주요정보통신기반시설 104종',
    enBadge: 'Major Infrastructure Standards',
    standards: '주요정보통신기반시설 기술적 취약점 분석·평가 기준 (UNIX/Windows/DB/Network/Security)',
    enStandards: 'Technical Vulnerability Assessment Guide for Critical Telecommunications Infrastructure',
    desc: '정부·공공기관 및 국가 핵심 시설이 준수해야 하는 서버, 데이터베이스, 네트워크 라우터/스위치, 보안장비 104종 전 항목을 동적 인터랙티브 데모로 점검합니다.',
    enDesc: '104 infrastructure diagnostic items covering Linux, Windows, DBMS, network, and firewall/VPN devices.',
    hubGroup: 'groupB',
    filterTag: 'infra',
    totalLabs: '104+ 실습',
    threats: [
      { title: 'root 원격 접속 제한 (U-01)', page: '05_linux-u01.html', desc: 'Telnet/SSH에서 관리자 직간접 접속 통제' },
      { title: 'DBA 권한 최소화 (D-06)', page: '06_db-d06.html', desc: '일반 계정의 PUBLIC 권한 회수 및 스키마 격리' },
      { title: '광범위 Any-Any 룰 제거 (S-10)', page: '10_sec-s10.html', desc: '방화벽 정책의 과도한 개방 방지 및 기본 Deny' },
      { title: 'VTY 접근 ACL 제한 (N-05)', page: '09_net-n05.html', desc: '네트워크 관리 포트의 비인가 IP 접속 차단' }
    ],
    role: '인프라/시스템 엔지니어, 정보보호 컨설턴트, 기반시설 진단원'
  },
  {
    id: 'privacy',
    name: '개인정보 · 거버넌스',
    enName: 'Privacy & Data Governance',
    icon: '🔏',
    badge: '2026 최신 안내서 & PIA 도구',
    enBadge: 'Privacy Act & PIA Self-Check',
    standards: '「개인정보 보호법(2024 개정)」 · 가명정보 처리 가이드라인 · 유출대응 안내서(2026.9.)',
    enStandards: 'Personal Information Protection Act · Pseudonymization Guide · Breach Response (2026.9)',
    desc: '단순 암기가 아닌 실제 산출물 중심 실습: 121개 항목 PIA 자가진단, 24개 조항 처리방침 작성·점검, 재식별 공격 가명처리 랩, 최신 기준 유출사고 모의훈련.',
    enDesc: 'Real-world privacy compliance: 121-item PIA assessment, 24-section policy linting, and k-anonymity lab.',
    hubGroup: 'groupF',
    filterTag: 'privacy',
    totalLabs: '34+ 실습',
    threats: [
      { title: '유출 72시간 모의 대응 훈련', page: 'privacy-breach-drill.html', desc: '2026.9 최신 안내서 기반 통지·신고 타임라인 작성' },
      { title: '개인정보 영향평가 (PIA)', page: 'pia-assessment.html', desc: '121개 평가항목 자가진단 및 위험도 채점' },
      { title: '가명처리 실습실 (k-익명성)', page: 'pseudonym-lab.html', desc: '연결공격(Linkage Attack) 방어 및 재식별 위험도 측정' },
      { title: '처리방침 자동 점검 빌더', page: 'privacy-policy-builder.html', desc: '24개 법정 기재사항 자동 린팅 및 검증' }
    ],
    role: '개인정보보호책임자(CPO), 개인정보 취급자, 컴플라이언스/법무 담당자'
  }
];

// 직무별 맞춤 로드맵 (Role-based Pathways)
window.WVS_ROLE_PATHWAYS = [
  {
    id: 'developer',
    title: 'SW 개발자 / 클라우드 엔지니어',
    enTitle: 'Software & Cloud Developer',
    icon: '💻',
    tag: '시큐어코딩 · API · Cloud',
    enTag: 'Secure Coding · API · Cloud',
    desc: '코드 수준의 보안 약점 예방과 안전한 클라우드 아키텍처 설계',
    curriculum: [
      { name: 'KISA 시큐어코딩 49개 보안약점', url: 'secure-dev-portal.html' },
      { name: '클라우드 IAM & K8s 보안 20종', url: '11_cloud-c01.html' },
      { name: '웹 취약점 51개 실습장 (BugPay)', url: 'vulnlab.html' },
      { name: 'OWASP LLM AI 보안 26종', url: '13_ai-ai01.html' }
    ]
  },
  {
    id: 'assessor',
    title: '보안 진단원 / 모의해킹 전문가',
    enTitle: 'Security Assessor & Pentester',
    icon: '🕵️',
    tag: '기반시설 진단 · DAST · 레드팀',
    enTag: 'Infrastructure Audit · Red Team',
    desc: '서버, 네트워크, 보안장비, 웹/앱 전 영역의 기술적 취약점 분석·평가',
    curriculum: [
      { name: '주요정보통신기반시설 104종 전수 점검', url: 'vuln-hub.html#catalog' },
      { name: '전자금융기반시설 취약점 평가 43종', url: '07_fin-transaction-integrity.html' },
      { name: 'AI 레드팀 아레나 (4단계 침투 대결)', url: 'redteam.html' },
      { name: '진단원 자격 취득 훈련장', url: 'training-dashboard.html' }
    ]
  },
  {
    id: 'compliance',
    title: '개인정보보호책임자(CPO) / 컴플라이언스',
    enTitle: 'CPO & Compliance Officer',
    icon: '⚖️',
    tag: '개인정보보호법 · PIA · 유출대응',
    enTag: 'Privacy Act · PIA · Breach Response',
    desc: '법률 조문 준수와 실제 시스템 산출물(PIA, 처리방침, 가명정보) 검증',
    curriculum: [
      { name: '개인정보보호 실무 학습 허브', url: 'privacy-hub.html' },
      { name: 'PIA 개인정보 영향평가 121항목 자가진단', url: 'pia-assessment.html' },
      { name: '가명정보 처리 실습 (k-익명성)', url: 'pseudonym-lab.html' },
      { name: '유출 사고 72시간 모의 대응 훈련', url: 'privacy-breach-drill.html' }
    ]
  },
  {
    id: 'embedded',
    title: '임베디드 / 모빌리티 / OT 엔지니어',
    enTitle: 'Embedded, Mobility & OT Engineer',
    icon: '⚙️',
    tag: 'ISO/SAE 21434 · MISRA · ICS',
    enTag: 'Automotive Cybersec · MISRA · ICS',
    desc: '자동차 제어망(CAN), 안전필수 C/C++ 표준, 스마트공장 제어시스템 보안',
    curriculum: [
      { name: '자동차 사이버보안 61종 (CAN·OTA·TARA)', url: '14_auto-auto01.html' },
      { name: 'C/C++ 안전 코딩 표준 (MISRA·AUTOSAR)', url: 'coding-standards.html' },
      { name: '스마트팩토리 제어시스템(ICS/SCADA) 14종', url: '12_ics-ics01.html' },
      { name: '스마트 모빌리티 복합 침해사고 대응', url: 'incident.html' }
    ]
  }
];
