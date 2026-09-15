# -*- coding: utf-8 -*-
"""KISA 49 보안약점 '현업 진단' 시나리오 — part 3 (15종).

시간 및 상태 · 에러처리 · 코드오류 · 캡슐화 · API 오용.
구성 규칙은 specs_code_lab.py 헤더 참조.

이 묶음은 "장애로 먼저 드러나는" 약점이 많다. 현업에서 이런 항목은 보안팀이 아니라
운영팀 티켓으로 먼저 도착하며, 그것이 보안 결함인지 알아보는 것이 진단원의 역할이다.
"""
from specs_code_lab import S, T, E, V, F, O

SCENARIOS = dict([

# ───────────────────────────── 경쟁조건 (TOCTOU) ─────────────────────────────
S('race_condition',
  T('정산팀 이상 보고', 'FIN-2026-51', '긴급', 'high',
    '포인트 잔액이 마이너스인 계정이 42개 발견됐습니다.\n'
    '해당 계정들은 모두 이벤트 응모 시각이 밀리초 단위로 겹칩니다.'),
  [
   E('🔍', '차감 로직', 'PointService.java',
     '$ sed -n \'44,51p\' src/main/java/point/PointService.java\n'
     '  public void use(String userId, int amount) {\n'
     '      int balance = pointRepo.findBalance(userId);      // 조회\n'
     '      if (balance < amount) {\n'
     '          throw new NotEnoughPointException();\n'
     '      }\n'
     '      pointRepo.updateBalance(userId, balance - amount); // 사용\n'
     '  }\n'
     '>> 조회와 사용 사이에 다른 트랜잭션이 끼어들 수 있음'),
   E('🧪', '동시 요청 재현', '점검 서버',
     '$ ./race-test.sh --user test01 --balance 1000 --requests 20 --amount 1000 --parallel\n'
     '성공 응답: 14건\n'
     '최종 잔액: -13000\n'
     '\n'
     '$ ./race-test.sh --user test01 --balance 1000 --requests 20 --amount 1000 --serial\n'
     '성공 응답: 1건\n'
     '최종 잔액: 0\n'
     '>> 순차 실행에서는 정상 — 동시 실행에서만 발생'),
   E('💰', '피해 규모', 'DB',
     '$ mysql -e "SELECT COUNT(*), SUM(balance) FROM point WHERE balance < 0"\n'
     '+----------+--------------+\n'
     '|       42 |    -8,412,000|\n'
     '+----------+--------------+\n'
     '$ mysql -e "SELECT user_id, COUNT(*) c FROM point_log WHERE created_at BETWEEN ... GROUP BY user_id HAVING c>5 ORDER BY c DESC LIMIT 2"\n'
     'user_8812   184건 (0.4초 내)\n'
     'user_9034   122건 (0.3초 내)'),
  ],
  V('true',
    '잔액을 확인한 시점과 차감하는 시점 사이에 다른 요청이 끼어들어 검사 결과가 무효가 됩니다. '
    '동시 요청 재현에서 1,000포인트로 14,000포인트를 사용했고, 실제 피해액이 841만원입니다. '
    '정탐이며 자동화 도구로 반복 악용된 흔적(0.4초에 184건)도 확인됩니다.',
    '단일 요청 테스트로는 절대 재현되지 않습니다. "검사 후 사용" 패턴을 보면 그 사이에 다른 주체가 끼어들 수 있는지를 먼저 의심해야 합니다.'),
  F(
   O('차감 전에 잔액을 한 번 더 조회해 재확인한다', False,
     '$ ./race-test.sh --requests 20 --parallel\n'
     '성공 응답: 11건 / 최종 잔액: -10000\n'
     '>> 확인을 두 번 해도 확인과 사용 사이의 틈은 그대로',
     '검사 횟수를 늘려도 검사와 사용이 원자적이지 않으면 틈은 남습니다. 창이 좁아질 뿐입니다.'),
   O('DB 원자 연산 또는 비관적 잠금으로 검사와 차감을 한 번에 처리한다', True,
     '$ ./race-test.sh --user test01 --balance 1000 --requests 20 --amount 1000 --parallel\n'
     '성공 응답: 1건 / 최종 잔액: 0 / 나머지 19건: NotEnoughPointException\n'
     '\n'
     '-- 조건과 갱신을 한 문장으로 (원자적)\n'
     'UPDATE point SET balance = balance - :amt\n'
     ' WHERE user_id = :uid AND balance >= :amt;\n'
     '-- 영향 행 수가 0이면 잔액 부족\n'
     '\n'
     'ALTER TABLE point ADD CONSTRAINT chk_bal CHECK (balance >= 0);   -- 최후 방어선',
     '검사 조건을 갱신문 안에 넣으면 DB 가 원자성을 보장합니다. 여기에 CHECK 제약을 더해 코드가 실수해도 음수가 저장되지 않게 합니다.'),
   O('이벤트 응모 API 에 사용자별 1초 레이트 리밋을 건다', False,
     '$ ./race-test.sh --requests 20 --parallel --distributed\n'
     '성공 응답: 6건 / 최종 잔액: -5000\n'
     '>> 서버 2대에 분산 요청 — 인스턴스별 카운터라 우회됨',
     '레이트 리밋은 속도만 늦춥니다. 분산 환경에서는 카운터 자체가 또 다른 경쟁 상태가 됩니다.'))),

# ───────────────────────────── 종료되지 않는 반복문·재귀 ─────────────────────────────
S('infinite_loop',
  T('운영팀 장애 보고', 'OPS-25130', '높음', 'high',
    '특정 조직도를 조회하면 해당 요청 스레드가 응답하지 않고, 반복되면 서버 전체가 멈춥니다.\n'
    '재시작하면 잠시 정상이다가 같은 증상이 재발합니다.'),
  [
   E('💥', '스레드 덤프', 'jstack',
     '$ jstack 3182 | grep -A5 "http-nio-8080-exec-14"\n'
     '"http-nio-8080-exec-14" #14 daemon RUNNABLE\n'
     '   at org.corp.org.OrgService.buildTree(OrgService.java:61)\n'
     '   at org.corp.org.OrgService.buildTree(OrgService.java:64)\n'
     '   at org.corp.org.OrgService.buildTree(OrgService.java:64)\n'
     '   ... 8,192 frames omitted\n'
     '\n'
     '$ jstack 3182 | grep -c "OrgService.buildTree"\n'
     '188   >> 스레드 188개가 같은 지점에 묶여 있음'),
   E('🔍', '해당 코드', 'OrgService.java',
     '$ sed -n \'58,66p\' src/main/java/org/OrgService.java\n'
     '  private Node buildTree(Long deptId) {\n'
     '      Dept d = deptRepo.findById(deptId);\n'
     '      Node n = new Node(d);\n'
     '      for (Long childId : deptRepo.findChildIds(deptId)) {\n'
     '          n.add(buildTree(childId));        // 깊이 제한·방문 기록 없음\n'
     '      }\n'
     '      return n;\n'
     '  }'),
   E('🗄️', '데이터 확인', 'DB',
     '$ mysql -e "WITH RECURSIVE t AS (SELECT id,parent_id,1 lv FROM dept WHERE id=400 '
     'UNION ALL SELECT d.id,d.parent_id,t.lv+1 FROM dept d JOIN t ON d.parent_id=t.id WHERE t.lv<10) SELECT * FROM t"\n'
     '400 -> 412 -> 455 -> 400 -> 412 -> 455 -> 400 ...\n'
     '\n'
     '>> 조직도 데이터에 순환 참조 존재 (400 → 412 → 455 → 400)\n'
     '$ mysql -e "SELECT COUNT(*) FROM dept WHERE parent_id = id"\n'
     '2   >> 자기 자신을 부모로 갖는 행도 2건'),
  ],
  V('true',
    '데이터에 순환 참조가 있는데 재귀에 깊이 제한도 방문 기록도 없어 무한 재귀에 빠집니다. '
    '스레드 188개가 묶여 서버 전체가 멈췄습니다. 외부에서 조회 요청만으로 유발 가능하므로 '
    '가용성 공격 경로이기도 합니다. 정탐입니다.',
    '이런 항목은 "데이터 오류"로 분류돼 데이터만 고치고 닫히는 경우가 많습니다. 데이터는 언제든 다시 깨질 수 있으므로 코드가 방어해야 합니다.'),
  F(
   O('순환 참조 데이터 3건을 정정한다', False,
     '$ mysql -e "UPDATE dept SET parent_id=NULL WHERE id IN (455,...)"\n'
     '(2주 뒤 — 조직 개편 배치 실행 후)\n'
     '$ jstack 3182 | grep -c "OrgService.buildTree"\n'
     '204   >> 새 순환 참조 발생, 동일 장애 재현',
     '데이터 정정은 필요하지만 재발합니다. 조직 개편·이관·수기 입력 등 깨질 경로가 계속 있습니다.'),
   O('방문 노드 추적 + 깊이 상한 + 데이터 무결성 제약을 함께 넣는다', True,
     '$ curl -s -o /dev/null -w "%{http_code} %{time_total}s" https://app/org/tree?deptId=400\n'
     '400 0.031s\n'
     '{"error":"조직도에 순환 참조가 있습니다 (dept 400,412,455)"}\n'
     '\n'
     'private Node buildTree(Long id, Set<Long> seen, int depth) {\n'
     '    if (!seen.add(id)) throw new CyclicOrgException(id);   // 이미 방문\n'
     '    if (depth > MAX_DEPTH) throw new OrgTooDeepException();\n'
     '    ...\n'
     '}\n'
     '$ mysql -e "SELECT COUNT(*) FROM dept WHERE parent_id = id"  →  0  (제약 추가)',
     '코드가 방어하고, 데이터도 제약으로 막고, 문제가 생기면 멈추는 대신 원인을 알려주는 오류를 냅니다. 세 가지가 함께 가야 재발하지 않습니다.'),
   O('요청 타임아웃을 10초로 설정해 스레드를 회수한다', False,
     '$ ./load-test.sh --endpoint /org/tree?deptId=400 --rps 30\n'
     '스레드 풀 고갈까지 22초 · 전체 서비스 응답 불가\n'
     '>> 타임아웃이 걸려도 그동안 CPU 는 100%, 반복 요청이면 결국 고갈',
     '타임아웃은 회수를 돕지만 무한 재귀는 그 사이에도 CPU 를 태웁니다. 반복 요청으로 쉽게 고갈시킬 수 있습니다.'))),

# ───────────────────────────── 오류메시지 정보노출 ─────────────────────────────
S('error_message',
  T('모의해킹 보고서', 'PT-2026-052', '중간', 'mid',
    '모의해킹에서 "오류 메시지를 통해 내부 구조가 노출된다"는 지적을 받았습니다.\n'
    '개발팀 회신: "운영 환경은 스택트레이스를 끄도록 설정돼 있습니다."'),
  [
   E('💻', '오류 유발', '점검 서버',
     "$ curl -s 'https://app/board?id=abc' | head -12\n"
     '<html><head><title>HTTP Status 500</title></head><body>\n'
     '<h1>HTTP Status 500 – Internal Server Error</h1>\n'
     '<p><b>Type</b> Exception Report</p>\n'
     '<p><b>Message</b> For input string: "abc"</p>\n'
     '<pre>java.lang.NumberFormatException: For input string: "abc"\n'
     '  at org.corp.board.BoardController.view(BoardController.java:38)\n'
     '  at org.corp.board.BoardDao.findById(BoardDao.java:57)\n'
     '  ... jdbc:mysql://10.0.9.12:3306/appdb?user=appsvc</pre>'),
   E('🔍', '설정 확인', 'application.yml / web.xml',
     '$ grep -rn "include-stacktrace\\|include-message" src/main/resources/\n'
     'application-prod.yml:12   server.error.include-stacktrace: never\n'
     'application-prod.yml:13   server.error.include-message: never\n'
     '\n'
     '$ grep -rn "error-page" src/main/webapp/WEB-INF/web.xml\n'
     '(결과 없음)   >> 컨테이너 기본 오류 페이지가 사용됨\n'
     '\n'
     '$ ps -ef | grep java | grep -o "spring.profiles.active=[a-z]*"\n'
     'spring.profiles.active=prod   >> 프로파일은 정상 적용'),
   E('🧪', '경로별 차이 확인', '점검 서버',
     "$ curl -s 'https://app/api/board/abc' | jq .\n"
     '{"timestamp":"2026-09-12T15:04:22Z","status":500,"error":"Internal Server Error","path":"/api/board/abc"}\n'
     '>> 스프링이 처리하는 경로는 설정대로 정보가 가려짐\n'
     '\n'
     "$ curl -s 'https://app/board?id=abc' | grep -c 'jdbc:mysql'\n"
     '1\n'
     '>> 서블릿 예외가 컨테이너까지 올라간 경로는 기본 오류 페이지가 노출'),
  ],
  V('true',
    '설정은 제대로 돼 있지만 적용 범위가 좁습니다. 스프링이 처리하는 경로는 가려지는 반면, '
    '예외가 컨테이너까지 전파되는 경로에서는 톰캣 기본 오류 페이지가 그대로 나와 '
    '스택트레이스와 DB 접속 문자열(내부 IP·계정)까지 노출됩니다. 정탐입니다.',
    '"설정했다"는 회신을 받으면 **모든 경로에 적용되는지**를 확인해야 합니다. 프레임워크 설정은 프레임워크가 처리하는 범위에만 적용됩니다.'),
  F(
   O('프로파일 설정을 다시 한 번 확인하고 재배포한다', False,
     "$ curl -s 'https://app/board?id=abc' | grep -c 'jdbc:mysql'\n"
     '1\n'
     '>> 설정은 이미 올바름 — 아무 변화 없음',
     '이미 적용된 설정을 다시 확인해도 달라지지 않습니다. 원인이 설정이 아니라 적용 범위라는 것을 놓친 조치입니다.'),
   O('컨테이너 레벨 오류 페이지 등록 + 전역 예외 처리기 + 입력 검증', True,
     "$ curl -s 'https://app/board?id=abc'\n"
     '<html><body><h1>요청을 처리할 수 없습니다</h1>\n'
     '<p>오류 코드: ERR-9F2A41E8 (문의 시 알려주세요)</p></body></html>\n'
     '\n'
     '$ grep "ERR-9F2A41E8" /var/log/app/error.log\n'
     '[15:04:22] ERR-9F2A41E8 NumberFormatException: For input string: "abc"\n'
     '  at BoardController.view(BoardController.java:38) ...\n'
     '>> 상세는 서버 로그에만. 사용자에게는 추적용 코드만 전달\n'
     '\n'
     '<error-page><location>/error</location></error-page>   <!-- web.xml -->',
     '사용자에게는 추적 코드만 주고 상세는 로그에 남깁니다. 컨테이너 기본 페이지까지 덮어야 모든 경로가 가려집니다.'),
   O('500 오류가 나지 않도록 입력 검증만 추가한다', False,
     "$ curl -s 'https://app/board?id=99999999999999999999' | grep -c 'jdbc:mysql'\n"
     '1\n'
     '>> 다른 예외(ArithmeticException, DataAccessException)에서 동일 노출',
     '개별 예외를 막는 접근은 예외 종류만큼 구멍이 남습니다. 오류 응답의 형태 자체를 통제해야 합니다.'))),

# ───────────────────────────── 오류상황 대응 부재 ─────────────────────────────
S('error_handling_missing',
  T('정산팀 이상 보고', 'FIN-2026-58', '높음', 'high',
    '대외 기관 전송 배치가 "성공"으로 기록됐는데 상대 기관에는 파일이 도착하지 않았습니다.\n'
    '3일치 정산 데이터가 누락됐고 아무도 알아채지 못했습니다.'),
  [
   E('🔍', '전송 코드', 'SettleSender.java',
     '$ sed -n \'38,47p\' src/main/java/batch/SettleSender.java\n'
     '  public void send(File f) {\n'
     '      try {\n'
     '          sftp.upload(f, REMOTE_PATH);\n'
     '      } catch (Exception e) {\n'
     '          // TODO: 나중에 처리\n'
     '      }\n'
     '      jobRepo.markSuccess(jobId);        // 예외와 무관하게 성공 기록\n'
     '  }'),
   E('📜', '배치 로그', 'batch.log',
     '$ grep "settle-send" /var/log/app/batch.log | tail -4\n'
     '[09/09 02:00:04] settle-send START\n'
     '[09/09 02:00:09] settle-send SUCCESS  (0.5s)\n'
     '[09/10 02:00:03] settle-send START\n'
     '[09/10 02:00:08] settle-send SUCCESS  (0.5s)\n'
     '\n'
     '>> 정상 전송 시 평균 소요 42초. 0.5초 완료는 실제로 전송하지 않았다는 뜻'),
   E('🔌', '연결 상태 확인', '네트워크',
     '$ ssh-keyscan -p 22 sftp.partner.example 2>&1 | head -2\n'
     '# sftp.partner.example:22 SSH-2.0-OpenSSH_8.9\n'
     '$ sftp -b /dev/null batch@sftp.partner.example\n'
     'Permission denied (publickey).\n'
     '\n'
     '$ ls -la ~/.ssh/id_rsa\n'
     '-rw------- 1 batch batch 1679 Sep 09 01:44 id_rsa\n'
     '>> 9월 9일 01:44 에 키가 교체됨 (상대 기관 정기 키 교체) — 그 직후부터 인증 실패'),
  ],
  V('true',
    '예외를 삼키고(빈 catch) 예외 발생 여부와 무관하게 성공으로 기록하고 있습니다. '
    '9월 9일 상대 기관 키 교체 이후 3일간 전송이 전부 실패했는데 배치는 "SUCCESS" 를 남겼습니다. '
    '정탐이며, 실패를 감지할 수 없는 구조 자체가 결함입니다.',
    '이 유형은 보안 취약점으로 분류되지 않고 넘어가기 쉽습니다. 하지만 "실패를 성공으로 기록하는 시스템"은 무결성과 부인방지의 문제이며, 사고 대응의 근거 자체를 무너뜨립니다.'),
  F(
   O('catch 블록에 로그 출력을 추가한다', False,
     '$ grep "settle-send" /var/log/app/batch.log | tail -2\n'
     '[09/13 02:00:08] ERROR sftp upload failed: Permission denied\n'
     '[09/13 02:00:08] settle-send SUCCESS\n'
     '>> 로그는 남지만 여전히 성공으로 기록되고 아무도 보지 않음',
     '로그만 남기는 것은 "기록했다"일 뿐입니다. 상태가 여전히 성공이면 후속 절차가 전부 잘못 흘러갑니다.'),
   O('실패 시 작업 상태를 실패로 기록하고 알림·재시도·검증까지 연결한다', True,
     '$ grep "settle-send" /var/log/app/batch.log | tail -3\n'
     '[09/13 02:00:08] ERROR sftp upload failed: Permission denied (publickey)\n'
     '[09/13 02:00:08] settle-send FAILED  retry 1/3\n'
     '[09/13 02:00:41] ALERT sent: #ops-settle (PagerDuty INC-4412)\n'
     '\n'
     'try { sftp.upload(f, REMOTE_PATH); }\n'
     'catch (Exception e) { jobRepo.markFailed(jobId, e); alert.notify(e); throw e; }\n'
     'long remote = sftp.size(REMOTE_PATH + f.getName());\n'
     'if (remote != f.length()) throw new TransferVerifyException();   // 전송 후 검증\n'
     '\n'
     '$ ./job-monitor.sh --check stale\n'
     '>> 소요 시간이 평소의 10% 미만이면 이상으로 판정 (조용한 실패 탐지)',
     '실패를 실패로 기록하고, 사람에게 도달시키고, 전송 결과를 상대편에서 검증합니다. "성공했다고 말하는 것"과 "성공한 것"을 분리해야 합니다.'),
   O('배치 실행 결과를 매일 아침 담당자가 수동 확인한다', False,
     '(운영 현황)\n'
     '일일 배치 작업 184개 · 담당자 2명\n'
     '$ grep -c SUCCESS /var/log/app/batch.log   →  184\n'
     '>> 전부 SUCCESS 로 보이므로 수동 확인으로도 발견 불가',
     '상태 기록 자체가 틀렸으므로 사람이 봐도 알 수 없습니다. 데이터가 거짓이면 아무리 성실히 봐도 소용없습니다.'))),

# ───────────────────────────── 부적절한 예외처리 ─────────────────────────────
S('improper_exception',
  T('보안 관제 경보', 'SOC-4488', '높음', 'high',
    '한 계정에서 권한 오류가 초당 수십 건씩 발생하는데 서비스는 정상 동작 중이라는 경보입니다.\n'
    '해당 계정은 일반 사용자입니다.'),
  [
   E('🔍', '권한 검사 코드', 'AuthAspect.java',
     '$ sed -n \'27,36p\' src/main/java/auth/AuthAspect.java\n'
     '  try {\n'
     '      permissionService.check(userId, resource);\n'
     '  } catch (Throwable t) {          // Throwable 전체를 잡음\n'
     '      log.debug("권한 검사 실패", t);\n'
     '  }\n'
     '  return joinPoint.proceed();      // 예외와 무관하게 계속 진행'),
   E('💻', '재현', '점검 서버',
     '$ curl -s -b "SESSION=<일반사용자>" https://app/admin/members | jq \'.[0]\'\n'
     '{"userId":"kim","name":"김**","rrn":"880417-1******","role":"USER"}\n'
     '\n'
     '$ grep "권한 검사 실패" /var/log/app/app.log | tail -1\n'
     '[15:12:04] DEBUG 권한 검사 실패\n'
     '  org.corp.auth.PermissionDeniedException: user=kim resource=/admin/members\n'
     '>> 예외는 발생했지만 요청은 그대로 처리됨'),
   E('📊', '영향 범위', 'audit log',
     '$ ./audit-scan.sh --pattern "permission-exception-swallowed" --days 30\n'
     '권한 예외 발생 후 정상 응답: 88,412건\n'
     '  영향 엔드포인트 41개 (관리자 기능 12개 포함)\n'
     '  관련 계정 1,204개\n'
     '>> 권한 검사가 사실상 동작하지 않는 상태'),
  ],
  V('true',
    '권한 검사 실패 예외를 잡아 삼키고 요청을 그대로 진행시킵니다. '
    '일반 사용자가 관리자 기능에 접근해 개인정보를 조회하는 것이 재현됐고, '
    '30일간 88,412건이 같은 경로로 통과했습니다. 정탐이며 접근 통제가 전면 무력화된 상태입니다.',
    '예외 처리 결함은 "코드 품질" 문제로 분류되기 쉽습니다. 하지만 **보안 검사 코드에서 예외를 삼키면 그것은 곧 통제 부재**입니다. 어디서 삼키는지가 심각도를 결정합니다.'),
  F(
   O('로그 레벨을 DEBUG 에서 ERROR 로 올린다', False,
     '$ curl -s -b "SESSION=<일반사용자>" https://app/admin/members | jq \'.|length\'\n'
     '482113\n'
     '$ grep "권한 검사 실패" /var/log/app/app.log | tail -1\n'
     '[15:20:11] ERROR 권한 검사 실패 ...\n'
     '>> 로그는 잘 보이지만 접근은 그대로 허용',
     '로그가 잘 남는 것과 통제가 동작하는 것은 다릅니다. 보이는 것이 늘었을 뿐입니다.'),
   O('보안 예외는 삼키지 않고 차단으로 이어지게 하고, 예외 유형별로 처리를 분리한다', True,
     '$ curl -s -o /dev/null -w "%{http_code}" -b "SESSION=<일반사용자>" https://app/admin/members\n'
     '403\n'
     '\n'
     'try {\n'
     '    permissionService.check(userId, resource);\n'
     '} catch (PermissionDeniedException e) {\n'
     '    auditLog.denied(userId, resource);\n'
     '    throw e;                       // 차단으로 이어진다\n'
     '} catch (PermissionServiceUnavailableException e) {\n'
     '    throw new ServiceUnavailable();  // 확인 불가 시에도 허용하지 않는다(fail-closed)\n'
     '}\n'
     '$ grep -rn "catch (Throwable\\|catch (Exception e) {}" src/ | wc -l  →  0',
     '보안 검사는 실패 시 **거부**가 기본값이어야 합니다(fail-closed). 검사 자체가 불가능한 상황에서도 통과시키면 안 됩니다.'),
   O('권한 검사 로직에 버그가 없도록 테스트를 보강한다', False,
     '$ ./gradlew test --tests "*Permission*"\n'
     'PermissionServiceTest: 42 tests PASSED\n'
     '$ curl -s -b "SESSION=<일반사용자>" https://app/admin/members | jq \'.|length\'\n'
     '482113\n'
     '>> 검사 로직 자체는 정상 — 결과를 버리는 쪽이 문제',
     '검사는 제대로 동작하고 있습니다. 그 결과를 무시하는 호출부가 문제이므로 테스트를 늘려도 잡히지 않습니다.'))),

# ───────────────────────────── Null Pointer 역참조 ─────────────────────────────
S('null_pointer',
  T('운영팀 장애 보고', 'OPS-25166', '중간', 'mid',
    '결제 완료 페이지에서 간헐적으로 500 오류가 납니다. 발생률 약 0.3%.\n'
    '개발팀 회신: "재현이 안 되고 빈도가 낮아 우선순위를 낮췄습니다."'),
  [
   E('💥', '예외 로그', 'error.log',
     '$ grep NullPointerException /var/log/app/error.log | tail -2\n'
     '[15:31:08] NullPointerException: Cannot invoke "Coupon.getDiscount()" because "coupon" is null\n'
     '  at pay.PaymentService.calculate(PaymentService.java:88)\n'
     '\n'
     '$ grep -c NullPointerException /var/log/app/error.log\n'
     '1284'),
   E('🔍', '해당 코드', 'PaymentService.java',
     '$ sed -n \'84,92p\' src/main/java/pay/PaymentService.java\n'
     '  Coupon coupon = couponRepo.findByCode(code);       // 없으면 null\n'
     '  int discount = coupon.getDiscount();               // <== NPE 지점\n'
     '  int finalAmount = amount - discount;\n'
     '  ...\n'
     '  paymentRepo.save(new Payment(orderId, finalAmount, PAID));\n'
     '  inventoryService.decrease(orderId);\n'
     '  couponRepo.markUsed(code);'),
   E('🗄️', '데이터 정합성 확인', 'DB',
     '$ mysql -e "SELECT COUNT(*) FROM payment p LEFT JOIN inventory_log i ON p.order_id=i.order_id WHERE i.order_id IS NULL AND p.status=\'PAID\'"\n'
     '0\n'
     '$ mysql -e "SELECT COUNT(*) FROM orders WHERE status=\'PENDING\' AND created_at < NOW() - INTERVAL 1 DAY"\n'
     '1284\n'
     '\n'
     '$ ./tx-check.sh --method PaymentService.calculate\n'
     '@Transactional 적용됨 — 예외 시 전체 롤백 확인'),
  ],
  V('more',
    '예외가 발생하지만 트랜잭션이 롤백되어 결제·재고·쿠폰 상태는 모두 일관됩니다(정합성 깨짐 0건). '
    '즉 데이터 무결성 사고는 아니고, 사용자 입장에서는 결제 실패로 끝납니다. '
    '다만 1,284건의 주문이 PENDING 으로 방치돼 있고, 만료 쿠폰 코드를 반복 전송해 '
    '의도적으로 오류를 유발할 수 있는지(자원 소모·오류 기반 정보 수집) 확인이 필요합니다.',
    'NPE 를 무조건 "낮음"으로 처리하면 안 되고, 반대로 무조건 "높음"도 아닙니다. **트랜잭션 경계 안인지, 예외 후 어떤 상태가 남는지**를 보고 판단해야 합니다. 이 경우 롤백이 보호해 주고 있습니다.'),
  F(
   O('해당 줄에 null 검사를 추가한다', False,
     '$ grep -c NullPointerException /var/log/app/error.log   # 1주 뒤\n'
     '1102\n'
     '$ grep NullPointerException /var/log/app/error.log | grep -oP \'at \\K[\\w.]+\' | sort -u | head -3\n'
     'pay.PaymentService.applyPoint\n'
     'pay.PaymentService.validateCard\n'
     'order.OrderService.attachMemo\n'
     '>> 같은 패턴이 다른 지점에 다수 존재',
     '한 줄만 고치면 같은 유형이 계속 나옵니다. "없을 수 있는 값"을 어떻게 다룰지 규약이 없는 것이 원인입니다.'),
   O('없을 수 있는 값을 타입으로 드러내고, 오류 응답·PENDING 정리까지 함께 처리한다', True,
     '$ curl -s -X POST https://app/pay -d "code=EXPIRED_XX"\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"유효하지 않은 쿠폰입니다","code":"COUPON_NOT_FOUND"}\n'
     '\n'
     'Optional<Coupon> coupon = couponRepo.findByCode(code);   // 없을 수 있음이 타입에 드러남\n'
     'int discount = coupon.map(Coupon::getDiscount)\n'
     '                     .orElseThrow(() -> new InvalidCouponException(code));\n'
     '\n'
     '$ grep -c NullPointerException /var/log/app/error.log   →  0\n'
     '$ ./batch-run.sh cleanup-pending-orders   →  1,284건 정리 완료\n'
     '$ ./rate-limit.sh --path /pay --key coupon-fail --max 5/min   (오류 유발 남용 차단)',
     '"없을 수 있음"을 타입으로 표현하면 컴파일러가 처리를 강제합니다. 사용자에게는 원인을 알려주는 오류를 주고, 이미 쌓인 PENDING 도 함께 정리합니다.'),
   O('전역 예외 처리기에서 NPE 를 잡아 200 으로 응답한다', False,
     '$ curl -s -X POST https://app/pay -d "code=EXPIRED_XX"\n'
     'HTTP/1.1 200 OK\n'
     '{"result":"ok"}\n'
     '>> 결제가 안 됐는데 성공으로 응답 — 사용자·정산 모두 혼란',
     '오류를 감추면 더 큰 문제가 됩니다. 실패는 실패로 알려야 합니다.'))),

# ───────────────────────────── 정수형 오버플로우 ─────────────────────────────
S('integer_overflow',
  T('정산팀 이상 보고', 'FIN-2026-63', '높음', 'high',
    '대량 주문 1건의 결제 금액이 음수로 기록돼 있습니다.\n'
    '해당 주문은 정상 승인 처리됐고 상품도 출고됐습니다.'),
  [
   E('🔍', '금액 계산 코드', 'OrderService.java',
     '$ sed -n \'71,76p\' src/main/java/order/OrderService.java\n'
     '  int unitPrice = item.getPrice();      // 최대 2,000,000\n'
     '  int qty = request.getQty();           // 상한 검사 없음\n'
     '  int total = unitPrice * qty;          // int 연산\n'
     '  if (total < 0) { /* 없음 */ }\n'
     '  payment.request(total);'),
   E('🧪', '재현', '점검 서버',
     '$ curl -s -X POST https://app/order -d "itemId=8812&qty=2000" | jq .\n'
     '{"orderId":88921,"total":-1294967296,"status":"APPROVED"}\n'
     '\n'
     '# 2,000,000 * 2000 = 4,000,000,000 > int 최대값(2,147,483,647)\n'
     '$ python3 -c "print((2000000*2000 + 2**31) % 2**32 - 2**31)"\n'
     '-294967296'),
   E('💳', '결제 처리 결과', 'PG / 재고',
     '$ ./pg-audit.sh --order 88921\n'
     'amount: -1294967296  →  PG 응답: APPROVED (음수 금액 검증 없음)\n'
     'settlement: 0원 청구\n'
     '\n'
     '$ mysql -e "SELECT qty FROM inventory_log WHERE order_id=88921"\n'
     '2000   >> 재고 2,000개 차감 · 출고 완료'),
  ],
  V('true',
    '수량 상한이 없어 int 범위를 넘는 곱셈이 음수로 뒤집혔고, 음수 금액이 그대로 승인되어 '
    '0원 청구로 상품 2,000개가 출고됐습니다. 정탐이며 직접적인 금전 손실이 발생한 사고입니다.',
    '오버플로우는 "이론적 위험"으로 치부되기 쉽습니다. 금액·수량·크기 계산에서는 실제 손실로 직결되며, 이 경우 PG 도 음수를 걸러내지 않았다는 점이 함께 드러났습니다.'),
  F(
   O('total 이 음수이면 주문을 거부한다', False,
     '$ curl -s -X POST https://app/order -d "itemId=8812&qty=2148"\n'
     '{"orderId":88922,"total":1999999999,"status":"APPROVED"}\n'
     '# 2,000,000 * 2148 = 4,296,000,000 → 오버플로우 후 양수로 착지\n'
     '>> 음수 검사를 우회하면서 실제와 다른 금액으로 승인',
     '오버플로우 결과가 항상 음수인 것은 아닙니다. 값을 검사하는 방식은 우회됩니다.'),
   O('수량 상한 검증 + 오버플로우를 예외로 만드는 연산 + 금액 타입 변경', True,
     '$ curl -s -X POST https://app/order -d "itemId=8812&qty=2000"\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"주문 수량은 1~999 입니다"}\n'
     '\n'
     'if (qty < 1 || qty > MAX_QTY) throw new InvalidQuantityException();\n'
     'long total = Math.multiplyExact((long) unitPrice, qty);   // 넘치면 ArithmeticException\n'
     '// 금액은 BigDecimal 로 보관 (통화 계산의 표준)\n'
     '\n'
     '$ ./pg-guard.sh --add "amount > 0"   >> PG 연동 구간에도 금액 검증 추가',
     '입력 상한으로 막고, 연산이 넘치면 조용히 뒤집히는 대신 예외가 나게 하고, 금액 타입 자체를 바꿉니다. 하류 시스템에도 검증을 넣어 이중으로 막습니다.'),
   O('int 를 long 으로 바꾼다', False,
     '$ curl -s -X POST https://app/order -d "itemId=8812&qty=9223372036854775"\n'
     '{"total":-2000000,"status":"APPROVED"}\n'
     '>> 범위만 넓어졌을 뿐 상한 검증이 없으면 동일 문제 재현',
     '타입을 넓히는 것은 시간을 벌 뿐입니다. 입력 상한 검증이 없으면 어떤 타입에서도 넘길 수 있습니다.'))),

# ───────────────────────────── 메모리 버퍼 오버플로우 ─────────────────────────────
S('bufferoverflow',
  T('운영팀 장애 보고', 'OPS-25188', '긴급', 'high',
    '금융 단말 연계 데몬이 특정 가맹점 전문 수신 시 비정상 종료됩니다.\n'
    '재시작 후에도 같은 전문이 오면 반복 종료됩니다.'),
  [
   E('💥', '크래시 분석', 'core dump',
     '$ dmesg | tail -2\n'
     'edid[4412]: segfault at 4141414141414141 ip 4141414141414141 sp 00007ffd... error 14\n'
     '\n'
     '$ gdb -c core.4412 ./edid -batch -ex "info registers rip" 2>/dev/null\n'
     'rip  0x4141414141414141   0x4141414141414141\n'
     '>> 명령 포인터가 0x41("A") 로 덮였음 — 반환주소 제어 가능 상태'),
   E('🔍', '해당 코드', 'edid.c',
     '$ sed -n \'142,149p\' src/edid.c\n'
     '  void parse_merchant(const char *packet) {\n'
     '      char name[64];\n'
     '      char addr[128];\n'
     '      strcpy(name, packet + 12);          /* 길이 검사 없음 */\n'
     '      sprintf(addr, "%s", packet + 76);   /* 길이 검사 없음 */\n'
     '      ...\n'
     '  }'),
   E('🛡️', '빌드 보호 옵션', '바이너리',
     '$ checksec --file=./edid\n'
     'RELRO      : Partial RELRO\n'
     'STACK CANARY : No canary found\n'
     'NX         : NX disabled\n'
     'PIE        : No PIE (0x400000)\n'
     '\n'
     '$ cat Makefile | grep CFLAGS\n'
     'CFLAGS = -O2 -w    # 경고 억제, 보호 옵션 없음'),
  ],
  V('true',
    '길이 검사 없는 문자열 복사로 스택 버퍼가 넘쳤고, 명령 포인터가 입력값으로 덮였습니다. '
    '스택 카나리·NX·PIE 가 모두 꺼져 있어 임의 코드 실행으로 이어지기 매우 쉬운 상태입니다. '
    '정탐이며 가용성 장애를 넘어 원격 코드 실행 가능성이 있는 최고 위험도 항목입니다.',
    'rip 가 입력값으로 덮였다는 것은 단순 크래시가 아니라 **제어 흐름 탈취가 가능하다**는 결정적 증거입니다. 크래시 로그에서 이 부분을 확인하면 위험도 판단이 달라집니다.'),
  F(
   O('버퍼 크기를 64에서 512로 늘린다', False,
     '$ ./fuzz.sh --field merchant_name --len 600\n'
     'edid[4489]: segfault at 4141414141414141\n'
     '>> 더 긴 입력으로 동일 재현',
     '버퍼를 키우는 것은 입력 길이를 조금 더 요구할 뿐입니다. 검사가 없으면 어떤 크기도 넘칠 수 있습니다.'),
   O('길이 제한 함수로 교체 + 입력 길이 검증 + 컴파일러 보호 옵션 활성화', True,
     '$ ./fuzz.sh --field merchant_name --len 600 --iterations 100000\n'
     '크래시 0건 / 거부 응답 100,000건\n'
     '\n'
     'if (strnlen(packet + 12, 64) >= sizeof(name)) return ERR_FIELD_TOO_LONG;\n'
     'snprintf(name, sizeof(name), "%s", packet + 12);\n'
     '\n'
     '$ checksec --file=./edid\n'
     'STACK CANARY : Canary found     NX : NX enabled     PIE : PIE enabled\n'
     '$ grep CFLAGS Makefile\n'
     'CFLAGS = -O2 -Wall -Wextra -Werror -D_FORTIFY_SOURCE=3 -fstack-protector-strong -fPIE -pie',
     '코드에서 길이를 검증하고, 안전한 함수로 바꾸고, 컴파일러·런타임 보호를 켭니다. 보호 옵션은 코드 실수가 남아 있을 때의 마지막 방어선입니다.'),
   O('데몬을 권한이 낮은 계정으로 실행한다', False,
     '$ ps -o user,comm -p $(pgrep edid)\n'
     'edidsvc  edid\n'
     '$ ./fuzz.sh --field merchant_name --len 600\n'
     'edid[4501]: segfault at 4141414141414141\n'
     '>> 크래시·제어흐름 탈취는 그대로. 영향 범위만 축소',
     '권한 축소는 침해 후 피해를 줄이는 유효한 보완통제이지만 취약점 자체는 남습니다. 함께 적용하되 조치로 갈음할 수 없습니다.'))),

# ───────────────────────────── 해제된 자원 사용 (Use-After-Free) ─────────────────────────────
S('use_after_free',
  T('운영팀 장애 보고', 'OPS-25201', '높음', 'high',
    '실시간 시세 배포 데몬이 하루 3~5회 비정상 종료됩니다.\n'
    '크래시 지점이 매번 달라 원인을 찾지 못하고 있습니다.'),
  [
   E('💥', '메모리 검사 도구 결과', 'ASan',
     '$ ./quoted -fsanitize=address < replay/session_88213.bin\n'
     '==4412==ERROR: AddressSanitizer: heap-use-after-free on address 0x60300000eff0\n'
     'READ of size 8 at 0x60300000eff0 thread T3\n'
     '    #0 session_broadcast quoted.c:288\n'
     'freed by thread T1 here:\n'
     '    #0 session_close quoted.c:214\n'
     'previously allocated by thread T1 here:\n'
     '    #0 session_open quoted.c:151'),
   E('🔍', '해당 코드', 'quoted.c',
     '$ sed -n \'210,218p\' src/quoted.c\n'
     '  void session_close(session_t *s) {\n'
     '      free(s->buf);\n'
     '      free(s);                    /* 포인터를 NULL 로 만들지 않음 */\n'
     '  }\n'
     '\n'
     '$ sed -n \'285,290p\' src/quoted.c\n'
     '  for (int i = 0; i < n_sess; i++) {\n'
     '      send(sessions[i]->fd, buf, len, 0);   /* 닫힌 세션이 배열에 남아 있음 */\n'
     '  }'),
   E('🧪', '재현 조건', '점검',
     '$ ./repro.sh --disconnect-during-broadcast --iterations 1000\n'
     '크래시 412회 / 힙 오염 후 정상 진행 588회\n'
     '\n'
     '$ ./repro.sh --heap-spray --disconnect-during-broadcast\n'
     '제어 포인터가 공격자 데이터로 치환됨 (4/1000)\n'
     '>> 클라이언트가 접속을 끊는 시점을 조절해 유발 가능'),
  ],
  V('true',
    '세션 해제 후에도 배열에 포인터가 남아 이미 해제된 메모리를 참조합니다. '
    '외부 클라이언트가 접속 종료 시점을 조절해 유발할 수 있고, 힙 스프레이와 결합하면 '
    '제어 포인터가 공격자 데이터로 치환되는 것까지 확인됐습니다. 정탐이며 원격 유발 가능한 고위험 항목입니다.',
    '"간헐적 크래시"로 접수되면 메모리 오염을 의심해야 합니다. 크래시 지점이 매번 다른 것이 오히려 메모리 오염의 특징입니다. ASan 같은 도구로 확인하기 전에는 원인을 단정할 수 없습니다.'),
  F(
   O('free 후 포인터에 NULL 을 대입한다', False,
     '$ ./quoted -fsanitize=address < replay/session_88213.bin\n'
     '==4489==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000000\n'
     '    #0 session_broadcast quoted.c:288\n'
     '>> 크래시는 여전. 배열에 남은 다른 참조는 NULL 이 아님',
     '지역 포인터를 NULL 로 만들어도 다른 곳에 복사된 참조는 그대로입니다. 소유권이 명확하지 않은 것이 원인입니다.'),
   O('소유권·수명을 명확히 하고(참조 카운트), 해제 시 컬렉션에서 먼저 제거한다', True,
     '$ ./quoted -fsanitize=address < replay/session_88213.bin\n'
     '(정상 종료, ASan 오류 0건)\n'
     '$ ./repro.sh --disconnect-during-broadcast --iterations 100000\n'
     '크래시 0건\n'
     '\n'
     'void session_close(session_t *s) {\n'
     '    sessions_remove(s);            /* 먼저 컬렉션에서 뺀다 */\n'
     '    if (--s->refcnt == 0) {        /* 사용 중인 스레드가 없을 때만 해제 */\n'
     '        free(s->buf); free(s);\n'
     '    }\n'
     '}\n'
     '$ cat .github/workflows/ci.yml | grep sanitize\n'
     '  - run: make test CFLAGS="-fsanitize=address,undefined"   # 회귀 방지',
     '누가 언제까지 이 메모리를 쓰는지를 코드가 명시적으로 관리해야 합니다. CI 에 메모리 검사 도구를 넣어 같은 결함이 다시 들어오지 못하게 막습니다.'),
   O('크래시 시 자동 재시작하도록 systemd 설정을 추가한다', False,
     '$ systemctl status quoted\n'
     'Active: active (running)  restarts: 118\n'
     '$ ./repro.sh --heap-spray --disconnect-during-broadcast\n'
     '>> 제어 포인터 치환 여전 — 재시작은 코드 실행 위험을 막지 못함',
     '가용성은 일부 회복되지만 메모리 오염을 이용한 공격은 그대로입니다. 증상만 가리면 원인 분석도 어려워집니다.'))),

# ───────────────────────────── 초기화되지 않은 변수 사용 ─────────────────────────────
S('uninitialized_variable',
  T('보안팀 정기 진단', 'SEC-1355', '중간', 'mid',
    '응답 전문에 의미를 알 수 없는 바이트가 섞여 나온다는 지적입니다.\n'
    '개발팀 회신: "패딩 영역이라 무시해도 되는 값입니다."'),
  [
   E('🔍', '응답 생성 코드', 'resp.c',
     '$ sed -n \'88,95p\' src/resp.c\n'
     '  void build_response(int code, char *out) {\n'
     '      resp_t r;                       /* 초기화 없음 */\n'
     '      r.code = code;\n'
     '      r.len  = 16;\n'
     '      /* r.reserved[32] 는 설정하지 않음 */\n'
     '      memcpy(out, &r, sizeof(r));     /* 구조체 전체를 그대로 전송 */\n'
     '  }'),
   E('🔬', '전송된 바이트 분석', '패킷 캡처',
     '$ tcpdump -r capture.pcap -X port 9443 | sed -n \'4,8p\'\n'
     '  0x0020:  0000 0010 5072 3064 2144 6223 3230 3236  ....Pr0d!Db#2026\n'
     '  0x0030:  0a53 4553 5349 4f4e 3d39 4632 4134 3145  .SESSION=9F2A41E\n'
     '  0x0040:  382e 2e2e 0000 0000 0000 0000 0000 0000  8.............\n'
     '\n'
     '>> "패딩"에 이전 요청 처리 때 스택에 남아 있던 DB 비밀번호와 세션 ID 가 담겨 있음'),
   E('📊', '노출 범위 측정', '점검',
     '$ ./leak-scan.sh --capture 10000 --pattern "SESSION=|password|Bearer"\n'
     '10,000개 응답 중 민감 문자열 포함: 1,284건 (12.8%)\n'
     '  타 사용자 세션 ID: 884건\n'
     '  내부 자격증명 단편: 400건'),
  ],
  V('true',
    '초기화하지 않은 스택 메모리가 그대로 전송되고 있습니다. "패딩"이 아니라 '
    '직전 처리에서 남은 데이터이며, 실제로 10,000개 응답 중 12.8% 에 타 사용자 세션 ID 와 '
    '내부 자격증명이 섞여 나갔습니다. 정탐이며 메모리 정보 노출입니다.',
    '"의미 없는 값"이라는 설명을 그대로 받아들이면 안 됩니다. 초기화되지 않은 메모리는 무작위가 아니라 **직전에 무엇이 있었는지**를 담고 있습니다. 실제 바이트를 열어 봐야 알 수 있습니다.'),
  F(
   O('reserved 영역을 응답에서 제외하고 전송 길이를 줄인다', False,
     '$ ./leak-scan.sh --capture 10000 --pattern "SESSION=|password"\n'
     '민감 문자열 포함: 402건 (4.0%)\n'
     '$ grep -rn "\\b\\(resp_t\\|req_t\\|hdr_t\\) [a-z]*;" src/ | grep -v "= *{0}" | wc -l\n'
     '14\n'
     '>> 다른 구조체 14곳에서 동일 패턴 지속',
     '한 구조체만 고치면 같은 패턴이 남습니다. 구조체를 통째로 전송하는 코드 전반을 봐야 합니다.'),
   O('구조체를 0으로 초기화하고, 컴파일러 경고를 오류로 승격한다', True,
     '$ ./leak-scan.sh --capture 100000 --pattern "SESSION=|password|Bearer"\n'
     '민감 문자열 포함: 0건\n'
     '\n'
     'resp_t r = {0};              /* 전체 0 초기화 */\n'
     'r.code = code; r.len = 16;\n'
     '\n'
     '$ make CFLAGS="-Wall -Wextra -Werror -Wuninitialized -ftrivial-auto-var-init=zero"\n'
     '>> 동일 패턴 14곳 전부 빌드 단계에서 검출·수정\n'
     '$ valgrind --track-origins=yes ./resp_test   →  0 errors',
     '초기화를 기본값으로 만들고 컴파일러가 강제하게 합니다. 사람이 매번 기억하는 방식은 규모가 커지면 실패합니다.'),
   O('응답 구간을 TLS 로 암호화한다', False,
     '$ ./leak-scan.sh --at-application-layer --capture 10000\n'
     '민감 문자열 포함: 1,284건\n'
     '>> 전송 구간은 보호되지만 수신 측 애플리케이션에는 그대로 도달',
     'TLS 는 중간자만 막습니다. 정당한 수신자(다른 사용자·연계 기관)에게 남의 세션 ID 가 그대로 전달되는 문제는 남습니다.'))),

# ───────────────────────────── 부적절한 자원 해제 ─────────────────────────────
S('improper_resource_release',
  T('운영팀 장애 보고', 'OPS-25219', '높음', 'high',
    '배포 후 6~8시간이 지나면 서버가 응답하지 않습니다. 재시작하면 정상으로 돌아옵니다.\n'
    '매일 새벽 예약 재시작으로 버티는 중입니다.'),
  [
   E('📊', '자원 사용 추이', '모니터링',
     '$ ./metric.sh --host app-prod-01 --metric db_pool_active --window 8h\n'
     '00:00  2 / 50\n'
     '02:00 14 / 50\n'
     '04:00 31 / 50\n'
     '06:00 49 / 50\n'
     '06:40 50 / 50   >> 고갈, 이후 모든 요청 대기\n'
     '\n'
     '$ lsof -p 3182 | wc -l\n'
     '9,842   (한도 10,240)'),
   E('🔍', '해당 코드', 'ReportDao.java',
     '$ sed -n \'44,54p\' src/main/java/report/ReportDao.java\n'
     '  public List<Row> find(String q) {\n'
     '      Connection con = ds.getConnection();\n'
     '      PreparedStatement ps = con.prepareStatement(SQL);\n'
     '      ps.setString(1, q);\n'
     '      ResultSet rs = ps.executeQuery();\n'
     '      List<Row> rows = map(rs);\n'
     '      con.close();                  // 정상 경로에서만 닫힘\n'
     '      return rows;\n'
     '  }                                 // 예외 발생 시 커넥션 누수'),
   E('📜', '예외 발생 빈도', 'error.log',
     '$ grep -c "ReportDao.find" /var/log/app/error.log\n'
     '1,284\n'
     '$ grep "ReportDao.find" /var/log/app/error.log | grep -oP \'\\w+Exception\' | sort | uniq -c\n'
     '   884 SQLTimeoutException\n'
     '   400 DataIntegrityViolationException\n'
     '\n'
     '>> 예외 1건당 커넥션 1개 누수 — 발생 빈도와 고갈 속도가 일치'),
  ],
  V('true',
    '예외 경로에서 커넥션이 반환되지 않아 누적 누수가 발생합니다. '
    '예외 발생 빈도와 풀 고갈 속도가 정확히 일치하며, 6~8시간마다 전체 서비스가 멈춥니다. '
    '외부에서 타임아웃을 유발하는 질의를 반복하면 의도적으로 고갈시킬 수 있어 가용성 공격 경로이기도 합니다. 정탐입니다.',
    '"매일 재시작으로 버틴다"는 운영 방식이 굳어지면 아무도 이것을 결함으로 보지 않게 됩니다. 재시작으로 해결되는 증상은 대부분 자원 누수입니다.'),
  F(
   O('커넥션 풀 크기를 50에서 200으로 늘린다', False,
     '$ ./metric.sh --metric db_pool_active --window 30h\n'
     '28:00  200 / 200   >> 고갈 시점이 6시간에서 28시간으로 늦춰졌을 뿐\n'
     '$ ./metric.sh --metric db_server_connections\n'
     'DB 서버 최대 연결 수 초과 — 다른 서비스까지 영향',
     '누수가 있으면 용량을 늘려도 시간을 벌 뿐이고, 오히려 DB 서버 전체에 부담을 줍니다.'),
   O('try-with-resources 로 반환을 보장하고, 누수 감지를 모니터링에 넣는다', True,
     '$ ./metric.sh --host app-prod-01 --metric db_pool_active --window 72h\n'
     'max 12 / 50   (72시간 무재시작 운영)\n'
     '\n'
     'try (Connection con = ds.getConnection();\n'
     '     PreparedStatement ps = con.prepareStatement(SQL)) {\n'
     '    ps.setString(1, q);\n'
     '    try (ResultSet rs = ps.executeQuery()) { return map(rs); }\n'
     '}   // 예외가 나도 역순으로 반드시 닫힌다\n'
     '\n'
     '$ grep -rn "getConnection()" src/ | grep -v "try (" | wc -l  →  0\n'
     '$ ./hikari-config.sh --leak-detection-threshold 5000   >> 누수 시 스택트레이스 경고',
     '언어가 제공하는 자동 반환 구문을 쓰면 예외 경로를 빠뜨릴 수 없습니다. 풀의 누수 감지 기능을 켜 두면 재발 시 즉시 원인 지점이 로그에 남습니다.'),
   O('새벽 예약 재시작 주기를 6시간마다로 단축한다', False,
     '$ ./metric.sh --metric availability --window 7d\n'
     '재시작 중 요청 실패 4,128건 · 가용성 99.2% → 98.1%\n'
     '>> 누수는 그대로, 재시작 자체가 장애 요인이 됨',
     '재시작으로 버티는 것은 운영 부담과 장애 위험만 키웁니다. 원인을 고치는 것보다 비싼 대응입니다.'))),

# ───────────────────────────── Public 메서드의 Private 배열 반환 ─────────────────────────────
S('private_array_return',
  T('SAST 스캐너 리포트', 'SONAR-3612', '낮음', 'low',
    '내부 배열을 그대로 반환하는 메서드 2곳이 지적됐습니다.\n'
    '개발팀 회신: "내부에서만 쓰는 클래스라 문제없습니다."'),
  [
   E('🔍', '지적된 2곳', '소스',
     '$ sed -n \'18,22p\' src/main/java/crypto/KeyHolder.java\n'
     '  private byte[] masterKey;\n'
     '  public byte[] getMasterKey() { return masterKey; }      // 원본 반환\n'
     '\n'
     '$ sed -n \'31,34p\' src/main/java/report/ColumnSpec.java\n'
     '  private String[] columns;\n'
     '  public String[] getColumns() { return columns; }        // 원본 반환'),
   E('🧪', '변조 재현', '점검',
     '$ cat KeyLeakTest.java\n'
     'byte[] k = keyHolder.getMasterKey();\n'
     'System.out.println(Hex.encode(k));      // 키 값 노출\n'
     'Arrays.fill(k, (byte) 0);               // 원본이 0으로 덮임\n'
     'System.out.println(keyHolder.canDecrypt());\n'
     '\n'
     '$ java KeyLeakTest\n'
     '9a2c41e8b7d3...\n'
     'false        >> 외부에서 키를 읽고, 지워버릴 수도 있음'),
   E('🌐', '호출 경로 확인', '소스',
     '$ grep -rn "getMasterKey()" src/ --include=*.java\n'
     'crypto/CipherService.java:44   (내부)\n'
     'plugin/PluginApi.java:112      return keyHolder.getMasterKey();   // 플러그인에 노출\n'
     '\n'
     '$ grep -rn "PluginApi" src/main/java/plugin/PluginLoader.java\n'
     'PluginLoader.java:28   외부 JAR 을 런타임에 로드해 PluginApi 를 전달\n'
     '>> 서드파티 플러그인이 마스터 키에 접근 가능'),
  ],
  V('true',
    'ColumnSpec 쪽은 영향이 작지만, KeyHolder 는 마스터 키 배열을 그대로 반환하고 '
    '그 경로가 서드파티 플러그인 API 까지 열려 있습니다. 플러그인이 키를 읽는 것도, '
    '원본을 지워 복호화를 못 하게 만드는 것도 가능합니다. 위험도를 "낮음"에서 상향해야 하는 정탐입니다.',
    '이 항목은 스캐너가 기계적으로 "낮음"을 매기는 대표적인 유형입니다. **무엇을 담은 배열인지, 누가 그 메서드를 호출할 수 있는지**에 따라 등급이 완전히 달라집니다.'),
  F(
   O('메서드를 package-private 으로 바꾼다', False,
     '$ javac PluginApi.java\n'
     '>> 컴파일 오류 — 플러그인 기능이 동작하지 않음\n'
     '(개발팀) "플러그인에서 암복호화를 해야 해서 필요합니다."',
     '접근 제어자만 좁히면 기능이 깨집니다. 플러그인이 정말 키 자체를 필요로 하는지부터 다시 봐야 합니다.'),
   O('키를 노출하지 않고 암복호화 연산만 제공하도록 인터페이스를 바꾼다', True,
     '$ java KeyLeakTest\n'
     '>> 컴파일 오류: getMasterKey() 제거됨\n'
     '\n'
     '// 키를 주는 대신 연산을 해 준다\n'
     'public byte[] encrypt(byte[] plain) { ... }\n'
     'public byte[] decrypt(byte[] cipher) { ... }\n'
     '\n'
     '// 값 객체는 방어적 복사\n'
     'public String[] getColumns() { return columns.clone(); }\n'
     '$ ./plugin-test.sh   >> 플러그인 기능 정상 · 키 접근 불가',
     '비밀은 건네주지 말고 그것으로 하는 일을 대신해 주면 됩니다. 단순 값 객체는 방어적 복사로 충분합니다.'),
   O('반환 전에 배열을 복사해서 준다', False,
     '$ java KeyLeakTest\n'
     '9a2c41e8b7d3...\n'
     '>> 원본 변조는 막혔지만 키 값은 여전히 읽힘',
     '방어적 복사는 ColumnSpec 같은 값 객체에는 정답이지만, 비밀 키에는 부족합니다. 읽히는 것 자체가 문제이기 때문입니다.'))),

# ───────────────────────────── Private 배열에 Public 데이터 할당 ─────────────────────────────
S('public_to_private_array',
  T('보안팀 정기 진단', 'SEC-1372', '중간', 'mid',
    '외부에서 받은 배열을 내부 필드에 그대로 저장하는 코드가 지적됐습니다.\n'
    '대상은 접근 제어 목록을 다루는 클래스입니다.'),
  [
   E('🔍', '해당 코드', 'AccessPolicy.java',
     '$ sed -n \'14,21p\' src/main/java/auth/AccessPolicy.java\n'
     '  private String[] allowedRoles;\n'
     '\n'
     '  public AccessPolicy(String[] roles) {\n'
     '      this.allowedRoles = roles;         // 외부 배열 참조를 그대로 보관\n'
     '  }\n'
     '  public boolean permits(String role) {\n'
     '      return Arrays.asList(allowedRoles).contains(role);\n'
     '  }'),
   E('🧪', '변조 재현', '점검',
     '$ cat PolicyTest.java\n'
     'String[] roles = {"ADMIN"};\n'
     'AccessPolicy p = new AccessPolicy(roles);\n'
     'System.out.println(p.permits("USER"));     // false 기대\n'
     'roles[0] = "USER";                         // 호출자가 원본을 수정\n'
     'System.out.println(p.permits("USER"));\n'
     '\n'
     '$ java PolicyTest\n'
     'false\n'
     'true         >> 정책 생성 후에도 외부에서 정책을 바꿀 수 있음'),
   E('🌐', '실제 사용 경로', '소스',
     '$ grep -rn "new AccessPolicy" src/ --include=*.java\n'
     'config/PolicyLoader.java:38   new AccessPolicy(cfg.getRoles())\n'
     '\n'
     '$ sed -n \'34,40p\' src/main/java/config/PolicyLoader.java\n'
     '  String[] shared = cfg.getRoles();        // 설정 객체의 내부 배열\n'
     '  policies.put(path, new AccessPolicy(shared));\n'
     '  // 같은 배열이 여러 정책에 공유되고, 설정 리로드 시 내용이 바뀜\n'
     '\n'
     '$ grep -rn "reload()" src/main/java/config/ConfigWatcher.java\n'
     'ConfigWatcher.java:52   cfg.getRoles()[i] = newValue;   // 리로드 시 제자리 수정'),
  ],
  V('true',
    '외부 배열 참조를 그대로 보관해 정책 객체가 불변이 아닙니다. '
    '실제로 설정 리로드가 같은 배열을 제자리에서 수정하고 있어, 리로드 시점에 '
    '여러 경로의 접근 정책이 의도치 않게 함께 바뀝니다. 접근 통제의 정확성이 깨지므로 정탐입니다.',
    '이 유형은 "이론적 결함"으로 넘기기 쉽습니다. **그 배열이 어디서 오는지 호출부를 따라가 보면** 실제로 공유·변경되는 경우가 드물지 않습니다. 보안 결정에 쓰이는 데이터라면 등급이 올라갑니다.'),
  F(
   O('생성자 파라미터에 final 을 붙인다', False,
     '$ java PolicyTest\n'
     'false\n'
     'true\n'
     '>> final 은 참조 재할당만 막고 배열 내용 변경은 막지 못함',
     'final 배열은 "다른 배열을 가리킬 수 없다"는 뜻이지 "내용이 바뀌지 않는다"는 뜻이 아닙니다. 흔한 오해입니다.'),
   O('생성 시 복사해 보관하고 불변 컬렉션으로 바꾼다', True,
     '$ java PolicyTest\n'
     'false\n'
     'false        >> 외부에서 원본을 바꿔도 정책은 그대로\n'
     '\n'
     'private final Set<String> allowedRoles;\n'
     'public AccessPolicy(String[] roles) {\n'
     '    this.allowedRoles = Set.copyOf(Arrays.asList(roles));   // 복사 + 불변\n'
     '}\n'
     '$ ./policy-test.sh --reload-during-request\n'
     '>> 리로드 중 요청 1,000건 — 정책 교차 적용 0건 (교체는 객체 단위로만)',
     '경계에서 복사하고 불변으로 만들면 이후 어떤 외부 변경에도 영향받지 않습니다. 정책 갱신은 객체를 통째로 교체하는 방식이 안전합니다.'),
   O('설정 리로드 시 배열을 제자리 수정하지 않도록 PolicyLoader 를 고친다', False,
     '$ java PolicyTest\n'
     'false\n'
     'true\n'
     '>> 현재 호출부는 안전해지지만 AccessPolicy 자체는 여전히 외부 변경에 노출',
     '호출부를 고치는 것도 필요하지만, 클래스가 스스로를 보호하지 않으면 새 호출부가 추가될 때 같은 문제가 반복됩니다.'))),

# ───────────────────────────── 제거되지 않은 디버그 코드 ─────────────────────────────
S('debug_code',
  T('외부 제보', 'EXT-2026-14', '높음', 'high',
    '"URL 뒤에 특정 파라미터를 붙이면 디버그 정보가 나온다"는 제보를 받았습니다.'),
  [
   E('💻', '제보 내용 확인', '점검 서버',
     "$ curl -s 'https://app/main?debug=1' | head -8\n"
     '=== DEBUG MODE ===\n'
     'session: {userId=kim, role=USER, token=eyJhbGciOiJIUzI1NiIs...}\n'
     'datasource: jdbc:mysql://10.0.9.12:3306/appdb (user=appsvc)\n'
     'cache: redis://10.0.9.30:6379\n'
     'build: 2026.09.10-rc3 (commit 9e14b7f)'),
   E('🔍', '디버그 코드 전수', '소스',
     '$ grep -rn "debug\\|DEBUG\\|isDev\\|TEST_MODE" src/main/java/ --include=*.java | grep -v "log\\." | head -5\n'
     'common/DebugFilter.java:22   if ("1".equals(req.getParameter("debug"))) { dumpContext(resp); }\n'
     'auth/LoginController.java:88 if ("1".equals(req.getParameter("skipOtp"))) { return success(); }\n'
     'pay/PayController.java:141   if (TEST_MODE) { return approve(amount); }   // 결제 승인 우회\n'
     '\n'
     '$ grep -rn "TEST_MODE *=" src/\n'
     'pay/PayController.java:31   private static final boolean TEST_MODE = true;'),
   E('🧪', '위험 경로 재현', '점검 서버',
     "$ curl -s -X POST 'https://app/login?skipOtp=1' -d 'id=admin&pw=wrong'\n"
     '{\"result\":\"success\",\"role\":\"ADMIN\"}\n'
     '>> OTP 는 물론 비밀번호 검증까지 우회됨\n'
     '\n'
     "$ curl -s -X POST 'https://app/pay' -d 'orderId=88213&amount=1980000'\n"
     '{"status":"APPROVED","pgTxId":"TEST-000000"}\n'
     '>> 실제 결제 없이 승인 처리'),
  ],
  V('true',
    '제보된 debug 파라미터는 시작에 불과합니다. 전수 검색에서 OTP·비밀번호 검증을 우회하는 '
    'skipOtp 파라미터와, 실제 결제 없이 승인 처리하는 TEST_MODE 상수가 운영 코드에서 발견됐습니다. '
    '관리자 로그인과 무료 결제가 모두 재현됐습니다. 정탐이며 최고 위험도입니다.',
    '제보는 대개 빙산의 일각입니다. 제보된 한 지점만 확인하고 닫지 말고, **같은 성격의 코드를 전수 검색**해야 합니다. 여기서도 실제 심각한 것은 제보되지 않은 쪽이었습니다.'),
  F(
   O('debug 파라미터 처리 코드를 삭제한다', False,
     "$ curl -s -X POST 'https://app/login?skipOtp=1' -d 'id=admin&pw=wrong'\n"
     '{"result":"success","role":"ADMIN"}\n'
     '>> 제보된 것만 고쳐 더 위험한 경로가 그대로 남음',
     '제보 내용만 대응하면 진짜 문제를 놓칩니다. 전수 점검이 빠진 조치입니다.'),
   O('디버그·테스트 코드를 전수 제거하고, 빌드·CI 에서 차단한다', True,
     "$ curl -s 'https://app/main?debug=1' | head -2\n"
     '(디버그 출력 없음 — 정상 페이지)\n'
     "$ curl -s -X POST 'https://app/login?skipOtp=1' -d 'id=admin&pw=wrong'\n"
     '{"error":"인증 실패"}\n'
     "$ curl -s -X POST 'https://app/pay' -d 'orderId=88213&amount=1980000'\n"
     '{"error":"결제 요청이 유효하지 않습니다"}\n'
     '\n'
     '$ grep -rn "skipOtp\\|TEST_MODE\\|debug=" src/ | wc -l  →  0\n'
     '$ cat .github/workflows/ci.yml | grep -A1 forbidden-pattern\n'
     '  - run: ./scripts/check-debug-code.sh   # 패턴 발견 시 빌드 실패\n'
     '$ ./iam-admin.sh audit --since 2024-03   >> 우회 로그인 이력 조사 의뢰',
     '전수 제거하고 CI 에서 기계적으로 막습니다. 이미 악용됐을 수 있으므로 과거 로그 조사도 함께 진행해야 합니다.'),
   O('디버그 기능을 관리자 권한에서만 동작하도록 바꾼다', False,
     "$ curl -s -X POST 'https://app/login?skipOtp=1' -d 'id=admin&pw=wrong'\n"
     '{"result":"success","role":"ADMIN"}\n'
     '>> 권한 검사를 우회하는 코드 자체에 권한 검사를 붙이는 모순',
     '인증을 우회하는 코드에 인증을 걸 수는 없습니다. 운영 빌드에는 존재하지 않아야 합니다.'))),

# ───────────────────────────── 취약한 API 사용 ─────────────────────────────
S('vulnerable_api',
  T('정적 분석 리포트', 'SONAR-3644', '중간', 'mid',
    '사용 금지 API 사용 8건이 지적됐습니다.\n'
    '개발팀 회신: "폐기 예정(deprecated) 경고일 뿐이고 동작에는 문제없습니다."'),
  [
   E('🔍', '지적된 8건 분류', '소스',
     '$ ./api-scan.sh --rule deprecated-and-unsafe\n'
     'Runtime.exec(String)            pay/BatchRunner.java:51      [셸 해석 · 명령 주입 위험]\n'
     'Thread.stop()                   job/Worker.java:88           [자원 정리 없이 중단]\n'
     'SimpleDateFormat (static 공유)   util/DateUtil.java:14        [스레드 안전하지 않음]\n'
     'new Random()                    auth/OtpService.java:22      [예측 가능 난수]\n'
     'URLDecoder.decode(String)       web/ParamUtil.java:33        [기본 인코딩 의존]\n'
     'Class.forName(String) (외부입력) plugin/Loader.java:41        [임의 클래스 로드]\n'
     'System.gc()                     report/Exporter.java:77      [성능 영향만]\n'
     'Date.getYear()                  legacy/Old.java:12           [동작만 폐기예정]'),
   E('🧪', '위험 항목 재현', '점검 서버',
     "$ curl -s -X POST https://app/batch/run -d 'name=daily;id'\n"
     'uid=1000(appsvc) gid=1000(appsvc)\n'
     '>> Runtime.exec(String) 이 셸을 거쳐 명령 주입 성립\n'
     '\n'
     '$ ./otp-predict.sh --target kim\n'
     '시드 후보 200개 생성 → 14회 시도 만에 OTP 적중\n'
     '>> new Random() 기반 OTP 예측 성공'),
   E('🧵', '동시성 항목 재현', '점검',
     '$ ./concurrent-test.sh --target DateUtil.format --threads 50\n'
     '잘못된 날짜 출력 412건 / 예외 88건 (NumberFormatException)\n'
     '>> static SimpleDateFormat 공유로 데이터 오염\n'
     '\n'
     '$ ./job-kill-test.sh\n'
     'Thread.stop() 호출 후 DB 커넥션 미반환 3건 · 파일 락 잔존 1건'),
  ],
  V('true',
    '8건을 같은 등급으로 볼 수 없습니다. System.gc()·Date.getYear() 는 성능·폐기예정 이슈로 보안과 무관하지만, '
    'Runtime.exec(String) 은 명령 주입이 실제 재현됐고 new Random() 기반 OTP 는 14회 만에 예측됐습니다. '
    '"동작에는 문제없다"는 반론은 성립하지 않습니다. 보안 영향이 있는 4건에 대해 정탐입니다.',
    '"deprecated 경고일 뿐"이라는 반론이 가장 흔한 유형입니다. **폐기예정(deprecated)과 안전하지 않음(unsafe)은 다른 개념**이고, 한 리포트에 섞여 올라옵니다. 건별로 재현해 봐야 구분됩니다.'),
  F(
   O('8건 모두 대체 API 로 일괄 교체한다', False,
     '$ ./gradlew test\n'
     'legacy/OldTest: 12 FAILED  (Date API 변경으로 회귀)\n'
     'report/ExporterTest: 3 FAILED\n'
     '>> 보안과 무관한 항목까지 건드려 회귀 발생. 릴리스 지연',
     '일괄 교체는 위험도가 낮은 항목에서 불필요한 회귀를 만듭니다. 우선순위를 나누는 것이 진단원의 역할입니다.'),
   O('보안 영향 기준으로 분류해 우선순위를 나누고, 위험 항목부터 조치한다', True,
     '$ cat findings/SONAR-3644.md\n'
     '[긴급] Runtime.exec(String) → ProcessBuilder(List) · 명령주입 재현됨\n'
     '[긴급] new Random() (OTP)  → SecureRandom · 예측 재현됨\n'
     '[높음] SimpleDateFormat    → DateTimeFormatter · 동시성 오염 재현됨\n'
     '[높음] Thread.stop()       → 인터럽트 기반 종료 · 자원 누수 확인\n'
     '[중간] Class.forName(외부입력) → 허용 클래스 화이트리스트\n'
     '[낮음] URLDecoder(String)  → 인코딩 명시 (기능 이슈)\n'
     '[정보] System.gc(), Date.getYear() → 보안 무관. 기술부채 백로그로 이관\n'
     '\n'
     "$ curl -s -X POST https://app/batch/run -d 'name=daily;id'\n"
     'HTTP/1.1 400 {"error":"허용되지 않은 배치명"}\n'
     '$ ./otp-predict.sh --target kim   →  200회 시도, 적중 0회',
     '한 리포트를 보안 영향 기준으로 쪼개 우선순위를 매깁니다. 보안과 무관한 항목은 기술부채로 넘기는 것도 정확한 판정입니다.'),
   O('정적 분석 규칙에서 해당 항목들을 예외 처리한다', False,
     '$ sonar-cli rule disable java:S1874\n'
     '(3개월 뒤, 신규 코드)\n'
     '$ grep -rn "Runtime.exec(\\|new Random()" src/ | wc -l\n'
     '14\n'
     '>> 규칙을 끄자 같은 패턴이 계속 유입',
     '노이즈를 줄이려고 규칙을 끄면 진짜 위험까지 안 보이게 됩니다. 규칙은 유지하고 건별로 정탐/오탐을 판정하는 편이 맞습니다.'))),

])
