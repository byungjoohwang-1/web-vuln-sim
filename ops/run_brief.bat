@echo off
REM 숫자 브리프 — Windows 작업 스케줄러가 매일 아침 호출한다.
set PYTHONIOENCODING=utf-8
cd /d C:\firebaseprojects\web-vuln-sim
python ops\brief.py >> ops\brief.log 2>&1
