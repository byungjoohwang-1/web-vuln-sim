@echo off
REM 오케스트레이터 — Windows 작업 스케줄러가 15분마다 호출한다.
REM 실 LLM 검증(python ops\triage_run.py 독립 실행)이 끝난 뒤 등록할 것.
set PYTHONIOENCODING=utf-8
cd /d C:\firebaseprojects\web-vuln-sim
python ops\tick.py >> ops\tick.log 2>&1
