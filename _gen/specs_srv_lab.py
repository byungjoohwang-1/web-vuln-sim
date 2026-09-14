# -*- coding: utf-8 -*-
"""금융 서버 진단 실습(리눅스) 미션 명세.

항목이 "무엇을 보는가"라는 구조만 참고하고, 호스트 시나리오·설정 파일 내용·해설은 전부 새로 썼다.
verdict/fix 는 브라우저에서 실행되는 JS 소스 문자열이다(가상 파일시스템을 읽고 판정한다).

판정을 하드코딩하지 않는다는 점이 중요하다. verdict 는 **현재 파일 내용**을 보고 결정하므로,
학습자가 조치를 적용하면 같은 함수가 '양호'를 돌려준다. 그래서 재점검이 의미를 가진다.
"""

# ── 공통: RHEL 계열 금융 업무 서버 한 대 ─────────────────────────
def _host(name, os_):
    return {'name': name, 'os': os_, 'procs': [], 'ports': [], 'pkgs': {}}


# ═══════════════════════════════════════════════════════════════
# LAB 1 — 원격 접속과 인증
# ═══════════════════════════════════════════════════════════════
REMOTE_FS = {
    '/etc/ssh/sshd_config': {'mode': '0600', 'body': (
        '# 금융 업무 서버 SSH 설정\n'
        'Port 22\n'
        'Protocol 2\n'
        'PermitRootLogin yes\n'
        'PasswordAuthentication yes\n'
        'PermitEmptyPasswords no\n'
        'MaxAuthTries 12\n'
        '#AllowGroups sshusers\n'
        'ClientAliveInterval 0\n'
        'ClientAliveCountMax 3\n'
        'Banner none\n'
        'X11Forwarding yes\n'
        'UsePAM yes\n'
    )},
    '/etc/hosts.equiv': {'mode': '0644', 'body': '+ +\n'},
    '/root/.rhosts': {'mode': '0600', 'body': 'batch-svr01 root\n+ +\n'},
    '/etc/profile': {'mode': '0644', 'body': (
        'PATH=/usr/local/bin:/usr/bin:/bin\n'
        'export PATH\n'
        'umask 022\n'
        '# TMOUT 미설정\n'
    )},
    '/etc/hosts.allow': {'mode': '0644', 'body': 'ALL: ALL\n'},
    '/etc/hosts.deny': {'mode': '0644', 'body': '# 비어 있음\n'},
    '/etc/issue.net': {'mode': '0644', 'body': 'Red Hat Enterprise Linux release 8.8 (Ootpa)\nKernel \\r on an \\m\n'},
    '/root/.ssh/id_rsa': {'mode': '0600', 'body': (
        '-----BEGIN OPENSSH PRIVATE KEY-----\n'
        'b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAB\n'
        'kLmNoPqRsTuVwXyZ0123456789abcdefghijklmnopqrstuvwxyzABCD/+xy\n'
        '-----END OPENSSH PRIVATE KEY-----\n'
    )},
    '/etc/telnetd.conf': {'mode': '0644', 'missing': True, 'body': ''},
}

REMOTE_HOST = dict(_host('fin-app-01', 'Red Hat Enterprise Linux 8.8'),
                   procs=[
                       {'pid': 1042, 'cmd': '/usr/sbin/sshd -D'},
                       {'pid': 1188, 'cmd': 'xinetd -stayalive -pidfile /var/run/xinetd.pid'},
                       {'pid': 1195, 'cmd': 'in.telnetd'},
                       {'pid': 2210, 'cmd': '/usr/sbin/crond -n'},
                   ],
                   ports=[
                       {'port': 22, 'svc': 'sshd'},
                       {'port': 23, 'svc': 'in.telnetd'},
                       {'port': 3306, 'bind': '127.0.0.1', 'svc': 'mysqld'},
                   ])

REMOTE = {
    'key': 'remote', 'file': '07_srv-remote.html', 'code': 'SRV-REMOTE',
    'title': '원격 접속·인증',
    'desc': '모의 리눅스 서버에 붙어 sshd 설정, 신뢰 호스트 파일, 세션 타임아웃을 직접 확인하고 '
            '양호·취약을 판정한 뒤 조치까지 적용해 보는 실습입니다.',
    'host': REMOTE_HOST, 'fs': REMOTE_FS,
    'missions': [
        {
            'id': 'SRV-031', 'risk': 5, 'title': '최상위 권한 계정의 직접 원격 로그인 차단',
            'brief': 'root 로 바로 원격 로그인이 되면, 공격자는 <b>아이디를 맞힐 필요 없이 비밀번호만</b> 맞히면 됩니다. '
                     '또 누가 접속해 무엇을 했는지도 개인 계정으로 구분되지 않습니다.',
            'where': '/etc/ssh/sshd_config',
            'hint': 'PermitRootLogin 항목을 보세요.',
            'cmds': ['grep -i permitrootlogin /etc/ssh/sshd_config'],
            'options': ['PermitRootLogin yes', 'PermitRootLogin no',
                        'PasswordAuthentication yes', 'Protocol 2'],
            'evidence': ['PermitRootLogin yes'],
            'verdict': "function(fs){var b=fs.read('/etc/ssh/sshd_config')||'';"
                       "return /^\\s*PermitRootLogin\\s+(yes|without-password)\\s*$/im.test(b)?'vuln':'good';}",
            'why': 'PermitRootLogin 이 yes 라 root 로 바로 원격 로그인이 됩니다. 개인 계정으로 로그인한 뒤 '
                   '필요할 때만 권한을 올리는 방식으로 바꿔야 접속 주체를 추적할 수 있습니다.',
            'fix': "function(fs){var b=fs.read('/etc/ssh/sshd_config');"
                   "fs.write('/etc/ssh/sshd_config', b.replace(/PermitRootLogin\\s+yes/i,'PermitRootLogin no'));}",
            'fixNote': 'sshd_config 의 PermitRootLogin 을 no 로 바꿨습니다.',
        },
        {
            'id': 'SRV-030', 'risk': 5, 'title': '신뢰 호스트 기반 무인증 접속 설정 제거',
            'brief': 'hosts.equiv 와 .rhosts 에 등록된 호스트·계정은 <b>비밀번호 없이</b> 접속할 수 있습니다. '
                     '특히 <code>+ +</code> 는 "어느 호스트의 누구든" 이라는 뜻이라 사실상 인증이 없는 것과 같습니다.',
            'where': '/etc/hosts.equiv, /root/.rhosts',
            'hint': '두 파일 안에 + 기호가 있는지 보세요.',
            'cmds': ['cat /etc/hosts.equiv', 'cat /root/.rhosts'],
            'options': ['+ +', 'batch-svr01 root', '파일이 비어 있음', '파일이 존재하지 않음'],
            'evidence': ['+ +'],
            'verdict': "function(fs){var a=fs.read('/etc/hosts.equiv')||'',b=fs.read('/root/.rhosts')||'';"
                       "return /^\\s*\\+\\s+\\+/m.test(a)||/^\\s*\\+\\s+\\+/m.test(b)?'vuln':'good';}",
            'why': '두 파일 모두 <code>+ +</code> 를 담고 있어 임의의 호스트에서 인증 없이 접속할 수 있습니다. '
                   '신뢰 호스트 방식 자체를 쓰지 않는 것이 원칙이고, 꼭 써야 한다면 호스트와 계정을 하나씩 지정해야 합니다.',
            'fix': "function(fs){fs.write('/etc/hosts.equiv','');"
                   "fs.write('/root/.rhosts','');}",
            'fixNote': 'hosts.equiv 와 .rhosts 의 전체 허용 설정을 비웠습니다.',
        },
        {
            'id': 'SRV-029', 'risk': 3, 'title': '평문 원격 터미널 서비스 중지',
            'brief': 'telnet 은 아이디와 비밀번호를 <b>암호화하지 않고</b> 그대로 보냅니다. '
                     '같은 구간을 들여다볼 수 있는 사람은 계정을 그대로 가져갈 수 있습니다.',
            'where': '실행 중인 프로세스와 열린 포트',
            'hint': '23번 포트에 무엇이 떠 있는지 보세요.',
            'cmds': ['ps -ef | grep telnet', 'netstat -an | grep 23'],
            'options': ['in.telnetd 프로세스가 실행 중', '23번 포트 LISTEN',
                        'sshd 만 실행 중', '23번 포트 없음'],
            'evidence': ['in.telnetd 프로세스가 실행 중', '23번 포트 LISTEN'],
            'verdict': "function(fs){return window.SRV_LAB_DATA.host.ports.some(function(p){return p.port===23;})?'vuln':'good';}",
            'why': 'telnet 데몬이 23번 포트로 떠 있습니다. 원격 접속은 SSH 로만 받고 telnet 은 중지해야 합니다.',
            'fix': "function(fs){var h=window.SRV_LAB_DATA.host;"
                   "h.ports=h.ports.filter(function(p){return p.port!==23;});"
                   "h.procs=h.procs.filter(function(p){return !/telnet/.test(p.cmd);});}",
            'fixNote': 'telnet 데몬을 중지하고 23번 포트를 닫았습니다.',
        },
        {
            'id': 'SRV-033', 'risk': 2, 'title': '원격 접속 세션 유휴 시간 제한',
            'brief': '자리를 비운 사이 열려 있는 세션은 <b>그 자리에 앉은 사람이 곧 그 계정</b>이 되게 만듭니다. '
                     '일정 시간 입력이 없으면 세션이 끊어져야 합니다.',
            'where': '/etc/profile 의 TMOUT, sshd_config 의 ClientAliveInterval',
            'hint': 'TMOUT 값이 설정돼 있는지 보세요.',
            'cmds': ['grep -i tmout /etc/profile', 'grep -i clientalive /etc/ssh/sshd_config'],
            'options': ['TMOUT 설정이 없음', 'ClientAliveInterval 0',
                        'TMOUT=600', 'ClientAliveInterval 300'],
            'evidence': ['TMOUT 설정이 없음', 'ClientAliveInterval 0'],
            'verdict': "function(fs){var p=fs.read('/etc/profile')||'',s=fs.read('/etc/ssh/sshd_config')||'';"
                       "var t=p.match(/^\\s*TMOUT=(\\d+)/m), c=s.match(/^\\s*ClientAliveInterval\\s+(\\d+)/im);"
                       "var tv=t?parseInt(t[1],10):0, cv=c?parseInt(c[1],10):0;"
                       "return (tv>0&&tv<=900)||(cv>0&&cv<=900)?'good':'vuln';}",
            'why': 'TMOUT 이 없고 ClientAliveInterval 도 0 이라 유휴 세션이 끊기지 않습니다. '
                   '내부 기준이 따로 없다면 15분(900초) 이내로 두는 것이 일반적입니다.',
            'fix': "function(fs){var p=fs.read('/etc/profile');"
                   "fs.write('/etc/profile', p.replace('# TMOUT 미설정','TMOUT=600\\nexport TMOUT'));"
                   "var s=fs.read('/etc/ssh/sshd_config');"
                   "fs.write('/etc/ssh/sshd_config', s.replace(/ClientAliveInterval\\s+0/i,'ClientAliveInterval 300'));}",
            'fixNote': 'TMOUT=600 을 추가하고 ClientAliveInterval 을 300 으로 바꿨습니다.',
        },
        {
            'id': 'SRV-034', 'risk': 3, 'title': '원격 접속 허용 그룹 제한',
            'brief': '접속 가능한 그룹을 지정하지 않으면 <b>계정이 하나 늘 때마다 접속 가능한 사람이 하나 늘어납니다</b>. '
                     '원격 접속이 필요한 사람만 모아 둔 그룹으로 좁혀야 합니다.',
            'where': '/etc/ssh/sshd_config 의 AllowGroups',
            'hint': 'AllowGroups 줄이 주석 처리돼 있지 않은지 보세요.',
            'cmds': ['grep -i allowgroups /etc/ssh/sshd_config'],
            'options': ['#AllowGroups sshusers (주석 처리됨)', 'AllowGroups sshusers',
                        'AllowUsers root', 'DenyGroups 없음'],
            'evidence': ['#AllowGroups sshusers (주석 처리됨)'],
            'verdict': "function(fs){var b=fs.read('/etc/ssh/sshd_config')||'';"
                       "return /^\\s*AllowGroups\\s+\\S+/im.test(b)?'good':'vuln';}",
            'why': 'AllowGroups 가 주석 처리돼 있어 모든 계정이 원격 접속을 시도할 수 있습니다. '
                   '접속이 필요한 그룹만 명시하면 계정이 늘어도 접속 범위는 그대로입니다.',
            'fix': "function(fs){var b=fs.read('/etc/ssh/sshd_config');"
                   "fs.write('/etc/ssh/sshd_config', b.replace('#AllowGroups sshusers','AllowGroups sshusers'));}",
            'fixNote': 'AllowGroups sshusers 주석을 해제했습니다.',
        },
        {
            'id': 'SRV-032', 'risk': 4, 'title': '서비스별 접속 허용 주소·포트 제한',
            'brief': '접근 통제가 없으면 <b>인터넷 어디서든 로그인 시도를 할 수 있습니다</b>. '
                     '업무상 접속하는 대역만 열고 나머지는 기본 거부로 두어야 합니다.',
            'where': '/etc/hosts.allow, /etc/hosts.deny',
            'hint': 'hosts.allow 의 ALL: ALL 이 무슨 뜻인지 생각해 보세요.',
            'cmds': ['cat /etc/hosts.allow', 'cat /etc/hosts.deny'],
            'options': ['ALL: ALL (모든 출발지 허용)', 'sshd: 10.20.30.0/24',
                        'hosts.deny 가 비어 있음', 'ALL: ALL 이 deny 에 있음'],
            'evidence': ['ALL: ALL (모든 출발지 허용)'],
            'verdict': "function(fs){var a=fs.read('/etc/hosts.allow')||'';"
                       "return /^\\s*ALL\\s*:\\s*ALL/m.test(a)?'vuln':'good';}",
            'why': 'hosts.allow 가 <code>ALL: ALL</code> 이라 모든 출발지를 허용합니다. '
                   '필요한 대역만 allow 에 적고 deny 를 기본 거부로 두는 순서가 맞습니다.',
            'fix': "function(fs){fs.write('/etc/hosts.allow','sshd: 10.20.30.0/24\\n');"
                   "fs.write('/etc/hosts.deny','ALL: ALL\\n');}",
            'fixNote': 'hosts.allow 를 업무 대역으로 좁히고 hosts.deny 를 기본 거부로 바꿨습니다.',
        },
        {
            'id': 'SRV-036', 'risk': 4, 'title': '개인 키 파일의 암호구절 설정',
            'brief': 'SSH 개인 키에 암호구절이 없으면 <b>키 파일을 손에 넣은 사람이 곧 그 계정</b>입니다. '
                     '백업 매체나 개발자 노트북을 통해 키가 새는 일이 실제로 자주 있습니다.',
            'where': '/root/.ssh/id_rsa',
            'hint': '키 헤더에 암호화 표시가 있는지 보세요.',
            'cmds': ['cat /root/.ssh/id_rsa', 'ls -al /root/.ssh/id_rsa'],
            'options': ['암호구절 없음(암호화 표시 없는 키)', 'Proc-Type: 4,ENCRYPTED',
                        '권한이 0600', '소유자가 root'],
            'evidence': ['암호구절 없음(암호화 표시 없는 키)'],
            'verdict': "function(fs){var b=fs.read('/root/.ssh/id_rsa')||'';"
                       "return /ENCRYPTED|Proc-Type/i.test(b)?'good':'vuln';}",
            'why': '키 본문에 암호화 표시가 없어 암호구절 없이 만들어진 키입니다. '
                   '권한이 0600 인 것은 맞지만, 파일이 유출되면 권한은 아무 소용이 없습니다.',
            'fix': "function(fs){fs.write('/root/.ssh/id_rsa','-----BEGIN OPENSSH PRIVATE KEY-----\\n"
                   "Proc-Type: 4,ENCRYPTED\\nDEK-Info: AES-256-CBC\\n(암호구절로 보호된 키)\\n"
                   "-----END OPENSSH PRIVATE KEY-----\\n');}",
            'fixNote': '키에 암호구절을 걸어 다시 발급했습니다(ssh-keygen -p).',
        },
        {
            'id': 'SRV-055', 'risk': 1, 'title': '접속 시 경고 문구 표시',
            'brief': '접속 배너는 두 가지를 합니다. 인가되지 않은 접근이라는 <b>경고</b>를 남기고, '
                     '동시에 <b>배포판·커널 버전을 알려 주지 않아야</b> 합니다. 지금 배너는 반대로 하고 있습니다.',
            'where': '/etc/issue.net',
            'hint': '배너에 무엇이 적혀 있는지 그대로 읽어 보세요.',
            'cmds': ['cat /etc/issue.net'],
            'options': ['배포판·커널 버전이 그대로 노출됨', '경고 문구가 있음',
                        '배너가 비어 있음', '배너 파일이 없음'],
            'evidence': ['배포판·커널 버전이 그대로 노출됨'],
            'verdict': "function(fs){var b=fs.read('/etc/issue.net')||'';"
                       "return /release|Kernel|\\\\r|\\\\m/i.test(b)?'vuln':'good';}",
            'why': '배너가 배포판 이름과 커널 버전을 그대로 보여 줍니다. 공격자는 이 정보로 '
                   '적용 가능한 공개 취약점을 좁힙니다. 경고 문구만 남기고 버전 표기는 지워야 합니다.',
            'fix': "function(fs){fs.write('/etc/issue.net',"
                   "'허가된 사용자만 접속할 수 있습니다. 모든 접속 기록은 저장·검토됩니다.\\n');}",
            'fixNote': '버전 표기를 지우고 경고 문구로 바꿨습니다.',
        },
        {
            'id': 'SRV-028', 'risk': 3, 'title': '취약한 원격 인증 방식 사용 금지',
            'brief': '비밀번호 인증만 열려 있고 <b>실패 횟수 제한이 느슨하면</b> 자동화 도구가 계속 두드릴 수 있습니다. '
                     '키 기반 인증을 기본으로 두고 시도 횟수도 좁혀야 합니다.',
            'where': '/etc/ssh/sshd_config 의 MaxAuthTries',
            'hint': 'MaxAuthTries 값이 몇인지 보세요.',
            'cmds': ['grep -iE "maxauthtries|passwordauth" /etc/ssh/sshd_config'],
            'options': ['MaxAuthTries 12', 'MaxAuthTries 3',
                        'PermitEmptyPasswords no', 'UsePAM yes'],
            'evidence': ['MaxAuthTries 12'],
            'verdict': "function(fs){var b=fs.read('/etc/ssh/sshd_config')||'';"
                       "var m=b.match(/^\\s*MaxAuthTries\\s+(\\d+)/im);"
                       "return m&&parseInt(m[1],10)<=5?'good':'vuln';}",
            'why': 'MaxAuthTries 가 12 라 한 연결에서 열두 번까지 시도할 수 있습니다. '
                   '3~5 회로 줄이면 같은 시간에 시도할 수 있는 횟수가 크게 떨어집니다.',
            'fix': "function(fs){var b=fs.read('/etc/ssh/sshd_config');"
                   "fs.write('/etc/ssh/sshd_config', b.replace(/MaxAuthTries\\s+12/i,'MaxAuthTries 3'));}",
            'fixNote': 'MaxAuthTries 를 3 으로 낮췄습니다.',
        },
    ],
}

LABS = [REMOTE]
