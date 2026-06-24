# -*- coding: utf-8 -*-
"""C/C++ 코딩 표준 레퍼런스 페이지 생성기 → public/coding-standards.html
대상: MISRA C:2012 / MISRA C++:2023 / CERT C / CERT C++ / AUTOSAR C++14
레이아웃: 좌측 고정 사이드바 트리(표준→섹션→규칙) + 전역 KO/EN 토글 + 연습 IDE(Wandbox).
규칙 데이터는 표준별 모듈(std_*.py)의 RULES 에서 임포트.
원문(규범 텍스트) 비복제 — 룰 ID·제목·분류 체계는 인용하되, 설명/예제는 자체 작성.
rule 스키마: {id, cat, title, why, bad, good [, title_en, why_en]}
  - title_en/why_en 없으면 한국어로 폴백(점진 전환 호환).
"""
import html, os, importlib, re
try:
    from std_pdf_overrides import PDF_EXAMPLE_OVERRIDES
except Exception:
    PDF_EXAMPLE_OVERRIDES = {}
try:
    from std_pdf_full_rules import PDF_FULL_RULES
except Exception:
    PDF_FULL_RULES = {}
try:
    from std_cert_sei_rules import SEI_CERT_RULES
except Exception:
    SEI_CERT_RULES = {}

OUT = os.path.join(os.path.dirname(__file__), '..', 'public')


def esc(s):
    return html.escape(s or '', quote=False)


def _rules(mod):
    return importlib.import_module(mod).RULES


def apply_pdf_overrides(std_key, rules):
    """Apply locally extracted MISRA PDF examples over existing rule data."""
    overrides = PDF_EXAMPLE_OVERRIDES.get(std_key, {})
    if not overrides:
        return rules
    out = []
    for rule in rules:
        r = dict(rule)
        o = overrides.get(r.get('id'))
        if o:
            if o.get('bad'):
                r['bad'] = o['bad']
            if o.get('good'):
                r['good'] = o['good']
            r['pdf_example'] = True
            # PDF examples are often focused snippets, not self-contained programs.
            r['compiles'] = False
        out.append(r)
    return out


def merge_pdf_full_rules(std_key, rules):
    """Use the local MISRA PDFs as the canonical rule order/count when available."""
    full = PDF_FULL_RULES.get(std_key, {})
    if not full:
        return rules
    by_id = {r.get('id'): dict(r) for r in rules}
    merged = []
    used = set()
    for pdf_rule in full:
        rid = pdf_rule.get('id')
        if rid in by_id:
            r = by_id[rid]
            r['pdf_rule'] = True
            merged.append(r)
        else:
            merged.append(dict(pdf_rule))
        used.add(rid)
    return merged


def cert_placeholder(lang, gid, title, compliant):
    mark = 'Compliant' if compliant else 'Non-compliant'
    return (
        f"/* {mark} training placeholder for {gid}\n"
        f" * SEI official index entry: {title}\n"
        f" * Add a reviewed {lang} example before using this item as a hands-on lab.\n"
        f" */"
    )


def merge_sei_cert_rules(std_key, rules):
    """Use the SEI public index as canonical for CERT C/C++ guideline coverage."""
    official = SEI_CERT_RULES.get(std_key, [])
    if not official:
        return rules
    by_id = {r.get('id'): dict(r) for r in rules}
    merged = []
    used = set()
    lang = 'C++' if std_key == 'certcpp' else 'C'
    for item in official:
        gid = item.get('id')
        if gid in by_id:
            r = by_id[gid]
            r['sei_rule'] = True
            merged.append(r)
        else:
            section = item.get('section') or (gid[:3] if gid else 'MSC')
            kind = item.get('kind') or 'Rule'
            title = item.get('title') or gid
            is_rec = kind.lower().startswith('rec')
            merged.append({
                'id': gid,
                'cat': section + ' · ' + ('Rec' if is_rec else 'Rule') + ' · SEI',
                'title': title,
                'title_en': item.get('title_en') or title,
                'bad': cert_placeholder(lang, gid, title, False),
                'good': cert_placeholder(lang, gid, title, True),
                'why': f'{gid}는 SEI CERT 공식 공개 인덱스 기준으로 추가한 항목입니다. 현재 항목은 목록 완전성을 위해 먼저 반영했으며, 실습 전 공식 페이지와 정적분석 진단 기준으로 예제를 보강하세요.',
                'why_en': f'{gid} was added from the official public SEI CERT index. It is included for coverage completeness; add reviewed examples against the official page and static-analysis diagnostics before hands-on use.',
                'compiles': False,
                'sei_rule': True,
                'source_url': item.get('source_url', ''),
            })
        used.add(gid)
    return merged


def bi(ko, en):
    """KO/EN 두 언어 span. 전역 토글이 .ko/.en 가시성을 제어한다."""
    return ('<span class="ko">' + esc(ko) + '</span>'
            '<span class="en">' + esc(en or ko) + '</span>')


def hl_markers(code):
    """공식 예제(단일 페인) 안의 // Compliant / // Non-compliant 라인 주석을
    색상 하이라이트해 위반·준수 라인을 한눈에 보이게 한다(블록 분리는 불가하므로 인라인 표시)."""
    lines = []
    for line in code.split('\n'):
        pos = line.find('//')
        if pos < 0:
            lines.append(esc(line))
            continue
        comment = line[pos:]
        cl = comment.lower()
        cls = None
        if 'non-compliant' in cl or 'noncompliant' in cl or 'non compliant' in cl:
            cls = 'mk-bad'
        elif 'compliant' in cl:
            cls = 'mk-good'
        if cls:
            lines.append(esc(line[:pos]) + '<span class="' + cls + '">' + esc(comment) + '</span>')
        else:
            lines.append(esc(line))
    return '\n'.join(lines)


STANDARDS = [
 {'key': 'misrac', 'name': 'MISRA C:2012', 'lang': 'c',
  'full': 'Guidelines for the use of the C language in critical systems',
  'org': 'MISRA Consortium (영국 자동차 SW 신뢰성 협회)', 'org_en': 'MISRA Consortium (UK automotive SW reliability association)',
  'basis': 'C90/C99 (임베디드·안전필수 C)', 'basis_en': 'C90/C99 (embedded, safety-critical C)',
  'classes': ['Directive(Dir) + Rule', 'Mandatory / Required / Advisory', 'Decidable / Undecidable'],
  'classes_en': ['Directive(Dir) + Rule', 'Mandatory / Required / Advisory', 'Decidable / Undecidable'],
  'note': '안전필수 임베디드 C의 사실상 표준. 의무도(Mandatory>Required>Advisory)와 정적분석 결정가능성(Decidable/Undecidable)으로 분류된다.',
  'note_en': 'The de-facto standard for safety-critical embedded C. Guidelines are graded by obligation (Mandatory>Required>Advisory) and static-analysis decidability (Decidable/Undecidable).',
  'mod': 'std_misrac'},
 {'key': 'misracpp', 'name': 'MISRA C++:2023', 'lang': 'cpp',
  'full': 'Guidelines for the use of C++17 in critical systems',
  'org': 'MISRA Consortium', 'org_en': 'MISRA Consortium',
  'basis': 'C++17 (구 MISRA C++:2008 + AUTOSAR C++14 통합)', 'basis_en': 'C++17 (merges MISRA C++:2008 + AUTOSAR C++14)',
  'classes': ['Mandatory / Required / Advisory', 'Decidable / Undecidable', 'Rule 섹션.그룹.번호'],
  'classes_en': ['Mandatory / Required / Advisory', 'Decidable / Undecidable', 'Rule section.group.number'],
  'note': 'AUTOSAR C++14 가이드라인을 흡수해 C++17 기준으로 재편한 최신 표준. 룰 번호는 "Rule 섹션.그룹.번호"(예: Rule 8.2.2).',
  'note_en': 'The latest standard, absorbing AUTOSAR C++14 and re-based on C++17. Rule numbers use the form "Rule section.group.number" (e.g. Rule 8.2.2).',
  'mod': 'std_misracpp'},
 {'key': 'certc', 'name': 'CERT C', 'lang': 'c',
  'full': 'SEI CERT C Coding Standard',
  'org': 'SEI / Carnegie Mellon University', 'org_en': 'SEI / Carnegie Mellon University',
  'basis': '보안 중심 C (취약점 예방)', 'basis_en': 'Security-focused C (vulnerability prevention)',
  'classes': ['Rules / Recommendations', 'Severity × Likelihood × Remediation → Priority', 'Level L1 / L2 / L3'],
  'classes_en': ['Rules / Recommendations', 'Severity × Likelihood × Remediation → Priority', 'Level L1 / L2 / L3'],
  'note': '보안 취약점 예방에 초점을 둔 코딩 표준. 규칙 ID는 "섹션+번호-C"(예: INT30-C). 공식 사이트(cmu-sei.github.io) 대조로 ID 정확성 확인.',
  'note_en': 'A coding standard focused on preventing security vulnerabilities. Rule IDs use "section+number-C" (e.g. INT30-C). IDs verified against the official site (cmu-sei.github.io).',
  'mod': 'std_certc'},
 {'key': 'certcpp', 'name': 'CERT C++', 'lang': 'cpp',
  'full': 'SEI CERT C++ Coding Standard',
  'org': 'SEI / Carnegie Mellon University', 'org_en': 'SEI / Carnegie Mellon University',
  'basis': '보안 중심 C++', 'basis_en': 'Security-focused C++',
  'classes': ['Rules / Recommendations', 'Severity × Likelihood × Remediation', 'Level L1 / L2 / L3'],
  'classes_en': ['Rules / Recommendations', 'Severity × Likelihood × Remediation', 'Level L1 / L2 / L3'],
  'note': 'CERT C의 C++ 판으로, RAII·예외·객체수명 등 C++ 고유 위험을 다룬다. 규칙 ID는 "섹션+번호-CPP"(예: MEM50-CPP).',
  'note_en': 'The C++ edition of CERT C, covering C++-specific hazards such as RAII, exceptions and object lifetime. Rule IDs use "section+number-CPP" (e.g. MEM50-CPP).',
  'mod': 'std_certcpp'},
 {'key': 'autosar', 'name': 'AUTOSAR C++14', 'lang': 'cpp',
  'full': 'Guidelines for the use of C++14 in critical and safety-related systems',
  'org': 'AUTOSAR (자동차 SW 아키텍처 컨소시엄)', 'org_en': 'AUTOSAR (automotive SW architecture consortium)',
  'basis': 'C++14 (Adaptive Platform). MISRA C++:2023에 승계', 'basis_en': 'C++14 (Adaptive Platform); succeeded by MISRA C++:2023',
  'classes': ['Required / Advisory', 'Automated / Non-automated', 'A###(AUTOSAR) / M###(MISRA 유래)'],
  'classes_en': ['Required / Advisory', 'Automated / Non-automated', 'A###(AUTOSAR-original) / M###(MISRA-origin)'],
  'note': '자동차 안전필수 C++14 가이드라인. 규칙 ID는 A0-1-1·M0-1-1 형식(A=AUTOSAR 신규, M=MISRA 유래). 현재 MISRA C++:2023이 승계.',
  'note_en': 'Automotive safety-critical C++14 guidelines. Rule IDs use the A0-1-1 / M0-1-1 form (A=AUTOSAR-original, M=MISRA-origin). Now succeeded by MISRA C++:2023.',
  'mod': 'std_autosar'},
]

# ── 섹션 분류 ──────────────────────────────────────────────
SEC_NAME = {
 # CERT 공통 섹션
 'PRE': ('전처리기', 'Preprocessor'), 'DCL': ('선언·초기화', 'Declarations'),
 'EXP': ('표현식', 'Expressions'), 'INT': ('정수', 'Integers'),
 'FLP': ('부동소수', 'Floating Point'), 'ARR': ('배열', 'Arrays'),
 'STR': ('문자·문자열', 'Strings'), 'MEM': ('메모리 관리', 'Memory'),
 'FIO': ('입출력', 'Input/Output'), 'ENV': ('환경', 'Environment'),
 'SIG': ('시그널', 'Signals'), 'ERR': ('오류 처리', 'Error Handling'),
 'CON': ('동시성', 'Concurrency'), 'API': ('API', 'Application Programming Interfaces'), 'MSC': ('기타', 'Miscellaneous'),
 'POS': ('POSIX', 'POSIX'), 'WIN': ('Windows', 'Windows'),
 'CTR': ('컨테이너', 'Containers'), 'OOP': ('객체지향', 'OOP'),
 # MISRA C 카테고리
 'Dir': ('지침(Directive)', 'Directives'),
 'R1': ('표준 C 환경', 'Standard C environment'), 'R2': ('미사용 코드', 'Unused code'),
 'R3': ('주석', 'Comments'), 'R4': ('문자 집합', 'Character sets'),
 'R5': ('식별자', 'Identifiers'), 'R6': ('타입', 'Types'),
 'R7': ('리터럴·상수', 'Literals & constants'), 'R8': ('선언·정의', 'Declarations & definitions'),
 'R9': ('초기화', 'Initialization'), 'R10': ('essential type 모델', 'Essential type model'),
 'R11': ('포인터 변환', 'Pointer conversions'), 'R12': ('표현식', 'Expressions'),
 'R13': ('부작용', 'Side effects'), 'R14': ('제어문 표현식', 'Control-stmt expressions'),
 'R15': ('제어 흐름', 'Control flow'), 'R16': ('switch 문', 'Switch statements'),
 'R17': ('함수', 'Functions'), 'R18': ('포인터·배열', 'Pointers & arrays'),
 'R19': ('중첩 저장', 'Overlapping storage'), 'R20': ('전처리 지시문', 'Preprocessing directives'),
 'R21': ('표준 라이브러리', 'Standard libraries'), 'R22': ('자원', 'Resources'),
 'R23': ('Generic 선택', 'Generic selections'),
}


def sec_of(key, rid):
    if key in ('certc', 'certcpp'):
        m = re.match(r'^([A-Z]+)', rid)
        return m.group(1) if m else 'MSC'
    if key == 'misrac':
        if rid.startswith('Dir'):
            return 'Dir'
        m = re.match(r'Rule (\d+)', rid)
        return 'R' + m.group(1) if m else 'R0'
    if key == 'misracpp':
        if rid.startswith('Dir'):
            return 'Dir'
        m = re.match(r'Rule (\d+)', rid)
        return 'M' + m.group(1) if m else 'M0'
    if key == 'autosar':
        m = re.match(r'^([AM]\d+)', rid)
        return m.group(1) if m else 'X'
    return 'X'


def sec_label(key, sec):
    if sec in SEC_NAME:
        ko, en = SEC_NAME[sec]
        return ko, en
    if key == 'misracpp' and sec.startswith('M'):
        n = sec[1:]
        return ('섹션 ' + n, 'Section ' + n)
    if key == 'autosar':
        kind = 'AUTOSAR' if sec.startswith('A') else 'MISRA 유래'
        kind_en = 'AUTOSAR-original' if sec.startswith('A') else 'MISRA-origin'
        return (sec + ' (' + kind + ')', sec + ' (' + kind_en + ')')
    return (sec, sec)


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0b1220;--card:#fff;--primary:#0ea5e9;--ink:#1e293b;--muted:#64748b;--border:#e2e8f0;--bad:#ef4444;--good:#22c55e}
body{font-family:'Segoe UI','Malgun Gothic',sans-serif;background:#0f172a;color:var(--ink)}
body:not(.lang-en) .en{display:none}body.lang-en .ko{display:none}
.top{background:#0b1220;padding:9px 18px;display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:50}
.top a{color:#7dd3fc;text-decoration:none;font-size:13px;font-family:'JetBrains Mono',monospace}
.top .sp{margin-left:auto}
.langtog{cursor:pointer;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:999px;padding:5px 12px;font-size:12.5px;font-weight:700;font-family:'JetBrains Mono',monospace}
.langtog b{color:#7dd3fc}
.layout{display:flex;align-items:flex-start;max-width:1320px;margin:0 auto}
/* ── 사이드바 ── */
.side{width:290px;flex:0 0 290px;position:sticky;top:42px;height:calc(100vh - 42px);overflow-y:auto;background:#0b1220;border-right:1px solid #1e293b;padding:12px 10px 40px}
.side .sb{width:100%;padding:9px 11px;border:1px solid #334155;background:#111a2e;color:#e2e8f0;border-radius:9px;font-size:13px;margin-bottom:10px}
.snode{display:flex;align-items:center;gap:6px;cursor:pointer;padding:8px 9px;border-radius:8px;color:#cbd5e1;font-weight:700;font-size:13.5px}
.snode:hover{background:#16223c}.snode.on{background:#1e293b;color:#fff}
.snode .nm{flex:1}.snode .cnt{font-size:11px;color:#64748b;font-family:'JetBrains Mono',monospace}
.snode .tw{font-size:10px;color:#64748b;transition:transform .15s}.snode.open .tw{transform:rotate(90deg)}
.seclist{display:none;margin:2px 0 6px 8px;border-left:1px solid #1e293b;padding-left:6px}
.seclist.show{display:block}
.seclist a{display:flex;gap:6px;align-items:baseline;text-decoration:none;color:#94a3b8;font-size:12.5px;padding:5px 8px;border-radius:6px;cursor:pointer}
.seclist a:hover{background:#16223c;color:#e2e8f0}
.seclist a .sc{font-family:'JetBrains Mono',monospace;font-size:10.5px;color:#7dd3fc}
.seclist a .scnt{margin-left:auto;font-size:10.5px;color:#475569}
/* ── 본문 ── */
.main{flex:1;min-width:0;padding:16px 20px 60px;background:linear-gradient(180deg,#0f172a,#1e3a8a 1400px)}
.hero{color:#fff;padding:8px 4px 16px}.hero h1{font-size:23px;margin-bottom:6px}
.hero p{opacity:.9;font-size:13.5px;max-width:820px;line-height:1.6}
.panel{display:none}.panel.on{display:block}
.ov{background:#fff;border-radius:14px;padding:18px 20px;margin-bottom:14px;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.ov h2{font-size:19px;color:#0c4a6e}.ov .full{color:var(--muted);font-size:12.5px;margin:3px 0 10px;font-style:italic}
.ov .meta{font-size:13px;line-height:1.8}.ov .meta b{color:#0369a1}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 4px}
.chip{background:#f0f9ff;border:1px solid #bae6fd;color:#075985;border-radius:20px;padding:5px 12px;font-size:11.5px;font-weight:600}
.ov .note{margin-top:10px;font-size:13px;line-height:1.7;color:#334155;background:#f8fafc;border-left:4px solid var(--primary);padding:11px 13px;border-radius:8px}
.sech{scroll-margin-top:52px;color:#e2e8f0;font-size:15px;font-weight:800;margin:18px 2px 10px;padding-bottom:6px;border-bottom:1px solid #334155}
.sech .sc{font-family:'JetBrains Mono',monospace;font-size:12px;color:#7dd3fc;margin-right:8px}
.card{background:#fff;border-radius:13px;padding:16px 18px;margin-bottom:12px;box-shadow:0 8px 24px rgba(0,0,0,.14)}
.card .rid{display:flex;flex-wrap:wrap;align-items:center;gap:9px;margin-bottom:5px}
.rid .id{font-family:'JetBrains Mono',monospace;font-weight:700;background:#0b1220;color:#7dd3fc;padding:4px 11px;border-radius:8px;font-size:13px}
.rid .cat{font-size:11px;font-weight:700;color:#7c3aed;background:#f3e8ff;border-radius:20px;padding:3px 10px}
.rid .ok{font-size:10.5px;font-weight:700;color:#15803d;background:#dcfce7;border-radius:20px;padding:3px 9px}
.rid .pdf{font-size:10.5px;font-weight:700;color:#9a3412;background:#ffedd5;border-radius:20px;padding:3px 9px}
.rid .sei{font-size:10.5px;font-weight:700;color:#075985;background:#e0f2fe;border-radius:20px;padding:3px 9px}
.card h3{font-size:15px;color:var(--ink);margin:2px 0 11px;line-height:1.5}
.sw{display:flex;gap:5px;background:#0b1220;border-radius:9px;padding:4px;width:fit-content;margin-bottom:10px;flex-wrap:wrap}
.sw button{border:none;background:transparent;color:#94a3b8;font-weight:700;font-size:12px;padding:7px 13px;border-radius:7px;cursor:pointer;font-family:inherit}
.sw button.on.bad{background:var(--bad);color:#fff}.sw button.on.good{background:var(--good);color:#fff}
.sw button.prac{color:#a5b4fc}.sw button.prac:hover{color:#fff}
.pane{display:none}.pane.show{display:block}
.chdr{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:12px;padding:8px 13px;border-radius:9px 9px 0 0;color:#fff}
.chdr.bad{background:var(--bad)}.chdr.good{background:var(--good)}
pre{background:var(--bg);color:#e2e8f0;padding:14px 15px;border-radius:0 0 9px 9px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:12.5px;line-height:1.6;white-space:pre}
.why{margin-top:11px;background:#fffbeb;border-left:4px solid #f59e0b;border-radius:8px;padding:11px 14px;font-size:13px;line-height:1.7;color:#78350f}
.foot{color:#cbd5e1;font-size:12px;margin-top:18px;line-height:1.7}
/* ── 연습 IDE ── */
.ide{position:fixed;left:0;right:0;bottom:0;height:72vh;background:#0b1220;border-top:2px solid #6366f1;box-shadow:0 -10px 40px rgba(0,0,0,.5);display:none;flex-direction:column;z-index:9999}
.ide.on{display:flex}
.ide-bar{display:flex;align-items:center;gap:8px;padding:8px 12px;background:#111a2e;border-bottom:1px solid #1e293b;flex-wrap:wrap}
.ide-bar .ide-title{color:#c7d2fe;font-weight:700;font-size:13.5px;margin-right:auto}
.ide-bar select,.ide-bar button{font-family:'JetBrains Mono',monospace;font-size:12.5px;font-weight:700;border:none;border-radius:8px;padding:7px 12px;cursor:pointer;background:#1e293b;color:#cbd5e1}
.ide-bar button.run{background:#22c55e;color:#06210f}.ide-bar button.x{background:#334155}
.ide-body{flex:1;display:flex;min-height:0}.ide-ed{flex:1;min-width:0}
.ide-out{width:38%;max-width:460px;display:flex;flex-direction:column;border-left:1px solid #1e293b;background:#0b1220}
.ide-outhdr{padding:7px 12px;font-size:11.5px;font-weight:700;color:#94a3b8;background:#111a2e;border-bottom:1px solid #1e293b}
.ide-out pre{flex:1;margin:0;border-radius:0;white-space:pre-wrap;overflow:auto}
.ide-note{font-size:11px;color:#94a3b8;padding:6px 12px;background:#111a2e;border-top:1px solid #1e293b}
@media(max-width:860px){
 .side{position:fixed;left:0;top:42px;z-index:40;transform:translateX(-100%);transition:transform .2s;box-shadow:6px 0 30px rgba(0,0,0,.5)}
 .side.open{transform:translateX(0)}
 .menubtn{display:inline-block!important}
 .main{padding:14px 13px 60px}.hero h1{font-size:19px}
 .ide{height:84vh}.ide-body{flex-direction:column}.ide-out{width:100%;max-width:none;border-left:none;border-top:1px solid #1e293b;height:34%}
}
.menubtn{display:none;cursor:pointer;border:1px solid #334155;background:#1e293b;color:#e2e8f0;border-radius:8px;padding:5px 11px;font-size:13px}
/* ── 추가 개선: 공식예제 배지·복사·맨위로·검색·접근성 ── */
.rid .off{font-size:10.5px;font-weight:700;color:#334155;background:#e2e8f0;border-radius:20px;padding:3px 9px}
.chdr.off{background:#475569}
.chdr.off b{padding:0 2px}
.mk-bad{color:#fca5a5;font-weight:700}
.mk-good{color:#86efac;font-weight:700}
.pane{position:relative}
.copy{position:absolute;top:6px;right:8px;z-index:2;border:1px solid #334155;background:#1e293b;color:#cbd5e1;border-radius:6px;font-size:11px;font-weight:700;padding:3px 8px;cursor:pointer;opacity:.5;font-family:'JetBrains Mono',monospace}
.copy:hover,.copy:focus-visible{opacity:1;color:#7dd3fc}
.totop{position:fixed;right:16px;bottom:16px;z-index:60;display:none;width:42px;height:42px;border-radius:50%;border:none;background:#0ea5e9;color:#fff;font-size:18px;cursor:pointer;box-shadow:0 6px 18px rgba(0,0,0,.35)}
.totop.on{display:block}
.scount{color:#7dd3fc;font-size:11.5px;font-family:'JetBrains Mono',monospace;padding:0 6px 8px;display:none}
body.searching .scount{display:block}
body.searching .panel{display:block!important}
body.searching .ov{display:none}
.sech.hide,.card.hide{display:none}
.snode:focus-visible,.langtog:focus-visible,.seclist a:focus-visible,.menubtn:focus-visible{outline:2px solid #7dd3fc;outline-offset:2px}
"""


def render_card(sk, i, r, lang):
    cid = sk + str(i)
    title_en = r.get('title_en') or r['title']
    why_en = r.get('why_en') or r['why']
    blob = esc(r['id'] + ' ' + r['title'] + ' ' + title_en + ' ' + r.get('cat', ''))
    okbadge = '<span class="ok">✓ compilable</span>' if r.get('compiles') else ''
    if r.get('sei_rule'):
        okbadge += '<span class="sei">SEI index</span>'
    if r.get('pdf_rule') and not r.get('pdf_example'):
        okbadge += '<span class="pdf rule">PDF rule</span>'
    if r.get('pdf_example'):
        okbadge += '<span class="pdf">PDF example</span>'
    head = (
      '<div class="card" data-s="' + blob + '">'
      '<div class="rid"><span class="id">' + esc(r['id']) + '</span><span class="cat">' + esc(r['cat']) + '</span>' + okbadge)
    prac = ('<button class="prac" onclick="practice(\'' + cid + '\',\'' + lang + '\')">🧪 '
            '<span class="ko">IDE에서 연습</span><span class="en">Practice in IDE</span></button>')
    if r.get('single'):
        # 공식 추출 예제(위반·준수 주석 포함) — 단일 페인
        return (
          head + '<span class="off">📄 <span class="ko">공식 예제</span><span class="en">Official example</span></span></div>'
          '<h3>' + bi(r['title'], title_en) + '</h3>'
          '<div class="sw">' + prac + '</div>'
          '<div class="pane show" id="' + cid + 'b"><div class="chdr off">📄 '
          '<span class="ko">공식 예제 — <b class="mk-bad">// Non-compliant</b> 위반 · <b class="mk-good">// Compliant</b> 준수 라인</span>'
          '<span class="en">Official example — <b class="mk-bad">// Non-compliant</b> vs <b class="mk-good">// Compliant</b> lines</span></div>'
          '<pre>' + hl_markers(r['bad']) + '</pre></div>'
          '<div class="why">⚠️ ' + bi(r['why'], why_en) + '</div>'
          '</div>')
    return (
      head + '</div>'
      '<h3>' + bi(r['title'], title_en) + '</h3>'
      '<div class="sw"><button class="on bad" onclick="sw(\'' + cid + '\',0)">❌ <span class="ko">위반</span><span class="en">Non-compliant</span></button>'
      '<button class="good" onclick="sw(\'' + cid + '\',1)">✅ <span class="ko">준수</span><span class="en">Compliant</span></button>'
      + prac + '</div>'
      '<div class="pane show" id="' + cid + 'b"><div class="chdr bad">❌ <span class="ko">위반 예시</span><span class="en">Non-compliant example</span></div><pre>' + esc(r['bad']) + '</pre></div>'
      '<div class="pane" id="' + cid + 'g"><div class="chdr good">✅ <span class="ko">준수 예시</span><span class="en">Compliant example</span></div><pre>' + esc(r['good']) + '</pre></div>'
      '<div class="why">⚠️ ' + bi(r['why'], why_en) + '</div>'
      '</div>')


def grouped(s):
    """규칙을 섹션별로 그룹화(등장 순서 보존). [(sec,[(idx,rule),...]),...]"""
    order = []
    buckets = {}
    for i, r in enumerate(s['rules']):
        sec = sec_of(s['key'], r['id'])
        if sec not in buckets:
            buckets[sec] = []
            order.append(sec)
        buckets[sec].append((i, r))
    return [(sec, buckets[sec]) for sec in order]


def render_panel(s, active):
    chips = ''.join('<span class="chip">' + bi(s['classes'][k], s['classes_en'][k]) + '</span>'
                    for k in range(len(s['classes'])))
    body = ''
    for sec, items in grouped(s):
        ko, en = sec_label(s['key'], sec)
        body += ('<h2 class="sech" id="sec-' + s['key'] + '-' + sec + '"><span class="sc">' + esc(sec) + '</span>'
                 + bi(ko, en) + '</h2>')
        body += ''.join(render_card(s['key'], i, r, s['lang']) for i, r in items)
    return (
      '<div class="panel' + (' on' if active else '') + '" id="p-' + s['key'] + '">'
      '<div class="ov"><h2>' + esc(s['name']) + '</h2><div class="full">' + esc(s['full']) + '</div>'
      '<div class="meta"><b><span class="ko">제정/관리</span><span class="en">Maintained by</span>:</b> '
      + bi(s['org'], s.get('org_en')) + '<br><b><span class="ko">대상</span><span class="en">Basis</span>:</b> '
      + bi(s['basis'], s.get('basis_en')) + '</div>'
      '<div class="chips">' + chips + '</div>'
      '<div class="note">' + bi(s['note'], s.get('note_en')) + '</div></div>'
      + body + '</div>')


def render_side():
    out = ('<input class="sb" type="search" aria-label="search rules by id or title" '
           'placeholder="🔎 search id / title (all standards)…" oninput="gsearch(this.value)">'
           '<div class="scount" id="scount"></div>')
    for idx, s in enumerate(STANDARDS):
        secs = grouped(s)
        out += ('<div class="snode' + (' on open' if idx == 0 else '') + '" id="sn-' + s['key'] + '"'
                ' role="button" tabindex="0" aria-label="' + esc(s['name']) + '"'
                ' onclick="selStd(\'' + s['key'] + '\')" onkeydown="kd(event)">'
                '<span class="tw">▶</span><span class="nm">' + esc(s['name']) + '</span>'
                '<span class="cnt">' + str(len(s['rules'])) + '</span></div>')
        links = ''
        for sec, items in secs:
            ko, en = sec_label(s['key'], sec)
            links += ('<a role="link" tabindex="0" onkeydown="kd(event)" onclick="goSec(\'' + s['key'] + '\',\'' + sec + '\')"><span class="sc">' + esc(sec) + '</span>'
                      + bi(ko, en) + '<span class="scnt">' + str(len(items)) + '</span></a>')
        out += '<div class="seclist' + (' show' if idx == 0 else '') + '" id="sl-' + s['key'] + '">' + links + '</div>'
    return out


def _clean_rules(rules):
    """불완전한 룰 제거 + 위반/준수가 동일한 (공식 추출) 룰은 single 플래그.
    AUTOSAR 공식 예제는 한 파일에 위반·준수 주석이 함께 있어 bad==good 이 되므로,
    의미 없는 토글 대신 단일 '공식 예제' 페인으로 렌더하도록 표시한다."""
    out = []
    for r in rules:
        if not (r.get('bad') and r.get('good') and r.get('why') and r.get('title')):
            continue  # 빈/불완전 룰 제외
        if r['bad'] == r['good']:
            r = dict(r)
            r['single'] = True
        out.append(r)
    return out


def build():
    for s in STANDARDS:
        base_rules = merge_pdf_full_rules(s['key'], _rules(s['mod']))
        base_rules = merge_sei_cert_rules(s['key'], base_rules)
        s['rules'] = _clean_rules(apply_pdf_overrides(s['key'], base_rules))
    panels = ''.join(render_panel(s, i == 0) for i, s in enumerate(STANDARDS))
    total = sum(len(s['rules']) for s in STANDARDS)
    side = render_side()
    counts = ' · '.join(s['name'] + ' ' + str(len(s['rules'])) for s in STANDARDS)
    html_doc = (
      '<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">'
      '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
      '<meta name="description" content="MISRA C:2012 / MISRA C++:2023 / CERT C / CERT C++ / AUTOSAR C++14 coding-standard rules with non-compliant vs compliant examples and a live Wandbox practice IDE. KO/EN.">'
      '<title>C/C++ 코딩 표준 — MISRA · CERT · AUTOSAR</title>'
      '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">'
      '<style>' + CSS + '</style></head><body>'
      '<div class="top"><span class="menubtn" onclick="toggleSide()">☰</span>'
      '<a href="index.html">← <span class="ko">홈</span><span class="en">Home</span></a> '
      '<a href="vuln-hub.html"><span class="ko">취약점 학습 허브</span><span class="en">Vuln Hub</span></a>'
      '<span class="sp"></span>'
      '<span class="langtog" role="button" tabindex="0" aria-label="toggle language" onclick="toggleLang()" onkeydown="kd(event)"><b class="ko">한국어</b><b class="en">English</b>'
      ' <span class="ko">→ EN</span><span class="en">→ 한</span></span></div>'
      '<div class="layout"><div class="side" id="side">' + side + '</div>'
      '<div class="main">'
      '<div class="hero"><h1>🛠️ <span class="ko">C/C++ 코딩 표준 레퍼런스</span><span class="en">C/C++ Coding Standards Reference</span></h1>'
      '<p><span class="ko">임베디드·안전필수·보안 C/C++ 5대 코딩 표준의 분류 체계와 규칙을 위반/준수 예제로 비교합니다. 좌측 트리로 표준→섹션을 탐색하고, 🧪 버튼으로 코드를 직접 실행해 보세요.</span>'
      '<span class="en">Compare the five major embedded/safety-critical/security C/C++ coding standards rule-by-rule with non-compliant vs compliant examples. Navigate standard→section in the left tree, and run code live with the 🧪 button.</span></p></div>'
      + panels +
      '<div class="foot">' + esc(counts) + ' &nbsp;|&nbsp; <span class="ko">대표 규칙</span><span class="en">rules</span> ' + str(total) + ' · '
      '<span class="ko">사내 교육용. MISRA C:2012 / MISRA C++:2023의 매칭 가능한 예제 코드는 로컬 PDF에서 추출해 반영했고, 나머지 표준·미매칭 룰은 기존 교육용 예제를 유지합니다.</span>'
      '<span class="en">Internal training. Matched MISRA C:2012 / MISRA C++:2023 examples are extracted from the local PDFs; other standards and unmatched rules keep the existing training examples.</span></div></div></div>'
      # ── 연습 IDE ──
      '<div class="ide" id="ide"><div class="ide-bar"><span class="ide-title">🧪 <span class="ko">연습 IDE</span><span class="en">Practice IDE</span></span>'
      '<select id="ideLang" onchange="setLang(this.value)"><option value="c">C</option><option value="cpp">C++</option></select>'
      '<button onclick="wrapMain()"><span class="ko">main 스캐폴드</span><span class="en">main scaffold</span></button>'
      '<button onclick="resetIde()"><span class="ko">예제 다시</span><span class="en">reset</span></button>'
      '<button class="run" onclick="runCode()">▶ <span class="ko">실행</span><span class="en">Run</span></button>'
      '<button class="x" onclick="closeIde()">✕</button></div>'
      '<div class="ide-body"><div class="ide-ed" id="ideEd"></div>'
      '<div class="ide-out"><div class="ide-outhdr"><span class="ko">실행 결과 (Wandbox 원격 gcc)</span><span class="en">Output (Wandbox remote gcc)</span></div><pre id="ideOut">▶</pre></div></div>'
      '<div class="ide-note"><span class="ko">⚠️ 예시는 규칙 설명용입니다. \'main 스캐폴드\'로 골격을 감싸 실행하세요.</span>'
      '<span class="en">⚠️ Examples illustrate the rule. Use \'main scaffold\' to wrap a runnable skeleton.</span></div></div>'
      '<button class="totop" id="totop" onclick="window.scrollTo({top:0,behavior:\'smooth\'})" aria-label="back to top">↑</button>'
      '<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js"></script>'
      '<script>'
      # 언어 선택은 사이트 전역(wvs_lang)과 공유 — 다른 페이지에서 EN 선택 시 이어짐. ?lang= 파라미터도 지원.
      'function curLangPref(){try{var p=new URLSearchParams(location.search).get("lang");if(p)return p;return localStorage.getItem("wvs_lang")||localStorage.getItem("lang")||localStorage.getItem("std_lang")||"ko";}catch(e){return "ko";}}'
      'function toggleLang(){var en=!document.body.classList.contains("lang-en");document.body.classList.toggle("lang-en",en);var v=en?"en":"ko";try{localStorage.setItem("wvs_lang",v);localStorage.setItem("lang",v);localStorage.setItem("std_lang",v);}catch(e){}}'
      'document.body.classList.toggle("lang-en",curLangPref()==="en");'
      'function toggleSide(){document.getElementById("side").classList.toggle("open");}'
      'function selStd(k){document.querySelectorAll(".panel").forEach(p=>p.classList.toggle("on",p.id==="p-"+k));'
      'document.querySelectorAll(".snode").forEach(n=>{var on=n.id==="sn-"+k;n.classList.toggle("on",on);n.classList.toggle("open",on);});'
      'document.querySelectorAll(".seclist").forEach(l=>l.classList.toggle("show",l.id==="sl-"+k));'
      'try{history.replaceState(null,"","#"+k);}catch(e){}window.scrollTo(0,0);}'
      'function goSec(k,sec){selStd(k);var el=document.getElementById("sec-"+k+"-"+sec);if(el)el.scrollIntoView({behavior:"smooth",block:"start"});'
      'try{history.replaceState(null,"","#sec-"+k+"-"+sec);}catch(e){}'
      'document.getElementById("side").classList.remove("open");}'
      'function kd(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();e.currentTarget.click();}}'
      'function sw(id,good){document.getElementById(id+"b").classList.toggle("show",!good);'
      'document.getElementById(id+"g").classList.toggle("show",!!good);'
      'var bt=event.currentTarget.parentNode.children;bt[0].classList.toggle("on",!good);bt[1].classList.toggle("on",!!good);}'
      # 전역 검색 — 모든 표준을 가로질러 검색하고 일치 카드만 노출, 빈 섹션은 숨김.
      'function gsearch(q){q=q.trim().toLowerCase();var sc=document.getElementById("scount");'
      'if(!q){document.body.classList.remove("searching");document.querySelectorAll(".card.hide,.sech.hide").forEach(function(e){e.classList.remove("hide");});sc.textContent="";return;}'
      'document.body.classList.add("searching");var total=0;'
      'document.querySelectorAll(".panel").forEach(function(p){'
      'p.querySelectorAll(".card").forEach(function(c){var hit=(c.getAttribute("data-s")||"").toLowerCase().indexOf(q)>=0;c.classList.toggle("hide",!hit);if(hit)total++;});'
      'p.querySelectorAll(".sech").forEach(function(h){var n=h.nextElementSibling,any=false;while(n&&n.classList.contains("card")){if(!n.classList.contains("hide")){any=true;break;}n=n.nextElementSibling;}h.classList.toggle("hide",!any);});});'
      'sc.textContent=total+" match"+(total===1?"":"es");}'
      # IDE
      'var ed=null,curLang="c",seed="";'
      'function ensureMonaco(cb){if(window.monaco&&ed){cb();return;}'
      'require.config({paths:{vs:"https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"}});'
      'require(["vs/editor/editor.main"],function(){if(!ed){ed=monaco.editor.create(document.getElementById("ideEd"),'
      '{value:"",language:"cpp",theme:"vs-dark",fontSize:13,minimap:{enabled:false},automaticLayout:true,scrollBeyondLastLine:false});}cb();});}'
      'function practice(cid,lang){var pre=document.querySelector("#"+cid+"g pre")||document.querySelector("#"+cid+"b pre");'
      'seed=pre?pre.textContent:"";curLang=lang;document.getElementById("ideLang").value=lang;'
      'document.getElementById("ide").classList.add("on");document.getElementById("ideOut").textContent="▶";'
      'ensureMonaco(function(){monaco.editor.setModelLanguage(ed.getModel(),lang==="c"?"c":"cpp");ed.setValue(seed);ed.layout();});}'
      'function setLang(v){curLang=v;if(ed)monaco.editor.setModelLanguage(ed.getModel(),v==="c"?"c":"cpp");}'
      'function resetIde(){if(ed)ed.setValue(seed);}'
      'function closeIde(){document.getElementById("ide").classList.remove("on");}'
      'function wrapMain(){if(!ed)return;var c=ed.getValue();if(c.indexOf("int main")>=0)return;'
      'var inc=curLang==="c"?"#include <stdio.h>\\n#include <stdlib.h>\\n#include <string.h>\\n":'
      '"#include <iostream>\\n#include <vector>\\n#include <string>\\n#include <memory>\\nusing namespace std;\\n";'
      'ed.setValue(inc+"\\n"+c+"\\n\\nint main(void){\\n    // TODO\\n    return 0;\\n}\\n");}'
      'function runCode(){if(!ed){return;}var code=ed.getValue();var comp=curLang==="c"?"gcc-13.2.0-c":"gcc-13.2.0";'
      'var opt=curLang==="c"?"-std=gnu11\\n-lm\\n-pthread":"-std=gnu++17\\n-pthread";'
      'var out=document.getElementById("ideOut");out.textContent="⏳ Wandbox...";'
      'fetch("https://wandbox.org/api/compile.json",{method:"POST",headers:{"Content-Type":"application/json"},'
      'body:JSON.stringify({code:code,compiler:comp,options:"warning","compiler-option-raw":opt,stdin:""})})'
      '.then(r=>r.json()).then(function(j){var t="";if(j.compiler_error)t+="[compile]\\n"+j.compiler_error+"\\n";'
      'if(j.program_output)t+=j.program_output;if(j.program_error)t+="\\n[stderr]\\n"+j.program_error;'
      'out.textContent=t.trim()||"(no output · status "+(j.status||"?")+")";})'
      '.catch(function(e){out.textContent="🚫 "+e;});}'
      # 코드 복사 버튼 주입
      'document.querySelectorAll(".pane pre").forEach(function(pre){var b=document.createElement("button");b.className="copy";b.type="button";b.textContent="copy";b.setAttribute("aria-label","copy code");b.onclick=function(ev){ev.stopPropagation();if(navigator.clipboard)navigator.clipboard.writeText(pre.textContent);var o=b.textContent;b.textContent="✓";setTimeout(function(){b.textContent=o;},1200);};pre.parentNode.appendChild(b);});'
      # 맨 위로 버튼
      'var _tt=document.getElementById("totop");if(_tt)window.addEventListener("scroll",function(){_tt.classList.toggle("on",window.scrollY>500);},{passive:true});'
      # 로드 시 해시 라우팅(#표준 / #sec-표준-섹션) — 딥링크/공유 지원
      '(function(){var h=decodeURIComponent((location.hash||"").replace(/^#/,""));if(!h)return;if(h.indexOf("sec-")===0){var m=h.match(/^sec-([a-z]+)-(.+)$/);if(m){goSec(m[1],m[2]);return;}}if(["misrac","misracpp","certc","certcpp","autosar"].indexOf(h)>=0)selStd(h);})();'
      '</script></body></html>')
    open(os.path.join(OUT, 'coding-standards.html'), 'w', encoding='utf-8').write(html_doc)
    print('wrote coding-standards.html | standards=%d rules=%d' % (len(STANDARDS), total))


if __name__ == '__main__':
    build()
