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
