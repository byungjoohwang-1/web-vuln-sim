# -*- coding: utf-8 -*-
"""MISRA C++:2023 규칙 (파트1: 섹션 0~8) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'Rule 0.0.1','cat':'Required · Decidable',
  'title':'함수에 도달 불가능한 코드를 두지 않는다',
  'bad': r"""int f(int x) {
    return x;
    log("unreached");   // 도달 불가""",
  'good': r"""int f(int x) {
    log("before");
    return x;
}""",
  'why':'return/throw 이후의 도달 불가 코드는 논리 오류의 신호다. 제거하거나 흐름을 바로잡는다.'},

 {'id':'Rule 0.1.1','cat':'Advisory · Decidable',
  'title':'계산된 값이 사용되지 않게 두지 않는다(useless value)',
  'bad': r"""int n = compute();
n = 0;                // compute() 결과를 쓰지 않고 덮어씀""",
  'good': r"""int n = 0;""",
  'why':'읽히기 전에 덮어쓰이는 값은 죽은 계산이며 대입 누락 등 오류의 신호다. 사용되지 않는 계산을 제거한다.'},

 {'id':'Rule 0.1.2','cat':'Advisory · Decidable',
  'title':'사용되지 않는 변수/멤버를 두지 않는다',
  'bad': r"""void f() {
    int tmp = read();   // 어디서도 사용 안 됨
    do_other();
}""",
  'good': r"""void f() {
    do_other();
}""",
  'why':'사용되지 않는 객체는 누락된 로직을 의심하게 하고 코드를 어지럽힌다. 미사용 변수는 제거한다.'},

 {'id':'Rule 0.2.2','cat':'Required · Decidable',
  'title':'한 객체에 같은 값을 중복으로 대입하지 않는다(중복 부작용)',
  'bad': r"""x = compute();
x = compute();        // 동일 호출 중복 — 의도 불명""",
  'good': r"""x = compute();""",
  'why':'동일 부작용을 중복 수행하면 의도를 알 수 없고 성능·정확성 문제를 부른다. 중복 대입을 제거한다.'},

 {'id':'Rule 4.6.1','cat':'Advisory · Undecidable',
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'bad': r"""int i = 0;
f(i++, i++);          // 인자 평가 순서 미명세""",
  'good': r"""int a = i++;
int b = i++;
f(a, b);""",
  'why':'한 식에서 같은 객체를 여러 번 수정하면 평가 순서에 따라 결과가 달라진다. 부작용을 분리해 순서를 확정한다.'},

 {'id':'Rule 5.13.1','cat':'Required · Decidable',
  'title':'표준에 정의된 이스케이프 시퀀스만 사용한다',
  'bad': r"""const char* s = "a\qb";   // \q 비표준 이스케이프""",
  'good': r"""const char* s = "a\tb";""",
  'why':'표준에 없는 이스케이프 시퀀스는 미정의 동작이거나 구현마다 다르다. 정의된 이스케이프만 사용한다.'},

 {'id':'Rule 5.13.3','cat':'Required · Decidable',
  'title':'8진(octal) 상수와 8진 이스케이프 사용을 피한다',
  'bad': r"""int perm = 0755;      // 8진 상수 — 오독 유발""",
  'good': r"""int perm = 0x1ED;     // 또는 493""",
  'why':'선행 0의 8진 상수는 010이 8이 되는 등 의도와 다른 값으로 읽히기 쉽다. 10진/16진 표기를 사용한다.'},

 {'id':'Rule 5.13.5','cat':'Required · Decidable',
  'title':'정수 리터럴의 접미사는 대문자로 표기한다',
  'bad': r"""long v = 100l;        // 소문자 l — 1과 혼동""",
  'good': r"""long v = 100L;""",
  'why':'소문자 l 접미사는 숫자 1과 시각적으로 구분되지 않는다. 항상 대문자 L/U를 사용한다.'},

 {'id':'Rule 6.0.1','cat':'Required · Decidable',
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지 않게 한다',
  'bad': r"""int count = 0;
void f() { int count = 5; use(count); }   // 외부 가림""",
  'good': r"""int g_count = 0;
void f() { int local = 5; use(local); }""",
  'why':'바깥 식별자를 같은 이름으로 가리면 잘못된 변수를 참조하는 결함을 부른다. 내부 식별자는 다른 이름을 쓴다.'},

 {'id':'Rule 6.4.1','cat':'Required · Decidable',
  'title':'식별자는 가능한 가장 좁은 범위에서 선언한다',
  'bad': r"""int tmp;
for (int i = 0; i < n; ++i) { tmp = a[i]; use(tmp); }   // tmp 범위 과대""",
  'good': r"""for (int i = 0; i < n; ++i) {
    int tmp = a[i];
    use(tmp);
}""",
  'why':'필요 이상으로 넓은 범위의 변수는 오용·상태 누출 위험을 키운다. 사용 지점에 가장 가까운 범위에 선언한다.'},

 {'id':'Rule 6.7.1','cat':'Required · Decidable',
  'title':'지역 정적(local static) 객체를 신중히 사용한다(스레드 안전·초기화 순서)',
  'bad': r"""int& counter() {
    static int n = init();   // 스레드 경합·초기화 순서 주의 필요
    return n;
}""",
  'good': r"""// 명시적 수명·동기화로 관리하거나 의존성을 주입
struct Counter { int n = 0; };""",
  'why':'함수 지역 정적 객체는 초기화 시점·스레드 안전·전역 상태 공유 문제를 숨긴다. 수명과 동기화를 명시적으로 설계한다.'},

 {'id':'Rule 6.8.2','cat':'Mandatory · Undecidable',
  'title':'수명이 끝난 객체에 대한 참조/포인터를 반환·사용하지 않는다',
  'bad': r"""const int& f() {
    int local = 42;
    return local;     // 지역 객체 참조 반환 — 댕글링""",
  'good': r"""int f() {
    int local = 42;
    return local;     // 값 반환
}""",
  'why':'지역 객체의 참조/주소는 함수 종료 시 무효가 되어 댕글링 접근을 유발한다. 값으로 반환하거나 수명이 보장된 객체를 가리킨다.'},

 {'id':'Rule 7.0.2','cat':'Required · Decidable',
  'title':'조건 문맥에는 본질적으로 bool 인 표현식을 사용한다',
  'bad': r"""int* p = find();
if (p) { use(p); }    // 포인터를 bool처럼""",
  'good': r"""int* p = find();
if (p != nullptr) { use(p); }""",
  'why':'포인터·정수를 그대로 조건에 쓰면 의도가 모호하고 0 비교 누락을 부른다. 명시적 비교로 bool 표현식을 만든다.'},

 {'id':'Rule 7.0.5','cat':'Required · Decidable',
  'title':'암시적 정수 변환이 값을 손실하거나 부호를 바꾸지 않게 한다',
  'bad': r"""std::uint8_t b = wide;   // 8비트 초과분 절단""",
  'good': r"""if (wide <= 0xFF) {
    auto b = static_cast<std::uint8_t>(wide);
}""",
  'why':'넓은 값을 좁은 타입으로 암시 변환하면 절단·부호 변화로 손실이 생긴다. 범위 검사 후 명시적으로 변환한다.'},

 {'id':'Rule 7.11.1','cat':'Required · Decidable',
  'title':'널 포인터 상수로는 nullptr 만 사용한다',
  'bad': r"""int* p = 0;           // 또는 NULL""",
  'good': r"""int* p = nullptr;""",
  'why':'0/NULL은 정수·포인터 문맥이 섞여 오버로드 해석 오류를 부른다. 타입 안전한 nullptr만 사용한다.'},

 {'id':'Rule 8.0.1','cat':'Required · Decidable',
  'title':'연산자 우선순위는 괄호로 명시한다',
  'bad': r"""int r = a + b << c & d;   // 우선순위 혼동""",
  'good': r"""int r = ((a + b) << c) & d;""",
  'why':'시프트·비트·산술이 섞인 식은 우선순위를 오해하기 쉽다. 괄호로 평가 순서를 명확히 한다.'},

 {'id':'Rule 8.2.2','cat':'Required · Decidable',
  'title':'C 스타일 캐스트를 사용하지 않는다',
  'bad': r"""double d = 3.9;
int n = (int)d;""",
  'good': r"""int n = static_cast<int>(d);""",
  'why':'C 스타일 캐스트는 어떤 변환인지 드러나지 않아 위험을 숨긴다. 의도가 명확한 C++ 캐스트를 쓴다.'},

 {'id':'Rule 8.2.3','cat':'Required · Decidable',
  'title':'캐스트로 const/volatile 한정을 제거하지 않는다',
  'bad': r"""void g(const int& v) {
    const_cast<int&>(v) = 9;   // const 대상 수정 — 미정의""",
  'good': r"""void g(int& v) { v = 9; }""",
  'why':'const_cast로 한정을 떼고 실제 const 객체를 수정하면 미정의 동작이다. 수정이 필요하면 비-const 인터페이스를 쓴다.'},

 {'id':'Rule 8.2.5','cat':'Required · Decidable',
  'title':'reinterpret_cast 를 사용하지 않는다',
  'bad': r"""float f = 1.0f;
auto u = *reinterpret_cast<std::uint32_t*>(&f);   // 별칭 위반""",
  'good': r"""std::uint32_t u;
std::memcpy(&u, &f, sizeof u);""",
  'why':'reinterpret_cast는 엄격 별칭·정렬 규칙을 어겨 미정의 동작을 부른다. 비트 재해석은 memcpy/bit_cast로 한다.'},

 {'id':'Rule 8.2.10','cat':'Required · Decidable',
  'title':'함수를 정의되지 않은 시그니처로 호출하지 않는다',
  'bad': r"""void (*fp)() = reinterpret_cast<void(*)()>(&g);
fp();                 // 다른 시그니처로 호출""",
  'good': r"""void (*fp)(int) = &g;   // 일치하는 시그니처
fp(3);""",
  'why':'함수를 실제 정의와 다른 시그니처로 호출하면 인자 전달이 어긋나 미정의 동작이 된다. 정확한 타입의 함수 포인터로 호출한다.'},

 {'id':'Rule 8.3.1','cat':'Required · Decidable',
  'title':'시프트 횟수는 0 이상이며 피연산자 비트폭 미만이어야 한다',
  'bad': r"""std::uint32_t v = 1;
auto r = v << 40;     // 32비트를 40 시프트 — 미정의""",
  'good': r"""if (n < 32u) { auto r = v << n; }""",
  'why':'피연산자 비트폭 이상 또는 음수로 시프트하면 결과가 미정의다. 시프트량을 유효 범위로 보장한다.'},

 {'id':'Rule 8.7.1','cat':'Required · Undecidable',
  'title':'포인터 산술 결과는 같은 배열의 범위 안을 가리켜야 한다',
  'bad': r"""int a[10];
int* p = a + 12;      // 범위 밖
*p = 0;""",
  'good': r"""int a[10];
if (i >= 0 && i < 10) { a[i] = 0; }""",
  'why':'배열 경계를 벗어난 포인터를 역참조하면 메모리 손상·미정의 동작이 된다. 인덱스를 검증해 범위 내에서만 접근한다.'},

 {'id':'Rule 8.18.1','cat':'Mandatory · Undecidable',
  'title':'겹치는(overlapping) 객체에 대입하지 않는다',
  'bad': r"""std::memcpy(buf, buf + 1, n);   // 영역 중첩 — 미정의""",
  'good': r"""std::memmove(buf, buf + 1, n);  // 중첩 허용""",
  'why':'중첩된 메모리 영역에 memcpy/대입을 하면 미정의 동작이 된다. 중첩이 가능하면 memmove를 사용한다.'},

 {'id':'Rule 8.19.1','cat':'Advisory · Decidable',
  'title':'쉼표(,) 연산자를 사용하지 않는다',
  'bad': r"""x = (a(), b());       // 부작용이 한 식에 숨음""",
  'good': r"""a();
x = b();""",
  'why':'쉼표 연산자는 부작용과 평가 순서를 한 식에 숨겨 가독성·분석을 해친다. 문장을 분리한다.'},

 {'id':'Rule 8.7.2','cat':'Required · Undecidable',
  'title':'관계 연산은 같은 배열/객체를 가리키는 포인터끼리만 한다',
  'bad': r"""if (&x[0] < &y[0]) { ... }   // 다른 배열 포인터 비교 — 미정의""",
  'good': r"""if (ix < iy) { ... }   // 인덱스로 비교""",
  'why':'서로 다른 객체를 가리키는 포인터의 대소 비교는 미정의다. 같은 배열 내 포인터이거나 인덱스로 비교한다.'},
]
