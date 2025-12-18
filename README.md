-----

# 📚 WEB-VULN-SIM: 웹 취약점 시뮬레이터 (v0.5)
Link https://vuln-sim-test.web.app/
Notice: This similator with secure coding is for education only. If you have any questions, please feel free to contact me to jackhwang0210@gmail.com
Copyright 2025 Jack Hwang. This program is complied with Apache License 2.0.
## 🇰🇷 한국어 버전

## 💡 프로젝트 소개

**WEB-VULN-SIM**은 개발자와 보안 학습자가 웹 애플리케이션의 **주요 보안 취약점**을 직접 체험하고 **Secure Coding Guideline**을 학습할 수 있도록 설계된 교육용 웹 애플리케이션입니다.

  * **목적**: 실제 공격 시나리오를 시뮬레이션하여 취약점의 원리를 이해하고, 안전한 코딩 기법을 습득합니다.
  * **기술 기반**: Google Firebase Hosting을 기반으로 동작하여 접근성과 배포 용이성을 확보했습니다.
  * **보안 가이드**: KISA(한국인터넷진흥원)의 **SW 개발 보안 약점 가이드**와 파이썬 코딩 가이드라인을 참고하여 **취약점별 방어(Secure Coding) 방법**을 상세히 설명합니다.

V0.5 주요 기능 추가(2025-12-16)
1) 웹 보안 취약점 시뮬레이터를 20개로 추가 했습니다-2) KISA 기준으로 보안 기능에 대해 직접 실습 할 수 있는 16개의 취약점 기능을 추가 했습니다.(Korean Only)

## ✨ 주요 시뮬레이션 및 학습 항목

| 분류 | 취약점 파일명 | 내용 |
| :--- | :--- | :--- |
| **인젝션** | `sim-sql.html` | SQL Injection 시뮬레이션 |
| | `sim-xss.html` | Cross-Site Scripting (XSS) 시뮬레이션 |
| | `sim-cmd.html` | Command Injection 시뮬레이션 |
| | `sim-xxe.html` | XXE (XML External Entity) 시뮬레이션 |
| **접근/인가** | `sim-idor.html` | IDOR (Insecure Direct Object Reference) 시뮬레이션 |
| | `sim-csrf.html` | CSRF (Cross-Site Request Forgery) 시뮬레이션 |
| **서버/네트워크** | `sim-ssrf.html` | SSRF (Server-Side Request Forgery) 시뮬레이션 |
| | `sim-path.html` | 경로 조작 (Path Traversal) 시뮬레이션 |
| | `sim-upload.html` | 파일 업로드 취약점 시뮬레이션 |
| **기타** | `sim-brute.html` | Brute Force 시뮬레이션 |
| **가이드** | `guide-input.html` | 2-1. 입력 데이터 검증 가이드 |
| | `guide-security.html` | 2-2. 보안 기능 가이드 |
| | `sim-error-handling.html` | 2-4. 에러 처리 실습 |

-----

## 🛠️ 기술 스택 (Tech Stack)

  * **Frontend**: HTML5, CSS (Bootstrap 5), JavaScript
  * **Backend**: Firebase Cloud Functions (Node.js)
  * **Hosting**: Firebase Hosting
  * **Online Demo**: [https://vuln-sim-test.web.app/](https://vuln-sim-test.web.app/)

-----

## 🚀 설치 및 환경 구성 가이드

### 📋 사전 준비 사항 (Prerequisites)

이 프로젝트를 실행하기 위해서는 다음 도구들이 설치되어 있어야 합니다.

1.  **Node.js**: [최신 LTS 버전](https://nodejs.org/) 설치
2.  **Firebase CLI**: 터미널에서 다음 명령어를 실행하여 설치합니다.
    ```bash
    npm install -g firebase-tools
    ```

### 1단계: 프로젝트 폴더 생성 및 Firebase 초기화

```bash
# 폴더 생성 및 이동
mkdir C:\WEB-VULN-SIM
cd C:\WEB-VULN-SIM

# Firebase 로그인 (브라우저가 열림)
firebase login

# Firebase 프로젝트 초기화 (대화형 프롬프트 진행)
firebase init
```

  * **Which Firebase features...?**: `Hosting` 및 `Functions` 선택
  * **Project Setup**: 기존 프로젝트 선택
  * **Functions Setup**: Language: `JavaScript`, ESLint: `No`, Install dependencies: `Yes`
  * **Hosting Setup**: Public directory: `public`, Single-page app: `No`

### 2단계: 파일 구성 및 배치

초기화 후 생성된 `public` 폴더 내부에 모든 HTML 소스 코드(`index.html`, `guide-*.html`, `sim-*.html` 등)를 배치합니다.

```
📂 C:\WEB-VULN-SIM
├── functions/ (서버 로직 index.js 등)
└── public/ (★ 모든 HTML 파일 위치)
    ├── index.html
    ├── guide-input.html
    ├── sim-sql.html
    └── ... (기타 시뮬레이터 파일들)
```

-----

## ▶️ 실행 및 배포 (Usage)

### 로컬에서 테스트하기

코드를 수정하고 로컬 환경에서 미리 테스트합니다.

```bash
firebase serve
# 또는
firebase emulators:start
```

접속 주소: `http://localhost:5000`

### 서버에 배포하기

테스트가 완료되면 Firebase Hosting 서버에 배포합니다.

```bash
firebase deploy
```

배포 완료 후 Hosting URL이 출력됩니다.

-----

-----

## 🇬🇧 English Version

# 📚 WEB-VULN-SIM: Web Vulnerability Simulator (v1.0)

## 💡 Project Overview

**WEB-VULN-SIM** is an educational web application designed to help developers and security learners simulate and study **major web security vulnerabilities** and corresponding **Secure Coding Guidelines**.

  * **Objective**: To simulate real-world attack scenarios, understand vulnerability principles, and acquire safe coding techniques.
  * **Platform**: The project runs on Google Firebase Hosting for high accessibility and easy deployment.
  * **Guidelines**: Secure coding practices are detailed based on the **KISA (Korea Internet & Security Agency) SW Development Security Weakness Guide** and Python coding guidelines.

-----

## ✨ Key Simulations and Learning Topics

| Category | Filename | Description |
| :--- | :--- | :--- |
| **Injection** | `sim-sql.html` | SQL Injection Simulation |
| | `sim-xss.html` | Cross-Site Scripting (XSS) Simulation |
| | `sim-cmd.html` | Command Injection Simulation |
| | `sim-xxe.html` | XXE (XML External Entity) Simulation |
| **Access/Auth** | `sim-idor.html` | IDOR (Insecure Direct Object Reference) Simulation |
| | `sim-csrf.html` | CSRF (Cross-Site Request Forgery) Simulation |
| **Server/Network** | `sim-ssrf.html` | SSRF (Server-Side Request Forgery) Simulation |
| | `sim-path.html` | Path Traversal Simulation |
| | `sim-upload.html` | File Upload Vulnerability Simulation |
| **Others** | `sim-brute.html` | Brute Force Simulation |
| **Guides** | `guide-input.html` | 2-1. Input Data Validation Guide |
| | `guide-security.html` | 2-2. Security Function Guide |
| | `sim-error-handling.html` | 2-4. Error Handling Practice |

-----

## 🛠️ Tech Stack

  * **Frontend**: HTML5, CSS (Bootstrap 5), JavaScript
  * **Backend**: Firebase Cloud Functions (Node.js)
  * **Hosting**: Firebase Hosting
  * **Online Demo**: [https://vuln-sim-test.web.app/](https://vuln-sim-test.web.app/)

-----

## 🚀 Installation & Setup Guide

### 📋 Prerequisites

The following tools must be installed to run and deploy the project:

1.  **Node.js**: Install the [latest LTS version](https://nodejs.org/).
2.  **Firebase CLI**: Install the command-line tool globally via npm:
    ```bash
    npm install -g firebase-tools
    ```

### Step 1: Create Project Directory and Initialize Firebase

```bash
# Create and navigate to the folder
mkdir C:\WEB-VULN-SIM
cd C:\WEB-VULN-SIM

# Firebase Login
firebase login

# Initialize Firebase Project (Follow interactive prompts)
firebase init
```

  * **Which Firebase features...?**: Select `Hosting` and `Functions`
  * **Project Setup**: Select an existing project
  * **Functions Setup**: Language: `JavaScript`, ESLint: `No`, Install dependencies: `Yes`
  * **Hosting Setup**: Public directory: `public`, Single-page app: `No`

### Step 2: File Structure Configuration

Place all the HTML source files (`index.html`, `guide-*.html`, `sim-*.html`, etc.) inside the generated `public` folder.

```
📂 C:\WEB-VULN-SIM
├── functions/ (Server logic index.js, etc.)
└── public/ (★ All HTML files go here)
    ├── index.html
    ├── guide-security.html
    ├── sim-xss.html
    └── ... (Other simulation files)
```

-----

## ▶️ Usage (Run & Deploy)

### Run Locally (Testing)

Test the application on your local machine before deploying.

```bash
firebase serve
# OR
firebase emulators:start
```

Access at: `http://localhost:5000`

### Deploy to Server

Deploy the application to Firebase Hosting for public access.

```bash
firebase deploy
```

The Hosting URL will be displayed upon completion.

-----

## ⚠️ Disclaimer

This application is created for **educational purposes only**. The attack techniques demonstrated here must **NEVER** be used on systems you do not own or have explicit permission to test.


