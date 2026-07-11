#include <stdio.h>

/*
 * [취약 예제] 초기화되지 않은 변수 사용 (CWE-457 / KISA 5.04)
 *
 * total 을 선언만 하고 초기값을 주지 않은 채 덧셈에 사용한다.
 * 지역 변수는 자동으로 0 이 되지 않으며, 스택에 남아 있던 쓰레기 값을
 * 그대로 갖는다. 따라서 합계 결과가 실행할 때마다 달라지고,
 * 이 값으로 크기 계산이나 분기를 하면 예측 불가능한 오작동이 생긴다.
 *
 * 위험 지점:
 *   int total;   ← 초기화 없는 선언. 이후 total 을 누산에 사용
 */

int sum_prices(const int *prices, int n) {
    /* ★ 취약: total 을 초기화하지 않았다. 시작값이 쓰레기 값이다. */
    int total;
    int i = n;

    while (i-- > 0) {
        total += prices[i];   /* 쓰레기 값에서 누산이 시작됨 → 결과 오염 */
    }
    return total;
}

int main(void) {
    int prices[] = {100, 200, 300};
    printf("sum=%d\n", sum_prices(prices, 3));
    return 0;
}
