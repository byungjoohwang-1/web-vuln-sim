# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트1: DCL·OOP·EXP) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'DCL50-CPP','cat':'DCL · Rule · L1',
  'title':'C 스타일 가변인자 함수를 정의하지 않는다',
  'bad': r"""int sum(int n, ...) {        // 타입 안전성 없는 가변인자
    va_list ap; va_start(ap, n);
    int s = 0;
    for (int i = 0; i < n; ++i) s += va_arg(ap, int);
    va_end(ap);
    return s;
}""",
  'good': r"""template <typename... Args>
int sum(Args... args) {     // 가변 템플릿 — 타입 안전
    return (args + ... + 0);
}""",
  'why':'C 스타일 ... 가변인자는 타입·개수 검사가 없어 잘못된 추출로 미정의 동작이 된다. 가변 템플릿이나 std::initializer_list로 타입 안전하게 대체한다.'},

 {'id':'DCL51-CPP','cat':'DCL · Rule · L1',
  'title':'예약된 식별자를 선언하거나 정의하지 않는다',
  'bad': r"""#define _DEBUG 1          // 밑줄+대문자 — 구현 예약
int __count = 0;""",
  'good': r"""#define APP_DEBUG 1
int count = 0;""",
  'why':'밑줄로 시작하는 이름이나 표준 예약 식별자를 정의하면 구현 내부와 충돌해 미정의 동작이 된다. 비예약 이름을 사용한다.'},

 {'id':'DCL53-CPP','cat':'DCL · Rule · L3',
  'title':'구문적으로 모호한 선언(most vexing parse)을 작성하지 않는다',
  'bad': r"""Widget w(Gadget());   // 함수 선언으로 해석됨(객체 아님)""",
  'good': r"""Widget w{Gadget{}};   // 중괄호 초기화로 객체 생성 명확화""",
  'why':'괄호 초기화는 함수 선언으로 해석되는 most vexing parse를 일으켜 의도한 객체가 생성되지 않는다. 중괄호 초기화로 모호함을 없앤다.'},

 {'id':'DCL54-CPP','cat':'DCL · Rule · L1',
  'title':'할당/해제 연산자는 짝을 맞춰 오버로드한다',
  'bad': r"""struct S {
    static void* operator new(std::size_t);   // delete 미정의
};""",
  'good': r"""struct S {
    static void* operator new(std::size_t);
    static void  operator delete(void*);      // 짝 정의
};""",
  'why':'operator new만 오버로드하고 delete를 빠뜨리면 사용자 정의 할당과 기본 해제가 어긋나 힙 손상이 난다. new/delete를 짝으로 정의한다.'},

 {'id':'DCL57-CPP','cat':'DCL · Rule · L1',
  'title':'소멸자나 해제 연산자에서 예외가 빠져나가지 않게 한다',
  'bad': r"""~File() {
    flush();          // 예외를 던질 수 있음 → 스택 풀기 중 terminate
}""",
  'good': r"""~File() noexcept {
    try { flush(); } catch (...) { /* 로깅 후 흡수 */ }
}""",
  'why':'스택 풀기 중 소멸자에서 예외가 빠져나가면 std::terminate가 호출된다. 소멸자는 noexcept로 두고 내부 예외를 흡수한다.'},

 {'id':'DCL58-CPP','cat':'DCL · Rule · L1',
  'title':'표준 네임스페이스(std)를 수정하지 않는다',
  'bad': r"""namespace std {
    template <> struct hash<MyKey> { ... };   // 일부 수정은 허용되나, 일반 추가는 금지
    void my_helper();                          // std에 임의 추가 — 미정의
}""",
  'good': r"""namespace mylib {
    void my_helper();
}
// 사용자 타입 특수화는 규정된 범위에서만""",
  'why':'std 네임스페이스에 임의로 선언·정의를 추가하면 미정의 동작이다. 사용자 코드는 자체 네임스페이스에 두고, 허용된 특수화만 규정대로 한다.'},

 {'id':'DCL59-CPP','cat':'DCL · Rule · L2',
  'title':'헤더에 이름 없는(unnamed) 네임스페이스를 정의하지 않는다',
  'bad': r"""// util.h
namespace { int counter = 0; }   // 포함하는 TU마다 별도 사본""",
  'good': r"""// util.h
namespace util { extern int counter; }
// util.cpp
namespace util { int counter = 0; }""",
  'why':'헤더의 무명 네임스페이스는 포함하는 번역단위마다 별도 실체를 만들어 ODR 혼란과 예기치 않은 사본을 낳는다. 명명 네임스페이스+선언/정의 분리를 쓴다.'},

 {'id':'DCL60-CPP','cat':'DCL · Rule · L2',
  'title':'단일 정의 규칙(ODR)을 준수한다',
  'bad': r"""// a.cpp
struct P { int x; };
// b.cpp
struct P { long x; };   // 같은 이름, 다른 정의 — ODR 위반""",
  'good': r"""// p.h (단일 정의)
struct P { int x; };
// a.cpp, b.cpp 에서 #include "p.h" """,
  'why':'같은 타입/함수를 번역단위마다 다르게 정의하면 ODR 위반으로 미정의 동작이 된다. 정의는 헤더 한 곳에 두고 공유한다.'},

 {'id':'OOP50-CPP','cat':'OOP · Rule · L1',
  'title':'생성자/소멸자에서 가상 함수를 호출하지 않는다',
  'bad': r"""struct Base {
    Base() { init(); }              // 파생 오버라이드가 아직 없음
    virtual void init() { }
};""",
  'good': r"""struct Base {
    Base() { }
    void start() { init(); }        // 생성 완료 후 호출
    virtual void init() { }
};""",
  'why':'생성/소멸 중에는 동적 타입이 해당 클래스라 가상 디스패치가 파생 오버라이드로 가지 않아 의도와 다르게 동작한다. 생성 완료 후 별도 메서드에서 호출한다.'},

 {'id':'OOP51-CPP','cat':'OOP · Rule · L2',
  'title':'파생 객체를 슬라이싱(slicing)하지 않는다',
  'bad': r"""void take(Base b);        // 값 전달
Derived d;
take(d);                  // 파생 부분이 잘려나감""",
  'good': r"""void take(const Base& b); // 참조 전달
Derived d;
take(d);""",
  'why':'파생 객체를 기반 클래스 값으로 받으면 파생 부분이 잘려(slicing) 다형성이 깨진다. 기반 타입은 참조나 포인터로 전달한다.'},

 {'id':'OOP52-CPP','cat':'OOP · Rule · L1',
  'title':'가상 소멸자가 없는 다형 객체를 기반 포인터로 delete 하지 않는다',
  'bad': r"""struct Base { ~Base() {} };          // 비가상 소멸자
struct Derived : Base { Resource r; };
Base* p = new Derived;
delete p;                            // Derived 소멸자 미호출 — 누수""",
  'good': r"""struct Base { virtual ~Base() = default; };
struct Derived : Base { Resource r; };
Base* p = new Derived;
delete p;""",
  'why':'기반 클래스 소멸자가 비가상이면 기반 포인터로 delete 시 파생 소멸자가 호출되지 않아 자원이 누수된다. 다형 기반 클래스에 가상 소멸자를 둔다.'},

 {'id':'OOP53-CPP','cat':'OOP · Rule · L3',
  'title':'생성자 멤버 초기화 목록을 선언 순서대로 작성한다',
  'bad': r"""struct S {
    int a, b;
    S(int x) : b(x), a(b) {}   // 실제 초기화는 a 먼저 — b 미초기화 사용
};""",
  'good': r"""struct S {
    int a, b;
    S(int x) : a(x), b(x) {}   // 선언 순서와 일치
};""",
  'why':'멤버는 초기화 목록 순서가 아니라 선언 순서로 초기화되므로, 순서가 어긋나면 아직 초기화 안 된 멤버를 읽는다. 선언 순서대로 초기화 목록을 작성한다.'},

 {'id':'OOP54-CPP','cat':'OOP · Rule · L3',
  'title':'자기 대입(self copy-assignment)을 안전하게 처리한다',
  'bad': r"""S& operator=(const S& o) {
    delete data;            // o가 this면 자기 데이터 해제
    data = new int(*o.data);// 해제된 메모리 복사 — UAF
    return *this;
}""",
  'good': r"""S& operator=(S o) {     // copy-and-swap
    std::swap(data, o.data);
    return *this;
}""",
  'why':'자기 대입 시 먼저 해제하면 곧바로 복사할 원본이 사라져 use-after-free가 난다. copy-and-swap 또는 자기 검사로 안전하게 처리한다.'},

 {'id':'OOP58-CPP','cat':'OOP · Rule · L2',
  'title':'복사 연산은 원본(source)을 변경하지 않는다',
  'bad': r"""S(const S& o) {
    data = o.data;
    o.data = nullptr;       // const 위반 의도 — 원본 훼손""",
  'good': r"""S(const S& o) : data(o.data ? new int(*o.data) : nullptr) { }
S(S&& o) noexcept : data(o.data) { o.data = nullptr; }  // 이동만 원본 비움""",
  'why':'복사 생성/대입이 원본을 비우거나 바꾸면 복사 의미가 깨진다. 원본을 훼손하는 동작은 이동 연산에만 두고 복사는 원본을 보존한다.'},

 {'id':'EXP50-CPP','cat':'EXP · Rule · L2',
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'bad': r"""int i = 0;
f(i++, i++);          // 두 인자 평가 순서 미명세""",
  'good': r"""int a = i++;
int b = i++;
f(a, b);""",
  'why':'함수 인자나 한 식 내 여러 부작용의 평가 순서는 일반적으로 정해져 있지 않아 결과가 비결정적이다. 부작용을 분리해 순서를 확정한다.'},

 {'id':'EXP51-CPP','cat':'EXP · Rule · L1',
  'title':'잘못된 타입의 포인터로 배열을 delete 하지 않는다',
  'bad': r"""Base* p = new Derived[3];   // 배열을 기반 포인터로
delete[] p;                 // 요소 크기 불일치 — 미정의""",
  'good': r"""std::vector<Derived> v(3);  // 컨테이너로 다형 배열 회피""",
  'why':'파생 배열을 기반 포인터로 delete[]하면 요소 크기가 달라 미정의 동작이 된다. 다형 객체 배열은 raw 배열 대신 컨테이너/스마트포인터로 관리한다.'},

 {'id':'EXP52-CPP','cat':'EXP · Rule · L3',
  'title':'미평가 피연산자(sizeof 등)의 부작용에 의존하지 않는다',
  'bad': r"""int i = 0;
std::size_t n = sizeof(a[i++]);   // i 증가 안 됨""",
  'good': r"""std::size_t n = sizeof(a[0]);
++i;""",
  'why':'sizeof/decltype/noexcept의 피연산자는 평가되지 않아 부작용이 발생하지 않는다. 의도한 부작용은 별도 문장으로 수행한다.'},

 {'id':'EXP53-CPP','cat':'EXP · Rule · L3',
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'bad': r"""int v;
int w = v + 1;        // v 미초기화""",
  'good': r"""int v = 0;
int w = v + 1;""",
  'why':'미초기화 객체를 읽으면 불확정 값으로 미정의 동작이 된다. 선언 시 또는 사용 전에 초기화한다.'},

 {'id':'EXP54-CPP','cat':'EXP · Rule · L1',
  'title':'수명이 끝난(out-of-lifetime) 객체에 접근하지 않는다',
  'bad': r"""const std::string& r = make_temp();  // 임시의 수명 종료 후 참조
use(r);""",
  'good': r"""std::string s = make_temp();   // 값으로 보관
use(s);""",
  'why':'소멸된 임시·지역 객체를 가리키는 참조/포인터 접근은 미정의 동작이다. 필요한 값은 수명이 보장되는 객체에 보관한다.'},

 {'id':'EXP55-CPP','cat':'EXP · Rule · L1',
  'title':'cv 한정(const/volatile) 객체를 비한정 타입으로 접근하지 않는다',
  'bad': r"""const int k = 5;
int& r = const_cast<int&>(k);
r = 9;                // const 객체 수정 — 미정의""",
  'good': r"""int k = 5;            // 수정 필요하면 비-const
k = 9;""",
  'why':'const_cast로 const를 제거하고 실제 const 객체를 수정하면 미정의 동작이다. 수정이 필요한 객체는 처음부터 비-const로 선언한다.'},

 {'id':'EXP57-CPP','cat':'EXP · Rule · L1',
  'title':'불완전(incomplete) 클래스 타입 포인터를 delete 하거나 잘못 캐스트하지 않는다',
  'bad': r"""struct Impl;          // 전방 선언만
void f(Impl* p) { delete p; }   // 불완전 타입 delete — 소멸자 미호출""",
  'good': r"""// Impl 완전 정의가 보이는 곳에서 삭제하거나 unique_ptr+커스텀 deleter
std::unique_ptr<Impl, void(*)(Impl*)> p{create(), &destroy};""",
  'why':'불완전 타입 포인터를 delete하면 소멸자 호출 여부가 미정의라 누수·손상이 난다. 완전 정의가 보이는 곳에서 삭제하거나 PIMPL 전용 deleter를 쓴다.'},

 {'id':'EXP61-CPP','cat':'EXP · Rule · L2',
  'title':'람다 객체가 캡처한 참조보다 오래 살지 않게 한다',
  'bad': r"""std::function<int()> make() {
    int local = 42;
    return [&]{ return local; };   // local 참조가 함수 종료 후 무효""",
  'good': r"""std::function<int()> make() {
    int local = 42;
    return [local]{ return local; };  // 값으로 캡처""",
  'why':'참조 캡처한 지역 변수가 람다보다 먼저 소멸하면 댕글링 참조가 된다. 수명이 람다보다 짧은 대상은 값으로 캡처한다.'},

 {'id':'EXP63-CPP','cat':'EXP · Rule · L2',
  'title':'이동된(moved-from) 객체의 값에 의존하지 않는다',
  'bad': r"""std::string a = "hi";
std::string b = std::move(a);
std::cout << a;        // a는 유효하나 미지정 상태""",
  'good': r"""std::string a = "hi";
std::string b = std::move(a);
a = "reset";           // 재사용 전 명확히 재설정""",
  'why':'이동된 객체는 유효하지만 값이 미지정 상태라, 그 값에 의존하면 비결정적이다. 재사용하려면 먼저 명확한 값을 다시 대입한다.'},

 {'id':'OOP57-CPP','cat':'OOP · Rule · L3',
  'title':'C 표준 함수 대신 특수 멤버 함수/연산자를 선호한다',
  'bad': r"""MyObj a, b;
std::memcpy(&a, &b, sizeof a);   // 비trivial 객체에 memcpy — 불변식 파괴""",
  'good': r"""MyObj a, b;
a = b;                 // 복사 대입 연산자 사용""",
  'why':'비trivial 클래스에 memcpy/memcmp를 쓰면 가상 포인터·소유 자원 같은 불변식을 깨뜨린다. 복사/비교는 클래스의 연산자를 사용한다.'},

 {'id':'OOP55-CPP','cat':'OOP · Rule · L1',
  'title':'존재하지 않는 멤버를 멤버 포인터 연산으로 접근하지 않는다',
  'bad': r"""int Base::* pm = ...;
Derived d;
d.*pm = 1;            // pm이 d에 없는 멤버를 가리키면 미정의""",
  'good': r"""int Derived::* pm = &Derived::field;
Derived d;
d.*pm = 1;""",
  'why':'대상 객체에 실제로 존재하지 않는 멤버를 멤버 포인터로 접근하면 미정의 동작이다. 멤버 포인터가 가리키는 멤버가 객체에 존재함을 보장한다.'},
]
