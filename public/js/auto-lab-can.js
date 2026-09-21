/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 (가상 차량)",
 "vin": "Z9HAN00XXP0000001",
 "buses": {
  "PT": {
   "name": "파워트레인 CAN",
   "speed": "500kbps",
   "iface": "can0"
  },
  "CH": {
   "name": "섀시 CAN(제동·조향)",
   "speed": "500kbps",
   "iface": "can1"
  },
  "BODY": {
   "name": "바디 CAN(도어·램프)",
   "speed": "125kbps",
   "iface": "can2"
  },
  "ADAS": {
   "name": "ADAS/센서 CAN",
   "speed": "500kbps",
   "iface": "can3"
  }
 },
 "secoc": {
  "PT": false,
  "CH": false,
  "BODY": false,
  "ADAS": false
 },
 "freshness": {
  "PT": false,
  "CH": false,
  "BODY": false,
  "ADAS": false
 },
 "rateLimit": {
  "PT": false,
  "CH": false,
  "BODY": false,
  "ADAS": false
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
   "bus": "PT",
   "id": "0x0C9",
   "data": "1A 00 00 00",
   "desc": "RPM"
  },
  {
   "bus": "PT",
   "id": "0x120",
   "data": "00 00 10 00",
   "desc": "가속페달"
  },
  {
   "bus": "CH",
   "id": "0x2B0",
   "data": "00 00 00 00",
   "desc": "제동 요청"
  },
  {
   "bus": "CH",
   "id": "0x2C1",
   "data": "80 00 00 00",
   "desc": "조향 토크"
  },
  {
   "bus": "BODY",
   "id": "0x3F0",
   "data": "01 00 00 00",
   "desc": "도어 잠금 상태"
  },
  {
   "bus": "BODY",
   "id": "0x3F1",
   "data": "00 00 00 00",
   "desc": "실내등"
  },
  {
   "bus": "ADAS",
   "id": "0x410",
   "data": "00 40 00 00",
   "desc": "전방 레이더 거리"
  }
 ],
 "ecus": {},
 "obd": {
  "present": true,
  "gatewayFiltered": false
 }
},
  missions: [
    {id:"CAN-01",risk:4,title:"차속 계기 스푸핑 (위조 프레임 주입)",r155:"R155 Annex5 통신채널 · T4 메시지 스푸핑 (A4.1 위장)",brief:"파워트레인 버스의 차속 프레임을 흉내 낸 프레임을 주입하면, 수신 ECU가 <b>진짜 센서 값 대신 공격자 값</b>을 믿습니다. 계기판·주행보조가 잘못된 속도로 동작합니다.",try:"candump PT → cansend PT 0x1A0#00F00000",hint:"cansend 결과가 \"주입 성공\"이면 취약, \"MAC 검증 실패 → 폐기\"면 양호.",why:"파워트레인 버스에 메시지 인증이 없어 위조 차속 프레임이 그대로 수용됩니다. CAN 은 원래 발신자 인증·암호화가 없는 프로토콜이라, 붙을 수만 있으면 어떤 값도 위조됩니다.",ez:"CAN 은 발신자를 확인하지 않는 사내 방송 같아서, 아무나 \"지금 시속 0\" 이라고 방송하면 모두가 믿는다.",defense:"안전 관련 프레임에 메시지 인증(SecOC = 메시지별 MAC)을 적용한다. 위조 프레임은 MAC 검증에서 폐기된다.",cmds:["candump PT", "cansend PT 0x1A0#00F00000"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "MAC 검증 실패 → 프레임 폐기(SecOC)", "버스를 찾을 수 없음", "프레임이 관측되지 않음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.PT?'good':'vuln';},fix:function(v){v.secoc.PT=true;},fixNote:"PT(파워트레인) 버스에 SecOC 메시지 인증(MAC)을 적용했습니다."},
    {id:"CAN-02",risk:5,title:"도어 언락 명령 주입 (코드/명령 인젝션)",r155:"R155 Annex5 통신채널 · T5 무단 조작 (A5.1 코드 인젝션)",brief:"바디 버스의 도어 잠금 프레임을 주입하면 <b>키 없이 문을 열 수</b> 있습니다. 차량 절도·내부 침입의 출발점입니다.",try:"candump BODY → cansend BODY 0x3F0#00000000",hint:"바디 버스(BODY)의 cansend 결과를 보세요.",why:"바디 버스에 인증이 없어 위조 도어 명령이 수용됩니다. 편의 기능 버스라도 도난과 직결됩니다.",ez:"현관 인터폰에 \"문 열어\" 라고 방송하면 확인 없이 열리는 셈이다.",defense:"도어·이모빌라이저 관련 명령에 메시지 인증을 적용하고, 외부(OBD)에서 오는 프레임은 게이트웨이가 차단한다.",cmds:["candump BODY", "cansend BODY 0x3F0#00000000"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "MAC 검증 실패 → 프레임 폐기(SecOC)", "도어 ECU가 응답하지 않음", "OBD 포트가 잠겨 있음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.BODY?'good':'vuln';},fix:function(v){v.secoc.BODY=true;},fixNote:"BODY(바디) 버스에 SecOC 메시지 인증을 적용했습니다."},
    {id:"CAN-03",risk:5,title:"제동·조향 신호 위조 (악성 내부 메시지)",r155:"R155 Annex5 통신채널 · T11 악성 메시지 (A11.1 내부 메시지)",brief:"섀시 버스의 제동/조향 프레임을 위조하면 <b>주행 중 안전에 직접</b> 영향을 줄 수 있습니다. 가장 위험한 등급입니다.",try:"candump CH → cansend CH 0x2B0#FF000000",hint:"섀시 버스(CH)의 주입 결과를 보세요.",why:"섀시 버스에 인증이 없어 위조 제동/조향 프레임이 수용됩니다. 안전 무결성이 높은 버스는 인증이 필수입니다.",ez:"브레이크에게 \"밟아/놓아\" 라고 아무나 명령할 수 있으면 운전자가 통제를 잃는다.",defense:"섀시 도메인은 메시지 인증에 더해 도메인 분리·침입탐지(IDS)로 이중 방어한다.",cmds:["candump CH", "cansend CH 0x2B0#FF000000"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "MAC 검증 실패 → 프레임 폐기(SecOC)", "섀시 버스가 없음", "프레임이 관측되지 않음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.CH?'good':'vuln';},fix:function(v){v.secoc.CH=true;},fixNote:"CH(섀시) 버스에 SecOC 메시지 인증을 적용했습니다."},
    {id:"CAN-04",risk:4,title:"리플레이 공격 (프레시니스 부재)",r155:"R155 Annex5 통신채널 · T6 리플레이 (A6.3)",brief:"메시지 인증(MAC)이 있어도 <b>프레시니스(재전송 방지 카운터)</b>가 없으면, 캡처한 정상 프레임을 그대로 재전송해 같은 동작(예: 도어 해제)을 재현할 수 있습니다. MAC 만으로는 리플레이를 못 막습니다.",try:"candump BODY → canreplay BODY 0x3F0",hint:"canreplay 결과가 \"재전송 성공\"이면 취약, \"프레시니스가 만료 처리\"면 양호.",why:"바디 버스에 프레시니스 카운터가 없어 캡처한 정상 프레임을 재전송하면 그대로 통합니다. MAC(위조 방지)와 프레시니스(재전송 방지)는 별개로 둘 다 필요합니다.",ez:"한 번 통과된 정품 출입증을 복사해 다시 쓰면 통과되는 셈. 매번 바뀌는 번호가 있어야 재사용을 막는다.",defense:"SecOC 에 프레시니스(단조 증가 카운터/논스)를 포함해 재전송된 옛 메시지를 거부한다.",cmds:["candump BODY", "canreplay BODY 0x3F0"],options:["재전송 성공 — 프레시니스(재전송 방지)가 없어 옛 프레임 재사용", "거부됨 — 프레시니스 카운터가 옛 프레임을 만료 처리", "프레임이 관측되지 않음", "MAC 검증 실패"],evidence:["재전송 성공 — 프레시니스(재전송 방지)가 없어 옛 프레임 재사용"],verdict:function(v){return v.freshness.BODY?'good':'vuln';},fix:function(v){v.freshness.BODY=true;},fixNote:"BODY 버스 SecOC 에 프레시니스(재전송 방지 카운터)를 추가했습니다."},
    {id:"CAN-05",risk:4,title:"버스오프 DoS (고우선순위 프레임 폭주)",r155:"R155 Annex5 통신채널 · T8 서비스 거부 (A8.1 가비지 폭주)",brief:"고우선순위 CAN ID 를 <b>고속으로 쏟아부으면</b> 버스를 독점해 정상 ECU 통신이 끊깁니다(버스오프). 계기·제어 신호가 마비됩니다.",try:"canflood PT 0x000",hint:"canflood 결과가 \"버스오프\"면 취약, \"완화됨\"이면 양호.",why:"파워트레인 버스에 부하 제한이 없어 폭주 프레임이 버스를 독점합니다. 가용성(availability) 위협입니다.",ez:"한 사람이 회의에서 쉬지 않고 큰 소리로 떠들면 아무도 말을 못 하는 것과 같다.",defense:"버스 부하 제한/속도 제한, 게이트웨이의 프레임율 필터링, 그리고 이상 프레임율을 잡는 IDS 로 대응한다.",cmds:["canflood PT 0x000"],options:["버스오프 성공 — 부하 제한이 없어 버스가 마비됨", "완화됨 — 부하 제한/필터로 통신 유지", "버스를 찾을 수 없음", "MAC 검증 실패"],evidence:["버스오프 성공 — 부하 제한이 없어 버스가 마비됨"],verdict:function(v){return v.rateLimit.PT?'good':'vuln';},fix:function(v){v.rateLimit.PT=true;},fixNote:"PT 버스에 부하 제한/프레임율 필터를 적용했습니다."},
    {id:"CAN-06",risk:5,title:"게이트웨이 도메인 우회 (OBD→제어망 직접 주입)",r155:"R155 Annex5 · T18 OBD 진단 접근 / T29 네트워크 분리 (A18.3/A29.2)",brief:"OBD 포트에서 넣은 프레임이 게이트웨이에 <b>걸러지지 않고 제어망으로 그대로 전달</b>되면, 동글 하나로 안전 관련 버스에 직접 프레임을 주입할 수 있습니다.",try:"obd connect → obd inject ADAS 0x410#00000000",hint:"obd inject 결과가 \"주입 성공\"이면 취약, \"게이트웨이 차단\"이면 양호.",why:"게이트웨이가 OBD/진단 구간과 내부 제어망 사이를 필터링하지 않아, 물리 접근만으로 제어망에 프레임이 닿습니다.",ez:"정비용 점검구가 사실은 건물 전체로 통하는 뒷문이면, 점검한다며 아무 방에나 들어갈 수 있다.",defense:"게이트웨이가 도메인 간 프레임을 화이트리스트로 필터링·인증하고, 진단 요청은 세션·보안 접근으로 통제한다.",cmds:["obd connect", "obd inject ADAS 0x410#00000000"],options:["게이트웨이 우회 성공 — OBD에서 제어망 버스에 직접 도달", "게이트웨이 차단 — 도메인 필터가 외부 프레임을 막음", "OBD 포트 없음", "버스를 찾을 수 없음"],evidence:["게이트웨이 우회 성공 — OBD에서 제어망 버스에 직접 도달"],verdict:function(v){return v.gateway.filtered?'good':'vuln';},fix:function(v){v.gateway.filtered=true;},fixNote:"게이트웨이에 도메인 간 프레임 필터링을 적용했습니다."},
    {id:"CAN-07",risk:3,title:"무탐지 공격 (IDS 부재)",r155:"R155 Annex5 · 탐지·대응 (M-controls, 침입탐지)",brief:"프레임 주입·리플레이·DoS 가 <b>아무 경보 없이</b> 성공하면, 공격이 일어나도 아무도 모릅니다. 차량 IDS(침입탐지)가 있어야 이상 프레임/주기 이탈을 잡아냅니다.",try:"cansend ADAS 0x410#FFFFFFFF (IDS 경보 여부 확인)",hint:"cansend 결과에 \"IDS 경보 없음\"이면 취약, \"IDS 경보 발생\"이면 양호.",why:"차량에 침입탐지(IDS)가 없어 프레임 주입이 경보 없이 성공합니다. 예방(인증)이 뚫려도 탐지가 있으면 대응할 수 있습니다.",ez:"CCTV 가 없으면 도둑이 들어와도 아무도 모른다. 자물쇠(예방)와 CCTV(탐지)는 둘 다 필요하다.",defense:"차량 IDS/IDPS 로 이상 프레임·주기 이탈·비인가 ID 를 탐지하고, SOC/텔레매틱스로 경보를 올린다(탐지는 예방의 보완책).",cmds:["cansend ADAS 0x410#FFFFFFFF"],options:["공격이 탐지되지 않음 — IDS 경보 없음", "IDS 경보 발생 — 이상 프레임 탐지됨", "버스를 찾을 수 없음", "MAC 검증 실패"],evidence:["공격이 탐지되지 않음 — IDS 경보 없음"],verdict:function(v){return v.ids.enabled?'good':'vuln';},fix:function(v){v.ids.enabled=true;},fixNote:"차량 침입탐지(IDS)를 활성화했습니다."}
  ]
};
