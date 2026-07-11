import java.io.IOException;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.Set;

/**
 * [안전 예제] 중요자원에 대한 올바른 권한 설정 (CWE-732 / KISA 2.3)
 *
 * 민감정보 파일은 소유자에게만 읽기/쓰기를 허용하고 그 외에는 모두 차단한다.
 * (POSIX 기준 0700 / "rw-------")
 *
 * 완화 지표:
 *   OWNER_READ/OWNER_WRITE 권한만 부여하거나 "rw-------" 로 최소권한을 적용,
 *   setReadable(true, true) 로 "소유자에게만" 권한을 제한한다.
 */
public class Secure {

    public Path writeSecretConfig() throws IOException {
        Path p = Path.of("app-secret.conf");
        // ★ 안전: 비밀값은 소스에 넣지 않고 환경변수에서 읽어 파일에 기록한다.
        String secret = System.getenv("DB_PASSWORD");
        Files.writeString(p, "db.password=" + (secret == null ? "" : secret) + "\n");

        try {
            // ★ 안전: 소유자 전용 권한만 부여 (rw-------), 그룹/기타는 권한 없음.
            Set<PosixFilePermission> perms = Set.of(
                    PosixFilePermission.OWNER_READ,
                    PosixFilePermission.OWNER_WRITE);
            Files.setPosixFilePermissions(p, perms);
            // 문자열로도 동일: PosixFilePermissions.fromString("rw-------")
            PosixFilePermissions.asFileAttribute(
                    PosixFilePermissions.fromString("rw-------"));
        } catch (UnsupportedOperationException nonPosix) {
            // ★ 안전(대체): Windows 등 비 POSIX 파일시스템에서는
            //   두 번째 인자 true 로 "소유자에게만" 권한을 제한한다.
            File f = p.toFile();
            f.setReadable(false, false); // 우선 모두 차단
            f.setWritable(false, false);
            f.setReadable(true, true);   // 소유자에게만 허용
            f.setWritable(true, true);
        }
        return p;
    }

    public static void main(String[] args) throws IOException {
        Path p = new Secure().writeSecretConfig();
        System.out.println("생성(소유자 전용 권한): " + p);
    }
}
