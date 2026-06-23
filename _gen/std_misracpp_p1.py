# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트1: 섹션 0~8) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17` 기준."""

RULES = [
 {'id':'Rule 0.0.1','cat':'Required · Decidable','compiles':True,
  'title':'함수에 도달 불가능한 코드를 두지 않는다',
  'title_en':'A function shall not contain unreachable statements',
  'bad': r"""#include <iostream>
static int scale(int x){
    return x * 2;
    std::cout << "scaling " << x << '\n';   // return 이후 — 절대 실행되지 않음
}
int main(){ std::cout << scale(21) << '\n'; }""",
  'good': r"""#include <iostream>
static int scale(int x){
    std::cout << "scaling " << x << '\n';   // 의도한 순서로 배치
    return x * 2;
}
int main(){ std::cout << scale(21) << '\n'; }""",
  'why':'return·throw·무조건 분기 이후에 놓인 도달 불가 코드는 제어 흐름을 잘못 작성했다는 신호이며, 의도한 로깅·정리 같은 부작용이 실행되지 않는 결함을 숨긴다. 도달 불가 코드는 제거하거나 흐름을 바로잡는다.',
  'why_en':'Unreachable code after return, throw, or an unconditional branch signals mis-written control flow and hides a defect where intended side effects such as logging or cleanup never run. Remove unreachable code or fix the flow.'},

 {'id':'Rule 0.1.1','cat':'Advisory · Decidable','compiles':True,
  'title':'계산된 값이 사용되지 않게 두지 않는다(useless value)',
  'title_en':'A value should not be unnecessarily computed (a computed value should be used)',
  'bad': r"""#include <iostream>
static int compute(){ return 42; }
int main(){
    int n = compute();   // compute() 결과를 읽기 전에
    n = 0;               // 곧바로 덮어씀 — 죽은 계산, 대입 누락 의심
    std::cout << n << '\n';
}""",
  'good': r"""#include <iostream>
static int compute(){ return 42; }
int main(){
    int n = compute();   // 계산한 값을 실제로 사용
    std::cout << n << '\n';
}""",
  'why':'읽히기 전에 덮어써지는 계산 결과는 죽은 계산이며, 흔히 대입을 빠뜨렸거나 조건 분기를 잘못 작성했다는 신호다. 사용되지 않는 계산은 제거하거나, 누락된 로직을 채워 그 값을 실제로 사용하도록 고친다.',
  'why_en':'A computed result overwritten before it is read is dead computation and usually signals a missed assignment or a wrong branch. Remove the unused computation, or fix the missing logic so the value is actually used.'},

 {'id':'Rule 0.1.2','cat':'Advisory · Decidable','compiles':True,
  'title':'사용되지 않는 변수/멤버를 두지 않는다',
  'title_en':'A named object that is not used should not be declared',
  'bad': r"""#include <iostream>
static int read_sensor(){ return 7; }
static void do_other(){ std::cout << "other\n"; }
int main(){
    int tmp = read_sensor();   // 어디서도 사용되지 않음 — 누락 로직 의심
    do_other();
}""",
  'good': r"""#include <iostream>
static void do_other(){ std::cout << "other\n"; }
int main(){
    do_other();   // 사용되지 않는 변수와 그 부작용 호출을 함께 정리
}""",
  'why':'사용되지 않는 객체는 빠뜨린 로직(읽어 놓고 쓰지 않음)을 의심하게 만들고 코드를 어지럽혀 가독성을 떨어뜨린다. 미사용 변수·멤버는 제거하되, 부작용 있는 초기화였다면 그 의도까지 검토해 정리한다.',
  'why_en':'An unused object suggests omitted logic (read but never used) and clutters the code, hurting readability. Remove unused variables and members, and when the initializer had side effects, review that intent while cleaning up.'},

 {'id':'Rule 0.2.2','cat':'Required · Decidable','compiles':True,
  'title':'한 객체에 같은 값을 중복으로 대입하지 않는다(중복 부작용)',
  'title_en':'A function or object should not be assigned a value that is never used before being overwritten',
  'bad': r"""#include <iostream>
static int seq = 0;
static int compute(){ return ++seq; }
int main(){
    int x = compute();
    x = compute();        // 첫 compute() 결과를 쓰지 않고 즉시 덮어씀 — 의도 불명·부작용 중복
    std::cout << x << " seq=" << seq << '\n';
}""",
  'good': r"""#include <iostream>
static int seq = 0;
static int compute(){ return ++seq; }
int main(){
    int x = compute();    // 필요한 만큼만 호출
    std::cout << x << " seq=" << seq << '\n';
}""",
  'why':'같은 객체에 사용되지 않은 값을 연달아 대입하면 첫 결과(그리고 그 함수의 부작용)가 무의미하게 버려져, 의도를 알 수 없고 부작용이 중복 수행되어 성능·정확성 문제를 만든다. 필요한 대입만 남기고 중복을 제거한다.',
  'why_en':'Assigning successive unused values to the same object discards the first result (and its function’s side effects) pointlessly, obscuring intent and duplicating side effects with performance and correctness costs. Keep only the needed assignment and remove the duplication.'},

 {'id':'Rule 4.6.1','cat':'Advisory · Undecidable','compiles':True,
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'title_en':'The behaviour of a program shall not depend on the order of evaluation of side effects',
  'bad': r"""#include <iostream>
static void use(int a, int b){ std::cout << a << ' ' << b << '\n'; }
int main(){
    int i = 0;
    use(i++, i++);   // 두 인자의 평가 순서가 미명세 — 결과가 컴파일러마다 다름
}""",
  'good': r"""#include <iostream>
static void use(int a, int b){ std::cout << a << ' ' << b << '\n'; }
int main(){
    int i = 0;
    int a = i++;     // 부작용을 분리해 순서를 확정
    int b = i++;
    use(a, b);
}""",
  'why':'함수 인자나 한 식에서 같은 객체를 여러 번 수정하면(use(i++, i++)) 부작용의 평가 순서가 미명세라 결과가 컴파일러·최적화 수준마다 달라진다. 부작용을 별도 문장으로 분리해 순서를 명확히 확정한다.',
  'why_en':'Modifying the same object multiple times in function arguments or one expression (use(i++, i++)) leaves the order of side effects unspecified, so results vary by compiler and optimization level. Split side effects into separate statements to fix the order definitively.'},

 {'id':'Rule 5.13.1','cat':'Required · Decidable','compiles':True,
  'title':'표준에 정의된 이스케이프 시퀀스만 사용한다',
  'title_en':'Octal and hexadecimal escape sequences, and the escape sequences defined by the standard, shall be used correctly',
  'bad': r"""#include <iostream>
int main(){
    const char* s = "a\qb";   // \q 는 표준에 없는 이스케이프 — 구현정의/미정의
    std::cout << s << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    const char* s = "a\tb";   // 표준 이스케이프(\t)만 사용
    std::cout << s << '\n';
}""",
  'why':'표준이 정의하지 않은 이스케이프 시퀀스(\\q 등)는 구현마다 다르게 해석되거나 미정의 동작이 되어 의도와 다른 문자가 들어간다. \\t, \\n, \\\\ 처럼 표준이 정의한 이스케이프만 사용해 문자열의 의미를 고정한다.',
  'why_en':'Escape sequences not defined by the standard (such as \\q) are interpreted differently across implementations or are undefined, inserting unintended characters. Use only standard-defined escapes like \\t, \\n, \\\\ to fix the string’s meaning.'},

 {'id':'Rule 5.13.3','cat':'Required · Decidable','compiles':True,
  'title':'8진(octal) 상수와 8진 이스케이프 사용을 피한다',
  'title_en':'Octal constants shall not be used',
  'bad': r"""#include <iostream>
int main(){
    int perm = 0755;        // 8진 상수(=493) — 십진 755 로 오독하기 쉬움
    std::cout << perm << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    int perm = 0x1ED;       // 또는 493 (십진) — 의도가 분명
    std::cout << perm << '\n';
}""",
  'why':'선행 0이 붙은 정수는 8진수로 해석되어 0755 가 493 이 되는 등 십진으로 오독하기 쉬워, 권한 비트·코드 값 설정에서 미묘한 버그를 만든다. 십진 또는 명시적 16진(0x) 표기를 사용한다.',
  'why_en':'An integer with a leading 0 is interpreted as octal, so 0755 is 493 — easily misread as decimal, producing subtle bugs in permission bits and code values. Use decimal or explicit hexadecimal (0x) notation.'},

 {'id':'Rule 5.13.5','cat':'Required · Decidable','compiles':True,
  'title':'정수 리터럴의 접미사는 대문자로 표기한다',
  'title_en':'The lowercase form of L shall be used in integer literal suffixes',
  'bad': r"""#include <iostream>
int main(){
    long v = 100l;          // 끝의 'l' 이 숫자 '1' 과 구분되지 않음 (1001?)
    std::cout << v << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    long v = 100L;          // 대문자 L — 명확
    std::cout << v << '\n';
}""",
  'why':'소문자 l 접미사는 글꼴에 따라 숫자 1과 거의 구분되지 않아 100l 이 1001 처럼 오독되어 값 자체를 잘못 읽게 만든다. 정수 리터럴 접미사는 항상 대문자(L, LL, U)로 표기한다.',
  'why_en':'A lowercase l suffix is nearly indistinguishable from the digit 1 in many fonts, so 100l can be misread as 1001, causing the value itself to be misread. Always write integer literal suffixes in uppercase (L, LL, U).'},

 {'id':'Rule 6.0.1','cat':'Required · Decidable','compiles':True,
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지 않게 한다',
  'title_en':'A declaration shall not hide a declaration with the same name in an enclosing scope',
  'bad': r"""#include <iostream>
static int count = 0;        // 파일 범위
static void tick(){
    int count = 5;           // 바깥 count 를 가림(shadow)
    count++;                 // 전역은 갱신되지 않는다 — 혼동
    std::cout << "local=" << count << '\n';
}
int main(){ tick(); std::cout << "global=" << count << '\n'; }""",
  'good': r"""#include <iostream>
static int g_count = 0;      // 전역은 접두사로 구분
static void tick(){
    int local = 5;           // 바깥 이름과 다르게
    local++;
    g_count++;               // 의도가 명확
    std::cout << "local=" << local << '\n';
}
int main(){ tick(); std::cout << "global=" << g_count << '\n'; }""",
  'why':'안쪽 범위에서 바깥 식별자와 같은 이름을 선언하면(shadowing) 어느 객체를 쓰는지 혼동되어, 전역을 갱신하려다 지역만 바꾸는 결함을 만든다. 내부 식별자는 바깥 이름과 다르게(예: 접두사) 지어 가림을 방지한다.',
  'why_en':'Declaring an inner-scope name identical to an enclosing identifier (shadowing) confuses which object is used, causing defects where a global is meant to be updated but only the local changes. Name inner identifiers differently (e.g., with a prefix) to avoid hiding.'},

 {'id':'Rule 6.4.1','cat':'Required · Decidable','compiles':True,
  'title':'식별자는 가능한 가장 좁은 범위에서 선언한다',
  'title_en':'An identifier declared in a block shall have a scope no larger than necessary',
  'bad': r"""#include <iostream>
int main(){
    int a[4] = {1, 2, 3, 4};
    int tmp;                       // 루프 밖에 선언 — 범위가 필요 이상으로 넓음
    for (int i = 0; i < 4; ++i) {
        tmp = a[i];
        std::cout << tmp << ' ';
    }
    std::cout << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    int a[4] = {1, 2, 3, 4};
    for (int i = 0; i < 4; ++i) {
        int tmp = a[i];            // 사용 지점에 가장 가까운 좁은 범위에 선언
        std::cout << tmp << ' ';
    }
    std::cout << '\n';
}""",
  'why':'필요 이상으로 넓은 범위에 선언된 변수는 의도치 않은 재사용·상태 누출의 위험을 키우고, 반복 간에 이전 값이 남아 미묘한 버그를 만든다. 식별자는 사용 지점에 가장 가까운 가장 좁은 범위에 선언해 수명을 한정한다.',
  'why_en':'A variable declared in a scope larger than necessary increases the risk of accidental reuse and state leakage, and leftover values across iterations cause subtle bugs. Declare identifiers in the narrowest scope nearest their use to bound their lifetime.'},

 {'id':'Rule 6.7.1','cat':'Required · Decidable','compiles':True,
  'title':'지역 정적(local static) 객체를 신중히 사용한다(스레드 안전·초기화 순서)',
  'title_en':'Local objects with static storage duration shall be used with care',
  'bad': r"""#include <iostream>
static int init(){ return 100; }
static int& counter(){
    static int n = init();   // 초기화 시점·스레드 경합·전역 상태 공유가 숨음
    return n;
}
int main(){ std::cout << ++counter() << '\n'; }""",
  'good': r"""#include <iostream>
struct Counter { int n = 0; int next(){ return ++n; } };   // 수명·상태를 명시적으로 소유
int main(){
    Counter c;               // 의존성을 주입/명시적으로 관리
    std::cout << c.next() << '\n';
}""",
  'why':'함수 지역 정적 객체는 첫 호출 시 초기화되어 초기화 순서·스레드 안전(동시 첫 호출 경합)·암묵적 전역 상태 공유 문제를 코드 뒤에 숨긴다. 상태의 수명과 동기화를 명시적으로 설계하거나 의존성을 주입해 가시화한다.',
  'why_en':'A function-local static is initialized on first call, hiding initialization-order, thread-safety (races on concurrent first call), and implicit global-state-sharing issues behind the code. Design the state’s lifetime and synchronization explicitly, or inject the dependency to make it visible.'},

 {'id':'Rule 6.8.2','cat':'Mandatory · Undecidable','compiles':True,
  'title':'수명이 끝난 객체에 대한 참조/포인터를 반환·사용하지 않는다',
  'title_en':'A function shall not return a reference or a pointer to an object whose lifetime has ended',
  'bad': r"""#include <iostream>
static const int& make(){
    int local = 42;
    return local;     // 지역 객체 참조 반환 — 함수 종료 후 댕글링
}
int main(){
    const int& r = make();
    std::cout << r << '\n';   // 무효 참조 사용 — 미정의 동작
}""",
  'good': r"""#include <iostream>
static int make(){
    int local = 42;
    return local;     // 값으로 반환 — 호출자가 복사본을 소유
}
int main(){
    int v = make();
    std::cout << v << '\n';
}""",
  'why':'지역 객체의 참조·주소는 함수가 반환되면 수명이 끝나 무효가 되므로, 그것을 반환·보관해 사용하면 사라진 스택 객체를 가리키는 댕글링 접근(미정의 동작)이 된다. 값으로 반환하거나 수명이 보장된 객체(호출자 소유·동적 수명)를 가리키게 한다.',
  'why_en':'A reference or address to a local object becomes invalid when the function returns, so returning or retaining and using it is a dangling access (undefined behaviour) to a vanished stack object. Return by value, or refer to an object with guaranteed lifetime (caller-owned or dynamic).'},

 {'id':'Rule 7.0.2','cat':'Required · Decidable','compiles':True,
  'title':'조건 문맥에는 본질적으로 bool 인 표현식을 사용한다',
  'title_en':'The operand of an explicit or implicit conversion to bool shall be of essentially Boolean type',
  'bad': r"""#include <iostream>
static int* find(int* a, int n, int key){
    for (int i = 0; i < n; ++i) { if (a[i] == key) return &a[i]; }
    return nullptr;
}
int main(){
    int a[3] = {1, 2, 3};
    int* p = find(a, 3, 2);
    if (p) {                 // 포인터를 bool 처럼 — 의도 모호
        std::cout << *p << '\n';
    }
}""",
  'good': r"""#include <iostream>
static int* find(int* a, int n, int key){
    for (int i = 0; i < n; ++i) { if (a[i] == key) return &a[i]; }
    return nullptr;
}
int main(){
    int a[3] = {1, 2, 3};
    int* p = find(a, 3, 2);
    if (p != nullptr) {      // 명시적 비교로 bool 표현식 구성
        std::cout << *p << '\n';
    }
}""",
  'why':'포인터나 정수를 그대로 조건에 쓰면 "널이 아님/0이 아님" 이라는 비교가 암묵화되어 의도가 모호해지고, 비교 대상을 잘못 가정하는 결함을 부른다. p != nullptr, n != 0 처럼 명시적 비교로 본질적 bool 표현식을 만든다.',
  'why_en':'Using a pointer or integer directly as a condition hides the implicit "not null / not zero" comparison, obscuring intent and inviting wrong assumptions about what is tested. Build an essentially Boolean expression with explicit comparisons such as p != nullptr or n != 0.'},

 {'id':'Rule 7.0.5','cat':'Required · Decidable','compiles':True,
  'title':'암시적 정수 변환이 값을 손실하거나 부호를 바꾸지 않게 한다',
  'title_en':'Integer conversions shall not lose information or change signedness unexpectedly',
  'bad': r"""#include <iostream>
#include <cstdint>
int main(){
    int wide = 300;
    std::uint8_t b = wide;   // 8비트 초과분 절단 → 44
    std::cout << static_cast<int>(b) << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstdint>
int main(){
    int wide = 300;
    if (wide >= 0 && wide <= 0xFF) {                 // 범위 검사 후
        auto b = static_cast<std::uint8_t>(wide);    // 명시적 변환으로 의도 표현
        std::cout << static_cast<int>(b) << '\n';
    } else {
        std::cout << "out of range\n";
    }
}""",
  'why':'넓은 정수를 좁은 타입으로 암시 변환하면 상위 비트가 잘리거나 부호 있는/없는 변환으로 값이 바뀌어, 의도와 다른 값이 조용히 저장된다. 변환 전 범위를 검사하고 static_cast 로 명시적으로 변환해 손실 가능성을 드러낸다.',
  'why_en':'Implicitly converting a wide integer to a narrower type truncates high bits or changes the value through signed/unsigned conversion, silently storing the wrong value. Check the range before converting and use static_cast to make the conversion — and its potential loss — explicit.'},

 {'id':'Rule 7.11.1','cat':'Required · Decidable','compiles':True,
  'title':'널 포인터 상수로는 nullptr 만 사용한다',
  'title_en':'nullptr shall be the only form of the null pointer constant',
  'bad': r"""#include <iostream>
int main(){
    int* p = 0;          // 정수 0 을 널 포인터로 — 오버로드 해석·가독성 문제
    if (p == 0) {
        std::cout << "null\n";
    }
}""",
  'good': r"""#include <iostream>
int main(){
    int* p = nullptr;    // 타입 안전한 널 포인터 상수
    if (p == nullptr) {
        std::cout << "null\n";
    }
}""",
  'why':'0 이나 NULL 을 널 포인터로 쓰면 정수와 포인터 문맥이 섞여, 정수 오버로드와 포인터 오버로드 중 잘못된 쪽이 선택되는 오버로드 해석 오류를 부르고 가독성도 떨어진다. C++ 에서는 타입이 포인터로 고정된 nullptr 만 사용한다.',
  'why_en':'Using 0 or NULL as a null pointer mixes integer and pointer contexts, causing overload-resolution errors where an integer overload is chosen over a pointer one, and hurts readability. In C++, use only nullptr, whose type is fixed as a pointer.'},

 {'id':'Rule 8.0.1','cat':'Required · Decidable','compiles':True,
  'title':'연산자 우선순위는 괄호로 명시한다',
  'title_en':'Parentheses should be used to make the meaning of an expression appropriately explicit',
  'bad': r"""#include <iostream>
int main(){
    int a = 1, b = 2, c = 1, d = 6;
    int r = a + b << c & d;   // 우선순위 혼동: ((a+b)<<c)&d
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    int a = 1, b = 2, c = 1, d = 6;
    int r = ((a + b) << c) & d;   // 의도한 평가 순서를 괄호로 명시
    std::cout << r << '\n';
}""",
  'why':'시프트·비트·산술 연산이 섞인 식은 우선순위를 사람이 오해하기 쉬워, 작성자의 의도와 컴파일러의 해석이 어긋난다. 괄호로 평가 순서를 분명히 하면 의도가 코드에 드러나고 검토 오류가 줄어든다.',
  'why_en':'Expressions mixing shift, bitwise, and arithmetic operators are easy for humans to misread on precedence, so the author’s intent and the compiler’s interpretation diverge. Parentheses make the evaluation order explicit, surfacing intent and reducing review errors.'},

 {'id':'Rule 8.2.2','cat':'Required · Decidable','compiles':True,
  'title':'C 스타일 캐스트를 사용하지 않는다',
  'title_en':'C-style casts and functional notation casts shall not be used',
  'bad': r"""#include <iostream>
int main(){
    double d = 3.9;
    int n = (int)d;       // C 스타일 캐스트 — 어떤 변환인지 드러나지 않음
    std::cout << n << '\n';
}""",
  'good': r"""#include <iostream>
int main(){
    double d = 3.9;
    int n = static_cast<int>(d);   // 의도가 명확한 C++ 캐스트
    std::cout << n << '\n';
}""",
  'why':'C 스타일 캐스트 (int)d 는 static_cast·const_cast·reinterpret_cast 중 무엇을 수행하는지 드러나지 않아, const 제거나 위험한 재해석 같은 의도를 숨기고 검색·검토를 어렵게 한다. 의도를 명시하는 C++ 캐스트(static_cast 등)를 사용한다.',
  'why_en':'A C-style cast (int)d does not reveal whether it performs static_cast, const_cast, or reinterpret_cast, hiding intent such as const removal or dangerous reinterpretation and making it hard to search and review. Use the C++ casts that state intent (static_cast, etc.).'},

 {'id':'Rule 8.2.3','cat':'Required · Decidable','compiles':True,
  'title':'캐스트로 const/volatile 한정을 제거하지 않는다',
  'title_en':'A cast shall not remove any const or volatile qualification from the type of a pointer or reference',
  'bad': r"""#include <iostream>
int main(){
    const int v = 7;
    const int& r = v;
    const_cast<int&>(r) = 9;   // 실제 const 객체를 수정 — 미정의 동작
    std::cout << v << '\n';
}""",
  'good': r"""#include <iostream>
static void set(int& v, int x){ v = x; }   // 수정이 필요하면 비-const 인터페이스
int main(){
    int v = 7;
    set(v, 9);
    std::cout << v << '\n';
}""",
  'why':'const_cast 로 한정을 떼어내고 실제로 const 로 선언된 객체를 수정하면 미정의 동작이 되고, 컴파일러의 const 최적화 가정을 깨뜨려 예측 불가한 결과를 만든다. 수정이 필요한 대상은 처음부터 비-const 인터페이스로 다루고 const 한정을 제거하지 않는다.',
  'why_en':'Casting away qualifiers with const_cast and then modifying an object actually declared const is undefined behaviour and breaks the compiler’s const-based optimization assumptions, yielding unpredictable results. Handle objects that must be modified through a non-const interface from the start and do not strip const.'},

 {'id':'Rule 8.2.5','cat':'Required · Decidable','compiles':True,
  'title':'reinterpret_cast 를 사용하지 않는다',
  'title_en':'reinterpret_cast shall not be used',
  'bad': r"""#include <iostream>
#include <cstdint>
int main(){
    float f = 1.0f;
    auto u = *reinterpret_cast<std::uint32_t*>(&f);   // 엄격 별칭·정렬 규칙 위반
    std::cout << u << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstdint>
#include <cstring>
int main(){
    float f = 1.0f;
    std::uint32_t u;
    std::memcpy(&u, &f, sizeof u);   // 안전한 비트 재해석
    std::cout << u << '\n';
}""",
  'why':'reinterpret_cast 로 한 타입의 객체를 다른 타입으로 재해석해 접근하면 엄격 별칭(strict aliasing)과 정렬 규칙을 어겨 미정의 동작이 되고, 최적화 시 예측 불가한 결과가 나온다. 비트 패턴 재해석은 std::memcpy(또는 C++20 std::bit_cast)로 안전하게 수행한다.',
  'why_en':'Reinterpreting an object of one type as another via reinterpret_cast and accessing it violates strict aliasing and alignment rules — undefined behaviour with unpredictable results under optimization. Reinterpret bit patterns safely with std::memcpy (or std::bit_cast in C++20).'},

 {'id':'Rule 8.2.10','cat':'Required · Decidable','compiles':True,
  'title':'함수를 정의되지 않은 시그니처로 호출하지 않는다',
  'title_en':'Functions shall not be called through a pointer of an incompatible function type',
  'bad': r"""#include <iostream>
static void g(int x){ std::cout << x << '\n'; }
int main(){
    auto fp = reinterpret_cast<void(*)()>(&g);   // 다른 시그니처로 변환
    fp();                                        // 인자 없이 호출 — 미정의 동작
}""",
  'good': r"""#include <iostream>
static void g(int x){ std::cout << x << '\n'; }
int main(){
    void (*fp)(int) = &g;   // 실제 시그니처와 일치하는 포인터
    fp(3);
}""",
  'why':'함수를 실제 정의와 다른 시그니처의 포인터로 호출하면 인자·반환값 전달 규약이 어긋나 스택·레지스터가 오염되는 미정의 동작이 된다. 함수 포인터는 대상 함수의 정확한 타입으로 선언하고 그 시그니처대로 호출한다.',
  'why_en':'Calling a function through a pointer with a signature different from its real definition mismatches the argument/return calling convention, corrupting the stack and registers — undefined behaviour. Declare function pointers with the target function’s exact type and call them according to that signature.'},

 {'id':'Rule 8.3.1','cat':'Required · Decidable','compiles':True,
  'title':'시프트 횟수는 0 이상이며 피연산자 비트폭 미만이어야 한다',
  'title_en':'The right operand of a shift operator shall lie between zero and one less than the width in bits of the left operand',
  'bad': r"""#include <iostream>
#include <cstdint>
int main(){
    std::uint32_t v = 1;
    unsigned n = 40;
    auto r = v << n;     // 32비트를 40 만큼 시프트 — 미정의 동작
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstdint>
int main(){
    std::uint32_t v = 1;
    unsigned n = 40;
    if (n < 32u) {       // 0..31 범위 보장
        auto r = v << n;
        std::cout << r << '\n';
    } else {
        std::cout << "shift out of range\n";
    }
}""",
  'why':'피연산자의 비트폭 이상으로, 또는 음수로 시프트하면 결과가 미정의가 되어 0·원값·쓰레기 등 플랫폼마다 다르게 동작한다. 시프트량을 0..(폭-1) 범위로 검증한 뒤에만 시프트한다.',
  'why_en':'Shifting by the operand width or more, or by a negative amount, is undefined behaviour that yields 0, the original, or garbage depending on the platform. Validate the shift amount to the range 0..(width-1) before shifting.'},

 {'id':'Rule 8.7.1','cat':'Required · Undecidable','compiles':True,
  'title':'포인터 산술 결과는 같은 배열의 범위 안을 가리켜야 한다',
  'title_en':'A pointer operand and any pointer resulting from pointer arithmetic shall address an element of the same array',
  'bad': r"""#include <iostream>
static int get_offset(){ return 12; }
int main(){
    int a[10] = {0};
    int* p = a + get_offset();   // 배열(10) 밖을 가리킴
    *p = 7;                      // 경계 밖 쓰기 — 미정의 동작
    std::cout << a[0] << '\n';
}""",
  'good': r"""#include <iostream>
static int get_offset(){ return 12; }
int main(){
    int a[10] = {0};
    int i = get_offset();
    if (i >= 0 && i < 10) {      // 인덱스를 검증해 범위 내에서만 접근
        a[i] = 7;
    } else {
        std::cout << "offset out of range\n";
    }
    std::cout << a[0] << '\n';
}""",
  'why':'배열 경계를 벗어난 포인터를 만들어 역참조하면 인접 메모리를 침범하는 미정의 동작이 되어 데이터 손상·보안 결함으로 이어진다. 인덱스를 사용 전에 [0, 길이) 범위로 검증해 항상 같은 배열 안을 가리키는 접근만 수행한다.',
  'why_en':'Forming and dereferencing a pointer past an array’s bounds is undefined behaviour that intrudes on adjacent memory, causing corruption or security defects. Validate the index against [0, length) before use so accesses stay within the same array.'},

 {'id':'Rule 8.18.1','cat':'Mandatory · Undecidable','compiles':True,
  'title':'겹치는(overlapping) 객체에 대입/복사하지 않는다',
  'title_en':'An object shall not be assigned or copied to an overlapping object',
  'bad': r"""#include <iostream>
#include <cstring>
int main(){
    char buf[8] = "abcdefg";
    std::memcpy(buf, buf + 1, 4);   // 원본과 대상 영역이 중첩 — 미정의 동작
    std::cout << buf << '\n';
}""",
  'good': r"""#include <iostream>
#include <cstring>
int main(){
    char buf[8] = "abcdefg";
    std::memmove(buf, buf + 1, 4);  // 중첩을 허용하도록 정의된 함수
    std::cout << buf << '\n';
}""",
  'why':'memcpy 나 단순 대입은 원본과 대상 메모리가 겹치지 않는다고 가정하므로, 중첩된 영역에 사용하면 복사 도중 원본을 덮어써 미정의 동작과 데이터 손상이 발생한다. 중첩 가능성이 있으면 중첩을 허용하도록 정의된 std::memmove 를 사용한다.',
  'why_en':'memcpy and plain assignment assume the source and destination do not overlap, so using them on overlapping regions overwrites the source mid-copy — undefined behaviour and data corruption. When overlap is possible, use std::memmove, which is defined to handle it.'},

 {'id':'Rule 8.19.1','cat':'Advisory · Decidable','compiles':True,
  'title':'쉼표(,) 연산자를 사용하지 않는다',
  'title_en':'The comma operator should not be used',
  'bad': r"""#include <iostream>
static int a(){ std::cout << "a "; return 1; }
static int b(){ std::cout << "b "; return 2; }
int main(){
    int x = (a(), b());   // 두 부작용을 한 식에 숨김 — a() 결과는 버려짐
    std::cout << "x=" << x << '\n';
}""",
  'good': r"""#include <iostream>
static int a(){ std::cout << "a "; return 1; }
static int b(){ std::cout << "b "; return 2; }
int main(){
    a();                  // 부작용을 문장으로 분리
    int x = b();
    std::cout << "x=" << x << '\n';
}""",
  'why':'쉼표 연산자는 여러 부작용과 평가 순서를 한 식에 압축해 숨기고 좌변 결과를 조용히 버려, 가독성과 정적 분석을 모두 해친다. 각 부작용을 독립된 문장으로 분리하면 실행 순서와 의도가 분명해진다.',
  'why_en':'The comma operator packs multiple side effects and their order into one expression and silently discards the left result, hurting readability and static analysis. Splitting each side effect into its own statement makes execution order and intent clear.'},

 {'id':'Rule 8.7.2','cat':'Required · Undecidable','compiles':True,
  'title':'관계 연산은 같은 배열/객체를 가리키는 포인터끼리만 한다',
  'title_en':'The relational operators shall not be applied to pointers that do not address elements of the same array',
  'bad': r"""#include <iostream>
int main(){
    int x[4] = {0};
    int y[4] = {0};
    if (&x[0] < &y[0]) {   // 서로 다른 배열의 포인터 대소 비교 — 미정의
        std::cout << "x before y\n";
    }
}""",
  'good': r"""#include <iostream>
int main(){
    int ix = 1, iy = 3;
    if (ix < iy) {         // 인덱스로 비교하거나, 같은 배열 내 포인터만 비교
        std::cout << "x before y\n";
    }
}""",
  'why':'서로 다른 객체·배열을 가리키는 포인터의 대소 비교 결과는 표준이 보장하지 않아 미정의이며, 메모리 배치 가정에 의존한 코드는 플랫폼마다 다르게 동작한다. 같은 배열 내 포인터끼리 비교하거나 인덱스로 비교한다.',
  'why_en':'Relational comparison of pointers to different objects or arrays is undefined, so code relying on memory-layout assumptions behaves differently across platforms. Compare pointers within the same array, or compare indices instead.'},
]
