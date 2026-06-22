# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트3: INT·ERR·CON·FIO·MSC) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'INT50-CPP','cat':'INT · Rule · L1',
  'title':'열거형의 범위를 벗어난 값으로 캐스트하지 않는다',
  'bad': r"""enum class Color { Red, Green, Blue };  // 0,1,2
Color c = static_cast<Color>(7);        // 범위 밖 값""",
  'good': r"""int raw = read();
if (raw >= 0 && raw <= 2) {
    Color c = static_cast<Color>(raw);
}""",
  'why':'고정 열거 범위를 벗어난 정수를 enum으로 캐스트하면 미정의/미지정 값이 되어 switch 등에서 오동작한다. 캐스트 전에 유효 범위를 검사한다.'},

 {'id':'ERR50-CPP','cat':'ERR · Rule · L3',
  'title':'프로그램을 비정상적으로 종료(abort/terminate)시키지 않는다',
  'bad': r"""if (bad) { std::abort(); }   // 스택 풀기·소멸자 없이 종료""",
  'good': r"""if (bad) { throw std::runtime_error("bad state"); }
// 상위에서 catch하여 정상 정리 후 종료""",
  'why':'abort/terminate는 소멸자와 자원 정리를 건너뛰어 데이터 손상·누수를 남긴다. 예외를 던져 정상적인 스택 풀기로 정리하게 한다.'},

 {'id':'ERR51-CPP','cat':'ERR · Rule · L3',
  'title':'모든 예외를 처리한다',
  'bad': r"""int main() {
    run();              // 예외가 main 밖으로 — terminate
}""",
  'good': r"""int main() {
    try { run(); }
    catch (const std::exception& e) { log(e.what()); return 1; }
    catch (...) { log("unknown"); return 1; }
}""",
  'why':'잡히지 않은 예외는 std::terminate로 비정상 종료를 일으킨다. 최상위에서 모든 예외를 포착해 정의된 방식으로 처리한다.'},

 {'id':'ERR52-CPP','cat':'ERR · Rule · L1',
  'title':'setjmp/longjmp 를 사용하지 않는다',
  'bad': r"""std::jmp_buf env;
if (setjmp(env)) { recover(); }
... longjmp(env, 1);    // 소멸자 건너뜀""",
  'good': r"""try { work(); }
catch (const std::exception&) { recover(); }""",
  'why':'longjmp는 자동 객체 소멸자를 호출하지 않아 자원이 누수되고 C++ 객체 모델을 위반한다. 예외 처리 메커니즘을 사용한다.'},

 {'id':'ERR55-CPP','cat':'ERR · Rule · L1',
  'title':'예외 명세(noexcept 등)를 준수한다',
  'bad': r"""void f() noexcept {
    mayThrow();         // noexcept인데 예외 발생 → terminate""",
  'good': r"""void f() noexcept {
    try { mayThrow(); } catch (...) { /* 내부 처리 */ }
}""",
  'why':'noexcept로 선언한 함수에서 예외가 빠져나가면 즉시 terminate된다. 명세대로 예외를 내부에서 처리하거나 명세를 수정한다.'},

 {'id':'ERR56-CPP','cat':'ERR · Rule · L2',
  'title':'예외 안전성(exception safety)을 보장한다',
  'bad': r"""void S::set(T* n) {
    delete cur;
    cur = n->clone();   // clone이 던지면 cur는 댕글링""",
  'good': r"""void S::set(T* n) {
    T* tmp = n->clone();  // 먼저 성공시키고
    delete cur;           // 그 다음 교체
    cur = tmp;
}""",
  'why':'중간에 예외가 발생하면 객체가 깨진 상태로 남을 수 있다. 작업을 먼저 완성한 뒤 상태를 교체(strong guarantee)해 예외 안전을 확보한다.'},

 {'id':'ERR57-CPP','cat':'ERR · Rule · L2',
  'title':'예외 처리 중 자원을 누수하지 않는다',
  'bad': r"""void f() {
    int* p = new int[100];
    risky();            // 예외 시 p 누수
    delete[] p;
}""",
  'good': r"""void f() {
    auto p = std::make_unique<int[]>(100);
    risky();            // 예외에도 자동 해제
}""",
  'why':'raw 자원을 보유한 채 예외가 발생하면 해제 코드를 건너뛰어 누수가 난다. RAII로 모든 자원을 객체 수명에 묶는다.'},

 {'id':'ERR58-CPP','cat':'ERR · Rule · L3',
  'title':'main 시작 전에 던져지는 예외를 처리한다',
  'bad': r"""Config g_cfg = load_config();   // 정적 초기화 중 예외 → 처리 불가""",
  'good': r"""Config& cfg() {
    static Config c = load_config();   // 최초 사용 시 초기화·catch 가능
    return c;
}""",
  'why':'전역/정적 객체 생성자에서 던진 예외는 main 이전이라 일반적으로 포착할 수 없어 terminate된다. 지연 초기화로 제어 가능한 시점에서 처리한다.'},

 {'id':'ERR61-CPP','cat':'ERR · Rule · L3',
  'title':'예외는 lvalue 참조로 catch 한다',
  'bad': r"""try { f(); }
catch (std::exception e) { ... }   // 값 catch — 슬라이싱""",
  'good': r"""try { f(); }
catch (const std::exception& e) { ... }""",
  'why':'예외를 값으로 잡으면 파생 예외가 기반으로 슬라이싱되어 정보를 잃는다. const 참조로 잡아 다형성을 보존한다.'},

 {'id':'ERR62-CPP','cat':'ERR · Rule · L3',
  'title':'문자열을 숫자로 변환할 때 오류를 검출한다',
  'bad': r"""int n = std::atoi(s.c_str());   // 실패·범위 초과 구분 불가""",
  'good': r"""try {
    std::size_t pos;
    int n = std::stoi(s, &pos);
    if (pos != s.size()) { handle(); }
} catch (const std::exception&) { handle(); }""",
  'why':'atoi는 변환 실패와 정상 0을 구분하지 못한다. std::stoi와 예외/위치 검사로 변환 성공 여부를 명확히 판정한다.'},

 {'id':'CON50-CPP','cat':'CON · Rule · L2',
  'title':'잠긴 뮤텍스를 파괴하지 않는다',
  'bad': r"""std::mutex* m = new std::mutex;
m->lock();
delete m;               // 잠긴 채 파괴 — 미정의""",
  'good': r"""std::mutex m;
{
    std::lock_guard<std::mutex> g(m);
    work();
}                       // 스코프 종료 시 해제 후 정상 소멸""",
  'why':'잠긴 뮤텍스를 파괴하면 미정의 동작이 된다. RAII 잠금(lock_guard)으로 항상 먼저 해제되도록 보장한다.'},

 {'id':'CON51-CPP','cat':'CON · Rule · L2',
  'title':'예외 상황에서도 보유한 잠금을 해제한다',
  'bad': r"""m.lock();
risky();                // 예외 시 unlock 건너뜀 — 교착
m.unlock();""",
  'good': r"""std::lock_guard<std::mutex> g(m);
risky();                // 예외에도 스코프 탈출 시 해제""",
  'why':'명시적 lock/unlock 사이에서 예외가 나면 잠금이 영원히 유지되어 교착된다. lock_guard/unique_lock으로 예외 안전 해제를 보장한다.'},

 {'id':'CON53-CPP','cat':'CON · Rule · L2',
  'title':'정해진 순서로 잠가 교착을 방지한다',
  'bad': r"""// T1: lock(a); lock(b)  /  T2: lock(b); lock(a)
std::lock_guard<std::mutex> g1(b);
std::lock_guard<std::mutex> g2(a);""",
  'good': r"""std::scoped_lock lock(a, b);   // 교착 회피 알고리즘으로 동시 잠금""",
  'why':'스레드마다 잠금 순서가 다르면 교착이 발생한다. std::scoped_lock으로 여러 뮤텍스를 교착 없이 한 번에 잠근다.'},

 {'id':'CON54-CPP','cat':'CON · Rule · L2',
  'title':'가짜 깨어남이 가능한 대기는 루프로 감싼다',
  'bad': r"""if (!ready) { cv.wait(lk); }   // 가짜 깨어남 처리 못함""",
  'good': r"""cv.wait(lk, []{ return ready; });   // 술어 버전(내부 루프)""",
  'why':'조건 변수는 가짜 깨어남이 있어 if 검사만으로는 조건이 거짓인데 진행할 수 있다. 술어를 받는 wait나 while 루프로 재확인한다.'},

 {'id':'CON56-CPP','cat':'CON · Rule · L2',
  'title':'호출 스레드가 이미 보유한 비재귀 뮤텍스를 다시 잠그지 않는다',
  'bad': r"""void a() { std::lock_guard<std::mutex> g(m); b(); }
void b() { std::lock_guard<std::mutex> g(m); }   // 같은 m 재잠금 — 교착""",
  'good': r"""void a() { std::lock_guard<std::mutex> g(m); b_locked(); }
void b_locked() { /* 잠금 보유 가정, 다시 잠그지 않음 */ }""",
  'why':'비재귀 뮤텍스를 같은 스레드가 다시 잠그면 자기 교착이 발생한다. 내부 함수는 잠금을 다시 얻지 않도록 설계한다.'},

 {'id':'FIO50-CPP','cat':'FIO · Rule · L2',
  'title':'위치 지정 없이 입력과 출력을 번갈아 하지 않는다',
  'bad': r"""std::fstream f("d.bin");
f << "a";
f >> x;                 // 위치 지정 없이 출력→입력 전환 — 미정의""",
  'good': r"""std::fstream f("d.bin");
f << "a";
f.seekg(0);             // 명시적 위치 지정 후 입력
f >> x;""",
  'why':'갱신 모드 스트림에서 위치 지정 없이 읽기/쓰기를 전환하면 동작이 미정의다. 전환 사이에 seekg/seekp로 위치를 명시한다.'},

 {'id':'FIO51-CPP','cat':'FIO · Rule · L2',
  'title':'더 이상 필요 없는 파일은 닫는다',
  'bad': r"""std::FILE* f = std::fopen(p, "r");
read(f);                // fclose 누락""",
  'good': r"""std::ifstream f(p);     // RAII — 소멸 시 자동 close
read(f);""",
  'why':'파일 핸들을 닫지 않으면 디스크립터 누수로 자원이 고갈된다. RAII 스트림(ifstream/ofstream)으로 자동 닫힘을 보장한다.'},

 {'id':'MSC50-CPP','cat':'MSC · Rule · L3',
  'title':'std::rand() 로 보안용 난수를 만들지 않는다',
  'bad': r"""int token = std::rand();   // 예측 가능""",
  'good': r"""std::random_device rd;     // 또는 OS CSPRNG
std::uniform_int_distribution<int> dist(0, INT_MAX);
std::mt19937 gen(rd());
int v = dist(gen);         // 보안 토큰은 CSPRNG 사용""",
  'why':'std::rand()는 품질·예측성이 낮아 보안 요소에 부적합하다. 비보안 용도는 <random> 엔진, 보안 용도는 암호학적 난수를 쓴다.'},

 {'id':'MSC51-CPP','cat':'MSC · Rule · L3',
  'title':'난수 생성기를 적절히 시드한다',
  'bad': r"""std::mt19937 gen;          // 기본 시드(고정) — 매 실행 동일""",
  'good': r"""std::random_device rd;
std::mt19937 gen(rd());    // 엔트로피 소스로 시드""",
  'why':'고정 시드 엔진은 매 실행 같은 수열을 만들어 예측 가능하다. random_device 등 엔트로피 소스로 시드한다.'},

 {'id':'MSC52-CPP','cat':'MSC · Rule · L1',
  'title':'값을 반환하는 함수는 모든 종료 경로에서 값을 반환한다',
  'bad': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
}                          // x==0 경로 반환 없음""",
  'good': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}""",
  'why':'반환 없이 끝나는 비void 함수의 결과는 미정의 동작이다. 모든 경로에서 명시적으로 값을 반환한다.'},

 {'id':'MSC54-CPP','cat':'MSC · Rule · L1',
  'title':'시그널 핸들러는 일반(plain old) 함수여야 한다',
  'bad': r"""std::signal(SIGINT, [](int){ log("hit"); });  // 캡처 없는 람다라도 C++ 기능·비안전 호출 위험""",
  'good': r"""extern "C" void on_sigint(int) { g_flag = 1; }   // POF, async-safe 작업만
std::signal(SIGINT, on_sigint);""",
  'why':'시그널 핸들러에서 C++ 고유 기능(예외·비POD 호출)을 쓰면 미정의 동작이 된다. C 연결의 일반 함수로 작성하고 async-safe 작업만 한다.'},

 {'id':'ERR54-CPP','cat':'ERR · Rule · L2',
  'title':'catch 핸들러는 가장 파생된 것부터 기본 순으로 배치한다',
  'bad': r"""try { f(); }
catch (const std::exception& e) { ... }      // 먼저 — 파생도 여기서 잡힘
catch (const std::runtime_error& e) { ... }  // 도달 불가""",
  'good': r"""try { f(); }
catch (const std::runtime_error& e) { ... }  // 파생 먼저
catch (const std::exception& e) { ... }""",
  'why':'기반 클래스 핸들러를 먼저 두면 파생 예외가 거기서 잡혀 더 구체적인 핸들러가 도달 불가가 된다. 파생→기반 순으로 배치한다.'},

 {'id':'ERR60-CPP','cat':'ERR · Rule · L2',
  'title':'예외 객체는 nothrow 복사 생성 가능해야 한다',
  'bad': r"""struct MyErr { std::string big; };   // 복사 시 할당 → 던질 수 있음
throw MyErr{...};""",
  'good': r"""struct MyErr {
    const char* msg;            // 복사가 noexcept
    explicit MyErr(const char* m) : msg(m) {}
};""",
  'why':'예외 전파 중 예외 객체 복사가 또 던지면 terminate된다. 예외 타입은 복사 생성이 예외를 던지지 않도록(noexcept) 설계한다.'},
]
