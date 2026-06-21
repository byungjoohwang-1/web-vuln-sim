# -*- coding: utf-8 -*-
"""MISRA C/C++ 기반 'C/C++ 안전 코딩' 페이지 생성기.
원문 비복제 — 잘 알려진 C/C++ 안전 코딩 원칙을 자체 작성한 '안전하지 않은 코드 vs 안전한 코드'로 시연.
탭(안전하지 않은/안전한 코드) 토글 + 💡 비유 + 왜 위험한가 + 체크포인트."""
import html, os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')


def esc(s):
    return html.escape(s, quote=False)


PAGE = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{code}: {title} | C/C++ 안전 코딩</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lora:wght@600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{ --primary:#0ea5e9; --danger:#ef4444; --success:#22c55e; --dark:#0b1220; --text:#1e293b; --muted:#64748b; --border:#e2e8f0; }}
body {{ font-family:'Lora',serif; background:linear-gradient(135deg,#0ea5e9 0%,#1e3a8a 100%); min-height:100vh; padding:40px 20px; color:var(--text); }}
.container {{ max-width:1100px; margin:0 auto; background:#fff; border-radius:16px; box-shadow:0 25px 50px rgba(0,0,0,.3); overflow:hidden; }}
.topbar {{ background:#0b1220; padding:10px 24px; }}
.topbar a {{ color:#7dd3fc; text-decoration:none; font-family:'JetBrains Mono',monospace; font-size:13px; }}
.header {{ background:linear-gradient(135deg,#0ea5e9 0%,#1e3a8a 100%); color:#fff; padding:34px 40px; text-align:center; }}
.code-badge {{ display:inline-block; background:rgba(255,255,255,.2); padding:6px 16px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-weight:700; margin-bottom:12px; }}
.header h1 {{ font-size:28px; margin-bottom:8px; }}
.header p {{ opacity:.9; font-size:14px; }}
.lang-pill {{ display:inline-block; margin-top:10px; background:#0b1220; color:#7dd3fc; padding:4px 12px; border-radius:8px; font-family:'JetBrains Mono',monospace; font-size:12px; font-weight:700; }}
.sev {{ display:inline-block; margin:10px 0 0 8px; padding:4px 12px; border-radius:8px; font-size:12px; font-weight:700; font-family:'JetBrains Mono',monospace; }}
.sev-상 {{ background:var(--danger); color:#fff; }} .sev-중 {{ background:#f59e0b; color:#fff; }} .sev-하 {{ background:var(--success); color:#fff; }}
.body {{ padding:32px 40px; }}
.section {{ margin-bottom:26px; }}
.section h2 {{ font-size:19px; color:var(--primary); margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid #e0f2fe; }}
.easy {{ background:linear-gradient(135deg,#fff8e6,#fff3d6); border:1px solid #ffe08a; border-radius:12px; padding:18px 20px; font-size:16px; line-height:1.75; }}
.easy .tag {{ display:inline-block; background:#f59e0b; color:#fff; font-size:13px; font-weight:700; padding:3px 12px; border-radius:20px; margin-bottom:8px; font-family:'Lora',serif; }}
.easy b {{ color:#b45309; }}
.switch {{ display:flex; background:#0b1220; border-radius:10px; padding:4px; gap:4px; width:fit-content; margin-bottom:14px; }}
.switch button {{ border:none; background:transparent; color:#94a3b8; font-family:'Lora',serif; font-weight:700; font-size:14px; padding:9px 18px; border-radius:8px; cursor:pointer; transition:.2s; }}
.switch button.on.bad {{ background:var(--danger); color:#fff; }}
.switch button.on.good {{ background:var(--success); color:#fff; }}
.codepane {{ display:none; }}
.codepane.show {{ display:block; }}
.codehdr {{ font-family:'JetBrains Mono',monospace; font-weight:700; font-size:13px; padding:9px 14px; border-radius:10px 10px 0 0; color:#fff; }}
.codehdr.bad {{ background:var(--danger); }} .codehdr.good {{ background:var(--success); }}
pre {{ background:var(--dark); color:#e2e8f0; padding:18px 20px; border-radius:0 0 10px 10px; overflow-x:auto; font-family:'JetBrains Mono',monospace; font-size:13px; line-height:1.7; white-space:pre; }}
pre .c {{ color:#64748b; }} pre .k {{ color:#c792ea; }} pre .s {{ color:#c3e88d; }} pre .bad {{ color:#ff8a80; font-weight:700; }} pre .good {{ color:#a5ff90; font-weight:700; }}
.why {{ background:#fef2f2; border-left:4px solid var(--danger); border-radius:8px; padding:16px 18px; line-height:1.7; font-size:15px; }}
.why b {{ color:#b91c1c; }}
.checklist {{ list-style:none; }}
.checklist li {{ padding:12px 16px; margin-bottom:10px; background:#f0f9ff; border:1px solid var(--border); border-radius:10px; cursor:pointer; display:flex; align-items:center; gap:12px; transition:.2s; }}
.checklist li:hover {{ background:#e0f2fe; }}
.checklist li.done {{ background:#f0fdf4; border-color:#bbf7d0; }}
.checklist .box {{ width:22px; height:22px; border:2px solid var(--primary); border-radius:6px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-weight:700; color:#fff; }}
.checklist li.done .box {{ background:var(--success); border-color:var(--success); }}
.kref {{ font-family:'JetBrains Mono',monospace; font-size:12.5px; color:var(--muted); background:#f1f5f9; padding:12px 16px; border-radius:8px; margin-top:10px; }}
.footer {{ text-align:center; padding:22px; color:var(--muted); font-size:13px; border-top:1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="topbar"><a href="index.html">&larr; cd /index</a></div>
  <div class="header">
    <div class="code-badge">{code}</div>
    <h1>{icon} {title}</h1>
    <p>{category}</p>
    <div><span class="lang-pill">{lang}</span><span class="sev sev-{severity}">위험도: {severity}</span></div>
  </div>
  <div class="body">

    <div class="section">
      <div class="easy"><span class="tag">💡 쉽게 말하면</span><br>{easy}</div>
    </div>

    <div class="section">
      <h2>🔬 코드 비교 — 버튼으로 전환해 보세요</h2>
      <div class="switch">
        <button id="btnBad" class="on bad" onclick="show('bad')">❌ 안전하지 않은 코드</button>
        <button id="btnGood" class="good" onclick="show('good')">✅ 안전한 코드</button>
      </div>
      <div class="codepane show" id="paneBad">
        <div class="codehdr bad">❌ 안전하지 않은 코드 ({lang})</div>
        <pre>{bad_code}</pre>
      </div>
      <div class="codepane" id="paneGood">
        <div class="codehdr good">✅ 안전한 코드 ({lang})</div>
        <pre>{good_code}</pre>
      </div>
    </div>

    <div class="section">
      <h2>⚠️ 왜 위험한가</h2>
      <div class="why">{why}</div>
    </div>

    <div class="section">
      <h2>✅ 안전 코딩 체크포인트</h2>
      <ul class="checklist" id="checklist">{checklist}</ul>
      <div class="kref">참고 규칙: {ref}</div>
    </div>
  </div>
  <div class="footer">MISRA C:2012 / MISRA C++:2023 등 C·C++ 안전 코딩 원칙 기반 · 교육용 자체 재구성(원문 비복제)</div>
</div>
<script>
function show(s){{
  document.getElementById('btnBad').classList.toggle('on', s==='bad');
  document.getElementById('btnGood').classList.toggle('on', s==='good');
  document.getElementById('paneBad').classList.toggle('show', s==='bad');
  document.getElementById('paneGood').classList.toggle('show', s==='good');
}}
document.querySelectorAll('#checklist li').forEach(li=>li.addEventListener('click',()=>{{
  li.classList.toggle('done');
  li.querySelector('.box').textContent = li.classList.contains('done')?'✓':'';
}}));
</script>
</body>
</html>'''


def render(s):
    chk = ''.join('<li><span class="box"></span><span>%s</span></li>' % esc(c) for c in s['checkpoints'])
    return PAGE.format(
        code=esc(s['code']), title=esc(s['title']), icon=s['icon'], category=esc(s['category']),
        lang=esc(s['lang']), severity=s['severity'], easy=s['easy'],
        bad_code=esc(s['bad_code']), good_code=esc(s['good_code']),
        why=s['why'], checklist=chk, ref=esc(s['ref']),
    )


def main():
    import importlib, sys
    mods = sys.argv[1:] or ['specs_misra']
    total = 0
    for m in mods:
        for s in importlib.import_module(m).SPECS:
            with open(os.path.join(OUT_DIR, s['file']), 'w', encoding='utf-8') as f:
                f.write(render(s))
            print('wrote', s['file'])
            total += 1
    print('TOTAL', total)


if __name__ == '__main__':
    main()
