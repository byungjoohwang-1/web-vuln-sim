(function () {
  const KEY = 'wvs_lang';
  const LANGS = { ko: '한국어', en: 'EN' };

  const exact = new Map(Object.entries({
    '← 메인': '← Main',
    '한국어': 'Korean',
    '대시보드': 'Dashboard',
    '미션 보드': 'Mission Board',
    '종합 아카데미': 'Academy',
    '문제팩 학습': 'Question Packs',
    '문제팩': 'Question Packs',
    '콘텐츠 맵': 'Content Map',
    '오답노트': 'Wrong Notes',
    '클래스 입장': 'Classroom',
    '강사용 메뉴': 'Instructor',
    '문제 관리': 'Question Admin',
    '학습 트랙 선택 (홈)': 'Learning Track Home',
    '개발보안 학습 포털': 'Secure Development Portal',
    '진단원 학습 센터': 'Assessor Learning Center',
    '진단원 실전 훈련장': 'Assessor Training Arena',
    'C/C++ 코딩 표준 (MISRA·CERT·AUTOSAR)': 'C/C++ Coding Standards (MISRA, CERT, AUTOSAR)',
    '취약점': 'Vulnerability',
    '위험': 'Risk',
    '권장': 'Recommended',
    '대기중': 'Waiting',
    '초기화': 'Reset',
    '문의 등록': 'Submit Inquiry',
    '브라우저 실행 결과': 'Browser Output',
    '공격 진행 단계': 'Attack Stages',
    '방어 체크리스트': 'Defense Checklist',
    '취약한 코드': 'Vulnerable Code',
    '안전한 코드': 'Safe Code',
    '취약한 JSP 코드': 'Vulnerable JSP Code',
    '안전한 JSP 코드': 'Safe JSP Code',
    '고객명': 'Customer Name',
    '문의 내용': 'Inquiry Content',
    '고객센터 문의 게시판': 'Customer Support Board',
    '공격 시나리오': 'Attack Scenario',
    '시나리오': 'Scenario',
    '저장': 'Save',
    '실행': 'Run',
    '검사': 'Check',
    '진단': 'Diagnosis',
    '실습': 'Practice',
    '결과': 'Result',
    '해설': 'Explanation',
    '학습 진행도': 'Learning Progress',
    '진단 시작': 'Start Diagnosis',
    '안전': 'Safe',
    '취약': 'Vulnerable',
    '높음': 'High',
    '중간': 'Medium',
    '낮음': 'Low',
    '보안약점': 'Software Weakness',
    '평가기준': 'Assessment Criteria',
    /* WVS_INFRA_DICT */
    '📋 취약점 개요': '📋 Vulnerability Overview',
    '🖥️ 상태 비교 시뮬레이션': '🖥️ State Comparison Simulation',
    '🔧 조치 방법': '🔧 Remediation Steps',
    '✅ 점검 체크리스트': '✅ Inspection Checklist',
    '⚠️ 취약한 상태': '⚠️ Vulnerable State',
    '✅ 안전한 상태': '✅ Secure State',
    '🎯 직접 해보기 — 공격을 실행해 보세요': '🎯 Try It Yourself — Run the Attack',
    '💡 쉽게 말하면': '💡 In Simple Terms',
    '📋 설정 비교 (왜 막혔나?)': '📋 Configuration Comparison (Why Was It Blocked?)',
    '🛡️ 보안 조치 적용': '🛡️ Apply Security Hardening',
    '⚠️ 취약한 설정': '⚠️ Vulnerable Configuration',
    '✓ 안전한 설정': '✓ Secure Configuration',
    '✗ 취약한 설정': '✗ Vulnerable Configuration',
    '▶ 공격 실행': '▶ Run Attack',
    '공격 실행': 'Run Attack',
    '안전(조치 적용)': 'Secure (Hardened)',
    '현재: 취약한 설정 — 공격이 통할까요?': 'Current: Vulnerable configuration — will the attack succeed?',
    '# [공격 실행] 버튼을 누르면 시작합니다.': '# Press the [Run Attack] button to start.',
    '아래에서 시스템 상태를 ': 'Below, switch the system state to ',
    '으로 바꾼 뒤 ': ', then press ',
    '을 눌러, 같은 공격이 어떻게 다르게 끝나는지 직접 확인하세요.': ' to see how the same attack ends differently.',
    '주요정보통신기반시설 기술적 취약점 분석·평가 가이드(KISA) 기반 · 교육용 재구성': 'Based on the KISA Critical Information Infrastructure Technical Vulnerability Assessment Guide (reconstructed for education)',
    '⚖️ 컴플라이언스 위반 분석': '⚖️ Compliance Violation Analysis',
    '힌트(정답) 보기': 'Show Hint (Answer)',
    '코드 검증': 'Validate Code',
    '요청 전송': 'Send Request',
    '✅ 정상 거래': '✅ Normal Transaction',
    '❌ 여전히 취약함 (Vulnerable)': '❌ Still Vulnerable',
    '✅ 보안 조치 완료 (Secure)': '✅ Hardening Complete (Secure)',
  }));

  const terms = [
    /* WVS_INFRA_DICT */
    ['주요정보통신기반시설', 'Critical Information Infrastructure'],
    ['기술적 취약점 분석·평가', 'Technical Vulnerability Assessment'],
    ['교육 시뮬레이터', 'Training Simulator'],
    ['계정 잠금 임계값', 'Account Lockout Threshold'],
    ['계정 잠금', 'Account Lockout'],
    ['불필요한 계정 제거', 'Remove Unnecessary Accounts'],
    ['불필요한 서비스', 'Unnecessary Services'],
    ['원격 접속 제한', 'Remote Access Restriction'],
    ['비밀번호 관리정책 설정', 'Password Management Policy'],
    ['비밀번호 관리정책', 'Password Management Policy'],
    ['비밀번호 복잡도', 'Password Complexity'],
    ['비밀번호 복잡성', 'Password Complexity'],
    ['비밀번호 파일 보호', 'Password File Protection'],
    ['비밀번호 정책', 'Password Policy'],
    ['비밀번호 변경', 'Password Change'],
    ['파일 및 디렉터리 관리', 'File and Directory Management'],
    ['파일 및 디렉토리 관리', 'File and Directory Management'],
    ['파일 권한 설정', 'File Permission Settings'],
    ['파일 권한', 'File Permissions'],
    ['소유자 설정', 'Owner Configuration'],
    ['세션 타임아웃', 'Session Timeout'],
    ['로그인 실패', 'Login Failure'],
    ['접근 통제', 'Access Control'],
    ['최소 권한', 'Least Privilege'],
    ['권한 최소화', 'Privilege Minimization'],
    ['관리자 권한', 'Administrator Privileges'],
    ['권한 설정', 'Permission Settings'],
    ['보안 패치', 'Security Patch'],
    ['감사 정책', 'Audit Policy'],
    ['감사 기능', 'Audit Logging'],
    ['로그 기록', 'Logging'],
    ['시각 동기화', 'Time Synchronization'],
    ['서비스 비활성화', 'Service Disablement'],
    ['원격 관리', 'Remote Management'],
    ['기본 계정', 'Default Account'],
    ['익명 접근', 'Anonymous Access'],
    ['계정 관리', 'Account Management'],
    ['취약점', 'Vulnerability'],
    ['취약한 상태', 'Vulnerable State'],
    ['안전한 상태', 'Secure State'],
    ['취약한 설정', 'Vulnerable Configuration'],
    ['안전한 설정', 'Secure Configuration'],
    ['취약한', 'Vulnerable'],
    ['안전한', 'Secure'],
    ['관리자', 'Administrator'],
    ['디렉터리', 'Directory'],
    ['디렉토리', 'Directory'],
    ['비밀번호', 'Password'],
    ['이름 변경', 'Rename'],
    ['이름 바꾸기', 'Rename'],
    ['재설정', 'Reset'],
    ['비활성화', 'Disable'],
    ['활성화', 'Enable'],
    ['불필요한', 'Unnecessary'],
    ['미사용', 'Unused'],
    ['임계값', 'Threshold'],
    ['복잡도', 'Complexity'],
    ['세션', 'Session'],
    ['감사', 'Audit'],
    ['접근', 'Access'],
    ['통제', 'Control'],
    ['권한', 'Permission'],
    ['공유', 'Sharing'],
    ['소유자', 'Owner'],
    ['계정', 'Account'],
    ['방화벽', 'Firewall'],
    ['네트워크', 'Network'],
    ['서비스', 'Service'],
    ['시스템 상태', 'System State'],
    ['시스템', 'System'],
    ['서버', 'Server'],
    ['정책', 'Policy'],
    ['점검기준', 'Reference'],
    ['점검', 'Inspection'],
    ['설정', 'Configuration'],
    ['관리', 'Management'],
    ['상태', 'State'],
    ['위험도', 'Risk Level'],
    ['양호', 'Pass'],
    ['취약', 'Vulnerable'],
    ['전자금융기반시설 보안 취약점 평가기준', 'Electronic Financial Infrastructure Security Vulnerability Assessment Criteria'],
    ['크로스사이트 스크립팅', 'Cross-Site Scripting'],
    ['크로스 사이트 스크립트', 'Cross-Site Scripting'],
    ['SQL 삽입', 'SQL Injection'],
    ['코드 삽입', 'Code Injection'],
    ['경로 조작 및 삽입', 'Path Traversal and Injection'],
    ['경로 조작', 'Path Traversal'],
    ['OS 명령어 삽입', 'OS Command Injection'],
    ['위험한 형식 파일 업로드', 'Dangerous File Upload'],
    ['신뢰되지 않은 URL 접속', 'Untrusted URL Redirect'],
    ['XML 외부 개체 참조', 'XML External Entity Reference'],
    ['XML 삽입', 'XML Injection'],
    ['LDAP 삽입', 'LDAP Injection'],
    ['HTTP 응답분할', 'HTTP Response Splitting'],
    ['정수형 오버플로우', 'Integer Overflow'],
    ['버퍼오버플로우', 'Buffer Overflow'],
    ['포맷스트링 삽입', 'Format String Injection'],
    ['적절한 인증 없는 중요 기능', 'Missing Authentication for Critical Function'],
    ['부적절한 인가', 'Improper Authorization'],
    ['잘못된 권한 설정', 'Incorrect Permission Assignment'],
    ['취약한 암호화 알고리즘', 'Weak Cryptographic Algorithm'],
    ['암호화 되지 않은 중요 정보', 'Unencrypted Sensitive Information'],
    ['하드코드된 중요 정보', 'Hard-Coded Sensitive Information'],
    ['하드코드된 비밀번호', 'Hard-Coded Password'],
    ['충분하지 않은 키 길이', 'Insufficient Key Length'],
    ['적절하지 않은 난수 값', 'Insufficient Randomness'],
    ['취약한 비밀번호 허용', 'Weak Password Policy'],
    ['부적절한 전자서명 확인', 'Improper Signature Verification'],
    ['부적절한 인증서 유효성', 'Improper Certificate Validation'],
    ['쿠키를 통한 정보 노출', 'Information Exposure Through Cookies'],
    ['주석문 안 시스템 정보', 'System Information in Comments'],
    ['솔트 없는 일방향 해시', 'One-Way Hash Without Salt'],
    ['무결성 검사없는 코드 다운로드', 'Code Download Without Integrity Check'],
    ['반복 인증시도 제한 부재', 'Missing Login Attempt Limit'],
    ['경쟁조건', 'Race Condition'],
    ['종료되지 않는 반복·재귀', 'Uncontrolled Loop or Recursion'],
    ['오류메시지 정보노출', 'Error Message Information Exposure'],
    ['오류상황 대응 부재', 'Missing Error Handling'],
    ['부적절한 예외처리', 'Improper Exception Handling'],
    ['널 포인터 역참조', 'Null Pointer Dereference'],
    ['초기화되지 않은 변수', 'Uninitialized Variable'],
    ['자원 해제 누락', 'Missing Resource Release'],
    ['해제된 자원 사용', 'Use After Free'],
    ['프라이빗 배열 반환', 'Return of Private Array'],
    ['퍼블릭 데이터의 프라이빗 배열 저장', 'Storing Public Data in Private Array'],
    ['사용자 입력값', 'User Input'],
    ['입력값 필터링 미흡', 'Insufficient Input Filtering'],
    ['입력값', 'Input Value'],
    ['외부 입력값', 'External Input'],
    ['게시글이 표시됩니다', 'The post will be displayed here'],
    ['쿠키 탈취', 'Cookie Theft'],
    ['피싱 페이지', 'Phishing Page'],
    ['인터넷뱅킹 게시판 시스템', 'Internet Banking Board System'],
    ['고객센터', 'Customer Support'],
    ['문의하실 내용을 입력하세요', 'Enter your inquiry'],
    ['계좌이체가 안됩니다.', 'The account transfer is not working.'],
    ['공격자', 'Attacker'],
    ['사용자', 'User'],
    ['관리자', 'Administrator'],
    ['서버', 'Server'],
    ['데이터베이스', 'Database'],
    ['브라우저', 'Browser'],
    ['인증', 'Authentication'],
    ['인가', 'Authorization'],
    ['암호화', 'Encryption'],
    ['정보 노출', 'Information Exposure'],
    ['보안 기능', 'Security Function'],
    ['서비스 보호', 'Service Protection'],
    ['통제구분', 'Control Category'],
    ['위험도', 'Risk Level'],
    ['높음', 'High'],
    ['중간', 'Medium'],
    ['낮음', 'Low']
  ];

  function shouldSkip(node) {
    const p = node.parentElement;
    if (!p) return true;
    if (p.closest('[data-en], [data-i18n-en]')) return true;
    return ['SCRIPT', 'STYLE', 'CODE', 'PRE', 'TEXTAREA', 'INPUT', 'SELECT', 'OPTION'].includes(p.tagName);
  }

  function translateText(text) {
    const trimmed = text.trim();
    if (!trimmed) return text;
    if (exact.has(trimmed)) return text.replace(trimmed, exact.get(trimmed));
    let out = text;
    terms.forEach(([ko, en]) => {
      out = out.split(ko).join(en);
    });
    return out;
  }

  function ensureOriginal(el) {
    if (!el.dataset.wvsKo) el.dataset.wvsKo = el.textContent;
  }

  function translateElementData(el, lang) {
    const enText = el.dataset.en !== undefined ? el.dataset.en
                 : (el.dataset.i18nEn !== undefined ? el.dataset.i18nEn : undefined);
    if (enText !== undefined) {
      if (/[<>]/.test(enText)) {
        // value contains HTML markup -> swap innerHTML so tags are not shown as text
        if (el.dataset.wvsKoHtml === undefined) el.dataset.wvsKoHtml = el.innerHTML;
        el.innerHTML = lang === 'en' ? enText : el.dataset.wvsKoHtml;
      } else {
        ensureOriginal(el);
        el.textContent = lang === 'en' ? enText : el.dataset.wvsKo;
      }
    }
    if (el.dataset.enTitle) {
      if (!el.dataset.wvsTitle) el.dataset.wvsTitle = el.getAttribute('title') || '';
      el.setAttribute('title', lang === 'en' ? el.dataset.enTitle : el.dataset.wvsTitle);
    }
    if (el.dataset.enPlaceholder) {
      if (!el.dataset.wvsPlaceholder) el.dataset.wvsPlaceholder = el.getAttribute('placeholder') || '';
      el.setAttribute('placeholder', lang === 'en' ? el.dataset.enPlaceholder : el.dataset.wvsPlaceholder);
    }
  }

  function translateTextNodes(lang) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (shouldSkip(node)) return NodeFilter.FILTER_REJECT;
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      if (!node.__wvsKo) node.__wvsKo = node.nodeValue;
      const ko = node.__wvsKo;
      node.nodeValue = lang === 'en' ? translateText(ko) : ko;
    });
  }

  function translateAttributes(lang) {
    document.querySelectorAll('input[placeholder], textarea[placeholder], [title]').forEach(el => {
      if (el.placeholder !== undefined) {
        if (!el.dataset.wvsPhKo) el.dataset.wvsPhKo = el.getAttribute('placeholder') || '';
        el.setAttribute('placeholder', lang === 'en' ? translateText(el.dataset.wvsPhKo) : el.dataset.wvsPhKo);
      }
      if (el.hasAttribute('title')) {
        if (!el.dataset.wvsTitleKo) el.dataset.wvsTitleKo = el.getAttribute('title') || '';
        el.setAttribute('title', lang === 'en' ? translateText(el.dataset.wvsTitleKo) : el.dataset.wvsTitleKo);
      }
    });
  }

  function updateButtons(lang) {
    document.querySelectorAll('[data-wvs-lang]').forEach(btn => {
      btn.classList.toggle('on', btn.dataset.wvsLang === lang);
      btn.setAttribute('aria-pressed', btn.dataset.wvsLang === lang ? 'true' : 'false');
    });
    const ko = document.getElementById('lang-ko');
    const en = document.getElementById('lang-en');
    if (ko) ko.classList.toggle('on', lang === 'ko');
    if (en) en.classList.toggle('on', lang === 'en');
  }

  function applyLang(lang) {
    const next = lang === 'en' ? 'en' : 'ko';
    localStorage.setItem(KEY, next);
    localStorage.setItem('lang', next);
    document.documentElement.lang = next;
    document.querySelectorAll('[data-en], [data-i18n-en], [data-en-title], [data-en-placeholder]').forEach(el => translateElementData(el, next));
    translateTextNodes(next);
    translateAttributes(next);
    updateButtons(next);
    /* 공용 크롬(탑바·설치 배너 등)은 자체 스크립트가 그리므로 알려서 다시 그리게 한다. */
    try { document.dispatchEvent(new CustomEvent('wvs:lang', { detail: { lang: next } })); } catch (e) { /* no-op */ }
    notifyUntranslated(next);
  }

  /* ── 번역 안 된 페이지에서 EN 을 고른 경우 정직하게 알린다 ──
     사이트 전체 커버리지가 낮은데 토글만 보여주면 "영어를 지원한다"는 거짓 약속이 된다.
     본문에 data-en/data-i18n 이 거의 없으면 안내를 띄운다(내비게이션은 계속 영어로 동작). */
  function pageHasTranslation() {
    if (document.querySelector('[data-i18n], [data-i18n-html]')) return true;   /* 사전 기반 페이지 */
    return document.querySelectorAll('[data-en]').length >= 8;
  }
  function notifyUntranslated(lang) {
    const id = 'wvs-i18n-notice';
    const old = document.getElementById(id);
    if (lang !== 'en' || pageHasTranslation()) { if (old) old.remove(); return; }
    if (old) return;
    const n = document.createElement('div');
    n.id = id;
    n.setAttribute('role', 'status');
    n.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);bottom:16px;z-index:var(--wvs-z-toast,1000);' +
      'max-width:min(560px,92vw);background:rgba(20,20,30,.94);color:#e2e8f0;border:1px solid #475569;' +
      'border-radius:10px;padding:10px 14px;font:500 13px/1.5 system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.4)';
    n.innerHTML = 'This page is available in <b>Korean only</b> for now — the security guidance is not machine-translated ' +
      'to avoid inaccuracies. Navigation stays in English. ' +
      '<button type="button" style="margin-left:8px;background:#334155;border:0;color:#e2e8f0;border-radius:6px;padding:3px 9px;cursor:pointer">Dismiss</button>';
    n.querySelector('button').addEventListener('click', () => n.remove());
    document.body.appendChild(n);
    setTimeout(() => { if (n.parentNode) n.remove(); }, 9000);
  }

  function ensureStyle() {
    if (document.getElementById('wvs-bilingual-style')) return;
    const style = document.createElement('style');
    style.id = 'wvs-bilingual-style';
    style.textContent = `
      /* 공통 상단 바(soc-chrome .wvsx-top)가 있으면 그 아래로 내려간다. 예전에는 top 이
         --wvs-edge(14px) 라 바 우측의 🔍검색 버튼 위에 그대로 얹혀서 검색을 누르면
         언어 버튼이 눌렸다(데스크톱에서 재현). --wvs-topbar-h 는 바가 실제로 만들어진
         뒤 soc-chrome 이 채우며, 바가 없는 페이지에서는 0px 로 떨어져 종전과 같다. */
      .wvs-langbar{position:fixed;top:calc(var(--wvs-topbar-h, 0px) + var(--wvs-edge,14px));right:var(--wvs-edge,14px);z-index:var(--wvs-z-float,300);display:flex;align-items:center;gap:4px;background:rgba(20,20,30,.78);padding:4px;border-radius:9px;box-shadow:0 2px 10px rgba(0,0,0,.32);backdrop-filter:blur(8px);transition:opacity .18s ease;height:auto;max-height:36px;box-sizing:border-box}
      .wvs-langbar button,.langbar button{border:0;padding:5px 11px;border-radius:7px;font:700 12px/1 'Malgun Gothic',Arial,sans-serif;cursor:pointer;white-space:nowrap;height:24px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center}
      .wvs-langbar button{background:transparent;color:#cbd5e1}
      .wvs-langbar button.on,.langbar button.on{background:#2563eb!important;color:#fff!important}
      /* 고정 배치라 스크롤한 본문 위에 계속 떠서 글자를 가린다(예: AI 페이지의 상태 줄).
         맨 위를 벗어나면 흐려지고 클릭을 통과시키며, 마우스/키보드로 다가오면 즉시 복구한다. */
      .wvs-langbar.wvs-dim{opacity:.28;pointer-events:none}
      /* 버튼만 클릭을 받으므로 여백은 아래 본문으로 통과되고, 버튼에 hover 하면
         조상인 바에도 :hover 가 걸려 다시 선명해진다. */
      .wvs-langbar.wvs-dim button{pointer-events:auto}
      .wvs-langbar.wvs-dim:hover,.wvs-langbar.wvs-dim:focus-within{opacity:1}
      @media (max-width:768px){
        .wvs-langbar{display:none!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important}
      }
      @media (prefers-reduced-motion:reduce){.wvs-langbar{transition:none}}
    `;
    document.head.appendChild(style);
  }

  function ensureBar() {
    ensureStyle();
    if (document.querySelector('.langbar')) {
      document.querySelectorAll('.langbar button').forEach(btn => {
        const text = btn.textContent.trim().toLowerCase();
        btn.dataset.wvsLang = text.includes('en') ? 'en' : 'ko';
        btn.addEventListener('click', () => setTimeout(() => applyLang(btn.dataset.wvsLang), 0), true);
      });
      return;
    }
    // 모바일 스마트폰(화면 폭 768px 이하)에서는 화면을 가리는 고정 플로팅 바를 생성하지 않음
    if (window.innerWidth <= 768) return;
    if (document.querySelector('.wvs-langbar')) return;
    const bar = document.createElement('div');
    bar.className = 'wvs-langbar';
    bar.setAttribute('aria-label', 'Language selector');
    bar.innerHTML = Object.entries(LANGS).map(([code, label]) =>
      `<button type="button" data-wvs-lang="${code}" onclick="window.WVS_BILINGUAL.setLang('${code}')">${label}</button>`
    ).join('');
    document.body.appendChild(bar);
    bindDim(bar);
    window.addEventListener('resize', () => {
      bar.style.display = window.innerWidth <= 768 ? 'none' : 'flex';
    });
  }

  /* 맨 위에서 벗어나면 언어 바를 흐리게 해 본문을 가리지 않도록 한다.
     rAF 로 미루면 탭이 숨겨져 있을 때(백그라운드·미렌더링 창) 콜백이 멈춰
     상태가 낡은 채로 남는다. 토글 자체가 가벼우니 시간 기반으로 직접 처리하고,
     다시 보이게 될 때 한 번 더 맞춘다. */
  function bindDim(bar) {
    let last = 0;
    const update = () => {
      last = Date.now();
      const y = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
      bar.classList.toggle('wvs-dim', y > 60);
    };
    let pending = null;
    window.addEventListener('scroll', () => {
      const since = Date.now() - last;
      if (since >= 80) { update(); return; }
      if (pending) return;
      pending = setTimeout(() => { pending = null; update(); }, 80 - since);
    }, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') update();
    });
    update();
  }

  window.WVS_BILINGUAL = { setLang: applyLang };

  document.addEventListener('DOMContentLoaded', () => {
    ensureBar();
    const params = new URLSearchParams(location.search);
    const initial = params.get('lang') || localStorage.getItem(KEY) || localStorage.getItem('lang') || 'ko';
    applyLang(initial);
  });
})();
