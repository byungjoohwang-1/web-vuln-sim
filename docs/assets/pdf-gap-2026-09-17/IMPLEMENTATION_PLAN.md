# PDF 갭 구현 계획 (books/new2 6종 · 2026-09-17 분석 기준)

> 갭 원본: `gap-analysis.json` (6 PDF · 42갭: high 17 / mid 17 / low 8) · 우선순위: `gap-analysis.json` .ranking
> 원칙: PDF 원문 문장은 상업/공공 저작물 — 의도 요약 + 자체 작성 데이터로만 만든다(프로젝트 저작권 방침).
> 게이트 순서(모든 배치 공통): gen_registry → inject_shell → (필요시 inject_safety/inject_ai_meta) → gen_sitemap → page-order.json → validate_build.py

## 배치 A — 9/20 마감 전 (평가 리포트 배포 직후 착수)

| # | 항목 | PDF | 형태 | 핵심 설계 |
|---|------|-----|------|-----------|
| A1 | '부분 이행' 판정 단계 | 관리·물리(2026) | mp-assessment 엔진 확장 | 양호/취약 2상태 → **양호/부분 이행/미이행 3상태** + 가중 이행률. localStorage 키 `wvs_mp_assess` 하위호환 필수(기존 2상태값은 그대로 유효 취급). 가이드의 3단계 루브릭 표를 항목별 판정 기준으로 |
| A2 | MISRA C:2025 신규 룰 4종 카드 | MISRA C:2025 | coding-standards misrac 카드 패턴 | Rule 8.18(포인터→배열 변환), 8.19(? 접근), 11.11(NULL 암시 비교 금지), 19.3(union type-punning 미지정값 읽기). 위반/준수 코드쌍 + "쉽게 말하면" 비유. 원문 문장 금지 — 의도 요약 + 자체 코드 |
| A3 | 2012→2025 마이그레이션 레퍼런스 | MISRA C:2025 | 레퍼런스 1장 + 기존 카드 배지 주입 | 철회 룰 5장(1.2, 11.7, 17.6, 21.1, 21.2)에 "2025 판에서 철회 → 이동/병합 규칙" 배지. 대응표(번호 이동·병합·재분류). 스크립트 일괄 주입 |
| A4 | AI 이용자 보안 수칙 12종 자가진단 | AI 보안 안내서(정오판) | 신규 페이지 1개 (mp-assessment 패턴) | 개발자가 아닌 이용자 관점 12문항. KO/EN 이중. 대상: 임직원·일반 이용자(전역 0건 확인) |
| A5 | Purdue 모델 × ZT 학습카드 | OT ZT 안내서 | 학습카드 1장 | Level 0~4+DMZ 구조·구성요소(SCADA/PLC/RTU/HMI…)·레벨별 보안 적용 차이·PEP/PDP 배치 2시나리오. 16_zt↔12_ics 잇는 뼈대. 인터랙티브 레벨 선택기는 마감 후 |
| A6 | AI 생성 코드 × MISRA C (1.5.3) | MISRA C:2025 | 소형 카드+체크리스트 | "LLM 코드는 '자동생성 코드' 혜택 없음 = 전량 검증 대상". A2/A3와 같은 배치. ai-hub(academy-data-ai.js)↔Track 04 연결 |
| A7 | ZT 성숙도 자가진단 축소판 | ZT 성숙도 해설서 | zt-maturity-assessment.html (27개 기능별 1문항) | mp-assessment 링 + skill-radar.js(WVSRadar) 8축 4단계. 396체크리스트 전량은 마감 후 |

## 배치 B — 9/20 마감 후 (원문 ranking 8위 이하)

- AI 개발자 생명주기 57항목 + 서비스 제공자 44항목 자가진단(한 페이지 2탭)
- OT ZT 도입 로드맵 5단계 인터랙티브 랩 (CSA 5단계: 자산식별→가시화→PEP 배치→Kipling 정책→모니터링)
- OT 특화 ZT 자가진단 (표 23 기반 22항목 × Purdue 레벨)
- OT 사이버 공격 사례 아카이브 15건+ (security-incidents.html IT/OT 필터·인프라 피해 축 확장 포함)
- 자동차 퍼징 랩 · 침투테스트 TC 카탈로그 · TARA 8단계 워크스루 (21434 Vol.2)
- 문서·증거 감사 실습(서식 기반 모의 감사) · 16_zt-maturity-model 레퍼런스
- IT vs OT 비교 카드 · Zone-Conduit 세그멘테이터 · Kipling 정책 빌더 · 국내외 정책 동향 레퍼런스

## UI 고도화 아이디어 (gap-analysis.json .uiUpgradeIdeas)

1. 16_zt 8종 카드에 'OT에서는?' 콜아웃 패널
2. 12_ics 14종에 '실제 사례' 배경 배지(사례 아카이브와 상호 링크)
3. security-incidents.html IT/OT 필터 + 인프라 피해 축
4. wvs_otzt_* 진도 키로 OT ZT 5단계 완료 칩
5. vuln-hub에 'OT 제로트러스트' 그룹(16_zt+12_ics 묶는 중간 허브) — **기둥 목록 드리프트 주의: page-order.json·gen_registry 동시 등록**
6. Purdue 레벨 선택기 인터랙티브 다이어그램(레벨별 가능/금지 조치 토글)

## 별도 트랙 — 라이브 시뮬레이터 공격 애니메이션 고도화 (사용자 요청 ②)

- 대상: sim-*.html 62종 중 공격형. 전부 페이지 내부 mock(원칙 유지), 방어 코드와 짝지음
- 접근: 단계별 시각 피드백(요청 흐름 애니메이션→취약점 적중 하이라이트→방어 적용 후 차단 대비), aria-live 상태 알림
- 배치 A·B와 독립 진행 가능하나 UI 일관성을 위해 배치 A 완료 후 착수 권장
