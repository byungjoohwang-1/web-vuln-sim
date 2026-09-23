#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ops 파이프라인 라이브 대시보드 (로컬 전용, LAN·스마트폰 접속용).

`state.db` 를 **읽기 전용**으로 열어 7단계 파이프라인의 현재 상태를 한 화면에
띄운다. 파이프라인을 조작하지 않는다 — 오직 관측만 한다(read-only). 폰에서 같은
와이파이로 http://<이-PC-LAN-IP>:8787 로 들어오면 실시간으로 상태가 보인다.

  python ops/dashboard.py                 # 0.0.0.0:8787 로 서빙(기본)
  python ops/dashboard.py --port 9000     # 포트 지정
  python ops/dashboard.py --host 127.0.0.1  # 로컬만(폰 접속 차단)

노출 데이터: 공개 취약점 피드(KEV·NVD·GHSA)에서 수집한 사실과 파이프라인 진행
상태뿐이다. 자격증명·비밀은 state.db 에 없다. 그래도 가정용 LAN 밖으로는 열지
않는다(인증 없음 — 신뢰된 사설망 전제). 라우터 포트포워딩 금지.

프런트엔드는 10초마다 /api/state 를 폴링해 부분 갱신한다(폰 데이터·배터리 절약).
"""
import argparse
import json
import os
import socket
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB_PATH = os.path.join(HERE, 'state.db')
TICKETS = os.path.join(HERE, 'queue', 'tickets')
BRIEF_DIR = os.path.join(HERE, 'brief')

# fetch_feeds 는 20분 주기 cron. 이 배수를 넘겨 소식이 없으면 '지연'으로 본다.
FETCH_PERIOD = 20 * 60


def _ro_conn():
    """state.db 를 읽기 전용 URI 로 연다. WAL 이 활성이어도 안전하게 읽는다."""
    uri = 'file:' + DB_PATH.replace('\\', '/') + '?mode=ro'
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=5000')
    return conn


def _rows(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def load_tickets():
    out = []
    if not os.path.isdir(TICKETS):
        return out
    for f in sorted(os.listdir(TICKETS)):
        if f.endswith('.json'):
            try:
                with open(os.path.join(TICKETS, f), encoding='utf-8') as fh:
                    out.append(json.load(fh))
            except Exception:
                pass
    return out


def latest_brief():
    if not os.path.isdir(BRIEF_DIR):
        return None, None
    files = sorted(f for f in os.listdir(BRIEF_DIR) if f.endswith('.md'))
    if not files:
        return None, None
    name = files[-1]
    try:
        with open(os.path.join(BRIEF_DIR, name), encoding='utf-8') as fh:
            return name[:-3], fh.read()
    except Exception:
        return name[:-3], None


def lan_ips():
    """이 PC 의 접속 가능한 IPv4 후보(가상 어댑터 제외 시도)."""
    ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
    except Exception:
        pass
    # 가상 어댑터로 흔한 대역을 뒤로 밀어 실제 LAN 을 먼저 보여준다.
    def rank(ip):
        if ip.startswith('192.168.56.') or ip.startswith('192.168.174.') \
                or ip.startswith('192.168.98.') or ip.startswith('172.'):
            return 1
        return 0
    ips.sort(key=rank)
    return ips


def snapshot():
    """대시보드가 그릴 전체 상태 스냅샷(JSON 직렬화 가능 dict)."""
    now = int(time.time())
    snap = {'now': now, 'ok': True}
    try:
        conn = _ro_conn()
    except Exception as e:
        snap['ok'] = False
        snap['error'] = 'state.db 를 열 수 없습니다: ' + str(e)
        return snap
    try:
        # 상태별 건수
        snap['status'] = {r['status']: r['n'] for r in
                          conn.execute('SELECT status, COUNT(*) n FROM items GROUP BY status')}
        snap['total_items'] = sum(snap['status'].values())
        # 소스별 건수
        snap['by_source'] = {r['source']: r['n'] for r in
                             conn.execute('SELECT source, COUNT(*) n FROM items GROUP BY source')}
        # AI/ML 관련(전략 축) — 우선순위 점수에 AI 가점(+20)이 반영된 항목 근사
        snap['ai_items'] = conn.execute(
            "SELECT COUNT(*) n FROM items WHERE lower(title||' '||coalesce(summary,'')) "
            "LIKE '%llm%' OR lower(title||' '||coalesce(summary,'')) LIKE '%prompt injection%' "
            "OR lower(title||' '||coalesce(summary,'')) LIKE '%machine learning%' "
            "OR lower(title||' '||coalesce(summary,'')) LIKE '%ai model%'").fetchone()['n']
        # 콘텐츠화 후보 상위(선별 전 큐)
        snap['queue'] = _rows(conn,
            "SELECT canonical_id, source, title, cvss, priority, status, published_at "
            "FROM items WHERE status IN ('new','queued') "
            "ORDER BY priority DESC, cvss DESC NULLS LAST, fetched_at DESC LIMIT 15")
        # 최근 유입
        snap['recent'] = _rows(conn,
            "SELECT canonical_id, source, title, cvss, priority, fetched_at "
            "FROM items ORDER BY fetched_at DESC LIMIT 8")
        # 24시간 유입
        snap['intake_24h'] = conn.execute(
            'SELECT COUNT(*) n FROM items WHERE fetched_at >= ?', (now - 86400,)).fetchone()['n']
        # 피드 커서(수집 건강)
        snap['cursors'] = _rows(conn,
            'SELECT source, last_fetch, backoff_until FROM cursors ORDER BY source')
        # 파이프라인 실행 이력
        snap['runs'] = _rows(conn,
            'SELECT run_id, item_uid, phase, started_at, ended_at, gate_verdict, '
            'review_verdict, approved_at, deployed_at FROM runs ORDER BY started_at DESC LIMIT 10')
        snap['runs_total'] = conn.execute('SELECT COUNT(*) n FROM runs').fetchone()['n']
        # 예산(토큰 원장)
        snap['budget'] = _rows(conn,
            'SELECT window_start, calls, tokens_in, tokens_out FROM budget '
            'ORDER BY window_start DESC LIMIT 3')
        # deadletter
        snap['deadletter'] = conn.execute('SELECT COUNT(*) n FROM deadletter').fetchone()['n']
    except Exception as e:
        snap['ok'] = False
        snap['error'] = str(e)
    finally:
        conn.close()

    # 티켓(파일 기반, 3단계+ 산출물)
    tickets = load_tickets()
    tstatus = {}
    for t in tickets:
        s = t.get('status', 'unknown')
        tstatus[s] = tstatus.get(s, 0) + 1
    snap['tickets'] = tstatus
    snap['tickets_total'] = len(tickets)
    snap['pending_tickets'] = [
        {'id': t.get('id'), 'title': t.get('title') or t.get('canonical_id'),
         'status': t.get('status'), 'created_at': t.get('created_at')}
        for t in tickets if t.get('status') in ('pending', 'gate-pass', 'awaiting_build')
    ][:10]

    # 브리프
    bdate, btext = latest_brief()
    snap['brief_date'] = bdate
    snap['brief_text'] = btext

    # 피드 신선도 판정
    fresh = None
    if snap.get('cursors'):
        last = max((c['last_fetch'] or 0) for c in snap['cursors'])
        if last:
            fresh = now - last
    snap['feed_age'] = fresh
    snap['feed_stale'] = (fresh is not None and fresh > FETCH_PERIOD * 2)
    return snap


PAGE = r"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b1220">
<title>WVS 파이프라인 라이브 — 콘텐츠 자동화 관제</title>
<style>
:root{--bg:#0b1220;--panel:#111a2e;--panel2:#0f172a;--panel3:#16233c;--bd:#22314f;
 --ink:#e6edf7;--muted:#93a4c0;--acc:#22d3ee;--good:#3fb950;--bad:#f85149;--warn:#e3a008;
 --mono:'JetBrains Mono','Consolas',monospace}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.6 "Segoe UI","Malgun Gothic",sans-serif;
 padding:0 0 60px;-webkit-text-size-adjust:100%}
.top{position:sticky;top:0;z-index:9;background:#0b1220ee;backdrop-filter:blur(6px);
 border-bottom:1px solid var(--bd);padding:12px 16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.top h1{font-size:17px;color:#fff;display:flex;align-items:center;gap:8px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--good);box-shadow:0 0 8px var(--good);
 animation:pulse 2s infinite}
.dot.stale{background:var(--warn);box-shadow:0 0 8px var(--warn)}
.dot.err{background:var(--bad);box-shadow:0 0 8px var(--bad)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.sp{margin-left:auto}
.meta{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.wrap{max-width:1200px;margin:0 auto;padding:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--bd);border-radius:12px;padding:14px 16px}
.card h2{font-size:12px;text-transform:uppercase;letter-spacing:.5px;color:var(--acc);
 font-family:var(--mono);margin-bottom:10px;display:flex;gap:8px;align-items:center}
.big{font-size:30px;font-weight:800;color:#fff;font-family:var(--mono)}
.big small{font-size:13px;color:var(--muted);font-weight:400;margin-left:6px}
.kv{display:flex;justify-content:space-between;font-family:var(--mono);font-size:12.5px;
 padding:4px 0;border-bottom:1px dashed #1e2b47}
.kv:last-child{border:0}.kv b{color:#fff}
.pill{display:inline-block;font-family:var(--mono);font-size:11px;padding:1px 7px;border-radius:999px;
 border:1px solid var(--bd);color:var(--muted);margin:2px 4px 2px 0}
.flow{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 0}
.stage{flex:1;min-width:92px;background:var(--panel2);border:1px solid var(--bd);border-radius:10px;
 padding:9px 10px;text-align:center;position:relative}
.stage .n{font-family:var(--mono);font-size:10px;color:var(--muted)}
.stage .v{font-size:20px;font-weight:800;color:#fff;font-family:var(--mono)}
.stage .lb{font-size:11px;color:var(--muted);margin-top:2px}
.stage.live{border-color:var(--good)}.stage.live .v{color:var(--good)}
.stage.armed{border-color:#2a3a5c}
.stage.idle{opacity:.6}
tbl,table{width:100%;border-collapse:collapse}
th,td{text-align:left;font-size:12px;padding:6px 8px;border-bottom:1px solid #1a2740;vertical-align:top}
th{color:var(--muted);font-family:var(--mono);font-weight:600;font-size:10.5px;text-transform:uppercase}
td.mono,.mono{font-family:var(--mono)}
.src{font-family:var(--mono);font-size:10px;padding:1px 6px;border-radius:5px;color:#062a30}
.src.kev{background:#fca5a5}.src.nvd{background:#7dd3fc}.src.ghsa{background:#c4b5fd}
.score{font-family:var(--mono);font-weight:700;color:var(--warn)}
.cvss{font-family:var(--mono);color:var(--muted)}
.title{color:var(--ink)}
.full{grid-column:1/-1}
.brief{white-space:pre-wrap;font-size:12.5px;line-height:1.6;color:#cdd9ec;font-family:var(--mono);
 max-height:340px;overflow:auto;background:var(--panel2);border:1px solid var(--bd);border-radius:10px;padding:12px}
.note{font-size:12px;color:var(--muted);margin-top:6px}
.err{background:#3a1518;border:1px solid var(--bad);color:#fecaca;padding:12px;border-radius:10px}
a{color:#67e8f9}
.access{font-family:var(--mono);font-size:12px;color:var(--muted)}
.access b{color:var(--acc)}
@media(max-width:600px){.big{font-size:26px}.stage{min-width:80px}}
</style></head>
<body>
<div class="top">
  <h1><span class="dot" id="dot"></span> WVS 파이프라인 <span class="meta">라이브 관제</span></h1>
  <span class="sp"></span>
  <span class="meta" id="clock">—</span>
</div>
<div class="wrap">
  <div id="err"></div>
  <div class="grid">
    <div class="card"><h2>수집 상태 · Feeds</h2>
      <div class="big" id="totalItems">—<small>누적 항목</small></div>
      <div class="kv"><span>24시간 유입</span><b id="intake24">—</b></div>
      <div class="kv"><span>AI/ML 관련</span><b id="aiItems">—</b></div>
      <div class="kv"><span>피드 신선도</span><b id="feedAge">—</b></div>
      <div id="sources" style="margin-top:8px"></div>
    </div>
    <div class="card"><h2>파이프라인 · 7단계 흐름</h2>
      <div class="flow" id="flow"></div>
      <div class="note" id="flowNote"></div>
    </div>
    <div class="card"><h2>승인 대기 · Human gate</h2>
      <div class="big" id="pendingN">—<small>티켓</small></div>
      <div id="pendingList" style="margin-top:8px"></div>
      <div class="note">사람이 <span class="mono">publish.py &lt;ticket&gt; --deploy</span> 로 승인해야 배포됩니다.</div>
    </div>
  </div>

  <div class="grid" style="margin-top:12px">
    <div class="card full"><h2>콘텐츠화 후보 · 선별 대기 상위</h2>
      <table><thead><tr><th>점수</th><th>CVSS</th><th>ID</th><th>소스</th><th>제목</th></tr></thead>
      <tbody id="queue"></tbody></table>
    </div>
  </div>

  <div class="grid" style="margin-top:12px">
    <div class="card"><h2>최근 유입</h2><table><tbody id="recent"></tbody></table></div>
    <div class="card"><h2>실행 이력 · Runs</h2>
      <div class="big" id="runsN">—<small>총 실행</small></div>
      <table><tbody id="runs"></tbody></table>
      <div class="note" id="runsNote"></div>
    </div>
  </div>

  <div class="grid" style="margin-top:12px">
    <div class="card full"><h2 id="briefH">오늘의 브리프</h2>
      <div class="brief" id="brief">—</div>
    </div>
  </div>

  <div class="card full" style="margin-top:12px"><h2>접속 안내</h2>
    <div class="access" id="access">—</div>
    <div class="note">이 대시보드는 관측 전용입니다(read-only). 가정용 사설망 안에서만 접속하세요 — 라우터 포트포워딩 금지.</div>
  </div>
</div>
<script>
var STAGES=[
 {k:'fetch',n:'1',lb:'수집'},{k:'triage',n:'3',lb:'선별 A1'},
 {k:'build',n:'5',lb:'작성 A2'},{k:'review',n:'6',lb:'검토 A3'},
 {k:'pending',n:'6',lb:'승인대기'},{k:'published',n:'7',lb:'발행'}];
function esc(s){return (s==null?'':(''+s)).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function ago(sec){if(sec==null)return '—';sec=Math.max(0,sec);
 if(sec<90)return sec+'초 전';if(sec<5400)return Math.round(sec/60)+'분 전';
 if(sec<172800)return Math.round(sec/3600)+'시간 전';return Math.round(sec/86400)+'일 전';}
function tsAgo(now,t){if(!t)return '—';return ago(now-t);}
function render(d){
 var dot=document.getElementById('dot'), err=document.getElementById('err');
 if(!d.ok){dot.className='dot err';err.innerHTML='<div class="err">'+esc(d.error||'상태를 읽을 수 없습니다')+'</div>';return;}
 err.innerHTML='';
 dot.className='dot'+(d.feed_stale?' stale':'');
 document.getElementById('clock').textContent=new Date(d.now*1000).toLocaleTimeString('ko-KR')+' 갱신';
 document.getElementById('totalItems').innerHTML=(d.total_items||0).toLocaleString()+'<small>누적 항목</small>';
 document.getElementById('intake24').textContent=(d.intake_24h||0).toLocaleString()+' 건';
 document.getElementById('aiItems').textContent=(d.ai_items||0).toLocaleString()+' 건';
 var fa=document.getElementById('feedAge');
 fa.textContent=ago(d.feed_age)+(d.feed_stale?' ⚠ 지연':' ✓');
 fa.style.color=d.feed_stale?'var(--warn)':'var(--good)';
 // 소스
 var sh='';for(var s in (d.by_source||{})){sh+='<span class="pill">'+esc(s)+' '+d.by_source[s].toLocaleString()+'</span>';}
 document.getElementById('sources').innerHTML=sh;
 // 흐름
 var st=d.status||{}, tk=d.tickets||{};
 var counts={fetch:d.total_items||0,triage:tk['awaiting_build']||0,build:tk['building']||0,
  review:tk['gate-pass']||0,pending:tk['pending']||0,published:tk['published']||0};
 var live={fetch:!d.feed_stale};
 var fh='';STAGES.forEach(function(g){
  var v=counts[g.k]||0; var cls=g.k==='fetch'?(d.feed_stale?'armed':'live'):(v>0?'live':'armed');
  fh+='<div class="stage '+cls+'"><div class="n">'+g.n+'</div><div class="v">'+v.toLocaleString()+'</div><div class="lb">'+g.lb+'</div></div>';
 });
 document.getElementById('flow').innerHTML=fh;
 var runs=d.runs_total||0;
 document.getElementById('flowNote').innerHTML=runs>0
  ? 'LLM 단계(선별·작성·검토) 실행 '+runs+'회 — 에이전트 가동 중.'
  : '수집·브리프는 자동 가동 중. LLM 단계(선별·작성·검토)는 대기(첫 독립 검증 후 tick cron 등록).';
 // 승인 대기
 document.getElementById('pendingN').innerHTML=(tk['pending']||0)+'<small>티켓</small>';
 var pl='';(d.pending_tickets||[]).forEach(function(t){
  pl+='<div class="kv"><span class="title">'+esc(t.title||t.id)+'</span><b>'+esc(t.status)+'</b></div>';});
 document.getElementById('pendingList').innerHTML=pl||'<div class="note">대기 중인 티켓이 없습니다.</div>';
 // 큐
 var qh='';(d.queue||[]).forEach(function(r){
  qh+='<tr><td class="score">'+(r.priority||0)+'</td><td class="cvss">'+(r.cvss==null?'—':r.cvss)+'</td>'
   +'<td class="mono">'+esc(r.canonical_id||'')+'</td>'
   +'<td><span class="src '+esc(r.source)+'">'+esc(r.source)+'</span></td>'
   +'<td class="title">'+esc((r.title||'').slice(0,90))+'</td></tr>';});
 document.getElementById('queue').innerHTML=qh||'<tr><td colspan="5" class="note">큐가 비어 있습니다.</td></tr>';
 // 최근
 var rh='';(d.recent||[]).forEach(function(r){
  rh+='<tr><td><span class="src '+esc(r.source)+'">'+esc(r.source)+'</span></td>'
   +'<td class="mono">'+esc(r.canonical_id||'')+'</td>'
   +'<td class="title">'+esc((r.title||'').slice(0,60))+'</td>'
   +'<td class="mono" style="color:var(--muted)">'+tsAgo(d.now,r.fetched_at)+'</td></tr>';});
 document.getElementById('recent').innerHTML=rh||'<tr><td class="note">—</td></tr>';
 // runs
 document.getElementById('runsN').innerHTML=runs+'<small>총 실행</small>';
 var rr='';(d.runs||[]).forEach(function(r){
  rr+='<tr><td class="mono">'+esc(r.phase||'')+'</td><td class="mono">'+esc((r.gate_verdict||r.review_verdict||'-'))+'</td>'
   +'<td class="mono" style="color:var(--muted)">'+tsAgo(d.now,r.started_at)+'</td></tr>';});
 document.getElementById('runs').innerHTML=rr;
 document.getElementById('runsNote').textContent = runs===0
  ? '아직 실행 이력이 없습니다 (LLM 단계 미가동).' : '';
 // 브리프
 document.getElementById('briefH').textContent=d.brief_date?('브리프 · '+d.brief_date):'오늘의 브리프';
 document.getElementById('brief').textContent=d.brief_text||'브리프가 아직 생성되지 않았습니다.';
}
function tick(){
 fetch('/api/state',{cache:'no-store'}).then(function(r){return r.json();}).then(render)
  .catch(function(e){document.getElementById('dot').className='dot err';
   document.getElementById('err').innerHTML='<div class="err">서버 응답 없음: '+esc(e.message)+'</div>';});
}
tick();setInterval(tick,10000);
// 접속 안내는 서버가 주입
fetch('/api/access',{cache:'no-store'}).then(function(r){return r.json();}).then(function(a){
 var urls=a.urls||[];
 if(!urls.length){document.getElementById('access').textContent='접속 주소를 찾지 못했습니다.';return;}
 var h='폰에서 같은 와이파이로 접속(주소창에 입력):<br><b style="font-size:16px">'+esc(urls[0])+'</b>';
 if(urls.length>1){h+='<br><span style="color:#64748b">위 주소가 안 되면(가상 어댑터일 수 있음): '
  +urls.slice(1).map(function(u){return esc(u);}).join(' · ')+'</span>';}
 document.getElementById('access').innerHTML=h;}).catch(function(){});
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_port = 8787  # main() 에서 갱신

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/' or path == '/index.html':
            self._send(200, PAGE, 'text/html; charset=utf-8')
        elif path == '/api/state':
            self._send(200, json.dumps(snapshot(), ensure_ascii=False))
        elif path == '/api/access':
            urls = ['http://%s:%d' % (ip, self.server_port) for ip in lan_ips()]
            self._send(200, json.dumps({'urls': urls}, ensure_ascii=False))
        elif path == '/healthz':
            self._send(200, json.dumps({'ok': True}))
        else:
            self._send(404, json.dumps({'error': 'not found'}))

    def log_message(self, *a):  # 콘솔 소음 억제
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8787)
    ap.add_argument('--host', default='0.0.0.0')
    args = ap.parse_args()
    Handler.server_port = args.port
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    banner = '=' * 56
    print(banner)
    print(' WVS 파이프라인 라이브 대시보드 (read-only)'.encode('ascii', 'replace').decode())
    print(banner)
    print(' local : http://127.0.0.1:%d' % args.port)
    if args.host == '0.0.0.0':
        for ip in lan_ips():
            print(' phone : http://%s:%d' % (ip, args.port))
    print(' (Ctrl+C to stop)')
    print(banner)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nstopped.')


if __name__ == '__main__':
    main()
