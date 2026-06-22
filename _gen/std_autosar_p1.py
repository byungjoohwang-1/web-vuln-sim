# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트1: A0~A8·M0~M5) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'A0-1-1','cat':'Required · Automated',
  'title':'결과가 사용되지 않는 값(useless assignment)을 두지 않는다',
  'bad': r"""int x = compute();
x = 5;                // 직전 compute() 결과를 쓰지 않고 덮어씀""",
  'good': r"""int x = 5;            // 필요한 값만 대입""",
  'why':'읽히기 전에 덮어쓰이는 대입은 죽은 계산이며 논리 오류(대입 누락)의 신호다. 사용되지 않는 값 계산을 제거한다.'},

 {'id':'A0-1-2','cat':'Required · Automated',
  'title':'비void 함수의 반환값을 사용한다',
  'bad': r"""resize(buf, n);       // 성공 여부 반환을 무시""",
  'good': r"""if (!resize(buf, n)) { handle_error(); }""",
  'why':'반환값을 무시하면 오류·결과를 감지하지 못한 채 진행한다. 의미 있는 반환값은 사용하거나 명시적으로 버린다.'},

 {'id':'A0-1-3','cat':'Required · Automated',
  'title':'정의된 모든 함수는 사용되어야 한다',
  'bad': r"""static void legacy_helper() { ... }   // 어디서도 호출 안 됨""",
  'good': r"""// 사용되지 않는 함수는 제거""",
  'why':'호출되지 않는 정적 함수는 죽은 코드로 유지보수를 어지럽힌다. 미사용 함수는 삭제한다.'},

 {'id':'A0-4-1','cat':'Required · Non-automated',
  'title':'부동소수 구현은 IEEE 754(IEC 60559)를 따라야 한다',
  'bad': r"""// IEEE 미준수 플랫폼/플래그에서 NaN·Inf 동작에 의존""",
  'good': r"""static_assert(std::numeric_limits<double>::is_iec559,
              "IEEE 754 float required");""",
  'why':'부동소수 동작이 IEEE 754를 따르지 않으면 반올림·특수값 처리가 달라져 결과가 흔들린다. 표준 준수를 정적으로 검증한다.'},

 {'id':'A2-7-2','cat':'Required · Automated',
  'title':'코드 섹션을 주석 처리(commented-out)로 비활성화하지 않는다',
  'bad': r"""// transform(d);
// commit(d);
notify(d);""",
  'good': r"""#if FEATURE_TRANSFORM
transform(d);
commit(d);
#endif
notify(d);""",
  'why':'주석으로 막은 코드는 의도가 불명확하고 버전관리로 충분히 추적된다. 조건부 컴파일로 처리하거나 제거한다.'},

 {'id':'A2-10-1','cat':'Required · Automated',
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지 않게 한다',
  'bad': r"""int count = 0;
void f() { int count = 5; use(count); }   // 외부 count 가림""",
  'good': r"""int g_count = 0;
void f() { int local = 5; use(local); }""",
  'why':'바깥 식별자를 같은 이름으로 가리면 잘못된 변수를 참조하는 결함을 부른다. 내부 식별자는 다른 이름을 쓴다.'},

 {'id':'A2-13-1','cat':'Required · Automated',
  'title':'표준에 정의된 이스케이프 시퀀스만 사용한다',
  'bad': r"""const char* s = "line\qbreak";   // \q 는 비표준 이스케이프""",
  'good': r"""const char* s = "line\tbreak";   // 표준 이스케이프""",
  'why':'표준에 없는 이스케이프 시퀀스는 미정의 동작이거나 구현마다 다르게 처리된다. 정의된 이스케이프만 사용한다.'},

 {'id':'A2-13-3','cat':'Required · Automated',
  'title':'wchar_t 타입을 사용하지 않는다',
  'bad': r"""wchar_t buf[16];      // 폭이 플랫폼마다 다름(16/32비트)""",
  'good': r"""char16_t buf16[16];   // 폭이 고정된 문자 타입
char32_t buf32[16];""",
  'why':'wchar_t의 크기는 구현정의(Windows 16비트, Linux 32비트)라 이식성과 인코딩 처리를 어렵게 한다. char16_t/char32_t 등 폭이 고정된 타입을 쓴다.'},

 {'id':'A3-1-1','cat':'Required · Automated',
  'title':'헤더는 자체적으로(self-contained) 포함 순서와 무관하게 컴파일되어야 한다',
  'bad': r"""// b.h — A 타입을 쓰지만 a.h를 포함하지 않음
struct B { A member; };""",
  'good': r"""// b.h
#include "a.h"
struct B { A member; };""",
  'why':'필요한 헤더를 포함하지 않으면 포함 순서에 따라 컴파일이 깨진다. 각 헤더는 필요한 의존성을 직접 포함해 자체 완결되게 한다.'},

 {'id':'A3-3-2','cat':'Required · Automated',
  'title':'정적/스레드-지역 객체는 상수 초기화 가능해야 한다',
  'bad': r"""static std::string g = build_name();   // 동적 초기화 — 순서 문제""",
  'good': r"""static constexpr int g_limit = 100;   // 상수 초기화""",
  'why':'정적 객체의 동적 초기화는 번역단위 간 초기화 순서 문제(static init order fiasco)를 일으킨다. 상수식으로 초기화하거나 지연 초기화를 쓴다.'},

 {'id':'A4-7-1','cat':'Required · Automated',
  'title':'정수 표현식이 데이터 손실을 일으키지 않게 한다',
  'bad': r"""std::uint8_t b = large_value;   // 8비트 초과분 절단""",
  'good': r"""if (large_value <= 0xFF) {
    std::uint8_t b = static_cast<std::uint8_t>(large_value);
}""",
  'why':'넓은 값을 좁은 정수에 넣으면 절단·부호 변화로 데이터가 손실된다. 범위를 검사하고 명시적으로 변환한다.'},

 {'id':'A4-10-1','cat':'Required · Automated',
  'title':'널 포인터 상수로는 nullptr 만 사용한다',
  'bad': r"""int* p = NULL;        // 또는 0
if (p == 0) { ... }""",
  'good': r"""int* p = nullptr;
if (p == nullptr) { ... }""",
  'why':'0/NULL은 정수와 포인터 문맥이 섞여 오버로드 해석 오류를 부른다. 타입 안전한 nullptr만 사용한다.'},

 {'id':'A5-0-1','cat':'Required · Automated',
  'title':'표현식의 값이 평가 순서에 의존하지 않게 한다',
  'bad': r"""int i = 0;
f(i++, i++);          // 인자 평가 순서 미명세""",
  'good': r"""int a = i++;
int b = i++;
f(a, b);""",
  'why':'한 식에서 같은 객체를 여러 번 수정하면 평가 순서에 따라 결과가 달라진다. 부작용을 분리해 순서를 확정한다.'},

 {'id':'A5-1-1','cat':'Required · Automated',
  'title':'리터럴 값은 명명된 상수로 정의해 사용한다(매직 넘버 금지)',
  'bad': r"""if (speed > 120) { warn(); }   // 매직 넘버""",
  'good': r"""constexpr int kSpeedLimit = 120;
if (speed > kSpeedLimit) { warn(); }""",
  'why':'코드에 흩어진 매직 넘버/문자열은 의미가 불명확하고 변경 시 누락을 부른다. 의미 있는 명명 상수로 정의한다.'},

 {'id':'A5-1-2','cat':'Required · Automated',
  'title':'스코프를 벗어나는 람다에서 변수를 참조로 캡처하지 않는다',
  'bad': r"""std::function<int()> make() {
    int x = 1;
    return [&]{ return x; };   // x 참조가 무효화""",
  'good': r"""std::function<int()> make() {
    int x = 1;
    return [x]{ return x; };   // 값 캡처""",
  'why':'호출보다 먼저 소멸하는 지역 변수를 참조 캡처하면 댕글링 참조가 된다. 스코프를 벗어나는 람다는 값으로 캡처한다.'},

 {'id':'A5-2-2','cat':'Required · Automated',
  'title':'전통적 C 스타일 캐스트를 사용하지 않는다',
  'bad': r"""double d = 3.9;
int n = (int)d;       // C 스타일 캐스트""",
  'good': r"""double d = 3.9;
int n = static_cast<int>(d);""",
  'why':'C 스타일 캐스트는 어떤 변환(const 제거·재해석 등)인지 드러나지 않아 위험을 숨긴다. 의도가 명확한 C++ 캐스트를 쓴다.'},

 {'id':'A5-2-3','cat':'Required · Automated',
  'title':'const_cast 로 const/volatile 한정을 제거하지 않는다',
  'bad': r"""void g(const int& v) {
    int& r = const_cast<int&>(v);
    r = 9;            // const 대상 수정 — 미정의""",
  'good': r"""void g(int& v) { v = 9; }   // 수정 필요하면 비-const 인자""",
  'why':'const_cast로 한정을 제거하고 실제 const 객체를 수정하면 미정의 동작이다. 수정이 필요하면 비-const 인터페이스를 쓴다.'},

 {'id':'A5-2-4','cat':'Required · Automated',
  'title':'reinterpret_cast 를 사용하지 않는다',
  'bad': r"""float f = 1.0f;
auto bits = *reinterpret_cast<std::uint32_t*>(&f);   // 별칭 위반""",
  'good': r"""float f = 1.0f;
std::uint32_t bits;
std::memcpy(&bits, &f, sizeof bits);""",
  'why':'reinterpret_cast는 엄격 별칭·정렬 규칙을 어겨 미정의 동작을 부른다. 비트 재해석은 memcpy나 std::bit_cast로 안전하게 한다.'},

 {'id':'A5-2-6','cat':'Required · Automated',
  'title':'&& 와 || 의 피연산자는 단순하지 않으면 괄호로 묶는다',
  'bad': r"""if (a && b || c) { ... }   // 우선순위 혼동""",
  'good': r"""if ((a && b) || c) { ... }""",
  'why':'&&와 ||를 괄호 없이 섞으면 우선순위를 오해하기 쉽다. 복합 피연산자를 괄호로 묶어 의도를 명확히 한다.'},

 {'id':'A5-3-2','cat':'Required · Automated',
  'title':'널 포인터를 역참조하지 않는다',
  'bad': r"""Node* n = find(k);
n->v = 0;             // NULL 미검사""",
  'good': r"""Node* n = find(k);
if (n != nullptr) { n->v = 0; }""",
  'why':'널 포인터 역참조는 크래시·미정의 동작이다. 역참조 전에 nullptr 여부를 확인한다.'},

 {'id':'A5-6-1','cat':'Required · Automated',
  'title':'0으로 나누는 일이 없도록 한다',
  'bad': r"""int q = sum / count;   // count==0 가능""",
  'good': r"""if (count != 0) { int q = sum / count; }""",
  'why':'0으로 나누거나 나머지를 구하면 미정의 동작(대개 크래시)이다. 나누기 전 분모가 0이 아님을 확인한다.'},

 {'id':'A5-16-1','cat':'Required · Automated',
  'title':'삼항 연산자를 다른 식의 하위 표현식으로 사용하지 않는다',
  'bad': r"""int r = base + (cond ? 10 : 20) * factor;   // 가독성 저하""",
  'good': r"""int adj = cond ? 10 : 20;
int r = base + adj * factor;""",
  'why':'삼항 연산자를 큰 식 안에 끼워 넣으면 우선순위·의도 파악이 어려워진다. 별도 변수로 분리해 가독성을 확보한다.'},

 {'id':'A6-4-1','cat':'Required · Automated',
  'title':'enum 을 다루는 switch 는 모든 열거자에 대한 case 를 가진다',
  'bad': r"""switch (state) {   // State에 Idle/Run/Stop 있는데 Stop 누락
    case State::Idle: a(); break;
    case State::Run:  b(); break;
}""",
  'good': r"""switch (state) {
    case State::Idle: a(); break;
    case State::Run:  b(); break;
    case State::Stop: c(); break;
}""",
  'why':'열거자 일부를 누락하면 새 값 추가 시 조용히 처리가 빠진다. 모든 열거자를 명시적으로 처리한다(default보다 전수 처리 권장).'},

 {'id':'A6-5-3','cat':'Advisory · Automated',
  'title':'do-while 문을 사용하지 않는다',
  'bad': r"""do { step(); } while (cond);   // 본문이 항상 1회 실행 — 실수 유발""",
  'good': r"""while (cond) { step(); }""",
  'why':'do-while은 조건이 본문 뒤에 있어 최소 1회 실행되는 점을 간과하기 쉽다. 선조건 while로 흐름을 명확히 한다.'},

 {'id':'A6-6-1','cat':'Required · Automated',
  'title':'goto 문을 사용하지 않는다',
  'bad': r"""    if (err) goto cleanup;
    work();
cleanup:
    release();""",
  'good': r"""// RAII로 자동 정리, 구조적 제어 사용
{
    Guard g;
    if (!err) { work(); }
}""",
  'why':'goto는 비선형 제어 흐름으로 분석을 어렵게 한다. RAII와 구조적 제어문으로 대체한다.'},

 {'id':'A7-1-1','cat':'Required · Automated',
  'title':'변경되지 않는 변수/멤버는 const(또는 constexpr)로 선언한다',
  'bad': r"""int radius = 5;       // 이후 수정 없음에도 비-const""",
  'good': r"""const int radius = 5;""",
  'why':'불변 값을 const로 표시하지 않으면 실수로 수정되거나 의도가 흐려진다. const/constexpr로 불변성을 강제한다.'},

 {'id':'A7-1-6','cat':'Required · Automated',
  'title':'typedef 대신 using 별칭을 사용한다',
  'bad': r"""typedef std::map<int, std::string> Table;""",
  'good': r"""using Table = std::map<int, std::string>;""",
  'why':'using 별칭은 typedef보다 읽기 쉽고 템플릿 별칭을 지원한다. 일관되게 using을 사용한다.'},

 {'id':'A7-1-7','cat':'Required · Automated',
  'title':'한 선언문에는 하나의 변수/이름만 선언한다',
  'bad': r"""int* a, b;            // a는 포인터, b는 int — 오해 유발""",
  'good': r"""int* a;
int  b;""",
  'why':'한 줄에 여러 변수를 선언하면 포인터 표기 등에서 타입을 오해하기 쉽다. 선언을 하나씩 분리한다.'},

 {'id':'A7-2-2','cat':'Required · Automated',
  'title':'열거형의 기반 타입(underlying type)을 명시한다',
  'bad': r"""enum class Mode { A, B, C };   // 기반 타입 미명시""",
  'good': r"""enum class Mode : std::uint8_t { A, B, C };""",
  'why':'기반 타입을 명시하지 않으면 크기·표현이 불명확해 직렬화·ABI에 영향을 준다. 명시적 기반 타입으로 표현을 고정한다.'},

 {'id':'A7-2-3','cat':'Required · Automated',
  'title':'열거형은 범위 지정 enum class 로 선언한다',
  'bad': r"""enum Color { Red, Green };   // 비범위 — 전역 이름 오염·암시적 변환""",
  'good': r"""enum class Color { Red, Green };""",
  'why':'비범위 enum은 열거자가 둘러싼 범위로 새어나오고 정수로 암시 변환되어 오류를 부른다. enum class로 범위·타입 안전을 확보한다.'},

 {'id':'A7-5-2','cat':'Required · Automated',
  'title':'함수는 직접/간접 재귀를 사용하지 않는다',
  'bad': r"""std::uint64_t fib(int n) {
    return (n < 2) ? n : fib(n-1) + fib(n-2);   // 재귀 — 스택 불확정""",
  'good': r"""std::uint64_t fib(int n) {
    std::uint64_t a = 0, b = 1;
    for (int i = 0; i < n; ++i) { auto t = a + b; a = b; b = t; }
    return a;
}""",
  'why':'재귀는 최대 스택 사용량을 정적으로 보장하기 어려워 안전필수 시스템에 부적합하다. 반복으로 변환한다.'},

 {'id':'A7-6-1','cat':'Required · Automated',
  'title':'[[noreturn]] 함수는 반환하지 않아야 한다',
  'bad': r"""[[noreturn]] void fail() {
    if (recoverable) return;   // noreturn인데 반환 — 미정의""",
  'good': r"""[[noreturn]] void fail() {
    std::terminate();          // 항상 비반환
}""",
  'why':'[[noreturn]]으로 표시한 함수가 실제로 반환하면 미정의 동작이 된다. 모든 경로에서 비반환(종료·throw)을 보장한다.'},

 {'id':'A8-4-1','cat':'Required · Automated',
  'title':'함수를 C 스타일 가변인자(...)로 정의하지 않는다',
  'bad': r"""void logf(const char* fmt, ...);   // 타입 비안전""",
  'good': r"""template <typename... Args>
void logf(const char* fmt, const Args&... args);""",
  'why':'... 가변인자는 타입 검사가 없어 잘못된 추출로 미정의 동작이 된다. 가변 템플릿으로 타입 안전하게 작성한다.'},

 {'id':'A8-4-7','cat':'Required · Automated',
  'title':'작고 trivially copyable 한 입력 매개변수는 값으로 전달한다',
  'bad': r"""void use(const int& x);   // 작은 타입에 const 참조 — 불필요한 간접화""",
  'good': r"""void use(int x);""",
  'why':'작고 복사 비용이 낮은 타입을 참조로 받으면 간접 접근 비용과 별칭 가능성만 늘어난다. 값으로 전달해 명확성과 최적화를 돕는다.'},

 {'id':'A8-5-2','cat':'Required · Automated',
  'title':'초기화에는 중괄호 초기화(braced-init)를 사용한다',
  'bad': r"""int x = 3.9;          // 좁히기 변환이 조용히 일어남(3)""",
  'good': r"""int x{3};             // 좁히기 변환은 컴파일 오류로 차단""",
  'why':'중괄호 초기화는 좁히기 변환을 컴파일 오류로 막아 데이터 손실을 예방한다. 일관되게 {} 초기화를 사용한다.'},

 {'id':'M0-1-1','cat':'Required · Automated',
  'title':'도달할 수 없는(unreachable) 코드를 두지 않는다',
  'bad': r"""int f(int x) {
    return x;
    log("after");      // 도달 불가""",
  'good': r"""int f(int x) {
    log("before");
    return x;
}""",
  'why':'return/throw 이후의 도달 불가 코드는 논리 오류의 신호다. 제거하거나 흐름을 바로잡는다.'},

 {'id':'M0-1-3','cat':'Required · Automated',
  'title':'사용되지 않는 변수를 두지 않는다',
  'bad': r"""int tmp = compute();   // 어디서도 사용 안 됨
return base;""",
  'good': r"""return base;""",
  'why':'사용되지 않는 변수는 의도(누락된 사용)를 의심하게 하고 코드를 어지럽힌다. 미사용 변수는 제거한다.'},

 {'id':'M0-3-2','cat':'Required · Automated',
  'title':'함수가 오류 정보를 반환하면 호출부에서 검사한다',
  'bad': r"""file.open(path);      // 실패 상태 미검사
file.write(data);""",
  'good': r"""if (!file.open(path)) { return Error::Open; }
file.write(data);""",
  'why':'오류 표시를 반환하는 함수의 결과를 무시하면 실패 상태로 진행해 손상이 누적된다. 반환된 오류 정보를 즉시 검사한다.'},

 {'id':'M5-0-2','cat':'Advisory · Automated',
  'title':'연산자 우선순위 의존을 괄호로 제한한다',
  'bad': r"""int r = a + b << c & d;   // 우선순위 혼동""",
  'good': r"""int r = ((a + b) << c) & d;""",
  'why':'복합 표현식의 우선순위를 외워서 의존하면 오독·오류를 부른다. 괄호로 평가 순서를 명시한다.'},

 {'id':'M5-0-4','cat':'Required · Automated',
  'title':'암시적 정수 변환이 부호(signedness)를 바꾸지 않게 한다',
  'bad': r"""unsigned u = 1u;
int s = -1;
if (s < u) { ... }    // s가 큰 양수로 변환됨""",
  'good': r"""int s = -1;
int u = 1;
if (s < u) { ... }""",
  'why':'부호 있는/없는 값을 섞으면 음수가 거대한 양수로 변환되어 비교가 뒤집힌다. 부호를 통일하거나 명시적으로 변환한다.'},

 {'id':'M5-0-15','cat':'Required · Automated',
  'title':'포인터 산술은 배열 첨자 형태로만 수행한다',
  'bad': r"""int* p = a;
*(p + 3) = 0;         // 포인터 산술""",
  'good': r"""int* p = a;
p[3] = 0;             // 배열 첨자""",
  'why':'노골적인 포인터 산술은 경계 오류를 숨기고 가독성을 해친다. 배열 첨자 표기로 의도를 드러낸다.'},

 {'id':'M5-2-8','cat':'Required · Automated',
  'title':'객체 포인터를 정수나 void* 로 무분별하게 변환하지 않는다',
  'bad': r"""Widget* w = get();
auto n = reinterpret_cast<std::uintptr_t>(w);   // 정수 변환""",
  'good': r"""Widget* w = get();
use(w);               // 포인터 타입 그대로 사용""",
  'why':'포인터를 정수/void*로 바꿔 보관·복원하면 타입 안전성과 추적성이 무너진다. 포인터는 원래 타입으로 유지한다.'},

 {'id':'M5-14-1','cat':'Required · Automated',
  'title':'&&/|| 의 우변에 부작용을 두지 않는다',
  'bad': r"""if (ok && (n = fetch()) > 0) { ... }   // 단락 시 n 미할당""",
  'good': r"""n = fetch();
if (ok && n > 0) { ... }""",
  'why':'단락 평가로 우변이 실행되지 않을 수 있어 부작용이 조건부로 누락된다. 부작용은 논리 연산 밖으로 뺀다.'},

 {'id':'M5-18-1','cat':'Required · Automated',
  'title':'쉼표 연산자를 사용하지 않는다',
  'bad': r"""x = (a(), b());       // 부작용이 한 식에 숨음""",
  'good': r"""a();
x = b();""",
  'why':'쉼표 연산자는 부작용과 평가 순서를 한 식에 숨겨 가독성과 분석을 해친다. 문장을 분리한다.'},
]
