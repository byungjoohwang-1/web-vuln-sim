# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트1: A0~A8·M0~M5) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17 -pthread` 기준."""

RULES = [
 {'id':'A0-1-1','cat':'Required · Automated','compiles':True,
  'title':'결과가 사용되지 않는 값(useless assignment)을 두지 않는다',
  'title_en':'A project shall not contain instances of non-volatile variables being given values that are not used',
  'bad': r"""#include <iostream>
static int compute() { return 42; }
int main() {
    int x = compute();   // compute() 결과를 받았지만
    x = 5;               // 읽기 전에 덮어씀 — compute() 호출과 그 대입이 죽은 코드
    std::cout << x << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int x = 5;           // 실제로 쓰일 값만 대입
    std::cout << x << '\n';
}""",
  'why':'근거: 어떤 값을 변수에 넣은 뒤 읽히기 전에 다른 값으로 덮어쓰면 그 첫 계산과 대입은 결과에 아무 영향이 없는 죽은 코드(dead store)다. 영향: 대개 의도한 대입을 빠뜨렸거나 조건 분기가 잘못된 신호이며, 부작용 있는 함수를 호출해 놓고 결과를 버리면 의도와 다른 동작이 숨는다. 대응: 사용되지 않는 계산·대입을 제거하고, 정말 필요한 값만 대입한다.',
  'why_en':'Rationale: assigning a value to a variable and then overwriting it before it is read makes the first computation and assignment a dead store with no effect on the result. Impact: it usually signals a missed assignment or a wrong branch, and discarding the result of a side-effecting call hides behaviour that differs from intent. Fix: remove the unused computation and assignment, keeping only the value actually needed.'},

 {'id':'A0-1-2','cat':'Required · Automated','compiles':True,
  'title':'비void 함수의 반환값을 사용한다',
  'title_en':'The value returned by a function having a non-void return type that is not an overloaded operator shall be used',
  'bad': r"""#include <iostream>
#include <vector>
static bool resize_buf(std::vector<int>& v, std::size_t n) {
    if (n > 1000) return false;   // 실패를 bool 로 알림
    v.resize(n); return true;
}
int main() {
    std::vector<int> v;
    resize_buf(v, 5000);   // 반환값 무시 — 실패해도 모른 채 진행
    std::cout << v.size() << '\n';   // 0 인데 성공으로 가정하면 버그
}""",
  'good': r"""#include <iostream>
#include <vector>
static bool resize_buf(std::vector<int>& v, std::size_t n) {
    if (n > 1000) return false;
    v.resize(n); return true;
}
int main() {
    std::vector<int> v;
    if (!resize_buf(v, 5000)) { std::cout << "resize rejected\n"; return 1; }
    std::cout << v.size() << '\n';
}""",
  'why':'근거: 비void 함수의 반환값은 보통 결과나 성공/실패 같은 의미 있는 정보를 담는데, 이를 사용하지 않으면 그 정보가 소실된다. 영향: 오류 코드를 반환하는 함수의 결과를 무시하면 실패한 상태로 다음 단계를 진행해 데이터 손상·잘못된 결정이 누적된다. 대응: 반환값을 검사·사용하고, 의도적으로 버리는 경우에는 (void) 캐스트로 명시한다.',
  'why_en':'Rationale: the return value of a non-void function usually carries meaningful information such as a result or success/failure, which is lost if not used. Impact: ignoring the result of a function that returns an error code proceeds into the next step in a failed state, accumulating data corruption and wrong decisions. Fix: inspect and use the return value, and when intentionally discarding it make that explicit with a (void) cast.'},

 {'id':'A0-1-3','cat':'Required · Automated','compiles':True,
  'title':'정의된 모든 함수(정적/익명 네임스페이스)는 사용되어야 한다',
  'title_en':'Every function defined in an anonymous namespace, or static function, shall be used',
  'bad': r"""#include <iostream>
namespace {
    int helper() { return 7; }   // 정의했지만 어디서도 호출 안 됨 — 죽은 코드
}
int main() {
    std::cout << "no call to helper\n";
}""",
  'good': r"""#include <iostream>
namespace {
    int helper() { return 7; }   // 정의한 함수를 실제로 사용
}
int main() {
    std::cout << helper() << '\n';
}""",
  'why':'근거: 내부 링크(정적/익명 네임스페이스)를 가진 함수는 그 번역단위 안에서만 쓸 수 있으므로, 호출되지 않으면 영원히 죽은 코드로 남는다. 영향: 미사용 함수는 유지보수자가 호출 의도를 추측하게 만들고, 호출을 빠뜨린 진짜 버그(연결 누락)를 가리며 바이너리·검토 부담을 늘린다. 대응: 사용되지 않는 정적/익명 함수는 삭제하거나, 빠뜨린 호출을 추가해 실제로 사용한다.',
  'why_en':'Rationale: a function with internal linkage (static or anonymous namespace) can only be used within its translation unit, so if it is never called it remains dead code forever. Impact: an unused function makes maintainers guess the intended call site, can mask a real bug (a missed call), and adds binary and review burden. Fix: delete unused static/anonymous functions, or add the missing call so they are actually used.'},

 {'id':'A0-4-1','cat':'Required · Non-automated','compiles':True,
  'title':'부동소수 구현은 IEEE 754(IEC 60559)를 따라야 한다',
  'title_en':'Floating-point implementation shall comply with IEEE 754',
  'bad': r"""#include <iostream>
#include <cmath>
// IEEE 754 준수 여부를 확인하지 않고 NaN/Inf 동작에 의존
int main() {
    double x = 0.0 / 0.0;   // IEEE 면 NaN, 비준수 환경에선 동작이 다름
    if (x != x) std::cout << "treated as NaN\n";   // Na!=Na 가정에 의존
    else std::cout << "no NaN semantics\n";
}""",
  'good': r"""#include <iostream>
#include <limits>
// IEEE 754 준수를 컴파일 타임에 강제 — 비준수 플랫폼은 빌드 자체가 실패
static_assert(std::numeric_limits<double>::is_iec559,
              "IEEE 754 (IEC 60559) floating point is required");
int main() {
    std::cout << "IEEE 754 guaranteed at compile time\n";
}""",
  'why':'근거: 반올림 규칙, NaN·무한대 같은 특수값, 비정규수 처리 같은 부동소수 의미론은 IEEE 754 를 따를 때만 보장되며, 컴파일러 플래그(-ffast-math 등)나 플랫폼에 따라 달라질 수 있다. 영향: IEEE 비준수 환경에서 Na != NaN 같은 가정에 의존하면 비교·예외 처리가 조용히 다르게 동작해 안전필수 계산 결과가 흔들린다. 대응: std::numeric_limits<T>::is_iec559 를 static_assert 로 검사해 비준수 플랫폼에서 빌드를 막고, 부동소수 동작 가정을 명시적으로 보증한다.',
  'why_en':'Rationale: floating-point semantics such as rounding rules, special values like NaN and infinity, and subnormal handling are guaranteed only under IEEE 754, and can change with compiler flags (e.g. -ffast-math) or platform. Impact: relying on assumptions like NaN != NaN in a non-IEEE environment makes comparisons and exception handling silently differ, destabilizing safety-critical results. Fix: check std::numeric_limits<T>::is_iec559 with static_assert to block builds on non-compliant platforms and explicitly guarantee the assumed floating-point behaviour.'},

 {'id':'A2-7-2','cat':'Required · Automated','compiles':True,
  'title':'코드 섹션을 주석 처리(commented-out)로 비활성화하지 않는다',
  'title_en':'Sections of code shall not be commented out',
  'bad': r"""#include <iostream>
static void transform(int& d) { d *= 2; }
static void notify(int d) { std::cout << "notify " << d << '\n'; }
int main() {
    int d = 10;
    // transform(d);   // 의도가 불명확한 주석 처리 — 비활성? 임시? 삭제 예정?
    notify(d);
}""",
  'good': r"""#include <iostream>
static void transform(int& d) { d *= 2; }
static void notify(int d) { std::cout << "notify " << d << '\n'; }
#ifndef DISABLE_TRANSFORM
#define USE_TRANSFORM 1
#endif
int main() {
    int d = 10;
#if USE_TRANSFORM
    transform(d);       // 조건부 컴파일로 의도를 명시
#endif
    notify(d);
}""",
  'why':'근거: 주석으로 막은 코드는 그것이 영구 삭제 대상인지, 일시 비활성인지, 디버깅 잔재인지 의도를 전혀 드러내지 못한다. 영향: 시간이 지나면 주석 처리된 코드가 본문과 어긋난 채 방치되어 오해를 부르고, 리뷰·검색을 어지럽힌다(이력은 버전관리로 충분히 추적된다). 대응: 임시 비활성은 조건부 컴파일(#if)·기능 플래그로 의도를 드러내고, 더 이상 필요 없는 코드는 삭제한다.',
  'why_en':'Rationale: commented-out code reveals nothing about intent — whether it is slated for permanent deletion, temporarily disabled, or leftover debugging. Impact: over time it drifts out of sync with the live code, misleads readers, and clutters reviews and searches (history is already tracked by version control). Fix: express temporary disabling with conditional compilation (#if) or feature flags to show intent, and delete code that is no longer needed.'},

 {'id':'A2-10-1','cat':'Required · Automated','compiles':True,
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지(shadow) 않게 한다',
  'title_en':'An identifier declared in an inner scope shall not hide an identifier declared in an outer scope',
  'bad': r"""#include <iostream>
static int count = 100;   // 외부(파일) 범위
static void f() {
    int count = 5;        // 같은 이름으로 외부 count 를 가림(shadow)
    std::cout << count << '\n';   // 5 — 어느 count 인지 혼동
}
int main() { f(); std::cout << count << '\n'; }""",
  'good': r"""#include <iostream>
static int g_count = 100;   // 외부 범위는 g_ 접두사로 구분
static void f() {
    int local = 5;          // 다른 이름 — 가림 없음
    std::cout << local << '\n';
}
int main() { f(); std::cout << g_count << '\n'; }""",
  'why':'근거: 안쪽 범위에서 바깥 범위와 같은 이름을 선언하면 안쪽 이름이 바깥 이름을 가려, 그 구간에서는 의도와 다른 객체를 참조할 수 있다. 영향: 리팩터링·복사 과정에서 가려진 변수를 수정한 줄 알았는데 지역 사본만 바뀌는 식의 미묘한 버그가 생기고, 코드 리뷰에서 어느 변수인지 즉시 알기 어렵다. 대응: 내부 식별자에 다른 이름(또는 접두사 규칙)을 부여해 가림을 없애고, 컴파일러 경고(-Wshadow)를 켠다.',
  'why_en':'Rationale: declaring the same name in an inner scope as in an outer scope hides the outer name, so within that region a different object than intended may be referenced. Impact: during refactoring or copy-paste a subtle bug arises where a line thought to modify the outer variable changes only a local copy, and reviewers cannot tell at a glance which variable is meant. Fix: give inner identifiers different names (or a prefix convention) to remove the shadowing, and enable compiler warnings (-Wshadow).'},

 {'id':'A2-13-1','cat':'Required · Automated','compiles':True,
  'title':'표준에 정의된 이스케이프 시퀀스만 사용한다',
  'title_en':'Only those escape sequences that are defined in the C++ Standard shall be used',
  'bad': r"""#include <iostream>
int main() {
    const char* s = "col1\qcol2";   // \q 는 표준에 없는 이스케이프 — 구현정의
    std::cout << s << '\n';          // 어떻게 처리될지 불확실
}""",
  'good': r"""#include <iostream>
int main() {
    const char* s = "col1\tcol2";   // \t 는 표준 이스케이프(탭)
    std::cout << s << '\n';
}""",
  'why':'근거: C++ 표준은 \\n, \\t, \\\\ 등 허용되는 이스케이프 시퀀스 집합을 명시하며, 그 밖의 역슬래시 조합(\\q 등)은 조건부 지원이거나 구현정의 동작이다. 영향: 비표준 이스케이프는 컴파일러마다 경고만 내고 다르게 해석하거나 무시해, 의도한 문자열과 실제 내용이 달라지는 이식성 결함이 된다. 대응: 표준에 정의된 이스케이프만 사용하고, 특수 문자는 \\x·\\u 같은 표준 형식이나 명명 상수로 표현한다.',
  'why_en':'Rationale: the C++ Standard specifies the allowed set of escape sequences (\\n, \\t, \\\\, etc.), and any other backslash combination (such as \\q) is conditionally-supported or implementation-defined. Impact: a non-standard escape is interpreted differently or ignored across compilers with only a warning, making the intended string differ from the actual content — a portability defect. Fix: use only standard-defined escapes, and represent special characters with standard forms like \\x/\\u or named constants.'},

 {'id':'A2-13-3','cat':'Required · Automated','compiles':True,
  'title':'wchar_t 타입을 사용하지 않는다',
  'title_en':'Type wchar_t shall not be used',
  'bad': r"""#include <iostream>
int main() {
    wchar_t buf[] = L"hey";   // 요소 폭이 플랫폼마다 다름(Windows 2, Unix 4)
    std::cout << "sizeof wchar_t = " << sizeof(wchar_t) << '\n';   // 2 또는 4 — 비이식
    (void)buf;
}""",
  'good': r"""#include <iostream>
#include <cstdint>
int main() {
    char16_t u16[] = u"hey";   // 폭이 16비트로 고정
    char32_t u32[] = U"hey";   // 폭이 32비트로 고정
    std::cout << sizeof(u16[0]) << ' ' << sizeof(u32[0]) << '\n';   // 2 4 (이식 가능)
}""",
  'why':'근거: wchar_t 의 크기와 인코딩은 구현정의라 Windows 에서는 16비트(UTF-16), 대부분의 유닉스에서는 32비트(UTF-32)로 서로 다르다. 영향: wchar_t 로 직렬화·파일 포맷·프로토콜을 다루면 플랫폼 간에 폭과 인코딩이 어긋나 데이터가 깨지고, 코드가 한 플랫폼에 고착된다. 대응: 폭이 표준으로 고정된 char16_t/char32_t(및 std::u16string/u32string)를 사용해 이식 가능한 유니코드 처리를 한다.',
  'why_en':'Rationale: the size and encoding of wchar_t are implementation-defined, being 16-bit (UTF-16) on Windows but 32-bit (UTF-32) on most Unix systems. Impact: using wchar_t for serialization, file formats, or protocols mismatches width and encoding across platforms, corrupting data and locking code to one platform. Fix: use char16_t/char32_t (and std::u16string/u32string) whose widths are fixed by the standard for portable Unicode handling.'},

 {'id':'A3-1-1','cat':'Required · Automated',
  'title':'헤더는 자체적으로(self-contained) 포함 순서와 무관하게 컴파일되어야 한다',
  'title_en':'It shall be possible to include any header file in multiple translation units without violating the ODR',
  'bad': r"""// shape.h — Point 를 쓰면서 그 정의를 포함하지 않음
struct Shape {
    Point origin;   // Point 미정의 — 이 헤더를 단독 포함하면 컴파일 에러
};""",
  'good': r"""// shape.h — 필요한 의존성을 직접 포함
#include "point.h"   // Point 정의 제공
struct Shape {
    Point origin;
};""",
  'why':'근거: 헤더는 어떤 순서로 포함되든 단독으로 컴파일될 수 있어야 하며(자체 완결), 필요한 타입·선언을 직접 포함하지 않으면 그 가용성이 포함하는 쪽의 우연한 포함 순서에 의존하게 된다. 영향: 자체 완결되지 않은 헤더는 다른 헤더보다 먼저 포함되면 컴파일이 깨지는 깨지기 쉬운 빌드를 만들고, 포함 순서를 맞추는 숨은 규칙이 코드 전반에 퍼진다. 대응: 각 헤더가 사용하는 모든 타입·심볼의 정의/선언을 그 헤더에서 직접 #include 해 순서 독립적으로 컴파일되게 한다.',
  'why_en':'Rationale: a header must compile on its own regardless of include order (self-contained), and failing to include the types and declarations it uses makes their availability depend on the accidental include order of the includer. Impact: a non-self-contained header creates a fragile build that breaks when included before another header, spreading hidden ordering rules across the codebase. Fix: have each header directly #include the definitions/declarations of every type and symbol it uses so it compiles order-independently.'},

 {'id':'A3-3-2','cat':'Required · Automated','compiles':True,
  'title':'정적/스레드-지역 객체는 상수 초기화(constant initialization) 가능해야 한다',
  'title_en':'Static and thread-local objects shall be constant-initialized',
  'bad': r"""#include <iostream>
#include <string>
static std::string build() { return "config"; }
static std::string g_name = build();   // 동적 초기화 — TU 간 초기화 순서 문제
int main() { std::cout << g_name << '\n'; }""",
  'good': r"""#include <iostream>
#include <string>
// 상수 초기화 가능한 전역 + 지연 초기화로 동적 의존을 격리
static constexpr int kLimit = 100;
static const std::string& name() {
    static const std::string n = "config";   // 최초 사용 시 초기화(순서 안전)
    return n;
}
int main() { std::cout << kLimit << ' ' << name() << '\n'; }""",
  'why':'근거: 네임스페이스 범위 정적 객체가 런타임 함수 호출로 초기화되면(동적 초기화), 서로 다른 번역단위 간 초기화 순서가 표준으로 정해지지 않는다(static init order fiasco). 영향: 한 전역이 아직 초기화되지 않은 다른 전역에 의존하면 빌드·링크 순서에 따라 미초기화 값을 읽어 비결정적 버그가 생기고, 진단이 어렵다. 대응: 전역은 constexpr/상수식으로 초기화하고, 불가피한 동적 초기화는 함수 지역 static(최초 사용 시 초기화)으로 감싸 순서를 보장한다.',
  'why_en':'Rationale: when a namespace-scope static object is initialized by a runtime function call (dynamic initialization), the initialization order across different translation units is not defined by the standard (the static initialization order fiasco). Impact: if one global depends on another not-yet-initialized global, it reads an uninitialized value depending on build/link order, a nondeterministic and hard-to-diagnose bug. Fix: initialize globals with constexpr/constant expressions, and wrap unavoidable dynamic initialization in a function-local static (initialized on first use) to guarantee order.'},

 {'id':'A4-7-1','cat':'Required · Automated','compiles':True,
  'title':'정수 표현식이 데이터 손실을 일으키지 않게 한다',
  'title_en':'An integer expression shall not lead to data loss',
  'bad': r"""#include <iostream>
#include <cstdint>
int main() {
    std::uint32_t wide = 300;
    std::uint8_t narrow = wide;   // 8비트 초과분 절단 — 300 & 0xFF = 44
    std::cout << static_cast<int>(narrow) << '\n';   // 44, 조용한 데이터 손실
}""",
  'good': r"""#include <iostream>
#include <cstdint>
int main() {
    std::uint32_t wide = 300;
    if (wide <= 0xFF) {
        std::uint8_t narrow = static_cast<std::uint8_t>(wide);
        std::cout << static_cast<int>(narrow) << '\n';
    } else {
        std::cout << "value does not fit in uint8_t\n";   // 손실 방지
    }
}""",
  'why':'근거: 넓은 정수 타입의 값을 더 좁은 타입에 대입하면 표현 범위를 넘는 상위 비트가 잘려 나가고, 부호 있는/없는 변환에서는 값의 부호·크기가 바뀐다. 영향: 300 을 uint8_t 에 넣으면 44 가 되는 식의 조용한 데이터 손실이 발생해, 길이·카운트·인덱스로 쓰일 때 경계 오류나 잘못된 계산으로 번진다. 대응: 좁은 타입에 넣기 전에 값이 대상 범위에 맞는지 검사하고, 의도한 변환은 static_cast 로 명시한다.',
  'why_en':'Rationale: assigning a value of a wider integer type to a narrower type truncates the high bits beyond the representable range, and signed/unsigned conversions change the sign or magnitude. Impact: putting 300 into a uint8_t yields 44 — a silent data loss that, when used as a length, count, or index, escalates to boundary errors or wrong computations. Fix: check that the value fits the target range before narrowing, and make the intended conversion explicit with static_cast.'},

 {'id':'A4-10-1','cat':'Required · Automated','compiles':True,
  'title':'널 포인터 상수로는 nullptr 만 사용한다',
  'title_en':'Only nullptr literal shall be used as the null-pointer-constant',
  'bad': r"""#include <iostream>
static void handle(int v)    { std::cout << "int " << v << '\n'; }
static void handle(int* p)   { std::cout << "ptr " << (p?*p:-1) << '\n'; }
int main() {
    handle(0);   // 0 을 널 의도로 넘김 → 정수로 해석돼 handle(int) 선택(의도와 반대)
}""",
  'good': r"""#include <iostream>
static void handle(int v)    { std::cout << "int " << v << '\n'; }
static void handle(int* p)   { std::cout << "ptr " << (p?*p:-1) << '\n'; }
int main() {
    handle(nullptr);   // nullptr 은 포인터 타입 → handle(int*) 가 정확히 선택됨
}""",
  'why':'근거: NULL 과 0 은 정수 문맥과 포인터 문맥에서 모두 쓰일 수 있는 정수 상수라, 오버로드 해석에서 포인터 버전이 아니라 정수 버전이 선택될 수 있다. 영향: 예제처럼 handle(NULL) 이 의도와 달리 정수 오버로드를 부르면 잘못된 함수가 호출되거나, 템플릿·가변인자 문맥에서 타입이 어긋나 미묘한 버그가 된다. 대응: 널 포인터에는 포인터 타입으로만 추론되는 nullptr 만 사용한다.',
  'why_en':'Rationale: NULL and 0 are integer constants usable in both integer and pointer contexts, so overload resolution may select the integer version rather than the pointer version. Impact: as in the example, handle(NULL) calling the integer overload against intent invokes the wrong function, or in template/variadic contexts mismatches the type — a subtle bug. Fix: use nullptr for null pointers, since it deduces only to a pointer type.'},

 {'id':'A5-0-1','cat':'Required · Automated','compiles':True,
  'title':'표현식의 값이 평가 순서에 의존하지 않게 한다',
  'title_en':'The value of an expression shall be the same under any order of evaluation that the standard permits',
  'bad': r"""#include <iostream>
static int use(int a, int b) { return a * 10 + b; }
int main() {
    int i = 0;
    int r = use(i++, i++);   // 두 인자 평가 순서 미명세 — 결과 비결정적
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
static int use(int a, int b) { return a * 10 + b; }
int main() {
    int i = 0;
    int a = i++;   // 부작용을 분리해 순서 확정
    int b = i++;
    int r = use(a, b);
    std::cout << r << '\n';   // 항상 01
}""",
  'why':'근거: 함수 인자나 한 식 안 여러 피연산자의 평가 순서는(C++17에서 일부 강화됐어도) 일반적으로 미명세라, 같은 객체를 한 식에서 여러 번 수정하면 결과가 정해지지 않는다. 영향: use(i++, i++) 의 값이 컴파일러·최적화에 따라 달라져 이식성·재현성이 깨지고, 같은 스칼라에 부작용이 겹치면 미정의 동작이 된다. 대응: 부작용을 별도 문장으로 분리해 평가 순서를 명시적으로 확정한다.',
  'why_en':'Rationale: the evaluation order of function arguments and of multiple operands within one expression is generally unspecified (even with C++17 tightening), so modifying the same object several times in one expression leaves the result undefined. Impact: the value of use(i++, i++) varies by compiler/optimization, breaking portability and reproducibility, and overlapping side effects on one scalar become undefined behaviour. Fix: split side effects into separate statements to fix the evaluation order explicitly.'},

 {'id':'A5-1-1','cat':'Required · Automated','compiles':True,
  'title':'리터럴 값은 명명된 상수로 정의해 사용한다(매직 넘버 금지)',
  'title_en':'Literal values shall not be used apart from type initialization; named constants shall be used instead',
  'bad': r"""#include <iostream>
int main() {
    int speed = 130;
    if (speed > 120) std::cout << "over limit\n";   // 120 의 의미가 불명확(매직 넘버)
    if (speed > 120) std::cout << "log\n";           // 같은 값이 흩어져 변경 누락 위험
}""",
  'good': r"""#include <iostream>
int main() {
    constexpr int kSpeedLimitKmh = 120;   // 의미를 담은 명명 상수
    int speed = 130;
    if (speed > kSpeedLimitKmh) std::cout << "over limit\n";
    if (speed > kSpeedLimitKmh) std::cout << "log\n";
}""",
  'why':'근거: 코드 곳곳에 흩어진 리터럴(매직 넘버·문자열)은 그 값이 무엇을 뜻하는지, 여러 곳의 같은 값이 같은 개념인지 드러내지 못한다. 영향: 제한값이 바뀌면 흩어진 모든 리터럴을 빠짐없이 고쳐야 하는데 하나라도 놓치면 일관성이 깨지고, 의미 불명으로 리뷰·디버깅이 어렵다. 대응: 의미를 담은 constexpr 명명 상수로 한 번 정의하고 모든 곳에서 그 이름을 참조한다.',
  'why_en':'Rationale: literals scattered through code (magic numbers and strings) fail to convey what the value means or whether identical values in different places represent the same concept. Impact: when a limit changes, every scattered literal must be updated, and missing one breaks consistency, while the unclear meaning hampers review and debugging. Fix: define a meaningful constexpr named constant once and reference that name everywhere.'},

 {'id':'A5-1-2','cat':'Required · Automated','compiles':True,
  'title':'스코프를 벗어나는 람다에서 변수를 참조로 캡처하지 않는다',
  'title_en':'Variables shall not be implicitly captured in a lambda expression that outlives its scope',
  'bad': r"""#include <iostream>
#include <functional>
static std::function<int()> make() {
    int x = 1;
    return [&]{ return x; };   // x 참조 캡처 — 함수 종료 시 x 소멸 → 댕글링
}
int main() {
    auto f = make();
    std::cout << f() << '\n';   // 무효 참조 접근 — 미정의 동작
}""",
  'good': r"""#include <iostream>
#include <functional>
static std::function<int()> make() {
    int x = 1;
    return [x]{ return x; };   // 값 캡처 — 람다가 사본 소유
}
int main() {
    auto f = make();
    std::cout << f() << '\n';   // 1
}""",
  'why':'근거: 참조로 캡처한 변수는 람다 안에 포인터처럼 보관되므로, 그 변수가 람다보다 먼저 소멸하면 람다 내부 참조는 댕글링이 된다. 영향: 지역 변수를 참조 캡처한 람다(또는 std::function)를 반환하면, 호출 시점에 이미 해제된 스택을 읽어 쓰레기 값·크래시가 난다. 대응: 람다가 자신을 만든 스코프보다 오래 살 수 있으면 필요한 값을 값으로 캡처하고, 공유 수명이 필요하면 shared_ptr 를 캡처한다.',
  'why_en':'Rationale: a reference-captured variable is held like a pointer inside the lambda, so if it is destroyed before the lambda, the captured reference dangles. Impact: returning a lambda (or std::function) that reference-captures a local reads already-freed stack at call time, yielding garbage or a crash. Fix: capture needed values by value when the lambda may outlive the scope that created it, and capture a shared_ptr when shared lifetime is required.'},

 {'id':'A5-2-2','cat':'Required · Automated','compiles':True,
  'title':'전통적 C 스타일 캐스트를 사용하지 않는다',
  'title_en':'Traditional C-style casts shall not be used',
  'bad': r"""#include <iostream>
int main() {
    const double d = 3.9;
    int n = (int)d;   // C 스타일 캐스트 — 어떤 변환인지(절단? const 제거?) 불투명
    std::cout << n << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    const double d = 3.9;
    int n = static_cast<int>(d);   // 의도(수치 변환)가 명확한 C++ 캐스트
    std::cout << n << '\n';
}""",
  'why':'근거: C 스타일 캐스트 (T)x 는 static_cast·const_cast·reinterpret_cast 중 어떤 변환이든 상황에 맞춰 조용히 수행하므로, 코드만 봐서는 어떤 종류의(때로 위험한) 변환이 일어나는지 알 수 없다. 영향: const 제거나 무관한 타입 재해석 같은 위험한 변환이 무해한 수치 변환과 똑같이 보여 숨겨지고, grep 으로 위험한 캐스트를 찾기도 어렵다. 대응: 의도를 드러내는 C++ 캐스트(static_cast 등)를 사용해 변환 종류를 명시하고 컴파일러 검사를 받게 한다.',
  'why_en':'Rationale: a C-style cast (T)x silently performs whichever of static_cast, const_cast, or reinterpret_cast fits the situation, so the code alone does not reveal which (sometimes dangerous) conversion occurs. Impact: dangerous conversions like casting away const or reinterpreting unrelated types look identical to a harmless numeric conversion and are hidden, and dangerous casts are hard to grep for. Fix: use the intent-revealing C++ casts (static_cast, etc.) to make the conversion kind explicit and subject to compiler checks.'},

 {'id':'A5-2-3','cat':'Required · Automated','compiles':True,
  'title':'const_cast 로 const/volatile 한정을 제거하지 않는다',
  'title_en':'A cast shall not remove any const or volatile qualification from the type of a pointer or reference',
  'bad': r"""#include <iostream>
static void tamper(const int& v) {
    int& r = const_cast<int&>(v);   // const 제거
    r = 9;   // 호출자가 진짜 const 객체를 넘겼다면 수정은 미정의 동작
}
int main() {
    const int k = 5;
    tamper(k);
    std::cout << k << '\n';   // 5 또는 9 — 구현/최적화에 따라 불확정
}""",
  'good': r"""#include <iostream>
static void update(int& v) { v = 9; }   // 수정이 필요하면 비-const 인터페이스
int main() {
    int k = 5;   // 수정 대상은 비-const 로 선언
    update(k);
    std::cout << k << '\n';   // 9
}""",
  'why':'근거: const_cast 로 한정을 제거한 경로를 통해 실제로 const 로 정의된 객체를 수정하는 것은 미정의 동작이다(컴파일러가 const 객체를 상수 폴딩하거나 읽기 전용 메모리에 둘 수 있기 때문). 영향: 수정이 무시되거나, 읽기 전용 페이지에 쓰다 크래시가 나거나, 같은 객체의 두 읽기가 다른 값을 주는 등 진단 없는 결함이 된다. 대응: 객체를 수정해야 하면 처음부터 비-const 로 선언하고 비-const 인터페이스를 제공하며, const 를 벗겨 쓰지 않는다.',
  'why_en':'Rationale: modifying an object that is truly defined as const through a const-cast-stripped path is undefined behaviour, because the compiler may constant-fold it or place it in read-only memory. Impact: the write may be ignored, may crash when writing a read-only page, or two reads of the same object may differ — a defect with no diagnostic. Fix: declare objects that need modification as non-const from the start and provide a non-const interface, never casting away const to write.'},

 {'id':'A5-2-4','cat':'Required · Automated','compiles':True,
  'title':'reinterpret_cast 를 사용하지 않는다',
  'title_en':'reinterpret_cast shall not be used',
  'bad': r"""#include <iostream>
#include <cstdint>
int main() {
    float f = 1.5f;
    std::uint32_t bits = *reinterpret_cast<std::uint32_t*>(&f);   // 엄격 별칭 위반
    std::cout << bits << '\n';   // 미정의 동작 — 최적화에 따라 결과가 달라질 수 있음
}""",
  'good': r"""#include <iostream>
#include <cstdint>
#include <cstring>
int main() {
    float f = 1.5f;
    std::uint32_t bits;
    std::memcpy(&bits, &f, sizeof bits);   // 별칭·정렬 안전한 비트 재해석
    std::cout << bits << '\n';
}""",
  'why':'근거: reinterpret_cast 로 한 타입의 객체를 무관한 타입의 포인터로 보고 역참조하면 엄격 별칭 규칙(strict aliasing)과 정렬 요건을 위반해 미정의 동작이 된다. 영향: 컴파일러는 서로 다른 타입의 포인터가 같은 메모리를 가리키지 않는다고 가정해 최적화하므로, 그 가정을 깬 코드는 최적화 수준에 따라 다른 결과를 내거나 정렬 폴트로 크래시한다. 대응: 비트 단위 재해석이 필요하면 std::memcpy(또는 C++20 std::bit_cast)를 사용해 별칭·정렬 안전하게 처리한다.',
  'why_en':'Rationale: using reinterpret_cast to view an object of one type through a pointer to an unrelated type and dereferencing it violates the strict aliasing rule and alignment requirements, which is undefined behaviour. Impact: the compiler optimizes assuming pointers of different types do not alias, so code breaking that assumption produces different results by optimization level or crashes on an alignment fault. Fix: when bitwise reinterpretation is needed, use std::memcpy (or C++20 std::bit_cast) for aliasing- and alignment-safe handling.'},

 {'id':'A5-2-6','cat':'Required · Automated','compiles':True,
  'title':'&& 와 || 의 피연산자는 단순하지 않으면 괄호로 묶는다',
  'title_en':'The operands of a logical && or || shall be parenthesized if the operands contain binary operators',
  'bad': r"""#include <iostream>
int main() {
    bool a = true, b = false, c = true;
    if (a && b || c) std::cout << "taken\n";   // && 가 || 보다 우선 — (a&&b)||c 로 해석
    // 의도가 a && (b||c) 였다면 결과가 정반대
}""",
  'good': r"""#include <iostream>
int main() {
    bool a = true, b = false, c = true;
    if ((a && b) || c) std::cout << "taken\n";   // 우선순위를 괄호로 명시
}""",
  'why':'근거: && 는 || 보다 우선순위가 높지만, 이를 외워서 의존하면 a && b || c 가 (a && b) || c 인지 a && (b || c) 인지 독자가 오해하기 쉽다. 영향: 우선순위를 잘못 가정하면 조건이 정반대로 평가되어, 안전 점검·권한 검사 같은 논리에서 치명적 결함이 된다. 대응: 이항 연산자를 포함하는 && / || 의 피연산자를 괄호로 묶어 평가 순서를 코드에 명시한다.',
  'why_en':'Rationale: && has higher precedence than ||, but relying on memorizing this makes readers easily misread whether a && b || c means (a && b) || c or a && (b || c). Impact: a wrong precedence assumption evaluates the condition the opposite way, a critical defect in logic such as safety checks or authorization. Fix: parenthesize the operands of && / || that contain binary operators to make the evaluation order explicit in the code.'},

 {'id':'A5-3-2','cat':'Required · Automated','compiles':True,
  'title':'널 포인터를 역참조하지 않는다',
  'title_en':'Null pointers shall not be dereferenced',
  'bad': r"""#include <iostream>
#include <map>
struct Node { int v; };
static Node* find(std::map<int,Node>& m, int k) {
    auto it = m.find(k);
    return it == m.end() ? nullptr : &it->second;
}
int main() {
    std::map<int,Node> m;
    Node* n = find(m, 7);   // 없는 키 → nullptr
    n->v = 0;               // nullptr 역참조 — 크래시
    std::cout << "unreached\n";
}""",
  'good': r"""#include <iostream>
#include <map>
struct Node { int v; };
static Node* find(std::map<int,Node>& m, int k) {
    auto it = m.find(k);
    return it == m.end() ? nullptr : &it->second;
}
int main() {
    std::map<int,Node> m;
    Node* n = find(m, 7);
    if (n != nullptr) { n->v = 0; }   // 역참조 전 nullptr 검사
    else std::cout << "not found\n";
}""",
  'why':'근거: 어떤 객체도 가리키지 않는 널 포인터를 역참조해 그 대상에 접근하는 것은 미정의 동작이며, 대부분의 플랫폼에서 즉시 세그멘테이션 폴트로 이어진다. 영향: 조회·할당 실패로 널을 반환하는 함수의 결과를 검사 없이 역참조하면 프로그램이 크래시하고, 입력으로 유도되면 서비스 거부 취약점이 된다. 대응: 포인터를 역참조하기 전에 nullptr 인지 검사하거나, 널이 될 수 없도록 참조·옵셔널·보장된 팩토리를 사용한다.',
  'why_en':'Rationale: dereferencing a null pointer — which points to no object — to access its target is undefined behaviour and on most platforms causes an immediate segmentation fault. Impact: dereferencing without checking the result of a function that returns null on lookup or allocation failure crashes the program, and when input-driven becomes a denial-of-service vulnerability. Fix: check for nullptr before dereferencing, or use references, optionals, or guaranteed factories so the pointer cannot be null.'},

 {'id':'A5-6-1','cat':'Required · Automated','compiles':True,
  'title':'0으로 나누는 일이 없도록 한다',
  'title_en':'The right hand operand of the integer division or remainder operators shall not be equal to zero',
  'bad': r"""#include <iostream>
static int average(int sum, int count) {
    return sum / count;   // count==0 이면 0 나눗셈 — 미정의 동작(대개 크래시)
}
int main() {
    std::cout << average(100, 0) << '\n';
}""",
  'good': r"""#include <iostream>
#include <optional>
static std::optional<int> average(int sum, int count) {
    if (count == 0) return std::nullopt;   // 분모 0 을 먼저 차단
    return sum / count;
}
int main() {
    auto a = average(100, 0);
    std::cout << (a ? std::to_string(*a) : "undefined (count=0)") << '\n';
}""",
  'why':'근거: 정수 나눗셈 / 과 나머지 % 의 우변(분모)이 0 이면 결과가 수학적으로 정의되지 않아 표준은 미정의 동작으로 규정하며, 대부분의 하드웨어에서 정수 나눗셈 예외로 프로세스가 즉시 종료된다. 영향: 카운트·길이 등 0 이 될 수 있는 값을 검사 없이 분모로 쓰면 런타임 크래시가 나고, 분모가 외부 입력이면 서비스 거부로 악용된다. 대응: 나누기 전에 분모가 0 이 아님을 검사하고, 0 인 경우를 옵셔널·오류 코드 등으로 명시 처리한다.',
  'why_en':'Rationale: when the right operand (divisor) of integer division / or remainder % is zero, the result is mathematically undefined, so the standard makes it undefined behaviour, and most hardware raises an integer-divide exception that immediately terminates the process. Impact: using a possibly-zero value such as a count or length as a divisor without checking causes a runtime crash, and an input-controlled divisor can be exploited for denial of service. Fix: check that the divisor is non-zero before dividing and handle the zero case explicitly with an optional or error code.'},

 {'id':'A5-16-1','cat':'Required · Automated','compiles':True,
  'title':'삼항 연산자를 다른 식의 하위 표현식으로 사용하지 않는다',
  'title_en':'The ternary conditional operator shall not be used as a sub-expression',
  'bad': r"""#include <iostream>
int main() {
    bool cond = true; int base = 100, factor = 3;
    int r = base + (cond ? 10 : 20) * factor;   // 삼항이 큰 식에 묻혀 우선순위 혼동
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    bool cond = true; int base = 100, factor = 3;
    int adj = cond ? 10 : 20;   // 삼항을 독립 문장으로 분리
    int r = base + adj * factor;
    std::cout << r << '\n';
}""",
  'why':'근거: 삼항 연산자를 더 큰 산술·논리 식의 하위 표현식으로 끼워 넣으면, 삼항의 경계와 연산자 우선순위가 시각적으로 명확하지 않아 의미를 오독하기 쉽다. 영향: base + (cond?10:20) * factor 에서 곱셈이 삼항 결과에만 적용되는지 헷갈려 괄호를 잘못 두면 계산이 어긋나고, 안전필수 로직에서 결함이 된다. 대응: 삼항 결과를 의미 있는 이름의 별도 변수에 담아 한 단계씩 평가가 드러나게 한다.',
  'why_en':'Rationale: embedding the ternary operator as a sub-expression of a larger arithmetic or logical expression makes the boundary of the ternary and the operator precedence visually unclear, easy to misread. Impact: in base + (cond?10:20) * factor it is confusing whether the multiplication applies only to the ternary result, and misplacing parentheses skews the computation — a defect in safety-critical logic. Fix: assign the ternary result to a separate well-named variable so the evaluation is revealed one step at a time.'},

 {'id':'A6-4-1','cat':'Required · Automated','compiles':True,
  'title':'enum 을 다루는 switch 는 모든 열거자에 대한 case 를 가진다',
  'title_en':'A switch statement shall have a case for each enumerator of the controlling enum',
  'bad': r"""#include <iostream>
enum class State { Idle, Run, Stop };
static const char* name(State s) {
    switch (s) {
        case State::Idle: return "idle";
        case State::Run:  return "run";
        // State::Stop 누락 — Stop 이 들어오면 아무 case 도 안 탐
    }
    return "?";
}
int main() { std::cout << name(State::Stop) << '\n'; }""",
  'good': r"""#include <iostream>
enum class State { Idle, Run, Stop };
static const char* name(State s) {
    switch (s) {
        case State::Idle: return "idle";
        case State::Run:  return "run";
        case State::Stop: return "stop";   // 모든 열거자 명시 처리
    }
    return "?";
}
int main() { std::cout << name(State::Stop) << '\n'; }""",
  'why':'근거: 열거형을 다루는 switch 에 모든 열거자 case 를 두면, 나중에 열거자가 추가됐을 때 컴파일러가 처리되지 않은 case 를 경고(-Wswitch)로 잡아준다. 영향: 일부 열거자를 빠뜨리면 새 값이 추가돼도 조용히 처리가 누락되어, 상태 기계·명령 디스패치에서 의도치 않은 기본 동작이나 오류가 발생한다. 대응: default 로 뭉뚱그리기보다 모든 열거자를 명시적으로 처리해, 열거형 변경 시 컴파일러가 미처리 case 를 알려주게 한다.',
  'why_en':'Rationale: having a case for every enumerator in a switch on an enum lets the compiler warn (-Wswitch) about an unhandled case when an enumerator is later added. Impact: omitting some enumerators silently drops handling when a new value is added, causing unintended default behaviour or errors in state machines and command dispatch. Fix: handle every enumerator explicitly rather than lumping them under default, so the compiler flags unhandled cases when the enum changes.'},

 {'id':'A6-5-3','cat':'Advisory · Automated','compiles':True,
  'title':'do-while 문을 사용하지 않는다',
  'title_en':'Do statements should not be used',
  'bad': r"""#include <iostream>
int main() {
    int n = 0;
    do {
        std::cout << "body runs at least once\n";   // 조건이 처음부터 거짓이어도 1회 실행
    } while (n > 0);
}""",
  'good': r"""#include <iostream>
int main() {
    int n = 0;
    while (n > 0) {
        std::cout << "body\n";   // 선조건 — 조건이 거짓이면 한 번도 실행 안 함
    }
    std::cout << "loop checked condition first\n";
}""",
  'why':'근거: do-while 은 조건 검사가 본문 뒤에 있어 본문이 항상 최소 한 번 실행되는데, 코드를 위에서 아래로 읽는 독자는 이 사실을 간과하기 쉽다. 영향: 입력이 비어 있거나 조건이 처음부터 거짓인 경우에도 본문이 한 번 실행되어, 빈 컬렉션 처리·경계 조건에서 예기치 않은 부작용이 발생한다. 대응: 조건을 먼저 검사하는 while 또는 for 로 바꿔 0회 실행 가능성을 코드 형태로 드러낸다.',
  'why_en':'Rationale: in a do-while the condition is checked after the body, so the body always runs at least once, a fact readers scanning top to bottom easily overlook. Impact: even with empty input or a condition false from the start, the body executes once, causing unexpected side effects when handling empty collections or boundary conditions. Fix: switch to a while or for loop that checks the condition first, making the zero-iteration possibility visible in the code structure.'},

 {'id':'A6-6-1','cat':'Required · Automated','compiles':True,
  'title':'goto 문을 사용하지 않는다',
  'title_en':'The goto statement shall not be used',
  'bad': r"""#include <iostream>
int main() {
    int* buf = new int[10];
    bool err = true;
    if (err) goto cleanup;   // 비선형 점프 — 흐름 분석을 어렵게 함
    buf[0] = 1;
cleanup:
    delete[] buf;
    std::cout << "done\n";
}""",
  'good': r"""#include <iostream>
#include <memory>
int main() {
    auto buf = std::make_unique<int[]>(10);   // RAII — 모든 경로에서 자동 정리
    bool err = true;
    if (!err) { buf[0] = 1; }
    std::cout << "done\n";   // goto 없이 구조적 제어로 정리 보장
}""",
  'why':'근거: goto 는 함수 안 임의 지점으로 제어를 옮겨 비선형 흐름을 만들고, 객체 수명·초기화를 건너뛰는 점프는 분석과 추론을 어렵게 한다. 영향: goto 기반 정리 패턴은 라벨이 늘수록 흐름이 얽혀 자원 해제 누락·이중 해제 같은 결함을 부르고, 정적 분석·검토를 방해한다. 대응: RAII 로 정리를 객체 소멸자에 위임하고, 분기·반복·조기 return 같은 구조적 제어문으로 흐름을 선형적으로 표현한다.',
  'why_en':'Rationale: goto transfers control to an arbitrary point in a function, creating non-linear flow, and jumps that skip object lifetimes or initialization make analysis and reasoning hard. Impact: goto-based cleanup patterns tangle as labels multiply, inviting defects like missed or double resource release, and hinder static analysis and review. Fix: delegate cleanup to object destructors via RAII and express flow linearly with structured control statements such as branches, loops, and early return.'},

 {'id':'A7-1-1','cat':'Required · Automated','compiles':True,
  'title':'변경되지 않는 변수/멤버는 const(또는 constexpr)로 선언한다',
  'title_en':'Constexpr or const specifiers shall be used for immutable data declaration',
  'bad': r"""#include <iostream>
int main() {
    int radius = 5;   // 이후 수정이 없는데도 비-const — 실수로 바뀔 여지
    double area = 3.14159 * radius * radius;
    std::cout << area << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    const int radius = 5;   // 불변 의도를 const 로 강제
    double area = 3.14159 * radius * radius;
    std::cout << area << '\n';
}""",
  'why':'근거: 초기화 후 값이 바뀌지 않는 변수에 const(컴파일 타임 상수면 constexpr)를 붙이면, 그 불변 의도가 코드에 드러나고 컴파일러가 우발적 수정을 차단한다. 영향: 불변 값을 비-const 로 두면 나중에 실수로 대입되거나, 독자가 그 값이 변할 수 있다고 오해해 불필요한 방어 코드를 더하게 된다. 대응: 변경되지 않는 지역·멤버·매개변수를 const/constexpr 로 선언해 불변성을 강제하고 의도를 명확히 한다.',
  'why_en':'Rationale: marking a variable whose value never changes after initialization as const (constexpr if a compile-time constant) reveals the immutable intent in the code and lets the compiler block accidental modification. Impact: leaving an immutable value non-const allows a later mistaken assignment, or leads readers to assume it can change and add unnecessary defensive code. Fix: declare unchanging locals, members, and parameters as const/constexpr to enforce immutability and clarify intent.'},

 {'id':'A7-1-6','cat':'Required · Automated','compiles':True,
  'title':'typedef 대신 using 별칭을 사용한다',
  'title_en':'The typedef specifier shall not be used',
  'bad': r"""#include <iostream>
#include <map>
#include <string>
typedef std::map<int, std::string> Table;   // 구식 typedef — 템플릿 별칭 불가
int main() {
    Table t; t[1] = "one";
    std::cout << t[1] << '\n';
}""",
  'good': r"""#include <iostream>
#include <map>
#include <string>
using Table = std::map<int, std::string>;   // using 별칭 — 읽기 쉽고 일관적
template <typename V> using IntMap = std::map<int, V>;   // 별칭 템플릿도 가능
int main() {
    Table t; t[1] = "one";
    IntMap<double> d; d[2] = 2.5;
    std::cout << t[1] << ' ' << d[2] << '\n';
}""",
  'why':'근거: using 별칭은 "별명 = 실제타입" 형태로 좌→우로 자연스럽게 읽히고, typedef 가 지원하지 못하는 별칭 템플릿(template using)까지 표현할 수 있다. 영향: typedef 와 using 을 섞어 쓰면 스타일이 불일치하고, 함수 포인터·배열 같은 복잡한 타입의 typedef 는 읽기 어려워 오해를 부른다. 대응: 타입 별칭은 일관되게 using 으로 작성해 가독성과 템플릿 별칭 지원을 확보한다.',
  'why_en':'Rationale: a using alias reads naturally left to right as "alias = actual type" and can even express alias templates (template using), which typedef cannot. Impact: mixing typedef and using is stylistically inconsistent, and typedefs of complex types like function pointers or arrays are hard to read and misleading. Fix: write type aliases consistently with using for readability and alias-template support.'},

 {'id':'A7-1-7','cat':'Required · Automated','compiles':True,
  'title':'한 선언문에는 하나의 변수/이름만 선언한다',
  'title_en':'Each expression statement and identifier declaration shall be placed on a separate line',
  'bad': r"""#include <iostream>
int main() {
    int* a, b;   // 직관과 달리 a 만 포인터, b 는 int — 오해 유발
    int x = 0;
    a = &x; b = 5;
    std::cout << *a << ' ' << b << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int* a;   // 한 줄에 하나씩 — 타입이 명확
    int  b;
    int x = 0;
    a = &x; b = 5;
    std::cout << *a << ' ' << b << '\n';
}""",
  'why':'근거: 한 선언문에 여러 이름을 적으면 포인터·참조 표기(*, &)가 첫 이름에만 적용되는 등 타입이 직관과 달라, int* a, b; 에서 b 가 포인터가 아니라 int 라는 사실이 가려진다. 영향: 선언을 잘못 읽으면 b 를 포인터로 착각해 잘못 사용하거나, 초기화를 한 변수에만 적용하는 실수가 생긴다. 대응: 한 선언문에는 하나의 변수만 선언하고 각 선언을 별도 줄에 두어 타입을 분명히 한다.',
  'why_en':'Rationale: declaring multiple names in one statement applies pointer/reference notation (*, &) only to the first name, so in int* a, b; the fact that b is an int rather than a pointer is hidden. Impact: misreading the declaration leads to mistaking b for a pointer and misusing it, or applying initialization to only one variable by mistake. Fix: declare one variable per statement on its own line to make types clear.'},

 {'id':'A7-2-2','cat':'Required · Automated','compiles':True,
  'title':'열거형의 기반 타입(underlying type)을 명시한다',
  'title_en':'Enumeration underlying base type shall be explicitly defined',
  'bad': r"""#include <iostream>
#include <cstdint>
enum class Mode { A, B, C };   // 기반 타입 미명시 — 크기·표현이 불확실
int main() {
    std::cout << sizeof(Mode) << '\n';   // 구현정의 크기(보통 int=4)
}""",
  'good': r"""#include <iostream>
#include <cstdint>
enum class Mode : std::uint8_t { A, B, C };   // 기반 타입 명시 — 1바이트로 고정
int main() {
    std::cout << sizeof(Mode) << '\n';   // 1 — 직렬화·ABI 안정
}""",
  'why':'근거: 범위 지정 enum 의 기반 타입을 명시하지 않으면 기본값(보통 int)에 맡겨져 열거형의 크기와 비트 표현이 불확실해진다. 영향: 직렬화·메모리 매핑·하드웨어 레지스터·다른 언어와의 ABI 경계에서 기대한 폭과 실제 폭이 어긋나 데이터가 깨지고, 좁은 저장이 필요한 임베디드에서 메모리를 낭비한다. 대응: enum class Mode : std::uint8_t 처럼 기반 타입을 명시해 크기와 표현을 고정한다.',
  'why_en':'Rationale: not specifying the underlying type of a scoped enum leaves it to the default (usually int), making the size and bit representation of the enum uncertain. Impact: at serialization, memory mapping, hardware registers, or an ABI boundary with another language, the expected and actual widths mismatch and corrupt data, and it wastes memory in embedded systems that need narrow storage. Fix: specify the underlying type, as in enum class Mode : std::uint8_t, to fix the size and representation.'},

 {'id':'A7-2-3','cat':'Required · Automated','compiles':True,
  'title':'열거형은 범위 지정 enum class 로 선언한다',
  'title_en':'Enumerations shall be declared as scoped enum classes',
  'bad': r"""#include <iostream>
enum Color { Red, Green, Blue };   // 비범위 — 열거자가 전역으로 새고 int 로 암시 변환
int main() {
    int x = Red;          // 암시적 정수 변환 — 타입 안전성 없음
    if (x == Green - 1) std::cout << "fragile compare\n";   // 열거자 산술
}""",
  'good': r"""#include <iostream>
enum class Color { Red, Green, Blue };   // 범위 지정 — 이름 충돌·암시 변환 차단
int main() {
    Color c = Color::Red;
    if (c == Color::Red) std::cout << "type-safe compare\n";
}""",
  'why':'근거: 비범위 enum 은 열거자 이름이 둘러싼 범위로 그대로 새어 나와 다른 이름과 충돌할 수 있고, 값이 정수로 암시 변환되어 의미 없는 산술·비교가 허용된다. 영향: 전역 이름 오염으로 Red 같은 흔한 이름이 충돌하고, enum 값이 정수처럼 다뤄져 서로 다른 열거형이 뒤섞이거나 잘못된 비교가 컴파일을 통과한다. 대응: enum class 로 선언해 열거자를 enum 범위 안에 가두고 암시적 정수 변환을 막아 타입 안전성을 확보한다.',
  'why_en':'Rationale: an unscoped enum leaks its enumerator names into the enclosing scope where they can collide with other names, and its values implicitly convert to integers, allowing meaningless arithmetic and comparison. Impact: global name pollution makes common names like Red collide, and treating enum values as integers lets different enums mix or wrong comparisons compile. Fix: declare it as an enum class to confine enumerators to the enum scope and block implicit integer conversion, securing type safety.'},

 {'id':'A7-5-2','cat':'Required · Automated','compiles':True,
  'title':'함수는 직접/간접 재귀를 사용하지 않는다',
  'title_en':'Functions shall not call themselves, either directly or indirectly',
  'bad': r"""#include <iostream>
#include <cstdint>
static std::uint64_t fib(int n) {   // 직접 재귀 — 최대 스택 깊이를 정적으로 보장 못함
    return (n < 2) ? n : fib(n-1) + fib(n-2);
}
int main() { std::cout << fib(20) << '\n'; }""",
  'good': r"""#include <iostream>
#include <cstdint>
static std::uint64_t fib(int n) {   // 반복 — 상수 스택, 선형 시간
    std::uint64_t a = 0, b = 1;
    for (int i = 0; i < n; ++i) { std::uint64_t t = a + b; a = b; b = t; }
    return a;
}
int main() { std::cout << fib(20) << '\n'; }""",
  'why':'근거: 재귀 함수는 호출 깊이가 입력에 따라 달라져, 최악의 경우 스택 사용량을 컴파일 타임에 정적으로 한정하기 어렵다. 영향: 안전필수·임베디드 시스템에서는 깊은(또는 무한) 재귀가 스택 오버플로우를 일으켜 인접 메모리를 침범하거나 시스템을 정지시키는데, 이는 사전 검증으로 막아야 할 결함이다. 대응: 재귀를 반복(루프)과 명시적 자료구조(스택·큐)로 변환해 메모리 사용량을 정적으로 한정 가능하게 만든다.',
  'why_en':'Rationale: a recursive function has a call depth that varies with input, making it hard to statically bound the worst-case stack usage at compile time. Impact: in safety-critical and embedded systems, deep (or infinite) recursion causes a stack overflow that invades adjacent memory or halts the system — a defect that must be prevented by up-front verification. Fix: convert recursion into iteration (loops) with an explicit data structure (stack or queue) so memory usage can be statically bounded.'},

 {'id':'A7-6-1','cat':'Required · Automated','compiles':True,
  'title':'[[noreturn]] 함수는 반환하지 않아야 한다',
  'title_en':'Functions declared with the [[noreturn]] attribute shall not return',
  'bad': r"""#include <cstdlib>
[[noreturn]] void fail(bool recoverable) {
    if (recoverable) return;   // [[noreturn]] 인데 일부 경로에서 반환 — 미정의 동작
    std::abort();
}
int main() { (void)&fail; }   // 실행 회피(반환 경로 미트리거). 패턴 자체가 결함""",
  'good': r"""#include <cstdlib>
#include <stdexcept>
[[noreturn]] void fail(bool recoverable) {
    if (recoverable) throw std::runtime_error("recoverable handled elsewhere");
    std::abort();   // 모든 경로가 throw 또는 종료 — 절대 반환 안 함
}
int main() { (void)&fail; }""",
  'why':'근거: [[noreturn]] 속성은 그 함수가 호출자에게 결코 제어를 돌려주지 않는다고 컴파일러·호출자에게 약속하며, 컴파일러는 이를 믿고 호출 지점 뒤를 도달 불가로 간주해 최적화한다. 영향: 실제로 그 함수가 반환하면 약속이 깨져 미정의 동작이 되고, 호출 뒤가 없다고 가정해 제거·재배치된 코드 때문에 예측 불가능한 흐름·손상이 발생한다. 대응: [[noreturn]] 함수가 모든 경로에서 throw 하거나 abort/exit/무한 루프로 끝나도록 보장해 절대 반환하지 않게 한다.',
  'why_en':'Rationale: the [[noreturn]] attribute promises the compiler and callers that the function never returns control, and the compiler relies on this to treat code after the call site as unreachable and optimize accordingly. Impact: if the function actually returns, the promise is broken — undefined behaviour — and code removed or rearranged on the assumption that nothing follows the call leads to unpredictable flow and corruption. Fix: ensure a [[noreturn]] function ends on every path by throwing or via abort/exit/an infinite loop so it never returns.'},

 {'id':'A8-4-1','cat':'Required · Automated','compiles':True,
  'title':'함수를 C 스타일 가변인자(...)로 정의하지 않는다',
  'title_en':'Functions shall not be defined using the ellipsis notation',
  'bad': r"""#include <cstdarg>
#include <iostream>
static long total(int count, ...) {   // 타입 검사 없는 C 가변인자
    va_list ap; va_start(ap, count);
    long s = 0;
    for (int i = 0; i < count; ++i) s += va_arg(ap, int);   // double 을 넘기면 미정의
    va_end(ap);
    return s;
}
int main() { std::cout << total(2, 10, 3.5) << '\n'; }   // 두 번째 인자 타입 불일치""",
  'good': r"""#include <iostream>
template <typename... Args>   // 가변 템플릿 — 타입·개수가 컴파일 타임에 검증됨
static auto total(Args... args) { return (args + ... + 0); }
int main() { std::cout << total(10, 3.5) << '\n'; }""",
  'why':'근거: ... 가변인자는 전달된 인자의 타입·개수 정보가 컴파일러에 남지 않아, va_arg 가 지정한 타입과 실제 인자가 다르면 검사 없이 잘못된 비트를 읽는다. 영향: 호출자가 형식과 다른 타입을 넘기면 쓰레기 값·크래시·정보 유출이 발생하고, 인자 개수 불일치도 진단되지 않는다. 대응: 가변 템플릿(fold expression)이나 std::initializer_list 로 대체해 타입과 개수를 컴파일 타임에 검증되게 한다.',
  'why_en':'Rationale: ellipsis varargs keep no type or count information about the passed arguments, so va_arg reads wrong bits unchecked when the requested type differs from the actual argument. Impact: passing a type different from the format yields garbage, crashes, or information disclosure, and an argument-count mismatch goes undiagnosed. Fix: replace with variadic templates (fold expressions) or std::initializer_list so types and counts are checked at compile time.'},

 {'id':'A8-4-7','cat':'Required · Automated','compiles':True,
  'title':'작고 trivially copyable 한 입력 매개변수는 값으로 전달한다',
  'title_en':'Small trivially copyable input parameters shall be passed by value',
  'bad': r"""#include <iostream>
static int scale(const int& x, const int& f) {   // 작은 타입에 const 참조 — 불필요한 간접화
    return x * f;
}
int main() { std::cout << scale(6, 7) << '\n'; }""",
  'good': r"""#include <iostream>
static int scale(int x, int f) {   // 값 전달 — 직접 접근, 별칭 가능성 없음
    return x * f;
}
int main() { std::cout << scale(6, 7) << '\n'; }""",
  'why':'근거: int 처럼 작고 trivially copyable 한 타입은 복사 비용이 레지스터 한 개 수준이라, 참조로 받으면 오히려 포인터 한 단계 간접 접근과 잠재적 별칭(aliasing) 가능성만 더해진다. 영향: 불필요한 const 참조는 컴파일러가 값이 다른 경로로 바뀌지 않는다고 가정하지 못하게 해 최적화를 방해하고, 인터페이스 의도를 모호하게 한다. 대응: 작고 복사 비용이 낮은 입력 매개변수는 값으로 전달하고, 크거나 복사가 비싼 타입만 const 참조로 받는다.',
  'why_en':'Rationale: a small trivially copyable type like int costs about one register to copy, so passing it by reference instead adds a level of pointer indirection and potential aliasing. Impact: an unnecessary const reference prevents the compiler from assuming the value is not changed through another path, hindering optimization and obscuring interface intent. Fix: pass small, cheap-to-copy input parameters by value, reserving const reference for large or expensive-to-copy types.'},

 {'id':'A8-5-2','cat':'Required · Automated','compiles':True,
  'title':'초기화에는 중괄호 초기화(braced-init)를 사용한다',
  'title_en':'Braced-initialization shall be used for variable initialization',
  'bad': r"""#include <iostream>
int main() {
    int x = 3.9;   // double→int 좁히기 변환이 조용히 일어남 → 3, 소수부 소실
    std::cout << x << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int x{3};   // 중괄호 초기화 — 좁히기 변환을 컴파일 오류로 차단(int x{3.9}; 는 에러)
    std::cout << x << '\n';
}""",
  'why':'근거: 중괄호 초기화 {} 는 좁히기 변환(narrowing, 예: double→int, 넓은 정수→좁은 정수)을 컴파일 오류로 금지하는 반면, = 나 () 초기화는 이를 조용히 허용한다. 영향: int x = 3.9; 가 경고 없이 3 이 되는 것처럼 데이터 손실이 진단 없이 통과해, 정밀도·범위가 중요한 계산에서 결함이 된다. 대응: 변수 초기화에 일관되게 {} 를 사용해 좁히기 변환을 컴파일 타임에 잡아낸다.',
  'why_en':'Rationale: braced-initialization {} forbids narrowing conversions (e.g. double to int, wide to narrow integer) as a compile error, whereas = or () initialization allows them silently. Impact: data loss passes with no diagnostic — like int x = 3.9; becoming 3 without a warning — a defect in computations where precision or range matters. Fix: use {} consistently for variable initialization to catch narrowing conversions at compile time.'},

 {'id':'M0-1-1','cat':'Required · Automated','compiles':True,
  'title':'도달할 수 없는(unreachable) 코드를 두지 않는다',
  'title_en':'A project shall not contain unreachable code',
  'bad': r"""#include <iostream>
static int f(int x) {
    return x;
    std::cout << "after return\n";   // return 뒤 — 절대 실행되지 않는 죽은 코드
}
int main() { std::cout << f(3) << '\n'; }""",
  'good': r"""#include <iostream>
static int f(int x) {
    std::cout << "before return\n";   // 의미 있는 위치로 이동
    return x;
}
int main() { std::cout << f(3) << '\n'; }""",
  'why':'근거: return·throw·break 뒤에 오는, 어떤 입력으로도 실행될 수 없는 코드는 흐름상 도달 불가능하다. 영향: 도달 불가 코드는 보통 잘못된 조기 return 이나 흐름 오류의 신호이며, 실행될 것으로 믿고 작성한 로깅·정리 코드가 조용히 무시되어 버그가 숨는다. 대응: 도달 불가 코드를 제거하거나, 실행되어야 한다면 분기·순서를 바로잡아 도달 가능하게 만든다(컴파일러 -Wunreachable 계열 경고 활용).',
  'why_en':'Rationale: code following return, throw, or break that can never execute under any input is flow-unreachable. Impact: unreachable code usually signals a misplaced early return or a flow error, and logging or cleanup written in the belief it would run is silently ignored, hiding bugs. Fix: remove unreachable code, or if it should run, correct the branching/ordering to make it reachable (using compiler -Wunreachable-style warnings).'},

 {'id':'M0-1-3','cat':'Required · Automated','compiles':True,
  'title':'사용되지 않는 변수를 두지 않는다',
  'title_en':'A project shall not contain unused variables',
  'bad': r"""#include <iostream>
static int compute() { return 42; }
int main() {
    int tmp = compute();   // 선언·초기화했지만 어디서도 사용 안 됨
    int base = 10;
    std::cout << base << '\n';   // tmp 는 죽은 변수
}""",
  'good': r"""#include <iostream>
int main() {
    int base = 10;
    std::cout << base << '\n';   // 필요한 변수만 유지
}""",
  'why':'근거: 선언·초기화만 되고 한 번도 읽히지 않는 변수는 그 계산이 결과에 기여하지 않는 죽은 코드다. 영향: 미사용 변수는 흔히 빠뜨린 사용(예: tmp 를 써야 할 자리에 다른 값을 씀)이라는 진짜 버그의 신호이고, 코드를 어지럽혀 리뷰·유지보수를 방해한다. 대응: 미사용 변수를 제거하고, 부작용 때문에 호출은 필요하지만 결과가 불필요하면 결과를 받지 않도록 한다(또는 [[maybe_unused]] 로 의도 표시).',
  'why_en':'Rationale: a variable that is declared and initialized but never read is dead code whose computation does not contribute to the result. Impact: an unused variable often signals a real bug of missed use (e.g. writing another value where tmp should have been used) and clutters the code, hindering review and maintenance. Fix: remove unused variables, and when a call is needed for its side effect but its result is not, do not capture the result (or mark intent with [[maybe_unused]]).'},

 {'id':'M0-3-2','cat':'Required · Automated','compiles':True,
  'title':'함수가 오류 정보를 반환하면 호출부에서 검사한다',
  'title_en':'If a function generates error information, then that error information shall be tested',
  'bad': r"""#include <iostream>
#include <fstream>
int main() {
    std::ofstream f("/root/forbidden/out.txt");   // 열기 실패 가능(권한)
    f << "data";   // 실패 상태 미검사 — 쓰기가 조용히 버려짐
    std::cout << "thought it wrote\n";
}""",
  'good': r"""#include <iostream>
#include <fstream>
int main() {
    std::ofstream f("/root/forbidden/out.txt");
    if (!f) { std::cout << "open failed\n"; return 1; }   // 실패를 즉시 검사
    f << "data";
    std::cout << "wrote\n";
}""",
  'why':'근거: 오류 정보를 반환·설정하는 함수(또는 스트림 상태 플래그)의 결과를 검사하지 않으면, 실패가 발생했는지 알 수 없는 채로 다음 단계로 넘어간다. 영향: 파일 열기 실패 후에도 쓰기를 계속하면 데이터가 조용히 사라지고, 실패가 누적되어 일관성 깨짐·데이터 손상으로 이어지며 사후 원인 추적이 어렵다. 대응: 오류를 알리는 반환값·상태를 호출 직후 검사해 실패 경로를 명시적으로 처리한다.',
  'why_en':'Rationale: not testing the result of a function that returns or sets error information (or a stream state flag) moves on to the next step without knowing whether a failure occurred. Impact: continuing to write after a file open fails silently discards data, and accumulated failures lead to broken consistency and corruption that is hard to trace afterward. Fix: test the error-indicating return value or state right after the call and handle the failure path explicitly.'},

 {'id':'M5-0-2','cat':'Advisory · Automated','compiles':True,
  'title':'연산자 우선순위 의존을 괄호로 제한한다',
  'title_en':'Limited dependence should be placed on operator precedence rules in expressions',
  'bad': r"""#include <iostream>
int main() {
    int a = 1, b = 2, c = 1, d = 6;
    int r = a + b << c & d;   // +, <<, & 우선순위를 외워야 의미 파악
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int a = 1, b = 2, c = 1, d = 6;
    int r = ((a + b) << c) & d;   // 괄호로 평가 순서를 명시
    std::cout << r << '\n';
}""",
  'why':'근거: +, <<, & 처럼 우선순위가 직관적이지 않은 연산자들을 한 식에 섞으면, 괄호 없이는 평가 순서를 외워야만 의미를 알 수 있다. 영향: 독자나 유지보수자가 우선순위를 잘못 가정하면 식의 의미를 오독해 결함을 넣고, 특히 비트·시프트 연산이 섞이면 산술 우선순위와 헷갈리기 쉽다. 대응: 우선순위가 자명하지 않은 복합 표현식은 괄호로 평가 순서를 명시해 의도를 코드에 드러낸다.',
  'why_en':'Rationale: mixing operators with non-intuitive precedence such as +, <<, and & in one expression forces readers to memorize the evaluation order to know the meaning without parentheses. Impact: a reader or maintainer who assumes the wrong precedence misreads the expression and introduces defects, especially where bitwise and shift operators are confused with arithmetic precedence. Fix: parenthesize compound expressions whose precedence is not obvious to make the evaluation order explicit in the code.'},

 {'id':'M5-0-4','cat':'Required · Automated','compiles':True,
  'title':'암시적 정수 변환이 부호(signedness)를 바꾸지 않게 한다',
  'title_en':'An implicit integral conversion shall not change the signedness of the underlying type',
  'bad': r"""#include <iostream>
int main() {
    unsigned u = 1u;
    int s = -1;
    if (s < u) std::cout << "s < u\n";   // s 가 거대한 unsigned 로 변환 → 비교 뒤집힘
    else std::cout << "s >= u\n";        // 실제로 이쪽이 출력됨(직관과 반대)
}""",
  'good': r"""#include <iostream>
int main() {
    int s = -1;
    int u = 1;   // 부호를 통일(또는 명시적 캐스트로 의도 표현)
    if (s < u) std::cout << "s < u\n";   // -1 < 1 — 직관대로
    else std::cout << "s >= u\n";
}""",
  'why':'근거: 부호 있는 값과 없는 값을 한 식에서 비교·연산하면, 일반적 산술 변환 규칙에 따라 부호 있는 값이 부호 없는 타입으로 변환되어 음수가 거대한 양수가 된다. 영향: -1 < 1u 같은 비교가 거짓이 되는 등 결과가 직관과 정반대로 뒤집혀, 길이·인덱스 비교나 루프 종료 조건에서 경계 오류·무한 루프를 일으킨다. 대응: 비교·연산 대상의 부호를 통일하거나, 의도한 변환을 static_cast 로 명시하고 컴파일러 부호 변환 경고(-Wsign-conversion)를 켠다.',
  'why_en':'Rationale: comparing or operating on a signed and an unsigned value in one expression converts the signed value to the unsigned type under the usual arithmetic conversions, turning a negative number into a huge positive one. Impact: comparisons like -1 < 1u become false, flipping the result opposite to intuition and causing boundary errors or infinite loops in length/index comparisons or loop termination conditions. Fix: unify the signedness of the operands, or make the intended conversion explicit with static_cast and enable the compiler sign-conversion warning (-Wsign-conversion).'},

 {'id':'M5-0-15','cat':'Required · Automated','compiles':True,
  'title':'포인터 산술은 배열 첨자 형태로만 수행한다',
  'title_en':'Array indexing shall be the only form of pointer arithmetic',
  'bad': r"""#include <iostream>
int main() {
    int a[5] = {0, 1, 2, 3, 4};
    int* p = a;
    *(p + 3) = 99;   // 노골적 포인터 산술 — 경계 오류를 가리기 쉬움
    std::cout << a[3] << '\n';
}""",
  'good': r"""#include <iostream>
int main() {
    int a[5] = {0, 1, 2, 3, 4};
    int* p = a;
    p[3] = 99;   // 배열 첨자 표기 — 인덱스 의도가 분명
    std::cout << a[3] << '\n';
}""",
  'why':'근거: p[i] 와 *(p+i) 는 의미가 같지만, 명시적 포인터 덧셈은 인덱스가 무엇이고 그것이 배열 범위 안인지에 대한 의도를 흐린다. 영향: 노골적 포인터 산술은 경계를 벗어난 오프셋을 평범한 덧셈처럼 보이게 해 버퍼 오버런을 숨기고, 정적 분석기가 인덱스 범위를 추론하기 어렵게 만든다. 대응: 포인터 산술을 배열 첨자 표기 p[i] 로만 표현해 인덱스 의도를 드러내고, 가능하면 std::array·범위 기반 접근으로 경계 검사를 돕는다.',
  'why_en':'Rationale: p[i] and *(p+i) mean the same, but explicit pointer addition obscures the intent of what the index is and whether it is within the array bounds. Impact: explicit pointer arithmetic makes an out-of-bounds offset look like ordinary addition, hiding buffer overruns and making it harder for static analyzers to infer the index range. Fix: express pointer arithmetic only as array indexing p[i] to reveal index intent, and prefer std::array or range-based access to aid bounds checking where possible.'},

 {'id':'M5-2-8','cat':'Required · Automated','compiles':True,
  'title':'객체 포인터를 정수나 void* 로 무분별하게 변환하지 않는다',
  'title_en':'An object pointer shall not be converted to an integer or unrelated pointer type',
  'bad': r"""#include <iostream>
#include <cstdint>
struct Widget { int id = 7; };
int main() {
    Widget w;
    auto n = reinterpret_cast<std::uintptr_t>(&w);   // 포인터를 정수로 — 타입 추적성 상실
    Widget* back = reinterpret_cast<Widget*>(n);     // 복원 시 타입 안전성 없음
    std::cout << back->id << '\n';
}""",
  'good': r"""#include <iostream>
struct Widget { int id = 7; };
static void use(Widget* w) { std::cout << w->id << '\n'; }
int main() {
    Widget w;
    use(&w);   // 포인터를 원래 타입 그대로 전달
}""",
  'why':'근거: 객체 포인터를 정수(uintptr_t)나 무관한 포인터 타입으로 바꿔 보관·복원하면, 컴파일러의 타입 검사를 우회하고 원래 가리키던 타입 정보를 잃는다. 영향: 정수로 왕복한 포인터는 잘못된 타입으로 복원되거나, 객체 수명·정렬과 무관하게 다뤄져 미정의 동작·추적 불가능한 손상을 부른다. 대응: 포인터는 원래의 정적 타입으로 유지·전달하고, 다형성이 필요하면 공통 기반 타입 포인터나 std::variant·태그된 핸들 같은 타입 안전한 추상을 사용한다.',
  'why_en':'Rationale: converting an object pointer to an integer (uintptr_t) or an unrelated pointer type to store and restore it bypasses the compiler type checks and loses the original pointed-to type information. Impact: a pointer round-tripped through an integer may be restored as the wrong type or handled regardless of object lifetime and alignment, causing undefined behaviour and untraceable corruption. Fix: keep and pass pointers in their original static type, and when polymorphism is needed use a common base pointer or a type-safe abstraction such as std::variant or a tagged handle.'},

 {'id':'M5-14-1','cat':'Required · Automated','compiles':True,
  'title':'&&/|| 의 우변에 부작용을 두지 않는다',
  'title_en':'The right hand operand of a && or || operator shall not contain side effects',
  'bad': r"""#include <iostream>
static int g_calls = 0;
static int fetch() { ++g_calls; return 5; }
int main() {
    bool ok = false;
    int n = 0;
    if (ok && (n = fetch()) > 0) std::cout << "branch\n";   // ok 가 거짓 → 우변 미실행
    std::cout << "n=" << n << " calls=" << g_calls << '\n';  // n=0 calls=0 — 부작용 누락
}""",
  'good': r"""#include <iostream>
static int g_calls = 0;
static int fetch() { ++g_calls; return 5; }
int main() {
    bool ok = false;
    int n = fetch();   // 부작용을 조건 밖에서 무조건 수행
    if (ok && n > 0) std::cout << "branch\n";
    std::cout << "n=" << n << " calls=" << g_calls << '\n';  // n=5 calls=1
}""",
  'why':'근거: && 와 || 는 단락 평가(short-circuit)를 하므로, 좌변 결과에 따라 우변이 아예 실행되지 않을 수 있다. 영향: 우변에 대입·증가·함수 호출 같은 부작용을 두면 그것이 조건부로만 일어나, 예제처럼 n=fetch() 가 건너뛰어져 변수·카운터가 기대와 달라지는 미묘한 버그가 된다. 대응: 부작용은 논리 연산 밖의 독립 문장에서 무조건 수행하고, && / || 의 피연산자는 부작용 없는 순수 조건식으로 유지한다.',
  'why_en':'Rationale: && and || short-circuit, so the right operand may not execute at all depending on the left operand result. Impact: putting side effects like assignment, increment, or a function call in the right operand makes them happen only conditionally, so as in the example n=fetch() is skipped and variables or counters differ from expectation — a subtle bug. Fix: perform side effects unconditionally in a separate statement outside the logical operator and keep the operands of && / || pure, side-effect-free conditions.'},

 {'id':'M5-18-1','cat':'Required · Automated','compiles':True,
  'title':'쉼표 연산자를 사용하지 않는다',
  'title_en':'The comma operator shall not be used',
  'bad': r"""#include <iostream>
static int a() { std::cout << "a "; return 1; }
static int b() { std::cout << "b "; return 2; }
int main() {
    int x = (a(), b());   // 쉼표 연산자 — a() 부작용이 한 식에 숨고 결과는 b()
    std::cout << "x=" << x << '\n';
}""",
  'good': r"""#include <iostream>
static int a() { std::cout << "a "; return 1; }
static int b() { std::cout << "b "; return 2; }
int main() {
    a();           // 부작용을 독립 문장으로 드러냄
    int x = b();
    std::cout << "x=" << x << '\n';
}""",
  'why':'근거: 쉼표 연산자 (e1, e2) 는 e1 을 평가해 부작용만 취하고 버린 뒤 e2 의 값을 결과로 주는데, 이 구조는 부작용과 결과가 한 식에 뒤섞여 잘 드러나지 않는다. 영향: 독자가 첫 피연산자의 부작용을 놓치거나, 쉼표를 함수 인자 구분자와 혼동해 의미를 오독하기 쉬워 분석·리뷰가 어려워진다. 대응: 쉼표 연산자를 쓰지 말고 각 부작용·계산을 별도 문장으로 분리해 평가 순서와 결과를 명확히 한다.',
  'why_en':'Rationale: the comma operator (e1, e2) evaluates e1 only for its side effect, discards it, and yields the value of e2, a structure that mixes side effects and result into one expression where they are hard to see. Impact: readers miss the side effect of the first operand or confuse the comma with an argument separator, easily misreading the meaning and making analysis and review harder. Fix: avoid the comma operator and split each side effect and computation into separate statements to make the evaluation order and result clear.'},
]
