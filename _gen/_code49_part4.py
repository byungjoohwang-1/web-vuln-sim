# -*- coding: utf-8 -*-
PART = {
  '암호화되지 않은 중요정보': {
    'javaLang': 'Java',
    'javaVuln': '''String id = request.getParameter("id");
// 외부값에 의해 비밀번호 정보를 얻고 있다.
String pwd = request.getParameter("pwd");
......
String sql = " insert into customer(id, pwd, name, ssn, zipcode, addr)"
    + " values (?, ?, ?, ?, ?, ?)";
PreparedStatement stmt = con.prepareStatement(sql);
stmt.setString(1, id);
stmt.setString(2, pwd);
// 입력받은 비밀번호가 평문으로 DB에 저장되어 안전하지 않다.
stmt.executeUpdate();''',
    'javaSafe': '''String id = request.getParameter("id");
String pwd = request.getParameter("pwd");
// 비밀번호를 솔트값을 포함하여 SHA-256 해시로 변경하여 안전하게 저장한다.
MessageDigest md = MessageDigest.getInstance("SHA-256");
md.reset();
md.update(salt);
byte[] hashInBytes = md.digest(pwd.getBytes());
StringBuilder sb = new StringBuilder();
for (byte b : hashInBytes) {
    sb.append(String.format("%02x", b));
}
pwd = sb.toString();
......
PreparedStatement stmt = con.prepareStatement(sql);
stmt.setString(1, id);
stmt.setString(2, pwd);
stmt.executeUpdate();''',
    'pyVuln': '''def update_pass(dbconn, password, user_id):
  curs = dbconn.cursor()
  # 암호화되지 않은 패스워드를 DB에 저장
  curs.execute(
    'UPDATE USERS SET PASSWORD=%s WHERE USER_ID=%s',
    password,
    user_id
  )
  dbconn.commit()''',
    'pySafe': '''from Crypto.Hash import SHA256
def update_pass(dbconn, password, user_id, salt):
  # 단방향 암호화를 이용하여 패스워드를 암호화
  hash_obj = SHA256.new()
  hash_obj.update(bytes(password + salt, 'utf-8'))
  hash_pwd = hash_obj.hexdigest()
  curs = dbconn.cursor()
  curs.execute(
    'UPDATE USERS SET PASSWORD=%s WHERE USER_ID=%s',
    (hash_pwd, user_id)
  )
  dbconn.commit()''',
    'note': ''
  },
  '하드코드된 중요정보': {
    'javaLang': 'Java',
    'javaVuln': '''public class MemberDAO {
  private static final String DRIVER = "oracle.jdbc.driver.OracleDriver";
  private static final String URL = "jdbc:oracle:thin:@192.168.0.3:1521:ORCL";
  private static final String USER = "SCOTT"; // DB ID
  // DB 비밀번호가 소스코드에 평문으로 저장되어 있다.
  private static final String PASS = "SCOTT"; // DB PW
  ......
  public Connection getConn() {
    Connection con = null;
    try {
      Class.forName(DRIVER);
      con = DriverManager.getConnection(URL, USER, PASS);
      ......''',
    'javaSafe': '''public class MemberDAO {
  private static final String DRIVER = "oracle.jdbc.driver.OracleDriver";
  private static final String URL = "jdbc:oracle:thin:@192.168.0.3:1521:ORCL";
  private static final String USER = "SCOTT"; // DB ID
  ......
  public Connection getConn() {
    Connection con = null;
    try {
      Class.forName(DRIVER);
      // 암호화된 비밀번호를 프로퍼티에서 읽어들여 복호화해서 사용해야 한다.
      String PASS = props.getProperty("EncryptedPswd");
      byte[] decryptedPswd = cipher.doFinal(PASS.getBytes());
      PASS = new String(decryptedPswd);
      con = DriverManager.getConnection(URL, USER, PASS);
      ......''',
    'pyVuln': '''import pymysql
def query_execute(query):
  # user, passwd가 소스코드에 평문으로 하드코딩되어 있음
  dbconn = pymysql.connect(
    host='127.0.0.1',
    port='1234',
    user='root',
    passwd='1234',
    db='mydb',
    charset='utf8',
  )
  curs = dbconn.cursor()
  curs.execute(query)
  dbconn.commit()
  dbconn.close()''',
    'pySafe': '''import pymysql
import json
def query_execute(query, config_path):
  with open(config_path, 'r') as config:
    # 설정 파일에서 user, passwd를 가져와 사용
    dbconf = json.load(fp=config)
    # 암호화되어 있는 블록 암호화 키를 복호화 해서 가져오는 사용자 정의 함수
    blockKey = get_decrypt_key(dbconf['blockKey'])
    # 설정 파일에 암호화되어 있는 값을 가져와 복호화한 후에 사용
    dbUser = decrypt(blockKey, dbconf['user'])
    dbPasswd = decrypt(blockKey, dbconf['passwd'])
  dbconn = pymysql.connect(
    host=dbconf['host'],
    port=dbconf['port'],
    user=dbUser,
    passwd=dbPasswd,
    db=dbconf['db_name'],
    charset='utf8',
  )''',
    'note': ''
  },
  '충분하지 않은 키 길이 사용': {
    'javaLang': 'Java',
    'javaVuln': '''public static final String ALGORITHM = "RSA";
public static final String PRIVATE_KEY_FILE = "C:/keys/private.key";
public static final String PUBLIC_KEY_FILE = "C:/keys/public.key";
public static void generateKey() {
  try {
    final KeyPairGenerator keyGen = KeyPairGenerator.getInstance(ALGORITHM);
    // RSA 키 길이를 1024 비트로 짧게 설정하는 경우 안전하지 않다.
    keyGen.initialize(1024);
    final KeyPair key = keyGen.generateKeyPair();
    ......''',
    'javaSafe': '''public static final String ALGORITHM = "RSA";
public static final String PRIVATE_KEY_FILE = "C:/keys/private.key";
public static final String PUBLIC_KEY_FILE = "C:/keys/public.key";
public static void generateKey() {
  try {
    final KeyPairGenerator keyGen = KeyPairGenerator.getInstance(ALGORITHM);
    // 공개키 암호화에 사용하는 키의 길이는 적어도 2048비트 이상으로 설정한다.
    keyGen.initialize(2048);
    final KeyPair key = keyGen.generateKeyPair();
    ......''',
    'pyVuln': '''from Crypto.PublicKey import RSA, DSA, ECC
from tinyec import registry
import secrets
def make_rsa_key_pair():
  # RSA키 길이를 2048 비트 이하로 설정하는 경우 안전하지 않음
  private_key = RSA.generate(1024)
  public_key = private_key.publickey()
def make_ecc():
  # ECC의 키 길이를 224비트 이하로 설정하는 경우 안전하지 않음
  ecc_curve = registry.get_curve('secp192r1')
  private_key = secrets.randbelow(ecc_curve.field.n)
  public_key = private_key * ecc_curve.g''',
    'pySafe': '''from Crypto.PublicKey import RSA, DSA, ECC
from tinyec import registry
import secrets
def make_rsa_key_pair():
  # RSA 키 길이를 2048 비트 이상으로 길게 설정
  private_key = RSA.generate(2048)
  public_key = private_key.publickey()
def make_ecc():
  # ECC 키 길이를 224 비트 이상으로 설정
  ecc_curve = registry.get_curve('secp224r1')
  private_key = secrets.randbelow(ecc_curve.field.n)
  public_key = private_key * ecc_curve.g''',
    'note': ''
  },
  '적절하지 않은 난수값 사용': {
    'javaLang': 'Java',
    'javaVuln': '''import java.util.Random;
...
public static int getRandomValue(int maxValue) {
  // 고정된 시드값을 사용하여 동일한 난수값이 생성되어 안전하지 않다.
  Random random = new Random(100);
  return random.nextInt(maxValue);
}
public static String getAuthKey() {
  // 매번 변경되나 보안결정을 위한 난수로는 안전하지 않다.
  Random random = new Random();
  String authKey = Integer.toString(random.nextInt());
}''',
    'javaSafe': '''import java.security.SecureRandom;
...
public static String getAuthKey() {
  // 보안결정을 위한 난수로는 암호학적으로 보호된 SecureRandom을 사용한다.
  try {
    SecureRandom secureRandom = SecureRandom.getInstance("SHA1PRNG");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    secureRandom.setSeed(secureRandom.generateSeed(128));
    String authKey = new String(digest.digest((secureRandom.nextLong() + "").getBytes()));
    ...
  } catch (NoSuchAlgorithmException e) {
    ......
  }
}''',
    'pyVuln': '''import random
def get_otp_number():
  random_str = ''
  # 시스템 현재 시간 값을 시드로 사용하고 있으며, 주요 보안 기능을 위한
  # 난수로 안전하지 않다
  for i in range(6):
    random_str += str(random.randrange(10))
  return random_str''',
    'pySafe': '''import secrets
def get_otp_number():
  random_str = ''
  # 보안기능에 적합한 난수 생성용 secrets 라이브러리 사용
  for i in range(6):
    random_str += str(secrets.randbelow(10))
  return random_str''',
    'note': ''
  },
  '취약한 비밀번호 허용': {
    'javaLang': 'Java',
    'javaVuln': '''String id = request.getParameter("id");
String pass = request.getParameter("pass");
UserVo userVO = new UserVo(id, pass);
......
// 비밀번호의 자릿수, 특수문자 포함 여부 등 복잡도를 체크하지 않고 등록
String result = registerDAO.register(userVO);''',
    'javaSafe': '''String id = request.getParameter("id");
String pass = request.getParameter("pass");
// 비밀번호에 자릿수, 특수문자 포함여부 등의 복잡도를 체크하고 등록하게 한다.
Pattern pattern = Pattern.compile("((?=.*[a-zA-Z])(?=.*[0-9@#$%]).{9,})");
Matcher matcher = pattern.matcher(pass);
if (!matcher.matches()) {
  return "비밀번호 조합규칙 오류";
}
UserVo userVO = new UserVo(id, pass);
......
String result = registerDAO.register(userVO);''',
    'pyVuln': '''@app.route('/register', methods=['POST'])
def register():
  userid = request.form.get('userid')
  password = request.form.get('password')
  confirm_password = request.form.get('confirm_password')
  if password != confirm_password:
    return make_response("패스워드가 일치하지 않습니다", 400)
  else:
    usertable = User()
    usertable.userid = userid
    usertable.password = password
    # 패스워드 생성 규칙을 확인하지 않고 회원 가입
    db.session.add(usertable)
    db.session.commit()
    return make_response("회원가입 성공", 200)''',
    'pySafe': '''import re
@app.route('/register', methods=['POST'])
def register():
  userid = request.form.get('userid')
  password = request.form.get('password')
  confirm_password = request.form.get('confirm_password')
  if password != confirm_password:
    return make_response("패스워드가 일치하지 않습니다.", 400)
  if not check_password(password):
    return make_response("패스워드 조합규칙에 맞지 않습니다.", 400)
  else:
    usertable = User()
    usertable.userid = userid
    usertable.password = password
    db.session.add(usertable)
    db.session.commit()
    return make_response("회원가입 성공", 200)
def check_password(password):
  # 3종 이상 문자로 구성된 8자리 이상 패스워드 검사 정규식 적용
  PT1 = re.compile('^(?=.*[A-Z])(?=.*[a-z])[A-Za-z\\d!@#$%^&*]{8,}$')
  # 문자 구성 상관없이 10자리 이상 패스워드 검사 정규식
  PT7 = re.compile('^[A-Za-z\\d!@#$%^&*]{10,}$')
  for pattern in [PT1, PT7]:
    if pattern.match(password):
      return True
  return False''',
    'note': ''
  },
  '부적절한 전자서명 확인': {
    'javaLang': 'Java',
    'javaVuln': '''// 신뢰할 수 없는 곳에서 다운로드 한 JAR 파일의 서명을 확인하지 않고 사용한다.
File f = new File(downloadedFilePath);
JarFile jf = new JarFile(f);''',
    'javaSafe': '''File f = new File(downloadedFilePath);
// JarFile 생성자에 boolean형 파라미터를 사용하여 전자서명을 확인한다.
JarFile jf = new JarFile(f, true);
Enumeration<JarEntry> ens = jf.entries();
while (ens.hasMoreElements()) {
  JarEntry en = ens.nextElement();
  if (!en.isDirectory()) {
    if (en.toString().equals(path)) {
      byte[] data = readAll(jar.getInputStream(en), en.getSize());
      // 전자서명 주체를 신뢰할 수 있는지 확인한다.
      CodeSigner[] signers = en.getCodeSigners();
      ...
    }
  }
}
jf.close();''',
    'pyVuln': '''def verify_data(request):
    # 클라이언트로부터 전달받은 데이터(전자서명을 수신 처리 하지 않음)
    encrypted_code = request.POST.get("encrypted_msg", "")  # 암호화된 파이썬 코드
    with open(f"{PATH}/keys/secret_key.out", "rb") as f:
        secret_key = f.read()
    # 대칭키로 클라이언트가 전달한 파이썬 코드 복호화
    origin_python_code = decrypt_with_symmetric_key(secret_key, encrypted_code)
    # 전자서명 검증 없이 클라이언트로부터 전달 받은 파이썬 코드 실행
    eval(origin_python_code)''',
    'pySafe': '''from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5 as SIGNATURE_PKCS1_v1_5
import base64
def verify_digit_signature(origin_data, origin_signature, client_pub_key):
    # 공개키로 복호화한 전자서명과 원본 데이터 해시값의 일치 여부를 검사
    hashed_data = SHA256.new(origin_data)
    signer = SIGNATURE_PKCS1_v1_5.new(RSA.importKey(client_pub_key))
    return signer.verify(hashed_data, base64.b64decode(origin_signature))
def verify_data(request):
    # 클라이언트의 공개키를 통해 파이썬 코드(원문)와 전자서명을 검증
    verify_result = verify_digit_signature(origin_python_code, origin_signature, client_pub_key)
    # 전자서명 검증을 통과했다면 파이썬 코드 실행
    if verify_result:
        eval(origin_python_code)''',
    'note': ''
  },
  '부적절한 인증서 유효성 검증': {
    'javaLang': 'C/Java',
    'javaVuln': '''// 인증서 검증결과가 X509_V_OK로 반환되더라도 호스트가
// Common Name과 일치하는지 확인하지 않으므로 안전하지 않다.
cert = SSL_get_peer_certificate(ssl);
if (cert && (SSL_get_verify_result(ssl) == X509_V_OK)) {
  /* CN을 확인하지 않았지만 신뢰하고 진행한다. 공격자가 Common Name을
     www.attack.com으로 설정하여 중간자 공격에 사용할 수 있다. */
}''',
    'javaSafe': '''private boolean verifySignature(X509Certificate toVerify, X509Certificate signingCert) {
  /* 검증하려는 호스트 인증서(toVerify)와 CA인증서(signingCert)의
     DN(Distinguished Name)이 일치하는지 여부를 확인한다. */
  if (!toVerify.getIssuerDN().equals(signingCert.getSubjectDN())) return false;
  try {
    // 호스트 인증서가 CA인증서로 서명 되었는지 확인한다.
    toVerify.verify(signingCert.getPublicKey());
    // 호스트 인증서의 유효기간이 만료되었는지 확인한다.
    toVerify.checkValidity();
    return true;
  } catch (GeneralSecurityException verifyFailed) {
    return false;
  }
}''',
    'pyVuln': '''import socket
import ssl
HOST, PORT = "127.0.0.1", 7917
def connect_with_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        context = ssl.SSLContext()
        # SSLContext 생성자를 직접 호출할 때, CERT_NONE이 기본값
        # 상대방을 인증하지 않기 때문에 서버의 신뢰성을 보장할 수 없음
        context.verify_mode = ssl.CERT_NONE
        with context.wrap_socket(sock) as ssock:
            ssock.connect((HOST, PORT))
            ssock.send("Hello I'm a vulnerable client".encode("utf-8"))''',
    'pySafe': '''import os
import socket
import ssl
HOST, PORT = "127.0.0.1", 7917
SERVER_CA_PEM = f"{os.getcwd()}/rsa_server/CA.pem"  # 서버로부터 전달받은 CA 인증서
def connect_with_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        # PROTOCOL_TLS_CLIENT로 인증서 유효성 검사와 호스트 이름 확인을 위한 context 구성
        # verify_mode가 CERT_REQUIRED, check_hostname이 True로 설정됨
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # 서버로부터 전달받은 CA 인증서를 context에 로드 (CERT_REQUIRED로 인해 필수)
        context.load_verify_locations(SERVER_CA_PEM)''',
    'note': ''
  },
}
