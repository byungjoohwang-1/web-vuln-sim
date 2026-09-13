/* ai-track.js - AI 보안 트랙 학습 경로 (AI 개편안 A-04, A-05, A-07)
 *
 * 26개 개념 카드가 파일명 순서로만 놓여 있으면 학습자는 어디부터 볼지 모른다.
 * 여기에 모듈, 난이도, 예상 시간, 선수 개념, 권장 순서를 한곳에 모아 두고
 * 허브(ai-hub.html)와 각 카드의 상단 정보 띠가 같은 자료를 읽는다.
 *
 * 선수 개념은 이 사이트 안의 웹 약점 페이지를 가리킨다.
 * AI 보안은 새 취약점 목록이 아니라, 익숙한 약점이 새 표면에서 다시 나타나는 것이기 때문이다.
 */
(function () {
  'use strict';

  function isEn() {
    try { return (localStorage.getItem('wvs_lang') || localStorage.getItem('lang')) === 'en'; }
    catch (e) { return false; }
  }
  function T(v) { return Array.isArray(v) ? (isEn() ? v[1] : v[0]) : v; }

  var MODULES = [
    { id: 'basic',
      label: ['1. 기초: 입력과 출력의 경계', '1. Foundations: the input and output boundary'],
      desc: ['모델에 들어가는 것과 나오는 것을 누가 통제하는지부터 잡는다. 여기를 건너뛰면 나머지가 흩어진다.',
             'Start with who controls what goes into the model and what comes out. Skip this and the rest will not hold together.'] },
    { id: 'app',
      label: ['2. 응용: 서비스에 붙였을 때', '2. In production: once it is wired into a service'],
      desc: ['모델을 실제 시스템에 연결하면 권한, 비용, 데이터 흐름이 새 공격면이 된다.',
             'Connect a model to real systems and permissions, cost and data flow all become attack surface.'] },
    { id: 'advml',
      label: ['3. 적대적 ML: 모델 자체를 노린다', '3. Adversarial ML: attacking the model itself'],
      desc: ['학습 데이터와 모델 파라미터를 겨냥하는 공격. 코드 수정으로는 막히지 않는다.',
             'Attacks aimed at training data and model parameters. No code change stops these.'] },
    { id: 'deep',
      label: ['4. 딥페이크와 사회공학', '4. Deepfakes and social engineering'],
      desc: ['사람을 속이는 쪽. 기술 대책과 절차 대책이 함께 필요하다.',
             'The side that targets people. Technical controls and procedural controls are both required.'] },
    { id: 'case',
      label: ['5. 사고 재구성', '5. Incident reconstruction'],
      desc: ['실제로 벌어진 유형을 되짚으며 앞 모듈에서 배운 것을 엮는다.',
             'Walk back through real incident patterns and tie the earlier modules together.'] },
    { id: 'pqc',
      label: ['6. 양자내성암호 전환', '6. Post-quantum migration'],
      desc: ['지금 쓰는 암호가 언제까지 버티는가. 마이그레이션은 오래 걸리므로 일찍 시작한다.',
             'How long does today\u0027s cryptography hold? Migration takes years, so it starts early.'] },
    { id: 'gov',
      label: ['7. 거버넌스와 운영', '7. Governance and operations'],
      desc: ['조직 차원에서 AI 사용을 어떻게 관리할 것인가. 관리자, 심사원 관점.',
             'How an organization governs its use of AI, from the administrator and auditor side.'] }
  ];

  /* file, 코드, 모듈, 난이도(1 입문 / 2 중급 / 3 심화), 예상 분, 선수 개념 */
  var CARDS = [
    ['13_ai-ai01.html', 'AI-01', 'basic',  1, 12, [['03_code_untrusted_input.html', '신뢰할 수 없는 입력']]],
    ['13_ai-ai02.html', 'AI-02', 'basic',  2, 15, [['13_ai-ai01.html', 'AI-01 직접 프롬프트 인젝션'], ['03_code_ssrf.html', 'SSRF']]],
    ['13_ai-ai10.html', 'AI-10', 'basic',  1, 10, []],
    ['13_ai-ai08.html', 'AI-08', 'basic',  2, 12, [['13_ai-ai01.html', 'AI-01 직접 프롬프트 인젝션']]],
    ['13_ai-ai03.html', 'AI-03', 'basic',  2, 14, [['03_code_session_data_exposure.html', '민감정보 노출']]],

    ['13_ai-ai06.html', 'AI-06', 'app',    2, 15, [['03_code_xss.html', 'XSS'], ['03_code_os_command.html', '운영체제 명령 삽입']]],
    ['13_ai-ai07.html', 'AI-07', 'app',    3, 18, [['03_code_missing_auth.html', '인가 누락']]],
    ['13_ai-ai11.html', 'AI-11', 'app',    2, 12, [['03_code_infinite_loop.html', '무한 루프']]],
    ['13_ai-ai09.html', 'AI-09', 'app',    3, 16, [['13_ai-ai03.html', 'AI-03 민감정보 유출']]],
    ['13_ai-ai05.html', 'AI-05', 'app',    3, 16, [['13_ai-ai02.html', 'AI-02 간접 프롬프트 인젝션']]],
    ['13_ai-ai04.html', 'AI-04', 'app',    2, 14, [['03_code_vulnerable_api.html', '취약한 API 사용']]],

    ['13_ai-ai12.html', 'AI-12', 'advml',  3, 15, []],
    ['13_ai-ai13.html', 'AI-13', 'advml',  3, 16, [['13_ai-ai05.html', 'AI-05 데이터, 모델 오염']]],
    ['13_ai-ai14.html', 'AI-14', 'advml',  3, 14, [['13_ai-ai03.html', 'AI-03 민감정보 유출']]],
    ['13_ai-ai15.html', 'AI-15', 'advml',  3, 14, []],

    ['13_ai-ai16.html', 'AI-16', 'deep',   1, 10, []],
    ['13_ai-ai17.html', 'AI-17', 'deep',   2, 12, [['13_ai-ai16.html', 'AI-16 딥보이스 보이스피싱']]],
    ['13_ai-ai18.html', 'AI-18', 'deep',   2, 13, [['03_code_wrong_auth.html', '잘못된 인증']]],

    ['13_ai-ai19.html', 'AI-19', 'case',   2, 14, [['13_ai-ai03.html', 'AI-03 민감정보 유출']]],
    ['13_ai-ai20.html', 'AI-20', 'case',   2, 14, [['13_ai-ai09.html', 'AI-09 벡터, 임베딩 취약점']]],

    ['13_ai-ai21.html', 'AI-21', 'pqc',    2, 12, [['03_code_risky_crypto.html', '취약한 암호 알고리즘']]],
    ['13_ai-ai22.html', 'AI-22', 'pqc',    3, 18, [['13_ai-ai21.html', 'AI-21 지금 수집, 나중 복호화']]],
    ['13_ai-ai23.html', 'AI-23', 'pqc',    3, 16, [['03_code_impropersignature.html', '부적절한 전자서명 검증']]],

    ['13_ai-ai24.html', 'AI-24', 'gov',    1, 10, []],
    ['13_ai-ai25.html', 'AI-25', 'gov',    2, 12, []],
    ['13_ai-ai26.html', 'AI-26', 'gov',    3, 16, [['13_ai-ai24.html', 'AI-24 섀도우 AI']]]
  ];

  var LEVEL = { 1: '입문', 2: '중급', 3: '심화' };
  var LEVEL_EN = { 1: 'Intro', 2: 'Core', 3: 'Advanced' };

  /* 선수 개념 링크의 영문 표기. 위 표에는 한국어만 적고 여기서 짝을 맞춘다. */
  var PREREQ_EN = {
    '03_code_untrusted_input.html': 'Untrusted input',
    '03_code_ssrf.html': 'SSRF',
    '03_code_session_data_exposure.html': 'Sensitive data exposure',
    '03_code_xss.html': 'XSS',
    '03_code_os_command.html': 'OS command injection',
    '03_code_missing_auth.html': 'Missing authorization',
    '03_code_infinite_loop.html': 'Infinite loop',
    '03_code_vulnerable_api.html': 'Use of a vulnerable API',
    '03_code_wrong_auth.html': 'Improper authentication',
    '03_code_risky_crypto.html': 'Broken cryptographic algorithm',
    '03_code_impropersignature.html': 'Improper signature verification',
    '13_ai-ai01.html': 'AI-01 Direct prompt injection',
    '13_ai-ai02.html': 'AI-02 Indirect prompt injection',
    '13_ai-ai03.html': 'AI-03 Sensitive information disclosure',
    '13_ai-ai05.html': 'AI-05 Data and model poisoning',
    '13_ai-ai09.html': 'AI-09 Vector and embedding weaknesses',
    '13_ai-ai16.html': 'AI-16 Deep-voice vishing',
    '13_ai-ai21.html': 'AI-21 Harvest now, decrypt later',
    '13_ai-ai24.html': 'AI-24 Shadow AI'
  };

  /* AI 카드 제목. 허브와 정보 띠가 같은 표를 읽는다. */
  var TITLES = {
    'AI-01': ['직접 프롬프트 인젝션', 'Direct prompt injection'],
    'AI-02': ['간접 프롬프트 인젝션', 'Indirect prompt injection'],
    'AI-03': ['민감정보 유출', 'Sensitive information disclosure'],
    'AI-04': ['모델 공급망 오염', 'Model supply chain compromise'],
    'AI-05': ['데이터, 모델 오염 (RAG 포이즈닝)', 'Data and model poisoning (RAG)'],
    'AI-06': ['불안전한 출력 처리', 'Insecure output handling'],
    'AI-07': ['과도한 에이전시 (툴 권한 남용)', 'Excessive agency (tool permissions)'],
    'AI-08': ['시스템 프롬프트 유출', 'System prompt leakage'],
    'AI-09': ['벡터, 임베딩 취약점', 'Vector and embedding weaknesses'],
    'AI-10': ['환각, 잘못된 정보', 'Hallucination and misinformation'],
    'AI-11': ['무제한 소비 (비용 폭탄, DoS)', 'Unbounded consumption (cost, DoS)'],
    'AI-12': ['적대적 예제 (이미지 기만)', 'Adversarial examples (image evasion)'],
    'AI-13': ['데이터 포이즈닝 백도어', 'Data poisoning backdoors'],
    'AI-14': ['멤버십 추론 (프라이버시)', 'Membership inference (privacy)'],
    'AI-15': ['모델 추출, 탈취', 'Model extraction and theft'],
    'AI-16': ['딥보이스 보이스피싱', 'Deep-voice vishing'],
    'AI-17': ['딥페이크 영상 탐지', 'Deepfake video detection'],
    'AI-18': ['생체인증 우회 vs Liveness', 'Biometric bypass vs liveness'],
    'AI-19': ['사고 재구성: 생성형 AI 기밀 유출', 'Case: confidential data into a chatbot'],
    'AI-20': ['사고 재구성: AI 서비스 데이터 노출', 'Case: AI service data exposure'],
    'AI-21': ['지금 수집, 나중 복호화 (HNDL)', 'Harvest now, decrypt later'],
    'AI-22': ['양자내성암호 전환', 'Post-quantum migration'],
    'AI-23': ['양자 취약 전자서명에서 ML-DSA 로', 'Quantum-vulnerable signatures to ML-DSA'],
    'AI-24': ['섀도우 AI (미승인 AI 사용 통제)', 'Shadow AI (unsanctioned use)'],
    'AI-25': ['AI 투명성, 책임성', 'AI transparency and accountability'],
    'AI-26': ['AI 위험관리, 레드팀 (NIST AI RMF)', 'AI risk management and red teaming']
  };

  function toObj(row, i) {
    return {
      file: row[0], code: row[1], module: row[2],
      level: row[3], levelLabel: LEVEL[row[3]], levelLabelEn: LEVEL_EN[row[3]],
      minutes: row[4],
      prereq: (row[5] || []).map(function (p) {
        return { file: p[0], label: p[1], labelEn: PREREQ_EN[p[0]] || p[1] };
      }),
      title: TITLES[row[1]] || [row[1], row[1]],
      order: i + 1
    };
  }

  var PATH = CARDS.map(toObj);
  var BY_FILE = {};
  PATH.forEach(function (c) { BY_FILE[c.file] = c; });

  function moduleOf(id) {
    for (var i = 0; i < MODULES.length; i++) { if (MODULES[i].id === id) return MODULES[i]; }
    return null;
  }

  function grouped() {
    return MODULES.map(function (m) {
      return { module: m, cards: PATH.filter(function (c) { return c.module === m.id; }) };
    });
  }

  function totalMinutes() {
    return PATH.reduce(function (a, c) { return a + c.minutes; }, 0);
  }

  /* ---------- 진도 (wvs_ai_* 네임스페이스로 통일, A-07) ---------- */
  var STORE = 'wvs_ai_track';
  function progress() {
    try { return JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { return {}; }
  }
  function markVisited(file) {
    try {
      var p = progress();
      if (p[file]) return p;
      p[file] = { at: new Date().toISOString().slice(0, 10) };
      localStorage.setItem(STORE, JSON.stringify(p));
      return p;
    } catch (e) { return {}; }
  }
  function doneCount() {
    var p = progress();
    return PATH.filter(function (c) { return p[c.file]; }).length;
  }

  window.WvsAiTrack = {
    T: T, isEn: isEn,
    MODULES: MODULES, PATH: PATH, BY_FILE: BY_FILE, TITLES: TITLES,
    moduleOf: moduleOf, grouped: grouped, totalMinutes: totalMinutes,
    progress: progress, markVisited: markVisited, doneCount: doneCount
  };
})();
