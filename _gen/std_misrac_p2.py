# -*- coding: utf-8 -*-
"""MISRA C:2012 규칙 (파트2: Rule 10~17) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu11 -lm` 기준."""

RULES = [
 {'id':'Rule 10.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'피연산자는 부적절한 essential type으로 사용하지 않는다',
  'title_en':'Operands shall not be of an inappropriate essential type',
  'bad': r"""#include <stdio.h>
int main(void){
    unsigned int flags = 0x0Fu;
    if (flags & 1) {            /* essentially unsigned 값을 불리언 문맥에 직접 사용 */
        printf("bit0 set\n");
    }
    char c = 'A';
    int x = c << 2;            /* plain char 를 시프트 피연산자로 — 부호/폭이 구현정의 */
    printf("%d\n", x);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    unsigned int flags = 0x0Fu;
    if ((flags & 1u) != 0u) {   /* 비트 검사 결과를 명시적 불리언으로 */
        printf("bit0 set\n");
    }
    unsigned int uc = (unsigned int)'A';   /* 시프트 전에 unsigned 정수로 변환 */
    unsigned int x = uc << 2u;
    printf("%u\n", x);
    return 0;
}""",
  'why':'essential type 범주(불리언·문자·부호 있는/없는 정수·부동소수·열거)에 맞지 않는 연산은 암묵 변환을 거치며 의도와 다른 결과를 낸다. 불리언 문맥에는 명시적 비교를, 시프트·비트 연산에는 부호 없는 정수를 사용해 변환을 통제한다.',
  'why_en':'Operations that do not match an operand’s essential type category (boolean, character, signed/unsigned integer, floating, enum) go through implicit conversions and produce unintended results. Use explicit comparisons in boolean contexts and unsigned integers for shift/bitwise operations to control conversions.'},

 {'id':'Rule 10.2','cat':'Required · Decidable · Rule','compiles':True,
  'title':'문자형(char) 값은 덧셈/뺄셈 외 산술에 사용하지 않는다',
  'title_en':'Expressions of essentially character type shall not be used inappropriately in addition and subtraction operations',
  'bad': r"""#include <stdio.h>
int main(void){
    char a = 'A';
    char b = a * 2;     /* plain char 에 곱셈 — 부호·폭이 구현정의라 결과가 흔들림 */
    printf("%d\n", (int)b);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char a = 'A';
    int code = (int)a;       /* 산술이 필요하면 명시적으로 정수형으로 변환 */
    int b = code * 2;
    printf("%d\n", b);
    return 0;
}""",
  'why':'plain char 는 signed/unsigned 여부가 구현정의이므로 곱셈·시프트 같은 산술에 쓰면 같은 코드가 플랫폼마다 다른 값을 낸다. 문자에서 수치 계산이 필요하면 먼저 명시적으로 정수형으로 변환해 의미와 폭·부호를 고정한다.',
  'why_en':'Because plain char has implementation-defined signedness, using it in arithmetic such as multiplication or shifting makes the same code yield different values across platforms. When a numeric computation on a character is needed, first convert it explicitly to an integer type to fix meaning, width, and signedness.'},

 {'id':'Rule 10.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'표현식 값을 더 좁거나 다른 essential type 범주로 대입하지 않는다',
  'title_en':'The value of an expression shall not be assigned to an object with a narrower essential type or of a different essential type category',
  'bad': r"""#include <stdio.h>
int main(void){
    int big = 300;
    unsigned char b = big;   /* 300 을 8비트에 암묵 대입 → 44 로 절단 */
    printf("%u\n", (unsigned)b);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int big = 300;
    if (big >= 0 && big <= 255) {        /* 범위 검사 후 */
        unsigned char b = (unsigned char)big;   /* 명시적 캐스트로 의도 표현 */
        printf("%u\n", (unsigned)b);
    } else {
        printf("out of range: %d\n", big);
    }
    return 0;
}""",
  'why':'넓은 타입의 값을 더 좁은 타입에 암묵적으로 대입하면 상위 비트가 조용히 잘리거나 부호가 바뀌어 의도와 다른 값이 저장된다. 대입 전 범위를 검사하고, 좁히는 변환은 명시적 캐스트로 의도를 드러낸다.',
  'why_en':'Implicitly assigning a wide value to a narrower type silently truncates high bits or flips the sign, storing an unintended value. Check the range before assigning and make the narrowing explicit with a cast to show intent.'},

 {'id':'Rule 10.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'산술 연산의 두 피연산자는 같은 essential type 범주여야 한다',
  'title_en':'Both operands of an operator in which the usual arithmetic conversions are performed shall have the same essential type category',
  'bad': r"""#include <stdio.h>
int main(void){
    unsigned int u = 1u;
    int s = -2;
    if (u + s > 0u) {         /* s 가 거대한 unsigned 로 변환되어 항상 참이 됨 */
        printf("unexpectedly positive\n");
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int u = 1;
    int s = -2;
    if (u + s > 0) {          /* 부호 범주를 통일 → -1, 직관대로 거짓 */
        printf("positive\n");
    } else {
        printf("not positive\n");
    }
    return 0;
}""",
  'why':'부호 있는 타입과 없는 타입을 한 연산에 섞으면 일반 산술 변환으로 음수가 거대한 양수로 바뀌어, u + s > 0 같은 비교가 직관과 정반대로 동작한다. 피연산자의 부호 범주를 통일해 변환에 의한 함정을 제거한다.',
  'why_en':'Mixing signed and unsigned types in one operation triggers the usual arithmetic conversions that turn a negative into a huge positive, so comparisons like u + s > 0 behave opposite to intuition. Unify the signedness category of the operands to remove this conversion trap.'},

 {'id':'Rule 10.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'복합 표현식 결과를 더 넓은 essential type에 대입하지 않는다',
  'title_en':'The value of a composite expression shall not be assigned to an object with wider essential type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t a = 50000u, b = 50000u;
    uint32_t s = a + b;       /* a+b 는 (승격 후) 좁은 폭에서 계산 후 확장 — 의도 모호 */
    printf("%u\n", s);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t a = 50000u, b = 50000u;
    uint32_t s = (uint32_t)a + (uint32_t)b;   /* 연산 전에 목표 폭으로 넓혀 계산 */
    printf("%u\n", s);                        /* 100000 — 손실 없음 */
    return 0;
}""",
  'why':'좁은 타입끼리 계산한 복합 표현식을 더 넓은 타입에 대입하면, 계산이 좁은(또는 int 로 승격된) 폭에서 일어난 뒤 확장되어 오버플로우·래핑이 결과에 숨는다. 연산 전에 피연산자를 목표 폭으로 명시적으로 넓혀 손실을 방지한다.',
  'why_en':'Assigning a composite expression computed in narrow types to a wider type lets the computation happen at the narrow (or int-promoted) width before widening, hiding overflow/wraparound in the result. Widen the operands to the target width explicitly before the operation to avoid loss.'},

 {'id':'Rule 10.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'복합 표현식 값을 다른/넓은 essential type으로 캐스트하지 않는다',
  'title_en':'The value of a composite expression shall not be cast to a different or wider essential type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t x = 40000u, y = 40000u;
    uint32_t z = (uint32_t)(x + y);   /* 이미 좁은 폭에서 래핑된 결과를 사후 캐스트 — 복원 불가 */
    printf("%u\n", z);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint16_t x = 40000u, y = 40000u;
    uint32_t z = (uint32_t)x + (uint32_t)y;   /* 캐스트를 피연산자 단계에서 적용 */
    printf("%u\n", z);                        /* 80000 — 정확 */
    return 0;
}""",
  'why':'좁은 폭에서 평가된 복합 표현식을 사후에 넓은 타입으로 캐스트해도, 이미 손실(래핑·절단)된 비트는 되살아나지 않는다. 캐스트는 표현식 전체가 아니라 피연산자 단계에서 적용해 계산 자체가 넓은 폭에서 일어나게 한다.',
  'why_en':'Casting a composite expression to a wider type after it was evaluated at narrow width cannot recover bits already lost to wraparound or truncation. Apply the cast to the operands, not the whole expression, so the computation itself happens at the wider width.'},

 {'id':'Rule 11.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'함수 포인터를 호환되지 않는 타입으로 변환하지 않는다',
  'title_en':'Conversions shall not be performed between a pointer to a function and any other type',
  'bad': r"""#include <stdio.h>
typedef int (*fn_t)(int);
static int real(int x){ return x + 1; }
int main(void){
    fn_t f = (fn_t)(void *)real;   /* 함수↔객체 포인터 변환 — 표현이 달라 미정의 */
    printf("%d\n", f(41));
    return 0;
}""",
  'good': r"""#include <stdio.h>
typedef int (*fn_t)(int);
static int real(int x){ return x + 1; }
int main(void){
    fn_t f = real;   /* 호환되는 함수 타입끼리만 대입 */
    printf("%d\n", f(41));
    return 0;
}""",
  'why':'함수 포인터와 객체 포인터(또는 다른 시그니처의 함수 포인터)는 호출 규약·내부 표현이 달라, 변환 후 호출하면 미정의 동작과 충돌을 일으킨다. 호환되는 동일 시그니처의 함수만 대입한다.',
  'why_en':'Function pointers and object pointers (or function pointers with a different signature) have different calling conventions and representations, so calling through a converted pointer causes undefined behaviour and crashes. Only assign functions of a compatible, identical signature.'},

 {'id':'Rule 11.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'서로 다른 객체 타입을 가리키는 포인터 간 캐스트를 하지 않는다',
  'title_en':'A cast shall not be performed between a pointer to object type and a pointer to a different object type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint8_t buf[4] = {0};
    uint32_t *p = (uint32_t *)buf;   /* 정렬 위반·엄격 별칭 위반 가능 */
    *p = 0x01020304u;
    printf("%02x\n", buf[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
#include <string.h>
int main(void){
    uint8_t buf[4] = {0};
    uint32_t v = 0x01020304u;
    memcpy(buf, &v, sizeof v);   /* 바이트 단위 복사 — 정렬·별칭 안전 */
    printf("%02x\n", buf[0]);
    return 0;
}""",
  'why':'다른 객체 타입으로 포인터를 캐스트해 접근하면 정렬되지 않은 접근과 엄격 별칭(strict aliasing) 규칙 위반으로 미정의 동작이 되어, 최적화 시 예측 불가한 결과가 나온다. 표현을 재해석할 때는 memcpy로 바이트 단위 복사를 사용한다.',
  'why_en':'Accessing through a pointer cast to a different object type causes misaligned access and strict-aliasing violations — undefined behaviour that yields unpredictable results under optimization. Use memcpy for a byte-wise copy when reinterpreting a representation.'},

 {'id':'Rule 11.4','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'정수와 객체 포인터 사이를 변환하지 않는다',
  'title_en':'A conversion should not be performed between a pointer to object and an integer type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint32_t addr = 0x4000u;
    uint8_t *reg = (uint8_t *)(uintptr_t)addr;   /* 정수 → 포인터: 이식성·검증성 저하 */
    printf("mapped to %p\n", (void *)reg);        /* 임의 주소 역참조는 위험 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
static volatile uint8_t device_register;             /* 실제 객체로 모델링 */
static volatile uint8_t *reg_access(void){ return &device_register; }
int main(void){
    volatile uint8_t *reg = reg_access();   /* 포인터 타입을 유지하는 접근자 */
    *reg = 1u;
    printf("%u\n", (unsigned)device_register);
    return 0;
}""",
  'why':'정수와 포인터를 직접 변환하면 표현 차이로 잘못된 주소 접근이 생기고, 어떤 주소를 다루는지 코드만으로 검증하기 어려워진다. 메모리맵 레지스터처럼 불가피한 경우는 의미를 캡슐화한 접근자 한 곳에 가두고, 그 외에는 포인터 타입을 그대로 유지한다.',
  'why_en':'Directly converting between integers and pointers risks wrong-address access due to representation differences and makes it hard to verify which address is handled. When unavoidable (e.g., memory-mapped registers), confine it to a single encapsulated accessor and otherwise keep values in pointer types.'},

 {'id':'Rule 11.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'void 포인터와 정수 사이를 변환하지 않는다',
  'title_en':'A cast shall not be performed between pointer to void and an arithmetic type',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
static int ctx = 7;
int main(void){
    void *p = &ctx;
    uintptr_t n = (uintptr_t)p;   /* 포인터를 정수로 보관 */
    void *q = (void *)n;          /* 다시 포인터로 — 표현 차이 시 정보 손실 위험 */
    printf("%d\n", *(int *)q);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int ctx = 7;
static void use_ctx(void *p){ printf("%d\n", *(int *)p); }
int main(void){
    void *p = &ctx;
    use_ctx(p);   /* 포인터를 포인터 타입 그대로 보관·전달 */
    return 0;
}""",
  'why':'void* 를 정수로 바꿔 저장했다 복원하면, 정수 폭이 포인터를 온전히 담지 못하는 플랫폼에서 주소가 손상될 수 있다. 포인터는 포인터 타입 그대로 유지·전달하고, 정수 왕복을 피한다.',
  'why_en':'Storing a void* as an integer and restoring it can corrupt the address on platforms where the integer width cannot hold the full pointer. Keep and pass pointers in pointer types and avoid round-tripping through integers.'},

 {'id':'Rule 11.8','cat':'Required · Decidable · Rule','compiles':True,
  'title':'캐스트로 포인터가 가리키는 대상의 const/volatile 한정자를 제거하지 않는다',
  'title_en':'A cast shall not remove any const or volatile qualification from the type pointed to by a pointer',
  'bad': r"""#include <stdio.h>
static void tweak(const char *s){
    char *m = (char *)s;   /* const 제거 */
    m[0] = 'X';            /* 읽기 전용일 수 있는 대상 수정 — 미정의 동작 */
    printf("%s\n", s);
}
int main(void){ tweak("READY"); return 0; }""",
  'good': r"""#include <stdio.h>
#include <string.h>
static void tweak(const char *s){
    char buf[64];
    strncpy(buf, s, sizeof buf - 1);   /* 복사본을 만들어 수정 */
    buf[sizeof buf - 1] = '\0';
    buf[0] = 'X';
    printf("%s\n", buf);
}
int main(void){ tweak("READY"); return 0; }""",
  'why':'캐스트로 const/volatile 를 떼어내고 대상을 수정하면, 읽기 전용 메모리 수정이나 컴파일러의 잘못된 최적화로 미정의 동작이 된다. 한정자는 보존하고, 변경이 필요하면 한정자 없는 복사본을 만들어 다룬다.',
  'why_en':'Casting away const/volatile and then modifying the target causes undefined behaviour through writes to read-only memory or incorrect compiler optimizations. Preserve the qualifiers and, when modification is needed, work on an unqualified copy.'},

 {'id':'Rule 11.9','cat':'Required · Decidable · Rule','compiles':True,
  'title':'널 포인터 상수로는 매크로 NULL을 사용한다(정수 0 직접 사용 금지)',
  'title_en':'The macro NULL shall be the only permitted form of integer null pointer constant',
  'bad': r"""#include <stdio.h>
int main(void){
    char *p = 0;          /* 정수 0 을 널 포인터로 — 의도가 모호 */
    if (p == 0) {         /* 포인터 비교인지 정수 비교인지 불명확 */
        printf("null\n");
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
int main(void){
    char *p = NULL;       /* 널 포인터 상수는 NULL 로 일관되게 */
    if (p == NULL) {
        printf("null\n");
    }
    return 0;
}""",
  'why':'정수 0 을 널 포인터로 직접 쓰면 포인터 문맥인지 정수 문맥인지 코드만으로 구분되지 않아 가독성과 의도가 흐려진다. 널 포인터 상수는 일관되게 NULL 매크로로 표기해 포인터임을 분명히 한다.',
  'why_en':'Using the integer 0 directly as a null pointer makes it unclear whether the context is pointer or integer, blurring readability and intent. Consistently write null pointer constants as the NULL macro to make the pointer nature explicit.'},

 {'id':'Rule 12.1','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'연산자 우선순위는 괄호로 명시한다',
  'title_en':'The precedence of operators within expressions should be made explicit',
  'bad': r"""#include <stdio.h>
int main(void){
    int a = 1, b = 2, c = 1, d = 6;
    int r = a + b << c & d;   /* 우선순위 혼동: ((a+b)<<c)&d 로 평가됨 */
    printf("%d\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a = 1, b = 2, c = 1, d = 6;
    int r = ((a + b) << c) & d;   /* 의도한 평가 순서를 괄호로 명시 */
    printf("%d\n", r);
    return 0;
}""",
  'why':'시프트·비트·산술 연산이 섞인 표현식은 우선순위를 사람이 오해하기 쉬워, 작성자의 의도와 컴파일러의 해석이 어긋난다. 괄호로 평가 순서를 분명히 하면 의도가 코드에 드러나고 검토 오류가 줄어든다.',
  'why_en':'Expressions mixing shift, bitwise, and arithmetic operators are easy for humans to misread on precedence, so the author’s intent and the compiler’s interpretation diverge. Parentheses make the evaluation order explicit, surfacing intent and reducing review errors.'},

 {'id':'Rule 12.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'시프트 횟수는 0 이상이며 피연산자 비트폭 미만이어야 한다',
  'title_en':'The right operand of a shift shall lie in the range zero to one less than the width of the left operand',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint32_t v = 1u;
    unsigned n = 40;          /* 외부에서 온 시프트량이라고 가정 */
    uint32_t r = v << n;      /* 32비트를 40만큼 시프트 — 미정의 동작 */
    printf("%u\n", r);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    uint32_t v = 1u;
    unsigned n = 40;
    if (n < 32u) {            /* 0..31 범위 보장 */
        uint32_t r = v << n;
        printf("%u\n", r);
    } else {
        printf("shift out of range\n");
    }
    return 0;
}""",
  'why':'피연산자의 비트폭 이상으로, 또는 음수로 시프트하면 결과가 미정의가 되어 0·원값·쓰레기 등 플랫폼마다 다르게 동작한다. 시프트량을 0..(폭-1) 범위로 검증한 뒤에만 시프트한다.',
  'why_en':'Shifting by the operand width or more, or by a negative amount, is undefined behaviour that yields 0, the original, or garbage depending on the platform. Validate the shift amount to the range 0..(width-1) before shifting.'},

 {'id':'Rule 12.3','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'쉼표 연산자를 사용하지 않는다',
  'title_en':'The comma operator should not be used',
  'bad': r"""#include <stdio.h>
int main(void){
    int n = 4;
    for (int i = 0, j = n; i < j; i++, j--) {   /* 한 식에 여러 부작용을 숨김 */
        printf("%d-%d ", i, j);
    }
    printf("\n");
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int n = 4;
    int j = n;
    for (int i = 0; i < j; i++) {   /* 부작용을 문장으로 분리 — 흐름이 명확 */
        printf("%d-%d ", i, j);
        j--;
    }
    printf("\n");
    return 0;
}""",
  'why':'쉼표 연산자는 한 표현식에 여러 부작용을 압축해 평가 순서와 의도를 가려, 가독성과 정적 분석을 모두 떨어뜨린다. 부작용을 독립된 문장으로 분리하면 제어 흐름이 분명해진다.',
  'why_en':'The comma operator packs multiple side effects into one expression, obscuring evaluation order and intent and hurting both readability and static analysis. Splitting side effects into separate statements makes the control flow clear.'},

 {'id':'Rule 13.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'초기자 목록에는 영속적 부작용을 두지 않는다',
  'title_en':'Initializer lists shall not contain persistent side effects',
  'bad': r"""#include <stdio.h>
static int seq = 0;
static int f(void){ return ++seq; }   /* 영속적 부작용 */
static int g(void){ return ++seq; }
int main(void){
    int a[2] = { f(), g() };   /* 평가 순서 미명세 → a[0]/a[1] 값이 비결정적 */
    printf("%d %d\n", a[0], a[1]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int seq = 0;
static int f(void){ return ++seq; }
static int g(void){ return ++seq; }
int main(void){
    int x = f();              /* 부작용을 초기자 밖에서 순서대로 처리 */
    int y = g();
    int a[2] = { x, y };
    printf("%d %d\n", a[0], a[1]);
    return 0;
}""",
  'why':'초기자 목록 요소들의 평가 순서는 표준이 정하지 않으므로, 요소에 영속적 부작용(전역 갱신·입출력)이 있으면 결과가 비결정적이 된다. 부작용은 초기자 밖에서 정해진 순서로 처리하고 초기자에는 그 결과값만 넣는다.',
  'why_en':'The Standard does not fix the evaluation order of initializer-list elements, so persistent side effects (global updates, I/O) in them make the result non-deterministic. Perform side effects outside the initializer in a defined order and place only their resulting values in the initializer.'},

 {'id':'Rule 13.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'표현식의 값과 부작용은 모든 평가 순서에서 동일해야 한다',
  'title_en':'The value of an expression and its persistent side effects shall be the same under all permitted evaluation orders',
  'bad': r"""#include <stdio.h>
int main(void){
    int arr[4] = {0};
    int i = 1;
    arr[i] = i++;     /* i 의 인덱스 사용과 증가 순서가 미명세 */
    printf("%d %d\n", arr[1], arr[2]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int arr[4] = {0};
    int i = 1;
    arr[i] = i;       /* 사용과 수정을 분리 — 순서에 무관하게 결정적 */
    i++;
    printf("%d %d\n", arr[1], arr[2]);
    return 0;
}""",
  'why':'한 표현식에서 같은 객체를 읽으면서 동시에 수정하면(arr[i] = i++) 컴파일러가 허용하는 평가 순서에 따라 결과가 달라져 이식·최적화 시 버그가 된다. 읽기와 수정을 별도 문장으로 분리해 모든 순서에서 같은 결과가 나오게 한다.',
  'why_en':'Reading and modifying the same object in one expression (arr[i] = i++) makes the result depend on the compiler’s permitted evaluation order, becoming a bug across ports and optimizations. Split the read and the modification into separate statements so the result is the same under every order.'},

 {'id':'Rule 13.3','cat':'Advisory · Undecidable · Rule','compiles':True,
  'title':'증감 연산자(++/--)를 다른 부작용과 한 표현식에 섞지 않는다',
  'title_en':'A full expression containing an increment or decrement operator should have no other potential side effects',
  'bad': r"""#include <stdio.h>
static int last_x;
static int rec(int x){ last_x = x; return x + 1; }   /* 부작용 있는 함수 */
int main(void){
    int x = 5;
    int y = x++ + rec(x);   /* x 의 증가와 rec(x) 의 x 사용이 섞임 — 순서 의존 */
    printf("%d (last=%d)\n", y, last_x);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int last_x;
static int rec(int x){ last_x = x; return x + 1; }
int main(void){
    int x = 5;
    int t = x;
    x++;                    /* 증감을 독립 문장으로 분리 */
    int y = t + rec(x);
    printf("%d (last=%d)\n", y, last_x);
    return 0;
}""",
  'why':'++/-- 를 다른 부작용(함수 호출·대입)과 한 표현식에 결합하면, 어떤 부작용이 먼저 일어나는지 평가 순서에 의존해 결과가 모호해진다. 증감을 독립 문장으로 분리하면 순서가 명확해지고 결과가 결정적이 된다.',
  'why_en':'Combining ++/-- with other side effects (function calls, assignments) in one expression makes the result depend on which side effect happens first. Splitting the increment/decrement into its own statement makes the order clear and the result deterministic.'},

 {'id':'Rule 13.4','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'대입 연산자의 결과값을 사용하지 않는다',
  'title_en':'The result of an assignment operator should not be used',
  'bad': r"""#include <stdio.h>
static int read_val(void){ return 7; }
int main(void){
    int x;
    if ((x = read_val()) != 0) {   /* 대입 결과를 조건으로 — == 오타와 혼동 */
        printf("%d\n", x);
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int read_val(void){ return 7; }
int main(void){
    int x = read_val();   /* 대입과 검사를 분리 */
    if (x != 0) {
        printf("%d\n", x);
    }
    return 0;
}""",
  'why':'대입의 결과값을 조건·표현식에 사용하면 의도한 비교(==)를 실수로 대입(=)한 흔한 버그와 시각적으로 구분되지 않아 검토에서 놓치기 쉽다. 대입과 검사를 분리하면 의도가 분명해지고 오타 버그가 드러난다.',
  'why_en':'Using the value of an assignment in a condition is visually indistinguishable from the common bug of writing assignment (=) instead of comparison (==), so it is easily missed in review. Separating the assignment from the test makes intent clear and surfaces typo bugs.'},

 {'id':'Rule 13.5','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'&&/|| 의 우변에는 영속적 부작용을 두지 않는다',
  'title_en':'The right hand operand of a logical && or || operator shall not contain persistent side effects',
  'bad': r"""#include <stdio.h>
static int fetch_count(void){ return 3; }
int main(void){
    int ready = 0;
    int count = 0;
    if (ready && (count = fetch_count()) > 0) {   /* ready 가 거짓이면 count 대입이 누락 */
        printf("ready with %d\n", count);
    }
    printf("count=%d\n", count);   /* 0 — 부작용이 단락으로 사라짐 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int fetch_count(void){ return 3; }
int main(void){
    int ready = 0;
    int count = fetch_count();   /* 부작용을 논리 연산 밖에서 항상 수행 */
    if (ready && count > 0) {
        printf("ready with %d\n", count);
    }
    printf("count=%d\n", count);
    return 0;
}""",
  'why':'&&/|| 는 단락 평가(short-circuit)라 좌변 결과에 따라 우변이 아예 실행되지 않을 수 있어, 우변에 둔 부작용(대입·호출)이 조건부로 누락되어 상태가 일관되지 않게 된다. 부작용은 논리 연산 밖으로 빼 항상 정해진 대로 수행한다.',
  'why_en':'&& and || short-circuit, so the right operand may not run at all depending on the left, causing side effects (assignments, calls) placed there to be conditionally skipped and leaving inconsistent state. Move side effects outside the logical operator so they always run as intended.'},

 {'id':'Rule 13.6','cat':'Mandatory · Decidable · Rule','compiles':True,
  'title':'sizeof 피연산자에는 부작용이 있는 표현식을 두지 않는다',
  'title_en':'The operand of the sizeof operator shall not contain any expression which has potential side effects',
  'bad': r"""#include <stdio.h>
int main(void){
    int arr[8] = {0};
    int i = 0;
    size_t n = sizeof(arr[i++]);   /* sizeof 피연산자는 미평가 → i 는 증가하지 않음 */
    printf("size=%zu i=%d\n", n, i);   /* i 는 여전히 0 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int arr[8] = {0};
    int i = 0;
    size_t n = sizeof(arr[0]);   /* 부작용 없는 피연산자 */
    i++;                         /* 의도한 증가는 별도 문장으로 */
    printf("size=%zu i=%d\n", n, i);
    return 0;
}""",
  'why':'sizeof 의 피연산자는 (가변길이 배열 제외) 평가되지 않으므로, 그 안에 둔 i++ 같은 부작용은 실제로 일어나지 않아 의도한 증가가 조용히 사라진다. sizeof 안에는 부작용 없는 표현식만 두고 부작용은 별도 문장으로 분리한다.',
  'why_en':'The operand of sizeof is not evaluated (except for VLAs), so a side effect like i++ inside it never happens and the intended increment silently disappears. Put only side-effect-free expressions inside sizeof and perform side effects in separate statements.'},

 {'id':'Rule 14.1','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'반복 카운터로 부동소수형을 사용하지 않는다',
  'title_en':'A loop counter shall not have essentially floating type',
  'bad': r"""#include <stdio.h>
int main(void){
    int count = 0;
    for (float x = 0.0f; x != 1.0f; x += 0.1f) {   /* 0.1 은 정확히 표현 안 됨 → x != 1.0f 영원히 참 */
        if (++count > 1000) { printf("did not terminate\n"); break; }
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    for (int i = 0; i < 10; i++) {   /* 정수 카운터로 반복 */
        float x = (float)i * 0.1f;   /* 실수값은 파생 */
        printf("%.1f ", x);
    }
    printf("\n");
    return 0;
}""",
  'why':'0.1 처럼 이진 부동소수로 정확히 표현되지 않는 값을 카운터 증분으로 쓰면 표현 오차가 누적되어 x != 1.0f 같은 종료 조건을 정확히 만족하지 못하고 무한 루프가 된다. 정수 카운터로 반복하고 필요한 실수값은 카운터에서 파생한다.',
  'why_en':'Using an increment like 0.1 that cannot be represented exactly in binary floating point accumulates rounding error, so termination tests like x != 1.0f are never met and the loop runs forever. Iterate with an integer counter and derive any floating value from it.'},

 {'id':'Rule 14.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'for 루프는 잘 정의된 형태(초기화·조건·증감 일관)여야 한다',
  'title_en':'A for loop shall be well-formed',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[4] = {1, 2, 3, 4};
    int n = 4, total = 0, i;
    for (i = 0; i < n; total += a[i]) {   /* 증감부에 카운터와 무관한 로직 */
        i++;                              /* 카운터 제어가 본문으로 새어 나감 */
    }
    printf("%d\n", total);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[4] = {1, 2, 3, 4};
    int n = 4, total = 0;
    for (int i = 0; i < n; i++) {   /* 헤더는 카운터 제어만, 본문은 작업만 */
        total += a[i];
    }
    printf("%d\n", total);
    return 0;
}""",
  'why':'for 헤더의 증감부가 카운터와 무관한 작업을 하고 카운터 제어가 본문으로 흩어지면, 루프의 반복 횟수와 종료 조건을 한눈에 이해·검증하기 어렵다. 헤더(초기화·조건·증감)는 카운터 제어만, 본문은 작업만 담당하게 분리한다.',
  'why_en':'When a for header’s update does work unrelated to the counter and counter control leaks into the body, the loop’s iteration count and termination become hard to understand and verify at a glance. Keep the header (init, condition, update) for counter control only and the body for the work.'},

 {'id':'Rule 14.3','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'제어 표현식이 항상 참/거짓으로 불변(invariant)이면 안 된다',
  'title_en':'Controlling expressions shall not be invariant',
  'bad': r"""#include <stdio.h>
#include <stdint.h>
static uint32_t get_level(void){ return 0u; }
int main(void){
    uint32_t u = get_level();
    if (u >= 0u) {            /* unsigned 는 항상 >= 0 — 조건이 항상 참 */
        printf("always taken\n");
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
static uint32_t get_level(void){ return 0u; }
int main(void){
    uint32_t u = get_level();
    if (u > 0u) {            /* 실제로 분기되는 조건 */
        printf("nonzero level\n");
    } else {
        printf("zero level\n");
    }
    return 0;
}""",
  'why':'항상 참이거나 항상 거짓으로 평가되는 제어식(부호 없는 값의 >= 0 등)은 의도한 비교를 잘못 작성했다는 신호이며, 죽은 분기나 의도치 않은 무한 실행을 만든다. 조건이 실제로 양쪽으로 분기되도록 비교를 바로잡는다.',
  'why_en':'A controlling expression that always evaluates true or false (such as unsigned >= 0) signals a mis-written comparison and creates a dead branch or unintended always-execution. Fix the comparison so the condition genuinely branches both ways.'},

 {'id':'Rule 14.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'if/while 의 제어 표현식은 본질적으로 불리언이어야 한다',
  'title_en':'The controlling expression of an if statement or iteration statement shall have essentially Boolean type',
  'bad': r"""#include <stdio.h>
static int *find(int *a, int n, int key){
    for (int i = 0; i < n; i++) { if (a[i] == key) return &a[i]; }
    return 0;
}
int main(void){
    int a[3] = {1, 2, 3};
    int *p = find(a, 3, 2);
    if (p) {                 /* 포인터를 불리언처럼 — 의도 모호, 0 비교 누락 유발 */
        printf("%d\n", *p);
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
static int *find(int *a, int n, int key){
    for (int i = 0; i < n; i++) { if (a[i] == key) return &a[i]; }
    return NULL;
}
int main(void){
    int a[3] = {1, 2, 3};
    int *p = find(a, 3, 2);
    if (p != NULL) {         /* 명시적 비교로 불리언 표현식 구성 */
        printf("%d\n", *p);
    }
    return 0;
}""",
  'why':'포인터나 정수를 그대로 조건에 쓰면 "0 이 아님" 이라는 비교가 암묵화되어 의도가 모호해지고, 비교 대상을 잘못 가정하는 결함을 부른다. p != NULL, n != 0 처럼 명시적 비교로 본질적 불리언 표현식을 만든다.',
  'why_en':'Using a pointer or integer directly as a condition hides the implicit "not zero" comparison, obscuring intent and inviting wrong assumptions about what is tested. Build an essentially Boolean expression with explicit comparisons such as p != NULL or n != 0.'},

 {'id':'Rule 15.1','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'goto 문을 사용하지 않는다',
  'title_en':'The goto statement should not be used',
  'bad': r"""#include <stdio.h>
static int work(void){ return 0; }
static void cleanup(void){ printf("cleanup\n"); }
int main(void){
    int err = 0;
    if (err) { goto fail; }   /* 비선형 제어 흐름 — 분석·검증 곤란 */
    (void)work();
fail:
    cleanup();
    return 0;
}""",
  'good': r"""#include <stdio.h>
static int work(void){ return 0; }
static void cleanup(void){ printf("cleanup\n"); }
int main(void){
    int err = 0;
    if (!err) {              /* 구조적 제어문으로 같은 의도를 표현 */
        (void)work();
    }
    cleanup();
    return 0;
}""",
  'why':'goto 는 제어 흐름을 비선형으로 만들어 어디서 어디로 점프하는지 추적·검증을 어렵게 하고, 자원 해제·초기화 순서를 무너뜨리기 쉽다. if/while 같은 구조적 제어문이나 함수 분리로 같은 의도를 표현한다.',
  'why_en':'goto makes control flow nonlinear, making it hard to trace and verify where execution jumps and easy to break resource-release or initialization order. Express the same intent with structured control statements (if/while) or by factoring into functions.'},

 {'id':'Rule 15.5','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'함수는 끝에 단일 종료점(return)을 둔다',
  'title_en':'A function should have a single point of exit at the end',
  'bad': r"""#include <stdio.h>
static int classify(int x){
    if (x < 0)  return -1;   /* 중간 return 이 흩어짐 — 후처리 누락 위험 */
    if (x == 0) return 0;
    return x * 2;
}
int main(void){ printf("%d\n", classify(5)); return 0; }""",
  'good': r"""#include <stdio.h>
static int classify(int x){
    int r;
    if (x < 0)       { r = -1; }     /* 결과를 모아 마지막에 한 번 반환 */
    else if (x == 0) { r = 0; }
    else             { r = x * 2; }
    return r;
}
int main(void){ printf("%d\n", classify(5)); return 0; }""",
  'why':'함수 곳곳에 중간 return 이 흩어지면 모든 경로에서 자원 해제·로깅 같은 공통 후처리를 빠뜨리기 쉽고 흐름 추적이 어렵다. 결과를 변수에 모아 마지막에 한 번만 반환하면 공통 종료 처리를 한곳에서 보장할 수 있다.',
  'why_en':'Scattered mid-function returns make it easy to skip common cleanup such as resource release or logging on some paths and hard to trace flow. Collecting the result in a variable and returning once at the end lets common exit handling be guaranteed in one place.'},

 {'id':'Rule 15.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'반복/선택문의 본문은 복합문(중괄호)으로 감싼다',
  'title_en':'The body of an iteration statement or a selection statement shall be a compound statement',
  'bad': r"""#include <stdio.h>
static void a(void){ printf("a\n"); }
static void b(void){ printf("b\n"); }
int main(void){
    int ready = 0;
    if (ready)
        a();
        b();      /* 들여쓰기 착시 — b 는 if 와 무관하게 항상 실행됨 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void a(void){ printf("a\n"); }
static void b(void){ printf("b\n"); }
int main(void){
    int ready = 0;
    if (ready) {
        a();
    }
    b();          /* 중괄호로 본문 범위가 명확 */
    return 0;
}""",
  'why':'중괄호 없는 단일 문 본문은 나중에 문장을 추가할 때 들여쓰기만 맞춘 채 본문 범위 밖에 놓이는 결함(예: Apple "goto fail" 버그)을 부른다. if/while/for 본문은 항상 중괄호로 감싸 범위를 코드로 고정한다.',
  'why_en':'A braceless single-statement body invites the defect where a later-added statement is indented but falls outside the body (e.g., Apple’s "goto fail" bug). Always wrap if/while/for bodies in braces to fix the scope in code.'},

 {'id':'Rule 15.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'if-else if 사슬은 마지막에 else 로 마무리한다',
  'title_en':'All if ... else if constructs shall be terminated with an else statement',
  'bad': r"""#include <stdio.h>
static void a(void){ printf("a\n"); }
static void b(void){ printf("b\n"); }
int main(void){
    int m = 3;
    if (m == 1)      { a(); }
    else if (m == 2) { b(); }   /* 그 외 값(3 등)은 조용히 무시됨 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void a(void){ printf("a\n"); }
static void b(void){ printf("b\n"); }
static void handle_other(int m){ printf("unhandled %d\n", m); }
int main(void){
    int m = 3;
    if (m == 1)      { a(); }
    else if (m == 2) { b(); }
    else             { handle_other(m); }   /* 나머지 경우를 명시적으로 처리 */
    return 0;
}""",
  'why':'else 로 닫지 않은 if-else if 사슬은 예상하지 못한 입력을 아무 처리 없이 지나쳐, 오류 상황이 조용히 무시되고 디버깅을 어렵게 한다. 마지막 else 로 나머지 모든 경우를 명시적으로 처리(또는 의도적 무시를 기록)한다.',
  'why_en':'An if-else if chain not closed with else lets unexpected inputs pass with no handling, silently ignoring error cases and hampering debugging. Terminate with a final else that explicitly handles all remaining cases (or records a deliberate no-op).'},

 {'id':'Rule 16.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'switch 문은 잘 정의된 구문 형태를 따른다',
  'title_en':'All switch statements shall be well-formed',
  'bad': r"""#include <stdio.h>
int main(void){
    int s = 1;
    switch (s) {
        int local;              /* case 밖 선언 — 초기화가 실행되지 않음 */
        case 1: local = 1; printf("%d\n", local); break;
        default: break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int s = 1;
    switch (s) {
        case 1: {
            int local = 1;      /* 모든 코드를 절(case) 안에, 블록으로 한정 */
            printf("%d\n", local);
            break;
        }
        default:
            break;
    }
    return 0;
}""",
  'why':'switch 본문에서 case/default 절 밖에 놓인 선언·문장은 실행되지 않거나 점프를 건너뛰어 초기화가 누락되는 등 모호한 동작을 만든다. 모든 코드를 절 안에 두고 지역 변수는 블록으로 감싸 구조를 정형화한다.',
  'why_en':'Declarations or statements placed outside case/default clauses in a switch body are not executed or are skipped by the jump, causing missed initialization and ambiguous behaviour. Put all code inside clauses and scope locals in a block to keep the structure well-formed.'},

 {'id':'Rule 16.3','cat':'Required · Decidable · Rule','compiles':True,
  'title':'switch 의 각 절은 무조건 break(또는 종료)로 끝낸다',
  'title_en':'An unconditional break statement shall terminate every switch-clause',
  'bad': r"""#include <stdio.h>
static void open_dev(void){ printf("open\n"); }
static void close_dev(void){ printf("close\n"); }
int main(void){
    int cmd = 1;
    switch (cmd) {
        case 1: open_dev();      /* break 누락 — case 2 로 흘러내림 */
        case 2: close_dev(); break;
        default: break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void open_dev(void){ printf("open\n"); }
static void close_dev(void){ printf("close\n"); }
int main(void){
    int cmd = 1;
    switch (cmd) {
        case 1: open_dev();  break;   /* 각 절을 명시적으로 종료 */
        case 2: close_dev(); break;
        default: break;
    }
    return 0;
}""",
  'why':'break 누락으로 인한 fall-through 는 의도치 않게 다음 절까지 실행되어, 한 명령이 두 동작을 수행하는 흔하고 찾기 어려운 버그를 만든다. 각 switch 절을 break/return 으로 명확히 종료하고, 의도적 fall-through 는 주석으로 표시한다.',
  'why_en':'A missing break causes fall-through that unintentionally runs into the next clause, producing a common and elusive bug where one command performs two actions. Terminate every switch clause explicitly with break/return and mark intentional fall-through with a comment.'},

 {'id':'Rule 16.4','cat':'Required · Decidable · Rule','compiles':True,
  'title':'모든 switch 문은 default 절을 가진다',
  'title_en':'Every switch statement shall have a default label',
  'bad': r"""#include <stdio.h>
enum S { S_IDLE, S_RUN };
static void idle(void){ printf("idle\n"); }
static void run(void){ printf("run\n"); }
int main(void){
    int state = 99;            /* 정의되지 않은 상태값 */
    switch (state) {
        case S_IDLE: idle(); break;
        case S_RUN:  run();  break;
    }                          /* default 없음 — 99 가 조용히 무시됨 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
enum S { S_IDLE, S_RUN };
static void idle(void){ printf("idle\n"); }
static void run(void){ printf("run\n"); }
static void handle_invalid(int s){ printf("invalid state %d\n", s); }
int main(void){
    int state = 99;
    switch (state) {
        case S_IDLE: idle(); break;
        case S_RUN:  run();  break;
        default: handle_invalid(state); break;   /* 예외 상황 처리 */
    }
    return 0;
}""",
  'why':'default 절이 없는 switch 는 case 에 없는 값(손상된 상태·미래 확장값)을 아무 처리 없이 지나쳐 오류를 숨긴다. 모든 switch 에 default 를 두어 정의되지 않은 입력을 반드시 감지·처리한다.',
  'why_en':'A switch without a default clause passes over values not covered by any case (corrupt states, future values) with no handling, hiding errors. Give every switch a default so undefined inputs are always detected and handled.'},

 {'id':'Rule 16.5','cat':'Required · Decidable · Rule','compiles':True,
  'title':'default 레이블은 switch 본문의 처음 또는 마지막에 둔다',
  'title_en':'A default label shall appear as either the first or the last switch label',
  'bad': r"""#include <stdio.h>
int main(void){
    int x = 2;
    switch (x) {
        case 1: printf("one\n"); break;
        default: printf("other\n"); break;   /* 절들 사이에 위치 — 가독성 저하 */
        case 2: printf("two\n"); break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int x = 2;
    switch (x) {
        case 1: printf("one\n"); break;
        case 2: printf("two\n"); break;
        default: printf("other\n"); break;   /* 마지막에 일관 배치 */
    }
    return 0;
}""",
  'why':'default 레이블이 case 절들 사이에 끼면 코드를 읽을 때 분기 구조를 한눈에 파악하기 어렵고 fall-through 의도를 오해하기 쉽다. default 를 본문의 처음 또는 마지막에 일관되게 배치해 가독성을 높인다.',
  'why_en':'A default label wedged between case clauses makes the branch structure hard to grasp at a glance and easy to misread for fall-through intent. Place default consistently at the first or last position of the body for readability.'},

 {'id':'Rule 16.6','cat':'Required · Decidable · Rule','compiles':True,
  'title':'switch 문은 두 개 이상의 절을 가진다',
  'title_en':'Every switch statement shall have at least two switch-clauses',
  'bad': r"""#include <stdio.h>
static void handle(void){ printf("handle\n"); }
int main(void){
    int flag = 1;
    switch (flag) {
        default: handle(); break;   /* 절이 사실상 하나 — switch 가 과함 */
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void handle(void){ printf("handle\n"); }
int main(void){
    int flag = 1;
    if (flag != 0) {   /* 분기가 하나면 if 가 적절 */
        handle();
    }
    return 0;
}""",
  'why':'절이 하나뿐인 switch 는 단일 분기를 표현하는 데 if 로 충분한 일을 과한 구문으로 부풀려 가독성을 떨어뜨린다. 분기가 둘 이상일 때만 switch 를 쓰고, 단일 분기는 if 로 표현한다.',
  'why_en':'A switch with only one clause inflates a single branch — which an if expresses adequately — into an over-heavy construct, hurting readability. Use switch only when there are two or more branches and express a single branch with if.'},

 {'id':'Rule 16.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'switch 의 제어 표현식은 본질적 불리언 타입이 아니어야 한다',
  'title_en':'A switch-expression shall not have essentially Boolean type',
  'bad': r"""#include <stdio.h>
#include <stdbool.h>
static bool check(void){ return true; }
int main(void){
    bool ok = check();
    switch (ok) {              /* 참/거짓 두 값뿐인데 switch — 부자연스러움 */
        case true:  printf("ok\n");  break;
        case false: printf("ng\n");  break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdbool.h>
static bool check(void){ return true; }
int main(void){
    bool ok = check();
    if (ok) {                  /* 불리언 분기는 if-else 로 */
        printf("ok\n");
    } else {
        printf("ng\n");
    }
    return 0;
}""",
  'why':'값이 참/거짓 둘뿐인 불리언에 switch 를 쓰면 case true/false 같은 부자연스러운 구조가 되어 가독성이 낮고 의도가 흐려진다. 불리언 분기는 if-else 로 표현하고 switch 는 다중 값 분기에만 쓴다.',
  'why_en':'Using switch on a Boolean — which has only true/false — produces awkward case true/false structures that read poorly and obscure intent. Express Boolean branching with if-else and reserve switch for multi-value dispatch.'},

 {'id':'Rule 17.1','cat':'Required · Decidable · Rule','compiles':True,
  'title':'<stdarg.h> 의 가변인자 기능을 사용하지 않는다',
  'title_en':'The features of <stdarg.h> shall not be used',
  'bad': r"""#include <stdio.h>
#include <stdarg.h>
static int vsum(int n, ...){      /* 타입·개수 검사 없는 가변인자 */
    va_list ap; va_start(ap, n);
    int s = 0;
    for (int i = 0; i < n; i++) { s += va_arg(ap, int); }   /* 잘못된 타입이면 미정의 */
    va_end(ap);
    return s;
}
int main(void){ printf("%d\n", vsum(3, 1, 2, 3)); return 0; }""",
  'good': r"""#include <stdio.h>
static int sum(const int *a, int n){   /* 명시적 배열 + 개수 — 타입 안전 */
    int s = 0;
    for (int i = 0; i < n; i++) { s += a[i]; }
    return s;
}
int main(void){
    int a[3] = {1, 2, 3};
    printf("%d\n", sum(a, 3));
    return 0;
}""",
  'why':'va_arg 가변인자는 전달된 인자의 타입·개수를 컴파일러가 검사하지 못해, 기대와 다른 타입을 추출하면 진단 없는 미정의 동작이 된다. 배열과 길이를 함께 넘기는 타입 안전한 인터페이스로 대체한다.',
  'why_en':'va_arg variadic arguments are not type- or count-checked by the compiler, so extracting a type that differs from what was passed is undiagnosed undefined behaviour. Replace them with a type-safe interface that passes an array together with its length.'},

 {'id':'Rule 17.2','cat':'Required · Undecidable · Rule','compiles':True,
  'title':'함수는 직접 또는 간접 재귀를 사용하지 않는다',
  'title_en':'Functions shall not call themselves, either directly or indirectly',
  'bad': r"""#include <stdio.h>
static unsigned fact(unsigned n){
    return (n <= 1u) ? 1u : n * fact(n - 1u);   /* 재귀 — 최대 스택 사용량 불확정 */
}
int main(void){ printf("%u\n", fact(5u)); return 0; }""",
  'good': r"""#include <stdio.h>
static unsigned fact(unsigned n){
    unsigned r = 1u;
    for (unsigned i = 2u; i <= n; i++) { r *= i; }   /* 반복 — 스택 사용 결정적 */
    return r;
}
int main(void){ printf("%u\n", fact(5u)); return 0; }""",
  'why':'재귀는 입력에 따라 호출 깊이가 달라져 최대 스택 사용량을 정적으로 보장하기 어렵고, 안전필수 시스템에서 깊은 재귀가 스택 오버플로우로 이어진다. 동일 로직을 반복문으로 변환해 스택 사용을 결정적으로 만든다.',
  'why_en':'Recursion makes call depth depend on input, so the maximum stack usage cannot be statically guaranteed, and deep recursion in safety-critical systems leads to stack overflow. Convert the same logic into a loop to make stack usage deterministic.'},

 {'id':'Rule 17.3','cat':'Mandatory · Decidable · Rule','compiles':True,
  'title':'함수는 암시적 선언 없이 호출해야 한다',
  'title_en':'A function shall not be declared implicitly',
  'bad': r"""#include <stdio.h>
int main(void){
    int r = compute(3);   /* 선언/프로토타입이 보이지 않음 → 암시적 선언(인자·반환 타입 가정) */
    printf("%d\n", r);
    return 0;
}
int compute(int x){ return x * 2; }""",
  'good': r"""#include <stdio.h>
static int compute(int x){ return x * 2; }   /* 호출 전에 선언/정의가 보임 */
int main(void){
    int r = compute(3);
    printf("%d\n", r);
    return 0;
}""",
  'why':'프로토타입 없이 함수를 호출하면 컴파일러가 인자·반환 타입을 임의로 가정해, 실제 정의와 다르면 잘못된 호출 규약으로 스택·레지스터를 오염시킨다. 호출 지점에서 항상 선언(헤더 포함)이 보이도록 한다.',
  'why_en':'Calling a function without a visible prototype makes the compiler assume argument and return types, so a mismatch with the real definition corrupts the stack/registers via a wrong calling convention. Ensure a declaration (via a header) is always visible at the call site.'},

 {'id':'Rule 17.4','cat':'Mandatory · Decidable · Rule','compiles':True,
  'title':'비void 함수는 모든 경로에서 값을 반환해야 한다',
  'title_en':'All exit paths from a function with non-void return type shall have an explicit return statement with an expression',
  'bad': r"""#include <stdio.h>
static int classify(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
}   /* x==0 경로에서 반환값 없음 — 불확정 반환값 */
int main(void){ printf("%d\n", classify(0)); return 0; }""",
  'good': r"""#include <stdio.h>
static int classify(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;   /* 모든 경로에서 명시적 반환 */
}
int main(void){ printf("%d\n", classify(0)); return 0; }""",
  'why':'반환값을 명시하지 않고 끝나는 비void 함수의 반환값은 불확정이라, 호출부가 스택·레지스터에 남은 쓰레기값을 결과로 사용하게 된다. 모든 종료 경로에서 명시적 return 문으로 값을 반환한다.',
  'why_en':'A non-void function that ends without an explicit return has an indeterminate return value, so the caller uses leftover garbage from the stack/registers as the result. Return a value with an explicit return statement on every exit path.'},

 {'id':'Rule 17.6','cat':'Mandatory · Decidable · Rule','compiles':True,
  'title':'배열 매개변수 선언에 static 키워드를 쓰지 않는다',
  'title_en':'The declaration of an array parameter shall not contain the static keyword between the [ ]',
  'bad': r"""#include <stdio.h>
static int first(int a[static 10]){   /* '최소 10개' 보장 — 호출부가 어기면 미정의 */
    return a[0];
}
int main(void){
    int a[10] = {7};
    printf("%d\n", first(a));
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
static int first(const int *a, size_t n){   /* 포인터 + 길이로 명시적 계약 */
    return (n > 0u) ? a[0] : -1;
}
int main(void){
    int a[10] = {7};
    printf("%d\n", first(a, 10));
    return 0;
}""",
  'why':'배열 매개변수의 [static N] 은 호출부가 최소 N개 요소를 보장한다고 약속하지만, 약속이 깨져도 컴파일러가 진단하지 못해 경계 밖 접근이 미정의 동작으로 숨는다. 포인터와 길이를 함께 전달해 길이를 실행시간에 검사 가능한 명시적 계약으로 만든다.',
  'why_en':'An array parameter’s [static N] promises the caller provides at least N elements, but a broken promise goes undiagnosed and hides out-of-bounds access as undefined behaviour. Pass a pointer with a length to make the length an explicit, run-time-checkable contract.'},

 {'id':'Rule 17.7','cat':'Required · Decidable · Rule','compiles':True,
  'title':'비void 함수의 반환값은 사용한다',
  'title_en':'The value returned by a function having non-void return type shall be used',
  'bad': r"""#include <stdio.h>
int main(void){
    char buf[4];
    snprintf(buf, sizeof buf, "%d", 12345);   /* 반환(필요 길이)을 무시 → 절단 감지 못함 */
    printf("[%s]\n", buf);                      /* "123" 으로 조용히 잘림 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char buf[4];
    int need = snprintf(buf, sizeof buf, "%d", 12345);
    if (need < 0 || (size_t)need >= sizeof buf) {   /* 절단을 감지해 처리 */
        printf("truncated (need %d)\n", need);
    } else {
        printf("[%s]\n", buf);
    }
    return 0;
}""",
  'why':'의미 있는 반환값(오류 코드·필요 길이·실제 처리량)을 무시하면 실패나 절단을 감지하지 못한 채 잘못된 데이터로 진행한다. 반환값을 검사해 분기하고, 정말 불필요할 때만 (void) 캐스트로 의도를 명시한다.',
  'why_en':'Ignoring a meaningful return value (error code, required length, bytes processed) lets execution continue with bad data without detecting failure or truncation. Test the return value and branch on it, casting to (void) only when it is genuinely unneeded to signal intent.'},

 {'id':'Rule 17.8','cat':'Advisory · Decidable · Rule','compiles':True,
  'title':'함수 매개변수를 함수 안에서 수정하지 않는다',
  'title_en':'A function parameter should not be modified',
  'bad': r"""#include <stdio.h>
static int scale(int n){
    n = n * 2;        /* 매개변수 직접 수정 — 원래 전달값과의 대응이 흐려짐 */
    return n + 1;
}
int main(void){ printf("%d\n", scale(5)); return 0; }""",
  'good': r"""#include <stdio.h>
static int scale(int n){
    int v = n * 2;    /* 지역 변수에 복사해 수정, 매개변수는 입력으로만 읽음 */
    return v + 1;
}
int main(void){ printf("%d\n", scale(5)); return 0; }""",
  'why':'매개변수를 함수 안에서 수정하면, 디버깅·로깅 시 "이 함수가 받은 원래 인자값" 과 현재 값의 대응이 흐려져 추적이 어려워진다. 매개변수는 입력으로만 읽고, 변경이 필요하면 지역 복사본을 두어 원래 입력을 보존한다.',
  'why_en':'Modifying a parameter inside a function blurs the correspondence between the original argument the function received and its current value, complicating debugging and logging. Read parameters as inputs only and use a local copy when modification is needed so the original input is preserved.'},
]
