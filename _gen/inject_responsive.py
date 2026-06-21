# -*- coding: utf-8 -*-
"""모든 public/*.html 의 모바일 반응형 보강(멱등).
1) viewport 메타태그가 없으면 <head> 직후에 추가 (모바일 폭 적응의 전제).
2) 자체 @media 쿼리가 전혀 없는 페이지에 한해, 모바일 안전망 CSS(<!-- RESP-NET -->)를
   </head> 직전에 주입 — 코드블록(pre)·표(table)·이미지 가로 넘침을 막는다.
   * 이미 @media 가 있는(직접 반응형 설계된) 페이지는 건드리지 않아 레이아웃 충돌을 피한다.
주의: 보수적으로 element 단위 max-width/스크롤만 적용하며, 전역 overflow:hidden(콘텐츠 잘림) 은 쓰지 않는다.
"""
import os, glob, re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
NET = '''<!-- RESP-NET -->
<style>
@media (max-width: 768px){
  html{-webkit-text-size-adjust:100%}
  img,svg,video,canvas,iframe{max-width:100%;height:auto}
  pre,code{max-width:100%;overflow-x:auto;white-space:pre-wrap;word-break:break-word}
  table{display:block;width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
  body{padding-left:max(10px,env(safe-area-inset-left));padding-right:max(10px,env(safe-area-inset-right))}
}
</style>
'''

vp_added = net_added = skipped = 0
for f in glob.glob(os.path.join(PUB, '*.html')):
    h = open(f, encoding='utf-8').read()
    orig = h
    # 1) viewport
    if not re.search(r'name=["\']viewport', h, re.I):
        m = re.search(r'<head[^>]*>', h, re.I)
        if m:
            h = h[:m.end()] + '\n' + VIEWPORT + h[m.end():]
            vp_added += 1
    # 2) 안전망: 자체 @media 없고 마커도 없을 때만
    if '@media' not in h and '<!-- RESP-NET -->' not in h:
        if '</head>' in h:
            h = h.replace('</head>', NET + '</head>', 1)
            net_added += 1
    if h != orig:
        open(f, 'w', encoding='utf-8').write(h)
    else:
        skipped += 1

print('viewport 추가=%d, 안전망 주입=%d, 변경없음=%d' % (vp_added, net_added, skipped))
