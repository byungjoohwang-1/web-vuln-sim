# 🛡️ Web Vulnerability Simulator

Website: https://vuln-sim-test.web.app/

## 📖 Introduction
This project is a **Web Vulnerability Simulation Platform** designed for educational purposes. It utilizes **Google Firebase** as a serverless backend to demonstrate common web vulnerabilities (such as XSS, Injection, and Insecure Direct Object References) and their mitigation strategies. This tool is intended for students and professionals preparing for certifications like CISA, ISRM, and penetration testing practice.

## 📂 Project Structure
The current file structure of the project is organized as follows:

```text
web-vuln-sim/
├── index.html            # Main entry point (Login & Dashboard)
├── styles.css            # Global stylesheets and layout
├── firebase-config.js    # Firebase SDK initialization and configuration logic
├── README.md             # Project documentation
└── .gitignore            # Git ignore rules

🚀 Features
User Authentication: Secure sign-up and login using Firebase Authentication.

Real-time Database: CRUD operations (Create, Read, Update, Delete) using Cloud Firestore.

Vulnerability Labs:

Simulation of web vulnerabilities (e.g., XSS, Broken Access Control).

Secure coding practice environment.

Responsive Design: Simple and accessible UI for testing.

🛠️ Prerequisites
Before you begin, ensure you have the following:

A modern web browser (Chrome, Edge, etc.)

A Google Account (to access Firebase Console)

Git or GitHub Desktop installed

⚙️ Installation & Setup Guide
Step 1: Clone the Repository
Clone this repository to your local machine using Git or GitHub Desktop.

git clone [https://github.com/byungjoohwang-1/web-vuln-sim.git](https://github.com/byungjoohwang-1/web-vuln-sim.git)

Step 2: Set up Firebase Project
Since this project relies on Firebase, you must create your own Firebase project.

Go to the Firebase Console.

Click "Add project" and follow the instructions to create a new project (e.g., my-security-lab).

Once the project is ready, click the Web icon (</>) to register an app.

Enter an app nickname (e.g., WebSimulator) and click Register app.

You will see a code snippet containing firebaseConfig. Copy this code block.

Step 3: Enable Firebase Services
You need to enable Authentication and Firestore in the console for the code to work.

Authentication:

Go to Build > Authentication in the sidebar.

Click Get Started.

Select Email/Password as the Sign-in provider and Enable it.

Firestore Database:

Go to Build > Firestore Database.

Click Create Database.

Start in Test mode (for development) or Production mode (requires setting security rules).

Step 4: Configure the Code
Open the firebase-config.js file in your code editor (VS Code, Notepad, etc.).

Paste the firebaseConfig object you copied in Step 2. It should look like this:

// firebase-config.js

// Import the functions you need from the SDKs you need
import { initializeApp } from "[https://www.gstatic.com/firebasejs/9.x.x/firebase-app.js](https://www.gstatic.com/firebasejs/9.x.x/firebase-app.js)";
// TODO: Add SDKs for Firebase products that you want to use
// [https://firebase.google.com/docs/web/setup#available-libraries](https://firebase.google.com/docs/web/setup#available-libraries)

const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.firebasestorage.app",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

Step 5: Run the Simulator
Simply open index.html in your web browser. You can now test the signup and login features connected to your own Firebase backend.

⚠️ Disclaimer
This tool is created strictly for educational and authorized testing purposes only. Any misuse of the techniques demonstrated in this project on unauthorized systems is illegal and punishable by law. The author assumes no responsibility for any misuse or damage caused by this program.

Contact: Copyright 2025 jackhwang0210@gmail.com
