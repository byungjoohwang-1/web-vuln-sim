# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트3: Rule 18~23) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'Rule 18.1','cat':'Required · Undecidable · Rule',
  'title':'포인터 산술 결과는 같은 배열의 범위 안을 가리켜야 한다',
  'bad': r"""int a[10];
int *p = a + 12;     /* 배열 밖을 가리킴 */
*p = 0;""",
  'good': r"""int a[10];
int i = get_index();
if (i >= 0 && i < 10) {
    int *p = a + i;
    *p = 0;
}""",
  'why':'배열 경계를 벗어난 포인터 연산 결과를 역참조하면 미정의 동작·메모리 손상이 발생한다. 인덱스를 검증해 범위 내 포인터만 만든다.'},

 {'id':'Rule 18.2','cat':'Required · Undecidable · Rule',
  'title':'포인터 뺄셈은 같은 배열의 원소들 사이에서만 한다',
  'bad': r"""int x, y;
ptrdiff_t d = &y - &x;   /* 서로 다른 객체 간 뺄셈 — 미정의 */""",
  'good': r"""int arr[8];
ptrdiff_t d = &arr[5] - &arr[1];   /* 같은 배열 내 */""",
  'why':'서로 다른 객체의 주소를 빼면 결과가 미정의다. 포인터 뺄셈은 동일 배열의 원소 사이에서만 수행한다.'},

 {'id':'Rule 18.3','cat':'Required · Undecidable · Rule',
  'title':'관계 연산(<,>)은 같은 객체를 가리키는 포인터끼리만 한다',
  'bad': r"""if (&bufA[0] < &bufB[0]) { ... }   /* 다른 배열 포인터 비교 — 미정의 */""",
  'good': r"""if (idxA < idxB) { ... }   /* 인덱스로 비교 */""",
  'why':'서로 다른 객체를 가리키는 포인터의 대소 비교 결과는 미정의다. 같은 배열 내 포인터이거나 인덱스로 비교한다.'},

 {'id':'Rule 18.4','cat':'Advisory · Decidable · Rule',
  'title':'포인터에 +, -, +=, -= 산술을 적용하지 않는다(배열 첨자 사용)',
  'bad': r"""int *p = buf;
*(p + 3) = 0;       /* 포인터 산술 */""",
  'good': r"""int *p = buf;
p[3] = 0;           /* 배열 첨자 표기 */""",
  'why':'포인터 산술은 경계 오류를 숨기고 가독성을 떨어뜨린다. 배열 첨자 표기를 써서 의도를 명확히 하고 분석을 쉽게 한다.'},

 {'id':'Rule 18.5','cat':'Advisory · Decidable · Rule',
  'title':'포인터의 중첩 수준은 2단계를 넘지 않는다',
  'bad': r"""int ***ppp;          /* 3중 포인터 — 이해/검증 곤란 */""",
  'good': r"""typedef struct Matrix { int *data; int rows, cols; } Matrix;
Matrix *m;          /* 구조체로 간접 단계 캡슐화 */""",
  'why':'3단계 이상의 포인터 중첩은 추론과 검증을 매우 어렵게 한다. 구조체로 간접 단계를 캡슐화해 중첩을 2단계 이하로 낮춘다.'},

 {'id':'Rule 18.6','cat':'Required · Undecidable · Rule',
  'title':'자동 저장기간 객체의 주소를 그 수명 밖으로 내보내지 않는다',
  'bad': r"""int *make(void) {
    int local = 42;
    return &local;   /* 함수 종료 후 무효한 주소 반환 */
}""",
  'good': r"""void make(int *out) {
    *out = 42;        /* 호출자가 소유한 저장소에 기록 */
}""",
  'why':'지역 변수의 주소는 함수가 끝나면 무효가 되어, 그 주소를 보관·역참조하면 미정의 동작이다. 호출자 소유 저장소나 정적 저장기간을 사용한다.'},

 {'id':'Rule 18.7','cat':'Required · Decidable · Rule',
  'title':'유연 배열 멤버(flexible array member)를 선언하지 않는다',
  'bad': r"""struct Packet { int len; char data[]; };  /* 유연 배열 멤버 */""",
  'good': r"""#define MAX_DATA 256
struct Packet { int len; char data[MAX_DATA]; };""",
  'why':'유연 배열 멤버는 크기가 런타임에 결정되어 정적 분석·경계 검사를 어렵게 한다. 최대 크기를 갖는 고정 배열로 대체한다.'},

 {'id':'Rule 18.8','cat':'Required · Decidable · Rule',
  'title':'가변 길이 배열(VLA)을 사용하지 않는다',
  'bad': r"""void f(int n) {
    int buf[n];      /* VLA — 스택 사용량 불확정 */
}""",
  'good': r"""#define MAX_N 128
void f(int n) {
    int buf[MAX_N];
    if (n <= MAX_N) { ... }
}""",
  'why':'VLA는 스택 사용량을 정적으로 알 수 없어 스택 오버플로우 위험이 있다. 컴파일 시 고정 크기 배열을 사용한다.'},

 {'id':'Rule 19.2','cat':'Advisory · Decidable · Rule',
  'title':'union 키워드 사용을 피한다',
  'bad': r"""union Conv { uint32_t u; float f; };
union Conv c; c.u = 0x40490FDBu;
float pi = c.f;     /* 타입 퍼닝 — 구현정의 */""",
  'good': r"""uint32_t u = 0x40490FDBu;
float pi;
memcpy(&pi, &u, sizeof pi);   /* 명시적 바이트 재해석 */""",
  'why':'union을 통한 타입 퍼닝은 마지막에 쓰지 않은 멤버를 읽을 때 구현정의 동작이 된다. memcpy로 의도를 명확히 하고 union 의존을 피한다.'},

 {'id':'Rule 20.1','cat':'Advisory · Decidable · Rule',
  'title':'#include 지시문 앞에는 전처리기 지시문/주석만 둔다',
  'bad': r"""int x = 0;
#include "late.h"    /* 코드 뒤에 등장 */""",
  'good': r"""#include "late.h"
int x = 0;""",
  'why':'코드 중간의 #include는 포함 순서 의존 결함과 가독성 저하를 일으킨다. 모든 #include는 파일 상단에 모은다.'},

 {'id':'Rule 20.3','cat':'Required · Decidable · Rule',
  'title':'#include 뒤에는 <헤더> 또는 "헤더" 형태만 온다',
  'bad': r"""#define HDR cfg.h
#include HDR        /* 매크로 확장 결과가 올바른 헤더명 보장 안 됨 */""",
  'good': r"""#include "cfg.h"   /* 명시적 헤더명 */""",
  'why':'매크로 확장으로 헤더명을 만들면 올바른 형식이 보장되지 않아 이식성 문제가 생긴다. #include에는 직접 헤더명을 적는다.'},

 {'id':'Rule 20.4','cat':'Required · Decidable · Rule',
  'title':'키워드와 같은 이름의 매크로를 정의하지 않는다',
  'bad': r"""#define int long    /* 키워드 재정의 — 전역 혼란 */""",
  'good': r"""typedef long wide_int_t;   /* 별칭 타입 정의 */""",
  'why':'키워드를 매크로로 재정의하면 모든 사용처의 의미가 바뀌어 예측 불가능한 동작을 만든다. 키워드 이름의 매크로 정의를 금지한다.'},

 {'id':'Rule 20.5','cat':'Advisory · Decidable · Rule',
  'title':'#undef 를 사용하지 않는다',
  'bad': r"""#define LIMIT 100
...
#undef LIMIT        /* 매크로 수명 추적 곤란 */
#define LIMIT 200""",
  'good': r"""#define LIMIT_LOW  100
#define LIMIT_HIGH 200   /* 서로 다른 이름으로 명시 */""",
  'why':'#undef 후 재정의는 같은 이름이 위치마다 다른 의미를 갖게 해 추적을 어렵게 한다. 서로 다른 값은 서로 다른 매크로 이름으로 둔다.'},

 {'id':'Rule 20.7','cat':'Required · Decidable · Rule',
  'title':'함수형 매크로의 매개변수는 괄호로 감싼다',
  'bad': r"""#define SCALE(x) x * 2
int r = SCALE(a + b);   /* a + b*2 로 전개됨 */""",
  'good': r"""#define SCALE(x) ((x) * 2)
int r = SCALE(a + b);   /* ((a + b) * 2) */""",
  'why':'매개변수를 괄호로 감싸지 않으면 전개 시 연산자 우선순위가 깨져 의도와 다른 식이 된다. 각 매개변수와 전체 식을 괄호로 보호한다.'},

 {'id':'Rule 20.8','cat':'Required · Decidable · Rule',
  'title':'#if/#elif 의 제어 표현식은 0 또는 1로 평가되어야 한다',
  'bad': r"""#if CONFIG_NAME       /* 정의 안 됐거나 비숫자면 모호 */
...
#endif""",
  'good': r"""#if defined(CONFIG_FEATURE) && (CONFIG_FEATURE == 1)
...
#endif""",
  'why':'정의되지 않았거나 불리언이 아닌 매크로를 #if에 쓰면 의도와 다르게 평가된다. defined()와 명시적 비교로 0/1을 보장한다.'},

 {'id':'Rule 20.9','cat':'Required · Decidable · Rule',
  'title':'#if/#elif 에 쓰는 식별자는 정의 여부를 defined 로 먼저 확인한다',
  'bad': r"""#if MODE == 2        /* MODE 미정의 시 0으로 간주되어 오판 */
...
#endif""",
  'good': r"""#if defined(MODE) && (MODE == 2)
...
#endif""",
  'why':'정의되지 않은 식별자는 #if에서 0으로 치환되어 의도치 않은 분기를 만든다. defined()로 존재를 확인한 뒤 값을 비교한다.'},

 {'id':'Rule 20.10','cat':'Advisory · Decidable · Rule',
  'title':'전처리기 연산자 # 와 ## 사용을 피한다',
  'bad': r"""#define MAKE(name) int var_##name = 0
MAKE(abc);          /* 토큰 붙이기 — 디버깅 곤란 */""",
  'good': r"""int var_abc = 0;    /* 명시적 선언 */""",
  'why':'#(문자열화)와 ##(토큰 결합)은 평가 순서가 까다롭고 디버깅이 어려운 코드를 만든다. 가능하면 명시적 코드로 대체한다.'},

 {'id':'Rule 20.12','cat':'Required · Decidable · Rule',
  'title':'# 또는 ## 의 피연산자가 되는 매크로 매개변수를 일관되게 사용한다',
  'bad': r"""#define J(a) a ## _x a   /* a 가 ##피연산자이면서 일반 사용 — 모호 */""",
  'good': r"""#define LABEL(a) a ## _x   /* 한 가지 용도로만 */""",
  'why':'한 매개변수를 ## 피연산자와 일반 확장에 동시에 쓰면 확장 결과가 모호해진다. 매개변수 사용 방식을 한 가지로 일관되게 둔다.'},

 {'id':'Rule 20.13','cat':'Required · Decidable · Rule',
  'title':'# 으로 시작하는 줄은 올바른 전처리기 지시문이어야 한다',
  'bad': r"""#インクルード "x.h"   /* 유효하지 않은 지시문 */""",
  'good': r"""#include "x.h"
/* 표준 지시문 철자만 사용 */""",
  'why':'#로 시작하지만 유효한 지시문이 아닌 줄은 미정의 동작이거나 이식성 문제를 만든다. 표준 지시문 철자만 사용한다.'},

 {'id':'Rule 20.14','cat':'Required · Decidable · Rule',
  'title':'#else/#endif 는 대응하는 #if 와 같은 파일에 둔다',
  'bad': r"""/* a.h */ #if COND
/* b.h 에서 */ #endif      /* 매칭이 파일을 가로지름 */""",
  'good': r"""/* a.h */
#if COND
...
#endif      /* 같은 파일에서 매칭 */""",
  'why':'조건부 컴파일 지시문이 파일 경계를 가로질러 매칭되면 포함 순서에 따라 동작이 달라진다. #if와 #endif를 같은 파일에서 짝짓는다.'},

 {'id':'Rule 21.1','cat':'Required · Undecidable · Rule',
  'title':'예약 식별자/매크로 이름을 #define 하거나 #undef 하지 않는다',
  'bad': r"""#define _MAX 100      /* 밑줄+대문자 — 구현 예약 */
#undef errno""",
  'good': r"""#define APP_MAX 100   /* 비예약 이름 */""",
  'why':'밑줄로 시작하거나 표준이 예약한 이름을 재정의하면 구현 내부와 충돌해 미정의 동작이 된다. 비예약 식별자만 정의한다.'},

 {'id':'Rule 21.2','cat':'Required · Undecidable · Rule',
  'title':'예약된 식별자/함수 이름을 선언하거나 정의하지 않는다',
  'bad': r"""int memcpy(int x) { return x; }   /* 표준 함수명 재정의 */""",
  'good': r"""int copy_block(int x) { return x; }""",
  'why':'표준 라이브러리·구현 예약 이름을 사용자가 정의하면 충돌과 미정의 동작이 발생한다. 고유한 사용자 이름을 쓴다.'},

 {'id':'Rule 21.3','cat':'Required · Undecidable · Rule',
  'title':'<stdlib.h> 의 동적 메모리 함수(malloc/calloc/realloc/free)를 쓰지 않는다',
  'bad': r"""int *buf = malloc(n * sizeof(int));
process(buf, n);
free(buf);""",
  'good': r"""#define MAX_N 256
int buf[MAX_N];
if (n <= MAX_N) { process(buf, n); }""",
  'why':'동적 할당은 단편화·비결정적 실패·누수·이중해제 위험이 있어 안전필수 코드에서 금지된다. 정적/자동 저장소로 대체한다.'},

 {'id':'Rule 21.4','cat':'Required · Decidable · Rule',
  'title':'<setjmp.h> 를 사용하지 않는다',
  'bad': r"""#include <setjmp.h>
jmp_buf env;
if (setjmp(env)) { recover(); }   /* 비국소 점프 */""",
  'good': r"""int rc = do_work();
if (rc != OK) { recover(); }      /* 반환값 기반 오류 전파 */""",
  'why':'setjmp/longjmp의 비국소 점프는 자원 해제를 건너뛰고 제어 흐름을 추적 불가능하게 만든다. 반환값으로 오류를 전파한다.'},

 {'id':'Rule 21.5','cat':'Required · Decidable · Rule',
  'title':'<signal.h> 의 시그널 기능을 사용하지 않는다',
  'bad': r"""#include <signal.h>
signal(SIGINT, handler);   /* 시그널 동작은 구현정의·비동기 위험 */""",
  'good': r"""/* 협조적 폴링으로 종료 요청 처리 */
while (!stop_requested()) { step(); }""",
  'why':'시그널 처리는 비동기·구현정의 동작이 많아 안전필수 환경에서 예측 불가능하다. 협조적 폴링 등 결정적 메커니즘을 쓴다.'},

 {'id':'Rule 21.6','cat':'Required · Decidable · Rule',
  'title':'표준 라이브러리 입출력 함수(<stdio.h>)를 사용하지 않는다',
  'bad': r"""#include <stdio.h>
printf("temp=%d\n", t);   /* 표준 I/O — 버퍼/포맷 위험 */""",
  'good': r"""/* 검증된 전용 입출력 계층 사용 */
uart_write_int("temp=", t);""",
  'why':'stdio의 포맷 입출력은 포맷 문자열 취약점·버퍼·예외 동작 위험이 있다. 안전필수 코드에서는 검증된 전용 I/O 계층을 사용한다.'},

 {'id':'Rule 21.7','cat':'Required · Decidable · Rule',
  'title':'atoi/atol/atoll/atof 변환 함수를 사용하지 않는다',
  'bad': r"""int n = atoi(text);   /* 오류·범위 초과를 알 수 없음 */""",
  'good': r"""char *end;
long v = strtol(text, &end, 10);
if (end == text || *end != '\0' || v < INT_MIN || v > INT_MAX) {
    handle_error();
}""",
  'why':'atoi 계열은 변환 실패와 범위 초과를 구분하지 못해 잘못된 값을 조용히 반환한다. 오류 검출이 가능한 strtol 계열을 쓴다.'},

 {'id':'Rule 21.8','cat':'Required · Decidable · Rule',
  'title':'<stdlib.h> 의 system/abort/exit/getenv 를 사용하지 않는다',
  'bad': r"""char *home = getenv("HOME");
system("rm -f /tmp/lock");   /* 환경 의존·셸 인젝션 위험 */""",
  'good': r"""/* 외부 셸 호출 없이 내부 API로 처리 */
remove_lock_file();""",
  'why':'system은 셸 인젝션, getenv는 신뢰 못 할 환경 의존, abort/exit는 자원 해제를 건너뛴다. 내부 API와 정상 반환 경로로 대체한다.'},

 {'id':'Rule 21.9','cat':'Required · Decidable · Rule',
  'title':'<stdlib.h> 의 bsearch/qsort 를 사용하지 않는다',
  'bad': r"""qsort(a, n, sizeof(int), cmp);   /* 콜백·비결정 동작 */""",
  'good': r"""/* 검증된 자체 정렬 루틴으로 결정적 동작 보장 */
insertion_sort(a, n);""",
  'why':'qsort/bsearch는 콜백 의존과 구현별 동작 차이로 결정성·검증성을 떨어뜨린다. 검증된 자체 알고리즘으로 대체한다.'},

 {'id':'Rule 21.10','cat':'Required · Decidable · Rule',
  'title':'<time.h> 의 날짜/시간 함수를 사용하지 않는다',
  'bad': r"""#include <time.h>
time_t now = time(NULL);   /* 구현정의·환경 의존 */""",
  'good': r"""uint32_t ticks = rtc_get_ticks();   /* 하드웨어 타이머 추상화 */""",
  'why':'표준 시간 함수는 구현정의 동작과 환경 의존성이 커 안전필수 시스템에 부적합하다. 하드웨어 타이머 추상화를 사용한다.'},

 {'id':'Rule 21.11','cat':'Required · Decidable · Rule',
  'title':'<tgmath.h> 타입-제네릭 수학 매크로를 사용하지 않는다',
  'bad': r"""#include <tgmath.h>
double r = sqrt(x);   /* 인자 타입에 따라 호출이 달라짐 */""",
  'good': r"""#include <math.h>
double r = sqrt((double)x);   /* 호출할 함수가 명확 */""",
  'why':'tgmath의 제네릭 매크로는 인자 타입에 따라 다른 함수를 선택해 의도 파악과 분석을 어렵게 한다. 타입별 함수를 명시적으로 호출한다.'},

 {'id':'Rule 21.13','cat':'Mandatory · Undecidable · Rule',
  'title':'<ctype.h> 함수 인자는 unsigned char 로 표현 가능하거나 EOF 여야 한다',
  'bad': r"""char c = get();
if (isdigit(c)) { ... }   /* c가 음수면 미정의 동작 */""",
  'good': r"""int c = get();
if (isdigit((unsigned char)c)) { ... }""",
  'why':'ctype 함수에 음수(부호 있는 char)를 넘기면 미정의 동작이 된다. unsigned char로 캐스트해 유효 범위를 보장한다.'},

 {'id':'Rule 21.14','cat':'Required · Decidable · Rule',
  'title':'memcmp 로 널 종료 문자열을 비교하지 않는다',
  'bad': r"""if (memcmp(a, b, strlen(a)) == 0) { ... }   /* 종료자/길이 차이 무시 */""",
  'good': r"""if (strcmp(a, b) == 0) { ... }""",
  'why':'memcmp는 널 종료를 모르고 고정 길이만 비교해, 길이가 다른 문자열을 같다고 오판할 수 있다. 문자열 비교는 strcmp를 쓴다.'},

 {'id':'Rule 21.15','cat':'Required · Decidable · Rule',
  'title':'memcpy/memmove/memcmp 의 포인터 인자는 호환되는 타입이어야 한다',
  'bad': r"""float f[4]; int i[4];
memcpy(f, i, sizeof f);   /* 서로 다른 타입 — 표현 차이 위험 */""",
  'good': r"""int src[4]; int dst[4];
memcpy(dst, src, sizeof dst);   /* 동일 타입 */""",
  'why':'표현이 다른 타입 간 바이트 복사는 잘못된 비트 패턴을 만들 수 있다. 메모리 함수의 두 포인터 인자는 같은 타입을 가리키게 한다.'},

 {'id':'Rule 21.17','cat':'Mandatory · Undecidable · Rule',
  'title':'문자열 함수 사용 시 대상 버퍼 경계를 벗어나지 않는다',
  'bad': r"""char dst[8];
strcpy(dst, src);     /* src가 8바이트 이상이면 오버플로우 */""",
  'good': r"""char dst[8];
size_t n = strlen(src);
if (n < sizeof dst) { memcpy(dst, src, n + 1); }""",
  'why':'strcpy/strcat은 대상 크기를 모르고 복사해 버퍼 오버플로우를 일으킨다. 길이를 확인하고 경계 내에서만 복사한다.'},

 {'id':'Rule 22.1','cat':'Required · Undecidable · Rule',
  'title':'획득한 자원은 모두 해제되어야 한다',
  'bad': r"""FILE *f = fopen(p, "r");
if (read_fail(f)) { return -1; }   /* fclose 누락 */
fclose(f);""",
  'good': r"""FILE *f = fopen(p, "r");
if (f == NULL) { return -1; }
int rc = read_fail(f) ? -1 : 0;
fclose(f);                         /* 모든 경로에서 해제 */
return rc;""",
  'why':'오류 경로에서 자원 해제를 빠뜨리면 핸들·메모리 누수가 누적된다. 모든 종료 경로에서 획득한 자원을 해제한다.'},

 {'id':'Rule 22.2','cat':'Mandatory · Undecidable · Rule',
  'title':'동적으로 할당된 메모리만 해제하며, 같은 메모리를 두 번 해제하지 않는다',
  'bad': r"""int x;
free(&x);          /* 비동적 메모리 해제 — 미정의 */""",
  'good': r"""/* 동적 메모리를 쓰지 않거나, 할당된 포인터만 한 번 해제 */
int x;
(void)x;""",
  'why':'정적/자동 객체나 이미 해제된 포인터를 free하면 힙 손상·미정의 동작이 된다. free 대상은 살아 있는 동적 할당 포인터로 한정한다.'},

 {'id':'Rule 22.3','cat':'Required · Undecidable · Rule',
  'title':'같은 파일을 동시에 읽기/쓰기 스트림으로 중복 개방하지 않는다',
  'bad': r"""FILE *r = fopen("d.bin", "r");
FILE *w = fopen("d.bin", "w");   /* 동시 개방 — 일관성 깨짐 */""",
  'good': r"""FILE *f = fopen("d.bin", "r+");   /* 단일 핸들로 갱신 */""",
  'why':'같은 파일을 여러 스트림으로 동시에 열면 버퍼 불일치와 데이터 손상이 발생한다. 단일 핸들로 접근을 일원화한다.'},

 {'id':'Rule 22.6','cat':'Mandatory · Undecidable · Rule',
  'title':'닫힌 FILE 포인터를 사용하지 않는다',
  'bad': r"""fclose(f);
fprintf(f, "x");   /* 닫힌 후 사용 — 미정의 */""",
  'good': r"""fprintf(f, "x");
fclose(f);
f = NULL;          /* 닫은 뒤 무효화 */""",
  'why':'fclose 이후의 FILE 포인터 사용은 미정의 동작이다. 닫은 후에는 사용하지 않고 포인터를 NULL로 무효화한다.'},

 {'id':'Rule 22.8','cat':'Required · Decidable · Rule',
  'title':'errno 를 검사하기 전에 0으로 초기화한다',
  'bad': r"""double v = strtod(s, NULL);
if (errno != 0) { ... }   /* 이전 errno 잔존 가능 */""",
  'good': r"""errno = 0;
double v = strtod(s, NULL);
if (errno != 0) { ... }""",
  'why':'호출 전 errno를 0으로 두지 않으면 이전 오류의 잔존 값을 현재 오류로 오인한다. 검사 대상 호출 직전에 errno를 0으로 설정한다.'},

 {'id':'Rule 22.10','cat':'Required · Undecidable · Rule',
  'title':'함수가 errno 를 설정하는 경우에만 errno 를 검사한다',
  'bad': r"""int n = some_func();
if (errno != 0) { ... }   /* errno를 설정하지 않는 함수에 검사 */""",
  'good': r"""errno = 0;
double v = strtod(s, NULL);   /* errno를 설정하는 함수 */
if (errno != 0) { ... }""",
  'why':'errno를 설정하지 않는 함수 뒤에 errno를 검사하면 무관한 이전 값을 보고 오판한다. errno 기반 검사는 errno를 설정하도록 명세된 함수에만 적용한다.'},
]
