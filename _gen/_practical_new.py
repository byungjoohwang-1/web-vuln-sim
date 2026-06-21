# -*- coding: utf-8 -*-

PRACTICAL_NEW = [

    # ============================================================
    # CD-13 (하, TP) 코드 삽입 - Python eval
    # ============================================================
    {'id':'CD-13','lang':'Python','cat':'입력검증','diff':'하',
     'title':'계산기 기능의 수식 처리 로직 검토',
     'code':'''def calculate(request):
    expr = request.GET.get("expr")
    result = eval(expr)
    return str(result)''',
     'isTruePositive':True,'weaknessName':'코드 삽입','cwe':'CWE-94',
     'reasonKeywords':['eval','외부 입력','임의 코드 실행','동적 실행'],
     'negKw':['SQL 삽입','XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import ast
def calculate(request):
    expr = request.GET.get("expr")
    result = ast.literal_eval(expr)
    return str(result)''',
     'safeCodeKeywords':['ast.literal_eval','ast','expr'],
     'explanation':'외부 입력 expr을 eval로 직접 실행하므로 __import__ 등으로 임의 코드 실행이 가능한 코드 삽입에 취약합니다. eval 대신 ast.literal_eval 등 안전한 평가를 사용해야 합니다.'},

    # ============================================================
    # CD-14 (하, TP) 적절하지 않은 난수값 사용 - java.util.Random 토큰
    # ============================================================
    {'id':'CD-14','lang':'Java','cat':'보안기능','diff':'하',
     'title':'비밀번호 재설정 토큰 생성 로직 검토',
     'code':'''public String createResetToken() {
    Random random = new Random();
    long token = random.nextLong();
    return Long.toHexString(token);
}''',
     'isTruePositive':True,'weaknessName':'적절하지 않은 난수값 사용','cwe':'CWE-330',
     'reasonKeywords':['java.util.Random','예측 가능','보안 토큰','CSPRNG 미사용'],
     'negKw':['하드코딩','안전한 코드','취약하지 않','SecureRandom 사용','오탐'],
     'safeCode':'''public String createResetToken() {
    SecureRandom random = new SecureRandom();
    byte[] bytes = new byte[32];
    random.nextBytes(bytes);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
}''',
     'safeCodeKeywords':['SecureRandom','nextBytes','encodeToString'],
     'explanation':'보안에 사용되는 재설정 토큰을 예측 가능한 java.util.Random으로 생성하므로 토큰이 추측되어 계정이 탈취될 수 있습니다. 암호학적으로 안전한 SecureRandom을 사용해야 합니다.'},

    # ============================================================
    # CD-15 (하, TP) 솔트 없이 일방향 해시함수 사용
    # ============================================================
    {'id':'CD-15','lang':'Java','cat':'보안기능','diff':'하',
     'title':'회원 비밀번호 저장 해시 처리 검토',
     'code':'''public String storePassword(String password) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    byte[] digest = md.digest(password.getBytes("UTF-8"));
    return Base64.getEncoder().encodeToString(digest);
}''',
     'isTruePositive':True,'weaknessName':'솔트 없이 일방향 해시함수 사용','cwe':'CWE-759',
     'reasonKeywords':['솔트 없음','레인보우 테이블','일방향 해시','SHA-256 단순 해시'],
     'negKw':['취약한 알고리즘','MD5','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public String storePassword(String password) {
    int cost = 12;
    return BCrypt.hashpw(password, BCrypt.gensalt(cost));
}''',
     'safeCodeKeywords':['BCrypt','gensalt','hashpw'],
     'explanation':'SHA-256 자체는 안전한 알고리즘이지만 솔트 없이 비밀번호를 단순 해시하면 레인보우 테이블 공격으로 원문 복원이 쉬워집니다. 사용자별 솔트와 bcrypt 등 적응형 해시를 사용해야 합니다.'},

    # ============================================================
    # CD-16 (하, TP) 제거되지 않고 남은 디버그 코드
    # ============================================================
    {'id':'CD-16','lang':'Java','cat':'캡슐화','diff':'하',
     'title':'운영 배포된 로그인 처리 코드 검토',
     'code':'''public boolean login(String id, String pw) {
    if (id.equals("test") && pw.equals("test")) {
        return true;  // 개발용 백도어 계정
    }
    return authService.authenticate(id, pw);
}''',
     'isTruePositive':True,'weaknessName':'제거되지 않고 남은 디버그 코드','cwe':'CWE-489',
     'reasonKeywords':['백도어','테스트 계정','디버그 코드','우회 접근'],
     'negKw':['하드코드된 중요정보','안전한 코드','취약하지 않','SQL','오탐'],
     'safeCode':'''public boolean login(String id, String pw) {
    return authService.authenticate(id, pw);
}''',
     'safeCodeKeywords':['authenticate','authService','return'],
     'explanation':'운영 코드에 test/test 백도어 계정이 남아 있어 디버그 코드로 인증을 우회할 수 있습니다. 배포 전 디버그·테스트 진입점을 모두 제거해야 합니다.'},

    # ============================================================
    # CD-17 (중, TP) 신뢰되지 않는 URL 주소로 자동접속 연결 (open redirect)
    # ============================================================
    {'id':'CD-17','lang':'Java','cat':'입력검증','diff':'중',
     'title':'로그인 후 페이지 이동 처리 검토',
     'code':'''public void afterLogin(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String returnUrl = req.getParameter("returnUrl");
    resp.sendRedirect(returnUrl);
}''',
     'isTruePositive':True,'weaknessName':'신뢰되지 않는 URL 주소로 자동접속 연결','cwe':'CWE-601',
     'reasonKeywords':['sendRedirect','외부 입력','리다이렉트','허용 목록 없음'],
     'negKw':['XSS','HTTP 응답 분할','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void afterLogin(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String returnUrl = req.getParameter("returnUrl");
    Set<String> allowed = Set.of("/home", "/dashboard", "/mypage");
    if (returnUrl != null && allowed.contains(returnUrl)) {
        resp.sendRedirect(returnUrl);
    } else {
        resp.sendRedirect("/home");
    }
}''',
     'safeCodeKeywords':['allowed','contains','/home'],
     'explanation':'외부 입력 returnUrl을 검증 없이 sendRedirect 대상으로 사용하므로 공격자가 피해자를 악성 사이트로 유도하는 오픈 리다이렉트에 취약합니다. 허용된 URL 목록과 대조해야 합니다.'},

    # ============================================================
    # CD-18 (중, TP) HTTP 응답 분할
    # ============================================================
    {'id':'CD-18','lang':'Java','cat':'입력검증','diff':'중',
     'title':'언어 설정 쿠키 발급 로직 검토',
     'code':'''public void setLang(HttpServletRequest req, HttpServletResponse resp) {
    String lang = req.getParameter("lang");
    Cookie cookie = new Cookie("LANG", lang);
    resp.addCookie(cookie);
    resp.setHeader("X-Lang", lang);
}''',
     'isTruePositive':True,'weaknessName':'HTTP 응답 분할','cwe':'CWE-113',
     'reasonKeywords':['CR LF','개행 문자','응답 헤더','외부 입력'],
     'negKw':['XSS','오픈 리다이렉트','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void setLang(HttpServletRequest req, HttpServletResponse resp) {
    String lang = req.getParameter("lang");
    if (lang != null && lang.matches("^[a-zA-Z\\\\-]{2,5}$")) {
        Cookie cookie = new Cookie("LANG", lang);
        resp.addCookie(cookie);
        resp.setHeader("X-Lang", lang);
    }
}''',
     'safeCodeKeywords':['matches','^[a-zA-Z','addCookie'],
     'explanation':'외부 입력 lang을 개행 필터링 없이 응답 헤더·쿠키에 넣으므로 CR·LF를 삽입해 응답을 분할·조작하는 HTTP 응답 분할에 취약합니다. 개행 문자를 제거하거나 화이트리스트로 검증해야 합니다.'},

    # ============================================================
    # CD-19 (중, TP) 서버사이드 요청 위조(SSRF)
    # ============================================================
    {'id':'CD-19','lang':'Python','cat':'입력검증','diff':'중',
     'title':'외부 이미지 미리보기 프록시 기능 검토',
     'code':'''import requests
def fetch_image(request):
    url = request.GET.get("url")
    resp = requests.get(url, timeout=5)
    return resp.content''',
     'isTruePositive':True,'weaknessName':'서버사이드 요청 위조(SSRF)','cwe':'CWE-918',
     'reasonKeywords':['requests.get','외부 입력 URL','내부망 접근','메타데이터','허용 목록 없음'],
     'negKw':['오픈 리다이렉트','XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import requests
from urllib.parse import urlparse
ALLOWED_HOSTS = {"img.example.com", "cdn.example.com"}
def fetch_image(request):
    url = request.GET.get("url")
    host = urlparse(url).hostname
    if host not in ALLOWED_HOSTS:
        raise ValueError("not allowed host")
    resp = requests.get(url, timeout=5)
    return resp.content''',
     'safeCodeKeywords':['ALLOWED_HOSTS','urlparse','hostname'],
     'explanation':'서버가 외부 입력 url로 직접 요청을 보내므로 내부망 IP나 클라우드 메타데이터(169.254.169.254)에 접근하는 SSRF에 취약합니다. 요청 대상을 허용 목록으로 제한해야 합니다.'},

    # ============================================================
    # CD-20 (중, TP) XML 외부 개체(XXE)
    # ============================================================
    {'id':'CD-20','lang':'Java','cat':'입력검증','diff':'중',
     'title':'XML 주문서 업로드 파싱 로직 검토',
     'code':'''public Document parse(InputStream xml) throws Exception {
    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
    DocumentBuilder db = dbf.newDocumentBuilder();
    return db.parse(xml);
}''',
     'isTruePositive':True,'weaknessName':'XML 외부 개체(XXE)','cwe':'CWE-611',
     'reasonKeywords':['DocumentBuilderFactory','외부 개체','DTD 미비활성화','파일 노출'],
     'negKw':['XML 삽입','SQL','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public Document parse(InputStream xml) throws Exception {
    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
    dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
    dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
    DocumentBuilder db = dbf.newDocumentBuilder();
    return db.parse(xml);
}''',
     'safeCodeKeywords':['disallow-doctype-decl','setFeature','external-general-entities'],
     'explanation':'XML 파서가 DTD·외부 개체 처리를 비활성화하지 않아 악의적 외부 개체로 내부 파일 노출·SSRF가 가능한 XXE에 취약합니다. disallow-doctype-decl 등 외부 개체 처리를 비활성화해야 합니다.'},

    # ============================================================
    # CD-21 (중, TP) LDAP 삽입
    # ============================================================
    {'id':'CD-21','lang':'Java','cat':'입력검증','diff':'하',
     'title':'LDAP 사용자 검색 필터 생성 검토',
     'code':'''public NamingEnumeration search(DirContext ctx, String user) throws NamingException {
    String filter = "(&(objectClass=person)(uid=" + user + "))";
    SearchControls sc = new SearchControls();
    return ctx.search("ou=users,dc=example,dc=com", filter, sc);
}''',
     'isTruePositive':True,'weaknessName':'LDAP 삽입','cwe':'CWE-90',
     'reasonKeywords':['LDAP 필터','문자열 결합','외부 입력','이스케이프 없음'],
     'negKw':['SQL 삽입','XPath','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public NamingEnumeration search(DirContext ctx, String user) throws NamingException {
    String filter = "(&(objectClass=person)(uid={0}))";
    SearchControls sc = new SearchControls();
    return ctx.search("ou=users,dc=example,dc=com", filter, new Object[]{ user }, sc);
}''',
     'safeCodeKeywords':['{0}','new Object[]','search'],
     'explanation':'외부 입력 user를 검증·이스케이프 없이 LDAP 검색 필터에 결합하므로 *)(uid=* 등으로 필터 구조를 변조하는 LDAP 삽입에 취약합니다. 파라미터화 필터나 특수문자 이스케이프를 사용해야 합니다.'},

    # ============================================================
    # CD-22 (중, TP) 부적절한 인가 (IDOR)
    # ============================================================
    {'id':'CD-22','lang':'Java','cat':'보안기능','diff':'중',
     'title':'주문 상세 조회 API 권한 처리 검토',
     'code':'''public Order getOrder(HttpServletRequest req) {
    Long orderId = Long.valueOf(req.getParameter("orderId"));
    HttpSession session = req.getSession();
    String userId = (String) session.getAttribute("userId");
    return orderRepository.findById(orderId);
}''',
     'isTruePositive':True,'weaknessName':'부적절한 인가','cwe':'CWE-285',
     'reasonKeywords':['소유자 검증 없음','orderId','IDOR','권한 검사 누락'],
     'negKw':['인증 없는 중요기능','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public Order getOrder(HttpServletRequest req) {
    Long orderId = Long.valueOf(req.getParameter("orderId"));
    HttpSession session = req.getSession();
    String userId = (String) session.getAttribute("userId");
    Order order = orderRepository.findById(orderId);
    if (order == null || !order.getOwnerId().equals(userId)) {
        throw new AccessDeniedException("forbidden");
    }
    return order;
}''',
     'safeCodeKeywords':['getOwnerId','equals(userId)','AccessDeniedException'],
     'explanation':'로그인은 되어 있으나 조회 대상 orderId가 요청자 소유인지 검사하지 않으므로 다른 사용자의 주문을 열람할 수 있는 부적절한 인가(IDOR)에 취약합니다. 자원 소유자 권한을 검사해야 합니다.'},

    # ============================================================
    # CD-23 (중, FP) PreparedStatement + 화이트리스트 ORDER BY
    # ============================================================
    {'id':'CD-23','lang':'Java','cat':'입력검증','diff':'중',
     'title':'정렬 옵션이 포함된 목록 조회 쿼리 검토',
     'code':'''public ResultSet list(HttpServletRequest req, String name) throws SQLException {
    String sort = req.getParameter("sort");
    String orderBy = "name";
    if ("date".equals(sort)) orderBy = "created_at";
    else if ("price".equals(sort)) orderBy = "price";
    String sql = "SELECT * FROM product WHERE name = ? ORDER BY " + orderBy;
    PreparedStatement ps = conn.prepareStatement(sql);
    ps.setString(1, name);
    return ps.executeQuery();
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['화이트리스트','PreparedStatement','setString','고정 컬럼 매핑','외부 입력 직접 결합 아님'],
     'negKw':['SQL 삽입 가능','정탐','삽입 가능','조작 가능','주입 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'ORDER BY 절은 문자열로 결합되지만 외부 입력 sort를 직접 넣지 않고 if 분기로 고정된 컬럼명만 매핑하며, name 값은 PreparedStatement로 바인딩하므로 SQL 삽입이 불가능한 안전한 코드(오탐)입니다.'},

    # ============================================================
    # CD-24 (중, FP) SecureRandom으로 토큰 생성 (안전)
    # ============================================================
    {'id':'CD-24','lang':'Java','cat':'보안기능','diff':'중',
     'title':'세션 식별자 생성 로직 안전성 검토',
     'code':'''public String newSessionId() {
    SecureRandom random = new SecureRandom();
    byte[] buf = new byte[24];
    random.nextBytes(buf);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(buf);
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['SecureRandom','CSPRNG','예측 불가','충분한 길이','nextBytes'],
     'negKw':['예측 가능','정탐','추측 가능','공격 가능','노출 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'세션 식별자를 암호학적으로 안전한 SecureRandom으로 192비트(24바이트) 길이로 생성하므로 예측이 불가능한 안전한 코드(오탐)입니다. java.util.Random이 아니므로 난수 취약점이 없습니다.'},

    # ============================================================
    # CD-25 (중, FP) 예외를 구체적으로 잡고 안전하게 실패 처리 (안전)
    # ============================================================
    {'id':'CD-25','lang':'Java','cat':'에러처리','diff':'중',
     'title':'결제 검증 단계의 예외 처리 안전성 검토',
     'code':'''public boolean verifyPayment(String token) {
    try {
        return paymentGateway.verify(token);
    } catch (PaymentException e) {
        log.error("payment verify failed", e);
        return false;
    }
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['구체적 예외','PaymentException','실패 시 false','안전한 기본값','로깅'],
     'negKw':['부적절한 예외','정탐','검증 우회 가능','공격 가능','우회 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'예외를 포괄적 Exception이 아닌 구체적인 PaymentException으로 잡고, 검증 실패 시 안전하게 false를 반환하며 오류를 로깅하므로 검증 우회가 없는 안전한 코드(오탐)입니다.'},

    # ============================================================
    # CD-26 (상, TP) 경쟁조건 TOCTOU
    # ============================================================
    {'id':'CD-26','lang':'C','cat':'시간상태','diff':'상',
     'title':'설정 파일 쓰기 권한 확인 후 기록 로직 검토',
     'code':'''void write_config(const char *path, const char *data, size_t n) {
    if (access(path, W_OK) == 0) {
        FILE *fp = fopen(path, "w");
        if (fp) {
            fwrite(data, 1, n, fp);
            fclose(fp);
        }
    }
}''',
     'isTruePositive':True,'weaknessName':'경쟁조건: 검사시점과 사용시점(TOCTOU)','cwe':'CWE-367',
     'reasonKeywords':['access','fopen','검사시점 사용시점','심볼릭 링크 교체','비원자적'],
     'negKw':['경로 조작','버퍼 오버플로우','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''void write_config(const char *path, const char *data, size_t n) {
    int fd = open(path, O_WRONLY | O_NOFOLLOW);
    if (fd >= 0) {
        write(fd, data, n);
        close(fd);
    }
}''',
     'safeCodeKeywords':['open(','O_NOFOLLOW','write(fd'],
     'explanation':'access로 권한을 검사한 시점과 fopen으로 여는 시점 사이에 공격자가 파일을 심볼릭 링크 등으로 교체할 수 있어 TOCTOU 경쟁조건에 취약합니다. 검사·사용을 분리하지 말고 O_NOFOLLOW 등으로 원자적으로 열어야 합니다.'},

    # ============================================================
    # CD-27 (상, FP) CSRF 보호가 적용된 상태변경 요청 (안전)
    # ============================================================
    {'id':'CD-27','lang':'Java','cat':'입력검증','diff':'상',
     'title':'비밀번호 변경 요청의 위조 방지 처리 검토',
     'code':'''public void changePassword(HttpServletRequest req, HttpServletResponse resp) {
    String formToken = req.getParameter("csrfToken");
    String sessionToken = (String) req.getSession().getAttribute("csrfToken");
    if (sessionToken == null || !sessionToken.equals(formToken)) {
        resp.setStatus(403);
        return;
    }
    String newPw = req.getParameter("newPw");
    userService.updatePassword(currentUser(req), newPw);
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['CSRF 토큰','세션 토큰 비교','equals','위조 방지','403'],
     'negKw':['CSRF 가능','정탐','위조 가능','공격 가능','우회 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'상태를 변경하는 비밀번호 변경 요청에서 폼의 CSRF 토큰을 세션에 저장된 토큰과 비교해 일치할 때만 처리하므로 요청 위조가 불가능한 안전한 코드(오탐)입니다.'},

    # ============================================================
    # CD-28 (상, TP) 적절한 인증 없는 중요기능 허용
    # ============================================================
    {'id':'CD-28','lang':'Java','cat':'보안기능','diff':'상',
     'title':'관리자 사용자 삭제 기능 접근 통제 검토',
     'code':'''@PostMapping("/admin/users/delete")
public String deleteUser(@RequestParam Long id, HttpServletRequest req) {
    boolean isAdmin = Boolean.parseBoolean(req.getParameter("isAdmin"));
    if (isAdmin) {
        userService.delete(id);
    }
    return "redirect:/admin/users";
}''',
     'isTruePositive':True,'weaknessName':'적절한 인증 없는 중요기능 허용','cwe':'CWE-306',
     'reasonKeywords':['서버 인증 없음','isAdmin 파라미터','클라이언트 값 신뢰','중요기능'],
     'negKw':['부적절한 인가','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''@PostMapping("/admin/users/delete")
public String deleteUser(@RequestParam Long id, HttpServletRequest req) {
    User user = (User) req.getSession().getAttribute("loginUser");
    if (user == null || !user.hasRole("ADMIN")) {
        throw new AccessDeniedException("forbidden");
    }
    userService.delete(id);
    return "redirect:/admin/users";
}''',
     'safeCodeKeywords':['getSession','hasRole("ADMIN")','AccessDeniedException'],
     'explanation':'사용자 삭제라는 중요 기능을 서버 측 인증·세션 검사 없이 클라이언트가 보낸 isAdmin 파라미터만으로 허용하므로, 누구나 isAdmin=true를 보내 실행할 수 있는 적절한 인증 없는 중요기능 허용에 취약합니다.'},

    # ============================================================
    # CD-29 (상, FP) 정수 오버플로우처럼 보이나 사전 범위검사로 안전
    # ============================================================
    {'id':'CD-29','lang':'Java','cat':'입력검증','diff':'상',
     'title':'요청 건수에 따른 버퍼 크기 계산 로직 검토',
     'code':'''public byte[] allocate(HttpServletRequest req) {
    int count = Integer.parseInt(req.getParameter("count"));
    if (count < 0 || count > 1000) {
        throw new IllegalArgumentException("invalid count");
    }
    int size = count * 64;
    return new byte[size];
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['범위 검사','count > 1000','오버플로우 불가','상한 제한','안전한 곱셈'],
     'negKw':['정탐','오버플로우 발생','공격 가능','오버플로우 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'count * 64 연산 전에 count를 0~1000으로 제한하므로 결과 최대값이 64000으로 int 범위를 절대 넘지 않습니다. 정수형 오버플로우가 발생할 수 없는 안전한 코드(오탐)입니다.'},

    # ============================================================
    # CD-30 (상, FP) try-with-resources로 자원 해제 보장 (안전)
    # ============================================================
    {'id':'CD-30','lang':'Java','cat':'코드오류','diff':'상',
     'title':'예외 발생 가능 구간의 파일 자원 처리 검토',
     'code':'''public String readFirstLine(String path) throws IOException {
    try (BufferedReader br = new BufferedReader(new FileReader(path))) {
        String line = br.readLine();
        if (line == null) {
            throw new IOException("empty file");
        }
        return line.trim();
    }
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['try-with-resources','자동 close','예외 시에도 해제','자원 누수 없음'],
     'negKw':['정탐','close 누락','해제 누락','누수 발생'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'중간에 IOException을 던지더라도 try-with-resources 구문이 BufferedReader를 자동으로 close하므로 자원 누수가 발생하지 않는 안전한 코드(오탐)입니다.'},
]
