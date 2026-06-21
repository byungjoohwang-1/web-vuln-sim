# -*- coding: utf-8 -*-

PRACTICAL = [
    {'id':'CD-01','lang':'Java','cat':'입력검증','diff':'하','title':'데이터베이스 사용자 조회 로직 검토',
     'code':'''public void process(HttpServletRequest request) {
    String id = request.getParameter("id");
    String query = "SELECT * FROM users WHERE id = '" + id + "'";
    Statement stmt = conn.createStatement();
    stmt.executeQuery(query);
}''',
     'isTruePositive':True,'weaknessName':'SQL 삽입','cwe':'CWE-89',
     'reasonKeywords':['Statement','문자열 결합','외부 입력','PreparedStatement 미사용'],
     'negKw':['XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void process(HttpServletRequest request) {
    String id = request.getParameter("id");
    String query = "SELECT * FROM users WHERE id = ?";
    PreparedStatement pstmt = conn.prepareStatement(query);
    pstmt.setString(1, id);
    pstmt.executeQuery();
}''',
     'safeCodeKeywords':['PreparedStatement','setString','prepareStatement'],
     'explanation':'외부 입력 id를 검증 없이 문자열 결합하여 동적 쿼리를 생성하므로 SQL 삽입에 취약합니다. PreparedStatement로 파라미터를 바인딩해야 합니다.'},

    {'id':'CD-02','lang':'Java','cat':'입력검증','diff':'중','title':'회원 ID 검색 로직 필터링 검토',
     'code':'''public void process(HttpServletRequest request) {
    String id = request.getParameter("id");
    if (id != null && id.matches("^[a-zA-Z0-9]{1,20}$")) {
        String query = "SELECT * FROM users WHERE id = '" + id + "'";
        Statement stmt = conn.createStatement();
        stmt.executeQuery(query);
    }
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['matches','정규식','화이트리스트','영문자와 숫자'],
     'negKw':['SQL 삽입 가능','정탐','삽입 가능','우회 가능','공격 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'Statement로 동적 쿼리를 만들지만 id가 영문자·숫자 1~20자만 허용하는 정규식 화이트리스트 검증을 통과하므로 SQL 삽입이 불가능한 안전한 코드(오탐)입니다.'},

    {'id':'CD-03','lang':'Java','cat':'입력검증','diff':'중','title':'고정 조건 통계 쿼리 검토',
     'code':'''public void countActive() {
    static final String STATUS = "ACTIVE";
    String query = "SELECT COUNT(*) FROM users WHERE status = '" + STATUS + "'";
    Statement stmt = conn.createStatement();
    stmt.executeQuery(query);
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['static final','내부 상수','외부 입력 아님','문자열 결합'],
     'negKw':['SQL 삽입 가능','정탐','삽입 가능','조작 가능','공격 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'문자열 결합으로 쿼리를 만들지만 결합되는 값이 외부 입력이 아닌 코드 내부의 static final 상수이므로 공격자가 조작할 수 없어 SQL 삽입이 불가능한 안전한 코드(오탐)입니다.'},

    {'id':'CD-04','lang':'Java','cat':'입력검증','diff':'하','title':'게시판 댓글 출력 화면 검토',
     'code':'''public void render(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String comment = req.getParameter("comment");
    PrintWriter out = resp.getWriter();
    out.println("<div>" + comment + "</div>");
}''',
     'isTruePositive':True,'weaknessName':'크로스사이트 스크립트(XSS)','cwe':'CWE-79',
     'reasonKeywords':['외부 입력','출력 인코딩 미적용','HTML 직접 출력','script 실행'],
     'negKw':['SQL','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void render(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String comment = req.getParameter("comment");
    String safe = org.apache.commons.text.StringEscapeUtils.escapeHtml4(comment);
    PrintWriter out = resp.getWriter();
    out.println("<div>" + safe + "</div>");
}''',
     'safeCodeKeywords':['escapeHtml4','StringEscapeUtils','safe'],
     'explanation':'외부 입력 comment를 인코딩 없이 HTML에 직접 출력하므로 스크립트가 실행되는 XSS에 취약합니다. 출력 시 HTML 엔티티로 인코딩해야 합니다.'},

    {'id':'CD-05','lang':'Java','cat':'입력검증','diff':'중','title':'검색어 출력 화면 이스케이프 검토',
     'code':'''public void render(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String keyword = req.getParameter("keyword");
    String safe = org.springframework.web.util.HtmlUtils.htmlEscape(keyword);
    PrintWriter out = resp.getWriter();
    out.println("<p>검색어: " + safe + "</p>");
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['htmlEscape','출력 인코딩','이스케이프','HtmlUtils'],
     'negKw':['XSS 가능','정탐','스크립트 실행','공격 가능','삽입 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'외부 입력을 출력하지만 htmlEscape()로 HTML 특수문자를 이스케이프한 후 출력하므로 스크립트가 실행되지 않는 안전한 코드(오탐)입니다.'},

    {'id':'CD-06','lang':'Java','cat':'입력검증','diff':'중','title':'파일 다운로드 경로 처리 검토',
     'code':'''public File getFile(HttpServletRequest req) {
    String name = req.getParameter("name");
    File file = new File("/data/files/" + name);
    return file;
}''',
     'isTruePositive':True,'weaknessName':'경로 조작 및 자원 삽입','cwe':'CWE-22',
     'reasonKeywords':['외부 입력','../','경로 검증 없음','디렉터리 트래버설'],
     'negKw':['SQL','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public File getFile(HttpServletRequest req) throws IOException {
    String name = req.getParameter("name").replaceAll("[\\\\/.]", "");
    File base = new File("/data/files/");
    File file = new File(base, name);
    if (!file.getCanonicalPath().startsWith(base.getCanonicalPath())) {
        throw new SecurityException("invalid path");
    }
    return file;
}''',
     'safeCodeKeywords':['getCanonicalPath','startsWith','replaceAll'],
     'explanation':'외부 입력 name을 검증 없이 경로에 결합하므로 ../ 등을 이용한 디렉터리 트래버설(경로 조작)에 취약합니다. 경로 문자 제거와 Canonical Path 하위 검증이 필요합니다.'},

    {'id':'CD-07','lang':'Java','cat':'입력검증','diff':'상','title':'첨부파일 경로 결합 안전성 검토',
     'code':'''public File getFile(HttpServletRequest req) throws IOException {
    String name = req.getParameter("name").replaceAll("[\\\\/]|\\.\\.", "");
    File base = new File("/data/files/");
    File f = new File(base, name);
    if (!f.getCanonicalPath().startsWith(base.getCanonicalPath())) return null;
    return f;
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['replaceAll','../ 제거','getCanonicalPath','startsWith','하위폴더 검증'],
     'negKw':['경로 조작 가능','정탐','트래버설 가능','우회 가능','공격 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'입력에서 경로 구분자와 ..를 제거하고 Canonical Path가 기준 디렉터리 하위인지 검증하므로 경로 조작이 불가능한 안전한 코드(오탐)입니다.'},

    {'id':'CD-08','lang':'Java','cat':'보안기능','diff':'하','title':'외부 시스템 연동 인증정보 관리 검토',
     'code':'''public Connection connect() throws SQLException {
    String url = "jdbc:mysql://10.0.0.5/app";
    String user = "admin";
    String password = "P@ssw0rd123!";
    return DriverManager.getConnection(url, user, password);
}''',
     'isTruePositive':True,'weaknessName':'하드코드된 중요정보','cwe':'CWE-798',
     'reasonKeywords':['하드코딩','비밀번호','소스코드 노출','password 상수'],
     'negKw':['XSS','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public Connection connect() throws SQLException {
    String url = System.getenv("DB_URL");
    String user = System.getenv("DB_USER");
    String password = System.getenv("DB_PASSWORD");
    return DriverManager.getConnection(url, user, password);
}''',
     'safeCodeKeywords':['getenv','DB_PASSWORD','System'],
     'explanation':'DB 접속 비밀번호가 소스코드에 평문으로 하드코딩되어 있어 소스 유출 시 노출됩니다. 환경변수나 안전한 외부 설정·키 저장소에서 읽어야 합니다.'},

    {'id':'CD-09','lang':'Java','cat':'보안기능','diff':'하','title':'비밀번호 저장용 해시 알고리즘 검토',
     'code':'''public String hash(String password) throws Exception {
    MessageDigest md = MessageDigest.getInstance("MD5");
    byte[] digest = md.digest(password.getBytes("UTF-8"));
    return Base64.getEncoder().encodeToString(digest);
}''',
     'isTruePositive':True,'weaknessName':'취약한 암호화 알고리즘 사용','cwe':'CWE-327',
     'reasonKeywords':['MD5','취약한 해시','충돌 공격','안전하지 않은 알고리즘'],
     'negKw':['안전한 코드','오탐','SQL','XSS'],
     'safeCode':'''public String hash(String password) throws Exception {
    MessageDigest md = MessageDigest.getInstance("SHA-256");
    byte[] digest = md.digest(password.getBytes("UTF-8"));
    return Base64.getEncoder().encodeToString(digest);
}''',
     'safeCodeKeywords':['SHA-256','MessageDigest','getInstance'],
     'explanation':'MD5는 충돌 공격에 취약하여 안전하지 않은 알고리즘입니다. SHA-256 이상(비밀번호는 솔트+적응형 해시 권장)을 사용해야 합니다.'},

    {'id':'CD-10','lang':'Python','cat':'코드오류','diff':'중','title':'사용자 프로필 조회 결과 처리 검토',
     'code':'''def get_email(user_id):
    user = db.find_user(user_id)
    return user.email.lower()''',
     'isTruePositive':True,'weaknessName':'Null Pointer 역참조','cwe':'CWE-476',
     'reasonKeywords':['None 반환','검사 없음','역참조','find_user'],
     'negKw':['SQL','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''def get_email(user_id):
    user = db.find_user(user_id)
    if user is None:
        return None
    return user.email.lower()''',
     'safeCodeKeywords':['if user is None','return','user.email'],
     'explanation':'find_user가 사용자를 찾지 못하면 None을 반환할 수 있는데 Null 검사 없이 멤버에 접근하므로 Null Pointer 역참조에 취약합니다. 사용 전 None 여부를 확인해야 합니다.'},

    {'id':'CD-11','lang':'Python','cat':'API오용','diff':'중','title':'외부 데이터 역직렬화 처리 검토',
     'code':'''import pickle
def load_session(data):
    obj = pickle.loads(data)
    return obj''',
     'isTruePositive':True,'weaknessName':'신뢰할 수 없는 데이터의 역직렬화','cwe':'CWE-502',
     'reasonKeywords':['pickle.loads','신뢰할 수 없는 입력','임의 코드 실행','역직렬화'],
     'negKw':['SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import json
def load_session(data):
    obj = json.loads(data)
    return obj''',
     'safeCodeKeywords':['json.loads','json','data'],
     'explanation':'외부에서 받은 데이터를 pickle로 역직렬화하면 악의적 페이로드로 임의 코드 실행이 가능합니다. 신뢰할 수 없는 데이터는 json 등 안전한 형식으로 처리해야 합니다.'},

    {'id':'CD-12','lang':'Python','cat':'입력검증','diff':'하','title':'관리자용 시스템 진단 명령 실행 검토',
     'code':'''import os
def ping(host):
    cmd = "ping -c 1 " + host
    os.system(cmd)''',
     'isTruePositive':True,'weaknessName':'운영체제 명령어 삽입','cwe':'CWE-78',
     'reasonKeywords':['os.system','외부 입력','명령어 결합','셸 메타문자'],
     'negKw':['SQL','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import subprocess
def ping(host):
    subprocess.run(["ping", "-c", "1", host], shell=False, check=True)''',
     'safeCodeKeywords':['subprocess.run','shell=False','["ping"'],
     'explanation':'외부 입력 host를 셸 명령 문자열에 결합하여 os.system으로 실행하므로 ; 등 메타문자를 이용한 OS 명령어 삽입에 취약합니다. 인자 배열과 shell=False로 실행해야 합니다.'},
]

THEORY = [
    # ---- OX (12) ----
    {'type':'OX','cat':'법령','q':'대한민국의 소프트웨어 개발보안 의무제는 2012년 12월부터 시행되었다.','a':True,'e':'2009~2011년 시범사업을 거쳐 2012년 12월부터 의무 적용되었습니다.'},
    {'type':'OX','cat':'법령','q':'소프트웨어 개발보안 적용의 근거는 「행정기관 및 공공기관 정보시스템 구축·운영 지침」(행정안전부 고시)이다.','a':True,'e':'해당 행정안전부 고시에 개발보안 적용 근거가 규정되어 있습니다.'},
    {'type':'OX','cat':'법령','q':'행정기관 정보시스템 감리 의무 대상은 통상 사업비 5억원 이상인 정보화사업이다.','a':True,'e':'일정 규모(통상 5억원) 이상의 정보화사업이 감리 의무 대상이며 개발보안 의무가 적용됩니다.'},
    {'type':'OX','cat':'법령','q':'보안약점 진단은 운영·폐기 단계에서만 수행하면 충분하다.','a':False,'e':'보안약점 진단은 구현/시험 단계에 수행하며 분석·설계 단계에서는 보안설계를 적용해 SDLC 전반에 반영합니다.'},
    {'type':'OX','cat':'법령','q':'개인정보보호법상 주민등록번호 등 고유식별정보와 비밀번호는 암호화하여 저장해야 한다.','a':True,'e':'개인정보보호법은 고유식별정보·비밀번호 등의 암호화 저장을 의무로 규정합니다.'},
    {'type':'OX','cat':'개념','q':'SQL 삽입을 막는 가장 근본적인 방법은 입력값을 블랙리스트로 일부 위험 문자만 제거하는 것이다.','a':False,'e':'블랙리스트는 우회가 쉬워 근본 대책이 아니며, PreparedStatement 파라미터 바인딩이 근본 대책입니다.'},
    {'type':'OX','cat':'개념','q':'저장형(Stored) XSS의 핵심 대응책은 사용자 입력을 화면에 출력할 때 출력 인코딩을 적용하는 것이다.','a':True,'e':'데이터 출력 위치(HTML, 속성, 스크립트 등)에 맞는 출력 인코딩이 XSS의 핵심 대응책입니다.'},
    {'type':'OX','cat':'개념','q':'보안 토큰·세션 식별자 생성에는 java.util.Random 같은 일반 난수 생성기를 사용하는 것이 권장된다.','a':False,'e':'예측 가능성이 낮은 SecureRandom 등 암호학적으로 안전한 난수생성기(CSPRNG)를 사용해야 합니다.'},
    {'type':'OX','cat':'개념','q':'TOCTOU는 검사 시점과 사용 시점 사이의 상태 변화로 발생하는 경쟁조건 취약점이다.','a':True,'e':'Time-Of-Check to Time-Of-Use, 즉 검사시점과 사용시점의 불일치로 인한 경쟁조건입니다.'},
    {'type':'OX','cat':'개념','q':'비밀번호 저장 시 솔트(salt)를 사용하면 동일한 비밀번호라도 서로 다른 해시값이 생성된다.','a':True,'e':'사용자별 고유 솔트를 사용하면 같은 비밀번호도 다른 해시가 되어 레인보우 테이블 공격을 방어합니다.'},
    {'type':'OX','cat':'개념','q':'최소 권한 원칙은 사용자·프로세스에 업무 수행에 필요한 최소한의 권한만 부여하는 것이다.','a':True,'e':'필요 이상 권한 부여를 막아 피해 범위를 최소화하는 보안 설계 원칙입니다.'},
    {'type':'OX','cat':'개념','q':'CWE는 소프트웨어의 보안약점 유형을 분류·식별하기 위한 공통 약점 목록이다.','a':True,'e':'CWE(Common Weakness Enumeration)는 소프트웨어 보안약점을 표준화해 분류한 목록입니다.'},

    # ---- SHORT (8) ----
    {'type':'SHORT','cat':'개념','q':'SQL 삽입을 근본적으로 막기 위해 입력값과 SQL 명령을 분리하는 Java의 대표 API는?','answers':['PreparedStatement','파라미터 바인딩','프리페어드스테이트먼트'],'e':'PreparedStatement로 파라미터를 바인딩하면 입력이 명령 구조를 바꾸지 못합니다.'},
    {'type':'SHORT','cat':'개념','q':'XSS를 방지하기 위해 사용자 입력을 화면에 표시하기 전 HTML 특수문자를 안전한 형태로 바꾸는 처리를 무엇이라 하는가?','answers':['출력 인코딩','이스케이프','HTML 인코딩','출력 이스케이프'],'e':'출력 위치에 맞는 출력 인코딩(이스케이프)으로 스크립트 실행을 차단합니다.'},
    {'type':'SHORT','cat':'개념','q':'예측 불가능성을 보장해 보안용 난수 생성에 사용해야 하는, 암호학적으로 안전한 난수생성기를 가리키는 영문 약어는?','answers':['CSPRNG','SecureRandom'],'e':'CSPRNG(Cryptographically Secure PRNG), Java에서는 SecureRandom이 대표적입니다.'},
    {'type':'SHORT','cat':'개념','q':'검사 시점(Time-Of-Check)과 사용 시점(Time-Of-Use) 사이의 상태 변화를 악용하는 경쟁조건 취약점의 약어는?','answers':['TOCTOU','TOCTTOU'],'e':'TOCTOU는 검사와 사용 사이의 시간차로 인한 경쟁조건 취약점입니다.'},
    {'type':'SHORT','cat':'개념','q':'OS 명령어 삽입을 방지하기 위해 명령과 인자를 분리하고 셸을 거치지 않도록 Python에서 권장되는 모듈은?','answers':['subprocess','서브프로세스'],'e':'subprocess로 인자 배열을 전달하고 shell=False로 실행하면 셸 메타문자 해석을 피할 수 있습니다.'},
    {'type':'SHORT','cat':'개념','q':'경로 조작 방지를 위해 입력으로 만든 파일 경로를 정규화하여 실제 절대경로로 변환한 뒤 허용 디렉터리 하위인지 검증할 때, 이 정규화된 경로를 무엇이라 하는가?','answers':['Canonical Path','정규 경로','캐노니컬 패스'],'e':'getCanonicalPath() 등으로 얻은 정규 경로가 기준 디렉터리 하위인지 검사합니다.'},
    {'type':'SHORT','cat':'법령','q':'구현단계에서 점검하는 KISA 소프트웨어 보안약점은 총 몇 개인가? (숫자만)','answers':['49','49개'],'e':'KISA 가이드 기준 구현단계 보안약점은 7대 유형, 총 49개입니다.'},
    {'type':'SHORT','cat':'개념','q':'비밀번호를 안전하게 저장하기 위해 솔트와 함께 사용하는, 의도적으로 계산을 느리게 한 해시 방식을 무엇이라 하는가?','answers':['적응형 해시','bcrypt','PBKDF2','scrypt','Argon2'],'e':'bcrypt, PBKDF2, scrypt, Argon2 같은 적응형(키 스트레칭) 해시로 무차별 대입을 어렵게 합니다.'},

    # ---- MC (6) ----
    {'type':'MC','cat':'법령','q':'소프트웨어 개발보안 의무제의 근거가 되는 행정안전부 고시는?','o':['정보통신망법 시행령','행정기관 및 공공기관 정보시스템 구축·운영 지침','개인정보 안전성 확보조치 기준','전자정부법 시행규칙'],'a':1,'e':'「행정기관 및 공공기관 정보시스템 구축·운영 지침」에 개발보안 적용 근거가 있습니다.'},
    {'type':'MC','cat':'법령','q':'소프트웨어 개발보안에서 보안약점 진단을 주로 수행하는 단계로 가장 적절한 것은?','o':['기획 단계','요구사항 정의 단계','구현/시험 단계','폐기 단계'],'a':2,'e':'보안약점 진단은 구현/시험 단계에서 수행하며 분석·설계 단계에는 보안설계를 적용합니다.'},
    {'type':'MC','cat':'개념','q':'다음 중 SQL 삽입에 대한 근본적 대응책으로 가장 적절한 것은?','o':['에러 메시지 숨기기','PreparedStatement 파라미터 바인딩','HTTPS 적용','입력 길이만 제한'],'a':1,'e':'입력과 명령을 분리하는 파라미터 바인딩이 근본 대책입니다.'},
    {'type':'MC','cat':'개념','q':'비밀번호 저장 시 가장 권장되는 방식은?','o':['MD5 단순 해시','평문 저장','솔트 + 적응형 해시(bcrypt 등)','Base64 인코딩'],'a':2,'e':'사용자별 솔트와 bcrypt 등 적응형 해시를 함께 사용하는 것이 권장됩니다.'},
    {'type':'MC','cat':'법령','q':'개인정보보호법상 반드시 암호화하여 저장해야 하는 정보로 옳은 것은?','o':['공개된 회사명','주민등록번호 등 고유식별정보와 비밀번호','게시글 제목','접속 IP만'],'a':1,'e':'주민등록번호 등 고유식별정보와 비밀번호는 암호화 저장 의무 대상입니다.'},
    {'type':'MC','cat':'개념','q':'CWE(Common Weakness Enumeration)에 대한 설명으로 옳은 것은?','o':['알려진 공개 취약점(제품 인스턴스) 식별 번호','소프트웨어 보안약점 유형 분류 목록','암호화 알고리즘 표준','네트워크 포트 번호 체계'],'a':1,'e':'CWE는 보안약점 유형 분류 체계이며, 개별 공개 취약점 식별은 CVE입니다.'},
]

# 확장 실무 문제 병합: CD-13~CD-30(난이도·부정키워드) + PC-01~PC-29(49 약점 정탐 커버리지)
import importlib as _il
PRACTICAL = PRACTICAL + _il.import_module('_practical_new').PRACTICAL_NEW
for _mod in ('_prac_cov1', '_prac_cov2', '_prac_cov3', '_prac_ext', '_prac_exam2412'):
    PRACTICAL = PRACTICAL + _il.import_module(_mod).PART

# 1교시 이론 확장 병합: KISA 7대 유형 균형 + 법령/진단 + 기출(2024.12) 단답
THEORY = (THEORY + _il.import_module('_theory_ext').PART
          + _il.import_module('_theory_exam').PART
          + _il.import_module('_theory_exam2').PART
          + _il.import_module('_theory_exam3').PART)
