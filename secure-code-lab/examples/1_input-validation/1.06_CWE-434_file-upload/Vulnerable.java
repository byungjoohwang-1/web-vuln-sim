import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;

/**
 * [취약 예제] 위험한 형식 파일 업로드 (CWE-434 / KISA 4.6)
 *
 * 업로드된 파일을 확장자·형식 검증 없이 원본 파일명 그대로 저장한다.
 * 공격자가 실행 가능한 스크립트(webshell 등)를 업로드하면
 * 서버에서 실행되어 원격 제어로 이어질 수 있다.
 *
 * 위험 지점:
 *   part.getOriginalFilename() 을 검증 없이 저장 경로로 사용
 */
public class Vulnerable {

    /** Spring MultipartFile / Servlet Part 를 흉내내는 최소 목(mock). */
    static class UploadedFile {
        String getOriginalFilename() {
            // 예: "shell.jsp" 또는 "evil.php"
            return "photo.dat";
        }
        InputStream getInputStream() {
            return new java.io.ByteArrayInputStream(new byte[0]);
        }
    }

    static final String UPLOAD_DIR = "/var/app/webroot/files/";

    public void save(UploadedFile file) throws Exception {
        // ★ 취약: 확장자/형식 검증 없이 원본 파일명을 그대로 저장한다.
        //   실행 가능한 스크립트 파일도 그대로 웹루트에 저장된다.
        String filename = file.getOriginalFilename();
        File dest = new File(UPLOAD_DIR, filename);

        try (InputStream in = file.getInputStream()) {
            Files.copy(in, dest.toPath());
        }
        System.out.println("저장됨: " + dest.getPath());
    }

    public static void main(String[] args) throws Exception {
        new Vulnerable().save(new UploadedFile());
    }
}
