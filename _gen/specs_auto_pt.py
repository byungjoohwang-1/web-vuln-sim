# -*- coding: utf-8 -*-
"""자동차 모의 해킹 실습(sim-auto-*) 미션 명세.

UN R155 Annex 5 Part A(공개 규정)의 위협 분류(Threat 1~32, 공격수법 A#.#)만 구조로 참고하고,
차량 시나리오·설정·해설·판정 로직은 전부 새로 썼다. 차량 브랜드는 가상(HANARO)이다.
AutoCrypt 독자 체크리스트 번호·제품명·NDA 자료 본문은 쓰지 않는다.

verdict/fix 는 브라우저에서 실행되는 JS 소스 문자열이다(가상 차량 veh 를 읽고 판정/방어한다).
판정을 하드코딩하지 않는 것이 핵심: verdict 는 **현재 차량 설정**을 보고 결정하므로,
방어(fix)를 적용하면 같은 함수가 '양호'를 돌려주고 재점검이 의미를 가진다.

한 페이지의 미션들은 같은 veh 인스턴스를 공유하므로, 미션마다 **서로 다른 플래그/ECU**를
겨냥해 앞 미션의 방어가 뒤 미션 판정을 바꾸지 않도록 설계했다.
"""


def _frame(bus, fid, data, desc):
    return {'bus': bus, 'id': fid, 'data': data, 'desc': desc}


# ═══════════════════════════════════════════════════════════════
# LAB 1 — CAN 버스 공격 (통신채널: T4 스푸핑 / T5 인젝션 / T11 악성 내부 메시지)
#   주제: 내부 버스에 메시지 인증(SecOC)이 없으면 어떤 프레임이든 위조·주입된다.
#   각 미션은 서로 다른 버스를 겨냥한다 → secoc[BUS] 플래그가 독립적.
# ═══════════════════════════════════════════════════════════════
CAN_VEHICLE = {
    'brand': 'HANARO', 'model': 'EV9 (가상 차량)',
    'vin': 'KMHXX00XXP0000001',
    'buses': {
        'PT': {'name': '파워트레인 CAN', 'speed': '500kbps'},
        'CH': {'name': '섀시 CAN(제동·조향)', 'speed': '500kbps'},
        'BODY': {'name': '바디 CAN(도어·램프)', 'speed': '125kbps'},
    },
    'secoc': {'PT': False, 'CH': False, 'BODY': False},
    'frames': [
        _frame('PT', '0x1A0', '00 32 00 00', '차속(km/h)'),
        _frame('PT', '0x0C9', '10 00 00 00', 'RPM'),
        _frame('CH', '0x2B0', '00 00 00 00', '제동 요청'),
        _frame('CH', '0x2C1', '80 00 00 00', '조향 토크'),
        _frame('BODY', '0x3F0', '00 00 00 00', '도어 잠금 상태'),
        _frame('BODY', '0x3F1', '01 00 00 00', '실내등'),
    ],
    'ecus': {},
    'obd': {'open': True, 'secureDebug': False},
}

CAN_LAB = {
    'key': 'can', 'file': 'sim-auto-can.html', 'code': 'AUTO-PT-CAN',
    'title': 'CAN 버스 공격', 'r155cat': 'R155 Annex5 · 통신채널',
    'desc': '차량 내부 CAN 버스에 붙어 프레임을 관측(candump)하고 위조 프레임을 주입(cansend)해 '
            '계기·제동·도어를 조작해 봅니다. 메시지 인증(SecOC)이 없으면 어떤 신호든 위조된다는 것을 '
            '직접 확인하고, 버스별로 인증을 적용해 방어합니다.',
    'vehicle': CAN_VEHICLE,
    'missions': [
        {
            'id': 'CAN-01', 'risk': 4, 'title': '차속 계기 스푸핑 (메시지 위장)',
            'r155': 'R155 Annex5 통신채널 · T4 메시지 스푸핑 (A4.1 위장)',
            'brief': '파워트레인 버스의 차속 프레임을 흉내 낸 프레임을 주입하면, 수신 ECU가 '
                     '<b>진짜 센서 값 대신 공격자 값</b>을 믿습니다. 계기판·주행보조가 잘못된 속도로 동작합니다.',
            'try': 'candump PT → cansend PT 0x1A0#00F0',
            'hint': 'cansend 결과에 "인증 없이" 가 있으면 취약, "MAC/SecOC 검증"이면 양호.',
            'cmds': ['candump PT', 'cansend PT 0x1A0#00F0'],
            'options': [
                '주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰',
                '거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기',
                '버스를 찾을 수 없음',
                '프레임이 관측되지 않음',
            ],
            'evidence': ['주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰'],
            'verdict': "function(v){return v.secoc.PT?'good':'vuln';}",
            'why': '파워트레인 버스에 메시지 인증이 없어 위조 차속 프레임이 그대로 수용됩니다. '
                   'CAN 은 원래 인증·암호화가 없는 프로토콜이라, 붙을 수만 있으면 어떤 값도 위조됩니다.',
            'ez': 'CAN 은 발신자를 확인하지 않는 사내 방송 같아서, 아무나 "지금 시속 0" 이라고 방송하면 모두가 믿는다.',
            'defense': '안전 관련 프레임에 메시지 인증(SecOC = 메시지별 MAC + 프레시니스 카운터)을 적용하고, '
                       '게이트웨이에서 도메인 간 프레임을 필터링한다.',
            'fix': "function(v){v.secoc.PT=true;}",
            'fixNote': 'PT(파워트레인) 버스에 SecOC 메시지 인증을 적용했습니다.',
        },
        {
            'id': 'CAN-02', 'risk': 5, 'title': '도어 언락 명령 주입 (코드/명령 인젝션)',
            'r155': 'R155 Annex5 통신채널 · T5 무단 조작 (A5.1 코드 인젝션)',
            'brief': '바디 버스의 도어 잠금 프레임을 주입하면 <b>키 없이 문을 열 수</b> 있습니다. '
                     '차량 절도·내부 침입의 출발점입니다.',
            'try': 'candump BODY → cansend BODY 0x3F0#00',
            'hint': '바디 버스(BODY)의 cansend 결과를 보세요.',
            'cmds': ['candump BODY', 'cansend BODY 0x3F0#00'],
            'options': [
                '주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰',
                '거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기',
                '도어 ECU가 응답하지 않음',
                'OBD 포트가 잠겨 있음',
            ],
            'evidence': ['주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰'],
            'verdict': "function(v){return v.secoc.BODY?'good':'vuln';}",
            'why': '바디 버스에 인증이 없어 위조 도어 명령이 수용됩니다. 편의 기능 버스라도 도난과 직결됩니다.',
            'ez': '현관 인터폰에 "문 열어" 라고 방송하면 확인 없이 열리는 셈이다.',
            'defense': '도어·이모빌라이저 관련 명령에 메시지 인증을 적용하고, 물리 접근(OBD)에서 오는 프레임을 '
                       '게이트웨이가 차단한다.',
            'fix': "function(v){v.secoc.BODY=true;}",
            'fixNote': 'BODY(바디) 버스에 SecOC 메시지 인증을 적용했습니다.',
        },
        {
            'id': 'CAN-03', 'risk': 5, 'title': '제동·조향 신호 위조 (악성 내부 메시지)',
            'r155': 'R155 Annex5 통신채널 · T11 악성 메시지 (A11.1 내부 메시지)',
            'brief': '섀시 버스의 제동/조향 프레임을 위조하면 <b>주행 중 안전에 직접</b> 영향을 줄 수 있습니다. '
                     '가장 위험한 등급입니다.',
            'try': 'candump CH → cansend CH 0x2B0#FF',
            'hint': '섀시 버스(CH)의 주입 결과를 보세요.',
            'cmds': ['candump CH', 'cansend CH 0x2B0#FF'],
            'options': [
                '주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰',
                '거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기',
                '섀시 버스가 없음',
                '프레임이 관측되지 않음',
            ],
            'evidence': ['주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰'],
            'verdict': "function(v){return v.secoc.CH?'good':'vuln';}",
            'why': '섀시 버스에 인증이 없어 위조 제동/조향 프레임이 수용됩니다. 안전 관련 버스는 인증이 필수입니다.',
            'ez': '브레이크에게 "밟아/놓아" 라고 아무나 명령할 수 있으면 운전자가 통제를 잃는다.',
            'defense': '안전 무결성이 높은 섀시 도메인은 메시지 인증에 더해 도메인 분리·침입탐지(IDS)로 이중 방어한다.',
            'fix': "function(v){v.secoc.CH=true;}",
            'fixNote': 'CH(섀시) 버스에 SecOC 메시지 인증을 적용했습니다.',
        },
    ],
}


# ═══════════════════════════════════════════════════════════════
# LAB 2 — 진단(UDS) 공격 (T5/T9/T19/T20/T21)
#   미션마다 ECU 를 달리해 상태 격리. ISO 14229 표준 서비스만 사용.
# ═══════════════════════════════════════════════════════════════
def _ecu(name, bus, req, res, **kw):
    d = {'name': name, 'bus': bus, 'reqId': req, 'resId': res,
         'session': 'default', 'unlocked': False,
         'secAccess': {'present': False, 'algo': 'none'},
         'guarded': {'wdbi': True, 'rmba': True, 'wmba': True},
         'secureBoot': True, 'secureFlash': True, 'dids': {}, 'mem': {}, 'fwStrings': []}
    d.update(kw)
    return d

UDS_VEHICLE = {
    'brand': 'HANARO', 'model': 'EV9 (가상 차량)',
    'vin': 'KMHXX00XXP0000002',
    'buses': {'DIAG': {'name': '진단 CAN', 'speed': '500kbps'}},
    'secoc': {'DIAG': False},
    'frames': [],
    'ecus': {
        'GW': _ecu('중앙 게이트웨이', 'DIAG', '0x710', '0x718',
                   secAccess={'present': True, 'algo': 'xor', 'seed': '1A2B3C4D'}),
        'IMMO': _ecu('이모빌라이저/BCM', 'DIAG', '0x730', '0x738',
                     guarded={'wdbi': False, 'rmba': True, 'wmba': True},
                     dids={'F190': {'name': 'VIN', 'kind': 'vin'}}),
        'CLU': _ecu('계기(클러스터)', 'DIAG', '0x720', '0x728',
                    guarded={'wdbi': False, 'rmba': True, 'wmba': True},
                    dids={'F121': {'name': '주행거리(km)', 'value': '058231'}}),
        'ECM': _ecu('엔진제어', 'DIAG', '0x7E0', '0x7E8',
                    guarded={'wdbi': True, 'rmba': False, 'wmba': True},
                    mem={'0x6872': 'AF 3C 91 20 (소유자 전화번호 단편)', '*': '00 00'}),
        'TCU': _ecu('텔레매틱스 제어', 'DIAG', '0x740', '0x748',
                    guarded={'wdbi': True, 'rmba': True, 'wmba': False}),
    },
}

UDS_LAB = {
    'key': 'uds', 'file': 'sim-auto-uds.html', 'code': 'AUTO-PT-UDS',
    'title': '진단(UDS) 공격', 'r155cat': 'R155 Annex5 · 데이터/코드',
    'desc': 'ISO 14229 진단 프로토콜(UDS)로 ECU 를 두드립니다. 보안 접근(0x27) 우회, VIN·주행거리 '
            '위변조(0x2E), 임의 메모리 읽기·쓰기(0x23/0x3D), 로그 삭제(0x31)를 직접 시도하고, '
            '세션·보안접근·쓰기보호로 방어합니다.',
    'vehicle': UDS_VEHICLE,
    'missions': [
        {
            'id': 'UDS-01', 'risk': 5, 'title': 'Security Access(0x27) seed/key 우회',
            'r155': 'R155 Annex5 · T9 권한 상승 (보안 접근 우회)',
            'brief': '진단 보안 접근은 seed 를 받아 key 를 되돌려주는 절차입니다. key 계산이 <b>고정 상수·XOR</b>처럼 '
                     '약하면, 공격자가 seed 만으로 key 를 만들어 위험 서비스를 엽니다.',
            'try': 'uds GW session 03 → uds GW secaccess',
            'hint': 'secaccess 결과가 "성공(unlocked)"이면 취약, "실패(HSM)"면 양호.',
            'cmds': ['uds GW session 03', 'uds GW secaccess'],
            'options': [
                '보안 접근 성공 — seed 로부터 key 를 즉시 계산(약한 알고리즘)',
                '보안 접근 실패 — key 가 HSM 안에서 계산되어 seed 만으로 알 수 없음',
                '세션 진입 실패',
                'ECU 응답 없음',
            ],
            'evidence': ['보안 접근 성공 — seed 로부터 key 를 즉시 계산(약한 알고리즘)'],
            'verdict': "function(v){var a=v.ecus.GW.secAccess.algo;return (a==='aes'||a==='hsm')?'good':'vuln';}",
            'why': '게이트웨이의 seed/key 알고리즘이 약해(XOR 상수) seed 만으로 key 를 계산할 수 있습니다. '
                   '보안 접근이 뚫리면 그 뒤의 메모리·플래시 서비스가 전부 노출됩니다.',
            'ez': '자물쇠가 "숫자에 1 더하기" 규칙이면, 받은 숫자를 보고 누구나 열쇠를 만든다.',
            'defense': 'seed/key 를 HSM 안에서 강한 알고리즘(예: AES 기반 챌린지-응답)으로 계산하고, '
                       '실패 지연·시도 제한을 둔다. 키는 ECU 밖으로 나오지 않는다.',
            'fix': "function(v){v.ecus.GW.secAccess.algo='hsm';}",
            'fixNote': '게이트웨이 보안 접근을 HSM 기반 강한 알고리즘으로 교체했습니다.',
        },
        {
            'id': 'UDS-02', 'risk': 4, 'title': 'VIN 위변조 (WriteDataByIdentifier 0x2E)',
            'r155': 'R155 Annex5 · T20 데이터 조작 (A20.1 전자 ID 변경)',
            'brief': 'VIN(차대번호, DID F190)을 보안 접근 없이 덮어쓸 수 있으면 <b>차량 신원을 위조</b>할 수 있습니다. '
                     '도난 차량 세탁·통행료 회피 등에 악용됩니다.',
            'try': 'uds IMMO read F190 → uds IMMO write F190 HACKEDVIN00000000',
            'hint': 'write 결과가 "긍정응답(변경됨)"이면 취약, "securityAccessDenied"면 양호.',
            'cmds': ['uds IMMO read F190', 'uds IMMO write F190 HACKEDVIN00000000'],
            'options': [
                'VIN 쓰기 성공 — 보안 접근 없이 F190 이 변경됨',
                'VIN 쓰기 거부 — securityAccessDenied(먼저 보안 접근 필요)',
                'VIN 을 읽을 수 없음',
                '알 수 없는 DID',
            ],
            'evidence': ['VIN 쓰기 성공 — 보안 접근 없이 F190 이 변경됨'],
            'verdict': "function(v){return v.ecus.IMMO.guarded.wdbi?'good':'vuln';}",
            'why': '이모빌라이저 ECU 가 VIN 쓰기(0x2E F190)를 보안 접근 없이 허용합니다. '
                   '전자 신원 항목은 보안 접근 뒤에만, 또는 쓰기 자체를 금지해야 합니다.',
            'ez': '신분증 번호를 아무 확인 없이 아무나 고쳐 쓸 수 있게 둔 것과 같다.',
            'defense': 'VIN 등 전자 ID 쓰기 서비스는 보안 접근(0x27) 이후에만 허용하거나, 생산 이후 쓰기 잠금(write-protect)한다.',
            'fix': "function(v){v.ecus.IMMO.guarded.wdbi=true;}",
            'fixNote': 'VIN 쓰기(0x2E F190)에 보안 접근 요구를 걸었습니다.',
        },
        {
            'id': 'UDS-03', 'risk': 3, 'title': '주행거리계 조작 (Odometer DID F121)',
            'r155': 'R155 Annex5 · T20 데이터 조작 (A20.4 주행데이터 위조)',
            'brief': '주행거리(DID F121)를 보안 접근 없이 덮어쓰면 <b>중고차 주행거리 조작</b>이 됩니다. '
                     '소비자 피해·보증 사기와 직결됩니다.',
            'try': 'uds CLU read F121 → uds CLU write F121 000010',
            'hint': 'CLU(계기) write 결과를 보세요.',
            'cmds': ['uds CLU read F121', 'uds CLU write F121 000010'],
            'options': [
                '주행거리 쓰기 성공 — 보안 접근 없이 F121 이 변경됨',
                '주행거리 쓰기 거부 — securityAccessDenied',
                '주행거리를 읽을 수 없음',
                '계기 ECU 응답 없음',
            ],
            'evidence': ['주행거리 쓰기 성공 — 보안 접근 없이 F121 이 변경됨'],
            'verdict': "function(v){return v.ecus.CLU.guarded.wdbi?'good':'vuln';}",
            'why': '계기 ECU 가 주행거리 쓰기를 보안 접근 없이 허용합니다. 주행 데이터는 여러 소스와 대조·서명해 위조를 막아야 합니다.',
            'ez': '자동차의 "이만큼 달렸다"는 기록을 아무나 되돌려 쓸 수 있는 셈이다.',
            'defense': '주행거리 쓰기는 보안 접근 이후로 제한하고, 여러 ECU 값과 교차 검증하며 이력에 서명을 남긴다.',
            'fix': "function(v){v.ecus.CLU.guarded.wdbi=true;}",
            'fixNote': '주행거리 쓰기(0x2E F121)에 보안 접근 요구를 걸었습니다.',
        },
        {
            'id': 'UDS-04', 'risk': 4, 'title': '임의 메모리 읽기 (ReadMemoryByAddress 0x23)',
            'r155': 'R155 Annex5 · T19 데이터 추출 (A19.2 개인정보 / A19.3 키 추출)',
            'brief': '임의 주소 메모리를 보안 접근 없이 읽을 수 있으면 <b>개인정보·암호키</b>가 그대로 유출됩니다.',
            'try': 'uds ECM rmba 0x6872',
            'hint': 'rmba 결과가 실제 메모리 값을 내놓으면 취약, "securityAccessDenied"면 양호.',
            'cmds': ['uds ECM session 03', 'uds ECM rmba 0x6872'],
            'options': [
                '메모리 읽기 성공 — 보안 접근 없이 임의 주소의 민감정보 노출',
                '메모리 읽기 거부 — securityAccessDenied',
                '주소를 찾을 수 없음',
                'ECU 응답 없음',
            ],
            'evidence': ['메모리 읽기 성공 — 보안 접근 없이 임의 주소의 민감정보 노출'],
            'verdict': "function(v){return v.ecus.ECM.guarded.rmba?'good':'vuln';}",
            'why': '엔진 ECU 가 임의 주소 읽기(0x23)를 보안 접근 없이 허용해 메모리의 민감정보가 노출됩니다.',
            'ez': '금고 안을 확인 없이 아무나 들여다보게 열어 둔 것과 같다.',
            'defense': '메모리 접근 서비스(0x23/0x3D)는 보안 접근 뒤에만, 필요한 주소 범위로만 허용하고, 키·개인정보는 HSM/보호영역에 둔다.',
            'fix': "function(v){v.ecus.ECM.guarded.rmba=true;}",
            'fixNote': '임의 메모리 읽기(0x23)에 보안 접근 요구를 걸었습니다.',
        },
        {
            'id': 'UDS-05', 'risk': 4, 'title': '이벤트 로그 삭제 (RoutineControl 0x31)',
            'r155': 'R155 Annex5 · T21 데이터/코드 삭제 (A21.1 로그 삭제)',
            'brief': '메모리 쓰기·루틴(0x31 eraseMemory)이 보안 접근 없이 열려 있으면 <b>공격 흔적(이벤트 로그)을 삭제</b>할 수 있습니다.',
            'try': 'uds TCU erase',
            'hint': 'erase 결과가 "긍정응답"이면 취약, "securityAccessDenied"면 양호.',
            'cmds': ['uds TCU erase', 'uds TCU wmba 0x2000 00'],
            'options': [
                '로그/메모리 삭제 성공 — 보안 접근 없이 흔적 삭제 가능',
                '삭제 거부 — securityAccessDenied',
                '루틴을 찾을 수 없음',
                'ECU 응답 없음',
            ],
            'evidence': ['로그/메모리 삭제 성공 — 보안 접근 없이 흔적 삭제 가능'],
            'verdict': "function(v){return v.ecus.TCU.guarded.wmba?'good':'vuln';}",
            'why': '텔레매틱스 ECU 가 메모리 쓰기·삭제 루틴을 보안 접근 없이 허용해 로그를 지울 수 있습니다. '
                   '침해 대응·포렌식이 무력화됩니다.',
            'ez': 'CCTV 녹화본을 아무나 지울 수 있으면 무슨 일이 있었는지 아무도 모른다.',
            'defense': '쓰기·삭제 루틴은 보안 접근 뒤에만 허용하고, 이벤트 로그는 추가전용(append-only)·원격 백업으로 보존한다.',
            'fix': "function(v){v.ecus.TCU.guarded.wmba=true;}",
            'fixNote': '메모리 쓰기·삭제 루틴에 보안 접근 요구를 걸었습니다.',
        },
    ],
}


# ═══════════════════════════════════════════════════════════════
# LAB 3 — 무선/원격 공격 (T16 외부 연결성)
# ═══════════════════════════════════════════════════════════════
RF_VEHICLE = {
    'brand': 'HANARO', 'model': 'EV9 (가상 차량)',
    'vin': 'KMHXX00XXP0000003',
    'buses': {}, 'secoc': {}, 'frames': [], 'ecus': {},
    'keyfob': {'type': 'fixed', 'pke': True, 'distanceBound': False},
    'gps': {'plausibility': False},
    'telematics': {'authRemote': False},
}

RF_LAB = {
    'key': 'rf', 'file': 'sim-auto-rf.html', 'code': 'AUTO-PT-RF',
    'title': '무선·원격 공격', 'r155cat': 'R155 Annex5 · 외부 연결성',
    'desc': '무선 키(RF/PKE), GPS, 텔레매틱스 원격 기능을 시험합니다. 고정코드 리플레이, 릴레이 공격, '
            'GPS 스푸핑, 무인증 원격 명령을 직접 실행해 보고 롤링코드·거리한정·위치 타당성·원격 인증으로 방어합니다.',
    'vehicle': RF_VEHICLE,
    'missions': [
        {
            'id': 'RF-01', 'risk': 4, 'title': '무선 키 고정코드 리플레이',
            'r155': 'R155 Annex5 · T16 근거리 무선 (A16.3 리플레이)',
            'brief': '무선 키가 <b>고정 코드</b>를 쓰면, 잠금/해제 신호를 한 번 캡처(SDR 장비)해 그대로 재전송하면 문이 열립니다.',
            'try': 'rf record → rf replay',
            'hint': 'replay 결과가 "성공(고정코드)"이면 취약, "무시됨(롤링코드)"이면 양호.',
            'cmds': ['rf record', 'rf replay'],
            'options': [
                '재전송 성공 — 고정코드라 캡처한 신호가 그대로 통함',
                '재전송 무시됨 — 롤링코드라 캡처 신호가 만료됨',
                '캡처 실패',
                '이 차량은 무선 키가 없음',
            ],
            'evidence': ['재전송 성공 — 고정코드라 캡처한 신호가 그대로 통함'],
            'verdict': "function(v){return v.keyfob.type==='rolling'?'good':'vuln';}",
            'why': '무선 키가 고정 코드를 써서, 한 번 캡처한 해제 신호를 재전송하면 다시 열립니다.',
            'ez': '매번 같은 비밀번호를 외치는 문이라, 한 번 엿들으면 언제든 다시 들어갈 수 있다.',
            'defense': '매 사용마다 코드가 바뀌는 롤링코드(또는 챌린지-응답)를 쓴다. 재전송된 옛 코드는 거부된다.',
            'fix': "function(v){v.keyfob.type='rolling';}",
            'fixNote': '무선 키를 롤링코드 방식으로 교체했습니다.',
        },
        {
            'id': 'RF-02', 'risk': 4, 'title': '스마트키(PKE) 릴레이 공격',
            'r155': 'R155 Annex5 · T16 원격 조작 (A16.1 원격 진입)',
            'brief': '스마트 진입(PKE)은 키가 가까이 있으면 자동으로 열립니다. 공격자 둘이 키↔차량 신호를 <b>중계</b>하면 '
                     '키가 집 안에 있어도 차 옆에 있는 것처럼 속여 문을 열고 시동을 겁니다. 롤링코드로도 못 막습니다.',
            'try': 'rf relay',
            'hint': 'relay 결과가 "성공"이면 취약, "차단(거리 한정)"이면 양호. (롤링코드는 릴레이를 못 막음)',
            'cmds': ['rf relay'],
            'options': [
                '릴레이 성공 — 키↔차량 신호를 중계해 근접을 위조',
                '릴레이 차단 — 거리 한정(UWB)으로 실제 근접을 검증',
                '이 차량은 PKE 가 아님',
                '재전송 무시됨(롤링코드)',
            ],
            'evidence': ['릴레이 성공 — 키↔차량 신호를 중계해 근접을 위조'],
            'verdict': "function(v){return v.keyfob.distanceBound?'good':'vuln';}",
            'why': 'PKE 가 신호 세기만 보고 근접을 판단해, 신호를 중계하면 키가 멀리 있어도 열립니다. '
                   '롤링코드는 리플레이는 막아도 릴레이는 못 막습니다.',
            'ez': '문이 "목소리가 가까이 들리면 열어줌" 이라면, 확성기로 멀리 있는 주인 목소리를 옆에서 틀어주면 열린다.',
            'defense': 'UWB 등 거리 한정(distance bounding)으로 키의 실제 물리 거리를 측정한다. 사용자 모션 인증(잠들면 비활성)도 보완책.',
            'fix': "function(v){v.keyfob.distanceBound=true;}",
            'fixNote': 'PKE 에 UWB 거리 한정을 적용했습니다.',
        },
        {
            'id': 'RF-03', 'risk': 3, 'title': 'GPS 스푸핑',
            'r155': 'R155 Annex5 · T16 센서 간섭 (A16.3)',
            'brief': '위조 GPS 신호(SDR 장비)를 쏘면 차량이 <b>가짜 위치</b>를 믿습니다. 내비·지오펜스·긴급통화 위치가 틀어집니다.',
            'try': 'gps spoof 37.0,127.0',
            'hint': 'gps 결과가 "성공(반영)"이면 취약, "완화(교차검증)"면 양호.',
            'cmds': ['gps spoof 37.0,127.0'],
            'options': [
                'GPS 스푸핑 성공 — 위조 좌표가 그대로 반영됨',
                'GPS 스푸핑 완화 — 위치 타당성 교차검증으로 거부',
                'GPS 인터페이스 없음',
                '좌표 형식 오류',
            ],
            'evidence': ['GPS 스푸핑 성공 — 위조 좌표가 그대로 반영됨'],
            'verdict': "function(v){return v.gps.plausibility?'good':'vuln';}",
            'why': 'GPS 위치를 그대로 신뢰해 위조 좌표가 반영됩니다. 위성 신호는 인증이 없어 스푸핑에 취약합니다.',
            'ez': '내비가 "하늘에서 들리는 위치 안내"를 무조건 믿으면, 가짜 방송으로 엉뚱한 곳에 있다고 속일 수 있다.',
            'defense': '속도·관성(IMU)·맵매칭과 교차 검증해 급변·물리적으로 불가능한 좌표를 거부한다. 다중 위성군·인증 신호를 활용한다.',
            'fix': "function(v){v.gps.plausibility=true;}",
            'fixNote': 'GPS 위치에 타당성 교차검증을 적용했습니다.',
        },
        {
            'id': 'RF-04', 'risk': 4, 'title': '텔레매틱스 원격 명령 무인증',
            'r155': 'R155 Annex5 · T16 원격 조작 (A16.1 원격키/텔레매틱스)',
            'brief': '앱·서버를 거치는 원격 잠금해제/시동이 <b>소유자 인증을 제대로 하지 않으면</b>, 공격자가 원격으로 차량을 조작합니다.',
            'try': 'remote unlock',
            'hint': 'remote 결과가 "성공(무인증)"이면 취약, "거부(인증 검증)"면 양호.',
            'cmds': ['remote unlock', 'remote start'],
            'options': [
                '원격 명령 성공 — 인증 없이 명령이 차량에 전달됨',
                '원격 명령 거부 — 소유자 인증·토큰 검증',
                '텔레매틱스 정보 없음',
                '네트워크 분리됨',
            ],
            'evidence': ['원격 명령 성공 — 인증 없이 명령이 차량에 전달됨'],
            'verdict': "function(v){return v.telematics.authRemote?'good':'vuln';}",
            'why': '텔레매틱스 원격 명령이 소유자 인증 없이 전달됩니다. 원격 기능은 편의만큼 인증이 중요합니다.',
            'ez': '집 현관을 여는 앱이 로그인·본인확인 없이 "열어" 버튼만 있으면 누구나 연다.',
            'defense': '원격 명령마다 강한 소유자 인증(토큰·MFA)과 서버-차량 상호 인증, 명령 서명·재전송 방지를 적용한다.',
            'fix': "function(v){v.telematics.authRemote=true;}",
            'fixNote': '텔레매틱스 원격 명령에 소유자 인증·토큰 검증을 적용했습니다.',
        },
    ],
}


# ═══════════════════════════════════════════════════════════════
# LAB 4 — ECU 물리·펌웨어·앱 공격 (T12/T17/T18/T22/T26/T28)
# ═══════════════════════════════════════════════════════════════
ECU_VEHICLE = {
    'brand': 'HANARO', 'model': 'EV9 (가상 차량)',
    'vin': 'KMHXX00XXP0000004',
    'buses': {'DIAG': {'name': '진단 CAN', 'speed': '500kbps'}},
    'secoc': {'DIAG': False},
    'frames': [],
    'ecus': {
        'IVI': _ecu('인포테인먼트', 'DIAG', '0x760', '0x768',
                    secureBoot=True, secureFlash=False, signedFw=False,
                    fwStrings=['fw build 2023.11', 'WIFI_PSK=hanaro1234',
                               'AES_KEY=00112233445566778899aabbccddeeff']),
    },
    'obd': {'open': True, 'secureDebug': False},
    'jtag': {'present': True, 'secureDebug': False},
    'usb': {'autorun': True, 'mountExec': True, 'inputValidated': False},
    'bt': {'version': '4.2', 'oneDayPatched': False, 'nameSanitized': False},
}

ECU_LAB = {
    'key': 'ecu', 'file': 'sim-auto-ecu.html', 'code': 'AUTO-PT-ECU',
    'title': 'ECU 물리·펌웨어 공격', 'r155cat': 'R155 Annex5 · 외부/업데이트/잠재취약',
    'desc': 'ECU 하드웨어와 펌웨어를 시험합니다. JTAG/OBD 디버그 포트, secure flash 부재로 인한 위조 펌웨어, '
            '펌웨어 하드코딩 키 노출, USB 실행/퍼징, Bluetooth 취약점을 직접 다루고 secure boot/flash·HSM·'
            '입력검증으로 방어합니다.',
    'vehicle': ECU_VEHICLE,
    'missions': [
        {
            'id': 'ECU-01', 'risk': 4, 'title': 'JTAG 디버그 포트 개방',
            'r155': 'R155 Annex5 · T18 외부 인터페이스 (A18.1 디버그 포트)',
            'brief': '보드의 JTAG 포트가 잠기지 않으면 <b>메모리 덤프·동적 디버깅</b>으로 펌웨어와 비밀을 통째로 가져갑니다.',
            'try': 'jtag connect',
            'hint': 'jtag 결과가 "성공"이면 취약, "잠김(secure debug)"이면 양호.',
            'cmds': ['jtag connect'],
            'options': [
                'JTAG 연결 성공 — 디버그 포트로 메모리 덤프·디버깅 가능',
                'JTAG 잠김 — secure debug 로 차단',
                '보드에 디버그 포트 없음',
                'OBD 포트 잠김',
            ],
            'evidence': ['JTAG 연결 성공 — 디버그 포트로 메모리 덤프·디버깅 가능'],
            'verdict': "function(v){return v.jtag.secureDebug?'good':'vuln';}",
            'why': 'JTAG 디버그가 열려 있어 펌웨어 덤프·동적 분석이 가능합니다. 양산 ECU 는 디버그를 잠가야 합니다.',
            'ez': '기계 뒤판 나사를 안 잠가 두면 누구나 열어 속을 뜯어본다.',
            'defense': '양산 단계에서 디버그 포트를 비활성화하거나 인증 기반 secure debug 로 잠근다. 포트 자체를 두지 않는 것이 최선.',
            'fix': "function(v){v.jtag.secureDebug=true;}",
            'fixNote': 'JTAG 에 secure debug(인증 필요)를 적용했습니다.',
        },
        {
            'id': 'ECU-02', 'risk': 4, 'title': 'OBD 무보호 진단 접근',
            'r155': 'R155 Annex5 · T18 진단 접근 (A18.3 OBD 동글)',
            'brief': 'OBD 포트의 진단 요청이 게이트웨이에서 걸러지지 않고 <b>내부망으로 무제한 전달</b>되면, '
                     '동글 하나로 제어망까지 도달합니다.',
            'try': 'obd connect',
            'hint': 'obd 결과가 "무제한 전달"이면 취약, "진단만 가능"이면 양호.',
            'cmds': ['obd connect'],
            'options': [
                'OBD 진단 요청이 제어망으로 무제한 전달됨',
                'OBD 는 진단만 가능(위험 서비스는 보안 접근 뒤)',
                'OBD 포트 없음',
                'JTAG 잠김',
            ],
            'evidence': ['OBD 진단 요청이 제어망으로 무제한 전달됨'],
            'verdict': "function(v){return v.obd.secureDebug?'good':'vuln';}",
            'why': 'OBD 진단 접근을 게이트웨이가 통제하지 않아 물리 접근만으로 제어망에 닿습니다.',
            'ez': '정비용 점검구가 사실은 건물 전체로 통하는 뒷문이면, 점검한다며 아무 데나 들어갈 수 있다.',
            'defense': 'OBD↔내부망 사이 게이트웨이가 진단 메시지를 필터링·인증하고, 위험 서비스는 보안 접근 뒤에만 연다.',
            'fix': "function(v){v.obd.secureDebug=true;}",
            'fixNote': 'OBD 진단 접근에 게이트웨이 통제·보안 접근을 적용했습니다.',
        },
        {
            'id': 'ECU-03', 'risk': 5, 'title': 'Secure Flash 부재 — 위조 펌웨어 기록',
            'r155': 'R155 Annex5 · T12 업데이트 훼손 (A12.2 로컬 플래시)',
            'brief': 'ECU 플래시에 <b>서명·무결성 검증</b>이 없으면, 위조 펌웨어를 그대로 기록해 차량을 공격자 의도대로 동작시킵니다.',
            'try': 'uds IVI flash',
            'hint': 'flash 결과가 "성공(서명 없이 기록)"이면 취약, "실패(secure flash)"면 양호.',
            'cmds': ['uds IVI flash'],
            'options': [
                '위조 펌웨어 기록 성공 — 서명 검증 없이 플래시됨',
                '위조 펌웨어 거부 — secure flash 서명·무결성 검증',
                'ECU 를 찾을 수 없음',
                '보안 접근 필요',
            ],
            'evidence': ['위조 펌웨어 기록 성공 — 서명 검증 없이 플래시됨'],
            'verdict': "function(v){var e=v.ecus.IVI;return (e.secureFlash||(e.secureBoot&&e.signedFw))?'good':'vuln';}",
            'why': '인포테인먼트 ECU 가 서명 검증 없이 펌웨어를 기록합니다. 위조 펌웨어가 그대로 실행됩니다.',
            'ez': '누가 보낸 건지 확인 안 하고 받은 앱을 그대로 설치하는 것과 같다.',
            'defense': 'secure flash(서명·무결성 검증)와 secure boot(부팅 시 서명 검증)를 함께 적용하고, 서명 키는 HSM 에 둔다.',
            'fix': "function(v){v.ecus.IVI.secureFlash=true;}",
            'fixNote': '인포테인먼트 ECU 에 secure flash 서명·무결성 검증을 적용했습니다.',
        },
        {
            'id': 'ECU-04', 'risk': 4, 'title': '펌웨어 하드코딩 키 노출',
            'r155': 'R155 Annex5 · T19 키 추출 (A19.3) / T26 암호 오용',
            'brief': '펌웨어에서 <b>하드코딩된 비밀키·비밀번호</b>가 문자열로 그대로 보이면, 추출한 펌웨어에서 키를 뽑아냅니다.',
            'try': 'fw strings IVI',
            'hint': 'fw strings 결과에 KEY/PSK 가 보이면 취약, 안 보이면(HSM 보관) 양호.',
            'cmds': ['fw strings IVI'],
            'options': [
                '하드코딩된 비밀키/자격증명이 펌웨어에 노출됨',
                '비밀키가 보이지 않음(HSM 보관·심볼 제거)',
                '펌웨어를 읽을 수 없음',
                'ECU 없음',
            ],
            'evidence': ['하드코딩된 비밀키/자격증명이 펌웨어에 노출됨'],
            'verdict': "function(v){var s=(v.ecus.IVI.fwStrings||[]).join(' ');return /key|secret|passwd|password|token|psk/i.test(s)?'vuln':'good';}",
            'why': '펌웨어에 Wi‑Fi 비밀번호·AES 키가 평문으로 박혀 있어 문자열 추출만으로 노출됩니다. 난독화·심볼 제거는 보조 수단일 뿐입니다.',
            'ez': '금고 열쇠를 금고 표면에 유성펜으로 적어 둔 셈이다.',
            'defense': '비밀키는 코드에 넣지 않고 HSM/보안 저장소에 두고 런타임에만 참조한다. 자격증명은 기기별로 다르게 프로비저닝한다.',
            'fix': "function(v){v.ecus.IVI.fwStrings=['fw build 2024.1','(비밀키는 HSM 에 보관)'];}",
            'fixNote': '하드코딩 키를 제거하고 HSM 보관으로 바꿨습니다.',
        },
        {
            'id': 'ECU-05', 'risk': 3, 'title': 'USB 실행권한 — 저장 실행파일 동작',
            'r155': 'R155 Annex5 · T18 외부 인터페이스 (A18.1/A18.2 USB)',
            'brief': 'USB 마운트가 <b>실행권한(exec)</b>으로 붙으면, 저장해 둔 실행파일이 인포테인먼트에서 동작해 발판이 됩니다.',
            'try': 'usb plug payload.sh',
            'hint': 'usb plug 결과가 "실행됨"이면 취약, "실행 안 됨"이면 양호.',
            'cmds': ['usb plug payload.sh'],
            'options': [
                'USB 저장 실행파일이 실행됨 — 마운트에 실행권한이 있음',
                'USB 파일이 실행되지 않음(noexec)',
                'USB 인터페이스 없음',
                '자동 재생만 됨',
            ],
            'evidence': ['USB 저장 실행파일이 실행됨 — 마운트에 실행권한이 있음'],
            'verdict': "function(v){return v.usb.mountExec?'vuln':'good';}",
            'why': 'USB 마운트에 실행권한이 있어 저장된 실행파일이 동작합니다. 외부 저장소는 실행권한 없이 마운트해야 합니다.',
            'ez': '방문객이 들고 온 USB 를 꽂자마자 그 안의 프로그램이 자동 실행되게 둔 것과 같다.',
            'defense': '외부 저장소는 noexec·nosuid 로 마운트하고, 미디어 파서를 샌드박스에 격리하며 파일 형식을 엄격히 검증한다.',
            'fix': "function(v){v.usb.mountExec=false;}",
            'fixNote': 'USB 마운트를 noexec 로 바꿨습니다.',
        },
        {
            'id': 'ECU-06', 'risk': 3, 'title': 'USB 퍼징 — 입력 검증 부재',
            'r155': 'R155 Annex5 · T28 SW 버그 (A28.1) / T18',
            'brief': '변조된 미디어·USB 패킷에 <b>입력 검증이 없으면</b> 인포테인먼트가 재부팅·크래시합니다. 취약점 발판이 됩니다.',
            'try': 'usb fuzz',
            'hint': 'usb fuzz 결과가 "취약(재부팅/크래시)"이면 취약, "안정"이면 양호.',
            'cmds': ['usb fuzz'],
            'options': [
                'USB 퍼징에 인포테인먼트가 재부팅/크래시함(입력 검증 부재)',
                'USB 퍼징에도 안정적임(입력 검증 있음)',
                'USB 인터페이스 없음',
                '실행파일이 동작함',
            ],
            'evidence': ['USB 퍼징에 인포테인먼트가 재부팅/크래시함(입력 검증 부재)'],
            'verdict': "function(v){return v.usb.inputValidated?'good':'vuln';}",
            'why': '미디어/USB 입력 검증이 없어 변조 입력에 크래시합니다. 크래시는 메모리 손상 취약점으로 이어질 수 있습니다.',
            'ez': '엉터리로 적힌 서류를 받고도 검토 없이 처리하다 담당자가 뻗어버리는 셈이다.',
            'defense': '모든 외부 입력(미디어 헤더·USB 디스크립터)을 경계 검사·형식 검증하고, 파서를 최신 상태로 유지하며 크래시 시 격리·복구한다.',
            'fix': "function(v){v.usb.inputValidated=true;}",
            'fixNote': 'USB/미디어 입력 검증을 적용했습니다.',
        },
        {
            'id': 'ECU-07', 'risk': 3, 'title': 'Bluetooth 미패치 취약점(1-day)',
            'r155': 'R155 Annex5 · T17 3rd party/스택 (A17.1) / T28',
            'brief': 'Bluetooth 스택에 <b>알려진 취약점 패치가 안 되어</b> 있으면, 공개된 1-day 공격으로 코드 실행이 됩니다.',
            'try': 'bt exploit',
            'hint': 'bt exploit 결과가 "성공(미패치)"이면 취약, "차단(패치)"이면 양호.',
            'cmds': ['bt exploit', 'bt pair PoC%x%x'],
            'options': [
                'Bluetooth 1-day 공격 성공 — 미패치 스택에서 코드 실행',
                'Bluetooth 1-day 차단 — 패치 적용됨',
                'Bluetooth 인터페이스 없음',
                '페어링만 됨',
            ],
            'evidence': ['Bluetooth 1-day 공격 성공 — 미패치 스택에서 코드 실행'],
            'verdict': "function(v){return v.bt.oneDayPatched?'good':'vuln';}",
            'why': 'Bluetooth 스택이 알려진 취약점에 패치되지 않아 공개 익스플로잇이 통합니다. 무선 스택은 패치 관리가 핵심입니다.',
            'ez': '이미 널리 알려진 자물쇠 결함을 고치지 않고 그대로 쓰는 셈이다.',
            'defense': '무선 스택(BT/Wi‑Fi)을 최신 패치로 유지하고, SBOM 으로 구성요소·버전을 추적하며 취약 버전을 차단한다.',
            'fix': "function(v){v.bt.oneDayPatched=true;}",
            'fixNote': 'Bluetooth 스택에 알려진 취약점 패치를 적용했습니다.',
        },
    ],
}


# ═══════════════════════════════════════════════════════════════
# LAB 5 — 백엔드·OTA·개인정보 (T1/T2/T3/T12/T13/T29/T31)
# ═══════════════════════════════════════════════════════════════
BE_VEHICLE = {
    'brand': 'HANARO', 'model': 'Connected Cloud (가상 백엔드)',
    'vin': 'KMHXX00XXP0000005',
    'buses': {}, 'secoc': {}, 'frames': [], 'ecus': {},
    'backend': {'reachable': True, 'openPorts': ['22/ssh(불필요)', '443/https', '8080/http(관리)'],
                'sqli': True, 'dosProtected': False, 'segmented': False, 'firmwareExposed': True},
    'ota': {'signed': False, 'encrypted': False, 'rollback': False},
    'privacy': {'wipedOnHandover': False},
}

BE_LAB = {
    'key': 'backend', 'file': 'sim-auto-backend.html', 'code': 'AUTO-PT-BE',
    'title': '백엔드·OTA·개인정보', 'r155cat': 'R155 Annex5 · 백엔드/업데이트',
    'desc': '차량 백엔드 서버와 OTA 업데이트, 개인정보를 시험합니다. 서버 무단접근(SQLi), 위조 펌웨어 OTA, '
            '업데이트 서버 DoS, 네트워크 분리 미흡, 중고 이전 시 개인정보 잔존을 직접 확인하고 방어합니다.',
    'vehicle': BE_VEHICLE,
    'missions': [
        {
            'id': 'BE-01', 'risk': 5, 'title': '백엔드 서버 무단접근 (SQLi)',
            'r155': 'R155 Annex5 · T1 서버 무단접근 (A1.2 SQLi)',
            'brief': '차량 백엔드가 <b>SQL 인젝션</b>에 취약하면, 인증 우회·차량 데이터 대량 추출이 가능하고 '
                     '서버를 발판으로 차량에 명령을 보낼 수도 있습니다.',
            'try': 'net scan → net sqli',
            'hint': 'net sqli 결과가 "성공"이면 취약, "실패(바인딩)"면 양호.',
            'cmds': ['net scan', 'net sqli'],
            'options': [
                'SQLi 성공 — 인증 우회·데이터 추출 가능',
                'SQLi 실패 — 파라미터 바인딩/검증됨',
                '서버에 도달 불가',
                '포트가 닫혀 있음',
            ],
            'evidence': ['SQLi 성공 — 인증 우회·데이터 추출 가능'],
            'verdict': "function(v){return v.backend.sqli?'vuln':'good';}",
            'why': '백엔드 API 가 입력을 그대로 질의에 넣어 SQL 인젝션이 됩니다. 서버 침해는 연결된 차량 전체 위협으로 번집니다.',
            'ez': '주문서에 적힌 말을 그대로 명령으로 실행하는 주방이라, "재료 다 내놔" 라고 적으면 그대로 따른다.',
            'defense': '모든 질의를 파라미터 바인딩(prepared statement)으로 처리하고 입력을 검증한다. 서버는 최신 패치·최소 권한·WAF 로 하드닝한다.',
            'fix': "function(v){v.backend.sqli=false;}",
            'fixNote': '백엔드 질의를 파라미터 바인딩으로 바꾸고 입력 검증을 적용했습니다.',
        },
        {
            'id': 'BE-02', 'risk': 5, 'title': 'OTA 위조 펌웨어 배포 (서명 검증 부재)',
            'r155': 'R155 Annex5 · T12 업데이트 훼손 (A12.1 OTA)',
            'brief': 'OTA 펌웨어에 <b>서명·무결성 검증</b>이 없으면, 공격자가 위조 펌웨어를 배포해 차량에 설치시킵니다. 전 차량 규모의 위협입니다.',
            'try': 'ota push evil.fw',
            'hint': 'ota push 결과가 "성공(서명 없이 설치)"이면 취약, "거부(서명 검증)"면 양호.',
            'cmds': ['ota push evil.fw'],
            'options': [
                'OTA 위조 펌웨어 설치 성공 — 서명 검증 없음',
                'OTA 위조 펌웨어 거부 — 서명·무결성 검증',
                'OTA 정보 없음',
                '업데이트 서버 다운',
            ],
            'evidence': ['OTA 위조 펌웨어 설치 성공 — 서명 검증 없음'],
            'verdict': "function(v){return v.ota.signed?'good':'vuln';}",
            'why': 'OTA 펌웨어를 서명 검증 없이 설치해 위조 이미지가 통합니다. 업데이트 경로는 가장 강하게 지켜야 합니다.',
            'ez': '누가 보냈는지 확인 안 하는 자동 업데이트는, 사칭한 사람이 보낸 것도 그대로 깔아 버린다.',
            'defense': 'OTA 이미지에 공급자 서명·무결성 검증(secure update)을 적용하고, 서명 키는 HSM 에 두며 롤백·버전 다운그레이드를 막는다.',
            'fix': "function(v){v.ota.signed=true;}",
            'fixNote': 'OTA 에 서명·무결성 검증을 적용했습니다.',
        },
        {
            'id': 'BE-03', 'risk': 4, 'title': '업데이트 서버 DoS — 배포 거부',
            'r155': 'R155 Annex5 · T13 정상 업데이트 거부 (A13.1 DoS)',
            'brief': '업데이트 서버가 <b>DoS 에 약하면</b>, 공격자가 서버를 마비시켜 중요 보안 패치 배포를 막습니다(취약점 방치 유도).',
            'try': 'net dos',
            'hint': 'net dos 결과가 "성공(서비스 정지)"이면 취약, "완화"면 양호.',
            'cmds': ['net dos'],
            'options': [
                'DoS 성공 — 업데이트/텔레매틱스 서비스가 정지됨',
                'DoS 완화 — 속도제한·이중화로 유지됨',
                '서버 정보 없음',
                '네트워크 분리됨',
            ],
            'evidence': ['DoS 성공 — 업데이트/텔레매틱스 서비스가 정지됨'],
            'verdict': "function(v){return v.backend.dosProtected?'good':'vuln';}",
            'why': '업데이트 서버가 DoS 완화가 없어 마비됩니다. 보안 패치 배포가 막히면 알려진 취약점이 방치됩니다.',
            'ez': '소방서 전화를 계속 울려 마비시키면, 정작 불이 났을 때 도움을 못 받는 셈이다.',
            'defense': '속도 제한·CDN·이중화·자동 확장으로 가용성을 확보하고, 시스템 장애 시 복구 절차를 둔다.',
            'fix': "function(v){v.backend.dosProtected=true;}",
            'fixNote': '업데이트 서버에 속도제한·이중화를 적용했습니다.',
        },
        {
            'id': 'BE-04', 'risk': 5, 'title': '네트워크 분리 미흡 — 서버→차량 횡적 이동',
            'r155': 'R155 Annex5 · T29 네트워크 설계 (A29.2 분리 우회)',
            'brief': '서버망과 차량 제어망이 <b>분리되어 있지 않으면</b>, 서버 침해가 곧바로 차량 제어망으로 번집니다.',
            'try': 'net seg',
            'hint': 'net seg 결과가 "취약(횡적 이동 가능)"이면 취약, "분리됨"이면 양호.',
            'cmds': ['net scan', 'net seg'],
            'options': [
                '네트워크 분리 취약 — 서버에서 차량 제어망으로 횡적 이동 가능',
                '네트워크 분리됨 — 서버 침해가 제어망으로 전파되지 않음',
                '서버 정보 없음',
                'SQLi 실패',
            ],
            'evidence': ['네트워크 분리 취약 — 서버에서 차량 제어망으로 횡적 이동 가능'],
            'verdict': "function(v){return v.backend.segmented?'good':'vuln';}",
            'why': '서버망과 제어망이 분리되지 않아 서버 하나가 뚫리면 차량 제어까지 도달합니다.',
            'ez': '사무실과 금고방 사이 문이 없으면, 사무실에 들어온 사람이 금고까지 곧장 간다.',
            'defense': '망 분리·세그멘테이션·최소 권한 경로로 서버-차량 사이를 격리하고, 경계에 상호 인증·모니터링을 둔다.',
            'fix': "function(v){v.backend.segmented=true;}",
            'fixNote': '서버망과 차량 제어망을 분리(세그멘테이션)했습니다.',
        },
        {
            'id': 'BE-05', 'risk': 3, 'title': '중고 이전 시 개인정보 잔존',
            'r155': 'R155 Annex5 · T31 사용자 변경 시 정보 유출 (A31.1)',
            'brief': '차량 사용자가 바뀔 때 <b>이전 사용자 데이터가 소거되지 않으면</b>, 위치 이력·연락처·계정이 다음 사람에게 남습니다.',
            'try': 'handover',
            'hint': 'handover 결과가 "취약(데이터 잔존)"이면 취약, "양호(소거)"면 양호.',
            'cmds': ['handover'],
            'options': [
                '이전 사용자 데이터 잔존 — 위치·연락처·계정이 남음',
                '이전 사용자 데이터 소거됨',
                '개인정보 정보 없음',
                'OTA 미서명',
            ],
            'evidence': ['이전 사용자 데이터 잔존 — 위치·연락처·계정이 남음'],
            'verdict': "function(v){return v.privacy.wipedOnHandover?'good':'vuln';}",
            'why': '사용자 변경 시 개인정보 소거 절차가 없어 이전 사용자 데이터가 남습니다. 개인정보 보호 요구사항 위반입니다.',
            'ez': '중고폰을 초기화 없이 넘기면 사진·메시지가 다음 주인에게 그대로 넘어가는 셈이다.',
            'defense': '사용자 변경(반납·중고 이전) 시 개인정보·계정·키를 안전하게 소거하는 절차를 두고, 저장은 최소화·암호화한다.',
            'fix': "function(v){v.privacy.wipedOnHandover=true;}",
            'fixNote': '사용자 변경 시 개인정보 소거 절차를 적용했습니다.',
        },
        {
            'id': 'BE-06', 'risk': 3, 'title': 'OTA 평문 스니핑 — 펌웨어 복원',
            'r155': 'R155 Annex5 · T3 데이터 유출 / T19 펌웨어 추출',
            'brief': 'OTA 전송이 <b>평문</b>이면, 통신을 감청해 펌웨어 이미지를 복원하고 독점 코드·키를 추출합니다.',
            'try': 'ota sniff',
            'hint': 'ota sniff 결과가 "성공(복원)"이면 취약, "암호화(복원 불가)"면 양호.',
            'cmds': ['ota sniff'],
            'options': [
                'OTA 스니핑 성공 — 평문 전송이라 펌웨어 복원 가능',
                'OTA 스니핑 실패 — 암호화되어 복원 불가',
                'OTA 정보 없음',
                '서명 없음',
            ],
            'evidence': ['OTA 스니핑 성공 — 평문 전송이라 펌웨어 복원 가능'],
            'verdict': "function(v){return v.ota.encrypted?'good':'vuln';}",
            'why': 'OTA 전송이 평문이라 감청으로 펌웨어를 복원할 수 있습니다. 서명(무결성)과 암호화(기밀성)는 별개로 둘 다 필요합니다.',
            'ez': '택배 상자를 투명 비닐로 보내면 도중에 내용물을 그대로 베낄 수 있다.',
            'defense': 'OTA 전송을 TLS 등으로 암호화하고, 펌웨어 자체도 기밀이 필요하면 암호화한다. 서명(무결성)과 함께 적용한다.',
            'fix': "function(v){v.ota.encrypted=true;}",
            'fixNote': 'OTA 전송에 암호화를 적용했습니다.',
        },
    ],
}


LABS = [CAN_LAB, UDS_LAB, RF_LAB, ECU_LAB, BE_LAB]
