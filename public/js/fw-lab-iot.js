/* 생성물 — _gen/gen_fw_lab.py 가 만든다. 직접 고치지 말 것. */
window.FW_LAB_DATA = {
  host: {"name": "fw-workbench", "device": "CamEye C-210 (IP 카메라)", "arch": "ARM (32-bit, little-endian)", "prompt": "analyst@fw-lab:~/cameye.extracted$", "image": {"file": "cameye_c210_fw_1.4.img", "encrypted": false, "len": 8192, "layout": [{"kind": "jffs2", "size": 512}, {"kind": "uimage", "size": 64, "name": "CamEye C-210 Linux-4.9"}, {"kind": "lzma", "size": 1024}, {"kind": "squashfs", "size": 4096}]}, "nvram": {}},
  fs: {
 "/": {
  "dir": true
 },
 "/etc": {
  "dir": true
 },
 "/etc/inittab": {
  "body": "::sysinit:/etc/init.d/rcS\nttyS0::respawn:/bin/sh\n::shutdown:/etc/init.d/rcK\n"
 },
 "/etc/passwd": {
  "body": "root:x:0:0:root:/root:/bin/sh\nnobody:x:65534:65534:nobody:/:/bin/false\n"
 },
 "/etc/rtsp.conf": {
  "body": "# CamEye C-210 RTSP 서버\nlisten = 0.0.0.0:554\nauth = none\nstream = /live\n"
 },
 "/etc/config": {
  "dir": true
 },
 "/etc/config/cloud": {
  "body": "# 클라우드 연동 계정\nendpoint = https://cloud.cameye.example\nusername = device-838271\npassword = c210-cloud-8s7d6f\n"
 },
 "/etc/init.d": {
  "dir": true
 },
 "/etc/init.d/rcS": {
  "body": "#!/bin/sh\nmount -a\n/usr/bin/camd &\n",
  "mode": "0777"
 },
 "/etc/init.d/rcK": {
  "body": "#!/bin/sh\nkillall camd\n",
  "mode": "0755"
 },
 "/etc/rc.local": {
  "body": "#!/bin/sh\n# debug (임시)\n/usr/sbin/telnetd -p 2323 -l /bin/sh &\nexit 0\n"
 },
 "/usr": {
  "dir": true
 },
 "/usr/bin": {
  "dir": true
 },
 "/usr/bin/camd": {
  "bin": true,
  "mode": "0755",
  "ftype": "ELF 32-bit LSB executable, ARM, EABI5, dynamically linked",
  "strings": [
   "camd 1.4 (CamEye C-210)",
   "rtsp://0.0.0.0:554/live",
   "CLOUD_API_KEY=ak_live_9f3b2c7d1e5a4088c6b0d2f1",
   "POST /v1/devices/register"
  ]
 },
 "/data": {
  "dir": true
 }
},
  missions: [
    {id:"FW-11",risk:4,title:"UART 시리얼 콘솔 무인증 루트 셸",brief:"<code>/etc/inittab</code> 을 본다. 시리얼 콘솔(ttyS0)에 로그인 절차 없이 셸이 붙으면, 기기를 뜯어 UART 에 연결한 사람이 곧바로 루트를 얻는다.",where:"/etc/inittab",hint:"ttyS0 줄이 /sbin/getty(로그인) 가 아니라 /bin/sh 를 바로 실행하는지 본다.",why:"시리얼 콘솔이 <code>ttyS0::respawn:/bin/sh</code> 로 떠서 인증 없이 루트 셸이 열린다. 양산 펌웨어는 콘솔에 getty+login 을 두거나 시리얼 콘솔을 비활성화해야 한다.",cmds:["cat /etc/inittab", "cat /etc/inittab | grep ttyS0"],options:["ttyS0::respawn:/bin/sh", "::sysinit:/etc/init.d/rcS", "::shutdown:/etc/init.d/rcK", "listen = 0.0.0.0:554"],evidence:["ttyS0::respawn:/bin/sh"],verdict:function(fs){var t=fs.read('/etc/inittab')||'';return /ttyS0::respawn:\/bin\/(sh|ash)\b/.test(t)?'vuln':'good';},fix:function(fs){var t=fs.read('/etc/inittab')||'';fs.write('/etc/inittab',t.replace(/ttyS0::respawn:\/bin\/(sh|ash)\b/,'ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100'));},fixNote:"시리얼 콘솔을 getty+login 으로 바꿔 인증을 거치게 했다."},
    {id:"FW-12",risk:5,title:"바이너리에 하드코딩된 클라우드 API 키",brief:"카메라 데몬 <code>/usr/bin/camd</code> 를 strings 로 훑어 하드코딩된 키·토큰이 있는지 본다. 펌웨어에 박힌 키는 한 대만 추출해도 전 기기의 클라우드 계정을 침해한다.",where:"/usr/bin/camd (strings)",hint:"KEY/TOKEN/SECRET 뒤에 실제 값처럼 보이는 문자열이 붙어 있는지 본다.",why:"<code>CLOUD_API_KEY=ak_live_...</code> 가 바이너리에 그대로 박혀 있어, 펌웨어를 가진 누구나 클라우드 API 를 그 키로 호출할 수 있다. 키는 펌웨어에 넣지 말고 기기별 보안 저장소에서 로드해야 한다.",cmds:["file /usr/bin/camd", "strings /usr/bin/camd | grep -iE \"key|token|secret\""],options:["CLOUD_API_KEY=ak_live_9f3b2c7d1e5a4088c6b0d2f1", "rtsp://0.0.0.0:554/live", "POST /v1/devices/register", "camd 1.4 (CamEye C-210)"],evidence:["CLOUD_API_KEY=ak_live_9f3b2c7d1e5a4088c6b0d2f1"],verdict:function(fs){var f=fs.files['/usr/bin/camd'];var s=((f&&f.strings)||[]).join('\n');return /(api[_-]?key|secret|token)\s*[=:]\s*\S{8,}/i.test(s)?'vuln':'good';},fix:function(fs){var f=fs.files['/usr/bin/camd'];if(f)f.strings=['camd 1.4 (CamEye C-210)','rtsp://0.0.0.0:554/live','cloud_key loaded from /data/keystore (per-device)','POST /v1/devices/register'];},fixNote:"하드코딩 키를 제거하고 기기별 keystore 에서 로드하도록 재빌드했다."},
    {id:"FW-13",risk:4,title:"RTSP 영상 스트림 인증 없음",brief:"<code>/etc/rtsp.conf</code> 를 본다. 스트림에 인증이 없으면 IP 만 알면 누구나 카메라 영상을 실시간으로 볼 수 있다.",where:"/etc/rtsp.conf",hint:"auth 값이 none 인지 digest/basic 인지 본다.",why:"RTSP 서버가 <code>auth = none</code> 으로, 0.0.0.0:554 에 붙는 누구나 인증 없이 영상을 본다. 최소 digest 인증을 켜고, 가능하면 외부 노출을 막아야 한다.",cmds:["cat /etc/rtsp.conf", "cat /etc/rtsp.conf | grep -i auth"],options:["auth = none", "listen = 0.0.0.0:554", "stream = /live", "auth = digest"],evidence:["auth = none"],verdict:function(fs){var c=fs.read('/etc/rtsp.conf')||'';return /^\s*auth\s*=\s*none\b/im.test(c)?'vuln':'good';},fix:function(fs){var c=fs.read('/etc/rtsp.conf')||'';fs.write('/etc/rtsp.conf',c.replace(/^\s*auth\s*=\s*none\b/im,'auth = digest'));},fixNote:"RTSP 스트림 인증을 digest 로 켰다."},
    {id:"FW-14",risk:4,title:"월드-라이터블 부팅 스크립트",brief:"부팅 시 실행되는 <code>/etc/init.d/rcS</code> 의 권한을 본다. 누구나 쓸 수 있으면 기기에 발판을 얻은 공격자가 부팅 스크립트를 고쳐 영구 지속성을 심는다.",where:"/etc/init.d/rcS",hint:"권한 끝자리가 others 에 쓰기(2)를 포함하는지 본다. -rwxrwxrwx 면 누구나 수정 가능하다.",why:"부팅 스크립트가 <code>0777</code>(world-writable) 이라, 로컬 권한이 있는 프로세스나 계정이 rcS 를 덮어써 재부팅마다 실행되는 백도어를 심을 수 있다. 부팅 스크립트는 root 소유 0755 여야 한다.",cmds:["ls -al /etc/init.d/rcS", "stat /etc/init.d/rcS"],options:["-rwxrwxrwx (rcS 가 others 에도 쓰기 가능)", "-rwxr-xr-x (rcK: 표준 실행 권한)", "#!/bin/sh 로 시작하는 스크립트", "mount -a; /usr/bin/camd &"],evidence:["-rwxrwxrwx (rcS 가 others 에도 쓰기 가능)"],verdict:function(fs){var f=fs.files['/etc/init.d/rcS'];if(!f||f.missing)return 'good';return (parseInt(f.mode,8)&2)?'vuln':'good';},fix:function(fs){fs.chmod('/etc/init.d/rcS','0755');},fixNote:"rcS 권한을 0755 로 조여 others 쓰기를 없앴다."},
    {id:"FW-15",risk:3,title:"설정에 평문 저장된 클라우드 비밀번호",brief:"<code>/etc/config/cloud</code> 를 본다. 클라우드 계정 비밀번호가 평문으로 저장돼 있으면 펌웨어·설정 백업을 얻은 사람이 그대로 로그인한다.",where:"/etc/config/cloud",hint:"password 항목에 값이 그대로 적혀 있는지, 아니면 보안 저장소 참조인지 본다.",why:"클라우드 계정 비밀번호가 <code>password = c210-cloud-...</code> 로 평문 저장돼 있다. 비밀번호는 평문으로 두지 말고 보안 저장소 참조(keystore)로 대체해야 한다.",cmds:["cat /etc/config/cloud", "cat /etc/config/cloud | grep -i password"],options:["password = c210-cloud-8s7d6f", "endpoint = https://cloud.cameye.example", "username = device-838271", "password_ref = keystore://cloud/device"],evidence:["password = c210-cloud-8s7d6f"],verdict:function(fs){var c=fs.read('/etc/config/cloud')||'';return /^\s*password\s*=\s*\S+/im.test(c)?'vuln':'good';},fix:function(fs){var c=fs.read('/etc/config/cloud')||'';fs.write('/etc/config/cloud',c.replace(/^\s*password\s*=\s*\S+.*$/im,'password_ref = keystore://cloud/device'));},fixNote:"평문 비밀번호를 보안 저장소 참조(keystore)로 바꿨다."},
    {id:"FW-16",risk:4,title:"카메라 배포 이미지 암호화·서명 부재",brief:"카메라 배포 펌웨어 <code>cameye_c210_fw_1.4.img</code> 를 binwalk 로 연다. 이미지가 평문이면 앞의 모든 결함을 공격자가 앉아서 분석할 수 있고, 위조 펌웨어도 만들 수 있다.",where:"binwalk cameye_c210_fw_1.4.img",hint:"binwalk 에 SquashFS/JFFS2 파일시스템이 그대로 잡히면 이미지가 보호되지 않은 것이다.",why:"이미지가 암호화·서명돼 있지 않아 파일시스템이 그대로 추출된다. 공급망 관점에서 배포 이미지는 서명(설치 시 검증)과 본문 암호화로 분석·위조를 어렵게 해야 한다.",cmds:["binwalk cameye_c210_fw_1.4.img"],options:["Squashfs filesystem, little endian, version 4.0 — 파일시스템 평문 노출", "JFFS2 filesystem, little endian", "uImage header, OS: Linux, CPU: ARM", "식별된 시그니처 없음 — 고엔트로피 데이터"],evidence:["Squashfs filesystem, little endian, version 4.0 — 파일시스템 평문 노출", "JFFS2 filesystem, little endian"],verdict:function(fs){return (fs.host.image&&fs.host.image.encrypted)?'good':'vuln';},fix:function(fs){fs.host.image.encrypted=true;},fixNote:"재빌드 시 이미지를 서명하고 본문을 암호화했다. binwalk 로 시그니처가 잡히지 않는다."},
    {id:"FW-17",risk:5,title:"부팅 후 드러나는 디버그 telnet 포트",brief:"정적 파일만 봐서는 놓치기 쉬운 서비스가 있다. 펌웨어를 <code>boot</code> 로 부팅하고 <code>netstat</code> 로 실제 열린 포트를 보면, 문서에 없는 디버그 telnet 이 리스닝하는지 드러난다.",where:"부팅 후 netstat / /etc/rc.local",hint:"boot 후 netstat 에서 RTSP(554) 외에 낯선 포트가 떠 있는지 본다. 그 포트를 여는 곳을 rc.local 에서 찾는다.",why:"<code>/etc/rc.local</code> 이 부팅 때 <code>telnetd -p 2323 -l /bin/sh</code> 로 인증 없는 셸을 2323 포트에 띄운다. 정적 점검에서 놓쳐도 부팅 후 netstat 에 <code>0.0.0.0:2323</code> 로 드러난다. 출하 전 rc.local 의 디버그 줄을 제거해야 한다.",cmds:["boot cameye_c210_fw_1.4.img", "netstat -an", "cat /etc/rc.local"],options:["0.0.0.0:2323 (문서에 없는 디버그 telnet)", "0.0.0.0:554 (RTSP — 이미 알려진 항목)", "/usr/sbin/telnetd -p 2323 -l /bin/sh &", "mount -a; /usr/bin/camd &"],evidence:["0.0.0.0:2323 (문서에 없는 디버그 telnet)", "/usr/sbin/telnetd -p 2323 -l /bin/sh &"],verdict:function(fs){var r=fs.read('/etc/rc.local')||'';return /telnetd\s+-p\s*2323/.test(r)?'vuln':'good';},fix:function(fs){var r=fs.read('/etc/rc.local')||'';fs.write('/etc/rc.local',r.split('\n').filter(function(l){return l.indexOf('telnetd')<0;}).join('\n'));},fixNote:"rc.local 에서 디버그 telnet 시작 줄을 제거했다. 재부팅 시 2323 포트가 열리지 않는다."}
  ]
};
