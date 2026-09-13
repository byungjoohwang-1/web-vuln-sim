#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""로컬 정적 서버 (public/).

`python -m http.server` 를 그냥 쓰면 안 되는 이유:
Windows 에서는 mimetypes 가 레지스트리를 읽는데, 여기서 .js 가 text/plain 으로
잡혀 있으면 브라우저가 스크립트를 거부한다("unsupported MIME type ('text/plain')").
그러면 로컬 검증 결과가 실제 배포와 달라져 엉뚱한 디버깅을 하게 된다.
확장자 매핑을 코드로 못박아 Firebase Hosting 과 같은 타입을 내려준다.

사용: python tools/dev-server.py [포트]
"""
import functools
import mimetypes
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')

TYPES = {
    '.js': 'text/javascript',
    '.mjs': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.svg': 'image/svg+xml',
    '.wasm': 'application/wasm',
    '.webmanifest': 'application/manifest+json',
    '.woff2': 'font/woff2',
    '.html': 'text/html',
}


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, **TYPES}

    def end_headers(self):
        # 로컬에서는 캐시가 검증을 방해하므로 항상 새로 받게 한다.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('%s\n' % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5199
    for ext, t in TYPES.items():
        mimetypes.add_type(t, ext)
    handler = functools.partial(Handler, directory=os.path.abspath(ROOT))
    srv = ThreadingHTTPServer(('127.0.0.1', port), handler)
    print('serving %s at http://127.0.0.1:%d' % (os.path.abspath(ROOT), port))
    srv.serve_forever()


if __name__ == '__main__':
    main()
