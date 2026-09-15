# -*- coding: utf-8 -*-
"""KISA 49 보안약점 '현업 진단' 시나리오 — part 2 (보안기능, 17종).

구성 규칙은 specs_code_lab.py 헤더 참조.
이 묶음은 오탐·추가확인 비중을 의도적으로 높였다. 암호화·인증 항목은 스캐너가
패턴만 보고 올리는 오탐이 특히 많은 영역이고, 그것을 걸러내는 것이 진단원의 일이다.
"""
from specs_code_lab import S, T, E, V, F, O

SCENARIOS = dict([

# ───────────────────────────── 적절한 인증 없는 중요기능 허용 ─────────────────────────────
S('missing_auth',
  T('내부 감사 지적', 'AUD-2026-22', '긴급', 'high',
    '감사에서 "고객 상세정보 조회 API 가 인증 없이 호출된다"는 지적이 나왔습니다.\n'
    '개발팀 회신: "그 API 는 내부 화면에서만 호출하고, 화면 진입 시 로그인을 검사합니다."'),
  [
   E('💻', '직접 호출 시도', '점검 서버',
     '$ curl -s https://app/api/customer/detail?id=10024 | jq .\n'
     '{\n'
     '  "name": "홍**", "phone": "010-1234-5678",\n'
     '  "addr": "서울시 ...", "card_bin": "451234", "birth": "1988-04-17"\n'
     '}\n'
     '>> 쿠키·토큰 없이 200 OK — 개인정보 반환'),
   E('🔍', '인증 설정', 'SecurityConfig.java',
     '$ sed -n \'31,37p\' src/main/java/config/SecurityConfig.java\n'
     '  .authorizeHttpRequests(a -> a\n'
     '      .requestMatchers("/api/**").permitAll()      // <== API 전체 개방\n'
     '      .requestMatchers("/admin/**").hasRole("ADMIN")\n'
     '      .anyRequest().authenticated())\n'
     '\n'
     '>> 화면(anyRequest)은 인증하지만 /api/** 는 예외 처리돼 있음'),
   E('🌐', 'API 호출 통계', 'API 게이트웨이',
     '$ ./apigw-stats.sh --path /api/customer/detail --days 30\n'
     '총 호출 1,284,110건\n'
     '  인증 헤더 있음: 1,283,904\n'
     '  인증 헤더 없음:       206   (출처 IP 4개, 모두 해외)\n'
     '  순차 id 열거 패턴:    198   (id=10001~10199)'),
  ],
  V('true',
    '인증 없이 개인정보가 반환되며, 실제로 순차 ID 열거 흔적 198건이 확인됩니다. '
    '"화면에서 로그인을 검사한다"는 방어는 화면을 거치지 않는 직접 호출 앞에서 무의미합니다. '
    '정탐이며 개인정보 유출이 이미 진행됐을 가능성이 높아 침해대응 검토가 필요합니다.',
    '화면 단의 인증과 API 단의 인증은 별개입니다. "우리 화면만 호출한다"는 전제는 공격자가 지키지 않습니다.'),
  F(
   O('API 를 내부망에서만 호출 가능하도록 방화벽으로 막는다', False,
     '$ curl -s https://app/api/customer/detail?id=10024   # 내부망 단말에서\n'
     '{"name":"홍**","phone":"010-1234-5678", ...}\n'
     '>> 내부망 사용자·침해 단말에는 여전히 무인증 개방',
     '망 통제는 외부만 막습니다. 내부자와 침해된 단말에는 아무 장애물이 아니며, 개인정보는 내부에서도 인가된 사람만 봐야 합니다.'),
   O('인증을 기본값으로 두고 공개 엔드포인트만 예외로 등록한다', True,
     '$ curl -s -o /dev/null -w "%{http_code}" https://app/api/customer/detail?id=10024\n'
     '401\n'
     '$ curl -s -H "Authorization: Bearer <일반사용자>" https://app/api/customer/detail?id=10024\n'
     '403   (본인 정보가 아님 — 인가 검사까지 통과해야 함)\n'
     '\n'
     '.requestMatchers("/api/health","/api/version").permitAll()\n'
     '.anyRequest().authenticated()     // 기본값 = 인증 필요',
     '"기본 거부, 예외만 허용" 순서가 핵심입니다. 반대로 하면 새 엔드포인트가 추가될 때마다 조용히 열린 채 배포됩니다.'),
   O('id 값을 순차 정수 대신 UUID 로 바꾼다', False,
     '$ curl -s https://app/api/customer/detail?id=9a2c41e8-...\n'
     '{"name":"홍**", ...}\n'
     '>> 여전히 무인증. 열거만 어려워졌을 뿐',
     '식별자를 추측하기 어렵게 만드는 것은 열거를 늦출 뿐입니다. 인증 부재라는 원인은 그대로입니다.'))),

# ───────────────────────────── 부적절한 인가 ─────────────────────────────
S('inappropriate_auth',
  T('고객 문의(VOC)', 'VOC-7899', '긴급', 'high',
    '"주문 상세 페이지에서 새로고침했더니 다른 사람 주문 내역이 보였다"는 문의가 접수됐습니다.\n'
    '고객이 캡처를 보냈고, 실제로 타인의 이름·주소·연락처가 담겨 있습니다.'),
  [
   E('💻', '재현', '점검 서버',
     '$ curl -s -b "SESSION=<kim 로그인>" https://app/order/88213 | jq .buyer\n'
     '{"name":"이**","phone":"010-9876-5432","addr":"부산시 ..."}\n'
     '$ curl -s -b "SESSION=<kim 로그인>" https://app/order/88214 | jq .buyer\n'
     '{"name":"박**","phone":"010-5555-1111","addr":"대전시 ..."}\n'
     '>> 로그인은 했지만 남의 주문번호로 조회됨'),
   E('🔍', '조회 코드', 'OrderController.java',
     '$ sed -n \'44,49p\' src/main/java/order/OrderController.java\n'
     '  @GetMapping("/order/{orderId}")\n'
     '  public Order get(@PathVariable Long orderId, HttpSession session) {\n'
     '      if (session.getAttribute("userId") == null) return null;   // 인증만 확인\n'
     '      return orderRepository.findById(orderId).orElseThrow();    // 소유 확인 없음\n'
     '  }'),
   E('📊', '접근 이력 분석', 'audit log',
     '$ ./audit-scan.sh --pattern cross-owner --days 7\n'
     '교차 접근 의심 1,942건 (계정 17개)\n'
     '  최다: user_id=park  →  3,118개 주문 순차 조회 (2026-09-10 02:11~04:40)\n'
     '  조회 성공률 100%'),
  ],
  V('true',
    '인증은 있지만 인가가 없습니다. 로그인한 사용자가 남의 주문번호를 넣으면 그대로 조회됩니다. '
    '한 계정이 3,118건을 순차 조회한 이력까지 확인됩니다. 정탐이며 대량 개인정보 유출 사고입니다.',
    '인증(누구인가)과 인가(무엇을 할 수 있는가)를 혼동하면 이 결함을 놓칩니다. 로그인 검사가 있다고 인가가 있는 것이 아닙니다.'),
  F(
   O('주문번호를 추측하기 어려운 난수로 바꾼다', False,
     '$ curl -s -b "SESSION=<kim>" https://app/order/8f2a41e89c2b\n'
     '{"buyer":{"name":"이**", ...}}\n'
     '>> 주문번호를 알기만 하면 여전히 조회 가능 (공유 링크·영수증·로그에서 노출)',
     '식별자를 감추는 것은 인가가 아닙니다. 주문번호는 영수증·알림·고객센터 등 여러 경로로 새어 나갑니다.'),
   O('조회 시 세션의 사용자와 주문 소유자가 같은지 서버에서 확인한다', True,
     '$ curl -s -o /dev/null -w "%{http_code}" -b "SESSION=<kim>" https://app/order/88213\n'
     '403\n'
     '$ curl -s -b "SESSION=<kim>" https://app/order/88999 | jq .buyer.name\n'
     '"김**"    (본인 주문만 조회됨)\n'
     '\n'
     'Order o = orderRepository.findById(orderId).orElseThrow();\n'
     'if (!o.getUserId().equals(session.getAttribute("userId"))) throw new ForbiddenException();',
     '모든 조회·수정 시점에 "이 자원이 이 사용자의 것인가"를 서버가 확인해야 합니다. 목록 조회도 소유자 조건으로 걸러야 합니다.'),
   O('프런트엔드에서 본인 주문 목록에 있는 번호만 링크로 노출한다', False,
     '$ curl -s -b "SESSION=<kim>" https://app/order/88213\n'
     '{"buyer":{"name":"이**", ...}}\n'
     '>> URL 을 직접 입력하면 그대로 조회됨',
     '화면에서 링크를 감추는 것은 통제가 아닙니다. 서버는 여전히 누구에게나 응답합니다.'))),

# ───────────────────────────── 반복된 인증시도 제한 부재 ─────────────────────────────
S('improper_auth_attempts',
  T('보안 관제 경보', 'SOC-4412', '높음', 'high',
    '심야에 로그인 실패 이벤트가 평소의 400배로 급증했다는 경보입니다.\n'
    '성공 로그인도 평소보다 늘었습니다.'),
  [
   E('🚨', '로그인 시도 통계', 'auth.log',
     '$ ./auth-stat.sh --window "2026-09-12 01:00~05:00"\n'
     '실패 1,284,110건 / 성공 412건\n'
     '출발지 IP 2,184개 (봇넷 추정, 국가 41개)\n'
     '대상 계정 8,842개 · 계정당 평균 시도 145회\n'
     '\n'
     '>> 계정 8,842개 중 412개가 결국 로그인 성공 (크리덴셜 스터핑)'),
   E('🔍', '로그인 처리 코드', 'LoginService.java',
     '$ sed -n \'22,29p\' src/main/java/auth/LoginService.java\n'
     '  public boolean login(String id, String pw) {\n'
     '      Member m = repo.findById(id);\n'
     '      if (m == null) return false;\n'
     '      return passwordEncoder.matches(pw, m.getPwHash());\n'
     '  }\n'
     '  // 실패 횟수 기록·잠금·지연 없음'),
   E('🧱', '앞단 통제 확인', 'WAF / 게이트웨이',
     '$ ./gw-policy.sh --path /login\n'
     'rate-limit: 없음\n'
     'captcha:    없음\n'
     'ip-reputation: 없음\n'
     '$ grep -c "429" /var/log/nginx/access.log\n'
     '0'),
  ],
  V('true',
    '시도 횟수 제한이 코드에도 앞단에도 전혀 없습니다. 128만 건의 시도로 412개 계정이 실제로 탈취됐습니다. '
    '정탐이며 진행 중인 사고입니다. 취약점 보고와 동시에 침해대응(계정 잠금·비밀번호 강제 변경·통지)이 필요합니다.',
    '단순 무차별 대입이 아니라 크리덴셜 스터핑입니다. 계정당 145회라 계정 단위 잠금만으로는 탐지 임계에 걸리지 않을 수 있어, IP·디바이스·전체 실패율까지 함께 봐야 합니다.'),
  F(
   O('실패 5회 시 해당 계정을 30분 잠근다', False,
     '$ ./replay-attack.sh --mode stuffing\n'
     '계정당 시도 4회로 조절 — 잠금 미발동\n'
     '성공 388건\n'
     '>> 계정 잠금만 있으면 공격자가 임계 아래로 속도를 맞춤.\n'
     '   또한 공격자가 일부러 잠가 정상 사용자를 막는 서비스 거부도 가능',
     '계정 단위 잠금은 필요하지만 단독으로는 부족하고, 오히려 계정 잠금 공격에 악용됩니다.'),
   O('계정·IP·디바이스 다층 제한 + 점증 지연 + 위험 기반 추가 인증', True,
     '$ ./replay-attack.sh --mode stuffing\n'
     'IP당 10회 초과 → 429 Too Many Requests\n'
     '전체 실패율 임계 초과 → 전역 CAPTCHA 발동\n'
     '새 디바이스 + 해외 IP → 추가 인증(OTP) 요구\n'
     '성공 0건 / 정상 사용자 영향 0건\n'
     '$ tail -1 /var/log/app/auth-anomaly.log\n'
     '[02:14] STUFFING_DETECTED ips=2184 accounts=8842 → 자동 차단',
     '여러 축(계정·IP·디바이스·전체 실패율)을 함께 봐야 분산 공격이 잡힙니다. 정상 사용자를 막지 않으려면 위험도에 따라 단계적으로 강화하는 편이 낫습니다.'),
   O('비밀번호 복잡도 규칙을 강화한다', False,
     '$ ./replay-attack.sh --mode stuffing\n'
     '성공 402건\n'
     '>> 탈취된 자격증명을 그대로 넣는 공격이라 복잡도와 무관',
     '크리덴셜 스터핑은 이미 유효한 비밀번호를 재사용합니다. 복잡도 규칙은 추측 공격에만 유효합니다.'))),

# ───────────────────────────── 취약한 비밀번호 허용 ─────────────────────────────
S('weakpassword',
  T('SAST 스캐너 리포트', 'SONAR-3512', '중간', 'mid',
    '회원가입 비밀번호 검증 로직이 약하다는 지적입니다.\n'
    '기획팀 회신: "가입 이탈률 때문에 규칙을 완화한 것이고, 이후 2단계 인증을 도입했습니다."'),
  [
   E('🔍', '검증 코드', 'SignupValidator.java',
     '$ sed -n \'14,18p\' src/main/java/member/SignupValidator.java\n'
     '  if (pw.length() < 6) {\n'
     '      errors.reject("password.tooShort");\n'
     '  }\n'
     '  // 사전 단어·연속문자·유출목록 대조 없음'),
   E('🔑', '2단계 인증 적용 현황', 'IAM',
     '$ ./mfa-coverage.sh\n'
     '전체 회원 482,113명\n'
     '  MFA 활성: 18,204명 (3.8%)   — 선택 가입\n'
     '  MFA 미설정: 463,909명 (96.2%)\n'
     '\n'
     '>> "2단계 인증 도입"은 맞으나 선택 사항이라 실제 적용률은 3.8%'),
   E('📊', '실제 비밀번호 강도 표본', '해시 대조',
     '$ ./pw-audit.sh --sample 50000 --wordlist rockyou\n'
     '유출 목록과 일치: 11,842건 (23.7%)\n'
     '상위 사용 비밀번호: 123456 (1,204건) / password (884건) / qwerty123 (712건)\n'
     '6자리 숫자만: 9,118건'),
  ],
  V('true',
    '2단계 인증을 도입한 것은 맞지만 선택 사항이라 96.2% 가 적용받지 않습니다. '
    '실제 표본에서 23.7% 가 이미 공개 유출 목록에 있는 비밀번호였습니다. 완화 근거가 성립하지 않으므로 정탐입니다.',
    '"보완통제를 도입했다"는 반론은 **적용률**까지 확인해야 검증됩니다. 도입 여부와 실제 커버리지는 전혀 다른 이야기입니다.'),
  F(
   O('복잡도 규칙을 강화한다 (대소문자·숫자·특수문자 + 90일 주기 변경)', False,
     '$ ./pw-audit.sh --sample 50000 --after-policy\n'
     '유출 목록과 일치: 8,204건 (16.4%)\n'
     '상위 사용: Password1! (1,882건) / Qwerty123! (1,104건)\n'
     '>> 규칙을 만족하면서 여전히 흔한 패턴으로 수렴',
     '복잡도 규칙은 사람이 규칙을 만족하는 뻔한 변형(첫 글자 대문자 + 뒤에 1!)으로 수렴하게 만듭니다. 주기적 변경 강제는 오히려 약한 비밀번호를 부릅니다.'),
   O('길이 하한 상향 + 유출 목록 대조 + 고위험 행위에 추가 인증', True,
     '$ curl -X POST https://app/signup -d "pw=Password1!"\n'
     '{"error":"이 비밀번호는 공개 유출 목록에 포함되어 있습니다"}\n'
     '$ curl -X POST https://app/signup -d "pw=바다거북이가느리게걷는다"\n'
     '{"ok":true}\n'
     '$ ./pw-audit.sh --sample 50000 --after-policy\n'
     '유출 목록과 일치: 0건\n'
     '가입 이탈률: 변화 없음 (긴 문장 허용으로 오히려 입력 편의 개선)',
     '유출 목록 대조가 복잡도 규칙보다 훨씬 효과적입니다. 길이를 늘리고 문장형을 허용하면 기획팀의 이탈률 우려도 함께 해결됩니다.'),
   O('전 회원에게 2단계 인증을 의무화한다', False,
     '$ ./mfa-rollout.sh --mandatory --simulate\n'
     '예상 이탈: 회원 12.4% · 콜센터 문의 급증\n'
     '>> 약한 비밀번호 자체는 그대로 남음',
     '좋은 방향이지만 이 지적에 대한 조치는 아닙니다. 비밀번호 정책과 MFA 는 각각 필요하며 하나가 다른 하나를 대신하지 않습니다.'))),

# ───────────────────────────── 하드코드된 중요정보 ─────────────────────────────
S('hardcoded_credentials',
  T('외부 제보', 'EXT-2026-09', '긴급', 'high',
    '보안 연구자로부터 "귀사 모바일 앱에서 운영 API 키를 추출할 수 있다"는 제보를 받았습니다.\n'
    '제보에는 실제 키 값 앞 8자리가 포함돼 있습니다.'),
  [
   E('📱', '앱 디컴파일', '점검 단말',
     '$ apktool d app-release.apk -o out/ >/dev/null\n'
     '$ grep -rn "api_key\\|secret\\|password" out/smali/ | head -3\n'
     'out/smali/com/corp/net/ApiClient.smali:88:  const-string v0, "sk_live_9a2c41e8b7d3"\n'
     'out/smali/com/corp/net/ApiClient.smali:92:  const-string v1, "Pr0d!Db#2026"\n'
     '\n'
     '>> 제보된 앞 8자리(sk_live_)와 일치'),
   E('📜', '이력 확인', 'git',
     '$ git log -S "sk_live_9a2c41e8" --oneline\n'
     'a3f81c2 (2024-03-11) 결제 연동 초기 구현\n'
     '\n'
     '$ git log --oneline -1\n'
     '9e14b7f (2026-09-10) 결제 모듈 리팩터링\n'
     '>> 2년 6개월간 저장소와 배포 앱에 평문으로 존재'),
   E('💳', '키 사용 내역', '결제 게이트웨이',
     '$ ./pg-audit.sh --key sk_live_9a2c41e8 --days 30\n'
     '호출 412,884건\n'
     '  등록된 서버 IP: 412,102건\n'
     '  미등록 IP:          782건  (해외 7개국)\n'
     '  실패(권한):         689건  (환불 API 시도)\n'
     '  성공:                93건  (조회 API — 거래내역 열람)'),
  ],
  V('true',
    '운영 결제 키가 앱 바이너리에 평문으로 박혀 있고, 이미 미등록 IP 에서 782건 사용됐습니다. '
    '환불 시도는 권한 부족으로 막혔지만 거래내역 조회 93건은 성공했습니다. '
    '정탐이며 즉시 키 폐기·회전이 필요한 진행 중 사고입니다.',
    '이런 항목은 "코드를 고치면 끝"이 아닙니다. 배포된 앱은 회수할 수 없으므로 **키 폐기가 먼저**이고 코드 수정은 그 다음입니다.'),
  F(
   O('소스에서 키를 지우고 다음 버전에 반영한다', False,
     '$ apktool d app-release-old.apk | grep sk_live_\n'
     'const-string v0, "sk_live_9a2c41e8b7d3"\n'
     '>> 이미 배포된 구버전 앱에는 그대로 남아 있고, 사용자는 즉시 업데이트하지 않음\n'
     '>> git 이력에도 남아 있어 저장소 접근자는 계속 확인 가능',
     '배포된 바이너리는 되돌릴 수 없습니다. 유출된 비밀은 지우는 것이 아니라 **무효화**해야 합니다.'),
   O('키를 즉시 폐기·회전하고, 앱은 단기 토큰을 서버에서 받아 쓰게 바꾼다', True,
     '$ ./pg-admin.sh revoke --key sk_live_9a2c41e8\n'
     'revoked at 2026-09-12T15:04:22Z\n'
     '$ curl -H "X-Api-Key: sk_live_9a2c41e8" https://pg.example/v1/tx\n'
     'HTTP/1.1 401 {"error":"key revoked"}\n'
     '\n'
     '$ apktool d app-release-new.apk | grep -c "sk_live_"\n'
     '0\n'
     '>> 앱은 로그인 후 서버에서 15분짜리 토큰을 발급받아 사용\n'
     '$ trufflehog git file://. --only-verified   →  0 findings (CI 게이트 추가)',
     '폐기 → 아키텍처 변경(앱에 장기 비밀을 두지 않음) → 재발 방지(CI 비밀 스캔) 순서입니다. 앱은 신뢰할 수 없는 환경이라는 전제에서 설계해야 합니다.'),
   O('키를 앱 안에서 암호화해 저장하고 실행 시 복호화한다', False,
     '$ frida -U -f com.corp.app -l dump-key.js\n'
     '[+] decrypted key: sk_live_9a2c41e8b7d3\n'
     '>> 복호화 키도 앱 안에 있어야 하므로 런타임에서 추출 가능',
     '앱 안에 복호화 키를 함께 두는 한 난독화일 뿐입니다. 시간만 벌 뿐 추출을 막지 못합니다.'))),

# ───────────────────────────── 암호화되지 않은 중요정보 ─────────────────────────────
S('no_encrypted_info',
  T('개인정보 점검', 'PRIV-2026-14', '높음', 'high',
    '개인정보 보호 점검에서 "주민등록번호가 평문으로 저장돼 있다"는 지적을 받았습니다.\n'
    '개발팀 회신: "DB 서버 디스크 전체가 암호화(TDE)돼 있습니다."'),
  [
   E('🗄️', '저장 형태 확인', 'DB',
     '$ mysql -e "SELECT user_id, rrn, phone FROM members LIMIT 2\\G"\n'
     'user_id: kim\n'
     'rrn:     880417-1******   (뒤 6자리 마스킹 저장)\n'
     'phone:   010-1234-5678\n'
     '\n'
     'user_id: lee\n'
     'rrn:     920311-2******\n'
     '>> 주민등록번호 뒤 7자리는 저장하지 않고 앞 6자리 + 성별 1자리만 보관'),
   E('🔐', '암호화 구성', 'DB / 애플리케이션',
     '$ mysql -e "SHOW VARIABLES LIKE \'%keyring%\'"\n'
     'keyring_file_data  /var/lib/mysql-keyring/keyring\n'
     '$ mysql -e "SELECT name, encryption FROM information_schema.innodb_tablespaces WHERE name LIKE \'%members%\'"\n'
     'app/members   Y     (TDE 적용)\n'
     '\n'
     '$ grep -rn "@Convert\\|AttributeConverter\\|encrypt" src/main/java/member/Member.java\n'
     '(결과 없음)   >> 컬럼 단위 암호화는 없음'),
   E('📋', '수집 항목 대조', '개인정보 처리방침 / 설계서',
     '$ ./pii-inventory.sh --table members\n'
     'rrn      : 수집근거 = 법령(전자금융거래법) · 보유 = 앞 7자리만 · 용도 = 실명확인\n'
     'phone    : 수집근거 = 동의 · 암호화 = 없음\n'
     'addr     : 수집근거 = 동의 · 암호화 = 없음\n'
     '\n'
     '>> 설계상 주민등록번호 전체는 저장하지 않음'),
  ],
  V('more',
    '지적된 "주민등록번호 평문 저장"은 사실과 다릅니다 — 뒤 7자리를 저장하지 않고 앞 7자리만 보관합니다. '
    '다만 TDE 는 디스크 도난만 막고 DB 접근 권한을 얻은 공격자에게는 무력합니다. '
    '또 주민번호 외에 전화번호·주소가 평문이고 암호화 대상인지 판단이 필요합니다. '
    '법령상 암호화 의무 대상 항목이 정확히 무엇인지 확인해야 최종 판정할 수 있습니다.',
    'TDE 를 "암호화했다"의 근거로 드는 반론이 매우 흔합니다. TDE 는 저장매체 수준 보호이고, SQL 삽입이나 계정 탈취로 DB 에 질의하면 평문으로 나옵니다. 위협 모델이 다릅니다.'),
  F(
   O('TDE 가 있으므로 조치 불요로 종결한다', False,
     '(2개월 뒤, 다른 화면의 SQL 삽입으로 침해)\n'
     '$ (공격자) SELECT user_id, rrn, phone FROM members\n'
     'kim  880417-1******  010-1234-5678\n'
     '>> TDE 는 질의 결과를 보호하지 않음 — 그대로 유출',
     'TDE 로 막히는 위협은 "디스크를 물리적으로 가져가는 것"입니다. 애플리케이션을 통한 유출은 전혀 막지 못합니다.'),
   O('암호화 의무 대상을 확정한 뒤 컬럼 단위 암호화·마스킹을 적용한다', True,
     '$ cat findings/PRIV-2026-14.md\n'
     '확인 결과: 주민번호 전체 저장 없음(앞 7자리만) — 지적 내용 일부 사실과 다름\n'
     '실제 조치 대상: 전화번호·주소 (법령 및 내부기준 대조 결과 암호화 대상)\n'
     '\n'
     '$ mysql -e "SELECT phone FROM members LIMIT 1"\n'
     'phone: gAAAAABm4x2K...   (컬럼 단위 암호화)\n'
     '$ mysql -e "SELECT phone_masked FROM members LIMIT 1"\n'
     'phone_masked: 010-****-5678   (조회 화면은 마스킹 컬럼 사용)\n'
     '>> 키는 DB 밖(KMS)에 보관 — DB 접근만으로는 복호화 불가',
     '먼저 대상을 확정하고(사실관계 정정 포함), 컬럼 단위로 암호화하며, 키를 DB 밖에 둡니다. 조회 화면은 복호화 없이 마스킹 값을 씁니다.'),
   O('DB 접근 권한을 축소하고 접속 기록을 남긴다', False,
     '$ ./db-acl.sh --table members\n'
     'SELECT 권한: appsvc, batch (2계정)\n'
     '>> 필요한 조치이나 평문 저장 자체는 그대로. appsvc 경유 유출에 무방비',
     '권한 축소와 감사는 반드시 병행해야 하지만, 애플리케이션 계정이 여전히 평문을 읽습니다. 그 계정이 바로 SQL 삽입의 통로입니다.'))),

# ───────────────────────────── 솔트 없는 해시 ─────────────────────────────
S('nosalthash',
  T('SAST 스캐너 리포트', 'SONAR-3540', '높음', 'high',
    '비밀번호 저장에 솔트 없는 해시를 쓴다는 지적입니다.\n'
    '개발팀 회신: "레거시 코드이고, 현재는 신규 가입에 다른 방식을 씁니다."'),
  [
   E('🔍', '해시 코드', 'PasswordUtil.java',
     '$ grep -rn "MessageDigest\\|BCrypt\\|Argon2" src/main/java/ | head -4\n'
     'auth/PasswordUtil.java:18:   MessageDigest md = MessageDigest.getInstance("SHA-256");\n'
     'auth/PasswordUtil.java:19:   return toHex(md.digest(pw.getBytes()));   // 솔트 없음\n'
     'auth/PasswordEncoderV2.java:12:  return new BCryptPasswordEncoder(12).encode(pw);\n'
     '\n'
     '$ grep -rn "PasswordUtil\\.\\|PasswordEncoderV2" src/main/java/ | grep -c "PasswordUtil\\."\n'
     '3'),
   E('🗄️', '저장된 해시 분포', 'DB',
     '$ mysql -e "SELECT LENGTH(pw_hash) len, COUNT(*) FROM members GROUP BY len"\n'
     '+-----+--------+\n'
     '| len | COUNT  |\n'
     '+-----+--------+\n'
     '|  64 | 391204 |   <- SHA-256 hex (솔트 없음)\n'
     '|  60 |  90909 |   <- BCrypt\n'
     '+-----+--------+\n'
     '>> 전체 48만 중 39만(81%)이 여전히 솔트 없는 해시'),
   E('🔓', '크래킹 실증', '점검 장비',
     '$ hashcat -m 1400 -a 0 sample_1000.txt rockyou.txt --quiet\n'
     'Recovered: 684/1000 (68.4%)  Time: 00:02:11\n'
     '\n'
     '$ sort sample_1000.txt | uniq -d | wc -l\n'
     '212\n'
     '>> 동일 해시 212쌍 — 같은 비밀번호를 쓰는 계정이 그대로 드러남'),
  ],
  V('true',
    '"레거시라 현재는 다른 방식"이라는 반론과 달리, 전체 계정의 81%(39만 건)가 여전히 솔트 없는 해시로 저장돼 있고 '
    '기존 코드 경로도 3곳 살아 있습니다. 2분 만에 68%가 복원됐고, 솔트가 없어 동일 비밀번호 사용자까지 드러납니다. 정탐입니다.',
    '"신규는 개선했다"는 말을 들으면 **기존 데이터의 비율**을 확인해야 합니다. 새 코드를 넣는 것과 기존 데이터를 이행하는 것은 별개의 일입니다.'),
  F(
   O('SHA-256 을 여러 번 반복 적용해 연산 비용을 올린다', False,
     '$ hashcat -m 1410 -a 0 sample_1000.txt rockyou.txt --quiet\n'
     'Recovered: 612/1000 (61.2%)  Time: 00:09:40\n'
     '>> 시간만 늘 뿐 GPU 앞에서는 여전히 빠름. 동일 해시 중복 문제도 그대로',
     '범용 해시는 빠르게 설계된 함수라 반복해도 GPU 병렬화에 취약합니다. 솔트가 없으면 중복 노출 문제도 남습니다.'),
   O('비밀번호 전용 해시로 전환하고, 로그인 시 점진적으로 재해시한다', True,
     '$ mysql -e "SELECT LENGTH(pw_hash) len, COUNT(*) FROM members GROUP BY len"\n'
     '|  60 | 482113 |   (4주 경과 후 — 전량 이행 완료)\n'
     '\n'
     '// 로그인 성공 시 옛 형식이면 조용히 새 형식으로 다시 저장한다\n'
     'if (isLegacy(m.getPwHash()) && legacyMatches(pw, m.getPwHash())) {\n'
     '    m.setPwHash(bcrypt.encode(pw));   // 사용자는 아무것도 하지 않아도 됨\n'
     '}\n'
     '$ hashcat -m 3200 sample_1000.txt rockyou.txt --quiet\n'
     'Recovered: 3/1000  Time: 06:14:22 (중단)',
     '평문을 모르니 일괄 변환은 불가능합니다. 로그인 시점에 재해시하는 것이 사용자 영향 없이 이행하는 표준 방법이고, 미접속 계정은 기한 후 비밀번호 재설정으로 처리합니다.'),
   O('DB 의 pw_hash 컬럼을 추가로 암호화한다', False,
     '(애플리케이션 침해 시)\n'
     '$ (공격자) 애플리케이션 복호화 경로 이용 → 해시 획득 → 오프라인 크래킹\n'
     'Recovered: 681/1000\n'
     '>> 복호화 키를 가진 애플리케이션이 뚫리면 원점',
     '해시를 암호화하는 것(peppering 과 다름)은 키 관리 부담만 늘리고 근본 문제인 해시 알고리즘 선택을 바꾸지 못합니다.'))),

# ───────────────────────────── 충분하지 않은 키 길이 ─────────────────────────────
S('notenoughkey',
  T('SAST 스캐너 리포트', 'SONAR-3566', '중간', 'mid',
    '암호화 키 길이가 짧다는 지적이 3건 올라왔습니다.\n'
    '대상: 결제 연동 모듈, 내부 캐시, 레거시 배치.'),
  [
   E('🔍', '지적된 3곳', '소스',
     '$ grep -rn "KeyGenerator\\|generateKey\\|KeyPairGenerator" src/main/java/\n'
     'pay/PgClient.java:31       KeyPairGenerator.getInstance("RSA").initialize(1024)\n'
     'cache/CacheCipher.java:22  KeyGenerator.getInstance("AES").init(128)\n'
     'batch/LegacyExport.java:19 KeyGenerator.getInstance("DES").init(56)'),
   E('📦', '각 지점의 용도와 데이터', '설계서 / 코드',
     '$ ./data-flow.sh --components PgClient,CacheCipher,LegacyExport\n'
     'PgClient     : 결제사 연동 전문 서명 · 대외 · 카드정보 포함 · 장기 보존\n'
     'CacheCipher  : 세션 캐시 암호화 · 내부 · TTL 30분 · AES-128 (표준 권고 충족)\n'
     'LegacyExport : 정산 파일 암호화 · 대외 전송 · DES-56\n'
     '\n'
     '$ ./usage-check.sh LegacyExport\n'
     '마지막 실행: 2023-06-30   상태: 스케줄 비활성 (죽은 코드)'),
   E('🧪', '실제 통신 확인', '점검 서버',
     '$ openssl s_client -connect pg.example:443 </dev/null 2>/dev/null | grep -i "server public key"\n'
     'Server public key is 2048 bit\n'
     '\n'
     '$ ./pg-spec.sh --field signature\n'
     '전문 서명 알고리즘: SHA256withRSA / 키 길이 1024 (우리 측 서명키)\n'
     '>> 결제사 요구 규격은 2048 이상. 현재 1024 로 운영 중'),
  ],
  V('more',
    '3건을 같은 지적으로 묶을 수 없습니다. AES-128(CacheCipher)은 현행 권고를 충족하므로 오탐입니다. '
    'DES-56(LegacyExport)은 명백히 부적절하지만 2023년 이후 실행되지 않는 죽은 코드라 위험도 판단이 달라집니다. '
    'RSA-1024(PgClient)는 대외 결제 전문 서명에 쓰이며 결제사 규격에도 미달하는 실제 문제입니다. '
    '각각 별건으로 분리하고, 죽은 코드의 제거 가능 여부를 확인해야 합니다.',
    '스캐너는 "키 길이 부족" 한 줄로 묶어 올리지만, 용도·노출 범위·실제 사용 여부에 따라 결론이 완전히 달라집니다. 건별로 쪼개는 것이 진단원의 일입니다.'),
  F(
   O('3건 모두 정탐으로 올려 일괄 상향을 요구한다', False,
     '(개발팀 회신)\n'
     '"AES-128 이 왜 취약한지 근거를 알려주세요. 현행 권고 기준으로 적합한 것으로 압니다."\n'
     '>> 근거 제시 불가 — 나머지 2건의 신뢰도까지 함께 떨어짐',
     '한 건이라도 근거 없이 올리면 같은 보고서의 진짜 지적까지 의심받습니다. 건별 근거가 보고서의 힘입니다.'),
   O('건별로 분리해 각각 판정하고 우선순위를 나눈다', True,
     '$ cat findings/SONAR-3566.md\n'
     '#1 PgClient RSA-1024  → 정탐/긴급. 대외 서명키, 결제사 규격(2048) 미달\n'
     '     조치: 키 재발급 + 결제사 키 교체 협의 (교체창 필요)\n'
     '#2 LegacyExport DES-56 → 정탐/중. 2023-06 이후 미실행 죽은 코드\n'
     '     조치: 코드 제거 (제거가 상향보다 확실) — 소유팀 확인 후 삭제\n'
     '#3 CacheCipher AES-128 → 오탐. 현행 권고 충족. 재검토 조건: 권고 상향 시\n'
     '\n'
     '$ ./pg-spec.sh --field signature\n'
     '전문 서명 알고리즘: SHA256withRSA / 키 길이 2048   ✓\n'
     '$ grep -rn "DES" src/  →  0 (모듈 삭제 완료)',
     '용도와 노출을 기준으로 나누면 조치 방법도 달라집니다. 안 쓰는 코드는 고치는 것보다 지우는 것이 확실합니다.'),
   O('전사 표준으로 모든 키를 RSA-4096 으로 통일한다', False,
     '$ ./load-test.sh --tls-handshake\n'
     '핸드셰이크 지연 +340% · 결제사 연동 호환성 실패 (상대 규격 미지원)\n'
     '>> 과도한 상향으로 성능·호환성 문제 발생',
     '더 긴 키가 항상 좋은 선택은 아닙니다. 상대 시스템 규격과 성능 요구를 함께 봐야 합니다.'))),

# ───────────────────────────── 취약한 암호화 알고리즘 ─────────────────────────────
S('risky_crypto',
  T('내부 감사 지적', 'AUD-2026-27', '높음', 'high',
    '감사에서 "취약한 암호 알고리즘(MD5)을 사용 중"이라는 지적을 받았습니다.\n'
    '개발팀 회신: "그 MD5 는 비밀번호가 아니라 파일 중복 체크용입니다."'),
  [
   E('🔍', 'MD5 사용 지점 전수', '소스',
     '$ grep -rn "MD5\\|md5" src/main/java/ --include=*.java\n'
     'file/DedupService.java:24   MessageDigest.getInstance("MD5")   // 업로드 중복 판정\n'
     'auth/LegacyToken.java:41    DigestUtils.md5Hex(userId + SECRET)  // 자동로그인 토큰\n'
     'util/ETagUtil.java:15       DigestUtils.md5Hex(body)            // HTTP ETag'),
   E('🎫', '자동로그인 토큰 분석', '점검 서버',
     '$ curl -sI https://app/main -b "auto=$(echo -n \'kim|SECRET\' | md5sum | cut -c1-32)"\n'
     'HTTP/1.1 200 OK\n'
     'X-Authenticated-User: kim\n'
     '\n'
     '$ sed -n \'38,44p\' src/main/java/auth/LegacyToken.java\n'
     '  String token = DigestUtils.md5Hex(userId + SECRET);   // SECRET 은 소스에 상수\n'
     '  if (token.equals(cookie.getValue())) { login(userId); }\n'
     '>> SECRET 이 하드코딩돼 있어 임의 사용자의 토큰을 계산 가능'),
   E('🔐', 'SECRET 값 확인', 'git',
     '$ grep -rn "SECRET *=" src/main/java/auth/LegacyToken.java\n'
     'private static final String SECRET = "corp2019!";\n'
     '\n'
     '$ ./token-forge.sh --user admin --secret \'corp2019!\'\n'
     'auto=8f2a41e89c2b4d7a1e3f5b8c9d0a2e41\n'
     '$ curl -sI https://app/main -b "auto=8f2a41e8..." | grep X-Auth\n'
     'X-Authenticated-User: admin'),
  ],
  V('true',
    '개발팀 설명은 절반만 맞습니다. 중복 체크(DedupService)와 ETag 용도의 MD5 는 보안 목적이 아니라 수용 가능하지만, '
    '자동로그인 토큰(LegacyToken)에도 MD5 가 쓰이고 있고 SECRET 까지 하드코딩돼 있어 **임의 계정 위장이 실제로 성공**했습니다. '
    '관리자 계정 위장이 재현됐으므로 정탐이며 긴급입니다.',
    '"그 용도가 아니다"라는 반론이 나오면 **전수 검색으로 다른 용도를 확인**해야 합니다. 한 지점만 보고 판단하면 진짜 문제를 놓칩니다.'),
  F(
   O('MD5 를 SHA-256 으로 바꾼다', False,
     '$ ./token-forge.sh --user admin --secret \'corp2019!\' --algo sha256\n'
     'auto=c4f8...\n'
     '$ curl -sI https://app/main -b "auto=c4f8..." | grep X-Auth\n'
     'X-Authenticated-User: admin\n'
     '>> 해시를 바꿔도 SECRET 이 공개돼 있어 위조 가능',
     '이 취약점의 원인은 해시 알고리즘이 아니라 **비밀 없는 서명 구조**입니다. 알고리즘만 바꾸면 그대로 뚫립니다.'),
   O('용도별로 분리해 조치한다 — 토큰은 서버 보관 난수, MD5 는 비보안 용도만 유지', True,
     '$ ./token-forge.sh --user admin --secret \'corp2019!\'\n'
     '$ curl -sI https://app/main -b "auto=<위조 토큰>"\n'
     'HTTP/1.1 401 Unauthorized\n'
     '\n'
     '// 토큰: 계산하는 값이 아니라 서버가 발급·보관하는 난수\n'
     'String token = secureRandom256();           // 추측·계산 불가\n'
     'tokenRepo.save(token, userId, expiry);      // 서버가 대조\n'
     '\n'
     '// 중복체크·ETag: 보안 목적이 아니므로 유지 (근거 문서화)\n'
     '$ cat findings/AUD-2026-27.md | grep -A1 "DedupService"\n'
     'DedupService/ETagUtil: 비보안 용도 — 유지. 근거: 무결성/인증에 사용하지 않음',
     '알고리즘 이름이 아니라 **용도와 위협**으로 판단합니다. 토큰은 계산 가능한 값이면 안 되고, 비보안 용도 MD5 는 근거를 남기고 유지해도 됩니다.'),
   O('자동로그인 기능을 없앤다', False,
     '(기획팀 회신)\n'
     '"모바일 웹 이탈률이 22% 증가합니다. 대안 없이는 수용 불가."\n'
     '>> 기능 제거는 조치가 아니라 요구사항 변경. 합의 없이 결정할 수 없음',
     '기능을 없애면 위험도 없어지지만 그것은 진단원이 단독으로 결정할 사안이 아닙니다. 안전한 구현 방법을 제시하는 것이 먼저입니다.'))),

# ───────────────────────────── 부적절한 난수 ─────────────────────────────
S('useofinsufficient_random',
  T('고객 문의(VOC)', 'VOC-7955', '높음', 'high',
    '"비밀번호 재설정 메일을 신청하지도 않았는데 내 계정 비밀번호가 바뀌었다"는 신고가 5건 접수됐습니다.\n'
    '피해 계정들의 재설정 시각이 3분 이내로 몰려 있습니다.'),
  [
   E('🔍', '토큰 생성 코드', 'ResetService.java',
     '$ sed -n \'27,32p\' src/main/java/auth/ResetService.java\n'
     '  Random r = new Random(System.currentTimeMillis());\n'
     '  String token = String.valueOf(r.nextInt(900000) + 100000);   // 6자리\n'
     '  resetRepo.save(userId, token, now.plusHours(24));\n'
     '  mailer.sendResetLink(email, token);'),
   E('🎲', '토큰 분포 분석', 'DB',
     '$ mysql -e "SELECT token, created_at FROM pw_reset ORDER BY created_at DESC LIMIT 6"\n'
     '481203  2026-09-12 02:11:04\n'
     '481204  2026-09-12 02:11:05\n'
     '481207  2026-09-12 02:11:08\n'
     '481211  2026-09-12 02:11:12\n'
     '>> 생성 시각이 가까우면 토큰도 연속 — 시드가 현재 시각이기 때문'),
   E('💻', '예측 재현', '점검 서버',
     '$ ./predict-token.sh --target victim@example.com\n'
     '[1] 재설정 요청 발송 (t=02:30:00.000)\n'
     '[2] 같은 밀리초 시드로 후보 200개 생성\n'
     '[3] 후보 대입 시도...\n'
     '    시도 37회 만에 적중 — token=community 692418\n'
     'HTTP/1.1 200 OK  {"result":"비밀번호가 변경되었습니다"}\n'
     '>> 소요 시간 11초'),
  ],
  V('true',
    '재설정 토큰이 현재 시각을 시드로 한 예측 가능한 난수입니다. 실제로 11초 만에 타인 계정의 비밀번호가 변경됐고, '
    '신고된 5건의 시각 근접성도 이 패턴과 일치합니다. 정탐이며 진행 중인 계정 탈취 사고입니다.',
    '난수 관련 지적을 "확률이 낮으니 위험도 중간"으로 낮추는 경우가 있습니다. 예측 가능한 난수는 확률의 문제가 아니라 계산의 문제입니다.'),
  F(
   O('토큰 자릿수를 6자리에서 10자리로 늘린다', False,
     '$ ./predict-token.sh --target victim@example.com --digits 10\n'
     '    시도 41회 만에 적중\n'
     '>> 시드가 예측 가능하면 자릿수는 의미가 없음',
     '예측 가능한 생성기에서 나온 값은 길이와 무관하게 재현됩니다. 문제는 범위가 아니라 생성 방식입니다.'),
   O('암호학적 난수 생성기 + 1회용·단기 만료 + 시도 제한', True,
     '$ ./predict-token.sh --target victim@example.com\n'
     '    시도 200회 — 적중 0회 (예측 불가)\n'
     '    시도 11회에서 429 Too Many Requests (레이트 리밋)\n'
     '\n'
     'byte[] b = new byte[32];\n'
     'SecureRandom.getInstanceStrong().nextBytes(b);\n'
     'String token = Base64.getUrlEncoder().withoutPadding().encodeToString(b);\n'
     '// 유효 15분 · 1회 사용 후 즉시 폐기 · 사용 시 기존 세션 전부 무효화',
     '암호학적 난수가 기본이고, 여기에 짧은 만료·1회용·시도 제한을 더합니다. 재설정 성공 시 기존 세션을 끊는 것도 중요합니다.'),
   O('재설정 메일에 본인 확인 질문을 추가한다', False,
     '$ ./predict-token.sh --target victim@example.com --with-kba\n'
     '    질문: "출생 도시는?" → SNS 공개 정보로 응답 → 통과\n'
     '>> 지식 기반 인증은 공개 정보로 우회되는 경우가 많음',
     '지식 기반 확인은 보조 수단일 뿐이며, 예측 가능한 토큰이라는 원인을 그대로 둡니다.'))),

# ───────────────────────────── 부적절한 전자서명 확인 ─────────────────────────────
S('impropersignature',
  T('연계 기관 보안 권고', 'ADV-2026-88', '높음', 'high',
    '연계 기관에서 "JWT 서명 검증 우회 취약점"에 대한 권고를 배포했습니다.\n'
    '우리 시스템이 영향받는지 확인이 필요합니다.'),
  [
   E('🔍', '토큰 검증 코드', 'JwtVerifier.java',
     '$ sed -n \'18,26p\' src/main/java/auth/JwtVerifier.java\n'
     '  DecodedJWT jwt = JWT.decode(token);            // 디코드만 — 검증 아님\n'
     '  String alg = jwt.getAlgorithm();\n'
     '  if ("none".equals(alg)) {\n'
     '      throw new SecurityException("alg=none 금지");\n'
     '  }\n'
     '  Algorithm a = Algorithm.HMAC256(SECRET);\n'
     '  JWT.require(a).build().verify(token);          // 검증 수행\n'
     '  return jwt.getClaim("userId").asString();'),
   E('💻', 'alg=none 시도', '점검 서버',
     '$ ./jwt-forge.sh --alg none --claim userId=admin\n'
     'eyJhbGciOiJub25lIn0.eyJ1c2VySWQiOiJhZG1pbiJ9.\n'
     '$ curl -H "Authorization: Bearer eyJhbGciOiJub25lIn0..." https://app/api/me\n'
     'HTTP/1.1 401 {"error":"alg=none 금지"}\n'
     '>> 차단됨'),
   E('🔑', '알고리즘 혼동 시도', '점검 서버',
     '$ ./jwt-forge.sh --alg HS256 --key-from public.pem --claim userId=admin\n'
     '$ curl -H "Authorization: Bearer <위조 토큰>" https://app/api/me\n'
     'HTTP/1.1 401 {"error":"signature verification failed"}\n'
     '\n'
     '$ grep -rn "RSA\\|RS256\\|getPublicKey" src/main/java/auth/\n'
     '(결과 없음)   >> 비대칭 서명을 쓰지 않아 알고리즘 혼동 공격 불가\n'
     '$ ./secret-entropy.sh SECRET\n'
     '길이 64바이트 · 엔트로피 충분 · KMS 에서 주입 (소스에 없음)'),
  ],
  V('false',
    'alg=none 은 명시적으로 차단되고, 검증도 decode 가 아니라 verify 로 수행합니다. '
    '대칭키(HMAC)만 쓰므로 공개키를 HMAC 키로 악용하는 알고리즘 혼동 공격도 성립하지 않습니다. '
    '비밀키는 KMS 에서 주입되고 엔트로피도 충분합니다. 권고 대상 패턴에 해당하지 않으므로 오탐입니다.',
    '다만 decode 로 얻은 클레임을 verify 전에 읽는 코드 순서는 위험합니다. 지금은 검증을 통과해야만 반환하지만, 나중에 누군가 이 사이에 로직을 추가하면 검증 전 값을 신뢰하게 됩니다. 오탐 종결과 별개로 코드 순서 개선을 권고사항으로 남기세요.'),
  F(
   O('오탐 종결 + 검증 순서 개선을 권고사항으로 등록한다', True,
     '$ cat findings/ADV-2026-88.md\n'
     '판정: 오탐 — alg=none 차단 확인, HMAC 전용(혼동 공격 불가), 키 KMS 주입\n'
     '근거: PoC 2종 401 실패 (로그 첨부)\n'
     '권고(별건, 위험도 낮음): decode → verify 순서를 verify 우선으로 정리\n'
     '재검토 조건: 비대칭 서명(RS256) 도입 시 / 다중 발급자 지원 시\n'
     '\n'
     '// 권고 반영 후\n'
     'DecodedJWT jwt = JWT.require(Algorithm.HMAC256(SECRET))\n'
     '                    .withIssuer(ISS).build().verify(token);   // 검증이 먼저',
     '오탐이지만 그냥 닫지 않고, 위험이 생길 수 있는 구조는 별건 권고로 남깁니다. 이것이 진단이 개발에 실제로 기여하는 방식입니다.'),
   O('권고가 나왔으니 JWT 라이브러리를 최신으로 올린다', False,
     '$ ./jwt-forge.sh --alg none --claim userId=admin\n'
     'HTTP/1.1 401  (이전과 동일)\n'
     '>> 원래 취약하지 않았으므로 변화 없음. 회귀 위험만 발생',
     '영향받지 않는 것을 확인했다면 업그레이드는 정기 일정으로 처리하면 됩니다. 권고가 나왔다는 이유만으로 긴급 변경을 넣으면 회귀 위험이 더 큽니다.'),
   O('정탐으로 올리고 서명 검증 로직 전면 재작성을 요구한다', False,
     '(개발팀 회신)\n'
     '"alg=none 도 막히고 PoC 도 실패하는데 어떤 시나리오인지 알려주세요."\n'
     '>> 근거 없는 지적 — 다음 보고서의 신뢰도까지 손상',
     '재현되지 않는 지적은 올리지 않습니다. 대신 구조적 우려는 위험도를 낮춰 권고로 남기는 것이 정확합니다.'))),

# ───────────────────────────── 부적절한 인증서 유효성 검증 ─────────────────────────────
S('impropersignature_validity',
  T('운영팀 장애 보고', 'OPS-25102', '중간', 'mid',
    '대외 연계 서버 인증서가 만료됐는데도 우리 시스템만 아무 오류 없이 통신했습니다.\n'
    '다른 연계 기관은 전부 연결 실패 알람이 떴습니다.'),
  [
   E('🔍', 'TLS 클라이언트 설정', 'HttpClientConfig.java',
     '$ sed -n \'22,31p\' src/main/java/net/HttpClientConfig.java\n'
     '  TrustManager[] tm = new TrustManager[]{\n'
     '      new X509TrustManager() {\n'
     '          public void checkServerTrusted(X509Certificate[] c, String a) { }  // 항상 통과\n'
     '          public void checkClientTrusted(X509Certificate[] c, String a) { }\n'
     '          public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }\n'
     '      }};\n'
     '  ctx.init(null, tm, new SecureRandom());\n'
     '  builder.hostnameVerifier((h, s) -> true);        // 호스트명 검증도 무력화'),
   E('📜', '이력 추적', 'git',
     '$ git log -S "checkServerTrusted" --format="%h %ad %an %s" --date=short\n'
     'c81f2a3 2021-04-02 (개발팀) 개발환경 자가서명 인증서 대응 (임시)\n'
     '\n'
     '$ git log --format="%h %ad" --date=short -1 -- src/main/java/net/HttpClientConfig.java\n'
     'c81f2a3 2021-04-02\n'
     '>> "임시" 조치가 5년 5개월간 운영에 그대로'),
   E('💻', '중간자 공격 재현', '점검 서버',
     '$ mitmproxy --mode reverse:https://partner.example -p 8443 &\n'
     '$ ./app-call.sh --endpoint https://partner.example/api/settle\n'
     '[mitmproxy] POST /api/settle  200\n'
     '  request body: {"acct":"110-***-45678","amount":18400000, ...}\n'
     '\n'
     '>> 자가서명 인증서로 가로챘는데 애플리케이션은 정상 처리. 정산 전문 평문 노출'),
  ],
  V('true',
    '인증서 검증과 호스트명 검증이 모두 무력화돼 있습니다. 만료 인증서로도 통신이 된 것이 그 증거이며, '
    '중간자 공격 재현에서 정산 전문(계좌번호·금액)이 그대로 노출됐습니다. '
    '2021년 "임시" 조치가 5년간 운영에 남아 있었습니다. 정탐이며 대외 연계 구간 전체가 영향 범위입니다.',
    '"장애가 안 났다"가 오히려 위험 신호일 수 있습니다. 만료 인증서에서도 연결이 됐다는 것은 검증을 하지 않는다는 뜻입니다.'),
  F(
   O('만료된 상대 인증서를 갱신해 달라고 요청한다', False,
     '$ ./app-call.sh --endpoint https://partner.example/api/settle   # 갱신 후\n'
     '200 OK\n'
     '$ mitmproxy --mode reverse:... & ./app-call.sh\n'
     '[mitmproxy] POST /api/settle  200   >> 여전히 가로채짐',
     '증상(만료 인증서 통과)만 없앴고 원인(검증 무력화)은 그대로입니다. 중간자 공격은 계속 성립합니다.'),
   O('기본 TrustManager 로 되돌리고, 개발환경은 별도 신뢰 저장소로 분리한다', True,
     '$ mitmproxy --mode reverse:https://partner.example -p 8443 &\n'
     '$ ./app-call.sh --endpoint https://partner.example/api/settle\n'
     'javax.net.ssl.SSLHandshakeException: PKIX path building failed\n'
     '>> 중간자 차단됨\n'
     '\n'
     '// 운영: 기본 검증 사용 (커스텀 TrustManager 제거)\n'
     '// 개발: -Djavax.net.ssl.trustStore=dev-truststore.jks 로 분리\n'
     '$ ./cert-monitor.sh --add partner.example --alert-days 30\n'
     '>> 만료 30일 전 알람 등록 (검증을 켜면 만료가 장애가 되므로 감시가 필수)',
     '검증을 되살리고 개발 편의는 환경 분리로 해결합니다. 검증을 켜는 순간 인증서 만료가 장애로 이어지므로 만료 감시를 함께 넣어야 합니다.'),
   O('연계 구간을 전용선으로 옮긴다', False,
     '(비용 검토)\n'
     '전용선 신설 3개월 · 연 4,800만원\n'
     '>> 그동안 검증 무력화 코드는 그대로 유지됨. 다른 대외 연계 12곳도 동일 코드 사용',
     '망을 바꿔도 같은 클라이언트 코드를 쓰는 다른 연계 구간이 남습니다. 코드를 고치는 편이 빠르고 넓게 적용됩니다.'))),

# ───────────────────────────── 무결성 검사 없는 코드 다운로드 ─────────────────────────────
S('nointegritycode',
  T('보안팀 정기 진단', 'SEC-1301', '높음', 'high',
    '웹 페이지가 외부 CDN 스크립트를 무결성 검증 없이 로드한다는 지적입니다.\n'
    '해당 스크립트는 결제 화면에도 포함돼 있습니다.'),
  [
   E('🔍', '스크립트 태그 전수', 'HTML',
     '$ grep -rhn "<script src=\\"https://" public/*.html | grep -v integrity | head -4\n'
     'checkout.html:41  <script src="https://cdn.thirdparty.example/analytics.js"></script>\n'
     'checkout.html:44  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>\n'
     'main.html:22      <script src="https://cdn.thirdparty.example/widget.js"></script>\n'
     '\n'
     '$ grep -c "integrity=" public/checkout.html\n'
     '0'),
   E('🌐', '외부 스크립트 변경 감시', '모니터링',
     '$ ./js-watch.sh --url https://cdn.thirdparty.example/analytics.js --days 90\n'
     '해시 변경 14회 (공지 없음)\n'
     '  2026-08-30  +2.1KB  신규 함수 추가\n'
     '  2026-09-07  +0.4KB  엔드포인트 변경 (collect.thirdparty.example → t.metrics-cdn.example)\n'
     '\n'
     '$ whois metrics-cdn.example | grep -i "creation"\n'
     'Creation Date: 2026-08-28   >> 최근 등록된 도메인'),
   E('💳', '결제 화면 DOM 접근 확인', '브라우저',
     '$ ./dom-audit.sh --page checkout.html --watch "input[name=cardNumber]"\n'
     'analytics.js: addEventListener("input") 등록 확인\n'
     'analytics.js: navigator.sendBeacon("https://t.metrics-cdn.example/c", ...) 호출 확인\n'
     '>> 결제 카드번호 입력 필드 값이 외부로 전송되고 있음'),
  ],
  V('true',
    '무결성 검증 없이 로드되는 외부 스크립트가 결제 화면에서 카드번호 입력값을 읽어 최근 등록된 외부 도메인으로 전송하고 있습니다. '
    '스크립트는 90일간 14회 무단 변경됐습니다. 정탐이며 카드정보 유출이 진행 중인 사고(전형적인 웹 스키밍)입니다.',
    '"믿을 만한 CDN"이라는 이유로 위험도를 낮추면 안 됩니다. 공급망 공격의 핵심은 신뢰받는 경로를 통해 들어온다는 점입니다.'),
  F(
   O('해당 분석 스크립트를 결제 화면에서만 제거한다', False,
     '$ ./dom-audit.sh --page main.html\n'
     'widget.js: 동일 오리진에서 로드 · 동일 외부 도메인으로 전송 확인\n'
     '>> 다른 화면의 스크립트도 같은 공급자 — 세션 쿠키·입력값 수집 계속',
     '한 화면만 걷어내도 같은 공급자의 다른 스크립트가 남습니다. 공급자 단위로 판단해야 합니다.'),
   O('SRI(무결성 해시) 적용 + 자체 호스팅 + CSP 로 출처 제한', True,
     '$ curl -sI https://app/checkout.html | grep -i content-security-policy\n'
     "content-security-policy: script-src 'self' https://cdn.jsdelivr.net; connect-src 'self'\n"
     '\n'
     '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"\n'
     '        integrity="sha384-9ndCyUa..." crossorigin="anonymous"></script>\n'
     '\n'
     '$ ./js-watch.sh --simulate-tamper\n'
     '>> 브라우저: Failed to find a valid digest — 스크립트 로드 거부\n'
     '$ ./dom-audit.sh --page checkout.html\n'
     '>> 외부 전송 0건 (connect-src 로 차단)',
     'SRI 로 변조를 막고, CSP 로 전송 목적지까지 제한합니다. 결제 같은 민감 화면은 서드파티 스크립트를 아예 두지 않는 것이 가장 안전합니다.'),
   O('CDN 공급자에게 변경 시 사전 공지를 요청한다', False,
     '(공급자 회신)\n'
     '"표준 약관상 사전 공지 의무는 없습니다."\n'
     '>> 계약으로 해결되지 않으며, 공급자 자신이 침해될 경우에도 무방비',
     '계약은 사고 후 책임을 정할 뿐 기술적으로 막지 못합니다. 공급자 자신이 침해되는 경우가 실제 사고의 다수입니다.'))),

# ───────────────────────────── 중요자원에 대한 잘못된 권한 설정 ─────────────────────────────
S('wrong_auth',
  T('서버 점검', 'SRV-2026-33', '높음', 'high',
    '정기 서버 점검에서 설정 파일 권한이 과도하다는 지적이 나왔습니다.\n'
    '운영팀 회신: "해당 서버는 운영자만 접속 가능합니다."'),
  [
   E('📁', '파일 권한', '운영 서버',
     '$ ls -la /app/config/\n'
     '-rw-rw-rw- 1 appsvc appsvc  1284 Mar 11  2024 application.yml\n'
     '-rw-rw-rw- 1 appsvc appsvc   417 Mar 11  2024 datasource.properties\n'
     '-rwxrwxrwx 1 appsvc appsvc  2841 Sep 10 14:02 deploy.sh\n'
     '\n'
     '$ grep -i password /app/config/datasource.properties\n'
     'spring.datasource.password=Pr0d!Db#2026'),
   E('👥', '서버 접속 계정 현황', 'IAM',
     '$ ./host-accounts.sh --host app-prod-01\n'
     '로그인 가능 계정 14개\n'
     '  운영자      3  (kim, lee, park)\n'
     '  개발자      6  (배포 확인 목적, 2024년 임시 부여 — 회수 안 됨)\n'
     '  협력사      2  (공용 계정 1개 포함)\n'
     '  서비스계정  3\n'
     '>> "운영자만 접속"이라는 전제와 실제가 다름'),
   E('📜', '접근 이력', 'auditd',
     '$ ausearch -f /app/config/datasource.properties -ts recent | grep -c "success=yes"\n'
     '47\n'
     '$ ausearch -f /app/config/datasource.properties -ts recent | grep -oP \'uid=\\K\\w+\' | sort -u\n'
     'appsvc\n'
     'dev_choi\n'
     'partner_ops'),
  ],
  V('true',
    '설정 파일이 666(모든 사용자 읽기·쓰기)이고 운영 DB 비밀번호가 평문으로 들어 있습니다. '
    '"운영자만 접속한다"는 전제는 사실과 다릅니다 — 실제로 14개 계정이 접속 가능하고, '
    '개발자·협력사 계정이 해당 파일을 읽은 이력이 47건 남아 있습니다. 정탐입니다.',
    '권한 설정 지적은 "누가 접속할 수 있는가"를 확인해야 실제 위험을 알 수 있습니다. 파일 권한과 계정 현황을 함께 봐야 합니다. 쓰기 권한(deploy.sh 777)은 코드 실행으로 이어져 더 위험합니다.'),
  F(
   O('파일 권한을 644 로 바꾼다', False,
     '$ ls -la /app/config/datasource.properties\n'
     '-rw-r--r-- 1 appsvc appsvc 417 Sep 12 16:02 datasource.properties\n'
     '$ sudo -u dev_choi cat /app/config/datasource.properties\n'
     'spring.datasource.password=Pr0d!Db#2026\n'
     '>> 여전히 모든 로그인 계정이 읽을 수 있음',
     '644 는 "다른 사용자 읽기 허용"입니다. 비밀이 담긴 파일에는 부족합니다.'),
   O('600 + 소유자 분리 + 비밀은 파일 밖(비밀관리 서비스)으로 이동', True,
     '$ ls -la /app/config/\n'
     '-rw------- 1 appsvc appsvc  1284 Sep 12 16:10 application.yml\n'
     '-rwxr-x--- 1 deploy appsvc  2841 Sep 12 16:10 deploy.sh\n'
     '$ sudo -u dev_choi cat /app/config/application.yml\n'
     'cat: Permission denied\n'
     '\n'
     '$ grep -i password /app/config/application.yml\n'
     'spring.datasource.password=${VAULT:secret/prod/db#password}\n'
     '>> 파일에는 참조만 남고 실제 값은 기동 시 주입 · 접근 이력은 Vault 에 기록\n'
     '$ ./host-accounts.sh --host app-prod-01  →  로그인 가능 계정 5개 (회수 완료)',
     '권한을 좁히고, 비밀 자체를 파일에서 들어내고, 불필요한 계정을 회수합니다. 세 가지가 같이 가야 실제로 좁혀집니다.'),
   O('파일을 암호화해 저장한다', False,
     '$ sudo -u dev_choi cat /app/config/datasource.properties.enc\n'
     '(암호문)\n'
     '$ sudo -u dev_choi cat /app/config/decrypt-key.txt\n'
     'k8Fj2...   >> 복호화 키도 같은 서버 같은 권한으로 존재',
     '복호화 키를 같은 곳에 같은 권한으로 두면 암호화의 의미가 없습니다. 키는 반드시 다른 신뢰 경계에 있어야 합니다.'))),

# ───────────────────────────── 쿠키를 통한 정보 노출 ─────────────────────────────
S('cookiedisclosure',
  T('SAST 스캐너 리포트', 'SONAR-3588', '중간', 'mid',
    '쿠키에 민감정보가 저장된다는 지적입니다.\n'
    '개발팀 회신: "Base64 로 인코딩해서 저장하고 있습니다."'),
  [
   E('🍪', '실제 쿠키 값', '브라우저',
     '$ curl -sI https://app/login -d "id=kim&pw=..." | grep -i set-cookie\n'
     'Set-Cookie: uinfo=a2ltfDAxMC0xMjM0LTU2Nzh8ODgwNDE3LTF8VVNFUg==; Path=/\n'
     'Set-Cookie: JSESSIONID=9F2A41E8...; Path=/; HttpOnly; Secure\n'
     '\n'
     '$ echo \'a2ltfDAxMC0xMjM0LTU2Nzh8ODgwNDE3LTF8VVNFUg==\' | base64 -d\n'
     'kim|010-1234-5678|880417-1|USER'),
   E('🔍', '쿠키 사용 코드', 'LoginController.java',
     '$ sed -n \'61,66p\' src/main/java/auth/LoginController.java\n'
     '  String info = String.join("|", m.getId(), m.getPhone(), m.getRrnPrefix(), m.getRole());\n'
     '  Cookie c = new Cookie("uinfo", Base64.getEncoder().encodeToString(info.getBytes()));\n'
     '  c.setPath("/");\n'
     '  response.addCookie(c);        // HttpOnly·Secure 미설정\n'
     '\n'
     '$ grep -rn "uinfo" src/main/java/ | grep -v LoginController\n'
     'common/HeaderTag.java:22   String role = decode(cookie("uinfo")).split("\\\\|")[3];   // 권한 판단에 사용'),
   E('🌐', '전송 구간 확인', '네트워크',
     '$ curl -sI http://app.corp.example/ | grep -i "location\\|strict-transport"\n'
     'Location: https://app.corp.example/\n'
     '(Strict-Transport-Security 헤더 없음)\n'
     '\n'
     '$ ./cookie-scope.sh uinfo\n'
     'Secure: 미설정 → 평문 HTTP 요청에도 전송됨\n'
     'HttpOnly: 미설정 → JavaScript 접근 가능 (XSS 시 탈취)'),
  ],
  V('true',
    'Base64 는 인코딩이지 암호화가 아닙니다. 한 줄 명령으로 전화번호와 주민등록번호 앞자리가 그대로 드러납니다. '
    'Secure·HttpOnly 도 없어 평문 구간 전송과 스크립트 접근이 모두 가능하며, '
    '심지어 이 쿠키 값으로 권한(role)까지 판단하고 있어 변조 시 권한 상승도 성립합니다. 정탐입니다.',
    '"인코딩했다"를 "암호화했다"로 받아들이면 안 됩니다. Base64·URL 인코딩·16진수는 전부 되돌리기 위한 표현 형식이지 보호 수단이 아닙니다.'),
  F(
   O('Base64 대신 AES 로 암호화해서 쿠키에 담는다', False,
     '$ ./cookie-replay.sh --cookie "uinfo=<다른 사용자 암호문 복사>"\n'
     'HTTP/1.1 200 OK — 해당 사용자로 인식됨\n'
     '>> 복호화는 못 해도 통째로 재사용 가능. 개인정보를 클라이언트에 두는 문제도 그대로',
     '암호화해도 클라이언트에 있는 값은 복사·재사용될 수 있습니다. 무결성 검증이 없으면 replay 가 성립합니다.'),
   O('개인정보를 쿠키에서 빼고 세션 식별자만 남긴다 + 쿠키 속성 적용', True,
     '$ curl -sI https://app/login -d "id=kim&pw=..." | grep -i set-cookie\n'
     'Set-Cookie: JSESSIONID=9F2A41E8...; Path=/; HttpOnly; Secure; SameSite=Lax\n'
     '(uinfo 쿠키 없음)\n'
     '\n'
     '// 개인정보·권한은 서버 세션에서 조회\n'
     'Member m = memberRepo.findById((String) session.getAttribute("userId"));\n'
     '$ curl -sI https://app/ | grep -i strict-transport\n'
     'strict-transport-security: max-age=31536000; includeSubDomains',
     '클라이언트에는 "누구인지 가리키는 값"만 두고 실제 정보는 서버가 갖습니다. 권한 판단도 서버 데이터로 해야 합니다.'),
   O('쿠키 만료 시간을 짧게 설정한다', False,
     '$ echo \'a2ltfDAxMC0xMjM0...\' | base64 -d\n'
     'kim|010-1234-5678|880417-1|USER\n'
     '>> 유효 기간과 무관하게 발급 즉시 노출',
     '만료 단축은 탈취 후 악용 창을 줄일 뿐, 개인정보가 클라이언트에 평문으로 내려가는 문제 자체를 해결하지 못합니다.'))),

# ───────────────────────────── 잘못된 세션에 의한 정보 노출 ─────────────────────────────
S('session_data_exposure',
  T('고객 문의(VOC)', 'VOC-8012', '긴급', 'high',
    '"마이페이지에 들어갔는데 모르는 사람 이름과 주문 내역이 떴다"는 문의가 접수됐습니다.\n'
    '점심시간과 저녁 접속 몰리는 시간대에만 발생합니다.'),
  [
   E('🔍', '사용자 정보 보관 방식', 'UserContext.java',
     '$ sed -n \'8,16p\' src/main/java/common/UserContext.java\n'
     '  @Component\n'
     '  public class UserContext {\n'
     '      private String userId;                  // 인스턴스 필드\n'
     '      private String userName;\n'
     '\n'
     '      public void set(String id, String name) { this.userId = id; this.userName = name; }\n'
     '      public String getUserId() { return userId; }\n'
     '  }\n'
     '>> 싱글턴 빈의 인스턴스 필드에 요청별 사용자 정보를 저장'),
   E('🧪', '동시 요청 재현', '점검 서버',
     '$ ./concurrent-test.sh --users kim,lee,park --threads 50 --duration 60s\n'
     '요청 8,412건 중 교차 응답 1,204건 (14.3%)\n'
     '  kim 세션 요청 → lee 데이터 반환: 402건\n'
     '  park 세션 요청 → kim 데이터 반환: 388건\n'
     '\n'
     '$ ./concurrent-test.sh --threads 1\n'
     '요청 500건 중 교차 응답 0건\n'
     '>> 동시 접속 시에만 발생 — 부하가 낮은 개발환경에서는 재현되지 않음'),
   E('📊', '시간대별 발생 분포', 'app log',
     '$ ./log-scan.sh --pattern "user-mismatch" --group-by hour\n'
     '12시 412건 · 13시 388건 · 19시 294건 · 20시 110건\n'
     '기타 시간대 0건\n'
     '>> 동시 접속자 수와 정확히 비례'),
  ],
  V('true',
    '싱글턴 빈의 인스턴스 필드에 요청별 사용자 정보를 담아 스레드 간에 공유되고 있습니다. '
    '동시 요청 테스트에서 14.3% 가 다른 사용자 데이터를 반환했습니다. '
    '개발환경에서 재현되지 않은 이유는 동시성이 낮아서일 뿐입니다. 정탐이며 개인정보 교차 노출 사고입니다.',
    '"재현이 안 된다"는 이유로 오탐 처리하기 쉬운 유형입니다. 동시성 결함은 부하 조건에서만 드러나므로, 단일 요청 테스트로는 절대 확인할 수 없습니다.'),
  F(
   O('해당 메서드에 synchronized 를 붙인다', False,
     '$ ./concurrent-test.sh --threads 50 --duration 60s\n'
     '교차 응답 0건 / 평균 응답 시간 4,120ms (기존 82ms)\n'
     '처리량 94% 감소 — 사실상 서비스 불가\n'
     '>> 데이터 오염은 막았으나 모든 요청이 한 줄로 직렬화됨',
     '공유 상태에 락을 걸면 정확해지지만 동시성이 사라집니다. 애초에 공유하지 않는 것이 옳습니다.'),
   O('요청 범위(request scope) 또는 스레드 로컬로 바꾸고 동시성 테스트를 회귀에 넣는다', True,
     '$ ./concurrent-test.sh --threads 50 --duration 60s\n'
     '요청 8,412건 / 교차 응답 0건 / 평균 응답 79ms\n'
     '\n'
     '@Component @RequestScope          // 요청마다 새 인스턴스\n'
     'public class UserContext { ... }\n'
     '\n'
     '$ grep -rn "@Component" src/ | xargs grep -l "private String user" \n'
     '(0건 — 동일 패턴 전수 점검 완료)\n'
     '$ cat .github/workflows/ci.yml | grep concurrent\n'
     '  - run: ./concurrent-test.sh --threads 50   # 회귀 방지',
     '상태를 요청 단위로 격리하면 락 없이 해결됩니다. 같은 패턴이 다른 빈에 없는지 전수 확인하고, 동시성 테스트를 CI 에 넣어 재발을 막습니다.'),
   O('세션 검증 로직을 응답 직전에 한 번 더 추가한다', False,
     '$ ./concurrent-test.sh --threads 50\n'
     '교차 응답 0건 / 오류 응답 1,180건 (14.0%)\n'
     '>> 잘못된 데이터를 걸러내지만 정상 요청이 실패로 바뀜. 원인은 그대로',
     '검증을 덧대면 노출은 막히지만 그 자체가 장애가 됩니다. 오염된 상태를 만들지 않는 것이 먼저입니다.'))),

# ───────────────────────────── 주석문 안의 시스템 주요정보 ─────────────────────────────
S('sensitiveinfo_sourcecodecomments',
  T('외부 제보', 'EXT-2026-11', '중간', 'mid',
    '"귀사 웹 페이지 소스 주석에서 내부 서버 정보와 테스트 계정을 확인했다"는 제보를 받았습니다.'),
  [
   E('🌐', '배포된 페이지 소스', '운영',
     '$ curl -s https://app.corp.example/login | grep -n "<!--" -A2 | head -12\n'
     '41:<!-- TODO: 운영 반영 전 삭제\n'
     '42:     테스트 계정: test_admin / Test!2024\n'
     '43:     내부 API: http://10.0.9.14:8080/internal/v1 -->\n'
     '--\n'
     '88:<!-- 결제 모듈 담당: 김** (내선 3412)\n'
     '89:     PG 테스트키: sk_test_4a2f81c9 -->'),
   E('🔑', '노출 정보 유효성 확인', '점검',
     '$ curl -s -o /dev/null -w "%{http_code}" -u test_admin:\'Test!2024\' https://app/admin\n'
     '200\n'
     '>> 테스트 계정이 운영 환경에서 살아 있음\n'
     '\n'
     '$ ./iam-check.sh test_admin\n'
     'role: ADMIN · 생성 2024-03-11 · 마지막 로그인 2026-09-08 · MFA 미설정'),
   E('🔍', '동일 패턴 전수', '빌드 산출물',
     '$ grep -rn "TODO\\|FIXME\\|테스트 계정\\|sk_test_\\|10\\.0\\." dist/ --include=*.html --include=*.js | wc -l\n'
     '84\n'
     '$ ./build-config.sh --check comment-strip\n'
     'HTML 주석 제거: 미적용\n'
     'JS 주석 제거(minify): 적용됨 (소스맵 함께 배포 — 원본 주석 복원 가능)'),
  ],
  V('true',
    '주석에 노출된 테스트 관리자 계정이 운영 환경에서 실제로 동작하고(200 OK, ADMIN 권한, MFA 없음), '
    '내부 API 주소까지 드러났습니다. 동일 패턴이 배포 산출물에 84건 남아 있고 소스맵도 함께 배포돼 있습니다. '
    '정탐이며 계정 즉시 비활성화가 필요합니다.',
    '주석 노출은 "정보 노출"로 분류돼 위험도가 낮게 매겨지기 쉽습니다. 하지만 노출된 자격증명이 **살아 있는지**를 확인하면 등급이 완전히 달라집니다.'),
  F(
   O('지적된 주석 2곳을 삭제하고 재배포한다', False,
     '$ curl -s https://app/checkout | grep -c "<!--.*TODO"\n'
     '9\n'
     '$ curl -s https://app/assets/app.js.map | grep -c "sk_test_"\n'
     '3\n'
     '>> 나머지 82건과 소스맵은 그대로. 테스트 계정도 여전히 활성',
     '지적된 곳만 고치는 것은 같은 제보를 반복해서 받게 만듭니다. 노출된 자격증명 무효화가 빠져 있는 것이 더 큰 문제입니다.'),
   O('노출 계정 즉시 무효화 + 빌드에서 주석·소스맵 제거 + CI 검사 추가', True,
     '$ ./iam-admin.sh disable test_admin\n'
     '$ curl -s -o /dev/null -w "%{http_code}" -u test_admin:\'Test!2024\' https://app/admin\n'
     '401\n'
     '\n'
     '$ ./build-config.sh --check comment-strip\n'
     'HTML 주석 제거: 적용 · 소스맵: 배포 제외(내부 저장소만)\n'
     '$ grep -rn "TODO\\|sk_test_\\|10\\.0\\." dist/ | wc -l\n'
     '0\n'
     '$ cat .github/workflows/ci.yml | grep -A1 secret-scan\n'
     '  - run: trufflehog filesystem dist/ --fail   # 배포 전 차단',
     '노출된 비밀은 지우는 것이 아니라 무효화하는 것이 먼저입니다. 그다음 빌드 단계에서 기계적으로 제거하고, CI 게이트로 재발을 막습니다.'),
   O('개발 가이드에 "주석에 민감정보 금지" 항목을 추가한다', False,
     '(3개월 뒤)\n'
     '$ grep -rn "TODO\\|password\\|sk_test_" dist/ | wc -l\n'
     '61\n'
     '>> 가이드만으로는 줄지 않음',
     '사람의 주의에 의존하는 통제는 규모가 커지면 반드시 실패합니다. 빌드·CI 단계에서 기계적으로 막아야 합니다.'))),

])
