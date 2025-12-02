🛡️ Web Vulnerability Simulation (Vuln-Sim) : Made by Jack Hwang(jackhwang0210@gmail.com)
WebSite: https://vuln-sim-test.web.app/

This project is an educational simulator designed to demonstrate the mechanisms of major web security vulnerabilities and practice Secure Coding techniques to defend against them. It is built on the Firebase (Cloud Functions & Hosting) platform.

🚀 Project Overview

Objective: To allow developers and security beginners to directly attack vulnerabilities in a realistic environment and visually experience the difference when defense code is applied.

Tech Stack:

Frontend: HTML, CSS, JavaScript (Firebase Hosting)

Backend: Node.js (Firebase Cloud Functions)

Platform: Firebase (Serverless Architecture)

🎯 Implemented Vulnerability Scenarios (7 Types)

This simulator covers 7 major vulnerabilities selected based on KISA's (Korea Internet & Security Agency) Software Development Security Guide and OWASP Top 10.

HTTP Response Splitting

Scenario: Practice header splitting and cookie manipulation that occur when user input is included in response headers (e.g., Cookie) without validation.

Cross-Site Scripting (Reflected XSS)

Scenario: Practice DOM-based XSS attacks where scripts are executed in bulletin boards or search bars, and defense using textContent.

Path Traversal

Scenario: Practice attacks accessing sensitive system files (e.g., /etc/passwd) using ../ characters in file download/view functions.

SQL Injection

Scenario: Practice authentication bypass by hijacking an administrator account using the ' OR '1'='1 pattern in a login window.

Code Injection

Scenario: Practice attacks where system commands or arbitrary code are executed due to the misuse of the eval() function in a calculator feature.

Insecure Direct Object References (IDOR)

Scenario: Practice unauthorized viewing of others' order history or personal information simply by manipulating URL parameters due to insufficient authorization checks.

OS Command Injection

Scenario: Practice attacks executing system commands like ls using ; characters in a Ping test tool.

🛠️ Installation & Execution Guide

Follow these steps to run this project locally or deploy it directly.

1. Prerequisites

Node.js installed (LTS version recommended)

Firebase CLI installed: npm install -g firebase-tools

Firebase Account and a Blaze Plan (Pay-as-you-go) project (Required for Cloud Functions)

2. Project Setup

Clone the repository.

git clone [https://github.com/YOUR_USERNAME/web-vuln-sim.git](https://github.com/YOUR_USERNAME/web-vuln-sim.git)
cd web-vuln-sim


Initialize and connect the Firebase project.

firebase login
firebase init
# Select Functions, Hosting -> Select Existing Project


Modify the configuration file (public/config.js).

// Change to your Firebase Project ID
const PROJECT_ID = "YOUR_PROJECT_ID"; 
const REGION = "us-central1"; 
const BASE_URL = `https://${REGION}-${PROJECT_ID}.cloudfunctions.net`;


3. Deploy

Deploy the code to the Firebase server.

firebase deploy


Once deployment is complete, access the Hosting URL displayed in the terminal to start the simulation.

📂 File Structure

/
├── functions/          # Backend (Cloud Functions)
│   └── index.js        # Implementation of vulnerability and defense logic (Core)
└── public/             # Frontend (Hosting)
    ├── config.js       # Project configuration file
    ├── index.html      # Main Menu
    ├── sim-split.html  # 1. HTTP Response Splitting
    ├── sim-xss.html    # 2. XSS
    ├── sim-path.html   # 3. Path Traversal
    ├── sim-sql.html    # 4. SQL Injection
    ├── sim-code.html   # 5. Code Injection
    ├── sim-idor.html   # 6. IDOR
    └── sim-cmd.html    # 7. OS Command Injection
