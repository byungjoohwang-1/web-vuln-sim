# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트4: 공식 사이트 대조로 보강한 누락 규칙) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 cmu-sei.github.io 공식 목록 대조로 확인, 코드·해설은 자체 작성(규범 원문 비복제).
강화판: bad/good 를 현실적 맥락의 컴파일 가능 C 프로그램(int main 포함)으로 작성하고
KO/EN 이중언어(title_en/why_en) 제공. Wandbox gcc-13.2.0 `-std=gnu11 -lm -pthread` 기준.
다중 번역단위 링크 규칙(DCL36-C)은 단일 파일로 성립하지 않아 초점 스니펫으로 둔다.
스레드별 저장소·조건변수는 이식성을 위해 C11 <threads.h> 대신 POSIX(pthread)로 예시한다."""

RULES = [
 {'id':'DCL36-C','cat':'DCL · Rule · L2',
  'title':'충돌하는 링크(linkage) 분류로 식별자를 선언하지 않는다',
  'title_en':'Do not declare an identifier with conflicting linkage classifications',
  'bad': r"""/* a.c */
static int shared;      /* 내부 링크(이 파일 전용) */

/* b.c */
extern int shared;      /* 외부 링크로 같은 이름 참조 — 링크 분류 충돌, 미정의 동작 */""",
  'good': r"""/* shared.h */
extern int shared;      /* 외부 링크 선언을 헤더에 단일화 */

/* shared.c */
#include "shared.h"
int shared;             /* 일관된 외부 링크 정의 */""",
  'why':'같은 식별자를 한 곳에서는 static(내부 링크), 다른 곳에서는 extern(외부 링크)으로 모순되게 선언하면 어느 객체를 가리키는지 모호해져 미정의 동작이 된다. 공유 헤더에 단일 extern 선언을 두고 한 소스에서만 정의해 링크 분류를 일관되게 유지한다.',
  'why_en':'Declaring the same identifier as static (internal linkage) in one place and extern (external linkage) in another is contradictory, making it ambiguous which object is referred to — undefined behaviour. Put a single extern declaration in a shared header and define it in exactly one source file to keep linkage consistent.'},

 {'id':'EXP35-C','cat':'EXP · Rule · L1','compiles':True,
  'title':'임시(temporary) 수명 객체를 수정하거나 그 수명 밖에서 접근하지 않는다',
  'title_en':'Do not modify objects with temporary lifetime',
  'bad': r"""#include <stdio.h>
struct S { int a[4]; };
static struct S f(void){ struct S s = {{0,0,0,0}}; return s; }
int main(void){
    int *p = f().a;   /* 임시 객체의 멤버 배열 주소 — 전체 식이 끝나면 임시 소멸 */
    *p = 1;           /* 소멸한 임시에 접근 — 미정의 동작 */
    printf("%d\n", *p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
struct S { int a[4]; };
static struct S f(void){ struct S s = {{0,0,0,0}}; return s; }
int main(void){
    struct S s = f();   /* 임시를 지속 객체에 복사해 보관 */
    s.a[0] = 1;
    printf("%d\n", s.a[0]);
    return 0;
}""",
  'why':'함수가 값으로 반환한 구조체는 임시 수명 객체라 그것을 포함한 전체 식이 끝나는 즉시 소멸하므로, 그 내부 배열·멤버의 주소를 보관했다 접근·수정하면 사라진 객체를 가리키는 미정의 동작이 된다. 반환값을 지속 수명 객체에 복사한 뒤 다룬다.',
  'why_en':'A struct returned by value has temporary lifetime and is destroyed as soon as the full expression containing it ends, so storing and then accessing/modifying the address of its array or member dereferences a vanished object — undefined behaviour. Copy the return value into an object of persistent lifetime first.'},

 {'id':'EXP42-C','cat':'EXP · Rule · L2','compiles':True,
  'title':'구조체를 통째로 비교해 패딩 데이터까지 비교하지 않는다',
  'title_en':'Do not compare padding data',
  'bad': r"""#include <string.h>
#include <stdio.h>
struct P { char c; int v; };   /* c 와 v 사이에 패딩 바이트 존재 가능 */
int main(void){
    struct P a, b;
    memset(&a, 0, sizeof a); a.c = 'x'; a.v = 1;
    b.c = 'x'; b.v = 1;        /* 패딩 바이트는 불확정 */
    if (memcmp(&a, &b, sizeof a) == 0) printf("equal\n");
    else printf("differ (padding)\n");   /* 논리적으로 같아도 패딩 때문에 다를 수 있음 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
struct P { char c; int v; };
int main(void){
    struct P a = { 'x', 1 };
    struct P b = { 'x', 1 };
    if (a.c == b.c && a.v == b.v) printf("equal\n");   /* 멤버별 비교 */
    else printf("differ\n");
    return 0;
}""",
  'why':'memcmp 로 구조체 전체를 비교하면 멤버 사이·끝에 채워지는 불확정 패딩 바이트까지 비교되어, 모든 멤버 값이 같아도 패딩 차이로 다르다고 판정될 수 있다. 의미 있는 동등성은 멤버별 비교로 판정한다.',
  'why_en':'Comparing a whole struct with memcmp also compares the indeterminate padding bytes inserted between and after members, so two structs with identical member values can be judged different due to padding. Determine meaningful equality by comparing members individually.'},

 {'id':'EXP43-C','cat':'EXP · Rule · L2','compiles':True,
  'title':'restrict 한정 포인터로 미정의 동작을 일으키지 않는다',
  'title_en':'Avoid undefined behavior when using restrict-qualified pointers',
  'bad': r"""#include <stdio.h>
static void add(int *restrict a, const int *restrict b, int n){
    for (int i = 0; i < n; i++) { a[i] += b[i]; }   /* a, b 가 별칭 없음을 약속 */
}
int main(void){
    int buf[4] = {1, 2, 3, 4};
    add(buf, buf, 4);   /* 같은 배열을 둘 다 전달 — restrict 약속 위반, 미정의 동작 */
    printf("%d\n", buf[0]);
    return 0;
}""",
  'good': r"""#include <stdio.h>
static void add(int *a, const int *b, int n){   /* restrict 미사용 — 별칭 허용 */
    for (int i = 0; i < n; i++) { a[i] += b[i]; }
}
int main(void){
    int buf[4] = {1, 2, 3, 4};
    add(buf, buf, 4);   /* 겹쳐도 정의된 동작 */
    printf("%d\n", buf[0]);
    return 0;
}""",
  'why':'restrict 는 해당 포인터들이 같은 메모리를 가리키지 않는다는 약속을 컴파일러에 주어 최적화를 허용하는데, 실제로 겹치는 포인터를 넘기면 그 약속이 깨져 진단 없는 미정의 동작이 된다. 별칭 가능성이 있는 인터페이스에서는 restrict 를 사용하지 않는다.',
  'why_en':'restrict promises the compiler that the pointers do not alias, enabling optimizations, but passing overlapping pointers breaks that promise — undiagnosed undefined behaviour. Do not use restrict in interfaces where aliasing is possible.'},

 {'id':'INT36-C','cat':'INT · Rule · L1','compiles':True,
  'title':'포인터와 정수를 변환할 때 주의한다',
  'title_en':'Converting a pointer to integer or integer to pointer',
  'bad': r"""#include <stdio.h>
int main(void){
    int x = 0;
    void *ptr = &x;
    unsigned int n = (unsigned int)(unsigned long)ptr;   /* 포인터가 더 넓으면 상위 비트 절단 */
    void *back = (void *)(unsigned long)n;               /* 복원 시 잘못된 주소가 될 수 있음 */
    printf("%p\n", back);
    return 0;
}""",
  'good': r"""#include <stdio.h>
#include <stdint.h>
int main(void){
    int x = 0;
    void *ptr = &x;
    uintptr_t n = (uintptr_t)ptr;   /* 포인터를 온전히 담는 타입 */
    void *back = (void *)n;          /* 정확히 복원 */
    printf("%d\n", back == ptr);
    return 0;
}""",
  'why':'포인터를 그것보다 좁은 정수형으로 변환하면 상위 비트가 잘려, 다시 포인터로 복원할 때 원래와 다른 주소가 되어 잘못된 메모리 접근으로 이어진다. 포인터↔정수 변환이 불가피하면 포인터를 온전히 담도록 정의된 uintptr_t/intptr_t 를 사용한다.',
  'why_en':'Converting a pointer to an integer narrower than it truncates the high bits, so restoring it to a pointer yields a different address and wrong memory access. When pointer/integer conversion is unavoidable, use uintptr_t/intptr_t, defined to hold a pointer in full.'},

 {'id':'ARR37-C','cat':'ARR · Rule · L1','compiles':True,
  'title':'배열이 아닌 객체를 가리키는 포인터에 정수를 더하거나 빼지 않는다',
  'title_en':'Do not add or subtract an integer to a pointer to a non-array object',
  'bad': r"""#include <stdio.h>
struct P { int x; int y; };
int main(void){
    struct P p = { 1, 2 };
    int *q = &p.x + 1;   /* 단일 멤버를 1-원소 배열처럼 취급 — 그 객체 범위를 벗어남(미정의) */
    printf("%d\n", *q);
    return 0;
}""",
  'good': r"""#include <stdio.h>
struct P { int x; int y; };
int main(void){
    struct P p = { 1, 2 };
    int *q = &p.y;       /* 의도한 멤버의 주소를 직접 사용 */
    printf("%d\n", *q);
    return 0;
}""",
  'why':'포인터 산술은 배열 안에서만 정의되므로, 단일(비배열) 객체나 구조체 멤버의 주소에 +1 을 하면 그 객체의 범위를 벗어나 미정의 동작이 된다(멤버 사이의 패딩·재배치 가정도 깨진다). 다른 멤버가 필요하면 그 멤버의 주소를 직접 취한다.',
  'why_en':'Pointer arithmetic is defined only within an array, so adding 1 to the address of a single (non-array) object or struct member goes outside that object — undefined behaviour (and assumes member layout/padding that is not guaranteed). Take the address of the desired member directly instead.'},

 {'id':'FLP36-C','cat':'FLP · Rule · L2','compiles':True,
  'title':'정수를 부동소수로 변환할 때 정밀도 손실에 주의한다',
  'title_en':'Preserve precision when converting integral values to floating-point type',
  'bad': r"""#include <stdio.h>
int main(void){
    long big = 16777217L;   /* 2^24 + 1 */
    float f = (float)big;   /* float 가수는 24비트 — 가장 가까운 값으로 반올림되어 값 변형 */
    printf("%ld -> %.0f\n", big, (double)f);   /* 16777217 -> 16777216 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    long big = 16777217L;
    double d = (double)big;   /* double 가수는 53비트 — 이 값을 정확히 표현 */
    printf("%ld -> %.0f\n", big, d);
    return 0;
}""",
  'why':'부동소수형의 가수(mantissa) 비트 수보다 큰 정수를 변환하면 정확히 표현할 수 없어 가장 가까운 표현값으로 반올림되어 값이 조용히 달라진다(float 는 약 2^24, double 은 약 2^53 초과부터). 정수 범위를 담을 수 있는 충분한 정밀도의 부동소수형을 사용한다.',
  'why_en':'Converting an integer larger than the floating type’s mantissa width cannot be represented exactly and is silently rounded to the nearest value (beyond about 2^24 for float, 2^53 for double). Use a floating type with enough precision to hold the integer range.'},

 {'id':'FLP37-C','cat':'FLP · Rule · L2','compiles':True,
  'title':'부동소수 객체의 비트 표현으로 동등성을 비교하지 않는다',
  'title_en':'Do not use object representations to compare floating-point values',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    double x = 0.0;
    double y = -0.0;   /* +0.0 와 -0.0 은 값은 같지만 비트 표현이 다름 */
    if (memcmp(&x, &y, sizeof x) == 0) printf("equal\n");
    else printf("differ (bit pattern)\n");   /* 값은 같은데 다르다고 판정 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    double x = 0.0;
    double y = -0.0;
    if (x == y) printf("equal\n");   /* 값 비교 — +0.0 == -0.0 은 참 */
    else printf("differ\n");
    return 0;
}""",
  'why':'부동소수는 +0.0/-0.0 처럼 값이 같아도 비트 표현이 다르거나, NaN 처럼 같은 비트라도 같지 않은 경우가 있어 memcmp(비트 비교)로는 수학적 동등성을 올바로 판정하지 못한다. 부동소수는 == 같은 값 비교(또는 허용 오차 비교)를 사용한다.',
  'why_en':'Floating-point values can have equal values with different bit patterns (+0.0/-0.0) or equal bit patterns that are not equal (NaN), so memcmp (bitwise) cannot correctly judge mathematical equality. Compare floating-point with value comparison (==) or a tolerance comparison.'},

 {'id':'MEM33-C','cat':'MEM · Rule · L2','compiles':True,
  'title':'유연 배열 멤버를 가진 구조체는 동적으로 할당·복사한다',
  'title_en':'Allocate and copy structures containing a flexible array member dynamically',
  'bad': r"""#include <stdio.h>
struct Buf { size_t n; char d[]; };   /* 유연 배열 멤버 */
int main(void){
    struct Buf b;       /* 자동 객체로 선언 — d 를 위한 공간이 전혀 없음 */
    b.n = 1;
    b.d[0] = 'x';       /* 할당되지 않은 영역에 쓰기 — 미정의 동작·손상 */
    printf("%zu\n", b.n);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
struct Buf { size_t n; char d[]; };
int main(void){
    size_t len = 8;
    struct Buf *b = malloc(sizeof *b + len);   /* 헤더 + 배열 공간을 함께 할당 */
    if (b == NULL) return 1;
    b->n = len;
    b->d[0] = 'x';
    printf("%c\n", b->d[0]);
    free(b);
    return 0;
}""",
  'why':'유연 배열 멤버(char d[])는 구조체 크기에 포함되지 않아, 자동·정적 객체로 선언하면 그 배열을 위한 실제 메모리가 전혀 확보되지 않은 채 접근하게 되어 인접 메모리를 손상시킨다. sizeof(구조체)+배열길이 만큼 동적 할당해 멤버 공간을 확보하고, 복사도 그 크기대로 한다.',
  'why_en':'A flexible array member (char d[]) is not counted in the struct size, so declaring the struct as an automatic or static object accesses an array with no memory reserved, corrupting adjacent memory. Allocate sizeof(struct)+array-length dynamically to reserve the member’s space, and copy by that size.'},

 {'id':'MEM36-C','cat':'MEM · Rule · L2','compiles':True,
  'title':'realloc 로 과도 정렬(over-aligned) 객체의 정렬을 잃지 않는다',
  'title_en':'Do not modify the alignment of objects by calling realloc()',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    void *p = aligned_alloc(64, 64);   /* 64바이트 정렬 요청 */
    if (p == NULL) return 1;
    void *q = realloc(p, 128);         /* realloc 은 기본 정렬만 보장 — 64바이트 정렬이 깨질 수 있음 */
    if (q == NULL) { free(p); return 1; }
    printf("%d\n", ((size_t)q % 64) == 0);
    free(q);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <string.h>
#include <stdio.h>
int main(void){
    void *p = aligned_alloc(64, 64);
    if (p == NULL) return 1;
    void *q = aligned_alloc(64, 128);   /* 정렬을 유지한 새 블록 할당 */
    if (q == NULL) { free(p); return 1; }
    memcpy(q, p, 64); free(p);          /* 복사 후 이전 블록 해제 */
    printf("%d\n", ((size_t)q % 64) == 0);
    free(q);
    return 0;
}""",
  'why':'realloc 은 malloc 과 동일한 기본 정렬만 보장하므로, aligned_alloc 등으로 과도 정렬한 객체를 realloc 하면 반환 블록의 정렬이 요구 정렬보다 약해져 SIMD·하드웨어 접근에서 오류가 난다. 정렬이 필요하면 새 정렬 블록을 할당해 복사하고 이전 블록을 해제한다.',
  'why_en':'realloc only guarantees the same default alignment as malloc, so reallocating an over-aligned object (from aligned_alloc) can return a block whose alignment is weaker than required, faulting SIMD or hardware access. When alignment matters, allocate a new aligned block, copy, and free the old one.'},

 {'id':'FIO32-C','cat':'FIO · Rule · L2','compiles':True,
  'title':'장치 특수 파일(device file)에 일반 파일 연산을 가정하지 않는다',
  'title_en':'Do not perform operations on devices that are only appropriate for files',
  'bad': r"""#define _GNU_SOURCE
#include <stdio.h>
static void read_all(FILE *f){ char b[16]; (void)fread(b, 1, sizeof b, f); }
int main(void){
    const char *user_path = "/dev/zero";   /* 사용자 입력이 장치 파일일 수 있음 */
    FILE *f = fopen(user_path, "r");
    if (f) { read_all(f); fclose(f); }      /* 일반 파일 가정 — 블로킹/무한 입력 위험 */
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <stdio.h>
#include <sys/stat.h>
int main(void){
    const char *path = "/etc/hostname";
    struct stat st;
    if (stat(path, &st) == 0 && S_ISREG(st.st_mode)) {   /* 일반 파일인지 확인 후 열기 */
        FILE *f = fopen(path, "r");
        if (f) fclose(f);
    }
    return 0;
}""",
  'why':'사용자가 준 경로가 /dev/* 같은 장치 특수 파일을 가리키면, 일반 파일이라는 가정으로 읽기·시킹을 하다가 무한 블로킹이나 예기치 않은 동작(DoS)에 빠질 수 있다. 열기 전에 stat 으로 일반 파일(S_ISREG)인지 확인한다.',
  'why_en':'If a user-supplied path points to a device special file like /dev/*, assuming it is a regular file and reading/seeking it can cause indefinite blocking or unexpected behaviour (DoS). Check with stat that it is a regular file (S_ISREG) before opening.'},

 {'id':'FIO38-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'FILE 객체를 복사하지 않는다',
  'title_en':'Do not copy a FILE object',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE f2 = *stdin;   /* FILE 객체를 값으로 복사 — 내부 상태가 어긋나 미정의 동작 */
    char buf[8];
    (void)fread(buf, 1, sizeof buf, &f2);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = stdin;    /* 항상 FILE 포인터로만 다룸 */
    char buf[8];
    (void)fread(buf, 1, sizeof buf, f);
    return 0;
}""",
  'why':'FILE 객체는 버퍼 포인터·위치·오류 플래그 등 내부 상태를 담고 구현이 그 주소를 추적하므로, 값으로 복사하면 복사본과 원본의 상태가 어긋나 미정의 동작이 된다. 스트림은 언제나 FILE 포인터로만 참조·전달한다.',
  'why_en':'A FILE object holds internal state (buffer pointers, position, error flags) and the implementation tracks its address, so copying it by value desynchronizes the copy and the original — undefined behaviour. Always reference and pass streams only through a FILE pointer.'},

 {'id':'FIO39-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'위치 지정 없이 입력과 출력을 번갈아 하지 않는다',
  'title_en':'Do not alternately input and output from a stream without an intervening flush or positioning call',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fprintf(f, "42 ");
    int x = 0;
    fscanf(f, "%d", &x);   /* 출력→입력 전환 사이에 위치 지정/flush 없음 — 미정의 동작 */
    fclose(f);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fprintf(f, "42 ");
    fflush(f);
    fseek(f, 0, SEEK_SET);   /* 전환 사이에 위치 지정으로 버퍼 상태 정리 */
    int x = 0;
    fscanf(f, "%d", &x);
    fclose(f);
    return 0;
}""",
  'why':'갱신(읽기/쓰기 겸용) 모드 스트림에서 fflush 나 fseek/fsetpos 같은 위치 지정 없이 출력 직후 입력으로(또는 그 반대로) 전환하면, 내부 버퍼 상태가 정의되지 않아 미정의 동작이 된다. 입출력 전환 사이에 flush 나 위치 지정 호출을 둔다.',
  'why_en':'On an update-mode (read/write) stream, switching from output to input (or vice versa) without an intervening fflush or positioning call (fseek/fsetpos) leaves the internal buffer state undefined — undefined behaviour. Place a flush or positioning call between input and output.'},

 {'id':'FIO40-C','cat':'FIO · Rule · L3','compiles':True,
  'title':'fgets/fgetws 실패 시 대상 문자열을 재설정한다',
  'title_en':'Reset strings on fgets() or fgetws() failure',
  'bad': r"""#include <stdio.h>
int main(void){
    char buf[64];
    FILE *f = fopen("/nonexistent_xyz123", "r");
    if (fgets(buf, sizeof buf, f ? f : stdin) == NULL) {
        printf("[%s]\n", buf);   /* 실패 후 buf 는 불확정 — 그대로 사용하면 오동작 */
    }
    if (f) fclose(f);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char buf[64] = "";
    FILE *f = fopen("/nonexistent_xyz123", "r");
    if (f == NULL || fgets(buf, sizeof buf, f) == NULL) {
        buf[0] = '\0';   /* 실패 시 빈 문자열로 재설정 */
        printf("read failed\n");
    } else {
        printf("[%s]\n", buf);
    }
    if (f) fclose(f);
    return 0;
}""",
  'why':'fgets 가 실패(오류·EOF)를 NULL 로 알릴 때 대상 버퍼의 내용은 불확정이므로, 그대로 출력·파싱하면 이전 데이터나 쓰레기 값을 처리하게 된다. 실패 시 버퍼를 빈 문자열로 재설정한 뒤 오류 경로를 처리한다.',
  'why_en':'When fgets reports failure (error or EOF) by returning NULL, the destination buffer contents are indeterminate, so using them directly processes stale or garbage data. Reset the buffer to an empty string on failure and then handle the error path.'},

 {'id':'FIO41-C','cat':'FIO · Rule · L1','compiles':True,
  'title':'부작용이 있는 표현식을 getc/putc 등의 스트림 인자로 넘기지 않는다',
  'title_en':'Do not call getc(), putc(), getwc(), or putwc() with a stream argument that has side effects',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *files[2] = { stdin, stdin };
    int i = 0;
    int c = getc(files[i++]);   /* getc 가 매크로면 스트림 인자(i++)를 여러 번 평가 */
    printf("i=%d\n", i);         /* i 가 의도보다 더 증가할 수 있음 */
    (void)c;
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *files[2] = { stdin, stdin };
    int i = 0;
    FILE *f = files[i++];   /* 부작용을 먼저 분리해 변수에 담음 */
    int c = getc(f);
    printf("i=%d\n", i);
    (void)c;
    return 0;
}""",
  'why':'getc/putc 는 성능을 위해 매크로로 구현될 수 있고, 그 경우 스트림 인자를 본문에서 여러 번 평가하므로 i++ 같은 부작용이 의도보다 여러 번 일어난다. 부작용 있는 표현식은 먼저 변수에 담아 그 변수를 인자로 전달한다.',
  'why_en':'getc/putc may be implemented as macros for speed, in which case the stream argument is evaluated multiple times in the body, so a side effect like i++ happens more times than intended. Evaluate the side-effecting expression into a variable first and pass that variable.'},

 {'id':'FIO44-C','cat':'FIO · Rule · L2','compiles':True,
  'title':'fsetpos 에는 fgetpos 가 반환한 값만 사용한다',
  'title_en':'Only use values for fsetpos() that are returned from fgetpos()',
  'bad': r"""#include <stdio.h>
#include <string.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fprintf(f, "hello");
    fpos_t pos;
    memset(&pos, 0, sizeof pos);   /* fgetpos 가 만든 값이 아닌 임의 값 */
    fsetpos(f, &pos);              /* 임의 fpos_t 사용 — 미정의 동작 */
    fclose(f);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fpos_t pos;
    fgetpos(f, &pos);    /* 같은 스트림에서 위치를 얻고 */
    fprintf(f, "hello");
    fsetpos(f, &pos);    /* 그 값으로만 복원 */
    fclose(f);
    return 0;
}""",
  'why':'fpos_t 는 구현 정의 불투명 타입이라 fgetpos 로 얻은 값만 의미가 있는데, 임의로 만든 값을 fsetpos 에 넘기면 정의되지 않은 위치로 해석되어 미정의 동작이 된다. 같은 스트림에서 fgetpos 로 얻은 위치 값만 fsetpos 에 사용한다.',
  'why_en':'fpos_t is an implementation-defined opaque type whose values are meaningful only when produced by fgetpos, so passing a hand-crafted value to fsetpos is interpreted as an undefined position — undefined behaviour. Use only position values obtained from fgetpos on the same stream.'},

 {'id':'FIO46-C','cat':'FIO · Rule · L2','compiles':True,
  'title':'닫힌 파일에 접근하지 않는다',
  'title_en':'Do not access a closed file',
  'bad': r"""#include <stdio.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fclose(f);
    fprintf(f, "x");   /* 닫은 뒤 사용 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    FILE *f = tmpfile();
    if (!f) return 1;
    fprintf(f, "x");   /* 닫기 전에 모든 사용을 완료 */
    fclose(f);
    f = NULL;          /* 닫은 뒤 포인터를 무효화 */
    return 0;
}""",
  'why':'fclose 이후의 FILE 포인터는 더 이상 유효한 스트림을 가리키지 않으므로, 그 포인터로 입출력을 하면 해제된 자원에 접근하는 미정의 동작이 된다. 모든 사용을 닫기 전에 끝내고, 닫은 뒤에는 포인터를 NULL 로 무효화해 재사용을 차단한다.',
  'why_en':'After fclose, a FILE pointer no longer refers to a valid stream, so doing I/O through it accesses a released resource — undefined behaviour. Complete all use before closing and null out the pointer afterward to prevent reuse.'},

 {'id':'ENV32-C','cat':'ENV · Rule · L2','compiles':True,
  'title':'atexit 등록 핸들러는 정상적으로 반환해야 한다',
  'title_en':'All exit handlers must return normally',
  'bad': r"""#include <stdlib.h>
#include <setjmp.h>
static jmp_buf env;
static void cleanup(void){ longjmp(env, 1); }   /* 종료 핸들러가 반환하지 않고 점프 — 미정의 */
int main(void){
    atexit(cleanup);
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
static void free_resources(void){ printf("cleanup done\n"); }
static void cleanup(void){ free_resources(); }   /* 작업 후 정상 반환 */
int main(void){
    atexit(cleanup);
    return 0;
}""",
  'why':'atexit 으로 등록한 종료 핸들러가 longjmp 로 점프하거나 exit 를 다시 호출하는 등 정상적으로 반환하지 않으면, 종료 처리 순서가 깨져 미정의 동작이 된다. 종료 핸들러는 자원 정리 같은 작업을 마친 뒤 호출자에게 정상적으로 반환한다.',
  'why_en':'If an atexit-registered handler does not return normally — e.g., it longjmps or calls exit again — the exit-processing sequence is broken, causing undefined behaviour. An exit handler should finish its work (such as resource cleanup) and return normally to its caller.'},

 {'id':'SIG35-C','cat':'SIG · Rule · L1','compiles':True,
  'title':'계산 예외(연산 오류) 시그널 핸들러에서 정상 반환하지 않는다',
  'title_en':'Do not return from a computational exception signal handler',
  'bad': r"""#include <signal.h>
static void h(int s){ (void)s; return; }   /* SIGFPE 핸들러가 반환 → 결함 명령 재실행 */
int main(void){
    signal(SIGFPE, h);
    return 0;
}""",
  'good': r"""#include <signal.h>
#include <stdlib.h>
static volatile sig_atomic_t fpe = 0;
static void h(int s){ (void)s; fpe = 1; _Exit(1); }   /* 정상 반환하지 않고 안전히 종료 */
int main(void){
    signal(SIGFPE, h);
    return 0;
}""",
  'why':'0 나눗셈 등 계산 예외(SIGFPE)의 핸들러에서 그냥 반환하면, 결함을 일으킨 바로 그 명령이 재실행되어 같은 예외가 무한히 반복되거나 미정의 동작이 된다. 이런 핸들러는 정상 반환하지 않고 _Exit 등으로 안전하게 종료한다.',
  'why_en':'Returning from a handler for a computational exception like division by zero (SIGFPE) re-executes the very instruction that faulted, repeating the same exception indefinitely or causing undefined behaviour. Such handlers must not return normally; terminate safely with _Exit or similar.'},

 {'id':'CON30-C','cat':'CON · Rule · L2','compiles':True,
  'title':'스레드별 저장소(thread-specific storage)를 정리한다',
  'title_en':'Clean up thread-specific storage',
  'bad': r"""#include <pthread.h>
#include <stdlib.h>
static pthread_key_t key;
int main(void){
    pthread_key_create(&key, NULL);   /* 소멸자(destructor) 미등록 — 스레드 종료 시 누수 */
    pthread_setspecific(key, malloc(64));
    return 0;
}""",
  'good': r"""#include <pthread.h>
#include <stdlib.h>
static pthread_key_t key;
int main(void){
    pthread_key_create(&key, free);   /* 소멸자 등록 — 스레드 종료 시 자동 해제 */
    pthread_setspecific(key, malloc(64));
    return 0;
}""",
  'why':'스레드별 저장소에 동적 할당한 값을 넣으면서 소멸자(정리 콜백)를 등록하지 않으면, 스레드가 종료될 때 그 값이 해제되지 않아 스레드마다 메모리가 누수된다. 키 생성 시 정리 함수(예: free)를 등록하거나 스레드 종료 전에 명시적으로 해제한다.',
  'why_en':'Storing a dynamically allocated value in thread-specific storage without registering a destructor (cleanup callback) leaks that value when the thread exits, accumulating leaks per thread. Register a cleanup function (e.g., free) at key creation, or free it explicitly before the thread exits.'},

 {'id':'CON32-C','cat':'CON · Rule · L2','compiles':True,
  'title':'비트필드 접근 시 데이터 경쟁을 방지한다',
  'title_en':'Prevent data races when accessing bit-fields from multiple threads',
  'bad': r"""#include <pthread.h>
static struct { unsigned a : 1; unsigned b : 1; } f;
static void *t1(void *p){ (void)p; f.a = 1; return NULL; }   /* 서로 다른 비트지만 */
static void *t2(void *p){ (void)p; f.b = 1; return NULL; }   /* 같은 메모리 워드 동시 갱신 — 경쟁 */
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t1, NULL); pthread_create(&b, NULL, t2, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return f.a + f.b;
}""",
  'good': r"""#include <pthread.h>
static struct { unsigned a : 1; unsigned b : 1; } f;
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void *t1(void *p){ (void)p; pthread_mutex_lock(&m); f.a = 1; pthread_mutex_unlock(&m); return NULL; }
static void *t2(void *p){ (void)p; pthread_mutex_lock(&m); f.b = 1; pthread_mutex_unlock(&m); return NULL; }
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t1, NULL); pthread_create(&b, NULL, t2, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return f.a + f.b;
}""",
  'why':'인접한 비트필드는 같은 메모리 워드(저장 단위)를 공유하므로, 서로 다른 비트를 갱신하더라도 두 스레드가 그 워드를 동시에 읽고-쓰면 한쪽 갱신이 다른 쪽에 덮어써지는 데이터 경쟁이 발생한다. 비트필드 접근을 같은 잠금으로 보호한다.',
  'why_en':'Adjacent bit-fields share the same memory word (storage unit), so even when updating different bits, two threads reading and writing that word concurrently race — one update overwrites the other. Protect bit-field accesses with the same lock.'},

 {'id':'CON34-C','cat':'CON · Rule · L2','compiles':True,
  'title':'스레드 간 공유 객체는 적절한 저장 기간으로 선언한다',
  'title_en':'Declare objects shared between threads with appropriate storage durations',
  'bad': r"""#include <pthread.h>
static void *worker(void *arg){ int *p = arg; return (void *)(long)*p; }
static pthread_t spawn_with_local(void){
    int local = 0;            /* 자동 저장 기간 */
    pthread_t t;
    pthread_create(&t, NULL, worker, &local);   /* 함수 종료 시 local 소멸 — 댕글링 공유 */
    return t;
}
int main(void){ pthread_t t = spawn_with_local(); pthread_join(t, NULL); return 0; }""",
  'good': r"""#include <pthread.h>
static int shared = 0;        /* 정적 저장 기간 — 프로그램 수명 동안 유효 */
static void *worker(void *arg){ int *p = arg; return (void *)(long)*p; }
int main(void){
    pthread_t t;
    pthread_create(&t, NULL, worker, &shared);
    pthread_join(t, NULL);
    return 0;
}""",
  'why':'자동 저장 기간(지역) 객체의 주소를 다른 스레드와 공유하면, 그 객체를 만든 함수가 반환하는 순간 객체가 소멸해 공유 스레드가 댕글링 포인터를 참조하는 미정의 동작이 된다. 스레드 간 공유 객체는 정적 또는 동적 저장 기간으로 선언해 수명이 충분히 유지되게 한다.',
  'why_en':'Sharing the address of an automatic (local) object with another thread makes it a dangling pointer the moment the creating function returns and the object is destroyed — undefined behaviour. Declare objects shared between threads with static or dynamic storage duration so their lifetime is long enough.'},

 {'id':'CON37-C','cat':'CON · Rule · L2','compiles':True,
  'title':'멀티스레드 프로그램에서 signal() 을 호출하지 않는다',
  'title_en':'Do not call signal() in a multithreaded program',
  'bad': r"""#include <signal.h>
#include <pthread.h>
static void handler(int s){ (void)s; }
static void *worker(void *p){ (void)p; return NULL; }
int main(void){
    signal(SIGINT, handler);   /* 멀티스레드에서 signal() 의 동작은 미정의 */
    pthread_t t; pthread_create(&t, NULL, worker, NULL); pthread_join(t, NULL);
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <signal.h>
#include <pthread.h>
int main(void){
    sigset_t set;
    sigemptyset(&set); sigaddset(&set, SIGINT);
    pthread_sigmask(SIG_BLOCK, &set, NULL);   /* 모든 스레드에서 차단 후 */
    int sig;
    /* 전용 스레드에서 sigwait 로 동기 처리하는 모델(여기선 즉시 반환을 위해 호출만 예시) */
    (void)sig;
    return 0;
}""",
  'why':'멀티스레드 환경에서 signal() 로 설정한 핸들러가 어느 스레드에서 실행될지, 다른 스레드의 signal() 호출과 어떻게 상호작용할지는 표준이 정의하지 않아 동작이 미정의다. 시그널은 모든 스레드에서 차단한 뒤 전용 스레드에서 sigwait 로 동기적으로 처리하는 모델을 사용한다.',
  'why_en':'In a multithreaded program, which thread runs a handler set by signal() and how it interacts with other threads’ signal() calls is undefined by the standard. Block signals in all threads and handle them synchronously in a dedicated thread with sigwait.'},

 {'id':'CON38-C','cat':'CON · Rule · L2','compiles':True,
  'title':'조건 변수 사용 시 스레드 안전성과 진행성(liveness)을 지킨다',
  'title_en':'Preserve thread safety and liveness when using condition variables',
  'bad': r"""#include <pthread.h>
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
int main(void){
    pthread_cond_signal(&cv);   /* 잠금·술어 설정 없이 신호 — 대기 스레드 없으면 신호 유실 */
    return 0;
}""",
  'good': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
static int ready = 0;
int main(void){
    pthread_mutex_lock(&m);
    ready = 1;                  /* 잠금 안에서 술어를 갱신하고 */
    pthread_cond_broadcast(&cv);   /* 모든 대기자에게 신호(유실·기아 방지) */
    pthread_mutex_unlock(&m);
    return 0;
}""",
  'why':'조건 변수에 잠금과 술어(예: ready) 설정 없이 신호만 보내면, 아직 대기에 들어가지 않은 스레드가 신호를 놓쳐(신호 유실) 영원히 깨어나지 못하는 진행성 결함이 생긴다. 잠금 안에서 술어를 갱신한 뒤 신호(필요 시 broadcast)를 보내고, 대기 측은 while 술어 루프로 재확인한다.',
  'why_en':'Signaling a condition variable without holding the lock and setting a predicate (e.g., ready) lets a thread not yet waiting miss the signal (lost wakeup), a liveness defect where it never wakes. Update the predicate under the lock before signaling (broadcast if needed), and have waiters re-check in a while-predicate loop.'},

 {'id':'CON41-C','cat':'CON · Rule · L2','compiles':True,
  'title':'가짜 실패가 가능한 원자 연산은 루프로 감싼다',
  'title_en':'Wrap functions that can fail spuriously in a loop',
  'bad': r"""#include <stdatomic.h>
int main(void){
    atomic_int v = 0;
    int expected = 0;
    atomic_compare_exchange_weak(&v, &expected, 5);   /* weak 은 가짜 실패 가능 — 한 번으론 보장 못함 */
    return atomic_load(&v);
}""",
  'good': r"""#include <stdatomic.h>
int main(void){
    atomic_int v = 0;
    int expected = 0;
    while (!atomic_compare_exchange_weak(&v, &expected, 5)) {
        /* 가짜 실패 시 expected 가 갱신되므로 루프로 재시도 */
    }
    return atomic_load(&v);
}""",
  'why':'atomic_compare_exchange_weak 같은 연산은 값이 일치해도 하드웨어 사정으로 가짜 실패(spurious failure)할 수 있어, 한 번 호출로는 교환 성공을 보장하지 못한다. 성공할 때까지 루프로 감싸 재시도하고(strong 변형이 적합한 경우엔 그쪽을 쓴다), 매 반복에서 expected 갱신을 활용한다.',
  'why_en':'Operations like atomic_compare_exchange_weak may fail spuriously due to hardware reasons even when the values match, so a single call does not guarantee the exchange. Wrap it in a retry loop until it succeeds (or use the strong variant when appropriate), making use of the updated expected each iteration.'},

 {'id':'MSC38-C','cat':'MSC · Rule · L1','compiles':True,
  'title':'미리 정의된(predefined) 식별자를 객체처럼 다루지 않는다',
  'title_en':'Do not treat a predefined identifier as an object',
  'bad': r"""#include <stdio.h>
static const char *saved;
static void here(void){
    saved = &__func__[0];   /* __func__ 의 주소를 보관 — 수명·표현이 보장되지 않음 */
}
int main(void){ here(); printf("%s\n", saved ? "set" : "null"); return 0; }""",
  'good': r"""#include <stdio.h>
#include <string.h>
static char name[64];
static void here(void){
    strncpy(name, __func__, sizeof name - 1);   /* 값을 복사해 사용 */
    name[sizeof name - 1] = '\0';
}
int main(void){ here(); printf("%s\n", name); return 0; }""",
  'why':'__func__ 같은 미리 정의된 식별자는 일반 객체가 아니라 컴파일러가 함수마다 제공하는 특수 식별자라, 그 주소를 보관해 함수 밖에서 재사용하는 동작은 수명·표현이 보장되지 않는다. 필요한 값은 별도 버퍼에 복사해 사용한다.',
  'why_en':'A predefined identifier like __func__ is not an ordinary object but a special, compiler-provided identifier per function, so storing its address and reusing it outside the function has no guaranteed lifetime or representation. Copy the needed value into a separate buffer and use that.'},

 {'id':'MSC39-C','cat':'MSC · Rule · L1','compiles':True,
  'title':'불확정 상태의 va_list 에 va_arg 를 호출하지 않는다',
  'title_en':'Do not call va_arg() on a va_list that has an indeterminate value',
  'bad': r"""#include <stdarg.h>
#include <stdio.h>
static int consume(va_list ap){ return va_arg(ap, int); }   /* 인자를 소비 */
static int bad_first(int n, ...){
    va_list ap; va_start(ap, n);
    (void)consume(ap);          /* 피호출자가 ap 를 소비 → ap 는 불확정 상태가 될 수 있음 */
    int x = va_arg(ap, int);    /* 소비된 ap 재사용 — 미정의 동작 */
    va_end(ap);
    return x;
}
int main(void){ printf("%d\n", bad_first(2, 10, 20)); return 0; }""",
  'good': r"""#include <stdarg.h>
#include <stdio.h>
static int consume(va_list ap){ return va_arg(ap, int); }
static int good_first(int n, ...){
    va_list ap, copy;
    va_start(ap, n);
    va_copy(copy, ap);          /* 독립 복사본을 만들어 넘김 */
    (void)consume(copy);
    va_end(copy);
    int x = va_arg(ap, int);    /* 원본 ap 는 소비되지 않아 안전 */
    va_end(ap);
    return x;
}
int main(void){ printf("%d\n", good_first(2, 10, 20)); return 0; }""",
  'why':'va_list 를 다른 함수에 값으로 넘기면 그 함수가 va_arg 로 인자를 소비해 호출 측의 va_list 가 불확정 상태가 될 수 있는데, 그 상태에서 다시 va_arg 를 부르면 미정의 동작이 된다. 넘길 때는 va_copy 로 독립 복사본을 만들어 원본 상태를 보존한다.',
  'why_en':'Passing a va_list by value to another function lets that function consume arguments via va_arg, potentially leaving the caller’s va_list in an indeterminate state, and calling va_arg again then is undefined behaviour. Make an independent copy with va_copy before passing to preserve the original’s state.'},

 {'id':'POS30-C','cat':'POS · Rule · L1','compiles':True,
  'title':'readlink() 를 올바르게 사용한다(널 종료·버퍼 크기)',
  'title_en':'Use the readlink() function properly',
  'bad': r"""#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
int main(void){
    char buf[64];
    readlink("/proc/self/exe", buf, sizeof buf);   /* 반환 무시 + 널 종료 안 함 + 잘림 가능 */
    printf("%s\n", buf);   /* 널 종료되지 않은 버퍼 출력 — 경계 밖 읽기 */
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
int main(void){
    char buf[64];
    ssize_t n = readlink("/proc/self/exe", buf, sizeof buf - 1);   /* 널 자리 확보 */
    if (n >= 0) {
        buf[n] = '\0';   /* 반환 길이로 직접 널 종료 */
        printf("%s\n", buf);
    }
    return 0;
}""",
  'why':'readlink 는 대상 문자열에 널 종료 문자를 붙이지 않고, 버퍼가 작으면 조용히 잘라 쓰며 반환값으로만 실제 길이를 알린다. 따라서 반환값을 무시하거나 널 종료를 직접 하지 않으면 경계 밖 읽기·잘린 경로 사용 결함이 생긴다. 버퍼에 널 자리를 남기고, 반환 길이로 직접 널 종료한다.',
  'why_en':'readlink does not null-terminate the target string, silently truncates if the buffer is small, and reports the actual length only via its return value. So ignoring the return value or not null-terminating yourself causes out-of-bounds reads or use of a truncated path. Reserve room for the terminator and null-terminate using the returned length.'},

 {'id':'POS36-C','cat':'POS · Rule · L1','compiles':True,
  'title':'권한 포기(setuid/setgid)는 올바른 순서로 수행한다',
  'title_en':'Observe correct revocation order while relinquishing privileges',
  'bad': r"""#define _GNU_SOURCE
#include <unistd.h>
int main(void){
    /* 데모: 실제 권한 변경은 root 권한이 필요하므로 호출 순서만 예시 */
    (void)setuid(1000);   /* 사용자 권한을 먼저 버리면 그룹 권한을 버릴 권한이 사라짐 */
    (void)setgid(1000);   /* 이미 권한이 없어 실패할 수 있음 */
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <unistd.h>
int main(void){
    (void)setgid(1000);   /* 그룹(및 보조 그룹) 권한을 먼저 포기 */
    (void)setuid(1000);   /* 그 다음 사용자 권한 포기 */
    return 0;
}""",
  'why':'사용자(uid) 권한을 먼저 포기하면 그룹(gid)·보조 그룹 권한을 변경할 권한까지 함께 사라져, 그룹 권한이 상승된 채로 남는 위험이 생긴다. 항상 그룹·보조 그룹 권한을 먼저 포기하고 사용자 권한을 나중에 포기해 모든 상승 권한이 확실히 내려가게 한다.',
  'why_en':'Relinquishing user (uid) privileges first also removes the ability to change group (gid) and supplementary-group privileges, risking leaving elevated group privileges in place. Always drop group and supplementary-group privileges first and user privileges last, so all elevated privileges are reliably lowered.'},

 {'id':'POS37-C','cat':'POS · Rule · L1','compiles':True,
  'title':'권한 포기가 실제로 성공했는지 확인한다',
  'title_en':'Ensure that privilege relinquishment is successful',
  'bad': r"""#define _GNU_SOURCE
#include <unistd.h>
static void do_work(void){ /* 권한이 필요한 작업 */ }
int main(void){
    setuid(1000);   /* 반환값 미검사 — 실패해도 상승 권한으로 계속 실행 */
    do_work();
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <unistd.h>
#include <stdlib.h>
static void do_work(void){ /* 권한이 필요한 작업 */ }
int main(void){
    if (setuid(1000) != 0) { _Exit(1); }       /* 반환값 검사 */
    if (getuid() != 1000) { _Exit(1); }         /* 실제로 포기됐는지 재확인 */
    do_work();
    return 0;
}""",
  'why':'setuid/setgid 호출이 실패해도 반환값을 무시하면 의도와 달리 상승된 권한이 그대로 유지된 채 위험한 작업을 수행하게 되어 권한 상승 취약점이 된다. 반환값을 검사하고, getuid/getgid 로 실제 권한이 의도대로 낮아졌는지까지 확인한다.',
  'why_en':'Ignoring the return value of setuid/setgid when it fails lets the program run sensitive work with elevated privileges still intact — a privilege-escalation vulnerability. Check the return value and also verify with getuid/getgid that privileges were actually lowered as intended.'},

 {'id':'POS38-C','cat':'POS · Rule · L2','compiles':True,
  'title':'fork 후 파일 디스크립터 경쟁을 피한다',
  'title_en':'Beware of race conditions when using fork and file descriptors',
  'bad': r"""#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
int main(void){
    int fd = open("/dev/null", O_WRONLY);
    pid_t p = fork();
    (void)p;
    write(fd, "x", 1);   /* 부모/자식이 같은 fd(오프셋 공유)에 동시 쓰기 — 데이터 섞임 */
    if (fd >= 0) close(fd);
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
int main(void){
    pid_t p = fork();
    int fd = open("/dev/null", O_WRONLY);   /* 부모·자식이 각자 fd 를 연다 */
    if (fd >= 0) { write(fd, "x", 1); close(fd); }
    (void)p;
    return 0;
}""",
  'why':'fork 전에 연 파일 디스크립터는 부모와 자식이 동일한 열린-파일 기술자(파일 오프셋)를 공유하므로, 둘이 동기화 없이 동시에 쓰면 오프셋 경쟁으로 데이터가 섞이거나 덮어써진다. 자식이 자체 디스크립터를 새로 열거나 명시적 동기화로 접근을 직렬화한다.',
  'why_en':'A file descriptor opened before fork is shared by parent and child as the same open-file description (file offset), so concurrent writes without synchronization race on the offset, interleaving or overwriting data. Have the child open its own descriptor, or serialize access with explicit synchronization.'},

 {'id':'POS39-C','cat':'POS · Rule · L1','compiles':True,
  'title':'데이터 전송 시 올바른 바이트 순서(byte ordering)를 사용한다',
  'title_en':'Use the correct byte ordering when transferring data between systems',
  'bad': r"""#include <stdint.h>
#include <stdio.h>
static uint32_t get_value(void){ return 0x01020304u; }
int main(void){
    uint32_t v = get_value();
    /* 호스트 바이트 순서 그대로 전송한다고 가정 — 엔디안이 다른 수신측에서 값이 뒤바뀜 */
    printf("%02x %02x\n", (v >> 24) & 0xFF, v & 0xFF);
    return 0;
}""",
  'good': r"""#include <stdint.h>
#include <arpa/inet.h>
#include <stdio.h>
static uint32_t get_value(void){ return 0x01020304u; }
int main(void){
    uint32_t net = htonl(get_value());   /* 네트워크 바이트 순서(빅엔디안)로 변환해 전송 */
    /* 수신측은 ntohl 로 자신의 호스트 순서로 되돌린다 */
    printf("%02x %02x\n", (net >> 24) & 0xFF, net & 0xFF);
    return 0;
}""",
  'why':'엔디안이 서로 다른 호스트 사이에서 정수를 바이트 순서 변환 없이 그대로 전송하면, 수신측이 바이트를 반대로 해석해 0x01020304 가 0x04030201 처럼 뒤바뀐 값이 된다. 전송 전에 htonl/htons 로 네트워크 바이트 순서로 변환하고 수신측에서 ntohl/ntohs 로 되돌린다.',
  'why_en':'Sending an integer between hosts of different endianness without byte-order conversion makes the receiver interpret the bytes reversed, turning 0x01020304 into 0x04030201. Convert to network byte order with htonl/htons before sending and back with ntohl/ntohs on receipt.'},

 {'id':'POS44-C','cat':'POS · Rule · L1','compiles':True,
  'title':'스레드를 종료시키기 위해 시그널을 사용하지 않는다',
  'title_en':'Do not use signals to terminate threads',
  'bad': r"""#include <pthread.h>
#include <signal.h>
static void *worker(void *p){ (void)p; for(;;){ } return NULL; }
int main(void){
    pthread_t t; pthread_create(&t, NULL, worker, NULL);
    pthread_kill(t, SIGTERM);   /* 시그널로 스레드 강제 종료 — 잠금·자원 정리 안 됨 */
    return 0;
}""",
  'good': r"""#include <pthread.h>
#include <stdatomic.h>
static atomic_int stop = 0;
static void *worker(void *p){ (void)p; while (!atomic_load(&stop)) { } return NULL; }
int main(void){
    pthread_t t; pthread_create(&t, NULL, worker, NULL);
    atomic_store(&stop, 1);     /* 협조적 종료 플래그 */
    pthread_join(t, NULL);      /* 정상 종료를 기다림 */
    return 0;
}""",
  'why':'시그널로 스레드를 강제 종료하면 그 스레드가 보유한 잠금·동적 자원이 정리되지 않은 채 사라져, 다른 스레드가 영원히 잠금을 기다리는 교착이나 메모리 누수가 발생한다. 협조적 종료 플래그를 두고 스레드가 안전한 지점에서 스스로 빠져나오게 한 뒤 join 으로 회수한다.',
  'why_en':'Forcibly terminating a thread with a signal abandons the locks and dynamic resources it holds, causing deadlock (other threads waiting forever on a lock) or memory leaks. Use a cooperative stop flag so the thread exits itself at a safe point, then reap it with join.'},

 {'id':'POS47-C','cat':'POS · Rule · L2','compiles':True,
  'title':'비동기적으로 취소될 수 있는 스레드를 사용하지 않는다',
  'title_en':'Do not use threads that can be canceled asynchronously',
  'bad': r"""#include <pthread.h>
static void *worker(void *p){
    pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);   /* 임의 명령 사이에서 취소 가능 */
    for(;;){ }
    return p;
}
int main(void){
    pthread_t t; pthread_create(&t, NULL, worker, NULL);
    pthread_cancel(t); pthread_join(t, NULL);
    return 0;
}""",
  'good': r"""#include <pthread.h>
static void *worker(void *p){
    pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, NULL);   /* 취소 지점에서만 취소 */
    for(;;){ pthread_testcancel(); }   /* 안전한 취소 지점을 명시 */
    return p;
}
int main(void){
    pthread_t t; pthread_create(&t, NULL, worker, NULL);
    pthread_cancel(t); pthread_join(t, NULL);
    return 0;
}""",
  'why':'비동기 취소(PTHREAD_CANCEL_ASYNCHRONOUS)는 스레드를 임의의 명령 사이에서 즉시 멈춰, 자료구조 갱신 도중이거나 잠금을 쥔 상태에서 종료되어 불변식 손상·교착을 일으킨다. 지연 취소(DEFERRED)를 사용해 pthread_testcancel 같은 안전한 취소 지점에서만 취소되게 한다.',
  'why_en':'Asynchronous cancellation (PTHREAD_CANCEL_ASYNCHRONOUS) stops a thread instantly between arbitrary instructions, possibly mid-update of a data structure or while holding a lock, corrupting invariants or deadlocking. Use deferred cancellation so the thread is canceled only at safe cancellation points like pthread_testcancel.'},

 {'id':'POS48-C','cat':'POS · Rule · L2','compiles':True,
  'title':'다른 스레드가 잠근(또는 잠기지 않은) 뮤텍스를 잠금 해제하지 않는다',
  'title_en':'Do not unlock or destroy another POSIX thread’s mutex',
  'bad': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
int main(void){
    pthread_mutex_unlock(&m);   /* 잠그지 않은(소유하지 않은) 뮤텍스를 해제 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
int main(void){
    pthread_mutex_lock(&m);     /* 잠근 스레드가 */
    /* 임계 구역 */
    pthread_mutex_unlock(&m);   /* 같은 스레드에서 직접 해제 */
    return 0;
}""",
  'why':'POSIX 뮤텍스는 소유 개념이 있어, 잠그지 않았거나 다른 스레드가 잠근 뮤텍스를 해제하면 미정의 동작이 되어 잠금 상태가 손상되고 경쟁이 노출된다. 뮤텍스는 그것을 잠근 바로 그 스레드가 같은 임계 구역에서 직접 해제한다.',
  'why_en':'A POSIX mutex has ownership, so unlocking one that was not locked or was locked by a different thread is undefined behaviour that corrupts the lock state and exposes races. The thread that locked a mutex must unlock it itself within the same critical section.'},

 {'id':'POS49-C','cat':'POS · Rule · L2','compiles':True,
  'title':'인접 멤버에 서로 다른 스레드가 동시 접근할 때 동기화한다',
  'title_en':'When data must be accessed by multiple threads, provide a mutex and guarantee no adjacent data is also accessed',
  'bad': r"""#include <pthread.h>
static struct { char a; char b; } s;   /* 같은 워드에 인접한 멤버 */
static void *t1(void *p){ (void)p; s.a = 1; return NULL; }
static void *t2(void *p){ (void)p; s.b = 1; return NULL; }   /* 다른 멤버지만 같은 메모리 단위 — 경쟁 가능 */
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t1, NULL); pthread_create(&b, NULL, t2, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return s.a + s.b;
}""",
  'good': r"""#include <pthread.h>
static struct { char a; char b; } s;
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void *t1(void *p){ (void)p; pthread_mutex_lock(&m); s.a = 1; pthread_mutex_unlock(&m); return NULL; }
static void *t2(void *p){ (void)p; pthread_mutex_lock(&m); s.b = 1; pthread_mutex_unlock(&m); return NULL; }
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t1, NULL); pthread_create(&b, NULL, t2, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return s.a + s.b;
}""",
  'why':'CPU 는 메모리를 워드 단위로 읽고 쓰므로, 같은 워드 안에 인접한 별도 멤버(char a; char b;)라도 두 스레드가 각각 갱신하면 읽기-수정-쓰기 과정에서 한쪽 갱신이 사라지는 경쟁이 발생할 수 있다. 인접 멤버 접근을 같은 잠금으로 보호하거나 멤버를 캐시라인 단위로 분리한다.',
  'why_en':'CPUs read and write memory in word units, so even separate adjacent members in the same word (char a; char b;) can race when two threads update them, losing one update in the read-modify-write. Protect adjacent-member access with the same lock, or separate the members onto distinct cache lines.'},

 {'id':'POS50-C','cat':'POS · Rule · L2','compiles':True,
  'title':'스레드 간 공유하는 POSIX 객체는 적절한 저장 기간으로 선언한다',
  'title_en':'Declare objects shared between POSIX threads with appropriate storage durations',
  'bad': r"""#include <pthread.h>
static void *work(void *arg){ pthread_mutex_t *mp = arg; pthread_mutex_lock(mp); pthread_mutex_unlock(mp); return NULL; }
static pthread_t start(void){
    pthread_mutex_t m;          /* 자동 저장 기간 뮤텍스 */
    pthread_mutex_init(&m, NULL);
    pthread_t t;
    pthread_create(&t, NULL, work, &m);   /* start 종료 시 m 소멸 — 무효 객체 접근 */
    return t;
}
int main(void){ pthread_t t = start(); pthread_join(t, NULL); return 0; }""",
  'good': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;   /* 정적 저장 기간 */
static void *work(void *arg){ pthread_mutex_t *mp = arg; pthread_mutex_lock(mp); pthread_mutex_unlock(mp); return NULL; }
int main(void){
    pthread_t t;
    pthread_create(&t, NULL, work, &m);
    pthread_join(t, NULL);
    return 0;
}""",
  'why':'뮤텍스·조건변수 같은 POSIX 동기화 객체를 자동(지역) 저장 기간으로 선언해 다른 스레드와 공유하면, 그 객체를 만든 함수가 반환하는 순간 객체가 소멸해 공유 스레드가 무효 객체를 잠그려다 미정의 동작에 빠진다. 공유 동기화 객체는 정적 또는 동적 저장 기간으로 둔다.',
  'why_en':'Declaring POSIX synchronization objects like mutexes or condition variables with automatic (local) storage duration and sharing them with other threads destroys the object when the creating function returns, so a sharing thread locks an invalid object — undefined behaviour. Give shared synchronization objects static or dynamic storage duration.'},

 {'id':'POS51-C','cat':'POS · Rule · L2','compiles':True,
  'title':'순환 대기로 인한 스레드 교착을 방지한다',
  'title_en':'Avoid deadlock with POSIX threads by locking in a predefined order',
  'bad': r"""#include <pthread.h>
static pthread_mutex_t a = PTHREAD_MUTEX_INITIALIZER, b = PTHREAD_MUTEX_INITIALIZER;
static void *t2(void *p){ (void)p;
    pthread_mutex_lock(&b); pthread_mutex_lock(&a);   /* 반대 순서 — 순환 대기 교착 위험 */
    pthread_mutex_unlock(&a); pthread_mutex_unlock(&b); return NULL; }
int main(void){
    pthread_mutex_lock(&a); pthread_mutex_lock(&b);
    pthread_mutex_unlock(&b); pthread_mutex_unlock(&a);
    return 0;
}""",
  'good': r"""#include <pthread.h>
static pthread_mutex_t a = PTHREAD_MUTEX_INITIALIZER, b = PTHREAD_MUTEX_INITIALIZER;
static void *t2(void *p){ (void)p;
    pthread_mutex_lock(&a); pthread_mutex_lock(&b);   /* 전역 잠금 순서 a→b 로 통일 */
    pthread_mutex_unlock(&b); pthread_mutex_unlock(&a); return NULL; }
int main(void){
    pthread_mutex_lock(&a); pthread_mutex_lock(&b);
    pthread_mutex_unlock(&b); pthread_mutex_unlock(&a);
    return 0;
}""",
  'why':'스레드마다 두 뮤텍스를 잠그는 순서가 다르면(한쪽은 a→b, 다른 쪽은 b→a) 서로가 상대의 잠금을 기다리는 순환 대기 교착이 발생한다. 모든 스레드가 동일한 전역 잠금 순서(예: 항상 a→b)를 따르도록 강제해 순환을 끊는다.',
  'why_en':'If threads lock two mutexes in different orders (one a→b, another b→a), each waits on the other’s lock — a circular-wait deadlock. Enforce a single global lock ordering (e.g., always a→b) across all threads to break the cycle.'},

 {'id':'POS52-C','cat':'POS · Rule · L2','compiles':True,
  'title':'잠금을 보유한 채 블로킹 연산을 수행하지 않는다',
  'title_en':'Do not perform operations that can block while holding a POSIX lock',
  'bad': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void blocking_io(void){ /* 오래 걸리는 I/O 라고 가정 */ }
static void update(void){ /* 공유 상태 갱신 */ }
int main(void){
    pthread_mutex_lock(&m);
    blocking_io();   /* 잠금을 쥔 채 블로킹 — 다른 스레드가 그 시간 내내 대기 */
    update();
    pthread_mutex_unlock(&m);
    return 0;
}""",
  'good': r"""#include <pthread.h>
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void blocking_io(void){ /* 오래 걸리는 I/O 라고 가정 */ }
static void update(void){ /* 공유 상태 갱신 */ }
int main(void){
    blocking_io();   /* 블로킹은 잠금 밖에서 수행 */
    pthread_mutex_lock(&m);
    update();        /* 공유 상태 갱신만 짧게 잠금 */
    pthread_mutex_unlock(&m);
    return 0;
}""",
  'why':'잠금을 보유한 채 네트워크·디스크 I/O 같은 블로킹 연산을 하면, 그 잠금을 기다리는 다른 스레드들이 I/O 가 끝날 때까지 모두 멈춰 처리량이 급락하고 교착 위험이 커진다. 블로킹 연산은 잠금 밖에서 수행하고, 공유 상태를 실제로 갱신하는 짧은 구간만 잠근다.',
  'why_en':'Performing a blocking operation such as network or disk I/O while holding a lock stalls every other thread waiting on that lock until the I/O completes, crashing throughput and raising deadlock risk. Do blocking operations outside the lock and hold it only for the short section that actually updates shared state.'},

 {'id':'POS53-C','cat':'POS · Rule · L2','compiles':True,
  'title':'조건 변수는 항상 같은 뮤텍스와 함께 사용한다',
  'title_en':'Do not use more than one mutex for concurrent waiting operations on a condition variable',
  'bad': r"""#include <pthread.h>
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t m1 = PTHREAD_MUTEX_INITIALIZER, m2 = PTHREAD_MUTEX_INITIALIZER;
static void wait_a(void){ pthread_mutex_lock(&m1); pthread_cond_wait(&cv, &m1); pthread_mutex_unlock(&m1); }
static void wait_b(void){ pthread_mutex_lock(&m2); pthread_cond_wait(&cv, &m2); pthread_mutex_unlock(&m2); }
int main(void){ (void)&wait_a; (void)&wait_b; return 0; }   /* 같은 cv 에 서로 다른 뮤텍스 — 미정의 */""",
  'good': r"""#include <pthread.h>
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
static void wait_for(void){ pthread_mutex_lock(&m); pthread_cond_wait(&cv, &m); pthread_mutex_unlock(&m); }
int main(void){ (void)&wait_for; return 0; }   /* 항상 동일 뮤텍스(m) 사용 */""",
  'why':'하나의 조건 변수에 대해 서로 다른 뮤텍스로 동시에 대기하면, 조건 변수 내부의 대기 큐와 잠금 해제·재획득 규약이 깨져 미정의 동작이 된다. 한 조건 변수에는 항상 같은 뮤텍스를 짝지어 사용한다.',
  'why_en':'Waiting on one condition variable with different mutexes concurrently breaks the condition variable’s internal wait queue and its unlock/re-acquire protocol — undefined behaviour. Always pair a condition variable with the same single mutex.'},
]
