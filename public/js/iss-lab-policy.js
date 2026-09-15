/* 생성물 — _gen/gen_iss_lab.py 가 만든다. 직접 고치지 말 것. */
window.ISS_LAB_DATA = {
  units: [
  {device: {"name": "fin-fw-02", "type": "FW", "typeLabel": "방화벽 (내부망 경계)", "configDate": "2026-09-15 09:41:55 KST"},
   neverFlagged: [1, 3],
   cfg: {
 "system": {
  "model": "SENTRA SG-6300",
  "serial": "SG63-2312-4417",
  "os": "SentraOS 7.4.0",
  "build": "7.4.0-b5102",
  "role": "Firewall (internal boundary)",
  "uptime": "221 days 03:47",
  "eosDate": "2030-09-30",
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
 "rules": [
  {
   "srcZone": "trust",
   "src": "10.20.0.0/16",
   "dstZone": "dmz",
   "dst": "10.30.0.21",
   "sport": "any",
   "svc": "TCP/443",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 882134,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "trust",
   "src": "10.20.0.0/16",
   "dstZone": "srv",
   "dst": "10.40.0.0/16",
   "sport": "any",
   "svc": "TCP/22,3389,1433",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 4120,
   "lastHit": "2026-09-14"
  },
  {
   "srcZone": "untrust",
   "src": "ANY",
   "dstZone": "dmz",
   "dst": "10.30.0.0/24",
   "sport": "any",
   "svc": "TCP/80,443",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 220140,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "untrust",
   "src": "198.51.100.0/24",
   "dstZone": "dmz",
   "dst": "10.30.0.0/24",
   "sport": "any",
   "svc": "ALL",
   "action": "deny",
   "log": true,
   "bidir": false,
   "hits": 0,
   "lastHit": "never"
  },
  {
   "srcZone": "trust",
   "src": "10.20.4.55",
   "dstZone": "srv",
   "dst": "10.40.2.10",
   "sport": "any",
   "svc": "TCP/1024-65535",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 77012,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "trust",
   "src": "10.20.6.0/24",
   "dstZone": "srv",
   "dst": "10.40.6.0/24",
   "sport": "any",
   "svc": "TCP/1521",
   "action": "permit",
   "log": true,
   "bidir": true,
   "hits": 9921,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "untrust",
   "src": "ANY",
   "dstZone": "trust",
   "dst": "10.20.0.0/16",
   "sport": "TCP/53",
   "svc": "TCP/8080",
   "action": "permit",
   "log": false,
   "bidir": false,
   "hits": 3301,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "trust",
   "src": "10.20.8.0/24",
   "dstZone": "srv",
   "dst": "10.40.8.10",
   "sport": "any",
   "svc": "TCP/512-514,UDP/69",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 340,
   "lastHit": "2026-09-10"
  },
  {
   "srcZone": "trust",
   "src": "10.20.9.0/24",
   "dstZone": "srv",
   "dst": "10.40.9.0/24",
   "sport": "any",
   "svc": "TCP/8080",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 0,
   "lastHit": "2025-11-20"
  },
  {
   "srcZone": "srv",
   "src": "10.40.2.10",
   "dstZone": "srv",
   "dst": "10.40.3.20",
   "sport": "any",
   "svc": "TCP/22",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 88,
   "lastHit": "2026-09-13"
  },
  {
   "srcZone": "user",
   "src": "10.20.30.0/24",
   "dstZone": "srv",
   "dst": "10.40.0.0/16",
   "sport": "any",
   "svc": "TCP/3389",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 4400,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "trust",
   "src": "10.20.0.0/16",
   "dstZone": "ext",
   "dst": "10.50.0.0/16",
   "sport": "any",
   "svc": "TCP/8443",
   "action": "permit",
   "log": true,
   "bidir": false,
   "hits": 2210,
   "lastHit": "2026-09-15"
  },
  {
   "srcZone": "any",
   "src": "ANY",
   "dstZone": "any",
   "dst": "ANY",
   "sport": "any",
   "svc": "ALL",
   "action": "permit",
   "log": false,
   "bidir": false,
   "hits": 512900,
   "lastHit": "2026-09-15"
  }
 ],
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
 },
 "zoneNote": "untrust=외부  dmz=공개서버  trust=내부 업무  user=사용자 단말  srv=서버팜  ext=대외계  mgmt=관리 (접근통제시스템 10.99.1.10)"
},
   missions: [
    {id:"ISS-030",expectRules:[13],risk:5,appliesTo:["FW", "VPN"],title:"모든 목적지 및 서비스로의 허용 정책 금지 여부",brief:"출발지·목적지·서비스가 전부 ANY 인 룰 하나면 <b>방화벽이 사실상 없는 것</b>과 같습니다. 아래쪽에 있어도 그 위에서 막히지 않은 것은 전부 통과합니다.",where:"show policy — SOURCE·DESTINATION 이 ANY 이고 SERVICE 가 ALL 인 줄",hint:"기본 정책이 deny 여도, 그보다 위에 있는 전체 허용 룰이 먼저 걸립니다.",why:"맨 아래 룰이 ANY→ANY / ALL / permit 입니다. 히트 수가 51만이 넘는다는 것은 <b>다른 룰에서 처리되지 않은 트래픽이 전부 이 룰로 통과하고 있다</b>는 뜻입니다. 기본 정책 deny 는 이 룰 뒤에 있으므로 아무 역할을 못 합니다.",cmds:["show policy"],options:["ANY→ANY / ALL 을 허용하는 룰이 존재 (히트 51만)", "기본 정책이 deny 라 안전함", "공개 웹 허용 룰이 ANY 출발지", "로그가 꺼진 룰이 있음"],evidence:["ANY→ANY / ALL 을 허용하는 룰이 존재 (히트 51만)"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst)&&P.svcIsAll(x.svc);})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];c.set('rules', r.filter(function(x){return !(x.action==='permit'&&P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst)&&P.svcIsAll(x.svc));}));},fixNote:"전체 허용 룰을 삭제했습니다. 이제 기본 정책 deny 가 실제로 동작합니다."},
    {id:"ISS-031",expectRules:[2, 6, 8, 11],risk:5,appliesTo:["FW", "VPN"],title:"취약한 서비스의 네트워크 대역 단위 허용 금지 여부",brief:"관리용 포트를 <b>대역 단위로</b> 열면, 그 대역 안의 아무 장비나 서버 관리 포트에 닿습니다. 한 대만 뚫려도 전부에 닿습니다.",where:"show policy — 관리 포트(22·3389·1433·1521·512-514 등)를 쓰면서 주소가 대역/ANY 인 줄",hint:"이 항목은 <b>주소 범위</b>만 봅니다. 방향이나 서비스 종류는 다른 항목이 봅니다. 해당하는 줄이 하나가 아닙니다.",why:"관리 포트를 열면서 출발지나 목적지가 대역인 룰이 4개 있습니다(22·3389·1433 / 1521 / 512-514·69 / 3389). 관리 접속은 <b>지정한 단말에서 지정한 서버로</b>만 열어야 합니다. 대역으로 열어 두면 그 안의 감염된 PC 한 대가 서버팜 전체의 관리 포트에 닿습니다.",cmds:["show policy"],options:["관리 포트를 열면서 주소가 대역/ANY 인 룰이 여러 개 존재", "관리 포트 룰이 모두 단일 호스트로 지정됨", "기본 정책이 deny", "공개 웹 룰의 출발지가 ANY"],evidence:["관리 포트를 열면서 주소가 대역/ANY 인 룰이 여러 개 존재"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&P.svcHasMgmtPort(x.svc)&&!(P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst))&&(P.addrIsBroad(x.src)||P.addrIsBroad(x.dst));})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var H={"trust": "10.20.4.55", "srv": "10.40.2.10", "user": "10.20.30.41", "untrust": "203.0.113.60", "ext": "10.50.1.20", "dmz": "10.30.0.21"};var r=c.get('rules')||[];r.forEach(function(x){if(x.action==='permit'&&P.svcHasMgmtPort(x.svc)&&!(P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst))&&(P.addrIsBroad(x.src)||P.addrIsBroad(x.dst))){x.src=P.narrowAddr(x.src,H[x.srcZone]||'10.20.4.55');x.dst=P.narrowAddr(x.dst,H[x.dstZone]||'10.40.2.10');}});c.set('rules',r);},fixNote:"관리 포트를 여는 룰의 출발지·목적지를 지정 호스트로 좁혔습니다."},
    {id:"ISS-032",expectRules:[5],risk:5,appliesTo:["FW", "VPN"],title:"서비스 포트 허용 정책 적정성",brief:"<code>1024-65535</code> 같은 범위 허용은 <b>사실상 전부 허용</b>입니다. 포트를 적어 놨을 뿐 좁힌 게 아닙니다.",where:"show policy 의 SERVICE 열 — ALL, TCP ALL, 1024-65535 같은 범위",hint:"이 항목은 <b>서비스 범위</b>만 봅니다. 전체 허용(ANY→ANY/ALL)은 앞 항목이 따로 봅니다.",why:"내부 배치서버(10.20.4.55)에서 서버팜으로 TCP/1024-65535 를 열어 뒀습니다. 범위 하나에 DB·RDP·관리 포트가 전부 들어갑니다. 실제로 쓰는 포트만 적어야 합니다. \"어떤 포트를 쓰는지 모르겠어서 범위로 열었다\"가 이런 룰이 생기는 전형적인 경로입니다.",cmds:["show policy"],options:["TCP/1024-65535 처럼 과도한 범위를 허용한 룰이 존재", "모든 룰이 필요한 포트만 지정", "ANY→ANY 허용 룰이 존재", "r-계열 서비스가 허용됨"],evidence:["TCP/1024-65535 처럼 과도한 범위를 허용한 룰이 존재"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&P.svcIsBroad(x.svc)&&!(P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst));})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];r.forEach(function(x){if(x.action==='permit'&&P.svcIsBroad(x.svc)&&!(P.addrIsCatchAll(x.src)&&P.addrIsCatchAll(x.dst))) x.svc='TCP/8081';});c.set('rules',r);},fixNote:"범위 허용을 실제 사용 포트(TCP/8081)로 좁혔습니다."},
    {id:"ISS-033",expectRules:[6],risk:4,appliesTo:["FW", "VPN"],title:"불필요한 양방향 정책 금지 여부",brief:"양방향으로 열면 <b>서버가 단말로 먼저 접속하는 것도</b> 허용됩니다. 서버가 장악됐을 때 내부로 돌아 나오는 길이 됩니다.",where:"show policy 의 DIR 열 — both 인 줄",hint:"이 항목은 <b>방향</b>만 봅니다. 주소가 대역인지는 다른 항목이 봅니다.",why:"DB 포트(TCP/1521)가 양방향으로 열려 있습니다. 업무상 필요한 것은 단말→DB 한 방향입니다. DB 서버가 내부 단말로 먼저 접속할 일은 없습니다. 관리용·DB 접속용 포트는 특히 양방향으로 열려 있지 않은지 중점적으로 봐야 합니다.",cmds:["show policy"],options:["DB 포트(TCP/1521)가 양방향(both)으로 허용됨", "모든 룰이 단방향", "해당 룰의 주소가 대역 단위", "해당 룰의 로그가 켜져 있음"],evidence:["DB 포트(TCP/1521)가 양방향(both)으로 허용됨"],verdict:function(c){var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&x.bidir;})?'vuln':'good';},fix:function(c){var r=c.get('rules')||[];r.forEach(function(x){if(x.bidir) x.bidir=false;});c.set('rules',r);},fixNote:"양방향 설정을 단방향으로 바꿨습니다."},
    {id:"ISS-034",expectRules:[3, 4],risk:4,appliesTo:["FW", "VPN"],title:"정책 적용 순서의 적절성",brief:"방화벽은 <b>위에서부터 먼저 걸리는 룰</b>을 씁니다. 차단 정책이 허용 정책 아래에 있으면 설정은 있는데 동작하지 않습니다.",where:"show policy — deny 룰의 위치와 HITS",hint:"차단 룰인데 히트가 0 이고 LAST-HIT 이 never 라면, 그 위 어딘가에서 이미 허용되고 있습니다.",why:"유해 IP 대역(198.51.100.0/24) 차단 룰이 <b>공개 웹 허용 룰 바로 아래</b>에 있습니다. 그 허용 룰이 같은 목적지를 ANY 출발지로 먼저 허용하므로 차단 룰까지 오지 않습니다. 히트 0 / never 가 그 증거입니다. 차단 정책은 허용 정책보다 위에 있어야 합니다.",cmds:["show policy"],options:["차단 룰이 같은 목적지의 허용 룰 아래에 있어 히트 0 / never", "차단 룰이 맨 위에 있음", "차단 룰의 서비스가 ALL", "기본 정책이 deny"],evidence:["차단 룰이 같은 목적지의 허용 룰 아래에 있어 히트 0 / never"],verdict:function(c){var r=c.get('rules')||[];return r.some(function(x,i){return x.action==='deny'&&x.hits===0&&x.lastHit==='never'&&r.slice(0,i).some(function(p){return p.action==='permit'&&p.dst===x.dst;});})?'vuln':'good';},fix:function(c){var r=(c.get('rules')||[]).slice();for(var i=0;i<r.length;i++){var x=r[i];if(!(x.action==='deny'&&x.hits===0&&x.lastHit==='never')) continue;var j=-1;for(var k=0;k<i;k++){if(r[k].action==='permit'&&r[k].dst===x.dst){j=k;break;}}if(j<0) continue;r.splice(i,1);r.splice(j,0,x);i=j;}c.set('rules',r);},fixNote:"차단 룰을 같은 목적지의 허용 룰보다 위로 올렸습니다."},
    {id:"ISS-035",expectRules:[7],risk:5,appliesTo:["FW", "VPN"],title:"출발지 포트 기반의 정책 금지 여부",brief:"출발지 포트는 <b>보내는 쪽이 마음대로 정합니다</b>. 그걸 신뢰 근거로 쓰면 공격자가 그 번호를 그대로 흉내 내 통과합니다.",where:"show policy 의 SPORT 열 — any 가 아닌 줄",hint:"출발지 포트를 53(DNS)으로 맞춰 보내는 것은 공격자에게 아무 제약이 아닙니다.",why:"출발지 포트 TCP/53 을 조건으로 외부에서 내부 대역으로 허용하고 있습니다. 공격자가 자기 출발지 포트를 53 으로 지정하면 그대로 통과합니다. 게다가 이 룰은 <b>로그도 꺼져 있어</b> 통과한 기록조차 남지 않습니다.",cmds:["show policy"],options:["출발지 포트(TCP/53)를 조건으로 허용하는 룰이 존재", "모든 룰의 출발지 포트가 any", "해당 룰의 목적지가 내부 대역", "기본 정책이 deny"],evidence:["출발지 포트(TCP/53)를 조건으로 허용하는 룰이 존재"],verdict:function(c){var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&x.sport&&x.sport!=='any';})?'vuln':'good';},fix:function(c){var r=c.get('rules')||[];r.forEach(function(x){if(x.sport&&x.sport!=='any'){x.sport='any';x.log=true;}});c.set('rules',r);},fixNote:"출발지 포트 조건을 없애고 해당 룰의 로그를 켰습니다."},
    {id:"ISS-036",expectRules:[8],risk:5,appliesTo:["FW", "VPN"],title:"취약한 원격 서비스 금지 여부",brief:"r-계열(512-514)과 TFTP(69)는 <b>비밀번호 없이</b> 접속하거나 파일을 가져갈 수 있게 설계된 옛 프로토콜입니다.",where:"show policy 의 SERVICE — TCP/512-514, UDP/69, TCP/21·23",hint:"이 항목은 <b>서비스의 종류</b>를 봅니다. 포트 개수가 적다고 안전한 게 아닙니다.",why:"r-계열(rsh/rlogin/rexec, TCP 512-514)과 TFTP(UDP 69)가 허용돼 있고 <b>최근까지 실제로 쓰이고 있습니다</b>(마지막 히트 2026-09-10). r-계열은 신뢰 호스트 목록만으로 인증을 건너뛰고, TFTP 는 인증 자체가 없습니다. SSH·SFTP 로 옮기고 이 룰은 없애야 합니다.",cmds:["show policy"],options:["r-계열(512-514)·TFTP(69) 허용 룰이 존재하며 최근까지 사용 중", "취약한 원격 서비스가 허용되지 않음", "해당 룰의 출발지가 대역 단위", "해당 룰의 히트가 0"],evidence:["r-계열(512-514)·TFTP(69) 허용 룰이 존재하며 최근까지 사용 중"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&!P.svcIsAll(x.svc)&&P.svcHasWeakRemote(x.svc);})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];c.set('rules', r.filter(function(x){return !(x.action==='permit'&&!P.svcIsAll(x.svc)&&P.svcHasWeakRemote(x.svc));}));},fixNote:"취약한 원격 서비스 허용 룰을 삭제했습니다. (업무는 SSH·SFTP 로 전환)"},
    {id:"ISS-037",expectRules:[9],risk:4,appliesTo:["FW", "VPN"],title:"불필요한 정책 제거 여부",brief:"아무도 안 쓰는 룰은 <b>지울 근거가 없어서</b> 계속 남습니다. 그 사이 그 경로가 열려 있다는 사실은 잊힙니다.",where:"show policy 의 HITS 와 LAST-HIT",hint:"허용 룰만 보세요. 차단 룰의 히트가 0 인 것은 다른 이유일 수 있습니다(앞 항목).",why:"10.20.9.0/24 → 10.40.9.0/24 (TCP/8080) 룰이 히트 0, 마지막 사용 2025-11-20 입니다. 10개월 넘게 쓰이지 않았습니다. 판단기준은 6개월입니다. <b>차단 룰의 히트 0 과 혼동하면 안 됩니다</b> — 차단 룰은 가려져서 0 일 수 있습니다.",cmds:["show policy"],options:["6개월 넘게 사용되지 않은 허용 룰이 존재 (마지막 2025-11-20)", "모든 허용 룰이 최근 사용됨", "차단 룰의 히트가 0", "해당 룰의 서비스가 TCP/8080"],evidence:["6개월 넘게 사용되지 않은 허용 룰이 존재 (마지막 2025-11-20)"],verdict:function(c){var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&(x.lastHit==='never'||x.lastHit<'2026-03-15');})?'vuln':'good';},fix:function(c){var r=c.get('rules')||[];c.set('rules', r.filter(function(x){return !(x.action==='permit'&&(x.lastHit==='never'||x.lastHit<'2026-03-15'));}));},fixNote:"6개월 이상 사용되지 않은 허용 룰을 삭제했습니다. (삭제 전 사용 부서 확인 필요)"},
    {id:"ISS-038",expectRules:[10],risk:5,appliesTo:["FW", "VPN"],title:"서버간 관리포트 허용 금지 여부",brief:"서버끼리 관리 포트로 닿으면, <b>한 대가 뚫렸을 때 옆 서버로 바로 넘어갑니다</b>. 내부 확산 경로가 미리 열려 있는 셈입니다.",where:"show policy — 출발지와 목적지가 모두 srv 존인 줄",hint:"이 항목은 <b>존 경계</b>를 봅니다. 주소가 호스트로 좁혀져 있어도 서버간이면 해당합니다.",why:"서버팜 안에서 10.40.2.10 → 10.40.3.20 으로 SSH(22)가 열려 있습니다. 주소가 호스트 단위로 좁혀져 있어 얼핏 괜찮아 보이지만, <b>서버끼리 관리 포트로 닿는 것</b> 자체가 문제입니다. 서버 관리는 지정된 관리 단말에서만 하도록 합니다.",cmds:["show policy"],options:["서버팜 내 서버간 SSH(22) 허용 룰이 존재", "서버간 통신이 업무 포트로만 허용됨", "해당 룰의 주소가 호스트 단위라 안전함", "해당 룰의 로그가 켜져 있음"],evidence:["서버팜 내 서버간 SSH(22) 허용 룰이 존재"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&x.srcZone==='srv'&&x.dstZone==='srv'&&!P.svcIsAll(x.svc)&&P.svcHasMgmtPort(x.svc);})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];c.set('rules', r.filter(function(x){return !(x.action==='permit'&&x.srcZone==='srv'&&x.dstZone==='srv'&&!P.svcIsAll(x.svc)&&P.svcHasMgmtPort(x.svc));}));},fixNote:"서버간 관리포트 허용 룰을 삭제했습니다. (관리는 관리 단말에서만)"},
    {id:"ISS-039",expectRules:[11],risk:5,appliesTo:["FW", "VPN"],title:"단말과 서버간 접근통제를 우회한 접속 금지 여부",brief:"접근통제시스템을 두는 이유는 <b>누가 언제 무엇을 했는지 남기기 위해서</b>입니다. 그걸 건너뛰는 길이 있으면 시스템을 둔 의미가 없습니다.",where:"show policy — 출발지가 user 존이고 목적지가 srv 존인 관리 포트 룰",hint:"Zones 줄에 접근통제시스템 주소가 적혀 있습니다. 그 주소를 거치지 않는 경로를 찾으세요.",why:"사용자 단말 대역에서 서버팜으로 RDP(3389)가 직접 열려 있습니다. 접근통제시스템(10.99.1.10)을 거치지 않으므로 <b>사용자 권한 확인도, 감사 로그도 남지 않습니다</b>. 단말→접근통제시스템, 접근통제시스템→서버 두 단계로 나눠야 합니다.",cmds:["show policy"],options:["사용자 단말에서 서버팜으로 RDP 가 직접 허용됨 (접근통제 미경유)", "모든 서버 접속이 접근통제시스템을 거침", "해당 룰의 목적지가 대역 단위", "해당 룰의 히트가 4400"],evidence:["사용자 단말에서 서버팜으로 RDP 가 직접 허용됨 (접근통제 미경유)"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&x.srcZone==='user'&&x.dstZone==='srv'&&!P.svcIsAll(x.svc)&&P.svcHasMgmtPort(x.svc);})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];var out=[];r.forEach(function(x){if(x.action==='permit'&&x.srcZone==='user'&&x.dstZone==='srv'&&!P.svcIsAll(x.svc)&&P.svcHasMgmtPort(x.svc)){out.push({srcZone:'user',src:x.src,dstZone:'mgmt',dst:'10.99.1.10',sport:'any',svc:'TCP/443',action:'permit',log:true,bidir:false,hits:0,lastHit:'2026-09-15'});out.push({srcZone:'mgmt',src:'10.99.1.10',dstZone:'srv',dst:x.dst,sport:'any',svc:x.svc,action:'permit',log:true,bidir:false,hits:0,lastHit:'2026-09-15'});} else out.push(x);});c.set('rules',out);},fixNote:"단말→서버 직접 경로를 없애고, 단말→접근통제시스템→서버 두 단계로 나눴습니다."},
    {id:"ISS-041",expectRules:[7, 9, 12],risk:4,appliesTo:["FW", "VPN"],title:"불필요한 네트워크 대역 단위 설정 금지 여부",brief:"출발지와 목적지가 <b>둘 다 대역</b>이면, 그 안의 모든 조합이 열립니다. 필요한 것은 보통 그중 몇 개뿐입니다.",where:"show policy — SOURCE 와 DESTINATION 이 모두 대역/ANY 인 줄",hint:"<b>공개 서비스 구간(dmz)으로 들어오는 허용은 대역 단위가 정상입니다.</b> 내부 구간으로 향하는 것을 보세요. 관리 포트 룰은 앞 항목(ISS-031)이 따로 봅니다.",why:"출발지·목적지가 모두 대역인 룰이 내부 구간으로 향해 있습니다(외부→내부 10.20.0.0/16, 내부→대외계 10.50.0.0/16). 공개 웹 룰(untrust→dmz)은 대역이 정상이므로 <b>같은 모양이라도 향하는 구간에 따라 판단이 달라집니다</b>.",cmds:["show policy"],options:["출발지·목적지가 모두 대역이면서 내부 구간으로 향하는 룰이 존재", "모든 룰이 호스트 단위로 지정됨", "공개 웹 룰의 출발지가 ANY 라 취약", "관리 포트 룰이 대역 단위"],evidence:["출발지·목적지가 모두 대역이면서 내부 구간으로 향하는 룰이 존재"],verdict:function(c){var P=window.WVS_ISS_LAB.rule;var r=c.get('rules')||[];return r.some(function(x){return x.action==='permit'&&x.dstZone!=='dmz'&&!P.svcHasMgmtPort(x.svc)&&P.addrIsBroad(x.src)&&P.addrIsBroad(x.dst);})?'vuln':'good';},fix:function(c){var P=window.WVS_ISS_LAB.rule;var H={"trust": "10.20.4.55", "srv": "10.40.2.10", "user": "10.20.30.41", "untrust": "203.0.113.60", "ext": "10.50.1.20", "dmz": "10.30.0.21"};var r=c.get('rules')||[];r.forEach(function(x){if(x.action==='permit'&&x.dstZone!=='dmz'&&!P.svcHasMgmtPort(x.svc)&&P.addrIsBroad(x.src)&&P.addrIsBroad(x.dst)){x.src=P.narrowAddr(x.src,H[x.srcZone]||'10.20.4.55');x.dst=P.narrowAddr(x.dst,H[x.dstZone]||'10.40.2.10');}});c.set('rules',r);},fixNote:"내부 구간으로 향하는 대역 단위 룰의 출발지·목적지를 지정 호스트로 좁혔습니다."}
   ]}
  ]
};
