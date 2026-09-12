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
]
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(r'^([A-Z]{1,4}-\d{1,3})\s*[:：]\s*(.+)$')
CWE_RE = re.compile(r'CWE-\d+')
SUFFIXES = [' | 교육 시뮬레이터', ' - 교육 시뮬레이터', ' - 실습 시뮬레이터', ' | 실습 시뮬레이터',
            ' · WEB-VULN-SIM', ' | WEB-VULN-SIM', ' - WEB-VULN-SIM']
PREFIX_STRIP = ['전자금융 보안: ', '전자금융 보안 · ', '전자금융 보안 - ']


def category(name):
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
    # 카테고리별 집계 리포트
    by_cat = {}
    for it in items:
        by_cat[it['cat']] = by_cat.get(it['cat'], 0) + 1
    print('gen_progress_catalog: %d items -> js/progress-catalog.json' % len(items))
    for c in sorted(by_cat):
        print('  %-22s %3d' % (c, by_cat[c]))


if __name__ == '__main__':
    main()
