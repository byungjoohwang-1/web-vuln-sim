# -*- coding: utf-8 -*-
"""정보보호시스템(보안장비) 진단 실습 — 계정·인증 / 접근 통제

평가 기준의 구조(항목ID, 위험도, 판단기준, 판단방법, 평가대상 장비)를 참고했고
장비 설정·시나리오·해설은 교육용으로 새로 작성했다. 장비명은 가상 브랜드다.

의도적으로 '양호' 항목을 섞었다. 모든 항목이 취약한 실습은 출력을 읽지 않고
무조건 '취약'을 찍는 습관을 길러 준다. 실제 점검에서 제일 많이 하는 실수다.
"""

# ── 모의 장비: 방화벽/VPN 겸용 ────────────────────────────────
FW_DEVICE = {
    'name': 'fin-fw-01',
    'type': 'FW',
    'typeLabel': '방화벽 (VPN 겸용)',
    'configDate': '2026-09-15 09:12:04 KST',
}

FW_CFG = {
    'system': {
        'model': 'SENTRA SG-4200',
        'serial': 'SG42-2201-8871',
        'os': 'SentraOS 7.2.1',
        'build': '7.2.1-b4410',
        'role': 'Firewall / IPSec VPN',
        'uptime': '412 days 06:21',
        'eosDate': '2028-03-31',
        'eosPassed': False,
        'sigVersion': None,
        'sigDate': None,
    },
    'admins': [
        {'name': 'admin',   'role': 'super',    'shared': True,
         'lastLogin': '2026-09-15 08:41:12', 'pwChanged': '2023-11-02'},
        {'name': 'fw_ops',  'role': 'super',    'shared': True,
         'lastLogin': '2026-09-15 07:55:30', 'pwChanged': '2024-02-18'},
        {'name': 'audit',   'role': 'super',    'shared': False,
         'lastLogin': '2026-09-12 14:02:55', 'pwChanged': '2026-07-01'},
        {'name': 'nms',     'role': 'readonly', 'shared': False,
         'lastLogin': '2026-09-15 09:10:02', 'pwChanged': '2026-06-30'},
    ],
    'auth': {
        'defaultAccount': {'present': True, 'name': 'admin', 'passwordChanged': False},
        'password': {'minLength': 6, 'complexity': 'none', 'maxAgeDays': 0, 'reuseCheck': False},
        'lockout': {'enabled': False, 'threshold': 0, 'durationMin': 0},
        'session': {'lines': [
            {'name': 'console', 'timeoutMin': 0},
            {'name': 'ssh',     'timeoutMin': 10},
            {'name': 'web',     'timeoutMin': 60},
            {'name': 'monitor', 'timeoutMin': 0},
        ]},
    },
    'mgmt': {
        'protocols': [
            {'name': 'https',  'port': 443, 'enabled': True,  'encrypted': True},
            {'name': 'ssh',    'port': 22,  'enabled': True,  'encrypted': True},
            {'name': 'telnet', 'port': 23,  'enabled': True,  'encrypted': False},
            {'name': 'http',   'port': 80,  'enabled': True,  'encrypted': False},
        ],
        'allowedIps': [],
        'banner': False,
    },
    'snmp': {
        'enabled': True, 'version': 'v2c', 'community': 'public',
        'access': 'read-only', 'user': '',
        'secLevel': '', 'purpose': 'NMS 연동 (운영팀 상시 사용)',
    },
    'logging': {
        'enabled': True, 'loginSuccess': True, 'loginFail': False, 'configChange': True,
        'rawPacket': False, 'rawPacketSeverity': 0, 'retentionDays': 30,
        'remote': {'enabled': False, 'proto': '', 'host': '', 'port': 0, 'retentionDays': 0},
    },
    'ntp': {'enabled': True, 'servers': [
        {'host': '10.10.0.10', 'stratum': 3, 'state': 'synchronized'},
    ]},
    'interfaces': [
        {'name': 'eth0', 'zone': 'untrust',  'address': '203.0.113.10/29',  'state': 'up'},
        {'name': 'eth1', 'zone': 'trust',    'address': '10.20.0.1/16',     'state': 'up'},
        {'name': 'eth2', 'zone': 'dmz',      'address': '10.30.0.1/24',     'state': 'up'},
        {'name': 'eth3', 'zone': 'mgmt',     'address': '10.99.0.1/24',     'state': 'up'},
    ],
    'nat': [
        {'name': 'web-pub',   'original': '10.30.0.21',  'translated': '203.0.113.11', 'note': 'DMZ 웹'},
        {'name': 'batch-pub', 'original': '10.20.4.55',  'translated': '203.0.113.14', 'note': '내부 배치서버'},
    ],
    'policyDefault': 'deny',
    'rules': [],
    'services': [
        {'name': 'ssh',    'port': 22,  'enabled': True,  'purpose': '관리'},
        {'name': 'https',  'port': 443, 'enabled': True,  'purpose': '관리 웹'},
        {'name': 'telnet', 'port': 23,  'enabled': True,  'purpose': '-'},
        {'name': 'http',   'port': 80,  'enabled': True,  'purpose': '-'},
    ],
    'net': {'sourceRouting': True},
    'detect': {'groups': [], 'blockMode': 'n/a', 'hwBypass': False, 'blocks30d': None},
    'monitor': {
        'cpu': 38, 'memory': 61, 'sessions': 84120, 'sessionMax': 500000,
        'usageReview': False, 'usageReviewCycle': '', 'realtime': False,
        'alerting': [], 'logReview': False, 'logReviewCycle': '',
    },
    'backup': {
        'policy': False, 'policyCycle': '', 'log': False, 'logCycle': '',
        'last': 'never', 'dest': '-', 'integrity': False, 'integrityCycle': '',
    },
    'patch': {
        'latest': 'SentraOS 7.4.0', 'latestSig': None, 'review': False,
        'reviewCycle': '', 'advisoriesApplied': 2, 'advisoriesTotal': 7,
    },
    'change': {'procedure': False, 'requestForm': False, 'techReview': False,
               'recent': 14, 'unapproved': 6},
}

ALL6 = ['FW', 'VPN', 'IDS', 'IPS', 'DDoS', 'WAF']


# ── Lab 1 : 계정·인증 ─────────────────────────────────────────
ACCT_MISSIONS = [
    {
        'id': 'ISS-017', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 Default 계정 변경 여부',
        'brief': '장비를 사 오면 들어 있는 <b>공장 출하 계정</b>은 모델명만 알면 누구나 압니다. '
                 '설명서와 벤더 사이트에 그대로 적혀 있습니다.',
        'where': 'show admin 의 Factory default account 줄',
        'hint': '출하 계정이 아직 남아 있는지, 비밀번호는 바뀌었는지 두 가지를 같이 보세요.',
        'why': '출하 계정 admin 이 이름 그대로 남아 있고 비밀번호도 바뀌지 않았습니다. '
               '계정 이름을 바꾸거나 삭제하고, 관리자마다 자기 계정을 쓰게 해야 합니다.',
        'cmds': ['show admin'],
        'options': ['출하 계정 admin 이 이름·비밀번호 모두 그대로',
                    '출하 계정이 삭제됨',
                    'nms 계정이 readonly',
                    'audit 계정이 2026-07-01 에 비밀번호 변경'],
        'evidence': ['출하 계정 admin 이 이름·비밀번호 모두 그대로'],
        'verdict': "function(c){var d=c.get('auth.defaultAccount')||{};"
                   "return (d.present&&!d.passwordChanged)?'vuln':'good';}",
        'fix': "function(c){c.set('auth.defaultAccount',{present:false,name:'admin',passwordChanged:true});"
               "var a=c.get('admins');c.set('admins',a.filter(function(u){return u.name!=='admin';}));}",
        'fixNote': '출하 계정 admin 을 삭제했습니다. 관리자는 각자 계정으로 접속합니다.',
    },
    {
        'id': 'ISS-018', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 Default 비밀번호 및 복잡도 기준',
        'brief': '비밀번호 규칙이 느슨하면 <b>실패 제한이 없을 때</b> 대입 공격에 그대로 노출됩니다. '
                 '길이와 조합을 같이 봐야 합니다.',
        'where': 'show password-policy 의 min-length, complexity',
        'hint': '판단기준은 영문·숫자·특수문자를 섞어 8자리 이상입니다.',
        'why': '최소 길이가 6자이고 조합 규칙이 없습니다(none). 출하 비밀번호도 바뀌지 않은 상태라 '
               '두 가지가 겹쳐 있습니다. 8자리 이상 + 3종 조합으로 올려야 합니다.',
        'cmds': ['show password-policy', 'show admin'],
        'options': ['최소 길이 6자, 조합 규칙 없음',
                    '최소 길이 8자 이상 적용 중',
                    'reuse-check 가 꺼져 있음',
                    '잠금 임계값이 5회'],
        'evidence': ['최소 길이 6자, 조합 규칙 없음'],
        'verdict': "function(c){var p=c.get('auth.password')||{};"
                   "return (p.minLength>=8&&p.complexity&&p.complexity!=='none')?'good':'vuln';}",
        'fix': "function(c){c.set('auth.password.minLength',9);"
               "c.set('auth.password.complexity','alpha+digit+special');"
               "c.set('auth.defaultAccount.passwordChanged',true);}",
        'fixNote': '최소 9자 + 영문·숫자·특수문자 조합으로 바꿨습니다.',
    },
    {
        'id': 'ISS-019', 'risk': 5, 'appliesTo': ALL6,
        'title': '보안장비 계정 관리 적정성',
        'brief': '여러 사람이 <b>같은 계정 하나</b>로 접속하면, 사고가 났을 때 누가 했는지 '
                 '로그로 가릴 수 없습니다. 감사증적이 사실상 사라집니다.',
        'where': 'show admin 의 SHARED 열',
        'hint': '공용으로 표시된 계정이 몇 개인지 세어 보세요.',
        'why': 'admin 과 fw_ops 두 계정을 여러 관리자가 공용으로 씁니다. 개인별 계정을 주는 것이 원칙이고, '
               '공동 사용이 불가피하면 개인별 사용내역을 따로 기록·관리해야 합니다.',
        'cmds': ['show admin'],
        'options': ['admin·fw_ops 를 여러 관리자가 공용으로 사용',
                    '모든 계정이 개인별로 분리됨',
                    'audit 계정의 권한이 super',
                    'nms 계정의 최근 접속이 오늘'],
        'evidence': ['admin·fw_ops 를 여러 관리자가 공용으로 사용'],
        'verdict': "function(c){var a=c.get('admins')||[];"
                   "return a.some(function(u){return u.shared;})?'vuln':'good';}",
        'fix': "function(c){var a=c.get('admins')||[];"
               "var out=a.filter(function(u){return u.name!=='admin'&&u.name!=='fw_ops';});"
               "out.unshift({name:'park.fw',role:'super',shared:false,"
               "lastLogin:'2026-09-15 08:41:12',pwChanged:'2026-09-15'});"
               "out.unshift({name:'kim.fw',role:'super',shared:false,"
               "lastLogin:'2026-09-15 07:55:30',pwChanged:'2026-09-15'});"
               "c.set('admins',out);c.set('auth.defaultAccount',{present:false,name:'admin',passwordChanged:true});}",
        'fixNote': '공용 계정을 없애고 관리자 개인 계정(kim.fw, park.fw)으로 나눴습니다.',
    },
    {
        'id': 'ISS-020', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 계정별 권한 설정 여부',
        'brief': '모두에게 최고 권한을 주면 <b>실수 한 번이 곧 정책 변경</b>이 됩니다. '
                 '보는 일만 하는 계정에는 보는 권한만 줍니다.',
        'where': 'show admin 의 ROLE 열',
        'hint': '계정의 용도(이름)와 부여된 권한이 맞는지 하나씩 대조해 보세요.',
        'why': '감사 용도인 audit 계정에 super 권한이 있습니다. 감사자는 설정을 읽을 수만 있으면 되므로 '
               'readonly 로 충분합니다. 권한이 넓을수록 그 계정이 탈취됐을 때 잃는 것이 많습니다.',
        'cmds': ['show admin'],
        'options': ['audit 계정에 super 권한이 부여됨',
                    '모든 계정 권한이 용도에 맞음',
                    'nms 계정이 readonly',
                    'admin 계정이 공용'],
        'evidence': ['audit 계정에 super 권한이 부여됨'],
        'verdict': "function(c){var a=c.get('admins')||[];"
                   "return a.some(function(u){return u.name==='audit'&&u.role!=='readonly';})?'vuln':'good';}",
        'fix': "function(c){var a=c.get('admins')||[];a.forEach(function(u){"
               "if(u.name==='audit') u.role='readonly';});c.set('admins',a);}",
        'fixNote': 'audit 계정을 readonly 로 낮췄습니다.',
    },
    {
        'id': 'ISS-023', 'risk': 3, 'appliesTo': ALL6,
        'title': '로그인 실패횟수 제한 설정 여부',
        'brief': '실패 제한이 없으면 자동화 도구가 <b>시간만 들이면 계속 시도</b>할 수 있습니다. '
                 '비밀번호를 아무리 길게 해도 무제한 시도 앞에서는 시간문제입니다.',
        'where': 'show password-policy 의 lockout',
        'hint': '판단기준은 5회 이내입니다.',
        'why': '계정 잠금이 꺼져 있어 실패 횟수 제한이 걸리지 않습니다. 최소 길이 6자 규칙과 겹쳐서 '
               '대입 공격의 성공 가능성이 크게 올라갑니다. 5회 이내로 잠그도록 설정해야 합니다.',
        'cmds': ['show password-policy'],
        'options': ['계정 잠금이 비활성화 상태',
                    '잠금 임계값 5회로 설정됨',
                    '최소 길이가 6자',
                    'max-age 가 0'],
        'evidence': ['계정 잠금이 비활성화 상태'],
        'verdict': "function(c){var l=c.get('auth.lockout')||{};"
                   "return (l.enabled&&l.threshold>0&&l.threshold<=5)?'good':'vuln';}",
        'fix': "function(c){c.set('auth.lockout',{enabled:true,threshold:5,durationMin:10});}",
        'fixNote': '5회 실패 시 10분간 잠기도록 설정했습니다.',
    },
    {
        'id': 'ISS-040', 'risk': 3, 'appliesTo': ALL6,
        'title': '보안장비 비밀번호의 주기적인 변경 여부',
        'brief': '비밀번호를 한 번 만들고 <b>몇 년째 그대로</b>면, 어디선가 유출됐어도 계속 유효합니다. '
                 '유출을 눈치채지 못한 기간만큼 악용 기간이 됩니다.',
        'where': 'show password-policy 의 max-age, show admin 의 PW-CHANGED 열',
        'hint': '만료 정책과 실제 마지막 변경일을 같이 보세요. 판단기준은 분기별 1회 이상입니다.',
        'why': 'max-age 가 0 이라 만료가 없고, admin 은 2023-11-02 이후 3년 가까이 그대로입니다. '
               '정책값만 바꾸면 되는 게 아니라 <b>이미 오래된 비밀번호는 따로 재설정</b>해야 합니다.',
        'cmds': ['show password-policy', 'show admin'],
        'options': ['만료 정책이 없고(max-age 0) admin 이 2023-11-02 이후 미변경',
                    '90일 만료가 적용 중',
                    'audit 계정이 2026-07-01 에 변경함',
                    '잠금 기능이 꺼져 있음'],
        'evidence': ['만료 정책이 없고(max-age 0) admin 이 2023-11-02 이후 미변경'],
        'verdict': "function(c){var p=c.get('auth.password')||{};"
                   "if(!(p.maxAgeDays>0&&p.maxAgeDays<=90)) return 'vuln';"
                   "var a=c.get('admins')||[];"
                   "return a.some(function(u){return u.pwChanged<'2026-06-15';})?'vuln':'good';}",
        'fix': "function(c){c.set('auth.password.maxAgeDays',90);c.set('auth.password.reuseCheck',true);"
               "var a=c.get('admins')||[];a.forEach(function(u){"
               "if(u.pwChanged<'2026-06-15') u.pwChanged='2026-09-15';});c.set('admins',a);}",
        'fixNote': '90일 만료를 적용하고, 오래된 계정의 비밀번호를 재설정했습니다.',
    },
]


# ── Lab 2 : 접근 통제 ─────────────────────────────────────────
ACCESS_MISSIONS = [
    {
        'id': 'ISS-016', 'risk': 5, 'appliesTo': ALL6,
        'title': '보안장비 접속 시 보안 접속 사용 여부',
        'brief': 'Telnet 과 HTTP 는 <b>비밀번호를 평문으로</b> 보냅니다. 같은 구간을 들여다보는 사람이 '
                 '있으면 관리자 계정이 그대로 넘어갑니다.',
        'where': 'show management 의 ENCRYPTED 열',
        'hint': '암호화되지 않는데 켜져 있는 프로토콜을 찾으세요.',
        'why': 'telnet(23)과 http(80)가 켜져 있습니다. https·ssh 가 이미 있으므로 평문 프로토콜은 '
               '꺼도 관리에 지장이 없습니다. 켜 두면 안전한 경로를 만들어 둔 의미가 없어집니다.',
        'cmds': ['show management'],
        'options': ['telnet(23)·http(80) 가 활성화되어 있음',
                    'https·ssh 만 활성화됨',
                    '관리 접근 목록이 비어 있음',
                    '로그인 배너가 없음'],
        'evidence': ['telnet(23)·http(80) 가 활성화되어 있음'],
        'verdict': "function(c){var p=(c.get('mgmt.protocols')||[]);"
                   "return p.some(function(x){return x.enabled&&!x.encrypted;})?'vuln':'good';}",
        'fix': "function(c){var p=c.get('mgmt.protocols')||[];p.forEach(function(x){"
               "if(!x.encrypted) x.enabled=false;});c.set('mgmt.protocols',p);"
               "var s=c.get('services')||[];s.forEach(function(x){"
               "if(x.name==='telnet'||x.name==='http') x.enabled=false;});c.set('services',s);}",
        'fixNote': 'telnet 과 http 를 껐습니다. 관리는 ssh·https 로만 합니다.',
    },
    {
        'id': 'ISS-021', 'risk': 5, 'appliesTo': ALL6,
        'title': '보안장비 원격 관리 접근 통제 여부',
        'brief': '관리 화면에 <b>어디서든 접속할 수 있으면</b>, 계정 정보만 알아내면 끝입니다. '
                 '접속 가능한 출발지를 먼저 좁혀야 합니다.',
        'where': 'show management 의 Management access list',
        'hint': '허용 목록이 비어 있을 때 장비가 어떻게 동작하는지 출력에 적혀 있습니다.',
        'why': '관리 접근 목록이 비어 있어 모든 출발지에서 관리 접속을 시도할 수 있습니다. '
               '관리 전용 대역(10.99.0.0/24)만 허용하면 계정이 유출돼도 접속 자체가 막힙니다.',
        'cmds': ['show management', 'show interface'],
        'options': ['관리 접근 목록이 비어 있어 모든 출발지 허용',
                    '관리 대역만 허용되어 있음',
                    'telnet 이 켜져 있음',
                    'mgmt 존이 10.99.0.1/24'],
        'evidence': ['관리 접근 목록이 비어 있어 모든 출발지 허용'],
        'verdict': "function(c){var a=c.get('mgmt.allowedIps')||[];return a.length?'good':'vuln';}",
        'fix': "function(c){c.set('mgmt.allowedIps',['10.99.0.0/24','10.20.9.11/32']);}",
        'fixNote': '관리 대역과 보안관리자 PC 만 허용하도록 접근 목록을 넣었습니다.',
    },
    {
        'id': 'ISS-022', 'risk': 3, 'appliesTo': ALL6,
        'title': '보안장비 접속성공/실패 로깅 여부',
        'brief': '실패 기록이 없으면 <b>누가 대입을 시도했는지 알 수 없습니다</b>. '
                 '성공만 남기면 공격의 흔적이 아니라 결과만 남습니다.',
        'where': 'show logging 의 Login success / Login failure',
        'hint': '두 줄을 각각 보세요. 하나만 켜져 있을 수 있습니다.',
        'why': '로그인 성공은 기록하는데 실패가 꺼져 있습니다. 잠금 기능도 없는 상태라 대입 시도가 '
               '있어도 남는 흔적이 전혀 없습니다. 성공과 실패를 모두 남겨야 합니다.',
        'cmds': ['show logging', 'show password-policy'],
        'options': ['로그인 실패 로깅이 꺼져 있음',
                    '성공·실패 모두 기록 중',
                    '설정 변경 로깅이 켜져 있음',
                    '로컬 보관이 30일'],
        'evidence': ['로그인 실패 로깅이 꺼져 있음'],
        'verdict': "function(c){var g=c.get('logging')||{};"
                   "return (g.loginSuccess&&g.loginFail)?'good':'vuln';}",
        'fix': "function(c){c.set('logging.loginFail',true);}",
        'fixNote': '로그인 실패 로깅을 켰습니다.',
    },
    {
        'id': 'ISS-024', 'risk': 4, 'appliesTo': ALL6,
        'title': '세션 타임아웃 설정 여부',
        'brief': '자리를 비운 사이 <b>열려 있는 관리 세션</b>은 옆사람에게도, 그 PC 를 잡은 공격자에게도 '
                 '그대로 넘어갑니다. 내부 규정이 없으면 15분이 기준입니다.',
        'where': 'show session 의 TIMEOUT 열',
        'hint': '판단기준에 예외가 하나 있습니다. 모니터링 계정은 세션 타임아웃 예외를 허용합니다.',
        'why': 'console 이 never, web 이 60분으로 기준(15분)을 넘습니다. '
               '<b>monitor 라인도 never 지만 이건 취약이 아닙니다</b> — 상시 관제 화면이 꺼지면 안 되므로 '
               '판단기준이 모니터링 계정을 예외로 두고 있습니다. 예외를 예외로 아는 것이 점검의 일부입니다.',
        'cmds': ['show session'],
        'options': ['console 이 never, web 이 60분으로 기준 초과',
                    '모든 라인이 15분 이내',
                    'monitor 라인이 never (모니터링 예외 대상)',
                    'ssh 가 10분'],
        'evidence': ['console 이 never, web 이 60분으로 기준 초과'],
        'verdict': "function(c){var s=(c.get('auth.session.lines')||[]);"
                   "return s.some(function(l){return l.name!=='monitor'&&"
                   "(l.timeoutMin===0||l.timeoutMin>15);})?'vuln':'good';}",
        'fix': "function(c){var s=c.get('auth.session.lines')||[];s.forEach(function(l){"
               "if(l.name!=='monitor'&&(l.timeoutMin===0||l.timeoutMin>15)) l.timeoutMin=10;});"
               "c.set('auth.session.lines',s);}",
        'fixNote': 'console 과 web 세션을 10분으로 맞췄습니다. monitor 는 예외로 그대로 뒀습니다.',
    },
    {
        'id': 'ISS-014', 'risk': 4, 'appliesTo': ALL6,
        'title': '사용하지 않는 SNMP 비활성화 여부',
        'brief': 'SNMP 는 장비의 하드웨어·소프트웨어 정보를 그대로 알려 줍니다. '
                 '<b>쓰지 않는데 켜져 있으면</b> 공격자에게 정찰 창구를 열어 둔 셈입니다.',
        'where': 'show snmp 의 agent 상태와 Purpose',
        'hint': '이 항목이 묻는 것은 "안전하게 쓰는가"가 아니라 "쓰지도 않는데 켜 뒀는가"입니다.',
        'why': 'SNMP 가 켜져 있지만 <b>용도가 기록돼 있고 실제로 NMS 가 상시 사용 중</b>입니다. '
               '(nms 계정의 최근 접속이 오늘로 찍혀 있습니다.) 사용 중인 서비스를 켜 둔 것은 취약이 아닙니다. '
               '설정이 안전한지는 다음 항목(ISS-015)에서 따로 봅니다. '
               '<b>같은 출력이라도 항목마다 묻는 것이 다릅니다.</b>',
        'cmds': ['show snmp', 'show admin'],
        'options': ['SNMP 를 쓰지 않는데 켜져 있음',
                    'SNMP 가 NMS 연동 용도로 실제 사용 중',
                    'community 가 public',
                    'SNMP 가 꺼져 있음'],
        'evidence': ['SNMP 가 NMS 연동 용도로 실제 사용 중'],
        'verdict': "function(c){var s=c.get('snmp')||{};"
                   "if(!s.enabled) return 'good';"
                   "return (s.purpose&&s.purpose.indexOf('미사용')<0)?'good':'vuln';}",
        'fix': 'null',
        'fixNote': '',
    },
    {
        'id': 'ISS-015', 'risk': 4, 'appliesTo': ALL6,
        'title': '안전한 네트워크 모니터링 서비스 사용 여부',
        'brief': '앞 항목에서 "써야 하니까 켠 게 맞다"까지 봤습니다. 이번엔 <b>그 설정이 안전한지</b>를 봅니다. '
                 'v2c 는 community 문자열이 평문으로 오갑니다.',
        'where': 'show snmp 의 Version 과 Community',
        'hint': 'v3 를 쓸 수 있는데 v2c 를 쓰는지, community 가 초기값인지 두 가지를 보세요.',
        'why': 'v2c 를 쓰면서 community 가 초기값 public 입니다. 읽기 전용이어도 장비 정보가 그대로 '
               '넘어갑니다. v3 + AuthPriv 로 바꾸는 것이 원칙이고, 불가피하게 v2c 라면 최소한 '
               '유추 불가능한 문자열(복잡도 기준 충족)로 바꿔야 합니다.',
        'cmds': ['show snmp', 'show version'],
        'options': ['v2c 를 쓰면서 community 가 초기값 public',
                    'v3 AuthPriv 로 설정됨',
                    'SNMP 가 실제 사용 중',
                    '읽기 전용이라 안전함'],
        'evidence': ['v2c 를 쓰면서 community 가 초기값 public'],
        'verdict': "function(c){var s=c.get('snmp')||{};if(!s.enabled) return 'good';"
                   "if(s.version==='v3') return (s.secLevel==='AuthPriv')?'good':'vuln';"
                   "var weak=['public','private','manager','admin'];"
                   "return weak.indexOf(String(s.community).toLowerCase())>=0?'vuln':"
                   "(String(s.community).length>=10?'good':'vuln');}",
        'fix': "function(c){c.set('snmp.version','v3');c.set('snmp.secLevel','AuthPriv');"
               "c.set('snmp.user','nmsmon');c.set('snmp.community','');}",
        'fixNote': 'SNMP v3 로 올리고 보안수준을 AuthPriv(인증+암호화)로 설정했습니다.',
    },
]


LABS = [
    {
        'key': 'acct',
        'file': '07_iss-account.html',
        'code': 'ISS-ACCT',
        'title': '정보보호시스템 진단 실습: 계정·인증',
        'desc': '모의 방화벽에 접속해 show 명령으로 계정과 인증 설정을 뽑고, '
                '판단기준에 따라 양호/취약을 가린 뒤 조치까지 해 봅니다.',
        'device': FW_DEVICE,
        'cfg': FW_CFG,
        'missions': ACCT_MISSIONS,
    },
    {
        'key': 'access',
        'file': '07_iss-access.html',
        'code': 'ISS-ACCESS',
        'title': '정보보호시스템 진단 실습: 접근 통제',
        'desc': '관리 접속 경로, 접근 통제, 세션, SNMP 설정을 점검합니다. '
                '같은 출력을 놓고 항목마다 다른 것을 묻는 경우를 다룹니다.',
        'device': FW_DEVICE,
        'cfg': FW_CFG,
        'missions': ACCESS_MISSIONS,
    },
]
