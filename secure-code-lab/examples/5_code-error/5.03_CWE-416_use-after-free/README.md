# 해제된 자원 사용 (Use-After-Free) · CWE-416 · KISA 5.03

## 개념
이미 `free()`로 반환한 메모리를 가리키는 포인터(dangling pointer)를 통해 그 메모리를 다시 읽거나 쓰는 약점이다. 해제된 공간은 할당자가 재사용할 수 있으므로, 접근 결과는 미정의 동작(undefined behavior)이다.

## 취약 원인
- `free(buf)` 이후에도 `buf`가 옛 주소를 그대로 가리킨다.
- 해제 직후 포인터를 `NULL`로 무효화하지 않았다.
- 재사용 전 유효성 검사가 없어 dangling pointer에 `strcpy`/`printf`를 수행한다.

## 영향
- 재사용된 힙 청크의 값이 손상되어 데이터 무결성이 깨진다.
- 공격자가 그 사이에 힙을 조작하면 값 위조, 제어 흐름 탈취, 원격 코드 실행으로 이어질 수 있다.
- 같은 포인터를 다시 `free`하면 이중 해제(double free)로 힙 메타데이터가 파손된다.

## 안전한 코딩
- `free(buf);` 직후 반드시 `buf = NULL;`로 포인터를 무효화한다.
- 재사용 전에는 `if (buf != NULL)`로 유효성을 확인한다.
- 소유권과 수명을 명확히 하여 해제 이후 접근 경로 자체를 없앤다.

## 취약 vs 안전 차이
| 구분 | 취약 (Vulnerable.c) | 안전 (Secure.c) |
|------|---------------------|------------------|
| 해제 후 포인터 | 그대로 유지(dangling) | `buf = NULL;` |
| 재사용 검사 | 없음 | `if (buf != NULL)` |
| double free | 가능 | NULL 대입으로 예방 |

## CWE·KISA 매핑
- CWE-416: Use After Free
- KISA 소프트웨어 개발보안 가이드(2021) 5장 코드오류 — 해제된 자원 사용 (5.03)

## 실행/컴파일 방법
```
gcc Vulnerable.c -o vuln   # (권장) -fsanitize=address 로 UAF 관찰
gcc Secure.c -o safe

./vuln     # 해제된 메모리 접근(미정의 동작)
./safe     # NULL 처리로 안전

# 프로젝트 루트에서 탐지 검증
python bugfinder/bugfinder.py examples/5_code-error/5.03_CWE-416_use-after-free
```

## 참고
- CWE-416: https://cwe.mitre.org/data/definitions/416.html
- AddressSanitizer(ASan): `-fsanitize=address`로 use-after-free 탐지
