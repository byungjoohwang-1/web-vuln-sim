# -*- coding: utf-8 -*-
"""MISRA C++:2023 대표 규칙 — 위반/준수 예제 (사내 교육용, 규범 원문 비복제·자체 작성)"""
RULES = [
 {'id':'Rule 0.0.1','cat':'Required · Decidable',
  'title':'함수에 도달 불가능한(dead) 문장을 두지 않는다',
  'bad': r"""int classify(int x) {
    if (x > 0) {
        return 1;
        x = 0;            // 도달 불가능: return 이후 실행되지 않음
    }
    return -1;
}""",
  'good': r"""int classify(int x) {
    if (x > 0) {
        return 1;
    }
    return -1;
}""",
  'why':'return 이후의 문장은 절대 실행되지 않는 죽은 코드로, 의도한 로직이 누락됐다는 신호다. 도달 불가능 코드를 제거하면 결함과 오해를 막는다.'},

 {'id':'Rule 0.1.1','cat':'Advisory · Undecidable',
  'title':'지역 객체에 불필요하게 값을 기록하지 않는다',
  'bad': r"""int sum(const int* a, int n) {
    int total = 0;
    total = 100;          // 곧바로 덮어써지는 무의미한 기록
    for (int i = 0; i < n; ++i) {
        total += a[i];
    }
    return total;
}""",
  'good': r"""int sum(const int* a, int n) {
    int total = 0;
    for (int i = 0; i < n; ++i) {
        total += a[i];
    }
    return total;
}""",
  'why':'사용되기 전에 덮어써지는 대입은 죽은 저장(dead store)으로, 흔히 논리 오류의 흔적이다. 불필요한 기록을 없애면 의도가 분명해진다.'},

 {'id':'Rule 0.1.2','cat':'Required · Undecidable',
  'title':'함수가 반환한 값은 사용한다',
  'bad': r"""[[nodiscard]] int parse(const std::string& s);

void run(const std::string& s) {
    parse(s);             // 반환된 결과(성공/실패)를 무시
}""",
  'good': r"""[[nodiscard]] int parse(const std::string& s);

void run(const std::string& s) {
    const int rc = parse(s);
    if (rc != 0) {
        handle_error(rc);
    }
}""",
  'why':'함수가 의미 있게 반환한 값을 버리면 오류 코드나 결과가 묻혀 결함이 숨는다. 반환값을 검사하거나 명시적으로 활용해야 한다.'},

 {'id':'Rule 0.2.2','cat':'Required · Decidable',
  'title':'명명된 함수 매개변수는 최소 한 번 사용한다',
  'bad': r"""int area(int width, int height) {
    return width * width;   // height 매개변수가 사용되지 않음
}""",
  'good': r"""int area(int width, int height) {
    return width * height;
}""",
  'why':'선언만 되고 쓰이지 않는 매개변수는 오타나 논리 누락의 징후다. 의도적으로 미사용이라면 이름을 생략해 의도를 명시한다.'},

 {'id':'Rule 4.6.1','cat':'Required · Undecidable',
  'title':'한 메모리 위치에 대한 연산의 평가 순서를 적절히 한정한다',
  'bad': r"""int i = 0;
int arr[3] = {0, 0, 0};
arr[i] = i++;             // 같은 시퀀스 포인트 내 i 읽기/쓰기 → 미정의 동작""",
  'good': r"""int i = 0;
int arr[3] = {0, 0, 0};
arr[i] = i;
++i;                      // 부작용을 분리해 순서를 확정""",
  'why':'동일 시퀀스 안에서 같은 객체를 읽고 쓰면 평가 순서가 한정되지 않아 미정의 동작이 된다. 부작용을 별도 문장으로 분리해야 한다.'},

 {'id':'Rule 6.4.1','cat':'Required · Decidable',
  'title':'내부 범위 변수가 외부 범위 변수를 가리지(shadow) 않게 한다',
  'bad': r"""int compute(int value) {
    int result = value * 2;
    if (value > 10) {
        int result = value + 1;  // 바깥 result 를 가림
        return result;
    }
    return result;
}""",
  'good': r"""int compute(int value) {
    int result = value * 2;
    if (value > 10) {
        int adjusted = value + 1;
        return adjusted;
    }
    return result;
}""",
  'why':'이름 가림(shadowing)은 어느 변수를 참조하는지 혼동시켜 미묘한 버그를 만든다. 안쪽 변수에 별개의 이름을 부여하면 모호함이 사라진다.'},

 {'id':'Rule 6.7.1','cat':'Required · Decidable',
  'title':'지역 변수에 정적 저장 기간을 부여하지 않는다',
  'bad': r"""int next_id() {
    static int counter = 0;   // 함수 지역의 정적 상태 → 재진입·동시성 위험
    return ++counter;
}""",
  'good': r"""int next_id(int& counter) {
    return ++counter;         // 상태를 호출자가 명시적으로 소유
}""",
  'why':'함수 지역의 정적 변수는 숨은 가변 상태로 재진입성과 스레드 안전성을 해친다. 상태를 외부에서 명시적으로 전달·소유하게 한다.'},

 {'id':'Rule 6.8.2','cat':'Mandatory · Undecidable',
  'title':'자동 저장 기간 지역 변수의 참조/포인터를 반환하지 않는다',
  'bad': r"""const int& first_element() {
    int local[3] = {1, 2, 3};
    return local[0];          // 함수 종료 후 소멸하는 지역에 대한 참조
}""",
  'good': r"""int first_element() {
    int local[3] = {1, 2, 3};
    return local[0];          // 값으로 복사해 반환
}""",
  'why':'지역 객체는 함수 반환과 함께 소멸하므로 그 참조/포인터를 반환하면 매달린(dangling) 접근이 되어 미정의 동작이다. 값으로 반환하거나 수명이 긴 저장소를 사용한다.'},

 {'id':'Rule 7.0.2','cat':'Required · Undecidable',
  'title':'bool 타입으로의 부적절한 암시적 변환을 하지 않는다',
  'bad': r"""void process(int* ptr) {
    bool ok = ptr;            // 포인터가 bool 로 암시적 변환
    if (ok) { /* ... */ }
}""",
  'good': r"""void process(int* ptr) {
    const bool ok = (ptr != nullptr);  // 의도를 명시적으로 표현
    if (ok) { /* ... */ }
}""",
  'why':'포인터나 정수가 bool 로 암시적 변환되면 의도가 흐려지고 오탐 비교가 생긴다. 명시적 비교로 진리값을 만든다.'},

 {'id':'Rule 7.0.5','cat':'Required · Undecidable',
  'title':'정수 승격·통상 산술 변환이 피연산자의 부호/타입 범주를 바꾸지 않게 한다',
  'bad': r"""unsigned int u = 1U;
int s = -1;
if (u > s) {              // s 가 거대한 unsigned 로 변환 → 의도와 반대
    /* ... */
}""",
  'good': r"""unsigned int u = 1U;
int s = -1;
if (s < 0 || u > static_cast<unsigned int>(s)) {
    /* 부호를 명시적으로 고려 */
}""",
  'why':'부호 있는/없는 정수가 한 식에서 섞이면 암시적 변환으로 부호가 뒤바뀌어 비교 결과가 역전된다. 변환을 명시적으로 통제해야 한다.'},

 {'id':'Rule 7.11.1','cat':'Required · Decidable',
  'title':'널 포인터 상수는 nullptr 형태만 사용한다',
  'bad': r"""int* p = 0;               // 0 을 널 포인터 상수로 사용
char* q = NULL;           // NULL 매크로 사용""",
  'good': r"""int* p = nullptr;
char* q = nullptr;""",
  'why':'0 이나 NULL 은 정수 문맥과 혼동되어 오버로드 해석 오류를 일으킨다. 타입 안전한 nullptr 만 사용한다.'},

 {'id':'Rule 8.2.1','cat':'Required · Undecidable',
  'title':'가상 기반 클래스를 파생 클래스로 변환할 때 dynamic_cast 만 사용한다',
  'bad': r"""struct Base { virtual ~Base() = default; };
struct Derived : virtual Base {};

void use(Base& b) {
    Derived& d = static_cast<Derived&>(b);  // 가상 기반 → static_cast 불가/위험
    (void)d;
}""",
  'good': r"""struct Base { virtual ~Base() = default; };
struct Derived : virtual Base {};

void use(Base& b) {
    if (auto* d = dynamic_cast<Derived*>(&b)) {
        (void)d;          // 실행시간 타입 검사로 안전하게 다운캐스트
    }
}""",
  'why':'가상 기반 클래스는 static_cast 로 파생으로 내려갈 수 없거나 안전하지 않다. dynamic_cast 로 실행시간에 타입을 검증해야 한다.'},

 {'id':'Rule 8.2.2','cat':'Required · Decidable',
  'title':'C 스타일 캐스트와 함수형 표기 캐스트를 사용하지 않는다',
  'bad': r"""double d = 3.9;
int n = (int)d;           // C 스타일 캐스트
long L = long(d);         // 함수형 표기 캐스트""",
  'good': r"""double d = 3.9;
int n = static_cast<int>(d);
long L = static_cast<long>(d);""",
  'why':'C 스타일 캐스트는 const 제거·재해석 등 위험한 변환을 한 문법에 숨겨 의도를 가린다. 명시적 C++ 캐스트로 의도와 위험을 드러낸다.'},

 {'id':'Rule 8.2.3','cat':'Required · Decidable',
  'title':'캐스트로 포인터/참조의 const·volatile 한정을 제거하지 않는다',
  'bad': r"""void mutate(const int* p) {
    int* q = const_cast<int*>(p);  // const 제거 후 쓰기 → 미정의 동작 위험
    *q = 42;
}""",
  'good': r"""void mutate(int* p) {
    *p = 42;              // 처음부터 비-const 인터페이스를 사용
}""",
  'why':'const 를 캐스트로 벗겨내 원래 const 객체를 수정하면 미정의 동작이 된다. 가변성이 필요하면 인터페이스 자체를 비-const 로 설계한다.'},

 {'id':'Rule 8.2.5','cat':'Required · Decidable',
  'title':'reinterpret_cast 를 사용하지 않는다',
  'bad': r"""long addr = 0x1000;
int* p = reinterpret_cast<int*>(addr);  // 임의 비트 재해석
*p = 0;""",
  'good': r"""// 메모리 매핑 등 불가피한 경우라도 잘 정의된 추상화를 사용
std::array<std::byte, 4> buffer{};
int value = 0;
std::memcpy(&value, buffer.data(), sizeof(value));  // 타입 안전한 복사""",
  'why':'reinterpret_cast 는 타입 시스템을 우회해 정렬/별칭 규칙 위반과 미정의 동작을 초래한다. std::memcpy 등 잘 정의된 수단으로 대체한다.'},

 {'id':'Rule 8.2.10','cat':'Required · Undecidable',
  'title':'함수가 직접·간접으로 자기 자신을 호출(재귀)하지 않는다',
  'bad': r"""unsigned long fact(unsigned n) {
    return (n <= 1) ? 1UL : n * fact(n - 1);  // 재귀 → 스택 사용량 예측 곤란
}""",
  'good': r"""unsigned long fact(unsigned n) {
    unsigned long result = 1UL;
    for (unsigned i = 2; i <= n; ++i) {
        result *= i;      // 반복으로 변환해 스택 사용량을 한정
    }
    return result;
}""",
  'why':'재귀는 스택 깊이를 정적으로 한정하기 어려워 안전 임계 시스템에서 스택 오버플로 위험이 있다. 반복 구조로 변환한다.'},

 {'id':'Rule 8.7.1','cat':'Required · Undecidable',
  'title':'포인터 산술로 유효하지 않은 포인터를 만들지 않는다',
  'bad': r"""void fill(int* a, int n) {
    for (int i = 0; i <= n; ++i) {   // <= 로 인해 a[n] 한 칸 초과 접근
        a[i] = 0;
    }
}""",
  'good': r"""void fill(int* a, int n) {
    for (int i = 0; i < n; ++i) {    // 배열 경계 내로 한정
        a[i] = 0;
    }
}""",
  'why':'배열 경계를 한 칸이라도 넘는 포인터 산술은 유효하지 않은 포인터를 만들어 버퍼 오버런과 미정의 동작을 일으킨다. 인덱스 범위를 엄격히 한정한다.'},

 {'id':'Rule 8.7.2','cat':'Required · Undecidable',
  'title':'포인터 뺄셈은 같은 배열의 원소를 가리킬 때만 한다',
  'bad': r"""int x = 0, y = 0;
std::ptrdiff_t d = &x - &y;   // 서로 다른 객체 간 포인터 뺄셈 → 미정의""",
  'good': r"""int arr[4] = {0, 1, 2, 3};
std::ptrdiff_t d = &arr[3] - &arr[0];  // 같은 배열 내에서만 뺄셈""",
  'why':'서로 다른 객체의 주소를 빼면 결과가 미정의다. 포인터 뺄셈은 동일한 배열의 원소 사이에서만 의미가 있다.'},

 {'id':'Rule 8.18.1','cat':'Mandatory · Undecidable',
  'title':'객체를 겹치는(overlapping) 대상에 복사하지 않는다',
  'bad': r"""void copy_self(char* p) {
    std::memcpy(p, p + 1, 8);  // 원본과 대상 영역이 겹침 → 미정의""",
  'good': r"""void copy_self(char* p) {
    std::memmove(p, p + 1, 8); // 겹침을 허용하는 memmove 사용""",
  'why':'겹치는 메모리 영역에 대한 복사는 미정의 동작이다. 겹침이 있을 수 있으면 memmove 처럼 겹침을 정의하는 연산을 사용한다.'},

 {'id':'Rule 8.19.1','cat':'Advisory · Decidable',
  'title':'콤마 연산자를 사용하지 않는다',
  'bad': r"""int a = 0, b = 0;
int c = (a = 1, b = 2, a + b);  // 콤마 연산자로 부작용을 한 식에 응축""",
  'good': r"""int a = 1;
int b = 2;
int c = a + b;        // 각 단계를 분리""",
  'why':'콤마 연산자는 여러 부작용을 한 식에 숨겨 가독성과 평가 순서 이해를 해친다. 문장을 분리해 명확히 한다.'},

 {'id':'Rule 9.4.1','cat':'Required · Decidable',
  'title':'모든 if … else if 연쇄는 else 로 종결한다',
  'bad': r"""int grade(int s) {
    int g;
    if (s >= 90) g = 1;
    else if (s >= 80) g = 2;   // 나머지 경우가 처리되지 않음 → g 미초기화 가능
    return g;
}""",
  'good': r"""int grade(int s) {
    int g;
    if (s >= 90) g = 1;
    else if (s >= 80) g = 2;
    else g = 3;            // 모든 경우를 명시적으로 처리
    return g;
}""",
  'why':'else 누락 시 처리되지 않는 입력에서 변수가 미초기화되거나 의도가 불명확해진다. 마지막 else 로 모든 경우를 명시한다.'},

 {'id':'Rule 9.4.2','cat':'Required · Decidable',
  'title':'switch 문은 default 와 break 등 구조를 적절히 갖춘다',
  'bad': r"""void handle(int code) {
    switch (code) {
        case 1: act_a();      // break 누락 → 의도치 않은 fall-through
        case 2: act_b(); break;
    }                          // default 없음
}""",
  'good': r"""void handle(int code) {
    switch (code) {
        case 1: act_a(); break;
        case 2: act_b(); break;
        default: act_default(); break;
    }
}""",
  'why':'break 누락은 의도치 않은 fall-through 를, default 누락은 미처리 입력을 만든다. 각 case 를 break 로 닫고 default 를 두어야 한다.'},

 {'id':'Rule 9.6.1','cat':'Advisory · Decidable',
  'title':'goto 문을 사용하지 않는다',
  'bad': r"""void scan(int n) {
    int i = 0;
loop:
    if (i < n) {
        process(i);
        ++i;
        goto loop;        // 제어 흐름을 비구조적으로 점프
    }
}""",
  'good': r"""void scan(int n) {
    for (int i = 0; i < n; ++i) {
        process(i);       // 구조적 반복으로 표현
    }
}""",
  'why':'goto 는 제어 흐름을 비구조적으로 만들어 분석과 유지보수를 어렵게 한다. 반복·분기 구조로 대체한다.'},

 {'id':'Rule 11.3.1','cat':'Advisory · Decidable',
  'title':'C 스타일 배열 타입 변수를 선언하지 않는다',
  'bad': r"""void init() {
    int data[10];         // C 스타일 배열: 경계 정보 손실, 포인터 붕괴
    for (int i = 0; i < 10; ++i) data[i] = i;
}""",
  'good': r"""void init() {
    std::array<int, 10> data{};
    for (std::size_t i = 0; i < data.size(); ++i) {
        data[i] = static_cast<int>(i);  // 크기 정보와 경계 검사 지원
    }
}""",
  'why':'C 스타일 배열은 함수 인자로 넘길 때 포인터로 붕괴해 크기 정보를 잃고 경계 오류를 유발한다. std::array 로 크기를 타입에 보존한다.'},

 {'id':'Rule 11.6.1','cat':'Advisory · Undecidable',
  'title':'모든 변수를 초기화한다',
  'bad': r"""int risky() {
    int total;            // 초기화되지 않음
    if (rare_condition()) {
        total = 1;
    }
    return total;         // 일부 경로에서 미초기화 값 반환
}""",
  'good': r"""int risky() {
    int total = 0;        // 선언 시 초기화
    if (rare_condition()) {
        total = 1;
    }
    return total;
}""",
  'why':'초기화되지 않은 변수는 비결정적 쓰레기 값을 가져 미정의 동작과 재현 불가능한 버그를 만든다. 선언 시점에 항상 초기화한다.'},

 {'id':'Rule 11.6.2','cat':'Mandatory · Undecidable',
  'title':'객체의 값을 설정하기 전에 읽지 않는다',
  'bad': r"""int compute() {
    int v;                // 미설정
    int w = v + 1;        // 설정 전 읽기 → 미정의 동작
    return w;
}""",
  'good': r"""int compute() {
    int v = 5;            // 읽기 전에 설정
    int w = v + 1;
    return w;
}""",
  'why':'값이 설정되기 전 객체를 읽으면 부정 동작과 보안 취약점이 발생한다. 모든 읽기 이전에 명확히 값을 기록해야 한다.'},

 {'id':'Rule 12.3.1','cat':'Required · Decidable',
  'title':'union 키워드를 사용하지 않는다',
  'bad': r"""union Value {
    int i;
    float f;              // 비활성 멤버 접근 시 타입 혼동·미정의 동작
};""",
  'good': r"""// 타입 안전한 합 타입을 사용
std::variant<int, float> value;
value = 42;
if (std::holds_alternative<int>(value)) {
    int i = std::get<int>(value);
    (void)i;
}""",
  'why':'union 은 비활성 멤버를 읽는 타입 혼동(type punning)으로 미정의 동작을 일으킨다. std::variant 같은 타입 안전한 대안을 사용한다.'},

 {'id':'Rule 13.3.1','cat':'Required · Decidable',
  'title':'virtual·override·final 지정자를 적절히 사용한다',
  'bad': r"""struct Base { virtual void run(int) {} };
struct Derived : Base {
    void run(long) {}     // 오버라이드 의도였으나 시그니처 불일치 → 새 함수
};""",
  'good': r"""struct Base { virtual void run(int) {} };
struct Derived : Base {
    void run(int) override {}  // override 로 시그니처 일치를 강제
};""",
  'why':'override 없이 가상 함수를 재정의하면 시그니처 불일치가 조용히 새 함수를 만들어 다형성이 깨진다. override 지정자로 컴파일러가 검증하게 한다.'},

 {'id':'Rule 15.1.3','cat':'Required · Decidable',
  'title':'단일 인자로 호출 가능한 생성자·변환 연산자는 explicit 로 한다',
  'bad': r"""struct Meters {
    Meters(double v) : value(v) {}  // 암시적 변환 허용
    double value;
};
void travel(Meters m);
// travel(3.0);  // double 이 조용히 Meters 로 변환됨""",
  'good': r"""struct Meters {
    explicit Meters(double v) : value(v) {}  // 암시적 변환 차단
    double value;
};
void travel(Meters m);
// travel(Meters{3.0});  // 변환을 명시적으로 요구""",
  'why':'단일 인자 생성자가 암시적이면 의도치 않은 타입 변환이 조용히 일어나 단위/의미 오류를 만든다. explicit 로 의도적 변환만 허용한다.'},

 {'id':'Rule 15.1.2','cat':'Advisory · Undecidable',
  'title':'생성자는 모든 기반 클래스와 멤버를 명시적으로 초기화한다',
  'bad': r"""struct Sensor {
    int id;
    double value;
    Sensor(int i) {       // value 가 초기화 목록에서 누락됨
        id = i;
    }
};""",
  'good': r"""struct Sensor {
    int id;
    double value;
    Sensor(int i) : id(i), value(0.0) {}  // 모든 멤버를 초기화 목록에서 설정
};""",
  'why':'생성자에서 멤버를 초기화 목록으로 설정하지 않으면 미초기화 멤버나 불필요한 이중 대입이 생긴다. 모든 멤버/기반을 초기화 목록에서 명시한다.'},

 {'id':'Rule 16.5.2','cat':'Required · Decidable',
  'title':'주소 연산자(&)를 오버로드하지 않는다',
  'bad': r"""struct Widget {
    Widget* operator&() { return nullptr; }  // & 의 의미를 왜곡
};""",
  'good': r"""struct Widget {
    Widget* address() { return this; }  // 명시적 멤버 함수로 제공
};""",
  'why':'단항 & 를 오버로드하면 객체의 실제 주소를 얻는 표준 의미가 깨져 일반 코드와 표준 라이브러리를 오작동시킨다. 별도 명명 함수로 의도를 표현한다.'},

 {'id':'Rule 18.1.1','cat':'Required · Decidable',
  'title':'예외 객체는 포인터 타입을 갖지 않는다(값으로 throw)',
  'bad': r"""void fail() {
    throw new std::runtime_error("boom");  // 포인터를 throw → 누수·소유권 모호
}""",
  'good': r"""void fail() {
    throw std::runtime_error("boom");      // 값으로 throw
}""",
  'why':'포인터를 throw 하면 누가 delete 할지 불분명해 메모리 누수와 슬라이싱 위험이 생긴다. 예외 객체는 값으로 던진다.'},

 {'id':'Rule 18.3.2','cat':'Required · Decidable',
  'title':'클래스 타입 예외는 const 참조 또는 참조로 잡는다',
  'bad': r"""try {
    risky();
} catch (std::exception e) {   // 값으로 catch → 객체 슬라이싱 발생
    log(e.what());
}""",
  'good': r"""try {
    risky();
} catch (const std::exception& e) {  // const 참조로 catch
    log(e.what());
}""",
  'why':'예외를 값으로 잡으면 파생 예외 정보가 잘려나가는 슬라이싱이 일어난다. const 참조로 잡아 다형성과 정보를 보존한다.'},

 {'id':'Rule 18.4.1','cat':'Required · Undecidable',
  'title':'예외에 안전하지 않은 함수는 noexcept 로 표시한다',
  'bad': r"""struct Buffer {
    Buffer(Buffer&& other) { /* 자원 이동, 던질 수 있음 */ }
    // 이동 생성자가 noexcept 가 아니면 컨테이너가 복사로 폴백
};""",
  'good': r"""struct Buffer {
    Buffer(Buffer&& other) noexcept { /* 절대 던지지 않음 */ }
};""",
  'why':'이동 연산이 noexcept 가 아니면 표준 컨테이너가 강한 예외 보증을 위해 비싼 복사로 폴백하고, 던지면 안 되는 함수가 던지면 즉시 종료된다. 적절히 noexcept 를 명시한다.'},

 {'id':'Rule 19.0.2','cat':'Required · Decidable',
  'title':'함수형(function-like) 매크로를 정의하지 않는다',
  'bad': r"""#define SQUARE(x) x * x
int r = SQUARE(1 + 2);   // 1 + 2 * 1 + 2 = 5, 의도(9)와 다름""",
  'good': r"""constexpr int square(int x) { return x * x; }
int r = square(1 + 2);   // 항상 9, 타입 안전""",
  'why':'함수형 매크로는 인자 재평가와 우선순위 함정으로 미묘한 버그를 만들고 타입 검사도 받지 않는다. constexpr/inline 함수로 대체한다.'},

 {'id':'Rule 19.3.4','cat':'Required · Decidable',
  'title':'매크로 인자가 올바르게 전개되도록 괄호를 사용한다',
  'bad': r"""#define DOUBLE(x) x + x
int r = DOUBLE(3) * 2;   // 3 + 3 * 2 = 9, 의도(12)와 다름""",
  'good': r"""#define DOUBLE(x) ((x) + (x))
int r = DOUBLE(3) * 2;   // ((3)+(3))*2 = 12""",
  'why':'매크로 본문과 인자에 괄호가 없으면 연산자 우선순위로 인해 예기치 않은 결과가 나온다. 매크로가 불가피하면 전체와 각 인자를 괄호로 감싼다.'},

 {'id':'Rule 21.6.1','cat':'Advisory · Undecidable',
  'title':'동적 메모리(직접 new/delete)를 사용하지 않는다',
  'bad': r"""void work() {
    int* p = new int(42);  // 직접 new → 예외 경로에서 누수 위험
    use(*p);
    delete p;
}""",
  'good': r"""void work() {
    auto p = std::make_unique<int>(42);  // RAII 로 자동 해제
    use(*p);
}""",
  'why':'직접 new/delete 는 예외나 조기 반환 경로에서 누수와 이중 해제를 유발한다. 스마트 포인터(RAII)로 수명을 자동 관리한다.'},

 {'id':'Rule 21.6.5','cat':'Required · Undecidable',
  'title':'불완전 클래스 타입에 대한 포인터를 delete 하지 않는다',
  'bad': r"""struct Impl;            // 전방 선언만 존재(불완전 타입)
void destroy(Impl* p) {
    delete p;              // 소멸자 미인식 → 미정의 동작
}""",
  'good': r"""struct Impl { ~Impl(); };  // 완전한 정의가 보이는 시점에서 해제
void destroy(Impl* p) {
    delete p;
}""",
  'why':'불완전 타입을 delete 하면 컴파일러가 소멸자를 호출하지 못해 자원 누수와 미정의 동작이 발생한다. 해제 지점에서 타입이 완전해야 한다.'},

 {'id':'Rule 23.11.1','cat':'Advisory · Decidable',
  'title':'shared_ptr·unique_ptr 의 원시 포인터 생성자를 쓰지 않는다',
  'bad': r"""std::shared_ptr<int> a(new int(1));
std::shared_ptr<int> b = a;
// new 표현식이 노출되어 예외 안전성·소유권이 약화""",
  'good': r"""auto a = std::make_shared<int>(1);  // 단일 할당, 예외 안전
auto b = a;""",
  'why':'원시 포인터로 스마트 포인터를 만들면 할당과 제어블록이 분리되어 예외 시 누수가 가능하다. make_shared/make_unique 가 더 안전하고 효율적이다.'},

 {'id':'Rule 28.6.3','cat':'Required · Undecidable',
  'title':'이동된(moved-from) 상태의 객체를 다시 사용하지 않는다',
  'bad': r"""std::string s = "data";
std::string t = std::move(s);
std::size_t n = s.size();   // 이동 후 불특정 상태인 s 를 사용""",
  'good': r"""std::string s = "data";
std::string t = std::move(s);
s = "reset";                // 재사용 전 다시 명확한 값으로 설정
std::size_t n = s.size();""",
  'why':'std::move 후 원본은 유효하지만 불특정한 상태이므로 값을 가정하고 사용하면 안 된다. 재사용 전 명시적으로 새 값을 대입한다.'},

 {'id':'Rule 30.0.1','cat':'Required · Decidable',
  'title':'C 라이브러리 입출력 함수를 사용하지 않는다',
  'bad': r"""#include <cstdio>
void dump(const char* msg) {
    printf("%s\n", msg);   // 타입 비검사 가변 인자 → 포맷 취약점
}""",
  'good': r"""#include <iostream>
void dump(const std::string& msg) {
    std::cout << msg << '\n';  // 타입 안전한 스트림 입출력
}""",
  'why':'printf 계열은 포맷 문자열과 인자 타입을 검사하지 않아 포맷 스트링 취약점과 미정의 동작을 낳는다. 타입 안전한 C++ 스트림을 사용한다.'},
]
