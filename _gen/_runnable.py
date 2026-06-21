# -*- coding: utf-8 -*-
"""온라인 IDE에서 '실제로 실행'되는 자기완결형 보안 데모.
Python=Pyodide(브라우저 내 실행), Java/C=Piston(외부 실행 API). 각 데모는 취약 vs 안전을
한 번에 출력해 차이를 직접 확인하게 한다. (KISA 49개 단편은 프레임워크 의존이라 별도 편집용)
스키마: lang / weakness / title / code / note
"""

RUNNABLE = [
    # ---------------- Python (Pyodide) ----------------
    {'lang':'Python','weakness':'코드 삽입','title':'eval vs ast.literal_eval',
     'code':'''import ast

safe_in = "[1, 2, 3]"
evil_in = "__import__('os').getcwd()"   # 공격 입력

print("[취약] eval(정상):", eval(safe_in))
print("[취약] eval(공격):", eval(evil_in), " <- eval은 임의 코드를 실행해버림")

for label, code in [("정상", safe_in), ("공격", evil_in)]:
    try:
        print(f"[안전] literal_eval({label}):", ast.literal_eval(code))
    except (ValueError, SyntaxError) as e:
        print(f"[안전] literal_eval가 {label} 입력 차단 ->", type(e).__name__)
''',
     'note':'eval은 공격 입력까지 실행한다. ast.literal_eval은 리터럴만 허용해 코드 삽입을 차단한다.'},
    {'lang':'Python','weakness':'적절하지 않은 난수값 사용','title':'random vs secrets',
     'code':'''import random, secrets

# [취약] 시드를 알면 예측 가능 (재현됨)
print("[취약] random(seed=1234):", random.Random(1234).randint(1000, 9999))
print("[취약] random(seed=1234):", random.Random(1234).randint(1000, 9999), "<- 항상 동일")

# [안전] 암호학적으로 안전한 난수
print("[안전] secrets.token_hex:", secrets.token_hex(8))
print("[안전] secrets.token_hex:", secrets.token_hex(8), "<- 매번 다름")
''',
     'note':'일반 PRNG(random)는 시드로 예측·재현된다. 토큰·키에는 secrets/SecureRandom을 써야 한다.'},
    {'lang':'Python','weakness':'솔트 없이 일방향 해시함수 사용','title':'단순 해시 vs 솔트+PBKDF2',
     'code':'''import hashlib, os

pw = b"password123"

# [취약] 솔트 없는 단순 해시 -> 같은 비밀번호는 항상 같은 값(레인보우 테이블 공격)
print("[취약] sha256(솔트X):", hashlib.sha256(pw).hexdigest()[:32], "...")
print("[취약] sha256(솔트X):", hashlib.sha256(pw).hexdigest()[:32], "... <- 동일")

# [안전] 사용자별 솔트 + 반복(적응형) 해시
salt = os.urandom(16)
dk = hashlib.pbkdf2_hmac('sha256', pw, salt, 100_000)
print("[안전] pbkdf2(솔트O):", dk.hex()[:32], "... <- 솔트마다 달라짐")
''',
     'note':'솔트 없는 해시는 사전/레인보우 공격에 약하다. 사용자별 솔트 + 적응형(pbkdf2/bcrypt)이 표준.'},

    # ---------------- Java (Piston) ----------------
    {'lang':'Java','weakness':'SQL 삽입','title':'문자열 결합 쿼리 vs 파라미터 바인딩',
     'code':'''public class Main {
    public static void main(String[] args) {
        String id = "1' OR '1'='1";   // 공격 입력
        // [취약] 외부 입력을 문자열로 결합
        String vuln = "SELECT * FROM users WHERE id = '" + id + "'";
        System.out.println("[취약] 생성된 쿼리: " + vuln);
        System.out.println("       -> 조건이 항상 참이 되어 전체 행이 노출됨(SQL 삽입)");
        // [안전] PreparedStatement는 ?로 값만 바인딩 -> 입력이 쿼리 '구조'를 못 바꿈
        System.out.println("[안전] 쿼리: SELECT * FROM users WHERE id = ?  (값='" + id + "' 바인딩)");
        System.out.println("       -> 입력은 데이터로만 취급되어 삽입 불가");
    }
}''',
     'note':'문자열 결합은 입력이 쿼리 구조를 바꿔 SQL 삽입이 된다. PreparedStatement + setXxx 바인딩이 근본 대책.'},
    {'lang':'Java','weakness':'정수형 오버플로우','title':'int 오버플로우 vs long 승격',
     'code':'''public class Main {
    public static void main(String[] args) {
        int max = Integer.MAX_VALUE;
        System.out.println("[취약] Integer.MAX_VALUE + 1 = " + (max + 1) + "  <- 음수로 래핑");
        long safe = (long) max + 1;
        System.out.println("[안전] (long)MAX_VALUE + 1 = " + safe + "  <- 정상");
        System.out.println("-> 연산 전 범위 검증/충분한 자료형/Math.addExact 사용");
    }
}''',
     'note':'고정폭 정수 연산이 한계를 넘으면 래핑(오버플로우)된다. 범위 검증·승격·Math.*Exact로 방지.'},
    {'lang':'Java','weakness':'취약한 암호화 알고리즘 사용','title':'안전한 해시(SHA-256)',
     'code':'''import java.security.MessageDigest;

public class Main {
    public static void main(String[] args) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");  // DES/MD5/SHA-1 금지
        byte[] d = md.digest("hello".getBytes("UTF-8"));
        StringBuilder sb = new StringBuilder();
        for (byte b : d) sb.append(String.format("%02x", b));
        System.out.println("[안전] SHA-256: " + sb);
        System.out.println("-> MD5/SHA-1/DES 같은 취약 알고리즘 대신 SHA-256 이상/AES 사용");
    }
}''',
     'note':'MD5·SHA-1·DES는 취약하다. SHA-256 이상, 대칭키는 AES(GCM/CBC)로 교체해야 한다.'},

    # ---------------- C (Piston) ----------------
    {'lang':'C','weakness':'정수형 오버플로우','title':'INT_MAX 오버플로우 vs long',
     'code':'''#include <stdio.h>
#include <limits.h>

int main(void) {
    int max = INT_MAX;
    printf("[취약] INT_MAX + 1 = %d   <- 음수로 래핑(오버플로우)\\n", max + 1);
    long safe = (long)max + 1;
    printf("[안전] (long)INT_MAX + 1 = %ld\\n", safe);
    printf("-> 연산 전 범위 검증 및 충분한 크기의 자료형 사용\\n");
    return 0;
}''',
     'note':'C의 int 연산은 한계를 넘으면 미정의/래핑 동작을 한다. 경계 검증과 자료형 크기로 방지.'},
    {'lang':'C','weakness':'메모리 버퍼 오버플로우','title':'strcpy 위험 vs strncpy 안전',
     'code':'''#include <stdio.h>
#include <string.h>

int main(void) {
    char buf[8];
    const char *src = "ABCDEFGHIJKLMNOP";   /* 16바이트 > buf(8) */
    /* [안전] 대상 크기만큼만 복사 + 널 종료 보장 */
    strncpy(buf, src, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\\0';
    printf("[안전] strncpy 결과(잘림): %s\\n", buf);
    printf("-> strcpy(buf, src) 였다면 buf 경계를 넘어 인접 메모리 손상(버퍼 오버플로우)\\n");
    return 0;
}''',
     'note':'경계를 검사하지 않는 strcpy/gets는 버퍼 오버플로우를 일으킨다. 크기를 받는 strncpy/snprintf 사용.'},
    {'lang':'C','weakness':'포맷 스트링 삽입','title':'printf(user) 위험 vs printf("%s", user)',
     'code':'''#include <stdio.h>

int main(void) {
    char *user = "%x %x %x";   /* 공격자가 포맷 지정자를 주입 */
    printf("[취약] printf(user) -> ");
    printf(user);              /* 포맷 문자열로 해석되어 메모리 누출 위험 */
    printf("\\n[안전] printf(\\"%%s\\", user) -> ");
    printf("%s", user);        /* 사용자 입력은 인자로만 */
    printf("\\n-> 포맷 문자열은 항상 고정 리터럴, 외부 입력은 %%s 인자로 전달\\n");
    return 0;
}''',
     'note':'사용자 입력을 printf의 포맷 인자로 직접 주면 포맷 스트링 삽입이 된다. 포맷은 고정하고 입력은 %s로.'},
]
