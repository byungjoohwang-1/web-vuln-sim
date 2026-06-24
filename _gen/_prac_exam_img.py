# -*- coding: utf-8 -*-
"""실무 코드진단(정/오탐) — 2026 진단원 양성과정 강조 11개 hot topic.
근거: 행안부·KISA「소프트웨어 보안약점 진단가이드」「Python 시큐어코딩 가이드」(공공저작물).
코드는 가이드 예제에 충실하게 재구성, 해설·정/오탐 키워드는 자체작성. 출처표시 부기."""

PART = [
 {'id':'IMG-01','lang':'Java','cat':'입력검증','diff':'중',
  'title':'게시글 등록 요청 처리 로직 검토 (CSRF)',
  'code':'''public void doPost(HttpServletRequest request, HttpServletResponse response) {
    String title = request.getParameter("title");
    String content = request.getParameter("content");
    // 로그인 세션만 확인하고 곧바로 상태 변경 수행
    Long uid = (Long) request.getSession().getAttribute("uid");
    boardDao.insert(uid, title, content);
}''',
  'isTruePositive':True,'weaknessName':'크로스사이트 요청 위조(CSRF)','cwe':'CWE-352',
  'reasonKeywords':['CSRF 토큰','토큰 검증','상태 변경','자동화된 요청','POST'],
  'negKw':['안전한 코드','오탐','취약하지 않','SQL'],
  'safeCode':'''public void doPost(HttpServletRequest request, HttpServletResponse response) {
    String pToken = request.getParameter("csrf_token");
    String sToken = (String) request.getSession().getAttribute("CSRF_TOKEN");
    if (pToken == null || !pToken.equals(sToken)) {   // 세션 토큰과 일치할 때만 처리
        response.setStatus(403);
        return;
    }
    String title = request.getParameter("title");
    String content = request.getParameter("content");
    Long uid = (Long) request.getSession().getAttribute("uid");
    boardDao.insert(uid, title, content);
}''',
  'safeCodeKeywords':['csrf_token','getAttribute','equals','403','CSRF_TOKEN'],
  'explanation':'세션 로그인 여부만 확인하고 요청이 실제 사용자가 의도한 것인지(요청 위조 여부)를 검증하지 않아 CSRF에 취약합니다. 공격자가 미리 심어둔 자동화 요청으로 회원 권한의 상태 변경(글쓰기 등)이 수행될 수 있습니다. 입력 폼에 임의 토큰을 hidden 필드로 심고, 요청 파라미터의 토큰을 세션에 저장한 토큰과 비교해 일치할 때만 처리해야 합니다. (출처: KISA 진단가이드 CSRF 예제 기반)'},

 {'id':'IMG-02','lang':'Java','cat':'입력검증','diff':'중',
  'title':'CSRF 토큰 비교가 포함된 요청 처리 검토',
  'code':'''public void doPost(HttpServletRequest request, HttpServletResponse response) {
    String pToken = request.getParameter("csrf_token");
    String sToken = (String) request.getSession().getAttribute("CSRF_TOKEN");
    if (pToken != null && pToken.equals(sToken)) {
        accountService.transfer(request);   // 토큰 일치 시에만 실행
    } else {
        response.setStatus(403);
    }
}''',
  'isTruePositive':False,'weaknessName':'','cwe':'',
  'reasonKeywords':['토큰 비교','equals','일치할 때만','세션 토큰','안전'],
  'negKw':['CSRF 가능','정탐','취약','위조 가능'],
  'safeCode':'','safeCodeKeywords':[],
  'explanation':'요청 파라미터로 받은 토큰을 세션에 저장된 CSRF 토큰과 비교하여 일치하는 경우에만 상태 변경을 처리하므로 위조 요청이 차단되는 안전한 코드(오탐)입니다. 토큰은 추측 불가능한 난수(UUID 등)로 생성되고 세션에 보관된다는 전제이며, null 검사도 포함되어 있습니다.'},

 {'id':'IMG-03','lang':'Java','cat':'입력검증','diff':'상',
  'title':'외부 연동 URL 호출 로직 검토 (SSRF)',
  'code':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String target = req.getParameter("url");           // 사용자 입력값으로 URL 받음
    URL url = new URL(target);
    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
    conn.connect();
    resp.getOutputStream().write(conn.getInputStream().readAllBytes());
}''',
  'isTruePositive':True,'weaknessName':'서버사이드 요청 위조(SSRF)','cwe':'CWE-918',
  'reasonKeywords':['사용자 입력','URL','openConnection','내부 자원','화이트리스트 없음'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    // key-value 형식으로 허용된 URL 목록을 미리 정의(화이트리스트)
    Map<String, String> urlMap = new HashMap<>();
    urlMap.put("members", "http://192.168.0.45/member/list.json");
    String key = req.getParameter("url");
    String allowed = urlMap.get(key);                  // 허용된 key 만 실제 URL로 매핑
    if (allowed == null) { resp.setStatus(400); return; }
    HttpURLConnection conn = (HttpURLConnection) new URL(allowed).openConnection();
    conn.connect();
    resp.getOutputStream().write(conn.getInputStream().readAllBytes());
}''',
  'safeCodeKeywords':['urlMap','allowed','key','HttpURLConnection','openConnection'],
  'explanation':'사용자가 전달한 url 파라미터를 그대로 URL로 만들어 서버가 요청을 보내므로, 공격자가 내부망 주소(예: 169.254.169.254, 내부 관리 페이지)를 지정해 서버를 우회 통로로 악용하는 SSRF에 취약합니다. 외부 입력을 직접 URL로 쓰지 말고, 허용된 URL을 key-value 화이트리스트로 두어 key만 받아 매핑해야 합니다. (출처: KISA 진단가이드 SSRF 예제 기반)'},

 {'id':'IMG-04','lang':'Java','cat':'입력검증','diff':'중',
  'title':'화이트리스트 기반 URL 연동 로직 검토',
  'code':'''public class Connector {
    private static final Map<String, String> URL_MAP = Map.of(
        "members", "http://192.168.0.45/member/list.json",
        "notice",  "http://192.168.0.45/notice/list.json");
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        String allowed = URL_MAP.get(req.getParameter("url"));
        if (allowed == null) { resp.setStatus(400); return; }
        HttpURLConnection conn = (HttpURLConnection) new URL(allowed).openConnection();
        conn.connect();
    }
}''',
  'isTruePositive':False,'weaknessName':'','cwe':'',
  'reasonKeywords':['화이트리스트','URL_MAP','허용된 목록','key','안전'],
  'negKw':['SSRF 가능','정탐','취약','우회 가능'],
  'safeCode':'','safeCodeKeywords':[],
  'explanation':'사용자 입력을 직접 URL로 사용하지 않고, 미리 정의한 허용 목록(URL_MAP)의 key로만 실제 URL을 참조하므로 임의 내부 자원 요청이 불가능한 안전한 코드(오탐)입니다. 허용되지 않은 key는 400으로 거부합니다.'},

 {'id':'IMG-05','lang':'Java','cat':'입력검증','diff':'상',
  'title':'쿠키 값 설정 로직 검토 (HTTP 응답 분할)',
  'code':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
    String lastLogin = req.getParameter("last_login");   // 외부 입력
    Cookie c = new Cookie("LASTLOGIN", lastLogin);        // 개행문자 제거 없이 헤더에 설정
    resp.addCookie(c);
    resp.setContentType("text/html");
}''',
  'isTruePositive':True,'weaknessName':'HTTP 응답 분할','cwe':'CWE-113',
  'reasonKeywords':['개행문자','\\r\\n','외부 입력','응답 헤더','제거하지 않'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
    String lastLogin = req.getParameter("last_login");
    if (lastLogin == null || "".equals(lastLogin)) return;
    // 외부 입력값에서 개행문자(\\r\\n)를 제거한 후 쿠키 값으로 설정
    lastLogin = lastLogin.replaceAll("\\r\\n", "");
    Cookie c = new Cookie("LASTLOGIN", lastLogin);
    resp.addCookie(c);
    resp.setContentType("text/html");
}''',
  'safeCodeKeywords':['replaceAll','\\r\\n','Cookie','addCookie'],
  'explanation':'외부 입력값을 개행문자(CR/LF) 제거 없이 응답 헤더(쿠키)에 넣으므로, 공격자가 %0d%0a를 삽입해 헤더를 조작하거나 응답을 둘로 나누는 HTTP 응답 분할에 취약합니다. 헤더에 반영하기 전 \\r\\n을 제거(또는 거부)해야 합니다. (출처: KISA 진단가이드 HTTP 응답분할 예제 기반)'},

 {'id':'IMG-06','lang':'Java','cat':'보안기능','diff':'중',
  'title':'비밀번호 저장 해시 처리 검토 (솔트)',
  'code':'''public void register(String id, String pwd) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    byte[] hash = digest.digest(pwd.getBytes());   // 솔트 없이 비밀번호만 해시
    userDao.save(id, toHex(hash));
}''',
  'isTruePositive':True,'weaknessName':'솔트 없이 일방향 해시함수 사용','cwe':'CWE-759',
  'reasonKeywords':['솔트','salt','레인보우 테이블','사용자별','digest.update'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public void register(String id, String pwd) throws Exception {
    byte[] salt = new byte[16];
    SecureRandom.getInstanceStrong().nextBytes(salt);   // 사용자별 난수 솔트
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    digest.reset();
    digest.update(salt);                                // 솔트를 먼저 반영
    byte[] hash = digest.digest(pwd.getBytes());
    userDao.save(id, toHex(salt), toHex(hash));
}''',
  'safeCodeKeywords':['salt','SecureRandom','digest.update','nextBytes'],
  'explanation':'솔트 없이 비밀번호만 해시하면 같은 비밀번호가 항상 같은 해시가 되어 레인보우 테이블·사전 공격으로 원문 복원이 쉬워집니다. 사용자별 난수 솔트를 생성해 해시에 포함(digest.update(salt))하고 솔트를 함께 저장해야 합니다. (출처: KISA 진단가이드 솔트 해시 예제 기반)'},

 {'id':'IMG-07','lang':'Java','cat':'보안기능','diff':'중',
  'title':'솔트가 적용된 해시 저장 로직 검토',
  'code':'''public void register(String id, String pwd) throws Exception {
    byte[] salt = new byte[16];
    SecureRandom.getInstanceStrong().nextBytes(salt);
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    digest.update(salt);
    byte[] hash = digest.digest(pwd.getBytes());
    userDao.save(id, toHex(salt), toHex(hash));
}''',
  'isTruePositive':False,'weaknessName':'','cwe':'',
  'reasonKeywords':['솔트','SecureRandom','update(salt)','사용자별','안전'],
  'negKw':['취약','정탐','솔트 없'],
  'safeCode':'','safeCodeKeywords':[],
  'explanation':'사용자별로 SecureRandom으로 생성한 난수 솔트를 해시에 반영(update)하고 솔트를 함께 저장하므로, 동일 비밀번호라도 해시값이 달라져 레인보우 테이블 공격이 무력화되는 안전한 코드(오탐)입니다.'},

 {'id':'IMG-08','lang':'Java','cat':'보안기능','diff':'하',
  'title':'DB 접속 정보 설정 로직 검토 (하드코드)',
  'code':'''public Connection getConnection() throws SQLException {
    String url  = "jdbc:mysql://10.0.0.5:3306/app";
    String user = "admin";
    String pass = "P@ssw0rd!2024";   // 소스에 비밀번호 하드코딩
    return DriverManager.getConnection(url, user, pass);
}''',
  'isTruePositive':True,'weaknessName':'하드코드된 중요정보','cwe':'CWE-798',
  'reasonKeywords':['하드코드','소스코드','비밀번호','외부 설정','복호화'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public Connection getConnection() throws SQLException {
    // 접속 정보는 소스 밖(설정/보안저장소)에서 로드, 비밀번호는 암호화 보관 후 복호화
    String url  = config.get("db.url");
    String user = config.get("db.user");
    String pass = vault.decrypt(config.get("db.pass.enc"));
    return DriverManager.getConnection(url, user, pass);
}''',
  'safeCodeKeywords':['config','vault','decrypt','getConnection'],
  'explanation':'비밀번호 등 중요정보를 소스코드에 평문으로 하드코딩하면 소스 유출·디컴파일·형상관리 노출 시 그대로 탈취됩니다. 접속 정보는 소스 외부의 설정/보안 저장소에서 로드하고 비밀번호는 암호화해 보관 후 복호화해 사용해야 합니다. (출처: KISA 진단가이드 하드코드 예제 기반)'},

 {'id':'IMG-09','lang':'Java','cat':'보안기능','diff':'상',
  'title':'내려받은 코드 실행 전 검증 로직 검토 (전자서명)',
  'code':'''public void runPlugin(JarFile jar, String entryName) throws Exception {
    JarEntry entry = jar.getJarEntry(entryName);
    jar.getInputStream(entry).readAllBytes();   // 서명 주체 확인 없이 로드
    loader.loadClass(entry.getName()).getDeclaredConstructor().newInstance();
}''',
  'isTruePositive':True,'weaknessName':'부적절한 전자서명 확인','cwe':'CWE-347',
  'reasonKeywords':['getCodeSigners','전자서명','서명 주체','신뢰','null 검사'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public void runPlugin(JarFile jar, String entryName) throws Exception {
    JarEntry entry = jar.getJarEntry(entryName);
    jar.getInputStream(entry).readAllBytes();        // 스트림을 끝까지 읽어야 서명 검증됨
    CodeSigner[] signers = entry.getCodeSigners();
    if (signers == null || signers.length == 0 || !isTrusted(signers)) {
        throw new SecurityException("신뢰할 수 없는 서명");   // 미서명/비신뢰 시 실행 거부
    }
    loader.loadClass(entry.getName()).getDeclaredConstructor().newInstance();
}''',
  'safeCodeKeywords':['getCodeSigners','signers','null','isTrusted','SecurityException'],
  'explanation':'JAR로 내려받은 코드의 전자서명 주체를 확인하지 않고 실행하면, 위·변조되거나 신뢰할 수 없는 코드가 그대로 실행됩니다. JarEntry.getCodeSigners()로 서명자를 확인하고, 서명이 없거나(null/0) 신뢰할 수 없으면 실행을 거부해야 합니다. (출처: KISA 진단가이드 전자서명 확인 예제 기반)'},

 {'id':'IMG-10','lang':'Java','cat':'보안기능','diff':'중',
  'title':'관리자 기능 인가 판단 로직 검토 (부적절한 입력값)',
  'code':'''public void adminAction(HttpServletRequest request) {
    // 클라이언트가 보낸 hidden 필드/쿠키 값으로 권한을 판단
    boolean isAdmin = "true".equals(request.getParameter("is_admin"));
    if (isAdmin) {
        userDao.deleteAll();   // 보안 결정에 외부 입력값을 그대로 신뢰
    }
}''',
  'isTruePositive':True,'weaknessName':'보안기능 결정에 사용되는 부적절한 입력값','cwe':'CWE-807',
  'reasonKeywords':['외부 입력','hidden','쿠키','서버 세션','권한 판단','신뢰'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public void adminAction(HttpServletRequest request) {
    // 권한은 서버 세션에 저장된 신뢰 가능한 값으로만 판단
    String role = (String) request.getSession().getAttribute("ROLE");
    if ("ADMIN".equals(role)) {
        userDao.deleteAll();
    }
}''',
  'safeCodeKeywords':['getSession','getAttribute','ROLE','adminAction'],
  'explanation':'권한·인증 같은 보안 결정을 클라이언트가 조작 가능한 입력값(hidden 필드·쿠키·파라미터)으로 판단하면, 공격자가 is_admin=true를 보내 보호 메커니즘을 우회하고 권한을 상승시킬 수 있습니다. 보안 결정에 쓰는 값은 서버 세션 등 내부의 신뢰 가능한 값만 사용해야 합니다. (출처: KISA 진단가이드 부적절한 입력값 예제 기반)'},

 {'id':'IMG-11','lang':'Java','cat':'보안기능','diff':'상',
  'title':'외부 코드 다운로드 후 사용 로직 검토 (무결성)',
  'code':'''public void update() throws Exception {
    URL src = new URL("https://cdn.example.com/patch.jar");
    Files.copy(src.openStream(), Paths.get("patch.jar"), REPLACE_EXISTING);
    // 무결성 검증 없이 곧바로 로드·실행
    new URLClassLoader(new URL[]{ new File("patch.jar").toURI().toURL() })
        .loadClass("Patch").getDeclaredConstructor().newInstance();
}''',
  'isTruePositive':True,'weaknessName':'무결성 검사 없는 코드 다운로드','cwe':'CWE-494',
  'reasonKeywords':['무결성','해시','전자서명','검증','다운로드','변조'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public void update() throws Exception {
    URL src = new URL("https://cdn.example.com/patch.jar");
    byte[] data = src.openStream().readAllBytes();
    // 게시된 기대 해시와 비교해 무결성 검증 후에만 사용
    String expected = "8f3a...";   // 안전한 채널로 받은 기준 해시(SHA-256)
    String actual = toHex(MessageDigest.getInstance("SHA-256").digest(data));
    if (!expected.equals(actual)) throw new SecurityException("무결성 검증 실패");
    Files.write(Paths.get("patch.jar"), data);
    // ... 검증된 코드만 로드 ...
}''',
  'safeCodeKeywords':['SHA-256','expected','MessageDigest','getInstance'],
  'explanation':'원격에서 내려받은 실행 코드를 무결성 검증 없이 곧바로 로드·실행하면, 전송 중간자 공격이나 변조된 배포본이 그대로 실행됩니다. 안전한 채널로 받은 기준 해시(또는 전자서명)와 대조해 무결성을 검증한 뒤에만 사용해야 합니다. (출처: KISA 진단가이드 코드 다운로드 무결성 예제 기반)'},

 {'id':'IMG-12','lang':'Java','cat':'보안기능','diff':'중',
  'title':'로그인 인증 처리 로직 검토 (반복 인증 제한)',
  'code':'''public boolean login(String id, String pw) {
    User u = userDao.find(id);
    // 시도 횟수 제한 없이 무제한 비밀번호 검증
    return u != null && u.getPw().equals(hash(pw));
}''',
  'isTruePositive':True,'weaknessName':'반복된 인증시도 제한 기능 부재','cwe':'CWE-307',
  'reasonKeywords':['시도 횟수','제한','잠금','무차별 대입','brute force','카운트'],
  'negKw':['안전한 코드','오탐','취약하지 않'],
  'safeCode':'''public boolean login(String id, String pw) {
    if (attemptStore.isLocked(id)) return false;        // 임계치 초과 시 잠금
    User u = userDao.find(id);
    boolean ok = u != null && u.getPw().equals(hash(pw));
    if (!ok) attemptStore.fail(id);                     // 실패 누적
    else     attemptStore.reset(id);                    // 성공 시 초기화
    return ok;
}''',
  'safeCodeKeywords':['isLocked','attempt','fail','attemptStore','reset'],
  'explanation':'로그인 실패 횟수에 제한이 없으면 공격자가 자동화 도구로 비밀번호를 무차별 대입(brute force)할 수 있습니다. 계정·IP별 실패 횟수를 누적해 임계치 초과 시 일정 시간 잠금하고, 성공 시 초기화해야 합니다. (출처: KISA 진단가이드 반복 인증시도 제한 예제 기반)'},
]
