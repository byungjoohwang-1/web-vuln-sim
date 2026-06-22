# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트2: ARR·STR·MEM·FIO) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'ARR30-C','cat':'ARR · Rule · L1',
  'title':'배열 범위를 벗어난 포인터/첨자를 만들거나 사용하지 않는다',
  'bad': r"""int a[10];
int i = read_index();
a[i] = 0;            /* i 범위 미검증 */""",
  'good': r"""int a[10];
int i = read_index();
if (i >= 0 && i < 10) {
    a[i] = 0;
}""",
  'why':'범위를 벗어난 배열 접근은 메모리 손상·정보 유출·미정의 동작을 일으킨다. 인덱스를 0..size-1로 검증한 뒤 접근한다.'},

 {'id':'ARR32-C','cat':'ARR · Rule · L1',
  'title':'가변 길이 배열(VLA) 크기 인자가 유효 범위인지 보장한다',
  'bad': r"""void f(int n) {
    int buf[n];      /* n이 음수/과대면 미정의·스택 폭주 */
}""",
  'good': r"""void f(int n) {
    if (n <= 0 || n > 1024) { return; }
    int buf[n];
}""",
  'why':'VLA 크기가 음수이거나 지나치게 크면 미정의 동작이나 스택 고갈이 발생한다. 크기를 양수·상한 이내로 검증한다.'},

 {'id':'ARR36-C','cat':'ARR · Rule · L2',
  'title':'관련 없는 포인터를 빼거나 비교하지 않는다',
  'bad': r"""int x[4], y[4];
ptrdiff_t d = &x[3] - &y[0];   /* 다른 배열 — 미정의 */""",
  'good': r"""int x[4];
ptrdiff_t d = &x[3] - &x[0];""",
  'why':'서로 다른 배열에 속한 포인터의 뺄셈/비교 결과는 미정의다. 같은 배열의 원소들 사이에서만 연산한다.'},

 {'id':'ARR38-C','cat':'ARR · Rule · L1',
  'title':'라이브러리 함수가 무효한 포인터를 만들지 않도록 인자를 보장한다',
  'bad': r"""char d[8];
memcpy(d, s, len);   /* len > 8 이면 d 경계 초과 */""",
  'good': r"""char d[8];
if (len <= sizeof d) {
    memcpy(d, s, len);
}""",
  'why':'길이 인자가 버퍼 크기를 초과하면 memcpy 등이 경계를 넘는 무효 포인터로 쓰기를 수행한다. 호출 전에 길이가 버퍼 범위 내인지 확인한다.'},

 {'id':'ARR39-C','cat':'ARR · Rule · L1',
  'title':'스케일된 정수를 포인터에 더하거나 빼지 않는다',
  'bad': r"""int *p = a;
p = (int *)((char *)p + 1 * sizeof(int) * 2);  /* 수동 스케일 — 오류 유발 */""",
  'good': r"""int *p = a;
p = p + 2;          /* 요소 단위 산술 */""",
  'why':'바이트 단위로 직접 스케일한 포인터 산술은 이중 스케일·정렬 오류를 부른다. 요소 타입 단위의 포인터 산술을 사용한다.'},

 {'id':'ARR01-C','cat':'ARR · Rec · L2',
  'title':'배열 크기를 구할 때 포인터에 sizeof 를 적용하지 않는다',
  'bad': r"""void f(int a[]) {
    size_t n = sizeof(a) / sizeof(a[0]);   /* a는 포인터 — n 틀림 */
}""",
  'good': r"""void f(int *a, size_t n) {   /* 길이를 인자로 전달 */
    for (size_t i = 0; i < n; i++) { ... }
}""",
  'why':'함수 인자로 전달된 배열은 포인터로 붕괴하므로 sizeof로 요소 수를 구하면 틀린다. 요소 수를 별도 인자로 전달한다.'},

 {'id':'STR30-C','cat':'STR · Rule · L1',
  'title':'문자열 리터럴을 수정하려 하지 않는다',
  'bad': r"""char *s = "hello";
s[0] = 'H';          /* 리터럴 수정 — 미정의 */""",
  'good': r"""char s[] = "hello";   /* 수정 가능한 배열 복사본 */
s[0] = 'H';""",
  'why':'문자열 리터럴은 읽기 전용일 수 있어 수정 시 미정의 동작이다. 수정이 필요하면 배열로 복사해 다룬다.'},

 {'id':'STR31-C','cat':'STR · Rule · L1',
  'title':'문자열 저장 공간에 널 종료자 자리를 보장한다',
  'bad': r"""char d[8];
strcpy(d, "12345678");   /* 8자 + 널 = 9바이트 필요 */""",
  'good': r"""char d[9];
strncpy(d, src, sizeof d - 1);
d[sizeof d - 1] = '\0';""",
  'why':'널 종료자 공간을 빠뜨리면 한 바이트 오버플로우와 종료되지 않은 문자열이 생긴다. 버퍼에 내용+널 자리를 확보하고 명시적으로 종료한다.'},

 {'id':'STR32-C','cat':'STR · Rule · L1',
  'title':'널 종료되지 않은 문자 시퀀스를 문자열 인자로 넘기지 않는다',
  'bad': r"""char buf[4];
memcpy(buf, "abcd", 4);   /* 널 없음 */
size_t n = strlen(buf);   /* 경계 초과 읽기 */""",
  'good': r"""char buf[5];
memcpy(buf, "abcd", 4);
buf[4] = '\0';
size_t n = strlen(buf);""",
  'why':'널 종료가 없는 버퍼를 strlen/printf 등에 넘기면 메모리를 넘어 읽는다. 문자열 함수에 넘기기 전에 널 종료를 보장한다.'},

 {'id':'STR34-C','cat':'STR · Rule · L2',
  'title':'문자를 더 큰 정수로 변환하기 전에 unsigned char 로 캐스트한다',
  'bad': r"""char c = get();
int v = c;           /* 음수 char가 부호 확장 */""",
  'good': r"""char c = get();
int v = (unsigned char)c;   /* 0..255 로 해석 */""",
  'why':'부호 있는 char를 더 큰 정수로 바로 변환하면 음수가 부호 확장되어 의도치 않은 큰 값이 된다. unsigned char로 먼저 캐스트한다.'},

 {'id':'STR37-C','cat':'STR · Rule · L1',
  'title':'문자 처리 함수 인자는 unsigned char 로 표현 가능해야 한다',
  'bad': r"""char c = get();
if (isalpha(c)) { ... }   /* 음수면 미정의 */""",
  'good': r"""char c = get();
if (isalpha((unsigned char)c)) { ... }""",
  'why':'is*/to* 함수에 음수(EOF 외)를 넘기면 미정의 동작이다. unsigned char로 캐스트해 유효 범위를 보장한다.'},

 {'id':'STR38-C','cat':'STR · Rule · L1',
  'title':'좁은 문자열과 넓은 문자열/함수를 혼동하지 않는다',
  'bad': r"""wchar_t w[8];
strcpy((char *)w, "hi");   /* 넓은 버퍼에 좁은 복사 */""",
  'good': r"""wchar_t w[8];
wcscpy(w, L"hi");          /* 넓은 문자열 함수 */""",
  'why':'좁은/넓은 문자 함수를 섞으면 요소 크기 차이로 데이터가 손상된다. 문자 폭에 맞는 함수와 리터럴을 사용한다.'},

 {'id':'STR03-C','cat':'STR · Rec · L2',
  'title':'널 종료 문자열을 의도치 않게 잘라내지 않는다',
  'bad': r"""char d[8];
strncpy(d, src, sizeof d);   /* 정확히 8자면 널 없음 */""",
  'good': r"""char d[8];
strncpy(d, src, sizeof d - 1);
d[sizeof d - 1] = '\0';""",
  'why':'strncpy는 한도까지 채우면 널을 붙이지 않아 종료되지 않은 문자열이 남는다. 마지막 바이트를 널로 명시 설정한다.'},

 {'id':'MEM30-C','cat':'MEM · Rule · L1',
  'title':'해제된 메모리에 접근하지 않는다(use-after-free)',
  'bad': r"""free(p);
p->next = NULL;      /* 해제 후 접근 */""",
  'good': r"""free(p);
p = NULL;            /* 즉시 무효화 */""",
  'why':'해제된 메모리를 읽거나 쓰면 힙 손상·정보 유출·임의 코드 실행으로 이어질 수 있다. 해제 직후 포인터를 NULL로 무효화한다.'},

 {'id':'MEM31-C','cat':'MEM · Rule · L1',
  'title':'동적으로 할당된 메모리는 정확히 한 번만 해제한다',
  'bad': r"""free(p);
if (err) { free(p); }   /* 이중 해제 */""",
  'good': r"""free(p);
p = NULL;
if (err) { free(p); }   /* NULL free는 무해 */""",
  'why':'같은 메모리를 두 번 해제하면 힙 메타데이터가 손상되어 악용 가능한 취약점이 된다. 해제 후 NULL로 두어 이중 해제를 막는다.'},

 {'id':'MEM34-C','cat':'MEM · Rule · L1',
  'title':'동적으로 할당된 메모리만 해제한다',
  'bad': r"""char buf[32];
char *p = buf;
free(p);             /* 자동 객체 해제 — 미정의 */""",
  'good': r"""char *p = malloc(32);
if (p != NULL) {
    use(p);
    free(p);
}""",
  'why':'정적/자동 객체나 배열 중간 포인터를 free하면 힙 손상·미정의 동작이 된다. malloc 계열로 받은 시작 포인터만 해제한다.'},

 {'id':'MEM35-C','cat':'MEM · Rule · L2',
  'title':'객체에 충분한 메모리를 할당한다(곱셈 오버플로우 주의)',
  'bad': r"""int *a = malloc(n * sizeof(int));   /* n*size 오버플로우 가능 */""",
  'good': r"""if (n > SIZE_MAX / sizeof(int)) { return NULL; }
int *a = malloc(n * sizeof(int));""",
  'why':'요소 수×크기 계산이 오버플로우하면 실제보다 작은 버퍼가 할당되어 힙 오버플로우가 난다. 곱셈 전에 오버플로우를 검사한다.'},

 {'id':'MEM01-C','cat':'MEM · Rec · L2',
  'title':'free 직후 포인터에 새 값(NULL)을 즉시 저장한다',
  'bad': r"""free(node->data);
/* node->data 가 댕글링 상태로 남음 */""",
  'good': r"""free(node->data);
node->data = NULL;""",
  'why':'해제 후 그대로 둔 포인터는 댕글링 상태로 남아 후속 사용·이중 해제 위험이 된다. 해제 직후 NULL을 대입한다.'},

 {'id':'MEM04-C','cat':'MEM · Rec · L2',
  'title':'길이 0 할당에 주의한다',
  'bad': r"""char *p = malloc(len);   /* len==0 이면 NULL 또는 0바이트 — 역참조 위험 */
p[0] = 'x';""",
  'good': r"""if (len == 0) { return; }
char *p = malloc(len);
if (p != NULL) { p[0] = 'x'; }""",
  'why':'malloc(0)은 NULL이나 역참조 불가한 포인터를 반환할 수 있다. 0 길이를 별도 처리하고 반환값을 항상 검사한다.'},

 {'id':'MEM12-C','cat':'MEM · Rec · L3',
  'title':'다중 자원 정리는 goto 체인 등으로 누수 없이 처리한다',
  'bad': r"""FILE *f = fopen(p, "r");
char *buf = malloc(n);
if (!buf) { return -1; }   /* f 누수 */""",
  'good': r"""FILE *f = fopen(p, "r");
if (!f) { return -1; }
char *buf = malloc(n);
if (!buf) { fclose(f); return -1; }
...
free(buf); fclose(f); return 0;""",
  'why':'중간 실패 시 앞서 획득한 자원을 해제하지 않으면 누수가 쌓인다. 역순 정리(goto 체인 등)로 모든 경로에서 해제를 보장한다.'},

 {'id':'FIO30-C','cat':'FIO · Rule · L1',
  'title':'사용자 입력을 포맷 문자열에 직접 사용하지 않는다',
  'bad': r"""printf(user_input);   /* 포맷 문자열 인젝션 */""",
  'good': r"""printf("%s", user_input);""",
  'why':'사용자 입력을 포맷 문자열로 쓰면 %n/%s 등으로 메모리 읽기·쓰기 공격이 가능하다. 항상 고정 포맷("%s")에 인자로 전달한다.'},

 {'id':'FIO34-C','cat':'FIO · Rule · L1',
  'title':'입력 문자와 EOF/WEOF 를 구분한다',
  'bad': r"""char c;
while ((c = getchar()) != EOF) { ... }   /* char로 받으면 EOF 구분 실패 */""",
  'good': r"""int c;
while ((c = getchar()) != EOF) { ... }""",
  'why':'getchar 반환을 char에 담으면 0xFF 문자와 EOF가 구분되지 않아 루프가 잘못 종료·무한 반복한다. 반환값은 int로 받는다.'},

 {'id':'FIO37-C','cat':'FIO · Rule · L2',
  'title':'fgets/fgetws 성공 시 비어있지 않은 결과를 가정하지 않는다',
  'bad': r"""fgets(line, sizeof line, f);
line[strlen(line) - 1] = '\0';   /* 빈 줄이면 인덱스 -1 */""",
  'good': r"""if (fgets(line, sizeof line, f) != NULL) {
    size_t n = strlen(line);
    if (n > 0 && line[n-1] == '\n') { line[n-1] = '\0'; }
}""",
  'why':'성공한 fgets라도 내용이 비어 있을 수 있어 strlen-1 같은 접근이 경계를 벗어난다. 길이를 확인하고 안전하게 인덱싱한다.'},

 {'id':'FIO42-C','cat':'FIO · Rule · L2',
  'title':'더 이상 필요 없는 파일은 닫는다',
  'bad': r"""FILE *f = fopen(p, "r");
read_all(f);
return;              /* fclose 누락 — 핸들 누수 */""",
  'good': r"""FILE *f = fopen(p, "r");
if (!f) { return; }
read_all(f);
fclose(f);""",
  'why':'열린 파일을 닫지 않으면 디스크립터 누수로 결국 자원이 고갈된다. 사용이 끝나면 모든 경로에서 fclose한다.'},

 {'id':'FIO45-C','cat':'FIO · Rule · L3',
  'title':'파일 접근에서 TOCTOU 경쟁 조건을 피한다',
  'bad': r"""if (access(path, W_OK) == 0) {   /* 검사 */
    FILE *f = fopen(path, "w");  /* 사용 — 사이에 교체 가능 */
}""",
  'good': r"""int fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
if (fd >= 0) { FILE *f = fdopen(fd, "w"); }""",
  'why':'access 후 fopen 사이에 파일이 심볼릭 링크 등으로 교체되면 권한 우회가 일어난다(TOCTOU). 검사-사용을 원자적 open 플래그로 결합한다.'},

 {'id':'FIO47-C','cat':'FIO · Rule · L1',
  'title':'유효한 포맷 문자열을 사용한다(인자와 변환 지정자 일치)',
  'bad': r"""long v = 10;
printf("%d\n", v);   /* %d 에 long — 불일치 */""",
  'good': r"""long v = 10;
printf("%ld\n", v);""",
  'why':'변환 지정자와 인자 타입이 어긋나면 잘못된 크기로 읽어 미정의 동작·정보 유출이 된다. 지정자와 인자 타입을 정확히 맞춘다.'},

 {'id':'FIO02-C','cat':'FIO · Rec · L2',
  'title':'경로 이름을 정규화(canonicalize)한 뒤 사용한다',
  'bad': r"""char path[256];
sprintf(path, "/data/%s", user);   /* ../ 포함 시 경로 이탈 */
FILE *f = fopen(path, "r");""",
  'good': r"""char resolved[PATH_MAX];
if (realpath(joined, resolved) && starts_with(resolved, "/data/")) {
    FILE *f = fopen(resolved, "r");
}""",
  'why':'정규화하지 않은 경로는 ../ 를 통한 디렉터리 이탈에 악용된다. realpath로 정규화하고 허용된 기준 디렉터리 내인지 확인한다.'},
]
