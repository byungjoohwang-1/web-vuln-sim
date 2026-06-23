# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트3: A16~A27·M10~M19) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17 -pthread` 기준.
주의: 검증은 컴파일 후 실행하므로 종료/시그널/longjmp 등 위험 경로는 런타임에 도달하지 않게 가드한다.
std::auto_ptr 는 C++17에서 제거되어 단독 컴파일 불가 → 초점 스니펫으로 유지."""

RULES = [
 {'id':'A16-2-2','cat':'Required · Automated','compiles':True,
  'title':'사용되지 않는 #include 를 두지 않는다',
  'title_en':'There shall be no unused include directives',
  'bad': r"""#include <iostream>
#include <vector>    // 이 파일에서 vector 를 전혀 사용하지 않음 — 불필요한 의존
#include <string>
int main() {
    std::string s = "hi";
    std::cout << s << '\n';
}""",
  'good': r"""#include <iostream>
#include <string>   // 실제 사용하는 헤더만 포함
int main() {
    std::string s = "hi";
    std::cout << s << '\n';
}""",
  'why':'근거: 어떤 헤더의 심볼을 전혀 쓰지 않으면서 그 헤더를 포함하면, 코드가 실제로 무엇에 의존하는지 흐려지고 불필요한 컴파일 의존이 생긴다. 영향: 사용되지 않는 #include 는 컴파일 시간을 늘리고, 그 헤더가 바뀔 때 불필요한 재빌드를 유발하며, 모듈 간 결합을 실제보다 커 보이게 한다. 대응: 파일이 실제로 사용하는 심볼을 제공하는 헤더만 포함하고, 사용하지 않게 된 포함은 제거한다.',
  'why_en':'Rationale: including a header while using none of its symbols obscures what the code actually depends on and creates an unnecessary compile dependency. Impact: an unused #include increases compile time, triggers needless rebuilds when that header changes, and makes inter-module coupling look larger than it is. Fix: include only headers that provide symbols the file actually uses, and remove includes that are no longer needed.'},

 {'id':'A16-7-1','cat':'Required · Automated','compiles':True,
  'title':'#pragma 지시문을 사용하지 않는다',
  'title_en':'The #pragma directive shall not be used',
  'bad': r"""#include <iostream>
#pragma pack(1)   // 구현정의 패킹 — 컴파일러마다 다르게 동작/무시될 수 있음
struct Packet { char tag; int value; };
#pragma pack()
int main() { std::cout << sizeof(Packet) << '\n'; }""",
  'good': r"""#include <iostream>
#include <cstdint>
// 표준 메커니즘으로 명시적 레이아웃 표현(필요한 정렬을 alignas 로)
struct alignas(4) Packet { char tag; std::int32_t value; };
int main() { std::cout << sizeof(Packet) << '\n'; }""",
  'why':'근거: #pragma 의 의미는 표준이 정의하지 않고 전적으로 구현(컴파일러)에 맡겨져 있어, 같은 #pragma 가 컴파일러마다 다르게 동작하거나 조용히 무시될 수 있다. 영향: #pragma pack 같은 지시문에 의존하면 구조체 레이아웃이 컴파일러·버전에 따라 달라져 직렬화·ABI 가 깨지고, 이식할 때 진단 없는 결함이 된다. 대응: 정렬·표현이 필요하면 alignas 같은 표준 언어 기능으로 명시하고, 컴파일러 고유 동작이 불가피하면 한 곳에 격리해 문서화한다.',
  'why_en':'Rationale: the meaning of #pragma is not defined by the standard and is left entirely to the implementation, so the same #pragma may behave differently across compilers or be silently ignored. Impact: relying on directives like #pragma pack makes struct layout vary by compiler and version, breaking serialization and ABI and becoming a defect with no diagnostic when porting. Fix: express needed alignment/representation with standard language features like alignas, and isolate and document any unavoidable compiler-specific behaviour in one place.'},

 {'id':'A17-1-1','cat':'Required · Non-automated','compiles':True,
  'title':'C 라이브러리 기능 대신 C++ 표준 라이브러리 대안을 사용한다',
  'title_en':'Use of the C Standard Library shall be encapsulated and isolated',
  'bad': r"""#include <cstdio>
#include <iostream>
int main() {
    int v = 42;
    char buf[4];                 // 작은 고정 버퍼
    std::sprintf(buf, "%d", v);  // 경계 미검사 C 함수 — 큰 값이면 오버플로우
    std::cout << buf << '\n';
}""",
  'good': r"""#include <string>
#include <iostream>
int main() {
    int v = 42;
    std::string s = std::to_string(v);   // 타입 안전·길이 자동 관리
    std::cout << s << '\n';
}""",
  'why':'근거: sprintf·strcpy 같은 C 라이브러리 함수는 형식 문자열과 인자의 타입 일치를 컴파일러가 보장하지 못하고 대상 버퍼 크기를 받지 않아 경계 검사가 없다. 영향: 형식·타입 불일치나 버퍼 초과가 미정의 동작·버퍼 오버플로우로 이어져, 흔한 보안 취약점의 원천이 된다. 대응: 동등한 C++ 표준 라이브러리 기능(std::to_string, std::string, <iostream>·<format>)을 우선 사용하고, 불가피한 C API 호출은 안전한 래퍼로 캡슐화·격리한다.',
  'why_en':'Rationale: C library functions like sprintf and strcpy give the compiler no way to verify that the format string matches argument types and take no destination buffer size, so there is no bounds checking. Impact: a format/type mismatch or buffer overrun leads to undefined behaviour and buffer overflow, a frequent source of security vulnerabilities. Fix: prefer the equivalent C++ standard-library facilities (std::to_string, std::string, <iostream>/<format>), and encapsulate any unavoidable C API call in a safe wrapper.'},

 {'id':'A18-0-2','cat':'Required · Automated','compiles':True,
  'title':'문자열→숫자 변환의 오류 상태를 검사한다',
  'title_en':'The error state of conversion from string to a numeric value shall be checked',
  'bad': r"""#include <cstdlib>
#include <iostream>
#include <string>
int main() {
    std::string s = "not a number";
    int n = std::atoi(s.c_str());   // 변환 실패를 정상 0 과 구분 못함
    std::cout << n << '\n';          // 0 — 입력이 숫자가 아닌데 성공으로 오인
}""",
  'good': r"""#include <iostream>
#include <string>
#include <stdexcept>
int main() {
    std::string s = "not a number";
    try {
        std::size_t pos;
        int n = std::stoi(s, &pos);
        if (pos != s.size()) throw std::invalid_argument("trailing chars");
        std::cout << n << '\n';
    } catch (const std::exception& e) { std::cout << "convert error: " << e.what() << '\n'; }
}""",
  'why':'근거: atoi 는 변환에 실패해도 0 을 반환할 뿐 오류 신호가 없고, 어디까지 변환했는지도 알려주지 않으며 범위 초과를 미정의 동작으로 둔다. 영향: 입력 "0" 과 변환 실패가 구분되지 않고 "12abc" 처럼 일부만 변환된 값이 조용히 통과해, 잘못된 수치가 계산·인덱스로 흘러든다. 대응: 예외를 던지는 std::stoi/stol(또는 std::from_chars)을 사용하고, 변환 종료 위치(pos)로 전체 문자열이 정확히 소비됐는지 확인한다.',
  'why_en':'Rationale: atoi returns 0 even on failure with no error signal, does not report how far it converted, and leaves out-of-range as undefined behaviour. Impact: input "0" is indistinguishable from a failure and partially converted values like "12abc" pass silently, letting a wrong number flow into computations or indices. Fix: use std::stoi/stol (or std::from_chars) which signal errors, and check the end position (pos) to confirm the whole string was consumed.'},

 {'id':'A18-1-1','cat':'Required · Automated','compiles':True,
  'title':'C 스타일 배열을 사용하지 않는다',
  'title_en':'C-style arrays shall not be used',
  'bad': r"""#include <iostream>
#include <cstddef>
static std::size_t count(int arr[]) {   // 배열이 포인터로 붕괴 — 크기 정보 손실
    return sizeof(arr) / sizeof(arr[0]);  // 포인터 크기 / int 크기 (보통 2) — 틀림
}
int main() {
    int a[10] = {0};
    std::cout << count(a) << '\n';   // 10 이 아니라 2 — 크기 추론 실패
}""",
  'good': r"""#include <iostream>
#include <array>
static std::size_t count(const std::array<int,10>& arr) {
    return arr.size();   // 크기가 타입에 보존됨
}
int main() {
    std::array<int,10> a{};
    std::cout << count(a) << '\n';   // 10
}""",
  'why':'근거: C 스타일 배열은 함수에 전달될 때 첫 원소를 가리키는 포인터로 붕괴(decay)해 크기 정보를 잃고, 경계 검사도 제공하지 않는다. 영향: 함수 안에서 sizeof 로 원소 수를 구하려 하면 포인터 크기를 재게 되어 틀린 값이 나오고, 인덱스 접근의 경계를 알 수 없어 오버런이 숨는다. 대응: 크기를 타입에 보존하고 .size()·범위 기반 접근·경계 검사(at)를 제공하는 std::array(고정 크기)·std::vector(가변 크기)를 사용한다.',
  'why_en':'Rationale: a C-style array decays to a pointer to its first element when passed to a function, losing size information and providing no bounds checking. Impact: trying to get the element count with sizeof inside the function measures the pointer instead, giving a wrong value, and the bounds for index access are unknown so overruns hide. Fix: use std::array (fixed size) or std::vector (dynamic) which preserve size in the type and provide .size(), range-based access, and bounds-checked at().'},

 {'id':'A18-1-2','cat':'Required · Automated','compiles':True,
  'title':'std::vector<bool> 을 사용하지 않는다',
  'title_en':'The std::vector<bool> specialization shall not be used',
  'bad': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<bool> flags(4, false);   // 비트 압축 특수화
    auto ref = flags[0];   // bool& 가 아니라 프록시 객체 — auto 가 프록시를 잡음
    flags[1] = true;
    ref = true;            // 프록시를 통한 대입 — 일반 vector 와 의미가 다름
    std::cout << flags[0] << flags[1] << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <cstdint>
int main() {
    std::vector<std::uint8_t> flags(4, 0);   // 일반 컨테이너 — 원소 참조가 진짜 참조
    std::uint8_t& ref = flags[0];
    flags[1] = 1;
    ref = 1;
    std::cout << int(flags[0]) << int(flags[1]) << '\n';
}""",
  'why':'근거: std::vector<bool> 은 메모리 절약을 위해 각 원소를 1비트로 압축한 특수화라, operator[] 가 bool& 가 아니라 비트를 가리키는 프록시 객체를 반환한다. 영향: auto x = v[i] 가 프록시를 잡아 예상과 다르게 동작하고, &v[i] 로 진짜 bool* 를 얻을 수 없으며, 다른 컨테이너를 가정한 제네릭 코드가 깨진다. 대응: 불리언 시퀀스가 필요하면 크기가 고정이면 std::bitset 을, 가변이면 std::vector<std::uint8_t>(또는 char) 처럼 일반 원소 의미를 갖는 타입을 사용한다.',
  'why_en':'Rationale: std::vector<bool> is a specialization that packs each element into a single bit to save memory, so operator[] returns a proxy object referring to a bit, not a bool&. Impact: auto x = v[i] captures the proxy and behaves unexpectedly, you cannot obtain a real bool* via &v[i], and generic code assuming a normal container breaks. Fix: use std::bitset for a fixed-size boolean sequence, or a type with normal element semantics like std::vector<std::uint8_t> (or char) for a dynamic one.'},

 {'id':'A18-1-3','cat':'Required · Automated',
  'title':'std::auto_ptr 를 사용하지 않는다',
  'title_en':'The std::auto_ptr type shall not be used',
  'bad': r"""#include <memory>
// std::auto_ptr 은 C++11 에서 폐기, C++17 에서 제거됨(현 표준에선 컴파일조차 안 됨)
std::auto_ptr<int> p(new int(1));
std::auto_ptr<int> q = p;   // 복사처럼 보이지만 소유권을 몰래 이전 — p 는 널이 됨""",
  'good': r"""#include <memory>
auto p = std::make_unique<int>(1);
std::unique_ptr<int> q = std::move(p);   // 소유권 이전이 std::move 로 명시됨
// (단독 소유는 unique_ptr, 이전은 항상 std::move 로 표현)""",
  'why':'근거: std::auto_ptr 은 복사 생성·복사 대입이 사실상 소유권을 이전(원본을 널로)하는 위험한 의미를 가져, 복사처럼 보이는 연산이 원본을 조용히 무력화한다. 영향: auto_ptr 을 값으로 컨테이너에 넣거나 복사하면 원본 포인터가 널이 되어 예기치 않은 널 역참조·이중 관리가 발생하며, 이 때문에 C++11 에서 폐기되고 C++17 에서 표준에서 제거되었다(현 표준 빌드에서는 컴파일 자체가 실패한다). 대응: 단독 소유는 std::unique_ptr 로 표현하고 소유권 이전은 std::move 로 명시한다.',
  'why_en':'Rationale: std::auto_ptr has dangerous semantics where copy construction and copy assignment actually transfer ownership (nulling the source), so an operation that looks like a copy silently disables the original. Impact: putting an auto_ptr by value into a container or copying it nulls the source pointer, causing unexpected null dereferences and double management, which is why it was deprecated in C++11 and removed from the standard in C++17 (it no longer even compiles under the current standard). Fix: express single ownership with std::unique_ptr and make ownership transfer explicit with std::move.'},

 {'id':'A18-5-1','cat':'Required · Automated','compiles':True,
  'title':'malloc/calloc/realloc/free 를 사용하지 않는다',
  'title_en':'Functions malloc, calloc, realloc and free shall not be used',
  'bad': r"""#include <cstdlib>
#include <iostream>
#include <string>
int main() {
    // malloc 은 생성자를 호출하지 않음 → std::string 의 불변식이 성립하지 않은 메모리
    auto* s = static_cast<std::string*>(std::malloc(sizeof(std::string)));
    // s->size();   // 생성자 미호출 객체 사용 — 미정의 동작
    std::free(s);   // 소멸자도 미호출
    std::cout << "raw malloc/free used\n";
}""",
  'good': r"""#include <iostream>
#include <memory>
#include <string>
int main() {
    auto s = std::make_unique<std::string>("hi");   // 생성자 호출·소멸 자동
    std::cout << *s << '\n';
}""",
  'why':'근거: malloc/calloc/realloc/free 는 메모리 블록만 다룰 뿐 C++ 객체의 생성자·소멸자를 호출하지 않아, 비trivial 타입에 쓰면 객체가 초기화되지 않고 정리되지도 않는다. 영향: 생성자가 불려야 성립하는 불변식(std::string 의 내부 포인터 등)이 깨진 채 사용되어 미정의 동작이 되고, 소멸자 누락으로 자원이 누수되며, realloc 은 객체 이동 의미를 무시해 손상시킨다. 대응: 동적 객체는 new/delete 또는 스마트 포인터(make_unique/make_shared)로 관리해 생성·소멸이 자동으로 일어나게 한다.',
  'why_en':'Rationale: malloc/calloc/realloc/free only manage memory blocks and do not call C++ constructors or destructors, so using them with non-trivial types leaves objects neither initialized nor cleaned up. Impact: invariants that require a constructor (such as the internal pointer of std::string) are used while broken — undefined behaviour — resources leak from missed destructors, and realloc corrupts objects by ignoring move semantics. Fix: manage dynamic objects with new/delete or smart pointers (make_unique/make_shared) so construction and destruction happen automatically.'},

 {'id':'A18-5-2','cat':'Required · Automated','compiles':True,
  'title':'raw new/delete 를 직접 쓰지 않는다(make_unique/make_shared 사용)',
  'title_en':'Non-placement new and delete expressions shall not be used',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct Widget { int v = 7; };
static void risky(int argc) { if (argc >= 0) throw std::runtime_error("fail"); }
static void use(int argc) {
    Widget* w = new Widget();   // raw new
    risky(argc);                // 예외 시 아래 delete 를 건너뜀 → 누수
    delete w;
}
int main(int argc, char**) { try { use(argc); } catch (...) { std::cout << "leaked w\n"; } }""",
  'good': r"""#include <iostream>
#include <memory>
#include <stdexcept>
struct Widget { int v = 7; };
static void risky() { throw std::runtime_error("fail"); }
static void use() {
    auto w = std::make_unique<Widget>();   // 예외에도 자동 해제
    risky();
}
int main() { try { use(); } catch (...) { std::cout << "no leak (RAII)\n"; } }""",
  'why':'근거: 명시적 new 로 얻은 raw 포인터는 짝이 되는 delete 를 모든 실행 경로에서 사람이 직접 보장해야 하는데, 그 사이 코드가 예외를 던지면 delete 가 실행되지 않는다. 영향: 예외 경로에서 누수가 발생하고, 소유권이 여러 곳으로 흩어지면 이중 해제·use-after-free 같은 결함이 추가된다. 대응: new/delete 를 직접 쓰지 말고 make_unique/make_shared 로 소유권을 스마트 포인터에 맡겨 예외에도 수명이 자동 관리되게 한다.',
  'why_en':'Rationale: a raw pointer from an explicit new requires a human to guarantee the matching delete on every execution path, but if code in between throws, the delete never runs. Impact: leaks occur on exception paths, and when ownership is scattered, defects like double free and use-after-free are added. Fix: instead of raw new/delete, give ownership to smart pointers via make_unique/make_shared so lifetime is managed automatically even under exceptions.'},

 {'id':'A18-5-3','cat':'Required · Automated','compiles':True,
  'title':'delete 의 형태는 new 의 형태와 일치시킨다',
  'title_en':'The form of delete shall match the form of the new expression used',
  'bad': r"""#include <iostream>
int main() {
    int* a = new int[10];   // 배열 형태로 할당
    a[0] = 1;
    delete a;               // new[] 를 delete 로 해제 — 형태 불일치, 미정의 동작
    std::cout << "mismatched delete\n";
}""",
  'good': r"""#include <iostream>
#include <memory>
int main() {
    auto a = std::make_unique<int[]>(10);   // 컨테이너/스마트포인터가 올바른 해제 보장
    a[0] = 1;
    std::cout << a[0] << '\n';
}""",
  'why':'근거: new 와 new[] 는 서로 다른 할당 경로를 사용하므로 표준은 new 는 delete 로, new[] 는 delete[] 로만 해제하도록 요구한다. 영향: 형태가 어긋나면 배열 원소의 소멸자가 호출되지 않거나 잘못된 크기로 메모리가 반환되어 힙이 손상되는 미정의 동작이 되며, 진단 없이 통과하기 쉽다. 대응: 직접 new[]/delete[] 를 쓰는 대신 std::vector 나 std::make_unique<T[]> 로 할당·해제를 자동화해 형태 불일치를 원천 차단한다.',
  'why_en':'Rationale: new and new[] use different allocation paths, so the standard requires new to be released with delete and new[] with delete[]. Impact: a mismatched form skips array element destructors or frees with the wrong size, corrupting the heap — undefined behaviour that often passes with no diagnostic. Fix: instead of raw new[]/delete[], automate allocation and deallocation with std::vector or std::make_unique<T[]> to eliminate form mismatch.'},

 {'id':'A18-9-1','cat':'Required · Automated','compiles':True,
  'title':'std::bind 를 사용하지 않는다(람다 사용)',
  'title_en':'The std::bind shall not be used',
  'bad': r"""#include <iostream>
#include <functional>
static int calc(int x, int factor) { return x * factor; }
int main() {
    using namespace std::placeholders;
    auto f = std::bind(calc, _1, 10);   // 자리표시자 — 가독성 낮고 오버로드에 취약
    std::cout << f(5) << '\n';
}""",
  'good': r"""#include <iostream>
static int calc(int x, int factor) { return x * factor; }
int main() {
    auto f = [](int x){ return calc(x, 10); };   // 의도가 명확한 람다
    std::cout << f(5) << '\n';
}""",
  'why':'근거: std::bind 는 _1, _2 같은 자리표시자로 인자를 재배치하는데, 이 표기는 호출 시 인자가 어디로 가는지 한눈에 드러나지 않고 오버로드된 함수나 완벽 전달과 결합할 때 모호성·오류가 생기기 쉽다. 영향: bind 표현식은 읽기 어려워 유지보수자가 동작을 오해하고, 인자 복사·참조 정책이 암묵적이라 의도치 않은 복사나 댕글링이 숨는다. 대응: 부분 적용·인자 재배치가 필요하면 의도가 코드에 그대로 드러나는 람다로 대체한다.',
  'why_en':'Rationale: std::bind rearranges arguments with placeholders like _1, _2, but this notation does not make clear at a glance where call arguments go, and combining it with overloaded functions or perfect forwarding easily creates ambiguity and errors. Impact: bind expressions are hard to read so maintainers misunderstand the behaviour, and the implicit argument copy/reference policy hides unintended copies or dangling. Fix: replace partial application and argument rearrangement with a lambda whose intent is plainly visible in the code.'},

 {'id':'A18-9-2','cat':'Required · Automated','compiles':True,
  'title':'rvalue 는 std::move, 전달 참조는 std::forward 로 전달한다',
  'title_en':'Forwarding values to other functions shall be done via std::move or std::forward',
  'bad': r"""#include <iostream>
#include <string>
#include <utility>
static void sink(std::string s) { std::cout << "sink: " << s << '\n'; }
template <typename T>
static void wrap(T&& x) { sink(std::move(x)); }   // 전달 참조에 무조건 move
int main() {
    std::string a = "keep me";
    wrap(a);                  // a 는 lvalue 인데 move 됨 → a 가 비워짐
    std::cout << "a after = '" << a << "'\n";   // '' — 호출자 객체 훼손
}""",
  'good': r"""#include <iostream>
#include <string>
#include <utility>
static void sink(std::string s) { std::cout << "sink: " << s << '\n'; }
template <typename T>
static void wrap(T&& x) { sink(std::forward<T>(x)); }   // 값 범주 보존
int main() {
    std::string a = "keep me";
    wrap(a);                  // lvalue → 복사로 전달, a 보존
    std::cout << "a after = '" << a << "'\n";   // 'keep me'
}""",
  'why':'근거: 템플릿의 T&& 는 전달 참조(forwarding reference)로 lvalue 와 rvalue 를 모두 받는데, 여기에 std::move 를 무조건 적용하면 lvalue 로 넘긴 호출자 객체까지 이동 대상으로 만들어 버린다. 영향: 호출자가 계속 쓰려던 변수가 이동되어 비워지면(예제의 a), 그 객체에 의존하는 이후 코드가 빈 값·미지정 상태를 만나 조용한 버그가 된다. 대응: 전달 참조는 std::forward<T> 로 전달해 원래의 값 범주(lvalue 는 복사, rvalue 는 이동)를 보존하고, 확실한 rvalue 만 std::move 한다.',
  'why_en':'Rationale: a template T&& is a forwarding reference that accepts both lvalues and rvalues, and applying std::move unconditionally makes even a caller object passed as an lvalue a move target. Impact: a variable the caller intended to keep using is moved-from and emptied (a in the example), so later code depending on it meets an empty or unspecified value — a silent bug. Fix: forward a forwarding reference with std::forward<T> to preserve the original value category (copy for lvalues, move for rvalues), and use std::move only on definite rvalues.'},

 {'id':'A18-9-3','cat':'Required · Automated','compiles':True,
  'title':'const 객체에 std::move 를 적용하지 않는다',
  'title_en':'The std::move shall not be used on const objects',
  'bad': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    const std::string s = "payload";
    std::string t = std::move(s);   // s 가 const → 이동 불가, 조용히 복사로 폴백
    std::cout << "s='" << s << "' t='" << t << "'\n";   // s 그대로 — move 의 의미 없음
}""",
  'good': r"""#include <iostream>
#include <string>
#include <utility>
int main() {
    std::string s = "payload";      // 이동할 대상은 비-const
    std::string t = std::move(s);   // 실제 이동 — s 의 버퍼를 t 가 가져감
    std::cout << "moved; t='" << t << "'\n";
}""",
  'why':'근거: std::move 는 인자를 rvalue 로 캐스트할 뿐이고, 대상이 const 이면 const rvalue 가 되어 이동 생성자(비-const rvalue 참조를 받음)가 아니라 복사 생성자가 선택된다. 영향: const 객체에 std::move 를 쓰면 코드 작성자는 이동(저렴)을 기대하지만 실제로는 조용히 복사(비쌈)가 일어나, 의도한 성능 이점이 사라지고 잘못된 기대가 코드에 남는다. 대응: 이동하려는 객체는 비-const 로 선언하고, 정말 복사가 필요하면 std::move 없이 그대로 대입해 의도를 분명히 한다.',
  'why_en':'Rationale: std::move only casts its argument to an rvalue, and if the target is const it becomes a const rvalue, so the copy constructor — not the move constructor (which takes a non-const rvalue reference) — is selected. Impact: using std::move on a const object makes the author expect a cheap move but silently performs an expensive copy, losing the intended performance benefit and leaving a wrong expectation in the code. Fix: declare objects to be moved as non-const, and when a copy is genuinely needed, assign directly without std::move to make the intent clear.'},

 {'id':'A20-8-1','cat':'Required · Automated','compiles':True,
  'title':'소유 포인터(owning pointer)는 스마트 포인터로 표현한다',
  'title_en':'A std::unique_ptr shall be used to represent exclusive ownership',
  'bad': r"""#include <iostream>
struct Widget { int v = 7; };
static Widget* create() { return new Widget(); }   // 소유권이 모호한 raw 반환
int main() {
    Widget* w = create();   // 호출자가 delete 해야 하는지 인터페이스만 봐선 모름
    std::cout << w->v << '\n';
    delete w;               // 깜빡하면 누수, 두 번 하면 이중 해제
}""",
  'good': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
static std::unique_ptr<Widget> create() { return std::make_unique<Widget>(); }
int main() {
    auto w = create();   // 반환 타입이 단독 소유권을 명시 — 해제는 자동
    std::cout << w->v << '\n';
}""",
  'why':'근거: raw 포인터는 그것이 단지 가리키기만 하는지(비소유) 아니면 해제 책임까지 넘기는지(소유) 타입만으로는 구분되지 않아, 소유권 계약이 인터페이스에 드러나지 않는다. 영향: 함수가 new 한 raw 포인터를 반환하면 호출자가 delete 책임을 모르거나 잘못 알아 누수·이중 해제가 발생하고, 예외 경로에서 특히 취약하다. 대응: 단독 소유는 std::unique_ptr, 공유 소유는 std::shared_ptr 로 반환·전달해 소유권과 해제 책임을 타입으로 명시한다.',
  'why_en':'Rationale: a raw pointer does not distinguish by type alone whether it merely points (non-owning) or transfers the responsibility to release (owning), so the ownership contract is not expressed in the interface. Impact: a function returning a new-ed raw pointer leaves the caller unaware or mistaken about the delete responsibility, causing leaks or double frees, and is especially fragile on exception paths. Fix: return and pass std::unique_ptr for exclusive ownership and std::shared_ptr for shared ownership to make ownership and release responsibility explicit in the type.'},

 {'id':'A20-8-4','cat':'Required · Automated','compiles':True,
  'title':'공유가 필요 없으면 shared_ptr 대신 unique_ptr 를 쓴다',
  'title_en':'A std::unique_ptr shall be used over std::shared_ptr if ownership is not shared',
  'bad': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    std::shared_ptr<Widget> w = std::make_shared<Widget>();   // 단독 소유에 shared
    std::cout << w->v << " use_count=" << w.use_count() << '\n';   // 원자적 카운트 비용
}""",
  'good': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    auto w = std::make_unique<Widget>();   // 단독 소유 — 오버헤드 없음
    std::cout << w->v << '\n';
}""",
  'why':'근거: shared_ptr 는 여러 소유자가 수명을 공유하기 위해 제어 블록과 원자적(스레드 안전) 참조 카운트를 유지하는데, 소유자가 하나뿐이면 이 비용이 순수한 낭비다. 영향: 단독 소유에 shared_ptr 를 쓰면 매 복사·소멸마다 원자적 증감 비용이 들고, 메모리(제어 블록)도 더 쓰며, 의도(이 자원은 한 소유자)가 코드에 잘못 전달된다. 대응: 소유권을 실제로 공유해야 할 때만 shared_ptr 를 쓰고, 그 외에는 더 가볍고 의도가 분명한 unique_ptr 를 사용한다.',
  'why_en':'Rationale: shared_ptr maintains a control block and an atomic (thread-safe) reference count so multiple owners can share a lifetime, but when there is only one owner this cost is pure waste. Impact: using shared_ptr for sole ownership pays an atomic increment/decrement on every copy and destruction, uses extra memory for the control block, and miscommunicates the intent (this resource has one owner). Fix: use shared_ptr only when ownership is genuinely shared, and otherwise use the lighter, clearer unique_ptr.'},

 {'id':'A20-8-5','cat':'Required · Automated','compiles':True,
  'title':'unique_ptr 는 std::make_unique 로 생성한다',
  'title_en':'std::make_unique shall be used to construct objects owned by std::unique_ptr',
  'bad': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    std::unique_ptr<Widget> w(new Widget());   // 타입 중복 표기, 예외 안전성 약함
    std::cout << w->v << '\n';
}""",
  'good': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    auto w = std::make_unique<Widget>();   // 타입 한 번, 예외 안전
    std::cout << w->v << '\n';
}""",
  'why':'근거: make_unique 는 객체 생성과 unique_ptr 소유를 한 표현식으로 묶어, 타입 이름을 한 번만 쓰고 raw new 포인터가 잠시라도 소유자 없이 노출되는 구간을 없앤다. 영향: 직접 new 로 unique_ptr 를 만들면 타입을 두 번 적어 불일치 위험이 생기고, 함수 인자로 여러 new 를 평가하는 옛 문맥에서는 예외 시 누수가 날 수 있으며 코드가 장황해진다. 대응: unique_ptr 생성은 일관되게 make_unique 로 하고, 사용자 deleter 같은 특수한 경우에만 예외적으로 직접 생성한다.',
  'why_en':'Rationale: make_unique binds object creation and unique_ptr ownership into one expression, writing the type name once and eliminating any window where a raw new pointer is exposed without an owner. Impact: constructing a unique_ptr directly with new repeats the type (risking mismatch), can leak on exceptions in older contexts that evaluate multiple news as arguments, and is more verbose. Fix: construct unique_ptr consistently with make_unique, using direct construction only for special cases like a custom deleter.'},

 {'id':'A20-8-6','cat':'Required · Automated','compiles':True,
  'title':'shared_ptr 는 std::make_shared 로 생성한다',
  'title_en':'std::make_shared shall be used to construct objects owned by std::shared_ptr',
  'bad': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    std::shared_ptr<Widget> w(new Widget());   // 객체와 제어블록을 별도로 두 번 할당
    std::cout << w->v << '\n';
}""",
  'good': r"""#include <iostream>
#include <memory>
struct Widget { int v = 7; };
int main() {
    auto w = std::make_shared<Widget>();   // 객체+제어블록을 한 번에 할당
    std::cout << w->v << '\n';
}""",
  'why':'근거: make_shared 는 관리 대상 객체와 참조 카운트를 담는 제어 블록을 한 번의 할당으로 함께 배치해, 메모리 할당 횟수와 캐시 미스를 줄이고 예외 안전성을 높인다. 영향: shared_ptr<T>(new T) 형태는 객체와 제어 블록을 두 번 할당해 비효율적이고, new 와 shared_ptr 생성 사이 예외 시 누수 위험이 있다. 대응: shared_ptr 생성은 make_shared 로 한다(단, 객체와 제어 블록 수명을 분리하고 싶거나 weak_ptr 로 큰 객체 메모리를 오래 붙잡고 싶지 않은 특수 경우는 예외).',
  'why_en':'Rationale: make_shared places the managed object and the control block holding the reference count together in a single allocation, reducing allocation count and cache misses and improving exception safety. Impact: the shared_ptr<T>(new T) form allocates the object and control block twice (inefficient) and risks a leak on an exception between the new and the shared_ptr construction. Fix: construct shared_ptr with make_shared (except in special cases where you want the object and control-block lifetimes separated, or to avoid a weak_ptr keeping a large object memory alive).'},

 {'id':'A20-8-7','cat':'Advisory · Automated','compiles':True,
  'title':'순환 참조를 끊기 위해 weak_ptr 를 사용한다',
  'title_en':'A std::weak_ptr shall be used to represent temporary shared ownership',
  'bad': r"""#include <iostream>
#include <memory>
struct Node {
    std::shared_ptr<Node> next;
    std::shared_ptr<Node> prev;   // 서로를 shared 로 가리킴 → 순환 참조
    ~Node() { std::cout << "~Node\n"; }
};
int main() {
    auto a = std::make_shared<Node>();
    auto b = std::make_shared<Node>();
    a->next = b; b->prev = a;   // a,b 의 카운트가 0 으로 못 내려감 → 소멸자 미호출, 누수
    std::cout << "use_count a=" << a.use_count() << '\n';   // 2
}""",
  'good': r"""#include <iostream>
#include <memory>
struct Node {
    std::shared_ptr<Node> next;
    std::weak_ptr<Node> prev;   // 역방향(비소유) 링크는 weak_ptr
    ~Node() { std::cout << "~Node\n"; }
};
int main() {
    auto a = std::make_shared<Node>();
    auto b = std::make_shared<Node>();
    a->next = b; b->prev = a;   // weak 는 카운트를 올리지 않음 → 정상 소멸
    std::cout << "use_count a=" << a.use_count() << '\n';   // 1
}""",
  'why':'근거: 두 객체가 서로를 shared_ptr 로 가리키면 각자의 참조 카운트가 상대 때문에 0 으로 내려가지 못해, 외부 참조가 모두 사라져도 둘 다 해제되지 않는다. 영향: 이런 순환 참조는 소멸자가 호출되지 않는 메모리 누수를 만들고, 누수가 쌓이면 장시간 구동 시스템의 메모리가 고갈된다. 대응: 소유 관계의 한 방향(부모→자식 등)만 shared_ptr 로 두고, 역방향이나 비소유 관찰 링크는 카운트를 올리지 않는 weak_ptr 로 두어 순환을 끊는다.',
  'why_en':'Rationale: when two objects point at each other with shared_ptr, neither reference count can reach zero because of the other, so even after all external references are gone neither is released. Impact: such a reference cycle creates a memory leak where destructors are never called, and accumulated leaks exhaust memory in long-running systems. Fix: keep only one direction of an ownership relationship (parent to child) as shared_ptr and make the reverse or non-owning observing link a weak_ptr, which does not raise the count, breaking the cycle.'},

 {'id':'A21-8-1','cat':'Required · Automated','compiles':True,
  'title':'문자 분류/변환 함수 인자는 unsigned char 로 표현 가능해야 한다',
  'title_en':'Arguments to character-handling functions shall be representable as an unsigned char',
  'bad': r"""#include <iostream>
#include <cctype>
static bool is_letter(char c) {
    return std::isalpha(c);   // char 가 음수(서명 char에서 0x80 이상)면 EOF 외 음수 → 미정의
}
int main() {
    char c = static_cast<char>(0xE9);   // 'é' 등 — 서명 char 에서 음수
    std::cout << is_letter(c) << '\n';   // 미정의 동작(구현에 따라 크래시/오답)
}""",
  'good': r"""#include <iostream>
#include <cctype>
static bool is_letter(char c) {
    return std::isalpha(static_cast<unsigned char>(c));   // 유효 범위 보장
}
int main() {
    char c = static_cast<char>(0xE9);
    std::cout << is_letter(c) << '\n';
}""",
  'why':'근거: <cctype> 의 isalpha·toupper 등은 인자가 unsigned char 로 표현 가능한 값이거나 EOF 여야 한다고 규정한다. 영향: char 가 서명 타입인 구현에서 0x80 이상의 바이트(확장 ASCII·UTF-8 바이트)는 음수가 되어 EOF 가 아닌 음수로 전달되면 미정의 동작이 되며, 일부 구현은 내부 룩업 테이블을 음수 인덱스로 접근해 크래시한다. 대응: 이들 함수에 char 를 넘기기 전에 static_cast<unsigned char> 로 변환해 항상 유효한 범위의 값을 전달한다.',
  'why_en':'Rationale: functions in <cctype> like isalpha and toupper require their argument to be a value representable as unsigned char or EOF. Impact: on implementations where char is signed, bytes at or above 0x80 (extended ASCII or UTF-8 bytes) become negative, and passing a negative value that is not EOF is undefined behaviour — some implementations index an internal lookup table with a negative index and crash. Fix: convert char with static_cast<unsigned char> before passing it to these functions so the value is always in the valid range.'},

 {'id':'A23-0-1','cat':'Required · Automated','compiles':True,
  'title':'무효화된(invalidated) 반복자를 사용하지 않는다',
  'title_en':'An iterator that is invalidated shall not be used',
  'bad': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> v{1, 0, 2, 0, 3};
    for (auto it = v.begin(); it != v.end(); ++it) {
        if (*it == 0) v.erase(it);   // erase 가 it 을 무효화 → 이후 ++it/역참조는 미정의
    }
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
int main() {
    std::vector<int> v{1, 0, 2, 0, 3};
    for (auto it = v.begin(); it != v.end(); ) {
        if (*it == 0) it = v.erase(it);   // erase 가 돌려준 유효한 다음 반복자로 갱신
        else ++it;
    }
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';   // 1 2 3
}""",
  'why':'근거: 컨테이너의 erase·insert 나 재할당을 유발하는 연산은 그 위치(또는 이후, 때로 전체)의 반복자·참조·포인터를 무효화하며, 무효화된 반복자를 증가·역참조·비교하는 것은 미정의 동작이다. 영향: 반복 중 erase 후 같은 it 을 계속 쓰면 해제된 위치를 가리켜 원소를 건너뛰거나, 쓰레기를 읽거나, 크래시하는 미묘한 버그가 된다. 대응: 변경 연산이 반환하는 유효한 반복자(it = v.erase(it))로 갱신하거나, 표준 알고리즘(std::remove_if + erase 관용구)을 사용한다.',
  'why_en':'Rationale: a container erase, insert, or a reallocating operation invalidates iterators, references, and pointers at (or after, sometimes all of) that position, and incrementing, dereferencing, or comparing an invalidated iterator is undefined behaviour. Impact: continuing to use the same it after erase during iteration points at a freed position, skipping elements, reading garbage, or crashing — a subtle bug. Fix: update with the valid iterator returned by the modifying operation (it = v.erase(it)) or use standard algorithms (the std::remove_if + erase idiom).'},

 {'id':'A25-4-1','cat':'Required · Automated','compiles':True,
  'title':'정렬/연관 컨테이너의 비교 술어는 엄격 약순서를 만족해야 한다',
  'title_en':'Ordering predicates used with associative containers and sorting algorithms shall adhere to a strict weak ordering relation',
  'bad': r"""#include <iostream>
#include <vector>
#include <algorithm>
struct Item { int x; };
int main() {
    std::vector<Item> v{{5},{2},{8},{2},{1}};
    std::sort(v.begin(), v.end(),
              [](const Item& a, const Item& b){ return a.x <= b.x; });   // <= 위반
    for (auto& i : v) std::cout << i.x << ' ';
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <algorithm>
struct Item { int x; };
int main() {
    std::vector<Item> v{{5},{2},{8},{2},{1}};
    std::sort(v.begin(), v.end(),
              [](const Item& a, const Item& b){ return a.x < b.x; });   // 엄격 약순서
    for (auto& i : v) std::cout << i.x << ' ';
    std::cout << '\n';
}""",
  'why':'근거: std::sort 와 std::map·std::set 은 비교 술어가 엄격 약순서(strict weak ordering)를 만족한다고 가정하며, 그 핵심은 같은 값에 대해 comp(a, a) 가 false 여야 한다는 비반사성이다. 영향: a.x <= b.x 처럼 동치에 true 를 주는 술어는 두 동일 원소에서 a < b 와 b < a 가 동시에 참인 모순을 만들어, 정렬이 범위를 넘어 메모리를 침범하거나(미정의 동작) 연관 컨테이너의 트리 불변식이 깨진다. 대응: 동치에 false 를 돌려주는 < 형태의 술어를 사용하고, 복합 키는 모든 필드에 대해 일관된 약순서를 구성한다.',
  'why_en':'Rationale: std::sort and std::map/std::set assume the comparison predicate satisfies a strict weak ordering, whose core is irreflexivity — comp(a, a) must be false for equal values. Impact: a predicate like a.x <= b.x that returns true for equal values makes both a < b and b < a true for two identical elements, so sorting can run past the range and corrupt memory (undefined behaviour) or break the tree invariant of an associative container. Fix: use a < form predicate that returns false for equal values, and compose a consistent weak ordering over all fields for composite keys.'},

 {'id':'A26-5-1','cat':'Required · Automated','compiles':True,
  'title':'의사난수는 std::rand 가 아닌 <random> 엔진으로 생성한다',
  'title_en':'Pseudorandom numbers shall not be generated using std::rand()',
  'bad': r"""#include <iostream>
#include <cstdlib>
int main() {
    int r = std::rand() % 100;   // % 로 인한 분포 편향 + 낮은 품질
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
#include <random>
int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<int> dist(0, 99);   // 균등 분포 보장
    std::cout << dist(gen) << '\n';
}""",
  'why':'근거: std::rand 는 구현마다 품질·주기가 천차만별이고, rand() % N 방식은 RAND_MAX 가 N 의 배수가 아닐 때 작은 값에 더 높은 확률을 주는 모듈로 편향(modulo bias)을 만든다. 영향: 분포가 균등하지 않으면 시뮬레이션·샘플링 결과가 왜곡되고, 보안 문맥에서는 낮은 엔트로피와 예측 가능성 때문에 토큰·논스가 추측 가능해진다. 대응: <random> 의 엔진(mt19937 등)과 분포(uniform_int_distribution)를 조합해 균등성을 보장하고, 보안 용도는 암호학적 CSPRNG 를 사용한다.',
  'why_en':'Rationale: std::rand varies widely in quality and period across implementations, and the rand() % N approach creates modulo bias — giving small values higher probability when RAND_MAX is not a multiple of N. Impact: a non-uniform distribution skews simulation and sampling results, and in a security context low entropy and predictability make tokens and nonces guessable. Fix: combine a <random> engine (such as mt19937) with a distribution (uniform_int_distribution) to guarantee uniformity, and use a cryptographic CSPRNG for security purposes.'},

 {'id':'A27-0-1','cat':'Required · Non-automated','compiles':True,
  'title':'독립 컴포넌트(네트워크·파일 등)로부터의 입력은 검증한다',
  'title_en':'Inputs from independent components shall be validated',
  'bad': r"""#include <iostream>
#include <vector>
#include <cstddef>
static std::size_t read_size_from_network() { return 1000000000; }   // 외부가 준 거대 값
int main() {
    std::size_t n = read_size_from_network();
    std::vector<int> buf;
    buf.resize(n);   // 외부 크기를 검증 없이 그대로 사용 — 자원 고갈/예외
    std::cout << buf.size() << '\n';
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <cstddef>
static std::size_t read_size_from_network() { return 1000000000; }
int main() {
    constexpr std::size_t kMaxBuf = 4096;
    std::size_t n = read_size_from_network();
    if (n > kMaxBuf) { std::cout << "rejected oversized input\n"; return 1; }   // 경계 검증
    std::vector<int> buf(n);
    std::cout << buf.size() << '\n';
}""",
  'why':'근거: 네트워크·파일·IPC·사용자 입력 등 신뢰할 수 없는 출처의 값은 공격자나 손상된 컴포넌트가 임의로 조작할 수 있으므로, 사용 전에 유효 범위·형식을 검증해야 한다. 영향: 외부가 준 크기를 검증 없이 할당·인덱스로 쓰면 거대한 값으로 메모리를 고갈시키는 서비스 거부나, 음수·과대 값으로 경계를 넘는 접근이 발생한다. 대응: 신뢰 경계에서 입력의 범위·길이·형식을 명시적으로 검증하고, 한도를 벗어나면 안전하게 거부한다.',
  'why_en':'Rationale: values from untrusted sources such as network, file, IPC, or user input can be arbitrarily manipulated by an attacker or a compromised component, so they must be validated for valid range and format before use. Impact: using an externally supplied size for allocation or indexing without validation enables denial of service by exhausting memory with a huge value, or out-of-bounds access from a negative or oversized value. Fix: explicitly validate the range, length, and format of input at the trust boundary and safely reject anything outside the limits.'},

 {'id':'A27-0-4','cat':'Required · Automated','compiles':True,
  'title':'C 스타일 문자열을 사용하지 않는다',
  'title_en':'C-style strings shall not be used',
  'bad': r"""#include <iostream>
#include <cstring>
int main() {
    const char* input = "user-provided";
    char name[8];                  // 고정 버퍼
    std::strcpy(name, input);      // 경계 미검사 — input 이 8바이트 넘으면 오버플로우
    std::cout << name << '\n';
}""",
  'good': r"""#include <iostream>
#include <string>
int main() {
    std::string input = "user-provided";
    std::string name = input;      // 길이에 맞춰 동적 관리 — 오버플로우 불가
    std::cout << name << '\n';
}""",
  'why':'근거: C 스타일 문자열(char 배열 + 널 종료)은 길이를 별도로 추적하지 않아, 복사·연결 시 대상 버퍼 크기를 사람이 직접 맞춰야 하고 널 종료를 깜빡하면 읽기가 버퍼를 넘어간다. 영향: strcpy·strcat 같은 경계 없는 연산은 입력이 버퍼보다 길면 인접 메모리를 덮어쓰는 버퍼 오버플로우를 일으켜, 크래시와 코드 실행 공격의 통로가 된다. 대응: 문자열은 길이를 스스로 관리하고 경계를 넘지 않는 std::string·std::string_view 로 다룬다.',
  'why_en':'Rationale: a C-style string (char array plus null terminator) does not track its length separately, so on copy or concatenation a human must match the destination buffer size, and forgetting the null terminator makes reads run past the buffer. Impact: unbounded operations like strcpy and strcat overwrite adjacent memory when input exceeds the buffer — a buffer overflow that opens a path to crashes and code-execution attacks. Fix: handle strings with std::string and std::string_view, which manage length themselves and do not run past bounds.'},

 {'id':'M10-1-1','cat':'Advisory · Automated','compiles':True,
  'title':'비인터페이스 클래스를 둘 이상 상속하지 않는다',
  'title_en':'Classes should not be derived from more than one base class that is not an interface class',
  'bad': r"""#include <iostream>
struct Engine { void run() { std::cout << "run\n"; } int rpm = 0; };   // 구현+데이터
struct Logger { void log() { std::cout << "log\n"; } int level = 0; };  // 구현+데이터
struct Car : public Engine, public Logger {};   // 다중 구현 상속 — 결합·모호성
int main() { Car c; c.run(); c.log(); }""",
  'good': r"""#include <iostream>
struct Engine { void run() { std::cout << "run\n"; } int rpm = 0; };
struct ILogger { virtual void log() = 0; virtual ~ILogger() = default; };  // 순수 인터페이스
struct Car : public ILogger {       // 인터페이스만 상속
    Engine engine_;                 // 구현은 구성(composition)으로 보유
    void run() { engine_.run(); }
    void log() override { std::cout << "log\n"; }
};
int main() { Car c; c.run(); c.log(); }""",
  'why':'근거: 데이터·구현을 가진 클래스를 둘 이상 상속하면, 두 기반의 멤버·이름이 한 파생 클래스에 합쳐져 이름 모호성과 강한 결합이 생기고, 공통 조상이 있으면 다이아몬드 문제로 기반 서브오브젝트가 중복된다. 영향: 어떤 기반의 멤버인지 모호해 잘못된 멤버를 참조하거나, 한 기반의 변경이 무관한 기능까지 깨뜨리고, 초기화·레이아웃이 복잡해져 추론이 어렵다. 대응: 다중 상속은 데이터 없는 순수 가상 인터페이스에 한정하고, 구현 재사용은 멤버로 보유하는 구성(composition)으로 해결한다.',
  'why_en':'Rationale: deriving from more than one class that carries data and implementation merges both bases members and names into one derived class, creating name ambiguity and tight coupling, and with a common ancestor the diamond problem duplicates the base subobject. Impact: it becomes ambiguous which base a member belongs to (referencing the wrong one), a change in one base breaks unrelated functionality, and initialization and layout grow complex and hard to reason about. Fix: limit multiple inheritance to data-free pure-virtual interfaces and reuse implementation through composition by holding members.'},

 {'id':'M10-1-2','cat':'Required · Automated','compiles':True,
  'title':'가상 기반 클래스는 데이터 없는 추상 인터페이스로만 둔다',
  'title_en':'A base class shall only be declared virtual if it is used in a diamond hierarchy',
  'bad': r"""#include <iostream>
struct Base { int data_ = 0; };          // 데이터를 가진 클래스를
struct D : virtual public Base {          // 가상 기반으로 — 초기화 책임이 최파생으로 이동
    void set() { data_ = 1; }
};
int main() { D d; d.set(); std::cout << d.data_ << '\n'; }""",
  'good': r"""#include <iostream>
struct IBase {                            // 데이터 없는 추상 인터페이스
    virtual void f() = 0;
    virtual ~IBase() = default;
};
struct D : virtual public IBase {
    void f() override { std::cout << "f\n"; }
};
int main() { D d; d.f(); }""",
  'why':'근거: 가상 상속에서는 가상 기반 서브오브젝트가 최종 파생 클래스에 의해 한 번만 생성·초기화되는데, 그 기반이 데이터 멤버를 가지면 초기화 책임과 레이아웃이 계층 전체로 퍼져 복잡해진다. 영향: 데이터를 가진 가상 기반은 어느 생성자가 그 멤버를 초기화하는지 추적하기 어렵게 만들고, 가상 기반 포인터 조정(virtual base offset)으로 성능·디버깅 부담이 커진다. 대응: 가상 기반(다이아몬드 구조의 공유 기반)은 데이터 없는 순수 가상 인터페이스로 한정하고, 공유해야 할 상태는 별도 설계로 분리한다.',
  'why_en':'Rationale: in virtual inheritance the virtual base subobject is constructed and initialized exactly once by the most-derived class, and if that base has data members the initialization responsibility and layout spread across the whole hierarchy, growing complex. Impact: a virtual base with data makes it hard to track which constructor initializes those members, and virtual-base pointer adjustment adds performance and debugging burden. Fix: limit a virtual base (the shared base of a diamond) to a data-free pure-virtual interface, and separate any shared state through a different design.'},

 {'id':'M12-1-1','cat':'Required · Automated','compiles':True,
  'title':'생성자/소멸자 안에서 객체의 동적 타입에 의존하지 않는다',
  'title_en':'An object dynamic type shall not be used from the body of its constructor or destructor',
  'bad': r"""#include <iostream>
struct Base {
    Base();                       // 정의는 Derived 가 완전해진 뒤로
    virtual ~Base() = default;
};
struct Derived : Base { void f() { std::cout << "f\n"; } };
Base::Base() {
    // 생성 중 동적 타입은 Base — dynamic_cast 가 파생(Derived)을 인식하지 못함
    if (dynamic_cast<Derived*>(this) == nullptr)
        std::cout << "ctor sees Base only (not Derived)\n";
}
int main() { Derived d; }   // Base() 는 d 를 Derived 로 보지 못함""",
  'good': r"""#include <iostream>
struct Base {
    Base() = default;
    virtual ~Base() = default;
};
struct Derived : Base {
    void f() { std::cout << "f\n"; }
    void start() { f(); }   // 생성 완료 후 별도 단계에서 파생 동작 호출
};
int main() { Derived d; d.start(); }""",
  'why':'근거: 객체가 생성·소멸되는 동안에는 동적 타입이 현재 실행 중인 생성자/소멸자의 클래스로 고정되므로, 그 안에서의 dynamic_cast 나 가상 디스패치는 아직(또는 이미) 존재하지 않는 파생 부분을 인식하지 못한다. 영향: 생성자에서 dynamic_cast<Derived*>(this) 가 nullptr 을 돌려주거나 가상 호출이 기반 버전으로 가, 파생 초기화를 기대한 코드가 조용히 잘못 동작한다. 대응: 파생 타입에 의존하는 동작은 생성이 완전히 끝난 뒤 별도의 초기화 메서드(start() 등)에서 수행한다.',
  'why_en':'Rationale: while an object is being constructed or destroyed, its dynamic type is fixed to the class of the currently running constructor/destructor, so a dynamic_cast or virtual dispatch inside does not recognize the derived part that does not yet (or no longer) exist. Impact: a dynamic_cast<Derived*>(this) in a constructor returns nullptr or a virtual call goes to the base version, so code expecting derived initialization silently misbehaves. Fix: perform behaviour that depends on the derived type in a separate initialization method (such as start()) after construction fully completes.'},

 {'id':'M15-1-2','cat':'Required · Automated','compiles':True,
  'title':'NULL(널 포인터 상수)을 throw 하지 않는다',
  'title_en':'NULL shall not be thrown explicitly',
  'bad': r"""#include <iostream>
struct ResourceError {};
int main() {
    try {
        throw NULL;   // 포인터가 아니라 정수 0 으로 해석되어 던져짐
    }
    catch (ResourceError*) { std::cout << "as pointer\n"; }   // 잡지 못함
    catch (...) { std::cout << "caught as integer, not a pointer\n"; }   // 이쪽으로 감
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
int main() {
    try {
        throw std::runtime_error("null result");   // 의미 있는 예외 객체
    }
    catch (const std::exception& e) { std::cout << e.what() << '\n'; }
}""",
  'why':'근거: NULL 은 널 포인터처럼 보이지만 실제로는 정수 상수(0 또는 구현정의 정수형)라, throw NULL 은 포인터가 아니라 정수 값을 던진다. 영향: 던진 측은 널 포인터 예외를 의도했는데 catch(SomeType*) 같은 포인터 핸들러는 이를 잡지 못하고, 정수 핸들러나 catch(...) 로만 잡혀 의도와 다른 처리가 되거나 잡히지 않아 terminate 로 간다. 대응: 오류는 std::exception 에서 파생된 의미 있는 예외 객체로 던져, 타입과 메시지로 일관되게 처리되게 한다.',
  'why_en':'Rationale: NULL looks like a null pointer but is actually an integer constant (0 or an implementation-defined integer type), so throw NULL throws an integer value, not a pointer. Impact: the thrower intends a null-pointer exception, but a pointer handler like catch(SomeType*) does not catch it — only an integer handler or catch(...) does — leading to handling that differs from intent or going uncaught to terminate. Fix: throw a meaningful exception object derived from std::exception so it is handled consistently by type and message.'},

 {'id':'M15-3-4','cat':'Required · Automated','compiles':True,
  'title':'발생할 수 있는 모든 예외는 어딘가에서 catch 되어야 한다',
  'title_en':'Each exception explicitly thrown in the code shall have a handler of a compatible type',
  'bad': r"""#include <stdexcept>
static void run(int argc) { if (argc >= 0) throw std::runtime_error("boom"); }   // 가드: 항상 참
int main(int argc, char**) {
    run(argc);   // 어떤 try 로도 감싸지 않음 → 예외가 main 밖으로 → std::terminate
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
static void run() { throw std::runtime_error("boom"); }
int main() {
    try { run(); }
    catch (const std::exception& e) { std::cout << "handled: " << e.what() << '\n'; return 1; }
    catch (...) { std::cout << "unknown error\n"; return 1; }
}""",
  'why':'근거: 던져진 예외가 호환되는 타입의 핸들러를 만나지 못하고 호출 스택을 끝까지(즉 main 밖으로) 빠져나가면, 표준은 std::terminate 를 호출하도록 규정한다. 영향: 처리되지 않은 예외는 진단 메시지 없이 프로그램을 비정상 종료시키고, 스택 풀기 수행 여부조차 구현 정의라 소멸자가 안 불려 자원이 남을 수 있다. 대응: 최상위 진입점(main 과 각 스레드 함수)에서 std::exception 과 catch(...) 로 모든 예외를 포착해 로깅·정의된 종료 코드로 처리한다.',
  'why_en':'Rationale: if a thrown exception finds no handler of a compatible type and escapes the call stack all the way out of main, the standard mandates a call to std::terminate. Impact: an unhandled exception aborts the program with no diagnostic, and whether stack unwinding even runs is implementation-defined, so destructors may not be called and resources can leak. Fix: at the top-level entry points (main and each thread function) catch all exceptions with std::exception and catch(...) and handle them with logging and a defined exit code.'},

 {'id':'M15-3-6','cat':'Required · Automated','compiles':True,
  'title':'catch 핸들러는 가장 파생된 것부터 기본 순으로 배치한다',
  'title_en':'Where multiple handlers are provided, they shall be ordered most-derived to base class',
  'bad': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::logic_error("bad arg"); }
    catch (const std::exception& e) {        // 기반 먼저 — 파생도 여기서 잡힘
        std::cout << "generic: " << e.what() << '\n';
    }
    catch (const std::logic_error& e) {      // 도달 불가 — 컴파일러 경고
        std::cout << "specific: " << e.what() << '\n';
    }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::logic_error("bad arg"); }
    catch (const std::logic_error& e) {      // 파생(구체적) 먼저
        std::cout << "specific: " << e.what() << '\n';
    }
    catch (const std::exception& e) {        // 기반(일반) 나중
        std::cout << "generic: " << e.what() << '\n';
    }
}""",
  'why':'근거: catch 핸들러는 선언된 순서대로 검사되며 던져진 예외와 호환되는 첫 핸들러가 선택된다(가상 디스패치가 아니라 순차 매칭). 영향: 기반 클래스 핸들러를 먼저 두면 모든 파생 예외가 거기서 잡혀, 뒤에 둔 더 구체적인 핸들러는 영영 도달하지 못해 의도한 세분화 처리가 사라진다. 대응: 핸들러를 가장 파생된 타입부터 기반 타입 순으로 배치해 구체적 예외가 먼저 잡히게 한다.',
  'why_en':'Rationale: catch handlers are examined in declaration order and the first one compatible with the thrown exception is chosen (sequential matching, not virtual dispatch). Impact: placing a base-class handler first catches all derived exceptions there, so a more specific handler placed afterwards is never reached and the intended fine-grained handling is lost. Fix: order handlers from the most derived type down to the base type so specific exceptions are caught first.'},

 {'id':'M15-3-7','cat':'Required · Automated',
  'title':'catch-all(...) 핸들러는 마지막에 둔다',
  'title_en':'Where multiple handlers are provided, any ellipsis (catch-all) handler shall occur last',
  'bad': r"""    try { f(); }
    catch (...) { ... }                       // catch-all 이 먼저 — 모든 예외를 흡수
    catch (const std::exception& e) { ... }   // 도달 불가
    // gcc 는 이를 하드 에러로 거부: "'...' handler must be the last handler" — 컴파일 불가""",
  'good': r"""    try { f(); }
    catch (const std::exception& e) { ... }   // 구체 핸들러 먼저
    catch (...) { ... }                       // catch-all 은 마지막""",
  'why':'근거: catch(...) 는 모든 타입의 예외와 호환되므로, 핸들러 목록에서 그 앞의 어떤 구체 핸들러보다 먼저 두면 모든 예외를 가장 먼저 흡수해 버린다. 영향: catch-all 을 앞에 두면 뒤따르는 std::exception 등 구체 핸들러가 도달 불가가 되어, 타입별 정보를 활용한 세분화된 처리가 모두 무력화된다. 대응: 구체적인 타입 핸들러들을 먼저 나열하고, 마지막에 남은 모든 예외를 위한 catch(...) 를 둔다.',
  'why_en':'Rationale: catch(...) is compatible with exceptions of every type, so placing it before any specific handler in the list makes it absorb all exceptions first. Impact: a leading catch-all renders the following specific handlers (like std::exception) unreachable, disabling all fine-grained handling that uses type information. Fix: list specific-type handlers first and place catch(...) last for any remaining exceptions.'},

 {'id':'M16-0-6','cat':'Required · Automated','compiles':True,
  'title':'함수형 매크로의 매개변수와 전체를 괄호로 감싼다',
  'title_en':'In the definition of a function-like macro, each instance of a parameter shall be enclosed in parentheses',
  'bad': r"""#include <iostream>
#define DOUBLE(x) x + x   // 매개변수·전체에 괄호 없음
int main() {
    int a = 3;
    int r = DOUBLE(a) * 2;   // 3 + 3 * 2 = 9 (의도는 (3+3)*2 = 12)
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
#define DOUBLE(x) ((x) + (x))   // 매개변수와 전체를 괄호로 보호
int main() {
    int a = 3;
    int r = DOUBLE(a) * 2;   // ((3)+(3)) * 2 = 12
    std::cout << r << '\n';
}""",
  'why':'근거: 함수형 매크로는 토큰을 그대로 치환할 뿐 함수처럼 인자를 평가하지 않으므로, 매개변수와 전체 식을 괄호로 보호하지 않으면 호출 문맥의 연산자 우선순위가 치환 결과에 끼어든다. 영향: DOUBLE(a) * 2 가 a + a * 2 로 전개되어 의도한 (a+a)*2 와 다른 값을 내는 등, 인자가 복합 식일 때 조용한 계산 오류가 발생한다. 대응: 가능하면 매크로 대신 inline 함수·템플릿을 쓰고, 불가피한 함수형 매크로는 각 매개변수 사용처와 전체 본문을 괄호로 감싼다.',
  'why_en':'Rationale: a function-like macro merely substitutes tokens rather than evaluating arguments like a function, so without parenthesizing the parameters and the whole expression, the operator precedence of the call context bleeds into the substituted result. Impact: DOUBLE(a) * 2 expands to a + a * 2, producing a value different from the intended (a+a)*2 — a silent computation error when the argument is a compound expression. Fix: prefer inline functions or templates over macros, and for unavoidable function-like macros wrap each parameter use and the whole body in parentheses.'},

 {'id':'M16-3-2','cat':'Advisory · Automated','compiles':True,
  'title':'전처리기 # 와 ## 연산자를 사용하지 않는다',
  'title_en':'The # and ## operators should not be used',
  'bad': r"""#include <iostream>
#define MAKE(name) int value_##name = 0   // ## 토큰 붙이기 — 디버깅·검색 어려움
int main() {
    MAKE(alpha);   // int value_alpha = 0; 로 전개 — grep 으로 찾기 힘든 이름 생성
    std::cout << value_alpha << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int value_alpha = 0;   // 명시적 코드 — 이름이 그대로 드러나 검색·디버깅 용이
    std::cout << value_alpha << '\n';
}""",
  'why':'근거: 전처리기 # (문자열화)와 ## (토큰 결합)는 평가·치환 순서 규칙이 까다롭고, 결과로 만들어진 식별자나 문자열이 소스 코드에 그대로 나타나지 않는다. 영향: ## 로 합성한 이름(value_##name)은 grep·IDE 검색으로 찾기 어렵고, 디버거가 매크로 전개 후 코드를 보여주지 못해 추적이 힘들며, 중첩 매크로에서는 전개 결과가 직관과 달라 미묘한 버그가 생긴다. 대응: 가능한 한 # / ## 를 피하고 명시적 코드나 타입 안전한 템플릿·constexpr 로 대체하며, 불가피하면 한 곳에 격리해 문서화한다.',
  'why_en':'Rationale: the preprocessor # (stringize) and ## (token paste) operators have tricky evaluation and substitution ordering rules, and the resulting identifiers or strings do not appear literally in the source. Impact: a name synthesized with ## (value_##name) is hard to find with grep or IDE search, debuggers cannot show post-expansion code, and in nested macros the expansion result differs from intuition, creating subtle bugs. Fix: avoid # / ## where possible, replacing them with explicit code or type-safe templates and constexpr, and isolate and document any unavoidable use.'},

 {'id':'M17-0-5','cat':'Required · Automated','compiles':True,
  'title':'setjmp / longjmp 를 사용하지 않는다',
  'title_en':'The setjmp macro and the longjmp function shall not be used',
  'bad': r"""#include <csetjmp>
#include <iostream>
static std::jmp_buf env;
struct Guard { ~Guard() { std::cout << "cleanup\n"; } };   // longjmp 시 호출 안 됨
static void work() {
    Guard g;
    std::longjmp(env, 1);   // g 의 소멸자를 건너뛰고 점프 — 자원 누수
}
int main() {
    if (setjmp(env) == 0) work();
    else std::cout << "recovered (but cleanup skipped)\n";
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Guard { ~Guard() { std::cout << "cleanup\n"; } };
static void work() {
    Guard g;
    throw std::runtime_error("fail");   // 예외 — 스택 풀기로 g 정상 소멸
}
int main() {
    try { work(); }
    catch (const std::exception&) { std::cout << "recovered\n"; }
}""",
  'why':'근거: longjmp 는 C 의 비지역 점프로, 스택을 되감을 때 그 사이에 살아 있던 C++ 자동 객체의 소멸자를 전혀 호출하지 않으며, 비trivial 객체가 있는 스코프를 건너뛰는 longjmp 자체가 미정의 동작이다. 영향: RAII 로 잠금·메모리·파일을 관리하던 객체가 정리되지 않아 누수·교착이 발생하고, C++ 객체 모델과 예외 안전성이 깨진다. 대응: 비지역 제어 이동과 오류 복구는 예외 처리(throw/catch)로 구현해 스택 풀기 중 소멸자가 항상 실행되게 한다.',
  'why_en':'Rationale: longjmp is C non-local jump that, when rewinding the stack, does not call destructors of any C++ automatic objects alive in between, and a longjmp that skips a scope containing non-trivial objects is itself undefined behaviour. Impact: objects managing locks, memory, or files via RAII are not cleaned up, causing leaks or deadlock and breaking the C++ object model and exception safety. Fix: implement non-local control transfer and error recovery with exception handling (throw/catch) so destructors always run during unwinding.'},

 {'id':'M18-0-3','cat':'Required · Automated','compiles':True,
  'title':'<cstdlib> 의 abort/exit/getenv/system 을 사용하지 않는다',
  'title_en':'The library functions abort, exit, getenv and system from <cstdlib> shall not be used',
  'bad': r"""#include <cstdlib>
#include <iostream>
static int g_runtime_false = 0;   // 검증 시 실제 호출은 회피(패턴만 시연)
int main() {
    if (g_runtime_false) {
        std::system("rm -rf /tmp/x");   // 셸 인젝션·이식성 위험
        std::exit(1);                    // 스택 풀기·소멸자 건너뜀
    }
    std::cout << "shows forbidden calls, guarded\n";
}""",
  'good': r"""#include <iostream>
enum class Status { Ok, Error };
static Status run() { return Status::Error; }
int main() {
    Status s = run();
    if (s == Status::Error) { std::cout << "error path\n"; return 1; }   // 정상 반환 경로
    std::cout << "ok\n";
    return 0;
}""",
  'why':'근거: std::system 은 인자를 셸에 넘겨 실행하므로 입력이 섞이면 셸 인젝션 취약점이 되고 동작이 환경(셸·OS)에 의존하며, std::exit/abort 는 스택 풀기 없이 프로세스를 끝내 활성 객체의 소멸자를 건너뛴다. 영향: system 으로 외부 명령을 부르면 보안·이식성이 무너지고, exit/abort 로 갑자기 종료하면 열린 파일·잠금·버퍼가 정리되지 않아 데이터 손상·누수가 남는다. 대응: 외부 작업은 셸을 거치지 않는 안전한 내부 API 로, 종료는 예외나 반환 코드로 정상 흐름을 통해 처리한다.',
  'why_en':'Rationale: std::system passes its argument to a shell, so mixed-in input becomes a shell-injection vulnerability and behaviour depends on the environment (shell, OS), while std::exit/abort end the process without stack unwinding, skipping destructors of active objects. Impact: calling external commands via system breaks security and portability, and abruptly terminating with exit/abort leaves open files, locks, and buffers uncleaned, causing corruption and leaks. Fix: perform external work through safe internal APIs that do not go through a shell, and handle termination via exceptions or return codes through the normal flow.'},

 {'id':'M18-0-5','cat':'Required · Automated','compiles':True,
  'title':'<cstring> 의 경계 없는(unbounded) 함수를 사용하지 않는다',
  'title_en':'The unbounded functions of library <cstring> shall not be used',
  'bad': r"""#include <cstring>
#include <iostream>
int main() {
    char dst[32];
    const char* src = "fits here";
    std::strcpy(dst, src);   // 경계 없는 복사 — src 가 dst 보다 길면 오버플로우
    std::cout << dst << '\n';   // (여기선 들어맞지만 strcpy 자체가 검사 없는 위험 API)
}""",
  'good': r"""#include <string>
#include <iostream>
int main() {
    std::string dst = "fits here";   // 길이를 자동 관리 — 경계 초과 불가
    std::cout << dst << '\n';
}""",
  'why':'근거: strcpy·strcat·strlen·gets 등 <cstring> 의 경계 없는 함수는 대상 버퍼의 크기를 인자로 받지 않아, 원본이 대상보다 길어도 검사 없이 계속 기록·탐색한다. 영향: 입력 길이를 통제할 수 없는 상황에서 이런 함수를 쓰면 버퍼 오버플로우로 인접 메모리·반환 주소가 덮여 크래시·코드 실행 공격으로 이어지며, 이는 가장 흔한 메모리 취약점 부류다. 대응: 길이를 스스로 관리하는 std::string 을 쓰거나, 불가피하면 크기를 받는 경계 있는 연산(strncpy 의 올바른 사용·std::snprintf·std::copy_n)으로 대체한다.',
  'why_en':'Rationale: unbounded functions in <cstring> such as strcpy, strcat, strlen, and gets take no destination buffer size, so they keep writing or scanning unchecked even when the source is longer than the destination. Impact: using them where input length is not controlled causes buffer overflows that overwrite adjacent memory and return addresses, leading to crashes and code-execution attacks — the most common class of memory vulnerability. Fix: use std::string, which manages length itself, or when unavoidable use size-taking bounded operations (correct use of strncpy, std::snprintf, std::copy_n).'},

 {'id':'M18-7-1','cat':'Required · Automated','compiles':True,
  'title':'<csignal> 의 시그널 처리를 사용하지 않는다',
  'title_en':'The signal handling facilities of <csignal> shall not be used',
  'bad': r"""#include <csignal>
#include <iostream>
static volatile std::sig_atomic_t g_stop = 0;
extern "C" void on_sigint(int) { g_stop = 1; }   // 비동기·구현정의 제약이 큰 핸들러
int main() {
    std::signal(SIGINT, on_sigint);   // 시그널 기반 제어 — 안전필수에 부적합
    std::cout << "signal handler installed\n";
}""",
  'good': r"""#include <iostream>
#include <atomic>
static std::atomic<bool> g_stop{false};
static bool stop_requested() { return g_stop.load(); }
int main() {
    // 결정적 이벤트/플래그 폴링으로 종료 요청 처리(여기선 즉시 종료)
    int steps = 0;
    while (!stop_requested() && steps < 3) { ++steps; }
    std::cout << "cooperative loop done, steps=" << steps << '\n';
}""",
  'why':'근거: 시그널은 프로그램 흐름과 비동기적으로 끼어들고, 핸들러 안에서 호출 가능한 함수가 async-signal-safe 한 극소수로 제한되며 그 동작 상당 부분이 구현정의다. 영향: 핸들러에서 비안전 함수(동적 할당·예외·비POD 입출력)를 부르면 락·힙이 일관되지 않은 순간에 진입해 교착·손상·크래시가 나고, 제어 흐름이 비결정적이 되어 안전필수 시스템의 검증을 어렵게 한다. 대응: 종료·중단 요청 같은 비동기 이벤트는 시그널 대신 결정적 메커니즘(원자적 플래그 폴링, 이벤트 루프, OS 의 동기적 통지)으로 처리한다.',
  'why_en':'Rationale: signals interrupt program flow asynchronously, the set of functions callable in a handler is restricted to a tiny async-signal-safe subset, and much of the behaviour is implementation-defined. Impact: calling unsafe functions (dynamic allocation, exceptions, non-POD I/O) in a handler enters while locks or the heap are inconsistent, causing deadlock, corruption, or crashes, and makes control flow nondeterministic, hindering verification of safety-critical systems. Fix: handle asynchronous events like stop/abort requests with deterministic mechanisms instead of signals — atomic-flag polling, an event loop, or synchronous OS notifications.'},

 {'id':'M19-3-1','cat':'Required · Automated','compiles':True,
  'title':'errno 를 직접 사용하지 않는다',
  'title_en':'The error indicator errno shall not be used',
  'bad': r"""#include <cerrno>
#include <cstdlib>
#include <iostream>
int main() {
    errno = 0;
    double v = std::strtod("not-a-number", nullptr);   // 실패 시 errno 설정
    if (errno != 0) std::cout << "conversion failed via errno\n";   // 전역 errno 의존
    else std::cout << "v=" << v << '\n';
}""",
  'good': r"""#include <iostream>
#include <optional>
#include <string>
static std::optional<double> parse_double(const std::string& s) {
    try { std::size_t pos; double v = std::stod(s, &pos);
          return pos == s.size() ? std::optional<double>(v) : std::nullopt; }
    catch (...) { return std::nullopt; }
}
int main() {
    auto r = parse_double("not-a-number");
    std::cout << (r ? "ok" : "conversion failed") << '\n';   // 결과에 오류가 함께 담김
}""",
  'why':'근거: errno 는 함수가 오류를 알리려고 설정하는 전역(스레드 로컬) 상태라, 오류 발생과 검사 사이가 떨어져 있고 그 사이 다른 호출이 errno 를 덮어쓸 수 있으며 사용 전 0 으로 초기화하는 규약을 사람이 지켜야 한다. 영향: errno 검사를 빠뜨리거나 초기화를 잊으면 오류가 조용히 무시되거나 엉뚱한 호출의 오류로 오인되어, 실패 처리 로직이 신뢰할 수 없게 된다. 대응: 오류를 반환값·예외·std::optional·std::expected 처럼 결과와 함께 명시적으로 전달하는 인터페이스를 사용해, 오류 검사가 호출 지점에 묶이게 한다.',
  'why_en':'Rationale: errno is a global (thread-local) state that functions set to signal errors, so the error and its check are separated, another call in between can overwrite errno, and the convention of zeroing it before use must be upheld by a human. Impact: forgetting to check errno or to reset it lets errors be silently ignored or mistaken for the error of an unrelated call, making failure-handling logic unreliable. Fix: use interfaces that carry the error together with the result explicitly — return values, exceptions, std::optional, or std::expected — so the error check is bound to the call site.'},
]
