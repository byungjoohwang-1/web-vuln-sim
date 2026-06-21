# -*- coding: utf-8 -*-

PART = [

    # ============================================================
    # PC-01 (하, TP) 위험한 형식 파일 업로드 (CWE-434) - Java
    # ============================================================
    {'id':'PC-01','lang':'Java','cat':'입력검증','diff':'하',
     'title':'게시판 첨부파일 업로드 처리 검토',
     'code':'''public void upload(HttpServletRequest request) throws Exception {
    MultipartRequest multi = new MultipartRequest(
        request, savePath, sizeLimit, "euc-kr", new DefaultFileRenamePolicy());
    // 업로드되는 파일명을 검증 없이 그대로 저장에 사용한다.
    String fileName = multi.getFilesystemName("filename");
    PreparedStatement pstmt = conn.prepareStatement(SQL);
    pstmt.setString(6, fileName);
    pstmt.executeUpdate();
    Thumbnail.create(savePath + "/" + fileName, savePath + "/s_" + fileName, 150);
}''',
     'isTruePositive':True,'weaknessName':'위험한 형식 파일 업로드','cwe':'CWE-434',
     'reasonKeywords':['확장자 검증 없음','화이트리스트 미적용','jsp 업로드','웹쉘'],
     'negKw':['경로 조작','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void upload(HttpServletRequest request) throws Exception {
    MultipartRequest multi = new MultipartRequest(
        request, savePath, sizeLimit, "euc-kr", new DefaultFileRenamePolicy());
    String fileName = multi.getFilesystemName("filename");
    if (fileName != null) {
        String ext = fileName.substring(fileName.lastIndexOf(".") + 1).toLowerCase();
        // 화이트리스트 방식으로 허용 확장자만 업로드를 허용한다.
        if (!"gif".equals(ext) && !"jpg".equals(ext) && !"png".equals(ext)) {
            alertMessage("업로드 불가능한 파일입니다.");
            return;
        }
    }
}''',
     'safeCodeKeywords':['lastIndexOf','toLowerCase','gif'],
     'explanation':'업로드 파일의 확장자를 화이트리스트로 검증하지 않으므로 jsp 등 실행 가능한 파일(웹쉘)을 올려 서버에서 코드를 실행시킬 수 있어 위험한 형식 파일 업로드에 취약합니다. 허용 확장자만 통과시켜야 합니다.'},

    # ============================================================
    # PC-02 (중, TP) XML 삽입 (CWE-91) - Java XQuery
    # ============================================================
    {'id':'PC-02','lang':'Java','cat':'입력검증','diff':'중',
     'title':'사용자 정보 XML 조회 질의 생성 검토',
     'code':'''public XQResultSequence find(Properties props) throws Exception {
    String name = props.getProperty("name");
    // 외부 입력값을 검증 없이 XQuery 표현식에 문자열로 결합한다.
    String es = "doc('users.xml')/userlist/user[uname='" + name + "']";
    XQPreparedExpression expr = conn.prepareExpression(es);
    return expr.executeQuery();
}''',
     'isTruePositive':True,'weaknessName':'XML 삽입','cwe':'CWE-91',
     'reasonKeywords':['XQuery','문자열 결합','외부 입력','쿼리 구조 변경','bindString 미사용'],
     'negKw':['XML 외부 개체','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public XQResultSequence find(Properties props) throws Exception {
    String name = props.getProperty("name");
    // bindString으로 인자화하여 쿼리 구조 변경을 방지한다.
    String es = "doc('users.xml')/userlist/user[uname='$xname']";
    XQPreparedExpression expr = conn.prepareExpression(es);
    expr.bindString(new QName("xname"), name, null);
    return expr.executeQuery();
}''',
     'safeCodeKeywords':['bindString','$xname','QName'],
     'explanation':'외부 입력 name을 XQuery 표현식에 직접 결합하므로 공격자가 쿼리 구조를 변조해 권한 밖 데이터를 조회할 수 있는 XML 삽입에 취약합니다. bindString 등으로 인자를 바인딩해야 합니다.'},

    # ============================================================
    # PC-03 (중, TP) 크로스사이트 요청 위조(CSRF) (CWE-352) - Java
    # ============================================================
    {'id':'PC-03','lang':'Java','cat':'입력검증','diff':'중',
     'title':'회원 등급 변경 요청 처리 로직 검토',
     'code':'''public void updateLevel(HttpServletRequest request) {
    String id = request.getParameter("id");
    String level = request.getParameter("level");
    // 상태를 변경하는 요청이지만 토큰 검증 절차가 없다.
    memberService.updateLevel(id, level);
}''',
     'isTruePositive':True,'weaknessName':'크로스사이트 요청 위조(CSRF)','cwe':'CWE-352',
     'reasonKeywords':['CSRF 토큰 없음','상태 변경 요청','토큰 검증 누락','위조 요청'],
     'negKw':['XSS','부적절한 인가','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void updateLevel(HttpServletRequest request) {
    HttpSession session = request.getSession();
    String pToken = request.getParameter("param_csrf_token");
    String sToken = (String) session.getAttribute("SESSION_CSRF_TOKEN");
    // 요청 토큰과 세션 토큰이 일치할 때만 처리한다.
    if (pToken == null || !pToken.equals(sToken)) {
        throw new SecurityException("invalid csrf token");
    }
    String id = request.getParameter("id");
    String level = request.getParameter("level");
    memberService.updateLevel(id, level);
}''',
     'safeCodeKeywords':['param_csrf_token','SESSION_CSRF_TOKEN','equals'],
     'explanation':'회원 등급 변경이라는 상태 변경 요청을 CSRF 토큰 검증 없이 처리하므로 공격자가 피해자의 인증된 세션으로 위조 요청을 전송해 등급을 변조하는 CSRF에 취약합니다. 세션에 저장한 토큰과 대조해야 합니다.'},

    # ============================================================
    # PC-04 (중, TP) 정수형 오버플로우 (CWE-190) - Java
    # ============================================================
    {'id':'PC-04','lang':'Java','cat':'입력검증','diff':'중',
     'title':'요청 파라미터 기반 배열 생성 로직 검토',
     'code':'''public void process(HttpServletRequest request) {
    String tmp = StringUtil.isNullTrim(request.getParameter("slf_msg_param_num"));
    // 외부 입력값의 크기를 검증하지 않고 정수로 변환해 사용한다.
    int param_ct = Integer.parseInt(tmp);
    // param_ct가 음수가 되면 배열 크기가 음수가 되어 예외가 발생한다.
    String[] strArr = new String[param_ct];
}''',
     'isTruePositive':True,'weaknessName':'정수형 오버플로우','cwe':'CWE-190',
     'reasonKeywords':['크기 검증 없음','Integer.parseInt','배열 크기','음수 범위'],
     'negKw':['버퍼 오버플로우','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void process(HttpServletRequest request) {
    String tmp = StringUtil.isNullTrim(request.getParameter("slf_msg_param_num"));
    try {
        int param_ct = Integer.parseInt(tmp);
        // 음수 등 비정상 값 여부를 검증한 후 사용한다.
        if (param_ct < 0) {
            throw new IllegalArgumentException();
        }
        String[] strArr = new String[param_ct];
    } catch (Exception e) {
        msg_str = "잘못된 입력(접근) 입니다.";
    }
}''',
     'safeCodeKeywords':['param_ct < 0','IllegalArgumentException','try'],
     'explanation':'외부 입력값을 크기 검증 없이 정수로 변환해 배열 크기로 사용하므로, 연산 결과가 정수 범위를 넘어 음수가 되면 비정상 배열 생성으로 이어지는 정수형 오버플로우에 취약합니다. 사용 전 범위를 검증해야 합니다.'},

    # ============================================================
    # PC-05 (하, TP) 보안기능 결정에 사용되는 부적절한 입력값 (CWE-807) - Python
    # ============================================================
    {'id':'PC-05','lang':'Python','cat':'입력검증','diff':'하',
     'title':'비밀번호 초기화 권한 판단 로직 검토',
     'code':'''from django.shortcuts import render
def init_password(request):
    # 쿠키에서 권한 정보를 가져와 보안 결정에 사용한다.
    role = request.COOKIES['role']
    request_id = request.POST.get('user_id', '')
    request_mail = request.POST.get('user_email', '')
    if role == 'admin':
        password_init_and_sendmail(request_id, request_mail)
        return render(request, '/success.html')
    return render(request, '/failed.html')''',
     'isTruePositive':True,'weaknessName':'보안기능 결정에 사용되는 부적절한 입력값','cwe':'CWE-807',
     'reasonKeywords':['쿠키','클라이언트 조작 가능','권한 결정','신뢰할 수 없는 입력'],
     'negKw':['부적절한 인가','XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''from django.shortcuts import render
def init_password(request):
    # 서버가 관리하는 세션에서 권한 정보를 가져와 결정에 사용한다.
    role = request.session['role']
    request_id = request.POST.get('user_id', '')
    request_mail = request.POST.get('user_email', '')
    if role == 'admin':
        password_init_and_sendmail(request_id, request_mail)
        return render(request, '/success.html')
    return render(request, '/failed.html')''',
     'safeCodeKeywords':['request.session','role','admin'],
     'explanation':'관리자 여부라는 보안 결정을 클라이언트가 임의로 조작 가능한 쿠키 값에 의존하므로, role=admin 쿠키를 위조해 권한을 우회할 수 있는 부적절한 입력값 사용 약점에 취약합니다. 서버 측 세션 값으로 판단해야 합니다.'},

    # ============================================================
    # PC-06 (중, TP) 메모리 버퍼 오버플로우 (CWE-120) - C
    # ============================================================
    {'id':'PC-06','lang':'C','cat':'입력검증','diff':'중',
     'title':'구조체 버퍼로의 문자열 복사 로직 검토',
     'code':'''typedef struct _charvoid {
    char x[16];
    void *y;
    void *z;
} charvoid;

void badCode() {
    charvoid cv_struct;
    cv_struct.y = (void *) SRC_STR;
    /* sizeof(cv_struct) 만큼 복사하여 x 버퍼를 넘어 포인터 y를 덮어쓴다. */
    memcpy(cv_struct.x, SRC_STR, sizeof(cv_struct));
    printLine((char *) cv_struct.x);
}''',
     'isTruePositive':True,'weaknessName':'메모리 버퍼 오버플로우','cwe':'CWE-120',
     'reasonKeywords':['memcpy','sizeof(cv_struct)','버퍼 경계 초과','x[16] 덮어쓰기'],
     'negKw':['포맷 스트링','정수 오버플로우','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''typedef struct _charvoid {
    char x[16];
    void *y;
    void *z;
} charvoid;

static void goodCode() {
    charvoid cv_struct;
    cv_struct.y = (void *) SRC_STR;
    /* 대상 버퍼 크기 sizeof(cv_struct.x)만큼만 복사한다. */
    memcpy(cv_struct.x, SRC_STR, sizeof(cv_struct.x));
    /* 문자열 종료를 위해 널 문자를 삽입한다. */
    cv_struct.x[(sizeof(cv_struct.x) / sizeof(char)) - 1] = '\\0';
    printLine((char *) cv_struct.x);
}''',
     'safeCodeKeywords':['sizeof(cv_struct.x)','\\0','memcpy'],
     'explanation':'복사 크기를 대상 버퍼 x[16]가 아니라 구조체 전체 sizeof(cv_struct)로 지정해 버퍼 경계를 넘어 인접한 포인터 y를 덮어쓰므로 메모리 버퍼 오버플로우에 취약합니다. 대상 버퍼 크기만큼만 복사해야 합니다.'},

    # ============================================================
    # PC-07 (중, TP) 포맷 스트링 삽입 (CWE-134) - Java
    # ============================================================
    {'id':'PC-07','lang':'Java','cat':'입력검증','diff':'중',
     'title':'사용자 입력을 포함한 메시지 출력 로직 검토',
     'code':'''public static void main(String[] args) {
    Calendar validDate = Calendar.getInstance();
    validDate.set(2014, Calendar.OCTOBER, 14);
    // 외부 입력값 args[0]을 포맷 문자열에 직접 결합하여 출력한다.
    System.out.printf(args[0] + " did not match! HINT: issued on %1$terd", validDate);
}''',
     'isTruePositive':True,'weaknessName':'포맷 스트링 삽입','cwe':'CWE-134',
     'reasonKeywords':['printf','포맷 문자열','외부 입력 결합','정보 노출'],
     'negKw':['버퍼 오버플로우','XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public static void main(String[] args) {
    Calendar validDate = Calendar.getInstance();
    validDate.set(2014, Calendar.OCTOBER, 14);
    // 사용자 입력은 %s 인자로 전달하고 포맷 문자열은 고정한다.
    System.out.printf("%s did not match! HINT: issued on %2$terd", args[0], validDate);
}''',
     'safeCodeKeywords':['%s','args[0]','printf'],
     'explanation':'외부 입력 args[0]을 포맷 문자열 자체에 결합하므로 %x, %1$t 등 변환 지정자를 주입해 내부 메모리·날짜 등 민감 정보를 노출시키는 포맷 스트링 삽입에 취약합니다. 입력은 %s 인자로만 전달해야 합니다.'},

    # ============================================================
    # PC-08 (하, TP) 중요한 자원에 대한 잘못된 권한 설정 (CWE-732) - Python
    # ============================================================
    {'id':'PC-08','lang':'Python','cat':'보안기능','diff':'하',
     'title':'시스템 설정 파일 권한 부여 로직 검토',
     'code':'''import os
def write_file():
    # 모든 사용자에게 읽기, 쓰기, 실행 권한을 부여한다.
    os.chmod('/root/system_config', 0o777)
    with open("/root/system_config", 'w') as f:
        f.write("your config is broken")''',
     'isTruePositive':True,'weaknessName':'중요한 자원에 대한 잘못된 권한 설정','cwe':'CWE-732',
     'reasonKeywords':['chmod 0o777','과도한 권한','최소 권한 위배','모든 사용자'],
     'negKw':['하드코드된 중요정보','암호화되지 않은','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import os
def write_file():
    # 소유자에게만 권한을 부여하고 그 외에는 권한을 주지 않는다.
    os.chmod('/root/system_config', 0o700)
    with open("/root/system_config", 'w') as f:
        f.write("your config is broken")''',
     'safeCodeKeywords':['0o700','chmod','system_config'],
     'explanation':'중요한 설정 파일에 0o777로 모든 사용자에게 읽기·쓰기·실행 권한을 부여하므로 권한 없는 사용자가 설정을 변조·탈취할 수 있는 잘못된 권한 설정에 취약합니다. 최소 권한 원칙에 따라 소유자 권한(0o700)으로 제한해야 합니다.'},

    # ============================================================
    # PC-09 (하, TP) 암호화되지 않은 중요정보 (CWE-311) - Java
    # ============================================================
    {'id':'PC-09','lang':'Java','cat':'보안기능','diff':'하',
     'title':'회원 가입 시 비밀번호 저장 로직 검토',
     'code':'''public void register(HttpServletRequest request) throws Exception {
    String id = request.getParameter("id");
    String pwd = request.getParameter("pwd");
    String sql = "insert into customer(id, pwd) values (?, ?)";
    PreparedStatement stmt = con.prepareStatement(sql);
    stmt.setString(1, id);
    // 입력받은 비밀번호를 평문 그대로 DB에 저장한다.
    stmt.setString(2, pwd);
    stmt.executeUpdate();
}''',
     'isTruePositive':True,'weaknessName':'암호화되지 않은 중요정보','cwe':'CWE-311',
     'reasonKeywords':['평문 저장','비밀번호','암호화 미적용','DB 노출'],
     'negKw':['하드코드된 중요정보','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void register(HttpServletRequest request) throws Exception {
    String id = request.getParameter("id");
    String pwd = request.getParameter("pwd");
    // 솔트를 포함해 SHA-256 해시로 변환한 후 저장한다.
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    md.update(salt);
    byte[] hashInBytes = md.digest(pwd.getBytes());
    StringBuilder sb = new StringBuilder();
    for (byte b : hashInBytes) {
        sb.append(String.format("%02x", b));
    }
    pwd = sb.toString();
    PreparedStatement stmt = con.prepareStatement("insert into customer(id, pwd) values (?, ?)");
    stmt.setString(1, id);
    stmt.setString(2, pwd);
    stmt.executeUpdate();
}''',
     'safeCodeKeywords':['MessageDigest','SHA-256','salt'],
     'explanation':'비밀번호 같은 중요정보를 암호화·해시 처리 없이 평문으로 DB에 저장하므로 DB가 유출되면 그대로 노출되는 암호화되지 않은 중요정보 약점에 취약합니다. 솔트를 포함한 안전한 해시로 변환해 저장해야 합니다.'},

    # ============================================================
    # PC-10 (중, TP) 충분하지 않은 키 길이 사용 (CWE-326) - Python
    # ============================================================
    {'id':'PC-10','lang':'Python','cat':'보안기능','diff':'중',
     'title':'RSA 키쌍 생성 시 키 길이 설정 검토',
     'code':'''from Crypto.PublicKey import RSA
def make_rsa_key_pair():
    # RSA 키 길이를 1024비트로 짧게 설정한다.
    private_key = RSA.generate(1024)
    public_key = private_key.publickey()
    return private_key, public_key''',
     'isTruePositive':True,'weaknessName':'충분하지 않은 키 길이 사용','cwe':'CWE-326',
     'reasonKeywords':['RSA 1024','키 길이 부족','2048 미만','해독 가능'],
     'negKw':['취약한 암호화 알고리즘','적절하지 않은 난수값','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''from Crypto.PublicKey import RSA
def make_rsa_key_pair():
    # RSA 키 길이를 2048비트 이상으로 설정한다.
    private_key = RSA.generate(2048)
    public_key = private_key.publickey()
    return private_key, public_key''',
     'safeCodeKeywords':['RSA.generate(2048)','publickey','private_key'],
     'explanation':'RSA 키 길이를 권장 기준(2048비트)에 못 미치는 1024비트로 설정하므로 충분한 계산 자원으로 키가 해독될 수 있는 충분하지 않은 키 길이 사용 약점에 취약합니다. 공개키는 2048비트 이상으로 생성해야 합니다.'},
]
