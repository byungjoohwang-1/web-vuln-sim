# -*- coding: utf-8 -*-
"""AUTOSAR C++14 규칙 (파트3: A16~A27·M10~M18) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'A16-2-2','cat':'Required · Automated',
  'title':'사용되지 않는 #include 를 두지 않는다',
  'bad': r"""#include <vector>     // 이 파일에서 vector 미사용
#include <string>
std::string f();""",
  'good': r"""#include <string>
std::string f();""",
  'why':'쓰이지 않는 헤더 포함은 컴파일 시간을 늘리고 의존성을 흐린다. 실제 사용하는 헤더만 포함한다.'},

 {'id':'A16-7-1','cat':'Required · Automated',
  'title':'#pragma 지시문을 사용하지 않는다',
  'bad': r"""#pragma pack(1)       // 구현정의 동작""",
  'good': r"""// 표준 alignas/표준 메커니즘 사용
struct alignas(1) Packed { /* ... */ };""",
  'why':'#pragma는 구현정의라 이식성과 예측성을 해친다. 표준 언어 기능(alignas 등)으로 대체한다.'},

 {'id':'A17-1-1','cat':'Required · Non-automated',
  'title':'C 라이브러리 기능 사용을 제한하고 C++ 대안을 쓴다',
  'bad': r"""char buf[32];
sprintf(buf, "%d", v);   // C 라이브러리""",
  'good': r"""std::string s = std::to_string(v);""",
  'why':'C 라이브러리 함수는 타입 안전성·경계 검사가 약하다. 동등한 C++ 표준 라이브러리 기능을 우선 사용한다.'},

 {'id':'A18-0-2','cat':'Required · Automated',
  'title':'문자열→숫자 변환의 오류 상태를 검사한다',
  'bad': r"""int n = std::atoi(s.c_str());   // 실패 구분 불가""",
  'good': r"""try { int n = std::stoi(s); }
catch (const std::exception&) { handle(); }""",
  'why':'atoi는 변환 실패와 정상 0을 구분하지 못한다. 예외를 던지는 std::stoi 등으로 오류를 검출한다.'},

 {'id':'A18-1-1','cat':'Required · Automated',
  'title':'C 스타일 배열을 사용하지 않는다',
  'bad': r"""int a[10];            // 크기 정보 손실·경계 미검사""",
  'good': r"""std::array<int, 10> a{};   // 크기 보존·경계 검사 가능""",
  'why':'C 배열은 함수 전달 시 포인터로 붕괴해 크기 정보를 잃고 경계 검사를 어렵게 한다. std::array/std::vector를 쓴다.'},

 {'id':'A18-1-2','cat':'Required · Automated',
  'title':'std::vector<bool> 을 사용하지 않는다',
  'bad': r"""std::vector<bool> flags(8);   // 특수화 — 원소 참조가 비트프록시""",
  'good': r"""std::vector<std::uint8_t> flags(8);   // 또는 std::bitset""",
  'why':'std::vector<bool>은 비트 압축 특수화라 원소 참조·주소 의미가 일반 컨테이너와 달라 오류를 부른다. bitset이나 다른 타입을 쓴다.'},

 {'id':'A18-1-3','cat':'Required · Automated',
  'title':'std::auto_ptr 를 사용하지 않는다',
  'bad': r"""std::auto_ptr<int> p(new int);   // 복사 시 소유권 이전 — 폐기됨""",
  'good': r"""auto p = std::make_unique<int>();""",
  'why':'auto_ptr는 복사 시 소유권을 몰래 이전하는 위험한 의미를 가져 표준에서 제거되었다. unique_ptr를 사용한다.'},

 {'id':'A18-5-1','cat':'Required · Automated',
  'title':'malloc/calloc/realloc/free 를 사용하지 않는다(new/delete 사용)',
  'bad': r"""int* p = (int*)std::malloc(sizeof(int));   // 생성자 미호출
std::free(p);""",
  'good': r"""auto p = std::make_unique<int>();""",
  'why':'malloc/free는 생성자·소멸자를 호출하지 않아 C++ 객체 모델과 어긋나고 누수·미초기화를 부른다. new/delete 또는 스마트포인터를 쓴다.'},

 {'id':'A18-5-2','cat':'Required · Automated',
  'title':'raw new/delete 를 직접 쓰지 않는다(make_unique/make_shared 사용)',
  'bad': r"""Widget* w = new Widget();
... delete w;          // 예외 경로에서 누수""",
  'good': r"""auto w = std::make_unique<Widget>();""",
  'why':'명시적 new/delete는 예외 발생 시 누수와 이중 해제 위험이 있다. make_unique/make_shared로 소유권과 수명을 자동 관리한다.'},

 {'id':'A18-5-3','cat':'Required · Automated',
  'title':'delete 의 형태는 new 의 형태와 일치시킨다',
  'bad': r"""int* a = new int[10];
delete a;             // new[] 를 delete 로 — 미정의""",
  'good': r"""auto a = std::make_unique<int[]>(10);""",
  'why':'new[]는 delete[]로 해제해야 하며 형태 불일치는 미정의 동작이다. 스마트포인터/컨테이너로 올바른 해제를 자동화한다.'},

 {'id':'A18-9-1','cat':'Required · Automated',
  'title':'std::bind 를 사용하지 않는다(람다 사용)',
  'bad': r"""auto f = std::bind(&calc, _1, 10);   // 가독성·오버로드 문제""",
  'good': r"""auto f = [](int x){ return calc(x, 10); };""",
  'why':'std::bind는 가독성이 낮고 오버로드·완벽전달 처리가 까다롭다. 의도가 명확한 람다로 대체한다.'},

 {'id':'A18-9-2','cat':'Required · Automated',
  'title':'rvalue 는 std::move, 전달 참조는 std::forward 로 전달한다',
  'bad': r"""template <typename T>
void wrap(T&& x) { sink(std::move(x)); }   // 전달 참조에 move""",
  'good': r"""template <typename T>
void wrap(T&& x) { sink(std::forward<T>(x)); }""",
  'why':'전달 참조에 std::move를 쓰면 lvalue까지 이동시켜 호출자 객체를 훼손한다. 전달 참조는 std::forward로 값 범주를 보존한다.'},

 {'id':'A18-9-3','cat':'Required · Automated',
  'title':'const 객체에 std::move 를 적용하지 않는다',
  'bad': r"""const std::string s = "x";
auto t = std::move(s);   // const라 이동 불가 — 조용히 복사""",
  'good': r"""std::string s = "x";
auto t = std::move(s);""",
  'why':'const 객체에 move를 쓰면 이동이 아니라 복사로 폴백되어 의도한 성능 이점이 사라진다. 이동할 객체는 비-const로 둔다.'},

 {'id':'A20-8-1','cat':'Required · Automated',
  'title':'소유 포인터(owning pointer)는 스마트 포인터로 표현한다',
  'bad': r"""Widget* create();    // 소유권이 모호한 raw 반환""",
  'good': r"""std::unique_ptr<Widget> create();""",
  'why':'소유권을 raw 포인터로 전달하면 해제 책임이 불명확해 누수·이중 해제가 난다. 소유는 unique_ptr/shared_ptr로 명시한다.'},

 {'id':'A20-8-4','cat':'Required · Automated',
  'title':'공유가 필요 없으면 shared_ptr 대신 unique_ptr 를 쓴다',
  'bad': r"""std::shared_ptr<Widget> w = std::make_shared<Widget>();   // 단독 소유에 shared""",
  'good': r"""auto w = std::make_unique<Widget>();""",
  'why':'shared_ptr는 원자적 참조계수 비용이 있어 단독 소유에는 과하다. 공유가 실제로 필요할 때만 shared_ptr를 쓴다.'},

 {'id':'A20-8-5','cat':'Required · Automated',
  'title':'unique_ptr 는 std::make_unique 로 생성한다',
  'bad': r"""std::unique_ptr<Widget> w(new Widget());""",
  'good': r"""auto w = std::make_unique<Widget>();""",
  'why':'make_unique는 예외 안전하고 중복 타입 표기를 줄인다. unique_ptr 생성에 일관되게 사용한다.'},

 {'id':'A20-8-6','cat':'Required · Automated',
  'title':'shared_ptr 는 std::make_shared 로 생성한다',
  'bad': r"""std::shared_ptr<Widget> w(new Widget());   // 별도 제어블록 할당""",
  'good': r"""auto w = std::make_shared<Widget>();""",
  'why':'make_shared는 객체와 제어 블록을 한 번에 할당해 효율적이고 예외 안전하다. shared_ptr 생성에 사용한다.'},

 {'id':'A20-8-7','cat':'Advisory · Automated',
  'title':'순환 참조를 끊기 위해 weak_ptr 를 사용한다',
  'bad': r"""struct Node { std::shared_ptr<Node> parent; };   // 자식-부모 순환 — 누수""",
  'good': r"""struct Node { std::weak_ptr<Node> parent; };""",
  'why':'shared_ptr끼리 서로 가리키면 참조계수가 0이 되지 않아 메모리가 누수된다. 역방향(소유 아님) 링크는 weak_ptr로 둔다.'},

 {'id':'A21-8-1','cat':'Required · Automated',
  'title':'is*/to* 문자 함수 인자는 unsigned char 로 표현 가능해야 한다',
  'bad': r"""char c = get();
if (std::isalpha(c)) { ... }   // 음수 char — 미정의""",
  'good': r"""char c = get();
if (std::isalpha(static_cast<unsigned char>(c))) { ... }""",
  'why':'문자 분류 함수에 음수(EOF 외)를 넘기면 미정의 동작이 된다. unsigned char로 캐스트해 유효 범위를 보장한다.'},

 {'id':'A23-0-1','cat':'Required · Automated',
  'title':'무효화된(invalidated) 반복자를 사용하지 않는다',
  'bad': r"""for (auto it = v.begin(); it != v.end(); ++it) {
    if (*it == 0) v.erase(it);   // erase 후 it 무효""",
  'good': r"""for (auto it = v.begin(); it != v.end(); ) {
    if (*it == 0) it = v.erase(it);   // erase 반환값으로 갱신
    else ++it;
}""",
  'why':'erase/insert/재할당 후 기존 반복자는 무효화되어 사용 시 미정의 동작이 된다. 연산이 반환한 유효 반복자로 갱신한다.'},

 {'id':'A25-4-1','cat':'Required · Automated',
  'title':'정렬 술어는 엄격 약순서(strict weak ordering)를 만족해야 한다',
  'bad': r"""std::sort(v.begin(), v.end(),
          [](auto& a, auto& b){ return a.x <= b.x; });   // <= 위반""",
  'good': r"""std::sort(v.begin(), v.end(),
          [](auto& a, auto& b){ return a.x < b.x; });""",
  'why':'<= 같은 술어는 엄격 약순서를 위반해 정렬 알고리즘에서 미정의 동작(범위 초과)을 일으킨다. 동치를 false로 두는 < 술어를 쓴다.'},

 {'id':'A26-5-1','cat':'Required · Automated',
  'title':'의사난수는 std::rand 가 아닌 <random> 엔진으로 생성한다',
  'bad': r"""int r = std::rand() % 100;   // 품질·분포 불량""",
  'good': r"""std::mt19937 gen(seed);
std::uniform_int_distribution<int> dist(0, 99);
int r = dist(gen);""",
  'why':'std::rand는 분포 편향과 낮은 품질 문제가 있다. <random>의 엔진과 분포를 사용하고, 보안 용도는 암호학적 난수를 쓴다.'},

 {'id':'A27-0-1','cat':'Required · Non-automated',
  'title':'독립 컴포넌트로부터의 입력은 검증한다',
  'bad': r"""std::size_t n = read_size_from_network();
buf.resize(n);        // 외부 크기 미검증""",
  'good': r"""std::size_t n = read_size_from_network();
if (n <= kMaxBuf) { buf.resize(n); }
else { reject(); }""",
  'why':'외부(네트워크·파일·IPC) 입력을 검증 없이 크기·인덱스로 쓰면 자원 고갈·경계 초과로 이어진다. 신뢰 경계에서 입력을 검증한다.'},

 {'id':'A27-0-4','cat':'Required · Automated',
  'title':'C 스타일 문자열을 사용하지 않는다',
  'bad': r"""char name[32];
std::strcpy(name, input);   // 경계 미검사""",
  'good': r"""std::string name = input;   // 길이 자동 관리""",
  'why':'C 문자열은 널 종료·경계 관리를 수동으로 해야 해 오버플로우를 부른다. std::string으로 안전하게 다룬다.'},

 {'id':'M10-1-1','cat':'Advisory · Automated',
  'title':'비인터페이스 클래스를 둘 이상 상속하지 않는다',
  'bad': r"""class C : public Engine, public Logger { ... };   // 다중 구현 상속""",
  'good': r"""class C : public ILogger {   // 인터페이스 상속 + 구성
    Engine engine_;
};""",
  'why':'구현을 가진 다중 상속은 다이아몬드 문제와 모호성을 부른다. 인터페이스(순수 가상) 다중 상속과 멤버 구성(composition)으로 대체한다.'},

 {'id':'M10-1-2','cat':'Required · Automated',
  'title':'가상 기반 클래스는 추상 인터페이스(기반)로만 둔다',
  'bad': r"""class Base { int data_; };
class D : virtual public Base { ... };   // 데이터 가진 가상 기반""",
  'good': r"""class IBase { public: virtual ~IBase() = default; virtual void f() = 0; };
class D : virtual public IBase { void f() override; };""",
  'why':'데이터 멤버를 가진 가상 기반 클래스는 초기화·레이아웃을 복잡하게 만든다. 가상 기반은 데이터 없는 추상 인터페이스로 한정한다.'},

 {'id':'M12-1-1','cat':'Required · Automated',
  'title':'생성자/소멸자 안에서 객체의 동적 타입에 의존하지 않는다',
  'bad': r"""Base::Base() { dynamic_cast<Derived*>(this)->f(); }   // 생성 중 동적 타입은 Base""",
  'good': r"""// 생성 완료 후 별도 초기화 단계에서 파생 동작 호출
void start() { onReady(); }""",
  'why':'생성/소멸 중에는 동적 타입이 해당 클래스라 dynamic_cast·가상 디스패치가 파생으로 가지 않는다. 파생 동작은 생성 완료 후 수행한다.'},

 {'id':'M15-1-2','cat':'Required · Automated',
  'title':'NULL(널 포인터)을 throw 하지 않는다',
  'bad': r"""throw NULL;           // 정수 0으로 해석 — 핸들러 불일치""",
  'good': r"""throw std::runtime_error("null result");""",
  'why':'NULL을 던지면 포인터가 아닌 정수 0으로 해석되어 catch(T*)에 잡히지 않는 등 혼란을 부른다. 의미 있는 예외 객체를 던진다.'},

 {'id':'M15-3-4','cat':'Required · Automated',
  'title':'발생할 수 있는 모든 예외는 어딘가에서 catch 되어야 한다',
  'bad': r"""int main() { run(); }   // 예외가 잡히지 않으면 terminate""",
  'good': r"""int main() {
    try { run(); }
    catch (...) { log("unhandled"); return 1; }
}""",
  'why':'잡히지 않은 예외는 terminate로 비정상 종료된다. 최상위(main/태스크 진입점)에서 모든 예외를 포착한다.'},

 {'id':'M15-3-6','cat':'Required · Automated',
  'title':'catch 핸들러는 가장 파생된 것부터 배치한다',
  'bad': r"""try { f(); }
catch (const std::exception& e) { ... }
catch (const std::logic_error& e) { ... }   // 도달 불가""",
  'good': r"""try { f(); }
catch (const std::logic_error& e) { ... }
catch (const std::exception& e) { ... }""",
  'why':'기반 핸들러를 먼저 두면 파생 예외가 거기서 잡혀 구체적 핸들러가 도달 불가가 된다. 파생→기반 순으로 배치한다.'},

 {'id':'M15-3-7','cat':'Required · Automated',
  'title':'catch-all(...) 핸들러는 마지막에 둔다',
  'bad': r"""try { f(); }
catch (...) { ... }                       // 먼저 — 모든 예외 흡수
catch (const std::exception& e) { ... }   // 도달 불가""",
  'good': r"""try { f(); }
catch (const std::exception& e) { ... }
catch (...) { ... }""",
  'why':'catch(...)를 앞에 두면 모든 예외를 먼저 흡수해 구체 핸들러가 무력화된다. catch-all은 마지막에 배치한다.'},

 {'id':'M16-0-6','cat':'Required · Automated',
  'title':'함수형 매크로 매개변수는 괄호로 감싼다',
  'bad': r"""#define DBL(x) x + x
int r = DBL(a) * 2;   // a + a*2 로 전개""",
  'good': r"""#define DBL(x) ((x) + (x))
int r = DBL(a) * 2;""",
  'why':'매크로 매개변수를 괄호로 보호하지 않으면 전개 시 우선순위가 깨진다. 각 매개변수와 전체를 괄호로 감싼다.'},

 {'id':'M16-3-2','cat':'Advisory · Automated',
  'title':'전처리기 # 와 ## 연산자를 사용하지 않는다',
  'bad': r"""#define VAR(n) value_##n
int VAR(1) = 0;""",
  'good': r"""int value_1 = 0;     // 명시적 코드""",
  'why':'# / ## 는 평가 순서가 까다롭고 디버깅이 어려운 코드를 만든다. 명시적 코드로 대체한다.'},

 {'id':'M17-0-5','cat':'Required · Automated',
  'title':'setjmp / longjmp 를 사용하지 않는다',
  'bad': r"""std::jmp_buf env;
if (setjmp(env)) recover();
... longjmp(env, 1);""",
  'good': r"""try { work(); }
catch (const std::exception&) { recover(); }""",
  'why':'setjmp/longjmp는 소멸자를 건너뛰어 C++ 객체 모델을 위반하고 자원을 누수시킨다. 예외 처리를 사용한다.'},

 {'id':'M18-0-3','cat':'Required · Automated',
  'title':'<cstdlib> 의 abort/exit/getenv/system 을 사용하지 않는다',
  'bad': r"""std::system("ls");   // 셸 인젝션
std::exit(1);        // 소멸자 건너뜀""",
  'good': r"""// 셸 호출 없이 내부 API, 정상 반환 경로로 종료
return Status::Error;""",
  'why':'system은 셸 인젝션, exit/abort는 자원 정리를 건너뛰는 위험이 있다. 내부 API와 예외/반환으로 대체한다.'},

 {'id':'M18-0-5','cat':'Required · Automated',
  'title':'<cstring> 의 경계 없는(unbounded) 함수를 사용하지 않는다',
  'bad': r"""char d[8];
std::strcpy(d, src);   // 경계 미검사 — 오버플로우""",
  'good': r"""std::string d = src;   // 또는 경계 있는 복사""",
  'why':'strcpy/strcat/strlen 등 경계 없는 C 문자열 함수는 버퍼 오버플로우의 주원인이다. std::string이나 경계 있는 연산을 쓴다.'},

 {'id':'M18-7-1','cat':'Required · Automated',
  'title':'<csignal> 의 시그널 처리를 사용하지 않는다',
  'bad': r"""std::signal(SIGINT, handler);   // 비동기·구현정의 위험""",
  'good': r"""// 협조적 폴링/이벤트 루프로 종료 요청 처리
while (!stop_requested()) { step(); }""",
  'why':'시그널 처리는 비동기·구현정의 동작이 많아 안전필수 C++에 부적합하다. 결정적 이벤트 메커니즘으로 대체한다.'},

 {'id':'M19-3-1','cat':'Required · Automated',
  'title':'errno 를 사용하지 않는다',
  'bad': r"""errno = 0;
double v = std::strtod(s, nullptr);
if (errno) { ... }    // 전역 errno 의존""",
  'good': r"""// 오류를 반환/예외로 전달하는 인터페이스 사용
auto r = parse_double(s);   // std::optional 등
if (!r) { handle(); }""",
  'why':'전역 errno는 스레드·재진입 환경에서 오류 출처를 흐리고 검사 누락을 부른다. 반환값·예외·optional로 오류를 명시 전달한다.'},
]
