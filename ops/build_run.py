#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 5단계] A2 작성 에이전트 실행기.

awaiting_build 티켓을 하나 집어 격리된 git worktree(auto/<ticket> 브랜치)에서만
콘텐츠를 쓰게 하고, scope_guard 로 손대면 안 되는 파일을 막고, gate.py 로 검증한다.
main 에는 절대 쓰지 않는다 — 발행은 6단계 publish 가 사람 승인 뒤에만 한다.

A2 가 원문(raw)을 읽지 못하게 한다: 티켓의 구조화 요약만 준다. 원문 전재와
프롬프트 인젝션을 같은 경계에서 막는다(A1 만 원문을 봤고, 그 판정은 사람 배치
승인을 거쳐야 여기 온다 — 6단계).

scope_guard 가 막는 것(diff 에 있으면 실행 무효):
  검사기·배포도구(tools/, _gen/validate_build.py)·설정(firebase.json,
  firestore.rules)·서버(functions/)·개인정보 고지·출처 등록부·CLAUDE.md·
  파이프라인 자체(ops/). 이걸 A2 가 고치면 게이트는 초록인데 신뢰가 무너진다.

worktree 정리: gate-pass 는 유지(6단계 검토·발행이 쓴다), content-fault 는 1회
반송 후 2회째 데드레터(worktree 제거, patch 보존).

사용:
  WVS_AGENT_DRYRUN=1 python ops/build_run.py   # LLM 없이 흐름 검증(대화 중)
  python ops/build_run.py                       # 실제 작성(cron/독립 실행)
"""
import datetime
import json
import os
import re
import subprocess
import sys

import state
import agent

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TICKETS = os.path.join(HERE, 'queue', 'tickets')
WT = os.path.join(HERE, 'wt')
DEAD = os.path.join(HERE, 'deadletter')
MAX_ATTEMPTS = 2

FORBIDDEN = [
    r'^_gen/validate_build\.py$', r'^_gen/build_site\.py$', r'^_gen/gen_sources\.py$',
    r'^_gen/sources\.json$', r'^_gen/source-links\.json$',
    r'^tools/', r'^firebase\.json$', r'^firestore\.rules$', r'^functions/',
    r'^CLAUDE\.md$', r'^public/privacy', r'^public/data/sources\.json$',
    r'^\.gitignore$', r'^ops/',
]

MODEL = 'claude-sonnet-4-5'   # 작성은 상위 모델(설계) — 여기서 낮추면 게이트 실패 왕복이 는다
SYSTEM = (
    '너는 한국어 보안 학습 포털의 콘텐츠 작성자다. 주어진 티켓의 취약점을 이 사이트의 '
    '기존 페이지에 최신 사례로 반영하거나(권장), 정말 새로운 계열이면 새 sim 페이지를 만든다. '
    '반드시 지킨다: (1) 외부 원문 문장을 옮기지 말고 개념적으로 재구성한다. '
    '(2) 공격 시연은 페이지 내부 mock 만 — 실제 호스트·동작 익스플로잇 금지. '
    '(3) 공격 설명에는 방어 코드와 "쉽게 말하면" 비유를 함께 둔다. (4) 한국어·영어 병기. '
    '(5) 검사기·설정·서버·개인정보 고지·출처 파일은 절대 건드리지 않는다. '
    '(6) 화면 수치를 손으로 고치지 않는다(레지스트리가 단일 원천). '
    '작업은 현재 worktree 의 public/ 안에서만 한다.')


def sh(argv, cwd=None, timeout=120):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', timeout=timeout,
                          env=dict(os.environ, PYTHONIOENCODING='utf-8'))


def pick_ticket():
    if not os.path.isdir(TICKETS):
        return None
    cands = []
    for f in sorted(os.listdir(TICKETS)):
        if not f.endswith('.json'):
            continue
        with open(os.path.join(TICKETS, f), encoding='utf-8') as fh:
            t = json.load(fh)
        if t.get('status') == 'awaiting_build':
            cands.append(t)
    return cands[0] if cands else None


def save_ticket(t):
    with open(os.path.join(TICKETS, t['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(t, fh, ensure_ascii=False, indent=2)


def make_worktree(ticket_id):
    wt_dir = os.path.join(WT, ticket_id)
    branch = 'auto/' + ticket_id
    # 이전 잔여 정리
    sh(['git', 'worktree', 'remove', wt_dir, '--force'], cwd=ROOT)
    sh(['git', 'branch', '-D', branch], cwd=ROOT)
    r = sh(['git', 'worktree', 'add', wt_dir, '-b', branch, 'HEAD'], cwd=ROOT, timeout=120)
    return (wt_dir, branch) if r.returncode == 0 else (None, r.stderr[:200])


def cleanup_worktree(wt_dir, branch, keep=False):
    if keep:
        return
    sh(['git', 'worktree', 'remove', wt_dir, '--force'], cwd=ROOT)
    sh(['git', 'branch', '-D', branch], cwd=ROOT)


def changed_files(wt_dir):
    r = sh(['git', 'status', '--porcelain'], cwd=wt_dir)
    files = []
    for line in r.stdout.splitlines():
        f = line[3:].strip()
        if f:
            files.append(f)
    return files


def scope_violations(files):
    bad = []
    for f in files:
        for pat in FORBIDDEN:
            if re.search(pat, f):
                bad.append(f)
                break
    return bad


def a2_stub(wt_dir, ticket):
    """드라이런: A2 대신 무해하고 gate 를 통과하는 최소 변경을 만들어 흐름을 검증한다.
    기존 sim 페이지에 '최신 사례' HTML 주석 한 줄을 넣는다(문법 유효·집계 무관·scope 준수)."""
    target = None
    tr = (ticket.get('track') or '')
    if tr.startswith('update:'):
        cand = os.path.join(wt_dir, 'public', tr.split(':', 1)[1])
        if os.path.isfile(cand):
            target = cand
    if not target:
        # 기본: incident.html, 없으면 첫 sim
        for name in ('public/incident.html',):
            p = os.path.join(wt_dir, name)
            if os.path.isfile(p):
                target = p
                break
    if not target:
        return False, '대상 파일 없음'
    note = '<!-- pipeline-dryrun: 최신 사례 %s (%s) -->\n' % (
        ticket.get('canonical_id') or ticket['id'], ticket.get('cwe') or '')
    with open(target, 'r', encoding='utf-8', errors='replace') as fh:
        html = fh.read()
    idx = html.rfind('</body>')          # CLAUDE.md 원칙: rfind, 첫 </body> 금지
    if idx < 0:
        return False, '</body> 없음'
    html = html[:idx] + note + html[idx:]
    with open(target, 'w', encoding='utf-8') as fh:
        fh.write(html)
    return True, os.path.relpath(target, wt_dir)


def main():
    ticket = pick_ticket()
    if not ticket:
        print('작성할 awaiting_build 티켓이 없습니다.')
        return 0
    tid = ticket['id']
    dry = os.environ.get('WVS_AGENT_DRYRUN') == '1'
    print('작성 대상: %s (%s) 드라이런=%s' % (tid, ticket.get('title', '')[:50], dry))

    wt_dir, branch = make_worktree(tid)
    if not wt_dir:
        print('worktree 생성 실패: %s' % branch)
        return 1
    print('worktree: %s (%s)' % (os.path.relpath(wt_dir, ROOT), branch))

    # A2 작성
    if dry:
        ok, detail = a2_stub(wt_dir, ticket)
        print('  A2(스텁) %s: %s' % ('작성' if ok else '실패', detail))
        if not ok:
            cleanup_worktree(wt_dir, branch)
            return 1
    else:
        # 실제 A2: worktree 를 cwd 로, claude 가 그 안에서 작성.
        prompt = ('티켓:\n' + json.dumps({k: ticket.get(k) for k in
                  ('canonical_id', 'title', 'summary', 'track', 'cwe', 'reason')},
                  ensure_ascii=False, indent=2)
                  + '\n\n이 취약점을 위 규칙에 따라 반영하라. 완료하면 무엇을 바꿨는지 한 줄로 요약하라.')
        res = agent.run_agent(prompt, system=SYSTEM, model=MODEL, timeout=900)
        # 주의: 실제 작성은 claude 가 worktree cwd 에서 도구로 파일을 써야 한다.
        # 이 어댑터는 -p 텍스트 모드라, 실운영에서는 --add-dir/도구 허용 설정이 필요하다.
        if not res['ok']:
            print('  A2 실패: %s' % res.get('error'))
            cleanup_worktree(wt_dir, branch)
            return 1

    # scope_guard
    files = changed_files(wt_dir)
    bad = scope_violations(files)
    if bad:
        print('  scope_guard 위반: %s' % ', '.join(bad[:5]))
        _record_deadletter(ticket, 'scope-violation: ' + ', '.join(bad[:5]))
        cleanup_worktree(wt_dir, branch)
        return 1
    print('  변경 %d파일, scope 위반 없음' % len(files))

    attempts = ticket.get('build_attempts', 0) + 1
    ticket['build_attempts'] = attempts

    # A2 콘텐츠를 사이트에 편입: 집계·빌드 스탬프 재생성. 이걸 빼면 gate 가
    # stamp drift 를 콘텐츠 결함으로 오해한다 — A2 는 콘텐츠만, build_site 가 집계다.
    rb = sh(['python', os.path.join('_gen', 'build_site.py')], cwd=wt_dir, timeout=600)
    if rb.returncode != 0:
        tail = '\n'.join((rb.stdout + rb.stderr).strip().splitlines()[-4:])
        return _fault(ticket, wt_dir, branch, attempts, 'build_site 실패: ' + tail[:120])

    # 집계 산출물(registry·sitemap·stamp 등)은 허용 목록. 그래도 scope 재확인.
    bad2 = scope_violations(changed_files(wt_dir))
    if bad2:
        return _fault(ticket, wt_dir, branch, attempts, 'scope(집계후): ' + ', '.join(bad2[:3]))

    # 커밋(worktree 안) — gate 가 깨끗한 상태를 보게
    sh(['git', 'add', '-A'], cwd=wt_dir)
    sh(['git', 'commit', '-m', 'auto: %s' % tid], cwd=wt_dir)

    # gate
    r = sh(['python', os.path.join('ops', 'gate.py'), '--dir', wt_dir, '--ticket', tid],
           cwd=ROOT, timeout=700)
    for ln in (r.stdout or '').strip().splitlines()[-3:]:
        print('  ' + ln)
    if r.returncode != 0:
        return _fault(ticket, wt_dir, branch, attempts, 'gate content-fault')

    # gate-pass
    ticket['status'] = 'gate-pass'
    ticket['branch'] = branch
    save_ticket(ticket)
    conn = state.init()
    conn.execute("UPDATE items SET status='gate' WHERE run_id=?", (tid,))
    conn.commit()
    conn.close()
    print('판정: gate-pass -> 6단계 검토 대기 (worktree 유지)')
    cleanup_worktree(wt_dir, branch, keep=True)
    return 0


def _fault(ticket, wt_dir, branch, attempts, reason):
    """content-fault 처리: 1회는 반송(재시도), 상한 도달 시 데드레터."""
    if attempts >= MAX_ATTEMPTS:
        _record_deadletter(ticket, reason)
        cleanup_worktree(wt_dir, branch)
        print('판정: content-fault %d회 -> 데드레터 (%s)' % (attempts, reason[:70]))
    else:
        ticket['status'] = 'awaiting_build'
        save_ticket(ticket)
        cleanup_worktree(wt_dir, branch)
        print('판정: content-fault -> 반송 %d/%d (%s)' % (attempts, MAX_ATTEMPTS, reason[:70]))
    return 1


def _record_deadletter(ticket, reason):
    os.makedirs(DEAD, exist_ok=True)
    ticket['status'] = 'deadletter'
    ticket['deadletter_reason'] = reason
    save_ticket(ticket)
    with open(os.path.join(DEAD, ticket['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(ticket, fh, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    sys.exit(main())
