/* 생성물 — _gen/gen_auto_pentest.py 가 만든다. 직접 고치지 말 것. */
window.AUTO_LAB_DATA = {
  vehicle: {
 "brand": "HANARO",
 "model": "EV9 (가상 차량)",
 "vin": "KMHXX00XXP0000004",
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
  "IVI": {
   "name": "인포테인먼트",
   "bus": "DIAG",
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
   "dids": {},
   "mem": {},
   "fwStrings": [
    "fw build 2023.11",
    "WIFI_PSK=hanaro1234",
    "AES_KEY=00112233445566778899aabbccddeeff"
   ],
   "signedFw": false
  }
 },
 "obd": {
  "open": true,
  "secureDebug": false
 },
 "jtag": {
  "present": true,
  "secureDebug": false
 },
 "usb": {
  "autorun": true,
  "mountExec": true,
  "inputValidated": false
 },
 "bt": {
  "version": "4.2",
  "oneDayPatched": false,
  "nameSanitized": false
 }
},
  missions: [
    {id:"ECU-01",risk:4,title:"JTAG 디버그 포트 개방",r155:"R155 Annex5 · T18 외부 인터페이스 (A18.1 디버그 포트)",brief:"보드의 JTAG 포트가 잠기지 않으면 <b>메모리 덤프·동적 디버깅</b>으로 펌웨어와 비밀을 통째로 가져갑니다.",try:"jtag connect",hint:"jtag 결과가 \"성공\"이면 취약, \"잠김(secure debug)\"이면 양호.",why:"JTAG 디버그가 열려 있어 펌웨어 덤프·동적 분석이 가능합니다. 양산 ECU 는 디버그를 잠가야 합니다.",ez:"기계 뒤판 나사를 안 잠가 두면 누구나 열어 속을 뜯어본다.",defense:"양산 단계에서 디버그 포트를 비활성화하거나 인증 기반 secure debug 로 잠근다. 포트 자체를 두지 않는 것이 최선.",cmds:["jtag connect"],options:["JTAG 연결 성공 — 디버그 포트로 메모리 덤프·디버깅 가능", "JTAG 잠김 — secure debug 로 차단", "보드에 디버그 포트 없음", "OBD 포트 잠김"],evidence:["JTAG 연결 성공 — 디버그 포트로 메모리 덤프·디버깅 가능"],verdict:function(v){return v.jtag.secureDebug?'good':'vuln';},fix:function(v){v.jtag.secureDebug=true;},fixNote:"JTAG 에 secure debug(인증 필요)를 적용했습니다."},
    {id:"ECU-02",risk:4,title:"OBD 무보호 진단 접근",r155:"R155 Annex5 · T18 진단 접근 (A18.3 OBD 동글)",brief:"OBD 포트의 진단 요청이 게이트웨이에서 걸러지지 않고 <b>내부망으로 무제한 전달</b>되면, 동글 하나로 제어망까지 도달합니다.",try:"obd connect",hint:"obd 결과가 \"무제한 전달\"이면 취약, \"진단만 가능\"이면 양호.",why:"OBD 진단 접근을 게이트웨이가 통제하지 않아 물리 접근만으로 제어망에 닿습니다.",ez:"정비용 점검구가 사실은 건물 전체로 통하는 뒷문이면, 점검한다며 아무 데나 들어갈 수 있다.",defense:"OBD↔내부망 사이 게이트웨이가 진단 메시지를 필터링·인증하고, 위험 서비스는 보안 접근 뒤에만 연다.",cmds:["obd connect"],options:["OBD 진단 요청이 제어망으로 무제한 전달됨", "OBD 는 진단만 가능(위험 서비스는 보안 접근 뒤)", "OBD 포트 없음", "JTAG 잠김"],evidence:["OBD 진단 요청이 제어망으로 무제한 전달됨"],verdict:function(v){return v.obd.secureDebug?'good':'vuln';},fix:function(v){v.obd.secureDebug=true;},fixNote:"OBD 진단 접근에 게이트웨이 통제·보안 접근을 적용했습니다."},
    {id:"ECU-03",risk:5,title:"Secure Flash 부재 — 위조 펌웨어 기록",r155:"R155 Annex5 · T12 업데이트 훼손 (A12.2 로컬 플래시)",brief:"ECU 플래시에 <b>서명·무결성 검증</b>이 없으면, 위조 펌웨어를 그대로 기록해 차량을 공격자 의도대로 동작시킵니다.",try:"uds IVI flash",hint:"flash 결과가 \"성공(서명 없이 기록)\"이면 취약, \"실패(secure flash)\"면 양호.",why:"인포테인먼트 ECU 가 서명 검증 없이 펌웨어를 기록합니다. 위조 펌웨어가 그대로 실행됩니다.",ez:"누가 보낸 건지 확인 안 하고 받은 앱을 그대로 설치하는 것과 같다.",defense:"secure flash(서명·무결성 검증)와 secure boot(부팅 시 서명 검증)를 함께 적용하고, 서명 키는 HSM 에 둔다.",cmds:["uds IVI flash"],options:["위조 펌웨어 기록 성공 — 서명 검증 없이 플래시됨", "위조 펌웨어 거부 — secure flash 서명·무결성 검증", "ECU 를 찾을 수 없음", "보안 접근 필요"],evidence:["위조 펌웨어 기록 성공 — 서명 검증 없이 플래시됨"],verdict:function(v){var e=v.ecus.IVI;return (e.secureFlash||(e.secureBoot&&e.signedFw))?'good':'vuln';},fix:function(v){v.ecus.IVI.secureFlash=true;},fixNote:"인포테인먼트 ECU 에 secure flash 서명·무결성 검증을 적용했습니다."},
    {id:"ECU-04",risk:4,title:"펌웨어 하드코딩 키 노출",r155:"R155 Annex5 · T19 키 추출 (A19.3) / T26 암호 오용",brief:"펌웨어에서 <b>하드코딩된 비밀키·비밀번호</b>가 문자열로 그대로 보이면, 추출한 펌웨어에서 키를 뽑아냅니다.",try:"fw strings IVI",hint:"fw strings 결과에 KEY/PSK 가 보이면 취약, 안 보이면(HSM 보관) 양호.",why:"펌웨어에 Wi‑Fi 비밀번호·AES 키가 평문으로 박혀 있어 문자열 추출만으로 노출됩니다. 난독화·심볼 제거는 보조 수단일 뿐입니다.",ez:"금고 열쇠를 금고 표면에 유성펜으로 적어 둔 셈이다.",defense:"비밀키는 코드에 넣지 않고 HSM/보안 저장소에 두고 런타임에만 참조한다. 자격증명은 기기별로 다르게 프로비저닝한다.",cmds:["fw strings IVI"],options:["하드코딩된 비밀키/자격증명이 펌웨어에 노출됨", "비밀키가 보이지 않음(HSM 보관·심볼 제거)", "펌웨어를 읽을 수 없음", "ECU 없음"],evidence:["하드코딩된 비밀키/자격증명이 펌웨어에 노출됨"],verdict:function(v){var s=(v.ecus.IVI.fwStrings||[]).join(' ');return /key|secret|passwd|password|token|psk/i.test(s)?'vuln':'good';},fix:function(v){v.ecus.IVI.fwStrings=['fw build 2024.1','(비밀키는 HSM 에 보관)'];},fixNote:"하드코딩 키를 제거하고 HSM 보관으로 바꿨습니다."},
    {id:"ECU-05",risk:3,title:"USB 실행권한 — 저장 실행파일 동작",r155:"R155 Annex5 · T18 외부 인터페이스 (A18.1/A18.2 USB)",brief:"USB 마운트가 <b>실행권한(exec)</b>으로 붙으면, 저장해 둔 실행파일이 인포테인먼트에서 동작해 발판이 됩니다.",try:"usb plug payload.sh",hint:"usb plug 결과가 \"실행됨\"이면 취약, \"실행 안 됨\"이면 양호.",why:"USB 마운트에 실행권한이 있어 저장된 실행파일이 동작합니다. 외부 저장소는 실행권한 없이 마운트해야 합니다.",ez:"방문객이 들고 온 USB 를 꽂자마자 그 안의 프로그램이 자동 실행되게 둔 것과 같다.",defense:"외부 저장소는 noexec·nosuid 로 마운트하고, 미디어 파서를 샌드박스에 격리하며 파일 형식을 엄격히 검증한다.",cmds:["usb plug payload.sh"],options:["USB 저장 실행파일이 실행됨 — 마운트에 실행권한이 있음", "USB 파일이 실행되지 않음(noexec)", "USB 인터페이스 없음", "자동 재생만 됨"],evidence:["USB 저장 실행파일이 실행됨 — 마운트에 실행권한이 있음"],verdict:function(v){return v.usb.mountExec?'vuln':'good';},fix:function(v){v.usb.mountExec=false;},fixNote:"USB 마운트를 noexec 로 바꿨습니다."},
    {id:"ECU-06",risk:3,title:"USB 퍼징 — 입력 검증 부재",r155:"R155 Annex5 · T28 SW 버그 (A28.1) / T18",brief:"변조된 미디어·USB 패킷에 <b>입력 검증이 없으면</b> 인포테인먼트가 재부팅·크래시합니다. 취약점 발판이 됩니다.",try:"usb fuzz",hint:"usb fuzz 결과가 \"취약(재부팅/크래시)\"이면 취약, \"안정\"이면 양호.",why:"미디어/USB 입력 검증이 없어 변조 입력에 크래시합니다. 크래시는 메모리 손상 취약점으로 이어질 수 있습니다.",ez:"엉터리로 적힌 서류를 받고도 검토 없이 처리하다 담당자가 뻗어버리는 셈이다.",defense:"모든 외부 입력(미디어 헤더·USB 디스크립터)을 경계 검사·형식 검증하고, 파서를 최신 상태로 유지하며 크래시 시 격리·복구한다.",cmds:["usb fuzz"],options:["USB 퍼징에 인포테인먼트가 재부팅/크래시함(입력 검증 부재)", "USB 퍼징에도 안정적임(입력 검증 있음)", "USB 인터페이스 없음", "실행파일이 동작함"],evidence:["USB 퍼징에 인포테인먼트가 재부팅/크래시함(입력 검증 부재)"],verdict:function(v){return v.usb.inputValidated?'good':'vuln';},fix:function(v){v.usb.inputValidated=true;},fixNote:"USB/미디어 입력 검증을 적용했습니다."},
    {id:"ECU-07",risk:3,title:"Bluetooth 미패치 취약점(1-day)",r155:"R155 Annex5 · T17 3rd party/스택 (A17.1) / T28",brief:"Bluetooth 스택에 <b>알려진 취약점 패치가 안 되어</b> 있으면, 공개된 1-day 공격으로 코드 실행이 됩니다.",try:"bt exploit",hint:"bt exploit 결과가 \"성공(미패치)\"이면 취약, \"차단(패치)\"이면 양호.",why:"Bluetooth 스택이 알려진 취약점에 패치되지 않아 공개 익스플로잇이 통합니다. 무선 스택은 패치 관리가 핵심입니다.",ez:"이미 널리 알려진 자물쇠 결함을 고치지 않고 그대로 쓰는 셈이다.",defense:"무선 스택(BT/Wi‑Fi)을 최신 패치로 유지하고, SBOM 으로 구성요소·버전을 추적하며 취약 버전을 차단한다.",cmds:["bt exploit", "bt pair PoC%x%x"],options:["Bluetooth 1-day 공격 성공 — 미패치 스택에서 코드 실행", "Bluetooth 1-day 차단 — 패치 적용됨", "Bluetooth 인터페이스 없음", "페어링만 됨"],evidence:["Bluetooth 1-day 공격 성공 — 미패치 스택에서 코드 실행"],verdict:function(v){return v.bt.oneDayPatched?'good':'vuln';},fix:function(v){v.bt.oneDayPatched=true;},fixNote:"Bluetooth 스택에 알려진 취약점 패치를 적용했습니다."}
  ]
};
