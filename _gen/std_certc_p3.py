# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트3: ENV·SIG·ERR·CON·MSC·POS·WIN) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 표준 인용, 코드·해설은 자체 작성(규범 원문 비복제).
모든 bad/good 는 self-contained 컴파일 가능 C 프로그램(int main 포함).
검증: `-std=gnu11 -lm -pthread` (Wandbox gcc-13.2.0). POSIX/pthread/stdatomic 사용.
WIN30/MSC40 은 Windows·언어제약 개념을 리눅스에서 컴파일되는 동등 예시로 재구성(주석/why 에 매핑 설명)."""

RULES = [
 {'id':'ENV30-C','cat':'ENV · Rule · L1','compiles':True,
  'title':'getenv 가 반환한 객체를 수정하지 않는다',
  'title_en':'Do not modify the object referenced by the return value of getenv',
  'bad': r"""#include <stdlib.h>
int main(void){
    char *home = getenv("HOME");
    if (home) home[0] = '/';   /* getenv 결과를 직접 수정 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <string.h>
int main(void){
    const char *home = getenv("HOME");
    char copy[256] = "";
    if (home) { strncpy(copy, home, sizeof copy - 1); copy[sizeof copy - 1] = '\0'; }
    if (copy[0]) copy[0] = '/';   /* 복사본을 수정 */
    return 0;
}""",
  'why':'getenv가 가리키는 문자열을 수정하면 미정의 동작이며 환경이 손상될 수 있다. 복사본을 만들어 수정한다.',
  'why_en':'Modifying the string returned by getenv is undefined behavior and may corrupt the environment. Copy it first and modify the copy.'},

 {'id':'ENV31-C','cat':'ENV · Rule · L2','compiles':True,
  'title':'환경을 무효화할 수 있는 연산 후의 환경 포인터를 신뢰하지 않는다',
  'title_en':'Do not rely on an environment pointer following an operation that may invalidate it',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    char *p = getenv("PATH");
    setenv("PATH", "/tmp", 1);   /* p 를 무효화할 수 있음 */
    if (p) printf("%s\n", p);     /* p 가 댕글링일 수 있음 */
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
#include <string.h>
int main(void){
    char buf[512] = "";
    char *p = getenv("PATH");
    if (p) { strncpy(buf, p, sizeof buf - 1); buf[sizeof buf - 1] = '\0'; }
    setenv("PATH", "/tmp", 1);
    printf("%s\n", buf);           /* 변경 전 복사해 둔 값 사용 */
    return 0;
}""",
  'why':'setenv/putenv 등은 이전에 받은 환경 포인터를 무효화할 수 있다. 변경 전에 필요한 값을 복사해 둔다.',
  'why_en':'setenv/putenv can invalidate a previously obtained environment pointer. Copy any needed value before modifying the environment.'},

 {'id':'ENV33-C','cat':'ENV · Rule · L1','compiles':True,
  'title':'system() 을 호출하지 않는다',
  'title_en':'Do not call system()',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    const char *dir = "/tmp";
    char cmd[128];
    snprintf(cmd, sizeof cmd, "ls %s", dir);
    system(cmd);   /* 셸을 거침 — 입력에 메타문자가 섞이면 명령 주입 */
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <spawn.h>
#include <unistd.h>
#include <sys/wait.h>
extern char **environ;
int main(void){
    const char *dir = "/tmp";
    char *const argv[] = { "/bin/ls", (char *)dir, NULL };
    pid_t pid;
    if (posix_spawn(&pid, "/bin/ls", NULL, NULL, argv, environ) == 0)
        waitpid(pid, NULL, 0);   /* 셸을 거치지 않고 인자 분리 전달 */
    return 0;
}""",
  'why':'system은 셸을 거쳐 명령을 실행하므로 입력에 메타문자가 섞이면 임의 명령이 실행된다. 셸을 거치지 않는 exec/posix_spawn으로 인자를 분리 전달한다.',
  'why_en':'system runs commands through a shell, so embedded metacharacters can execute arbitrary commands. Use exec/posix_spawn to pass arguments separately without a shell.'},

 {'id':'ENV34-C','cat':'ENV · Rule · L2','compiles':True,
  'title':'특정 함수가 반환한 포인터를 보관해 재사용하지 않는다',
  'title_en':'Do not store pointers returned by certain functions for later reuse',
  'bad': r"""#include <locale.h>
#include <stdio.h>
int main(void){
    char *a = setlocale(LC_ALL, "C");
    setlocale(LC_ALL, "POSIX");   /* a 가 가리키던 내용이 덮어써질 수 있음 */
    if (a) printf("%s\n", a);
    return 0;
}""",
  'good': r"""#include <locale.h>
#include <string.h>
#include <stdio.h>
int main(void){
    char saved[64] = "";
    char *a = setlocale(LC_ALL, NULL);
    if (a) { strncpy(saved, a, sizeof saved - 1); saved[sizeof saved - 1] = '\0'; }
    setlocale(LC_ALL, "POSIX");
    printf("%s\n", saved);   /* 즉시 복사해 보관한 값 사용 */
    return 0;
}""",
  'why':'getenv/setlocale/strerror 등이 반환한 포인터는 다음 호출에서 덮어써질 수 있다. 값을 즉시 복사해 보관한다.',
  'why_en':'Pointers returned by getenv/setlocale/strerror may be overwritten by a subsequent call. Copy the value immediately if you need to retain it.'},

 {'id':'SIG30-C','cat':'SIG · Rule · L1','compiles':True,
  'title':'시그널 핸들러에서는 비동기-안전(async-signal-safe) 함수만 호출한다',
  'title_en':'Call only asynchronous-safe functions within signal handlers',
  'bad': r"""#include <signal.h>
#include <stdio.h>
void handler(int s){ printf("caught %d\n", s); }   /* printf 는 async-signal-safe 아님 */
int main(void){ signal(SIGTERM, handler); return 0; }""",
  'good': r"""#include <signal.h>
volatile sig_atomic_t flag = 0;
void handler(int s){ (void)s; flag = 1; }   /* 플래그만 설정 */
int main(void){ signal(SIGTERM, handler); return (int)flag; }""",
  'why':'핸들러에서 malloc/printf 등 비동기-안전하지 않은 함수를 부르면 교착·재진입 손상이 생긴다. 플래그 설정 등 async-safe 작업만 한다.',
  'why_en':'Calling non-async-signal-safe functions (malloc/printf) in a handler can deadlock or corrupt reentrant state. Do only async-safe work, such as setting a flag.'},

 {'id':'SIG31-C','cat':'SIG · Rule · L1','compiles':True,
  'title':'시그널 핸들러에서 공유 객체를 안전하지 않게 접근하지 않는다',
  'title_en':'Do not access shared objects in signal handlers in an unsafe manner',
  'bad': r"""#include <signal.h>
int counter;
void handler(int s){ (void)s; counter++; }   /* 비원자 공유 접근 */
int main(void){ signal(SIGINT, handler); return counter; }""",
  'good': r"""#include <signal.h>
volatile sig_atomic_t got = 0;
void handler(int s){ (void)s; got = 1; }   /* sig_atomic_t 만 공유 */
int main(void){ signal(SIGINT, handler); return (int)got; }""",
  'why':'핸들러가 일반 변수를 갱신하면 메인 흐름과의 경쟁으로 값이 손상된다. volatile sig_atomic_t 또는 원자 타입만 공유한다.',
  'why_en':'Updating an ordinary variable in a handler races with the main flow and corrupts it. Share only volatile sig_atomic_t or atomic types.'},

 {'id':'SIG34-C','cat':'SIG · Rule · L2','compiles':True,
  'title':'인터럽트 가능한 시그널 핸들러 내부에서 signal() 을 호출하지 않는다',
  'title_en':'Do not call signal() from within interruptible signal handlers',
  'bad': r"""#include <signal.h>
void handler(int s){ signal(s, handler); }   /* 핸들러 안에서 재설정 — 경쟁 구간 */
int main(void){ signal(SIGTERM, handler); return 0; }""",
  'good': r"""#include <signal.h>
#include <string.h>
void handler(int s){ (void)s; }
int main(void){
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = handler;
    sigaction(SIGTERM, &sa, NULL);   /* 지속적 처리를 미리 설정 */
    return 0;
}""",
  'why':'핸들러 안의 signal() 재설정은 경쟁 구간을 만들어 시그널을 놓칠 수 있다. sigaction으로 영속적 처리를 미리 설정한다.',
  'why_en':'Re-arming with signal() inside a handler creates a race window where a signal can be lost. Establish a persistent disposition up front with sigaction.'},

 {'id':'ERR30-C','cat':'ERR · Rule · L2','compiles':True,
  'title':'errno 기반 함수는 호출 전 errno=0, 호출 후 검사한다',
  'title_en':'Set errno to zero before, and check it after, calling errno-setting functions',
  'bad': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    long v = strtol("123", NULL, 10);
    if (errno) printf("error\n");   /* 이전 errno 잔존 가능 — 오인 */
    return (int)v;
}""",
  'good': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    errno = 0;
    long v = strtol("123", NULL, 10);
    if (errno != 0) { printf("error\n"); return -1; }
    return (int)v;
}""",
  'why':'호출 전에 errno를 0으로 두지 않으면 이전 오류를 현재 오류로 오인한다. 호출 직전 0으로 설정하고 직후에 검사한다.',
  'why_en':'If errno is not cleared before the call, a stale error is mistaken for a current one. Set it to zero immediately before and check immediately after.'},

 {'id':'ERR32-C','cat':'ERR · Rule · L2','compiles':True,
  'title':'errno 의 불확정 값에 의존하지 않는다',
  'title_en':'Do not rely on indeterminate values of errno',
  'bad': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    double d = atof("abc");        /* atof 는 errno 를 설정하지 않음 */
    if (errno) printf("error\n");  /* 무관한 errno 값을 봄 */
    return (int)d;
}""",
  'good': r"""#include <stdlib.h>
#include <errno.h>
#include <stdio.h>
int main(void){
    char s[] = "3.14";
    errno = 0;
    char *end;
    double d = strtod(s, &end);
    if (end == s || errno != 0) { printf("error\n"); return -1; }
    return (int)d;
}""",
  'why':'errno를 설정하지 않는 함수(atof 등) 뒤에 errno를 검사하면 무관한 값을 본다. errno를 설정하도록 명세된 함수와 함께 사용한다.',
  'why_en':'Checking errno after a function that does not set it (e.g., atof) reads an unrelated value. Use functions specified to set errno (e.g., strtod).'},

 {'id':'ERR33-C','cat':'ERR · Rule · L2','compiles':True,
  'title':'표준 라이브러리 함수의 오류를 검출하고 처리한다',
  'title_en':'Detect and handle standard library errors',
  'bad': r"""#include <stdio.h>
int main(void){
    char buf[64];
    FILE *f = fopen("/nonexistent_xyz123", "r");
    fread(buf, 1, sizeof buf, f);   /* fopen 실패·부분 읽기 미검사 */
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    char buf[64];
    FILE *f = fopen("/etc/hostname", "r");
    if (!f) return -1;
    size_t r = fread(buf, 1, sizeof buf, f);
    if (r < sizeof buf && ferror(f)) { fclose(f); return -1; }
    fclose(f);
    return 0;
}""",
  'why':'라이브러리 함수의 실패 표시(NULL·반환값·ferror)를 무시하면 잘못된 상태로 진행한다. 명세된 오류 표시를 검사해 처리한다.',
  'why_en':'Ignoring a library function’s failure indication (NULL, return value, ferror) proceeds in a bad state. Check the specified error indicator and handle it.'},

 {'id':'ERR34-C','cat':'ERR · Rule · L3','compiles':True,
  'title':'문자열을 숫자로 변환할 때 오류를 검출한다',
  'title_en':'Detect errors when converting a string to a number',
  'bad': r"""#include <stdlib.h>
int main(void){
    int n = atoi("abc");   /* 변환 실패와 정상 0 을 구분 못함 */
    return n;
}""",
  'good': r"""#include <stdlib.h>
#include <errno.h>
int main(void){
    char s[] = "42";
    errno = 0;
    char *end;
    long v = strtol(s, &end, 10);
    if (end == s || *end != '\0' || errno == ERANGE) return -1;
    return (int)v;
}""",
  'why':'atoi는 변환 실패와 정상 0을 구분하지 못한다. strtol과 end 포인터·errno로 변환 성공 여부를 명확히 판정한다.',
  'why_en':'atoi cannot distinguish a failed conversion from a valid 0. Use strtol with the end pointer and errno to determine success unambiguously.'},

 {'id':'CON31-C','cat':'CON · Rule · L2','compiles':True,
  'title':'잠긴 뮤텍스를 파괴하지 않는다',
  'title_en':'Do not destroy a mutex while it is locked',
  'bad': r"""#include <pthread.h>
int main(void){
    pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_lock(&m);
    pthread_mutex_destroy(&m);   /* 잠긴 상태로 파괴 — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <pthread.h>
int main(void){
    pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
    pthread_mutex_lock(&m);
    /* critical section */
    pthread_mutex_unlock(&m);
    pthread_mutex_destroy(&m);   /* 해제 후 파괴 */
    return 0;
}""",
  'why':'잠긴 뮤텍스를 파괴하면 미정의 동작과 교착이 발생한다. 파괴 전에 반드시 잠금을 해제한다.',
  'why_en':'Destroying a locked mutex is undefined behavior and can deadlock. Always unlock before destroying.'},

 {'id':'CON33-C','cat':'CON · Rule · L2','compiles':True,
  'title':'라이브러리 함수 사용 시 경쟁 조건을 피한다',
  'title_en':'Avoid race conditions when using library functions',
  'bad': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char buf[] = "a,b,c";
    char *t = strtok(buf, ",");   /* 내부 정적 상태 공유 — 멀티스레드 비안전 */
    while (t) { printf("%s\n", t); t = strtok(NULL, ","); }
    return 0;
}""",
  'good': r"""#include <string.h>
#include <stdio.h>
int main(void){
    char buf[] = "a,b,c";
    char *save;
    char *t = strtok_r(buf, ",", &save);   /* 재진입(_r) 버전 */
    while (t) { printf("%s\n", t); t = strtok_r(NULL, ",", &save); }
    return 0;
}""",
  'why':'strtok/rand/asctime 등 내부 정적 상태를 쓰는 함수는 멀티스레드에서 경쟁한다. 재진입(_r) 또는 스레드-안전 변형을 쓴다.',
  'why_en':'Functions with internal static state (strtok/rand/asctime) race across threads. Use reentrant (_r) or thread-safe variants.'},

 {'id':'CON35-C','cat':'CON · Rule · L2','compiles':True,
  'title':'정해진 순서로 잠가 교착(deadlock)을 방지한다',
  'title_en':'Lock in a predefined order to avoid deadlock',
  'bad': r"""#include <pthread.h>
pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER, B = PTHREAD_MUTEX_INITIALIZER;
void *t2(void *p){ (void)p;
    pthread_mutex_lock(&B); pthread_mutex_lock(&A);   /* 반대 순서 — 교착 위험 */
    pthread_mutex_unlock(&A); pthread_mutex_unlock(&B); return NULL; }
int main(void){
    pthread_mutex_lock(&A); pthread_mutex_lock(&B);
    pthread_mutex_unlock(&B); pthread_mutex_unlock(&A);
    return 0;
}""",
  'good': r"""#include <pthread.h>
pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER, B = PTHREAD_MUTEX_INITIALIZER;
void *t2(void *p){ (void)p;
    pthread_mutex_lock(&A); pthread_mutex_lock(&B);   /* 모든 스레드 동일 순서 */
    pthread_mutex_unlock(&B); pthread_mutex_unlock(&A); return NULL; }
int main(void){
    pthread_mutex_lock(&A); pthread_mutex_lock(&B);
    pthread_mutex_unlock(&B); pthread_mutex_unlock(&A);
    return 0;
}""",
  'why':'스레드마다 잠금 순서가 다르면 서로의 잠금을 기다리는 교착이 생긴다. 전역적으로 일관된 잠금 순서를 정한다.',
  'why_en':'Different lock orders across threads cause a deadlock where each waits on the other’s lock. Define a globally consistent lock ordering.'},

 {'id':'CON36-C','cat':'CON · Rule · L2','compiles':True,
  'title':'조건 변수 대기는 루프로 감싼다',
  'title_en':'Wrap condition-variable waits in a loop',
  'bad': r"""#include <pthread.h>
int ready = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
void *w(void *p){ (void)p; pthread_mutex_lock(&m); ready = 1;
    pthread_cond_signal(&cv); pthread_mutex_unlock(&m); return NULL; }
int main(void){
    pthread_t th; pthread_create(&th, NULL, w, NULL);
    pthread_mutex_lock(&m);
    if (!ready) pthread_cond_wait(&cv, &m);   /* if — 가짜 깨어남 처리 못함 */
    pthread_mutex_unlock(&m);
    pthread_join(th, NULL);
    return 0;
}""",
  'good': r"""#include <pthread.h>
int ready = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
void *w(void *p){ (void)p; pthread_mutex_lock(&m); ready = 1;
    pthread_cond_signal(&cv); pthread_mutex_unlock(&m); return NULL; }
int main(void){
    pthread_t th; pthread_create(&th, NULL, w, NULL);
    pthread_mutex_lock(&m);
    while (!ready) pthread_cond_wait(&cv, &m);   /* while — 조건 재확인 */
    pthread_mutex_unlock(&m);
    pthread_join(th, NULL);
    return 0;
}""",
  'why':'조건 변수는 가짜 깨어남(spurious wakeup)이 발생할 수 있어 if로는 조건이 거짓인데 진행한다. while 루프로 조건을 재확인한다.',
  'why_en':'Condition variables can wake spuriously, so an if lets execution proceed while the predicate is still false. Re-check the predicate in a while loop.'},

 {'id':'CON40-C','cat':'CON · Rule · L2','compiles':True,
  'title':'한 표현식에서 원자 변수를 두 번 참조하지 않는다',
  'title_en':'Do not refer to an atomic variable twice in an expression',
  'bad': r"""#include <stdatomic.h>
int main(void){
    atomic_int a = 0;
    a = a + 1;   /* 읽기+쓰기 두 연산 — 사이에 경쟁, 원자성 깨짐 */
    return atomic_load(&a);
}""",
  'good': r"""#include <stdatomic.h>
int main(void){
    atomic_int a = 0;
    atomic_fetch_add(&a, 1);   /* 단일 원자 RMW 연산 */
    return atomic_load(&a);
}""",
  'why':'원자 변수를 같은 식에서 읽고 다시 쓰면 두 연산 사이에 경쟁이 생겨 원자성이 깨진다. 원자 RMW 연산을 사용한다.',
  'why_en':'Reading then writing an atomic variable in the same expression opens a race between the two operations. Use an atomic read-modify-write operation.'},

 {'id':'CON43-C','cat':'CON · Rule · L2','compiles':True,
  'title':'멀티스레드에서 데이터 경쟁(data race)을 허용하지 않는다',
  'title_en':'Do not allow data races in multithreaded code',
  'bad': r"""#include <pthread.h>
int shared = 0;
void *t(void *p){ (void)p; for (int i = 0; i < 100000; i++) shared++; return NULL; }
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t, NULL); pthread_create(&b, NULL, t, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return shared & 0x7f;   /* 보호 없는 공유 갱신 — 데이터 경쟁 */
}""",
  'good': r"""#include <pthread.h>
int shared = 0;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
void *t(void *p){ (void)p;
    for (int i = 0; i < 100000; i++){ pthread_mutex_lock(&m); shared++; pthread_mutex_unlock(&m); }
    return NULL; }
int main(void){
    pthread_t a, b;
    pthread_create(&a, NULL, t, NULL); pthread_create(&b, NULL, t, NULL);
    pthread_join(a, NULL); pthread_join(b, NULL);
    return shared & 0x7f;
}""",
  'why':'동기화 없이 공유 변수를 여러 스레드가 갱신하면 데이터 경쟁으로 결과가 미정의가 된다. 뮤텍스나 원자 연산으로 보호한다.',
  'why_en':'Updating a shared variable from multiple threads without synchronization is a data race with undefined results. Protect it with a mutex or atomics.'},

 {'id':'MSC30-C','cat':'MSC · Rule · L3','compiles':True,
  'title':'보안 목적에 rand() 를 사용하지 않는다',
  'title_en':'Do not use rand() for security purposes',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    int token = rand();   /* 예측 가능한 의사난수 — 토큰/키에 부적합 */
    printf("%d\n", token);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    unsigned char token[16];
    FILE *f = fopen("/dev/urandom", "rb");   /* OS 암호학적 난수(CSPRNG) */
    if (!f || fread(token, 1, sizeof token, f) != sizeof token) { if (f) fclose(f); return -1; }
    fclose(f);
    printf("%02x\n", token[0]);
    return 0;
}""",
  'why':'rand()는 예측 가능해 토큰·키·논스 등 보안 요소에 부적합하다. OS의 암호학적 난수(CSPRNG)를 사용한다.',
  'why_en':'rand() is predictable and unfit for tokens, keys, or nonces. Use the OS cryptographically secure RNG (CSPRNG), e.g., /dev/urandom.'},

 {'id':'MSC32-C','cat':'MSC · Rule · L3','compiles':True,
  'title':'의사난수 생성기를 적절히 시드(seed)한다',
  'title_en':'Properly seed pseudorandom number generators',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    srand(1);   /* 고정 시드 — 매 실행 동일 수열 */
    printf("%d\n", rand());
    return 0;
}""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
int main(void){
    srand((unsigned)time(NULL) ^ (unsigned)getpid());   /* 비보안 용도에 한해 */
    printf("%d\n", rand());
    return 0;
}""",
  'why':'고정 시드는 매 실행마다 같은 수열을 만들어 예측 가능하다. 비보안 용도라도 변하는 값으로 시드하고, 보안 용도는 CSPRNG를 쓴다.',
  'why_en':'A fixed seed yields the same sequence every run and is predictable. Seed with a varying value for non-security use; use a CSPRNG for security.'},

 {'id':'MSC33-C','cat':'MSC · Rule · L2','compiles':True,
  'title':'asctime() 에 유효하지 않은 데이터를 넘기지 않는다',
  'title_en':'Do not pass invalid data to asctime()',
  'bad': r"""#include <time.h>
#include <stdio.h>
int main(void){
    struct tm t = {0};
    t.tm_mon = 13;             /* 범위를 벗어난 필드 */
    char *s = asctime(&t);     /* 내부 고정 버퍼 오버플로우 가능 */
    printf("%s", s);
    return 0;
}""",
  'good': r"""#include <time.h>
#include <stdio.h>
int main(void){
    struct tm t = {0};
    t.tm_year = 124; t.tm_mon = 5; t.tm_mday = 23;
    char buf[64];
    strftime(buf, sizeof buf, "%Y-%m-%d %H:%M:%S", &t);   /* 경계가 안전 */
    printf("%s\n", buf);
    return 0;
}""",
  'why':'asctime은 tm 필드가 범위를 벗어나면 내부 고정 버퍼를 넘쳐 손상된다. 경계가 안전한 strftime을 사용한다.',
  'why_en':'asctime can overflow its fixed internal buffer when tm fields are out of range. Use the bounded strftime instead.'},

 {'id':'MSC37-C','cat':'MSC · Rule · L1','compiles':True,
  'title':'비void 함수의 끝에 제어가 도달하지 않도록 한다',
  'title_en':'Ensure that control never reaches the end of a non-void function',
  'bad': r"""#include <stdio.h>
int sign(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
}   /* x==0 일 때 반환 없음 — 불확정 반환값 */
int main(void){ printf("%d\n", sign(0)); return 0; }""",
  'good': r"""#include <stdio.h>
int sign(int x){
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;   /* 모든 경로에서 반환 */
}
int main(void){ printf("%d\n", sign(0)); return 0; }""",
  'why':'반환 없이 끝나는 비void 함수의 반환값은 불확정이라 호출부가 쓰레기값을 쓴다. 모든 경로에서 값을 반환한다.',
  'why_en':'A non-void function that falls off the end returns an indeterminate value the caller then uses. Return a value on every path.'},

 {'id':'MSC41-C','cat':'MSC · Rule · L1','compiles':True,
  'title':'민감 정보를 소스에 하드코딩하지 않는다',
  'title_en':'Never hard code sensitive information',
  'bad': r"""#include <stdio.h>
int main(void){
    const char *db_pass = "P@ssw0rd!";   /* 소스에 비밀번호 노출 */
    printf("connecting...\n");
    return db_pass[0] ? 0 : 1;
}""",
  'good': r"""#include <stdio.h>
#include <stdlib.h>
int main(void){
    const char *db_pass = getenv("DB_PASS");   /* 런타임에 외부에서 로드 */
    if (!db_pass) { fprintf(stderr, "secret not provided\n"); return 1; }
    printf("connecting...\n");
    return 0;
}""",
  'why':'소스에 박힌 비밀번호·키는 바이너리·저장소를 통해 유출된다. 비밀은 보안 저장소·환경에서 런타임에 로드한다.',
  'why_en':'Passwords and keys embedded in source leak through the binary and the repository. Load secrets at runtime from a secure store or environment.'},

 {'id':'MSC12-C','cat':'MSC · Rec · L2','compiles':True,
  'title':'죽은(dead) 코드를 검출하고 제거한다',
  'title_en':'Detect and remove code that has no effect or is never executed',
  'bad': r"""#include <stdio.h>
int compute(void){ return 42; }
int demo(void){
    int v = compute();
    return v;
    printf("unreached\n");   /* 도달 불가 — 죽은 코드 */
}
int main(void){ return demo() & 1; }""",
  'good': r"""#include <stdio.h>
int compute(void){ return 42; }
int demo(void){
    int v = compute();
    printf("computed %d\n", v);
    return v;
}
int main(void){ return demo() & 1; }""",
  'why':'도달 불가·효과 없는 코드는 논리 오류의 신호이며 유지보수를 방해한다. 죽은 코드는 제거하거나 흐름을 바로잡는다.',
  'why_en':'Unreachable or no-effect code signals a logic error and hampers maintenance. Remove dead code or fix the control flow.'},

 {'id':'MSC17-C','cat':'MSC · Rec · L2','compiles':True,
  'title':'모든 switch 절을 break 로 마무리한다',
  'title_en':'Finish every nonempty switch clause with break',
  'bad': r"""#include <stdio.h>
int main(void){
    int c = 1;
    switch (c) {
        case 1: printf("one\n");   /* break 누락 — fall-through */
        case 2: printf("two\n"); break;
    }
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    int c = 1;
    switch (c) {
        case 1: printf("one\n"); break;
        case 2: printf("two\n"); break;
        default: break;
    }
    return 0;
}""",
  'why':'break 누락은 의도치 않은 다음 절 실행을 유발한다. 각 절을 break/return으로 명시 종료한다(의도적 fall-through는 주석으로 표시).',
  'why_en':'A missing break causes unintended fall-through to the next clause. End each clause with break/return (mark intentional fall-through with a comment).'},

 {'id':'MSC21-C','cat':'MSC · Rec · L2','compiles':True,
  'title':'견고한 루프 종료 조건을 사용한다',
  'title_en':'Use robust loop termination conditions',
  'bad': r"""#include <stddef.h>
#include <stdio.h>
int main(void){
    size_t n = 3;
    for (size_t i = n; i >= 0; i--)   /* size_t 는 항상 >=0 — 무한 루프 */
        printf("%zu\n", i);
    return 0;
}""",
  'good': r"""#include <stddef.h>
#include <stdio.h>
int main(void){
    size_t n = 3;
    for (size_t i = n; i-- > 0; )   /* 부호 없는 타입에 안전한 종료 */
        printf("%zu\n", i);
    return 0;
}""",
  'why':'부호 없는 카운터에 >=0 종료 조건을 쓰면 영원히 참이라 무한 루프가 된다. 타입 특성을 고려한 안전한 종료 조건을 쓴다.',
  'why_en':'An unsigned counter with a >=0 termination test is always true, creating an infinite loop. Use a termination condition that accounts for the type.'},

 {'id':'POS34-C','cat':'POS · Rule · L1','compiles':True,
  'title':'putenv() 에 자동(지역) 변수를 넘기지 않는다',
  'title_en':'Do not call putenv() with a pointer to an automatic variable as the argument',
  'bad': r"""#include <stdlib.h>
#include <stdio.h>
void set_var(int v){
    char buf[32];
    snprintf(buf, sizeof buf, "K=%d", v);
    putenv(buf);   /* putenv 는 이 포인터를 보관 — 함수 종료 후 무효 메모리 */
}
int main(void){ set_var(7); return 0; }""",
  'good': r"""#include <stdlib.h>
#include <stdio.h>
int main(void){
    char val[16];
    snprintf(val, sizeof val, "%d", 7);
    setenv("K", val, 1);   /* setenv 는 값을 복사함 */
    return 0;
}""",
  'why':'putenv는 넘긴 메모리를 그대로 참조하므로, 지역 버퍼를 넘기면 함수 종료 후 환경이 무효 메모리를 가리킨다. 복사하는 setenv를 쓴다.',
  'why_en':'putenv retains the pointer it is given, so passing a local buffer leaves the environment pointing at invalid memory after the function returns. Use setenv, which copies.'},

 {'id':'POS35-C','cat':'POS · Rule · L2','compiles':True,
  'title':'심볼릭 링크 확인 시 경쟁 조건을 피한다',
  'title_en':'Avoid race conditions while checking for the existence of a symbolic link',
  'bad': r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
int main(void){
    const char *p = "/tmp/cert_demo_file";
    struct stat st;
    if (lstat(p, &st) == 0 && !S_ISLNK(st.st_mode)) {
        int fd = open(p, O_RDONLY);   /* 검사와 open 사이에 링크로 교체 가능(TOCTOU) */
        if (fd >= 0) close(fd);
    }
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
int main(void){
    const char *p = "/tmp/cert_demo_file";
    int fd = open(p, O_RDONLY | O_NOFOLLOW);   /* 링크면 원자적으로 거부 */
    if (fd >= 0) close(fd);
    return 0;
}""",
  'why':'lstat 검사와 open 사이에 경로가 심볼릭 링크로 교체되면 의도치 않은 파일이 열린다. O_NOFOLLOW로 원자적으로 링크를 거부한다.',
  'why_en':'If the path is swapped to a symlink between the lstat check and the open, an unintended file is opened. Use O_NOFOLLOW to refuse symlinks atomically.'},

 {'id':'POS54-C','cat':'POS · Rule · L1','compiles':True,
  'title':'POSIX 라이브러리 함수의 오류를 검출하고 처리한다',
  'title_en':'Detect and handle POSIX library errors',
  'bad': r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
int main(void){
    char buf[64];
    int fd = open("/nonexistent_xyz123", O_RDONLY);
    read(fd, buf, sizeof buf);   /* open 실패(-1)·read 오류 미검사 */
    return 0;
}""",
  'good': r"""#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
int main(void){
    char buf[64];
    int fd = open("/etc/hostname", O_RDONLY);
    if (fd < 0) return -1;
    ssize_t r = read(fd, buf, sizeof buf);
    if (r < 0) { close(fd); return -1; }
    close(fd);
    return 0;
}""",
  'why':'POSIX 함수의 -1/errno 반환을 무시하면 실패 상태로 계속 진행해 손상이 누적된다. 반환값을 검사하고 errno로 처리한다.',
  'why_en':'Ignoring a POSIX function’s -1/errno return proceeds in a failed state and accumulates damage. Check the return value and handle errno.'},

 {'id':'WIN30-C','cat':'WIN · Rule · L1','compiles':True,
  'title':'할당과 해제 함수를 올바르게 짝지어 사용한다',
  'title_en':'Properly pair allocation and deallocation functions',
  'bad': r"""#include <stdlib.h>
int main(void){
    char *p = (char *)malloc(32);
    if (!p) return 1;
    free(p + 1);   /* malloc 이 돌려준 포인터가 아님 — 힙 손상 (Win: malloc/HeapFree 불일치와 동일) */
    return 0;
}""",
  'good': r"""#include <stdlib.h>
int main(void){
    char *p = (char *)malloc(32);
    if (!p) return 1;
    free(p);   /* 같은 할당기가 돌려준 정확한 포인터로 해제 */
    return 0;
}""",
  'why':'서로 다른 할당기로 할당·해제하거나 잘못된 포인터를 해제하면 힙이 손상된다. malloc↔free, (Windows) HeapAlloc↔HeapFree처럼 동일 계열·정확한 포인터로 짝지어 사용한다.',
  'why_en':'Freeing with a mismatched allocator or a wrong pointer corrupts the heap. Pair them correctly with the exact pointer: malloc/free, and on Windows HeapAlloc/HeapFree.'},

 {'id':'CON39-C','cat':'CON · Rule · L2','compiles':True,
  'title':'이미 join/detach 한 스레드를 다시 join/detach 하지 않는다',
  'title_en':'Do not join or detach a thread that was previously joined or detached',
  'bad': r"""#include <pthread.h>
void *worker(void *p){ (void)p; return NULL; }
int main(void){
    pthread_t t;
    pthread_create(&t, NULL, worker, NULL);
    pthread_join(t, NULL);
    pthread_join(t, NULL);   /* 이미 join 된 스레드 재join — 미정의 동작 */
    return 0;
}""",
  'good': r"""#include <pthread.h>
void *worker(void *p){ (void)p; return NULL; }
int main(void){
    pthread_t t;
    pthread_create(&t, NULL, worker, NULL);
    int joined = 0;
    if (!joined) { pthread_join(t, NULL); joined = 1; }   /* 한 번만 회수 */
    (void)joined;
    return 0;
}""",
  'why':'이미 회수된 스레드 핸들을 다시 join/detach하면 미정의 동작이다. 상태를 추적해 한 번만 수행한다.',
  'why_en':'Joining or detaching an already-reaped thread handle is undefined behavior. Track the state and do it exactly once.'},

 {'id':'MSC40-C','cat':'MSC · Rule · L2','compiles':True,
  'title':'언어 제약(constraints)을 위반하지 않는다',
  'title_en':'Do not violate constraints',
  'bad': r"""#include <stdio.h>
int main(void){
    int *p = "text";   /* 호환되지 않는 포인터 타입으로 초기화 — 제약 위반 */
    printf("%p\n", (void *)p);
    return 0;
}""",
  'good': r"""#include <stdio.h>
int main(void){
    const char *p = "text";   /* 타입을 일치 */
    printf("%s\n", p);
    return 0;
}""",
  'why':'표준이 정의한 제약(호환되지 않는 타입 대입 등)을 어기면 진단 가능하지만 이식성·동작이 깨질 수 있다. 타입 규칙 등 언어 제약을 준수한다.',
  'why_en':'Violating a Standard constraint (e.g., assigning incompatible pointer types) is diagnosable but breaks portability and behavior. Honor language constraints such as type rules.'},
]
