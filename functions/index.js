/**
 * Web Security Simulator Backend
 * Firebase Cloud Functions for KISA Secure Coding Guide
 */

const functions = require("firebase-functions");

// ============================================================
// 2-1. 입력 데이터 검증 (Input Validation) - SQL Injection
// ============================================================

exports.vulnerableSql = functions.https.onRequest((req, res) => {
    const input = req.query.id || "";
    const query = `SELECT * FROM users WHERE id = '${input}'`;
    
    // 공격 예시: ?id=' OR '1'='1
    if (input.includes("' OR '1'='1")) {
        res.send(`
            <div style="color:red; font-family:sans-serif;">
                <h2>⚠️ [SQL Injection] 공격 성공</h2>
                <p>실행된 쿼리: <strong>${query}</strong></p>
                <p>결과: 모든 사용자 정보 유출 (Admin, Guest...)</p>
            </div>
        `);
    } else {
        res.send(`조회 결과 없음: ${query}`);
    }
});

exports.secureSql = functions.https.onRequest((req, res) => {
    const input = req.query.id || "";
    // 파라미터 바인딩 흉내 (입력값을 데이터로만 처리)
    if (input.includes("' OR '1'='1")) {
         res.send(`
            <div style="color:green; font-family:sans-serif;">
                <h2>🛡️ [SQL Injection] 방어 성공</h2>
                <p>입력값이 문자열 리터럴로 이스케이프 처리되었습니다.</p>
                <p>실행 쿼리: <code>SELECT * FROM users WHERE id = ?</code> ([Data]: ${input})</p>
            </div>
        `);
    } else {
        res.send(`정상 조회: ${input}`);
    }
});


// ============================================================
// 2-3. 시간 및 상태 (Time and State) - Race Condition (TOCTOU)
// ============================================================
let globalBalance = 1000; // 공유 자원

exports.vulnerableTime = functions.https.onRequest(async (req, res) => {
    const withdrawAmount = 1000;
    
    // 1. 검사 (Check)
    if (globalBalance >= withdrawAmount) {
        
        // [Java/Python 책 분석 반영]
        // 검사와 사용 시점 사이의 시간차(Gap) 발생 시뮬레이션
        // Java의 synchronized 미사용, Python의 Lock 미사용 상황 가정
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 2. 사용 (Use)
        globalBalance -= withdrawAmount;
        
        res.send(`
            <div style="background:#fff5f5; border-left: 5px solid red; padding: 20px;">
                <h3 style="color:red; margin-top:0;">⚠️ 경쟁 조건(Race Condition) 발생</h3>
                <p><strong>TOCTOU (Time Of Check to Time Of Use)</strong> 취약점입니다.</p>
                <p>검사 후 실행까지의 지연 시간(Context Switch 등) 동안 상태가 변할 수 있습니다.</p>
                <p>현재 잔액: ${globalBalance} (중복 출금 등 무결성 훼손 가능)</p>
            </div>
        `);
    } else {
        res.send("잔액이 부족합니다.");
    }
    // 테스트용 리셋
    setTimeout(() => { globalBalance = 1000; }, 2500);
});

exports.secureTime = functions.https.onRequest((req, res) => {
    const withdrawAmount = 1000;
    
    // 원자적(Atomic) 실행 시뮬레이션
    if (globalBalance >= withdrawAmount) {
        globalBalance -= withdrawAmount;
        
        res.send(`
            <div style="background:#f0fff4; border-left: 5px solid green; padding: 20px;">
                <h3 style="color:green; margin-top:0;">✅ 안전한 거래 (Synchronized)</h3>
                <p>검사와 실행이 원자적(Atomic)으로 처리되었습니다.</p>
                <p><strong>Java:</strong> synchronized 블록 / <strong>Python:</strong> threading.Lock 사용 효과</p>
                <p>현재 잔액: ${globalBalance}</p>
            </div>
        `);
    } else {
        res.send("잔액이 부족합니다.");
    }
    setTimeout(() => { globalBalance = 1000; }, 2500);
});


// ============================================================
// 2-4. 에러 처리 (Error Handling) - Information Leakage
// ============================================================

exports.vulnerableError = functions.https.onRequest((req, res) => {
    try {
        // 인위적인 DB 연결 에러
        throw new Error("JDBC Connection Refused: 192.168.10.55:3306 (Access Denied)");
    } catch (error) {
        // [책 분석] e.printStackTrace() 결과를 그대로 웹에 노출하는 상황
        res.status(500).send(`
            <div style="font-family: monospace; background: #eee; padding: 20px;">
                <h2 style="color:red">HTTP Status 500 - Internal Server Error</h2>
                <hr>
                <p><strong>Type</strong> Exception Report</p>
                <p><strong>Message</strong> ${error.message}</p>
                <p><strong>Description</strong> The server encountered an internal error that prevented it from fulfilling this request.</p>
                <p><strong>Exception</strong></p>
                <pre style="color:red;">${error.stack}</pre>
                <hr>
                <p style="color:red; font-weight:bold;">[취약점 분석] 내부 IP 주소, 함수 경로, 라이브러리 정보가 모두 노출되었습니다.</p>
            </div>
        `);
    }
});

exports.secureError = functions.https.onRequest((req, res) => {
    try {
        throw new Error("JDBC Connection Refused: 192.168.10.55:3306");
    } catch (error) {
        // 서버 로그에는 상세 기록
        console.error("Critical System Error:", error);
        
        // 사용자에게는 일반 메시지
        res.status(500).send(`
            <div style="text-align:center; padding: 50px; font-family: sans-serif;">
                <h1 style="color:#555;">일시적인 서비스 장애</h1>
                <p>죄송합니다. 현재 요청을 처리할 수 없습니다.</p>
                <p>잠시 후 다시 시도해 주세요.</p>
                <p style="color:#999; font-size:12px;">(Error ID: ERR-2024-X881)</p>
                <br>
                <div style="background:#e6fffa; padding:10px; display:inline-block; border-radius:5px; color:green;">
                    ✅ <strong>안전함:</strong> 내부 시스템 정보는 로그 파일에만 기록되었습니다.
                </div>
            </div>
        `);
    }
});


// ============================================================
// 2-5. 코드 품질 (Code Quality) - Hardcoded Credentials
// ============================================================

exports.vulnerableQuality = functions.https.onRequest((req, res) => {
    // [책 분석] 소스코드 내에 비밀번호 하드코딩
    const DB_ADMIN_PW = "P@ssw0rd123!";
    const API_SECRET = "sk";

    res.send(`
        <div style="font-family:sans-serif; padding:20px;">
            <h2 style="color:red;">⚠️ 하드코딩된 중요 정보 발견</h2>
            <p>소스코드를 디컴파일(Reverse Engineering)하거나 Git 저장소가 유출될 경우, 아래 정보가 즉시 탈취됩니다.</p>
            <ul style="background:#ffffcc; padding:20px; border:1px solid #e2e2e2;">
                <li><strong>DB Password:</strong> <code>${DB_ADMIN_PW}</code></li>
                <li><strong>API Secret:</strong> <code>${API_SECRET}</code></li>
            </ul>
        </div>
    `);
});

exports.secureQuality = functions.https.onRequest((req, res) => {
    // 환경변수 사용 시뮬레이션
    const dbPw = process.env.DB_PW || "********"; 
    
    res.send(`
        <div style="font-family:sans-serif; padding:20px;">
            <h2 style="color:green;">✅ 안전한 자격증명 관리</h2>
            <p>소스코드에는 실제 비밀번호가 존재하지 않습니다.</p>
            <p>서버의 환경 변수(Environment Variable) 또는 보안 저장소(Vault)에서 값을 로드합니다.</p>
            <ul style="background:#f0f0f0; padding:20px; border:1px solid #ccc;">
                <li><strong>DB Password:</strong> <code>${dbPw}</code> (마스킹 처리됨)</li>
            </ul>
        </div>
    `);
});


// ============================================================
// 2-6. 캡슐화 (Encapsulation) - Mass Assignment / Public Fields
// ============================================================

exports.vulnerableEncap = functions.https.onRequest((req, res) => {
    // 기본 사용자 객체
    let userModel = {
        id: "user1",
        role: "USER",     // 변경 불가능해야 함
        name: "Hong Gil Dong"
    };
    
    // 공격자가 보낸 JSON 데이터 (쿼리 스트링 시뮬레이션)
    // 예: ?data={"role":"ADMIN"}
    const inputData = req.query.data ? JSON.parse(req.query.data) : {};

    // [책 분석] Mass Assignment 취약점
    // Java의 Public 필드 직접 접근이나 Python의 __dict__.update()와 유사
    // 입력받은 모든 필드를 검증 없이 덮어씀
    Object.assign(userModel, inputData);

    let alertMsg = "";
    if (userModel.role === "ADMIN") {
        alertMsg = `<h3 style="color:red;">🚨 경고: 일반 사용자가 ADMIN 권한을 획득했습니다!</h3>`;
    }

    res.send(`
        <div style="padding:20px; border:1px solid #ccc;">
            <h2>🚫 캡슐화 위반 (Mass Assignment)</h2>
            ${alertMsg}
            <p>현재 객체 상태:</p>
            <pre style="background:#eee; padding:10px;">${JSON.stringify(userModel, null, 2)}</pre>
            <p>Setter나 DTO 없이 외부 입력을 내부 객체에 바로 매핑하여 <strong>무결성</strong>이 깨졌습니다.</p>
        </div>
    `);
});

exports.secureEncap = functions.https.onRequest((req, res) => {
    let userModel = {
        id: "user1",
        role: "USER",
        name: "Hong Gil Dong"
    };

    const inputData = req.query.data ? JSON.parse(req.query.data) : {};

    // [방어] DTO 패턴 / 명시적 Setter 사용
    // 허용된 필드(name)만 수정하고, role은 변경 로직에서 제외
    if (inputData.name) {
        userModel.name = inputData.name;
    }
    // role 필드는 업데이트 하지 않음

    res.send(`
        <div style="padding:20px; border:1px solid green;">
            <h2>🛡️ 안전한 객체 접근 (Encapsulation)</h2>
            <p>공격자가 <code>role: ADMIN</code>을 전송했지만 무시되었습니다.</p>
            <pre style="background:#f0fff4; padding:10px;">${JSON.stringify(userModel, null, 2)}</pre>
            <p><strong>Java:</strong> Private 필드 + Setter 검증 / <strong>Python:</strong> @property 데코레이터 활용</p>
        </div>
    `);
});