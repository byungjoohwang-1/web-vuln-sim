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
