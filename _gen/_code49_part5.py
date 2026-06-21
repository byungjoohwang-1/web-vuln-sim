# -*- coding: utf-8 -*-
PART = {
  '사용자 하드디스크에 저장되는 쿠키를 통한 정보 노출': {
    'javaLang': 'Java',
    'javaVuln': '''Cookie loginCookie = new Cookie("rememberme", "YES");
// 쿠키의 만료시간을 1년으로 과도하게 길게 설정하고 있어 안전하지 않다.
loginCookie.setMaxAge(60*60*24*365);
response.addCookie(loginCookie);''',
    'javaSafe': '''Cookie loginCookie = new Cookie("rememberme", "YES");
// 쿠키의 만료시간은 해당 기능에 맞춰 최소로 사용한다.
loginCookie.setMaxAge(60*60*24);
response.addCookie(loginCookie);''',
    'pyVuln': '''from django.http import HttpResponse

def remind_user_state(request):
  res = HttpResponse()
  # 쿠키의 만료시간을 1년으로 과도하게 길게 설정하고 있어 안전하지 않다
  res.set_cookie('rememberme', 1, max_age=60*60*24*365)
  return res''',
    'pySafe': '''from django.http import HttpResponse

def remind_user_state(request):
  res = HttpResponse()
  # 쿠키의 만료시간을 적절하게 부여하고 secure 및 httpOnly 옵션을 활성화 한다.
  res.set_cookie('rememberme', 1, max_age=60*60, secure=True, httponly=True)
  return res''',
    'note': ''
  },
  '주석문 안에 포함된 시스템 주요정보': {
    'javaLang': 'Java',
    'javaVuln': '''// 주석문으로 DB연결 ID, 비밀번호의 중요한 정보를 노출시켜 안전하지 않다.
// DB연결 root / a1q2w3r3f2!@
con = DriverManager.getConnection(URL, USER, PASS);''',
    'javaSafe': '''// ID, 비밀번호등의 중요 정보는 주석에 포함해서는 안된다.
con = DriverManager.getConnection(URL, USER, PASS);''',
    'pyVuln': '''def user_login(id, passwd):
    # 주석문에 포함된 중요 시스템의 인증 정보
    # id = admin
    # passwd = passw0rd
    result = login(id, passwd)
    return result''',
    'pySafe': '''def user_login(id, passwd):
  # 주석문에 포함된 민감한 정보는 삭제
  result = login(id, passwd)
  return result''',
    'note': ''
  },
  '솔트 없이 일방향 해시함수 사용': {
    'javaLang': 'Java',
    'javaVuln': '''public String getPasswordHash(String password) throws Exception {
  MessageDigest md = MessageDigest.getInstance("SHA-256");
  // 해시에 솔트를 적용하지 않아 안전하지 않다.
  md.update(password.getBytes());
  byte byteData[] = md.digest();
  StringBuffer hexString = new StringBuffer();
  for (int i=0; i<byteData.length; i++) {
    String hex = Integer.toHexString(0xff & byteData[i]);
    if (hex.length() == 1) { hexString.append('0'); }
    hexString.append(hex);
  }
  return hexString.toString();
}''',
    'javaSafe': '''public String getPasswordHash(String password, byte[] salt) throws Exception {
  MessageDigest md = MessageDigest.getInstance("SHA-256");
  md.update(password.getBytes());
  // 해시 사용 시에는 원문을 찾을 수 없도록 솔트를 사용하여야 한다.
  md.update(salt);
  byte byteData[] = md.digest();
  StringBuffer hexString = new StringBuffer();
  for (int i=0; i<byteData.length; i++) {
    String hex = Integer.toHexString(0xff & byteData[i]);
    if (hex.length() == 1) { hexString.append('0'); }
    hexString.append(hex);
  }
  return hexString.toString();
}''',
    'pyVuln': '''import hashlib

def get_hash_from_pwd(pw):
  # salt 없이 생성된 해시값은 강도가 약해 취약하다
  h = hashlib.sha256(pw.encode())
  return h.digest()''',
    'pySafe': '''import hashlib
import secrets

def get_hash_from_pwd(pw):
  # 솔트 값을 사용하면 길이가 짧은 패스워드로도 고강도의 해시를 생성할 수 있다.
  # 솔트 값은 사용자별로 유일하게 생성해야 하며, 패스워드와 함께 DB에 저장해야 한다
  salt = secrets.token_hex(32)
  h = hashlib.sha256(salt.encode() + pw.encode())
  return h.digest(), salt''',
    'note': ''
  },
  '무결성 검사 없는 코드 다운로드': {
    'javaLang': 'Java',
    'javaVuln': '''URL[] classURLs = new URL[] { new URL("file:subdir/") };
URLClassLoader loader = new URLClassLoader(classURLs);
Class loadedClass = Class.forName("LoadMe", true, loader);''',
    'javaSafe': '''// 공개키 방식의 암호화로 전송파일에 대한 시그니처를 생성하고 변조유무를 판단한다.
String jarFile = "./download/util.jar";
byte[] loadFile = FileManager.getBytes(jarFile);
loadFile = encrypt(loadFile, privateKey);
FileManager.createFile(loadFile, jarFileName);
URL[] classURLs = new URL[] { new URL("http://filesave.com/download/util.jar") };
URLConnection conn = classURLs.openConnection();
InputStream is = conn.getInputStream();
FileOutputStream fos = new FileOutputStream(new File(jarFile));
while (is.read(buf) != -1) { ...... }
byte[] loadFile = FileManager.getBytes(jarFile);
loadFile = decrypt(loadFile, publicKey);
FileManager.createFile(loadFile, jarFile);
URLClassLoader loader = new URLClassLoader(classURLs);
Class loadedClass = Class.forName("MyClass", true, loader);''',
    'pyVuln': '''import requests

def execute_remote_code():
    # 신뢰할 수 없는 사이트에서 코드를 다운로드
    url = "https://www.somewhere.com/storage/code.py"
    file = requests.get(url)
    remote_code = file.content
    file_name = 'save.py'
    with open(file_name, 'wb') as f:
        f.write(file.content)
    ......''',
    'pySafe': '''import requests
import hashlib
import configparser

def execute_remote_code():
  config = configparser.RawConfigParser()
  config.read('sample_config.cfg')
  url = "https://www.somewhere.com/storage/code.py"
  remote_code_hash = config.get('HASH', 'file_hash')
  file = requests.get(url)
  remote_code = file.content
  sha = hashlib.sha256()
  sha.update(remote_code)
  # 다운로드 받은 파일의 해시값 검증
  if sha.hexdigest() != remote_code_hash:
    raise Exception('파일이 손상되었습니다.')
  file_name = 'save.py'
  with open(file_name, 'wb') as f:
    f.write(file.content)''',
    'note': ''
  },
  '반복된 인증시도 제한 기능 부재': {
    'javaLang': 'Java',
    'javaVuln': '''public void login() {
  String username = null;
  String password = null;
  Socket socket = null;
  int result = FAIL;
  try {
    socket = new Socket(SERVER_IP, SERVER_PORT);
    // 인증 실패에 대해 제한을 두지 않아 안전하지 않다.
    while (result == FAIL) {
      ...
      result = verifyUser(username, password);
    }
  }
}''',
    'javaSafe': '''private static final int MAX_ATTEMPTS = 5;
public void login() {
  String username = null;
  String password = null;
  Socket socket = null;
  int result = FAIL;
  int count = 0;
  try {
    socket = new Socket(SERVER_IP, SERVER_PORT);
    // 인증 실패 및 시도 횟수에 제한을 두어 안전하다.
    while (result == FAIL && count < MAX_ATTEMPTS) {
      ...
      result = verifyUser(username, password);
      count++;
    }
  }
}''',
    'pyVuln': '''import hashlib
from django.shortcuts import render

def login(request):
  user_id = request.POST.get('user_id', '')
  user_pw = request.POST.get('user_pw', '')
  sha = hashlib.sha256()
  sha.update(user_pw.encode('utf-8'))
  hashed_passwd = get_user_pw(user_id)
  # 인증 시도에 따른 제한이 없어 반복적인 인증 시도가 가능
  if sha.hexdigest() == hashed_passwd:
    return render(request, '/index.html', {'state':'login_success'})
  else:
    return render(request, '/login.html', {'state':'login_failed'})''',
    'pySafe': '''import hashlib
from django.shortcuts import render
from .models import LoginFail
LOGIN_TRY_LIMIT = 5

def login(request):
  user_id = request.POST.get('user_id', '')
  user_pw = request.POST.get('user_pw', '')
  sha = hashlib.sha256()
  sha.update(user_pw.encode('utf-8'))
  hashed_passwd = get_user_pw(user_id)
  if sha.hexdigest() == hashed_passwd:
    LoginFail.objects.filter(user_id=user_id).delete()
    return render(request, '/index.html', {'state':'login_success'})
  if LoginFail.objects.filter(user_id=user_id).exists():
    COUNT = LoginFail.objects.get(user_id=user_id).count
  else:
    COUNT = 0
  if COUNT >= LOGIN_TRY_LIMIT:
    return render(request, "/account_lock.html", {"state": "account_lock"})
  else:
    LoginFail.objects.update_or_create(
      user_id=user_id, defaults={"count": COUNT + 1})
    return render(request, "/login.html", {"state": "login_failed"})''',
    'note': ''
  },
  '경쟁조건: 검사시점과 사용시점(TOCTOU)': {
    'javaLang': 'Java',
    'javaVuln': '''class FileMgmtThread extends Thread {
  private String manageType = "";
  public FileMgmtThread (String type) { manageType = type; }
  // 멀티쓰레드 환경에서 공유자원에 동시에 접근할 가능성이 있어 안전하지 않다.
  public void run() {
    try {
      if (manageType.equals("READ")) {
        File f = new File("Test_367.txt");
        if (f.exists()) {
          BufferedReader br = new BufferedReader(new FileReader(f));
          br.close();
        }
      } else if (manageType.equals("DELETE")) {
        File f = new File("Test_367.txt");
        if (f.exists()) { f.delete(); }
      }
    } catch (IOException e) { ... }
  }
}''',
    'javaSafe': '''class FileMgmtThread extends Thread {
  private static final String SYNC = "SYNC";
  private String manageType = "";
  public FileMgmtThread (String type) { manageType = type; }
  public void run() {
    // 멀티쓰레드 환경에서 synchronized를 사용하여 동시에 접근할 수 없도록 한다.
    synchronized(SYNC) {
      try {
        if (manageType.equals("READ")) {
          File f = new File("Test_367.txt");
          if (f.exists()) {
            BufferedReader br = new BufferedReader(new FileReader(f));
            br.close();
          }
        } else if (manageType.equals("DELETE")) {
          File f = new File("Test_367.txt");
          if (f.exists()) { f.delete(); }
        }
      } catch (IOException e) { ... }
    }
  }
}''',
    'pyVuln': '''import os
import io
import datetime
import threading

def write_shared_file(filename, content):
  # 멀티스레드 환경에서는 파일이 사라질 수 있어
  # 공유 자원에 대해서는 검사와 사용을 동시에 해야 한다.
  if os.path.isfile(filename) is True:
    f = open(filename, 'w')
    f.seek(0, io.SEEK_END)
    f.write(content)
    f.close()''',
    'pySafe': '''import os
import io
import datetime
import threading
lock = threading.Lock()

def write_shared_file(filename, content):
  # lock을 이용하여 여러 사용자가 동시에 파일에 접근하지 못하도록 제한
  with lock:
    if os.path.isfile(filename) is True:
      f = open(filename, 'w')
      f.seek(0, io.SEEK_END)
      f.write(content)
      f.close()''',
    'note': ''
  },
  '종료되지 않는 반복문 또는 재귀함수': {
    'javaLang': 'C',
    'javaVuln': '''#include <stdio.h>
int factorial(int i)
{
  // 재귀함수 탈출 조건을 설정하지 않아 무한루프가 된다.
  return i * factorial(i - 1);
}
int main()
{
  int num = 5;
  int result = factorial(num);
  printf("%d! : %d\\n", num, result);
  return 0;
}''',
    'javaSafe': '''#include <stdio.h>
int factorial(int i)
{
  // 재귀함수 사용 시에는 아래와 같이 탈출 조건을 사용해야 한다.
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
    'pyVuln': '''def factorial(num):
  # 재귀함수 탈출조건을 설정하지 않아 동작 중 에러 발생
  return num * factorial(num - 1)

if __name__ == '__main__':
  itr = 5
  result = factorial(itr)
  print(str(itr) + ' 팩토리얼 값은 : ' + str(result))''',
    'pySafe': '''def factorial(num):
  # 재귀함수 사용 시에는 탈출 조건을 명시해야 한다.
  if (num == 0):
    return 1
  else:
    return num * factorial(num - 1)

if __name__ == '__main__':
  itr = 5
  result = factorial(itr)
  print(str(itr) + ' 팩토리얼 값은 : ' + str(result))''',
    'note': ''
  },
}
