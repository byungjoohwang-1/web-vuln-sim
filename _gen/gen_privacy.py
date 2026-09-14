# -*- coding: utf-8 -*-
"""15_privacy-pvXX 개인정보보호 시뮬레이터 생성기.

gen_infra 의 렌더링(취약/안전 상태 토글 + 조치 + 체크리스트)을 재사용하되,
푸터/기준 라벨을 개인정보 도메인에 맞게 교정한다.
사용: python gen_privacy.py            # specs_privacy + specs_privacy_b 전체 생성
"""
import os
import gen_infra

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

# 개인정보 도메인 문구로 치환 + 공통 자산 주입 + 관련 도구 링크
TOOLBAR = (
    '<div class="topbar"><a href="index.html">&larr; cd /index</a>'
    '&nbsp;&nbsp;<a href="vuln-hub.html">취약점 학습 허브</a>'
    '&nbsp;&nbsp;<a href="pia-assessment.html">영향평가 자가진단</a>'
    '&nbsp;&nbsp;<a href="privacy-policy-builder.html">처리방침 작성기</a>'
    '&nbsp;&nbsp;<a href="pseudonym-lab.html">가명처리 실습실</a></div>'
)

PAGE = (gen_infra.PAGE
    .replace(
        'KISA 공개 가이드의 점검 항목 구성을 참고한 교육용 재구성 · 항목 번호는 이 사이트의 자체 번호이며 공식 고시의 항목 번호와 다릅니다',
        '「개인정보 보호법」·개인정보 영향평가 수행 안내서·가명정보 처리 가이드라인 등 '
        '개인정보보호위원회 공개 자료 기반 · 교육용 재구성')
    .replace('점검기준: {kisa_ref}', '근거: {kisa_ref}')
    .replace('<div class="topbar"><a href="index.html">&larr; cd /index</a></div>', TOOLBAR)
    .replace('<head>\n<meta charset="UTF-8">', '<head>\n' + HEAD_ASSETS + '\n<meta charset="UTF-8">')
    .replace('<link href="https://fonts.googleapis.com', PRECONNECT + '\n<link href="https://fonts.googleapis.com')
    .replace('</body>\n</html>', '<script src="js/bilingual.js"></script>\n</body>\n</html>'))


def render(s):
    vt = gen_infra.term_html(s['vuln_term'])
    st = gen_infra.term_html(s['secure_term'])
    fix = ''.join('<li>%s</li>' % f for f in s['fix_steps'])
    chk = ''.join('<li><span class="box"></span><span>%s</span></li>' % gen_infra.esc(c) for c in s['checklist'])
    host = s.get('host', 'privacy$')
    return PAGE.format(
        code=gen_infra.esc(s['code']), title=gen_infra.esc(s['title']), icon=s['icon'],
        category=gen_infra.esc(s['category']), severity=s['severity'], description=s['description'],
        vuln_term=vt, secure_term=st, vuln_term_js=gen_infra.jss(vt), secure_term_js=gen_infra.jss(st),
        fix_steps=fix, checklist=chk, kisa_ref=gen_infra.esc(s['kisa_ref']),
        host=gen_infra.esc(host), host_js=gen_infra.jss(host),
    )


def all_specs():
    import specs_privacy, specs_privacy_b
    return specs_privacy.SPECS + specs_privacy_b.SPECS


def main():
    total = 0
    for s in all_specs():
        path = os.path.join(gen_infra.OUT_DIR, s['file'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(render(s))
        print('wrote', s['file'])
        total += 1
    print('TOTAL', total)


if __name__ == '__main__':
    main()
