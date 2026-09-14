# -*- coding: utf-8 -*-
"""배포 전 검증 게이트 (QA F-01)

왜 필요한가
    이 저장소의 결함 상당수는 "생성기가 만든 산출물을 아무도 검사하지 않는다"는
    하나의 원인에서 나왔다.
      - inject_progress.py 가 첫 번째 </body> 를 치환하다가 자바스크립트 문자열 안에
        </script> 를 박아 페이지 6개를 망가뜨렸다(QA N-05, I-04).
      - 존재하지 않는 login.html 로 가는 링크가 남았다(QA N-11).
      - 파일명 규칙(sim_ vs sim-) 때문에 진도 엔진이 빠진 페이지가 있었다(QA N-12).
      - 화면 표기 수치와 실제 콘텐츠 수가 달랐다(QA I-11).
      - 개발용 백도어가 프로덕션에 남았다(QA N-01).
    모두 기계로 잡을 수 있는 것들이다.

사용법
    python _gen/validate_build.py            # 검사만
    python _gen/validate_build.py --strict   # 경고도 실패로 처리

    배포 스크립트에서 이 검사가 통과해야 firebase deploy 로 넘어가도록 연결한다.
"""
import json
import os
import posixpath
import re
import sys

PUB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public'))

errors = []
warnings = []


def err(code, msg):
    errors.append('[%s] %s' % (code, msg))


def warn(code, msg):
    warnings.append('[%s] %s' % (code, msg))


def html_files():
    return sorted(f for f in os.listdir(PUB) if f.endswith('.html'))


def read(name):
    with open(os.path.join(PUB, name), encoding='utf-8', errors='replace') as f:
        return f.read()


# ------------------------------------------------------------------ #
# 1. 스크립트 블록 균형 (QA N-05)
# ------------------------------------------------------------------ #
def check_script_blocks():
    """HTML 파서와 같은 방식으로 <script> 블록을 훑어, 블록 밖으로 새어나온
    자바스크립트 소스가 있는지 본다. 문자열 리터럴 안의 </script> 가 블록을
    조기에 끝내면 그 뒤의 코드가 본문 텍스트로 노출된다."""
    js_token = re.compile(
        r"(function\s*\w*\s*\([^)]*\)\s*\{|\bvar\s+\w+\s*=\s*|\breturn\s+\w+\(|if\s*\(path===)")
    for name in html_files():
        s = read(name)
        segs, pos, unclosed = [], 0, False
        while True:
            m = re.search(r'<script\b[^>]*>', s[pos:])
            if not m:
                segs.append(s[pos:])
                break
            segs.append(s[pos:pos + m.start()])
            st = pos + m.end()
            e = s.find('</script>', st)
            if e < 0:
                unclosed = True
                break
            pos = e + 9
        if unclosed:
            err('SCRIPT-UNCLOSED', '%s: 닫히지 않은 <script> 블록이 있다' % name)
            continue
        outside = ''.join(segs)
        # 화면에 보여 주는 코드 예제는 자바스크립트처럼 보이는 것이 정상이다.
        for block in (r'<style[\s\S]*?</style>', r'<pre[\s\S]*?</pre>',
                      r'<code[\s\S]*?</code>', r'<textarea[\s\S]*?</textarea>'):
            outside = re.sub(block, '', outside)
        text = re.sub(r'<[^>]+>', ' ', outside)
        hits = len(js_token.findall(text))
        if hits > 5:
            err('SCRIPT-LEAK',
                '%s: 자바스크립트 소스가 본문 텍스트로 노출된 것으로 보인다(신호 %d개). '
                '문자열 안의 </script> 를 <\\/script> 로 이스케이프했는지 확인한다.' % (name, hits))


# ------------------------------------------------------------------ #
# 2. 주입 태그 위치 (QA N-05 재발 방지)
# ------------------------------------------------------------------ #
INJECTED = [
    '<script src="/js/progress.js" defer></script>',
    '<script src="/js/vuln-anim.js" defer></script>',
    '<script src="/js/shell.js" defer></script>',
    '<script src="/js/boot-guard.js" defer></script>',
]


def check_injected_tags():
    for name in html_files():
        s = read(name)
        last = s.rfind('</body>')
        if last < 0:
            warn('NO-BODY', '%s: </body> 가 없다' % name)
            continue
        # 파서 기준으로 각 <script> 블록의 내부 구간을 구한다.
        spans, pos = [], 0
        while True:
            m = re.search(r'<script\b[^>]*>', s[pos:])
            if not m:
                break
            st = pos + m.end()
            e = s.find('</script>', st)
            if e < 0:
                break
            spans.append((st, e))
            pos = e + 9
        for tag in INJECTED:
            for m in re.finditer(re.escape(tag), s):
                inside = any(a <= m.start() < b for a, b in spans)
                if inside:
                    err('INJECT-MISPLACED',
                        '%s: 주입 태그가 <script> 블록 내부(%d)에 있다. '
                        '자바스크립트 문자열 안에 삽입돼 블록이 조기에 닫힌다.' % (name, m.start()))


# ------------------------------------------------------------------ #
# 3. 내부 링크 무결성 (QA N-11, I-11)
# ------------------------------------------------------------------ #
def check_links():
    existing = set(os.listdir(PUB))
    for name in html_files():
        s = read(name)
        for m in re.finditer(r'href="(?!https?:|mailto:|#|data:)([^"#?]+\.html)"', s):
            target = normalize_link(m.group(1))
            if target is None:
                continue
            if target not in existing:
                err('DEAD-LINK', '%s -> %s (대상 파일 없음)' % (name, m.group(1)))


def normalize_link(href):
    """href 를 public 기준 파일명으로 바꾼다. 못 정하면 None(검사 제외).

    예전에는 lstrip('/') 만 해서 './page.html' 이 그대로 남아 실제로 존재하는
    파일을 '없음'으로 보고했다. 게이트가 헛경보를 내면 진짜 경고까지 무시하게 된다.
    하위 디렉터리나 public 밖으로 나가는 경로는 이 검사의 대상이 아니므로 건너뛴다.
    """
    p = posixpath.normpath(href.lstrip('/'))
    if p.startswith('..'):
        return None          # public 밖 — 여기서 판단하지 않는다
    if '/' in p:
        return None          # 하위 디렉터리 페이지는 목록(os.listdir)에 없다
    return p


# ------------------------------------------------------------------ #
# 4. 개발용 백도어와 잔재 (QA N-01, N-08)
# ------------------------------------------------------------------ #
BACKDOOR = [
    (r'window\.force\w*\s*=', '전역 강제 해제 함수'),
    (r'function\s+\w*ForDev\b', '개발 전용 함수'),
    (r'\bskipAuth\b|\bbypassAuth\b', '인증 우회 플래그'),
]
LEFTOVER_FILES = ['sim-test.html', 'config.js']


def check_backdoors():
    for name in html_files():
        s = read(name)
        for pat, label in BACKDOOR:
            for m in re.finditer(pat, s):
                # 주석 안의 언급은 허용한다
                line_start = s.rfind('\n', 0, m.start()) + 1
                line = s[line_start:s.find('\n', m.start())]
                if line.strip().startswith(('//', '*', '/*')):
                    continue
                err('BACKDOOR', '%s: %s 가 배포본에 남아 있다 (%s)' % (name, label, m.group(0)[:40]))
    for f in LEFTOVER_FILES:
        if os.path.exists(os.path.join(PUB, f)):
            err('LEFTOVER', '%s: 개발 잔재 파일이 남아 있다' % f)


# ------------------------------------------------------------------ #
# 5. 텍스트 품질 (QA I-09)
# ------------------------------------------------------------------ #
LIGATURE = re.compile(r'\b([A-Za-z]+(?:fi|fl|ff)) ([a-z]{2,})\b')


def check_text_quality():
    # 자기 검증형 판정: "defi ne" 은 같은 문서 어딘가에 "define" 이 붙어서도 나온다.
    # 반면 "off the", "diff comparison" 처럼 원래 두 단어인 경우는 붙인 형태가 없다.
    for name in html_files():
        s = read(name)
        low = s.lower()
        bad = set()
        for a, b in LIGATURE.findall(s):
            joined = (a + b).lower()
            if len(joined) >= 6 and joined in low:
                bad.add(a + ' ' + b)
        if bad:
            err('LIGATURE', '%s: PDF 합자 분할로 보이는 단어 %s' % (name, sorted(bad)[:6]))
        if 'PDF 원문에서' in s:
            warn('INTERNAL-NOTE', '%s: 제작 공정을 설명하는 내부 메모가 노출돼 있다' % name)

        # 합자가 숫자나 기호로 바뀐 경우 (QA W-04).
        # fi -> 9, fi -> %, fl -> 8. 코드에도 같은 모양이 나오므로
        # 복원한 결과가 같은 문서 안에서 정상 표기로도 쓰일 때만 실패로 본다.
        prose = re.sub(r'<(pre|code|script|style)\b[^>]*>.*?</\1>', ' ', s,
                       flags=re.S | re.I)
        prose = re.sub(r'<[^>]+>', ' ', prose)
        broken = set()
        for w in re.findall(r'[A-Za-z][A-Za-z0-9%\-]*[A-Za-z]', prose):
            if not re.search(r'[A-Za-z][98%][A-Za-z]', w):
                continue
            for ch, rep in (('9', 'fi'), ('%', 'fi'), ('8', 'fl'), ('%', 'ff')):
                if ch in w and w.replace(ch, rep).lower() in low:
                    broken.add(w)
                    break
        if broken:
            err('LIGATURE-SYMBOL',
                '%s: 합자가 기호로 깨진 단어 %s. python _gen/fix_ligatures.py 로 고친다.'
                % (name, sorted(broken)[:6]))


# ------------------------------------------------------------------ #
# 6. 접근성 기본 (QA I-08)
# ------------------------------------------------------------------ #
def check_a11y():
    missing_skip, missing_shell = [], []
    for name in html_files():
        s = read(name)
        if 'class="wvs-skip"' not in s:
            missing_skip.append(name)
        if '/js/shell.js' not in s:
            missing_shell.append(name)
    if missing_skip:
        err('A11Y-SKIP', 'skip link 가 없는 페이지 %d개: %s' % (len(missing_skip), missing_skip[:5]))
    if missing_shell:
        err('A11Y-SHELL', '공통 셸이 없는 페이지 %d개: %s' % (len(missing_shell), missing_shell[:5]))


# ------------------------------------------------------------------ #
# 7. 외부 자원 무결성 (QA I-07)
# ------------------------------------------------------------------ #
def check_sri():
    tag = re.compile(r'<(script|link)\b[^>]*\b(?:src|href)="(https://[^"]+)"[^>]*>')
    # 구글 폰트 스타일시트는 브라우저마다 내용이 달라 SRI 를 걸 수 없다.
    exempt = ('fonts.googleapis.com', 'fonts.gstatic.com')
    for name in html_files():
        s = read(name)
        for m in tag.finditer(s):
            whole, url = m.group(0), m.group(2)
            if any(e in url for e in exempt):
                continue
            if 'rel="preconnect"' in whole or 'rel="dns-prefetch"' in whole:
                continue
            if 'integrity=' not in whole:
                err('NO-SRI', '%s: 무결성 검증이 없는 외부 자원 %s' % (name, url[:90]))


# ------------------------------------------------------------------ #
# 8. 콘텐츠 수치 일관성 (QA I-11)
# ------------------------------------------------------------------ #
def check_counts():
    order_path = os.path.join(PUB, 'js', 'page-order.json')
    if not os.path.exists(order_path):
        err('NO-CATALOG', 'js/page-order.json 이 없다. 이전-다음 이동이 동작하지 않는다.')
        return
    with open(order_path, encoding='utf-8') as f:
        order = json.load(f)
    existing = set(os.listdir(PUB))
    missing = [p for p in order if p not in existing]
    if missing:
        err('CATALOG-STALE', '카탈로그에 있으나 실제로 없는 페이지: %s' % missing[:5])

    sitemap = os.path.join(PUB, 'sitemap.xml')
    if os.path.exists(sitemap):
        with open(sitemap, encoding='utf-8') as f:
            locs = re.findall(r'<loc>[^<]*/([^/<]+)</loc>', f.read())
        gone = [l for l in locs if l not in existing]
        if gone:
            err('SITEMAP-STALE', 'sitemap 에 있으나 실제로 없는 페이지: %s' % gone[:5])


# ------------------------------------------------------------------ #
# 8-2. 학습 순서 카탈로그와 기둥 목록 동기화
# ------------------------------------------------------------------ #
def check_page_order():
    """이전-다음 내비게이션이 새 기둥에서 조용히 사라지는 것을 막는다.

    이 저장소는 기둥 목록(03_code, 04_design, ...)을 여러 파일에 따로 적어 두는
    습관이 있었고, 기둥이 늘 때마다 한 곳씩 낡았다. 실제로 자동차 61종,
    개인정보 34종, 제로트러스트 8종이 page-order.json 에서 빠져 103개 페이지에서
    이전-다음이 뜨지 않았고, shell.js 의 ORDER_PREFIX 도 13_ai 에서 멈춰 있었다.
    둘 다 화면에 오류를 내지 않고 기능만 사라져서 눈에 띄지 않는다.
    """
    order_path = os.path.join(PUB, 'js', 'page-order.json')
    if not os.path.exists(order_path):
        err('NO-PAGE-ORDER', 'js/page-order.json 이 없다. python _gen/gen_page_order.py')
        return
    try:
        with open(order_path, encoding='utf-8') as fh:
            order = json.load(fh)
    except (OSError, ValueError) as exc:
        err('PAGE-ORDER-BROKEN', 'page-order.json 을 읽을 수 없다: %s' % exc)
        return

    names = set(html_files())
    listed = set(order)

    ghost = sorted(n for n in listed if n not in names)
    if ghost:
        err('PAGE-ORDER-STALE',
            '카탈로그에 있으나 실제로 없는 페이지: %s' % ghost[:5])

    # 번호 기둥(NN_xxx) 페이지는 모두 카탈로그에 있어야 한다.
    pillar = sorted(n for n in names if re.match(r'^\d{2}_', n))
    missing = [n for n in pillar if n not in listed]
    if missing:
        err('PAGE-ORDER-STALE',
            '카탈로그에 빠진 학습 페이지 %d개 (예: %s). python _gen/gen_page_order.py'
            % (len(missing), ', '.join(missing[:4])))

    # shell.js 가 그 페이지에서 카탈로그를 불러오기는 하는지.
    shell_path = os.path.join(PUB, 'js', 'shell.js')
    if os.path.exists(shell_path):
        with open(shell_path, encoding='utf-8', errors='replace') as fh:
            shell = fh.read()
        m = re.search(r'var ORDER_PREFIX\s*=\s*/([^/]+)/', shell)
        if m:
            try:
                rx = re.compile(m.group(1).replace('\\\\', '\\'))
            except re.error:
                rx = None
            if rx is not None:
                blocked = [n for n in pillar if not rx.match(n)]
                if blocked:
                    err('PAGER-PREFIX-STALE',
                        'shell.js ORDER_PREFIX 가 %d개 페이지를 걸러낸다 (예: %s). '
                        '기둥 이름을 나열하지 말고 번호 규칙으로 받는다.'
                        % (len(blocked), ', '.join(blocked[:3])))


# ------------------------------------------------------------------ #
# 9-2. 출처 연결 정합성 (C03)
# ------------------------------------------------------------------ #
def check_sources():
    """출처를 실제보다 강하게 주장하지 못하게 막는다.

    게시문까지만 본 자료를 "절까지 대조함" 으로 표시하거나, 대조하지 않은
    절 번호를 적는 것이 가장 흔한 과장이다. 사람이 손으로 적는 파일이라
    기계가 대신 지켜야 한다.
    """
    path = os.path.join(PUB, 'data', 'sources.json')
    if not os.path.exists(path):
        return                      # 아직 안 만들었으면 검사 대상 아님
    try:
        with open(path, encoding='utf-8') as fh:
            d = json.load(fh)
    except (OSError, ValueError) as exc:
        err('SOURCES-BROKEN', 'data/sources.json 을 읽을 수 없다: %s' % exc)
        return

    scope = {s['id']: s.get('verifiedScope') for s in d.get('sources', [])}
    for s in d.get('sources', []):
        if not s.get('checkedAt') or not s.get('checkedBy'):
            err('SOURCE-PROVENANCE', '%s: 누가 언제 확인했는지가 없다' % s.get('id'))
        if s.get('verifiedScope') == 'not-verified':
            err('SOURCE-UNVERIFIED', '%s: 확인하지 않은 자료가 등록부에 있다' % s.get('id'))

    for l in d.get('links', []):
        cid, sid, st = l.get('contentId'), l.get('sourceId'), l.get('reviewStatus')
        if sid not in scope:
            err('SOURCE-MISSING', '%s: 등록부에 없는 출처(%s)' % (cid, sid))
            continue
        if l.get('section') and st != 'section-verified':
            err('SOURCE-OVERCLAIM',
                '%s: 대조하지 않은 절 번호를 적었다(reviewStatus=%s)' % (cid, st))
        if st == 'section-verified' and scope[sid] != 'full-text':
            err('SOURCE-OVERCLAIM',
                '%s: 절까지 대조했다고 하는데 출처 %s 는 게시문까지만 확인돼 있다' % (cid, sid))
        if not l.get('why'):
            err('SOURCE-NO-REASON', '%s: 근거로 삼는 이유가 비어 있다' % cid)

# ------------------------------------------------------------------ #
# 9. 콘텐츠 레지스트리 (QA W-06)
# ------------------------------------------------------------------ #
def check_registry():
    """화면 배지는 data/content-registry.json 을 읽어 채운다.
    HTML 에 남겨 둔 값은 스크립트가 실패했을 때 보일 대비값이므로,
    레지스트리와 어긋나면 학습자가 틀린 숫자를 보게 된다.
    레지스트리 자체가 실제 파일 수와 맞는지도 여기서 다시 센다."""
    reg_path = os.path.join(PUB, 'data', 'content-registry.json')
    if not os.path.exists(reg_path):
        err('NO-REGISTRY',
            'public/data/content-registry.json 이 없다. python _gen/gen_registry.py 를 먼저 돌린다.')
        return
    with open(reg_path, encoding='utf-8') as f:
        reg = json.load(f)

    # 9-1. 레지스트리 수치가 실제 파일 수와 같은가
    names = set(os.listdir(PUB))
    for d in reg.get('domains', []):
        actual = len([n for n in names
                      if n.startswith(d['prefix']) and n.endswith('.html')])
        if actual != d['count']:
            err('REGISTRY-STALE',
                '%s 도메인: 레지스트리 %d, 실제 %d. gen_registry.py 를 다시 돌린다.'
                % (d['id'], d['count'], actual))
        for fn_ in d.get('files', []):
            if fn_ not in names:
                err('REGISTRY-STALE', '레지스트리에 있으나 실제로 없는 파일: %s' % fn_)
    sim_pfx = tuple(reg['simulators'].get('prefixes') or [reg['simulators']['prefix']])
    sims = len([n for n in names
                if n.startswith(sim_pfx) and n.endswith('.html')])
    if sims != reg['simulators']['count']:
        err('REGISTRY-STALE',
            '시뮬레이터: 레지스트리 %d, 실제 %d' % (reg['simulators']['count'], sims))

    # 9-2. HTML 대비값이 레지스트리와 같은가
    def pick(path):
        cur = reg
        for key in path.split('.'):
            if isinstance(cur, list):
                cur = next((x for x in cur if x.get('id') == key), None)
            elif isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return None
            if cur is None:
                return None
        return cur

    pat = re.compile(
        r'<span[^>]*data-wvs-count="([^"]+)"[^>]*>([^<]*)</span>')
    for name in html_files():
        doc = read(name)
        if 'data-wvs-count' not in doc:
            continue
        if '/js/registry.js' not in doc:
            err('REGISTRY-NOJS',
                '%s 에 data-wvs-count 가 있으나 js/registry.js 를 불러오지 않는다.' % name)
        for path, shown in pat.findall(doc):
            want = pick(path)
            if want is None:
                err('REGISTRY-PATH', '%s: 레지스트리에 없는 경로 %s' % (name, path))
                continue
            if shown.replace(',', '').strip() != str(want):
                err('REGISTRY-DRIFT',
                    '%s: %s 표기 "%s" 가 레지스트리 값 %s 와 다르다.'
                    % (name, path, shown.strip(), want))


def main():
    strict = '--strict' in sys.argv
    for fn in (check_script_blocks, check_injected_tags, check_links, check_backdoors,
               check_text_quality, check_a11y, check_sri, check_counts,
               check_page_order, check_sources, check_registry):
        fn()

    print('=' * 62)
    print('WEB-VULN-SIM 배포 전 검증  (public 파일 %d개)' % len(html_files()))
    print('=' * 62)
    if warnings:
        print('\n경고 %d건' % len(warnings))
        for w in warnings[:40]:
            print('  ' + w)
        if len(warnings) > 40:
            print('  ... 외 %d건' % (len(warnings) - 40))
    if errors:
        print('\n실패 %d건' % len(errors))
        for e in errors[:60]:
            print('  ' + e)
        if len(errors) > 60:
            print('  ... 외 %d건' % (len(errors) - 60))
        print('\n결과: 실패')
        return 1
    if strict and warnings:
        print('\n결과: 실패 (strict 모드에서는 경고도 실패로 처리)')
        return 1
    print('\n결과: 통과')
    return 0


if __name__ == '__main__':
    sys.exit(main())
