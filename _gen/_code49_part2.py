# -*- coding: utf-8 -*-
PART = {
  'XML 외부 개체(XXE) (CWE-611)': {
    'javaLang': 'Java',
    'javaVuln': '''SAXParserFactory factory = SAXParserFactory.newInstance();
SAXParser saxParser = factory.newSAXParser();
// 외부개체 참조 제한 설정 없이 secure.xml 파일을 읽어서 파싱하여 안전하지 않다.
saxParser.parse(new FileInputStream("secure.xml"), new DefaultHandler());''',
    'javaSafe': '''DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
// XML 파서가 doctype을 정의하지 못하도록 설정한다.
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
// 외부 일반 엔티티를 포함하지 않도록 설정한다.
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
// 외부 파라미터도 포함하지 않도록 설정한다.
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
// 외부 DTD 비활성화한다.
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
DocumentBuilder db = dbf.newDocumentBuilder();
Document document = db.parse(receivedXml);''',
    'pyVuln': '''from xml.sax import make_parser
from xml.sax.handler import feature_external_ges
from xml.dom.pulldom import parseString, START_ELEMENT

def get_xml(request):
    if request.method == "POST":
        parser = make_parser()
        # 외부 일반 엔티티를 포함하는 설정을 True로 적용할 경우 취약하다
        parser.setFeature(feature_external_ges, True)
        doc = parseString(request.body.decode('utf-8'), parser=parser)''',
    'pySafe': '''from xml.sax import make_parser
from xml.sax.handler import feature_external_ges
from xml.dom.pulldom import parseString, START_ELEMENT

def get_xml(request):
    if request.method == "POST":
        parser = make_parser()
        # 외부 엔티티 처리 옵션을 False로 설정한다.
        parser.setFeature(feature_external_ges, False)
        doc = parseString(request.body.decode('utf-8'), parser=parser)''',
    'note': '',
  },

  'XML 삽입 (CWE-91)': {
    'javaLang': 'Java',
    'javaVuln': '''// 외부 입력 값을 검증하지 않고 XQuery 표현식에 사용한다.
String name = props.getProperty("name");
// 외부 입력 값에 의해 쿼리 구조가 변경 되어 안전하지 않다.
String es = "doc('users.xml')/userlist/user[uname='" + name + "']";
XQPreparedExpression expr = conn.prepareExpression(es);
XQResultSequence result = expr.executeQuery();''',
    'javaSafe': '''// bindString 함수로 쿼리 구조가 변경되는 것을 방지한다.
String name = props.getProperty("name");
String es = "doc('users.xml')/userlist/user[uname='$xname']";
XQPreparedExpression expr = conn.prepareExpression(es);
expr.bindString(new QName("xname"), name, null);
XQResultSequence result = expr.executeQuery();''',
    'pyVuln': '''from lxml import etree

def parse_xml(request):
    user_name = request.POST.get('user_name', '')
    parser = etree.XMLParser(resolve_entities=False)
    tree = etree.parse('user.xml', parser)
    root = tree.getroot()
    # 검증되지 않은 외부 입력값 user_name을 그대로 사용한 안전하지 않은 질의문
    query = "/collection/users/user[@name='" + user_name + "']/home/text()"
    elmts = root.xpath(query)''',
    'pySafe': '''from lxml import etree

def parse_xml(request):
    user_name = request.POST.get('user_name', '')
    parser = etree.XMLParser(resolve_entities=False)
    tree = etree.parse('user.xml', parser)
    root = tree.getroot()
    # 외부 입력값을 paramname으로 인자화 해서 사용
    query = '/collection/users/user[@name = $paramname]/home/text()'
    elmts = root.xpath(query, paramname=user_name)''',
    'note': '',
  },

  'LDAP 삽입 (CWE-90)': {
    'javaLang': 'Java',
    'javaVuln': '''SearchControls sc = new SearchControls();
sc.setReturningAttributes(new String[]{ "cn", "mail" });
sc.setSearchScope(SearchControls.SUBTREE_SCOPE);
String base = "dc=example,dc=com";
// userSN과 userPassword 값에 LDAP 필터를 조작할 수 있는 공격 문자열에 대한 검증이 없어 안전하지 않다.
String filter = "(&(sn=" + userSN + ")(userPassword=" + userPassword + "))";
NamingEnumeration<?> results = dctx.search(base, filter, sc);''',
    'javaSafe': '''SearchControls sc = new SearchControls();
sc.setReturningAttributes(new String[]{ "cn", "mail" });
sc.setSearchScope(SearchControls.SUBTREE_SCOPE);
String base = "dc=example,dc=com";
// userSN과 userPassword 값에서 LDAP 필터를 조작할 수 있는 문자열을 검증한 뒤 사용
if (!userSN.matches("[\\w\\s]*") || !userPassword.matches("[\\w]*")) {
    throw new IllegalArgumentException("Invalid input");
}
String filter = "(&(sn=" + userSN + ")(userPassword=" + userPassword + "))";
NamingEnumeration<?> results = dctx.search(base, filter, sc);''',
    'pyVuln': '''from ldap3 import Connection, Server, ALL

def ldap_query(request):
    search_keyword = request.POST.get('search_keyword', '')
    server = Server('ldap.badsource.com', get_info=ALL)
    conn = Connection(server, user=dn, password=password, auto_bind=True)
    # 사용자 입력을 필터링 하지 않는 경우 공격자의 권한 상승으로 이어질 수 있다
    search_str = '(&(objectclass=%s))' % search_keyword
    conn.search('dc=company,dc=com', search_str,
                attributes=['sn', 'cn', 'mail', 'uid'])''',
    'pySafe': '''from ldap3 import Connection, Server, ALL
from ldap3.utils.conv import escape_filter_chars

def ldap_query(request):
    search_keyword = request.POST.get('search_keyword', '')
    server = Server('ldap.goodsource.com', get_info=ALL)
    conn = Connection(server, dn, password, auto_bind=True)
    # 공격에 사용될 수 있는 문자를 이스케이프하여 사용한다
    escape_keyword = escape_filter_chars(search_keyword)
    search_str = '(&(objectclass=%s))' % escape_keyword
    conn.search('dc=company,dc=com', search_str,
                attributes=['sn', 'cn', 'mail', 'uid'])''',
    'note': '',
  },

  '크로스사이트 요청 위조(CSRF) (CWE-352)': {
    'javaLang': 'Java',
    'javaVuln': '''// 어떤 형태의 요청이든 토큰 검증 없이 처리하면 기본적으로 CSRF 취약점을 가질 수 있다.
String id = request.getParameter("id");
String level = request.getParameter("level");
// 정상적인 요청인지 검증하는 토큰 절차가 없어 안전하지 않다.
memberService.updateLevel(id, level);''',
    'javaSafe': '''// 입력화면이 요청되었을 때, 임의의 토큰을 생성한 후 세션에 저장한다.
session.setAttribute("SESSION_CSRF_TOKEN", UUID.randomUUID().toString());
// 입력화면에 토큰을 HIDDEN 필드로 설정한다.
// <input type="hidden" name="param_csrf_token" value="${SESSION_CSRF_TOKEN}" />
// 요청 파라미터와 세션에 저장된 토큰을 비교해서 일치하는 경우에만 요청을 처리한다.
String pToken = request.getParameter("param_csrf_token");
String sToken = (String) session.getAttribute("SESSION_CSRF_TOKEN");
if (pToken != null && pToken.equals(sToken)) {
    // 일치하는 토큰이 존재하는 경우 -> 정상 처리
} else {
    // 토큰이 없거나 값이 일치하지 않는 경우 -> 오류 메시지 출력
}''',
    'pyVuln': '''MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # MIDDLEWARE 목록에서 CSRF 항목을 삭제 또는 주석처리 하면
    # Django 앱에서 CSRF 유효성 검사가 전역적으로 제거된다
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]''',
    'pySafe': '''MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    # MIDDLEWARE 목록에서 CSRF 항목을 활성화 한다
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
# 템플릿의 form 태그 안에는 {% csrf_token %} 을 명시해야 한다.''',
    'note': '',
  },

  '서버사이드 요청 위조(SSRF) (CWE-918)': {
    'javaLang': 'Java',
    'javaVuln': '''protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    // 사용자 입력값(url)을 검증없이 사용하여 안전하지 않다.
    URL url = new URL(req.getParameter("url"));
    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
}''',
    'javaSafe': '''public class Connect {
    // key, value 형식으로 URL의 리스트를 작성한다.
    private Map<String, URL> urlMap;

    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        // 사용자에게 urlMap의 key를 입력받아 urlMap에서 URL값을 참조한다.
        URL url = urlMap.get(req.getParameter("url"));
        // urlMap에서 참조한 값으로 Connection을 만들어 접속한다.
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
    }
}''',
    'pyVuln': '''import requests
from django.shortcuts import render

def call_third_party_api(request):
    addr = request.POST.get('address', '')
    # 사용자가 입력한 주소를 검증하지 않고 HTTP 요청을 보낸 후 응답을 사용자에게 반환
    result = requests.get(addr).text
    return render(request, '/result.html', {'result': result})''',
    'pySafe': '''import requests
from django.shortcuts import render

# 신뢰할 수 있는 자원에 대한 IP를 화이트리스트로 정의한다.
ALLOW_SERVER_LIST = [
    'https://127.0.0.1/latest/',
    'https://192.168.0.1/user_data',
    'https://192.168.0.100/v1/public',
]

def call_third_party_api(request):
    addr = request.POST.get('address', '')
    # 사용자가 입력한 URL을 화이트리스트로 검증한 후 그 결과를 반환한다
    if addr not in ALLOW_SERVER_LIST:
        return render(request, '/error.html', {'error': '허용되지 않은 서버입니다.'})
    result = requests.get(addr).text
    return render(request, '/result.html', {'result': result})''',
    'note': '',
  },

  'HTTP 응답 분할 (CWE-113)': {
    'javaLang': 'Java',
    'javaVuln': '''// 외부로부터 입력받은 값을 검증 없이 사용할 경우 안전하지 않다.
String lastLogin = request.getParameter("last_login");
if (lastLogin == null || "".equals(lastLogin)) {
    return;
}
// 쿠키는 Set-Cookie 응답헤더로 전달되므로 개행문자 포함 여부 검증이 필요
Cookie c = new Cookie("LASTLOGIN", lastLogin);
c.setMaxAge(1000);
c.setSecure(true);
response.addCookie(c);''',
    'javaSafe': '''String lastLogin = request.getParameter("last_login");
if (lastLogin == null || "".equals(lastLogin)) {
    return;
}
// 외부 입력값에서 개행문자(\\r\\n)를 제거한 후 쿠키의 값으로 설정
lastLogin = lastLogin.replaceAll("[\\r\\n]", "");
Cookie c = new Cookie("LASTLOGIN", lastLogin);
c.setMaxAge(1000);
c.setSecure(true);
response.addCookie(c);''',
    'pyVuln': '''from django.http import HttpResponse

def route(request):
    content_type = request.POST.get('content-type')
    # 외부 입력값을 검증 또는 필터링 하지 않고 응답 헤더의 값으로 포함시켜 회신한다
    res = HttpResponse()
    res['Content-Type'] = content_type
    return res''',
    'pySafe': '''from django.http import HttpResponse

def route(request):
    content_type = request.POST.get('content-type')
    # 응답헤더에 포함될 수 있는 외부 입력값 내의 개행 문자를 제거한다
    content_type = content_type.replace('\\r', '')
    content_type = content_type.replace('\\n', '')
    res = HttpResponse()
    res['Content-Type'] = content_type
    return res''',
    'note': '',
  },

  '정수형 오버플로우 (CWE-190)': {
    'javaLang': 'Java',
    'javaVuln': '''String tmp = request.getParameter("slf_msg_param_num");
tmp = StringUtil.isNullTrim(tmp);
// 외부 입력값을 정수형으로 사용할 때 입력값의 크기를 검증하지 않고 사용
int param_ct = Integer.parseInt(tmp);
// param_ct가 오버플로우로 음수가 되면 배열 크기가 음수가 되어 문제가 발생한다.
String[] strArr = new String[param_ct];''',
    'javaSafe': '''String tmp = request.getParameter("slf_msg_param_num");
tmp = StringUtil.isNullTrim(tmp);
// 외부 입력값을 정수형으로 사용할 때 입력값의 크기를 검증하고 사용
try {
    int param_ct = Integer.parseInt(tmp);
    if (param_ct < 0) {
        throw new Exception();
    }
    String[] strArr = new String[param_ct];
} catch (Exception e) {
    msg_str = "잘못된 입력(접근) 입니다.";
}''',
    'pyVuln': '''import numpy as np

def handle_data(number, pow):
    res = np.power(number, pow, dtype=np.int64)
    # 64비트를 넘어서는 숫자와 지수가 입력될 경우 오버플로우가 발생해 결과값이 0이 된다
    return res''',
    'pySafe': '''import numpy as np

MAX_NUMBER = np.iinfo(np.int64).max
MIN_NUMBER = np.iinfo(np.int64).min

def handle_data(number, pow):
    # 파이썬 기본 자료형으로 큰 수를 계산한 후 이를 검사해 오버플로우 탐지
    calculated = number ** pow
    if calculated > MAX_NUMBER or calculated < MIN_NUMBER:
        # 오버플로우 탐지 시 비정상 종료를 나타내는 -1 값 반환
        return -1
    res = np.power(number, pow, dtype=np.int64)
    return res''',
    'note': '',
  },
}
