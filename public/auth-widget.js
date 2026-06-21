// 공통 Google 로그인 + 학습 진도 클라우드 동기화 위젯 (전 페이지 공통, Firebase 무료/Spark)
// Firebase Auth(Google) + Firestore(users/{uid}.store = localStorage 스냅샷). Cloud Functions 미사용(무과금).
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged,
         setPersistence, browserLocalPersistence } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyBaRXs5HJ1ABFcshaTpqNj-uFuq2H9ZOcw",
  authDomain: "vuln-sim.firebaseapp.com",
  projectId: "vuln-sim",
  storageBucket: "vuln-sim.firebasestorage.app",
  messagingSenderId: "493267417608",
  appId: "1:493267417608:web:a76ea57fcd71185ae86fbd"
};

const app = initializeApp(firebaseConfig);
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

function collectStore(){
  const o = {};
  for (let i = 0; i < localStorage.length; i++){ const k = localStorage.key(i); o[k] = localStorage.getItem(k); }
  return o;
}
function setStatus(t){ const s = document.getElementById('authSync'); if (s) s.textContent = t; }

async function pushNow(){
  if (!currentUser) return;
  try {
    await setDoc(doc(db, 'users', currentUser.uid), {
      store: collectStore(),
      email: currentUser.email || '', name: currentUser.displayName || '',
      updatedAt: serverTimestamp()
    }, { merge: true });
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
      for (const k in remote){ if (localStorage.getItem(k) !== remote[k]){ _set(k, remote[k]); changed = true; } }
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
async function doLogin(){
  try { await signInWithPopup(auth, provider); }
  catch (e){
    console.error('[login]', e);
    if (e.code === 'auth/popup-closed-by-user' || e.code === 'auth/cancelled-popup-request') return;
    let msg = '로그인에 실패했습니다. 잠시 후 다시 시도해 주세요.';
    if (e.code === 'auth/operation-not-allowed') msg = 'Google 로그인이 아직 활성화되지 않았습니다. (관리자: Firebase 콘솔 → Authentication에서 Google 제공업체를 켜주세요)';
    else if (e.code === 'auth/unauthorized-domain') msg = '허용되지 않은 도메인에서의 로그인입니다.';
    alert(msg);
  }
}

setPersistence(auth, browserLocalPersistence).catch(() => {});
onAuthStateChanged(auth, u => u ? onLogin(u) : onLogout());
render();
