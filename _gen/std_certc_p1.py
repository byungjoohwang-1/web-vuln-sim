# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트1: PRE·DCL·EXP·INT·FLP) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'PRE30-C','cat':'PRE · Rule · L1',
  'title':'토큰 연결로 보편 문자 이름(universal character name)을 만들지 않는다',
  'bad': r"""#define MK(a, b) a ## b
const char *s = "\MK(u, 0041)";   /* \u 결합 시도 — 미정의 */""",
  'good': r"""const wchar_t *s = L"A";   /* 완성된 형태로 직접 표기 */""",
  'why':'## 로 \\u 같은 보편 문자 이름을 조립하면 결과가 미정의다. 보편 문자 이름은 완성된 형태로 직접 작성한다.'},

 {'id':'PRE31-C','cat':'PRE · Rule · L1',
  'title':'안전하지 않은 매크로의 인자에 부작용을 두지 않는다',
  'bad': r"""#define ABS(x) ((x) < 0 ? -(x) : (x))
int y = ABS(i++);   /* i 가 두 번 평가 — 부작용 중복 */""",
  'good': r"""int t = i++;
int y = (t < 0) ? -t : t;   /* 인자를 한 번만 평가 */""",
  'why':'매크로가 인자를 여러 번 평가하면 부작용(증감·함수호출)이 중복 실행되어 결과가 어긋난다. 부작용은 매크로 밖에서 한 번만 수행한다.'},

 {'id':'PRE32-C','cat':'PRE · Rule · L1',
  'title':'함수형 매크로 호출 인자 안에 전처리기 지시문을 두지 않는다',
  'bad': r"""memcpy(dst, src,
#ifdef BIG
  64
#else
  32
#endif
);   /* 매크로일 경우 인자 내 지시문은 미정의 */""",
  'good': r"""#ifdef BIG
  size_t n = 64;
#else
  size_t n = 32;
#endif
memcpy(dst, src, n);""",
  'why':'함수형 매크로 인자 안의 #if 등은 표준에서 미정의 동작이다. 조건부 컴파일로 값을 먼저 정하고 매크로/함수에 전달한다.'},

 {'id':'PRE00-C','cat':'PRE · Rec · L3',
  'title':'함수형 매크로보다 인라인/정적 함수를 선호한다',
  'bad': r"""#define MAX(a,b) ((a) > (b) ? (a) : (b))""",
  'good': r"""static inline int imax(int a, int b) {
    return (a > b) ? a : b;
}""",
  'why':'매크로는 타입 검사가 없고 인자를 다중 평가한다. inline 함수는 동일 성능에 타입 안전성과 단일 평가를 보장한다.'},

 {'id':'PRE10-C','cat':'PRE · Rec · L3',
  'title':'여러 문장을 담는 매크로는 do-while(0)으로 감싼다',
  'bad': r"""#define LOG(x) printf("%d", x); fflush(stdout)
if (v) LOG(v);   /* if 본문에 첫 문장만 묶임 */""",
  'good': r"""#define LOG(x) do { printf("%d", x); fflush(stdout); } while (0)
if (v) { LOG(v); }""",
  'why':'여러 문장 매크로를 그냥 나열하면 if/else 본문에서 일부만 묶여 의도와 다르게 동작한다. do{...}while(0)으로 단일 문장처럼 만든다.'},

 {'id':'DCL30-C','cat':'DCL · Rule · L3',
  'title':'객체는 그 용도에 맞는 저장 기간(storage duration)으로 선언한다',
  'bad': r"""const char *get_name(void) {
    char buf[32];
    strcpy(buf, "node");
    return buf;        /* 자동 객체 주소 반환 — 수명 종료 */
}""",
  'good': r"""const char *get_name(void) {
    static const char name[] = "node";
    return name;       /* 정적 저장 기간 */
}""",
  'why':'자동 저장 기간 객체의 주소를 함수 밖으로 반환하면 수명이 끝나 무효한 메모리를 가리킨다. 정적 저장 기간이나 호출자 버퍼를 쓴다.'},

 {'id':'DCL31-C','cat':'DCL · Rule · L3',
  'title':'식별자는 사용 전에 선언한다',
  'bad': r"""int r = scale(3);    /* 선언 없이 호출 — 암시적 int 가정 */
int scale(int x) { return x * 2; }""",
  'good': r"""int scale(int x);    /* 사용 전 선언 */
int r = scale(3);
int scale(int x) { return x * 2; }""",
  'why':'선언 없는 사용은 타입을 잘못 가정해 인자/반환 손상을 일으킨다. 모든 식별자를 사용 전에 선언한다.'},

 {'id':'DCL37-C','cat':'DCL · Rule · L1',
  'title':'예약된 식별자를 선언하거나 정의하지 않는다',
  'bad': r"""int _internal_count;   /* 밑줄 시작 — 구현 예약 영역 */
#define __MYMACRO 1""",
  'good': r"""int internal_count;
#define MYMACRO 1""",
  'why':'밑줄로 시작하는 이름이나 표준 예약 이름을 사용자가 선언하면 구현 내부와 충돌해 미정의 동작이 된다. 비예약 이름을 쓴다.'},

 {'id':'DCL38-C','cat':'DCL · Rule · L1',
  'title':'유연 배열 멤버는 올바른 구문으로 선언한다',
  'bad': r"""struct Buf { size_t n; char data[1]; };  /* [1] 트릭 — 경계 모호 */""",
  'good': r"""struct Buf { size_t n; char data[]; };   /* C99 유연 배열 멤버 */
struct Buf *b = malloc(sizeof *b + len);""",
  'why':'data[1] 같은 옛 트릭은 실제 크기와 선언이 어긋나 경계 검사를 무력화한다. C99 유연 배열 멤버 구문을 정확히 사용한다.'},

 {'id':'DCL39-C','cat':'DCL · Rec · L3',
  'title':'구조체 패딩을 통한 정보 유출을 피한다',
  'bad': r"""struct S { char c; int v; };   /* c와 v 사이 패딩에 잔존 데이터 */
write(fd, &s, sizeof s);       /* 패딩 바이트 유출 */""",
  'good': r"""struct S s;
memset(&s, 0, sizeof s);       /* 패딩 포함 0으로 초기화 */
s.c = 'x'; s.v = 1;
write(fd, &s, sizeof s);""",
  'why':'구조체를 그대로 외부로 쓰면 초기화되지 않은 패딩 바이트에 남은 민감 데이터가 유출될 수 있다. 전체를 0으로 초기화한 뒤 채운다.'},

 {'id':'DCL40-C','cat':'DCL · Rule · L2',
  'title':'같은 함수/객체에 호환되지 않는 선언을 만들지 않는다',
  'bad': r"""/* a.c */ extern int data[8];
/* b.c */ extern int *data;    /* 배열을 포인터로 — 호환 안 됨 */""",
  'good': r"""/* shared.h */ extern int data[8];
/* a.c, b.c */ #include "shared.h" """,
  'why':'같은 심볼을 파일마다 다른(호환 안 되는) 타입으로 선언하면 링커가 잡지 못한 채 잘못 접근한다. 공유 헤더로 단일 선언을 보장한다.'},

 {'id':'DCL41-C','cat':'DCL · Rule · L3',
  'title':'switch 의 첫 case 이전에 변수를 선언하지 않는다',
  'bad': r"""switch (x) {
    int y = 5;          /* 초기화가 실행되지 않음 */
    case 1: use(y); break;
}""",
  'good': r"""int y = 5;
switch (x) {
    case 1: use(y); break;
    default: break;
}""",
  'why':'switch 본문 첫 레이블 이전의 선언 초기화는 점프로 건너뛰어져 미초기화 값을 읽게 된다. 선언은 switch 밖이나 case 블록 안에 둔다.'},

 {'id':'DCL00-C','cat':'DCL · Rec · L3',
  'title':'변경되지 않는 객체는 const 로 한정한다',
  'bad': r"""int limit = 100;     /* 이후 수정 없음에도 비-const */
use(limit);""",
  'good': r"""const int limit = 100;
use(limit);""",
  'why':'불변 객체를 const로 표시하지 않으면 실수로 수정되거나 의도가 흐려진다. const로 변경 불가를 컴파일러가 강제하게 한다.'},

 {'id':'DCL02-C','cat':'DCL · Rec · L2',
  'title':'시각적으로 구별되는 식별자를 사용한다',
  'bad': r"""int rn, m;
int rnn;            /* rn, rnn — 혼동 */""",
  'good': r"""int row_count, max_count;
int running_total;""",
  'why':'철자가 비슷한 짧은 이름은 잘못된 변수 참조를 부른다. 의미가 드러나는 구별되는 이름을 쓴다.'},

 {'id':'DCL18-C','cat':'DCL · Rec · L3',
  'title':'정수 상수를 0으로 시작(8진수)하지 않는다',
  'bad': r"""int code = 013;     /* 8진수 11, 의도는 13? */""",
  'good': r"""int code = 13;      /* 10진수 */""",
  'why':'선행 0은 8진수로 해석되어 013이 11이 되는 등 의도와 다른 값이 된다. 10진/16진 표기를 쓴다.'},

 {'id':'EXP30-C','cat':'EXP · Rule · L2',
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'bad': r"""int i = 0;
arr[i] = i++;       /* i 사용과 증가 순서 미명세 */""",
  'good': r"""int i = 0;
arr[i] = i;
i++;""",
  'why':'한 표현식에서 같은 객체를 수정·사용하면 평가 순서에 따라 결과가 달라진다. 부작용을 분리해 순서를 결정한다.'},

 {'id':'EXP32-C','cat':'EXP · Rule · L1',
  'title':'volatile 객체를 비-volatile 참조로 접근하지 않는다',
  'bad': r"""volatile int reg;
int *p = (int *)&reg;
int v = *p;         /* volatile 의미 상실 */""",
  'good': r"""volatile int reg;
volatile int *p = &reg;
int v = *p;""",
  'why':'volatile 객체를 비-volatile 포인터로 접근하면 컴파일러가 접근을 최적화로 제거·재배치해 하드웨어 동작이 깨진다. 한정자를 보존한다.'},

 {'id':'EXP33-C','cat':'EXP · Rule · L3',
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'bad': r"""int sum;
for (int i = 0; i < n; i++) sum += a[i];   /* sum 미초기화 */""",
  'good': r"""int sum = 0;
for (int i = 0; i < n; i++) sum += a[i];""",
  'why':'미초기화 객체의 값은 불확정이라 읽으면 미정의 동작과 비결정적 결과를 낳는다. 사용 전 명시적으로 초기화한다.'},

 {'id':'EXP34-C','cat':'EXP · Rule · L1',
  'title':'널 포인터를 역참조하지 않는다',
  'bad': r"""Node *n = find(key);
n->value = 0;       /* find 실패(NULL) 미검사 */""",
  'good': r"""Node *n = find(key);
if (n != NULL) {
    n->value = 0;
}""",
  'why':'널 포인터 역참조는 크래시나 미정의 동작을 일으킨다. 역참조 전에 NULL 여부를 확인한다.'},

 {'id':'EXP36-C','cat':'EXP · Rule · L1',
  'title':'포인터를 더 엄격히 정렬된 타입으로 캐스트하지 않는다',
  'bad': r"""char buf[16];
int *p = (int *)&buf[1];   /* 정렬 위반 가능 */
*p = 0;""",
  'good': r"""char buf[16];
int v = 0;
memcpy(&buf[1], &v, sizeof v);   /* 정렬 무관 */""",
  'why':'정렬 요건이 더 큰 타입으로 포인터를 캐스트해 접근하면 일부 플랫폼에서 폴트나 미정의 동작이 난다. memcpy로 정렬 비의존 접근을 한다.'},

 {'id':'EXP37-C','cat':'EXP · Rule · L1',
  'title':'함수는 올바른 개수·타입의 인자로 호출한다',
  'bad': r"""int f(int, int);
int r = ((int(*)(int))f)(3);   /* 잘못된 시그니처로 호출 */""",
  'good': r"""int f(int, int);
int r = f(3, 4);""",
  'why':'선언과 다른 시그니처로 함수를 호출하면 인자 전달이 어긋나 미정의 동작이 된다. 정확한 프로토타입대로 호출한다.'},

 {'id':'EXP39-C','cat':'EXP · Rule · L2',
  'title':'호환되지 않는 타입의 포인터로 변수에 접근하지 않는다',
  'bad': r"""float f = 3.14f;
unsigned u = *(unsigned *)&f;   /* 엄격 별칭 위반 */""",
  'good': r"""float f = 3.14f;
unsigned u;
memcpy(&u, &f, sizeof u);""",
  'why':'엄격 별칭 규칙을 어기고 다른 타입 포인터로 접근하면 컴파일러 최적화와 충돌해 미정의 동작이 된다. memcpy로 안전하게 재해석한다.'},

 {'id':'EXP40-C','cat':'EXP · Rule · L1',
  'title':'const 로 선언된 객체를 수정하지 않는다',
  'bad': r"""const int k = 5;
int *p = (int *)&k;
*p = 9;             /* const 객체 수정 — 미정의 */""",
  'good': r"""int k = 5;          /* 수정이 필요하면 비-const */
k = 9;""",
  'why':'const 객체를 캐스트로 우회해 수정하면 미정의 동작이다. 수정이 필요한 객체는 처음부터 비-const로 선언한다.'},

 {'id':'EXP44-C','cat':'EXP · Rule · L3',
  'title':'sizeof/_Alignof/_Generic 피연산자의 부작용에 의존하지 않는다',
  'bad': r"""int i = 0;
size_t n = sizeof(a[i++]);   /* i 증가 안 됨 */""",
  'good': r"""size_t n = sizeof(a[0]);
i++;""",
  'why':'sizeof 등의 피연산자는 평가되지 않아 부작용이 발생하지 않는다. 의도한 부작용은 별도 문장으로 수행한다.'},

 {'id':'EXP45-C','cat':'EXP · Rule · L3',
  'title':'선택문(if/while 등)의 조건에서 대입을 수행하지 않는다',
  'bad': r"""if (x = compute()) { ... }   /* == 오타? 의도 모호 */""",
  'good': r"""x = compute();
if (x != 0) { ... }""",
  'why':'조건식 안의 대입은 비교(==) 오타와 혼동되며 의도가 불명확하다. 대입과 조건 검사를 분리한다.'},

 {'id':'EXP46-C','cat':'EXP · Rule · L3',
  'title':'불리언 성격의 피연산자에 비트 연산자를 쓰지 않는다',
  'bad': r"""if ((a == b) & (c == d)) { ... }   /* & 는 단락 없음·의도 모호 */""",
  'good': r"""if ((a == b) && (c == d)) { ... }""",
  'why':'논리 비교 결과에 비트 &/|를 쓰면 단락 평가가 사라지고 의도가 흐려진다. 논리 연산에는 &&/||를 쓴다.'},

 {'id':'EXP47-C','cat':'EXP · Rule · L1',
  'title':'va_arg 를 잘못된 타입으로 호출하지 않는다',
  'bad': r"""va_list ap; va_start(ap, fmt);
long v = va_arg(ap, long);   /* 실제 인자가 int면 미정의 */""",
  'good': r"""va_list ap; va_start(ap, fmt);
int v = va_arg(ap, int);     /* 실제 전달 타입과 일치 */""",
  'why':'va_arg에 실제 전달된 타입과 다른 타입을 지정하면 잘못된 비트를 읽어 미정의 동작이 된다. 전달 타입과 정확히 일치시킨다.'},

 {'id':'EXP12-C','cat':'EXP · Rec · L2',
  'title':'함수의 반환값을 무시하지 않는다',
  'bad': r"""fwrite(buf, 1, n, f);   /* 실제 기록량 무시 */""",
  'good': r"""size_t w = fwrite(buf, 1, n, f);
if (w != n) { handle_write_error(); }""",
  'why':'반환값을 무시하면 부분 실패·오류를 감지하지 못한다. 의미 있는 반환값은 검사하거나 명시적으로 (void)로 버린다.'},

 {'id':'INT30-C','cat':'INT · Rule · L2',
  'title':'부호 없는 정수 연산이 래핑(wrap)되지 않도록 보장한다',
  'bad': r"""unsigned a = get(), b = get();
unsigned s = a + b;   /* 오버플로우 시 모듈로 래핑 */""",
  'good': r"""unsigned a = get(), b = get();
if (a > UINT_MAX - b) { handle_overflow(); }
else { unsigned s = a + b; }""",
  'why':'부호 없는 덧셈은 오버플로우 시 조용히 모듈로 래핑되어 길이·인덱스 계산을 망가뜨린다. 연산 전에 래핑 조건을 검사한다.'},

 {'id':'INT31-C','cat':'INT · Rule · L2',
  'title':'정수 변환이 데이터를 잃거나 잘못 해석하지 않도록 한다',
  'bad': r"""long big = get_long();
int n = big;          /* 범위 초과 시 구현정의 절단 */
char buf[n];""",
  'good': r"""long big = get_long();
if (big < 0 || big > INT_MAX) { handle_range(); }
else { int n = (int)big; }""",
  'why':'넓은 정수를 좁은 타입으로 변환하면 값이 잘리거나 부호가 뒤바뀐다. 변환 전에 대상 타입 범위를 검사한다.'},

 {'id':'INT32-C','cat':'INT · Rule · L2',
  'title':'부호 있는 정수 연산이 오버플로우되지 않도록 보장한다',
  'bad': r"""int a = get(), b = get();
int p = a * b;        /* signed 오버플로우 — 미정의 */""",
  'good': r"""int a = get(), b = get();
if (a != 0 && (b > INT_MAX / a || b < INT_MIN / a)) { handle_overflow(); }
else { int p = a * b; }""",
  'why':'부호 있는 정수 오버플로우는 미정의 동작이다. 곱셈·덧셈 전에 피연산자로 한계를 나눠 오버플로우 가능성을 검사한다.'},

 {'id':'INT33-C','cat':'INT · Rule · L2',
  'title':'나눗셈/나머지 연산에서 0으로 나누지 않는다',
  'bad': r"""int q = total / count;   /* count==0 가능 */""",
  'good': r"""if (count == 0) { handle_error(); }
else { int q = total / count; }""",
  'why':'0으로 나누거나 나머지를 구하면 미정의 동작(대개 크래시)이 된다. 나누기 전에 분모가 0이 아님을 확인한다.'},

 {'id':'INT34-C','cat':'INT · Rule · L2',
  'title':'음수나 비트폭 이상으로 시프트하지 않는다',
  'bad': r"""unsigned v = 1u;
unsigned r = v << n;   /* n >= 32 또는 음수면 미정의 */""",
  'good': r"""unsigned v = 1u;
if (n < (unsigned)(sizeof(unsigned) * CHAR_BIT)) {
    unsigned r = v << n;
}""",
  'why':'시프트량이 음수이거나 피연산자 비트폭 이상이면 결과가 미정의다. 시프트 전에 0..(폭-1) 범위를 보장한다.'},

 {'id':'INT35-C','cat':'INT · Rule · L1',
  'title':'정수 정밀도(precision)를 올바르게 사용한다',
  'bad': r"""unsigned bits = sizeof(unsigned) * 8;   /* CHAR_BIT가 8이라 가정 */""",
  'good': r"""#include <limits.h>
unsigned bits = sizeof(unsigned) * CHAR_BIT;""",
  'why':'바이트가 항상 8비트라고 가정하면 비표준 플랫폼에서 정밀도 계산이 틀어진다. CHAR_BIT로 실제 비트 수를 구한다.'},

 {'id':'INT18-C','cat':'INT · Rec · L3',
  'title':'정수 표현식은 충분히 큰 타입에서 평가한다',
  'bad': r"""uint16_t a = 60000u, b = 10000u;
uint32_t s = a + b;   /* 16비트로 계산 후 확장 — 래핑 */""",
  'good': r"""uint16_t a = 60000u, b = 10000u;
uint32_t s = (uint32_t)a + b;   /* 32비트로 평가 */""",
  'why':'좁은 타입끼리 계산 후 넓히면 계산이 좁은 폭에서 일어나 오버플로우가 숨는다. 평가 전에 충분히 큰 타입으로 승격한다.'},

 {'id':'FLP30-C','cat':'FLP · Rule · L3',
  'title':'부동소수형을 루프 카운터로 사용하지 않는다',
  'bad': r"""for (float x = 0.0f; x != 1.0f; x += 0.1f) { ... }  /* 종료 실패 */""",
  'good': r"""for (int i = 0; i < 10; i++) {
    float x = (float)i / 10.0f;
}""",
  'why':'부동소수 카운터는 표현 오차로 종료 조건을 정확히 만족하지 못해 무한 루프가 될 수 있다. 정수로 반복하고 실수는 파생한다.'},

 {'id':'FLP32-C','cat':'FLP · Rule · L2',
  'title':'수학 함수의 도메인/범위 오류를 예방하거나 검출한다',
  'bad': r"""double r = sqrt(x);   /* x<0 이면 NaN */""",
  'good': r"""if (x < 0.0) { handle_domain(); }
else { double r = sqrt(x); }""",
  'why':'정의역을 벗어난 인자(예: sqrt의 음수)는 도메인 오류·NaN을 만든다. 호출 전 인자 범위를 검사하거나 errno/예외 플래그를 확인한다.'},

 {'id':'FLP34-C','cat':'FLP · Rule · L2',
  'title':'부동소수 변환은 대상 타입 범위 안에서만 수행한다',
  'bad': r"""double d = get();
int n = (int)d;       /* 범위 초과 시 미정의 */""",
  'good': r"""double d = get();
if (d >= (double)INT_MIN && d <= (double)INT_MAX) {
    int n = (int)d;
}""",
  'why':'대상 정수 타입 범위를 벗어난 부동소수를 변환하면 미정의 동작이 된다. 변환 전에 범위를 검사한다.'},

 {'id':'FLP03-C','cat':'FLP · Rec · L2',
  'title':'부동소수 연산 오류를 검출하고 처리한다',
  'bad': r"""double r = a / b;     /* 0 나눗셈·언더플로우 미검사 */
use(r);""",
  'good': r"""#include <fenv.h>
feclearexcept(FE_ALL_EXCEPT);
double r = a / b;
if (fetestexcept(FE_DIVBYZERO | FE_INVALID)) { handle_fp_error(); }""",
  'why':'부동소수 예외(0 나눗셈·무효 연산)를 무시하면 NaN/Inf가 후속 계산에 전파된다. fenv로 예외 플래그를 확인해 처리한다.'},
]
