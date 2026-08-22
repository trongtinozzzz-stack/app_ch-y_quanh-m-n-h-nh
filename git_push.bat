@echo off
chcp 65001 >nul
title Git Push - Desktop Pet Mascot

cd /d "%~dp0"

echo ========================================================
echo         GIT PUSH - DONG BO CODE LEN GITHUB
echo ========================================================
echo.

if not exist ".git" (
    echo [*] Khoi tao Git repository...
    git init
    git branch -M main
    git remote add origin https://github.com/trongtinozzzz-stack/app_ch-y_quanh-m-n-h-nh.git
)

echo [*] Cac file da thay doi:
git status --short
echo.

set "COMMIT_MSG="
set /p "COMMIT_MSG=Nhap thong diep commit (Hoac an Enter de dung mac dinh): "

if "%COMMIT_MSG%"=="" (
    set "COMMIT_MSG=feat: update Electron Desktop Pet mascot with renderer UI and batch scripts"
)

echo.
echo [*] Dang them file: git add .
git add .

echo [*] Dang tao commit: "%COMMIT_MSG%"
git commit -m "%COMMIT_MSG%"

echo [*] Dang day len GitHub (origin main)...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   [OK] THANH CONG! Code da duoc day len GitHub.
    echo ========================================================
) else (
    echo.
    echo [!] Push bi tu choi hoac xung dot. Dang thu push voi force-with-lease...
    git push -u origin main --force-with-lease
    if %ERRORLEVEL% equ 0 (
        echo [OK] Da force push thanh cong!
    ) else (
        echo [ERROR] Khong the day code len GitHub.
    )
)

echo.
pause
