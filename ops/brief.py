#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 2단계] 숫자 브리프. 모델을 쓰지 않는다.

매일 아침(설계상 07:30 cron) 사람이 5분 안에 "어젯밤 이 분야에서 무엇이 나왔나"
를 파악하게 해 준다. 집계와 정렬만 하므로 LLM 이 죽어도, 쿼터가 바닥나도 이
브리프는 나간다 — 관측이 모델에 의존하면 모델이 죽은 날 사람이 장님이 된다.

3단계 이후에는 A4(브리프 서술자)가 이 숫자 위에 '어젯밤 무엇이 진짜 문제였나'
한 문단을 얹지만, 그건 선택이고 이 숫자 브리프가 토대다.

산출: ops/brief/YYYY-MM-DD.md + stdout.

사용:
  python ops/brief.py            # 최근 24시간 수집분
  python ops/brief.py --hours 48
  python ops/brief.py --all      # 전체 대기 항목(초기 백필 점검용)
"""
import datetime
import json
import os
import sys

import state
import agent

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_DIR = os.path.join(HERE, 'brief')
TICKETS = os.path.join(HERE, 'queue', 'tickets')
DEAD = os.path.join(HERE, 'deadletter')

AI_HINT = ('llm', 'prompt injection', 'machine learning', 'jailbreak',
           'ai model', 'neural', 'model poison')


def gather_signals():
    """A4 가 서술할 사고/대기 신호. 없으면 빈 dict — 평온한 날엔 A4 를 안 부른다."""
    sig = {}
    if os.path.isdir(TICKETS):
        pend, dead_status = 0, 0
        for f in os.listdir(TICKETS):
            if not f.endswith('.json'):
                continue
            try:
                with open(os.path.join(TICKETS, f), encoding='utf-8') as fh:
                    st = json.load(fh).get('status')
            except (OSError, ValueError):
                continue
            if st == 'pending':
                pend += 1
            elif st == 'deadletter':
                dead_status += 1
        if pend:
            sig['pending'] = pend
    if os.path.isdir(DEAD):
        n = len([f for f in os.listdir(DEAD) if f.endswith('.json')])
        if n:
            sig['deadletter'] = n
    return sig


def narrate(signals):
    """A4 브리프 서술자. 사고/대기가 있을 때만 한 문단을 얹는다. 모델이 죽어도
    숫자 브리프는 나가야 하므로, 실패하면 None 을 돌려 서술 없이 진행한다."""
    if not signals:
        return None
    prompt = ('어젯밤 콘텐츠 파이프라인 상태 신호: ' + json.dumps(signals, ensure_ascii=False)
              + '. 사람이 5분 안에 파악하도록 한 문단(3문장 이내)으로 요약하고, 승인 대기가'
              + ' 있으면 무엇부터 볼지 제안하라. JSON {"narration":"..."} 로만 답하라.')
    res = agent.run_agent(
        prompt, model='claude-haiku-4-5-20251001',
        dry_stub=lambda: {'narration': '(dryrun) 승인 대기 %d건, 데드레터 %d건. '
                          '승인 대기부터 확인 권장.'
                          % (signals.get('pending', 0), signals.get('deadletter', 0))})
    if res.get('ok') and isinstance(res.get('data'), dict):
        return res['data'].get('narration')
    return None


def render(conn, since_epoch, scope_label):
    cnt = state.counts_by_status(conn)

    where = '' if since_epoch is None else 'AND fetched_at>=%d' % since_epoch
    top = conn.execute(
        """SELECT canonical_id, title, summary, cvss, priority, source, url
           FROM items WHERE status IN ('new','queued') %s
           ORDER BY priority DESC, cvss DESC LIMIT 15""" % where).fetchall()
    recent = conn.execute(
        "SELECT COUNT(*) n FROM items WHERE 1=1 %s" % where).fetchall()[0]['n']
    by_source = conn.execute(
        """SELECT source, COUNT(*) n FROM items WHERE 1=1 %s
           GROUP BY source ORDER BY n DESC""" % where).fetchall()

    ai_n = 0
    for r in conn.execute(
            "SELECT title, summary FROM items WHERE 1=1 %s" % where).fetchall():
        t = ((r['title'] or '') + ' ' + (r['summary'] or '')).lower()
        if any(k in t for k in AI_HINT):
            ai_n += 1

    today = datetime.date.today().isoformat()
    L = []
    L.append('# 파이프라인 브리프 — %s' % today)
    L.append('')
    L.append('> 범위: %s · 모델 없이 집계만' % scope_label)
    L.append('')
    # A4 서술: 사고/대기가 있는 날만. 숫자 브리프 위에 한 문단(모델 죽어도 숫자는 나감).
    signals = gather_signals()
    narration = narrate(signals) if signals else None
    if narration:
        L.append('## 어젯밤 요약 (A4)')
        L.append('')
        L.append('> ' + narration)
        L.append('')

    L.append('## 한눈에')
    L.append('')
    L.append('- 이 범위 유입: **%d건** (AI/ML 관련 %d건)' % (recent, ai_n))
    L.append('- 소스별: ' + (' · '.join('%s %d' % (r['source'], r['n']) for r in by_source) or '없음'))
    L.append('- 전체 상태: ' + (', '.join('%s %d' % (k, v) for k, v in sorted(cnt.items())) or '비어있음'))
    L.append('')
    L.append('## 우선순위 상위 (콘텐츠화 후보)')
    L.append('')
    if not top:
        L.append('_이 범위에 항목이 없습니다._')
    else:
        L.append('| 점수 | CVSS | ID | 소스 | 제목 |')
        L.append('|--:|--:|:--|:--|:--|')
        for r in top:
            title = (r['title'] or '')[:70].replace('|', '\\|')
            cid = r['canonical_id'] or '-'
            cvss = ('%.1f' % r['cvss']) if r['cvss'] else '-'
            L.append('| %d | %s | %s | %s | %s |'
                     % (r['priority'], cvss, cid, r['source'], title))
    L.append('')
    L.append('## 다음 행동')
    L.append('')
    L.append('- 3단계(A1 선별) 가동 전이므로, 위 목록은 사람이 직접 골라 '
             '기존 493개 콘텐츠 갱신·보강에 쓸 수 있습니다.')
    L.append('- 콘텐츠화는 원문 재구성 방침을 지킵니다(사실만 추출, 원문 전재 금지).')
    L.append('')
    return '\n'.join(L)


def main():
    args = sys.argv[1:]
    if '--all' in args:
        since, label = None, '전체 대기 항목'
    else:
        hours = 24
        if '--hours' in args:
            hours = int(args[args.index('--hours') + 1])
        since, label = state.now() - hours * 3600, '최근 %d시간' % hours

    conn = state.init()
    md = render(conn, since, label)
    conn.close()

    os.makedirs(BRIEF_DIR, exist_ok=True)
    path = os.path.join(BRIEF_DIR, datetime.date.today().isoformat() + '.md')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(md)

    print(md)
    print('\n(저장: %s)' % os.path.relpath(path, os.path.dirname(HERE)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
