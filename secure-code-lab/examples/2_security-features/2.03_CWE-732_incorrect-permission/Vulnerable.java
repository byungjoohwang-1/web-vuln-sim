import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * [취약 예제] 중요자원에 대한 잘못된 권한 설정 (CWE-732 / KISA 2.3)
 *
 * 민감정보가 담긴 파일(비밀키, 설정 등)을 만들면서
 * 모든 사용자가 읽고 쓸 수 있도록 권한을 과도하게 부여한다.
 * 같은 서버의 다른 계정/프로세스가 파일을 열람하거나 변조할 수 있다.
 *
 * 위험 지점:
 *   setReadable(true, false) / setWritable(true, false)
 *   → 두 번째 인자 false는 "소유자뿐 아니라 모두에게" 적용을 뜻한다.
 */
public class Vulnerable {

    public File writeSecretConfig() throws IOException {
        File f = new File("app-secret.conf");
        try (FileWriter w = new FileWriter(f)) {
            w.write("db.password=super-secret\n");
        }

        // ★ 취약: 두 번째 인자 false = "전체 사용자"에게 권한 부여.
        //   결과적으로 다른 사용자도 읽고 쓸 수 있는(0666에 준하는) 상태가 된다.
        f.setReadable(true, false);
        f.setWritable(true, false);
        f.setExecutable(true, false);

        return f;
    }

    public static void main(String[] args) throws IOException {
        File f = new Vulnerable().writeSecretConfig();
        System.out.println("생성: " + f.getName()
                + " (readable=" + f.canRead() + ", writable=" + f.canWrite() + ")");
    }
}
