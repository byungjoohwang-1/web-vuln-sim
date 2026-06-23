# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트2: 섹션 9~16) — 위반/준수 예제, 사내 교육용·자체작성

규칙 ID/의무도/제목 출처(교차검증):
  - MathWorks Polyspace Bug Finder, "MISRA C++:2023 Rules and Directives"
  - Perforce Helix QAC "MISRA_M2CPP" enforcement 매핑표 (의무도·결정가능성)
  - Klocwork "MISRA C++:2023 checker reference"
  - CodeAnt AI MISRA-CPP-2023 컴플라이언스 문서
규범 본문(verbatim) 미사용 — 제목은 한국어 의역, 예제·해설은 전부 자체작성(C++17).

강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17` 기준.
헤더 익명 네임스페이스(10.3.1)처럼 단일 파일로 성립하지 않는 규칙은 초점 스니펫으로 둔다.
"""
RULES = [
 # ── 섹션 9: 문장(Statements) ───────────────────────────────────────────
 {'id':'Rule 9.2.1','cat':'Required · Decidable','compiles':True,
  'title':'명시적 형변환을 단독 표현식 문장으로 쓰지 않는다',
  'title_en':'An explicit type conversion shall not be used as a standalone expression statement',
  'bad': r"""#include <iostream>
static void poll(int raw){
    static_cast<double>(raw);   // 변환 결과를 버리는 의미 없는 표현식 문장 — 효과 없음
    std::cout << "polled\n";
}
int main(){ poll(42); }""",
  'good': r"""#include <iostream>
static double poll(int raw){
    double scaled = static_cast<double>(raw) * 0.01;   // 변환 결과를 실제로 사용
    return scaled;
}
int main(){ std::cout << poll(42) << '\n'; }""",
  'why':'결과를 사용하지 않는 캐스트 단독 문장은 아무 효과가 없으면서, 대입을 빠뜨렸거나 다른 부작용을 의도했을 가능성을 숨긴다. 변환 결과를 변수에 담거나 반환해 실제로 사용하도록 작성한다.',
  'why_en':'A standalone cast statement whose result is unused has no effect while hiding a likely missed assignment or intended side effect. Store the conversion result in a variable or return it so it is actually used.'},

 {'id':'Rule 9.3.1','cat':'Required · Decidable','compiles':True,
  'title':'반복문·선택문의 본문은 복합문(중괄호 블록)이어야 한다',
  'title_en':'The body of an iteration or selection statement shall be a compound statement',
  'bad': r"""#include <iostream>
static int sum(const int* a, int n){
    int s = 0;
    for (int i = 0; i < n; ++i)
        s += a[i];        // 중괄호 없는 본문 — 줄 추가 시 범위가 어긋나기 쉬움
    return s;
}
int main(){ int a[3] = {1,2,3}; std::cout << sum(a, 3) << '\n'; }""",
  'good': r"""#include <iostream>
static int sum(const int* a, int n){
    int s = 0;
    for (int i = 0; i < n; ++i) {
        s += a[i];        // 복합문 블록으로 본문 범위를 고정
    }
    return s;
}
int main(){ int a[3] = {1,2,3}; std::cout << sum(a, 3) << '\n'; }""",
  'why':'중괄호 없는 단일 문 본문은 나중에 문장을 추가할 때 들여쓰기만 맞춘 채 본문 밖에 놓이는 결함(dangling)을 부른다. 반복문·선택문 본문을 항상 복합문 블록으로 감싸 범위를 코드로 고정한다.',
  'why_en':'A braceless single-statement body invites the dangling defect where a later-added statement is indented but falls outside the body. Always wrap iteration and selection bodies in a compound-statement block to fix the scope in code.'},

 {'id':'Rule 9.4.1','cat':'Required · Decidable','compiles':True,
  'title':'if … else if 연쇄는 마지막 else로 종결한다',
  'title_en':'All if ... else if chains shall be terminated with an else statement',
  'bad': r"""#include <iostream>
static int classify(int x){
    int r = -1;
    if (x > 0)       r = 1;
    else if (x < 0)  r = 2;   // x==0 경로 미처리 — -1 이 의도인지 불명확
    return r;
}
int main(){ std::cout << classify(0) << '\n'; }""",
  'good': r"""#include <iostream>
static int classify(int x){
    int r;
    if (x > 0)       r = 1;
    else if (x < 0)  r = 2;
    else             r = 0;   // 모든 경우를 명시적으로 처리
    return r;
}
int main(){ std::cout << classify(0) << '\n'; }""",
  'why':'마지막 else 가 없는 if-else if 연쇄는 어느 분기에도 맞지 않는 입력을 아무 처리 없이 통과시켜, 오류 상황이 조용히 무시되고 디버깅을 어렵게 한다. 마지막 else 로 나머지 모든 경우를 명시적으로 처리한다.',
  'why_en':'An if-else if chain without a final else lets inputs matching no branch pass with no handling, silently ignoring error cases and hampering debugging. Terminate with a final else that explicitly handles all remaining cases.'},

 {'id':'Rule 9.4.2','cat':'Required · Decidable','compiles':True,
  'title':'switch 문은 적절한 구조(default·break·case 라벨)를 갖춘다',
  'title_en':'A switch statement shall be a well-formed switch statement',
  'bad': r"""#include <iostream>
static int speed(int gear){
    int v = 0;
    switch (gear) {
    case 1: v = 10;   // break 누락 → case 2 로 흘러내림
    case 2: v = 20; break;
    }                 // default 없음
    return v;
}
int main(){ std::cout << speed(1) << '\n'; }""",
  'good': r"""#include <iostream>
static int speed(int gear){
    int v = 0;
    switch (gear) {
    case 1:  v = 10; break;
    case 2:  v = 20; break;
    default: v = 0;  break;   // 각 case break + default 제공
    }
    return v;
}
int main(){ std::cout << speed(1) << '\n'; }""",
  'why':'break 누락은 의도치 않은 fall-through 로 한 case 가 다음 case 까지 실행시키고, default 부재는 정의되지 않은 값을 조용히 무시해 오류를 숨긴다. 각 case 를 break 로 닫고 default 절을 두어 모든 입력을 처리한다.',
  'why_en':'A missing break causes unintended fall-through where one case runs into the next, and a missing default silently ignores undefined values, hiding errors. Close each case with break and provide a default to handle all inputs.'},

 {'id':'Rule 9.5.1','cat':'Advisory · Decidable','compiles':True,
  'title':'전통적 for 문은 단순하게 작성한다',
  'title_en':'A traditional for-loop should be simple',
  'bad': r"""#include <iostream>
static double avg(const double* a, int n){
    double s = 0.0;
    for (int i = 0, j = 0; i < n; ++i, j += 2) {   // 다중 카운터
        s += a[i];
        if (a[i] < 0.0) i += 1;   // 본문에서 카운터 수정 — 반복 횟수 추론 곤란
    }
    return n ? s / n : 0.0;
}
int main(){ double a[3] = {1,2,3}; std::cout << avg(a, 3) << '\n'; }""",
  'good': r"""#include <iostream>
static double avg(const double* a, int n){
    double s = 0.0;
    for (int i = 0; i < n; ++i) {   // 단일 카운터, 본문에서 미수정
        s += a[i];
    }
    return n ? s / n : 0.0;
}
int main(){ double a[3] = {1,2,3}; std::cout << avg(a, 3) << '\n'; }""",
  'why':'다중 카운터나 본문 내 카운터 변경은 루프가 몇 번 도는지, 언제 끝나는지 정적으로 추론하기 어렵게 만들어 오프바이원·무한루프 결함을 숨긴다. 카운터는 하나로, 증감은 for 헤더에서만 수행한다.',
  'why_en':'Multiple counters or modifying the counter in the body make it hard to statically reason about how many times the loop runs and when it ends, hiding off-by-one and infinite-loop defects. Use a single counter and change it only in the for header.'},

 {'id':'Rule 9.5.2','cat':'Required · Decidable','compiles':True,
  'title':'범위 기반 for의 범위식은 함수 호출을 최대 1회만 포함한다',
  'title_en':'A range-based for loop’s range-initializer should contain at most one function call',
  'bad': r"""#include <vector>
#include <iostream>
static std::vector<int> load_a(){ return {1, 2}; }
static std::vector<int> load_b(){ return {3, 4}; }
static std::vector<int> merge(std::vector<int> x, std::vector<int> y){
    x.insert(x.end(), y.begin(), y.end()); return x;
}
int main(){
    int s = 0;
    for (int v : merge(load_a(), load_b())) { s += v; }   // 호출이 여럿 — 임시객체 수명·순서 모호
    std::cout << s << '\n';
}""",
  'good': r"""#include <vector>
#include <iostream>
static std::vector<int> load_a(){ return {1, 2}; }
static std::vector<int> load_b(){ return {3, 4}; }
static std::vector<int> merge(std::vector<int> x, std::vector<int> y){
    x.insert(x.end(), y.begin(), y.end()); return x;
}
int main(){
    auto data = merge(load_a(), load_b());   // 범위 객체를 먼저 확정
    int s = 0;
    for (int v : data) { s += v; }           // 범위식은 단순한 lvalue
    std::cout << s << '\n';
}""",
  'why':'범위 기반 for 의 범위식에 임시객체를 만드는 함수 호출이 여럿이면, 임시객체의 수명과 평가 순서가 모호해져 순회 도중 댕글링 참조 위험이 생긴다. 범위 객체를 먼저 변수로 확정한 뒤 그 lvalue 를 순회한다.',
  'why_en':'When a range-based for’s range-initializer contains several calls that create temporaries, their lifetimes and evaluation order become unclear, risking a dangling reference during iteration. Bind the range object to a variable first and iterate over that lvalue.'},

 {'id':'Rule 9.6.1','cat':'Advisory · Decidable','compiles':True,
  'title':'goto 문은 사용하지 않는다',
  'title_en':'The goto statement should not be used',
  'bad': r"""#include <iostream>
static int find(const int* a, int n, int key){
    int idx = -1;
    for (int i = 0; i < n; ++i) {
        if (a[i] == key) { idx = i; goto done; }   // 비구조적 제어 흐름
    }
done:
    return idx;
}
int main(){ int a[3] = {1,2,3}; std::cout << find(a, 3, 2) << '\n'; }""",
  'good': r"""#include <iostream>
static int find(const int* a, int n, int key){
    int idx = -1;
    for (int i = 0; i < n; ++i) {
        if (a[i] == key) { idx = i; break; }   // 구조적 제어로 대체
    }
    return idx;
}
int main(){ int a[3] = {1,2,3}; std::cout << find(a, 3, 2) << '\n'; }""",
  'why':'goto 는 제어 흐름을 비구조적으로 만들어 어디로 점프하는지 추적·검증을 어렵게 하고 초기화·정리 순서를 무너뜨릴 수 있다. break/continue/return 같은 구조적 제어나 함수 분리로 같은 의도를 표현한다.',
  'why_en':'goto makes control flow non-structured, making jumps hard to trace and verify and able to break initialization/cleanup order. Express the same intent with structured control (break/continue/return) or by factoring into functions.'},

 {'id':'Rule 9.6.2','cat':'Required · Decidable','compiles':True,
  'title':'goto는 같은 또는 둘러싼 블록의 라벨만 참조한다',
  'title_en':'A goto statement shall reference a label in a surrounding block',
  'bad': r"""#include <iostream>
static void do_work(){ std::cout << "work\n"; }
static void run(bool c){
    if (c) {
        goto inner;   // 더 안쪽 블록의 라벨로 점프 — 초기화를 건너뛸 수 있음
    }
    {
inner:
        do_work();
    }
}
int main(){ run(true); }""",
  'good': r"""#include <iostream>
static void do_work(){ std::cout << "work\n"; }
static void run(bool /*c*/){
    do_work();   // goto 없이 직접 호출 — 구조가 단순
}
int main(){ run(true); }""",
  'why':'바깥에서 더 안쪽 블록의 라벨로 점프하면 그 블록 안 객체의 초기화를 건너뛰어 미초기화 객체 사용 등 정의되지 않은 흐름을 만든다. 점프를 제거하거나, 불가피하면 같은/둘러싼 블록의 라벨만 참조한다.',
  'why_en':'Jumping from outside into a more deeply nested block bypasses initialization of objects in that block, creating undefined flow such as use of uninitialized objects. Remove the jump, or if unavoidable, only reference labels in the same or an enclosing block.'},

 {'id':'Rule 9.6.3','cat':'Required · Decidable','compiles':True,
  'title':'goto는 본문에서 나중에 선언된 라벨로만 전방 점프한다',
  'title_en':'A goto statement shall jump forward to a label declared later in the same function',
  'bad': r"""#include <iostream>
static bool attempt(){ static int c = 0; return ++c >= 3; }
static void retry(){
    int tries = 0;
again:                       // 후방 점프 대상 — 암묵적 루프를 형성
    if (++tries < 5) {
        if (!attempt()) goto again;   // 뒤에서 앞으로 점프 → 종료 보장 흐려짐
    }
}
int main(){ retry(); std::cout << "done\n"; }""",
  'good': r"""#include <iostream>
static bool attempt(){ static int c = 0; return ++c >= 3; }
static void retry(){
    for (int tries = 0; tries < 5; ++tries) {   // 명시적 루프 — 종료 조건이 분명
        if (attempt()) return;
    }
}
int main(){ retry(); std::cout << "done\n"; }""",
  'why':'후방 goto 는 명시적 반복문 없이 암묵적 루프를 만들어 반복 횟수와 종료 조건을 코드만으로 파악하기 어렵게 한다. 반복이 필요하면 for/while 같은 명시적 반복문을 사용하고, goto 는 전방 점프로만 제한한다.',
  'why_en':'A backward goto forms an implicit loop without an explicit loop construct, making iteration count and termination hard to read from the code. Use explicit loops (for/while) when iteration is needed and restrict goto to forward jumps.'},

 {'id':'Rule 9.6.4','cat':'Mandatory · Undecidable','compiles':True,
  'title':'[[noreturn]] 함수는 절대 반환하지 않는다',
  'title_en':'A function declared [[noreturn]] shall not return',
  'bad': r"""#include <cstdlib>
[[noreturn]] static void fail(int code){
    if (code == 0) {
        return;        // noreturn 인데 정상 반환 경로 존재 — 미정의 동작
    }
    std::abort();
}
int main(){ (void)&fail; return 0; }""",
  'good': r"""#include <cstdlib>
[[noreturn]] static void fail(int /*code*/){
    std::abort();      // 모든 경로가 비반환(abort)으로 종료
}
int main(){ (void)&fail; return 0; }""",
  'why':'[[noreturn]] 로 선언한 함수가 실제로 반환하면, 호출자는 절대 돌아오지 않는다는 가정 하에 생성된 코드로 인해 미정의 동작에 빠진다. 모든 실행 경로가 abort·throw·exit·무한 루프 등으로 반드시 종료되도록 보장한다.',
  'why_en':'If a function declared [[noreturn]] actually returns, the caller — built on the assumption it never comes back — enters undefined behaviour. Ensure every execution path terminates via abort, throw, exit, or an infinite loop.'},

 {'id':'Rule 9.6.5','cat':'Mandatory · Undecidable','compiles':True,
  'title':'비-void 반환형 함수는 모든 경로에서 값을 반환한다',
  'title_en':'A function with non-void return type shall return a value on all paths',
  'bad': r"""#include <iostream>
static int sign(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
}   // x==0 경로에서 반환 없음 — 호출자가 쓰레기 값을 읽음
int main(){ std::cout << sign(0) << '\n'; }""",
  'good': r"""#include <iostream>
static int sign(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;   // 모든 경로가 값을 반환
}
int main(){ std::cout << sign(0) << '\n'; }""",
  'why':'값을 반환하지 않고 함수 끝에 도달하면 호출자는 스택·레지스터에 남은 불확정 값을 결과로 읽어 미정의 동작이 된다. 모든 분기에서 명시적으로 값을 반환하도록 보장한다.',
  'why_en':'Falling off the end without returning a value makes the caller read an indeterminate leftover from the stack/registers — undefined behaviour. Ensure a value is explicitly returned on every branch.'},

 # ── 섹션 10: 선언(Declarations) ──────────────────────────────────────────
 {'id':'Rule 10.0.1','cat':'Advisory · Decidable','compiles':True,
  'title':'한 선언에서 둘 이상의 변수/멤버를 선언하지 않는다',
  'title_en':'Only one variable or member shall be declared in a declaration',
  'bad': r"""#include <iostream>
int main(){
    int* p, q;      // p 는 포인터, q 는 int — 결합이 직관과 다름
    int  a = 0, b;  // b 는 미초기화
    p = nullptr;
    q = 0; b = 0;
    std::cout << q << a << b << '\n';
    (void)p;
}""",
  'good': r"""#include <iostream>
int main(){
    int* p = nullptr;   // 선언당 하나, 각자 초기화
    int  q = 0;
    int  a = 0;
    int  b = 0;
    std::cout << q << a << b << '\n';
    (void)p;
}""",
  'why':'한 줄에 여러 객체를 선언하면 int* p, q; 에서 q 가 포인터가 아닌 점처럼 포인터 결합을 오해하기 쉽고, 일부 변수의 초기화를 빠뜨리기도 쉽다. 선언당 하나의 변수만 두고 각각 초기화한다.',
  'why_en':'Declaring multiple objects in one statement invites misreading pointer binding (in int* p, q; only p is a pointer) and makes it easy to miss initializing some of them. Declare one variable per declaration and initialize each.'},

 {'id':'Rule 10.1.1','cat':'Advisory · Decidable','compiles':True,
  'title':'포인터·참조 매개변수의 대상 타입은 적절히 const 한정한다',
  'title_en':'The target type of a pointer or lvalue reference parameter should be const-qualified where appropriate',
  'bad': r"""#include <iostream>
static int length(char* s){      // 수정하지 않는데 비-const → const 인자 못 받음
    int n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
int main(){ char buf[] = "hello"; std::cout << length(buf) << '\n'; }""",
  'good': r"""#include <iostream>
static int length(const char* s){   // 읽기 전용 의도를 const 로 표현
    int n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
int main(){ const char* s = "hello"; std::cout << length(s) << '\n'; }""",
  'why':'대상을 수정하지 않는데 const 를 빠뜨리면 함수의 의도(읽기 전용)가 드러나지 않고, const 객체나 리터럴을 인자로 받지 못해 호출 측 유연성이 떨어진다. 읽기 전용 대상은 const 로 한정해 의도와 인터페이스를 명확히 한다.',
  'why_en':'Omitting const where the target is not modified hides the read-only intent and prevents accepting const objects or literals as arguments, reducing caller flexibility. Const-qualify read-only targets to make intent and interface explicit.'},

 {'id':'Rule 10.1.2','cat':'Required · Decidable','compiles':True,
  'title':'volatile 한정자는 적절한 경우에만 사용한다',
  'title_en':'The volatile qualifier shall be used only where necessary',
  'bad': r"""#include <iostream>
int main(){
    volatile int tmp = 0;   // 단순 지역 누적기에 불필요한 volatile — 최적화 차단
    for (int i = 0; i < 100; ++i) {
        tmp += i;
    }
    std::cout << tmp << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    int sum = 0;            // 일반 연산은 비-volatile
    for (int i = 0; i < 100; ++i) {
        sum += i;
    }
    std::cout << sum << '\n';
    // volatile 은 메모리맵 하드웨어 레지스터처럼 외부 요인으로 값이 바뀌는 객체에만 사용
}""",
  'why':'외부 요인으로 값이 바뀌지 않는 일반 객체에 volatile 을 붙이면 컴파일러의 최적화(레지스터 보관·중복 제거)를 막아 성능만 떨어뜨리고, volatile 의 의미를 오해하게 만든다. volatile 은 하드웨어 레지스터·시그널 핸들러 공유 변수처럼 진짜 필요한 곳에만 적용한다.',
  'why_en':'Applying volatile to an ordinary object whose value is not changed by external factors blocks compiler optimizations (register caching, redundancy removal), costing performance and obscuring volatile’s meaning. Use volatile only where truly needed, such as hardware registers or signal-handler-shared variables.'},

 {'id':'Rule 10.2.1','cat':'Required · Decidable','compiles':True,
  'title':'열거형은 기반 정수 타입을 명시해 정의한다',
  'title_en':'An enumeration shall be defined with an explicit underlying type',
  'bad': r"""#include <iostream>
enum class Mode {        // 기반 타입 미지정 — 크기·범위가 구현 의존적
    Idle, Run, Stop
};
int main(){ Mode m = Mode::Run; std::cout << static_cast<int>(m) << '\n'; }""",
  'good': r"""#include <iostream>
#include <cstdint>
enum class Mode : std::uint8_t {   // 기반 타입 명시 — 크기·표현 범위 고정
    Idle, Run, Stop
};
int main(){ Mode m = Mode::Run; std::cout << static_cast<int>(m) << '\n'; }""",
  'why':'기반 타입을 명시하지 않은 열거형은 크기와 표현 범위가 구현에 따라 달라져, 직렬화·하드웨어 인터페이스·이식 시 레이아웃이 어긋난다. 명시적 underlying type(예: std::uint8_t)을 지정해 표현을 고정한다.',
  'why_en':'An enumeration without an explicit underlying type has implementation-defined size and range, so its layout diverges across serialization, hardware interfaces, and ports. Specify an explicit underlying type (e.g., std::uint8_t) to fix the representation.'},

 {'id':'Rule 10.2.2','cat':'Advisory · Decidable','compiles':True,
  'title':'범위 없는(unscoped) 열거형은 선언하지 않는다',
  'title_en':'Unscoped enumerations should not be declared',
  'bad': r"""#include <iostream>
enum Color { Red, Green, Blue };   // 전역 이름공간 오염 + int 로 암묵 변환
int main(){
    int x = Green;   // 열거자가 정수로 새어 나감 — 이름 충돌·오용 위험
    std::cout << x << '\n';
}""",
  'good': r"""#include <iostream>
enum class Color { Red, Green, Blue };   // 범위 지정 — 이름공간 보호
int main(){
    Color c = Color::Green;   // 명시적 한정, 암묵 정수 변환 없음
    std::cout << static_cast<int>(c) << '\n';
}""",
  'why':'unscoped enum 은 열거자 이름을 둘러싼 이름공간에 그대로 노출해 충돌을 일으키고, 정수로 암묵 변환되어 잘못된 비교·산술을 조용히 허용한다. enum class(scoped enum)를 사용해 이름을 한정하고 암묵 변환을 차단한다.',
  'why_en':'An unscoped enum leaks enumerator names into the enclosing namespace causing clashes, and implicitly converts to int, silently allowing wrong comparisons and arithmetic. Use enum class (scoped enum) to qualify names and block implicit conversion.'},

 {'id':'Rule 10.2.3','cat':'Required · Decidable','compiles':True,
  'title':'고정 기반 타입 없는 unscoped 열거형의 수치값을 사용하지 않는다',
  'title_en':'The numeric value of an unscoped enumeration without a fixed underlying type shall not be used',
  'bad': r"""#include <iostream>
enum Flags { A, B, C };   // 고정 기반 타입 없음
int main(){
    Flags f = B;
    int r = f + 1;        // 열거값을 산술 수치로 사용 — 표현 범위 불명확
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
enum class Flags : int { A, B, C };   // 고정 기반 타입 명시
int main(){
    Flags f = Flags::B;
    int r = static_cast<int>(f) + 1;  // 명시적 변환 후 산술
    std::cout << r << '\n';
}""",
  'why':'기반 타입이 고정되지 않은 unscoped 열거형은 표현 범위가 구현 정의라, 그 값을 직접 산술에 쓰면 범위·승격 규칙이 불명확해 이식 시 다른 결과가 날 수 있다. 고정 기반 타입을 가진 enum class 로 선언하고 수치가 필요할 때만 명시적으로 변환한다.',
  'why_en':'An unscoped enumeration without a fixed underlying type has an implementation-defined range, so using its value directly in arithmetic leaves range and promotion rules unclear, risking different results across ports. Declare an enum class with a fixed underlying type and convert explicitly only when a numeric value is needed.'},

 {'id':'Rule 10.3.1','cat':'Advisory · Decidable',
  'title':'헤더 파일에는 익명 네임스페이스를 두지 않는다',
  'title_en':'There should be no unnamed namespaces in header files',
  'bad': r"""// util.hpp  (비준수)
namespace {
    int counter = 0;            // 이 헤더를 포함하는 모든 번역단위마다 별도 사본 생성
    inline void tick() { ++counter; }   // TU 마다 다른 counter 를 증가 → ODR 혼란
}""",
  'good': r"""// util.hpp  (준수) — 헤더에는 선언만
namespace util {
    void tick();
}

// util.cpp — 정의는 한 곳에, 내부 연결은 파일 정적으로
namespace util {
    static int counter = 0;
    void tick() { ++counter; }
}""",
  'why':'헤더의 익명 네임스페이스는 그 헤더를 포함하는 번역단위마다 내부 연결의 별도 실체(별도 counter)를 만들어, 모두가 같은 상태를 공유한다는 착각과 ODR 혼란을 일으킨다. 헤더에는 선언만 두고 정의·내부 상태는 소스 파일에 둔다.',
  'why_en':'An unnamed namespace in a header creates a separate internal-linkage instance (a separate counter) in every translation unit that includes it, causing the illusion of shared state and ODR confusion. Keep only declarations in headers and put definitions and internal state in source files.'},

 {'id':'Rule 10.4.1','cat':'Required · Decidable','compiles':True,
  'title':'asm 선언(인라인 어셈블리)을 사용하지 않는다',
  'title_en':'The asm declaration shall not be used',
  'bad': r"""#include <iostream>
static int read_low(){
    int lo = 0;
    asm volatile("rdtsc" : "=a"(lo));   // 인라인 어셈블리 — 이식성·정적분석 저하
    return lo;
}
int main(){ std::cout << (read_low() != 0) << '\n'; }""",
  'good': r"""#include <chrono>
#include <iostream>
static long read_low(){
    auto now = std::chrono::steady_clock::now().time_since_epoch();   // 이식성 있는 표준 API
    return static_cast<long>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
}
int main(){ std::cout << (read_low() != 0) << '\n'; }""",
  'why':'인라인 어셈블리는 특정 CPU·컴파일러에 묶여 이식성을 깨뜨리고, 정적 분석 도구가 의미를 파악하지 못해 검증 사각지대를 만든다. 표준 라이브러리(예: <chrono>)나 잘 캡슐화된 컴파일러 내장함수로 대체한다.',
  'why_en':'Inline assembly ties code to a specific CPU and compiler, breaking portability, and static-analysis tools cannot interpret it, creating a verification blind spot. Replace it with the standard library (e.g., <chrono>) or well-encapsulated compiler intrinsics.'},

 # ── 섹션 11: 객체·타입(Objects / Types) ─────────────────────────────────
 {'id':'Rule 11.3.1','cat':'Advisory · Decidable','compiles':True,
  'title':'C 스타일 배열 타입 변수를 선언하지 않는다',
  'title_en':'A C-style array shall not be declared',
  'bad': r"""#include <iostream>
static double mean(int n){
    double buf[64];          // C 스타일 배열 — 경계 정보 없음
    double s = 0.0;
    for (int i = 0; i < n; ++i) { buf[i] = i; s += buf[i]; }   // n>64 면 오버런
    return n ? s / n : 0.0;
}
int main(){ std::cout << mean(8) << '\n'; }""",
  'good': r"""#include <array>
#include <numeric>
#include <iostream>
static double mean(){
    std::array<double, 64> buf{};   // 크기·경계를 아는 컨테이너
    for (std::size_t i = 0; i < buf.size(); ++i) buf[i] = static_cast<double>(i);
    double s = std::accumulate(buf.begin(), buf.end(), 0.0);
    return s / static_cast<double>(buf.size());
}
int main(){ std::cout << mean() << '\n'; }""",
  'why':'C 스타일 배열은 자신의 크기 정보를 갖지 않고 포인터로 쉽게 붕괴(decay)되어 경계 검사 없이 오버런을 일으킨다. std::array(고정 크기)·std::vector(가변 크기)는 size()와 경계 검사 인터페이스를 제공해 안전하게 다룰 수 있다.',
  'why_en':'A C-style array carries no size information and decays to a pointer, enabling overruns with no bounds checking. std::array (fixed size) and std::vector (dynamic) provide size() and bounds-aware interfaces for safe handling.'},

 {'id':'Rule 11.3.2','cat':'Advisory · Decidable','compiles':True,
  'title':'객체 선언의 포인터 간접 단계는 2단계를 넘지 않는다',
  'title_en':'The declaration of an object should contain no more than two levels of pointer indirection',
  'bad': r"""#include <iostream>
static int build(int*** grid){   // 3중 포인터 — 소유권·수명 추론 곤란
    return grid != nullptr;
}
int main(){ std::cout << build(nullptr) << '\n'; }""",
  'good': r"""#include <vector>
#include <iostream>
static int build(const std::vector<std::vector<int>>& grid){   // 컨테이너로 표현
    return static_cast<int>(grid.size());
}
int main(){ std::vector<std::vector<int>> g; std::cout << build(g) << '\n'; }""",
  'why':'2단계를 넘는 포인터 간접(int***)은 각 단계가 무엇을, 누가 소유하며, 언제 해제되는지 추론하기 매우 어려워 누수·댕글링을 부른다. 중첩 컨테이너(std::vector<std::vector<...>>)나 전용 타입으로 표현해 간접 단계를 낮춘다.',
  'why_en':'More than two levels of pointer indirection (int***) make it very hard to reason about what each level points to, who owns it, and when it is freed, inviting leaks and dangling. Express it with nested containers (std::vector<std::vector<...>>) or a dedicated type to reduce indirection.'},

 {'id':'Rule 11.6.1','cat':'Advisory · Decidable','compiles':True,
  'title':'모든 변수는 초기화한다',
  'title_en':'All variables should be initialized',
  'bad': r"""#include <iostream>
static int scale(int k){
    int factor;          // 미초기화
    if (k > 0) factor = 2;
    return k * factor;   // k<=0 이면 미초기화 값 사용 — 비결정적
}
int main(){ std::cout << scale(-1) << '\n'; }""",
  'good': r"""#include <iostream>
static int scale(int k){
    int factor = 1;      // 선언 시점에 초기화
    if (k > 0) factor = 2;
    return k * factor;
}
int main(){ std::cout << scale(-1) << '\n'; }""",
  'why':'미초기화 변수는 일부 경로에서 스택에 남은 비결정적 값을 읽어, 실행마다 결과가 달라지는 재현 불가 버그를 만든다. 모든 변수를 선언 시점에 의미 있는 초기값으로 초기화한다.',
  'why_en':'An uninitialized variable read on some path uses non-deterministic leftover stack values, producing irreproducible bugs that vary by run. Initialize every variable with a meaningful value at the point of declaration.'},

 {'id':'Rule 11.6.2','cat':'Mandatory · Undecidable','compiles':True,
  'title':'객체의 값은 설정되기 전에 읽지 않는다',
  'title_en':'The value of an object shall not be read before it has been set',
  'bad': r"""#include <iostream>
static int compute(bool on){
    int v;                 // 미설정
    if (on) v = 10;
    return v + 1;          // on==false 면 미설정 값을 읽음 — 미정의 동작
}
int main(){ std::cout << compute(false) << '\n'; }""",
  'good': r"""#include <iostream>
static int compute(bool on){
    int v = 0;             // 읽기 전 반드시 설정
    if (on) v = 10;
    return v + 1;
}
int main(){ std::cout << compute(false) << '\n'; }""",
  'why':'설정되기 전의 객체를 읽으면 불확정 값을 사용하게 되어 동작이 미정의가 되고, 컴파일러 최적화에 따라 예측 불가한 결과가 나온다(필수 규칙). 모든 읽기 경로에서 사전 대입을 보장한다.',
  'why_en':'Reading an object before it is set uses an indeterminate value — undefined behaviour with results unpredictable under optimization (a mandatory rule). Guarantee a prior assignment on every read path.'},

 {'id':'Rule 11.6.3','cat':'Required · Decidable','compiles':True,
  'title':'열거자 목록에서 암묵적으로 결정되는 값은 서로 중복되지 않는다',
  'title_en':'Within an enumerator list, the value of an implicitly-specified enumeration constant shall be unique',
  'bad': r"""#include <iostream>
enum class E : int {
    A = 1,
    B,        // 자동으로 2
    C = 2     // B 와 값 충돌(둘 다 2)
};
int main(){ std::cout << (static_cast<int>(E::B) == static_cast<int>(E::C)) << '\n'; }""",
  'good': r"""#include <iostream>
enum class E : int {
    A = 1,
    B = 2,    // 명시적·고유 값
    C = 3
};
int main(){ std::cout << (static_cast<int>(E::B) == static_cast<int>(E::C)) << '\n'; }""",
  'why':'명시 값과 암묵(앞 값+1) 값이 섞여 두 열거자가 같은 정수가 되면, switch 분기나 값-기반 테이블 매핑에서 둘을 구분하지 못해 논리 오류가 숨는다. 각 열거자의 값이 고유하도록 명시한다.',
  'why_en':'When explicit and implicit (previous+1) values mix so two enumerators share the same integer, switch branches or value-based table mappings cannot distinguish them, hiding logic errors. Specify values so each enumerator is unique.'},

 # ── 섹션 12: 비트필드·union ──────────────────────────────────────────────
 {'id':'Rule 12.2.1','cat':'Advisory · Decidable','compiles':True,
  'title':'비트필드는 선언하지 않는다',
  'title_en':'Bit-fields should not be declared',
  'bad': r"""#include <iostream>
struct Reg {
    unsigned enable : 1;   // 비트필드 — 배치·패딩·부호가 구현 의존적
    unsigned mode   : 3;
    unsigned        : 4;
};
int main(){ Reg r{1u, 2u}; std::cout << r.mode << '\n'; }""",
  'good': r"""#include <cstdint>
#include <iostream>
struct Reg { std::uint8_t value; };   // 명시적 정수 + 마스크 상수로 표현
constexpr std::uint8_t ENABLE = 0x01u;
constexpr std::uint8_t MODE   = 0x0Eu;   // bits 1..3
int main(){
    Reg r{0};
    r.value |= ENABLE;
    r.value = static_cast<std::uint8_t>((r.value & ~MODE) | (2u << 1));
    std::cout << ((r.value & MODE) >> 1) << '\n';
}""",
  'why':'비트필드는 메모리 내 배치 순서, 부호 처리, 패딩이 모두 구현 의존적이라 같은 코드가 컴파일러·엔디안마다 다른 비트를 가리켜 하드웨어 레지스터 매핑·직렬화에서 깨진다. 명시적 부호 없는 정수와 마스크 연산으로 비트 위치를 코드에 고정한다.',
  'why_en':'Bit-fields have implementation-defined layout order, sign handling, and padding, so the same code addresses different bits across compilers and endianness, breaking hardware-register mapping and serialization. Use explicit unsigned integers with mask operations to fix bit positions in code.'},

 {'id':'Rule 12.2.2','cat':'Required · Decidable','compiles':True,
  'title':'비트필드를 쓴다면 적절한 타입(명시적 부호/크기)을 사용한다',
  'title_en':'If a bit-field is used, it shall have an appropriate type',
  'bad': r"""#include <iostream>
struct Flags {
    int a : 1;   // 부호 있는 int 비트필드 — 1비트 부호 표현이 모호
    int b : 2;
};
int main(){ Flags f{0, 1}; std::cout << f.b << '\n'; }""",
  'good': r"""#include <cstdint>
#include <iostream>
struct Flags {
    std::uint8_t a : 1;   // 부호 없는 고정폭 타입
    std::uint8_t b : 2;
};
int main(){ Flags f{0u, 1u}; std::cout << static_cast<int>(f.b) << '\n'; }""",
  'why':'부호 있는 정수나 구현정의 타입의 비트필드는 표현 범위와 부호 동작이 모호해, 같은 비트 폭이라도 값 해석이 컴파일러마다 달라진다. 비트필드가 불가피하면 std::uint8_t 같은 부호 없는 고정폭 타입을 기반으로 사용한다.',
  'why_en':'A bit-field of signed or implementation-defined type has ambiguous range and sign behaviour, so the same bit width is interpreted differently across compilers. When a bit-field is unavoidable, base it on an unsigned fixed-width type such as std::uint8_t.'},

 {'id':'Rule 12.2.3','cat':'Required · Decidable','compiles':True,
  'title':'부호 있는 정수형 명명 비트필드의 길이를 1비트로 두지 않는다',
  'title_en':'A named bit-field with signed integer type shall not have a length of one bit',
  'bad': r"""#include <iostream>
struct S {
    signed int flag : 1;   // 부호 1비트 → 값이 0 또는 -1, 1 을 넣어도 -1
};
int main(){ S s{}; s.flag = 1; std::cout << s.flag << '\n'; }""",
  'good': r"""#include <iostream>
struct S {
    unsigned int flag : 1;   // 부호 없는 1비트 → 0 또는 1
};
int main(){ S s{}; s.flag = 1u; std::cout << s.flag << '\n'; }""",
  'why':'부호 있는 1비트 비트필드는 값을 담을 비트가 부호 비트뿐이라 표현 가능한 값이 0 과 -1 로 제한되어, flag=1 을 넣어도 -1 로 저장되는 직관 위배가 생긴다. 1비트 플래그는 항상 부호 없는 타입으로 선언한다.',
  'why_en':'A signed one-bit bit-field has only the sign bit to hold a value, limiting representable values to 0 and -1, so assigning flag=1 stores -1 — counterintuitive. Always declare one-bit flags with an unsigned type.'},

 {'id':'Rule 12.3.1','cat':'Required · Decidable','compiles':True,
  'title':'union 키워드를 사용하지 않는다',
  'title_en':'The union keyword shall not be used',
  'bad': r"""#include <iostream>
union Packet {        // 활성 멤버를 추적하지 못함 — 타입 안전 깨짐
    int   asInt;
    float asFloat;
};
int main(){
    Packet p; p.asInt = 1065353216;
    std::cout << p.asFloat << '\n';   // asInt 로 썼는데 asFloat 읽기 — 사실상 타입 퍼닝
}""",
  'good': r"""#include <variant>
#include <iostream>
using Packet = std::variant<int, float>;   // 타입 안전 합집합
static float read(const Packet& p){
    return std::holds_alternative<float>(p) ? std::get<float>(p) : 0.0f;
}
int main(){ Packet p = 1.0f; std::cout << read(p) << '\n'; }""",
  'why':'union 은 어느 멤버가 현재 유효한지 자체적으로 추적하지 못해, 쓴 멤버와 다른 멤버를 읽는 타입 혼동·미정의 읽기를 쉽게 허용한다. std::variant 는 활성 타입을 추적하고 잘못된 접근을 검출해 타입 안전한 합집합을 제공한다.',
  'why_en':'A union does not track which member is currently active, easily allowing type confusion and undefined reads where a member other than the one written is read. std::variant tracks the active type and detects wrong access, providing a type-safe union.'},

 # ── 섹션 13: 상속(Derived classes) ──────────────────────────────────────
 {'id':'Rule 13.1.1','cat':'Advisory · Decidable','compiles':True,
  'title':'가상 상속(virtual base)을 사용하지 않는다',
  'title_en':'Virtual base classes should not be used',
  'bad': r"""#include <iostream>
struct Base { int v{0}; };
struct A : virtual Base {};   // 가상 상속 — 객체 레이아웃·초기화 순서가 복잡
struct B : virtual Base {};
struct D : A, B {};
int main(){ D d; d.v = 5; std::cout << d.v << '\n'; }""",
  'good': r"""#include <iostream>
struct Base { int v{0}; };
struct D {                    // 가상 상속 대신 합성(composition)으로 공유
    Base shared;
};
int main(){ D d; d.shared.v = 5; std::cout << d.shared.v << '\n'; }""",
  'why':'가상 상속은 공유 기반 서브객체를 위해 추가 포인터·복잡한 초기화 순서를 도입해 객체 레이아웃을 어렵게 만들고 검증 부담과 미묘한 초기화 버그를 키운다. 공유 구조가 필요하면 합성(멤버로 포함)으로 단순화한다.',
  'why_en':'Virtual inheritance introduces extra pointers and a complex initialization order for the shared base subobject, complicating object layout and increasing verification burden and subtle init bugs. When a shared structure is needed, simplify with composition (holding it as a member).'},

 {'id':'Rule 13.1.2','cat':'Required · Decidable','compiles':True,
  'title':'접근 가능한 기반 클래스를 가상·비가상으로 동시에 두지 않는다',
  'title_en':'An accessible base class shall not be both virtual and non-virtual in the same hierarchy',
  'bad': r"""#include <iostream>
struct Base { int v{0}; };
struct A : virtual Base {};
struct B : Base {};            // 비가상
struct D : A, B {};            // Base 가 가상+비가상 혼재 → 서브객체 중복·모호
int main(){ D d; d.B::v = 1; std::cout << d.B::v << '\n'; }""",
  'good': r"""#include <iostream>
struct Base { int v{0}; };
struct A : virtual Base {};
struct B : virtual Base {};    // 일관되게 가상으로 — 단일 공유 서브객체
struct D : A, B {};
int main(){ D d; d.v = 1; std::cout << d.v << '\n'; }""",
  'why':'같은 기반 클래스가 한 계층에서 가상과 비가상으로 섞여 상속되면 가상 경로의 공유 서브객체와 비가상 경로의 별도 서브객체가 동시에 생겨, 멤버 접근이 모호해지고 데이터가 둘로 갈려 불일치가 발생한다. 상속 방식을 일관되게(모두 가상 또는 모두 비가상) 통일한다.',
  'why_en':'When the same base is inherited both virtually and non-virtually in one hierarchy, a shared subobject from the virtual path coexists with a separate subobject from the non-virtual path, making member access ambiguous and splitting data into two inconsistent copies. Make the inheritance consistent (all virtual or all non-virtual).'},

 {'id':'Rule 13.3.1','cat':'Required · Decidable','compiles':True,
  'title':'멤버 함수는 virtual/override/final 지정자를 적절히(셋 중 하나만) 사용한다',
  'title_en':'A function that overrides shall be declared with override or final but not virtual',
  'bad': r"""#include <iostream>
struct Base { virtual void f(){ std::cout << "B\n"; } virtual ~Base() = default; };
struct Derived : Base {
    virtual void f() override { std::cout << "D\n"; }   // virtual 과 override 중복 지정
};
int main(){ Derived d; d.f(); }""",
  'good': r"""#include <iostream>
struct Base { virtual void f(){ std::cout << "B\n"; } virtual ~Base() = default; };
struct Derived : Base {
    void f() override { std::cout << "D\n"; }   // override 하나만 명시
};
int main(){ Derived d; d.f(); }""",
  'why':'재정의 함수에 virtual 과 override 를 함께 쓰면 의미가 중복되어 의도(새 가상 함수인지, 재정의인지)가 흐려지고 일관성이 떨어진다. 재정의는 override, 더 이상 재정의 금지는 final 로 하나만 명시해 의도를 분명히 한다.',
  'why_en':'Specifying both virtual and override on an overriding function is redundant and blurs intent (a new virtual function vs. an override) and consistency. Mark overrides with override, and seal further overriding with final — exactly one, to state intent clearly.'},

 {'id':'Rule 13.3.2','cat':'Required · Decidable','compiles':True,
  'title':'재정의 가상 함수는 다른 기본 인자를 지정하지 않는다',
  'title_en':'Parameters in an overriding virtual function shall not specify different default arguments',
  'bad': r"""#include <iostream>
struct Base { virtual int f(int x = 1){ return x; } virtual ~Base() = default; };
struct Derived : Base {
    int f(int x = 2) override { return x; }   // 기본 인자가 기반과 다름
};
int main(){
    Derived d; Base& b = d;
    std::cout << b.f() << ' ' << d.f() << '\n';   // 1 2 — 정적 타입에 따라 기본값이 갈림
}""",
  'good': r"""#include <iostream>
struct Base { virtual int f(int x = 1){ return x; } virtual ~Base() = default; };
struct Derived : Base {
    int f(int x = 1) override { return x; }   // 동일 기본 인자
};
int main(){
    Derived d; Base& b = d;
    std::cout << b.f() << ' ' << d.f() << '\n';   // 1 1 — 일관
}""",
  'why':'기본 인자는 호출 식의 정적 타입을 기준으로 결정되는데, 실제 호출되는 함수는 동적 타입의 재정의본이므로, 기반과 파생의 기본값이 다르면 같은 호출이 정적 타입에 따라 다른 인자로 실행되어 예측 불가해진다. 재정의에서는 기본 인자를 기반과 일치시킨다(가능하면 기본 인자 미사용).',
  'why_en':'Default arguments are chosen by the static type of the call expression, while the function actually invoked is the dynamic-type override; if base and derived defaults differ, the same call runs with different arguments depending on the static type — unpredictable. Match the override’s default arguments to the base (preferably avoid default arguments).'},

 {'id':'Rule 13.3.3','cat':'Required · Decidable','compiles':True,
  'title':'함수의 모든 선언·재정의에서 매개변수 이름은 무명이거나 동일해야 한다',
  'title_en':'Parameters shall be unnamed or have the same name in all declarations and overrides',
  'bad': r"""#include <iostream>
struct Base { virtual void set(int width, int height){ (void)width; (void)height; } virtual ~Base() = default; };
struct Derived : Base {
    void set(int height, int width) override {   // 이름이 뒤바뀜 — 인자 의미 오해 유발
        (void)height; (void)width;
    }
};
int main(){ Derived d; d.set(10, 20); std::cout << "ok\n"; }""",
  'good': r"""#include <iostream>
struct Base { virtual void set(int width, int height){ (void)width; (void)height; } virtual ~Base() = default; };
struct Derived : Base {
    void set(int width, int height) override {   // 동일 이름·순서
        (void)width; (void)height;
    }
};
int main(){ Derived d; d.set(10, 20); std::cout << "ok\n"; }""",
  'why':'선언마다 매개변수 이름이 다르거나(특히 width/height 처럼 뒤바뀌면) 호출자가 인자의 의미를 오해해 순서를 바꿔 전달하는 결함을 부른다. 한 함수의 모든 선언·재정의에서 매개변수 이름을 동일하게(또는 전부 무명으로) 맞춘다.',
  'why_en':'Different parameter names across declarations — especially swapped ones like width/height — lead callers to misunderstand argument meaning and pass them in the wrong order. Keep parameter names identical (or all unnamed) across every declaration and override of a function.'},

 {'id':'Rule 13.3.4','cat':'Required · Decidable','compiles':True,
  'title':'멤버 함수 포인터는 널 상수와의 동등 비교에만 쓴다',
  'title_en':'A pointer to member function shall only be compared for equality with a null pointer constant',
  'bad': r"""#include <iostream>
struct W { virtual void on(){} virtual void off(){} virtual ~W() = default; };
static bool same(void (W::*a)(), void (W::*b)()){
    return a == b;   // 가상 멤버함수 포인터끼리 비교 — 결과가 구현마다 불명확
}
int main(){ std::cout << same(&W::on, &W::off) << '\n'; }""",
  'good': r"""#include <iostream>
struct W { virtual void on(){} virtual void off(){} virtual ~W() = default; };
static bool isSet(void (W::*p)()){
    return p != nullptr;   // 널 여부만 검사
}
int main(){ std::cout << isSet(&W::on) << '\n'; }""",
  'why':'가상 멤버 함수에 대한 포인터끼리의 동등 비교는 표준이 결과를 명확히 규정하지 않아 구현마다 다르게 동작할 수 있어 신뢰할 수 없다. 멤버 함수 포인터는 nullptr 과의 동등 비교(설정 여부 판정)에만 사용한다.',
  'why_en':'Equality comparison between pointers to virtual member functions is not clearly specified by the standard and may behave differently across implementations, so it is unreliable. Use pointers to member functions only for equality comparison with nullptr (to test whether one is set).'},

 # ── 섹션 14: 멤버 접근(Member access) ───────────────────────────────────
 {'id':'Rule 14.1.1','cat':'Advisory · Decidable','compiles':True,
  'title':'비정적 데이터 멤버는 모두 private이거나 모두 public이어야 한다',
  'title_en':'Non-static data members should be either all private or all public',
  'bad': r"""#include <iostream>
struct Account {
    long balance;        // public
private:
    long limit;          // private — 접근 수준 혼재
public:
    void deposit(long a){ balance += a; }
    Account() : balance(0), limit(0) {}
};
int main(){ Account a; a.deposit(100); std::cout << a.balance << '\n'; }""",
  'good': r"""#include <iostream>
class Account {
public:
    void deposit(long a){ balance_ += a; }
    long balance() const { return balance_; }
private:
    long balance_{0};    // 비정적 멤버 모두 private
    long limit_{0};
};
int main(){ Account a; a.deposit(100); std::cout << a.balance() << '\n'; }""",
  'why':'데이터 멤버의 접근 수준이 섞이면 일부는 외부에서 직접 수정 가능하고 일부는 메서드를 통해서만 바뀌어, 불변식(invariant) 유지 책임이 흩어지고 캡슐화가 깨진다. 비정적 데이터 멤버는 전부 private(또는 단순 집합체면 전부 public)으로 통일한다.',
  'why_en':'Mixed access levels on data members let some be modified directly from outside while others change only through methods, scattering responsibility for invariants and breaking encapsulation. Make non-static data members all private (or all public for a plain aggregate).'},

 # ── 섹션 15: 특수 멤버 함수(Special member functions) ───────────────────
 {'id':'Rule 15.0.1','cat':'Required · Decidable','compiles':True,
  'title':'특수 멤버 함수를 일관되게 제공한다(Rule of Five)',
  'title_en':'Special member functions shall be provided consistently (Rule of Five)',
  'bad': r"""#include <cstring>
#include <iostream>
struct Buf {
    char* p;
    explicit Buf(int n) : p(new char[n]) {}
    ~Buf(){ delete[] p; }   // 소멸자만 정의 — 복사/이동 미정의 → 얕은 복사·이중 해제
};
int main(){ Buf b(8); std::strcpy(b.p, "ok"); std::cout << b.p << '\n'; }""",
  'good': r"""#include <memory>
#include <cstring>
#include <iostream>
struct Buf {
    std::unique_ptr<char[]> p;
    explicit Buf(int n) : p(std::make_unique<char[]>(n)) {}
    Buf(const Buf&) = delete;            // 복사 금지 명시
    Buf& operator=(const Buf&) = delete;
    Buf(Buf&&) = default;                // 이동 허용 명시
    Buf& operator=(Buf&&) = default;
};
int main(){ Buf b(8); std::strcpy(b.p.get(), "ok"); std::cout << b.p.get() << '\n'; }""",
  'why':'소멸자·복사·이동 중 하나만 정의하면 나머지는 컴파일러 기본 구현이 쓰이는데, 자원을 소유한 클래스에서는 기본 복사가 얕은 복사가 되어 이중 해제·댕글링을 일으킨다. 특수 멤버 집합(Rule of Five)을 일관되게 정의하거나 명시적으로 삭제(=delete)하고, 가능하면 스마트 포인터로 소유권을 위임한다.',
  'why_en':'Defining only one of destructor/copy/move leaves the rest to compiler defaults, and for a resource-owning class the default copy is a shallow copy causing double free or dangling. Provide the special-member set (Rule of Five) consistently or explicitly =delete them, and prefer delegating ownership to smart pointers.'},

 {'id':'Rule 15.0.2','cat':'Advisory · Decidable','compiles':True,
  'title':'사용자 제공 복사/이동 멤버 함수는 적절한 시그니처를 가진다',
  'title_en':'User-provided copy and move member functions should have the correct signature',
  'bad': r"""#include <iostream>
struct S {
    int v{0};
    S() = default;
    S(S& o){ v = o.v; }                 // const 아님 → const 객체를 복사할 수 없음
    S operator=(const S& o){ v = o.v; return *this; }   // 값 반환(참조여야 함)
};
int main(){ S a; a.v = 7; S b(a); std::cout << b.v << '\n'; }""",
  'good': r"""#include <iostream>
struct S {
    int v{0};
    S() = default;
    S(const S& o) : v(o.v) {}           // const 참조 매개변수
    S& operator=(const S& o){ v = o.v; return *this; }   // 참조 반환
};
int main(){ S a; a.v = 7; const S& ca = a; S b(ca); std::cout << b.v << '\n'; }""",
  'why':'복사 생성자의 매개변수가 const& 가 아니면 const 객체·임시객체를 복사할 수 없고, 대입 연산자가 참조 대신 값을 반환하면 a = b = c 같은 연쇄 대입이나 표준 알고리즘과 어긋난다. 관례에 따라 const& 매개변수와 *this 참조 반환 시그니처를 사용한다.',
  'why_en':'A copy constructor whose parameter is not const& cannot copy const or temporary objects, and an assignment operator that returns by value rather than reference breaks chained assignment (a = b = c) and standard algorithms. Follow the convention of a const& parameter and returning a reference to *this.'},

 {'id':'Rule 15.1.1','cat':'Required · Undecidable','compiles':True,
  'title':'생성자/소멸자 본문에서 가상 디스패치에 의존하지 않는다',
  'title_en':'A virtual function shall not be called from a constructor or destructor in a way that relies on dynamic type',
  'bad': r"""#include <iostream>
struct Base {
    Base(){ init(); }              // 생성 중 가상 호출 — 파생 재정의로 가지 않음
    virtual void init(){ std::cout << "Base::init\n"; }
    virtual ~Base() = default;
};
struct Derived : Base {
    void init() override { std::cout << "Derived::init\n"; }
};
int main(){ Derived d; (void)d; }   // 출력: Base::init (의도와 다름)""",
  'good': r"""#include <iostream>
struct Base {
    Base() = default;
    virtual void init(){ std::cout << "Base::init\n"; }
    virtual ~Base() = default;
};
struct Derived : Base {
    void init() override { std::cout << "Derived::init\n"; }
};
int main(){ Derived d; d.init(); }   // 생성 완료 후 호출 → Derived::init""",
  'why':'생성자·소멸자가 실행되는 동안 객체의 동적 타입은 현재 생성/소멸 중인 클래스이므로, 그 안에서 가상 함수를 부르면 파생 클래스의 재정의가 아니라 현재 클래스 버전이 호출되어 의도와 다르게 동작한다. 가상 디스패치가 필요한 초기화는 객체 생성이 완료된 뒤에 호출한다.',
  'why_en':'During a constructor or destructor the object’s dynamic type is the class currently being constructed/destroyed, so calling a virtual function invokes that class’s version, not the derived override — behaving unexpectedly. Perform initialization that needs virtual dispatch after the object is fully constructed.'},

 {'id':'Rule 15.1.2','cat':'Advisory · Decidable','compiles':True,
  'title':'모든 생성자는 기반 클래스 생성자를 명시적으로 호출한다',
  'title_en':'All constructors should explicitly call a base class constructor',
  'bad': r"""#include <iostream>
struct Base { int x; explicit Base(int v) : x(v) {} };
struct Derived : Base {
    int y;
    explicit Derived(int v) : Base(v), y(v) {}   // (기반 생성자 호출이 누락되면 컴파일 불가)
};
int main(){ Derived d(5); std::cout << d.x << ' ' << d.y << '\n'; }""",
  'good': r"""#include <iostream>
struct Base { int x; explicit Base(int v) : x(v) {} };
struct Derived : Base {
    int y;
    explicit Derived(int v) : Base(v), y(v) {}   // 기반 생성자를 명시적으로 위임
};
int main(){ Derived d(5); std::cout << d.x << ' ' << d.y << '\n'; }""",
  'why':'파생 생성자가 기반 생성자를 명시적으로 호출하지 않으면 기본 생성에 의존하게 되어 초기화 의도가 흐려지고, 기반에 기본 생성자가 없으면 아예 컴파일되지 않는다. 모든 생성자에서 적절한 기반 생성자를 초기화 목록에 명시해 초기화 경로를 분명히 한다.',
  'why_en':'If a derived constructor does not explicitly call a base constructor it relies on default construction, obscuring initialization intent, and fails to compile when the base has no default constructor. Name the appropriate base constructor in every constructor’s initializer list to make the initialization path explicit.'},

 {'id':'Rule 15.1.3','cat':'Required · Decidable','compiles':True,
  'title':'단일 인자 변환 생성자/연산자는 explicit로 선언한다',
  'title_en':'Conversion operators and constructors callable with a single argument shall be explicit',
  'bad': r"""#include <iostream>
struct Meters {
    double v;
    Meters(double d) : v(d) {}     // 암묵 변환 허용
};
static void travel(Meters m){ std::cout << m.v << '\n'; }
int main(){ travel(3.0); }         // double → Meters 암묵 변환이 조용히 일어남""",
  'good': r"""#include <iostream>
struct Meters {
    double v;
    explicit Meters(double d) : v(d) {}   // 암묵 변환 차단
};
static void travel(Meters m){ std::cout << m.v << '\n'; }
int main(){ travel(Meters{3.0}); }        // 명시적 생성 필요""",
  'why':'단일 인자로 호출 가능한 생성자나 변환 연산자가 암묵 변환을 허용하면, 의도하지 않은 형변환이 조용히 일어나 잘못된 단위·타입이 함수에 전달되는 결함을 만든다. explicit 로 선언해 변환을 의도적으로 명시할 때만 일어나게 한다.',
  'why_en':'A constructor or conversion operator callable with a single argument that permits implicit conversion lets unintended conversions happen silently, passing the wrong unit or type into functions. Declare it explicit so conversion happens only when deliberately spelled out.'},

 {'id':'Rule 15.1.4','cat':'Advisory · Undecidable','compiles':True,
  'title':'클래스의 모든 직접 비정적 데이터 멤버를 초기화한다',
  'title_en':'All direct non-static data members of a class shall be initialized',
  'bad': r"""#include <iostream>
struct P {
    int x;
    int y;
    P() : x(0) { }    // y 초기화 누락
    int sum() const { return x + y; }   // y 는 미초기화 값
};
int main(){ P p; std::cout << p.sum() << '\n'; }""",
  'good': r"""#include <iostream>
struct P {
    int x{0};
    int y{0};         // 기본 멤버 초기화로 모든 멤버 초기화
    P() = default;
    int sum() const { return x + y; }
};
int main(){ P p; std::cout << p.sum() << '\n'; }""",
  'why':'생성자에서 일부 데이터 멤버를 초기화하지 않으면 객체가 부분적으로 비결정적 상태가 되어, 그 멤버를 읽는 순간 재현 불가한 버그가 발생한다. 기본 멤버 초기자(int x{0};)나 초기화 목록으로 모든 직접 비정적 멤버를 빠짐없이 초기화한다.',
  'why_en':'Leaving some data members uninitialized in a constructor puts the object in a partially non-deterministic state, producing irreproducible bugs the moment such a member is read. Initialize every direct non-static member via default member initializers (int x{0};) or the initializer list.'},

 {'id':'Rule 15.1.5','cat':'Required · Decidable','compiles':True,
  'title':'initializer-list 생성자는 그것이 유일한 생성자일 때만 정의한다',
  'title_en':'An initializer-list constructor should be the only constructor when provided',
  'bad': r"""#include <initializer_list>
#include <iostream>
struct Vec {
    int n{0};
    Vec(std::initializer_list<int> xs) : n(static_cast<int>(xs.size())) {}
    explicit Vec(int count) : n(count) {}   // 다른 생성자와 공존 → 중괄호 초기화가 모호
};
int main(){ Vec a{5}; std::cout << a.n << '\n'; }   // count=5? 원소 1개? — 후자 선택됨""",
  'good': r"""#include <iostream>
struct Vec {
    int n{0};
    explicit Vec(int count) : n(count) {}   // 의도가 명확한 단일 생성자
};
int main(){ Vec a{5}; std::cout << a.n << '\n'; }""",
  'why':'initializer-list 생성자가 다른 생성자와 공존하면, 중괄호 초기화 Vec{5} 가 "원소 5 하나" 인지 "count=5" 인지 오버로드 해석이 initializer-list 쪽을 강하게 선호해 의도와 다른 생성자가 선택된다. 둘 중 의도에 맞는 하나만 두어 모호함을 없앤다.',
  'why_en':'When an initializer-list constructor coexists with other constructors, brace initialization like Vec{5} is strongly biased toward the initializer-list overload, so it may pick a different constructor than intended ("one element 5" vs "count=5"). Keep only the one that matches intent to remove the ambiguity.'},

 {'id':'Dir 15.8.1','cat':'Required · Undecidable','compiles':True,
  'title':'복사/이동 대입 연산자는 자기 대입을 안전하게 처리한다',
  'title_en':'User-provided copy/move assignment operators shall handle self-assignment safely',
  'bad': r"""#include <iostream>
struct Buf {
    char* p; int n;
    Buf(const char* s, int len) : p(new char[len]), n(len) { for(int i=0;i<len;++i) p[i]=s[i]; }
    Buf& operator=(const Buf& o){
        delete[] p;                 // o==*this 면 자기 데이터를 먼저 해제
        p = new char[o.n];
        for (int i = 0; i < o.n; ++i) p[i] = o.p[i];   // 해제된 메모리를 읽음
        n = o.n; return *this;
    }
    ~Buf(){ delete[] p; }
};
int main(){ Buf b("hi", 2); b = b; std::cout << b.n << '\n'; }""",
  'good': r"""#include <iostream>
struct Buf {
    char* p; int n;
    Buf(const char* s, int len) : p(new char[len]), n(len) { for(int i=0;i<len;++i) p[i]=s[i]; }
    Buf& operator=(const Buf& o){
        if (this == &o) return *this;          // 자기 대입 가드
        char* np = new char[o.n];
        for (int i = 0; i < o.n; ++i) np[i] = o.p[i];
        delete[] p; p = np; n = o.n;
        return *this;
    }
    ~Buf(){ delete[] p; }
};
int main(){ Buf b("hi", 2); b = b; std::cout << b.n << '\n'; }""",
  'why':'자기 대입(b = b)을 고려하지 않은 대입 연산자는 대상의 자원을 먼저 해제한 뒤 같은(이미 해제된) 자원을 읽어 복사하므로 미정의 동작과 데이터 손상이 발생한다. this==&o 가드를 두거나 copy-and-swap 관용구를 적용해 자기 대입을 안전하게 처리한다.',
  'why_en':'An assignment operator that ignores self-assignment (b = b) frees the destination’s resource first and then reads the same (now-freed) resource to copy it, causing undefined behaviour and data corruption. Add a this==&o guard or apply the copy-and-swap idiom to handle self-assignment safely.'},

 # ── 섹션 16: 오버로딩(Overloading) ──────────────────────────────────────
 {'id':'Rule 16.5.1','cat':'Required · Decidable','compiles':True,
  'title':'논리 AND(&&)·OR(||) 연산자를 오버로드하지 않는다',
  'title_en':'The logical && and || operators shall not be overloaded',
  'bad': r"""#include <iostream>
struct Cond {
    bool v;
    bool operator&&(const Cond& o) const { return v && o.v; }   // 오버로드 시 단락 평가 사라짐
};
int main(){ Cond a{false}, b{true}; std::cout << (a && b) << '\n'; }   // 두 피연산자 모두 평가""",
  'good': r"""#include <iostream>
struct Cond {
    bool v;
    explicit operator bool() const { return v; }   // bool 변환만 제공
};
int main(){ Cond a{false}, b{true}; std::cout << (a && b) << '\n'; }   // 내장 && 의 단락 평가 유지""",
  'why':'&&/|| 를 오버로드하면 일반 함수 호출이 되어 내장 연산자의 단락 평가(short-circuit)가 사라지고 두 피연산자가 항상 평가되므로, 좌변으로 우변을 보호하던 코드(예: p != nullptr && p->ok())가 깨진다. 대신 explicit operator bool 등을 제공해 내장 &&/|| 의 단락 평가를 유지한다.',
  'why_en':'Overloading && or || turns them into ordinary function calls, losing the built-in short-circuit so both operands are always evaluated, breaking code that guards the right operand with the left (e.g., p != nullptr && p->ok()). Provide explicit operator bool instead, preserving the built-in short-circuit of && and ||.'},

 {'id':'Rule 16.5.2','cat':'Required · Decidable','compiles':True,
  'title':'주소 연산자(단항 &)를 오버로드하지 않는다',
  'title_en':'The unary & operator shall not be overloaded',
  'bad': r"""#include <iostream>
struct Handle {
    int id;
    int operator&() const { return id; }   // 단항 & 오버로드 → 실제 주소를 얻을 수 없음
};
int main(){ Handle h{7}; auto x = &h; std::cout << x << '\n'; }   // 주소가 아니라 id 반환""",
  'good': r"""#include <iostream>
struct Handle {
    int id;
    int key() const { return id; }   // 의도를 별도 이름 함수로 표현
};
int main(){ Handle h{7}; Handle* p = &h; std::cout << (p->id) << '\n'; }   // & 는 정상적으로 주소""",
  'why':'단항 & 를 오버로드하면 그 타입의 실제 주소를 얻을 수 없게 되어, 객체 주소를 가정하는 표준 라이브러리(std::addressof 없이 쓰는 코드)와 일반 코드가 조용히 깨진다. 주소가 아닌 의미(키·식별자 반환 등)는 별도 명명 함수로 표현하고 & 는 본래 의미를 유지한다.',
  'why_en':'Overloading unary & makes it impossible to obtain the type’s real address, silently breaking standard-library and generic code that assumes the object’s address. Express non-address meanings (returning a key or identifier) with a separately named function and keep & for its original meaning.'},

 {'id':'Rule 16.6.1','cat':'Advisory · Decidable','compiles':True,
  'title':'대칭 이항 연산자는 비멤버 함수로 구현한다',
  'title_en':'Symmetric binary operators should be implemented as non-member functions',
  'bad': r"""#include <iostream>
struct Money {
    long cents;
    Money operator+(const Money& o) const { return {cents + o.cents}; }   // 멤버 → 비대칭 변환
};
int main(){ Money a{100}, b{50}; std::cout << (a + b).cents << '\n'; }""",
  'good': r"""#include <iostream>
struct Money { long cents; };
inline Money operator+(const Money& a, const Money& b){   // 비멤버 → 양쪽에 동일 변환
    return Money{a.cents + b.cents};
}
int main(){ Money a{100}, b{50}; std::cout << (a + b).cents << '\n'; }""",
  'why':'+ 나 == 같은 대칭 이항 연산자를 멤버 함수로 두면 좌측 피연산자에는 암묵 변환이 적용되지 않아, 100 + m 처럼 좌측이 변환 대상인 경우 a + b 와 b + a 의 동작이 달라지는 비대칭이 생긴다. 대칭 연산자는 비멤버 함수로 구현해 양쪽 피연산자에 동일한 변환 규칙이 적용되게 한다.',
  'why_en':'Implementing a symmetric binary operator like + or == as a member means no implicit conversion applies to the left operand, so when the left side needs conversion (e.g., 100 + m) a + b and b + a behave differently — an asymmetry. Implement symmetric operators as non-member functions so the same conversion rules apply to both operands.'},
]
