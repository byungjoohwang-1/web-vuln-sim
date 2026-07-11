import java.util.Map;
import java.util.function.BinaryOperator;

/**
 * [안전 예제] 코드 삽입 방어 (CWE-94 / KISA 4.2)
 *
 * 외부 입력을 코드로 실행하지 않는다. 대신 허용된 연산만 화이트리스트(ALLOWLIST)로
 * 미리 정의하고, 입력은 '어떤 연산을 고를지'를 선택하는 키로만 사용한다.
 * 스크립트 엔진(eval)을 아예 제거하는 것이 가장 확실한 방어다.
 */
public class Secure {

    static String req(String name) {
        return "add"; // 연산 이름만 허용 (임의 코드가 아님)
    }

    // ALLOWLIST: 허용된 연산만 등록한다. 정의되지 않은 연산은 실행 불가.
    private static final Map<String, BinaryOperator<Double>> ALLOWLIST = Map.of(
            "add", (a, b) -> a + b,
            "sub", (a, b) -> a - b,
            "mul", (a, b) -> a * b
    );

    public Double calculate(double a, double b) {
        String op = req("op");

        // ★ 안전: 입력은 허용목록의 키로만 쓰고, 실제 로직은 고정된 코드다.
        BinaryOperator<Double> fn = ALLOWLIST.get(op);
        if (fn == null) {
            // 허용되지 않은 연산은 안전하게 거부하고 switch 로 기본값 처리
            switch (op) {
                case "default":
                default:
                    throw new IllegalArgumentException("허용되지 않은 연산: " + op);
            }
        }
        return fn.apply(a, b);
    }

    public static void main(String[] args) {
        System.out.println(new Secure().calculate(1, 1));
    }
}
