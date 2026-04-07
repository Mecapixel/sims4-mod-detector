@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - FULL SCAN
color 0A

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - FULL COMPREHENSIVE SCAN
echo   DBPF Parsing ^| TGI Conflicts ^| LOD Analysis ^| Version Check
echo   Merged Package Breakdown ^| Broken Mod DB
echo ====================================================================
echo.

REM =====================================================================
REM  CONFIGURATION - Edit this path if yours is different
REM =====================================================================
set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"
set "SCRIPT_DIR=%~dp0"

REM  Uncomment and edit if your Mods folder is somewhere else:
REM  set "MODS_PATH=D:\Games\The Sims 4\Mods"

echo Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Install Python 3.10+ from python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

if not exist "%MODS_PATH%" (
    echo [ERROR] Mods folder not found at: %MODS_PATH%
    echo Edit this .bat file and set MODS_PATH to your actual Mods folder.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%mod_detector_v6.py" (
    echo [ERROR] mod_detector_v6.py not found! Place this .bat in the same folder.
    pause
    exit /b 1
)

echo.
echo Mods folder: %MODS_PATH%
echo Mode:        FULL SCAN (everything including merged analysis)
echo.
echo Press any key to start...
pause >nul
echo.

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --export "full_scan_report.csv"

echo.
echo ====================================================================
echo  DONE! Report: %SCRIPT_DIR%full_scan_report.csv
echo ====================================================================
echo.
pause
