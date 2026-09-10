# -*- coding: utf-8 -*-
"""13_ai-aiXX AI/LLM·미래보안 시뮬레이터 생성기.
gen_infra 의 렌더링(취약/안전 상태 토글 + 조치 + 체크리스트)을 그대로 재사용하되,
푸터/기준 라벨만 AI 도메인에 맞게 교정한다. (인프라 KISA 문구 → AI 보안 출처)
사용: python gen_ai.py            # specs_ai.SPECS 전체(26종) 생성
"""
import os
import gen_infra

# 공통 자산(다른 넘버드 시뮬 페이지와 동일): PWA/파비콘/폰트 preconnect/언어토글
HEAD_ASSETS = (
    '<meta name="theme-color" content="#0ea5e9">'
    '<link rel="manifest" href="/manifest.json">'
    '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
    '<script src="/js/pwa.js" defer></script>'
)
PRECONNECT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
)

# 인프라 전용 문구를 AI 도메인 문구로 치환 + 공통 자산 주입한 템플릿
PAGE = (gen_infra.PAGE
    .replace(
        '주요정보통신기반시설 기술적 취약점 분석·평가 가이드(KISA) 기반 · 교육용 재구성',
        'OWASP LLM Top 10 (2025) · 적대적 ML · 딥페이크 · PQC · AI 거버넌스 기반 · 교육용 재구성')
    .replace('점검기준: {kisa_ref}', '참고 기준: {kisa_ref}')
    .replace('<head>\n<meta charset="UTF-8">', '<head>\n' + HEAD_ASSETS + '\n<meta charset="UTF-8">')
    .replace('<link href="https://fonts.googleapis.com', PRECONNECT + '\n<link href="https://fonts.googleapis.com')
    .replace('</body>\n</html>', '<script src="js/bilingual.js"></script>\n</body>\n</html>'))


def render(s):
    """gen_infra.render 와 동일하되 AI 전용 PAGE 사용."""
    vt = gen_infra.term_html(s['vuln_term'])
    st = gen_infra.term_html(s['secure_term'])
    fix = ''.join('<li>%s</li>' % f for f in s['fix_steps'])
    chk = ''.join('<li><span class="box"></span><span>%s</span></li>' % gen_infra.esc(c) for c in s['checklist'])
    host = s.get('host', 'ai$')
    return PAGE.format(
        code=gen_infra.esc(s['code']), title=gen_infra.esc(s['title']), icon=s['icon'],
        category=gen_infra.esc(s['category']), severity=s['severity'], description=s['description'],
        vuln_term=vt, secure_term=st, vuln_term_js=gen_infra.jss(vt), secure_term_js=gen_infra.jss(st),
        fix_steps=fix, checklist=chk, kisa_ref=gen_infra.esc(s['kisa_ref']),
        host=gen_infra.esc(host), host_js=gen_infra.jss(host),
    )


def main():
    import specs_ai
    total = 0
    for s in specs_ai.SPECS:
        path = os.path.join(gen_infra.OUT_DIR, s['file'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(render(s))
        print('wrote', s['file'])
        total += 1
    print('TOTAL', total)


if __name__ == '__main__':
    main()
