# -*- coding: utf-8 -*-
"""동적·초보친화형 인프라 시뮬 데모 2종 (전체 적용 전 방향 확인용)."""

SPECS = [
{
 'file': '09_net-n06.html',
 'code': 'N-06', 'title': 'SSH 사용 / Telnet 비활성화', 'icon': '🔒',
 'category': '네트워크 장비 · 접근 관리', 'severity': '상',
 'easy': 'Telnet은 비밀번호를 <b>엽서</b>에 적어 보내는 것과 같습니다 — 배달 도중 누구나 읽을 수 있죠. '
         'SSH는 <b>밀봉된 금고</b>에 넣어 보내는 방식입니다. 같은 네트워크의 공격자가 통신을 “엿들을” 때, '
         '엽서(Telnet)는 비밀번호가 그대로 보이지만 금고(SSH)는 열 수 없습니다.',
 'attack_label': '같은 네트워크의 공격자가 관리자 접속을 도청한다',
 'attack_vuln': [
   ['cmt', '# 공격자가 스위치 미러 포트에서 트래픽을 도청'],
   ['prompt', 'attacker$ tcpdump -i eth0 port 23 -A   (Telnet=23)'],
   ['', 'listening on eth0 ... 관리자가 접속을 시작함'],
   ['bad', '>> Username: admin'],
   ['bad', '>> Password: P@ssw0rd!   ← 평문 그대로 노출!'],
   ['prompt', 'attacker$ telnet 10.0.0.1   (탈취한 계정으로 로그인)'],
   ['bad', 'admin@router#  ← 장비 장악 성공'],
 ],
 'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 관리자 계정 탈취',
                  'desc': 'Telnet은 비밀번호를 평문으로 전송하므로, 도청(스니핑)만으로 자격증명이 그대로 유출됩니다.'},
 'attack_secure': [
   ['cmt', '# 동일하게, 이번엔 SSH(22) 트래픽을 도청 시도'],
   ['prompt', 'attacker$ tcpdump -i eth0 port 22 -A   (SSH=22)'],
   ['', 'listening on eth0 ... 관리자가 접속을 시작함'],
   ['good', '>> 8f a1 3e c2 9d 77 b0 ...  (암호문, 해독 불가)'],
   ['prompt', 'attacker$ telnet 10.0.0.1   (Telnet으로 시도)'],
   ['good', 'Connection refused  ← Telnet 비활성화됨'],
   ['warn', '>> 비밀번호를 가로챌 수도, 평문 접속할 수도 없음'],
 ],
 'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 도청 실패',
                    'desc': 'SSH는 통신을 암호화하고 Telnet은 꺼져 있어, 트래픽을 가로채도 비밀번호를 알아낼 수 없습니다.'},
 'vuln_term': [('cmt', '! line vty 설정'), ('bad', 'transport input telnet'), ('warn', '→ 평문 통신, 도청 시 비밀번호 노출')],
 'secure_term': [('cmt', '! line vty 설정'), ('good', 'transport input ssh'), ('good', 'ip ssh version 2'), ('good', '→ 암호화 통신, Telnet 차단')],
 'fix_steps': [
   '<code>transport input ssh</code>로 SSH만 허용하고 Telnet을 차단합니다.',
   '<code>ip ssh version 2</code> 설정 후 2048bit 이상 RSA 키를 생성합니다.',
   '관리 접근은 ACL(<code>access-class</code>)로 관리 대역만 허용합니다.',
 ],
 'checklist': ['Telnet이 비활성화되어 있는가', 'SSHv2만 허용되는가', 'RSA 키 길이가 2048bit 이상인가'],
 'kisa_ref': '네트워크 접근 관리 > SSH 사용 / Telnet 차단',
},
{
 'file': '06_db-d09.html',
 'code': 'D-09', 'title': '로그인 실패 횟수 제한', 'icon': '🔒',
 'category': '데이터베이스 보안', 'severity': '상',
 'easy': '현관 비밀번호를 <b>무한정 눌러볼 수 있다면</b> 도둑은 언젠가 맞힙니다. '
         '“5번 틀리면 잠김”을 걸어두면, 자동으로 수천 번 눌러보는 공격이 5번 만에 멈춥니다. '
         '그것이 바로 <b>계정 잠금 정책(FAILED_LOGIN_ATTEMPTS)</b>입니다.',
 'attack_label': '공격자가 자동화 도구로 DB 비밀번호를 무차별 대입한다',
 'attack_vuln': [
   ['cmt', '# 계정 잠금이 없어 비밀번호를 무한히 시도 가능'],
   ['prompt', 'attacker$ hydra -l SYSTEM -P rockyou.txt oracle://10.0.0.5'],
   ['', '[try] SYSTEM : 123456   ... 실패'],
   ['', '[try] SYSTEM : password ... 실패'],
   ['', '[try] SYSTEM : oracle   ... 실패'],
   ['bad', '[try] SYSTEM : Summer2024 ... 성공!'],
   ['bad', '>> 12,438회 시도 끝에 비밀번호 획득 — 계정 탈취'],
 ],
 'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 비밀번호 크랙',
                  'desc': '잠금 정책이 없어 자동화 도구가 수천 번 시도 끝에 비밀번호를 알아냈습니다.'},
 'attack_secure': [
   ['cmt', '# 동일하게 무차별 대입을 시도'],
   ['prompt', 'attacker$ hydra -l SYSTEM -P rockyou.txt oracle://10.0.0.5'],
   ['', '[try] SYSTEM : 123456   ... 실패 (1/5)'],
   ['', '[try] SYSTEM : password ... 실패 (2/5)'],
   ['', '[try] SYSTEM : ... 실패 (3/5) ... (4/5) ... (5/5)'],
   ['good', '>> ORA-28000: the account is locked'],
   ['warn', '>> 5회 실패로 계정 잠김 — 더 이상 시도 불가'],
 ],
 'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 계정 잠금',
                    'desc': 'FAILED_LOGIN_ATTEMPTS=5 설정으로 5회 실패 시 계정이 잠겨 무차별 대입이 무력화됩니다.'},
 'vuln_term': [('cmt', '-- 실패 임계값 확인'), ('prompt', 'SQL> '), ('', "SELECT limit FROM dba_profiles WHERE resource_name='FAILED_LOGIN_ATTEMPTS';"),
               ('bad', 'UNLIMITED'), ('warn', '→ 무차별 대입 무한 시도 가능')],
 'secure_term': [('cmt', '-- 임계값/잠금 설정'), ('prompt', 'SQL> '), ('', 'ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS 5 PASSWORD_LOCK_TIME 1;'),
                 ('good', 'FAILED_LOGIN_ATTEMPTS = 5'), ('good', '→ 5회 실패 시 자동 잠금')],
 'fix_steps': [
   '<code>ALTER PROFILE DEFAULT LIMIT FAILED_LOGIN_ATTEMPTS 5;</code>로 임계값을 5회 이하로 설정합니다.',
   '<code>PASSWORD_LOCK_TIME</code>으로 잠금 유지 시간을 설정합니다.',
   '모든 사용자 프로파일에 정책이 적용되는지 확인합니다.',
 ],
 'checklist': ['FAILED_LOGIN_ATTEMPTS가 UNLIMITED가 아닌가(5회 이하)', '계정 잠금 시간이 설정되었는가', '전 계정 프로파일에 적용되었는가'],
 'kisa_ref': '데이터베이스 > 로그인 실패 횟수 제한',
},
]
