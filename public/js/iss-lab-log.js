/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */
window.ISS_LAB_DATA = {
  device: {"name": "fin-fw-01", "type": "FW", "typeLabel": "방화벽 (VPN 겸용)", "configDate": "2026-09-15 09:12:04 KST"},
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
    {id:"ISS-001",risk:4,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"보안장비 정책 및 로그 백업 설정 여부",brief:"장비가 죽었을 때 <b>정책을 다시 만들 수 있는가</b>가 복구 시간을 가릅니다. 백업이 없으면 몇 년치 정책을 기억으로 복원해야 합니다.",where:"show backup 의 Policy backup / Log backup / Last backup",hint:"백업 설정 여부와 마지막 백업 시각을 같이 보세요.",why:"정책·로그 백업이 모두 꺼져 있고 마지막 백업 기록도 없습니다(never). 장애가 나면 정책을 복원할 방법이 없습니다. 정기 백업을 걸고, 장비 밖에 보관해야 합니다.",cmds:["show backup"],options:["정책·로그 백업이 모두 비활성, 마지막 백업 기록 없음", "정책 백업이 주 1회 동작 중", "무결성 검사가 수행되지 않음", "백업 대상지가 원격 스토리지"],evidence:["정책·로그 백업이 모두 비활성, 마지막 백업 기록 없음"],verdict:function(c){var b=c.get('backup')||{};return (b.policy&&b.log)?'good':'vuln';},fix:function(c){c.set('backup.policy',true);c.set('backup.policyCycle','weekly');c.set('backup.log',true);c.set('backup.logCycle','daily');c.set('backup.last','2026-09-15 03:00');c.set('backup.dest','10.99.2.30:/backup/fw');},fixNote:"정책은 주 1회, 로그는 매일 원격 스토리지로 백업하도록 설정했습니다."},
    {id:"ISS-002",risk:3,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"원격 로그 서버 사용 여부",brief:"장비 안에만 로그가 있으면 <b>장비를 장악한 쪽이 로그도 지웁니다</b>. 저장 공간도 한정돼 있어 오래된 것부터 덮어써집니다.",where:"show logging 의 Remote log server",hint:"원격 전송 여부와 보관 기간을 같이 보세요. 판단기준은 1년 이상 보관입니다.",why:"원격 로그 서버가 설정돼 있지 않고 로컬 보관도 30일뿐입니다. 침해사고는 몇 달 뒤에 드러나는 일이 흔한데, 그때는 이미 로그가 남아 있지 않습니다. Syslog 등으로 밖에 보내고 1년 이상 보관해야 합니다.",cmds:["show logging"],options:["원격 로그 서버 미설정, 로컬 보관 30일", "Syslog 로 원격 전송 중", "로그인 실패 로깅이 꺼져 있음", "RAW 패킷 저장이 꺼져 있음"],evidence:["원격 로그 서버 미설정, 로컬 보관 30일"],verdict:function(c){var r=(c.get('logging.remote')||{});return (r.enabled&&r.retentionDays>=365)?'good':'vuln';},fix:function(c){c.set('logging.remote',{enabled:true,proto:'syslog-tls',host:'10.99.2.40',port:6514,retentionDays:365});},fixNote:"원격 Syslog(TLS) 로 전송하고 365일 보관하도록 설정했습니다."},
    {id:"ISS-025",risk:2,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"시간 동기화를 위한 NTP 설정",brief:"장비마다 시계가 다르면 <b>사고 순서를 맞출 수 없습니다</b>. 어느 장비 로그가 먼저인지 모르면 경로 추적이 불가능합니다.",where:"show ntp",hint:"NTP 가 켜져 있는지, 그리고 실제로 동기화된 상태인지 두 가지를 보세요.",why:"NTP 가 켜져 있고 서버와 <b>실제로 동기화된 상태(synchronized)</b>입니다. 설정만 있고 동기화가 안 된 경우(unsynchronized)가 흔한데 이 장비는 정상입니다. 켜져 있다는 것과 맞춰져 있다는 것은 다르므로 상태까지 확인해야 합니다.",cmds:["show ntp"],options:["NTP 가 꺼져 있고 로컬 시계를 씀", "NTP 가 켜져 있고 서버와 동기화된 상태", "서버가 stratum 3", "로그 보관이 30일"],evidence:["NTP 가 켜져 있고 서버와 동기화된 상태"],verdict:function(c){var n=c.get('ntp')||{};if(!n.enabled) return 'vuln';var s=n.servers||[];return s.some(function(x){return x.state==='synchronized';})?'good':'vuln';},fix:null,fixNote:""},
    {id:"ISS-026",risk:2,appliesTo:["FW", "VPN", "IDS", "IPS", "DDoS", "WAF"],title:"주요 파일에 대한 주기적인 무결성 검사 여부",brief:"설정 파일이 <b>몰래 바뀌어도 알 수 없다면</b>, 장비를 장악당한 뒤에도 정상으로 보입니다. 주기적으로 원본과 대조해야 합니다.",where:"show backup 의 Integrity check",hint:"이 기능을 지원하지 않는 장비라면 해당없음이지만, 이 장비는 항목이 출력에 있습니다.",why:"무결성 검사가 수행되지 않고 있습니다. 설정·로그 파일이 변조돼도 탐지되지 않습니다. 백업본과 주기적으로 대조하도록 설정해야 합니다.",cmds:["show backup"],options:["무결성 검사가 수행되지 않음", "주 1회 무결성 검사 수행 중", "정책 백업이 꺼져 있음", "마지막 백업이 never"],evidence:["무결성 검사가 수행되지 않음"],verdict:function(c){return c.get('backup.integrity')?'good':'vuln';},fix:function(c){c.set('backup.integrity',true);c.set('backup.integrityCycle','weekly');},fixNote:"주 1회 설정·주요 파일 무결성 검사를 걸었습니다."}
  ]
};
