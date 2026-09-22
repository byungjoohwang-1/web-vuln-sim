#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 7단계] 오케스트레이터 — 24/7 안전장치.

cron(설계상 15분 주기)이 이걸 부른다. 상태를 정리하고, 조건이 맞는 LLM 단계를
정확히 하나만 기동한다. 에이전트끼리 직접 부르지 않는다 — 상태가 에이전트 머릿속이
아니라 DB·티켓 파일에 있으므로, 정전·재부팅·429 로 죽어도 다음 tick 이 같은
지점에서 재개한다.

정리(housekeeping):
  - 72시간 넘게 미승인인 pending 티켓 -> expired (사람이 자리를 비워도 안전)
  - gate-pass/pending 이 아닌 떠도는 worktree 제거(디스크 캡)
백프레셔:
  - 승인 대기(pending)가 MAX_PENDING 이상이면 작성(build)을 멈춘다 — 사람이
    감당할 만큼만 쌓는다. 적체가 쌓이면 사람은 일괄 승인으로 도망가고 게이트가
    종잇장이 된다.
단계 선택(우선순위): review > build > triage. 뒤에서 앞으로 비워야 파이프라인이
  막히지 않는다(먼저 만든 것을 먼저 내보낸다).

사용:
  WVS_AGENT_DRYRUN=1 python ops/tick.py   # 로직 검증(대화 중)
  python ops/tick.py                       # 실제 오케스트레이션(cron/독립)
"""
import json
import os
import subprocess
import sys

import state

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TICKETS = os.path.join(HERE, 'queue', 'tickets')
WT = os.path.join(HERE, 'wt')

MAX_PENDING = 2                 # 승인 대기 상한(백프레셔)
PENDING_TTL = 72 * 3600        # 72시간 미승인 -> 만료
MAX_BUILDS_PER_DAY = 3


def sh(argv, cwd=ROOT, timeout=900):
    return subprocess.run(argv, cwd=cwd, timeout=timeout,
                          env=dict(os.environ, PYTHONIOENCODING='utf-8'))


def load_tickets():
    out = []
    if not os.path.isdir(TICKETS):
        return out
    for f in sorted(os.listdir(TICKETS)):
        if f.endswith('.json'):
            with open(os.path.join(TICKETS, f), encoding='utf-8') as fh:
                out.append(json.load(fh))
    return out


def save_ticket(t):
    with open(os.path.join(TICKETS, t['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(t, fh, ensure_ascii=False, indent=2)


def housekeeping(tickets):
    now = state.now()
    expired = 0
    for t in tickets:
        if t.get('status') == 'pending':
            age = now - t.get('created_at', now)
            if age > PENDING_TTL:
                t['status'] = 'expired'
                save_ticket(t)
                expired += 1
    # 떠도는 worktree: 살아있는(gate-pass/pending) 티켓의 것만 남기고 제거
    live_branches = {t.get('branch') for t in tickets
                     if t.get('status') in ('gate-pass', 'pending') and t.get('branch')}
    removed = 0
    if os.path.isdir(WT):
        for name in os.listdir(WT):
            branch = 'auto/' + name
            if branch not in live_branches:
                sh(['git', 'worktree', 'remove', os.path.join(WT, name), '--force'], timeout=60)
                sh(['git', 'branch', '-D', branch], timeout=60)
                removed += 1
    return expired, removed


def choose_stage(tickets):
    """실행할 단계 하나를 고른다(우선순위: review > build > triage)."""
    statuses = [t.get('status') for t in tickets]
    pending_n = statuses.count('pending')

    if 'gate-pass' in statuses:
        return 'review', 'gate-pass 티켓 검토'
    # 백프레셔: 승인 대기가 상한 이상이면 새로 만들지 않는다
    if pending_n >= MAX_PENDING:
        return None, '백프레셔: 승인 대기 %d건(상한 %d) — 작성 보류' % (pending_n, MAX_PENDING)
    if 'awaiting_build' in statuses:
        # 하루 상한 확인
        import datetime
        today = datetime.date.today().isoformat().replace('-', '')
        made = sum(1 for t in tickets
                   if t.get('status') in ('gate-pass', 'pending', 'published')
                   and t['id'].startswith('t-' + today))
        if made >= MAX_BUILDS_PER_DAY:
            return None, '하루 build 상한 %d 도달' % MAX_BUILDS_PER_DAY
        return 'build', 'awaiting_build 티켓 작성'
    # 큐에 선별 대상이 있으면 triage
    conn = state.init()
    q = conn.execute("SELECT COUNT(*) n FROM items WHERE status='queued'").fetchone()['n']
    conn.close()
    if q > 0:
        return 'triage', 'queued %d건 선별' % q
    return None, '할 일 없음'


STAGE_CMD = {
    'triage': ['python', os.path.join('ops', 'triage_run.py')],
    'build': ['python', os.path.join('ops', 'build_run.py')],
    'review': ['python', os.path.join('ops', 'review_run.py')],
}


def main():
    conn = state.init()
    tickets = load_tickets()
    expired, removed = housekeeping(tickets)
    if expired or removed:
        print('정리: pending 만료 %d · worktree 제거 %d' % (expired, removed))

    tickets = load_tickets()   # 정리 후 다시
    stage, why = choose_stage(tickets)
    print('선택: %s (%s)' % (stage or '없음', why))
    if not stage:
        return 0

    r = sh(STAGE_CMD[stage])
    print('%s 종료코드 %d' % (stage, r.returncode))
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
