import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.security.MessageDigest;

/**
 * [취약 예제] 취약한 암호화 알고리즘 사용 (CWE-327 / KISA 2.4)
 *
 * 이미 안전하지 않다고 알려진 알고리즘(DES, MD5)을 사용한다.
 * - DES: 56비트 키로 현대 하드웨어에서 전수조사가 가능하다.
 * - ECB 모드: 같은 평문 블록이 같은 암호문이 되어 패턴이 드러난다.
 * - MD5: 충돌이 발견되어 무결성/서명 용도로 부적합하다.
 *
 * 위험 지점:
 *   Cipher.getInstance("DES/ECB/PKCS5Padding")
 *   MessageDigest.getInstance("MD5")
 */
public class Vulnerable {

    public byte[] encrypt(byte[] plain) throws Exception {
        KeyGenerator kg = KeyGenerator.getInstance("DES");
        SecretKey key = kg.generateKey();

        // ★ 취약: 취약 알고리즘(DES) + 취약 모드(ECB)
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        return cipher.doFinal(plain);
    }

    public byte[] digest(byte[] data) throws Exception {
        // ★ 취약: 충돌 취약점이 있는 MD5로 무결성 값을 계산한다.
        MessageDigest md = MessageDigest.getInstance("MD5");
        return md.digest(data);
    }

    public static void main(String[] args) throws Exception {
        Vulnerable v = new Vulnerable();
        System.out.println("enc.len=" + v.encrypt("hello".getBytes()).length);
        System.out.println("md.len=" + v.digest("hello".getBytes()).length);
    }
}
