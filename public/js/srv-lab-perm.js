/* 생성물 — _gen/gen_srv_lab.py 가 만든다. 직접 고치지 말 것. */
window.SRV_LAB_DATA = {
  host: {"name": "fin-file-03", "os": "Red Hat Enterprise Linux 8.8", "procs": [{"pid": 1001, "cmd": "/usr/sbin/sshd -D"}, {"pid": 2210, "cmd": "/usr/sbin/crond -n"}], "ports": [{"port": 22, "svc": "sshd"}], "pkgs": {}},
  fs: {
 "/etc/passwd": {
  "mode": "0644",
  "body": "root:x:0:0:root:/root:/bin/bash\nkim.tx:x:1001:1001::/home/kim.tx:/bin/bash\n"
 },
 "/etc/shadow": {
  "mode": "0644",
  "body": "root:$6$k2Jd$9sLm2...:20180:0:99999:7:::\n"
 },
 "/etc/hosts": {
  "mode": "0644",
  "body": "127.0.0.1 localhost\n10.20.30.11 fin-app-01\n"
 },
 "/etc/services": {
  "mode": "0666",
  "body": "ssh   22/tcp\nsmtp  25/tcp\n"
 },
 "/etc/crontab": {
  "mode": "0666",
  "body": "SHELL=/bin/bash\nPATH=/sbin:/bin:/usr/sbin:/usr/bin\n0 2 * * * root /opt/batch/settle_daily.sh\n"
 },
 "/opt/batch/settle_daily.sh": {
  "mode": "0777",
  "owner": "root",
  "body": "#!/bin/bash\n# 일일 정산 배치\n/usr/bin/psql -f /opt/batch/settle.sql\n"
 },
 "/etc/cron.allow": {
  "mode": "0644",
  "missing": true,
  "body": ""
 },
 "/etc/cron.deny": {
  "mode": "0644",
  "missing": true,
  "body": ""
 },
 "/etc/rc.local": {
  "mode": "0777",
  "body": "#!/bin/sh\n/opt/batch/warmup.sh\n"
 },
 "/usr/bin/dump": {
  "mode": "4755",
  "owner": "root",
  "body": "(바이너리)"
 },
 "/usr/bin/legacytool": {
  "mode": "4777",
  "owner": "root",
  "body": "(사내 제작 바이너리)"
 },
 "/usr/bin/gcc": {
  "mode": "0755",
  "owner": "root",
  "body": "(컴파일러)"
 },
 "/home/kim.tx": {
  "mode": "0777",
  "owner": "kim.tx",
  "group": "kim.tx",
  "dir": true,
  "body": ""
 },
 "/home/kim.tx/.bash_profile": {
  "mode": "0666",
  "owner": "kim.tx",
  "group": "kim.tx",
  "body": "PATH=$PATH:/home/kim.tx/bin\nexport PATH\n"
 },
 "/var/log/messages": {
  "mode": "0666",
  "body": "Sep 14 09:01:22 fin-app-01 sshd[1042]: Server listening on 0.0.0.0 port 22.\n"
 },
 "/var/tmp/stage.dat": {
  "mode": "0666",
  "owner": "1499",
  "group": "1499",
  "body": "(이전 담당자가 남긴 파일)"
 },
 "/root/.bash_profile": {
  "mode": "0644",
  "owner": "root",
  "body": "PATH=.:/usr/local/bin:/usr/bin:/bin\nexport PATH\n"
 },
 "/etc/profile": {
  "mode": "0644",
  "body": "umask 000\nexport PATH\n"
 }
},
  missions: [
    {id:"SRV-072",risk:5,title:"시스템 주요 설정 파일 권한 통제",brief:"shadow 에는 <b>비밀번호 해시</b>가 들어 있습니다. 일반 사용자가 읽을 수 있으면 해시를 복사해 나가서 시간을 들여 원문을 복원할 수 있습니다.",where:"/etc/shadow 의 권한",hint:"shadow 는 소유자만 읽을 수 있어야 합니다.",why:"shadow 가 0644 라 모든 사용자가 해시를 읽을 수 있습니다. passwd 는 0644 가 맞지만 shadow 는 <b>그래서 따로 분리된 파일</b>이므로 0000 또는 0600 이어야 합니다.",cmds:["ls -al /etc/shadow", "ls -al /etc/passwd"],options:["/etc/shadow 가 0644 (누구나 읽기 가능)", "/etc/shadow 가 0000", "/etc/passwd 가 0644", "/etc/hosts 가 0644"],evidence:["/etc/shadow 가 0644 (누구나 읽기 가능)"],verdict:function(fs){var f=fs.files['/etc/shadow']; if(!f) return 'good';var o=parseInt(String(f.mode).slice(-1),10), g=parseInt(String(f.mode).slice(-2,-1),10);return (o>0||g>0)?'vuln':'good';},fix:function(fs){fs.chmod('/etc/shadow','0000');},fixNote:"/etc/shadow 권한을 0000 으로 바꿨습니다(root 는 권한 검사를 우회합니다)."},
    {id:"SRV-071",risk:4,title:"시스템 주요 디렉터리·파일의 전체 쓰기 권한 제거",brief:"<b>누구나 쓸 수 있는 설정 파일</b>은 내용을 바꿔치기할 수 있다는 뜻입니다. services 처럼 평범해 보이는 파일도 예외가 아닙니다.",where:"/etc/services 의 권한",hint:"맨 뒤 자리(others)에 쓰기 권한이 있는지 보세요.",why:"/etc/services 가 0666 이라 일반 사용자가 내용을 바꿀 수 있습니다. 시스템 설정 파일은 root 만 쓰고 나머지는 읽기만 가능해야 합니다.",cmds:["ls -al /etc/services", "find /etc -perm -002"],options:["/etc/services 가 0666 (전체 쓰기 가능)", "/etc/services 가 0644", "/etc/hosts 가 0644", "/etc/passwd 가 0644"],evidence:["/etc/services 가 0666 (전체 쓰기 가능)"],verdict:function(fs){var f=fs.files['/etc/services']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/etc/services','0644');},fixNote:"/etc/services 권한을 0644 로 바꿨습니다."},
    {id:"SRV-067",risk:4,title:"주기 작업 설정 파일의 권한 보호",brief:"crontab 에 쓰기 권한이 있으면 <b>원하는 명령을 root 권한으로 주기 실행</b>시킬 수 있습니다. 권한 상승 경로 중 가장 조용한 편에 속합니다.",where:"/etc/crontab 의 권한",hint:"crontab 은 누가 쓸 수 있어야 할까요?",why:"crontab 이 0666 이라 누구나 편집할 수 있고, 그 안의 작업은 root 로 실행됩니다. 0600 으로 좁혀야 합니다.",cmds:["ls -al /etc/crontab", "cat /etc/crontab"],options:["/etc/crontab 이 0666 (전체 쓰기 가능)", "/etc/crontab 이 0600", "root 로 배치가 실행됨", "PATH 가 지정돼 있음"],evidence:["/etc/crontab 이 0666 (전체 쓰기 가능)"],verdict:function(fs){var f=fs.files['/etc/crontab']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)||(parseInt(String(f.mode).slice(-2,-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/etc/crontab','0600');},fixNote:"/etc/crontab 권한을 0600 으로 바꿨습니다."},
    {id:"SRV-068",risk:4,title:"주기 작업이 참조하는 스크립트의 권한 보호",brief:"crontab 자체를 지켜도 <b>거기서 실행하는 스크립트가 열려 있으면</b> 결과는 같습니다. 공격자는 스크립트 내용만 바꾸면 됩니다.",where:"/opt/batch/settle_daily.sh 의 권한",hint:"crontab 이 무엇을 실행하는지 먼저 보고, 그 파일의 권한을 보세요.",why:"정산 배치 스크립트가 0777 입니다. root 로 매일 실행되는 파일을 누구나 고칠 수 있으면 사실상 root 권한을 넘겨준 것과 같습니다.",cmds:["cat /etc/crontab", "ls -al /opt/batch/settle_daily.sh"],options:["settle_daily.sh 가 0777 (전체 쓰기·실행 가능)", "settle_daily.sh 가 0700", "crontab 이 0666", "소유자가 root"],evidence:["settle_daily.sh 가 0777 (전체 쓰기·실행 가능)"],verdict:function(fs){var f=fs.files['/opt/batch/settle_daily.sh']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/opt/batch/settle_daily.sh','0750');},fixNote:"배치 스크립트 권한을 0750 으로 바꿨습니다."},
    {id:"SRV-069",risk:3,title:"주기 작업 사용 계정 제한",brief:"cron.allow 와 cron.deny 가 모두 없으면 배포판에 따라 <b>모든 사용자가 cron 을 등록</b>할 수 있습니다. 누가 예약 작업을 만들 수 있는지 명시해야 합니다.",where:"/etc/cron.allow, /etc/cron.deny",hint:"두 파일이 존재하는지 확인해 보세요.",why:"두 파일이 모두 없어 cron 사용 주체가 통제되지 않습니다. cron.allow 에 허용 계정을 명시하는 방식(허용 목록)이 더 안전합니다.",cmds:["ls -al /etc/cron.allow", "ls -al /etc/cron.deny"],options:["cron.allow·cron.deny 가 모두 없음", "cron.allow 에 root 만 등록", "crontab 이 0666", "배치가 root 로 실행"],evidence:["cron.allow·cron.deny 가 모두 없음"],verdict:function(fs){return (fs.exists('/etc/cron.allow')||fs.exists('/etc/cron.deny'))?'good':'vuln';},fix:function(fs){fs.write('/etc/cron.allow','root\nbatchsvc\n');fs.chmod('/etc/cron.allow','0640');},fixNote:"cron.allow 를 만들어 허용 계정만 등록했습니다."},
    {id:"SRV-073",risk:3,title:"부팅 스크립트 권한 통제",brief:"부팅 스크립트는 <b>재부팅할 때마다 root 로 실행</b>됩니다. 여기에 한 줄을 넣어 두면 정리해도 다음 부팅에 되살아납니다.",where:"/etc/rc.local 의 권한",hint:"others 에 쓰기 권한이 있는지 보세요.",why:"rc.local 이 0777 이라 누구나 부팅 시 실행될 명령을 추가할 수 있습니다. 지속성(persistence) 확보에 자주 쓰이는 경로입니다.",cmds:["ls -al /etc/rc.local", "cat /etc/rc.local"],options:["/etc/rc.local 이 0777", "/etc/rc.local 이 0700", "warmup.sh 를 실행함", "소유자가 root"],evidence:["/etc/rc.local 이 0777"],verdict:function(fs){var f=fs.files['/etc/rc.local']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/etc/rc.local','0700');},fixNote:"/etc/rc.local 권한을 0700 으로 바꿨습니다."},
    {id:"SRV-074",risk:4,title:"권한 승계 비트가 설정된 파일 정리",brief:"SUID 가 걸린 파일은 <b>실행한 사람이 아니라 소유자(root) 권한으로</b> 돕니다. 거기에 전체 쓰기 권한까지 있으면 내용을 바꿔 root 권한을 그대로 가져갈 수 있습니다.",where:"SUID 비트(4000)가 설정된 파일",hint:"find 로 SUID 파일을 찾고, 그중 others 쓰기 권한이 있는 것을 보세요.",why:"legacytool 이 SUID + 0777 입니다. 누구나 내용을 바꾼 뒤 실행하면 root 권한으로 동작합니다. dump(4755)처럼 쓰기 권한이 없는 SUID 는 별개로 필요성 자체를 검토해야 합니다.",cmds:["find / -perm -4000", "ls -al /usr/bin/legacytool"],options:["legacytool 이 4777 (SUID + 전체 쓰기)", "dump 가 4755", "gcc 가 0755", "SUID 파일이 없음"],evidence:["legacytool 이 4777 (SUID + 전체 쓰기)"],verdict:function(fs){var f=fs.files['/usr/bin/legacytool']; if(!f) return 'good';var m=String(f.mode); var suid=m.length>3&&(parseInt(m[m.length-4],10)&4);return (suid&&(parseInt(m.slice(-1),10)&2))?'vuln':'good';},fix:function(fs){fs.chmod('/usr/bin/legacytool','0755');},fixNote:"legacytool 의 SUID 비트와 전체 쓰기 권한을 제거했습니다."},
    {id:"SRV-075",risk:4,title:"전체 쓰기 가능 파일 정리",brief:"로그 파일이 <b>누구나 쓸 수 있으면</b> 침해 흔적을 지우거나 가짜 기록을 넣을 수 있습니다. 로그는 사고 조사의 출발점이라 특히 문제가 됩니다.",where:"/var/log/messages 의 권한",hint:"로그 파일에 others 쓰기 권한이 있는지 보세요.",why:"로그 파일이 0666 이라 누구나 수정·삭제할 수 있습니다. 최소 0640 으로 좁히고 가능하면 원격 로그 서버로 함께 보내야 합니다.",cmds:["ls -al /var/log/messages", "find /var -perm -002"],options:["/var/log/messages 가 0666", "/var/log/messages 가 0600", "소유자가 root", "sshd 로그가 기록됨"],evidence:["/var/log/messages 가 0666"],verdict:function(fs){var f=fs.files['/var/log/messages']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/var/log/messages','0640');},fixNote:"/var/log/messages 권한을 0640 으로 바꿨습니다."},
    {id:"SRV-076",risk:4,title:"사용자 홈 디렉터리 권한 적정성",brief:"홈 디렉터리가 <b>전체 쓰기 가능</b>하면 다른 사용자가 그 안에 파일을 심을 수 있습니다. 로그인 시 읽히는 설정 파일을 바꿔치기하는 수법이 흔합니다.",where:"/home/kim.tx 의 권한",hint:"디렉터리 권한의 마지막 자리를 보세요.",why:"홈 디렉터리가 0777 이라 다른 사용자가 파일을 만들거나 바꿀 수 있습니다. 0700 또는 0750 이 적절합니다.",cmds:["ls -al /home/kim.tx", "ls -l /home/kim.tx"],options:["/home/kim.tx 가 0777", "/home/kim.tx 가 0700", "소유자가 kim.tx", ".bash_profile 이 존재"],evidence:["/home/kim.tx 가 0777"],verdict:function(fs){var f=fs.files['/home/kim.tx']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/home/kim.tx','0700');},fixNote:"홈 디렉터리 권한을 0700 으로 바꿨습니다."},
    {id:"SRV-077",risk:4,title:"사용자 환경 설정 파일 보호",brief:".bash_profile 은 <b>로그인할 때마다 실행</b>됩니다. 다른 사람이 쓸 수 있으면 그 사용자가 로그인하는 순간 원하는 명령을 실행시킬 수 있습니다.",where:"/home/kim.tx/.bash_profile 의 권한",hint:"환경 파일에 others/group 쓰기 권한이 있는지 보세요.",why:"환경 파일이 0666 이라 누구나 고칠 수 있습니다. 0600 으로 두어야 소유자만 바꿀 수 있습니다.",cmds:["ls -al /home/kim.tx/.bash_profile", "cat /home/kim.tx/.bash_profile"],options:[".bash_profile 이 0666", ".bash_profile 이 0600", "PATH 에 홈 디렉터리가 추가됨", "소유자가 kim.tx"],evidence:[".bash_profile 이 0666"],verdict:function(fs){var f=fs.files['/home/kim.tx/.bash_profile']; if(!f) return 'good';var m=String(f.mode);return ((parseInt(m.slice(-1),10)&2)||(parseInt(m.slice(-2,-1),10)&2))?'vuln':'good';},fix:function(fs){fs.chmod('/home/kim.tx/.bash_profile','0600');},fixNote:".bash_profile 권한을 0600 으로 바꿨습니다."},
    {id:"SRV-078",risk:4,title:"소유자가 없는 파일 정리",brief:"계정을 지우면 그 계정이 만든 파일은 <b>숫자 UID 만 남습니다</b>. 나중에 같은 UID 가 새 계정에 배정되면 그 사람이 옛 파일을 그대로 물려받습니다.",where:"소유자 UID 가 계정으로 풀리지 않는 파일",hint:"find 로 nouser 파일을 찾아보세요.",why:"stage.dat 의 소유자가 계정으로 풀리지 않는 숫자 UID 입니다. 내용을 확인해 필요하면 현재 담당자에게 소유권을 옮기고, 아니면 지워야 합니다.",cmds:["find / -nouser", "ls -al /var/tmp/stage.dat"],options:["/var/tmp/stage.dat 의 소유자가 숫자 UID(1499)", "모든 파일에 소유자가 있음", "권한이 0666", "/var/log 에 파일 있음"],evidence:["/var/tmp/stage.dat 의 소유자가 숫자 UID(1499)"],verdict:function(fs){for(var p in fs.files){var f=fs.files[p];if(!f.missing&&/^\d+$/.test(String(f.owner))) return 'vuln';} return 'good';},fix:function(fs){fs.chown('/var/tmp/stage.dat','root','root');},fixNote:"stage.dat 의 소유권을 root 로 정리했습니다(내용 확인 후)."},
    {id:"SRV-082",risk:5,title:"최상위 계정의 명령 탐색 경로 안전성",brief:"PATH 맨 앞에 <code>.</code>(현재 디렉터리)가 있으면, root 가 어떤 디렉터리에서 <code>ls</code> 를 치는 순간 <b>그 디렉터리에 있는 가짜 ls</b> 가 먼저 실행됩니다.",where:"/root/.bash_profile 의 PATH",hint:"PATH 맨 앞에 무엇이 있는지 보세요.",why:"root 의 PATH 가 <code>.</code> 로 시작합니다. 공격자가 쓰기 가능한 디렉터리에 가짜 명령을 두고 root 가 그 위치에서 명령을 치기만 기다리면 됩니다.",cmds:["cat /root/.bash_profile", "grep PATH /root/.bash_profile"],options:["PATH 맨 앞에 . 이 있음", "PATH 가 /usr/bin 으로 시작", "export PATH 가 있음", "umask 설정이 있음"],evidence:["PATH 맨 앞에 . 이 있음"],verdict:function(fs){var b=fs.read('/root/.bash_profile')||'';var m=b.match(/^\s*PATH=([^\n]*)/m); if(!m) return 'good';return /(^|=|:)\.(:|$)/.test(m[1])?'vuln':'good';},fix:function(fs){var b=fs.read('/root/.bash_profile');fs.write('/root/.bash_profile', b.replace('PATH=.:','PATH='));},fixNote:"root PATH 에서 현재 디렉터리(.)를 제거했습니다."},
    {id:"SRV-083",risk:3,title:"파일 생성 기본 권한 설정",brief:"umask 는 <b>앞으로 만들 파일의 기본 권한</b>을 정합니다. 000 이면 새로 만드는 파일마다 전체 쓰기 권한이 붙어, 위에서 하나씩 고친 문제가 계속 다시 생깁니다.",where:"/etc/profile 의 umask",hint:"umask 값이 몇 인지 보세요.",why:"umask 가 000 이라 새로 만드는 파일이 666, 디렉터리가 777 로 생깁니다. 022(또는 027)로 두어야 group·others 쓰기 권한이 기본으로 빠집니다.",cmds:["grep umask /etc/profile", "cat /etc/profile"],options:["umask 000 (새 파일이 전체 쓰기 가능)", "umask 022", "umask 027", "export PATH 가 있음"],evidence:["umask 000 (새 파일이 전체 쓰기 가능)"],verdict:function(fs){var b=fs.read('/etc/profile')||'';var m=b.match(/^\s*umask\s+(\d+)/m); if(!m) return 'vuln';var v=m[1].slice(-3); return (parseInt(v[1],10)>=2&&parseInt(v[2],10)>=2)?'good':'vuln';},fix:function(fs){var b=fs.read('/etc/profile');fs.write('/etc/profile', b.replace('umask 000','umask 022'));},fixNote:"/etc/profile 의 umask 를 022 로 바꿨습니다."},
    {id:"SRV-079",risk:3,title:"개발 도구 실행 권한 제한",brief:"운영 서버에 컴파일러가 <b>누구나 실행 가능</b>하면, 침입자가 공격 코드를 그 자리에서 빌드해 쓸 수 있습니다. 필요 없으면 지우고, 필요하면 실행을 제한합니다.",where:"/usr/bin/gcc 의 권한",hint:"others 에 실행 권한이 있는지 보세요.",why:"운영 서버의 gcc 를 모든 사용자가 실행할 수 있습니다. 빌드는 별도 서버에서 하고 운영 서버에서는 제거하거나 실행 권한을 관리자 그룹으로 좁히는 것이 일반적입니다.",cmds:["ls -al /usr/bin/gcc"],options:["gcc 가 0755 (모든 사용자 실행 가능)", "gcc 가 0750", "gcc 가 설치돼 있지 않음", "소유자가 root"],evidence:["gcc 가 0755 (모든 사용자 실행 가능)"],verdict:function(fs){var f=fs.files['/usr/bin/gcc']; if(!f||f.missing) return 'good';return (parseInt(String(f.mode).slice(-1),10)&1)?'vuln':'good';},fix:function(fs){fs.chmod('/usr/bin/gcc','0750');},fixNote:"gcc 의 others 실행 권한을 제거했습니다(0750)."},
    {id:"SRV-099",risk:3,title:"로그 파일 접근 통제",brief:"로그를 <b>읽을 수 있는 범위</b>도 통제 대상입니다. 로그에는 계정명, 내부 주소, 오류 메시지 같은 정찰에 쓸 만한 정보가 그대로 남습니다.",where:"/var/log/messages 의 읽기 권한",hint:"others 읽기 권한이 필요할까요?",why:"로그 파일에 others 읽기 권한이 있어 일반 사용자도 내용을 볼 수 있습니다. 0640 이하로 두고 열람이 필요한 인원은 그룹으로 관리해야 합니다.",cmds:["ls -al /var/log/messages", "cat /var/log/messages"],options:["로그를 모든 사용자가 읽을 수 있음", "로그가 0600", "로그에 sshd 기록이 있음", "소유자가 root"],evidence:["로그를 모든 사용자가 읽을 수 있음"],verdict:function(fs){var f=fs.files['/var/log/messages']; if(!f) return 'good';return (parseInt(String(f.mode).slice(-1),10)&4)?'vuln':'good';},fix:function(fs){fs.chmod('/var/log/messages','0640');},fixNote:"/var/log/messages 권한을 0640 으로 바꿔 others 읽기를 막았습니다."}
  ]
};
