@echo off
chcp 65001 >nul
title Tao Shortcut Desktop Pet

cd /d "%~dp0"

echo ========================================================
echo        TAO SHORTCUT NGOAI MAN HINH DESKTOP
echo ========================================================
echo.

set "TARGET_BAT=%~dp0start_app.bat"
set "ICON_FILE=%~dp0assets\icon.ico"
set "WORK_DIR=%~dp0"
set "VBS_FILE=%temp%\create_pet_shortcut.vbs"

(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\Desktop Pet Mascot.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "%TARGET_BAT%"
echo oLink.WorkingDirectory = "%WORK_DIR%"
echo oLink.IconLocation = "%ICON_FILE%,0"
echo oLink.Description = "Desktop Pet Mascot - Anya Forger"
echo oLink.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%"
if exist "%VBS_FILE%" del "%VBS_FILE%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [OK] Da tao thanh cong Shortcut 'Desktop Pet Mascot' ngoai Desktop!
    echo [*] Ban co the ra man hinh Desktop va click dup vao icon de khoi dong.
) else (
    echo.
    echo [ERROR] Co loi khi tao shortcut!
)

echo.
echo ========================================================
pause
