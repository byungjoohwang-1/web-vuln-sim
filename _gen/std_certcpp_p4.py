# -*- coding: utf-8 -*-
"""SEI CERT C++ 규칙 (파트4: 공식 사이트 대조로 보강한 누락 규칙) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 cmu-sei.github.io 공식 목록 대조로 확인, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'DCL52-CPP','cat':'DCL · Rule · L1',
  'title':'참조(reference) 타입에 const/volatile 한정을 붙이지 않는다',
  'bad': r"""int x = 0;
int& const r = x;       // 참조는 본래 재바인딩 불가 — const 무의미·오류""",
  'good': r"""int x = 0;
int& r = x;             // 참조 자체엔 cv 한정 불필요
const int& cr = x;      // 가리키는 대상에 const""",
  'why':'참조는 이미 재바인딩이 불가능하므로 참조 자체에 const/volatile을 붙이는 것은 무의미하거나 오류다. 한정은 참조 대상 타입에 적용한다.'},

 {'id':'DCL55-CPP','cat':'DCL · Rule · L1',
  'title':'신뢰 경계 너머로 객체를 전달할 때 정보 유출을 막는다',
  'bad': r"""struct Msg { char tag; int val; };   // tag와 val 사이 패딩
Msg m; m.tag = 1; m.val = 2;
send(fd, &m, sizeof m);   // 패딩에 잔존 데이터 유출""",
  'good': r"""Msg m{};                  // 패딩 포함 0 초기화
m.tag = 1; m.val = 2;
send(fd, &m, sizeof m);""",
  'why':'구조체를 통째로 경계 밖에 보내면 초기화되지 않은 패딩 바이트의 잔존 데이터가 유출될 수 있다. 전체를 0으로 초기화한 뒤 채운다.'},

 {'id':'DCL56-CPP','cat':'DCL · Rule · L2',
  'title':'정적 객체 초기화 중 순환 의존을 만들지 않는다',
  'bad': r"""int a = b + 1;          // 다른 TU의 b에 의존
int b = a + 1;          // 초기화 순서 미정 — 순환""",
  'good': r"""int& a() { static int v = 1; return v; }   // 지연 초기화로 순환 차단""",
  'why':'정적 객체가 서로의 초기화에 의존하면 번역단위 간 초기화 순서가 정해지지 않아 미초기화 값을 읽는다. 지연 초기화(함수 지역 static)로 순서를 보장한다.'},

 {'id':'EXP56-CPP','cat':'EXP · Rule · L1',
  'title':'언어 연결(language linkage)이 일치하지 않는 함수를 통해 호출하지 않는다',
  'bad': r"""extern "C" void reg(void(*cb)());   // C 연결 콜백 기대
void cpp_cb();                       // C++ 연결
reg(cpp_cb);            // 연결 불일치""",
  'good': r"""extern "C" void c_cb();   // C 연결로 선언
reg(c_cb);""",
  'why':'함수 포인터의 언어 연결(extern "C" vs C++)이 호출 측 기대와 다르면 호출 규약이 어긋나 미정의 동작이 된다. 연결을 일치시킨다.'},

 {'id':'EXP58-CPP','cat':'EXP · Rule · L1',
  'title':'va_start 에 올바른 타입의 객체를 전달한다',
  'bad': r"""void f(std::string& last, ...) {
    va_list ap; va_start(ap, last);   // 참조형을 va_start 인자로 — 미정의""",
  'good': r"""void f(int last, ...) {
    va_list ap; va_start(ap, last);   // 마지막 고정 인자는 적합한 타입
}""",
  'why':'va_start의 마지막 고정 매개변수가 참조형·register·승격 대상 타입이면 미정의 동작이 된다. 가변인자 자체를 피하거나 적합한 타입을 사용한다.'},

 {'id':'EXP59-CPP','cat':'EXP · Rule · L1',
  'title':'offsetof 는 표준 레이아웃 타입의 유효한 멤버에만 사용한다',
  'bad': r"""struct NS { virtual void f(); int m; };   // 비표준 레이아웃
size_t o = offsetof(NS, m);   // 미정의""",
  'good': r"""struct SL { int a; int m; };   // 표준 레이아웃
size_t o = offsetof(SL, m);""",
  'why':'비표준 레이아웃 타입이나 정적/비멤버에 offsetof를 적용하면 미정의 동작이 된다. 표준 레이아웃 타입의 비정적 멤버에만 사용한다.'},

 {'id':'EXP60-CPP','cat':'EXP · Rule · L2',
  'title':'비표준 레이아웃(non-standard-layout) 객체를 실행 경계 너머로 전달하지 않는다',
  'bad': r"""struct NS { private: int a; public: int b; };  // 혼합 접근 — 레이아웃 미보장
extern "C" void api(NS*);   // C 경계로 전달""",
  'good': r"""struct SL { int a; int b; };   // 표준 레이아웃
extern "C" void api(SL*);""",
  'why':'비표준 레이아웃 타입은 메모리 배치가 보장되지 않아 C 등 다른 경계로 넘기면 잘못 해석된다. 경계를 넘는 타입은 표준 레이아웃으로 만든다.'},

 {'id':'EXP62-CPP','cat':'EXP · Rule · L2',
  'title':'객체 값에 속하지 않는 표현(representation) 비트에 접근하지 않는다',
  'bad': r"""struct S { char c; int v; };
auto* p = reinterpret_cast<unsigned char*>(&s);
hash(p, sizeof s);      // 패딩 비트까지 해시 — 불확정""",
  'good': r"""hash_combine(s.c, s.v);   // 값 멤버만 사용""",
  'why':'패딩 등 값에 속하지 않는 비트는 불확정이라 해시·비교에 사용하면 비결정적 결과를 낸다. 값 멤버만 사용한다.'},

 {'id':'ERR53-CPP','cat':'ERR · Rule · L1',
  'title':'생성자/소멸자 function-try-block 핸들러에서 멤버·기반을 참조하지 않는다',
  'bad': r"""S::S() try : member_(init()) { }
catch (...) { use(member_); }   // 핸들러 진입 시 member_ 이미 소멸""",
  'good': r"""S::S() try : member_(init()) { }
catch (...) { log("ctor failed"); throw; }   // 멤버 미참조""",
  'why':'생성자 function-try-block 핸들러에 도달하면 이미 구성된 멤버·기반은 소멸된 상태라 참조하면 미정의 동작이다. 핸들러에서 멤버를 접근하지 않는다.'},

 {'id':'ERR59-CPP','cat':'ERR · Rule · L1',
  'title':'예외를 실행 경계(언어 경계·스레드 등) 너머로 던지지 않는다',
  'bad': r"""extern "C" void api() { throw std::runtime_error("x"); }   // C 경계 밖으로""",
  'good': r"""extern "C" int api() {
    try { work(); return 0; } catch (...) { return -1; }
}""",
  'why':'C 인터페이스나 스레드 같은 실행 경계 밖으로 예외가 빠져나가면 정의되지 않은 동작·terminate가 발생한다. 경계 내부에서 포착해 오류 코드로 변환한다.'},

 {'id':'MEM55-CPP','cat':'MEM · Rule · L2',
  'title':'교체(replacement) operator new/delete 는 요구사항을 준수한다',
  'bad': r"""void* operator new(std::size_t n) {
    return std::malloc(n);   // 실패 시 nullptr 반환 — 표준 계약 위반""",
  'good': r"""void* operator new(std::size_t n) {
    if (void* p = std::malloc(n)) return p;
    throw std::bad_alloc();   // 계약대로 실패 시 예외
}""",
  'why':'교체 operator new는 실패 시 std::bad_alloc을 던지는 등 표준이 정한 계약을 지켜야 한다. 계약을 어기면 라이브러리 동작이 미정의가 된다.'},

 {'id':'OOP56-CPP','cat':'OOP · Rule · L2',
  'title':'교체한 핸들러(new_handler/terminate_handler 등)의 요구사항을 준수한다',
  'bad': r"""void my_new_handler() { /* 메모리 확보도 종료도 안 함 */ }
std::set_new_handler(my_new_handler);   // 무한 루프 유발""",
  'good': r"""void my_new_handler() {
    if (!free_some_memory()) { std::set_new_handler(nullptr); throw std::bad_alloc(); }
}""",
  'why':'new_handler는 메모리를 확보하거나, 핸들러를 해제하거나, 예외/종료로 끝나야 한다. 아무것도 하지 않으면 할당 재시도가 무한 반복된다.'},

 {'id':'CTR55-CPP','cat':'CTR · Rule · L2',
  'title':'반복자 덧셈 연산이 범위를 넘쳐 오버플로우하지 않게 한다',
  'bad': r"""auto it = v.begin() + offset;   // offset이 size보다 크면 범위 밖""",
  'good': r"""if (offset <= v.size()) {
    auto it = v.begin() + offset;
}""",
  'why':'반복자에 큰 정수를 더해 컨테이너 끝을 넘으면 무효 반복자가 되어 역참조 시 미정의 동작이 된다. 오프셋이 크기 이내인지 확인한다.'},

 {'id':'CON52-CPP','cat':'CON · Rule · L2',
  'title':'비트필드 접근 시 데이터 경쟁을 방지한다',
  'bad': r"""struct F { unsigned a:1; unsigned b:1; };
// T1: f.a=1   T2: f.b=1   — 같은 워드 동시 갱신""",
  'good': r"""std::mutex m;
{ std::lock_guard<std::mutex> g(m); f.a = 1; }""",
  'why':'인접 비트필드는 같은 메모리 워드를 공유해, 서로 다른 비트라도 동시 갱신 시 경쟁으로 손상된다. 잠금으로 보호한다.'},

 {'id':'CON55-CPP','cat':'CON · Rule · L2',
  'title':'조건 변수 사용 시 스레드 안전성과 진행성을 보존한다',
  'bad': r"""cv.notify_one();        // 잠금·술어 갱신 없이 통지 — 신호 유실""",
  'good': r"""{
    std::lock_guard<std::mutex> g(m);
    ready = true;
}
cv.notify_all();""",
  'why':'잠금 안에서 술어를 갱신하지 않고 통지하면 신호 유실·교착으로 진행성이 깨진다. 상태를 잠금 안에서 갱신하고 통지한다.'},

 {'id':'MSC53-CPP','cat':'MSC · Rule · L1',
  'title':'[[noreturn]] 으로 표시된 함수에서 반환하지 않는다',
  'bad': r"""[[noreturn]] void fatal() {
    if (canRecover) return;   // noreturn인데 반환 — 미정의""",
  'good': r"""[[noreturn]] void fatal() {
    std::abort();             // 항상 비반환
}""",
  'why':'[[noreturn]]으로 표시한 함수가 실제로 반환하면 미정의 동작이 된다. 모든 경로에서 종료·예외 등 비반환을 보장한다.'},
]
