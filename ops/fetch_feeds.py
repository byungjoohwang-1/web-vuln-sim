#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""[파이프라인 2단계] 피드 수집기. 판단하지 않는다 — 받아서 정규화해 담을 뿐.

설계상 20분 주기 cron 으로 돈다(Windows 작업 스케줄러). 각 소스를 조건부 GET
(ETag/If-Modified-Since)으로 받아 state.db 의 items 에 upsert 한다. 304 면 본문을
받지 않는다. 소스 하나가 죽으면 그 소스만 지수 백오프로 격리하고 나머지는 계속
수집한다. 요약·번역·판정·콘텐츠화는 하지 않는다(그건 에이전트의 일).

중복 제거 두 겹:
  1) uid = sha1(source|외부ID)  — 같은 소스 재수집이 접힌다(INSERT OR IGNORE)
  2) canonical_id UNIQUE        — 같은 CVE 가 KEV·NVD 양쪽에서 와도 한 행

사용:
  python ops/fetch_feeds.py            # 전체 소스 수집
  python ops/fetch_feeds.py --source kev
  python ops/fetch_feeds.py --dry      # 받되 DB 에 쓰지 않고 건수만 보고
"""
import hashlib
import sys
import traceback

import state
import feeds


def uid_of(source, canonical_id, url):
    key = '%s|%s' % (source, canonical_id or url or '')
    return hashlib.sha1(key.encode('utf-8')).hexdigest()


def upsert(conn, it):
    """새 항목이면 insert(status=new), 이미 있으면 건드리지 않는다.
    이미 처리 중/발행된 항목을 재수집이 되돌리면 안 되기 때문이다."""
    uid = uid_of(it['source'], it.get('canonical_id'), it.get('url'))
    body_hash = hashlib.sha1(
        ((it.get('title') or '') + (it.get('summary') or '')).encode('utf-8')).hexdigest()
    # canonical_id 가 다른 소스에서 이미 들어왔는지 — 있으면 새로 만들지 않는다.
    if it.get('canonical_id'):
        dup = conn.execute(
            'SELECT uid FROM items WHERE canonical_id=?', (it['canonical_id'],)).fetchone()
        if dup:
            return False
    cur = conn.execute(
        """INSERT OR IGNORE INTO items
           (uid, canonical_id, source, url, title, summary, published_at,
            fetched_at, cvss, priority, status, body_hash)
           VALUES (?,?,?,?,?,?,?,?,?,?, 'new', ?)""",
        (uid, it.get('canonical_id'), it['source'], it.get('url'), it.get('title'),
         it.get('summary'), it.get('published_at'), state.now(), it.get('cvss'),
         it.get('priority', 0), body_hash))
    return cur.rowcount > 0


def promote_queued(conn, min_priority=10):
    """사전 필터: 점수가 임계 이상인 new 항목을 queued 로 올린다(선별 대기).
    임계 미만은 new 로 남아 브리프의 '기타' 로만 집계된다."""
    conn.execute(
        "UPDATE items SET status='queued' WHERE status='new' AND priority>=?",
        (min_priority,))


def main():
    args = sys.argv[1:]
    dry = '--dry' in args
    only = None
    if '--source' in args:
        only = args[args.index('--source') + 1]

    conn = state.init()
    total_new = 0
    for name, fn in feeds.SOURCES.items():
        if only and name != only:
            continue
        row = conn.execute('SELECT * FROM cursors WHERE source=?', (name,)).fetchone()
        cursor = dict(row) if row else {}
        if cursor.get('backoff_until', 0) > state.now():
            print('  [skip] %s — 백오프 중(%d초 남음)'
                  % (name, cursor['backoff_until'] - state.now()))
            continue
        try:
            items, etag, lm = fn(cursor)
        except Exception as e:  # noqa: BLE001 — 한 소스 장애가 전체를 멈추면 안 된다
            # 지수 백오프: 실패할수록 다음 시도를 미룬다(최대 6시간).
            prev = cursor.get('backoff_until', 0)
            base = 600
            delay = min(base * 2 if prev > state.now() else base, 21600)
            conn.execute(
                """INSERT INTO cursors(source, backoff_until, last_fetch)
                   VALUES(?,?,?)
                   ON CONFLICT(source) DO UPDATE SET backoff_until=?, last_fetch=?""",
                (name, state.now() + delay, state.now(), state.now() + delay, state.now()))
            conn.commit()
            print('  [FAIL] %s — %s (%d초 백오프)' % (name, str(e)[:80], delay))
            continue

        added = 0
        if not dry:
            for it in items:
                if upsert(conn, it):
                    added += 1
            conn.execute(
                """INSERT INTO cursors(source, etag, last_modified, last_fetch, backoff_until)
                   VALUES(?,?,?,?,0)
                   ON CONFLICT(source) DO UPDATE SET etag=?, last_modified=?,
                     last_fetch=?, backoff_until=0""",
                (name, etag, lm, state.now(), etag, lm, state.now()))
            conn.commit()
        total_new += added
        tag = '(dry) ' if dry else ''
        print('  [ok]   %s%s — 받음 %d · 신규 %d' % (tag, name, len(items), added))

    if not dry:
        promote_queued(conn)
        conn.commit()

    cnt = state.counts_by_status(conn)
    print('상태: ' + (', '.join('%s=%d' % (k, v) for k, v in sorted(cnt.items())) or '비어있음'))
    print('이번 수집 신규 %d건' % total_new)
    conn.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
