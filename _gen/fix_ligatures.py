#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 추출로 깨진 합자와 쪼개진 단어를 고친다 (QA W-04).

무엇이 깨졌나
    표준 문서 PDF 에서 텍스트를 뽑으면 합자(ligature)가 엉뚱한 글자로 바뀐다.
        fi -> 9      de9ned, identi9er, speci9ed
        fi -> %      unde%ned, unspeci%ed, quali%ed
        fl -> 8      con8ict, over8ow
    또 자간 처리 때문에 단어 안에 공백이 들어가기도 한다 (unused ta g).

왜 조심해야 하나
    같은 패턴이 정상적인 코드에도 나온다.
        uint8_t u8a = 1.0f;      <- MISRA 예제의 변수 이름. 고치면 안 된다.
        0x9e3779b9               <- 16진 상수
    그래서 기계적으로 치환하지 않고, **고친 결과가 실제로 이 저장소 안에서
    쓰이는 단어일 때만** 바꾼다. 판단 근거를 코퍼스 자신에게서 가져오는 방식이다.

사용법
    python _gen/fix_ligatures.py --dry     # 무엇을 고칠지만 출력
    python _gen/fix_ligatures.py           # 실제로 고침
"""

import io
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(os.path.dirname(HERE), 'public')

# 합자 복원 후보. 어떤 글자로 깨지는지는 원본 PDF 의 글꼴마다 다르므로
# 한 기호에 여러 후보를 둔다. 맞는 것은 아래 코퍼스 검증이 골라 준다.
SUBS = [('9', 'fi'), ('8', 'fl'), ('%', 'fi'), ('%', 'ff'), ('%', 'ffi'), ('8', 'ffl')]


# ---------------------------------------------------------------------------
# 쪼개진 단어. 자동 탐지 결과를 사람이 한 건씩 확인해 확정한 목록이다.
#
# 왜 목록으로 두는가
#   "size of", "can not", "wake up", "any way", "name space" 처럼 띄어 쓰는 것이
#   맞는 표현이 같은 패턴으로 걸린다. 기계가 가릴 수 없어서 확인한 것만 적었다.
#
# 아래는 확인 후 **일부러 뺀** 것들이다. 붙이면 오히려 틀린다.
#   prepared statement   영어로는 띄어 쓰는 것이 맞다 (코드의 PreparedStatement 와 별개)
#   pseudo random        둘 다 통용된다. 깨진 것이 아니다
#   non existent         하이픈, 붙임 모두 통용. 표기 취향이지 결함이 아니다
#   multi threaded       같은 이유
SPLITS = [
    # 'identifi er s' 를 'identifi er' 보다 먼저 둔다. 순서가 바뀌면 'identifier s' 가 남는다.
    ('identifi er s', 'identifiers'),   # 정상 표기 identifiers 73회
    ('identifi er', 'identifier'),      # 정상 표기 identifier 150회
    ('defi ne', 'define'),              # 정상 표기 define 230회
    ('qualifi ed', 'qualified'),        # 정상 표기 qualified 47회
    ('T rigraphs', 'Trigraphs'),
    ('T echnical', 'Technical'),
    ('T raceability', 'Traceability'),
    ('T rivially', 'Trivially'),
    ('T rivial', 'Trivial'),
    ('T ransferring', 'Transferring'),
    ('T esting', 'Testing'),
    ('T emplates', 'Templates'),
    ('T emplate', 'Template'),
    ('T agged', 'Tagged'),
    ('T ypes', 'Types'),
    ('l abel', 'label'),
    ('c omposite', 'composite'),
    ('u sual', 'usual'),
    ('con stant', 'constant'),
    ('cha racters', 'characters'),
    ('fol lowing', 'following'),
    ('cov ers', 'covers'),
    ('condi tion', 'condition'),
    ('ad dressed', 'addressed'),
    ('cast ing', 'casting'),
    ('pointe r', 'pointer'),
    ('fi elds', 'fields'),
    ('fi eld', 'field'),
    ('pr eprocessing', 'preprocessing'),
    ('Undecida ble', 'Undecidable'),
    ('n ot', 'not'),
]

# 코드 문맥은 건드리지 않는다. 변수명과 상수가 여기 산다.
CODE_BLOCK = re.compile(r'<(pre|code|script|style)\b[^>]*>.*?</\1>', re.S | re.I)

WORD = re.compile(r'[A-Za-z][A-Za-z0-9%\-]*[A-Za-z]')
SUSPECT = re.compile(r'[A-Za-z][98%][A-Za-z]')


def targets():
    out = []
    for name in sorted(os.listdir(PUB)):
        if name.endswith('.html'):
            out.append(name)
    for sub in ('data', 'js'):
        d = os.path.join(PUB, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(('.json', '.js')):
                out.append(os.path.join(sub, name))
    return out


def read(rel):
    with io.open(os.path.join(PUB, rel), encoding='utf-8', errors='replace') as f:
        return f.read()


def prose_of(doc):
    """코드 블록과 태그를 걷어낸 본문 텍스트."""
    body = CODE_BLOCK.sub(' ', doc)
    return re.sub(r'<[^>]+>', ' ', body)


def build_vocabulary(docs):
    """저장소 전체에서 정상적으로 쓰인 영어 단어를 모은다.
    복원 결과가 이 안에 있을 때만 고친다."""
    vocab = Counter()
    for doc in docs.values():
        for w in WORD.findall(prose_of(doc)):
            if SUSPECT.search(w):
                continue
            vocab[w.lower()] += 1
    return vocab


def candidates(word):
    """de9ned -> {defined}, unde%ned -> {undefined} 처럼 복원 후보를 만든다."""
    outs = {word}
    for _ in range(3):                       # 한 단어에 깨짐이 여러 번일 수 있다
        nxt = set()
        for w in outs:
            for ch, rep in SUBS:
                if ch in w:
                    nxt.add(w.replace(ch, rep, 1))
        if not nxt:
            break
        outs |= nxt
    outs.discard(word)
    return outs


def main():
    dry = '--dry' in sys.argv
    rels = targets()
    docs = {r: read(r) for r in rels}
    vocab = build_vocabulary(docs)

    # 1단계: 어떤 깨진 단어를 어떤 단어로 고칠지 정한다
    mapping = {}
    rejected = Counter()
    for doc in docs.values():
        for w in WORD.findall(prose_of(doc)):
            if not SUSPECT.search(w) or w in mapping:
                continue
            best = None
            for cand in candidates(w):
                n = vocab.get(cand.lower(), 0)
                if n > 0 and (best is None or n > vocab.get(best.lower(), 0)):
                    best = cand
            if best:
                mapping[w] = best
            else:
                rejected[w] += 1

    print('=' * 62)
    print('합자 복원 후보 %d종' % len(mapping))
    print('=' * 62)
    for k in sorted(mapping, key=lambda x: -len(x)):
        print('  %-22s -> %s   (근거: 정상 표기 %d회)'
              % (k, mapping[k], vocab[mapping[k].lower()]))
    if rejected:
        print('\n건드리지 않음 (복원해도 쓰이지 않는 말이라 코드로 판단) %d종' % len(rejected))
        print('  ' + ', '.join(sorted(rejected)[:20]))

    print('\n확인 후 확정한 분리 단어 %d종도 함께 고친다.' % len(SPLITS))
    if not mapping and not SPLITS:
        print('\n고칠 것이 없다.')
        return 0
    if dry:
        print('\n--dry 모드라 파일은 바꾸지 않았다.')
        return 0

    # 2단계: 코드 블록 밖에서만 치환한다.
    # 합자 복원과 쪼개진 단어를 같은 패스에서 처리한다.
    table = dict(mapping)
    for a, b in SPLITS:
        table[a] = b
    pat = re.compile(r'(?<![A-Za-z0-9_])(' +
                     '|'.join(re.escape(k) for k in sorted(table, key=len, reverse=True)) +
                     r')(?![A-Za-z0-9_])')

    changed = 0
    total = 0
    for rel in rels:
        doc = docs[rel]
        pieces = []
        last = 0
        hits = [0]

        def swap(m):
            hits[0] += 1
            return table[m.group(1)]

        # 코드 블록은 그대로 두고, 그 사이 구간만 치환한다
        for m in CODE_BLOCK.finditer(doc):
            pieces.append(pat.sub(swap, doc[last:m.start()]))
            pieces.append(m.group(0))
            last = m.end()
        pieces.append(pat.sub(swap, doc[last:]))
        new = ''.join(pieces)

        if new != doc:
            with io.open(os.path.join(PUB, rel), 'w', encoding='utf-8') as f:
                f.write(new)
            changed += 1
            total += hits[0]
            print('  고침 %-28s %d곳' % (rel, hits[0]))

    print('\n파일 %d개, 총 %d곳 수정' % (changed, total))
    return 0


if __name__ == '__main__':
    sys.exit(main())
