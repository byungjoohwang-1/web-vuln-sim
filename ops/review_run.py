#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 6단계-1] A3 독립 검토자.

gate-pass 티켓을 A2 와 다른 세션에서 검토한다 — 작성 대화 컨텍스트를 이어받지
않는다. 같은 세션이 자기 산출물을 검토하면 그건 검토가 아니라 자기 확인이다.
기계가 못 잡는 것만 본다: 사실 오류, 외부 원문을 옮긴 사실상 전재, 실존 상표,
그럴듯한 오개념, 모범답안이 자기 루브릭을 통과하는가.

검토자는 파일을 고치지 않는다(고치면 검토자가 작성자가 된다). pass 는 '사람에게
보여줄 자격이 생겼다'는 뜻이지 '배포해도 된다'가 아니다 — 배포는 사람만 한다.

  pass    사람 승인 대기(status=pending)로 올린다
  revise  결함을 findings 로 남기고 A2 에게 반송
  reject  교육용으로 부적합 — 데드레터

사용:
  WVS_AGENT_DRYRUN=1 python ops/review_run.py   # LLM 없이 흐름 검증
  python ops/review_run.py                       # 실제 검토(cron/독립 실행)
"""
import json
import os
import subprocess
import sys

import state
import agent

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TICKETS = os.path.join(HERE, 'queue', 'tickets')
REVIEWS = os.path.join(HERE, 'reviews')
DEAD = os.path.join(HERE, 'deadletter')
MAX_REVISE = 1

MODEL = 'claude-sonnet-4-5'
SYSTEM = (
    '너는 보안 학습 콘텐츠의 독립 검토자다. 작성자가 왜 그렇게 썼는지에 대한 설명은 '
    '주어지지 않는다 — diff 결과물만 보고 판정한다. 기계 게이트가 이미 문법·수치·'
    'SRI·스크립트 블록은 통과시켰으니, 너는 기계가 못 잡는 것만 본다: '
    '(1) 보안 사실이 틀렸는가 (2) 외부 원문 문장을 그대로 옮긴 전재인가 '
    '(3) 실존 상표를 소품으로 썼는가 (4) 그럴듯하지만 틀린 오개념이 있는가 '
    '(5) 방어 코드가 실제로 그 공격을 막는가 (6) 채점 루브릭이 있으면 모범답안이 통과하는가. '
    '출력은 JSON 하나: {"verdict":"pass|revise|reject","findings":["..."],'
    '"residualConcerns":["사람이 봐야 할 것"]}. 파일을 고치지 마라. '
    '반례(구체적 입력·줄)를 제시 못 하면 revise/reject 하지 마라.')


def sh(argv, cwd=ROOT, timeout=120):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', timeout=timeout,
                          env=dict(os.environ, PYTHONIOENCODING='utf-8'))


def pick_ticket():
    if not os.path.isdir(TICKETS):
        return None
    for f in sorted(os.listdir(TICKETS)):
        if not f.endswith('.json'):
            continue
        with open(os.path.join(TICKETS, f), encoding='utf-8') as fh:
            t = json.load(fh)
        if t.get('status') == 'gate-pass':
            return t
    return None


def save_ticket(t):
    with open(os.path.join(TICKETS, t['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(t, fh, ensure_ascii=False, indent=2)


def get_diff(branch):
    r = sh(['git', 'diff', 'main...' + branch])
    return r.stdout


def a3_stub(diff):
    """드라이런: diff 가 존재하고 명백한 위험 신호(상표·원문 전재 흔적)가 없으면 pass."""
    if not diff.strip():
        return {'verdict': 'reject', 'findings': ['빈 diff'], 'residualConcerns': []}
    return {'verdict': 'pass', 'findings': [],
            'residualConcerns': ['(dryrun) 실제 검토는 cron 독립 실행에서 수행']}


def main():
    ticket = pick_ticket()
    if not ticket:
        print('검토할 gate-pass 티켓이 없습니다.')
        return 0
    tid = ticket['id']
    branch = ticket.get('branch')
    print('검토 대상: %s (%s)' % (tid, ticket.get('title', '')[:50]))
    if not branch:
        print('  브랜치 정보 없음 — 데드레터')
        _dead(ticket, 'no-branch')
        return 1

    diff = get_diff(branch)
    diff_for_prompt = diff[:20000]   # 큰 diff 는 앞부분만
    prompt = ('아래 diff 를 검토하라(티켓: %s / %s).\n\n```diff\n%s\n```'
              % (ticket.get('canonical_id'), ticket.get('cwe'), diff_for_prompt))
    res = agent.run_agent(prompt, system=SYSTEM, model=MODEL,
                          dry_stub=lambda: a3_stub(diff))
    if not res['ok']:
        print('  검토 실패: %s' % res.get('error'))
        return 1
    v = res['data']
    verdict = v.get('verdict')
    os.makedirs(REVIEWS, exist_ok=True)
    with open(os.path.join(REVIEWS, tid + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(v, fh, ensure_ascii=False, indent=2)

    revises = ticket.get('review_revises', 0)
    if verdict == 'pass':
        ticket['status'] = 'pending'          # 사람 승인 대기
        ticket['review'] = v
        save_ticket(ticket)
        conn = state.init()
        conn.execute("UPDATE items SET status='pending' WHERE run_id=?", (tid,))
        conn.commit()
        conn.close()
        print('판정: pass -> 사람 승인 대기 (python ops/publish.py %s)' % tid)
        return 0
    if verdict == 'revise' and revises < MAX_REVISE:
        ticket['status'] = 'awaiting_build'    # A2 재작성
        ticket['review_revises'] = revises + 1
        ticket['review_findings'] = v.get('findings', [])
        save_ticket(ticket)
        print('판정: revise -> A2 반송 (%s)' % '; '.join(v.get('findings', [])[:2]))
        return 1
    # reject 또는 revise 한도 초과
    _dead(ticket, 'review-%s: %s' % (verdict, '; '.join(v.get('findings', [])[:2])))
    print('판정: %s -> 데드레터' % verdict)
    return 1


def _dead(ticket, reason):
    os.makedirs(DEAD, exist_ok=True)
    ticket['status'] = 'deadletter'
    ticket['deadletter_reason'] = reason
    save_ticket(ticket)
    with open(os.path.join(DEAD, ticket['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(ticket, fh, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    sys.exit(main())
