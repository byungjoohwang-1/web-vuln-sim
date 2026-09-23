# 자동 기능개선 파이프라인 구조 (WEB-VULN-SIM)

사용자 요청 구조(2026-09-23): **최신 취약점 → 범위 분석(에이전트 협의) → 구현 →
빡센 QA(에이전트 협의) → 라이브 배포 + GitHub push만 사람 승인.**

```
[수집]  ops/fetch_feeds (cron 20분) — KEV·NVD·GHSA 최신 취약점 → ops/state.db
   │
[분석/범위]  PO 역할 — 피드 상위(우선순위=악용중+CVSS+AI가점)를 훑어
   │         기존 콘텐츠 갭 대비 "무엇을 만들/고도화할지" 범위 선정
   │              ⇅  협의(devteam event: po↔dev) — 범위·설계 합의
[구현]  DEV 역할 — 구현. 기존 파일 수정 전 devteam backup/created 로 기록.
   │         새 자산은 자체 완결형(DEF 엔진 등), 고유 매칭 토큰으로 분기충돌 예방.
   │              ⇅  협의(devteam event: dev↔qa) — 테스트 범위 합의
[QA]   QA 역할 — 빡센 테스트. 통과할 때까지 DEV 와 왕복.
   │         · 브라우저 전수 순회(공격 인식·출력충돌·방어후 변화·양방향 채점)
   │         · predeploy 게이트 전체(레지스트리·a11y·deadlink·SRI·문법)
   │         · 콘솔 오류 0
   │
[로컬 커밋]  자율 — 내 논리 파일만 stage 후 커밋(다른 세션 파일 불가침)
   │
[사람 게이트]  ★ 유일한 사람 승인 지점 ★  라이브 배포 + GitHub push
              devteam gate --cmd "git push origin main && firebase deploy ..."
              → 승인 콘솔(_devteam/approve_console.py, 폰 8790)에서 버튼/‘승인’
```

## 역할과 도구
- **관측/승인 UI**: `_devteam/approve_console.py` (폰 8790) — PO→DEV→QA 흐름·실시간
  협의 피드·승인 버튼을 **한 페이지**로. 승인은 PIN 게이트 + 실제 대기 런만 허용.
- **런 기록**: `_devteam/devteam.py` (init·event·stage·spec·report·gate·approve).
  이벤트가 곧 "에이전트 간 대화" — 보드에 실시간 표시.
- **모델 제약**: 서브에이전트/Workflow 가 glm-5.3(아웃)로 라우팅돼 자율 다중에이전트가
  현재 불가 → 메인 세션(opus)이 PO·DEV·QA 역할을 직접 수행하며 devteam 으로 기록.
  glm 복구 시 각 역할을 실제 서브에이전트로 분리 가능(구조 동일).

## 원칙
- **사람 승인은 배포+push 뿐.** 수집·분석·구현·QA·로컬커밋은 자율.
- **작업트리 격리**: 내 파일만 커밋. 다른 세션의 미커밋 변경분은 건드리지 않는다.
  단 `firebase deploy` 는 작업트리 전체를 올리므로, 타 세션 미커밋 변경이 있으면
  게이트 이벤트에 경고를 남기고 사람이 알고 승인하게 한다.
- **백프레셔**: 승인 대기 런이 쌓이면(≥2) 새 구현을 멈춘다(사람이 감당할 만큼만).
- **정직성**: 미측정은 미측정. QA 수치는 실제 실행값만.

## 사이클 로그
- #1 (완료·배포) FEAT-20260923-oauth-oidc-lab — OAuth·OIDC·JWT 9도전. 커밋 a6d1f34.
- #2 (진행) FEAT-20260923-llm-appsec — LLM 앱·게이트웨이 보안. 최신 KEV LiteLLM
  (CVE-2026-59822 인증우회·42271 명령주입·42208 SQLi) 구동.
