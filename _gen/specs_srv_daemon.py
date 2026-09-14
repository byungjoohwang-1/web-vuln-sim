# -*- coding: utf-8 -*-
"""금융 서버 진단 실습 — 부가 데몬·장치 경로 랩 (리눅스).

기존 5개 리눅스 랩과 2개 Windows 랩에서 빠져 있던 나머지 항목을 모은다.
업무와 무관하게 떠 있는 데몬(관리 조회·메일·파일 공유·이름 조회), 메일 큐 권한,
파일 전송 접근 주체, 원격 터미널 암호화 방식, 장치 경로와 숨김 항목이 대상이다.

호스트 설정: EDI 연계 서버 한 대. 오래 운영되면서 쓰지 않는 데몬이 그대로 남아 있고,
장치 경로에 장치가 아닌 파일이 섞여 있는 상태로 잡았다.
"""

_SENDMAIL_CF = '\n'.join([
    '# 로컬 설정 — 재생성 금지',
    'Cwfin-edi-06.example.internal',
    'O DaemonPortOptions=Port=smtp,Addr=0.0.0.0,Name=MTA',
    'O LogLevel=1',
    'O PrivacyOptions=authwarnings',
    'O MaxDaemonChildren=0',
])

_VSFTPD = '\n'.join([
    'listen=YES',
    'anonymous_enable=NO',
    'local_enable=YES',
    'write_enable=YES',
    'userlist_enable=NO',
    'xferlog_enable=YES',
])

_HOSTS_ALLOW = '\n'.join([
    '# 접근 허용 목록',
    'ALL: ALL',
])

_SSHD = '\n'.join([
    'Port 22',
    'PermitRootLogin no',
    'PasswordAuthentication yes',
    'Ciphers 3des-cbc,aes128-cbc,aes128-ctr',
    'MACs hmac-md5,hmac-sha1',
    'ClientAliveInterval 300',
])

_EXPORTS = '\n'.join([
    '/edi/out    *(rw,sync,no_root_squash)',
    '/edi/in     192.168.30.0/24(rw,sync)',
])

_NAMED = '\n'.join([
    'options {',
    '    directory "/var/named";',
    '    listen-on port 53 { any; };',
    '};',
])

FS = {
    '/etc/mail/sendmail.cf': {'body': _SENDMAIL_CF, 'mode': '0644'},
    '/var/spool/mqueue': {'body': '', 'mode': '0777', 'dir': True},
    '/var/spool/mqueue/qf7K2a01': {'body': 'V8\nT1757900000\nrRFC822; ops@example.internal\n', 'mode': '0666'},
    '/etc/vsftpd/vsftpd.conf': {'body': _VSFTPD, 'mode': '0644'},
    '/etc/hosts.allow': {'body': _HOSTS_ALLOW, 'mode': '0644'},
    '/etc/hosts.deny': {'body': '# 비어 있음\n', 'mode': '0644'},
    '/etc/ssh/sshd_config': {'body': _SSHD, 'mode': '0600'},
    '/etc/exports': {'body': _EXPORTS, 'mode': '0644'},
    '/etc/named.conf': {'body': _NAMED, 'mode': '0644'},
    '/etc/snmp/snmpd.conf': {'body': 'rocommunity finops 127.0.0.1\nsyslocation IDC-B3\n', 'mode': '0600'},
    # 장치 경로 — 정상 장치 노드와 그렇지 않은 항목이 섞여 있다
    '/dev/null': {'body': '', 'mode': '0666', 'dev': 'c'},
    '/dev/zero': {'body': '', 'mode': '0666', 'dev': 'c'},
    '/dev/sda1': {'body': '', 'mode': '0660', 'dev': 'b', 'group': 'disk'},
    '/dev/edi.cache': {'body': '(이진 데이터)', 'mode': '0666'},
    '/dev/.hist': {'body': 'cd /edi/out\ntar czf /tmp/o.tgz .\n', 'mode': '0644'},
    # 숨김 항목
    '/tmp/...': {'body': '(작업 흔적)', 'mode': '0777', 'dir': True},
    '/tmp/.../dump.bin': {'body': '(이진 데이터)', 'mode': '0666'},
    '/var/tmp/.cap.log': {'body': '수집 대상 인터페이스 eth0\n', 'mode': '0644'},
    '/edi/out': {'body': '', 'mode': '0750', 'dir': True, 'owner': 'edi', 'group': 'edi'},
}

HOST = {
    'name': 'fin-edi-06', 'os': 'Rocky Linux 8.9 (EDI 연계)', 'platform': 'linux',
    'procs': [
        {'pid': 1, 'cmd': '/usr/lib/systemd/systemd'},
        {'pid': 812, 'cmd': '/usr/sbin/sshd -D'},
        {'pid': 990, 'cmd': '/usr/sbin/snmpd -LS0-6d -f'},
        {'pid': 1104, 'cmd': 'sendmail: accepting connections'},
        {'pid': 1288, 'cmd': '/usr/sbin/vsftpd /etc/vsftpd/vsftpd.conf'},
        {'pid': 1440, 'cmd': '/usr/sbin/rpc.nfsd 8'},
        {'pid': 1442, 'cmd': '/usr/sbin/rpc.mountd'},
        {'pid': 1610, 'cmd': '/usr/sbin/named -u named'},
        {'pid': 2201, 'cmd': '/edi/bin/edi-agent --daemon', 'user': 'edi'},
    ],
    'ports': [
        {'port': 22, 'svc': 'sshd'},
        {'port': 25, 'svc': 'sendmail'},
        {'port': 53, 'svc': 'named'},
        {'port': 161, 'svc': 'snmpd', 'bind': '0.0.0.0'},
        {'port': 2049, 'svc': 'nfsd'},
        {'port': 21, 'svc': 'vsftpd'},
    ],
    'pkgs': {
        'sendmail': '8.14.7-5.el8',
        'vsftpd': '3.0.3-35.el8',
        'openssh-server': '8.0p1-19.el8',
        'bind': '9.11.36-8.el8',
    },
}

LABS = [{
    'key': 'daemon', 'file': '07_srv-daemon.html', 'code': 'SRV-DAEMON',
    'title': '부가 데몬·장치 경로',
    'desc': 'EDI 연계 서버에 남아 있는 관리 조회·메일·파일 공유·이름 조회 데몬과 '
            '메일 큐 권한, 파일 전송 접근 통제, 원격 터미널 암호화 방식, 장치 경로의 '
            '비정상 파일까지 명령으로 확인하고 판정하는 실습입니다.',
    'host': HOST, 'fs': FS,
    'missions': [
        {
            'id': 'SRV-003', 'risk': 3, 'title': '사용하지 않는 관리 조회 서비스 중지',
            'brief': '장비 상태를 외부에서 읽어 가는 <b>관리 조회 데몬</b>이 모든 주소에서 '
                     '요청을 받고 있습니다. 이 서버는 통합 모니터링 에이전트를 따로 쓰고 있습니다.',
            'where': '161번 포트와 데몬 프로세스',
            'hint': '어느 주소에서 요청을 받는지(bind 주소)까지 보세요.',
            'cmds': ['netstat -an', 'ps -ef | grep snmpd'],
            'options': ['snmpd 가 161번 포트를 0.0.0.0 으로 열고 있음', '161번 포트가 닫혀 있음',
                        'edi-agent 가 실행 중', 'sshd 가 22번 포트 LISTEN'],
            'evidence': ['snmpd 가 161번 포트를 0.0.0.0 으로 열고 있음'],
            'verdict': "function(fs){return fs.host.ports.some(function(p){return p.port===161;})?'vuln':'good';}",
            'why': '관리 조회 데몬이 전체 주소에서 요청을 받습니다. 별도 모니터링 에이전트가 있으므로 '
                   '업무상 필요가 없습니다. 당장 내릴 수 없다면 최소한 조회 대상 주소를 '
                   '관리망으로 제한하고 조회 문자열을 기본값에서 바꿔야 합니다.',
            'fix': "function(fs){var h=fs.host;"
                   "h.ports=h.ports.filter(function(p){return p.port!==161;});"
                   "h.procs=h.procs.filter(function(p){return !/snmpd/.test(p.cmd);});}",
            'fixNote': '관리 조회 데몬을 중지하고 161번 포트를 닫았습니다.',
        },
        {
            'id': 'SRV-004', 'risk': 3, 'title': '불필요한 메일 전송 서비스 중지',
            'brief': 'EDI 연계 서버가 <b>메일 전송 데몬을 직접 띄우고</b> 있습니다. '
                     '알림 메일은 사내 릴레이 서버를 거치도록 되어 있어 이 서버에서 보낼 일이 없습니다.',
            'where': '25번 포트와 데몬 프로세스',
            'hint': '포트만 보지 말고 프로세스도 함께 확인하세요.',
            'cmds': ['netstat -an', 'ps -ef | grep sendmail'],
            'options': ['메일 전송 데몬이 25번 포트로 떠 있음', '25번 포트가 닫혀 있음',
                        'vsftpd 가 실행 중', 'named 가 53번 포트 LISTEN'],
            'evidence': ['메일 전송 데몬이 25번 포트로 떠 있음'],
            'verdict': "function(fs){return fs.host.ports.some(function(p){return p.port===25;})?'vuln':'good';}",
            'why': '메일을 보내지 않는 서버에 전송 데몬이 떠 있습니다. 쓰지 않는 데몬은 '
                   '패치 대상에서도 잊히기 쉬워 오래된 버전으로 남습니다. '
                   '발송이 꼭 필요하면 데몬을 띄우지 말고 릴레이로 보내는 방식만 남기세요.',
            'fix': "function(fs){var h=fs.host;"
                   "h.ports=h.ports.filter(function(p){return p.port!==25;});"
                   "h.procs=h.procs.filter(function(p){return !/sendmail/.test(p.cmd);});}",
            'fixNote': '메일 전송 데몬을 중지하고 25번 포트를 닫았습니다.',
        },
        {
            'id': 'SRV-006', 'risk': 2, 'title': '메일 서비스 로그 상세 수준 확보',
            'brief': '메일 데몬의 <b>로그 수준이 너무 낮아</b> 누가 무엇을 보냈는지 추적할 수 없습니다. '
                     '데몬을 바로 내릴 수 없는 상황이라면 최소한 기록은 남겨야 합니다.',
            'where': '/etc/mail/sendmail.cf',
            'hint': 'LogLevel 항목을 보세요. 9 이상이어야 배달 단위 기록이 남습니다.',
            'cmds': ['grep -i loglevel /etc/mail/sendmail.cf', 'cat /etc/mail/sendmail.cf'],
            'options': ['LogLevel 이 1 로 설정됨', 'LogLevel 이 9',
                        'PrivacyOptions 가 authwarnings', 'MaxDaemonChildren 이 0'],
            'evidence': ['LogLevel 이 1 로 설정됨'],
            'verdict': "function(fs){var b=fs.read('/etc/mail/sendmail.cf')||'';"
                       "var m=b.match(/^\\s*O\\s+LogLevel\\s*=\\s*(\\d+)/im);"
                       "return (m&&parseInt(m[1],10)>=9)?'good':'vuln';}",
            'why': '로그 수준 1 은 심각한 오류만 남깁니다. 사고가 났을 때 "언제 누구에게 무엇이 나갔는가"를 '
                   '되짚을 수 없습니다. 중지가 원칙이지만, 중지 결정이 날 때까지의 기간에도 '
                   '기록은 남아 있어야 합니다. 두 조치는 서로를 대신하지 않습니다.',
            'fix': "function(fs){var b=fs.read('/etc/mail/sendmail.cf');"
                   "fs.write('/etc/mail/sendmail.cf', b.replace(/O\\s+LogLevel\\s*=\\s*\\d+/i,'O LogLevel=9'));}",
            'fixNote': '메일 데몬의 로그 수준을 9 로 올렸습니다.',
        },
        {
            'id': 'SRV-007', 'risk': 5, 'title': '메일 서비스 취약점 조치 상태',
            'brief': '설치된 메일 데몬이 <b>오래된 버전</b>입니다. 쓰지 않는 데몬이라 '
                     '패치 대상 목록에서도 빠져 있었습니다.',
            'where': '설치 패키지 버전',
            'hint': '설정 파일이 아니라 실제 설치된 패키지 버전을 보세요.',
            'cmds': ['rpm -q sendmail', 'rpm -q openssh-server'],
            'options': ['설치된 메일 데몬이 8.14 계열 구버전', '최신 보안 패치가 적용됨',
                        'openssh-server 가 8.0p1', 'vsftpd 가 3.0.3'],
            'evidence': ['설치된 메일 데몬이 8.14 계열 구버전'],
            'verdict': "function(fs){var v=fs.host.pkgs['sendmail']||'';"
                       "var m=v.match(/^(\\d+)\\.(\\d+)/); if(!m) return 'good';"
                       "return (parseInt(m[1],10)>8||(parseInt(m[1],10)===8&&parseInt(m[2],10)>=15))?'good':'vuln';}",
            'why': '8.14 계열은 지원이 끝난 지 오래입니다. 쓰지 않는 데몬이 패치에서 빠지는 것은 '
                   '흔한 일인데, 떠 있는 이상 공격 표면이라는 사실은 달라지지 않습니다. '
                   '올릴 계획이 없다면 올리는 대신 <b>지우는 것</b>이 더 확실한 조치입니다.',
            'fix': "function(fs){fs.host.pkgs['sendmail']='8.16.1-12.el8';}",
            'fixNote': '메일 데몬을 보안 패치가 적용된 버전으로 올렸습니다.',
        },
        {
            'id': 'SRV-010', 'risk': 4, 'title': '메일 대기열 디렉터리 권한 통제',
            'brief': '보내기 전 메일이 잠시 쌓이는 <b>대기열 디렉터리가 누구나 쓸 수 있는 권한</b>입니다. '
                     '대기 중인 메일을 읽거나 바꿔치기할 수 있습니다.',
            'where': '/var/spool/mqueue',
            'hint': 'ls -al 로 디렉터리 자체와 그 안의 파일 권한을 함께 보세요.',
            'cmds': ['ls -al /var/spool/mqueue', 'stat /var/spool/mqueue'],
            'options': ['대기열 디렉터리가 0777 이고 큐 파일도 0666', '0700 으로 제한되어 있음',
                        '소유자가 root', '큐가 비어 있음'],
            'evidence': ['대기열 디렉터리가 0777 이고 큐 파일도 0666'],
            'verdict': "function(fs){var d=fs.files['/var/spool/mqueue'],q=fs.files['/var/spool/mqueue/qf7K2a01'];"
                       "var dm=parseInt((d&&d.mode)||'0777',8), qm=parseInt((q&&q.mode)||'0666',8);"
                       "return ((dm&7)===0&&(qm&63)===0)?'good':'vuln';}",
            'why': '대기열에는 아직 보내지지 않은 본문이 그대로 들어 있습니다. 누구나 쓸 수 있으면 '
                   '내용을 읽는 것뿐 아니라 수신자를 바꾸는 것도 가능합니다. '
                   '<b>디렉터리만 고치고 그 안의 파일을 그대로 두면</b> 이미 쌓인 메일은 계속 열려 있습니다.',
            'fix': "function(fs){fs.chmod('/var/spool/mqueue','0700');"
                   "fs.chmod('/var/spool/mqueue/qf7K2a01','0600');}",
            'fixNote': '대기열 디렉터리를 0700, 큐 파일을 0600 으로 바꿨습니다.',
        },
        {
            'id': 'SRV-015', 'risk': 5, 'title': '파일 전송 서비스 접근 주체 제한',
            'brief': '파일 전송 서비스가 <b>어느 주소에서든, 어느 로컬 계정으로든</b> 접속을 받습니다. '
                     '접근 통제 파일이 사실상 전면 허용으로 되어 있습니다.',
            'where': '/etc/hosts.allow 와 vsftpd.conf',
            'hint': '허용 목록과 계정 제한 설정을 함께 보세요. 한쪽만 막아서는 부족합니다.',
            'cmds': ['cat /etc/hosts.allow', 'grep -i userlist /etc/vsftpd/vsftpd.conf'],
            'options': ['hosts.allow 가 ALL: ALL 이고 계정 제한도 꺼져 있음',
                        '업무 대역만 허용되어 있음',
                        'anonymous_enable 이 NO', 'xferlog_enable 이 YES'],
            'evidence': ['hosts.allow 가 ALL: ALL 이고 계정 제한도 꺼져 있음'],
            'verdict': "function(fs){var a=fs.read('/etc/hosts.allow')||'', c=fs.read('/etc/vsftpd/vsftpd.conf')||'';"
                       "var openAll=/^\\s*ALL\\s*:\\s*ALL\\s*$/im.test(a);"
                       "var userList=/^\\s*userlist_enable\\s*=\\s*YES/im.test(c);"
                       "return (!openAll&&userList)?'good':'vuln';}",
            'why': '출발지도 계정도 제한이 없습니다. 익명 접속을 막아 두었다는 것만으로는 근거가 되지 않습니다. '
                   '익명을 막아도 로컬 계정 하나만 알아내면 그대로 들어옵니다. '
                   '허용 대역을 업무망으로 좁히고, 접속할 수 있는 계정 목록도 따로 관리해야 합니다.',
            'fix': "function(fs){"
                   "fs.write('/etc/hosts.allow','# 접근 허용 목록\\nvsftpd: 192.168.30.0/24\\nsshd: 192.168.30.0/24\\n');"
                   "fs.write('/etc/hosts.deny','ALL: ALL\\n');"
                   "var c=fs.read('/etc/vsftpd/vsftpd.conf');"
                   "fs.write('/etc/vsftpd/vsftpd.conf', c.replace(/userlist_enable\\s*=\\s*NO/i,'userlist_enable=YES'));}",
            'fixNote': '허용 대역을 업무망으로 좁히고 기본 거부와 계정 목록 제한을 켰습니다.',
        },
        {
            'id': 'SRV-021', 'risk': 4, 'title': '사용하지 않는 원격 파일 공유 서비스 중지',
            'brief': '원격 파일 공유 데몬이 떠 있고, <b>공유 설정에 전체 대상 허용</b>이 남아 있습니다. '
                     '연계 파일은 이미 전송 서비스로 주고받고 있습니다.',
            'where': '공유 데몬과 /etc/exports',
            'hint': '데몬 기동 상태와 실제 공유 항목을 함께 보세요.',
            'cmds': ['ps -ef | grep rpc', 'cat /etc/exports'],
            'options': ['공유 데몬이 떠 있고 /edi/out 이 전체 대상에 공유됨',
                        '공유 데몬이 중지되어 있음',
                        '/edi/in 이 특정 대역에만 공유됨', 'vsftpd 가 실행 중'],
            'evidence': ['공유 데몬이 떠 있고 /edi/out 이 전체 대상에 공유됨'],
            'verdict': "function(fs){return fs.host.procs.some(function(p){return /rpc\\.nfsd/.test(p.cmd);})?'vuln':'good';}",
            'why': '데몬이 떠 있는 데다 공유 대상이 전체로 열려 있고 최상위 권한 축소도 꺼져 있습니다. '
                   '쓰지 않는 공유라면 데몬을 내리는 것이 가장 확실합니다. '
                   '공유 설정만 고치고 데몬을 두면 다음에 누군가 설정을 되돌릴 때 다시 열립니다.',
            'fix': "function(fs){var h=fs.host;"
                   "h.procs=h.procs.filter(function(p){return !/rpc\\./.test(p.cmd);});"
                   "h.ports=h.ports.filter(function(p){return p.port!==2049;});"
                   "fs.write('/etc/exports','# 공유 없음(연계는 전송 서비스로 처리)\\n');}",
            'fixNote': '공유 데몬을 중지하고 공유 설정을 비웠습니다.',
        },
        {
            'id': 'SRV-027', 'risk': 3, 'title': '원격 터미널 접속의 암호화 적용',
            'brief': '원격 터미널은 암호화해서 쓰고 있지만, <b>허용한 암호 방식 목록에 오래된 것들</b>이 '
                     '남아 있습니다. 협상 결과에 따라 약한 방식으로 연결될 수 있습니다.',
            'where': '/etc/ssh/sshd_config',
            'hint': 'Ciphers 와 MACs 줄을 보세요. 목록에 무엇이 들어 있는지가 중요합니다.',
            'cmds': ['grep -i ciphers /etc/ssh/sshd_config', 'cat /etc/ssh/sshd_config'],
            'options': ['Ciphers 목록에 오래된 블록 암호 방식이 남아 있음',
                        '최신 방식만 허용되어 있음',
                        'PermitRootLogin 이 no', 'Port 가 22'],
            'evidence': ['Ciphers 목록에 오래된 블록 암호 방식이 남아 있음'],
            'verdict': "function(fs){var b=fs.read('/etc/ssh/sshd_config')||'';"
                       "var m=b.match(/^\\s*Ciphers\\s+(.+)$/im);"
                       "if(!m) return 'vuln';"
                       "return /3des|-cbc/i.test(m[1])?'vuln':'good';}",
            'why': '암호화 자체는 켜져 있어서 "적용됨"으로 넘어가기 쉬운 항목입니다. 실제로 봐야 하는 것은 '
                   '<b>무엇을 허용했는가</b>입니다. 목록에 오래된 방식이 남아 있으면 상대가 그것만 '
                   '지원한다고 주장할 때 그쪽으로 맞춰 연결됩니다. 메시지 무결성 방식 목록도 같이 정리하세요.',
            'fix': "function(fs){var b=fs.read('/etc/ssh/sshd_config');"
                   "b=b.replace(/^\\s*Ciphers\\s+.*$/im,'Ciphers aes256-gcm@openssh.com,aes256-ctr');"
                   "b=b.replace(/^\\s*MACs\\s+.*$/im,'MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256');"
                   "fs.write('/etc/ssh/sshd_config', b);}",
            'fixNote': '허용 암호 방식과 무결성 방식 목록을 최신 것만 남기도록 정리했습니다.',
        },
        {
            'id': 'SRV-066', 'risk': 3, 'title': '사용하지 않는 이름 조회 서비스 중지',
            'brief': '이름 조회 데몬이 떠 있는데 <b>실제로 관리하는 영역 설정이 없습니다</b>. '
                     '이 서버는 사내 이름 조회 서버를 바라보는 쪽입니다.',
            'where': '데몬 기동 상태와 /etc/named.conf',
            'hint': '데몬이 떠 있는 것과 실제로 영역을 서비스하는 것은 다릅니다.',
            'cmds': ['ps -ef | grep named', 'cat /etc/named.conf'],
            'options': ['이름 조회 데몬이 떠 있으나 서비스하는 영역 설정이 없음',
                        '데몬이 중지되어 있음',
                        '53번 포트가 닫혀 있음', 'snmpd 가 실행 중'],
            'evidence': ['이름 조회 데몬이 떠 있으나 서비스하는 영역 설정이 없음'],
            'verdict': "function(fs){return fs.host.procs.some(function(p){return /named/.test(p.cmd);})?'vuln':'good';}",
            'why': '설정 파일에 영역 선언이 하나도 없는데 데몬만 떠 있습니다. 예전에 시험하다 남은 것으로 '
                   '보입니다. 이름 조회 데몬은 외부에서 질의를 받는 특성상 공격 표면이 커서, '
                   '쓰지 않으면 반드시 내려야 합니다.',
            'fix': "function(fs){var h=fs.host;"
                   "h.procs=h.procs.filter(function(p){return !/named/.test(p.cmd);});"
                   "h.ports=h.ports.filter(function(p){return p.port!==53;});}",
            'fixNote': '이름 조회 데몬을 중지하고 53번 포트를 닫았습니다.',
        },
        {
            'id': 'SRV-080', 'risk': 4, 'title': '장치 경로의 비정상 파일 제거',
            'brief': '장치 경로에 <b>장치 노드가 아닌 보통 파일</b>이 섞여 있습니다. '
                     '점검이 잘 닿지 않는 경로라 자료를 숨기는 자리로 쓰입니다.',
            'where': '/dev',
            'hint': 'ls -al 첫 글자를 보세요. c 와 b 는 장치, - 는 보통 파일입니다.',
            'cmds': ['ls -al /dev', 'find /dev -type f'],
            'options': ['/dev 에 장치가 아닌 보통 파일이 있음', '장치 노드만 있음',
                        '/dev/sda1 이 블록 장치', '/dev/null 이 문자 장치'],
            'evidence': ['/dev 에 장치가 아닌 보통 파일이 있음'],
            'verdict': "function(fs){for(var p in fs.files){var f=fs.files[p];"
                       "if(p.indexOf('/dev/')!==0||f.missing||f.dir||f.dev) continue;"
                       "return 'vuln';} return 'good';}",
            'why': '장치 경로는 원래 장치 노드만 있어야 합니다. 보통 파일이 있다면 누군가 일부러 '
                   '거기에 둔 것입니다. 지우기 전에 <b>내용과 생성 시각을 먼저 보존</b>하세요. '
                   '숨은 파일 하나가 어떤 경로로 들어왔는지 밝힐 유일한 단서일 수 있습니다.',
            'fix': "function(fs){for(var p in fs.files){var f=fs.files[p];"
                   "if(p.indexOf('/dev/')!==0||f.missing||f.dir||f.dev) continue;"
                   "fs.remove(p);}}",
            'fixNote': '장치가 아닌 항목을 보존 조치 후 장치 경로에서 제거했습니다.',
        },
        {
            'id': 'SRV-081', 'risk': 1, 'title': '불필요한 숨김 항목 정리',
            'brief': '임시 경로에 <b>눈에 잘 띄지 않는 이름</b>의 디렉터리와 파일이 있습니다. '
                     '점 세 개로 된 이름은 목록에서 정상 항목처럼 스쳐 지나가기 쉽습니다.',
            'where': '/tmp 와 /var/tmp',
            'hint': 'ls -al 로 점으로 시작하는 항목까지 보세요.',
            'cmds': ['ls -al /tmp', 'ls -al /var/tmp'],
            'options': ['/tmp 에 점 세 개 이름의 디렉터리가 있음', '숨김 항목이 없음',
                        '/edi/out 이 0750', '/dev/null 이 문자 장치'],
            'evidence': ['/tmp 에 점 세 개 이름의 디렉터리가 있음'],
            'verdict': "function(fs){return (fs.exists('/tmp/...')||fs.exists('/var/tmp/.cap.log'))?'vuln':'good';}",
            'why': '위험도는 낮게 잡혀 있지만 넘기기 아까운 항목입니다. 점으로 시작하는 이름은 '
                   '기본 목록에 나오지 않고, 점 세 개짜리는 목록에 나와도 상위 디렉터리 표시처럼 보입니다. '
                   '안에 든 것이 무엇인지 확인하고, 필요 없는 것만 지우세요. '
                   '설정이나 이력 파일처럼 정상적으로 숨김인 항목까지 한꺼번에 지우면 안 됩니다.',
            'fix': "function(fs){fs.remove('/tmp/...'); fs.remove('/tmp/.../dump.bin');"
                   "fs.remove('/var/tmp/.cap.log');}",
            'fixNote': '내용 확인 후 불필요한 숨김 항목을 제거했습니다.',
        },
    ],
}]
