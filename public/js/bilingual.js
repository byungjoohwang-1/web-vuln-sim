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
    '평가기준': 'Assessment Criteria'
  }));

  const terms = [
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
  }

  function ensureStyle() {
    if (document.getElementById('wvs-bilingual-style')) return;
    const style = document.createElement('style');
    style.id = 'wvs-bilingual-style';
    style.textContent = `
      .wvs-langbar{position:fixed;top:12px;right:12px;z-index:100000;display:flex;gap:4px;background:rgba(20,20,30,.78);padding:4px;border-radius:9px;box-shadow:0 2px 10px rgba(0,0,0,.32);backdrop-filter:blur(8px)}
      .wvs-langbar button,.langbar button{border:0;padding:6px 11px;border-radius:7px;font:700 12px/1 'Malgun Gothic',Arial,sans-serif;cursor:pointer}
      .wvs-langbar button{background:transparent;color:#cbd5e1}
      .wvs-langbar button.on,.langbar button.on{background:#2563eb!important;color:#fff!important}
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
    if (document.querySelector('.wvs-langbar')) return;
    const bar = document.createElement('div');
    bar.className = 'wvs-langbar';
    bar.setAttribute('aria-label', 'Language selector');
    bar.innerHTML = Object.entries(LANGS).map(([code, label]) =>
      `<button type="button" data-wvs-lang="${code}" onclick="window.WVS_BILINGUAL.setLang('${code}')">${label}</button>`
    ).join('');
    document.body.appendChild(bar);
  }

  window.WVS_BILINGUAL = { setLang: applyLang };

  document.addEventListener('DOMContentLoaded', () => {
    ensureBar();
    const params = new URLSearchParams(location.search);
    const initial = params.get('lang') || localStorage.getItem(KEY) || localStorage.getItem('lang') || 'ko';
    applyLang(initial);
  });
})();
