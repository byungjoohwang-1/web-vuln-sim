# -*- coding: utf-8 -*-
"""정보보호시스템(보안장비) 진단 실습 페이지 생성기.

specs_iss_*.py 의 LABS 를 읽어 페이지와 데이터 JS 를 만든다.
엔진은 public/js/iss-lab.js (손으로 쓴 것, 생성 대상 아님).
"""
from __future__ import print_function
import io
import json
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')

PAGE = u'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | 교육 시뮬레이터</title>
<meta name="description" content="{desc}">
<style>
:root{{--bg:#0b1220;--panel:#111b2e;--panel2:#16233c;--bd:#22314f;--ink:#e6edf7;
--muted:#93a4c0;--acc:#38bdf8;--good:#3fb950;--bad:#f85149;--warn:#e3a008;
--mono:'JetBrains Mono','Consolas','D2Coding',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.7 "Segoe UI","Malgun Gothic",sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:24px 18px 60px}}
h1{{font-size:24px;margin-bottom:6px}}
.sub{{color:var(--muted);font-size:14px;margin-bottom:18px}}
.dev{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;background:var(--panel);
border:1px solid var(--bd);border-radius:10px;padding:10px 14px;margin-bottom:16px;font-family:var(--mono);font-size:12.5px}}
.dev b{{color:var(--acc)}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}}
@media(max-width:1000px){{.cols{{grid-template-columns:1fr}}}}
.card{{background:var(--panel);border:1px solid var(--bd);border-radius:10px;padding:14px 16px;margin-bottom:14px}}
.card h2{{font-size:15px;color:var(--acc);margin-bottom:8px}}
.term{{background:#050a14;border:1px solid var(--bd);border-radius:10px;padding:0;overflow:hidden}}
.term .hd{{background:var(--panel2);padding:7px 12px;font-family:var(--mono);font-size:12px;color:var(--muted);
border-bottom:1px solid var(--bd)}}
#termOut{{height:420px;overflow:auto;padding:10px 12px;font-family:var(--mono);font-size:12.5px;
white-space:pre-wrap;word-break:break-all;line-height:1.55}}
#termOut .cmd{{color:var(--acc)}}
#termOut .err{{color:var(--bad)}}
.inrow{{display:flex;align-items:center;gap:8px;border-top:1px solid var(--bd);padding:8px 12px;background:#070d1a}}
#prompt{{font-family:var(--mono);font-size:12.5px;color:var(--good);white-space:nowrap}}
#termIn{{flex:1;background:transparent;border:none;outline:none;color:var(--ink);
font-family:var(--mono);font-size:12.5px}}
.qbtn{{display:inline-block;background:var(--panel2);border:1px solid var(--bd);color:var(--ink);
border-radius:7px;padding:4px 10px;font-family:var(--mono);font-size:11.5px;cursor:pointer;margin:2px 3px 2px 0}}
.qbtn:hover{{border-color:var(--acc);color:var(--acc)}}
.mlist{{list-style:none}}
.mlist li{{border:1px solid var(--bd);border-radius:8px;padding:8px 11px;margin-bottom:7px;cursor:pointer;
display:flex;gap:9px;align-items:center;background:var(--panel2)}}
.mlist li:hover{{border-color:var(--acc)}}
.mlist li.on{{border-color:var(--acc);background:#16304d}}
.mlist .id{{font-family:var(--mono);font-size:11.5px;color:var(--muted);flex:0 0 auto}}
.mlist .tt{{flex:1;font-size:13.5px}}
.mlist .st{{font-size:11.5px;font-weight:700;flex:0 0 auto}}
.risk{{font-family:var(--mono);font-size:10.5px;border:1px solid var(--bd);border-radius:999px;padding:0 6px;color:var(--muted)}}
.opt{{display:block;border:1px solid var(--bd);border-radius:8px;padding:8px 11px;margin-bottom:6px;cursor:pointer;background:var(--panel2);font-size:13.5px}}
.opt:hover{{border-color:var(--acc)}}
.opt input{{margin-right:8px}}
.vbtn{{background:var(--panel2);border:1px solid var(--bd);color:var(--ink);border-radius:8px;
padding:8px 18px;font-size:14px;font-weight:700;cursor:pointer;margin-right:8px}}
.vbtn.on{{border-color:var(--acc);background:#16304d;color:var(--acc)}}
.go{{background:var(--acc);color:#06121f;border:none;border-radius:8px;padding:9px 20px;
font-size:14px;font-weight:700;cursor:pointer}}
.go:disabled{{opacity:.45;cursor:not-allowed}}
.fixb{{background:var(--good);color:#06121f;border:none;border-radius:8px;padding:8px 16px;
font-size:13.5px;font-weight:700;cursor:pointer}}
.res{{border-radius:8px;padding:10px 13px;margin-top:10px;font-size:13.5px;line-height:1.75}}
.res.ok{{background:#0f2a18;border:1px solid var(--good)}}
.res.no{{background:#3a1518;border:1px solid var(--bad)}}
.na{{background:#1d2740;border:1px solid var(--bd);border-radius:8px;padding:10px 13px;
color:var(--muted);font-size:13px;margin-top:10px}}
.hint{{color:var(--muted);font-size:13px;margin-top:6px}}
code{{background:#050a14;border:1px solid var(--bd);border-radius:4px;padding:1px 5px;font-family:var(--mono);font-size:12.5px}}
.note{{color:var(--muted);font-size:12.5px;margin-top:20px;border-top:1px solid var(--bd);padding-top:14px}}
.prog{{font-family:var(--mono);font-size:12px;color:var(--muted);margin-bottom:10px}}
</style>
</head>
<body>
<div class="wrap">
<h1>{title}</h1>
<div class="sub">{desc}</div>

<div class="dev">
  <span>장비 <b id="devName"></b></span><span>·</span>
  <span>종류 <b id="devType"></b></span><span>·</span>
  <span>모델 <b id="devModel"></b></span><span>·</span>
  <span>점검 항목 <b>{count}</b>개</span>
</div>

<div class="cols">
  <div>
    <div class="term">
      <div class="hd">모의 콘솔 — 이 페이지 안에서만 동작합니다 (실제 장비 아님)</div>
      <div id="termOut"></div>
      <div class="inrow"><span id="prompt"></span><input id="termIn" autocomplete="off"
        spellcheck="false" aria-label="장비 명령 입력"
        placeholder="명령을 입력하세요.  ? 를 치면 목록이 나옵니다."></div>
    </div>
    <div class="card" style="margin-top:14px">
      <h2>자주 쓰는 명령</h2>
      <div id="quick"></div>
    </div>
  </div>

  <div>
    <div class="card">
      <h2>점검 항목</h2>
      <div class="prog" id="prog"></div>
      <ul class="mlist" id="mlist"></ul>
    </div>
    <div class="card" id="detail"></div>
  </div>
</div>

<div class="note">
  교육용 시뮬레이션입니다. 장비명 <code>SENTRA</code> 는 가상 브랜드이며 실제 제품과 관련이 없습니다.
  점검 항목의 구조(항목ID·위험도·판단기준·평가대상)는 전자금융기반시설 정보보호시스템 평가 기준을 참고했고,
  장비 설정·시나리오·해설은 교육용으로 새로 작성했습니다.
</div>
</div>

<script src="/js/iss-lab.js"></script>
<script src="/js/{data}"></script>
<script>
(function(){{
  var L = window.WVS_ISS_LAB, D = window.ISS_LAB_DATA;
  var cfg = new L.Config(D.cfg);
  var cli = new L.Cli(cfg, D.device);
  var missions = D.missions, cur = 0;
  var state = missions.map(function(){{ return {{ tried:false, pass:false, fixed:false }}; }});
  var PROMPT = D.device.name + '> ';

  var out = document.getElementById('termOut');
  function print(text, cls){{
    var d = document.createElement('div');
    if (cls) d.className = cls;
    d.textContent = text;
    out.appendChild(d);
    out.scrollTop = out.scrollHeight;
  }}
  function exec(cmd){{
    print(PROMPT + cmd, 'cmd');
    var r = cli.run(cmd);
    if (r) print(r, /^%/.test(r) ? 'err' : '');
  }}

  document.getElementById('devName').textContent = D.device.name;
  document.getElementById('devType').textContent = D.device.typeLabel;
  document.getElementById('devModel').textContent = D.cfg.system.model;
  document.getElementById('prompt').textContent = PROMPT;

  var inp = document.getElementById('termIn');
  inp.addEventListener('keydown', function(e){{
    if (e.key !== 'Enter') return;
    var v = inp.value.trim();
    if (!v) return;
    inp.value = '';
    if (v === 'clear') {{ out.innerHTML = ''; return; }}
    exec(v);
  }});

  var quick = document.getElementById('quick');
  cli.commands().forEach(function(c){{
    var b = document.createElement('button');
    b.className = 'qbtn'; b.type = 'button'; b.textContent = c;
    b.addEventListener('click', function(){{ exec(c); }});
    quick.appendChild(b);
  }});

  function renderList(){{
    var done = state.filter(function(s){{ return s.pass; }}).length;
    document.getElementById('prog').textContent =
      '판정 완료 ' + done + ' / ' + missions.length +
      '  ·  조치 적용 ' + state.filter(function(s){{ return s.fixed; }}).length + '건';
    var ul = document.getElementById('mlist');
    ul.innerHTML = '';
    missions.forEach(function(m, i){{
      var li = document.createElement('li');
      li.className = i === cur ? 'on' : '';
      var st = state[i].pass ? (state[i].fixed ? '조치완료' : '판정완료')
             : (state[i].tried ? '다시' : '미점검');
      var col = state[i].pass ? 'var(--good)' : (state[i].tried ? 'var(--bad)' : 'var(--muted)');
      li.innerHTML = '<span class="id">' + m.id + '</span>' +
        '<span class="tt">' + L.esc(m.title) + '</span>' +
        '<span class="risk">위험 ' + m.risk + '</span>' +
        '<span class="st" style="color:' + col + '">' + st + '</span>';
      li.addEventListener('click', function(){{ cur = i; render(); }});
      ul.appendChild(li);
    }});
  }}

  function render(){{
    renderList();
    var m = missions[cur], s = state[cur];
    var d = document.getElementById('detail');

    if (!L.applies(m, D.device.type)) {{
      d.innerHTML = '<h2>' + m.id + ' · ' + L.esc(m.title) + '</h2>' +
        '<div class="na">이 항목은 <b>' + D.device.typeLabel + '</b> 의 평가대상이 아닙니다 — 해당없음(N/A).' +
        '<br>평가대상: ' + (m.appliesTo || []).join(', ') + '</div>';
      return;
    }}

    var h = '<h2>' + m.id + ' · ' + L.esc(m.title) + '</h2>';
    h += '<p>' + m.brief + '</p>';
    h += '<p class="hint">어디를 보나 — ' + L.esc(m.where) + '</p>';
    h += '<div style="margin:10px 0">';
    m.cmds.forEach(function(c){{
      h += '<button class="qbtn" type="button" data-cmd="' + L.esc(c) + '">' + L.esc(c) + '</button>';
    }});
    h += '</div>';
    h += '<p class="hint">힌트 — ' + L.esc(m.hint) + '</p>';

    h += '<div style="margin-top:12px"><b style="font-size:13.5px">1. 판정</b><div style="margin-top:6px">' +
      '<button class="vbtn" type="button" data-v="good">양호</button>' +
      '<button class="vbtn" type="button" data-v="vuln">취약</button></div></div>';

    h += '<div style="margin-top:12px"><b style="font-size:13.5px">2. 그렇게 판단한 근거</b>' +
      '<div class="hint" style="margin-bottom:6px">출력에서 확인한 것만 고르세요. 개수도 맞아야 합니다.</div>';
    m.options.forEach(function(o, i){{
      h += '<label class="opt"><input type="checkbox" data-o="' + i + '">' + L.esc(o) + '</label>';
    }});
    h += '</div>';
    h += '<div style="margin-top:12px"><button class="go" id="submit" type="button">채점</button>' +
      (s.pass && m.fix && !s.fixed
        ? ' <button class="fixb" id="dofix" type="button">조치 적용</button>' : '') + '</div>';
    h += '<div id="res"></div>';
    d.innerHTML = h;

    var chosenV = null;
    d.querySelectorAll('[data-cmd]').forEach(function(b){{
      b.addEventListener('click', function(){{ exec(b.getAttribute('data-cmd')); }});
    }});
    d.querySelectorAll('[data-v]').forEach(function(b){{
      b.addEventListener('click', function(){{
        chosenV = b.getAttribute('data-v');
        d.querySelectorAll('[data-v]').forEach(function(x){{ x.className = 'vbtn'; }});
        b.className = 'vbtn on';
      }});
    }});
    document.getElementById('submit').addEventListener('click', function(){{
      var ev = [];
      d.querySelectorAll('[data-o]').forEach(function(cb){{
        if (cb.checked) ev.push(m.options[parseInt(cb.getAttribute('data-o'), 10)]);
      }});
      if (!chosenV) {{ document.getElementById('res').innerHTML =
        '<div class="res no">먼저 양호/취약을 고르세요.</div>'; return; }}
      var g = L.grade(m, cfg, chosenV, ev);
      state[cur].tried = true;
      state[cur].pass = g.pass;
      if (g.pass) {{
        /* 조치 버튼은 통과한 뒤에만 나온다. 상세 패널을 다시 그리지 않으면
           버튼이 영영 생기지 않아 조치를 할 수 없다. 다시 그린 뒤 결과를 넣는다. */
        var okHtml = '<div class="res ok"><b>통과</b> — 판정과 근거가 모두 맞습니다.<br><br>' +
          m.why + (m.fix && !state[cur].fixed
            ? '<br><br>아래 <b>조치 적용</b>을 누른 뒤 같은 명령을 다시 쳐 보세요. 출력이 바뀝니다.' : '') +
          '</div>';
        render();
        document.getElementById('res').innerHTML = okHtml;
      }} else {{
        var msg = [];
        if (!g.verdictOk) msg.push('판정이 다릅니다.');
        else msg.push('판정은 맞습니다.');
        if (!g.evidenceOk) msg.push('근거 선택이 맞지 않습니다 — 출력을 다시 보세요.');
        document.getElementById('res').innerHTML =
          '<div class="res no"><b>다시</b> — ' + msg.join(' ') + '</div>';
        renderList();
      }}
    }});
    var fb = document.getElementById('dofix');
    if (fb) fb.addEventListener('click', function(){{
      m.fix(cfg);
      state[cur].fixed = true;
      print('[조치 적용] ' + m.fixNote, 'cmd');
      render();
      document.getElementById('res').innerHTML =
        '<div class="res ok"><b>조치 완료</b> — ' + L.esc(m.fixNote) +
        '<br>같은 명령을 다시 실행해 출력이 바뀌었는지 확인하세요.</div>';
    }});

  }}

  exec('show version');
  render();
}})();
</script>
</body>
</html>
'''


def build(lab):
    data_js = 'iss-lab-%s.js' % lab['key']
    html = PAGE.format(
        title=lab['title'], desc=lab['desc'],
        count=len(lab['missions']), data=data_js,
    )
    with io.open(os.path.join(OUT, lab['file']), 'w', encoding='utf-8') as f:
        f.write(html)

    ms = []
    for m in lab['missions']:
        ms.append(
            '{id:%s,risk:%d,appliesTo:%s,title:%s,brief:%s,where:%s,hint:%s,why:%s,'
            'cmds:%s,options:%s,evidence:%s,verdict:%s,fix:%s,fixNote:%s}' % (
                json.dumps(m['id'], ensure_ascii=False), m['risk'],
                json.dumps(m.get('appliesTo', []), ensure_ascii=False),
                json.dumps(m['title'], ensure_ascii=False),
                json.dumps(m['brief'], ensure_ascii=False),
                json.dumps(m['where'], ensure_ascii=False),
                json.dumps(m['hint'], ensure_ascii=False),
                json.dumps(m['why'], ensure_ascii=False),
                json.dumps(m['cmds'], ensure_ascii=False),
                json.dumps(m['options'], ensure_ascii=False),
                json.dumps(m['evidence'], ensure_ascii=False),
                m['verdict'],
                m.get('fix', 'null') or 'null',
                json.dumps(m.get('fixNote', ''), ensure_ascii=False),
            )
        )
    js = ('/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */\n'
          'window.ISS_LAB_DATA = {\n'
          '  device: %s,\n'
          '  cfg: %s,\n'
          '  missions: [\n    %s\n  ]\n};\n' % (
              json.dumps(lab['device'], ensure_ascii=False),
              json.dumps(lab['cfg'], ensure_ascii=False, indent=1),
              ',\n    '.join(ms),
          ))
    with io.open(os.path.join(OUT, 'js', data_js), 'w', encoding='utf-8') as f:
        f.write(js)
    return lab['file'], len(lab['missions'])


def main():
    import importlib
    mods = [a for a in sys.argv[1:] if not a.startswith('--')] or ['specs_iss_acct']
    total = 0
    for name in mods:
        for lab in importlib.import_module(name).LABS:
            fn, n = build(lab)
            print('wrote %-30s %2d개 점검' % (fn, n))
            total += n
    print('TOTAL %d개 점검 항목' % total)


if __name__ == '__main__':
    main()
