# -*- coding: utf-8 -*-
"""금융 서버 진단 실습 — Windows 모의 호스트 2대.

리눅스 랩과 흐름은 같다(확인 → 판정 + 근거 → 조치 → 재점검). 다른 것은 확인 수단이다.
Windows 는 설정이 파일이 아니라 **레지스트리·로컬 보안 정책·서비스·공유**에 있으므로
판정 함수는 fs 대신 fs.host 의 reg/policy/services/shares/tasks/disks 를 읽는다.
그래서 조치를 적용하면 같은 명령의 출력이 실제로 바뀐다.

담는 항목은 리눅스 셸로는 판정할 수 없어 기존 5개 랩에서 빠졌던 것들이다.
항목이 "무엇을 보는가"라는 구조만 참고했고 시나리오·설정값·해설은 전부 새로 썼다.
"""

# ── 랩 A: 계정·보안 정책 ────────────────────────────────────────────────
HOST_A = {
    'name': 'FIN-WIN-01', 'os': 'Windows Server 2019 Standard', 'platform': 'windows',
    'today': '2026-09-15',
    'procs': [
        {'pid': 640, 'cmd': 'lsass.exe'},
        {'pid': 1180, 'cmd': 'svchost.exe'},
        {'pid': 2244, 'cmd': 'FinSettleSvc.exe'},
    ],
    'ports': [], 'pkgs': {}, 'hidden': [], 'disks': [],
    'reg': {
        r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RestrictAnonymous': 0,
        r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\RestrictAnonymousSAM': 0,
        r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\EveryoneIncludesAnonymous': 1,
        r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LmCompatibilityLevel': 1,
        r'HKLM\SYSTEM\CurrentControlSet\Control\Lsa\CrashOnAuditFail': 1,
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\AutoAdminLogon': '1',
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\DefaultUserName': 'Administrator',
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\DefaultPassword': 'W1nt3r-2026-fin',
        r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\ShutdownWithoutLogon': 1,
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\DontDisplayLastUserName': 0,
        r'HKLM\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters\RequireSignOrSeal': 0,
        r'HKLM\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters\SealSecureChannel': 1,
        r'HKLM\SOFTWARE\Policies\Microsoft\Windows\Control Panel\Desktop\ScreenSaveActive': '0',
        r'HKLM\SOFTWARE\Policies\Microsoft\Windows\Control Panel\Desktop\ScreenSaverIsSecure': '0',
        r'HKLM\SOFTWARE\Policies\Microsoft\Windows\Control Panel\Desktop\ScreenSaveTimeOut': '3600',
        r'HKLM\SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices\Deny_All': 0,
    },
    'policy': {
        'LSAAnonymousNameLookup': 1,
        'SeInteractiveLogonRight': 'Administrators,Users,Guest',
        'SeNetworkLogonRight': 'Everyone,Administrators,Users',
        'SeDenyNetworkLogonRight': '(없음)',
        'SeBackupPrivilege': 'Administrators,Users',
        'SeTakeOwnershipPrivilege': 'Administrators,Everyone',
        'SeLoadDriverPrivilege': 'Administrators,Users',
    },
    'users': {
        'Administrator': {'enabled': True, 'pwSet': '2024-03-11', 'groups': ['Administrators']},
        'Guest': {'enabled': True, 'pwSet': '-', 'groups': ['Guests']},
        'svc_settle': {'enabled': True, 'pwSet': '2026-08-02', 'groups': ['Users']},
        'ops.kim': {'enabled': True, 'pwSet': '2026-09-01', 'groups': ['Users']},
    },
    'groups': {
        'Administrators': ['Administrator'],
        'Users': ['svc_settle', 'ops.kim'],
        'Guests': ['Guest'],
    },
    'acl': {
        'C:\\fin\\keys': ['Everyone:(F)', 'BUILTIN\\Administrators:(F)', 'NT AUTHORITY\\SYSTEM:(F)'],
        'C:\\fin\\app': ['BUILTIN\\Administrators:(F)', 'BUILTIN\\Users:(RX)'],
    },
    'services': {}, 'shares': {}, 'tasks': [],
}

LAB_A = {
    'key': 'windows', 'file': '07_srv-windows.html', 'code': 'SRV-WINDOWS',
    'title': 'Windows 계정·보안 정책',
    'desc': 'Windows 금융 업무 서버의 계정, 로컬 보안 정책, 레지스트리 보안 설정을 '
            'reg query · net user · secedit 로 직접 확인하고 판정·조치하는 실습입니다.',
    'host': HOST_A, 'fs': {},
    'missions': [
        {
            'id': 'SRV-042', 'risk': 4, 'title': '기본 관리자 계정명 변경',
            'brief': 'Windows 의 <code>Administrator</code> 는 <b>이름이 이미 알려진 관리자 계정</b>입니다. '
                     '공격자는 계정명을 맞힐 필요 없이 비밀번호만 반복해서 시도하면 됩니다.',
            'where': '로컬 계정 목록',
            'hint': 'net user 로 나오는 계정 이름 중 기본값 그대로인 것을 찾으세요.',
            'cmds': ['net user', 'net localgroup Administrators'],
            'options': ['Administrator 라는 기본 계정명이 그대로 있음', '관리자 계정명이 변경되어 있음',
                        'Guest 가 활성 상태', 'ops.kim 이 Users 소속'],
            'evidence': ['Administrator 라는 기본 계정명이 그대로 있음'],
            'verdict': "function(fs){return fs.host.users['Administrator']?'vuln':'good';}",
            'why': '기본 계정명이 그대로입니다. 이름을 바꾼다고 비밀번호가 강해지지는 않지만, '
                   '자동화된 대입 공격이 전제하는 "계정명은 안다"를 깨뜨립니다. '
                   '비밀번호 정책·잠금 정책과 함께 써야 의미가 있습니다.',
            'fix': "function(fs){var h=fs.host;"
                   "h.users['adm_fin01']=h.users['Administrator']; delete h.users['Administrator'];"
                   "h.groups['Administrators']=h.groups['Administrators'].map("
                   "function(x){return x==='Administrator'?'adm_fin01':x;});"
                   "h.reg['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\Winlogon\\\\DefaultUserName']='adm_fin01';}",
            'fixNote': '기본 관리자 계정명을 adm_fin01 로 변경했습니다.',
        },
        {
            'id': 'SRV-045', 'risk': 4, 'title': '손님 계정 비활성화',
            'brief': 'Guest 는 <b>비밀번호 없이 쓰도록 만들어진 계정</b>입니다. 권한이 낮아도 '
                     '내부 정찰의 출발점이 되기에는 충분합니다.',
            'where': 'Guest 계정 상태',
            'hint': 'net user Guest 의 "계정 사용" 줄을 보세요.',
            'cmds': ['net user Guest', 'net localgroup Guests'],
            'options': ['Guest 계정이 사용(Yes) 상태', 'Guest 계정이 사용 안 함',
                        'Guest 가 Guests 그룹 소속', 'Guest 의 암호 설정 이력이 없음'],
            'evidence': ['Guest 계정이 사용(Yes) 상태'],
            'verdict': "function(fs){var g=fs.host.users['Guest']; return (g&&g.enabled)?'vuln':'good';}",
            'why': 'Guest 가 활성 상태입니다. 업무상 쓰는 일이 없으므로 비활성화가 기본입니다. '
                   '"소속 그룹이 Guests 라 권한이 낮다"는 것은 근거가 되지 않습니다. '
                   '문제는 권한 수준이 아니라 인증 없이 발판이 생긴다는 점입니다.',
            'fix': "function(fs){fs.host.users['Guest'].enabled=false;}",
            'fixNote': 'Guest 계정을 비활성화했습니다.',
        },
        {
            'id': 'SRV-035', 'risk': 3, 'title': '로컬 콘솔 로그인 허용 계정 제한',
            'brief': '로컬 로그온 권한이 <b>넓은 그룹과 Guest 까지</b> 열려 있습니다. '
                     '콘솔이나 원격 데스크톱에 닿을 수 있는 사람이면 누구나 들어올 수 있다는 뜻입니다.',
            'where': '로컬 보안 정책 SeInteractiveLogonRight',
            'hint': '허용 목록에 Guest 가 들어 있는지 보세요.',
            'cmds': ['secedit /export /cfg secpol.txt', 'net user Guest'],
            'options': ['SeInteractiveLogonRight 에 Guest 가 포함됨', '관리자 그룹만 허용됨',
                        'Guest 가 비활성 상태', 'SeBackupPrivilege 에 Users 포함'],
            'evidence': ['SeInteractiveLogonRight 에 Guest 가 포함됨'],
            'verdict': "function(fs){return /Guest|Everyone/.test(fs.host.policy.SeInteractiveLogonRight||'')?'vuln':'good';}",
            'why': '로컬 로그온 허용 목록에 Guest 가 있습니다. 이 서버에서 실제로 콘솔 작업을 하는 '
                   '계정만 남기고, 나머지는 명시적으로 빼야 합니다.',
            'fix': "function(fs){fs.host.policy.SeInteractiveLogonRight='Administrators,FIN-Ops';}",
            'fixNote': '로컬 로그온 허용을 관리자와 운영 그룹으로 좁혔습니다.',
        },
        {
            'id': 'SRV-051', 'risk': 5, 'title': '익명·전체 사용자 권한 부여 제거',
            'brief': '키 자료가 들어 있는 폴더에 <b>Everyone 모든 권한(F)</b>이 걸려 있습니다. '
                     '이 서버에 로그온할 수 있는 누구든 키를 읽고 바꾸고 지울 수 있습니다.',
            'where': 'C:\\fin\\keys 의 접근 권한',
            'hint': 'cacls 출력에서 Everyone 항목의 권한 문자를 보세요. (F) 는 모든 권한입니다.',
            'cmds': ['cacls C:\\fin\\keys', 'cacls C:\\fin\\app'],
            'options': ['C:\\fin\\keys 에 Everyone:(F) 가 부여됨', 'Administrators 와 SYSTEM 만 있음',
                        'C:\\fin\\app 은 Users 가 읽기·실행', 'Everyone 이 읽기만 가능'],
            'evidence': ['C:\\fin\\keys 에 Everyone:(F) 가 부여됨'],
            'verdict': "function(fs){var a=(fs.host.acl||{})['C:\\\\fin\\\\keys']||[];"
                       "return a.some(function(x){return /^Everyone:\\(F\\)/.test(x);})?'vuln':'good';}",
            'why': '전체 사용자에게 모든 권한을 준 경로가 있습니다. Everyone 은 "이 컴퓨터를 쓰는 모든 계정"이고, '
                   '익명 접속을 Everyone 에 포함하도록 설정한 서버에서는 인증조차 필요 없어집니다. '
                   'Everyone 항목 자체를 지우고 필요한 그룹에만 최소 권한을 줍니다.',
            'fix': "function(fs){var h=fs.host;"
                   "h.acl['C:\\\\fin\\\\keys']=h.acl['C:\\\\fin\\\\keys'].filter("
                   "function(x){return !/^Everyone/.test(x);});"
                   "h.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\EveryoneIncludesAnonymous']=0;}",
            'fixNote': 'Everyone 권한을 제거하고, 익명을 Everyone 에 포함하는 설정도 함께 껐습니다.',
        },
        {
            'id': 'SRV-052', 'risk': 5, 'title': '익명 접속을 통한 계정·공유 목록 조회 차단',
            'brief': '익명 제한이 꺼져 있으면 <b>인증 없이 계정 이름과 공유 목록을 열거</b>할 수 있습니다. '
                     '공격자가 가장 먼저 하는 일이 이 정찰입니다.',
            'where': 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa',
            'hint': 'RestrictAnonymous 와 RestrictAnonymousSAM 을 함께 보세요. 둘 다 1 이어야 합니다.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa"'],
            'options': ['RestrictAnonymous·RestrictAnonymousSAM 이 모두 0', '둘 다 1 로 설정됨',
                        'CrashOnAuditFail 이 1', 'LmCompatibilityLevel 이 1'],
            'evidence': ['RestrictAnonymous·RestrictAnonymousSAM 이 모두 0'],
            'verdict': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\',r=fs.host.reg;"
                       "return (r[b+'RestrictAnonymous']===1&&r[b+'RestrictAnonymousSAM']===1)?'good':'vuln';}",
            'why': '익명 열거가 모두 허용돼 있습니다. 계정 이름 목록이 새면 다음 단계는 비밀번호 대입입니다. '
                   '두 값을 1 로 두어 익명 세션이 계정 목록과 공유 목록을 읽지 못하게 합니다.',
            'fix': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\',r=fs.host.reg;"
                   "r[b+'RestrictAnonymous']=1; r[b+'RestrictAnonymousSAM']=1;}",
            'fixNote': 'RestrictAnonymous·RestrictAnonymousSAM 을 1 로 설정했습니다.',
        },
        {
            'id': 'SRV-053', 'risk': 3, 'title': '익명 식별자 변환 요청 차단',
            'brief': '익명 요청에 대해 <b>보안 식별자와 계정 이름을 서로 변환</b>해 주면, '
                     '인증 없이 관리자 계정의 실제 이름을 알아낼 수 있습니다.',
            'where': '로컬 보안 정책 LSAAnonymousNameLookup',
            'hint': '0 이어야 익명 변환 요청을 거부합니다.',
            'cmds': ['secedit /export /cfg secpol.txt'],
            'options': ['LSAAnonymousNameLookup 이 1 (익명 변환 허용)', '값이 0',
                        'SeNetworkLogonRight 에 Everyone 포함', 'SeBackupPrivilege 에 Users 포함'],
            'evidence': ['LSAAnonymousNameLookup 이 1 (익명 변환 허용)'],
            'verdict': "function(fs){return fs.host.policy.LSAAnonymousNameLookup===0?'good':'vuln';}",
            'why': '익명 식별자·이름 변환이 허용돼 있습니다. 잘 알려진 식별자 접미사로 조회하면 '
                   '계정명을 바꿔 두었더라도 실제 이름이 그대로 돌아옵니다. '
                   'SRV-042 의 조치를 무력화하는 설정이라 함께 봐야 합니다.',
            'fix': "function(fs){fs.host.policy.LSAAnonymousNameLookup=0;}",
            'fixNote': 'LSAAnonymousNameLookup 을 0 으로 설정했습니다.',
        },
        {
            'id': 'SRV-054', 'risk': 3, 'title': '마지막 로그인 계정명 표시 제거',
            'brief': '로그온 화면에 <b>마지막에 로그인한 계정 이름</b>이 남아 있으면 '
                     '화면을 보는 것만으로 유효한 계정 하나를 알려 주는 셈입니다.',
            'where': 'HKLM\\...\\Policies\\System\\DontDisplayLastUserName',
            'hint': '1 이어야 표시하지 않습니다.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DontDisplayLastUserName'],
            'options': ['DontDisplayLastUserName 이 0 (계정명 노출)', '값이 1',
                        'AutoAdminLogon 이 1', 'ScreenSaveActive 가 0'],
            'evidence': ['DontDisplayLastUserName 이 0 (계정명 노출)'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System\\\\DontDisplayLastUserName']===1?'good':'vuln';}",
            'why': '마지막 로그온 계정명이 화면에 남습니다. 서버실 출입자나 원격 데스크톱 화면을 '
                   '어깨너머로 보는 사람에게 계정명을 그대로 내주게 됩니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Policies\\\\System\\\\DontDisplayLastUserName']=1;}",
            'fixNote': 'DontDisplayLastUserName 을 1 로 설정했습니다.',
        },
        {
            'id': 'SRV-086', 'risk': 3, 'title': '구형 인증 프로토콜 수준 제한',
            'brief': '네트워크 인증 호환 수준이 낮으면 <b>구형 응답 형식</b>을 그대로 주고받습니다. '
                     '가로챈 응답에서 원래 비밀번호를 복원하기가 훨씬 쉬워집니다.',
            'where': 'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\LmCompatibilityLevel',
            'hint': '3 이상이어야 구형 응답을 보내지 않습니다.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v LmCompatibilityLevel'],
            'options': ['LmCompatibilityLevel 이 1 (구형 응답 허용)', '값이 5',
                        'RequireSignOrSeal 이 0', 'RestrictAnonymous 가 0'],
            'evidence': ['LmCompatibilityLevel 이 1 (구형 응답 허용)'],
            'verdict': "function(fs){var v=fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\LmCompatibilityLevel'];"
                       "return (typeof v==='number'&&v>=3)?'good':'vuln';}",
            'why': '수준 1 은 옛 방식과 현재 방식 응답을 함께 보냅니다. 값을 올리기 전에 구형 단말·장비가 '
                   '붙어 있는지 먼저 확인하세요. 호환성 때문에 낮춰 둔 값이 그대로 남아 있는 경우가 많습니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\LmCompatibilityLevel']=5;}",
            'fixNote': 'LmCompatibilityLevel 을 5(최신 방식 전용)로 올렸습니다.',
        },
        {
            'id': 'SRV-087', 'risk': 3, 'title': '보안 채널 데이터의 암호화·서명 적용',
            'brief': '도메인 구성원과 인증 서버 사이의 <b>보안 채널</b>에 서명·암호화가 '
                     '강제되지 않으면, 협상이 실패했을 때 보호 없이 그냥 진행됩니다.',
            'where': 'HKLM\\...\\Netlogon\\Parameters\\RequireSignOrSeal',
            'hint': '개별 옵션이 켜져 있어도 "항상 요구"가 0 이면 평문으로 내려갈 수 있습니다.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters"'],
            'options': ['RequireSignOrSeal 이 0 (평문 강등 가능)', '값이 1',
                        'SealSecureChannel 이 1', 'LmCompatibilityLevel 이 1'],
            'evidence': ['RequireSignOrSeal 이 0 (평문 강등 가능)'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\Netlogon\\\\Parameters\\\\RequireSignOrSeal']===1?'good':'vuln';}",
            'why': 'SealSecureChannel 이 1 이라 "암호화하도록 설정돼 있다"고 보기 쉽지만, '
                   'RequireSignOrSeal 이 0 이면 상대가 지원하지 않을 때 보호 없이 진행합니다. '
                   '<b>가능하면 한다</b>와 <b>항상 한다</b>는 다릅니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\Netlogon\\\\Parameters\\\\RequireSignOrSeal']=1;}",
            'fixNote': 'RequireSignOrSeal 을 1 로 설정했습니다.',
        },
        {
            'id': 'SRV-088', 'risk': 4, 'title': '자동 로그온 설정 해제',
            'brief': '자동 로그온이 켜져 있으면 <b>비밀번호가 레지스트리에 평문으로</b> 저장됩니다. '
                     '재부팅만 해도 관리자 세션이 자동으로 열립니다.',
            'where': 'HKLM\\...\\Winlogon',
            'hint': 'AutoAdminLogon 과 DefaultPassword 를 함께 보세요.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon"'],
            'options': ['AutoAdminLogon 이 1 이고 DefaultPassword 가 평문으로 저장됨', 'AutoAdminLogon 이 0',
                        'DefaultUserName 이 Administrator', 'ShutdownWithoutLogon 이 1'],
            'evidence': ['AutoAdminLogon 이 1 이고 DefaultPassword 가 평문으로 저장됨'],
            'verdict': "function(fs){var b='HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\Winlogon\\\\',r=fs.host.reg;"
                       "return (String(r[b+'AutoAdminLogon'])==='1'||r[b+'DefaultPassword'])?'vuln':'good';}",
            'why': '자동 로그온이 켜져 있고 비밀번호가 레지스트리에 그대로 남아 있습니다. '
                   '레지스트리를 읽을 수 있는 계정이면 관리자 비밀번호를 그대로 가져갑니다. '
                   '설정을 끄는 것만으로는 부족하고 <b>저장된 값도 지워야</b> 합니다.',
            'fix': "function(fs){var b='HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\Winlogon\\\\',r=fs.host.reg;"
                   "r[b+'AutoAdminLogon']='0'; delete r[b+'DefaultPassword'];}",
            'fixNote': '자동 로그온을 끄고 저장돼 있던 평문 비밀번호 값을 삭제했습니다.',
        },
        {
            'id': 'SRV-089', 'risk': 4, 'title': '화면 잠금 정책 적용',
            'brief': '자리를 비운 서버 콘솔이 <b>잠기지 않고 그대로 열려</b> 있으면, '
                     '물리적으로 접근한 사람이 인증 없이 로그온된 세션을 그대로 씁니다.',
            'where': 'HKLM\\SOFTWARE\\Policies\\...\\Control Panel\\Desktop',
            'hint': '켜져 있는지, 대기 시간이 적절한지, 복귀할 때 암호를 묻는지 세 가지를 모두 보세요.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Control Panel\\Desktop"'],
            'options': ['화면 보호기가 꺼져 있고 복귀 시 암호도 묻지 않음', '대기 10분·암호 확인이 설정됨',
                        '대기 시간이 3600초로 설정됨', 'DontDisplayLastUserName 이 0'],
            'evidence': ['화면 보호기가 꺼져 있고 복귀 시 암호도 묻지 않음'],
            'verdict': "function(fs){var b='HKLM\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Windows\\\\Control Panel\\\\Desktop\\\\',r=fs.host.reg;"
                       "return (r[b+'ScreenSaveActive']==='1'&&r[b+'ScreenSaverIsSecure']==='1'"
                       "&&Number(r[b+'ScreenSaveTimeOut'])<=600)?'good':'vuln';}",
            'why': '화면 보호기가 꺼져 있고, 대기 시간은 3600초에 복귀 시 암호도 묻지 않습니다. '
                   '세 가지가 모두 맞아야 잠금이 실제로 동작합니다. 하나만 보고 판정할 수 없습니다.',
            'fix': "function(fs){var b='HKLM\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Windows\\\\Control Panel\\\\Desktop\\\\',r=fs.host.reg;"
                   "r[b+'ScreenSaveActive']='1'; r[b+'ScreenSaverIsSecure']='1'; r[b+'ScreenSaveTimeOut']='600';}",
            'fixNote': '화면 보호기를 켜고 대기 10분·복귀 시 암호 확인으로 설정했습니다.',
        },
        {
            'id': 'SRV-090', 'risk': 5, 'title': '로그온 화면의 시스템 종료 기능 제거',
            'brief': '로그온하지 않고도 종료할 수 있으면 <b>인증 없이 서비스를 멈출 수</b> 있습니다. '
                     '금융 서버에서는 곧바로 가용성 사고가 됩니다.',
            'where': 'HKLM\\...\\Winlogon\\ShutdownWithoutLogon',
            'hint': '0 이어야 로그온 없이는 종료할 수 없습니다.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" /v ShutdownWithoutLogon'],
            'options': ['ShutdownWithoutLogon 이 1 (로그온 없이 종료 가능)', '값이 0',
                        'AutoAdminLogon 이 1', 'CrashOnAuditFail 이 1'],
            'evidence': ['ShutdownWithoutLogon 이 1 (로그온 없이 종료 가능)'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\Winlogon\\\\ShutdownWithoutLogon']===0?'good':'vuln';}",
            'why': '로그온 화면에 종료 버튼이 노출됩니다. 콘솔이나 원격 콘솔 화면에 닿을 수 있는 사람이면 '
                   '계정 없이도 정산 서버를 내릴 수 있습니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows NT\\\\CurrentVersion\\\\Winlogon\\\\ShutdownWithoutLogon']=0;}",
            'fixNote': 'ShutdownWithoutLogon 을 0 으로 설정했습니다.',
        },
        {
            'id': 'SRV-091', 'risk': 5, 'title': '감사 실패 시 시스템 정지 옵션 해제',
            'brief': '감사 실패 시 정지 옵션이 켜져 있으면 <b>감사 로그를 못 쓰는 순간 서버가 멈춥니다</b>. '
                     '로그 볼륨이 가득 차기만 해도 서비스가 중단됩니다.',
            'where': 'HKLM\\...\\Lsa\\CrashOnAuditFail',
            'hint': '0 이어야 로그 기록 실패로 시스템이 멈추지 않습니다.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa" /v CrashOnAuditFail'],
            'options': ['CrashOnAuditFail 이 1 (감사 실패 시 시스템 정지)', '값이 0',
                        'RestrictAnonymous 가 0', 'EveryoneIncludesAnonymous 가 1'],
            'evidence': ['CrashOnAuditFail 이 1 (감사 실패 시 시스템 정지)'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\CrashOnAuditFail']===0?'good':'vuln';}",
            'why': '이 항목은 방향이 거꾸로라 헷갈리기 쉽습니다. 로그를 남기는 것은 중요하지만, '
                   '금융 서비스가 <b>로그 저장 실패 때문에 멈추면 그 자체가 더 큰 사고</b>입니다. '
                   '옵션은 끄고, 대신 로그 볼륨 사용률과 원격 전송 실패를 감시해 미리 대응합니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Control\\\\Lsa\\\\CrashOnAuditFail']=0;}",
            'fixNote': 'CrashOnAuditFail 을 0 으로 바꿨습니다(로그 용량 감시로 대체).',
        },
        {
            'id': 'SRV-092', 'risk': 3, 'title': '네트워크 접근 권한 정책 적정성',
            'brief': '네트워크에서 이 컴퓨터에 접근할 권한이 <b>Everyone</b> 에 부여돼 있습니다. '
                     '거부 목록도 비어 있어 손님 계정조차 막히지 않습니다.',
            'where': '로컬 보안 정책 SeNetworkLogonRight / SeDenyNetworkLogonRight',
            'hint': '허용 목록만 보지 말고 거부 목록도 함께 보세요.',
            'cmds': ['secedit /export /cfg secpol.txt'],
            'options': ['SeNetworkLogonRight 에 Everyone 이 있고 거부 목록은 비어 있음',
                        '업무 그룹만 허용되고 Guest 는 거부됨',
                        'SeInteractiveLogonRight 에 Guest 포함', 'SeBackupPrivilege 에 Users 포함'],
            'evidence': ['SeNetworkLogonRight 에 Everyone 이 있고 거부 목록은 비어 있음'],
            'verdict': "function(fs){var p=fs.host.policy;"
                       "return (!/Everyone/.test(p.SeNetworkLogonRight||'')&&/Guest/.test(p.SeDenyNetworkLogonRight||''))?'good':'vuln';}",
            'why': '허용은 Everyone, 거부는 비어 있습니다. 허용 목록을 업무 그룹으로 좁히고, '
                   '익명·손님 계정은 <b>거부 목록에 명시</b>해야 합니다. 허용에서 빼는 것과 '
                   '거부에 넣는 것은 다릅니다. 다른 그룹 소속으로 권한이 흘러들어오면 '
                   '허용에서 빠진 것만으로는 막히지 않습니다.',
            'fix': "function(fs){var p=fs.host.policy;"
                   "p.SeNetworkLogonRight='Administrators,FIN-Ops';"
                   "p.SeDenyNetworkLogonRight='Guest,ANONYMOUS LOGON';}",
            'fixNote': '네트워크 접근 허용을 업무 그룹으로 좁히고 Guest·익명을 거부 목록에 넣었습니다.',
        },
        {
            'id': 'SRV-093', 'risk': 2, 'title': '백업·복원 권한 부여 범위 제한',
            'brief': '백업·복원 권한은 <b>파일 접근 권한을 우회</b>합니다. 이 권한이 있으면 '
                     '읽을 수 없게 막아 둔 파일도 백업이라는 이름으로 꺼내 갈 수 있습니다.',
            'where': '로컬 보안 정책 SeBackupPrivilege',
            'hint': '권한 목록에 Users 같은 넓은 그룹이 있는지 보세요.',
            'cmds': ['secedit /export /cfg secpol.txt'],
            'options': ['SeBackupPrivilege 에 Users 가 포함됨', 'Administrators 만 있음',
                        'SeTakeOwnershipPrivilege 에 Everyone 포함', 'SeLoadDriverPrivilege 에 Users 포함'],
            'evidence': ['SeBackupPrivilege 에 Users 가 포함됨'],
            'verdict': "function(fs){return /Users|Everyone|Guests/.test(fs.host.policy.SeBackupPrivilege||'')?'vuln':'good';}",
            'why': '백업 권한이 일반 사용자 그룹까지 열려 있습니다. 이 권한은 접근 권한 검사를 건너뛰므로, '
                   '아무리 폴더 권한을 촘촘히 걸어도 소용이 없습니다. 백업 담당 계정에만 남깁니다.',
            'fix': "function(fs){fs.host.policy.SeBackupPrivilege='Administrators,FIN-Backup';}",
            'fixNote': '백업·복원 권한을 관리자와 백업 담당 그룹으로 좁혔습니다.',
        },
        {
            'id': 'SRV-094', 'risk': 3, 'title': '소유권 변경 권한 부여 범위 제한',
            'brief': '소유권을 가져올 수 있으면 <b>권한 설정 자체를 다시 쓸 수</b> 있습니다. '
                     'Everyone 에게 열려 있으면 접근 통제가 사실상 없는 것과 같습니다.',
            'where': '로컬 보안 정책 SeTakeOwnershipPrivilege',
            'hint': 'Everyone 이 들어 있는지 보세요.',
            'cmds': ['secedit /export /cfg secpol.txt'],
            'options': ['SeTakeOwnershipPrivilege 에 Everyone 이 포함됨', 'Administrators 만 있음',
                        'SeBackupPrivilege 에 Users 포함', 'LSAAnonymousNameLookup 이 1'],
            'evidence': ['SeTakeOwnershipPrivilege 에 Everyone 이 포함됨'],
            'verdict': "function(fs){return /Everyone|Users|Guests/.test(fs.host.policy.SeTakeOwnershipPrivilege||'')?'vuln':'good';}",
            'why': '소유권 변경 권한에 Everyone 이 있습니다. 소유자가 되면 권한을 마음대로 바꿀 수 있어 '
                   '접근 거부 설정이 의미를 잃습니다. 관리자에게만 남겨야 합니다.',
            'fix': "function(fs){fs.host.policy.SeTakeOwnershipPrivilege='Administrators';}",
            'fixNote': '소유권 변경 권한을 Administrators 로 좁혔습니다.',
        },
        {
            'id': 'SRV-095', 'risk': 4, 'title': '이동식 매체 사용 통제',
            'brief': '이동식 저장 매체가 <b>아무 통제 없이 연결·사용</b>될 수 있습니다. '
                     '정산 자료가 통제 구간 밖으로 나가는 가장 흔한 경로입니다.',
            'where': 'HKLM\\SOFTWARE\\Policies\\...\\RemovableStorageDevices\\Deny_All',
            'hint': '1 이어야 이동식 매체 접근이 기본 차단됩니다.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\RemovableStorageDevices" /v Deny_All'],
            'options': ['Deny_All 이 0 (이동식 매체 사용 제한 없음)', '값이 1',
                        'ScreenSaveActive 가 0', 'DontDisplayLastUserName 이 0'],
            'evidence': ['Deny_All 이 0 (이동식 매체 사용 제한 없음)'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Windows\\\\RemovableStorageDevices\\\\Deny_All']===1?'good':'vuln';}",
            'why': '이동식 매체 사용이 기본 허용입니다. 서버에서는 기본 차단으로 두고, '
                   '반출이 필요한 작업만 승인 절차를 거쳐 한시적으로 예외를 주는 방식이 맞습니다. '
                   '설정만 걸고 승인·기록 절차가 없으면 결국 예외가 상시화됩니다.',
            'fix': "function(fs){fs.host.reg['HKLM\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Windows\\\\RemovableStorageDevices\\\\Deny_All']=1;}",
            'fixNote': '이동식 매체 접근을 기본 차단으로 설정했습니다.',
        },
        {
            'id': 'SRV-096', 'risk': 3, 'title': '일반 사용자의 드라이버 설치 제한',
            'brief': '드라이버는 <b>운영체제 핵심 권한으로 동작</b>합니다. 일반 사용자가 설치할 수 있으면 '
                     '서명되지 않은 드라이버 한 개로 시스템 전체가 넘어갑니다.',
            'where': '로컬 보안 정책 SeLoadDriverPrivilege',
            'hint': '권한 목록에 Users 가 있는지 보세요.',
            'cmds': ['secedit /export /cfg secpol.txt'],
            'options': ['SeLoadDriverPrivilege 에 Users 가 포함됨', 'Administrators 만 있음',
                        'SeBackupPrivilege 에 Users 포함', 'SeNetworkLogonRight 에 Everyone 포함'],
            'evidence': ['SeLoadDriverPrivilege 에 Users 가 포함됨'],
            'verdict': "function(fs){return /Users|Everyone|Guests/.test(fs.host.policy.SeLoadDriverPrivilege||'')?'vuln':'good';}",
            'why': '드라이버 로드 권한이 일반 사용자에게까지 열려 있습니다. 응용 프로그램 권한 상승과 '
                   '달리 이건 곧바로 운영체제 핵심 영역의 코드 실행이라 영향 범위가 다릅니다. '
                   '관리자에게만 남깁니다.',
            'fix': "function(fs){fs.host.policy.SeLoadDriverPrivilege='Administrators';}",
            'fixNote': '드라이버 로드 권한을 Administrators 로 좁혔습니다.',
        },
    ],
}

# ── 랩 B: 공유·서비스·자산 ──────────────────────────────────────────────
HOST_B = {
    'name': 'FIN-WIN-02', 'os': 'Windows Server 2016 Standard', 'platform': 'windows',
    'today': '2026-09-15',
    'procs': [
        {'pid': 612, 'cmd': 'lsass.exe'},
        {'pid': 1904, 'cmd': 'spoolsv.exe'},
        {'pid': 2130, 'cmd': 'FinFileSvc.exe'},
        {'pid': 3388, 'cmd': 'wupd.exe'},
    ],
    'ports': [], 'pkgs': {}, 'hidden': [], 'acl': {}, 'users': {}, 'groups': {}, 'policy': {},
    'dep': 0,
    'reg': {
        r'HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters\AutoShareServer': 1,
        r'HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters\AutoDisconnect': -1,
        r'HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters\EnableForcedLogOff': 0,
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\FinFileAgent': 'C:\\Program Files\\FinFile\\agent.exe',
        r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\wupdmgrsvc': 'C:\\Users\\Public\\wupd.exe',
        r'HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\SynAttackProtect': 0,
        r'HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\TcpMaxDataRetransmissions': 10,
        r'HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\EnableICMPRedirect': 1,
        r'HKLM\SOFTWARE\FinGuard\Engine\PatternDate': '2026-05-02',
        r'HKLM\SOFTWARE\FinGuard\Engine\PatternVersion': '20260502.01',
        r'HKLM\SOFTWARE\FinGuard\Engine\AutoUpdate': 0,
    },
    'services': {
        'Spooler': 'running',
        'RemoteRegistry': 'running',
        'LanmanServer': 'running',
        'W32Time': 'running',
        'FinGuardSvc': 'stopped',
    },
    'shares': {
        'C$': {'path': 'C:\\', 'note': '기본 공유', 'perm': 'Administrators, 모든 권한'},
        'ADMIN$': {'path': 'C:\\Windows', 'note': '원격 관리', 'perm': 'Administrators, 모든 권한'},
        'SETTLE': {'path': 'D:\\settle', 'note': '일일 정산 자료', 'perm': 'Everyone, 모든 권한'},
        'TEMP_MIG': {'path': 'D:\\temp_mig', 'note': '2025 이관 임시', 'perm': 'Everyone, 모든 권한'},
    },
    'tasks': [
        {'name': 'FIN\\SettleDaily', 'next': '2026-09-16 02:00',
         'cmd': 'D:\\fin\\bin\\settle.bat', 'user': 'svc_settle'},
        {'name': 'FIN\\UpdateCheck', 'next': '2026-09-15 23:30',
         'cmd': 'C:\\Users\\Public\\wupd.exe -q', 'user': 'SYSTEM'},
    ],
    'disks': [
        {'id': 'C:', 'fs': 'NTFS', 'size': '214748364800', 'enc': True, 'keyProt': '보안 칩 + PIN'},
        {'id': 'D:', 'fs': 'NTFS', 'size': '1099511627776', 'enc': False},
        {'id': 'E:', 'fs': 'FAT32', 'size': '107374182400', 'enc': False},
    ],
}

LAB_B = {
    'key': 'winsvc', 'file': '07_srv-winsvc.html', 'code': 'SRV-WINSVC',
    'title': 'Windows 공유·서비스·자산',
    'desc': 'Windows 파일 서버의 공유 권한, 기동 서비스, 자동 실행·예약 작업, 볼륨 암호화와 '
            '악성코드 대응 상태를 net share · sc query · schtasks · manage-bde 로 점검합니다.',
    'host': HOST_B, 'fs': {},
    'missions': [
        {
            'id': 'SRV-023', 'risk': 4, 'title': '관리 목적 기본 공유 해제',
            'brief': 'Windows 는 <code>C$</code>·<code>ADMIN$</code> 같은 <b>관리 공유</b>를 '
                     '설치할 때 자동으로 만들고, 지워도 재부팅하면 다시 만듭니다.',
            'where': '공유 목록과 AutoShareServer',
            'hint': '공유를 지우는 것만으로는 부족합니다. 재부팅 후에도 유지되는 설정을 보세요.',
            'cmds': ['net share',
                     'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters" /v AutoShareServer'],
            'options': ['C$·ADMIN$ 가 있고 AutoShareServer 가 1', '기본 공유가 없고 AutoShareServer 가 0',
                        'SETTLE 공유가 Everyone 권한', 'TEMP_MIG 공유가 남아 있음'],
            'evidence': ['C$·ADMIN$ 가 있고 AutoShareServer 가 1'],
            'verdict': "function(fs){return fs.host.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\LanmanServer\\\\Parameters\\\\AutoShareServer']===0?'good':'vuln';}",
            'why': '드라이브 단위 관리 공유가 살아 있고 자동 생성 설정도 켜져 있습니다. '
                   '관리자 자격 증명이 한 번 새면 이 경로로 디스크 전체가 열립니다. '
                   '<b>공유를 지우기만 하면 재부팅 때 되살아나므로</b> 자동 생성 설정을 함께 꺼야 합니다. '
                   '원격 관리 도구가 이 공유를 쓰고 있지 않은지 먼저 확인하세요.',
            'fix': "function(fs){var h=fs.host;"
                   "h.reg['HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\LanmanServer\\\\Parameters\\\\AutoShareServer']=0;"
                   "delete h.shares['C$']; delete h.shares['ADMIN$'];}",
            'fixNote': '기본 공유를 해제하고 AutoShareServer 를 0 으로 설정했습니다.',
        },
        {
            'id': 'SRV-024', 'risk': 5, 'title': '공유 폴더의 접근 권한 최소화',
            'brief': '정산 자료 공유에 <b>Everyone 모든 권한</b>이 걸려 있습니다. '
                     '접근할 수 있는 누구나 읽고 바꾸고 지울 수 있습니다.',
            'where': 'SETTLE 공유의 사용 권한',
            'hint': 'net share <공유이름> 으로 개별 공유의 사용 권한을 보세요.',
            'cmds': ['net share', 'net share SETTLE'],
            'options': ['SETTLE 공유에 Everyone 모든 권한이 부여됨', '업무 그룹에만 읽기 권한',
                        'SETTLE 경로가 D:\\settle', 'C$ 가 존재함'],
            'evidence': ['SETTLE 공유에 Everyone 모든 권한이 부여됨'],
            'verdict': "function(fs){var s=(fs.host.shares||{})['SETTLE'];"
                       "return (s&&/Everyone/.test(s.perm||''))?'vuln':'good';}",
            'why': '정산 자료에 전체 사용자 모든 권한이 걸려 있습니다. 업무 그룹에 필요한 만큼만 주고 '
                   'Everyone 은 제거해야 합니다. 공유 권한과 파일 권한은 <b>둘 중 더 좁은 쪽</b>이 '
                   '적용되므로, 공유만 좁히고 끝내지 말고 폴더 권한도 같이 확인하세요.',
            'fix': "function(fs){fs.host.shares['SETTLE'].perm='FIN-Settle 그룹, 변경; FIN-Audit 그룹, 읽기';}",
            'fixNote': 'SETTLE 공유 권한을 업무 그룹 기준으로 좁혔습니다.',
        },
        {
            'id': 'SRV-025', 'risk': 3, 'title': '업무와 무관한 공유 자원 제거',
            'brief': '목적이 끝난 공유가 남아 있으면 <b>아무도 보지 않는 경로</b>가 하나 더 생깁니다. '
                     '이관 작업 때 만든 임시 공유가 가장 흔한 사례입니다.',
            'where': '공유 목록',
            'hint': '공유 이름과 설명을 보고 지금 업무에 쓰이는 것인지 판단하세요.',
            'cmds': ['net share', 'net share TEMP_MIG'],
            'options': ['2025년 이관용 임시 공유 TEMP_MIG 가 남아 있음', '업무 공유만 남아 있음',
                        'SETTLE 이 Everyone 권한', 'ADMIN$ 가 존재함'],
            'evidence': ['2025년 이관용 임시 공유 TEMP_MIG 가 남아 있음'],
            'verdict': "function(fs){return (fs.host.shares||{})['TEMP_MIG']?'vuln':'good';}",
            'why': '이관이 끝난 지 한참 지난 임시 공유가 그대로입니다. 목적이 끝난 공유는 관리 대상 목록에서도 '
                   '빠져서 권한 점검이나 백업 대상에서 조용히 제외됩니다. '
                   '자료를 옮겼는지 확인한 뒤 공유와 폴더를 함께 정리하세요.',
            'fix': "function(fs){delete fs.host.shares['TEMP_MIG'];}",
            'fixNote': 'TEMP_MIG 임시 공유를 제거했습니다.',
        },
        {
            'id': 'SRV-026', 'risk': 3, 'title': '유휴 공유 세션 자동 종료',
            'brief': '유휴 세션이 <b>끊기지 않고 계속 유지</b>되면, 자리를 뜬 단말의 열린 연결을 '
                     '그대로 이어받아 쓸 수 있습니다.',
            'where': 'LanmanServer\\Parameters 의 AutoDisconnect',
            'hint': 'AutoDisconnect 는 분 단위입니다. -1 은 끊지 않는다는 뜻입니다.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters"'],
            'options': ['AutoDisconnect 가 -1 (유휴 세션을 끊지 않음)', 'AutoDisconnect 가 15분',
                        'AutoShareServer 가 1', 'EnableForcedLogOff 가 1'],
            'evidence': ['AutoDisconnect 가 -1 (유휴 세션을 끊지 않음)'],
            'verdict': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\LanmanServer\\\\Parameters\\\\',r=fs.host.reg;"
                       "var v=r[b+'AutoDisconnect'];"
                       "return (typeof v==='number'&&v>0&&v<=30&&r[b+'EnableForcedLogOff']===1)?'good':'vuln';}",
            'why': '유휴 세션이 무기한 유지되고, 로그온 허용 시간이 끝나도 강제 종료하지 않습니다. '
                   '두 설정은 짝입니다. 자동 해제 시간만 정하고 강제 로그오프를 켜지 않으면 '
                   '허용 시간 밖에서도 이미 열린 세션이 살아 있습니다.',
            'fix': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\LanmanServer\\\\Parameters\\\\',r=fs.host.reg;"
                   "r[b+'AutoDisconnect']=15; r[b+'EnableForcedLogOff']=1;}",
            'fixNote': '유휴 세션 자동 해제를 15분으로 두고 강제 로그오프를 켰습니다.',
        },
        {
            'id': 'SRV-056', 'risk': 3, 'title': '업무에 쓰이지 않는 서비스 중지',
            'brief': '파일 서버에 <b>인쇄 대기열 서비스</b>가 떠 있습니다. 쓰지 않는 서비스는 '
                     '공격 표면만 늘립니다.',
            'where': '기동 중인 서비스 목록',
            'hint': '서비스 상태와 실행 중인 프로세스를 함께 보고, 업무에 필요한지 판단하세요.',
            'cmds': ['sc query Spooler', 'tasklist'],
            'options': ['파일 서버에 Spooler(인쇄 대기열)가 RUNNING', 'Spooler 가 STOPPED',
                        'FinFileSvc 가 실행 중', 'W32Time 이 RUNNING'],
            'evidence': ['파일 서버에 Spooler(인쇄 대기열)가 RUNNING'],
            'verdict': "function(fs){return (fs.host.services||{})['Spooler']==='running'?'vuln':'good';}",
            'why': '이 서버는 파일 공유가 업무인데 인쇄 대기열이 떠 있습니다. 인쇄 서비스는 과거에 '
                   '원격 코드 실행 취약점이 반복해서 나온 구성 요소라 특히 눈여겨봅니다. '
                   'FinFileSvc 와 W32Time 은 각각 업무와 시각 동기화에 필요하므로 판정 근거가 아닙니다.',
            'fix': "function(fs){fs.host.services['Spooler']='stopped';"
                   "fs.host.procs=fs.host.procs.filter(function(p){return !/spoolsv/i.test(p.cmd);});}",
            'fixNote': 'Spooler 서비스를 중지하고 시작 유형을 사용 안 함으로 바꿨습니다.',
        },
        {
            'id': 'SRV-058', 'risk': 5, 'title': '원격 레지스트리 접근 서비스 중지',
            'brief': '원격 레지스트리 서비스가 떠 있으면 <b>원격에서 레지스트리를 읽고 쓸 수</b> 있습니다. '
                     '자동 로그온 비밀번호 같은 값이 그대로 나갑니다.',
            'where': 'RemoteRegistry 서비스 상태',
            'hint': 'sc query 로 서비스 상태를 보세요.',
            'cmds': ['sc query RemoteRegistry', 'sc query LanmanServer'],
            'options': ['RemoteRegistry 가 RUNNING', 'RemoteRegistry 가 STOPPED',
                        'LanmanServer 가 RUNNING', 'FinGuardSvc 가 STOPPED'],
            'evidence': ['RemoteRegistry 가 RUNNING'],
            'verdict': "function(fs){return (fs.host.services||{})['RemoteRegistry']==='running'?'vuln':'good';}",
            'why': '원격 레지스트리가 실행 중입니다. 원격 점검 도구가 이 서비스를 쓰는 경우가 있으므로 '
                   '무조건 내리기 전에 확인하되, 상시 기동이 필요한 경우는 드뭅니다. '
                   '점검할 때만 켜고 끝나면 내리는 운용이 안전합니다.',
            'fix': "function(fs){fs.host.services['RemoteRegistry']='stopped';}",
            'fixNote': 'RemoteRegistry 서비스를 중지했습니다.',
        },
        {
            'id': 'SRV-059', 'risk': 3, 'title': '부팅 시 자동 실행 항목 정리',
            'brief': '부팅할 때 자동 실행되는 항목 중에 <b>사용자 공용 폴더에서 실행되는 것</b>이 있습니다. '
                     '정상 프로그램은 보통 그런 경로에 설치되지 않습니다.',
            'where': 'HKLM\\...\\CurrentVersion\\Run',
            'hint': '실행 파일 경로를 보세요. 어디에 설치돼 있는지가 이름보다 중요합니다.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"', 'tasklist'],
            'options': ['wupdmgrsvc 가 C:\\Users\\Public 경로의 실행 파일을 자동 실행함',
                        '업무 에이전트만 등록되어 있음',
                        'FinFileAgent 가 Program Files 에 설치됨', 'Spooler 가 RUNNING'],
            'evidence': ['wupdmgrsvc 가 C:\\Users\\Public 경로의 실행 파일을 자동 실행함'],
            'verdict': "function(fs){var r=fs.host.reg,b='HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\';"
                       "for(var k in r){ if(k.indexOf(b)!==0) continue;"
                       "if(/\\\\Users\\\\Public\\\\|\\\\Temp\\\\|\\\\AppData\\\\/i.test(String(r[k]))) return 'vuln'; }"
                       "return 'good';}",
            'why': '이름은 업데이트 관리자처럼 보이지만 실행 파일이 공용 사용자 폴더에 있습니다. '
                   '이 경로는 권한이 느슨해 일반 사용자도 쓸 수 있어 지속성 확보에 자주 쓰입니다. '
                   '<b>이름이 아니라 경로와 서명을 보고 판단</b>하고, 같은 파일이 예약 작업에도 걸려 있는지 확인하세요.',
            'fix': "function(fs){var r=fs.host.reg;"
                   "delete r['HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\\\\wupdmgrsvc'];"
                   "fs.host.procs=fs.host.procs.filter(function(p){return !/wupd/i.test(p.cmd);});}",
            'fixNote': '공용 폴더에서 실행되던 자동 실행 항목을 제거하고 프로세스를 종료했습니다.',
        },
        {
            'id': 'SRV-060', 'risk': 3, 'title': '예약 작업 목록 정리',
            'brief': '예약 작업은 <b>지속성을 확보하는 통로</b>로 자주 쓰입니다. '
                     '실행 명령과 실행 계정을 보면 업무 작업인지 아닌지가 드러납니다.',
            'where': '예약 작업 목록',
            'hint': '작업 이름이 아니라 실행할 명령의 경로와 실행 계정을 보세요.',
            'cmds': ['schtasks', 'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"'],
            'options': ['UpdateCheck 가 공용 폴더의 실행 파일을 SYSTEM 권한으로 실행함',
                        '정산 배치만 등록되어 있음',
                        'SettleDaily 가 svc_settle 로 실행됨', '예약 작업이 없음'],
            'evidence': ['UpdateCheck 가 공용 폴더의 실행 파일을 SYSTEM 권한으로 실행함'],
            'verdict': "function(fs){return (fs.host.tasks||[]).some(function(t){"
                       "return /\\\\Users\\\\Public\\\\|\\\\Temp\\\\/i.test(String(t.cmd||''));})?'vuln':'good';}",
            'why': '자동 실행 항목과 <b>같은 실행 파일</b>이 예약 작업에도 걸려 있고, 실행 계정은 SYSTEM 입니다. '
                   '한쪽만 지우면 다른 쪽이 다시 만들어 놓는 구조가 흔하므로 둘을 함께 봐야 합니다. '
                   '정산 배치는 전용 서비스 계정으로 돌고 경로도 업무 디렉터리라 정상입니다.',
            'fix': "function(fs){fs.host.tasks=fs.host.tasks.filter(function(t){"
                   "return !/\\\\Users\\\\Public\\\\|\\\\Temp\\\\/i.test(String(t.cmd||''));});}",
            'fixNote': '공용 폴더 실행 파일을 돌리던 예약 작업을 제거했습니다(파일은 별도 분석 의뢰).',
        },
        {
            'id': 'SRV-084', 'risk': 3, 'title': '안전한 파일 시스템 포맷 사용',
            'brief': 'FAT 계열 파일 시스템은 <b>접근 권한을 지원하지 않습니다</b>. '
                     '그 볼륨에 올린 파일은 권한으로 보호할 방법이 없습니다.',
            'where': '볼륨별 파일 시스템',
            'hint': 'wmic logicaldisk 로 각 드라이브의 파일 시스템 종류를 보세요.',
            'cmds': ['wmic logicaldisk get DeviceID,FileSystem,Size'],
            'options': ['E: 드라이브가 FAT32 로 포맷되어 있음', '모든 볼륨이 NTFS',
                        'D: 가 NTFS', 'C: 가 암호화되어 있음'],
            'evidence': ['E: 드라이브가 FAT32 로 포맷되어 있음'],
            'verdict': "function(fs){return (fs.host.disks||[]).some(function(d){return /FAT/i.test(d.fs);})?'vuln':'good';}",
            'why': 'E: 가 FAT32 입니다. 이 볼륨에서는 파일 권한도 감사 설정도 걸 수 없어서, '
                   '다른 볼륨을 아무리 촘촘히 통제해도 여기로 복사하면 그만입니다. '
                   'NTFS 로 변환한 뒤 권한을 다시 설계해야 합니다(변환 전 백업은 필수입니다).',
            'fix': "function(fs){fs.host.disks=fs.host.disks.map(function(d){"
                   "return /FAT/i.test(d.fs)?{id:d.id,fs:'NTFS',size:d.size,enc:d.enc}:d;});}",
            'fixNote': 'FAT32 볼륨을 NTFS 로 변환했습니다.',
        },
        {
            'id': 'SRV-085', 'risk': 4, 'title': '저장 볼륨 암호화 적용',
            'brief': '정산 자료가 있는 볼륨이 <b>암호화되어 있지 않습니다</b>. '
                     '디스크를 떼어 다른 장비에 붙이면 운영체제 권한과 무관하게 내용을 읽을 수 있습니다.',
            'where': '볼륨 암호화 상태',
            'hint': 'manage-bde 로 볼륨별 변환 상태와 키 보호기를 보세요.',
            'cmds': ['manage-bde -status', 'net share'],
            'options': ['정산 자료 볼륨 D: 가 암호화되지 않음', '모든 볼륨이 암호화됨',
                        'C: 가 보안 칩 + PIN 으로 보호됨', 'E: 가 FAT32'],
            'evidence': ['정산 자료 볼륨 D: 가 암호화되지 않음'],
            'verdict': "function(fs){return (fs.host.disks||[]).some(function(d){return !d.enc;})?'vuln':'good';}",
            'why': '시스템 볼륨만 암호화돼 있고 데이터 볼륨은 평문입니다. 암호화는 <b>중요 자료가 실제로 '
                   '있는 볼륨</b>에 걸어야 의미가 있습니다. 함께 확인할 것은 키 보관 방식입니다. '
                   '키를 같은 장비에 평문으로 두면 디스크만 떼어 가는 시나리오를 막지 못합니다.',
            'fix': "function(fs){fs.host.disks=fs.host.disks.map(function(d){"
                   "return d.enc?d:{id:d.id,fs:d.fs,size:d.size,enc:true,keyProt:'보안 칩 + 복구 키(금고 보관)'};});}",
            'fixNote': '데이터 볼륨을 암호화하고 복구 키를 별도 보관하도록 설정했습니다.',
        },
        {
            'id': 'SRV-097', 'risk': 2, 'title': '메모리 실행 방지 기능 활성화',
            'brief': '메모리 실행 방지가 <b>꺼져 있습니다</b>. 데이터 영역에 올라간 코드가 '
                     '그대로 실행될 수 있어, 메모리 손상 취약점의 성공률이 크게 올라갑니다.',
            'where': '시스템 정보의 실행 방지 정책',
            'hint': 'wmic os get 출력의 실행 방지 지원 정책 값을 보세요. 0 은 전부 제외입니다.',
            'cmds': ['wmic os get DataExecutionPrevention_SupportPolicy', 'systeminfo'],
            'options': ['실행 방지 정책이 0 (모든 프로그램 제외)', '정책이 3 (모든 프로그램 적용)',
                        'OS 가 Windows Server 2016', '현재 시스템 날짜가 2026-09-15'],
            'evidence': ['실행 방지 정책이 0 (모든 프로그램 제외)'],
            'verdict': "function(fs){var d=fs.host.dep; return (typeof d==='number'&&d>=2)?'good':'vuln';}",
            'why': '실행 방지가 전면 해제돼 있습니다. 예전 업무 프로그램이 오동작해서 꺼 둔 뒤 '
                   '그대로 남아 있는 경우가 많습니다. 전체를 끄는 대신 해당 프로그램만 예외로 등록하고, '
                   '예외 목록은 근거와 함께 관리해야 합니다.',
            'fix': "function(fs){fs.host.dep=3;}",
            'fixNote': '실행 방지를 모든 프로그램에 적용하도록 되돌렸습니다.',
        },
        {
            'id': 'SRV-098', 'risk': 2, 'title': '네트워크 스택 보호 설정',
            'brief': '연결 대기열 보호가 꺼져 있고 재전송 횟수가 큽니다. <b>연결 요청만으로 '
                     '대기열을 채우는 공격</b>에 오래 버티지 못합니다.',
            'where': 'Tcpip\\Parameters',
            'hint': 'SynAttackProtect 와 TcpMaxDataRetransmissions 를 함께 보세요.',
            'cmds': ['reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters"'],
            'options': ['SynAttackProtect 가 0 이고 재전송 횟수가 10회', '보호가 켜져 있고 재전송 3회',
                        'EnableICMPRedirect 가 1', 'AutoShareServer 가 1'],
            'evidence': ['SynAttackProtect 가 0 이고 재전송 횟수가 10회'],
            'verdict': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\Tcpip\\\\Parameters\\\\',r=fs.host.reg;"
                       "return (r[b+'SynAttackProtect']===1&&r[b+'TcpMaxDataRetransmissions']<=3"
                       "&&r[b+'EnableICMPRedirect']===0)?'good':'vuln';}",
            'why': '미완성 연결이 쌓여도 서버가 대기열을 오래 붙들고 있습니다. 재전송 횟수를 줄이면 '
                   '점유 시간이 짧아집니다. 함께 볼 것은 경로 변경 요청 수용 설정입니다. '
                   '켜져 있으면 외부에서 보낸 요청으로 통신 경로가 바뀔 수 있습니다. '
                   '다만 이 설정들은 앞단 장비의 방어를 대체하지 못합니다.',
            'fix': "function(fs){var b='HKLM\\\\SYSTEM\\\\CurrentControlSet\\\\Services\\\\Tcpip\\\\Parameters\\\\',r=fs.host.reg;"
                   "r[b+'SynAttackProtect']=1; r[b+'TcpMaxDataRetransmissions']=3; r[b+'EnableICMPRedirect']=0;}",
            'fixNote': '연결 대기열 보호를 켜고 재전송 횟수와 경로 변경 수용 설정을 조정했습니다.',
        },
        {
            'id': 'SRV-103', 'risk': 5, 'title': '악성코드 대응 프로그램 설치',
            'brief': '악성코드 대응 프로그램이 설치는 되어 있지만 <b>서비스가 멈춰 있습니다</b>. '
                     '설치 여부만 확인하고 넘어가면 놓치는 부분입니다.',
            'where': 'FinGuardSvc 서비스 상태',
            'hint': '설치되어 있는 것과 감시가 돌고 있는 것은 다릅니다.',
            'cmds': ['sc query FinGuardSvc', 'tasklist'],
            'options': ['백신 서비스가 설치되어 있으나 STOPPED', '백신 서비스가 RUNNING',
                        '백신이 설치되지 않음', 'Spooler 가 RUNNING'],
            'evidence': ['백신 서비스가 설치되어 있으나 STOPPED'],
            'verdict': "function(fs){return (fs.host.services||{})['FinGuardSvc']==='running'?'good':'vuln';}",
            'why': '"백신 설치 완료"로 점검을 끝내면 이 상태를 양호로 적게 됩니다. '
                   '실시간 감시가 실제로 돌고 있는지, 성능 문제로 누가 꺼 놓지 않았는지까지 봐야 합니다. '
                   '재발을 막으려면 서비스 중지 이벤트를 알림으로 받도록 해 두는 것이 좋습니다.',
            'fix': "function(fs){fs.host.services['FinGuardSvc']='running';"
                   "fs.host.procs.push({pid:4120,cmd:'FinGuardSvc.exe'});}",
            'fixNote': '악성코드 대응 서비스를 다시 시작하고 자동 시작으로 설정했습니다.',
        },
        {
            'id': 'SRV-104', 'risk': 5, 'title': '악성코드 탐지 정보 최신화',
            'brief': '탐지 패턴이 <b>넉 달 넘게 갱신되지 않았습니다</b>. 자동 갱신도 꺼져 있어 '
                     '앞으로도 저절로 최신화되지 않습니다.',
            'where': '백신 엔진 패턴 정보',
            'hint': '패턴 날짜를 시스템 현재 날짜와 비교하세요. 자동 갱신 설정도 함께 봅니다.',
            'cmds': ['reg query "HKLM\\SOFTWARE\\FinGuard\\Engine"', 'wmic os get'],
            'options': ['패턴 날짜가 2026-05-02 이고 자동 갱신이 꺼져 있음', '패턴이 최근에 갱신됨',
                        '백신 서비스가 STOPPED', '엔진 버전이 20260502.01'],
            'evidence': ['패턴 날짜가 2026-05-02 이고 자동 갱신이 꺼져 있음'],
            'verdict': "function(fs){var h=fs.host,b='HKLM\\\\SOFTWARE\\\\FinGuard\\\\Engine\\\\';"
                       "var d=Date.parse(h.reg[b+'PatternDate']), t=Date.parse(h.today);"
                       "if(isNaN(d)||isNaN(t)) return 'vuln';"
                       "return (((t-d)/86400000)<=7&&h.reg[b+'AutoUpdate']===1)?'good':'vuln';}",
            'why': '패턴이 넉 달 넘게 멈춰 있습니다. 갱신이 안 된 백신은 <b>있다는 사실 자체가 '
                   '오히려 위험</b>합니다. 대응하고 있다고 착각하게 만들기 때문입니다. '
                   '자동 갱신을 켜는 데서 끝내지 말고 갱신 실패를 알림으로 받는 경로까지 만들어야, '
                   '외부로 나갈 수 없는 망 분리 구간에서 같은 일이 반복되지 않습니다.',
            'fix': "function(fs){var h=fs.host,b='HKLM\\\\SOFTWARE\\\\FinGuard\\\\Engine\\\\';"
                   "h.reg[b+'PatternDate']=h.today; h.reg[b+'PatternVersion']='20260915.01';"
                   "h.reg[b+'AutoUpdate']=1;}",
            'fixNote': '패턴을 최신으로 갱신하고 자동 갱신을 켰습니다(내부 배포 서버 경유).',
        },
    ],
}

LABS = [LAB_A, LAB_B]
