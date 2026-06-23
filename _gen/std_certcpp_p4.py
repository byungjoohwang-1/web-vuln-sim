# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트4: 공식 사이트 대조로 보강한 누락 규칙) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 cmu-sei.github.io 공식 목록 대조로 확인, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17 -pthread` 기준.
단, ill-formed(컴파일 에러가 정상)·TU 간·언어연결 룰은 초점 스니펫으로 유지."""

RULES = [
 {'id':'DCL52-CPP','cat':'DCL · Rule · L1',
  'title':'참조(reference) 타입에 const/volatile 한정을 붙이지 않는다',
  'title_en':'Never qualify a reference type with const or volatile',
  'bad': r"""int x = 0;
int& const r = x;   // 참조는 본래 재바인딩 불가 — 참조에 const 는 무의미하며 컴파일 에러
int& volatile vr = x;   // 마찬가지로 부적격(ill-formed)""",
  'good': r"""int x = 0;
int& r = x;          // 참조 자체엔 cv 한정 불필요
const int& cr = x;   // 한정은 가리키는 '대상' 타입에 적용
volatile int& vr = x;""",
  'why':'근거: 참조는 초기화 후 다른 객체를 가리키도록 재바인딩될 수 없으므로 참조 자체는 이미 변경 불가이고, 거기에 다시 const/volatile 을 붙이는 것은 의미가 없어 표준이 부적격(ill-formed)으로 규정한다. 영향: 의도(가리키는 대상을 const 로 보호)와 표기가 어긋나, 컴파일 에러가 나거나 typedef 를 거쳐 조용히 무시되면서 오해를 부른다. 대응: cv 한정은 참조가 가리키는 대상 타입(const int&)에 적용한다.',
  'why_en':'Rationale: a reference cannot be rebound to another object after initialization, so the reference itself is already immutable, and adding const/volatile to it is meaningless — the standard makes it ill-formed. Impact: intent (protecting the referent as const) and notation diverge, causing a compile error or, when laundered through a typedef, being silently ignored and misleading readers. Fix: apply cv-qualification to the referent type (const int&).'},

 {'id':'DCL55-CPP','cat':'DCL · Rule · L1','compiles':True,
  'title':'신뢰 경계 너머로 객체를 전달할 때 패딩으로 정보가 유출되지 않게 한다',
  'title_en':'Avoid information leakage when passing a class object across a trust boundary',
  'bad': r"""#include <iostream>
#include <cstring>
struct Msg { char tag; int val; };   // tag 와 val 사이에 패딩 바이트 존재
int main() {
    char prev[sizeof(Msg)];
    std::memset(prev, 0xAB, sizeof prev);   // 이전에 쓰던 민감 데이터를 흉내
    Msg m;
    std::memcpy(&m, prev, sizeof m);        // 패딩에 0xAB 잔존
    m.tag = 1; m.val = 2;                   // 멤버만 덮음 — 패딩은 그대로
    const unsigned char* raw = reinterpret_cast<const unsigned char*>(&m);
    for (std::size_t i = 0; i < sizeof m; ++i) std::printf("%02X ", raw[i]);  // 패딩에 AB 유출
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstring>
struct Msg { char tag; int val; };
int main() {
    Msg m{};                 // 값 초기화 — 패딩 포함 전체가 0
    m.tag = 1; m.val = 2;
    const unsigned char* raw = reinterpret_cast<const unsigned char*>(&m);
    for (std::size_t i = 0; i < sizeof m; ++i) std::printf("%02X ", raw[i]);
    std::cout << '\n';       // 패딩은 00 — 잔존 데이터 없음
}""",
  'why':'근거: 구조체 멤버 사이에는 정렬을 맞추기 위한 패딩 바이트가 들어가는데, 멤버만 대입하면 이 패딩은 초기화되지 않은 채(이전에 그 메모리에 있던 값) 남는다. 영향: sizeof 만큼 통째로 직렬화해 소켓·파일·다른 프로세스 등 신뢰 경계 밖으로 보내면, 패딩에 남은 스택·힙 잔존물(키·포인터 등)이 함께 유출된다. 대응: 경계를 넘는 객체는 값 초기화({})로 패딩까지 0 으로 만든 뒤 멤버를 채우거나, 패딩 없는 명시적 직렬화 포맷을 사용한다.',
  'why_en':'Rationale: padding bytes are inserted between struct members for alignment, and assigning only the members leaves that padding uninitialized — holding whatever was previously in that memory. Impact: serializing the whole object by sizeof and sending it across a trust boundary (socket, file, another process) leaks the leftover stack/heap contents (keys, pointers) sitting in the padding. Fix: value-initialize ({}) objects that cross a boundary so padding is zeroed before filling members, or use an explicit padding-free serialization format.'},

 {'id':'DCL56-CPP','cat':'DCL · Rule · L2',
  'title':'정적 객체 초기화 중 순환 의존을 만들지 않는다',
  'title_en':'Avoid cycles during initialization of static objects',
  'bad': r"""// a.cpp
extern int b;
int a = b + 1;   // 다른 TU 의 b 에 의존
// b.cpp
extern int a;
int b = a + 1;   // 초기화 순서가 TU 간에 미정 — 한쪽은 0 을 읽음""",
  'good': r"""// 지연 초기화로 순서를 강제 — 최초 호출 시 정확히 한 번 초기화
int& a();
int& b() { static int v = 1; return v; }
int& a() { static int v = b() + 1; return v; }   // a() 호출이 b() 를 먼저 보장""",
  'why':'근거: 서로 다른 번역단위의 네임스페이스 범위 정적 객체들은 초기화 순서가 표준으로 정해지지 않아(미지정), 한 객체가 아직 초기화 안 된 다른 객체의 값에 의존하면 0(영초기화 상태)을 읽을 수 있다. 영향: a, b 가 서로의 값으로 초기화되면 빌드·링크 순서에 따라 결과가 달라지는 비결정적 버그가 되어 재현이 어렵다. 대응: 전역 의존 대신 함수 지역 static(최초 사용 시 초기화)으로 감싸 호출이 의존 순서를 강제하게 한다.',
  'why_en':'Rationale: namespace-scope static objects in different translation units have no standardized initialization order (unspecified), so one that depends on another not-yet-initialized object may read 0 (the zero-initialized state). Impact: if a and b initialize from each other, the result varies with build/link order — a nondeterministic bug that is hard to reproduce. Fix: wrap dependencies in function-local statics (initialized on first use) so calls enforce the dependency order instead of relying on globals.'},

 {'id':'EXP56-CPP','cat':'EXP · Rule · L1',
  'title':'언어 연결(language linkage)이 일치하지 않는 함수 포인터로 호출하지 않는다',
  'title_en':'Do not call a function with a mismatched language linkage',
  'bad': r"""extern "C" void register_cb(void (*cb)());   // C 언어 연결의 콜백을 기대
void cpp_cb();                                  // 기본 C++ 언어 연결
// C 연결 포인터 자리에 C++ 연결 함수 전달 — 호출 규약 불일치(부적격)
register_cb(cpp_cb);""",
  'good': r"""extern "C" void register_cb(void (*cb)());
extern "C" void c_cb();    // 콜백을 C 언어 연결로 선언
register_cb(c_cb);         // 연결 일치""",
  'why':'근거: 함수 타입의 언어 연결(extern "C" 대 C++)은 타입의 일부이며, 일부 ABI 에서는 연결에 따라 호출 규약·이름 맞춤이 달라진다. 영향: C 연결을 기대하는 자리에 C++ 연결 함수를 넘기면 호출 측과 피호출 측의 규약이 어긋나 인자 전달·스택 정리가 깨지는 미정의 동작이 될 수 있다. 대응: 경계를 넘나드는 콜백은 호출 측이 기대하는 언어 연결(보통 extern "C")로 선언해 연결을 일치시킨다.',
  'why_en':'Rationale: the language linkage of a function type (extern "C" vs C++) is part of the type, and on some ABIs the calling convention or name mangling differs by linkage. Impact: passing a C++-linkage function where C linkage is expected can mismatch the conventions of caller and callee, breaking argument passing or stack cleanup — undefined behaviour. Fix: declare callbacks that cross boundaries with the language linkage the caller expects (usually extern "C") so the linkage matches.'},

 {'id':'EXP58-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'va_start 에 올바른 타입의 객체를 전달한다',
  'title_en':'Pass an object of the correct type to va_start',
  'bad': r"""#include <cstdarg>
#include <iostream>
#include <string>
// va_start 의 마지막 고정 매개변수가 참조형 — 미정의 동작
static void log(std::string& last, ...) {
    va_list ap; va_start(ap, last);   // last 가 참조형 → UB
    va_end(ap);
    std::cout << last << '\n';
}
int main() { std::string s = "tag"; log(s); }""",
  'good': r"""#include <cstdarg>
#include <iostream>
// 마지막 고정 매개변수를 승격·참조 문제가 없는 적합한 타입으로
static long sum(int count, ...) {
    va_list ap; va_start(ap, count);   // count 는 int — 적합
    long s = 0;
    for (int i = 0; i < count; ++i) s += va_arg(ap, int);
    va_end(ap);
    return s;
}
int main() { std::cout << sum(3, 10, 20, 30) << '\n'; }""",
  'why':'근거: va_start 의 두 번째 인자(마지막 고정 매개변수)가 참조형이거나 register 저장, 함수/배열, 기본 인자 승격 대상 타입이면 표준은 그 동작을 미정의로 둔다(가변인자 영역의 시작 주소 계산이 보장되지 않음). 영향: 참조형을 넘기면 va_arg 추출 기준점이 어긋나 쓰레기 값을 읽거나 크래시가 나며, 플랫폼마다 다르게 깨진다. 대응: 가변인자 자체를 가변 템플릿으로 대체하는 것을 우선하고, C 가변인자가 불가피하면 마지막 고정 인자를 int 같은 적합한 값 타입으로 둔다.',
  'why_en':'Rationale: if the second argument to va_start (the last fixed parameter) is a reference type, register storage, a function/array, or subject to default argument promotion, the standard leaves the behaviour undefined, since the start address of the variadic area is not guaranteed to be computable. Impact: passing a reference type makes the va_arg extraction baseline wrong, reading garbage or crashing, and breaking differently per platform. Fix: prefer replacing varargs with variadic templates, and when C varargs are unavoidable make the last fixed parameter a suitable value type such as int.'},

 {'id':'EXP59-CPP','cat':'EXP · Rule · L1','compiles':True,
  'title':'offsetof 는 표준 레이아웃 타입의 유효한 멤버에만 사용한다',
  'title_en':'Use offsetof() on valid types and members',
  'bad': r"""#include <cstddef>
#include <iostream>
struct WithVtbl {           // 가상 함수 보유 — 비표준 레이아웃
    virtual void f() {}
    int m;
};
int main() {
    std::size_t o = offsetof(WithVtbl, m);   // 비표준 레이아웃에 offsetof — 조건부 지원/미정의
    std::cout << o << '\n';                    // vptr 때문에 의미가 불분명한 값
}""",
  'good': r"""#include <cstddef>
#include <iostream>
struct PlainData {          // 가상 없음, 단일 접근 — 표준 레이아웃
    int a;
    int m;
};
int main() {
    std::size_t o = offsetof(PlainData, m);   // 표준 레이아웃의 비정적 멤버 — 유효
    std::cout << o << '\n';
}""",
  'why':'근거: offsetof 는 표준 레이아웃(standard-layout) 타입의 비정적 데이터 멤버에 대해서만 정의되며, 가상 함수·가상 기반·혼합 접근 지정 등으로 비표준 레이아웃이 된 타입에 쓰면 조건부 지원이거나 미정의 동작이다. 영향: 숨은 vptr 이나 컴파일러가 자유롭게 정하는 배치 때문에 반환 오프셋이 무의미해져, 그 값으로 메모리를 직접 인덱싱하면 잘못된 위치에 접근한다. 대응: offsetof 는 표준 레이아웃 타입의 실제 멤버에만 사용하고, 필요하면 static_assert(std::is_standard_layout_v<T>) 로 보증한다.',
  'why_en':'Rationale: offsetof is defined only for non-static data members of a standard-layout type, and using it on a type made non-standard-layout by virtual functions, virtual bases, or mixed access specifiers is conditionally-supported or undefined. Impact: a hidden vptr or compiler-chosen layout makes the returned offset meaningless, so indexing memory with that value accesses the wrong location. Fix: use offsetof only on real members of standard-layout types, asserting it with static_assert(std::is_standard_layout_v<T>) when needed.'},

 {'id':'EXP60-CPP','cat':'EXP · Rule · L2','compiles':True,
  'title':'비표준 레이아웃(non-standard-layout) 객체를 실행 경계 너머로 전달하지 않는다',
  'title_en':'Do not pass a nonstandard-layout type object across execution boundaries',
  'bad': r"""#include <iostream>
#include <type_traits>
struct Mixed {              // private/public 혼합 — 멤버 순서 배치 미보장
private: int a;
public:  int b;
    Mixed(int x, int y): a(x), b(y) {}
    int sum() const { return a + b; }
};
// C 등 다른 경계 코드가 {int,int} 라고 가정하고 접근하면 a/b 순서가 어긋날 수 있음
int main() {
    std::cout << std::boolalpha << std::is_standard_layout<Mixed>::value << '\n';  // false
}""",
  'good': r"""#include <iostream>
#include <type_traits>
struct Flat {               // 단일 접근 지정 — 표준 레이아웃, 멤버 순서 보장
    int a;
    int b;
};
int main() {
    static_assert(std::is_standard_layout<Flat>::value, "must be standard-layout");
    std::cout << std::boolalpha << std::is_standard_layout<Flat>::value << '\n';   // true
}""",
  'why':'근거: 접근 지정자가 섞이거나 가상 기능이 있는 비표준 레이아웃 타입은 멤버의 상대적 메모리 배치가 표준으로 보장되지 않아 컴파일러가 자유롭게 재배치할 수 있다. 영향: 이런 타입을 C 코드·다른 컴파일러·디스크/네트워크 포맷 같은 실행 경계 밖으로 그대로 넘기면, 받는 쪽이 가정한 오프셋과 실제 배치가 달라 잘못된 필드를 읽는 손상이 발생한다. 대응: 경계를 넘는 타입은 단일 접근 지정·가상 없음으로 표준 레이아웃을 보장하고 static_assert 로 검증한다.',
  'why_en':'Rationale: a non-standard-layout type with mixed access specifiers or virtual features has no standardized relative memory layout of members, so the compiler may reorder them freely. Impact: passing such a type as-is across an execution boundary (C code, another compiler, an on-disk/network format) makes the receiver assume offsets that differ from the actual layout, reading the wrong field and corrupting data. Fix: ensure types that cross boundaries are standard-layout (single access specifier, no virtuals) and verify with static_assert.'},

 {'id':'EXP62-CPP','cat':'EXP · Rule · L2','compiles':True,
  'title':'객체 값에 속하지 않는 표현(representation) 비트에 접근하지 않는다',
  'title_en':'Do not access the bits of an object representation that are not part of the value representation',
  'bad': r"""#include <iostream>
#include <cstring>
struct S { char c; int v; };   // c 와 v 사이 패딩(값에 속하지 않는 비트)
static std::size_t bad_hash(const S& s) {
    const unsigned char* p = reinterpret_cast<const unsigned char*>(&s);
    std::size_t h = 0;
    for (std::size_t i = 0; i < sizeof s; ++i) h = h * 131 + p[i];   // 패딩까지 해시
    return h;
}
int main() {
    S a;                                      // a 의 패딩은 불확정(이전 스택 값)
    std::memset(&a, 0xFF, sizeof a);          // 패딩을 0xFF 로 오염시킨 뒤
    a.c = 'x'; a.v = 7;                        // 멤버만 설정 — 패딩엔 0xFF 잔존
    S b{};                                     // b 의 패딩은 0
    b.c = 'x'; b.v = 7;                        // 같은 논리 값
    std::cout << std::boolalpha
              << (bad_hash(a) == bad_hash(b)) << '\n';   // 값이 같아도 false 가능
}""",
  'good': r"""#include <iostream>
#include <functional>
struct S { char c; int v; };
static std::size_t good_hash(const S& s) {
    std::size_t h = std::hash<char>{}(s.c);          // 값 멤버만 결합
    h ^= std::hash<int>{}(s.v) + 0x9e3779b9 + (h << 6) + (h >> 2);
    return h;
}
int main() {
    S a{'x', 7}, b{'x', 7};
    std::cout << std::boolalpha << (good_hash(a) == good_hash(b)) << '\n';  // 항상 true
}""",
  'why':'근거: 객체의 표현 비트 중 패딩 같은 부분은 값(value)에 속하지 않아 불확정 상태일 수 있고, 같은 논리적 값을 가진 두 객체라도 그 비트는 다를 수 있다. 영향: reinterpret_cast 로 객체를 바이트열로 보고 전체를 해시·비교하면, 값이 같은데도 패딩 차이로 해시·비교 결과가 달라져 컨테이너 조회 실패·비결정적 동작이 생긴다. 대응: 해시·동등 비교는 의미 있는 값 멤버만을 결합해 계산하고, 객체 전체 바이트열에 의존하지 않는다.',
  'why_en':'Rationale: some object-representation bits, such as padding, are not part of the value and may be indeterminate, so two objects with the same logical value can still differ in those bits. Impact: reinterpret_cast-ing an object to a byte array and hashing or comparing the whole thing makes equal values produce different hash/compare results due to padding, causing container lookup failures and nondeterministic behaviour. Fix: compute hashes and equality from the meaningful value members only, never relying on the full object byte representation.'},

 {'id':'ERR53-CPP','cat':'ERR · Rule · L1','compiles':True,
  'title':'생성자/소멸자 function-try-block 핸들러에서 멤버·기반을 참조하지 않는다',
  'title_en':'Do not reference base classes or class data members in a constructor or destructor function-try-block handler',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct Resource { int id = 0; Resource(){ throw std::runtime_error("init"); } };
struct Widget {
    Resource r;
    Widget()
    try : r() {}
    catch (...) {
        std::cout << "id=" << r.id << '\n';   // 핸들러 도달 시 r 은 이미 소멸 — 미정의 접근
        throw;
    }
};
int main() {
    try { Widget w; } catch (...) { std::cout << "ctor failed\n"; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Resource { int id = 0; Resource(){ throw std::runtime_error("init"); } };
struct Widget {
    Resource r;
    Widget()
    try : r() {}
    catch (...) {
        std::cout << "ctor failed, logging only\n";   // 멤버 미참조
        throw;     // 생성자 function-try-block 은 반드시 예외로 끝나야 함
    }
};
int main() {
    try { Widget w; } catch (...) { std::cout << "handled\n"; }
}""",
  'why':'근거: 생성자의 function-try-block 핸들러는 멤버나 기반 클래스의 생성이 실패했거나 이미 풀린(소멸된) 뒤에 진입하므로, 그 시점에 멤버·기반 객체는 더 이상 존재하지 않는다. 영향: 핸들러에서 멤버를 읽거나 쓰면 수명이 끝난 객체에 접근하는 미정의 동작이 되어 쓰레기 값·크래시가 난다. 또한 이 핸들러는 정상 반환할 수 없어 반드시 예외를 다시 던지거나 새로 던져야 한다. 대응: 핸들러에서는 멤버를 참조하지 말고 로깅 등 멤버 독립적 작업만 한 뒤 예외를 전파한다.',
  'why_en':'Rationale: a constructor function-try-block handler is entered after a member or base class either failed to construct or has already been unwound (destroyed), so those subobjects no longer exist at that point. Impact: reading or writing a member in the handler accesses an out-of-lifetime object — undefined behaviour yielding garbage or a crash — and the handler cannot return normally, so it must rethrow or throw anew. Fix: in the handler do only member-independent work such as logging, then propagate the exception, without referencing members.'},

 {'id':'ERR59-CPP','cat':'ERR · Rule · L1','compiles':True,
  'title':'예외를 실행 경계(언어 경계 등) 너머로 던지지 않는다',
  'title_en':'Do not throw an exception across execution boundaries',
  'bad': r"""#include <iostream>
#include <stdexcept>
// C 호출자가 부를 수 있는 인터페이스인데 예외를 경계 밖으로 던짐
extern "C" void c_api(int x) {
    if (x < 0) throw std::runtime_error("negative");   // C 경계 밖으로 — 미정의
}
int main() {
    try { c_api(-1); } catch (...) { std::cout << "only safe because caller is C++\n"; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
// 경계 내부에서 모든 예외를 포착해 오류 코드로 변환
extern "C" int c_api(int x) {
    try {
        if (x < 0) throw std::runtime_error("negative");
        return 0;
    } catch (...) { return -1; }   // 예외를 경계 밖으로 내보내지 않음
}
int main() {
    std::cout << "rc=" << c_api(-1) << '\n';   // rc=-1
}""",
  'why':'근거: C 함수 인터페이스나 스레드 진입점, 콜백 같은 실행 경계는 C++ 예외 전파 메커니즘을 이해하지 못하므로, 예외가 그 경계를 넘어 전파되면 표준은 미정의 동작(대개 std::terminate)으로 둔다. 영향: C 코드가 호출한 함수에서 예외가 빠져나가면 스택 풀기가 C 프레임에서 깨져 프로그램이 정리 없이 강제 종료된다. 대응: 경계로 노출되는 모든 함수는 내부에서 catch(...) 로 예외를 포착해 반환 코드·에러 객체 같은 경계가 이해하는 형태로 변환한다.',
  'why_en':'Rationale: execution boundaries such as a C function interface, a thread entry point, or a callback do not understand the C++ exception propagation mechanism, so the standard makes an exception propagating across such a boundary undefined behaviour (usually std::terminate). Impact: if an exception escapes a function called from C code, stack unwinding breaks at the C frame and the program is forcibly terminated without cleanup. Fix: have every boundary-exposed function catch exceptions internally with catch(...) and translate them into a form the boundary understands, such as a return code or error object.'},

 {'id':'MEM55-CPP','cat':'MEM · Rule · L2','compiles':True,
  'title':'교체(replacement) operator new/delete 는 요구사항을 준수한다',
  'title_en':'Honor replacement dynamic storage management requirements',
  'bad': r"""#include <cstdlib>
#include <iostream>
// 전역 operator new 교체인데 실패 시 nullptr 반환 — non-throwing new 계약 위반
void* operator new(std::size_t n) {
    return std::malloc(n);   // 실패해도 예외를 던지지 않음
}
void operator delete(void* p) noexcept { std::free(p); }
int main() {
    int* p = new int(5);     // 표준은 실패 시 bad_alloc 을 기대 → 호출 코드가 nullptr 미대비
    std::cout << *p << '\n';
    delete p;
}""",
  'good': r"""#include <cstdlib>
#include <new>
#include <iostream>
// 계약 준수: 성공하면 정렬된 메모리, 실패하면 std::bad_alloc
void* operator new(std::size_t n) {
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
int main() {
    int* p = new int(5);
    std::cout << *p << '\n';
    delete p;
}""",
  'why':'근거: 기본(throwing) operator new 를 교체하면, 성공 시 적절히 정렬된 메모리를 돌려주고 실패 시 std::bad_alloc 을 던진다는 표준 계약을 그대로 지켜야 한다. 영향: 실패 시 nullptr 을 반환하면 표준 라이브러리와 사용자 코드가 모두 new 는 절대 nullptr 을 주지 않는다고 가정하므로, 검사 없이 역참조해 널 포인터 역참조로 크래시가 난다. 대응: 교체 operator new 는 실패 시 bad_alloc 을 던지고(또는 nothrow 버전만 nullptr), 0 바이트 요청도 유효 포인터를 주도록 계약을 충족하며, delete 와 짝을 맞춘다.',
  'why_en':'Rationale: replacing the default (throwing) operator new requires honoring the standard contract — return suitably aligned memory on success and throw std::bad_alloc on failure. Impact: returning nullptr on failure breaks the assumption (held by the standard library and user code) that new never returns nullptr, so the result is dereferenced unchecked, causing a null-pointer-dereference crash. Fix: have replacement operator new throw bad_alloc on failure (only the nothrow form returns nullptr), return a valid pointer even for a zero-byte request, and pair it with a matching delete.'},

 {'id':'OOP56-CPP','cat':'OOP · Rule · L2','compiles':True,
  'title':'교체한 핸들러(new_handler 등)의 요구사항을 준수한다',
  'title_en':'Honor replacement handler requirements',
  'bad': r"""#include <new>
#include <iostream>
// new_handler 인데 메모리 확보도, 핸들러 해제도, 예외/종료도 하지 않음
static void my_handler() {
    std::cout << "tried\n";   // 아무 해결 없이 반환 → operator new 가 무한 재시도
}
int main() {
    std::set_new_handler(my_handler);
    std::cout << "handler installed (not exercised)\n";   // 실제 OOM 유발은 회피
}""",
  'good': r"""#include <new>
#include <iostream>
static void my_handler() {
    // 1) 메모리를 확보하거나 2) 핸들러를 풀거나 3) 예외/종료 중 하나를 반드시 수행
    std::set_new_handler(nullptr);   // 더는 못 푼다고 판단 → 다음엔 bad_alloc 으로
    throw std::bad_alloc();
}
int main() {
    std::set_new_handler(my_handler);
    std::cout << "handler installed\n";
}""",
  'why':'근거: operator new 는 할당 실패 시 등록된 new_handler 를 호출하고 다시 할당을 시도하는 루프를 도는데, 표준은 핸들러가 (a) 더 많은 메모리를 확보하거나 (b) set_new_handler 로 자신을 해제하거나 (c) 예외를 던지거나 종료하도록 요구한다. 영향: 이 중 무엇도 하지 않고 그냥 반환하면 가용 메모리가 늘지 않은 채 같은 실패와 호출이 영원히 반복되어 프로그램이 무한 루프에 빠진다. 대응: new_handler 는 셋 중 하나를 반드시 수행하도록 작성하고, 더 풀 수 없으면 bad_alloc 을 던져 루프를 끝낸다.',
  'why_en':'Rationale: operator new loops by calling the registered new_handler on allocation failure and retrying, and the standard requires the handler to (a) make more memory available, (b) deregister itself via set_new_handler, or (c) throw an exception or terminate. Impact: simply returning without doing any of these leaves available memory unchanged, so the same failure and call repeat forever, hanging the program in an infinite loop. Fix: write the new_handler to always do one of the three, throwing bad_alloc to end the loop when nothing more can be freed.'},

 {'id':'CTR55-CPP','cat':'CTR · Rule · L2','compiles':True,
  'title':'반복자 덧셈 연산이 범위를 넘쳐 오버플로우하지 않게 한다',
  'title_en':'Do not use an additive operator on an iterator if the result would overflow',
  'bad': r"""#include <iostream>
#include <vector>
static int at_offset(const std::vector<int>& v, std::size_t offset) {
    auto it = v.begin() + offset;   // offset 이 size 보다 크면 end 를 넘어선 무효 반복자
    return *it;                     // 무효 반복자 역참조 — 미정의 동작
}
int main() {
    std::vector<int> v{1, 2, 3};
    std::cout << at_offset(v, 9) << '\n';   // 범위 밖
}""",
  'good': r"""#include <iostream>
#include <vector>
#include <optional>
static std::optional<int> at_offset(const std::vector<int>& v, std::size_t offset) {
    if (offset >= v.size()) return std::nullopt;   // 덧셈 전 범위 검증
    return *(v.begin() + offset);
}
int main() {
    std::vector<int> v{1, 2, 3};
    auto r = at_offset(v, 9);
    std::cout << (r ? std::to_string(*r) : "out of range") << '\n';
}""",
  'why':'근거: 임의 접근 반복자에 정수를 더하는 연산은 결과가 [begin, end] 범위 안에 머무를 때만 유효하며, 그 범위를 벗어나거나 정수 계산이 오버플로우하면 무효 반복자가 된다. 영향: 무효 반복자를 역참조하면 컨테이너 버퍼 밖 메모리를 읽어 미정의 동작·정보 유출·크래시가 나고, 오프셋이 외부 입력이면 보안 결함이 된다. 대응: 반복자에 오프셋을 더하기 전에 그 오프셋이 size() 이내인지 검사하고, 실패는 optional·예외 등으로 명시 처리한다.',
  'why_en':'Rationale: adding an integer to a random-access iterator is valid only when the result stays within [begin, end], and going past that range or overflowing the integer arithmetic produces an invalid iterator. Impact: dereferencing an invalid iterator reads memory outside the container buffer, causing undefined behaviour, information disclosure, or a crash, and becomes a security flaw when the offset is external input. Fix: check that the offset is within size() before adding it to an iterator, and handle failure explicitly via optional or an exception.'},

 {'id':'CON52-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'비트필드 멤버 접근 시 데이터 경쟁을 방지한다',
  'title_en':'Prevent data races when accessing bit-fields from multiple threads',
  'bad': r"""#include <iostream>
struct Flags { unsigned a : 1; unsigned b : 1; };   // a, b 가 같은 메모리 워드 공유
// T1 이 f.a 를, T2 가 f.b 를 동시에 써도, 둘은 같은 워드를 read-modify-write 하므로 경쟁
static void set_a(Flags& f) { f.a = 1; }
static void set_b(Flags& f) { f.b = 1; }
int main() {
    Flags f{0, 0};
    set_a(f); set_b(f);   // 단일 스레드 데모(동시 실행 시 한쪽 갱신이 유실될 수 있음)
    std::cout << f.a << f.b << '\n';
}""",
  'good': r"""#include <iostream>
#include <mutex>
struct Flags { unsigned a : 1; unsigned b : 1; };
static std::mutex m;
static void set_a(Flags& f) { std::lock_guard<std::mutex> g(m); f.a = 1; }
static void set_b(Flags& f) { std::lock_guard<std::mutex> g(m); f.b = 1; }
int main() {
    Flags f{0, 0};
    set_a(f); set_b(f);   // 동일 뮤텍스로 워드 단위 갱신을 직렬화
    std::cout << f.a << f.b << '\n';
}""",
  'why':'근거: 인접한 비트필드 멤버는 서로 다른 비트라도 같은 메모리 워드를 공유할 수 있고, 비트필드 갱신은 워드를 읽어 일부 비트를 바꾼 뒤 다시 쓰는 read-modify-write 로 구현된다. 영향: 두 스레드가 같은 워드의 서로 다른 비트필드를 잠금 없이 동시에 갱신하면, 한쪽의 read-modify-write 가 다른쪽 변경을 덮어써 갱신이 유실되는 데이터 경쟁(미정의 동작)이 된다. 대응: 같은 워드를 공유하는 비트필드들의 접근을 동일 뮤텍스로 보호하거나, 인접 비트필드를 별도 워드로 분리한다.',
  'why_en':'Rationale: adjacent bit-field members can share the same memory word even when they are different bits, and updating a bit-field is implemented as a read-modify-write of the whole word. Impact: if two threads update different bit-fields in the same word concurrently without a lock, one read-modify-write overwrites the other change, losing an update — a data race and undefined behaviour. Fix: protect accesses to bit-fields sharing a word with the same mutex, or separate adjacent bit-fields into distinct words.'},

 {'id':'CON55-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'조건 변수 사용 시 스레드 안전성과 진행성을 보존한다',
  'title_en':'Preserve thread safety and liveness when using condition variables',
  'bad': r"""#include <condition_variable>
#include <mutex>
static std::mutex m;
static std::condition_variable cv;
static bool ready = false;
// 잠금 밖에서 술어 갱신 없이 통지 — 대기자가 아직 wait 에 안 들어갔으면 신호 유실
static void producer() {
    ready = true;        // 잠금 보호 없이 공유 상태 변경(경쟁)
    cv.notify_one();     // 술어 갱신과 통지가 원자적이지 않음 → 신호 유실 가능
}
int main() { producer(); }""",
  'good': r"""#include <iostream>
#include <condition_variable>
#include <mutex>
static std::mutex m;
static std::condition_variable cv;
static bool ready = false;
static void producer() {
    { std::lock_guard<std::mutex> g(m); ready = true; }   // 잠금 안에서 술어 갱신
    cv.notify_all();                                      // 그 다음 통지
}
int main() {
    producer();
    std::unique_lock<std::mutex> lk(m);
    cv.wait(lk, []{ return ready; });   // 술어로 신호 유실에도 안전
    std::cout << "made progress\n";
}""",
  'why':'근거: 조건 변수의 올바른 사용은 공유 술어(조건)를 뮤텍스로 보호한 채 갱신한 뒤 통지하고, 대기 측은 술어를 받는 wait 로 조건을 재확인하는 것을 요구한다. 영향: 잠금 없이 술어를 바꾸고 통지하면, 통지가 대기 측이 wait 에 진입하기 전에 발생해 신호가 유실(lost wakeup)되어 대기 스레드가 영원히 깨어나지 못하는 진행성(liveness) 상실이 생긴다. 대응: 술어 갱신을 잠금 안에서 수행하고 그 뒤 통지하며, 대기는 술어 버전 wait(lk, pred) 로 작성한다.',
  'why_en':'Rationale: correct condition-variable use requires updating the shared predicate while holding the mutex, then notifying, while the waiter rechecks the condition via the predicate form of wait. Impact: changing the predicate and notifying without the lock lets the notification occur before the waiter enters wait, losing the wakeup so the waiting thread never wakes — a loss of liveness. Fix: update the predicate under the lock and then notify, and write the wait using the predicate form wait(lk, pred).'},

 {'id':'MSC53-CPP','cat':'MSC · Rule · L1','compiles':True,
  'title':'[[noreturn]] 으로 표시된 함수에서 반환하지 않는다',
  'title_en':'Do not return from a function declared [[noreturn]]',
  'bad': r"""#include <cstdlib>
// [[noreturn]] 인데 일부 경로에서 반환할 수 있음 — 호출자 가정과 모순
[[noreturn]] void fatal(bool can_recover) {
    if (can_recover) return;   // noreturn 함수가 반환 → 미정의 동작
    std::abort();
}
int main() { (void)&fatal; }   // 실행 회피(반환 경로 미트리거). 패턴 자체가 결함""",
  'good': r"""#include <cstdlib>
#include <stdexcept>
// 모든 경로에서 비반환을 보장
[[noreturn]] void fatal(bool can_recover) {
    if (can_recover) throw std::runtime_error("recoverable handled elsewhere");
    std::abort();              // 어느 경로든 예외 또는 종료로 끝남
}
int main() { (void)&fatal; }""",
  'why':'근거: [[noreturn]] 속성은 그 함수가 호출자에게 결코 제어를 되돌려주지 않는다고 컴파일러와 호출자에게 약속하는 것이며, 컴파일러는 이를 믿고 호출 지점 뒤를 도달 불가로 간주해 최적화한다. 영향: 실제로 그 함수가 반환하면 약속이 깨져 미정의 동작이 되고, 호출 뒤에 더는 없다고 가정해 제거·재배치된 코드 때문에 예측 불가능한 흐름·손상이 발생한다. 대응: [[noreturn]] 함수는 모든 경로에서 예외를 던지거나 abort/exit/무한 루프 등으로 끝나게 하여 절대 반환하지 않도록 보장한다.',
  'why_en':'Rationale: the [[noreturn]] attribute promises the compiler and callers that the function never returns control, and the compiler relies on this to treat code after the call site as unreachable and optimize accordingly. Impact: if the function actually returns, the promise is broken — undefined behaviour — and code that was removed or rearranged on the assumption that nothing follows the call leads to unpredictable flow and corruption. Fix: ensure a [[noreturn]] function ends on every path by throwing, or via abort/exit/an infinite loop, so it never returns.'},
]
