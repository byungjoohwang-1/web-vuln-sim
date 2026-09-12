# -*- coding: utf-8 -*-
"""개인정보 영향평가 수행 안내서(2025.10, 개인정보보호위원회·KISA) 파서.

PDF 본문 Ⅲ장 "개인정보 영향평가 항목"에서 평가항목(N.N.N)을 구조화해
public/js/pia-items.json 을 생성한다.

각 항목: code, area_no, area, field_no, field, subfield, question,
        checkpoints[](주요 점검 사항), explain(지표 해설), laws[](관련 법령·지침)

사용: python parse_pia_guide.py
"""
import os
import re
import json
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '..', 'books', '개인정보', '개인정보_영향평가_수행안내서(2025.10).pdf')
OUT = os.path.join(BASE, '..', 'public', 'js', 'pia-items.json')

SOURCE = '개인정보 영향평가 수행 안내서(2025.10.) · 개인정보보호위원회 / 한국인터넷진흥원'

# 평가영역(Ⅰ~Ⅴ) — 안내서 Ⅲ장 항목 개요표 기준
AREAS = {
    1: '대상기관 개인정보보호 관리체계',
    2: '대상시스템의 개인정보보호 관리체계',
    3: '개인정보 처리단계별 보호조치',
    4: '대상시스템의 기술적 보호조치',
    5: '특정 IT기술 활용 시 개인정보보호',
}

# 평가분야 — 안내서 항목 개요표 기준(PDF 파싱 결과와 교차 검증)
FIELDS = {
    '1.1': '개인정보보호 조직', '1.2': '개인정보보호 계획',
    '1.3': '개인정보 침해대응', '1.4': '정보주체 권리보장',
    '2.1': '개인정보취급자 관리', '2.2': '개인정보파일 관리',
    '2.3': '개인정보 처리방침', '2.4': '공공시스템 내부 관리계획',
    '3.1': '수집', '3.2': '보유', '3.3': '이용·제공', '3.4': '위탁', '3.5': '파기',
    '4.1': '접근권한 관리', '4.2': '접근통제', '4.3': '개인정보의 암호화',
    '4.4': '접속기록의 보관 및 점검', '4.5': '악성프로그램 등 방지',
    '4.6': '물리적 접근방지', '4.7': '개인정보의 파기',
    '4.8': '기타 기술적 보호조치', '4.9': '개인정보처리구역 보호조치',
    '5.1': '고정형 영상정보처리기기', '5.2': '이동형 영상정보처리기기',
    '5.3': '생체인식정보', '5.4': '위치정보', '5.5': '가명정보',
    '5.6': '자동화된 결정', '5.7': '인공지능(AI)',
}

CODE_RE = re.compile(r'^([1-5]\.\d{1,2}\.\d{1,2})\s*$', re.M)

# 페이지 머리말/꼬리말/세로 장표기 등 잡음
NOISE_LINES = (
    re.compile(r'^\s*\d{1,3}\s{1,4}개인정보 영향평가 수행 안내서\s*$'),
    re.compile(r'^\s*Ⅲ\.\s*개인정보 영향평가 항목\s+\d{1,3}\s*$'),
    re.compile(r'^\s*(평가영역|평가분야|세부분야|No\.|평가항목|질의문 코드|질의문)\s*$'),
    re.compile(r'^\s*[가-힣]\s*$'),          # 세로쓰기 장표기 한 글자
    re.compile(r'^\s*[1-5]\.\s*$'),
    re.compile(r'^\s*$'),
)


def extract_text():
    import fitz
    doc = fitz.open(PDF)
    return '\n'.join(page.get_text() for page in doc)


def clean_block(s):
    """블록에서 페이지 머리말/꼬리말/세로 장표기 제거 후 줄 목록 반환.

    끝 공백은 보존한다 — 줄바꿈이 단어 중간인지(공백 없음) 어절 경계인지(공백 있음)
    판단하는 근거로 join_wrapped 가 사용한다.
    """
    out = []
    for ln in s.split('\n'):
        if any(p.match(ln) for p in NOISE_LINES):
            continue
        out.append(ln)
    return out


def join_wrapped(lines):
    """PDF 줄바꿈으로 끊긴 문장을 이어붙인다.

    원문 줄 끝에 공백이 없고 한글이 이어지면 단어가 잘린 것이므로 붙여 쓴다
    (예: '개인정보 처리' + '방침에' → '개인정보 처리방침에').
    """
    out, prev_ws = '', True
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if not out:
            out = s
        else:
            glue = ' '
            if not prev_ws and re.match(r'[가-힣]', s) and re.search(r'[가-힣]$', out):
                glue = ''
            out += glue + s
        prev_ws = ln.endswith((' ', '\t'))
    return re.sub(r'[ \t]+', ' ', out).strip()


def split_detail_blocks(text):
    """Ⅲ장 '개인정보 영향평가 항목 설명' 구간을 코드 단위 블록으로 분리."""
    start = text.find('개인정보 영향평가 항목 설명', 80000)
    if start < 0:
        raise SystemExit('detail section not found')
    # Ⅳ장(영향평가서 작성) 또는 부록 시작 전까지
    end = len(text)
    for marker in ('개인정보 영향평가서 작성', '부록1. 개인정보 영향평가 양식'):
        p = text.find(marker, start + 1000)
        if p > 0:
            end = min(end, p)
    body = text[start:end]

    marks = [(m.start(), m.group(1)) for m in CODE_RE.finditer(body)]
    blocks = []
    for i, (pos, code) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        head = body[:pos]          # 세부분야 추출용(코드 직전 텍스트)
        blocks.append((code, head, body[pos + len(code):nxt]))
    return blocks


def parse_subfield(head):
    """코드 직전의 '질의문' 헤더 뒤 텍스트 = 세부분야."""
    p = head.rfind('질의문\n')
    if p < 0:
        return ''
    seg = head[p + len('질의문\n'):]
    lines = clean_block(seg)
    name = join_wrapped(lines)
    # 너무 길면 세부분야가 아니라 이전 항목 본문 꼬리 — 버린다
    return name if 0 < len(name) <= 40 else ''


SECT_MARKS = ['【주요 점검 사항】', '【지표 해설】', '【용어 설명】', '【참고】', '관련 법령ㆍ지침', '관련 법령·지침']


def cut_section(body, start_mark, stops):
    i = body.find(start_mark)
    if i < 0:
        return ''
    i += len(start_mark)
    j = len(body)
    for s in stops:
        k = body.find(s, i)
        if 0 <= k < j:
            j = k
    return body[i:j]


def parse_question(body):
    """본문 앞부분에서 '…습니까?' 로 끝나는 질의문 추출."""
    head = body.split('【')[0]
    lines = clean_block(head)
    txt = join_wrapped(lines)
    m = re.search(r'^(.*?습니까\?)', txt)
    return m.group(1) if m else txt[:300]


def parse_checkpoints(body):
    """'1. … 2. …' 번호 목록 분해. 본문 중 우연한 숫자와 섞이지 않도록
    다음에 올 번호(1→2→3…)만 순서대로 찾는다."""
    seg = cut_section(body, '【주요 점검 사항】', SECT_MARKS[1:])
    if not seg:
        return []
    txt = join_wrapped(clean_block(seg))
    marks, n, frm = [], 1, 0
    while True:
        m = re.search(r'(?:(?<=\s)|^)%d\.\s' % n, txt[frm:])
        if not m:
            break
        marks.append((frm + m.start(), frm + m.end()))
        frm += m.end()
        n += 1
    if not marks:
        return [txt] if len(txt) > 6 else []
    out = []
    for i, (_, e) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(txt)
        p = txt[e:end].strip(' ·')
        if len(p) > 6:
            out.append(p)
    return out


def parse_explain(body):
    seg = cut_section(body, '【지표 해설】', ['【용어 설명】', '【참고】', '관련 법령'])
    if not seg:
        return ''
    txt = join_wrapped(clean_block(seg))
    # 'n ' 글머리(원문 ■ 기호가 n 으로 추출됨) → 문단 분리
    txt = re.sub(r'\s*\bn\s+', '\n• ', txt).strip()
    if len(txt) > 2200:                     # 문장 중간에서 잘리지 않게 정리
        cut = txt[:2200]
        p = max(cut.rfind('다.'), cut.rfind('함'), cut.rfind('\n'))
        txt = (cut[:p + 2] if p > 800 else cut).rstrip() + ' …'
    return txt


LAW_RE = re.compile(r'【([^】]{2,30})】\s*((?:제\d+조[^\n【]*\n?)+)')


def parse_laws(body):
    i = -1
    for mark in ('관련 법령ㆍ지침', '관련 법령·지침'):
        i = body.find(mark)
        if i >= 0:
            break
    if i < 0:
        return []
    seg = body[i:]
    out = []
    for m in LAW_RE.finditer(seg):
        act = m.group(1).strip()
        for art in re.findall(r'제\d+조(?:의\d+)?\([^)]*\)|제\d+조(?:의\d+)?', m.group(2)):
            out.append('%s %s' % (act, art))
    return out[:12]


def main():
    text = extract_text()
    blocks = split_detail_blocks(text)

    items, seen = [], set()
    for code, head, body in blocks:
        if code in seen:
            continue
        field_no = code.rsplit('.', 1)[0]
        if field_no not in FIELDS:
            continue
        q = parse_question(body)
        if not q.endswith('습니까?'):
            continue                      # 본문 인용 등 오탐 제외
        seen.add(code)
        area_no = int(code.split('.')[0])
        items.append({
            'code': code,
            'area_no': area_no,
            'area': AREAS[area_no],
            'field_no': field_no,
            'field': FIELDS[field_no],
            'subfield': parse_subfield(head),
            'question': q,
            'checkpoints': parse_checkpoints(body),
            'explain': parse_explain(body),
            'laws': parse_laws(body),
        })

    items.sort(key=lambda x: [int(n) for n in x['code'].split('.')])

    data = {
        'source': SOURCE,
        'generated': datetime.date.today().isoformat(),
        'areas': [{'no': k, 'name': v} for k, v in sorted(AREAS.items())],
        'fields': [{'no': k, 'name': v} for k, v in sorted(
            FIELDS.items(), key=lambda kv: [int(n) for n in kv[0].split('.')])],
        'items': items,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print('items:', len(items))
    miss_cp = [i['code'] for i in items if not i['checkpoints']]
    miss_ex = [i['code'] for i in items if not i['explain']]
    miss_law = [i['code'] for i in items if not i['laws']]
    miss_sf = [i['code'] for i in items if not i['subfield']]
    print('no checkpoints:', len(miss_cp), miss_cp[:12])
    print('no explain    :', len(miss_ex), miss_ex[:12])
    print('no laws       :', len(miss_law), miss_law[:12])
    print('no subfield   :', len(miss_sf), miss_sf[:12])
    print('wrote', OUT)


if __name__ == '__main__':
    main()
