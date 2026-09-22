#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ops/ 파이프라인 자체 검증 — 각 단계의 핵심 불변식을 순수 함수 단위로 확인한다.

이 저장소의 원칙은 "AI 가 만든 것도 기계가 검증한다"이다. 파이프라인은 미래에
자동 콘텐츠를 만들 도구이므로, 그 판정 로직 자체가 회귀하면 조용히 잘못된 것을
만들어낸다. 여기서 막는다. 실제 LLM 호출·네트워크·DB 없이 결정론 함수만 본다
(배포 게이트에 넣어도 빠르고 안전하게 돈다).

사용: python ops/test_pipeline.py   (predeploy 후보)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import agent
import feeds
import fetch_feeds
import triage_run
import build_run

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(name)


# ── 1. JSON 추출기 (agent) — 코드펜스·산문·배열·실패 ──
check('json: 코드펜스', agent._extract_json('```json\n{"a":1}\n```') == {'a': 1})
check('json: 산문 혼입', agent._extract_json('result: {"d":"build"} end') == {'d': 'build'})
check('json: 배열', agent._extract_json('[{"x":1}]') == [{'x': 1}])
check('json: 실패는 None', agent._extract_json('no json') is None)
check('json: 중첩 균형', agent._extract_json('{"a":{"b":[1,2]},"c":3}') == {'a': {'b': [1, 2]}, 'c': 3})
check('json: 빈 입력', agent._extract_json('') is None)

# ── 2. 사전 필터 점수 (feeds) — KEV·AI·도메인 가중 ──
kev_score = feeds._score('SQL Injection', 'sql injection in x', None, in_kev=True)
plain_score = feeds._score('typo fix', 'a documentation typo', None, in_kev=False)
ai_score = feeds._score('LLM prompt injection', 'prompt injection in llm agent', None, in_kev=False)
check('score: KEV 가중(+50)', kev_score >= 50)
check('score: AI 키워드 가중', ai_score >= 20)
check('score: 무관 항목 낮음', plain_score < ai_score)
check('score: CVSS 반영', feeds._score('x', 'buffer overflow', 9.0, in_kev=False)
      > feeds._score('x', 'buffer overflow', 3.0, in_kev=False))

# ── 3. scope_guard (build_run) — 금지 파일 차단 ──
check('scope: validate_build 차단', build_run.scope_violations(['_gen/validate_build.py']) == ['_gen/validate_build.py'])
check('scope: tools 차단', build_run.scope_violations(['tools/predeploy-check.js']))
check('scope: firebase.json 차단', build_run.scope_violations(['firebase.json']))
check('scope: functions 차단', build_run.scope_violations(['functions/index.js']))
check('scope: sources.json 차단', build_run.scope_violations(['public/data/sources.json']))
check('scope: ops 자체 차단', build_run.scope_violations(['ops/gate.py']))
check('scope: CLAUDE.md 차단', build_run.scope_violations(['CLAUDE.md']))
check('scope: 정상 콘텐츠 허용', build_run.scope_violations(['public/sim-x.html', 'public/js/x.js']) == [])
check('scope: 집계물 허용', build_run.scope_violations(['public/data/content-registry.json', 'public/sitemap.xml']) == [])

# ── 4. uid 중복 제거 (fetch_feeds) — 같은 소스+ID 는 같은 uid ──
u1 = fetch_feeds.uid_of('kev', 'CVE-2026-1', None)
u2 = fetch_feeds.uid_of('kev', 'CVE-2026-1', None)
u3 = fetch_feeds.uid_of('nvd', 'CVE-2026-1', None)
check('uid: 같은 소스+ID 동일', u1 == u2)
check('uid: 다른 소스 다름', u1 != u3)

# ── 5. 슬러그 (triage) — 파일명 안전 ──
check('slug: CVE 정규화', triage_run.slugify('CVE-2026-1234', 't', 1) == 'cve-2026-1234')
check('slug: 특수문자 제거', '/' not in triage_run.slugify('a/b c!', None, 1))
check('slug: 폴백', triage_run.slugify(None, None, 5) == 'item5')

# ── 6. 선별 판정 (triage.dry_stub) — 순수 판정, 상한은 모름 ──
rows = [
    {'title': 'x', 'summary': 'llm prompt injection', 'priority': 80, 'canonical_id': 'CVE-1'},
    {'title': 'y', 'summary': 'sql injection', 'priority': 60, 'canonical_id': 'CVE-2'},
    {'title': 'z', 'summary': 'typo', 'priority': 5, 'canonical_id': 'CVE-3'},
]
verdicts = triage_run.dry_stub(rows)
builds = [v for v in verdicts if v['decision'] == 'build']
ignores = [v for v in verdicts if v['decision'] == 'ignore']
check('triage: 고점수 build', len(builds) == 2)
check('triage: 저점수 ignore', len(ignores) == 1)
check('triage: AI 는 13_ai 트랙', any(v['track'] == '13_ai' for v in builds))
check('triage: 판정에 상한 안 섞임(전부 build/ignore)',
      all(v['decision'] in ('build', 'ignore') for v in verdicts))

# ── 7. gate 환경실패 판별 (gate) ──
import gate
check('gate: 에뮬레이터 실패는 env',
      gate.looks_like_env_failure({'tail': 'Error: ECONNREFUSED 127.0.0.1:8080'}))
check('gate: 도구 부재는 env',
      gate.looks_like_env_failure({'missing': True, 'tail': 'not recognized'}))
check('gate: 진짜 콘텐츠 실패는 env 아님',
      not gate.looks_like_env_failure({'tail': 'SCRIPT-BLOCK: syntax error in sim-x.html'}))

print('=' * 50)
print('ops 파이프라인 자체 검증: %d 통과 / %d 실패' % (PASS, FAIL))
if FAILURES:
    for f in FAILURES:
        print('  FAIL: %s' % f)
    sys.exit(1)
print('전부 통과')
sys.exit(0)
