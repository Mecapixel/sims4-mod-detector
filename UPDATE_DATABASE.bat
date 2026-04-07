@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - Update Database
color 0D

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - UPDATE BROKEN MOD DATABASE
echo ====================================================================
echo.
echo Saves/updates broken_cc_hashes.json in your Mods folder.
echo You can add your own entries and they will be preserved.
echo.

set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"
set "SCRIPT_DIR=%~dp0"
REM  set "MODS_PATH=D:\Games\The Sims 4\Mods"

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo [ERROR] Python not found! & pause & exit /b 1 )
if not exist "%MODS_PATH%" ( echo [ERROR] Mods folder not found: %MODS_PATH% & pause & exit /b 1 )
if not exist "%SCRIPT_DIR%mod_detector_v6.py" ( echo [ERROR] mod_detector_v6.py not found! & pause & exit /b 1 )

echo Press any key to update...
pause >nul

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --mods "%MODS_PATH%" --update-db

echo.
echo Done!
pause
