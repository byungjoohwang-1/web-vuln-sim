# -*- coding: utf-8 -*-
"""fincloud-hub.html — 금융 클라우드 진단 시뮬레이터 랜딩 생성기.

항목 목록은 specs 모듈에서 직접 읽는다. 스펙을 추가하면 허브가 자동으로 따라오도록 해서
"페이지는 만들었는데 목록에 없는" 어긋남을 막는다(이 저장소에서 반복됐던 실수).
"""
import html
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, '..', 'public', 'fincloud-hub.html')

MODULES = ['specs_fincloud', 'specs_fincloud_b']

# PISM 평가기준 전체 항목 수 — 이 중 몇 개를 시뮬레이터로 구현했는지 정직하게 밝힌다.
PISM_TOTAL = 73


def esc(s):
    return html.escape(str(s), quote=False)


def load():
    rows = []
    for m in MODULES:
        for s in importlib.import_module(m).SPECS:
            rows.append(s)
    rows.sort(key=lambda r: r['pism'])
    return rows


PAGE = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta name="theme-color" content="#232f3e"><link rel="manifest" href="/manifest.json"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="/js/pwa.js" defer></script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>금융 클라우드 보안 진단 시뮬레이터 · WEB-VULN-SIM</title>
<meta property="og:type" content="website">
<meta property="og:site_name" content="WEB-VULN-SIM 보안 학습 포털">
<meta property="og:title" content="금융 클라우드 보안 진단 시뮬레이터 · WEB-VULN-SIM">
<meta property="og:description" content="클라우드 관리체계 보안 취약점 평가기준(PISM) 기반 AWS 진단 실습 — 실제 CLI 명령을 실행하고 양호/취약을 판정한 뒤 조치까지">
<meta property="og:url" content="https://vuln-sim.web.app/fincloud-hub.html">
<meta property="og:image" content="https://vuln-sim.web.app/favicon.svg">
<meta name="twitter:card" content="summary">
<meta name="description" content="금융권 클라우드 관리체계 보안 취약점 평가기준(퍼블릭 클라우드) PISM 항목을 실제 AWS CLI 진단 절차로 실습합니다. S3 암호화·퍼블릭 액세스·보안그룹·CloudTrail·EBS/RDS 암호화·IAM MFA·액세스 키·IMDSv2 등 {n}개 항목.">
<style>
:root{{--aws-navy:#232f3e;--aws-orange:#ff9900;--aws-blue:#0972d3;--bg:#f2f3f3;--panel:#fff;--line:#d5dbdb;--ink:#16191f;--muted:#5f6b7a;--bad:#d13212;--good:#037f0c;--warn:#8d6605;--mono:'Consolas','Menlo','JetBrains Mono',monospace;}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Amazon Ember','Segoe UI','Malgun Gothic',sans-serif;background:var(--bg);color:var(--ink);line-height:1.55}}
a{{color:inherit;text-decoration:none}}
.awsbar{{background:var(--aws-navy);color:#fff;display:flex;align-items:center;gap:16px;padding:9px 18px;flex-wrap:wrap;font-size:13px}}
.awsbar .logo{{font-weight:800}} .awsbar .logo i{{color:var(--aws-orange);font-style:normal}}
.awsbar a{{color:#d5dbdb;font-size:12.5px}} .awsbar a:hover{{color:#fff}}
.awsbar .sp{{margin-left:auto}}
.awsbar .acct{{font-family:var(--mono);font-size:12px;background:rgba(255,255,255,.08);border-radius:4px;padding:3px 9px}}
.wrap{{max-width:1180px;margin:0 auto;padding:20px 16px 80px}}
.hero{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin-bottom:18px}}
.hero h1{{font-size:23px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.hero p{{font-size:14px;color:#414d5c;margin-top:10px;max-width:900px}}
.hero .src{{font-family:var(--mono);font-size:11.5px;color:var(--aws-blue);margin-top:9px}}
.stats{{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}}
.stat{{background:#f7f8f8;border:1px solid var(--line);border-radius:9px;padding:10px 15px;min-width:112px}}
.stat b{{display:block;font-size:21px;font-family:var(--mono)}}
.stat span{{font-size:11.5px;color:var(--muted)}}
.how{{background:#eef6ff;border-left:4px solid var(--aws-blue);border-radius:8px;padding:13px 15px;font-size:13.5px;color:#0b3c63;margin:16px 0}}
.how ol{{margin:8px 0 0 19px}} .how li{{margin:3px 0}}
.warnbox{{background:#fdf3e2;border-left:4px solid var(--warn);border-radius:8px;padding:12px 15px;font-size:13px;color:#5c4405;margin:16px 0}}
.filters{{display:flex;gap:7px;flex-wrap:wrap;margin:18px 0 12px}}
.fbtn{{cursor:pointer;border:1px solid var(--line);background:#fff;border-radius:20px;padding:6px 14px;font-size:12.5px;font-weight:700;color:#414d5c;font-family:inherit}}
.fbtn.on{{background:var(--aws-navy);border-color:var(--aws-navy);color:#fff}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:13px}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:15px 17px;display:block;transition:.15s;border-left:5px solid var(--line)}}
.card:hover{{border-color:var(--aws-blue);border-left-color:var(--aws-blue);box-shadow:0 3px 12px rgba(0,0,0,.08);transform:translateY(-2px)}}
.card.r5{{border-left-color:var(--bad)}} .card.r4{{border-left-color:var(--warn)}} .card.r3{{border-left-color:var(--aws-blue)}}
.card .top{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:7px}}
.card .pid{{font-family:var(--mono);font-size:11.5px;background:var(--aws-navy);color:#fff;border-radius:4px;padding:2px 8px;font-weight:700}}
.card .rk{{font-size:11px;font-weight:800;border-radius:20px;padding:2px 9px}}
.card .rk.r5{{background:#fdecea;color:var(--bad)}} .card .rk.r4{{background:#fdf3e2;color:var(--warn)}} .card .rk.r3{{background:#eef6ff;color:var(--aws-blue)}}
.card h3{{font-size:14.5px;line-height:1.45;margin-bottom:6px}}
.card .svc{{font-family:var(--mono);font-size:11.5px;color:var(--aws-orange);font-weight:700;margin-bottom:6px}}
.card p{{font-size:12.5px;color:var(--muted);line-height:1.6}}
.card .go{{font-size:12.5px;color:var(--aws-blue);font-weight:700;margin-top:9px;display:inline-block}}
.sec{{font-size:16px;font-weight:800;margin:26px 0 10px;display:flex;align-items:baseline;gap:9px}}
.sec span{{font-size:12px;color:var(--muted);font-family:var(--mono);font-weight:400}}
table{{width:100%;border-collapse:collapse;font-size:13px;background:var(--panel);margin-top:9px}}
th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left}}
th{{background:#f2f3f3;font-size:12.5px}}
.disc{{font-size:12px;color:var(--muted);border-top:1px dashed var(--line);padding-top:12px;margin-top:22px}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="awsbar">
  <span class="logo"><i>aws</i> &nbsp;금융 클라우드 진단</span>
  <a href="index.html">홈</a>
  <a href="vuln-hub.html">카탈로그</a>
  <a href="11_cloud-c01.html">클라우드 개념 시뮬</a>
  <span class="sp"></span>
  <span class="acct">ap-northeast-2 · 3820-1174-9265</span>
</div>
<div class="wrap">

  <div class="hero">
    <h1>☁️ 금융 클라우드 보안 진단 시뮬레이터</h1>
    <p><b>평가기준을 읽는 실습이 아니라, 실제로 진단해 보는 실습입니다.</b> 평가기준의 &lsquo;평가방법&rsquo;에 적힌 AWS CLI 명령을
       모의 터미널에서 그대로 실행하고, <b>실제 AWS 응답 형식의 출력</b>을 읽어 양호/취약을 직접 판정한 뒤 조치까지 수행합니다.
       계정 ID·ARN·리소스 ID 는 형식만 실제와 같게 만든 가상 값이며, 어떤 AWS 환경에도 접속하지 않습니다.</p>
    <div class="src">📕 근거: 「클라우드 관리체계 보안 취약점 평가기준 (퍼블릭 클라우드)」 — 교육용 재구성</div>
    <div class="stats">
      <div class="stat"><b>{n}</b><span>구현 진단 항목</span></div>
      <div class="stat"><b>{r5}</b><span>위험도 5</span></div>
      <div class="stat"><b>{ncmd}</b><span>AWS CLI 명령</span></div>
      <div class="stat"><b>{total}</b><span>평가기준 전체 항목</span></div>
    </div>
  </div>

  <div class="how">
    <b>진행 방식</b>
    <ol>
      <li><b>점검 대상 확인</b> — 콘솔 경로와 평가항목의 상세설명을 읽습니다.</li>
      <li><b>CLI 진단</b> — 등록된 명령을 눌러 실행하거나 직접 입력합니다. 출력은 실제 AWS 응답 형식입니다.</li>
      <li><b>양호/취약 판정</b> — <b>명령을 실행하지 않으면 판정할 수 없습니다.</b> 출력을 근거로 스스로 판단합니다.</li>
      <li><b>조치·재확인</b> — 조치 CLI 와 IaC(Terraform)를 확인하고, 조치 후 결과를 봅니다.</li>
    </ol>
  </div>

  <div class="warnbox">
    ⚠️ 이 시뮬레이터는 평가기준 <b>전체 {total}개 항목 중 {n}개</b>를 다룹니다. AWS CLI 로 기계적 확인이 가능한
    <b>스크립트 평가 항목</b>을 우선 구현했습니다. 나머지는 정책 문서·인터뷰·현장 확인이 필요한 <b>관리체계 평가 항목</b>이라
    터미널 실습으로 재현하면 오히려 실제 평가를 오도할 수 있어 포함하지 않았습니다.
    또한 평가기준·AWS 사양은 개정되므로, 실제 평가에서는 <b>최신 원문과 AWS 공식 문서</b>를 따르십시오.
  </div>

  <div class="filters" id="filters">
    <button class="fbtn on" data-f="all">전체 {n}</button>
    <button class="fbtn" data-f="r5">위험도 5</button>
    <button class="fbtn" data-f="enc">암호화</button>
    <button class="fbtn" data-f="iam">계정·권한</button>
    <button class="fbtn" data-f="net">네트워크</button>
    <button class="fbtn" data-f="log">로그·추적</button>
  </div>

  <div class="grid" id="grid">
{cards}
  </div>

  <div class="sec">📊 통제분야별 분포 <span>/ coverage</span></div>
  <table>
    <tr><th>통제분야</th><th>구현 항목</th><th>대상 서비스</th></tr>
{areas}
  </table>

  <div class="sec">🔗 함께 보면 좋은 것 <span>/ related</span></div>
  <table>
    <tr><th>콘텐츠</th><th>차이</th></tr>
    <tr><td><a href="11_cloud-c01.html" style="color:var(--aws-blue);font-weight:700">클라우드 보안 개념 시뮬 (C-01~20)</a></td>
        <td>같은 주제를 <b>개념 중심</b>으로 설명합니다. 이 페이지는 <b>AWS 진단 절차</b>가 중심입니다.</td></tr>
    <tr><td><a href="07_fin-transaction-integrity.html" style="color:var(--aws-blue);font-weight:700">전자금융 보안 시뮬 (43종)</a></td>
        <td>전자금융기반시설 평가기준 기반의 <b>애플리케이션 계층</b> 취약점 실습입니다.</td></tr>
    <tr><td><a href="privacy-hub.html" style="color:var(--aws-blue);font-weight:700">개인정보보호 트랙</a></td>
        <td>암호화·접속기록·파기 요건의 <b>법적 근거</b>(개인정보 보호법)를 다룹니다.</td></tr>
  </table>

  <div class="disc">
    「클라우드 관리체계 보안 취약점 평가기준(퍼블릭 클라우드)」의 평가항목을 교육 목적으로 재구성한 시뮬레이터입니다.
    원문을 복제하지 않으며, 모든 명령 출력은 학습용으로 작성한 가상 데이터입니다.
    실제 진단·평가에는 기관이 배포한 최신 평가기준과 스크립트를 사용하십시오.
  </div>
</div>

<script src="/js/progress.js" defer></script>
<script src="/js/soc-chrome.js" data-topbar="off" defer></script>
<script>
document.getElementById('filters').addEventListener('click', function (e) {{
  var b = e.target.closest('.fbtn');
  if (!b) return;
  document.querySelectorAll('.fbtn').forEach(function (x) {{ x.classList.remove('on'); }});
  b.classList.add('on');
  var f = b.getAttribute('data-f');
  document.querySelectorAll('#grid .card').forEach(function (c) {{
    c.style.display = (f === 'all' || c.getAttribute('data-tags').indexOf(f) >= 0) ? '' : 'none';
  }});
}});
try {{ if (window.WVSProgress) window.WVSProgress.markVisited('fincloud-hub.html'); }} catch (e) {{}}
</script>
<script src="js/bilingual.js"></script>
</body>
</html>
'''


def tags_of(s):
    """필터용 태그. 카드 하나가 여러 분류에 속할 수 있다."""
    t = ['r' + s['risk']]
    svc = s.get('svc', '') + ' ' + s['title']
    if any(k in s['title'] for k in ('암호화', '복원')):
        t.append('enc')
    if any(k in svc for k in ('IAM', 'CloudShell')) or '권한' in s['title'] or '계정' in s['title'] or '비밀번호' in s['title'] or '자격 증명' in s['title']:
        t.append('iam')
    if any(k in svc for k in ('Security Group',)) or '네트워크' in s['title'] or '퍼블릭' in s['title'] or '통신구간' in s['title']:
        t.append('net')
    if 'CloudTrail' in svc or '로그' in s['title'] or '추적' in s['title']:
        t.append('log')
    return ' '.join(t)


def main():
    rows = load()
    cards = []
    for s in rows:
        cards.append(
            '    <a class="card r{risk}" data-tags="{tags}" href="{file}">\n'
            '      <div class="top"><span class="pid">{pism}</span>'
            '<span class="rk r{risk}">위험도 {risk}</span></div>\n'
            '      <div class="svc">{svc}</div>\n'
            '      <h3>{title}</h3>\n'
            '      <p>{detail}</p>\n'
            '      <span class="go">진단 시작 →</span>\n'
            '    </a>'.format(
                risk=s['risk'], tags=tags_of(s), file=s['file'], pism=s['pism'],
                svc=esc(s.get('svc', 'AWS')), title=esc(s['title']),
                detail=esc(s['detail'][:105] + ('…' if len(s['detail']) > 105 else '')),
            ))

    areas = {}
    for s in rows:
        a = areas.setdefault(s['area'], {'n': 0, 'svc': set()})
        a['n'] += 1
        for x in s.get('svc', 'AWS').split(' · '):
            a['svc'].add(x)
    area_rows = ''.join(
        '    <tr><td>%s</td><td>%d개</td><td>%s</td></tr>\n' % (esc(k), v['n'], esc(', '.join(sorted(v['svc']))))
        for k, v in sorted(areas.items()))

    ncmd = sum(len(s['cmds']) for s in rows)
    r5 = sum(1 for s in rows if s['risk'] == '5')

    out = PAGE.format(n=len(rows), r5=r5, ncmd=ncmd, total=PISM_TOTAL,
                      cards='\n'.join(cards), areas=area_rows)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(out)
    # 윈도 콘솔이 cp949 라 em-dash 같은 문자에서 죽는다. 로그는 ASCII 로만.
    print('wrote fincloud-hub.html : items=%d risk5=%d cli=%d' % (len(rows), r5, ncmd))


if __name__ == '__main__':
    main()
