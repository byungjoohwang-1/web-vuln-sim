# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트2: A9~A15·M6~M9) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17 -pthread` 기준."""

RULES = [
 {'id':'A9-3-1','cat':'Required · Automated','compiles':True,
  'title':'멤버 함수가 내부 데이터에 대한 비-const 핸들을 반환하지 않게 한다',
  'title_en':'Member functions shall not return non-const handles to class data members',
  'bad': r"""#include <iostream>
#include <vector>
class Buf {
    std::vector<int> data_{1, 2, 3};
public:
    std::vector<int>& data() { return data_; }   // 내부 벡터의 수정 가능 참조 노출
};
int main() {
    Buf b;
    b.data().clear();   // 외부에서 내부 상태를 마음대로 변경 — 캡슐화 붕괴
    std::cout << b.data().size() << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
class Buf {
    std::vector<int> data_{1, 2, 3};
public:
    const std::vector<int>& data() const { return data_; }   // 읽기 전용 접근만
    void clear() { data_.clear(); }                          // 동작은 명시적 메서드로
};
int main() {
    Buf b;
    std::cout << b.data().size() << '\n';   // 3 — 외부는 읽기만 가능
}""",
  'why':'근거: 멤버 함수가 내부 데이터의 비-const 참조·포인터를 반환하면, 호출자가 클래스를 거치지 않고 그 데이터를 직접 수정할 수 있어 캡슐화가 깨진다. 영향: 외부 코드가 불변식을 검증하는 메서드를 우회해 내부 상태를 바꾸면, 클래스가 유지하려던 불변식(정렬·합계 일관성 등)이 조용히 위반되어 결함을 추적하기 어려워진다. 대응: 읽기 접근은 const 핸들만 반환하고, 변경은 불변식을 보장하는 전용 메서드를 통해서만 하게 한다.',
  'why_en':'Rationale: when a member function returns a non-const reference or pointer to internal data, callers can modify that data directly without going through the class, breaking encapsulation. Impact: external code that bypasses the validating methods to change internal state silently violates the invariants the class tries to maintain (ordering, sum consistency), making defects hard to trace. Fix: return only const handles for read access and route all changes through dedicated methods that preserve the invariants.'},

 {'id':'A9-5-1','cat':'Required · Automated','compiles':True,
  'title':'union 대신 std::variant 를 사용한다',
  'title_en':'Unions shall not be used; use std::variant instead',
  'bad': r"""#include <iostream>
union Value { int i; double d; };   // 어느 멤버가 활성인지 추적 불가
int main() {
    Value v; v.i = 42;       // i 를 활성화
    std::cout << v.d << '\n';  // 비활성 멤버 d 읽기 — 미정의 동작(타입 퍼닝)
}""",
  'good': r"""#include <iostream>
#include <variant>
using Value = std::variant<int, double>;   // 현재 타입을 스스로 추적
int main() {
    Value v = 42;            // int 보유
    if (std::holds_alternative<int>(v))
        std::cout << std::get<int>(v) << '\n';   // 잘못된 타입 접근은 예외로 차단
}""",
  'why':'근거: union 은 모든 멤버가 같은 메모리를 공유하지만 현재 어떤 멤버가 유효한지(활성 멤버)를 스스로 기록하지 않는다. 영향: 한 멤버에 쓰고 다른 멤버로 읽으면(타입 퍼닝) 미정의 동작이며, 활성 멤버를 잘못 추적하면 쓰레기 값·크래시가 나는데 컴파일러는 이를 막아주지 못한다. 대응: 활성 타입을 스스로 추적하고 잘못된 접근을 예외로 막는 std::variant 를 사용한다.',
  'why_en':'Rationale: a union shares one memory for all members but does not itself record which member is currently valid (the active member). Impact: writing one member and reading another (type punning) is undefined behaviour, and mistracking the active member yields garbage or crashes, which the compiler cannot prevent. Fix: use std::variant, which tracks the active type itself and blocks wrong accesses with an exception.'},

 {'id':'A10-2-1','cat':'Required · Automated','compiles':True,
  'title':'파생 클래스에서 비가상 멤버 함수를 재정의(hide)하지 않는다',
  'title_en':'Non-virtual member functions shall not be redefined in derived classes',
  'bad': r"""#include <iostream>
struct Base    { void f() { std::cout << "Base::f\n"; } };       // 비가상
struct Derived : Base { void f() { std::cout << "Derived::f\n"; } };  // 이름 숨김
int main() {
    Derived d;
    Base& b = d;
    b.f();   // 정적 타입이 Base → Base::f (다형성 아님, 직관과 다름)
}""",
  'good': r"""#include <iostream>
struct Base    { virtual void f() { std::cout << "Base::f\n"; } };
struct Derived : Base { void f() override { std::cout << "Derived::f\n"; } };
int main() {
    Derived d;
    Base& b = d;
    b.f();   // 가상 디스패치 → Derived::f (의도대로)
}""",
  'why':'근거: 기반 클래스의 비가상 함수를 파생 클래스에서 같은 이름으로 다시 정의하면, 다형적 재정의(override)가 아니라 단순한 이름 숨김(name hiding)이 되어 호출되는 함수가 객체의 동적 타입이 아닌 정적 타입에 따라 결정된다. 영향: 기반 참조·포인터로 호출하면 파생 버전이 아닌 기반 버전이 불려, 다형성을 기대한 코드가 조용히 잘못된 동작을 한다. 대응: 다형성이 필요하면 기반 함수를 virtual 로 선언하고 파생에서 override 로 재정의하며, 다형성이 불필요하면 이름을 숨기지 않도록 다른 이름을 쓴다.',
  'why_en':'Rationale: redefining a base non-virtual function with the same name in a derived class is not polymorphic overriding but mere name hiding, so the function called is chosen by the static type of the object rather than its dynamic type. Impact: a call through a base reference or pointer invokes the base version instead of the derived one, so code expecting polymorphism silently misbehaves. Fix: when polymorphism is needed declare the base function virtual and override it in the derived class, and when it is not, avoid hiding by using a different name.'},

 {'id':'A10-3-1','cat':'Required · Automated','compiles':True,
  'title':'가상 함수 선언에 virtual/override/final 중 정확히 하나만 사용한다',
  'title_en':'Virtual function declaration shall contain exactly one of the three specifiers',
  'bad': r"""#include <iostream>
struct B { virtual void f() { std::cout << "B\n"; } };
struct D : B {
    virtual void f() override { std::cout << "D\n"; }   // virtual + override 중복
};
int main() { D d; d.f(); }""",
  'good': r"""#include <iostream>
struct B { virtual void f() { std::cout << "B\n"; } };
struct D : B {
    void f() override { std::cout << "D\n"; }   // override 만 — 재정의 의도 명확
};
int main() { D d; d.f(); }""",
  'why':'근거: 재정의 함수에 virtual 과 override 를 함께 쓰면 의미가 중복되고(virtual 은 이미 기반에서 결정됨), 어떤 의도(새 가상 함수인지 재정의인지)인지 모호해진다. 영향: 일관성이 없는 표기는 독자에게 혼란을 주고, 새 가상 함수와 재정의를 구분하기 어렵게 해 유지보수 실수를 부른다. 대응: 새로 도입하는 가상 함수에는 virtual 만, 재정의에는 override 만, 더 이상 재정의 불가로 봉인할 때는 final 만 사용한다.',
  'why_en':'Rationale: combining virtual and override on a redefining function is redundant (virtual is already determined by the base) and obscures whether the intent is a new virtual function or an override. Impact: inconsistent notation confuses readers and makes it hard to distinguish new virtual functions from overrides, inviting maintenance mistakes. Fix: use virtual alone on a newly introduced virtual function, override alone on a redefinition, and final alone when sealing against further overriding.'},

 {'id':'A10-3-2','cat':'Required · Automated','compiles':True,
  'title':'재정의하는 모든 가상 함수에 override 를 표시한다',
  'title_en':'Each overriding virtual function shall be declared with the override specifier',
  'bad': r"""#include <iostream>
struct B { virtual void f(int) { std::cout << "B::f(int)\n"; } };
struct D : B {
    void f(long) { std::cout << "D::f(long)\n"; }   // 시그니처 다름 → 재정의 아님(새 함수)
};
int main() {
    D d; B& b = d;
    b.f(1);   // B::f(int) 호출 — 재정의로 믿었다면 조용한 버그
}""",
  'good': r"""#include <iostream>
struct B { virtual void f(int) { std::cout << "B::f(int)\n"; } };
struct D : B {
    void f(int) override { std::cout << "D::f(int)\n"; }   // override → 시그니처 검증
};
int main() {
    D d; B& b = d;
    b.f(1);   // D::f(int) 호출 — 의도대로 재정의
}""",
  'why':'근거: override 지정자는 그 함수가 기반 클래스의 가상 함수를 실제로 재정의하는지 컴파일러가 검증하게 한다. 영향: override 를 빠뜨리고 시그니처가 미세하게 다르면(f(int) 대 f(long)) 재정의가 아니라 별개의 새 함수가 만들어지는데 컴파일러가 경고하지 않아, 기반 포인터 호출이 엉뚱한 함수로 가는 조용한 버그가 된다. 대응: 재정의하는 모든 가상 함수에 override 를 붙여 시그니처 불일치를 컴파일 오류로 잡는다.',
  'why_en':'Rationale: the override specifier makes the compiler verify that a function actually overrides a base-class virtual function. Impact: omitting override with a slightly different signature (f(int) vs f(long)) creates a separate new function instead of an override, with no warning, so a base-pointer call goes to the wrong function — a silent bug. Fix: add override to every overriding virtual function so a signature mismatch becomes a compile error.'},

 {'id':'A11-3-1','cat':'Required · Automated','compiles':True,
  'title':'friend 선언을 사용하지 않는다',
  'title_en':'Friend declarations shall not be used',
  'bad': r"""#include <iostream>
class Account {
    friend class Auditor;   // Auditor 에 내부를 통째로 개방 — 캡슐화 우회
    double balance_ = 100.0;
};
class Auditor {
public:
    double peek(const Account& a) { return a.balance_; }   // private 직접 접근
};
int main() { Account a; Auditor au; std::cout << au.peek(a) << '\n'; }""",
  'good': r"""#include <iostream>
class Account {
    double balance_ = 100.0;
public:
    double balance() const { return balance_; }   // 명시적 공개 인터페이스
};
class Auditor {
public:
    double peek(const Account& a) { return a.balance(); }   // 공개 API 만 사용
};
int main() { Account a; Auditor au; std::cout << au.peek(a) << '\n'; }""",
  'why':'근거: friend 선언은 다른 클래스·함수에 private/protected 멤버 전체를 개방해 접근 제어를 우회한다. 영향: friend 관계는 두 클래스를 강하게 결합시켜, 한쪽의 내부 표현을 바꾸면 friend 도 함께 깨지고, 캡슐화로 보호하려던 불변식을 외부가 직접 위반할 수 있게 만든다. 대응: 필요한 협력은 의도를 드러내는 명시적 공개 인터페이스(접근자·동작 메서드)로 제공하고 friend 의존을 제거한다.',
  'why_en':'Rationale: a friend declaration opens all private/protected members to another class or function, bypassing access control. Impact: a friend relationship tightly couples two classes, so changing the internal representation of one breaks the friend too, and it lets outside code directly violate invariants that encapsulation was meant to protect. Fix: provide needed collaboration through an intent-revealing public interface (accessors, action methods) and remove the friend dependency.'},

 {'id':'A12-0-1','cat':'Required · Automated','compiles':True,
  'title':'특수 멤버 중 하나를 정의하면 모두 정의하거나 모두 생략한다(Rule of Five/Zero)',
  'title_en':'If a class declares any of the special member functions, it shall declare all of them',
  'bad': r"""#include <iostream>
class R {
    int* p_;
public:
    explicit R(int v) : p_(new int(v)) {}
    ~R() { delete p_; }   // 소멸자만 정의 → 복사 생성/대입은 얕은 복사 → 이중 해제
    int get() const { return *p_; }
};
int main() {
    R a(5);
    R b = a;   // 컴파일러 생성 복사 — p_ 포인터만 복사, a/b 가 같은 메모리 소유
    std::cout << b.get() << '\n';
}              // a, b 소멸 시 같은 p_ 를 두 번 delete — 힙 손상""",
  'good': r"""#include <iostream>
#include <memory>
class R {
    std::unique_ptr<int> p_;   // Rule of Zero — 소유권을 스마트포인터에 위임
public:
    explicit R(int v) : p_(std::make_unique<int>(v)) {}
    int get() const { return *p_; }
};
int main() {
    R a(5);
    // R b = a;  // unique_ptr 이 복사 불가 → 얕은 복사 자체가 컴파일 차단
    std::cout << a.get() << '\n';
}""",
  'why':'근거: 소멸자·복사 생성자·복사 대입·이동 생성자·이동 대입은 자원 관리에서 한 묶음으로 동작하며, 하나만 사용자 정의하면 나머지는 컴파일러가 생성한 얕은(멤버별) 버전을 쓴다. 영향: 소멸자만 정의해 raw 포인터를 해제하면, 얕은 복사로 두 객체가 같은 포인터를 소유해 소멸 시 이중 해제로 힙이 손상된다. 대응: 다섯 특수 멤버를 모두 일관되게 정의하거나(Rule of Five), 더 나아가 자원을 스마트 포인터·컨테이너에 위임해 특수 멤버를 아예 선언하지 않는다(Rule of Zero).',
  'why_en':'Rationale: the destructor, copy constructor, copy assignment, move constructor, and move assignment work together for resource management, and defining only one leaves the rest as compiler-generated shallow (member-wise) versions. Impact: defining only a destructor that frees a raw pointer means a shallow copy lets two objects own the same pointer, double-freeing and corrupting the heap on destruction. Fix: define all five special members consistently (Rule of Five), or better, delegate resources to smart pointers/containers and declare none of them (Rule of Zero).'},

 {'id':'A12-1-1','cat':'Required · Automated','compiles':True,
  'title':'생성자는 모든 기반 클래스와 비정적 멤버를 명시적으로 초기화한다',
  'title_en':'Constructors shall explicitly initialize all virtual base classes, all direct non-virtual base classes and all non-static data members',
  'bad': r"""#include <iostream>
class P {
    int x_;
    int y_;
public:
    P() { x_ = 0; }   // y_ 를 초기화하지 않음 → 불확정 값
    void print() const { std::cout << x_ << ' ' << y_ << '\n'; }
};
int main() { P p; p.print(); }   // y_ 는 쓰레기 값""",
  'good': r"""#include <iostream>
class P {
    int x_;
    int y_;
public:
    P() : x_{0}, y_{0} {}   // 모든 멤버를 초기화 목록에서 명시 초기화
    void print() const { std::cout << x_ << ' ' << y_ << '\n'; }
};
int main() { P p; p.print(); }   // 0 0""",
  'why':'근거: 생성자가 어떤 비정적 멤버를 초기화 목록에서도 본문에서도 초기화하지 않으면, 기본 타입 멤버는 불확정 값으로 남는다. 영향: 미초기화 멤버를 읽으면 미정의 동작이 되어, 디버그에서는 우연히 0 이 나오다 릴리스에서 다른 값이 나오는 재현 어려운 버그가 된다. 대응: 모든 기반 클래스와 멤버를 생성자 초기화 목록에서 명시적으로 초기화하고(가능하면 기본 멤버 초기자도 활용), 컴파일러 경고(-Weffc++ 등)를 켠다.',
  'why_en':'Rationale: if a constructor initializes some non-static member neither in the initializer list nor in the body, a fundamental-type member is left with an indeterminate value. Impact: reading an uninitialized member is undefined behaviour, producing a hard-to-reproduce bug that incidentally reads 0 in debug but differs in release. Fix: explicitly initialize all base classes and members in the constructor initializer list (also using default member initializers where possible) and enable compiler warnings.'},

 {'id':'A12-1-4','cat':'Required · Automated','compiles':True,
  'title':'단일 인자 생성자는 explicit 로 선언한다',
  'title_en':'All constructors that are callable with a single argument shall be declared explicit',
  'bad': r"""#include <iostream>
struct Meters { double v; Meters(double x) : v(x) {} };   // 암시적 변환 허용
static void travel(Meters m) { std::cout << m.v << "m\n"; }
int main() {
    travel(3.0);   // double 3.0 이 조용히 Meters 로 변환 — 단위 혼동 위험
}""",
  'good': r"""#include <iostream>
struct Meters { double v; explicit Meters(double x) : v(x) {} };   // 명시적 생성만
static void travel(Meters m) { std::cout << m.v << "m\n"; }
int main() {
    travel(Meters{3.0});   // 의도를 분명히 — 단위를 명시적으로 감쌈
}""",
  'why':'근거: 단일 인자로 호출 가능한 생성자가 explicit 가 아니면, 컴파일러가 그 인자 타입을 클래스 타입으로 암시적으로 변환하는 경로를 열어준다. 영향: 함수 인자·반환·대입 등 예상치 못한 곳에서 double 이 Meters 로 조용히 바뀌어, 단위·의미가 다른 값이 섞이거나 오버로드 해석이 의도와 달라진다. 대응: 단일 인자 생성자를 explicit 로 선언해 변환을 명시적 생성으로만 제한한다(의도적 암시 변환은 드물게 문서화해 둔다).',
  'why_en':'Rationale: a constructor callable with a single argument that is not explicit opens a path for the compiler to implicitly convert that argument type into the class type. Impact: in unexpected places like function arguments, returns, or assignment, a double silently becomes a Meters, mixing values of different units or meanings and skewing overload resolution. Fix: declare single-argument constructors explicit to restrict conversion to explicit construction only (documenting the rare intentional implicit conversion).'},

 {'id':'A12-8-1','cat':'Required · Automated','compiles':True,
  'title':'이동/복사 연산은 이동/복사 외의 부작용을 갖지 않는다',
  'title_en':'Move and copy constructors shall move and respectively copy base classes and data members without any side effects',
  'bad': r"""#include <iostream>
static int g_copies = 0;
struct S {
    int v;
    S(int v) : v(v) {}
    S(const S& o) : v(o.v) { ++g_copies; }   // 복사에 전역 카운터 부작용
};
static S make() { return S(7); }
int main() {
    S a = make();   // 복사 생략(RVO)으로 복사 생성자 호출이 0 회일 수 있음
    std::cout << "copies=" << g_copies << '\n';   // 0? 1? 최적화에 따라 달라짐
}""",
  'good': r"""#include <iostream>
struct S {
    int v;
    S(int v) : v(v) {}
    S(const S& o) : v(o.v) {}   // 복사 의미만 — 관찰 가능한 부작용 없음
};
static S make() { return S(7); }
int main() {
    S a = make();
    std::cout << a.v << '\n';   // 7 — 복사 횟수와 무관하게 결과 일정
}""",
  'why':'근거: 컴파일러는 복사 생략(copy elision/RVO)으로 복사·이동 생성자 호출을 합법적으로 제거할 수 있어, 그 호출 횟수는 관찰 가능한 보장이 아니다. 영향: 복사·이동 연산에 로깅·카운팅·자원 등록 같은 부작용을 넣으면, 최적화 수준이나 컴파일러에 따라 그 부작용 발생 횟수가 달라져 동작이 비결정적이 된다. 대응: 복사·이동 생성자는 멤버를 복사/이동하는 의미만 구현하고, 관찰 가능한 부작용은 별도의 명시적 연산으로 분리한다.',
  'why_en':'Rationale: the compiler may legally eliminate copy/move constructor calls via copy elision (RVO), so the number of such calls is not an observable guarantee. Impact: putting side effects like logging, counting, or resource registration in copy/move operations makes the count of those side effects vary by optimization level or compiler, rendering behaviour nondeterministic. Fix: implement only the copy/move semantics of members in copy/move constructors and separate any observable side effect into an explicit operation.'},

 {'id':'A12-8-3','cat':'Required · Automated','compiles':True,
  'title':'이동된(moved-from) 객체의 값을 읽지 않는다',
  'title_en':'Moved-from object shall not be read-accessed',
  'bad': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    std::string a = "payload";
    std::string b = std::move(a);   // a 는 유효하나 값은 미지정
    std::cout << "a.size()=" << a.size() << '\n';   // 미지정 상태 읽기 — 비결정적
}""",
  'good': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    std::string a = "payload";
    std::string b = std::move(a);
    a = "reset";   // 재사용 전 명확한 값으로 재설정
    std::cout << "a.size()=" << a.size() << '\n';   // 5
}""",
  'why':'근거: 표준 라이브러리 타입은 이동 후 "유효하지만 미지정(valid but unspecified)" 상태가 되어, 소멸·재대입은 안전하지만 그 구체적 값(길이·내용)은 보장되지 않는다. 영향: 이동된 객체의 값을 읽어 계산·분기하면 구현·최적화에 따라 결과가 달라지는 비결정적 버그가 되고, 이동을 빠뜨린 진짜 논리 오류를 가린다. 대응: 이동된 객체는 다시 대입하거나 clear() 등으로 명확한 상태로 만든 뒤에만 재사용한다.',
  'why_en':'Rationale: standard-library types are left valid but unspecified after a move — destruction and reassignment are safe, but the concrete value (size, contents) is not guaranteed. Impact: reading a moved-from value to compute or branch yields nondeterministic bugs that vary by implementation/optimization and mask a real logic error of a missed move. Fix: reuse a moved-from object only after putting it in a known state, such as reassigning or calling clear().'},

 {'id':'A12-8-5','cat':'Required · Automated','compiles':True,
  'title':'복사/이동 대입은 자기 대입(self-assignment)을 처리한다',
  'title_en':'A copy assignment and a move assignment operators shall handle self-assignment',
  'bad': r"""#include <iostream>
struct S {
    int* p_;
    explicit S(int v) : p_(new int(v)) {}
    ~S() { delete p_; }
    S& operator=(const S& o) {
        delete p_;             // o 가 this 면 자기 데이터를 먼저 해제
        p_ = new int(*o.p_);   // 해제된 메모리에서 복사 — use-after-free
        return *this;
    }
};
int main() { S a(5); a = a; std::cout << *a.p_ << '\n'; }""",
  'good': r"""#include <iostream>
#include <utility>
struct S {
    int* p_;
    explicit S(int v) : p_(new int(v)) {}
    S(const S& o) : p_(new int(*o.p_)) {}
    ~S() { delete p_; }
    S& operator=(S o) {        // copy-and-swap — 자기 대입 자동 안전
        std::swap(p_, o.p_);
        return *this;
    }
};
int main() { S a(5); a = a; std::cout << *a.p_ << '\n'; }""",
  'why':'근거: 복사·이동 대입에서 기존 자원을 먼저 해제한 뒤 원본을 복사하는 순서로 작성하면, 원본과 대상이 같은 객체(자기 대입)일 때 복사할 원본이 이미 해제된 상태가 된다. 영향: use-after-free 로 쓰레기 값을 읽거나 크래시가 나고, 이중 해제로 힙이 손상될 수 있다. 대응: copy-and-swap 관용구(또는 명시적 자기 검사 if (this == &o) return *this;)로 자기 대입에서도 항상 안전하게 만든다.',
  'why_en':'Rationale: a copy/move assignment that frees the existing resource before copying the source breaks when source and target are the same object (self-assignment), because the source is already freed when copied. Impact: a use-after-free reads garbage or crashes, and a double free can corrupt the heap. Fix: use the copy-and-swap idiom (or an explicit self-check if (this == &o) return *this;) so self-assignment is always safe.'},

 {'id':'A13-2-1','cat':'Required · Automated','compiles':True,
  'title':'대입 연산자는 *this 에 대한 참조(비-const lvalue ref)를 반환한다',
  'title_en':'An assignment operator shall return a reference to this',
  'bad': r"""#include <iostream>
struct S {
    int v;
    void operator=(const S& o) { v = o.v; }   // void 반환 — 연쇄 대입 불가
};
int main() {
    S a{1}, b{2}, c{3};
    // a = b = c;  // void 반환이라 (b=c) 결과를 a 에 대입할 수 없음 — 컴파일 에러
    a = c;
    std::cout << a.v << '\n';
}""",
  'good': r"""#include <iostream>
struct S {
    int v;
    S& operator=(const S& o) { v = o.v; return *this; }   // *this 참조 반환
};
int main() {
    S a{1}, b{2}, c{3};
    a = b = c;   // 연쇄 대입 — 우→좌, 표준 관례대로 동작
    std::cout << a.v << ' ' << b.v << '\n';   // 3 3
}""",
  'why':'근거: 내장 타입의 대입식은 대입된 객체를 lvalue 로 돌려주어 a = b = c 같은 연쇄 대입과 (a = b).method() 같은 관례가 성립하는데, 사용자 정의 operator= 가 이를 따르려면 *this 에 대한 비-const lvalue 참조를 반환해야 한다. 영향: void 나 값으로 반환하면 연쇄 대입이 컴파일되지 않거나 불필요한 사본이 생겨, 표준 컨테이너·제네릭 코드가 기대하는 대입 의미와 어긋난다. 대응: 모든 대입 연산자(복사·이동·복합)는 return *this; 로 *this 참조를 반환한다.',
  'why_en':'Rationale: a built-in assignment expression yields the assigned object as an lvalue, enabling chained assignment like a = b = c and conventions like (a = b).method(), and a user-defined operator= must return a non-const lvalue reference to this to follow it. Impact: returning void or by value makes chained assignment fail to compile or creates needless copies, diverging from the assignment semantics expected by standard containers and generic code. Fix: have every assignment operator (copy, move, compound) return a reference to this via return *this;.'},

 {'id':'A13-2-3','cat':'Required · Automated','compiles':True,
  'title':'관계(비교) 연산자는 bool 을 반환한다',
  'title_en':'A relational operator shall return a boolean value',
  'bad': r"""#include <iostream>
struct S {
    int v;
    int operator<(const S& o) const { return v - o.v; }   // int 반환 — 오용 유발
};
int main() {
    S a{3}, b{3};
    if (a < b) std::cout << "less\n";   // a<b 가 거짓이어야 하는데 0(거짓)이라 우연히 맞음
    S c{5};
    std::cout << (c < a) << '\n';   // 2 출력 — bool 이 아니라 차이값
}""",
  'good': r"""#include <iostream>
struct S {
    int v;
    bool operator<(const S& o) const { return v < o.v; }   // bool 반환
};
int main() {
    S a{3}, b{3}, c{5};
    if (a < b) std::cout << "less\n";   // 정확히 false
    std::cout << std::boolalpha << (c < a) << '\n';   // false
}""",
  'why':'근거: <, <=, ==, > 같은 관계·동등 연산자는 의미상 참/거짓을 돌려주는 술어이며, 표준 알고리즘·컨테이너도 이들이 bool 로 변환되는 결과를 반환한다고 가정한다. 영향: int 같은 다른 타입을 반환하면 0 이 아닌 모든 값이 참으로 취급되어 a < b 가 차이값을 돌려주는 식의 오용이 생기고, std::sort 의 비교자나 if 조건에서 직관과 다른 결과를 낸다. 대응: 모든 관계·동등 연산자는 bool 을 반환하도록 정의한다.',
  'why_en':'Rationale: relational and equality operators like <, <=, ==, > are predicates that semantically yield true/false, and standard algorithms and containers assume they return a result convertible to bool. Impact: returning another type such as int treats every non-zero value as true, allowing misuse like a < b returning a difference, and produces counterintuitive results in std::sort comparators or if conditions. Fix: define every relational and equality operator to return bool.'},

 {'id':'A13-5-2','cat':'Required · Automated','compiles':True,
  'title':'사용자 정의 변환 연산자는 explicit 로 선언한다',
  'title_en':'All user-defined conversion operators shall be defined explicit',
  'bad': r"""#include <iostream>
struct Handle {
    int fd;
    operator int() const { return fd; }   // 암시적 변환 연산자
};
int main() {
    Handle h{7};
    int x = h + 1;   // h 가 조용히 int 로 변환되어 산술에 끼어듦 — 의도 불명
    std::cout << x << '\n';
}""",
  'good': r"""#include <iostream>
struct Handle {
    int fd;
    explicit operator int() const { return fd; }   // 명시적 변환만
};
int main() {
    Handle h{7};
    int x = static_cast<int>(h) + 1;   // 변환 의도를 명시
    std::cout << x << '\n';
}""",
  'why':'근거: explicit 가 아닌 변환 연산자는 컴파일러가 그 타입을 대상 타입으로 암시적으로 바꾸도록 허용해, 산술·비교·함수 인자 등 예상치 못한 문맥에서 변환이 일어난다. 영향: Handle 이 조용히 int 로 바뀌어 fd 값이 산술에 끼어들거나, 여러 암시 변환이 겹쳐 오버로드 해석이 의도와 다른 함수를 고르는 미묘한 버그가 된다. 대응: 변환 연산자를 explicit 로 선언해 static_cast 같은 명시적 변환을 통해서만 쓰이게 한다(단, bool 문맥용 explicit operator bool 처럼 의도된 경우만 둔다).',
  'why_en':'Rationale: a non-explicit conversion operator lets the compiler implicitly convert the type to the target type, so the conversion happens in unexpected contexts like arithmetic, comparison, or function arguments. Impact: a Handle silently becomes an int and its fd value slips into arithmetic, or stacked implicit conversions make overload resolution pick the wrong function — a subtle bug. Fix: declare conversion operators explicit so they are used only through explicit conversions like static_cast (keeping intended ones such as explicit operator bool for boolean contexts).'},

 {'id':'A14-8-2','cat':'Required · Automated','compiles':True,
  'title':'함수 템플릿의 명시적 특수화를 사용하지 않는다',
  'title_en':'Explicit specializations of function templates shall not be used',
  'bad': r"""#include <iostream>
template <typename T> void f(T)   { std::cout << "generic\n"; }
template <> void f<int>(int)      { std::cout << "int special\n"; }   // 함수 템플릿 특수화
void f(int)                       { std::cout << "int overload\n"; }   // 오버로드도 존재
int main() { f(3); }   // 특수화가 아니라 오버로드가 선택됨 — 직관과 다른 함정""",
  'good': r"""#include <iostream>
template <typename T> void f(T) { std::cout << "generic\n"; }
void f(int)                     { std::cout << "int overload\n"; }   // 일반 오버로드만
int main() { f(3); }   // int 오버로드가 명확히 선택됨""",
  'why':'근거: 함수 템플릿의 명시적 특수화는 오버로드 해석에 직접 참여하지 않고, 오버로드 해석이 먼저 기본 템플릿을 고른 뒤에만 그 특수화가 적용된다. 영향: 일반 함수 오버로드가 함께 있으면 직관과 달리 특수화가 아니라 오버로드가 선택되어, 어떤 함수가 호출될지 예측하기 어려운 함정이 된다. 대응: 타입별로 동작을 분기하려면 명시적 특수화 대신 일반 함수 오버로드(또는 클래스 템플릿 특수화)를 사용한다.',
  'why_en':'Rationale: an explicit function-template specialization does not participate directly in overload resolution; it applies only after overload resolution has first chosen the primary template. Impact: when an ordinary function overload is also present, the overload — not the specialization — is selected against intuition, a trap that makes it hard to predict which function is called. Fix: to branch behaviour by type, use ordinary function overloads (or class-template specialization) instead of explicit function-template specialization.'},

 {'id':'A15-1-1','cat':'Required · Automated','compiles':True,
  'title':'std::exception 에서 파생된 타입만 예외로 사용한다',
  'title_en':'Only instances of types derived from std::exception should be thrown',
  'bad': r"""#include <iostream>
int main() {
    try {
        throw 42;   // 정수 예외 — 표준 핸들링 계층과 무관, 메시지 없음
    }
    catch (int e) { std::cout << "caught int " << e << '\n'; }
    // 다른 곳의 catch(const std::exception&) 는 이 예외를 잡지 못함
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
int main() {
    try {
        throw std::runtime_error("invalid state");   // 표준 예외 계층
    }
    catch (const std::exception& e) { std::cout << "caught: " << e.what() << '\n'; }
}""",
  'why':'근거: int·문자열·임의 사용자 타입을 던지면 표준 예외 계층(std::exception)과 무관해, 공통 기반으로 일괄 포착(catch(const std::exception&))하거나 what() 으로 진단 메시지를 얻을 수 없다. 영향: 라이브러리·상위 계층이 std::exception 만 잡는 일반 핸들러를 두면 비표준 예외가 그 그물을 빠져나가 처리되지 않은 채 terminate 로 이어진다. 대응: 예외는 std::exception 에서 파생된 타입(표준 예외 또는 그것을 상속한 사용자 예외)만 사용해 일관된 포착과 메시지 전달을 보장한다.',
  'why_en':'Rationale: throwing an int, a string, or an arbitrary user type is unrelated to the standard exception hierarchy (std::exception), so it cannot be caught uniformly through a common base (catch(const std::exception&)) or yield a diagnostic via what(). Impact: when a library or upper layer installs a general handler catching only std::exception, a non-standard exception slips through that net and goes unhandled to terminate. Fix: throw only types derived from std::exception (standard exceptions or user exceptions inheriting them) to guarantee consistent catching and message delivery.'},

 {'id':'A15-1-2','cat':'Required · Automated','compiles':True,
  'title':'예외 객체를 포인터로 throw 하지 않는다(값으로 throw)',
  'title_en':'An exception object shall not be a pointer',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct MyError : std::runtime_error { using std::runtime_error::runtime_error; };
int main() {
    try { throw new MyError("disk"); }   // 포인터 throw — 누가 delete? 누수/이중해제
    catch (MyError* e) { std::cout << e->what() << '\n'; delete e; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct MyError : std::runtime_error { using std::runtime_error::runtime_error; };
int main() {
    try { throw MyError("disk"); }   // 값으로 throw
    catch (const MyError& e) { std::cout << e.what() << '\n'; }   // const 참조로 catch
}""",
  'why':'근거: 예외를 포인터로 던지면 그 예외 객체의 메모리를 누가·언제 해제해야 하는지가 catch 측에 위임되어 소유권이 모호해진다. 영향: catch 가 delete 를 빠뜨리면 누수, 두 번 delete 하면 이중 해제가 되고, 던진 포인터가 지역 객체를 가리키면 댕글링이 된다. 대응: 예외는 값으로 던지고 const 참조로 잡아, 예외 객체의 수명을 런타임이 자동으로 관리하게 한다.',
  'why_en':'Rationale: throwing an exception by pointer delegates to the catch site the question of who frees the exception object and when, making ownership ambiguous. Impact: the catch leaks if it forgets delete, double-frees if it deletes twice, and dangles if the thrown pointer refers to a local object. Fix: throw by value and catch by const reference so the runtime manages the lifetime of the exception object automatically.'},

 {'id':'A15-1-5','cat':'Required · Automated','compiles':True,
  'title':'예외를 실행 경계(스레드·콜백 경계 등) 너머로 던지지 않는다',
  'title_en':'Exceptions shall not be thrown across execution boundaries',
  'bad': r"""#include <thread>
#include <stdexcept>
int main(int argc, char**) {
    std::thread t([argc]{
        if (argc < 0) throw std::runtime_error("escapes thread");   // 스레드 밖으로 → terminate
    });   // (가드로 실제 throw 는 회피; 패턴 자체가 결함 — 스레드 함수의 예외는 잡을 곳이 없음)
    t.join();
}""",
  'good': r"""#include <iostream>
#include <thread>
#include <stdexcept>
#include <exception>
int main() {
    std::exception_ptr err;
    std::thread t([&err]{
        try { throw std::runtime_error("work failed"); }   // 경계 내부에서 포착
        catch (...) { err = std::current_exception(); }     // 전달 가능한 형태로 저장
    });
    t.join();
    if (err) { try { std::rethrow_exception(err); }
               catch (const std::exception& e) { std::cout << "from thread: " << e.what() << '\n'; } }
}""",
  'why':'근거: 스레드 진입 함수나 C 콜백 같은 실행 경계는 C++ 예외 전파 메커니즘 밖이라, 예외가 그 경계를 넘어 빠져나가면 표준은 std::terminate 를 호출하도록 규정한다. 영향: 스레드 함수에서 예외가 탈출하면 그 예외를 잡을 호출자 프레임이 없어 프로그램이 정리 없이 강제 종료된다. 대응: 경계 안에서 catch(...) 로 예외를 포착하고 std::exception_ptr 같은 전달 가능한 형태로 저장해, 경계 밖(join 이후 등)에서 다시 던져 처리한다.',
  'why_en':'Rationale: an execution boundary such as a thread entry function or a C callback is outside the C++ exception propagation mechanism, so the standard calls std::terminate if an exception escapes across it. Impact: an exception escaping a thread function has no caller frame to catch it, so the program is forcibly terminated without cleanup. Fix: catch the exception inside the boundary with catch(...) and store it in a transferable form like std::exception_ptr, then rethrow and handle it outside the boundary (e.g. after join).'},

 {'id':'A15-2-2','cat':'Required · Automated','compiles':True,
  'title':'생성자가 실패하면 이미 획득한 자원을 모두 해제한다',
  'title_en':'If a constructor is not noexcept and the constructor cannot finish, all already-allocated resources shall be released',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct S {
    int* a_;
    int* b_;
    S(int argc) : a_(new int(1)), b_(new int(2)) {
        if (argc >= 0) throw std::runtime_error("ctor fail");   // a_,b_ 는 소멸자 미호출 → 누수
    }
    ~S() { delete a_; delete b_; }
};
int main(int argc, char**) {
    try { S s(argc); } catch (...) { std::cout << "leaked a_ and b_\n"; }
}""",
  'good': r"""#include <iostream>
#include <memory>
#include <stdexcept>
struct S {
    std::unique_ptr<int> a_;
    std::unique_ptr<int> b_;
    S(int argc) : a_(std::make_unique<int>(1)), b_(std::make_unique<int>(2)) {
        if (argc >= 0) throw std::runtime_error("ctor fail");   // 이미 만든 멤버는 자동 해제
    }
};
int main(int argc, char**) {
    try { S s(argc); } catch (...) { std::cout << "no leak (members RAII-freed)\n"; }
}""",
  'why':'근거: 생성자 본문에서 예외가 던져지면 그 객체의 소멸자는 호출되지 않지만, 이미 완전히 생성된 멤버(서브오브젝트)의 소멸자는 호출된다. 영향: 멤버를 raw 포인터로 두고 생성자에서 new 로 할당한 뒤 예외가 나면, 객체 소멸자가 불리지 않아 그 raw 자원이 누수된다. 대응: 멤버를 unique_ptr·컨테이너 같은 RAII 타입으로 두어, 생성자가 중간에 실패해도 이미 생성된 멤버가 스택 풀기에서 자동 해제되게 한다.',
  'why_en':'Rationale: if an exception is thrown in a constructor body, the destructor of that object is not called, but destructors of already fully-constructed members (subobjects) are. Impact: keeping members as raw pointers and allocating them with new in the constructor leaks those raw resources when an exception follows, since the object destructor never runs. Fix: hold members in RAII types like unique_ptr or containers so that already-constructed members are freed automatically during unwinding even if the constructor fails partway.'},

 {'id':'A15-3-5','cat':'Required · Automated','compiles':True,
  'title':'클래스 타입 예외는 (const) 참조로 catch 한다',
  'title_en':'A class type exception shall be caught by reference or const reference',
  'bad': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::runtime_error("boom"); }
    catch (std::exception e) {   // 값 catch — 파생 예외가 base 로 슬라이싱
        std::cout << e.what() << '\n';   // 파생 정보 손실, 불필요한 복사
    }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::runtime_error("boom"); }
    catch (const std::exception& e) {   // const 참조 — 다형성·메시지 보존
        std::cout << e.what() << '\n';
    }
}""",
  'why':'근거: 예외를 값으로 잡으면 던져진 객체가 핸들러 매개변수 타입으로 복사되며, 그 타입이 기반 클래스면 파생 부분이 잘려 나간다(slicing). 영향: 파생 예외가 담은 오류 코드·문맥과 다형적 what() 동작을 잃어 진단 정보가 사라지고, 복사 자체가 예외를 던지면(메모리 부족 등) 처리 중 또 다른 문제가 생긴다. 대응: 클래스 타입 예외는 const 참조로 잡아 복사·슬라이싱 없이 실제 동적 타입의 정보를 보존한다.',
  'why_en':'Rationale: catching an exception by value copies the thrown object into the handler parameter type, and if that type is a base class the derived part is sliced off. Impact: the error code, context, and polymorphic what() behaviour carried by the derived exception are lost, and if the copy itself throws (e.g. out of memory) another problem arises during handling. Fix: catch class-type exceptions by const reference to preserve the actual dynamic type information without a copy or slicing.'},

 {'id':'A15-4-2','cat':'Required · Automated','compiles':True,
  'title':'noexcept 함수에서 예외가 빠져나가지 않게 한다',
  'title_en':'If a function is declared to be noexcept, it shall not exit with an exception',
  'bad': r"""#include <stdexcept>
static void may_throw(int argc) { if (argc >= 0) throw std::runtime_error("x"); }
static void f(int argc) noexcept { may_throw(argc); }   // noexcept 인데 예외 탈출 → terminate
int main(int argc, char**) { f(argc); }""",
  'good': r"""#include <iostream>
#include <stdexcept>
static void may_throw() { throw std::runtime_error("x"); }
static void f() noexcept {
    try { may_throw(); }
    catch (...) { std::cout << "absorbed inside noexcept fn\n"; }   // 명세 준수
}
int main() { f(); }""",
  'why':'근거: noexcept 로 선언한 함수에서 예외가 빠져나가면 표준은 즉시 std::terminate 를 호출하도록 규정하며 이는 되돌릴 수 없다. 영향: 호출자가 noexcept 를 믿고 예외 처리를 생략한 상태에서 프로그램이 정리 없이 강제 종료되고, 이동 연산이 noexcept 가 아니면 표준 컨테이너가 더 느린 복사 경로를 택하는 부작용도 있다. 대응: noexcept 함수 내부에서 예외를 try/catch 로 흡수하거나, 예외가 빠져나갈 수 있으면 noexcept 를 떼어 명세를 사실에 맞춘다.',
  'why_en':'Rationale: if an exception escapes a function declared noexcept, the standard mandates an immediate, unrecoverable call to std::terminate. Impact: callers that trusted noexcept and omitted handling see the program forcibly terminated without cleanup, and a move operation that is not noexcept has the side effect of standard containers choosing a slower copy path. Fix: absorb exceptions inside the noexcept function with try/catch, or remove noexcept so the specification matches reality if exceptions can escape.'},

 {'id':'A15-4-4','cat':'Required · Automated','compiles':True,
  'title':'예외를 던지지 않는 함수는 noexcept 로 표시한다',
  'title_en':'A declaration of a non-throwing function shall contain noexcept',
  'bad': r"""#include <iostream>
struct Buf {
    int n_ = 0;
    int size() const { return n_; }   // 던지지 않는데 noexcept 미표시
};
int main() { Buf b; std::cout << b.size() << '\n'; }""",
  'good': r"""#include <iostream>
struct Buf {
    int n_ = 0;
    int size() const noexcept { return n_; }   // 비-throw 보장을 명시
};
int main() { Buf b; std::cout << b.size() << '\n'; }""",
  'why':'근거: 예외를 절대 던지지 않는 함수에 noexcept 를 명시하면, 호출자와 표준 라이브러리가 그 보장에 기대 더 나은 최적화와 예외 안전 결정을 내릴 수 있다. 영향: 특히 이동 생성자·소멸자·swap 이 noexcept 가 아니면 std::vector 같은 컨테이너가 강한 예외 보장을 위해 이동 대신 복사를 선택해 성능이 저하되고, 인터페이스의 비-throw 의도가 코드에 드러나지 않는다. 대응: 던지지 않음이 확실한 함수(특히 이동·swap·관찰자)에 noexcept 를 붙여 보장을 명시한다.',
  'why_en':'Rationale: marking a function that never throws as noexcept lets callers and the standard library rely on that guarantee for better optimization and exception-safety decisions. Impact: in particular, when a move constructor, destructor, or swap is not noexcept, containers like std::vector choose copy over move to preserve the strong guarantee, degrading performance, and the non-throwing intent of the interface is not visible in the code. Fix: add noexcept to functions that certainly do not throw (especially move, swap, and observers) to state the guarantee.'},

 {'id':'A15-5-1','cat':'Required · Automated','compiles':True,
  'title':'특수 멤버(소멸자·이동·swap)는 예외를 던지지 않게 한다',
  'title_en':'All user-provided class destructors, deallocation functions, move constructors, move assignment operators and swap functions shall not exit with an exception',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct Conn {
    bool open_ = true;
    void send_close() { throw std::runtime_error("net error"); }
    ~Conn() { if (open_) send_close(); }   // 던지는 소멸자 — 스택 풀기 중이면 terminate
};
int main() {
    try { Conn c; } catch (const std::exception& e) { std::cout << e.what() << '\n'; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Conn {
    bool open_ = true;
    void send_close() { throw std::runtime_error("net error"); }
    ~Conn() noexcept {
        try { if (open_) send_close(); }
        catch (...) { std::cerr << "close failed in dtor, logged\n"; }   // 흡수
    }
};
int main() { Conn c; std::cout << "clean\n"; }""",
  'why':'근거: 소멸자·이동 연산·swap 은 예외 안전성의 기반으로, 다른 예외로 스택이 풀리는 도중 이들이 또 예외를 던지면 두 예외가 동시에 전파되어 std::terminate 가 호출된다. 영향: 던지는 소멸자는 정상 오류 처리 경로에서도 프로그램을 강제 종료시키고, 던지는 이동 연산은 컨테이너가 강한 예외 보장을 깨뜨려 객체를 일관성 없는 상태로 남길 수 있다. 대응: 이 특수 멤버들을 noexcept 로 선언하고 내부에서 발생 가능한 예외를 try/catch 로 흡수해 로깅만 한다.',
  'why_en':'Rationale: destructors, move operations, and swap are the foundation of exception safety, and if they themselves throw while the stack is already unwinding from another exception, two exceptions propagate at once and std::terminate is called. Impact: a throwing destructor forcibly terminates the program even on a normal error path, and a throwing move operation can break the strong guarantee of containers and leave objects in an inconsistent state. Fix: declare these special members noexcept and absorb any internal exception with try/catch, logging only.'},

 {'id':'M6-2-1','cat':'Required · Automated','compiles':True,
  'title':'대입을 하위 표현식(subexpression)에서 수행하지 않는다',
  'title_en':'Assignment operators shall not be used in sub-expressions',
  'bad': r"""#include <iostream>
static int next() { static int n = 0; return ++n; }
int main() {
    int x = 0;
    if ((x = next()) != 0) std::cout << "x=" << x << '\n';   // 조건 안 대입 — == 오타와 혼동
}""",
  'good': r"""#include <iostream>
static int next() { static int n = 0; return ++n; }
int main() {
    int x = next();   // 대입을 독립 문장으로 분리
    if (x != 0) std::cout << "x=" << x << '\n';
}""",
  'why':'근거: 조건식·인자 같은 하위 표현식 안에 대입을 끼워 넣으면, 의도한 = 인지 비교 == 의 오타인지 한눈에 구분되지 않고 부작용이 식 안에 숨는다. 영향: if (x = f()) 처럼 쓰면 비교를 의도했는데 대입이 일어나 항상 참이 되는 흔한 버그가 생기고, 평가 순서·부작용이 얽혀 분석이 어려워진다. 대응: 대입은 독립된 문장으로 분리해 부작용을 드러내고, 조건에는 비교만 둔다.',
  'why_en':'Rationale: embedding an assignment inside a sub-expression like a condition or argument makes it hard to tell at a glance whether = is intended or a typo for ==, and hides the side effect inside the expression. Impact: writing if (x = f()) when a comparison was intended performs an assignment and is always true — a common bug — and tangles evaluation order with side effects, hindering analysis. Fix: split assignment into its own statement to expose the side effect and keep only comparisons in conditions.'},

 {'id':'M6-2-2','cat':'Required · Automated','compiles':True,
  'title':'부동소수 값을 등호(==)로 비교하지 않는다',
  'title_en':'Floating-point expressions shall not be directly or indirectly tested for equality or inequality',
  'bad': r"""#include <iostream>
int main() {
    double x = 0.1 + 0.2;   // 0.30000000000000004 (표현 오차)
    if (x == 0.3) std::cout << "equal\n";
    else std::cout << "NOT equal (representation error)\n";   // 실제로 이쪽
}""",
  'good': r"""#include <iostream>
#include <cmath>
int main() {
    double x = 0.1 + 0.2;
    const double eps = 1e-9;
    if (std::fabs(x - 0.3) < eps) std::cout << "equal within tolerance\n";   // 의도대로
    else std::cout << "different\n";
}""",
  'why':'근거: 부동소수 수는 십진 소수를 이진으로 정확히 표현하지 못해 0.1 + 0.2 가 0.3 과 비트 단위로 같지 않은 등 미세한 표현 오차를 갖는다. 영향: == / != 로 정확한 동등을 검사하면 수학적으로 같아야 할 값이 거의 항상 다르다고 판정되어, 종료 조건·상태 비교가 의도와 다르게 동작한다. 대응: 두 값의 차이의 절댓값이 문제 규모에 맞는 허용 오차(epsilon) 미만인지로 비교하고, 가능하면 상대 오차도 함께 고려한다.',
  'why_en':'Rationale: floating-point numbers cannot represent decimal fractions exactly in binary, so values carry tiny representation errors — for example 0.1 + 0.2 is not bit-identical to 0.3. Impact: testing exact equality with == / != judges values that should be mathematically equal as almost always different, making termination conditions and state comparisons misbehave. Fix: compare whether the absolute difference is below a tolerance (epsilon) sized to the problem, also considering relative error where possible.'},

 {'id':'M6-3-1','cat':'Required · Automated','compiles':True,
  'title':'반복문/조건문의 본문은 복합문(중괄호)으로 감싼다',
  'title_en':'The statement forming the body of a loop or selection shall be a compound statement',
  'bad': r"""#include <iostream>
int main() {
    int n = 3;
    for (int i = 0; i < n; ++i)
        std::cout << "loop ";
        std::cout << "once\n";   // 들여쓰기 착시 — 사실 루프 밖, 1회만 실행
}""",
  'good': r"""#include <iostream>
int main() {
    int n = 3;
    for (int i = 0; i < n; ++i) {
        std::cout << "loop ";
    }
    std::cout << "once\n";   // 의도가 명확
}""",
  'why':'근거: 반복문·조건문의 본문을 중괄호 없이 단일 문으로 쓰면, 본문에 포함된 문장은 첫 한 문장뿐인데 들여쓰기는 여러 줄을 본문처럼 보이게 한다. 영향: 나중에 줄을 추가하면(예제의 둘째 출력) 그 줄이 루프 밖에 놓여 들여쓰기 착시와 실제 흐름이 어긋나는 결함이 되며, 이는 보안 패치에서 유명한 버그 유형이다. 대응: 반복문·조건문의 본문을 항상 중괄호로 감싸 범위를 명확히 한다.',
  'why_en':'Rationale: writing a loop or selection body as a single statement without braces means only the first statement is in the body, yet indentation makes several lines look like the body. Impact: later adding a line (the second print in the example) places it outside the loop, creating a mismatch between the indentation illusion and the actual flow — a famously dangerous bug type in security patches. Fix: always wrap loop and selection bodies in braces to make their extent clear.'},

 {'id':'M6-4-2','cat':'Required · Automated','compiles':True,
  'title':'if-else if 사슬은 else 로 마무리한다',
  'title_en':'All if-else if constructs shall be terminated with an else statement',
  'bad': r"""#include <iostream>
static const char* mode_name(int m) {
    if (m == 1) return "read";
    else if (m == 2) return "write";   // 그 외 값은 처리되지 않음
    return "?";   // (함수 반환이라 그나마 동작; 부작용 코드였다면 조용히 누락)
}
int main() { std::cout << mode_name(9) << '\n'; }""",
  'good': r"""#include <iostream>
static const char* mode_name(int m) {
    if (m == 1) return "read";
    else if (m == 2) return "write";
    else return "unknown";   // 나머지 경우를 명시적으로 처리
}
int main() { std::cout << mode_name(9) << '\n'; }""",
  'why':'근거: if-else if 사슬을 마지막 else 로 닫으면, 앞의 어떤 조건에도 맞지 않는 "그 외 모든 경우"가 반드시 한 곳에서 명시적으로 처리된다. 영향: else 로 닫지 않으면 예상치 못한 입력이 조용히 아무 분기도 타지 않고 지나가, 상태 갱신·검증이 누락되어 결함이 숨고 새 값 추가 시 처리가 빠진다. 대응: 모든 if-else if 사슬을 else 로 마무리해 나머지 경우를 명시 처리하거나, 최소한 도달하면 안 되는 경우임을 단언(assert)한다.',
  'why_en':'Rationale: terminating an if-else if chain with a final else ensures that the "all other cases" not matching any prior condition is handled explicitly in one place. Impact: without a closing else, unexpected input silently falls through taking no branch, so state updates or validation are missed, hiding defects and dropping handling when new values are added. Fix: terminate every if-else if chain with an else that handles the remaining cases, or at least assert that the case should be unreachable.'},

 {'id':'M6-4-3','cat':'Required · Automated','compiles':True,
  'title':'switch 문은 잘 정의된 형태(각 절 break, default 포함)를 따른다',
  'title_en':'A switch statement shall be a well-formed switch statement',
  'bad': r"""#include <iostream>
static void run(int x) {
    switch (x) {
        case 1: std::cout << "one ";   // break 누락 → case 2 로 흘러내림(fall-through)
        case 2: std::cout << "two\n"; break;
        // default 없음
    }
}
int main() { run(1); }   // "one two" 출력 — 의도치 않은 fall-through""",
  'good': r"""#include <iostream>
static void run(int x) {
    switch (x) {
        case 1: std::cout << "one\n"; break;
        case 2: std::cout << "two\n"; break;
        default: std::cout << "other\n"; break;
    }
}
int main() { run(1); }   // "one" 만 출력""",
  'why':'근거: switch 의 각 case 절은 break(또는 return·throw, 의도된 fall-through 는 명시 표시)로 끝나야 하고 default 절을 두어야 잘 정의된 형태가 된다. 영향: break 를 빠뜨리면 다음 case 로 의도치 않게 흘러내려(fall-through) 여러 분기가 실행되는 흔한 버그가 생기고, default 가 없으면 예상 못한 값이 조용히 무시된다. 대응: 각 절을 break 등으로 종료하고, 의도된 fall-through 는 [[fallthrough]] 로 표시하며, default 절을 두어 나머지 값을 처리한다.',
  'why_en':'Rationale: each case label in a switch must end with break (or return/throw, with intended fall-through explicitly marked) and a default label must be present for it to be well-formed. Impact: omitting break falls through to the next case unintentionally, executing multiple branches — a common bug — and a missing default silently ignores unexpected values. Fix: terminate each label with break or similar, mark intended fall-through with [[fallthrough]], and include a default to handle the remaining values.'},

 {'id':'M6-4-6','cat':'Required · Automated','compiles':True,
  'title':'switch 의 default 절은 마지막에 둔다',
  'title_en':'The final clause of a switch statement shall be the default-clause',
  'bad': r"""#include <iostream>
static void run(int x) {
    switch (x) {
        default: std::cout << "other\n"; break;   // default 가 중간/처음에 위치 — 가독성 저하
        case 1:  std::cout << "one\n";  break;
        case 2:  std::cout << "two\n";  break;
    }
}
int main() { run(2); }""",
  'good': r"""#include <iostream>
static void run(int x) {
    switch (x) {
        case 1:  std::cout << "one\n";  break;
        case 2:  std::cout << "two\n";  break;
        default: std::cout << "other\n"; break;   // 마지막에 위치 — 관례적, 읽기 쉬움
    }
}
int main() { run(2); }""",
  'why':'근거: default 절을 switch 의 맨 마지막에 두는 것은 널리 통용되는 관례로, 모든 명시적 case 를 먼저 보고 그 외 처리를 마지막에서 확인하는 자연스러운 읽기 순서를 만든다. 영향: default 가 case 들 사이나 앞에 끼면 흐름을 오해하기 쉽고, 위에서 아래로 훑는 독자가 default 를 일반 case 로 착각하거나 fall-through 관계를 잘못 읽을 수 있다. 대응: default 절을 항상 switch 의 마지막에 배치한다.',
  'why_en':'Rationale: placing the default clause last in a switch is a widely followed convention that creates a natural reading order — all explicit cases first, then the catch-all handling at the end. Impact: a default wedged between or before cases is easy to misread, and a reader scanning top to bottom may mistake default for an ordinary case or misread the fall-through relationships. Fix: always place the default clause last in the switch.'},

 {'id':'M6-6-1','cat':'Required · Automated','compiles':True,
  'title':'비구조적 점프(goto 등)를 사용하지 않는다',
  'title_en':'Any label referenced by a goto statement shall be declared in the same block, or in a block enclosing the goto statement',
  'bad': r"""#include <iostream>
int main() {
    int attempts = 0;
retry:                       // 임의 점프 대상 — 비구조적 흐름
    ++attempts;
    if (attempts < 3) goto retry;
    std::cout << "attempts=" << attempts << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int attempts = 0;
    while (attempts < 3) { ++attempts; }   // 구조적 반복으로 의도를 명확히
    std::cout << "attempts=" << attempts << '\n';
}""",
  'why':'근거: goto 는 함수 안 임의 라벨로 제어를 옮겨 위→아래로 읽는 구조적 흐름을 깨뜨리고, 점프 방향(앞/뒤)에 따라 반복·분기·예외 처리가 뒤섞일 수 있다. 영향: 비구조적 점프는 제어 흐름 그래프를 복잡하게 만들어 정적 분석과 사람의 추론을 어렵게 하고, 객체 초기화·정리를 건너뛰는 점프는 미묘한 자원 결함을 부른다. 대응: 반복은 while/for, 조기 종료는 break/continue/return, 정리는 RAII 같은 구조적 제어로 대체한다.',
  'why_en':'Rationale: goto transfers control to an arbitrary label in a function, breaking the top-to-bottom structured flow, and depending on jump direction (forward/backward) it can entangle loops, branches, and exception handling. Impact: non-structured jumps complicate the control-flow graph, hindering static analysis and human reasoning, and jumps that skip object initialization or cleanup invite subtle resource defects. Fix: replace with structured control — while/for for loops, break/continue/return for early exit, and RAII for cleanup.'},

 {'id':'M7-1-2','cat':'Required · Automated','compiles':True,
  'title':'수정되지 않는 포인터/참조 매개변수는 const 를 가리키게 한다',
  'title_en':'A pointer or reference parameter in a function shall be declared as pointing to const if the corresponding object is not modified',
  'bad': r"""#include <iostream>
#include <cstddef>
static std::size_t length(char* s) {   // s 내용을 수정하지 않는데 비-const
    std::size_t n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
int main() {
    char buf[] = "hello";
    std::cout << length(buf) << '\n';
    // length("literal");  // const 리터럴을 넘길 수 없어 컴파일 에러
}""",
  'good': r"""#include <iostream>
#include <cstddef>
static std::size_t length(const char* s) {   // 읽기 전용 의도를 const 로 표현
    std::size_t n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
int main() {
    std::cout << length("literal") << '\n';   // const 객체도 자유롭게 전달 가능
}""",
  'why':'근거: 함수가 포인터·참조로 받은 객체를 수정하지 않는다면 그 매개변수를 const 를 가리키게 선언함으로써, 읽기 전용이라는 계약을 인터페이스에 드러내고 컴파일러가 우발적 수정을 막게 한다. 영향: 비-const 로 두면 const 객체(문자열 리터럴·const 변수)를 인자로 넘길 수 없어 호출이 제한되고, 독자는 함수가 대상을 바꿀 수 있다고 오해해 불필요한 방어 코드를 넣는다. 대응: 수정하지 않는 모든 포인터·참조 매개변수를 const 를 가리키도록 선언한다.',
  'why_en':'Rationale: if a function does not modify the object received by pointer or reference, declaring that parameter as pointing to const expresses the read-only contract in the interface and lets the compiler prevent accidental modification. Impact: leaving it non-const prevents passing const objects (string literals, const variables) as arguments, restricting calls, and leads readers to assume the function may change the target and add unnecessary defensive code. Fix: declare every pointer or reference parameter that is not modified as pointing to const.'},

 {'id':'M7-3-6','cat':'Required · Automated','compiles':True,
  'title':'헤더(또는 넓은 범위)에서 using 지시문으로 이름을 도입하지 않는다',
  'title_en':'using-directives and using-declarations shall not be used in header files',
  'bad': r"""#include <iostream>
using namespace std;   // 넓은 범위에 std 전체 도입 — 이름 충돌·모호성 위험
static int count(int) { return 1; }   // std::count 와 이름이 겹칠 소지
int main() { cout << count(0) << "\n"; }""",
  'good': r"""#include <iostream>
static int count_items(int) { return 1; }   // 완전 한정 이름 + 고유 이름
int main() { std::cout << count_items(0) << "\n"; }""",
  'why':'근거: using namespace 지시문은 대상 네임스페이스의 모든 이름을 현재 범위로 끌어들이는데, 이를 헤더나 넓은 범위에 두면 그 헤더를 포함하는 모든 번역단위가 의도치 않게 오염된다. 영향: 사용자 이름과 표준 라이브러리 이름(count, distance 등)이 겹쳐 모호성 오류가 나거나, 오버로드 해석이 예상 밖 함수를 골라 조용한 버그가 되며, 충돌은 포함 순서에 따라 산발적으로 나타난다. 대응: 헤더에서는 완전 한정 이름(std::)을 쓰고, using 은 함수·블록 같은 좁은 범위에 한정해 필요한 이름만 도입한다.',
  'why_en':'Rationale: a using namespace directive pulls every name of the target namespace into the current scope, and placing it in a header or broad scope unintentionally pollutes every translation unit that includes the header. Impact: user names clash with standard-library names (count, distance), causing ambiguity errors or silent bugs where overload resolution picks an unexpected function, and conflicts appear sporadically by include order. Fix: use fully qualified names (std::) in headers and confine using to narrow scopes like functions or blocks, importing only the needed names.'},

 {'id':'M7-5-1','cat':'Required · Automated','compiles':True,
  'title':'함수는 자동(지역) 객체에 대한 참조/포인터를 반환하지 않는다',
  'title_en':'A function shall not return a reference or a pointer to an automatic variable',
  'bad': r"""#include <iostream>
#include <string>
static const std::string& name() {
    std::string s = "node";   // 자동(지역) 객체
    return s;                  // 함수 종료 시 소멸되는 객체의 참조 반환 — 댕글링
}
int main() { std::cout << name() << '\n'; }   // 무효 참조 접근 — 미정의 동작""",
  'good': r"""#include <iostream>
#include <string>
static std::string name() {
    return std::string{"node"};   // 값으로 반환(이동/RVO)
}
int main() { std::cout << name() << '\n'; }""",
  'why':'근거: 함수의 자동(지역) 변수는 함수가 반환하는 순간 수명이 끝나므로, 그 변수에 대한 참조나 주소를 반환하면 호출자는 이미 소멸한 객체를 가리키게 된다. 영향: 호출자가 그 댕글링 참조·포인터를 사용하면 해제된 스택 메모리를 읽어 쓰레기 값·크래시가 나고, 입력에 따라 동작이 달라지는 보안 취약점이 된다. 대응: 필요한 값은 값으로 반환하거나(이동·RVO 로 효율적), 수명이 호출자보다 긴 객체(멤버·정적·힙 소유)를 가리키게 한다.',
  'why_en':'Rationale: a function automatic (local) variable ends its lifetime the moment the function returns, so returning a reference or address to it makes the caller point at an already-destroyed object. Impact: using that dangling reference or pointer reads freed stack memory, yielding garbage or crashes, and becomes a security vulnerability whose behaviour varies with input. Fix: return needed values by value (efficient via move/RVO) or point to objects that outlive the caller (member, static, or heap-owned).'},

 {'id':'M8-4-2','cat':'Required · Automated','compiles':True,
  'title':'함수 선언과 정의의 매개변수 이름을 일치시킨다',
  'title_en':'The identifiers used in the declaration and definition of a function shall be identical',
  'bad': r"""#include <iostream>
#include <cstring>
static void copy_n(char* dst, const char* src, std::size_t n);   // 선언: dst, src
static void copy_n(char* a, const char* b, std::size_t n) {       // 정의: a, b — 이름 불일치
    std::memcpy(a, b, n);
}
int main() { char d[4]; copy_n(d, "abc", 4); std::cout << d << '\n'; }""",
  'good': r"""#include <iostream>
#include <cstring>
static void copy_n(char* dst, const char* src, std::size_t n);   // 선언
static void copy_n(char* dst, const char* src, std::size_t n) {   // 정의 — 동일 이름
    std::memcpy(dst, src, n);
}
int main() { char d[4]; copy_n(d, "abc", 4); std::cout << d << '\n'; }""",
  'why':'근거: 함수 선언(헤더)과 정의(소스)의 매개변수 이름이 같으면, 헤더만 보는 호출자와 정의를 보는 구현자가 같은 어휘로 각 인자의 의미를 이해한다. 영향: 이름이 다르면(dst/src 대 a/b) 인자 순서·역할을 헷갈려 dst 와 src 를 바꿔 호출하는 등의 실수를 부르고, 검토·디버깅 시 두 위치를 대조하기 어렵다. 대응: 선언과 정의에서 매개변수 이름을 동일하게 맞춰 인터페이스 문서성과 일관성을 유지한다.',
  'why_en':'Rationale: when the parameter names in a function declaration (header) and definition (source) match, callers who see only the header and implementers who see the definition understand each argument with the same vocabulary. Impact: differing names (dst/src vs a/b) confuse argument order and roles, inviting mistakes like swapping dst and src in a call, and make it hard to cross-reference the two locations during review and debugging. Fix: keep parameter names identical in the declaration and definition to preserve interface documentation and consistency.'},

 {'id':'M8-5-1','cat':'Required · Automated','compiles':True,
  'title':'모든 변수는 사용되기 전에 정의된 값을 가져야 한다',
  'title_en':'All variables shall have a defined value before they are used',
  'bad': r"""#include <iostream>
int main() {
    int total;   // 초기화 누락
    int a[3] = {1, 2, 3};
    for (int i = 0; i < 3; ++i) total += a[i];   // 미초기화 total 에 누적 — 미정의 동작
    std::cout << total << '\n';   // 쓰레기 값에 6 을 더한 결과
}""",
  'good': r"""#include <iostream>
int main() {
    int total = 0;   // 사용 전에 명확히 초기화
    int a[3] = {1, 2, 3};
    for (int i = 0; i < 3; ++i) total += a[i];
    std::cout << total << '\n';   // 6
}""",
  'why':'근거: 자동 저장 기간의 기본 타입 변수는 명시적으로 초기화하지 않으면 불확정 값을 가지며, 그 값을 읽는 것은 미정의 동작이다. 영향: 미초기화 누적 변수(total)에 값을 더하면 쓰레기 초기값 위에 계산이 쌓여 결과가 매 실행·빌드마다 달라지는 재현 어려운 버그가 되고, 보안상 이전 스택 내용이 노출될 수 있다. 대응: 모든 변수를 선언과 동시에(또는 첫 사용 이전에) 명확한 값으로 초기화하고, 컴파일러 경고(-Wuninitialized)와 정적 분석을 활용한다.',
  'why_en':'Rationale: a fundamental-type variable with automatic storage has an indeterminate value unless explicitly initialized, and reading that value is undefined behaviour. Impact: adding to an uninitialized accumulator (total) stacks the computation on a garbage initial value, producing a hard-to-reproduce bug that differs per run or build, and may expose prior stack contents as a security issue. Fix: initialize every variable to a defined value at declaration (or before first use) and rely on compiler warnings (-Wuninitialized) and static analysis.'},

 {'id':'M9-3-1','cat':'Required · Automated','compiles':True,
  'title':'const 멤버 함수가 내부 데이터에 대한 비-const 핸들을 반환하지 않게 한다',
  'title_en':'const member functions shall not return non-const pointers or references to class-data',
  'bad': r"""#include <iostream>
class C {
    int data_ = 7;
public:
    int* get() const { return const_cast<int*>(&data_); }   // const 함수가 수정 핸들 노출
};
int main() {
    const C c;
    *c.get() = 99;   // const 객체의 내부를 수정 — const 계약 위반
    std::cout << *c.get() << '\n';
}""",
  'good': r"""#include <iostream>
class C {
    int data_ = 7;
public:
    const int* get() const { return &data_; }   // const 함수는 const 핸들만 반환
    void set(int v) { data_ = v; }              // 변경은 비-const 메서드로
};
int main() {
    C c; c.set(99);
    std::cout << *c.get() << '\n';   // 99 — 읽기는 const 핸들로
}""",
  'why':'근거: const 멤버 함수는 그 객체의 논리적 상태를 바꾸지 않겠다는 계약이며, 그 일부로 내부 데이터에 대한 수정 가능한 핸들을 외부에 넘기지 않아야 한다. 영향: const 함수가 비-const 포인터·참조를 반환하면 const 객체를 통해서도 내부가 수정될 수 있어 const 보장이 무너지고, const_cast 로 const 를 벗긴 경우 진짜 const 객체 수정으로 미정의 동작까지 갈 수 있다. 대응: const 멤버 함수는 const 포인터·참조만 반환하고, 수정이 필요한 접근은 별도의 비-const 멤버 함수로 제공한다.',
  'why_en':'Rationale: a const member function is a contract not to change the logical state of the object, and as part of that it must not hand out a modifiable handle to internal data. Impact: a const function returning a non-const pointer or reference lets the internals be modified even through a const object, breaking the const guarantee, and casting away const can escalate to modifying a truly const object — undefined behaviour. Fix: have const member functions return only const pointers/references and provide a separate non-const member function for accesses that need modification.'},

 {'id':'M9-3-3','cat':'Required · Automated','compiles':True,
  'title':'상태를 바꾸지 않는 멤버 함수는 const 로 선언한다',
  'title_en':'If a member function can be made static then it shall be made static, otherwise if it can be made const then it shall be made const',
  'bad': r"""#include <iostream>
class C {
    int v_ = 42;
public:
    int value() { return v_; }   // 상태를 바꾸지 않는데 비-const
};
int main() {
    const C c;
    // std::cout << c.value();  // const 객체에서 비-const 함수 호출 불가 — 컴파일 에러
    C m; std::cout << m.value() << '\n';
}""",
  'good': r"""#include <iostream>
class C {
    int v_ = 42;
public:
    int value() const { return v_; }   // 상태 불변임을 const 로 명시
};
int main() {
    const C c;
    std::cout << c.value() << '\n';   // const 객체에서도 호출 가능
}""",
  'why':'근거: 객체의 논리적 상태를 변경하지 않는 멤버 함수를 const 로 선언하면, 그 불변성이 인터페이스에 드러나고 const 객체에서도 호출할 수 있게 된다(멤버를 전혀 쓰지 않으면 static 이 더 적절하다). 영향: const 로 표시하지 않으면 const 객체·const 참조를 통해 그 함수를 호출할 수 없어 사용이 제한되고, 함수가 상태를 바꿀 수 있다고 독자가 오해한다. 대응: 상태를 바꾸지 않는 관찰자(getter·조회) 함수는 const 로, 인스턴스 데이터를 쓰지 않는 함수는 static 으로 선언한다.',
  'why_en':'Rationale: declaring a member function that does not change the logical state of the object as const makes that immutability visible in the interface and allows calling it on const objects (and if it uses no members at all, static is more appropriate). Impact: not marking it const prevents calling the function through const objects or const references, restricting use, and leads readers to assume the function may change state. Fix: declare observer (getter/query) functions that do not change state as const, and functions that use no instance data as static.'},

 {'id':'M9-5-1','cat':'Required · Automated','compiles':True,
  'title':'union 을 사용하지 않는다(타입 퍼닝 금지)',
  'title_en':'Unions shall not be used',
  'bad': r"""#include <iostream>
union U { int i; float f; };
int main() {
    U u; u.i = 1065353216;   // i 를 활성화
    std::cout << u.f << '\n';  // 비활성 멤버 f 로 읽기(타입 퍼닝) — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <variant>
int main() {
    std::variant<int, float> u = 1.0f;   // 활성 타입을 스스로 추적
    if (std::holds_alternative<float>(u))
        std::cout << std::get<float>(u) << '\n';   // 잘못된 타입 접근은 예외
}""",
  'why':'근거: union 의 모든 멤버는 같은 메모리를 공유하지만, 한 멤버에 쓴 뒤 다른(비활성) 멤버로 읽는 타입 퍼닝(type punning)은 표준상 미정의 동작이고, union 은 현재 활성 멤버를 스스로 추적하지 않는다. 영향: 활성 멤버를 잘못 추적하면 쓰레기 값을 읽거나, 비trivial 타입을 담으면 생성·소멸 관리가 복잡해져 누수·손상이 발생하는데 컴파일러가 막아주지 못한다. 대응: 합집합이 필요하면 활성 타입을 추적하고 잘못된 접근을 예외로 막는 std::variant 를, 비트 재해석이 목적이면 std::memcpy/std::bit_cast 를 사용한다.',
  'why_en':'Rationale: all members of a union share the same memory, but writing one member and reading another (inactive) member — type punning — is undefined behaviour in the standard, and a union does not track its currently active member itself. Impact: mistracking the active member reads garbage, and holding non-trivial types complicates construction/destruction, causing leaks or corruption that the compiler cannot prevent. Fix: use std::variant when a union is needed (it tracks the active type and blocks wrong accesses with an exception), and std::memcpy/std::bit_cast when bitwise reinterpretation is the goal.'},
]
