#include <stdio.h>
#include <string.h>

/*
 * [취약 예제] CWE-120 메모리 버퍼 오버플로우 (KISA 1.16)
 *
 * 대상 버퍼 크기를 고려하지 않는 함수(strcpy, strcat, sprintf)로
 * 외부 입력을 고정 크기 배열에 복사한다. 입력이 버퍼보다 길면
 * 인접 스택 영역(저장된 반환주소 등)을 덮어써 크래시나 코드 실행으로
 * 이어진다.
 */
void greet(const char *userName) {
    char banner[32];

    /* ✗ 위험: 길이 검사 없이 복사 (danger: strcpy() */
    strcpy(banner, "Hello, ");
    /* ✗ 위험: 경계 없는 연결 (danger: strcat() */
    strcat(banner, userName);

    char msg[64];
    /* ✗ 위험: 경계 없는 포맷 출력 (danger: sprintf() */
    sprintf(msg, "banner=%s", banner);

    printf("%s\n", msg);
}

int main(int argc, char **argv) {
    /* argv[1] 이 32바이트를 넘으면 스택이 훼손된다. */
    const char *name = (argc > 1) ? argv[1] : "world";
    greet(name);
    return 0;
}
