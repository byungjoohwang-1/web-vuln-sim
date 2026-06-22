# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트3: ENV·SIG·ERR·CON·MSC·POS·WIN) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'ENV30-C','cat':'ENV · Rule · L1',
  'title':'getenv 가 반환한 객체를 수정하지 않는다',
  'bad': r"""char *home = getenv("HOME");
home[0] = '/';       /* 반환 문자열 직접 수정 — 미정의 */""",
  'good': r"""const char *home = getenv("HOME");
char copy[256];
if (home) { strncpy(copy, home, sizeof copy - 1); copy[sizeof copy - 1] = '\0'; }""",
  'why':'getenv가 가리키는 문자열을 수정하면 미정의 동작이며 환경이 손상될 수 있다. 복사본을 만들어 수정한다.'},

 {'id':'ENV31-C','cat':'ENV · Rule · L2',
  'title':'환경을 무효화할 수 있는 연산 후의 환경 포인터를 신뢰하지 않는다',
  'bad': r"""char *p = getenv("PATH");
setenv("PATH", "/x", 1);
use(p);              /* setenv 이후 p 무효 가능 */""",
  'good': r"""char buf[512];
char *p = getenv("PATH");
if (p) { strncpy(buf, p, sizeof buf - 1); buf[sizeof buf - 1] = '\0'; }
setenv("PATH", "/x", 1);
use(buf);""",
  'why':'setenv/putenv 등은 이전에 받은 환경 포인터를 무효화할 수 있다. 변경 전에 필요한 값을 복사해 둔다.'},

 {'id':'ENV33-C','cat':'ENV · Rule · L1',
  'title':'system() 을 호출하지 않는다',
  'bad': r"""char cmd[128];
sprintf(cmd, "ls %s", dir);
system(cmd);         /* 셸 인젝션 */""",
  'good': r"""char *const argv[] = { "/bin/ls", dir, NULL };
posix_spawn(&pid, "/bin/ls", NULL, NULL, argv, environ);""",
  'why':'system은 셸을 거쳐 명령을 실행하므로 입력에 메타문자가 섞이면 임의 명령이 실행된다. 셸을 거치지 않는 exec/posix_spawn으로 인자를 분리 전달한다.'},

 {'id':'ENV34-C','cat':'ENV · Rule · L2',
  'title':'특정 함수가 반환한 포인터를 보관해 재사용하지 않는다',
  'bad': r"""char *a = setlocale(LC_ALL, "C");
setlocale(LC_ALL, "en_US.UTF-8");
use(a);              /* a 가 가리키던 내용 덮어쓰임 */""",
  'good': r"""char saved[64];
char *a = setlocale(LC_ALL, NULL);
if (a) { strncpy(saved, a, sizeof saved - 1); saved[sizeof saved - 1] = '\0'; }""",
  'why':'getenv/setlocale/strerror 등이 반환한 포인터는 다음 호출에서 덮어써질 수 있다. 값을 즉시 복사해 보관한다.'},

 {'id':'SIG30-C','cat':'SIG · Rule · L1',
  'title':'시그널 핸들러에서는 비동기-안전(async-signal-safe) 함수만 호출한다',
  'bad': r"""void handler(int s) {
    printf("caught %d\n", s);   /* printf는 async-safe 아님 */
}""",
  'good': r"""volatile sig_atomic_t flag = 0;
void handler(int s) { flag = 1; }   /* 플래그만 설정 */""",
  'why':'핸들러에서 malloc/printf 등 비동기-안전하지 않은 함수를 부르면 교착·재진입 손상이 생긴다. 플래그 설정 등 async-safe 작업만 한다.'},

 {'id':'SIG31-C','cat':'SIG · Rule · L1',
  'title':'시그널 핸들러에서 공유 객체를 안전하지 않게 접근하지 않는다',
  'bad': r"""int counter;
void handler(int s) { counter++; }   /* 비원자 접근 */""",
  'good': r"""volatile sig_atomic_t got = 0;
void handler(int s) { got = 1; }""",
  'why':'핸들러가 일반 변수를 갱신하면 메인 흐름과의 경쟁으로 값이 손상된다. volatile sig_atomic_t 또는 원자 타입만 공유한다.'},

 {'id':'SIG34-C','cat':'SIG · Rule · L2',
  'title':'인터럽트 가능한 시그널 핸들러 내부에서 signal() 을 호출하지 않는다',
  'bad': r"""void handler(int s) {
    signal(s, handler);   /* 핸들러 안에서 재설정 — 경쟁 */
}""",
  'good': r"""struct sigaction sa = {0};
sa.sa_handler = handler;
sigaction(SIGTERM, &sa, NULL);   /* 지속적 처리를 미리 설정 */""",
  'why':'핸들러 안의 signal() 재설정은 경쟁 구간을 만들어 시그널을 놓칠 수 있다. sigaction으로 영속적 처리를 미리 설정한다.'},

 {'id':'ERR30-C','cat':'ERR · Rule · L2',
  'title':'errno 기반 함수는 호출 전 errno=0, 호출 후 검사한다',
  'bad': r"""long v = strtol(s, NULL, 10);
if (errno) { ... }   /* 이전 errno 잔존 가능 */""",
  'good': r"""errno = 0;
long v = strtol(s, NULL, 10);
if (errno != 0) { handle_error(); }""",
  'why':'호출 전에 errno를 0으로 두지 않으면 이전 오류를 현재 오류로 오인한다. 호출 직전 0으로 설정하고 직후에 검사한다.'},

 {'id':'ERR32-C','cat':'ERR · Rule · L2',
  'title':'errno 의 불확정 값에 의존하지 않는다',
  'bad': r"""double d = atof(s);
if (errno) { ... }   /* atof는 errno를 설정하지 않음 */""",
  'good': r"""errno = 0;
char *end;
double d = strtod(s, &end);
if (end == s || errno != 0) { handle_error(); }""",
  'why':'errno를 설정하지 않는 함수(atof 등) 뒤에 errno를 검사하면 무관한 값을 본다. errno를 설정하도록 명세된 함수와 함께 사용한다.'},

 {'id':'ERR33-C','cat':'ERR · Rule · L2',
  'title':'표준 라이브러리 함수의 오류를 검출하고 처리한다',
  'bad': r"""FILE *f = fopen(p, "r");
fread(buf, 1, n, f);   /* fopen 실패·부분 읽기 미검사 */""",
  'good': r"""FILE *f = fopen(p, "r");
if (!f) { return -1; }
size_t r = fread(buf, 1, n, f);
if (r < n && ferror(f)) { fclose(f); return -1; }""",
  'why':'라이브러리 함수의 실패 표시(NULL·반환값·ferror)를 무시하면 잘못된 상태로 진행한다. 명세된 오류 표시를 검사해 처리한다.'},

 {'id':'ERR34-C','cat':'ERR · Rule · L3',
  'title':'문자열을 숫자로 변환할 때 오류를 검출한다',
  'bad': r"""int n = atoi(s);     /* 실패·범위 초과 구분 불가 */""",
  'good': r"""errno = 0;
char *end;
long v = strtol(s, &end, 10);
if (end == s || *end != '\0' || errno == ERANGE) { handle_error(); }""",
  'why':'atoi는 변환 실패와 정상 0을 구분하지 못한다. strtol과 end 포인터·errno로 변환 성공 여부를 명확히 판정한다.'},

 {'id':'CON31-C','cat':'CON · Rule · L2',
  'title':'잠긴 뮤텍스를 파괴하지 않는다',
  'bad': r"""pthread_mutex_lock(&m);
pthread_mutex_destroy(&m);   /* 잠긴 상태로 파괴 — 미정의 */""",
  'good': r"""pthread_mutex_lock(&m);
work();
pthread_mutex_unlock(&m);
pthread_mutex_destroy(&m);""",
  'why':'잠긴 뮤텍스를 파괴하면 미정의 동작과 교착이 발생한다. 파괴 전에 반드시 잠금을 해제한다.'},

 {'id':'CON33-C','cat':'CON · Rule · L2',
  'title':'라이브러리 함수 사용 시 경쟁 조건을 피한다',
  'bad': r"""char *t = strtok(buf, ",");   /* strtok 는 내부 상태 공유 — 스레드 비안전 */""",
  'good': r"""char *save;
char *t = strtok_r(buf, ",", &save);   /* 재진입 버전 */""",
  'why':'strtok/rand/asctime 등 내부 정적 상태를 쓰는 함수는 멀티스레드에서 경쟁한다. 재진입(_r) 또는 스레드-안전 변형을 쓴다.'},

 {'id':'CON35-C','cat':'CON · Rule · L2',
  'title':'정해진 순서로 잠가 교착(deadlock)을 방지한다',
  'bad': r"""/* T1: lock(A); lock(B)  /  T2: lock(B); lock(A)  → 교착 */
lock(&B); lock(&A);""",
  'good': r"""/* 모든 스레드가 동일 순서로 잠금 */
lock(&A); lock(&B);
... unlock(&B); unlock(&A);""",
  'why':'스레드마다 잠금 순서가 다르면 서로의 잠금을 기다리는 교착이 생긴다. 전역적으로 일관된 잠금 순서를 정한다.'},

 {'id':'CON36-C','cat':'CON · Rule · L2',
  'title':'조건 변수 대기는 루프로 감싼다',
  'bad': r"""if (!ready) {
    pthread_cond_wait(&cv, &m);   /* 가짜 깨어남 처리 못함 */
}""",
  'good': r"""while (!ready) {
    pthread_cond_wait(&cv, &m);
}""",
  'why':'조건 변수는 가짜 깨어남(spurious wakeup)이 발생할 수 있어 if로는 조건이 거짓인데 진행한다. while 루프로 조건을 재확인한다.'},

 {'id':'CON40-C','cat':'CON · Rule · L2',
  'title':'한 표현식에서 원자 변수를 두 번 참조하지 않는다',
  'bad': r"""atomic_int a;
a = a + 1;           /* 읽기+쓰기 두 번 — 원자성 깨짐 */""",
  'good': r"""atomic_int a;
atomic_fetch_add(&a, 1);   /* 단일 원자 연산 */""",
  'why':'원자 변수를 같은 식에서 읽고 다시 쓰면 두 연산 사이에 경쟁이 생겨 원자성이 깨진다. 원자 RMW 연산을 사용한다.'},

 {'id':'CON43-C','cat':'CON · Rule · L2',
  'title':'멀티스레드에서 데이터 경쟁(data race)을 허용하지 않는다',
  'bad': r"""int shared;
void *t(void *p) { shared++; return NULL; }   /* 보호 없는 공유 */""",
  'good': r"""int shared;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
void *t(void *p) { pthread_mutex_lock(&m); shared++; pthread_mutex_unlock(&m); return NULL; }""",
  'why':'동기화 없이 공유 변수를 여러 스레드가 갱신하면 데이터 경쟁으로 결과가 미정의가 된다. 뮤텍스나 원자 연산으로 보호한다.'},

 {'id':'MSC30-C','cat':'MSC · Rule · L3',
  'title':'보안 목적에 rand() 를 사용하지 않는다',
  'bad': r"""int token = rand();   /* 예측 가능한 의사난수 */""",
  'good': r"""unsigned char token[16];
arc4random_buf(token, sizeof token);   /* 또는 OS CSPRNG */""",
  'why':'rand()는 예측 가능해 토큰·키·논스 등 보안 요소에 부적합하다. OS의 암호학적 난수(CSPRNG)를 사용한다.'},

 {'id':'MSC32-C','cat':'MSC · Rule · L3',
  'title':'의사난수 생성기를 적절히 시드(seed)한다',
  'bad': r"""srand(1);             /* 고정 시드 — 매 실행 동일 수열 */
int r = rand();""",
  'good': r"""srand((unsigned)time(NULL) ^ (unsigned)getpid());
int r = rand();   /* 비보안 용도에 한해 */""",
  'why':'고정 시드는 매 실행마다 같은 수열을 만들어 예측 가능하다. 비보안 용도라도 변하는 값으로 시드하고, 보안 용도는 CSPRNG를 쓴다.'},

 {'id':'MSC33-C','cat':'MSC · Rule · L2',
  'title':'asctime() 에 유효하지 않은 데이터를 넘기지 않는다',
  'bad': r"""struct tm t = parse(input);
char *s = asctime(&t);   /* 범위 밖 필드면 버퍼 오버플로우 */""",
  'good': r"""struct tm t = parse(input);
char buf[64];
strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S", &t);""",
  'why':'asctime은 tm 필드가 범위를 벗어나면 내부 고정 버퍼를 넘쳐 손상된다. 경계가 안전한 strftime을 사용한다.'},

 {'id':'MSC37-C','cat':'MSC · Rule · L1',
  'title':'비void 함수의 끝에 제어가 도달하지 않도록 한다',
  'bad': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
}                          /* x==0 시 반환 없음 */""",
  'good': r"""int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}""",
  'why':'반환 없이 끝나는 비void 함수의 반환값은 불확정이라 호출부가 쓰레기값을 쓴다. 모든 경로에서 값을 반환한다.'},

 {'id':'MSC41-C','cat':'MSC · Rule · L1',
  'title':'민감 정보를 소스에 하드코딩하지 않는다',
  'bad': r"""const char *db_pass = "P@ssw0rd!";   /* 소스에 비밀번호 노출 */""",
  'good': r"""const char *db_pass = read_secret_from_secure_store();""",
  'why':'소스에 박힌 비밀번호·키는 바이너리·저장소를 통해 유출된다. 비밀은 보안 저장소·환경에서 런타임에 로드한다.'},

 {'id':'MSC12-C','cat':'MSC · Rec · L2',
  'title':'죽은(dead) 코드를 검출하고 제거한다',
  'bad': r"""int v = compute();
return v;
log("unreached");    /* 도달 불가 */""",
  'good': r"""int v = compute();
log("computed");
return v;""",
  'why':'도달 불가·효과 없는 코드는 논리 오류의 신호이며 유지보수를 방해한다. 죽은 코드는 제거하거나 흐름을 바로잡는다.'},

 {'id':'MSC17-C','cat':'MSC · Rec · L2',
  'title':'모든 switch 절을 break 로 마무리한다',
  'bad': r"""switch (c) {
    case 1: a();      /* break 누락 — fall-through */
    case 2: b(); break;
}""",
  'good': r"""switch (c) {
    case 1: a(); break;
    case 2: b(); break;
    default: break;
}""",
  'why':'break 누락은 의도치 않은 다음 절 실행을 유발한다. 각 절을 break/return으로 명시 종료한다(의도적 fall-through는 주석으로 표시).'},

 {'id':'MSC21-C','cat':'MSC · Rec · L2',
  'title':'견고한 루프 종료 조건을 사용한다',
  'bad': r"""for (size_t i = n; i >= 0; i--) { ... }   /* unsigned는 항상 >=0 — 무한 */""",
  'good': r"""for (size_t i = n; i-- > 0; ) { ... }""",
  'why':'부호 없는 카운터에 >=0 종료 조건을 쓰면 영원히 참이라 무한 루프가 된다. 타입 특성을 고려한 안전한 종료 조건을 쓴다.'},

 {'id':'POS34-C','cat':'POS · Rule · L1',
  'title':'putenv() 에 자동(지역) 변수를 넘기지 않는다',
  'bad': r"""void set(void) {
    char buf[32];
    sprintf(buf, "K=%d", v);
    putenv(buf);     /* 함수 종료 후 환경이 무효 메모리 가리킴 */
}""",
  'good': r"""setenv("K", value_str, 1);   /* 내부 복사본 사용 */""",
  'why':'putenv는 넘긴 메모리를 그대로 참조하므로, 지역 버퍼를 넘기면 함수 종료 후 환경이 무효 메모리를 가리킨다. 복사하는 setenv를 쓴다.'},

 {'id':'POS35-C','cat':'POS · Rule · L2',
  'title':'심볼릭 링크 확인 시 경쟁 조건을 피한다',
  'bad': r"""if (lstat(p, &st) == 0 && !S_ISLNK(st.st_mode)) {
    int fd = open(p, O_RDONLY);   /* 사이에 링크로 교체 가능 */
}""",
  'good': r"""int fd = open(p, O_RDONLY | O_NOFOLLOW);
if (fd >= 0) { ... }""",
  'why':'lstat 검사와 open 사이에 경로가 심볼릭 링크로 교체되면 의도치 않은 파일이 열린다. O_NOFOLLOW로 원자적으로 링크를 거부한다.'},

 {'id':'POS54-C','cat':'POS · Rule · L1',
  'title':'POSIX 라이브러리 함수의 오류를 검출하고 처리한다',
  'bad': r"""int fd = open(p, O_RDONLY);
read(fd, buf, n);    /* open 실패(-1)·read 오류 미검사 */""",
  'good': r"""int fd = open(p, O_RDONLY);
if (fd < 0) { return -1; }
ssize_t r = read(fd, buf, n);
if (r < 0) { close(fd); return -1; }""",
  'why':'POSIX 함수의 -1/errno 반환을 무시하면 실패 상태로 계속 진행해 손상이 누적된다. 반환값을 검사하고 errno로 처리한다.'},

 {'id':'WIN30-C','cat':'WIN · Rule · L1',
  'title':'할당과 해제 함수를 올바르게 짝지어 사용한다',
  'bad': r"""char *p = (char *)malloc(32);
HeapFree(GetProcessHeap(), 0, p);   /* malloc/HeapFree 불일치 */""",
  'good': r"""char *p = (char *)malloc(32);
free(p);            /* 같은 할당기로 해제 */""",
  'why':'서로 다른 할당기로 할당·해제하면 힙 손상이 발생한다. malloc↔free, HeapAlloc↔HeapFree처럼 동일 계열로 짝지어 사용한다.'},

 {'id':'CON39-C','cat':'CON · Rule · L2',
  'title':'이미 join/detach 한 스레드를 다시 join/detach 하지 않는다',
  'bad': r"""pthread_join(t, NULL);
pthread_join(t, NULL);   /* 이미 join된 스레드 재join — 미정의 */""",
  'good': r"""if (!joined) {
    pthread_join(t, NULL);
    joined = 1;
}""",
  'why':'이미 회수된 스레드 핸들을 다시 join/detach하면 미정의 동작이다. 상태를 추적해 한 번만 수행한다.'},

 {'id':'MSC40-C','cat':'MSC · Rule · L2',
  'title':'언어 제약(constraints)을 위반하지 않는다',
  'bad': r"""inline int f(void) {
    static int s = 0;   /* 외부 inline 정의에서 내부 정적 변경 — 제약 위반 */
    return ++s;
}""",
  'good': r"""static int f(void) {
    static int s = 0;
    return ++s;
}""",
  'why':'표준이 정의한 제약을 어기면 진단 가능하지만 이식성·동작이 깨질 수 있다. inline·정적 저장소 규칙 등 언어 제약을 준수한다.'},
]
