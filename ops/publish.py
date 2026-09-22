#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 6단계-2] 원클릭 발행 — 사람만 실행한다.

이 스크립트가 파이프라인 전체의 유일한 사람 게이트다. 수집·선별·작성·검토는
전부 자동으로 돌아 pending 까지 쌓이고, 사람은 아침에 브리프를 읽고 티켓 하나에
대해 이 명령을 친다. 인자는 하나만 받고 일괄 승인 플래그는 두지 않는다 —
'배포 승인은 요청마다 개별'을 말이 아니라 도구 인터페이스로 지킨다.

무결성 세 겹:
  1) pending 티켓만 대상(검토를 통과한 것)
  2) main 에는 ff-only 로만 넣는다 — '승인한 커밋'과 '배포되는 커밋'이 같다
  3) 머지 후 main 에서 게이트를 한 번 더 돌린다(머지가 뭔가 깨지지 않았는지)

기본은 예행(--dry): 무엇이 배포될지 보여주고 멈춘다. 실제 배포는 --deploy.
롤백은 자동으로 하지 않는다(롤백도 배포다) — releases.jsonl 에 좌표만 남긴다.

사용:
  python ops/publish.py <ticket-id>            # 예행: 승인 대상 확인
  python ops/publish.py <ticket-id> --deploy   # 실제 머지 + 재게이트 + 배포
"""
import datetime
import json
import os
import subprocess
import sys

import state

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TICKETS = os.path.join(HERE, 'queue', 'tickets')
RELEASES = os.path.join(HERE, 'releases.jsonl')


def sh(argv, cwd=ROOT, timeout=300):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          encoding='utf-8', timeout=timeout,
                          env=dict(os.environ, PYTHONIOENCODING='utf-8'))


def load_ticket(tid):
    p = os.path.join(TICKETS, tid + '.json')
    if not os.path.isfile(p):
        return None
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


def save_ticket(t):
    with open(os.path.join(TICKETS, t['id'] + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(t, fh, ensure_ascii=False, indent=2)


def main():
    args = sys.argv[1:]
    positional = [a for a in args if not a.startswith('--')]
    if len(positional) != 1:
        print('사용: python ops/publish.py <ticket-id> [--deploy]')
        print('(인자는 티켓 하나만. 일괄 승인은 지원하지 않는다.)')
        return 2
    tid = positional[0]
    do_deploy = '--deploy' in args

    ticket = load_ticket(tid)
    if not ticket:
        print('티켓 없음: %s' % tid)
        return 2
    if ticket.get('status') != 'pending':
        print('티켓 상태가 pending 이 아님: %s (검토 통과분만 발행 가능)' % ticket.get('status'))
        return 2
    branch = ticket.get('branch')

    # 현재 브랜치가 main 인지
    cur = sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()
    if cur != 'main':
        print('현재 브랜치가 main 이 아님(%s). main 에서 실행하라.' % cur)
        return 2
    # 브랜치 존재 확인
    if sh(['git', 'rev-parse', '--verify', branch]).returncode != 0:
        print('작성 브랜치 없음: %s' % branch)
        return 2

    main_sha = sh(['git', 'rev-parse', 'main']).stdout.strip()
    branch_sha = sh(['git', 'rev-parse', branch]).stdout.strip()
    base = sh(['git', 'merge-base', 'main', branch]).stdout.strip()
    ff_possible = (base == main_sha)
    stat = sh(['git', 'diff', '--stat', 'main...' + branch]).stdout.strip()
    review = ticket.get('review', {})

    print('=' * 56)
    print('발행 대상: %s' % tid)
    print('  제목: %s' % ticket.get('title', ''))
    print('  브랜치: %s @ %s' % (branch, branch_sha[:10]))
    print('  검토: %s' % review.get('verdict', '?'))
    if review.get('residualConcerns'):
        print('  검토가 사람에게 넘긴 것: %s' % '; '.join(review['residualConcerns'][:3]))
    print('  변경:\n    ' + '\n    '.join(stat.splitlines()[-6:]))
    print('  ff-only 가능: %s' % ('예' if ff_possible else '아니오 (main 이 진행됨 — rebase 필요)'))
    print('=' * 56)

    if not do_deploy:
        print('예행입니다. 실제로 배포하려면:')
        print('  python ops/publish.py %s --deploy' % tid)
        return 0

    if not ff_possible:
        # ff-only 불가(사람이 낮에 main 에 커밋해 auto 브랜치가 뒤처짐) — 자동 rebase.
        # rebase 는 커밋 diff 를 최신 main 위에 재적용하므로, 충돌이 없으면 내용이
        # 그대로 보존된다. 그래도 머지 후 재게이트가 '내용이 안 깨졌나'를 다시 보증한다.
        wt_dir = os.path.join(HERE, 'wt', tid)
        if not os.path.isdir(wt_dir):
            print('중단: ff-only 불가하고 rebase 할 worktree 가 없다 — 재작성이 필요하다.')
            return 1
        print('ff-only 불가(main 진행) — auto 브랜치를 최신 main 에 rebase 시도...')
        rb = sh(['git', 'rebase', 'main'], cwd=wt_dir)
        if rb.returncode != 0:
            sh(['git', 'rebase', '--abort'], cwd=wt_dir)
            print('중단: rebase 충돌 — 내용이 최신 main 과 겹친다. 사람이 해결해야 한다.')
            return 1
        branch_sha = sh(['git', 'rev-parse', branch]).stdout.strip()
        print('  rebase 완료 — auto 브랜치 재적용 @ %s (머지 후 재게이트가 안전을 재보증)'
              % branch_sha[:10])

    # ff-only 머지 (rebase 를 거쳤으면 이제 fast-forward 가능)
    m = sh(['git', 'merge', '--ff-only', branch])
    if m.returncode != 0:
        print('머지 실패: %s' % (m.stderr or '')[:200])
        return 1
    print('머지 완료 (ff-only). main @ %s' % sh(['git', 'rev-parse', 'main']).stdout.strip()[:10])

    # 머지된 main 에서 게이트 재실행
    g = sh(['python', os.path.join('ops', 'gate.py'), '--ticket', tid + '-postmerge'],
           timeout=700)
    if g.returncode != 0:
        print('머지 후 게이트 실패 — 머지를 되돌린다.')
        sh(['git', 'reset', '--hard', main_sha])
        return 1
    print('머지 후 게이트 통과.')

    # 배포
    print('배포: firebase deploy --only hosting ...')
    d = sh(['firebase', 'deploy', '--only', 'hosting'], timeout=600)
    ok = d.returncode == 0
    print((d.stdout or '')[-300:] if ok else '배포 실패:\n' + (d.stderr or '')[-300:])
    if not ok:
        print('배포 실패. main 은 머지된 상태로 남는다(롤백은 사람이 판단).')
        return 1

    # 릴리스 기록(롤백 좌표)
    rec = {
        'ticket': tid, 'sha': sh(['git', 'rev-parse', 'main']).stdout.strip(),
        'prev_sha': main_sha, 'at': datetime.datetime.now().isoformat(),
        'rollback': 'git reset --hard %s && firebase deploy --only hosting' % main_sha[:10],
    }
    with open(RELEASES, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    ticket['status'] = 'published'
    save_ticket(ticket)
    conn = state.init()
    conn.execute("UPDATE items SET status='published' WHERE run_id=?", (tid,))
    conn.commit()
    conn.close()
    print('발행 완료. 롤백이 필요하면: %s' % rec['rollback'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
