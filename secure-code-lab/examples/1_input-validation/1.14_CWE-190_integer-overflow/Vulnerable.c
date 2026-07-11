#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * [취약 예제] CWE-190 정수형 오버플로우 (KISA 1.14)
 *
 * 원소 개수(count)와 원소 크기(size)를 곱해 할당 크기를 계산한다.
 * 두 값이 크면 곱셈 결과가 size_t 표현 범위를 넘어 값이 작은 수로
 * 되돌아온다(wrap-around). 그러면 필요한 양보다 훨씬 작은 버퍼가
 * 할당되고, 이후 원소를 채우면서 힙 경계를 넘어 쓰게 된다.
 */
char *make_buffer(size_t count, size_t size) {
    /* ✗ 위험: count * size 가 되돌아올 수 있음 (danger: malloc( count * ) */
    char *buf = (char *)malloc(count * size);
    if (buf == NULL) {
        return NULL;
    }
    /* 곱이 되돌아왔다면 여기서 힙 경계 밖으로 씀 */
    memset(buf, 'A', count * size);
    return buf;
}

int main(void) {
    /* 공격자가 조종하는 값이라고 가정 */
    size_t count = (size_t)1 << 60;   /* 매우 큰 개수 */
    size_t size = 32;

    char *p = make_buffer(count, size);
    if (p != NULL) {
        printf("allocated (return value trusted blindly)\n");
        free(p);
    } else {
        printf("malloc failed\n");
    }
    return 0;
}
