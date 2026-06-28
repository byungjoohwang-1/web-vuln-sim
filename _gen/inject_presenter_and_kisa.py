# -*- coding: utf-8 -*-
import os
import re

PUB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))

# KISA Software Development Security Guide (2021) Mapping
KISA_MAPPING = {
    "03_code_sql_injection.html": ("1.1", "SQL 삽입", "16"),
    "03_code_path_traversal.html": ("1.2", "경로 조작 및 자원 삽입", "25"),
    "03_code_xss.html": ("1.3", "크로스사이트 스크립트", "33"),
    "03_code_os_command.html": ("1.4", "운영체제 명령어 삽입", "42"),
    "03_code_dangerous_file_upload.html": ("1.5", "위험한 형식 파일 업로드", "49"),
    "03_code_untrusted_input.html": ("1.6", "신뢰생성 보안결정", "56"),
    "03_code_csrf.html": ("1.7", "크로스사이트 요청 위조", "61"),
    "03_code_bufferoverflow.html": ("1.8", "메모리 버퍼 오버플로우", "68"),
    "03_code_formatstring.html": ("1.9", "포맷 스트링 삽입", "74"),
    "03_code_http_split.html": ("1.10", "HTTP 응답분할", "79"),
    "03_code_dns_security_decision.html": ("7.1", "DNS lookup에 의존한 보안결정", "284"),
    "03_code_error_handling_missing.html": ("4.2", "오류 상황 대응 부재", "212"),
    "03_code_error_message.html": ("4.1", "에러 메시지를 통한 정보노출", "206"),
    "03_code_hardedcode.html": ("2.4", "하드코드된 중요 정보", "132"),
    "03_code_impropersignature.html": ("2.12", "무결성 검증 없는 코드 다운로드", "172"),
    "03_code_impropersignature_validity.html": ("2.12", "무결성 검증 없는 코드 다운로드", "172"),
    "03_code_improper_auth_attempts.html": ("2.9", "패스워드 최소 요구조건 미흡", "166"),
    "03_code_improper_exception.html": ("4.3", "부적절한 예외 처리", "218"),
    "03_code_improper_resource_release.html": ("5.2", "부적절한 자원 해제", "230"),
    "03_code_inapporiate_auth.html": ("2.1", "적절한 인증 없는 중요기능 수행", "114"),
    "03_code_infinite_loop.html": ("3.2", "종료되지 않는 반복문 또는 재귀", "199"),
    "03_code_integer_overflow.html": ("1.8", "정수 오버플로우", "68"),
    "03_code_ldap_injection.html": ("1.13", "LDAP 삽입", "95"),
    "03_code_missing_auth.html": ("2.1", "적절한 인증 없는 중요기능 수행", "114"),
    "03_code_nointegritycode.html": ("2.12", "무결성 검증 없는 코드 다운로드", "172"),
    "03_code_nosalthash.html": ("2.11", "솔트 없는 일방향 암호화", "179"),
    "03_code_notenoughkey.html": ("2.6", "충분하지 않은 키 길이 사용", "147"),
    "03_code_no_encrypted_info.html": ("2.5", "암호화되지 않은 중요 정보", "139"),
    "03_code_null_pointer.html": ("5.1", "Null Pointer 역참조", "224"),
    "03_code_open_redirect.html": ("1.14", "크로스사이트 리다이렉트", "101"),
    "03_code_private_array_return.html": ("6.4", "Public 메소드로부터 반환된 Private 배열", "270"),
    "03_code_public_to_private_array.html": ("6.5", "Private 메소드에 Public 배열이 인자로 전달", "277"),
    "03_code_race_condition.html": ("3.1", "경쟁 조건", "192"),
    "03_code_risky_crypto.html": ("2.8", "약한 암호 알고리즘 사용", "159"),
    "03_code_sensitiveinfo_sourcecodecomments.html": ("6.3", "시스템 데이터 정보 노출", "263"),
    "03_code_session_data_exposure.html": ("6.1", "잘못된 세션에 의한 데이터 노출", "249"),
    "03_code_ssrf.html": ("1.15", "서버측 요청 위조", "107"),
    "03_code_uninitialized_variable.html": ("5.3", "초기화되지 않은 변수 사용", "236"),
    "03_code_useofinsufficient_random.html": ("2.7", "적절하지 않은 난수 값 사용", "153"),
    "03_code_use_after_free.html": ("1.8", "메모리 버퍼 오버플로우 (UAF)", "68"),
    "03_code_vulnerable_api.html": ("7.2", "취약한 API 사용", "291"),
    "03_code_weakpassword.html": ("2.9", "패스워드 최소 요구조건 미흡", "166"),
    "03_code_wrong_auth.html": ("2.2", "부적절한 인가", "120"),
    "03_code_xml.html": ("1.12", "XML 삽입", "89"),
    "03_code_xxe.html": ("1.15", "서버측 요청 위조 (XXE)", "107"),
    "03_code_cookiedisclosure.html": ("2.12", "중요정보 노출 (쿠키)", "185"),
    "03_code_processvalidation.html": ("2.2", "부적절한 인가 (프로세스 검증 누락)", "120"),
    "03_code_codeinjection.html": ("1.4", "운영체제 명령어 삽입 (코드 주입)", "42"),
    "03_code_deserialization.html": ("5.4", "신뢰할 수 없는 데이터의 역직렬화", "242"),
}

PRESENTER_CSS = """
    <!-- Presenter Mode Styling -->
    <style>
        body.presenter-mode {
            font-size: 1.15rem !important;
        }
        body.presenter-mode .code-display, body.presenter-mode .code-textarea {
            font-size: 18px !important;
            line-height: 1.8 !important;
        }
        body.presenter-mode .checklist-item {
            font-size: 16px !important;
        }
        body.presenter-mode .exploit-panel {
            border: 2px solid #eab308 !important;
            box-shadow: 0 15px 35px rgba(234, 179, 8, 0.25) !important;
        }
        body.presenter-mode .panel-title {
            font-size: 22px !important;
        }
        body.presenter-mode .header h1 {
            font-size: 32px !important;
        }
    </style>
"""

PRESENTER_JS = """
    <!-- Presenter Mode Script -->
    <script>
        function togglePresenterMode() {
            const isPresenter = document.body.classList.toggle('presenter-mode');
            localStorage.setItem('wvs_presenter', isPresenter ? 'on' : 'off');
            updatePresenterButton();
        }
        function updatePresenterButton() {
            const btn = document.getElementById('btn-presenter');
            if (!btn) return;
            const isEn = localStorage.getItem('wvs_lang') === 'en';
            if (document.body.classList.contains('presenter-mode')) {
                btn.style.background = '#22c55e';
                btn.style.color = '#fff';
                btn.textContent = isEn ? '🎤 Presenter: ON' : '🎤 발표자 모드: 켜짐';
                btn.setAttribute('data-en', '🎤 Presenter: ON');
                btn.dataset.ko = '🎤 발표자 모드: 켜짐';
            } else {
                btn.style.background = '#eab308';
                btn.style.color = '#000';
                btn.textContent = isEn ? '🎤 Presenter Mode' : '🎤 발표자 모드';
                btn.setAttribute('data-en', '🎤 Presenter Mode');
                btn.dataset.ko = '🎤 발표자 모드';
            }
        }
        // Run on load
        (function() {
            if (localStorage.getItem('wvs_presenter') === 'on') {
                document.body.classList.add('presenter-mode');
            }
            window.addEventListener('DOMContentLoaded', updatePresenterButton);
        })();
    </script>
"""

def inject_presenter_and_kisa(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already injected
    if "Presenter Mode Script" in content:
        print(f"[-] Already has presenter mode: {filename}")
        return

    # 1. Inject CSS and SAST Script reference
    head_close = content.find("</head>")
    if head_close != -1:
        sast_script = '\n    <script src="/js/sast-engine.js"></script>\n'
        content = content[:head_close] + PRESENTER_CSS + sast_script + content[head_close:]

    # 2. Inject JS before </body>
    body_close = content.rfind("</body>")
    if body_close != -1:
        content = content[:body_close] + PRESENTER_JS + content[body_close:]

    # 3. Inject Button in Langbar
    langbar_str = '<div class="langbar"><button id="lang-ko" onclick="setLang(\'ko\')">한국어</button><button id="lang-en" onclick="setLang(\'en\')">EN</button></div>'
    new_langbar_str = '<div class="langbar"><button id="lang-ko" onclick="setLang(\'ko\')">한국어</button><button id="lang-en" onclick="setLang(\'en\')">EN</button><button id="btn-presenter" onclick="togglePresenterMode()" style="background:#eab308;color:#000;margin-left:5px;border:none;padding:5px 11px;border-radius:6px;font:600 12px/1 \'Malgun Gothic\',sans-serif;cursor:pointer;" data-en="🎤 Presenter Mode">🎤 발표자 모드</button></div>'
    content = content.replace(langbar_str, new_langbar_str)

    # 4. Inject KISA Guide Reference in Header
    if filename in KISA_MAPPING:
        sec, title, page = KISA_MAPPING[filename]
        guide_html = f"""
            <!-- KISA Guide Mapping Reference -->
            <div class="kisa-guide-reference" style="margin-top: 10px; display: inline-flex; align-items: center; gap: 8px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); padding: 6px 12px; border-radius: 6px; font-size: 13px; color: #1e40af; font-weight: 500;">
                <span style="background: #1e40af; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; font-family: sans-serif;">KISA Guide</span>
                <span data-en="KISA Secure Coding Guide (2021) Sec {sec} (p. {page})">행정안전부·KISA 개발보안 가이드 (2021) - {sec} {title} (p. {page})</span>
            </div>
        """
        
        # Inject right after the description <p> in <div class="header">
        header_pos = content.find('<div class="header">')
        if header_pos != -1:
            header_end_pos = content.find('</div>', header_pos)
            if header_end_pos != -1:
                content = content[:header_end_pos] + guide_html + content[header_end_pos:]
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[+] Presenter & KISA reference injected successfully: {filename}")


def main():
    print("Injecting Presenter Mode, KISA guide reference, and sast-engine.js into practice pages...")
    for filename in os.listdir(PUB_DIR):
        if filename.startswith("03_code_") and filename.endswith(".html"):
            filepath = os.path.join(PUB_DIR, filename)
            inject_presenter_and_kisa(filepath)

if __name__ == "__main__":
    main()
