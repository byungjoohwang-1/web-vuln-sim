# -*- coding: utf-8 -*-
"""vuln-hub.html 상단에 AI 챔피언십 히어로 섹션을 멱등 주입한다.

마커: <!-- WVS-HERO-BOOST:v1 -->
위치: content-header 닫힘 직후, container-fluid 시작 전.
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
FILE = os.path.join(BASE, 'vuln-hub.html')
MARKER = '<!-- WVS-HERO-BOOST:v1 -->'

HERO = '''
<!-- WVS-HERO-BOOST:v1 -->
<style>
.wvs-hero{margin:0 0 2rem;border-radius:18px;overflow:hidden;background:linear-gradient(120deg,#0b1220 0%,#1a1030 55%,#2a0f1e 100%);color:#e2e8f0;padding:2rem 2.2rem;position:relative;box-shadow:0 10px 30px rgba(15,23,42,.25)}
.wvs-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(600px 200px at 85% -10%,rgba(239,68,68,.25),transparent 60%),radial-gradient(500px 220px at 10% 110%,rgba(167,139,250,.2),transparent 60%);pointer-events:none}
.wvs-hero .wh-in{position:relative;display:flex;gap:2rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
.wvs-hero .wh-badge{display:inline-flex;align-items:center;gap:8px;font-size:.72rem;font-weight:800;letter-spacing:.4px;color:#fca5a5;border:1px solid rgba(239,68,68,.45);background:rgba(239,68,68,.1);border-radius:99px;padding:5px 14px;margin-bottom:12px}
.wvs-hero h2{font-weight:800;font-size:1.75rem;color:#fff;margin-bottom:8px;line-height:1.35}
.wvs-hero h2 .accent{color:#7dd3fc}
.wvs-hero .wh-sub{color:#9fb0ca;font-size:.9rem;line-height:1.7;max-width:560px;margin-bottom:16px}
.wh-stats{display:flex;gap:12px;flex-wrap:wrap}
.wh-stat{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px 18px;text-align:center;min-width:96px}
.wh-stat b{display:block;font-size:1.5rem;color:#fff;font-variant-numeric:tabular-nums}
.wh-stat span{font-size:.66rem;color:#8fa0ba;letter-spacing:.3px}
.wh-ctas{display:flex;flex-direction:column;gap:12px;min-width:250px}
.wh-cta{display:flex;align-items:center;gap:12px;text-decoration:none;border-radius:14px;padding:14px 18px;font-weight:800;transition:transform .15s ease,box-shadow .15s ease}
.wh-cta:hover{transform:translateY(-2px);color:#fff}
.wh-cta .ic{font-size:1.6rem}
.wh-cta small{display:block;font-weight:500;font-size:.7rem;opacity:.85;margin-top:2px}
.wh-cta.red{background:linear-gradient(135deg,#dc2626,#7f1d1d);color:#fff;box-shadow:0 6px 18px rgba(220,38,38,.35)}
.wh-cta.violet{background:linear-gradient(135deg,#7c3aed,#312e81);color:#fff;box-shadow:0 6px 18px rgba(124,58,237,.35)}
.wh-note{position:relative;margin-top:14px;font-size:.72rem;color:#7c8aa5}
@media(max-width:800px){.wvs-hero .wh-in{flex-direction:column;align-items:stretch}.wh-ctas{flex-direction:row}.wh-cta{flex:1}}
</style>
<section class="wvs-hero">
  <div class="wh-in">
    <div>
      <div class="wh-badge">🏆 원티드 AI Championship 2026 출품작</div>
      <h2>AI가 공격하고, 당신이 막는다<br><span class="accent">생성 → 적응 → 검증</span>이 폐루프로 돌아가는 보안 훈련장</h2>
      <p class="wh-sub">AI 레드팀 에이전트가 230종 시나리오 DB를 <b>도구로 호출</b>해 공격 체인을 조립하고, AI가 만든 문제는
        <b>기계 검증</b>을 통과해야만 출제됩니다. API 키 없이도 즉시 체험할 수 있습니다.</p>
      <div class="wh-stats">
        <div class="wh-stat"><b data-cnt="230">0</b><span>공격 시나리오</span></div>
        <div class="wh-stat"><b data-cnt="425">0</b><span>학습 페이지</span></div>
        <div class="wh-stat"><b data-cnt="10">0</b><span>보안 도메인</span></div>
        <div class="wh-stat"><b data-cnt="20">0+</b><span>학습 도구</span></div>
      </div>
    </div>
    <div class="wh-ctas">
      <a class="wh-cta red" href="redteam.html"><span class="ic">🦹</span><span>레드팀 아레나<small>AI 공격자 vs 나 · 4단계 체인 방어</small></span></a>
      <a class="wh-cta violet" href="quiz-forge.html"><span class="ic">🔨</span><span>AI 문제 포지<small>AI 생성 → 기계 검증 출제 · 통계 공개</small></span></a>
    </div>
  </div>
  <div class="wh-note">🔑 내 Anthropic 키를 등록하면 무제한 실시간 AI · 키 없이는 공유 AI(일 12회) → 데모 규칙 엔진 순서로 자동 폴백</div>
</section>
<script>
(function(){
  var els=document.querySelectorAll('.wh-stat b[data-cnt]');
  els.forEach(function(el){
    var target=+el.getAttribute('data-cnt'),cur=0,step=Math.max(1,Math.round(target/38));
    var iv=setInterval(function(){cur+=step;if(cur>=target){cur=target;clearInterval(iv);}el.textContent=cur+(el.textContent.indexOf('+')>=0?'+':'');},24);
  });
})();
</script>
<!-- /WVS-HERO-BOOST -->
'''

ANCHOR = '<div class="container-fluid p-4">'


def main():
    with open(FILE, encoding='utf-8', newline='') as f:
        h = f.read()
    if MARKER in h:
        print('SKIP: 이미 적용됨')
        return
    i = h.find(ANCHOR)
    if i < 0:
        print('FAIL: 앵커 없음')
        return
    nl = '\r\n' if '\r\n' in h[:2000] else '\n'
    block = HERO.replace('\n', nl)
    h = h[:i] + block + nl + '        ' + h[i:]
    with open(FILE, 'w', encoding='utf-8', newline='') as f:
        f.write(h)
    print('OK: hero 주입 완료')


if __name__ == '__main__':
    main()
