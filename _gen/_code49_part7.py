# -*- coding: utf-8 -*-
PART = {
  '신뢰할 수 없는 데이터의 역직렬화': {
    'javaLang': 'Java',
    'javaVuln': '''class DeserializeExample {
  public static Object deserialize(byte[] buffer)
      throws IOException, ClassNotFoundException {
    Object ret = null;
    try (ByteArrayInputStream bais = new ByteArrayInputStream(buffer)) {
      try (ObjectInputStream ois = new ObjectInputStream(bais)) {
        ret = ois.readObject();
      }
    }
    return ret;
  }
}''',
    'javaSafe': '''public class WhitelistedObjectInputStream extends ObjectInputStream {
  public Set<String> whitelist;
  public WhitelistedObjectInputStream(InputStream inputStream, Set<String> wl)
      throws IOException {
    super(inputStream);
    whitelist = wl;
  }
  @Override
  protected Class<?> resolveClass(ObjectStreamClass cls)
      throws IOException, ClassNotFoundException {
    // ObjectStreamClass의 클래스명이 화이트리스트에 있는지 확인한다.
    if (!whitelist.contains(cls.getName())) {
      throw new InvalidClassException("Unexpected serialized class", cls.getName());
    }
    return super.resolveClass(cls);
  }
}''',
    'pyVuln': '''import pickle
from django.shortcuts import render
def load_user_object(request):
  # 사용자로부터 입력받은 알 수 없는 데이터를 역직렬화
  pickled_userinfo = pickle.dump(request.POST.get('userinfo', ''))
  # 역직렬화(unpickle)
  user_obj = pickle.loads(pickled_userinfo)
  return render(request, '/load_user_obj.html', {'obj':user_obj})''',
    'pySafe': '''import hmac
import hashlib
import pickle
from django.shortcuts import render
def load_user_object(request):
  # 데이터 변조를 확인하기 위한 해시값
  hashed_pickle = request.POST.get("hashed_pickle", "")
  # 사용자로부터 입력받은 데이터를 직렬화(pickle)
  pickled_userinfo = pickle.dumps(request.POST.get("userinfo", ""))
  # HMAC 검증을 위한 비밀키 생성
  m = hmac.new(key="secret_key".encode("utf-8"), digestmod=hashlib.sha512)
  m.update(pickled_userinfo)
  # 전달받은 해시값과 직렬화 데이터의 해시값을 비교하여 검증
  if hmac.compare_digest(str(m.digest()), hashed_pickle):
    user_obj = pickle.loads(pickled_userinfo)
    return render(request, "/load_user_obj.html", {"obj": user_obj})
  else:
    return render(request, "/error.html", {"error": "신뢰할 수 없는 데이터입니다."})''',
    'note': '',
  },
  '잘못된 세션에 의한 데이터 정보 노출': {
    'javaLang': 'Java',
    'javaVuln': '''@Controller
public class TrendForecastController {
  // Controller에서 int 필드가 멤버 변수로 선언되어 스레드간에 공유됨
  private int currentPage = 1;
  public void doSomething(HttpServletRequest request) {
    currentPage = Integer.parseInt(request.getParameter("page"));
  }
  // ......
}''',
    'javaSafe': '''@Controller
public class TrendForecastController {
  public void doSomething(HttpServletRequest request) {
    // 지역변수로 사용하여 스레드간 공유되지 못하도록 한다.
    int currentPage = Integer.parseInt(request.getParameter("page"));
  }
  // ......
}''',
    'pyVuln': '''from django.shortcuts import render
class UserDescription:
  user_name = ''

  def get_user_profile(self):
    result = self.get_user_discription(UserDescription.user_name)
    return result
  def show_user_profile(self, request):
    # 클래스변수는 다른 세션과 공유되는 값이기 때문에 멀티스레드
    # 환경에서 공유되지 않아야 할 자원을 사용하는 경우
    # 다른 스레드 세션에 의해 데이터가 노출될 수 있다
    UserDescription.user_name = request.POST.get('name', '')
    self.user_profile = self.get_user_profile()
    return render(request, 'profile.html', {'profile':self.user_profile})''',
    'pySafe': '''from django.shortcuts import render
class UserDescription:
  def get_user_profile(self):
    result = self.get_user_discription(self.user_name)
    return result
  def show_user_profile(self, name):
    # 인스턴스 변수로 사용해 스레드 간 공유되지 않도록 한다
    self.user_name = request.POST.get('name', '')
    self.user_profile = self.get_user_profile()
    return render(request, 'profile.html', {'profile':self.user_profile})''',
    'note': '',
  },
  '제거되지 않고 남은 디버그 코드': {
    'javaLang': 'Java',
    'javaVuln': '''class Base64 {
  public static void main(String[] args) {
    if (debug) {
      byte[] a = { (byte) 0xfc, (byte) 0x0f, (byte) 0xc0 };
      byte[] b = { (byte) 0x03, (byte) 0xf0, (byte) 0x3f };
      // ......
    }
  }
  public void otherMethod() { ... }
}''',
    'javaSafe': '''class Base64 {
  public void otherMethod() { ... }
}''',
    'pyVuln': '''from django.urls import reverse_lazy
from django.utils.text import format_lazy
DEBUG = True
ROOT_URLCONF = 'test.urls'
SITE_ID = 1
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}''',
    'pySafe': '''from django.urls import reverse_lazy
from django.utils.text import format_lazy
DEBUG = False
ROOT_URLCONF = 'test.urls'
SITE_ID = 1
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}''',
    'note': '',
  },
  'Public 메소드로부터 반환된 Private 배열': {
    'javaLang': 'Java',
    'javaVuln': '''// private 인 배열을 public인 메소드가 return한다.
private String[] colors;
public String[] getColors() { return colors; }''',
    'javaSafe': '''private String[] colors;
// 복제본을 반환하여 의도하지 않은 수정을 방지한다.
public String[] getColors() {
  String[] ret = null;
  if (this.colors != null) {
    ret = new String[colors.length];
    for (int i = 0; i < colors.length; i++) { ret[i] = this.colors[i]; }
  }
  return ret;
}''',
    'pyVuln': '''class UserObj:
  __private_variable = []
  def __init__(self):
    pass

  # private 배열을 리턴하는 public 메소드를 사용하는 경우 취약함
  def get_private_member(self):
    return self.__private_variable''',
    'pySafe': '''class UserObj:
  __private_variable = []
  def __init__(self):
    pass

  # private 배열을 반환하는 경우 [:]를 사용하여 외부와 내부의
  # 배열이 서로 참조되지 않도록 해야 한다
  def get_private_member(self):
    return self.__private_variable[:]''',
    'note': '',
  },
  'Private 배열에 Public 데이터 할당': {
    'javaLang': 'Java',
    'javaVuln': '''// userRoles 필드는 private이지만, public인 setUserRoles()로 외부의
// 배열이 할당되면, 사실상 public 필드가 된다.
private String[] userRoles;
public void setUserRoles(String[] userRoles) {
  this.userRoles = userRoles;
}''',
    'javaSafe': '''// 객체가 클래스의 private member를 수정하지 않도록 한다.
private String[] userRoles;
public void setUserRoles(String[] userRoles) {
  this.userRoles = new String[userRoles.length];
  for (int i = 0; i < userRoles.length; ++i)
    this.userRoles[i] = userRoles[i];
}''',
    'pyVuln': '''class UserObj:
  __private_variable = []
  def __init__(self):
    pass
  # private 배열에 외부 값을 바로 대입하는 public 메소드를 사용하는
  # 경우 취약하다
  def set_private_member(self, input_list):
    self.__private_variable = input_list''',
    'pySafe': '''class UserObj:
  def __init__(self):
    self.__privateVariable = []

  # private 배열에 외부 값을 바로 대입하는 경우 [:]를 사용하여
  # 외부와 내부의 배열이 서로 참조되지 않도록 해야 한다
  def set_private_member(self, input_list):
    self.__privateVariable = input_list[:]''',
    'note': '',
  },
  'DNS lookup에 의존한 보안 결정': {
    'javaLang': 'Java',
    'javaVuln': '''public void doGet(HttpServletRequest req, HttpServletResponse res)
    throws ServletException, IOException {
  boolean trusted = false;
  String ip = req.getRemoteAddr();
  InetAddress addr = InetAddress.getByName(ip);
  // 도메인은 공격자에 의해 실행되는 서버의 DNS가 변경될 수 있으므로 안전하지 않다.
  if (addr.getCanonicalHostName().endsWith("trustme.com")) {
    do_something_for_Trust_System();
  }
}''',
    'javaSafe': '''public void doGet(HttpServletRequest req, HttpServletResponse res)
    throws ServletException, IOException {
  String ip = req.getRemoteAddr();
  if (ip == null || "".equals(ip)) return;
  // 이용하려는 실제 서버의 IP 주소를 사용하여 DNS변조에 방어한다.
  String trustedAddr = "127.0.0.1";
  if (ip.equals(trustedAddr)) {
    do_something_for_Trust_System();
  }
}''',
    'pyVuln': '''def is_trust(host_domain_name):
  trusted = False
  trusted_host = "trust.example.com"
  # 공격자에 의해 실행되는 서버의 DNS가 변경될 수 있으므로
  # 안전하지 않다
  if trusted_host == host_name:
    trusted = True
  return trusted''',
    'pySafe': '''import socket
def is_trust(host_domain_name):
  trusted = False
  trusted_ip = "192.168.10.7"
  # 실제 서버의 IP 주소를 비교하여 DNS 변조에 대응
  dns_resolved_ip = socket.gethostbyname(host_domain_name)
  if trusted_ip == dns_resolved_ip:
    trusted = True
  return trusted''',
    'note': '',
  },
  '취약한 API 사용': {
    'javaLang': 'C',
    'javaVuln': '''#include <stdio.h>
void requestString()
{
  char str[100];
  // gets() 함수는 문자열 길이를 제한 할 수 없어 안전하지 않다.
  gets(str);
}''',
    'javaSafe': '''#include <stdio.h>
void requestString()
{
  char str[100];
  // gets_s() 함수는 문자열 길이 제한이 가능하다.
  gets_s(str, sizeof(str));
}''',
    'pyVuln': '',
    'pySafe': '',
    'note': 'Python 가이드의 "취약한 API 사용" 항목은 코드예제 없이 안전한 패키지 선택 및 SBOM 기반 사후관리 절차만 서술하므로 Python 예제는 부재. Java/C# 가이드는 C(gets→gets_s) 예제 외에 직접 소켓 사용 대신 URLConnection 사용(CWE-246), J2EE에서 System.exit() 사용 금지(CWE-382) 예제도 포함함.',
  },
}
