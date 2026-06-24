# -*- coding: utf-8 -*-
"""Fetch current SEI CERT C/C++ guideline lists from the official SEI wiki.

The script does not clone full guideline pages. It captures the guideline ID,
title, section and whether the item is a rule/recommendation so gen_standards.py
can keep the portal aligned with the current official index.
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import http.client
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "std_cert_sei_rules.py"
REPORT = ROOT / "cert_sei_compare_report.json"

C_MAIN = "https://cmu-sei.github.io/secure-coding-standards/sei-cert-c-coding-standard/"
CPP_MAIN = "https://cmu-sei.github.io/secure-coding-standards/sei-cert-cpp-coding-standard/"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 web-vuln-sim CERT updater",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    last: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as res:
                return res.read().decode("utf-8", "replace")
        except (urllib.error.URLError, TimeoutError, http.client.RemoteDisconnected) as exc:
            last = exc
            time.sleep(1.2 + attempt)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).replace("\xa0", " ").strip()


def absolutize(href: str, base: str) -> str:
    return urllib.parse.urljoin(base, html.unescape(href))


def anchors(page: str, base: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', page, re.I | re.S):
        text = strip_tags(m.group(2))
        href = absolutize(m.group(1), base)
        if text:
            out.append((text, href))
    return out


def section_links(main_html: str, base: str, prefix: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    seen = set()
    pat = re.compile(rf"^{re.escape(prefix)}\s+\d+\.\s+")
    for text, href in anchors(main_html, base):
        if pat.search(text) and href not in seen:
            seen.add(href)
            links.append((text, href))
    return links


GUIDELINE_RE = re.compile(r"^([A-Z]{3}\d{2}-(?:C|CPP))\.\s+(.+)$")


def section_code(section_title: str) -> str:
    m = re.search(r"\(([A-Z]{3})\)", section_title)
    return m.group(1) if m else "MSC"


def collect_from_sections(section_pages: list[tuple[str, str]], lang: str, include_cross_c: bool) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    seen = set()
    for idx, (section_title, url) in enumerate(section_pages, start=1):
        sys.stderr.write(f"fetch {lang} {idx}/{len(section_pages)} {section_title}\n")
        page = fetch(url)
        sec = section_code(section_title)
        kind = "Rec" if section_title.startswith("Rec.") else "Rule"
        for text, href in anchors(page, url):
            m = GUIDELINE_RE.match(text)
            if not m:
                continue
            gid, title = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip()
            is_cpp = gid.endswith("-CPP")
            is_c = gid.endswith("-C")
            if lang == "certc" and not is_c:
                continue
            if lang == "certcpp" and not (is_cpp or (include_cross_c and is_c)):
                continue
            if gid in seen:
                continue
            seen.add(gid)
            rules.append(
                {
                    "id": gid,
                    "title": title,
                    "title_en": title,
                    "section": sec,
                    "kind": kind,
                    "source_url": href,
                    "from_c_standard": bool(lang == "certcpp" and is_c),
                }
            )
        time.sleep(0.1)
    return rules


def load_existing() -> dict[str, list[str]]:
    sys.path.insert(0, str(ROOT))
    import std_certc
    import std_certcpp

    return {
        "certc": [r["id"] for r in std_certc.RULES],
        "certcpp": [r["id"] for r in std_certcpp.RULES],
    }


def main() -> None:
    c_html = fetch(C_MAIN)
    cpp_html = fetch(CPP_MAIN)
    c_sections = section_links(c_html, C_MAIN, "Rule")
    c_rec_sections = section_links(c_html, C_MAIN, "Rec.")
    cpp_sections = section_links(cpp_html, CPP_MAIN, "Rule")

    certc = collect_from_sections(c_sections + c_rec_sections, "certc", include_cross_c=False)
    certcpp_all = collect_from_sections(cpp_sections, "certcpp", include_cross_c=True)
    certcpp_cpp_only = [r for r in certcpp_all if not r["from_c_standard"]]

    data = {
        "certc": certc,
        "certcpp": certcpp_cpp_only,
        "certcpp_with_c_cross_rules": certcpp_all,
    }
    OUT.write_text(
        "# -*- coding: utf-8 -*-\n"
        '"""Auto-generated from official SEI CERT C/C++ wiki section indexes."""\n\n'
        "SEI_CERT_RULES = "
        + repr(data)
        + "\n",
        encoding="utf-8",
    )

    existing = load_existing()
    report = {}
    for key, official in [("certc", certc), ("certcpp", certcpp_cpp_only)]:
        official_ids = [r["id"] for r in official]
        current_ids = existing[key]
        report[key] = {
            "official_count": len(official_ids),
            "current_count": len(current_ids),
            "missing_in_current": [gid for gid in official_ids if gid not in set(current_ids)],
            "extra_in_current": [gid for gid in current_ids if gid not in set(official_ids)],
        }
    report["certcpp_with_c_cross_rules"] = {
        "official_count": len(certcpp_all),
        "cpp_only_count": len(certcpp_cpp_only),
        "cross_c_count": len(certcpp_all) - len(certcpp_cpp_only),
        "cross_c_ids": [r["id"] for r in certcpp_all if r["from_c_standard"]],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("wrote", OUT)
    print("wrote", REPORT)


if __name__ == "__main__":
    main()
