/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 (가상 차량)",
 "vin": "KMHXX00XXP0000001",
 "buses": {
  "PT": {
   "name": "파워트레인 CAN",
   "speed": "500kbps"
  },
  "CH": {
   "name": "섀시 CAN(제동·조향)",
   "speed": "500kbps"
  },
  "BODY": {
   "name": "바디 CAN(도어·램프)",
   "speed": "125kbps"
  }
 },
 "secoc": {
  "PT": false,
  "CH": false,
  "BODY": false
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
   "data": "10 00 00 00",
   "desc": "RPM"
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
   "data": "00 00 00 00",
   "desc": "도어 잠금 상태"
  },
  {
   "bus": "BODY",
   "id": "0x3F1",
   "data": "01 00 00 00",
   "desc": "실내등"
  }
 ],
 "ecus": {},
 "obd": {
  "open": true,
  "secureDebug": false
 }
},
  missions: [
    {id:"CAN-01",risk:4,title:"차속 계기 스푸핑 (메시지 위장)",r155:"R155 Annex5 통신채널 · T4 메시지 스푸핑 (A4.1 위장)",brief:"파워트레인 버스의 차속 프레임을 흉내 낸 프레임을 주입하면, 수신 ECU가 <b>진짜 센서 값 대신 공격자 값</b>을 믿습니다. 계기판·주행보조가 잘못된 속도로 동작합니다.",try:"candump PT → cansend PT 0x1A0#00F0",hint:"cansend 결과에 \"인증 없이\" 가 있으면 취약, \"MAC/SecOC 검증\"이면 양호.",why:"파워트레인 버스에 메시지 인증이 없어 위조 차속 프레임이 그대로 수용됩니다. CAN 은 원래 인증·암호화가 없는 프로토콜이라, 붙을 수만 있으면 어떤 값도 위조됩니다.",ez:"CAN 은 발신자를 확인하지 않는 사내 방송 같아서, 아무나 \"지금 시속 0\" 이라고 방송하면 모두가 믿는다.",defense:"안전 관련 프레임에 메시지 인증(SecOC = 메시지별 MAC + 프레시니스 카운터)을 적용하고, 게이트웨이에서 도메인 간 프레임을 필터링한다.",cmds:["candump PT", "cansend PT 0x1A0#00F0"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기", "버스를 찾을 수 없음", "프레임이 관측되지 않음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.PT?'good':'vuln';},fix:function(v){v.secoc.PT=true;},fixNote:"PT(파워트레인) 버스에 SecOC 메시지 인증을 적용했습니다."},
    {id:"CAN-02",risk:5,title:"도어 언락 명령 주입 (코드/명령 인젝션)",r155:"R155 Annex5 통신채널 · T5 무단 조작 (A5.1 코드 인젝션)",brief:"바디 버스의 도어 잠금 프레임을 주입하면 <b>키 없이 문을 열 수</b> 있습니다. 차량 절도·내부 침입의 출발점입니다.",try:"candump BODY → cansend BODY 0x3F0#00",hint:"바디 버스(BODY)의 cansend 결과를 보세요.",why:"바디 버스에 인증이 없어 위조 도어 명령이 수용됩니다. 편의 기능 버스라도 도난과 직결됩니다.",ez:"현관 인터폰에 \"문 열어\" 라고 방송하면 확인 없이 열리는 셈이다.",defense:"도어·이모빌라이저 관련 명령에 메시지 인증을 적용하고, 물리 접근(OBD)에서 오는 프레임을 게이트웨이가 차단한다.",cmds:["candump BODY", "cansend BODY 0x3F0#00"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기", "도어 ECU가 응답하지 않음", "OBD 포트가 잠겨 있음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.BODY?'good':'vuln';},fix:function(v){v.secoc.BODY=true;},fixNote:"BODY(바디) 버스에 SecOC 메시지 인증을 적용했습니다."},
    {id:"CAN-03",risk:5,title:"제동·조향 신호 위조 (악성 내부 메시지)",r155:"R155 Annex5 통신채널 · T11 악성 메시지 (A11.1 내부 메시지)",brief:"섀시 버스의 제동/조향 프레임을 위조하면 <b>주행 중 안전에 직접</b> 영향을 줄 수 있습니다. 가장 위험한 등급입니다.",try:"candump CH → cansend CH 0x2B0#FF",hint:"섀시 버스(CH)의 주입 결과를 보세요.",why:"섀시 버스에 인증이 없어 위조 제동/조향 프레임이 수용됩니다. 안전 관련 버스는 인증이 필수입니다.",ez:"브레이크에게 \"밟아/놓아\" 라고 아무나 명령할 수 있으면 운전자가 통제를 잃는다.",defense:"안전 무결성이 높은 섀시 도메인은 메시지 인증에 더해 도메인 분리·침입탐지(IDS)로 이중 방어한다.",cmds:["candump CH", "cansend CH 0x2B0#FF"],options:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰", "거부됨 — 수신 ECU가 메시지 인증(MAC/SecOC)으로 폐기", "섀시 버스가 없음", "프레임이 관측되지 않음"],evidence:["주입 성공 — 수신 ECU가 인증 없이 위조 프레임을 신뢰"],verdict:function(v){return v.secoc.CH?'good':'vuln';},fix:function(v){v.secoc.CH=true;},fixNote:"CH(섀시) 버스에 SecOC 메시지 인증을 적용했습니다."}
  ]
};
