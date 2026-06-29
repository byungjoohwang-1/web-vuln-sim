/* WEB-VULN-SIM — shared CWE → simulator-page map.
 * Single source of truth reused by skill-tree, breach-campaign, etc. */
window.SIM_BY_CWE = {
  'CWE-89': 'sim-sql.html', 'CWE-94': 'sim-code.html', 'CWE-22': 'sim-path.html',
  'CWE-79': 'sim-xss.html', 'CWE-78': 'sim-cmd.html', 'CWE-434': 'sim-upload.html',
  'CWE-601': 'sim-open-redirect.html', 'CWE-611': 'sim-xxe.html', 'CWE-91': 'sim-xml-injection.html',
  'CWE-90': 'sim-ldap.html', 'CWE-352': 'sim-csrf.html', 'CWE-918': 'sim-ssrf.html',
  'CWE-113': 'sim-split.html', 'CWE-190': 'sim-int-overflow.html', 'CWE-807': 'sim-untrusted-decision.html',
  'CWE-120': 'sim-bufferoverflow.html', 'CWE-134': 'sim-formatstring.html', 'CWE-306': 'sim-no-auth.html',
  'CWE-285': 'sim-idor.html', 'CWE-732': 'sim-wrong-permission.html', 'CWE-327': 'sim-weak-crypto.html',
  'CWE-311': 'sim-unencrypted_data.html', 'CWE-798': 'sim-hardedcode.html', 'CWE-326': 'sim-weak-keylength.html',
  'CWE-330': 'sim-weak-random.html', 'CWE-521': 'sim-weak-password.html', 'CWE-347': 'sim-signature-verify.html',
  'CWE-295': 'sim-cert-validation.html', 'CWE-539': 'sim-cookiebyunjo.html', 'CWE-615': 'sim-source-comments.html',
  'CWE-759': 'sim-nosalt-hash.html', 'CWE-494': 'sim-code-integrity.html', 'CWE-307': 'sim-brute.html',
  'CWE-367': 'sim-racecondition.html', 'CWE-835': 'sim-infinite-loop.html', 'CWE-209': 'sim-error-msg.html',
  'CWE-391': 'sim-error-missing.html', 'CWE-755': 'sim-improper-exception.html', 'CWE-476': 'sim-nullpointer.html',
  'CWE-404': 'sim-resource-leak.html', 'CWE-416': 'sim-use-after-free.html', 'CWE-457': 'sim-uninitialized.html',
  'CWE-502': 'sim-deserialization.html', 'CWE-488': 'sim-session_hijacking.html', 'CWE-489': 'sim-debug-code.html',
  'CWE-495': 'sim-private-array-return.html', 'CWE-496': 'sim-public-to-private.html', 'CWE-350': 'sim-dns-decision.html',
  'CWE-676': 'sim-vulnerable-api.html'
};
