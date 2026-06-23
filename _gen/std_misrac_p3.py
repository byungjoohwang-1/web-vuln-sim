# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트3: Rule 18~23) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu11 -lm` 기준.
다중 파일·전처리 토큰 결합처럼 단일 파일로 성립하지 않는 규칙은 초점 스니펫으로 둔다."""

RULES = [
 {'id':'Rule 18.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'포인터 산술 결과는 같은 배열의 범위 안을 가리켜야 한다',
  'title_en':'A pointer resulting from arithmetic on a pointer operand shall address an element of the same array',
  'bad': r"""#include <stdio.h>
static int get_offset(void){ return 12; }
int main(void){
    int a[10] = {0};
    int *p = a + get_offset();   /* 배열(10) 밖을 가리킴 */
    *p = 7;                      /* 경계 밖 쓰기 — 미정의 동작·메모리 손상 */
    printf("%d\n", a[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int get_offset(void){ return 12; }
int main(void){
    int a[10] = {0};
    int i = get_offset();
    if (i >= 0 && i < 10) {      /* 인덱스를 검증해 범위 내 포인터만 생성 */
        int *p = a + i;
        *p = 7;
    } else {
        printf("offset out of range\n");
    }
    printf("%d\n", a[0]);
    return 0;
}""",
  'why':'배열 경계를 벗어난 포인터를 만들어 역참조하면 인접 메모리를 침범하는 미정의 동작이 되어, 데이터 손상이나 보안 결함으로 이어진다. 인덱스를 사용 전에 [0, 길이) 범위로 검증해 항상 같은 배열 안을 가리키는 포인터만 생성한다.',
  'why_en':'Forming and dereferencing a pointer past an array’s bounds is undefined behaviour that intrudes on adjacent memory, leading to corruption or security defects. Validate the index against [0, length) before use so only pointers within the same array are created.'},

 {'id':'Rule 18.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'포인터 뺄셈은 같은 배열의 원소들 사이에서만 한다',
  'title_en':'Subtraction between pointers shall only be applied to pointers that address elements of the same array',
  'bad': r"""#include <stdio.h>
#include <stddef.h>
int main(void){
    int x = 1, y = 2;
    ptrdiff_t d = &y - &x;   /* 서로 다른 객체의 주소를 뺌 — 결과 미정의 */
    printf("%ld\n", (long)d);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
int main(void){
    int arr[8] = {0};
    ptrdiff_t d = &arr[5] - &arr[1];   /* 같은 배열 내 원소 간 뺄셈 — 정의됨(=4) */
    printf("%ld\n", (long)d);
    return 0;
}""",
  'why':'서로 다른 객체의 주소 차이는 표준이 정의하지 않으므로(같은 배열의 원소가 아니므로) 결과가 미정의가 되어 이식·최적화 시 의미 없는 값이 나온다. 포인터 뺄셈은 동일 배열의 원소들 사이에서만 수행한다.',
  'why_en':'The difference between addresses of distinct objects is undefined (they are not elements of one array), yielding meaningless values across ports and optimizations. Perform pointer subtraction only between elements of the same array.'},

 {'id':'Rule 18.3','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'관계 연산(<,>)은 같은 객체를 가리키는 포인터끼리만 한다',
  'title_en':'The relational operators >, >=, < and <= shall not be applied to pointers to different objects',
  'bad': r"""#include <stdio.h>
int main(void){
    int bufA[4] = {0};
    int bufB[4] = {0};
    if (&bufA[0] < &bufB[0]) {   /* 다른 객체를 가리키는 포인터의 대소 비교 — 미정의 */
        printf("A before B\n");
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int idxA = 1, idxB = 3;
    if (idxA < idxB) {           /* 인덱스로 비교하거나, 같은 배열 내 포인터만 비교 */
        printf("A before B\n");
    }
    return 0;
}""",
  'why':'서로 다른 객체를 가리키는 포인터의 대소 비교 결과는 표준이 보장하지 않아 미정의이며, 메모리 배치 가정에 의존한 코드는 플랫폼마다 다르게 동작한다. 같은 배열 내 포인터끼리 비교하거나 인덱스로 비교한다.',
  'why_en':'Relational comparison of pointers to different objects is undefined, so code relying on memory-layout assumptions behaves differently across platforms. Compare pointers within the same array, or compare indices instead.'},

 {'id':'Rule 18.4','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'포인터에 +, -, +=, -= 산술을 적용하지 않는다(배열 첨자 사용)',
  'title_en':'The +, -, += and -= operators should not be applied to an expression of pointer type',
  'bad': r"""#include <stdio.h>
int main(void){
    int buf[8] = {0};
    int *p = buf;
    *(p + 3) = 7;       /* 포인터 산술 — 경계 오류를 숨기고 가독성 저하 */
    printf("%d\n", buf[3]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int buf[8] = {0};
    int *p = buf;
    p[3] = 7;           /* 배열 첨자 표기 — 의도가 명확하고 분석이 쉬움 */
    printf("%d\n", buf[3]);
    return 0;
}""",
  'why':'p + n 같은 포인터 산술은 어느 배열의 몇 번째인지 한눈에 드러나지 않아 경계 오류를 숨기고 정적 분석을 어렵게 한다. 동일한 접근을 배열 첨자 p[n] 표기로 쓰면 의도가 명확해지고 도구의 경계 검사도 쉬워진다.',
  'why_en':'Pointer arithmetic like p + n does not make clear which array element is meant, hiding bounds errors and hampering static analysis. Writing the same access with subscript notation p[n] clarifies intent and eases tool-based bounds checking.'},

 {'id':'Rule 18.5','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'포인터의 중첩 수준은 2단계를 넘지 않는다',
  'title_en':'Declarations should contain no more than two levels of pointer nesting',
  'bad': r"""#include <stdio.h>
int main(void){
    int v = 7;
    int *p = &v;
    int **pp = &p;
    int ***ppp = &pp;     /* 3중 포인터 — 추론·검증이 매우 어려움 */
    printf("%d\n", ***ppp);
    return 0;
}""",
  'good': r"""#include <stdio.h>
typedef struct Matrix { int *data; int rows; int cols; } Matrix;   /* 간접 단계를 캡슐화 */
int main(void){
    int storage[4] = {7, 0, 0, 0};
    Matrix m = { storage, 2, 2 };
    Matrix *mp = &m;       /* 2단계 이하로 유지 */
    printf("%d\n", mp->data[0]);
    return 0;
}""",
  'why':'3단계 이상의 포인터 중첩(int***)은 각 단계가 무엇을 가리키는지 추적하기 어려워 오용과 검증 실패를 부른다. 간접 단계를 구조체로 캡슐화해 의미를 부여하면 중첩을 2단계 이하로 낮출 수 있다.',
  'why_en':'Three or more levels of pointer nesting (int***) make it hard to track what each level points to, inviting misuse and verification failure. Encapsulating indirection in a struct gives it meaning and reduces nesting to two levels or fewer.'},

 {'id':'Rule 18.6','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'자동 저장기간 객체의 주소를 그 수명 밖으로 내보내지 않는다',
  'title_en':'The address of an object with automatic storage shall not be copied to another object that persists after the first object has ceased to exist',
  'bad': r"""#include <stdio.h>
static int *make(void){
    int local = 42;
    return &local;   /* 함수 종료 후 무효가 되는 지역 변수의 주소 반환 */
}
int main(void){
    int *p = make();
    printf("%d\n", *p);   /* 무효 메모리 역참조 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void make(int *out){
    *out = 42;        /* 호출자가 소유한 저장소에 기록 */
}
int main(void){
    int value;
    make(&value);     /* 수명이 보장된 객체를 전달 */
    printf("%d\n", value);
    return 0;
}""",
  'why':'지역 변수는 함수가 반환되면 수명이 끝나 그 주소가 무효가 되므로, 주소를 반환·보관해 역참조하면 사라진 스택 프레임을 가리키는 미정의 동작이 된다. 결과는 호출자가 소유한 저장소나 정적 저장기간 객체에 기록한다.',
  'why_en':'A local variable’s lifetime ends when the function returns, so its address becomes invalid; returning or retaining it and dereferencing it points at a vanished stack frame — undefined behaviour. Write results into caller-owned storage or an object with static storage duration.'},

 {'id':'Rule 18.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'유연 배열 멤버(flexible array member)를 선언하지 않는다',
  'title_en':'Flexible array members shall not be declared',
  'bad': r"""#include <stdio.h>
struct Packet { int len; char data[]; };   /* 유연 배열 멤버 — 크기가 런타임 결정 */
int main(void){
    /* sizeof(struct Packet) 가 data 를 포함하지 않아 경계 검사·정적 분석이 어렵다 */
    printf("%zu\n", sizeof(struct Packet));
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define MAX_DATA 256
struct Packet { int len; char data[MAX_DATA]; };   /* 최대 크기 고정 배열 */
int main(void){
    struct Packet p = { 0, {0} };
    printf("%zu\n", sizeof p);   /* 크기가 정적으로 결정 — 경계 검사 가능 */
    return 0;
}""",
  'why':'유연 배열 멤버는 실제 크기가 런타임 할당에 따라 정해져 sizeof 로 알 수 없으므로, 정적 경계 검사와 메모리 사용량 분석을 어렵게 한다. 최대 크기를 갖는 고정 배열로 대체하면 크기가 컴파일 시 결정되어 검증이 쉬워진다.',
  'why_en':'A flexible array member’s actual size is set by run-time allocation and is unknown via sizeof, hampering static bounds checking and memory-usage analysis. Replacing it with a fixed array of maximum size makes the size compile-time determined and easy to verify.'},

 {'id':'Rule 18.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'가변 길이 배열(VLA)을 사용하지 않는다',
  'title_en':'Variable-length array types shall not be used',
  'bad': r"""#include <stdio.h>
static int sum_first(int n){
    int buf[n];          /* VLA — 스택 사용량이 n 에 따라 달라져 정적 분석 불가 */
    int s = 0;
    for (int i = 0; i < n; i++) { buf[i] = i; s += buf[i]; }
    return s;
}
int main(void){ printf("%d\n", sum_first(5)); return 0; }""",
  'good': r"""#include <stdio.h>
#define MAX_N 128
static int sum_first(int n){
    int buf[MAX_N];      /* 컴파일 시 고정 크기 — 스택 사용량 결정적 */
    if (n > MAX_N) { return -1; }
    int s = 0;
    for (int i = 0; i < n; i++) { buf[i] = i; s += buf[i]; }
    return s;
}
int main(void){ printf("%d\n", sum_first(5)); return 0; }""",
  'why':'가변 길이 배열은 크기가 런타임 값에 의존해 최대 스택 사용량을 정적으로 알 수 없으므로, 큰 입력에서 스택 오버플로우 위험이 있다. 컴파일 시 크기가 고정된 배열을 쓰고 입력을 그 한계와 비교해 결정적인 메모리 사용을 보장한다.',
  'why_en':'A variable-length array’s size depends on a run-time value, so maximum stack usage cannot be known statically, risking stack overflow on large inputs. Use a compile-time fixed-size array and compare the input against its limit to guarantee deterministic memory use.'},

 {'id':'Rule 19.2','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'union 키워드 사용을 피한다',
  'title_en':'The union keyword should not be used',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
union Conv { uint32_t u; float f; };   /* union 을 통한 타입 퍼닝 */
int main(void){
    union Conv c;
    c.u = 0x40490FDBu;
    float pi = c.f;     /* 마지막에 쓰지 않은 멤버 읽기 — 구현정의 동작 */
    printf("%f\n", pi);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
#include <string.h>
int main(void){
    uint32_t u = 0x40490FDBu;
    float pi;
    memcpy(&pi, &u, sizeof pi);   /* 명시적 바이트 재해석 — 의도가 분명 */
    printf("%f\n", pi);
    return 0;
}""",
  'why':'union 의 한 멤버에 쓴 뒤 다른 멤버를 읽는 타입 퍼닝은 표현이 다른 타입을 재해석하는 것이라 구현정의 동작이 되고, 코드만으로 의도를 파악하기 어렵다. memcpy 로 바이트 단위 재해석을 명시하면 동작이 정의되고 의도가 드러난다.',
  'why_en':'Writing one union member and reading another (type punning) reinterprets a differently represented type, which is implementation-defined and whose intent is unclear from the code. Using memcpy to spell out the byte-wise reinterpretation makes the behaviour defined and the intent explicit.'},

 {'id':'Rule 20.1','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'#include 지시문 앞에는 전처리기 지시문/주석만 둔다',
  'title_en':'#include directives should only be preceded by preprocessor directives or comments',
  'bad': r"""int x = 0;            /* 코드가 먼저 등장 */
#include <string.h>   /* 코드 뒤의 #include — 포함 순서 의존·가독성 저하 */
int main(void){
    char b[4];
    memset(b, 0, sizeof b);
    return x + b[0];
}""",
  'good': r"""#include <string.h>   /* 모든 #include 를 파일 상단에 모음 */
int x = 0;
int main(void){
    char b[4];
    memset(b, 0, sizeof b);
    return x + b[0];
}""",
  'why':'코드 중간에 등장하는 #include 는 그 위치까지의 선언·매크로 상태에 따라 포함 결과가 달라지는 순서 의존 결함을 만들고, 의존 관계를 한눈에 파악하기 어렵게 한다. 모든 #include 를 파일 상단에 모아 포함 순서를 단순하고 예측 가능하게 한다.',
  'why_en':'An #include in the middle of code creates order-dependent defects, since what it pulls in can depend on the declarations and macros seen so far, and it obscures dependencies. Collecting all #includes at the top of the file makes inclusion order simple and predictable.'},

 {'id':'Rule 20.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'#include 뒤에는 <헤더> 또는 "헤더" 형태만 온다',
  'title_en':'The #include directive shall be followed by either a <filename> or "filename" sequence',
  'bad': r"""#define HDR <string.h>
#include HDR          /* 매크로 확장으로 헤더명을 만듦 — 올바른 형식 보장 안 됨 */
int main(void){
    char b[4];
    memset(b, 0, sizeof b);
    return b[0];
}""",
  'good': r"""#include <string.h>   /* 직접 헤더명을 명시 */
int main(void){
    char b[4];
    memset(b, 0, sizeof b);
    return b[0];
}""",
  'why':'매크로 확장으로 헤더명을 생성하면 확장 결과가 올바른 <...> 또는 "..." 형식이 된다는 보장이 없어, 컴파일러·이식 환경마다 다르게 해석되는 위험이 있다. #include 에는 헤더명을 직접 적어 형식을 고정한다.',
  'why_en':'Generating a header name via macro expansion does not guarantee the result is a valid <...> or "..." form, risking different interpretations across compilers and ports. Write the header name directly in #include to fix the form.'},

 {'id':'Rule 20.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'키워드와 같은 이름의 매크로를 정의하지 않는다',
  'title_en':'A macro shall not be defined with the same name as a keyword',
  'bad': r"""#include <stdio.h>
#define while if      /* 키워드를 매크로로 재정의 — 모든 사용처의 의미가 바뀜 */
int main(void){
    int n = 0;
    while (n < 3) {    /* 'while' 가 'if' 로 치환되어 루프가 한 번만 실행됨 */
        printf("%d\n", n);
        n++;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int n = 0;
    while (n < 3) {    /* 키워드는 키워드 그대로 */
        printf("%d\n", n);
        n++;
    }
    return 0;
}""",
  'why':'키워드를 매크로로 재정의하면 그 키워드를 쓰는 모든 코드의 의미가 조용히 바뀌어(while 이 if 가 되는 등) 추적 불가능한 전역 혼란을 일으킨다. 키워드 이름의 매크로 정의를 금지하고, 별칭이 필요하면 typedef 등 정상 수단을 쓴다.',
  'why_en':'Redefining a keyword as a macro silently changes the meaning of all code using that keyword (e.g., while becomes if), causing untraceable global chaos. Never define a macro with a keyword name; use proper means such as typedef when an alias is needed.'},

 {'id':'Rule 20.5','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'#undef 를 사용하지 않는다',
  'title_en':'#undef should not be used',
  'bad': r"""#include <stdio.h>
#define LIMIT 100
/* ... 일부 코드에서 LIMIT=100 으로 사용 ... */
#undef LIMIT          /* 같은 이름이 위치마다 다른 의미를 갖게 됨 — 추적 곤란 */
#define LIMIT 200
int main(void){ printf("%d\n", LIMIT); return 0; }""",
  'good': r"""#include <stdio.h>
#define LIMIT_LOW  100   /* 서로 다른 값은 서로 다른 이름으로 */
#define LIMIT_HIGH 200
int main(void){ printf("%d %d\n", LIMIT_LOW, LIMIT_HIGH); return 0; }""",
  'why':'#undef 후 재정의는 같은 매크로 이름이 소스 위치에 따라 다른 값을 갖게 만들어, 어느 코드가 어떤 값을 보는지 추적하기 어렵고 리뷰 오류를 부른다. 서로 다른 의미·값은 서로 다른 매크로 이름으로 정의해 수명과 의미를 명확히 한다.',
  'why_en':'Redefining after #undef makes the same macro name hold different values depending on source position, making it hard to trace which value a given piece of code sees and inviting review errors. Define distinct meanings/values under distinct macro names to keep lifetime and meaning clear.'},

 {'id':'Rule 20.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'함수형 매크로의 매개변수는 괄호로 감싼다',
  'title_en':'Expressions resulting from the expansion of macro parameters shall be enclosed in parentheses',
  'bad': r"""#include <stdio.h>
#define SCALE(x) x * 2      /* 매개변수·전체 식을 괄호로 감싸지 않음 */
int main(void){
    int a = 1, b = 2;
    int r = SCALE(a + b);   /* a + b * 2 = 5 로 전개됨 (의도는 6) */
    printf("%d\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define SCALE(x) ((x) * 2)  /* 각 매개변수와 전체 식을 괄호로 보호 */
int main(void){
    int a = 1, b = 2;
    int r = SCALE(a + b);   /* ((a + b) * 2) = 6 */
    printf("%d\n", r);
    return 0;
}""",
  'why':'함수형 매크로에서 매개변수와 전체 식을 괄호로 감싸지 않으면, 전개 시 호출부 표현식과 매크로 본문의 연산자 우선순위가 섞여 SCALE(a+b) 가 a + b*2 처럼 의도와 다른 식이 된다. 각 매개변수와 결과 전체를 괄호로 보호한다.',
  'why_en':'Without parenthesizing the parameters and the whole expression in a function-like macro, expansion mixes the caller’s expression with the macro body’s operator precedence, turning SCALE(a+b) into a + b*2. Protect each parameter and the entire result with parentheses.'},

 {'id':'Rule 20.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'#if/#elif 의 제어 표현식은 0 또는 1로 평가되어야 한다',
  'title_en':'The controlling expression of a #if or #elif preprocessing directive shall evaluate to 0 or 1',
  'bad': r"""#include <stdio.h>
#if CONFIG_NAME        /* 정의 안 됐거나 숫자가 아니면 의도와 다르게 평가됨 */
#define MODE_STR "named"
#else
#define MODE_STR "default"
#endif
int main(void){ printf("%s\n", MODE_STR); return 0; }""",
  'good': r"""#include <stdio.h>
#if defined(CONFIG_FEATURE) && (CONFIG_FEATURE == 1)   /* 0/1 로 명확히 평가 */
#define MODE_STR "feature on"
#else
#define MODE_STR "feature off"
#endif
int main(void){ printf("%s\n", MODE_STR); return 0; }""",
  'why':'정의되지 않았거나 불리언이 아닌 매크로를 #if 에 직접 쓰면 전처리기가 그 토큰을 0 으로 치환하거나 임의 정수로 해석해, 의도하지 않은 분기가 선택된다. defined() 로 존재를 확인하고 명시적 비교로 결과를 0/1 로 보장한다.',
  'why_en':'Using an undefined or non-Boolean macro directly in #if makes the preprocessor substitute 0 or interpret an arbitrary integer, selecting an unintended branch. Confirm existence with defined() and use explicit comparison to guarantee a 0/1 result.'},

 {'id':'Rule 20.9','cat':'Required · Decidable · Rule','compiles':True,
  'title':'#if/#elif 에 쓰는 식별자는 정의 여부를 defined 로 먼저 확인한다',
  'title_en':'All identifiers used in the controlling expression of #if or #elif shall be defined before evaluation',
  'bad': r"""#include <stdio.h>
#if MODE == 2          /* MODE 미정의 시 0 으로 간주되어 0 == 2 (거짓) — 오판 */
#define SEL "mode2"
#else
#define SEL "other"
#endif
int main(void){ printf("%s\n", SEL); return 0; }""",
  'good': r"""#include <stdio.h>
#if defined(MODE) && (MODE == 2)   /* 존재를 먼저 확인한 뒤 값 비교 */
#define SEL "mode2"
#else
#define SEL "other"
#endif
int main(void){ printf("%s\n", SEL); return 0; }""",
  'why':'정의되지 않은 식별자는 #if 평가 시 0 으로 치환되므로, MODE 가 없을 때 MODE == 2 가 조용히 거짓이 되어 의도와 다른 분기가 선택되고 오타·구성 누락을 숨긴다. defined() 로 존재를 먼저 확인한 뒤 값을 비교한다.',
  'why_en':'An undefined identifier is replaced by 0 during #if evaluation, so when MODE is absent, MODE == 2 silently becomes false, selecting the wrong branch and hiding typos or missing configuration. Confirm existence with defined() before comparing the value.'},

 {'id':'Rule 20.10','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'전처리기 연산자 # 와 ## 사용을 피한다',
  'title_en':'The # and ## preprocessor operators should not be used',
  'bad': r"""#include <stdio.h>
#define MAKE(name) int var_##name = 0   /* ## 토큰 결합 — 디버깅·검색이 어려움 */
int main(void){
    MAKE(abc);
    return var_abc;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int var_abc = 0;   /* 명시적 선언 — 도구로 검색·디버깅이 쉬움 */
    return var_abc;
}""",
  'why':'#(문자열화)와 ##(토큰 결합)은 전처리 후에야 실제 식별자가 만들어져, 소스에서 그 이름을 검색·디버깅하기 어렵고 평가 순서도 까다로워 미묘한 버그를 숨긴다. 가능하면 명시적 코드로 대체해 추적성을 확보한다.',
  'why_en':'# (stringize) and ## (token paste) form the real identifier only after preprocessing, making the name hard to search and debug and their evaluation order tricky, hiding subtle bugs. Replace them with explicit code where possible for traceability.'},

 {'id':'Rule 20.12','cat':'Required · Decidable · Rule',
  'title':'# 또는 ## 의 피연산자가 되는 매크로 매개변수를 일관되게 사용한다',
  'title_en':'A macro parameter used as an operand to the # or ## operators shall only be used as such',
  'bad': r"""/* a 가 ## 의 피연산자이면서 동시에 일반 확장에도 쓰임 — 확장 결과가 모호 */
#define JOIN_AND_USE(a) a ## _suffix a
/* 호출부에서 a 가 한 번은 토큰 결합, 한 번은 일반 치환되어 전처리 결과 예측이 어렵다 */""",
  'good': r"""/* 매개변수를 한 가지 용도(토큰 결합)로만 사용 */
#define LABEL(a) a ## _suffix
/* 일반 확장이 필요하면 별도의 매개변수/매크로로 분리한다 */""",
  'why':'한 매크로 매개변수를 ## 의 피연산자(토큰 결합)와 일반 확장에 동시에 쓰면, 전처리기가 인자를 먼저 확장할지 결합할지에 따라 결과가 달라져 전개 결과가 모호해진다. 매개변수는 한 가지 용도로만 일관되게 사용한다.',
  'why_en':'Using one macro parameter both as an operand of ## (token paste) and in ordinary expansion makes the result depend on whether the preprocessor expands or pastes the argument first, making expansion ambiguous. Use a parameter for only one purpose, consistently.'},

 {'id':'Rule 20.13','cat':'Required · Decidable · Rule',
  'title':'# 으로 시작하는 줄은 올바른 전처리기 지시문이어야 한다',
  'title_en':'A line whose first token is # shall be a valid preprocessing directive',
  'bad': r"""# include_file "config.h"
/* '#' 뒤가 표준 지시문 철자(include/define/if ...)가 아님 — 미정의·이식성 문제 */""",
  'good': r"""#include "config.h"
/* '#' 으로 시작하는 줄은 표준 지시문 철자만 사용한다 */""",
  'why':'# 으로 시작하지만 include/define/if 같은 표준 지시문 철자가 아닌 줄은, 일부 컴파일러가 무시하거나 확장 지시문으로 해석하는 등 미정의·비이식 동작을 만든다. # 으로 시작하는 줄은 반드시 표준 전처리기 지시문 형태를 따른다.',
  'why_en':'A line starting with # that is not a standard directive spelling (include/define/if, …) is ignored by some compilers and treated as an extension directive by others — undefined, non-portable behaviour. Lines beginning with # must follow a standard preprocessing-directive form.'},

 {'id':'Rule 20.14','cat':'Required · Decidable · Rule',
  'title':'#else/#endif 는 대응하는 #if 와 같은 파일에 둔다',
  'title_en':'All #else, #elif and #endif preprocessor directives shall reside in the same file as the #if to which they relate',
  'bad': r"""/* a.h */
#if CONFIG_X
/* ... 선언 ... */

/* b.h (a.h 에 이어 포함됨) */
#endif    /* 대응 #endif 가 다른 파일에 있음 — 포함 순서에 따라 동작이 달라짐 */""",
  'good': r"""/* a.h — #if 와 #endif 를 같은 파일에서 짝지음 */
#if CONFIG_X
/* ... 선언 ... */
#endif

/* b.h — 독립적으로 자신의 조건부 블록을 닫음 */""",
  'why':'조건부 컴파일 지시문(#if/#else/#endif)이 파일 경계를 가로질러 매칭되면, 헤더 포함 순서에 따라 어떤 #if 와 짝지어지는지 달라져 빌드 구성이 깨지기 쉽다. #if 와 그 #else/#endif 를 같은 파일 안에서 짝지어 구조를 자기완결적으로 만든다.',
  'why_en':'When conditional-compilation directives (#if/#else/#endif) match across file boundaries, which #if they pair with depends on header inclusion order, easily breaking the build configuration. Pair an #if with its #else/#endif within the same file so each block is self-contained.'},

 {'id':'Rule 21.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'예약 식별자/매크로 이름을 #define 하거나 #undef 하지 않는다',
  'title_en':'#define and #undef shall not be used on a reserved identifier or reserved macro name',
  'bad': r"""#include <stdio.h>
#define _MAX 100        /* 밑줄+대문자로 시작 — 구현이 예약한 이름 영역 */
int main(void){ printf("%d\n", _MAX); return 0; }""",
  'good': r"""#include <stdio.h>
#define APP_MAX 100      /* 비예약(애플리케이션) 이름 */
int main(void){ printf("%d\n", APP_MAX); return 0; }""",
  'why':'밑줄로 시작하는 이름이나 표준이 예약한 매크로를 재정의·해제하면 구현 내부 헤더·매크로와 충돌해 진단 없는 미정의 동작이 된다. 애플리케이션 고유의 비예약 이름(예: APP_ 접두사)만 정의한다.',
  'why_en':'Defining or undefining a leading-underscore name or a Standard-reserved macro collides with the implementation’s internal headers and macros, causing undiagnosed undefined behaviour. Define only application-specific, non-reserved names (e.g., an APP_ prefix).'},

 {'id':'Rule 21.2','cat':'Required · Undecidable · Rule',
  'title':'예약된 식별자/함수 이름을 선언하거나 정의하지 않는다',
  'title_en':'A reserved identifier or reserved macro name shall not be declared',
  'bad': r"""/* 표준 라이브러리 함수명을 사용자 함수로 재정의 — 충돌·미정의 동작 */
size_t memcpy(int x) {     /* 'memcpy' 는 표준이 예약 */
    return (size_t)x;
}""",
  'good': r"""/* 고유한 사용자 이름을 사용 */
size_t copy_block(int x) {
    return (size_t)x;
}""",
  'why':'memcpy·strlen 같은 표준 라이브러리 이름이나 구현 예약 이름을 사용자가 선언·정의하면, 표준 헤더의 선언·내장 함수와 충돌해 링크 오류나 미정의 동작이 발생한다. 예약 영역과 겹치지 않는 고유한 사용자 이름을 사용한다.',
  'why_en':'Declaring or defining a Standard library name like memcpy or strlen, or any reserved identifier, collides with declarations in standard headers and built-ins, causing link errors or undefined behaviour. Use unique, application-specific names that do not overlap the reserved space.'},

 {'id':'Rule 21.3','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'<stdlib.h> 의 동적 메모리 함수(malloc/calloc/realloc/free)를 쓰지 않는다',
  'title_en':'The memory allocation and deallocation functions of <stdlib.h> shall not be used',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
static int process(int *buf, int n){ int s = 0; for (int i=0;i<n;i++){ buf[i]=i; s+=buf[i]; } return s; }
int main(void){
    int n = 4;
    int *buf = malloc((size_t)n * sizeof(int));   /* 동적 할당 — 단편화·실패·누수·이중해제 위험 */
    if (buf == NULL) { return 1; }
    int s = process(buf, n);
    free(buf);
    printf("%d\n", s);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#define MAX_N 256
static int process(int *buf, int n){ int s = 0; for (int i=0;i<n;i++){ buf[i]=i; s+=buf[i]; } return s; }
int main(void){
    int n = 4;
    int buf[MAX_N];               /* 정적/자동 저장소 — 결정적 메모리 */
    if (n > MAX_N) { return 1; }
    printf("%d\n", process(buf, n));
    return 0;
}""",
  'why':'동적 할당은 힙 단편화, 비결정적 할당 시간, 할당 실패, 누수·이중해제 위험을 동반해 안전필수 시스템의 장기 가동 신뢰성을 떨어뜨린다. 컴파일 시 크기가 정해지는 정적/자동 저장소로 대체해 메모리 사용을 결정적이고 검증 가능하게 만든다.',
  'why_en':'Dynamic allocation brings heap fragmentation, non-deterministic allocation time, allocation failure, and leak/double-free risks that undermine long-uptime reliability in safety-critical systems. Replace it with statically/automatically sized storage to make memory use deterministic and verifiable.'},

 {'id':'Rule 21.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<setjmp.h> 를 사용하지 않는다',
  'title_en':'The standard header file <setjmp.h> shall not be used',
  'bad': r"""#include <setjmp.h>
#include <stdio.h>
static jmp_buf env;
static void recover(void){ printf("recovered\n"); }
int main(void){
    if (setjmp(env) != 0) { recover(); return 0; }   /* 비국소 점프 — 자원 해제 건너뜀 */
    /* ... longjmp(env, 1) 로 이 지점으로 되돌아올 수 있음 ... */
    return 0;
}""",
  'good': r"""#include <stdio.h>
enum { OK = 0, ERR_IO = 1 };
static int do_work(void){ return OK; }
static void recover(void){ printf("recovered\n"); }
int main(void){
    int rc = do_work();          /* 반환값으로 오류를 전파 — 흐름이 명시적 */
    if (rc != OK) { recover(); }
    return 0;
}""",
  'why':'setjmp/longjmp 의 비국소 점프는 중간 스택 프레임의 자원 해제·소멸 처리를 건너뛰고 제어 흐름을 코드만으로 추적할 수 없게 만들어 누수와 일관성 깨짐을 부른다. 오류는 반환값(또는 상태 코드)으로 명시적으로 전파한다.',
  'why_en':'The non-local jump of setjmp/longjmp skips resource release in intermediate stack frames and makes control flow untraceable from the code, causing leaks and inconsistency. Propagate errors explicitly through return values or status codes.'},

 {'id':'Rule 21.5','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<signal.h> 의 시그널 기능을 사용하지 않는다',
  'title_en':'The standard header file <signal.h> shall not be used',
  'bad': r"""#include <signal.h>
#include <stdio.h>
static void handler(int s){ (void)s; }   /* 시그널 핸들러 — 비동기·구현정의 동작 */
int main(void){
    signal(SIGINT, handler);   /* 시그널 처리는 안전필수 환경에서 예측 불가 */
    printf("running\n");
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int stop_requested(void){ return 1; }   /* 상태 플래그를 협조적으로 검사 */
static void step(void){ /* 한 단계 처리 */ }
int main(void){
    while (!stop_requested()) {   /* 협조적 폴링 — 결정적이고 추적 가능 */
        step();
    }
    printf("stopped\n");
    return 0;
}""",
  'why':'시그널은 임의 시점에 비동기로 끼어들고 핸들러에서 할 수 있는 일이 구현정의·제한적이라, 안전필수 환경에서 경쟁·재진입·예측 불가 동작을 만든다. 종료·이벤트 요청은 상태 플래그를 협조적으로 폴링하는 결정적 메커니즘으로 처리한다.',
  'why_en':'Signals interrupt asynchronously at arbitrary points and what a handler may do is implementation-defined and limited, producing races, reentrancy, and unpredictable behaviour in safety-critical environments. Handle shutdown/event requests with a deterministic mechanism that cooperatively polls a status flag.'},

 {'id':'Rule 21.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'표준 라이브러리 입출력 함수(<stdio.h>)를 사용하지 않는다',
  'title_en':'The Standard Library input/output functions shall not be used',
  'bad': r"""#include <stdio.h>
int main(void){
    int t = 25;
    printf("temp=%d\n", t);   /* 포맷 I/O — 포맷 문자열·버퍼·예외 동작 위험 */
    return 0;
}""",
  'good': r"""static void uart_write_str(const char *s){ (void)s; /* 검증된 전용 출력 */ }
static void uart_write_int(const char *label, int v){ (void)label; (void)v; }
int main(void){
    int t = 25;
    uart_write_int("temp=", t);   /* 검증된 전용 입출력 계층 */
    uart_write_str("\n");
    return 0;
}""",
  'why':'stdio 의 포맷 입출력은 포맷 문자열 취약점, 가려진 버퍼링, 구현정의 예외 동작 등 안전필수 시스템에 부적합한 위험을 동반한다. 동작이 검증된 전용 I/O 계층(예: UART 드라이버)을 사용해 입출력 경로를 통제한다.',
  'why_en':'stdio formatted I/O carries risks unsuitable for safety-critical systems — format-string vulnerabilities, hidden buffering, implementation-defined exceptional behaviour. Use a validated dedicated I/O layer (e.g., a UART driver) to keep I/O paths controlled.'},

 {'id':'Rule 21.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'atoi/atol/atoll/atof 변환 함수를 사용하지 않는다',
  'title_en':'The Standard Library functions atof, atoi, atol and atoll shall not be used',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int n = atoi("99999999999abc");   /* 변환 실패·범위 초과를 알 수 없음 */
    printf("%d\n", n);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>
int main(void){
    const char *text = "12345";
    char *end;
    errno = 0;
    long v = strtol(text, &end, 10);
    if (end == text || *end != '\0' || errno == ERANGE || v < INT_MIN || v > INT_MAX) {
        printf("conversion error\n");   /* 오류를 명확히 검출 */
        return 1;
    }
    printf("%d\n", (int)v);
    return 0;
}""",
  'why':'atoi 계열은 변환 실패와 정상적인 0, 범위 초과를 전혀 구분하지 못해 잘못된 값을 조용히 반환하고, 이후 계산에 오류가 전파된다. end 포인터·errno 로 변환 결과를 검사할 수 있는 strtol 계열을 사용한다.',
  'why_en':'The atoi family cannot distinguish a failed conversion, a legitimate 0, or out-of-range input, silently returning a wrong value that propagates into later computation. Use the strtol family, whose end pointer and errno let you verify the conversion.'},

 {'id':'Rule 21.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<stdlib.h> 의 system/abort/exit/getenv 를 사용하지 않는다',
  'title_en':'The library functions abort, exit, getenv and system of <stdlib.h> shall not be used',
  'bad': r"""#include <stdlib.h>
int main(void){
    char *home = getenv("HOME");   /* 신뢰할 수 없는 환경 의존 */
    (void)home;
    system("rm -f /tmp/lock");     /* 셸을 거침 — 인젝션·환경 의존 위험 */
    return 0;
}""",
  'good': r"""static void remove_lock_file(void){ /* 셸 없이 내부 API 로 파일 제거 */ }
int main(void){
    remove_lock_file();   /* 외부 셸 호출·환경 변수 의존 없이 처리 */
    return 0;
}""",
  'why':'system 은 셸을 거쳐 명령 인젝션 위험이 있고, getenv 는 신뢰할 수 없는 외부 환경에 의존하며, abort/exit 는 등록된 정리 루틴이나 자원 해제를 건너뛸 수 있다. 동일 기능을 내부 API와 정상 반환 경로로 대체한다.',
  'why_en':'system runs through a shell with command-injection risk, getenv depends on an untrusted external environment, and abort/exit can skip registered cleanup or resource release. Replace these with internal APIs and normal return paths.'},

 {'id':'Rule 21.9','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<stdlib.h> 의 bsearch/qsort 를 사용하지 않는다',
  'title_en':'The library functions bsearch and qsort of <stdlib.h> shall not be used',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
static int cmp(const void *a, const void *b){ return (*(const int *)a) - (*(const int *)b); }
int main(void){
    int a[5] = {3, 1, 4, 1, 5};
    qsort(a, 5, sizeof(int), cmp);   /* 콜백 의존·구현별 동작 차이 — 결정성 저하 */
    printf("%d\n", a[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void insertion_sort(int *a, int n){
    for (int i = 1; i < n; i++) {
        int key = a[i], j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = key;
    }
}
int main(void){
    int a[5] = {3, 1, 4, 1, 5};
    insertion_sort(a, 5);   /* 검증된 자체 알고리즘 — 결정적 동작 */
    printf("%d\n", a[0]);
    return 0;
}""",
  'why':'qsort/bsearch 는 함수 포인터 콜백에 의존하고 정렬 안정성·동작이 구현마다 달라, 결과의 결정성과 정적 검증성을 떨어뜨린다. 동작이 검증된 자체 정렬·탐색 루틴으로 대체해 모든 입력에서 동일하고 예측 가능한 결과를 보장한다.',
  'why_en':'qsort/bsearch rely on function-pointer callbacks and have implementation-varying stability and behaviour, reducing determinism and static verifiability. Replace them with validated in-house sort/search routines that guarantee identical, predictable results for all inputs.'},

 {'id':'Rule 21.10','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<time.h> 의 날짜/시간 함수를 사용하지 않는다',
  'title_en':'The Standard Library time and date functions shall not be used',
  'bad': r"""#include <time.h>
#include <stdio.h>
int main(void){
    time_t now = time(NULL);   /* 구현정의 동작·환경(시스템 클록) 의존 */
    printf("%ld\n", (long)now);
    return 0;
}""",
  'good': r"""#include <stdint.h>
#include <stdio.h>
static uint32_t rtc_get_ticks(void){ return 1000u; }   /* 하드웨어 타이머 추상화 */
int main(void){
    uint32_t ticks = rtc_get_ticks();   /* 결정적·검증 가능한 시간 소스 */
    printf("%u\n", ticks);
    return 0;
}""",
  'why':'표준 시간 함수(time/localtime/strftime 등)는 구현정의 동작과 시스템 클록·로캘 같은 환경 의존성이 커, 안전필수 시스템에서 동작을 재현·검증하기 어렵다. 하드웨어 타이머를 감싼 추상화 계층을 사용해 시간 소스를 결정적으로 통제한다.',
  'why_en':'Standard time functions (time/localtime/strftime, …) have implementation-defined behaviour and depend on the system clock and locale, making them hard to reproduce and verify in safety-critical systems. Use a hardware-timer abstraction layer to keep the time source deterministic and controlled.'},

 {'id':'Rule 21.11','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<tgmath.h> 타입-제네릭 수학 매크로를 사용하지 않는다',
  'title_en':'The standard header file <tgmath.h> shall not be used',
  'bad': r"""#include <tgmath.h>
#include <stdio.h>
int main(void){
    float x = 2.0f;
    double r = sqrt(x);   /* 인자 타입에 따라 sqrtf/sqrt/sqrtl 중 무엇이 호출될지 가려짐 */
    printf("%f\n", r);
    return 0;
}""",
  'good': r"""#include <math.h>
#include <stdio.h>
int main(void){
    float x = 2.0f;
    double r = sqrt((double)x);   /* 호출할 함수가 명확(sqrt, double 정밀도) */
    printf("%f\n", r);
    return 0;
}""",
  'why':'tgmath 의 타입-제네릭 매크로는 인자 타입에 따라 sqrtf/sqrt/sqrtl 중 하나를 자동 선택해, 실제로 어떤 정밀도의 함수가 호출되는지 코드만으로 알 수 없어 의도 파악과 정적 분석을 어렵게 한다. <math.h> 의 타입별 함수를 명시적으로 호출한다.',
  'why_en':'tgmath’s type-generic macros auto-select among sqrtf/sqrt/sqrtl based on argument type, so which precision is actually called is not evident from the code, hampering intent and static analysis. Call the type-specific functions from <math.h> explicitly.'},

 {'id':'Rule 21.13','cat':'Mandatory · Undecidable · Rule','compiles':True,
  'title':'<ctype.h> 함수 인자는 unsigned char 로 표현 가능하거나 EOF 여야 한다',
  'title_en':'Any value passed to a function in <ctype.h> shall be representable as an unsigned char or be the value EOF',
  'bad': r"""#include <ctype.h>
#include <stdio.h>
int main(void){
    char c = (char)0xC0;   /* signed char 환경이면 음수 */
    if (isdigit(c)) {      /* 음수를 ctype 함수에 전달 — 미정의 동작 */
        printf("digit\n");
    }
    return 0;
}""",
  'good': r"""#include <ctype.h>
#include <stdio.h>
int main(void){
    char c = (char)0xC0;
    if (isdigit((unsigned char)c)) {   /* unsigned char 로 캐스트 — 유효 범위 보장 */
        printf("digit\n");
    } else {
        printf("not a digit\n");
    }
    return 0;
}""",
  'why':'ctype 함수는 인자가 unsigned char 범위(0..UCHAR_MAX) 또는 EOF 일 것을 요구하는데, signed char 가 음수일 때 그대로 넘기면 음수 인덱스로 내부 테이블을 접근해 미정의 동작이 된다. 인자를 unsigned char 로 캐스트해 유효 범위를 보장한다.',
  'why_en':'ctype functions require the argument to be in the unsigned char range (0..UCHAR_MAX) or EOF; passing a negative signed char indexes their internal table with a negative value — undefined behaviour. Cast the argument to unsigned char to guarantee a valid range.'},

 {'id':'Rule 21.14','cat':'Required · Decidable · Rule','compiles':True,
  'title':'memcmp 로 널 종료 문자열을 비교하지 않는다',
  'title_en':'The Standard Library function memcmp shall not be used to compare null terminated strings',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    const char *a = "cat";
    const char *b = "catalog";
    if (memcmp(a, b, strlen(a)) == 0) {   /* 앞 3바이트만 비교 — 길이 차이 무시 */
        printf("equal\n");                /* "cat" 과 "catalog" 를 같다고 오판 */
    }
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    const char *a = "cat";
    const char *b = "catalog";
    if (strcmp(a, b) == 0) {   /* 널 종료까지 고려한 문자열 비교 */
        printf("equal\n");
    } else {
        printf("not equal\n");
    }
    return 0;
}""",
  'why':'memcmp 는 널 종료를 인식하지 못하고 지정한 고정 길이만 바이트 비교하므로, 접두사가 같고 길이가 다른 문자열("cat" vs "catalog")을 같다고 잘못 판단할 수 있다. 널 종료 문자열 비교에는 종료자를 고려하는 strcmp 를 사용한다.',
  'why_en':'memcmp does not recognize null termination and compares only the specified fixed length of bytes, so it can wrongly judge strings with a shared prefix but different lengths ("cat" vs "catalog") as equal. Use strcmp, which accounts for the terminator, to compare null-terminated strings.'},

 {'id':'Rule 21.15','cat':'Required · Decidable · Rule','compiles':True,
  'title':'memcpy/memmove/memcmp 의 포인터 인자는 호환되는 타입이어야 한다',
  'title_en':'The pointer arguments to the Standard Library functions memcpy, memmove and memcmp shall be pointers to qualified or unqualified versions of compatible types',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    float f[4] = {0};
    int   i[4] = {1, 2, 3, 4};
    memcpy(f, i, sizeof f);   /* int 표현을 float 로 복사 — 잘못된 비트 패턴 */
    printf("%f\n", f[0]);
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    int src[4] = {1, 2, 3, 4};
    int dst[4] = {0};
    memcpy(dst, src, sizeof dst);   /* 동일 타입 간 복사 — 표현이 일치 */
    printf("%d\n", dst[0]);
    return 0;
}""",
  'why':'표현(비트 배치)이 다른 타입 사이에서 memcpy 로 바이트를 복사하면, 원본의 비트 패턴이 대상 타입에서는 전혀 다른 값(예: int 4 가 float 의 비정상 값)으로 해석된다. 메모리 함수의 두 포인터 인자는 호환되는 같은 타입을 가리키게 한다.',
  'why_en':'Copying bytes with memcpy between types of different representation makes the source bit pattern mean something entirely different in the destination type (e.g., int 4 as a denormal float). Ensure both pointer arguments of memory functions point to compatible, like types.'},

 {'id':'Rule 21.17','cat':'Mandatory · Undecidable · Rule','compiles':True,
  'title':'문자열 함수 사용 시 대상 버퍼 경계를 벗어나지 않는다',
  'title_en':'Use of the string handling functions from <string.h> shall not result in accesses beyond the bounds of the objects',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char dst[8];
    const char *src = "this is too long";
    strcpy(dst, src);   /* dst(8) 보다 긴 src 복사 — 버퍼 오버플로우 */
    printf("%s\n", dst);
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char dst[8];
    const char *src = "this is too long";
    size_t n = strlen(src);
    if (n < sizeof dst) {           /* 길이를 확인하고 경계 내에서만 복사 */
        memcpy(dst, src, n + 1);
        printf("%s\n", dst);
    } else {
        printf("source too long (%zu)\n", n);
    }
    return 0;
}""",
  'why':'strcpy/strcat 은 대상 버퍼의 크기를 알지 못한 채 널 종료까지 복사하므로, 원본이 대상보다 길면 인접 메모리를 덮어쓰는 버퍼 오버플로우가 발생한다. 복사 전에 원본 길이를 확인하고 대상 경계 안에서만 복사한다.',
  'why_en':'strcpy/strcat copy up to the null terminator without knowing the destination buffer’s size, so a source longer than the destination overruns adjacent memory. Check the source length before copying and copy only within the destination’s bounds.'},

 {'id':'Rule 22.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'획득한 자원은 모두 해제되어야 한다',
  'title_en':'All resources obtained dynamically by means of Standard Library functions shall be explicitly released',
  'bad': r"""#include <stdio.h>
static int read_fail(FILE *f){ (void)f; return 1; }
int main(void){
    FILE *f = fopen("/etc/hostname", "r");
    if (f == NULL) { return 1; }
    if (read_fail(f)) { return -1; }   /* 오류 경로에서 fclose 누락 — 핸들 누수 */
    fclose(f);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int read_fail(FILE *f){ (void)f; return 1; }
int main(void){
    FILE *f = fopen("/etc/hostname", "r");
    if (f == NULL) { return 1; }
    int rc = read_fail(f) ? -1 : 0;
    fclose(f);                         /* 모든 종료 경로에서 해제 */
    return rc;
}""",
  'why':'정상 경로에서만 해제하고 오류·조기 반환 경로에서 fclose/free 를 빠뜨리면, 반복 호출 시 파일 핸들·메모리가 누수되어 결국 자원 고갈로 이어진다. 자원 해제를 단일 종료 지점에 모으거나 모든 경로에서 해제를 보장한다.',
  'why_en':'Releasing only on the normal path and skipping fclose/free on error or early-return paths leaks handles and memory across repeated calls, eventually exhausting resources. Consolidate release at a single exit point or guarantee release on every path.'},

 {'id':'Rule 22.2','cat':'Mandatory · Undecidable · Rule','compiles':True,
  'title':'동적으로 할당된 메모리만 해제하며, 같은 메모리를 두 번 해제하지 않는다',
  'title_en':'A block of memory shall only be freed if it was allocated by means of a Standard Library function',
  'bad': r"""#include <stdlib.h>
int main(void){
    int x = 5;
    free(&x);   /* 동적 할당이 아닌 자동 객체의 주소를 free — 힙 손상·미정의 동작 */
    return 0;
}""",
  'good': r"""#include <stdlib.h>
int main(void){
    int x = 5;
    (void)x;    /* 자동/정적 객체는 free 하지 않는다(스코프 종료 시 자동 회수) */
    /* 동적 메모리를 쓴다면 할당된 포인터를 정확히 한 번만 free 하고 NULL 로 무효화 */
    return 0;
}""",
  'why':'malloc 계열로 할당하지 않은 메모리(자동·정적 객체)나 이미 해제된 포인터를 free 하면 힙 메타데이터가 손상되어 미정의 동작·크래시가 발생한다. free 대상은 살아 있는 동적 할당 포인터로 한정하고, 해제 후에는 포인터를 NULL 로 무효화해 이중 해제를 막는다.',
  'why_en':'Freeing memory not obtained from the malloc family (automatic/static objects) or an already-freed pointer corrupts heap metadata, causing undefined behaviour or crashes. Restrict free to live dynamically allocated pointers and null out the pointer after freeing to prevent double free.'},

 {'id':'Rule 22.3','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'같은 파일을 동시에 읽기/쓰기 스트림으로 중복 개방하지 않는다',
  'title_en':'The same file shall not be open for read and write access at the same time on different streams',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *r = fopen("data.bin", "r");
    FILE *w = fopen("data.bin", "w");   /* 같은 파일을 두 스트림으로 동시 개방 — 버퍼 불일치 */
    if (r) fclose(r);
    if (w) fclose(w);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("data.bin", "w+");   /* 단일 핸들로 읽기/쓰기 일원화 */
    if (f == NULL) { return 1; }
    fclose(f);
    return 0;
}""",
  'why':'같은 파일을 여러 스트림으로 동시에 열면 각 스트림이 독립 버퍼를 가져, 한쪽의 쓰기가 다른 쪽 버퍼에 반영되지 않아 데이터 손상·불일치가 발생한다. 한 파일은 단일 핸들로 접근을 일원화해 일관성을 보장한다.',
  'why_en':'Opening the same file on multiple streams gives each its own buffer, so a write on one is not reflected in the other’s buffer, causing corruption and inconsistency. Consolidate access to a file through a single handle to guarantee consistency.'},

 {'id':'Rule 22.6','cat':'Mandatory · Undecidable · Rule','compiles':True,
  'title':'닫힌 FILE 포인터를 사용하지 않는다',
  'title_en':'The value of a pointer to a FILE shall not be used after the associated stream has been closed',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/dev/null", "w");
    if (f == NULL) { return 1; }
    fclose(f);
    fprintf(f, "x");   /* 닫힌 스트림 사용 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/dev/null", "w");
    if (f == NULL) { return 1; }
    fprintf(f, "x");   /* 닫기 전에 모든 사용을 완료 */
    fclose(f);
    f = NULL;          /* 닫은 뒤 포인터를 무효화 */
    return 0;
}""",
  'why':'fclose 이후 FILE 포인터는 더 이상 유효한 스트림을 가리키지 않으므로, 그 포인터로 입출력을 하면 해제된 자원을 사용하는 미정의 동작이 된다. 모든 사용을 닫기 전에 끝내고, 닫은 뒤에는 포인터를 NULL 로 무효화해 재사용을 차단한다.',
  'why_en':'After fclose, a FILE pointer no longer refers to a valid stream, so doing I/O through it uses a released resource — undefined behaviour. Complete all use before closing and null out the pointer afterward to prevent reuse.'},

 {'id':'Rule 22.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'errno 를 검사하기 전에 0으로 초기화한다',
  'title_en':'The value of errno shall be set to zero prior to a call to an errno-setting function',
  'bad': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    double v = strtod("1.5", NULL);
    if (errno != 0) {   /* 호출 전 errno 를 0 으로 두지 않음 — 이전 오류 잔존 가능 */
        printf("error\n");
    }
    printf("%f\n", v);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    errno = 0;          /* 검사 대상 호출 직전에 0 으로 초기화 */
    double v = strtod("1.5", NULL);
    if (errno != 0) {
        printf("error\n");
        return 1;
    }
    printf("%f\n", v);
    return 0;
}""",
  'why':'호출 직전에 errno 를 0 으로 초기화하지 않으면, 이전의 어떤 함수가 남겨 둔 errno 값을 현재 호출의 오류로 오인해 정상 결과를 실패로 잘못 처리한다. 검사 대상 함수 호출 바로 앞에서 errno 를 0 으로 설정한다.',
  'why_en':'Without clearing errno to zero just before the call, a value left by some earlier function is mistaken for the current call’s error, wrongly treating a valid result as a failure. Set errno to zero immediately before calling the function whose errno you will test.'},

 {'id':'Rule 22.10','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'함수가 errno 를 설정하는 경우에만 errno 를 검사한다',
  'title_en':'The value of errno shall only be tested when the last function to be called was an errno-setting function',
  'bad': r"""#include <errno.h>
#include <stdio.h>
static int compute(int x){ return x + 1; }   /* errno 를 설정하지 않는 함수 */
int main(void){
    int n = compute(3);
    if (errno != 0) {   /* errno 를 설정하지 않는 함수 뒤에 검사 — 무관한 값을 봄 */
        printf("error\n");
    }
    printf("%d\n", n);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    errno = 0;
    double v = strtod("1.5", NULL);   /* errno 를 설정하도록 명세된 함수 */
    if (errno != 0) {                 /* 이런 함수 뒤에서만 errno 검사 */
        printf("error\n");
        return 1;
    }
    printf("%f\n", v);
    return 0;
}""",
  'why':'errno 를 설정하지 않는다고 명세된 함수 뒤에서 errno 를 검사하면, 그 값은 과거의 무관한 호출이 남긴 잔존 값이라 오류를 오판하게 된다. errno 기반 검사는 errno 를 설정하도록 명세된 함수(strtod·strtol 등) 직후에만 적용한다.',
  'why_en':'Testing errno after a function specified not to set it reads a leftover value from an unrelated earlier call, leading to a false error judgement. Apply errno-based checks only immediately after functions specified to set errno (e.g., strtod, strtol).'},
]
