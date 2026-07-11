import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.io.FileOutputStream;
import java.io.IOException;
import java.security.SecureRandom;
import java.util.Base64;

/**
 * [안전 예제] 중요정보 암호화 저장 (CWE-311 / KISA 2.5)
 *
 * 비밀번호는 원문 복원이 필요 없으므로 저장하지 않는 것이 원칙이지만,
 * 카드번호/주민등록번호처럼 복호화가 필요한 값은 반드시 암호화해 저장한다.
 * 여기서는 AES/GCM으로 암호화한 뒤에만 파일에 기록한다.
 *
 * 완화 지표:
 *   Cipher + AES 로 민감정보를 encrypt 한 후 저장한다.
 */
public class Secure {

    private static final SecureRandom RNG = new SecureRandom();
    private final SecretKey key;

    public Secure() throws Exception {
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256);
        this.key = kg.generateKey();
    }

    /** 민감정보를 AES/GCM으로 암호화한다(iv || ciphertext 를 Base64로 반환). */
    private String encrypt(String plain) throws Exception {
        byte[] iv = new byte[12];
        RNG.nextBytes(iv);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        byte[] ct = cipher.doFinal(plain.getBytes("UTF-8"));
        byte[] out = new byte[iv.length + ct.length];
        System.arraycopy(iv, 0, out, 0, iv.length);
        System.arraycopy(ct, 0, out, iv.length, ct.length);
        return Base64.getEncoder().encodeToString(out);
    }

    public void saveMember(String userId, String ssn, String cardNo) throws Exception {
        // ★ 안전: 민감정보를 암호화(encrypt)한 결과만 저장한다.
        String encSsn = encrypt(ssn);
        String encCard = encrypt(cardNo);
        try (FileOutputStream fos = new FileOutputStream("members.enc", true)) {
            fos.write(("ssn.enc=" + encSsn + "\n").getBytes("UTF-8"));
            fos.write(("card.enc=" + encCard + "\n").getBytes("UTF-8"));
        }
        // 로그에는 민감정보 원문을 남기지 않는다.
        System.out.println("saved encrypted member: " + userId);
    }

    public static void main(String[] args) throws Exception {
        new Secure().saveMember("alice", "900101-1234567", "4111111111111111");
    }
}
