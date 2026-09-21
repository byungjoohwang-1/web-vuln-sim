/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 (가상 차량)",
 "vin": "KMHXX00XXP0000002",
 "buses": {
  "DIAG": {
   "name": "진단 CAN",
   "speed": "500kbps"
  }
 },
 "secoc": {
  "DIAG": false
 },
 "frames": [],
 "ecus": {
  "GW": {
   "name": "중앙 게이트웨이",
   "bus": "DIAG",
   "reqId": "0x710",
   "resId": "0x718",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": true,
    "algo": "xor",
    "seed": "1A2B3C4D"
   },
   "guarded": {
    "wdbi": true,
    "rmba": true,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": true,
   "dids": {},
   "mem": {},
   "fwStrings": []
  },
  "IMMO": {
   "name": "이모빌라이저/BCM",
   "bus": "DIAG",
   "reqId": "0x730",
   "resId": "0x738",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": false,
    "algo": "none"
   },
   "guarded": {
    "wdbi": false,
    "rmba": true,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": true,
   "dids": {
    "F190": {
     "name": "VIN",
     "kind": "vin"
    }
   },
   "mem": {},
   "fwStrings": []
  },
  "CLU": {
   "name": "계기(클러스터)",
   "bus": "DIAG",
   "reqId": "0x720",
   "resId": "0x728",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": false,
    "algo": "none"
   },
   "guarded": {
    "wdbi": false,
    "rmba": true,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": true,
   "dids": {
    "F121": {
     "name": "주행거리(km)",
     "value": "058231"
    }
   },
   "mem": {},
   "fwStrings": []
  },
  "ECM": {
   "name": "엔진제어",
   "bus": "DIAG",
   "reqId": "0x7E0",
   "resId": "0x7E8",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": false,
    "algo": "none"
   },
   "guarded": {
    "wdbi": true,
    "rmba": false,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": true,
   "dids": {},
   "mem": {
    "0x6872": "AF 3C 91 20 (소유자 전화번호 단편)",
    "*": "00 00"
   },
   "fwStrings": []
  },
  "TCU": {
   "name": "텔레매틱스 제어",
   "bus": "DIAG",
   "reqId": "0x740",
   "resId": "0x748",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": false,
    "algo": "none"
   },
   "guarded": {
    "wdbi": true,
    "rmba": true,
    "wmba": false
   },
   "secureBoot": true,
   "secureFlash": true,
   "dids": {},
   "mem": {},
   "fwStrings": []
  }
 }
},
  missions: [
    {id:"UDS-01",risk:5,title:"Security Access(0x27) seed/key 우회",r155:"R155 Annex5 · T9 권한 상승 (보안 접근 우회)",brief:"진단 보안 접근은 seed 를 받아 key 를 되돌려주는 절차입니다. key 계산이 <b>고정 상수·XOR</b>처럼 약하면, 공격자가 seed 만으로 key 를 만들어 위험 서비스를 엽니다.",try:"uds GW session 03 → uds GW secaccess",hint:"secaccess 결과가 \"성공(unlocked)\"이면 취약, \"실패(HSM)\"면 양호.",why:"게이트웨이의 seed/key 알고리즘이 약해(XOR 상수) seed 만으로 key 를 계산할 수 있습니다. 보안 접근이 뚫리면 그 뒤의 메모리·플래시 서비스가 전부 노출됩니다.",ez:"자물쇠가 \"숫자에 1 더하기\" 규칙이면, 받은 숫자를 보고 누구나 열쇠를 만든다.",defense:"seed/key 를 HSM 안에서 강한 알고리즘(예: AES 기반 챌린지-응답)으로 계산하고, 실패 지연·시도 제한을 둔다. 키는 ECU 밖으로 나오지 않는다.",cmds:["uds GW session 03", "uds GW secaccess"],options:["보안 접근 성공 — seed 로부터 key 를 즉시 계산(약한 알고리즘)", "보안 접근 실패 — key 가 HSM 안에서 계산되어 seed 만으로 알 수 없음", "세션 진입 실패", "ECU 응답 없음"],evidence:["보안 접근 성공 — seed 로부터 key 를 즉시 계산(약한 알고리즘)"],verdict:function(v){var a=v.ecus.GW.secAccess.algo;return (a==='aes'||a==='hsm')?'good':'vuln';},fix:function(v){v.ecus.GW.secAccess.algo='hsm';},fixNote:"게이트웨이 보안 접근을 HSM 기반 강한 알고리즘으로 교체했습니다."},
    {id:"UDS-02",risk:4,title:"VIN 위변조 (WriteDataByIdentifier 0x2E)",r155:"R155 Annex5 · T20 데이터 조작 (A20.1 전자 ID 변경)",brief:"VIN(차대번호, DID F190)을 보안 접근 없이 덮어쓸 수 있으면 <b>차량 신원을 위조</b>할 수 있습니다. 도난 차량 세탁·통행료 회피 등에 악용됩니다.",try:"uds IMMO read F190 → uds IMMO write F190 HACKEDVIN00000000",hint:"write 결과가 \"긍정응답(변경됨)\"이면 취약, \"securityAccessDenied\"면 양호.",why:"이모빌라이저 ECU 가 VIN 쓰기(0x2E F190)를 보안 접근 없이 허용합니다. 전자 신원 항목은 보안 접근 뒤에만, 또는 쓰기 자체를 금지해야 합니다.",ez:"신분증 번호를 아무 확인 없이 아무나 고쳐 쓸 수 있게 둔 것과 같다.",defense:"VIN 등 전자 ID 쓰기 서비스는 보안 접근(0x27) 이후에만 허용하거나, 생산 이후 쓰기 잠금(write-protect)한다.",cmds:["uds IMMO read F190", "uds IMMO write F190 HACKEDVIN00000000"],options:["VIN 쓰기 성공 — 보안 접근 없이 F190 이 변경됨", "VIN 쓰기 거부 — securityAccessDenied(먼저 보안 접근 필요)", "VIN 을 읽을 수 없음", "알 수 없는 DID"],evidence:["VIN 쓰기 성공 — 보안 접근 없이 F190 이 변경됨"],verdict:function(v){return v.ecus.IMMO.guarded.wdbi?'good':'vuln';},fix:function(v){v.ecus.IMMO.guarded.wdbi=true;},fixNote:"VIN 쓰기(0x2E F190)에 보안 접근 요구를 걸었습니다."},
    {id:"UDS-03",risk:3,title:"주행거리계 조작 (Odometer DID F121)",r155:"R155 Annex5 · T20 데이터 조작 (A20.4 주행데이터 위조)",brief:"주행거리(DID F121)를 보안 접근 없이 덮어쓰면 <b>중고차 주행거리 조작</b>이 됩니다. 소비자 피해·보증 사기와 직결됩니다.",try:"uds CLU read F121 → uds CLU write F121 000010",hint:"CLU(계기) write 결과를 보세요.",why:"계기 ECU 가 주행거리 쓰기를 보안 접근 없이 허용합니다. 주행 데이터는 여러 소스와 대조·서명해 위조를 막아야 합니다.",ez:"자동차의 \"이만큼 달렸다\"는 기록을 아무나 되돌려 쓸 수 있는 셈이다.",defense:"주행거리 쓰기는 보안 접근 이후로 제한하고, 여러 ECU 값과 교차 검증하며 이력에 서명을 남긴다.",cmds:["uds CLU read F121", "uds CLU write F121 000010"],options:["주행거리 쓰기 성공 — 보안 접근 없이 F121 이 변경됨", "주행거리 쓰기 거부 — securityAccessDenied", "주행거리를 읽을 수 없음", "계기 ECU 응답 없음"],evidence:["주행거리 쓰기 성공 — 보안 접근 없이 F121 이 변경됨"],verdict:function(v){return v.ecus.CLU.guarded.wdbi?'good':'vuln';},fix:function(v){v.ecus.CLU.guarded.wdbi=true;},fixNote:"주행거리 쓰기(0x2E F121)에 보안 접근 요구를 걸었습니다."},
    {id:"UDS-04",risk:4,title:"임의 메모리 읽기 (ReadMemoryByAddress 0x23)",r155:"R155 Annex5 · T19 데이터 추출 (A19.2 개인정보 / A19.3 키 추출)",brief:"임의 주소 메모리를 보안 접근 없이 읽을 수 있으면 <b>개인정보·암호키</b>가 그대로 유출됩니다.",try:"uds ECM rmba 0x6872",hint:"rmba 결과가 실제 메모리 값을 내놓으면 취약, \"securityAccessDenied\"면 양호.",why:"엔진 ECU 가 임의 주소 읽기(0x23)를 보안 접근 없이 허용해 메모리의 민감정보가 노출됩니다.",ez:"금고 안을 확인 없이 아무나 들여다보게 열어 둔 것과 같다.",defense:"메모리 접근 서비스(0x23/0x3D)는 보안 접근 뒤에만, 필요한 주소 범위로만 허용하고, 키·개인정보는 HSM/보호영역에 둔다.",cmds:["uds ECM session 03", "uds ECM rmba 0x6872"],options:["메모리 읽기 성공 — 보안 접근 없이 임의 주소의 민감정보 노출", "메모리 읽기 거부 — securityAccessDenied", "주소를 찾을 수 없음", "ECU 응답 없음"],evidence:["메모리 읽기 성공 — 보안 접근 없이 임의 주소의 민감정보 노출"],verdict:function(v){return v.ecus.ECM.guarded.rmba?'good':'vuln';},fix:function(v){v.ecus.ECM.guarded.rmba=true;},fixNote:"임의 메모리 읽기(0x23)에 보안 접근 요구를 걸었습니다."},
    {id:"UDS-05",risk:4,title:"이벤트 로그 삭제 (RoutineControl 0x31)",r155:"R155 Annex5 · T21 데이터/코드 삭제 (A21.1 로그 삭제)",brief:"메모리 쓰기·루틴(0x31 eraseMemory)이 보안 접근 없이 열려 있으면 <b>공격 흔적(이벤트 로그)을 삭제</b>할 수 있습니다.",try:"uds TCU erase",hint:"erase 결과가 \"긍정응답\"이면 취약, \"securityAccessDenied\"면 양호.",why:"텔레매틱스 ECU 가 메모리 쓰기·삭제 루틴을 보안 접근 없이 허용해 로그를 지울 수 있습니다. 침해 대응·포렌식이 무력화됩니다.",ez:"CCTV 녹화본을 아무나 지울 수 있으면 무슨 일이 있었는지 아무도 모른다.",defense:"쓰기·삭제 루틴은 보안 접근 뒤에만 허용하고, 이벤트 로그는 추가전용(append-only)·원격 백업으로 보존한다.",cmds:["uds TCU erase", "uds TCU wmba 0x2000 00"],options:["로그/메모리 삭제 성공 — 보안 접근 없이 흔적 삭제 가능", "삭제 거부 — securityAccessDenied", "루틴을 찾을 수 없음", "ECU 응답 없음"],evidence:["로그/메모리 삭제 성공 — 보안 접근 없이 흔적 삭제 가능"],verdict:function(v){return v.ecus.TCU.guarded.wmba?'good':'vuln';},fix:function(v){v.ecus.TCU.guarded.wmba=true;},fixNote:"메모리 쓰기·삭제 루틴에 보안 접근 요구를 걸었습니다."}
  ]
};
