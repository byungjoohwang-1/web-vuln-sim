const functions = require("firebase-functions");
const admin = require("firebase-admin");

admin.initializeApp();

// ==============================================================
// 1. HTTP 응답 분할 (HTTP Response Splitting)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 입력값을 검증 없이 헤더에 포함하여 개행 문자(CRLF)로 헤더 분리가 가능함
// [EN] Vulnerable: Input included in header without validation (CRLF can split headers)
exports.vulnerableSplit = functions.https.onRequest((req, res) => {
    const userInput = req.query.input || "guest";
    
    // [KR] 위험: 개행 문자(%0d%0a)가 들어오면 응답 헤더가 쪼개짐
    res.setHeader("Set-Cookie", `AuthToken=${userInput}; Max-Age=3600`);
    
    res.status(200).send(`
        <h3>⚠️ 취약한 모드 (Vulnerable Mode)</h3>
        <p>Input: ${userInput}</p>
        <p>[KR] 개발자 도구(F12) Network 탭에서 응답 헤더를 확인하세요.</p>
        <p>[EN] Check response headers in Developer Tools (F12) Network tab.</p>
    `);
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 개행 문자(\r, \n)를 제거하여 헤더 분할 방지
// [EN] Secure: Remove CRLF (\r, \n) to prevent header splitting
exports.secureSplit = functions.https.onRequest((req, res) => {
    const userInput = req.query.input || "guest";
    
    // [KR] 안전: URL 디코딩 후 개행 문자 제거
    const safeInput = decodeURIComponent(userInput).replace(/[\r\n]/g, "");
    
    res.setHeader("Set-Cookie", `AuthToken=${safeInput}; Max-Age=3600`);
    
    res.status(200).send(`
        <h3>✅ 안전한 모드 (Secure Mode)</h3>
        <p>Filtered Input: ${safeInput}</p>
        <p>[KR] 개행 문자가 제거되어 안전합니다.</p>
        <p>[EN] Safe as CRLF characters are removed.</p>
    `);
});


// ==============================================================
// 2. XSS (Cross Site Scripting)
// [참고] XSS는 프런트엔드(public/sim-xss.html)에서 DOM 조작을 통해 시뮬레이션하므로
// 별도의 백엔드 함수가 필요하지 않습니다.
// ==============================================================


// ==============================================================
// 3. 경로 조작 및 자원 삽입 (Path Traversal)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 상위 경로 이동 문자(../)가 포함되면 시스템 파일 유출 가정
// [EN] Simulation: Assume system file leakage if path traversal chars (../) exist
exports.vulnerablePath = functions.https.onRequest((req, res) => {
    const fileName = req.query.file || "report.txt";

    if (fileName.includes("../") || fileName.includes("..\\")) {
        res.status(200).send(`
            <div style="border:2px solid red; padding:10px; background:#xffcccc;">
                <h3>⚠️ [KR] 시스템 파일 접근 성공! (Hacked)</h3>
                <p>Path: <code>/var/www/uploads/${fileName}</code></p>
                <hr>
                <strong>[ /etc/passwd Content ]</strong><br>
                root:x:0:0:root:/root:/bin/bash<br>
                daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin<br>
                bin:x:2:2:bin:/bin:/usr/sbin/nologin<br>
                ... (Sensitive Info Leaked)
            </div>
        `);
    } else {
        res.status(200).send(`
            <h3>📄 일반 파일 (Normal File)</h3>
            <p>File: ${fileName}</p>
            <p>Content: Security Report Q1 2024...</p>
        `);
    }
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 경로 이동 문자(../)를 공백으로 치환하여 무력화
// [EN] Secure: Neutralize path traversal by removing "../"
exports.securePath = functions.https.onRequest((req, res) => {
    let fileName = req.query.file || "report.txt";

    // [KR] 안전: 디코딩 후 상위 경로 문자 제거
    const safeName = decodeURIComponent(fileName).replace(/(\.\.\/|\.\.\\)/g, "");

    if (decodeURIComponent(fileName) !== safeName) {
        res.status(200).send(`
            <div style="border:2px solid green; padding:10px; background:#e6fffa;">
                <h3>🛡️ [KR] 공격 차단됨 (Blocked)</h3>
                <p>Input: ${fileName}</p>
                <p>Filtered: <strong>${safeName}</strong></p>
                <hr>
                <p>[KR] 경로 조작 문자가 제거되었습니다.</p>
                <p>[EN] Path traversal characters have been removed.</p>
            </div>
        `);
    } else {
        res.status(200).send(`
            <h3>✅ 안전한 접근 (Secure Access)</h3>
            <p>File: ${safeName}</p>
            <p>Content: Security Report Q1 2024...</p>
        `);
    }
});


// ==============================================================
// 4. SQL 삽입 (SQL Injection)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] ' OR '1'='1 패턴 입력 시 관리자 권한 탈취 가정
// [EN] Simulation: Assume admin takeover if ' OR '1'='1 pattern is input
exports.vulnerableSQL = functions.https.onRequest((req, res) => {
    const userId = req.query.id || "";
    
    // [KR] 취약점: 입력값이 쿼리문의 구조를 변경함
    if (userId.includes("' OR '1'='1") || userId.includes("' or '1'='1")) {
        res.status(200).send(`
            <div style="color:red; border:2px solid red; padding:10px; background:#fff0f0;">
                <h3>⚠️ [KR] SQL 삽입 성공! (Hacked)</h3>
                <p>Query: <code>SELECT * FROM users WHERE id = '${userId}'</code></p>
                <p>[KR] 무조건 참(True)이 되어 모든 정보가 노출됩니다.</p>
                <p>[EN] Always True condition exposes all data.</p>
            </div>
        `);
    } else {
        res.status(200).send(`
            <h3>ℹ️ 일반 조회 (Normal Query)</h3>
            <p>ID: ${userId}</p>
            <p>Result: Public Profile...</p>
        `);
    }
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 특수문자(')를 제거하거나 파라미터 바인딩 시뮬레이션
// [EN] Secure: Simulate parameter binding or remove special char (')
exports.secureSQL = functions.https.onRequest((req, res) => {
    const userId = req.query.id || "";

    // [KR] 안전: 위험 문자(') 제거
    const safeId = userId.replace(/'/g, ""); 

    res.status(200).send(`
        <div style="color:green; border:2px solid green; padding:10px; background:#f0fff0;">
            <h3>🛡️ [KR] 방어 성공 (Secure)</h3>
            <p>Query: <code>SELECT * FROM users WHERE id = ? (Binding: ${safeId})</code></p>
            <p>[KR] 입력값이 단순 문자열로 처리되었습니다.</p>
            <p>[EN] Input treated as a literal string.</p>
        </div>
    `);
});


// ==============================================================
// 5. 코드 삽입 (Code Injection)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 사용자가 입력한 코드를 eval()로 그대로 실행
// [EN] Vulnerable: Execute user input code directly with eval()
exports.vulnerableCode = functions.https.onRequest((req, res) => {
    const expression = req.query.exp || "1+1";
    let result;
    try {
        // [KR] 위험: 입력값을 코드 그 자체로 실행
        result = eval(expression); 
    } catch (error) {
        result = "Error: " + error.message;
    }

    res.status(200).send(`
        <div style="border:2px solid red; padding:10px; background:#fff0f0;">
            <h3>⚠️ [KR] 코드 실행 결과 (Vulnerable)</h3>
            <p>Code: <code>${expression}</code></p>
            <p><strong>Result:</strong> ${result}</p>
            <hr>
            <p>[KR] eval() 함수를 통해 임의의 코드가 실행되었습니다.</p>
            <p>[EN] Arbitrary code executed via eval().</p>
        </div>
    `);
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 정규식으로 숫자와 연산자만 허용 (화이트리스트)
// [EN] Secure: Allow only numbers and operators (Whitelist)
exports.secureCode = functions.https.onRequest((req, res) => {
    const expression = req.query.exp || "1+1";
    let result;

    // [KR] 안전: 허용된 문자 패턴인지 검사
    const safePattern = /^[0-9+\-*/().\s]+$/;

    if (!safePattern.test(expression)) {
        res.status(200).send(`
            <div style="border:2px solid green; padding:10px; background:#f0fff0;">
                <h3>🛡️ [KR] 공격 차단됨 (Blocked)</h3>
                <p>Input: ${expression}</p>
                <hr>
                <p>[KR] 허용되지 않은 문자가 포함되어 실행을 거부했습니다.</p>
                <p>[EN] Execution blocked due to disallowed characters.</p>
            </div>
        `);
        return;
    }

    try {
        result = eval(expression); 
    } catch (error) {
        result = "Error";
    }

    res.status(200).send(`
        <h3>✅ 안전한 계산 (Secure Calc)</h3>
        <p>Exp: ${expression}</p>
        <p>Result: ${result}</p>
    `);
});


// ==============================================================
// 6. 부적절한 인가 (Insecure Direct Object References - IDOR)
// ==============================================================

// 가상 DB (Mock Database)
const mockDB = {
    "100": { owner: "userA", item: "Gaming Laptop", price: "$1500" },
    "101": { owner: "userB", item: "Smartphone", price: "$1000" },
    "102": { owner: "admin", item: "Master Key", price: "$999999" }
};

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 소유자 확인 없이 요청한 ID의 데이터를 바로 반환
// [EN] Vulnerable: Returns data for requested ID without ownership check
exports.vulnerableIDOR = functions.https.onRequest((req, res) => {
    const orderId = req.query.id || "100";
    const currentUser = "userA"; 

    // [KR] 취약점: 권한 검증 부재
    const data = mockDB[orderId];

    if (data) {
        res.status(200).send(`
            <div style="border:2px solid red; padding:10px; background:#fff0f0;">
                <h3>⚠️ [KR] 타인 정보 조회 성공! (Hacked)</h3>
                <p>Current User: ${currentUser}</p>
                <p>Requested ID: ${orderId}</p>
                <hr>
                <p><strong>Owner:</strong> ${data.owner}</p>
                <p><strong>Item:</strong> ${data.item}</p>
                <p style="color:red;">[KR] 본인의 주문이 아닌데도 조회가 되었습니다!</p>
                <p style="color:red;">[EN] Data accessed without ownership!</p>
            </div>
        `);
    } else {
        res.status(200).send("<h3>No Data</h3>");
    }
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 데이터 소유자와 현재 사용자가 일치하는지 검증
// [EN] Secure: Verify if data owner matches current user
exports.secureIDOR = functions.https.onRequest((req, res) => {
    const orderId = req.query.id || "100";
    const currentUser = "userA"; 

    const data = mockDB[orderId];

    if (data) {
        // [KR] 안전: 소유자 검증
        if (data.owner !== currentUser) {
            res.status(403).send(`
                <div style="border:2px solid green; padding:10px; background:#f0fff0;">
                    <h3>🛡️ [KR] 접근 권한 없음 (Access Denied)</h3>
                    <p>Current User: ${currentUser}</p>
                    <p>Owner: ${data.owner}</p>
                    <hr>
                    <p>[KR] 타인의 주문 내역은 조회할 수 없습니다.</p>
                    <p>[EN] You cannot access other user's order.</p>
                </div>
            `);
        } else {
            res.status(200).send(`
                <h3>✅ 정상 조회 (Authorized)</h3>
                <p>Item: ${data.item}</p>
            `);
        }
    } else {
        res.status(200).send("<h3>No Data</h3>");
    }
});
// ==============================================================
// 7. 운영체제 명령어 삽입 (OS Command Injection)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 사용자 입력을 시스템 명령어의 일부로 직접 사용
// [EN] Vulnerable: User input directly used in system command
exports.vulnerableCmd = functions.https.onRequest((req, res) => {
    const ip = req.query.ip || "8.8.8.8";

    // [가상 시나리오] 실제 서버에서는: exec("ping -c 1 " + ip)
    // 공격자가 "8.8.8.8; ls -al"을 입력하면 -> "ping -c 1 8.8.8.8; ls -al" 실행됨
    
    let output = `PING ${ip} (56 data bytes)\n64 bytes from ${ip}: icmp_seq=1 ttl=115 time=12.4 ms\n\n--- ${ip} ping statistics ---\n1 packets transmitted, 1 received, 0% packet loss`;

    // 시뮬레이션: 공격 패턴(; | &)이 있으면 해킹된 결과를 보여줌
    if (ip.includes(";") || ip.includes("|") || ip.includes("&")) {
        const command = ip.split(/;|\||&/)[1].trim(); // 뒤에 붙은 명령어 추출
        
        let hackedOutput = "";
        if (command.startsWith("ls")) {
            hackedOutput = `
drwxr-xr-x 2 root root 4096 May 20 10:00 .
drwxr-xr-x 3 root root 4096 May 20 09:00 ..
-rw-r--r-- 1 root root  512 May 20 10:01 secret_config.json
-rw-r--r-- 1 root root 1024 May 20 10:02 admin_password.txt
            `;
        } else if (command.startsWith("whoami")) {
            hackedOutput = "root";
        } else {
            hackedOutput = `Command not found: ${command}`;
        }

        res.status(200).send(`
            <div style="border:2px solid red; padding:10px; background:#2d2d2d; color:#00ff00; font-family:monospace;">
                <h3>⚠️ [KR] 터미널 실행 결과 (Hacked)</h3>
                <p>$ ping -c 1 ${ip}</p>
                <pre>${output}</pre>
                <hr style="border-color:#00ff00;">
                <p><strong>$ ${command}</strong></p>
                <pre>${hackedOutput}</pre>
            </div>
        `);
    } else {
        res.status(200).send(`
            <div style="background:#f0f0f0; padding:10px; font-family:monospace;">
                <h3>ℹ️ Ping Result</h3>
                <pre>${output}</pre>
            </div>
        `);
    }
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] IP 주소 형식(숫자와 점)만 허용하는 화이트리스트 검증
// [EN] Secure: Allow only IP address format (Whitelist)
exports.secureCmd = functions.https.onRequest((req, res) => {
    const ip = req.query.ip || "8.8.8.8";

    // IP 주소 정규식 (IPv4)
    const ipPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;

    if (!ipPattern.test(ip)) {
        res.status(200).send(`
            <div style="border:2px solid green; padding:10px; background:#f0fff0;">
                <h3>🛡️ [KR] 실행 차단 (Blocked)</h3>
                <p>Input: ${ip}</p>
                <hr>
                <p>[KR] 잘못된 IP 주소 형식이거나, 금지된 문자가 포함되어 있습니다.</p>
                <p>[EN] Invalid IP format or forbidden characters detected.</p>
            </div>
        `);
    } else {
        res.status(200).send(`
            <div style="background:#f0f0f0; padding:10px; font-family:monospace;">
                <h3>✅ Safe Ping Result</h3>
                <pre>PING ${ip} ... (Normal Execution)</pre>
            </div>
        `);
    }
});
// ==============================================================
// 8. 오류 메시지 정보 노출 (Security Misconfiguration)
// ==============================================================

// 🚫 취약한 코드 (Vulnerable Mode)
// [KR] 에러 발생 시 스택 트레이스(Stack Trace)를 그대로 노출
// [EN] Vulnerable: Expose full stack trace to the user
exports.vulnerableError = functions.https.onRequest((req, res) => {
    try {
        // [시나리오] DB 연결을 시도하다가 에러가 발생한 상황 연출
        // 존재하지 않는 함수를 호출하여 강제로 에러 유발
        const dbConnection = database.connect("192.168.0.10", "root", "password123");
    } catch (error) {
        // ⚠️ 위험: 개발자용 에러 메시지(내부 정보 포함)를 사용자에게 그대로 보여줌
        res.status(500).send(`
            <div style="border:2px solid red; padding:10px; background:#fff0f0; font-family:monospace;">
                <h3>⚠️ 500 Internal Server Error</h3>
                <p style="color:red; font-weight:bold;">ReferenceError: database is not defined</p>
                <hr>
                <p><strong>Stack Trace:</strong></p>
                <pre>${error.stack}</pre>
                <hr>
                <p><strong>[KR] 해커가 얻은 정보:</strong></p>
                <ul>
                    <li>오류 원인 (변수명 노출)</li>
                    <li>서버 내부 파일 경로 (/user_code/index.js...)</li>
                    <li>사용 중인 함수 로직 위치</li>
                </ul>
            </div>
        `);
    }
});

// ✅ 안전한 코드 (Secure Mode)
// [KR] 에러 발생 시 내부 정보를 숨기고, 약속된 일반 메시지만 출력
// [EN] Secure: Hide details and show generic error message
exports.secureError = functions.https.onRequest((req, res) => {
    try {
        // 동일하게 강제 에러 유발
        const dbConnection = database.connect("192.168.0.10", "root", "password123");
    } catch (error) {
        // 🛡️ 방어: 상세 내용은 서버 로그(console.error)에만 남기고,
        // 사용자에게는 "서비스 이용에 불편을 드려 죄송합니다" 같은 단순 메시지만 전달
        console.error("System Error:", error); // 내부 로그 기록

        res.status(500).send(`
            <div style="border:2px solid green; padding:10px; background:#f0fff0;">
                <h3>✅ 서비스 오류 (Service Error)</h3>
                <p>시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.</p>
                <p style="color:gray; font-size:0.9em;">(Error Code: 500)</p>
                <hr>
                <p><strong>[KR] 방어 성공:</strong> 내부 정보가 전혀 노출되지 않았습니다.</p>
            </div>
        `);
    }
});
