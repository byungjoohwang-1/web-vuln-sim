# -*- coding: utf-8 -*-
# 2교시 실무 문항 확장 (PE-01~PE-08). 모든 정탐 모범답안은 LASHR 구조검증을 통과하고,
# 부정키워드(negKw)는 모범 서술/해설과 충돌하지 않도록 작성됨(harness 강제 검증 대상).

PART = [

    # ============================================================
    # PE-01 (중, TP) 운영체제 명령어 삽입 (CWE-78) - Python
    # ============================================================
    {'id':'PE-01','lang':'Python','cat':'입력검증','diff':'중',
     'title':'호스트 점검용 ping 실행 로직 검토',
     'code':'''import os

def ping(host):
    # 외부 입력 host를 검증 없이 셸 명령 문자열에 결합한다.
    os.system("ping -c 1 " + host)''',
     'isTruePositive':True,'weaknessName':'운영체제 명령어 삽입','cwe':'CWE-78',
     'reasonKeywords':['os.system','문자열 결합','셸 메타문자','외부 입력','명령 주입'],
     'negKw':['경로 조작','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import subprocess

def ping(host):
    # 인자를 리스트로 전달해 셸을 거치지 않는다(shell=False 기본).
    return subprocess.run(["ping", "-c", "1", host], capture_output=True)''',
     'safeCodeKeywords':['subprocess.run','capture_output'],
     'explanation':'os.system에 외부 입력 host를 문자열로 결합하므로 ";rm -rf" 같은 셸 메타문자를 넣어 임의 명령을 실행시킬 수 있습니다. 인자를 리스트로 전달하고 셸을 거치지 않도록 subprocess.run을 사용해야 합니다.'},

    # ============================================================
    # PE-02 (하, TP) 적절하지 않은 난수값 사용 (CWE-330) - Python
    # ============================================================
    {'id':'PE-02','lang':'Python','cat':'보안기능','diff':'하',
     'title':'비밀번호 재설정 토큰 생성 검토',
     'code':'''import random

def reset_token():
    # 보안 토큰을 예측 가능한 일반 PRNG로 생성한다.
    return str(random.random())''',
     'isTruePositive':True,'weaknessName':'적절하지 않은 난수값 사용','cwe':'CWE-330',
     'reasonKeywords':['random 모듈','예측 가능','시드 추측','일반 PRNG','보안 토큰'],
     'negKw':['하드코딩','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import secrets

def reset_token():
    # 암호학적으로 안전한 난수원(secrets)을 사용한다.
    return secrets.token_hex(16)''',
     'safeCodeKeywords':['secrets','token_hex'],
     'explanation':'random 모듈은 예측 가능한 일반 PRNG라 시드를 추측하면 토큰을 재현할 수 있습니다. 비밀번호 재설정 토큰처럼 보안에 민감한 값은 CSPRNG인 secrets로 생성해야 합니다.'},

    # ============================================================
    # PE-03 (중, TP) 취약한 암호화 알고리즘 사용 (CWE-327) - Java
    # ============================================================
    {'id':'PE-03','lang':'Java','cat':'보안기능','diff':'중',
     'title':'대칭키 암호화 방식 검토',
     'code':'''public byte[] enc(byte[] data, SecretKey key) throws Exception {
    // 취약한 블록 암호/모드 사용
    Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
    cipher.init(Cipher.ENCRYPT_MODE, key);
    return cipher.doFinal(data);
}''',
     'isTruePositive':True,'weaknessName':'취약한 암호화 알고리즘 사용','cwe':'CWE-327',
     'reasonKeywords':['DES','ECB 모드','짧은 키 길이','패턴 노출','블록 암호'],
     'negKw':['솔트','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public byte[] enc(byte[] data, SecretKey key, byte[] iv) throws Exception {
    // AES-GCM 인증 암호화 사용(무작위 IV 전제)
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
    return cipher.doFinal(data);
}''',
     'safeCodeKeywords':['GCMParameterSpec','doFinal'],
     'explanation':'DES는 키 길이가 짧아 전수 공격에 약하고 ECB 모드는 동일 평문이 동일 암호문으로 드러나 패턴이 노출됩니다. AES-GCM 같은 강한 알고리즘과 인증 암호 모드를 사용해야 합니다.'},

    # ============================================================
    # PE-04 (중, TP) 솔트 없이 일방향 해시함수 사용 (CWE-759) - Python
    # ============================================================
    {'id':'PE-04','lang':'Python','cat':'보안기능','diff':'중',
     'title':'회원 비밀번호 저장 해시 검토',
     'code':'''import hashlib

def hash_pw(pw):
    # 솔트 없이 MD5로 비밀번호를 해시한다.
    return hashlib.md5(pw.encode()).hexdigest()''',
     'isTruePositive':True,'weaknessName':'솔트 없이 일방향 해시함수 사용','cwe':'CWE-759',
     'reasonKeywords':['MD5','솔트 미적용','레인보우 테이블','단순 해시','사전 공격'],
     'negKw':['평문 저장','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import bcrypt

def hash_pw(pw):
    # bcrypt(솔트 자동 생성)로 비밀번호를 적응형 해시한다.
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())''',
     'safeCodeKeywords':['bcrypt','gensalt','hashpw'],
     'explanation':'MD5 단순 해시는 빠르고 솔트가 없어 레인보우 테이블·사전 공격으로 원문을 복원당하기 쉽습니다. 사용자별 솔트가 포함되는 bcrypt 같은 적응형 해시를 사용해야 합니다.'},

    # ============================================================
    # PE-05 (중, TP) 경로 조작 및 자원 삽입 (CWE-22) - Java
    # ============================================================
    {'id':'PE-05','lang':'Java','cat':'입력검증','diff':'중',
     'title':'다운로드 파일 경로 처리 검토',
     'code':'''public File open(String base, String name) throws IOException {
    // 외부 입력 name을 검증 없이 경로에 사용한다(../ 허용).
    return new File(base + "/" + name);
}''',
     'isTruePositive':True,'weaknessName':'경로 조작 및 자원 삽입','cwe':'CWE-22',
     'reasonKeywords':['디렉터리 트래버설','상위 경로 참조','정규화 미수행','임의 파일 접근','기준 경로 이탈'],
     'negKw':['난수','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''public File open(String base, String name) throws IOException {
    File f = new File(base, name);
    String canonical = f.getCanonicalPath();
    // 정규화한 경로가 기준 디렉터리 하위인지 확인한다.
    if (!canonical.startsWith(new File(base).getCanonicalPath())) {
        throw new SecurityException("잘못된 경로");
    }
    return f;
}''',
     'safeCodeKeywords':['getCanonicalPath','startsWith'],
     'explanation':'입력 name에 "../"가 포함되면 기준 디렉터리를 벗어나 임의 파일에 접근할 수 있습니다. getCanonicalPath로 정규화한 뒤 기준 경로 하위인지 startsWith로 확인해야 합니다.'},

    # ============================================================
    # PE-06 (하, TP) 하드코드된 중요정보 (CWE-798) - Python
    # ============================================================
    {'id':'PE-06','lang':'Python','cat':'보안기능','diff':'하',
     'title':'DB 접속 비밀번호 취득 로직 검토',
     'code':'''def get_db_password():
    # 비밀번호를 소스코드에 직접 적어 둔다.
    return "P@ssw0rd_2024!"''',
     'isTruePositive':True,'weaknessName':'하드코드된 중요정보','cwe':'CWE-798',
     'reasonKeywords':['하드코딩','소스 노출','버전관리 유출','자격증명 평문','비밀정보'],
     'negKw':['경로 조작','SQL 삽입','안전한 코드','취약하지 않','오탐'],
     'safeCode':'''import os

def get_db_password():
    # 비밀정보는 환경변수에서 읽는다(코드에 포함하지 않음).
    return os.environ.get("DB_PASSWORD")''',
     'safeCodeKeywords':['os.environ','DB_PASSWORD'],
     'explanation':'비밀번호를 소스코드에 직접 적으면 저장소·배포물에 그대로 노출되어 유출 시 즉시 악용됩니다. 환경변수나 비밀 관리 서비스에서 주입받아야 합니다.'},

    # ============================================================
    # PE-07 (중, FP) 정수형 오버플로우 — 안전한 코드 (오탐 대상) - Java
    # ============================================================
    {'id':'PE-07','lang':'Java','cat':'코드오류','diff':'중',
     'title':'주문 총액 계산 로직 안전성 검토',
     'code':'''public int totalPrice(int unit, int qty) {
    if (qty < 0 || qty > 1000) throw new IllegalArgumentException();
    // 초과 시 예외를 던지는 multiplyExact로 안전하게 계산한다.
    return Math.multiplyExact(unit, qty);
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['Math.multiplyExact','경계 검사','수량 상한','초과 시 예외','안전한 산술'],
     'negKw':['오버플로우 발생','정탐','계산 조작 가능','우회 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'수량 범위를 검사하고 multiplyExact가 초과 시 예외를 던지므로 정수형 오버플로우 위험이 없는 안전한 코드(오탐)입니다.'},

    # ============================================================
    # PE-08 (하, FP) XSS — 출력 인코딩 적용 (오탐 대상) - Java
    # ============================================================
    {'id':'PE-08','lang':'Java','cat':'입력검증','diff':'하',
     'title':'사용자 이름 출력 처리 안전성 검토',
     'code':'''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String name = req.getParameter("name");
    // 출력 전 HTML 특수문자를 이스케이프한다.
    String safe = org.apache.commons.text.StringEscapeUtils.escapeHtml4(name);
    resp.getWriter().println("<p>" + safe + "</p>");
}''',
     'isTruePositive':False,'weaknessName':'','cwe':'',
     'reasonKeywords':['escapeHtml4','출력 인코딩','HTML 이스케이프','특수문자 변환','스크립트 무력화'],
     'negKw':['스크립트 실행 가능','정탐','삽입 가능','우회 가능'],
     'safeCode':'','safeCodeKeywords':[],
     'explanation':'출력 값을 escapeHtml4로 이스케이프하므로 삽입된 태그가 일반 문자로 변환되어 브라우저에서 스크립트로 동작하지 않는 안전한 코드(오탐)입니다.'},

]
