/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 표적 (가상 차량)",
 "vin": "Z9HAN00XXP0000009",
 "buses": {
  "PT": {
   "name": "파워트레인 CAN",
   "speed": "500kbps",
   "iface": "can0"
  },
  "CH": {
   "name": "섀시 CAN",
   "speed": "500kbps",
   "iface": "can1"
  }
 },
 "secoc": {
  "PT": false,
  "CH": false
 },
 "freshness": {
  "PT": false,
  "CH": false
 },
 "rateLimit": {
  "PT": false,
  "CH": false
 },
 "gateway": {
  "filtered": false
 },
 "ids": {
  "enabled": false
 },
 "frames": [
  {
   "bus": "PT",
   "id": "0x1A0",
   "data": "00 32 00 00",
   "desc": "차속(km/h)"
  },
  {
   "bus": "CH",
   "id": "0x2B0",
   "data": "00 00 00 00",
   "desc": "제동 요청"
  }
 ],
 "ecus": {
  "GW": {
   "name": "중앙 게이트웨이",
   "bus": "CH",
   "reqId": "0x710",
   "resId": "0x718",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": true,
    "algo": "fixed",
    "seed": "DEADBEEF"
   },
   "guarded": {
    "wdbi": true,
    "rmba": true,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": true,
   "signedFw": true,
   "dids": {},
   "mem": {},
   "fwStrings": []
  },
  "IVI": {
   "name": "인포테인먼트(외부연결)",
   "bus": "CH",
   "reqId": "0x760",
   "resId": "0x768",
   "session": "default",
   "unlocked": false,
   "secAccess": {
    "present": false,
    "algo": "none"
   },
   "guarded": {
    "wdbi": true,
    "rmba": true,
    "wmba": true
   },
   "secureBoot": true,
   "secureFlash": false,
   "signedFw": false,
   "dids": {},
   "mem": {},
   "fwStrings": []
  },
  "TCU": {
   "name": "텔레매틱스 제어",
   "bus": "CH",
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
   "signedFw": true,
   "dids": {},
   "mem": {},
   "fwStrings": []
  }
 },
 "obd": {
  "present": true,
  "gatewayFiltered": false
 },
 "telematics": {
  "authRemote": false
 }
},
  missions: [
    {id:"CHAIN-01",risk:5,title:"① 초기 접근 — OBD→제어망 게이트웨이 우회",r155:"R155 Annex5 · T18/T29 (초기 접근: 물리 진단→제어망)",brief:"킬체인 1단계. 정비소 대기 중 OBD 포트에 동글을 꽂았다고 가정합니다. 게이트웨이가 진단 구간을 <b>필터링하지 않으면</b>, OBD 에서 넣은 프레임이 파워트레인 제어망까지 그대로 도달합니다.",try:"recon → obd connect → obd inject PT 0x1A0#00F00000",hint:"obd inject 결과가 \"주입 성공\"이면 취약, \"게이트웨이 차단\"이면 양호.",why:"게이트웨이가 진단/외부 구간과 제어망을 분리하지 않아, 물리 접근만으로 제어망에 발을 들입니다. 킬체인의 첫 고리입니다.",ez:"건물 안내데스크(OBD)가 사실 모든 사무실로 통하면, 방문객이 곧장 어디든 들어간다.",defense:"게이트웨이가 도메인 간 프레임을 화이트리스트로 필터링·인증한다. 이 고리만 끊어도 이후 단계가 막힌다.",cmds:["obd connect", "obd inject PT 0x1A0#00F00000"],options:["초기 접근 성공 — OBD에서 제어망에 직접 프레임 도달(게이트웨이 미필터)", "게이트웨이 차단 — 진단 구간 프레임이 제어망으로 못 넘어감", "OBD 포트 없음", "버스를 찾을 수 없음"],evidence:["초기 접근 성공 — OBD에서 제어망에 직접 프레임 도달(게이트웨이 미필터)"],verdict:function(v){return v.gateway.filtered?'good':'vuln';},fix:function(v){v.gateway.filtered=true;},fixNote:"게이트웨이 도메인 필터링을 적용해 초기 접근 고리를 끊었습니다."},
    {id:"CHAIN-02",risk:5,title:"② 권한 상승 — 게이트웨이 보안 접근 우회",r155:"R155 Annex5 · T9 권한 상승 (보안 접근 우회)",brief:"킬체인 2단계. 게이트웨이 ECU 의 보안 접근(0x27)이 <b>고정 key</b>를 쓰면, seed 를 받아 고정 key 를 되보내 위험 서비스 권한을 얻습니다.",try:"uds GW session 03 → uds GW secaccess",hint:"secaccess 가 \"긍정응답(unlocked)\"이면 취약, \"invalidKey\"면 양호.",why:"게이트웨이 보안 접근이 고정 key 라 seed 만 받으면 바로 뚫립니다. 권한을 얻으면 이후 플래시·삭제 서비스로 확장됩니다.",ez:"모든 방의 마스터키가 \"항상 같은 열쇠\"라면, 한 번 알아내면 어디든 연다.",defense:"보안 접근을 HSM 기반 강한 챌린지-응답으로 바꾸고 시도 제한을 둔다. 이 고리를 끊으면 권한 상승이 막힌다.",cmds:["uds GW session 03", "uds GW secaccess"],options:["권한 상승 성공 — 고정 key 로 보안 접근 해제", "권한 상승 실패 — key 를 알 수 없음(HSM)", "세션 진입 실패", "ECU 응답 없음"],evidence:["권한 상승 성공 — 고정 key 로 보안 접근 해제"],verdict:function(v){var a=v.ecus.GW.secAccess.algo;return (a==='aes'||a==='hsm')?'good':'vuln';},fix:function(v){v.ecus.GW.secAccess.algo='hsm';},fixNote:"게이트웨이 보안 접근을 HSM 강한 알고리즘으로 교체했습니다."},
    {id:"CHAIN-03",risk:5,title:"③ 횡적 이동 — 안전 버스에 위조 프레임 주입",r155:"R155 Annex5 · T5/T11 (횡적 이동: 제어 프레임 주입)",brief:"킬체인 3단계. 확보한 접근으로 <b>섀시(안전) 버스</b>에 위조 제동 프레임을 주입합니다. 메시지 인증이 없으면 그대로 수용됩니다.",try:"cansend CH 0x2B0#FF000000",hint:"cansend 결과가 \"주입 성공\"이면 취약, \"MAC 폐기\"면 양호.",why:"안전 무결성이 높은 섀시 버스에 메시지 인증이 없어 위조 제어 프레임이 수용됩니다. 킬체인이 안전 도메인으로 번집니다.",ez:"한 부서에 들어온 사람이 아무 확인 없이 옆 부서 결재까지 찍을 수 있는 셈이다.",defense:"안전 버스에 SecOC 메시지 인증을 적용한다. 이 고리를 끊으면 초기 접근이 있어도 안전 도메인은 지켜진다.",cmds:["cansend CH 0x2B0#FF000000"],options:["횡적 이동 성공 — 섀시 버스가 위조 프레임을 인증 없이 수용", "MAC 검증 실패 → 폐기(SecOC)", "섀시 버스 없음", "프레임 관측 안 됨"],evidence:["횡적 이동 성공 — 섀시 버스가 위조 프레임을 인증 없이 수용"],verdict:function(v){return v.secoc.CH?'good':'vuln';},fix:function(v){v.secoc.CH=true;},fixNote:"섀시(CH) 버스에 SecOC 메시지 인증을 적용했습니다."},
    {id:"CHAIN-04",risk:4,title:"④ 지속성 — 위조 펌웨어 설치",r155:"R155 Annex5 · T12/T23 (지속성: 펌웨어 변조)",brief:"킬체인 4단계. 재부팅해도 살아남도록 인포테인먼트 ECU 에 <b>위조 펌웨어</b>를 심습니다. secure flash 가 없으면 서명 검증 없이 기록됩니다.",try:"uds IVI flash",hint:"flash 가 \"성공\"이면 취약, \"secure flash 거부\"면 양호.",why:"인포테인먼트 ECU 에 secure flash 가 없어 위조 펌웨어가 설치됩니다. 공격자가 재부팅 후에도 지속적으로 자리 잡습니다.",ez:"집 열쇠를 복사해 숨겨두면, 쫓겨나도 다시 들어올 수 있는 셈이다.",defense:"secure boot/flash 로 서명된 펌웨어만 실행·기록하고 서명 키는 HSM 에 둔다. 이 고리를 끊으면 지속성 확보가 막힌다.",cmds:["uds IVI flash"],options:["지속성 확보 — 서명 검증 없이 위조 펌웨어 설치됨", "거부됨 — secure flash 서명·무결성 검증", "ECU 없음", "보안 접근 필요"],evidence:["지속성 확보 — 서명 검증 없이 위조 펌웨어 설치됨"],verdict:function(v){var e=v.ecus.IVI;return (e.secureFlash||(e.secureBoot&&e.signedFw))?'good':'vuln';},fix:function(v){v.ecus.IVI.secureFlash=true;},fixNote:"인포테인먼트 ECU 에 secure flash 를 적용했습니다."},
    {id:"CHAIN-05",risk:5,title:"⑤ 목표 달성 — 원격 도어/시동 탈취",r155:"R155 Annex5 · T16 (목표: 원격 제어 탈취)",brief:"킬체인 5단계(목표). 텔레매틱스 원격 명령이 <b>소유자 인증 없이</b> 처리되면, 원격으로 문을 열고 시동을 걸어 차량을 탈취합니다.",try:"remote unlock → remote start",hint:"remote 가 \"성공(무인증)\"이면 취약, \"거부(인증)\"면 양호.",why:"텔레매틱스 원격 명령이 소유자 인증 없이 처리돼 최종 목표(차량 탈취)가 달성됩니다.",ez:"현관을 여는 앱에 본인확인이 없으면, 남이 원격으로 문을 열고 들어온다.",defense:"원격 명령마다 강한 소유자 인증(토큰·MFA)·상호 인증·명령 서명을 적용한다. 이 고리를 끊으면 목표 달성이 막힌다.",cmds:["remote unlock", "remote start"],options:["목표 달성 — 인증 없이 원격 잠금해제·시동", "거부됨 — 소유자 인증·토큰 검증", "텔레매틱스 정보 없음", "네트워크 분리됨"],evidence:["목표 달성 — 인증 없이 원격 잠금해제·시동"],verdict:function(v){return v.telematics.authRemote?'good':'vuln';},fix:function(v){v.telematics.authRemote=true;},fixNote:"텔레매틱스 원격 명령에 소유자 인증·토큰 검증을 적용했습니다."},
    {id:"CHAIN-06",risk:3,title:"⑥ 흔적 제거 — 이벤트 로그 삭제",r155:"R155 Annex5 · T21 (흔적 제거: 로그 삭제)",brief:"킬체인 마지막. 텔레매틱스 ECU 의 삭제 루틴이 <b>보안 접근 없이</b> 열려 있으면, 공격 흔적(이벤트 로그)을 지워 탐지·포렌식을 무력화합니다.",try:"uds TCU erase",hint:"erase 가 \"성공\"이면 취약, \"securityAccessDenied\"면 양호.",why:"삭제 루틴이 보안 접근 없이 열려 있어 공격 흔적을 지웁니다. 로그 보존이 없으면 사고 원인도, 대응도 어렵습니다.",ez:"침입자가 CCTV 녹화까지 지우고 나가면 무슨 일이 있었는지 아무도 모른다.",defense:"삭제 루틴은 보안 접근 뒤에만, 이벤트 로그는 추가전용·원격 백업으로 보존해 지울 수 없게 한다.",cmds:["uds TCU erase"],options:["흔적 제거 성공 — 보안 접근 없이 이벤트 로그 삭제", "삭제 거부 — securityAccessDenied", "루틴 없음", "ECU 응답 없음"],evidence:["흔적 제거 성공 — 보안 접근 없이 이벤트 로그 삭제"],verdict:function(v){return v.ecus.TCU.guarded.wmba?'good':'vuln';},fix:function(v){v.ecus.TCU.guarded.wmba=true;},fixNote:"삭제 루틴에 보안 접근 요구를 걸고 로그를 보존 처리했습니다."}
  ]
};
