# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트2: 섹션 9~16) — 위반/준수 예제, 사내 교육용·자체작성

규칙 ID/의무도/제목 출처(교차검증):
  - MathWorks Polyspace Bug Finder, "MISRA C++:2023 Rules and Directives"
  - Perforce Helix QAC "MISRA_M2CPP" enforcement 매핑표 (의무도·결정가능성)
  - Klocwork "MISRA C++:2023 checker reference"
  - CodeAnt AI MISRA-CPP-2023 컴플라이언스 문서
규범 본문(verbatim) 미사용 — 제목은 한국어 의역, 예제·해설은 전부 자체작성(C++17).

참고: MISRA C++:2023의 섹션 9~16은 규칙 분포가 희소한 구간으로,
표준에 실재하는 가이드라인은 규칙 45개 + 지침(Directive) 1개(Dir 15.8.1) =
총 46개뿐이다. ID 위조 금지 원칙에 따라 실재 ID 46개만 수록한다.
"""
RULES = [
 # ── 섹션 9: 문장(Statements) ───────────────────────────────────────────
 {'id':'Rule 9.2.1','cat':'Required · Decidable',
  'title':'명시적 형변환을 단독 표현식 문장으로 쓰지 않는다',
  'bad': r"""void poll(int raw) {
    // 변환 결과를 버리는 의미 없는 표현식 문장
    static_cast<double>(raw);   // 비준수: 효과 없음
    (void)0;
    // 의도가 모호: 부작용도, 사용처도 없는 캐스트
}
""",
  'good': r"""double poll(int raw) {
    // 변환 결과를 실제로 사용하거나 반환한다
    double scaled = static_cast<double>(raw) * 0.01;
    return scaled;   // 준수: 변환 결과가 사용됨
}
""",
  'why':'결과를 사용하지 않는 캐스트 단독 문장은 의도 불명·오타 가능성을 숨긴다. 변환 결과를 변수에 담거나 반환해 실제로 사용하라.'},

 {'id':'Rule 9.3.1','cat':'Required · Decidable',
  'title':'반복문·선택문의 본문은 복합문(중괄호 블록)이어야 한다',
  'bad': r"""int sum(const int* a, int n) {
    int s = 0;
    for (int i = 0; i < n; ++i)
        s += a[i];          // 비준수: 중괄호 없는 본문
    if (s < 0)
        s = 0;              // 추후 줄 추가 시 범위 오류 위험
    return s;
}
""",
  'good': r"""int sum(const int* a, int n) {
    int s = 0;
    for (int i = 0; i < n; ++i) {
        s += a[i];          // 준수: 복합문
    }
    if (s < 0) {
        s = 0;
    }
    return s;
}
""",
  'why':'중괄호 없는 본문은 줄을 추가할 때 범위가 의도와 어긋나기 쉽다(dangling). 항상 복합문 블록으로 감싸라.'},

 {'id':'Rule 9.4.1','cat':'Required · Decidable',
  'title':'if … else if 연쇄는 마지막 else로 종결한다',
  'bad': r"""int classify(int x) {
    int r = -1;
    if (x > 0)        r = 1;
    else if (x < 0)   r = 2;   // 비준수: 0인 경우 처리 누락
    return r;                  // x==0이면 -1, 의도 불명확
}
""",
  'good': r"""int classify(int x) {
    int r;
    if (x > 0)        r = 1;
    else if (x < 0)   r = 2;
    else              r = 0;   // 준수: 모든 경우를 명시
    return r;
}
""",
  'why':'마지막 else가 없으면 처리되지 않는 입력이 조용히 통과한다. else를 두어 누락 경로를 명시적으로 처리하라.'},

 {'id':'Rule 9.4.2','cat':'Required · Decidable',
  'title':'switch 문은 적절한 구조(default·break·case 라벨)를 갖춘다',
  'bad': r"""int speed(int gear) {
    int v = 0;
    switch (gear) {
    case 1: v = 10;   // 비준수: break 누락 → fall-through
    case 2: v = 20;
            break;
    }                 // default 없음
    return v;
}
""",
  'good': r"""int speed(int gear) {
    int v = 0;
    switch (gear) {
    case 1:  v = 10; break;
    case 2:  v = 20; break;
    default: v = 0;  break;   // 준수: 모든 case break + default
    }
    return v;
}
""",
  'why':'break 누락·default 부재는 의도치 않은 fall-through와 미처리 입력을 부른다. 각 case를 break로 닫고 default를 제공하라.'},

 {'id':'Rule 9.5.1','cat':'Advisory · Decidable',
  'title':'전통적 for 문은 단순하게 작성한다',
  'bad': r"""double avg(const double* a, int n) {
    double s = 0.0;
    // 비준수: 루프 카운터를 본문에서 추가 변경
    for (int i = 0, j = 0; i < n; ++i, j += 2) {
        s += a[i];
        if (a[i] < 0.0) i += 1;   // 카운터 본문 수정 → 추론 곤란
    }
    return n ? s / n : 0.0;
}
""",
  'good': r"""double avg(const double* a, int n) {
    double s = 0.0;
    for (int i = 0; i < n; ++i) {   // 준수: 단일 카운터, 본문서 미수정
        s += a[i];
    }
    return n ? s / n : 0.0;
}
""",
  'why':'다중 카운터·본문 내 카운터 변경은 반복 횟수 추론을 어렵게 한다. 카운터는 하나로, 증감은 for 헤더에서만 하라.'},

 {'id':'Rule 9.5.2','cat':'Required · Decidable',
  'title':'범위 기반 for의 초기화식은 함수 호출을 최대 1회만 포함한다',
  'bad': r"""#include <vector>
int total() {
    int s = 0;
    // 비준수: 초기화식에 함수 호출이 둘 → 평가 순서·수명 모호
    for (int v : merge(load_a(), load_b())) { (void)v; s += 1; }
    return s;
}
std::vector<int> load_a(); std::vector<int> load_b();
std::vector<int> merge(std::vector<int>, std::vector<int>);
""",
  'good': r"""#include <vector>
int total() {
    auto data = merge(load_a(), load_b());  // 범위 객체를 먼저 확정
    int s = 0;
    for (int v : data) { (void)v; s += 1; } // 준수: 호출 1회 이하
    return s;
}
std::vector<int> load_a(); std::vector<int> load_b();
std::vector<int> merge(std::vector<int>, std::vector<int>);
""",
  'why':'범위식에 임시객체를 만드는 호출이 여럿이면 수명·평가 순서가 모호해 댕글링 위험이 생긴다. 범위 객체를 먼저 만들고 순회하라.'},

 {'id':'Rule 9.6.1','cat':'Advisory · Decidable',
  'title':'goto 문은 사용하지 않는다',
  'bad': r"""int find(const int* a, int n, int key) {
    int idx = -1;
    for (int i = 0; i < n; ++i) {
        if (a[i] == key) { idx = i; goto done; }  // 비준수
    }
done:
    return idx;
}
""",
  'good': r"""int find(const int* a, int n, int key) {
    int idx = -1;
    for (int i = 0; i < n; ++i) {
        if (a[i] == key) { idx = i; break; }  // 준수: 구조적 제어
    }
    return idx;
}
""",
  'why':'goto는 제어 흐름을 비구조적으로 만들어 가독성·검증을 저해한다. break/return 등 구조적 제어로 대체하라.'},

 {'id':'Rule 9.6.2','cat':'Required · Decidable',
  'title':'goto는 같은 또는 둘러싼 블록의 라벨만 참조한다',
  'bad': r"""void run(bool c) {
    if (c) {
        goto inner;   // 비준수: 더 안쪽 블록 라벨로 점프
    }
    {
inner:
        do_work();
    }
}
void do_work();
""",
  'good': r"""void run(bool c) {
    if (c) {
        do_work();    // 준수: goto 없이 직접 호출
        return;
    }
    do_work();
}
void do_work();
""",
  'why':'바깥에서 안쪽 블록 라벨로 점프하면 초기화를 건너뛰는 등 정의되지 않은 흐름을 만든다. 점프를 없애거나 같은/둘러싼 블록만 참조하라.'},

 {'id':'Rule 9.6.3','cat':'Required · Decidable',
  'title':'goto는 본문에서 나중에 선언된 라벨로만 전방 점프한다',
  'bad': r"""void retry() {
    int tries = 0;
again:                    // 비준수: 뒤에서 앞으로 후방 점프(루프 형성)
    if (++tries < 3) {
        if (!attempt()) goto again;
    }
}
bool attempt();
""",
  'good': r"""void retry() {
    for (int tries = 0; tries < 3; ++tries) {  // 준수: 명시적 루프
        if (attempt()) return;
    }
}
bool attempt();
""",
  'why':'후방 goto는 암묵적 루프를 만들어 종료 보장을 흐린다. 반복이 필요하면 명시적 반복문을 사용하라.'},

 {'id':'Rule 9.6.4','cat':'Mandatory · Undecidable',
  'title':'[[noreturn]] 함수는 절대 반환하지 않는다',
  'bad': r"""[[noreturn]] void fail(int code) {
    if (code == 0) {
        return;        // 비준수: noreturn인데 정상 반환 경로 존재
    }
    std::abort();
}
#include <cstdlib>
""",
  'good': r"""#include <cstdlib>
[[noreturn]] void fail(int /*code*/) {
    std::abort();      // 준수: 모든 경로가 비반환(abort)으로 종료
}
""",
  'why':'[[noreturn]] 함수가 실제로 반환하면 동작이 정의되지 않는다. 모든 경로가 abort/throw/exit 등으로 종료되도록 보장하라.'},

 {'id':'Rule 9.6.5','cat':'Mandatory · Undecidable',
  'title':'비-void 반환형 함수는 모든 경로에서 값을 반환한다',
  'bad': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    // 비준수: x==0 경로에서 반환 없음 → 미정의 동작
}
""",
  'good': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;          // 준수: 모든 경로가 값을 반환
}
""",
  'why':'값을 반환하지 않고 함수 끝에 도달하면 호출자는 쓰레기 값을 읽어 미정의 동작이 된다. 모든 분기에서 반환하라.'},

 # ── 섹션 10: 선언(Declarations) ────────────────────────────────────────
 {'id':'Rule 10.0.1','cat':'Advisory · Decidable',
  'title':'한 선언에서 둘 이상의 변수/멤버를 선언하지 않는다',
  'bad': r"""void f() {
    int* p, q;   // 비준수: p는 포인터, q는 int — 혼동 유발
    int  a = 0, b;  // b는 미초기화
    (void)p; (void)q; (void)a; (void)b;
}
""",
  'good': r"""void f() {
    int* p = nullptr;   // 준수: 선언당 하나
    int  q = 0;
    int  a = 0;
    int  b = 0;
    (void)p; (void)q; (void)a; (void)b;
}
""",
  'why':'한 줄 다중 선언은 포인터 결합 오해와 초기화 누락을 부른다. 한 선언에 하나의 변수만 두고 각자 초기화하라.'},

 {'id':'Rule 10.1.1','cat':'Advisory · Decidable',
  'title':'포인터·lvalue 참조 매개변수의 대상 타입은 적절히 const 한정한다',
  'bad': r"""int length(char* s) {     // 비준수: 수정 안 하는데 비-const
    int n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
""",
  'good': r"""int length(const char* s) {   // 준수: 읽기 전용을 const로 표현
    int n = 0;
    while (s[n] != '\0') ++n;
    return n;
}
""",
  'why':'수정하지 않는 대상에 const를 빠뜨리면 의도가 흐려지고 const 인자를 못 받는다. 읽기 전용 대상은 const로 한정하라.'},

 {'id':'Rule 10.1.2','cat':'Required · Decidable',
  'title':'volatile 한정자는 적절한 경우에만 사용한다',
  'bad': r"""void compute() {
    volatile int tmp = 0;   // 비준수: 단순 지역 누적기에 불필요한 volatile
    for (int i = 0; i < 100; ++i) {
        tmp += i;           // 최적화 차단·성능 저하만 유발
    }
    (void)tmp;
}
""",
  'good': r"""// 메모리 맵 하드웨어 레지스터 등 진짜 필요한 곳에만 사용
extern volatile unsigned int STATUS_REG;
void compute() {
    int sum = 0;            // 준수: 일반 연산은 비-volatile
    for (int i = 0; i < 100; ++i) sum += i;
    while ((STATUS_REG & 0x1u) == 0u) { }  // 외부 변경 폴링엔 적절
}
""",
  'why':'불필요한 volatile은 최적화를 막고 오용을 유발한다. 외부 요인으로 값이 바뀌는 객체(하드웨어 레지스터 등)에만 적용하라.'},

 {'id':'Rule 10.2.1','cat':'Required · Decidable',
  'title':'열거형은 기반 정수 타입을 명시해 정의한다',
  'bad': r"""enum class Mode {       // 비준수: 기반 타입 미지정
    Idle, Run, Stop
};
int g(Mode m) { return static_cast<int>(m); }
""",
  'good': r"""enum class Mode : unsigned char {   // 준수: 기반 타입 명시
    Idle, Run, Stop
};
int g(Mode m) { return static_cast<int>(m); }
""",
  'why':'기반 타입을 명시하지 않으면 크기·표현 범위가 구현 의존적이라 이식성이 깨진다. 명시적 underlying type을 지정하라.'},

 {'id':'Rule 10.2.2','cat':'Advisory · Decidable',
  'title':'범위 없는(unscoped) 열거형은 선언하지 않는다',
  'bad': r"""enum Color { Red, Green, Blue };   // 비준수: 전역 이름공간 오염
void use() {
    int x = Green;   // 암묵 int 변환, 이름 충돌 위험
    (void)x;
}
""",
  'good': r"""enum class Color { Red, Green, Blue };  // 준수: 범위 지정
void use() {
    Color c = Color::Green;   // 명시적 한정, 암묵 변환 없음
    (void)c;
}
""",
  'why':'unscoped enum은 이름공간을 오염시키고 int로 암묵 변환되어 오류를 숨긴다. enum class를 사용하라.'},

 {'id':'Rule 10.2.3','cat':'Required · Decidable',
  'title':'고정 기반 타입 없는 unscoped 열거형의 수치값을 사용하지 않는다',
  'bad': r"""enum Flags { A, B, C };
int raw() {
    Flags f = B;
    return f + 1;     // 비준수: 열거값을 산술 수치로 사용
}
""",
  'good': r"""enum class Flags : int { A, B, C };
int raw() {
    Flags f = Flags::B;
    return static_cast<int>(f) + 1;  // 준수: 명시적 변환 후 산술
}
""",
  'why':'기반 타입이 고정되지 않은 열거값을 수치로 쓰면 표현 범위가 불명확해 미정의 결과가 날 수 있다. 고정 타입 enum + 명시 변환을 쓰라.'},

 {'id':'Rule 10.3.1','cat':'Advisory · Decidable',
  'title':'헤더 파일에는 익명 네임스페이스를 두지 않는다',
  'bad': r"""// util.hpp  (비준수)
namespace {
    int counter = 0;   // 포함하는 모든 TU마다 별도 사본 → ODR 혼란
    inline void tick() { ++counter; }
}
""",
  'good': r"""// util.hpp  (준수)
namespace util {
    void tick();       // 선언만 헤더에, 정의는 .cpp로
}
// util.cpp
namespace util { static int counter = 0; void tick() { ++counter; } }
""",
  'why':'헤더의 익명 네임스페이스는 포함 단위마다 별도 실체를 만들어 의도치 않은 중복·혼란을 부른다. 헤더엔 선언만 두라.'},

 {'id':'Rule 10.4.1','cat':'Required · Decidable',
  'title':'asm 선언(인라인 어셈블리)을 사용하지 않는다',
  'bad': r"""int read_tsc() {
    int lo;
    asm volatile("rdtsc" : "=a"(lo));  // 비준수: 이식성·검증성 저하
    return lo;
}
""",
  'good': r"""#include <chrono>
long read_tsc() {
    // 준수: 표준 라이브러리로 이식성 있는 타이밍 확보
    auto now = std::chrono::steady_clock::now().time_since_epoch();
    return static_cast<long>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(now).count());
}
""",
  'why':'인라인 어셈블리는 이식성과 정적 분석을 깨뜨린다. 표준 라이브러리나 잘 캡슐화된 컴파일러 내장함수로 대체하라.'},

 # ── 섹션 11: 선언자(Declarators) ───────────────────────────────────────
 {'id':'Rule 11.3.1','cat':'Advisory · Decidable',
  'title':'배열 타입 변수를 선언하지 않는다(C 스타일 배열 회피)',
  'bad': r"""double mean(int n) {
    double buf[64];          // 비준수: C 스타일 배열, 경계 검사 없음
    double s = 0.0;
    for (int i = 0; i < n; ++i) { buf[i] = i; s += buf[i]; }  // n>64면 오버런
    return s / n;
}
""",
  'good': r"""#include <array>
#include <numeric>
double mean() {
    std::array<double, 64> buf{};   // 준수: 크기·경계 인지 컨테이너
    for (std::size_t i = 0; i < buf.size(); ++i) buf[i] = static_cast<double>(i);
    double s = std::accumulate(buf.begin(), buf.end(), 0.0);
    return s / buf.size();
}
""",
  'why':'C 스타일 배열은 경계 정보가 없어 오버런·붕괴(decay)를 일으킨다. std::array/std::vector로 경계를 안전하게 관리하라.'},

 {'id':'Rule 11.3.2','cat':'Advisory · Decidable',
  'title':'객체 선언의 포인터 간접 단계는 2단계를 넘지 않는다',
  'bad': r"""void build(int*** grid) {   // 비준수: 3중 포인터 — 가독성·안전성 저하
    (void)grid;
}
""",
  'good': r"""#include <vector>
void build(std::vector<std::vector<int>>& grid) {  // 준수: 컨테이너로 표현
    (void)grid;
}
""",
  'why':'2단계를 넘는 포인터 간접은 소유권·수명 추론을 어렵게 한다. 중첩 컨테이너나 전용 타입으로 표현하라.'},

 {'id':'Rule 11.6.1','cat':'Advisory · Decidable',
  'title':'모든 변수는 초기화한다',
  'bad': r"""int scale(int k) {
    int factor;          // 비준수: 미초기화
    if (k > 0) factor = 2;
    return k * factor;   // k<=0이면 미초기화 값 사용
}
""",
  'good': r"""int scale(int k) {
    int factor = 1;      // 준수: 선언 시 초기화
    if (k > 0) factor = 2;
    return k * factor;
}
""",
  'why':'미초기화 변수는 비결정적 값을 읽어 재현 불가 버그를 만든다. 선언 시점에 항상 초기값을 주라.'},

 {'id':'Rule 11.6.2','cat':'Mandatory · Undecidable',
  'title':'객체의 값은 설정되기 전에 읽지 않는다',
  'bad': r"""int compute(bool on) {
    int v;                 // 미설정
    if (on) v = 10;
    return v + 1;          // 비준수: on==false면 미설정 값을 읽음
}
""",
  'good': r"""int compute(bool on) {
    int v = 0;             // 준수: 읽기 전 반드시 설정
    if (on) v = 10;
    return v + 1;
}
""",
  'why':'설정 전에 읽으면 정의되지 않은 값으로 동작이 깨진다. 모든 읽기 경로에서 사전 대입을 보장하라(필수 규칙).'},

 {'id':'Rule 11.6.3','cat':'Required · Decidable',
  'title':'열거자 목록에서 암묵적으로 결정되는 값은 서로 중복되지 않는다',
  'bad': r"""enum class E : int {
    A = 1,
    B,        // 자동 2
    C = 2     // 비준수: B와 값 충돌(둘 다 2)
};
""",
  'good': r"""enum class E : int {
    A = 1,
    B = 2,    // 준수: 명시적·고유 값
    C = 3
};
""",
  'why':'암묵 값이 명시 값과 겹치면 서로 다른 열거자가 같은 정수가 되어 분기·매핑 오류를 낳는다. 값이 고유하도록 명시하라.'},

 # ── 섹션 12: 집합 타입(Compound Types) ─────────────────────────────────
 {'id':'Rule 12.2.1','cat':'Advisory · Decidable',
  'title':'비트필드는 선언하지 않는다',
  'bad': r"""struct Reg {
    unsigned enable : 1;   // 비준수: 비트필드, 레이아웃 구현 의존
    unsigned mode   : 3;
    unsigned        : 4;
};
""",
  'good': r"""#include <cstdint>
struct Reg {
    std::uint8_t value;    // 준수: 명시적 정수 + 마스크 상수
};
constexpr std::uint8_t ENABLE = 0x01u;
constexpr std::uint8_t MODE   = 0x0Eu;   // bits 1..3
""",
  'why':'비트필드는 배치·부호·패딩이 구현 의존적이라 이식성과 검증성이 떨어진다. 명시적 정수와 마스크 연산으로 표현하라.'},

 {'id':'Rule 12.2.2','cat':'Required · Decidable',
  'title':'비트필드를 쓴다면 적절한 타입(명시적 부호/크기)을 사용한다',
  'bad': r"""struct Flags {
    int  a : 1;   // 비준수: 부호 있는 int 비트필드 — 1비트 부호 표현 모호
    int  b : 2;
};
""",
  'good': r"""#include <cstdint>
struct Flags {
    std::uint8_t a : 1;   // 준수: 부호 없는 고정폭 타입
    std::uint8_t b : 2;
};
""",
  'why':'부호 있는/구현정의 타입의 비트필드는 표현 범위와 부호 동작이 모호하다. 부호 없는 고정폭 타입을 비트필드 기반으로 쓰라.'},

 {'id':'Rule 12.2.3','cat':'Required · Decidable',
  'title':'부호 있는 정수형 명명 비트필드의 길이를 1비트로 두지 않는다',
  'bad': r"""struct S {
    signed int flag : 1;   // 비준수: 부호 1비트 → 값이 0 또는 -1
};
void f(S& s) { s.flag = 1; /* 실제로는 -1로 저장될 수 있음 */ }
""",
  'good': r"""struct S {
    unsigned int flag : 1;   // 준수: 부호 없는 1비트 → 0 또는 1
};
void f(S& s) { s.flag = 1u; }
""",
  'why':'부호 있는 1비트 비트필드는 부호 비트만 남아 1을 넣어도 -1이 되는 직관 위배가 생긴다. 1비트 플래그는 unsigned로 선언하라.'},

 {'id':'Rule 12.3.1','cat':'Required · Decidable',
  'title':'union 키워드를 사용하지 않는다',
  'bad': r"""union Packet {        // 비준수: 활성 멤버 추적 불가, 타입 안전 깨짐
    int   asInt;
    float asFloat;
};
float read(Packet p) { return p.asFloat; }  // asInt로 썼다면 미정의
""",
  'good': r"""#include <variant>
using Packet = std::variant<int, float>;   // 준수: 타입 안전 합집합
float read(const Packet& p) {
    return std::holds_alternative<float>(p) ? std::get<float>(p) : 0.0f;
}
""",
  'why':'union은 어떤 멤버가 유효한지 추적하지 못해 타입 혼동·미정의 읽기를 부른다. std::variant 등 타입 안전 대안을 사용하라.'},

 # ── 섹션 13: 파생 클래스(Derived Classes) ──────────────────────────────
 {'id':'Rule 13.1.1','cat':'Advisory · Decidable',
  'title':'가상 상속(virtual base)을 사용하지 않는다',
  'bad': r"""struct Base { int v{0}; };
struct A : virtual Base {};   // 비준수: 가상 상속 — 복잡한 레이아웃
struct B : virtual Base {};
struct D : A, B {};
""",
  'good': r"""struct Base { int v{0}; };
// 준수: 가상 상속 대신 합성(composition)으로 공유
struct A { Base* base; };
struct B { Base* base; };
struct D { Base shared; A a{&shared}; B b{&shared}; };
""",
  'why':'가상 상속은 객체 레이아웃·초기화 순서를 복잡하게 만들어 오류와 검증 부담을 키운다. 합성 등으로 공유 구조를 단순화하라.'},

 {'id':'Rule 13.1.2','cat':'Required · Decidable',
  'title':'접근 가능한 기반 클래스를 가상·비가상으로 동시에 두지 않는다',
  'bad': r"""struct Base {};
struct A : virtual Base {};
struct B : Base {};            // 비가상
struct D : A, B {};            // 비준수: Base가 가상+비가상 혼재
""",
  'good': r"""struct Base {};
struct A : virtual Base {};
struct B : virtual Base {};    // 준수: 일관되게 가상으로
struct D : A, B {};
""",
  'why':'동일 기반이 가상·비가상으로 섞이면 서로 다른 서브객체가 생겨 모호성과 데이터 불일치가 발생한다. 상속 방식을 일관되게 하라.'},

 {'id':'Rule 13.3.1','cat':'Required · Decidable',
  'title':'멤버 함수는 virtual/override/final 지정자를 적절히(셋 중 하나만) 사용한다',
  'bad': r"""struct Base { virtual void f(); };
struct Derived : Base {
    virtual void f() override;   // 비준수: virtual과 override 중복 지정
};
""",
  'good': r"""struct Base { virtual void f(); };
struct Derived : Base {
    void f() override;           // 준수: override 하나만 명시
};
""",
  'why':'재정의에 virtual과 override를 함께 쓰는 등 중복 지정은 의도를 흐린다. 재정의는 override, 봉인은 final 식으로 하나만 명시하라.'},

 {'id':'Rule 13.3.2','cat':'Required · Decidable',
  'title':'재정의 가상 함수는 다른 기본 인자를 지정하지 않는다',
  'bad': r"""struct Base { virtual int f(int x = 1); };
struct Derived : Base {
    int f(int x = 2) override;   // 비준수: 기본 인자가 기반과 다름
};
// 호출 시 정적 타입에 따라 기본값이 달라져 혼란
""",
  'good': r"""struct Base { virtual int f(int x = 1); };
struct Derived : Base {
    int f(int x = 1) override;   // 준수: 동일 기본 인자(가능하면 미지정)
};
""",
  'why':'기본 인자는 정적 타입 기준으로 결정되므로 재정의에서 값이 다르면 호출 결과가 예측 불가해진다. 기본 인자를 일치시켜라.'},

 {'id':'Rule 13.3.3','cat':'Required · Decidable',
  'title':'함수의 모든 선언·재정의에서 매개변수 이름은 무명이거나 동일해야 한다',
  'bad': r"""struct Base { virtual void set(int width, int height); };
struct Derived : Base {
    void set(int height, int width) override;  // 비준수: 이름 뒤바뀜
};
""",
  'good': r"""struct Base { virtual void set(int width, int height); };
struct Derived : Base {
    void set(int width, int height) override;  // 준수: 동일 이름·순서
};
""",
  'why':'선언마다 매개변수 이름이 다르거나 뒤바뀌면 인자 의미를 오해해 잘못된 순서로 호출하기 쉽다. 이름을 일치(또는 모두 무명)시켜라.'},

 {'id':'Rule 13.3.4','cat':'Required · Decidable',
  'title':'잠재적 가상 멤버 함수 포인터는 널 상수와의 동등 비교에만 쓴다',
  'bad': r"""struct W { virtual void on(); virtual void off(); };
bool same(void (W::*a)(), void (W::*b)()) {
    return a == b;   // 비준수: 가상 멤버함수 포인터끼리 비교 — 결과 불명확
}
""",
  'good': r"""struct W { virtual void on(); virtual void off(); };
bool isSet(void (W::*p)()) {
    return p != nullptr;   // 준수: 널 여부만 검사
}
""",
  'why':'가상 멤버 함수 포인터 간 비교는 구현마다 결과가 달라 신뢰할 수 없다. 널 여부 판정에만 사용하라.'},

 # ── 섹션 14: 멤버 접근 제어(Member Access Control) ─────────────────────
 {'id':'Rule 14.1.1','cat':'Advisory · Decidable',
  'title':'비정적 데이터 멤버는 모두 private이거나 모두 public이어야 한다',
  'bad': r"""struct Account {
    long balance;        // public
private:
    long limit;          // 비준수: public/private 혼재
public:
    void deposit(long a) { balance += a; }
};
""",
  'good': r"""class Account {
public:
    void deposit(long a) { balance_ += a; }
    long balance() const { return balance_; }
private:
    long balance_{0};    // 준수: 비정적 멤버 모두 private
    long limit_{0};
};
""",
  'why':'접근 수준이 섞이면 불변식 유지 책임이 흩어져 캡슐화가 깨진다. 데이터 멤버는 전부 private(또는 단순 집합체면 전부 public)으로 통일하라.'},

 # ── 섹션 15: 특수 멤버 함수(Special Member Functions) ──────────────────
 {'id':'Rule 15.0.1','cat':'Required · Decidable',
  'title':'특수 멤버 함수를 적절히(일관되게) 제공한다(Rule of Five)',
  'bad': r"""struct Buf {
    char* p;
    Buf(int n) : p(new char[n]) {}
    ~Buf() { delete[] p; }   // 비준수: 소멸자만 정의, 복사/이동 미정의
};                            // 기본 복사가 얕은 복사 → 이중 해제 위험
""",
  'good': r"""#include <memory>
struct Buf {
    std::unique_ptr<char[]> p;
    explicit Buf(int n) : p(std::make_unique<char[]>(n)) {}
    Buf(const Buf&) = delete;            // 준수: 복사 금지 명시
    Buf& operator=(const Buf&) = delete;
    Buf(Buf&&) = default;               // 이동 허용 명시
    Buf& operator=(Buf&&) = default;
};
""",
  'why':'소멸자/복사/이동 중 하나만 정의하면 나머지 기본 구현이 자원을 잘못 다뤄 이중 해제 등을 일으킨다. 특수 멤버 집합을 일관되게 제공/삭제하라.'},

 {'id':'Rule 15.0.2','cat':'Advisory · Decidable',
  'title':'사용자 제공 복사/이동 멤버 함수는 적절한 시그니처를 가진다',
  'bad': r"""struct S {
    int v{0};
    S(S& o) { v = o.v; }            // 비준수: const 아님 → const 객체 복사 불가
    S operator=(const S& o);        // 비준수: 값 반환(참조여야 함)
};
""",
  'good': r"""struct S {
    int v{0};
    S(const S& o) : v(o.v) {}       // 준수: const 참조 매개변수
    S& operator=(const S& o) {      // 준수: 참조 반환
        v = o.v; return *this;
    }
};
""",
  'why':'관례를 벗어난 복사/이동 시그니처는 표준 알고리즘·컨테이너와 어긋나 미묘한 오류를 만든다. const& 매개변수와 *this 참조 반환 관례를 따르라.'},

 {'id':'Rule 15.1.1','cat':'Required · Undecidable',
  'title':'생성자/소멸자 본문에서 객체의 동적 타입을 사용하지 않는다',
  'bad': r"""struct Base {
    Base() { init(); }              // 비준수: 생성 중 가상 디스패치
    virtual void init();
};
struct Derived : Base {
    void init() override;           // Base() 안에서는 호출되지 않음(Base판 호출)
};
""",
  'good': r"""struct Base {
    Base() = default;
    virtual void init();
};
struct Derived : Base {
    void init() override;
};
void setup(Derived& d) { d.init(); }  // 준수: 생성 완료 후 가상 호출
""",
  'why':'생성/소멸 중에는 동적 타입이 현재 클래스이므로 가상 호출이 파생 재정의로 가지 않아 의도와 다르게 동작한다. 생성 완료 후 호출하라.'},

 {'id':'Rule 15.1.2','cat':'Advisory · Decidable',
  'title':'모든 생성자는 기반 클래스 생성자를 명시적으로 호출한다',
  'bad': r"""struct Base { int x; explicit Base(int v) : x(v) {} };
struct Derived : Base {
    int y;
    explicit Derived(int v) : /* 비준수: Base(...) 미호출 */ y(v) {}
};
""",
  'good': r"""struct Base { int x; explicit Base(int v) : x(v) {} };
struct Derived : Base {
    int y;
    explicit Derived(int v) : Base(v), y(v) {}  // 준수: 기반 생성자 명시 호출
};
""",
  'why':'기반 생성자를 명시하지 않으면 기본 생성에 의존해 초기화 의도가 흐려진다(기본 생성자가 없으면 컴파일 오류). 항상 명시적으로 위임하라.'},

 {'id':'Rule 15.1.3','cat':'Required · Decidable',
  'title':'단일 인자로 호출 가능한 변환 연산자/생성자는 explicit로 선언한다',
  'bad': r"""struct Meters {
    double v;
    Meters(double d) : v(d) {}     // 비준수: 암묵 변환 허용
};
void travel(Meters m);
void go() { travel(3.0); }         // double → Meters 암묵 변환
""",
  'good': r"""struct Meters {
    double v;
    explicit Meters(double d) : v(d) {}  // 준수: 암묵 변환 차단
};
void travel(Meters m);
void go() { travel(Meters{3.0}); }       // 명시적 생성 필요
""",
  'why':'단일 인자 생성자/변환 연산자가 암묵 변환을 허용하면 의도치 않은 형변환이 조용히 일어난다. explicit로 선언하라.'},

 {'id':'Rule 15.1.4','cat':'Advisory · Undecidable',
  'title':'클래스의 모든 직접 비정적 데이터 멤버는 객체 접근 전에 초기화한다',
  'bad': r"""struct P {
    int x;
    int y;
    P() : x(0) { }    // 비준수: y 초기화 누락
    int sum() const { return x + y; }   // y는 미초기화 값
};
""",
  'good': r"""struct P {
    int x{0};
    int y{0};         // 준수: 모든 멤버 초기화(기본 멤버 초기화)
    P() = default;
    int sum() const { return x + y; }
};
""",
  'why':'일부 멤버가 초기화되지 않으면 객체가 비결정적 상태로 사용된다. 모든 직접 데이터 멤버를 생성 시 초기화하라.'},

 {'id':'Rule 15.1.5','cat':'Required · Decidable',
  'title':'initializer-list 생성자는 그것이 유일한 생성자일 때만 정의한다',
  'bad': r"""#include <initializer_list>
struct Vec {
    int n{0};
    Vec(std::initializer_list<int> xs) : n(static_cast<int>(xs.size())) {}
    explicit Vec(int count) : n(count) {}  // 비준수: 다른 생성자와 공존
};
void g() { Vec a{5}; /* count=5? 아니면 원소 5? 모호 */ }
""",
  'good': r"""struct Vec {
    int n{0};
    explicit Vec(int count) : n(count) {}  // 준수: 의도 명확한 단일 생성자
};
void g() { Vec a{5}; }
""",
  'why':'initializer-list 생성자가 다른 생성자와 공존하면 중괄호 초기화 시 어느 쪽이 선택될지 헷갈려 오용된다. 둘 중 하나만 두라.'},

 {'id':'Dir 15.8.1','cat':'Required · Undecidable',
  'title':'사용자 제공 복사/이동 대입 연산자는 자기 대입을 안전하게 처리한다',
  'bad': r"""struct Buf {
    char* p; int n;
    Buf& operator=(const Buf& o) {     // 비준수: 자기 대입 미처리
        delete[] p;                     // o==*this면 자기 데이터를 먼저 해제
        p = new char[o.n];
        for (int i = 0; i < o.n; ++i) p[i] = o.p[i];  // 해제된 메모리 읽기
        n = o.n; return *this;
    }
};
""",
  'good': r"""struct Buf {
    char* p; int n;
    Buf& operator=(const Buf& o) {
        if (this == &o) return *this;   // 준수: 자기 대입 가드
        char* np = new char[o.n];
        for (int i = 0; i < o.n; ++i) np[i] = o.p[i];
        delete[] p; p = np; n = o.n;
        return *this;
    }
};
""",
  'why':'자기 대입을 고려하지 않으면 자기 자원을 먼저 해제한 뒤 읽어 미정의 동작이 난다. 자기 대입 가드 또는 copy-and-swap을 적용하라.'},

 # ── 섹션 16: 오버로딩(Overloading) ─────────────────────────────────────
 {'id':'Rule 16.5.1','cat':'Required · Decidable',
  'title':'논리 AND(&&)·OR(||) 연산자를 오버로드하지 않는다',
  'bad': r"""struct Cond {
    bool v;
    // 비준수: 오버로드 시 단락 평가가 사라짐
    bool operator&&(const Cond& o) const { return v && o.v; }
};
bool test(Cond a, Cond b) { return a && b; }  // 두 피연산자 모두 평가됨
""",
  'good': r"""struct Cond {
    bool v;
    explicit operator bool() const { return v; }  // 준수: bool 변환 제공
};
bool test(Cond a, Cond b) { return a && b; }  // 내장 &&의 단락 평가 유지
""",
  'why':'&&/||를 오버로드하면 내장 연산의 단락 평가(short-circuit)가 사라져 호출자 기대가 깨진다. explicit operator bool 등으로 대체하라.'},

 {'id':'Rule 16.5.2','cat':'Required · Decidable',
  'title':'주소 연산자(단항 &)를 오버로드하지 않는다',
  'bad': r"""struct Handle {
    int id;
    // 비준수: 단항 & 오버로드 → 실제 주소를 얻을 수 없어 일반 코드가 깨짐
    int operator&() const { return id; }
};
void use(Handle h) { auto x = &h; (void)x; }  // 주소가 아니라 id 반환
""",
  'good': r"""struct Handle {
    int id;
    int key() const { return id; }   // 준수: 의도를 별도 이름 함수로
};
void use(Handle h) { Handle* p = &h; (void)p; }  // & 는 정상적으로 주소 반환
""",
  'why':'단항 & 오버로드는 객체의 실제 주소 획득을 막아 표준 라이브러리·일반 코드의 가정을 깨뜨린다. 별도 명명 함수로 의도를 표현하라.'},

 {'id':'Rule 16.6.1','cat':'Advisory · Decidable',
  'title':'대칭 연산자는 비멤버 함수로만 구현한다',
  'bad': r"""struct Money {
    long cents;
    // 비준수: 대칭 연산자를 멤버로 → 좌측 피연산자 변환 비대칭
    Money operator+(const Money& o) const { return {cents + o.cents}; }
};
// 100 + m 형태(좌측이 정수)에서는 멤버 operator+가 적용되지 않음
""",
  'good': r"""struct Money {
    long cents;
};
// 준수: 비멤버로 두어 양쪽 피연산자에 동일한 암묵 변환 적용
inline Money operator+(const Money& a, const Money& b) {
    return Money{a.cents + b.cents};
}
""",
  'why':'대칭 이항 연산자를 멤버로 두면 좌측 피연산자에만 변환이 비대칭 적용되어 a+b와 b+a가 달라질 수 있다. 비멤버 함수로 구현하라.'},
]
