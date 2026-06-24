# -*- coding: utf-8 -*-
"""외부 CDN <script src> 에 Subresource Integrity(SRI) 멱등 주입.
대상은 버전 고정(immutable) CDN URL뿐 — 공급망 변조 방어. crossorigin=anonymous 필수
(cdnjs/jsdelivr 모두 CORS 허용). 해시는 실제 서빙 바이트에서 sha384 계산.
재계산: curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A"""
import os
import re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')

HASHES = {
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js':
        'sha384-06z5D//U/xpvxZHuUz92xBvq3DqBBFi7Up53HRrbV7Jlv7Yvh/MZ7oenfUe9iCEt',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-java.min.js':
        'sha384-DioAMZB4yk91W6LuFit5wJDh8c5Ov09f/MBvja94y0PodMqTpTZeBeejqpRUru7D',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js':
        'sha384-WJdEkJKrbsqw0evQ4GB6mlsKe5cGTxBOw4KAEIa52ZLB7DDpliGkwdme/HMa5n1m',
    'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js':
        'sha384-9WmlN8ABpoFSSHvBGGjhvB3E/D8UkNB9HpLJjBQFC2VSQsM1odiQDv4NbEo+7l15',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js':
        'sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz',
    'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.min.js':
        'sha384-UcP5/iVWyRzIhnVjcB2o9W1eoYKL5fAhHTRzvFZg8ctOsoAoDeBQyQuyIk+BJ/nh',
}


def main():
    pats = [(re.compile(r'<script\b([^>]*?)\bsrc="' + re.escape(u) + r'"([^>]*?)>'), h)
            for u, h in HASHES.items()]
    changed = tags = 0
    for name in os.listdir(PUB):
        if not name.endswith('.html'):
            continue
        path = os.path.join(PUB, name)
        with open(path, encoding='utf-8') as f:
            html = f.read()
        orig = html
        for pat, h in pats:
            def repl(m, _h=h):
                whole = m.group(0)
                if 'integrity=' in whole:
                    return whole
                return whole[:-1] + ' integrity="' + _h + '" crossorigin="anonymous">'
            html, n = pat.subn(repl, html)
            tags += n
        if html != orig:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            changed += 1
    print('inject_sri: files_changed=%d tags_with_integrity_now=%d' % (changed, tags))


if __name__ == '__main__':
    main()
