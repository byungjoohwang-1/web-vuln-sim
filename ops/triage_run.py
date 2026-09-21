#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 3단계] A1 선별 에이전트 실행기.

queued 항목을 배치로 꺼내 "이 취약점이 이 포털에 만들/갱신할 가치가 있는가"를
판정한다. 판단만 LLM 이 하고, 티켓 생성·상태 전이·상한 강제는 이 스크립트(결정론)
가 한다. 에이전트는 public/ 을 건드리지 않고, 새 기둥 접두사를 만들지 못하며,
하루 build 상한을 넘길 수 없다(상한이 프롬프트 설득 대상이면 상한이 아니다).

판정 3종:
  build   새롭고 mock 으로 재현 가능 → 티켓 생성(status=triaged)
  dup     기존 콘텐츠가 이미 다루는 계열 → dropped
  ignore  특정 제품 버그 등 교육용 재현 불가 → dropped

하루 build 상한(MAX_BUILDS)을 넘는 build 판정은 큐에 남겨 다음 날로 넘긴다.

사용:
  WVS_AGENT_DRYRUN=1 python ops/triage_run.py   # LLM 없이 로직 검증(대화 중)
  python ops/triage_run.py                       # 실제 선별(cron/독립 실행)
  python ops/triage_run.py --batch 20
"""
import datetime
import json
import os
import re
import sys

import state
import agent

HERE = os.path.dirname(os.path.abspath(__file__))
TICKETS = os.path.join(HERE, 'queue', 'tickets')
BATCH = 40
MAX_BUILDS = 3          # 하루 build 상한(설계)
MIN_BUILD_PRIORITY = 40  # 드라이런 스텁이 build 로 보는 최소 점수

MODEL = 'claude-haiku-4-5-20251001'   # 선별은 분류라 저가 모델

SYSTEM = (
    '너는 한국어 보안 학습 포털의 콘텐츠 선별자다. 매일 들어오는 취약점 정보 중 '
    '"이 포털에 새 학습 콘텐츠로 만들거나 기존 콘텐츠를 갱신할 가치가 있는 것"만 고른다. '
    '판정은 build / dup / ignore 셋 중 하나다. '
    'build = 새롭고 페이지 내부 mock 으로 교육적 재현이 가능하다. '
    'dup = 이미 다루는 취약점 계열이라 새 페이지가 중복이다(기존 갱신은 별도). '
    'ignore = 특정 제품의 힙 오버플로/인증 우회처럼 mock 으로 재현하면 실제를 오도한다. '
    '출력은 JSON 배열만. 각 원소는 {"n":번호,"decision":"build|dup|ignore",'
    '"track":"13_ai 같은 기둥 접두사 또는 update:<파일>","cwe":"CWE-89","reason":"한 문장"}. '
    '새 기둥 접두사를 지어내지 마라 — 주어진 기둥 목록 안에서만 고른다. '
    '다른 텍스트 없이 JSON 배열만 출력한다.')


def coverage_summary(conn):
    """기존 콘텐츠 요약 — 에이전트의 중복 판정 근거. content-registry 도메인."""
    reg_path = os.path.join(os.path.dirname(HERE), 'public', 'data', 'content-registry.json')
    lines = []
    try:
        with open(reg_path, encoding='utf-8') as fh:
            reg = json.load(fh)
        for d in reg.get('domains', []):
            lines.append('  %s (%s): %d개' % (d.get('prefix'), d.get('label'), d.get('count')))
    except (OSError, ValueError):
        lines.append('  (레지스트리를 읽지 못함)')
    return '\n'.join(lines)


def today_build_count():
    if not os.path.isdir(TICKETS):
        return 0
    today = datetime.date.today().isoformat()
    return sum(1 for f in os.listdir(TICKETS) if f.startswith('t-' + today.replace('-', '')))


def slugify(canonical_id, title, n):
    base = (canonical_id or title or ('item%d' % n)).lower()
    base = re.sub(r'[^a-z0-9]+', '-', base).strip('-')
    return base[:40] or ('item%d' % n)


def dry_stub(rows):
    """드라이런 판정. 실제 에이전트처럼 상한을 모른 채 순수 판정만 낸다 —
    상한 강제는 main 이 한다(설계: 상한이 프롬프트 설득 대상이면 상한이 아니다).
    점수 상위는 build, 미달은 ignore. 상한 초과 build 는 main 이 큐에 남긴다."""
    out = []
    for i, r in enumerate(rows, 1):
        text = ((r['title'] or '') + ' ' + (r['summary'] or '')).lower()
        is_ai = any(k in text for k in ('llm', 'prompt injection', 'ai ', 'model'))
        if r['priority'] >= MIN_BUILD_PRIORITY:
            out.append({'n': i, 'decision': 'build',
                        'track': '13_ai' if is_ai else 'update:incident.html',
                        'cwe': 'CWE-0', 'reason': '(dryrun) 점수 %d' % r['priority']})
        else:
            out.append({'n': i, 'decision': 'ignore', 'track': '', 'cwe': '',
                        'reason': '(dryrun) 점수 미달'})
    return out


def build_prompt(rows, coverage):
    lines = ['이 포털이 이미 다루는 기둥:', coverage, '',
             '아래 취약점 각각을 build/dup/ignore 로 판정하라(번호 n 그대로 사용):', '']
    for i, r in enumerate(rows, 1):
        lines.append('%d. [%s] %s (점수 %d%s)'
                     % (i, r['canonical_id'] or '-', (r['title'] or '')[:90],
                        r['priority'], ' CVSS %.1f' % r['cvss'] if r['cvss'] else ''))
        if r['summary']:
            lines.append('   %s' % r['summary'][:200])
    return '\n'.join(lines)


def main():
    args = sys.argv[1:]
    batch = int(args[args.index('--batch') + 1]) if '--batch' in args else BATCH

    conn = state.init()
    made = today_build_count()
    room = max(0, MAX_BUILDS - made)
    print('오늘 만든 build 티켓 %d / 상한 %d — 남은 여유 %d' % (made, MAX_BUILDS, room))

    rows = conn.execute(
        "SELECT * FROM items WHERE status='queued' ORDER BY priority DESC, cvss DESC LIMIT ?",
        (batch,)).fetchall()
    if not rows:
        print('선별할 queued 항목이 없습니다.')
        return 0
    print('배치 %d건 선별 시작 (드라이런=%s)'
          % (len(rows), os.environ.get('WVS_AGENT_DRYRUN') == '1'))

    coverage = coverage_summary(conn)
    prompt = build_prompt(rows, coverage)
    res = agent.run_agent(prompt, system=SYSTEM, model=MODEL,
                          dry_stub=lambda: dry_stub(rows))
    if not res['ok']:
        print('선별 실패: ' + res.get('error', '?'))
        return 1
    verdicts = res['data']
    if not isinstance(verdicts, list):
        print('선별 응답이 배열이 아님')
        return 1

    os.makedirs(TICKETS, exist_ok=True)
    by_n = {v.get('n'): v for v in verdicts if isinstance(v, dict)}
    builds = 0
    dropped = 0
    deferred = 0
    for i, r in enumerate(rows, 1):
        v = by_n.get(i)
        if not v:
            continue
        dec = v.get('decision')
        if dec == 'build':
            if builds >= room:
                deferred += 1          # 상한 초과 — status 그대로 queued 로 남김
                continue
            ticket_id = 't-%s-%s' % (datetime.date.today().isoformat().replace('-', ''),
                                     slugify(r['canonical_id'], r['title'], i))
            ticket = {
                'id': ticket_id,
                'canonical_id': r['canonical_id'],
                'source': r['source'],
                'title': r['title'],
                'summary': r['summary'],
                'url': r['url'],
                'decision': 'build',
                'track': v.get('track', ''),
                'cwe': v.get('cwe', ''),
                'reason': v.get('reason', ''),
                'item_uid': r['uid'],
                'created_at': state.now(),
                'status': 'awaiting_build',   # 4~5단계 작성 대기
            }
            with open(os.path.join(TICKETS, ticket_id + '.json'), 'w', encoding='utf-8') as fh:
                json.dump(ticket, fh, ensure_ascii=False, indent=2)
            conn.execute("UPDATE items SET status='triaged', run_id=? WHERE uid=?",
                         (ticket_id, r['uid']))
            builds += 1
        else:
            conn.execute("UPDATE items SET status='dropped' WHERE uid=?", (r['uid'],))
            dropped += 1
    conn.commit()

    print('결과: build %d(티켓 생성) · dropped %d · 상한초과 보류 %d' % (builds, dropped, deferred))
    print('상태: ' + ', '.join('%s=%d' % (k, v)
          for k, v in sorted(state.counts_by_status(conn).items())))
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
