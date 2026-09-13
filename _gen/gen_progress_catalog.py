# -*- coding: utf-8 -*-
"""통합 진도 시스템용 학습 항목 카탈로그 생성기.
public/*.html(넘버드 콘텐츠 + sim-*)을 스캔해 {id,code,title,cat,group,cwe}를
public/js/progress-catalog.json 으로 출력. 대시보드/홈이 이 카탈로그 + wvs_progress로
카테고리·CWE별 마스터리를 계산한다. (진도 엔진 progress.js 와 동일한 학습 항목 정의)
"""
import json
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')

# 접두사 → (카테고리 라벨, 허브 그룹)
PREFIX = [
    ('03_code', ('시큐어코딩 · 구현', 'A')),
    ('04_design', ('시큐어코딩 · 설계', 'A')),
    ('05_linux', ('인프라 · UNIX', 'B')),
    ('06_db', ('인프라 · DBMS', 'B')),
    ('07_fin', ('금융 · 전자금융', 'C')),
    ('08_win', ('인프라 · Windows', 'B')),
    ('09_net', ('인프라 · 네트워크', 'B')),
    ('10_sec', ('인프라 · 보안장비', 'B')),
    ('11_cloud', ('인프라 · 클라우드', 'B')),
    ('12_ics', ('인프라 · ICS/제어', 'B')),
    ('13_ai', ('AI·미래보안', 'D')),
    ('14_auto', ('자동차 보안', 'E')),
    ('15_privacy', ('개인정보보호', 'F')),
    ('16_zt', ('제로트러스트', 'G')),
]

# 실습 도구 — 접두사 규칙으로는 안 잡히지만 진도·XP 를 기록하는 페이지.
# 이게 카탈로그에 없으면 도구에서 완료해도 '내 기록'의 완료 수에 안 잡히고
# XP 만 올라가 수치가 서로 어긋난다(G02).
TOOLS = [
    ('vulnlab.html', ('실습 도구', 'B')),
    ('redteam.html', ('실습 도구', 'B')),
    ('quiz-forge.html', ('실습 도구', 'B')),
    ('incident.html', ('대표 사건 실습', 'E')),   # G08 — 자동차·개인정보를 잇는 4단계 사건
    ('privacy-data-transfer.html', ('개인정보 실습', 'F')),
    ('privacy-rights-desk.html', ('개인정보 실습', 'F')),
    ('privacy-breach-72h.html', ('개인정보 실습', 'F')),
    # 인증심사·산업기술보호는 기술 취약점이 아니라 관리체계/컴플라이언스 실습이다.
    ('audit-ismsp-lab.html', ('인증심사 · 관리체계', 'B')),
    ('industry-tech-protect.html', ('인증심사 · 관리체계', 'B')),

    # [G02 후속] 아래 12개는 예전부터 WVSProgress.complete() 로 완료를 기록해 왔는데
    # 카탈로그에 없어서 XP 만 오르고 '완료 수'에는 안 잡혔다(정확히 G02 가 없앤 그 어긋남).
    # tools/test-platform-integration.js 가 이 불일치를 검사한다.
    ('ai-grader.html', ('실습 도구', 'B')),
    ('lab-generator.html', ('실습 도구', 'B')),
    ('skill-assess.html', ('실습 도구', 'B')),
    ('fin-eval.html', ('금융 · 전자금융', 'C')),
    ('mp-assessment.html', ('인증심사 · 관리체계', 'B')),
    ('pia-assessment.html', ('개인정보 실습', 'F')),
    ('privacy-breach-drill.html', ('개인정보 실습', 'F')),
    ('privacy-consent-designer.html', ('개인정보 실습', 'F')),
    ('privacy-policy-builder.html', ('개인정보 실습', 'F')),
    ('privacy-policy-eval.html', ('개인정보 실습', 'F')),
    ('privacy-processor-check.html', ('개인정보 실습', 'F')),
    ('privacy-quiz.html', ('개인정보 실습', 'F')),
]
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(r'^([A-Z]{1,4}-\d{1,3})\s*[:：]\s*(.+)$')
CWE_RE = re.compile(r'CWE-\d+')
SUFFIXES = [' | 교육 시뮬레이터', ' - 교육 시뮬레이터', ' - 실습 시뮬레이터', ' | 실습 시뮬레이터',
            ' · WEB-VULN-SIM', ' | WEB-VULN-SIM', ' - WEB-VULN-SIM']
PREFIX_STRIP = ['전자금융 보안: ', '전자금융 보안 · ', '전자금융 보안 - ']


TOOL_MAP = dict(TOOLS)


def category(name):
    if name in TOOL_MAP:
        return TOOL_MAP[name]
    for pfx, meta in PREFIX:
        if name.startswith(pfx):
            return meta
    if name.startswith('sim-'):
        return ('실습 시뮬레이터', 'B')
    return None  # 학습 항목 아님


def clean_title(raw):
    t = re.sub(r'\s+', ' ', raw).strip()
    for s in SUFFIXES:
        if t.endswith(s):
            t = t[:-len(s)].strip()
    for p in PREFIX_STRIP:
        if t.startswith(p):
            t = t[len(p):].strip()
    return t


def sim_cwe_map():
    """sim-map.js 의 SIM_BY_CWE 를 역매핑: sim파일 → CWE."""
    path = os.path.join(PUB, 'js', 'sim-map.js')
    out = {}
    try:
        with open(path, encoding='utf-8') as f:
            js = f.read()
    except OSError:
        return out
    for cwe, fname in re.findall(r"'(CWE-\d+)'\s*:\s*'([\w.\-]+\.html)'", js):
        out[fname] = cwe
    return out


def sync_progress_js():
    """progress.js 의 학습 항목 판별식을 이 파일의 정의에서 다시 생성한다.

    [G02] 두 곳에서 따로 관리하다 어긋난 것이 원인이었으므로 정의를 한 곳으로 모은다.
    런타임에 카탈로그를 받아오게 하면 모든 페이지에 fetch 가 붙으니, 빌드 시점에 주입한다.
    """
    path = os.path.join(PUB, 'js', 'progress.js')
    with open(path, encoding='utf-8') as f:
        src = f.read()
    begin, end = '/* <generated:learnable> */', '/* </generated:learnable> */'
    i, j = src.find(begin), src.find(end)
    if i < 0 or j < 0:
        print('  WARN progress.js 에 생성 마커가 없어 건너뜀')
        return
    prefixes = '|'.join(p for p, _ in PREFIX)
    # 파일명에 정규식 특수문자는 '.' 뿐이라 그것만 이스케이프한다(re.escape 는 '-' 까지 escape 해 지저분해진다)
    tools = '|'.join(n.replace('.', r'\.') for n, _ in TOOLS)
    block = (begin + '\n'
             '  var LEARNABLE = /^(%s)/;\n'
             '  var TOOLS = /^(%s)$/;\n  ' % (prefixes, tools))
    new = src[:i] + block + src[j:]
    if new != src:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new)
        print('  progress.js 학습 항목 판별식 갱신')


def main():
    cwe_by_file = sim_cwe_map()
    items = []
    for name in sorted(os.listdir(PUB)):
        if not name.endswith('.html'):
            continue
        meta = category(name)
        if not meta:
            continue
        cat, group = meta
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            doc = f.read()
        m = TITLE_RE.search(doc)
        title = clean_title(m.group(1)) if m else name
        code = ''
        cm = CODE_RE.match(title)
        if cm:
            code, title = cm.group(1), cm.group(2).strip()
        cwe = cwe_by_file.get(name)
        if not cwe:
            found = CWE_RE.findall(doc)
            if found:
                # 본문에 CWE 표기가 하나뿐인 경우에만 신뢰(중복 언급 회피)
                uniq = sorted(set(found))
                if len(uniq) == 1:
                    cwe = uniq[0]
        item = {'id': name, 'title': title, 'cat': cat, 'group': group}
        if code:
            item['code'] = code
        if cwe:
            item['cwe'] = cwe
        items.append(item)

    catalog = {'version': 1, 'count': len(items), 'items': items}
    out_path = os.path.join(PUB, 'js', 'progress-catalog.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, separators=(',', ':'))

    sync_progress_js()
    # 카테고리별 집계 리포트
    by_cat = {}
    for it in items:
        by_cat[it['cat']] = by_cat.get(it['cat'], 0) + 1
    print('gen_progress_catalog: %d items -> js/progress-catalog.json' % len(items))
    for c in sorted(by_cat):
        print('  %-22s %3d' % (c, by_cat[c]))


if __name__ == '__main__':
    main()
