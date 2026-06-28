/**
 * WEB-VULN-SIM — Code-Fix Lab grader
 * Grades a user's attempt to fix vulnerable code, using window.sastEngine
 * (token-aware, comment-stripping) plus the per-exercise reference fix.
 *
 * Strategy (per exercise item from ACADEMY_DATA.PRACTICAL, isTruePositive only):
 *   POSITIVE — every item.safeCodeKeywords token/sequence must appear.
 *   NEGATIVE — any dangerous API token that THIS exercise's reference fix
 *              removed (present in vulnerable code, absent in safe code) must
 *              be gone from the user's code. The triple-gate
 *              (in-vuln & not-in-safe & in-user) avoids variable-name noise.
 *   NEGATIVE(literals) — weak crypto/algorithm names in string literals
 *              (MD5/DES/SHA-1/RC4/ECB) removed by the fix must be gone.
 *   CHANGED  — submission must differ from the original vulnerable code.
 *
 * Exposes window.CodeFixGrader.grade(item, userCode) -> result object.
 */
(function (global) {
  // Curated dangerous API tokens (token-level). The per-item triple-gate means
  // listing a token here is safe even if some other exercise keeps it.
  var DANGER = [
    // SQL
    'createStatement', 'Statement', 'executeQuery', 'executeUpdate',
    // OS command / process
    'exec', 'system', 'popen', 'Runtime', 'ProcessBuilder', 'getRuntime',
    // dynamic code execution
    'eval', 'compile', '__import__', 'ScriptEngine', 'getEngineByName',
    // unsafe deserialization
    'pickle', 'readObject', 'ObjectInputStream', 'marshal',
    // predictable RNG / weak seeds
    'Random', 'setSeed', 'nextLong', 'srand',
    // SSRF / DNS resolution from raw input
    'getCanonicalHostName', 'getByName', 'getAllByName',
    // dangerous loaders
    'loadLibrary', 'addURL',
    // unsafe C string handling
    'strcpy', 'strcat', 'gets', 'sprintf', 'scanf'
  ];

  // Weak algorithm / mode names that may live inside string literals.
  var LIT_DANGER = [
    { name: 'MD5', re: /\bMD5\b/i },
    { name: 'SHA-1', re: /\bSHA-?1\b/i },
    { name: 'DES', re: /\bDES\b/i },
    { name: 'RC4', re: /\bRC4\b/i },
    { name: 'ECB', re: /\bECB\b/i },
    { name: 'MD4', re: /\bMD4\b/i }
  ];

  function tokenizerFor(lang) {
    var SE = global.sastEngine;
    return lang === 'Python' ? SE.tokenizePython : SE.tokenizeJava;
  }

  function norm(s) {
    return String(s || '').replace(/\s+/g, ' ').trim();
  }

  // Strip comments but KEEP string-literal contents, so a required keyword that
  // lives inside a literal ("SHA-256", "%s", regex fragments) still matches,
  // while a keyword hidden in a comment does not count.
  function stripComments(code, lang) {
    var re = lang === 'Python'
      ? /[fF]?"(?:\\.|[^"\\])*"|[fF]?'(?:\\.|[^'\\])*'|(#.*|"""[\s\S]*?"""|'''[\s\S]*?''')/g
      : /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|(\/\/.*|\/\*[\s\S]*?\*\/)/g;
    return String(code || '').replace(re, function (m, g1) { return g1 ? '' : m; });
  }

  function grade(item, userCode) {
    var SE = global.sastEngine;
    if (!SE) return { ok: false, error: 'sastEngine 미로딩' };
    var tok = tokenizerFor(item.lang);

    var u = tok(userCode);
    var uSet = new Set(u);
    var safe = tok(item.safeCode || '');
    var safeSet = new Set(safe);
    var vuln = tok(item.code || '');
    var vulnSet = new Set(vuln);

    // CHANGED
    var changed = userCode.trim().length > 0 && norm(userCode) !== norm(item.code);

    // POSITIVE — required fix keywords must appear in the comment-stripped code.
    // Substring match (case-sensitive) handles literals, regex fragments and
    // special characters; comments are stripped so a keyword cannot be faked
    // in a comment.
    var cleanUser = stripComments(userCode, item.lang);
    var missing = (item.safeCodeKeywords || []).filter(function (k) {
      var key = String(k);
      if (cleanUser.indexOf(key) !== -1) return false;
      // identifier fallback: token match (covers tokenizer-normalized spacing)
      var kt = tok(key);
      if (kt.length === 1) return !uSet.has(kt[0]);
      if (kt.length > 1) return !SE.hasTokenSequence(u, kt);
      return true;
    });

    // NEGATIVE — dangerous API tokens this exercise removed must be gone
    var danger = DANGER.filter(function (d) {
      return vulnSet.has(d) && !safeSet.has(d) && uSet.has(d);
    });

    // NEGATIVE(literals) — weak algorithm names removed by the fix must be gone
    var dangerLit = LIT_DANGER.filter(function (L) {
      return L.re.test(item.code || '') && !L.re.test(item.safeCode || '') && L.re.test(userCode);
    }).map(function (L) { return L.name; });

    var allDanger = danger.concat(dangerLit);
    var pass = changed && missing.length === 0 && allDanger.length === 0;

    return {
      ok: true,
      pass: pass,
      changed: changed,
      missing: missing,        // required keywords not yet present
      danger: allDanger,       // dangerous tokens/algorithms still present
      // human-friendly reason for the first blocking issue
      reason: !changed ? 'unchanged'
        : missing.length ? 'missing'
        : allDanger.length ? 'danger'
        : 'pass'
    };
  }

  global.CodeFixGrader = { grade: grade, DANGER: DANGER };
})(typeof window !== 'undefined' ? window : globalThis);
