# -*- coding: utf-8 -*-
PART = {
  'SQL 삽입': {
    'javaLang':'Java',
    'javaVuln':'''//외부로부터 입력받은 값을 검증 없이 사용할 경우 안전하지 않다.
String gubun = request.getParameter("gubun");
......
String sql = "SELECT * FROM board WHERE b_gubun = '" + gubun + "'";
Connection con = db.getConnection();
Statement stmt = con.createStatement();
//외부로부터 입력받은 값이 검증 또는 처리 없이 쿼리로 수행되어 안전하지 않다.
ResultSet rs = stmt.executeQuery(sql);''',
    'javaSafe':'''String gubun = request.getParameter("gubun");
......
//PreparedStatement 사용을 위해 ?문자로 바인딩 변수를 사용한다.
String sql = "SELECT * FROM board WHERE b_gubun = ?";
Connection con = db.getConnection();
//PreparedStatement 객체를 상수 스트링으로 생성한다.
PreparedStatement pstmt = con.prepareStatement(sql);
//파라미터 부분을 setString 등의 메소드로 설정하여 안전하다.
pstmt.setString(1, gubun);
ResultSet rs = pstmt.executeQuery();''',
    'pyVuln':'''from django.shortcuts import render
from django.db import connection
def update_board(request):
  dbconn = connection
  with dbconn.cursor() as curs:
    # 외부로부터 입력받은 값을 검증 없이 사용할 경우 안전하지 않다
    name = request.POST.get('name', '')
    content_id = request.POST.get('content_id', '')
    # 사용자의 검증되지 않은 입력값을 사용해 동적 쿼리문 생성
    sql_query = "update board set name='" + name + "' where content_id='" + content_id + "'"
    # 외부 입력값이 검증 없이 쿼리로 포함되어 안전하지 않다
    curs.execute(sql_query)
    dbconn.commit()
    return render(request, '/success.html')''',
    'pySafe':'''from django.shortcuts import render
from django.db import connection
def update_board(request):
  dbconn = connection
  with dbconn.cursor() as curs:
    name = request.POST.get('name', '')
    content_id = request.POST.get('content_id', '')
    # 외부 입력값 조작으로부터 안전한 인자화된 쿼리를 생성한다.
    sql_query = 'update board set name=%s where content_id=%s'
    # 사용자의 입력값이 인자화된 쿼리에 바인딩 후 실행되므로 안전하다.
    curs.execute(sql_query, (name, content_id))
    dbconn.commit()
    return render(request, '/success.html')''',
    'note':'',
  },
  '코드 삽입': {
    'javaLang':'Java',
    'javaVuln':'''public class CodeInjectionController {
  @RequestMapping(value = "/execute", method = RequestMethod.GET)
  public String execute(@RequestParam("src") String src) throws ScriptException {
    ScriptEngineManager scriptEngineManager = new ScriptEngineManager();
    ScriptEngine scriptEngine = scriptEngineManager.getEngineByName("javascript");
    // 외부 입력값인 src를 javascript eval 함수로 실행하고 있어 안전하지 않다.
    String retValue = (String)scriptEngine.eval(src);
    return retValue;
  }
}''',
    'javaSafe':'''@RequestMapping(value = "/execute", method = RequestMethod.GET)
public String execute(@RequestParam("src") String src) throws ScriptException {
  // 정규식을 이용하여 특수문자 입력시 예외를 발생시킨다.
  if (src.matches("[\\\\w]*") == false) {
    throw new IllegalArgumentException();
  }
  ScriptEngineManager scriptEngineManager = new ScriptEngineManager();
  ScriptEngine scriptEngine = scriptEngineManager.getEngineByName("javascript");
  String retValue = (String)scriptEngine.eval(src);
  return retValue;
}''',
    'pyVuln':'''from django.shortcuts import render
def route(request):
  # 외부에서 입력받은 값을 검증 없이 사용하면 안전하지 않다
  message = request.POST.get('message', '')
  # 외부 입력값을 검증 없이 eval 함수에 전달할 경우 의도하지 않은 코드가
  # 실행될 수 있어 위험하다
  ret = eval(message)
  return render(request, '/success.html', {'data':ret})''',
    'pySafe':'''from django.shortcuts import render
def route(request):
  message = request.POST.get('message', '')
  # 사용자 입력을 영문, 숫자로 제한하며, 특수문자가 포함되어
  # 있을 경우 에러 메시지를 반환한다
  if message.isalnum():
    ret = eval(message)
    return render(request, '/success.html', {'data':ret})
  return render(request, '/error.html')''',
    'note':'',
  },
  '경로 조작 및 자원 삽입': {
    'javaLang':'Java',
    'javaVuln':'''//외부로부터 입력받은 값을 검증 없이 사용할 경우 안전하지 않다.
String fileName = request.getParameter("P");
BufferedInputStream bis = null;
BufferedOutputStream bos = null;
FileInputStream fis = null;
try {
  response.setHeader("Content-Disposition", "attachment;filename="+fileName+";");
  ...
  //외부로부터 입력받은 값이 검증 또는 처리 없이 파일처리에 수행되었다.
  fis = new FileInputStream("C:/datas/" + fileName);
  bis = new BufferedInputStream(fis);
  bos = new BufferedOutputStream(response.getOutputStream());''',
    'javaSafe':'''String fileName = request.getParameter("P");
BufferedInputStream bis = null;
BufferedOutputStream bos = null;
FileInputStream fis = null;
try {
  response.setHeader("Content-Disposition", "attachment;filename="+fileName+";");
  ...
  // 외부 입력받은 값을 경로순회 문자열(. / \\)을 제거하고 사용해야한다.
  fileName = fileName.replaceAll("\\\\.", "").replaceAll("/", "").replaceAll("\\\\\\\\", "");
  fis = new FileInputStream("C:/datas/" + fileName);
  bis = new BufferedInputStream(fis);
  bos = new BufferedOutputStream(response.getOutputStream());''',
    'pyVuln':'''import os
from django.shortcuts import render
def get_info(request):
  # 외부 입력값으로부터 파일명을 입력 받는다
  request_file = request.POST.get('request_file')
  (filename, file_ext) = os.path.splitext(request_file)
  file_ext = file_ext.lower()
  if file_ext not in ['.txt', '.csv']:
    return render(request, '/error.html', {'error':'파일을 열 수 없습니다.'})
  # 입력값을 검증 없이 파일 처리에 사용했다
  with open(request_file) as f:
    data = f.read()
  return render(request, '/success.html', {'data':data})''',
    'pySafe':'''import os
from django.shortcuts import render
def get_info(request):
  request_file = request.POST.get('request_file')
  (filename, file_ext) = os.path.splitext(request_file)
  file_ext = file_ext.lower()
  # 외부 입력값으로 받은 파일 이름은 검증하여 사용한다.
  if file_ext not in ['.txt', '.csv']:
    return render(request, '/error.html', {'error':'파일을 열수 없습니다.'})
  # 파일 명에서 경로 조작 문자열을 필터링 한다.
  filename = filename.replace('.', '')
  filename = filename.replace('/', '')
  filename = filename.replace('\\\\', '')
  with open(filename + file_ext) as f:
    data = f.read()
  return render(request, '/success.html', {'data':data})''',
    'note':'',
  },
  '크로스사이트 스크립트(XSS)': {
    'javaLang':'Java',
    'javaVuln':'''<% String keyword = request.getParameter("keyword"); %>
//외부 입력값에 대하여 검증 없이 화면에 출력될 경우 공격스크립트가 포함된
//URL을 생성 할 수 있어 안전하지 않다.(Reflected XSS)
검색어 : <%=keyword%>

//게시판 등의 입력form으로 외부값이 DB에 저장되고, 이를 검증 없이 화면에
//출력될 경우 공격스크립트가 실행되어 안전하지 않다.(Stored XSS)
검색결과 : ${m.content}
<script type="text/javascript">
//외부 입력값을 검증 없이 브라우저에서 실행하면 안전하지 않다.(DOM 기반 XSS)
document.write("keyword:" + <%=keyword%>);
</script>''',
    'javaSafe':'''<% String keyword = request.getParameter("keyword"); %>
// 방법1. 입력값에 대하여 스크립트 공격가능성이 있는 문자열을 치환한다.
keyword = keyword.replaceAll("&", "&amp;");
keyword = keyword.replaceAll("<", "&lt;");
keyword = keyword.replaceAll(">", "&gt;");
keyword = keyword.replaceAll("\\"", "&quot;");
keyword = keyword.replaceAll("'", "&#x27;");
검색어 : <%=keyword%>
// 방법2. JSP에서 출력값에 JSTL c:out 을 사용하여 처리한다.
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
검색결과 : <c:out value="${m.content}"/>''',
    'pyVuln':'''from django.shortcuts import render
from django.utils.safestring import mark_safe
def profile_link(request):
    # 외부 입력값을 검증 없이 HTML 태그 생성의 인자로 사용
    profile_url = request.POST.get('profile_url')
    profile_name = request.POST.get('profile_name')
    object_link = '<a href="{}">{}</a>'.format(profile_url, profile_name)
    # mark_safe함수는 Django의 XSS escape 정책을 따르지 않는다
    object_link = mark_safe(object_link)
    return render(request, 'my_profile.html', {'object_link':object_link})''',
    'pySafe':'''from django.shortcuts import render
def profile_link(request):
    profile_url = request.POST.get('profile_url')
    profile_name = request.POST.get('profile_name')
    object_link = '<a href="{}">{}</a>'.format(profile_url, profile_name)
    # 신뢰할 수 없는 데이터에 대해서는 mark_safe 함수를 사용해선 안 된다
    # (Django 템플릿은 기본적으로 위험 문자를 HTML 엔티티로 치환한다)
    return render(request, 'my_profile.html', {'object_link':object_link})''',
    'note':'',
  },
  '운영체제 명령어 삽입': {
    'javaLang':'Java',
    'javaVuln':'''public static void main(String args[]) throws IOException {
  // 실행할 프로그램을 제한하지 않아 파라미터로 전달되는 모든 프로그램이 실행될 수 있다.
  String cmd = args[0];
  Process ps = null;
  try {
    ps = Runtime.getRuntime().exec(cmd);
    ...
}''',
    'javaSafe':'''public static void main(String args[]) throws IOException {
  // 실행할 수 있는 프로그램을 노트패드와 계산기로 제한하고 있다.
  List<String> allowedCommands = new ArrayList<String>();
  allowedCommands.add("notepad");
  allowedCommands.add("calc");
  String cmd = args[0];
  if (!allowedCommands.contains(cmd)) {
    System.err.println("허용되지 않은 명령어입니다.");
    return;
  }
  Process ps = null;
  try {
    ps = Runtime.getRuntime().exec(cmd);
    ......
}''',
    'pyVuln':'''import os
from django.shortcuts import render
def execute_command(request):
  app_name_string = request.POST.get('app_name', '')
  # 입력 파라미터를 제한하지 않아 외부 입력값으로 전달된
  # 모든 프로그램이 실행될 수 있음
  os.system(app_name_string)
  return render(request, '/success.html')''',
    'pySafe':'''import os
from django.shortcuts import render
ALLOW_PROGRAM = ['notepad', 'calc']
def execute_command(request):
  app_name_string = request.POST.get('app_name', '')
  # 입력받은 파라미터가 허용된 시스템 명령어 목록에 포함되는지 검사
  if app_name_string not in ALLOW_PROGRAM:
    return render(request, '/error.html', {'error':'허용되지 않은 프로그램입니다.'})
  os.system(app_name_string)
  return render(request, '/success.html')''',
    'note':'',
  },
  '위험한 형식 파일 업로드': {
    'javaLang':'Java',
    'javaVuln':'''MultipartRequest multi = new MultipartRequest(
    request, savePath, sizeLimit, "euc-kr", new DefaultFileRenamePolicy());
......
//업로드 되는 파일명을 검증 없이 사용하고 있어 안전하지 않다.
String fileName = multi.getFilesystemName("filename");
......
pstmt.setString(6, fileName);
pstmt.executeUpdate();
Thumbnail.create(savePath+"/"+fileName, savePath+"/"+"s_"+fileName, 150);''',
    'javaSafe':'''MultipartRequest multi = new MultipartRequest(
    request, savePath, sizeLimit, "euc-kr", new DefaultFileRenamePolicy());
......
String fileName = multi.getFilesystemName("filename");
if (fileName != null) {
  //1. 마지막 "." 문자열 기준으로 실제 확장자를 확인하고, 소문자로 변환한다.
  String fileExt = fileName.substring(fileName.lastIndexOf(".")+1).toLowerCase();
  //2. 화이트 리스트 방식으로 허용되는 확장자로 업로드를 제한해야 안전하다.
  if (!"gif".equals(fileExt) && !"jpg".equals(fileExt) && !"png".equals(fileExt)) {
    alertMessage("업로드 불가능한 파일입니다.");
    return;
  }
}''',
    'pyVuln':'''from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
def file_upload(request):
    if request.FILES['upload_file']:
        # 사용자가 업로드하는 파일을 검증 없이 저장하고 있어 안전하지 않다
        upload_file = request.FILES['upload_file']
        fs = FileSystemStorage(location='media/screenshot', base_url='media/screenshot')
        # 업로드 하는 파일에 대한 크기, 개수, 확장자 등을 검증하지 않음
        filename = fs.save(upload_file.name, upload_file)
        return render(request, '/success.html', {'filename':filename})
    return render(request, '/error.html', {'error':'파일 업로드 실패'})''',
    'pySafe':'''import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
FILE_SIZE_LIMIT = 5242880          # 업로드 파일의 최대 사이즈 제한 (5MB)
WHITE_LIST_EXT = ['.jpg', '.jpeg']  # 허용 확장자는 화이트리스트로 관리
def file_upload(request):
  for filename, upload_file in request.FILES.items():
    # 파일 타입(MIME) 체크 - 확장자만 검사하면 변조로 우회될 수 있다
    if upload_file.content_type != 'image/jpeg':
      return render(request, '/error.html', {'error': '파일 타입 오류'})
    if upload_file.size > FILE_SIZE_LIMIT:
      return render(request, '/error.html', {'error': '파일사이즈 오류'})
    file_name, file_ext = os.path.splitext(upload_file.name)
    if file_ext.lower() not in WHITE_LIST_EXT:
      return render(request, '/error.html', {'error': '파일 타입 오류'})
    fs = FileSystemStorage(location='media/screenshot', base_url='media/screenshot')
    fs.save(upload_file.name, upload_file)
  return render(request, '/success.html')''',
    'note':'',
  },
  '신뢰되지 않는 URL 주소로 자동접속 연결': {
    'javaLang':'Java',
    'javaVuln':'''String id = (String)session.getValue("id");
String bn = request.getParameter("gubun");
//외부로부터 입력받은 URL이 검증 없이 다른 사이트로 이동이 가능하여 안전하지 않다.
String rd = request.getParameter("redirect");
if (id.length() > 0) {
  ......
  if ("0".equals(rs.getString(1)) && "01AD".equals(bn)) {
    response.sendRedirect(rd);
    return;
  }
}''',
    'javaSafe':'''//이동 할 수 있는 URL범위를 제한하여 피싱 사이트등으로 이동 못하도록 한다.
String allowedUrl[] = { "/main.do", "/login.jsp", "list.do" };
......
String rd = request.getParameter("redirect");
try {
  rd = allowedUrl[Integer.parseInt(rd)];
} catch(NumberFormatException e) {
  return "잘못된 접근입니다.";
} catch(ArrayIndexOutOfBoundsException e) {
  return "잘못된 입력입니다.";
}
response.sendRedirect(rd);''',
    'pyVuln':'''from django.shortcuts import redirect
def redirect_url(request):
  url_string = request.POST.get('url', '')
  # 사용자 입력에 포함된 URL 주소로 리다이렉트 하는 경우
  # 피싱 사이트로 접속되는 등 사용자가 피싱 공격에 노출될 수 있다
  return redirect(url_string)''',
    'pySafe':'''from django.shortcuts import render, redirect
ALLOW_URL_LIST = [
    '127.0.0.1',
    'https://login.myservice.com',
    '/notice',
]
def redirect_url(request):
  url_string = request.POST.get('url', '')
  # 이동할 수 있는 URL 범위를 제한하여 위험한 사이트의 접근을 차단하고 있다
  if url_string not in ALLOW_URL_LIST:
    return render(request, '/error.html', {'error':'허용되지 않는 주소입니다.'})
  return redirect(url_string)''',
    'note':'',
  },
}
