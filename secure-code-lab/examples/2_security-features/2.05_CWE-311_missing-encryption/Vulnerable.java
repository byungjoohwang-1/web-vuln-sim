import java.io.FileWriter;
import java.io.IOException;

/**
 * [취약 예제] 암호화되지 않은 중요정보 (CWE-311 / KISA 2.5)
 *
 * 비밀번호, 주민등록번호(ssn), 카드번호(cardNo) 같은 민감정보를
 * 아무런 보호 없이 평문 그대로 파일/로그에 저장한다.
 * 파일이 유출되거나 로그가 노출되면 민감정보가 그대로 드러난다.
 *
 * 위험 지점:
 *   write/println 으로 password, ssn, cardNo 같은 민감정보를 평문 저장.
 */
public class Vulnerable {

    static class Member {
        String userId;
        String password;   // 민감정보
        String ssn;        // 주민등록번호
        String cardNo;     // 카드번호
        Member(String u, String p, String s, String c) {
            this.userId = u; this.password = p; this.ssn = s; this.cardNo = c;
        }
    }

    public void saveMember(Member m) throws IOException {
        try (FileWriter w = new FileWriter("members.txt", true)) {
            // ★ 취약: 민감정보를 평문 그대로 파일에 기록한다.
            w.write("password=" + m.password + "\n");
            w.write("ssn=" + m.ssn + "\n");
            w.write("cardNo=" + m.cardNo + "\n");
        }
        // ★ 취약: 로그에도 비밀번호가 평문으로 남는다.
        System.out.println("saved password=" + m.password);
    }

    public static void main(String[] args) throws IOException {
        new Vulnerable().saveMember(
                new Member("alice", "P@ssw0rd!", "900101-1234567", "4111111111111111"));
    }
}
