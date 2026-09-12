# -*- coding: utf-8 -*-
"""vuln-hub.html을 다크 SOC 미션 컨트롤로 재생성한다 (v3).

전략 — "카탈로그는 보존, 껍데기를 교체":
  1) 기존 허브에서 카탈로그 DOM(list-group 내부 전체, ~400 링크)을 추출
  2) 기존 <style> 블록을 추출해 카탈로그 스타일 연속성 유지 (신규 CSS가 뒤에서 덮어씀)
  3) 새 레이아웃 = SOC 탑바 + 히어로 + 운영자 콘솔(내 기록) + 미션 카드 + 도메인 그리드 + 전체 카탈로그 + 푸터
  4) 카탈로그의 펼침 그룹(groupA)은 접힘 처리 — 페이지 진입 시 메뉴 벽이 보이지 않게

백업: _gen/backup_vuln-hub_v2.html
멱등: 재실행 시 백업에서 다시 추출하므로 항상 동일 결과.
"""
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
FILE = os.path.join(BASE, 'vuln-hub.html')
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backup_vuln-hub_v2.html')


def extract(src):
    """기존 허브에서 (style블록, 카탈로그 DOM) 추출"""
    # 1) 첫 <style> 블록 (사이드바·카탈로그 스타일 — 라이트 body 규칙 포함, 신규 CSS로 덮음)
    m = re.search(r'<style>(.*?)</style>', src, re.S)
    old_css = m.group(1) if m else ''

    # 2) 카탈로그: menu-scroll > list-group 내부
    i = src.find('<div class="list-group list-group-flush">')
    j = src.find('<div id="page-content-wrapper">')
    assert i > 0 and j > i, '카탈로그 경계를 못 찾음'
    inner = src[i + len('<div class="list-group list-group-flush">'):j]
    # 끝의 닫는 div 3개 제거 (list-group / menu-scroll / sidebar-wrapper)
    s = inner.rstrip()
    for _ in range(3):
        s = s.rstrip()
        if s.endswith('</div>'):
            s = s[:-6]
    # 3) 기본 펼침 해제 — 메뉴 벽 제거
    s = s.replace('collapse show guide-body', 'collapse guide-body')
    s = re.sub(r'(guide-group g[A-E][^>]*aria-expanded=)"true"', r'\1"false"', s)
    return old_css, s


PAGE = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta name="theme-color" content="#0b1220"><link rel="manifest" href="/manifest.json">
<script src="/js/pwa.js" defer></script><link rel="preconnect" href="https://cdnjs.cloudflare.com"><link rel="preconnect" href="https://cdn.jsdelivr.net"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WEB-VULN-SIM — AI 보안 훈련 플랫폼 | 레드팀 아레나 · 425페이지 학습 허브</title>
<meta name="description" content="AI 레드팀 에이전트와 방어 대결, 생성-검증 폐루프 출제, 10개 보안 도메인 425페이지 학습 카탈로그. 어디서든 Ctrl+K로 검색.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="WEB-VULN-SIM 보안 학습 포털">
<meta property="og:title" content="WEB-VULN-SIM — AI 보안 훈련 플랫폼">
<meta property="og:description" content="AI가 공격하고, 당신이 막는다. 생성 → 적응 → 검증이 폐루프로 돌아가는 보안 훈련장.">
<meta property="og:url" content="https://vuln-sim.web.app/vuln-hub.html">
<meta property="og:image" content="https://vuln-sim.web.app/favicon.svg">
<meta name="twitter:card" content="summary">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>__OLD_CSS__</style>
    <style>
/* ═══ WVS SOC v3 — 미션 컨트롤 테마 (기존 카탈로그 스타일 위에 덮어씀) ═══ */
:root{
  --bg:#0b1220;--panel:#111a2e;--panel2:#0e1626;--line:#1e293b;--line2:#26334d;
  --txt:#dbe4f0;--sub:#8fa0ba;--acc:#38bdf8;--red:#ef4444;--green:#4ade80;--amber:#fbbf24;--violet:#a78bfa;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body.soc{background:var(--bg);color:var(--txt);font-family:'Segoe UI','Noto Sans KR','Malgun Gothic',sans-serif;overflow-x:hidden}
#wrapper{display:block;width:100%;height:auto}
#sidebar-wrapper{width:auto;background:none;box-shadow:none}
.menu-scroll{overflow:visible}
body.soc a{color:var(--acc)}

/* ── SOC 탑바 ── */
.soc-top{position:sticky;top:0;z-index:9500;display:flex;align-items:center;gap:18px;height:46px;padding:0 20px;
  background:rgba(8,14,26,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.soc-top .logo{display:flex;align-items:center;gap:9px;color:#fff;text-decoration:none;font-weight:800;font-size:.95rem;letter-spacing:.4px;white-space:nowrap}
.soc-top .logo .mk{color:var(--acc);font-size:1.1rem}
.soc-top .logo small{display:block;font-size:.58rem;color:var(--sub);font-weight:500;letter-spacing:1px}
.soc-top nav{display:flex;gap:2px;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none}
.soc-top nav::-webkit-scrollbar{display:none}
.soc-top nav a{color:var(--sub);text-decoration:none;font-size:.8rem;font-weight:600;padding:6px 12px;border-radius:8px;white-space:nowrap}
.soc-top nav a:hover{color:var(--txt);background:rgba(56,189,248,.08)}
.soc-top .kbtn{display:flex;align-items:center;gap:8px;background:var(--panel2);border:1px solid var(--line2);color:var(--sub);
  border-radius:8px;padding:6px 13px;font-size:.76rem;cursor:pointer;white-space:nowrap;font-family:inherit}
.soc-top .kbtn:hover{border-color:var(--acc);color:#7dd3fc}
.soc-top .kbtn kbd{font-size:.62rem;border:1px solid #334155;border-radius:5px;padding:1px 6px;color:#64748b;background:none}
@media(max-width:760px){.soc-top{gap:10px;padding:0 12px}.soc-top .kbtn kbd{display:none}.soc-top nav a{padding:6px 8px}.soc-top .logo small{display:none}}

.soc-main{max-width:1240px;margin:0 auto;padding:22px 20px 60px}

/* ── 히어로 ── */
.hero{position:relative;border-radius:18px;overflow:hidden;padding:2.2rem 2.4rem;margin-bottom:18px;
  background:linear-gradient(120deg,#0b1220 0%,#141032 52%,#27102a 100%);border:1px solid var(--line);
  box-shadow:0 12px 40px rgba(2,6,16,.5)}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(600px 200px at 85% -10%,rgba(239,68,68,.22),transparent 60%),
             radial-gradient(500px 220px at 8% 110%,rgba(167,139,250,.18),transparent 60%)}
.hero .h-in{position:relative;display:flex;gap:2.2rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.hero .h-badge{display:inline-flex;align-items:center;gap:8px;font-size:.72rem;font-weight:800;letter-spacing:.4px;
  color:#fca5a5;border:1px solid rgba(239,68,68,.45);background:rgba(239,68,68,.1);border-radius:99px;padding:5px 14px;margin-bottom:12px}
.hero h1{font-weight:800;font-size:1.85rem;color:#fff;margin:0 0 10px;line-height:1.35}
.hero h1 .accent{color:#7dd3fc}
.hero .h-sub{color:#9fb0ca;font-size:.92rem;line-height:1.75;max-width:600px;margin:0 0 18px}
.hero .h-sub b{color:#c7d4e8}
.h-meta{font-size:.78rem;color:#8fa0ba;letter-spacing:.2px}
.h-meta b{color:#e2e8f0;font-variant-numeric:tabular-nums;font-size:.9rem}
.h-ctas{display:flex;flex-direction:column;gap:12px;min-width:260px}
.h-cta{display:flex;align-items:center;gap:13px;text-decoration:none;border-radius:14px;padding:14px 18px;font-weight:800;transition:transform .15s,box-shadow .15s}
.h-cta:hover{transform:translateY(-2px);color:#fff}
.h-cta .ic{font-size:1.7rem}
.h-cta small{display:block;font-weight:500;font-size:.7rem;opacity:.85;margin-top:3px}
.h-cta.red{background:linear-gradient(135deg,#dc2626,#7f1d1d);color:#fff;box-shadow:0 6px 18px rgba(220,38,38,.35)}
.h-cta.violet{background:linear-gradient(135deg,#7c3aed,#312e81);color:#fff;box-shadow:0 6px 18px rgba(124,58,237,.35)}
.hero .h-term{position:relative;margin-top:16px;background:#060b16;border:1px solid var(--line);border-radius:10px;
  font-family:'Cascadia Mono',Consolas,monospace;font-size:.76rem;line-height:1.8;padding:10px 14px;color:#7c8aa5;overflow-x:auto;white-space:nowrap}
.hero .h-term .p{color:var(--acc)} .hero .h-term .ok{color:var(--green)} .hero .h-term .warn{color:var(--amber)}
@media(max-width:860px){.hero .h-in{flex-direction:column;align-items:stretch}.h-ctas{flex-direction:row}.h-cta{flex:1}}

/* ── 운영자 콘솔 (내 기록) ── */
.ops{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin-bottom:18px;
  display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.ops .ops-tag{font-family:'Cascadia Mono',Consolas,monospace;font-size:.68rem;letter-spacing:1.5px;color:var(--sub);text-transform:uppercase;flex-shrink:0}
.ops .ops-grid{display:flex;gap:12px;flex-wrap:wrap;flex:1}
.ops .ostat{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:8px 16px;min-width:92px;text-align:center}
.ops .ostat b{display:block;font-size:1.25rem;color:#fff;font-variant-numeric:tabular-nums}
.ops .ostat span{font-size:.63rem;color:var(--sub)}
.ops .ostat b.red{color:#f87171}.ops .ostat b.grn{color:#4ade80}.ops .ostat b.cyn{color:#7dd3fc}
.ops .ops-cta{background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.4);color:#7dd3fc;border-radius:10px;
  padding:10px 16px;font-size:.8rem;font-weight:700;text-decoration:none;white-space:nowrap}
.ops .ops-cta:hover{background:rgba(56,189,248,.18)}
.ops .ai-pill{display:inline-flex;align-items:center;gap:7px;padding:6px 13px;border-radius:99px;font-size:.72rem;font-weight:700;border:1px solid var(--line2);white-space:nowrap}
.ops .ai-pill .dot{width:8px;height:8px;border-radius:50%;background:var(--amber)}
.ops .ai-pill.byo{color:#86efac;border-color:#14532d}.ops .ai-pill.byo .dot{background:var(--green)}
.ops .ai-pill.proxy{color:#7dd3fc;border-color:#0c4a6e}.ops .ai-pill.proxy .dot{background:var(--acc)}
.ops .ai-pill.demo{color:#fcd34d;border-color:#78350f}.ops .ai-pill.demo .dot{background:var(--amber)}

/* ── 섹션 공통 ── */
.sec-h{display:flex;align-items:baseline;gap:12px;margin:26px 0 14px}
.sec-h h2{font-size:1.05rem;font-weight:800;color:#fff;margin:0;letter-spacing:.3px}
.sec-h .sec-tag{font-family:'Cascadia Mono',Consolas,monospace;font-size:.65rem;color:var(--sub);letter-spacing:1.5px;text-transform:uppercase}
.sec-h .sec-more{margin-left:auto;font-size:.76rem;color:var(--sub);text-decoration:none}
.sec-h .sec-more:hover{color:var(--acc)}

/* ── 미션 카드 ── */
.m-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}
.mcard{position:relative;display:flex;flex-direction:column;gap:10px;background:var(--panel);border:1px solid var(--line);
  border-radius:14px;padding:20px;text-decoration:none;transition:transform .15s,border-color .15s;overflow:hidden}
.mcard:hover{transform:translateY(-3px);border-color:var(--line2)}
.mcard .m-ic{width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}
.mcard h3{font-size:.98rem;font-weight:800;color:#fff;margin:0}
.mcard p{font-size:.8rem;color:var(--sub);line-height:1.65;margin:0;flex:1}
.mcard .m-go{font-size:.76rem;font-weight:700}
.mcard .live{position:absolute;top:14px;right:14px;font-size:.6rem;font-weight:800;letter-spacing:1px;padding:3px 9px;border-radius:99px}
.mcard.red .m-ic{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.35)}
.mcard.red .m-go{color:#f87171}.mcard.red .live{color:#fca5a5;border:1px solid rgba(239,68,68,.45);background:rgba(239,68,68,.1)}
.mcard.violet .m-ic{background:rgba(167,139,250,.12);border:1px solid rgba(167,139,250,.35)}
.mcard.violet .m-go{color:#c4b5fd}
.mcard.grn .m-ic{background:rgba(74,222,128,.12);border:1px solid rgba(74,222,128,.35)}
.mcard.grn .m-go{color:#86efac}.mcard.grn .live{color:#bbf7d0;border:1px solid rgba(74,222,128,.4);background:rgba(74,222,128,.1)}
.mcard.cyn .m-ic{background:rgba(56,189,248,.12);border:1px solid rgba(56,189,248,.35)}
.mcard.cyn .m-go{color:#7dd3fc}
.mcard.amb .m-ic{background:rgba(251,191,36,.12);border:1px solid rgba(251,191,36,.35)}
.mcard.amb .m-go{color:#fcd34d}.mcard.amb .live{color:#fde68a;border:1px solid rgba(251,191,36,.45);background:rgba(251,191,36,.1)}
.tool-strip{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.tool-strip a{font-size:.74rem;color:var(--sub);text-decoration:none;border:1px solid var(--line);background:var(--panel2);
  border-radius:99px;padding:6px 13px}
.tool-strip a:hover{border-color:var(--acc);color:#7dd3fc}

/* ── 도메인 그리드 ── */
.d-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}
.dtile{position:relative;display:flex;flex-direction:column;gap:8px;background:var(--panel);border:1px solid var(--line);
  border-left:4px solid var(--dc,#38bdf8);border-radius:12px;padding:16px 18px;cursor:pointer;text-align:left;
  font-family:inherit;color:var(--txt);transition:transform .15s,border-color .15s}
.dtile:hover{transform:translateY(-2px);border-color:var(--dc)}
.dtile .d-top{display:flex;align-items:center;gap:10px}
.dtile .d-ic{font-size:1.3rem}
.dtile h3{font-size:.88rem;font-weight:800;color:#fff;margin:0;flex:1}
.dtile .d-cnt{font-family:'Cascadia Mono',Consolas,monospace;font-size:.7rem;color:var(--dc);border:1px solid var(--dc);
  border-radius:6px;padding:2px 8px;font-weight:700}
.dtile p{font-size:.72rem;color:var(--sub);margin:0;line-height:1.6}
.dtile .d-open{font-size:.68rem;color:var(--sub);font-weight:700}
.dtile:hover .d-open{color:var(--dc)}

/* ── 카탈로그 ── */
.catalog{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-top:8px}
.cat-head{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--line)}
.cat-head h2{font-size:1rem;font-weight:800;color:#fff;margin:0}
.cat-head .cat-total{font-family:'Cascadia Mono',Consolas,monospace;font-size:.7rem;color:var(--sub)}
.cat-head input{flex:1;min-width:220px;background:var(--panel2);border:1px solid var(--line2);border-radius:10px;
  padding:10px 16px;color:var(--txt);font-size:.86rem;font-family:inherit}
.cat-head input::placeholder{color:#475569}
.cat-head input:focus{outline:none;border-color:var(--acc);background:#0a1120}
/* 카탈로그 내부 다크 오버라이드 (기존 사이드바 스타일 위) */
#catalogBody .list-group-item{color:#9db0c8}
#catalogBody .list-group-item:hover{background:rgba(56,189,248,.07);color:#e2e8f0}
#catalogBody .list-group-item:hover .item-number{color:var(--acc)}
#catalogBody .item-number{color:#475569}
#catalogBody .menu-category{color:#e2e8f0}
#catalogBody .menu-category .badge{opacity:.95}
#catalogBody mark.highlight{background:rgba(56,189,248,.3);color:#fff;border-radius:3px;padding:0 2px}
#catalogBody .no-results{color:var(--sub);text-align:center;padding:30px 10px}
#catalogBody .no-results i{display:block;margin-bottom:8px;color:#334155}

/* ── 푸터 ── */
.soc-foot{border-top:1px solid var(--line);background:var(--panel2);padding:26px 20px;text-align:center}
.soc-foot .f-logo{font-weight:800;color:#fff;font-size:.9rem;margin-bottom:8px}
.soc-foot .f-logo span{color:var(--acc)}
.soc-foot p{font-size:.72rem;color:var(--sub);line-height:1.8;margin:0}
.soc-foot .f-kbd{font-size:.7rem;color:#64748b;margin-top:6px}
.soc-foot kbd{border:1px solid #334155;border-radius:5px;padding:1px 6px;font-size:.62rem;color:#94a3b8;background:none}
</style>
</head>
<body class="soc">
<div id="wrapper">
    <div id="sidebar-wrapper">

        <header class="soc-top">
            <a class="logo" href="vuln-hub.html"><span class="mk">⛨</span><span>WEB-VULN-SIM<small>SECURITY TRAINING PLATFORM</small></span></a>
            <nav>
                <a href="redteam.html">레드팀 아레나</a>
                <a href="vulnlab.html">취약점 실습장</a>
                <a href="quiz-forge.html">AI 문제 포지</a>
                <a href="labs-live.html">라이브 랩</a>
                <a href="#catalog">카탈로그</a>
                <a href="my-progress.html">내 기록</a>
            </nav>
            <button type="button" class="kbtn" id="palBtn">🔍 검색 <kbd>Ctrl K</kbd></button>
        </header>

        <main class="soc-main">

            <!-- ═══ 히어로 ═══ -->
            <section class="hero">
                <div class="h-in">
                    <div>
                        <div class="h-badge">🏆 원티드 AI Championship 2026 출품작</div>
                        <h1>AI가 공격하고, 당신이 막는다<br><span class="accent">생성 → 적응 → 검증</span>이 폐루프로 돌아가는 보안 훈련장</h1>
                        <p class="h-sub">AI가 공격 체인을 조립하고, AI가 만든 문제는 기계 검증을 통과해야 출제됩니다. 키 없이 즉시 체험.</p>
                        <div class="h-meta"><b>230</b> 시나리오 · <b>425</b> 학습 페이지 · <b>10</b> 도메인 · <b>20+</b> 도구</div>
                    </div>
                    <div class="h-ctas">
                        <a class="h-cta red" href="redteam.html"><span class="ic">🦹</span><span>레드팀 아레나<small>AI 공격자 vs 나 · 4단계 체인 방어</small></span></a>
                        <a class="h-cta violet" href="quiz-forge.html"><span class="ic">🔨</span><span>AI 문제 포지<small>AI 생성 → 기계 검증 출제 · 통계 공개</small></span></a>
                    </div>
                </div>
                <div class="h-term"><span class="p">$</span> wvs init --domains 10 --scenarios 230 <span class="ok">✓ modules loaded</span> · agent <span class="ok">online</span> · verifier <span class="ok">armed</span> <span class="warn">— awaiting defender…</span></div>
            </section>

            <!-- ═══ 운영자 콘솔: 내 기록 ═══ -->
            <section class="ops" id="ops">
                <span class="ops-tag">◤ Operator Console</span>
                <div class="ops-grid">
                    <div class="ostat"><b id="opsXp" class="cyn">0</b><span>누적 XP</span></div>
                    <div class="ostat"><b id="opsStreak">0</b><span>연속 학습일</span></div>
                    <div class="ostat"><b id="opsDone" class="grn">0</b><span>완료 항목</span></div>
                    <div class="ostat"><b id="opsDef" class="red">–</b><span>레드팀 방어율</span></div>
                </div>
                <span class="ai-pill demo" id="opsAi"><span class="dot"></span><span id="opsAiTxt">AI 확인 중…</span></span>
                <a class="ops-cta" href="my-progress.html">내 기록 상세 →</a>
            </section>

            <!-- ═══ 훈련 미션 ═══ -->
            <section id="missions">
                <div class="sec-h"><h2>훈련 미션</h2><span class="sec-tag">/ missions</span></div>
                <div class="m-grid">
                    <a class="mcard red" href="redteam.html">
                        <span class="live">● LIVE</span>
                        <div class="m-ic">🦹</div>
                        <h3>AI 레드팀 아레나</h3>
                        <p>AI 공격자와 8라운드 대결 — 4단계 침투 체인을 막아라</p>
                        <span class="m-go">대결 시작 →</span>
                    </a>
                    <a class="mcard violet" href="quiz-forge.html">
                        <div class="m-ic">🔨</div>
                        <h3>AI 문제 포지</h3>
                        <p>AI 생성 → 4단계 기계 검증을 통과한 문제만 출제</p>
                        <span class="m-go">출제 시작 →</span>
                    </a>
                    <a class="mcard grn" href="labs-live.html">
                        <span class="live">실제 실행</span>
                        <div class="m-ic">⚡</div>
                        <h3>라이브 랩</h3>
                        <p>브라우저에서 동작하는 실전 실행형 실습</p>
                        <span class="m-go">랩 입장 →</span>
                    </a>
                    <a class="mcard cyn" href="ai-tutor.html">
                        <div class="m-ic">🤖</div>
                        <h3>AI 튜터</h3>
                        <p>1:1 개념 코칭 · 다음 학습 경로 제안</p>
                        <span class="m-go">코치 연결 →</span>
                    </a>
                    <a class="mcard amb" href="vulnlab.html">
                        <span class="live">51 미션</span>
                        <div class="m-ic">🧪</div>
                        <h3>취약점 실습장</h3>
                        <p>버프 스타일 시뮬레이터 — 가상 쇼핑몰 BugPay Mall을 직접 공격·방어 (웹·금융·AI)</p>
                        <span class="m-go">실습 입장 →</span>
                    </a>
                </div>
                <div class="tool-strip">
                    <a href="ai-grader.html">🎯 AI 채점기</a>
                    <a href="lab-generator.html">♾️ 무한 문제 생성기</a>
                    <a href="skill-assess.html">📊 스킬 레이더</a>
                    <a href="wrong-note.html">📕 오답 노트</a>
                    <a href="classroom.html">👨‍🏫 강의실</a>
                    <a href="certificate.html">📜 수료증</a>
                </div>
            </section>

            <!-- ═══ 도메인 카탈로그 ═══ -->
            <section id="domains">
                <div class="sec-h"><h2>보안 도메인</h2><span class="sec-tag">/ domains</span><a class="sec-more" href="#catalog">전체 카탈로그 보기 →</a></div>
                <div class="d-grid">
                    <button type="button" class="dtile" data-g="#groupA" style="--dc:#34d399">
                        <div class="d-top"><span class="d-ic">🛡️</span><h3>KISA 시큐어 코딩</h3><span class="d-cnt" id="cntA">0</span></div>
                        <span class="d-open">펼쳐보기 ↓</span>
                    </button>
                    <button type="button" class="dtile" data-g="#groupB" style="--dc:#60a5fa">
                        <div class="d-top"><span class="d-ic">🏛️</span><h3>기반시설 취약점</h3><span class="d-cnt" id="cntB">0</span></div>
                        <span class="d-open">펼쳐보기 ↓</span>
                    </button>
                    <button type="button" class="dtile" data-g="#groupC" style="--dc:#fbbf24">
                        <div class="d-top"><span class="d-ic">🏦</span><h3>금융 보안</h3><span class="d-cnt" id="cntC">0</span></div>
                        <span class="d-open">펼쳐보기 ↓</span>
                    </button>
                    <button type="button" class="dtile" data-g="#groupD" style="--dc:#22d3ee">
                        <div class="d-top"><span class="d-ic">🤖</span><h3>AI · 미래보안</h3><span class="d-cnt" id="cntD">0</span></div>
                        <span class="d-open">펼쳐보기 ↓</span>
                    </button>
                    <button type="button" class="dtile" data-g="#groupE" style="--dc:#fb7185">
                        <div class="d-top"><span class="d-ic">🚗</span><h3>자동차 보안</h3><span class="d-cnt" id="cntE">0</span></div>
                        <span class="d-open">펼쳐보기 ↓</span>
                    </button>
                </div>
            </section>

            <!-- ═══ 전체 카탈로그 ═══ -->
            <section class="catalog" id="catalog">
                <div class="cat-head">
                    <h2>전체 카탈로그</h2>
                    <span class="cat-total" id="catTotal">LOADING…</span>
                    <input type="text" id="searchInput" placeholder="🔍 카탈로그 검색 (예: SQL, D-01, root)" data-en-placeholder="🔍 Search catalog (e.g. SQL, D-01, root)">
                </div>
                <div class="menu-scroll" id="catalogBody">
                    <div class="list-group list-group-flush">
__CATALOG__
                    </div>
                </div>
            </section>

        </main>

        <footer class="soc-foot">
            <div class="f-logo">⛨ WEB-<span>VULN-SIM</span> — 교육용 보안 훈련 플랫폼</div>
            <p>공개 가이드(OWASP · KISA · NIST · ISO/SAE 21434 · UN R155) 개념의 교육용 재구성 — 실제로 작동하는 공격 코드·페이로드는 제공하지 않습니다.<br>
               Apache License 2.0 · 문의 jackhwang0210@gmail.com</p>
            <div class="f-kbd">어디서든 <kbd>Ctrl</kbd> <kbd>K</kbd> 로 전체 사이트 검색</div>
        </footer>

    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>
<script>
(function () {
  'use strict';

  /* ── 1. 카운팅: 사이드바 배지 + 도메인 타일 ── */
  function countSel(sel) { return document.querySelectorAll(sel + ' .list-group-item').length; }
  document.addEventListener('DOMContentLoaded', function () {
    var badges = ['menu1','menu2','menu3','menu4','menu5','menu6','menu7','menu9','menu10','menu11','menu12','menu13','menuAI','menuAuto','menuTime','menuErr','menuCode','menuEncap','menuApi','menuDesign'];
    badges.forEach(function (id) {
      var el = document.getElementById('badge-' + id);
      if (el) el.textContent = countSel('#' + id);
    });
    var sums = {
      A: ['#menu3','#menu4','#menuTime','#menuErr','#menuCode','#menuEncap','#menuApi','#menuDesign','#menu2'].reduce(function(a,s){return a+countSel(s);},0),
      B: ['#menu1','#menu5','#menu9','#menu6','#menu10','#menu11','#menu12','#menu13'].reduce(function(a,s){return a+countSel(s);},0),
      C: countSel('#menu7'),
      D: countSel('#menuAI'),
      E: countSel('#menuAuto')
    };
    ['A','B','C','D','E'].forEach(function (k) {
      var gb = document.getElementById('badge-group' + k); if (gb) gb.textContent = sums[k];
      var dt = document.getElementById('cnt' + k); if (dt) dt.textContent = sums[k];
    });
    var total = sums.A + sums.B + sums.C + sums.D + sums.E;
    var ct = document.getElementById('catTotal'); if (ct) ct.textContent = total + ' ITEMS · 5 GUIDE SYSTEMS';
  });

  /* ── 2. 카탈로그 검색 (통합) ── */
  document.getElementById('searchInput').addEventListener('keyup', function (e) {
    var searchTerm = e.target.value.toLowerCase();
    var menuItems = document.querySelectorAll('#catalogBody .list-group-item-action');
    var categories = document.querySelectorAll('#catalogBody .menu-category');

    if (searchTerm === '') {
      menuItems.forEach(function (item) {
        item.style.display = '';
        item.innerHTML = item.innerHTML.replace(/<mark class="highlight">(.*?)<\/mark>/gi, '$1');
      });
      document.querySelectorAll('#catalogBody .collapse').forEach(function (c) { c.classList.remove('show'); });
      var nr0 = document.getElementById('noResults'); if (nr0) nr0.remove();
      return;
    }

    var hasGlobalResults = false;
    categories.forEach(function (category) {
      var targetId = category.getAttribute('data-bs-target');
      if (!targetId) return;
      var collapseEl = document.querySelector(targetId);
      if (!collapseEl) return;
      var items = collapseEl.querySelectorAll('.list-group-item-action');
      var categoryHasMatch = false;

      items.forEach(function (item) {
        var textContent = item.textContent.toLowerCase();
        var keywords = item.getAttribute('data-keywords') || '';
        var isMatch = textContent.indexOf(searchTerm) >= 0 || keywords.indexOf(searchTerm) >= 0;
        if (isMatch) { item.style.display = ''; categoryHasMatch = true; hasGlobalResults = true; }
        else { item.style.display = 'none'; }
      });

      if (categoryHasMatch) { collapseEl.classList.add('show'); category.setAttribute('aria-expanded', 'true'); }
      else { collapseEl.classList.remove('show'); category.setAttribute('aria-expanded', 'false'); }
    });

    var noResultsDiv = document.getElementById('noResults');
    if (!hasGlobalResults) {
      if (!noResultsDiv) {
        noResultsDiv = document.createElement('div');
        noResultsDiv.id = 'noResults';
        noResultsDiv.className = 'no-results';
        noResultsDiv.innerHTML = '<i class="fa-solid fa-magnifying-glass fa-2x mb-2"></i><p>검색 결과가 없습니다.</p>';
        var body = document.getElementById('catalogBody');
        if (body) body.appendChild(noResultsDiv);
      }
    } else if (noResultsDiv) { noResultsDiv.remove(); }
  });

  /* ── 3. 카테고리 클릭 시 아이콘 상태 ── */
  // Bootstrap Collapse owns aria-expanded; do not toggle it a second time.

  /* ── 4. 도메인 타일 → 해당 그룹 펼침 ── */
  document.querySelectorAll('.dtile[data-g]').forEach(function (tile) {
    tile.addEventListener('click', function () {
      var g = document.querySelector(tile.getAttribute('data-g'));
      if (!g) return;
      document.querySelectorAll('#catalogBody .guide-body.show, #catalogBody .collapse.show').forEach(function (c) {
        if (c.id !== g.id) { c.classList.remove('show'); }
      });
      g.classList.add('show');
      var head = document.querySelector('.guide-group[data-bs-target="#' + g.id + '"]');
      if (head) head.setAttribute('aria-expanded', 'true');
      g.scrollIntoView({ behavior: 'smooth', block: 'start' });
      document.getElementById('catalog').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  /* ── 5. 운영자 콘솔: 내 기록 (데이터 없으면 섹션 전체 숨김 — 첫 방문은 깨끗하게) ── */
  function renderOps() {
    var hasLearn = false, hasDef = false;
    try {
      var p = JSON.parse(localStorage.getItem('wvs_progress')) || {};
      var items = p.items || {};
      var done = 0;
      Object.keys(items).forEach(function (k) { if (items[k] && items[k].c) done++; });
      document.getElementById('opsXp').textContent = p.xp || 0;
      document.getElementById('opsDone').textContent = done;
      var days = p.days || [];
      document.getElementById('opsStreak').textContent = (days && days.length) ? calcStreak(days) + '일' : '0일';
      hasLearn = ((p.xp || 0) > 0) || done > 0;
    } catch (e) {}
    try {
      var rp = JSON.parse(localStorage.getItem('wvs_red_profile')) || {};
      var ok = 0, fail = 0;
      Object.keys(rp).forEach(function (d) {
        Object.keys(rp[d] || {}).forEach(function (c) {
          ok += (rp[d][c] && rp[d][c].ok) || 0;
          fail += (rp[d][c] && rp[d][c].fail) || 0;
        });
      });
      document.getElementById('opsDef').textContent = (ok + fail) ? Math.round(ok / (ok + fail) * 100) + '%' : '–';
      hasDef = (ok + fail) > 0;
    } catch (e) {}
    var opsEl = document.getElementById('ops');
    if (opsEl && !hasLearn && !hasDef) opsEl.style.display = 'none';
  }
  function calcStreak(days) {
    var set = {}; days.forEach(function (d) { set[d] = 1; });
    var cur = new Date();
    function key(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
    if (!set[key(cur)]) cur.setDate(cur.getDate() - 1);
    var n = 0;
    for (var i = 0; i < 400; i++) {
      if (set[key(cur)]) { n++; cur.setDate(cur.getDate() - 1); } else break;
    }
    return n;
  }
  document.addEventListener('DOMContentLoaded', renderOps);

  /* ── 7. AI 계층 상태 ── */
  var AI_LABEL = { byo: ['byo', '🔑 내 키 · 실시간 AI'], proxy: ['proxy', '⚡ 공유 AI · 실시간'], demo: ['demo', '🎭 데모 AI · 규칙 엔진'] };
  function setAi(t) {
    var pill = document.getElementById('opsAi'), txt = document.getElementById('opsAiTxt');
    var l = AI_LABEL[t] || AI_LABEL.demo;
    pill.className = 'ai-pill ' + l[0]; txt.textContent = l[1];
  }
  document.addEventListener('DOMContentLoaded', function () {
    if (window.WVS_AI && window.WVS_AI.tier) {
      window.WVS_AI.tier().then(setAi).catch(function () { setAi('demo'); });
    } else { setAi('demo'); }
  });
})();
</script>
<script src="js/ai-client.js"></script>
<script src="js/bilingual.js"></script>
<script src="/js/soc-chrome.js" data-topbar="off" defer></script>
</body>
</html>
'''


def main():
    # 멱등: 백업이 있으면 백업이 원본 (재실행 안전)
    src_path = BACKUP if os.path.exists(BACKUP) else FILE
    if not os.path.exists(BACKUP):
        import shutil
        shutil.copyfile(FILE, BACKUP)
        print('백업 생성:', BACKUP)
    src = open(src_path, encoding='utf-8').read()

    old_css, catalog = extract(src)
    print('카탈로그 추출: %d자, 링크 %d개' % (len(catalog), catalog.count('list-group-item-action')))

    html = PAGE.replace('__OLD_CSS__', old_css).replace('__CATALOG__', catalog)
    with open(FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print('OK: vuln-hub.html 재생성 (%d자)' % len(html))


if __name__ == '__main__':
    main()
