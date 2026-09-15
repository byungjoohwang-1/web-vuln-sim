/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */
window.ISS_LAB_DATA = {
  units: [
  {device: {"name": "fin-ips-01", "type": "IPS", "typeLabel": "침입방지시스템", "configDate": "2026-09-15 10:02:11 KST"},
   cfg: {
 "system": {
  "model": "SENTRA IP-900",
  "serial": "IP90-2405-7723",
  "os": "SentraOS-IPS 6.8.3",
  "build": "6.8.3-b3390",
  "role": "Intrusion Prevention",
  "uptime": "187 days 09:14",
  "eosDate": "2029-05-31",
  "eosPassed": false,
  "sigVersion": "2026.09.12-1180",
  "sigDate": "2026-09-12"
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
  "loginFail": true,
  "configChange": true,
  "rawPacket": false,
  "rawPacketSeverity": 0,
  "retentionDays": 90,
  "remote": {
   "enabled": true,
   "proto": "syslog-tls",
   "host": "10.99.2.40",
   "port": 6514,
   "retentionDays": 365
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
  "groups": [
   {
    "name": "TCP SYN Flooding",
    "enabled": false,
    "action": "-"
   },
   {
    "name": "UDP Flooding",
    "enabled": false,
    "action": "-"
   },
   {
    "name": "ICMP Flooding",
    "enabled": false,
    "action": "-"
   },
   {
    "name": "Port Scan",
    "enabled": true,
    "action": "block"
   },
   {
    "name": "Known Hacking Tool",
    "enabled": true,
    "action": "alert"
   },
   {
    "name": "Web Exploit",
    "enabled": true,
    "action": "block"
   },
   {
    "name": "Malware C2",
    "enabled": true,
    "action": "block"
   }
  ],
  "blockMode": "inline-block",
  "hwBypass": false,
  "blocks30d": 1840
 },
 "monitor": {
  "cpu": 44,
  "memory": 57,
  "sessions": 132400,
  "sessionMax": 400000,
  "usageReview": true,
  "usageReviewCycle": "monthly",
  "realtime": true,
  "alerting": [
   "email(관제팀)",
   "SNMP trap"
  ],
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
    {id:"ISS-010",risk:2,appliesTo:["IDS", "IPS", "DDoS"],title:"TCP/UDP/ICMP 탐지/차단 패턴 적용 여부",brief:"플러딩 공격은 <b>패턴이 단순한 대신 양으로</b> 밀어붙입니다. 탐지 패턴을 꺼 두면 장비가 있어도 그대로 통과합니다.",where:"show signature 의 PATTERN GROUP — Flooding 계열",hint:"세 가지(TCP·UDP·ICMP)를 각각 보세요. 하나만 켜져 있을 수도 있습니다.",why:"TCP SYN·UDP·ICMP Flooding 패턴이 셋 다 꺼져 있습니다. 인터넷 인입 구간에 있는 장비에서 이 패턴이 꺼져 있으면 대량 트래픽 공격이 내부 서버까지 그대로 도달합니다.",cmds:["show signature"],options:["TCP·UDP·ICMP Flooding 패턴이 모두 비활성", "세 패턴 모두 차단으로 동작 중", "Port Scan 패턴이 켜져 있음", "해킹 툴 패턴이 alert 동작"],evidence:["TCP·UDP·ICMP Flooding 패턴이 모두 비활성"],verdict:function(c){var g=(c.get('detect.groups')||[]);return g.some(function(x){return /Flooding/i.test(x.name)&&!x.enabled;})?'vuln':'good';},fix:function(c){var g=c.get('detect.groups')||[];g.forEach(function(x){if(/Flooding/i.test(x.name)){x.enabled=true;x.action='block';}});c.set('detect.groups',g);},fixNote:"TCP·UDP·ICMP Flooding 패턴을 켜고 차단으로 설정했습니다."},
    {id:"ISS-011",risk:2,appliesTo:["IDS", "IPS", "DDoS"],title:"Port Scan 탐지/차단 패턴 적용 여부",brief:"포트 스캔은 공격의 <b>정찰 단계</b>입니다. 여기서 막으면 그다음이 오지 않습니다.",where:"show signature 의 Port Scan 항목",hint:"켜져 있는지와 동작(ACTION)이 무엇인지를 같이 보세요.",why:"Port Scan 패턴이 켜져 있고 동작도 block 입니다. <b>이 항목은 양호</b>입니다. 앞 항목(Flooding)이 취약하다고 해서 같은 화면의 다른 패턴까지 취약인 것은 아닙니다. 항목마다 무엇을 묻는지 보고 해당하는 줄만 봐야 합니다.",cmds:["show signature"],options:["Port Scan 패턴이 비활성 상태", "Port Scan 패턴이 활성이고 차단(block)으로 동작", "Flooding 패턴이 꺼져 있음", "차단 모드가 inline-block"],evidence:["Port Scan 패턴이 활성이고 차단(block)으로 동작"],verdict:function(c){var g=(c.get('detect.groups')||[]);var p=g.filter(function(x){return /Port Scan/i.test(x.name);})[0];return (p&&p.enabled&&p.action==='block')?'good':'vuln';},fix:null,fixNote:""},
    {id:"ISS-012",risk:2,appliesTo:["IDS", "IPS", "WAF"],title:"해킹 툴 탐지/차단 패턴 적용 여부",brief:"탐지만 하고 <b>차단하지 않으면</b> 로그만 쌓입니다. 아무도 실시간으로 보지 않는다면 공격은 그대로 성공합니다.",where:"show signature 의 ACTION 열",hint:"판단기준은 \"탐지 <b>및</b> 차단\"입니다. 켜져 있다고 끝이 아닙니다.",why:"Known Hacking Tool 패턴이 켜져 있지만 동작이 alert(알림)뿐입니다. 다른 패턴들은 block 인데 이것만 alert 입니다. 오탐이 걱정돼 알림만 걸어 두고 그대로 둔 전형적인 경우입니다. 판단기준은 탐지와 차단을 모두 요구합니다.",cmds:["show signature"],options:["해킹 툴 패턴이 alert 로만 동작하고 차단하지 않음", "해킹 툴 패턴이 차단으로 동작 중", "해킹 툴 패턴이 비활성", "Web Exploit 패턴이 block"],evidence:["해킹 툴 패턴이 alert 로만 동작하고 차단하지 않음"],verdict:function(c){var g=(c.get('detect.groups')||[]);var p=g.filter(function(x){return /Hacking Tool/i.test(x.name);})[0];return (p&&p.enabled&&p.action==='block')?'good':'vuln';},fix:function(c){var g=c.get('detect.groups')||[];g.forEach(function(x){if(/Hacking Tool/i.test(x.name)){x.enabled=true;x.action='block';}});c.set('detect.groups',g);},fixNote:"해킹 툴 패턴을 차단(block)으로 바꿨습니다."},
    {id:"ISS-009",risk:2,appliesTo:["IDS", "IPS", "DDoS", "WAF"],title:"위험도가 높은 이벤트 및 로그에 대한 RAW 패킷 저장 여부",brief:"\"탐지됐다\"는 기록만 있고 <b>실제 패킷이 없으면</b> 사고 분석 때 무엇이 오갔는지 되짚을 수 없습니다.",where:"show logging 의 Raw packet capture",hint:"전부 저장할 필요는 없습니다. 위험도 높은 이벤트(보통 4~5단계)만 저장하면 됩니다.",why:"RAW 패킷 저장이 꺼져 있습니다. 탐지 이벤트는 남지만 페이로드가 없어 무엇이 실제로 전송됐는지 확인할 수 없습니다. 장비에 기능이 없다면 트래픽 분석기 같은 대체 수단이 있는지 확인해야 합니다.",cmds:["show logging"],options:["RAW 패킷 저장이 비활성 상태", "위험도 4 이상 RAW 패킷을 저장 중", "원격 로그 서버가 연동됨", "로컬 보관이 90일"],evidence:["RAW 패킷 저장이 비활성 상태"],verdict:function(c){var g=c.get('logging')||{};return (g.rawPacket&&g.rawPacketSeverity>=1)?'good':'vuln';},fix:function(c){c.set('logging.rawPacket',true);c.set('logging.rawPacketSeverity',4);},fixNote:"위험도 4 이상 이벤트의 RAW 패킷을 저장하도록 설정했습니다."},
    {id:"ISS-008",risk:3,appliesTo:["IDS", "IPS", "DDoS", "WAF"],title:"탐지된 이벤트 및 로그에 대한 정기적 분석 및 보고 여부",brief:"탐지는 자동이지만 <b>분석은 사람이 합니다</b>. 보는 사람이 없으면 침해 흔적이 로그 안에서 그냥 지나갑니다.",where:"show resource 의 Event/log review",hint:"실시간 모니터링(알림)과 정기 분석·보고는 다른 것입니다. 둘 다 있는지 보세요.",why:"실시간 모니터링과 알림은 설정돼 있는데 <b>이벤트·로그의 정기 분석·보고는 없습니다</b>. 알림은 임계치를 넘은 건만 알려 줄 뿐, 추세나 반복되는 저강도 시도는 주기적으로 모아서 봐야 드러납니다. 관제보고서 같은 형태로 남아야 합니다.",cmds:["show resource", "show logging"],options:["실시간 알림은 있으나 이벤트·로그 정기 분석·보고가 없음", "주간 단위로 분석·보고 중", "실시간 모니터링이 꺼져 있음", "RAW 패킷 저장이 꺼져 있음"],evidence:["실시간 알림은 있으나 이벤트·로그 정기 분석·보고가 없음"],verdict:function(c){return c.get('monitor.logReview')?'good':'vuln';},fix:function(c){c.set('monitor.logReview',true);c.set('monitor.logReviewCycle','weekly (관제보고서) + monthly (추세분석)');},fixNote:"주간 관제보고서와 월간 추세분석 절차를 세웠습니다."}
   ]},
  {device: {"name": "fin-waf-01", "type": "WAF", "typeLabel": "웹방화벽", "configDate": "2026-09-15 10:05:40 KST"},
   cfg: {
 "system": {
  "model": "SENTRA WA-300",
  "serial": "WA30-2502-1166",
  "os": "SentraOS-WAF 4.2.7",
  "build": "4.2.7-b1102",
  "role": "Web Application Firewall",
  "uptime": "62 days 11:38",
  "eosDate": "2030-02-28",
  "eosPassed": false,
  "sigVersion": "2026.09.14-0440",
  "sigDate": "2026-09-14"
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
  "loginFail": true,
  "configChange": true,
  "rawPacket": false,
  "rawPacketSeverity": 0,
  "retentionDays": 90,
  "remote": {
   "enabled": true,
   "proto": "syslog-tls",
   "host": "10.99.2.40",
   "port": 6514,
   "retentionDays": 365
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
  "groups": [
   {
    "name": "SQL Injection",
    "enabled": true,
    "action": "detect-only"
   },
   {
    "name": "Cross-Site Script",
    "enabled": true,
    "action": "detect-only"
   },
   {
    "name": "Path Traversal",
    "enabled": true,
    "action": "detect-only"
   },
   {
    "name": "Known Hacking Tool",
    "enabled": true,
    "action": "detect-only"
   }
  ],
  "blockMode": "detect-only",
  "hwBypass": true,
  "blocks30d": 0
 },
 "monitor": {
  "cpu": 44,
  "memory": 57,
  "sessions": 132400,
  "sessionMax": 400000,
  "usageReview": true,
  "usageReviewCycle": "monthly",
  "realtime": true,
  "alerting": [
   "email(관제팀)",
   "SNMP trap"
  ],
  "logReview": true,
  "logReviewCycle": "weekly"
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
    {id:"ISS-042",risk:5,appliesTo:["WAF"],title:"차단 기능 활성화 여부",brief:"보안장비를 <b>탐지 전용으로 돌려 두는</b> 경우가 많습니다. 오탐으로 서비스가 끊길까 봐서인데, 그 상태에서는 공격을 보기만 합니다.",where:"show signature 의 Blocking mode, Hardware bypass, Blocks last 30d",hint:"세 가지를 같이 보세요. 최근 30일 차단 건수가 0 이면 실제로 막은 적이 없다는 뜻입니다.",why:"차단 모드가 detect-only 이고 하드웨어 바이패스까지 켜져 있으며, 최근 30일 차단 건수가 0 입니다. 패턴은 전부 켜져 있지만 동작이 detect-only 라 <b>탐지만 하고 통과시킵니다</b>. 장비를 사 놓고 끄고 쓰는 것과 같습니다. 실제 평가에서는 차단 로그가 있는지를 먼저 확인합니다.",cmds:["show signature"],options:["차단 모드가 detect-only, 바이패스 켜짐, 30일 차단 0건", "인라인 차단으로 동작 중", "패턴이 모두 비활성", "시그니처가 2026-09-14 로 최신"],evidence:["차단 모드가 detect-only, 바이패스 켜짐, 30일 차단 0건"],verdict:function(c){var d=c.get('detect')||{};return (d.blockMode&&d.blockMode.indexOf('block')>=0&&!d.hwBypass)?'good':'vuln';},fix:function(c){c.set('detect.blockMode','inline-block');c.set('detect.hwBypass',false);var g=c.get('detect.groups')||[];g.forEach(function(x){x.action='block';});c.set('detect.groups',g);c.set('detect.blocks30d',0);},fixNote:"인라인 차단으로 전환하고 바이패스를 껐습니다. (오탐은 예외 정책으로 관리)"}
   ]}
  ]
};
