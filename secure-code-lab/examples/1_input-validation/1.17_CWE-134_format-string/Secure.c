#include <stdio.h>

/*
 * [안전 예제] CWE-134 포맷 스트링 삽입 방어 (KISA 1.17)
 *
 * 외부 입력을 절대 포맷 문자열 자리에 두지 않는다.
 * 포맷은 개발자가 고정한 상수("%s")로 지정하고, 사용자 입력은
 * 그에 대응하는 인자로만 전달한다. 그러면 입력에 %n 등이 있어도
 * 변환지정자가 아니라 평범한 문자로 출력된다.
 */
void logMessage(const char *userInput) {
    /* ✓ 안전: 포맷은 고정 상수, 입력은 인자로만 사용 */
    printf("%s\n", userInput);

    /* ✓ 안전: fprintf 도 고정 포맷 사용 */
    fprintf(stderr, "%s\n", userInput);
}

int main(int argc, char **argv) {
    const char *msg = (argc > 1) ? argv[1] : "hello";
    logMessage(msg);   /* "%x %n" 을 넣어도 그대로 출력될 뿐 */
    return 0;
}
