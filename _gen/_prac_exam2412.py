# -*- coding: utf-8 -*-
# 2교시 실무 — 2024.12 기출 복원 패턴 정밀 이식 (EX-01~EX-11).
# KISA SW보안약점 진단가이드 원문 코드예제 기반(역직렬화 resolveClass 화이트리스트,
# 전자서명 getCodeSigners, DNS getRemoteAddr, 키 길이 RSA 2048 등).
# 모든 정탐 모범답안은 LASHR 구조검증 통과 + negKw 비충돌(harness 강제).

PART = [

    # ============================================================
    # EX-01 (상, TP) 신뢰할 수 없는 데이터의 역직렬화 (CWE-502) - Java
    # ============================================================
    {'id':'EX-01','lang':'Java','cat':'코드오류','diff':'상',
     'title':'바이트 스트림 객체 역직렬화 검토',
     'code':'''public static Object deserialize(byte[] buffer)
        throws IOException, ClassNotFoundException {
    try (ByteArrayInputStream bais = new ByteArrayInputStream(buffer)) {
        // 입력값 검증 없이 임의 클래스를 역직렬화한다.
        try (ObjectInputStream ois = new ObjectInputStream(bais)) {
            return ois.readObject();
        }
    }
}''',
     'isTruePositive':True,'weaknessName':'신뢰할 수 없는 데이터의 역직렬화','cwe':'CWE-502',
     'reasonKeywords':['readObject','임의 클래스','검증 없는 역직렬화','가젯 체인','원격 코드 실행'],
     'negKw':['XML 외부 개체','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public class WhitelistedObjectInputStream extends ObjectInputStream {
    private final Set<String> whitelist;
    public WhitelistedObjectInputStream(InputStream in, Set<String> wl) throws IOException {
        super(in);
        this.whitelist = wl;
    }
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc)
            throws IOException, ClassNotFoundException {
        // 화이트리스트에 없는 클래스의 역직렬화를 거부한다.
        if (!whitelist.contains(desc.getName())) {
            throw new InvalidClassException("비인가 클래스", desc.getName());
        }
        return super.resolveClass(desc);
    }
}''',
     'safeCodeKeywords':['resolveClass','whitelist','WhitelistedObjectInputStream'],
     'explanation':'외부에서 받은 바이트 스트림을 검증 없이 readObject로 역직렬화하면 공격자가 가젯 체인을 담은 객체를 보내 임의 코드를 실행시킬 수 있습니다. ObjectInputStream을 상속해 resolveClass에서 허용 클래스 화이트리스트만 통과시켜야 합니다.'},

    # ============================================================
    # EX-02 (상, TP) 부적절한 전자서명 확인 (CWE-347) - Java
    # ============================================================
    {'id':'EX-02','lang':'Java','cat':'보안기능','diff':'상',
     'title':'JAR 코드 로딩 시 전자서명 확인 검토',
     'code':'''public byte[] load(JarFile jar, String path) throws IOException {
    Enumeration<JarEntry> ens = jar.entries();
    while (ens.hasMoreElements()) {
        JarEntry en = ens.nextElement();
        if (path.equals(en.toString())) {
            // 전자서명 주체 확인 없이 코드를 그대로 로딩한다.
            return readAll(jar.getInputStream(en), en.getSize());
        }
    }
    return null;
}''',
     'isTruePositive':True,'weaknessName':'부적절한 전자서명 확인','cwe':'CWE-347',
     'reasonKeywords':['전자서명 미검증','getCodeSigners 미사용','무결성 미확인','위변조 코드','서명 주체'],
     'negKw':['무결성 검사 없는 코드 다운로드','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public byte[] load(JarFile jar, String path) throws IOException {
    Enumeration<JarEntry> ens = jar.entries();
    while (ens.hasMoreElements()) {
        JarEntry en = ens.nextElement();
        if (path.equals(en.toString())) {
            byte[] data = readAll(jar.getInputStream(en), en.getSize());
            // 전자서명 주체를 확인해 서명되지 않은 코드를 거부한다.
            CodeSigner[] signers = en.getCodeSigners();
            if (signers == null || signers.length == 0) {
                throw new SecurityException("서명되지 않은 코드");
            }
            return data;
        }
    }
    return null;
}''',
     'safeCodeKeywords':['getCodeSigners','signers'],
     'explanation':'JAR에서 클래스를 읽어 실행하면서 전자서명 주체를 확인하지 않으면 위변조된 코드를 그대로 신뢰해 실행하게 됩니다. JarEntry.getCodeSigners로 서명 주체를 확인하고 서명되지 않은 코드는 거부해야 합니다.'},

    # ============================================================
    # EX-03 (중, TP) 충분하지 않은 키 길이 사용 (CWE-326) - Java
    # ============================================================
    {'id':'EX-03','lang':'Java','cat':'보안기능','diff':'중',
     'title':'RSA 키쌍 생성 키 길이 검토',
     'code':'''public KeyPair genKey() throws Exception {
    KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
    // 공개키 길이를 1024비트로 생성한다.
    kpg.initialize(1024);
    return kpg.generateKeyPair();
}''',
     'isTruePositive':True,'weaknessName':'충분하지 않은 키 길이 사용','cwe':'CWE-326',
     'reasonKeywords':['RSA 1024','짧은 키 길이','전수 공격','권고 미달'],
     'negKw':['취약한 암호화 알고리즘','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public KeyPair genKey() throws Exception {
    KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
    // 공개키는 최소 2048비트 이상으로 생성한다(KISA 권고).
    kpg.initialize(2048);
    return kpg.generateKeyPair();
}''',
     'safeCodeKeywords':['initialize','2048','RSA'],
     'explanation':'알고리즘이 안전해도 RSA 공개키 길이가 1024비트로 짧으면 전수 공격으로 키를 찾아낼 수 있습니다. KISA 암호 가이드는 RSA 공개키를 2048비트 이상(보안강도 112비트 이상)으로 사용하도록 권고합니다.'},

    # ============================================================
    # EX-04 (중, TP) 취약한 암호화 알고리즘 사용 — MD5 (CWE-327) - Java
    # ============================================================
    {'id':'EX-04','lang':'Java','cat':'보안기능','diff':'중',
     'title':'무결성 검증용 해시 알고리즘 검토',
     'code':'''public byte[] checksum(byte[] data) throws Exception {
    // 충돌 공격에 취약한 MD5로 무결성 값을 계산한다.
    MessageDigest md = MessageDigest.getInstance("MD5");
    return md.digest(data);
}''',
     'isTruePositive':True,'weaknessName':'취약한 암호화 알고리즘 사용','cwe':'CWE-327',
     'reasonKeywords':['MD5','충돌 공격','취약한 해시','안전성 미흡'],
     'negKw':['키 길이','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public byte[] checksum(byte[] data) throws Exception {
    // 안전성이 보장되는 SHA-256 해시를 사용한다.
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    return md.digest(data);
}''',
     'safeCodeKeywords':['SHA-256','MessageDigest','digest'],
     'explanation':'MD5는 충돌을 의도적으로 만들 수 있어 무결성·서명 용도로 더 이상 안전하지 않습니다. KISA가 안전하다고 분류한 SHA-256 등 SHA-2 계열 해시로 교체해야 합니다.'},

    # ============================================================
    # EX-05 (상, TP) DNS lookup에 의존한 보안 결정 (CWE-350) - Java
    # ============================================================
    {'id':'EX-05','lang':'Java','cat':'API오용','diff':'상',
     'title':'요청 출처 신뢰 판단 로직 검토',
     'code':'''public boolean isTrusted(HttpServletRequest req) throws Exception {
    InetAddress addr = InetAddress.getByName(req.getRemoteAddr());
    // 도메인명(DNS)으로 신뢰 여부를 판단한다.
    return addr.getCanonicalHostName().endsWith("trustme.com");
}''',
     'isTruePositive':True,'weaknessName':'DNS lookup에 의존한 보안 결정','cwe':'CWE-350',
     'reasonKeywords':['getCanonicalHostName','DNS 캐시 변조','도메인 기반 신뢰','스푸핑'],
     'negKw':['SSRF','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public boolean isTrusted(HttpServletRequest req) {
    String ip = req.getRemoteAddr();
    if (ip == null || "".equals(ip)) return false;
    // DNS 호스트명 대신 IP 주소를 직접 비교해 DNS 변조에 방어한다.
    String trustedAddr = "10.0.0.5";
    return ip.equals(trustedAddr);
}''',
     'safeCodeKeywords':['getRemoteAddr','trustedAddr','equals'],
     'explanation':'공격자가 DNS 캐시를 오염시키면 getCanonicalHostName이 반환하는 도메인명을 위조할 수 있어 도메인 기반 신뢰 판단은 우회됩니다. 보안 결정에는 getRemoteAddr로 얻은 IP 주소를 직접 비교해야 합니다.'},

    # ============================================================
    # EX-06 (중, TP) 오류 상황 대응 부재 — 빈 catch (CWE-391) - Java
    # ============================================================
    {'id':'EX-06','lang':'Java','cat':'에러처리','diff':'중',
     'title':'예외 처리 구문 누락 여부 검토(설계 산출물 연계)',
     'code':'''public void process(String data) {
    try {
        risky(data);
    } catch (IOException e) {
    }
}''',
     'isTruePositive':True,'weaknessName':'오류 상황 대응 부재','cwe':'CWE-391',
     'reasonKeywords':['빈 catch','예외 무시','오류 미처리','로깅 부재','상태 미복구'],
     'negKw':['오류 메시지 정보 노출','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void process(String data) {
    try {
        risky(data);
    } catch (IOException e) {
        // 예외를 로깅하고 상위로 전파해 오류 상황에 대응한다.
        logger.error("처리 실패", e);
        throw new ServiceException("처리 중 오류", e);
    }
}''',
     'safeCodeKeywords':['logger.error','throw','catch'],
     'explanation':'catch 블록을 비워 두면 예외가 조용히 무시되어 오류 상황에서 시스템이 잘못된 상태로 계속 진행됩니다. 예외를 로깅하고 상위로 전파하거나 적절히 복구해 오류 상황에 대응해야 합니다.'},

    # ============================================================
    # EX-07 (상, TP) 메모리 버퍼 오버플로우 (CWE-120) - C
    # ============================================================
    {'id':'EX-07','lang':'C','cat':'입력검증','diff':'상',
     'title':'문자열 복사 버퍼 처리 검토(설계 요구사항 연계)',
     'code':'''void copyName(const char *input) {
    char buf[64];
    // 입력 길이를 확인하지 않고 복사해 버퍼 경계를 넘을 수 있다.
    strcpy(buf, input);
    printf("%s", buf);
}''',
     'isTruePositive':True,'weaknessName':'메모리 버퍼 오버플로우','cwe':'CWE-120',
     'reasonKeywords':['strcpy','경계 검사 없음','버퍼 크기 초과','스택 손상','널 종단 미보장'],
     'negKw':['정수형 오버플로우','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''void copyName(const char *input) {
    char buf[64];
    // 대상 버퍼 크기만큼만 복사하고 널 종단을 보장한다.
    strncpy(buf, input, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\\0';
    printf("%s", buf);
}''',
     'safeCodeKeywords':['strncpy','sizeof'],
     'explanation':'strcpy는 입력 길이를 확인하지 않고 복사하므로 64바이트 버퍼를 넘는 입력이 들어오면 인접 메모리를 덮어써 스택이 손상됩니다. 대상 크기만큼만 복사하는 strncpy를 쓰고 마지막에 널 문자를 직접 넣어 종단을 보장해야 합니다.'},

    # ============================================================
    # EX-08 (상, TP) 정수형 오버플로우 (CWE-190) - C
    # ============================================================
    {'id':'EX-08','lang':'C','cat':'입력검증','diff':'상',
     'title':'수량×단가 계산 정수 처리 검토(설계 요구사항 연계)',
     'code':'''int totalPrice(int unit, int qty) {
    // 입력 검증 없이 곱셈하여 정수 범위를 넘을 수 있다.
    return unit * qty;
}''',
     'isTruePositive':True,'weaknessName':'정수형 오버플로우','cwe':'CWE-190',
     'reasonKeywords':['곱셈 오버플로우','경계 검사 없음','정수 범위 초과','음수 우회','잘못된 할당 크기'],
     'negKw':['메모리 버퍼 오버플로우','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''int totalPrice(int unit, int qty) {
    // 곱셈 전에 오버플로우 가능성을 검사한다.
    if (qty < 0 || (qty != 0 && unit > INT_MAX / qty)) {
        return -1;
    }
    return unit * qty;
}''',
     'safeCodeKeywords':['INT_MAX','qty'],
     'explanation':'unit*qty 결과가 int 최대값을 넘으면 값이 음수로 뒤집혀 잘못된 금액·할당 크기로 이어집니다. 곱셈 전에 qty 범위와 unit > INT_MAX / qty 조건으로 오버플로우 가능성을 검사해야 합니다.'},

    # ============================================================
    # EX-09 (중, FP) 암호화되지 않은 중요정보 — 안전(오탐) - Java
    # ============================================================
    {'id':'EX-09','lang':'Java','cat':'보안기능','diff':'중',
     'title':'회원 비밀번호 저장·전송 처리 안전성 검토',
     'code':'''public void saveUser(String pw, HttpServletResponse resp) {
    // 비밀번호는 bcrypt로 해시해 저장하고, 세션 쿠키는 보안 전송한다.
    String hashed = BCrypt.hashpw(pw, BCrypt.gensalt());
    repo.save(hashed);
    Cookie c = new Cookie("sid", newSessionId());
    c.setSecure(true);
    c.setHttpOnly(true);
    resp.addCookie(c);
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['bcrypt 해시','setSecure','TLS 전송','평문 미저장','암호화 적용'],
     'negKw':['평문 저장','정탐','복호화 가능','노출 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'비밀번호를 bcrypt로 해시해 저장하고 세션 쿠키에 setSecure를 적용해 HTTPS로만 전송하므로 중요정보가 평문으로 드러나지 않는 안전한 코드(오탐)입니다.'},

    # ============================================================
    # EX-10 (중, FP) 솔트 적용 해시 — 안전(오탐) - Java
    # ============================================================
    {'id':'EX-10','lang':'Java','cat':'보안기능','diff':'중',
     'title':'비밀번호 해시 저장 로직 안전성 검토',
     'code':'''public byte[] hashPw(char[] pw, byte[] salt) throws Exception {
    // 사용자별 솔트와 PBKDF2(반복 65536회)로 적응형 해시한다.
    PBEKeySpec spec = new PBEKeySpec(pw, salt, 65536, 256);
    SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
    return f.generateSecret(spec).getEncoded();
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['PBKDF2','사용자별 솔트','적응형 해시','반복 횟수','레인보우 방어'],
     'negKw':['솔트 미적용','정탐','복원 가능','크랙 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'사용자별 솔트를 입력으로 받아 PBKDF2를 65536회 반복하는 적응형 해시이므로 레인보우 테이블·사전 공격에 견디는 안전한 코드(오탐)입니다.'},

    # ============================================================
    # EX-11 (상, TP) 크로스사이트 스크립트(XSS) (CWE-79) - Java (설계 산출물 연계)
    # ============================================================
    {'id':'EX-11','lang':'Java','cat':'입력검증','diff':'상',
     'title':'검색어 화면 출력 처리 검토(설계 산출물 연계)',
     'code':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String q = req.getParameter("q");
    // 외부 입력을 인코딩 없이 그대로 응답 본문에 출력한다.
    resp.getWriter().println("<div>" + q + "</div>");
}''',
     'isTruePositive':True,'weaknessName':'크로스사이트 스크립트(XSS)','cwe':'CWE-79',
     'reasonKeywords':['출력 인코딩 부재','스크립트 실행','반사형','검증 없는 출력'],
     'negKw':['경로 조작','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String q = req.getParameter("q");
    // 출력 전 HTML 메타문자를 이스케이프해 스크립트 실행을 차단한다.
    String safe = StringEscapeUtils.escapeHtml4(q);
    resp.getWriter().println("<div>" + safe + "</div>");
}''',
     'safeCodeKeywords':['escapeHtml4','escape'],
     'explanation':'외부 입력 q를 인코딩 없이 응답 본문에 출력하면 <script> 같은 태그가 그대로 실행되어 반사형 XSS가 발생합니다. 출력 직전에 escapeHtml4로 HTML 메타문자를 이스케이프해야 합니다.'},

]
