@echo off
chcp 65001 > nul
echo ========================================================
echo   Dang day source code len GitHub...
echo ========================================================

cd /d "%~dp0"

REM Kiem tra git repository
if not exist ".git" (
    echo [*] Khoi tao Git repository...
    git init
    git branch -M main
    git remote add origin https://github.com/trongtinozzzz-stack/app_ch-y_quanh-m-n-h-nh.git
) else (
    git remote set-url origin https://github.com/trongtinozzzz-stack/app_ch-y_quanh-m-n-h-nh.git
)

echo [*] Them tat ca cac file vao git...
git add .

echo [*] Tao commit...
git commit -m "feat: cap nhat Desktop Pet Mascot Anya va he thong animation"

echo [*] Day len GitHub (main branch)...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   THANH CONG! Source code da duoc day len GitHub.
    echo ========================================================
) else (
    echo.
    echo [!] Co the can force push hoac dang nhap Git neu repo tren GitHub da co san file README/commit.
    echo [*] Thu lai voi force push neu ban muon ghi de...
    git push -u origin main --force
)

pause
