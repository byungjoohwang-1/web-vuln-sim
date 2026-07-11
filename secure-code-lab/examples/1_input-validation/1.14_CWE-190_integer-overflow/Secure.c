#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>   /* SIZE_MAX */

/*
 * [안전 예제] CWE-190 정수형 오버플로우 방어 (KISA 1.14)
 *
 * 곱셈을 수행하기 전에 결과가 size_t 범위를 넘는지 미리 검사한다.
 * count * size 가 SIZE_MAX 를 넘으면(즉 count > SIZE_MAX / size),
 * 할당을 시도하지 않고 실패로 처리한다. 나눗셈은 되돌아오지 않으므로
 * 안전하게 사전 검증할 수 있다.
 */
char *make_buffer(size_t count, size_t size) {
    /* ✓ 안전: 곱셈 전에 overflow 가능성을 검사한다. */
    if (size != 0 && count > SIZE_MAX / size) {
        /* 곱하면 되돌아올 것이므로 거부 */
        return NULL;
    }

    size_t total = count * size;   /* 이 시점엔 안전함이 보장됨 */
    char *buf = (char *)malloc(total);
    if (buf == NULL) {
        return NULL;
    }
    memset(buf, 'A', total);
    return buf;
}

int main(void) {
    size_t count = (size_t)1 << 60;
    size_t size = 32;

    char *p = make_buffer(count, size);
    if (p != NULL) {
        printf("allocated safely\n");
        free(p);
        p = NULL;   /* 해제 후 재사용 방지 */
    } else {
        printf("rejected: multiplication would overflow\n");
    }
    return 0;
}
