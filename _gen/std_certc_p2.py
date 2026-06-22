# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트2: ARR·STR·MEM·FIO) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준(공식 사이트 대조) 인용, 코드·해설은 자체 작성(규범 원문 비복제).
bad/good 는 gcc -std=c11 -lm 로 컴파일되는 자족 프로그램. title_en/why_en 영문 병기."""

RULES = [
 {'id':'ARR30-C','cat':'ARR · Rule · L1','compiles':True,
  'title':'배열 범위를 벗어난 포인터/첨자를 만들거나 사용하지 않는다',
  'title_en':'Do not form or use out-of-bounds pointers or array subscripts',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[10] = {0};
    int i = 12;             /* 외부 입력 가정 */
    a[i] = 1;               /* 범위 밖 쓰기 */
    printf("%d\n", a[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[10] = {0};
    int i = 12;
    if (i >= 0 && i < 10) a[i] = 1;
    printf("%d\n", a[0]);
    return 0;
}""",
  'why':'범위를 벗어난 배열 접근은 메모리 손상·정보 유출을 일으킨다. 인덱스를 0..size-1로 검증한 뒤 접근한다.',
  'why_en':'Out-of-bounds array access corrupts memory or leaks data. Validate the index against 0..size-1 before access.'},

 {'id':'ARR32-C','cat':'ARR · Rule · L1','compiles':True,
  'title':'가변 길이 배열(VLA) 크기 인자가 유효 범위인지 보장한다',
  'title_en':'Ensure size arguments for variable-length arrays are in a valid range',
  'bad': r"""#include <stdio.h>
static void f(int n){
    int buf[n];             /* n이 음수/과대면 미정의·스택 폭주 */
    buf[0] = n;
    printf("%d\n", buf[0]);
}
int main(void){ f(8); return 0; }""",
  'good': r"""#include <stdio.h>
static void f(int n){
    if (n <= 0 || n > 1024) return;
    int buf[n];
    buf[0] = n;
    printf("%d\n", buf[0]);
}
int main(void){ f(8); return 0; }""",
  'why':'VLA 크기가 음수이거나 지나치게 크면 미정의 동작이나 스택 고갈이 발생한다. 크기를 양수·상한 이내로 검증한다.',
  'why_en':'A VLA size that is negative or excessively large causes undefined behavior or stack exhaustion. Validate it as positive and bounded.'},

 {'id':'ARR36-C','cat':'ARR · Rule · L2','compiles':True,
  'title':'관련 없는 포인터를 빼거나 비교하지 않는다',
  'title_en':'Do not subtract or compare two pointers that do not refer to the same array',
  'bad': r"""#include <stdio.h>
#include <stddef.h>
int main(void){
    int x[4], y[4];
    ptrdiff_t d = &x[3] - &y[0];   /* 다른 배열 — 미정의 */
    printf("%td\n", d);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stddef.h>
int main(void){
    int x[4];
    ptrdiff_t d = &x[3] - &x[0];   /* 같은 배열 내 */
    printf("%td\n", d);
    return 0;
}""",
  'why':'서로 다른 배열에 속한 포인터의 뺄셈/비교 결과는 미정의다. 같은 배열의 원소들 사이에서만 연산한다.',
  'why_en':'Subtracting or comparing pointers into different arrays is undefined. Operate only between elements of the same array.'},

 {'id':'ARR38-C','cat':'ARR · Rule · L1','compiles':True,
  'title':'라이브러리 함수가 무효한 포인터를 만들지 않도록 인자를 보장한다',
  'title_en':'Guarantee that library functions do not form invalid pointers',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[8];
    size_t len = 16;
    memcpy(d, "0123456789abcdef", len);   /* d 경계 초과 */
    printf("%c\n", d[0]);
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[8];
    size_t len = 16;
    if (len <= sizeof d){ memcpy(d, "01234567", len); }
    printf("ok\n");
    return 0;
}""",
  'why':'길이 인자가 버퍼 크기를 초과하면 memcpy 등이 경계를 넘는 무효 포인터로 쓴다. 호출 전에 길이가 버퍼 범위 내인지 확인한다.',
  'why_en':'A length argument exceeding the buffer makes memcpy write through an out-of-bounds pointer. Check the length against the buffer size first.'},

 {'id':'ARR39-C','cat':'ARR · Rule · L1','compiles':True,
  'title':'스케일된 정수를 포인터에 더하거나 빼지 않는다',
  'title_en':'Do not add or subtract a scaled integer to a pointer',
  'bad': r"""#include <stdio.h>
int main(void){
    int a[4] = {0,1,2,3};
    int *p = a;
    p = (int *)((char *)p + 2 * sizeof(int));   /* 수동 스케일 — 오류 유발 */
    printf("%d\n", *p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int a[4] = {0,1,2,3};
    int *p = a;
    p = p + 2;              /* 요소 단위 산술 */
    printf("%d\n", *p);
    return 0;
}""",
  'why':'바이트 단위로 직접 스케일한 포인터 산술은 이중 스케일·정렬 오류를 부른다. 요소 타입 단위의 포인터 산술을 사용한다.',
  'why_en':'Manually byte-scaling a pointer invites double-scaling and misalignment. Use element-typed pointer arithmetic.'},

 {'id':'ARR01-C','cat':'ARR · Rec · L2','compiles':True,
  'title':'배열 크기를 구할 때 포인터에 sizeof 를 적용하지 않는다',
  'title_en':'Do not apply the sizeof operator to a pointer when taking the size of an array',
  'bad': r"""#include <stdio.h>
static void f(int a[]){
    size_t n = sizeof(a) / sizeof(a[0]);   /* a는 포인터 — n 틀림 */
    printf("%zu\n", n);
}
int main(void){ int v[5]; f(v); return 0; }""",
  'good': r"""#include <stdio.h>
static void f(const int *a, size_t n){
    for (size_t i = 0; i < n; i++){ (void)a[i]; }
    printf("%zu\n", n);
}
int main(void){ int v[5] = {0}; f(v, 5); return 0; }""",
  'why':'함수 인자로 전달된 배열은 포인터로 붕괴하므로 sizeof로 요소 수를 구하면 틀린다. 요소 수를 별도 인자로 전달한다.',
  'why_en':'An array argument decays to a pointer, so sizeof gives the wrong element count. Pass the element count as a separate argument.'},

 {'id':'STR30-C','cat':'STR · Rule · L1','compiles':True,
  'title':'문자열 리터럴을 수정하려 하지 않는다',
  'title_en':'Do not attempt to modify string literals',
  'bad': r"""#include <stdio.h>
int main(void){
    char *s = (char *)"hello";
    s[0] = 'H';             /* 리터럴 수정 — 미정의 */
    printf("%s\n", s);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char s[] = "hello";     /* 수정 가능한 배열 복사본 */
    s[0] = 'H';
    printf("%s\n", s);
    return 0;
}""",
  'why':'문자열 리터럴은 읽기 전용일 수 있어 수정 시 미정의 동작이다. 수정이 필요하면 배열로 복사해 다룬다.',
  'why_en':'String literals may be read-only, so modifying them is undefined. Copy into an array when modification is needed.'},

 {'id':'STR31-C','cat':'STR · Rule · L1','compiles':True,
  'title':'문자열 저장 공간에 널 종료자 자리를 보장한다',
  'title_en':'Guarantee that storage for strings has room for the null terminator',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[8];
    strcpy(d, "12345678");  /* 8자 + 널 = 9바이트 필요 */
    printf("%s\n", d);
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[9];
    const char *src = "12345678";
    strncpy(d, src, sizeof d - 1);
    d[sizeof d - 1] = '\0';
    printf("%s\n", d);
    return 0;
}""",
  'why':'널 종료자 공간을 빠뜨리면 한 바이트 오버플로우와 종료되지 않은 문자열이 생긴다. 버퍼에 내용+널 자리를 확보하고 명시적으로 종료한다.',
  'why_en':'Omitting room for the null terminator causes a one-byte overflow and an unterminated string. Reserve content+null space and terminate explicitly.'},

 {'id':'STR32-C','cat':'STR · Rule · L1','compiles':True,
  'title':'널 종료되지 않은 문자 시퀀스를 문자열 인자로 넘기지 않는다',
  'title_en':'Do not pass a non-null-terminated character sequence to a library function expecting a string',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char buf[4];
    memcpy(buf, "abcd", 4);   /* 널 없음 */
    printf("%zu\n", strlen(buf));   /* 경계 초과 읽기 */
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char buf[5];
    memcpy(buf, "abcd", 4);
    buf[4] = '\0';
    printf("%zu\n", strlen(buf));
    return 0;
}""",
  'why':'널 종료가 없는 버퍼를 strlen/printf 등에 넘기면 메모리를 넘어 읽는다. 문자열 함수에 넘기기 전에 널 종료를 보장한다.',
  'why_en':'Passing a non-terminated buffer to strlen/printf reads past memory. Ensure null termination before calling string functions.'},

 {'id':'STR34-C','cat':'STR · Rule · L2','compiles':True,
  'title':'문자를 더 큰 정수로 변환하기 전에 unsigned char 로 캐스트한다',
  'title_en':'Cast characters to unsigned char before converting to larger integer sizes',
  'bad': r"""#include <stdio.h>
int main(void){
    char c = (char)0xFF;
    int v = c;              /* 음수 char가 부호 확장 */
    printf("%d\n", v);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char c = (char)0xFF;
    int v = (unsigned char)c;   /* 0..255 로 해석 */
    printf("%d\n", v);
    return 0;
}""",
  'why':'부호 있는 char를 더 큰 정수로 바로 변환하면 음수가 부호 확장되어 의도치 않은 큰 값이 된다. unsigned char로 먼저 캐스트한다.',
  'why_en':'Converting a signed char directly sign-extends negatives into a large value. Cast to unsigned char first.'},

 {'id':'STR37-C','cat':'STR · Rule · L1','compiles':True,
  'title':'문자 처리 함수 인자는 unsigned char 로 표현 가능해야 한다',
  'title_en':'Arguments to character-handling functions must be representable as an unsigned char',
  'bad': r"""#include <ctype.h>
#include <stdio.h>
int main(void){
    char c = (char)0xC0;
    if (isalpha(c)){ printf("alpha\n"); }   /* 음수면 미정의 */
    return 0;
}""",
  'good': r"""#include <ctype.h>
#include <stdio.h>
int main(void){
    char c = (char)0xC0;
    if (isalpha((unsigned char)c)){ printf("alpha\n"); }
    else printf("not\n");
    return 0;
}""",
  'why':'is*/to* 함수에 음수(EOF 외)를 넘기면 미정의 동작이다. unsigned char로 캐스트해 유효 범위를 보장한다.',
  'why_en':'Passing a negative value (other than EOF) to is*/to* functions is undefined. Cast to unsigned char to guarantee a valid range.'},

 {'id':'STR38-C','cat':'STR · Rule · L1','compiles':True,
  'title':'좁은 문자열과 넓은 문자열/함수를 혼동하지 않는다',
  'title_en':'Do not confuse narrow and wide character strings and functions',
  'bad': r"""#include <string.h>
#include <wchar.h>
#include <stdio.h>
int main(void){
    wchar_t w[8];
    strcpy((char *)w, "hi");   /* 넓은 버퍼에 좁은 복사 */
    printf("%ls\n", w);
    return 0;
}""",
  'good': r"""#include <wchar.h>
#include <stdio.h>
int main(void){
    wchar_t w[8];
    wcscpy(w, L"hi");          /* 넓은 문자열 함수 */
    printf("%ls\n", w);
    return 0;
}""",
  'why':'좁은/넓은 문자 함수를 섞으면 요소 크기 차이로 데이터가 손상된다. 문자 폭에 맞는 함수와 리터럴을 사용한다.',
  'why_en':'Mixing narrow and wide character functions corrupts data due to element-size differences. Use functions and literals matching the character width.'},

 {'id':'STR03-C','cat':'STR · Rec · L2','compiles':True,
  'title':'널 종료 문자열을 의도치 않게 잘라내지 않는다',
  'title_en':'Do not inadvertently truncate a null-terminated byte string',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[8];
    strncpy(d, "12345678", sizeof d);   /* 정확히 8자면 널 없음 */
    printf("%zu\n", strlen(d));         /* 종료 안 됨 */
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char d[8];
    strncpy(d, "12345678", sizeof d - 1);
    d[sizeof d - 1] = '\0';
    printf("%zu\n", strlen(d));
    return 0;
}""",
  'why':'strncpy는 한도까지 채우면 널을 붙이지 않아 종료되지 않은 문자열이 남는다. 마지막 바이트를 널로 명시 설정한다.',
  'why_en':'strncpy does not append a null when it fills the limit, leaving an unterminated string. Set the last byte to null explicitly.'},

 {'id':'MEM30-C','cat':'MEM · Rule · L1','compiles':True,
  'title':'해제된 메모리에 접근하지 않는다(use-after-free)',
  'title_en':'Do not access freed memory',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int *p = malloc(sizeof *p);
    if (!p) return 1;
    free(p);
    *p = 7;                 /* 해제 후 사용 */
    printf("%d\n", *p);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int *p = malloc(sizeof *p);
    if (!p) return 1;
    *p = 7;
    printf("%d\n", *p);
    free(p);
    p = NULL;               /* 즉시 무효화 */
    return 0;
}""",
  'why':'해제된 메모리를 읽거나 쓰면 힙 손상·정보 유출·임의 코드 실행으로 이어질 수 있다. 해제 직후 포인터를 NULL로 무효화한다.',
  'why_en':'Reading or writing freed memory can lead to heap corruption, info leaks, or code execution. Null the pointer immediately after freeing.'},

 {'id':'MEM31-C','cat':'MEM · Rule · L1','compiles':True,
  'title':'동적으로 할당된 메모리는 정확히 한 번만 해제한다',
  'title_en':'Free dynamically allocated memory exactly once',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int *p = malloc(sizeof *p);
    int err = 1;
    free(p);
    if (err) free(p);       /* 이중 해제 */
    printf("done\n");
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int *p = malloc(sizeof *p);
    free(p);
    p = NULL;
    free(p);                /* NULL free는 무해 */
    printf("done\n");
    return 0;
}""",
  'why':'같은 메모리를 두 번 해제하면 힙 메타데이터가 손상되어 악용 가능한 취약점이 된다. 해제 후 NULL로 두어 이중 해제를 막는다.',
  'why_en':'Freeing the same memory twice corrupts heap metadata into an exploitable bug. Null the pointer after freeing to prevent double-free.'},

 {'id':'MEM34-C','cat':'MEM · Rule · L1','compiles':True,
  'title':'동적으로 할당된 메모리만 해제한다',
  'title_en':'Only free memory allocated dynamically',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    char buf[32];
    char *p = buf;
    free(p);                /* 자동 객체 해제 — 미정의 */
    printf("done\n");
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    char *p = malloc(32);
    if (p){ free(p); }      /* 할당된 시작 포인터만 해제 */
    printf("done\n");
    return 0;
}""",
  'why':'정적/자동 객체나 배열 중간 포인터를 free하면 힙 손상·미정의 동작이 된다. malloc 계열로 받은 시작 포인터만 해제한다.',
  'why_en':'Freeing a static/automatic object or mid-array pointer corrupts the heap. Only free the start pointer returned by malloc-family functions.'},

 {'id':'MEM35-C','cat':'MEM · Rule · L2','compiles':True,
  'title':'객체에 충분한 메모리를 할당한다(곱셈 오버플로우 주의)',
  'title_en':'Allocate sufficient memory for an object (beware multiplication overflow)',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    size_t n = 1000000000UL;
    int *a = malloc(n * sizeof(int));   /* n*size 오버플로우 가능 */
    if (a){ a[0] = 1; free(a); }
    printf("done\n");
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
int main(void){
    size_t n = 1000000000UL;
    if (n > SIZE_MAX / sizeof(int)){ printf("too big\n"); return 1; }
    int *a = malloc(n * sizeof(int));
    if (a){ a[0] = 1; free(a); }
    return 0;
}""",
  'why':'요소 수×크기 계산이 오버플로우하면 실제보다 작은 버퍼가 할당되어 힙 오버플로우가 난다. 곱셈 전에 오버플로우를 검사한다.',
  'why_en':'If count×size overflows, a too-small buffer is allocated and overflowed. Check for multiplication overflow before allocating.'},

 {'id':'MEM01-C','cat':'MEM · Rec · L2','compiles':True,
  'title':'free 직후 포인터에 새 값(NULL)을 즉시 저장한다',
  'title_en':'Store a new value in pointers immediately after free()',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
struct N { int *data; };
int main(void){
    struct N n;
    n.data = malloc(sizeof(int));
    free(n.data);           /* 댕글링 상태로 남음 */
    printf("%p\n", (void *)n.data);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
struct N { int *data; };
int main(void){
    struct N n;
    n.data = malloc(sizeof(int));
    free(n.data);
    n.data = NULL;          /* 즉시 무효화 */
    printf("%p\n", (void *)n.data);
    return 0;
}""",
  'why':'해제 후 그대로 둔 포인터는 댕글링 상태로 남아 후속 사용·이중 해제 위험이 된다. 해제 직후 NULL을 대입한다.',
  'why_en':'A pointer left as-is after free remains dangling, risking later use or double-free. Assign NULL right after freeing.'},

 {'id':'MEM04-C','cat':'MEM · Rec · L2','compiles':True,
  'title':'길이 0 할당에 주의한다',
  'title_en':'Beware of zero-length allocations',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    size_t len = 0;
    char *p = malloc(len);  /* NULL 또는 0바이트 반환 가능 */
    p[0] = 'x';             /* 역참조 위험 */
    free(p);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    size_t len = 0;
    if (len == 0){ printf("empty\n"); return 0; }
    char *p = malloc(len);
    if (p){ p[0] = 'x'; free(p); }
    return 0;
}""",
  'why':'malloc(0)은 NULL이나 역참조 불가한 포인터를 반환할 수 있다. 0 길이를 별도 처리하고 반환값을 항상 검사한다.',
  'why_en':'malloc(0) may return NULL or a non-dereferenceable pointer. Handle zero length separately and always check the result.'},

 {'id':'MEM12-C','cat':'MEM · Rec · L3','compiles':True,
  'title':'다중 자원 정리는 goto 체인 등으로 누수 없이 처리한다',
  'title_en':'Consider using a goto chain to clean up multiple resources without leaks',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    char *a = malloc(8);
    char *b = malloc(8);
    if (!b){ return 1; }    /* a 누수 */
    free(a); free(b);
    printf("ok\n");
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int rc = 1;
    char *a = malloc(8);
    if (!a) goto done;
    char *b = malloc(8);
    if (!b) goto free_a;
    rc = 0;
    free(b);
free_a:
    free(a);
done:
    printf("rc=%d\n", rc);
    return rc;
}""",
  'why':'중간 실패 시 앞서 획득한 자원을 해제하지 않으면 누수가 쌓인다. 역순 정리(goto 체인 등)로 모든 경로에서 해제를 보장한다.',
  'why_en':'Failing midway without releasing earlier resources leaks them. Use reverse-order cleanup (e.g. a goto chain) to free on every path.'},

 {'id':'FIO30-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'사용자 입력을 포맷 문자열에 직접 사용하지 않는다',
  'title_en':'Exclude user input from format strings',
  'bad': r"""#include <stdio.h>
int main(void){
    const char *user = "%x %x %n";
    printf(user);           /* 포맷 문자열 인젝션 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    const char *user = "%x %x %n";
    printf("%s", user);     /* 입력은 인자로 */
    return 0;
}""",
  'why':'사용자 입력을 포맷 문자열로 쓰면 %n/%s 등으로 메모리 읽기·쓰기 공격이 가능하다. 항상 고정 포맷("%s")에 인자로 전달한다.',
  'why_en':'Using user input as a format string enables memory read/write attacks via %n/%s. Always pass it as an argument to a fixed "%s" format.'},

 {'id':'FIO34-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'입력 문자와 EOF/WEOF 를 구분한다',
  'title_en':'Distinguish between characters read and EOF or WEOF',
  'bad': r"""#include <stdio.h>
int main(void){
    char c;                 /* char로 받으면 EOF 구분 실패 */
    int count = 0;
    while ((c = getchar()) != EOF){ if (++count > 3) break; }
    printf("%d\n", count);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int c;
    int count = 0;
    while ((c = getchar()) != EOF){ if (++count > 3) break; }
    printf("%d\n", count);
    return 0;
}""",
  'why':'getchar 반환을 char에 담으면 0xFF 문자와 EOF가 구분되지 않아 루프가 잘못 종료·무한 반복한다. 반환값은 int로 받는다.',
  'why_en':'Storing getchar in a char conflates byte 0xFF with EOF, breaking the loop. Capture the return value as int.'},

 {'id':'FIO37-C','cat':'FIO · Rule · L2','compiles':True,
  'title':'fgets 성공 시 비어있지 않은 결과를 가정하지 않는다',
  'title_en':'Do not assume that fgets() returns a nonempty string on success',
  'bad': r"""#include <stdio.h>
#include <string.h>
int main(void){
    char line[16] = "";
    if (fgets(line, sizeof line, stdin)){
        line[strlen(line) - 1] = '\0';   /* 빈 줄이면 인덱스 -1 */
    }
    printf("[%s]\n", line);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <string.h>
int main(void){
    char line[16] = "";
    if (fgets(line, sizeof line, stdin)){
        size_t n = strlen(line);
        if (n > 0 && line[n-1] == '\n') line[n-1] = '\0';
    }
    printf("[%s]\n", line);
    return 0;
}""",
  'why':'성공한 fgets라도 내용이 비어 있을 수 있어 strlen-1 같은 접근이 경계를 벗어난다. 길이를 확인하고 안전하게 인덱싱한다.',
  'why_en':'Even a successful fgets may yield an empty string, so strlen-1 indexing underflows. Check the length and index safely.'},

 {'id':'FIO42-C','cat':'FIO · Rule · L2','compiles':True,
  'title':'더 이상 필요 없는 파일은 닫는다',
  'title_en':'Close files when they are no longer needed',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/tmp/x.txt", "w");
    if (f){ fputs("hi", f); }   /* fclose 누락 — 핸들 누수 */
    printf("done\n");
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = fopen("/tmp/x.txt", "w");
    if (!f) return 1;
    fputs("hi", f);
    fclose(f);
    printf("done\n");
    return 0;
}""",
  'why':'열린 파일을 닫지 않으면 디스크립터 누수로 결국 자원이 고갈된다. 사용이 끝나면 모든 경로에서 fclose한다.',
  'why_en':'Not closing files leaks descriptors until resources are exhausted. fclose on every path once you are done.'},

 {'id':'FIO45-C','cat':'FIO · Rule · L3','compiles':True,
  'title':'파일 접근에서 TOCTOU 경쟁 조건을 피한다',
  'title_en':'Avoid TOCTOU race conditions while accessing files',
  'bad': r"""#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
int main(void){
    const char *p = "/tmp/x.txt";
    if (access(p, W_OK) == 0){          /* 검사 */
        int fd = open(p, O_WRONLY);     /* 사용 — 사이에 교체 가능 */
        if (fd >= 0) close(fd);
    }
    printf("done\n");
    return 0;
}""",
  'good': r"""#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
int main(void){
    const char *p = "/tmp/x.txt";
    int fd = open(p, O_WRONLY | O_CREAT | O_EXCL, 0600);  /* 검사+사용 원자화 */
    if (fd >= 0) close(fd);
    printf("done\n");
    return 0;
}""",
  'why':'access 후 open 사이에 파일이 심볼릭 링크 등으로 교체되면 권한 우회가 일어난다(TOCTOU). 검사-사용을 원자적 open 플래그로 결합한다.',
  'why_en':'Between access and open the file can be swapped (e.g. a symlink), bypassing checks (TOCTOU). Combine check and use with atomic open flags.'},

 {'id':'FIO47-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'유효한 포맷 문자열을 사용한다(인자와 변환 지정자 일치)',
  'title_en':'Use valid format strings',
  'bad': r"""#include <stdio.h>
int main(void){
    long v = 10;
    printf("%d\n", v);      /* %d 에 long — 불일치 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    long v = 10;
    printf("%ld\n", v);
    return 0;
}""",
  'why':'변환 지정자와 인자 타입이 어긋나면 잘못된 크기로 읽어 미정의 동작·정보 유출이 된다. 지정자와 인자 타입을 정확히 맞춘다.',
  'why_en':'A conversion specifier mismatched to the argument type reads the wrong size and is undefined. Match specifiers to argument types exactly.'},

 {'id':'FIO02-C','cat':'FIO · Rec · L2','compiles':True,
  'title':'경로 이름을 정규화(canonicalize)한 뒤 사용한다',
  'title_en':'Canonicalize path names originating from tainted sources',
  'bad': r"""#include <stdio.h>
#include <string.h>
int main(void){
    const char *user = "../etc/passwd";
    char path[256];
    snprintf(path, sizeof path, "/data/%s", user);   /* ../ 경로 이탈 */
    printf("%s\n", path);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(void){
    const char *user = "report.txt";
    char joined[256], resolved[4096];
    snprintf(joined, sizeof joined, "/data/%s", user);
    if (realpath(joined, resolved) && strncmp(resolved, "/data/", 6) == 0){
        printf("%s\n", resolved);
    } else {
        printf("rejected\n");
    }
    return 0;
}""",
  'why':'정규화하지 않은 경로는 ../ 를 통한 디렉터리 이탈에 악용된다. realpath로 정규화하고 허용된 기준 디렉터리 내인지 확인한다.',
  'why_en':'Un-canonicalized paths are exploited for directory traversal via ../. Canonicalize with realpath and verify the result stays under the allowed base.'},
]
