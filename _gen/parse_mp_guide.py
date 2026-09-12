# -*- coding: utf-8 -*-
"""주요정보통신기반시설 관리·물리적 취약점 분석·평가 방법 안내서(2026, KISA) 파서.
PDF 본문에서 점검항목(A-NN/P-NN)을 구조화해 public/js/kisa-mp-items.json 생성.
각 항목: code, domain(관리적|물리적), section_no, section, requirement, org, detail,
        consider, laws{공통,공공기관,금융회사,ICT기업}, evidence[]"""
import os, re, json

BASE = os.path.dirname(__file__)
PDF = os.path.join(BASE, '..', 'books', '주요정보통신기반시설 관리·물리적 취약점 분석·평가 방법 안내서.pdf')
OUT = os.path.join(BASE, '..', 'public', 'js', 'kisa-mp-items.json')

SECTIONS = {  # 정규 섹션명(번호+도메인 무관 최장일치용)
    '정보보호 정책', '정보보호 조직', '자산분류', '위험관리', '감사', '인적 보안', '인적보안',
    '외부자보안', '외부자 보안', '교육 및 훈련', '인증 및 권한관리', '접근통제', '운영관리',
    '보안관리', '사고대응', '업무연속성', '물리보안', '출입통제', '보호구역', '보호설비',
}

def extract_text():
    from pypdf import PdfReader
    r = PdfReader(PDF)
    return '\n'.join((p.extract_text() or '') for p in r.pages)

def clean(t):
    # 페이지 머리말/꼬리말/장 표기/페이지번호 제거
    t = re.sub(r'\d{2}\.\s*(관리적|물리적) 분야 기본 항목2026 주요정보통신기반시설[^\n]*', ' ', t)
    t = re.sub(r'(관리적|물리적) 분야 기본 항목Chapter \d+\s*2026[^\n]*', ' ', t)
    t = re.sub(r'\|\s*한국인터넷진흥원\s*\|', ' ', t)
    t = re.sub(r'2026 주요정보통신기반시설 관리·물리적 취약점 분석·평가 방법 안내서', ' ', t)
    t = re.sub(r'Chapter \d+', ' ', t)
    t = re.sub(r'\n\s*\d{1,3}\s*\n', '\n', t)  # 페이지 번호 단독 줄
    return t

def cut(s, start, ends):
    """s에서 start 라벨 이후 ~ ends 중 가장 먼저 오는 라벨 전까지."""
    i = s.find(start)
    if i < 0:
        return ''
    i += len(start)
    j = len(s)
    for e in ends:
        k = s.find(e, i)
        if 0 <= k < j:
            j = k
    return s[i:j].strip()

def parse_laws(block):
    laws = {}
    order = ['공통', '공공기관', '금융회사', 'ICT기업']
    # 각 주체 라벨로 분할
    idxs = []
    for key in order:
        p = block.find(key)
        if p >= 0:
            idxs.append((p, key))
    idxs.sort()
    for n, (pos, key) in enumerate(idxs):
        s = pos + len(key)
        e = idxs[n + 1][0] if n + 1 < len(idxs) else len(block)
        val = block[s:e].strip(' ·:：')
        if val:
            laws[key] = re.sub(r'\s+', ' ', val)
    return laws

def parse_evidence(block):
    # ☐ 로 분할
    parts = [x.strip() for x in re.split(r'☐', block) if x.strip()]
    return [re.sub(r'\s+', ' ', p)[:200] for p in parts]

SECTION_NORM = {'인적 보안': '인적보안', '외부자 보안': '외부자보안'}

def norm_section(name):
    return SECTION_NORM.get(name, name)

def strip_section_name(after_dot):
    """'자산분류주요정보통신기반시설 내 모든...' 에서 섹션명 제거 후 요건 반환."""
    for name in sorted(SECTIONS, key=len, reverse=True):
        if after_dot.startswith(name):
            return name, after_dot[len(name):].strip()
    # 폴백: 앞 2~6자를 섹션 추정
    m = re.match(r'([가-힣 ]{2,8}?)([가-힣A-Za-z0-9].{4,})', after_dot)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return '', after_dot

def main():
    raw = extract_text()
    t = clean(raw)
    # 부록(참고자료) 시작 지점에서 절단 — 마지막 항목(P-18) 본문에 부록 목차가 번지는 것 방지.
    # 앞쪽 목차에도 '<참고 제1호>'가 있으므로 본문 후반부(50% 이후)의 첫 등장을 부록 경계로 사용.
    apx = t.find('<참고 제1호>', len(t) // 2)
    if apx > 0:
        t = t[:apx]
    # 항목 분할: 코드(1~3자리)+도메인+"분야 > N. " (사고대응 A-104, 업무연속성 A-114 등 3자리 포함)
    pat = re.compile(r'([AP]-\d{1,3})\s*(관리적|물리적) 분야\s*>\s*(\d+)\.\s*')
    marks = list(pat.finditer(t))
    items = []
    seen = set()
    for n, m in enumerate(marks):
        code = m.group(1)
        if code in seen:
            continue
        seen.add(code)
        # 도메인은 코드 접두로 판정(추출 텍스트의 도메인 라벨이 물리 항목에서 '관리적'으로 오병합됨)
        domain = '물리적' if code.startswith('P-') else '관리적'
        section_no = int(m.group(3))
        body_start = m.end()
        body_end = marks[n + 1].start() if n + 1 < len(marks) else len(t)
        body = t[body_start:body_end]
        # 요건: 섹션명 직후 ~ '관련 조직'
        head = cut_head = body
        req_block = body[:body.find('관련 조직')] if '관련 조직' in body else body[:400]
        section, requirement = strip_section_name(req_block)
        requirement = re.sub(r'\s+', ' ', requirement).strip()
        org = cut(body, '관련 조직', ['세부 설명', '세부설명'])
        detail = cut(body, '세부 설명', ['고려 사항', '고려사항', '관계 법규'])
        if not detail:
            detail = cut(body, '세부설명', ['고려 사항', '고려사항', '관계 법규'])
        consider = cut(body, '고려 사항', ['관계 법규'])
        if not consider:
            consider = cut(body, '고려사항', ['관계 법규'])
        laws_block = cut(body, '관계 법규', ['확인 대상', '확인대상'])
        evid_block = ''
        for lab in ['확인 대상(예시)', '확인 대상', '확인대상(예시)', '확인대상']:
            p = body.find(lab)
            if p >= 0:
                evid_block = body[p + len(lab):]
                break
        items.append({
            'code': code,
            'domain': domain,
            'section_no': section_no,
            'section': norm_section(section),
            'requirement': requirement[:400],
            'org': re.sub(r'\s+', ' ', org)[:60],
            'detail': re.sub(r'\s+', ' ', detail)[:1200],
            'consider': re.sub(r'\s+', ' ', consider)[:1200],
            'laws': parse_laws(laws_block),
            'evidence': parse_evidence(evid_block)[:8],
        })
    # 코드 순 정렬(도메인 → 숫자)
    def key(it):
        return (0 if it['domain'] == '관리적' else 1, int(it['code'].split('-')[1]))
    items.sort(key=key)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({'source': 'KISA 주요정보통신기반시설 관리·물리적 취약점 분석·평가 방법 안내서(2026)',
               'count': len(items), 'items': items},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('parsed items:', len(items))
    print('관리적:', sum(1 for i in items if i['domain'] == '관리적'),
          '물리적:', sum(1 for i in items if i['domain'] == '물리적'))
    # 품질 점검: 요건/법규 비어있는 항목
    empty_req = [i['code'] for i in items if len(i['requirement']) < 8]
    no_laws = [i['code'] for i in items if not i['laws']]
    print('빈 요건:', len(empty_req), empty_req[:10])
    print('법규없음:', len(no_laws), no_laws[:10])
    # 샘플 3개
    for i in items[:2] + items[-1:]:
        print('\n---', i['code'], i['domain'], i['section_no'], i['section'])
        print('  요건:', i['requirement'][:90])
        print('  법규주체:', list(i['laws'].keys()))
        print('  확인대상:', i['evidence'][:2])

if __name__ == '__main__':
    main()
