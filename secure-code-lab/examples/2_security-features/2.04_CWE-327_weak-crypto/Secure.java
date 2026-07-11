import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.nio.charset.StandardCharsets;

/**
 * [안전 예제] 강한 암호화 알고리즘 사용 (CWE-327 / KISA 2.4)
 *
 * 검증된 최신 알고리즘을 사용한다.
 * - AES-256: 대칭키 암호의 표준.
 * - GCM 모드: 기밀성 + 무결성(인증)을 함께 제공하는 AEAD.
 * - SHA-256: 충돌 저항성이 있는 해시.
 *
 * 완화 지표:
 *   Cipher.getInstance("AES/GCM/NoPadding")
 *   MessageDigest.getInstance("SHA-256")
 */
public class Secure {

    private static final SecureRandom RNG = new SecureRandom();

    public byte[] encrypt(byte[] plain) throws Exception {
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256); // AES-256
        SecretKey key = kg.generateKey();

        byte[] iv = new byte[12];  // GCM 권장 IV 길이
        RNG.nextBytes(iv);

        // ★ 안전: AES/GCM/NoPadding (AEAD로 기밀성+무결성 동시 제공)
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        return cipher.doFinal(plain);
    }

    public byte[] digest(byte[] data) throws Exception {
        // ★ 안전: SHA-256으로 무결성 값을 계산한다.
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        return md.digest(data);
    }

    public static void main(String[] args) throws Exception {
        Secure s = new Secure();
        System.out.println("enc.len=" + s.encrypt("hello".getBytes(StandardCharsets.UTF_8)).length);
        System.out.println("md.len=" + s.digest("hello".getBytes(StandardCharsets.UTF_8)).length);
    }
}
