/* academy-data-ai.js - "AI가 짠 코드" 과제 (AI 개편안 Track D)
 *
 * 왜 따로 두는가
 *   코드 생성 도구는 동작하는 코드를 빠르게 준다. 안전한 코드를 준다고는
 *   약속하지 않는다. 여기 담긴 10개는 실제로 생성 도구가 자주 내놓는 모양이다.
 *   요청 문장(aiPrompt)을 함께 적어 두어, 무엇을 시켰을 때 이런 코드가
 *   나오는지 학습자가 보게 했다.
 *
 * 기존 커리큘럼과 어떻게 엮이는가
 *   스키마는 ACADEMY_DATA.PRACTICAL 과 같다. cwe 와 weaknessName 을 그대로 쓰므로
 *   KISA 49개 보안약점, 진단원 시험 범위와 자동으로 연결된다.
 *   tags: ['ai-generated'] 로 표시해 코드 수정 실습에서 따로 골라 볼 수 있다.
 *
 * 채점은 js/codefix-grader.js 가 한다.
 *   safeCodeKeywords 는 "고친 코드에 반드시 있어야 하는 것",
 *   위험 토큰 제거는 취약 코드에 있고 안전 코드에 없는 토큰으로 자동 판정한다.
 *   그래서 safeCode 를 정확히 써 두는 것이 채점 품질을 결정한다.
 */
(function (global) {
  'use strict';

  var AI_PRACTICAL = [
    /* ------------------------------------------------------------------ 1 */
    {
      id: 'AID-01', lang: 'Python', cat: '입력검증', diff: '하',
      tags: ['ai-generated'],
      aiPrompt: '"사용자 이름으로 주문 내역을 찾는 함수 만들어줘"',
      title: 'AI 생성: 주문 조회 함수',
      weaknessName: 'SQL 삽입', cwe: 'CWE-89',
      isTruePositive: true,
      code:
        'def find_orders(conn, username):\n' +
        '    sql = f"SELECT id, total FROM orders WHERE user = \'{username}\'"\n' +
        '    cur = conn.cursor()\n' +
        '    cur.execute(sql)\n' +
        '    return cur.fetchall()',
      reasonKeywords: ['f-string', '문자열 결합', '외부 입력', '바인딩 미사용'],
      negKw: ['XSS', '안전한 코드', '취약하지 않', '오탐'],
      safeCode:
        'def find_orders(conn, username):\n' +
        '    sql = "SELECT id, total FROM orders WHERE user = ?"\n' +
        '    cur = conn.cursor()\n' +
        '    cur.execute(sql, (username,))\n' +
        '    return cur.fetchall()',
      safeCodeKeywords: ['?', 'execute(sql, ('],
      explanation:
        '생성 도구는 f-string 으로 질의를 조립하는 형태를 특히 자주 내놓습니다. 읽기 좋아 보이지만 ' +
        '값과 구문이 같은 문자열에서 섞이므로, username 에 따옴표가 들어오는 순간 질의 구조가 바뀝니다. ' +
        '값을 인자로 넘겨 드라이버가 구문과 분리하도록 합니다.'
    },

    /* ------------------------------------------------------------------ 2 */
    {
      id: 'AID-02', lang: 'Python', cat: '보안기능', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"비밀번호 재설정 토큰 생성해주는 코드"',
      title: 'AI 생성: 비밀번호 재설정 토큰',
      weaknessName: '취약한 난수 사용', cwe: 'CWE-330',
      isTruePositive: true,
      code:
        'import random, string\n\n' +
        'def make_reset_token(length=16):\n' +
        '    chars = string.ascii_letters + string.digits\n' +
        '    return "".join(random.choice(chars) for _ in range(length))',
      reasonKeywords: ['random 모듈', '예측 가능', '시드', '보안 목적'],
      negKw: ['안전한 난수', '취약하지 않', '오탐'],
      safeCode:
        'import secrets\n\n' +
        'def make_reset_token(length=32):\n' +
        '    return secrets.token_urlsafe(length)',
      safeCodeKeywords: ['secrets'],
      explanation:
        'random 모듈은 재현 가능한 의사난수 생성기입니다. 시뮬레이션에는 알맞지만 보안 토큰에는 쓰면 안 됩니다. ' +
        '내부 상태를 몇 개의 출력만으로 복원할 수 있어, 남의 재설정 링크를 예측하는 일이 가능해집니다. ' +
        'Python 은 secrets, Java 는 SecureRandom, 브라우저는 crypto.getRandomValues 를 씁니다.'
    },

    /* ------------------------------------------------------------------ 3 */
    {
      id: 'AID-03', lang: 'Java', cat: '에러처리', diff: '하',
      tags: ['ai-generated'],
      aiPrompt: '"로그인 실패 원인을 알 수 있게 로그 좀 자세히 남겨줘"',
      title: 'AI 생성: 로그인 디버그 로그',
      weaknessName: '민감정보 로그 노출', cwe: 'CWE-532',
      isTruePositive: true,
      code:
        'public User login(String userId, String password) {\n' +
        '    log.info("login attempt userId=" + userId + " password=" + password);\n' +
        '    User u = repo.findByUserId(userId);\n' +
        '    if (u == null || !u.getPasswordHash().equals(hash(password))) {\n' +
        '        log.warn("login failed, stored hash=" + u.getPasswordHash());\n' +
        '        return null;\n' +
        '    }\n' +
        '    return u;\n' +
        '}',
      reasonKeywords: ['비밀번호 로그', '해시 노출', '민감정보', '로그 수집'],
      negKw: ['안전한 로깅', '취약하지 않', '오탐'],
      safeCode:
        'public User login(String userId, String password) {\n' +
        '    log.info("login attempt userId={}", mask(userId));\n' +
        '    User u = repo.findByUserId(userId);\n' +
        '    if (u == null || !u.getPasswordHash().equals(hash(password))) {\n' +
        '        log.warn("login failed userId={}", mask(userId));\n' +
        '        return null;\n' +
        '    }\n' +
        '    return u;\n' +
        '}',
      safeCodeKeywords: ['mask'],
      explanation:
        '"자세히 남겨줘" 라는 요청에 생성 도구는 변수 값을 그대로 찍는 코드를 내놓습니다. ' +
        '로그는 보통 평문으로 오래 보관되고 운영자 여러 명이 보며 외부 수집 도구로도 나갑니다. ' +
        '비밀번호는 물론이고 저장된 해시도 로그에 남기지 않습니다. 식별자는 마스킹하고, ' +
        'null 검사보다 로그가 먼저 나가는 순서 문제도 함께 고쳐야 합니다.'
    },

    /* ------------------------------------------------------------------ 4 */
    {
      id: 'AID-04', lang: 'Python', cat: '보안기능', diff: '하',
      tags: ['ai-generated'],
      aiPrompt: '"결제 API 호출하는 클라이언트 코드 만들어줘. 바로 돌아가게 해줘"',
      title: 'AI 생성: 결제 API 클라이언트',
      weaknessName: '하드코딩된 중요정보', cwe: 'CWE-798',
      isTruePositive: true,
      code:
        'import requests\n\n' +
        // 실존 결제사의 키 형식을 쓰지 않는다. 시크릿 스캐너가 진짜 유출로 오인해
        // 푸시를 막고, 무엇보다 실존 상표를 모의 소품으로 쓰지 않는다는 규칙에 어긋난다.
        'API_KEY = "paylive_EXAMPLE_ONLY_DO_NOT_USE_0000000000"\n\n' +
        'def charge(amount, token):\n' +
        '    return requests.post(\n' +
        '        "https://pay.example.com/v1/charges",\n' +
        '        headers={"Authorization": "Bearer " + API_KEY},\n' +
        '        json={"amount": amount, "source": token},\n' +
        '    )',
      reasonKeywords: ['하드코딩', '소스에 키', '형상관리 유출', '폐기 필요'],
      negKw: ['환경 변수', '취약하지 않', '오탐'],
      safeCode:
        'import os\n' +
        'import requests\n\n' +
        'API_KEY = os.environ["PAY_API_KEY"]\n\n' +
        'def charge(amount, token):\n' +
        '    return requests.post(\n' +
        '        "https://pay.example.com/v1/charges",\n' +
        '        headers={"Authorization": "Bearer " + API_KEY},\n' +
        '        json={"amount": amount, "source": token},\n' +
        '    )',
      safeCodeKeywords: ['os.environ'],
      explanation:
        '"바로 돌아가게" 라는 요청이 붙으면 생성 도구는 설정을 상수로 박아 넣는 쪽을 고릅니다. ' +
        '이 코드가 형상관리에 한 번 올라가면 키는 기록에 영구히 남고, 나중에 지워도 되돌릴 수 없습니다. ' +
        '환경 변수나 비밀 관리 서비스에서 읽고, 이미 커밋된 키는 반드시 폐기하고 재발급합니다.'
    },

    /* ------------------------------------------------------------------ 5 */
    {
      id: 'AID-05', lang: 'Java', cat: '입력검증', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"첨부파일 내려받는 엔드포인트 구현해줘"',
      title: 'AI 생성: 첨부파일 다운로드',
      weaknessName: '경로 조작', cwe: 'CWE-22',
      isTruePositive: true,
      code:
        'public void download(HttpServletRequest req, HttpServletResponse res) throws IOException {\n' +
        '    String name = req.getParameter("file");\n' +
        '    File f = new File("/var/app/uploads/" + name);\n' +
        '    Files.copy(f.toPath(), res.getOutputStream());\n' +
        '}',
      reasonKeywords: ['경로 결합', '상위 디렉터리', '정규화 없음', '기준 경로 검사'],
      negKw: ['안전한 경로', '취약하지 않', '오탐'],
      safeCode:
        'private static final Path BASE = Paths.get("/var/app/uploads").toAbsolutePath().normalize();\n\n' +
        'public void download(HttpServletRequest req, HttpServletResponse res) throws IOException {\n' +
        '    String name = req.getParameter("file");\n' +
        '    Path target = BASE.resolve(name).normalize();\n' +
        '    if (!target.startsWith(BASE)) {\n' +
        '        res.sendError(HttpServletResponse.SC_BAD_REQUEST);\n' +
        '        return;\n' +
        '    }\n' +
        '    Files.copy(target, res.getOutputStream());\n' +
        '}',
      safeCodeKeywords: ['normalize', 'startsWith'],
      explanation:
        '기준 디렉터리에 입력을 이어 붙이는 모양은 생성 도구가 가장 자주 내놓는 파일 접근 코드입니다. ' +
        'name 에 ../../etc/passwd 가 들어오면 기준을 벗어납니다. ' +
        '정규화한 뒤 결과가 여전히 기준 경로 아래인지 확인하는 두 단계가 모두 있어야 합니다. ' +
        '더 안전한 쪽은 파일명을 직접 받지 않고 식별자로 조회하는 설계입니다.'
    },

    /* ------------------------------------------------------------------ 6 */
    {
      id: 'AID-06', lang: 'Java', cat: '보안기능', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"관리자만 쓸 수 있는 사용자 삭제 API 만들어줘"',
      title: 'AI 생성: 사용자 삭제 API',
      weaknessName: '부적절한 인가', cwe: 'CWE-285',
      isTruePositive: true,
      code:
        '@DeleteMapping("/admin/users/{id}")\n' +
        'public ResponseEntity<Void> deleteUser(@PathVariable Long id,\n' +
        '                                       @RequestParam boolean isAdmin) {\n' +
        '    if (!isAdmin) {\n' +
        '        return ResponseEntity.status(403).build();\n' +
        '    }\n' +
        '    userService.delete(id);\n' +
        '    return ResponseEntity.noContent().build();\n' +
        '}',
      reasonKeywords: ['클라이언트 값 신뢰', '요청 파라미터로 권한', '서버 확인 없음'],
      negKw: ['안전한 인가', '취약하지 않', '오탐'],
      safeCode:
        '@DeleteMapping("/admin/users/{id}")\n' +
        '@PreAuthorize("hasRole(\'ADMIN\')")\n' +
        'public ResponseEntity<Void> deleteUser(@PathVariable Long id,\n' +
        '                                       Authentication auth) {\n' +
        '    userService.delete(id);\n' +
        '    return ResponseEntity.noContent().build();\n' +
        '}',
      safeCodeKeywords: ['PreAuthorize'],
      explanation:
        '권한 검사가 코드에 보이기 때문에 안전해 보이지만, 판단 근거가 요청 파라미터입니다. ' +
        '요청을 보내는 쪽이 isAdmin=true 를 그냥 붙이면 통과합니다. ' +
        '권한은 서버가 가진 인증 주체에서 읽어야 합니다. ' +
        '"클라이언트가 보낸 값으로 권한을 판단하지 않는다" 는 이 사이트의 다른 실습에서도 반복되는 원칙입니다.'
    },

    /* ------------------------------------------------------------------ 7 */
    {
      id: 'AID-07', lang: 'Python', cat: 'API오용', diff: '상',
      tags: ['ai-generated'],
      aiPrompt: '"세션 데이터를 파일로 저장했다가 다시 불러오는 코드"',
      title: 'AI 생성: 세션 저장과 복원',
      weaknessName: '안전하지 않은 역직렬화', cwe: 'CWE-502',
      isTruePositive: true,
      code:
        'import pickle\n\n' +
        'def save_session(path, data):\n' +
        '    with open(path, "wb") as f:\n' +
        '        pickle.dump(data, f)\n\n' +
        'def load_session(path):\n' +
        '    with open(path, "rb") as f:\n' +
        '        return pickle.loads(f.read())',
      reasonKeywords: ['pickle', '임의 코드 실행', '신뢰할 수 없는 데이터', '역직렬화'],
      negKw: ['JSON', '취약하지 않', '오탐'],
      safeCode:
        'import json\n\n' +
        'def save_session(path, data):\n' +
        '    with open(path, "w", encoding="utf-8") as f:\n' +
        '        json.dump(data, f)\n\n' +
        'def load_session(path):\n' +
        '    with open(path, "r", encoding="utf-8") as f:\n' +
        '        return json.load(f)',
      safeCodeKeywords: ['json'],
      explanation:
        '"파이썬 객체를 그대로 저장" 이라는 요구에는 pickle 이 가장 짧은 답이라 생성 도구가 즐겨 고릅니다. ' +
        '그런데 pickle 은 데이터 형식이 아니라 실행 형식입니다. 역직렬화 과정에서 임의 코드가 돌 수 있어, ' +
        '파일을 바꿔칠 수 있는 사람은 곧 서버에서 코드를 실행할 수 있는 사람입니다. ' +
        'JSON 같은 데이터 전용 형식을 쓰거나, 불가피하면 서명해서 출처를 확인합니다.'
    },

    /* ------------------------------------------------------------------ 8 */
    {
      id: 'AID-08', lang: 'Python', cat: 'API오용', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"사내 API 호출하는데 SSL 인증서 오류가 나. 에러 안 나게 해줘"',
      title: 'AI 생성: 사내 API 호출',
      weaknessName: '부적절한 인증서 검증', cwe: 'CWE-295',
      isTruePositive: true,
      code:
        'import requests\n' +
        'import urllib3\n\n' +
        'urllib3.disable_warnings()\n\n' +
        'def fetch_report(report_id):\n' +
        '    url = "https://intra.example.com/reports/" + str(report_id)\n' +
        '    return requests.get(url, verify=False, timeout=5).json()',
      reasonKeywords: ['verify=False', '인증서 검증 비활성', '중간자 공격', '경고 억제'],
      negKw: ['안전한 TLS', '취약하지 않', '오탐'],
      safeCode:
        'import os\n' +
        'import requests\n\n' +
        'CA_BUNDLE = os.environ["INTERNAL_CA_BUNDLE"]\n\n' +
        'def fetch_report(report_id):\n' +
        '    url = "https://intra.example.com/reports/" + str(report_id)\n' +
        '    return requests.get(url, verify=CA_BUNDLE, timeout=5).json()',
      safeCodeKeywords: ['CA_BUNDLE'],
      explanation:
        '"에러 안 나게" 는 생성 도구에게 가장 위험한 요청입니다. 오류가 사라지는 가장 짧은 길이 ' +
        '검증을 끄는 것이기 때문입니다. 게다가 경고까지 함께 꺼서 나중에 아무도 눈치채지 못합니다. ' +
        '사설 CA 를 쓴다면 그 CA 를 신뢰 목록에 등록하는 것이 정답입니다. ' +
        '검증을 끄면 같은 망에 있는 누구든 응답을 바꿔치기할 수 있습니다.'
    },

    /* ------------------------------------------------------------------ 9 */
    {
      id: 'AID-09', lang: 'Java', cat: '보안기능', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"회원가입할 때 비밀번호 저장하는 코드 만들어줘"',
      title: 'AI 생성: 비밀번호 저장',
      weaknessName: '취약한 암호 알고리즘 사용', cwe: 'CWE-327',
      isTruePositive: true,
      code:
        'public String storePassword(String raw) throws Exception {\n' +
        '    MessageDigest md = MessageDigest.getInstance("MD5");\n' +
        '    byte[] digest = md.digest(raw.getBytes(StandardCharsets.UTF_8));\n' +
        '    return Base64.getEncoder().encodeToString(digest);\n' +
        '}',
      reasonKeywords: ['MD5', '솔트 없음', '빠른 해시', '레인보우 테이블'],
      negKw: ['안전한 해시', '취약하지 않', '오탐'],
      safeCode:
        'public String storePassword(String raw) {\n' +
        '    return BCrypt.hashpw(raw, BCrypt.gensalt(12));\n' +
        '}',
      safeCodeKeywords: ['BCrypt'],
      explanation:
        '학습 데이터에 오래된 예제가 많아서 생성 도구는 아직도 MD5 를 자주 제안합니다. ' +
        '문제는 두 가지입니다. MD5 는 충돌이 발견돼 깨진 알고리즘이고, ' +
        '설령 SHA-256 으로 바꿔도 비밀번호 저장에는 여전히 부적합합니다. 너무 빨라서 대량 대입을 막지 못합니다. ' +
        '비밀번호에는 솔트가 들어가고 연산 비용을 조절할 수 있는 bcrypt, scrypt, argon2 를 씁니다.'
    },

    /* ----------------------------------------------------------------- 10 */
    {
      id: 'AID-10', lang: 'Java', cat: '에러처리', diff: '중',
      tags: ['ai-generated'],
      aiPrompt: '"결제 처리 중에 예외 나도 서비스가 안 죽게 해줘"',
      title: 'AI 생성: 결제 처리 예외 처리',
      weaknessName: '부적절한 예외 처리', cwe: 'CWE-390',
      isTruePositive: true,
      code:
        'public boolean pay(Order order) {\n' +
        '    try {\n' +
        '        gateway.charge(order.getAmount(), order.getToken());\n' +
        '        order.markPaid();\n' +
        '        return true;\n' +
        '    } catch (Exception e) {\n' +
        '        return true;\n' +
        '    }\n' +
        '}',
      reasonKeywords: ['예외 무시', '빈 catch', '실패를 성공으로', '로그 없음'],
      negKw: ['안전한 예외 처리', '취약하지 않', '오탐'],
      safeCode:
        'public boolean pay(Order order) {\n' +
        '    try {\n' +
        '        gateway.charge(order.getAmount(), order.getToken());\n' +
        '        order.markPaid();\n' +
        '        return true;\n' +
        '    } catch (PaymentException e) {\n' +
        '        log.error("payment failed orderId={}", order.getId(), e);\n' +
        '        order.markFailed(e.getCode());\n' +
        '        return false;\n' +
        '    }\n' +
        '}',
      safeCodeKeywords: ['PaymentException', 'markFailed', 'return false'],
      explanation:
        '"안 죽게 해줘" 를 생성 도구는 "예외를 삼켜라" 로 읽습니다. 서비스는 살아 있지만 ' +
        '결제가 실패해도 성공으로 기록되어, 상품은 나가고 돈은 들어오지 않습니다. ' +
        '가용성을 지키는 것과 실패를 감추는 것은 다릅니다. ' +
        '잡을 예외를 좁히고, 남기고, 실패를 실패로 돌려주어야 합니다.'
    }
  ];

  /* ACADEMY_DATA.PRACTICAL 에 이어 붙인다. 중복 id 는 넣지 않는다. */
  var A = global.ACADEMY_DATA = global.ACADEMY_DATA || {};
  A.PRACTICAL = A.PRACTICAL || [];
  var seen = {};
  A.PRACTICAL.forEach(function (x) { seen[x.id] = 1; });
  var added = 0;
  AI_PRACTICAL.forEach(function (x) {
    if (seen[x.id]) return;
    A.PRACTICAL.push(x);
    added++;
  });
  A.AI_PRACTICAL = AI_PRACTICAL;

  if (global.console && global.console.log) {
    global.console.log('[ai-track] +' + added + ' AI 생성 코드 과제');
  }
})(typeof window !== 'undefined' ? window : globalThis);
