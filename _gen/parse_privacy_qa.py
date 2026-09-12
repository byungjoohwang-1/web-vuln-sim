# -*- coding: utf-8 -*-
"""개인정보 질의응답 모음집(2025.12., 개인정보보호위원회) 파서.

PDF → public/js/privacy-qa.json
각 문항: no, cat(대분류), q(질의), law(조항), verdict(O|X|COND|None), answer(답변 요지),
        detail(상세 근거), page

verdict 는 답변 첫 문장에서 규칙으로 도출한다. 규칙이 명확히 걸리지 않으면 None 으로 두고
퀴즈 채점 대상에서 빼 카드 학습으로만 쓴다(오답을 정답으로 가르치는 것을 막기 위함).

사용: python parse_privacy_qa.py
"""
import os
import re
import json
import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(BASE, '..', 'books', '개인정보', '1. 개인정보 질의응답 모음집(2025.12.).pdf')
OUT = os.path.join(BASE, '..', 'public', 'js', 'privacy-qa.json')

SOURCE = '개인정보 질의응답 모음집(2025.12.) · 개인정보보호위원회'

CATS = ['정의', '영상정보', '가명정보', '공공서비스', '민간사업자',
        '민감·고유식별정보', '위·수탁', '기타 특수분야']

Q_MARK = re.compile(r'\nQ\s*(\d{1,3})\s*\n')
# 페이지 머리말: "Ⅰ. 정의  5" / "6  개인정보 질의응답 모음집"
PAGE_HEAD = re.compile(
    r'\n(?:[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+\.\s*[^\n]{1,20}\s+\d{1,3}|\d{1,3}\s+개인정보 질의응답 모음집)\n')


def extract_text():
    import fitz
    return '\n'.join(p.get_text() for p in fitz.open(PDF))


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def join_wrapped(block):
    """PDF 줄바꿈 복원: 줄 끝에 공백이 없고 한글이 이어지면 붙여 쓴다."""
    out, prev_ws = '', True
    for ln in block.split('\n'):
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


def parse_toc(text):
    """목차에서 번호 → (조항, 대분류) 매핑."""
    head = text[:13000]
    # 대분류 위치
    cat_pos = []
    for m in re.finditer(r'\n([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\.\s*([가-힣·\s]{2,20})\n', head):
        name = norm(m.group(2))
        if name in CATS:
            cat_pos.append((m.start(), name))
    law, cat = {}, {}
    # 목차 행이 연달아 붙어 있어 앞뒤 개행을 소비하면 다음 행을 놓친다 → 전후를 룩비하인드/룩어헤드로.
    for m in re.finditer(r'(?<=\n)(\d{1,3})\n(.+?)\n(§[^\n]{1,40})\n(\d{1,3})(?=\n)', head, re.S):
        no = int(m.group(1))
        if no in law:
            continue
        law[no] = norm(m.group(3))
        c = ''
        for pos, name in cat_pos:
            if pos < m.start():
                c = name
        cat[no] = c
    return law, cat


# 답변의 O/X 판정은 자동 분류하지 않는다.
# 시도해 본 규칙 기반 분류는 O 64 / X 7 / 조건부 4 로 심하게 쏠렸고, 오분류가 그대로
# "틀린 정답"이 되어 학습자에게 전달된다. 채점은 출처(목차)에 명시된 근거 조문으로만 한다.

LAW_ART = re.compile(r'제\s*(\d{1,3})\s*조(?:의\s*(\d))?')


def law_key(law):
    """'§15, §17' 같은 조항 표기를 대표 조문 키로 정규화('제15조')."""
    if not law:
        return ''
    m = re.search(r'§\s*(\d{1,3})(?:의\s*(\d))?', law)
    if not m:
        return ''
    return '제%s조%s' % (m.group(1), ('의' + m.group(2)) if m.group(2) else '')


def main():
    text = extract_text()
    law_by_no, cat_by_no = parse_toc(text)

    marks = [(m.start(), m.end(), int(m.group(1))) for m in Q_MARK.finditer(text)]
    body_start = marks[0][0] if marks else 0

    items = []
    for i, (s, e, no) in enumerate(marks):
        # 질의문: 직전 페이지 머리말 이후 ~ Q 마커 직전
        prev_end = marks[i - 1][1] if i else body_start - 4000
        seg = text[max(prev_end, 0):s]
        heads = list(PAGE_HEAD.finditer(seg))
        q_raw = seg[heads[-1].end():] if heads else seg
        question = join_wrapped(q_raw)

        # 답변: Q 마커 이후 ~ 다음 질의문 시작(= 다음 블록의 마지막 페이지 머리말) 전
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        blk = text[e:nxt]
        heads2 = list(PAGE_HEAD.finditer(blk))
        ans_raw = blk[:heads2[-1].start()] if heads2 else blk
        ans_raw = PAGE_HEAD.sub('\n', ans_raw)

        # 요지(첫 문단) / 상세(○ 이하)
        parts = re.split(r'\n(?=[○▪])', ans_raw, 1)
        summary = join_wrapped(parts[0])
        detail = join_wrapped(parts[1]) if len(parts) > 1 else ''

        law = law_by_no.get(no, '')
        items.append({
            'no': no,
            'cat': cat_by_no.get(no, ''),
            'law': law,
            'lawKey': law_key(law),
            'q': question,
            'answer': summary,
            'detail': detail[:1600],
        })

    data = {
        'source': SOURCE,
        'generated': datetime.date.today().isoformat(),
        'cats': CATS,
        'count': len(items),
        'items': items,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    from collections import Counter
    graded = [x for x in items if x['lawKey']]
    print('items:', len(items), '| 조문 채점가능:', len(graded), '| 카드전용:', len(items) - len(graded))
    print('cat    :', Counter(x['cat'] for x in items))
    print('lawKey :', Counter(x['lawKey'] for x in items).most_common(12))
    print('조항 없음:', [x['no'] for x in items if not x['law']])
    print('질의 이상(너무 짧거나 긴 것):',
          [x['no'] for x in items if not (8 <= len(x['q']) <= 160)])
    print('wrote', OUT)


if __name__ == '__main__':
    main()
