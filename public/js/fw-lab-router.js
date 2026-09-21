/* 생성물 — _gen/gen_fw_lab.py 가 만든다. 직접 고치지 말 것. */
window.FW_LAB_DATA = {
  host: {"name": "fw-workbench", "device": "GaonNet GN-7000 (가정용 공유기)", "arch": "MIPS (32-bit, big-endian)", "prompt": "analyst@fw-lab:~/gn7000.extracted$", "image": {"file": "gn7000_v2.3.bin", "encrypted": false, "len": 8192, "layout": [{"kind": "uimage", "size": 64, "name": "GN-7000 Linux-3.10.14"}, {"kind": "lzma", "size": 1024}, {"kind": "squashfs", "size": 5120}, {"kind": "text", "text": "admin:admin\nsupport factory shell\nGN7000-FACTORY-DEFAULT\n"}]}, "nvram": {"lan_ipaddr": "192.168.10.1", "http_username": "admin", "admin_password": "admin", "wifi_ssid": "GaonNet-7000", "telnet_enable": "1"}, "uboot": {"bootdelay": "3", "baudrate": "115200", "bootcmd": "bootm 0x82000000", "bootargs": "console=ttyS0,115200 root=/dev/mtdblock2 rootfstype=squashfs"}, "cvedb": {"busybox": [{"id": "CVE-2018-1000517", "sev": "HIGH", "desc": "wget 응답 처리 힙 버퍼 오버플로", "fixed": "1.29.0"}, {"id": "CVE-2017-16544", "sev": "MEDIUM", "desc": "lineedit 탭 자동완성으로 임의 문자 주입", "fixed": "1.28.0"}, {"id": "CVE-2021-42374", "sev": "MEDIUM", "desc": "unlzma 힙 범위 밖 읽기", "fixed": "1.34.0"}]}, "incident": {"title": "봇넷이 GN-7000 공유기를 장악한 사건", "story": "같은 모델 공유기 수천 대가 한밤중 낯선 IP 로 향하는 트래픽을 냈다는 신고가 들어왔다. 확보한 배포 펌웨어 한 벌을 이 워크벤치에서 열어, 봇넷이 어떻게 최초 침투 → 권한 획득 → 코드 실행 → 지속성·공급망 장악에 이르렀는지 순서대로 재구성한다. 각 단계 아래 칩을 눌러 해당 점검으로 이동하라. 판정은 각 점검의 고정 검사기가 하고, 막히면 아래 AI 코치가 다음 확인 행동 하나를 제안한다.", "stages": [{"label": "1. 정찰 — 배포 이미지 확보·추출", "ids": ["FW-01"]}, {"label": "2. 최초 침투 — 원격 접점·부트로더", "ids": ["FW-04", "FW-10", "FW-09"]}, {"label": "3. 권한 획득 — 계정·비밀번호·키", "ids": ["FW-02", "FW-03", "FW-05"]}, {"label": "4. 코드 실행 — 웹/서비스 취약점", "ids": ["FW-06", "FW-07"]}, {"label": "5. 지속성·공급망 — 업데이트 위조", "ids": ["FW-08"]}]}},
  fs: {
 "/": {
  "dir": true
 },
 "/etc": {
  "dir": true
 },
 "/etc/passwd": {
  "body": "root:x:0:0:root:/root:/bin/ash\ndaemon:x:1:1:daemon:/var:/bin/false\nnobody:x:65534:65534:nobody:/:/bin/false\nsupport:x:0:0:factory support:/root:/bin/ash\n"
 },
 "/etc/shadow": {
  "body": "root:$1$Xa1p$4bJt9Qm0eKpT2vC7dNlq30:19000:0:99999:7:::\nsupport:$1$s0s0$q7Yr2mE1nB8kZ4wV6tGxU1:19000:0:99999:7:::\n",
  "mode": "0644"
 },
 "/etc/group": {
  "body": "root:x:0:\nnobody:x:65534:\n"
 },
 "/etc/inittab": {
  "body": "::sysinit:/etc/init.d/rcS\n::respawn:/usr/sbin/telnetd -l /bin/sh\nttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100\n::shutdown:/etc/init.d/rcK\n"
 },
 "/etc/banner": {
  "body": "  GaonNet GN-7000  \n  home router firmware v2.3\n"
 },
 "/etc/fwupdate.conf": {
  "body": "# GN-7000 자동 펌웨어 업데이트 설정\nurl = http://update.gaonnet-cdn.example/gn7000/latest.bin\ncheck_interval = 86400\nverify_signature = 0\n"
 },
 "/etc/config": {
  "dir": true
 },
 "/etc/config/network": {
  "body": "config interface 'lan'\n    option ipaddr '192.168.10.1'\n"
 },
 "/etc/ssl": {
  "dir": true
 },
 "/etc/ssl/private": {
  "dir": true,
  "mode": "0755"
 },
 "/etc/ssl/private/device.key": {
  "body": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2n4Jq3f8Wd1oQKpShippedInEveryUnitxxxxxxxxxxxxxxxx\nb3RhbGx5IHRoZSBzYW1lIGtleSBvbiBldmVyeSBHTi03MDAwIGV2ZXIgc2hpcHBl\nZC4gTUlUTSBhbnlvbmUncyBUTFMu................................\n-----END RSA PRIVATE KEY-----\n",
  "mode": "0644"
 },
 "/www": {
  "dir": true
 },
 "/www/cgi-bin": {
  "dir": true
 },
 "/www/cgi-bin/ping.cgi": {
  "body": "#!/bin/sh\necho \"Content-type: text/plain\"\necho \"\"\n# host 파라미터로 대상 IP 를 받아 ping 한다\nhost=$(echo \"$QUERY_STRING\" | sed -n \"s/^host=//p\")\nsystem(\"ping -c 3 $host\")\n",
  "mode": "0755"
 },
 "/www/index.html": {
  "body": "<html><body>GN-7000 admin</body></html>\n"
 },
 "/bin": {
  "dir": true
 },
 "/bin/busybox": {
  "bin": true,
  "mode": "0755",
  "ftype": "ELF 32-bit MSB executable, MIPS, MIPS32 rel2, statically linked",
  "strings": [
   "BusyBox v1.19.4 (2013-07-22 14:10:20 CST) multi-call binary.",
   "Usage: busybox [function [arguments]...]",
   "httpd telnetd udhcpc ash sed wget",
   "GCC: (GNU) 4.3.3"
  ]
 },
 "/usr": {
  "dir": true
 },
 "/usr/sbin": {
  "dir": true
 },
 "/usr/sbin/telnetd": {
  "bin": true,
  "mode": "0755",
  "ftype": "ELF 32-bit MSB executable, MIPS",
  "strings": [
   "telnetd",
   "-l login shell"
  ]
 },
 "/etc/rc.local": {
  "body": "#!/bin/sh\n# factory debug hook (제거 예정이었으나 남음)\n/usr/sbin/utelnetd -p 9527 -l /bin/sh &\nexit 0\n"
 },
 "/usr/sbin/utelnetd": {
  "bin": true,
  "mode": "0755",
  "ftype": "ELF 32-bit MSB executable, MIPS",
  "strings": [
   "micro telnetd",
   "-p <port> -l <shell>"
  ]
 }
},
  missions: [
    {id:"FW-01",risk:4,title:"배포 펌웨어 이미지 암호화·서명 부재",brief:"배포되는 펌웨어 <code>gn7000_v2.3.bin</code> 을 binwalk 로 열어 본다. 이미지가 암호화·서명돼 있으면 시그니처가 안 잡히고, 평문이면 내장 파일시스템이 그대로 드러난다.",where:"binwalk gn7000_v2.3.bin",hint:"binwalk 출력에 SquashFS 파일시스템이 그대로 보인다면, 누구나 rootfs 를 꺼내 볼 수 있다는 뜻이다.",why:"이미지가 암호화·서명돼 있지 않아 binwalk 로 SquashFS 파일시스템이 그대로 추출된다. 공격자가 펌웨어를 내려받아 내부 설정·키·바이너리를 분석하고, 위조 펌웨어를 만들 수 있다.",cmds:["binwalk gn7000_v2.3.bin", "file /bin/busybox"],options:["Squashfs filesystem, little endian, version 4.0 — 파일시스템이 평문으로 노출", "uImage header, OS: Linux, CPU: MIPS", "LZMA compressed data — 표준 압축이므로 안전", "식별된 시그니처 없음 — 고엔트로피 데이터"],evidence:["Squashfs filesystem, little endian, version 4.0 — 파일시스템이 평문으로 노출"],verdict:function(fs){return (fs.host.image&&fs.host.image.encrypted)?'good':'vuln';},fix:function(fs){fs.host.image.encrypted=true;},fixNote:"재빌드 시 이미지를 서명하고 본문을 암호화했다. 이제 binwalk 는 시그니처를 찾지 못한다."},
    {id:"FW-02",risk:5,title:"펌웨어에 박힌 2차 관리자(uid 0) 계정",brief:"추출된 rootfs 의 <code>/etc/passwd</code> 를 본다. root 외에 uid 0 을 가진 계정이 펌웨어에 함께 배포되면, 모든 기기에서 동일한 백도어 관리자가 된다.",where:"/etc/passwd",hint:"uid·gid 가 0:0 인 줄이 root 말고 또 있는지 본다.",why:"root 외에 uid 0 인 <code>support</code> 계정이 펌웨어에 포함돼 있다. 모든 GN-7000 이 같은 관리자 계정을 공유하므로, 계정 하나가 뚫리면 전 기종이 뚫린다.",cmds:["cat /etc/passwd", "cat /etc/passwd | grep :0:0:"],options:["support:x:0:0:factory support:/root:/bin/ash", "root:x:0:0:root:/root:/bin/ash", "nobody:x:65534:65534:nobody:/:/bin/false", "daemon:x:1:1:daemon:/var:/bin/false"],evidence:["support:x:0:0:factory support:/root:/bin/ash"],verdict:function(fs){var p=fs.read('/etc/passwd')||'';var e=p.split('\n').filter(function(l){return /:0:0:/.test(l)&&l.indexOf('root:')!==0;});return e.length?'vuln':'good';},fix:function(fs){var p=fs.read('/etc/passwd')||'';fs.write('/etc/passwd',p.split('\n').filter(function(l){return l.indexOf('support:')!==0;}).join('\n'));},fixNote:"펌웨어 빌드에서 support 계정을 제거했다. 이제 uid 0 은 root 뿐이다."},
    {id:"FW-03",risk:4,title:"공장 기본 관리자 비밀번호",brief:"기기 설정(nvram)에 관리자 비밀번호가 <code>admin</code> 같은 공장 기본값으로 들어 있는지 본다. 사용자가 바꾸지 않으면 인터넷에서 그대로 로그인된다.",where:"nvram show",hint:"admin_password 값이 admin/1234 같은 추측 가능한 기본값인지 확인한다.",why:"관리자 비밀번호가 공장 기본값 <code>admin</code> 이다. 첫 부팅 시 강제 변경을 요구하지 않으면 대량의 기기가 기본 크리덴셜로 노출된다.",cmds:["nvram show", "nvram show | grep -i pass", "nvram get admin_password"],options:["admin_password=admin", "http_username=admin", "wifi_ssid=GaonNet-7000", "lan_ipaddr=192.168.10.1"],evidence:["admin_password=admin"],verdict:function(fs){var v=String((fs.host.nvram||{}).admin_password||'');return /^(admin|password|1234|0000|root|)$/i.test(v)?'vuln':'good';},fix:function(fs){fs.host.nvram.admin_password='!MUST_SET_ON_FIRST_BOOT!';},fixNote:"공장 기본 비밀번호를 없애고 첫 부팅 시 강제 설정하도록 바꿨다."},
    {id:"FW-04",risk:5,title:"부팅 시 인증 없는 telnet 백도어",brief:"<code>/etc/inittab</code> 을 본다. 부팅 때 자동으로 뜨는 서비스 중 인증을 건너뛰고 셸을 바로 붙이는 것이 있으면 원격 루트 백도어가 된다.",where:"/etc/inittab",hint:"telnetd 가 -l 로 무엇을 실행하는지 본다. /bin/login 이 아니라 /bin/sh 면 로그인을 건너뛴다.",why:"telnetd 가 <code>-l /bin/sh</code> 로 떠서, 접속하면 로그인 없이 루트 셸이 열린다. 표준 구성은 <code>-l /bin/login</code> 으로 인증을 거치게 하거나 telnet 자체를 끈다.",cmds:["cat /etc/inittab", "cat /etc/inittab | grep telnetd"],options:["::respawn:/usr/sbin/telnetd -l /bin/sh", "::sysinit:/etc/init.d/rcS", "ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100", "::shutdown:/etc/init.d/rcK"],evidence:["::respawn:/usr/sbin/telnetd -l /bin/sh"],verdict:function(fs){var t=fs.read('/etc/inittab')||'';return /telnetd\s+-l\s+\/bin\/(sh|ash)\b/.test(t)?'vuln':'good';},fix:function(fs){var t=fs.read('/etc/inittab')||'';fs.write('/etc/inittab',t.split('\n').filter(function(l){return l.indexOf('telnetd')<0;}).join('\n'));},fixNote:"inittab 에서 telnetd 자동 시작 줄을 제거했다. 원격 관리는 인증이 있는 SSH 로만 연다."},
    {id:"FW-05",risk:5,title:"펌웨어에 포함된 TLS 개인키",brief:"펌웨어 안에 개인키(.key/.pem)가 들어 있는지 찾는다. 모든 기기가 같은 키를 쓰면 한 대에서 키를 꺼내 나머지 전부의 TLS 를 가로챌 수 있다.",where:"/etc/ssl/private/",hint:"find 로 .key 파일이 나오면, 그 키가 전 기종 공통인지 생각해 본다.",why:"TLS 개인키 <code>/etc/ssl/private/device.key</code> 가 펌웨어에 그대로 포함돼 모든 기기가 동일한 키를 쓴다. 키가 한 번 유출되면 전 기종의 HTTPS·기기 인증이 위조·감청된다. 키는 펌웨어에 넣지 말고 첫 부팅 시 기기별로 생성해야 한다.",cmds:["find /etc -name \"*.key\"", "cat /etc/ssl/private/device.key"],options:["/etc/ssl/private/device.key", "/etc/ssl/fwupdate-release.pub", "/www/index.html", "/etc/config/network"],evidence:["/etc/ssl/private/device.key"],verdict:function(fs){return fs.exists('/etc/ssl/private/device.key')?'vuln':'good';},fix:function(fs){fs.remove('/etc/ssl/private/device.key');},fixNote:"펌웨어에서 공통 개인키를 제거했다. 기기 키는 첫 부팅 시 각 기기에서 생성한다."},
    {id:"FW-06",risk:5,title:"웹 CGI 명령 인젝션",brief:"<code>/www/cgi-bin/ping.cgi</code> 를 본다. 사용자가 보낸 값을 검증 없이 쉘 명령에 넣으면 누구나 기기에서 임의 명령을 실행할 수 있다.",where:"/www/cgi-bin/ping.cgi",hint:"$host 같은 요청 값이 검증 없이 system()/쉘로 넘어가는 줄을 찾는다.",why:"host 파라미터가 검증 없이 <code>system(\"ping -c 3 $host\")</code> 로 넘어간다. <code>host=8.8.8.8;telnetd -l /bin/sh</code> 같은 입력으로 임의 명령이 실행된다. 요청 값은 형식 검증 후 쉘을 거치지 않고 고정 인자로 실행해야 한다.",cmds:["cat /www/cgi-bin/ping.cgi", "cat /www/cgi-bin/ping.cgi | grep system"],options:["system(\"ping -c 3 $host\")", "host=$(echo \"$QUERY_STRING\" | sed -n \"s/^host=//p\")", "echo \"Content-type: text/plain\"", "#!/bin/sh"],evidence:["system(\"ping -c 3 $host\")"],verdict:function(fs){var c=fs.read('/www/cgi-bin/ping.cgi')||'';return /system\([^)]*\$(host|QUERY_STRING|_GET|FORM|ip)/.test(c)?'vuln':'good';},fix:function(fs){fs.write('/www/cgi-bin/ping.cgi','SAFE');},fixNote:"ping.cgi 를 재작성해 입력을 IPv4 형식으로 검증하고, 쉘을 거치지 않고 고정 인자로 실행하게 했다."},
    {id:"FW-07",risk:4,title:"지원 종료된 BusyBox — 알려진 취약점 다수",brief:"핵심 바이너리 <code>/bin/busybox</code> 의 버전을 strings 로 확인한다. 오래된 버전은 공개된 CVE 가 쌓여 있어 그 자체로 취약점 목록이 된다.",where:"/bin/busybox (strings)",hint:"BusyBox 버전 문자열을 찾아 현재 지원 버전과 비교한다. 1.2x 대 이하는 EOL 이다. cve-check 로 매핑된 CVE 를 확인하라.",why:"BusyBox v1.19.4(2013년) 는 지원이 끝난 버전으로, httpd·telnetd 등에서 공개된 취약점이 여럿 있다. 버전 문자열만으로 알려진 CVE 목록을 매핑할 수 있다. 현재 지원 버전으로 재빌드해야 한다.",cmds:["file /bin/busybox", "strings /bin/busybox | grep -i busybox", "cve-check busybox 1.19.4"],options:["BusyBox v1.19.4 (2013-07-22 14:10:20 CST) multi-call binary.", "GCC: (GNU) 4.3.3", "Usage: busybox [function [arguments]...]", "httpd telnetd udhcpc ash sed wget"],evidence:["BusyBox v1.19.4 (2013-07-22 14:10:20 CST) multi-call binary."],verdict:function(fs){var f=fs.files['/bin/busybox'];var s=((f&&f.strings)||[]).join('\n');var m=s.match(/BusyBox v(\d+)\.(\d+)/);if(!m)return 'good';var maj=+m[1],min=+m[2];return (maj<1||(maj===1&&min<30))?'vuln':'good';},fix:function(fs){var f=fs.files['/bin/busybox'];if(f)f.strings=['BusyBox v1.36.1 (2024-05-18 09:02:44 UTC) multi-call binary.','Usage: busybox [function [arguments]...]','httpd udhcpc ash sed wget','GCC: (GNU) 12.3.0'];},fixNote:"BusyBox 를 현재 지원 버전(1.36.1)으로 올려 재빌드했다. telnetd 도 함께 뺐다."},
    {id:"FW-08",risk:4,title:"서명 검증 없는 HTTP 펌웨어 업데이트",brief:"<code>/etc/fwupdate.conf</code> 를 본다. 업데이트를 평문 HTTP 로 받거나 서명 검증을 하지 않으면 중간자 공격자가 위조 펌웨어를 밀어 넣을 수 있다.",where:"/etc/fwupdate.conf",hint:"url 이 http:// 인지, verify_signature 가 0 인지 둘 다 본다. 하나라도 해당하면 위조 펌웨어가 통과한다.",why:"업데이트를 <code>http://</code> 로 받고 <code>verify_signature=0</code> 이라, 경로상의 공격자가 위조 펌웨어로 바꿔치기해도 기기가 그대로 설치한다. HTTPS + 서명 검증(공개키 고정)이 필요하다.",cmds:["cat /etc/fwupdate.conf", "cat /etc/fwupdate.conf | grep -i verify"],options:["verify_signature = 0", "url = http://update.gaonnet-cdn.example/gn7000/latest.bin", "check_interval = 86400", "url = https://update.gaonnet-cdn.example/gn7000/latest.bin"],evidence:["verify_signature = 0", "url = http://update.gaonnet-cdn.example/gn7000/latest.bin"],verdict:function(fs){var c=fs.read('/etc/fwupdate.conf')||'';var http=/^\s*url\s*=\s*http:\/\//im.test(c);var nv=/^\s*verify_signature\s*=\s*(0|no|false|off)\b/im.test(c);return (http||nv)?'vuln':'good';},fix:function(fs){fs.write('/etc/fwupdate.conf','# GN-7000 update\nurl = https://update.gaonnet-cdn.example/gn7000/latest.bin\ncheck_interval = 86400\nverify_signature = 1\npubkey = /etc/ssl/fwupdate-release.pub\n');},fixNote:"업데이트 URL 을 HTTPS 로 바꾸고 서명 검증(verify_signature=1)과 릴리스 공개키 고정을 켰다."},
    {id:"FW-09",risk:4,title:"U-Boot 부트 인터럽트로 부트로더 셸 탈취",brief:"U-Boot 환경변수를 <code>printenv</code> 로 본다. <code>bootdelay</code> 가 0보다 크면 부팅 중 시리얼 콘솔에서 키를 눌러 부트로더 셸에 진입하고, bootargs 에 <code>init=/bin/sh</code> 를 넣어 인증을 통째로 우회할 수 있다.",where:"U-Boot 환경변수 (printenv)",hint:"bootdelay 값이 0인지 본다. 0보다 크면 그 시간 동안 부팅을 멈추고 부트로더 셸을 얻을 수 있다.",why:"<code>bootdelay=3</code> 이라 기기를 뜯어 UART 에 연결한 사람이 부팅 3초 안에 콘솔을 눌러 U-Boot 셸에 들어가고, <code>setenv bootargs ... init=/bin/sh</code> 로 루트 셸로 부팅할 수 있다. 양산 기기는 bootdelay=0 과 콘솔 잠금이 필요하다.",cmds:["printenv", "printenv bootdelay"],options:["bootdelay=3", "baudrate=115200", "bootcmd=bootm 0x82000000", "bootargs=console=ttyS0,115200 root=/dev/mtdblock2 rootfstype=squashfs"],evidence:["bootdelay=3"],verdict:function(fs){var d=(fs.host.uboot||{}).bootdelay;return (d!=null&&Number(d)>0)?'vuln':'good';},fix:function(fs){if(fs.host.uboot)fs.host.uboot.bootdelay='0';},fixNote:"bootdelay 를 0으로 설정해 콘솔 인터럽트를 막았다(양산 시 콘솔 잠금도 함께)."},
    {id:"FW-10",risk:5,title:"부팅 후 드러나는 문서에 없는 백도어 포트",brief:"정적 설정만으로는 놓치기 쉬운 서비스가 있다. 펌웨어를 <code>boot</code> 로 부팅해 <code>netstat</code> 로 실제 열린 포트를 보면, 문서에 없는 서비스가 리스닝하고 있는지 드러난다.",where:"부팅 후 netstat / /etc/rc.local",hint:"boot 후 netstat 에서 문서화된 포트(23/80) 외에 낯선 고포트가 떠 있는지 본다. 그 포트를 여는 곳을 rc.local 에서 찾는다.",why:"<code>/etc/rc.local</code> 이 부팅 때 <code>utelnetd -p 9527 -l /bin/sh</code> 로 인증 없는 셸을 9527 포트에 띄운다. 정적 점검에서 놓쳐도 부팅 후 netstat 에 <code>0.0.0.0:9527</code> 로 드러난다. rc.local 의 해당 줄을 제거해야 한다.",cmds:["boot gn7000_v2.3.bin", "netstat -an", "cat /etc/rc.local"],options:["0.0.0.0:9527 (문서에 없는 서비스 utelnetd)", "0.0.0.0:23 (telnetd — 이미 알려진 항목)", "0.0.0.0:80 (httpd — 관리 웹)", "/usr/sbin/utelnetd -p 9527 -l /bin/sh &"],evidence:["0.0.0.0:9527 (문서에 없는 서비스 utelnetd)", "/usr/sbin/utelnetd -p 9527 -l /bin/sh &"],verdict:function(fs){var r=fs.read('/etc/rc.local')||'';return /utelnetd|-p\s*9527/.test(r)?'vuln':'good';},fix:function(fs){var r=fs.read('/etc/rc.local')||'';fs.write('/etc/rc.local',r.split('\n').filter(function(l){return l.indexOf('utelnetd')<0;}).join('\n'));},fixNote:"rc.local 에서 백도어 telnet 시작 줄을 제거했다. 재부팅 시 9527 포트가 열리지 않는다."}
  ]
};
