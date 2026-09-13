/**
 * WVS_REVIEW — 오개념 복습 엔진 (G09)
 *
 * 목적: "같은 실수를 다른 상황에서 반복하지 않게" 한다.
 *
 * 정직성 원칙 — 여기서 가장 중요한 부분:
 *   "오개념"은 학습자의 이해에 대한 주장이다. 근거 없이 붙이면 틀린 낙인이 된다.
 *   그래서 이 엔진은 **실제로 기록된 실패**만 근거로 삼고, 각 항목에 무엇을 보고
 *   그렇게 판단했는지(evidence)와 확신 수준(confidence)을 함께 남긴다.
 *     observed  — 같은 지점에서 2회 이상 실패했고 성공보다 많다
 *     single    — 1회 실패. 아직 오개념이라고 부르지 않는다(참고용)
 *   한 번 틀린 것을 오개념으로 부풀리지 않는다.
 *
 * 데이터 출처(모두 이미 있는 기록):
 *   wvs_red_profile  레드팀 도메인·분류별 ok/fail
 *   wvs_incident     대표 사건 단계별 검증 결과(실패한 테스트 ID 포함)
 *   wvs_progress     완료 여부(복습 대상에서 이미 푼 것을 뺄 때 쓴다)
 */
(function () {
  'use strict';

  /* 실패 테스트 ID → 오개념 태그.
     대표 사건의 고정 검사기가 내는 ID 라서 추측이 아니라 관찰된 실패에 직접 대응한다. */
  var TEST_TO_TAG = {
    's1-other-read': 'authz.ownership',
    's1-other-read-2': 'authz.ownership',
    's1-anon-read': 'authz.anonymous',
    's1-admin-read': 'authz.overblock',
    's1-own-read': 'authz.overblock',
    's1-own-read-2': 'authz.overblock',
    's4-other': 'authz.ownership',
    's4-anon': 'authz.anonymous',
    's4-own': 'authz.overblock',
    'p-tampered': 'integrity.signature',
    'p-downgrade': 'integrity.version',
    'p-wrong-target': 'integrity.target',
    'p-ok': 'integrity.overblock',
    's3-count': 'privacy.scope',
    's3-fields': 'privacy.scope',
  };

  var TAGS = {
    'authz.ownership': {
      label: '소유 관계를 서버에서 대조하지 않음',
      why: '로그인 여부나 역할만 보고 "이 자원이 이 사람 것인가"를 확인하지 않으면 타인 자원이 그대로 열립니다.',
      skills: ['CWE-639', 'CWE-285'],
    },
    'authz.anonymous': {
      label: '비인증 요청을 거르지 않음',
      why: '인가 규칙이 인증된 사용자만 가정하면, 로그인하지 않은 요청이 규칙을 그냥 빠져나갑니다.',
      skills: ['CWE-306'],
    },
    'authz.overblock': {
      label: '막다가 정상 사용까지 차단함',
      why: '비인가를 막는 것과 서비스를 죽이는 것은 다릅니다. 정상 경로가 계속 동작하는지 함께 확인해야 합니다.',
      skills: ['CWE-285'],
    },
    'integrity.signature': {
      label: '무결성 서명을 확인하지 않음',
      why: '전송·저장 중 바뀐 내용을 걸러내려면 서명 검증이 필요합니다. 출처만으로는 변조를 알 수 없습니다.',
      skills: ['CWE-345', 'CWE-347'],
    },
    'integrity.version': {
      label: '버전 되돌리기를 허용함',
      why: '서명이 유효한 옛 버전을 다시 설치하면 이미 고친 취약점이 되살아납니다.',
      skills: ['CWE-757'],
    },
    'integrity.target': {
      label: '적용 대상을 확인하지 않음',
      why: '다른 기종·지역용 패키지가 설치되면 의도하지 않은 동작이나 장애로 이어집니다.',
      skills: ['CWE-345'],
    },
    'integrity.overblock': {
      label: '정상 패키지까지 거부함',
      why: '검사를 과하게 걸어 정상 업데이트가 막히면 보안 패치가 배포되지 않습니다.',
      skills: [],
    },
    'privacy.scope': {
      label: '영향 범위를 정확히 세지 못함',
      why: '통지·신고 판단의 출발점은 "무엇이 실제로 조회됐는가"입니다. 정상 접근까지 세거나 항목을 빠뜨리면 대응이 어긋납니다.',
      skills: [],
    },
  };

  function readJson(key) {
    try { return JSON.parse(localStorage.getItem(key)) || {}; } catch (e) { return {}; }
  }

  /**
   * 기록된 실패에서 오개념 후보를 모은다.
   * @returns {Array<{tag,label,why,skills,count,confidence,evidence:string[]}>}
   */
  function collect(stores) {
    var red = (stores && stores.red) || readJson('wvs_red_profile');
    var inc = (stores && stores.incident) || readJson('wvs_incident');
    var hits = {};

    function add(tag, evidence) {
      if (!TAGS[tag]) return;
      if (!hits[tag]) hits[tag] = { tag: tag, count: 0, evidence: [] };
      hits[tag].count++;
      if (hits[tag].evidence.indexOf(evidence) < 0) hits[tag].evidence.push(evidence);
    }

    /* 대표 사건: 고정 검사기가 실패로 판정한 테스트 ID 만 본다 */
    Object.keys(inc).forEach(function (stageId) {
      if (stageId.charAt(0) === '_') return;
      var st = inc[stageId];
      if (!st || st.passed) return;                 /* 통과했으면 오개념 근거가 아니다 */
      var failed = st.failedTests || [];
      failed.forEach(function (t) {
        if (TEST_TO_TAG[t]) add(TEST_TO_TAG[t], '대표 사건 ' + stageId + ' — 실패한 검사 ' + t);
      });
    });

    /* 레드팀: 2회 이상 실패하고 성공보다 많은 분류만(1회 실수는 제외) */
    Object.keys(red).forEach(function (dom) {
      var cats = red[dom] || {};
      Object.keys(cats).forEach(function (c) {
        var s = cats[c] || {};
        if ((s.fail || 0) >= 2 && (s.fail || 0) > (s.ok || 0)) {
          /* 레드팀 분류는 자체 라벨이라 태그 사전에 없을 수 있다 → 일반 항목으로 남긴다 */
          var tag = 'redteam:' + c;
          if (!hits[tag]) hits[tag] = { tag: tag, count: 0, evidence: [], freeform: c };
          hits[tag].count += s.fail;
          hits[tag].evidence.push('레드팀 ' + dom + ' — ' + c + ' ' + s.fail + '회 실패 / ' + (s.ok || 0) + '회 성공');
        }
      });
    });

    return Object.keys(hits).map(function (k) {
      var h = hits[k];
      var meta = TAGS[h.tag] || { label: h.freeform || h.tag, why: '반복해서 막힌 지점입니다.', skills: [] };
      return {
        tag: h.tag,
        label: meta.label,
        why: meta.why,
        skills: meta.skills || [],
        count: h.count,
        /* 2회 이상이어야 "관찰됨". 1회는 참고용으로만 둔다. */
        confidence: h.count >= 2 ? 'observed' : 'single',
        evidence: h.evidence,
      };
    }).sort(function (a, b) { return b.count - a.count; });
  }

  /**
   * 오개념에 맞는 복습 항목을 고른다.
   * 같은 페이지를 다시 주지 않고 **다른 맥락**의 항목을 우선한다(전이 확인이 목적).
   * @param items content-catalog 의 items
   * @param mis   collect() 결과 한 건
   * @param opts  {exclude:Set<page>, limit:number}
   */
  function suggest(items, mis, opts) {
    opts = opts || {};
    var exclude = opts.exclude || {};
    var limit = opts.limit || 3;
    var wantSkills = mis.skills || [];
    var scored = [];
    (items || []).forEach(function (it) {
      if (exclude[it.page]) return;
      var score = 0;
      (it.skills || []).forEach(function (s) { if (wantSkills.indexOf(s) >= 0) score += 10; });
      /* 태그 앞부분(authz/integrity/privacy)이 키워드에 걸리면 약한 가점 */
      var area = String(mis.tag).split('.')[0];
      var hay = ((it.keywords || []).join(' ') + ' ' + (it.category || '')).toLowerCase();
      if (area === 'authz' && /인가|권한|authoriz|access/.test(hay)) score += 3;
      if (area === 'integrity' && /무결성|서명|integrity|signature/.test(hay)) score += 3;
      if (area === 'privacy' && /개인정보|privacy/.test(hay)) score += 3;
      if (score > 0) scored.push({ item: it, score: score });
    });
    scored.sort(function (a, b) { return b.score - a.score; });
    return scored.slice(0, limit).map(function (x) { return x.item; });
  }

  var API = {
    tags: TAGS,
    testToTag: TEST_TO_TAG,
    collect: collect,
    suggest: suggest,
  };
  if (typeof window !== 'undefined') window.WVS_REVIEW = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})();
