#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""에이전트 호출 어댑터.

백엔드는 claude CLI 헤드리스(구독 쿼터, 별도 과금 없음)다. 실제 호출은 부모
claude 세션이 없는 cron 실행에서 작동한다 — 대화형 세션 안에서 자식 claude 를
띄우면 중첩 충돌로 무응답이 되므로, 대화 중 검증은 드라이런으로만 한다.

  WVS_AGENT_DRYRUN=1  실제 호출 없이 dry_stub 을 돌려준다(로직·DB 전이 검증용)

JSON 추출은 운용 파서와 같은 원칙 — 코드펜스/과잉 텍스트를 걷어내고 첫 균형
잡힌 객체를 꺼낸다. 모델이 산문을 덧붙여도 계약 JSON 만 취한다.
"""
import json
import os
import subprocess


def _extract_json(text):
    """text 에서 첫 균형 잡힌 JSON 객체를 꺼낸다. 실패하면 None."""
    if not text:
        return None
    # 코드펜스 제거
    t = text.strip()
    if '```' in t:
        # ```json ... ``` 안쪽 우선
        parts = t.split('```')
        for p in parts:
            p = p.strip()
            if p.startswith('json'):
                p = p[4:].strip()
            if p.startswith('{') or p.startswith('['):
                t = p
                break
    start = None
    depth = 0
    in_str = False
    esc = False
    for i, ch in enumerate(t):
        if start is None:
            if ch in '{[':
                start = i
                depth = 1
            continue
        if in_str:
            if esc:
                esc = False
            elif ch == '\\':
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in '{[':
            depth += 1
        elif ch in '}]':
            depth -= 1
            if depth == 0:
                blob = t[start:i + 1]
                try:
                    return json.loads(blob)
                except ValueError:
                    return None
    return None


def run_agent(prompt, system=None, model=None, timeout=600, dry_stub=None):
    """에이전트 1회 호출. 반환:
      {ok: True, data: <파싱된 JSON>, text: <원문>, dry: bool}
      {ok: False, error: <사유>}
    dry_stub 은 드라이런일 때 돌려줄 파이썬 객체(또는 () -> 객체)."""
    if os.environ.get('WVS_AGENT_DRYRUN') == '1':
        data = dry_stub() if callable(dry_stub) else dry_stub
        return {'ok': True, 'dry': True, 'data': data, 'text': json.dumps(data, ensure_ascii=False)}

    cmd = ['claude', '-p', prompt, '--output-format', 'json',
           '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}']
    if system:
        cmd += ['--append-system-prompt', system]
    if model:
        cmd += ['--model', model]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                           timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'timeout(%ds)' % timeout}
    except FileNotFoundError:
        return {'ok': False, 'error': 'claude CLI 없음(PATH 확인)'}
    if r.returncode != 0:
        return {'ok': False, 'error': 'exit %d: %s' % (r.returncode, (r.stderr or '')[:200])}
    try:
        env = json.loads(r.stdout)
    except ValueError:
        return {'ok': False, 'error': 'CLI 응답이 JSON 아님', 'stdout': (r.stdout or '')[:200]}
    text = env.get('result') or env.get('text') or ''
    data = _extract_json(text)
    if data is None:
        return {'ok': False, 'error': '응답에서 JSON 계약을 못 찾음', 'text': text[:300]}
    return {'ok': True, 'dry': False, 'data': data, 'text': text, 'raw': env}


if __name__ == '__main__':
    # 파서 자체 검증(호출 없이).
    samples = [
        '```json\n{"a":1,"b":[2,3]}\n```',
        'Here is the result: {"decision":"build","cwe":"CWE-89"} done.',
        '[{"x":1},{"y":2}]',
        'no json here',
    ]
    for s in samples:
        print(repr(s[:30]), '->', _extract_json(s))
