# ops/ — 실시간 취약점 수집 → 콘텐츠 자동 구현 파이프라인

WEB-VULN-SIM 을 계속 자라게 하는 운영 자동화. 보안·AI 취약점 정보를 수집해
콘텐츠 후보를 선별·작성·검증하고, **사람이 아침에 한 줄로 승인하면** 배포한다.
설계 근거: `../docs/AGENT_PIPELINE_DESIGN.md`.

## 흐름

```
[20분] fetch_feeds  피드 수집(CISA KEV·NVD) → state.db (판단 안 함)
   ↓
[15분] tick         오케스트레이터 — 조건 맞는 단계 하나 기동 + 정리·백프레셔
   ├─ triage_run    A1 선별: build/dup/ignore → 티켓 (하루 3건 상한)
   ├─ build_run     A2 작성: worktree 격리 + scope_guard + build_site + gate
   └─ review_run    A3 검토: 독립 세션, 사실·전재·상표·오개념 → pending
   ↓
[07:30] brief       숫자 브리프 — "어젯밤 뭐가 나왔나" (모델 없이)
   ↓
 사람   publish.py <ticket> --deploy   ← 유일한 사람 게이트(원클릭)
```

LLM 좌석은 3개(A1 선별 / A2 작성 / A3 검토). 나머지는 전부 결정론 스크립트다.

## 파일

| 파일 | 역할 | LLM |
|:--|:--|:--:|
| `state.py` | SQLite 상태 저장소(items·cursors·runs·budget·deadletter) | |
| `feeds.py` | 피드 소스·파서(KEV·NVD, 미국 정부 저작물) + 사전 필터 점수 | |
| `fetch_feeds.py` | 조건부 수집, 이중 중복 제거, 소스별 백오프 | |
| `brief.py` | 숫자 브리프 → `brief/YYYY-MM-DD.md` | |
| `agent.py` | 에이전트 호출 어댑터(claude CLI) + JSON 추출 + 드라이런 | |
| `triage_run.py` | A1 선별 → 티켓 + 상한 강제 | ● |
| `gate.py` | 게이트 러너 — 콘텐츠결함/환경미측정 분류 | |
| `build_run.py` | A2 작성 → worktree + scope_guard + gate | ● |
| `review_run.py` | A3 독립 검토 → pending/revise/reject | ● |
| `publish.py` | 원클릭 발행(사람 전용) — ff-only + 재게이트 + 배포 | |
| `tick.py` | 오케스트레이터 + 백프레셔 + 72h 만료 + 정리 | |

`state.db`·`raw/`·`queue/`·`brief/`·`wt/`·`gates/`·`reviews/`·`deadletter/` 는
런타임 산출물이라 `.gitignore`(코드만 버전 관리).

## 안전 설계

- **사람 게이트는 발행 한 곳.** `publish.py` 는 인자 하나만 받고 일괄 승인이 없다
  (배포 승인은 요청마다 개별). 무인 라이브 발행 경로는 만들지 않았다.
- **인젝션 검역선.** A1 만 외부 원문을 본다. A2 는 구조화 티켓만 받아 원문 전재와
  프롬프트 인젝션을 같은 경계에서 차단.
- **scope_guard.** A2 가 검사기·설정·서버·개인정보 고지·출처·CLAUDE.md·ops/ 를
  건드리면 실행 무효.
- **백프레셔·만료.** 승인 대기 2건이면 작성 중단, 72시간 미승인이면 만료 — 사람이
  자리를 비워도 적체가 쌓이거나 재생성 루프가 돌지 않는다.
- **적대적 분리.** A3 는 A2 와 다른 세션. 파일을 못 고친다(고치면 자기 검토).

## 실운영 시작

1. **이미 등록된 cron** (Windows 작업 스케줄러):
   - `WVS-fetch-feeds` (20분) · `WVS-brief` (07:30)
2. **실 LLM 첫 검증** — 이 저장소를 여는 claude 대화 세션이 없는 상태에서:
   ```
   python ops/triage_run.py     # 실제 선별(claude CLI 헤드리스)
   ```
   대화형 세션 안에서는 자식 claude 가 중첩 충돌로 무응답이므로 반드시 독립
   실행에서 확인한다. 되면 build_run·review_run 도 같은 방식으로 돈다.
3. **검증되면 tick 등록**:
   ```
   schtasks /create /tn "WVS-tick" /tr "<repo>\ops\run_tick.bat" /sc minute /mo 15 /f
   ```
4. **매일 아침**: `brief/오늘.md` 를 읽고, 승인할 티켓에 대해
   ```
   python ops/publish.py <ticket-id>            # 예행: 무엇이 배포되는지 확인
   python ops/publish.py <ticket-id> --deploy   # 실제 배포
   ```

## 알려진 개선점

- **ff-only rebase 자동화**: 사람이 낮에 main 에 커밋하면 auto 브랜치가 뒤처져
  ff-only 가 실패한다. 지금은 `publish.py` 가 안전하게 중단하고 안내만 한다 —
  auto 브랜치를 main 에 rebase 후 재게이트하는 자동화가 필요하다.
- **A4 브리프 서술**: 사고가 있는 날 숫자 브리프 위에 한 문단을 얹는 선택적 LLM
  단계. 현재는 숫자 브리프만.
- **AI 보안 전용 피드**: 지금은 CVE 중심(KEV·NVD)이라 AI 취약점도 CVE 번호가
  붙은 것만 잡힌다. OWASP LLM·MITRE ATLAS 등 비-CVE 소스는 `feeds.py` 에 소스를
  한 줄 추가하면 된다.
