@echo off
REM 피드 수집 — Windows 작업 스케줄러가 20분마다 호출한다.
set PYTHONIOENCODING=utf-8
cd /d C:\firebaseprojects\web-vuln-sim
python ops\fetch_feeds.py >> ops\fetch.log 2>&1
