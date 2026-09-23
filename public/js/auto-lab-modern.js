/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 존아키텍처 (가상 차량)",
 "vin": "Z9HAN00XXP0000007",
 "buses": {},
 "doip": {
  "authRequired": false,
  "tls": false
 },
 "someip": {
  "auth": false
 },
 "ethernet": {
  "segmented": false
 },
 "charging": {
  "tlsPnc": false,
  "isolated": false
 }
},
  missions: [
    {id:"MOD-01",risk:5,title:"DoIP 무인증 라우팅 활성화",r155:"R155 Annex5 · T7 무단 진단 접근 · ISO 13400(DoIP)",brief:"현대 차량은 UDS 진단을 CAN 뿐 아니라 <b>이더넷(DoIP, 13400)</b>으로도 받습니다. 라우팅 활성화에 <b>인증</b>이 없으면, 네트워크에 닿는 누구나 원격으로 내부 ECU 진단에 접근합니다.",try:"doip discover → doip route",hint:"route 결과가 \"성공(인증 없음)\"이면 취약, \"거부(인증 필요)\"면 양호.",why:"DoIP 라우팅 활성화에 인증이 없어, 이더넷 경로(진단기·게이트웨이·원격)에서 무제한 진단 접근이 됩니다. CAN 물리 접근이 필요했던 진단이 이제 네트워크로 열립니다.",ez:"정비소 진단 단자가 이제 \"인터넷 선\"에도 달렸는데, 아무 확인 없이 누구나 꽂을 수 있는 셈이다.",defense:"DoIP 라우팅 활성화에 인증을 요구하고(활성화 타입·인증서), 진단기·게이트웨이를 상호 인증한다. 진단 네트워크를 방화벽·세분화로 격리한다.",cmds:["doip discover", "doip route"],options:["라우팅 활성화 성공 — 인증 없이 이더넷으로 내부 진단 접근", "라우팅 거부 — DoIP 인증(Authentication) 요구", "DoIP 인터페이스 없음", "VIN 조회 실패"],evidence:["라우팅 활성화 성공 — 인증 없이 이더넷으로 내부 진단 접근"],verdict:function(v){return v.doip.authRequired?'good':'vuln';},fix:function(v){v.doip.authRequired=true;},fixNote:"DoIP 라우팅 활성화에 인증 요구를 적용했습니다."},
    {id:"MOD-02",risk:4,title:"DoIP 평문 진단(TLS 부재) 스니핑",r155:"R155 Annex5 · T6 정보 가로채기 · ISO 13400",brief:"DoIP 세션이 <b>TLS 로 보호되지 않으면</b>, 같은 네트워크에서 UDS 요청/응답·VIN·SecurityAccess seed 가 평문으로 관측됩니다. 시드/키 왕복을 엿보면 보안 접근을 재현할 수 있습니다.",try:"doip sniff",hint:"sniff 결과가 \"성공(평문)\"이면 취약, \"암호화됨(TLS)\"이면 양호.",why:"DoIP 가 평문이라 진단 트래픽·자격 재료(seed)가 노출됩니다. 원격/공유 네트워크 경로에서 특히 위험합니다.",ez:"진단 대화가 스피커폰으로 복도에 울려, 지나가는 사람이 비밀번호 힌트까지 다 듣는 셈이다.",defense:"DoIP 세션에 TLS(상호 인증 포함)를 적용해 기밀성·무결성을 보장한다. 진단 네트워크를 물리·논리로 분리한다.",cmds:["doip sniff"],options:["DoIP 평문 관측 — UDS/VIN/seed 가 그대로 노출", "DoIP 암호화됨 — TLS 로 페이로드 판독 불가", "DoIP 인터페이스 없음", "트래픽 없음"],evidence:["DoIP 평문 관측 — UDS/VIN/seed 가 그대로 노출"],verdict:function(v){return v.doip.tls?'good':'vuln';},fix:function(v){v.doip.tls=true;},fixNote:"DoIP 세션에 TLS 를 적용했습니다."},
    {id:"MOD-03",risk:4,title:"SOME/IP 서비스 디스커버리 스푸핑",r155:"R155 Annex5 · T4/T5 스푸핑·인젝션 · SOME/IP",brief:"오토모티브 이더넷은 <b>SOME/IP</b> 서비스로 ECU 기능을 노출합니다. 서비스 디스커버리(SD)에 <b>인증이 없으면</b>, 공격자가 가짜 서비스를 offer 해 구독자를 자기 쪽으로 끌어와 알림·명령을 위조합니다.",try:"someip find → someip spoof DoorControlService",hint:"spoof 결과가 \"성공\"이면 취약, \"무시됨(상호 인증)\"이면 양호.",why:"SD 가 브로드캐스트이고 인증이 없어, 위조 offer 로 서비스 제공자를 가장해 데이터/명령을 가로채거나 위조합니다.",ez:"\"저를 따르세요\" 라고 아무나 외칠 수 있는 안내소라면, 가짜 안내원이 손님을 엉뚱한 곳으로 데려간다.",defense:"SOME/IP 제공자·클라이언트를 상호 인증(서명/TLS)하고, SD 를 신뢰 도메인으로 제한한다. 접근제어 목록으로 서비스 노출을 최소화한다.",cmds:["someip find", "someip spoof DoorControlService"],options:["가짜 서비스 offer 성공 — 구독자가 공격자 서비스에 연결됨", "가짜 서비스 무시됨 — 제공자/클라이언트 상호 인증", "SOME/IP 서비스 없음", "서비스 디스커버리 실패"],evidence:["가짜 서비스 offer 성공 — 구독자가 공격자 서비스에 연결됨"],verdict:function(v){return v.someip.auth?'good':'vuln';},fix:function(v){v.someip.auth=true;},fixNote:"SOME/IP 서비스에 상호 인증을 적용했습니다."},
    {id:"MOD-04",risk:5,title:"오토모티브 이더넷 세분화 부재(존 피벗)",r155:"R155 Annex5 · T10 권한상승/횡적이동 · 존 아키텍처",brief:"존(zonal) 아키텍처에서 인포테인먼트/외부 존과 <b>안전 관련 존이 분리되지 않으면</b>, 침해된 인포테인먼트에서 섀시·파워트레인 도메인으로 <b>횡적 이동</b>합니다.",try:"eth scan → eth pivot",hint:"pivot 결과가 \"성공\"이면 취약, \"차단(존 방화벽)\"이면 양호.",why:"이더넷 백본이 평면이면 외부 노출이 큰 인포테인먼트 한 곳의 침해가 제동/조향 도메인까지 번집니다.",ez:"건물 안내데스크와 금고실 사이에 문이 없으면, 로비만 뚫려도 금고까지 걸어 들어간다.",defense:"존별 VLAN·이더넷 방화벽으로 인포테인먼트/외부 존과 안전 도메인을 분리하고, 도메인 간 통신을 허용목록·게이트웨이로만 통과시킨다.",cmds:["eth scan", "eth pivot"],options:["존 피벗 성공 — 인포테인먼트에서 안전 도메인으로 횡적 이동", "존 피벗 차단 — VLAN·존 방화벽으로 분리", "이더넷 정보 없음", "스캔 실패"],evidence:["존 피벗 성공 — 인포테인먼트에서 안전 도메인으로 횡적 이동"],verdict:function(v){return v.ethernet.segmented?'good':'vuln';},fix:function(v){v.ethernet.segmented=true;},fixNote:"오토모티브 이더넷을 존별로 세분화(VLAN·방화벽)했습니다."},
    {id:"MOD-05",risk:4,title:"ISO 15118 충전 MITM (CCS PLC)",r155:"R155 Annex5 · T16 외부 연결성 · ISO 15118 Plug&Charge",brief:"EV 충전 케이블은 <b>PLC(HomePlug)</b>로 차량↔충전기가 통신합니다. Plug&Charge 세션이 <b>TLS·계약 인증서로 보호되지 않으면</b>, 중간자가 과금 대상·전력 협상을 가로채 변조합니다(에너지 절도·과금 조작).",try:"charge pnc → charge mitm",hint:"mitm 결과가 \"성공\"이면 취약, \"차단(TLS)\"이면 양호.",why:"ISO 15118 PnC 가 TLS·계약 인증서로 보호되지 않으면 PLC 구간 중간자가 세션을 관측·변조해 과금 주체와 전력을 조작합니다.",ez:"충전 콘센트와 카드 결제가 봉인 없는 우편으로 오가면, 중간에서 남의 카드로 바꿔치기할 수 있다.",defense:"ISO 15118 Plug&Charge 를 TLS + 계약/공급자 인증서 상호 검증으로 보호하고, 충전 세션 무결성을 강제한다.",cmds:["charge pnc", "charge mitm"],options:["충전 MITM 성공 — 과금/전력 협상을 가로채 변조", "충전 MITM 차단 — TLS·계약 인증서로 보호", "EV 충전 정보 없음", "충전 세션 없음"],evidence:["충전 MITM 성공 — 과금/전력 협상을 가로채 변조"],verdict:function(v){return v.charging.tlsPnc?'good':'vuln';},fix:function(v){v.charging.tlsPnc=true;},fixNote:"ISO 15118 충전 세션에 TLS·계약 인증서 검증을 적용했습니다."},
    {id:"MOD-06",risk:5,title:"충전 포트→내부망 격리 부재",r155:"R155 Annex5 · T18 외부 인터페이스 침투 · 충전 도메인",brief:"충전 인터페이스가 <b>내부 제어망과 격리되지 않으면</b>, 조작된 충전기 측에서 차량 내부 ECU 로 침투합니다. 충전 포트는 물리적으로 노출된 외부 인터페이스입니다.",try:"charge inject",hint:"inject 결과가 \"성공\"이면 취약, \"차단(격리)\"이면 양호.",why:"충전 도메인이 내부 제어망과 이어져 있으면, 악성 충전기·충전 통신이 곧 내부 ECU 로의 진입로가 됩니다.",ez:"건물 외벽의 콘센트가 사무실 내부 문과 바로 통하면, 밖에서 콘센트만 만져도 안으로 들어온다.",defense:"충전 도메인을 안전 제어망과 게이트웨이·방화벽으로 격리하고, 충전 인터페이스에서 오는 요청을 신뢰하지 않는다(제로트러스트).",cmds:["charge inject"],options:["충전 포트에서 내부망 접근 성공 — 격리 부재", "충전 포트에서 내부망 차단 — 충전 도메인 격리", "EV 충전 정보 없음", "충전기 연결 실패"],evidence:["충전 포트에서 내부망 접근 성공 — 격리 부재"],verdict:function(v){return v.charging.isolated?'good':'vuln';},fix:function(v){v.charging.isolated=true;},fixNote:"충전 도메인을 내부 제어망과 격리했습니다."}
  ]
};
