# -*- coding: utf-8 -*-
"""MISRA C:2012 대표 규칙 — 위반/준수 예제 (사내 교육용, 규범 원문 비복제·자체 작성)"""
RULES = [
 {'id':'Dir 4.1','cat':'Required · Undecidable · Dir',
  'title':'런타임 실패 발생 가능성을 최소화하도록 설계한다',
  'bad': r"""int avg(const int *a, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) sum += a[i];
    return sum / n;   /* n이 0이면 0 나눗셈 */
}""",
  'good': r"""int avg(const int *a, int n, int *ok) {
    if (a == NULL || n <= 0) { *ok = 0; return 0; }
    int sum = 0;
    for (int i = 0; i < n; i++) sum += a[i];
    *ok = 1;
    return sum / n;
}""",
  'why':'0 나눗셈·널 역참조 같은 런타임 실패는 정의되지 않은 동작을 일으킨다. 분모·포인터·인덱스를 사전에 검사하여 실패 가능성을 줄여야 한다.'},

 {'id':'Dir 4.6','cat':'Advisory · Undecidable · Dir',
  'title':'크기와 부호가 명시된 typedef 정수형을 사용한다',
  'bad': r"""long  timestamp;   /* 폭이 플랫폼마다 다름 */
short flags;        /* 부호·폭 불명확 */
unsigned char b;""",
  'good': r"""#include <stdint.h>
int32_t  timestamp;
uint16_t flags;
uint8_t  b;""",
  'why':'기본 정수형은 폭·부호가 구현 정의라 이식 시 동작이 달라질 수 있다. stdint.h의 명시형(int32_t 등)을 써서 표현 범위를 고정한다.'},

 {'id':'Dir 4.7','cat':'Required · Undecidable · Dir',
  'title':'오류 정보를 반환하는 함수의 결과를 반드시 검사한다',
  'bad': r"""FILE *fp = fopen("data.bin", "rb");
fread(buf, 1, 256, fp);   /* fopen 실패 검사 없음 */
fclose(fp);""",
  'good': r"""FILE *fp = fopen("data.bin", "rb");
if (fp != NULL) {
    (void)fread(buf, 1, 256, fp);
    (void)fclose(fp);
}""",
  'why':'오류를 반환하는 함수의 결과를 무시하면 실패 상태에서 잘못된 자원을 계속 사용하게 된다. 반환값을 검사해 실패 경로를 처리해야 한다.'},

 {'id':'Dir 4.11','cat':'Required · Undecidable · Dir',
  'title':'라이브러리 함수에 전달하는 인자의 유효성을 검사한다',
  'bad': r"""double r = sqrt(x);   /* x가 음수면 정의역 오류 */
double q = log(y);    /* y<=0 이면 오류 */""",
  'good': r"""double r = (x >= 0.0) ? sqrt(x) : 0.0;
double q = (y > 0.0)  ? log(y)  : 0.0;""",
  'why':'sqrt·log 등 표준 함수는 정의역을 벗어난 입력에 대해 정의되지 않은 결과를 낸다. 호출 전 인자가 유효 범위 안인지 확인해야 한다.'},

 {'id':'Dir 4.12','cat':'Required · Decidable · Dir',
  'title':'동적 메모리 할당을 사용하지 않는다',
  'bad': r"""int *p = malloc(n * sizeof(int));
process(p, n);
free(p);   /* 단편화·누수·예측 불가 지연 */""",
  'good': r"""#define MAX_N 256
int buf[MAX_N];
if (n <= MAX_N) {
    process(buf, n);
}""",
  'why':'동적 할당은 단편화·누수·비결정적 지연을 유발해 안전 임계 시스템에서 위험하다. 정적/자동 저장소로 고정 크기 버퍼를 사용한다.'},

 {'id':'Dir 4.14','cat':'Required · Undecidable · Dir',
  'title':'외부에서 들어온 값의 유효성을 검증한다',
  'bad': r"""int idx = read_index_from_input();
table[idx] = 0;   /* 외부값을 검증 없이 인덱스로 사용 */""",
  'good': r"""int idx = read_index_from_input();
if (idx >= 0 && idx < TABLE_SIZE) {
    table[idx] = 0;
}""",
  'why':'신뢰할 수 없는 외부 입력을 검증 없이 사용하면 버퍼 오버런·논리 오류로 이어진다. 범위·형식·길이를 검증한 뒤 사용해야 한다.'},

 {'id':'Rule 8.4','cat':'Required · Decidable · Rule',
  'title':'외부 연결 정의에는 가시적인 선언(프로토타입)이 있어야 한다',
  'bad': r"""/* 헤더 없이 정의만 존재 */
int compute(int a, int b) {
    return a + b;
}""",
  'good': r"""/* math_util.h */
int compute(int a, int b);

/* math_util.c */
#include "math_util.h"
int compute(int a, int b) {
    return a + b;
}""",
  'why':'정의 전에 보이는 선언이 없으면 호출부와 정의의 타입 불일치를 컴파일러가 잡지 못한다. 헤더로 프로토타입을 공유한다.'},

 {'id':'Rule 9.1','cat':'Mandatory · Undecidable · Rule',
  'title':'값을 설정하기 전에 읽지 않는다(미초기화 사용 금지)',
  'bad': r"""int sum;
for (int i = 0; i < n; i++)
    sum += a[i];   /* sum 미초기화 상태에서 read */""",
  'good': r"""int sum = 0;
for (int i = 0; i < n; i++)
    sum += a[i];""",
  'why':'미초기화 자동 변수는 불확정 값을 가져 읽을 경우 결과가 정의되지 않는다. 사용 전에 반드시 초기화한다.'},

 {'id':'Rule 10.1','cat':'Required · Decidable · Rule',
  'title':'essential type에 부적합한 연산을 적용하지 않는다',
  'bad': r"""float f = 3.5f;
int mask = f & 0x0F;   /* 부동소수에 비트 연산 */""",
  'good': r"""uint32_t u = 0x35u;
uint32_t mask = u & 0x0Fu;""",
  'why':'부동소수에 비트 연산을 적용하는 등 essential type에 맞지 않는 연산은 의미가 없거나 정의되지 않는다. 연산은 적절한 타입 범주에만 적용한다.'},

 {'id':'Rule 10.3','cat':'Required · Decidable · Rule',
  'title':'더 좁거나 다른 essential type 범주로 대입하지 않는다',
  'bad': r"""int32_t big = 100000;
int16_t small = big;   /* 좁은 타입으로 잘림 */""",
  'good': r"""int32_t big = 100000;
int16_t small;
if (big >= INT16_MIN && big <= INT16_MAX) {
    small = (int16_t)big;
}""",
  'why':'더 좁은 타입으로의 암묵적 대입은 값 절단·정보 손실을 일으킨다. 범위 확인 후 명시적으로 변환한다.'},

 {'id':'Rule 10.4','cat':'Required · Decidable · Rule',
  'title':'이항 연산자의 두 피연산자는 같은 essential type 범주여야 한다',
  'bad': r"""uint32_t u = 10u;
int32_t  s = -1;
if (u > s) { /* 부호 혼합으로 의도와 다른 비교 */ }""",
  'good': r"""int32_t u = 10;
int32_t s = -1;
if (u > s) { /* 동일 범주 비교 */ }""",
  'why':'부호 있는 값과 없는 값을 섞어 비교하면 암묵 변환으로 예상과 다른 결과가 나온다. 피연산자의 타입 범주를 통일한다.'},

 {'id':'Rule 11.3','cat':'Required · Decidable · Rule',
  'title':'서로 다른 객체 포인터 타입 간 캐스트를 하지 않는다',
  'bad': r"""uint8_t bytes[4];
uint32_t *p = (uint32_t *)bytes;   /* 정렬·앨리어싱 위반 위험 */
*p = 0x12345678u;""",
  'good': r"""uint8_t bytes[4];
uint32_t v = 0x12345678u;
(void)memcpy(bytes, &v, sizeof(v));""",
  'why':'호환되지 않는 포인터 타입 간 캐스트는 정렬 위반·엄격 앨리어싱 위반을 일으킨다. 바이트 복사(memcpy)로 안전하게 처리한다.'},

 {'id':'Rule 11.8','cat':'Required · Decidable · Rule',
  'title':'캐스트로 const/volatile 한정자를 제거하지 않는다',
  'bad': r"""void clear(const char *s) {
    char *m = (char *)s;   /* const 제거 */
    m[0] = '\0';
}""",
  'good': r"""void clear(char *s) {
    s[0] = '\0';
}""",
  'why':'const/volatile를 캐스트로 떼어내고 객체를 수정하면 정의되지 않은 동작이 될 수 있다. 수정이 필요하면 한정자 없는 인자로 받는다.'},

 {'id':'Rule 12.1','cat':'Advisory · Decidable · Rule',
  'title':'연산자 우선순위가 모호하면 괄호로 의도를 명시한다',
  'bad': r"""int r = a + b << 2 & mask;   /* 우선순위 혼동 */""",
  'good': r"""int r = ((a + b) << 2) & mask;""",
  'why':'복합 표현식의 우선순위는 읽는 사람이 오해하기 쉽다. 괄호로 평가 순서를 명시해 의도를 분명히 한다.'},

 {'id':'Rule 13.2','cat':'Required · Undecidable · Rule',
  'title':'평가 순서나 부수효과 순서에 의존하지 않는다',
  'bad': r"""i = 0;
arr[i] = i++;   /* 같은 객체에 미정의 순서로 접근 */""",
  'good': r"""i = 0;
arr[i] = i;
i++;""",
  'why':'한 표현식 안에서 동일 객체를 수정·접근하면 평가 순서가 정의되지 않아 결과가 불확정이다. 부수효과를 분리한 문장으로 나눈다.'},

 {'id':'Rule 14.3','cat':'Required · Undecidable · Rule',
  'title':'제어식이 항상 불변(상수)이 되지 않게 한다',
  'bad': r"""uint8_t x = 5;
if (x < 256u) {   /* uint8_t는 항상 256 미만, 항상 참 */
    do_work();
}""",
  'good': r"""uint16_t x = read_sensor();
if (x < 256u) {
    do_work();
}""",
  'why':'항상 참/거짓인 제어식은 분기를 죽은 코드로 만들거나 논리 오류를 숨긴다. 실제로 분기 의미가 있는 조건만 사용한다.'},

 {'id':'Rule 14.4','cat':'Required · Decidable · Rule',
  'title':'if/while 제어식은 boolean 타입(본질)이어야 한다',
  'bad': r"""int n = get_count();
if (n) {   /* 정수를 조건으로 직접 사용 */
    process();
}""",
  'good': r"""int n = get_count();
if (n != 0) {
    process();
}""",
  'why':'정수·포인터를 조건식에 직접 쓰면 의도(0 비교인지 boolean인지)가 모호하다. 명시적 비교로 boolean 결과를 만든다.'},

 {'id':'Rule 15.5','cat':'Advisory · Decidable · Rule',
  'title':'함수는 끝에 단일 종료점을 두는 것을 권장한다',
  'bad': r"""int find(const int *a, int n, int key) {
    for (int i = 0; i < n; i++)
        if (a[i] == key) return i;   /* 다중 return */
    return -1;
}""",
  'good': r"""int find(const int *a, int n, int key) {
    int result = -1;
    for (int i = 0; i < n && result < 0; i++)
        if (a[i] == key) result = i;
    return result;
}""",
  'why':'함수 중간의 산재한 return은 자원 해제·후처리 누락을 부르기 쉽다. 단일 종료점을 두면 정리 코드를 한 곳에서 보장한다.'},

 {'id':'Rule 15.6','cat':'Required · Decidable · Rule',
  'title':'반복문·선택문의 본문은 항상 중괄호로 감싼다',
  'bad': r"""if (ready)
    start();
    log();   /* 들여쓰기 착시, log는 항상 실행 */""",
  'good': r"""if (ready) {
    start();
    log();
}""",
  'why':'중괄호 없는 본문은 나중에 문장을 추가할 때 분기 밖으로 새어나가 논리 오류를 만든다. 항상 블록으로 묶는다.'},

 {'id':'Rule 16.3','cat':'Required · Decidable · Rule',
  'title':'switch의 각 절은 무조건 break 등으로 종료한다',
  'bad': r"""switch (cmd) {
    case 1: open();   /* break 누락, fall-through */
    case 2: close(); break;
    default: break;
}""",
  'good': r"""switch (cmd) {
    case 1: open();  break;
    case 2: close(); break;
    default: break;
}""",
  'why':'의도치 않은 fall-through는 다음 절까지 실행되어 흔한 버그가 된다. 각 절을 break/return 등으로 명확히 종료한다.'},

 {'id':'Rule 16.4','cat':'Required · Decidable · Rule',
  'title':'모든 switch 문에는 default 절이 있어야 한다',
  'bad': r"""switch (state) {
    case S_IDLE: idle(); break;
    case S_RUN:  run();  break;
}   /* 예상 밖 값 처리 없음 */""",
  'good': r"""switch (state) {
    case S_IDLE: idle(); break;
    case S_RUN:  run();  break;
    default:     handle_error(); break;
}""",
  'why':'default가 없으면 예상치 못한 값이 조용히 무시되어 오류가 드러나지 않는다. default로 비정상 경로를 명시 처리한다.'},

 {'id':'Rule 17.7','cat':'Required · Decidable · Rule',
  'title':'void가 아닌 함수의 반환값을 사용한다',
  'bad': r"""scanf("%d", &n);   /* 읽기 성공 개수 무시 */""",
  'good': r"""if (scanf("%d", &n) == 1) {
    use(n);
}""",
  'why':'반환값을 버리면 함수가 알린 성공/실패 정보를 잃는다. 결과를 검사하거나 (의도적이면) void 캐스트로 명시한다.'},

 {'id':'Rule 18.1','cat':'Required · Undecidable · Rule',
  'title':'포인터 산술 결과는 같은 배열 범위 안을 가리켜야 한다',
  'bad': r"""int a[10];
int *p = &a[0];
int v = *(p + 12);   /* 배열 경계 밖 접근 */""",
  'good': r"""int a[10];
int *p = &a[0];
int idx = 12;
int v = (idx < 10) ? *(p + idx) : 0;""",
  'why':'배열 경계를 벗어난 포인터 역참조는 정의되지 않은 동작이다. 오프셋이 배열 크기 안에 있는지 확인한 뒤 접근한다.'},

 {'id':'Rule 18.4','cat':'Advisory · Decidable · Rule',
  'title':'포인터에 +/- 산술 연산을 사용하지 않는다(배열 첨자 선호)',
  'bad': r"""int *q = arr + 3;
*q = 7;   /* 포인터 가산 */""",
  'good': r"""arr[3] = 7;   /* 배열 첨자 사용 */""",
  'why':'포인터 가감 산술은 경계 추론을 어렵게 하고 실수를 유발한다. 의미가 분명한 배열 첨자 표기를 선호한다.'},

 {'id':'Rule 20.7','cat':'Required · Decidable · Rule',
  'title':'매크로 매개변수는 괄호로 감싼다',
  'bad': r"""#define SQ(x) x * x
int r = SQ(a + 1);   /* a + 1 * a + 1 로 전개 */""",
  'good': r"""#define SQ(x) ((x) * (x))
int r = SQ(a + 1);""",
  'why':'매크로 인자에 괄호가 없으면 전개 후 우선순위가 깨져 의도와 다른 식이 된다. 각 매개변수와 전체식을 괄호로 보호한다.'},

 {'id':'Rule 21.3','cat':'Required · Undecidable · Rule',
  'title':'동적 메모리 할당 함수(malloc/free 등)를 사용하지 않는다',
  'bad': r"""char *buf = malloc(64);
strcpy(buf, src);
free(buf);""",
  'good': r"""char buf[64];
(void)strncpy(buf, src, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';""",
  'why':'malloc/calloc/realloc/free는 누수·이중 해제·비결정적 동작을 유발한다. 고정 크기 정적 버퍼로 대체한다.'},

 {'id':'Rule 21.6','cat':'Required · Decidable · Rule',
  'title':'표준 입출력(stdio) 함수를 사용하지 않는다',
  'bad': r"""printf("status=%d\n", code);
gets(line);   /* 위험한 표준 입출력 */""",
  'good': r"""/* 검증된 사내 로깅·입력 계층 사용 */
log_status(code);
read_line_safe(line, sizeof(line));""",
  'why':'stdio 함수는 버퍼 관리·서식 처리에서 위험(gets 오버플로 등)을 안고 있다. 안전성을 보장하는 자체 입출력 계층으로 대체한다.'},

 {'id':'Rule 21.7','cat':'Required · Decidable · Rule',
  'title':'atoi/atol/atof/atoll 변환 함수를 사용하지 않는다',
  'bad': r"""int n = atoi(s);   /* 오류·오버플로 감지 불가 */""",
  'good': r"""char *end;
long v = strtol(s, &end, 10);
if (end != s && *end == '\0') {
    use((int)v);
}""",
  'why':'atoi 계열은 변환 실패와 범위 초과를 구분해 알리지 못한다. 오류 정보를 제공하는 strtol 계열을 사용한다.'},

 {'id':'Rule 21.8','cat':'Required · Decidable · Rule',
  'title':'system/abort/exit/getenv 등 환경 함수를 사용하지 않는다',
  'bad': r"""char *path = getenv("CFG");
system("cleanup.sh");
exit(1);""",
  'good': r"""const char *path = config_get_path();
run_cleanup_task();
set_error_flag(1);   /* 정상 흐름으로 종료 처리 */""",
  'why':'system은 명령 주입, getenv는 신뢰 불가 입력, abort/exit는 자원 정리 우회 위험이 있다. 통제된 사내 메커니즘으로 대체한다.'},

 {'id':'Rule 22.1','cat':'Required · Undecidable · Rule',
  'title':'획득한 자원은 사용 후 반드시 해제한다',
  'bad': r"""FILE *fp = fopen("a.txt", "r");
if (read_all(fp) < 0)
    return -1;   /* fp 누수 */
fclose(fp);
return 0;""",
  'good': r"""FILE *fp = fopen("a.txt", "r");
if (fp == NULL) return -1;
int rc = read_all(fp);
(void)fclose(fp);
return (rc < 0) ? -1 : 0;""",
  'why':'오류 경로에서 자원을 해제하지 않으면 누수가 누적된다. 모든 종료 경로에서 획득한 자원을 해제하도록 구조화한다.'},

 {'id':'Rule 8.9','cat':'Advisory · Decidable · Rule',
  'title':'한 함수 안에서만 쓰는 객체는 블록 범위로 선언한다',
  'bad': r"""static int g_tmp;   /* 한 함수에서만 사용 */
void f(void) {
    g_tmp = compute();
    use(g_tmp);
}""",
  'good': r"""void f(void) {
    int tmp = compute();
    use(tmp);
}""",
  'why':'한 함수에서만 쓰는 변수를 파일 범위에 두면 생명주기가 불필요하게 길어지고 재진입 안전성이 떨어진다. 가장 좁은 범위로 선언한다.'},

 {'id':'Rule 8.11','cat':'Advisory · Decidable · Rule',
  'title':'외부 연결 배열 선언에는 크기를 명시한다',
  'bad': r"""extern int table[];   /* 크기 불명, 경계 검사 불가 */""",
  'good': r"""extern int table[16];""",
  'why':'불완전한 배열 선언은 sizeof·경계 검사를 어렵게 만든다. 외부 배열도 크기를 명시해 정보를 보존한다.'},

 {'id':'Rule 13.5','cat':'Required · Undecidable · Rule',
  'title':'&&·||의 우측 피연산자에 부수효과를 두지 않는다',
  'bad': r"""if (ok && (count++ > 0)) {   /* 단락 평가로 count++ 누락 가능 */
    proc();
}""",
  'good': r"""count++;
if (ok && (count > 0)) {
    proc();
}""",
  'why':'단락 평가되는 우측 피연산자에 부수효과를 두면 좌측 결과에 따라 실행 여부가 달라져 버그가 된다. 부수효과를 분리한다.'},

 {'id':'Rule 17.8','cat':'Advisory · Decidable · Rule',
  'title':'함수 매개변수를 함수 본문에서 수정하지 않는다',
  'bad': r"""int sum_to(int n) {
    int s = 0;
    while (n > 0) { s += n; n--; }   /* 매개변수 n 변경 */
    return s;
}""",
  'good': r"""int sum_to(int n) {
    int s = 0;
    for (int i = n; i > 0; i--) s += i;
    return s;
}""",
  'why':'매개변수를 수정하면 원래 인자값을 추적하기 어려워져 디버깅·유지보수가 힘들다. 지역 변수에 복사해 사용한다.'},
]
