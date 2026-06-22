# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트2: Rule 10~17) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'Rule 10.1','cat':'Required · Decidable · Rule',
  'title':'피연산자는 부적절한 essential type으로 사용하지 않는다',
  'bad': r"""unsigned int flags = 0x0Fu;
if (flags & 1) { ... }      /* bool 문맥에 essentially unsigned 사용 */
char c = 'A';
int x = c << 2;             /* char 를 시프트 피연산자로 */""",
  'good': r"""unsigned int flags = 0x0Fu;
if ((flags & 1u) != 0u) { ... }
unsigned int uc = (unsigned int)'A';
unsigned int x = uc << 2u;""",
  'why':'essential type 범주에 맞지 않는 연산(불리언 문맥의 산술형, 시프트의 부호형 등)은 암묵 변환으로 의도와 다른 결과를 낸다. 연산에 적합한 타입으로 명시한다.'},

 {'id':'Rule 10.2','cat':'Required · Decidable · Rule',
  'title':'문자형(char) 값은 덧셈/뺄셈 외 산술에 사용하지 않는다',
  'bad': r"""char a = 'A';
char b = a * 2;     /* char 에 곱셈 — 의미 불명확 */""",
  'good': r"""char a = 'A';
int  code = (int)a;
int  b = code * 2;  /* 정수형으로 변환 후 산술 */""",
  'why':'plain char에 곱셈·시프트 등을 적용하면 부호·폭이 구현정의라 결과가 흔들린다. 문자에서 산술이 필요하면 명시적으로 정수형으로 변환한다.'},

 {'id':'Rule 10.3','cat':'Required · Decidable · Rule',
  'title':'표현식 값을 더 좁거나 다른 essential type 범주로 대입하지 않는다',
  'bad': r"""int  big = 300;
unsigned char b = big;   /* 300 → 8비트 절단(44) */""",
  'good': r"""int big = 300;
if (big >= 0 && big <= 255) {
    unsigned char b = (unsigned char)big;
}""",
  'why':'넓은 타입을 좁은 타입에 암묵 대입하면 값이 절단되거나 부호가 바뀐다. 범위를 검사하고 명시적 캐스트로 의도를 드러낸다.'},

 {'id':'Rule 10.4','cat':'Required · Decidable · Rule',
  'title':'산술 연산의 두 피연산자는 같은 essential type 범주여야 한다',
  'bad': r"""unsigned int u = 1u;
int s = -2;
if (u + s > 0u) { ... }   /* signed/unsigned 혼합 — s가 큰 양수로 */""",
  'good': r"""int s = -2;
int u = 1;
if (u + s > 0) { ... }     /* 부호 범주를 통일 */""",
  'why':'부호 있는/없는 타입을 섞으면 일반 산술 변환으로 음수가 거대한 양수가 되는 등 직관과 다른 결과가 나온다. 피연산자 타입 범주를 통일한다.'},

 {'id':'Rule 10.6','cat':'Required · Decidable · Rule',
  'title':'복합 표현식 결과를 더 넓은 essential type에 대입하지 않는다',
  'bad': r"""uint16_t a = 50000u, b = 50000u;
uint32_t s = a + b;   /* a+b는 16비트로 계산 후 확장 — 래핑 */""",
  'good': r"""uint16_t a = 50000u, b = 50000u;
uint32_t s = (uint32_t)a + (uint32_t)b;  /* 넓혀서 계산 */""",
  'why':'좁은 타입끼리 계산한 뒤 넓은 타입에 대입하면 계산이 좁은 폭에서 일어나 오버플로우가 숨는다. 연산 전에 피연산자를 목표 폭으로 넓힌다.'},

 {'id':'Rule 10.8','cat':'Required · Decidable · Rule',
  'title':'복합 표현식 값을 다른/넓은 essential type으로 캐스트하지 않는다',
  'bad': r"""uint16_t x = 40000u, y = 40000u;
uint32_t z = (uint32_t)(x + y);  /* 16비트 결과를 캐스트 — 이미 래핑됨 */""",
  'good': r"""uint16_t x = 40000u, y = 40000u;
uint32_t z = (uint32_t)x + (uint32_t)y;""",
  'why':'좁은 폭에서 평가된 복합 표현식을 사후 캐스트해봐야 이미 손실된 비트는 복원되지 않는다. 캐스트는 피연산자 단계에서 적용한다.'},

 {'id':'Rule 11.1','cat':'Required · Decidable · Rule',
  'title':'함수 포인터를 다른 타입으로 변환하지 않는다',
  'bad': r"""typedef void (*fn_t)(void);
fn_t f = (fn_t)some_data_ptr;   /* 데이터 포인터를 함수 포인터로 */
f();""",
  'good': r"""typedef void (*fn_t)(void);
extern void real_handler(void);
fn_t f = real_handler;          /* 호환되는 함수만 대입 */
f();""",
  'why':'함수 포인터와 다른 포인터 간 변환은 호출 규약·표현이 달라 미정의 동작과 충돌을 일으킨다. 호환되는 함수 타입끼리만 대입한다.'},

 {'id':'Rule 11.3','cat':'Required · Decidable · Rule',
  'title':'서로 다른 객체 타입을 가리키는 포인터 간 캐스트를 하지 않는다',
  'bad': r"""uint8_t buf[4];
uint32_t *p = (uint32_t *)buf;   /* 정렬·엄격별칭 위반 가능 */
*p = 0x01020304u;""",
  'good': r"""uint8_t buf[4];
uint32_t v = 0x01020304u;
memcpy(buf, &v, sizeof v);       /* 별칭·정렬 안전 */""",
  'why':'다른 객체 타입으로의 포인터 캐스트는 정렬 위반과 엄격 별칭 규칙 위반으로 미정의 동작을 부른다. 바이트 단위 복사(memcpy)로 안전하게 재해석한다.'},

 {'id':'Rule 11.4','cat':'Advisory · Decidable · Rule',
  'title':'정수와 객체 포인터 사이를 변환하지 않는다',
  'bad': r"""uint32_t addr = 0x4000u;
uint8_t *reg = (uint8_t *)addr;   /* 정수 → 포인터(이식성·검증성 저하) */""",
  'good': r"""/* 메모리맵 레지스터는 의미를 캡슐화한 접근자로 */
volatile uint8_t * const REG = mmio_map(0x4000u);
*REG = 1u;""",
  'why':'정수와 포인터의 직접 변환은 이식성을 해치고 잘못된 주소 접근을 숨긴다. 불가피하면 한 곳에 캡슐화하고 그 외에는 피한다.'},

 {'id':'Rule 11.6','cat':'Required · Decidable · Rule',
  'title':'void 포인터와 정수 사이를 변환하지 않는다',
  'bad': r"""void *p = get_ctx();
uintptr_t n = (uintptr_t)p;
...
void *q = (void *)n;   /* 정수 왕복 — 정보 손실 위험 */""",
  'good': r"""void *p = get_ctx();
use_ctx(p);            /* 포인터를 그대로 보관·전달 */""",
  'why':'void*를 정수로 바꿔 보관·복원하면 표현 차이로 포인터가 손상될 수 있다. 포인터는 포인터 타입 그대로 유지한다.'},

 {'id':'Rule 11.8','cat':'Required · Decidable · Rule',
  'title':'캐스트로 포인터가 가리키는 대상의 const/volatile 한정자를 제거하지 않는다',
  'bad': r"""void log_msg(const char *s) {
    char *m = (char *)s;   /* const 제거 */
    m[0] = 'X';            /* 읽기전용 대상 수정 — 미정의 */
}""",
  'good': r"""void log_msg(const char *s) {
    char buf[64];
    strncpy(buf, s, sizeof buf - 1);   /* 복사본을 수정 */
    buf[sizeof buf - 1] = '\0';
    buf[0] = 'X';
}""",
  'why':'const/volatile를 캐스트로 떼어내고 수정하면 읽기 전용 대상 수정·최적화 오류 등 미정의 동작이 된다. 한정자를 보존하고 필요한 경우 복사본을 다룬다.'},

 {'id':'Rule 11.9','cat':'Required · Decidable · Rule',
  'title':'널 포인터 상수로는 매크로 NULL을 사용한다(정수 0 직접 사용 금지)',
  'bad': r"""char *p = 0;        /* 정수 0을 널 포인터로 */
if (p == 0) { ... }""",
  'good': r"""char *p = NULL;
if (p == NULL) { ... }""",
  'why':'정수 0을 널 포인터로 쓰면 의도가 모호하고 가독성이 떨어진다. 일관되게 NULL 매크로를 사용한다.'},

 {'id':'Rule 12.1','cat':'Advisory · Decidable · Rule',
  'title':'연산자 우선순위는 괄호로 명시한다',
  'bad': r"""int r = a + b << c & d;   /* 우선순위 혼동 */""",
  'good': r"""int r = (a + b) << (c & d) ... ;
int r2 = ((a + b) << c) & d;   /* 의도를 괄호로 명시 */""",
  'why':'시프트·비트·산술이 섞인 표현식은 우선순위를 오해하기 쉽다. 괄호로 평가 순서를 분명히 해 오류를 막는다.'},

 {'id':'Rule 12.2','cat':'Required · Undecidable · Rule',
  'title':'시프트 횟수는 0 이상이며 피연산자 비트폭 미만이어야 한다',
  'bad': r"""uint32_t v = 1u;
uint32_t r = v << 40;   /* 32비트를 40만큼 시프트 — 미정의 */""",
  'good': r"""uint32_t v = 1u;
unsigned n = get_shift();
if (n < 32u) { uint32_t r = v << n; }""",
  'why':'피연산자 비트폭 이상 또는 음수로 시프트하면 결과가 미정의다. 시프트량을 0..(폭-1) 범위로 보장한다.'},

 {'id':'Rule 12.3','cat':'Advisory · Decidable · Rule',
  'title':'쉼표 연산자를 사용하지 않는다',
  'bad': r"""for (i = 0, j = n; i < j; i++, j--) { swap(i, j); }""",
  'good': r"""j = n;
for (i = 0; i < j; i++) {
    swap(i, j);
    j--;
}""",
  'why':'쉼표 연산자는 한 표현식에 부작용을 숨겨 가독성과 분석을 어렵게 한다. 문장을 분리해 흐름을 명확히 한다.'},

 {'id':'Rule 13.1','cat':'Required · Undecidable · Rule',
  'title':'초기자 목록에는 영속적 부작용을 두지 않는다',
  'bad': r"""int a[2] = { f(), g() };   /* 평가 순서 미명세 — 부작용 순서 불명확 */""",
  'good': r"""int x = f();
int y = g();
int a[2] = { x, y };""",
  'why':'초기자 목록 요소의 평가 순서는 정해져 있지 않아 부작용이 있으면 결과가 비결정적이다. 부작용은 초기자 밖에서 순서대로 처리한다.'},

 {'id':'Rule 13.2','cat':'Required · Undecidable · Rule',
  'title':'표현식의 값과 부작용은 모든 평가 순서에서 동일해야 한다',
  'bad': r"""arr[i] = i++;        /* i 사용과 수정 순서 미명세 */""",
  'good': r"""arr[i] = i;
i++;""",
  'why':'한 표현식에서 같은 객체를 읽고 수정하면 평가 순서에 따라 결과가 달라진다. 읽기와 수정을 분리한다.'},

 {'id':'Rule 13.3','cat':'Advisory · Undecidable · Rule',
  'title':'증감 연산자(++/--)를 다른 부작용과 한 표현식에 섞지 않는다',
  'bad': r"""y = x++ + f(x);   /* x 증가와 f(x)의 x 사용이 섞임 */""",
  'good': r"""int t = x;
x++;
y = t + f(x);""",
  'why':'++/--를 다른 부작용과 결합하면 평가 순서 의존으로 결과가 모호해진다. 증감을 독립 문장으로 분리한다.'},

 {'id':'Rule 13.4','cat':'Advisory · Decidable · Rule',
  'title':'대입 연산자의 결과값을 사용하지 않는다',
  'bad': r"""if ((x = read()) != 0) { use(x); }   /* 대입 결과를 조건으로 */""",
  'good': r"""x = read();
if (x != 0) { use(x); }""",
  'why':'대입 결과를 조건·표현식에 쓰면 == 오타와 혼동되고 의도가 흐려진다. 대입과 검사를 분리한다.'},

 {'id':'Rule 13.5','cat':'Required · Undecidable · Rule',
  'title':'&&/|| 의 우변에는 영속적 부작용을 두지 않는다',
  'bad': r"""if (ready && (count = fetch()) > 0) { ... }  /* 단락 시 미평가 */""",
  'good': r"""count = fetch();
if (ready && count > 0) { ... }""",
  'why':'&&/||는 단락 평가라 좌변에 따라 우변이 실행되지 않을 수 있어, 우변 부작용이 조건부로 누락된다. 부작용은 논리 연산 밖으로 뺀다.'},

 {'id':'Rule 13.6','cat':'Mandatory · Decidable · Rule',
  'title':'sizeof 피연산자에는 부작용이 있는 표현식을 두지 않는다',
  'bad': r"""size_t n = sizeof(arr[i++]);   /* sizeof는 미평가 — i 증가 안 됨 */""",
  'good': r"""size_t n = sizeof(arr[0]);
i++;""",
  'why':'sizeof의 피연산자(가변길이 배열 제외)는 평가되지 않아 부작용이 적용되지 않는다. 의도한 부작용이 조용히 사라지므로 sizeof 안에 두지 않는다.'},

 {'id':'Rule 14.1','cat':'Required · Undecidable · Rule',
  'title':'반복 카운터로 부동소수형을 사용하지 않는다',
  'bad': r"""for (float x = 0.0f; x != 1.0f; x += 0.1f) { ... }  /* 누적 오차로 종료 실패 */""",
  'good': r"""for (int i = 0; i < 10; i++) {
    float x = (float)i * 0.1f;
}""",
  'why':'부동소수 카운터는 표현 오차가 누적되어 종료 조건을 정확히 만족하지 못하고 무한 루프가 될 수 있다. 정수 카운터로 반복하고 실수값은 파생한다.'},

 {'id':'Rule 14.2','cat':'Required · Undecidable · Rule',
  'title':'for 루프는 잘 정의된 형태(초기화·조건·증감 일관)여야 한다',
  'bad': r"""for (i = 0; i < n; total += a[i]) { i++; }  /* 증감부에 무관한 로직 */""",
  'good': r"""for (i = 0; i < n; i++) {
    total += a[i];
}""",
  'why':'for 헤더의 증감부가 카운터와 무관한 일을 하면 루프 동작을 이해·검증하기 어렵다. 헤더는 카운터 제어만, 본문은 작업만 담당하게 한다.'},

 {'id':'Rule 14.3','cat':'Required · Undecidable · Rule',
  'title':'제어 표현식이 항상 참/거짓으로 불변(invariant)이면 안 된다',
  'bad': r"""unsigned int u = get();
if (u >= 0u) { ... }   /* unsigned는 항상 >=0 — 항상 참 */""",
  'good': r"""unsigned int u = get();
if (u > 0u) { ... }    /* 실제로 분기되는 조건 */""",
  'why':'항상 같은 값으로 평가되는 제어식은 논리 오류(잘못된 비교)의 신호다. 조건이 실제로 분기되도록 바로잡는다.'},

 {'id':'Rule 14.4','cat':'Required · Decidable · Rule',
  'title':'if/while 의 제어 표현식은 본질적으로 불리언이어야 한다',
  'bad': r"""int *p = find();
if (p) { use(p); }     /* 포인터를 불리언처럼 */""",
  'good': r"""int *p = find();
if (p != NULL) { use(p); }""",
  'why':'포인터·정수를 그대로 조건에 쓰면 의도가 모호하고 0 비교 누락 오류를 부른다. 명시적 비교로 불리언 표현식을 만든다.'},

 {'id':'Rule 15.1','cat':'Advisory · Decidable · Rule',
  'title':'goto 문을 사용하지 않는다',
  'bad': r"""    if (err) goto fail;
    work();
fail:
    cleanup();""",
  'good': r"""    if (!err) {
        work();
    }
    cleanup();""",
  'why':'goto는 제어 흐름을 비선형으로 만들어 분석·검증을 어렵게 한다. 구조적 제어문(if/while/함수 분리)으로 대체한다.'},

 {'id':'Rule 15.5','cat':'Advisory · Decidable · Rule',
  'title':'함수는 끝에 단일 종료점(return)을 둔다',
  'bad': r"""int f(int x) {
    if (x < 0) return -1;
    if (x == 0) return 0;
    return x * 2;          /* 다중 return */
}""",
  'good': r"""int f(int x) {
    int r;
    if (x < 0)      { r = -1; }
    else if (x == 0){ r = 0; }
    else            { r = x * 2; }
    return r;
}""",
  'why':'중간 return이 흩어지면 자원 해제·후처리 누락과 흐름 추적 곤란을 부른다. 결과를 변수에 모아 마지막에 한 번 반환한다.'},

 {'id':'Rule 15.6','cat':'Required · Decidable · Rule',
  'title':'반복/선택문의 본문은 복합문(중괄호)으로 감싼다',
  'bad': r"""if (ready)
    a();
    b();        /* b는 if와 무관 — 들여쓰기 착시 */""",
  'good': r"""if (ready) {
    a();
}
b();""",
  'why':'중괄호 없는 단일 문 본문은 나중에 문장을 추가할 때 범위가 어긋나는 결함(예: Apple goto fail)을 부른다. 항상 중괄호로 본문을 감싼다.'},

 {'id':'Rule 15.7','cat':'Required · Decidable · Rule',
  'title':'if-else if 사슬은 마지막에 else 로 마무리한다',
  'bad': r"""if (m == 1) { a(); }
else if (m == 2) { b(); }   /* 그 외 경우 미처리 */""",
  'good': r"""if (m == 1) { a(); }
else if (m == 2) { b(); }
else { handle_other(); }    /* 모든 경우 처리 */""",
  'why':'else로 닫지 않은 if-else if는 예상 못한 입력을 조용히 무시한다. 마지막 else로 나머지 경우를 명시적으로 처리한다.'},

 {'id':'Rule 16.1','cat':'Required · Decidable · Rule',
  'title':'switch 문은 잘 정의된 구문 형태를 따른다',
  'bad': r"""switch (s) {
    int local;       /* case 밖 선언/문 */
    case 1: local = 1; break;
}""",
  'good': r"""switch (s) {
    case 1: {
        int local = 1;
        (void)local;
        break;
    }
    default: break;
}""",
  'why':'case 레이블 밖에 흩어진 선언·문장은 실행되지 않거나 모호한 동작을 만든다. 모든 코드를 case/default 절 안에 두어 구조를 정형화한다.'},

 {'id':'Rule 16.3','cat':'Required · Decidable · Rule',
  'title':'switch 의 각 절은 무조건 break(또는 종료)로 끝낸다',
  'bad': r"""switch (cmd) {
    case 1: open();    /* break 누락 — case 2로 흘러내림 */
    case 2: close(); break;
}""",
  'good': r"""switch (cmd) {
    case 1: open();  break;
    case 2: close(); break;
    default: break;
}""",
  'why':'break 누락에 의한 fall-through는 의도치 않은 다음 절 실행으로 흔한 버그를 만든다. 각 절을 break/return으로 명확히 종료한다.'},

 {'id':'Rule 16.4','cat':'Required · Decidable · Rule',
  'title':'모든 switch 문은 default 절을 가진다',
  'bad': r"""switch (state) {
    case S_IDLE: idle(); break;
    case S_RUN:  run();  break;
}                          /* 예상 못한 state 무시 */""",
  'good': r"""switch (state) {
    case S_IDLE: idle(); break;
    case S_RUN:  run();  break;
    default: handle_invalid(); break;
}""",
  'why':'default가 없으면 정의되지 않은 상태값이 조용히 무시되어 오류가 숨는다. default로 예외 상황을 반드시 처리한다.'},

 {'id':'Rule 16.5','cat':'Required · Decidable · Rule',
  'title':'default 레이블은 switch 본문의 처음 또는 마지막에 둔다',
  'bad': r"""switch (x) {
    case 1: a(); break;
    default: d(); break;   /* 중간에 위치 */
    case 2: b(); break;
}""",
  'good': r"""switch (x) {
    case 1: a(); break;
    case 2: b(); break;
    default: d(); break;
}""",
  'why':'default가 절들 사이에 끼면 가독성이 떨어지고 fall-through 의도를 오해하기 쉽다. 일관되게 처음이나 끝에 배치한다.'},

 {'id':'Rule 16.6','cat':'Required · Decidable · Rule',
  'title':'switch 문은 두 개 이상의 절을 가진다',
  'bad': r"""switch (flag) {
    default: handle(); break;   /* 절이 사실상 하나 */
}""",
  'good': r"""if (flag) { handle(); }   /* 분기가 하나면 if 가 적절 */""",
  'why':'절이 하나뿐인 switch는 if로 충분하며 구조를 과하게 만든다. 분기가 둘 이상일 때만 switch를 사용한다.'},

 {'id':'Rule 16.7','cat':'Required · Decidable · Rule',
  'title':'switch 의 제어 표현식은 본질적 불리언 타입이 아니어야 한다',
  'bad': r"""bool ok = check();
switch (ok) {            /* 참/거짓 분기에 switch */
    case true:  a(); break;
    case false: b(); break;
}""",
  'good': r"""bool ok = check();
if (ok) { a(); } else { b(); }""",
  'why':'두 값뿐인 불리언에 switch를 쓰면 부자연스럽고 가독성이 낮다. 불리언 분기는 if-else로 표현한다.'},

 {'id':'Rule 17.1','cat':'Required · Decidable · Rule',
  'title':'<stdarg.h> 의 가변인자 기능을 사용하지 않는다',
  'bad': r"""#include <stdarg.h>
int sum(int n, ...) {       /* 타입 안전성 없는 가변인자 */
    va_list ap; va_start(ap, n); ...
}""",
  'good': r"""int sum(const int *a, int n) {   /* 명시적 배열+개수 */
    int s = 0;
    for (int i = 0; i < n; i++) { s += a[i]; }
    return s;
}""",
  'why':'va_arg 가변인자는 타입·개수 검사가 없어 잘못된 타입 추출로 미정의 동작을 부른다. 배열+길이 같은 타입 안전 인터페이스로 대체한다.'},

 {'id':'Rule 17.2','cat':'Required · Undecidable · Rule',
  'title':'함수는 직접 또는 간접 재귀를 사용하지 않는다',
  'bad': r"""unsigned fact(unsigned n) {
    return (n <= 1u) ? 1u : n * fact(n - 1u);  /* 재귀 — 스택 한계 불확정 */
}""",
  'good': r"""unsigned fact(unsigned n) {
    unsigned r = 1u;
    for (unsigned i = 2u; i <= n; i++) { r *= i; }
    return r;   /* 반복으로 스택 사용 결정적 */
}""",
  'why':'재귀는 최대 스택 사용량을 정적으로 보장하기 어려워 안전필수 시스템에서 스택 오버플로우 위험이 있다. 반복(loop)으로 변환한다.'},

 {'id':'Rule 17.3','cat':'Mandatory · Decidable · Rule',
  'title':'함수는 암시적 선언 없이 호출해야 한다',
  'bad': r"""int r = compute(3);   /* 선언/프로토타입 없이 호출 */""",
  'good': r"""#include "compute.h"   /* int compute(int); 선언 포함 */
int r = compute(3);""",
  'why':'선언 없이 호출하면 인자·반환 타입이 잘못 가정되어 손상을 일으킨다. 호출 전에 프로토타입을 가시화한다.'},

 {'id':'Rule 17.4','cat':'Mandatory · Decidable · Rule',
  'title':'비void 함수는 모든 경로에서 값을 반환해야 한다',
  'bad': r"""int classify(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
}                          /* x==0 경로 반환 누락 */""",
  'good': r"""int classify(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}""",
  'why':'반환값을 명시하지 않고 끝나는 비void 함수의 반환값은 불확정이라 호출부에서 쓰레기값을 쓴다. 모든 경로에서 반환을 보장한다.'},

 {'id':'Rule 17.6','cat':'Mandatory · Decidable · Rule',
  'title':'배열 매개변수 선언에 static 키워드를 쓰지 않는다',
  'bad': r"""void f(int a[static 10]) { ... }   /* static 보장이 깨지면 미정의 */""",
  'good': r"""void f(const int *a, size_t n) {   /* 포인터+길이로 명시 */
    for (size_t i = 0; i < n; i++) { ... }
}""",
  'why':'배열 매개변수의 static 보장은 호출부가 어기면 진단 없이 미정의 동작이 된다. 포인터와 길이를 함께 전달하는 명시적 계약을 쓴다.'},

 {'id':'Rule 17.7','cat':'Required · Decidable · Rule',
  'title':'비void 함수의 반환값은 사용한다',
  'bad': r"""snprintf(buf, sizeof buf, "%d", v);   /* 반환(필요 길이) 무시 → 절단 감지 못함 */""",
  'good': r"""int need = snprintf(buf, sizeof buf, "%d", v);
if (need < 0 || (size_t)need >= sizeof buf) {
    handle_truncation();
}""",
  'why':'반환값을 무시하면 오류·절단·실제 결과를 감지하지 못한 채 진행한다. 의미 있는 반환값은 검사하거나 명시적으로 (void) 캐스트한다.'},

 {'id':'Rule 17.8','cat':'Advisory · Decidable · Rule',
  'title':'함수 매개변수를 함수 안에서 수정하지 않는다',
  'bad': r"""int scale(int n) {
    n = n * 2;        /* 매개변수 직접 수정 */
    return n + 1;
}""",
  'good': r"""int scale(int n) {
    int v = n * 2;    /* 지역 변수로 복사해 수정 */
    return v + 1;
}""",
  'why':'매개변수를 수정하면 호출 시 전달된 원래 인자값과의 대응이 흐려져 디버깅을 어렵게 한다. 지역 복사본을 두고 매개변수는 입력으로만 읽는다.'},
]
