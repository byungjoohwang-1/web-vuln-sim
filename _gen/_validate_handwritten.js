// 수기 수정 3개 페이지(risky_crypto/csrf/nosalthash)의 실제 validate 함수를
// DOM shim 위에서 실행하여, 안전/취약 코드 케이스가 의도대로 판정되는지 검증.
const fs = require('fs'), vm = require('vm'), path = require('path');
const PUB = path.join(__dirname, '..', 'public');

function mkEl() {
  const el = { _html:'', textContent:'', value:'', disabled:false, style:{},
    classList:{ _s:new Set(), add(){[].forEach.call(arguments,a=>this._s.add(a));}, remove(){[].forEach.call(arguments,a=>this._s.delete(a));}, toggle(c,f){if(f===undefined)f=!this._s.has(c);f?this._s.add(c):this._s.delete(c);return f;}, contains(c){return this._s.has(c);} },
    setAttribute(){}, getAttribute(){return '';}, getElementsByTagName(){return [];},
    querySelector(){return mkEl();}, querySelectorAll(){return [];}, appendChild(){}, focus(){} };
  Object.defineProperty(el,'innerHTML',{get(){return this._html;},set(v){this._html=v;}});
  return el;
}

function loadPage(file) {
  const html = fs.readFileSync(path.join(PUB, file), 'utf8');
  // inline script 모두 수집 (src 있는 것 제외)
  let code = '';
  const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g; let m;
  while ((m = re.exec(html))) code += '\n' + m[1];
  const elCache = {};
  const document = { getElementById(id){return elCache[id]||(elCache[id]=mkEl());}, createElement(){return mkEl();}, querySelector(){return mkEl();}, querySelectorAll(){return [];} };
  const Prism = { highlightElement(){} };
  const sandbox = { document, window:{Prism}, Prism, event:{target:{closest(){return mkEl();}}}, console, Math, JSON, Array, Object, String, Number, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  return { sandbox, elCache };
}

let fail = 0;
function check(name, cond) { if (!cond) { fail++; console.log('  X', name); } else { console.log('  ok', name); } }

// 공통: editor에 코드 넣고 validate 호출 후 status가 '안전한 코드'인지
function run(ctx, editorId, statusId, fn, codeStr) {
  ctx.elCache[editorId] = ctx.elCache[editorId] || mkEl();
  ctx.elCache[editorId].value = codeStr;
  const st = ctx.elCache[statusId] = ctx.elCache[statusId] || mkEl();
  st.textContent = ''; st.className = '';
  ctx.sandbox[fn]();
  return st.textContent.includes('안전한 코드') || (st.className||'').includes('status-secure');
}

console.log('=== risky_crypto ===');
{
  const c = loadPage('03_code_risky_crypto.html');
  const desJava = 'KeyGenerator.getInstance("DES");\nCipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");';
  const aesEcbJava = 'KeyGenerator.getInstance("AES");\nCipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");';
  const aesCbcJava = 'KeyGenerator.getInstance("AES");\nCipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");';
  check('Java DES(취약) => 실패', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', desJava)===false);
  check('Java AES/ECB => 실패(ECB 차단)', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', aesEcbJava)===false);
  check('Java AES/CBC => 통과', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', aesCbcJava)===true);
  const desPy = 'from Crypto.Cipher import DES\ncipher = DES.new(key, DES.MODE_ECB)';
  const aesEcbPy = 'from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_ECB)';
  const aesCbcPy = 'from Crypto.Cipher import AES\ncipher = AES.new(key, AES.MODE_CBC)';
  check('Py DES(취약) => 실패', run(c,'codeEditorPython','codeStatusPython','validateCodePython', desPy)===false);
  check('Py AES/ECB => 실패(ECB 차단)', run(c,'codeEditorPython','codeStatusPython','validateCodePython', aesEcbPy)===false);
  check('Py AES/CBC => 통과', run(c,'codeEditorPython','codeStatusPython','validateCodePython', aesCbcPy)===true);
}

console.log('=== csrf ===');
{
  const c = loadPage('03_code_csrf.html');
  const vuln = 'HttpSession session = request.getSession(false);\nif (session != null) { /* run */ }';
  const token = 'String sessionToken = (String) request.getSession().getAttribute("csrfToken");\nString formToken = request.getParameter("csrfToken");\nif (sessionToken != null && sessionToken.equals(formToken)) { run(); }';
  const referer = 'String referer = request.getHeader("Referer");\nif (referer != null && referer.startsWith("https://my-secure-site.com")) { run(); }';
  check('Java 세션만(취약) => 실패', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', vuln)===false);
  check('Java CSRF 토큰 => 통과', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', token)===true);
  check('Java Referer 검증 => 통과(보조)', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', referer)===true);
  const pyVuln = '@app.route("/x", methods=["POST"])\ndef x():\n    return do()';
  const pyTok = 'csrf = CSRFProtect(app)\n# form uses csrf_token()';
  check('Py 토큰 없음(취약) => 실패', run(c,'codeEditorPython','codeStatusPython','validateCodePython', pyVuln)===false);
  check('Py CSRFProtect => 통과', run(c,'codeEditorPython','codeStatusPython','validateCodePython', pyTok)===true);
}

console.log('=== nosalthash ===');
{
  const c = loadPage('03_code_nosalthash.html');
  const vulnJ = 'MessageDigest md = MessageDigest.getInstance("SHA-256");\nmd.update(password.getBytes());';
  const saltJ = 'MessageDigest md = MessageDigest.getInstance("SHA-256");\nmd.update(salt);\nmd.update(password.getBytes());';
  const adaptJ = 'return BCrypt.hashpw(password, BCrypt.gensalt(12));';
  check('Java 솔트없음(취약) => 실패', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', vulnJ)===false);
  check('Java 솔트 추가 => 통과', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', saltJ)===true);
  check('Java bcrypt(적응형) => 통과', run(c,'codeEditorJava','codeStatusJava','validateCodeJava', adaptJ)===true);
  const vulnP = 'return hashlib.sha256(password.encode()).hexdigest()';
  const pbkdfP = "return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)";
  check('Py 단순 sha256(취약) => 실패', run(c,'codeEditorPython','codeStatusPython','validateCodePython', vulnP)===false);
  check('Py pbkdf2 => 통과', run(c,'codeEditorPython','codeStatusPython','validateCodePython', pbkdfP)===true);
}

console.log('-'.repeat(40));
console.log(fail===0 ? 'HANDWRITTEN VALIDATION PASS' : ('FAIL count='+fail));
process.exit(fail===0?0:1);
