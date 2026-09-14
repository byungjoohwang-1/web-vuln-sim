# -*- coding: utf-8 -*-
"""'🏗️ 현대 금융 IT 환경에서의 변형' 패널 내용 — 파일명 키.

왜 필요한가:
  「전자금융기반시설 보안 취약점 평가기준」은 **웹 · 모바일앱 · HTS** 3계층을 전제로 쓰였다.
  현장은 API 게이트웨이 · MSA · 컨테이너 · 오픈뱅킹/마이데이터로 옮겨 갔고, 같은 취약점이
  다른 모습으로 나타난다. 평가항목을 그대로 두되, **오늘의 아키텍처에서 어디를 봐야 하는지**를
  덧붙여 학습자가 실제 시스템에 옮길 수 있게 한다.

작성 원칙:
  - 일반론 금지. 그 항목에서만 통하는 구체적 지점을 쓴다.
  - 각 항목은 [아키텍처 맥락] → [구체적 조치] → [놓치기 쉬운 지점] 순서.
  - 한국 금융 규제와 글로벌 관행이 충돌하면 그 사실을 밝힌다(예: 비밀번호 주기 변경).
  - stack 칩은 4개 이하. 많으면 아무 의미가 없다.
"""

MODERN = {

# ══════════════════════════ 거래 ══════════════════════════
'07_fin-transaction-integrity.html': {
 'stack': ['API Gateway', 'MSA', 'mTLS', 'Kafka'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>모놀리식에서는 전문이 한 프로세스 안에서 끝났지만, MSA 에서는 <code>api-gw → txn-orchestrator → ledger-service</code> 처럼
여러 홉을 지납니다. <b>게이트웨이에서만 HMAC 을 검증하고 내부 구간은 "내부망이니까" 신뢰하는 설계</b>가 가장 흔한 구멍입니다.
내부 서비스 하나가 SSRF 로 뚫리면 그 뒤는 검증 없이 통과합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>서명은 종단 간(end-to-end)으로.</b> 게이트웨이가 검증한 뒤 <u>다시 서명해서</u> 내부로 넘기거나, 원 서명을 그대로 전달해 최종 처리 서비스가 검증합니다.</li>
<li>서비스 간 채널은 <b>mTLS + SPIFFE/SPIRE</b> 로 신원을 증명합니다. 네트워크 위치(내부망)를 신원으로 쓰지 않습니다.</li>
<li>이벤트 기반이라면 <b>메시지 자체에 서명</b>합니다. Kafka 토픽에 올라간 이체 이벤트는 컨슈머가 여럿이고, 재처리도 됩니다.</li>
</ul>
<pre>// 게이트웨이 통과 후에도 최종 서비스에서 다시 검증
@PostMapping("/internal/transfer")
public void transfer(@RequestHeader("X-Txn-Signature") String sig,
                     @RequestHeader("X-Spiffe-Id") String caller,
                     @RequestBody TxnRequest req) {
    if (!allowedCallers.contains(caller))          // 누가 불렀는지
        throw new SecurityException("unknown caller");
    if (!hmacValid(sig, req.canonical()))          // 무엇을 보냈는지
        throw new SecurityException("tampered payload");
    ...
}</pre>
<div class="warn">놓치기 쉬운 곳 — <b>서비스 메시(Istio)의 mTLS 는 "누가 불렀는지"만 증명합니다.</b>
전문 내용이 바뀌지 않았음은 증명하지 못합니다. 두 가지는 대체재가 아니라 함께 써야 합니다.</div>''',
},

'07_fin-replay.html': {
 'stack': ['멱등성 키', 'Redis', '오토스케일링', 'Kafka'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>단일 서버에서는 <code>Set&lt;String&gt; usedNonce</code> 같은 인메모리 저장으로도 막혔습니다.
<b>오토스케일링으로 파드가 여러 개면 이 방어는 즉시 무너집니다</b> — 같은 nonce 가 다른 파드로 가면 "처음 보는 값"이 됩니다.
게다가 Kafka 같은 스트림은 기본이 <b>at-least-once</b> 라 정상 운영 중에도 같은 이벤트가 두 번 옵니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>nonce 저장소를 <b>공유 저장소로</b>: Redis <code>SET key NX EX 300</code> 또는 DB 유니크 제약. 원자적 연산이어야 합니다.</li>
<li>API 는 <b>Idempotency-Key 헤더</b>를 받습니다(Stripe·토스페이먼츠 등이 쓰는 표준 방식). 같은 키의 재요청에는 <u>재처리 대신 첫 응답을 그대로 반환</u>합니다.</li>
<li>컨슈머는 <b>멱등하게</b> 설계합니다. "이미 처리된 주문인가"를 원장에서 확인하는 것이 재전송 방어의 최종선입니다.</li>
</ul>
<pre>// Redis 원자적 선점 — 다중 파드에서도 단 한 번만 통과
Boolean first = redis.opsForValue()
        .setIfAbsent("nonce:" + req.getNonce(), "1", Duration.ofMinutes(5));
if (!Boolean.TRUE.equals(first))
    return ledger.findResult(req.getIdempotencyKey());  // 첫 응답 재사용</pre>
<div class="warn">놓치기 쉬운 곳 — <b>Redis 가 죽으면 어떻게 되는가.</b> 예외를 삼키고 통과시키면
장애 시점이 곧 리플레이 창구가 됩니다. 저장소 장애 시에는 <b>거래를 거절</b>하는 쪽이 안전합니다(fail-closed).</div>''',
},

# ══════════════════════════ 인증 · 인가 ══════════════════════════
'07_fin-idor-account.html': {
 'stack': ['OWASP API #1', 'BFF', 'GraphQL', '오픈뱅킹'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>이 취약점은 오늘날 <b>OWASP API Security Top 10 의 1위(BOLA, Broken Object Level Authorization)</b> 입니다.
API 우선 아키텍처에서 더 위험해진 이유는 <b>엔드포인트가 화면이 아니라 자원 단위</b>이기 때문입니다 —
<code>/accounts/{id}/transactions</code> 는 화면 흐름과 무관하게 누구나 직접 호출할 수 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>게이트웨이는 이 검증을 못 합니다.</b> JWT 의 <code>sub</code> 는 알지만 "이 계좌가 그 사람 것인지"는 도메인 지식이라, <u>반드시 서비스 계층</u>에서 확인해야 합니다.</li>
<li>GraphQL 이라면 <b>노드 단위 인가</b>가 필요합니다. 리졸버마다 소유권을 확인하지 않으면 중첩 쿼리로 우회됩니다.</li>
<li>오픈뱅킹/마이데이터는 <b>동의 범위(scope)와 계좌 목록</b>을 서버가 보관하고, 요청 계좌가 그 목록에 있는지 매 호출 확인합니다.</li>
</ul>
<pre># FastAPI — 의존성으로 강제해 "빠뜨릴 수 없게" 만든다
async def owned_account(account_id: str, user=Depends(current_user)) -> Account:
    acc = await repo.get(account_id)
    if acc is None or acc.owner_id != user.id:
        raise HTTPException(404)     # 403 이 아니라 404 — 계좌 존재 여부도 숨긴다
    return acc

@router.get("/accounts/{account_id}/transactions")
async def txns(acc: Account = Depends(owned_account)): ...</pre>
<div class="warn">놓치기 쉬운 곳 — <b>403 을 주면 "그 계좌는 존재한다"를 알려 주는 셈</b>입니다.
계좌번호 순회로 실계좌 목록을 만들 수 있으므로, 남의 자원에는 <b>404</b> 가 안전합니다.</div>''',
},

'07_fin-txn-auth.html': {
 'stack': ['FIDO2 / 패스키', '푸시 승인', 'Transaction Signing'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>OTP·보안카드는 <b>공유 비밀</b> 방식이라 피싱·중계 공격에 약합니다. 국내외 금융권은
<b>FIDO2/패스키(공개키 기반)</b> 와 <b>앱 푸시 승인</b> 으로 옮겨 가고 있습니다. 다만 인증 방식이 바뀌어도
<b>취약점의 본질은 그대로</b>입니다 — "2차 인증을 통과했다"는 사실을 <u>누가 서버에 알려 주는가</u>.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>클라이언트가 <code>{"otpVerified": true}</code> 를 보내는 구조는 방식과 무관하게 위험합니다. <b>서버가 인증 상태를 보관</b>해야 합니다.</li>
<li><b>거래 단위 서명(Transaction Signing)</b>: 인증 대상에 <u>수취계좌·금액</u>을 포함시켜 서명받습니다. "로그인 승인"과 "5천만원 이체 승인"이 구분됩니다.</li>
<li>FIDO2 라면 <code>challenge</code> 에 거래 해시를 넣고, 응답의 <code>clientDataJSON</code> 에서 그 값을 서버가 대조합니다.</li>
</ul>
<pre>// 푸시 승인 화면에 반드시 거래 내용을 띄운다 — "무엇을 승인하는지" 모르면 의미가 없다
{
  "title": "이체 승인",
  "amount": "50,000,000원",
  "to": "국민 123-45-6789 홍길동",
  "challenge": "sha256(txnId|to|amount|nonce)"
}</pre>
<div class="warn">놓치기 쉬운 곳 — <b>승인 화면에 거래 내용을 안 띄우면 중계 공격이 그대로 성립</b>합니다.
공격자가 유도한 이체를 사용자가 "로그인인 줄 알고" 승인합니다. 이를 <b>거래 내용 확인(WYSIWYS)</b> 이라 부릅니다.</div>''',
},

'07_fin-fixed-authcode.html': {
 'stack': ['SMS 대체', '레이트리밋', 'Redis'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>SMS 인증코드는 <b>SIM 스와핑·문자 가로채기</b>에 취약해 국제적으로 권고 등급이 낮아졌습니다(NIST SP 800-63B 는
SMS 를 &ldquo;restricted&rdquo; 로 분류). 국내는 본인확인 제도상 SMS 의존이 크지만, <b>앱 푸시·패스키를 1순위로 두고
SMS 는 대체 수단</b>으로 내리는 것이 현재 방향입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>코드는 <b>서버에서 CSPRNG 로 생성</b>하고 절대 클라이언트로 내려보내지 않습니다(응답 본문·로그·에러 메시지 포함).</li>
<li><b>시도 횟수 제한</b>(예: 5회 후 무효화)과 <b>발급 레이트리밋</b>을 분산 저장소로 구현합니다 — 파드마다 세면 의미가 없습니다.</li>
<li>코드 검증은 <b>상수 시간 비교</b>로. 문자열 <code>equals</code> 는 타이밍 정보를 흘립니다.</li>
</ul>
<pre># 발급·검증 모두 서버 상태로 (TTL + 시도 횟수)
key = f"authcode:{user_id}"
code = secrets.randbelow(1_000_000)            # CSPRNG
redis.hset(key, mapping={"code": hash(code), "tries": 0})
redis.expire(key, 180)                          # 3분
# 검증 시 tries 증가, 5회 초과면 삭제 후 재발급 요구</pre>
<div class="warn">놓치기 쉬운 곳 — <b>APM·로그 수집기가 요청 본문을 통째로 저장</b>하면 인증코드가 로그에 남습니다.
Datadog·Sentry 등에 마스킹 규칙을 넣었는지 확인하세요.</div>''',
},

'07_fin-credential-reuse.html': {
 'stack': ['금융인증서', 'Refresh Rotation', 'OIDC'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>공동인증서(구 공인인증서) 독점이 풀리면서 <b>금융인증서·간편인증·패스키</b>가 병존합니다.
인증 수단은 늘었지만 &ldquo;한 번 만든 인증 결과를 계속 재사용할 수 있는가&rdquo;라는 문제는 오히려 커졌습니다 —
특히 <b>OAuth/OIDC 토큰</b>이 새로운 재사용 대상입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>전자서명 검증에는 <b>서버가 발급한 일회성 challenge</b> 를 포함시킵니다. 서명값만 캡처해 재사용하지 못하게 합니다.</li>
<li><b>Refresh Token Rotation</b>: 갱신할 때마다 새 refresh 를 발급하고 구 토큰을 무효화합니다. 구 토큰이 다시 쓰이면 <u>탈취로 간주</u>하고 세션 계열 전체를 폐기합니다.</li>
<li>access token 수명은 짧게(5~15분), 민감 거래에는 <b>재인증(step-up)</b> 을 요구합니다.</li>
</ul>
<pre>// refresh 재사용 탐지 — 토큰 계열(family) 단위로 폐기
if (tokenStore.isUsed(refreshJti)) {
    tokenStore.revokeFamily(familyId);        // 탈취 신호
    audit.warn("refresh reuse detected", userId);
    throw new SecurityException("re-authentication required");
}</pre>
<div class="warn">놓치기 쉬운 곳 — <b>인증서 검증에서 만료·폐기(CRL/OCSP) 확인을 빠뜨리는</b> 구현이 흔합니다.
서명이 수학적으로 맞는 것과 그 인증서가 지금 유효한 것은 다릅니다.</div>''',
},

'07_fin-session-reuse.html': {
 'stack': ['JWT', 'Redis Deny List', 'SPA'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>세션 쿠키에서 <b>무상태 JWT</b> 로 옮겨 가면서 새 문제가 생겼습니다 — <b>JWT 는 서버가 취소할 수 없습니다.</b>
로그아웃해도 만료 전까지 유효하고, 권한을 회수해도 토큰 안의 <code>roles</code> 는 그대로입니다.
&ldquo;세션 무효화&rdquo;라는 평가항목이 그냥 사라진 것처럼 보이지만, 실제로는 <b>더 어려워진</b> 것입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>access token 은 <b>짧게(5~15분)</b>, 취소는 <b>refresh 폐기 + Redis deny list</b>(jti 기준, 남은 수명만큼만 보관)로 구현합니다.</li>
<li>중요 변경(비밀번호 변경·권한 회수·기기 해제) 시 <b>사용자 단위 토큰 무효화 시각</b>을 저장하고, 그보다 오래된 <code>iat</code> 토큰을 거부합니다.</li>
<li>SPA 는 토큰을 <code>localStorage</code> 에 두지 말고 <b>HttpOnly·Secure·SameSite 쿠키</b> 로. XSS 실습을 같은 출처에서 제공하는 서비스라면 더욱 그렇습니다.</li>
</ul>
<pre>// 사용자 단위 일괄 무효화 — deny list 보다 가볍다
long cutoff = userRepo.getTokensInvalidAfter(userId);   // 비밀번호 변경 시각 등
if (claims.getIssuedAt().toEpochMilli() &lt; cutoff)
    throw new SecurityException("session invalidated");</pre>
<div class="warn">놓치기 쉬운 곳 — <b>동시 접속 제한</b>은 무상태 구조에서 저절로 사라집니다.
전자금융 환경에서 요구된다면 서버측 세션 레지스트리를 <u>따로</u> 두어야 합니다.</div>''',
},

'07_fin-authmeans-owner.html': {
 'stack': ['오픈뱅킹', '마이데이터', 'MSA'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>인증수단이 <b>기관 경계를 넘습니다.</b> 핀테크 앱이 오픈뱅킹으로 여러 은행 계좌를 다루고,
마이데이터 사업자가 타 기관 정보를 모읍니다. &ldquo;이 인증수단이 이 사람 것인가&rdquo;를
<b>내 시스템 안에서만 확인할 수 없는</b> 구조가 되었습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>사용자 ↔ 인증수단 ↔ <b>계좌 목록</b>의 매핑을 서버가 보관하고, 거래 요청마다 세 가지가 모두 일치하는지 확인합니다.</li>
<li>오픈뱅킹은 <b>access token 의 사용자와 요청 핀테크 이용번호</b>가 일치하는지 검증합니다. 토큰만 맞으면 통과시키는 구현이 실제 사고 사례입니다.</li>
<li>기기 변경·재설치 시 인증수단을 <b>재등록</b>하게 하고, 이전 기기의 등록은 폐기합니다.</li>
</ul>
<pre>// 세 겹 검증 — 하나라도 빠지면 남의 계좌로 이체된다
assertOwner(session.userId, req.fintechUseNo);      // 인증수단 소유자
assertLinked(req.fintechUseNo, req.withdrawAccount); // 인증수단-계좌 연결
assertScope(token, "transfer");                      // 동의 범위</pre>
<div class="warn">놓치기 쉬운 곳 — <b>탈퇴·해지 시 매핑을 지우지 않으면</b> 같은 번호가 재발급될 때
과거 연결이 되살아납니다. 해지 처리에 매핑 정리를 포함하세요.</div>''',
},

'07_fin-auth-step-bypass.html': {
 'stack': ['SPA', 'BFF', 'Deep Link'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>SPA·네이티브 앱에서 <b>화면 전환은 전적으로 클라이언트가 합니다.</b>
서버는 어떤 화면이 떠 있는지 모릅니다. 그래서 &ldquo;인증 화면을 건너뛰었다&rdquo;는 개념 자체가
<b>&ldquo;인증 API 를 호출하지 않고 다음 API 를 호출했다&rdquo;</b> 로 바뀝니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>화면이 아니라 <b>상태 머신을 서버가 보관</b>합니다. <code>txnState: INIT → AUTHED → CONFIRMED</code> 를 서버가 들고, 순서를 어기면 거절합니다.</li>
<li><b>BFF(Backend for Frontend)</b> 를 두면 흐름 제어를 서버로 되돌릴 수 있습니다. 프런트는 다음 단계를 서버에서 받습니다.</li>
<li>딥링크로 내부 화면에 바로 진입하는 경로도 <b>같은 상태 검증</b>을 통과해야 합니다.</li>
</ul>
<pre>// 단계 건너뛰기 차단 — 화면이 아니라 상태로
var txn = txnStore.get(txnId);
if (txn.state != AUTHED)
    throw new SecurityException("인증 단계 미완료: " + txn.state);
txn.state = CONFIRMED;</pre>
<div class="warn">놓치기 쉬운 곳 — <b>상태를 클라이언트가 들고 서버에 보내면</b> 아무것도 막지 못합니다.
상태 토큰을 서명해서 넘기더라도 <u>이전 단계의 유효한 토큰</u>을 재사용할 수 있으므로, 서버 보관이 원칙입니다.</div>''',
},

'07_fin-admin-access.html': {
 'stack': ['제로트러스트', 'IdP SSO', 'Private ALB'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>&ldquo;관리자 페이지는 내부망에서만&rdquo;이라는 전제가 <b>재택근무와 클라우드로 무너졌습니다.</b>
IP 허용목록은 VPN·사무실 IP 를 계속 추가하다 결국 넓어지고, 클라우드에서는 관리 콘솔 자체가 인터넷에 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>관리 평면을 <b>인터넷에서 분리</b>: 내부 전용 ALB + PrivateLink, 또는 <b>제로트러스트 프록시</b>(IAP·Cloudflare Access 류)로 IdP 인증을 먼저 통과시킵니다.</li>
<li>접근에 <b>MFA 를 강제</b>하고, 관리자 행위는 <b>별도 감사 로그</b>로 남깁니다. 일반 트래픽 로그에 섞으면 사후 추적이 어렵습니다.</li>
<li>상시 권한 대신 <b>Just-In-Time 권한</b>(승인 후 N시간)으로 부여합니다.</li>
</ul>
<pre># K8s Ingress — 관리 경로를 별도 인그레스로 분리하고 인증을 앞단에 둔다
metadata:
  annotations:
    nginx.ingress.kubernetes.io/auth-url: "https://idp.internal/oauth2/auth"
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.40.0.0/16"
spec:
  rules:
    - host: admin.fin.internal        # 공개 도메인과 분리</pre>
<div class="warn">놓치기 쉬운 곳 — <b>액추에이터·메트릭·스웨거</b>가 관리자 페이지와 같은 부류입니다.
<code>/actuator/env</code> 는 환경변수를, <code>/swagger-ui</code> 는 전체 API 구조를 그대로 보여 줍니다.</div>''',
},

'07_fin-password-change.html': {
 'stack': ['재인증', '세션 폐기', 'Argon2id'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>비밀번호 변경은 <b>계정 탈취의 마지막 단계</b>입니다. 공격자가 세션을 잡은 뒤 비밀번호를 바꿔
정당한 소유자를 밀어내는 흐름이라, &ldquo;변경 기능의 보안&rdquo;은 곧 <b>탈취 복구 가능성</b>의 문제입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>변경 시 <b>현재 비밀번호 재확인</b>(step-up). 세션이 있다는 사실만으로 허용하지 않습니다.</li>
<li>변경 성공 시 <b>다른 모든 세션·토큰을 폐기</b>하고 등록된 연락처로 <b>알림</b>을 보냅니다. 알림은 되돌릴 기회를 줍니다.</li>
<li>저장은 <b>Argon2id</b>(또는 bcrypt) 로. 금융권 레거시에 아직 남아 있는 <code>SHA-256(salt+pw)</code> 는 GPU 공격에 약합니다.</li>
</ul>
<pre>// 변경 = 재인증 + 전 세션 폐기 + 알림, 셋이 한 묶음
requireRecentAuth(session, Duration.ofMinutes(5));
userRepo.updatePassword(userId, argon2.hash(newPw));
tokenStore.revokeAllForUser(userId);
notifier.send(user.email(), "비밀번호가 변경되었습니다");</pre>
<div class="warn">놓치기 쉬운 곳 — <b>변경 직후 자기 세션까지 끊어 버리면</b> 사용자가 당황합니다.
현재 세션은 새 토큰으로 교체하고 나머지만 폐기하는 것이 올바른 동작입니다.</div>''',
},

'07_fin-predictable-reset.html': {
 'stack': ['CSPRNG', '일회성 토큰', 'Rate Limit'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>초기화 비밀번호를 <b>생년월일·전화번호 뒷자리</b>로 만드는 관행은 여전히 레거시에 남아 있습니다.
현대적 흐름은 임시 비밀번호를 아예 만들지 않고 <b>일회성 재설정 링크</b>를 보내는 것입니다 —
비밀번호가 채널(SMS·메일)을 타지 않으므로 유출 지점이 하나 줄어듭니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>토큰은 <b>CSPRNG 128비트 이상</b>, <b>단일 사용</b>, <b>짧은 만료</b>(15~30분). DB 에는 <u>해시로</u> 저장합니다.</li>
<li>요청 응답은 <b>계정 존재 여부와 무관하게 동일</b>해야 합니다. "가입되지 않은 이메일"은 계정 열거 경로입니다.</li>
<li>재설정 요청·검증 모두 <b>레이트리밋</b>을 겁니다.</li>
</ul>
<pre>token = secrets.token_urlsafe(32)                  # 256비트
db.save(user_id, sha256(token), expires=now()+15*60, used=False)
send_link(f"https://bank.example/reset?t={token}")  # DB엔 해시만 남는다</pre>
<div class="warn">놓치기 쉬운 곳 — <b>재설정 링크가 Referer 헤더로 외부에 샙니다.</b>
재설정 페이지에 외부 스크립트(광고·분석)가 있으면 토큰이 그대로 전달됩니다.
<code>Referrer-Policy: no-referrer</code> 와 외부 태그 제거가 함께 필요합니다.</div>''',
},

'07_fin-guessable-cred.html': {
 'stack': ['NIST 800-63B', '유출 목록 대조', '규제 충돌'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>글로벌 기준(NIST SP 800-63B)은 <b>복잡도 규칙과 주기적 변경 강제를 권장하지 않습니다.</b>
사용자가 <code>Password1!</code> → <code>Password2!</code> 로 바꾸는 행동을 유발해 오히려 약해지기 때문입니다.
대신 <b>길이 우선 + 유출 목록 대조</b>를 권합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>길이를 늘리고(12자 이상) 문자 구성 강제는 완화</b>, 대신 <b>유출된 비밀번호 목록과 대조</b>합니다(HIBP k-anonymity API 또는 자체 목록).</li>
<li>사전 단어·반복·키보드 패턴은 <b>zxcvbn</b> 같은 추정 엔트로피로 거릅니다. 정규식 규칙보다 정확합니다.</li>
<li>궁극적으로는 <b>패스키(FIDO2)</b> 로 비밀번호 자체를 없애는 방향입니다.</li>
</ul>
<pre>// 유출 목록 대조 — 앞 5자리만 보내고 나머지는 로컬 비교(k-anonymity)
String sha1 = sha1Hex(password).toUpperCase();
List&lt;String&gt; suffixes = hibp.range(sha1.substring(0, 5));
if (suffixes.contains(sha1.substring(5)))
    reject("이미 유출된 비밀번호입니다");</pre>
<div class="warn">규제 충돌에 주의 — <b>국내 전자금융감독규정은 주기적 변경을 요구</b>합니다.
글로벌 권고와 어긋나므로, <u>국내 금융 서비스는 규정을 따르되</u> 유출 목록 대조를 <b>추가</b>하는 식으로
두 기준을 함께 만족시키는 것이 현실적인 해법입니다.</div>''',
},

'07_fin-realname.html': {
 'stack': ['비대면 실명확인', 'eKYC', '딥페이크'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>접근매체 발급이 <b>비대면(eKYC)</b> 으로 옮겨 가면서 실명확인의 무게중심이 바뀌었습니다.
신분증 사본 제출 → <b>신분증 진위확인 API + 얼굴 대조 + 계좌 인증</b> 의 다중 확인 구조입니다.
그리고 <b>생성형 AI 로 만든 위조 신분증·딥페이크 영상</b>이 새로운 위협으로 올라왔습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>신분증은 OCR 로 읽는 데 그치지 말고 <b>발급기관 진위확인</b>(정부24·금융결제원 등)을 거칩니다. 사본 위조는 OCR 을 통과합니다.</li>
<li>얼굴 대조에는 <b>라이브니스 검사(수동/능동)</b> 를 넣습니다. 사진·영상 재생·딥페이크를 거르는 핵심 단계입니다.</li>
<li>확인 결과와 근거는 <b>보존 의무 기간 동안 증적으로</b> 남깁니다 — 분쟁 시 실명확인 이행을 증명해야 합니다.</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — <b>수집한 신분증 이미지와 얼굴 정보는 민감정보·고유식별정보</b>입니다.
개인정보 보호법상 <u>별도 동의와 암호화 저장</u>이 필요하고, 목적 달성 후 파기해야 합니다.
eKYC 를 도입하며 개인정보 처리방침을 갱신하지 않는 실수가 흔합니다.</div>''',
},

# ══════════════════════════ 전송 구간 · TLS ══════════════════════════
'07_fin-transport-encryption.html': {
 'stack': ['ALB 종단', '서비스 메시', 'HSTS'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>클라우드에서는 TLS 가 대개 <b>ALB·CloudFront 에서 종단</b>됩니다. 겉보기에는 HTTPS 이지만
<b>로드밸런서 뒤 구간이 평문</b>인 구성이 매우 흔합니다. 평가항목은 &ldquo;통신구간 암호화&rdquo;인데,
점검 대상이 <u>외부 구간만</u>인 것으로 오해하기 쉽습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>ALB → 타깃 구간도 <b>HTTPS 로</b> 설정합니다. 사설 인증서라도 평문보다 낫습니다.</li>
<li>MSA 내부는 <b>서비스 메시 mTLS</b>(Istio <code>PeerAuthentication: STRICT</code>)로 자동 암호화합니다.</li>
<li>외부에는 <b>HSTS + preload</b>, 리다이렉트는 <b>301 로 HTTPS 강제</b>. 평문 요청 자체를 없앱니다.</li>
</ul>
<pre># Istio — 네임스페이스 전체 mTLS 강제
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata: { name: default, namespace: fin-core }
spec:
  mtls: { mode: STRICT }        # PERMISSIVE 는 평문도 받는다</pre>
<div class="warn">놓치기 쉬운 곳 — Istio 의 기본값은 <b>PERMISSIVE</b> 입니다.
"메시를 깔았으니 mTLS 가 된다"고 생각하지만 평문 트래픽이 그대로 통과합니다. <code>STRICT</code> 로 바꿨는지 확인하세요.</div>''',
},

'07_fin-cert-integrity.html': {
 'stack': ['인증서 피닝', 'ACME 자동갱신', 'CT 로그'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>인증서 <b>자동 갱신(ACME/ACM)</b>이 표준이 되면서 피닝과 충돌이 생겼습니다.
90일마다 인증서가 바뀌는데 앱에 고정 핀을 박아 두면 <b>갱신 시점에 앱이 통째로 죽습니다.</b>
실제로 이 사고로 서비스가 중단된 금융 앱 사례가 여럿 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>리프 인증서가 아니라 중간 CA 또는 공개키(SPKI)에 피닝</b>합니다. 갱신되어도 키가 유지되면 핀이 살아 있습니다.</li>
<li><b>백업 핀을 반드시 포함</b>합니다(차기 키). 핀이 하나뿐이면 되돌릴 방법이 없습니다.</li>
<li>Android 는 <b>Network Security Configuration</b>, iOS 는 <b>ATS + 코드 피닝</b>으로 선언합니다. 서버 측은 <b>CT(인증서 투명성) 로그 모니터링</b>으로 오발급을 탐지합니다.</li>
</ul>
<pre>&lt;!-- Android: 핀 2개(현재+백업)와 만료일을 함께 --&gt;
&lt;pin-set expiration="2027-06-30"&gt;
  &lt;pin digest="SHA-256"&gt;k3rNk9bT1r8p...=&lt;/pin&gt;  &lt;!-- 현재 --&gt;
  &lt;pin digest="SHA-256"&gt;Q2xVd8mZ4fA1...=&lt;/pin&gt;  &lt;!-- 백업 --&gt;
&lt;/pin-set&gt;</pre>
<div class="warn">놓치기 쉬운 곳 — <b>피닝은 앱 업데이트 없이 못 고칩니다.</b>
앱 심사·배포에 며칠이 걸리므로, 핀 만료일은 인증서 갱신 주기보다 <u>넉넉히</u> 잡고
원격 설정으로 피닝을 끌 수 있는 킬스위치를 두는 팀도 많습니다.</div>''',
},

'07_fin-tls-protocol.html': {
 'stack': ['ALB 보안정책', 'TLS 1.3', 'IaC'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>클라우드에서는 프로토콜 버전을 <b>웹서버 설정 파일이 아니라 로드밸런서의 보안 정책 이름</b>으로 정합니다.
<code>ssl_protocols</code> 를 아무리 고쳐도 앞단 ALB 가 TLS 1.0 을 받고 있으면 의미가 없습니다 —
<b>점검 지점이 옮겨 갔다</b>는 것이 이 항목의 핵심 변화입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>ALB 리스너에 <b>TLS 1.2 이상 정책</b>을 적용합니다(<code>ELBSecurityPolicy-TLS13-1-2-2021-06</code> 등).</li>
<li>CloudFront 는 <b>Minimum Protocol Version</b> 을 별도로 설정합니다 — ALB 와 따로 놉니다.</li>
<li>정책을 <b>IaC 로 고정</b>하고, 콘솔에서 바꿔도 다음 배포에 되돌아가게 합니다.</li>
</ul>
<pre>resource "aws_lb_listener" "https" {
  protocol   = "HTTPS"
  ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"   # 1.2/1.3 만
  # 레거시 단말 호환이 필요하면 별도 리스너로 분리하고 기한을 정해 폐기
}</pre>
<div class="warn">놓치기 쉬운 곳 — <b>내부 서비스·배치 API·파트너 연동 엔드포인트</b>는 점검에서 빠지기 쉽습니다.
외부 공개 도메인만 스캔하고 끝내면 남은 TLS 1.0 을 못 찾습니다.</div>''',
},

'07_fin-tls-cipher.html': {
 'stack': ['ALB 정책', 'PFS', '사후 양자'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>관리형 로드밸런서에서는 <b>암호 스위트를 개별로 켜고 끌 수 없습니다.</b>
AWS·GCP 모두 <b>미리 정의된 정책 묶음</b> 중에서 고르는 방식이라, 점검 결과가
&ldquo;어떤 스위트가 열렸는가&rdquo;가 아니라 <b>&ldquo;어떤 정책을 골랐는가&rdquo;</b> 로 바뀝니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>PFS(전방향 비밀성)</b> 를 보장하는 ECDHE 계열만 남기는 정책을 고릅니다. RSA 키 교환은 서버 키 유출 시 <u>과거 트래픽까지</u> 복호화됩니다.</li>
<li>TLS 1.3 은 취약 스위트가 규격에서 제거되어 있어, <b>1.3 전용 정책</b>이 가장 단순한 해법입니다.</li>
<li>실제 노출은 <code>sslscan</code>·<code>testssl.sh</code> 로 <b>엔드포인트에서 확인</b>합니다. 설정과 실제가 다른 경우가 많습니다.</li>
</ul>
<pre>$ testssl.sh --severity HIGH https://bank.example
 NULL ciphers (no encryption)      not offered (OK)
 Anonymous NULL ciphers            not offered (OK)
 Export ciphers                    not offered (OK)
 3DES / RC4                        not offered (OK)
 PFS                               offered (OK) — ECDHE only</pre>
<div class="warn">앞을 내다본다면 — 금융권은 <b>사후 양자 암호(PQC) 전환</b> 논의가 시작됐습니다.
&ldquo;지금 저장해 두고 나중에 복호화&rdquo;(harvest-now, decrypt-later) 위협 때문에
장기 보존 가치가 큰 거래 데이터부터 <u>하이브리드 키 교환</u> 검토가 권고됩니다.</div>''',
},

'07_fin-tls-component.html': {
 'stack': ['컨테이너 이미지', 'SBOM', '이미지 스캔'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>OpenSSL 은 더 이상 서버에 <code>yum update</code> 로 패치하는 대상이 아닙니다.
<b>컨테이너 베이스 이미지에 박혀서 배포</b>되므로, 취약점 대응은 <b>이미지 재빌드 + 재배포</b> 입니다.
그리고 실행 중인 컨테이너를 패치해도 <u>다음 배포에 되돌아갑니다.</u></p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>SBOM 을 생성·보관</b>합니다(Syft·CycloneDX). Heartbleed 급 취약점이 나왔을 때 <u>어느 이미지에 무슨 버전이 들어 있는지</u>를 몇 분 안에 답할 수 있어야 합니다.</li>
<li>CI 에 <b>이미지 취약점 스캔</b>(Trivy·ECR 스캔)을 걸고, 기준 초과 시 배포를 막습니다.</li>
<li>베이스 이미지를 <b>정기 재빌드</b>합니다. 코드가 안 바뀌어도 베이스는 늙습니다.</li>
</ul>
<pre># CI — 취약점이 있으면 배포 중단
$ syft fin-core:1.42 -o cyclonedx-json &gt; sbom.json
$ trivy image --severity HIGH,CRITICAL --exit-code 1 fin-core:1.42
  openssl  3.0.11  CVE-2024-XXXX  HIGH  → fixed in 3.0.13
$ echo "build failed"   # 게이트가 없으면 스캔은 장식이다</pre>
<div class="warn">놓치기 쉬운 곳 — <b>애플리케이션이 정적 링크한 TLS 라이브러리</b>는 OS 패키지 목록에 안 잡힙니다.
Go 바이너리나 번들된 Node 모듈 안의 취약 버전은 SBOM 으로만 보입니다.</div>''',
},

'07_fin-tls-renegotiation.html': {
 'stack': ['TLS 1.3', 'ALB', 'DoS'],
 'html': '''<h4>어디가 달라졌나</h4>
<p><b>TLS 1.3 에는 재협상 기능 자체가 없습니다.</b> 규격에서 제거되었기 때문에,
1.3 전용으로 운영하면 이 항목은 구조적으로 해소됩니다.
문제는 <b>1.2 를 함께 지원하는 동안</b>이며, 대부분의 금융 서비스가 여기에 해당합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>TLS 1.2 구간에서는 <b>클라이언트 개시 재협상을 거부</b>합니다. 관리형 LB(ALB·CloudFront)는 기본적으로 거부하므로, 직접 운영하는 nginx·HAProxy 가 점검 대상입니다.</li>
<li>재협상은 <b>비대칭 연산 증폭 DoS</b> 경로이기도 합니다 — 적은 대역폭으로 서버 CPU 를 소모시킵니다.</li>
<li>가능하면 <b>TLS 1.3 전용 정책</b>으로 옮겨 문제를 없앱니다.</li>
</ul>
<pre># 직접 운영하는 nginx 라면 (OpenSSL 1.0.2 이후 기본 거부지만 명시해 둔다)
ssl_protocols TLSv1.2 TLSv1.3;
# 1.3 전용이 가능하면:
# ssl_protocols TLSv1.3;</pre>
<div class="warn">놓치기 쉬운 곳 — <b>ALB 뒤의 오리진 서버</b>는 점검에서 빠집니다.
외부에서 스캔하면 ALB 만 보이므로, 내부 오리진은 <u>별도로</u> 확인해야 합니다.</div>''',
},

# ══════════════════════════ 모바일 앱 ══════════════════════════
'07_fin-app-integrity.html': {
 'stack': ['Play Integrity', 'App Attest', '서버 검증'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>앱이 스스로 위·변조를 탐지하던 방식은 <b>공격자가 그 탐지 코드를 지우면 끝</b>이었습니다.
현재 표준은 <b>OS 가 보증하고 서버가 검증</b>하는 구조입니다 —
Android <b>Play Integrity API</b>, iOS <b>App Attest / DeviceCheck</b>.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>앱이 무결성 토큰을 받아 서버로 보내고, <b>서버가 구글·애플에 검증</b>합니다. 판정 주체가 단말 밖으로 나가는 것이 핵심입니다.</li>
<li>검증 대상: 패키지명·서명 인증서 해시·<b>정품 설치 경로 여부</b>(사이드로딩 탐지)·기기 무결성.</li>
<li>실패 시 <b>즉시 차단이 아니라 위험 점수로</b> 다룹니다 — 오탐이 있어 정상 사용자를 막을 수 있습니다.</li>
</ul>
<pre>// 서버에서 검증 — 앱의 "괜찮다"는 말을 믿지 않는다
IntegrityTokenResponse r = playIntegrity.decode(token);
if (!r.appRecognitionVerdict().equals("PLAY_RECOGNIZED"))
    risk.add(40, "비정품 앱 또는 변조");
if (!r.deviceRecognitionVerdict().contains("MEETS_DEVICE_INTEGRITY"))
    risk.add(30, "기기 무결성 미충족");</pre>
<div class="warn">놓치기 쉬운 곳 — <b>토큰을 앱에서 받아 그대로 서버에 넘기고 서버는 파싱만 하는</b> 구현이 흔합니다.
반드시 <u>구글/애플 API 로 원격 검증</u>해야 하며, nonce 를 서버가 발급해 재사용도 막아야 합니다.</div>''',
},

'07_fin-device-rooting.html': {
 'stack': ['Play Integrity', '위험 기반 인증', 'RASP'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>루팅 탐지는 <b>본질적으로 우회 가능</b>합니다. Magisk·Zygisk 계열은 탐지 회피를 전제로 만들어져 있고,
클라이언트 로직은 결국 공격자의 기기 위에서 돕니다. 그래서 현대적 접근은
<b>&ldquo;막는다&rdquo;에서 &ldquo;위험을 점수로 반영한다&rdquo;</b> 로 바뀌었습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>탐지 결과를 <b>서버의 위험 엔진 입력</b>으로 씁니다. 루팅 단말은 이체 한도를 낮추거나 추가 인증을 요구합니다.</li>
<li>클라이언트 자체 탐지 대신 <b>Play Integrity 의 기기 무결성 판정</b>을 우선 신뢰합니다.</li>
<li>탐지 신호를 <b>기기·행동 지문과 결합</b>합니다(신규 기기 + 루팅 + 심야 대액 이체 = 고위험).</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — <b>루팅 탐지 실패 = 즉시 앱 종료</b>는 사용자 불만과 우회 동기를 동시에 키웁니다.
게다가 커스텀 ROM 을 쓰는 정상 사용자가 금융 서비스에서 배제됩니다.
<u>차단이 아니라 단계적 제한</u>이 현재 권장되는 설계입니다.</div>''',
},

'07_fin-obfuscation.html': {
 'stack': ['R8 / ProGuard', '매핑 파일', 'Flutter·RN'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>Android 는 <b>R8</b> 이 기본 축약·난독화기입니다. 그런데 <b>크로스플랫폼 프레임워크가 늘면서</b>
난독화 범위가 애매해졌습니다 — <b>React Native 의 JS 번들</b>과 <b>Flutter 의 Dart 스냅샷</b>은
R8 이 건드리지 않으므로, 자바 계층만 난독화하고 정작 비즈니스 로직은 평문인 경우가 많습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>RN 은 <b>Hermes 바이트코드 + 별도 JS 난독화</b>, Flutter 는 <code>--obfuscate --split-debug-info</code> 로 심볼을 분리합니다.</li>
<li><b>매핑 파일(mapping.txt)</b> 은 난독화 해제 열쇠입니다 — 소스 저장소가 아니라 <b>접근 통제된 별도 저장소</b>에 보관하고 빌드별로 버전 관리합니다.</li>
<li>난독화는 <b>지연 수단이지 보호 수단이 아닙니다.</b> 비밀값은 어차피 빼내집니다 — 서버에 두는 것이 원칙입니다.</li>
</ul>
<pre># Flutter — 심볼을 빼서 따로 보관
$ flutter build apk --obfuscate --split-debug-info=build/symbols
# 크래시 리포트 복원은 이 심볼로만 가능하므로 유실 주의</pre>
<div class="warn">놓치기 쉬운 곳 — 난독화를 켜면 <b>리플렉션·JSON 역직렬화가 조용히 깨집니다.</b>
<code>-keep</code> 규칙을 넣다가 결국 핵심 클래스를 전부 예외 처리해 난독화가 무력해지는 일이 흔합니다.</div>''',
},

'07_fin-debug-detection.html': {
 'stack': ['Frida 탐지', 'RASP', '서버 상관분석'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>오늘날 모바일 분석의 표준 도구는 <b>Frida</b> 입니다. 디버거 연결(<code>ptrace</code>) 탐지만으로는
동적 계측을 잡지 못합니다. 게다가 탐지 코드를 <b>Frida 로 무력화</b>하는 스크립트가 공개되어 있어
클라이언트 단독 방어는 한계가 분명합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>탐지 신호를 <b>여러 개 겹치고</b>(디버거·계측 라이브러리 로드·후킹 흔적·타이밍 이상), <b>서버로 전송</b>해 상관분석합니다.</li>
<li>탐지 시 <b>즉시 반응하지 않습니다.</b> 바로 종료하면 공격자가 어느 코드가 탐지기인지 즉시 알아냅니다 — 지연·서버측 제한이 유효합니다.</li>
<li>상용 <b>RASP</b> 도입 시에도 서버측 이상거래탐지(FDS)와 연동해야 의미가 있습니다.</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — 이 항목은 <b>완전한 방어가 불가능하다는 전제</b>에서 설계해야 합니다.
목표는 &ldquo;분석 불가&rdquo;가 아니라 <b>&ldquo;비용을 올리고, 시도를 서버가 알아채는 것&rdquo;</b> 입니다.
따라서 탐지 이벤트가 <u>서버 로그에 남고 FDS 가 소비하는지</u>가 실질적인 점검 포인트입니다.</div>''',
},

'07_fin-memory-protection.html': {
 'stack': ['Keystore/Enclave', 'GC 언어 한계', 'TEE'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>Java·Kotlin·Swift 같은 <b>GC 언어에서는 메모리를 확실히 지울 수 없습니다.</b>
<code>String</code> 은 불변이고 GC 가 언제 회수할지 모릅니다. 그래서 &ldquo;사용 후 즉시 삭제&rdquo;라는 조치는
<b>구현 가능한 범위</b>를 정확히 알고 접근해야 합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>비밀값은 <b><code>char[]</code>·<code>ByteArray</code></b> 로 다루고 사용 후 <b>명시적으로 0 으로 채웁니다</b>. <code>String</code> 은 피합니다.</li>
<li>가장 좋은 방법은 <b>평문을 앱 메모리에 올리지 않는 것</b>입니다 — <b>Android Keystore / iOS Secure Enclave</b> 안에서 서명·복호화를 수행하고 결과만 받습니다. 키는 하드웨어 밖으로 나오지 않습니다.</li>
<li>생체인증 연동 시 <code>setUserAuthenticationRequired(true)</code> 로 키 사용 자체를 인증에 묶습니다.</li>
</ul>
<pre>// 키가 앱 메모리에 존재하지 않는 구조
KeyGenParameterSpec spec = new KeyGenParameterSpec.Builder("txn-sign",
        KeyProperties.PURPOSE_SIGN)
    .setUserAuthenticationRequired(true)       // 생체인증 후에만 사용
    .setIsStrongBoxBacked(true)                // 하드웨어 보안 모듈
    .build();</pre>
<div class="warn">놓치기 쉬운 곳 — <b>크래시 덤프와 힙 스냅샷</b>에 비밀값이 그대로 담깁니다.
Firebase Crashlytics 같은 도구가 덤프를 외부로 보내므로, 수집 범위를 확인해야 합니다.</div>''',
},

'07_fin-device-storage.html': {
 'stack': ['Keystore', 'EncryptedSharedPrefs', '백업 제외'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>단말 저장은 <b>앱 샌드박스 밖으로 새는 경로</b>가 많아졌습니다 —
<b>자동 백업</b>(Android Auto Backup, iCloud), <b>기기 이전</b>, <b>스크린 캐시</b>, <b>로그 수집기</b>.
&ldquo;내부 저장소에 뒀으니 안전하다&rdquo;는 전제가 더 이상 성립하지 않습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>키는 <b>Android Keystore / iOS Keychain</b> 에 두고, 데이터는 <b>EncryptedSharedPreferences·SQLCipher</b> 로 암호화합니다.</li>
<li><b>백업에서 제외</b>합니다 — <code>android:allowBackup="false"</code> 또는 <code>dataExtractionRules</code>, iOS 는 Keychain 항목의 <code>ThisDeviceOnly</code> 접근성.</li>
<li>토큰·세션은 <b>만료와 함께 삭제</b>하고, 로그아웃 시 로컬 캐시를 정리합니다.</li>
</ul>
<pre>&lt;!-- Android 12+ : 백업·기기이전에서 민감 데이터 제외 --&gt;
&lt;data-extraction-rules&gt;
  &lt;cloud-backup&gt;&lt;exclude domain="sharedpref" path="auth.xml"/&gt;&lt;/cloud-backup&gt;
  &lt;device-transfer&gt;&lt;exclude domain="database" path="txn.db"/&gt;&lt;/device-transfer&gt;
&lt;/data-extraction-rules&gt;</pre>
<div class="warn">놓치기 쉬운 곳 — <b>WebView 가 쓰는 저장소</b>(쿠키·localStorage·캐시)는 별도입니다.
하이브리드 앱에서 인증 토큰이 WebView localStorage 에 남아 있는 경우가 실제로 자주 발견됩니다.</div>''',
},

'07_fin-screen-protection.html': {
 'stack': ['FLAG_SECURE', 'iOS 한계', '화면 공유'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>위협이 <b>스크린샷에서 실시간 화면 공유</b>로 옮겨 갔습니다.
보이스피싱에서 <b>원격제어 앱으로 피해자 화면을 보며</b> 이체를 유도하는 수법이 일반화되어,
정적인 캡처 차단만으로는 부족합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>Android 는 <code>FLAG_SECURE</code> 로 캡처·미러링·최근 앱 미리보기를 한 번에 막습니다.</li>
<li><b>iOS 에는 동등한 API 가 없습니다.</b> <code>UIScreen.isCaptured</code> 로 <u>녹화·미러링 중임을 감지</u>해 민감 화면을 가리는 우회 구현이 필요합니다.</li>
<li><b>원격제어 앱 동작 탐지</b>(접근성 서비스 오용·화면 공유 세션)를 서버 위험 신호로 보냅니다.</li>
</ul>
<pre>// iOS — 캡처 상태를 관찰해 민감 화면을 가린다
NotificationCenter.default.addObserver(forName: UIScreen.capturedDidChangeNotification,
                                       object: nil, queue: .main) { _ in
    blurOverlay.isHidden = !UIScreen.main.isCaptured
}</pre>
<div class="warn">놓치기 쉬운 곳 — <code>FLAG_SECURE</code> 를 걸면 <b>정상적인 화면 공유 고객지원</b>도 막힙니다.
콜센터가 화면을 함께 보며 안내하는 서비스가 있다면 화면별로 정책을 나눠야 합니다.</div>''',
},

'07_fin-background-screen.html': {
 'stack': ['앱 전환기', 'FLAG_SECURE', '생명주기'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>최근 앱 목록(앱 전환기)의 미리보기는 <b>OS 가 자동으로 캡처</b>해 디스크에 저장합니다.
잠금화면에서도 보이고, 기기를 잠깐 빌려준 사이에 <b>잔액·계좌번호가 그대로 노출</b>됩니다.
개발자가 명시적으로 막지 않으면 기본값이 &ldquo;캡처함&rdquo;입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>Android 는 <code>FLAG_SECURE</code> 하나로 미리보기까지 차단됩니다.</li>
<li>iOS 는 <b>생명주기 이벤트에 맞춰 가림막을 올립니다</b> — <code>sceneWillResignActive</code> 에서 오버레이를 띄우고 <code>sceneDidBecomeActive</code> 에서 내립니다.</li>
<li>SwiftUI·Compose 등 선언형 UI 에서는 <b>씬 단위</b>로 걸어야 합니다. 뷰 컨트롤러 기준 코드가 동작하지 않는 경우가 있습니다.</li>
</ul>
<pre>// iOS — 백그라운드 진입 직전에 가린다 (순서가 중요: resignActive 에서 해야 캡처 전이다)
func sceneWillResignActive(_ scene: UIScene) {
    privacyOverlay.frame = window!.bounds
    window?.addSubview(privacyOverlay)
}
func sceneDidBecomeActive(_ scene: UIScene) { privacyOverlay.removeFromSuperview() }</pre>
<div class="warn">놓치기 쉬운 곳 — <code>sceneDidEnterBackground</code> 에서 가리면 <b>이미 늦습니다.</b>
OS 는 <code>willResignActive</code> 직후에 스냅샷을 뜹니다.</div>''',
},

'07_fin-input-protection.html': {
 'stack': ['OS 보안 키보드', '접근성 오용', '한국 특수성'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>국내 금융앱의 <b>자체 보안 키보드</b>는 글로벌 관행과 다른 한국 특유의 통제입니다.
현재 Android·iOS 는 OS 차원에서 <b>비밀번호 입력 시 서드파티 키보드를 차단</b>하는 수단을 제공하므로,
자체 구현의 상대적 이점이 줄었고 <b>접근성·사용성 문제</b>가 부각되고 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>Android <code>android:inputType="textPassword"</code> + <code>imeOptions="flagNoPersonalizedLearning"</code>, iOS <code>isSecureTextEntry</code> 로 OS 보호를 먼저 받습니다.</li>
<li>실제 위협은 키로깅보다 <b>접근성 서비스 오용</b>입니다 — 악성 앱이 접근성 권한으로 화면을 읽고 입력을 대신합니다. <b>비정상 접근성 서비스 탐지</b>가 더 실효적입니다.</li>
<li>궁극적으로는 <b>생체인증·패스키로 입력 자체를 없애는</b> 방향입니다.</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — <b>자체 보안 키보드는 스크린리더 사용자를 배제</b>하는 경우가 많습니다.
장애인차별금지법상 접근성 의무와 충돌할 수 있으므로, 대체 입력 수단을 함께 제공해야 합니다.</div>''',
},

'07_fin-deeplink.html': {
 'stack': ['App Links', 'Universal Links', 'PKCE'],
 'html': '''<h4>어디가 달라졌나</h4>
<p><b>커스텀 스킴(<code>mybank://</code>)은 누구나 선점할 수 있습니다.</b> 악성 앱이 같은 스킴을 등록하면
OS 가 선택 창을 띄우거나 그쪽으로 보내 버립니다. 그래서 <b>검증된 딥링크</b>
(Android <b>App Links</b>, iOS <b>Universal Links</b>)가 표준이 되었습니다 — 도메인 소유 증명이 필요해 선점이 불가능합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><code>assetlinks.json</code> / <code>apple-app-site-association</code> 을 도메인에 게시하고 <b>autoVerify</b> 를 켭니다.</li>
<li>딥링크 파라미터는 <b>전부 신뢰할 수 없는 입력</b>입니다. 이체 금액·수취계좌를 딥링크로 받아 화면에 미리 채우는 설계는 피싱에 직결됩니다.</li>
<li>OAuth 리다이렉트에는 <b>PKCE</b> 를 적용합니다. 인가코드가 탈취돼도 <code>code_verifier</code> 없이는 못 씁니다.</li>
</ul>
<pre>&lt;!-- 검증된 App Link — 스킴이 아니라 도메인 소유로 증명한다 --&gt;
&lt;intent-filter android:autoVerify="true"&gt;
  &lt;data android:scheme="https" android:host="m.bank.example" /&gt;
&lt;/intent-filter&gt;</pre>
<div class="warn">놓치기 쉬운 곳 — <b>App Links 를 켜도 커스텀 스킴을 같이 남겨 두면</b> 우회 경로가 유지됩니다.
레거시 호환 때문에 남긴 스킴이 실제 공격 경로가 됩니다 — 기한을 정해 제거하세요.</div>''',
},

'07_fin-malware-protection.html': {
 'stack': ['Play Protect', '접근성 오용', 'FDS 연동'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>모바일 악성코드의 주력이 <b>보이스피싱 연계형</b>으로 바뀌었습니다.
피해자가 스스로 설치하는 <b>사칭 앱</b>이 <b>접근성 권한</b>을 받아 화면을 읽고 입력을 대신하며,
발신 전화를 가로채 &ldquo;은행 상담원&rdquo;에게 연결합니다. 전통적 &ldquo;백신 탑재&rdquo;로는 막히지 않습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>앱이 <b>비정상 접근성 서비스·오버레이 권한·통화 리디렉션</b>을 탐지해 서버에 보고합니다.</li>
<li><b>사이드로딩 탐지</b>(설치 출처가 스토어가 아님)를 Play Integrity 로 확인합니다.</li>
<li>탐지 신호를 <b>FDS 에 연동</b>합니다 — 악성앱 신호 + 신규 수취계좌 + 대액 이체는 즉시 보류 대상입니다.</li>
</ul>
<pre>// 화면 위에 덧씌우는 앱이 있는지 (오버레이 피싱)
if (Settings.canDrawOverlays(ctx) &amp;&amp; hasSuspiciousOverlayApp())
    risk.add(50, "오버레이 권한 보유 앱 탐지");
if (accessibilityEnabled() &amp;&amp; !isKnownAssistiveApp())
    risk.add(60, "비인가 접근성 서비스");</pre>
<div class="warn">놓치기 쉬운 곳 — <b>접근성 서비스는 장애인 보조 기술의 정당한 기능</b>입니다.
무조건 차단하면 스크린리더 사용자가 금융 서비스를 못 씁니다. <u>허용 목록 기반</u>으로 판단해야 합니다.</div>''',
},

'07_fin-security-program.html': {
 'stack': ['플러그인 종말', 'EDR', 'SaaS 전환'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>브라우저가 <b>NPAPI·ActiveX 를 완전히 제거</b>하면서 설치형 보안 플러그인 모델이 사실상 끝났습니다.
금융권도 <b>플러그인 없는 웹(no-plugin)</b> 으로 전환 중이며, 이 항목의 무게중심은
&ldquo;보안프로그램이 살아 있는가&rdquo;에서 <b>&ldquo;단말 보안을 무엇으로 보증하는가&rdquo;</b> 로 이동했습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>PC 는 <b>EDR·MDM 으로 상태를 확인</b>하고, 미충족 단말은 접근을 제한합니다(장치 신뢰 기반 접근).</li>
<li>보안 기능은 <b>서버측·브라우저 표준 기능</b>으로 대체합니다 — TLS·CSP·SameSite·WebAuthn.</li>
<li>남아 있는 설치형 모듈은 <b>버전·구동 상태를 서버가 확인</b>하고, 임의 종료 시 거래를 제한합니다.</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — <b>보안프로그램 자체가 공격 표면</b>입니다.
관리자 권한으로 상주하는 모듈의 취약점은 곧 단말 장악이며, 실제로 국내 금융 보안 모듈에서
원격코드실행 취약점이 보고된 사례가 있습니다. <u>탑재 여부만큼 패치 상태</u>가 중요합니다.</div>''',
},

'07_fin-secprog-update.html': {
 'stack': ['자동 업데이트', '서명 검증', '공급망'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>업데이트 채널은 <b>가장 매력적인 공급망 공격 경로</b>입니다.
관리자 권한으로 실행되는 모듈에 &ldquo;정상 업데이트&rdquo;로 위장한 코드를 밀어 넣으면 전 고객 단말이 한 번에 감염됩니다.
실제로 국내에서 <b>업데이트 서버를 경유한 대규모 침해</b>가 발생한 전례가 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>업데이트 패키지는 <b>코드 서명 검증 후에만</b> 설치합니다. TLS 로 받았다는 것과 내용이 정품인 것은 다릅니다.</li>
<li>버전 <b>다운그레이드를 거부</b>합니다(롤백 공격 방지). 서명이 유효해도 과거 취약 버전이면 막습니다.</li>
<li>업데이트 서버·빌드 파이프라인에 <b>SLSA 수준의 공급망 통제</b>를 적용하고, 서명 키는 <b>HSM</b> 에 둡니다.</li>
</ul>
<pre># 검증 순서: 서명 → 버전 → 설치
verify_signature(pkg, pubkey=HSM_PUBKEY) or abort("서명 불일치")
assert pkg.version > installed.version, "다운그레이드 거부"
install(pkg)</pre>
<div class="warn">놓치기 쉬운 곳 — <b>업데이트 실패 시 구버전으로 계속 동작</b>하면 패치가 영영 적용되지 않습니다.
&ldquo;최신 여부&rdquo;를 서버가 확인하고, 일정 기간 미갱신 단말은 <u>거래를 제한</u>해야 실효가 있습니다.</div>''',
},

'07_fin-source-info-leak.html': {
 'stack': ['시크릿 스캔', 'CI 게이트', '소스맵'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>앱·프런트엔드 빌드에 <b>비밀값이 섞여 들어가는 경로</b>가 늘었습니다 —
환경변수를 번들에 인라인하는 프레임워크(<code>NEXT_PUBLIC_*</code>, <code>REACT_APP_*</code>),
<b>배포된 소스맵</b>, 커밋된 <code>.env</code>. APK 는 누구나 내려받아 풀어 볼 수 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>CI 에 <b>시크릿 스캔</b>(gitleaks·trufflehog)을 게이트로 걸고, <u>커밋 이력 전체</u>를 검사합니다. 지운 커밋에도 남아 있습니다.</li>
<li><b>소스맵을 공개 경로에 올리지 않습니다.</b> 오류 추적 도구에는 업로드하되 웹루트에서는 제외합니다.</li>
<li>운영 빌드에서 <b>디버그 로그를 제거</b>합니다(R8 <code>assumenosideeffects</code>, <code>console.*</code> 제거).</li>
</ul>
<pre># ProGuard/R8 — 릴리스에서 로그 호출을 통째로 지운다
-assumenosideeffects class android.util.Log {
    public static *** d(...); public static *** v(...);
}</pre>
<div class="warn">놓치기 쉬운 곳 — <b>이미 배포된 앱의 비밀값은 회수 불가</b>입니다.
스캔으로 찾았다면 제거가 아니라 <u>즉시 교체(rotate)</u> 가 조치입니다. 앱 업데이트는 그다음입니다.</div>''',
},

'07_fin-cmdline-exposure.html': {
 'stack': ['컨테이너 env', 'K8s Secret', '프로세스 목록'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>명령줄 인자 노출은 <b>컨테이너 환경에서 더 넓어졌습니다.</b>
<code>docker inspect</code>·<code>kubectl describe pod</code> 가 <b>환경변수와 실행 인자를 그대로 출력</b>하고,
CI 로그에도 남습니다. 같은 노드의 다른 컨테이너에서 <code>/proc</code> 를 읽는 경로도 있습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>비밀값은 인자·환경변수가 아니라 <b>파일 마운트</b>로 전달합니다(K8s Secret 볼륨, <code>tmpfs</code>).</li>
<li>더 나은 방법은 <b>런타임 조회</b>입니다 — Secrets Manager·Vault 에서 시작 시 가져옵니다.</li>
<li>K8s Secret 은 <b>base64 인코딩일 뿐 암호화가 아닙니다.</b> etcd 암호화와 RBAC 을 함께 설정해야 합니다.</li>
</ul>
<pre># 나쁨: kubectl describe 로 그대로 보인다
args: ["--db-password=Fin!Core#2026"]

# 좋음: 파일로 마운트하고 앱이 읽는다
volumeMounts: [{ name: db-secret, mountPath: /run/secrets, readOnly: true }]</pre>
<div class="warn">놓치기 쉬운 곳 — <b>CI 파이프라인 로그</b>가 가장 흔한 유출 지점입니다.
빌드 스크립트가 <code>set -x</code> 로 실행되면 모든 인자가 로그에 찍히고, 그 로그는 대개 조직 전체에 공개됩니다.</div>''',
},

# ══════════════════════════ 웹 서버 ══════════════════════════
'07_fin-dir-listing.html': {
 'stack': ['컨테이너 기본값', 'S3 정적호스팅', 'IaC'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>점검 대상이 <b>서버 설정 파일에서 이미지·클라우드 설정</b>으로 옮겨 갔습니다.
공식 <code>nginx</code> 이미지는 기본적으로 autoindex 가 꺼져 있지만, <b>사내 베이스 이미지에서 켜 두고 잊는</b> 경우가 있고,
S3 정적 호스팅에서는 <b>ListBucket 권한</b>이 사실상 같은 결과를 냅니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>이미지 빌드 시 <code>autoindex off;</code> 를 <b>명시</b>하고, 그 설정을 이미지에 굽습니다.</li>
<li>S3 는 <b>퍼블릭 <code>s3:ListBucket</code> 을 부여하지 않습니다.</b> 객체 읽기 권한만으로 충분합니다.</li>
<li>정적 자산은 <b>CloudFront + OAC</b> 로 서빙하고 버킷 직접 접근을 막습니다.</li>
</ul>
<pre># 취약한 버킷 정책 — ListBucket 이 곧 디렉터리 목록이다
{"Effect":"Allow","Principal":"*",
 "Action":["s3:GetObject","s3:ListBucket"],        ← ListBucket 제거
 "Resource":["arn:aws:s3:::fin-assets","arn:aws:s3:::fin-assets/*"]}</pre>
<div class="warn">놓치기 쉬운 곳 — 목록이 막혀도 <b>파일명을 추측할 수 있으면 의미가 없습니다.</b>
<code>backup.zip</code>·<code>db_2026.sql</code> 같은 이름은 그대로 열립니다 — 웹루트에 두지 않는 것이 근본 조치입니다.</div>''',
},

'07_fin-file-exposure.html': {
 'stack': ['.dockerignore', '멀티스테이지', '.git 노출'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>컨테이너 빌드에서 <code>COPY . .</code> 한 줄이 <b><code>.git</code>·<code>.env</code>·백업 파일을 통째로 이미지에 담습니다.</b>
이미지는 레지스트리에 올라가고, 웹루트에 그대로 서빙되면 <code>/.git/config</code> 로 <b>전체 소스 복원</b>이 가능합니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b><code>.dockerignore</code></b> 에 <code>.git</code>·<code>.env</code>·<code>*.bak</code>·<code>node_modules</code> 를 넣습니다. <code>.gitignore</code> 와는 별개 파일입니다.</li>
<li><b>멀티스테이지 빌드</b>로 최종 이미지에는 산출물만 남깁니다. 빌드 도구·소스가 따라가지 않습니다.</li>
<li>레지스트리에 올리기 전 <b>이미지 내용을 스캔</b>합니다(시크릿·불필요 파일).</li>
</ul>
<pre># 멀티스테이지 — 최종 이미지에 소스가 없다
FROM gradle:8 AS build
COPY . /src
RUN gradle bootJar

FROM eclipse-temurin:21-jre
COPY --from=build /src/build/libs/app.jar /app.jar   # 산출물만
</pre>
<div class="warn">놓치기 쉬운 곳 — <b>이미지 레이어는 지워도 남습니다.</b>
<code>COPY secret.txt</code> 후 <code>RUN rm secret.txt</code> 해도 이전 레이어에 그대로 있어
<code>docker history</code> 로 추출됩니다. 처음부터 넣지 않는 것이 유일한 해법입니다.</div>''',
},

'07_fin-web-methods.html': {
 'stack': ['API Gateway', 'K8s Ingress', 'CORS'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>메서드 통제 지점이 <b>웹서버에서 API 게이트웨이·인그레스</b>로 옮겨 갔습니다.
REST 에서는 <code>PUT</code>·<code>DELETE</code> 가 정상 메서드라 &ldquo;무조건 차단&rdquo;이 성립하지 않고,
<b>경로별로 허용 메서드를 정의</b>하는 방식이 되었습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>API 게이트웨이에 <b>정의된 메서드만 라우팅</b>하고 나머지는 405 로 거절합니다. 스펙(OpenAPI)에서 자동 생성하면 어긋남이 줄어듭니다.</li>
<li><b>TRACE·TRACK</b> 은 여전히 차단합니다(XST). 프레임워크 기본값에 남아 있는 경우가 있습니다.</li>
<li><b>CORS 프리플라이트</b>와 혼동하지 않도록 <code>OPTIONS</code> 는 게이트웨이가 처리하고 백엔드로 넘기지 않습니다.</li>
</ul>
<pre># K8s Ingress — 허용 메서드를 명시적으로 제한
nginx.ingress.kubernetes.io/configuration-snippet: |
  if ($request_method !~ ^(GET|POST|PUT|DELETE|OPTIONS)$) { return 405; }</pre>
<div class="warn">놓치기 쉬운 곳 — <b>HTTP 메서드 오버라이드 헤더</b>(<code>X-HTTP-Method-Override</code>)를
프레임워크가 해석하면 <code>POST</code> 로 위장한 <code>DELETE</code> 가 통과합니다. 사용하지 않으면 꺼 두세요.</div>''',
},

'07_fin-ssi.html': {
 'stack': ['레거시 잔존', '컨테이너 설정', 'CSP'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>SSI 는 거의 쓰이지 않지만 <b>레거시 설정으로 살아 있는</b> 경우가 있습니다.
문제는 <b>아무도 쓰지 않는 기능이 켜져 있다</b>는 점입니다 — 사용하지 않으니 점검에서도 빠지고,
공격자만 그 경로를 찾습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li><b>SSI 를 끕니다</b>(<code>Options -Includes</code>, nginx <code>ssi off;</code>). 쓰지 않는 기능을 켜 둘 이유가 없습니다.</li>
<li>동적 포함이 필요하면 <b>템플릿 엔진·엣지 함수</b>로 대체하고, 사용자 입력은 렌더링 대상이 아니라 <b>데이터로</b> 전달합니다.</li>
<li>사용자 생성 콘텐츠는 <b>저장 시 정제 + 출력 시 이스케이프</b>를 모두 적용합니다.</li>
</ul>
<div class="warn">놓치기 쉬운 곳 — <b>사내 베이스 이미지</b>에 예전 설정이 남아 전 서비스로 퍼지는 구조입니다.
한 서비스에서 발견되면 <u>같은 이미지를 쓰는 전체</u>를 점검해야 합니다.</div>''',
},

'07_fin-ssti.html': {
 'stack': ['샌드박스 템플릿', '서버리스', 'LLM 프롬프트'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>SSTI 는 <b>서버리스에서 더 위험</b>합니다 — 함수 실행 역할의 권한을 그대로 얻기 때문에
템플릿 주입 하나가 <b>클라우드 자격증명 탈취</b>로 직결됩니다(IMDS·환경변수 접근).
그리고 <b>LLM 프롬프트 템플릿</b>이라는 새로운 주입 표면이 생겼습니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>템플릿은 <b>샌드박스 모드</b>로 실행합니다(Jinja2 <code>SandboxedEnvironment</code>, Freemarker <code>TemplateClassResolver.SAFE_RESOLVER</code>).</li>
<li><b>사용자 입력으로 템플릿을 구성하지 않습니다.</b> 입력은 <u>렌더링 컨텍스트의 값</u>으로만 전달합니다.</li>
<li>서버리스 함수는 <b>최소 권한 역할</b>을 부여합니다 — 주입되어도 얻을 것이 없게 만듭니다.</li>
</ul>
<pre># 위험: 사용자 입력이 템플릿 문자열 자체가 된다
Template(f"안녕하세요 {user_input}님").render()

# 안전: 템플릿은 고정, 입력은 값으로
Template("안녕하세요 {{ name }}님").render(name=user_input)   # 샌드박스 환경에서</pre>
<div class="warn">앞을 내다본다면 — <b>LLM 연동 기능</b>(상담 요약·문서 생성)에서 사용자 입력을
프롬프트 템플릿에 문자열 결합하면 같은 부류의 취약점이 됩니다.
출력을 그대로 실행·렌더링하지 않는 것이 원칙입니다.</div>''',
},

'07_fin-system-info-leak.html': {
 'stack': ['구조화 로깅', 'APM', '에러 핸들러'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>스택트레이스가 <b>브라우저가 아니라 로그 수집기·APM 으로</b> 갑니다.
화면에는 안 보여도 <b>Sentry·Datadog 대시보드에 요청 본문과 함께 그대로 남고</b>,
그 대시보드는 대개 조직 전체에 열려 있습니다 — 노출 대상이 바뀐 것뿐입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>사용자에게는 <b>추적 ID 만</b> 보여 줍니다(<code>traceId: 7f3a...</code>). 상세는 서버 로그에서 그 ID 로 찾습니다.</li>
<li>APM·로그 수집기에 <b>마스킹 규칙</b>을 설정합니다 — 계좌번호·주민번호·토큰·인증코드.</li>
<li>프레임워크 기본 에러 페이지를 <b>반드시 교체</b>합니다(Spring <code>server.error.include-stacktrace=never</code>).</li>
</ul>
<pre>// 사용자 응답과 내부 로그를 분리한다
log.error("txn failed userId={} traceId={}", userId, traceId, e);   // 내부
return ResponseEntity.status(500)
        .body(Map.of("message", "처리 중 오류", "traceId", traceId)); // 외부</pre>
<div class="warn">놓치기 쉬운 곳 — <b>응답 헤더</b>도 정보원입니다.
<code>Server: Apache/2.4.41 (Ubuntu)</code>, <code>X-Powered-By</code>, 상세 <code>WWW-Authenticate</code> 는 제거하세요.</div>''',
},

'07_fin-external-info-leak.html': {
 'stack': ['서드파티 태그', 'CSP', 'Referrer-Policy'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>이 항목이 <b>가장 크게 확장된</b> 영역입니다. 현대 금융 웹페이지에는 분석·광고·채팅·A/B 테스트 등
<b>서드파티 스크립트가 수십 개</b> 실립니다. 각각이 DOM 전체를 읽을 수 있으므로,
<b>거래내역 화면에 붙은 분석 태그 하나가 계좌정보 유출 경로</b>가 됩니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>거래·계좌 화면에는 <b>서드파티 태그를 싣지 않습니다.</b> 마케팅 요구가 있어도 이 원칙이 우선입니다.</li>
<li><b>CSP 로 외부 전송을 통제</b>합니다 — <code>connect-src</code>·<code>img-src</code> 를 좁히면 데이터 반출 경로가 막힙니다.</li>
<li><b><code>Referrer-Policy: no-referrer</code></b> 로 URL 에 담긴 식별자가 외부로 가지 않게 합니다.</li>
<li>태그 매니저는 <b>변경 승인 절차</b>를 둡니다 — 코드 배포 없이 스크립트가 추가되는 경로입니다.</li>
</ul>
<pre>Content-Security-Policy:
  default-src 'self';
  connect-src 'self' https://api.bank.example;   # 외부 전송 차단
  script-src 'self';                              # 서드파티 스크립트 금지
Referrer-Policy: no-referrer</pre>
<div class="warn">놓치기 쉬운 곳 — <b>태그 매니저는 코드 배포를 우회합니다.</b>
보안 검토를 거친 코드만 올라간다고 믿지만, 마케팅 담당자가 콘솔에서 스크립트를 추가할 수 있습니다.
실제 금융·의료 분야에서 이 경로로 개인정보가 광고 플랫폼에 전송된 사례가 다수 적발됐습니다.</div>''',
},

# ══════════════════════════ HTS ══════════════════════════
'07_fin-hts-param.html': {
 'stack': ['데스크톱 앱', '코드서명', 'Electron'],
 'html': '''<h4>어디가 달라졌나</h4>
<p>HTS 는 여전히 네이티브 데스크톱이지만, 신규 개발은 <b>Electron·웹뷰 기반</b>으로 옮겨 가고 있습니다.
그러면서 <b>웹 취약점이 데스크톱 권한으로 실행</b>되는 새로운 위험이 생겼습니다 —
Electron 에서 <code>nodeIntegration</code> 이 켜져 있으면 XSS 하나가 곧 로컬 코드 실행입니다.</p>
<h4>현대 스택에서의 조치</h4>
<ul>
<li>실행 파라미터로 <b>인증 상태를 전달하지 않습니다.</b> 프로세스 목록에 그대로 보이고 재사용됩니다 — 서버 세션으로 처리합니다.</li>
<li>Electron 이라면 <b><code>contextIsolation: true</code>, <code>nodeIntegration: false</code>, <code>sandbox: true</code></b> 를 기본으로 둡니다.</li>
<li>실행 파일에 <b>코드 서명</b>을 적용하고, 자동 업데이트는 <b>서명 검증 후</b> 설치합니다.</li>
</ul>
<pre>// Electron 기본 보안 설정 — 이 셋이 빠지면 웹 취약점이 곧 RCE 다
new BrowserWindow({
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: false,
    sandbox: true,
  }
});</pre>
<div class="warn">놓치기 쉬운 곳 — <b>Electron 은 Chromium 을 통째로 품고 있습니다.</b>
런타임을 갱신하지 않으면 알려진 브라우저 취약점을 그대로 안고 갑니다 —
&ldquo;업데이트&rdquo;는 우리 코드뿐 아니라 <u>런타임 버전</u>까지 포함해야 합니다.</div>''',
},

}
