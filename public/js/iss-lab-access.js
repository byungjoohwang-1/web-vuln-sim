/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */
window.ISS_LAB_DATA = {
  units: [
  {device: {"name": "fin-fw-01", "type": "FW", "typeLabel": "방화벽 (VPN 겸용)", "configDate": "2026-09-15 09:12:04 KST"},
   neverFlagged: null,
   cfg: {
 "system": {
  "model": "SENTRA SG-4200",
  "serial": "SG42-2201-8871",
  "os": "SentraOS 7.2.1",
  "build": "7.2.1-b4410",
  "role": "Firewall / IPSec VPN",
  "uptime": "412 days 06:21",
  "eosDate": "2028-03-31",
  "eosPassed": false,
  "sigVersion": null,
  "sigDate": null
 },
 "admins": [
  {
   "name": "admin",
   "role": "super",
   "shared": true,
   "lastLogin": "2026-09-15 08:41:12",
   "pwChanged": "2023-11-02"
  },
  {
   "name": "fw_ops",
   "role": "super",
   "shared": true,
   "lastLogin": "2026-09-15 07:55:30",
   "pwChanged": "2024-02-18"
  },
  {
   "name": "audit",
   "role": "super",
   "shared": false,
   "lastLogin": "2026-09-12 14:02:55",
   "pwChanged": "2026-07-01"
  },
  {
   "name": "nms",
   "role": "readonly",
   "shared": false,
   "lastLogin": "2026-09-15 09:10:02",
   "pwChanged": "2026-06-30"
  }
 ],
 "auth": {
  "defaultAccount": {
   "present": true,
   "name": "admin",
   "passwordChanged": false
  },
  "password": {
   "minLength": 6,
   "complexity": "none",
   "maxAgeDays": 0,
   "reuseCheck": false
  },
  "lockout": {
   "enabled": false,
   "threshold": 0,
   "durationMin": 0
  },
  "session": {
   "lines": [
    {
     "name": "console",
     "timeoutMin": 0
    },
    {
     "name": "ssh",
     "timeoutMin": 10
    },
    {
     "name": "web",
     "timeoutMin": 60
    },
    {
     "name": "monitor",
     "timeoutMin": 0
    }
   ]
  }
 },
 "mgmt": {
  "protocols": [
   {
    "name": "https",
    "port": 443,
    "enabled": true,
    "encrypted": true
   },
   {
    "name": "ssh",
    "port": 22,
    "enabled": true,
    "encrypted": true
   },
   {
    "name": "telnet",
    "port": 23,
    "enabled": true,
    "encrypted": false
   },
   {
    "name": "http",
    "port": 80,
    "enabled": true,
    "encrypted": false
   }
  ],
  "allowedIps": [],
  "banner": false
 },
 "snmp": {
  "enabled": true,
  "version": "v2c",
  "community": "public",
  "access": "read-only",
  "user": "",
  "secLevel": "",
  "purpose": "NMS 연동 (운영팀 상시 사용)"
 },
 "logging": {
  "enabled": true,
  "loginSuccess": true,
  "loginFail": false,
  "configChange": true,
  "rawPacket": false,
  "rawPacketSeverity": 0,
  "retentionDays": 30,
  "remote": {
   "enabled": false,
   "proto": "",
   "host": "",
   "port": 0,
   "retentionDays": 0
  }
 },
 "ntp": {
  "enabled": true,
  "servers": [
   {
    "host": "10.10.0.10",
    "stratum": 3,
    "state": "synchronized"
   }
  ]
 },
 "interfaces": [
  {
   "name": "eth0",
   "zone": "untrust",
   "address": "203.0.113.10/29",
   "state": "up"
  },
  {
   "name": "eth1",
   "zone": "trust",
   "address": "10.20.0.1/16",
   "state": "up"
  },
  {
   "name": "eth2",
   "zone": "dmz",
   "address": "10.30.0.1/24",
   "state": "up"
  },
  {
   "name": "eth3",
   "zone": "mgmt",
   "address": "10.99.0.1/24",
   "state": "up"
  }
 ],
 "nat": [
  {
   "name": "web-pub",
   "original": "10.30.0.21",
   "translated": "203.0.113.11",
   "note": "DMZ 웹"
  },
  {
   "name": "batch-pub",
   "original": "10.20.4.55",
   "translated": "203.0.113.14",
   "note": "내부 배치서버"
  }
 ],
 "policyDefault": "deny",
 "rules": [],
 "services": [
  {
   "name": "ssh",
   "port": 22,
   "enabled": true,
   "purpose": "관리"
  },
  {
   "name": "https",
   "port": 443,
   "enabled": true,
   "purpose": "관리 웹"
  },
  {
   "name": "telnet",
   "port": 23,
   "enabled": true,
   "purpose": "-"
  },
  {
   "name": "http",
   "port": 80,
   "enabled": true,
   "purpose": "-"
  }
 ],
 "net": {
  "sourceRouting": true
 },
 "detect": {
  "groups": [],
  "blockMode": "n/a",
  "hwBypass": false,
  "blocks30d": null
 },
 "monitor": {
  "cpu": 38,
  "memory": 61,
  "sessions": 84120,
  "sessionMax": 500000,
  "usageReview": false,
  "usageReviewCycle": "",
  "realtime": false,
  "alerting": [],
  "logReview": false,
  "logReviewCycle": ""
 },
 "backup": {
  "policy": false,
  "policyCycle": "",
  "log": false,
  "logCycle": "",
  "last": "never",
  "dest": "-",
  "integrity": false,
  "integrityCycle": ""
 },
 "patch": {
  "latest": "SentraOS 7.4.0",
  "latestSig": null,
  "review": false,
  "reviewCycle": "",
  "advisoriesApplied": 2,
  "advisoriesTotal": 7
 },
 "change": {
  "procedure": false,
  "requestForm": false,
  "techReview": false,
  "recent": 14,
  "unapproved": 6
 }
},
   missions: [
    {id:"ISS-016",expectRules:null,risk:5,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 접속 시 보안 접속 사용 여부",brief:"Telnet 과 HTTP 는 <b>비밀번호를 평문으로</b> 보냅니다. 같은 구간을 들여다보는 사람이 있으면 관리자 계정이 그대로 넘어갑니다.",where:"show management 의 ENCRYPTED 열",hint:"암호화되지 않는데 켜져 있는 프로토콜을 찾으세요.",why:"telnet(23)과 http(80)가 켜져 있습니다. https·ssh 가 이미 있으므로 평문 프로토콜은 꺼도 관리에 지장이 없습니다. 켜 두면 안전한 경로를 만들어 둔 의미가 없어집니다.",cmds:["show management"],options:["telnet(23)·http(80) 가 활성화되어 있음", "https·ssh 만 활성화됨", "관리 접근 목록이 비어 있음", "로그인 배너가 없음"],evidence:["telnet(23)·http(80) 가 활성화되어 있음"],verdict:function(c){var p=(c.get('mgmt.protocols')||[]);return p.some(function(x){return x.enabled&&!x.encrypted;})?'vuln':'good';},fix:function(c){var p=c.get('mgmt.protocols')||[];p.forEach(function(x){if(!x.encrypted) x.enabled=false;});c.set('mgmt.protocols',p);var s=c.get('services')||[];s.forEach(function(x){if(x.name==='telnet'||x.name==='http') x.enabled=false;});c.set('services',s);},fixNote:"telnet 과 http 를 껐습니다. 관리는 ssh·https 로만 합니다."},
    {id:"ISS-021",expectRules:null,risk:5,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 원격 관리 접근 통제 여부",brief:"관리 화면에 <b>어디서든 접속할 수 있으면</b>, 계정 정보만 알아내면 끝입니다. 접속 가능한 출발지를 먼저 좁혀야 합니다.",where:"show management 의 Management access list",hint:"허용 목록이 비어 있을 때 장비가 어떻게 동작하는지 출력에 적혀 있습니다.",why:"관리 접근 목록이 비어 있어 모든 출발지에서 관리 접속을 시도할 수 있습니다. 관리 전용 대역(10.99.0.0/24)만 허용하면 계정이 유출돼도 접속 자체가 막힙니다.",cmds:["show management", "show interface"],options:["관리 접근 목록이 비어 있어 모든 출발지 허용", "관리 대역만 허용되어 있음", "telnet 이 켜져 있음", "mgmt 존이 10.99.0.1/24"],evidence:["관리 접근 목록이 비어 있어 모든 출발지 허용"],verdict:function(c){var a=c.get('mgmt.allowedIps')||[];return a.length?'good':'vuln';},fix:function(c){c.set('mgmt.allowedIps',['10.99.0.0/24','10.20.9.11/32']);},fixNote:"관리 대역과 보안관리자 PC 만 허용하도록 접근 목록을 넣었습니다."},
    {id:"ISS-022",expectRules:null,risk:3,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 접속성공/실패 로깅 여부",brief:"실패 기록이 없으면 <b>누가 대입을 시도했는지 알 수 없습니다</b>. 성공만 남기면 공격의 흔적이 아니라 결과만 남습니다.",where:"show logging 의 Login success / Login failure",hint:"두 줄을 각각 보세요. 하나만 켜져 있을 수 있습니다.",why:"로그인 성공은 기록하는데 실패가 꺼져 있습니다. 잠금 기능도 없는 상태라 대입 시도가 있어도 남는 흔적이 전혀 없습니다. 성공과 실패를 모두 남겨야 합니다.",cmds:["show logging", "show password-policy"],options:["로그인 실패 로깅이 꺼져 있음", "성공·실패 모두 기록 중", "설정 변경 로깅이 켜져 있음", "로컬 보관이 30일"],evidence:["로그인 실패 로깅이 꺼져 있음"],verdict:function(c){var g=c.get('logging')||{};return (g.loginSuccess&&g.loginFail)?'good':'vuln';},fix:function(c){c.set('logging.loginFail',true);},fixNote:"로그인 실패 로깅을 켰습니다."},
    {id:"ISS-024",expectRules:null,risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"세션 타임아웃 설정 여부",brief:"자리를 비운 사이 <b>열려 있는 관리 세션</b>은 옆사람에게도, 그 PC 를 잡은 공격자에게도 그대로 넘어갑니다. 내부 규정이 없으면 15분이 기준입니다.",where:"show session 의 TIMEOUT 열",hint:"판단기준에 예외가 하나 있습니다. 모니터링 계정은 세션 타임아웃 예외를 허용합니다.",why:"console 이 never, web 이 60분으로 기준(15분)을 넘습니다. <b>monitor 라인도 never 지만 이건 취약이 아닙니다</b> — 상시 관제 화면이 꺼지면 안 되므로 판단기준이 모니터링 계정을 예외로 두고 있습니다. 예외를 예외로 아는 것이 점검의 일부입니다.",cmds:["show session"],options:["console 이 never, web 이 60분으로 기준 초과", "모든 라인이 15분 이내", "monitor 라인이 never (모니터링 예외 대상)", "ssh 가 10분"],evidence:["console 이 never, web 이 60분으로 기준 초과"],verdict:function(c){var s=(c.get('auth.session.lines')||[]);return s.some(function(l){return l.name!=='monitor'&&(l.timeoutMin===0||l.timeoutMin>15);})?'vuln':'good';},fix:function(c){var s=c.get('auth.session.lines')||[];s.forEach(function(l){if(l.name!=='monitor'&&(l.timeoutMin===0||l.timeoutMin>15)) l.timeoutMin=10;});c.set('auth.session.lines',s);},fixNote:"console 과 web 세션을 10분으로 맞췄습니다. monitor 는 예외로 그대로 뒀습니다."},
    {id:"ISS-014",expectRules:null,risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"사용하지 않는 SNMP 비활성화 여부",brief:"SNMP 는 장비의 하드웨어·소프트웨어 정보를 그대로 알려 줍니다. <b>쓰지 않는데 켜져 있으면</b> 공격자에게 정찰 창구를 열어 둔 셈입니다.",where:"show snmp 의 agent 상태와 Purpose",hint:"이 항목이 묻는 것은 \"안전하게 쓰는가\"가 아니라 \"쓰지도 않는데 켜 뒀는가\"입니다.",why:"SNMP 가 켜져 있지만 <b>용도가 기록돼 있고 실제로 NMS 가 상시 사용 중</b>입니다. (nms 계정의 최근 접속이 오늘로 찍혀 있습니다.) 사용 중인 서비스를 켜 둔 것은 취약이 아닙니다. 설정이 안전한지는 다음 항목(ISS-015)에서 따로 봅니다. <b>같은 출력이라도 항목마다 묻는 것이 다릅니다.</b>",cmds:["show snmp", "show admin"],options:["SNMP 를 쓰지 않는데 켜져 있음", "SNMP 가 NMS 연동 용도로 실제 사용 중", "community 가 public", "SNMP 가 꺼져 있음"],evidence:["SNMP 가 NMS 연동 용도로 실제 사용 중"],verdict:function(c){var s=c.get('snmp')||{};if(!s.enabled) return 'good';return (s.purpose&&s.purpose.indexOf('미사용')<0)?'good':'vuln';},fix:null,fixNote:""},
    {id:"ISS-015",expectRules:null,risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"안전한 네트워크 모니터링 서비스 사용 여부",brief:"앞 항목에서 \"써야 하니까 켠 게 맞다\"까지 봤습니다. 이번엔 <b>그 설정이 안전한지</b>를 봅니다. v2c 는 community 문자열이 평문으로 오갑니다.",where:"show snmp 의 Version 과 Community",hint:"v3 를 쓸 수 있는데 v2c 를 쓰는지, community 가 초기값인지 두 가지를 보세요.",why:"v2c 를 쓰면서 community 가 초기값 public 입니다. 읽기 전용이어도 장비 정보가 그대로 넘어갑니다. v3 + AuthPriv 로 바꾸는 것이 원칙이고, 불가피하게 v2c 라면 최소한 유추 불가능한 문자열(복잡도 기준 충족)로 바꿔야 합니다.",cmds:["show snmp", "show version"],options:["v2c 를 쓰면서 community 가 초기값 public", "v3 AuthPriv 로 설정됨", "SNMP 가 실제 사용 중", "읽기 전용이라 안전함"],evidence:["v2c 를 쓰면서 community 가 초기값 public"],verdict:function(c){var s=c.get('snmp')||{};if(!s.enabled) return 'good';if(s.version==='v3') return (s.secLevel==='AuthPriv')?'good':'vuln';var weak=['public','private','manager','admin'];return weak.indexOf(String(s.community).toLowerCase())>=0?'vuln':(String(s.community).length>=10?'good':'vuln');},fix:function(c){c.set('snmp.version','v3');c.set('snmp.secLevel','AuthPriv');c.set('snmp.user','nmsmon');c.set('snmp.community','');},fixNote:"SNMP v3 로 올리고 보안수준을 AuthPriv(인증+암호화)로 설정했습니다."}
   ]}
  ]
};
