@echo off
chcp 65001 >nul
title Dong Goi Chrome Extension - Desktop Pet Mascot

cd /d "%~dp0"

echo ========================================================
echo     DONG GOI CHROME EXTENSION THANH 1 FILE ZIP
echo ========================================================
echo.

set "SOURCE_DIR=%~dp0extension"
set "ZIP_OUT=%~dp0desktop-pet-extension.zip"

if not exist "%SOURCE_DIR%" (
    echo [ERROR] Khong tim thay thu muc extension!
    pause
    exit /b 1
)

if exist "%ZIP_OUT%" (
    echo [*] Xoa file zip cu...
    del /f /q "%ZIP_OUT%"
)

echo [*] Dang nen thu muc extension thanh desktop-pet-extension.zip...

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%SOURCE_DIR%\*' -DestinationPath '%ZIP_OUT%' -Force"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   [OK] THANH CONG! Da tao 1 file ZIP duy nhat:
    echo   %ZIP_OUT%
    echo ========================================================
    echo.
    echo [*] Ban co the dung file ZIP nay de:
    echo     1. Gui cho ban be giai nen su dung.
    echo     2. Tai truc tiep len Google Chrome Web Store Developer Console.
    echo.
) else (
    echo [ERROR] Co loi khi dong goi file ZIP!
)

pause
