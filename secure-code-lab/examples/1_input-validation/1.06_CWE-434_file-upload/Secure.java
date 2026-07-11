import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Set;
import java.util.UUID;

/**
 * [안전 예제] 위험한 형식 파일 업로드 방어 (CWE-434 / KISA 4.6)
 *
 * 확장자 화이트리스트(ALLOWED_EXT)와 MIME 타입을 검증하고,
 * 원본 파일명을 신뢰하지 않고 서버가 생성한 안전한 이름으로 저장한다.
 * 저장 위치는 웹에서 직접 실행되지 않는 디렉터리를 사용한다.
 */
public class Secure {

    static class UploadedFile {
        String getOriginalFilename() { return "photo.png"; }
        String getContentType() { return "image/png"; }
        InputStream getInputStream() { return new java.io.ByteArrayInputStream(new byte[0]); }
    }

    // 허용 확장자 화이트리스트
    private static final Set<String> ALLOWED_EXT = Set.of(".png", ".jpg", ".jpeg", ".gif");
    private static final Set<String> ALLOWED_MIME = Set.of("image/png", "image/jpeg", "image/gif");
    static final String UPLOAD_DIR = "/var/app/storage/uploads/"; // 실행 불가 영역

    public void save(UploadedFile file) throws Exception {
        String original = file.getOriginalFilename();
        String lower = original.toLowerCase();

        // ★ 안전: 확장자 화이트리스트 + MIME 타입 이중 검증
        boolean extOk = false;
        for (String ext : ALLOWED_EXT) {
            if (lower.endsWith(ext)) { extOk = true; break; }
        }
        if (!extOk || !ALLOWED_MIME.contains(file.getContentType())) {
            throw new SecurityException("허용되지 않은 파일 형식: " + original);
        }

        // 원본 파일명을 신뢰하지 않고 안전한 새 이름으로 저장한다.
        String ext = lower.substring(lower.lastIndexOf('.'));
        String safeName = UUID.randomUUID() + ext;
        File dest = new File(UPLOAD_DIR, safeName);

        try (InputStream in = file.getInputStream()) {
            Files.copy(in, dest.toPath());
        }
        System.out.println("저장됨: " + dest.getPath());
    }

    public static void main(String[] args) throws Exception {
        new Secure().save(new UploadedFile());
    }
}
