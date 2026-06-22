# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트3: 섹션 17 이상) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'Rule 17.8.1','cat':'Advisory · Decidable',
  'title':'함수 템플릿의 명시적 특수화를 사용하지 않는다',
  'bad': r"""template <typename T> void f(T);
template <> void f<int>(int);   // 함수 템플릿 특수화 — 오버로드 함정""",
  'good': r"""template <typename T> void f(T);
void f(int);          // 일반 오버로드""",
  'why':'함수 템플릿 명시적 특수화는 오버로드 해석과의 상호작용이 직관에 반해 잘못된 함수가 선택될 수 있다. 일반 오버로드를 사용한다.'},

 {'id':'Rule 18.1.1','cat':'Required · Decidable',
  'title':'예외는 값으로 throw 한다(포인터로 throw 금지)',
  'bad': r"""throw new MyError("x");   // 포인터 — 소유권·누수 모호""",
  'good': r"""throw MyError("x");""",
  'why':'포인터를 던지면 누가 해제할지 모호해 누수·이중 해제가 난다. 예외는 값으로 던지고 const 참조로 잡는다.'},

 {'id':'Rule 18.3.2','cat':'Required · Decidable',
  'title':'예외는 const 참조(const lvalue reference)로 catch 한다',
  'bad': r"""try { f(); } catch (std::exception e) { ... }   // 값 catch — 슬라이싱""",
  'good': r"""try { f(); } catch (const std::exception& e) { ... }""",
  'why':'예외를 값으로 잡으면 파생 예외가 슬라이싱되어 정보를 잃는다. const 참조로 잡아 다형성을 보존한다.'},

 {'id':'Rule 18.4.1','cat':'Required · Decidable',
  'title':'예외를 던지지 않는 함수는 noexcept 로 표시하고 명세를 준수한다',
  'bad': r"""void f() noexcept { mayThrow(); }   // 예외 시 terminate""",
  'good': r"""void f() noexcept {
    try { mayThrow(); } catch (...) { /* 내부 처리 */ }
}""",
  'why':'noexcept 함수에서 예외가 빠져나가면 즉시 terminate된다. 명세대로 내부에서 처리하거나 명세를 수정한다.'},

 {'id':'Rule 18.5.1','cat':'Required · Decidable',
  'title':'소멸자나 해제 연산에서 예외가 빠져나가지 않게 한다',
  'bad': r"""~File() { flush(); }   // flush가 던지면 스택 풀기 중 terminate""",
  'good': r"""~File() noexcept {
    try { flush(); } catch (...) { /* 로깅 후 흡수 */ }
}""",
  'why':'스택 풀기 중 소멸자에서 예외가 탈출하면 std::terminate가 호출된다. 소멸자는 noexcept로 두고 내부 예외를 흡수한다.'},

 {'id':'Rule 19.0.2','cat':'Required · Decidable',
  'title':'함수형 매크로보다 inline 함수를 사용한다',
  'bad': r"""#define MAX(a,b) ((a) > (b) ? (a) : (b))
int y = MAX(i++, j);   // i 다중 평가""",
  'good': r"""template <typename T>
constexpr T imax(T a, T b) { return (a > b) ? a : b; }""",
  'why':'함수형 매크로는 타입 검사가 없고 인자를 다중 평가한다. inline/constexpr 함수가 같은 성능에 안전하다.'},

 {'id':'Rule 19.1.1','cat':'Required · Decidable',
  'title':'#include 에는 올바른 헤더명 형식만 사용한다',
  'bad': r"""#define HDR cfg.h
#include HDR          // 매크로 확장 — 형식 보장 안 됨""",
  'good': r"""#include "cfg.h"
/* 직접 헤더명 표기 */""",
  'why':'매크로 확장으로 만든 헤더명은 올바른 형식이 보장되지 않아 이식성 문제를 만든다. 직접 헤더명을 적는다.'},

 {'id':'Rule 19.3.4','cat':'Required · Decidable',
  'title':'함수형 매크로 매개변수는 괄호로 감싼다',
  'bad': r"""#define SCALE(x) x * 2
int r = SCALE(a + b);   // a + b*2""",
  'good': r"""#define SCALE(x) ((x) * 2)""",
  'why':'매크로 매개변수를 괄호로 보호하지 않으면 전개 시 우선순위가 깨진다. 각 매개변수와 전체를 괄호로 감싼다.'},

 {'id':'Rule 21.2.1','cat':'Required · Decidable',
  'title':'<cstdio> 의 표준 입출력 기능을 사용하지 않는다',
  'bad': r"""#include <cstdio>
std::printf("v=%d\n", v);""",
  'good': r"""std::cout << "v=" << v << '\n';   // 또는 검증된 I/O 계층""",
  'why':'cstdio의 포맷 입출력은 포맷 문자열 취약점·타입 불일치 위험이 있다. 타입 안전한 스트림이나 전용 I/O를 쓴다.'},

 {'id':'Rule 21.6.1','cat':'Advisory · Decidable',
  'title':'동적 메모리는 직접 new/delete 대신 스마트 포인터로 관리한다',
  'bad': r"""Widget* w = new Widget();
... delete w;          // 예외 경로 누수""",
  'good': r"""auto w = std::make_unique<Widget>();""",
  'why':'명시적 new/delete는 예외 발생 시 누수·이중 해제 위험이 있다. make_unique/make_shared로 수명을 자동 관리한다.'},

 {'id':'Rule 21.6.5','cat':'Required · Decidable',
  'title':'불완전(incomplete) 타입 포인터를 delete 하지 않는다',
  'bad': r"""struct Impl;
void f(Impl* p) { delete p; }   // 불완전 타입 — 소멸자 미호출""",
  'good': r"""// 완전 정의가 보이는 곳에서 삭제하거나 전용 deleter 사용
std::unique_ptr<Impl, void(*)(Impl*)> p{create(), &destroy};""",
  'why':'불완전 타입 포인터를 delete하면 소멸자 호출 여부가 미정의라 누수·손상이 난다. 완전 정의가 보이는 곳에서 삭제한다.'},

 {'id':'Rule 21.10.1','cat':'Required · Decidable',
  'title':'<csetjmp> 의 setjmp/longjmp 를 사용하지 않는다',
  'bad': r"""std::jmp_buf env;
if (setjmp(env)) recover();
... longjmp(env, 1);   // 소멸자 건너뜀""",
  'good': r"""try { work(); }
catch (const std::exception&) { recover(); }""",
  'why':'longjmp는 자동 객체 소멸자를 호출하지 않아 누수·객체 모델 위반을 일으킨다. 예외 처리를 사용한다.'},

 {'id':'Rule 21.10.2','cat':'Required · Decidable',
  'title':'<csignal> 의 시그널 처리를 사용하지 않는다',
  'bad': r"""std::signal(SIGINT, handler);   // 비동기·구현정의 위험""",
  'good': r"""while (!stop_requested()) { step(); }   // 협조적 폴링""",
  'why':'시그널 처리는 비동기·구현정의 동작이 많아 안전필수 C++에 부적합하다. 결정적 메커니즘을 쓴다.'},

 {'id':'Rule 22.3.1','cat':'Required · Decidable',
  'title':'errno 기반 오류 검출에 의존하지 않는다',
  'bad': r"""errno = 0;
double v = std::strtod(s, nullptr);
if (errno) { ... }    // 전역 errno 의존""",
  'good': r"""auto v = parse_double(s);   // optional/예외 반환
if (!v) { handle(); }""",
  'why':'전역 errno는 스레드·재진입 환경에서 오류 출처를 흐린다. 반환값·예외·optional로 오류를 명시 전달한다.'},

 {'id':'Rule 23.11.1','cat':'Advisory · Decidable',
  'title':'raw 포인터로 스마트 포인터를 생성해 소유권을 이중으로 만들지 않는다',
  'bad': r"""int* raw = new int(1);
std::shared_ptr<int> a(raw);
std::shared_ptr<int> b(raw);   // 별도 제어블록 — 이중 해제""",
  'good': r"""auto a = std::make_shared<int>(1);
auto b = a;           // 소유권 공유""",
  'why':'같은 raw 포인터로 독립 스마트 포인터를 만들면 제어 블록이 둘이라 이중 해제가 난다. make_shared와 복사로 소유권을 공유한다.'},

 {'id':'Rule 24.5.1','cat':'Required · Decidable',
  'title':'<cstring> 의 경계 없는 문자열 함수를 사용하지 않는다',
  'bad': r"""char d[8];
std::strcpy(d, src);   // 경계 미검사 — 오버플로우""",
  'good': r"""std::string d = src;   // 길이 자동 관리""",
  'why':'strcpy/strcat 등 경계 없는 함수는 버퍼 오버플로우의 주원인이다. std::string이나 경계 있는 연산을 쓴다.'},

 {'id':'Rule 25.5.1','cat':'Required · Decidable',
  'title':'<clocale>/전역 로케일 변경이 반환한 포인터를 보관해 재사용하지 않는다',
  'bad': r"""char* a = std::setlocale(LC_ALL, "C");
std::setlocale(LC_ALL, "en_US.UTF-8");
use(a);               // a 내용 덮어쓰임""",
  'good': r"""std::string saved = current_locale_name();   // 값 복사 보관""",
  'why':'로케일 변경 함수가 반환한 포인터는 다음 호출에서 덮어써질 수 있다. 필요한 값을 즉시 복사해 보관한다.'},

 {'id':'Rule 26.3.1','cat':'Required · Decidable',
  'title':'정렬/연관 컨테이너에 엄격 약순서를 만족하는 술어를 제공한다',
  'bad': r"""std::sort(v.begin(), v.end(),
          [](int a, int b){ return a <= b; });   // <= 위반""",
  'good': r"""std::sort(v.begin(), v.end(),
          [](int a, int b){ return a < b; });""",
  'why':'<= 같은 술어는 엄격 약순서를 위반해 정렬에서 미정의 동작을 일으킨다. 동치를 false로 두는 < 술어를 쓴다.'},

 {'id':'Rule 26.3.2','cat':'Required · Decidable',
  'title':'무효화된 반복자/참조를 사용하지 않는다',
  'bad': r"""auto it = v.begin();
v.push_back(9);       // 재할당 시 it 무효
use(*it);""",
  'good': r"""v.push_back(9);
auto it = v.begin();  // 수정 후 반복자 획득
use(*it);""",
  'why':'컨테이너 수정으로 무효화된 반복자·참조를 사용하면 미정의 동작이 된다. 수정 후 반복자를 다시 얻는다.'},

 {'id':'Rule 28.6.3','cat':'Required · Decidable',
  'title':'이동된(moved-from) 객체의 값에 의존하지 않는다',
  'bad': r"""std::string b = std::move(a);
std::cout << a;       // a는 유효하나 미지정 상태""",
  'good': r"""std::string b = std::move(a);
a = "reset";          // 재사용 전 명확히 재설정""",
  'why':'이동된 객체는 유효하나 값이 미지정 상태라 그 값에 의존하면 비결정적이다. 재사용 전에 명확한 값을 다시 대입한다.'},

 {'id':'Rule 28.6.4','cat':'Required · Decidable',
  'title':'전달 참조(forwarding reference)는 std::forward 로 전달한다',
  'bad': r"""template <typename T>
void wrap(T&& x) { sink(std::move(x)); }   // lvalue까지 이동""",
  'good': r"""template <typename T>
void wrap(T&& x) { sink(std::forward<T>(x)); }""",
  'why':'전달 참조에 std::move를 쓰면 lvalue 인자까지 이동시켜 호출자 객체를 훼손한다. std::forward로 값 범주를 보존한다.'},

 {'id':'Rule 30.0.1','cat':'Required · Decidable',
  'title':'C 표준 입출력(<cstdio>) 대신 C++ 스트림/검증된 I/O 를 사용한다',
  'bad': r"""char buf[16];
std::sprintf(buf, "%d", v);   // 경계 미검사""",
  'good': r"""std::string s = std::to_string(v);""",
  'why':'cstdio 함수는 경계·타입 안전성이 약해 오버플로우·포맷 취약점을 부른다. C++ 문자열/스트림으로 대체한다.'},

 {'id':'Rule 21.6.2','cat':'Required · Decidable',
  'title':'delete 의 형태(배열/단일)를 new 의 형태와 일치시킨다',
  'bad': r"""int* a = new int[10];
delete a;             // new[] 를 delete — 미정의""",
  'good': r"""auto a = std::make_unique<int[]>(10);""",
  'why':'new[]는 delete[]로 해제해야 하며 형태 불일치는 미정의 동작이다. 스마트 포인터/컨테이너로 올바른 해제를 자동화한다.'},
]
