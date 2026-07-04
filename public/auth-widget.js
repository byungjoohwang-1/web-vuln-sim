// 공통 Google 로그인 + 학습 진도 클라우드 동기화 위젯 (전 페이지 공통, Firebase 무료/Spark)
// Firebase Auth(Google) + Firestore(users/{uid}.store = localStorage 스냅샷). Cloud Functions 미사용(무과금).
import { initializeApp, getApps } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, getRedirectResult,
         signOut, onAuthStateChanged,
         setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, serverTimestamp,
         collection, query, orderBy, limit, getDocs } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyBaRXs5HJ1ABFcshaTpqNj-uFuq2H9ZOcw",
  authDomain: "vuln-sim.firebaseapp.com",
  projectId: "vuln-sim",
  storageBucket: "vuln-sim.firebasestorage.app",
  messagingSenderId: "493267417608",
  appId: "1:493267417608:web:a76ea57fcd71185ae86fbd"
};

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

// ===== 스타일 =====
const css = `
#authWidget{position:fixed;top:12px;right:12px;z-index:100000;font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif}
#authWidget .aw-btn{cursor:pointer;border:none;border-radius:10px;font-weight:700;font-size:13px;padding:9px 14px;display:flex;align-items:center;gap:8px;box-shadow:0 3px 12px rgba(0,0,0,.28);transition:transform .15s}
#authWidget .aw-btn:hover{transform:translateY(-1px)}
#authWidget .aw-in{background:#fff;color:#3c4043;border:1px solid #dadce0}
#authWidget .aw-card{display:flex;align-items:center;gap:10px;background:rgba(17,20,32,.86);color:#fff;border-radius:12px;padding:6px 8px 6px 7px;box-shadow:0 3px 14px rgba(0,0,0,.4)}
#authWidget .aw-user{display:flex;align-items:center;gap:9px}
#authWidget .aw-user img{width:32px;height:32px;border-radius:50%;background:#475569}
#authWidget .aw-av{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
#authWidget .aw-meta{display:flex;flex-direction:column;line-height:1.25}
#authWidget .aw-meta b{font-size:13px;max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#authWidget .aw-meta span{font-size:10.5px;color:#86efac}
#authWidget .aw-out{background:rgba(255,255,255,.16);color:#fff;border:none;border-radius:8px;padding:7px 11px;font-size:12px;font-weight:700;cursor:pointer}
#authWidget .aw-out:hover{background:rgba(255,255,255,.28)}
@media(max-width:560px){#authWidget{top:8px;right:8px}#authWidget .aw-meta b{max-width:84px}#authWidget .aw-meta span{display:none}}
`;
const style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);
const box = document.createElement('div'); box.id = 'authWidget';
(document.body || document.documentElement).appendChild(box);

// ===== 동기화 =====
let currentUser = null, pushTimer = null;
const _set = localStorage.setItem.bind(localStorage);
const _rem = localStorage.removeItem.bind(localStorage);
const _clr = localStorage.clear.bind(localStorage);

// 동기화 대상은 앱 진도/설정 키(sda_/sdq_/wvs_)로 한정한다.
// Firebase 인증 내부 키(firebase:authUser…)를 동기화하면 원격의 오래된 값이
// 세션을 덮어써 로그인이 깨지고, wvs_ai_key(개인 API 키)는 절대 업로드하면 안 된다.
const SYNC_PREFIXES = ['sda_', 'sdq_', 'wvs_'];
const SYNC_DENY = new Set(['wvs_ai_key']);
function shouldSync(k){
  if (!k || SYNC_DENY.has(k)) return false;
  return SYNC_PREFIXES.some(p => k.indexOf(p) === 0);
}
function collectStore(){
  const o = {};
  for (let i = 0; i < localStorage.length; i++){ const k = localStorage.key(i); if (shouldSync(k)) o[k] = localStorage.getItem(k); }
  return o;
}
function setStatus(t){ const s = document.getElementById('authSync'); if (s) s.textContent = t; }

async function pushNow(){
  if (!currentUser) return;
  try {
    // 비-merge 쓰기로 문서를 통째로 재작성 → 과거에 잘못 올라간 firebase 인증 키·
    // API 키 등 stale 필드를 원격에서 정리(purge)한다.
    await setDoc(doc(db, 'users', currentUser.uid), {
      store: collectStore(),
      email: currentUser.email || '', name: currentUser.displayName || '',
      updatedAt: serverTimestamp()
    });
    setStatus('동기화됨 ✓');
  } catch (e){ console.error('[sync push]', e); setStatus('동기화 보류'); }
}
function schedulePush(){ if (!currentUser) return; setStatus('동기화 중…'); clearTimeout(pushTimer); pushTimer = setTimeout(pushNow, 1500); }

// localStorage 쓰기를 가로채 자동 동기화
localStorage.setItem = (k, v) => { _set(k, v); schedulePush(); };
localStorage.removeItem = (k) => { _rem(k); schedulePush(); };
localStorage.clear = () => { _clr(); schedulePush(); };

async function onLogin(user){
  currentUser = user; render();
  try {
    const snap = await getDoc(doc(db, 'users', user.uid));
    let changed = false;
    if (snap.exists() && snap.data().store){
      const remote = snap.data().store;
      // 앱 키만 적용한다(firebase 인증 키/민감 키는 원격에 남아 있어도 무시).
      for (const k in remote){ if (shouldSync(k) && localStorage.getItem(k) !== remote[k]){ _set(k, remote[k]); changed = true; } }
    }
    await pushNow();
    if (changed) setTimeout(() => location.reload(), 400); // 동기화된 진도로 화면 갱신
  } catch (e){ console.error('[sync pull]', e); setStatus('동기화 보류'); }
}
function onLogout(){ currentUser = null; render(); }

// ===== UI =====
function esc(s){ const d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
const GICON = '<svg width="16" height="16" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.6l6.7-6.7C35.6 2.6 30.2 0 24 0 14.6 0 6.4 5.4 2.5 13.3l7.8 6.1C12.2 13.2 17.6 9.5 24 9.5z"/><path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.5 3-2.2 5.5-4.7 7.2l7.3 5.7c4.3-4 6.8-9.9 6.8-17.4z"/><path fill="#FBBC05" d="M10.3 28.4c-.5-1.5-.8-3-.8-4.4s.3-3 .8-4.4l-7.8-6.1C.9 16.5 0 20.1 0 24s.9 7.5 2.5 10.5l7.8-6.1z"/><path fill="#34A853" d="M24 48c6.2 0 11.4-2 15.2-5.5l-7.3-5.7c-2 1.4-4.7 2.3-7.9 2.3-6.4 0-11.8-3.7-13.7-9l-7.8 6.1C6.4 42.6 14.6 48 24 48z"/></svg>';

function render(){
  if (currentUser){
    const u = currentUser;
    const av = u.photoURL
      ? `<img src="${esc(u.photoURL)}" referrerpolicy="no-referrer" alt="">`
      : `<div class="aw-av">${esc((u.displayName || u.email || 'U').slice(0,1).toUpperCase())}</div>`;
    box.innerHTML = `<div class="aw-card"><div class="aw-user">${av}<div class="aw-meta"><b>${esc(u.displayName || u.email || '사용자')}</b><span id="authSync">동기화됨 ✓</span></div></div><button class="aw-out" id="awOut">로그아웃</button></div>`;
    document.getElementById('awOut').onclick = () => signOut(auth);
  } else {
    box.innerHTML = `<button class="aw-btn aw-in" id="awIn">${GICON}<span>Google 로그인</span></button>`;
    document.getElementById('awIn').onclick = doLogin;
  }
}
function isMobile(){ return /Android|iPhone|iPad|iPod|Mobile|Silk/i.test(navigator.userAgent || ''); }

async function doLogin(){
  // 모바일은 팝업이 차단·미지원인 경우가 많아 리다이렉트 방식을 우선한다.
  try {
    if (isMobile()) { await signInWithRedirect(auth, provider); return; }
    await signInWithPopup(auth, provider);
  } catch (e){
    if (e.code === 'auth/popup-closed-by-user' || e.code === 'auth/cancelled-popup-request') return;
    // 팝업 차단/환경 미지원 → 리다이렉트로 폴백
    if (e.code === 'auth/popup-blocked' || e.code === 'auth/operation-not-supported-in-this-environment'){
      try { await signInWithRedirect(auth, provider); return; } catch (e2){ e = e2; }
    }
    console.error('[login]', e);
    let msg = '로그인에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    if (e.code === 'auth/operation-not-allowed') msg = 'Google 로그인이 아직 활성화되지 않았습니다. (관리자: Firebase 콘솔 → Authentication에서 Google 제공업체를 켜주세요)';
    else if (e.code === 'auth/unauthorized-domain') msg = '허용되지 않은 도메인에서의 로그인입니다. (관리자: Firebase 콘솔 → Authentication → 승인된 도메인에 현재 도메인을 추가하세요)';
    alert(msg);
  }
}

// ===== 리더보드 브리지: 아카데미(인라인 스크립트)에서 호출하는 공개 API =====
// leaderboard/{uid} = {name, xp, level, streak, updatedAt}. 본인만 쓰기, 로그인자만 읽기(firestore.rules).
window.sdaBoard = {
  getUser(){ return currentUser ? { uid: currentUser.uid, name: currentUser.displayName || currentUser.email || '사용자' } : null; },
  async publish(p){
    if (!currentUser) throw new Error('not-logged-in');
    const name = (p && p.name ? String(p.name) : (currentUser.displayName || '익명')).slice(0, 24);
    await setDoc(doc(db, 'leaderboard', currentUser.uid), {
      name, xp: (p && +p.xp) || 0, level: (p && +p.level) || 1, streak: (p && +p.streak) || 0,
      updatedAt: serverTimestamp()
    }, { merge: true });
    return true;
  },
  async fetchTop(n){
    const q = query(collection(db, 'leaderboard'), orderBy('xp', 'desc'), limit(n || 20));
    const snap = await getDocs(q);
    const me = currentUser ? currentUser.uid : null;
    const rows = [];
    snap.forEach(d => { const v = d.data(); rows.push({ uid: d.id, name: v.name || '익명', xp: v.xp || 0, level: v.level || 1, streak: v.streak || 0, me: d.id === me }); });
    return rows;
  },
  // 수료증 온라인 등록(진위 검증용). certificates/{certId} 는 불변(create-only).
  async registerCert(cert){
    if (!currentUser) throw new Error('not-logged-in');
    if (!cert || !cert.certId) throw new Error('bad-cert');
    await setDoc(doc(db, 'certificates', String(cert.certId)), {
      uid: currentUser.uid,
      name: String(cert.name || '').slice(0, 40),
      certId: String(cert.certId),
      date: String(cert.date || ''),
      level: (+cert.level) || 1,
      xp: (+cert.xp) || 0,
      concepts: (+cert.concepts) || 0,
      practical: (+cert.practical) || 0,
      hash: String(cert.hash || ''),
      createdAt: serverTimestamp()
    });
    return true;
  },
  // 공개 단건 조회(로그인 불필요). verify 페이지에서 사용.
  async fetchCert(certId){
    if (!certId) return null;
    const snap = await getDoc(doc(db, 'certificates', String(certId)));
    return snap.exists() ? snap.data() : null;
  }
};

setPersistence(auth, browserLocalPersistence).catch(() => {});
// 리다이렉트 로그인 복귀 처리(에러 표면화). 성공 시 onAuthStateChanged가 이어서 처리한다.
getRedirectResult(auth).catch(e => {
  if (e && e.code && e.code !== 'auth/no-auth-event'){
    console.error('[redirect]', e);
    if (e.code === 'auth/unauthorized-domain') alert('허용되지 않은 도메인에서의 로그인입니다. (관리자: 승인된 도메인 확인)');
  }
});
onAuthStateChanged(auth, u => u ? onLogin(u) : onLogout());
render();
