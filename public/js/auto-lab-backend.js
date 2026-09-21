/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "Connected Cloud (가상 백엔드)",
 "vin": "KMHXX00XXP0000005",
 "buses": {},
 "secoc": {},
 "frames": [],
 "ecus": {},
 "backend": {
  "reachable": true,
  "openPorts": [
   "22/ssh(불필요)",
   "443/https",
   "8080/http(관리)"
  ],
  "sqli": true,
  "dosProtected": false,
  "segmented": false,
  "firmwareExposed": true
 },
 "ota": {
  "signed": false,
  "encrypted": false,
  "rollback": false
 },
 "privacy": {
  "wipedOnHandover": false
 }
},
  missions: [
    {id:"BE-01",risk:5,title:"백엔드 서버 무단접근 (SQLi)",r155:"R155 Annex5 · T1 서버 무단접근 (A1.2 SQLi)",brief:"차량 백엔드가 <b>SQL 인젝션</b>에 취약하면, 인증 우회·차량 데이터 대량 추출이 가능하고 서버를 발판으로 차량에 명령을 보낼 수도 있습니다.",try:"net scan → net sqli",hint:"net sqli 결과가 \"성공\"이면 취약, \"실패(바인딩)\"면 양호.",why:"백엔드 API 가 입력을 그대로 질의에 넣어 SQL 인젝션이 됩니다. 서버 침해는 연결된 차량 전체 위협으로 번집니다.",ez:"주문서에 적힌 말을 그대로 명령으로 실행하는 주방이라, \"재료 다 내놔\" 라고 적으면 그대로 따른다.",defense:"모든 질의를 파라미터 바인딩(prepared statement)으로 처리하고 입력을 검증한다. 서버는 최신 패치·최소 권한·WAF 로 하드닝한다.",cmds:["net scan", "net sqli"],options:["SQLi 성공 — 인증 우회·데이터 추출 가능", "SQLi 실패 — 파라미터 바인딩/검증됨", "서버에 도달 불가", "포트가 닫혀 있음"],evidence:["SQLi 성공 — 인증 우회·데이터 추출 가능"],verdict:function(v){return v.backend.sqli?'vuln':'good';},fix:function(v){v.backend.sqli=false;},fixNote:"백엔드 질의를 파라미터 바인딩으로 바꾸고 입력 검증을 적용했습니다."},
    {id:"BE-02",risk:5,title:"OTA 위조 펌웨어 배포 (서명 검증 부재)",r155:"R155 Annex5 · T12 업데이트 훼손 (A12.1 OTA)",brief:"OTA 펌웨어에 <b>서명·무결성 검증</b>이 없으면, 공격자가 위조 펌웨어를 배포해 차량에 설치시킵니다. 전 차량 규모의 위협입니다.",try:"ota push evil.fw",hint:"ota push 결과가 \"성공(서명 없이 설치)\"이면 취약, \"거부(서명 검증)\"면 양호.",why:"OTA 펌웨어를 서명 검증 없이 설치해 위조 이미지가 통합니다. 업데이트 경로는 가장 강하게 지켜야 합니다.",ez:"누가 보냈는지 확인 안 하는 자동 업데이트는, 사칭한 사람이 보낸 것도 그대로 깔아 버린다.",defense:"OTA 이미지에 공급자 서명·무결성 검증(secure update)을 적용하고, 서명 키는 HSM 에 두며 롤백·버전 다운그레이드를 막는다.",cmds:["ota push evil.fw"],options:["OTA 위조 펌웨어 설치 성공 — 서명 검증 없음", "OTA 위조 펌웨어 거부 — 서명·무결성 검증", "OTA 정보 없음", "업데이트 서버 다운"],evidence:["OTA 위조 펌웨어 설치 성공 — 서명 검증 없음"],verdict:function(v){return v.ota.signed?'good':'vuln';},fix:function(v){v.ota.signed=true;},fixNote:"OTA 에 서명·무결성 검증을 적용했습니다."},
    {id:"BE-03",risk:4,title:"업데이트 서버 DoS — 배포 거부",r155:"R155 Annex5 · T13 정상 업데이트 거부 (A13.1 DoS)",brief:"업데이트 서버가 <b>DoS 에 약하면</b>, 공격자가 서버를 마비시켜 중요 보안 패치 배포를 막습니다(취약점 방치 유도).",try:"net dos",hint:"net dos 결과가 \"성공(서비스 정지)\"이면 취약, \"완화\"면 양호.",why:"업데이트 서버가 DoS 완화가 없어 마비됩니다. 보안 패치 배포가 막히면 알려진 취약점이 방치됩니다.",ez:"소방서 전화를 계속 울려 마비시키면, 정작 불이 났을 때 도움을 못 받는 셈이다.",defense:"속도 제한·CDN·이중화·자동 확장으로 가용성을 확보하고, 시스템 장애 시 복구 절차를 둔다.",cmds:["net dos"],options:["DoS 성공 — 업데이트/텔레매틱스 서비스가 정지됨", "DoS 완화 — 속도제한·이중화로 유지됨", "서버 정보 없음", "네트워크 분리됨"],evidence:["DoS 성공 — 업데이트/텔레매틱스 서비스가 정지됨"],verdict:function(v){return v.backend.dosProtected?'good':'vuln';},fix:function(v){v.backend.dosProtected=true;},fixNote:"업데이트 서버에 속도제한·이중화를 적용했습니다."},
    {id:"BE-04",risk:5,title:"네트워크 분리 미흡 — 서버→차량 횡적 이동",r155:"R155 Annex5 · T29 네트워크 설계 (A29.2 분리 우회)",brief:"서버망과 차량 제어망이 <b>분리되어 있지 않으면</b>, 서버 침해가 곧바로 차량 제어망으로 번집니다.",try:"net seg",hint:"net seg 결과가 \"취약(횡적 이동 가능)\"이면 취약, \"분리됨\"이면 양호.",why:"서버망과 제어망이 분리되지 않아 서버 하나가 뚫리면 차량 제어까지 도달합니다.",ez:"사무실과 금고방 사이 문이 없으면, 사무실에 들어온 사람이 금고까지 곧장 간다.",defense:"망 분리·세그멘테이션·최소 권한 경로로 서버-차량 사이를 격리하고, 경계에 상호 인증·모니터링을 둔다.",cmds:["net scan", "net seg"],options:["네트워크 분리 취약 — 서버에서 차량 제어망으로 횡적 이동 가능", "네트워크 분리됨 — 서버 침해가 제어망으로 전파되지 않음", "서버 정보 없음", "SQLi 실패"],evidence:["네트워크 분리 취약 — 서버에서 차량 제어망으로 횡적 이동 가능"],verdict:function(v){return v.backend.segmented?'good':'vuln';},fix:function(v){v.backend.segmented=true;},fixNote:"서버망과 차량 제어망을 분리(세그멘테이션)했습니다."},
    {id:"BE-05",risk:3,title:"중고 이전 시 개인정보 잔존",r155:"R155 Annex5 · T31 사용자 변경 시 정보 유출 (A31.1)",brief:"차량 사용자가 바뀔 때 <b>이전 사용자 데이터가 소거되지 않으면</b>, 위치 이력·연락처·계정이 다음 사람에게 남습니다.",try:"handover",hint:"handover 결과가 \"취약(데이터 잔존)\"이면 취약, \"양호(소거)\"면 양호.",why:"사용자 변경 시 개인정보 소거 절차가 없어 이전 사용자 데이터가 남습니다. 개인정보 보호 요구사항 위반입니다.",ez:"중고폰을 초기화 없이 넘기면 사진·메시지가 다음 주인에게 그대로 넘어가는 셈이다.",defense:"사용자 변경(반납·중고 이전) 시 개인정보·계정·키를 안전하게 소거하는 절차를 두고, 저장은 최소화·암호화한다.",cmds:["handover"],options:["이전 사용자 데이터 잔존 — 위치·연락처·계정이 남음", "이전 사용자 데이터 소거됨", "개인정보 정보 없음", "OTA 미서명"],evidence:["이전 사용자 데이터 잔존 — 위치·연락처·계정이 남음"],verdict:function(v){return v.privacy.wipedOnHandover?'good':'vuln';},fix:function(v){v.privacy.wipedOnHandover=true;},fixNote:"사용자 변경 시 개인정보 소거 절차를 적용했습니다."},
    {id:"BE-06",risk:3,title:"OTA 평문 스니핑 — 펌웨어 복원",r155:"R155 Annex5 · T3 데이터 유출 / T19 펌웨어 추출",brief:"OTA 전송이 <b>평문</b>이면, 통신을 감청해 펌웨어 이미지를 복원하고 독점 코드·키를 추출합니다.",try:"ota sniff",hint:"ota sniff 결과가 \"성공(복원)\"이면 취약, \"암호화(복원 불가)\"면 양호.",why:"OTA 전송이 평문이라 감청으로 펌웨어를 복원할 수 있습니다. 서명(무결성)과 암호화(기밀성)는 별개로 둘 다 필요합니다.",ez:"택배 상자를 투명 비닐로 보내면 도중에 내용물을 그대로 베낄 수 있다.",defense:"OTA 전송을 TLS 등으로 암호화하고, 펌웨어 자체도 기밀이 필요하면 암호화한다. 서명(무결성)과 함께 적용한다.",cmds:["ota sniff"],options:["OTA 스니핑 성공 — 평문 전송이라 펌웨어 복원 가능", "OTA 스니핑 실패 — 암호화되어 복원 불가", "OTA 정보 없음", "서명 없음"],evidence:["OTA 스니핑 성공 — 평문 전송이라 펌웨어 복원 가능"],verdict:function(v){return v.ota.encrypted?'good':'vuln';},fix:function(v){v.ota.encrypted=true;},fixNote:"OTA 전송에 암호화를 적용했습니다."}
  ]
};
