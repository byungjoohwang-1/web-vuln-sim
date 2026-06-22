# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트2: A9~A15·M6~M9) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'A9-3-1','cat':'Required · Automated',
  'title':'멤버 함수가 내부 데이터에 대한 비-const 핸들을 반환하지 않게 한다',
  'bad': r"""class Buf {
    std::vector<int> data_;
public:
    std::vector<int>& data() { return data_; }   // 내부 캡슐화 파괴
};""",
  'good': r"""class Buf {
    std::vector<int> data_;
public:
    const std::vector<int>& data() const { return data_; }
};""",
  'why':'내부 데이터의 비-const 참조/포인터를 노출하면 캡슐화가 깨지고 클래스 불변식을 외부에서 위반할 수 있다. const 접근만 제공하거나 동작 메서드를 둔다.'},

 {'id':'A9-5-1','cat':'Required · Automated',
  'title':'union 을 사용하지 않는다(std::variant 사용)',
  'bad': r"""union Value { int i; double d; };   // 활성 멤버 추적 불가""",
  'good': r"""using Value = std::variant<int, double>;   // 타입 안전 합집합""",
  'why':'union은 현재 활성 멤버를 추적하지 않아 잘못된 멤버 접근으로 미정의 동작이 된다. 타입 안전한 std::variant를 사용한다.'},

 {'id':'A10-2-1','cat':'Required · Automated',
  'title':'파생 클래스에서 비가상 멤버 함수를 재정의하지 않는다',
  'bad': r"""struct Base { void f() {} };
struct Derived : Base { void f() {} };   // 숨김 — 정적 타입에 따라 호출 달라짐""",
  'good': r"""struct Base { virtual void f() {} };
struct Derived : Base { void f() override {} };""",
  'why':'비가상 함수를 재정의하면 다형성이 아닌 이름 숨김이 되어 정적 타입에 따라 다른 함수가 호출된다. 다형성이 필요하면 virtual+override를 쓴다.'},

 {'id':'A10-3-1','cat':'Required · Automated',
  'title':'가상 함수 선언에 virtual/override/final 중 정확히 하나만 사용한다',
  'bad': r"""struct D : B { virtual void f() override; };   // virtual+override 중복""",
  'good': r"""struct D : B { void f() override; };""",
  'why':'재정의에 virtual과 override를 함께 쓰면 의도가 모호하고 중복이다. 재정의에는 override만, 새 가상 함수에는 virtual만 사용한다.'},

 {'id':'A10-3-2','cat':'Required · Automated',
  'title':'재정의하는 모든 가상 함수에 override 를 표시한다',
  'bad': r"""struct D : B { void f(); };   // 시그니처 오타 시 새 함수가 됨(조용한 버그)""",
  'good': r"""struct D : B { void f() override; };""",
  'why':'override를 빠뜨리면 시그니처 불일치 시 재정의가 아닌 새 함수가 만들어져도 컴파일러가 잡지 못한다. override로 재정의 의도를 검증받는다.'},

 {'id':'A11-3-1','cat':'Required · Automated',
  'title':'friend 선언을 사용하지 않는다',
  'bad': r"""class Account {
    friend class Auditor;   // 캡슐화 우회
    double balance_;
};""",
  'good': r"""class Account {
    double balance_;
public:
    double balance() const { return balance_; }   // 명시적 인터페이스
};""",
  'why':'friend는 캡슐화를 우회해 결합도를 높이고 불변식 보호를 약화한다. 필요한 접근은 명시적 공개 인터페이스로 제공한다.'},

 {'id':'A12-0-1','cat':'Required · Automated',
  'title':'사용자 정의 소멸자/복사/이동 중 하나가 있으면 모두 정의한다(Rule of Five)',
  'bad': r"""class R {
    int* p_;
public:
    ~R() { delete p_; }   // 소멸자만 — 복사 시 이중 해제""",
  'good': r"""class R {
    std::unique_ptr<int> p_;   // Rule of Zero: 특수 멤버 불필요
};""",
  'why':'특수 멤버 중 일부만 정의하면 컴파일러 생성 복사/이동이 자원을 잘못 다뤄 이중 해제·누수가 난다. 모두 정의하거나(스마트포인터로) 모두 생략한다.'},

 {'id':'A12-1-1','cat':'Required · Automated',
  'title':'생성자는 모든 기반 클래스와 멤버를 명시적으로 초기화한다',
  'bad': r"""class P {
    int x_; int y_;
public:
    P() { x_ = 0; }   // y_ 미초기화""",
  'good': r"""class P {
    int x_; int y_;
public:
    P() : x_{0}, y_{0} {}
};""",
  'why':'초기화하지 않은 멤버는 불확정 값을 가져 미정의 동작을 부른다. 모든 멤버·기반을 초기화 목록에서 명시 초기화한다.'},

 {'id':'A12-1-4','cat':'Required · Automated',
  'title':'단일 인자 생성자는 explicit 로 선언한다',
  'bad': r"""struct Meters { Meters(double v); };   // 암시적 변환 허용
void f(Meters m);
f(3.0);               // double이 조용히 Meters로""",
  'good': r"""struct Meters { explicit Meters(double v); };
f(Meters{3.0});""",
  'why':'단일 인자 생성자가 explicit가 아니면 의도치 않은 암시적 변환이 일어난다. explicit로 명시적 생성만 허용한다.'},

 {'id':'A12-8-1','cat':'Required · Automated',
  'title':'이동/복사 연산은 이동/복사 외의 부작용을 갖지 않는다',
  'bad': r"""S(const S& o) { ++g_counter; copy(o); }   // 전역 카운터 부작용""",
  'good': r"""S(const S& o) { copy(o); }   // 복사만 수행""",
  'why':'복사/이동에 로깅·카운팅 같은 부작용을 넣으면 최적화(복사 생략)로 호출 횟수가 달라져 동작이 예측 불가해진다. 복사/이동 의미만 구현한다.'},

 {'id':'A12-8-3','cat':'Required · Automated',
  'title':'이동된(moved-from) 객체의 값을 읽지 않는다',
  'bad': r"""auto b = std::move(a);
use(a.size());        // 이동 후 미지정 상태 읽기""",
  'good': r"""auto b = std::move(a);
a = make_default();   // 재사용 전 재설정""",
  'why':'이동 후 객체는 유효하나 미지정 상태라 그 값에 의존하면 비결정적이다. 재사용 전에 명확한 값을 다시 대입한다.'},

 {'id':'A12-8-5','cat':'Required · Automated',
  'title':'복사/이동 대입은 자기 대입(self-assignment)을 처리한다',
  'bad': r"""S& operator=(const S& o) {
    delete p_; p_ = new int(*o.p_);   // o==this면 UAF
    return *this;
}""",
  'good': r"""S& operator=(S o) {   // copy-and-swap
    std::swap(p_, o.p_);
    return *this;
}""",
  'why':'자기 대입 시 먼저 해제하면 복사할 원본이 사라져 use-after-free가 난다. copy-and-swap이나 자기 검사로 안전하게 처리한다.'},

 {'id':'A13-2-1','cat':'Required · Automated',
  'title':'대입 연산자는 *this 에 대한 참조를 반환한다',
  'bad': r"""void operator=(const S& o);   // void 반환 — 연쇄 대입 불가""",
  'good': r"""S& operator=(const S& o) { ...; return *this; }""",
  'why':'대입 연산자가 *this 참조를 반환하지 않으면 연쇄 대입(a=b=c)과 표준 관례가 깨진다. S& 를 반환한다.'},

 {'id':'A13-2-3','cat':'Required · Automated',
  'title':'관계(비교) 연산자는 bool 을 반환한다',
  'bad': r"""int operator<(const S& o) const;   // int 반환 — 오용 유발""",
  'good': r"""bool operator<(const S& o) const;""",
  'why':'비교 연산자가 bool이 아닌 타입을 반환하면 조건문·알고리즘에서 예상치 못한 변환과 오용을 부른다. bool을 반환한다.'},

 {'id':'A13-5-2','cat':'Required · Automated',
  'title':'사용자 정의 변환 연산자는 explicit 로 선언한다',
  'bad': r"""struct Handle { operator int() const; };   // 암시적 변환
Handle h; int x = h + 1;   // 의도치 않은 변환""",
  'good': r"""struct Handle { explicit operator int() const; };
int x = static_cast<int>(h) + 1;""",
  'why':'암시적 변환 연산자는 예상 못한 곳에서 변환을 일으켜 오버로드 해석을 망친다. explicit로 명시적 변환만 허용한다.'},

 {'id':'A14-8-2','cat':'Required · Automated',
  'title':'함수 템플릿의 명시적 특수화를 사용하지 않는다',
  'bad': r"""template <typename T> void f(T);
template <> void f<int>(int);   // 함수 템플릿 특수화 — 오버로드 해석 함정""",
  'good': r"""template <typename T> void f(T);
void f(int);          // 일반 오버로드 사용""",
  'why':'함수 템플릿 명시적 특수화는 오버로드 해석과 상호작용이 직관에 반해 잘못된 함수가 선택될 수 있다. 일반 오버로드를 쓴다.'},

 {'id':'A15-1-1','cat':'Required · Automated',
  'title':'std::exception 파생 타입만 예외로 사용한다',
  'bad': r"""throw 42;             // 정수 예외 — 핸들링 불일관""",
  'good': r"""throw std::runtime_error("invalid state");""",
  'why':'임의 타입을 던지면 일관된 처리(메시지·계층 catch)가 어렵다. std::exception에서 파생된 타입만 던진다.'},

 {'id':'A15-1-2','cat':'Required · Automated',
  'title':'예외 객체를 포인터로 throw 하지 않는다(값으로 throw)',
  'bad': r"""throw new MyError("x");   // 포인터 — 누수·소유권 모호""",
  'good': r"""throw MyError("x");       // 값으로 throw""",
  'why':'포인터를 던지면 누가 delete할지 모호해 누수나 이중 해제가 난다. 예외는 값으로 던지고 const 참조로 잡는다.'},

 {'id':'A15-1-5','cat':'Required · Automated',
  'title':'예외를 실행 경계(스레드·콜백 경계 등) 너머로 던지지 않는다',
  'bad': r"""std::thread t([]{ throw std::runtime_error("x"); });   // 스레드 밖으로 — terminate""",
  'good': r"""std::thread t([]{
    try { work(); } catch (...) { store_error(); }
});""",
  'why':'스레드 함수 등 실행 경계를 넘어 예외가 빠져나가면 std::terminate가 호출된다. 경계 내부에서 예외를 포착해 전달 가능한 형태로 저장한다.'},

 {'id':'A15-2-2','cat':'Required · Automated',
  'title':'생성자가 실패하면 이미 획득한 자원을 모두 해제한다',
  'bad': r"""S() { a_ = new int; b_ = new int; risky(); }   // risky 예외 시 a_,b_ 누수""",
  'good': r"""S() : a_{std::make_unique<int>()}, b_{std::make_unique<int>()} { risky(); }""",
  'why':'생성 도중 예외가 나면 이미 할당한 raw 자원이 누수된다. 멤버를 RAII로 두어 부분 생성 상태에서도 자동 해제되게 한다.'},

 {'id':'A15-3-5','cat':'Required · Automated',
  'title':'클래스 타입 예외는 참조로 catch 한다',
  'bad': r"""try { f(); } catch (std::exception e) { ... }   // 값 catch — 슬라이싱""",
  'good': r"""try { f(); } catch (const std::exception& e) { ... }""",
  'why':'예외를 값으로 잡으면 파생 예외가 슬라이싱되어 정보를 잃는다. const 참조로 잡아 다형성을 보존한다.'},

 {'id':'A15-4-2','cat':'Required · Automated',
  'title':'noexcept 함수에서 예외가 빠져나가지 않게 한다',
  'bad': r"""void f() noexcept { mayThrow(); }   // 예외 시 terminate""",
  'good': r"""void f() noexcept {
    try { mayThrow(); } catch (...) { /* 내부 처리 */ }
}""",
  'why':'noexcept 함수에서 예외가 탈출하면 즉시 terminate된다. 내부에서 예외를 처리하거나 noexcept를 제거한다.'},

 {'id':'A15-4-4','cat':'Required · Automated',
  'title':'예외를 던지지 않는 함수는 noexcept 로 표시한다',
  'bad': r"""int size() const { return n_; }   // 던지지 않는데 noexcept 미표시""",
  'good': r"""int size() const noexcept { return n_; }""",
  'why':'예외를 던지지 않는 함수에 noexcept를 표시하면 호출부 최적화와 예외 안전 보장이 향상된다. 비-throw 함수는 noexcept로 명시한다.'},

 {'id':'A15-5-1','cat':'Required · Automated',
  'title':'특수 멤버 함수(소멸자·이동·swap)는 예외를 던지지 않게 한다',
  'bad': r"""~Conn() { send_close(); }   // 던질 수 있는 소멸자""",
  'good': r"""~Conn() noexcept {
    try { send_close(); } catch (...) { /* 흡수 */ }
}""",
  'why':'소멸자·이동·swap에서 예외가 나면 스택 풀기 중 terminate나 깨진 상태가 발생한다. 이들은 noexcept로 두고 내부 예외를 흡수한다.'},

 {'id':'M6-2-1','cat':'Required · Automated',
  'title':'대입을 하위 표현식(subexpression)에서 수행하지 않는다',
  'bad': r"""if ((x = next()) != 0) { ... }   // 조건 안 대입""",
  'good': r"""x = next();
if (x != 0) { ... }""",
  'why':'표현식 내부의 대입은 == 오타와 혼동되고 부작용을 숨긴다. 대입은 독립 문장으로 분리한다.'},

 {'id':'M6-2-2','cat':'Required · Automated',
  'title':'부동소수 값을 등호(==)로 비교하지 않는다',
  'bad': r"""if (x == 0.1) { ... }   // 표현 오차로 거의 항상 거짓""",
  'good': r"""if (std::fabs(x - 0.1) < 1e-9) { ... }""",
  'why':'부동소수는 표현 오차가 있어 정확한 동등 비교가 의도대로 동작하지 않는다. 허용 오차(epsilon) 범위 비교를 한다.'},

 {'id':'M6-3-1','cat':'Required · Automated',
  'title':'반복문/switch 의 본문은 복합문(중괄호)으로 감싼다',
  'bad': r"""for (int i = 0; i < n; ++i)
    a(); b();         // b는 루프 밖 — 들여쓰기 착시""",
  'good': r"""for (int i = 0; i < n; ++i) {
    a();
}
b();""",
  'why':'중괄호 없는 단일 문 본문은 문장 추가 시 범위가 어긋나는 결함을 부른다. 항상 중괄호로 본문을 감싼다.'},

 {'id':'M6-4-2','cat':'Required · Automated',
  'title':'if-else if 사슬은 else 로 마무리한다',
  'bad': r"""if (m == 1) a();
else if (m == 2) b();   // 그 외 경우 미처리""",
  'good': r"""if (m == 1) { a(); }
else if (m == 2) { b(); }
else { handle_other(); }""",
  'why':'else로 닫지 않으면 예상 못한 값이 조용히 무시된다. 마지막 else로 나머지 경우를 명시적으로 처리한다.'},

 {'id':'M6-4-3','cat':'Required · Automated',
  'title':'switch 문은 잘 정의된 형태를 따른다',
  'bad': r"""switch (x) {
    case 1: a();      // break 누락
    case 2: b(); break;
}""",
  'good': r"""switch (x) {
    case 1: a(); break;
    case 2: b(); break;
    default: break;
}""",
  'why':'break 누락 fall-through와 비정형 switch는 흔한 버그를 만든다. 각 절을 break로 종료하고 default를 둔다.'},

 {'id':'M6-4-6','cat':'Required · Automated',
  'title':'switch 의 default 절은 마지막에 둔다',
  'bad': r"""switch (x) {
    default: d(); break;   // 중간에 위치
    case 1: a(); break;
}""",
  'good': r"""switch (x) {
    case 1: a(); break;
    default: d(); break;
}""",
  'why':'default가 절들 사이에 끼면 가독성이 떨어지고 흐름을 오해하기 쉽다. 마지막에 배치한다.'},

 {'id':'M6-6-1','cat':'Required · Automated',
  'title':'문서화되지 않은 형태의 점프(goto 등)를 사용하지 않는다',
  'bad': r"""goto retry;           // 임의 점프""",
  'good': r"""while (!done) { done = attempt(); }   // 구조적 반복""",
  'why':'goto 등 비구조적 점프는 제어 흐름 분석을 어렵게 한다. 반복·함수 분리 등 구조적 제어로 대체한다.'},

 {'id':'M7-1-2','cat':'Required · Automated',
  'title':'수정되지 않는 포인터 매개변수는 const 를 가리키게 한다',
  'bad': r"""std::size_t len(char* s) {   // s 내용 수정 안 하면서 비-const""",
  'good': r"""std::size_t len(const char* s) { ... }""",
  'why':'읽기만 하는 포인터 인자를 const로 표시하지 않으면 const 객체를 넘길 수 없고 의도가 흐려진다. 수정하지 않으면 const를 가리키게 한다.'},

 {'id':'M7-3-6','cat':'Required · Automated',
  'title':'헤더에서 using 지시문/선언으로 이름을 전역에 도입하지 않는다',
  'bad': r"""// util.h
using namespace std;   // 포함하는 모든 곳에 std 도입 — 충돌""",
  'good': r"""// util.h — 명시적 한정 사용
std::string make();""",
  'why':'헤더의 using namespace는 포함하는 모든 번역단위 이름공간을 오염시켜 모호성·충돌을 부른다. 헤더에서는 완전 한정 이름을 쓴다.'},

 {'id':'M7-5-1','cat':'Required · Automated',
  'title':'함수는 자동(지역) 객체에 대한 참조/포인터를 반환하지 않는다',
  'bad': r"""const std::string& name() {
    std::string s = "node";
    return s;          // 지역 객체 참조 반환 — 댕글링""",
  'good': r"""std::string name() {
    return std::string{"node"};   // 값 반환
}""",
  'why':'지역 객체의 참조/주소는 함수 종료 시 무효가 되어 댕글링 접근을 유발한다. 값으로 반환하거나 수명이 보장된 객체를 가리킨다.'},

 {'id':'M8-4-2','cat':'Required · Automated',
  'title':'함수 선언과 정의의 매개변수 이름을 일치시킨다',
  'bad': r"""void copy(char* dst, char* src);   // 선언
void copy(char* a, char* b) { ... }   // 정의 — 이름 다름(혼동)""",
  'good': r"""void copy(char* dst, char* src);
void copy(char* dst, char* src) { ... }""",
  'why':'선언과 정의의 매개변수 이름이 다르면 의미 파악과 인자 순서 확인이 어려워진다. 이름을 일치시켜 일관성을 유지한다.'},

 {'id':'M8-5-1','cat':'Required · Automated',
  'title':'모든 변수는 사용 전에 정의된 값을 가져야 한다',
  'bad': r"""int total;
for (int i = 0; i < n; ++i) total += a[i];   // total 미초기화""",
  'good': r"""int total = 0;
for (int i = 0; i < n; ++i) total += a[i];""",
  'why':'미초기화 변수를 읽으면 불확정 값으로 미정의 동작이 된다. 사용 전에 초기화한다.'},

 {'id':'M9-3-1','cat':'Required · Automated',
  'title':'const 멤버 함수가 내부 데이터에 대한 비-const 핸들을 반환하지 않게 한다',
  'bad': r"""class C {
    int* p_;
public:
    int* get() const { return p_; }   // const 함수가 수정 가능 핸들 노출""",
  'good': r"""class C {
    int* p_;
public:
    const int* get() const { return p_; }
};""",
  'why':'const 멤버 함수가 수정 가능한 내부 핸들을 노출하면 const 의미가 무너진다. const 함수는 const 핸들만 반환한다.'},

 {'id':'M9-3-3','cat':'Required · Automated',
  'title':'const 나 static 으로 만들 수 있는 멤버 함수는 그렇게 선언한다',
  'bad': r"""class C {
    int v_;
public:
    int value() { return v_; }   // 상태 변경 없는데 비-const""",
  'good': r"""class C {
    int v_;
public:
    int value() const { return v_; }
};""",
  'why':'상태를 바꾸지 않는 함수를 const로 표시하지 않으면 const 객체에서 호출할 수 없고 의도가 흐려진다. 가능하면 const(또는 static)로 선언한다.'},

 {'id':'M9-5-1','cat':'Required · Automated',
  'title':'union 을 사용하지 않는다',
  'bad': r"""union U { int i; float f; };
U u; u.i = 1; float x = u.f;   // 비활성 멤버 읽기 — 미정의""",
  'good': r"""std::variant<int, float> u = 1;
// std::get<float>(u) 는 잘못된 타입이면 예외""",
  'why':'union의 비활성 멤버를 읽는 타입 퍼닝은 미정의 동작이다. 타입 안전한 std::variant로 대체한다.'},
]
