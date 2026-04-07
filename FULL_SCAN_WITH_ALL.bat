@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v8.0 - Full Scan + Log + Mod Checker
color 0E

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v8.0 - FULL SCAN + LOG + MOD CHECKER
echo   The complete scan: exception log + Scarlet Mod Checker + everything
echo ====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"

if not exist "%MODS_PATH%" (
    set "MODS_PATH=%USERPROFILE%\OneDrive\Documents\Electronic Arts\The Sims 4\Mods"
)
if not exist "%MODS_PATH%" (
    echo [!] Could not auto-detect Mods folder!
    echo.
    set /p "MODS_PATH=Drag and drop your Mods folder here: "
)

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%mod_detector_v6.py" (
    echo [ERROR] Script not found!
    pause
    exit /b 1
)

echo Mods folder: %MODS_PATH%
echo.

echo ====================================================================
echo  STEP 1: Drag and drop your Better Exceptions log file here,
echo          then press Enter.
echo          (e.g. better_exceptions_log.txt or mc_lastexception.html)
echo.
echo          Press Enter without a file to skip log analysis.
echo ====================================================================
echo.
set /p "LOG_FILE=Log file: "

echo.
echo ====================================================================
echo  STEP 2: Drag and drop your Scarlet Mod Checker CSV here,
echo          then press Enter.
echo          (e.g. Mod_List_Checker_v4_04_-_All_Mods.csv)
echo          Download latest from: https://scarletsrealm.com
echo.
echo          Press Enter without a file to skip mod checker.
echo ====================================================================
echo.
set /p "MODLIST_FILE=Mod Checker CSV: "

echo.
echo ====================================================================
echo  Press any key to start full scan...
echo ====================================================================
pause >nul
echo.
echo ====================================================================
echo  SCANNING...
echo ====================================================================
echo.

cd /d "%SCRIPT_DIR%"

REM Strip quotes from dragged paths
if defined LOG_FILE set "LOG_FILE=%LOG_FILE:"=%"
if defined MODLIST_FILE set "MODLIST_FILE=%MODLIST_FILE:"=%"

REM Run with both log and modlist
if defined LOG_FILE if defined MODLIST_FILE if not "%LOG_FILE%"=="" if not "%MODLIST_FILE%"=="" (
    python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --log "%LOG_FILE%" --modlist "%MODLIST_FILE%" --export "full_complete_report.csv"
    goto :done
)

REM Run with log only
if defined LOG_FILE if not "%LOG_FILE%"=="" (
    python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --log "%LOG_FILE%" --export "full_complete_report.csv"
    goto :done
)

REM Run with modlist only
if defined MODLIST_FILE if not "%MODLIST_FILE%"=="" (
    python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --modlist "%MODLIST_FILE%" --export "full_complete_report.csv"
    goto :done
)

REM Run with neither
python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --export "full_complete_report.csv"

:done
echo.
echo ====================================================================
echo  DONE!
echo  CSV Report:       %SCRIPT_DIR%full_complete_report.csv
echo  Excel Checklist:  %SCRIPT_DIR%full_complete_report_cleanup_checklist.xlsx
echo ====================================================================
echo.
pause
