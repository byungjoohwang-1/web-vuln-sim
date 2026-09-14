# -*- coding: utf-8 -*-
"""금융 서버 진단 실습 — 계정·비밀번호 랩.

passwd / shadow / group / login.defs / PAM / sudoers 를 실제로 읽어 판정한다.
판정 함수는 현재 파일 내용을 보고 결정하므로, 조치를 적용하면 같은 함수가 '양호'를 돌려준다.
"""

FS = {
    '/etc/passwd': {'mode': '0644', 'body': (
        'root:x:0:0:root:/root:/bin/bash\n'
        'bin:x:1:1:bin:/bin:/sbin/nologin\n'
        'daemon:x:2:2:daemon:/sbin:/sbin/nologin\n'
        'ftp:x:14:50:FTP User:/var/ftp:/bin/bash\n'
        'batchadm:x:0:0:batch admin:/home/batchadm:/bin/bash\n'
        'kim.tx:x:1001:1001:transfer team:/home/kim.tx:/bin/bash\n'
        'lee.old:x:1002:1002:2024-11 퇴사:/home/lee.old:/bin/bash\n'
        'svc_settle:x:1003:1003:settlement svc:/home/svc_settle:/bin/bash\n'
        'guestops:x:1004:1004::/home/guestops:/bin/bash\n'
    )},
    '/etc/shadow': {'mode': '0000', 'body': (
        'root:$6$k2Jd$9sLm2...:20180:0:99999:7:::\n'
        'kim.tx:$6$Qa1x$Tz8...:20240:0:99999:7:::\n'
        'lee.old:$6$Wp3z$Lm4...:19980:0:99999:7:::\n'
        'svc_settle:$1$abc$Xy9...:20100:0:99999:7:::\n'
        'guestops::20240:0:99999:7:::\n'
    )},
    '/etc/group': {'mode': '0644', 'body': (
        'root:x:0:root,batchadm,kim.tx\n'
        'wheel:x:10:root,batchadm,kim.tx,svc_settle\n'
        'oldteam:x:1500:\n'
        'sshusers:x:1600:kim.tx\n'
    )},
    '/etc/login.defs': {'mode': '0644', 'body': (
        'PASS_MAX_DAYS   99999\n'
        'PASS_MIN_DAYS   0\n'
        'PASS_MIN_LEN    5\n'
        'ENCRYPT_METHOD  SHA512\n'
    )},
    '/etc/security/pwquality.conf': {'mode': '0644', 'body': (
        '# minlen = 8\n# dcredit = -1\n# ucredit = -1\n# lcredit = -1\n# ocredit = -1\n'
    )},
    '/etc/pam.d/system-auth': {'mode': '0644', 'body': (
        'auth        required      pam_env.so\n'
        'auth        sufficient    pam_unix.so nullok try_first_pass\n'
        'account     required      pam_unix.so\n'
        'password    sufficient    pam_unix.so sha512 shadow\n'
        '# 계정 잠금(pam_faillock) 미설정\n'
    )},
    '/etc/sudoers': {'mode': '0440', 'body': (
        'root    ALL=(ALL)       ALL\n'
        '%wheel  ALL=(ALL)       ALL\n'
        'kim.tx  ALL=(ALL)       NOPASSWD: ALL\n'
    )},
    '/etc/pam.d/su': {'mode': '0644', 'body': (
        '#auth       required        pam_wheel.so use_uid\n'
        'auth        substack        system-auth\n'
    )},
}

HOST = {'name': 'fin-batch-02', 'os': 'Red Hat Enterprise Linux 8.8',
        'procs': [{'pid': 1001, 'cmd': '/usr/sbin/sshd -D'}],
        'ports': [{'port': 22, 'svc': 'sshd'}], 'pkgs': {}}

LABS = [{
    'key': 'account', 'file': '07_srv-account.html', 'code': 'SRV-ACCOUNT',
    'title': '계정·비밀번호',
    'desc': 'passwd·shadow·group·PAM·sudoers 를 직접 읽어 UID 중복, 빈 비밀번호, 약한 해시, '
            '잠금 정책, 권한 상승 경로를 판정하고 조치하는 실습입니다.',
    'host': HOST, 'fs': FS,
    'missions': [
        {
            'id': 'SRV-046', 'risk': 4, 'title': '동일 식별번호를 가진 계정 제거',
            'brief': '리눅스는 계정 이름이 아니라 <b>UID 로 권한을 판단</b>합니다. UID 0 인 계정이 하나 더 있으면 '
                     '이름만 다를 뿐 root 와 똑같은 권한을 가집니다.',
            'where': '/etc/passwd 의 세 번째 필드(UID)',
            'hint': 'UID 가 0 인 줄이 몇 개인지 세어 보세요.',
            'cmds': ['grep -E ":0:0:" /etc/passwd', 'cat /etc/passwd'],
            'options': ['batchadm 의 UID 가 0 (root 와 동일)', 'root 만 UID 0',
                        'ftp 계정에 /bin/bash 셸', 'guestops 에 비밀번호 없음'],
            'evidence': ['batchadm 의 UID 가 0 (root 와 동일)'],
            'verdict': "function(fs){var b=fs.read('/etc/passwd')||'';"
                       "var n=b.split('\\n').filter(function(l){return /^[^:]+:[^:]*:0:/.test(l);}).length;"
                       "return n>1?'vuln':'good';}",
            'why': 'batchadm 의 UID 가 0 이라 root 와 동일한 권한을 갖습니다. 배치 운영 계정이라도 '
                   '고유 UID 를 주고 필요한 권한만 sudo 로 위임해야 감사 로그에서 주체가 구분됩니다.',
            'fix': "function(fs){var b=fs.read('/etc/passwd');"
                   "fs.write('/etc/passwd', b.replace('batchadm:x:0:0:','batchadm:x:1005:1005:'));}",
            'fixNote': 'batchadm 의 UID/GID 를 1005 로 바꿨습니다.',
        },
        {
            'id': 'SRV-037', 'risk': 3, 'title': '비밀번호가 설정되지 않은 계정 제거',
            'brief': 'shadow 의 비밀번호 칸이 비어 있으면 <b>아무 비밀번호 없이 로그인</b>이 됩니다. '
                     '테스트용으로 만들고 지우지 않은 계정에서 자주 나옵니다.',
            'where': '/etc/shadow 의 두 번째 필드',
            'hint': '콜론 두 개가 연달아 나오는 줄을 찾아보세요.',
            'cmds': ['cat /etc/shadow'],
            'options': ['guestops 의 비밀번호 필드가 비어 있음', '모든 계정에 해시가 있음',
                        'svc_settle 의 해시가 $1$', 'root 해시가 $6$'],
            'evidence': ['guestops 의 비밀번호 필드가 비어 있음'],
            'verdict': "function(fs){var b=fs.read('/etc/shadow')||'';"
                       "return b.split('\\n').some(function(l){return /^[^:]+::/.test(l);})?'vuln':'good';}",
            'why': 'guestops 계정의 비밀번호 필드가 비어 있어 인증 없이 로그인할 수 있습니다. '
                   '쓰지 않는 계정이면 지우고, 써야 한다면 잠그거나 비밀번호를 설정해야 합니다.',
            'fix': "function(fs){var b=fs.read('/etc/shadow');"
                   "fs.write('/etc/shadow', b.replace('guestops::','guestops:!LOCKED!:'));}",
            'fixNote': 'guestops 계정을 잠갔습니다(passwd -l).',
        },
        {
            'id': 'SRV-040', 'risk': 5, 'title': '비밀번호 저장 시 안전한 해시 사용',
            'brief': '비밀번호는 해시로 저장되는데 <b>해시 방식이 약하면</b> 파일이 유출됐을 때 '
                     '원문을 되찾는 데 걸리는 시간이 크게 줄어듭니다. <code>$1$</code> 은 MD5 입니다.',
            'where': '/etc/shadow 해시 접두사, /etc/login.defs 의 ENCRYPT_METHOD',
            'hint': '해시가 $6$ 이 아닌 계정을 찾아보세요.',
            'cmds': ['cat /etc/shadow', 'grep ENCRYPT /etc/login.defs'],
            'options': ['svc_settle 이 $1$ (MD5) 해시', '모두 $6$ (SHA-512)',
                        'ENCRYPT_METHOD SHA512', 'PASS_MIN_LEN 5'],
            'evidence': ['svc_settle 이 $1$ (MD5) 해시'],
            'verdict': "function(fs){var b=fs.read('/etc/shadow')||'';"
                       "return /:\\$1\\$/.test(b)?'vuln':'good';}",
            'why': 'ENCRYPT_METHOD 는 SHA512 로 맞춰져 있는데 svc_settle 만 MD5($1$) 해시입니다. '
                   '설정을 바꿔도 <b>이미 저장된 해시는 그대로</b>이고, 비밀번호를 다시 설정해야 바뀝니다.',
            'fix': "function(fs){var b=fs.read('/etc/shadow');"
                   "fs.write('/etc/shadow', b.replace('svc_settle:$1$abc$Xy9...','svc_settle:$6$Rt7v$Kd2...'));}",
            'fixNote': 'svc_settle 의 비밀번호를 재설정해 SHA-512 해시로 다시 저장했습니다.',
        },
        {
            'id': 'SRV-039', 'risk': 5, 'title': '비밀번호 복잡도 강제',
            'brief': '복잡도 규칙 파일이 있어도 <b>전부 주석 처리돼 있으면 적용되지 않습니다</b>. '
                     '파일이 존재한다는 것과 규칙이 동작한다는 것은 다릅니다.',
            'where': '/etc/security/pwquality.conf',
            'hint': '설정 줄 앞에 # 이 붙어 있는지 보세요.',
            'cmds': ['cat /etc/security/pwquality.conf', 'grep PASS_MIN_LEN /etc/login.defs'],
            'options': ['pwquality 설정이 전부 주석 처리됨', 'minlen = 8 적용 중',
                        'ENCRYPT_METHOD SHA512', 'PASS_MIN_DAYS 0'],
            'evidence': ['pwquality 설정이 전부 주석 처리됨'],
            'verdict': "function(fs){var b=fs.read('/etc/security/pwquality.conf')||'';"
                       "return /^\\s*minlen\\s*=\\s*\\d+/m.test(b)?'good':'vuln';}",
            'why': 'pwquality.conf 의 모든 규칙이 주석 처리돼 있어 복잡도 검사가 동작하지 않습니다. '
                   'login.defs 의 PASS_MIN_LEN 5 도 금융권 기준으로는 짧습니다.',
            'fix': "function(fs){fs.write('/etc/security/pwquality.conf',"
                   "'minlen = 8\\ndcredit = -1\\nucredit = -1\\nlcredit = -1\\nocredit = -1\\n');}",
            'fixNote': 'pwquality 규칙(최소 8자 + 4종 조합)을 적용했습니다.',
        },
        {
            'id': 'SRV-038', 'risk': 5, 'title': '비밀번호 사용 정책 적용',
            'brief': '비밀번호를 <b>한 번 만들면 영원히 쓰는</b> 설정입니다. 유출을 눈치채지 못한 채 '
                     '오래 쓰면 그만큼 악용 기간이 길어집니다.',
            'where': '/etc/login.defs 의 PASS_MAX_DAYS',
            'hint': 'PASS_MAX_DAYS 값이 몇 인지 보세요.',
            'cmds': ['grep PASS_ /etc/login.defs'],
            'options': ['PASS_MAX_DAYS 99999 (사실상 무기한)', 'PASS_MAX_DAYS 90',
                        'PASS_MIN_DAYS 0', 'ENCRYPT_METHOD SHA512'],
            'evidence': ['PASS_MAX_DAYS 99999 (사실상 무기한)'],
            'verdict': "function(fs){var b=fs.read('/etc/login.defs')||'';"
                       "var m=b.match(/^\\s*PASS_MAX_DAYS\\s+(\\d+)/m);"
                       "return m&&parseInt(m[1],10)<=90?'good':'vuln';}",
            'why': 'PASS_MAX_DAYS 가 99999 라 비밀번호를 바꾸지 않아도 됩니다. '
                   '내부 규정이 없다면 90일 이내가 일반적인 기준입니다.',
            'fix': "function(fs){var b=fs.read('/etc/login.defs');"
                   "fs.write('/etc/login.defs', b.replace('PASS_MAX_DAYS   99999','PASS_MAX_DAYS   90'));}",
            'fixNote': 'PASS_MAX_DAYS 를 90 으로 바꿨습니다.',
        },
        {
            'id': 'SRV-041', 'risk': 4, 'title': '로그인 실패 횟수에 따른 계정 잠금',
            'brief': '실패 횟수 제한이 없으면 자동화 도구가 <b>시간만 들이면 계속 시도</b>할 수 있습니다. '
                     '일정 횟수 실패 시 일시적으로 잠기게 해야 합니다.',
            'where': '/etc/pam.d/system-auth 의 pam_faillock',
            'hint': 'faillock 관련 줄이 있는지 보세요.',
            'cmds': ['cat /etc/pam.d/system-auth'],
            'options': ['pam_faillock 설정이 없음', 'deny=5 unlock_time=600 적용 중',
                        'pam_env.so 사용', 'pam_unix.so sha512'],
            'evidence': ['pam_faillock 설정이 없음'],
            'verdict': "function(fs){var b=fs.read('/etc/pam.d/system-auth')||'';"
                       "return /pam_faillock\\.so|pam_tally2?\\.so/.test(b)?'good':'vuln';}",
            'why': '계정 잠금 모듈이 없어 실패 횟수 제한이 걸리지 않습니다. '
                   '참고로 <code>pam_unix.so nullok</code> 도 함께 보이는데, 빈 비밀번호 로그인을 허용하는 옵션입니다.',
            'fix': "function(fs){var b=fs.read('/etc/pam.d/system-auth');"
                   "fs.write('/etc/pam.d/system-auth', b.replace('# 계정 잠금(pam_faillock) 미설정',"
                   "'auth        required      pam_faillock.so preauth deny=5 unlock_time=600\\n"
                   "account     required      pam_faillock.so').replace(' nullok',''));}",
            'fixNote': 'pam_faillock(5회 실패 시 10분 잠금)을 적용하고 nullok 옵션을 제거했습니다.',
        },
        {
            'id': 'SRV-047', 'risk': 1, 'title': '대화형 셸이 필요 없는 계정의 셸 제거',
            'brief': '서비스 전용 계정에 로그인 셸이 있으면 <b>그 계정이 탈취됐을 때 바로 명령을 실행</b>할 수 있습니다.',
            'where': '/etc/passwd 의 마지막 필드',
            'hint': 'ftp 같은 서비스 계정의 셸을 보세요.',
            'cmds': ['grep -E "^(ftp|bin|daemon)" /etc/passwd'],
            'options': ['ftp 계정에 /bin/bash 가 부여됨', 'bin·daemon 은 nologin',
                        'kim.tx 에 /bin/bash', 'root 에 /bin/bash'],
            'evidence': ['ftp 계정에 /bin/bash 가 부여됨'],
            'verdict': "function(fs){var b=fs.read('/etc/passwd')||'';"
                       "return /^ftp:[^\\n]*\\/bin\\/(ba)?sh\\s*$/m.test(b)?'vuln':'good';}",
            'why': 'ftp 서비스 계정에 /bin/bash 가 부여돼 있습니다. bin·daemon 처럼 nologin 으로 바꾸면 '
                   '계정이 탈취돼도 셸을 얻지 못합니다.',
            'fix': "function(fs){var b=fs.read('/etc/passwd');"
                   "fs.write('/etc/passwd', b.replace('ftp:x:14:50:FTP User:/var/ftp:/bin/bash',"
                   "'ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin'));}",
            'fixNote': 'ftp 계정의 셸을 /sbin/nologin 으로 바꿨습니다.',
        },
        {
            'id': 'SRV-049', 'risk': 3, 'title': '권한 상승 명령 사용 가능 그룹 제한',
            'brief': 'su 를 아무나 쓸 수 있으면 <b>root 비밀번호를 아는 사람 수만큼</b> 관리자가 늘어납니다.',
            'where': '/etc/pam.d/su 의 pam_wheel',
            'hint': 'pam_wheel 줄이 주석 처리돼 있는지 보세요.',
            'cmds': ['cat /etc/pam.d/su', 'grep wheel /etc/group'],
            'options': ['pam_wheel.so 가 주석 처리됨', 'pam_wheel.so 적용 중',
                        'wheel 그룹에 4명', 'sshusers 에 kim.tx'],
            'evidence': ['pam_wheel.so 가 주석 처리됨'],
            'verdict': "function(fs){var b=fs.read('/etc/pam.d/su')||'';"
                       "return /^\\s*auth\\s+required\\s+pam_wheel\\.so/m.test(b)?'good':'vuln';}",
            'why': 'pam_wheel 줄이 주석 처리돼 있어 모든 사용자가 su 를 시도할 수 있습니다. '
                   '주석을 풀면 wheel 그룹 구성원만 su 를 쓸 수 있습니다.',
            'fix': "function(fs){var b=fs.read('/etc/pam.d/su');"
                   "fs.write('/etc/pam.d/su', b.replace('#auth       required        pam_wheel.so use_uid',"
                   "'auth       required        pam_wheel.so use_uid'));}",
            'fixNote': 'pam_wheel.so 주석을 해제해 wheel 그룹만 su 를 쓰도록 했습니다.',
        },
        {
            'id': 'SRV-050', 'risk': 3, 'title': '대리 실행 권한 설정의 최소화',
            'brief': '<code>NOPASSWD: ALL</code> 은 <b>비밀번호도 묻지 않고 모든 명령</b>을 root 로 실행하게 합니다. '
                     '그 계정이 탈취되면 추가 인증 없이 곧바로 서버 전체를 잃습니다.',
            'where': '/etc/sudoers',
            'hint': 'NOPASSWD 가 붙은 줄을 찾아보세요.',
            'cmds': ['cat /etc/sudoers'],
            'options': ['kim.tx 에 NOPASSWD: ALL 부여', '%wheel 에만 sudo 허용',
                        'root ALL=(ALL) ALL', 'sudoers 권한이 0440'],
            'evidence': ['kim.tx 에 NOPASSWD: ALL 부여'],
            'verdict': "function(fs){var b=fs.read('/etc/sudoers')||'';"
                       "return /NOPASSWD:\\s*ALL/.test(b)?'vuln':'good';}",
            'why': 'kim.tx 계정에 NOPASSWD: ALL 이 부여돼 있습니다. 꼭 필요하다면 '
                   '<b>실행할 명령을 하나씩 지정</b>하고 비밀번호 확인은 남겨 두어야 합니다.',
            'fix': "function(fs){var b=fs.read('/etc/sudoers');"
                   "fs.write('/etc/sudoers', b.replace('kim.tx  ALL=(ALL)       NOPASSWD: ALL',"
                   "'kim.tx  ALL=(ALL)       /usr/bin/systemctl restart batchd'));}",
            'fixNote': 'kim.tx 의 sudo 권한을 필요한 명령 하나로 좁혔습니다.',
        },
        {
            'id': 'SRV-043', 'risk': 4, 'title': '관리자 그룹 구성원 최소화',
            'brief': '관리자 그룹에 사람이 많을수록 <b>탈취될 수 있는 관리자 계정도 많아집니다</b>.',
            'where': '/etc/group 의 root·wheel 그룹',
            'hint': 'root 그룹의 마지막 칸에 누가 들어 있는지 보세요.',
            'cmds': ['grep -E "^(root|wheel):" /etc/group'],
            'options': ['root 그룹에 batchadm·kim.tx 가 포함됨', 'root 그룹에 root 만 있음',
                        'oldteam 이 비어 있음', 'sshusers 에 1명'],
            'evidence': ['root 그룹에 batchadm·kim.tx 가 포함됨'],
            'verdict': "function(fs){var b=fs.read('/etc/group')||'';"
                       "var m=b.match(/^root:x:0:(.*)$/m); if(!m) return 'good';"
                       "var mem=m[1].split(',').filter(function(x){return x&&x!=='root';});"
                       "return mem.length>0?'vuln':'good';}",
            'why': 'root 그룹에 batchadm 과 kim.tx 가 들어 있습니다. 관리자 권한이 필요하면 '
                   'sudo 로 필요한 명령만 위임하는 편이 추적과 회수 모두 쉽습니다.',
            'fix': "function(fs){var b=fs.read('/etc/group');"
                   "fs.write('/etc/group', b.replace('root:x:0:root,batchadm,kim.tx','root:x:0:root'));}",
            'fixNote': 'root 그룹에서 batchadm·kim.tx 를 제외했습니다.',
        },
        {
            'id': 'SRV-044', 'risk': 4, 'title': '미사용·퇴직자 계정 정리',
            'brief': '퇴직자 계정이 남아 있으면 <b>아무도 쓰지 않는데 로그인은 되는</b> 상태가 됩니다. '
                     '감시가 느슨한 만큼 공격자에게는 조용한 통로입니다.',
            'where': '/etc/passwd 의 설명 칸, /etc/shadow 의 잠금 여부',
            'hint': 'passwd 설명 칸(GECOS)과 shadow 의 해시 앞 느낌표를 같이 보세요.',
            'cmds': ['cat /etc/passwd', 'cat /etc/shadow'],
            'options': ['lee.old 이 퇴사 표기인데 계정이 잠기지 않음', '모든 계정이 재직자',
                        'guestops 에 비밀번호 없음', 'svc_settle 이 서비스 계정'],
            'evidence': ['lee.old 이 퇴사 표기인데 계정이 잠기지 않음'],
            'verdict': "function(fs){var p=fs.read('/etc/passwd')||'',s=fs.read('/etc/shadow')||'';"
                       "if(!/^lee\\.old:/m.test(p)) return 'good';"
                       "return /^lee\\.old:!/m.test(s)?'good':'vuln';}",
            'why': 'lee.old 설명에 퇴사 표기가 있는데 비밀번호가 그대로 살아 있습니다. '
                   '인사 정보와 계정 상태가 이어져 있지 않으면 이런 계정이 계속 쌓입니다.',
            'fix': "function(fs){var s=fs.read('/etc/shadow');"
                   "fs.write('/etc/shadow', s.replace('lee.old:$6$Wp3z$Lm4...','lee.old:!$6$Wp3z$Lm4...'));}",
            'fixNote': 'lee.old 계정을 잠갔습니다(보존 기간 후 삭제).',
        },
        {
            'id': 'SRV-048', 'risk': 2, 'title': '구성원이 없는 그룹 정리',
            'brief': '구성원이 없는 그룹은 <b>그 그룹 권한으로 남은 파일</b>이 어디에 있는지 모르게 만듭니다. '
                     '나중에 같은 GID 가 재사용되면 의도치 않은 접근이 생깁니다.',
            'where': '/etc/group',
            'hint': '마지막 칸이 비어 있는 그룹을 찾아보세요.',
            'cmds': ['cat /etc/group'],
            'options': ['oldteam 그룹에 구성원이 없음', '모든 그룹에 구성원이 있음',
                        'wheel 에 4명', 'root 에 3명'],
            'evidence': ['oldteam 그룹에 구성원이 없음'],
            'verdict': "function(fs){var b=fs.read('/etc/group')||'';"
                       "return b.split('\\n').some(function(l){return /^oldteam:/.test(l)&&/:$/.test(l);})?'vuln':'good';}",
            'why': 'oldteam 그룹에 구성원이 없습니다. 지우기 전에 그 GID 로 남은 파일이 있는지 먼저 확인해야 '
                   '삭제 후 접근 문제가 생기지 않습니다.',
            'fix': "function(fs){var b=fs.read('/etc/group');"
                   "fs.write('/etc/group', b.split('\\n').filter(function(l){return !/^oldteam:/.test(l);}).join('\\n'));}",
            'fixNote': 'oldteam 그룹을 삭제했습니다(잔여 파일 확인 후).',
        },
    ],
}]
