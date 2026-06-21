# -*- coding: utf-8 -*-
"""SEI CERT C 대표 규칙 — 위반/준수 예제 (사내 교육용, 규범 원문 비복제·자체 작성)"""
RULES = [
 {'id':'PRE30-C','cat':'PRE · Rule · L1',
  'title':'매크로 확장으로 인해 같은 식별자를 두 번 연결(##)하지 않는다',
  'bad': r"""#define JOIN(a, b) a ## b
// 한 토큰을 만들기 위해 또 다른 매크로 확장 결과를 붙이려 함
#define WIDE(x) L ## x
const wchar_t *s = WIDE("hi");  // L"hi" 가 아니라 미정의 토큰 연결""",
  'good': r"""#define WIDE_HELPER(x) L ## x
#define WIDE(x) WIDE_HELPER(x)   // 한 단계 우회로 인자를 먼저 확장
const wchar_t *s = WIDE("hi");   // 의도대로 L"hi" 생성""",
  'why':'토큰 연결(##)은 매크로 인자를 확장하기 전에 수행되므로 한 매크로에서 곧바로 붙이면 미정의 토큰이 만들어진다. 보조 매크로로 한 단계 우회해 인자를 먼저 확장시킨다.'},

 {'id':'PRE31-C','cat':'PRE · Rule · L1',
  'title':'안전하지 않은 매크로의 인자에서 부작용을 일으키지 않는다',
  'bad': r"""#define ABS(x) (((x) < 0) ? -(x) : (x))
int i = -5;
int a = ABS(i++);   // i++ 가 매크로 확장으로 여러 번 평가됨""",
  'good': r"""static inline int abs_int(int x) { return x < 0 ? -x : x; }
int i = -5;
int a = abs_int(i++);  // 함수는 인자를 한 번만 평가""",
  'why':'매크로는 인자를 텍스트로 치환하므로 부작용이 있는 식(i++)이 여러 번 평가되어 미정의 동작을 일으킨다. 인라인 함수를 사용하면 인자가 정확히 한 번만 평가된다.'},

 {'id':'DCL30-C','cat':'DCL · Rule · L3',
  'title':'객체는 참조되는 동안 유효한 수명을 갖도록 선언한다',
  'bad': r"""const char *get_label(void) {
    char buf[16];
    strcpy(buf, "ready");
    return buf;   // 지역 배열 주소 반환 — 함수 종료 시 무효
}""",
  'good': r"""const char *get_label(void) {
    static const char buf[] = "ready";  // 정적 수명
    return buf;   // 호출 후에도 유효
}""",
  'why':'자동 저장 수명을 가진 지역 객체의 주소를 반환하면 함수 종료 후 해당 메모리가 무효가 되어 댕글링 포인터가 된다. 정적 수명이나 호출자 제공 버퍼를 사용한다.'},

 {'id':'DCL37-C','cat':'DCL · Rule · L1',
  'title':'예약된 식별자(언더스코어·표준 이름)를 재선언·정의하지 않는다',
  'bad': r"""#define _MAX 100        // 언더스코어로 시작하는 예약 식별자 재정의
int errno = 0;             // 표준 식별자 재정의
size_t _len;""",
  'good': r"""#define APP_MAX 100      // 충돌하지 않는 자체 접두사 사용
#include <errno.h>          // 표준 errno 그대로 사용
size_t app_len;""",
  'why':'언더스코어로 시작하는 식별자나 표준 라이브러리 이름은 구현에 예약되어 있어 재정의 시 미정의 동작이 발생한다. 고유한 접두사를 가진 이름을 사용한다.'},

 {'id':'EXP33-C','cat':'EXP · Rule · L3',
  'title':'초기화되지 않은 메모리를 읽지 않는다',
  'bad': r"""int sum_first_n(int n) {
    int v[8];
    int total = 0;
    for (int i = 0; i < n; i++) total += v[i];  // v 미초기화 읽기
    return total;
}""",
  'good': r"""int sum_first_n(int n) {
    int v[8] = {0};   // 0 으로 초기화
    int total = 0;
    for (int i = 0; i < n && i < 8; i++) total += v[i];
    return total;
}""",
  'why':'초기화되지 않은 자동 변수는 불확정 값을 가지므로 이를 읽으면 미정의 동작과 정보 노출이 발생한다. 사용 전에 반드시 명시적으로 초기화한다.'},

 {'id':'EXP34-C','cat':'EXP · Rule · L1',
  'title':'널 포인터를 역참조하지 않는다',
  'bad': r"""size_t length(const char *s) {
    return strlen(s);   // s 가 NULL 이면 역참조 시 크래시
}""",
  'good': r"""size_t length(const char *s) {
    if (s == NULL) return 0;   // 널 검사 후 사용
    return strlen(s);
}""",
  'why':'널 포인터를 역참조하면 미정의 동작(흔히 크래시)이 발생한다. 함수 인자나 할당 반환값 등 널 가능성이 있는 포인터는 사용 전에 검사한다.'},

 {'id':'EXP44-C','cat':'EXP · Rule · L1',
  'title':'sizeof·_Alignof·_Generic 피연산자에서 부작용을 일으키지 않는다',
  'bad': r"""int i = 0;
size_t n = sizeof(i++);   // i++ 는 평가되지 않아 i 가 증가하지 않음
// 프로그래머는 i 가 1 이 되었다고 가정""",
  'good': r"""int i = 0;
size_t n = sizeof(i);     // 타입 크기만 필요
i++;                       // 증가는 별도 문장으로 명시""",
  'why':'sizeof의 피연산자는 (가변길이 배열 제외) 평가되지 않으므로 부작용 식을 넣으면 기대한 부작용이 발생하지 않는다. 부작용은 별도의 문장으로 분리한다.'},

 {'id':'INT30-C','cat':'INT · Rule · L2',
  'title':'부호 없는 정수 연산의 래핑(오버플로우)을 보장 검사한다',
  'bad': r"""unsigned int add(unsigned int a, unsigned int b) {
    return a + b;   // a + b 가 UINT_MAX 초과 시 조용히 래핑
}""",
  'good': r"""#include <limits.h>
int safe_add(unsigned int a, unsigned int b, unsigned int *r) {
    if (b > UINT_MAX - a) return -1;  // 래핑 사전 검사
    *r = a + b;
    return 0;
}""",
  'why':'부호 없는 정수는 오버플로우 시 모듈로 래핑되어 길이·인덱스 계산에서 보안 결함으로 이어진다. 연산 전에 한계를 비교해 래핑 가능성을 검사한다.'},

 {'id':'INT31-C','cat':'INT · Rule · L2',
  'title':'정수 변환 시 데이터·부호 손실이 없도록 보장한다',
  'bad': r"""long read_count(long n) {
    unsigned char c = n;   // 범위 초과 값이 잘려 손실
    return c;
}""",
  'good': r"""#include <limits.h>
int to_uchar(long n, unsigned char *out) {
    if (n < 0 || n > UCHAR_MAX) return -1;  // 범위 검사
    *out = (unsigned char)n;
    return 0;
}""",
  'why':'더 작거나 부호가 다른 정수형으로 변환할 때 값이 범위를 벗어나면 데이터 손실·부호 변화가 발생한다. 변환 전에 대상형의 범위를 검사한다.'},

 {'id':'INT32-C','cat':'INT · Rule · L2',
  'title':'부호 있는 정수 연산이 오버플로우하지 않도록 보장한다',
  'bad': r"""int mul(int a, int b) {
    return a * b;   // signed 오버플로우는 미정의 동작
}""",
  'good': r"""#include <limits.h>
int safe_mul(int a, int b, int *r) {
    if (a > 0 && b > 0 && a > INT_MAX / b) return -1;
    if (a < 0 && b < 0 && a < INT_MAX / b) return -1;
    *r = a * b;
    return 0;
}""",
  'why':'부호 있는 정수의 오버플로우는 미정의 동작으로 컴파일러 최적화에 따라 예측 불가능한 결과를 낸다. 연산 전에 피연산자 범위를 검사한다.'},

 {'id':'INT33-C','cat':'INT · Rule · L2',
  'title':'정수 나눗셈·나머지에서 0 나눗셈을 방지한다',
  'bad': r"""int avg(int sum, int n) {
    return sum / n;   // n 이 0 이면 미정의 동작
}""",
  'good': r"""int avg(int sum, int n, int *r) {
    if (n == 0) return -1;   // 0 나눗셈 방지
    *r = sum / n;
    return 0;
}""",
  'why':'0으로 나누거나 0으로 나머지 연산을 하면 미정의 동작이 발생한다. 나누기 전에 제수가 0이 아닌지 확인한다.'},

 {'id':'FLP32-C','cat':'FLP · Rule · L2',
  'title':'수학 함수의 도메인·범위 오류를 방지한다',
  'bad': r"""#include <math.h>
double root(double x) {
    return sqrt(x);   // x < 0 이면 도메인 오류(NaN)
}""",
  'good': r"""#include <math.h>
int root(double x, double *r) {
    if (x < 0.0) return -1;   // 도메인 검사
    *r = sqrt(x);
    return 0;
}""",
  'why':'sqrt·log·asin 등은 정의역을 벗어난 입력에 대해 도메인 오류(NaN)를 일으킨다. 함수 호출 전에 입력이 유효 범위인지 검사한다.'},

 {'id':'ARR30-C','cat':'ARR · Rule · L2',
  'title':'배열의 범위를 벗어난 인덱스를 만들거나 사용하지 않는다',
  'bad': r"""int get(int *a, size_t len, size_t i) {
    return a[i];   // i 가 len 이상이면 범위 밖 접근
}""",
  'good': r"""int get(int *a, size_t len, size_t i, int *out) {
    if (i >= len) return -1;   // 경계 검사
    *out = a[i];
    return 0;
}""",
  'why':'배열 경계를 벗어난 인덱스로 접근하면 미정의 동작과 버퍼 오버플로우 취약점이 발생한다. 인덱스를 사용하기 전에 길이와 비교한다.'},

 {'id':'ARR38-C','cat':'ARR · Rule · L2',
  'title':'라이브러리 함수에 무효한 포인터·길이를 전달하지 않는다',
  'bad': r"""void copy(char *dst, const char *src) {
    memcpy(dst, src, 32);   // dst/src 가 32바이트보다 작을 수 있음
}""",
  'good': r"""void copy(char *dst, size_t dn, const char *src, size_t sn) {
    size_t n = dn < sn ? dn : sn;   // 두 버퍼의 최소 크기만큼만
    memcpy(dst, src, n);
}""",
  'why':'memcpy 등에 실제 버퍼보다 큰 길이를 넘기면 범위를 벗어난 읽기·쓰기가 발생한다. 두 버퍼의 실제 크기를 알고 더 작은 값으로 복사 길이를 제한한다.'},

 {'id':'STR31-C','cat':'STR · Rule · L1',
  'title':'문자 데이터와 널 종료를 위한 충분한 저장공간을 확보한다',
  'bad': r"""void store(const char *in) {
    char buf[8];
    strcpy(buf, in);   // in 이 8바이트 이상이면 오버플로우
}""",
  'good': r"""void store(const char *in) {
    char buf[8];
    snprintf(buf, sizeof(buf), "%s", in);  // 크기 한정 복사
}""",
  'why':'대상 버퍼보다 긴 문자열을 복사하면 널 종료 문자를 포함해 버퍼 오버플로우가 발생한다. 크기를 명시하는 안전한 복사 함수를 사용한다.'},

 {'id':'STR32-C','cat':'STR · Rule · L2',
  'title':'문자열을 인자로 받는 함수에 널 종료를 보장한다',
  'bad': r"""void log_name(const char *src, size_t n) {
    char name[16];
    strncpy(name, src, sizeof(name));  // 널 종료 안 될 수 있음
    printf("%s\n", name);              // 비종료 문자열 사용
}""",
  'good': r"""void log_name(const char *src) {
    char name[16];
    snprintf(name, sizeof(name), "%s", src);  // 항상 널 종료
    printf("%s\n", name);
}""",
  'why':'strncpy는 원본이 길면 널 종료를 붙이지 않아 이후 문자열 함수가 경계를 넘어 읽는다. 항상 널 종료를 보장하는 방식으로 문자열을 다룬다.'},

 {'id':'MEM30-C','cat':'MEM · Rule · L1',
  'title':'해제된 메모리에 접근하지 않는다',
  'bad': r"""char *p = malloc(16);
free(p);
strcpy(p, "x");   // 해제 후 사용(use-after-free)""",
  'good': r"""char *p = malloc(16);
if (p) {
    strcpy(p, "x");
    free(p);
    p = NULL;     // 해제 후 포인터 무효화
}""",
  'why':'해제된 메모리에 접근하면 use-after-free 취약점으로 임의 코드 실행까지 이어질 수 있다. 해제 직후 포인터를 NULL로 설정해 재사용을 방지한다.'},

 {'id':'MEM31-C','cat':'MEM · Rule · L2',
  'title':'동적 할당 메모리는 정확히 한 번만 해제한다',
  'bad': r"""char *p = malloc(16);
free(p);
free(p);   // 이중 해제(double free)""",
  'good': r"""char *p = malloc(16);
free(p);
p = NULL;
free(p);   // NULL 해제는 무해 — 이중 해제 방지""",
  'why':'동일한 포인터를 두 번 해제하면 힙 메타데이터가 손상되어 미정의 동작·익스플로잇이 가능하다. 해제 후 NULL 대입으로 이중 해제를 차단한다.'},

 {'id':'MEM34-C','cat':'MEM · Rule · L1',
  'title':'동적으로 할당된 메모리만 free 한다',
  'bad': r"""char buf[16] = "hi";
char *p = buf;
free(p);   // 정적/자동 메모리를 free — 미정의 동작""",
  'good': r"""char *p = malloc(16);
if (p) {
    strcpy(p, "hi");
    free(p);   // malloc 으로 얻은 포인터만 free
}""",
  'why':'malloc 계열로 할당하지 않은 메모리(배열·정적 변수)를 free하면 미정의 동작이 발생한다. 동적 할당으로 얻은 포인터만 해제한다.'},

 {'id':'MEM35-C','cat':'MEM · Rule · L2',
  'title':'객체에 충분한 메모리를 할당한다',
  'bad': r"""int n = 100;
int *a = malloc(n);   // n*sizeof(int) 가 아닌 n 바이트만 할당
a[10] = 1;            // 범위 밖 쓰기""",
  'good': r"""int n = 100;
int *a = malloc(n * sizeof(*a));   // 요소 크기를 곱해 할당
if (a) a[10] = 1;""",
  'why':'요소 크기를 고려하지 않고 개수만큼만 할당하면 실제 객체가 들어갈 공간이 부족해 힙 오버플로우가 발생한다. 개수에 요소 크기를 곱해 할당한다.'},

 {'id':'FIO30-C','cat':'FIO · Rule · L1',
  'title':'사용자 입력을 포맷 문자열로 직접 사용하지 않는다',
  'bad': r"""void show(const char *user) {
    printf(user);   // 사용자 입력이 포맷 문자열로 해석됨
}""",
  'good': r"""void show(const char *user) {
    printf("%s", user);   // 고정 포맷, 입력은 인자로만
}""",
  'why':'사용자 입력을 포맷 문자열로 넘기면 %n·%s 등으로 메모리 읽기·쓰기가 가능한 포맷 스트링 취약점이 된다. 포맷은 항상 고정 리터럴로 두고 입력은 인자로 전달한다.'},

 {'id':'FIO34-C','cat':'FIO · Rule · L2',
  'title':'문자 입력값과 EOF·WEOF를 올바르게 구분한다',
  'bad': r"""char c;
while ((c = getchar()) != EOF) {  // char 로 받으면 EOF 와 0xFF 혼동
    putchar(c);
}""",
  'good': r"""int c;
while ((c = getchar()) != EOF) {  // int 로 받아 EOF 정확히 비교
    putchar(c);
}""",
  'why':'getchar의 반환값을 char에 담으면 유효 문자 0xFF와 EOF를 구별할 수 없어 무한 루프나 조기 종료가 발생한다. 반환값은 int로 받아 비교한다.'},

 {'id':'FIO47-C','cat':'FIO · Rule · L1',
  'title':'유효한 포맷 문자열과 일치하는 인자를 사용한다',
  'bad': r"""long v = 42;
printf("%d\n", v);   // long 을 %d 로 출력 — 변환 명세 불일치""",
  'good': r"""long v = 42;
printf("%ld\n", v);  // 인자 타입에 맞는 변환 명세""",
  'why':'변환 명세와 실제 인자의 타입·개수가 맞지 않으면 미정의 동작과 정보 노출이 발생한다. 각 인자 타입에 정확히 대응하는 명세를 사용한다.'},

 {'id':'ENV33-C','cat':'ENV · Rule · L1',
  'title':'system() 으로 명령을 실행하지 않는다',
  'bad': r"""void rm(const char *name) {
    char cmd[64];
    snprintf(cmd, sizeof(cmd), "rm %s", name);
    system(cmd);   // 셸 주입 가능
}""",
  'good': r"""#include <unistd.h>
void rm(const char *name) {
    if (unlink(name) != 0) {   // 셸 없이 직접 시스템 호출
        /* 오류 처리 */
    }
}""",
  'why':'system()은 셸을 거쳐 명령을 실행하므로 입력에 메타문자가 포함되면 명령 주입이 가능하다. 셸을 거치지 않는 직접 API나 exec 계열을 사용한다.'},

 {'id':'SIG30-C','cat':'SIG · Rule · L1',
  'title':'시그널 핸들러에서는 async-signal-safe 함수만 호출한다',
  'bad': r"""#include <signal.h>
#include <stdio.h>
void handler(int s) {
    printf("caught %d\n", s);   // printf 는 async-safe 아님
}""",
  'good': r"""#include <signal.h>
#include <unistd.h>
volatile sig_atomic_t flag = 0;
void handler(int s) {
    flag = 1;   // sig_atomic_t 플래그만 설정 — async-safe
}""",
  'why':'시그널 핸들러에서 비동기 안전하지 않은 함수를 호출하면 재진입으로 자료구조가 손상될 수 있다. 핸들러에서는 sig_atomic_t 플래그 설정 등 안전한 작업만 수행한다.'},

 {'id':'ERR30-C','cat':'ERR · Rule · L2',
  'title':'errno 를 호출 전 0 으로 설정하고 호출 직후 검사한다',
  'bad': r"""char *end;
long v = strtol(in, &end, 10);
if (errno != 0) {   // 호출 전 errno 미초기화 — 이전 값 오판
    /* ... */
}""",
  'good': r"""char *end;
errno = 0;          // 호출 전 초기화
long v = strtol(in, &end, 10);
if (errno != 0 || end == in) {   // 직후 검사
    /* 오류 처리 */
}""",
  'why':'errno는 성공 시 갱신되지 않으므로 호출 전에 0으로 초기화하지 않으면 이전 오류 값을 오판한다. 호출 직전 0으로 설정하고 직후에 검사한다.'},

 {'id':'ERR33-C','cat':'ERR · Rule · L1',
  'title':'표준 라이브러리 오류를 검출하고 처리한다',
  'bad': r"""FILE *f = fopen("data.txt", "r");
char buf[64];
fread(buf, 1, sizeof(buf), f);   // fopen 실패(NULL) 확인 안 함""",
  'good': r"""FILE *f = fopen("data.txt", "r");
if (f == NULL) return -1;   // 반환값 검사
size_t n = fread(buf, 1, sizeof(buf), f);
fclose(f);""",
  'why':'fopen·malloc 등의 반환값을 검사하지 않으면 실패 시 널 포인터 역참조나 잘못된 데이터 처리로 이어진다. 모든 표준 함수의 오류 반환을 검사한다.'},

 {'id':'CON33-C','cat':'CON · Rule · L1',
  'title':'라이브러리 함수 사용 시 데이터 경쟁을 회피한다',
  'bad': r"""char *t = strtok(buf, ",");   // strtok 는 내부 정적 상태로
// 다중 스레드에서 동시 호출 시 데이터 경쟁
while (t) { use(t); t = strtok(NULL, ","); }""",
  'good': r"""char *save;
char *t = strtok_r(buf, ",", &save);  // 재진입 버전, 상태를 호출자가 보유
while (t) { use(t); t = strtok_r(NULL, ",", &save); }""",
  'why':'strtok·rand 같은 함수는 내부 정적 상태를 공유해 다중 스레드에서 데이터 경쟁을 일으킨다. 재진입(_r) 또는 스레드 안전 변종을 사용한다.'},

 {'id':'MSC30-C','cat':'MSC · Rule · L1',
  'title':'보안 목적으로 rand() 를 사용하지 않는다',
  'bad': r"""unsigned token = rand();   // 예측 가능한 PRNG 로 보안 토큰 생성""",
  'good': r"""#include <stdint.h>
// 플랫폼 CSPRNG 사용 (예: arc4random / getrandom)
uint32_t token;
if (get_secure_random(&token, sizeof(token)) != 0) {
    /* 오류 처리 */
}""",
  'why':'rand()는 통계적·예측 가능성이 약해 토큰·키 생성에 쓰면 공격자가 값을 예측할 수 있다. 보안에는 암호학적으로 안전한 난수 생성기(CSPRNG)를 사용한다.'},

 {'id':'MSC32-C','cat':'MSC · Rule · L2',
  'title':'의사난수 생성기를 적절히 시드한다',
  'bad': r"""srand(1);            // 고정 시드 — 매 실행 동일한 난수열
int r = rand();""",
  'good': r"""#include <time.h>
srand((unsigned)time(NULL));   // 실행마다 다른 시드(비보안 용도 한정)
int r = rand();""",
  'why':'고정값으로 시드하면 매 실행 같은 난수열이 생성되어 예측이 쉬워진다. 비보안 용도라도 실행마다 변하는 값으로 시드하고, 보안 용도라면 CSPRNG를 쓴다.'},

 {'id':'MSC33-C','cat':'MSC · Rule · L1',
  'title':'asctime() 함수를 사용하지 않는다',
  'bad': r"""struct tm *t = localtime(&now);
char *s = asctime(t);   // 내부 고정 버퍼·범위 검사 없음
printf("%s", s);""",
  'good': r"""struct tm *t = localtime(&now);
char buf[64];
strftime(buf, sizeof(buf), "%a %b %d %H:%M:%S %Y", t);  // 크기 한정
printf("%s\n", buf);""",
  'why':'asctime은 입력 검증 없이 고정 내부 버퍼에 기록해 오버플로우 위험이 있고 스레드 안전하지 않다. 크기를 지정하는 strftime을 사용한다.'},
]
