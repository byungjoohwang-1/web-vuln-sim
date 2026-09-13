# -*- coding: utf-8 -*-
"""제로트러스트 시뮬레이터 명세 — 6대 핵심 요소.

참고한 것은 공개 자료의 **구조**뿐이다(6대 핵심 요소 = 식별자·신원 / 기기·엔드포인트 /
네트워크 / 시스템 / 애플리케이션·워크로드 / 데이터, 4단계 성숙도 = 기존·초기·향상·최적화).
시나리오·코드·문장은 전부 새로 썼다.

'risk' 필드는 이 템플릿에서 성숙도 이동(현재 → 목표)을 표시하는 데 쓴다.
"""

SPECS = [

# ── 1. 식별자·신원 : 식별자 관리 ───────────────────────────────────────
{
 'file': '16_zt-identity-inventory.html',
 'title': '사용자 인벤토리 없는 조직의 유령 계정',
 'icon': '🪪', 'target': '사내 통합 인증(IdP)', 'risk': '기존 → 향상',
 'item_code': '식별자·신원 / 식별자 관리',
 'attack_panel_title': '퇴사자 계정으로 로그인',
 'scenario_html': '제로트러스트의 출발점은 "누가 있는지 전부 알고 있는가"입니다. '
    '사용자 목록이 시스템마다 흩어져 있고 인사 시스템과 연결돼 있지 않으면, '
    '<b>퇴사·부서이동으로 없어져야 할 계정이 살아남습니다</b>. '
    '경계 안에 있다는 이유로 신뢰하는 구조에서는 이 유령 계정이 가장 조용한 침입 경로가 됩니다.',
 'attack_name': '비활성화되지 않은 퇴사자 계정 사용', 'attack_sub': '인사 퇴직 처리 후 62일 경과, 계정은 여전히 활성',
 'normal_req': 'POST /idp/login\n{\n  "user": "kim.jr",\n  "hr_status": "재직",\n  "last_login": "2026-09-12"\n}',
 'attack_req': 'POST /idp/login\n{\n  "user": "lee.former",      // 2026-07-13 퇴직\n  "hr_status": "퇴직",        // IdP 는 이 값을 보지 않는다\n  "last_login": "2026-07-10"\n}',
 'vuln_logs_js': "addLog('[IdP] lee.former 인증 성공 — 계정 상태 activate','warn'); "
                 "addLog('[HR] 동일 사번 퇴직 처리일 2026-07-13 (62일 전)','warn'); "
                 "addLog('[IdP] 인사 시스템 연계 없음 → 상태 대조 미수행','error'); "
                 "addLog('[VPN] 사내망 접속 허용 → 파일서버 3종 마운트','error');",
 'breach_html': '<strong>🚨 유령 계정 접속 성공</strong><br>인사 상태와 계정 상태가 연결돼 있지 않아 퇴직자 계정이 그대로 살아 있었습니다.'
    '<table class="data-table"><tr><th>구분</th><th>인사 시스템</th><th>인증 시스템</th></tr>'
    '<tr><td>상태</td><td>퇴직(2026-07-13)</td><td style="color:#b71c1c">활성</td></tr>'
    '<tr><td>권한</td><td>회수 대상</td><td style="color:#b71c1c">영업DB 조회 유지</td></tr>'
    '<tr><td>점검 주기</td><td>—</td><td style="color:#b71c1c">수동, 반기 1회</td></tr></table>',
 'violations': ['식별자·신원 / 식별자 관리 — 사용자 인벤토리가 권위 있는 출처와 연계되지 않음',
                '퇴직·이동 시 접근 권한 회수가 자동으로 일어나지 않음',
                '성숙도 1단계(기존): 계정 목록을 사람이 수작업으로 맞춤'],
 'defense_intro': '사용자 인벤토리는 <strong>인사 시스템을 권위 있는 출처(authoritative source)</strong>로 삼아야 합니다. '
    '인증할 때마다 재직 상태를 확인하고, 상태가 바뀌면 즉시 권한이 따라 움직이게 만드세요.',
 'vuln_code': '// [취약] 계정 테이블만 보고 인증을 끝낸다\npublic Session login(String id, String pw) {\n    Account a = accounts.find(id);\n    if (a != null && a.verify(pw)) {\n        return Session.create(a);   // 재직 여부는 확인하지 않음\n    }\n    throw new AuthException("인증 실패");\n}',
 'secure_hint': '// [안전] 권위 있는 출처(HR)와 대조 + 상태 변경 시 즉시 반영\npublic Session login(String id, String pw) {\n    Account a = accounts.find(id);\n    if (a == null || !a.verify(pw)) throw new AuthException("인증 실패");\n\n    // 1) 인사 시스템을 권위 있는 출처로 삼아 재직 상태를 확인\n    HrRecord hr = hrDirectory.lookup(a.getEmployeeNo());\n    if (hr == null || !hr.isActive())\n        throw new AuthException("재직 상태가 아닌 계정");\n\n    // 2) 인벤토리에 없는 계정(고아 계정)은 거부하고 기록\n    if (!inventory.contains(a.getId())) {\n        audit.orphanAccount(a.getId());\n        throw new AuthException("인벤토리 미등록 계정");\n    }\n\n    // 3) 상태 변경 이벤트를 구독해 권한을 즉시 회수\n    hrDirectory.onStatusChange(a.getEmployeeNo(), ev -> entitlements.revokeAll(a));\n    return Session.create(a);\n}',
 'checks': [['hrDirectory', 'isActive', '재직'], ['inventory', 'orphan', 'revoke']],
 'success_msg': '인사 상태 대조와 인벤토리 검증으로 유령 계정 로그인이 차단됩니다.',
 'fail_msg': '권위 있는 출처(인사) 대조와 인벤토리 미등록 계정 거부가 필요합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>조직이 가진 <b>모든 사용자 식별자를 한 곳에서 알고 있는지</b>, '
    '그 목록이 사람 손이 아니라 권위 있는 출처와 자동으로 맞춰지는지를 본다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 시스템마다 계정 목록이 따로 있고 반기·연 단위로 수작업 대조</li>'
    '<li><b>초기</b> — 통합 디렉터리는 있으나 인사 연계는 배치(일 1회)</li>'
    '<li><b>향상</b> — 입·퇴사/이동 이벤트가 실시간으로 계정·권한에 반영</li>'
    '<li><b>최적화</b> — 미사용·고아 계정을 자동 탐지해 스스로 정리하고 그 근거를 남김</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>인사-디렉터리 연계 설정과 최근 동기화 이력</li>'
    '<li>퇴직 처리 시각 대비 권한 회수 시각의 간격 통계</li>'
    '<li>고아 계정 탐지 규칙과 조치 기록</li></ul>',
},

# ── 2. 식별자·신원 : 인증(MFA) ────────────────────────────────────────
{
 'file': '16_zt-mfa.html',
 'title': '단일 비밀번호가 남긴 크리덴셜 스터핑',
 'icon': '🔑', 'target': '임직원 포털 로그인', 'risk': '기존 → 향상',
 'item_code': '식별자·신원 / 인증 — 다중인증(MFA)',
 'attack_panel_title': '유출 계정 목록 대입',
 'scenario_html': '비밀번호는 이미 유출된 자격 증명으로 간주해야 합니다. '
    '<b>다중인증이 없으면</b> 외부에서 떠도는 아이디·비밀번호 목록을 그대로 대입하는 것만으로 '
    '정상 로그인과 구분되지 않는 접속이 만들어집니다. '
    '"내부망이니까 괜찮다"는 가정은 이 지점에서 가장 먼저 무너집니다.',
 'attack_name': '크리덴셜 스터핑', 'attack_sub': '타 서비스 유출 목록 1,200건 자동 대입',
 'normal_req': 'POST /login\n{\n  "id": "park.dev",\n  "pw": "********"\n}\n→ 200 OK (세션 발급)',
 'attack_req': 'POST /login   × 1,200 (자동화)\n{\n  "id": "park.dev",\n  "pw": "Summer2025!"   // 타 서비스 유출본\n}\n→ 2차 인증 요구 없음',
 'vuln_logs_js': "addLog('[BOT] 유출 목록 1,200건 대입 시작','warn'); "
                 "addLog('[AUTH] 비밀번호 일치 14건 → 전부 세션 발급','error'); "
                 "addLog('[AUTH] 2차 인증 단계 없음','error'); "
                 "addLog('[AUTH] 신규 국가/신규 단말 여부 미판정','warn');",
 'breach_html': '<strong>🚨 14개 계정 탈취</strong><br>비밀번호 하나만 맞으면 끝나는 구조라 자동 대입이 그대로 통했습니다.'
    '<table class="data-table"><tr><th>시도</th><th>성공</th><th>추가 인증</th><th>차단</th></tr>'
    '<tr><td>1,200</td><td style="color:#b71c1c">14</td><td style="color:#b71c1c">없음</td><td style="color:#b71c1c">없음</td></tr></table>',
 'violations': ['식별자·신원 / 인증 — 다중인증이 일부 시스템에만 적용되거나 우회 가능',
                '비정상 인증 시도(대량·연속 실패)에 대한 자동 대응 부재',
                '성숙도 1단계(기존): 비밀번호 단일 요소 인증에 의존'],
 'defense_intro': '모든 접근을 <strong>인증된 신원 + 추가 요소</strong>로 검증하고, '
    '요청의 맥락(새 단말·새 위치·연속 실패)을 함께 보고 단계를 올려야 합니다. '
    '피싱에 견디는 방식(FIDO2 등)을 우선하세요.',
 'vuln_code': '// [취약] 비밀번호만 맞으면 세션을 준다\npublic Session login(Cred c) {\n    if (!password.verify(c.id(), c.pw()))\n        throw new AuthException("인증 실패");\n    return Session.create(c.id());\n}',
 'secure_hint': '// [안전] 2차 요소 + 위험 기반 단계 상승\npublic Session login(Cred c, RequestContext ctx) {\n    if (!password.verify(c.id(), c.pw()))\n        throw new AuthException("인증 실패");\n\n    // 1) 피싱 저항 2차 요소를 기본값으로 요구\n    if (!mfa.verify(c.id(), c.assertion(), Mfa.FIDO2))\n        throw new AuthException("2차 인증 실패");\n\n    // 2) 요청 맥락으로 위험도를 매기고, 높으면 더 강한 확인을 요구\n    int risk = riskEngine.score(ctx);        // 새 단말·새 국가·연속 실패 등\n    if (risk >= HIGH) {\n        mfa.stepUp(c.id(), ctx);\n        audit.stepUp(c.id(), risk, ctx);\n    }\n\n    // 3) 대량 대입은 계정이 아니라 출처 기준으로도 차단\n    rateLimiter.checkBySource(ctx.sourceIp(), ctx.deviceId());\n    return Session.create(c.id());\n}',
 'checks': [['mfa.verify', 'FIDO2', '2차'], ['riskEngine', 'stepUp', 'rateLimiter']],
 'success_msg': '2차 요소와 위험 기반 단계 상승으로 대입 공격이 성공해도 세션이 발급되지 않습니다.',
 'fail_msg': '2차 인증 검증과 위험도 기반 단계 상승·출처 기준 제한이 필요합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>다중인증이 <b>어디까지, 어떤 방식으로</b> 적용돼 있는지를 본다. '
    '일부 시스템만 적용되거나 SMS 하나로 끝난다면 공격자는 적용되지 않은 쪽을 고른다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 비밀번호 단일 요소, 일부 시스템만 선택적 2차 인증</li>'
    '<li><b>초기</b> — 외부 접속 경로에 2차 인증 적용, 방식은 혼재</li>'
    '<li><b>향상</b> — 내부 포함 전 경로 적용, 위험 신호에 따라 단계 상승</li>'
    '<li><b>최적화</b> — 피싱 저항 방식이 기본, 인증 결과가 실시간 정책 판단에 사용</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>시스템별 MFA 적용 현황과 예외 목록·사유·만료일</li>'
    '<li>단계 상승이 발동한 사례와 그 판단 근거</li>'
    '<li>인증 실패·차단 통계의 추이</li></ul>',
},

# ── 3. 식별자·신원 : 지속 인증 ────────────────────────────────────────
{
 'file': '16_zt-continuous-auth.html',
 'title': '한 번 통과하면 끝나는 세션의 대가',
 'icon': '⏱️', 'target': '업무 포털 세션', 'risk': '초기 → 최적화',
 'item_code': '식별자·신원 / 인증 — 지속 인증',
 'attack_panel_title': '탈취한 세션 토큰 재사용',
 'scenario_html': '제로트러스트는 "한 번 인증했으니 계속 믿는다"를 거부합니다. '
    '로그인 순간에만 검증하고 이후에는 토큰만 보는 구조에서는, '
    '<b>세션 토큰을 훔친 쪽이 곧 사용자</b>가 됩니다. '
    '위치가 바뀌든 단말이 바뀌든 서버는 아무것도 눈치채지 못합니다.',
 'attack_name': '세션 하이재킹 후 지속 사용', 'attack_sub': '다른 국가·다른 단말에서 동일 토큰 사용',
 'normal_req': 'GET /portal/docs\nCookie: sid=9f3a...c21\nUA: Windows / Chrome\nIP: 203.0.113.10 (본사)',
 'attack_req': 'GET /portal/docs\nCookie: sid=9f3a...c21   // 동일 토큰\nUA: Linux / curl        // 단말 바뀜\nIP: 198.51.100.77 (해외) // 위치 바뀜',
 'vuln_logs_js': "addLog('[SESSION] sid=9f3a...c21 검증 통과','warn'); "
                 "addLog('[SESSION] 단말 지문 변경 감지 로직 없음','error'); "
                 "addLog('[SESSION] 접속 국가 급변(본사→해외) 미판정','error'); "
                 "addLog('[APP] 문서 1,940건 연속 열람 — 재인증 요구 없음','error');",
 'breach_html': '<strong>🚨 세션 지속 악용</strong><br>최초 인증 이후 아무 검증도 하지 않아 탈취한 토큰이 만료까지 그대로 쓰였습니다.'
    '<table class="data-table"><tr><th>신호</th><th>정상</th><th>공격</th><th>서버 반응</th></tr>'
    '<tr><td>단말</td><td>Windows/Chrome</td><td>Linux/curl</td><td style="color:#b71c1c">무반응</td></tr>'
    '<tr><td>위치</td><td>본사</td><td>해외</td><td style="color:#b71c1c">무반응</td></tr>'
    '<tr><td>행위량</td><td>시간당 20건</td><td>시간당 1,940건</td><td style="color:#b71c1c">무반응</td></tr></table>',
 'violations': ['식별자·신원 / 인증 — 세션 수명 동안 신뢰를 재평가하지 않음',
                '단말 지문·위치·행위량 변화가 정책 판단에 반영되지 않음',
                '성숙도 2단계(초기): 인증은 강화했으나 인증 이후는 여전히 정적'],
 'defense_intro': '세션은 <strong>계속 의심받아야 하는 상태</strong>입니다. '
    '요청마다 맥락을 다시 평가하고, 신호가 어긋나면 세션을 끊거나 재인증을 요구하세요.',
 'vuln_code': '// [취약] 토큰이 유효하면 무조건 통과\npublic void handle(Request r) {\n    Session s = sessions.get(r.cookie("sid"));\n    if (s == null || s.expired())\n        throw new AuthException("세션 없음");\n    serve(r, s);   // 이후 아무 것도 다시 보지 않는다\n}',
 'secure_hint': '// [안전] 요청마다 신뢰를 다시 계산한다\npublic void handle(Request r) {\n    Session s = sessions.get(r.cookie("sid"));\n    if (s == null || s.expired()) throw new AuthException("세션 없음");\n\n    // 1) 세션을 만든 단말과 지금 단말이 같은지 확인\n    if (!s.deviceFingerprint().equals(r.deviceFingerprint())) {\n        sessions.revoke(s);\n        throw new AuthException("단말이 바뀐 세션");\n    }\n\n    // 2) 맥락 변화를 점수로 환산해 임계치를 넘으면 재인증\n    int risk = riskEngine.reassess(s, r);   // 위치 급변·행위량 급증 등\n    if (risk >= HIGH) {\n        sessions.revoke(s);\n        throw new ReauthRequired("맥락 변화로 재인증 필요");\n    }\n\n    // 3) 민감 자원은 수명과 무관하게 짧은 주기로 다시 확인\n    if (r.isSensitive() && s.ageSeconds() > 900)\n        throw new ReauthRequired("민감 자원 재인증");\n\n    serve(r, s);\n}',
 'checks': [['deviceFingerprint', 'revoke'], ['reassess', 'ReauthRequired', 'ageSeconds']],
 'success_msg': '단말 지문 대조와 맥락 재평가로 탈취한 세션이 즉시 끊어집니다.',
 'fail_msg': '요청마다 단말·맥락을 다시 평가하고 재인증을 요구하는 로직이 필요합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>인증을 <b>한 시점의 사건이 아니라 계속되는 과정</b>으로 다루는지를 본다. '
    '세션이 살아 있는 동안 조건이 달라졌을 때 무슨 일이 일어나는지가 핵심이다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 로그인 시점에만 검증, 세션 만료까지 무조건 신뢰</li>'
    '<li><b>초기</b> — 세션 수명을 줄이고 일부 민감 기능에만 재인증</li>'
    '<li><b>향상</b> — 단말·위치·행위 변화를 감지해 세션을 끊거나 단계를 올림</li>'
    '<li><b>최적화</b> — 요청 단위로 신뢰를 계산하고 그 근거가 로그로 설명됨</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>세션 강제 종료·재인증 발동 이력과 발동 사유</li>'
    '<li>민감 자원별 재인증 주기 정책</li>'
    '<li>단말 지문 불일치 탐지 건수</li></ul>',
},

# ── 4. 식별자·신원 : 접근 관리(최소 권한) ─────────────────────────────
{
 'file': '16_zt-least-privilege.html',
 'title': '언젠가 쓸지 몰라서 준 권한',
 'icon': '🎚️', 'target': '사내 권한 관리(IAM)', 'risk': '기존 → 최적화',
 'item_code': '식별자·신원 / 접근 관리 — 조건부·최소 권한',
 'attack_panel_title': '일반 직원 계정으로 권한 확장',
 'scenario_html': '권한은 "필요할 때 필요한 만큼"이어야 합니다. '
    '업무가 바뀔 때마다 더하기만 하고 빼지 않으면 권한은 쌓입니다(권한 적체). '
    '<b>한 계정이 털렸을 때 잃는 것의 크기</b>가 바로 이 적체의 크기입니다.',
 'attack_name': '누적 권한 악용', 'attack_sub': '부서 3회 이동하며 누적된 역할 11개',
 'normal_req': '역할 요청\n{\n  "user": "choi.mk",\n  "need": "마케팅 대시보드 조회",\n  "period": "2026-09-01 ~ 09-30"\n}',
 'attack_req': '현재 보유 권한 조회\n{\n  "user": "choi.mk",\n  "roles": [\n    "마케팅_조회", "영업_고객DB_조회",\n    "인사_급여_조회",   // 2년 전 부서\n    "결제_승인",        // 1년 전 부서\n    ... 총 11개\n  ]\n}',
 'vuln_logs_js': "addLog('[IAM] choi.mk 보유 역할 11개','warn'); "
                 "addLog('[IAM] 부서 이동 시 이전 역할 회수 절차 없음','error'); "
                 "addLog('[IAM] 유효기간 없는 영구 권한 9개','error'); "
                 "addLog('[DLP] 급여 데이터 4,200행 내려받기 — 정책상 차단 대상 아님','error');",
 'breach_html': '<strong>🚨 한 계정으로 3개 부서 데이터 접근</strong><br>권한이 쌓이기만 하고 회수되지 않아 침해 범위가 그만큼 넓어졌습니다.'
    '<table class="data-table"><tr><th>권한</th><th>부여 시점</th><th>현재 업무 관련</th><th>유효기간</th></tr>'
    '<tr><td>인사_급여_조회</td><td>2년 전</td><td style="color:#b71c1c">무관</td><td style="color:#b71c1c">없음</td></tr>'
    '<tr><td>결제_승인</td><td>1년 전</td><td style="color:#b71c1c">무관</td><td style="color:#b71c1c">없음</td></tr>'
    '<tr><td>영업_고객DB_조회</td><td>1년 전</td><td style="color:#b71c1c">무관</td><td style="color:#b71c1c">없음</td></tr></table>',
 'violations': ['식별자·신원 / 접근 관리 — 최소 권한 원칙이 부여 시점에만 적용되고 유지되지 않음',
                '권한에 유효기간과 재승인 주기가 없음',
                '성숙도 1단계(기존): 역할이 정적이고 회수는 수동'],
 'defense_intro': '권한은 <strong>기본이 없음(deny)</strong>이고, 필요할 때 <strong>기간을 정해</strong> 부여했다가 '
    '자동으로 사라져야 합니다. 요청 시점의 맥락(기기 상태·위치·업무)까지 조건으로 넣으세요.',
 'vuln_code': '// [취약] 한 번 준 역할은 계속 남는다\npublic boolean can(User u, String action) {\n    return u.roles().stream()\n            .anyMatch(r -> r.allows(action));   // 유효기간·조건 없음\n}',
 'secure_hint': '// [안전] 기간이 정해진 권한 + 요청 맥락 조건\npublic boolean can(User u, String action, RequestContext ctx) {\n    // 1) 기본은 거부. 명시적으로 허용된 것만 통과시킨다\n    Grant g = grants.findActive(u.getId(), action);\n    if (g == null) { audit.deny(u, action, "부여된 권한 없음"); return false; }\n\n    // 2) 유효기간이 지난 권한은 스스로 사라진다\n    if (g.expiresAt().isBefore(now())) {\n        grants.revoke(g);\n        audit.deny(u, action, "권한 유효기간 만료");\n        return false;\n    }\n\n    // 3) 조건부 접근: 기기 상태·위치 등 맥락이 정책을 만족해야 한다\n    if (!policy.conditionsMet(g, ctx)) {\n        audit.deny(u, action, "접근 조건 불충족");\n        return false;\n    }\n\n    // 4) 고위험 작업은 승인받은 시간 창에서만\n    if (policy.isHighRisk(action) && !g.withinApprovedWindow(now()))\n        return false;\n\n    audit.allow(u, action, g);\n    return true;\n}',
 'checks': [['findActive', 'expiresAt', 'revoke'], ['conditionsMet', 'isHighRisk', 'audit']],
 'success_msg': '기간이 정해진 권한과 조건부 접근으로 누적 권한 악용이 차단됩니다.',
 'fail_msg': '기본 거부·유효기간 만료·접근 조건 검증을 모두 갖춰야 합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>권한이 <b>업무에 맞게 줄어드는 구조인지</b>를 본다. '
    '부여 절차만 있고 회수 절차가 없으면 최소 권한은 문서에만 존재한다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 역할이 정적이고 회수는 담당자 기억에 의존</li>'
    '<li><b>초기</b> — 정기 권한 재검토(반기·연)를 수행</li>'
    '<li><b>향상</b> — 유효기간이 붙은 권한, 조건부 접근 정책 적용</li>'
    '<li><b>최적화</b> — 요청 시점에 필요한 만큼만 임시 부여하고 자동 회수</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>권한별 유효기간·재승인 주기 설정값</li>'
    '<li>부서 이동 건 대비 권한 회수 완료율</li>'
    '<li>거부된 접근 요청과 그 사유 로그</li></ul>',
},

# ── 5. 기기 및 엔드포인트 : 정책 준수 ─────────────────────────────────
{
 'file': '16_zt-device-compliance.html',
 'title': '어떤 기기인지 묻지 않는 접속',
 'icon': '💻', 'target': '사내 자원 접근 게이트웨이', 'risk': '기존 → 향상',
 'item_code': '기기·엔드포인트 / 정책 준수 모니터링',
 'attack_panel_title': '비관리 개인 PC에서 접속',
 'scenario_html': '제로트러스트는 사용자만이 아니라 <b>기기도 검증 대상</b>으로 봅니다. '
    '아이디·비밀번호가 맞아도 그 기기가 조직이 아는 기기인지, '
    '보안 설정이 살아 있는지 확인하지 않으면 감염된 개인 PC가 그대로 사내 자원에 붙습니다.',
 'attack_name': '비관리 단말 접속', 'attack_sub': '자산 미등록 · 백신 미동작 · 디스크 미암호화',
 'normal_req': '접속 요청\n{\n  "user": "jung.ops",\n  "device_id": "AST-11902",   // 자산 등록됨\n  "posture": {\n    "edr": "running",\n    "disk_encrypted": true,\n    "patch_age_days": 3\n  }\n}',
 'attack_req': '접속 요청\n{\n  "user": "jung.ops",\n  "device_id": null,          // 자산 미등록\n  "posture": null             // 게이트웨이가 요구하지 않음\n}',
 'vuln_logs_js': "addLog('[GW] 사용자 인증 성공 — 기기 검증 항목 없음','warn'); "
                 "addLog('[GW] device_id 미제출 → 그대로 통과','error'); "
                 "addLog('[EDR] 해당 단말 에이전트 없음(비관리)','error'); "
                 "addLog('[FILE] 설계도면 공유 폴더 마운트 성공','error');",
 'breach_html': '<strong>🚨 비관리 단말이 사내 자원에 연결</strong><br>사용자만 확인하고 기기는 묻지 않아 통제 밖 단말이 그대로 들어왔습니다.'
    '<table class="data-table"><tr><th>검증 항목</th><th>정책 기준</th><th>접속 단말</th></tr>'
    '<tr><td>자산 등록</td><td>필수</td><td style="color:#b71c1c">미등록</td></tr>'
    '<tr><td>EDR 동작</td><td>필수</td><td style="color:#b71c1c">없음</td></tr>'
    '<tr><td>디스크 암호화</td><td>필수</td><td style="color:#b71c1c">해제</td></tr>'
    '<tr><td>패치 경과일</td><td>14일 이내</td><td style="color:#b71c1c">417일</td></tr></table>',
 'violations': ['기기·엔드포인트 / 정책 준수 모니터링 — 접근 판단에 기기 상태가 반영되지 않음',
                '자산 인벤토리에 없는 단말의 접속이 허용됨',
                '성숙도 1단계(기존): 기기 검증 없이 사용자 인증만 수행'],
 'defense_intro': '접근 결정은 <strong>사용자 신원 × 기기 상태</strong>로 내려야 합니다. '
    '기기가 등록돼 있고 보안 설정이 살아 있는지 접속 시점에 확인하고, 기준 미달이면 '
    '차단하거나 제한된 범위만 허용하세요.',
 'vuln_code': '// [취약] 사용자만 보고 자원을 열어준다\npublic Access authorize(User u, Resource r) {\n    if (!auth.isValid(u)) deny();\n    return Access.full(r);   // 어떤 기기인지 묻지 않음\n}',
 'secure_hint': '// [안전] 기기 상태를 접근 결정에 포함\npublic Access authorize(User u, Device d, Resource r) {\n    if (!auth.isValid(u)) deny();\n\n    // 1) 조직이 아는 기기인지 확인(자산 인벤토리 대조)\n    if (d == null || !inventory.isRegistered(d.getId()))\n        return Access.denied("미등록 단말");\n\n    // 2) 접속 시점의 보안 상태를 실시간으로 검사\n    Posture p = postureService.check(d);      // EDR·암호화·패치·화면잠금\n    if (!p.meets(policy.baselineFor(r)))\n        return Access.denied("기기 보안 기준 미달: " + p.failedItems());\n\n    // 3) 기준에 조금 못 미치면 전부 막지 말고 범위를 줄인다\n    if (p.isDegraded())\n        return Access.limited(r, "읽기 전용 · 내려받기 금지");\n\n    return Access.full(r);\n}',
 'checks': [['isRegistered', 'inventory'], ['postureService', 'meets', 'limited']],
 'success_msg': '자산 등록 확인과 실시간 상태 검사로 비관리 단말이 차단됩니다.',
 'fail_msg': '기기 등록 여부와 접속 시점 보안 상태 검사를 접근 결정에 넣어야 합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>접근을 허용할 때 <b>기기의 현재 상태를 실제로 확인하는지</b>를 본다. '
    '등록 여부만 보고 상태를 보지 않으면 감염된 등록 단말을 막지 못한다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 기기 검증 없음, 사용자 인증만으로 접근 허용</li>'
    '<li><b>초기</b> — 자산 등록 여부만 확인(상태는 확인하지 않음)</li>'
    '<li><b>향상</b> — 접속 시점 보안 상태를 검사해 허용·제한·차단을 나눔</li>'
    '<li><b>최적화</b> — 상태 변화가 세션 중에도 반영돼 접근 범위가 즉시 조정됨</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>기기 상태 검사 항목 정의와 자원별 기준선</li>'
    '<li>기준 미달로 차단·제한된 접속 통계</li>'
    '<li>자산 인벤토리와 실제 접속 단말의 차이 분석</li></ul>',
},

# ── 6. 네트워크 : 마이크로 세그멘테이션 ───────────────────────────────
{
 'file': '16_zt-microseg.html',
 'title': '평평한 내부망에서의 횡적 이동',
 'icon': '🕸️', 'target': '사내 서버 네트워크', 'risk': '기존 → 최적화',
 'item_code': '네트워크 / 네트워크 세분화',
 'attack_panel_title': '침해된 단말에서 내부 확산',
 'scenario_html': '경계만 지키는 망은 <b>한 대만 뚫리면 전부 뚫린 것</b>과 같습니다. '
    '내부에 들어온 트래픽을 아무도 검사하지 않으면, 감염된 업무용 PC 한 대가 '
    '결제 서버·인사 DB·백업 저장소로 차례차례 옮겨 다닙니다. '
    '세분화는 "못 들어오게"가 아니라 "들어와도 못 퍼지게"를 위한 통제입니다.',
 'attack_name': '내부 횡적 이동(lateral movement)', 'attack_sub': '업무 PC → 파일서버 → 결제 서버 → 백업',
 'normal_req': '업무 PC → 그룹웨어(443)\n  허용: 업무 목적 통신',
 'attack_req': '업무 PC → 파일서버(445)      허용\n업무 PC → 결제서버(3389)     허용\n업무 PC → 백업 스토리지(22)  허용\n  ※ 내부 구간 정책 없음(any→any)',
 'vuln_logs_js': "addLog('[NET] 내부 구간 ACL: any → any','warn'); "
                 "addLog('[HOST] 업무 PC → 파일서버 SMB 접속 성공','error'); "
                 "addLog('[HOST] 파일서버 자격증명 재사용 → 결제서버 RDP 성공','error'); "
                 "addLog('[HOST] 백업 스토리지 SSH 접속 → 스냅샷 삭제','error');",
 'breach_html': '<strong>🚨 4홉 만에 백업까지 도달</strong><br>내부 통신을 제한하지 않아 한 대의 침해가 전체 침해가 되었습니다.'
    '<table class="data-table"><tr><th>단계</th><th>출발</th><th>도착</th><th>차단</th></tr>'
    '<tr><td>1</td><td>업무 PC</td><td>파일서버</td><td style="color:#b71c1c">없음</td></tr>'
    '<tr><td>2</td><td>파일서버</td><td>결제서버</td><td style="color:#b71c1c">없음</td></tr>'
    '<tr><td>3</td><td>결제서버</td><td>백업 스토리지</td><td style="color:#b71c1c">없음</td></tr></table>',
 'violations': ['네트워크 / 네트워크 세분화 — 내부 구간이 사실상 단일 신뢰 영역',
                '워크로드 단위 통신 정책(마이크로 세그멘테이션) 부재',
                '성숙도 1단계(기존): 경계 방화벽 위주, 내부는 검사하지 않음'],
 'defense_intro': '내부 통신도 <strong>기본 거부</strong>로 두고, 실제로 필요한 '
    '<strong>출발지→목적지→포트→목적</strong> 조합만 여세요. '
    '먼저 흐름을 관찰해 목록을 만들고(가시성), 그다음 좁히는 순서가 안전합니다.',
 'vuln_code': '// [취약] 내부는 전부 신뢰 — 목적지만 보고 통과\nboolean allow(Flow f) {\n    if (f.dst().isInternal()) return true;   // 내부면 무조건 허용\n    return perimeter.check(f);\n}',
 'secure_hint': '// [안전] 워크로드 단위 기본 거부 + 필요한 흐름만 허용\nboolean allow(Flow f) {\n    // 1) 내부라는 이유만으로 통과시키지 않는다\n    WorkloadId src = identity.of(f.src());\n    WorkloadId dst = identity.of(f.dst());\n    if (src == null || dst == null) return deny(f, "식별되지 않은 워크로드");\n\n    // 2) 허용 목록에 정확히 일치하는 흐름만 통과\n    FlowPolicy p = policies.find(src, dst, f.port());\n    if (p == null) return deny(f, "허용되지 않은 내부 흐름");\n\n    // 3) 관리 포트(SMB/RDP/SSH)는 승인된 경로에서만\n    if (p.isAdminPort() && !jumpHost.isApproved(f.src()))\n        return deny(f, "관리 포트는 승인된 경유 지점에서만");\n\n    // 4) 차단뿐 아니라 허용한 흐름도 기록해 정책을 계속 좁힌다\n    telemetry.record(f, p);\n    return true;\n}',
 'checks': [['policies.find', 'deny', '허용되지'], ['isAdminPort', 'jumpHost', 'telemetry']],
 'success_msg': '워크로드 단위 기본 거부 정책으로 횡적 이동이 1홉에서 멈춥니다.',
 'fail_msg': '내부 흐름도 기본 거부하고 허용 목록·관리 포트 제한을 적용해야 합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>침해가 일어난 뒤 <b>피해가 어디까지 번지는가</b>를 결정하는 항목이다. '
    '경계 방화벽의 두께가 아니라 내부 구간의 촘촘함이 기준이 된다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 경계 방화벽 중심, 내부는 사실상 any→any</li>'
    '<li><b>초기</b> — 업무·부서 단위 대분할(매크로 세그멘테이션)</li>'
    '<li><b>향상</b> — 워크로드 단위 정책, 관리 포트는 경유 지점 강제</li>'
    '<li><b>최적화</b> — 흐름 가시성 기반으로 정책이 자동 제안·조정됨</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>구간별 정책 수와 any 규칙 잔존 건수</li>'
    '<li>허용된 내부 흐름 목록과 각 흐름의 업무 목적</li>'
    '<li>차단 로그 기반 미승인 통신 시도 추이</li></ul>',
},

# ── 7. 시스템 : PAM / 특권 계정 ───────────────────────────────────────
{
 'file': '16_zt-pam.html',
 'title': '모두가 아는 root 비밀번호',
 'icon': '🗝️', 'target': '운영 서버 관리 접근', 'risk': '기존 → 향상',
 'item_code': '시스템 / 접근통제 — 시스템 계정·자격 증명 관리',
 'attack_panel_title': '공용 관리자 계정 사용',
 'scenario_html': '특권 계정은 조직에서 가장 위험한 자산입니다. '
    '<b>공용 계정을 여러 명이 나눠 쓰면</b> 누가 무엇을 했는지 추적할 수 없고, '
    '한 사람이 퇴사해도 비밀번호는 계속 밖을 돌아다닙니다. '
    '제로트러스트에서는 특권 접근도 "그때그때 승인받아 잠깐"이어야 합니다.',
 'attack_name': '공용 특권 계정 오·남용', 'attack_sub': '인프라팀 4명이 root 비밀번호 공유',
 'normal_req': 'ssh admin_kim@prod-db-01\n  → 개인 계정, sudo 로 권한 상승, 명령 기록 남음',
 'attack_req': 'ssh root@prod-db-01\n  비밀번호: (4명이 공유, 최근 변경 2년 전)\n  → 누가 접속했는지 구분 불가',
 'vuln_logs_js': "addLog('[SSH] root 직접 로그인 허용','error'); "
                 "addLog('[AUTH] 공용 비밀번호 — 최종 변경일 2024-08-11','warn'); "
                 "addLog('[AUDIT] 세션 주체 식별 불가(root)','error'); "
                 "addLog('[DB] 고객 테이블 덤프 실행 — 책임 추적 불가','error');",
 'breach_html': '<strong>🚨 책임 추적이 불가능한 특권 세션</strong><br>공용 계정이라 감사 로그에 남은 주체가 사람이 아니라 계정 이름뿐입니다.'
    '<table class="data-table"><tr><th>항목</th><th>있어야 할 상태</th><th>현재</th></tr>'
    '<tr><td>접속 주체</td><td>개인 식별</td><td style="color:#b71c1c">root(공용)</td></tr>'
    '<tr><td>권한 획득</td><td>요청·승인 후 한시 부여</td><td style="color:#b71c1c">상시 보유</td></tr>'
    '<tr><td>세션 기록</td><td>명령·화면 기록</td><td style="color:#b71c1c">없음</td></tr></table>',
 'violations': ['시스템 / 접근통제 — 특권 계정이 개인에 귀속되지 않고 공용으로 운영',
                '특권 접근에 요청·승인·한시 부여 절차 부재',
                '성숙도 1단계(기존): 관리 계정을 수동 관리하고 세션을 기록하지 않음'],
 'defense_intro': '특권 접근은 <strong>개인 식별 → 요청·승인 → 한시 부여 → 세션 기록 → 자동 회수</strong> '
    '순서로 만들어야 합니다. 비밀번호는 사람이 알지 못하게 금고가 대신 주입하게 하세요.',
 'vuln_code': '// [취약] 공용 계정으로 바로 붙는다\npublic Session connect(String host) {\n    return ssh.connect(host, "root", sharedPassword);\n}',
 'secure_hint': '// [안전] 요청·승인 기반 한시 특권 + 세션 기록\npublic Session connect(String host, User who, String reason) {\n    // 1) 누가 왜 필요한지 남기고 승인받는다\n    ElevationRequest req = pam.request(who, host, reason);\n    if (!pam.approved(req)) throw new AccessDenied("특권 접근 미승인");\n\n    // 2) 비밀번호는 사람에게 주지 않고 금고가 주입한다(주기적 자동 교체)\n    Credential c = vault.checkout(host, req.getTtl());\n\n    // 3) 세션을 개인에게 귀속시키고 명령을 기록한다\n    Session s = ssh.connectAs(host, c, who.getId());\n    recorder.attach(s, who, req);\n\n    // 4) 사용 시간이 끝나면 자격 증명을 회수하고 즉시 교체한다\n    scheduler.after(req.getTtl(), () -> {\n        vault.checkin(c);\n        vault.rotate(host);\n        s.close();\n    });\n    return s;\n}',
 'checks': [['pam.request', 'approved', '승인'], ['vault', 'recorder', 'rotate']],
 'success_msg': '한시 특권 부여와 금고 기반 자격 증명으로 공용 계정 문제가 사라집니다.',
 'fail_msg': '요청·승인, 금고 주입, 세션 기록, 자동 회수가 모두 필요합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4>특권 접근이 <b>누구에게, 언제까지, 무엇을 위해</b> 열렸는지 '
    '설명할 수 있는지를 본다. 설명할 수 없으면 사고가 나도 원인을 좁힐 수 없다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 공용 관리 계정, 비밀번호 공유, 세션 기록 없음</li>'
    '<li><b>초기</b> — 개인 계정 + sudo, 비밀번호 주기 변경</li>'
    '<li><b>향상</b> — 금고 기반 자격 증명, 요청·승인 후 한시 부여, 세션 기록</li>'
    '<li><b>최적화</b> — 상시 특권 0을 목표로 하고 이상 명령을 실시간 차단</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>상시 특권 계정 수의 감소 추이</li>'
    '<li>특권 요청·승인 이력과 평균 보유 시간</li>'
    '<li>자격 증명 자동 교체 주기와 실패 건수</li></ul>',
},

# ── 8. 데이터 : 분류·라벨링·DLP ───────────────────────────────────────
{
 'file': '16_zt-data-dlp.html',
 'title': '무엇이 중요한지 모르는 채 지키는 데이터',
 'icon': '🏷️', 'target': '사내 문서·데이터 저장소', 'risk': '기존 → 최적화',
 'item_code': '데이터 / 데이터 분류 · 손실 방지',
 'attack_panel_title': '대량 반출 시도',
 'scenario_html': '데이터 통제는 <b>분류에서 시작</b>합니다. '
    '어떤 문서가 중요한지 표시돼 있지 않으면 보호 정책을 걸 대상 자체를 고를 수 없고, '
    '탐지 규칙은 "이름에 기밀이 들어간 파일"처럼 허술해집니다. '
    '결과적으로 반출은 평범한 업무 활동과 구분되지 않습니다.',
 'attack_name': '분류되지 않은 민감 데이터 반출', 'attack_sub': '개인 클라우드로 12,400건 업로드',
 'normal_req': '문서 열람\n{\n  "file": "2026_마케팅_계획.pptx",\n  "label": "내부용",\n  "action": "read"\n}',
 'attack_req': '대량 반출\n{\n  "files": 12400,\n  "label": null,              // 분류 안 됨\n  "contains": "주민등록번호, 계좌번호",\n  "dest": "personal-cloud.example"\n}',
 'vuln_logs_js': "addLog('[STORE] 문서 12,400건 접근 — 라벨 없음','warn'); "
                 "addLog('[DLP] 탐지 규칙: 파일명에 기밀 포함 → 해당 없음','error'); "
                 "addLog('[NET] 외부 스토리지 업로드 4.2GB 허용','error'); "
                 "addLog('[AUDIT] 무엇이 나갔는지 사후 식별 불가','error');",
 'breach_html': '<strong>🚨 무엇이 유출됐는지 모르는 유출</strong><br>분류가 없으니 탐지도, 사후 영향 분석도 불가능했습니다.'
    '<table class="data-table"><tr><th>항목</th><th>필요</th><th>현재</th></tr>'
    '<tr><td>데이터 분류</td><td>등급·라벨 부여</td><td style="color:#b71c1c">미분류 87%</td></tr>'
    '<tr><td>탐지 기준</td><td>내용 기반</td><td style="color:#b71c1c">파일명 기반</td></tr>'
    '<tr><td>반출 통제</td><td>등급별 차등</td><td style="color:#b71c1c">일괄 허용</td></tr></table>',
 'violations': ['데이터 / 데이터 분류 — 데이터 목록과 등급 체계가 없어 보호 대상 선정 불가',
                '데이터 손실 방지(DLP) 규칙이 내용이 아닌 이름에 의존',
                '성숙도 1단계(기존): 데이터 위치·민감도를 수작업으로 파악'],
 'defense_intro': '먼저 <strong>어디에 무엇이 있는지 목록을 만들고 등급을 붙인 다음</strong>, '
    '등급에 따라 열람·복사·반출을 다르게 통제하세요. 탐지는 파일명이 아니라 내용과 라벨을 기준으로 합니다.',
 'vuln_code': '// [취약] 이름으로 중요도를 짐작한다\nboolean canExport(File f, User u) {\n    if (f.getName().contains("기밀")) return false;\n    return true;   // 나머지는 전부 허용\n}',
 'secure_hint': '// [안전] 분류 → 등급별 통제 → 내용 기반 탐지\nboolean canExport(File f, User u, Destination d) {\n    // 1) 라벨이 없으면 먼저 분류한다(미분류를 기본 허용으로 두지 않는다)\n    Label lb = f.label() != null ? f.label() : classifier.inspect(f);\n    if (lb == null) return deny(f, "분류되지 않은 데이터는 반출 불가");\n\n    // 2) 등급별로 허용 목적지를 다르게 둔다\n    if (!policy.allowedDestinations(lb).contains(d.kind()))\n        return deny(f, lb + " 등급은 해당 목적지로 반출 불가");\n\n    // 3) 내용 기반 탐지: 라벨이 낮아도 실제 내용이 민감하면 막는다\n    Findings fd = contentScanner.scan(f);   // 주민등록번호·계좌번호 등\n    if (fd.hasSensitive()) return deny(f, "민감정보 포함: " + fd.summary());\n\n    // 4) 대량 반출은 양 자체를 신호로 본다\n    if (usage.exportedCountLastHour(u) > policy.bulkThreshold())\n        return deny(f, "대량 반출 임계 초과");\n\n    audit.export(u, f, lb, d);\n    return true;\n}',
 'checks': [['classifier', 'label', '분류'], ['contentScanner', 'bulkThreshold', 'allowedDestinations']],
 'success_msg': '분류·등급별 통제·내용 기반 탐지로 미분류 대량 반출이 차단됩니다.',
 'fail_msg': '데이터 분류, 등급별 목적지 제한, 내용 기반 탐지, 대량 반출 임계가 필요합니다.',
 'kisa_ref': '<h4>1. 무엇을 보는 항목인가</h4><b>보호할 대상을 조직이 알고 있는지</b>를 본다. '
    '분류가 없으면 그 뒤의 암호화·접근제어·탐지 규칙이 모두 근거 없이 세워진다.'
    '<h4>2. 성숙도 단계별 모습</h4><ul>'
    '<li><b>기존</b> — 데이터 목록·등급 없음, 담당자 경험에 의존</li>'
    '<li><b>초기</b> — 주요 시스템만 수동 분류, 일부 DLP 규칙 운영</li>'
    '<li><b>향상</b> — 자동 분류·라벨링, 등급별 접근·반출 정책 적용</li>'
    '<li><b>최적화</b> — 생성 시점에 라벨이 붙고 라벨이 데이터를 따라 이동함</li></ul>'
    '<h4>3. 무엇을 증적으로 남길 수 있나</h4><ul>'
    '<li>저장소별 분류 완료율과 미분류 데이터 추이</li>'
    '<li>등급별 접근·반출 정책 정의서</li>'
    '<li>DLP 탐지·차단 건수와 오탐 조정 이력</li></ul>',
},

]
