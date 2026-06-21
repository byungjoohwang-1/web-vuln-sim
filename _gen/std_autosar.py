# -*- coding: utf-8 -*-
"""AUTOSAR C++14 대표 규칙 — 위반/준수 예제 (사내 교육용, 규범 원문 비복제·자체 작성)"""
RULES = [
 {'id':'A0-1-1','cat':'Required · Automated',
  'title':'계산했으나 사용하지 않는 값/요소를 두지 않는다',
  'bad': r"""int compute(int a, int b) {
  int sum = a + b;          // 계산했지만
  int product = a * b;      // product는 어디서도 쓰이지 않음 (dead value)
  return sum;
}""",
  'good': r"""int compute(int a, int b) {
  int sum = a + b;
  return sum;               // 필요한 값만 계산·반환
}""",
  'why':'사용되지 않는 값은 의도 누락이나 로직 오류의 신호이며 유지보수 시 혼란을 준다. 실제로 필요한 계산만 남겨 코드 의도를 명확히 한다.'},

 {'id':'A2-13-1','cat':'Required · Automated',
  'title':'표준에 정의된 이스케이프 시퀀스만 사용한다',
  'bad': r"""const char* path = "C:\temp\report";  // \t는 탭, \r은 CR로 잘못 해석됨
const char* msg  = "ratio is 50\% done"; // \%는 표준 이스케이프가 아님""",
  'good': r"""const char* path = "C:\\temp\\report"; // 역슬래시를 명시적으로 이스케이프
const char* msg  = "ratio is 50% done";  // %는 그대로 사용""",
  'why':'비표준/오타 이스케이프는 컴파일러마다 동작이 다르거나 의도치 않은 제어문자를 만든다. 정의된 이스케이프만 사용해 문자열 의미를 명확히 한다.'},

 {'id':'A5-0-1','cat':'Required · Non-automated',
  'title':'평가 순서가 정해지지 않은 식에 의존하지 않는다',
  'bad': r"""int i = 0;
int arr[3] = {0, 0, 0};
arr[i] = i++;                 // i 사용과 i++의 순서가 미정의
int v = f(i) + g(i++);        // f와 g 인자 평가 순서 미정의""",
  'good': r"""int i = 0;
int arr[3] = {0, 0, 0};
arr[i] = i;
++i;                          // 부작용을 별도 문장으로 분리
int a = f(i);
++i;
int v = a + g(i);""",
  'why':'C++에서 같은 객체를 한 식 안에서 읽고 수정하면 결과가 미정의일 수 있다. 부작용을 분리해 결정적 동작을 보장한다.'},

 {'id':'A5-1-1','cat':'Required · Automated',
  'title':'매직 리터럴 대신 의미 있는 명명 상수를 사용한다',
  'bad': r"""double area(double r) {
  return 3.14159 * r * r;     // 매직 넘버
}
bool ok(int retries) {
  return retries < 3;         // 3의 의미 불명확
}""",
  'good': r"""constexpr double kPi = 3.14159;
constexpr int kMaxRetries = 3;
double area(double r) { return kPi * r * r; }
bool ok(int retries) { return retries < kMaxRetries; }""",
  'why':'리터럴이 코드 곳곳에 흩어지면 의미 파악과 일괄 변경이 어렵다. 명명 상수로 의도를 드러내고 단일 지점에서 관리한다.'},

 {'id':'A5-2-2','cat':'Required · Automated',
  'title':'C 스타일 캐스트와 함수형 표기 캐스트를 사용하지 않는다',
  'bad': r"""void* p = getBuffer();
int* ip = (int*)p;            // C 스타일 캐스트: 위험성 은폐
double d = double(ip[0]);     // 함수형 표기 캐스트""",
  'good': r"""void* p = getBuffer();
int* ip = static_cast<int*>(p);
double d = static_cast<double>(ip[0]);""",
  'why':'C 스타일 캐스트는 const 제거·재해석 등 위험한 변환을 한 구문에 숨긴다. 명시적 C++ 캐스트로 의도와 위험성을 드러낸다.'},

 {'id':'A7-1-1','cat':'Required · Automated',
  'title':'변경되지 않는 변수는 const(또는 constexpr)로 선언한다',
  'bad': r"""void process(std::vector<int>& data) {
  int factor = 5;            // 이후 변경 없음
  for (auto& x : data) {
    x *= factor;
  }
}""",
  'good': r"""void process(std::vector<int>& data) {
  const int factor = 5;      // 불변임을 명시
  for (auto& x : data) {
    x *= factor;
  }
}""",
  'why':'불변 변수를 const로 표기하면 우발적 수정을 컴파일 시점에 막고 독자에게 불변 의도를 전달한다. 최적화에도 유리하다.'},

 {'id':'A7-1-7','cat':'Required · Automated',
  'title':'한 줄에 하나의 선언/정의만 둔다',
  'bad': r"""int* p, q;                  // p는 포인터, q는 int — 오해 유발
int a = 1, b = 2, c = 3;""",
  'good': r"""int* p;
int q;
int a = 1;
int b = 2;
int c = 3;""",
  'why':'한 줄 다중 선언은 포인터 결합 등에서 타입을 오해하게 만든다. 한 줄 한 선언으로 가독성과 정확성을 높인다.'},

 {'id':'A7-2-2','cat':'Required · Automated',
  'title':'열거형은 기반 타입(underlying type)을 명시한다',
  'bad': r"""enum class Color {
  Red, Green, Blue
};                            // 기반 타입 미지정""",
  'good': r"""enum class Color : std::uint8_t {
  Red, Green, Blue
};                            // 크기·표현 범위 명확""",
  'why':'기반 타입을 명시하면 열거형의 크기와 표현 범위가 플랫폼에 무관하게 확정된다. ABI 안정성과 직렬화 정확성에 중요하다.'},

 {'id':'A7-5-1','cat':'Required · Non-automated',
  'title':'인자의 수명보다 오래 사는 참조/포인터를 반환하지 않는다',
  'bad': r"""const int& pick(int a, int b) {
  int larger = (a > b) ? a : b;
  return larger;             // 지역 변수 참조 반환 (dangling)
}""",
  'good': r"""int pick(int a, int b) {
  int larger = (a > b) ? a : b;
  return larger;             // 값으로 반환
}""",
  'why':'지역 객체나 값 인자를 가리키는 참조를 반환하면 호출 후 댕글링 참조가 되어 미정의 동작을 일으킨다. 값으로 반환하거나 충분히 오래 사는 객체만 가리킨다.'},

 {'id':'A7-5-2','cat':'Required · Automated',
  'title':'함수는 자기 자신을 직접/간접으로 호출(재귀)하지 않는다',
  'bad': r"""std::uint64_t factorial(std::uint32_t n) {
  if (n <= 1) { return 1; }
  return n * factorial(n - 1); // 재귀: 스택 한계 예측 곤란
}""",
  'good': r"""std::uint64_t factorial(std::uint32_t n) {
  std::uint64_t result = 1;
  for (std::uint32_t i = 2; i <= n; ++i) {
    result *= i;             // 반복으로 변환
  }
  return result;
}""",
  'why':'재귀는 최악 스택 사용량을 정적으로 보장하기 어려워 안전필수 시스템에서 스택 오버플로 위험이 있다. 반복문으로 변환해 자원 사용을 결정적으로 만든다.'},

 {'id':'A8-4-7','cat':'Required · Automated',
  'title':'작고 trivially copyable한 타입은 값으로 전달한다',
  'bad': r"""struct Point { int x; int y; };
void move(const Point& p);    // 작은 trivial 타입을 참조로""",
  'good': r"""struct Point { int x; int y; };
void move(Point p);           // 값 전달이 더 단순·효율적""",
  'why':'작고 복사 비용이 낮은 타입은 값 전달이 참조보다 단순하고 별칭(aliasing) 문제도 없으며 최적화에 유리하다. 큰 타입만 const 참조로 받는다.'},

 {'id':'A12-1-1','cat':'Required · Automated',
  'title':'생성자는 모든 비정적 데이터 멤버를 명시적으로 초기화한다',
  'bad': r"""class Sensor {
public:
  Sensor() : id_(0) {}        // value_ 초기화 누락
private:
  int id_;
  double value_;
};""",
  'good': r"""class Sensor {
public:
  Sensor() : id_(0), value_(0.0) {} // 모든 멤버 초기화
private:
  int id_;
  double value_;
};""",
  'why':'초기화되지 않은 멤버는 부정확한 값으로 시작해 비결정적 버그를 만든다. 모든 멤버를 생성자에서 명시 초기화해 정의된 상태를 보장한다.'},

 {'id':'A12-4-1','cat':'Required · Automated',
  'title':'다형적으로 사용되는 기반 클래스는 가상 소멸자를 갖는다',
  'bad': r"""class Base {
public:
  ~Base() {}                  // 비가상 소멸자
};
class Derived : public Base { /* 자원 보유 */ };
Base* b = new Derived();
delete b;                     // Derived 소멸자 미호출 → 자원 누수""",
  'good': r"""class Base {
public:
  virtual ~Base() = default;  // 가상 소멸자
};
class Derived : public Base { /* 자원 보유 */ };
std::unique_ptr<Base> b = std::make_unique<Derived>();
// 스코프 종료 시 Derived 소멸자까지 정상 호출""",
  'why':'기반 포인터로 파생 객체를 delete할 때 소멸자가 비가상이면 파생 소멸자가 호출되지 않아 자원이 누수된다. 다형 기반 클래스는 가상 소멸자를 둔다.'},

 {'id':'A12-8-1','cat':'Required · Non-automated',
  'title':'이동/복사 생성자는 부작용 없이 복사·이동만 수행한다',
  'bad': r"""class Buffer {
public:
  Buffer(const Buffer& other) : data_(other.data_) {
    std::cout << "copied\n";  // 로깅 등 부작용
    ++globalCounter;          // 외부 상태 변경
  }
private:
  std::vector<int> data_;
};""",
  'good': r"""class Buffer {
public:
  Buffer(const Buffer& other) = default; // 순수 복사만
private:
  std::vector<int> data_;
};""",
  'why':'복사/이동 생성자에 부작용이 있으면 컴파일러의 복사 생략(copy elision) 여부에 따라 동작이 달라져 예측 불가능해진다. 멤버 복사·이동 외 동작을 넣지 않는다.'},

 {'id':'A15-1-2','cat':'Required · Automated',
  'title':'포인터를 예외로 throw하지 않는다',
  'bad': r"""void load() {
  throw new std::runtime_error("fail"); // 포인터 throw → 누가 delete?
}""",
  'good': r"""void load() {
  throw std::runtime_error("fail");     // 값(객체)으로 throw
}""",
  'why':'포인터를 throw하면 핸들러가 메모리 해제 책임을 떠안아 누수나 잘못된 해제가 발생한다. 예외 객체는 값으로 던지고 const 참조로 받는다.'},

 {'id':'A15-2-1','cat':'Required · Non-automated',
  'title':'생성자에서 예외 발생 시 이미 획득한 자원을 누수 없이 정리한다',
  'bad': r"""class Conn {
public:
  Conn() {
    a_ = new Resource();
    b_ = new Resource();      // 여기서 예외 시 a_ 누수
  }
private:
  Resource* a_;
  Resource* b_;
};""",
  'good': r"""class Conn {
public:
  Conn() : a_(std::make_unique<Resource>()),
           b_(std::make_unique<Resource>()) {}
private:
  std::unique_ptr<Resource> a_;
  std::unique_ptr<Resource> b_; // b_ 생성 실패 시 a_ 자동 해제
};""",
  'why':'생성자 본문 도중 예외가 나면 소멸자가 호출되지 않아 부분 획득 자원이 누수된다. RAII(스마트 포인터)로 각 자원의 정리를 자동화한다.'},

 {'id':'A15-4-2','cat':'Required · Automated',
  'title':'소멸자와 이동 연산은 noexcept로 선언한다',
  'bad': r"""class Widget {
public:
  ~Widget() { cleanup(); }            // noexcept 미지정
  Widget(Widget&& o) { steal(o); }    // 이동 생성자 noexcept 아님
};""",
  'good': r"""class Widget {
public:
  ~Widget() noexcept { cleanup(); }
  Widget(Widget&& o) noexcept { steal(o); }
};""",
  'why':'소멸자에서 예외가 나가면 스택 풀기 도중 std::terminate가 호출된다. 이동 연산이 noexcept가 아니면 컨테이너가 복사로 폴백해 성능이 떨어진다.'},

 {'id':'A15-5-1','cat':'Required · Automated',
  'title':'특수 멤버 함수(소멸자/이동 등)는 예외를 누출하지 않는다',
  'bad': r"""class FileGuard {
public:
  ~FileGuard() {
    if (!flush()) {
      throw std::runtime_error("flush failed"); // 소멸자에서 throw
    }
  }
};""",
  'good': r"""class FileGuard {
public:
  ~FileGuard() noexcept {
    if (!flush()) {
      logError("flush failed"); // 로깅으로 대체, 예외 미전파
    }
  }
};""",
  'why':'소멸자·이동 연산에서 예외가 빠져나가면 프로그램이 비정상 종료될 수 있다. 내부에서 처리하거나 기록하고 예외를 외부로 전파하지 않는다.'},

 {'id':'A18-1-1','cat':'Required · Automated',
  'title':'C 스타일 배열 대신 std::array/std::vector를 사용한다',
  'bad': r"""void sum() {
  int values[5] = {1, 2, 3, 4, 5}; // C 배열: 크기 정보 소실, 경계검사 없음
  int total = 0;
  for (int i = 0; i < 5; ++i) { total += values[i]; }
}""",
  'good': r"""void sum() {
  std::array<int, 5> values = {1, 2, 3, 4, 5};
  int total = 0;
  for (auto v : values) { total += v; } // 크기 보존, 안전한 순회
}""",
  'why':'C 배열은 함수 전달 시 포인터로 붕괴되어 크기 정보를 잃고 경계 검사가 불가능하다. std::array/std::vector는 크기를 유지하고 안전한 인터페이스를 제공한다.'},

 {'id':'A18-5-1','cat':'Required · Non-automated',
  'title':'malloc/free 대신 new/delete 또는 스마트 포인터를 사용한다',
  'bad': r"""Widget* w = static_cast<Widget*>(std::malloc(sizeof(Widget)));
// 생성자 미호출 — 객체가 초기화되지 않음
std::free(w);                 // 소멸자 미호출""",
  'good': r"""auto w = std::make_unique<Widget>(); // 생성자 호출 + 자동 해제
// 스코프 종료 시 소멸자 호출""",
  'why':'malloc/free는 생성자·소멸자를 호출하지 않아 C++ 객체 수명 규칙을 위반한다. 스마트 포인터로 생성·소멸과 해제를 일관되게 관리한다.'},

 {'id':'A18-5-2','cat':'Required · Automated',
  'title':'raw new/delete 대신 std::make_unique/make_shared를 사용한다',
  'bad': r"""Widget* w = new Widget();
configure(w);                 // 예외 시 누수 가능
delete w;                     // 수동 해제 — 누락/이중해제 위험""",
  'good': r"""auto w = std::make_unique<Widget>();
configure(w.get());           // 예외 안전 + 자동 해제""",
  'why':'수동 new/delete는 예외 경로나 조기 반환에서 해제 누락·이중 해제를 일으킨다. make_unique/make_shared는 소유권을 명확히 하고 예외 안전을 보장한다.'},

 {'id':'A18-9-1','cat':'Required · Automated',
  'title':'std::bind 대신 람다 표현식을 사용한다',
  'bad': r"""auto add5 = std::bind(std::plus<int>(), std::placeholders::_1, 5);
int r = add5(10);             // 가독성 낮고 오버로드/인라인화 불리""",
  'good': r"""auto add5 = [](int x) { return x + 5; };
int r = add5(10);             // 명확하고 인라인화 용이""",
  'why':'std::bind는 자리표시자 사용이 난해하고 타입 추론·인라인화를 방해한다. 람다는 의도가 명확하고 컴파일러 최적화에 유리하다.'},

 {'id':'A20-8-1','cat':'Required · Automated',
  'title':'공유 소유 포인터에는 std::shared_ptr를 사용한다',
  'bad': r"""Resource* shared = new Resource();
registerA(shared);
registerB(shared);            // 누가 언제 delete? 소유권 불명확
delete shared;""",
  'good': r"""auto shared = std::make_shared<Resource>();
registerA(shared);
registerB(shared);            // 참조 카운트로 안전한 공유 소유
// 마지막 소유자 소멸 시 자동 해제""",
  'why':'raw 포인터로 소유권을 공유하면 해제 시점과 책임이 불명확해 누수나 이중 해제가 발생한다. shared_ptr는 참조 카운팅으로 안전하게 공유 소유를 관리한다.'},

 {'id':'A20-8-5','cat':'Required · Automated',
  'title':'단독 소유에는 std::unique_ptr를 사용한다',
  'bad': r"""class Engine {
public:
  Engine() { parts_ = new Part[4]; }
  ~Engine() { delete[] parts_; } // 복사 시 이중 해제 위험
private:
  Part* parts_;
};""",
  'good': r"""class Engine {
public:
  Engine() : parts_(std::make_unique<Part[]>(4)) {}
private:
  std::unique_ptr<Part[]> parts_; // 단독 소유·자동 해제""",
  'why':'단독 소유를 raw 포인터로 다루면 복사·예외 경로에서 이중 해제나 누수가 생긴다. unique_ptr는 소유권 이전을 명시하고 해제를 자동화한다.'},

 {'id':'M0-1-1','cat':'Required · Automated',
  'title':'도달 불가능한(unreachable) 코드를 두지 않는다',
  'bad': r"""int classify(int x) {
  if (x > 0) {
    return 1;
    int unused = x;          // return 이후 — 절대 실행 안 됨
  }
  return 0;
}""",
  'good': r"""int classify(int x) {
  if (x > 0) {
    return 1;
  }
  return 0;
}""",
  'why':'도달 불가능한 코드는 논리 오류의 흔적이거나 잘못된 제어 흐름을 의미한다. 제거하여 의도를 명확히 하고 정적 분석 경고를 없앤다.'},

 {'id':'M0-1-3','cat':'Required · Automated',
  'title':'사용되지 않는 변수를 선언하지 않는다',
  'bad': r"""void run() {
  int counter = 0;           // 선언 후 한 번도 사용되지 않음
  doWork();
}""",
  'good': r"""void run() {
  doWork();                  // 불필요한 변수 제거
}""",
  'why':'사용되지 않는 변수는 누락된 로직이나 리팩터링 잔재일 수 있다. 제거하면 의도가 분명해지고 잠재적 버그를 드러낼 수 있다.'},

 {'id':'M0-3-2','cat':'Required · Non-automated',
  'title':'함수가 오류를 반환할 수 있으면 반환값을 검사한다',
  'bad': r"""void save(const Data& d) {
  writeToDisk(d);            // 반환 코드 무시 — 실패해도 진행
}""",
  'good': r"""void save(const Data& d) {
  const bool ok = writeToDisk(d);
  if (!ok) {
    handleWriteFailure();    // 실패를 명시적으로 처리
  }
}""",
  'why':'오류 코드를 무시하면 실패가 조용히 전파되어 데이터 손상이나 후속 미정의 동작을 일으킨다. 반환값을 검사해 실패를 명시적으로 처리한다.'},

 {'id':'M5-0-3','cat':'Required · Automated',
  'title':'복합식의 결과를 더 넓은 타입으로 암묵 변환하지 않는다',
  'bad': r"""std::uint16_t a = 50000;
std::uint16_t b = 50000;
std::uint32_t sum = a + b;   // a+b가 먼저 int로 평가 후 대입""",
  'good': r"""std::uint16_t a = 50000;
std::uint16_t b = 50000;
std::uint32_t sum = static_cast<std::uint32_t>(a) + b; // 의도된 폭으로 명시""",
  'why':'좁은 타입의 산술이 암묵적으로 넓은 타입에 대입되면 의도치 않은 승격·절단으로 오버플로 버그가 숨는다. 의도한 폭으로 명시적 캐스트한다.'},

 {'id':'M6-2-1','cat':'Required · Automated',
  'title':'대입 연산자를 불리언 문맥(조건식)에서 사용하지 않는다',
  'bad': r"""int x = readValue();
if (x = 0) {                 // == 의도였으나 = 사용 → 항상 거짓/대입
  reset();
}""",
  'good': r"""int x = readValue();
if (x == 0) {                // 비교 연산자
  reset();
}""",
  'why':'조건식의 대입은 비교(==) 오타인 경우가 많아 항상 같은 분기로 빠지는 버그를 만든다. 조건에는 비교 연산자만 사용한다.'},

 {'id':'M6-4-1','cat':'Required · Automated',
  'title':'if 다음 본문은 반드시 복합문(중괄호)으로 감싼다',
  'bad': r"""if (active)
  enable();
  log();                     // 들여쓰기는 if 안처럼 보이나 항상 실행됨""",
  'good': r"""if (active) {
  enable();
}
log();""",
  'why':'중괄호 없는 단문은 추가 문장이 끼어들 때 제어 범위를 오해하게 만든다(예: goto-fail 류 버그). 항상 블록으로 감싸 범위를 명확히 한다.'},

 {'id':'M6-4-2','cat':'Required · Automated',
  'title':'if ... else if 연쇄는 마지막에 else를 둔다',
  'bad': r"""if (level == 1) { lowPower(); }
else if (level == 2) { midPower(); }
else if (level == 3) { highPower(); }
// 예상 밖 level 값이 조용히 무시됨""",
  'good': r"""if (level == 1) { lowPower(); }
else if (level == 2) { midPower(); }
else if (level == 3) { highPower(); }
else { handleUnexpected(level); } // 모든 경우 처리""",
  'why':'else 누락은 예상하지 못한 값이 조용히 처리되지 않게 만든다. 마지막 else로 모든 경로를 명시해 방어적으로 작성한다.'},

 {'id':'M8-5-1','cat':'Required · Automated',
  'title':'변수는 선언 시점에 초기화한다',
  'bad': r"""int count;                  // 미초기화
double ratio;
count = compute();
// ratio는 사용 전 초기화 안 될 수 있음""",
  'good': r"""int count = compute();
double ratio = 0.0;         // 선언과 동시에 초기화""",
  'why':'미초기화 변수는 불확정 값을 가져 비결정적 동작과 보안 취약점을 유발한다. 선언과 동시에 의미 있는 값으로 초기화한다.'},

 {'id':'A2-7-3','cat':'Advisory · Non-automated',
  'title':'공개(public) 선언에는 문서화 주석을 단다',
  'bad': r"""class Pump {
public:
  void start(int rpm);       // 단위·범위·예외 조건 설명 없음
};""",
  'good': r"""class Pump {
public:
  /// 펌프를 지정한 회전수로 구동한다.
  /// @param rpm 목표 회전수(0~6000), 범위 밖이면 예외 발생
  void start(int rpm);
};""",
  'why':'문서화 없는 공개 API는 호출자가 단위·범위·예외 계약을 추측하게 만들어 오용을 부른다. 의도와 제약을 주석으로 명시해 안전한 사용을 돕는다.'},

 {'id':'A13-2-2','cat':'Required · Automated',
  'title':'이항 산술 연산자는 prvalue(값)를 반환한다',
  'bad': r"""class Money {
public:
  const Money& operator+(const Money& o) const; // 참조 반환 — 위험
};""",
  'good': r"""class Money {
public:
  Money operator+(const Money& o) const;        // 값 반환""",
  'why':'산술 연산자가 참조를 반환하면 임시 객체를 가리켜 댕글링이 되거나 연쇄식에서 의도치 않은 별칭을 만든다. 새 값(prvalue)을 반환한다.'},

 {'id':'A12-0-1','cat':'Required · Automated',
  'title':'특수 멤버 함수를 정의하면 관련 함수도 일관되게 정의한다(Rule of Five)',
  'bad': r"""class Handle {
public:
  ~Handle() { close(fd_); }  // 소멸자만 정의 → 복사 시 fd 이중 close
private:
  int fd_;
};""",
  'good': r"""class Handle {
public:
  ~Handle() { close(fd_); }
  Handle(const Handle&) = delete;            // 복사 금지
  Handle& operator=(const Handle&) = delete;
  Handle(Handle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
  Handle& operator=(Handle&&) noexcept;
private:
  int fd_;
};""",
  'why':'소멸자/복사/이동 중 하나만 정의하면 컴파일러가 만든 나머지가 자원 관리를 깨뜨려 이중 해제 등을 일으킨다. 다섯 가지 특수 멤버를 일관되게 정의(또는 삭제)한다.'},
]
