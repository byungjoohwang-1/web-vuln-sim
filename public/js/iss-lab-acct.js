/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */
window.ISS_LAB_DATA = {
  units: [
  {device: {"name": "fin-fw-01", "type": "FW", "typeLabel": "방화벽 (VPN 겸용)", "configDate": "2026-09-15 09:12:04 KST"},
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
    {id:"ISS-017",risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 Default 계정 변경 여부",brief:"장비를 사 오면 들어 있는 <b>공장 출하 계정</b>은 모델명만 알면 누구나 압니다. 설명서와 벤더 사이트에 그대로 적혀 있습니다.",where:"show admin 의 Factory default account 줄",hint:"출하 계정이 아직 남아 있는지, 비밀번호는 바뀌었는지 두 가지를 같이 보세요.",why:"출하 계정 admin 이 이름 그대로 남아 있고 비밀번호도 바뀌지 않았습니다. 계정 이름을 바꾸거나 삭제하고, 관리자마다 자기 계정을 쓰게 해야 합니다.",cmds:["show admin"],options:["출하 계정 admin 이 이름·비밀번호 모두 그대로", "출하 계정이 삭제됨", "nms 계정이 readonly", "audit 계정이 2026-07-01 에 비밀번호 변경"],evidence:["출하 계정 admin 이 이름·비밀번호 모두 그대로"],verdict:function(c){var d=c.get('auth.defaultAccount')||{};return (d.present&&!d.passwordChanged)?'vuln':'good';},fix:function(c){c.set('auth.defaultAccount',{present:false,name:'admin',passwordChanged:true});var a=c.get('admins');c.set('admins',a.filter(function(u){return u.name!=='admin';}));},fixNote:"출하 계정 admin 을 삭제했습니다. 관리자는 각자 계정으로 접속합니다."},
    {id:"ISS-018",risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 Default 비밀번호 및 복잡도 기준",brief:"비밀번호 규칙이 느슨하면 <b>실패 제한이 없을 때</b> 대입 공격에 그대로 노출됩니다. 길이와 조합을 같이 봐야 합니다.",where:"show password-policy 의 min-length, complexity",hint:"판단기준은 영문·숫자·특수문자를 섞어 8자리 이상입니다.",why:"최소 길이가 6자이고 조합 규칙이 없습니다(none). 출하 비밀번호도 바뀌지 않은 상태라 두 가지가 겹쳐 있습니다. 8자리 이상 + 3종 조합으로 올려야 합니다.",cmds:["show password-policy", "show admin"],options:["최소 길이 6자, 조합 규칙 없음", "최소 길이 8자 이상 적용 중", "reuse-check 가 꺼져 있음", "잠금 임계값이 5회"],evidence:["최소 길이 6자, 조합 규칙 없음"],verdict:function(c){var p=c.get('auth.password')||{};return (p.minLength>=8&&p.complexity&&p.complexity!=='none')?'good':'vuln';},fix:function(c){c.set('auth.password.minLength',9);c.set('auth.password.complexity','alpha+digit+special');c.set('auth.defaultAccount.passwordChanged',true);},fixNote:"최소 9자 + 영문·숫자·특수문자 조합으로 바꿨습니다."},
    {id:"ISS-019",risk:5,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 계정 관리 적정성",brief:"여러 사람이 <b>같은 계정 하나</b>로 접속하면, 사고가 났을 때 누가 했는지 로그로 가릴 수 없습니다. 감사증적이 사실상 사라집니다.",where:"show admin 의 SHARED 열",hint:"공용으로 표시된 계정이 몇 개인지 세어 보세요.",why:"admin 과 fw_ops 두 계정을 여러 관리자가 공용으로 씁니다. 개인별 계정을 주는 것이 원칙이고, 공동 사용이 불가피하면 개인별 사용내역을 따로 기록·관리해야 합니다.",cmds:["show admin"],options:["admin·fw_ops 를 여러 관리자가 공용으로 사용", "모든 계정이 개인별로 분리됨", "audit 계정의 권한이 super", "nms 계정의 최근 접속이 오늘"],evidence:["admin·fw_ops 를 여러 관리자가 공용으로 사용"],verdict:function(c){var a=c.get('admins')||[];return a.some(function(u){return u.shared;})?'vuln':'good';},fix:function(c){var a=c.get('admins')||[];var out=a.filter(function(u){return u.name!=='admin'&&u.name!=='fw_ops';});out.unshift({name:'park.fw',role:'super',shared:false,lastLogin:'2026-09-15 08:41:12',pwChanged:'2026-09-15'});out.unshift({name:'kim.fw',role:'super',shared:false,lastLogin:'2026-09-15 07:55:30',pwChanged:'2026-09-15'});c.set('admins',out);c.set('auth.defaultAccount',{present:false,name:'admin',passwordChanged:true});},fixNote:"공용 계정을 없애고 관리자 개인 계정(kim.fw, park.fw)으로 나눴습니다."},
    {id:"ISS-020",risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 계정별 권한 설정 여부",brief:"모두에게 최고 권한을 주면 <b>실수 한 번이 곧 정책 변경</b>이 됩니다. 보는 일만 하는 계정에는 보는 권한만 줍니다.",where:"show admin 의 ROLE 열",hint:"계정의 용도(이름)와 부여된 권한이 맞는지 하나씩 대조해 보세요.",why:"감사 용도인 audit 계정에 super 권한이 있습니다. 감사자는 설정을 읽을 수만 있으면 되므로 readonly 로 충분합니다. 권한이 넓을수록 그 계정이 탈취됐을 때 잃는 것이 많습니다.",cmds:["show admin"],options:["audit 계정에 super 권한이 부여됨", "모든 계정 권한이 용도에 맞음", "nms 계정이 readonly", "admin 계정이 공용"],evidence:["audit 계정에 super 권한이 부여됨"],verdict:function(c){var a=c.get('admins')||[];return a.some(function(u){return u.name==='audit'&&u.role!=='readonly';})?'vuln':'good';},fix:function(c){var a=c.get('admins')||[];a.forEach(function(u){if(u.name==='audit') u.role='readonly';});c.set('admins',a);},fixNote:"audit 계정을 readonly 로 낮췄습니다."},
    {id:"ISS-023",risk:3,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"로그인 실패횟수 제한 설정 여부",brief:"실패 제한이 없으면 자동화 도구가 <b>시간만 들이면 계속 시도</b>할 수 있습니다. 비밀번호를 아무리 길게 해도 무제한 시도 앞에서는 시간문제입니다.",where:"show password-policy 의 lockout",hint:"판단기준은 5회 이내입니다.",why:"계정 잠금이 꺼져 있어 실패 횟수 제한이 걸리지 않습니다. 최소 길이 6자 규칙과 겹쳐서 대입 공격의 성공 가능성이 크게 올라갑니다. 5회 이내로 잠그도록 설정해야 합니다.",cmds:["show password-policy"],options:["계정 잠금이 비활성화 상태", "잠금 임계값 5회로 설정됨", "최소 길이가 6자", "max-age 가 0"],evidence:["계정 잠금이 비활성화 상태"],verdict:function(c){var l=c.get('auth.lockout')||{};return (l.enabled&&l.threshold>0&&l.threshold<=5)?'good':'vuln';},fix:function(c){c.set('auth.lockout',{enabled:true,threshold:5,durationMin:10});},fixNote:"5회 실패 시 10분간 잠기도록 설정했습니다."},
    {id:"ISS-040",risk:3,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 비밀번호의 주기적인 변경 여부",brief:"비밀번호를 한 번 만들고 <b>몇 년째 그대로</b>면, 어디선가 유출됐어도 계속 유효합니다. 유출을 눈치채지 못한 기간만큼 악용 기간이 됩니다.",where:"show password-policy 의 max-age, show admin 의 PW-CHANGED 열",hint:"만료 정책과 실제 마지막 변경일을 같이 보세요. 판단기준은 분기별 1회 이상입니다.",why:"max-age 가 0 이라 만료가 없고, admin 은 2023-11-02 이후 3년 가까이 그대로입니다. 정책값만 바꾸면 되는 게 아니라 <b>이미 오래된 비밀번호는 따로 재설정</b>해야 합니다.",cmds:["show password-policy", "show admin"],options:["만료 정책이 없고(max-age 0) admin 이 2023-11-02 이후 미변경", "90일 만료가 적용 중", "audit 계정이 2026-07-01 에 변경함", "잠금 기능이 꺼져 있음"],evidence:["만료 정책이 없고(max-age 0) admin 이 2023-11-02 이후 미변경"],verdict:function(c){var p=c.get('auth.password')||{};if(!(p.maxAgeDays>0&&p.maxAgeDays<=90)) return 'vuln';var a=c.get('admins')||[];return a.some(function(u){return u.pwChanged<'2026-06-15';})?'vuln':'good';},fix:function(c){c.set('auth.password.maxAgeDays',90);c.set('auth.password.reuseCheck',true);var a=c.get('admins')||[];a.forEach(function(u){if(u.pwChanged<'2026-06-15') u.pwChanged='2026-09-15';});c.set('admins',a);},fixNote:"90일 만료를 적용하고, 오래된 계정의 비밀번호를 재설정했습니다."}
   ]}
  ]
};
