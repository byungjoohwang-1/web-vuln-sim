/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 (가상 차량)",
 "vin": "KMHXX00XXP0000003",
 "buses": {},
 "secoc": {},
 "frames": [],
 "ecus": {},
 "keyfob": {
  "type": "fixed",
  "pke": true,
  "distanceBound": false
 },
 "gps": {
  "plausibility": false
 },
 "telematics": {
  "authRemote": false
 }
},
  missions: [
    {id:"RF-01",risk:4,title:"무선 키 고정코드 리플레이",r155:"R155 Annex5 · T16 근거리 무선 (A16.3 리플레이)",brief:"무선 키가 <b>고정 코드</b>를 쓰면, 잠금/해제 신호를 한 번 캡처(SDR 장비)해 그대로 재전송하면 문이 열립니다.",try:"rf record → rf replay",hint:"replay 결과가 \"성공(고정코드)\"이면 취약, \"무시됨(롤링코드)\"이면 양호.",why:"무선 키가 고정 코드를 써서, 한 번 캡처한 해제 신호를 재전송하면 다시 열립니다.",ez:"매번 같은 비밀번호를 외치는 문이라, 한 번 엿들으면 언제든 다시 들어갈 수 있다.",defense:"매 사용마다 코드가 바뀌는 롤링코드(또는 챌린지-응답)를 쓴다. 재전송된 옛 코드는 거부된다.",cmds:["rf record", "rf replay"],options:["재전송 성공 — 고정코드라 캡처한 신호가 그대로 통함", "재전송 무시됨 — 롤링코드라 캡처 신호가 만료됨", "캡처 실패", "이 차량은 무선 키가 없음"],evidence:["재전송 성공 — 고정코드라 캡처한 신호가 그대로 통함"],verdict:function(v){return v.keyfob.type==='rolling'?'good':'vuln';},fix:function(v){v.keyfob.type='rolling';},fixNote:"무선 키를 롤링코드 방식으로 교체했습니다."},
    {id:"RF-02",risk:4,title:"스마트키(PKE) 릴레이 공격",r155:"R155 Annex5 · T16 원격 조작 (A16.1 원격 진입)",brief:"스마트 진입(PKE)은 키가 가까이 있으면 자동으로 열립니다. 공격자 둘이 키↔차량 신호를 <b>중계</b>하면 키가 집 안에 있어도 차 옆에 있는 것처럼 속여 문을 열고 시동을 겁니다. 롤링코드로도 못 막습니다.",try:"rf relay",hint:"relay 결과가 \"성공\"이면 취약, \"차단(거리 한정)\"이면 양호. (롤링코드는 릴레이를 못 막음)",why:"PKE 가 신호 세기만 보고 근접을 판단해, 신호를 중계하면 키가 멀리 있어도 열립니다. 롤링코드는 리플레이는 막아도 릴레이는 못 막습니다.",ez:"문이 \"목소리가 가까이 들리면 열어줌\" 이라면, 확성기로 멀리 있는 주인 목소리를 옆에서 틀어주면 열린다.",defense:"UWB 등 거리 한정(distance bounding)으로 키의 실제 물리 거리를 측정한다. 사용자 모션 인증(잠들면 비활성)도 보완책.",cmds:["rf relay"],options:["릴레이 성공 — 키↔차량 신호를 중계해 근접을 위조", "릴레이 차단 — 거리 한정(UWB)으로 실제 근접을 검증", "이 차량은 PKE 가 아님", "재전송 무시됨(롤링코드)"],evidence:["릴레이 성공 — 키↔차량 신호를 중계해 근접을 위조"],verdict:function(v){return v.keyfob.distanceBound?'good':'vuln';},fix:function(v){v.keyfob.distanceBound=true;},fixNote:"PKE 에 UWB 거리 한정을 적용했습니다."},
    {id:"RF-03",risk:3,title:"GPS 스푸핑",r155:"R155 Annex5 · T16 센서 간섭 (A16.3)",brief:"위조 GPS 신호(SDR 장비)를 쏘면 차량이 <b>가짜 위치</b>를 믿습니다. 내비·지오펜스·긴급통화 위치가 틀어집니다.",try:"gps spoof 37.0,127.0",hint:"gps 결과가 \"성공(반영)\"이면 취약, \"완화(교차검증)\"면 양호.",why:"GPS 위치를 그대로 신뢰해 위조 좌표가 반영됩니다. 위성 신호는 인증이 없어 스푸핑에 취약합니다.",ez:"내비가 \"하늘에서 들리는 위치 안내\"를 무조건 믿으면, 가짜 방송으로 엉뚱한 곳에 있다고 속일 수 있다.",defense:"속도·관성(IMU)·맵매칭과 교차 검증해 급변·물리적으로 불가능한 좌표를 거부한다. 다중 위성군·인증 신호를 활용한다.",cmds:["gps spoof 37.0,127.0"],options:["GPS 스푸핑 성공 — 위조 좌표가 그대로 반영됨", "GPS 스푸핑 완화 — 위치 타당성 교차검증으로 거부", "GPS 인터페이스 없음", "좌표 형식 오류"],evidence:["GPS 스푸핑 성공 — 위조 좌표가 그대로 반영됨"],verdict:function(v){return v.gps.plausibility?'good':'vuln';},fix:function(v){v.gps.plausibility=true;},fixNote:"GPS 위치에 타당성 교차검증을 적용했습니다."},
    {id:"RF-04",risk:4,title:"텔레매틱스 원격 명령 무인증",r155:"R155 Annex5 · T16 원격 조작 (A16.1 원격키/텔레매틱스)",brief:"앱·서버를 거치는 원격 잠금해제/시동이 <b>소유자 인증을 제대로 하지 않으면</b>, 공격자가 원격으로 차량을 조작합니다.",try:"remote unlock",hint:"remote 결과가 \"성공(무인증)\"이면 취약, \"거부(인증 검증)\"면 양호.",why:"텔레매틱스 원격 명령이 소유자 인증 없이 전달됩니다. 원격 기능은 편의만큼 인증이 중요합니다.",ez:"집 현관을 여는 앱이 로그인·본인확인 없이 \"열어\" 버튼만 있으면 누구나 연다.",defense:"원격 명령마다 강한 소유자 인증(토큰·MFA)과 서버-차량 상호 인증, 명령 서명·재전송 방지를 적용한다.",cmds:["remote unlock", "remote start"],options:["원격 명령 성공 — 인증 없이 명령이 차량에 전달됨", "원격 명령 거부 — 소유자 인증·토큰 검증", "텔레매틱스 정보 없음", "네트워크 분리됨"],evidence:["원격 명령 성공 — 인증 없이 명령이 차량에 전달됨"],verdict:function(v){return v.telematics.authRemote?'good':'vuln';},fix:function(v){v.telematics.authRemote=true;},fixNote:"텔레매틱스 원격 명령에 소유자 인증·토큰 검증을 적용했습니다."}
  ]
};
