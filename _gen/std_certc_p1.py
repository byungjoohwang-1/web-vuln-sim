# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트1: PRE·DCL·EXP·INT·FLP) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준(공식 사이트 대조) 인용, 코드·해설은 자체 작성(규범 원문 비복제).
bad/good 는 gcc -std=c11 로 컴파일되는 자족(self-contained) 프로그램. title_en/why_en 영문 병기."""

RULES = [
 {'id':'PRE30-C','cat':'PRE · Rule · L1','compiles':True,
  'title':'토큰 연결로 식별자/보편 문자 이름을 조립하지 않는다',
  'title_en':'Do not create identifiers or universal character names through token concatenation',
  'bad': r"""#include <stdio.h>
#define JOIN(a,b) a##b
int main(void){
    int JOIN(co,unt) = 3;   /* 토큰 결합으로 'count' 조립 — 깨지기 쉬움 */
    printf("%d\n", count);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int count = 3;          /* 완성된 식별자를 직접 사용 */
    printf("%d\n", count);
    return 0;
}""",
  'why':'## 로 식별자(또는 보편 문자 이름)를 조립하면 의도와 다른 토큰이 생기고 가독성이 떨어진다. 완성된 식별자를 직접 작성한다.',
  'why_en':'Assembling identifiers (or universal character names) with ## yields fragile, hard-to-read code and can produce unintended tokens. Write completed identifiers directly.'},

 {'id':'PRE31-C','cat':'PRE · Rule · L1','compiles':True,
  'title':'안전하지 않은 매크로의 인자에 부작용을 두지 않는다',
  'title_en':'Avoid side effects in arguments to unsafe macros',
  'bad': r"""#include <stdio.h>
#define ABS(x) ((x) < 0 ? -(x) : (x))
int main(void){
    int i = -3;
    int y = ABS(i++);       /* i 가 두 번 평가됨 */
    printf("y=%d i=%d\n", y, i);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define ABS(x) ((x) < 0 ? -(x) : (x))
int main(void){
    int i = -3;
    int t = i++;            /* 부작용은 한 번만 */
    int y = ABS(t);
    printf("y=%d i=%d\n", y, i);
    return 0;
}""",
  'why':'매크로가 인자를 여러 번 평가하면 부작용(증감·함수호출)이 중복 실행된다. 부작용은 매크로 밖에서 한 번만 수행한다.',
  'why_en':'A macro may evaluate its argument multiple times, so side effects (increment, calls) run more than once. Perform side effects once, outside the macro.'},

 {'id':'PRE32-C','cat':'PRE · Rule · L1','compiles':True,
  'title':'함수형 매크로 호출의 인자 안에서 전처리 지시문을 사용하지 않는다',
  'title_en':'Do not use preprocessor directives in invocations of function-like macros',
  'bad': r"""#include <string.h>
#define COPY(d,s,n) memcpy((d),(s),(n))
int main(void){
    char d[8];
    /* 위반: 인자 안에서 크기를 #if 로 고른다(미정의). 아래는 동치의 위험 패턴 */
    int n = 4;
#ifdef BIG
    n = 8;
#endif
    COPY(d, "abcd", (n>8?8:n));
    return 0;
}""",
  'good': r"""#include <string.h>
#define COPY(d,s,n) memcpy((d),(s),(n))
int main(void){
    char d[8];
#ifdef BIG
    int n = 8;
#else
    int n = 4;
#endif
    COPY(d, "abcd", n);     /* 값을 먼저 정하고 매크로에 전달 */
    return 0;
}""",
  'why':'함수형 매크로 인자 안의 #if 등은 미정의 동작이다. 조건부 컴파일로 값을 먼저 정한 뒤 매크로/함수에 전달한다.',
  'why_en':'A #if directive inside a function-like macro argument is undefined behavior. Decide the value first with conditional compilation, then pass it to the macro.'},

 {'id':'PRE00-C','cat':'PRE · Rec · L3','compiles':True,
  'title':'함수형 매크로보다 인라인/정적 함수를 선호한다',
  'title_en':'Prefer inline or static functions to function-like macros',
  'bad': r"""#include <stdio.h>
#define MAX(a,b) ((a) > (b) ? (a) : (b))
int main(void){
    int i = 2;
    int m = MAX(i++, 5);    /* 인자 다중 평가 */
    printf("%d %d\n", m, i);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static inline int imax(int a, int b){ return a > b ? a : b; }
int main(void){
    int i = 2;
    int m = imax(i++, 5);   /* 인자 1회 평가, 타입 검사 */
    printf("%d %d\n", m, i);
    return 0;
}""",
  'why':'매크로는 타입 검사가 없고 인자를 다중 평가한다. inline 함수가 같은 성능에 타입 안전과 단일 평가를 보장한다.',
  'why_en':'Macros have no type checking and evaluate arguments multiple times. An inline function gives the same performance with type safety and single evaluation.'},

 {'id':'PRE10-C','cat':'PRE · Rec · L3','compiles':True,
  'title':'여러 문장을 담는 매크로는 do-while(0)으로 감싼다',
  'title_en':'Wrap multi-statement macros in a do-while loop',
  'bad': r"""#include <stdio.h>
#define LOG(x) printf("%d\n", x); fflush(stdout)
int main(void){
    int v = 1;
    if (v) LOG(v);          /* fflush 는 if 와 무관하게 항상 실행 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define LOG(x) do { printf("%d\n", x); fflush(stdout); } while (0)
int main(void){
    int v = 1;
    if (v) { LOG(v); }
    return 0;
}""",
  'why':'여러 문장 매크로를 나열하면 if/else 본문에서 일부만 묶여 의도와 다르게 동작한다. do{...}while(0)으로 단일 문장처럼 만든다.',
  'why_en':'Listing multiple statements in a macro can bind only part of it to an if/else body. Wrap it in do{...}while(0) so it behaves as a single statement.'},

 {'id':'DCL30-C','cat':'DCL · Rule · L3','compiles':True,
  'title':'객체는 용도에 맞는 저장 기간으로 선언한다',
  'title_en':'Declare objects with appropriate storage durations',
  'bad': r"""#include <stdio.h>
const char *get_name(void){
    char buf[8];
    snprintf(buf, sizeof buf, "node");
    return buf;             /* 자동 객체 주소 반환 — 수명 종료 */
}
int main(void){ printf("%s\n", get_name()); return 0; }""",
  'good': r"""#include <stdio.h>
const char *get_name(void){
    static const char name[] = "node";
    return name;            /* 정적 저장 기간 */
}
int main(void){ printf("%s\n", get_name()); return 0; }""",
  'why':'자동 저장 기간 객체의 주소를 함수 밖으로 반환하면 수명이 끝나 무효한 메모리를 가리킨다. 정적 저장 기간이나 호출자 버퍼를 쓴다.',
  'why_en':'Returning the address of an automatic object outlives its lifetime and points to invalid memory. Use static storage or a caller-supplied buffer.'},

 {'id':'DCL31-C','cat':'DCL · Rule · L3','compiles':True,
  'title':'식별자는 사용 전에 선언한다',
  'title_en':'Declare identifiers before using them',
  'bad': r"""#include <stdio.h>
int main(void){
    int r = scale(3);       /* 선언 없이 호출 — 암시적 선언 */
    printf("%d\n", r);
    return 0;
}
int scale(int x){ return x * 2; }""",
  'good': r"""#include <stdio.h>
int scale(int x);           /* 사용 전 선언 */
int main(void){
    int r = scale(3);
    printf("%d\n", r);
    return 0;
}
int scale(int x){ return x * 2; }""",
  'why':'선언 없는 사용은 타입을 잘못 가정해 인자/반환 손상을 일으킨다. 모든 식별자를 사용 전에 선언한다.',
  'why_en':'Using an identifier without a prior declaration mis-assumes its type, corrupting arguments/returns. Declare every identifier before use.'},

 {'id':'DCL37-C','cat':'DCL · Rule · L1','compiles':True,
  'title':'예약된 식별자를 선언하거나 정의하지 않는다',
  'title_en':'Do not declare or define reserved identifiers',
  'bad': r"""#include <stdio.h>
#define __MYMAX 100         /* 밑줄 두 개 시작 — 구현 예약 */
int _count = 0;             /* 밑줄+소문자(파일 범위) 예약 */
int main(void){ _count = __MYMAX; printf("%d\n", _count); return 0; }""",
  'good': r"""#include <stdio.h>
#define APP_MAX 100
int app_count = 0;
int main(void){ app_count = APP_MAX; printf("%d\n", app_count); return 0; }""",
  'why':'밑줄로 시작하거나 표준이 예약한 이름을 정의하면 구현 내부와 충돌해 미정의 동작이 된다. 비예약 이름을 쓴다.',
  'why_en':'Defining names that begin with an underscore or are reserved by the standard collides with the implementation and is undefined. Use non-reserved names.'},

 {'id':'DCL38-C','cat':'DCL · Rule · L1','compiles':True,
  'title':'유연 배열 멤버는 올바른 구문으로 선언한다',
  'title_en':'Use the correct syntax when declaring a flexible array member',
  'bad': r"""#include <stdlib.h>
struct Buf { size_t n; char data[1]; };   /* [1] 트릭 — 경계 모호 */
int main(void){
    struct Buf *b = malloc(sizeof *b + 10);
    if (b){ b->n = 10; b->data[5] = 'x'; free(b); }   /* 선언 크기 초과 접근 */
    return 0;
}""",
  'good': r"""#include <stdlib.h>
struct Buf { size_t n; char data[]; };     /* C99 유연 배열 멤버 */
int main(void){
    size_t len = 10;
    struct Buf *b = malloc(sizeof *b + len);
    if (b){ b->n = len; b->data[5] = 'x'; free(b); }
    return 0;
}""",
  'why':'data[1] 같은 옛 트릭은 선언 크기와 실제 크기가 어긋나 경계 검사를 무력화한다. C99 유연 배열 멤버 구문을 쓴다.',
  'why_en':'The old data[1] trick makes the declared size differ from the real size, defeating bounds analysis. Use the C99 flexible array member syntax.'},

 {'id':'DCL39-C','cat':'DCL · Rec · L3','compiles':True,
  'title':'구조체 패딩을 통한 정보 유출을 피한다',
  'title_en':'Avoid information leakage through structure padding',
  'bad': r"""#include <stdio.h>
#include <string.h>
struct S { char c; int v; };   /* c와 v 사이 패딩에 잔존 데이터 */
int main(void){
    struct S s;
    s.c = 'x'; s.v = 1;        /* 패딩 미초기화 */
    fwrite(&s, sizeof s, 1, stdout);   /* 패딩 바이트 유출 가능 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <string.h>
struct S { char c; int v; };
int main(void){
    struct S s;
    memset(&s, 0, sizeof s);   /* 패딩 포함 0으로 초기화 */
    s.c = 'x'; s.v = 1;
    fwrite(&s, sizeof s, 1, stdout);
    return 0;
}""",
  'why':'구조체를 그대로 외부로 쓰면 초기화되지 않은 패딩 바이트의 잔존 데이터가 유출될 수 있다. 전체를 0으로 초기화한 뒤 채운다.',
  'why_en':'Writing a struct verbatim can leak residual data in uninitialized padding bytes. Zero the whole object before populating it.'},

 {'id':'DCL40-C','cat':'DCL · Rule · L2','compiles':True,
  'title':'같은 함수/객체에 호환되지 않는 선언을 만들지 않는다',
  'title_en':'Do not create incompatible declarations of the same function or object',
  'bad': r"""#include <stdio.h>
int f();                    /* 매개변수 미명세 — 정의와 호환 안 되는 느슨한 선언 */
int f(int x){ return x * 2; }
int main(void){ printf("%d\n", f(3)); return 0; }""",
  'good': r"""#include <stdio.h>
int f(int x);               /* 정의와 일치하는 프로토타입 */
int f(int x){ return x * 2; }
int main(void){ printf("%d\n", f(3)); return 0; }""",
  'why':'정의와 호환되지 않는(매개변수 미명세 등) 선언을 두면 잘못된 인자 개수·타입 호출을 컴파일러가 잡지 못한다. 정의와 일치하는 단일 프로토타입을 둔다.',
  'why_en':'A declaration incompatible with the definition (e.g. unspecified parameters) lets wrong-arity/type calls slip past the compiler. Keep a single prototype matching the definition.'},

 {'id':'DCL41-C','cat':'DCL · Rule · L3','compiles':True,
  'title':'switch 의 첫 case 이전에 변수를 선언하지 않는다',
  'title_en':'Do not declare variables inside a switch before the first case label',
  'bad': r"""#include <stdio.h>
int main(void){
    int x = 1;
    switch (x){
        int y = 5;          /* 초기화가 실행되지 않음 */
        case 1: printf("%d\n", y); break;
        default: break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int x = 1;
    int y = 5;              /* switch 밖에서 초기화 */
    switch (x){
        case 1: printf("%d\n", y); break;
        default: break;
    }
    return 0;
}""",
  'why':'switch 첫 레이블 이전의 선언 초기화는 점프로 건너뛰어져 미초기화 값을 읽는다. 선언은 switch 밖이나 case 블록 안에 둔다.',
  'why_en':'An initializer before the first switch label is skipped by the jump, leaving an uninitialized read. Declare outside the switch or inside a case block.'},

 {'id':'DCL00-C','cat':'DCL · Rec · L3','compiles':True,
  'title':'변경되지 않는 객체는 const 로 한정한다',
  'title_en':'Const-qualify immutable objects',
  'bad': r"""#include <stdio.h>
int main(void){
    int limit = 100;        /* 이후 수정 없음에도 비-const */
    printf("%d\n", limit);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    const int limit = 100;  /* 변경 불가를 컴파일러가 강제 */
    printf("%d\n", limit);
    return 0;
}""",
  'why':'불변 객체를 const로 표시하지 않으면 실수로 수정되거나 의도가 흐려진다. const로 변경 불가를 강제한다.',
  'why_en':'Not marking immutable objects const allows accidental modification and obscures intent. Let const enforce immutability.'},

 {'id':'DCL02-C','cat':'DCL · Rec · L2','compiles':True,
  'title':'시각적으로 구별되는 식별자를 사용한다',
  'title_en':'Use visually distinct identifiers',
  'bad': r"""#include <stdio.h>
int main(void){
    int rn = 1, rnn = 2;    /* rn / rnn — 혼동 */
    printf("%d\n", rn + rnn);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int row_count = 1, running_total = 2;
    printf("%d\n", row_count + running_total);
    return 0;
}""",
  'why':'철자가 비슷한 짧은 이름은 잘못된 변수 참조를 부른다. 의미가 드러나는 구별되는 이름을 쓴다.',
  'why_en':'Short, similar-looking names invite referencing the wrong variable. Use distinct, meaningful names.'},

 {'id':'DCL18-C','cat':'DCL · Rec · L3','compiles':True,
  'title':'정수 상수를 0으로 시작(8진수)하지 않는다',
  'title_en':'Do not begin integer constants with 0 (octal)',
  'bad': r"""#include <stdio.h>
int main(void){
    int code = 013;         /* 8진수 11, 의도는 13? */
    printf("%d\n", code);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int code = 13;          /* 10진수 */
    printf("%d\n", code);
    return 0;
}""",
  'why':'선행 0은 8진수로 해석되어 013이 11이 되는 등 의도와 다른 값이 된다. 10진/16진 표기를 쓴다.',
  'why_en':'A leading 0 is interpreted as octal, so 013 becomes 11, not 13. Use decimal or hexadecimal notation.'},

 {'id':'EXP30-C','cat':'EXP · Rule · L2','compiles':True,
  'title':'부작용의 평가 순서에 의존하지 않는다',
  'title_en':'Do not depend on the order of evaluation for side effects',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[4] = {0};
    int i = 0;
    a[i] = i++;             /* i 사용과 증가 순서 미명세 */
    printf("%d %d\n", a[0], i);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[4] = {0};
    int i = 0;
    a[i] = i;
    i++;                    /* 부작용 분리 */
    printf("%d %d\n", a[0], i);
    return 0;
}""",
  'why':'한 표현식에서 같은 객체를 수정·사용하면 평가 순서에 따라 결과가 달라진다. 부작용을 분리해 순서를 결정한다.',
  'why_en':'Modifying and reading the same object in one expression makes the result order-dependent. Separate the side effect to fix the order.'},

 {'id':'EXP32-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'volatile 객체를 비-volatile 참조로 접근하지 않는다',
  'title_en':'Do not access a volatile object through a nonvolatile reference',
  'bad': r"""#include <stdio.h>
int main(void){
    volatile int reg = 1;
    int *p = (int *)&reg;   /* volatile 의미 상실 */
    printf("%d\n", *p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    volatile int reg = 1;
    volatile int *p = &reg;
    printf("%d\n", *p);
    return 0;
}""",
  'why':'volatile 객체를 비-volatile 포인터로 접근하면 컴파일러가 접근을 최적화로 제거·재배치해 하드웨어 동작이 깨진다. 한정자를 보존한다.',
  'why_en':'Accessing a volatile object through a nonvolatile pointer lets the compiler optimize away or reorder accesses, breaking hardware semantics. Preserve the qualifier.'},

 {'id':'EXP33-C','cat':'EXP · Rule · L3','compiles':True,
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'title_en':'Do not read uninitialized memory',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[3] = {1,2,3};
    int sum;                /* 미초기화 */
    for (int i = 0; i < 3; i++) sum += a[i];
    printf("%d\n", sum);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[3] = {1,2,3};
    int sum = 0;
    for (int i = 0; i < 3; i++) sum += a[i];
    printf("%d\n", sum);
    return 0;
}""",
  'why':'미초기화 객체의 값은 불확정이라 읽으면 미정의 동작과 비결정적 결과를 낳는다. 사용 전 초기화한다.',
  'why_en':'An uninitialized object holds an indeterminate value; reading it is undefined and nondeterministic. Initialize before use.'},

 {'id':'EXP34-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'널 포인터를 역참조하지 않는다',
  'title_en':'Do not dereference null pointers',
  'bad': r"""#include <stdio.h>
#include <stdlib.h>
int main(void){
    int *p = malloc(sizeof *p);
    *p = 5;                 /* malloc 실패(NULL) 미검사 */
    printf("%d\n", *p);
    free(p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdlib.h>
int main(void){
    int *p = malloc(sizeof *p);
    if (p == NULL) return 1;
    *p = 5;
    printf("%d\n", *p);
    free(p);
    return 0;
}""",
  'why':'널 포인터 역참조는 크래시나 미정의 동작을 일으킨다. 역참조 전에 NULL 여부를 확인한다.',
  'why_en':'Dereferencing a null pointer causes a crash or undefined behavior. Check for NULL before dereferencing.'},

 {'id':'EXP36-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'포인터를 더 엄격히 정렬된 타입으로 캐스트하지 않는다',
  'title_en':'Do not cast pointers into more strictly aligned pointer types',
  'bad': r"""#include <stdio.h>
#include <string.h>
int main(void){
    char buf[16] = {0};
    int *p = (int *)&buf[1];   /* 정렬 위반 가능 */
    *p = 42;
    printf("%d\n", *p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <string.h>
int main(void){
    char buf[16] = {0};
    int v = 42;
    memcpy(&buf[1], &v, sizeof v);   /* 정렬 무관 */
    memcpy(&v, &buf[1], sizeof v);
    printf("%d\n", v);
    return 0;
}""",
  'why':'정렬 요건이 더 큰 타입으로 포인터를 캐스트해 접근하면 일부 플랫폼에서 폴트나 미정의 동작이 난다. memcpy로 정렬 비의존 접근을 한다.',
  'why_en':'Casting to a more strictly aligned type and dereferencing can fault or be undefined on some platforms. Use memcpy for alignment-independent access.'},

 {'id':'EXP37-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'함수는 올바른 개수·타입의 인자로 호출한다',
  'title_en':'Call functions with the correct number and type of arguments',
  'bad': r"""#include <stdio.h>
int add(int a, int b){ return a + b; }
int main(void){
    int (*fp)(int) = (int (*)(int))add;   /* 잘못된 시그니처로 호출 */
    printf("%d\n", fp(3));
    return 0;
}""",
  'good': r"""#include <stdio.h>
int add(int a, int b){ return a + b; }
int main(void){
    int (*fp)(int,int) = add;
    printf("%d\n", fp(3, 4));
    return 0;
}""",
  'why':'선언과 다른 시그니처로 함수를 호출하면 인자 전달이 어긋나 미정의 동작이 된다. 정확한 프로토타입대로 호출한다.',
  'why_en':'Calling a function through a mismatched signature misaligns argument passing and is undefined. Call with the exact prototype.'},

 {'id':'EXP39-C','cat':'EXP · Rule · L2','compiles':True,
  'title':'호환되지 않는 타입의 포인터로 변수에 접근하지 않는다',
  'title_en':'Do not access a variable through a pointer of an incompatible type',
  'bad': r"""#include <stdio.h>
int main(void){
    float f = 3.14f;
    unsigned u = *(unsigned *)&f;   /* 엄격 별칭 위반 */
    printf("%u\n", u);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <string.h>
int main(void){
    float f = 3.14f;
    unsigned u;
    memcpy(&u, &f, sizeof u);       /* 안전한 재해석 */
    printf("%u\n", u);
    return 0;
}""",
  'why':'엄격 별칭 규칙을 어기고 다른 타입 포인터로 접근하면 최적화와 충돌해 미정의 동작이 된다. memcpy로 안전하게 재해석한다.',
  'why_en':'Violating strict aliasing by accessing through an incompatible pointer conflicts with optimization and is undefined. Reinterpret safely via memcpy.'},

 {'id':'EXP40-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'const 로 선언된 객체를 수정하지 않는다',
  'title_en':'Do not modify constant objects',
  'bad': r"""#include <stdio.h>
int main(void){
    const int k = 5;
    int *p = (int *)&k;
    *p = 9;                 /* const 객체 수정 — 미정의 */
    printf("%d\n", k);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int k = 5;              /* 수정이 필요하면 비-const */
    k = 9;
    printf("%d\n", k);
    return 0;
}""",
  'why':'const 객체를 캐스트로 우회해 수정하면 미정의 동작이다. 수정이 필요한 객체는 처음부터 비-const로 선언한다.',
  'why_en':'Modifying a const object by casting away const is undefined. Declare objects that must change as non-const from the start.'},

 {'id':'EXP44-C','cat':'EXP · Rule · L3','compiles':True,
  'title':'sizeof 피연산자의 부작용에 의존하지 않는다',
  'title_en':'Do not rely on side effects in operands to sizeof',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[5] = {0};
    int i = 0;
    size_t n = sizeof(a[i++]);   /* i 증가 안 됨 */
    printf("%zu %d\n", n, i);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[5] = {0};
    int i = 0;
    size_t n = sizeof(a[0]);
    i++;
    printf("%zu %d\n", n, i);
    return 0;
}""",
  'why':'sizeof 의 피연산자(가변길이 배열 제외)는 평가되지 않아 부작용이 발생하지 않는다. 의도한 부작용은 별도 문장으로 수행한다.',
  'why_en':'The operand of sizeof (except VLAs) is not evaluated, so side effects do not occur. Perform intended side effects in a separate statement.'},

 {'id':'EXP45-C','cat':'EXP · Rule · L3','compiles':True,
  'title':'선택문의 조건에서 대입을 수행하지 않는다',
  'title_en':'Do not perform assignments in selection statements',
  'bad': r"""#include <stdio.h>
int compute(void){ return 7; }
int main(void){
    int x;
    if (x = compute()){ printf("%d\n", x); }   /* == 오타 혼동 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int compute(void){ return 7; }
int main(void){
    int x = compute();
    if (x != 0){ printf("%d\n", x); }
    return 0;
}""",
  'why':'조건식 안의 대입은 비교(==) 오타와 혼동되며 의도가 불명확하다. 대입과 조건 검사를 분리한다.',
  'why_en':'An assignment inside a condition is confused with an == typo and obscures intent. Separate the assignment from the test.'},

 {'id':'EXP46-C','cat':'EXP · Rule · L3','compiles':True,
  'title':'불리언 성격의 피연산자에 비트 연산자를 쓰지 않는다',
  'title_en':'Do not use a bitwise operator with a Boolean-like operand',
  'bad': r"""#include <stdio.h>
int main(void){
    int a = 1, b = 1, c = 0, d = 0;
    if ((a == b) & (c == d)){ printf("hit\n"); }   /* & : 단락 없음 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a = 1, b = 1, c = 0, d = 0;
    if ((a == b) && (c == d)){ printf("hit\n"); }
    return 0;
}""",
  'why':'논리 비교 결과에 비트 &/|를 쓰면 단락 평가가 사라지고 의도가 흐려진다. 논리 연산에는 &&/||를 쓴다.',
  'why_en':'Using bitwise &/| on comparison results loses short-circuiting and obscures intent. Use &&/|| for logical operations.'},

 {'id':'EXP47-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'va_arg 를 잘못된 타입으로 호출하지 않는다',
  'title_en':'Do not call va_arg with an argument of the incorrect type',
  'bad': r"""#include <stdio.h>
#include <stdarg.h>
long sum(int n, ...){
    va_list ap; va_start(ap, n);
    long s = 0;
    for (int i = 0; i < n; i++) s += va_arg(ap, long);   /* 실제는 int 전달 */
    va_end(ap);
    return s;
}
int main(void){ printf("%ld\n", sum(2, 1, 2)); return 0; }""",
  'good': r"""#include <stdio.h>
#include <stdarg.h>
long sum(int n, ...){
    va_list ap; va_start(ap, n);
    long s = 0;
    for (int i = 0; i < n; i++) s += va_arg(ap, int);    /* 전달 타입과 일치 */
    va_end(ap);
    return s;
}
int main(void){ printf("%ld\n", sum(2, 1, 2)); return 0; }""",
  'why':'va_arg에 실제 전달된 타입과 다른 타입을 지정하면 잘못된 비트를 읽어 미정의 동작이 된다. 전달 타입과 정확히 일치시킨다.',
  'why_en':'Specifying a va_arg type different from what was passed reads the wrong bits and is undefined. Match the promoted type exactly.'},

 {'id':'EXP12-C','cat':'EXP · Rec · L2','compiles':True,
  'title':'함수의 반환값을 무시하지 않는다',
  'title_en':'Do not ignore values returned by functions',
  'bad': r"""#include <stdio.h>
int main(void){
    char buf[4];
    snprintf(buf, sizeof buf, "%d", 12345);   /* 절단 여부 무시 */
    printf("%s\n", buf);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char buf[4];
    int need = snprintf(buf, sizeof buf, "%d", 12345);
    if (need < 0 || (size_t)need >= sizeof buf) printf("truncated\n");
    printf("%s\n", buf);
    return 0;
}""",
  'why':'반환값을 무시하면 부분 실패·오류·절단을 감지하지 못한다. 의미 있는 반환값은 검사하거나 명시적으로 버린다.',
  'why_en':'Ignoring a return value hides partial failure, errors, or truncation. Check meaningful return values or explicitly discard them.'},

 {'id':'INT30-C','cat':'INT · Rule · L2','compiles':True,
  'title':'부호 없는 정수 연산이 래핑되지 않도록 보장한다',
  'title_en':'Ensure that unsigned integer operations do not wrap',
  'bad': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    unsigned a = UINT_MAX, b = 2;
    unsigned s = a + b;     /* 래핑 */
    printf("%u\n", s);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    unsigned a = UINT_MAX, b = 2;
    if (a > UINT_MAX - b){ printf("overflow\n"); return 1; }
    printf("%u\n", a + b);
    return 0;
}""",
  'why':'부호 없는 덧셈은 오버플로우 시 조용히 모듈로 래핑되어 길이·인덱스 계산을 망가뜨린다. 연산 전에 래핑 조건을 검사한다.',
  'why_en':'Unsigned addition silently wraps modulo on overflow, corrupting size/index math. Check the wrap condition before the operation.'},

 {'id':'INT31-C','cat':'INT · Rule · L2','compiles':True,
  'title':'정수 변환이 데이터를 잃거나 잘못 해석하지 않도록 한다',
  'title_en':'Ensure that integer conversions do not lose or misinterpret data',
  'bad': r"""#include <stdio.h>
int main(void){
    long big = 300;
    unsigned char b = (unsigned char)big;   /* 300 → 44 절단 */
    printf("%u\n", b);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    long big = 300;
    if (big < 0 || big > 255){ printf("range\n"); return 1; }
    unsigned char b = (unsigned char)big;
    printf("%u\n", b);
    return 0;
}""",
  'why':'넓은 정수를 좁은 타입으로 변환하면 값이 잘리거나 부호가 뒤바뀐다. 변환 전에 대상 타입 범위를 검사한다.',
  'why_en':'Converting a wide integer to a narrow type truncates or flips sign. Check the target type range before converting.'},

 {'id':'INT32-C','cat':'INT · Rule · L2','compiles':True,
  'title':'부호 있는 정수 연산이 오버플로우되지 않도록 보장한다',
  'title_en':'Ensure that signed integer operations do not result in overflow',
  'bad': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    int a = INT_MAX, b = 2;
    int p = a * b;          /* signed 오버플로우 — 미정의 */
    printf("%d\n", p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    int a = INT_MAX, b = 2;
    if (a != 0 && (b > INT_MAX / a || b < INT_MIN / a)){ printf("overflow\n"); return 1; }
    printf("%d\n", a * b);
    return 0;
}""",
  'why':'부호 있는 정수 오버플로우는 미정의 동작이다. 곱셈·덧셈 전에 피연산자로 한계를 나눠 오버플로우 가능성을 검사한다.',
  'why_en':'Signed integer overflow is undefined behavior. Before multiplying/adding, divide the limits by an operand to test for overflow.'},

 {'id':'INT33-C','cat':'INT · Rule · L2','compiles':True,
  'title':'나눗셈/나머지 연산에서 0으로 나누지 않는다',
  'title_en':'Ensure that division and remainder operations do not result in divide-by-zero',
  'bad': r"""#include <stdio.h>
int main(void){
    int total = 10, count = 0;
    int q = total / count;  /* 0 나눗셈 */
    printf("%d\n", q);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int total = 10, count = 0;
    if (count == 0){ printf("div by zero\n"); return 1; }
    printf("%d\n", total / count);
    return 0;
}""",
  'why':'0으로 나누거나 나머지를 구하면 미정의 동작(대개 크래시)이 된다. 나누기 전에 분모가 0이 아님을 확인한다.',
  'why_en':'Dividing or taking remainder by zero is undefined (usually a crash). Verify the divisor is nonzero first.'},

 {'id':'INT34-C','cat':'INT · Rule · L2','compiles':True,
  'title':'음수나 비트폭 이상으로 시프트하지 않는다',
  'title_en':'Do not shift by a negative count or a count greater than or equal to the width',
  'bad': r"""#include <stdio.h>
int main(void){
    unsigned v = 1u;
    int n = 40;
    unsigned r = v << n;    /* 32비트를 40 시프트 — 미정의 */
    printf("%u\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    unsigned v = 1u;
    int n = 40;
    if (n < 0 || n >= (int)(sizeof(unsigned) * CHAR_BIT)){ printf("bad shift\n"); return 1; }
    printf("%u\n", v << n);
    return 0;
}""",
  'why':'시프트량이 음수이거나 피연산자 비트폭 이상이면 결과가 미정의다. 시프트 전에 0..(폭-1) 범위를 보장한다.',
  'why_en':'A shift count that is negative or >= the operand width is undefined. Ensure the count is within 0..(width-1) before shifting.'},

 {'id':'INT35-C','cat':'INT · Rule · L1','compiles':True,
  'title':'정수 정밀도(precision)를 올바르게 사용한다',
  'title_en':'Use correct integer precisions',
  'bad': r"""#include <stdio.h>
int main(void){
    unsigned bits = sizeof(unsigned) * 8;   /* CHAR_BIT==8 가정 */
    printf("%u\n", bits);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    unsigned bits = sizeof(unsigned) * CHAR_BIT;
    printf("%u\n", bits);
    return 0;
}""",
  'why':'바이트가 항상 8비트라고 가정하면 비표준 플랫폼에서 정밀도 계산이 틀어진다. CHAR_BIT로 실제 비트 수를 구한다.',
  'why_en':'Assuming a byte is always 8 bits breaks precision math on unusual platforms. Use CHAR_BIT for the real bit count.'},

 {'id':'INT18-C','cat':'INT · Rec · L3','compiles':True,
  'title':'정수 표현식은 충분히 큰 타입에서 평가한다',
  'title_en':'Evaluate integer expressions in a larger size',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t a = 60000, b = 10000;
    uint32_t s = a + b;     /* 16비트로 계산 후 확장? (승격 덕에 안전하나 의도 명확화) */
    uint16_t bad = (uint16_t)(a + b);   /* 좁은 폭으로 절단 */
    printf("%u %u\n", s, bad);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t a = 60000, b = 10000;
    uint32_t s = (uint32_t)a + b;   /* 32비트로 평가 */
    printf("%u\n", s);
    return 0;
}""",
  'why':'좁은 타입끼리 계산 후 좁은 타입에 담으면 오버플로우가 숨는다. 평가 전에 충분히 큰 타입으로 승격한다.',
  'why_en':'Computing in a narrow type and storing back narrowly hides overflow. Promote to a sufficiently large type before evaluating.'},

 {'id':'FLP30-C','cat':'FLP · Rule · L3','compiles':True,
  'title':'부동소수형을 루프 카운터로 사용하지 않는다',
  'title_en':'Do not use floating-point variables as loop counters',
  'bad': r"""#include <stdio.h>
int main(void){
    int cnt = 0;
    for (float x = 0.0f; x != 1.0f; x += 0.1f){ if (++cnt > 100) break; }
    printf("%d\n", cnt);    /* 오차로 1.0 정확히 안 맞음 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int cnt = 0;
    for (int i = 0; i < 10; i++){ float x = (float)i / 10.0f; (void)x; cnt++; }
    printf("%d\n", cnt);
    return 0;
}""",
  'why':'부동소수 카운터는 표현 오차로 종료 조건을 정확히 만족하지 못해 무한 루프가 될 수 있다. 정수로 반복하고 실수는 파생한다.',
  'why_en':'A floating-point counter may never exactly meet the termination test due to rounding, risking an infinite loop. Iterate with an integer and derive the float.'},

 {'id':'FLP32-C','cat':'FLP · Rule · L2','compiles':True,
  'title':'수학 함수의 도메인/범위 오류를 예방하거나 검출한다',
  'title_en':'Prevent or detect domain and range errors in math functions',
  'bad': r"""#include <stdio.h>
#include <math.h>
int main(void){
    double x = -4.0;
    double r = sqrt(x);     /* x<0 → NaN */
    printf("%f\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <math.h>
int main(void){
    double x = -4.0;
    if (x < 0.0){ printf("domain\n"); return 1; }
    printf("%f\n", sqrt(x));
    return 0;
}""",
  'why':'정의역을 벗어난 인자(예: sqrt의 음수)는 도메인 오류·NaN을 만든다. 호출 전 인자 범위를 검사하거나 오류 플래그를 확인한다.',
  'why_en':'Out-of-domain arguments (e.g. negative to sqrt) cause domain errors/NaN. Check the argument range before calling, or inspect the error flags.'},

 {'id':'FLP34-C','cat':'FLP · Rule · L2','compiles':True,
  'title':'부동소수 변환은 대상 타입 범위 안에서만 수행한다',
  'title_en':'Ensure that floating-point conversions are within range of the new type',
  'bad': r"""#include <stdio.h>
int main(void){
    double d = 1e18;
    int n = (int)d;         /* int 범위 초과 — 미정의 */
    printf("%d\n", n);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <limits.h>
int main(void){
    double d = 1e18;
    if (d < (double)INT_MIN || d > (double)INT_MAX){ printf("range\n"); return 1; }
    printf("%d\n", (int)d);
    return 0;
}""",
  'why':'대상 정수 타입 범위를 벗어난 부동소수를 변환하면 미정의 동작이 된다. 변환 전에 범위를 검사한다.',
  'why_en':'Converting a floating-point value outside the target integer range is undefined. Check the range before converting.'},

 {'id':'FLP03-C','cat':'FLP · Rec · L2','compiles':True,
  'title':'부동소수 연산 오류를 검출하고 처리한다',
  'title_en':'Detect and handle floating-point errors',
  'bad': r"""#include <stdio.h>
int main(void){
    double a = 1.0, b = 0.0;
    double r = a / b;       /* inf — 미검사로 전파 */
    printf("%f\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <fenv.h>
#pragma STDC FENV_ACCESS ON
int main(void){
    feclearexcept(FE_ALL_EXCEPT);
    double a = 1.0, b = 0.0;
    double r = a / b;
    if (fetestexcept(FE_DIVBYZERO | FE_INVALID)){ printf("fp error\n"); return 1; }
    printf("%f\n", r);
    return 0;
}""",
  'why':'부동소수 예외(0 나눗셈·무효 연산)를 무시하면 NaN/Inf가 후속 계산에 전파된다. fenv로 예외 플래그를 확인해 처리한다.',
  'why_en':'Ignoring floating-point exceptions (divide-by-zero, invalid) lets NaN/Inf propagate. Check the fenv exception flags and handle them.'},
]
