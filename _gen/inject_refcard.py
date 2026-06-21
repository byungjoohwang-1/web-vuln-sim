# -*- coding: utf-8 -*-
"""03_code_*.html 시큐어코딩 랩 페이지에 '실제 사고사례 + 표준 매핑(CWE/OWASP)' 카드 주입.
- 공개적으로 알려진 실제 침해사고만 사용(개발보안 가이드 원문 비복제).
- 멱등(idempotent): <!-- REF-CARD --> 마커가 있으면 건너뜀.
"""
import os, re

PUB = os.path.join(os.path.dirname(__file__), '..', 'public')

# key(파일명 접미사): (CWE, OWASP, 사고사례 HTML)
M = {
 'bufferoverflow': ('CWE-120 · CWE-787', '-', '2001년 <b>Code Red 웜</b>이 IIS의 버퍼 오버플로우(CVE-2001-0500)를 악용해 수십만 대 서버를 감염시켰습니다.'),
 'codeinjection': ('CWE-94', 'A03 Injection', '2017년 <b>Equifax</b> 사고 — Apache Struts의 OGNL 코드 인젝션(CVE-2017-5638)으로 약 1.4억 명의 개인정보가 유출됐습니다.'),
 'cookiedisclosure': ('CWE-315 · CWE-539', '-', '2010년 <b>Firesheep</b> 확장으로 공개 와이파이에서 평문 세션 쿠키를 가로채 계정을 탈취하는 공격이 시연됐습니다.'),
 'csrf': ('CWE-352', 'A01 Broken Access Control', '2008년 <b>Gmail CSRF</b>로 피해자 몰래 메일 전달 필터가 추가돼 메일이 외부로 유출됐습니다.'),
 'dangerous_file_upload': ('CWE-434', 'A04 Insecure Design', '<b>웹쉘 업로드</b>는 국내외 웹사이트 침해의 대표 경로로, 이미지로 위장한 스크립트 파일 업로드 후 서버 장악이 반복적으로 발생했습니다.'),
 'debug_code': ('CWE-489', '-', '운영 환경에 남은 <b>디버그/테스트 엔드포인트</b>가 노출돼 인증을 우회하거나 내부 정보가 드러난 사례가 다수 보고됐습니다.'),
 'deserialization': ('CWE-502', 'A08 Software & Data Integrity', '2015년 <b>Apache Commons Collections</b> 자바 역직렬화 취약점으로 WebLogic·Jenkins 등 수많은 시스템에서 원격코드실행이 가능했습니다.'),
 'dns_security_decision': ('CWE-350', '-', '2008년 <b>Kaminsky DNS 캐시 포이즈닝</b>으로 DNS 응답을 신뢰한 시스템들이 위조 주소로 유도될 수 있었습니다.'),
 'error_handling_missing': ('CWE-391', '-', '예외를 처리하지 않아 서비스가 비정상 종료되거나 내부 상태가 노출되는 장애가 반복됐습니다.'),
 'error_message': ('CWE-209', 'A04 Insecure Design', '<b>상세 에러·스택트레이스 노출</b>로 DB 구조와 쿼리, 내부 경로가 공격자에게 드러난 사례가 흔합니다.'),
 'formatstring': ('CWE-134', '-', '2000년대 다수 유닉스 데몬이 <b>포맷스트링 취약점</b>으로 메모리 읽기·쓰기 및 코드 실행에 악용됐습니다.'),
 'hardedcode': ('CWE-798', 'A07 Identification & Auth Failures', '2016년 <b>Mirai 봇넷</b>이 IoT 기기의 하드코딩·기본 자격증명을 이용해 대규모 DDoS를 일으켰습니다.'),
 'http_split': ('CWE-113', '-', '<b>HTTP 응답분할</b>로 캐시 포이즈닝과 XSS가 유발돼 다른 사용자에게 변조된 페이지가 제공된 사례가 있습니다.'),
 'improper_auth_attempts': ('CWE-307', 'A07 Identification & Auth Failures', '<b>로그인 시도 제한 부재</b>는 크리덴셜 스터핑·무차별 대입의 핵심 원인으로, 다수 서비스의 대량 계정 탈취로 이어졌습니다.'),
 'improper_exception': ('CWE-248', '-', '부적절한 예외처리로 보안 점검이 우회되거나 비정상 흐름이 그대로 진행된 사례가 보고됐습니다.'),
 'improper_resource_release': ('CWE-772', '-', '자원(메모리·핸들·커넥션) 미해제가 누적돼 서비스가 고갈·다운되는 가용성 사고가 발생했습니다.'),
 'impropersignature': ('CWE-347', '-', '2012년 <b>Flame 멀웨어</b>가 위조된 MS 인증서로 서명 검증을 우회해 정상 업데이트로 위장했습니다.'),
 'impropersignature_validity': ('CWE-298 · CWE-324', '-', '인증서 만료·유효기간 검증을 생략해 폐기·만료된 인증서가 그대로 신뢰된 사례가 있습니다.'),
 'inapporiate_auth': ('CWE-285', 'A01 Broken Access Control', '<b>부적절한 인가</b>로 일반 사용자가 관리자 기능·타인 데이터에 접근하는 권한상승 사고가 반복됩니다.'),
 'infinite_loop': ('CWE-835', '-', '제어되지 않는 <b>무한 루프</b>로 CPU가 점유돼 서비스 거부(DoS)가 발생한 사례가 있습니다.'),
 'integer_overflow': ('CWE-190', '-', '2018년 다수 스마트컨트랙트가 <b>정수 오버플로우</b>(batchOverflow 등)로 토큰이 무단 발행·탈취됐습니다.'),
 'ldap_injection': ('CWE-90', 'A03 Injection', '<b>LDAP 인젝션</b>으로 인증을 우회하거나 디렉토리의 사용자 정보가 무단 조회된 사례가 있습니다.'),
 'missing_auth': ('CWE-306', 'A07 Identification & Auth Failures', '<b>인증 누락</b>으로 인터넷에 노출된 관리 콘솔·API가 무인증 접근돼 대량 데이터가 유출된 사고가 다수입니다.'),
 'no_encrypted_info': ('CWE-311', 'A02 Cryptographic Failures', '중요정보를 <b>평문 저장</b>한 DB가 유출돼 주민번호·카드번호가 그대로 노출된 사고가 반복됩니다.'),
 'nointegritycode': ('CWE-494', 'A08 Software & Data Integrity', '<b>무결성 검증 없는 코드/업데이트 다운로드</b>는 공급망 변조의 통로로, 정상 배포로 위장한 악성코드 유포에 악용됐습니다.'),
 'nosalthash': ('CWE-759 · CWE-916', 'A02 Cryptographic Failures', '2012년 <b>LinkedIn</b>의 솔트 없는 SHA-1 해시 650만 건이 유출돼 상당수가 빠르게 평문 복원됐습니다.'),
 'notenoughkey': ('CWE-326', 'A02 Cryptographic Failures', '짧은 키(512비트 RSA, 56비트 DES 등)는 현대 연산으로 해독 가능해 암호화가 사실상 무력화됩니다.'),
 'null_pointer': ('CWE-476', '-', '<b>Null 포인터 역참조</b>로 애플리케이션이 비정상 종료돼 서비스 거부가 발생한 사례가 있습니다.'),
 'open_redirect': ('CWE-601', 'A01 Broken Access Control', '<b>오픈 리다이렉트</b>가 피싱에 악용돼 정상 도메인 링크가 공격자 사이트로 사용자를 유도했습니다.'),
 'os_command': ('CWE-78', 'A03 Injection', '2014년 <b>Shellshock</b>(Bash, CVE-2014-6271)로 전 세계 서버에서 원격 OS 명령 실행이 가능했습니다.'),
 'path_traversal': ('CWE-22', 'A01 Broken Access Control', '<b>경로 조작</b>으로 ../ 입력을 통해 설정파일·인증정보 등 임의 파일이 읽힌 사고가 다수 보고됐습니다.'),
 'private_array_return': ('CWE-495', '-', 'Private 배열의 참조를 그대로 반환해 외부에서 내부 데이터를 변조할 수 있는 캡슐화 결함입니다.'),
 'processvalidation': ('CWE-841', '-', '거래·결제의 <b>처리 흐름 검증</b>이 미흡해 중간 단계를 건너뛰고 최종 승인에 도달하는 우회가 발생했습니다.'),
 'public_to_private_array': ('CWE-496', '-', 'Public 데이터를 Private 배열에 그대로 할당해 외부 입력이 내부 상태를 오염시킬 수 있습니다.'),
 'race_condition': ('CWE-362', '-', '2016년 <b>Dirty COW</b>(CVE-2016-5195) 리눅스 경쟁조건으로 일반 사용자가 root 권한을 획득할 수 있었습니다.'),
 'risky_crypto': ('CWE-327', 'A02 Cryptographic Failures', '2008년 <b>MD5 충돌</b>을 이용해 위조 CA 인증서가 생성되는 등 취약 알고리즘의 위험이 입증됐습니다.'),
 'sensitiveinfo_sourcecodecomments': ('CWE-615 · CWE-540', '-', '소스 주석·자바스크립트에 남은 <b>비밀번호·키·내부 URL</b>이 그대로 노출된 사례가 흔합니다.'),
 'session_data_exposure': ('CWE-488', '-', '세션 간 데이터가 격리되지 않아 한 사용자의 정보가 다른 사용자에게 노출된 사례가 있습니다.'),
 'sql_injection': ('CWE-89', 'A03 Injection', '2008년 <b>Heartland</b> SQL 인젝션으로 약 1억 건의 카드 정보가, 2015년 <b>TalkTalk</b>에서도 SQLi로 대량 고객정보가 유출됐습니다.'),
 'ssrf': ('CWE-918', 'A10 SSRF', '2019년 <b>Capital One</b> 사고 — SSRF로 클라우드 메타데이터의 자격증명을 탈취해 약 1억 건이 유출됐습니다.'),
 'uninitialized_variable': ('CWE-457', '-', '초기화되지 않은 변수의 잔류 메모리 값이 사용돼 정보 노출·예측불가 동작이 발생할 수 있습니다.'),
 'untrusted_input': ('CWE-20', 'A03 Injection', '<b>입력값 검증 미흡</b>은 거의 모든 인젝션 공격의 근원으로, 단일 결함이 광범위한 침해로 확대됩니다.'),
 'use_after_free': ('CWE-416', '-', '<b>해제 후 사용</b> 취약점은 브라우저·OS 원격코드실행의 단골 원인으로 다수 CVE가 보고됐습니다.'),
 'useofinsufficient_random': ('CWE-330 · CWE-338', 'A02 Cryptographic Failures', '2013년 안드로이드 <b>약한 난수</b> 결함으로 일부 비트코인 지갑의 개인키가 노출·탈취됐습니다.'),
 'vulnerable_api': ('CWE-477', '-', '폐기·취약한 API 사용은 알려진 결함을 그대로 떠안아 공격에 노출됩니다.'),
 'weakpassword': ('CWE-521', 'A07 Identification & Auth Failures', '<b>약한 비밀번호 정책</b>은 크리덴셜 스터핑의 성공률을 높여 대량 계정 탈취로 이어집니다.'),
 'wrong_auth': ('CWE-863', 'A01 Broken Access Control', '<b>잘못된 인가 결정</b>으로 권한 검증이 우회돼 타인 자원에 접근한 사고가 반복됩니다.'),
 'xml': ('CWE-91', 'A03 Injection', '<b>XML 인젝션</b>으로 질의·문서 구조가 변조돼 데이터 노출·우회가 발생했습니다.'),
 'xss': ('CWE-79', 'A03 Injection', '2005년 <b>Samy 웜</b>이 XSS로 24시간 만에 MySpace 친구 100만 명을 감염시켰고, 2018년 <b>British Airways</b>는 Magecart 스크립트로 38만 건의 카드정보가 탈취됐습니다.'),
 'xxe': ('CWE-611', 'A05 Security Misconfiguration', '<b>XXE</b>로 외부 엔터티를 통해 서버 내부 파일이 유출되거나 SSRF로 연결된 사례가 다수입니다.'),
}


def card(cwe, owasp, incident):
    owasp_html = ('<span class="rc-tag rc-owasp">OWASP %s</span>' % owasp) if owasp and owasp != '-' else ''
    return (
'<!-- REF-CARD -->\n'
'<div style="max-width:1000px;margin:18px auto 28px;padding:0 16px;font-family:\'Segoe UI\',Roboto,\'Malgun Gothic\',sans-serif;">\n'
'  <div style="border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,.06);">\n'
'    <div style="background:linear-gradient(90deg,#1e293b,#334155);color:#fff;padding:12px 18px;font-weight:700;font-size:15px;">📰 실제 사고사례 &amp; 표준 매핑</div>\n'
'    <div style="background:#fff;padding:16px 18px;color:#2c3e50;line-height:1.7;font-size:14.5px;">\n'
'      <div style="margin-bottom:12px;">%s</div>\n'
'      <div style="display:flex;gap:8px;flex-wrap:wrap;">\n'
'        <span class="rc-tag" style="background:#eef2ff;color:#4338ca;border:1px solid #c7d2fe;border-radius:20px;padding:4px 12px;font-size:12.5px;font-weight:700;font-family:monospace;">🏷️ %s</span>\n'
'        %s\n'
'      </div>\n'
'      <div style="margin-top:12px;font-size:12px;color:#94a3b8;">※ 공개적으로 알려진 사례 기반 교육용 요약 · CWE/OWASP는 공개 표준 분류</div>\n'
'    </div>\n'
'  </div>\n'
'</div>\n'
% (incident, cwe, owasp_html)).replace('class="rc-tag rc-owasp"',
   'style="background:#fff7ed;color:#c2410c;border:1px solid #fed7aa;border-radius:20px;padding:4px 12px;font-size:12.5px;font-weight:700;font-family:monospace;"')


def main():
    done = skip = miss = 0
    for key, (cwe, owasp, incident) in M.items():
        fn = '03_code_%s.html' % key
        path = os.path.join(PUB, fn)
        if not os.path.exists(path):
            print('MISSING FILE', fn); miss += 1; continue
        html = open(path, encoding='utf-8').read()
        if '<!-- REF-CARD -->' in html:
            skip += 1; continue
        if '</body>' not in html:
            print('NO BODY', fn); miss += 1; continue
        block = card(cwe, owasp, incident)
        html = html.replace('</body>', block + '</body>', 1)
        open(path, 'w', encoding='utf-8').write(html)
        done += 1
    # 매핑되지 않은 03_code 페이지 확인
    all_pages = [f for f in os.listdir(PUB) if re.match(r'03_code_.*\.html$', f)]
    mapped = {'03_code_%s.html' % k for k in M}
    unmapped = sorted(set(all_pages) - mapped)
    print('injected=%d skipped=%d missing=%d' % (done, skip, miss))
    if unmapped:
        print('UNMAPPED PAGES (%d):' % len(unmapped), ', '.join(unmapped))


if __name__ == '__main__':
    main()
