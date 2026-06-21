# -*- coding: utf-8 -*-
PART = [

    # ============================================================
    # PC-11 (하, TP) 취약한 비밀번호 허용 (CWE-521)
    # ============================================================
    {'id':'PC-11','lang':'Python','cat':'보안기능','diff':'하',
     'title':'회원 가입 비밀번호 등록 처리 검토',
     'code':'''@app.route('/register', methods=['POST'])
def register():
    userid = request.form.get('userid')
    password = request.form.get('password')
    confirm = request.form.get('confirm_password')
    if password != confirm:
        return make_response("패스워드가 일치하지 않습니다", 400)
    user = User()
    user.userid = userid
    user.password = password
    db.session.add(user)
    db.session.commit()
    return make_response("회원가입 성공", 200)''',
     'isTruePositive':True,'weaknessName':'취약한 비밀번호 허용','cwe':'CWE-521',
     'reasonKeywords':['복잡도 검증 없음','자릿수','특수문자','조합규칙 미확인'],
     'negKw':['하드코드된 중요정보','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import re
def check_password(password):
    PT = re.compile('^(?=.*[A-Za-z])(?=.*[0-9@#$%^&*]).{8,}$')
    return bool(PT.match(password))

@app.route('/register', methods=['POST'])
def register():
    userid = request.form.get('userid')
    password = request.form.get('password')
    confirm = request.form.get('confirm_password')
    if password != confirm:
        return make_response("패스워드가 일치하지 않습니다", 400)
    if not check_password(password):
        return make_response("패스워드 조합규칙에 맞지 않습니다", 400)
    user = User()
    user.userid = userid
    user.password = password
    db.session.add(user)
    db.session.commit()
    return make_response("회원가입 성공", 200)''',
     'safeCodeKeywords':['check_password','re.compile','{8,}'],
     'explanation':'가입 시 비밀번호의 자릿수·특수문자 포함 여부 등 복잡도(조합규칙)를 전혀 검증하지 않으므로 1234 같은 취약한 비밀번호가 허용됩니다. 길이와 문자 조합 규칙을 검증해야 합니다.'},

    # ============================================================
    # PC-12 (중, TP) 부적절한 전자서명 확인 (CWE-347)
    # ============================================================
    {'id':'PC-12','lang':'Python','cat':'보안기능','diff':'중',
     'title':'클라이언트가 전달한 코드 실행 전 검증 로직 검토',
     'code':'''def verify_data(request):
    encrypted_code = request.POST.get("encrypted_msg", "")
    with open(f"{PATH}/keys/secret_key.out", "rb") as f:
        secret_key = f.read()
    origin_python_code = decrypt_with_symmetric_key(secret_key, encrypted_code)
    # 전자서명 검증 없이 전달받은 코드를 그대로 실행
    eval(origin_python_code)''',
     'isTruePositive':True,'weaknessName':'부적절한 전자서명 확인','cwe':'CWE-347',
     'reasonKeywords':['전자서명 미검증','서명 확인 없음','위변조 탐지 불가','신뢰할 수 없는 출처'],
     'negKw':['코드 삽입','신뢰할 수 없는 데이터의 역직렬화','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as SIGNATURE_PKCS1_v1_5
import base64

def verify_signature(origin_data, origin_signature, client_pub_key):
    hashed = SHA256.new(origin_data)
    signer = SIGNATURE_PKCS1_v1_5.new(RSA.importKey(client_pub_key))
    return signer.verify(hashed, base64.b64decode(origin_signature))

def verify_data(request):
    # 클라이언트 공개키로 원문과 전자서명을 검증한 뒤에만 실행
    if verify_signature(origin_python_code, origin_signature, client_pub_key):
        eval(origin_python_code)''',
     'safeCodeKeywords':['verify_signature','signer.verify','PKCS1_v1_5'],
     'explanation':'전달받은 코드의 전자서명을 검증하지 않고 복호화 후 바로 실행하므로 송신자 위변조·내용 변조를 탐지할 수 없는 부적절한 전자서명 확인 약점이 있습니다. 실행 전 공개키로 서명을 검증해야 합니다.'},

    # ============================================================
    # PC-13 (중, TP) 부적절한 인증서 유효성 검증 (CWE-295)
    # ============================================================
    {'id':'PC-13','lang':'Python','cat':'보안기능','diff':'중',
     'title':'서버와의 SSL 연결 설정 로직 검토',
     'code':'''import socket
import ssl
HOST, PORT = "127.0.0.1", 7917
def connect_with_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        context = ssl.SSLContext()
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(sock) as ssock:
            ssock.connect((HOST, PORT))
            ssock.send("hello".encode("utf-8"))''',
     'isTruePositive':True,'weaknessName':'부적절한 인증서 유효성 검증','cwe':'CWE-295',
     'reasonKeywords':['CERT_NONE','인증서 검증 안 함','중간자 공격','서버 신뢰 불가'],
     'negKw':['부적절한 전자서명 확인','취약한 암호화 알고리즘 사용','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import ssl
HOST, PORT = "127.0.0.1", 7917
SERVER_CA_PEM = "./rsa_server/CA.pem"
def connect_with_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        # PROTOCOL_TLS_CLIENT는 verify_mode=CERT_REQUIRED, check_hostname=True
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(SERVER_CA_PEM)
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            ssock.connect((HOST, PORT))''',
     'safeCodeKeywords':['PROTOCOL_TLS_CLIENT','load_verify_locations','wrap_socket'],
     'explanation':'verify_mode를 CERT_NONE으로 설정해 서버 인증서를 검증하지 않으므로 중간자 공격에 노출되는 부적절한 인증서 유효성 검증 약점이 있습니다. CERT_REQUIRED와 호스트 이름 확인을 적용해야 합니다.'},

    # ============================================================
    # PC-14 (하, TP) 사용자 하드디스크에 저장되는 쿠키를 통한 정보 노출 (CWE-539)
    # ============================================================
    {'id':'PC-14','lang':'Python','cat':'보안기능','diff':'하',
     'title':'로그인 유지 쿠키 발급 처리 검토',
     'code':'''from django.http import HttpResponse

def remind_user_state(request):
    res = HttpResponse()
    # 만료시간을 1년으로 길게 설정하여 디스크에 영속 저장됨
    res.set_cookie('rememberme', 1, max_age=60*60*24*365)
    return res''',
     'isTruePositive':True,'weaknessName':'사용자 하드디스크에 저장되는 쿠키를 통한 정보 노출','cwe':'CWE-539',
     'reasonKeywords':['과도한 만료시간','max_age 1년','디스크 영속 저장','secure httponly 미설정'],
     'negKw':['하드코드된 중요정보','HTTP 응답 분할','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''from django.http import HttpResponse

def remind_user_state(request):
    res = HttpResponse()
    # 만료시간을 최소로 두고 secure, httponly 옵션을 활성화
    res.set_cookie('rememberme', 1, max_age=60*60, secure=True, httponly=True)
    return res''',
     'safeCodeKeywords':['max_age=60*60','secure=True','httponly=True'],
     'explanation':'쿠키 만료시간을 1년으로 과도하게 길게 설정해 사용자 하드디스크에 영속 저장되므로 단말 탈취 시 정보가 노출됩니다. 만료시간을 최소로 하고 secure·httponly 옵션을 적용해야 합니다.'},

    # ============================================================
    # PC-15 (하, TP) 주석문 안에 포함된 시스템 주요정보 (CWE-615)
    # ============================================================
    {'id':'PC-15','lang':'Java','cat':'보안기능','diff':'하',
     'title':'DB 연결 처리 코드 주석 검토',
     'code':'''public Connection getConnection() throws SQLException {
    // DB연결 root / a1q2w3r3f2!@
    Connection con = DriverManager.getConnection(URL, USER, PASS);
    return con;
}''',
     'isTruePositive':True,'weaknessName':'주석문 안에 포함된 시스템 주요정보','cwe':'CWE-615',
     'reasonKeywords':['주석에 계정정보','비밀번호 노출','DB 접속정보','소스 유출 시 노출'],
     'negKw':['하드코드된 중요정보','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public Connection getConnection() throws SQLException {
    // 중요 정보는 주석에 포함하지 않는다
    Connection con = DriverManager.getConnection(URL, USER, PASS);
    return con;
}''',
     'safeCodeKeywords':['DriverManager.getConnection','return con','Connection con'],
     'explanation':'주석문에 DB 연결 계정과 비밀번호(root / a1q2w3r3f2!@)가 남아 있어 소스코드 유출 시 주요정보가 노출됩니다. 인증 정보 등 중요정보는 주석에 포함해서는 안 됩니다.'},

    # ============================================================
    # PC-16 (중, TP) 무결성 검사 없는 코드 다운로드 (CWE-494)
    # ============================================================
    {'id':'PC-16','lang':'Python','cat':'보안기능','diff':'중',
     'title':'원격 코드 다운로드 후 저장 처리 검토',
     'code':'''import requests

def execute_remote_code():
    url = "https://www.somewhere.com/storage/code.py"
    file = requests.get(url)
    remote_code = file.content
    with open('save.py', 'wb') as f:
        f.write(remote_code)
    exec(remote_code)''',
     'isTruePositive':True,'weaknessName':'무결성 검사 없는 코드 다운로드','cwe':'CWE-494',
     'reasonKeywords':['무결성 검증 없음','해시 미검증','원격 코드 다운로드','변조 탐지 불가'],
     'negKw':['서버사이드 요청 위조(SSRF)','코드 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import requests
import hashlib

def execute_remote_code(expected_hash):
    url = "https://www.somewhere.com/storage/code.py"
    remote_code = requests.get(url).content
    sha = hashlib.sha256()
    sha.update(remote_code)
    if sha.hexdigest() != expected_hash:
        raise Exception('파일이 손상되었습니다')
    with open('save.py', 'wb') as f:
        f.write(remote_code)
    exec(remote_code)''',
     'safeCodeKeywords':['hashlib.sha256','hexdigest','expected_hash'],
     'explanation':'원격에서 받은 코드를 무결성 검증 없이 저장·실행하므로 전송 중 변조되거나 악성 코드로 교체되어도 탐지하지 못하는 무결성 검사 없는 코드 다운로드 약점이 있습니다. 사전 공유 해시·서명으로 무결성을 검증해야 합니다.'},

    # ============================================================
    # PC-17 (중, TP) 반복된 인증시도 제한 기능 부재 (CWE-307)
    # ============================================================
    {'id':'PC-17','lang':'Java','cat':'보안기능','diff':'중',
     'title':'소켓 기반 로그인 인증 반복 처리 검토',
     'code':'''public void login() {
    int result = FAIL;
    try {
        Socket socket = new Socket(SERVER_IP, SERVER_PORT);
        while (result == FAIL) {
            String username = readUsername();
            String password = readPassword();
            result = verifyUser(username, password);
        }
    } catch (IOException e) {
        log.error("login error");
    }
}''',
     'isTruePositive':True,'weaknessName':'반복된 인증시도 제한 기능 부재','cwe':'CWE-307',
     'reasonKeywords':['시도 횟수 제한 없음','무한 반복','무차별 대입','잠금 없음'],
     'negKw':['종료되지 않는 반복문 또는 재귀함수','적절한 인증 없는 중요기능 허용','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''private static final int MAX_ATTEMPTS = 5;
public void login() {
    int result = FAIL;
    int count = 0;
    try {
        Socket socket = new Socket(SERVER_IP, SERVER_PORT);
        while (result == FAIL && count < MAX_ATTEMPTS) {
            String username = readUsername();
            String password = readPassword();
            result = verifyUser(username, password);
            count++;
        }
    } catch (IOException e) {
        log.error("login error");
    }
}''',
     'safeCodeKeywords':['MAX_ATTEMPTS','count < MAX_ATTEMPTS','count++'],
     'explanation':'인증 실패 시 시도 횟수에 제한을 두지 않아 비밀번호가 맞을 때까지 무제한 반복 시도가 가능하므로 무차별 대입(brute force)에 취약합니다. 최대 시도 횟수를 제한하고 초과 시 잠금해야 합니다.'},

    # ============================================================
    # PC-18 (하, TP) 종료되지 않는 반복문 또는 재귀함수 (CWE-835)
    # ============================================================
    {'id':'PC-18','lang':'C','cat':'시간상태','diff':'하',
     'title':'팩토리얼 재귀 계산 함수 검토',
     'code':'''#include <stdio.h>
int factorial(int i)
{
    return i * factorial(i - 1);
}
int main()
{
    int num = 5;
    int result = factorial(num);
    printf("%d! : %d\\n", num, result);
    return 0;
}''',
     'isTruePositive':True,'weaknessName':'종료되지 않는 반복문 또는 재귀함수','cwe':'CWE-835',
     'reasonKeywords':['탈출 조건 없음','무한 재귀','스택 오버플로우','종료 조건 누락'],
     'negKw':['Null Pointer 역참조','오류 상황 대응 부재','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''#include <stdio.h>
int factorial(int i)
{
    if (i <= 1) {
        return 1;
    }
    return i * factorial(i - 1);
}
int main()
{
    int num = 5;
    int result = factorial(num);
    printf("%d! : %d\\n", num, result);
    return 0;
}''',
     'safeCodeKeywords':['if (i <= 1)','return 1','factorial(i - 1)'],
     'explanation':'재귀함수에 탈출(종료) 조건이 없어 i가 음수로 계속 감소하며 무한 재귀로 스택 오버플로우가 발생합니다. 재귀에는 반드시 종료 조건을 두어야 합니다.'},

    # ============================================================
    # PC-19 (하, TP) 오류 메시지 정보 노출 (CWE-209)
    # ============================================================
    {'id':'PC-19','lang':'Java','cat':'에러처리','diff':'하',
     'title':'파일 읽기 예외 처리 로직 검토',
     'code':'''public void readFile(String filename) {
    try {
        BufferedReader rd = new BufferedReader(new FileReader(new File(filename)));
        process(rd);
    } catch (IOException e) {
        e.printStackTrace();
    }
}''',
     'isTruePositive':True,'weaknessName':'오류 메시지 정보 노출','cwe':'CWE-209',
     'reasonKeywords':['printStackTrace','스택 트레이스 노출','내부 경로 노출','상세 오류 정보'],
     'negKw':['오류 상황 대응 부재','부적절한 예외 처리','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public void readFile(String filename) {
    try {
        BufferedReader rd = new BufferedReader(new FileReader(new File(filename)));
        process(rd);
    } catch (IOException e) {
        // 최소 정보만 별도 로깅, 사용자에게는 일반화된 메시지
        logger.error("ERROR-01: 파일 열기 에러");
    }
}''',
     'safeCodeKeywords':['logger.error','ERROR-01','IOException'],
     'explanation':'예외 발생 시 printStackTrace로 스택 트레이스를 그대로 출력해 내부 경로·구조 등 시스템 정보가 노출되는 오류 메시지 정보 노출 약점이 있습니다. 상세 오류는 내부 로깅하고 사용자에게는 일반화된 메시지만 노출해야 합니다.'},

    # ============================================================
    # PC-20 (중, TP) 오류 상황 대응 부재 (CWE-391)
    # ============================================================
    {'id':'PC-20','lang':'Java','cat':'에러처리','diff':'중',
     'title':'로그인 파라미터 처리 예외 구간 검토',
     'code':'''protected Element createContent(WebSession s) {
    String username, password;
    try {
        username = s.getParser().getRawParameter(USERNAME);
        password = s.getParser().getRawParameter(PASSWORD);
        if (!"webgoat".equals(username) || !password.equals("webgoat")) {
            s.setMessage("Invalid username and password entered.");
            return makeLogin(s);
        }
    } catch (NullPointerException e) {
        // 예외 발생 시 아무 대응이 없음
    }
    return makeSuccess(s);
}''',
     'isTruePositive':True,'weaknessName':'오류 상황 대응 부재','cwe':'CWE-391',
     'reasonKeywords':['빈 catch','예외 무시','대응 없음','인증 우회'],
     'negKw':['오류 메시지 정보 노출','Null Pointer 역참조','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''protected Element createContent(WebSession s) {
    String username, password;
    try {
        username = s.getParser().getRawParameter(USERNAME);
        password = s.getParser().getRawParameter(PASSWORD);
        if (!"webgoat".equals(username) || !password.equals("webgoat")) {
            s.setMessage("Invalid username and password entered.");
            return makeLogin(s);
        }
    } catch (NullPointerException e) {
        // 예외 상황에 대해 적절히 대응(로그인 화면으로 복귀)
        s.setMessage("Invalid username and password entered.");
        return makeLogin(s);
    }
    return makeSuccess(s);
}''',
     'safeCodeKeywords':['return makeLogin','setMessage','NullPointerException'],
     'explanation':'PASSWORD가 없으면 NullPointerException이 발생하는데 catch 블록이 비어 있어 예외를 무시하고 그대로 진행하므로, 인증 검사를 건너뛰고 성공 처리되는 오류 상황 대응 부재 약점이 있습니다. 예외 발생 시 안전하게 실패(로그인 화면 복귀) 처리해야 합니다.'},
]
