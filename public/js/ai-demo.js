/* ai-demo.js - 키 없는 데모 튜터 엔진 (AI 개편안 A-01, A-03, A-06)
 *
 * 왜 규칙 기반인가
 *   학습자가 API 키를 브라우저에 넣지 않아도 AI 트랙의 핵심 흐름을 끝까지
 *   체험할 수 있어야 한다. 그래서 데모 모드는 외부 호출을 하지 않고,
 *   이미 사이트가 들고 있는 학습 데이터(ACADEMY_DATA.CONCEPTS)로 답을 구성한다.
 *
 * 무엇을 보장하는가
 *   1. 주제 1개를 개념부터 진단 포인트까지 설명한다.
 *   2. 코드 리뷰 힌트를 1단계에서 3단계까지 단계적으로 준다. 정답을 먼저 말하지 않는다.
 *   3. 악용 요청(실제 타깃 공격, 페이로드 제작 대행)은 거부하고 방어 관점으로 돌린다.
 *
 * 한계도 화면에 밝힌다. 데모는 정해진 자료를 조합할 뿐 추론하지 않는다.
 */
(function () {
  'use strict';

  function isEn() {
    try {
      return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en';
    } catch (e) { return false; }
  }
  function L(ko, en) { return isEn() ? en : ko; }

  /* ---------- 의도 판별 ---------- */

  /* 악용 요청. 방어 학습이 아니라 실제 공격 수행을 시키려는 표현을 본다. */
  var ABUSE = [
    /실제\s*(사이트|서버|타깃|대상|기업|고객사)/,
    /(해킹|침투|공격)\s*(해줘|해\s*줘|해\s*주세요|대행|의뢰)/,
    /(우회|bypass)\s*(페이로드|코드|스크립트)\s*(만들|생성|짜)/,
    /(waf|방화벽|백신|edr)\s*(우회|회피)/i,
    /(랜섬웨어|악성코드|멀웨어|키로거|백도어|봇넷)\s*(만들|제작|작성|코드)/,
    /(exploit|익스플로잇)\s*(만들|제작|작성)/i,
    /(계정|비밀번호|세션)\s*(탈취|훔)/,
    /무단|허가\s*없이|동의\s*없이/
  ];
  function isAbuse(t) {
    for (var i = 0; i < ABUSE.length; i++) { if (ABUSE[i].test(t)) return true; }
    return false;
  }

  var INTENTS = [
    ['hint',    /힌트|hint|단서|모르겠|막혔|어디부터/i],
    ['answer',  /정답|답\s*알려|정확히\s*알려|answer|solution|바로\s*알려/i],
    ['review',  /리뷰|검토|점검|봐\s*줘|review|check\s*my|이\s*코드|아래\s*코드/i],
    ['example', /예시|샘플|example|sample|코드\s*보여|비교/i],
    ['quiz',    /퀴즈|문제\s*내|연습\s*문제|quiz|test\s*me/i],
    ['diag',    /진단|탐지|찾는\s*법|찾으려|패턴|어떻게\s*발견|어디를\s*봐|diagnos|detect|spot/i],
    ['fix',     /고치|고쳐|고침|수정|조치|대응|방어|막는|막을|막으려|해결|안전하게|fix|remediat|mitigat|secure|harden/i],
    ['explain', /설명|뭐야|무엇|개념|알려\s*줘|explain|what\s+is|why/i]
  ];
  function intentOf(t) {
    for (var i = 0; i < INTENTS.length; i++) {
      if (INTENTS[i][1].test(t)) return INTENTS[i][0];
    }
    return 'explain';
  }

  /* ---------- 코드 냄새 규칙 ----------
     붙여넣은 코드에서 눈에 띄는 위험 패턴을 찾는다.
     정적 분석이 아니라 교육용 신호다. 놓치는 것이 있을 수 있다고 화면에 밝힌다. */
  var SMELLS = [
    { id: 'sqli', cwe: 'CWE-89',
      re: /(select|insert|update|delete)[^\n;]{0,120}(\+\s*\w+|\$\{|%s['"]?\s*%|f["'].*\{)/i,
      ko: 'SQL 문자열을 값과 이어 붙이고 있다', en: 'SQL built by string concatenation',
      fixKo: '바인딩 변수(PreparedStatement, 파라미터화 쿼리)로 바꾼다',
      fixEn: 'switch to bound parameters (PreparedStatement, parameterized query)' },
    { id: 'cmd', cwe: 'CWE-78',
      re: /(Runtime\.getRuntime\(\)\.exec|ProcessBuilder|os\.system|subprocess\.\w+\([^)]*shell\s*=\s*True|exec\s*\()/,
      ko: '외부 입력이 셸 명령으로 들어갈 수 있다', en: 'external input may reach a shell command',
      fixKo: '셸을 거치지 않는 배열 인자 실행으로 바꾸고 허용 목록으로 검증한다',
      fixEn: 'run without a shell using an argument array, and validate against an allow list' },
    { id: 'xss', cwe: 'CWE-79',
      re: /(innerHTML|document\.write|dangerouslySetInnerHTML|\|\s*safe\b|v-html)/,
      ko: '사용자 값이 HTML 로 해석되는 자리에 들어간다', en: 'user value lands where HTML is parsed',
      fixKo: 'textContent 로 넣거나 출력 인코딩을 적용한다',
      fixEn: 'assign via textContent or apply output encoding' },
    { id: 'secret', cwe: 'CWE-798',
      re: /(password|passwd|secret|api[_-]?key|token|private[_-]?key)\s*[:=]\s*["'][^"']{6,}["']/i,
      ko: '비밀값이 소스에 문자열로 박혀 있다', en: 'a secret is hardcoded as a string literal',
      fixKo: '환경 변수나 비밀 관리 서비스로 옮기고, 노출된 값은 즉시 폐기한다',
      fixEn: 'move it to an environment variable or a secret manager, and rotate the exposed value' },
    { id: 'crypto', cwe: 'CWE-327',
      re: /\b(MD5|SHA-?1|DES|RC4|ECB)\b/i,
      ko: '깨진 것으로 알려진 암호 알고리즘을 쓰고 있다', en: 'a broken cryptographic algorithm is in use',
      fixKo: '해시는 SHA-256 이상, 암호화는 AES-GCM 같은 인증 암호를 쓴다',
      fixEn: 'use SHA-256 or stronger for hashing, and an authenticated cipher such as AES-GCM' },
    { id: 'random', cwe: 'CWE-330',
      re: /(Math\.random|new\s+Random\s*\(|random\.randint|rand\s*\(\s*\))/,
      ko: '예측 가능한 난수를 보안 목적에 쓰고 있다', en: 'a predictable RNG is used for a security purpose',
      fixKo: 'SecureRandom, secrets, crypto.getRandomValues 로 바꾼다',
      fixEn: 'switch to SecureRandom, secrets, or crypto.getRandomValues' },
    { id: 'path', cwe: 'CWE-22',
      re: /(new\s+File\s*\(|open\s*\(|readFile\w*\s*\()[^)]*(\+|\$\{|%s|f["'])/,
      ko: '입력값이 파일 경로에 그대로 섞인다', en: 'input is spliced straight into a file path',
      fixKo: '정규화 후 기준 디렉터리 안에 있는지 검사하거나 화이트리스트 식별자를 쓴다',
      fixEn: 'canonicalize and confirm the path stays under a base directory, or use whitelisted identifiers' },
    { id: 'deser', cwe: 'CWE-502',
      re: /(ObjectInputStream|readObject\s*\(|pickle\.loads|yaml\.load\s*\((?![^)]*Safe)|unserialize\s*\()/,
      ko: '신뢰할 수 없는 데이터를 역직렬화한다', en: 'untrusted data is deserialized',
      fixKo: 'JSON 같은 데이터 전용 형식을 쓰거나 허용 클래스를 제한한다',
      fixEn: 'use a data-only format such as JSON, or restrict the allowed classes' },
    { id: 'verify', cwe: 'CWE-295',
      re: /(verify\s*=\s*False|InsecureRequestWarning|ALLOW_ALL_HOSTNAME|TrustAllCerts|rejectUnauthorized\s*:\s*false)/i,
      ko: '인증서 검증을 꺼 두었다', en: 'certificate validation is disabled',
      fixKo: '검증을 켜고, 사설 CA 는 신뢰 저장소에 등록한다',
      fixEn: 'turn validation back on and register a private CA in the trust store' },
    { id: 'log', cwe: 'CWE-532',
      re: /(console\.log|System\.out\.print\w*|print\s*\(|logger?\.\w+)\s*\([^)]*(password|token|secret|카드|주민)/i,
      ko: '민감한 값이 로그로 나간다', en: 'a sensitive value is written to a log',
      fixKo: '마스킹하거나 로그에서 제외한다', fixEn: 'mask it or keep it out of the log' }
  ];

  function looksLikeCode(t) {
    if (t.indexOf('```') >= 0) return true;
    var hits = 0;
    if (/[;{}]/.test(t)) hits++;
    if (/\b(function|def|class|public|private|var|let|const|import|SELECT|if\s*\()/i.test(t)) hits++;
    if (t.split('\n').length >= 3) hits++;
    return hits >= 2;
  }

  function findSmells(t) {
    var out = [];
    for (var i = 0; i < SMELLS.length; i++) {
      if (SMELLS[i].re.test(t)) out.push(SMELLS[i]);
    }
    return out;
  }

  /* ---------- 응답 조립 ---------- */

  function bullet(items) { return items.map(function (s) { return '- ' + s; }).join('\n'); }

  function refusal() {
    return L(
      '그 요청은 도와드릴 수 없습니다. 이 사이트는 실제 시스템을 공격하는 방법이 아니라, ' +
      '공격이 왜 통하는지 이해하고 막는 방법을 배우는 곳입니다.\n\n' +
      '대신 이렇게 바꿔 볼 수 있어요.\n' +
      bullet([
        '"이 취약점이 왜 생기는지 설명해줘"',
        '"아래 코드에서 위험한 부분을 찾도록 힌트를 줘"',
        '"이 코드를 안전하게 고치는 방법을 알려줘"'
      ]) +
      '\n\n실습은 모두 이 페이지 안에서 동작하는 모의 환경입니다. 외부 시스템을 대상으로 시도하지 마세요.',

      'I cannot help with that. This site teaches why attacks work and how to stop them, ' +
      'not how to attack real systems.\n\nTry asking instead:\n' +
      bullet([
        '"Explain why this weakness happens"',
        '"Give me a hint to find the risky part of this code"',
        '"How do I fix this safely?"'
      ]) +
      '\n\nEvery lab here is a mock running inside the page. Do not point it at systems you do not own.'
    );
  }

  function noTopic() {
    return L(
      '어떤 약점을 볼까요? 위의 **주제** 선택 상자에서 하나 고르면 그 약점에 맞춰 설명합니다.\n\n' +
      '코드를 검토받고 싶다면 아래 입력창에 붙여넣고 "리뷰해줘" 라고 적어 주세요. ' +
      '정답을 먼저 말하지 않고 힌트를 1단계부터 드립니다.',

      'Which weakness should we look at? Pick one from the **topic** selector above and I will tailor the explanation.\n\n' +
      'To get code reviewed, paste it below and say "review". I give hints starting at level 1 instead of the answer.'
    );
  }

  function explain(c) {
    return L(
      '### [' + c.cwe + '] ' + c.name + '\n\n' +
      '**무엇인가**\n' + c.desc + '\n\n' +
      '**왜 위험한가**\n' + c.risk + '\n\n' +
      '**안전한 처리**\n' + c.safe + '\n\n' +
      '다음으로 "진단 포인트" 나 "안전한 코드 예시" 를 물어보세요.',

      '### [' + c.cwe + '] ' + c.name + '\n\n' +
      '**What it is**\n' + c.desc + '\n\n' +
      '**Why it matters**\n' + c.risk + '\n\n' +
      '**Safe handling**\n' + c.safe + '\n\n' +
      'Next, ask about "diagnosis points" or "a safe code example".'
    );
  }

  function diag(c) {
    return L(
      '**[' + c.cwe + '] 진단 포인트**\n\n' + c.diag + '\n\n' +
      '코드 리뷰에서는 보통 이 순서로 봅니다.\n' +
      bullet([
        '입력이 들어오는 지점을 먼저 찾는다 (요청 파라미터, 파일, 외부 API 응답)',
        '그 값이 어디까지 흘러가는지 따라간다 (질의문, 파일 경로, 명령어, 화면 출력)',
        '흘러간 자리에서 값이 코드로 해석되는지 본다',
        '검증과 인코딩이 그 사이 어디에 있는지 확인한다'
      ]),

      '**[' + c.cwe + '] diagnosis points**\n\n' + c.diag + '\n\n' +
      'In review, the usual order is:\n' +
      bullet([
        'find where input enters (request parameters, files, third-party responses)',
        'follow where that value flows (queries, file paths, commands, rendered output)',
        'check whether the value is interpreted as code at the destination',
        'see where validation and encoding sit along that path'
      ])
    );
  }

  function fix(c) {
    return L(
      '**[' + c.cwe + '] 안전한 처리**\n\n' + c.safe + '\n\n' +
      '적용할 때 같이 확인할 것.\n' +
      bullet([
        '한 곳만 고치지 말고 같은 패턴을 코드 전체에서 찾는다',
        '수정 후 실패 사례(거부되어야 할 입력)로 검증한다',
        '프레임워크가 이미 제공하는 안전한 API 가 있는지 먼저 본다'
      ]),

      '**[' + c.cwe + '] safe handling**\n\n' + c.safe + '\n\n' +
      'While applying it:\n' +
      bullet([
        'search the whole codebase for the same pattern instead of patching one spot',
        'verify with inputs that should now be rejected',
        'check whether the framework already ships a safe API for this'
      ])
    );
  }

  function quiz(c) {
    return L(
      '**연습 문제 [' + c.cwe + ']**\n\n' +
      '1. 이 약점이 실제로 성립하려면 어떤 조건 두 가지가 동시에 필요할까요?\n' +
      '2. 아래 중 이 약점의 근본 해결책은 무엇일까요?\n' +
      '   a) 위험한 문자를 목록으로 막는다\n' +
      '   b) 값과 코드를 구조적으로 분리한다\n' +
      '   c) 오류 메시지를 숨긴다\n\n' +
      '생각한 답을 적어 주세요. 맞는지 같이 봅니다. ' +
      '(참고: 차단 목록은 항상 빠뜨리는 것이 생기고, 오류 숨김은 증상만 가립니다.)',

      '**Practice [' + c.cwe + ']**\n\n' +
      '1. Which two conditions must hold at the same time for this weakness to be real?\n' +
      '2. Which is the root fix?\n' +
      '   a) block dangerous characters with a deny list\n' +
      '   b) structurally separate data from code\n' +
      '   c) hide the error message\n\n' +
      'Write your answer and we will check it together. ' +
      '(Hint: deny lists always miss something, and hiding errors only masks the symptom.)'
    );
  }

  /* 코드 리뷰 힌트 사다리. 정답을 먼저 말하지 않는 것이 이 모드의 목표다. */
  function reviewHint(smells, step, hasCode) {
    if (!hasCode) {
      return L(
        '검토할 코드를 입력창에 붙여넣어 주세요. 언어는 상관없습니다.\n\n' +
        '붙여넣으면 1단계 힌트부터 시작해서, "힌트" 를 다시 요청할 때마다 한 단계씩 구체적으로 짚어 드립니다.',
        'Paste the code you want reviewed. Any language is fine.\n\n' +
        'I start at hint level 1 and get more specific each time you ask for another hint.'
      );
    }
    if (!smells.length) {
      return L(
        '규칙 기반 데모라서 제가 아는 패턴 안에서만 찾습니다. 눈에 띄는 위험 패턴은 없었습니다.\n\n' +
        '다만 "패턴이 없다" 가 "안전하다" 는 아닙니다. 직접 확인해 보세요.\n' +
        bullet([
          '이 코드로 들어오는 값 중 사용자가 정하는 것은 무엇인가',
          '그 값이 질의문, 경로, 명령, 화면 중 어디에 닿는가',
          '권한 검사는 누가, 어느 시점에 하는가',
          '실패했을 때 무엇이 로그와 화면에 남는가'
        ]) +
        '\n\n더 정밀한 검토는 로그인 후 서버 프록시 모드나 개인 키 모드에서 받을 수 있습니다.',

        'This demo matches a fixed rule set, and none of its patterns fired here.\n\n' +
        'No match does not mean safe. Check these yourself:\n' +
        bullet([
          'which incoming values does the user control',
          'where do those values land: query, path, command, or rendered output',
          'who checks authorization, and at what point',
          'what ends up in logs and on screen when it fails'
        ]) +
        '\n\nFor a deeper review, sign in for proxy mode or use personal-key mode.'
      );
    }

    var s = smells[0];
    var more = smells.length > 1
      ? L('\n\n(이 밖에 ' + (smells.length - 1) + '개 지점이 더 걸렸습니다. 이것부터 정리하고 이어서 봅시다.)',
          '\n\n(' + (smells.length - 1) + ' more spots matched. Let us clear this one first.)')
      : '';

    if (step <= 1) {
      return L(
        '**힌트 1/3 : 어느 영역인가**\n\n' +
        '입력이 코드로 해석되는 자리가 있습니다. 분류로 보면 **' + s.cwe + '** 계열입니다.\n\n' +
        '코드를 다시 읽으면서, 사용자가 정할 수 있는 값이 실행 문맥(질의문, 명령, 경로, HTML)에 ' +
        '그대로 닿는 곳을 찾아보세요.\n\n"힌트" 를 한 번 더 요청하면 2단계로 좁혀 드립니다.' + more,

        '**Hint 1 of 3: which area**\n\n' +
        'Somewhere input is interpreted as code. By category this is the **' + s.cwe + '** family.\n\n' +
        'Read the code again and look for a user-controlled value reaching an execution context ' +
        '(query, command, path, HTML).\n\nAsk for another hint to narrow it down.' + more
      );
    }
    if (step === 2) {
      return L(
        '**힌트 2/3 : 어느 줄인가**\n\n' +
        '문제가 되는 지점의 특징은 이것입니다: ' + s.ko + '.\n\n' +
        '그 줄을 찾았다면, 그 자리에서 값과 구문이 어떻게 섞이는지 손으로 적어 보세요. ' +
        '값이 따옴표를 벗어나거나 구분자 역할을 하게 되는 순간이 공격 지점입니다.\n\n' +
        '"힌트" 를 한 번 더 요청하면 고치는 방향을 알려 드립니다.' + more,

        '**Hint 2 of 3: which line**\n\n' +
        'The giveaway is: ' + s.en + '.\n\n' +
        'Once you find that line, write out by hand how the value and the syntax mix there. ' +
        'The attack starts the moment a value can escape its quotes or act as a delimiter.\n\n' +
        'Ask once more and I will point at the fix.' + more
      );
    }
    return L(
      '**힌트 3/3 : 고치는 방향**\n\n' +
      '진단: ' + s.ko + ' (' + s.cwe + ')\n\n' +
      '조치: ' + s.fixKo + '.\n\n' +
      '고친 뒤 이렇게 확인하세요.\n' +
      bullet([
        '정상 입력이 여전히 통과하는가',
        '공격 형태의 입력이 값으로만 취급되는가 (오류가 아니라 값으로)',
        '같은 패턴이 다른 파일에도 있는가'
      ]) +
      '\n\n고친 코드를 붙여넣고 "리뷰해줘" 라고 하면 다시 봐 드립니다.' + more,

      '**Hint 3 of 3: the fix**\n\n' +
      'Finding: ' + s.en + ' (' + s.cwe + ')\n\n' +
      'Action: ' + s.fixEn + '.\n\n' +
      'After fixing, confirm:\n' +
      bullet([
        'valid input still works',
        'attack-shaped input is treated as data, not as an error',
        'the same pattern does not survive in other files'
      ]) +
      '\n\nPaste the fixed code and say "review" for another pass.' + more
    );
  }

  function answerNow(c, smells, hasCode) {
    if (hasCode && smells.length) {
      var lines = smells.map(function (s) {
        return '**' + s.cwe + '** ' + (isEn() ? s.en : s.ko) + '\n  -> ' + (isEn() ? s.fixEn : s.fixKo);
      });
      return L('요청하셔서 바로 정리합니다.\n\n' + lines.join('\n\n') +
               '\n\n규칙 기반 데모라 놓친 것이 있을 수 있습니다. 최종 판단은 직접 하세요.',
               'Here it is directly.\n\n' + lines.join('\n\n') +
               '\n\nThis is a fixed rule set, so it can miss things. Make the final call yourself.');
    }
    if (c) return fix(c);
    return noTopic();
  }

  function example(c) {
    if (!c) return noTopic();
    return L(
      '**[' + c.cwe + '] 취약한 코드와 안전한 코드**\n\n' +
      '데모 모드는 코드를 새로 만들어 내지 않습니다. 대신 이 약점의 비교 예제가 이미 준비돼 있어요.\n\n' +
      '- 개념 카드와 Java, Python 예제: **진단원 학습 센터**\n' +
      '- 직접 고쳐 보고 채점받기: **코드 수정 실습(code-fix-lab.html)**\n' +
      '- 동작을 눈으로 보기: 해당 약점의 **시뮬레이터**\n\n' +
      '핵심만 말하면 이렇습니다: ' + c.safe,

      '**[' + c.cwe + '] vulnerable vs safe**\n\n' +
      'Demo mode does not generate new code. The comparison examples already exist here.\n\n' +
      '- concept cards with Java and Python examples: **Diagnostician Center**\n' +
      '- fix it yourself and get graded: **Code-Fix Lab**\n' +
      '- watch it happen: the matching **simulator**\n\n' +
      'The short version: ' + c.safe
    );
  }

  /* ---------- 공개 API ---------- */

  function reply(opts) {
    opts = opts || {};
    var text = String(opts.text || '');
    var c = opts.concept || null;
    var state = opts.state || {};

    if (isAbuse(text)) {
      state.hintStep = 1;
      return { text: refusal(), refused: true, state: state };
    }

    var hasCode = looksLikeCode(text);
    var smells = hasCode ? findSmells(text) : [];
    var intent = intentOf(text);

    /* 코드를 새로 붙여넣으면 힌트 사다리를 처음부터 시작한다. */
    if (hasCode) state.hintStep = 1;

    var out;
    switch (intent) {
      case 'hint':
        out = reviewHint(smells.length ? smells : (state.lastSmells || []),
                         state.hintStep || 1,
                         hasCode || !!(state.lastSmells && state.lastSmells.length));
        state.hintStep = Math.min(3, (state.hintStep || 1) + 1);
        break;
      case 'review':
        out = reviewHint(smells, 1, hasCode);
        state.hintStep = 2;
        break;
      case 'answer':  out = answerNow(c, smells.length ? smells : (state.lastSmells || []), hasCode || !!(state.lastSmells || []).length); break;
      case 'example': out = example(c); break;
      case 'quiz':    out = c ? quiz(c) : noTopic(); break;
      case 'diag':    out = c ? diag(c) : noTopic(); break;
      case 'fix':     out = c ? fix(c) : noTopic(); break;
      default:
        if (hasCode) { out = reviewHint(smells, 1, true); state.hintStep = 2; }
        else out = c ? explain(c) : noTopic();
    }

    if (hasCode) state.lastSmells = smells;
    return { text: out, refused: false, state: state };
  }

  function greeting(c) {
    var head = L(
      '안녕하세요. **데모 모드**로 시작했습니다. API 키 없이 바로 쓸 수 있어요.\n\n',
      'Hi. You are in **demo mode**, which works without an API key.\n\n');
    var body = L(
      '이 모드는 사이트가 들고 있는 학습 자료를 규칙에 따라 조합해 답합니다. ' +
      '새로운 문장을 만들어 내지는 않지만, 개념 설명부터 코드 리뷰 힌트까지 한 바퀴를 끝낼 수 있습니다.\n\n' +
      '이렇게 해 보세요.\n' +
      bullet([
        '위에서 주제를 고르고 "설명해줘"',
        '이어서 "진단 포인트는?" 그리고 "어떻게 고쳐?"',
        '코드를 붙여넣고 "리뷰해줘" 그다음 "힌트" 를 세 번'
      ]),

      'This mode composes answers from the study material already on the site by rule. ' +
      'It does not write new prose, but it can take you from concept to code-review hints end to end.\n\n' +
      'Try this:\n' +
      bullet([
        'pick a topic above and say "explain"',
        'then "diagnosis points?" and "how do I fix it?"',
        'paste code, say "review", then ask for "hint" three times'
      ]));
    var tail = c ? '\n\n' + L('현재 주제: ', 'Current topic: ') + '[' + c.cwe + '] ' + c.name : '';
    return head + body + tail;
  }

  window.WvsAiDemo = {
    reply: reply,
    greeting: greeting,
    isAbuse: isAbuse,
    findSmells: findSmells,
    looksLikeCode: looksLikeCode,
    SMELLS: SMELLS
  };
})();
