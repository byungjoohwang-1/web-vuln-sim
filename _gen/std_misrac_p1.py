# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트1: Dir + Rule 1~9) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'Dir 1.1','cat':'Required · Undecidable · Dir',
  'title':'구현정의(implementation-defined) 동작에 의존하는 부분은 문서화·이해되어야 한다',
  'bad': r"""/* int 비트폭, char 부호 등 구현정의 사항을 가정하고 사용 */
int flags = 0;
flags = ~0;            /* int가 16비트인지 32비트인지 가정? */
char c = readByte();
if (c > 127) { ... }   /* char가 signed/unsigned인지 미문서화 */""",
  'good': r"""/* 폭·부호가 고정된 타입과 명시 상수를 사용해 구현정의 의존 제거 */
#include <stdint.h>
uint32_t flags = 0xFFFFFFFFu;
unsigned char c = readByte();   /* 부호 명시 */
if (c > 127u) { ... }""",
  'why':'int 폭이나 char 부호 같은 구현정의 동작에 암묵 의존하면 이식 시 결함이 발생한다. 고정폭 타입(stdint.h)과 명시적 부호로 의존을 제거하거나 문서화한다.'},

 {'id':'Dir 2.1','cat':'Required · Undecidable · Dir',
  'title':'모든 소스 파일은 오류 없이 컴파일되어야 한다',
  'bad': r"""/* 조건부로 컴파일에서 빠지는 깨진 코드가 방치됨 */
#if 0
int legacy(void) { return undefined_symbol; }  /* 컴파일 안 되는 죽은 코드 */
#endif""",
  'good': r"""/* 빌드에서 제외할 코드는 제거하거나, 유효하게 유지·컴파일 */
int legacy(void) {
    return 0;   /* 유지한다면 컴파일 가능한 상태로 */
}""",
  'why':'#if 0 등으로 가려둔 컴파일 불가 코드는 유지보수 시 되살아나 빌드를 깬다. 불필요한 코드는 삭제하고, 남길 코드는 항상 컴파일 가능하게 유지한다.'},

 {'id':'Dir 3.1','cat':'Required · Undecidable · Dir',
  'title':'모든 코드는 요구사항으로 추적 가능해야 한다',
  'bad': r"""/* 어떤 요구사항도 근거하지 않은 임시 기능 */
void hidden_debug_backdoor(void) {   /* 추적 불가 기능 */
    system("/bin/sh");
}""",
  'good': r"""/* 요구사항 ID를 주석으로 연계해 추적성 확보 */
/* REQ-LOG-014: 진단 로그 기록 */
void write_diag_log(const char *msg) {
    log_append(msg);
}""",
  'why':'요구사항에 근거하지 않은 코드는 검증·심사 대상에서 누락되며 백도어·불필요 기능의 온상이 된다. 코드와 요구사항 간 추적성을 유지한다.'},

 {'id':'Dir 4.1','cat':'Required · Undecidable · Dir',
  'title':'런타임 실패(0 나눗셈·범위 초과·널 역참조 등) 가능성을 최소화한다',
  'bad': r"""int average(const int *a, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) { sum += a[i]; }
    return sum / n;    /* n==0이면 0 나눗셈 */
}""",
  'good': r"""int average(const int *a, int n, int *ok) {
    if (a == NULL || n <= 0) { *ok = 0; return 0; }
    int sum = 0;
    for (int i = 0; i < n; i++) { sum += a[i]; }
    *ok = 1;
    return sum / n;
}""",
  'why':'0 나눗셈·널 역참조·배열 범위 초과 등은 정의되지 않은 동작이다. 연산 전에 분모·포인터·인덱스 유효성을 확인해 런타임 실패를 차단한다.'},

 {'id':'Dir 4.3','cat':'Required · Decidable · Dir',
  'title':'어셈블리 언어는 캡슐화하고 격리한다',
  'bad': r"""void delay(void) {
    int i = 100;
    __asm__("nop");      /* C 로직 한가운데 인라인 어셈블리 산재 */
    while (i--) { doWork(); __asm__("nop"); }
}""",
  'good': r"""/* 어셈블리는 전용 함수/매크로로 캡슐화 */
static inline void cpu_nop(void) { __asm__("nop"); }

void delay(void) {
    int i = 100;
    cpu_nop();
    while (i--) { doWork(); cpu_nop(); }
}""",
  'why':'C 로직에 인라인 어셈블리가 산재하면 가독성·이식성·정적분석이 모두 저하된다. 어셈블리는 명명된 함수나 매크로로 캡슐화해 한 곳에 격리한다.'},

 {'id':'Dir 4.4','cat':'Advisory · Undecidable · Dir',
  'title':'코드 섹션을 주석 처리(comment-out)로 비활성화하지 않는다',
  'bad': r"""void process(Data *d) {
    validate(d);
    /* transform(d);      // 임시로 막아둠
       commit(d); */
    notify(d);
}""",
  'good': r"""void process(Data *d) {
    validate(d);
#if FEATURE_TRANSFORM
    transform(d);
    commit(d);
#endif
    notify(d);
}""",
  'why':'주석으로 막아둔 코드는 의도가 불명확하고 버전관리로 충분히 추적 가능하다. 정말 필요하면 조건부 컴파일로, 아니면 삭제한다.'},

 {'id':'Dir 4.5','cat':'Advisory · Undecidable · Dir',
  'title':'동일 네임스페이스의 식별자는 철자만 다른 혼동 이름을 피한다',
  'bad': r"""int total;
int totaI;    /* 'l'(엘) vs 'I'(대문자 아이) — 혼동 */
int  rn_count;
int  m_count;""",
  'good': r"""int total_sum;
int total_avg;     /* 시각적으로 명확히 구분 */
int received_count;
int matched_count;""",
  'why':'l/I/1, O/0 처럼 시각적으로 혼동되는 이름은 잘못된 변수를 참조하는 결함을 부른다. 한 네임스페이스 안에서는 충분히 구별되는 이름을 쓴다.'},

 {'id':'Dir 4.6','cat':'Advisory · Undecidable · Dir',
  'title':'기본 수치형 대신 크기·부호를 명시한 typedef를 사용한다',
  'bad': r"""long  timestamp;     /* 플랫폼마다 32/64비트 */
unsigned int crc;    /* 폭이 16/32비트로 달라질 수 있음 */
short sample;""",
  'good': r"""#include <stdint.h>
int64_t  timestamp;
uint32_t crc;
int16_t  sample;""",
  'why':'int/long/short의 폭은 구현정의라 이식 시 오버플로우·절단이 발생한다. stdint.h의 고정폭 타입으로 폭과 부호를 명시한다.'},

 {'id':'Dir 4.7','cat':'Required · Undecidable · Dir',
  'title':'오류 정보를 반환하는 함수의 반환값은 반드시 검사한다',
  'bad': r"""FILE *f = fopen(path, "r");
char buf[64];
fgets(buf, sizeof buf, f);   /* fopen 실패(NULL) 미검사 */""",
  'good': r"""FILE *f = fopen(path, "r");
if (f == NULL) {
    return ERR_OPEN;
}
char buf[64];
if (fgets(buf, sizeof buf, f) == NULL) { /* 읽기 실패 처리 */ }
fclose(f);""",
  'why':'오류를 반환하는 함수의 결과를 무시하면 실패 상태에서 계속 진행해 널 역참조·미정의 동작으로 이어진다. 반환값을 즉시 검사하고 분기한다.'},

 {'id':'Dir 4.9','cat':'Advisory · Decidable · Dir',
  'title':'함수형 매크로보다 함수를 사용한다',
  'bad': r"""#define SQUARE(x) ((x)*(x))
int y = SQUARE(i++);   /* i가 두 번 증가 — 부작용 중복 */""",
  'good': r"""static inline int square(int x) {
    return x * x;       /* 인자 1회 평가, 타입 검사 */
}
int y = square(i++);""",
  'why':'함수형 매크로는 인자를 여러 번 평가해 부작용을 중복시키고 타입 검사를 못 한다. inline 함수가 같은 성능에 안전하다.'},

 {'id':'Dir 4.10','cat':'Required · Decidable · Dir',
  'title':'헤더 파일은 중복 포함을 방지(include guard)한다',
  'bad': r"""/* sensor.h — 가드 없음 */
typedef struct { int id; } Sensor;
void sensor_init(Sensor *);   /* 두 번 포함되면 재정의 오류 */""",
  'good': r"""/* sensor.h */
#ifndef SENSOR_H
#define SENSOR_H
typedef struct { int id; } Sensor;
void sensor_init(Sensor *);
#endif /* SENSOR_H */""",
  'why':'가드 없는 헤더가 중복 포함되면 타입·매크로 재정의로 컴파일 오류가 난다. #ifndef/#define 가드(또는 #pragma once)로 1회만 처리되게 한다.'},

 {'id':'Dir 4.11','cat':'Required · Undecidable · Dir',
  'title':'라이브러리 함수에 전달하는 인자의 유효성을 검사한다',
  'bad': r"""double r = sqrt(x);     /* x<0 이면 도메인 오류(NaN) */
double l = log(v);      /* v<=0 이면 도메인 오류 */""",
  'good': r"""if (x < 0.0) { return ERR_DOMAIN; }
double r = sqrt(x);
if (v <= 0.0) { return ERR_DOMAIN; }
double l = log(v);""",
  'why':'sqrt/log/memcpy 등은 인자 범위를 벗어나면 도메인 오류나 미정의 동작을 일으킨다. 호출 전에 정의역·길이·중첩 여부를 확인한다.'},

 {'id':'Dir 4.12','cat':'Required · Undecidable · Dir',
  'title':'동적 메모리 할당을 사용하지 않는다',
  'bad': r"""char *buf = malloc(len);   /* 단편화·할당 실패·누수 위험 */
read_into(buf, len);
free(buf);""",
  'good': r"""/* 정적/자동 저장기간 버퍼로 결정적 메모리 사용 */
#define MAX_LEN 256
char buf[MAX_LEN];
if (len <= MAX_LEN) {
    read_into(buf, len);
}""",
  'why':'안전필수 시스템에서 동적 할당은 단편화·비결정적 실패·누수를 야기한다. 컴파일 시 결정되는 정적/자동 버퍼로 대체한다.'},

 {'id':'Dir 4.13','cat':'Advisory · Undecidable · Dir',
  'title':'자원을 다루는 함수들은 적절히 짝지어 호출되도록 설계한다',
  'bad': r"""lock(&m);
if (cond) { return; }   /* 잠금 해제 없이 조기 반환 — 누수 */
work();
unlock(&m);""",
  'good': r"""lock(&m);
if (cond) { unlock(&m); return; }   /* 모든 경로에서 해제 */
work();
unlock(&m);""",
  'why':'획득(lock/open/alloc)과 해제(unlock/close/free)가 모든 실행 경로에서 짝지어지지 않으면 자원 누수·교착이 생긴다. 자원 함수는 대칭적으로 설계·사용한다.'},

 {'id':'Dir 4.14','cat':'Required · Undecidable · Dir',
  'title':'외부에서 들어온 값은 사용 전에 유효성을 검증한다',
  'bad': r"""int idx = read_index_from_packet();
table[idx] = value;     /* 외부 인덱스 범위 미검증 */""",
  'good': r"""int idx = read_index_from_packet();
if (idx >= 0 && idx < TABLE_SIZE) {
    table[idx] = value;
} else {
    handle_bad_input();
}""",
  'why':'신뢰할 수 없는 외부 입력(패킷·파일·사용자)을 검증 없이 인덱스·길이·포인터로 쓰면 경계 초과·인젝션이 발생한다. 사용 전 범위·형식을 검증한다.'},

 {'id':'Rule 1.3','cat':'Required · Undecidable · Rule',
  'title':'미정의(undefined) 또는 미명세(unspecified) 동작을 유발하지 않는다',
  'bad': r"""int i = 5;
i = i++ + ++i;      /* 시퀀스 포인트 사이 다중 수정 — 미정의 */""",
  'good': r"""int i = 5;
i = i + 1;
int j = i + (i + 1);   /* 한 표현식에서 i를 한 번만 수정 */""",
  'why':'한 시퀀스 포인트 사이에 같은 객체를 여러 번 수정하면 결과가 미정의다. 부작용을 분리해 명확한 평가 순서를 보장한다.'},

 {'id':'Rule 2.1','cat':'Required · Undecidable · Rule',
  'title':'도달 불가능한(unreachable) 코드를 두지 않는다',
  'bad': r"""int f(int x) {
    return x * 2;
    log("done");    /* return 이후 — 도달 불가 */
}""",
  'good': r"""int f(int x) {
    log("done");
    return x * 2;
}""",
  'why':'return/break 이후의 도달 불가 코드는 의도 오류의 신호이며 유지보수를 혼란스럽게 한다. 제거하거나 제어 흐름을 바로잡는다.'},

 {'id':'Rule 2.2','cat':'Required · Undecidable · Rule',
  'title':'죽은(dead) 코드 — 효과 없는 연산을 두지 않는다',
  'bad': r"""int total = compute();
total + 1;          /* 결과를 버림 — 효과 없는 문장 */
return total;""",
  'good': r"""int total = compute();
total = total + 1;   /* 결과를 실제로 사용 */
return total;""",
  'why':'결과를 사용하지 않는 연산은 로직 누락(대입 빠짐)을 의미할 때가 많다. 효과 없는 문장은 버그 신호로 보고 수정한다.'},

 {'id':'Rule 2.3','cat':'Advisory · Decidable · Rule',
  'title':'사용되지 않는 타입(typedef) 선언을 두지 않는다',
  'bad': r"""typedef unsigned int handle_t;   /* 어디서도 사용 안 함 */
typedef int status_t;
status_t run(void) { return 0; }""",
  'good': r"""typedef int status_t;
status_t run(void) { return 0; }""",
  'why':'쓰이지 않는 typedef는 코드를 어지럽히고 리팩터링 흔적일 수 있다. 미사용 타입 선언은 삭제한다.'},

 {'id':'Rule 2.7','cat':'Advisory · Decidable · Rule',
  'title':'함수의 사용되지 않는 매개변수를 두지 않는다',
  'bad': r"""int handler(int code, void *ctx) {
    return code * 2;     /* ctx 미사용 */
}""",
  'good': r"""int handler(int code, void *ctx) {
    (void)ctx;           /* 의도적 미사용 명시 */
    return code * 2;
}""",
  'why':'쓰지 않는 매개변수는 인터페이스 오류이거나 누락된 로직을 뜻할 수 있다. 콜백 등으로 시그니처가 고정이면 (void)캐스트로 의도를 명시한다.'},

 {'id':'Rule 3.1','cat':'Required · Decidable · Rule',
  'title':'주석 안에 /* 또는 // 문자열을 두지 않는다',
  'bad': r"""/* 이전 코드 /* 중첩 주석 */ 처럼 보임 */
x = 1;""",
  'good': r"""/* 이전 코드: 중첩 표기를 풀어서 작성 */
x = 1;""",
  'why':'주석 내 /* 는 중첩 주석으로 오인되어 의도치 않은 영역이 주석 처리될 수 있다. 주석 안에 주석 시작 문자를 넣지 않는다.'},

 {'id':'Rule 4.1','cat':'Required · Decidable · Rule',
  'title':'8진/16진 이스케이프 시퀀스는 명확히 종료한다',
  'bad': r"""const char *s = "\x41B";   /* \x41B 가 한 이스케이프로 해석될 수 있음 */""",
  'good': r"""const char *s = "\x41" "B";  /* 문자열 연결로 경계 명확화 */""",
  'why':'16진 이스케이프(\\x)는 뒤따르는 16진 문자를 계속 흡수해 의도와 다른 값이 된다. 인접 문자열 분리나 8진 3자리 표기로 경계를 명확히 한다.'},

 {'id':'Rule 5.1','cat':'Required · Decidable · Rule',
  'title':'외부 식별자는 유효 문자 범위 내에서 고유해야 한다',
  'bad': r"""int sensor_calibration_offset_a;
int sensor_calibration_offset_b;  /* 앞 31자가 동일 — 충돌 가능 */""",
  'good': r"""int calib_off_a;
int calib_off_b;     /* 짧고 고유한 외부 식별자 */""",
  'why':'일부 구현은 외부 식별자를 앞 31자로만 구분해, 긴 접두사를 공유하면 서로 다른 심볼이 충돌한다. 외부 연결 이름은 짧고 고유하게 짓는다.'},

 {'id':'Rule 5.3','cat':'Required · Decidable · Rule',
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지(shadow) 않게 한다',
  'bad': r"""int count = 0;
void f(void) {
    int count = 5;    /* 외부 count를 가림 */
    count++;          /* 어느 count? 혼동 */
}""",
  'good': r"""int g_count = 0;
void f(void) {
    int local_count = 5;
    local_count++;
}""",
  'why':'바깥 변수를 같은 이름으로 가리면 잘못된 객체를 수정하는 결함을 부른다. 내부 식별자는 바깥 이름과 다르게 짓는다.'},

 {'id':'Rule 5.6','cat':'Required · Decidable · Rule',
  'title':'typedef 이름은 고유한 식별자여야 한다',
  'bad': r"""typedef int counter;
void g(void) {
    int counter = 0;    /* typedef 이름을 변수로 재사용 */
}""",
  'good': r"""typedef int counter_t;
void g(void) {
    counter_t counter = 0;
}""",
  'why':'typedef 이름을 다른 식별자로 재사용하면 타입/변수 혼동과 가독성 저하를 부른다. typedef에는 _t 등 구별되는 고유 이름을 쓴다.'},

 {'id':'Rule 7.1','cat':'Required · Decidable · Rule',
  'title':'8진 상수(선행 0)를 사용하지 않는다',
  'bad': r"""int perm = 0755;     /* 8진수 — 의도와 다른 값으로 읽기 쉬움 */
int codes[] = {012, 015};""",
  'good': r"""int perm = 0x1ED;        /* 또는 493 (10진) */
int codes[] = {10, 13};""",
  'why':'선행 0이 붙은 정수는 8진수로 해석되어 010이 8이 되는 등 의도와 다른 값이 된다. 10진 또는 16진 표기를 쓴다.'},

 {'id':'Rule 7.2','cat':'Required · Decidable · Rule',
  'title':'unsigned 정수 상수에는 u/U 접미사를 붙인다',
  'bad': r"""uint16_t mask = 40000;   /* int 범위 초과분이 구현정의로 변환 */""",
  'good': r"""uint16_t mask = 40000u;  /* unsigned 의도 명시 */""",
  'why':'부호 없는 문맥에서 접미사 없는 상수는 부호 있는 int로 해석되어 의도치 않은 부호 변환·오버플로우를 부른다. u/U로 부호 없음을 명시한다.'},

 {'id':'Rule 7.3','cat':'Required · Decidable · Rule',
  'title':'정수 리터럴 접미사에 소문자 l을 쓰지 않는다',
  'bad': r"""long big = 100000l;   /* l 이 1과 혼동됨 */""",
  'good': r"""long big = 100000L;   /* 대문자 L */""",
  'why':'소문자 l 접미사는 숫자 1과 시각적으로 구분되지 않아 오독을 부른다. 항상 대문자 L/LL을 사용한다.'},

 {'id':'Rule 7.4','cat':'Required · Decidable · Rule',
  'title':'문자열 리터럴을 const 가 아닌 포인터에 대입하지 않는다',
  'bad': r"""char *msg = "READY";
msg[0] = 'r';     /* 리터럴 수정 — 미정의 동작 */""",
  'good': r"""const char *msg = "READY";   /* 읽기 전용 의도 명시 */
/* 수정이 필요하면 배열 사용: char buf[] = "READY"; */""",
  'why':'문자열 리터럴은 읽기 전용일 수 있어 수정 시 미정의 동작이다. const char *로 받아 수정을 컴파일 단계에서 차단한다.'},

 {'id':'Rule 8.1','cat':'Required · Decidable · Rule',
  'title':'타입은 명시적으로 지정한다(암시적 int 금지)',
  'bad': r"""static count = 0;     /* 타입 생략 → 암시적 int */
extern process(void);""",
  'good': r"""static int count = 0;
extern int process(void);""",
  'why':'타입을 생략한 암시적 int는 가독성을 해치고 표준에서 제거되었다. 모든 객체·함수에 타입을 명시한다.'},

 {'id':'Rule 8.2','cat':'Required · Decidable · Rule',
  'title':'함수는 매개변수 타입을 명시한 프로토타입 형식으로 선언한다',
  'bad': r"""int sum();          /* 매개변수 정보 없음 — 검사 불가 */
int r = sum(1, 2, 3);""",
  'good': r"""int sum(int a, int b);
int r = sum(1, 2);""",
  'why':'() 형태의 빈 매개변수 선언은 인자 개수·타입 검사를 막아 잘못된 호출을 허용한다. 항상 명시적 프로토타입(또는 void)을 쓴다.'},

 {'id':'Rule 8.3','cat':'Required · Decidable · Rule',
  'title':'동일 객체/함수의 모든 선언은 이름과 타입이 일치해야 한다',
  'bad': r"""/* a.h */ extern long counter;
/* b.c */ int counter;     /* 타입 불일치 */""",
  'good': r"""/* a.h */ extern long counter;
/* b.c */ long counter;""",
  'why':'선언과 정의의 타입이 다르면 링커가 잡지 못한 채 잘못된 크기로 접근해 손상이 일어난다. 공유 헤더로 단일 선언을 강제한다.'},

 {'id':'Rule 8.4','cat':'Required · Decidable · Rule',
  'title':'외부 연결 객체/함수는 정의 전에 호환되는 선언이 보여야 한다',
  'bad': r"""/* 헤더 없이 정의만 존재 */
int global_state = 0;
void update(void) { global_state++; }""",
  'good': r"""/* state.h */ extern int global_state;
/* state.c */
#include "state.h"
int global_state = 0;""",
  'why':'선언이 보이지 않는 외부 정의는 다른 파일에서 잘못된 타입으로 참조될 수 있다. 헤더에 선언을 두고 정의 파일이 이를 포함하게 한다.'},

 {'id':'Rule 8.6','cat':'Required · Decidable · Rule',
  'title':'외부 연결 식별자는 정확히 하나의 정의를 가진다',
  'bad': r"""/* config.h 에 정의가 들어가 여러 .c 에 중복 정의 */
int g_mode = 1;     /* 헤더에 정의 → 다중 정의 */""",
  'good': r"""/* config.h */ extern int g_mode;
/* config.c */ int g_mode = 1;   /* 정의는 한 곳만 */""",
  'why':'헤더에 외부 변수를 정의하면 포함하는 모든 번역단위에서 중복 정의되어 링크 오류·미정의 동작을 일으킨다. 헤더엔 선언, 정의는 한 파일에만 둔다.'},

 {'id':'Rule 8.8','cat':'Required · Decidable · Rule',
  'title':'내부 연결 객체/함수에는 static 을 일관되게 사용한다',
  'bad': r"""static int helper(void);   /* 선언은 static */
int helper(void) { return 1; }  /* 정의는 static 누락 */""",
  'good': r"""static int helper(void);
static int helper(void) { return 1; }""",
  'why':'static 사용이 선언과 정의에서 불일치하면 연결(linkage)이 모호해진다. 내부 연결 의도면 모든 곳에 static을 붙인다.'},

 {'id':'Rule 8.9','cat':'Advisory · Decidable · Rule',
  'title':'단일 함수에서만 쓰이는 객체는 블록 범위로 선언한다',
  'bad': r"""static int temp;     /* 파일 범위지만 한 함수에서만 사용 */
void f(void) { temp = compute(); use(temp); }""",
  'good': r"""void f(void) {
    int temp = compute();   /* 블록 범위로 한정 */
    use(temp);
}""",
  'why':'한 함수에서만 쓰는 변수를 파일 범위에 두면 불필요한 가시성·상태 공유로 오용 위험이 커진다. 사용 지점에 가장 가까운 블록 범위로 좁힌다.'},

 {'id':'Rule 8.11','cat':'Advisory · Decidable · Rule',
  'title':'외부 연결 배열 선언에는 크기를 명시한다',
  'bad': r"""extern int table[];   /* 크기 미상 — sizeof 불가, 경계검사 곤란 */""",
  'good': r"""extern int table[16];  /* 크기 명시 */""",
  'why':'크기 없는 외부 배열 선언은 sizeof·경계 검사를 불가능하게 한다. 선언에 요소 수를 명시해 일관성과 검사 가능성을 확보한다.'},

 {'id':'Rule 8.12','cat':'Required · Decidable · Rule',
  'title':'열거형 내 상수 값은 고유해야 한다',
  'bad': r"""enum { A = 1, B = 2, C = 2 };   /* B와 C 값 충돌 */""",
  'good': r"""enum { A = 1, B = 2, C = 3 };""",
  'why':'암시적·명시적 지정이 섞여 두 열거 상수가 같은 값을 가지면 분기·테이블 인덱싱이 어긋난다. 각 열거 상수 값을 고유하게 둔다.'},

 {'id':'Rule 8.14','cat':'Required · Decidable · Rule',
  'title':'restrict 한정자를 사용하지 않는다',
  'bad': r"""void copy(int *restrict dst, const int *restrict src, int n) {
    for (int i = 0; i < n; i++) { dst[i] = src[i]; }
}""",
  'good': r"""void copy(int *dst, const int *src, int n) {
    for (int i = 0; i < n; i++) { dst[i] = src[i]; }
}""",
  'why':'restrict는 별칭 없음을 컴파일러에 약속하지만, 약속이 깨지면 진단 없는 미정의 동작이 된다. 안전필수 코드에서는 사용을 피한다.'},

 {'id':'Rule 9.1','cat':'Mandatory · Undecidable · Rule',
  'title':'값이 설정되기 전의 객체를 읽지 않는다(미초기화 사용 금지)',
  'bad': r"""int sum;
for (int i = 0; i < n; i++) { sum += a[i]; }  /* sum 미초기화 */""",
  'good': r"""int sum = 0;
for (int i = 0; i < n; i++) { sum += a[i]; }""",
  'why':'미초기화 자동 객체의 값은 불확정이라 읽으면 미정의 동작이 된다. 사용 전 명시적으로 초기화한다.'},

 {'id':'Rule 9.2','cat':'Required · Decidable · Rule',
  'title':'집합체/공용체 초기화는 중괄호로 구조를 맞춘다',
  'bad': r"""int m[2][2] = {1, 2, 3, 4};   /* 평탄 초기화 — 구조 불명확 */""",
  'good': r"""int m[2][2] = { {1, 2}, {3, 4} };""",
  'why':'중첩 집합체를 평탄하게 초기화하면 의도한 구조와 어긋날 위험이 있다. 차원에 맞춰 중괄호를 명시해 매핑을 분명히 한다.'},

 {'id':'Rule 9.3','cat':'Required · Decidable · Rule',
  'title':'배열은 부분 초기화하지 않는다(모든 요소를 의도적으로 초기화)',
  'bad': r"""int v[5] = {1, 2};   /* 나머지 3개는 0 — 의도인지 불명확 */""",
  'good': r"""int v[5] = {1, 2, 0, 0, 0};   /* 모든 요소 명시 */""",
  'why':'부분 초기화는 나머지 0 초기화가 의도인지 실수인지 드러나지 않는다. 모든 요소를 명시하거나 명확한 관용표현을 쓴다.'},

 {'id':'Rule 9.4','cat':'Required · Decidable · Rule',
  'title':'집합체 초기화에서 같은 요소를 중복 초기화하지 않는다',
  'bad': r"""int a[3] = { [1] = 10, [1] = 20 };   /* 인덱스 1 중복 */""",
  'good': r"""int a[3] = { [1] = 20 };""",
  'why':'지정 초기자에서 같은 요소를 두 번 지정하면 앞 값이 조용히 덮어써져 의도 오류가 숨는다. 각 요소를 한 번만 초기화한다.'},

 {'id':'Rule 9.5','cat':'Required · Decidable · Rule',
  'title':'지정 초기자로 배열을 초기화할 때는 크기를 명시한다',
  'bad': r"""int codes[] = { [4] = 9 };   /* 크기를 초기자가 암묵 결정 */""",
  'good': r"""int codes[5] = { [4] = 9 };  /* 크기 명시 */""",
  'why':'지정 초기자가 배열 크기를 암묵 결정하면 의도한 크기와 달라질 수 있다. 배열 크기를 명시해 모호함을 없앤다.'},
]
