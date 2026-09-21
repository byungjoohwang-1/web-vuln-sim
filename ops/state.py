#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""파이프라인 공용 상태 저장소 (SQLite, WAL).

수집·선별·작성·검토·발행의 모든 상태를 에이전트 머릿속이 아니라 DB 행에 둔다.
정전·재부팅·429 로 프로세스가 죽어도 다음 tick 이 같은 지점에서 재개할 수 있게
하기 위해서다. fetch_feeds / brief / tick / (나중에) 에이전트 실행기가 이 모듈을
공유한다.

테이블
  items    수집된 취약점 항목. canonical_id(CVE/GHSA 번호) UNIQUE 로 중복 접기.
  cursors  피드별 ETag/Last-Modified 커서 — 조건부 요청으로 대역폭 절약.
  runs     항목 하나가 티켓→작성→게이트→검토→발행으로 가는 이력(3단계+ 사용).
  budget   5시간 창 단위 토큰·호출 원장(3단계+ 에이전트가 쿼터 지킬 때 사용).
  deadletter  두 번 실패해 사람이 봐야 하는 항목.

status 흐름(2단계에서는 new/queued 까지만 쓴다):
  new       수집됨, 아직 선별 안 함
  queued    사전 필터 통과, 선별 대기
  triaged   A1 선별 완료(티켓 생성/기각)  [3단계]
  building  A2 작성 중  [5단계]
  gate      게이트 검증 중  [4단계]
  review    A3 검토 중  [6단계]
  pending   검토 통과, 사람 승인 대기  [6단계]
  published 발행됨  [6단계]
  expired   72시간 미승인으로 만료  [7단계]
  dropped   선별에서 기각
"""
import os
import sqlite3
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, 'state.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  uid          TEXT PRIMARY KEY,   -- sha1(source|외부ID). 같은 소스 재수집 시 접힘
  canonical_id TEXT,               -- CVE-2026-1234 / GHSA-xxxx. 여러 소스 교차 중복 제거용
  source       TEXT NOT NULL,      -- kev | nvd | osv | ...
  url          TEXT,
  title        TEXT,
  summary      TEXT,               -- 400자 이내 요약(사실만, 원문 전재 아님)
  published_at TEXT,
  fetched_at   INTEGER,            -- epoch
  cvss         REAL,
  priority     INTEGER DEFAULT 0,  -- 사전 필터 점수(높을수록 먼저)
  status       TEXT DEFAULT 'new',
  lease_until  INTEGER,            -- 처리 리스: 만료되면 status 를 되돌려 재처리
  run_id       TEXT,
  body_hash    TEXT
);
CREATE INDEX IF NOT EXISTS idx_items_status   ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_priority ON items(priority DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_items_canonical
  ON items(canonical_id) WHERE canonical_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS cursors (
  source        TEXT PRIMARY KEY,
  etag          TEXT,
  last_modified TEXT,
  last_fetch    INTEGER,
  backoff_until INTEGER DEFAULT 0  -- 소스 장애 시 지수 백오프
);

CREATE TABLE IF NOT EXISTS runs (
  run_id        TEXT PRIMARY KEY,
  item_uid      TEXT,
  phase         TEXT,
  started_at    INTEGER,
  ended_at      INTEGER,
  gate_verdict  TEXT,
  review_verdict TEXT,
  approved_at   INTEGER,
  deployed_at   INTEGER,
  git_branch    TEXT,
  tokens_in     INTEGER DEFAULT 0,
  tokens_out    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS budget (
  window_start  INTEGER PRIMARY KEY,  -- 5시간 창 시작 epoch
  calls         INTEGER DEFAULT 0,
  tokens_in     INTEGER DEFAULT 0,
  tokens_out    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS deadletter (
  uid     TEXT,
  reason  TEXT,
  at      INTEGER
);
"""


def connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    return conn


def init():
    """스키마를 멱등 생성하고 연결을 돌려준다."""
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def now():
    return int(time.time())


def counts_by_status(conn):
    rows = conn.execute(
        'SELECT status, COUNT(*) n FROM items GROUP BY status').fetchall()
    return {r['status']: r['n'] for r in rows}


if __name__ == '__main__':
    # 직접 실행하면 스키마를 만들고 현재 상태를 찍는다(설치 확인용).
    c = init()
    print('state.db 초기화: ' + DB_PATH)
    print('항목 상태:', counts_by_status(c) or '(비어 있음)')
    c.close()
