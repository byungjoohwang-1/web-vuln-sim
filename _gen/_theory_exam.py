# -*- coding: utf-8 -*-
"""1교시 이론 — 2024.12 기출 복원의 단답/지식형 항목(KISA 진단가이드 수치 근거).
THEORY 스키마: OX{a:bool} / MC{o:[],a:idx} / SHORT{answers:[]}."""

PART = [
    {'type':'SHORT','cat':'보안기능',
     'q':'KISA 암호 가이드 기준, 공개키 암호(RSA)의 공개키 길이는 최소 몇 비트 이상을 사용해야 하는가? (숫자만)',
     'answers':['2048','2048비트','2048 비트'],
     'e':'KISA 암호이용안내서는 RSA 공개키를 최소 2048비트(보안강도 112비트) 이상으로 권고합니다. (3072 권장)'},

    {'type':'SHORT','cat':'보안기능',
     'q':'KISA가 정의한 안전한 암호 알고리즘의 최소 안전성 수준(보안강도)은 몇 비트인가? (숫자만)',
     'answers':['112','112비트','112 비트'],
     'e':'암호알고리즘 검증기준상 최소 안전성 수준은 112비트이며, 이는 RSA 2048비트·SHA-224 이상에 대응합니다.'},

    {'type':'MC','cat':'보안기능',
     'q':'FIPS 140-2 보안 레벨 중 "침입(변조)을 감지하면 저장된 암호키를 즉시 삭제"하는 강력한 변조 탐지·대응을 요구하는 레벨은?',
     'o':['Level 1','Level 2','Level 3','Level 4'],'a':2,
     'e':'FIPS 140-2 Level 3은 강력한 변조 탐지·대응으로 침입 감지 시 저장된 키를 삭제합니다. Level 4는 전압·온도 등 환경 변화까지 감지해 키를 삭제합니다.'},

    {'type':'SHORT','cat':'보안기능',
     'q':'세션ID가 담긴 쿠키를 자바스크립트(document.cookie)로 읽지 못하게 막는 쿠키 속성의 이름은?',
     'answers':['HttpOnly','httponly','HTTP Only'],
     'e':'HttpOnly 속성을 설정하면 스크립트로 쿠키를 조회할 수 없어 XSS를 통한 세션ID 탈취를 완화합니다. 전송 보호를 위해 Secure 속성도 함께 설정합니다.'},

    {'type':'SHORT','cat':'보안기능',
     'q':'JAR로 내려받은 코드의 전자서명 주체(서명자)를 확인하기 위해 사용하는 JarEntry의 메소드명은?',
     'answers':['getCodeSigners','getCodeSigners()','getcodesigners'],
     'e':'JarEntry.getCodeSigners()로 전자서명 주체를 확인하고, 서명이 없거나(null/length 0) 신뢰할 수 없으면 코드를 실행하지 않아야 합니다(부적절한 전자서명 확인 대책).'},

    {'type':'OX','cat':'코드오류',
     'q':'역직렬화 보안약점을 막기 위해 ObjectInputStream을 상속하여 resolveClass에서 허용 클래스 화이트리스트만 통과시키는 것은 올바른 대책이다.',
     'a':True,
     'e':'맞습니다. WhitelistedObjectInputStream처럼 resolveClass를 재정의해 화이트리스트에 없는 클래스의 역직렬화를 예외 처리하는 것이 KISA 권고 대책입니다.'},
]
