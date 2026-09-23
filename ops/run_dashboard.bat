@echo off
REM 파이프라인 라이브 대시보드 — 폰에서 볼 수 있게 LAN(0.0.0.0)으로 서빙한다.
REM 더블클릭하면 창이 뜨고, 같은 와이파이의 폰에서 http://<이-PC-IP>:8787 로 접속한다.
REM 창을 닫으면 서버도 멈춘다(관측 전용이라 계속 켜 둘 필요는 없다).
set PYTHONIOENCODING=utf-8
cd /d C:\firebaseprojects\web-vuln-sim
echo.
echo  파이프라인 대시보드를 시작합니다. 이 창을 닫으면 종료됩니다.
echo  폰에서 같은 와이파이로 접속하세요 (아래 phone 주소).
echo.
python ops\dashboard.py --port 8787
pause
