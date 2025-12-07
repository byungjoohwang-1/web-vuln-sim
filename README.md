# 🛡️ Web Vulnerability Simulator & Secure coding guideline

Website: https://vuln-sim-test.web.app/ 

WEB-VULN-SIM (웹 보안 취약점 시뮬레이터)

이 프로젝트는 웹 애플리케이션의 주요 보안 취약점(SQL Injection, XSS, CSRF 등)을 학습하고 시뮬레이션할 수 있는 교육용 웹 애플리케이션입니다. Google Firebase Hosting을 기반으로 동작합니다.  그리고 Secure coding guideline을 설명 합니다.
Secure coding guideline은 KISA의 SW개발 보안 약점 가이드와 파이싼 코딩 가이드라인을 참고 하였습니다.

📋 사전 준비 사항 (Prerequisites)

이 프로젝트를 실행하기 위해서는 다음 도구들이 설치되어 있어야 합니다.

Node.js: https://nodejs.org/ 에서 최신 LTS 버전을 다운로드하여 설치하세요.

Firebase CLI: 터미널(CMD 또는 PowerShell)에서 다음 명령어를 입력하여 설치합니다.

npm install -g firebase-tools


🚀 설치 및 환경 구성 가이드

1단계: 프로젝트 폴더 생성 및 Firebase 초기화

C드라이브(또는 원하는 위치)에 프로젝트 폴더를 만들고 Firebase 기본 구조를 생성하는 과정입니다.

폴더 생성 및 이동

C:\ 경로에 WEB-VULN-SIM 폴더를 생성합니다.

터미널(CMD 또는 PowerShell)을 열고 해당 폴더로 이동합니다.

cd C:\WEB-VULN-SIM


Firebase 로그인

firebase login


브라우저가 열리면 Google 계정으로 로그인합니다.

Firebase 프로젝트 초기화

firebase init


Which Firebase features do you want to set up?

키보드 방향키와 스페이스바를 이용해 **Hosting: Configure files for Firebase Hosting**과 **Functions: Configure a Cloud Functions directory**를 선택(체크)하고 엔터를 누릅니다.

Project Setup

Use an existing project를 선택하고, 미리 만들어둔 Firebase 프로젝트를 선택합니다. (없다면 Create a new project 선택)

Functions Setup

언어는 JavaScript를 선택합니다.

ESLint 사용 여부는 N (No)를 선택합니다.

의존성 설치 여부는 Y (Yes)를 선택합니다.

Hosting Setup

What do you want to use as your public directory?: public (기본값 엔터)

Configure as a single-page app?: N (No)

Set up automatic builds and deploys with GitHub?: N (No)

2단계: 파일 구성 및 배치 (이미지 구조 적용)

초기화가 완료되면 public 폴더와 functions 폴더가 생성됩니다. 아래 구조와 같이 파일들을 작성하고 배치하세요.

📂 전체 디렉토리 구조

C:\WEB-VULN-SIM
├── .firebase/
├── functions/
│   ├── node_modules/
│   ├── index.js          <-- (백엔드 로직이 필요한 경우 수정)
│   ├── package.json
│   └── ...
├── public/               <-- (★ 핵심: HTML 파일들을 이곳에 넣습니다)
│   ├── 404.html
│   ├── config.js
│   ├── index.html        <-- (메인 대시보드)
│   ├── guide-input.html  <-- (2-1. 입력 데이터 검증 가이드)
│   ├── guide-security.html <-- (2-2. 보안 기능 가이드)
│   ├── sim-sql.html      <-- (1. SQL Injection 시뮬레이터)
│   ├── sim-xss.html      <-- (3. XSS 시뮬레이터)
│   ├── sim-csrf.html     <-- (11. CSRF 시뮬레이터)
│   ├── sim-cmd.html      <-- (5. Command Injection 시뮬레이터)
│   ├── sim-upload.html   <-- (6. 파일 업로드 시뮬레이터)
│   ├── sim-path.html     <-- (3. 경로 조작 시뮬레이터)
│   ├── sim-ssrf.html     <-- (12. SSRF 시뮬레이터)
│   ├── sim-xxe.html      <-- (8. XXE 시뮬레이터)
│   ├── sim-brute.html    <-- (16. Brute Force 시뮬레이터)
│   ├── sim-idor.html     <-- (부적절한 인가 시뮬레이터)
│   ├── sim-error-handling.html <-- (2-4. 에러 처리)
│   ├── sim-quality.html   <-- (2-5. 코드 품질)
│   ├── sim-encap.html     <-- (2-6. 캡슐화)
│   ├── sim-time-state.html <-- (2-3. 시간 및 상태)
│   └── ... (기타 시뮬레이터 파일들)
├── firebase.json
└── ...


public 폴더: 작성한 모든 HTML 소스 코드(index.html, guide-*.html, sim-*.html 등)를 이 폴더 안에 넣습니다.

기존에 생성된 index.html이 있다면 덮어씌웁니다.

functions 폴더: 서버 사이드 로직이 필요한 경우 index.js를 수정합니다. (단순 정적 호스팅만 할 경우 기본 상태로 두어도 무방합니다.)

▶️ 실행 및 배포 (Usage)

1. 로컬에서 테스트하기

코드를 수정하고 웹사이트가 잘 작동하는지 내 컴퓨터에서 미리 확인해볼 수 있습니다.

firebase serve
# 또는
firebase emulators:start


명령어 실행 후 출력되는 Local server: http://localhost:5000 주소로 접속하여 확인합니다.

2. 서버에 배포하기

테스트가 끝났다면 실제 Firebase Hosting 서버에 배포하여 누구나 접속할 수 있게 합니다.

firebase deploy


배포가 완료되면 Hosting URL: https://your-project-id.web.app 주소가 출력됩니다.

🛠️ 주요 파일 설명

public/index.html: 웹 사이트의 메인 화면입니다. 사이드바 메뉴를 통해 각 시뮬레이터와 가이드로 이동할 수 있습니다.

public/guide-input.html: 입력 데이터 검증 및 표현에 대한 17개 보안 약점 가이드(Java/Python 예제 포함)입니다.

public/guide-security.html: 보안 기능에 대한 16개 보안 약점 가이드(Java/Python 예제 포함)입니다.

public/sim-*.html: 각 취약점(SQL Injection, XSS 등)을 직접 실습해볼 수 있는 시뮬레이터 페이지들입니다.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
(English)
WEB-VULN-SIM (Web Vulnerability Simulator)

WEB-VULN-SIM is an educational web application designed to simulate and demonstrate various web security vulnerabilities (SQL Injection, XSS, CSRF, etc.) and provide secure coding guidelines. This project is built to run on Google Firebase Hosting.

📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:

Node.js: Download and install the latest LTS version from nodejs.org.

Firebase CLI: Install the Firebase command-line tool via npm:

npm install -g firebase-tools


🚀 Installation & Setup Guide

Follow these steps to set up the project structure on your local machine (Windows environment).

Step 1: Create Project Directory

Create a dedicated folder for this project on your C:\ drive and navigate into it.

Open Command Prompt (CMD) or PowerShell.

Run the following commands:

mkdir C:\WEB-VULN-SIM
cd C:\WEB-VULN-SIM


Step 2: Initialize Firebase

Initialize the Firebase project structure within the folder.

Login to Firebase:

firebase login


Initialize Project:

firebase init


Follow the interactive prompts:

Which Firebase features do you want to set up?

Select Hosting: Configure files for Firebase Hosting and Functions: Configure a Cloud Functions directory (Press Space to select, Enter to confirm).

Project Setup: Select Use an existing project (Select your created Firebase project).

Functions Setup:

What language would you like to use to write Cloud Functions? -> JavaScript

Do you want to use ESLint to catch probable bugs and enforce style? -> No

Do you want to install dependencies with npm now? -> Yes

Hosting Setup:

What do you want to use as your public directory? -> Type public (Default).

Configure as a single-page app (rewrite all urls to /index.html)? -> No.

Set up automatic builds and deploys with GitHub? -> No (or Yes if you need CI/CD).

Step 3: File Structure & Configuration

Once initialized, your folder structure will look like the tree below. You must place the HTML/JS files into the public/ directory as shown in the project screenshots.

📂 Project Structure

C:\WEB-VULN-SIM
├── .firebase/
├── .firebaserc
├── firebase.json
├── functions/              <-- Backend logic (if needed)
│   ├── index.js
│   └── package.json
└── public/                 <-- ★ PLACE ALL HTML FILES HERE
    ├── 404.html
    ├── index.html          <-- Main Dashboard (Dashboard)
    ├── config.js
    │
    │   <!-- 1. Simulator Files -->
    ├── sim-sql.html        <-- SQL Injection
    ├── sim-cmd.html        <-- Command Injection
    ├── sim-xxe.html        <-- XXE Injection
    ├── sim-xss.html        <-- Reflected XSS
    ├── sim-csrf.html       <-- CSRF Attack
    ├── sim-ssrf.html       <-- SSRF
    ├── sim-upload.html     <-- File Upload
    ├── sim-path.html       <-- Path Traversal
    ├── sim-split.html      <-- HTTP Splitting
    ├── sim-brute.html      <-- Brute Force
    ├── sim-idor.html       <-- IDOR
    ├── sim-code.html       <-- Code Injection
    │
    │   <!-- 2. Guide & Extra Files -->
    ├── guide-input.html    <-- 2-1. Input Validation Guide
    ├── guide-security.html <-- 2-2. Security Function Guide
    ├── sim-time-state.html <-- 2-3. Time & State
    ├── sim-error-handling.html <-- 2-4. Error Handling
    ├── sim-quality.html    <-- 2-5. Code Quality
    └── sim-encap.html      <-- 2-6. Encapsulation


Action: Copy all the generated HTML codes (from the previous steps) and save them into the C:\WEB-VULN-SIM\public\ folder with the filenames listed above.

▶️ Usage (Run & Deploy)

1. Run Locally (Testing)

You can test the application locally before deploying it to the web.

firebase serve
# OR
firebase emulators:start


Access the local server at: http://localhost:5000

2. Deploy to Firebase Hosting

To make your simulator accessible online:

firebase deploy


Once completed, your Hosting URL will be displayed (e.g., https://your-project-id.web.app).

🛠️ Tech Stack

Frontend: HTML5, CSS (Bootstrap 5), JavaScript (Vanilla)

Backend: Firebase Cloud Functions (Node.js)

Hosting: Firebase Hosting

⚠️ Disclaimer

This application is for educational purposes only. Do not use the attack techniques demonstrated here on systems you do not own or have explicit permission to test.
