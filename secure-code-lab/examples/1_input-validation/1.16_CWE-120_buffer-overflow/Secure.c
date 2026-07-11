#include <stdio.h>
#include <string.h>

/*
 * [안전 예제] CWE-120 메모리 버퍼 오버플로우 방어 (KISA 1.16)
 *
 * 대상 버퍼 크기를 명시적으로 전달하는 경계 함수(strncpy, strncat, snprintf,
 * fgets)를 사용한다. 항상 남은 공간을 계산해 넘겨주고, 문자열이 NUL로
 * 종료되도록 보장한다.
 */
void greet(const char *userName) {
    char banner[32];

    /* ✓ 안전: 크기를 지정하고 NUL 종료 보장 */
    strncpy(banner, "Hello, ", sizeof(banner) - 1);
    banner[sizeof(banner) - 1] = '\0';

    /* ✓ 안전: 남은 공간만큼만 연결 */
    size_t room = sizeof(banner) - strlen(banner) - 1;
    strncat(banner, userName, room);

    char msg[64];
    /* ✓ 안전: 버퍼 크기를 넘겨 잘림을 보장 */
    snprintf(msg, sizeof(msg), "banner=%s", banner);

    printf("%s\n", msg);
}

int main(void) {
    char name[64];

    printf("name> ");
    /* ✓ 안전: fgets 로 입력 길이를 제한 */
    if (fgets(name, sizeof(name), stdin) != NULL) {
        name[strcspn(name, "\n")] = '\0';   /* 개행 제거 */
        greet(name);
    } else {
        greet("world");
    }
    return 0;
}
