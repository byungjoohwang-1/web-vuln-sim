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
import os
import sys

import state

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_DIR = os.path.join(HERE, 'brief')

AI_HINT = ('llm', 'prompt injection', 'machine learning', 'jailbreak',
           'ai model', 'neural', 'model poison')


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
