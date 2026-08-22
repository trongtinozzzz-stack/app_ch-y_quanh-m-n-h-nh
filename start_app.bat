@echo off
chcp 65001 >nul
title Desktop Pet Mascot

cd /d "%~dp0"

echo ========================================================
echo         DESKTOP PET MASCOT - ELECTRON EDITION
echo ========================================================
echo.

where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Khong tim thay Node.js tren he thong!
    echo [*] Vui long cai dat Node.js tu: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [*] Phat hien lan dau khoi chay, dang cai dat dependencies...
    cmd /c "npm install"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Co loi khi cai dat dependencies!
        pause
        exit /b 1
    )
)

echo [*] Dang khoi dong Desktop Pet...
echo [*] Cua so nay se tu dong dong lai sau khi khoi dong.
echo.

start "" cmd /c "npx electron ."

timeout /t 2 /nobreak >nul
exit
