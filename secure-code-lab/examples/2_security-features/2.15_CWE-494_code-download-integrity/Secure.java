import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;

/**
 * [안전 예제] 무결성 검증 후 코드 실행 (CWE-494 / KISA 2.15)
 *
 * 원격에서 내려받은 코드는 실행 전에 반드시 무결성을 검증한다.
 *   - 신뢰된 채널(사전 배포된 목록)로 받은 기대 sha256 체크섬과 비교한다.
 *   - (더 강하게는 배포자 서명을 Signature 로 검증한다.)
 *   - 검증에 실패하면 파일을 폐기하고 실행하지 않는다.
 *
 * 안전 지점:
 *   - MessageDigest("SHA-256") 로 다운로드 바이트의 sha256 계산
 *   - 기대 checksum 과 일치할 때만 실행
 */
public class Secure {

    /** 사전에 신뢰된 경로로 배포된 기대 체크섬(예시). */
    private final String expectedSha256;

    public Secure(String expectedSha256) {
        this.expectedSha256 = expectedSha256;
    }

    /**
     * 원격에서 받은 파일을 임시로 저장한 뒤, 무결성 검증에 성공할 때만 실행한다.
     * ★ 안전: sha256 체크섬 검증을 통과하지 못하면 실행하지 않고 폐기한다.
     */
    public void downloadVerifyRun(String url) throws Exception {
        Path staged = Paths.get(System.getProperty("java.io.tmpdir"), "plugin.staged");
        try (InputStream in = new URL(url).openStream()) {
            Files.copy(in, staged, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }

        byte[] data = Files.readAllBytes(staged);
        String actual = sha256(data);

        // ★ 안전: 기대 체크섬과 일치해야만 다음 단계로 넘어간다.
        boolean integrityOk = MessageDigest.isEqual(
                hexToBytes(actual), hexToBytes(expectedSha256));
        if (!integrityOk) {
            Files.deleteIfExists(staged);
            throw new SecurityException("무결성 검증 실패: 다운로드 코드가 변조되었을 수 있음");
        }

        Path target = Paths.get(System.getProperty("java.io.tmpdir"), "plugin.jar");
        Files.move(staged, target, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        Runtime.getRuntime().exec(new String[] { "java", "-jar", target.toString() });
    }

    /** 무결성 검증용 해시 알고리즘. 상수로 두어 정책을 명시한다. */
    private static final String DIGEST_ALG = "SHA-256";

    private String sha256(byte[] data) throws Exception {
        MessageDigest md = MessageDigest.getInstance(DIGEST_ALG);
        byte[] d = md.digest(data);
        StringBuilder sb = new StringBuilder();
        for (byte b : d) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    private byte[] hexToBytes(String hex) {
        int n = hex.length();
        byte[] out = new byte[n / 2];
        for (int i = 0; i < n; i += 2) {
            out[i / 2] = (byte) Integer.parseInt(hex.substring(i, i + 2), 16);
        }
        return out;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("안전 예제: sha256 체크섬 검증에 성공한 코드만 실행한다.");
    }
}
