# -*- coding: utf-8 -*-
"""정보보호시스템(보안장비) 진단 실습 — 네트워크 구성 (ISS-003, 004, 013)

구간을 어떻게 나눴는지, 밖에서 안으로 들어오는 길을 몇 개 열어 뒀는지,
경로를 보내는 쪽이 정할 수 있게 뒀는지를 본다. 정책 한 줄이 아니라
**망 구성 자체**가 판단 대상이라는 점이 정책 관리 랩과 다르다.
"""
import copy

from specs_iss_acct import FW_CFG

FW_VPN = ['FW', 'VPN']

NET_DEVICE = {
    'name': 'fin-fw-03',
    'type': 'FW',
    'typeLabel': '방화벽 (인터넷 경계)',
    'configDate': '2026-09-15 10:18:22 KST',
}

NET_CFG = copy.deepcopy(FW_CFG)
NET_CFG['system'].update({
    'model': 'SENTRA SG-4200', 'serial': 'SG42-2108-5502',
    'os': 'SentraOS 7.4.0', 'build': '7.4.0-b5102',
    'role': 'Firewall / IPSec VPN', 'uptime': '509 days 22:06',
    'eosDate': '2028-03-31', 'eosPassed': False,
})
# 공개용 웹·메일 서버가 내부 업무 구간(trust)에 그대로 들어가 있다.
NET_CFG['interfaces'] = [
    {'name': 'eth0', 'zone': 'untrust', 'address': '203.0.113.10/29', 'state': 'up'},
    {'name': 'eth1', 'zone': 'trust',   'address': '10.20.0.1/16',    'state': 'up'},
    {'name': 'eth2', 'zone': '(unused)', 'address': '-',              'state': 'down'},
    {'name': 'eth3', 'zone': 'mgmt',    'address': '10.99.0.1/24',    'state': 'up'},
]
NET_CFG['nat'] = [
    {'name': 'web-pub',    'original': '10.20.7.21', 'translated': '203.0.113.11',
     'note': '공개 웹 (내부 업무 구간에 위치)'},
    {'name': 'mail-pub',   'original': '10.20.7.25', 'translated': '203.0.113.12',
     'note': '공개 메일 (내부 업무 구간에 위치)'},
    {'name': 'batch-pub',  'original': '10.20.4.55', 'translated': '203.0.113.14',
     'note': '내부 배치서버 — 외부 연결 요건 없음'},
    {'name': 'admin-pub',  'original': '10.99.0.30', 'translated': '203.0.113.15',
     'note': '관리 단말 — 외부 연결 요건 없음'},
]
NET_CFG['net'] = {'sourceRouting': True}
NET_CFG['rules'] = []
NET_CFG['zoneNote'] = 'untrust=외부  trust=내부 업무  mgmt=관리  (DMZ 구간 없음)'


MISSIONS = [
    {
        'id': 'ISS-003', 'risk': 4, 'appliesTo': FW_VPN,
        'title': 'DMZ 구간 설정 여부',
        'brief': '밖에서 접속하는 서버를 <b>내부 업무망에 그대로 두면</b>, 그 서버가 뚫렸을 때 '
                 '공격자가 이미 내부에 들어와 있는 상태가 됩니다.',
        'where': 'show interface 의 ZONE, show nat 의 원본 주소',
        'hint': '공개 서버의 실제 주소가 어느 구간에 속하는지 보세요. 존 이름만 보지 말고 '
                'NAT 의 원본 주소 대역과 인터페이스 대역을 맞춰 보세요.',
        'why': 'DMZ 구간이 없고(eth2 미사용) 공개 웹·메일 서버가 내부 업무 구간(10.20.0.0/16)에 '
               '들어가 있습니다. 공개 서버는 외부에서 직접 닿는 만큼 침해 가능성이 높은데, '
               '뚫리면 내부 업무망과 같은 구간이라 옆으로 바로 번집니다. '
               '별도 구간으로 분리하고 그 구간에서 내부로 가는 트래픽을 통제해야 합니다.',
        'cmds': ['show interface', 'show nat'],
        'options': ['DMZ 구간이 없고 공개 웹·메일 서버가 내부 업무 구간에 위치',
                    '공개 서버가 DMZ 로 분리되어 있음',
                    'eth2 인터페이스가 down 상태',
                    '관리 구간이 10.99.0.0/24 로 분리됨'],
        'evidence': ['DMZ 구간이 없고 공개 웹·메일 서버가 내부 업무 구간에 위치'],
        'verdict': "function(c){var i=(c.get('interfaces')||[]);"
                   "var dmz=i.filter(function(x){return x.zone==='dmz'&&x.state==='up';})[0];"
                   "if(!dmz) return 'vuln';"
                   "var n=(c.get('nat')||[]);"
                   "return n.some(function(x){return /공개/.test(x.note||'')&&"
                   "x.original.indexOf('10.20.')===0;})?'vuln':'good';}",
        'fix': "function(c){var i=c.get('interfaces')||[];i.forEach(function(x){"
               "if(x.name==='eth2'){x.zone='dmz';x.address='10.30.0.1/24';x.state='up';}});"
               "c.set('interfaces',i);"
               "var n=c.get('nat')||[];n.forEach(function(x){"
               "if(x.name==='web-pub'){x.original='10.30.0.21';x.note='공개 웹 (DMZ)';}"
               "if(x.name==='mail-pub'){x.original='10.30.0.25';x.note='공개 메일 (DMZ)';}});"
               "c.set('nat',n);c.set('zoneNote','untrust=외부  dmz=공개서버  trust=내부 업무  mgmt=관리');}",
        'fixNote': 'eth2 를 DMZ 구간으로 올리고 공개 웹·메일 서버를 그 구간으로 옮겼습니다.',
    },
    {
        'id': 'ISS-004', 'risk': 4, 'appliesTo': FW_VPN,
        'title': 'NAT 정책 설정 적정성',
        'brief': 'NAT 를 걸어 두면 <b>밖에서 안으로 들어오는 길</b>이 하나 생깁니다. '
                 '들어올 필요가 없는 서버에 걸려 있으면 그냥 열어 둔 문입니다.',
        'where': 'show nat 의 NOTE — 외부 연결 요건이 있는지',
        'hint': '각 항목이 정말 외부에서 접속해야 하는 서버인지 따져 보세요. '
                '배치서버나 관리 단말은 보통 아닙니다.',
        'why': '내부 배치서버(10.20.4.55)와 관리 단말(10.99.0.30)에 외부 주소가 매핑돼 있습니다. '
               '둘 다 외부에서 접속할 요건이 없습니다. 특히 <b>관리 단말이 외부에 노출된 것</b>은 '
               '관리 구간을 따로 나눈 의미를 없앱니다. 쓰지 않는 NAT 는 지워야 합니다.',
        'cmds': ['show nat', 'show interface'],
        'options': ['외부 연결 요건이 없는 배치서버·관리 단말에 NAT 가 설정됨',
                    '모든 NAT 가 공개 서비스용',
                    '공개 웹이 203.0.113.11 로 매핑됨',
                    'NAT 가 4건 설정됨'],
        'evidence': ['외부 연결 요건이 없는 배치서버·관리 단말에 NAT 가 설정됨'],
        'verdict': "function(c){var n=(c.get('nat')||[]);"
                   "return n.some(function(x){return /요건 없음/.test(x.note||'');})?'vuln':'good';}",
        'fix': "function(c){var n=c.get('nat')||[];"
               "c.set('nat', n.filter(function(x){return !/요건 없음/.test(x.note||'');}));}",
        'fixNote': '외부 연결 요건이 없는 NAT 2건(배치서버·관리 단말)을 삭제했습니다.',
    },
    {
        'id': 'ISS-013', 'risk': 2, 'appliesTo': FW_VPN,
        'title': '불필요한 Source Routing 차단 설정 여부',
        'brief': '소스 라우팅은 <b>보내는 쪽이 경로를 지정</b>하는 옛 기능입니다. '
                 '설계해 둔 경로를 건너뛰어 통제 지점을 우회할 수 있습니다.',
        'where': 'show service 의 IP source-routing',
        'hint': '요즘 정상적인 업무 트래픽이 이 기능을 쓰는 경우는 사실상 없습니다.',
        'why': 'IP source-routing 이 활성 상태입니다. 공격자가 패킷에 경로를 직접 적어 보내면 '
               '중간의 통제 지점을 지나지 않는 경로로 들어올 수 있습니다. '
               '쓰는 곳이 없으므로 꺼야 합니다.',
        'cmds': ['show service'],
        'options': ['IP source-routing 이 활성 상태',
                    'IP source-routing 이 비활성',
                    'telnet 이 켜져 있음',
                    'ssh 가 관리 용도로 켜져 있음'],
        'evidence': ['IP source-routing 이 활성 상태'],
        'verdict': "function(c){return c.get('net.sourceRouting')?'vuln':'good';}",
        'fix': "function(c){c.set('net.sourceRouting',false);}",
        'fixNote': 'IP source-routing 을 껐습니다.',
    },
]


LABS = [
    {
        'key': 'net',
        'file': '07_iss-network.html',
        'code': 'ISS-NET',
        'title': '정보보호시스템 진단 실습: 네트워크 구성',
        'desc': '구간을 어떻게 나눴는지, 밖에서 안으로 들어오는 길을 몇 개 열어 뒀는지를 점검합니다. '
                '정책 한 줄이 아니라 망 구성 자체가 판단 대상입니다.',
        'device': NET_DEVICE,
        'cfg': NET_CFG,
        'missions': MISSIONS,
    },
]
