# -*- coding: utf-8 -*-
"""정보보호시스템(보안장비) 진단 실습 — 로그·시각 / 운영·패치

운영·패치 랩은 일부러 다른 장비를 쓴다. 지원이 끝난 장비(EoS)는 보통
제일 오래된 박스이고, 그 장비 하나에 패치·사용량·변경통제 문제가 같이
몰려 있는 것이 실제 현장의 모습이다.
"""
import copy

from specs_iss_acct import FW_DEVICE, FW_CFG, ALL6

FW_VPN = ['FW', 'VPN']

# ── 두 번째 모의 장비: 오래된 VPN 집선 장비 ────────────────────
VPN_DEVICE = {
    'name': 'fin-vpn-01',
    'type': 'VPN',
    'typeLabel': 'VPN 집선 장비',
    'configDate': '2026-09-15 09:20:37 KST',
}

VPN_CFG = copy.deepcopy(FW_CFG)
VPN_CFG['system'].update({
    'model': 'SENTRA VG-1200',
    'serial': 'VG12-1809-3310',
    'os': 'SentraOS 5.4.8',
    'build': '5.4.8-b2211',
    'role': 'IPSec / SSL VPN',
    'uptime': '903 days 14:02',
    'eosDate': '2025-12-31',
    'eosPassed': True,
})
VPN_CFG['patch'].update({
    'latest': 'SentraOS 5.4.8 (최종 — 후속 없음)',
    'latestSig': None,
    'review': False,
    'reviewCycle': '',
    'advisoriesApplied': 1,
    'advisoriesTotal': 9,
})
VPN_CFG['services'] = [
    {'name': 'ssh', 'port': 22, 'enabled': True, 'purpose': '관리'},
    {'name': 'https', 'port': 443, 'enabled': True, 'purpose': 'VPN 포털 / 관리'},
    {'name': 'ipsec', 'port': 500, 'enabled': True, 'purpose': 'VPN 터널'},
    {'name': 'ftpd', 'port': 21, 'enabled': True, 'purpose': '-'},
    {'name': 'tftpd', 'port': 69, 'enabled': True, 'purpose': '-'},
]
VPN_CFG['monitor'].update({
    'cpu': 72, 'memory': 88, 'sessions': 1820, 'sessionMax': 2000,
    'usageReview': False, 'realtime': False, 'alerting': [], 'logReview': False,
})
VPN_CFG['change'].update({'procedure': False, 'requestForm': False,
                          'techReview': False, 'recent': 14, 'unapproved': 6})


# ── Lab 3 : 로그·시각 (방화벽) ────────────────────────────────
LOG_MISSIONS = [
    {
        'id': 'ISS-001', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 정책 및 로그 백업 설정 여부',
        'brief': '장비가 죽었을 때 <b>정책을 다시 만들 수 있는가</b>가 복구 시간을 가릅니다. '
                 '백업이 없으면 몇 년치 정책을 기억으로 복원해야 합니다.',
        'where': 'show backup 의 Policy backup / Log backup / Last backup',
        'hint': '백업 설정 여부와 마지막 백업 시각을 같이 보세요.',
        'why': '정책·로그 백업이 모두 꺼져 있고 마지막 백업 기록도 없습니다(never). '
               '장애가 나면 정책을 복원할 방법이 없습니다. 정기 백업을 걸고, 장비 밖에 보관해야 합니다.',
        'cmds': ['show backup'],
        'options': ['정책·로그 백업이 모두 비활성, 마지막 백업 기록 없음',
                    '정책 백업이 주 1회 동작 중',
                    '무결성 검사가 수행되지 않음',
                    '백업 대상지가 원격 스토리지'],
        'evidence': ['정책·로그 백업이 모두 비활성, 마지막 백업 기록 없음'],
        'verdict': "function(c){var b=c.get('backup')||{};"
                   "return (b.policy&&b.log)?'good':'vuln';}",
        'fix': "function(c){c.set('backup.policy',true);c.set('backup.policyCycle','weekly');"
               "c.set('backup.log',true);c.set('backup.logCycle','daily');"
               "c.set('backup.last','2026-09-15 03:00');c.set('backup.dest','10.99.2.30:/backup/fw');}",
        'fixNote': '정책은 주 1회, 로그는 매일 원격 스토리지로 백업하도록 설정했습니다.',
    },
    {
        'id': 'ISS-002', 'risk': 3, 'appliesTo': ALL6,
        'title': '원격 로그 서버 사용 여부',
        'brief': '장비 안에만 로그가 있으면 <b>장비를 장악한 쪽이 로그도 지웁니다</b>. '
                 '저장 공간도 한정돼 있어 오래된 것부터 덮어써집니다.',
        'where': 'show logging 의 Remote log server',
        'hint': '원격 전송 여부와 보관 기간을 같이 보세요. 판단기준은 1년 이상 보관입니다.',
        'why': '원격 로그 서버가 설정돼 있지 않고 로컬 보관도 30일뿐입니다. 침해사고는 몇 달 뒤에 '
               '드러나는 일이 흔한데, 그때는 이미 로그가 남아 있지 않습니다. '
               'Syslog 등으로 밖에 보내고 1년 이상 보관해야 합니다.',
        'cmds': ['show logging'],
        'options': ['원격 로그 서버 미설정, 로컬 보관 30일',
                    'Syslog 로 원격 전송 중',
                    '로그인 실패 로깅이 꺼져 있음',
                    'RAW 패킷 저장이 꺼져 있음'],
        'evidence': ['원격 로그 서버 미설정, 로컬 보관 30일'],
        'verdict': "function(c){var r=(c.get('logging.remote')||{});"
                   "return (r.enabled&&r.retentionDays>=365)?'good':'vuln';}",
        'fix': "function(c){c.set('logging.remote',{enabled:true,proto:'syslog-tls',"
               "host:'10.99.2.40',port:6514,retentionDays:365});}",
        'fixNote': '원격 Syslog(TLS) 로 전송하고 365일 보관하도록 설정했습니다.',
    },
    {
        'id': 'ISS-025', 'risk': 2, 'appliesTo': ALL6,
        'title': '시간 동기화를 위한 NTP 설정',
        'brief': '장비마다 시계가 다르면 <b>사고 순서를 맞출 수 없습니다</b>. '
                 '어느 장비 로그가 먼저인지 모르면 경로 추적이 불가능합니다.',
        'where': 'show ntp',
        'hint': 'NTP 가 켜져 있는지, 그리고 실제로 동기화된 상태인지 두 가지를 보세요.',
        'why': 'NTP 가 켜져 있고 서버와 <b>실제로 동기화된 상태(synchronized)</b>입니다. '
               '설정만 있고 동기화가 안 된 경우(unsynchronized)가 흔한데 이 장비는 정상입니다. '
               '켜져 있다는 것과 맞춰져 있다는 것은 다르므로 상태까지 확인해야 합니다.',
        'cmds': ['show ntp'],
        'options': ['NTP 가 꺼져 있고 로컬 시계를 씀',
                    'NTP 가 켜져 있고 서버와 동기화된 상태',
                    '서버가 stratum 3',
                    '로그 보관이 30일'],
        'evidence': ['NTP 가 켜져 있고 서버와 동기화된 상태'],
        'verdict': "function(c){var n=c.get('ntp')||{};if(!n.enabled) return 'vuln';"
                   "var s=n.servers||[];"
                   "return s.some(function(x){return x.state==='synchronized';})?'good':'vuln';}",
        'fix': 'null',
        'fixNote': '',
    },
    {
        'id': 'ISS-026', 'risk': 2, 'appliesTo': ALL6,
        'title': '주요 파일에 대한 주기적인 무결성 검사 여부',
        'brief': '설정 파일이 <b>몰래 바뀌어도 알 수 없다면</b>, 장비를 장악당한 뒤에도 '
                 '정상으로 보입니다. 주기적으로 원본과 대조해야 합니다.',
        'where': 'show backup 의 Integrity check',
        'hint': '이 기능을 지원하지 않는 장비라면 해당없음이지만, 이 장비는 항목이 출력에 있습니다.',
        'why': '무결성 검사가 수행되지 않고 있습니다. 설정·로그 파일이 변조돼도 탐지되지 않습니다. '
               '백업본과 주기적으로 대조하도록 설정해야 합니다.',
        'cmds': ['show backup'],
        'options': ['무결성 검사가 수행되지 않음',
                    '주 1회 무결성 검사 수행 중',
                    '정책 백업이 꺼져 있음',
                    '마지막 백업이 never'],
        'evidence': ['무결성 검사가 수행되지 않음'],
        'verdict': "function(c){return c.get('backup.integrity')?'good':'vuln';}",
        'fix': "function(c){c.set('backup.integrity',true);c.set('backup.integrityCycle','weekly');}",
        'fixNote': '주 1회 설정·주요 파일 무결성 검사를 걸었습니다.',
    },
]


# ── Lab 4 : 운영·패치 (오래된 VPN 장비) ───────────────────────
OPS_MISSIONS = [
    {
        'id': 'ISS-043', 'risk': 5, 'appliesTo': ALL6,
        'title': '서비스 지원이 종료된(EoS) 시스템 및 장비 교체 여부',
        'brief': '지원이 끝난 장비는 <b>새 취약점이 나와도 고칠 패치가 나오지 않습니다</b>. '
                 '설정을 아무리 잘해도 시간이 갈수록 위험만 쌓입니다.',
        'where': 'show version 의 Support end (EoS)',
        'hint': '오늘 날짜와 비교하세요. 지난 날짜면 장비에 경고가 같이 찍힙니다.',
        'why': '지원 종료일이 2025-12-31 로 이미 지났습니다(*** End of Service ***). '
               '후속 버전도 없어 패치로 해결할 수 없습니다. 교체가 유일한 조치이고, '
               '교체 계획을 세워 보고했다면 <b>취약으로 반영하되 위험수용으로 관리</b>합니다.',
        'cmds': ['show version', 'show patch'],
        'options': ['지원 종료일(2025-12-31)이 이미 지남',
                    '지원 기간이 남아 있음',
                    '최신 빌드가 적용되어 있음',
                    '권고사항 1건만 적용됨'],
        'evidence': ['지원 종료일(2025-12-31)이 이미 지남'],
        'verdict': "function(c){return c.get('system.eosPassed')?'vuln':'good';}",
        'fix': "function(c){c.set('system.model','SENTRA VG-3400');"
               "c.set('system.serial','VG34-2609-0102');c.set('system.os','SentraOS 7.4.0');"
               "c.set('system.build','7.4.0-b5102');c.set('system.eosDate','2031-06-30');"
               "c.set('system.eosPassed',false);c.set('system.uptime','0 days 00:12');"
               "c.set('patch.latest','SentraOS 7.4.0');c.set('patch.advisoriesApplied',9);}",
        'fixNote': '지원 기간이 남은 장비로 교체하고 설정을 이관했습니다. (실제로는 교체 계획 수립·보고 후 진행)',
    },
    {
        'id': 'ISS-005', 'risk': 5, 'appliesTo': ALL6,
        'title': '주기적인 보안패치 및 벤더 권고사항 적용 여부',
        'brief': '공개된 취약점은 <b>공격자도 같은 날 알게 됩니다</b>. '
                 '패치가 밀린 기간이 그대로 노출 기간입니다.',
        'where': 'show patch 의 Vendor advisories, Patch review',
        'hint': '적용한 권고사항 수와 전체 수를 비교하고, 검토 절차가 있는지 보세요.',
        'why': '벤더 권고사항 9건 중 1건만 적용됐고 정기 검토 절차도 없습니다. '
               '패치 적용 자체보다 <b>검토·계획·이행이 절차로 돌아가는지</b>가 판단 대상입니다.',
        'cmds': ['show patch'],
        'options': ['권고사항 9건 중 1건만 적용, 정기 검토 절차 없음',
                    '모든 권고사항이 적용됨',
                    '분기별 검토 절차가 있음',
                    '지원 종료일이 지남'],
        'evidence': ['권고사항 9건 중 1건만 적용, 정기 검토 절차 없음'],
        'verdict': "function(c){var p=c.get('patch')||{};"
                   "return (p.review&&p.advisoriesApplied===p.advisoriesTotal)?'good':'vuln';}",
        'fix': "function(c){c.set('patch.review',true);c.set('patch.reviewCycle','monthly');"
               "c.set('patch.advisoriesApplied',c.get('patch.advisoriesTotal'));}",
        'fixNote': '월 1회 패치 검토 절차를 세우고 미적용 권고사항을 모두 반영했습니다.',
    },
    {
        'id': 'ISS-006', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 사용량의 주기적인 점검 및 보고 여부',
        'brief': '자원이 한계에 닿으면 장비가 <b>트래픽을 그냥 흘려보내거나 멈춥니다</b>. '
                 '보안장비의 가용성은 곧 보안 기능의 가용성입니다.',
        'where': 'show resource 의 CPU/Memory/Session 과 Usage review',
        'hint': '현재 수치도 보고, 그걸 정기적으로 검토하는 절차가 있는지도 보세요.',
        'why': '메모리 88%, 세션 1820/2000(91%)으로 한계에 가까운데 사용량 검토 절차가 없습니다. '
               '수치 자체보다 <b>이 수치를 정기적으로 보고 조치하는 체계가 있는지</b>가 판단 대상입니다.',
        'cmds': ['show resource'],
        'options': ['세션 91%·메모리 88% 인데 사용량 검토 절차가 없음',
                    '월 1회 사용량 검토 중',
                    'CPU 가 72%',
                    '실시간 모니터링이 켜져 있음'],
        'evidence': ['세션 91%·메모리 88% 인데 사용량 검토 절차가 없음'],
        'verdict': "function(c){return c.get('monitor.usageReview')?'good':'vuln';}",
        'fix': "function(c){c.set('monitor.usageReview',true);"
               "c.set('monitor.usageReviewCycle','monthly (보안운영보고서)');}",
        'fixNote': '월 1회 사용량 점검·보고 절차를 세웠습니다. (증설 검토는 별도 진행)',
    },
    {
        'id': 'ISS-007', 'risk': 4, 'appliesTo': ALL6,
        'title': '보안장비 장애/보안이벤트 모니터링 실시 여부',
        'brief': '이벤트가 <b>쌓이기만 하고 아무도 안 보면</b> 로그를 남기는 의미가 없습니다. '
                 '담당자가 즉시 알 수 있는 경로가 있어야 합니다.',
        'where': 'show resource 의 Realtime monitoring / Alerting',
        'hint': '알림 수단(메일·SMS·트랩)이 하나라도 설정돼 있는지 보세요.',
        'why': '실시간 모니터링이 꺼져 있고 알림 수단도 없습니다. 장애나 공격 징후가 생겨도 '
               '담당자가 알 방법이 없습니다. 장비 자체 기능이 없다면 Syslog 를 받는 '
               '모니터링 시스템 쪽에 설정돼 있는지 확인해야 합니다.',
        'cmds': ['show resource', 'show logging'],
        'options': ['실시간 모니터링과 알림이 모두 없음',
                    '메일·SMS 알림이 설정됨',
                    '이벤트 정기 검토가 수행 중',
                    '원격 로그 서버가 설정됨'],
        'evidence': ['실시간 모니터링과 알림이 모두 없음'],
        'verdict': "function(c){var m=c.get('monitor')||{};"
                   "return (m.realtime&&(m.alerting||[]).length)?'good':'vuln';}",
        'fix': "function(c){c.set('monitor.realtime',true);"
               "c.set('monitor.alerting',['email(보안운영팀)','SMS(당직자)','SNMP trap']);"
               "c.set('monitor.logReview',true);c.set('monitor.logReviewCycle','weekly');}",
        'fixNote': '실시간 모니터링을 켜고 메일·SMS·트랩 알림을 걸었습니다.',
    },
    {
        'id': 'ISS-027', 'risk': 2, 'appliesTo': ALL6,
        'title': '보안장비 기능외 서비스 제한 여부',
        'brief': '장비의 본래 기능과 <b>상관없는 서비스가 떠 있으면</b> 그만큼 공격 면이 넓어집니다. '
                 '보안장비가 공격 경유지가 되는 경로입니다.',
        'where': 'show service 의 PURPOSE 열',
        'hint': '용도가 비어 있는(-) 서비스를 찾고, 그게 이 장비의 기능에 필요한지 따져 보세요.',
        'why': 'VPN 장비에 ftpd(21)와 tftpd(69)가 떠 있고 용도도 기록돼 있지 않습니다. '
               '둘 다 인증이 약하거나 없는 프로토콜이라 설정 파일 유출·변조 경로가 됩니다. '
               'VPN 기능과 무관하므로 꺼야 합니다.',
        'cmds': ['show service', 'show version'],
        'options': ['용도 없는 ftpd(21)·tftpd(69) 가 구동 중',
                    '모든 서비스가 장비 기능에 필요함',
                    'ipsec(500) 이 켜져 있음',
                    'ssh(22) 가 관리 용도'],
        'evidence': ['용도 없는 ftpd(21)·tftpd(69) 가 구동 중'],
        'verdict': "function(c){var s=c.get('services')||[];"
                   "return s.some(function(x){return x.enabled&&(!x.purpose||x.purpose==='-');})?'vuln':'good';}",
        'fix': "function(c){var s=c.get('services')||[];s.forEach(function(x){"
               "if(!x.purpose||x.purpose==='-') x.enabled=false;});c.set('services',s);}",
        'fixNote': '용도가 없는 ftpd·tftpd 를 껐습니다.',
    },
    {
        'id': 'ISS-028', 'risk': 4, 'appliesTo': FW_VPN,
        'title': '보안장비 정책 변경통제 절차 수립 여부',
        'brief': '"급하니까 일단 열어 주세요"가 쌓이면 <b>아무도 이유를 모르는 정책</b>이 됩니다. '
                 '나중에 지우지도 못합니다 — 뭐가 끊길지 모르니까요.',
        'where': 'show change-control',
        'hint': '절차가 문서로 있는지, 그리고 최근 변경 중 미승인 건이 있는지 같이 보세요.',
        'why': '변경 절차가 문서화돼 있지 않고, 최근 30일 변경 14건 중 6건이 미승인입니다. '
               '절차가 없다는 것과 절차를 안 지킨다는 것이 같이 나타나 있습니다.',
        'cmds': ['show change-control'],
        'options': ['변경 절차 미문서화, 최근 30일 중 6건이 미승인',
                    '신청서 기반 변경 절차가 운영 중',
                    '기술 검토가 필수로 지정됨',
                    '최근 30일 변경이 14건'],
        'evidence': ['변경 절차 미문서화, 최근 30일 중 6건이 미승인'],
        'verdict': "function(c){var g=c.get('change')||{};"
                   "return (g.procedure&&g.requestForm&&!g.unapproved)?'good':'vuln';}",
        'fix': "function(c){c.set('change.procedure',true);c.set('change.requestForm',true);"
               "c.set('change.unapproved',0);}",
        'fixNote': '신청서 기반 변경 절차를 수립하고 미승인 변경 6건을 사후 승인·정리했습니다.',
    },
    {
        'id': 'ISS-029', 'risk': 4, 'appliesTo': FW_VPN,
        'title': '보안장비 변경요청 정책의 기술적 검토 여부',
        'brief': '신청서가 있어도 <b>그대로 넣기만 하면</b> 통제가 아닙니다. '
                 '요청한 범위가 정말 필요한 최소인지 보는 사람이 있어야 합니다.',
        'where': 'show change-control 의 Technical review',
        'hint': '앞 항목(절차 수립)과 다른 것을 묻습니다. 절차가 있어도 검토 단계가 없을 수 있습니다.',
        'why': '적용 전 기술 검토가 필수로 지정돼 있지 않습니다. 절차를 만드는 것과 '
               '<b>그 절차 안에 적정성을 따지는 단계를 두는 것</b>은 다릅니다. '
               '검토가 없으면 신청한 대로 ANY 가 그대로 들어갑니다.',
        'cmds': ['show change-control'],
        'options': ['적용 전 기술 검토가 필수로 지정돼 있지 않음',
                    '담당자 기술 검토 후 적용 중',
                    '변경 절차가 문서화됨',
                    '미승인 변경이 6건'],
        'evidence': ['적용 전 기술 검토가 필수로 지정돼 있지 않음'],
        'verdict': "function(c){return c.get('change.techReview')?'good':'vuln';}",
        'fix': "function(c){c.set('change.techReview',true);}",
        'fixNote': '정책 적용 전 보안담당자 기술 검토를 필수 단계로 넣었습니다.',
    },
]


LABS = [
    {
        'key': 'log',
        'file': '07_iss-log.html',
        'code': 'ISS-LOG',
        'title': '정보보호시스템 진단 실습: 로그·백업·시각',
        'desc': '로그를 어디에 얼마나 남기는지, 정책을 복구할 수 있는지, 시계가 맞는지 점검합니다.',
        'device': FW_DEVICE,
        'cfg': FW_CFG,
        'missions': LOG_MISSIONS,
    },
    {
        'key': 'ops',
        'file': '07_iss-ops.html',
        'code': 'ISS-OPS',
        'title': '정보보호시스템 진단 실습: 운영·패치',
        'desc': '지원이 끝난 오래된 VPN 장비를 점검합니다. 패치·사용량·모니터링·변경통제가 '
                '한 장비에 어떻게 같이 몰리는지 봅니다.',
        'device': VPN_DEVICE,
        'cfg': VPN_CFG,
        'missions': OPS_MISSIONS,
    },
]
