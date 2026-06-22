# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트1: Dir + Rule 1~9) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 더 긴 예제로 작성하고 KO/EN 이중언어(title_en/why_en) 제공.
대부분 self-contained 컴파일 가능 C 프로그램(int main 포함, compiles:True). Wandbox gcc-13.2.0
`-std=gnu11 -lm` 기준. 다중 번역단위·헤더 가드·중첩 주석처럼 단일 파일로 성립하지 않는 규칙은
초점 스니펫으로 두고 compiles 를 표시하지 않는다."""

RULES = [
 {'id':'Dir 1.1','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'구현정의(implementation-defined) 동작에 의존하는 부분은 문서화·이해되어야 한다',
  'title_en':'All implementation-defined behaviour relied upon must be documented and understood',
  'bad': r"""#include <stdio.h>
/* int 폭과 char 부호 부호성(signedness)을 가정 — 둘 다 구현정의 */
static int read_byte(void){ return 200; }   /* 0xC8 을 돌려준다고 가정 */
int main(void){
    int flags = ~0;                 /* int 폭(16/32/64?)을 가정한 전체 비트 마스크 */
    char c = (char)read_byte();     /* char 가 signed 면 200 이 음수가 됨 */
    if (c > 127) {                  /* signed char 환경에선 절대 참이 아님 */
        printf("high bit set\n");
    }
    printf("flags=%d\n", flags);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
static int read_byte(void){ return 200; }
int main(void){
    uint32_t flags = 0xFFFFFFFFu;        /* 폭이 고정된 타입 + 명시 상수 */
    unsigned char c = (unsigned char)read_byte();  /* 부호 명시 → 항상 0..255 */
    if (c > 127u) {                      /* 의도대로 동작 */
        printf("high bit set\n");
    }
    printf("flags=%u\n", flags);
    return 0;
}""",
  'why':'int 폭이나 char 부호성 같은 구현정의 동작에 암묵적으로 의존하면, 컴파일러·타깃이 바뀔 때 마스크가 잘리거나 비교가 항상 거짓이 되는 등 이식 시 결함이 발생한다. stdint.h의 고정폭 타입과 명시적 부호(unsigned char)로 의존을 제거하거나, 불가피하면 가정한 동작을 문서화한다.',
  'why_en':'Implicitly relying on implementation-defined behaviour such as the width of int or the signedness of char causes portability defects when the compiler or target changes — masks get truncated, comparisons become always-false. Remove the dependency with fixed-width types from stdint.h and explicit signedness, or document the assumption when unavoidable.'},

 {'id':'Dir 2.1','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'모든 소스 파일은 오류 없이 컴파일되어야 한다',
  'title_en':'All source files shall compile without any compilation errors',
  'bad': r"""#include <stdio.h>
/* #if 0 으로 가려둔 컴파일 불가 코드가 방치됨 — 되살리면 빌드가 깨진다 */
#if 0
int legacy_calc(void){
    return undefined_symbol * missing_factor();  /* 컴파일 안 되는 죽은 코드 */
}
#endif
int main(void){
    printf("build ok\n");
    return 0;
}""",
  'good': r"""#include <stdio.h>
/* 빌드에서 제외할 코드는 삭제하거나, 남길 경우 항상 컴파일 가능한 상태로 유지 */
static int legacy_calc(void){
    return 0;   /* 유지한다면 유효하게 — 또는 버전관리 이력으로만 보존 */
}
int main(void){
    printf("build ok: %d\n", legacy_calc());
    return 0;
}""",
  'why':'#if 0 이나 조건부 컴파일로 가려둔 깨진 코드는 빌드에서 빠져 있어 오류가 드러나지 않다가, 유지보수 중 되살아나는 순간 빌드를 깨뜨린다. 불필요한 코드는 삭제하고(이력은 버전관리에 남는다), 남길 코드는 항상 컴파일 가능한 상태로 둔다.',
  'why_en':'Broken code hidden behind #if 0 or conditional compilation stays out of the build, so its errors go unnoticed until someone re-enables it and breaks the build. Delete dead code (history lives in version control) and keep any retained code in a compilable state.'},

 {'id':'Dir 3.1','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'모든 코드는 요구사항으로 추적 가능해야 한다',
  'title_en':'All code shall be traceable to documented requirements',
  'bad': r"""#include <stdlib.h>
/* 어떤 요구사항에도 근거하지 않은 추적 불가 기능 — 심사·검증에서 누락된다 */
void maintenance_hook(const char *cmd){
    system(cmd);     /* 문서화되지 않은 임의 명령 실행 경로(백도어성) */
}
int main(void){
    /* 정상 흐름에서는 호출되지 않지만 코드에 남아 공격면이 된다 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
/* REQ-LOG-014: 운영 진단 로그를 파일에 기록한다 (요구사항 추적 ID 명시) */
static void write_diag_log(const char *msg){
    /* 요구사항에 정의된 기능만, 정의된 방식으로 구현 */
    printf("[DIAG] %s\n", msg);
}
int main(void){
    write_diag_log("system started");
    return 0;
}""",
  'why':'요구사항에 근거하지 않은 코드는 리뷰·검증·심사 대상에서 누락되기 쉬워 백도어나 불필요 기능의 온상이 된다. 각 기능을 요구사항 ID와 연계해 추적성을 유지하면, 정당화되지 않은 코드(특히 명령 실행·우회 경로)를 식별·제거할 수 있다.',
  'why_en':'Code not grounded in a requirement is easily missed by review, verification, and audit, becoming a haven for backdoors and unnecessary features. Linking each feature to a requirement ID keeps traceability, making unjustified code — especially command-execution or bypass paths — identifiable and removable.'},

 {'id':'Dir 4.1','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'런타임 실패(0 나눗셈·범위 초과·널 역참조 등) 가능성을 최소화한다',
  'title_en':'Run-time failures shall be minimized',
  'bad': r"""#include <stdio.h>
/* 분모 0, 널 포인터, 범위 초과 가능성을 검사하지 않는다 */
static int average(const int *a, int n){
    int sum = 0;
    for (int i = 0; i < n; i++) { sum += a[i]; }
    return sum / n;     /* n==0 이면 0 나눗셈(미정의), a==NULL 이면 널 역참조 */
}
int main(void){
    int data[3] = {10, 20, 30};
    printf("%d\n", average(data, 3));
    printf("%d\n", average(data, 0));   /* 0 나눗셈으로 비정상 종료 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
/* 연산 전에 분모·포인터·개수의 유효성을 확인하고 실패를 신호로 돌려준다 */
static int average(const int *a, int n, int *ok){
    if (a == NULL || n <= 0) { *ok = 0; return 0; }
    int sum = 0;
    for (int i = 0; i < n; i++) { sum += a[i]; }
    *ok = 1;
    return sum / n;
}
int main(void){
    int data[3] = {10, 20, 30};
    int ok;
    int r = average(data, 3, &ok);
    if (ok) printf("%d\n", r);
    (void)average(data, 0, &ok);
    if (!ok) printf("rejected empty input\n");
    return 0;
}""",
  'why':'0 나눗셈·널 역참조·배열 범위 초과는 모두 미정의 동작으로 비정상 종료나 보안 결함을 일으킨다. 연산 직전에 분모·포인터·인덱스의 유효성을 검사하고, 실패 시 명확한 오류 신호로 분기해 런타임 실패를 설계 단계에서 차단한다.',
  'why_en':'Division by zero, null dereference, and out-of-bounds indexing are all undefined behaviour that can crash the program or open security holes. Validate the divisor, pointer, and index immediately before use and branch on a clear failure signal, eliminating run-time failures by design.'},

 {'id':'Dir 4.3','cat':'Required · Decidable · Dir','compiles':True,
  'title':'어셈블리 언어는 캡슐화하고 격리한다',
  'title_en':'Assembly language shall be encapsulated and isolated',
  'bad': r"""#include <stdio.h>
static void do_work(void){ /* ... */ }
/* C 로직 한가운데 인라인 어셈블리가 산재 — 가독성·이식성·정적분석 저하 */
void busy_delay(void){
    int i = 100;
    __asm__ __volatile__("nop");
    while (i-- > 0) { do_work(); __asm__ __volatile__("nop"); }
}
int main(void){ busy_delay(); printf("done\n"); return 0; }""",
  'good': r"""#include <stdio.h>
static void do_work(void){ /* ... */ }
/* 어셈블리는 명명된 인라인 함수/매크로로 캡슐화해 한 곳에 격리 */
static inline void cpu_nop(void){ __asm__ __volatile__("nop"); }
void busy_delay(void){
    int i = 100;
    cpu_nop();
    while (i-- > 0) { do_work(); cpu_nop(); }   /* C 로직은 어셈블리에서 분리됨 */
}
int main(void){ busy_delay(); printf("done\n"); return 0; }""",
  'why':'C 로직 사이에 인라인 어셈블리가 흩어져 있으면 가독성, 이식성, 정적 분석 가능성이 모두 떨어지고 타깃 이식 시 손대야 할 곳이 산재한다. 어셈블리를 명명된 함수나 매크로로 캡슐화하면 플랫폼 의존 코드가 한 곳에 모여 교체·검증이 쉬워진다.',
  'why_en':'Inline assembly scattered through C logic hurts readability, portability, and static analysis, and spreads the places that must change when porting. Encapsulating assembly in named functions or macros collects platform-dependent code in one place, making it easy to replace and verify.'},

 {'id':'Dir 4.4','cat':'Advisory · Undecidable · Dir','compiles':True,
  'title':'코드 섹션을 주석 처리(comment-out)로 비활성화하지 않는다',
  'title_en':'Sections of code should not be "commented out"',
  'bad': r"""#include <stdio.h>
typedef struct { int v; } Data;
static void validate(Data *d){ (void)d; }
static void notify(Data *d){ (void)d; }
void process(Data *d){
    validate(d);
    /* transform(d);     // 임시로 막아둠 — 의도가 불명확
       commit(d); */
    notify(d);           /* 막아둔 코드가 정말 불필요한지, 잠시인지 알 수 없다 */
}
int main(void){ Data d = {1}; process(&d); printf("ok\n"); return 0; }""",
  'good': r"""#include <stdio.h>
typedef struct { int v; } Data;
static void validate(Data *d){ (void)d; }
static void notify(Data *d){ (void)d; }
#define FEATURE_TRANSFORM 0   /* 빌드 구성으로 의도를 명시 */
void process(Data *d){
    validate(d);
#if FEATURE_TRANSFORM
    transform(d);
    commit(d);
#endif
    notify(d);
}
int main(void){ Data d = {1}; process(&d); printf("ok\n"); return 0; }""",
  'why':'주석으로 막아둔 코드는 잠시 막은 것인지 폐기한 것인지 의도가 드러나지 않고, 시간이 지나면 노이즈가 된다. 정말 조건부로 필요한 코드는 빌드 구성(조건부 컴파일)으로 의도를 명시하고, 불필요하면 삭제한다(이력은 버전관리에 남는다).',
  'why_en':'Commented-out code does not reveal whether it is temporarily disabled or abandoned, and becomes noise over time. Express genuinely conditional code through build configuration (conditional compilation), and delete the rest — its history remains in version control.'},

 {'id':'Dir 4.5','cat':'Advisory · Undecidable · Dir','compiles':True,
  'title':'동일 네임스페이스의 식별자는 철자만 다른 혼동 이름을 피한다',
  'title_en':'Identifiers in the same name space should be typographically unambiguous',
  'bad': r"""#include <stdio.h>
int main(void){
    int total = 100;
    int totaI = 0;     /* 'l'(엘) vs 'I'(대문자 아이) — 시각적으로 동일 */
    int rn_count = 1;  /* 'rn' 이 'm' 처럼 보임 */
    int m_count  = 2;
    totaI = total + rn_count;   /* total 을 쓰려다 totaI 에 대입하는 실수 유발 */
    printf("%d %d %d\n", totaI, m_count, total);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int total_sum = 100;
    int total_avg = 0;        /* 시각적으로 명확히 구분 */
    int received_count = 1;
    int matched_count  = 2;
    total_avg = total_sum + received_count;
    printf("%d %d %d\n", total_avg, matched_count, total_sum);
    return 0;
}""",
  'why':'l/I/1, O/0, rn/m 처럼 글꼴에 따라 구별이 어려운 이름이 같은 네임스페이스에 있으면, 잘못된 변수를 참조·수정하는 결함을 부르고 코드 리뷰에서도 놓치기 쉽다. 한 네임스페이스 안에서는 충분히 구별되는 이름을 사용한다.',
  'why_en':'Names that are hard to tell apart in some fonts (l/I/1, O/0, rn/m) within one name space invite referencing or modifying the wrong variable and are easy to miss in review. Use names that are clearly distinguishable within a name space.'},

 {'id':'Dir 4.6','cat':'Advisory · Undecidable · Dir','compiles':True,
  'title':'기본 수치형 대신 크기·부호를 명시한 typedef를 사용한다',
  'title_en':'typedefs that indicate size and signedness should be used in place of the basic numerical types',
  'bad': r"""#include <stdio.h>
int main(void){
    long  timestamp = 0;   /* 플랫폼마다 32/64비트 — 2038 문제·오버플로우 */
    unsigned int crc = 0;  /* 16/32비트로 달라질 수 있어 마스크가 잘림 */
    short sample = 0;
    timestamp = 2147483647L + 1;   /* 32비트 long 이면 오버플로우 */
    crc = 0xDEADBEEF;              /* 16비트 int 환경이면 상위 비트 손실 */
    printf("%ld %u %d\n", timestamp, crc, sample);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
int main(void){
    int64_t  timestamp = 0;   /* 폭이 고정 → 동작이 플랫폼에 무관 */
    uint32_t crc = 0;
    int16_t  sample = 0;
    timestamp = (int64_t)2147483647 + 1;   /* 64비트로 안전 */
    crc = 0xDEADBEEFu;
    printf("%" PRId64 " %" PRIu32 " %d\n", timestamp, crc, sample);
    return 0;
}""",
  'why':'int/long/short의 폭은 구현정의라 같은 코드가 16/32/64비트 타깃에서 다르게 동작해 오버플로우·절단·플래그 손실을 일으킨다. stdint.h의 고정폭 typedef로 폭과 부호를 명시하면 산술·비트 연산이 플랫폼에 무관하게 동작한다.',
  'why_en':'The widths of int/long/short are implementation-defined, so the same code behaves differently on 16/32/64-bit targets, causing overflow, truncation, and lost flags. Fixed-width typedefs from stdint.h make width and signedness explicit so arithmetic and bit operations behave identically across platforms.'},

 {'id':'Dir 4.7','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'오류 정보를 반환하는 함수의 반환값은 반드시 검사한다',
  'title_en':'If a function returns error information, then that error information shall be tested',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/etc/hostname", "r");
    char buf[64];
    fgets(buf, sizeof buf, f);   /* fopen 실패(NULL) 미검사 → 널 역참조 */
    printf("%s", buf);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/etc/hostname", "r");
    if (f == NULL) {                 /* 실패를 즉시 검사하고 분기 */
        return 1;
    }
    char buf[64];
    if (fgets(buf, sizeof buf, f) != NULL) {
        printf("%s", buf);
    }
    fclose(f);
    return 0;
}""",
  'why':'fopen·malloc·read 처럼 실패를 반환값으로 알리는 함수의 결과를 무시하면, 실패 상태(NULL 등)에서 그대로 진행해 널 역참조나 손상된 데이터 사용으로 이어진다. 반환값을 즉시 검사해 실패 경로를 명확히 처리한다.',
  'why_en':'Ignoring the result of functions that report failure through a return value (fopen, malloc, read) lets execution continue from a failed state (e.g., NULL), leading to null dereference or use of corrupt data. Test the return value immediately and handle the failure path explicitly.'},

 {'id':'Dir 4.9','cat':'Advisory · Decidable · Dir','compiles':True,
  'title':'함수형 매크로보다 함수를 사용한다',
  'title_en':'A function should be used in preference to a function-like macro where they are interchangeable',
  'bad': r"""#include <stdio.h>
#define SQUARE(x) ((x)*(x))   /* 인자 다중 평가 + 타입 검사 없음 */
int main(void){
    int i = 3;
    int y = SQUARE(i++);      /* (i++)*(i++) — i 가 두 번 증가, 결과 미정의 */
    printf("y=%d i=%d\n", y, i);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static inline int square(int x){ return x * x; }  /* 1회 평가 + 타입 검사 */
int main(void){
    int i = 3;
    int y = square(i++);      /* i 는 정확히 한 번 증가 */
    printf("y=%d i=%d\n", y, i);
    return 0;
}""",
  'why':'함수형 매크로는 인자를 본문에 그대로 펼쳐 i++ 같은 부작용을 여러 번 평가하고 타입 검사도 하지 못해, 미정의 동작과 진단되지 않는 버그를 만든다. inline 함수는 동일한 성능에 인자를 한 번만 평가하고 타입 안전성까지 제공한다.',
  'why_en':'A function-like macro pastes its argument into the body, evaluating side effects like i++ multiple times and skipping type checking, producing undefined behaviour and silent bugs. An inline function gives the same performance while evaluating the argument once and enforcing type safety.'},

 {'id':'Dir 4.10','cat':'Required · Decidable · Dir',
  'title':'헤더 파일은 중복 포함을 방지(include guard)한다',
  'title_en':'Precautions shall be taken in order to prevent the contents of a header file being included more than once',
  'bad': r"""/* sensor.h — include guard 없음 */
typedef struct { int id; int raw; } Sensor;
int sensor_init(Sensor *s);

/* 다른 헤더가 sensor.h 를 또 포함하면 Sensor 재정의로 컴파일 오류:
   error: redefinition of 'struct Sensor' */""",
  'good': r"""/* sensor.h — #ifndef/#define 가드로 1회만 처리 */
#ifndef SENSOR_H
#define SENSOR_H

typedef struct { int id; int raw; } Sensor;
int sensor_init(Sensor *s);

#endif /* SENSOR_H */
/* 또는 컴파일러가 지원하면 파일 첫 줄에 #pragma once */""",
  'why':'include guard가 없는 헤더가 여러 경로로 중복 포함되면 타입·매크로가 재정의되어 컴파일 오류가 난다. #ifndef/#define/#endif 가드(또는 #pragma once)로 헤더 본문이 번역단위당 한 번만 처리되도록 보장한다.',
  'why_en':'A header without an include guard, included via multiple paths, redefines types and macros and fails to compile. An #ifndef/#define/#endif guard (or #pragma once) ensures the header body is processed only once per translation unit.'},

 {'id':'Dir 4.11','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'라이브러리 함수에 전달하는 인자의 유효성을 검사한다',
  'title_en':'The validity of values passed to library functions shall be checked',
  'bad': r"""#include <stdio.h>
#include <math.h>
static double rms(double x, double v){
    double r = sqrt(x);   /* x<0 이면 도메인 오류 → NaN */
    double l = log(v);    /* v<=0 이면 도메인 오류 → -inf/NaN */
    return r + l;
}
int main(void){
    printf("%f\n", rms(-1.0, 0.0));   /* NaN 전파 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <math.h>
static int rms(double x, double v, double *out){
    if (x < 0.0 || v <= 0.0) { return -1; }   /* 정의역(domain) 사전 검사 */
    *out = sqrt(x) + log(v);
    return 0;
}
int main(void){
    double out;
    if (rms(4.0, 1.0, &out) == 0) printf("%f\n", out);
    if (rms(-1.0, 0.0, &out) != 0) printf("rejected invalid domain\n");
    return 0;
}""",
  'why':'sqrt·log·memcpy 같은 라이브러리 함수는 인자가 정의역(domain)이나 길이·중첩 제약을 벗어나면 도메인 오류(NaN)나 미정의 동작을 일으킨다. 호출 전에 값의 범위·길이·별칭 여부를 검사하면 오류가 조용히 전파되는 것을 막는다.',
  'why_en':'Library functions like sqrt, log, and memcpy produce domain errors (NaN) or undefined behaviour when arguments fall outside their domain or length/overlap constraints. Checking ranges, lengths, and aliasing before the call prevents errors from propagating silently.'},

 {'id':'Dir 4.12','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'동적 메모리 할당을 사용하지 않는다',
  'title_en':'Dynamic memory allocation shall not be used',
  'bad': r"""#include <stdlib.h>
#include <string.h>
#include <stdio.h>
static void handle(const char *src, size_t len){
    char *buf = malloc(len);    /* 단편화·할당 실패·누수 위험(비결정적) */
    if (buf == NULL) return;
    memcpy(buf, src, len);
    printf("%.*s\n", (int)len, buf);
    /* free 누락 시 누수 — 안전필수 시스템에서 비결정적 실패 */
    free(buf);
}
int main(void){ handle("payload", 7); return 0; }""",
  'good': r"""#include <string.h>
#include <stdio.h>
#define MAX_LEN 256
static void handle(const char *src, size_t len){
    char buf[MAX_LEN];          /* 정적/자동 저장기간 — 결정적 메모리 */
    if (len > sizeof buf) { return; }   /* 용량 검사 */
    memcpy(buf, src, len);
    printf("%.*s\n", (int)len, buf);
}
int main(void){ handle("payload", 7); return 0; }""",
  'why':'안전필수·실시간 시스템에서 malloc/free는 힙 단편화, 비결정적 할당 시간, 할당 실패, 누수를 야기해 장기 가동 시 예측 불가능한 실패를 만든다. 컴파일 시 크기가 정해지는 정적/자동 버퍼로 대체하면 메모리 사용이 결정적이고 검증 가능해진다.',
  'why_en':'In safety-critical and real-time systems, malloc/free cause heap fragmentation, non-deterministic allocation time, allocation failure, and leaks, producing unpredictable failures over long uptimes. Replacing them with statically/automatically sized buffers makes memory use deterministic and verifiable.'},

 {'id':'Dir 4.13','cat':'Advisory · Undecidable · Dir','compiles':True,
  'title':'자원을 다루는 함수들은 적절히 짝지어 호출되도록 설계한다',
  'title_en':'Functions that operate on a resource should be called in an appropriate sequence',
  'bad': r"""#include <pthread.h>
#include <stdio.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static int g_state;
static int update(int cond){
    pthread_mutex_lock(&m);
    if (cond) { return -1; }    /* 잠금 해제 없이 조기 반환 — 영구 교착 유발 */
    g_state++;
    pthread_mutex_unlock(&m);
    return 0;
}
int main(void){ printf("%d\n", update(0)); return 0; }""",
  'good': r"""#include <pthread.h>
#include <stdio.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static int g_state;
static int update(int cond){
    pthread_mutex_lock(&m);
    if (cond) { pthread_mutex_unlock(&m); return -1; }  /* 모든 경로에서 해제 */
    g_state++;
    pthread_mutex_unlock(&m);
    return 0;
}
int main(void){ printf("%d\n", update(0)); return 0; }""",
  'why':'획득(lock/open/alloc)과 해제(unlock/close/free)가 모든 실행 경로(특히 조기 반환·예외 경로)에서 짝지어지지 않으면 자원 누수나 교착이 발생한다. 자원을 다루는 함수는 대칭적으로 호출되도록 설계하고, 모든 종료 경로에서 해제를 보장한다.',
  'why_en':'When acquire (lock/open/alloc) and release (unlock/close/free) are not paired on every path — especially early returns — resources leak or deadlock. Design resource functions to be called symmetrically and guarantee release on every exit path.'},

 {'id':'Dir 4.14','cat':'Required · Undecidable · Dir','compiles':True,
  'title':'외부에서 들어온 값은 사용 전에 유효성을 검증한다',
  'title_en':'The validity of values received from external sources shall be checked',
  'bad': r"""#include <stdio.h>
#define TABLE_SIZE 16
static int table[TABLE_SIZE];
static int read_index(void){ return 99; }   /* 외부(패킷/파일/사용자)에서 옴 */
int main(void){
    int idx = read_index();
    table[idx] = 1;     /* 외부 인덱스 범위 미검증 → 경계 밖 쓰기 */
    printf("ok\n");
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define TABLE_SIZE 16
static int table[TABLE_SIZE];
static int read_index(void){ return 99; }
int main(void){
    int idx = read_index();
    if (idx >= 0 && idx < TABLE_SIZE) {    /* 사용 전 범위 검증 */
        table[idx] = 1;
        printf("stored at %d\n", idx);
    } else {
        printf("rejected out-of-range index %d\n", idx);
    }
    return 0;
}""",
  'why':'패킷·파일·사용자 입력처럼 신뢰할 수 없는 외부 값을 검증 없이 인덱스·길이·포인터로 사용하면 버퍼 경계 초과, 인젝션, 정수 오버플로우로 이어진다. 신뢰 경계에서 값의 범위와 형식을 먼저 검증한 뒤에만 사용한다.',
  'why_en':'Using untrusted external values (packets, files, user input) as indices, lengths, or pointers without validation leads to buffer overruns, injection, and integer overflow. Validate range and format at the trust boundary before any use.'},

 {'id':'Rule 1.3','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'미정의(undefined) 또는 미명세(unspecified) 동작을 유발하지 않는다',
  'title_en':'There shall be no occurrence of undefined or critical unspecified behaviour',
  'bad': r"""#include <stdio.h>
int main(void){
    int i = 5;
    i = i++ + ++i;     /* 한 시퀀스 포인트 사이에서 i 를 여러 번 수정 — 미정의 */
    int a[3] = {0};
    int k = 0;
    a[k] = k++;        /* k 의 읽기/수정 순서 미명세 */
    printf("%d %d\n", i, a[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int i = 5;
    int next = i + 1;          /* 부작용을 분리해 평가 순서를 명확히 */
    i = i + next;
    int a[3] = {0};
    int k = 0;
    a[k] = k;                  /* 인덱스와 대입을 분리 */
    k++;
    printf("%d %d (k=%d)\n", i, a[0], k);
    return 0;
}""",
  'why':'한 시퀀스 포인트 사이에서 같은 객체를 여러 번 수정하거나, 수정과 별개의 읽기를 섞으면 결과가 미정의·미명세가 되어 컴파일러·최적화 수준마다 달라진다. 부작용(증가·대입)을 별도 문장으로 분리해 평가 순서를 명확히 한다.',
  'why_en':'Modifying the same object multiple times between sequence points, or mixing a modification with an unsequenced read, makes the result undefined or unspecified — varying by compiler and optimization level. Split side effects (increment, assignment) into separate statements to make evaluation order explicit.'},

 {'id':'Rule 2.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'도달 불가능한(unreachable) 코드를 두지 않는다',
  'title_en':'A project shall not contain unreachable code',
  'bad': r"""#include <stdio.h>
static int scale(int x){
    return x * 2;
    printf("scaling %d\n", x);   /* return 이후 — 절대 실행되지 않음 */
}
int main(void){ printf("%d\n", scale(21)); return 0; }""",
  'good': r"""#include <stdio.h>
static int scale(int x){
    printf("scaling %d\n", x);   /* 의도한 순서로 배치 */
    return x * 2;
}
int main(void){ printf("%d\n", scale(21)); return 0; }""",
  'why':'return·break·무조건 분기 이후에 놓인 도달 불가 코드는 제어 흐름을 잘못 작성했다는 신호이며, 의도한 부작용(로깅·정리)이 실행되지 않는 결함을 숨긴다. 도달 불가 코드는 제거하거나 흐름을 바로잡는다.',
  'why_en':'Unreachable code after return, break, or an unconditional branch signals mis-written control flow and hides a defect where intended side effects (logging, cleanup) never run. Remove unreachable code or fix the flow.'},

 {'id':'Rule 2.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'죽은(dead) 코드 — 효과 없는 연산을 두지 않는다',
  'title_en':'There shall be no dead code',
  'bad': r"""#include <stdio.h>
int main(void){
    int total = 10;
    total + 1;         /* 결과를 버림 — 'total = total + 1;' 의 누락일 가능성 */
    int n = 5;
    n == 6;            /* 비교 결과를 버림 — 'n = 6;' 오타일 가능성 */
    printf("%d %d\n", total, n);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int total = 10;
    total = total + 1;     /* 결과를 실제로 사용 */
    int n = 5;
    n = 6;
    printf("%d %d\n", total, n);
    return 0;
}""",
  'why':'결과를 사용하지 않는 연산(total + 1; / n == 6;)은 대입을 빠뜨린 오타일 때가 많아 로직 누락 버그를 가린다. 효과 없는 문장은 버그 신호로 보고 의도한 대입·호출로 수정한다.',
  'why_en':'Operations whose result is discarded (total + 1; / n == 6;) are often a missed assignment and mask logic-omission bugs. Treat statements with no effect as bug signals and fix them into the intended assignment or call.'},

 {'id':'Rule 2.3','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'사용되지 않는 타입(typedef) 선언을 두지 않는다',
  'title_en':'A project should not contain unused type declarations',
  'bad': r"""#include <stdio.h>
typedef unsigned int handle_t;   /* 어디서도 사용되지 않음 — 리팩터링 잔재 */
typedef int status_t;
static status_t run(void){ return 0; }
int main(void){ printf("%d\n", run()); return 0; }""",
  'good': r"""#include <stdio.h>
typedef int status_t;            /* 실제로 쓰이는 타입만 유지 */
static status_t run(void){ return 0; }
int main(void){ printf("%d\n", run()); return 0; }""",
  'why':'쓰이지 않는 typedef는 코드를 어지럽히고, 리팩터링 과정에서 무언가가 사라졌다는 흔적일 수 있어 오해를 부른다. 미사용 타입 선언은 삭제해 코드와 실제 사용을 일치시킨다.',
  'why_en':'Unused typedefs clutter the code and may be a leftover from refactoring that suggests something was removed, causing confusion. Delete unused type declarations to keep code aligned with actual use.'},

 {'id':'Rule 2.7','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'함수의 사용되지 않는 매개변수를 두지 않는다',
  'title_en':'There should be no unused parameters in functions',
  'bad': r"""#include <stdio.h>
/* 콜백 시그니처상 ctx 를 받지만 본문에서 쓰지 않음 — 누락 로직인지 불명확 */
static int on_event(int code, void *ctx){
    return code * 2;
}
int main(void){ printf("%d\n", on_event(21, NULL)); return 0; }""",
  'good': r"""#include <stdio.h>
static int on_event(int code, void *ctx){
    (void)ctx;          /* 의도적 미사용임을 명시 — 검토자에게 신호 */
    return code * 2;
}
int main(void){ printf("%d\n", on_event(21, NULL)); return 0; }""",
  'why':'사용되지 않는 매개변수는 인터페이스 설계 오류이거나 빠뜨린 로직을 뜻할 수 있다. 콜백처럼 시그니처가 고정이어서 불가피하면 (void) 캐스트로 의도적 미사용임을 명시해 검토자에게 신호를 준다.',
  'why_en':'An unused parameter may indicate an interface design error or omitted logic. When the signature is fixed (e.g., a callback), make the deliberate non-use explicit with a (void) cast to signal intent to reviewers.'},

 {'id':'Rule 3.1','cat':'Required · Decidable · Rule',
  'title':'주석 안에 /* 또는 // 문자열을 두지 않는다',
  'title_en':'The character sequences /* and // shall not be used within a comment',
  'bad': r"""/* 이전 구현 /* 임시 메모 */ 이 줄의 뒷부분은 코드로 해석됨 */
x = compute();
/* 위 줄: 첫 '*/' 에서 주석이 끝나 '이 줄의...' 가 코드가 되어 컴파일 오류 */""",
  'good': r"""/* 이전 구현 - 임시 메모: 중첩 표기를 풀어서 한 줄로 작성 */
x = compute();
/* 주석 시작 문자(슬래시-별표)를 주석 본문에 넣지 않는다 */""",
  'why':'주석 본문에 들어간 /* 는 일부 도구·사람에게 중첩 주석으로 오인되고, 먼저 나오는 */ 가 주석을 조기 종료시켜 그 뒤 텍스트가 코드로 해석되며 컴파일 오류나 의도치 않은 동작을 만든다. 주석 안에는 주석 시작 문자를 넣지 않는다.',
  'why_en':'A /* inside a comment body is misread as a nested comment by some tools and people, and the first */ ends the comment early so the following text is parsed as code, causing compile errors or unintended behaviour. Do not place comment-start sequences inside comments.'},

 {'id':'Rule 4.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'8진/16진 이스케이프 시퀀스는 명확히 종료한다',
  'title_en':'Octal and hexadecimal escape sequences shall be terminated',
  'bad': r"""#include <stdio.h>
int main(void){
    /* \x 는 뒤따르는 16진 문자를 계속 흡수 — "\x41B" 가 한 이스케이프로 해석될 수 있음 */
    const char *s = "\x41B";
    printf("len-ish: first=%d\n", (int)(unsigned char)s[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    /* 인접 문자열 분리로 이스케이프 경계를 명확히: 'A' 와 'B' */
    const char *s = "\x41" "B";
    printf("%s\n", s);   /* "AB" */
    return 0;
}""",
  'why':'16진 이스케이프 \\x 는 종료 규칙이 없어 뒤따르는 모든 16진 숫자를 흡수하므로, "\\x41B" 가 의도(A 뒤의 B)와 달리 하나의 큰 값으로 해석될 수 있다. 인접 문자열 리터럴로 분리하거나 8진 3자리 표기로 경계를 명확히 한다.',
  'why_en':'The hex escape \\x has no terminator and absorbs all following hex digits, so "\\x41B" may be read as one large value rather than the intended A followed by B. Make the boundary explicit by splitting into adjacent string literals or using three-digit octal.'},

 {'id':'Rule 5.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'외부 식별자는 유효 문자 범위 내에서 고유해야 한다',
  'title_en':'External identifiers shall be distinct',
  'bad': r"""#include <stdio.h>
/* 일부 구형 링커는 외부 식별자를 앞 31자로만 구분 → 아래 둘이 충돌 가능 */
int sensor_calibration_offset_alpha = 1;
int sensor_calibration_offset_beta  = 2;   /* 앞 31자 'sensor_calibration_offset_' 공유 */
int main(void){ printf("%d %d\n", sensor_calibration_offset_alpha, sensor_calibration_offset_beta); return 0; }""",
  'good': r"""#include <stdio.h>
int calib_off_alpha = 1;    /* 짧고 앞부분부터 고유한 외부 식별자 */
int calib_off_beta  = 2;
int main(void){ printf("%d %d\n", calib_off_alpha, calib_off_beta); return 0; }""",
  'why':'표준은 외부 연결 식별자의 구분을 최소 31자까지만 보장하므로, 긴 공통 접두사를 공유하는 이름들은 일부 구현에서 동일 심볼로 취급되어 조용히 충돌한다. 외부 식별자는 짧게, 앞부분부터 서로 구별되도록 짓는다.',
  'why_en':'The Standard only guarantees external identifiers are distinguished up to 31 characters, so names sharing a long common prefix can be treated as the same symbol on some implementations and silently collide. Keep external identifiers short and distinct from the start.'},

 {'id':'Rule 5.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'내부 범위 식별자가 외부 범위 식별자를 가리지(shadow) 않게 한다',
  'title_en':'An identifier declared in an inner scope shall not hide an identifier declared in an outer scope',
  'bad': r"""#include <stdio.h>
static int count = 0;        /* 파일 범위 카운터 */
static void tick(void){
    int count = 5;           /* 바깥 count 를 가림(shadow) */
    count++;                 /* 어느 count? 전역은 갱신되지 않는다 */
    printf("local=%d\n", count);
}
int main(void){ tick(); printf("global=%d\n", count); return 0; }""",
  'good': r"""#include <stdio.h>
static int g_count = 0;      /* 전역은 접두사로 구분 */
static void tick(void){
    int local_count = 5;     /* 바깥 이름과 다르게 */
    local_count++;
    g_count++;               /* 의도가 명확 */
    printf("local=%d\n", local_count);
}
int main(void){ tick(); printf("global=%d\n", g_count); return 0; }""",
  'why':'안쪽 범위에서 바깥 변수와 같은 이름을 선언하면(shadowing) 어느 객체를 쓰는지 혼동되어, 전역을 갱신하려다 지역만 바꾸는 결함을 만든다. 내부 식별자는 바깥 이름과 다르게(예: 접두사) 지어 가림을 방지한다.',
  'why_en':'Declaring an inner-scope name identical to an outer variable (shadowing) confuses which object is used, causing defects where a global is meant to be updated but only the local changes. Name inner identifiers differently (e.g., with a prefix) to avoid hiding.'},

 {'id':'Rule 5.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'typedef 이름은 고유한 식별자여야 한다',
  'title_en':'A typedef name shall be a unique identifier',
  'bad': r"""#include <stdio.h>
typedef int counter;     /* 타입 이름 'counter' */
static int run(void){
    int counter = 0;     /* 같은 이름을 변수로 재사용 — 타입/변수 혼동 */
    counter += 3;
    return counter;
}
int main(void){ printf("%d\n", run()); return 0; }""",
  'good': r"""#include <stdio.h>
typedef int counter_t;   /* _t 접미사로 타입임을 구별 */
static int run(void){
    counter_t counter = 0;   /* 타입과 변수 이름이 명확히 구분 */
    counter += 3;
    return counter;
}
int main(void){ printf("%d\n", run()); return 0; }""",
  'why':'typedef 이름을 변수·함수 등 다른 식별자로 재사용하면 같은 이름이 문맥에 따라 타입도 되고 객체도 되어 가독성과 정적 분석이 모두 저하된다. typedef에는 _t 같은 구별되는 고유 이름을 부여한다.',
  'why_en':'Reusing a typedef name as another identifier (variable, function) makes the same name mean a type in one context and an object in another, hurting readability and static analysis. Give typedefs a distinct, unique name such as a _t suffix.'},

 {'id':'Rule 7.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'8진 상수(선행 0)를 사용하지 않는다',
  'title_en':'Octal constants shall not be used',
  'bad': r"""#include <stdio.h>
int main(void){
    int perm = 0755;            /* 8진수 493 — 십진 755 로 오독하기 쉬움 */
    int codes[2] = {012, 015};  /* 10, 13 인데 12, 15 로 보임 */
    printf("%d %d %d\n", perm, codes[0], codes[1]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int perm = 493;             /* 십진으로 명확히 (또는 0x1ED) */
    int codes[2] = {10, 13};
    printf("%d %d %d\n", perm, codes[0], codes[1]);
    return 0;
}""",
  'why':'선행 0이 붙은 정수 리터럴은 8진수로 해석되어 010이 8이 되고 0755가 493이 되는 등, 십진으로 오독하기 쉬워 권한 비트·코드 값 설정에서 미묘한 버그를 만든다. 십진 또는 명시적 16진(0x) 표기를 사용한다.',
  'why_en':'An integer literal with a leading 0 is interpreted as octal (010 is 8, 0755 is 493), which is easily misread as decimal and produces subtle bugs in permission bits and code values. Use decimal or explicit hexadecimal (0x) notation.'},

 {'id':'Rule 7.2','cat':'Required · Decidable · Rule','compiles':True,
  'title':'unsigned 정수 상수에는 u/U 접미사를 붙인다',
  'title_en':'A "u" or "U" suffix shall be applied to all integer constants of unsigned type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t mask = 40000;     /* 40000 은 (16비트 환경에서) int 범위를 넘어 구현정의 변환 */
    uint32_t big  = 0x80000000;  /* 부호 있는 int 로 해석되어 음수 의미가 섞일 수 있음 */
    printf("%u %u\n", mask, big);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t mask = 40000u;     /* unsigned 의도 명시 */
    uint32_t big  = 0x80000000u;
    printf("%u %u\n", mask, big);
    return 0;
}""",
  'why':'부호 없는 문맥에서 접미사 없는 정수 상수는 부호 있는 int로 먼저 해석되어, 범위를 넘으면 구현정의 변환이나 의도치 않은 부호 확장·오버플로우를 일으킨다. u/U 접미사로 상수의 부호 없음을 명시한다.',
  'why_en':'In an unsigned context, an integer constant without a suffix is first interpreted as signed int, so values out of range undergo implementation-defined conversion or unintended sign extension/overflow. Apply a u/U suffix to make the constant explicitly unsigned.'},

 {'id':'Rule 7.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'정수 리터럴 접미사에 소문자 l을 쓰지 않는다',
  'title_en':'The lowercase character "l" shall not be used in a literal suffix',
  'bad': r"""#include <stdio.h>
int main(void){
    long big = 100000l;     /* 끝의 'l' 이 숫자 '1' 과 구분되지 않음 (1000001?) */
    long long huge = 5ll;   /* 'll' 도 마찬가지로 오독 위험 */
    printf("%ld %lld\n", big, huge);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    long big = 100000L;     /* 대문자 L — 명확 */
    long long huge = 5LL;
    printf("%ld %lld\n", big, huge);
    return 0;
}""",
  'why':'소문자 l 접미사는 글꼴에 따라 숫자 1과 거의 구분되지 않아 100000l 이 1000001 처럼 오독되는 등 값 자체를 잘못 읽게 만든다. 정수 리터럴 접미사는 항상 대문자 L/LL을 사용한다.',
  'why_en':'A lowercase l suffix is nearly indistinguishable from the digit 1 in many fonts, so 100000l can be misread as 1000001, causing the value itself to be misread. Always use uppercase L/LL for integer literal suffixes.'},

 {'id':'Rule 7.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'문자열 리터럴을 const 가 아닌 포인터에 대입하지 않는다',
  'title_en':'A string literal shall not be assigned to an object unless it has const-qualified type',
  'bad': r"""#include <stdio.h>
int main(void){
    char *msg = "READY";   /* 비-const 포인터로 리터럴을 가리킴 */
    msg[0] = 'r';          /* 읽기 전용 리터럴 수정 — 미정의 동작(흔히 크래시) */
    printf("%s\n", msg);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    const char *msg = "READY";   /* 읽기 전용 의도를 타입으로 명시 */
    /* 수정이 필요하면 수정 가능한 배열을 별도로 둔다 */
    char editable[] = "READY";
    editable[0] = 'r';
    printf("%s %s\n", msg, editable);
    return 0;
}""",
  'why':'문자열 리터럴은 읽기 전용 메모리에 놓일 수 있어 수정하면 미정의 동작(흔히 세그폴트)이 된다. 리터럴은 const char *로 받아 컴파일 단계에서 수정을 차단하고, 변경이 필요하면 별도의 수정 가능한 배열을 사용한다.',
  'why_en':'A string literal may reside in read-only memory, so modifying it is undefined behaviour (often a segfault). Receive literals as const char * to block modification at compile time, and use a separate modifiable array when changes are needed.'},

 {'id':'Rule 8.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'타입은 명시적으로 지정한다(암시적 int 금지)',
  'title_en':'Types shall be explicitly specified',
  'bad': r"""#include <stdio.h>
static count = 0;          /* 타입 생략 → 암시적 int (가독성 저하, 표준에서 제거됨) */
static incr(void){ return ++count; }
int main(void){ printf("%d\n", incr()); return 0; }""",
  'good': r"""#include <stdio.h>
static int count = 0;      /* 모든 객체·함수에 타입 명시 */
static int incr(void){ return ++count; }
int main(void){ printf("%d\n", incr()); return 0; }""",
  'why':'타입을 생략한 암시적 int 선언은 의도가 불명확하고 최신 C 표준(C99 이후)에서 제거되어 컴파일러마다 경고·오류로 다르게 처리된다. 모든 객체와 함수에 타입을 명시해 이식성과 가독성을 확보한다.',
  'why_en':'Implicit-int declarations that omit the type are unclear and were removed in modern C (since C99), so compilers treat them inconsistently as warnings or errors. Specify the type on every object and function for portability and readability.'},

 {'id':'Rule 8.2','cat':'Required · Decidable · Rule','compiles':True,
  'title':'함수는 매개변수 타입을 명시한 프로토타입 형식으로 선언한다',
  'title_en':'Function types shall be in prototype form with named parameters',
  'bad': r"""#include <stdio.h>
static int sum();          /* 매개변수 정보 없음 — 인자 개수·타입 검사 불가 */
static int sum(a, b) int a; int b; { return a + b; }  /* 구형 K&R 정의 */
int main(void){
    printf("%d\n", sum(1, 2, 3));   /* 인자 3개여도 진단되지 않음 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int sum(int a, int b);      /* 명시적 프로토타입 */
static int sum(int a, int b){ return a + b; }
int main(void){
    printf("%d\n", sum(1, 2));      /* 잘못된 인자 수는 컴파일 단계에서 진단 */
    return 0;
}""",
  'why':'() 형태의 빈 매개변수 선언이나 K&R 구형 정의는 인자의 개수·타입 검사를 막아 잘못된 호출을 컴파일러가 잡지 못하게 한다. 모든 함수를 명시적 프로토타입(인자 없음은 void) 형식으로 선언·정의해 호출 검사를 받게 한다.',
  'why_en':'An empty () parameter declaration or old K&R definition disables checking of argument count and type, so the compiler cannot catch wrong calls. Declare and define every function in explicit prototype form (use void for no parameters) so calls are checked.'},

 {'id':'Rule 8.3','cat':'Required · Decidable · Rule',
  'title':'동일 객체/함수의 모든 선언은 이름과 타입이 일치해야 한다',
  'title_en':'All declarations of an object or function shall use the same names and type qualifiers',
  'bad': r"""/* a.h */
extern long counter;          /* long 으로 선언 */

/* b.c */
int counter = 0;              /* int 로 정의 — 타입 불일치 */
/* 링커가 잡지 못한 채, 다른 파일에서 long 으로 4/8바이트 접근하면 인접 메모리 손상 */""",
  'good': r"""/* a.h */
extern long counter;

/* b.c */
#include "a.h"
long counter = 0;             /* 선언과 정의의 타입 일치 — 공유 헤더로 강제 */""",
  'why':'한 객체·함수의 선언과 정의가 파일마다 타입이 다르면, 컴파일러는 단일 파일만 보므로 불일치를 잡지 못하고 잘못된 크기·해석으로 접근해 메모리 손상이 일어난다. 공유 헤더에 단일 선언을 두고 정의 파일이 이를 포함하게 해 일치를 강제한다.',
  'why_en':'When an object/function is declared and defined with different types across files, the compiler sees only one file and cannot catch the mismatch, leading to access with the wrong size/interpretation and memory corruption. Put a single declaration in a shared header that the defining file includes to enforce agreement.'},

 {'id':'Rule 8.4','cat':'Required · Decidable · Rule',
  'title':'외부 연결 객체/함수는 정의 전에 호환되는 선언이 보여야 한다',
  'title_en':'A compatible declaration shall be visible when an object or function with external linkage is defined',
  'bad': r"""/* state.c — 헤더 없이 외부 연결 정의만 존재 */
int global_state = 0;             /* 다른 파일이 이를 어떤 타입으로 참조할지 강제되지 않음 */
void update(void){ global_state++; }
/* 다른 .c 가 'extern short global_state;' 로 잘못 선언해도 막을 수 없다 */""",
  'good': r"""/* state.h */
extern int global_state;
void update(void);

/* state.c */
#include "state.h"               /* 정의 시 선언이 보이므로 불일치를 컴파일러가 검출 */
int global_state = 0;
void update(void){ global_state++; }""",
  'why':'외부 연결 정의 시 호환 선언이 보이지 않으면, 다른 번역단위가 그 객체·함수를 잘못된 타입으로 선언해 참조해도 컴파일러가 검출하지 못한다. 헤더에 선언을 두고 정의 파일이 포함하면, 정의-선언 불일치가 컴파일 단계에서 잡힌다.',
  'why_en':'If no compatible declaration is visible when an externally linked object/function is defined, the compiler cannot detect another translation unit declaring and referencing it with the wrong type. Putting the declaration in a header that the defining file includes catches definition/declaration mismatches at compile time.'},

 {'id':'Rule 8.6','cat':'Required · Decidable · Rule',
  'title':'외부 연결 식별자는 정확히 하나의 정의를 가진다',
  'title_en':'An identifier with external linkage shall have exactly one external definition',
  'bad': r"""/* config.h — 헤더에 '정의'가 들어감 */
int g_mode = 1;                   /* 이 헤더를 포함하는 모든 .c 에서 중복 정의 */

/* a.c: #include "config.h"   →  g_mode 정의 1 */
/* b.c: #include "config.h"   →  g_mode 정의 2  → 링크 오류(다중 정의) */""",
  'good': r"""/* config.h — 헤더에는 '선언'만 */
extern int g_mode;

/* config.c — 정의는 단 한 곳 */
#include "config.h"
int g_mode = 1;""",
  'why':'헤더에 변수 정의(초기화 포함)를 두면 그 헤더를 포함하는 모든 번역단위에서 같은 심볼이 중복 정의되어 링크 오류나 미정의 동작이 발생한다. 헤더에는 extern 선언만 두고, 초기화 정의는 정확히 하나의 소스 파일에만 둔다.',
  'why_en':'Placing a variable definition (with initializer) in a header causes the same symbol to be defined in every translation unit that includes it, producing link errors or undefined behaviour. Keep only extern declarations in headers and put the defining initialization in exactly one source file.'},

 {'id':'Rule 8.8','cat':'Required · Decidable · Rule',
  'title':'내부 연결 객체/함수에는 static 을 일관되게 사용한다',
  'title_en':'The static storage class specifier shall be used consistently',
  'bad': r"""/* 선언은 static, 정의는 static 누락 — 연결(linkage)이 모호해짐 */
static int helper(int x);          /* 내부 연결 의도 */
int helper(int x){ return x + 1; } /* 정의에서 static 누락 → 일부 컴파일러가 외부 연결로 처리 */""",
  'good': r"""static int helper(int x);          /* 선언 */
static int helper(int x){ return x + 1; }  /* 정의 — static 일관 적용 */
/* 내부 연결 의도가 모든 선언/정의에서 일치 */""",
  'why':'같은 식별자의 선언과 정의에서 static 사용이 일치하지 않으면 내부/외부 연결이 모호해져, 컴파일러마다 심볼 가시성이 달라지고 이름 충돌·의도치 않은 노출이 생긴다. 내부 연결 의도면 모든 선언과 정의에 static을 일관되게 붙인다.',
  'why_en':'Inconsistent use of static between an identifier’s declaration and definition makes internal/external linkage ambiguous, so symbol visibility varies by compiler and causes name clashes or unintended exposure. Apply static consistently to all declarations and the definition when internal linkage is intended.'},

 {'id':'Rule 8.9','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'단일 함수에서만 쓰이는 객체는 블록 범위로 선언한다',
  'title_en':'An object should be defined at block scope if its identifier only appears in a single function',
  'bad': r"""#include <stdio.h>
static int temp;            /* 파일 범위지만 오직 compute() 에서만 사용 */
static int compute(void){
    temp = 21 * 2;          /* 불필요한 가시성·상태 공유로 오용 위험 */
    return temp;
}
int main(void){ printf("%d\n", compute()); return 0; }""",
  'good': r"""#include <stdio.h>
static int compute(void){
    int temp = 21 * 2;      /* 사용 지점에 가장 가까운 블록 범위로 한정 */
    return temp;
}
int main(void){ printf("%d\n", compute()); return 0; }""",
  'why':'한 함수에서만 쓰는 변수를 파일 범위에 두면 다른 코드에서 접근·수정할 수 있는 불필요한 가시성과 함수 호출 간 상태 유지가 생겨 오용과 재진입 결함을 부른다. 사용 지점에 가장 가까운 블록 범위로 선언 범위를 좁힌다.',
  'why_en':'Declaring a variable used by only one function at file scope creates unnecessary visibility (other code can touch it) and state retained across calls, inviting misuse and reentrancy defects. Narrow the declaration to the innermost block scope nearest its use.'},

 {'id':'Rule 8.11','cat':'Advisory · Decidable · Rule',
  'title':'외부 연결 배열 선언에는 크기를 명시한다',
  'title_en':'When an array with external linkage is declared, its size should be explicitly specified',
  'bad': r"""/* table.h */
extern int table[];          /* 크기 미상 — sizeof(table) 불가, 경계 검사 곤란 */

/* user.c 에서 for (i=0; i<sizeof table/sizeof table[0]; i++) 가 동작하지 않음 */""",
  'good': r"""/* table.h */
#define TABLE_SIZE 16
extern int table[TABLE_SIZE]; /* 크기 명시 → sizeof·경계 검사 가능 */

/* table.c */
int table[TABLE_SIZE];""",
  'why':'크기 없는 외부 배열 선언(extern int a[];)은 다른 번역단위에서 sizeof로 요소 수를 알 수 없게 해 경계 검사·반복을 불가능하게 만든다. 외부 배열 선언에 요소 수를 명시하면 일관성과 경계 검사 가능성이 확보된다.',
  'why_en':'A sizeless external array declaration (extern int a[];) prevents other translation units from learning the element count via sizeof, making bounds checks and iteration impossible. Specifying the element count in the external declaration restores consistency and checkability.'},

 {'id':'Rule 8.12','cat':'Required · Decidable · Rule','compiles':True,
  'title':'열거형 내 상수 값은 고유해야 한다',
  'title_en':'Within an enumerator list, the value of an implicitly-specified enumeration constant shall be unique',
  'bad': r"""#include <stdio.h>
/* 명시/암시 지정이 섞여 두 상수가 같은 값을 갖게 됨 */
enum State { S_IDLE = 1, S_RUN = 2, S_WAIT, S_STOP = 3 };
/* S_WAIT 는 암시적으로 3 → S_STOP(3) 과 충돌: switch/테이블 인덱싱이 어긋남 */
int main(void){ printf("%d %d\n", S_WAIT, S_STOP); return 0; }""",
  'good': r"""#include <stdio.h>
enum State { S_IDLE = 1, S_RUN = 2, S_WAIT = 3, S_STOP = 4 };  /* 값 고유 */
int main(void){ printf("%d %d\n", S_WAIT, S_STOP); return 0; }""",
  'why':'명시적 값과 암시적(앞 값+1) 지정이 섞이면 두 열거 상수가 우연히 같은 값을 가질 수 있고, 이 경우 switch 분기나 값-기반 테이블 인덱싱이 의도와 다르게 동작한다. 각 열거 상수의 값이 고유하도록 명시한다.',
  'why_en':'Mixing explicit values with implicit (previous+1) ones can give two enumerators the same value, causing switch branches or value-based table indexing to behave unexpectedly. Ensure each enumerator has a unique value, specifying them explicitly.'},

 {'id':'Rule 8.14','cat':'Required · Decidable · Rule','compiles':True,
  'title':'restrict 한정자를 사용하지 않는다',
  'title_en':'The restrict type qualifier shall not be used',
  'bad': r"""#include <stdio.h>
/* restrict 는 '별칭 없음' 을 컴파일러에 약속 — 약속이 깨지면 진단 없는 미정의 동작 */
static void merge(int *restrict dst, const int *restrict src, int n){
    for (int i = 0; i < n; i++) { dst[i] += src[i]; }
}
int main(void){
    int a[3] = {1, 2, 3};
    merge(a, a, 3);   /* dst 와 src 가 겹침 → restrict 위반, 미정의 동작 */
    printf("%d %d %d\n", a[0], a[1], a[2]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void merge(int *dst, const int *src, int n){  /* restrict 없이 안전 */
    for (int i = 0; i < n; i++) { dst[i] += src[i]; }
}
int main(void){
    int a[3] = {1, 2, 3};
    merge(a, a, 3);   /* 겹쳐도 정의된 동작 */
    printf("%d %d %d\n", a[0], a[1], a[2]);
    return 0;
}""",
  'why':'restrict 는 두 포인터가 같은 메모리를 가리키지 않는다는 약속을 컴파일러에 주어 최적화를 허용하지만, 호출자가 이 약속을 어기면 컴파일러가 진단하지 못하는 미정의 동작이 발생한다. 안전필수 코드에서는 restrict 사용을 피해 이런 함정을 제거한다.',
  'why_en':'restrict promises the compiler that two pointers never alias, enabling optimizations, but if the caller breaks that promise the result is undefined behaviour the compiler cannot diagnose. Avoid restrict in safety-critical code to remove this trap.'},

 {'id':'Rule 9.1','cat':'Mandatory · Undecidable · Rule','compiles':True,
  'title':'값이 설정되기 전의 객체를 읽지 않는다(미초기화 사용 금지)',
  'title_en':'The value of an object with automatic storage duration shall not be read before it has been set',
  'bad': r"""#include <stdio.h>
static int total(const int *a, int n){
    int sum;        /* 미초기화 — 불확정 값 */
    for (int i = 0; i < n; i++) { sum += a[i]; }  /* sum 을 설정 전에 읽음 */
    return sum;
}
int main(void){ int d[3] = {1,2,3}; printf("%d\n", total(d, 3)); return 0; }""",
  'good': r"""#include <stdio.h>
static int total(const int *a, int n){
    int sum = 0;    /* 사용 전 명시적 초기화 */
    for (int i = 0; i < n; i++) { sum += a[i]; }
    return sum;
}
int main(void){ int d[3] = {1,2,3}; printf("%d\n", total(d, 3)); return 0; }""",
  'why':'자동 저장기간(지역) 객체는 자동으로 0이 되지 않으므로, 초기화 전에 읽으면 스택에 남은 불확정 값을 사용하게 되어 미정의 동작과 재현 어려운 버그를 만든다. 모든 객체를 사용 전에 명시적으로 초기화한다.',
  'why_en':'Objects with automatic (local) storage are not zeroed automatically, so reading them before initialization uses indeterminate leftover stack values — undefined behaviour and hard-to-reproduce bugs. Initialize every object explicitly before use.'},

 {'id':'Rule 9.2','cat':'Required · Decidable · Rule','compiles':True,
  'title':'집합체/공용체 초기화는 중괄호로 구조를 맞춘다',
  'title_en':'The initializer for an aggregate or union shall be enclosed in braces',
  'bad': r"""#include <stdio.h>
int main(void){
    int m[2][2] = {1, 2, 3, 4};   /* 평탄 초기화 — 행/열 구조가 코드에 드러나지 않음 */
    printf("%d %d\n", m[0][1], m[1][0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int m[2][2] = { {1, 2}, {3, 4} };  /* 차원에 맞춰 중괄호 — 매핑이 명확 */
    printf("%d %d\n", m[0][1], m[1][0]);
    return 0;
}""",
  'why':'중첩 집합체를 평탄한 목록으로 초기화하면 어떤 값이 어느 차원·필드로 가는지 코드만 보고는 알 수 없어 유지보수 중 잘못된 매핑이 끼어든다. 차원·구조에 맞춰 중괄호를 명시하면 초기값과 구조의 대응이 분명해진다.',
  'why_en':'Initializing a nested aggregate with a flat list hides which value maps to which dimension or field, letting wrong mappings slip in during maintenance. Matching braces to the dimensions/structure makes the correspondence between values and structure explicit.'},

 {'id':'Rule 9.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'배열은 부분 초기화하지 않는다(모든 요소를 의도적으로 초기화)',
  'title_en':'Arrays shall not be partially initialized',
  'bad': r"""#include <stdio.h>
int main(void){
    int v[5] = {1, 2};   /* 나머지 3개가 0 — 의도인지 실수인지 코드에 드러나지 않음 */
    int s = 0;
    for (int i = 0; i < 5; i++) { s += v[i]; }
    printf("%d\n", s);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int v[5] = {1, 2, 0, 0, 0};   /* 모든 요소를 명시 — 0 이 의도임이 분명 */
    int s = 0;
    for (int i = 0; i < 5; i++) { s += v[i]; }
    printf("%d\n", s);
    return 0;
}""",
  'why':'배열을 일부만 초기화하면 나머지 요소가 0으로 채워지는 것이 의도된 설계인지 빠뜨린 실수인지 코드만으로 알 수 없어 검토·유지보수에서 오해를 부른다. 모든 요소를 명시하거나 전체 0 초기화처럼 의도가 분명한 관용표현을 쓴다.',
  'why_en':'Partially initializing an array leaves it unclear whether the zero-filled remainder is intended or an omission, causing misunderstanding in review and maintenance. Specify all elements, or use an unambiguous idiom such as full zero-initialization.'},

 {'id':'Rule 9.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'집합체 초기화에서 같은 요소를 중복 초기화하지 않는다',
  'title_en':'An element of an object shall not be initialized more than once',
  'bad': r"""#include <stdio.h>
int main(void){
    /* 지정 초기자에서 인덱스 1 을 두 번 — 앞 값(10)이 조용히 버려짐 */
    int a[3] = { [1] = 10, [1] = 20 };
    printf("%d %d %d\n", a[0], a[1], a[2]);   /* a[1] 은 20 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[3] = { [1] = 20 };   /* 각 요소를 한 번만 초기화 */
    printf("%d %d %d\n", a[0], a[1], a[2]);
    return 0;
}""",
  'why':'지정 초기자(designated initializer)에서 같은 요소를 두 번 지정하면 앞의 값이 진단 없이 덮어써져, 둘 중 어느 것이 의도인지 모호한 채로 버그가 숨는다. 각 요소는 정확히 한 번만 초기화한다.',
  'why_en':'Specifying the same element twice in a designated initializer silently overwrites the earlier value, hiding a bug with ambiguous intent. Initialize each element exactly once.'},

 {'id':'Rule 9.5','cat':'Required · Decidable · Rule','compiles':True,
  'title':'지정 초기자로 배열을 초기화할 때는 크기를 명시한다',
  'title_en':'Where designated initializers are used to initialize an array, the size shall be specified explicitly',
  'bad': r"""#include <stdio.h>
int main(void){
    int codes[] = { [4] = 9 };   /* 크기를 초기자가 암묵 결정(5) — 의도한 크기와 다를 수 있음 */
    printf("count=%zu last=%d\n", sizeof codes / sizeof codes[0], codes[4]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int codes[8] = { [4] = 9 };  /* 크기를 명시 — 모호함 제거 */
    printf("count=%zu last=%d\n", sizeof codes / sizeof codes[0], codes[4]);
    return 0;
}""",
  'why':'지정 초기자만으로 배열 크기를 암묵 결정하면, 가장 큰 인덱스에 따라 크기가 정해져 의도한 용량과 달라지고 이후 경계 가정이 깨진다. 배열 크기를 명시해 용량을 코드에 분명히 드러낸다.',
  'why_en':'Letting designated initializers implicitly determine the array size makes the size depend on the largest index, diverging from the intended capacity and breaking later bounds assumptions. Specify the array size explicitly so the capacity is clear in the code.'},
]
