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

V0.6 주요 기능 추가(2026-06-20)
1) **전자금융 보안 특화 시뮬레이터 10종** 신설 — 거래정보 무결성/재사용(리플레이) 방지, 금융형 IDOR(소유주 검증), 거래 인증수단 검증, 고정 인증코드, 루팅·탈옥 탐지, 앱 위·변조/안티디버깅, HTS 실행 파라미터 재사용, 초기화 비밀번호 규칙성, 유추 가능한 인증정보(복잡도). (출처: 금융보안원 「전자금융기반시설 보안 취약점 평가기준(제2026-1호)」 개념 재구성)
2) **시큐어 코딩 KISA 49개 보안약점 100% 커버 완성** — 기존 입력검증(17)·보안기능(16)에 더해 시간/상태(2), 에러처리(3), 코드오류(5: Null Pointer 역참조·자원 해제·Use-After-Free·미초기화 변수·역직렬화), 캡슐화(4), API 오용(2) 등 16개 시큐어 코딩 랩 추가.
3) **인프라 점검 확장** — UNIX 서비스 관리 18종(U-34~U-61: finger/r-command/NFS/RPC/NIS/Sendmail/DNS/SNMP 등) 및 DBMS 14종(D-05~D-24) 추가로 DB 점검 D-26까지 완성. 기존 깨진 내부 링크도 정리.

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

## 📑 출처 및 참고자료 (References)

본 시뮬레이터의 점검 항목은 아래 공개 가이드라인을 **개념적으로 재구성**한 교육용 콘텐츠이며, 원문을 복제하지 않습니다.

- KISA, 「소프트웨어 보안약점 진단가이드」(2021) — 시큐어 코딩 49개 보안약점
- KISA, 「주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드」 — UNIX/DBMS/웹 등 기술적 점검
- 금융보안원, 「전자금융기반시설 보안 취약점 평가기준(제2026-1호)」 — 전자금융 보안 특화 항목

각 자료의 저작권은 해당 기관에 있으며, 평가기준 문서의 무단 배포는 금지됩니다.


