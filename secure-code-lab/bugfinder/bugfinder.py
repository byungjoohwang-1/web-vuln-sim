#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secure Code Lab — Bug Finder
============================
KISA 소프트웨어 개발보안 가이드(2021)의 구현단계 49개 보안약점을 탐지하는
경량 정적분석기(패턴 기반 SAST). 상용 도구를 대체하지 않는 학습용 도구다.

동작 방식:
  - bugfinder/rules.json 의 규칙을 로드한다.
  - 각 규칙은 위험 싱크(danger) 정규식과 완화 지표(sanitizer) 정규식을 가진다.
  - 어떤 파일에서 danger 가 매칭되고 sanitizer 가 없으면 '약점'으로 보고한다.
    (sanitizer 가 있으면 안전한 코드로 보고 억제 → 오탐 감소)

사용법:
  python bugfinder.py                 # examples/ 전체 스캔
  python bugfinder.py <경로>          # 특정 파일/폴더 스캔 (본인 코드도 가능)
  python bugfinder.py --selftest      # 예제 정탐/오탐 자가검증 (CI용)
  python bugfinder.py --json <경로>   # JSON 출력
"""
import os
import re
import sys
import json
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RULES_PATH = os.path.join(HERE, "rules.json")

LANG_BY_EXT = {".java": "java", ".c": "c", ".h": "c", ".cpp": "c", ".py": "py"}

# ANSI 색 (Windows 터미널/VS Code 지원)
class C:
    RED = "\033[31m"; GRN = "\033[32m"; YEL = "\033[33m"; CYN = "\033[36m"
    GRY = "\033[90m"; BLD = "\033[1m"; RST = "\033[0m"

SEV_COLOR = {"High": C.RED, "Medium": C.YEL, "Low": C.CYN}


def load_rules():
    with open(RULES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    rules = []
    for r in data["rules"]:
        r = dict(r)
        r["_danger"] = re.compile(r["danger"])
        r["_sanitizer"] = re.compile(r["sanitizer"]) if r.get("sanitizer") else None
        rules.append(r)
    return rules


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan_file(path, rules):
    """파일 하나를 스캔해 findings 리스트를 돌려준다."""
    ext = os.path.splitext(path)[1].lower()
    lang = LANG_BY_EXT.get(ext)
    if not lang:
        return []
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    findings = []
    for rule in rules:
        if rule["lang"] != lang:
            continue
        m = rule["_danger"].search(text)
        if not m:
            continue
        # sanitizer 가 파일 전체에 존재하면 안전한 것으로 보고 억제
        if rule["_sanitizer"] and rule["_sanitizer"].search(text):
            continue
        findings.append({
            "cwe": rule["cwe"],
            "ko": rule["ko"],
            "cat": rule["cat"],
            "sev": rule["sev"],
            "line": line_of(text, m.start()),
            "snippet": text[m.start():m.end()].strip().replace("\n", " ")[:80],
        })
    findings.sort(key=lambda x: x["line"])
    return findings


def iter_source_files(target):
    if os.path.isfile(target):
        yield target
        return
    for dirpath, _dirs, files in os.walk(target):
        for name in sorted(files):
            if os.path.splitext(name)[1].lower() in LANG_BY_EXT:
                yield os.path.join(dirpath, name)


def cmd_scan(target, as_json):
    rules = load_rules()
    all_findings = []
    for path in iter_source_files(target):
        for f in scan_file(path, rules):
            f["file"] = os.path.relpath(path, ROOT).replace("\\", "/")
            all_findings.append(f)

    if as_json:
        print(json.dumps(all_findings, ensure_ascii=False, indent=2))
        return 0

    if not all_findings:
        print(f"{C.GRN}✔ 발견된 보안약점 없음{C.RST}  (경로: {target})")
        return 0

    by_file = {}
    for f in all_findings:
        by_file.setdefault(f["file"], []).append(f)

    counts = {"High": 0, "Medium": 0, "Low": 0}
    for f in all_findings:
        counts[f["sev"]] = counts.get(f["sev"], 0) + 1

    print(f"\n{C.BLD}Secure Code Lab — Bug Finder 결과{C.RST}")
    print(f"{C.GRY}{'-'*66}{C.RST}")
    for file in sorted(by_file):
        print(f"\n{C.BLD}{file}{C.RST}")
        for f in by_file[file]:
            col = SEV_COLOR.get(f["sev"], "")
            print(f"  {col}[{f['sev']:<6}]{C.RST} L{f['line']:<4} "
                  f"{C.CYN}{f['cwe']:<8}{C.RST} {f['ko']}")
            print(f"          {C.GRY}↳ {f['snippet']}{C.RST}")
    print(f"\n{C.GRY}{'-'*66}{C.RST}")
    print(f"총 {C.BLD}{len(all_findings)}{C.RST}건  "
          f"({C.RED}High {counts['High']}{C.RST} / "
          f"{C.YEL}Medium {counts['Medium']}{C.RST} / "
          f"{C.CYN}Low {counts['Low']}{C.RST})\n")
    return 1


def cmd_selftest():
    """examples/ 의 Vulnerable/Secure 쌍을 자가검증한다.
    - Vulnerable 파일은 자기 CWE 규칙에 탐지되어야 한다 (정탐).
    - Secure 파일은 자기 CWE 규칙에 탐지되지 않아야 한다 (오탐 없음)."""
    rules = load_rules()
    by_cwe = {r["cwe"]: r for r in rules}
    examples = os.path.join(ROOT, "examples")
    if not os.path.isdir(examples):
        print(f"{C.RED}examples/ 폴더가 없습니다.{C.RST}")
        return 2

    cwe_re = re.compile(r"(CWE-\d+)")
    total = fp = fn = 0
    fails = []
    seen_cwe = set()
    for dirpath, _dirs, files in os.walk(examples):
        m = cwe_re.search(os.path.basename(dirpath))
        if not m:
            continue
        cwe = m.group(1)
        rule = by_cwe.get(cwe)
        if not rule:
            continue
        seen_cwe.add(cwe)
        vuln = [f for f in files if f.lower().startswith("vulnerable")]
        safe = [f for f in files if f.lower().startswith("secure")]
        for vf in vuln:
            total += 1
            found = [x for x in scan_file(os.path.join(dirpath, vf), rules) if x["cwe"] == cwe]
            if not found:
                fn += 1
                fails.append(f"{C.RED}FN{C.RST} {cwe} {os.path.basename(dirpath)}/{vf} "
                             f"→ 취약 코드가 탐지되지 않음")
        for sf in safe:
            total += 1
            found = [x for x in scan_file(os.path.join(dirpath, sf), rules) if x["cwe"] == cwe]
            if found:
                fp += 1
                fails.append(f"{C.YEL}FP{C.RST} {cwe} {os.path.basename(dirpath)}/{sf} "
                             f"→ 안전 코드가 오탐됨 (L{found[0]['line']})")

    print(f"\n{C.BLD}자가검증(Self-Test){C.RST}")
    print(f"{C.GRY}{'-'*66}{C.RST}")
    for line in fails:
        print("  " + line)
    missing = sorted(set(by_cwe) - seen_cwe)
    if missing:
        print(f"  {C.GRY}예제 없음(미구현): {', '.join(missing)}{C.RST}")
    ok = total - fp - fn
    color = C.GRN if (fp == 0 and fn == 0) else C.RED
    print(f"{C.GRY}{'-'*66}{C.RST}")
    print(f"검사 {total}건 · {color}통과 {ok}{C.RST} · "
          f"미탐(FN) {fn} · 오탐(FP) {fp} · "
          f"규칙 {len(by_cwe)} 중 예제 {len(seen_cwe)} 존재\n")
    return 0 if (fp == 0 and fn == 0) else 1


def main():
    ap = argparse.ArgumentParser(description="Secure Code Lab — Bug Finder")
    ap.add_argument("path", nargs="?", default=os.path.join(ROOT, "examples"),
                    help="스캔할 파일/폴더 (기본: examples/)")
    ap.add_argument("--selftest", action="store_true", help="예제 정탐/오탐 자가검증")
    ap.add_argument("--json", action="store_true", help="JSON 출력")
    args = ap.parse_args()

    # Windows 콘솔: ANSI 활성화 + UTF-8 출력 강제 (cp949 인코딩 오류 방지)
    if os.name == "nt":
        os.system("")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    if args.selftest:
        return cmd_selftest()
    return cmd_scan(args.path, args.json)


if __name__ == "__main__":
    sys.exit(main())
