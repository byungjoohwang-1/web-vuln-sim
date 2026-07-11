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
