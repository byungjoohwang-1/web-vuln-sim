# FEAT-20260923-oauth-oidc-lab — OAuth 2.0 · OIDC · JWT 인증 심화 실습

## 배경 (PO)
API 보안 랩(sim-api-security)이 인증 실패(API2)를 다루지만, 실무에서 가장 사고가 잦은
**OAuth 2.0 / OpenID Connect / JWT** 계열 공격(redirect_uri 조작·state 부재 CSRF·PKCE
부재·JWT alg 혼동·토큰 유출·스코프 상승·ID 토큰 미검증·리프레시 회전 부재)은 전용 랩이
없다. SSO·소셜로그인·토큰 기반 인증이 표준이 된 지금 이 공백은 크다.

## 목표
모의 인증서버 **OrbitAuth**(idp.orbitauth.local, 전부 인페이지 mock)에 OAuth/OIDC
요청을 직접 던져 인증·인가 흐름의 약점을 시험하고, 표준(OAuth 2.0 Security BCP
RFC 9700, OIDC Core, JWT BCP RFC 8725)으로 방어한다.

## 도전 (9)
- O1 redirect_uri 검증 부재 → 인가코드 탈취 (open redirect)
- O2 state 파라미터 부재 → 로그인 CSRF / 계정 고정
- O3 PKCE 부재·다운그레이드 → 공용 클라이언트 코드 가로채기
- O4 JWT alg=none / 서명 미검증 → 토큰 위조
- O5 JWT alg 혼동 (RS256→HS256, 공개키를 HMAC 키로) → 토큰 위조
- O6 토큰 유출 (URL fragment·Referer·localStorage) → 세션 탈취
- O7 스코프 상승 / 과다 동의 → 권한 확대
- O8 ID 토큰 검증 부재 (aud·iss·exp·nonce 미검증) → 토큰 주입
- O9 리프레시 토큰 회전·폐기 부재 → 유출 토큰 영속

## 방식
DEF 플래그 단일 진실원천 엔진(공격 실행 → 취약/양호 판정 → 방어 적용 → 재점검).
각 도전은 고유 공격 동사/토큰으로 매칭(분기 정규식 충돌 방지). "쉽게 말하면" 비유 +
방어 코드 짝. 데모 토큰은 명백한 EXAMPLE 값.

## 완료 기준 (QA)
- 브라우저 자동 순회로 9도전 전수: 공격 인식·출력 충돌 없음·방어 후 출력 변화·양방향 채점.
- 게이트(레지스트리 대비값·a11y·dead-link·인라인 문법) 전부 통과.
- 홈 라이브 카드 + 허브 배선(#menuApi 인접) 반영.
