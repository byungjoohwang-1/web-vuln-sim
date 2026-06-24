# -*- coding: utf-8 -*-
"""Extract MISRA C:2012 / MISRA C++:2023 example snippets from local PDFs.

The extractor builds std_pdf_overrides.py. gen_standards.py can then apply the
extracted PDF examples over the existing rule metadata.
"""
from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
BOOKS = ROOT / "books"
OUT = Path(__file__).resolve().parent / "std_pdf_overrides.py"
FULL_OUT = Path(__file__).resolve().parent / "std_pdf_full_rules.py"


PDFS = {
    "misrac": "MISRA C2012 Guidelines for the Use of the C Language in Critical Systems",
    "misracpp": "MISRA-CPP-2023",
}


def find_pdf(prefix: str) -> Path:
    for p in BOOKS.glob("*.pdf"):
        if prefix in p.name:
            return p
    raise FileNotFoundError(prefix)


def clean_text(s: str) -> str:
    repl = {
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\u00a0": " ",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u25cf": "*",
        "\u25a0": "*",
        "\ufffd": "",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    lines = []
    for line in s.splitlines():
        t = line.rstrip()
        if not t:
            lines.append("")
            continue
        if re.search(r"^MISRA C(?:\+\+)? 20\d\d", t):
            continue
        if t.startswith("Licensed to:"):
            continue
        if re.match(r"^\d{1,3}\s*$", t):
            continue
        if re.match(r"^\d{1,2} [A-Z][a-z]+ 20\d{2}$", t):
            continue
        if t.startswith("Section "):
            continue
        lines.append(t)
    return "\n".join(lines)


def pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return clean_text("\n".join((p.extract_text() or "") for p in reader.pages))


def load_rule_ids(module_name: str) -> list[str]:
    import importlib
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    mod = importlib.import_module(module_name)
    return [r["id"] for r in mod.RULES]


def heading_pattern(rid: str) -> re.Pattern[str]:
    if rid.startswith("Dir "):
        n = re.escape(rid.split(" ", 1)[1])
        return re.compile(rf"(?m)^Dir\s+{n}(?:\s|$)")
    n = re.escape(rid.split(" ", 1)[1])
    return re.compile(rf"(?m)^Rule\s+{n}(?:\s|$)")


def is_real_rule_heading(text: str, pos: int) -> bool:
    """Avoid cross-reference/table hits such as "Rule 5.1 warning 347"."""
    first_line = text[pos : text.find("\n", pos) if "\n" in text[pos : pos + 300] else pos + 300].strip()
    if re.fullmatch(r"(?:Dir|Rule)\s+\d+(?:\.\d+)*", first_line):
        return False
    window = text[pos : pos + 1600]
    return bool(re.search(r"(?m)^Category\s+(?:Mandatory|Required|Advisory)\b", window))


def next_heading_pos(text: str, start: int) -> int:
    for m in re.finditer(r"(?m)^(?:Dir|Rule)\s+\d+(?:\.\d+)*(?:\s|$)", text[start + 1 :]):
        pos = start + 1 + m.start()
        if is_real_rule_heading(text, pos):
            return pos
    return len(text)


def section_for(text: str, rid: str) -> str:
    for m in heading_pattern(rid).finditer(text):
        if is_real_rule_heading(text, m.start()):
            return text[m.start() : next_heading_pos(text, m.start())]
    return ""


def codeish(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    if re.match(r"^(Rule|Dir|Category|Analysis|Rationale|Amplification|Exception|See also)\b", t):
        return False
    if re.match(r"^(In the following|The following|This rule|For the purposes|Note:|The comments refer|The declaration|The example|The name)\b", t):
        return False
    if t.startswith("* "):
        return False
    if len(t) > 120 and not re.search(r"[;{}#=]|//|/\*|\*/", t):
        return False
    if len(t.split()) > 14 and not re.search(r"[;{}#=]|//|/\*|\*/", t):
        return False
    markers = (";", "{", "}", "#", "//", "/*", "*/", "=", "::")
    keywords = re.compile(r"\b(?:int|void|char|bool|float|double|enum|struct|class|namespace|auto|const|volatile|static|extern|return|if|for|while|switch|catch|try|throw|using|template|typedef|uint|int\d+_t|uint\d+_t)\b")
    return any(m in t for m in markers) or bool(keywords.search(t))


def strong_code_line(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    if t.startswith(("#", "//", "/*", "*", "}")):
        return True
    if re.search(r"[;{}=]", t):
        return True
    if re.match(r"^(?:int|void|char|bool|float|double|enum|struct|class|namespace|auto|const|volatile|static|extern|return|if|for|while|switch|catch|try|throw|using|template|typedef|std::|[A-Za-z_]\w*::)", t):
        return True
    return False


def normalize_code(lines: list[str]) -> str:
    out = []
    for line in lines:
        line = line.rstrip()
        if re.search(r"^(See also|Rule|Dir)\b", line.strip()):
            break
        out.append(line)
    while out and not strong_code_line(out[0]):
        out.pop(0)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def split_blocks(example_text: str) -> list[str]:
    lines = example_text.splitlines()
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cur:
                blocks.append(cur)
                cur = []
            continue
        if codeish(line):
            cur.append(line)
        else:
            if cur:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    normalized = []
    for b in blocks:
        code = normalize_code(b)
        if len(code.strip()) >= 20:
            normalized.append(code)
    return normalized


LABEL_RE = re.compile(
    r"(?is)(?:in\s+the\s+following|the\s+following)[^\n]{0,260}?"
    r"\b(non[- ]?compliant|compliant)\b"
)


def has_noncompliant(s: str) -> bool:
    return bool(re.search(r"(?i)\bnon\W*compliant\b", s))


def has_compliant(s: str) -> bool:
    return bool(re.search(r"(?i)\bcompliant\b", s))


def blocks_after_labels(example: str) -> tuple[list[str], list[str]]:
    bad_blocks: list[str] = []
    good_blocks: list[str] = []
    labels = list(LABEL_RE.finditer(example))
    for idx, m in enumerate(labels):
        label = m.group(1).lower()
        start = m.end()
        end = labels[idx + 1].start() if idx + 1 < len(labels) else len(example)
        code = "\n\n".join(split_blocks(example[start:end])).strip()
        if not code:
            continue
        low_code = code.lower()
        if has_compliant(low_code) and has_noncompliant(low_code):
            split_bad, split_good = split_comment_classified(split_blocks(example[start:end]))
            bad_blocks.extend(x for x in split_bad if x)
            good_blocks.extend(x for x in split_good if x)
            continue
        if label.startswith("non"):
            bad_blocks.append(code)
        else:
            good_blocks.append(code)
    return bad_blocks, good_blocks


def split_comment_classified(blocks: list[str]) -> tuple[list[str], list[str]]:
    bad_lines: list[str] = []
    good_lines: list[str] = []
    for block in blocks:
        for line in block.splitlines():
            low = line.lower()
            if has_noncompliant(low):
                bad_lines.append(line)
            elif has_compliant(low):
                good_lines.append(line)
    return (
        [normalize_code(bad_lines)] if bad_lines else [],
        [normalize_code(good_lines)] if good_lines else [],
    )


def classify_blocks(section: str) -> tuple[str, str]:
    ex_idx = section.find("Example")
    if ex_idx < 0:
        return "", ""
    example = section[ex_idx:]
    stop = len(example)
    for token in ("\nSee also", "\nRule ", "\nDir "):
        p = example.find(token, 20)
        if p > 0:
            stop = min(stop, p)
    example = example[:stop]
    blocks = split_blocks(example)
    bad_blocks, good_blocks = blocks_after_labels(example)
    if not bad_blocks and not good_blocks:
        bad_blocks, good_blocks = split_comment_classified(blocks)
    for block in blocks:
        low = block.lower()
        if has_compliant(low) and has_noncompliant(low):
            split_bad, split_good = split_comment_classified([block])
            if split_bad and not bad_blocks:
                bad_blocks.extend(split_bad)
            if split_good and not good_blocks:
                good_blocks.extend(split_good)
            continue
        if not bad_blocks and has_noncompliant(low):
            bad_blocks.append(block)
        elif not good_blocks and has_compliant(low):
            good_blocks.append(block)
    # Some sections describe non-compliance in prose immediately before code.
    if not bad_blocks or not good_blocks:
        parts = re.split(r"(?i)(?=in the following|the following|/\*|#include|enum |int |void |class |namespace |const |auto )", example)
        for part in parts:
            blocks2 = split_blocks(part)
            if not blocks2:
                continue
            code = "\n".join(blocks2)
            low = part.lower()
            low_code = code.lower()
            if has_compliant(low_code) and has_noncompliant(low_code):
                split_bad, split_good = split_comment_classified(blocks2)
                if split_bad and not bad_blocks:
                    bad_blocks.extend(split_bad)
                if split_good and not good_blocks:
                    good_blocks.extend(split_good)
                continue
            if has_noncompliant(low) and not bad_blocks:
                bad_blocks.append(code)
            elif has_compliant(low) and not has_noncompliant(low) and not good_blocks:
                good_blocks.append(code)
    bad = "\n\n".join(bad_blocks[:2]).strip()
    good = "\n\n".join(good_blocks[:2]).strip()
    if bad == good:
        good = ""
    return bad, good


def build_overrides() -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {"misrac": {}, "misracpp": {}}
    sources = {
        "misrac": (find_pdf(PDFS["misrac"]), load_rule_ids("std_misrac")),
        "misracpp": (find_pdf(PDFS["misracpp"]), load_rule_ids("std_misracpp")),
    }
    for key, (pdf, ids) in sources.items():
        text = pdf_text(pdf)
        for rid in ids:
            sec = section_for(text, rid)
            if not sec:
                continue
            bad, good = classify_blocks(sec)
            payload = {}
            if bad:
                payload["bad"] = bad
            if good:
                payload["good"] = good
            if payload:
                out[key][rid] = payload
    return out


def all_pdf_rule_ids(text: str) -> list[str]:
    ids: list[str] = []
    for m in re.finditer(r"(?m)^(Dir|Rule)\s+(\d+(?:\.\d+)*)(?:\s|$)", text):
        if not is_real_rule_heading(text, m.start()):
            continue
        rid = f"{m.group(1)} {m.group(2)}"
        if rid not in ids:
            ids.append(rid)
    return ids


def tidy_inline(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    # Common PDF extraction splits from ligatures and superscript-like spacing.
    fixes = {
        "identi fi er": "identifier",
        "Identi fi er": "Identifier",
        "identi fi ers": "identifiers",
        "Identi fi ers": "Identifiers",
        "fi le": "file",
        "fi les": "files",
        "fl oating": "floating",
        "fl ow": "flow",
        "de fi ned": "defined",
        "unde fi ned": "undefined",
        "Unspeci fi ed": "Unspecified",
        "Undefi ned": "Undefined",
        "Impl ementation": "Implementation",
        "Ampli2cation": "Amplification",
        "9le": "file",
        "9les": "files",
        "9rst": "first",
        "eCect": "effect",
        "^oating": "floating",
    }
    for a, b in fixes.items():
        s = s.replace(a, b)
    return s


def parse_meta(section: str, rid: str, std_key: str) -> dict[str, str]:
    lines = [ln.strip() for ln in section.splitlines() if ln.strip()]
    title_parts: list[str] = []
    first_re = re.compile(rf"^(?:{re.escape(rid)})\s*(.*)$")
    for i, line in enumerate(lines[:12]):
        if i == 0:
            m = first_re.match(line)
            if m and m.group(1).strip():
                title_parts.append(m.group(1).strip())
            continue
        if re.match(r"^(?:C90|C99|C11|\[|Category|Analysis|Applies|Amplification|Ampli2cation|Rationale)\b", line):
            break
        if line.startswith("*"):
            break
        title_parts.append(line)
    title = tidy_inline(" ".join(title_parts)) or rid
    category = "Advisory"
    analysis = ""
    m = re.search(r"(?m)^Category\s+([A-Za-z]+)", section)
    if m:
        category = tidy_inline(m.group(1))
    m = re.search(r"(?m)^Analysis\s+([^\n]+)", section)
    if m:
        analysis = tidy_inline(m.group(1).split(",", 1)[0])
    cat = category
    if analysis:
        cat += f" · {analysis}"
    if std_key == "misrac":
        cat += " · " + ("Dir" if rid.startswith("Dir ") else "Rule")
    return {"title": title, "cat": cat}


def placeholder_code(std_key: str, rid: str, compliant: bool) -> str:
    marker = "Compliant" if compliant else "Non-compliant"
    lang = "C++" if std_key == "misracpp" else "C"
    return (
        f"/* {marker} example for {rid}\n"
        f" * PDF heading was imported, but an explicit {marker.lower()} code block\n"
        f" * was not safely separated by the automatic extractor.\n"
        f" * Add/verify the {lang} training snippet manually when preparing class material.\n"
        f" */"
    )


def build_full_rules(overrides: dict[str, dict[str, dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    full: dict[str, list[dict[str, str]]] = {"misrac": [], "misracpp": []}
    for key in full:
        text = pdf_text(find_pdf(PDFS[key]))
        for rid in all_pdf_rule_ids(text):
            sec = section_for(text, rid)
            meta = parse_meta(sec, rid, key)
            payload = overrides.get(key, {}).get(rid, {})
            title = meta["title"]
            full[key].append(
                {
                    "id": rid,
                    "cat": meta["cat"],
                    "title": title,
                    "title_en": title,
                    "bad": payload.get("bad") or placeholder_code(key, rid, False),
                    "good": payload.get("good") or placeholder_code(key, rid, True),
                    "why": f"{rid} ({title})은 로컬 PDF 원본 기준으로 추가한 MISRA 규칙입니다. 예제 코드를 기준으로 위반 조건과 준수 조건을 비교하며, 수업 전 정적분석 도구 결과와 함께 검증하세요.",
                    "why_en": f"{rid} ({title}) was added from the local PDF source. Compare the non-compliant and compliant examples, and verify them with static-analysis results before class delivery.",
                    "compiles": False,
                    "pdf_rule": True,
                    "pdf_example": bool(payload),
                }
            )
    return full


def main() -> None:
    overrides = build_overrides()
    header = (
        "# -*- coding: utf-8 -*-\n"
        "\"\"\"Auto-generated PDF example overrides for MISRA C:2012 and MISRA C++:2023.\n"
        "Generated from local books/*.pdf by extract_misra_pdf_examples.py.\n"
        "\"\"\"\n\n"
        "PDF_EXAMPLE_OVERRIDES = "
    )
    OUT.write_text(header + repr(overrides) + "\n", encoding="utf-8")
    full = build_full_rules(overrides)
    full_header = (
        "# -*- coding: utf-8 -*-\n"
        "\"\"\"Auto-generated full MISRA C/C++ rule metadata extracted from local PDFs.\n"
        "Generated by extract_misra_pdf_examples.py.\n"
        "\"\"\"\n\n"
        "PDF_FULL_RULES = "
    )
    FULL_OUT.write_text(full_header + repr(full) + "\n", encoding="utf-8")
    print("wrote", OUT)
    print("wrote", FULL_OUT)
    for k, v in overrides.items():
        both = sum(1 for x in v.values() if x.get("bad") and x.get("good"))
        print(k, "matched", len(v), "both", both)


if __name__ == "__main__":
    main()
