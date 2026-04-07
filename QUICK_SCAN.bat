@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - QUICK SCAN
color 0B

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - QUICK SCAN
echo   Duplicates ^| Outdated ^| Broken Mods ^| Integrity ^| Performance
echo ====================================================================
echo.

set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"
set "SCRIPT_DIR=%~dp0"
REM  set "MODS_PATH=D:\Games\The Sims 4\Mods"

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo [ERROR] Python not found! & pause & exit /b 1 )
if not exist "%MODS_PATH%" ( echo [ERROR] Mods folder not found: %MODS_PATH% & pause & exit /b 1 )
if not exist "%SCRIPT_DIR%mod_detector_v6.py" ( echo [ERROR] mod_detector_v6.py not found! & pause & exit /b 1 )

echo Mods folder: %MODS_PATH%
echo Mode:        QUICK (skips DBPF parsing, TGI, LOD, versions, merged)
echo.
echo Press any key to start...
pause >nul
echo.

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --mods "%MODS_PATH%" --fast --parallel --export "quick_scan_report.csv"

echo.
echo DONE! Report: %SCRIPT_DIR%quick_scan_report.csv
echo.
pause
