# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트3: 섹션 17 이상) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C++ 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu++17` 기준."""

RULES = [
 {'id':'Rule 17.8.1','cat':'Advisory · Decidable','compiles':True,
  'title':'함수 템플릿의 명시적 특수화를 사용하지 않는다',
  'title_en':'Function templates should not be explicitly specialized',
  'bad': r"""#include <iostream>
template <typename T> void f(T){ std::cout << "generic\n"; }
template <> void f<int>(int){ std::cout << "int special\n"; }   // 함수 템플릿 특수화 — 오버로드 함정
int main(){ f(3); }""",
  'good': r"""#include <iostream>
template <typename T> void f(T){ std::cout << "generic\n"; }
void f(int){ std::cout << "int overload\n"; }   // 일반 오버로드
int main(){ f(3); }""",
  'why':'함수 템플릿의 명시적 특수화는 오버로드 해석에 직접 참여하지 않고 이미 선택된 기본 템플릿에 한해 적용되므로, 일반 오버로드가 함께 있으면 직관과 다른 함수가 선택되는 함정을 만든다. 동작을 분기하려면 명시적 특수화 대신 일반 함수 오버로드를 사용한다.',
  'why_en':'An explicit function-template specialization does not take part in overload resolution directly but only applies once the primary template is chosen, so with overloads present an unexpected function may be selected. Use ordinary function overloads instead of explicit specialization to branch behaviour.'},

 {'id':'Rule 18.1.1','cat':'Required · Decidable','compiles':True,
  'title':'예외는 값으로 throw 한다(포인터로 throw 금지)',
  'title_en':'An exception object shall be thrown by value, not by pointer',
  'bad': r"""#include <stdexcept>
#include <iostream>
struct MyError : std::runtime_error { using std::runtime_error::runtime_error; };
int main(){
    try { throw new MyError("disk"); }   // 포인터 throw — 누가 delete? 누수·이중해제 모호
    catch (MyError* e){ std::cout << e->what() << '\n'; delete e; }
}""",
  'good': r"""#include <stdexcept>
#include <iostream>
struct MyError : std::runtime_error { using std::runtime_error::runtime_error; };
int main(){
    try { throw MyError("disk"); }        // 값으로 throw
    catch (const MyError& e){ std::cout << e.what() << '\n'; }   // const 참조로 catch
}""",
  'why':'예외를 포인터로 던지면 예외 객체를 누가·언제 해제해야 하는지 모호해져, catch 측이 delete 를 빠뜨리면 누수, 중복 delete 하면 이중 해제가 발생한다. 예외는 값으로 던지고 const 참조로 잡아 수명을 런타임이 자동 관리하게 한다.',
  'why_en':'Throwing an exception by pointer makes it unclear who frees the object and when, so the catch site leaks if it forgets delete or double-frees if it deletes twice. Throw by value and catch by const reference so the runtime manages the lifetime automatically.'},

 {'id':'Rule 18.3.2','cat':'Required · Decidable','compiles':True,
  'title':'예외는 const 참조(const lvalue reference)로 catch 한다',
  'title_en':'Exceptions shall be caught by const lvalue reference',
  'bad': r"""#include <stdexcept>
#include <iostream>
int main(){
    try { throw std::runtime_error("boom"); }
    catch (std::exception e){   // 값으로 catch — 파생 예외가 base 로 슬라이싱
        std::cout << e.what() << '\n';
    }
}""",
  'good': r"""#include <stdexcept>
#include <iostream>
int main(){
    try { throw std::runtime_error("boom"); }
    catch (const std::exception& e){   // const 참조 — 다형성·메시지 보존
        std::cout << e.what() << '\n';
    }
}""",
  'why':'예외를 값으로 잡으면 던져진 파생 예외 객체가 base 타입으로 복사되며 슬라이싱되어, 파생 클래스가 담고 있던 정보와 다형적 what() 동작을 잃는다. const 참조로 잡으면 복사 없이 다형성을 보존하고 불필요한 사본도 피한다.',
  'why_en':'Catching by value copies the thrown derived exception into the base type, slicing off the derived information and polymorphic what() behaviour. Catching by const reference preserves polymorphism without a copy and avoids an unnecessary duplicate.'},

 {'id':'Rule 18.4.1','cat':'Required · Decidable','compiles':True,
  'title':'예외를 던지지 않는 함수는 noexcept 로 표시하고 명세를 준수한다',
  'title_en':'A function declared noexcept shall not exit via an exception',
  'bad': r"""#include <stdexcept>
static void may_throw(){ throw std::runtime_error("x"); }
static void f() noexcept { may_throw(); }   // noexcept 인데 예외가 빠져나감 → std::terminate
int main(){ (void)&f; return 0; }""",
  'good': r"""#include <stdexcept>
#include <iostream>
static void may_throw(){ throw std::runtime_error("x"); }
static void f() noexcept {
    try { may_throw(); }
    catch (...) { std::cout << "handled internally\n"; }   // 명세대로 내부에서 처리
}
int main(){ f(); }""",
  'why':'noexcept 로 선언한 함수에서 예외가 빠져나가면 C++ 런타임은 즉시 std::terminate 를 호출해 프로그램을 강제 종료한다. noexcept 함수는 내부에서 모든 예외를 처리하거나, 예외가 나갈 수 있다면 noexcept 명세를 제거한다.',
  'why_en':'If an exception escapes a function declared noexcept, the C++ runtime immediately calls std::terminate, forcibly ending the program. A noexcept function must handle all exceptions internally, or its noexcept specification must be removed if exceptions can escape.'},

 {'id':'Rule 18.5.1','cat':'Required · Decidable','compiles':True,
  'title':'소멸자나 해제 연산에서 예외가 빠져나가지 않게 한다',
  'title_en':'A destructor shall not exit via an exception',
  'bad': r"""#include <stdexcept>
struct File {
    void flush(){ throw std::runtime_error("io"); }
    ~File(){ flush(); }   // 소멸자에서 예외 탈출 가능 → 스택 풀기 중이면 std::terminate
};
int main(){ (void)sizeof(File); return 0; }""",
  'good': r"""#include <stdexcept>
#include <iostream>
struct File {
    void flush(){ throw std::runtime_error("io"); }
    ~File() noexcept {
        try { flush(); }
        catch (...) { std::cout << "flush failed; logged\n"; }   // 내부에서 흡수
    }
};
int main(){ File f; (void)f; }""",
  'why':'예외로 인한 스택 풀기(unwinding) 도중 또 다른 예외가 소멸자에서 탈출하면 C++ 는 동시에 두 예외를 처리할 수 없어 std::terminate 를 호출한다. 소멸자는 noexcept 로 두고 내부에서 발생할 수 있는 예외를 try/catch 로 흡수(로깅 후 무시)한다.',
  'why_en':'If, during stack unwinding caused by one exception, another escapes a destructor, C++ cannot handle two simultaneously and calls std::terminate. Make destructors noexcept and absorb any internal exceptions with try/catch (log and swallow).'},

 {'id':'Rule 19.0.2','cat':'Required · Decidable','compiles':True,
  'title':'함수형 매크로보다 inline/constexpr 함수를 사용한다',
  'title_en':'A function-like macro shall not be used where an inline or constexpr function can be used',
  'bad': r"""#include <iostream>
#define MAX(a,b) ((a) > (b) ? (a) : (b))
int main(){
    int i = 3, j = 5;
    int y = MAX(i++, j);   // i 가 두 번 평가될 수 있음 — 부작용 중복
    std::cout << y << " i=" << i << '\n';
}""",
  'good': r"""#include <iostream>
template <typename T>
constexpr T imax(T a, T b){ return (a > b) ? a : b; }   // 1회 평가 + 타입 안전
int main(){
    int i = 3, j = 5;
    int y = imax(i++, j);
    std::cout << y << " i=" << i << '\n';
}""",
  'why':'함수형 매크로는 인자를 본문에 그대로 펼쳐 i++ 같은 부작용을 여러 번 평가하고 타입 검사도 하지 못해, 미정의 동작과 진단되지 않는 버그를 만든다. inline·constexpr(템플릿) 함수는 동일한 성능에 인자를 한 번만 평가하고 타입 안전성까지 제공한다.',
  'why_en':'A function-like macro pastes its argument into the body, evaluating side effects like i++ multiple times and skipping type checking, producing undefined behaviour and silent bugs. An inline/constexpr (template) function gives the same performance while evaluating the argument once and enforcing type safety.'},

 {'id':'Rule 19.1.1','cat':'Required · Decidable','compiles':True,
  'title':'#include 에는 올바른 헤더명 형식만 사용한다',
  'title_en':'The #include directive shall be followed by a valid header name',
  'bad': r"""#define HDR <cstdio>
#include HDR          // 매크로 확장으로 헤더명 생성 — 올바른 형식 보장 안 됨
int main(){ std::printf("ok\n"); return 0; }""",
  'good': r"""#include <cstdio>   // 직접 헤더명을 명시
int main(){ std::printf("ok\n"); return 0; }""",
  'why':'매크로 확장으로 헤더명을 만들면 확장 결과가 올바른 <...> 또는 "..." 형식이 된다는 보장이 없어, 컴파일러·이식 환경마다 다르게 해석될 위험이 있다. #include 에는 헤더명을 직접 적어 형식을 고정한다.',
  'why_en':'Generating a header name via macro expansion does not guarantee the result is a valid <...> or "..." form, risking different interpretations across compilers and ports. Write the header name directly in #include to fix the form.'},

 {'id':'Rule 19.3.4','cat':'Required · Decidable','compiles':True,
  'title':'함수형 매크로 매개변수는 괄호로 감싼다',
  'title_en':'Parameters in a function-like macro shall be enclosed in parentheses',
  'bad': r"""#include <iostream>
#define SCALE(x) x * 2      // 매개변수·전체를 괄호로 감싸지 않음
int main(){
    int a = 1, b = 2;
    int r = SCALE(a + b);   // a + b * 2 = 5 (의도는 6)
    std::cout << r << '\n';
}""",
  'good': r"""#include <iostream>
#define SCALE(x) ((x) * 2)  // 각 매개변수와 전체 식을 괄호로 보호
int main(){
    int a = 1, b = 2;
    int r = SCALE(a + b);   // ((a + b) * 2) = 6
    std::cout << r << '\n';
}""",
  'why':'함수형 매크로에서 매개변수와 전체 식을 괄호로 감싸지 않으면, 전개 시 호출부 표현식과 매크로 본문의 연산자 우선순위가 섞여 SCALE(a+b) 가 a + b*2 처럼 의도와 다른 식이 된다. 각 매개변수와 결과 전체를 괄호로 보호한다(다만 가능하면 inline 함수를 우선한다).',
  'why_en':'Without parenthesizing the parameters and the whole expression, expansion mixes the caller’s expression with the macro body’s operator precedence, turning SCALE(a+b) into a + b*2. Protect each parameter and the entire result with parentheses (though an inline function is preferable).'},

 {'id':'Rule 21.2.1','cat':'Required · Decidable','compiles':True,
  'title':'<cstdio> 의 표준 입출력 기능을 사용하지 않는다',
  'title_en':'The C Standard Library input/output functions shall not be used',
  'bad': r"""#include <cstdio>
int main(){
    int v = 42;
    std::printf("v=%d\n", v);   // 포맷 문자열·타입 불일치 위험(%d 와 인자 불일치 시 미정의)
}""",
  'good': r"""#include <iostream>
int main(){
    int v = 42;
    std::cout << "v=" << v << '\n';   // 타입 안전한 스트림
}""",
  'why':'cstdio 의 printf 계열은 포맷 문자열과 인자의 타입 일치를 컴파일러가 강제하지 못해, 불일치 시 미정의 동작과 포맷 문자열 취약점을 부른다. 타입 안전한 C++ 스트림(std::cout)이나 검증된 전용 I/O 계층을 사용한다.',
  'why_en':'The printf family in cstdio does not have the compiler enforce type agreement between the format string and arguments, so mismatches cause undefined behaviour and format-string vulnerabilities. Use type-safe C++ streams (std::cout) or a validated dedicated I/O layer.'},

 {'id':'Rule 21.6.1','cat':'Advisory · Decidable','compiles':True,
  'title':'동적 메모리는 직접 new/delete 대신 스마트 포인터로 관리한다',
  'title_en':'Dynamic memory should be managed with smart pointers rather than raw new/delete',
  'bad': r"""#include <iostream>
struct Widget { int v{7}; };
static void use(){
    Widget* w = new Widget();
    if (w->v == 0) { return; }   // 예외/조기 반환 경로에서 delete 누락 → 누수
    std::cout << w->v << '\n';
    delete w;
}
int main(){ use(); }""",
  'good': r"""#include <iostream>
#include <memory>
struct Widget { int v{7}; };
static void use(){
    auto w = std::make_unique<Widget>();   // 모든 경로에서 자동 해제
    if (w->v == 0) { return; }
    std::cout << w->v << '\n';
}
int main(){ use(); }""",
  'why':'명시적 new/delete 는 중간의 예외나 조기 반환 경로에서 delete 를 빠뜨리면 누수, 중복 실행하면 이중 해제가 되어 수명 관리 책임이 개발자에게 흩어진다. make_unique/make_shared 로 소유권을 스마트 포인터에 위임하면 모든 경로(예외 포함)에서 자동으로 해제된다.',
  'why_en':'Explicit new/delete scatter lifetime responsibility onto the developer — a missed delete on an exception or early-return path leaks, and a duplicated one double-frees. Delegating ownership to make_unique/make_shared releases the object automatically on every path, including exceptions.'},

 {'id':'Rule 21.6.5','cat':'Required · Decidable','compiles':True,
  'title':'불완전(incomplete) 타입 포인터를 delete 하지 않는다',
  'title_en':'A pointer to an incomplete type shall not be deleted',
  'bad': r"""struct Impl;                       // 전방 선언만 — 불완전 타입
static void f(Impl* p){ delete p; }   // 소멸자 호출 여부가 미정의 → 누수·손상
int main(){ f(nullptr); return 0; }""",
  'good': r"""#include <memory>
struct Impl { int v{0}; ~Impl(){} };   // 완전 정의가 보이는 곳
static Impl* create(){ return new Impl(); }
static void destroy(Impl* p){ delete p; }   // 완전 타입에서 삭제
int main(){
    std::unique_ptr<Impl, void(*)(Impl*)> p{create(), &destroy};
    return p->v;
}""",
  'why':'불완전 타입(전방 선언만 된 타입) 포인터를 delete 하면 컴파일러가 소멸자와 객체 크기를 몰라 소멸자를 호출하지 않거나 잘못 해제해 누수·메모리 손상이 발생한다. 완전 정의가 보이는 위치에서 삭제하거나, 완전 타입에서 만든 전용 deleter 를 사용한다.',
  'why_en':'Deleting a pointer to an incomplete type (only forward-declared) leaves the compiler unaware of the destructor and object size, so it skips the destructor or frees incorrectly — leaking or corrupting memory. Delete where the complete definition is visible, or use a dedicated deleter created in a complete-type context.'},

 {'id':'Rule 21.6.2','cat':'Required · Decidable','compiles':True,
  'title':'delete 의 형태(배열/단일)를 new 의 형태와 일치시킨다',
  'title_en':'The form of delete shall match the form of the corresponding new',
  'bad': r"""int main(){
    int* a = new int[10];   // 배열 new
    a[0] = 1;
    delete a;               // 단일 delete — 형태 불일치, 미정의 동작
    return 0;
}""",
  'good': r"""#include <memory>
int main(){
    auto a = std::make_unique<int[]>(10);   // 형태를 자동으로 맞춰 해제
    a[0] = 1;
    return a[0];
}""",
  'why':'new[] 로 할당한 메모리는 delete[] 로, new 로 할당한 것은 delete 로 해제해야 하며, 형태가 어긋나면 배열 원소들의 소멸자 미호출이나 잘못된 해제 루틴 사용으로 미정의 동작이 된다. std::make_unique<T[]> 나 컨테이너로 올바른 해제를 자동화한다.',
  'why_en':'Memory from new[] must be freed with delete[] and from new with delete; a form mismatch skips element destructors or uses the wrong deallocation routine — undefined behaviour. Automate correct deallocation with std::make_unique<T[]> or a container.'},

 {'id':'Rule 21.10.1','cat':'Required · Decidable','compiles':True,
  'title':'<csetjmp> 의 setjmp/longjmp 를 사용하지 않는다',
  'title_en':'The facilities provided by <csetjmp> shall not be used',
  'bad': r"""#include <csetjmp>
#include <iostream>
static std::jmp_buf env;
static void recover(){ std::cout << "recovered\n"; }
int main(){
    if (setjmp(env) != 0) { recover(); return 0; }   // longjmp 는 자동 객체 소멸자 건너뜀
    /* ... 어딘가에서 std::longjmp(env, 1) ... */
    return 0;
}""",
  'good': r"""#include <stdexcept>
#include <iostream>
static void work(){ throw std::runtime_error("fail"); }
static void recover(){ std::cout << "recovered\n"; }
int main(){
    try { work(); }
    catch (const std::exception&) { recover(); }   // 예외 — 스택 풀기로 소멸자 호출 보장
    return 0;
}""",
  'why':'longjmp 는 중간 스택 프레임의 자동 객체 소멸자를 호출하지 않은 채 점프하므로, RAII 로 관리되는 자원이 해제되지 않아 누수와 C++ 객체 모델 위반이 발생한다. 비국소 제어 이동이 필요하면 예외 처리를 사용해 스택 풀기 시 소멸자가 정상 호출되게 한다.',
  'why_en':'longjmp jumps without invoking the destructors of automatic objects in intermediate frames, so RAII-managed resources are not released, causing leaks and violating the C++ object model. Use exceptions for non-local transfer so destructors run correctly during stack unwinding.'},

 {'id':'Rule 21.10.2','cat':'Required · Decidable','compiles':True,
  'title':'<csignal> 의 시그널 처리를 사용하지 않는다',
  'title_en':'The signal handling facilities of <csignal> shall not be used',
  'bad': r"""#include <csignal>
#include <iostream>
static void handler(int){ /* 핸들러에서 할 수 있는 일이 매우 제한적 */ }
int main(){
    std::signal(SIGINT, handler);   // 비동기·구현정의 — 안전필수 C++ 에 부적합
    std::cout << "running\n";
}""",
  'good': r"""#include <iostream>
static bool stop_requested(){ return true; }   // 협조적으로 검사하는 상태 플래그
static void step(){ /* 한 단계 처리 */ }
int main(){
    while (!stop_requested()) { step(); }   // 결정적·추적 가능한 폴링
    std::cout << "stopped\n";
}""",
  'why':'시그널은 임의 시점에 비동기로 끼어들고 핸들러에서 호출 가능한 연산이 매우 제한적이며 동작이 구현정의라, C++ 객체·예외 모델과 충돌하고 안전필수 시스템에서 예측 불가하다. 종료·이벤트 요청은 상태 플래그를 협조적으로 폴링하는 결정적 메커니즘으로 처리한다.',
  'why_en':'Signals interrupt asynchronously at arbitrary points, the operations callable in a handler are very limited, and behaviour is implementation-defined, clashing with the C++ object/exception model and being unpredictable in safety-critical systems. Handle shutdown/event requests via a deterministic mechanism that cooperatively polls a status flag.'},

 {'id':'Rule 22.3.1','cat':'Required · Decidable','compiles':True,
  'title':'errno 기반 오류 검출에 의존하지 않는다',
  'title_en':'Reliance on errno-based error detection shall be avoided',
  'bad': r"""#include <cstdlib>
#include <cerrno>
#include <iostream>
int main(){
    errno = 0;
    double v = std::strtod("1.5", nullptr);
    if (errno != 0) { std::cout << "error\n"; }   // 전역 errno 의존 — 출처가 흐려짐
    std::cout << v << '\n';
}""",
  'good': r"""#include <optional>
#include <string>
#include <iostream>
static std::optional<double> parse_double(const std::string& s){
    try { return std::stod(s); }       // 오류를 예외/optional 로 명시 전달
    catch (...) { return std::nullopt; }
}
int main(){
    auto v = parse_double("1.5");
    if (!v) { std::cout << "error\n"; return 1; }
    std::cout << *v << '\n';
}""",
  'why':'전역 변수 errno 는 어느 호출이 설정했는지 명확하지 않고, 멀티스레드·재진입 환경에서 다른 코드가 덮어쓸 수 있어 오류 출처를 흐린다. 오류는 반환값·std::optional·예외로 함수 인터페이스에서 명시적으로 전달해 호출자가 출처와 처리를 분명히 하게 한다.',
  'why_en':'The global errno does not clearly indicate which call set it and can be overwritten by other code in multithreaded or reentrant contexts, obscuring the error’s origin. Convey errors explicitly through return values, std::optional, or exceptions in the function interface so the caller knows the source and handling.'},

 {'id':'Rule 23.11.1','cat':'Advisory · Decidable','compiles':True,
  'title':'raw 포인터로 스마트 포인터를 중복 생성해 소유권을 이중으로 만들지 않는다',
  'title_en':'A raw pointer shall not be used to construct multiple independent owning smart pointers',
  'bad': r"""#include <memory>
#include <iostream>
int main(){
    int* raw = new int(1);
    std::shared_ptr<int> a(raw);
    std::shared_ptr<int> b(raw);   // 같은 raw 로 별도 제어블록 2개 → 이중 해제
    std::cout << *a << *b << '\n';
}""",
  'good': r"""#include <memory>
#include <iostream>
int main(){
    auto a = std::make_shared<int>(1);
    auto b = a;                    // 제어블록을 공유 — 참조 카운트로 안전하게 해제
    std::cout << *a << *b << '\n';
}""",
  'why':'같은 raw 포인터로 서로 독립된 shared_ptr 를 만들면 각자 별도의 제어 블록(참조 카운트)을 가져, 둘이 각각 0이 될 때 같은 메모리를 두 번 해제하는 이중 해제가 발생한다. make_shared 로 한 번만 생성하고 복사로 소유권을 공유해 단일 제어 블록을 유지한다.',
  'why_en':'Constructing independent shared_ptrs from the same raw pointer gives each its own control block (reference count), so when both reach zero the same memory is freed twice — a double free. Create once with make_shared and share ownership by copying to keep a single control block.'},

 {'id':'Rule 24.5.1','cat':'Required · Decidable','compiles':True,
  'title':'<cstring> 의 경계 없는 문자열 함수를 사용하지 않는다',
  'title_en':'The unbounded string functions of <cstring> shall not be used',
  'bad': r"""#include <cstring>
#include <iostream>
int main(){
    char d[8];
    const char* src = "this is far too long";
    std::strcpy(d, src);   // 대상 크기 무시 — 버퍼 오버플로우
    std::cout << d << '\n';
}""",
  'good': r"""#include <string>
#include <iostream>
int main(){
    std::string src = "this is far too long";
    std::string d = src;   // 길이를 자동 관리 — 오버플로우 불가
    std::cout << d << '\n';
}""",
  'why':'strcpy/strcat 같은 경계 없는 함수는 대상 버퍼 크기를 모른 채 복사하므로, 원본이 대상보다 길면 인접 메모리를 덮어쓰는 버퍼 오버플로우(보안 결함의 주원인)를 일으킨다. std::string 은 길이를 스스로 관리해 오버플로우를 구조적으로 차단한다.',
  'why_en':'Unbounded functions like strcpy/strcat copy without knowing the destination size, so a source longer than the destination overruns adjacent memory — a leading cause of security defects. std::string manages its own length, structurally preventing overflow.'},

 {'id':'Rule 25.5.1','cat':'Required · Decidable','compiles':True,
  'title':'전역 로케일 변경 함수가 반환한 포인터를 보관해 재사용하지 않는다',
  'title_en':'A pointer returned by a locale-changing function shall not be stored for later reuse',
  'bad': r"""#include <clocale>
#include <iostream>
int main(){
    char* a = std::setlocale(LC_ALL, "C");
    std::setlocale(LC_ALL, "POSIX");   // a 가 가리키던 내용이 덮어써질 수 있음
    if (a) std::cout << a << '\n';
}""",
  'good': r"""#include <clocale>
#include <string>
#include <iostream>
static std::string current_locale_name(){
    const char* p = std::setlocale(LC_ALL, nullptr);
    return p ? std::string(p) : std::string();   // 값으로 즉시 복사 보관
}
int main(){
    std::string saved = current_locale_name();
    std::setlocale(LC_ALL, "POSIX");
    std::cout << saved << '\n';
}""",
  'why':'setlocale 등 로케일 변경 함수가 반환한 포인터는 다음 호출에서 내부 버퍼가 덮어써질 수 있어, 그 포인터를 보관했다 재사용하면 무관한 값을 읽게 된다. 필요한 값은 std::string 등으로 즉시 복사해 보관한다.',
  'why_en':'A pointer returned by locale-changing functions like setlocale may be overwritten on the next call, so storing and reusing it later reads an unrelated value. Copy any needed value immediately into something like std::string.'},

 {'id':'Rule 26.3.1','cat':'Required · Decidable','compiles':True,
  'title':'정렬/연관 컨테이너에 엄격 약순서를 만족하는 술어를 제공한다',
  'title_en':'A comparator shall impose a strict weak ordering',
  'bad': r"""#include <algorithm>
#include <vector>
#include <iostream>
int main(){
    std::vector<int> v = {3, 1, 2, 1};
    std::sort(v.begin(), v.end(),
              [](int a, int b){ return a <= b; });   // <= 는 엄격 약순서 위반 → 미정의
    std::cout << v.front() << '\n';
}""",
  'good': r"""#include <algorithm>
#include <vector>
#include <iostream>
int main(){
    std::vector<int> v = {3, 1, 2, 1};
    std::sort(v.begin(), v.end(),
              [](int a, int b){ return a < b; });   // 동치를 false 로 두는 < 술어
    std::cout << v.front() << '\n';
}""",
  'why':'std::sort 나 std::map 의 비교 술어는 엄격 약순서(strict weak ordering)를 요구하는데, <= 는 동치 원소에 대해서도 true 를 반환해 이 규약을 위반하여 범위를 벗어난 접근 등 미정의 동작을 일으킨다. 동치일 때 false 를 반환하는 < 형태의 술어를 제공한다.',
  'why_en':'Comparators for std::sort or std::map require a strict weak ordering, but <= returns true even for equivalent elements, violating the contract and causing undefined behaviour such as out-of-range access. Provide a < -style comparator that returns false for equivalent elements.'},

 {'id':'Rule 26.3.2','cat':'Required · Decidable','compiles':True,
  'title':'무효화된 반복자/참조를 사용하지 않는다',
  'title_en':'An invalidated iterator or reference shall not be used',
  'bad': r"""#include <vector>
#include <iostream>
int main(){
    std::vector<int> v = {1, 2, 3};
    auto it = v.begin();
    v.push_back(9);    // 재할당 시 it 무효화 가능
    std::cout << *it << '\n';   // 무효 반복자 역참조 — 미정의 동작
}""",
  'good': r"""#include <vector>
#include <iostream>
int main(){
    std::vector<int> v = {1, 2, 3};
    v.push_back(9);
    auto it = v.begin();   // 수정 후에 반복자를 다시 획득
    std::cout << *it << '\n';
}""",
  'why':'vector 의 push_back 등 컨테이너 수정은 내부 재할당을 유발해 기존 반복자·포인터·참조를 무효화하며, 무효화된 것을 사용하면 해제된 메모리를 가리키는 미정의 동작이 된다. 컨테이너를 수정한 뒤에는 반복자·참조를 다시 획득해 사용한다.',
  'why_en':'Container modifications such as vector::push_back can trigger reallocation that invalidates existing iterators, pointers, and references, and using an invalidated one is undefined behaviour pointing at freed memory. Re-acquire iterators and references after modifying the container.'},

 {'id':'Rule 28.6.3','cat':'Required · Decidable','compiles':True,
  'title':'이동된(moved-from) 객체의 값에 의존하지 않는다',
  'title_en':'The value of a moved-from object shall not be relied upon',
  'bad': r"""#include <string>
#include <utility>
#include <iostream>
int main(){
    std::string a = "hello";
    std::string b = std::move(a);
    std::cout << a << '\n';   // a 는 유효하나 값이 미지정 — 출력 결과가 비결정적
}""",
  'good': r"""#include <string>
#include <utility>
#include <iostream>
int main(){
    std::string a = "hello";
    std::string b = std::move(a);
    a = "reset";              // 재사용 전에 명확한 값을 다시 대입
    std::cout << a << '\n';
}""",
  'why':'std::move 후의 원본 객체는 소멸·재대입은 안전하지만 그 값은 "유효하나 미지정(valid but unspecified)" 상태라, 그 값을 읽거나 의존하면 구현·타입마다 다른 비결정적 결과가 나온다. 이동된 객체를 다시 쓰려면 먼저 명확한 값을 대입한 뒤 사용한다.',
  'why_en':'After std::move, the source object is safe to destroy or reassign, but its value is "valid but unspecified," so reading or depending on it yields non-deterministic, implementation- and type-dependent results. To reuse a moved-from object, assign it a definite value first.'},

 {'id':'Rule 28.6.4','cat':'Required · Decidable','compiles':True,
  'title':'전달 참조(forwarding reference)는 std::forward 로 전달한다',
  'title_en':'A forwarding reference shall be forwarded with std::forward',
  'bad': r"""#include <utility>
#include <string>
#include <iostream>
static void sink(std::string s){ std::cout << s << '\n'; }
template <typename T>
static void wrap(T&& x){ sink(std::move(x)); }   // lvalue 인자까지 이동 → 호출자 객체 훼손
int main(){
    std::string a = "data";
    wrap(a);
    std::cout << "after: [" << a << "]\n";   // a 가 비워질 수 있음
}""",
  'good': r"""#include <utility>
#include <string>
#include <iostream>
static void sink(std::string s){ std::cout << s << '\n'; }
template <typename T>
static void wrap(T&& x){ sink(std::forward<T>(x)); }   // 값 범주 보존 — lvalue 는 복사
int main(){
    std::string a = "data";
    wrap(a);
    std::cout << "after: [" << a << "]\n";   // a 보존됨
}""",
  'why':'전달 참조 T&& 에 std::move 를 쓰면 인자가 lvalue 든 rvalue 든 무조건 이동시켜, 호출자가 계속 쓰려던 lvalue 객체까지 비워 버리는 훼손이 발생한다. std::forward<T> 는 원래 값 범주(lvalue/rvalue)를 보존해 rvalue 만 이동하고 lvalue 는 복사로 전달한다.',
  'why_en':'Using std::move on a forwarding reference T&& moves the argument unconditionally whether it is an lvalue or rvalue, clobbering even an lvalue object the caller intended to keep. std::forward<T> preserves the original value category, moving only rvalues and copying lvalues.'},

 {'id':'Rule 30.0.1','cat':'Required · Decidable','compiles':True,
  'title':'C 표준 입출력(<cstdio>) 대신 C++ 문자열/스트림을 사용한다',
  'title_en':'C Standard I/O shall be replaced by C++ strings/streams',
  'bad': r"""#include <cstdio>
#include <iostream>
int main(){
    char buf[16];
    int v = 1234567;
    std::sprintf(buf, "%d", v);   // 대상 크기 미검사 — 큰 값이면 오버플로우
    std::cout << buf << '\n';
}""",
  'good': r"""#include <string>
#include <iostream>
int main(){
    int v = 1234567;
    std::string s = std::to_string(v);   // 길이를 자동 관리
    std::cout << s << '\n';
}""",
  'why':'sprintf 같은 cstdio 함수는 대상 버퍼 크기를 검사하지 않아 변환 결과가 길면 버퍼 오버플로우가 발생하고, 포맷-인자 타입 불일치 시 미정의 동작이 된다. std::to_string·std::string·스트림은 길이를 자동 관리하고 타입 안전해 이런 결함을 구조적으로 제거한다.',
  'why_en':'cstdio functions like sprintf do not check the destination buffer size, so a long conversion overflows the buffer, and format/argument type mismatches cause undefined behaviour. std::to_string, std::string, and streams manage length automatically and are type-safe, structurally removing these defects.'},
]
