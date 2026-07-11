#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * [취약 예제] 해제된 자원 사용 (CWE-416 / KISA 5.03)
 *
 * malloc 으로 확보한 버퍼를 free 한 뒤에도 같은 포인터를 계속 사용한다.
 * free 이후 그 메모리는 할당자 소유로 돌아가 재사용될 수 있으므로,
 * 이를 다시 읽거나 쓰면 값 손상, 크래시, 또는 힙 공격의 발판이 된다.
 *
 * 위험 지점:
 *   free(buf);  이후에 buf 를 NULL 로 만들지 않고 strcpy/printf 로 재사용
 */

int main(void) {
    char *buf = (char *)malloc(32);
    if (buf == NULL) {
        return 1;
    }

    strcpy(buf, "hello");
    printf("before free: %s\n", buf);

    /* ★ 취약: 여기서 메모리를 해제한다. 포인터는 여전히 옛 주소를 가리킨다(dangling). */
    free(buf);

    /* ★ 취약: 해제된 메모리에 다시 쓰고(Use-After-Free) 읽는다.
     *   buf 를 NULL 로 초기화하지 않았기 때문에 컴파일은 되지만 동작은 미정의다. */
    strcpy(buf, "world");
    printf("after free (UAF): %s\n", buf);

    return 0;
}
