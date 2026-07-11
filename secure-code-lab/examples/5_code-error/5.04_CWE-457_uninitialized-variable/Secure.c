#include <stdio.h>
#include <string.h>

/*
 * [안전 예제] 선언과 동시에 초기화 (CWE-457 / KISA 5.04)
 *
 * 모든 지역 변수를 선언과 동시에 명시적 초기값으로 채운다.
 * 누산기는 0 으로, 버퍼는 memset 으로 0 채움한다.
 * 그 결과 스택 쓰레기 값에 의존하지 않으며, 실행 결과가 항상 결정적이다.
 *
 * 안전 지점:
 *   int total = 0;      ← 초기화된 선언
 *   memset(buf, 0, ...) ← 배열도 0 으로 초기화
 */

int sum_prices(const int *prices, int n) {
    /* ★ 안전: total 을 0 으로 초기화하고 누산을 시작한다. */
    int total = 0;

    for (int i = 0; i < n; i++) {
        total += prices[i];
    }
    return total;
}

int main(void) {
    int prices[] = {100, 200, 300};

    /* 버퍼도 사용 전에 0 으로 초기화한다. */
    char label[16];
    memset(label, 0, sizeof(label));
    snprintf(label, sizeof(label), "sum");

    printf("%s=%d\n", label, sum_prices(prices, 3));
    return 0;
}
