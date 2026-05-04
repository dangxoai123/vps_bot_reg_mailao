@echo off
echo ==================================================
echo   DANG CAI DAT MOI TRUONG CHO BOT REG CLONE
echo ==================================================
echo.
echo 1. Dang cai dat thu vien Python (playwright, requests)...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [!] Loi khi cai dat thu vien. Vui long kiem tra ket noi mang hoac Python.
    pause
    exit /b
)

echo.
echo 2. Dang cai dat trinh duyet Chromium...
python -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [!] Loi khi cai dat Chromium.
    pause
    exit /b
)

echo.
echo ==================================================
echo   CAI DAT HOAN TAT! BAY GIO BAN CO THE CHAY:
echo   python vps_mailao.py
echo ==================================================
pause
