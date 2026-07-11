import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;

/**
 * [취약 예제] 코드 삽입 (CWE-94 / KISA 4.2)
 *
 * 외부 입력을 스크립트 엔진에 그대로 넘겨 실행한다.
 * 공격자는 임의의 자바스크립트를 주입해 서버에서 코드를 실행할 수 있다.
 * (예: Java 클래스에 접근해 파일 삭제, 명령 실행 등)
 *
 * 위험 지점:
 *   engine.eval(외부입력)
 */
public class Vulnerable {

    /** HTTP 요청 파라미터 흉내 헬퍼. */
    static String req(String name) {
        // 예: expr = "java.lang.Runtime.getRuntime().exec('calc')"
        return "1 + 1";
    }

    public Object calculate() throws Exception {
        String expr = req("expr"); // 신뢰할 수 없는 외부 입력

        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("JavaScript");

        // ★ 취약: 외부 문자열을 스크립트 코드로 그대로 실행한다.
        //   입력 안에 어떤 코드든 들어올 수 있어 임의 코드 실행이 가능하다.
        Object result = engine.eval(expr);
        return result;
    }

    public static void main(String[] args) throws Exception {
        System.out.println(new Vulnerable().calculate());
    }
}
