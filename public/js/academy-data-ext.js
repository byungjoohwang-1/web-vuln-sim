// Auto-generated extended question bank (객관식/주관식 대량 추가) — Java/Python 중심
// 8개 파트 병합(입력검증/보안기능/코드결함/시간상태/에러처리/캡슐화/API오용/법령·개념·진단·설계) + 중복 제거

// ===== partA =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  { c:"입력검증", q:"다음 Java 코드의 보안약점으로 가장 적절한 것은?", o:["SQL 삽입","경로 조작","XSS","정수 오버플로우"], a:0, e:"사용자 입력 id를 문자열 연결로 SQL 쿼리에 삽입하므로 SQL 삽입에 취약하다. PreparedStatement와 파라미터 바인딩(?)을 사용해야 한다.", code:`String sql = "SELECT * FROM users WHERE id = '" + request.getParameter("id") + "'";\nStatement stmt = conn.createStatement();\nResultSet rs = stmt.executeQuery(sql);` },
  { c:"입력검증", q:"다음 Java 코드는 SQL 삽입에 안전한가? 그 이유로 옳은 것은?", o:["안전하다. PreparedStatement와 ? 바인딩으로 입력이 데이터로만 처리됨","안전하지 않다. 문자열 연결이 있음","안전하지 않다. setString을 setInt로 바꿔야 함","안전하지 않다. executeQuery 대신 execute를 써야 함"], a:0, e:"PreparedStatement로 쿼리 구조를 먼저 컴파일하고 ? 위치에 바인딩하면 입력은 데이터로만 처리되어 SQL 삽입이 방지된다.", code:`PreparedStatement ps = conn.prepareStatement(\n    "SELECT * FROM users WHERE id = ?");\nps.setString(1, request.getParameter("id"));\nResultSet rs = ps.executeQuery();` },
  { c:"입력검증", q:"SQL 삽입을 근본적으로 방지하는 가장 권장되는 방법은?", o:["입력값에서 작은따옴표를 제거","PreparedStatement 등 매개변수화된 쿼리 사용","쿼리 결과 건수를 1건으로 제한","DB 계정 비밀번호를 주기적으로 변경"], a:1, e:"매개변수화된 쿼리(PreparedStatement)는 쿼리 구조와 데이터를 분리하여 입력값이 실행 구문으로 해석되지 않게 하므로 SQL 삽입의 근본 대책이다. 따옴표 제거 같은 블랙리스트는 우회 가능하다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["안전함","SQL 삽입","XXE","LDAP 삽입"], a:1, e:"f-string으로 사용자 입력을 쿼리에 직접 삽입하면 SQL 삽입에 취약하다. cursor.execute(\"... WHERE name=%s\", (name,)) 처럼 파라미터 바인딩을 사용해야 한다.", code:`name = request.args.get("name")\nquery = f"SELECT * FROM members WHERE name = '{name}'"\ncursor.execute(query)` },
  { c:"입력검증", q:"다음 Python 코드의 SQL 삽입 안전성 평가로 옳은 것은?", o:["안전하다. 파라미터화된 쿼리를 사용함","위험하다. % 포매팅과 동일함","위험하다. 튜플 대신 리스트를 써야 함","위험하다. fetchall이 문제임"], a:0, e:"execute의 두 번째 인자로 파라미터를 전달하면 DB 드라이버가 안전하게 바인딩하므로 SQL 삽입에 안전하다. 이는 문자열 % 포매팅과 다르다.", code:`cursor.execute("SELECT * FROM members WHERE name = %s", (name,))\nrows = cursor.fetchall()` },
  { c:"입력검증", q:"동적 SQL이 불가피하게 테이블/컬럼명을 입력으로 받아야 할 때 가장 안전한 처리는?", o:["입력값을 그대로 쿼리에 연결","화이트리스트로 허용된 식별자만 매핑하여 사용","작은따옴표만 이스케이프","입력값을 Base64로 인코딩"], a:1, e:"테이블명/컬럼명은 바인딩 파라미터로 처리할 수 없으므로, 허용된 식별자 목록(화이트리스트)에 존재하는 값만 사용하도록 검증해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["SQL 삽입","경로 조작(Path Traversal)","XSS","CSRF"], a:1, e:"사용자 입력 filename을 검증 없이 파일 경로에 결합하면 '../' 등을 통해 의도하지 않은 경로의 파일에 접근할 수 있다(경로 조작).", code:`String filename = request.getParameter("file");\nFile f = new File("/var/data/" + filename);\nFileInputStream fis = new FileInputStream(f);` },
  { c:"입력검증", q:"경로 조작(Path Traversal)을 방지하기 위한 적절한 방법이 아닌 것은?", o:["정규화(canonical path) 후 허용 디렉터리 하위인지 검증","파일명에서 경로 구분자와 '..' 제거/거부","허용된 파일명 화이트리스트 사용","파일을 읽기 전용으로 오픈"], a:3, e:"읽기 전용 오픈은 경로 조작 자체를 막지 못한다. 정규화 후 기준 디렉터리 검증, '..' 차단, 화이트리스트가 올바른 대책이다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드에서 경로 조작 방지를 위해 추가로 필요한 검증은?", o:["없음, 이미 안전함","getCanonicalPath()로 정규화 후 기준 디렉터리 하위인지 확인","파일 크기 제한","파일 확장자를 소문자로 변환"], a:1, e:"replace로 '..'를 제거해도 '....//' 같은 변형으로 우회 가능하다. getCanonicalPath()로 실제 경로를 구한 뒤 허용된 기준 경로의 하위에 있는지 startsWith로 확인해야 한다.", code:`String name = req.getParameter("f").replace("..", "");\nFile f = new File(BASE_DIR, name);` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점과 올바른 대책은?", o:["안전함","경로 조작 - os.path.realpath로 정규화 후 base 하위 검증","SSRF - 도메인 화이트리스트","XXE - DTD 비활성화"], a:1, e:"join은 '../'를 막지 못해 경로 조작에 취약하다. os.path.realpath로 정규화한 경로가 허용된 base 디렉터리로 시작하는지 검증해야 한다.", code:`path = os.path.join("/srv/files", request.args["name"])\nreturn open(path).read()` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["SQL 삽입","XSS(크로스 사이트 스크립트)","경로 조작","정수 오버플로우"], a:1, e:"사용자 입력 name을 인코딩 없이 HTML 응답에 출력하면 스크립트가 실행될 수 있는 반사형 XSS에 취약하다. 출력 시 HTML 엔티티 인코딩이 필요하다.", code:`String name = request.getParameter("name");\nout.println("<div>Welcome " + name + "</div>");` },
  { c:"입력검증", q:"XSS를 방지하기 위한 가장 핵심적인 대책은?", o:["입력값 길이 제한","출력 컨텍스트에 맞는 인코딩(이스케이프)","쿠키에 Secure 속성 부여","HTTPS 적용"], a:1, e:"XSS는 데이터가 HTML/JS/속성/URL 등 출력되는 컨텍스트에 맞게 인코딩될 때 방지된다. 컨텍스트별 이스케이프가 핵심 대책이다.", code:`` },
  { c:"입력검증", q:"다음 Python(Flask) 코드의 XSS 위험성 평가로 옳은 것은?", o:["render_template_string에 사용자 입력을 직접 넣어 XSS/SSTI 위험","안전함, Jinja2가 자동 이스케이프하므로 문제 없음","SQL 삽입 위험","경로 조작 위험"], a:0, e:"render_template_string에 사용자 입력으로 만든 템플릿 문자열을 넣으면 자동 이스케이프가 무력화되고 서버측 템플릿 삽입(SSTI) 및 XSS로 이어진다. 템플릿은 고정하고 데이터만 전달해야 한다.", code:`name = request.args.get("name")\nreturn render_template_string("<h1>Hi " + name + "</h1>")` },
  { c:"입력검증", q:"DOM 기반 XSS의 특징으로 옳은 것은?", o:["서버에서 응답에 입력을 반영하여 발생","클라이언트 측 자바스크립트가 신뢰되지 않은 데이터를 위험한 sink에 전달해 발생","DB에 저장된 후 다른 사용자에게 실행","HTTP 헤더 분할로 발생"], a:1, e:"DOM 기반 XSS는 서버 응답과 무관하게 브라우저의 자바스크립트가 location, innerHTML 등 위험한 sink로 신뢰되지 않은 데이터를 전달할 때 발생한다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XSS","OS 명령어 삽입","경로 조작","XXE"], a:1, e:"Runtime.exec에 셸을 통해 사용자 입력을 연결하면 ';', '|', '&&' 등으로 임의 명령을 실행할 수 있는 OS 명령어 삽입에 취약하다.", code:`String host = request.getParameter("host");\nRuntime.getRuntime().exec("ping -c 1 " + host);` },
  { c:"입력검증", q:"OS 명령어 삽입을 방지하기 위한 가장 좋은 방법은?", o:["입력에서 세미콜론만 제거","명령과 인자를 배열로 분리해 셸 해석 없이 실행하고 입력을 화이트리스트 검증","sudo로 권한 낮추기","명령 실행 로그 남기기"], a:1, e:"셸을 거치지 않고 명령/인자를 배열로 전달(ProcessBuilder, subprocess 리스트)하면 메타문자가 해석되지 않으며, 입력은 화이트리스트로 검증해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["안전함","OS 명령어 삽입","SQL 삽입","정수 오버플로우"], a:1, e:"os.system에 사용자 입력을 문자열 연결로 전달하면 셸 메타문자를 통해 명령어 삽입이 가능하다. subprocess.run([\"ping\",\"-c\",\"1\",host], shell=False)처럼 리스트 인자를 사용해야 한다.", code:`host = request.args.get("host")\nos.system("ping -c 1 " + host)` },
  { c:"입력검증", q:"다음 Python subprocess 사용 중 OS 명령어 삽입에 가장 취약한 것은?", o:["subprocess.run([\"ls\", path])","subprocess.run([\"grep\", pattern, file])","subprocess.run(\"ls \" + path, shell=True)","subprocess.run([\"cat\", filename])"], a:2, e:"shell=True와 문자열 연결을 함께 쓰면 셸이 메타문자를 해석하여 명령어 삽입에 취약하다. 나머지는 리스트 인자와 shell=False(기본)로 안전하다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드(ProcessBuilder)의 명령어 삽입 안전성은?", o:["안전하다. 인자를 분리해 셸을 거치지 않음","위험하다. 여전히 셸이 실행됨","위험하다. start() 대신 exec를 써야 함","위험하다. 인자 개수가 문제임"], a:0, e:"ProcessBuilder에 명령과 인자를 개별 요소로 전달하면 셸을 거치지 않으므로 메타문자가 해석되지 않아 명령어 삽입에 안전하다(입력 자체에 대한 의미 검증은 별도).", code:`ProcessBuilder pb = new ProcessBuilder("ping", "-c", "1", host);\npb.start();` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["SQL 삽입","코드 삽입(Code Injection)","경로 조작","XSS"], a:1, e:"ScriptEngine(자바스크립트 엔진)에 사용자 입력을 eval하면 임의 코드가 서버에서 실행되는 코드 삽입에 취약하다.", code:`ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");\nengine.eval(request.getParameter("expr"));` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["코드 삽입 - eval에 신뢰되지 않은 입력","경로 조작","SQL 삽입","XXE"], a:0, e:"eval(또는 exec)에 사용자 입력을 전달하면 임의 파이썬 코드가 실행된다. 산술식 평가가 필요하면 ast.literal_eval이나 안전한 파서를 사용해야 한다.", code:`expr = request.form["expr"]\nresult = eval(expr)` },
  { c:"입력검증", q:"신뢰되지 않은 입력으로 산술/데이터 평가가 필요할 때 Python에서 권장되는 안전한 함수는?", o:["eval()","exec()","ast.literal_eval()","compile()"], a:2, e:"ast.literal_eval은 리터럴(숫자, 문자열, 튜플 등)만 안전하게 평가하며 임의 코드 실행이 불가능하므로 eval/exec의 안전한 대안이다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XSS","위험한 형식 파일 업로드","SQL 삽입","CSRF"], a:1, e:"업로드 파일을 확장자/콘텐츠 검증 없이 웹 루트에 저장하면 JSP/PHP 같은 실행 가능한 파일이 업로드되어 원격 코드 실행으로 이어질 수 있다.", code:`Part part = request.getPart("file");\nString name = part.getSubmittedFileName();\npart.write("/app/webroot/upload/" + name);` },
  { c:"입력검증", q:"위험한 형식의 파일 업로드를 방지하기 위한 대책으로 가장 거리가 먼 것은?", o:["허용 확장자 화이트리스트와 MIME/콘텐츠 검증","웹 실행 권한이 없는 디렉터리에 저장","서버가 정한 임의의 파일명으로 저장","업로드 파일 크기만 제한하면 충분"], a:3, e:"크기 제한만으로는 악성 실행 파일 업로드를 막지 못한다. 화이트리스트 확장자/콘텐츠 검증, 실행 권한 없는 경로 저장, 파일명 재지정이 필요하다.", code:`` },
  { c:"입력검증", q:"파일 업로드 시 확장자 검증을 블랙리스트(차단 목록)로만 하면 위험한 이유는?", o:["블랙리스트는 성능이 느려서","대소문자/이중확장자/누락된 확장자 등 우회가 쉬워서","블랙리스트는 표준이 아니라서","화이트리스트보다 코드가 길어서"], a:1, e:"블랙리스트는 .jsP, file.php.jpg, 새로운 실행 확장자 등으로 우회되기 쉽다. 허용 목록(화이트리스트) 방식이 안전하다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XSS","신뢰되지 않은 URL 자동접속(Open Redirect)","경로 조작","SQL 삽입"], a:1, e:"사용자가 제공한 url 파라미터로 검증 없이 리다이렉트하면 피싱 사이트로 유도되는 오픈 리다이렉트에 취약하다. 허용된 내부 경로/도메인만 리다이렉트해야 한다.", code:`String url = request.getParameter("url");\nresponse.sendRedirect(url);` },
  { c:"입력검증", q:"오픈 리다이렉트(신뢰되지 않은 URL 자동접속)를 방지하는 방법으로 옳은 것은?", o:["리다이렉트 대상 도메인을 허용 목록과 대조","외부 URL이면 새 창으로 열기","URL을 URL 인코딩","리다이렉트 횟수 제한"], a:0, e:"리다이렉트 대상이 사전에 허용된 내부 경로 또는 도메인 화이트리스트에 속하는지 검증해야 오픈 리다이렉트를 막을 수 있다.", code:`` },
  { c:"입력검증", q:"다음 Python(Flask) 코드의 보안약점은?", o:["오픈 리다이렉트","SSRF","XSS","CSRF"], a:0, e:"next 파라미터를 검증 없이 redirect 대상으로 사용하면 외부 악성 사이트로 유도될 수 있다. url_parse로 호스트가 비어있는(같은 사이트) 상대경로인지 확인해야 한다.", code:`next = request.args.get("next")\nreturn redirect(next)` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XXE(XML External Entity)","SQL 삽입","XSS","경로 조작"], a:0, e:"외부 엔티티 처리를 비활성화하지 않은 XML 파서는 외부 엔티티를 통해 로컬 파일 노출, SSRF, DoS가 가능한 XXE에 취약하다.", code:`DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();\nDocumentBuilder db = dbf.newDocumentBuilder();\nDocument doc = db.parse(request.getInputStream());` },
  { c:"입력검증", q:"Java에서 XXE를 방지하기 위해 DocumentBuilderFactory에 설정해야 하는 것으로 가장 적절한 것은?", o:["setValidating(true)","disallow-doctype-decl 등 외부 엔티티/DTD 비활성화 feature 설정","setNamespaceAware(true)","setCoalescing(true)"], a:1, e:"FEATURE_SECURE_PROCESSING과 함께 http://apache.org/xml/features/disallow-doctype-decl을 true로, 외부 일반/파라미터 엔티티를 false로 설정해 DTD/외부 엔티티를 차단해야 XXE가 방지된다.", code:`` },
  { c:"입력검증", q:"다음 Python lxml 코드의 XXE 안전성 평가로 옳은 것은?", o:["안전하다. resolve_entities=False로 외부 엔티티 해석을 막음","위험하다. no_network가 빠짐","위험하다. parse 대신 fromstring을 써야 함","위험하다. 항상 DTD를 허용함"], a:0, e:"lxml에서 XMLParser(resolve_entities=False)(추가로 no_network=True, dtd_validation=False)를 사용하면 외부 엔티티가 해석되지 않아 XXE를 방지한다.", code:`parser = etree.XMLParser(resolve_entities=False, no_network=True)\ntree = etree.fromstring(data, parser)` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XXE","XML 삽입(XML Injection)","SQL 삽입","XSS"], a:1, e:"사용자 입력을 XML 문서에 문자열로 직접 삽입하면 태그/구조를 조작하는 XML 삽입에 취약하다. XML 특수문자를 이스케이프하거나 안전한 빌더 API를 사용해야 한다.", code:`String xml = "<user><name>" + userName + "</name></user>";\nparseAndStore(xml);` },
  { c:"입력검증", q:"XML 삽입을 방지하기 위한 적절한 처리는?", o:["입력을 그대로 두고 응답만 인코딩","XML 메타문자(<, >, &, 따옴표)를 이스케이프하거나 안전한 XML API 사용","XML을 JSON으로 변환","DTD를 추가"], a:1, e:"XML 삽입은 입력값을 XML에 합칠 때 <,>,&,\",' 같은 메타문자를 엔티티로 이스케이프하거나 DOM/JAXB 등 안전한 빌더를 사용해 구조 변조를 막는다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["SQL 삽입","LDAP 삽입","경로 조작","XSS"], a:1, e:"사용자 입력을 LDAP 검색 필터에 직접 연결하면 '*' ')' '(' 등으로 필터 논리를 변조하는 LDAP 삽입에 취약하다. 특수문자 이스케이프가 필요하다.", code:`String filter = "(uid=" + request.getParameter("user") + ")";\nNamingEnumeration r = ctx.search("ou=people", filter, sc);` },
  { c:"입력검증", q:"LDAP 삽입 방지를 위해 이스케이프해야 하는 LDAP 검색 필터 특수문자로 옳은 것은?", o:["%, _, [","( ) * \\ NUL","; -- /*","< > & \""], a:1, e:"LDAP 검색 필터에서는 '(' ')' '*' '\\' NUL 등이 특수 의미를 가지므로 이스케이프해야 LDAP 삽입을 방지할 수 있다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["오픈 리다이렉트","SSRF(Server-Side Request Forgery)","경로 조작","XXE"], a:1, e:"사용자가 지정한 URL로 서버가 직접 요청을 보내면 내부망 자원(메타데이터 서버 169.254.169.254 등)에 접근하는 SSRF에 취약하다. 대상 호스트/스킴 화이트리스트가 필요하다.", code:`String target = request.getParameter("url");\nURL u = new URL(target);\nInputStream in = u.openConnection().getInputStream();` },
  { c:"입력검증", q:"SSRF를 방지하기 위한 대책으로 가장 적절한 것은?", o:["요청 URL을 로그에 남김","허용 도메인/스킴 화이트리스트와 사설/링크로컬 IP 차단","요청 타임아웃 설정","User-Agent 헤더 검증"], a:1, e:"SSRF는 대상 스킴(http/https만 허용)과 도메인 화이트리스트, 사설/링크로컬/루프백 IP 차단으로 막는다. DNS 리바인딩 대비 IP 재검증도 필요하다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["SSRF","SQL 삽입","XSS","코드 삽입"], a:0, e:"requests.get에 사용자 입력 URL을 검증 없이 전달하면 서버가 내부망/클라우드 메타데이터로 요청을 보낼 수 있는 SSRF에 취약하다.", code:`url = request.args.get("u")\nresp = requests.get(url)\nreturn resp.text` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["XSS","HTTP 응답분할(Response Splitting)","SQL 삽입","경로 조작"], a:1, e:"사용자 입력을 CR/LF 제거 없이 HTTP 헤더(쿠키/Location)에 넣으면 개행문자로 응답을 분할해 헤더 주입/캐시 오염을 일으키는 HTTP 응답분할에 취약하다.", code:`String v = request.getParameter("v");\nresponse.addHeader("X-Custom", v);` },
  { c:"입력검증", q:"HTTP 응답분할(Response Splitting)을 방지하는 핵심 처리는?", o:["헤더 값에서 CR(\\r), LF(\\n) 제거 또는 거부","헤더 값을 Base64 인코딩","쿠키에 HttpOnly 부여","응답 압축 적용"], a:0, e:"응답분할은 입력에 포함된 CR/LF가 헤더 경계를 만들 때 발생하므로, 헤더에 넣는 값에서 개행문자를 제거하거나 거부해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["메모리 버퍼 오버플로우","정수형 오버플로우","경로 조작","XSS"], a:1, e:"int 곱셈 결과가 int 범위를 넘으면 음수/작은 값으로 래핑되는 정수 오버플로우가 발생한다. 곱셈 전 범위 검증 또는 Math.multiplyExact 사용이 필요하다.", code:`int count = Integer.parseInt(request.getParameter("n"));\nint size = count * 1024;\nbyte[] buf = new byte[size];` },
  { c:"입력검증", q:"정수형 오버플로우가 보안 문제로 이어지는 대표적 경로는?", o:["로그 파일 비대화","오버플로우된 크기로 버퍼 할당/경계 계산이 잘못되어 메모리 손상 유발","CPU 사용량 증가","네트워크 지연"], a:1, e:"오버플로우로 의도보다 작은 크기가 계산되면 버퍼 할당/길이 검사가 잘못되어 버퍼 오버플로우 등 메모리 손상으로 이어질 수 있다.", code:`` },
  { c:"입력검증", q:"Java에서 정수 오버플로우를 예외로 감지하려고 할 때 사용하는 것은?", o:["Math.abs","Math.addExact / Math.multiplyExact","Integer.MAX_VALUE 비교만으로 충분","BigDecimal.round"], a:1, e:"Math.addExact, Math.multiplyExact 등은 결과가 범위를 넘으면 ArithmeticException을 던져 오버플로우를 안전하게 감지할 수 있다.", code:`` },
  { c:"입력검증", q:"다음 C 코드의 보안약점은?", o:["정수 오버플로우","메모리 버퍼 오버플로우","포맷 스트링","경로 조작"], a:1, e:"strcpy는 길이 검사를 하지 않아 입력이 버퍼 크기를 초과하면 인접 메모리를 덮어쓰는 버퍼 오버플로우가 발생한다. strncpy/strlcpy 등 경계 검사 함수를 사용해야 한다.", code:`char buf[16];\nstrcpy(buf, argv[1]);` },
  { c:"입력검증", q:"메모리 버퍼 오버플로우를 완화하는 기법이 아닌 것은?", o:["경계 검사 함수 사용(strncpy 등)","스택 카나리, DEP/NX, ASLR","입력 길이 검증","setuid 비트 제거"], a:3, e:"setuid 제거는 권한 관리 이슈로 버퍼 오버플로우 자체와 직접 관련이 없다. 경계 검사, 카나리/DEP/ASLR, 길이 검증이 완화책이다.", code:`` },
  { c:"입력검증", q:"다음 C 코드의 보안약점은?", o:["버퍼 오버플로우","포맷 스트링 삽입(Format String)","정수 오버플로우","경로 조작"], a:1, e:"printf의 포맷 인자 자리에 사용자 입력을 직접 넣으면 '%n','%x' 등 포맷 지정자로 메모리 읽기/쓰기가 가능한 포맷 스트링 취약점이 된다. printf(\"%s\", input)으로 고정해야 한다.", code:`char *input = argv[1];\nprintf(input);` },
  { c:"입력검증", q:"포맷 스트링 삽입을 방지하는 올바른 호출은?", o:["printf(userInput)","printf(\"%s\", userInput)","fprintf(stdout, userInput)","sprintf(buf, userInput)"], a:1, e:"포맷 문자열을 고정 리터럴로 두고 사용자 입력은 %s 인자로 전달하면 포맷 지정자가 해석되지 않아 안전하다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["CSRF(Cross-Site Request Forgery)","XSS","SQL 삽입","SSRF"], a:0, e:"상태를 변경하는 요청에 CSRF 토큰 등 출처 검증이 없으면, 사용자의 인증 세션을 악용해 위조된 요청을 처리하는 CSRF에 취약하다.", code:`@PostMapping("/transfer")\npublic void transfer(@RequestParam String to, @RequestParam int amount){\n    accountService.transfer(currentUser(), to, amount);\n}` },
  { c:"입력검증", q:"CSRF를 방지하기 위한 대책으로 가장 적절한 것은?", o:["입력값 HTML 인코딩","요청별 CSRF 토큰 검증 및 SameSite 쿠키 적용","비밀번호 복잡도 강화","SQL 파라미터 바인딩"], a:1, e:"CSRF는 예측 불가능한 CSRF 토큰을 폼/요청에 포함해 서버가 검증하고, SameSite 쿠키 속성으로 교차 사이트 전송을 제한하여 방지한다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (보안기능 결정에 사용되는 부적절한 입력값)", o:["SQL 삽입","보안 결정을 신뢰되지 않은 입력(클라이언트 값)에 의존","XSS","경로 조작"], a:1, e:"권한/관리자 여부 같은 보안 결정을 클라이언트가 보낸 파라미터(isAdmin)로 판단하면 사용자가 값을 위조해 권한을 상승시킬 수 있다. 보안 결정은 서버측 신뢰 데이터(세션/DB)로 해야 한다.", code:`boolean isAdmin = Boolean.parseBoolean(request.getParameter("isAdmin"));\nif (isAdmin) { showAdminPanel(); }` },
  { c:"입력검증", q:"'보안기능 결정에 사용되는 부적절한 입력값' 약점을 피하는 원칙은?", o:["인가/권한 판단은 변조 가능한 클라이언트 입력이 아닌 서버측 신뢰 데이터로 수행","모든 입력을 암호화","쿠키를 사용하지 않음","HTTPS만 적용하면 충분"], a:0, e:"가격, 권한, 식별자 등 보안에 영향을 주는 결정은 hidden 필드/파라미터/쿠키 같은 변조 가능한 입력이 아니라 서버 세션/DB의 신뢰된 값으로 내려야 한다.", code:`` },
  { c:"입력검증", q:"입력 검증에서 화이트리스트 방식이 블랙리스트 방식보다 권장되는 이유로 옳은 것은?", o:["구현이 항상 더 빠르기 때문","허용되는 형태만 통과시켜 알려지지 않은 공격 패턴도 차단하기 때문","로그가 더 적게 남기 때문","정규식이 필요 없기 때문"], a:1, e:"화이트리스트는 '허용된 것만' 통과시키므로 미지의/변형된 공격 입력까지 기본 차단된다. 블랙리스트는 알려진 패턴만 막아 우회가 쉽다.", code:`` },
  { c:"입력검증", q:"입력 검증을 클라이언트(자바스크립트)에서만 수행할 때의 문제는?", o:["성능 저하","공격자가 클라이언트 검증을 우회해 서버로 직접 요청 가능","SEO 저하","브라우저 호환성 문제"], a:1, e:"클라이언트 검증은 사용자 편의/UX용이며 우회 가능하므로, 보안을 위한 입력 검증은 반드시 서버측에서 수행해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["LDAP 삽입","HTTP 응답분할(헤더 주입)","SSRF","XXE"], a:1, e:"사용자 입력을 그대로 응답 헤더에 설정하면 CR/LF가 포함될 경우 헤더 주입/응답분할이 발생한다. 개행문자 제거/검증이 필요하다.", code:`val = request.args.get("v")\nresp = make_response("ok")\nresp.headers["X-Data"] = val\nreturn resp` },
  { c:"입력검증", q:"2차(Stored) SQL 삽입에 대한 설명으로 옳은 것은?", o:["입력이 즉시 쿼리에 반영되어 발생","DB에 저장된 데이터가 이후 동적 쿼리에 사용될 때 발생","HTTP 헤더로만 발생","항상 GET 요청으로만 발생"], a:1, e:"2차 SQL 삽입은 먼저 저장된 데이터가 나중에 검증 없이 동적 쿼리에 사용될 때 발생한다. 저장 시점뿐 아니라 사용 시점에도 매개변수화가 필요하다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은?", o:["코드 삽입(역직렬화)","SQL 삽입","XSS","CSRF"], a:0, e:"신뢰되지 않은 데이터를 ObjectInputStream으로 역직렬화하면 가젯 체인을 통한 원격 코드 실행이 가능하다. 역직렬화 대상 클래스 화이트리스트 또는 안전한 포맷(JSON 등) 사용이 필요하다.", code:`ObjectInputStream ois = new ObjectInputStream(request.getInputStream());\nObject obj = ois.readObject();` },
  { c:"입력검증", q:"신뢰되지 않은 데이터의 역직렬화 위험을 줄이는 방법으로 가장 적절한 것은?", o:["역직렬화 후 로그 남기기","허용 클래스 화이트리스트(ObjectInputFilter) 적용 또는 데이터 포맷 사용","객체를 암호화","스트림 크기 제한만 적용"], a:1, e:"Java의 ObjectInputFilter(또는 LookAhead) 등으로 역직렬화 허용 클래스를 화이트리스트화하거나, 객체 직렬화 대신 JSON 같은 데이터 전용 포맷을 사용해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["코드 삽입(안전하지 않은 역직렬화)","경로 조작","SQL 삽입","XSS"], a:0, e:"pickle.loads는 신뢰되지 않은 데이터에 대해 임의 코드 실행이 가능하다. 신뢰되지 않은 입력에는 json 등 안전한 포맷을 사용해야 한다.", code:`data = request.get_data()\nobj = pickle.loads(data)` },
  { c:"입력검증", q:"다음 Python(YAML) 코드의 보안약점과 대책은?", o:["yaml.load는 임의 객체 생성 가능 - yaml.safe_load 사용","안전함","SQL 삽입 - 바인딩 사용","XXE - DTD 비활성화"], a:0, e:"yaml.load(Loader 미지정)는 임의 파이썬 객체를 생성해 코드 실행으로 이어질 수 있다. 신뢰되지 않은 입력에는 yaml.safe_load를 사용해야 한다.", code:`cfg = yaml.load(request.get_data())` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (자원 삽입)", o:["경로 조작 및 자원 삽입","XSS","SQL 삽입","CSRF"], a:0, e:"사용자 입력으로 포트/호스트 같은 시스템 자원 식별자를 결정하면 의도하지 않은 자원에 연결되는 자원 삽입에 취약하다. 허용 값으로 제한해야 한다.", code:`int port = Integer.parseInt(request.getParameter("port"));\nSocket s = new Socket("backend", port);` },
  { c:"입력검증", q:"NoSQL(MongoDB) 삽입을 방지하기 위한 방법으로 옳은 것은?", o:["사용자 입력이 쿼리 연산자($gt, $ne 등) 객체로 해석되지 않도록 타입/구조 검증","쿼리 결과를 캐싱","인덱스 추가","읽기 전용 계정 사용"], a:0, e:"JSON 입력이 그대로 쿼리 객체가 되면 $ne, $gt 등의 연산자 주입이 가능하다. 입력 타입을 강제(문자열만 허용)하고 연산자 키를 거부해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Python(Flask) 코드의 보안약점은?", o:["서버측 템플릿 삽입(SSTI)","경로 조작","SSRF","정수 오버플로우"], a:0, e:"사용자 입력을 템플릿 문법으로 평가하면 {{7*7}} 같은 표현식이 실행되는 SSTI로, RCE까지 이어질 수 있다. 사용자 입력은 데이터로만 전달하고 고정 템플릿을 써야 한다.", code:`tpl = "Hello %s" % request.args.get("name")\nreturn render_template_string(tpl)` },
  { c:"입력검증", q:"입력 데이터 정규화(Canonicalization)를 검증 전에 수행해야 하는 이유는?", o:["성능 향상을 위해","인코딩/표현 차이를 통일한 뒤 검증해야 우회를 막기 때문","로그 용량을 줄이려고","DB 부하를 줄이려고"], a:1, e:"같은 입력도 URL 인코딩, 유니코드, '..//' 등 여러 표현이 가능하므로, 정규화로 표준형으로 만든 뒤 검증해야 인코딩 우회를 차단할 수 있다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 SQL 삽입 위험에 대한 설명으로 옳은 것은?", o:["LIKE 절에 입력을 연결해 여전히 삽입 위험이 있고, 와일드카드 처리도 필요","안전함","XSS 위험","경로 조작 위험"], a:0, e:"PreparedStatement를 쓰더라도 LIKE 패턴 문자열을 직접 연결하면 삽입 위험이 남고, %와 _ 같은 와일드카드도 이스케이프해야 의도된 검색이 된다. 바인딩 파라미터로 패턴을 전달해야 한다.", code:`String kw = request.getParameter("kw");\nString sql = "SELECT * FROM goods WHERE name LIKE '%" + kw + "%'";` },
  { c:"입력검증", q:"다음 중 'CRLF 주입'이 직접적으로 유발할 수 있는 약점은?", o:["SQL 삽입","HTTP 응답분할 및 로그 위조","정수 오버플로우","버퍼 오버플로우"], a:1, e:"CR/LF(\\r\\n) 주입은 HTTP 헤더 경계를 만들어 응답분할을 일으키거나, 로그에 가짜 줄을 삽입해 로그 위조를 유발한다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["경로 조작","코드 삽입","XSS","정수 오버플로우"], a:1, e:"__import__와 getattr을 사용자 입력으로 호출하면 임의 모듈/함수 실행이 가능한 코드 삽입에 해당한다. 허용된 동작만 매핑하는 디스패치 테이블을 사용해야 한다.", code:`mod = request.args["m"]\nfunc = request.args["f"]\ngetattr(__import__(mod), func)()` },
  { c:"입력검증", q:"XSS 출력 인코딩에서 'HTML 속성 컨텍스트'와 'JavaScript 컨텍스트'를 구분해야 하는 이유는?", o:["인코딩이 불필요하기 때문","컨텍스트마다 위험 문자와 이스케이프 규칙이 달라 한 가지 인코딩으로는 충분하지 않기 때문","속성 컨텍스트는 항상 안전하기 때문","JS 컨텍스트는 항상 안전하기 때문"], a:1, e:"HTML 본문, 속성, JS, URL, CSS 컨텍스트는 각각 위험 문자와 이스케이프 규칙이 다르다. 출력 위치에 맞는 인코딩을 적용해야 XSS를 막을 수 있다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드는 XSS에 안전한가?", o:["안전하다. HtmlUtils로 HTML 이스케이프하여 출력","위험하다. 인코딩이 없음","위험하다. 입력 길이 제한이 없음","위험하다. UTF-8 설정이 없음"], a:0, e:"출력 전에 HTML 엔티티 이스케이프를 적용하면 <, >, & 등이 무해한 텍스트로 표시되어 본문 컨텍스트 XSS가 방지된다.", code:`String safe = org.springframework.web.util.HtmlUtils.htmlEscape(name);\nout.println("<div>" + safe + "</div>");` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (Expression Language 주입)", o:["EL/OGNL 표현식 삽입","SQL 삽입","경로 조작","CSRF"], a:0, e:"사용자 입력을 표현식 평가기(EL/OGNL/SpEL)에 전달하면 표현식이 실행되어 RCE로 이어질 수 있다. 입력을 표현식으로 평가하지 말아야 한다.", code:`ExpressionParser parser = new SpelExpressionParser();\nObject v = parser.parseExpression(request.getParameter("e")).getValue();` },
  { c:"입력검증", q:"다음 중 SSRF 방어에서 'DNS 리바인딩' 우회를 고려할 때 추가로 필요한 조치는?", o:["요청 전 1회만 도메인 검증","연결 직전 해석된 실제 IP를 재검증하고 사설/링크로컬 대역 차단","User-Agent 변경","HTTPS 강제"], a:1, e:"검증 시점과 연결 시점의 DNS 응답이 달라질 수 있으므로(DNS 리바인딩), 실제 소켓 연결 직전 해석된 IP를 다시 검사해 내부망 대역 접근을 차단해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은?", o:["경로 조작","SQL 삽입","XSS","SSRF"], a:0, e:"send_file에 사용자 입력 경로를 그대로 사용하면 '../'로 임의 파일을 다운로드할 수 있다. safe_join/secure_filename으로 기준 경로 하위만 허용해야 한다.", code:`fname = request.args.get("name")\nreturn send_file("/data/" + fname)` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (정수 오버플로우 / 음수)", o:["배열 인덱스에 검증되지 않은 정수 사용으로 인한 범위 초과","XSS","SQL 삽입","경로 조작"], a:0, e:"사용자가 음수나 큰 인덱스를 넣으면 배열 범위를 벗어나 ArrayIndexOutOfBounds 또는 의도치 않은 데이터 접근이 발생한다. 인덱스 범위(0 이상, length 미만)를 검증해야 한다.", code:`int idx = Integer.parseInt(request.getParameter("i"));\nreturn items[idx];` },
  { c:"입력검증", q:"파일 업로드에서 'Content-Type(MIME) 헤더만 검사'하는 것이 불충분한 이유는?", o:["MIME 검사는 느려서","클라이언트가 MIME을 위조할 수 있어 실제 파일 내용과 다를 수 있기 때문","MIME은 표준이 아니라서","MIME 검사는 서버 부하가 커서"], a:1, e:"Content-Type은 클라이언트가 설정하므로 위조 가능하다. 확장자 화이트리스트와 실제 파일 시그니처(매직 넘버)/콘텐츠 검증을 함께 해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Java JdbcTemplate 코드의 SQL 삽입 안전성은?", o:["안전하다. ? 플레이스홀더와 인자 배열로 바인딩","위험하다. queryForList가 문제","위험하다. 결과 타입이 문제","위험하다. 트랜잭션이 없음"], a:0, e:"JdbcTemplate에서 ? 플레이스홀더와 인자 배열을 사용하면 내부적으로 PreparedStatement 바인딩이 이뤄져 SQL 삽입에 안전하다.", code:`jdbcTemplate.queryForList(\n  "SELECT * FROM users WHERE name = ?", new Object[]{ name });` },
  { c:"입력검증", q:"다음 중 XSS 방어를 보조하는 HTTP 보안 헤더로 옳은 것은?", o:["Content-Security-Policy","X-Powered-By","Cache-Control: no-store","Accept-Encoding"], a:0, e:"Content-Security-Policy(CSP)는 실행 가능한 스크립트 출처를 제한해 XSS의 영향(인라인/외부 스크립트 실행)을 완화하는 보조 방어책이다.", code:`` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은? (운영체제 명령 - shlex 미사용)", o:["OS 명령어 삽입","경로 조작","SQL 삽입","XXE"], a:0, e:"shell=True와 문자열 포매팅을 함께 사용하면 사용자 입력의 셸 메타문자가 해석되어 명령어 삽입이 발생한다. shell=False와 리스트 인자, 입력 검증이 필요하다.", code:`cmd = "tar czf backup.tgz %s" % request.args["dir"]\nsubprocess.call(cmd, shell=True)` },
  { c:"입력검증", q:"입력 검증에서 '신뢰 경계(trust boundary)'를 넘는 데이터의 처리 원칙으로 옳은 것은?", o:["내부 데이터로 간주해 검증 생략","경계를 넘어 들어오는 모든 데이터를 신뢰하지 않고 검증/정규화/인코딩","암호화만 하면 검증 불필요","길이 제한만 적용"], a:1, e:"신뢰 경계를 넘는(외부에서 들어오는) 데이터는 신뢰되지 않은 것으로 간주하고, 사용 지점의 컨텍스트에 맞춰 검증/정규화/인코딩을 수행해야 한다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (StringBuilder로 만든 동적 쿼리)", o:["SQL 삽입","XSS","경로 조작","정수 오버플로우"], a:0, e:"StringBuilder를 사용해도 입력을 쿼리 문자열에 연결하는 것은 동일하게 SQL 삽입에 취약하다. 매개변수화된 쿼리를 사용해야 한다.", code:`StringBuilder sb = new StringBuilder("SELECT * FROM t WHERE c='");\nsb.append(request.getParameter("c")).append("'");\nstmt.executeQuery(sb.toString());` },
  { c:"입력검증", q:"다음 중 '위험한 형식 파일 업로드' 약점이 RCE로 이어지는 전형적 조건은?", o:["업로드 파일이 실행 가능한 디렉터리에 저장되고 서버가 해석 실행할 때","파일 크기가 클 때","파일명이 한글일 때","업로드가 HTTPS일 때"], a:0, e:"악성 스크립트 파일이 웹 서버가 실행하는 경로에 저장되어 URL로 호출되면 서버측 코드가 실행되어 RCE가 된다. 실행 불가 경로 저장과 콘텐츠 검증이 필요하다.", code:`` },
  { c:"입력검증", q:"LDAP 삽입과 SQL 삽입의 공통적인 근본 원인으로 옳은 것은?", o:["신뢰되지 않은 입력이 질의/필터 구문으로 해석되도록 결합되기 때문","둘 다 HTTP에서만 발생하기 때문","둘 다 정수 처리 문제 때문","둘 다 파일 시스템 접근 때문"], a:0, e:"두 약점 모두 사용자 입력을 질의(쿼리/필터) 구문에 그대로 결합해 데이터가 구문으로 해석되는 것이 원인이다. 입력과 구문 분리(바인딩/이스케이프)가 공통 해법이다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (sendRedirect에 헤더 분리)", o:["오픈 리다이렉트 + CRLF로 인한 응답분할 가능","SQL 삽입","XXE","버퍼 오버플로우"], a:0, e:"사용자 입력 url을 검증 없이 리다이렉트하면 오픈 리다이렉트이고, 입력에 CR/LF가 포함되면 헤더 분리로 응답분할까지 가능하다. 화이트리스트와 개행 제거가 필요하다.", code:`String url = request.getParameter("url");\nresponse.setHeader("Location", url);\nresponse.setStatus(302);` },
  { c:"입력검증", q:"다음 Python 코드의 안전성 평가로 옳은 것은? (정규식 검증)", o:["부분 일치 위험: re.match는 시작만 검사하므로 fullmatch나 ^...$ 앵커 필요","완전히 안전함","SQL 삽입 위험","경로 조작 위험"], a:0, e:"re.match는 문자열 시작부터 일치만 확인하고 끝은 보장하지 않아 'abc\\n악성' 같은 입력이 통과할 수 있다. re.fullmatch 또는 ^...$ 앵커(re.DOTALL 주의)로 전체 일치를 검증해야 한다.", code:`if re.match(r"[a-z0-9]+", user_id):\n    proceed(user_id)` },
  { c:"입력검증", q:"다음 중 '정규식 서비스 거부(ReDoS)'를 유발할 수 있는 패턴 특징은?", o:["고정 길이 문자열 매칭","중첩 수량자 등으로 인한 폭발적 백트래킹","앵커 사용","문자 클래스 사용"], a:1, e:"(a+)+ 같은 중첩 수량자 패턴은 특정 입력에서 백트래킹이 지수적으로 증가해 CPU를 소모하는 ReDoS를 유발할 수 있다. 패턴 단순화/입력 길이 제한이 필요하다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (XSLT/XPath)", o:["XPath 삽입","SQL 삽입","경로 조작","XSS"], a:0, e:"사용자 입력을 XPath 식에 직접 연결하면 ' or '1'='1 같은 조작으로 인증 우회/데이터 노출이 가능한 XPath 삽입에 취약하다. 변수 바인딩 또는 이스케이프가 필요하다.", code:`String expr = "/users/user[name='" + name + "' and pw='" + pw + "']";\nNodeList n = (NodeList) xpath.evaluate(expr, doc, NODESET);` },
  { c:"입력검증", q:"다음 Python 코드의 보안약점은? (tarfile 압축 해제)", o:["경로 조작(Zip Slip/Tar Slip)","SQL 삽입","XSS","SSRF"], a:0, e:"신뢰되지 않은 아카이브를 extractall로 풀면 '../'를 포함한 엔트리가 압축 해제 디렉터리 밖에 파일을 쓰는 경로 조작(Tar Slip)이 가능하다. 각 엔트리 경로가 대상 디렉터리 내부인지 검증해야 한다.", code:`tar = tarfile.open(uploaded)\ntar.extractall("/tmp/out")` },
  { c:"입력검증", q:"다음 중 입력값에 대한 '음수/경계값' 검증이 가장 중요한 보안약점은?", o:["XSS","정수 오버플로우 및 부적절한 범위 사용","CSRF","오픈 리다이렉트"], a:1, e:"길이/수량/금액/인덱스 같은 수치 입력은 음수, 0, 최대값 경계에서 오버플로우나 범위 초과를 일으킬 수 있어 경계값 검증이 핵심이다.", code:`` },
  { c:"입력검증", q:"다음 Java 코드의 보안약점은? (Header에 사용자 입력)", o:["HTTP 응답분할(헤더 주입)","SQL 삽입","XXE","CSRF"], a:0, e:"쿠키 값에 사용자 입력을 검증 없이 넣으면 CR/LF로 헤더를 분리해 응답분할/세션 관련 헤더 주입이 가능하다. 개행문자를 제거/거부해야 한다.", code:`Cookie c = new Cookie("pref", request.getParameter("pref"));\nresponse.addCookie(c);` },
  { c:"입력검증", q:"매개변수화된 쿼리를 사용해도 SQL 삽입이 남을 수 있는 경우는?", o:["바인딩 파라미터로 모든 값을 처리할 때","ORDER BY 컬럼, 테이블명 등 식별자를 문자열로 연결할 때","결과를 페이징할 때","트랜잭션을 사용할 때"], a:1, e:"바인딩은 값에만 적용되고 식별자(테이블/컬럼/정렬 컬럼)는 바인딩할 수 없다. 식별자를 입력으로 연결하면 삽입 위험이 남으므로 화이트리스트 매핑이 필요하다.", code:`` }
);
window.__QBANK.THEORY.push(
  { type:"OX", cat:"입력검증", q:"PreparedStatement를 사용하면 쿼리에 들어가는 모든 값(테이블명 포함)이 자동으로 SQL 삽입으로부터 안전해진다.", a:false, e:"바인딩 파라미터는 값에만 적용되며 테이블명/컬럼명 같은 식별자는 바인딩할 수 없다. 식별자는 화이트리스트로 검증해야 한다." },
  { type:"OX", cat:"입력검증", q:"입력값 검증은 클라이언트(자바스크립트)에서만 수행해도 보안상 충분하다.", a:false, e:"클라이언트 검증은 우회 가능하므로 보안 목적의 검증은 반드시 서버측에서 수행해야 한다." },
  { type:"OX", cat:"입력검증", q:"화이트리스트 기반 입력 검증은 블랙리스트 기반보다 미지의 공격 패턴 차단에 유리하다.", a:true, e:"화이트리스트는 허용된 형태만 통과시키므로 알려지지 않은 변형 공격까지 기본적으로 차단된다." },
  { type:"OX", cat:"입력검증", q:"XSS는 입력 시점의 필터링만으로 모든 컨텍스트에서 완전히 방지된다.", a:false, e:"XSS는 출력되는 컨텍스트(HTML/속성/JS/URL)마다 인코딩 규칙이 달라, 출력 컨텍스트에 맞는 인코딩이 핵심 대책이다." },
  { type:"OX", cat:"입력검증", q:"Java의 ProcessBuilder에 명령과 인자를 개별 요소로 분리해 전달하면 셸을 거치지 않아 OS 명령어 삽입을 방지하는 데 효과적이다.", a:true, e:"인자를 분리해 직접 실행하면 셸 메타문자가 해석되지 않으므로 명령어 삽입을 방지할 수 있다." },
  { type:"OX", cat:"입력검증", q:"파일 업로드 시 Content-Type 헤더만 검사하면 위험한 형식의 파일 업로드를 충분히 막을 수 있다.", a:false, e:"Content-Type은 클라이언트가 위조할 수 있으므로 확장자 화이트리스트와 실제 콘텐츠(시그니처) 검증을 함께 해야 한다." },
  { type:"OX", cat:"입력검증", q:"HTTP 응답분할은 사용자 입력에 포함된 CR/LF 문자가 응답 헤더에 반영될 때 발생할 수 있다.", a:true, e:"CR(\\r)/LF(\\n)이 헤더 경계를 만들어 응답을 분할하므로, 헤더에 들어가는 값에서 개행문자를 제거/거부해야 한다." },
  { type:"OX", cat:"입력검증", q:"Python에서 신뢰되지 않은 데이터를 pickle.loads로 역직렬화하는 것은 안전하다.", a:false, e:"pickle.loads는 임의 코드 실행이 가능하므로 신뢰되지 않은 데이터에는 사용하면 안 되고 json 등 안전한 포맷을 써야 한다." },
  { type:"OX", cat:"입력검증", q:"XXE를 방지하려면 XML 파서에서 외부 엔티티 및 DTD 처리를 비활성화해야 한다.", a:true, e:"외부 엔티티/DTD를 비활성화(disallow-doctype-decl, resolve_entities=False 등)하면 외부 엔티티를 통한 파일 노출/SSRF/DoS를 막는다." },
  { type:"OX", cat:"입력검증", q:"가격이나 관리자 권한 같은 보안 결정은 클라이언트가 보낸 hidden 필드 값으로 판단해도 안전하다.", a:false, e:"클라이언트가 보낸 값은 변조 가능하므로, 보안 결정은 서버측 세션/DB의 신뢰된 데이터로 수행해야 한다." },
  { type:"SHORT", cat:"입력검증", q:"사용자 입력을 SQL 쿼리에 안전하게 바인딩하기 위해 Java에서 사용하는, 쿼리를 미리 컴파일하는 객체의 이름은?", a:"PreparedStatement", answers:["프리페어드스테이트먼트","prepared statement","매개변수화된 쿼리","파라미터화 쿼리"], e:"PreparedStatement는 쿼리 구조를 선컴파일하고 ? 위치에 값을 바인딩하여 입력이 데이터로만 처리되게 함으로써 SQL 삽입을 방지한다." },
  { type:"SHORT", cat:"입력검증", q:"'../' 같은 시퀀스로 의도하지 않은 디렉터리의 파일에 접근하는 입력검증 약점의 이름은? (한글 또는 영문)", a:"경로 조작", answers:["경로 조작 및 자원 삽입","Path Traversal","패스 트래버설","디렉터리 트래버설","Directory Traversal"], e:"경로 조작(Path Traversal)은 입력에 포함된 '..' 등으로 기준 디렉터리를 벗어난 파일에 접근하는 약점이다." },
  { type:"SHORT", cat:"입력검증", q:"사용자가 제어하는 URL로 서버가 직접 요청을 보내게 만들어 내부망 자원에 접근하는 약점의 영문 약어는?", a:"SSRF", answers:["Server-Side Request Forgery","서버측 요청 위조"], e:"SSRF(Server-Side Request Forgery)는 서버가 공격자 지정 URL로 요청을 보내 내부망/메타데이터 자원에 접근하게 되는 약점이다." },
  { type:"SHORT", cat:"입력검증", q:"신뢰되지 않은 데이터가 동적 웹 페이지에 인코딩 없이 출력되어 스크립트가 실행되는 약점의 영문 약어는?", a:"XSS", answers:["Cross-Site Scripting","크로스 사이트 스크립팅","크로스사이트스크립트"], e:"XSS는 신뢰되지 않은 입력이 인코딩 없이 출력되어 사용자 브라우저에서 스크립트가 실행되는 약점이다." },
  { type:"SHORT", cat:"입력검증", q:"Python에서 신뢰되지 않은 입력으로 산술식 등을 평가할 때 eval 대신 안전하게 리터럴만 평가하는 함수는?", a:"ast.literal_eval", answers:["literal_eval","ast.literal_eval()"], e:"ast.literal_eval은 숫자/문자열/튜플 등 리터럴만 평가하여 임의 코드 실행을 막는 eval의 안전한 대안이다." },
  { type:"SHORT", cat:"입력검증", q:"Python에서 OS 명령 실행 시 명령어 삽입을 피하려면 subprocess에 인자를 어떤 형태로 전달하고 shell 옵션을 어떻게 설정해야 하는가? (예: 리스트, shell=False)", a:"리스트, shell=False", answers:["list shell=False","shell=False 리스트","리스트 인자 shell=False"], e:"명령과 인자를 리스트로 전달하고 shell=False(기본값)로 실행하면 셸 메타문자가 해석되지 않아 명령어 삽입을 방지한다." },
  { type:"SHORT", cat:"입력검증", q:"HTTP 응답분할/헤더 주입을 유발하는, 입력에서 반드시 제거/거부해야 하는 두 제어문자를 통칭하는 약어는?", a:"CRLF", answers:["CR/LF","CR LF","개행문자","\\r\\n"], e:"CR(\\r)과 LF(\\n)이 헤더 경계를 만들어 응답분할을 일으키므로 헤더 값에서 제거하거나 거부해야 한다." },
  { type:"SHORT", cat:"입력검증", q:"lxml에서 XXE를 방지하기 위해 XMLParser 생성 시 외부 엔티티 해석을 끄는 인자(키=값 형태)는?", a:"resolve_entities=False", answers:["resolve_entities = False","resolve_entities False"], e:"etree.XMLParser(resolve_entities=False)는 외부 엔티티 해석을 비활성화하여 XXE를 막는다. no_network=True와 함께 쓰면 더 안전하다." },
  { type:"SHORT", cat:"입력검증", q:"printf 계열 함수의 포맷 문자열 자리에 사용자 입력을 직접 넣을 때 발생하는, '%n','%x'를 악용하는 약점의 이름은?", a:"포맷 스트링 삽입", answers:["Format String","포맷스트링","포맷 스트링","format string injection"], e:"포맷 스트링 삽입은 사용자 입력이 포맷 문자열로 해석되어 메모리 읽기/쓰기가 가능한 약점으로, printf(\"%s\", input)처럼 고정 포맷을 써야 한다." },
  { type:"SHORT", cat:"입력검증", q:"인증된 사용자의 세션을 악용해 사용자 모르게 위조된 상태변경 요청을 전송하는 약점의 영문 약어는?", a:"CSRF", answers:["Cross-Site Request Forgery","크로스 사이트 요청 위조","사이트 간 요청 위조"], e:"CSRF는 토큰 검증/ SameSite 쿠키로 방어하며, 사용자의 인증 세션을 악용한 위조 요청을 서버가 처리하게 만드는 약점이다." },
  { type:"SHORT", cat:"입력검증", q:"정수 연산 결과가 자료형의 표현 범위를 초과해 값이 래핑(wrap-around)되는 입력검증 관련 약점의 이름은?", a:"정수 오버플로우", answers:["정수형 오버플로우","Integer Overflow","integer overflow"], e:"정수 오버플로우는 곱셈/덧셈 결과가 자료형 범위를 넘어 잘못된(작은/음수) 값이 되어 버퍼 크기 계산 오류 등 메모리 문제로 이어질 수 있다." },
  { type:"SHORT", cat:"입력검증", q:"여러 인코딩/표현으로 동일한 입력을 표준 형태로 변환한 뒤 검증해야 우회를 막을 수 있는데, 이 표준화 과정을 무엇이라 하는가?", a:"정규화", answers:["Canonicalization","Normalization","캐노니컬라이제이션","표준화"], e:"정규화(Canonicalization)는 URL 인코딩/유니코드/경로 표현 차이를 표준형으로 통일하는 것으로, 검증은 정규화 후에 수행해야 우회를 막는다." },
  { type:"MC", cat:"입력검증", q:"다음 중 SQL 삽입의 근본적 대책으로 가장 적절한 것은?", o:["입력값에서 작은따옴표 치환","매개변수화된 쿼리(바인딩) 사용","쿼리 결과 캐싱","DB 포트 변경"], a:1, e:"매개변수화된 쿼리는 입력을 데이터로만 처리해 SQL 삽입을 근본적으로 막는다. 문자 치환 같은 블랙리스트는 우회 가능하다." },
  { type:"MC", cat:"입력검증", q:"다음 중 OS 명령어 삽입을 가장 효과적으로 방지하는 방법은?", o:["셸을 통해 입력을 그대로 실행","명령/인자 분리 실행(배열, shell=False)과 입력 화이트리스트","입력 길이만 제한","명령 실행 결과 인코딩"], a:1, e:"셸을 거치지 않고 명령/인자를 분리 실행하면 메타문자가 해석되지 않으며, 입력 화이트리스트로 의미까지 검증해야 한다." },
  { type:"MC", cat:"입력검증", q:"다음 중 XXE 공격으로 직접 발생할 수 있는 결과가 아닌 것은?", o:["로컬 파일 노출","내부망 요청(SSRF)","서비스 거부(DoS)","정수 오버플로우"], a:3, e:"XXE는 외부 엔티티를 통해 파일 노출, SSRF, DoS를 유발한다. 정수 오버플로우는 수치 연산 약점으로 XXE와 무관하다." },
  { type:"MC", cat:"입력검증", q:"다음 중 오픈 리다이렉트(신뢰되지 않은 URL 자동접속) 방어로 가장 적절한 것은?", o:["리다이렉트 대상 도메인 화이트리스트 검증","리다이렉트 URL을 Base64 인코딩","새 탭으로 열기","리다이렉트 횟수 제한"], a:0, e:"리다이렉트 대상이 허용된 내부 경로/도메인인지 검증해야 외부 피싱 사이트로의 유도를 막을 수 있다." },
  { type:"MC", cat:"입력검증", q:"LDAP 검색 필터에서 삽입 방지를 위해 이스케이프해야 하는 문자로 옳은 것은?", o:["( ) * \\","; -- #","< > &","' \" `"], a:0, e:"LDAP 필터에서 '(' ')' '*' '\\' 등은 특수 의미를 가지므로 이스케이프해야 LDAP 삽입을 막는다." },
  { type:"MC", cat:"입력검증", q:"다음 중 '메모리 버퍼 오버플로우'를 완화하는 운영체제/컴파일러 기법이 아닌 것은?", o:["ASLR(주소 공간 배치 무작위화)","DEP/NX(실행 방지)","스택 카나리","SQL 바인딩"], a:3, e:"SQL 바인딩은 SQL 삽입 대책이다. ASLR, DEP/NX, 스택 카나리가 버퍼 오버플로우 완화 기법이다." },
  { type:"MC", cat:"입력검증", q:"다음 중 신뢰되지 않은 역직렬화 위험을 줄이는 방법으로 가장 적절한 것은?", o:["허용 클래스 화이트리스트(필터) 또는 데이터 포맷(JSON) 사용","스트림 압축","객체 캐싱","역직렬화 결과 로깅"], a:0, e:"역직렬화 허용 클래스를 화이트리스트로 제한(ObjectInputFilter)하거나 객체 직렬화 대신 데이터 전용 포맷을 사용해야 RCE 가젯 체인을 막는다." },
  { type:"MC", cat:"입력검증", q:"다음 중 입력검증 관점에서 '보안기능 결정에 사용되는 부적절한 입력값' 약점의 핵심 원인은?", o:["권한/가격 등 보안 결정을 변조 가능한 클라이언트 입력에 의존","로그 미흡","암호화 미적용","세션 타임아웃 과다"], a:0, e:"보안에 영향을 주는 결정을 hidden 필드/파라미터/쿠키 등 변조 가능한 입력으로 내리는 것이 원인으로, 서버측 신뢰 데이터로 결정해야 한다." }
);

// ===== partB =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  { c:"보안기능", q:"다음 중 '적절한 인증 없이 중요기능 허용' 약점(CWE-306)에 해당하는 상황으로 가장 적절한 것은?", o:["관리자 페이지 접근 시 세션 인증을 검사한다","계좌 이체 API가 로그인 여부를 확인하지 않고 호출 가능하다","비밀번호를 bcrypt로 해시한다","TLS로 통신 구간을 암호화한다"], a:1, e:"중요기능(이체, 관리자 기능 등)을 인증 검사 없이 호출할 수 있으면 CWE-306(Missing Authentication for Critical Function)에 해당한다." },
  { c:"보안기능", q:"취약한 암호화 알고리즘 약점을 제거하기 위해 대칭키 암호로 대체할 때 가장 권장되는 알고리즘은?", o:["DES","3DES","RC4","AES"], a:3, e:"DES/3DES/RC4는 취약하거나 권장되지 않는다. 대칭키는 AES(국내는 SEED, ARIA 포함)를 권장한다." },
  { c:"보안기능", q:"메시지 무결성/비밀번호 저장에 더 이상 사용하지 말아야 하는 해시 알고리즘으로 묶인 것은?", o:["SHA-256, SHA-512","SHA-3, BLAKE2","MD5, SHA-1","HMAC-SHA256, PBKDF2"], a:2, e:"MD5와 SHA-1은 충돌 공격이 가능해 취약하다. SHA-256 이상 또는 SHA-3 계열을 사용해야 한다." },
  { c:"보안기능", q:"블록 암호 운용모드 중 동일 평문 블록이 동일 암호문 블록으로 나타나 패턴이 노출되는 취약한 모드는?", o:["ECB","CBC","CTR","GCM"], a:0, e:"ECB 모드는 동일 평문 블록이 동일 암호문이 되어 데이터 패턴이 드러난다. 무결성/기밀성을 위해 GCM 등 인증 암호 모드를 권장한다." },
  { c:"보안기능", q:"RSA 알고리즘 사용 시 안전성을 위해 권장되는 최소 키 길이는?", o:["512비트","1024비트","2048비트","128비트"], a:2, e:"RSA는 최소 2048비트 이상을 권장한다. 1024비트 이하는 안전하지 않다." },
  { c:"보안기능", q:"AES 대칭키 암호에서 사용 가능한 키 길이가 아닌 것은?", o:["128비트","192비트","256비트","512비트"], a:3, e:"AES는 128, 192, 256비트 키만 지원한다. 최소 128비트 이상을 권장한다." },
  { c:"보안기능", q:"타원곡선 암호(ECC)에서 RSA-3072(128비트 보안강도)와 동등한 강도를 제공하는 키 길이는?", o:["112비트","160비트","256비트","2048비트"], a:2, e:"NIST SP 800-57 기준 ECC 256비트(P-256)는 128비트 보안강도로 RSA-3072와 동등하다. 참고로 RSA-2048은 112비트 강도로 ECC 224비트(P-224)에 대응한다." },
  { c:"보안기능", q:"Java에서 보안에 부적합하여 예측 가능한 난수를 생성하는 클래스는?", o:["java.security.SecureRandom","java.util.Random","javax.crypto.KeyGenerator","java.security.MessageDigest"], a:1, e:"java.util.Random은 선형 합동 방식으로 예측 가능하다. 보안 목적의 난수는 SecureRandom을 사용해야 한다." },
  { c:"보안기능", q:"Python에서 토큰/세션ID 등 보안용 난수를 생성할 때 권장되는 모듈은?", o:["random","secrets","time","os.urandom를 직접 가공한 random.seed"], a:1, e:"Python 표준 random은 예측 가능하다. 보안 난수는 secrets 모듈(내부적으로 os.urandom 사용)을 권장한다." },
  { c:"보안기능", q:"JWT 토큰에서 'alg: none'을 허용하면 발생하는 보안 문제는?", o:["토큰 크기가 커진다","서명 검증을 우회해 토큰을 위조할 수 있다","토큰 만료가 빨라진다","Base64 인코딩이 깨진다"], a:1, e:"alg=none은 서명 검증을 비활성화하므로 공격자가 임의의 토큰을 위조할 수 있다. 허용 알고리즘을 화이트리스트로 고정해야 한다." },
  { c:"보안기능", q:"비밀번호를 안전하게 저장하기 위한 가장 권장되는 방식은?", o:["MD5 단순 해시","SHA-1 단순 해시","평문 저장 후 DB 암호화","솔트를 적용한 bcrypt/Argon2/PBKDF2"], a:3, e:"솔트와 반복(work factor)을 적용한 bcrypt, Argon2, PBKDF2 같은 비밀번호 전용 해시를 사용해야 한다." },
  { c:"보안기능", q:"'솔트 없는 일방향 해시 저장' 약점(CWE-759)의 핵심 위험은?", o:["해시 계산이 느려진다","동일 비밀번호가 동일 해시가 되어 레인보우 테이블 공격에 취약하다","해시 충돌이 절대 발생하지 않는다","암호문 길이가 짧아진다"], a:1, e:"솔트가 없으면 같은 비밀번호가 같은 해시가 되어 사전 계산된 레인보우 테이블로 쉽게 복원된다." },
  { c:"보안기능", q:"민감정보를 담은 쿠키에 반드시 설정해야 하는 보안 속성 조합은?", o:["Secure, HttpOnly","Path, Domain","Max-Age, Expires","Version, Comment"], a:0, e:"Secure는 HTTPS 전송만 허용, HttpOnly는 JS 접근을 차단해 XSS로 인한 탈취를 막는다. SameSite도 함께 권장된다." },
  { c:"보안기능", q:"HTTPS 통신 시 서버 인증서 검증을 비활성화(verify=False)하면 발생하는 위험은?", o:["성능 저하만 발생","중간자(MITM) 공격에 노출","압축률 저하","쿠키 손실"], a:1, e:"인증서 검증을 끄면 위조 인증서를 가진 중간자 공격자에게 통신이 노출된다. 검증을 항상 활성화해야 한다." },
  { c:"보안기능", q:"소스코드 주석에 다음과 같이 남겨두면 발생하는 약점은? // DB접속: admin / P@ssw0rd!", o:["성능 약점","주석문 내 주요정보 노출(CWE-615)","코드 인젝션","경쟁 조건"], a:1, e:"주석에 계정/비밀번호/내부 URL 등을 남기면 정보가 노출된다(CWE-615). 배포 전 제거해야 한다." },
  { c:"보안기능", q:"하드코드된 중요정보(CWE-798)에 해당하지 않는 것은?", o:["소스에 박힌 API 비밀키","코드에 직접 작성한 DB 비밀번호","환경변수/외부 안전저장소에서 읽는 키","코드 상수로 정의된 암호화 키"], a:2, e:"환경변수나 비밀관리 저장소(Vault, KMS 등)에서 읽으면 하드코드가 아니다. 소스에 직접 박는 것이 약점이다." },
  { c:"보안기능", q:"'부적절한 인가'(CWE-285) 약점에 해당하는 상황은?", o:["로그인은 성공했지만 권한 검사 없이 타인의 자원에 접근 가능","비밀번호를 평문 저장","SQL 인젝션 발생","난수 예측 가능"], a:0, e:"인증(누구인가)은 통과했으나 인가(무엇을 할 수 있는가) 검사를 누락하면 권한 상승/수평적 접근이 가능하다." },
  { c:"보안기능", q:"다음 중 안전하지 않은 비밀번호 정책으로 가장 적절한 것은?", o:["최소 길이/복잡도 미적용으로 '1234' 허용","최소 8자 이상 요구","사전 단어 차단","연속/반복 문자 제한"], a:0, e:"길이/복잡도 정책이 없어 약한 비밀번호를 허용하면 무차별 대입에 취약하다(CWE-521)." },
  { c:"보안기능", q:"반복적인 인증 시도 제한이 없을 때(CWE-307) 가장 직접적으로 가능한 공격은?", o:["XSS","무차별 대입(brute-force) 공격","경로 조작","XML 외부 엔티티"], a:1, e:"로그인 시도 횟수 제한이 없으면 비밀번호를 반복 추측하는 무차별 대입/사전 공격이 가능하다." },
  { c:"보안기능", q:"무결성 검사 없는 코드 다운로드(CWE-494)를 방지하는 가장 적절한 방법은?", o:["HTTP로 빠르게 다운로드","다운로드 파일의 서명/해시를 검증","파일 크기만 확인","다운로드 후 즉시 실행"], a:1, e:"외부 코드/업데이트는 디지털 서명 검증 또는 안전한 해시 비교로 무결성을 확인한 뒤 실행해야 한다." },
  { c:"보안기능", q:"국내 표준 대칭키 블록암호 알고리즘으로 묶인 것은?", o:["SEED, ARIA","RSA, ECC","MD5, SHA-1","DES, RC4"], a:0, e:"SEED와 ARIA는 국내 표준 대칭키 블록암호다. RSA/ECC는 비대칭, MD5/SHA-1은 해시다." },
  { c:"보안기능", q:"국내 전자서명 표준 알고리즘으로 적절한 것은?", o:["KCDSA(또는 EC-KCDSA)","RC4","MD5","DES"], a:0, e:"KCDSA/EC-KCDSA는 국내 전자서명 표준이다. RC4/MD5/DES는 암호화·해시용이거나 취약하다." },
  { c:"보안기능", q:"중요정보(주민번호, 비밀번호 등)를 DB에 평문으로 저장하면 발생하는 약점은?", o:["암호화되지 않은 중요정보(CWE-311)","과도한 권한","경쟁 조건","버퍼 오버플로우"], a:0, e:"저장/전송 중인 중요정보를 암호화하지 않으면 유출 시 그대로 노출된다(CWE-311/312/319)." },
  { c:"보안기능", q:"Java에서 SSL/TLS 검증을 무력화하는 위험한 코드는?", o:["기본 TrustManager 사용","모든 인증서를 신뢰하는 빈 TrustManager 구현","HostnameVerifier로 도메인 검증","TLS 1.3 사용"], a:1, e:"checkServerTrusted를 비워둔 TrustManager는 모든 인증서를 신뢰해 MITM에 노출된다.", code:`// 위험: 모든 인증서 신뢰
TrustManager[] tm = new TrustManager[]{
  new X509TrustManager(){
    public void checkServerTrusted(X509Certificate[] c, String a){}
    public void checkClientTrusted(X509Certificate[] c, String a){}
    public X509Certificate[] getAcceptedIssuers(){ return null; }
  }
};` },
  { c:"보안기능", q:"다음 Python 코드의 보안 문제는?", o:["문법 오류","인증서 검증 비활성화로 MITM 노출","타임아웃 미설정","인코딩 오류"], a:1, e:"verify=False는 TLS 인증서 검증을 끄므로 중간자 공격에 노출된다. 검증을 켜고 신뢰 CA를 사용해야 한다.", code:`import requests
r = requests.get("https://api.example.com/pay", verify=False)` },
  { c:"보안기능", q:"세션 고정(Session Fixation) 공격을 방지하기 위한 가장 적절한 조치는?", o:["로그인 성공 후 세션 ID를 재발급한다","세션 ID를 URL에 노출한다","세션 만료시간을 무한으로 한다","세션 ID를 순차 증가시킨다"], a:0, e:"인증 성공 시 새 세션 ID를 발급(regenerate)하면 공격자가 미리 심어둔 세션 ID가 무효화된다." },
  { c:"보안기능", q:"GCM(Galois/Counter Mode)을 권장하는 가장 큰 이유는?", o:["키 길이를 줄여줘서","암호화와 무결성(인증)을 함께 제공해서","압축을 제공해서","난수가 필요 없어서"], a:1, e:"GCM은 인증 암호 모드(AEAD)로 기밀성과 무결성을 동시에 제공한다. ECB/CBC 대비 변조 탐지가 가능하다." },
  { c:"보안기능", q:"하드코드된 암호화 키의 가장 큰 문제는?", o:["연산 속도가 느려진다","코드를 디컴파일/유출하면 키가 그대로 드러나 모든 데이터가 위험해진다","키 길이가 자동 증가한다","컴파일이 실패한다"], a:1, e:"소스/바이너리에 박힌 키는 디컴파일·저장소 유출로 노출되며, 키 교체도 어렵다. 외부 KMS/환경변수로 관리해야 한다." },
  { c:"보안기능", q:"다음 중 PBKDF2의 안전성을 높이는 핵심 요소가 아닌 것은?", o:["충분히 큰 반복 횟수(iteration)","임의의 솔트","느린 의도적 비용(work factor)","짧은 출력 길이 고정 8바이트"], a:3, e:"출력을 너무 짧게 고정하면 오히려 약해진다. 반복 횟수, 솔트, 충분한 출력 길이가 안전성을 높인다." },
  { c:"보안기능", q:"OAuth/JWT 검증 시 알고리즘 혼동(Algorithm Confusion) 공격을 막는 방법은?", o:["서버가 허용하는 alg를 화이트리스트로 고정","alg 헤더를 클라이언트가 정하게 둔다","HS256과 RS256을 자동 전환","서명 검증을 생략"], a:0, e:"검증 시 토큰의 alg 헤더를 신뢰하지 말고 서버가 기대하는 알고리즘만 허용해야 RS256↔HS256 혼동을 막는다." },
  { c:"보안기능", q:"파일 업로드 후 저장 디렉터리 권한을 '777'로 설정하면 발생하는 약점은?", o:["잘못된 권한 설정(CWE-732)","SQL 인젝션","CSRF","오픈 리다이렉트"], a:0, e:"누구나 읽기/쓰기/실행 가능한 과도한 권한은 부적절한 권한 설정(CWE-732)으로, 최소권한 원칙을 위반한다." },
  { c:"보안기능", q:"다음 중 '취약한 비밀번호 허용'(CWE-521) 방지책으로 부적절한 것은?", o:["최소 길이 강제","복잡도(영문/숫자/특수문자) 요구","유출된 비밀번호 목록 차단","사용자 ID와 동일한 비밀번호 허용"], a:3, e:"ID와 동일하거나 흔한 비밀번호를 허용하면 약점이다. 알려진 유출 목록·사전 단어를 차단해야 한다." },
  { c:"보안기능", q:"전송 구간 암호화에서 더 이상 사용하면 안 되는 프로토콜 버전은?", o:["TLS 1.3","TLS 1.2","SSL 3.0 / TLS 1.0","TLS 1.2 with AEAD"], a:2, e:"SSL 2.0/3.0, TLS 1.0/1.1은 취약해 폐기 대상이다. TLS 1.2 이상(권장 1.3)을 사용해야 한다." },
  { c:"보안기능", q:"다음 Java 코드의 약점은?", o:["충분하지 않은 키 길이","난수 시드 누락","import 오류","스레드 안전성"], a:0, e:"RSA 1024비트는 안전하지 않다. 최소 2048비트 이상으로 생성해야 한다.", code:`KeyPairGenerator kpg = KeyPairGenerator.getInstance("RSA");
kpg.initialize(1024); // 취약: 키 길이 부족
KeyPair kp = kpg.generateKeyPair();` },
  { c:"보안기능", q:"다음 Java 코드의 약점은?", o:["DES(취약한 암호화 알고리즘) 사용","키 누락","패딩 오류","Base64 미사용"], a:0, e:"DES는 56비트 키로 취약하다. AES 등 안전한 알고리즘으로 교체해야 한다.", code:`Cipher c = Cipher.getInstance("DES/ECB/PKCS5Padding");
c.init(Cipher.ENCRYPT_MODE, desKey);` },
  { c:"보안기능", q:"다음 Python 코드의 약점은?", o:["예측 가능한 난수로 토큰 생성","문자열 인코딩 오류","import 누락","과도한 메모리 사용"], a:0, e:"random은 보안용으로 부적합하다. 토큰/세션ID는 secrets.token_hex 등을 사용해야 한다.", code:`import random
token = "".join(random.choice("0123456789abcdef") for _ in range(32))` },
  { c:"보안기능", q:"다음 Python 코드의 약점은?", o:["MD5로 비밀번호 저장","SQL 문자열 결합","파일 경로 조작","XML 파싱"], a:0, e:"MD5는 빠르고 취약해 비밀번호 저장에 부적합하다. 솔트 적용 bcrypt/argon2를 사용해야 한다.", code:`import hashlib
pw_hash = hashlib.md5(password.encode()).hexdigest()` },
  { c:"보안기능", q:"중요정보를 로그에 그대로 기록하는 행위의 약점은?", o:["민감정보 평문 노출(로그를 통한 정보 노출)","성능 약점","코드 인젝션","경쟁 조건"], a:0, e:"비밀번호/카드번호/토큰을 로그에 평문 기록하면 로그 접근만으로 유출된다. 마스킹/제외해야 한다." },
  { c:"보안기능", q:"다중 인증(MFA) 도입의 주된 보안 목적은?", o:["비밀번호 단일 인증의 한계를 보완해 계정 탈취 위험을 낮춘다","네트워크 속도를 높인다","세션 크기를 줄인다","암호화 키를 늘린다"], a:0, e:"비밀번호 유출 시에도 추가 인증요소가 있어 계정 탈취를 어렵게 만든다." },
  { c:"보안기능", q:"안전한 초기화 벡터(IV)/Nonce 사용 원칙으로 옳은 것은?", o:["고정값을 재사용한다","매 암호화마다 예측 불가능한 IV를 새로 생성한다","평문과 동일하게 둔다","항상 0으로 채운다"], a:1, e:"IV/Nonce는 매번 새롭고 예측 불가능해야 하며, 특히 GCM에서 nonce 재사용은 치명적이다." },
  { c:"보안기능", q:"권한 검사를 클라이언트 측(JS)에서만 수행하면 생기는 문제는?", o:["서버 우회로 인가가 무력화됨","화면이 느려짐","쿠키가 커짐","난수가 약해짐"], a:0, e:"클라이언트 검사는 우회 가능하므로 인가 검사는 반드시 서버에서 수행해야 한다." },
  { c:"보안기능", q:"Argon2가 비밀번호 해시로 선호되는 이유로 가장 적절한 것은?", o:["메모리-하드(memory-hard) 특성으로 GPU/ASIC 대량 공격에 강함","출력이 가장 짧아서","솔트가 필요 없어서","대칭 암호라서"], a:0, e:"Argon2는 메모리 비용을 요구해 병렬 무차별 대입을 어렵게 한다." },
  { c:"보안기능", q:"다음 중 '잘못된 권한 설정'으로 가장 적절한 예는?", o:["일반 사용자에게 관리자 권한을 기본 부여","최소권한 원칙 적용","역할 기반 접근제어(RBAC) 사용","권한 변경 시 감사로그 남김"], a:0, e:"필요 이상 권한을 부여하면 권한 상승·오남용 위험이 커진다. 최소권한이 원칙이다." },
  { c:"보안기능", q:"비대칭키 알고리즘으로만 묶인 것은?", o:["RSA, ECC, ECDSA","AES, SEED, ARIA","MD5, SHA-256","HMAC, PBKDF2"], a:0, e:"RSA, ECC, ECDSA는 공개키(비대칭) 방식이다. AES/SEED/ARIA는 대칭키, 나머지는 해시/MAC/KDF다." },
  { c:"보안기능", q:"전자서명 검증을 생략하거나 잘못 구현하면(CWE-347) 발생하는 위험은?", o:["서명 위조/변조된 데이터를 정상으로 수락","속도 저하만 발생","키 길이 감소","쿠키 손실"], a:0, e:"서명 검증이 부적절하면 위조·변조된 데이터를 신뢰하게 되어 인증·무결성이 무너진다." },
  { c:"보안기능", q:"다음 중 솔트(salt)의 올바른 사용 방법은?", o:["사용자마다 임의의 고유 솔트를 생성해 해시와 함께 저장","모든 사용자에게 동일한 고정 솔트 사용","솔트를 비밀번호 앞에 붙이지 않음","솔트를 4비트로 짧게 사용"], a:0, e:"솔트는 사용자별로 임의·고유해야 하며 해시값과 함께 저장한다. 충분한 길이(예: 16바이트 이상)가 권장된다." },
  { c:"보안기능", q:"민감 API에 대해 '캡차/속도 제한/계정 잠금'을 두는 주된 목적은?", o:["반복 인증/요청 시도를 제한해 무차별 공격 완화","SQL 인젝션 차단","XSS 차단","경로 조작 차단"], a:0, e:"속도 제한·계정 잠금·캡차는 반복 시도 제한(CWE-307) 대응책이다." },
  { c:"보안기능", q:"HMAC을 사용하는 주된 목적은?", o:["메시지 무결성과 출처 인증","데이터 압축","대칭키 교환","난수 생성"], a:0, e:"HMAC은 비밀키 기반 메시지 인증코드로 무결성과 송신자 인증을 제공한다." },
  { c:"보안기능", q:"다음 중 '암호화되지 않은 중요정보 전송'(CWE-319)에 해당하는 것은?", o:["로그인 폼을 HTTP(평문)로 전송","TLS로 비밀번호 전송","HTTPS API 호출","암호화된 토큰 사용"], a:0, e:"평문 HTTP로 자격증명을 전송하면 도청에 노출된다. 전 구간 HTTPS가 필요하다." },
  { c:"보안기능", q:"비밀번호 재설정 토큰 설계로 부적절한 것은?", o:["충분한 엔트로피의 난수 사용","짧은 만료시간 설정","1회용으로 사용 후 폐기","순차 증가하는 숫자 ID 사용"], a:3, e:"예측 가능한 순차 ID는 추측 가능하다. 토큰은 SecureRandom 기반 고엔트로피, 1회용, 단기 만료여야 한다." },
  { c:"보안기능", q:"key stretching(키 스트레칭)의 목적은?", o:["짧은 비밀번호로부터 도출되는 키를 의도적으로 느리게 계산해 무차별 대입을 어렵게 함","키 길이를 줄임","암호문을 압축","난수 시드를 고정"], a:0, e:"PBKDF2/bcrypt/scrypt/Argon2는 반복 계산으로 비용을 높여 오프라인 대입을 어렵게 한다." },
  { c:"보안기능", q:"안전하지 않은 직접 객체 참조(IDOR)는 어떤 약점 범주와 가장 밀접한가?", o:["부적절한 인가","취약한 암호화","난수 약점","주석 정보 노출"], a:0, e:"IDOR은 객체 식별자만 바꿔 타인 자원에 접근하는 것으로 인가 검증 누락(부적절한 인가)에 해당한다." },
  { c:"보안기능", q:"다음 중 안전한 비밀번호 비교 방법은?", o:["타이밍 공격에 안전한 상수시간 비교 사용","== 단순 문자열 비교","해시 없이 평문 비교","길이만 비교"], a:0, e:"인증 토큰/해시 비교는 hmac.compare_digest 등 상수시간 비교로 타이밍 누출을 막는다." },
  { c:"보안기능", q:"다음 Python 코드의 약점은?", o:["JWT 서명 검증을 끔(verify_signature False)","import 오류","인코딩 오류","타임존 오류"], a:0, e:"서명 검증을 끄면 토큰을 신뢰할 수 없다. options로 검증을 비활성화하면 안 된다.", code:`import jwt
data = jwt.decode(token, options={"verify_signature": False})` },
  { c:"보안기능", q:"세션 쿠키에 SameSite 속성을 설정하는 주된 목적은?", o:["CSRF 위험 완화","난수 강화","암호화 강화","로그 마스킹"], a:0, e:"SameSite(Lax/Strict)는 교차 사이트 요청에서 쿠키 전송을 제한해 CSRF를 완화한다." },
  { c:"보안기능", q:"비밀키를 저장/배포할 때 가장 권장되는 방식은?", o:["소스코드에 상수로 작성","KMS/Vault/환경변수 등 외부 안전저장소 사용","주석에 메모","공유 폴더에 텍스트 파일로 저장"], a:1, e:"비밀정보는 코드와 분리하여 KMS, Vault, 환경변수, 보안 설정파일 등으로 관리해야 한다." },
  { c:"보안기능", q:"다음 중 '적절한 인증 없는 중요기능 허용'을 예방하는 서버 측 조치는?", o:["중요기능 진입 시 인증·세션·권한을 매 요청마다 검증","UI에서 버튼만 숨김","JS에서만 검증","URL을 추측 어렵게만 만듦(보안 by 모호성)"], a:0, e:"기능 숨김/모호성은 우회 가능하다. 서버에서 인증과 인가를 매 요청 검증해야 한다." }
);
window.__QBANK.THEORY.push(
  { type:"OX", cat:"보안기능", q:"MD5와 SHA-1은 충돌 공격이 알려져 있어 무결성/비밀번호 용도로 권장되지 않는다.", a:true, e:"두 알고리즘 모두 충돌이 실증되어 폐기 권고 대상이다. SHA-256 이상을 사용한다." },
  { type:"OX", cat:"보안기능", q:"java.util.Random은 보안용 난수(토큰, 세션ID) 생성에 사용해도 안전하다.", a:false, e:"java.util.Random은 예측 가능하다. 보안 난수는 java.security.SecureRandom을 사용해야 한다." },
  { type:"OX", cat:"보안기능", q:"RSA는 최소 2048비트 이상의 키 길이를 권장한다.", a:true, e:"1024비트 이하는 안전하지 않으며 2048비트 이상이 권장된다." },
  { type:"OX", cat:"보안기능", q:"ECB 모드는 동일 평문 블록이 동일 암호문이 되어 패턴이 노출되므로 권장되지 않는다.", a:true, e:"ECB는 데이터 패턴이 드러나 취약하다. GCM 등 인증 암호 모드를 권장한다." },
  { type:"OX", cat:"보안기능", q:"JWT에서 alg를 none으로 허용하면 서명 검증 없이 토큰을 위조할 수 있다.", a:true, e:"alg=none은 서명 검증을 무력화하므로 절대 허용하면 안 된다." },
  { type:"OX", cat:"보안기능", q:"비밀번호 저장 시 모든 사용자에게 동일한 고정 솔트를 쓰면 안전성이 충분히 보장된다.", a:false, e:"고정 솔트는 레인보우 테이블에 다시 취약해진다. 사용자별 임의 솔트를 써야 한다." },
  { type:"OX", cat:"보안기능", q:"requests.get(url, verify=False)는 인증서 검증을 비활성화하여 MITM에 취약하다.", a:true, e:"verify=False는 서버 인증서 검증을 끄므로 중간자 공격에 노출된다." },
  { type:"OX", cat:"보안기능", q:"소스코드 주석에 DB 비밀번호를 적어두는 것은 배포 전 제거하면 보안상 문제없는 권장 관행이다.", a:false, e:"주석 내 주요정보(CWE-615)는 약점이다. 애초에 작성하지 말아야 한다." },
  { type:"OX", cat:"보안기능", q:"인가(authorization) 검사는 신뢰할 수 없는 클라이언트가 아니라 서버에서 수행해야 한다.", a:true, e:"클라이언트 검사는 우회 가능하므로 인가는 서버에서 강제해야 한다." },
  { type:"OX", cat:"보안기능", q:"GCM 모드에서 동일한 nonce(IV)를 같은 키로 재사용해도 안전하다.", a:false, e:"GCM에서 nonce 재사용은 인증키 노출로 이어질 수 있어 치명적이다. 매번 새로운 nonce를 사용해야 한다." },
  { type:"SHORT", cat:"보안기능", q:"Java에서 보안용 난수 생성을 위해 사용해야 하는 클래스 이름은?", a:"SecureRandom", answers:["java.security.SecureRandom"], e:"예측 불가능한 보안 난수는 SecureRandom을 사용한다." },
  { type:"SHORT", cat:"보안기능", q:"Python 표준 라이브러리에서 보안용 난수/토큰을 생성하는 모듈 이름은?", a:"secrets", answers:["secrets 모듈"], e:"secrets 모듈은 내부적으로 os.urandom을 사용해 암호학적으로 안전한 난수를 제공한다." },
  { type:"SHORT", cat:"보안기능", q:"동일 평문 블록이 동일 암호문이 되어 패턴이 노출되는 취약한 블록암호 운용모드 이름은?", a:"ECB", answers:["ECB 모드","Electronic Codebook"], e:"ECB 모드는 패턴 노출로 취약하다." },
  { type:"SHORT", cat:"보안기능", q:"기밀성과 무결성(인증)을 함께 제공하는 AEAD 블록암호 운용모드의 대표 예를 하나 쓰시오.", a:"GCM", answers:["GCM 모드","Galois/Counter Mode","CCM"], e:"GCM은 인증 암호 모드로 변조 탐지가 가능하다." },
  { type:"SHORT", cat:"보안기능", q:"비밀번호 저장 시 레인보우 테이블 공격을 막기 위해 비밀번호마다 추가하는 임의 값의 이름은?", a:"솔트", answers:["salt","솔트(salt)"], e:"사용자별 임의 솔트로 동일 비밀번호의 해시를 서로 다르게 만든다." },
  { type:"SHORT", cat:"보안기능", q:"국내 표준 대칭키 블록암호 두 가지를 쓰시오. (예: ____, ____)", a:"SEED, ARIA", answers:["SEED와 ARIA","ARIA, SEED","SEED ARIA"], e:"SEED와 ARIA가 국내 표준 대칭키 블록암호다." },
  { type:"SHORT", cat:"보안기능", q:"비밀번호 저장에 권장되는 메모리-하드 비밀번호 해시 알고리즘 이름을 하나 쓰시오.", a:"Argon2", answers:["argon2","bcrypt","scrypt","PBKDF2"], e:"Argon2(또는 bcrypt/scrypt/PBKDF2)는 비밀번호 전용 해시로 권장된다." },
  { type:"SHORT", cat:"보안기능", q:"쿠키 탈취를 막기 위해 JavaScript의 접근을 차단하는 쿠키 속성 이름은?", a:"HttpOnly", answers:["HttpOnly 속성","http only"], e:"HttpOnly는 document.cookie 등 스크립트 접근을 막아 XSS로 인한 탈취를 줄인다." },
  { type:"SHORT", cat:"보안기능", q:"HTTPS 환경에서만 쿠키를 전송하도록 강제하는 쿠키 속성 이름은?", a:"Secure", answers:["Secure 속성"], e:"Secure 속성은 평문(HTTP) 전송 시 쿠키를 보내지 않게 한다." },
  { type:"SHORT", cat:"보안기능", q:"반복적인 로그인 시도를 제한하지 않아 무차별 대입에 취약한 약점의 CWE 번호는?", a:"CWE-307", answers:["307","cwe307"], e:"CWE-307: Improper Restriction of Excessive Authentication Attempts." },
  { type:"SHORT", cat:"보안기능", q:"소스코드에 비밀번호/키를 직접 박아두는 약점의 영문 명칭(또는 CWE 번호)을 쓰시오.", a:"하드코드된 중요정보", answers:["hard-coded credentials","CWE-798","하드코딩","hardcoded secret"], e:"CWE-798: Use of Hard-coded Credentials." },
  { type:"SHORT", cat:"보안기능", q:"전송 구간 보안을 위해 사용해야 하는 최소 권장 프로토콜 버전은? (예: TLS ___ 이상)", a:"1.2", answers:["TLS 1.2","1.3","TLS 1.3"], e:"TLS 1.2 이상(권장 1.3)을 사용하고 SSL 및 TLS 1.0/1.1은 폐기한다." },
  { type:"MC", cat:"보안기능", q:"다음 중 비대칭키(공개키) 암호 알고리즘은?", o:["AES","SEED","RSA","ARIA"], a:2, e:"RSA는 비대칭키 알고리즘이다. AES/SEED/ARIA는 대칭키다." },
  { type:"MC", cat:"보안기능", q:"AES에서 지원하지 않는 키 길이는?", o:["128비트","192비트","256비트","384비트"], a:3, e:"AES는 128/192/256비트만 지원한다." },
  { type:"MC", cat:"보안기능", q:"비밀번호 저장에 가장 부적절한 방식은?", o:["MD5 단순 해시","bcrypt","Argon2","PBKDF2"], a:0, e:"MD5는 빠르고 취약해 비밀번호 저장에 부적절하다." },
  { type:"MC", cat:"보안기능", q:"JWT 서명 검증 시 가장 안전한 정책은?", o:["토큰의 alg 헤더를 그대로 신뢰","서버가 허용 알고리즘을 화이트리스트로 고정","alg=none 허용","검증 생략"], a:1, e:"알고리즘 혼동 공격을 막기 위해 허용 알고리즘을 고정해야 한다." },
  { type:"MC", cat:"보안기능", q:"다음 중 '부적절한 인가'에 해당하는 상황은?", o:["로그인 통과 후 권한 검사 없이 타인 데이터 접근","비밀번호 평문 저장","난수 예측 가능","주석에 키 노출"], a:0, e:"인증 후 인가 검사 누락은 CWE-285 부적절한 인가다." },
  { type:"MC", cat:"보안기능", q:"국내 전자서명 표준 알고리즘은?", o:["RC4","KCDSA","DES","MD5"], a:1, e:"KCDSA/EC-KCDSA가 국내 전자서명 표준이다." },
  { type:"MC", cat:"보안기능", q:"외부에서 내려받은 실행 코드의 안전한 검증 방법은?", o:["파일 크기만 확인","디지털 서명 또는 해시 검증","HTTP로만 다운로드","검증 없이 즉시 실행"], a:1, e:"무결성 검사 없는 코드 다운로드(CWE-494)는 서명/해시 검증으로 막는다." },
  { type:"MC", cat:"보안기능", q:"ECC에서 RSA-2048과 유사한 보안강도를 위한 최소 권장 키 길이는?", o:["128비트","160비트","224~256비트","2048비트"], a:2, e:"ECC 224~256비트가 RSA-2048~3072 수준의 강도를 제공한다. 일반적으로 256비트 이상을 권장한다." }
);

// ===== partC =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };

window.__QBANK.QUIZ.push(
  // ===================== 시간상태 (Time & State) =====================
  {
    c:"시간상태",
    q:"다음 Java 코드에서 발생하는 보안약점은 무엇인가?",
    o:["TOCTOU 경쟁조건(Race Condition)","SQL 인젝션","정수 오버플로우","하드코딩된 비밀번호"],
    a:0,
    e:"파일 존재 여부를 검사(exists)한 시점과 실제로 파일을 여는(use) 시점 사이에 공격자가 파일을 심볼릭 링크 등으로 바꿔치기할 수 있다. 검사-사용 사이의 시간 간격(Time-of-check to Time-of-use) 때문에 발생하는 경쟁조건이다.",
    code:`File f = new File(path);
if (f.exists() && f.canWrite()) {   // check
    FileWriter fw = new FileWriter(f); // use (간격 발생)
    fw.write(data);
}`
  },
  {
    c:"시간상태",
    q:"TOCTOU(Time-Of-Check Time-Of-Use) 경쟁조건을 완화하는 가장 올바른 접근은?",
    o:["검사와 사용 사이에 sleep을 추가한다","검사 단계를 두 번 반복한다","검사 없이 원자적(atomic) 연산이나 적절한 잠금/예외 처리로 한 번에 수행한다","파일 경로를 로그로 남긴다"],
    a:2,
    e:"별도의 검사 후 사용 패턴 자체를 제거하고, 원자적 연산(예: 파일을 직접 열고 발생하는 예외를 처리)이나 락을 사용해 검사와 사용 사이의 틈을 없애야 한다.",
  },
  {
    c:"시간상태",
    q:"여러 스레드가 공유 카운터를 동시에 갱신할 때 값이 유실되는 현상의 근본 원인은?",
    o:["메모리 부족","상호배제(mutual exclusion) 미보장으로 인한 경쟁조건","가비지 컬렉션","스택 오버플로우"],
    a:1,
    e:"읽기-수정-쓰기(read-modify-write)가 원자적이지 않아 여러 스레드가 동시에 접근하면 갱신이 유실된다. synchronized, Lock, AtomicInteger 등으로 임계영역을 보호해야 한다.",
    code:`// 취약: count++ 는 원자적이지 않음
class Counter { int count = 0;
  void inc(){ count++; } }
// 안전: AtomicInteger 또는 synchronized 사용`
  },
  {
    c:"시간상태",
    q:"다음 정규식을 사용자 입력에 적용할 때 발생할 수 있는 보안 문제는?",
    o:["메모리 누수","ReDoS(정규표현식 서비스 거부)","버퍼 오버플로우","역직렬화 취약점"],
    a:1,
    e:"중첩된 수량자(quantifier)와 백트래킹이 폭발적으로 증가하는 'evil regex'는 특정 입력에서 지수적 시간이 걸려 CPU를 고갈시킨다. 이를 ReDoS라 하며, 정규식 단순화나 입력 길이 제한, 비백트래킹 엔진으로 완화한다.",
    code:`// 취약한 evil regex
Pattern p = Pattern.compile("^(a+)+$");
// "aaaaaaaaaaaaaaaaaaaaa!" 같은 입력에서 지수적 백트래킹`
  },
  {
    c:"시간상태",
    q:"Python에서 종료 조건이 잘못되어 무한 재귀가 발생할 때 일어나는 일은?",
    o:["프로그램이 즉시 정상 종료된다","RecursionError(스택 한도 초과)가 발생하거나 서비스가 중단된다","컴파일 오류가 발생한다","자동으로 반복문으로 변환된다"],
    a:1,
    e:"기저 사례(base case)가 없거나 도달하지 못하면 재귀가 무한히 깊어져 RecursionError가 발생한다. 사용자 입력에 따라 재귀 깊이가 결정되면 DoS로 악용될 수 있으므로 깊이 제한과 종료 조건을 명확히 해야 한다.",
  },
  {
    c:"시간상태",
    q:"synchronized 블록 사용 시 데드락(교착상태)을 유발하기 쉬운 상황은?",
    o:["단일 락만 사용하는 경우","두 스레드가 서로 다른 순서로 두 개의 락을 획득하는 경우","락을 전혀 사용하지 않는 경우","읽기 전용 연산만 하는 경우"],
    a:1,
    e:"스레드 A가 락1→락2 순으로, 스레드 B가 락2→락1 순으로 획득하려 하면 서로 상대가 가진 락을 기다리며 교착된다. 모든 스레드가 동일한 순서로 락을 획득하도록 강제하면 예방할 수 있다.",
  },
  {
    c:"시간상태",
    q:"체크-후-사용(check-then-act) 경쟁조건을 막기 위해 ConcurrentHashMap에서 권장되는 메소드는?",
    o:["get 후 put","containsKey 후 put","putIfAbsent 또는 computeIfAbsent","values().add"],
    a:2,
    e:"containsKey로 검사한 뒤 put 하는 패턴은 검사와 삽입 사이에 다른 스레드가 끼어들 수 있다. putIfAbsent/computeIfAbsent는 검사와 삽입을 원자적으로 수행한다.",
  },
  {
    c:"시간상태",
    q:"다음 중 '종료되지 않는 반복문'으로 인한 보안약점에 해당하는 것은?",
    o:["루프 조건이 외부 입력에 의존하면서 증가/탈출 보장이 없는 경우","for 루프에 인덱스를 사용하는 경우","while(true) 안에 break가 있는 경우","루프 안에서 로그를 남기는 경우"],
    a:0,
    e:"루프 종료 변수가 갱신되지 않거나 외부 입력이 종료를 막을 수 있으면 무한 루프가 되어 자원을 고갈시킨다. 종료 조건의 명확성과 상한(최대 반복 횟수)을 보장해야 한다.",
  },
  {
    c:"시간상태",
    q:"파일 잠금(file lock) 없이 두 프로세스가 같은 상태 파일을 동시에 갱신할 때의 위험은?",
    o:["파일 크기 증가","상태 손상(lost update) 및 데이터 불일치","읽기 속도 저하","파일 권한 변경"],
    a:1,
    e:"동시 쓰기가 직렬화되지 않으면 한쪽의 갱신이 다른 쪽 갱신에 덮어써져 상태가 손상된다. 원자적 저장(임시파일 후 rename)과 파일 잠금으로 보호한다.",
  },
  {
    c:"시간상태",
    q:"다음 Python 코드의 시간상태 관련 약점은?",
    o:["권한 검사 결과를 캐시하지 않아 느림","os.access로 검사 후 open 하는 사이의 TOCTOU","파일을 두 번 연다","예외를 무시한다"],
    a:1,
    e:"os.access()는 실제 open과 다른 시점/다른 권한 모델로 검사하므로, 검사 후 open 사이에 파일이 바뀔 수 있다. 권장 방식은 바로 open을 시도하고 예외(PermissionError)를 처리하는 것이다.",
    code:`# 취약: TOCTOU
if os.access(path, os.W_OK):
    with open(path, 'w') as f:   # 사이에 바꿔치기 가능
        f.write(data)`
  },

  // ===================== 에러처리 (Error Handling) =====================
  {
    c:"에러처리",
    q:"예외 발생 시 스택 트레이스를 그대로 HTTP 응답에 출력하면 어떤 보안약점인가?",
    o:["오류 메시지를 통한 정보 노출","SQL 인젝션","경쟁조건","부적절한 인가"],
    a:0,
    e:"스택 트레이스에는 내부 클래스/패키지 구조, 파일 경로, 라이브러리 버전, SQL 쿼리 등 공격에 유용한 정보가 포함된다. 사용자에게는 일반 메시지를 보여주고 상세 내용은 서버 로그에만 남겨야 한다.",
    code:`// 취약
try { ... } catch (Exception e) {
    response.getWriter().println(e.toString());
    e.printStackTrace(response.getWriter());
}`
  },
  {
    c:"에러처리",
    q:"다음 catch 블록의 문제점은?",
    o:["로깅이 너무 많다","빈 catch 블록으로 오류를 무시(삼킴)한다","예외 타입이 너무 구체적이다","throws 선언이 누락됐다"],
    a:1,
    e:"예외를 잡고 아무 처리도 하지 않으면(빈 catch) 오류가 은폐되어 비정상 상태로 계속 진행된다. 최소한 로깅하거나 적절히 복구/재전파해야 한다.",
    code:`try {
    doImportant();
} catch (IOException e) {
    // 아무것도 하지 않음 -> 오류 은폐
}`
  },
  {
    c:"에러처리",
    q:"오류 상황 대응 부재(unchecked return value)의 대표적 예는?",
    o:["함수 반환값을 항상 검사하는 것","File.delete()나 메소드 반환값(성공/실패)을 검사하지 않고 진행하는 것","예외를 다시 던지는 것","try-with-resources 사용"],
    a:1,
    e:"delete(), createNewFile(), mkdir() 등은 예외 대신 boolean 성공 여부를 반환한다. 반환값을 검사하지 않으면 실패를 인지하지 못한 채 후속 로직이 잘못된 가정 위에서 동작한다.",
  },
  {
    c:"에러처리",
    q:"catch(Exception e) 또는 except Exception 으로 모든 예외를 광범위하게 잡는 것이 위험한 이유는?",
    o:["성능이 느려져서","의도치 않은 치명적 예외(예: 프로그래밍 오류)까지 삼켜 디버깅과 복구를 어렵게 만들기 때문","컴파일이 안 되기 때문","로그가 너무 길어져서"],
    a:1,
    e:"너무 광범위한 예외 포착은 NullPointerException 같은 버그성 예외나 시스템 오류까지 가려서 잘못된 상태로 계속 실행되게 한다. 가능한 한 구체적인 예외만 잡아 처리해야 한다.",
  },
  {
    c:"에러처리",
    q:"DB 오류 메시지를 사용자에게 그대로 노출하지 않기 위한 올바른 처리는?",
    o:["오류 메시지를 Base64로 인코딩한다","일반화된 메시지를 사용자에게 보여주고 상세 오류는 서버 로그에만 기록한다","오류 메시지를 클라이언트 쿠키에 저장한다","예외를 무시한다"],
    a:1,
    e:"SQL 오류 텍스트는 테이블/컬럼명, 쿼리 구조를 노출해 인젝션 공격에 단서를 준다. 사용자에게는 '요청을 처리할 수 없습니다' 같은 일반 메시지를, 상세 정보는 서버 로그에 남긴다.",
  },
  {
    c:"에러처리",
    q:"다음 Python 코드의 부적절한 예외처리는?",
    o:["except가 너무 구체적이다","except: pass 로 모든 예외를 조용히 삼킨다","try가 너무 짧다","finally가 누락됐다"],
    a:1,
    e:"맨몸 except: pass 는 KeyboardInterrupt, SystemExit를 포함한 모든 예외를 무음 처리하여 오류를 은폐한다. 구체적 예외를 잡고 로깅하거나 적절히 처리해야 한다.",
    code:`try:
    risky()
except:        # 모든 예외
    pass       # 조용히 무시`
  },
  {
    c:"에러처리",
    q:"예외를 잡아 로깅한 뒤, 호출자가 처리해야 하는 상황을 알려야 할 때 적절한 방법은?",
    o:["예외를 삼키고 null을 반환","원인 예외를 포함해 적절한 예외로 다시 던진다(예외 체이닝)","System.exit(0) 호출","무한 재시도"],
    a:1,
    e:"예외 체이닝(throw new XException(\"...\", e))으로 원인을 보존하면서 추상화 수준에 맞는 예외로 변환해 재전파하면, 정보 손실 없이 상위 계층이 적절히 대응할 수 있다.",
  },
  {
    c:"에러처리",
    q:"finally 블록에서 절대 하지 말아야 할 것은?",
    o:["자원을 해제하는 것","return 또는 예외를 던져 try 블록의 정상 예외/반환을 가리는 것","로그를 남기는 것","null 체크"],
    a:1,
    e:"finally에서 return하거나 새 예외를 던지면 try에서 발생한 원래 예외/반환값이 덮어써져 사라진다. finally는 정리 작업에만 사용하고 흐름 제어 문장은 피해야 한다.",
  },
  {
    c:"에러처리",
    q:"인증 실패 시 '아이디가 존재하지 않음'과 '비밀번호가 틀림'을 구분해 알려주면 생기는 문제는?",
    o:["성능 저하","사용자 열거(account enumeration) 정보 노출","경쟁조건","메모리 누수"],
    a:1,
    e:"오류 메시지를 구분하면 공격자가 유효한 계정 목록을 알아낼 수 있다. 인증 실패는 '아이디 또는 비밀번호가 올바르지 않습니다'처럼 동일한 일반 메시지로 응답해야 한다.",
  },

  // ===================== 코드오류 (Code Errors) =====================
  {
    c:"코드오류",
    q:"다음 코드에서 발생 가능한 보안약점은?",
    o:["널 포인터 역참조(Null Pointer Dereference)","정수 오버플로우","경쟁조건","SQL 인젝션"],
    a:0,
    e:"request.getParameter()는 파라미터가 없으면 null을 반환할 수 있고, 그 결과에 .trim()을 호출하면 NullPointerException이 발생한다. 사용 전 null 검사를 해야 한다.",
    code:`String name = request.getParameter("name");
// name 이 null 이면 NPE
if (name.trim().isEmpty()) { ... }`
  },
  {
    c:"코드오류",
    q:"Java 7+ 에서 자원(스트림 등)을 가장 안전하게 해제하는 방법은?",
    o:["finalize() 오버라이드","try-with-resources 구문","System.gc() 호출","finally에서 close를 호출하되 예외는 무시"],
    a:1,
    e:"try-with-resources는 AutoCloseable 자원을 블록 종료 시 자동으로(역순으로) 닫아주며, close 중 예외도 suppressed로 보존한다. 누락이나 예외로 인한 자원 누수를 방지한다.",
    code:`try (FileInputStream in = new FileInputStream(f)) {
    // 사용
} // 자동 close`
  },
  {
    c:"코드오류",
    q:"다음 코드의 '부적절한 자원 해제' 문제는?",
    o:["close가 finally가 아닌 try 블록 끝에 있어 예외 시 누수된다","스트림을 두 번 닫는다","스트림을 열지 않는다","버퍼 크기가 작다"],
    a:0,
    e:"읽기 중 예외가 발생하면 in.close()에 도달하지 못해 파일 핸들이 누수된다. try-with-resources나 finally 블록에서 닫아야 한다.",
    code:`FileInputStream in = new FileInputStream(f);
process(in);     // 여기서 예외 발생하면
in.close();      // 도달 못 함 -> 누수`
  },
  {
    c:"코드오류",
    q:"Python에서 파일 자원 누수를 방지하는 권장 구문은?",
    o:["open 후 수동 close","with 문(컨텍스트 매니저)","del 키워드","gc.collect()"],
    a:1,
    e:"with open(...) as f: 는 블록을 벗어날 때(예외 포함) 자동으로 파일을 닫는다. 수동 close는 예외 경로에서 누락되기 쉽다.",
    code:`with open(path) as f:
    data = f.read()
# 블록 종료 시 자동 close`
  },
  {
    c:"코드오류",
    q:"'해제된 자원 사용(use-after-close)'에 해당하는 코드는?",
    o:["close() 호출 후 같은 스트림에 다시 write/read를 시도","close()를 호출하지 않는 것","스트림을 새로 여는 것","try-with-resources 사용"],
    a:0,
    e:"이미 닫힌 스트림/커넥션을 다시 사용하면 IOException이나 정의되지 않은 동작이 발생한다. 닫은 자원의 참조를 더 이상 사용하지 않도록 관리해야 한다.",
    code:`conn.close();
Statement st = conn.createStatement(); // 닫힌 커넥션 사용 -> 오류`
  },
  {
    c:"코드오류",
    q:"초기화되지 않은 변수를 사용할 때의 위험은?",
    o:["항상 0으로 안전하게 동작","예측 불가능한 값/상태로 인한 오작동 또는 보안 결정 오류","컴파일 속도 향상","자동 가비지 컬렉션"],
    a:1,
    e:"Java 지역변수는 초기화 없이 사용하면 컴파일 오류가 나지만, 조건부 초기화 누락이나 필드의 부적절한 기본값은 잘못된 상태로 이어진다. 특히 보안 플래그가 초기화되지 않으면 인가 우회로 이어질 수 있다.",
  },
  {
    c:"코드오류",
    q:"다음 Java 코드의 심각한 보안약점은?",
    o:["신뢰할 수 없는 데이터의 역직렬화","문자열 비교 오류","정수 오버플로우","약한 난수"],
    a:0,
    e:"ObjectInputStream.readObject()로 신뢰할 수 없는 바이트를 역직렬화하면 가젯 체인을 통한 원격 코드 실행이 가능하다. JSON 같은 데이터 포맷을 쓰거나, 역직렬화 시 허용 클래스 화이트리스트(ObjectInputFilter)를 적용해야 한다.",
    code:`ObjectInputStream ois = new ObjectInputStream(socket.getInputStream());
Object obj = ois.readObject();  // 신뢰 불가 데이터 역직렬화 -> RCE`
  },
  {
    c:"코드오류",
    q:"Python에서 신뢰할 수 없는 데이터를 처리할 때 절대 사용하면 안 되는 함수는?",
    o:["json.loads","pickle.loads","int","str.split"],
    a:1,
    e:"pickle.loads()는 역직렬화 과정에서 임의의 객체 생성/코드 실행을 허용해 RCE로 이어진다. 외부 입력에는 json 등 데이터 전용 포맷을 사용해야 한다.",
    code:`import pickle
obj = pickle.loads(untrusted_bytes)  # 위험: 임의 코드 실행`
  },
  {
    c:"코드오류",
    q:"신뢰할 수 없는 역직렬화를 방어하는 가장 안전한 전략은?",
    o:["역직렬화 후 입력값을 검증","역직렬화 자체를 데이터 포맷(JSON)으로 대체하거나 클래스 허용목록을 적용","압축을 풀고 사용","try-catch로 감싸기"],
    a:1,
    e:"역직렬화는 객체 생성 과정 자체에서 코드가 실행되므로 사후 검증으로는 막을 수 없다. 임의 객체를 생성하는 직렬화 대신 JSON 같은 순수 데이터 포맷을 쓰거나, 불가피하면 허용 클래스 목록(allow-list) 필터를 적용한다.",
  },
  {
    c:"코드오류",
    q:"Optional 또는 null 검사로 방지하려는 대표 결함은?",
    o:["널 포인터 역참조","무한 루프","자원 누수","약한 암호화"],
    a:0,
    e:"메소드가 null을 반환할 수 있을 때 Optional이나 명시적 null 검사를 사용하면, 호출자가 null을 역참조해 NullPointerException을 일으키는 것을 방지할 수 있다.",
  },
  {
    c:"코드오류",
    q:"다음 코드에서 자원이 누수되는 경로는?",
    o:["정상 종료 경로","return early로 인해 close가 실행되지 않는 경로","루프 내부","생성자"],
    a:1,
    e:"조건 검사 후 close 전에 return하면 열린 자원이 닫히지 않는다. try-with-resources를 쓰면 어떤 경로로 빠져나가도 자동으로 닫힌다.",
    code:`InputStream in = open();
if (invalid) return;   // close 못 하고 반환 -> 누수
in.close();`
  },
  {
    c:"코드오류",
    q:"멀티스레드 환경에서 객체를 닫은 뒤 다른 스레드가 여전히 그 객체를 사용하면?",
    o:["문제없다","해제된 자원 사용으로 인한 오류/정의되지 않은 동작","성능이 향상된다","자동 재연결된다"],
    a:1,
    e:"한 스레드가 자원을 닫은 뒤 다른 스레드가 동일 자원을 참조해 사용하면 use-after-close 결함이 발생한다. 자원 수명주기를 명확히 관리하고 공유 시 동기화해야 한다.",
  },
  {
    c:"코드오류",
    q:"DB 커넥션, Statement, ResultSet을 모두 안전하게 닫으려면?",
    o:["ResultSet만 닫으면 된다","각각 try-with-resources로 선언하거나 finally에서 역순으로 닫는다","close는 GC가 알아서 한다","Connection만 닫으면 나머지도 닫힌다"],
    a:1,
    e:"세 자원 모두 명시적으로 닫아야 누수가 없다. try-with-resources에 함께 선언하면 선언의 역순으로 자동 close 된다. (단, 일부 드라이버는 Connection close 시 하위 자원도 닫지만 명시적 관리가 안전하다.)",
  },
  {
    c:"코드오류",
    q:"다음 중 NPE(Null Pointer)를 유발하기 가장 쉬운 패턴은?",
    o:["\"상수\".equals(변수)","변수.equals(\"상수\")","Objects.equals(a,b)","Optional.ofNullable 사용"],
    a:1,
    e:"변수가 null일 때 변수.equals(...)는 NPE를 던진다. 상수.equals(변수) 또는 Objects.equals(a,b)를 쓰면 null-safe 하다.",
    code:`// 취약: name 이 null 이면 NPE
if (name.equals("admin")) { ... }
// 안전
if ("admin".equals(name)) { ... }`
  },
  {
    c:"코드오류",
    q:"Java의 직렬화 가능한 클래스에서 역직렬화 공격 표면을 줄이는 방법은?",
    o:["모든 필드를 public으로","readObject를 커스터마이징하지 않기","민감 필드를 transient로, readObject에서 불변식 검증, 또는 직렬화를 아예 사용하지 않기","serialVersionUID 제거"],
    a:2,
    e:"민감 데이터는 transient로 직렬화에서 제외하고, readObject 내에서 객체 불변식을 검증하며, 가능하면 직렬화 사용 자체를 피하는 것이 가장 안전하다.",
  },

  // ===================== 캡슐화 (Encapsulation) =====================
  {
    c:"캡슐화",
    q:"public 메소드가 내부 private 배열의 참조를 그대로 반환하면 어떤 문제가 생기나?",
    o:["성능 저하","외부에서 내부 배열을 직접 수정해 캡슐화가 깨진다","컴파일 오류","메모리 누수"],
    a:1,
    e:"배열은 가변 객체이므로 내부 배열 참조를 그대로 반환하면 호출자가 내부 상태를 임의로 바꿀 수 있다. clone()이나 방어적 복사본을 반환해야 한다.",
    code:`private int[] data;
public int[] getData() {
    return data;        // 취약: 내부 참조 노출
    // return data.clone(); // 안전
}`
  },
  {
    c:"캡슐화",
    q:"setter나 생성자가 외부에서 받은 배열을 private 필드에 그대로 대입하면?",
    o:["문제없다","외부에서 원본 배열을 수정하면 내부 상태도 바뀐다(캡슐화 위반)","자동으로 복사된다","읽기 전용이 된다"],
    a:1,
    e:"외부가 보유한 동일 배열 참조를 그대로 저장하면, 외부가 나중에 그 배열을 수정해 내부 상태를 변경할 수 있다. 대입 시 방어적 복사(arr.clone() 또는 Arrays.copyOf)를 해야 한다.",
    code:`public void setData(int[] in) {
    this.data = in;                 // 취약
    // this.data = in.clone();      // 안전: 방어적 복사
}`
  },
  {
    c:"캡슐화",
    q:"코드에 남아있는 디버그 백도어/DEBUG 플래그가 위험한 이유는?",
    o:["코드가 길어져서","인증 우회 등 비정상 경로를 제공해 보안 통제를 무력화할 수 있어서","컴파일이 느려서","로그가 늘어서"],
    a:1,
    e:"if(DEBUG) 인증우회, 숨겨진 관리자 비밀번호, 테스트용 백도어 등은 운영 환경에 남으면 공격자가 통제를 우회하는 통로가 된다. 배포 전 제거하거나 빌드에서 분리해야 한다.",
    code:`if (user.equals("test") && DEBUG) {
    grantAdmin();  // 제거되지 않은 디버그 백도어
}`
  },
  {
    c:"캡슐화",
    q:"잘못된 세션에 의한 데이터 정보 노출이 발생하는 전형적 원인은?",
    o:["세션 타임아웃이 너무 길어서","사용자별로 분리되어야 할 데이터를 정적(static)/공유 변수에 저장해 다른 세션이 보게 됨","쿠키를 암호화해서","HTTPS를 사용해서"],
    a:1,
    e:"서블릿의 인스턴스 필드나 static 변수에 사용자별 데이터를 저장하면 여러 요청/세션이 같은 인스턴스를 공유하므로 A 사용자의 데이터가 B 사용자에게 노출될 수 있다. 요청/세션 스코프에 저장해야 한다.",
  },
  {
    c:"캡슐화",
    q:"방어적 복사(defensive copy)가 필요한 대상은?",
    o:["int, boolean 같은 기본형","String, Integer 같은 불변 객체","배열, Date, List 같은 가변 객체","상수"],
    a:2,
    e:"불변 객체(String 등)는 공유해도 안전하지만, 배열/Date/컬렉션 같은 가변 객체는 참조 공유 시 외부에서 변경될 수 있어 입력·출력 양쪽에서 방어적 복사가 필요하다.",
  },
  {
    c:"캡슐화",
    q:"다음 중 캡슐화를 강화하는 올바른 게터 구현은?",
    o:["return this.list;","return Collections.unmodifiableList(this.list); 또는 new ArrayList<>(this.list);","public 필드로 직접 노출","return null;"],
    a:1,
    e:"내부 컬렉션을 그대로 반환하면 호출자가 add/remove로 내부 상태를 바꿀 수 있다. 불변 뷰나 복사본을 반환해 내부를 보호한다.",
  },
  {
    c:"캡슐화",
    q:"운영 코드에 남은 '제거되지 않은 디버그 코드'를 점검할 때 주의할 항목이 아닌 것은?",
    o:["하드코딩된 테스트 계정/비밀번호","인증 검사를 건너뛰는 DEBUG 분기","상세 오류를 출력하는 디버그 로깅","정상적인 입력값 검증 로직"],
    a:3,
    e:"입력값 검증은 정상적인 보안 통제로 유지해야 한다. 나머지 항목(테스트 계정, 디버그 분기, 과도한 디버그 출력)은 배포 전 제거 대상이다.",
  },
  {
    c:"캡슐화",
    q:"Python에서 캡슐화를 위해 내부 가변 리스트를 보호하려면 게터에서?",
    o:["self._items 를 그대로 반환","list(self._items) 처럼 복사본을 반환하거나 tuple로 반환","global로 노출","del 후 반환"],
    a:1,
    e:"Python에는 강제 접근 제어가 없지만, 내부 가변 컬렉션을 그대로 반환하면 외부가 변경할 수 있으므로 복사본(list(...))이나 불변 tuple을 반환해 캡슐화를 지킨다.",
  },

  // ===================== API오용 (API Abuse) =====================
  {
    c:"API오용",
    q:"다음 코드의 보안약점은?",
    o:["명령어 삽입(Command Injection)을 허용하는 Runtime.exec 오용","경쟁조건","약한 난수","정보 노출"],
    a:0,
    e:"사용자 입력을 셸 명령 문자열에 연결해 Runtime.exec(\"sh -c ...\")로 실행하면 명령어 삽입이 가능하다. 외부 입력은 인자 배열로 전달하고, 셸을 거치지 않으며, 입력을 검증해야 한다.",
    code:`String cmd = "ping " + userInput;
Runtime.getRuntime().exec(new String[]{"sh","-c",cmd}); // 취약`
  },
  {
    c:"API오용",
    q:"보안에 사용할 난수가 필요할 때 java.util.Random을 쓰면 안 되는 이유는?",
    o:["속도가 느려서","예측 가능한(암호학적으로 안전하지 않은) 시퀀스를 생성하기 때문","음수를 반환해서","스레드 안전하지 않아서"],
    a:1,
    e:"java.util.Random은 선형 합동 생성기로 시드와 출력으로부터 다음 값을 예측할 수 있다. 토큰/세션ID/비밀번호 재설정 등에는 SecureRandom을 사용해야 한다.",
    code:`// 취약
Random r = new Random();
String token = Long.toString(r.nextLong());
// 안전: SecureRandom 사용`
  },
  {
    c:"API오용",
    q:"DNS 조회(역방향 lookup) 결과를 인증/인가 결정의 근거로 삼으면 안 되는 이유는?",
    o:["DNS가 느려서","DNS 응답은 위·변조(스푸핑)될 수 있어 신뢰할 수 없기 때문","IPv6를 지원하지 않아서","캐싱이 안 되어서"],
    a:1,
    e:"호스트명/역방향 DNS는 공격자가 제어하거나 위조할 수 있다. DNS 조회 결과만으로 접근을 허용하면 우회된다. 인증은 검증 가능한 자격증명(인증서, 토큰)에 기반해야 한다.",
  },
  {
    c:"API오용",
    q:"Python에서 사용자 입력을 처리할 때 절대 피해야 하는 함수 호출은?",
    o:["len(user_input)","eval(user_input) / exec(user_input)","user_input.strip()","int(user_input)"],
    a:1,
    e:"eval/exec는 임의의 파이썬 코드를 실행하므로 외부 입력에 사용하면 RCE로 직결된다. 계산이 필요하면 ast.literal_eval이나 명시적 파서를 사용한다.",
    code:`result = eval(request.args['expr'])  # 위험: 임의 코드 실행`
  },
  {
    c:"API오용",
    q:"취약한(deprecated) 암호 알고리즘 사용 사례로 가장 적절한 것은?",
    o:["AES-256-GCM","SHA-256","비밀번호 해싱에 MD5/SHA-1 단순 사용 또는 DES 암호화","PBKDF2/bcrypt 사용"],
    a:2,
    e:"MD5, SHA-1은 충돌 공격에 취약하고 빠른 해시라 비밀번호 저장에 부적합하며, DES는 키 길이가 짧아 무차별 대입에 약하다. 비밀번호는 bcrypt/scrypt/Argon2, 대칭암호는 AES-GCM 등을 사용한다.",
  },
  {
    c:"API오용",
    q:"외부 프로그램을 안전하게 호출하기 위한 권장 방법은?",
    o:["문자열 연결 후 셸로 실행","인자를 배열/리스트로 분리해 셸 없이 실행(ProcessBuilder, subprocess(shell=False))","사용자 입력을 그대로 명령에 넣되 따옴표만 추가","eval로 명령 구성"],
    a:1,
    e:"인자를 배열로 전달하고 셸을 거치지 않으면(예: subprocess.run([...], shell=False)) 셸 메타문자 해석이 없어 명령어 삽입을 차단할 수 있다.",
    code:`# 안전
subprocess.run(["ping","-c","1",host], shell=False)
# 위험
subprocess.run("ping -c 1 "+host, shell=True)`
  },
  {
    c:"API오용",
    q:"MessageDigest로 비밀번호를 저장할 때의 문제와 올바른 대안은?",
    o:["문제없음 / 그대로 사용","빠른 해시+무솔트는 무차별/레인보우테이블에 취약 / bcrypt·Argon2 등 솔트 포함 KDF 사용","Base64로 인코딩하면 안전","ROT13 사용"],
    a:1,
    e:"단순 해시(SHA-256 등)는 너무 빨라 GPU 무차별 대입에 약하고, 솔트가 없으면 레인보우 테이블에 노출된다. 솔트와 작업 인자를 가진 전용 KDF(bcrypt, scrypt, Argon2, PBKDF2)를 사용해야 한다.",
  },
  {
    c:"API오용",
    q:"SSL/TLS 클라이언트에서 인증서 검증을 비활성화(모든 인증서 신뢰)하면 발생하는 위험은?",
    o:["연결 속도 저하","중간자 공격(MITM)에 노출","메모리 누수","인코딩 오류"],
    a:1,
    e:"TrustManager를 모두 신뢰하도록 만들거나 호스트명 검증을 끄면, 공격자가 위조 인증서로 중간에서 트래픽을 가로채고 변조할 수 있다. 기본 검증을 유지해야 한다.",
    code:`// 취약: 모든 인증서 신뢰
TrustManager[] trustAll = new TrustManager[]{ new X509TrustManager(){
  public void checkServerTrusted(X509Certificate[] c, String a){} ... }};`
  },
  {
    c:"API오용",
    q:"hashCode()만으로 객체의 동일성/보안 식별을 판단하면 안 되는 이유는?",
    o:["hashCode는 음수라서","서로 다른 객체가 같은 hashCode를 가질 수 있어(충돌) 식별에 부적합하기 때문","hashCode는 느려서","hashCode는 항상 0이라서"],
    a:1,
    e:"hashCode는 해시 버킷 분배용이며 충돌이 허용된다. 동일성/접근 결정은 equals나 안전한 식별자로 해야 한다. 특히 보안 토큰 비교에 단순 == 대신 시간 일정 비교를 써야 한다.",
  },
  {
    c:"API오용",
    q:"민감 정보(토큰) 비교 시 일반 String.equals 대신 권장되는 것은?",
    o:["== 연산자","길이만 비교","상수 시간 비교(MessageDigest.isEqual / hmac.compare_digest)","toString 비교"],
    a:2,
    e:"일반 비교는 첫 불일치에서 빨리 반환되어 타이밍 공격으로 값을 추론당할 수 있다. MessageDigest.isEqual(Java)이나 hmac.compare_digest(Python) 같은 상수 시간 비교를 사용한다.",
  }
);

window.__QBANK.THEORY.push(
  // ---------- OX ----------
  { type:"OX", cat:"시간상태", q:"TOCTOU는 자원을 검사한 시점과 사용하는 시점 사이의 시간 간격에서 발생하는 경쟁조건이다.", a:true, e:"Time-Of-Check to Time-Of-Use. 검사 후 사용 사이에 자원이 변경되어 발생한다." },
  { type:"OX", cat:"시간상태", q:"중첩 수량자를 가진 정규식은 입력에 따라 지수적 백트래킹을 일으켜 ReDoS의 원인이 될 수 있다.", a:true, e:"^(a+)+$ 같은 evil regex는 특정 입력에서 CPU를 고갈시킨다." },
  { type:"OX", cat:"에러처리", q:"예외의 스택 트레이스를 사용자 화면에 그대로 출력하는 것은 정보 노출 측면에서 안전하다.", a:false, e:"내부 구조/경로/쿼리 등이 노출되므로 사용자에게는 일반 메시지만 보이고 상세는 서버 로그에 남겨야 한다." },
  { type:"OX", cat:"에러처리", q:"빈 catch 블록으로 예외를 삼키면 오류가 은폐되어 비정상 상태로 계속 진행될 수 있다.", a:true, e:"최소한 로깅하거나 적절히 복구/재전파해야 한다." },
  { type:"OX", cat:"코드오류", q:"Java의 try-with-resources는 블록을 벗어날 때 자원을 자동으로 닫아주며 예외 발생 시에도 동작한다.", a:true, e:"AutoCloseable 자원을 선언의 역순으로 자동 close 한다." },
  { type:"OX", cat:"코드오류", q:"Python의 pickle.loads는 신뢰할 수 없는 데이터를 처리하는 데 안전한 함수다.", a:false, e:"pickle 역직렬화는 임의 코드 실행이 가능해 RCE로 이어진다. JSON 등 데이터 포맷을 써야 한다." },
  { type:"OX", cat:"코드오류", q:"\"admin\".equals(name) 형태는 name이 null이어도 NPE가 발생하지 않는다.", a:true, e:"리터럴에 equals를 호출하므로 null-safe 하다." },
  { type:"OX", cat:"캡슐화", q:"public 게터가 내부 private 배열의 참조를 그대로 반환해도 캡슐화는 유지된다.", a:false, e:"가변 배열의 참조 노출은 외부 수정을 허용하므로 clone()/방어적 복사본을 반환해야 한다." },
  { type:"OX", cat:"캡슐화", q:"서블릿의 인스턴스 필드에 사용자별 데이터를 저장하면 여러 요청이 공유하여 다른 사용자에게 노출될 수 있다.", a:true, e:"서블릿은 보통 싱글톤이므로 사용자 데이터는 요청/세션 스코프에 저장해야 한다." },
  { type:"OX", cat:"API오용", q:"세션 토큰 생성에는 java.util.Random보다 SecureRandom을 사용해야 한다.", a:true, e:"java.util.Random은 예측 가능하여 암호학적 용도에 부적합하다." },
  { type:"OX", cat:"API오용", q:"역방향 DNS 조회 결과는 위조될 수 있으므로 인가 결정의 단독 근거로 삼으면 안 된다.", a:true, e:"DNS 응답은 스푸핑 가능하므로 검증 가능한 자격증명에 기반해 인가해야 한다." },

  // ---------- SHORT ----------
  { type:"SHORT", cat:"시간상태", q:"파일을 검사(check)한 시점과 사용(use)하는 시점 사이의 경쟁조건을 가리키는 보안약점의 약어는?", a:"TOCTOU", answers:["TOCTTOU","Time-of-check to time-of-use","TOC TOU"], e:"Time-Of-Check to Time-Of-Use 경쟁조건." },
  { type:"SHORT", cat:"시간상태", q:"중첩 수량자 등으로 정규식 백트래킹이 폭발해 CPU를 고갈시키는 서비스 거부 공격의 약어는?", a:"ReDoS", answers:["Regular expression Denial of Service","정규식 DoS","정규표현식 서비스 거부"], e:"Regular expression Denial of Service." },
  { type:"SHORT", cat:"에러처리", q:"Java에서 객체 생성 없이 예외의 원인을 보존하며 다른 예외로 재전파하는 기법을 무엇이라 하는가? (한글 또는 영어)", a:"예외 체이닝", answers:["exception chaining","예외 연쇄","cause 예외","chained exception"], e:"throw new XException(msg, cause) 형태로 원인 예외를 보존한다." },
  { type:"SHORT", cat:"코드오류", q:"null인 객체 참조에 대해 메소드/필드 접근을 시도해 발생하는 결함의 영문 약어는?", a:"NPE", answers:["NullPointerException","Null Pointer Dereference","널 포인터 역참조","null pointer"], e:"Null Pointer Dereference / NullPointerException." },
  { type:"SHORT", cat:"코드오류", q:"Python에서 파일·소켓 등 자원을 블록 종료 시 자동으로 닫아주는 구문(키워드)은?", a:"with", answers:["with 문","context manager","컨텍스트 매니저","with statement"], e:"with 컨텍스트 매니저는 예외 발생 시에도 자원을 닫는다." },
  { type:"SHORT", cat:"코드오류", q:"Java에서 try() 괄호 안에 AutoCloseable 자원을 선언해 자동 해제하는 구문의 이름은?", a:"try-with-resources", answers:["try with resources","자원과 함께 try","TWR"], e:"Java 7부터 도입된 자동 자원 관리 구문." },
  { type:"SHORT", cat:"코드오류", q:"Java ObjectInputStream에서 역직렬화 허용 클래스를 제한하는 데 사용하는 인터페이스/필터의 이름은? (Java 9+)", a:"ObjectInputFilter", answers:["Serialization Filter","직렬화 필터","ObjectInputFilter allow-list"], e:"역직렬화 시 허용 클래스 화이트리스트를 적용하는 필터." },
  { type:"SHORT", cat:"캡슐화", q:"외부에서 받은 가변 객체(배열 등)를 내부에 저장하거나 반환할 때 원본 대신 복사본을 쓰는 기법을 무엇이라 하는가?", a:"방어적 복사", answers:["defensive copy","defensive copying","방어적 복사본","클론"], e:"입력/출력 양쪽에서 가변 객체를 복사해 내부 상태를 보호한다." },
  { type:"SHORT", cat:"API오용", q:"비밀번호 저장 시 단순 해시 대신 솔트와 작업인자를 갖는 전용 함수를 통칭하는 영문 약어는?", a:"KDF", answers:["Key Derivation Function","bcrypt","Argon2","PBKDF2","scrypt"], e:"Key Derivation Function. bcrypt/scrypt/Argon2/PBKDF2 등." },
  { type:"SHORT", cat:"API오용", q:"Python에서 안전한 표현식 평가가 필요할 때 eval 대신 사용하는 표준 라이브러리 함수는?", a:"ast.literal_eval", answers:["literal_eval","ast.literal_eval()"], e:"리터럴만 안전하게 파싱하여 임의 코드 실행을 막는다." },
  { type:"SHORT", cat:"API오용", q:"토큰 비교 시 타이밍 공격을 막기 위해 Python에서 사용하는 상수 시간 비교 함수는?", a:"hmac.compare_digest", answers:["compare_digest","hmac.compare_digest()","secrets.compare_digest"], e:"첫 불일치에서 일찍 반환하지 않는 상수 시간 비교." },

  // ---------- MC ----------
  { type:"MC", cat:"시간상태", q:"공유 변수에 대한 read-modify-write 경쟁조건을 막는 Java 도구가 아닌 것은?", o:["synchronized","ReentrantLock","AtomicInteger","System.out.println"], a:3, e:"println은 동기화 수단이 아니다. 나머지는 임계영역 보호/원자적 연산을 제공한다." },
  { type:"MC", cat:"에러처리", q:"다음 중 가장 바람직한 사용자 대상 오류 응답은?", o:["전체 스택 트레이스 출력","SQLException 메시지 그대로 출력","'요청을 처리할 수 없습니다' 같은 일반 메시지 + 서버 로그 상세 기록","DB 연결 문자열 출력"], a:2, e:"사용자에게는 일반 메시지, 상세 정보는 서버 로그에만." },
  { type:"MC", cat:"코드오류", q:"신뢰할 수 없는 입력을 받을 때 역직렬화 관련 가장 안전한 선택은?", o:["Java ObjectInputStream.readObject 사용","Python pickle.loads 사용","JSON 등 데이터 포맷 사용 + 스키마 검증","XMLDecoder로 객체 복원"], a:2, e:"객체 그래프를 복원하는 직렬화 대신 데이터 전용 포맷을 사용하고 검증한다." },
  { type:"MC", cat:"코드오류", q:"DB 자원(Connection/Statement/ResultSet) 누수를 막는 가장 좋은 방법은?", o:["GC에 맡긴다","try-with-resources로 자동 close","finally 없이 try 끝에서 close","close 호출 생략"], a:1, e:"try-with-resources는 예외 경로에서도 자동으로 닫는다." },
  { type:"MC", cat:"캡슐화", q:"내부 가변 컬렉션을 외부에 안전하게 노출하는 방법은?", o:["필드를 public으로 공개","내부 참조를 그대로 반환","Collections.unmodifiableList 또는 복사본 반환","static 필드로 공유"], a:2, e:"불변 뷰나 복사본을 반환해 외부 변경을 차단한다." },
  { type:"MC", cat:"API오용", q:"명령 실행 시 명령어 삽입을 방지하는 가장 좋은 방법은?", o:["입력에 따옴표만 덧붙인다","문자열을 셸로 실행한다","인자를 배열로 분리하고 셸을 거치지 않는다(ProcessBuilder/shell=False)","eval로 명령을 만든다"], a:2, e:"셸 메타문자 해석을 제거하는 인자 배열 + 셸 미사용이 핵심이다." },
  { type:"MC", cat:"API오용", q:"다음 중 보안용 난수로 적절한 것은?", o:["java.util.Random","System.currentTimeMillis()","SecureRandom / secrets 모듈","Math.random()"], a:2, e:"암호학적으로 안전한 SecureRandom(Java), secrets(Python)을 사용해야 한다." }
);

// ===== partD =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };

window.__QBANK.QUIZ.push(
  { c:"설계·일반", q:"SW개발보안(시큐어코딩) 의무제가 전자정부 정보화사업에 본격 적용되기 시작한 시점은?", o:["2010년 1월","2012년 12월","2015년 6월","2018년 1월"], a:1, e:"행정안전부 고시 「행정기관 및 공공기관 정보시스템 구축·운영 지침」에 근거하여 2012년 12월부터 SW개발보안이 의무화되었다." },
  { c:"설계·일반", q:"SW개발보안 의무제의 직접적 근거가 되는 행정규칙은?", o:["개인정보 보호법 시행령","정보통신망법 시행규칙","행정기관 및 공공기관 정보시스템 구축·운영 지침(행정안전부 고시)","전자금융거래법 감독규정"], a:2, e:"SW개발보안 적용 의무는 행정안전부 고시인 「행정기관 및 공공기관 정보시스템 구축·운영 지침」에 규정되어 있다." },
  { c:"설계·일반", q:"정보시스템 감리 대상이 되는 사업비 기준으로 통상 제시되는 금액은?", o:["1억원 이상","3억원 이상","5억원 이상","10억원 이상"], a:2, e:"통상 총사업비 5억원 이상 정보화사업이 감리 대상이며, 감리 시 SW개발보안 적용 여부가 점검된다." },
  { c:"설계·일반", q:"보안약점 진단원 자격 취득을 위한 기본교육 이수 시간으로 옳은 것은?", o:["20시간/3일","40시간/5일","60시간/7일","80시간/10일"], a:1, e:"기본교육은 40시간(5일) 과정이며, 수료 후 이수시험에 합격해야 진단원 자격이 부여된다." },
  { c:"설계·일반", q:"보안약점 진단원의 보수교육 주기와 시간으로 옳은 것은?", o:["연 1회 8시간","2년 1회 16시간","연 2회 4시간","3년 1회 24시간"], a:0, e:"진단원 자격 유지를 위해 연 1회 8시간의 보수교육을 이수해야 한다." },
  { c:"설계·일반", q:"보안약점 진단원 신청 경력 요건으로 옳은 것은?", o:["SW개발 3년 또는 진단 2년","SW개발 6년 또는 보안약점 진단 3년","SW개발 10년","보안 자격증 보유만으로 충분"], a:1, e:"통상 SW개발 6년 또는 보안약점 진단 3년 경력에 기본교육 40시간 수료와 이수시험 합격이 요구된다." },
  { c:"설계·일반", q:"진단원 이수시험에서 이론 평가의 구성으로 옳은 것은?", o:["60분/30문항 객관식","100분/15문항 서술형","90분/40문항 단답형","120분/50문항 객관식"], a:0, e:"이론은 60분 동안 30문항 객관식으로 출제되며 전체 배점의 40%를 차지한다." },
  { c:"설계·일반", q:"진단원 이수시험에서 실습 평가의 구성으로 옳은 것은?", o:["60분/30문항 객관식","100분/15문항 서술형","80분/20문항 단답형","120분/10문항 객관식"], a:1, e:"실습은 100분 동안 15문항 서술형으로 출제되며 전체 배점의 60%를 차지한다." },
  { c:"설계·일반", q:"진단원 이수시험의 합격 기준으로 옳은 것은?", o:["종합 60점 이상","종합 70점 이상이며 각 영역 60점 이상","각 영역 70점 이상","종합 80점 이상"], a:1, e:"종합 70점 이상이면서 이론·실습 각 영역에서 과락 기준인 60점 이상을 충족해야 합격한다." },
  { c:"설계·일반", q:"보안약점 진단의 일반적 절차 순서로 옳은 것은?", o:["진단→준비→조치확인→보고","준비→진단→보고→조치확인","보고→진단→준비→조치확인","준비→보고→진단→조치확인"], a:1, e:"진단은 준비 단계에서 대상·기준을 정하고, 진단을 수행한 뒤 보고서를 작성하고, 마지막에 조치 결과를 확인하는 순서로 진행된다." },
  { c:"설계·일반", q:"정적분석 도구가 실제 약점이 아닌 코드를 약점으로 잘못 보고한 경우를 무엇이라 하는가?", o:["정탐(True Positive)","오탐(False Positive)","미탐(False Negative)","진탐(True Negative)"], a:1, e:"오탐(False Positive)은 실제로는 안전한 코드를 약점으로 잘못 보고한 경우이며, 진단원이 수동으로 검증해 걸러내야 한다." },
  { c:"설계·일반", q:"실제 존재하는 약점을 도구가 탐지하지 못하고 놓친 경우를 무엇이라 하는가?", o:["정탐","오탐","미탐(False Negative)","과탐"], a:2, e:"미탐(False Negative)은 실제 약점을 탐지하지 못한 경우로, 정적분석 도구의 가장 위험한 한계 중 하나이다." },
  { c:"설계·일반", q:"소스코드를 실행하지 않고 분석하는 진단 방식은?", o:["DAST(동적분석)","SAST(정적분석)","IAST","퍼징(Fuzzing)"], a:1, e:"SAST(Static Application Security Testing)는 소스코드나 바이트코드를 실행하지 않고 분석하여 보안약점을 찾는 정적분석 기법이다." },
  { c:"설계·일반", q:"실행 중인 애플리케이션에 요청을 보내 취약점을 탐지하는 진단 방식은?", o:["SAST","DAST(동적분석)","코드리뷰","컴파일 검사"], a:1, e:"DAST(Dynamic Application Security Testing)는 실행 중인 애플리케이션을 외부에서 공격하듯 점검하는 동적분석 기법이다." },
  { c:"설계·일반", q:"소프트웨어 보안약점의 표준 분류 체계로, 약점 유형에 식별번호를 부여한 것은?", o:["CVE","CWE","CVSS","OWASP Top 10"], a:1, e:"CWE(Common Weakness Enumeration)는 소프트웨어 약점 유형을 분류·식별하는 표준 체계이다." },
  { c:"설계·일반", q:"공개적으로 알려진 개별 보안취약점에 부여되는 고유 식별자는?", o:["CWE","CVE","CWSS","SANS Top 25"], a:1, e:"CVE(Common Vulnerabilities and Exposures)는 개별적으로 공개된 보안취약점에 부여하는 고유 식별번호이다." },
  { c:"설계·일반", q:"구현단계 시큐어코딩 7대 분류에 해당하지 않는 것은?", o:["입력데이터 검증 및 표현","보안기능","에러처리","네트워크 토폴로지 설계"], a:3, e:"구현단계 7대 분류는 입력데이터 검증 및 표현, 보안기능, 시간 및 상태, 에러처리, 코드오류, 캡슐화, API오용이다. 네트워크 토폴로지 설계는 포함되지 않는다." },
  { c:"설계·일반", q:"설계단계 보안설계기준의 4대 분류에 해당하지 않는 것은?", o:["입력데이터 검증 및 표현","보안기능","에러처리","캡슐화"], a:3, e:"설계단계 보안설계기준은 입력데이터 검증 및 표현, 보안기능, 에러처리, 세션통제의 4분류이다. 캡슐화는 구현단계 분류이다." },
  { c:"설계·일반", q:"SQL 삽입(SQL Injection)을 예방하기 위한 설계단계 보안설계기준 항목은?", o:["DBMS 조회 및 결과 검증","암호키 관리","세션 통제","예외 처리"], a:0, e:"DBMS 조회 및 결과 검증은 데이터베이스 질의 시 입력값을 검증·필터링하도록 하는 설계기준으로 SQL 삽입을 예방한다." },
  { c:"설계·일반", q:"사용자가 업로드한 파일로 인한 위험을 막기 위한 설계기준 항목은?", o:["인증 대상 및 방식","업로드·다운로드 파일 검증","암호 연산","중요정보 전송"], a:1, e:"업로드·다운로드 파일 검증은 파일 확장자·크기·경로 등을 점검하여 위험한 파일 업로드 약점을 예방하는 설계기준이다." },
  { c:"설계·일반", q:"하드코딩된 비밀번호·암호키 노출을 예방하는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:1, e:"비밀번호 관리, 암호키 관리 등은 보안기능 분류에 속하며 하드코딩 노출 등을 방지한다." },
  { c:"설계·일반", q:"오류 메시지를 통한 내부 정보 노출을 막는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:2, e:"예외처리 및 오류메시지 관리 등은 에러처리 분류에 속하며 시스템 정보가 외부에 노출되지 않도록 한다." },
  { c:"설계·일반", q:"세션 ID 추측·고정 공격을 예방하는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:3, e:"세션통제 분류는 세션 생성·관리·만료 정책을 통해 세션 하이재킹·고정 등의 약점을 예방한다." },
  { c:"설계·일반", q:"크로스사이트 스크립트(XSS) 약점에 대응하는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:0, e:"XSS는 입력값 검증과 출력 인코딩 미흡에서 발생하므로 '입력데이터 검증 및 표현' 분류로 대응한다." },
  { c:"설계·일반", q:"운영체제 명령어 삽입(Command Injection)을 예방하는 설계기준 항목은?", o:["명령어 입력값 검증","암호키 관리","세션 만료","비밀번호 관리"], a:0, e:"시스템 명령 실행 시 입력값을 검증하는 '명령어 입력값 검증' 항목으로 명령어 삽입 약점을 예방한다." },
  { c:"설계·일반", q:"진단 결과 보고서에서 약점의 발견 여부를 표기하는 방식으로 일반적인 것은?", o:["O/X","Y/N(발견/미발견)","합/불","1/0 비율"], a:1, e:"진단 결과는 통상 항목별로 Y(발견)/N(미발견)으로 표기하며, 발견 시 정탐 여부와 조치방안을 함께 기재한다." },
  { c:"설계·일반", q:"보안약점과 보안취약점의 관계에 대한 설명으로 가장 옳은 것은?", o:["둘은 완전히 동일한 개념이다","보안약점은 잠재적 원인, 보안취약점은 실제 악용 가능한 결함이다","보안취약점이 보안약점의 부분집합이다","보안약점은 운영단계에만 존재한다"], a:1, e:"보안약점(weakness)은 취약점을 유발할 수 있는 잠재적 원인이며, 이것이 실제 공격에 악용될 수 있을 때 보안취약점(vulnerability)이 된다." },
  { c:"설계·일반", q:"SDLC 단계 중 보안설계기준(보안요구항목)이 적용되는 단계는?", o:["요구사항 단계","설계 단계","구현 단계","시험 단계"], a:1, e:"보안설계기준은 설계 단계에서 적용되며, 구현 단계에서는 이를 시큐어코딩 약점 점검으로 구체화한다." },
  { c:"설계·일반", q:"정적분석 도구의 일반적 한계로 보기 어려운 것은?", o:["오탐 발생","미탐 발생","실행 환경 의존 약점 탐지 어려움","컴파일 없이 분석 불가"], a:3, e:"많은 SAST 도구는 소스코드 자체를 분석하므로 반드시 컴파일이 필요한 것은 아니다. 오탐·미탐, 런타임 의존 약점 탐지의 어려움은 실제 한계이다." },
  { c:"설계·일반", q:"진단원이 도구 결과를 수동 검증하는 가장 중요한 이유는?", o:["도구 라이선스 비용 절감","정탐과 오탐을 구분하기 위해","코드 줄 수 측정","컴파일 시간 단축"], a:1, e:"도구는 오탐·미탐을 포함하므로 진단원이 결과를 수동 검증하여 정탐/오탐을 판정하는 것이 핵심 역할이다." },
  { c:"설계·일반", q:"중요정보를 평문으로 저장·전송하지 않도록 하는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:1, e:"중요정보 저장·전송, 암호 연산, 암호키 관리 등은 보안기능 분류에 속한다." },
  { c:"설계·일반", q:"LDAP 삽입 약점을 예방하기 위한 설계기준 항목으로 가장 적절한 것은?", o:["LDAP 조회 및 결과 검증","세션 만료 설정","오류메시지 통제","암호 연산"], a:0, e:"LDAP 질의에 사용되는 입력값을 검증하는 'LDAP 조회 및 결과 검증' 항목으로 LDAP 삽입을 예방한다." },
  { c:"설계·일반", q:"XML 삽입(XML Injection)·XPath 삽입을 예방하는 설계기준 항목은?", o:["XML 조회 및 결과 검증","비밀번호 관리","중요자원 접근통제","예외처리"], a:0, e:"XML/XPath 질의에 사용되는 입력값을 검증하는 'XML 조회 및 결과 검증' 항목으로 관련 삽입 약점을 예방한다." },
  { c:"설계·일반", q:"SW개발보안 및 진단원 제도 운영을 주관하는 기관 조합으로 옳은 것은?", o:["과학기술정보통신부·NIA","행정안전부·KISA","금융위원회·금융보안원","개인정보보호위원회·KISA"], a:1, e:"SW개발보안 제도는 행정안전부가 주관하고 KISA(한국인터넷진흥원)가 운영·교육·시험을 지원한다." },
  { c:"설계·일반", q:"진단원 이수시험 시 응시자에게 제공되는 것으로 옳은 것은?", o:["완성된 정답 코드","보안약점 '명칭(목록)'","취약점 익스플로잇 도구","감리 결과서 양식 전체"], a:1, e:"실습 시험에서는 점검 대상 보안약점의 '명칭'이 제공되며, 응시자는 해당 약점의 정·오탐을 분석하고 서술한다." },
  { c:"설계·일반", q:"인증 시도 횟수 제한·계정 잠금 등을 규정하는 설계기준 항목은?", o:["인증 수행 제한","암호키 관리","XML 조회 검증","세션 생성"], a:0, e:"'인증 수행 제한' 항목은 반복적인 인증 시도(무차별 대입)에 대해 시도 횟수 제한 등을 두도록 규정한다." }
);

window.__QBANK.THEORY.push(
  { type:"OX", cat:"법령", q:"SW개발보안 의무제는 2012년 12월부터 전자정부 정보화사업에 적용되기 시작하였다.", a:true, e:"행정안전부 고시에 근거하여 2012년 12월부터 SW개발보안이 의무화되었다." },
  { type:"OX", cat:"법령", q:"SW개발보안 의무제의 근거는 「개인정보 보호법」이다.", a:false, e:"근거는 행정안전부 고시 「행정기관 및 공공기관 정보시스템 구축·운영 지침」이다." },
  { type:"OX", cat:"법령", q:"통상 총사업비 5억원 이상 정보화사업이 감리 대상이며 SW개발보안 적용 여부가 점검된다.", a:true, e:"5억원 이상 사업이 감리 대상이 되는 것이 일반적 기준이다." },
  { type:"OX", cat:"법령", q:"보안약점 진단원의 보수교육은 2년에 1회 이수하면 된다.", a:false, e:"보수교육은 연 1회 8시간을 이수해야 한다." },
  { type:"OX", cat:"법령", q:"진단원 기본교육은 40시간(5일) 과정이다.", a:true, e:"기본교육은 40시간(5일)으로 운영되며 수료 후 이수시험에 합격해야 한다." },
  { type:"OX", cat:"법령", q:"진단원 이수시험은 종합 70점 이상이고 각 영역이 60점 이상이어야 합격한다.", a:true, e:"종합 70점 이상, 이론·실습 각 60점 이상(과락 기준)을 충족해야 합격한다." },
  { type:"OX", cat:"법령", q:"진단원 이수시험은 종합 60점만 넘으면 영역별 점수와 무관하게 합격한다.", a:false, e:"종합 70점 이상이어야 하고 각 영역도 60점 이상(과락 없음)이어야 한다." },
  { type:"OX", cat:"개념", q:"보안약점은 보안취약점을 유발할 수 있는 잠재적 원인을 의미한다.", a:true, e:"보안약점(weakness)이 실제 악용 가능하게 되면 보안취약점(vulnerability)이 된다." },
  { type:"OX", cat:"개념", q:"오탐(False Positive)은 실제 약점을 도구가 놓친 경우를 말한다.", a:false, e:"실제 약점을 놓친 경우는 미탐(False Negative)이며, 오탐은 안전한 코드를 약점으로 잘못 보고한 경우이다." },
  { type:"OX", cat:"개념", q:"SAST는 애플리케이션을 실행하지 않고 소스코드를 분석하는 정적분석 기법이다.", a:true, e:"SAST는 소스코드·바이트코드를 실행하지 않고 분석한다." },
  { type:"OX", cat:"개념", q:"DAST는 소스코드 없이 실행 중인 애플리케이션을 외부에서 점검할 수 있다.", a:true, e:"DAST는 실행 중인 애플리케이션에 요청을 보내 취약점을 탐지하므로 소스코드가 없어도 수행할 수 있다." },
  { type:"OX", cat:"개념", q:"CWE는 개별적으로 공개된 보안취약점에 부여하는 고유 식별번호이다.", a:false, e:"개별 취약점 식별번호는 CVE이며, CWE는 약점 유형을 분류하는 체계이다." },
  { type:"OX", cat:"개념", q:"구현단계 시큐어코딩은 7대 분류 체계로 약점을 구분한다.", a:true, e:"구현단계는 입력데이터 검증 및 표현, 보안기능, 시간 및 상태, 에러처리, 코드오류, 캡슐화, API오용의 7대 분류로 구분한다." },
  { type:"OX", cat:"진단", q:"진단 절차는 일반적으로 준비→진단→보고→조치확인 순서로 진행된다.", a:true, e:"준비 단계에서 대상과 기준을 정하고 진단·보고를 거쳐 조치 결과를 확인한다." },
  { type:"OX", cat:"진단", q:"정적분석 도구의 결과는 모두 정탐이므로 수동 검증이 필요 없다.", a:false, e:"도구 결과에는 오탐·미탐이 포함되므로 진단원의 수동 검증이 필수이다." },
  { type:"OX", cat:"설계", q:"설계단계 보안설계기준은 입력데이터 검증 및 표현, 보안기능, 에러처리, 세션통제의 4분류로 구성된다.", a:true, e:"설계단계는 4대 분류로 구성되며 구현단계의 7대 분류와 구분된다." },
  { type:"OX", cat:"설계", q:"세션 통제는 설계단계 보안설계기준의 4대 분류 중 하나이다.", a:true, e:"세션통제는 세션 생성·관리·만료를 통해 세션 관련 약점을 예방하는 설계기준 분류이다." },
  { type:"OX", cat:"설계", q:"캡슐화는 설계단계 보안설계기준의 4대 분류에 포함된다.", a:false, e:"캡슐화는 구현단계 7대 분류에 속하며, 설계단계 4대 분류에는 포함되지 않는다." },

  { type:"SHORT", cat:"법령", q:"SW개발보안 의무제가 본격 적용되기 시작한 연도와 월을 쓰시오. (예: 0000년 00월)", a:"2012년 12월", answers:["2012.12","2012년 12월","2012-12"], e:"행정안전부 고시에 근거하여 2012년 12월부터 의무화되었다." },
  { type:"SHORT", cat:"법령", q:"SW개발보안 의무 적용의 직접적 근거가 되는 행정안전부 고시의 명칭을 쓰시오.", a:"행정기관 및 공공기관 정보시스템 구축·운영 지침", answers:["정보시스템 구축·운영 지침","행정기관 및 공공기관 정보시스템 구축 운영 지침","구축운영지침"], e:"해당 고시에 SW개발보안 적용 의무가 규정되어 있다." },
  { type:"SHORT", cat:"법령", q:"진단원 기본교육의 총 이수 시간을 숫자(시간)로 쓰시오.", a:"40시간", answers:["40","40시간","40h"], e:"기본교육은 40시간(5일) 과정이다." },
  { type:"SHORT", cat:"법령", q:"진단원 보수교육의 연간 이수 시간을 쓰시오.", a:"8시간", answers:["8","8시간"], e:"진단원은 연 1회 8시간의 보수교육을 이수해야 한다." },
  { type:"SHORT", cat:"법령", q:"SW개발보안 제도의 운영·교육·시험을 지원하는 기관의 약칭을 쓰시오.", a:"KISA", answers:["KISA","한국인터넷진흥원","키사"], e:"행정안전부가 주관하고 KISA(한국인터넷진흥원)가 교육·시험 등을 지원한다." },
  { type:"SHORT", cat:"개념", q:"실제로는 안전한 코드를 도구가 약점으로 잘못 보고한 경우를 한글 용어로 쓰시오.", a:"오탐", answers:["오탐","False Positive","FP"], e:"오탐(False Positive)은 안전한 코드를 약점으로 잘못 보고한 경우이다." },
  { type:"SHORT", cat:"개념", q:"실제 존재하는 약점을 도구가 탐지하지 못하고 놓친 경우를 한글 용어로 쓰시오.", a:"미탐", answers:["미탐","False Negative","FN"], e:"미탐(False Negative)은 실제 약점을 탐지하지 못한 경우이다." },
  { type:"SHORT", cat:"개념", q:"소프트웨어 약점 유형을 분류·식별하는 표준 체계의 영문 약자를 쓰시오.", a:"CWE", answers:["CWE","Common Weakness Enumeration"], e:"CWE(Common Weakness Enumeration)는 약점 유형 분류 표준이다." },
  { type:"SHORT", cat:"개념", q:"개별적으로 공개된 보안취약점에 부여하는 고유 식별번호의 영문 약자를 쓰시오.", a:"CVE", answers:["CVE","Common Vulnerabilities and Exposures"], e:"CVE는 공개된 개별 취약점의 고유 식별자이다." },
  { type:"SHORT", cat:"개념", q:"소스코드를 실행하지 않고 분석하는 보안 점검 기법의 영문 약자를 쓰시오.", a:"SAST", answers:["SAST","정적분석","Static Application Security Testing"], e:"SAST는 정적분석 기법이다." },
  { type:"SHORT", cat:"진단", q:"진단 결과 보고서에서 약점의 발견 여부를 표기하는 두 가지 기호를 쓰시오. (예: A/B)", a:"Y/N", answers:["Y/N","Y N","발견/미발견"], e:"통상 항목별로 Y(발견)/N(미발견)으로 표기한다." },
  { type:"SHORT", cat:"진단", q:"진단원이 진단 후 발견된 약점의 조치를 요청하기 위해 작성하는 문서의 명칭을 쓰시오.", a:"보완요청서", answers:["보완요청서","조치요청서"], e:"진단원은 진단보고서와 함께 발견 약점에 대한 보완요청서를 작성한다." },
  { type:"SHORT", cat:"설계", q:"SQL 삽입 약점에 대응하는 설계단계 보안설계기준의 4대 분류명을 쓰시오.", a:"입력데이터 검증 및 표현", answers:["입력데이터 검증 및 표현","입력값 검증 및 표현","입력데이터검증및표현"], e:"SQL 삽입·XSS 등은 입력데이터 검증 및 표현 분류로 대응한다." },
  { type:"SHORT", cat:"설계", q:"오류 메시지를 통한 내부 정보 노출을 예방하는 설계기준 4대 분류명을 쓰시오.", a:"에러처리", answers:["에러처리","오류처리","예외처리"], e:"에러처리 분류는 오류메시지·예외처리를 통제하여 정보 노출을 막는다." },
  { type:"SHORT", cat:"설계", q:"세션 ID 추측·고정 공격을 예방하는 설계기준 4대 분류명을 쓰시오.", a:"세션통제", answers:["세션통제","세션 통제"], e:"세션통제 분류는 세션 생성·관리·만료를 규정한다." },

  { type:"MC", cat:"법령", q:"진단원 이수시험의 이론 평가 배점 비율로 옳은 것은?", o:["40%","60%","50%","70%"], a:0, e:"이론(객관식)은 전체 배점의 40%이며 실습(서술형)이 60%이다." },
  { type:"MC", cat:"법령", q:"진단원 이수시험의 실습 평가 구성으로 옳은 것은?", o:["60분/30문항 객관식","100분/15문항 서술형","90분/20문항 단답형","120분/40문항 객관식"], a:1, e:"실습은 100분/15문항 서술형으로 배점의 60%를 차지한다." },
  { type:"MC", cat:"법령", q:"진단원 자격 신청 시 경력 요건으로 옳은 것은?", o:["SW개발 3년","SW개발 6년 또는 보안약점 진단 3년","보안 자격증만 보유","SW개발 1년 + 교육 수료"], a:1, e:"SW개발 6년 또는 보안약점 진단 3년 경력이 요구된다." },
  { type:"MC", cat:"개념", q:"SDLC에서 보안설계기준(보안요구항목)이 주로 적용되는 단계는?", o:["요구사항 단계","설계 단계","시험 단계","운영 단계"], a:1, e:"보안설계기준은 설계 단계에서 적용되며 구현 단계에서 시큐어코딩 점검으로 구체화된다." },
  { type:"MC", cat:"개념", q:"다음 중 구현단계 시큐어코딩 7대 분류에 속하지 않는 것은?", o:["시간 및 상태","코드오류","API오용","세션통제"], a:3, e:"세션통제는 설계단계 4대 분류 항목이며, 구현 7대 분류는 입력검증/보안기능/시간및상태/에러처리/코드오류/캡슐화/API오용이다." },
  { type:"MC", cat:"개념", q:"DAST(동적분석)에 대한 설명으로 옳은 것은?", o:["소스코드 정적 분석만 수행한다","실행 중인 애플리케이션을 외부에서 점검한다","컴파일러 경고만 수집한다","주석을 분석한다"], a:1, e:"DAST는 실행 중인 애플리케이션에 입력을 보내 취약점을 탐지한다." },
  { type:"MC", cat:"진단", q:"정적분석 도구 결과에 대한 진단원의 핵심 역할은?", o:["라이선스 관리","정탐/오탐 판정을 위한 수동 검증","코드 컴파일","서버 운영"], a:1, e:"도구는 오탐·미탐을 포함하므로 진단원이 결과를 검증해 정탐/오탐을 판정한다." },
  { type:"MC", cat:"진단", q:"진단 절차의 일반적 순서로 옳은 것은?", o:["진단→준비→보고→조치확인","준비→진단→보고→조치확인","보고→준비→진단→조치확인","조치확인→진단→준비→보고"], a:1, e:"준비→진단→보고→조치확인 순서로 진행된다." },
  { type:"MC", cat:"설계", q:"업로드된 위험 파일로 인한 약점을 예방하는 설계기준 항목은?", o:["업로드·다운로드 파일 검증","암호키 관리","세션 만료","오류메시지 통제"], a:0, e:"파일 확장자·크기·경로 등을 점검하는 업로드·다운로드 파일 검증 항목으로 예방한다." },
  { type:"MC", cat:"설계", q:"하드코딩된 암호키·비밀번호 노출을 예방하는 설계기준 분류는?", o:["입력데이터 검증 및 표현","보안기능","에러처리","세션통제"], a:1, e:"비밀번호 관리·암호키 관리·암호 연산 등은 보안기능 분류에 속한다." },
  { type:"MC", cat:"설계", q:"LDAP 삽입 약점을 예방하는 설계기준 항목으로 가장 적절한 것은?", o:["LDAP 조회 및 결과 검증","세션 생성","인증 수행 제한","예외처리"], a:0, e:"LDAP 질의 입력값을 검증하는 'LDAP 조회 및 결과 검증' 항목으로 예방한다." },
  { type:"MC", cat:"설계", q:"무차별 대입(brute force) 공격에 대응하기 위한 설계기준 항목은?", o:["인증 수행 제한","중요정보 전송","XML 조회 검증","파일 다운로드 검증"], a:0, e:"'인증 수행 제한' 항목은 인증 시도 횟수 제한·계정 잠금 등을 규정한다." }
);

// ===== partE_time =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  {
    c: "시간상태",
    q: "다음 Java 코드에서 발생하는 대표적인 시간 및 상태 관련 보안약점은 무엇인가?",
    o: [
      "경쟁 조건(Race Condition, CWE-362)",
      "SQL 삽입(CWE-89)",
      "부적절한 인증(CWE-287)",
      "경로 조작(CWE-22)"
    ],
    a: 0,
    e: "count++ 는 읽기-증가-쓰기의 비원자적 연산이므로 여러 스레드가 동시에 접근하면 갱신이 유실된다. 이는 CWE-362 동시 실행에서의 부적절한 자원 접근(Race Condition)에 해당한다. AtomicInteger나 synchronized로 원자성을 보장해야 한다.",
    code: `public class Counter {
    private int count = 0;
    // 여러 스레드가 동시에 호출
    public void increment() {
        count++; // 비원자적: read-modify-write
    }
}`
  },
  {
    c: "시간상태",
    q: "TOCTOU(Time-of-Check to Time-of-Use) 취약점을 가장 정확하게 설명한 것은?",
    o: [
      "조건을 검사한 시점과 그 자원을 실제로 사용하는 시점 사이에 자원 상태가 바뀔 수 있는 결함",
      "사용자 입력을 검증하지 않고 SQL에 연결하는 결함",
      "암호 키를 하드코딩하는 결함",
      "세션 쿠키에 Secure 속성을 누락하는 결함"
    ],
    a: 0,
    e: "TOCTOU(CWE-367)는 검사 시점(예: 파일 존재/권한 확인)과 사용 시점(예: 파일 열기) 사이의 시간차를 이용해 공격자가 대상 자원을 교체(심볼릭 링크 등)할 수 있는 경쟁 조건 결함이다.",
    code: `# 취약: 검사와 사용 사이에 파일이 바뀔 수 있음
import os
if os.access("/tmp/data", os.W_OK):  # TIME OF CHECK
    with open("/tmp/data", "w") as f:  # TIME OF USE
        f.write("payload")`
  },
  {
    c: "시간상태",
    q: "다음 파이썬 파일 처리 코드의 TOCTOU 문제를 안전하게 해결하는 방법으로 가장 적절한 것은?",
    o: [
      "os.access()로 먼저 검사한 뒤 open() 한다",
      "os.path.exists()로 존재 여부를 여러 번 반복 확인한다",
      "검사를 생략하고 open()의 예외를 처리하거나 O_CREAT|O_EXCL 등 원자적 연산을 사용한다",
      "파일 권한을 0777로 설정한 뒤 처리한다"
    ],
    a: 2,
    e: "TOCTOU(CWE-367)는 검사와 사용을 분리하면 항상 경쟁 창이 생긴다. os.access() 선검사는 오히려 안티패턴이다. 검사를 생략하고 open()을 바로 수행하며 예외를 처리하거나, os.open(path, O_CREAT|O_EXCL) 처럼 검사와 생성을 하나의 원자적 연산으로 묶는 것이 올바른 해결책이다."
  },
  {
    c: "시간상태",
    q: "다음 Java double-checked locking 코드에서 field에 volatile을 붙이지 않으면 발생할 수 있는 문제는?",
    o: [
      "다른 스레드가 완전히 초기화되지 않은 객체 참조를 볼 수 있다",
      "컴파일 오류가 발생한다",
      "락이 절대 해제되지 않는다",
      "GC가 즉시 객체를 회수한다"
    ],
    a: 0,
    e: "volatile이 없으면 객체 생성(메모리 할당, 생성자 실행, 참조 대입)의 명령어 재정렬로 인해 다른 스레드가 참조는 non-null이지만 생성자가 끝나지 않은 객체를 관찰할 수 있다. 이것이 CWE-609 Double-Checked Locking 결함이며, 필드를 volatile로 선언해야 한다.",
    code: `class Singleton {
    private static Singleton instance; // volatile 필요
    static Singleton get() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null)
                    instance = new Singleton();
            }
        }
        return instance;
    }
}`
  },
  {
    c: "시간상태",
    q: "웹 애플리케이션에서 세션 고정(Session Fixation, CWE-384)을 방지하는 가장 확실한 방법은?",
    o: [
      "로그인 성공 직후 세션 ID를 새로 발급(재생성)한다",
      "세션 타임아웃을 24시간으로 늘린다",
      "세션 ID를 URL 파라미터로 전달한다",
      "로그인 폼에 CAPTCHA를 추가한다"
    ],
    a: 0,
    e: "세션 고정(CWE-384)은 공격자가 미리 만든 세션 ID를 피해자에게 사용하게 한 뒤, 인증 후 그 세션을 탈취하는 공격이다. 핵심 방어는 인증(로그인) 성공 시점에 세션 ID를 무효화하고 새로 발급하는 것이다(예: HttpServletRequest.changeSessionId()).",
    code: `// 방어: 로그인 성공 후 세션 재생성
request.getSession().invalidate();
HttpSession newSession = request.getSession(true);
newSession.setAttribute("user", user);`
  },
  {
    c: "시간상태",
    q: "여러 스레드가 공유하는 java.util.HashMap을 동기화 없이 put/get 하면 발생할 수 있는 문제로 가장 거리가 먼 것은?",
    o: [
      "무한 루프(특정 JDK 버전에서 리사이즈 중 링크 순환)",
      "데이터 손실 및 일관성 붕괴",
      "컴파일 시점 에러로 즉시 실패",
      "예측 불가능한 결과(비결정적 동작)"
    ],
    a: 2,
    e: "HashMap은 스레드 안전하지 않아 동시 접근 시 데이터 유실, 일관성 붕괴, 비결정적 결과가 발생하며, 구버전 JDK에서는 리사이즈 중 링크 순환으로 무한 루프(CPU 100%)도 발생했다. 그러나 컴파일 에러는 발생하지 않는다. 해결책은 ConcurrentHashMap 사용이다.",
    code: `// 취약: 여러 스레드가 공유
Map<String,Integer> map = new HashMap<>();
// 스레드1, 스레드2가 동시에
map.put(k, map.getOrDefault(k,0)+1);`
  },
  {
    c: "시간상태",
    q: "다음 중 데드락(교착 상태, CWE-833)을 유발하는 전형적인 상황은?",
    o: [
      "두 스레드가 서로 다른 순서로 두 개의 락을 획득하려 한다",
      "모든 스레드가 항상 동일한 순서로 락을 획득한다",
      "락을 사용하지 않고 불변 객체만 공유한다",
      "단일 스레드에서 재진입 가능한 락을 사용한다"
    ],
    a: 0,
    e: "데드락(CWE-833)은 스레드 A가 락1을 잡고 락2를 기다리고, 스레드 B가 락2를 잡고 락1을 기다릴 때처럼 순환 대기가 형성될 때 발생한다. 모든 스레드가 항상 같은 순서로 락을 획득하도록 강제하면 순환 대기가 제거되어 데드락이 예방된다.",
    code: `// 데드락 위험: 락 획득 순서가 반대
// 스레드A: synchronized(lockA){ synchronized(lockB){...} }
// 스레드B: synchronized(lockB){ synchronized(lockA){...} }`
  },
  {
    c: "시간상태",
    q: "Java에서 여러 스레드가 난수를 안전하고 효율적으로 생성하려 할 때 가장 적절한 것은?",
    o: [
      "하나의 java.util.Random 인스턴스를 모든 스레드가 공유한다",
      "ThreadLocalRandom.current().nextInt() 를 사용한다",
      "각 호출마다 new Random() 을 생성한다",
      "System.currentTimeMillis()를 시드로 매번 새 Random을 만든다"
    ],
    a: 1,
    e: "단일 java.util.Random을 공유하면 내부 seed의 CAS 경합으로 성능이 저하되고, new Random()을 매번 만들면 유사한 시드로 예측 가능한 값이 나올 수 있다. ThreadLocalRandom은 스레드별 독립 상태를 유지해 경합 없이 안전하다.",
    code: `import java.util.concurrent.ThreadLocalRandom;
int r = ThreadLocalRandom.current().nextInt(100);`
  },
  {
    c: "시간상태",
    q: "check-then-act(검사 후 행동) 패턴이 원자성 위반을 일으키는 이유로 옳은 것은?",
    o: [
      "검사와 행동이 별개의 연산이라 그 사이에 다른 스레드가 상태를 바꿀 수 있기 때문",
      "검사 연산 자체가 CPU를 과도하게 사용하기 때문",
      "행동 연산이 항상 예외를 던지기 때문",
      "검사와 행동이 같은 명령어로 컴파일되기 때문"
    ],
    a: 0,
    e: "if(map.containsKey(k)) map.put(k,v) 처럼 검사와 행동이 분리되면, 두 연산 사이의 창에서 다른 스레드가 상태를 변경할 수 있다. 이는 CWE-362 경쟁 조건의 대표 패턴이다. putIfAbsent 같은 원자적 복합 연산을 사용해야 한다."
  },
  {
    c: "시간상태",
    q: "다음 Java 코드를 스레드 안전하게 만드는 가장 올바른 수정은?",
    o: [
      "map.putIfAbsent(key, value) 같은 원자적 연산으로 대체한다",
      "map 변수를 static으로 바꾼다",
      "get과 put 사이에 Thread.sleep(1)을 넣는다",
      "value를 final로 선언한다"
    ],
    a: 0,
    e: "containsKey 검사와 put 행동 사이에 경쟁 창이 있어 두 스레드가 모두 put을 수행할 수 있다(CWE-362). ConcurrentHashMap의 putIfAbsent 또는 computeIfAbsent 같은 단일 원자적 연산으로 검사와 행동을 병합해야 한다.",
    code: `ConcurrentHashMap<String,Object> map = ...;
// 취약
if (!map.containsKey(k)) {
    map.put(k, create());
}`
  },
  {
    c: "시간상태",
    q: "부적절한 잠금(Improper Locking, CWE-667)의 예로 가장 적절한 것은?",
    o: [
      "공유 자원의 일부 접근 경로에만 락을 걸고 다른 경로는 락 없이 접근한다",
      "모든 공유 자원 접근에 동일한 락을 일관되게 사용한다",
      "락 없이 불변(immutable) 객체를 읽는다",
      "지역 변수를 synchronized 블록 안에서만 사용한다"
    ],
    a: 0,
    e: "동일 공유 자원을 어떤 곳에서는 락을 걸고 어떤 곳에서는 락 없이 접근하면 동기화가 깨진다(CWE-667). 공유 상태에 대한 모든 접근 경로에 대해 일관된 잠금 규율을 적용해야 한다."
  },
  {
    c: "시간상태",
    q: "다음 Python 코드에서 threading.Lock을 with 문 없이 acquire()만 하고 예외가 발생하면 생기는 문제는?",
    o: [
      "예외 경로에서 release가 호출되지 않아 락이 영구 점유되어 다른 스레드가 무한 대기(데드락)한다",
      "GIL이 자동으로 락을 해제해 준다",
      "락이 자동으로 재진입되어 문제가 없다",
      "인터프리터가 즉시 종료된다"
    ],
    a: 0,
    e: "acquire() 후 임계 구역에서 예외가 발생하면 release()에 도달하지 못해 락이 해제되지 않고, 이후 acquire를 시도하는 스레드가 영원히 대기한다(CWE-667/CWE-833). with lock: 구문이나 try/finally로 반드시 해제를 보장해야 한다.",
    code: `lock.acquire()
do_work()   # 예외 시 아래 release 미도달
lock.release()
# 올바름: with lock: do_work()`
  },
  {
    c: "시간상태",
    q: "무한 루프로 인한 자원 고갈(CWE-835)을 유발할 수 있는 코드로 가장 적절한 것은?",
    o: [
      "종료 조건이 외부 입력에 의존하지만 그 값이 절대 갱신되지 않는 while 루프",
      "고정된 배열 길이만큼 도는 for 루프",
      "명확한 카운터 상한을 가진 반복문",
      "예외 발생 시 break로 빠져나오는 루프"
    ],
    a: 0,
    e: "루프 종료 조건이 결코 참(또는 거짓)이 될 수 없으면 무한 루프가 되어 CPU/스레드/메모리가 고갈된다(CWE-835). 특히 종료 플래그가 다른 스레드에서 갱신되지만 volatile이 아니어서 가시성이 없거나, 갱신 코드에 도달하지 못하는 경우가 흔하다."
  },
  {
    c: "시간상태",
    q: "다음 중 스레드 간 데이터 누출(민감 정보의 부적절한 노출, CWE-488)과 가장 관련 있는 상황은?",
    o: [
      "요청별 사용자 데이터를 정적(static) 필드나 재사용되는 스레드의 ThreadLocal에 저장하고 초기화하지 않아 다른 요청에서 노출된다",
      "지역 변수를 메서드 내에서만 사용한다",
      "불변 객체를 여러 스레드가 읽기만 한다",
      "요청마다 새 객체를 생성해 반환한다"
    ],
    a: 0,
    e: "서블릿/스레드풀 환경에서 사용자별 데이터를 인스턴스의 정적 필드에 저장하거나, 재사용되는 스레드의 ThreadLocal을 요청 종료 시 remove()하지 않으면 다음 요청(다른 사용자)에서 이전 데이터가 노출될 수 있다(CWE-488). 요청 스코프 데이터는 반드시 요청 종료 시 정리해야 한다."
  },
  {
    c: "시간상태",
    q: "재진입 불가능(non-reentrant) 함수를 신호 처리기(signal handler) 안에서 호출할 때의 위험(CWE-364)은?",
    o: [
      "핸들러가 메인 흐름의 비원자적 연산을 중간에 가로채 공유 상태를 손상시키거나 교착/미정의 동작을 유발한다",
      "신호가 항상 무시된다",
      "핸들러가 컴파일되지 않는다",
      "신호 처리가 자동으로 원자적이 된다"
    ],
    a: 0,
    e: "신호는 언제든 비동기적으로 실행 흐름을 가로챌 수 있다. malloc이나 비동기-신호-안전하지 않은 함수를 핸들러에서 호출하면, 메인 코드가 그 함수 중간에 있을 때 재진입되어 힙 손상 등 미정의 동작이 발생한다(CWE-364, 신호 처리 중 경쟁 조건). 핸들러에서는 async-signal-safe 함수만 사용해야 한다."
  },
  {
    c: "시간상태",
    q: "다음 중 불변(immutable) 객체를 사용하는 것이 동시성 관점에서 안전한 근본 이유는?",
    o: [
      "생성 후 상태가 변하지 않으므로 여러 스레드가 동기화 없이 안전하게 공유·읽기 할 수 있다",
      "불변 객체는 GC 대상이 되지 않는다",
      "불변 객체는 항상 싱글턴이다",
      "불변 객체는 자동으로 암호화된다"
    ],
    a: 0,
    e: "불변 객체는 생성 시점 이후 상태 변경이 없어 경쟁 조건이나 원자성 위반이 원천적으로 발생하지 않는다. 따라서 락 없이도 안전하게 공유·공개될 수 있다(단, 안전한 초기화 공개가 보장되어야 함). Java의 final 필드와 String이 대표적이다."
  },
  {
    c: "시간상태",
    q: "Python의 GIL(Global Interpreter Lock)에 대한 설명으로 옳은 것은?",
    o: [
      "GIL이 있어도 여러 바이트코드로 나뉘는 복합 연산(예: x += 1)은 스레드 경쟁 조건에 취약하다",
      "GIL 덕분에 모든 연산이 원자적이므로 락이 전혀 필요 없다",
      "GIL은 멀티프로세싱에도 프로세스 간 공유 메모리를 자동 보호한다",
      "GIL은 CPU 바운드 작업을 여러 코어에서 진정 병렬로 실행시킨다"
    ],
    a: 0,
    e: "GIL은 한 번에 하나의 스레드만 바이트코드를 실행하게 하지만, x += 1 같은 연산은 LOAD/ADD/STORE 여러 바이트코드로 나뉘고 그 사이에 스레드가 전환될 수 있어 경쟁 조건이 발생한다(CWE-362). 따라서 공유 상태 갱신에는 여전히 threading.Lock이 필요하다."
  },
  {
    c: "시간상태",
    q: "다음 Java 코드에서 스레드 안전성을 보장하려면 어떤 조치가 가장 적절한가?",
    o: [
      "balance 접근을 synchronized로 감싸거나 AtomicLong을 사용한다",
      "balance를 static으로 선언한다",
      "withdraw 메서드를 private으로 바꾼다",
      "amount를 final로 선언한다"
    ],
    a: 0,
    e: "잔액 검사(check)와 차감(act)이 분리되어 있고 balance 갱신이 비원자적이라, 여러 스레드가 동시에 출금하면 초과 인출(오버드로우)이 발생할 수 있다(CWE-362 경쟁 조건). 검사와 갱신을 하나의 임계 구역(synchronized)으로 묶거나 원자 타입/락으로 보호해야 한다.",
    code: `class Account {
    private long balance;
    void withdraw(long amount) {
        if (balance >= amount)   // check
            balance -= amount;   // act (비원자적)
    }
}`
  }
);
window.__QBANK.THEORY.push(
  {
    type: "OX",
    cat: "시간상태",
    q: "TOCTOU(검사 시점과 사용 시점의 차이, CWE-367)는 검사와 사용을 하나의 원자적 연산으로 결합하면 완화할 수 있다.",
    a: true,
    e: "맞다. TOCTOU의 근본 원인은 검사와 사용 사이의 시간 창이므로, 두 연산을 원자적으로 결합(예: open의 O_CREAT|O_EXCL, 파일 디스크립터 기반 접근)하면 경쟁 창이 사라진다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "Java에서 double-checked locking을 사용할 때 대상 필드에 volatile을 붙이지 않아도 항상 안전하다.",
    a: false,
    e: "틀리다. volatile이 없으면 객체 생성 과정의 명령어 재정렬로 다른 스레드가 초기화되지 않은 객체를 볼 수 있다(CWE-609). 필드를 volatile로 선언해야 안전하다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "로그인 성공 후에도 기존 세션 ID를 그대로 유지하면 세션 고정(CWE-384) 공격에 노출될 수 있다.",
    a: true,
    e: "맞다. 인증 전후로 세션 ID가 동일하면, 공격자가 사전에 심어둔 세션 ID를 피해자가 인증에 사용하게 되어 세션을 탈취당한다. 로그인 시 세션 ID를 재발급해야 한다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "Python의 GIL이 존재하므로 여러 스레드가 공유 정수를 x += 1 로 증가시켜도 경쟁 조건이 발생하지 않는다.",
    a: false,
    e: "틀리다. x += 1은 여러 바이트코드로 나뉘고 그 사이 스레드 전환이 가능해 갱신 유실이 발생한다(CWE-362). 공유 상태 갱신에는 threading.Lock이 필요하다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "두 스레드가 항상 동일한 순서로 여러 락을 획득하도록 강제하면 순환 대기가 제거되어 데드락(CWE-833)을 예방할 수 있다.",
    a: true,
    e: "맞다. 데드락 발생 조건 중 순환 대기(circular wait)를 깨는 대표적 기법이 락 획득 순서를 전역적으로 일관되게 정하는 것이다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "불변(immutable) 객체는 상태가 변하지 않으므로 여러 스레드가 락 없이 안전하게 공유하여 읽을 수 있다.",
    a: true,
    e: "맞다. 불변 객체는 생성 후 상태 변경이 없어 경쟁 조건이 원천적으로 발생하지 않는다(안전한 초기화 공개 전제). 이 때문에 락 없이 공유 가능하다."
  },
  {
    type: "OX",
    cat: "시간상태",
    q: "스레드풀 환경에서 ThreadLocal에 요청별 사용자 데이터를 저장한 뒤 요청 종료 시 remove()하지 않아도 다음 요청에 영향이 없다.",
    a: false,
    e: "틀리다. 스레드가 재사용되므로 remove()하지 않으면 이전 요청의 데이터가 다음 요청(다른 사용자)에 남아 정보 노출/오염이 발생한다(CWE-488). 요청 종료 시 반드시 remove()해야 한다."
  },
  {
    type: "MC",
    cat: "시간상태",
    q: "다음 중 '검사 후 사용'(TOCTOU)에 해당하는 CWE 번호는?",
    o: ["CWE-89", "CWE-367", "CWE-79", "CWE-22"],
    a: 1,
    e: "CWE-367은 Time-of-check Time-of-use(TOCTOU) 경쟁 조건이다. CWE-89는 SQL 삽입, CWE-79는 XSS, CWE-22는 경로 조작이다."
  },
  {
    type: "MC",
    cat: "시간상태",
    q: "여러 스레드가 안전하게 정수 카운터를 증가시키기 위한 Java 클래스로 가장 적절한 것은?",
    o: ["java.util.ArrayList", "java.util.concurrent.atomic.AtomicInteger", "java.lang.StringBuilder", "java.util.HashMap"],
    a: 1,
    e: "AtomicInteger의 incrementAndGet()은 CAS 기반의 원자적 연산으로 락 없이 스레드 안전하게 카운터를 증가시킨다. StringBuilder와 HashMap은 스레드 안전하지 않다."
  },
  {
    type: "MC",
    cat: "시간상태",
    q: "Double-Checked Locking 결함에 해당하는 CWE는?",
    o: ["CWE-362", "CWE-609", "CWE-384", "CWE-835"],
    a: 1,
    e: "CWE-609가 Double-Checked Locking 결함이다. CWE-362는 일반 경쟁 조건, CWE-384는 세션 고정, CWE-835는 무한 루프(도달 불가 종료 조건)이다."
  },
  {
    type: "MC",
    cat: "시간상태",
    q: "다음 중 Python에서 임계 구역을 예외 안전하게 보호하는 올바른 방법은?",
    o: [
      "lock.acquire() 후 별도 release 호출 없이 그냥 둔다",
      "with lock: 블록 안에서 임계 구역을 실행한다",
      "GIL을 신뢰하고 락을 아예 사용하지 않는다",
      "time.sleep()으로 스레드 전환을 지연시킨다"
    ],
    a: 1,
    e: "with lock: 구문은 컨텍스트 매니저가 정상/예외 경로 모두에서 release를 보장한다. acquire만 하고 release를 명시적으로 관리하면 예외 시 락이 해제되지 않아 데드락 위험이 있다."
  },
  {
    type: "MC",
    cat: "시간상태",
    q: "무한 루프로 인한 자원 고갈에 해당하는 CWE는?",
    o: ["CWE-835", "CWE-367", "CWE-488", "CWE-364"],
    a: 0,
    e: "CWE-835는 Loop with Unreachable Exit Condition(무한 루프)이다. CWE-367은 TOCTOU, CWE-488은 데이터 요소의 잘못된 스레드 간 노출, CWE-364는 신호 처리기 경쟁 조건이다."
  },
  {
    type: "SHORT",
    cat: "시간상태",
    q: "여러 스레드가 공유 자원에 동시에 접근하여 실행 순서에 따라 결과가 달라지는(비결정적) 시간 및 상태 보안약점을 4글자 한글로 무엇이라 하는가?",
    a: "경쟁조건",
    answers: ["경쟁 조건", "레이스컨디션", "레이스 컨디션", "race condition", "Race Condition", "경쟁상태", "경쟁 상태"],
    e: "경쟁 조건(Race Condition, CWE-362)은 둘 이상의 스레드가 공유 자원에 동시 접근할 때 실행 타이밍에 따라 결과가 달라지는 결함이다. 동기화(락)나 원자적 연산으로 해결한다."
  },
  {
    type: "SHORT",
    cat: "시간상태",
    q: "Java에서 스레드 안전한 해시 맵 구현으로, put/get이 내부적으로 동기화되어 있는 java.util.concurrent 패키지의 클래스 이름은?",
    a: "ConcurrentHashMap",
    answers: ["concurrenthashmap", "java.util.concurrent.ConcurrentHashMap"],
    e: "ConcurrentHashMap은 세분화된 락킹(또는 CAS)으로 동시 접근을 안전하게 처리한다. HashMap을 여러 스레드가 동기화 없이 공유하면 데이터 손상과 무한 루프가 발생할 수 있어 이 클래스로 대체한다."
  },
  {
    type: "SHORT",
    cat: "시간상태",
    q: "로그인(인증) 성공 시 기존 세션 식별자를 폐기하고 새 식별자를 발급하는 것이 핵심 방어책인 공격의 이름은? (한글 또는 영문)",
    a: "세션 고정",
    answers: ["세션고정", "session fixation", "Session Fixation", "세션 고정 공격"],
    e: "세션 고정(Session Fixation, CWE-384)은 공격자가 고정한 세션 ID를 피해자가 인증에 사용하게 만드는 공격이다. 인증 성공 시 세션 재생성으로 방어한다."
  },
  {
    type: "SHORT",
    cat: "시간상태",
    q: "Java에서 필드에 이 키워드를 붙이면 한 스레드의 쓰기가 다른 스레드에 즉시 보이는 가시성이 보장되며, double-checked locking 필드에도 필요하다. 이 키워드는?",
    a: "volatile",
    answers: ["Volatile", "volatile 키워드"],
    e: "volatile은 변수의 읽기/쓰기가 메인 메모리를 거치게 하여 가시성을 보장하고, 관련 명령어 재정렬을 제한한다. double-checked locking(CWE-609)에서 초기화되지 않은 객체 노출을 막기 위해 필수적이다."
  },
  {
    type: "SHORT",
    cat: "시간상태",
    q: "둘 이상의 스레드가 서로가 점유한 락을 순환적으로 기다리며 모두 진행하지 못하는 상태를 가리키는 4글자 한글 용어는?",
    a: "교착상태",
    answers: ["교착 상태", "데드락", "deadlock", "Deadlock"],
    e: "교착 상태(Deadlock, CWE-833)는 순환 대기가 형성되어 관련 스레드가 모두 무한 대기하는 상태다. 락 획득 순서 일관화, 타임아웃(tryLock) 등으로 예방한다."
  }
);

// ===== partE_err =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  {
    c: "에러처리",
    q: "다음 Java 코드의 보안약점으로 가장 적절한 것은?",
    o: [
      "오류 메시지를 통한 정보 노출(CWE-209)",
      "확인되지 않은 오류 조건(CWE-391)",
      "부적절한 자원 해제(CWE-460)",
      "반환값 미확인(CWE-252)"
    ],
    a: 0,
    e: "예외의 e.getMessage() 또는 스택트레이스를 사용자 응답에 그대로 반환하면 내부 경로·SQL·라이브러리 버전 등 민감정보가 노출된다. 이는 CWE-209(오류 메시지를 통한 정보 노출)에 해당한다. 상세 정보는 서버 로그에만 남기고 사용자에게는 일반화된 메시지를 반환해야 한다.",
    code: `try {
    user = repository.find(userId);
} catch (SQLException e) {
    response.getWriter().write("오류: " + e.getMessage());
}`
  },
  {
    c: "에러처리",
    q: "예외를 catch한 뒤 아무런 조치도 하지 않는 아래 코드의 약점은?",
    o: [
      "처리되지 않은 예외(CWE-248)",
      "예외처리 후 적절한 조치 없음 / 빈 catch(CWE-390)",
      "오류 메시지 정보 노출(CWE-209)",
      "부적절한 반환값 확인(CWE-253)"
    ],
    a: 1,
    e: "catch 블록을 비워두면(빈 catch) 오류가 조용히 무시되어 프로그램이 잘못된 상태로 계속 실행된다. 이는 CWE-390(오류 조건을 감지했으나 조치하지 않음)에 해당한다. 최소한 로깅하거나 적절히 복구/전파해야 한다.",
    code: `try {
    transfer(amount);
} catch (Exception e) {
    // 아무것도 하지 않음
}`
  },
  {
    c: "에러처리",
    q: "e.printStackTrace()를 운영 환경 웹 애플리케이션에서 사용할 때의 주된 문제는?",
    o: [
      "성능이 크게 저하된다",
      "스택트레이스가 표준 출력/에러로 나가 노출되거나 내부 구조 정보를 흘릴 수 있다(CWE-209)",
      "예외가 다시 던져진다",
      "컴파일 경고가 발생한다"
    ],
    a: 1,
    e: "printStackTrace()는 스택트레이스를 표준 에러 스트림으로 출력하며, 이 출력이 사용자에게 노출되거나 로그를 통해 클래스명·경로·프레임워크 정보를 흘려 CWE-209로 이어질 수 있다. 통제된 로거를 사용해 서버 측에만 기록해야 한다.",
    code: `try {
    process(request);
} catch (Exception e) {
    e.printStackTrace();
}`
  },
  {
    c: "에러처리",
    q: "다음 Python 코드에서 나타나는 보안약점은?",
    o: [
      "확인되지 않은 오류 조건(CWE-391)",
      "예외처리 후 적절한 조치 없음(CWE-390)",
      "부적절한 정리(CWE-460)",
      "반환값 부적절 확인(CWE-253)"
    ],
    a: 1,
    e: "except: pass는 발생한 모든 예외(bare except)를 무시하고 아무 조치도 하지 않는다. 오류가 은폐되어 잘못된 상태로 실행이 계속되므로 CWE-390에 해당한다. 또한 bare except는 KeyboardInterrupt/SystemExit까지 삼킨다는 부가 문제도 있다.",
    code: `try:
    balance = get_balance(account)
except:
    pass`
  },
  {
    c: "에러처리",
    q: "C/Java에서 함수의 반환값을 확인하지 않아 실패를 성공으로 오인하는 약점의 CWE는?",
    o: [
      "CWE-209",
      "CWE-252 (반환값 미확인)",
      "CWE-390",
      "CWE-460"
    ],
    a: 1,
    e: "malloc, file open, 인증 함수 등이 실패를 반환값으로 알리는데 이를 확인하지 않으면 NULL 역참조·권한 우회 등이 발생한다. 이는 CWE-252(Unchecked Return Value)에 해당한다.",
    code: `File f = new File(path);
f.delete(); // boolean 반환값을 무시 -> 삭제 실패를 감지 못함`
  },
  {
    c: "에러처리",
    q: "아래 Java 코드에서 파일 스트림 해제와 관련한 가장 안전한 접근은?",
    o: [
      "정상 경로 끝에서만 close()를 호출한다",
      "finally 블록 또는 try-with-resources로 항상 close()가 호출되도록 한다",
      "close()를 호출하지 않고 GC에 맡긴다",
      "catch 블록에서만 close()를 호출한다"
    ],
    a: 1,
    e: "예외가 발생하면 정상 경로의 close()는 실행되지 않아 자원 누수가 생긴다(CWE-460 부적절한 정리 / CWE-404 자원 미해제). finally 블록이나 try-with-resources를 사용해 예외 여부와 무관하게 자원이 해제되도록 보장해야 한다.",
    code: `InputStream in = new FileInputStream(path);
process(in);
in.close(); // process()에서 예외 시 실행 안 됨`
  },
  {
    c: "에러처리",
    q: "Exception 또는 Throwable을 광범위하게 catch하는 것이 위험한 이유로 가장 적절한 것은?",
    o: [
      "컴파일 속도가 느려진다",
      "의도치 않은 예외(예: NPE, OutOfMemoryError)까지 삼켜 진짜 결함을 은폐한다",
      "checked 예외를 던질 수 없게 된다",
      "finally 블록이 실행되지 않는다"
    ],
    a: 1,
    e: "catch(Exception) 또는 catch(Throwable)은 예상한 특정 예외뿐 아니라 프로그래밍 오류(NullPointerException)나 심각한 오류(Error)까지 잡아 은폐한다. 이는 CWE-396(광범위한 catch)·CWE-397과 관련되며, 필요한 예외만 구체적으로 잡아야 한다.",
    code: `try {
    doWork();
} catch (Throwable t) {
    log.warn("무시");
}`
  },
  {
    c: "에러처리",
    q: "다음 코드에서 fail-safe(안전한 기본값) 원칙을 위반한 부분은?",
    o: [
      "예외 발생 시 권한을 true(허용)로 기본 설정한 것",
      "예외를 로깅한 것",
      "함수가 boolean을 반환한 것",
      "try 블록에서 DB를 조회한 것"
    ],
    a: 0,
    e: "인증/인가 검사에서 예외가 발생하면 접근을 거부(fail-secure)해야 한다. 예외 시 true를 반환하면 오류 상황이 곧 권한 우회로 이어진다. 안전한 기본값은 '거부'이며 이는 CWE-636(안전하지 않은 기본 동작)/CWE-703과 관련된다.",
    code: `boolean isAllowed(User u) {
    try {
        return acl.check(u);
    } catch (Exception e) {
        return true; // 오류 시 허용
    }
}`
  },
  {
    c: "에러처리",
    q: "'처리되지 않은 예외(CWE-248)'의 대표적 위험은?",
    o: [
      "스레드/프로세스가 비정상 종료되거나 서버가 기본 오류 페이지로 스택트레이스를 노출한다",
      "반환값이 항상 0이 된다",
      "메모리 사용량이 감소한다",
      "예외가 자동으로 재시도된다"
    ],
    a: 0,
    e: "잡히지 않은(uncaught) 예외는 스레드/프로세스를 중단시키거나, 웹 컨테이너가 기본 오류 페이지에 스택트레이스를 출력하게 만들어 가용성 저하와 정보 노출(CWE-209 연계)을 유발한다. 이것이 CWE-248(처리되지 않은 예외)이다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Python 코드에서 로깅과 노출을 올바르게 분리한 방식은?",
    o: [
      "예외 상세를 사용자에게 반환하고 로그는 남기지 않는다",
      "상세는 logging으로 서버에만 남기고 사용자에게는 일반 메시지를 반환한다",
      "print(e)로 콘솔에 출력한다",
      "예외를 그대로 다시 raise해 사용자 응답으로 보낸다"
    ],
    a: 1,
    e: "민감정보 노출(CWE-209)을 막으려면 예외의 상세 내용은 logging을 통해 서버 로그에만 남기고, 사용자에게는 식별자(요청 ID) 정도만 포함한 일반화된 메시지를 반환해야 한다.",
    code: `try:
    result = do_work()
except Exception:
    logging.exception("작업 실패")
    return "요청을 처리할 수 없습니다.", 500`
  },
  {
    c: "에러처리",
    q: "C에서 시스템 호출 후 errno를 확인하지 않고 사용하는 것과 관련된 약점은?",
    o: [
      "반환값/오류 표시자(errno)를 확인하지 않음(CWE-252/CWE-391)",
      "오류 메시지 노출(CWE-209)",
      "광범위 catch(CWE-396)",
      "부적절한 정리(CWE-460)"
    ],
    a: 0,
    e: "많은 C 라이브러리 함수는 실패를 반환값과 errno로 알린다. 반환값이나 errno를 확인하지 않으면 실패를 감지하지 못해(CWE-252/CWE-391) 잘못된 데이터로 진행한다. errno는 성공 시 초기화되지 않으므로 반환값이 실패를 표시할 때에만 참조해야 한다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 코드에서 finally 블록의 부적절한 사용으로 발생하는 문제는?",
    o: [
      "finally에서 return이 try/catch의 예외와 반환을 덮어써 오류가 은폐된다",
      "finally는 항상 실행되지 않는다",
      "finally에서 예외를 던질 수 없다",
      "finally는 catch보다 먼저 실행된다"
    ],
    a: 0,
    e: "finally 블록의 return이나 새 예외는 try/catch에서 발생·전파되던 예외를 삼켜 오류를 은폐한다. 이는 CWE-584(finally 내 return)와 CWE-703(예외 조건의 부적절한 처리)과 관련된다. finally에서는 정리만 수행하고 제어 흐름을 바꾸지 않아야 한다.",
    code: `try {
    return compute();
} finally {
    return -1; // compute()의 예외/결과를 덮어씀
}`
  },
  {
    c: "에러처리",
    q: "웹 애플리케이션의 운영 배포 시 스택트레이스 노출을 막는 가장 적절한 조치는?",
    o: [
      "디버그 모드를 끄고 커스텀 오류 페이지로 일반 메시지만 노출한다",
      "모든 예외를 catch(Exception)로 잡아 무시한다",
      "스택트레이스를 HTML 주석으로 숨겨 응답에 포함한다",
      "예외 메시지를 그대로 사용자에게 보여준다"
    ],
    a: 0,
    e: "운영 환경에서는 프레임워크의 debug 모드를 비활성화하고, 통일된 커스텀 오류 페이지(예: 500 페이지)로 일반화된 메시지만 노출해야 한다. HTML 주석에 숨기는 것은 소스만 보면 드러나므로 여전히 CWE-209 노출이다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Java 코드에서 반환값을 '부적절하게' 확인한 사례(CWE-253)는?",
    o: [
      "실패 시 음수를 반환하는 함수를 == -1로만 비교하고 그 외 오류 코드는 무시",
      "예외를 로깅한 것",
      "try-with-resources를 사용한 것",
      "일반 메시지를 반환한 것"
    ],
    a: 0,
    e: "CWE-253은 반환값을 확인은 하되 잘못된 방식으로 비교하는 경우다. 여러 오류 코드(예: 음수 전체가 실패)를 == -1 하나로만 검사하면 다른 실패값을 성공으로 오인한다. 성공/실패 판정 조건을 명세대로 정확히 검사해야 한다.",
    code: `int rc = native.read(buf);
if (rc == -1) { handleError(); }
// -2, -3 등 다른 실패 코드는 성공으로 처리됨`
  },
  {
    c: "에러처리",
    q: "예외 발생 시 자원 정리를 제대로 하지 못하는 약점(CWE-460)을 방지하는 방법으로 옳지 않은 것은?",
    o: [
      "Java의 try-with-resources 사용",
      "Python의 with 문(context manager) 사용",
      "예외를 빈 catch로 잡아 흐름을 계속 진행",
      "finally에서 획득한 자원을 역순으로 해제"
    ],
    a: 2,
    e: "빈 catch로 예외를 삼키면 오류가 은폐될 뿐 자원 정리와는 무관하며 오히려 상태를 악화시킨다(CWE-390). 자원 정리는 try-with-resources, with 문, finally 블록으로 예외 여부와 무관하게 보장해야 한다(CWE-460 예방).",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 중 CWE-703(예외적 조건의 부적절한 검사·처리)의 개념을 가장 잘 설명한 것은?",
    o: [
      "프로그램이 예외적/비정상 조건을 감지하지 못하거나 잘못 처리하는 상위 개념의 약점",
      "SQL 인젝션의 한 형태",
      "암호 알고리즘의 취약점",
      "세션 고정 공격"
    ],
    a: 0,
    e: "CWE-703은 예외적 조건(오류, 실패, 예상치 못한 입력 등)을 적절히 검사·처리하지 못하는 문제를 포괄하는 상위 카테고리다. CWE-248, CWE-252, CWE-390, CWE-391 등이 그 하위에 속한다.",
    code: ""
  },
  {
    c: "에러처리",
    q: "다음 Python bare except의 부가적 위험으로 옳은 것은?",
    o: [
      "SystemExit, KeyboardInterrupt까지 잡아 정상 종료/중단을 방해한다",
      "구문 오류가 발생한다",
      "예외가 두 번 발생한다",
      "로깅이 자동으로 활성화된다"
    ],
    a: 0,
    e: "bare except(except:)는 BaseException을 상속하는 SystemExit, KeyboardInterrupt까지 포착해 Ctrl+C나 정상 종료를 방해할 수 있다. 필요한 예외만 잡거나 최소한 except Exception:을 사용해야 한다. 무시하면 CWE-390으로도 이어진다.",
    code: `try:
    run()
except:   # KeyboardInterrupt까지 삼킴
    pass`
  },
  {
    c: "에러처리",
    q: "여러 예외 유형을 하나의 catch(Exception)로 처리할 때 권장되는 개선 방향은?",
    o: [
      "발생 가능한 예외 유형별로 구체적으로 catch하고 각기 적절히 처리한다",
      "catch(Throwable)로 범위를 더 넓힌다",
      "예외를 모두 무시한다",
      "printStackTrace로 사용자에게 출력한다"
    ],
    a: 0,
    e: "광범위 catch는 서로 다른 오류를 동일하게 처리해 복구 로직과 로깅을 부정확하게 만든다(CWE-396). 예상되는 예외를 유형별로 구체적으로 잡아 상황에 맞게 복구·전파·로깅해야 한다.",
    code: ""
  }
);
window.__QBANK.THEORY.push(
  {
    type: "OX",
    cat: "에러처리",
    q: "예외의 e.getMessage()나 스택트레이스를 사용자 응답에 그대로 반환하면 CWE-209(오류 메시지를 통한 정보 노출)에 해당한다.",
    a: true,
    e: "내부 경로, SQL 구문, 프레임워크/버전 정보 등이 노출되어 공격자에게 정찰 정보를 제공하므로 CWE-209에 해당한다. 사용자에게는 일반화된 메시지만 반환해야 한다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "빈 catch 블록(catch(Exception e){})은 오류를 무시하므로 안전한 방어적 코딩 기법이다.",
    a: false,
    e: "빈 catch는 오류를 은폐하여 프로그램이 잘못된 상태로 계속 실행되게 만든다. 이는 CWE-390(오류 조건 감지 후 조치 없음) 약점이며 방어적 코딩이 아니다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "인증/인가 검사 중 예외가 발생하면 접근을 '거부'하는 것이 안전한 기본값(fail-secure)이다.",
    a: true,
    e: "예외 상황에서 접근을 허용(fail-open)하면 오류가 곧 권한 우회로 이어진다. 안전한 기본값은 거부이며, 이를 어기면 CWE-636/CWE-703 관련 약점이 된다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "Python의 bare except(except:)는 SystemExit와 KeyboardInterrupt까지 포착할 수 있다.",
    a: true,
    e: "bare except는 BaseException 계열까지 잡으므로 Ctrl+C(KeyboardInterrupt)와 정상 종료(SystemExit)를 방해할 수 있다. except Exception: 또는 구체적 예외 사용이 권장된다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "finally 블록에서 return을 사용하면 try/catch에서 전파되던 예외가 은폐될 수 있다.",
    a: true,
    e: "finally의 return은 try/catch에서 던져지던 예외나 반환값을 덮어써 오류를 은폐한다(CWE-584/CWE-703). finally에서는 정리만 하고 제어 흐름을 바꾸지 말아야 한다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "잡히지 않은 예외(uncaught exception)는 웹 서버가 기본 오류 페이지로 스택트레이스를 노출하게 만들 수 있다.",
    a: true,
    e: "처리되지 않은 예외(CWE-248)는 컨테이너의 기본 오류 처리로 넘어가 스택트레이스를 노출(CWE-209 연계)하거나 스레드를 중단시킬 수 있다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "catch(Throwable)는 catch(Exception)보다 안전하므로 항상 권장된다.",
    a: false,
    e: "Throwable은 Error(OutOfMemoryError 등)까지 포함해 복구 불가능한 심각한 오류까지 삼킨다. 광범위 catch는 오히려 CWE-396 약점이며 권장되지 않는다. 필요한 예외만 구체적으로 잡아야 한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "오류 메시지나 스택트레이스로 내부 민감정보가 노출되는 보안약점의 CWE 번호를 쓰시오. (예: CWE-000)",
    a: "CWE-209",
    answers: ["CWE-209", "209", "cwe-209"],
    e: "CWE-209는 오류 메시지를 통한 정보 노출(Information Exposure Through an Error Message)이다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "예외를 잡은 후 아무런 조치(로깅/복구/전파)도 하지 않는, 빈 catch로 대표되는 보안약점의 CWE 번호를 쓰시오.",
    a: "CWE-390",
    answers: ["CWE-390", "390", "cwe-390"],
    e: "CWE-390은 오류 조건을 감지했으나 조치하지 않음(Detection of Error Condition Without Action)이다. 빈 catch, except: pass가 대표 예다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "함수의 반환값을 확인하지 않아 실패를 성공으로 오인하는 보안약점의 CWE 번호를 쓰시오.",
    a: "CWE-252",
    answers: ["CWE-252", "252", "cwe-252"],
    e: "CWE-252는 반환값 미확인(Unchecked Return Value)이다. malloc/파일열기/인증 함수 등의 실패 반환을 무시하면 발생한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "Java에서 예외 여부와 무관하게 자원(파일, 소켓 등)을 자동으로 닫아 주는 구문 이름을 쓰시오.",
    a: "try-with-resources",
    answers: ["try-with-resources", "try with resources", "트라이 위드 리소스", "try(자원)"],
    e: "try-with-resources는 AutoCloseable 자원을 선언하면 블록 종료 시 예외 여부와 무관하게 close()를 호출해 CWE-460/CWE-404를 예방한다."
  },
  {
    type: "SHORT",
    cat: "에러처리",
    q: "예외적/비정상 조건의 부적절한 검사·처리를 포괄하는 상위 CWE 카테고리 번호를 쓰시오.",
    a: "CWE-703",
    answers: ["CWE-703", "703", "cwe-703"],
    e: "CWE-703은 예외적 조건의 부적절한 검사 또는 처리(Improper Check or Handling of Exceptional Conditions)로, CWE-248/252/390/391 등의 상위 카테고리다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "다음 중 '처리되지 않은 예외'를 가리키는 CWE는?",
    o: ["CWE-209", "CWE-248", "CWE-252", "CWE-390"],
    a: 1,
    e: "CWE-248은 처리되지 않은 예외(Uncaught Exception)로, 잡히지 않은 예외가 프로세스 중단이나 스택트레이스 노출을 유발한다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "Python에서 예외 상세를 노출하지 않으면서 서버 측에 기록하기 위한 가장 적절한 방법은?",
    o: [
      "print(e)로 콘솔에 출력",
      "logging.exception()으로 로그에 남기고 사용자에게는 일반 메시지 반환",
      "예외를 사용자 응답 본문에 그대로 반환",
      "except: pass로 무시"
    ],
    a: 1,
    e: "logging.exception()은 스택트레이스를 서버 로그에만 기록한다. 사용자에게는 일반화된 메시지만 반환해야 CWE-209 노출을 막는다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "반환값을 확인은 하지만 성공/실패 판정 조건을 잘못 비교해 일부 실패를 성공으로 처리하는 약점의 CWE는?",
    o: ["CWE-252", "CWE-253", "CWE-391", "CWE-460"],
    a: 1,
    e: "CWE-253은 반환값의 부적절한 확인(Incorrect Check of Function Return Value)이다. 실패 코드 전체를 검사하지 않고 특정 값 하나로만 비교하는 경우가 해당된다."
  },
  {
    type: "MC",
    cat: "에러처리",
    q: "다음 중 광범위한 예외 포착(catch(Exception)/catch(Throwable)) 남용의 문제로 옳지 않은 것은?",
    o: [
      "프로그래밍 오류(NPE)까지 삼켜 결함이 은폐된다",
      "서로 다른 오류를 동일하게 처리해 복구 로직이 부정확해진다",
      "Error 등 복구 불가능한 심각한 오류까지 잡을 수 있다",
      "checked 예외를 컴파일 시점에 강제로 처리하게 만들어 안전해진다"
    ],
    a: 3,
    e: "광범위 catch는 결함 은폐, 부정확한 복구, 심각한 오류 포착 등의 문제를 낳는다(CWE-396). 컴파일 안전성을 높이는 것과는 무관하며 오히려 구체적 예외 처리를 회피하게 만든다."
  },
  {
    type: "OX",
    cat: "에러처리",
    q: "C에서 errno는 함수가 성공한 경우에도 이전 값이 남아 있을 수 있으므로, 반환값이 실패를 표시할 때에만 참조해야 한다.",
    a: true,
    e: "errno는 성공 시 0으로 초기화되지 않는다. 따라서 함수의 반환값이 실패를 나타낼 때에만 errno를 확인해야 하며, 그렇지 않으면 오탐이 생긴다(CWE-391 관련)."
  }
);

// ===== partE_encap =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  {
    c: "캡슐화",
    q: "다음 Java getter의 보안약점으로 가장 적절한 것은?",
    o: [
      "private 배열의 참조를 그대로 반환하여 외부에서 내부 상태를 변경할 수 있다 (CWE-495)",
      "배열 크기가 초기화되지 않아 NullPointerException이 발생한다",
      "getter는 반드시 void를 반환해야 한다",
      "배열 대신 List를 사용하지 않아 성능이 저하된다"
    ],
    a: 0,
    e: "getter가 private 배열 필드의 참조를 그대로 반환하면 호출자가 반환된 배열을 수정해 내부 상태를 바꿀 수 있다. 이는 CWE-495(Private Array-Typed Field Returned From a Public Method)에 해당한다. Arrays.copyOf() 등으로 방어적 복사본을 반환해야 한다.",
    code: "public class Account {\n    private int[] balances;\n    public int[] getBalances() {\n        return balances; // 내부 배열 참조 그대로 노출\n    }\n}"
  },
  {
    c: "캡슐화",
    q: "CWE-495(private 배열을 참조로 반환)를 올바르게 제거한 코드는?",
    o: [
      "return balances.clone();",
      "return balances;",
      "return null;",
      "balances = null; return balances;"
    ],
    a: 0,
    e: "clone() 또는 Arrays.copyOf()로 방어적 복사본을 반환하면 외부에서 원본 내부 배열을 수정할 수 없어 CWE-495를 제거한다. 원본 참조를 그대로 반환하거나 null을 반환하는 것은 올바른 해결이 아니다.",
    code: "public int[] getBalances() {\n    return balances.clone(); // 방어적 복사\n}"
  },
  {
    c: "캡슐화",
    q: "다음 setter 코드의 보안약점으로 가장 적절한 것은?",
    o: [
      "외부에서 받은 public 배열 참조를 private 필드에 그대로 대입한다 (CWE-496)",
      "setter는 반환값이 있어야 한다",
      "배열은 setter로 설정할 수 없다",
      "final 필드는 setter가 없어도 된다"
    ],
    a: 0,
    e: "외부에서 전달된 배열 참조를 private 필드에 그대로 대입하면 호출자가 그 배열을 계속 참조하며 나중에 내부 상태를 변경할 수 있다. 이는 CWE-496(Public Data Assigned to Private Array-Typed Field)이다. 방어적 복사 후 대입해야 한다.",
    code: "public void setData(int[] input) {\n    this.data = input; // 외부 참조를 그대로 대입\n}"
  },
  {
    c: "캡슐화",
    q: "CWE-496(public 데이터를 private 배열에 대입)의 안전한 처리 방법은?",
    o: [
      "this.data = input.clone(); 또는 Arrays.copyOf로 복사 후 대입",
      "this.data = input; 으로 즉시 대입",
      "입력을 static 필드에 저장",
      "input을 그대로 반환"
    ],
    a: 0,
    e: "외부 입력 배열을 clone()이나 Arrays.copyOf()로 복사한 뒤 대입하면 호출자가 원본 배열을 수정해도 내부 상태에 영향을 주지 않아 CWE-496을 방지한다.",
    code: "public void setData(int[] input) {\n    this.data = (input == null) ? null : input.clone();\n}"
  },
  {
    c: "캡슐화",
    q: "가변 객체(Date, 배열, 컬렉션)를 필드로 가진 클래스에서 방어적 복사를 적용해야 하는 지점은?",
    o: [
      "생성자/setter로 받을 때와 getter로 반환할 때 모두",
      "생성자에서 받을 때만",
      "getter로 반환할 때만",
      "toString() 호출 시에만"
    ],
    a: 0,
    e: "가변 객체는 입력 시점(생성자/setter)과 출력 시점(getter) 모두에서 방어적 복사를 해야 한다. 한쪽만 복사하면 나머지 경로로 내부 상태가 노출/변조될 수 있다.",
    code: "public final class Period {\n    private final Date start;\n    public Period(Date start) { this.start = new Date(start.getTime()); }\n    public Date getStart() { return new Date(start.getTime()); }\n}"
  },
  {
    c: "캡슐화",
    q: "java.util.Date를 그대로 필드에 저장하고 getter가 원본을 반환할 때의 문제는?",
    o: [
      "Date는 가변 객체라 호출자가 setTime()으로 내부 상태를 변경할 수 있다",
      "Date는 불변이라 문제가 없다",
      "Date는 직렬화가 불가능하다",
      "Date는 getter로 반환할 수 없다"
    ],
    a: 0,
    e: "java.util.Date는 setTime() 등으로 값이 바뀌는 가변 객체다. 원본을 노출하면 캡슐화가 깨진다. 방어적 복사(new Date(...))를 하거나 불변인 java.time.Instant/LocalDate 등을 사용해야 한다.",
    code: "public Date getExpiry() {\n    return this.expiry; // 가변 Date 원본 노출\n}"
  },
  {
    c: "캡슐화",
    q: "다음 중 신뢰 경계 위반(CWE-501)에 해당하는 상황은?",
    o: [
      "검증되지 않은 외부 입력을 신뢰 데이터(예: 세션)와 검증 없이 섞어 저장한다",
      "private 필드에 getter를 두었다",
      "final 상수를 public으로 선언했다",
      "로컬 변수를 초기화했다"
    ],
    a: 0,
    e: "CWE-501(Trust Boundary Violation)은 신뢰할 수 없는 데이터와 신뢰할 수 있는 데이터를 명확한 검증/분리 없이 같은 경계 안에서 혼합할 때 발생한다. 예를 들어 검증 없이 사용자 입력을 세션 객체에 직접 저장하면 이후 코드가 이를 신뢰해 오용될 수 있다.",
    code: "// 검증 없이 외부 입력을 세션에 저장\nsession.setAttribute(\"userRole\", request.getParameter(\"role\"));"
  },
  {
    c: "캡슐화",
    q: "예외 스택트레이스나 경로/버전 정보를 사용자에게 그대로 노출하는 약점의 CWE는?",
    o: [
      "CWE-497 (민감한 시스템 정보의 비인가 노출)",
      "CWE-89 (SQL Injection)",
      "CWE-22 (경로 조작)",
      "CWE-79 (XSS)"
    ],
    a: 0,
    e: "내부 파일 경로, 서버 버전, 스택트레이스, 환경변수 등 시스템 정보를 외부 사용자에게 노출하면 CWE-497(Exposure of Sensitive System Information to an Unauthorized Control Sphere)에 해당한다. 공격자가 후속 공격 정보를 얻을 수 있으므로 일반화된 오류 메시지를 사용해야 한다.",
    code: "catch (Exception e) {\n    response.getWriter().println(e.toString()); // 내부 정보 노출\n}"
  },
  {
    c: "캡슐화",
    q: "운영 배포본에 다음 코드가 남아 있을 때의 약점(CWE-489)은?",
    o: [
      "디버그 코드 잔존으로 인증 우회 등 의도치 않은 진입점이 생긴다",
      "성능이 향상된다",
      "코드 가독성만 낮아질 뿐 보안과 무관하다",
      "컴파일 오류가 발생한다"
    ],
    a: 0,
    e: "개발용 백도어/디버그 코드가 운영 환경에 남으면 CWE-489(Active Debug Code)로, 인증 우회나 민감 정보 노출 같은 심각한 취약점이 된다. 배포 전 반드시 제거해야 한다.",
    code: "if (\"debug\".equals(request.getParameter(\"mode\"))) {\n    login(user, true); // 비밀번호 검사 없이 로그인\n}"
  },
  {
    c: "캡슐화",
    q: "Java 클래스에서 public 가변 필드를 직접 노출할 때의 문제(불충분한 캡슐화, CWE-485)는?",
    o: [
      "외부에서 필드를 직접 읽고 쓸 수 있어 불변식과 접근 제어가 깨진다",
      "필드 접근 속도가 느려진다",
      "필드가 자동으로 final이 된다",
      "가비지 컬렉션이 동작하지 않는다"
    ],
    a: 0,
    e: "필드를 public으로 두면 검증/불변식 없이 외부에서 임의로 변경할 수 있어 캡슐화가 무너진다. 이는 불충분한 캡슐화(CWE-485/CWE-766 등)와 연관된다. 필드는 private으로 두고 접근자를 통해 검증된 접근만 허용해야 한다.",
    code: "public class Config {\n    public int maxUsers; // 외부에서 직접 변경 가능\n}"
  },
  {
    c: "캡슐화",
    q: "불변(immutable) 클래스를 올바르게 설계한 것은?",
    o: [
      "final class, 모든 필드 private final, setter 없음, 가변 필드는 방어적 복사",
      "모든 필드를 public으로 선언",
      "setter를 제공하되 내부에서만 호출",
      "필드를 static으로 선언"
    ],
    a: 0,
    e: "불변 클래스는 class를 final로, 모든 필드를 private final로 두고, setter를 제공하지 않으며, 가변 참조 필드는 생성자에서 방어적 복사하고 getter에서도 복사본을 반환해야 한다.",
    code: "public final class Money {\n    private final long amount;\n    public Money(long amount) { this.amount = amount; }\n    public long getAmount() { return amount; }\n}"
  },
  {
    c: "캡슐화",
    q: "여러 스레드/인스턴스가 공유하는 static 가변 필드의 위험으로 가장 적절한 것은?",
    o: [
      "모든 인스턴스가 상태를 공유하여 의도치 않은 데이터 노출·경쟁 조건이 발생한다",
      "static 필드는 스레드 안전이 보장된다",
      "static 필드는 GC 대상이 아니라 성능이 향상된다",
      "static 필드는 캡슐화 문제와 무관하다"
    ],
    a: 0,
    e: "static 가변 필드는 클래스 단위로 공유되므로 한 사용자/요청의 데이터가 다른 요청에 노출되거나 경쟁 조건이 발생할 수 있다. 사용자별 상태는 인스턴스 필드로 두고 static 가변 상태는 피하거나 동기화/불변화해야 한다.",
    code: "public class UserContext {\n    static String currentUser; // 모든 요청이 공유 -> 데이터 혼선\n}"
  },
  {
    c: "캡슐화",
    q: "다음 Python 함수의 결함으로 가장 적절한 것은?",
    o: [
      "mutable default argument로 인해 호출 간 리스트가 공유되어 상태가 누적된다",
      "함수는 리스트를 인자로 받을 수 없다",
      "append는 새 리스트를 반환한다",
      "기본 인자는 매 호출마다 새로 생성된다"
    ],
    a: 0,
    e: "Python의 기본 인자는 함수 정의 시 한 번만 평가되므로, 가변 기본값([])을 쓰면 여러 호출이 같은 리스트를 공유해 상태가 누적된다. 기본값을 None으로 두고 함수 내부에서 새 리스트를 생성해야 한다.",
    code: "def add_item(item, bucket=[]):\n    bucket.append(item)\n    return bucket  # 호출마다 같은 리스트 재사용"
  },
  {
    c: "캡슐화",
    q: "Python에서 이름 맹글링(__attr)에 대한 올바른 설명은?",
    o: [
      "접근을 어렵게 만들 뿐 완전한 접근 제한(보안 경계)이 아니며 _Class__attr로 접근 가능하다",
      "완전한 private을 보장해 외부에서 절대 접근할 수 없다",
      "컴파일 시 필드를 암호화한다",
      "성능 최적화를 위한 기능이다"
    ],
    a: 0,
    e: "Python의 이중 밑줄 접두사(__)는 name mangling으로 하위 클래스와의 이름 충돌을 줄이기 위한 관례일 뿐, _ClassName__attr 형태로 여전히 접근 가능하다. 보안 경계로 신뢰해서는 안 된다.",
    code: "class A:\n    def __init__(self):\n        self.__secret = 1\na = A()\nprint(a._A__secret)  # 접근 가능"
  },
  {
    c: "캡슐화",
    q: "Python에서 불변 값 객체를 만들 때 가장 적절한 방법은?",
    o: [
      "@dataclass(frozen=True) 를 사용해 필드 재할당을 막는다",
      "일반 클래스에 __del__을 정의한다",
      "모든 속성을 전역 변수로 선언한다",
      "필드 이름 앞에 __만 붙이면 불변이 된다"
    ],
    a: 0,
    e: "@dataclass(frozen=True)는 인스턴스 속성 재할당 시 FrozenInstanceError를 발생시켜 불변 값 객체를 만든다. name mangling(__)은 불변성과 무관하다.",
    code: "from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Point:\n    x: int\n    y: int"
  },
  {
    c: "캡슐화",
    q: "getter가 내부 List를 그대로 반환하는 것을 안전하게 만드는 방법으로 가장 적절한 것은?",
    o: [
      "Collections.unmodifiableList(list) 또는 새 리스트 복사본을 반환한다",
      "list.clear() 후 반환한다",
      "list를 그대로 반환하되 final로 선언한다",
      "getter를 public에서 protected로만 바꾼다"
    ],
    a: 0,
    e: "내부 컬렉션 원본을 반환하면 호출자가 add/remove로 내부 상태를 바꿀 수 있다. Collections.unmodifiableList로 감싸 읽기 전용 뷰를 주거나 방어적 복사본(new ArrayList<>(list))을 반환해야 한다. 필드를 final로 선언해도 컬렉션 내용 변경은 막지 못한다.",
    code: "public List<String> getRoles() {\n    return Collections.unmodifiableList(roles);\n}"
  },
  {
    c: "캡슐화",
    q: "가변 객체를 필드로 보관하는 클래스에서 방어적 복사를 '입력 시점'에만 하고 getter에서 원본을 반환하면?",
    o: [
      "getter로 얻은 원본을 외부에서 변경해 여전히 내부 상태를 훼손할 수 있다",
      "완전히 안전해진다",
      "입력 검증까지 자동으로 수행된다",
      "컴파일 오류가 발생한다"
    ],
    a: 0,
    e: "입력 시점에만 복사하고 출력(getter)에서 원본을 반환하면 노출 경로가 남는다. 캡슐화를 온전히 지키려면 입력과 출력 양쪽 모두에서 방어적 복사가 필요하다.",
    code: "public Date getStart() { return start; } // 출력 경로에서 원본 노출"
  },
  {
    c: "캡슐화",
    q: "시스템 정보 노출(CWE-497)을 줄이기 위한 가장 적절한 예외 처리 방식은?",
    o: [
      "사용자에게는 일반화된 오류 메시지를, 상세 스택트레이스는 서버 내부 로그에만 기록한다",
      "예외 전문을 화면에 그대로 출력한다",
      "예외를 무시하고 아무 로그도 남기지 않는다",
      "예외 메시지에 DB 접속 정보를 포함해 출력한다"
    ],
    a: 0,
    e: "상세 오류(스택트레이스, 경로, 버전)는 서버 로그에만 남기고, 사용자에게는 식별 코드 정도의 일반화된 메시지를 보여야 CWE-497(민감 시스템 정보 노출)을 방지한다."
  }
);
window.__QBANK.THEORY.push(
  {
    type: "OX",
    cat: "캡슐화",
    q: "getter가 private 배열 필드의 참조를 그대로 반환하면 CWE-495에 해당한다.",
    a: true,
    e: "public 메서드가 private 배열 참조를 그대로 반환하면 외부에서 내부 배열을 수정할 수 있어 CWE-495(Private Array-Typed Field Returned From a Public Method)이다. clone()/Arrays.copyOf로 복사본을 반환해야 한다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "외부에서 받은 배열을 clone() 없이 private 필드에 그대로 대입하는 것은 안전하다.",
    a: false,
    e: "외부 입력 배열 참조를 그대로 대입하면 호출자가 그 배열을 나중에 수정해 내부 상태를 바꿀 수 있다. CWE-496에 해당하며 방어적 복사가 필요하다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "java.util.Date는 불변 객체이므로 getter에서 원본을 반환해도 캡슐화가 깨지지 않는다.",
    a: false,
    e: "java.util.Date는 setTime() 등으로 값이 바뀌는 가변 객체다. 원본을 반환하면 내부 상태가 노출·변조될 수 있으므로 방어적 복사나 java.time의 불변 타입을 사용해야 한다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "운영 배포본에 남아 있는 디버그/백도어 코드는 CWE-489(Active Debug Code)에 해당한다.",
    a: true,
    e: "개발 편의를 위한 디버그 코드가 운영에 남으면 인증 우회 등 심각한 취약점이 되며 CWE-489로 분류된다. 배포 전 제거해야 한다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "Python에서 속성 이름 앞에 __를 붙이면 외부에서 절대 접근할 수 없는 완전한 private이 된다.",
    a: false,
    e: "이중 밑줄은 name mangling(_ClassName__attr) 관례일 뿐이며 여전히 접근 가능하다. 보안 경계로 신뢰하면 안 된다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "가변 객체를 필드로 가질 때 방어적 복사는 입력(생성자/setter)과 출력(getter) 양쪽 모두에서 필요하다.",
    a: true,
    e: "한쪽만 복사하면 나머지 경로로 내부 상태가 노출·변조될 수 있다. 온전한 캡슐화를 위해 입력과 출력 양쪽에서 방어적 복사를 해야 한다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "사용자별 상태를 static 가변 필드에 저장하면 다른 요청에 데이터가 노출될 수 있다.",
    a: true,
    e: "static 필드는 클래스 단위로 공유되므로 한 요청의 데이터가 다른 요청에서 보이거나 경쟁 조건이 발생할 수 있다. 사용자별 상태는 인스턴스 범위로 관리해야 한다."
  },
  {
    type: "OX",
    cat: "캡슐화",
    q: "Collections.unmodifiableList로 감싸 반환하면 호출자가 반환된 리스트에 add/remove로 원소를 추가·삭제할 수 없다.",
    a: true,
    e: "unmodifiableList는 읽기 전용 뷰를 제공하여 구조적 변경(add/remove) 시 UnsupportedOperationException을 던진다. 다만 원소 자체가 가변이면 원소 내부 상태 변경은 별도 문제로 남는다."
  },
  {
    type: "MC",
    cat: "캡슐화",
    q: "다음 중 신뢰 경계 위반(CWE-501)의 대표 사례는?",
    o: [
      "검증되지 않은 외부 입력을 세션 등 신뢰 저장소에 검증 없이 저장",
      "final 상수를 사용",
      "private 필드에 getter/setter 사용",
      "지역 변수를 초기화"
    ],
    a: 0,
    e: "신뢰할 수 없는 데이터를 신뢰 경계(세션 등) 안으로 검증 없이 들여오면 이후 코드가 이를 신뢰해 오용된다. 이것이 CWE-501이다."
  },
  {
    type: "MC",
    cat: "캡슐화",
    q: "private 배열을 참조로 반환하는 CWE-495를 제거하는 가장 적절한 방법은?",
    o: [
      "Arrays.copyOf() 또는 clone()으로 복사본을 반환",
      "배열을 null로 초기화",
      "필드를 public으로 변경",
      "getter를 제거하고 필드를 직접 노출"
    ],
    a: 0,
    e: "방어적 복사본을 반환하면 외부에서 원본 내부 배열을 수정할 수 없어 CWE-495를 제거한다. 필드를 public으로 노출하는 것은 오히려 캡슐화를 더 악화시킨다."
  },
  {
    type: "MC",
    cat: "캡슐화",
    q: "Python에서 mutable default argument 문제를 피하는 올바른 패턴은?",
    o: [
      "기본값을 None으로 두고 함수 내부에서 새 객체를 생성",
      "기본값으로 빈 리스트 []를 사용",
      "전역 리스트를 기본값으로 사용",
      "기본값을 tuple 대신 list로 강제"
    ],
    a: 0,
    e: "기본 인자는 정의 시 한 번만 평가되므로 가변 기본값은 호출 간 공유된다. 기본값을 None으로 두고 함수 내부에서 `if x is None: x = []`처럼 새로 생성해야 한다."
  },
  {
    type: "MC",
    cat: "캡슐화",
    q: "Java 불변 클래스 설계에서 필수가 아닌 것은?",
    o: [
      "모든 필드를 static으로 선언",
      "class를 final로 선언",
      "모든 필드를 private final로 선언",
      "가변 참조 필드는 방어적 복사"
    ],
    a: 0,
    e: "불변 클래스는 final class, private final 필드, setter 부재, 가변 참조의 방어적 복사가 핵심이다. 필드를 static으로 선언하는 것은 불변성과 무관하며 오히려 공유 상태 문제를 유발할 수 있다."
  },
  {
    type: "MC",
    cat: "캡슐화",
    q: "예외 처리에서 CWE-497(시스템 정보 노출)을 방지하는 방식은?",
    o: [
      "상세 스택트레이스는 서버 로그에만 남기고 사용자에겐 일반 메시지 제공",
      "예외 전문을 응답 본문에 출력",
      "예외 메시지에 DB 접속 문자열 포함",
      "내부 파일 경로를 화면에 표시"
    ],
    a: 0,
    e: "민감한 시스템 정보(스택트레이스, 경로, 버전)는 사용자에게 노출하지 않고 서버 로그로만 관리해야 CWE-497을 방지한다."
  },
  {
    type: "SHORT",
    cat: "캡슐화",
    q: "public 메서드가 private 배열 필드의 참조를 그대로 반환하는 보안약점의 CWE 번호는? (숫자만)",
    a: "495",
    answers: ["495", "CWE-495", "cwe-495"],
    e: "CWE-495(Private Array-Typed Field Returned From a Public Method). 방어적 복사본을 반환해 해결한다."
  },
  {
    type: "SHORT",
    cat: "캡슐화",
    q: "외부의 public 데이터(배열)를 검증/복사 없이 private 배열 필드에 그대로 대입하는 약점의 CWE 번호는? (숫자만)",
    a: "496",
    answers: ["496", "CWE-496", "cwe-496"],
    e: "CWE-496(Public Data Assigned to Private Array-Typed Field). 입력 배열을 clone()/copyOf로 복사한 뒤 대입해 해결한다."
  },
  {
    type: "SHORT",
    cat: "캡슐화",
    q: "가변 객체를 필드에 저장하거나 반환할 때 원본 대신 복사본을 만들어 내부 상태 노출을 막는 기법을 무엇이라 하는가?",
    a: "방어적 복사",
    answers: ["방어적 복사", "defensive copy", "defensive copying", "방어적복사"],
    e: "방어적 복사(defensive copy)는 입력·출력 경로에서 가변 객체의 복사본을 사용해 외부가 내부 상태를 변경하지 못하게 하는 캡슐화 기법이다."
  },
  {
    type: "SHORT",
    cat: "캡슐화",
    q: "Python에서 속성명 앞의 이중 밑줄(__)이 유발하는, _ClassName__attr 형태로 이름을 바꾸는 메커니즘의 명칭은?",
    a: "name mangling",
    answers: ["name mangling", "네임 맹글링", "이름 맹글링", "namemangling"],
    e: "name mangling(이름 맹글링)은 __ 접두사 속성을 _ClassName__attr로 변환하는 Python의 메커니즘으로, 완전한 접근 제한이 아니라 이름 충돌 방지용 관례다."
  },
  {
    type: "SHORT",
    cat: "캡슐화",
    q: "운영 환경에 남아 있는 디버그/백도어 코드로 인한 보안약점의 CWE 번호는? (숫자만)",
    a: "489",
    answers: ["489", "CWE-489", "cwe-489"],
    e: "CWE-489(Active Debug Code). 배포 전 디버그 코드를 제거해야 인증 우회 등의 취약점을 방지한다."
  }
);

// ===== partE_api =====
window.__QBANK = window.__QBANK || { QUIZ: [], THEORY: [] };
window.__QBANK.QUIZ.push(
  {
    c: "API오용",
    q: "다음 C 코드에서 발생하는 대표적인 보안약점과 그에 해당하는 CWE로 가장 적절한 것은?",
    o: [
      "위험한 함수 gets() 사용으로 인한 버퍼 오버플로우 (CWE-242)",
      "사용되지 않는 변수 (CWE-563)",
      "널 포인터 역참조 (CWE-476)",
      "정수 오버플로우 (CWE-190)"
    ],
    a: 0,
    e: "gets()는 입력 길이를 제한하지 않아 버퍼 경계를 넘어 쓰기가 발생하는 본질적으로 위험한 함수이며, C11에서 삭제되었다. '본질적으로 위험한 함수 사용'은 CWE-242(Use of Inherently Dangerous Function)에 해당한다. 대안으로 fgets()를 사용하고 버퍼 크기를 명시해야 한다.",
    code: `char buf[16];\ngets(buf);        // 위험: 길이 제한 없음\nprintf(\"%s\\n\", buf);`
  },
  {
    c: "API오용",
    q: "strcpy(dst, src) 대신 안전하게 문자열을 복사하기 위해 권장되는 방식으로 가장 적절한 것은?",
    o: [
      "strncpy 등 크기 제한 함수를 쓰고 널 종료를 보장한다",
      "strcpy를 두 번 호출한다",
      "src의 길이를 무시하고 그대로 복사한다",
      "memcpy로 항상 dst 전체 크기만큼 복사한다"
    ],
    a: 0,
    e: "strcpy는 대상 버퍼 크기를 검사하지 않아 버퍼 오버플로우(CWE-120)를 유발한다. strncpy나 snprintf처럼 크기를 제한하는 함수를 쓰되, strncpy는 널 종료를 보장하지 않으므로 마지막 바이트에 명시적으로 '\\0'을 넣어야 한다. memcpy로 dst 전체를 복사하면 src보다 길 때 잘못된 데이터를 읽을 수 있다.",
    code: `char dst[16];\nstrncpy(dst, src, sizeof(dst) - 1);\ndst[sizeof(dst) - 1] = '\\0';`
  },
  {
    c: "API오용",
    q: "sprintf(buf, \"%s\", user_input) 형태의 코드가 위험한 이유로 가장 정확한 것은?",
    o: [
      "출력 길이를 제한하지 않아 buf 경계를 넘는 쓰기가 가능하다 (CWE-676)",
      "sprintf는 항상 널 문자를 붙이지 않기 때문이다",
      "sprintf는 표준 함수가 아니기 때문이다",
      "정수 인자만 처리할 수 있기 때문이다"
    ],
    a: 0,
    e: "sprintf는 대상 버퍼 크기를 인자로 받지 않아 입력이 길면 오버플로우가 발생한다. 위험한 함수 사용(CWE-676) 및 버퍼 오버플로우(CWE-120)에 해당한다. 대안으로 크기를 지정하는 snprintf(buf, sizeof(buf), ...)를 사용한다.",
    code: `char buf[32];\nsnprintf(buf, sizeof(buf), \"%s\", user_input);  // 안전`
  },
  {
    c: "API오용",
    q: "scanf(\"%s\", buf) 사용의 문제점과 올바른 대안으로 가장 적절한 것은?",
    o: [
      "너비 지정 없는 %s는 오버플로우 위험 → %31s처럼 최대 폭을 지정",
      "scanf는 정수만 읽으므로 %d로 바꾼다",
      "scanf 대신 gets를 쓴다",
      "buf를 static으로 선언하면 안전해진다"
    ],
    a: 0,
    e: "scanf의 %s는 최대 입력 폭을 지정하지 않으면 임의 길이 입력으로 버퍼 오버플로우를 일으킨다(CWE-676/CWE-120). 버퍼가 32바이트면 \"%31s\"처럼 폭을 지정하거나 fgets를 사용해야 한다. gets는 더 위험하므로 절대 대안이 될 수 없다.",
    code: `char buf[32];\nscanf(\"%31s\", buf);   // 최대 폭 지정`
  },
  {
    c: "API오용",
    q: "이미 표준에서 폐기(deprecated)되었거나 안전한 대체가 존재함에도 옛 함수를 계속 사용하는 약점의 CWE는?",
    o: [
      "CWE-477 (Use of Obsolete Function)",
      "CWE-89 (SQL Injection)",
      "CWE-22 (Path Traversal)",
      "CWE-798 (Hard-coded Credentials)"
    ],
    a: 0,
    e: "폐기되었거나 지원이 종료된(obsolete/deprecated) 함수를 계속 사용하는 것은 CWE-477에 해당한다. 예: Java의 Thread.stop(), Runtime.exec(String) 일부 오버로드, C의 gethostbyname() 등. 대체 API로 전환해야 한다.",
    code: `// Java 예: 폐기된 API 사용\nnew Date().getYear();   // deprecated → Calendar/LocalDate 사용`
  },
  {
    c: "API오용",
    q: "DNS 조회 결과(호스트 이름)를 신뢰해 접근 제어를 결정하는 코드의 보안약점으로 가장 적절한 것은?",
    o: [
      "DNS 이름에 의존한 보안 결정 (CWE-350)",
      "안전하지 않은 난수 (CWE-330)",
      "부적절한 인증 (CWE-287)",
      "경쟁 조건 (CWE-362)"
    ],
    a: 0,
    e: "역방향 DNS(PTR) 조회로 얻은 호스트 이름은 공격자가 자신의 DNS 서버로 위조할 수 있어 신뢰할 수 없다. 이름 기반으로 인증/인가를 결정하면 CWE-350(Reliance on Reverse DNS Resolution for a Security-Sensitive Action)에 해당한다. IP 화이트리스트나 상호 TLS 등 검증 가능한 신원을 사용해야 한다.",
    code: `String host = addr.getCanonicalHostName();\nif (host.endsWith(\".trusted.com\")) grantAccess();  // 위조 가능`
  },
  {
    c: "API오용",
    q: "다음 Java 코드의 문제점으로 가장 정확한 것은?",
    o: [
      "== 는 참조 동일성을 비교하므로 문자열 내용 비교에는 equals()를 써야 한다",
      "== 는 컴파일 오류를 일으킨다",
      "== 는 대소문자를 무시하므로 안전하다",
      "문제가 없으며 == 가 내용을 비교한다"
    ],
    a: 0,
    e: "Java에서 == 는 객체 참조(주소)가 같은지를 비교한다. 문자열 리터럴 풀이나 캐시로 우연히 true가 될 수 있으나, 일반적으로 내용 비교에는 equals()를 써야 한다. 인증 토큰/비밀번호 비교를 ==로 하면 항상 실패하거나 우회될 수 있다(CWE-597).",
    code: `String pw = request.getParameter(\"pw\");\nif (pw == \"secret\") { ... }        // 잘못: equals() 사용해야 함\nif (\"secret\".equals(pw)) { ... }   // 올바름 (NPE 방지 위해 리터럴 먼저)`
  },
  {
    c: "API오용",
    q: "Java에서 equals()를 재정의할 때 반드시 함께 지켜야 하는 계약(contract)으로 가장 적절한 것은?",
    o: [
      "equals()가 같다고 판정한 두 객체는 hashCode()도 같아야 한다",
      "equals()를 재정의하면 toString()도 반드시 재정의해야 한다",
      "hashCode()는 항상 0을 반환해야 한다",
      "equals()는 반드시 final로 선언해야 한다"
    ],
    a: 0,
    e: "Object.equals/hashCode 계약상 equals()로 같은 두 객체는 동일한 hashCode()를 반환해야 한다. 이를 어기면 HashMap/HashSet에서 키를 찾지 못하는 논리 오류가 발생한다(CWE-581: Object Model Violation). equals만 재정의하고 hashCode를 빼먹는 것이 대표적 오용이다.",
    code: `@Override public boolean equals(Object o) { ... }\n@Override public int hashCode() { return Objects.hash(field1, field2); }`
  },
  {
    c: "API오용",
    q: "보안 토큰, 세션 ID, 비밀번호 초기화 값 등을 생성할 때 java.util.Random을 쓰면 안 되는 이유로 가장 정확한 것은?",
    o: [
      "예측 가능한 PRNG라서 다음 값을 유추당할 수 있으므로 SecureRandom을 써야 한다",
      "java.util.Random은 음수를 반환하지 못하기 때문이다",
      "java.util.Random은 스레드 안전하지 않아서만 문제이다",
      "java.util.Random은 실수를 생성할 수 없기 때문이다"
    ],
    a: 0,
    e: "java.util.Random은 48비트 선형 합동 생성기로, 소량의 출력만 관찰하면 시드/내부 상태를 복원해 이후 값을 예측할 수 있다. 보안 목적의 난수는 암호학적으로 안전한 java.security.SecureRandom을 사용해야 한다. 예측 가능한 난수 사용은 CWE-330/CWE-338에 해당한다.",
    code: `// 취약: new Random().nextInt()\nSecureRandom rnd = new SecureRandom();\nbyte[] token = new byte[32];\nrnd.nextBytes(token);`
  },
  {
    c: "API오용",
    q: "라이브러리/공용 컴포넌트 코드 내부에서 System.exit()를 호출하는 것이 위험한 이유로 가장 적절한 것은?",
    o: [
      "호출한 애플리케이션 전체 JVM을 강제 종료시켜 가용성을 해친다 (CWE-382)",
      "System.exit()는 컴파일되지 않기 때문이다",
      "System.exit()는 예외를 던져 로그가 남지 않기 때문이다",
      "System.exit()는 메모리 누수를 일으키기 때문이다"
    ],
    a: 0,
    e: "라이브러리 내부에서 System.exit()를 호출하면 이를 사용하는 애플리케이션 서버/컨테이너 전체가 종료되어 다른 정상 요청까지 중단된다. 라이브러리는 예외를 던져 호출자가 처리하도록 해야 한다. CWE-382(J2EE Bad Practices: Use of System.exit())에 해당한다.",
    code: `if (error) throw new IllegalStateException(\"...\");  // exit 대신 예외 전파`
  },
  {
    c: "API오용",
    q: "Java에서 finalize() 메서드 오용에 대한 설명으로 가장 정확하지 않은(잘못된) 것은?",
    o: [
      "finalize()는 GC 시점에 반드시 즉시 호출되므로 자원 해제를 신뢰할 수 있다",
      "finalize()는 호출 시점이 불확실해 자원 해제 용도로 부적절하다",
      "finalize()에서 예외가 발생하면 무시되어 객체가 불완전 상태가 될 수 있다",
      "자원 해제는 try-with-resources나 명시적 close()가 권장된다"
    ],
    a: 0,
    e: "finalize()는 GC 시점에 실행되며 언제 호출될지, 심지어 호출될지조차 보장되지 않는다. 자원 해제를 finalize에 의존하는 것은 CWE-586(Explicit Call to Finalize) 등 나쁜 관례이다. 명시적 close()나 try-with-resources를 사용해야 한다. 보기 1은 사실과 반대이므로 '잘못된 설명'이다.",
    code: `try (InputStream in = new FileInputStream(f)) {\n    // 자동 close, finalize 의존 X\n}`
  },
  {
    c: "API오용",
    q: "파일을 새 바이트로 인코딩할 때 new String(bytes) 또는 str.getBytes()를 문자셋 인자 없이 호출하면 생기는 문제는?",
    o: [
      "플랫폼 기본 문자셋에 의존해 환경마다 다른 결과/깨짐이 발생한다 (CWE-176/CWE-172)",
      "항상 UTF-16으로 고정되어 안전하다",
      "컴파일 오류가 발생한다",
      "성능만 저하될 뿐 결과는 동일하다"
    ],
    a: 0,
    e: "문자셋을 명시하지 않으면 JVM이 실행되는 플랫폼의 기본 인코딩을 사용하므로, 개발/운영 환경이 다르면 문자 깨짐이나 부적절한 인코딩 처리(CWE-176) 및 검증 우회가 발생할 수 있다. 항상 StandardCharsets.UTF_8 등 명시적 문자셋을 지정해야 한다.",
    code: `byte[] b = str.getBytes(StandardCharsets.UTF_8);\nString s = new String(b, StandardCharsets.UTF_8);`
  },
  {
    c: "API오용",
    q: "SimpleDateFormat 인스턴스를 static 필드로 두고 여러 스레드가 공유해 format/parse를 호출할 때의 문제는?",
    o: [
      "스레드 비안전이라 값이 섞이거나 예외가 발생한다 → 지역 변수화 또는 DateTimeFormatter 사용",
      "SimpleDateFormat은 불변이라 아무 문제 없다",
      "static이면 자동으로 동기화되어 안전하다",
      "parse만 문제이고 format은 안전하다"
    ],
    a: 0,
    e: "SimpleDateFormat은 내부 Calendar 상태를 공유하는 가변 객체로 스레드 안전하지 않다. 공유하면 잘못된 날짜, NumberFormatException 등이 발생한다. 스레드마다 새로 생성하거나 ThreadLocal, 혹은 불변인 java.time.format.DateTimeFormatter를 사용해야 한다.",
    code: `// 안전: 불변 DateTimeFormatter\nstatic final DateTimeFormatter F = DateTimeFormatter.ofPattern(\"yyyy-MM-dd\");`
  },
  {
    c: "API오용",
    q: "Runtime.getRuntime().exec()를 사용할 때 다음 중 명령어 주입 위험을 줄이는 가장 올바른 방법은?",
    o: [
      "문자열 대신 문자열 배열(String[])로 인자를 분리해 전달한다",
      "exec에 전달할 문자열을 그대로 사용자 입력과 이어붙인다",
      "shell을 통해 실행하도록 sh -c 로 감싼다",
      "exec 대신 System.out.println으로 출력한다"
    ],
    a: 0,
    e: "exec(String) 오버로드는 공백 기준으로 토큰을 나누므로 사용자 입력을 이어붙이면 인자 조작/주입에 취약하다. 프로그램과 각 인자를 String[] 배열로 명시하면 셸 해석을 거치지 않아 안전성이 높아진다(CWE-78 완화). sh -c로 감싸는 것은 오히려 셸 주입 위험을 키운다.",
    code: `String[] cmd = {\"/usr/bin/convert\", userFile, \"out.png\"};\nRuntime.getRuntime().exec(cmd);   // 배열로 분리`
  },
  {
    c: "API오용",
    q: "다음 Python 코드에서 -O(최적화) 플래그로 실행하면 발생하는 문제는?",
    o: [
      "assert 문이 제거되어 권한 검증이 통째로 사라진다 (CWE-617)",
      "assert 는 항상 실행되므로 문제 없다",
      "assert 는 성능만 개선한다",
      "assert 는 예외를 로그로만 남긴다"
    ],
    a: 0,
    e: "python -O 로 실행하면 __debug__가 False가 되어 모든 assert 문이 컴파일 단계에서 제거된다. 보안 검증(권한 체크 등)을 assert로 구현하면 최적화 모드에서 검증이 사라져 우회된다. 보안 검증은 명시적 if/raise로 해야 한다. CWE-617(Reachable Assertion) 관련 오용이다.",
    code: `# 취약\nassert user.is_admin, \"forbidden\"\n# 올바름\nif not user.is_admin:\n    raise PermissionError(\"forbidden\")`
  },
  {
    c: "API오용",
    q: "신뢰할 수 없는 외부 입력을 pickle.loads()로 역직렬화할 때의 위험으로 가장 정확한 것은?",
    o: [
      "역직렬화 과정에서 임의 코드 실행이 가능하다 (CWE-502)",
      "pickle은 JSON보다 느릴 뿐 안전하다",
      "pickle은 정수만 저장하므로 안전하다",
      "pickle은 자동으로 서명을 검증한다"
    ],
    a: 0,
    e: "pickle은 역직렬화 시 __reduce__ 등을 통해 임의 객체 생성과 코드 실행을 허용한다. 신뢰할 수 없는 데이터를 pickle.loads로 처리하면 원격 코드 실행으로 이어질 수 있다(CWE-502: Deserialization of Untrusted Data). 외부 데이터는 json 등 안전한 포맷을 쓰거나 서명/검증을 적용해야 한다.",
    code: `import pickle\nobj = pickle.loads(untrusted_bytes)  # 위험: RCE 가능`
  },
  {
    c: "API오용",
    q: "Python에서 사용자 입력을 os.system() 또는 subprocess(..., shell=True)로 실행할 때의 주된 위험과 완화책은?",
    o: [
      "셸 메타문자로 명령어 주입 가능 → shell=False에 인자 리스트 사용 (CWE-78)",
      "os.system은 항상 안전하므로 그대로 사용",
      "shell=True가 오히려 주입을 막아준다",
      "eval로 감싸면 안전해진다"
    ],
    a: 0,
    e: "shell=True나 os.system은 문자열을 셸이 해석하므로 ;, |, `` 등 메타문자로 명령어 주입(CWE-78)이 가능하다. subprocess.run([\"cmd\", arg])처럼 shell=False(기본)로 인자를 리스트로 전달하면 셸 해석을 우회해 안전하다.",
    code: `import subprocess\n# 취약: subprocess.run(f\"ls {d}\", shell=True)\nsubprocess.run([\"ls\", d], shell=False)   # 안전`
  },
  {
    c: "API오용",
    q: "Python에서 사용자 입력을 eval()에 넘겨 계산하는 코드의 대안으로 가장 적절한 것은?",
    o: [
      "숫자 파싱은 ast.literal_eval 또는 명시적 파서를 사용한다",
      "eval을 exec으로 바꾼다",
      "eval 앞뒤에 공백을 제거한다",
      "eval 결과를 str로 변환한다"
    ],
    a: 0,
    e: "eval()은 임의 파이썬 표현식을 실행하므로 입력이 신뢰되지 않으면 코드 실행(CWE-95: Code Injection)에 취약하다. 리터럴만 안전하게 해석하려면 ast.literal_eval()을 쓰고, 수식 계산이 필요하면 제한된 파서를 구현해야 한다. exec은 더 위험하므로 대안이 아니다.",
    code: `import ast\nvalue = ast.literal_eval(user_input)  # 리터럴만 허용`
  },
  {
    c: "API오용",
    q: "리플렉션(Reflection)을 사용해 사용자 입력으로 클래스명을 받아 인스턴스화(Class.forName(input).newInstance())하는 코드의 위험은?",
    o: [
      "임의 클래스 로딩으로 의도치 않은 코드 실행이 가능하다 (CWE-470)",
      "리플렉션은 컴파일 오류만 유발한다",
      "리플렉션은 성능만 저하시킨다",
      "리플렉션은 항상 private 필드 접근을 막아 안전하다"
    ],
    a: 0,
    e: "외부 입력으로 클래스 이름을 지정해 리플렉션으로 로딩/생성하면 공격자가 위험한 클래스를 인스턴스화하거나 의도치 않은 동작을 유발할 수 있다. CWE-470(Unsafe Reflection). 허용 클래스 화이트리스트로 제한해야 한다.",
    code: `Set<String> allow = Set.of(\"com.app.SafeA\", \"com.app.SafeB\");\nif (!allow.contains(name)) throw new SecurityException();`
  }
);
window.__QBANK.THEORY.push(
  {
    type: "OX",
    cat: "API오용",
    q: "C 함수 gets()는 입력 길이를 제한하지 않아 버퍼 오버플로우를 유발하며 C11 표준에서 삭제되었다.",
    a: true,
    e: "gets()는 대상 버퍼 크기를 알 수 없어 임의 길이 입력으로 오버플로우를 일으키는 대표적 위험 함수(CWE-242)이며, C11에서 표준에서 제거되었다. fgets()로 대체해야 한다."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "Java에서 두 문자열의 내용을 비교할 때 == 연산자를 사용하는 것이 equals()보다 항상 안전하다.",
    a: false,
    e: "== 는 참조(주소) 동일성을 비교하므로 내용이 같아도 false가 될 수 있다. 문자열 내용 비교에는 equals()를 사용해야 한다(CWE-597). == 사용은 오히려 논리 오류와 인증 우회를 부를 수 있다."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "보안 토큰이나 세션 식별자 생성에는 java.util.Random 대신 java.security.SecureRandom을 사용해야 한다.",
    a: true,
    e: "java.util.Random은 예측 가능한 PRNG라 출력 일부만으로 이후 값을 유추할 수 있다. 보안 목적 난수는 암호학적으로 안전한 SecureRandom을 써야 한다(CWE-330/338)."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "SimpleDateFormat 인스턴스는 스레드 안전하므로 static 필드로 여러 스레드가 공유해도 문제가 없다.",
    a: false,
    e: "SimpleDateFormat은 가변 내부 상태를 가져 스레드 안전하지 않다. 공유 시 값이 섞이거나 예외가 발생한다. 스레드별 생성, ThreadLocal, 또는 불변인 DateTimeFormatter를 사용해야 한다."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "Python에서 보안 권한 검증을 assert 문으로 작성하면 -O 최적화 실행 시 검증이 제거되어 우회될 수 있다.",
    a: true,
    e: "python -O 실행 시 __debug__가 False가 되어 모든 assert가 제거된다. 보안 검증을 assert로 하면 최적화 모드에서 통째로 사라지므로, 명시적 if/raise를 사용해야 한다."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "라이브러리 내부에서 System.exit()를 호출하는 것은 권장되는 예외 처리 방식이다.",
    a: false,
    e: "라이브러리에서 System.exit()를 호출하면 이를 사용하는 애플리케이션 전체 JVM이 종료되어 가용성을 해친다(CWE-382). 라이브러리는 예외를 던져 호출자가 처리하게 해야 한다."
  },
  {
    type: "OX",
    cat: "API오용",
    q: "역방향 DNS 조회로 얻은 호스트 이름은 위조가 어렵기 때문에 접근 제어 결정에 신뢰해도 된다.",
    a: false,
    e: "역방향 DNS(PTR) 레코드는 공격자가 자신의 DNS 서버로 위조할 수 있어 신뢰할 수 없다. 이름 기반 보안 결정은 CWE-350에 해당하며, 검증 가능한 신원(mTLS 등)이나 IP 검증을 함께 써야 한다."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "다음 중 '본질적으로 위험한 함수 사용(CWE-242)' 또는 '위험한 함수'로 흔히 지목되는 C 함수가 아닌 것은?",
    o: ["gets", "strcpy", "sprintf", "snprintf"],
    a: 3,
    e: "gets, strcpy, sprintf, strcat, scanf(%s) 등은 크기 검사가 없어 위험 함수로 분류된다. 반면 snprintf는 대상 버퍼 크기를 인자로 받아 경계를 지키므로 안전한 대체 함수이다."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "Java에서 equals()만 재정의하고 hashCode()를 재정의하지 않았을 때 발생하는 대표적 문제는?",
    o: [
      "HashMap/HashSet에서 논리적으로 같은 키를 찾지 못한다",
      "컴파일이 실패한다",
      "GC가 동작하지 않는다",
      "toString이 null을 반환한다"
    ],
    a: 0,
    e: "equals/hashCode 계약상 같다고 판정된 객체는 같은 hashCode를 반환해야 한다. hashCode를 빼먹으면 해시 기반 컬렉션에서 키 조회가 실패한다(CWE-581)."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "다음 중 신뢰할 수 없는 데이터를 처리할 때 가장 위험한(임의 코드 실행 가능) Python API는?",
    o: ["pickle.loads", "json.loads", "int()", "str.strip()"],
    a: 0,
    e: "pickle.loads는 역직렬화 과정에서 임의 객체 생성과 코드 실행을 허용해 RCE로 이어질 수 있다(CWE-502). json.loads는 데이터만 파싱하며 코드 실행을 하지 않는다."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "subprocess로 외부 명령을 안전하게 실행하기 위한 가장 올바른 호출 형태는?",
    o: [
      "subprocess.run([\"ls\", path], shell=False)",
      "subprocess.run(f\"ls {path}\", shell=True)",
      "os.system(\"ls \" + path)",
      "eval(\"ls \" + path)"
    ],
    a: 0,
    e: "인자를 리스트로 전달하고 shell=False(기본)로 실행하면 셸 메타문자 해석을 우회해 명령어 주입(CWE-78)을 막는다. shell=True나 os.system, eval은 문자열을 셸/인터프리터가 해석해 주입에 취약하다."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "외부 입력으로 클래스명을 받아 Class.forName(input).getDeclaredConstructor().newInstance()로 객체를 만드는 코드의 CWE로 가장 적절한 것은?",
    o: [
      "CWE-470 (Unsafe Reflection)",
      "CWE-79 (XSS)",
      "CWE-352 (CSRF)",
      "CWE-200 (Information Exposure)"
    ],
    a: 0,
    e: "신뢰할 수 없는 입력으로 클래스를 로딩/인스턴스화하는 리플렉션 오용은 CWE-470에 해당한다. 허용 클래스 화이트리스트로 제한해야 한다."
  },
  {
    type: "MC",
    cat: "API오용",
    q: "폐기(deprecated)되었거나 지원이 종료된 함수를 계속 사용하는 보안약점의 CWE는?",
    o: ["CWE-477", "CWE-89", "CWE-611", "CWE-434"],
    a: 0,
    e: "폐기/사용 금지된(obsolete) 함수 사용은 CWE-477(Use of Obsolete Function)이다. CWE-89는 SQL 인젝션, CWE-611은 XXE, CWE-434는 위험한 파일 업로드이다."
  },
  {
    type: "SHORT",
    cat: "API오용",
    q: "Java에서 보안 목적의 예측 불가능한 난수를 생성하기 위해 java.util.Random 대신 사용해야 하는 클래스 이름은? (클래스명)",
    a: "SecureRandom",
    answers: ["SecureRandom", "java.security.SecureRandom"],
    e: "java.security.SecureRandom은 암호학적으로 안전한 난수 생성기로, 토큰/세션ID/키 생성 등 보안 목적에 사용해야 한다(CWE-330)."
  },
  {
    type: "SHORT",
    cat: "API오용",
    q: "C에서 strcpy나 sprintf처럼 대상 버퍼 크기를 검사하지 않아 오버플로우를 유발하는 함수를 대체하기 위해 '크기를 인자로 받는' 대표 함수 하나를 쓰시오. (예: 문자열 포맷용)",
    a: "snprintf",
    answers: ["snprintf", "strncpy", "strlcpy", "fgets"],
    e: "snprintf(및 strncpy, strlcpy, fgets 등)는 대상 크기를 지정해 경계를 넘지 않도록 한다. strncpy 사용 시에는 널 종료를 별도로 보장해야 한다."
  },
  {
    type: "SHORT",
    cat: "API오용",
    q: "Java의 new String(bytes)나 getBytes()에서 문자셋을 명시하지 않으면 무엇에 의존하게 되어 환경마다 다른 결과가 나오는가? (핵심 용어)",
    a: "플랫폼 기본 문자셋",
    answers: ["플랫폼 기본 문자셋", "기본 문자셋", "기본 인코딩", "플랫폼 기본 인코딩", "default charset"],
    e: "문자셋을 지정하지 않으면 JVM 실행 환경의 플랫폼 기본 문자셋(default charset)을 사용해 환경마다 인코딩 결과가 달라진다. StandardCharsets.UTF_8 등을 명시해야 한다(CWE-176)."
  },
  {
    type: "SHORT",
    cat: "API오용",
    q: "Python에서 사용자 입력 문자열을 안전하게 리터럴(숫자/리스트 등)로만 평가하기 위해 eval() 대신 사용해야 하는 표준 라이브러리 함수는? (모듈.함수 형태)",
    a: "ast.literal_eval",
    answers: ["ast.literal_eval", "literal_eval"],
    e: "ast.literal_eval은 파이썬 리터럴 구조만 안전하게 평가하며 임의 코드 실행을 허용하지 않아 eval()의 코드 인젝션 위험(CWE-95)을 피한다."
  },
  {
    type: "SHORT",
    cat: "API오용",
    q: "Java에서 자원 해제를 finalize()에 의존하는 대신, close() 호출을 자동화하기 위해 Java 7부터 제공하는 문법(구문) 이름은?",
    a: "try-with-resources",
    answers: ["try-with-resources", "try with resources", "트라이 위드 리소스"],
    e: "try-with-resources는 AutoCloseable 자원을 블록 종료 시 자동으로 close() 한다. GC 시점이 불확실한 finalize() 의존(CWE-586)을 피할 수 있다."
  }
);


(function(){
  var D = window.ACADEMY_DATA, Q = window.__QBANK;
  if(!D || !Q){ return; }
  var norm = function(s){ return (s||"").replace(/\s+/g," ").trim(); };
  var seenQ = {}; D.QUIZ.forEach(function(x){ seenQ[norm(x.q)] = 1; });
  var addQ = 0;
  (Q.QUIZ||[]).forEach(function(x){ var k=norm(x.q); if(!seenQ[k]){ seenQ[k]=1; D.QUIZ.push(x); addQ++; } });
  var seenT = {}; D.THEORY.forEach(function(x){ seenT[norm(x.q)] = 1; });
  var addT = 0;
  (Q.THEORY||[]).forEach(function(x){ var k=norm(x.q); if(!seenT[k]){ seenT[k]=1; D.THEORY.push(x); addT++; } });
  try { if (typeof console!=="undefined" && console.debug) console.debug("[qbank] +"+addQ+" QUIZ, +"+addT+" THEORY"); } catch(e){}
})();
