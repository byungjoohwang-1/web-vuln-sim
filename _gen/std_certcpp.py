# -*- coding: utf-8 -*-
"""SEI CERT C++ 대표 규칙 — 위반/준수 예제 (사내 교육용, 규범 원문 비복제·자체 작성)"""
RULES = [
 {'id':'DCL50-CPP','cat':'DCL · Rule · L1',
  'title':'C 스타일 가변인자 함수를 정의하지 않는다',
  'bad': r"""#include <cstdarg>
// C 스타일 가변인자: 타입 안전성이 전혀 없다
double avg(int count, ...) {
    va_list ap;
    va_start(ap, count);
    double sum = 0;
    for (int i = 0; i < count; ++i)
        sum += va_arg(ap, double); // 실제 인자가 int면 UB
    va_end(ap);
    return sum / count;
}""",
  'good': r"""#include <initializer_list>
// 가변 템플릿/initializer_list로 타입 안전하게 처리
double avg(std::initializer_list<double> values) {
    double sum = 0;
    for (double v : values)
        sum += v;
    return sum / values.size();
}
// 호출: avg({1.0, 2.0, 3.0});""",
  'why':'C 스타일 가변인자는 컴파일러가 인자 타입을 검사하지 못해 잘못된 타입 전달 시 미정의 동작을 일으킨다. 가변 템플릿이나 initializer_list로 타입 안전하게 대체한다.'},

 {'id':'DCL58-CPP','cat':'DCL · Rule · L1',
  'title':'표준 네임스페이스(std)를 수정하지 않는다',
  'bad': r"""#include <utility>
// std 네임스페이스에 사용자 선언을 추가하는 것은 금지
namespace std {
    template <typename T>
    void swap(MyType<T>& a, MyType<T>& b) { /* ... */ }
}""",
  'good': r"""#include <utility>
namespace mylib {
    template <typename T> struct MyType { /* ... */ };
    // 자신의 네임스페이스에 swap을 두고 ADL로 찾게 한다
    template <typename T>
    void swap(MyType<T>& a, MyType<T>& b) noexcept { a.swap(b); }
}""",
  'why':'표준 네임스페이스에 임의 선언/정의를 추가하면(허용된 특수화 예외 제외) 미정의 동작이다. 사용자 타입 연산은 자신의 네임스페이스에 두고 ADL로 해결한다.'},

 {'id':'DCL59-CPP','cat':'DCL · Rule · L2',
  'title':'헤더에 익명 네임스페이스를 정의하지 않는다',
  'bad': r"""// util.h
namespace {
    int counter = 0;          // 헤더에 포함될 때마다 별도 인스턴스 생성
    inline void tick() { ++counter; }
}""",
  'good': r"""// util.h
namespace mylib {
    void tick();              // 선언만 헤더에 둔다
}
// util.cpp
namespace mylib {
    namespace { int counter = 0; }
    void tick() { ++counter; }
}""",
  'why':'헤더의 익명 네임스페이스는 이를 포함하는 번역 단위마다 독립 엔티티를 만들어 ODR 혼란과 의도치 않은 중복 상태를 유발한다. 익명 네임스페이스는 소스 파일에만 둔다.'},

 {'id':'EXP50-CPP','cat':'EXP · Rule · L1',
  'title':'평가 순서에 의존하지 않는다',
  'bad': r"""int i = 0;
int arr[3] = {0};
// 한 식 안에서 i를 읽고 쓰는 순서가 비결정적이다
arr[i] = i++;          // 미정의 동작
int x = f(i) + g(i++); // f,g 평가 순서 미정의""",
  'good': r"""int i = 0;
int arr[3] = {0};
arr[i] = i;            // 부수효과를 분리
++i;
int a = f(i);
++i;
int x = a + g(i);      // 순서를 명시적으로 고정""",
  'why':'동일 식 안에서 같은 객체를 수정하면서 읽거나, 순서 미보장 함수 호출에 부수효과를 섞으면 미정의 동작이 된다. 부수효과를 별도 문장으로 분리해 순서를 명확히 한다.'},

 {'id':'EXP51-CPP','cat':'EXP · Rule · L1',
  'title':'기반 클래스 포인터로 배열을 delete하지 않는다',
  'bad': r"""struct Base { virtual ~Base() {} };
struct Derived : Base { int extra; };

void f() {
    Base* p = new Derived[10]; // 포인터 산술이 Base 크기 기준
    delete[] p;                // 미정의 동작
}""",
  'good': r"""#include <vector>
#include <memory>
struct Base { virtual ~Base() {} };
struct Derived : Base { int extra; };

void f() {
    std::vector<std::unique_ptr<Base>> v;
    for (int i = 0; i < 10; ++i)
        v.push_back(std::make_unique<Derived>());
} // 컨테이너가 정확한 타입으로 해제""",
  'why':'파생 타입 배열을 기반 포인터로 delete[]하면 요소 크기가 달라 포인터 산술과 소멸자 호출이 어긋나 미정의 동작이 된다. 다형 객체 컬렉션은 스마트 포인터 컨테이너로 관리한다.'},

 {'id':'EXP53-CPP','cat':'EXP · Rule · L1',
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'bad': r"""int compute() {
    int sum;            // 미초기화
    for (int i = 0; i < 10; ++i)
        sum += i;       // sum의 초기값이 불확정 → UB
    return sum;
}""",
  'good': r"""int compute() {
    int sum = 0;        // 명시적 초기화
    for (int i = 0; i < 10; ++i)
        sum += i;
    return sum;
}""",
  'why':'초기화되지 않은 자동 변수의 값은 불확정이며 이를 읽으면 미정의 동작이다. 선언 시점에 항상 명시적으로 초기화한다.'},

 {'id':'EXP54-CPP','cat':'EXP · Rule · L1',
  'title':'수명이 끝난 객체에 접근하지 않는다',
  'bad': r"""const int& dangling() {
    int local = 42;
    return local;       // 지역 변수 참조 반환
}                       // local 소멸 → 댕글링 참조

void use() { int v = dangling(); /* UB */ }""",
  'good': r"""int byValue() {
    int local = 42;
    return local;       // 값으로 복사 반환
}

void use() { int v = byValue(); }""",
  'why':'수명이 종료된 지역 객체에 대한 참조/포인터를 반환해 접근하면 미정의 동작이다. 값으로 반환하거나 호출자가 소유권을 명확히 갖는 객체를 사용한다.'},

 {'id':'EXP55-CPP','cat':'EXP · Rule · L2',
  'title':'const 한정자를 우회해 객체를 수정하지 않는다',
  'bad': r"""void f(const int* p) {
    int* q = const_cast<int*>(p);
    *q = 99;            // 원본이 진짜 const면 UB
}
const int ci = 10;
// f(&ci);""",
  'good': r"""void f(int* p) {      // 수정이 필요하면 비const로 받는다
    *p = 99;
}
int value = 10;
// f(&value);
// 진짜 const 객체는 절대 수정하지 않는다""",
  'why':'원래 const로 정의된 객체를 const_cast로 벗겨 수정하면 미정의 동작이다. 수정이 필요한 인터페이스는 처음부터 비const 타입으로 설계한다.'},

 {'id':'EXP57-CPP','cat':'EXP · Rule · L2',
  'title':'다형 타입 포인터에 부적절한 캐스트를 적용하지 않는다',
  'bad': r"""struct Base { virtual ~Base() {} };
struct Derived : Base { void g(); };

void f(Base* b) {
    Derived* d = (Derived*)b; // C 스타일 강제 캐스트, 검사 없음
    d->g();                   // b가 Derived가 아니면 UB
}""",
  'good': r"""struct Base { virtual ~Base() {} };
struct Derived : Base { void g(); };

void f(Base* b) {
    if (auto* d = dynamic_cast<Derived*>(b)) {
        d->g();               // 런타임 타입 확인 후 사용
    }
}""",
  'why':'다형 객체를 잘못된 파생 타입으로 강제 캐스트해 접근하면 미정의 동작이다. dynamic_cast로 실제 타입을 확인한 뒤에만 파생 멤버에 접근한다.'},

 {'id':'EXP63-CPP','cat':'EXP · Rule · L2',
  'title':'moved-from 객체의 값에 의존하지 않는다',
  'bad': r"""#include <string>
#include <utility>
void f() {
    std::string a = "data";
    std::string b = std::move(a);
    size_t n = a.size();   // moved-from 상태 값에 의존 (미지정)
    char c = a[0];         // 위험
}""",
  'good': r"""#include <string>
#include <utility>
void f() {
    std::string a = "data";
    std::string b = std::move(a);
    a = "reset";           // 사용 전 재대입(유효 상태 복구)
    size_t n = a.size();   // 안전
}""",
  'why':'이동된(moved-from) 객체는 유효하지만 미지정 상태이므로 그 구체적 값에 의존하면 안 된다. 다시 대입하거나 clear() 같은 무조건 연산으로 상태를 재설정한 뒤 사용한다.'},

 {'id':'INT50-CPP','cat':'INT · Rule · L1',
  'title':'열거형 범위 밖 값으로 캐스트하지 않는다',
  'bad': r"""enum class Color { Red, Green, Blue }; // 0..2

Color from(int v) {
    return static_cast<Color>(v); // v=99면 표현 불가 값 → UB 위험
}""",
  'good': r"""enum class Color { Red, Green, Blue };

Color from(int v) {
    if (v < 0 || v > 2)
        throw std::out_of_range("invalid Color");
    return static_cast<Color>(v); // 범위 검증 후 캐스트
}""",
  'why':'열거형이 표현할 수 없는 정수 값을 그 열거형으로 캐스트하면 미정의 동작이 될 수 있다. 캐스트 전에 유효 범위를 검증한다.'},

 {'id':'CTR50-CPP','cat':'CTR · Rule · L1',
  'title':'컨테이너 인덱스/반복자가 범위 안에 있도록 보장한다',
  'bad': r"""#include <vector>
int get(const std::vector<int>& v, size_t i) {
    return v[i];        // 경계 검사 없음 → 범위 초과 시 UB
}""",
  'good': r"""#include <vector>
#include <stdexcept>
int get(const std::vector<int>& v, size_t i) {
    if (i >= v.size())
        throw std::out_of_range("index");
    return v[i];        // 또는 v.at(i) 사용
}""",
  'why':'operator[]는 경계를 검사하지 않아 범위를 벗어난 접근은 미정의 동작이다. 인덱스를 명시적으로 검증하거나 at()처럼 검사하는 인터페이스를 사용한다.'},

 {'id':'CTR53-CPP','cat':'CTR · Rule · L1',
  'title':'유효한 반복자 범위만 사용한다',
  'bad': r"""#include <vector>
#include <numeric>
int sum(std::vector<int>& a, std::vector<int>& b) {
    // 서로 다른 컨테이너의 반복자를 섞은 범위 → UB
    return std::accumulate(a.begin(), b.end(), 0);
}""",
  'good': r"""#include <vector>
#include <numeric>
int sum(std::vector<int>& a) {
    return std::accumulate(a.begin(), a.end(), 0); // 동일 컨테이너
}""",
  'why':'[first, last) 범위는 같은 컨테이너에 속하고 first가 last에 도달 가능해야 한다. 서로 다른 컨테이너의 반복자나 역순 범위를 알고리즘에 넘기면 미정의 동작이다.'},

 {'id':'CTR55-CPP','cat':'CTR · Rule · L2',
  'title':'반복자 가산 시 오버플로를 일으키지 않는다',
  'bad': r"""#include <vector>
void f(std::vector<int>& v, size_t n) {
    auto it = v.begin() + n; // n이 size보다 크면 범위 초과
    *it = 0;                 // UB
}""",
  'good': r"""#include <vector>
void f(std::vector<int>& v, size_t n) {
    if (n < v.size()) {
        auto it = v.begin() + n; // 검증된 오프셋만 사용
        *it = 0;
    }
}""",
  'why':'반복자에 컨테이너 크기를 넘는 오프셋을 더하면 end()를 지나쳐 유효하지 않은 반복자가 되어 역참조 시 미정의 동작이다. 오프셋이 크기 이내인지 먼저 확인한다.'},

 {'id':'CTR56-CPP','cat':'CTR · Rule · L2',
  'title':'다형 객체에 포인터 산술을 사용하지 않는다',
  'bad': r"""struct Base { virtual ~Base() {} };
struct Derived : Base { int extra; };
void f(Base* arr, int n) {
    for (int i = 0; i < n; ++i)
        (arr + i)->~Base(); // 실제 요소가 Derived면 보폭 불일치 → UB
}""",
  'good': r"""#include <vector>
#include <memory>
struct Base { virtual ~Base() {} };
struct Derived : Base { int extra; };
void f(std::vector<std::unique_ptr<Base>>& v) {
    v.clear();          // 컨테이너가 올바른 타입으로 정리
}""",
  'why':'기반 타입 포인터로 파생 객체 배열을 산술 순회하면 요소 크기가 달라 잘못된 주소를 가리켜 미정의 동작이 된다. 다형 컬렉션은 포인터 배열/스마트 포인터 컨테이너로 다룬다.'},

 {'id':'STR50-CPP','cat':'STR · Rule · L1',
  'title':'문자열 데이터에 충분한 저장 공간을 보장한다',
  'bad': r"""#include <cstring>
void f(const char* src) {
    char dst[8];
    std::strcpy(dst, src); // src가 8바이트 이상이면 버퍼 오버플로
}""",
  'good': r"""#include <string>
void f(const char* src) {
    std::string dst = src;  // 필요한 만큼 자동 할당
    // 고정 버퍼가 필수면 길이 검사 후 strncpy/snprintf 사용
}""",
  'why':'널 종료를 포함한 전체 길이를 담지 못하는 버퍼에 문자열을 복사하면 버퍼 오버플로가 발생한다. std::string으로 동적 관리하거나 대상 크기를 검사한다.'},

 {'id':'STR51-CPP','cat':'STR · Rule · L1',
  'title':'std::string의 유효하지 않은 포인터를 사용하지 않는다',
  'bad': r"""#include <string>
#include <cstdio>
const char* danger() {
    std::string s = "temp";
    return s.c_str();   // 함수 종료 시 s 소멸 → 댕글링 포인터
}""",
  'good': r"""#include <string>
std::string safe() {
    std::string s = "temp";
    return s;           // 문자열 객체 자체를 반환
}""",
  'why':'c_str()/data()가 돌려주는 포인터는 원본 string의 수명과 (비)변경 여부에 묶여 있어, 객체가 소멸하거나 변경되면 무효가 된다. 문자열 객체 자체를 보존·반환한다.'},

 {'id':'MEM50-CPP','cat':'MEM · Rule · L1',
  'title':'해제된 메모리에 접근하지 않는다',
  'bad': r"""void f() {
    int* p = new int(42);
    delete p;
    *p = 7;             // 해제 후 사용(use-after-free)
}""",
  'good': r"""#include <memory>
void f() {
    auto p = std::make_unique<int>(42);
    *p = 7;             // RAII가 수명을 관리, 해제 후 접근 불가
}""",
  'why':'delete 후의 포인터를 역참조하면 use-after-free로 미정의 동작이자 보안 취약점이다. 스마트 포인터(RAII)로 수명을 자동 관리해 해제 후 접근을 구조적으로 차단한다.'},

 {'id':'MEM51-CPP','cat':'MEM · Rule · L1',
  'title':'올바른 형식으로 동적 메모리를 해제한다',
  'bad': r"""void f() {
    int* arr = new int[10];
    delete arr;         // new[]에는 delete[]를 써야 한다 → UB
}""",
  'good': r"""#include <vector>
void f() {
    std::vector<int> arr(10); // 할당/해제 형식 불일치 자체가 사라짐
}""",
  'why':'new[]는 delete[]와, new는 delete와, malloc은 free와 정확히 짝지어야 하며 불일치 시 미정의 동작이다. 컨테이너/스마트 포인터를 쓰면 형식 불일치 위험이 제거된다.'},

 {'id':'MEM53-CPP','cat':'MEM · Rule · L2',
  'title':'수동 수명 관리 시 생성과 소멸을 명시적으로 호출한다',
  'bad': r"""#include <cstdlib>
struct Widget { Widget(); ~Widget(); };
void f() {
    void* mem = std::malloc(sizeof(Widget));
    Widget* w = static_cast<Widget*>(mem); // 생성자 미호출
    // w 사용 → 미초기화 객체
    std::free(mem);     // 소멸자 미호출
}""",
  'good': r"""#include <memory>
struct Widget { Widget(); ~Widget(); };
void f() {
    void* mem = ::operator new(sizeof(Widget));
    Widget* w = new (mem) Widget();  // placement new로 생성
    w->~Widget();                    // 명시적 소멸
    ::operator delete(mem);
}""",
  'why':'생성자를 호출하지 않은 raw 메모리를 객체처럼 쓰거나 소멸자 없이 해제하면 미정의 동작/리소스 누수가 된다. placement new와 명시적 소멸자 호출로 수명을 정확히 관리한다.'},

 {'id':'MEM54-CPP','cat':'MEM · Rule · L2',
  'title':'할당 메모리가 타입의 정렬 요건을 만족하게 한다',
  'bad': r"""#include <cstdlib>
struct alignas(16) Vec4 { float v[4]; };
void f() {
    void* p = std::malloc(sizeof(Vec4)); // 16바이트 정렬 보장 없음
    Vec4* q = new (p) Vec4();             // 정렬 위반 시 UB
}""",
  'good': r"""#include <new>
struct alignas(16) Vec4 { float v[4]; };
void f() {
    void* p = ::operator new(sizeof(Vec4), std::align_val_t{16});
    Vec4* q = new (p) Vec4();             // 정렬된 메모리에 생성
    q->~Vec4();
    ::operator delete(p, std::align_val_t{16});
}""",
  'why':'타입의 정렬 요건보다 약하게 정렬된 메모리에 객체를 생성/접근하면 미정의 동작이며 일부 플랫폼에서 충돌한다. 정렬을 보장하는 할당(aligned operator new 등)을 사용한다.'},

 {'id':'MEM56-CPP','cat':'MEM · Rule · L2',
  'title':'소유 포인터의 값을 무효한 상태로 보관하지 않는다',
  'bad': r"""#include <memory>
void f() {
    int* raw = new int(5);
    std::shared_ptr<int> a(raw);
    std::shared_ptr<int> b(raw); // 같은 raw로 두 소유권 → 이중 해제
}""",
  'good': r"""#include <memory>
void f() {
    auto a = std::make_shared<int>(5);
    std::shared_ptr<int> b = a;  // 참조 카운트 공유, 안전
}""",
  'why':'이미 스마트 포인터가 소유한 raw 포인터로 또 다른 소유 스마트 포인터를 만들면 이중 해제가 발생한다. make_shared/복사로 소유권을 공유하고 raw 포인터를 중복 보관하지 않는다.'},

 {'id':'OOP50-CPP','cat':'OOP · Rule · L1',
  'title':'생성자/소멸자에서 가상 함수를 동적 디스패치로 호출하지 않는다',
  'bad': r"""struct Base {
    Base() { init(); }            // 생성 중에는 파생 오버라이드 미적용
    virtual void init() { /* base */ }
};
struct Derived : Base {
    int* data;
    void init() override { *data = 0; } // data 아직 미초기화 → 위험
};""",
  'good': r"""struct Base {
    Base() = default;
    virtual void init() { /* base */ }
};
struct Derived : Base {
    int data = 0;
    Derived() { init(); }         // 객체가 완전히 구성된 뒤 호출
    void init() override { data = 0; }
};""",
  'why':'생성/소멸 중에는 동적 타입이 현재 클래스이므로 가상 호출이 파생 오버라이드로 디스패치되지 않아 의도와 다르게 동작한다. 초기화는 파생 객체 구성 완료 후 별도로 호출한다.'},

 {'id':'OOP51-CPP','cat':'OOP · Rule · L1',
  'title':'객체 슬라이싱이 일어나지 않게 한다',
  'bad': r"""#include <vector>
struct Base { virtual void f(); };
struct Derived : Base { int extra; void f() override; };
void g() {
    std::vector<Base> v;
    Derived d;
    v.push_back(d);     // Base 부분만 복사(슬라이싱) → 다형성 소실
}""",
  'good': r"""#include <vector>
#include <memory>
struct Base { virtual void f(); virtual ~Base() = default; };
struct Derived : Base { int extra; void f() override; };
void g() {
    std::vector<std::unique_ptr<Base>> v;
    v.push_back(std::make_unique<Derived>()); // 다형성 보존
}""",
  'why':'파생 객체를 기반 타입 값으로 복사하면 파생 부분이 잘려 나가(슬라이싱) 다형 동작을 잃는다. 다형 객체는 포인터/참조나 스마트 포인터로 다룬다.'},

 {'id':'OOP52-CPP','cat':'OOP · Rule · L1',
  'title':'다형적으로 삭제되는 기반 클래스에 가상 소멸자를 둔다',
  'bad': r"""struct Base { ~Base(); };          // 비가상 소멸자
struct Derived : Base { int* p; ~Derived(); };
void f() {
    Base* b = new Derived();
    delete b;           // Derived 소멸자 미호출 → 누수/UB
}""",
  'good': r"""struct Base { virtual ~Base() = default; };
struct Derived : Base { int* p; ~Derived() override; };
void f() {
    Base* b = new Derived();
    delete b;           // 올바르게 Derived 소멸자 호출
}""",
  'why':'기반 포인터로 파생 객체를 delete할 때 소멸자가 가상이 아니면 파생 소멸자가 호출되지 않아 리소스 누수와 미정의 동작이 생긴다. 다형 기반 클래스는 가상 소멸자를 선언한다.'},

 {'id':'OOP53-CPP','cat':'OOP · Rule · L2',
  'title':'멤버 초기화 순서를 선언 순서와 일치시킨다',
  'bad': r"""struct S {
    int b;
    int a;
    // 초기화는 선언 순서(b,a)대로 실행됨에 주의
    S(int x) : a(x), b(a + 1) {} // b가 a보다 먼저 초기화 → a 미정의
};""",
  'good': r"""struct S {
    int a;
    int b;
    S(int x) : a(x), b(a + 1) {} // 선언 순서와 초기화 순서 일치
};""",
  'why':'멤버는 초기화 리스트 작성 순서가 아니라 선언 순서대로 초기화되므로, 아직 초기화 안 된 멤버에 의존하면 불확정 값을 읽는다. 선언 순서와 의존 순서를 맞춘다.'},

 {'id':'OOP54-CPP','cat':'OOP · Rule · L2',
  'title':'자기 대입에 안전하게 대입 연산자를 구현한다',
  'bad': r"""struct Buf {
    int* data; size_t n;
    Buf& operator=(const Buf& o) {
        delete[] data;              // o가 자기 자신이면 data 파괴
        data = new int[o.n];        // 그 뒤 o.data 읽기 → UB
        std::copy(o.data, o.data + o.n, data);
        n = o.n; return *this;
    }
};""",
  'good': r"""#include <algorithm>
struct Buf {
    int* data; size_t n;
    Buf& operator=(Buf o) {         // copy-and-swap
        std::swap(data, o.data);
        std::swap(n, o.n);
        return *this;               // 자기 대입에도 안전
    }
};""",
  'why':'자기 대입(a = a) 시 먼저 자원을 해제하면 원본 데이터를 잃어 미정의 동작이 된다. copy-and-swap 관용구나 자기 대입 검사로 안전하게 구현한다.'},

 {'id':'OOP58-CPP','cat':'OOP · Rule · L2',
  'title':'복사 연산이 원본 객체를 변경하지 않게 한다',
  'bad': r"""struct Node {
    int* buf;
    Node(const Node& o) {           // 복사 생성자
        buf = o.buf;                // 얕은 복사
        const_cast<Node&>(o).buf = nullptr; // 원본을 망가뜨림
    }
};""",
  'good': r"""#include <algorithm>
struct Node {
    int* buf; size_t n;
    Node(const Node& o) : n(o.n) {  // 원본 불변
        buf = new int[o.n];
        std::copy(o.buf, o.buf + o.n, buf); // 깊은 복사
    }
};""",
  'why':'복사 생성/복사 대입은 원본을 읽기만 해야 하며 원본을 수정하면 호출자의 기대를 깨고 버그를 유발한다. 원본은 const로 취급하고 필요한 자원은 깊은 복사로 확보한다.'},

 {'id':'ERR50-CPP','cat':'ERR · Rule · L1',
  'title':'프로그램을 갑작스럽게 비정상 종료시키지 않는다',
  'bad': r"""#include <cstdlib>
void process(int code) {
    if (code != 0)
        std::abort();   // 스택 해제/정리 없이 즉시 종료
}""",
  'good': r"""#include <stdexcept>
void process(int code) {
    if (code != 0)
        throw std::runtime_error("processing failed"); // 정상 흐름
}""",
  'why':'abort/terminate 등으로 갑자기 종료하면 소멸자·정리 코드가 실행되지 않아 자원이 유실되고 데이터가 손상될 수 있다. 예외 등으로 제어된 오류 전파/정리 경로를 사용한다.'},

 {'id':'ERR51-CPP','cat':'ERR · Rule · L1',
  'title':'발생 가능한 모든 예외를 처리한다',
  'bad': r"""#include <vector>
int main() {
    std::vector<int> v;
    v.at(5);            // 예외 처리 없음 → 미처리 시 terminate
    return 0;
}""",
  'good': r"""#include <vector>
#include <iostream>
int main() {
    try {
        std::vector<int> v;
        v.at(5);
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << '\n';
        return 1;
    }
    return 0;
}""",
  'why':'처리되지 않은 예외는 std::terminate를 호출해 프로그램을 비정상 종료시킨다. 던질 수 있는 연산은 적절한 catch로 감싸 오류를 처리한다.'},

 {'id':'ERR52-CPP','cat':'ERR · Rule · L1',
  'title':'예외 처리에 setjmp/longjmp를 사용하지 않는다',
  'bad': r"""#include <csetjmp>
std::jmp_buf env;
struct R { ~R(); };
void f() {
    R r;
    std::longjmp(env, 1); // r의 소멸자가 호출되지 않음 → 자원 누수/UB
}""",
  'good': r"""struct R { ~R(); };
void f() {
    R r;
    throw std::runtime_error("fail"); // 스택 해제 중 소멸자 정상 호출
}""",
  'why':'longjmp는 C++ 객체의 소멸자를 호출하지 않고 스택을 건너뛰어 자원 누수와 미정의 동작을 일으킨다. 오류 전파는 예외 메커니즘으로 수행한다.'},

 {'id':'ERR55-CPP','cat':'ERR · Rule · L2',
  'title':'선언한 예외 명세(noexcept)를 준수한다',
  'bad': r"""#include <stdexcept>
void f() noexcept {
    throw std::runtime_error("oops"); // noexcept 함수에서 throw → terminate
}""",
  'good': r"""#include <stdexcept>
void f() noexcept {
    try {
        // 던질 수 있는 작업
    } catch (...) {
        // 내부에서 모두 처리, 밖으로 전파하지 않음
    }
}""",
  'why':'noexcept로 선언한 함수에서 예외가 빠져나가면 std::terminate가 호출되어 즉시 종료된다. noexcept 함수는 내부에서 예외를 모두 처리하거나 명세를 정확히 맞춘다.'},

 {'id':'ERR58-CPP','cat':'ERR · Rule · L2',
  'title':'main 진입 전 발생하는 예외를 처리한다',
  'bad': r"""#include <stdexcept>
struct Init { Init() { throw std::runtime_error("ctor fail"); } };
Init global; // main 이전 정적 초기화 중 예외 → 처리 불가, terminate
int main() { return 0; }""",
  'good': r"""#include <stdexcept>
struct Init { Init() noexcept { /* 던지지 않는 초기화 */ } };
Init& global() {                 // 지연 초기화로 예외를 처리 가능 시점에
    static Init instance;        // 첫 사용 시 생성, try로 감쌀 수 있음
    return instance;
}
int main() { (void)global(); return 0; }""",
  'why':'main 진입 전 정적 객체 생성 중 던진 예외는 일반 try/catch로 잡을 수 없어 terminate로 이어진다. 던지지 않는 초기화나 지연 초기화로 예외를 처리 가능한 시점으로 옮긴다.'},

 {'id':'ERR61-CPP','cat':'ERR · Rule · L2',
  'title':'예외를 lvalue 참조로 catch한다',
  'bad': r"""#include <stdexcept>
void f() {
    try {
        throw std::runtime_error("x");
    } catch (std::exception e) { // 값으로 catch → 슬라이싱, 복사 비용
        // 파생 정보 소실
    }
}""",
  'good': r"""#include <stdexcept>
void f() {
    try {
        throw std::runtime_error("x");
    } catch (const std::exception& e) { // const lvalue 참조
        // 다형성 보존, 복사 없음
    }
}""",
  'why':'예외를 값으로 잡으면 객체 슬라이싱으로 파생 예외 정보가 잘리고 불필요한 복사가 일어난다. 예외는 const lvalue 참조로 catch해 다형성을 보존한다.'},
]
