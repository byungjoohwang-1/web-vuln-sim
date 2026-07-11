#include <stdio.h>

/*
 * [취약 예제] CWE-134 포맷 스트링 삽입 (KISA 1.17)
 *
 * 외부 입력을 printf 계열 함수의 "포맷 문자열" 자리에 그대로 넘긴다.
 * 입력에 %x, %n 같은 변환지정자가 들어 있으면 printf 는 실재하지 않는
 * 인자를 읽어(스택 정보 유출) 출력하거나, %n 으로 임의 메모리에 값을
 * 쓸 수 있어 코드 실행까지 가능하다.
 */
void logMessage(const char *userInput) {
    /* ✗ 위험: 입력이 곧 포맷 문자열 (danger: printf( userInput ) */
    printf(userInput);
    printf("\n");

    /* ✗ 위험: 두 번째 인자를 포맷으로 사용 */
    fprintf(stderr, userInput);
}

int main(int argc, char **argv) {
    /* 예: ./vuln "%x %x %x %n" 이면 스택 유출/쓰기 발생 */
    const char *msg = (argc > 1) ? argv[1] : "hello";
    logMessage(msg);
    return 0;
}
