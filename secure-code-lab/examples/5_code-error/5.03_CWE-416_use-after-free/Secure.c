#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * [안전 예제] 해제 후 즉시 NULL 대입 (CWE-416 / KISA 5.03)
 *
 * free 직후 포인터를 NULL 로 만든다(dangling pointer 제거).
 * 이후 실수로 그 포인터를 다시 쓰려 해도, NULL 검사에 걸려
 * 해제된 메모리 접근이 원천 차단된다. 이중 해제(double free)도 예방된다.
 *
 * 안전 지점:
 *   free(buf); buf = NULL;  그리고 재사용 전 NULL 검사
 */

int main(void) {
    char *buf = (char *)malloc(32);
    if (buf == NULL) {
        return 1;
    }

    snprintf(buf, 32, "%s", "hello");
    printf("before free: %s\n", buf);

    /* ★ 안전: 해제와 동시에 포인터를 무효화한다. */
    free(buf);
    buf = NULL;

    /* ★ 안전: 재사용 전에 반드시 NULL 여부를 확인한다.
     *   buf 가 NULL 이므로 아래 블록은 실행되지 않아 UAF 가 발생하지 않는다. */
    if (buf != NULL) {
        snprintf(buf, 32, "%s", "world");
        printf("reused: %s\n", buf);
    } else {
        printf("pointer is NULL — safe, no use-after-free\n");
    }

    return 0;
}
