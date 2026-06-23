# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트1: DCL·OOP·EXP) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17` 기준."""

RULES = [
 {'id':'DCL50-CPP','cat':'DCL · Rule · L1','compiles':True,
  'title':'C 스타일 가변인자 함수를 정의하지 않는다',
  'title_en':'Do not define a C-style variadic function',
  'bad': r"""#include <cstdarg>
#include <iostream>
// 타입·개수 검사가 전혀 없는 C 스타일 가변인자
static long sum(int n, ...) {
    va_list ap; va_start(ap, n);
    long s = 0;
    for (int i = 0; i < n; ++i) s += va_arg(ap, int);   // 호출자가 double 을 넘기면 미정의
    va_end(ap);
    return s;
}
int main() {
    std::cout << sum(3, 10, 20, 30) << '\n';   // 우연히 동작하지만 타입 안전성 없음
    std::cout << sum(2, 10, 3.5) << '\n';       // 두 번째가 double — 잘못된 추출, 쓰레기 값
}""",
  'good': r"""#include <iostream>
// 가변 템플릿 — 인자 타입·개수를 컴파일 타임에 안전하게 처리
template <typename... Args>
auto sum(Args... args) { return (args + ... + 0); }   // C++17 fold expression
int main() {
    std::cout << sum(10, 20, 30) << '\n';
    std::cout << sum(10, 3.5) << '\n';   // double 도 타입 안전하게 합산
}""",
  'why':'근거: C 스타일 ... 가변인자는 인자의 타입과 개수에 대한 정보가 컴파일러에 남지 않아 va_arg 가 지정한 타입과 실제 인자가 다르면 검사 없이 잘못된 비트를 읽는다. 영향: 호출자가 형식 문자열과 인자를 어긋나게 넘기면 쓰레기 값·크래시·정보 유출로 이어진다. 대응: 가변 템플릿(fold expression)이나 std::initializer_list 로 대체하면 타입·개수가 모두 컴파일 타임에 검증된다.',
  'why_en':'Rationale: C-style "..." varargs keep no type or count information, so va_arg blindly reinterprets bytes when the requested type does not match the actual argument. Impact: a mismatch between caller arguments and extraction yields garbage values, crashes, or information disclosure. Fix: replace with variadic templates (fold expressions) or std::initializer_list so types and counts are checked at compile time.'},

 {'id':'DCL51-CPP','cat':'DCL · Rule · L1','compiles':True,
  'title':'예약된 식별자를 선언하거나 정의하지 않는다',
  'title_en':'Do not declare or define a reserved identifier',
  'bad': r"""#include <iostream>
#define _Max 100        // 밑줄+대문자로 시작 — 전역에서 구현에 예약됨
int __count = 0;         // 이중 밑줄 — 모든 사용처에서 구현에 예약됨
int main() {
    __count = _Max;
    std::cout << __count << '\n';   // 표준 라이브러리 매크로와 충돌하면 의미가 조용히 바뀜
}""",
  'good': r"""#include <iostream>
constexpr int kMax = 100;   // 예약되지 않은 일반 이름
int g_count = 0;
int main() {
    g_count = kMax;
    std::cout << g_count << '\n';
}""",
  'why':'근거: 밑줄+대문자/이중 밑줄로 시작하는 이름과 전역의 밑줄+소문자 이름은 표준이 구현(컴파일러·표준 라이브러리)에 예약한 영역이다. 영향: 그런 이름을 정의하면 헤더 내부 매크로·식별자와 충돌해 진단 없이 코드 의미가 바뀌거나 미정의 동작이 된다. 대응: 사용자 코드는 예약 패턴을 피한 비예약 이름만 사용한다.',
  'why_en':'Rationale: names beginning with an underscore followed by an uppercase letter, names containing a double underscore, and file-scope names beginning with an underscore are reserved for the implementation. Impact: defining them can silently collide with library macros or identifiers, changing program meaning or causing undefined behaviour with no diagnostic. Fix: user code must use only non-reserved names.'},

 {'id':'DCL53-CPP','cat':'DCL · Rule · L3','compiles':True,
  'title':'구문적으로 모호한 선언(most vexing parse)을 작성하지 않는다',
  'title_en':'Do not write syntactically ambiguous declarations',
  'bad': r"""#include <iostream>
struct Gadget { Gadget(){} };
struct Widget { Widget(Gadget){ } int v = 7; };
int main() {
    Widget w(Gadget());   // 객체가 아니라 'Gadget(*)() 를 받는 함수 w' 선언으로 해석
    // w 는 객체가 아니라 함수라서 w.v 같은 멤버 접근은 컴파일조차 되지 않는다
    std::cout << "no Widget object was constructed; 'w' is a function declaration\n";
}""",
  'good': r"""#include <iostream>
struct Gadget { Gadget(){} };
struct Widget { Widget(Gadget){ } int v = 7; };
int main() {
    Widget w{Gadget{}};   // 중괄호 초기화 — 명백히 객체 생성
    std::cout << w.v << '\n';
}""",
  'why':'근거: T obj( U() ) 형태는 객체 초기화가 아니라 "U(*)() 를 인자로 받아 T 를 반환하는 함수 obj" 의 선언으로 해석된다(most vexing parse). 영향: 의도한 객체가 만들어지지 않아 이후 멤버 접근이 컴파일 에러가 나거나, 더 미묘하게는 함수 선언이 조용히 통과해 런타임 논리가 어긋난다. 대응: 중괄호 초기화 Widget w{...} 를 써서 선언/함수 모호성을 제거한다.',
  'why_en':'Rationale: the form T obj( U() ) is parsed not as object initialization but as a declaration of a function obj taking a "U(*)()" and returning T (the most vexing parse). Impact: the intended object is never created, so later member access fails to compile, or more subtly a stray function declaration passes silently and breaks runtime logic. Fix: use brace initialization Widget w{...} to remove the declaration/function ambiguity.'},

 {'id':'DCL54-CPP','cat':'DCL · Rule · L1','compiles':True,
  'title':'할당/해제 연산자는 짝을 맞춰 오버로드한다',
  'title_en':'Overload allocation and deallocation functions as a pair',
  'bad': r"""#include <cstdlib>
#include <new>
#include <iostream>
struct Pool {
    static void* operator new(std::size_t n) {   // new 만 오버로드, delete 없음
        std::cout << "pool alloc\n";
        return std::malloc(n);
    }
    int v = 1;
};
int main() {
    Pool* p = new Pool;     // 사용자 정의 new
    delete p;               // 기본 delete — malloc 메모리를 표준 해제기로 반환, 짝 어긋남
}""",
  'good': r"""#include <cstdlib>
#include <new>
#include <iostream>
struct Pool {
    static void* operator new(std::size_t n) {
        std::cout << "pool alloc\n";
        return std::malloc(n);
    }
    static void operator delete(void* p) noexcept {   // 짝 정의 — 같은 할당기로 해제
        std::cout << "pool free\n";
        std::free(p);
    }
    int v = 1;
};
int main() {
    Pool* p = new Pool;
    delete p;
}""",
  'why':'근거: operator new 를 오버로드하면서 대응하는 operator delete 를 정의하지 않으면, 사용자 정의 할당으로 얻은 메모리가 기본 해제기로 반환되어 할당기와 해제기가 어긋난다. 영향: 풀·아레나 같은 커스텀 할당기에서 힙 메타데이터가 손상되고, 생성자 예외 시 호출되는 짝 맞는 delete 가 없어 누수가 발생한다. 대응: new/delete(및 배열 형태)를 항상 짝으로 오버로드한다.',
  'why_en':'Rationale: overloading operator new without the matching operator delete means memory from the custom allocator is returned through the default deallocator, so allocator and deallocator no longer agree. Impact: with pool/arena allocators this corrupts heap metadata, and if a constructor throws there is no matching delete to call, leaking memory. Fix: always overload new/delete (and the array forms) as a pair.'},

 {'id':'DCL57-CPP','cat':'DCL · Rule · L1','compiles':True,
  'title':'소멸자나 해제 연산자에서 예외가 빠져나가지 않게 한다',
  'title_en':'Do not let exceptions escape from destructors or deallocation functions',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct File {
    bool dirty = true;
    void flush() { throw std::runtime_error("disk full"); }
    ~File() { flush(); }   // 소멸자에서 예외가 빠져나감 → 스택 풀기 중이면 terminate
};
int main() {
    try { File f; }        // f 소멸 시 던진 예외 — 위험
    catch (const std::exception& e) { std::cout << e.what() << '\n'; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct File {
    bool dirty = true;
    void flush() { throw std::runtime_error("disk full"); }
    ~File() noexcept {                 // 명시적 noexcept
        try { flush(); }
        catch (...) { std::cerr << "flush failed in dtor, logged\n"; }  // 흡수
    }
};
int main() {
    File f;
    std::cout << "clean shutdown\n";
}""",
  'why':'근거: 예외로 스택이 풀리는 도중 또 다른 예외가 소멸자에서 빠져나가면 동시에 두 예외가 전파되어 std::terminate 가 호출된다. 영향: 정상 오류 처리 경로에서도 프로그램이 즉시 강제 종료되어 다른 자원 정리가 모두 건너뛰어진다. 대응: 소멸자·해제 연산자는 noexcept 로 두고 내부에서 발생할 수 있는 예외를 try/catch 로 흡수해 로깅만 한다.',
  'why_en':'Rationale: if a destructor lets an exception escape while the stack is already unwinding from another exception, two exceptions propagate at once and std::terminate is called. Impact: the program is killed even on an ordinary error path, skipping all other cleanup. Fix: mark destructors and deallocation functions noexcept and absorb any internal exception with try/catch, logging only.'},

 {'id':'DCL58-CPP','cat':'DCL · Rule · L1',
  'title':'표준 네임스페이스(std)를 수정하지 않는다',
  'title_en':'Do not modify the standard namespace',
  'bad': r"""// 다른 헤더에서 보이는 std 에 임의 선언을 추가 — 미정의 동작
namespace std {
    void my_helper();                 // std 에 사용자 함수 추가 — 금지
    template <typename T> struct vector;  // 표준 템플릿 재선언 — 금지
}""",
  'good': r"""#include <functional>
struct MyKey { int id; };
// 사용자 타입에 대한 std::hash 특수화는 규정된 범위에서만 허용된다
template <>
struct std::hash<MyKey> {
    std::size_t operator()(const MyKey& k) const noexcept {
        return std::hash<int>{}(k.id);
    }
};""",
  'why':'근거: 표준은 사용자가 정의한 타입에 한정한 일부 특수화만 허용하고, 그 밖에 std 네임스페이스에 선언·정의를 추가하는 것은 미정의 동작으로 규정한다. 영향: 구현이 제공하는 동일 이름과 충돌하거나 향후 표준 변경 시 깨져 진단 없이 동작이 바뀐다. 대응: 사용자 코드는 자체 네임스페이스에 두고, std 에는 허용된 사용자 타입 특수화(std::hash 등)만 규정대로 추가한다.',
  'why_en':'Rationale: the standard permits only certain specializations limited to user-defined types; otherwise adding declarations or definitions to namespace std is undefined behaviour. Impact: it can collide with implementation-provided names or break on a future standard revision, silently changing behaviour. Fix: keep user code in your own namespace and add to std only the permitted user-type specializations (e.g. std::hash) exactly as specified.'},

 {'id':'DCL59-CPP','cat':'DCL · Rule · L2',
  'title':'헤더에 이름 없는(unnamed) 네임스페이스를 정의하지 않는다',
  'title_en':'Do not define an unnamed namespace in a header file',
  'bad': r"""// util.h  — 여러 .cpp 가 포함
namespace { int counter = 0; }    // 포함하는 번역단위마다 별도 counter 사본 생성
inline int next() { return ++counter; }""",
  'good': r"""// util.h
namespace util { extern int counter; int next(); }
// util.cpp
namespace util { int counter = 0; int next(){ return ++counter; } }""",
  'why':'근거: 무명 네임스페이스의 멤버는 내부 링크를 가지므로 헤더를 포함하는 번역단위마다 완전히 별개의 실체가 만들어진다. 영향: 하나의 전역 상태라고 믿고 쓴 counter 가 TU마다 따로 존재해 값이 공유되지 않고, inline 함수가 TU별 사본을 참조해 ODR 혼란이 생긴다. 대응: 헤더에는 명명 네임스페이스의 extern 선언만 두고 정의는 한 .cpp 에 둔다.',
  'why_en':'Rationale: members of an unnamed namespace have internal linkage, so each translation unit that includes the header gets an entirely separate entity. Impact: a counter intended as one global instead exists per TU and is not shared, and inline functions referring to per-TU copies create ODR confusion. Fix: put only an extern declaration in a named namespace in the header and the definition in one .cpp.'},

 {'id':'DCL60-CPP','cat':'DCL · Rule · L2',
  'title':'단일 정의 규칙(ODR)을 준수한다',
  'title_en':'Obey the one-definition rule',
  'bad': r"""// a.cpp
struct Packet { int len; };          // 정의 #1
// b.cpp
struct Packet { long len; char f; }; // 같은 이름, 다른 레이아웃 — ODR 위반""",
  'good': r"""// packet.h  (유일한 정의)
struct Packet { int len; };
// a.cpp, b.cpp 모두 #include "packet.h" 로 같은 정의 공유""",
  'why':'근거: 같은 이름의 클래스·인라인 함수·템플릿은 프로그램 전체에서 토큰 단위로 동일한 단 하나의 정의만 가져야 한다(ODR). 영향: 번역단위마다 레이아웃이 다른 Packet 을 정의하면 링커가 그중 하나를 임의 선택해, 크기·오프셋 불일치로 메모리 손상이 진단 없이 발생한다. 대응: 타입·인라인 함수 정의는 헤더 한 곳에 두고 모든 TU가 그 헤더를 포함한다.',
  'why_en':'Rationale: a class, inline function, or template of a given name must have exactly one token-identical definition across the whole program (ODR). Impact: defining Packet with different layouts in different TUs lets the linker pick one arbitrarily, causing size/offset mismatch and silent memory corruption. Fix: put the type or inline-function definition in a single header that every TU includes.'},

 {'id':'OOP50-CPP','cat':'OOP · Rule · L1','compiles':True,
  'title':'생성자/소멸자에서 가상 함수를 호출하지 않는다',
  'title_en':'Do not invoke virtual functions from constructors or destructors',
  'bad': r"""#include <iostream>
struct Base {
    Base() { init(); }                       // 생성 중 — 동적 타입은 아직 Base
    virtual void init() { std::cout << "Base::init\n"; }
};
struct Derived : Base {
    int* buf;
    void init() override { buf = new int[4]; std::cout << "Derived::init\n"; }
};
int main() {
    Derived d;            // Derived::init 이 아니라 Base::init 호출 → buf 미할당
    std::cout << "done\n";
}""",
  'good': r"""#include <iostream>
struct Base {
    Base() { }                                // 생성자에서는 가상 호출 안 함
    void start() { init(); }                  // 생성 완료 후 별도 호출
    virtual void init() { std::cout << "Base::init\n"; }
};
struct Derived : Base {
    void init() override { std::cout << "Derived::init\n"; }
};
int main() {
    Derived d;
    d.start();            // 이제 Derived::init 으로 정상 디스패치
}""",
  'why':'근거: 생성·소멸 중에는 객체의 동적 타입이 현재 실행 중인 생성자/소멸자의 클래스로 고정되어, 가상 호출이 파생 오버라이드로 가지 않고 그 클래스 버전으로 정적 디스패치된다. 영향: 파생 클래스의 초기화를 기대한 가상 호출이 기반 버전을 부르면 멤버가 준비되지 않은 채 진행되어 미초기화 접근·논리 오류가 난다. 대응: 가상 동작이 필요한 초기화는 생성이 끝난 뒤 별도 메서드에서 호출한다.',
  'why_en':'Rationale: during construction and destruction the dynamic type of the object is fixed to the class whose constructor/destructor is running, so a virtual call dispatches statically to the version in that class, not a derived override. Impact: a virtual call expected to run derived initialization instead runs the base version, proceeding with uninitialized members and logic errors. Fix: perform virtual-dependent initialization in a separate method called after construction completes.'},

 {'id':'OOP51-CPP','cat':'OOP · Rule · L2','compiles':True,
  'title':'파생 객체를 슬라이싱(slicing)하지 않는다',
  'title_en':'Do not slice derived objects',
  'bad': r"""#include <iostream>
struct Shape { virtual double area() const { return 0; } };
struct Circle : Shape {
    double r;
    Circle(double r):r(r){}
    double area() const override { return 3.14159*r*r; }
};
static void print(Shape s) {                  // 값 전달 — 파생 부분이 잘림
    std::cout << s.area() << '\n';            // 항상 Shape::area → 0
}
int main() { print(Circle{2.0}); }""",
  'good': r"""#include <iostream>
struct Shape { virtual double area() const { return 0; } };
struct Circle : Shape {
    double r;
    Circle(double r):r(r){}
    double area() const override { return 3.14159*r*r; }
};
static void print(const Shape& s) {           // 참조 전달 — 다형성 보존
    std::cout << s.area() << '\n';
}
int main() { print(Circle{2.0}); }""",
  'why':'근거: 파생 객체를 기반 클래스 값 매개변수로 받으면 기반 부분만 복사되고 파생 클래스가 추가한 멤버와 vtable 연결이 잘려 나간다(slicing). 영향: 가상 디스패치가 기반 버전으로 고정되어 Circle 의 area() 가 호출되지 못하고 0 이 반환되는 등 다형성이 조용히 깨진다. 대응: 다형 객체는 항상 기반 타입의 참조나 포인터로 전달·보관한다.',
  'why_en':'Rationale: receiving a derived object by a base-class value parameter copies only the base subobject, slicing off the derived members and the vtable link. Impact: virtual dispatch is fixed to the base version, so Circle::area is never called and 0 is returned — polymorphism silently breaks. Fix: always pass and store polymorphic objects by reference or pointer to the base type.'},

 {'id':'OOP52-CPP','cat':'OOP · Rule · L1','compiles':True,
  'title':'가상 소멸자가 없는 다형 객체를 기반 포인터로 delete 하지 않는다',
  'title_en':'Do not delete a polymorphic object through a base pointer lacking a virtual destructor',
  'bad': r"""#include <iostream>
struct Base { ~Base() { std::cout << "~Base\n"; } };   // 비가상 소멸자
struct Derived : Base {
    int* res;
    Derived(){ res = new int[100]; }
    ~Derived(){ delete[] res; std::cout << "~Derived\n"; }
};
int main() {
    Base* p = new Derived;
    delete p;             // ~Derived 미호출 → res 누수, 미정의 동작
}""",
  'good': r"""#include <iostream>
struct Base { virtual ~Base() = default; };            // 가상 소멸자
struct Derived : Base {
    int* res;
    Derived(){ res = new int[100]; }
    ~Derived() override { delete[] res; std::cout << "~Derived\n"; }
};
int main() {
    Base* p = new Derived;
    delete p;             // ~Derived → ~Base 정상 호출
}""",
  'why':'근거: 기반 클래스 소멸자가 가상이 아니면 기반 포인터로 delete 할 때 정적 타입의 소멸자만 호출되고 파생 소멸자는 호출되지 않는다(미정의 동작). 영향: 파생 클래스가 소유한 자원이 정리되지 않아 누수되고, 일부 구현에서는 잘못된 크기로 해제되어 힙이 손상된다. 대응: 다형적으로 삭제될 기반 클래스에는 가상(또는 protected 비가상) 소멸자를 둔다.',
  'why_en':'Rationale: if the base destructor is not virtual, deleting through a base pointer invokes only the destructor of the static type, not the derived one (undefined behaviour). Impact: resources owned by the derived class are not cleaned up and leak, and some implementations free with the wrong size, corrupting the heap. Fix: give a base class that will be deleted polymorphically a virtual (or protected non-virtual) destructor.'},

 {'id':'OOP53-CPP','cat':'OOP · Rule · L3','compiles':True,
  'title':'생성자 멤버 초기화 목록을 선언 순서대로 작성한다',
  'title_en':'Write constructor member initializers in canonical (declaration) order',
  'bad': r"""#include <iostream>
struct S {
    int a;
    int b;
    S(int x) : b(x), a(b) {}   // 목록 순서와 무관: 실제로는 a 가 먼저 초기화됨
};                              // a(b) 시점에 b 는 아직 미초기화
int main() {
    S s(5);
    std::cout << s.a << ' ' << s.b << '\n';   // a 는 쓰레기 값
}""",
  'good': r"""#include <iostream>
struct S {
    int a;
    int b;
    S(int x) : a(x), b(x) {}   // 선언 순서(a, b)와 일치 — 의존성 제거
};
int main() {
    S s(5);
    std::cout << s.a << ' ' << s.b << '\n';
}""",
  'why':'근거: 멤버는 초기화 목록에 적은 순서가 아니라 클래스 내 선언 순서대로 초기화된다. 영향: b(x), a(b) 처럼 적으면 직관과 달리 a 가 먼저 초기화되어 아직 미초기화된 b 를 읽어 a 에 쓰레기 값이 들어간다. 대응: 초기화 목록을 항상 선언 순서대로 적고, 한 멤버를 다른 멤버로 초기화하는 의존을 피한다.',
  'why_en':'Rationale: members are initialized in their declaration order within the class, not in the order written in the initializer list. Impact: writing b(x), a(b) initializes a first against intuition, reading the still-uninitialized b and giving a a garbage value. Fix: always list initializers in declaration order and avoid initializing one member from another.'},

 {'id':'OOP54-CPP','cat':'OOP · Rule · L3','compiles':True,
  'title':'자기 대입(self copy-assignment)을 안전하게 처리한다',
  'title_en':'Gracefully handle self copy-assignment',
  'bad': r"""#include <iostream>
struct Buf {
    int* data;
    Buf(int v): data(new int(v)) {}
    ~Buf(){ delete data; }
    Buf& operator=(const Buf& o) {
        delete data;                 // o 가 this 면 자기 데이터를 먼저 해제
        data = new int(*o.data);     // 해제된 메모리에서 복사 — use-after-free
        return *this;
    }
};
int main() {
    Buf b(7);
    b = b;                           // 자기 대입 — UAF
    std::cout << *b.data << '\n';
}""",
  'good': r"""#include <iostream>
#include <utility>
struct Buf {
    int* data;
    Buf(int v): data(new int(v)) {}
    Buf(const Buf& o): data(new int(*o.data)) {}
    ~Buf(){ delete data; }
    Buf& operator=(Buf o) {          // copy-and-swap — 자기 대입 자동 안전
        std::swap(data, o.data);
        return *this;
    }
};
int main() {
    Buf b(7);
    b = b;
    std::cout << *b.data << '\n';
}""",
  'why':'근거: 복사 대입에서 기존 자원을 먼저 해제하고 원본을 복사하는 순서로 작성하면, 원본과 대상이 같은 객체(self-assignment)일 때 복사할 원본이 이미 해제된 상태가 된다. 영향: use-after-free 로 쓰레기 값을 읽거나 크래시가 나며, 이중 해제로 힙이 손상될 수 있다. 대응: copy-and-swap 관용구(또는 명시적 자기 검사)를 사용해 자기 대입에서도 항상 안전하게 만든다.',
  'why_en':'Rationale: a copy-assignment that frees the existing resource before copying the source breaks when source and target are the same object, because the source is already freed when copied. Impact: a use-after-free reads garbage or crashes, and a double free can corrupt the heap. Fix: use the copy-and-swap idiom (or an explicit self-check) so self-assignment is always safe.'},

 {'id':'OOP58-CPP','cat':'OOP · Rule · L2','compiles':True,
  'title':'복사 연산은 원본(source)을 변경하지 않는다',
  'title_en':'Copy operations must not mutate the source',
  'bad': r"""#include <iostream>
struct Handle {
    int* p;
    Handle(int v): p(new int(v)) {}
    ~Handle(){ delete p; }
    Handle(const Handle& o) {        // '복사'인데 원본을 비워버림
        p = o.p;
        const_cast<Handle&>(o).p = nullptr;   // 원본 훼손 — 복사 의미 위반
    }
};
int main() {
    Handle a(3);
    Handle b = a;                    // a 가 망가짐
    std::cout << (a.p ? *a.p : -1) << '\n';   // -1 — 원본이 비었음
}""",
  'good': r"""#include <iostream>
#include <utility>
struct Handle {
    int* p;
    Handle(int v): p(new int(v)) {}
    ~Handle(){ delete p; }
    Handle(const Handle& o): p(o.p ? new int(*o.p) : nullptr) {}   // 깊은 복사, 원본 보존
    Handle(Handle&& o) noexcept : p(o.p) { o.p = nullptr; }        // 비우기는 이동만
};
int main() {
    Handle a(3);
    Handle b = a;                    // a 보존
    std::cout << (a.p ? *a.p : -1) << '\n';   // 3
}""",
  'why':'근거: 복사 생성/대입은 원본을 읽기만 하고 그대로 보존해야 한다는 것이 복사의 의미론적 계약이며, 그래서 매개변수가 const 참조다. 영향: 복사가 원본을 비우거나 바꾸면 const_cast 로 계약을 위반하게 되고, 표준 알고리즘·컨테이너가 사본을 자유롭게 만든다는 가정 아래 원본이 예기치 않게 파괴된다. 대응: 원본을 비우는 동작은 이동 생성/대입에만 두고 복사는 깊은 복사로 원본을 보존한다.',
  'why_en':'Rationale: copy construction/assignment must only read and preserve the source — that is the semantic contract, which is why the parameter is a const reference. Impact: a copy that empties or alters the source violates the contract via const_cast, and standard algorithms/containers that freely make copies will unexpectedly destroy the original. Fix: put emptying behaviour only in move construction/assignment and keep copy as a deep copy that preserves the source.'},

 {'id':'EXP50-CPP','cat':'EXP · Rule · L2','compiles':True,
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'title_en':'Do not depend on the order of evaluation for side effects',
  'bad': r"""#include <iostream>
static int g(int x){ std::cout << "g(" << x << ") "; return x; }
int main() {
    int i = 0;
    int r = g(i++) + g(i++);   // 두 g 호출의 평가 순서가 미명세 — 인쇄 순서·증분 시점 불확정
    std::cout << "= " << r << '\n';
}""",
  'good': r"""#include <iostream>
static int g(int x){ std::cout << "g(" << x << ") "; return x; }
int main() {
    int i = 0;
    int a = g(i++);            // 부작용을 분리 — 순서 확정
    int b = g(i++);
    int r = a + b;
    std::cout << "= " << r << '\n';
}""",
  'why':'근거: 한 식 안의 여러 함수 호출 인자나 피연산자의 평가 순서는(C++17에서 일부 강화됐어도) 일반적으로 미명세라 같은 변수를 여러 번 수정·읽으면 결과가 정해지지 않는다. 영향: 컴파일러·최적화 수준에 따라 다른 값이 나와 이식성·재현성이 깨지고, 같은 객체에 부작용이 겹치면 미정의 동작이 된다. 대응: 부작용을 별도 문장으로 분리해 순서를 명시적으로 확정한다.',
  'why_en':'Rationale: the evaluation order of multiple call arguments or operands within one expression is generally unspecified (even with C++17 tightening), so modifying and reading the same variable multiple times gives an indeterminate result. Impact: different values appear depending on compiler/optimization, breaking portability and reproducibility, and overlapping side effects on one object are undefined behaviour. Fix: split side effects into separate statements to fix the order explicitly.'},

 {'id':'EXP51-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'잘못된 타입의 포인터로 배열을 delete 하지 않는다',
  'title_en':'Do not delete an array through a pointer of the incorrect type',
  'bad': r"""#include <iostream>
struct Base { int x = 1; };
struct Derived : Base { int y = 2; };           // sizeof(Derived) > sizeof(Base)
int main() {
    Base* p = new Derived[3];   // 배열 요소는 Derived 크기, 포인터는 Base*
    delete[] p;                 // delete[] 가 Base 보폭으로 순회 — 미정의 동작
    std::cout << "done\n";
}""",
  'good': r"""#include <iostream>
#include <vector>
struct Base { int x = 1; };
struct Derived : Base { int y = 2; };
int main() {
    std::vector<Derived> v(3);  // 다형 배열 대신 컨테이너로 타입·수명 관리
    std::cout << v.size() << '\n';
}""",
  'why':'근거: delete[] 는 정적 포인터 타입의 크기로 각 요소 주소를 계산해 소멸자를 호출하는데, 배열 실제 요소 타입이 더 큰 파생 클래스면 보폭이 어긋난다. 영향: 잘못된 주소에서 소멸자를 호출하고 잘못된 크기로 해제해 미정의 동작·힙 손상이 발생한다. 대응: 다형 객체 배열은 raw new[]/delete[] 대신 std::vector 나 스마트 포인터 컨테이너로 관리한다.',
  'why_en':'Rationale: delete[] computes each element address using the size of the static pointer type to call destructors, so if the real element type is a larger derived class the stride is wrong. Impact: it calls destructors at wrong addresses and frees with the wrong size, causing undefined behaviour and heap corruption. Fix: manage arrays of polymorphic objects with std::vector or smart-pointer containers instead of raw new[]/delete[].'},

 {'id':'EXP52-CPP','cat':'EXP · Rule · L3','compiles':True,
  'title':'미평가 피연산자(sizeof 등)의 부작용에 의존하지 않는다',
  'title_en':'Do not rely on side effects in unevaluated operands',
  'bad': r"""#include <iostream>
int main() {
    int a[5] = {0};
    int i = 0;
    std::size_t n = sizeof(a[i++]);   // sizeof 의 피연산자는 미평가 — i++ 가 일어나지 않음
    std::cout << n << ' ' << i << '\n';   // i 는 여전히 0
}""",
  'good': r"""#include <iostream>
int main() {
    int a[5] = {0};
    int i = 0;
    std::size_t n = sizeof(a[0]);     // 부작용 없는 표현
    ++i;                              // 의도한 증가는 별도 문장으로
    std::cout << n << ' ' << i << '\n';
}""",
  'why':'근거: sizeof, decltype, noexcept, typeid(다형 glvalue 제외) 의 피연산자는 평가되지 않고 타입만 검사되므로 그 안의 부작용(증가·호출·할당)은 실행되지 않는다. 영향: i++ 같은 부작용이 일어났다고 가정하면 카운터·인덱스가 갱신되지 않아 논리 오류가 조용히 생긴다. 대응: 의도한 부작용은 미평가 문맥 밖의 별도 문장에서 수행한다.',
  'why_en':'Rationale: the operands of sizeof, decltype, noexcept, and typeid (except a polymorphic glvalue) are unevaluated — only their type is inspected — so side effects inside (increment, call, assignment) do not run. Impact: assuming a side effect like i++ happened leaves counters/indices unchanged, silently introducing logic errors. Fix: perform intended side effects in a separate statement outside the unevaluated context.'},

 {'id':'EXP53-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'title_en':'Do not read uninitialized memory',
  'bad': r"""#include <iostream>
struct Point { int x; int y; };
int main() {
    Point p;                 // 자동 저장 기간 — x, y 불확정
    int sum = p.x + p.y;     // 미초기화 멤버 읽기 — 미정의 동작
    std::cout << sum << '\n';
}""",
  'good': r"""#include <iostream>
struct Point { int x = 0; int y = 0; };   // 기본 멤버 초기화
int main() {
    Point p{3, 4};
    int sum = p.x + p.y;
    std::cout << sum << '\n';
}""",
  'why':'근거: 자동 저장 기간의 기본 타입·집합체는 명시 초기화가 없으면 불확정 값을 가지며, 그 값을 읽는 것은 미정의 동작이다. 영향: 디버그 빌드에서는 우연히 0 이 나오다가 릴리스에서 다른 값이 나오는 등 재현이 어려운 버그가 되고, 보안상 이전 스택 내용이 누출될 수 있다. 대응: 선언 시 기본 멤버 초기화나 중괄호 초기화로 모든 멤버를 사용 전에 초기화한다.',
  'why_en':'Rationale: fundamental types and aggregates with automatic storage have indeterminate values without explicit initialization, and reading such a value is undefined behaviour. Impact: it may incidentally read 0 in a debug build but differ in release, producing hard-to-reproduce bugs and potentially leaking prior stack contents. Fix: initialize every member before use via default member initializers or brace initialization.'},

 {'id':'EXP54-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'수명이 끝난(out-of-lifetime) 객체에 접근하지 않는다',
  'title_en':'Do not access an object outside of its lifetime',
  'bad': r"""#include <iostream>
#include <string>
static const std::string& pick(bool b) {
    std::string local = b ? "yes" : "no";   // 지역 객체
    return local;                            // 소멸될 객체에 대한 참조 반환
}
int main() {
    const std::string& r = pick(true);       // r 는 이미 소멸된 객체를 가리킴
    std::cout << r << '\n';                   // 댕글링 참조 접근 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <string>
static std::string pick(bool b) {            // 값으로 반환
    return b ? "yes" : "no";
}
int main() {
    std::string s = pick(true);              // 수명이 보장되는 객체에 보관
    std::cout << s << '\n';
}""",
  'why':'근거: 지역 변수나 임시 객체의 수명이 끝난 뒤 그것을 가리키는 참조·포인터로 접근하는 것은 미정의 동작이다. 영향: 함수가 지역 객체의 참조를 반환하면 호출자는 이미 해제된 스택 메모리를 읽어 쓰레기 값·크래시·보안 취약점이 발생한다. 대응: 함수 밖에서 필요한 값은 값으로 반환하거나 수명이 호출자보다 긴 객체에 보관한다.',
  'why_en':'Rationale: accessing an object through a reference or pointer after its lifetime has ended (local or temporary) is undefined behaviour. Impact: returning a reference to a local makes the caller read already-freed stack memory, producing garbage, crashes, or security vulnerabilities. Fix: return needed values by value or store them in an object whose lifetime outlives the caller.'},

 {'id':'EXP55-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'cv 한정(const/volatile) 객체를 비한정 타입으로 접근하지 않는다',
  'title_en':'Do not access a cv-qualified object through a non-cv-qualified type',
  'bad': r"""#include <iostream>
int main() {
    const int k = 5;
    int& r = const_cast<int&>(k);   // const 제거
    r = 9;                          // 진짜 const 객체 수정 — 미정의 동작
    std::cout << k << ' ' << r << '\n';   // 두 값이 어긋날 수 있음
}""",
  'good': r"""#include <iostream>
int main() {
    int k = 5;        // 수정이 필요하면 처음부터 비-const 로 선언
    k = 9;
    std::cout << k << '\n';
}""",
  'why':'근거: 진짜로 const 로 정의된 객체를 const_cast 로 제거한 경로를 통해 수정하는 것은 미정의 동작이다(컴파일러가 const 객체를 상수 폴딩·읽기 전용 메모리에 둘 수 있기 때문). 영향: 수정이 무시되거나, 일부 플랫폼에서는 읽기 전용 페이지 쓰기로 크래시가 나며, 같은 객체의 두 읽기가 다른 값을 줄 수 있다. 대응: 수정이 필요한 객체는 처음부터 비-const 로 선언하고 const_cast 로 const 를 벗겨 쓰지 않는다.',
  'why_en':'Rationale: modifying a truly const-defined object through a const_cast-stripped path is undefined behaviour, because the compiler may constant-fold it or place it in read-only memory. Impact: the write may be ignored, may crash on platforms that write-protect read-only pages, and two reads of the same object may differ. Fix: declare objects that need modification as non-const from the start and do not cast away const to write.'},

 {'id':'EXP57-CPP','cat':'EXP · Rule · L1',
  'title':'불완전(incomplete) 클래스 타입 포인터를 delete 하지 않는다',
  'title_en':'Do not delete a pointer to an incomplete class type',
  'bad': r"""struct Impl;                 // 전방 선언만 — 불완전 타입
void release(Impl* p) {
    delete p;                // 소멸자·크기를 모른 채 delete — 소멸자 미호출(미정의)
}""",
  'good': r"""#include <memory>
struct Impl;
void destroy(Impl*);         // 완전 정의가 보이는 TU 에 정의
// PIMPL: 완전 정의가 보이는 곳에서만 삭제하거나 커스텀 deleter 사용
std::unique_ptr<Impl, void(*)(Impl*)> make() {
    extern Impl* create();
    return { create(), &destroy };
}""",
  'why':'근거: 클래스 정의가 보이지 않는(불완전) 타입의 포인터를 delete 하면 컴파일러가 소멸자와 정확한 크기를 알 수 없어, 표준은 소멸자 호출 여부를 미정의로 둔다. 영향: PIMPL 관용구에서 소멸자가 호출되지 않아 자원이 누수되고, 일부 컴파일러는 경고만 내고 통과시켜 발견이 늦어진다. 대응: 완전 정의가 보이는 번역단위에서 삭제하거나, unique_ptr 에 전용 deleter 를 지정한다.',
  'why_en':'Rationale: deleting a pointer to a type whose definition is not visible (incomplete) leaves the compiler unable to know the destructor or exact size, so the standard makes calling the destructor undefined. Impact: in the PIMPL idiom the destructor is not called and resources leak, and some compilers only warn and let it pass, delaying discovery. Fix: delete in a translation unit where the full definition is visible, or give unique_ptr a dedicated deleter.'},

 {'id':'EXP61-CPP','cat':'EXP · Rule · L2','compiles':True,
  'title':'람다 객체가 캡처한 참조보다 오래 살지 않게 한다',
  'title_en':'A lambda object must not outlive any of its reference-captured objects',
  'bad': r"""#include <iostream>
#include <functional>
static std::function<int()> make() {
    int local = 42;
    return [&]{ return local; };   // 참조 캡처 — local 은 함수 종료 시 소멸
}
int main() {
    auto f = make();
    std::cout << f() << '\n';       // 댕글링 참조 접근 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <functional>
static std::function<int()> make() {
    int local = 42;
    return [local]{ return local; };   // 값 캡처 — 람다가 사본 소유
}
int main() {
    auto f = make();
    std::cout << f() << '\n';           // 42
}""",
  'why':'근거: 참조로 캡처한 변수는 람다 안에 포인터처럼 보관되므로, 그 변수가 람다보다 먼저 소멸하면 람다 내부 참조는 댕글링이 된다. 영향: 함수가 지역 변수를 참조 캡처한 람다(또는 std::function)를 반환하면 호출 시점에 해제된 스택을 읽어 쓰레기 값·크래시가 난다. 대응: 람다보다 수명이 짧을 수 있는 대상은 값으로 캡처하거나, 공유 수명이 필요하면 shared_ptr 를 캡처한다.',
  'why_en':'Rationale: a reference-captured variable is held like a pointer inside the lambda, so if it is destroyed before the lambda its captured reference dangles. Impact: returning a lambda (or std::function) that reference-captures a local makes the call read freed stack, yielding garbage or a crash. Fix: capture by value anything that may be shorter-lived than the lambda, or capture a shared_ptr when shared lifetime is needed.'},

 {'id':'EXP63-CPP','cat':'EXP · Rule · L2','compiles':True,
  'title':'이동된(moved-from) 객체의 값에 의존하지 않는다',
  'title_en':'Do not rely on the value of a moved-from object',
  'bad': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    std::string a = "payload";
    std::string b = std::move(a);   // a 는 유효하나 값은 미지정
    std::cout << "len=" << a.size() << '\n';   // 미지정 상태에 의존 — 비결정적
}""",
  'good': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    std::string a = "payload";
    std::string b = std::move(a);
    a = "reset";                    // 재사용 전 명확히 재설정
    std::cout << "len=" << a.size() << '\n';   // 5
}""",
  'why':'근거: 표준 라이브러리 타입은 이동 후 "유효하지만 미지정(valid but unspecified)" 상태가 되어, 소멸·재대입은 안전하지만 구체적 값(길이·내용)은 보장되지 않는다. 영향: 이동된 객체의 값을 읽어 계산·분기하면 구현·최적화에 따라 결과가 달라지는 비결정적 버그가 된다. 대응: 이동된 객체는 다시 대입하거나 clear() 등으로 명확한 상태로 만든 뒤에만 재사용한다.',
  'why_en':'Rationale: standard-library types are left "valid but unspecified" after a move — destruction and reassignment are safe, but the concrete value (size, contents) is not guaranteed. Impact: reading the value of a moved-from object to compute or branch yields nondeterministic bugs that vary by implementation/optimization. Fix: reuse a moved-from object only after putting it in a known state, e.g. reassigning or calling clear().'},

 {'id':'OOP57-CPP','cat':'OOP · Rule · L3','compiles':True,
  'title':'복사·비교에 C 표준 함수 대신 특수 멤버 함수/연산자를 선호한다',
  'title_en':'Prefer special member functions and overloaded operators to C Standard Library functions',
  'bad': r"""#include <iostream>
#include <cstring>
#include <string>
struct Record {
    std::string name;       // 비trivial 멤버 — 내부에 포인터 보유
    int id = 0;
};
int main() {
    Record a; a.name = "alice"; a.id = 1;
    Record b;
    std::memcpy(&b, &a, sizeof a);   // 포인터 비트만 복사 — 두 객체가 같은 버퍼 공유
    std::cout << b.name << '\n';      // 소멸 시 이중 해제로 손상
}""",
  'good': r"""#include <iostream>
#include <string>
struct Record {
    std::string name;
    int id = 0;
};
int main() {
    Record a; a.name = "alice"; a.id = 1;
    Record b = a;            // 복사 생성자 — name 을 깊은 복사
    std::cout << b.name << '\n';
}""",
  'why':'근거: std::string 처럼 비trivial 타입은 내부에 소유 포인터·불변식을 가지므로, memcpy 로 비트만 복사하면 두 객체가 같은 버퍼를 가리키게 된다. 영향: 한쪽 수정이 다른쪽에 새고, 두 객체가 소멸하면서 같은 메모리를 이중 해제해 힙이 손상된다. memcmp 역시 패딩·포인터 값을 비교해 잘못된 결과를 준다. 대응: 복사는 복사 생성자/대입, 비교는 operator== 등 클래스가 정의한 특수 멤버·연산자를 사용한다.',
  'why_en':'Rationale: non-trivial types like std::string hold owning pointers and invariants, so a bitwise memcpy makes two objects point at the same buffer. Impact: a modification on one leaks to the other, and both objects double-free the same memory on destruction, corrupting the heap; memcmp likewise compares padding/pointer values and gives wrong results. Fix: use the copy constructor/assignment for copying and operator== for comparison — the special members and operators of the class.'},

 {'id':'OOP55-CPP','cat':'OOP · Rule · L1','compiles':True,
  'title':'존재하지 않는 멤버를 멤버 포인터 연산으로 접근하지 않는다',
  'title_en':'Do not use pointer-to-member operators to access nonexistent members',
  'bad': r"""#include <iostream>
struct Base { int b = 1; };
struct Derived : Base { int d = 2; };
int main() {
    int Derived::* pm = &Derived::d;   // Derived 의 멤버를 가리킴
    Base base;
    // pm 은 Derived 레이아웃 기준 오프셋 — Base 객체엔 그 멤버가 없음
    Base* bp = &base;
    auto* dp = static_cast<Derived*>(bp);   // 잘못된 다운캐스트(실제 Derived 아님)
    std::cout << dp->*pm << '\n';            // 객체에 없는 멤버 접근 — 미정의 동작
}""",
  'good': r"""#include <iostream>
struct Base { int b = 1; };
struct Derived : Base { int d = 2; };
int main() {
    int Derived::* pm = &Derived::d;
    Derived real;                       // 멤버가 실제로 존재하는 객체
    std::cout << real.*pm << '\n';      // 2 — 안전
}""",
  'why':'근거: 멤버 포인터 .* / ->* 는 대상 객체에 그 멤버가 실제로 존재한다는 전제하에 오프셋을 적용하는데, 잘못된 다운캐스트로 얻은 객체에는 해당 멤버가 없을 수 있다. 영향: 객체 경계 밖 메모리를 읽거나 써서 미정의 동작·메모리 손상이 발생하고, 진단이 나오지 않아 발견이 어렵다. 대응: 멤버 포인터를 적용하기 전 대상 객체가 그 멤버를 가진 정확한 동적 타입인지 보장한다(dynamic_cast 검사 등).',
  'why_en':'Rationale: the .* and ->* operators apply an offset assuming the target object actually has that member, but an object obtained by an invalid downcast may not. Impact: it reads or writes memory outside the bounds of the object, causing undefined behaviour and memory corruption with no diagnostic, making it hard to find. Fix: ensure the target object has the member (correct dynamic type, e.g. via dynamic_cast) before applying a pointer-to-member.'},
]
