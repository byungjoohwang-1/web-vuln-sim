# -*- coding: utf-8 -*-
"""SEI CERT C 규칙 (파트4: 공식 사이트 대조로 보강한 누락 규칙) — 위반/준수 예제, 사내 교육용·자체작성.
규칙 ID/분류는 cmu-sei.github.io 공식 목록 대조로 확인, 코드·해설은 자체 작성(규범 원문 비복제)."""

RULES = [
 {'id':'DCL36-C','cat':'DCL · Rule · L2',
  'title':'충돌하는 링크(linkage) 분류로 식별자를 선언하지 않는다',
  'bad': r"""// a.c
static int shared;      // 내부 링크
// b.c
extern int shared;      // 외부 링크 — 충돌""",
  'good': r"""// shared.h
extern int shared;
// shared.c
int shared;             // 일관된 외부 링크""",
  'why':'같은 식별자를 내부/외부 링크로 모순되게 선언하면 미정의 동작이 된다. 링크 분류를 일관되게 유지한다.'},

 {'id':'EXP35-C','cat':'EXP · Rule · L1',
  'title':'임시(temporary) 수명 객체를 수정하거나 그 수명 밖에서 접근하지 않는다',
  'bad': r"""struct S { int a[4]; };
struct S f(void);
int* p = f().a;         // 임시의 멤버 주소
*p = 1;                 // 임시 소멸 후 접근 — 미정의""",
  'good': r"""struct S s = f();       // 임시를 객체에 보관
s.a[0] = 1;""",
  'why':'함수가 반환한 임시 객체는 표현식 끝에서 소멸하므로 그 내부 주소를 보관·수정하면 미정의 동작이다. 값을 지속 객체에 복사해 다룬다.'},

 {'id':'EXP42-C','cat':'EXP · Rule · L2',
  'title':'구조체를 통째로 비교해 패딩 데이터까지 비교하지 않는다',
  'bad': r"""struct P { char c; int v; };
if (memcmp(&a, &b, sizeof a) == 0) { ... }  // 패딩 바이트도 비교""",
  'good': r"""if (a.c == b.c && a.v == b.v) { ... }      // 멤버별 비교""",
  'why':'memcmp는 멤버 사이의 불확정 패딩 바이트까지 비교해 논리적으로 같은 구조체를 다르다고 판정할 수 있다. 멤버별로 비교한다.'},

 {'id':'EXP43-C','cat':'EXP · Rule · L2',
  'title':'restrict 한정 포인터로 미정의 동작을 일으키지 않는다',
  'bad': r"""void f(int *restrict a, int *restrict b);
f(buf, buf);            // 별칭 없음 약속 위반""",
  'good': r"""void f(int *a, int *b);  // restrict 미사용
f(buf, buf);""",
  'why':'restrict는 별칭이 없다는 약속이며, 실제로 겹치는 포인터를 넘기면 진단 없는 미정의 동작이 된다. 별칭 가능성이 있으면 restrict를 쓰지 않는다.'},

 {'id':'INT36-C','cat':'INT · Rule · L1',
  'title':'포인터와 정수를 변환할 때 주의한다',
  'bad': r"""unsigned int n = (unsigned int)ptr;   // 포인터가 더 넓으면 절단""",
  'good': r"""#include <stdint.h>
uintptr_t n = (uintptr_t)ptr;         // 포인터 보관 가능한 타입""",
  'why':'포인터를 너무 좁은 정수로 변환하면 상위 비트가 잘려 복원 시 잘못된 주소가 된다. 변환이 필요하면 uintptr_t/intptr_t를 사용한다.'},

 {'id':'ARR37-C','cat':'ARR · Rule · L1',
  'title':'배열이 아닌 객체를 가리키는 포인터에 정수를 더하거나 빼지 않는다',
  'bad': r"""struct P { int x, y; };
struct P p;
int* q = &p.x + 1;      // 단일 멤버 포인터 산술 — 미정의""",
  'good': r"""struct P p;
int* q = &p.y;          // 실제 멤버 주소 사용""",
  'why':'단일 객체(비배열) 포인터에 산술을 하면 그 객체 범위를 벗어나 미정의 동작이 된다. 구조체 멤버는 직접 접근한다.'},

 {'id':'FLP36-C','cat':'FLP · Rule · L2',
  'title':'정수를 부동소수로 변환할 때 정밀도 손실에 주의한다',
  'bad': r"""long big = 16777217L;   // 2^24+1
float f = big;          // float 정밀도 초과 — 값 변형""",
  'good': r"""long big = 16777217L;
double d = (double)big;  // 더 넓은 정밀도 사용""",
  'why':'큰 정수를 정밀도가 부족한 부동소수형으로 변환하면 가장 가까운 표현값으로 반올림되어 값이 변한다. 충분한 정밀도의 타입을 사용한다.'},

 {'id':'FLP37-C','cat':'FLP · Rule · L2',
  'title':'부동소수 객체의 비트 표현으로 동등성을 비교하지 않는다',
  'bad': r"""if (memcmp(&x, &y, sizeof x) == 0) { ... }  // +0.0/-0.0, NaN 처리 어긋남""",
  'good': r"""if (x == y) { ... }     // 값 비교(또는 허용오차 비교)""",
  'why':'부동소수는 +0.0/-0.0, NaN 등으로 같은 값이 다른 비트 표현을 가질 수 있어 memcmp 비교는 틀린다. 값 비교 연산을 사용한다.'},

 {'id':'MEM33-C','cat':'MEM · Rule · L2',
  'title':'유연 배열 멤버를 가진 구조체는 동적으로 할당·복사한다',
  'bad': r"""struct Buf { size_t n; char d[]; };
struct Buf b;           // 유연 배열 멤버를 자동 객체로 — 공간 없음
b.d[0] = 'x';""",
  'good': r"""struct Buf *b = malloc(sizeof *b + len);
if (b) { b->n = len; b->d[0] = 'x'; }""",
  'why':'유연 배열 멤버는 동적 할당으로만 실제 공간을 확보할 수 있다. 자동/정적 객체로 선언하면 멤버 영역이 없어 손상이 난다.'},

 {'id':'MEM36-C','cat':'MEM · Rule · L2',
  'title':'realloc 로 객체의 정렬(alignment)을 변경하지 않는다',
  'bad': r"""void* p = aligned_alloc(64, 64);
p = realloc(p, 128);    // 정렬 보장 사라짐""",
  'good': r"""void* q = aligned_alloc(64, 128);
memcpy(q, p, 64); free(p);   // 정렬 유지하며 재할당""",
  'why':'realloc은 기본 정렬만 보장하므로 과도 정렬 객체에 쓰면 정렬이 깨진다. 정렬이 필요하면 정렬 할당+복사로 처리한다.'},

 {'id':'FIO32-C','cat':'FIO · Rule · L2',
  'title':'장치 특수 파일(device file)에 일반 파일 연산을 가정하지 않는다',
  'bad': r"""FILE* f = fopen(user_path, "r");   // /dev/* 일 수 있음
read_all(f);            // 블로킹·예기치 않은 동작""",
  'good': r"""struct stat st;
if (stat(path, &st) == 0 && S_ISREG(st.st_mode)) {
    FILE* f = fopen(path, "r");
}""",
  'why':'사용자 경로가 장치 파일을 가리키면 일반 파일 가정이 깨져 블로킹·DoS가 일어난다. 일반 파일인지 확인 후 연다.'},

 {'id':'FIO38-C','cat':'FIO · Rule · L1',
  'title':'FILE 객체를 복사하지 않는다',
  'bad': r"""FILE f2 = *stdin;       // FILE 객체 값 복사 — 미정의
fread(buf, 1, n, &f2);""",
  'good': r"""FILE* f = stdin;        // 포인터만 사용
fread(buf, 1, n, f);""",
  'why':'FILE 객체를 값으로 복사하면 내부 상태가 어긋나 미정의 동작이 된다. 항상 FILE 포인터로만 다룬다.'},

 {'id':'FIO39-C','cat':'FIO · Rule · L1',
  'title':'위치 지정 없이 입력과 출력을 번갈아 하지 않는다',
  'bad': r"""fprintf(f, "a");
fscanf(f, "%d", &x);    // 위치 지정 없이 출력→입력 — 미정의""",
  'good': r"""fprintf(f, "a");
fflush(f); fseek(f, 0, SEEK_SET);
fscanf(f, "%d", &x);""",
  'why':'갱신 모드 스트림에서 위치 지정/flush 없이 읽기·쓰기를 전환하면 미정의 동작이다. 전환 사이에 fseek/fflush를 둔다.'},

 {'id':'FIO40-C','cat':'FIO · Rule · L3',
  'title':'fgets/fgetws 실패 시 대상 문자열을 재설정한다',
  'bad': r"""if (fgets(buf, n, f) == NULL) { use(buf); }  // 실패 후 불확정 내용 사용""",
  'good': r"""if (fgets(buf, n, f) == NULL) { buf[0] = '\0'; handle(); }""",
  'why':'fgets 실패 시 버퍼 내용은 불확정이라 그대로 사용하면 오동작한다. 실패 시 빈 문자열로 재설정하고 처리한다.'},

 {'id':'FIO41-C','cat':'FIO · Rule · L1',
  'title':'부작용이 있는 표현식을 getc/putc 등의 스트림 인자로 넘기지 않는다',
  'bad': r"""int c = getc(files[i++]);   // 매크로가 인자 다중 평가 → i 중복 증가""",
  'good': r"""FILE* f = files[i++];
int c = getc(f);""",
  'why':'getc/putc는 매크로일 수 있어 스트림 인자를 여러 번 평가한다. 부작용 있는 식을 직접 넘기지 말고 변수에 담아 전달한다.'},

 {'id':'FIO44-C','cat':'FIO · Rule · L2',
  'title':'fsetpos 에는 fgetpos 가 반환한 값만 사용한다',
  'bad': r"""fpos_t pos; pos = (fpos_t){123};   // 임의 값 — 미정의
fsetpos(f, &pos);""",
  'good': r"""fpos_t pos;
fgetpos(f, &pos);       // 같은 스트림에서 얻은 값
... fsetpos(f, &pos);""",
  'why':'fsetpos에 fgetpos가 만든 값이 아닌 임의 값을 넘기면 미정의 동작이다. 동일 스트림에서 fgetpos로 얻은 위치만 사용한다.'},

 {'id':'FIO46-C','cat':'FIO · Rule · L2',
  'title':'닫힌 파일에 접근하지 않는다',
  'bad': r"""fclose(f);
fprintf(f, "x");        // 닫은 후 사용 — 미정의""",
  'good': r"""fprintf(f, "x");
fclose(f); f = NULL;""",
  'why':'fclose 이후 FILE 포인터 사용은 미정의 동작이다. 닫은 뒤에는 사용하지 않고 포인터를 NULL로 무효화한다.'},

 {'id':'ENV32-C','cat':'ENV · Rule · L2',
  'title':'atexit 등록 핸들러는 정상적으로 반환해야 한다',
  'bad': r"""void cleanup(void) { longjmp(env, 1); }   // 비정상 종료
atexit(cleanup);""",
  'good': r"""void cleanup(void) { free_resources(); }   // 정상 반환
atexit(cleanup);""",
  'why':'종료 핸들러가 반환하지 않고 점프·재종료하면 미정의 동작이 된다. 핸들러는 작업 후 정상적으로 반환한다.'},

 {'id':'SIG35-C','cat':'SIG · Rule · L1',
  'title':'계산 예외(연산 오류) 시그널 핸들러에서 정상 반환하지 않는다',
  'bad': r"""void h(int s) { /* SIGFPE */ return; }   // 반환 시 결함 명령 재실행""",
  'good': r"""volatile sig_atomic_t fpe = 0;
void h(int s) { fpe = 1; _Exit(1); }   // 안전히 종료""",
  'why':'0 나눗셈 등 계산 예외 핸들러에서 그냥 반환하면 결함 명령이 재실행되어 무한 루프·미정의 동작이 된다. 핸들러에서 정상 반환하지 않는다.'},

 {'id':'CON30-C','cat':'CON · Rule · L2',
  'title':'스레드별 저장소(thread-specific storage)를 정리한다',
  'bad': r"""tss_create(&key, NULL);   // 소멸자 미등록 — 누수
tss_set(key, malloc(64));""",
  'good': r"""tss_create(&key, free);   // 소멸자 등록으로 자동 해제
tss_set(key, malloc(64));""",
  'why':'스레드별 저장소에 소멸자를 등록하지 않으면 스레드 종료 시 메모리가 누수된다. 정리 콜백을 등록하거나 명시적으로 해제한다.'},

 {'id':'CON32-C','cat':'CON · Rule · L2',
  'title':'비트필드 접근 시 데이터 경쟁을 방지한다',
  'bad': r"""struct { unsigned a:1; unsigned b:1; } f;
// T1: f.a=1   T2: f.b=1   — 같은 워드 동시 접근""",
  'good': r"""pthread_mutex_lock(&m);
f.a = 1;
pthread_mutex_unlock(&m);""",
  'why':'인접 비트필드는 같은 메모리 워드를 공유해, 서로 다른 비트라도 동시 갱신 시 경쟁으로 손상된다. 잠금으로 보호한다.'},

 {'id':'CON34-C','cat':'CON · Rule · L2',
  'title':'스레드 간 공유 객체는 적절한 저장 기간으로 선언한다',
  'bad': r"""void* worker(void* a) {
    int local = 0;
    spawn(&local);      // 자동 객체 주소 공유 — 수명 종료 가능""",
  'good': r"""static int shared = 0;   // 정적 저장 기간
spawn(&shared);""",
  'why':'자동 저장 기간 객체를 다른 스레드와 공유하면 생성 스레드 종료 시 댕글링이 된다. 공유 객체는 정적/동적 저장 기간으로 둔다.'},

 {'id':'CON37-C','cat':'CON · Rule · L2',
  'title':'멀티스레드 프로그램에서 signal() 을 호출하지 않는다',
  'bad': r"""signal(SIGINT, handler);   // 멀티스레드에서 동작 미정의""",
  'good': r"""// 전용 시그널 처리 스레드 + sigwait 사용
sigwait(&set, &sig);""",
  'why':'멀티스레드 환경에서 signal()의 동작은 미정의다. 시그널을 한 스레드에서 sigwait로 동기 처리하는 모델을 쓴다.'},

 {'id':'CON38-C','cat':'CON · Rule · L2',
  'title':'조건 변수 사용 시 스레드 안전성과 진행성(liveness)을 지킨다',
  'bad': r"""cnd_signal(&cv);        // 대기 스레드 없으면 신호 유실""",
  'good': r"""mtx_lock(&m); ready = 1; cnd_broadcast(&cv); mtx_unlock(&m);""",
  'why':'조건 변수 신호를 잠금·술어 설정 없이 보내면 신호 유실·교착으로 진행성이 깨진다. 잠금 안에서 상태를 갱신하고 broadcast한다.'},

 {'id':'CON41-C','cat':'CON · Rule · L2',
  'title':'가짜 실패가 가능한 원자 연산은 루프로 감싼다',
  'bad': r"""atomic_compare_exchange_weak(&v, &e, d);   // 가짜 실패 미처리""",
  'good': r"""while (!atomic_compare_exchange_weak(&v, &e, d)) { /* e 갱신 후 재시도 */ }""",
  'why':'compare_exchange_weak 등은 가짜 실패(spurious failure)가 가능해 한 번 호출로는 성공을 보장하지 못한다. 루프로 재시도한다.'},

 {'id':'MSC38-C','cat':'MSC · Rule · L1',
  'title':'미리 정의된(predefined) 식별자를 객체처럼 다루지 않는다',
  'bad': r"""const char* p = &__func__[0];
store(p);               // __func__ 의 주소 보관 — 보장 안 됨""",
  'good': r"""char name[64];
strncpy(name, __func__, sizeof name - 1);   // 값을 복사""",
  'why':'__func__ 같은 미리 정의된 식별자를 일반 객체처럼 주소 보관·전달하는 동작은 보장되지 않는다. 필요한 값은 복사해 사용한다.'},

 {'id':'MSC39-C','cat':'MSC · Rule · L1',
  'title':'불확정 상태의 va_list 에 va_arg 를 호출하지 않는다',
  'bad': r"""va_list ap; va_start(ap, n);
forward(ap);            // 피호출자가 소비
int x = va_arg(ap, int);  // 소비된 ap 재사용 — 미정의""",
  'good': r"""va_list ap, copy;
va_start(ap, n);
va_copy(copy, ap);      // 복사본으로 안전하게 처리
forward(copy); va_end(copy);""",
  'why':'다른 함수에 넘겨 소비된 va_list를 다시 사용하면 불확정 상태로 미정의 동작이 된다. va_copy로 독립 복사본을 만든다.'},

 {'id':'POS30-C','cat':'POS · Rule · L1',
  'title':'readlink() 를 올바르게 사용한다(널 종료·버퍼 크기)',
  'bad': r"""char buf[64];
readlink(path, buf, sizeof buf);
printf("%s", buf);      // readlink는 널 종료 안 함""",
  'good': r"""char buf[64];
ssize_t n = readlink(path, buf, sizeof buf - 1);
if (n >= 0) { buf[n] = '\0'; printf("%s", buf); }""",
  'why':'readlink는 널 종료를 붙이지 않고 잘릴 수 있다. 반환 길이로 직접 널 종료하고 버퍼 크기를 정확히 다룬다.'},

 {'id':'POS36-C','cat':'POS · Rule · L1',
  'title':'권한 포기(setuid/setgid)는 올바른 순서로 수행한다',
  'bad': r"""setuid(uid);            // 그룹 권한을 먼저 버리지 않음
setgid(gid);""",
  'good': r"""setgid(gid);            // 보조/그룹 권한 먼저
setuid(uid);            // 그 다음 사용자 권한""",
  'why':'사용자 권한을 먼저 버리면 그룹 권한을 버릴 권한이 사라진다. 그룹·보조 그룹을 먼저 포기하고 사용자 권한을 나중에 포기한다.'},

 {'id':'POS37-C','cat':'POS · Rule · L1',
  'title':'권한 포기가 실제로 성공했는지 확인한다',
  'bad': r"""setuid(uid);            // 반환값 미검사 — 권한 유지될 수 있음
do_work();""",
  'good': r"""if (setuid(uid) != 0) { abort(); }
if (getuid() != uid) { abort(); }   // 실제 포기 확인
do_work();""",
  'why':'권한 포기 호출이 실패해도 무시하면 상승된 권한으로 계속 실행되어 위험하다. 반환값과 실제 권한을 모두 확인한다.'},

 {'id':'POS38-C','cat':'POS · Rule · L2',
  'title':'fork 후 파일 디스크립터 경쟁을 피한다',
  'bad': r"""pid_t p = fork();
write(shared_fd, buf, n);   // 부모/자식이 같은 오프셋 공유 — 경쟁""",
  'good': r"""pid_t p = fork();
if (p == 0) { int fd = open(path, O_WRONLY); /* 자식 전용 */ }""",
  'why':'fork된 부모와 자식이 같은 디스크립터(오프셋 공유)를 동시에 쓰면 데이터가 섞인다. 자식이 자체 디스크립터를 열거나 동기화한다.'},

 {'id':'POS39-C','cat':'POS · Rule · L1',
  'title':'데이터 전송 시 올바른 바이트 순서(byte ordering)를 사용한다',
  'bad': r"""uint32_t v = get();
send(sock, &v, 4, 0);   // 호스트 바이트 순서 그대로 전송""",
  'good': r"""uint32_t v = htonl(get());   // 네트워크 바이트 순서로 변환
send(sock, &v, 4, 0);""",
  'why':'엔디안이 다른 호스트 간에 변환 없이 정수를 전송하면 값이 뒤바뀐다. 네트워크 바이트 순서(htonl/ntohl)로 변환해 전송한다.'},

 {'id':'POS44-C','cat':'POS · Rule · L1',
  'title':'스레드를 종료시키기 위해 시그널을 사용하지 않는다',
  'bad': r"""pthread_kill(t, SIGTERM);   // 시그널로 스레드 강제 종료 — 자원 누수""",
  'good': r"""atomic_store(&stop, 1);     // 협조적 종료 플래그
pthread_join(t, NULL);""",
  'why':'시그널로 스레드를 강제 종료하면 잠금·자원이 정리되지 않아 교착·누수가 난다. 협조적 종료 플래그와 join을 사용한다.'},

 {'id':'POS47-C','cat':'POS · Rule · L2',
  'title':'비동기적으로 취소될 수 있는 스레드를 사용하지 않는다',
  'bad': r"""pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);   // 임의 지점 취소""",
  'good': r"""pthread_setcanceltype(PTHREAD_CANCEL_DEFERRED, NULL);   // 취소 지점에서만""",
  'why':'비동기 취소는 임의 명령 사이에서 스레드를 멈춰 불변식·잠금을 깨뜨린다. 지연(deferred) 취소로 안전한 취소 지점에서만 취소되게 한다.'},

 {'id':'POS48-C','cat':'POS · Rule · L2',
  'title':'다른 스레드가 잠근(또는 잠기지 않은) 뮤텍스를 잠금 해제하지 않는다',
  'bad': r"""// T1 lock  /  T2 unlock — 소유하지 않은 잠금 해제""",
  'good': r"""// 잠근 스레드가 직접 해제
pthread_mutex_lock(&m); ...; pthread_mutex_unlock(&m);""",
  'why':'소유하지 않거나 잠기지 않은 뮤텍스를 해제하면 미정의 동작이다. 잠근 스레드가 같은 임계구역에서 직접 해제한다.'},

 {'id':'POS49-C','cat':'POS · Rule · L2',
  'title':'서로 다른 스레드가 같은 구조체의 다른 멤버에 동시 접근할 때 동기화한다',
  'bad': r"""struct S { char a; char b; };   // 동일 캐시라인/워드 인접 멤버
// T1: s.a=1  T2: s.b=1   — 비트필드/패킹 시 경쟁""",
  'good': r"""// 멤버를 분리하거나 잠금으로 보호
pthread_mutex_lock(&m); s.a = 1; pthread_mutex_unlock(&m);""",
  'why':'좁은 인접 멤버는 같은 메모리 단위를 공유해 서로 다른 멤버라도 동시 접근 시 경쟁이 날 수 있다. 잠금이나 패딩 분리로 보호한다.'},

 {'id':'POS50-C','cat':'POS · Rule · L2',
  'title':'스레드 간 공유하는 POSIX 객체는 적절한 저장 기간으로 선언한다',
  'bad': r"""void start(void) {
    pthread_mutex_t m;          // 자동 객체 뮤텍스
    pthread_create(&t, 0, work, &m);   // start 종료 시 무효""",
  'good': r"""static pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
pthread_create(&t, 0, work, &m);""",
  'why':'자동 저장 기간의 뮤텍스/조건변수를 다른 스레드와 공유하면 함수 종료 시 무효 객체 접근이 된다. 정적/동적 저장 기간으로 둔다.'},

 {'id':'POS51-C','cat':'POS · Rule · L2',
  'title':'순환 대기로 인한 스레드 교착을 방지한다',
  'bad': r"""// T1: lock(a); lock(b)   T2: lock(b); lock(a)""",
  'good': r"""// 전역 잠금 순서 고정: 항상 a→b
pthread_mutex_lock(&a); pthread_mutex_lock(&b);""",
  'why':'스레드마다 잠금 순서가 다르면 서로의 잠금을 기다리는 교착이 생긴다. 전역적으로 일관된 잠금 순서를 강제한다.'},

 {'id':'POS52-C','cat':'POS · Rule · L2',
  'title':'잠금을 보유한 채 블로킹 연산을 수행하지 않는다',
  'bad': r"""pthread_mutex_lock(&m);
recv(sock, buf, n, 0);   // 잠금 보유 중 블로킹 — 다른 스레드 정지""",
  'good': r"""recv(sock, buf, n, 0);   // 잠금 밖에서 블로킹
pthread_mutex_lock(&m); update(buf); pthread_mutex_unlock(&m);""",
  'why':'잠금을 쥔 채 I/O 등 블로킹 연산을 하면 다른 스레드가 오래 대기해 처리량이 급락하거나 교착된다. 블로킹은 잠금 밖에서 수행한다.'},

 {'id':'POS53-C','cat':'POS · Rule · L2',
  'title':'조건 변수는 항상 같은 뮤텍스와 함께 사용한다',
  'bad': r"""pthread_cond_wait(&cv, &m1);   // 어떤 곳
pthread_cond_wait(&cv, &m2);   // 다른 뮤텍스로 같은 cv — 미정의""",
  'good': r"""pthread_cond_wait(&cv, &m);    // 항상 동일 뮤텍스""",
  'why':'하나의 조건 변수를 서로 다른 뮤텍스와 함께 대기하면 미정의 동작이 된다. 조건 변수마다 고정된 뮤텍스를 사용한다.'},
]
