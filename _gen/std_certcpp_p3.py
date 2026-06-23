# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트3: INT·ERR·CON·FIO·MSC) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17 -pthread` 기준.
주의: 검증은 컴파일 후 실행하므로 데드락/무한대기 위험 경로는 런타임에 도달하지 않게 가드한다."""

RULES = [
 {'id':'INT50-CPP','cat':'INT · Rule · L1','compiles':True,
  'title':'열거형의 범위를 벗어난 값으로 캐스트하지 않는다',
  'title_en':'Do not cast to an out-of-range enumeration value',
  'bad': r"""#include <iostream>
enum class Color { Red, Green, Blue };   // 유효 값 0,1,2
static const char* name(Color c) {
    switch (c) { case Color::Red: return "red";
                 case Color::Green: return "green";
                 case Color::Blue: return "blue"; }
    return "?";
}
int main() {
    Color c = static_cast<Color>(7);     // 범위 밖 값 — 미지정 동작
    std::cout << name(c) << '\n';         // switch 가 어떤 분기도 못 타거나 오동작
}""",
  'good': r"""#include <iostream>
enum class Color { Red, Green, Blue };
static bool to_color(int raw, Color& out) {
    if (raw < 0 || raw > 2) return false;   // 캐스트 전 범위 검사
    out = static_cast<Color>(raw);
    return true;
}
int main() {
    Color c;
    if (to_color(7, c)) std::cout << "ok\n";
    else std::cout << "rejected out-of-range\n";
}""",
  'why':'근거: 고정 기반 타입이 없는 enum 의 유효 값 집합은 열거자들을 표현하는 데 필요한 최소 비트 폭으로 정해지며, 그 범위를 벗어난 정수를 캐스트하면 미지정(또는 미정의) 값이 된다. 영향: 그런 값은 switch 의 어떤 case 에도 해당하지 않아 기본 처리가 누락되거나, 값 기반 분기·배열 인덱스로 쓰일 때 범위를 넘는 접근으로 이어진다. 대응: 외부에서 받은 정수는 유효 범위를 검사한 뒤에만 enum 으로 캐스트한다.',
  'why_en':'Rationale: for an enum without a fixed underlying type, the set of valid values is determined by the minimum bit width needed to represent its enumerators, and casting an integer outside that range yields an unspecified (or undefined) value. Impact: such a value matches no switch case so default handling is missed, and when used for value-based branching or as an array index it leads to out-of-range access. Fix: cast an externally supplied integer to the enum only after checking it is within the valid range.'},

 {'id':'ERR50-CPP','cat':'ERR · Rule · L3','compiles':True,
  'title':'프로그램을 비정상적으로 종료(abort/terminate)시키지 않는다',
  'title_en':'Do not abruptly terminate the program',
  'bad': r"""#include <iostream>
#include <cstdlib>
struct Logger { ~Logger(){ std::cout << "flush log\n"; } };   // 정리 작업
static void handle(int code, int argc) {
    Logger lg;
    if (code != 0) {
        if (argc >= 0) std::abort();   // 소멸자·정리 건너뛰고 즉시 종료(가드: 항상 참)
    }
}
int main(int argc, char**) { handle(1, argc); }""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Logger { ~Logger(){ std::cout << "flush log\n"; } };
static void handle(int code) {
    Logger lg;
    if (code != 0) throw std::runtime_error("bad state");   // 스택 풀기로 정리됨
}
int main() {
    try { handle(1); }
    catch (const std::exception& e) { std::cout << "handled: " << e.what() << '\n'; }
}""",
  'why':'근거: std::abort 와 std::terminate 는 스택 풀기를 수행하지 않으므로 활성 자동 객체의 소멸자가 호출되지 않는다. 영향: 열린 파일·획득한 잠금·버퍼에 모인 로그 같은 자원이 정리되지 않아 데이터 손상·누수·일관성 깨짐이 남는다. 대응: 오류는 예외로 전달해 정상적인 스택 풀기로 소멸자가 실행되게 하고, 최상위에서 포착해 정의된 방식으로 종료한다.',
  'why_en':'Rationale: std::abort and std::terminate do not perform stack unwinding, so destructors of active automatic objects are not run. Impact: resources such as open files, acquired locks, and buffered logs are left uncleaned, causing data corruption, leaks, and broken consistency. Fix: signal errors with exceptions so normal unwinding runs destructors, and catch at the top level to terminate in a defined way.'},

 {'id':'ERR51-CPP','cat':'ERR · Rule · L3','compiles':True,
  'title':'모든 예외를 처리한다',
  'title_en':'Handle all exceptions',
  'bad': r"""#include <stdexcept>
static void run(int argc) {
    if (argc >= 0) throw std::runtime_error("boom");   // 가드: 항상 참
}
int main(int argc, char**) {
    run(argc);            // 예외가 main 밖으로 — std::terminate
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
static void run() { throw std::runtime_error("boom"); }
int main() {
    try { run(); }
    catch (const std::exception& e) { std::cout << "err: " << e.what() << '\n'; return 1; }
    catch (...) { std::cout << "unknown error\n"; return 1; }
}""",
  'why':'근거: main 밖으로 빠져나온, 즉 어떤 핸들러도 잡지 않은 예외는 std::terminate 를 호출하며, 이때 스택 풀기 수행 여부조차 구현 정의라 소멸자가 실행되지 않을 수 있다. 영향: 진단 메시지 없이 비정상 종료되어 오류 원인 파악이 어렵고, 정리 누락으로 자원이 남는다. 대응: 최상위(main 또는 스레드 진입점)에서 std::exception 과 catch(...) 로 모든 예외를 포착해 로깅·정의된 종료 코드로 처리한다.',
  'why_en':'Rationale: an exception that escapes main — caught by no handler — calls std::terminate, and whether stack unwinding even occurs is implementation-defined, so destructors may not run. Impact: the program aborts with no diagnostic, making the cause hard to find, and leaves resources due to missed cleanup. Fix: at the top level (main or a thread entry point) catch all exceptions with std::exception and catch(...), logging and exiting with a defined code.'},

 {'id':'ERR52-CPP','cat':'ERR · Rule · L1','compiles':True,
  'title':'예외 대신 setjmp/longjmp 를 사용하지 않는다',
  'title_en':'Do not use setjmp() or longjmp()',
  'bad': r"""#include <csetjmp>
#include <iostream>
static std::jmp_buf env;
struct Guard { ~Guard(){ std::cout << "cleanup\n"; } };   // longjmp 시 호출 안 됨
static void work() {
    Guard g;
    std::longjmp(env, 1);   // g 소멸자 건너뜀 — 자원 누수
}
int main() {
    if (setjmp(env) == 0) work();
    else std::cout << "recovered\n";
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Guard { ~Guard(){ std::cout << "cleanup\n"; } };
static void work() {
    Guard g;
    throw std::runtime_error("fail");   // 예외 — 스택 풀기로 g 정상 소멸
}
int main() {
    try { work(); }
    catch (const std::exception&) { std::cout << "recovered\n"; }
}""",
  'why':'근거: longjmp 는 C 의 비지역 점프로, 스택을 되감을 때 그 사이에 살아 있던 C++ 자동 객체의 소멸자를 전혀 호출하지 않는다. 영향: 잠금·메모리·파일을 RAII 로 관리하던 객체가 정리되지 않아 누수·교착이 발생하고, 비trivial 객체가 있는 스코프를 건너뛰는 longjmp 자체가 미정의 동작이다. 대응: 오류 복구는 예외 처리(throw/catch)로 구현해 소멸자가 항상 실행되게 한다.',
  'why_en':'Rationale: longjmp is C non-local jump that, when rewinding the stack, does not call destructors of any C++ automatic objects that were alive in between. Impact: objects managing locks, memory, or files via RAII are not cleaned up, causing leaks or deadlock, and a longjmp that skips a scope containing non-trivial objects is itself undefined behaviour. Fix: implement error recovery with exception handling (throw/catch) so destructors always run.'},

 {'id':'ERR55-CPP','cat':'ERR · Rule · L1','compiles':True,
  'title':'예외 명세(noexcept)를 준수한다',
  'title_en':'Honor exception specifications',
  'bad': r"""#include <stdexcept>
static void may_throw(int argc) {
    if (argc >= 0) throw std::runtime_error("x");   // 가드: 항상 참
}
static void f(int argc) noexcept {
    may_throw(argc);      // noexcept 함수에서 예외가 빠져나감 → std::terminate
}
int main(int argc, char**) { f(argc); }""",
  'good': r"""#include <iostream>
#include <stdexcept>
static void may_throw() { throw std::runtime_error("x"); }
static void f() noexcept {
    try { may_throw(); }
    catch (...) { std::cout << "absorbed in noexcept fn\n"; }   // 명세 준수
}
int main() { f(); }""",
  'why':'근거: noexcept 로 선언한 함수에서 예외가 빠져나가면 표준은 즉시 std::terminate 를 호출하도록 규정한다(되돌릴 수 없음). 영향: 호출자가 noexcept 를 믿고 예외 처리를 생략한 상태에서 프로그램이 정리 없이 강제 종료된다. 대응: noexcept 함수 내부에서 예외를 try/catch 로 흡수하거나, 예외가 빠져나갈 수 있으면 noexcept 를 떼어 명세를 사실에 맞춘다.',
  'why_en':'Rationale: if an exception escapes a function declared noexcept, the standard mandates an immediate, unrecoverable call to std::terminate. Impact: callers that trusted noexcept and omitted handling see the program forcibly terminated without cleanup. Fix: absorb exceptions inside the noexcept function with try/catch, or remove noexcept so the specification matches reality if exceptions can escape.'},

 {'id':'ERR56-CPP','cat':'ERR · Rule · L2','compiles':True,
  'title':'예외 안전성(exception safety)을 보장한다',
  'title_en':'Guarantee exception safety',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct Node { int v; Node* clone() const { throw std::runtime_error("oom"); } };
struct Holder {
    Node* cur = nullptr;
    void set(const Node& n) {
        delete cur;            // 먼저 기존 것을 해제
        cur = n.clone();       // clone 이 던지면 cur 는 해제된 댕글링 상태로 남음
    }
};
int main() {
    Holder h; Node a{1};
    try { h.set(a); } catch (...) { std::cout << "cur is dangling now\n"; }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Node { int v; Node* clone() const { return new Node{v}; } };
struct Holder {
    Node* cur = nullptr;
    ~Holder(){ delete cur; }
    void set(const Node& n) {
        Node* tmp = n.clone();   // 먼저 성공시키고(던질 수 있는 작업 선행)
        delete cur;              // 그 다음에만 상태 교체
        cur = tmp;
    }
};
int main() {
    Holder h; Node a{1};
    h.set(a);
    std::cout << "value=" << h.cur->v << '\n';
}""",
  'why':'근거: 던질 수 있는 연산을 상태 변경의 중간에 두면, 예외 발생 시 객체가 일부만 갱신된 깨진 상태로 남는다. 영향: 예제처럼 기존 포인터를 먼저 해제하고 clone 이 던지면 cur 는 이미 해제된 메모리를 가리키는 댕글링이 되어 이후 접근이 use-after-free 가 된다. 대응: 던질 수 있는 작업을 임시 변수로 먼저 완성한 뒤, 던지지 않는 연산(swap/대입)으로 상태를 교체하는 강한 예외 보장(strong guarantee) 패턴을 쓴다.',
  'why_en':'Rationale: placing a throwing operation in the middle of a state change leaves the object in a broken, partially updated state if an exception occurs. Impact: as in the example, freeing the existing pointer first and having clone throw leaves cur dangling at freed memory, so later access is a use-after-free. Fix: complete the throwing work into a temporary first, then swap or assign with a non-throwing operation — the strong-guarantee pattern.'},

 {'id':'ERR57-CPP','cat':'ERR · Rule · L2','compiles':True,
  'title':'예외 처리 중 자원을 누수하지 않는다',
  'title_en':'Do not leak resources when handling exceptions',
  'bad': r"""#include <iostream>
#include <stdexcept>
static void risky(int argc) { if (argc >= 0) throw std::runtime_error("boom"); }
static void f(int argc) {
    int* buf = new int[100];   // raw 자원
    risky(argc);               // 예외 발생 시 아래 delete[] 를 건너뜀 → 누수
    delete[] buf;
}
int main(int argc, char**) {
    try { f(argc); } catch (...) { std::cout << "leaked buf\n"; }
}""",
  'good': r"""#include <iostream>
#include <memory>
#include <stdexcept>
static void risky() { throw std::runtime_error("boom"); }
static void f() {
    auto buf = std::make_unique<int[]>(100);   // RAII — 예외에도 자동 해제
    risky();
}
int main() {
    try { f(); } catch (...) { std::cout << "no leak (RAII freed)\n"; }
}""",
  'why':'근거: new 로 얻은 raw 자원을 보유한 채 그 뒤 코드에서 예외가 발생하면, 대응하는 delete 문장이 실행되지 않고 스택이 풀려 누수가 발생한다. 영향: 예외 경로가 반복되면 메모리·핸들이 점진적으로 고갈되어 장시간 구동 서비스가 불안정해진다. 대응: 모든 자원을 RAII 객체(unique_ptr, lock_guard, fstream)에 담아 예외로 스택이 풀릴 때 소멸자가 자동 해제하게 한다.',
  'why_en':'Rationale: holding a raw resource from new while later code throws means the matching delete statement never executes as the stack unwinds, leaking the resource. Impact: repeated exception paths progressively exhaust memory and handles, destabilizing long-running services. Fix: hold every resource in an RAII object (unique_ptr, lock_guard, fstream) so destructors free it automatically during unwinding.'},

 {'id':'ERR58-CPP','cat':'ERR · Rule · L3','compiles':True,
  'title':'main 시작 전에 던져지는 예외를 처리한다',
  'title_en':'Handle all exceptions thrown before main() begins executing',
  'bad': r"""#include <stdexcept>
struct Config { Config(){ throw std::runtime_error("cfg load failed"); } };
static Config g_cfg;      // 정적 초기화 중 예외 — main 이전이라 포착 불가 → terminate
int main() { return 0; }""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct Config { int v = 0; Config(){ throw std::runtime_error("cfg load failed"); } };
static Config& cfg() {
    static Config c;      // 최초 호출 시 초기화 — main 안에서 try 로 포착 가능
    return c;
}
int main() {
    try { (void)cfg(); }
    catch (const std::exception& e) { std::cout << "handled: " << e.what() << '\n'; }
}""",
  'why':'근거: 네임스페이스 범위 전역/정적 객체의 생성자는 main 진입 전에 실행되므로, 거기서 던진 예외를 감쌀 try 블록을 둘 수 없어 곧장 std::terminate 로 간다. 영향: 설정 로딩·자원 획득 실패가 진단 없는 비정상 종료가 되어 원인 파악과 우아한 실패 처리가 불가능하다. 대응: 무거운 초기화는 함수 내 지역 static(최초 사용 시 초기화)으로 미뤄, main 안의 제어 가능한 시점에서 try/catch 로 처리한다.',
  'why_en':'Rationale: constructors of namespace-scope global/static objects run before main begins, so there is no enclosing try block for an exception they throw, and it goes straight to std::terminate. Impact: a failed config load or resource acquisition becomes an abort with no diagnostic, making diagnosis and graceful failure impossible. Fix: defer heavy initialization to a function-local static (initialized on first use) so it can be handled with try/catch at a controlled point inside main.'},

 {'id':'ERR61-CPP','cat':'ERR · Rule · L3','compiles':True,
  'title':'예외는 lvalue 참조로 catch 한다',
  'title_en':'Catch exceptions by lvalue reference',
  'bad': r"""#include <iostream>
#include <stdexcept>
struct AppError : std::runtime_error {
    int code;
    AppError(const char* m, int c) : std::runtime_error(m), code(c) {}
};
int main() {
    try { throw AppError("disk", 42); }
    catch (std::runtime_error e) {   // 값 catch — AppError 의 code 가 슬라이싱됨
        std::cout << e.what() << '\n';   // code 정보 손실
    }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
struct AppError : std::runtime_error {
    int code;
    AppError(const char* m, int c) : std::runtime_error(m), code(c) {}
};
int main() {
    try { throw AppError("disk", 42); }
    catch (const AppError& e) {       // 참조 catch — 파생 정보·다형성 보존
        std::cout << e.what() << " code=" << e.code << '\n';
    }
}""",
  'why':'근거: 예외를 값으로 잡으면 던져진 객체가 핸들러 매개변수 타입으로 복사되며, 그 타입이 기반 클래스면 파생 부분이 잘려 나간다(slicing). 영향: 파생 예외가 담은 오류 코드·문맥 정보와 다형적 what() 동작을 잃어 진단 정보가 사라지고, 복사 비용도 든다. 대응: 예외는 const lvalue 참조로 잡아 복사·슬라이싱 없이 실제 동적 타입의 정보를 보존한다.',
  'why_en':'Rationale: catching an exception by value copies the thrown object into the handler parameter type, and if that type is a base class the derived part is sliced off. Impact: the error code, context, and polymorphic what() behaviour carried by the derived exception are lost, discarding diagnostic information and incurring a copy. Fix: catch by const lvalue reference to preserve the actual dynamic type information without a copy or slicing.'},

 {'id':'ERR62-CPP','cat':'ERR · Rule · L1','compiles':True,
  'title':'문자열을 숫자로 변환할 때 오류를 검출한다',
  'title_en':'Detect errors when converting a string to a number',
  'bad': r"""#include <iostream>
#include <cstdlib>
#include <string>
int main() {
    std::string s = "12abc";
    int n = std::atoi(s.c_str());   // 변환 실패와 정상 0 을 구분 못함, 범위초과 미검출
    std::cout << n << '\n';          // 12 — 뒤의 'abc' 가 조용히 무시됨
}""",
  'good': r"""#include <iostream>
#include <string>
#include <stdexcept>
int main() {
    std::string s = "12abc";
    try {
        std::size_t pos;
        int n = std::stoi(s, &pos);          // 범위초과 시 out_of_range, 무변환 시 invalid_argument
        if (pos != s.size()) throw std::invalid_argument("trailing chars");
        std::cout << n << '\n';
    } catch (const std::exception& e) { std::cout << "convert error: " << e.what() << '\n'; }
}""",
  'why':'근거: atoi 는 변환 실패 시 0 을 반환할 뿐 오류 신호가 없고, 변환을 멈춘 위치도 알려주지 않으며 범위 초과를 미정의 동작으로 둔다. 영향: "0" 과 변환 실패가 구분되지 않고 "12abc" 처럼 일부만 변환된 입력이 조용히 통과해, 잘못된 수치가 계산·인덱스로 흘러든다. 대응: std::stoi/stol 을 쓰고 예외와 변환 종료 위치(pos)를 검사해 전체 문자열이 정확히 소비됐는지 확인한다.',
  'why_en':'Rationale: atoi merely returns 0 on failure with no error signal, does not report where conversion stopped, and leaves out-of-range as undefined behaviour. Impact: "0" is indistinguishable from a failure and partially converted input like "12abc" passes silently, letting a wrong number flow into computations or indices. Fix: use std::stoi/stol and check both exceptions and the end position (pos) to confirm the whole string was consumed exactly.'},

 {'id':'CON50-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'잠긴 뮤텍스를 파괴하지 않는다',
  'title_en':'Do not destroy a mutex while it is locked',
  'bad': r"""#include <iostream>
#include <mutex>
int main() {
    auto* m = new std::mutex;
    m->lock();
    delete m;              // 잠긴 상태로 파괴 — 미정의 동작
    std::cout << "destroyed while locked\n";
}""",
  'good': r"""#include <iostream>
#include <mutex>
int main() {
    std::mutex m;
    {
        std::lock_guard<std::mutex> g(m);   // RAII 잠금
        std::cout << "in critical section\n";
    }                                       // 스코프 종료 시 자동 해제
    // m 은 잠기지 않은 상태로 소멸 — 안전
}""",
  'why':'근거: 표준은 어떤 스레드가 보유(잠금)하고 있는 뮤텍스를 파괴하는 것을 미정의 동작으로 규정한다(내부 OS 동기화 객체가 일관되지 않은 상태로 해제됨). 영향: 잠긴 뮤텍스 파괴는 대기 중인 다른 스레드를 영구 차단하거나 런타임 오류를 일으키며, 동적 할당된 뮤텍스에서 특히 발생하기 쉽다. 대응: 임계 영역은 lock_guard/unique_lock 같은 RAII 잠금으로 감싸 뮤텍스가 반드시 해제된 뒤에 소멸하도록 보장한다.',
  'why_en':'Rationale: the standard makes destroying a mutex that is owned (locked) by any thread undefined behaviour, since the underlying OS synchronization object is released in an inconsistent state. Impact: destroying a locked mutex can permanently block other waiting threads or raise a runtime error, and is especially easy to hit with dynamically allocated mutexes. Fix: wrap critical sections in RAII locks (lock_guard/unique_lock) so the mutex is guaranteed to be unlocked before it is destroyed.'},

 {'id':'CON51-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'예외 상황에서도 보유한 잠금을 해제한다',
  'title_en':'Ensure actively held locks are released on exceptional conditions',
  'bad': r"""#include <iostream>
#include <mutex>
#include <stdexcept>
static std::mutex m;
static void risky(int argc) { if (argc >= 0) throw std::runtime_error("boom"); }
static void f(int argc) {
    m.lock();
    risky(argc);          // 예외 발생 시 아래 unlock 을 건너뜀 → 잠금 영구 보유
    m.unlock();
}
int main(int argc, char**) {
    try { f(argc); } catch (...) { std::cout << "lock leaked\n"; }
}""",
  'good': r"""#include <iostream>
#include <mutex>
#include <stdexcept>
static std::mutex m;
static void risky() { throw std::runtime_error("boom"); }
static void f() {
    std::lock_guard<std::mutex> g(m);   // 예외로 스택이 풀려도 소멸자가 unlock
    risky();
}
int main() {
    try { f(); } catch (...) { std::cout << "lock released by RAII\n"; }
}""",
  'why':'근거: 명시적 lock 과 unlock 사이의 코드가 예외를 던지면 스택이 풀리면서 unlock 문장을 건너뛰어, 그 뮤텍스가 영원히 잠긴 채로 남는다. 영향: 같은 뮤텍스를 기다리는 다른 스레드가 모두 무기한 차단되어 교착·서비스 멈춤이 발생한다. 대응: lock_guard/unique_lock 같은 RAII 잠금을 사용해 정상 경로든 예외 경로든 스코프를 벗어날 때 자동으로 해제되게 한다.',
  'why_en':'Rationale: if code between an explicit lock and unlock throws, stack unwinding skips the unlock statement, leaving that mutex locked forever. Impact: every other thread waiting on the same mutex is blocked indefinitely, causing deadlock and a service hang. Fix: use RAII locks (lock_guard/unique_lock) so the mutex is released automatically on leaving scope, whether the path is normal or exceptional.'},

 {'id':'CON53-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'정해진 순서로 잠가 교착을 방지한다',
  'title_en':'Avoid deadlock by locking in a predefined order',
  'bad': r"""#include <iostream>
#include <mutex>
static std::mutex a, b;
// 스레드마다 잠금 순서가 다르면 교착: T1 이 a→b, T2 가 b→a 를 잡으면 서로 대기
static void t1(){ std::lock_guard<std::mutex> g1(a); std::lock_guard<std::mutex> g2(b); }
static void t2(){ std::lock_guard<std::mutex> g1(b); std::lock_guard<std::mutex> g2(a); }
int main() {
    (void)&t1; (void)&t2;   // 두 순서가 공존 — 동시 실행 시 교착 가능(여기선 실행만 회피)
    std::cout << "inconsistent lock order\n";
}""",
  'good': r"""#include <iostream>
#include <mutex>
static std::mutex a, b;
static void task() {
    std::scoped_lock lock(a, b);   // 교착 회피 알고리즘으로 여러 뮤텍스 동시 잠금
    std::cout << "both locked safely\n";
}
int main() { task(); }""",
  'why':'근거: 두 개 이상의 뮤텍스를 스레드마다 서로 다른 순서로 잠그면, 각 스레드가 상대가 이미 쥔 뮤텍스를 기다리는 순환 대기(circular wait)가 만들어져 교착에 빠진다. 영향: 교착된 스레드들은 영원히 진행하지 못해 기능이 멈추고, 타이밍 의존적이라 재현·디버깅이 어렵다. 대응: 모든 곳에서 동일한 전역 잠금 순서를 강제하거나, std::scoped_lock 으로 여러 뮤텍스를 교착 없는 알고리즘으로 한 번에 잠근다.',
  'why_en':'Rationale: locking two or more mutexes in different orders across threads creates a circular wait, where each thread waits on a mutex already held by another, leading to deadlock. Impact: the deadlocked threads never progress so functionality stalls, and being timing-dependent it is hard to reproduce and debug. Fix: enforce one consistent global lock order everywhere, or use std::scoped_lock to acquire multiple mutexes at once with a deadlock-avoidance algorithm.'},

 {'id':'CON54-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'가짜 깨어남(spurious wakeup)이 가능한 대기는 술어로 감싼다',
  'title_en':'Wrap functions that can spuriously wake up in a loop',
  'bad': r"""#include <condition_variable>
#include <mutex>
static std::mutex m;
static std::condition_variable cv;
static bool ready = false;
static void consume() {
    std::unique_lock<std::mutex> lk(m);
    if (!ready) cv.wait(lk);   // if 검사 — 가짜 깨어남이면 ready 가 거짓인데 진행
    // ... ready 를 가정하고 작업
}
int main() { (void)&consume; }   // 실행 회피(검증 시 무한대기 방지). 패턴 자체가 결함"""
,
  'good': r"""#include <iostream>
#include <condition_variable>
#include <mutex>
static std::mutex m;
static std::condition_variable cv;
static bool ready = false;
static void consume() {
    std::unique_lock<std::mutex> lk(m);
    cv.wait(lk, []{ return ready; });   // 술어 버전 — 내부에서 조건을 루프로 재확인
}
int main() {
    { std::lock_guard<std::mutex> g(m); ready = true; }
    cv.notify_one();
    consume();
    std::cout << "consumed safely\n";
}""",
  'why':'근거: 조건 변수의 wait 는 알림 없이도 깨어날 수 있는 가짜 깨어남(spurious wakeup)이 허용되므로, if 로 한 번만 조건을 검사하면 조건이 거짓인 상태로 깨어나 그대로 진행할 수 있다. 영향: 아직 준비되지 않은 데이터를 읽거나 만족하지 않은 불변식 위에서 작업해 경합·손상이 발생한다. 대응: 술어를 받는 wait(lk, pred) 형태나 while(!cond) wait(lk); 루프로 깨어날 때마다 조건을 다시 확인한다.',
  'why_en':'Rationale: a condition variable wait is permitted to return without notification (a spurious wakeup), so checking the condition only once with if can let the thread proceed while the condition is still false. Impact: it reads not-yet-ready data or operates on an unsatisfied invariant, causing races and corruption. Fix: use the predicate form wait(lk, pred) or a while(!cond) wait(lk); loop to recheck the condition on every wakeup.'},

 {'id':'CON56-CPP','cat':'CON · Rule · L2','compiles':True,
  'title':'호출 스레드가 이미 보유한 비재귀 뮤텍스를 다시 잠그지 않는다',
  'title_en':'Do not speculatively lock a non-recursive mutex that is already owned by the calling thread',
  'bad': r"""#include <mutex>
static std::mutex m;
static void inner(){ std::lock_guard<std::mutex> g(m); /* m 재잠금 */ }
static void outer(){ std::lock_guard<std::mutex> g(m); inner(); }   // 같은 스레드가 m 두 번 잠금 → 자기 교착
int main() { (void)&outer; }   // 실행 회피(검증 시 자기 교착 방지). 패턴 자체가 결함"""
,
  'good': r"""#include <iostream>
#include <mutex>
static std::mutex m;
static void inner_locked(){ /* 호출자가 m 을 이미 보유한다고 가정, 다시 잠그지 않음 */ }
static void outer(){
    std::lock_guard<std::mutex> g(m);
    inner_locked();           // 잠금을 중복 획득하지 않음
}
int main() { outer(); std::cout << "no self-deadlock\n"; }""",
  'why':'근거: 기본 std::mutex 는 비재귀(non-recursive)라 이미 잠근 스레드가 같은 뮤텍스를 다시 잠그려 하면 영원히 자기 자신을 기다리는 자기 교착(self-deadlock)이 된다(미정의 동작). 영향: 잠금을 쥔 함수가 같은 뮤텍스를 잠그는 다른 함수를 호출하는 흔한 리팩터링에서 의도치 않게 발생해 스레드가 멈춘다. 대응: 잠금을 이미 보유한 경로용 내부 함수는 다시 잠그지 않도록 설계하고, 진짜 재진입이 필요하면 std::recursive_mutex 를 명시적으로 사용한다.',
  'why_en':'Rationale: a default std::mutex is non-recursive, so a thread that has already locked it and tries to lock the same mutex again self-deadlocks, waiting on itself forever (undefined behaviour). Impact: it arises unintentionally in the common refactor where a lock-holding function calls another that also locks the same mutex, stalling the thread. Fix: design internal functions for the already-locked path so they do not lock again, and use std::recursive_mutex explicitly only when genuine reentrancy is required.'},

 {'id':'FIO50-CPP','cat':'FIO · Rule · L2','compiles':True,
  'title':'위치 지정 없이 입력과 출력을 번갈아 하지 않는다',
  'title_en':'Do not alternately input and output from a file stream without an intervening positioning call',
  'bad': r"""#include <iostream>
#include <fstream>
int main() {
    std::fstream f("data.bin", std::ios::in | std::ios::out | std::ios::trunc);
    f << "abc";
    char c;
    f >> c;        // 출력→입력 전환 전에 위치 지정 없음 — 미정의 동작
    std::cout << "read: " << c << '\n';
}""",
  'good': r"""#include <iostream>
#include <fstream>
int main() {
    std::fstream f("data.bin", std::ios::in | std::ios::out | std::ios::trunc);
    f << "abc";
    f.seekg(0);    // 명시적 위치 지정으로 입력 모드로 안전 전환
    char c;
    f >> c;
    std::cout << "read: " << c << '\n';
}""",
  'why':'근거: 읽기·쓰기를 함께 여는 갱신(update) 모드 스트림에서는, 출력 뒤 곧바로 입력(또는 그 반대)을 하기 전에 seekg/seekp/flush 같은 위치 지정 연산을 끼워 넣어야 한다는 것이 표준의 요구다. 영향: 이를 어기면 내부 버퍼와 파일 위치가 동기화되지 않아 미정의 동작이 되어, 엉뚱한 바이트를 읽거나 데이터가 유실된다. 대응: 입출력 방향을 바꿀 때마다 seek 또는 flush 로 스트림 위치를 명시적으로 동기화한다.',
  'why_en':'Rationale: on an update-mode stream opened for both reading and writing, the standard requires an intervening positioning operation such as seekg/seekp/flush before switching from output to input (or vice versa). Impact: violating this leaves the internal buffer and file position out of sync — undefined behaviour — so wrong bytes are read or data is lost. Fix: explicitly synchronize the stream position with a seek or flush each time the I/O direction changes.'},

 {'id':'FIO51-CPP','cat':'FIO · Rule · L2','compiles':True,
  'title':'더 이상 필요 없는 파일은 닫는다',
  'title_en':'Close files when they are no longer needed',
  'bad': r"""#include <cstdio>
static void process(int argc) {
    for (int i = 0; i < argc; ++i) {
        std::FILE* f = std::fopen("data.bin", "r");   // 매 반복 열기, fclose 누락
        if (f) { char b[4]; (void)std::fread(b, 1, 4, f); }  // 핸들 누수
    }
}
int main(int argc, char**) { process(argc); }""",
  'good': r"""#include <iostream>
#include <fstream>
static void process(int argc) {
    for (int i = 0; i < argc; ++i) {
        std::ifstream f("data.bin");   // RAII — 스코프 종료 시 자동 close
        char b[4]; f.read(b, 4);
    }
}
int main(int argc, char**) { process(argc); std::cout << "done\n"; }""",
  'why':'근거: 운영체제는 프로세스당 열 수 있는 파일 디스크립터 수에 한계를 두는데, 연 파일을 닫지 않으면 디스크립터가 회수되지 않고 쌓인다. 영향: 루프·장시간 구동에서 디스크립터가 고갈되면 이후 열기·소켓 생성이 모두 실패해 서비스가 마비되고, 버퍼가 flush 되지 않아 데이터가 유실될 수 있다. 대응: RAII 스트림(ifstream/ofstream)을 사용해 스코프 종료 시 자동으로 닫히게 하거나, 수동 FILE* 는 모든 경로에서 fclose 를 보장한다.',
  'why_en':'Rationale: the operating system caps the number of file descriptors per process, and not closing opened files leaves descriptors unreclaimed and accumulating. Impact: in loops or long-running services, exhausting descriptors makes all subsequent opens and socket creations fail, paralyzing the service, and unflushed buffers can lose data. Fix: use RAII streams (ifstream/ofstream) that close automatically at end of scope, or guarantee fclose on every path for a manual FILE*.'},

 {'id':'MSC50-CPP','cat':'MSC · Rule · L3','compiles':True,
  'title':'std::rand() 로 보안에 민감한 난수를 만들지 않는다',
  'title_en':'Do not use std::rand() for generating pseudorandom numbers',
  'bad': r"""#include <iostream>
#include <cstdlib>
static std::string make_token() {
    std::string t;
    for (int i = 0; i < 8; ++i) t += char('a' + std::rand() % 26);   // 예측 가능
    return t;
}
int main() { std::cout << make_token() << '\n'; }""",
  'good': r"""#include <iostream>
#include <random>
#include <string>
static std::string make_token() {
    std::random_device rd;                       // 비결정적 엔트로피 소스
    std::uniform_int_distribution<int> dist(0, 25);
    std::string t;
    for (int i = 0; i < 8; ++i) t += char('a' + dist(rd));
    return t;
}
int main() { std::cout << make_token() << '\n'; }""",
  'why':'근거: std::rand 는 구현마다 품질이 낮고 주기가 짧으며 내부 상태가 작아, 출력 몇 개만 보면 이후 값을 예측할 수 있는 경우가 많다. 영향: 토큰·세션 ID·솔트 같은 보안 요소를 rand 로 만들면 공격자가 값을 추측해 인증 우회·세션 탈취가 가능해진다. 대응: 보안 용도는 OS CSPRNG(또는 그에 시드된 엔진), 비보안 용도라도 <random> 의 분포·엔진 조합을 사용한다.',
  'why_en':'Rationale: std::rand is often low quality with a short period and small internal state, so a few outputs frequently suffice to predict subsequent values. Impact: generating security elements like tokens, session IDs, or salts with rand lets an attacker guess values, enabling authentication bypass or session hijacking. Fix: use an OS CSPRNG (or an engine seeded from one) for security, and even for non-security use the distribution/engine combinations in <random>.'},

 {'id':'MSC51-CPP','cat':'MSC · Rule · L3','compiles':True,
  'title':'난수 생성기를 적절히 시드(seed)한다',
  'title_en':'Ensure your random number generator is properly seeded',
  'bad': r"""#include <iostream>
#include <random>
int main() {
    std::mt19937 gen;          // 기본 고정 시드 — 매 실행 동일한 수열
    std::uniform_int_distribution<int> d(1, 100);
    std::cout << d(gen) << '\n';   // 항상 같은 값
}""",
  'good': r"""#include <iostream>
#include <random>
int main() {
    std::random_device rd;
    std::mt19937 gen(rd());    // 엔트로피 소스로 시드 — 실행마다 다른 수열
    std::uniform_int_distribution<int> d(1, 100);
    std::cout << d(gen) << '\n';
}""",
  'why':'근거: mt19937 같은 결정적 엔진은 같은 시드에서 항상 같은 수열을 생성하는데, 기본 생성하면 고정된 기본 시드가 쓰여 매 실행이 동일하다. 영향: 게임·시뮬레이션의 다양성이 사라지고, 보안 문맥에서는 수열이 완전히 예측 가능해져 토큰·논스를 공격자가 미리 계산할 수 있다. 대응: random_device 등 비결정적 엔트로피 소스로 엔진을 시드하고, 더 강한 무작위성이 필요하면 시드 시퀀스를 사용한다.',
  'why_en':'Rationale: a deterministic engine like mt19937 produces the same sequence from the same seed, and default-constructing it uses a fixed default seed so every run is identical. Impact: variety in games and simulations disappears, and in a security context the sequence becomes fully predictable, letting an attacker precompute tokens or nonces. Fix: seed the engine from a non-deterministic entropy source such as random_device, using a seed sequence when stronger randomness is needed.'},

 {'id':'MSC52-CPP','cat':'MSC · Rule · L1','compiles':True,
  'title':'값을 반환하는 함수는 모든 종료 경로에서 값을 반환한다',
  'title_en':'Value-returning functions must return a value from all exit paths',
  'bad': r"""#include <iostream>
static int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    // x == 0 경로에서 반환 없음 — 그 결과를 사용하면 미정의 동작
}
int main() { std::cout << sign(0) << '\n'; }""",
  'good': r"""#include <iostream>
static int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;              // 모든 경로에서 명시적 반환
}
int main() { std::cout << sign(0) << '\n'; }""",
  'why':'근거: void 가 아닌 함수가 return 문 없이 끝까지 흘러 그 반환값을 사용하면 미정의 동작이며, 컴파일러는 이를 가정해 해당 경로를 도달 불가로 최적화할 수 있다. 영향: x==0 같은 누락 경로에서 호출자가 레지스터·스택의 임의 값을 반환값으로 받아, 분기·인덱스로 쓰일 때 예측 불가능한 오동작이나 메모리 손상으로 번진다. 대응: 모든 종료 경로에서 명시적으로 값을 반환하고, 컴파일러 경고(-Wreturn-type)를 켜 누락을 잡는다.',
  'why_en':'Rationale: flowing off the end of a non-void function without a return statement and then using the result is undefined behaviour, and the compiler may assume it and optimize that path as unreachable. Impact: on a missed path like x==0 the caller receives an arbitrary register/stack value as the result, which when used for branching or indexing escalates to unpredictable misbehaviour or memory corruption. Fix: return a value explicitly on every exit path and enable compiler warnings (-Wreturn-type) to catch omissions.'},

 {'id':'MSC54-CPP','cat':'MSC · Rule · L1','compiles':True,
  'title':'시그널 핸들러는 일반(plain old) 함수로 작성한다',
  'title_en':'A signal handler must be a plain old function',
  'bad': r"""#include <iostream>
#include <csignal>
#include <string>
static void handler(int) {
    std::string s = "got signal";   // 비동기 비안전: 핸들러에서 동적 할당·스트림 사용
    std::cout << s << '\n';          // async-signal-safe 하지 않음 — 미정의 동작
}
int main() { std::signal(SIGTERM, handler); std::cout << "installed\n"; }""",
  'good': r"""#include <iostream>
#include <csignal>
#include <atomic>
static volatile std::sig_atomic_t g_flag = 0;
extern "C" void on_term(int) { g_flag = 1; }   // POF, async-safe 작업만
int main() {
    std::signal(SIGTERM, on_term);
    std::cout << "installed; flag=" << g_flag << '\n';
}""",
  'why':'근거: 시그널 핸들러는 프로그램 흐름과 비동기적으로 끼어들 수 있어, C++ 고유 기능(예외, 비trivial 객체 생성·소멸, 스트림 입출력, 동적 할당)을 호출하면 비재진입·비안전 함수를 잘못된 시점에 부르게 되어 미정의 동작이 된다. 영향: 핸들러 안의 std::string·std::cout 사용은 락·힙 상태가 일관되지 않은 순간에 진입해 교착·손상·크래시를 일으킬 수 있다. 대응: 핸들러는 C 연결의 일반 함수로 두고 volatile sig_atomic_t 플래그 설정 같은 async-signal-safe 작업만 한 뒤, 실제 처리는 메인 루프에서 수행한다.',
  'why_en':'Rationale: a signal handler can interrupt program flow asynchronously, so calling C++-specific features (exceptions, non-trivial construction/destruction, stream I/O, dynamic allocation) invokes non-reentrant, unsafe functions at the wrong moment — undefined behaviour. Impact: using std::string or std::cout in a handler may enter while locks or heap state are inconsistent, causing deadlock, corruption, or a crash. Fix: keep the handler a C-linkage plain old function doing only async-signal-safe work such as setting a volatile sig_atomic_t flag, and do the real processing in the main loop.'},

 {'id':'ERR54-CPP','cat':'ERR · Rule · L2','compiles':True,
  'title':'catch 핸들러는 가장 파생된 것부터 기본 순으로 배치한다',
  'title_en':'Catch handlers should order their parameter types from most derived to least derived',
  'bad': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::runtime_error("io"); }
    catch (const std::exception& e) {        // 기반 핸들러 먼저 — 파생도 여기서 잡힘
        std::cout << "generic: " << e.what() << '\n';
    }
    catch (const std::runtime_error& e) {    // 도달 불가 — 컴파일러 경고
        std::cout << "specific: " << e.what() << '\n';
    }
}""",
  'good': r"""#include <iostream>
#include <stdexcept>
int main() {
    try { throw std::runtime_error("io"); }
    catch (const std::runtime_error& e) {    // 파생(구체적) 먼저
        std::cout << "specific: " << e.what() << '\n';
    }
    catch (const std::exception& e) {        // 기반(일반) 나중
        std::cout << "generic: " << e.what() << '\n';
    }
}""",
  'why':'근거: catch 핸들러는 선언된 순서대로 검사되며, 던져진 예외의 타입과 호환되는 첫 핸들러가 선택된다(가상 디스패치가 아니라 순차 매칭). 영향: 기반 클래스 핸들러를 먼저 두면 모든 파생 예외가 거기서 잡혀, 뒤에 둔 더 구체적인 핸들러는 영영 도달하지 못해 의도한 세분화된 처리가 사라진다. 대응: 핸들러를 가장 파생된 타입부터 기반 타입 순으로 배치한다.',
  'why_en':'Rationale: catch handlers are examined in declaration order, and the first one compatible with the thrown exception type is chosen (sequential matching, not virtual dispatch). Impact: placing a base-class handler first catches all derived exceptions there, so a more specific handler placed afterwards is never reached and the intended fine-grained handling is lost. Fix: order handlers from the most derived type down to the base type.'},

 {'id':'ERR60-CPP','cat':'ERR · Rule · L2','compiles':True,
  'title':'예외 객체는 nothrow 복사 생성 가능해야 한다',
  'title_en':'Exception objects must be nothrow-copy-constructible',
  'bad': r"""#include <iostream>
#include <string>
struct HeavyError {
    std::string detail;                  // 복사 시 힙 할당 — 복사가 던질 수 있음
    explicit HeavyError(std::string d) : detail(std::move(d)) {}
};
int main() {
    try { throw HeavyError("disk full at sector 42"); }
    catch (const HeavyError& e) { std::cout << e.detail << '\n'; }
}""",
  'good': r"""#include <iostream>
struct LightError {
    const char* msg;                     // 복사가 noexcept(포인터 복사뿐)
    explicit LightError(const char* m) noexcept : msg(m) {}
};
int main() {
    try { throw LightError("disk full at sector 42"); }
    catch (const LightError& e) { std::cout << e.msg << '\n'; }
}""",
  'why':'근거: 예외 객체는 던지고 잡는 과정에서 구현이 복사·이동할 수 있는데, 그 복사 생성자가 또 예외를 던지면(예: std::string 복사 중 메모리 부족) 예외 처리 도중 새 예외가 발생해 std::terminate 로 간다. 영향: 정작 오류를 알리려던 예외가 전파 중 복사 실패로 프로그램을 강제 종료시켜, 진단조차 남기지 못하는 최악의 시점에 죽는다. 대응: 예외 타입은 복사·이동이 noexcept 가 되도록 설계하고(예: 동적 할당 멤버 대신 고정 버퍼·리터럴 포인터·참조 카운트 문자열), 풍부한 정보가 필요하면 표준 예외처럼 내부적으로 nothrow 복사를 보장하는 형태를 쓴다.',
  'why_en':'Rationale: an exception object may be copied or moved by the implementation while being thrown and caught, and if that copy constructor itself throws (e.g. out of memory while copying a std::string), a new exception arises during handling and goes to std::terminate. Impact: the very exception meant to report an error kills the program due to a copy failure during propagation, dying at the worst moment with no diagnostic. Fix: design exception types so copy/move is noexcept (e.g. a fixed buffer, literal pointer, or reference-counted string instead of a dynamically allocating member), using forms that guarantee nothrow copy internally when rich information is needed.'},
]
