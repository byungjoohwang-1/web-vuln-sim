#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""피드 소스 정의와 파서.

각 소스는 (사실 추출 자유도 = license) 를 명시한다. 이 프로젝트는 원문을 그대로
싣지 않고 개념적으로 재구성하는 방침이므로, 콘텐츠화(3단계+)에서 이 등급이
"본문 생성 가능(gov-public)" 인지 "링크·사실만(attrib)" 인지를 가른다. 수집·요약
단계에서는 사실 나열만 하므로 모든 등급이 허용된다.

지금 켜 둔 소스(전부 무인증·실측 확인):
  kev  CISA Known Exploited Vulnerabilities — 미국 정부 저작물(public domain)
  nvd  NVD CVE API 2.0 — 미국 정부 저작물. 무키 5req/30s

license 등급
  gov-public  미국 정부 저작물. 사실 추출·본문 생성 자유
  attrib      재사용 시 출처 표기 필요(예: GHSA=CC-BY). 콘텐츠화 시 sources.json 등재
  link-only   원문 인용 불가. 링크와 사실 요지만
"""
import json
import re
import urllib.request

UA = 'wvs-pipeline/1.0 (security education portal; contact via repo)'

# 이 포털이 다루는 도메인 키워드 — 사전 필터가 "우리 커리큘럼과 관련 있나" 판정에 쓴다.
DOMAIN_KEYWORDS = [
    'sql injection', 'xss', 'cross-site', 'csrf', 'ssrf', 'rce', 'remote code',
    'deserial', 'path traversal', 'directory traversal', 'authentication bypass',
    'authorization', 'privilege escalation', 'command injection', 'xxe',
    'open redirect', 'ldap', 'prototype pollution', 'insecure deserial',
    'buffer overflow', 'use after free', 'integer overflow', 'race condition',
    'hardcoded', 'weak crypto', 'cleartext', 'jwt', 'session',
    # AI/LLM 보안
    'llm', 'prompt injection', 'model', 'ml ', 'machine learning', 'ai ',
    'jailbreak', 'training data', 'inference',
    # 인프라·OT
    'firmware', 'iot', 'scada', 'ics', 'plc', 'modbus', 'container', 'kubernetes',
    'docker', 'cloud', 's3 bucket',
]

AI_KEYWORDS = ['llm', 'prompt injection', 'machine learning', 'jailbreak',
               'training data', 'model poisoning', 'ai model', 'neural']


def _get(url, etag=None, last_modified=None, timeout=30):
    """조건부 GET. (status, body_bytes, etag, last_modified) 반환.
    304 면 body 는 None."""
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    if etag:
        req.add_header('If-None-Match', etag)
    if last_modified:
        req.add_header('If-Modified-Since', last_modified)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return 304, None, etag, last_modified
        raise
    body = resp.read()
    return (resp.status, body,
            resp.headers.get('ETag'), resp.headers.get('Last-Modified'))


def _score(title, summary, cvss, in_kev):
    """사전 필터 점수. 높을수록 콘텐츠화 가치가 크다고 본다(사람/에이전트가 최종 판정)."""
    text = ((title or '') + ' ' + (summary or '')).lower()
    score = 0
    if in_kev:
        score += 50            # 실제로 악용 중 — 최우선
    if cvss:
        score += int(cvss * 3)  # CVSS 9.0 -> 27
    if any(k in text for k in AI_KEYWORDS):
        score += 20            # AI 보안은 이 포털의 전략 축
    if any(k in text for k in DOMAIN_KEYWORDS):
        score += 10            # 우리가 이미 다루는 취약점 계열
    return score


def fetch_kev(cursor):
    """CISA KEV 카탈로그. 악용 확인된 취약점만 담긴 고신뢰 소스."""
    url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
    status, body, etag, lm = _get(url, cursor.get('etag'), cursor.get('last_modified'))
    if status == 304:
        return [], etag, lm
    data = json.loads(body)
    items = []
    for v in data.get('vulnerabilities', []):
        cve = v.get('cveID')
        title = (v.get('vulnerabilityName') or cve or '').strip()
        summary = (v.get('shortDescription') or '')[:400]
        items.append({
            'canonical_id': cve,
            'source': 'kev',
            'url': 'https://nvd.nist.gov/vuln/detail/' + cve if cve else None,
            'title': title,
            'summary': summary,
            'published_at': v.get('dateAdded'),
            'cvss': None,
            'priority': _score(title, summary, None, in_kev=True),
            'license': 'gov-public',
        })
    return items, etag, lm


def fetch_nvd(cursor, results=40):
    """NVD 최근 수정 CVE. 무키 5req/30s 라 한 번에 소량만."""
    url = ('https://services.nvd.nist.gov/rest/json/cves/2.0'
           '?resultsPerPage=%d&startIndex=0' % results)
    status, body, etag, lm = _get(url, cursor.get('etag'), cursor.get('last_modified'))
    if status == 304:
        return [], etag, lm
    data = json.loads(body)
    items = []
    for entry in data.get('vulnerabilities', []):
        c = entry.get('cve', {})
        cve = c.get('id')
        descs = c.get('descriptions', [])
        summary = ''
        for d in descs:
            if d.get('lang') == 'en':
                summary = d.get('value', '')[:400]
                break
        # CVSS: v3.1 우선
        cvss = None
        metrics = c.get('metrics', {})
        for key in ('cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2'):
            if metrics.get(key):
                cvss = metrics[key][0].get('cvssData', {}).get('baseScore')
                break
        title = cve or ''
        items.append({
            'canonical_id': cve,
            'source': 'nvd',
            'url': 'https://nvd.nist.gov/vuln/detail/' + cve if cve else None,
            'title': title,
            'summary': summary,
            'published_at': c.get('published', '')[:10] or None,
            'cvss': cvss,
            'priority': _score(title, summary, cvss, in_kev=False),
            'license': 'gov-public',
        })
    return items, etag, lm


# 이름 -> fetch 함수. tick/fetch_feeds 가 이 목록을 돈다. 소스 추가 비용 = 한 줄.
SOURCES = {
    'kev': fetch_kev,
    'nvd': fetch_nvd,
}
