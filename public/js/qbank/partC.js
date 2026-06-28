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
  { type:"SHORT", cat:"시간상태", q:"중첩 수량자 등으로 정규식 백트래킹이 폭발해 CPU를 고갈시키는 서비스 거부 공격의 약어는?", a:"ReDoS", answers:["Regular expression Denominator of Service","정규식 DoS","정규표현식 서비스 거부"], e:"Regular expression Denial of Service." },
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
