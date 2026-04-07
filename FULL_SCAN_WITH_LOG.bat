@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - FULL SCAN + LOG
color 0E

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - FULL SCAN + EXCEPTION LOG
echo   Everything from FULL_SCAN plus exception log analysis
echo ====================================================================
echo.

set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"
set "SCRIPT_DIR=%~dp0"
REM  set "MODS_PATH=D:\Games\The Sims 4\Mods"

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo [ERROR] Python not found! & pause & exit /b 1 )
if not exist "%MODS_PATH%" ( echo [ERROR] Mods folder not found: %MODS_PATH% & pause & exit /b 1 )
if not exist "%SCRIPT_DIR%mod_detector_v6.py" ( echo [ERROR] Script not found! & pause & exit /b 1 )

echo Mods folder: %MODS_PATH%
echo.
echo Drag and drop your exception log file here, then press Enter:
echo (e.g. better_exceptions_log.txt or mc_lastexception.html)
echo.
set /p LOG_PATH="Log file: "
set "LOG_PATH=%LOG_PATH:"=%"

if "%LOG_PATH%"=="" (
    echo No log file provided. Running full scan without log analysis.
    set "LOG_ARG="
) else (
    if not exist "%LOG_PATH%" (
        echo [WARNING] Log file not found: %LOG_PATH%
        echo Running without log analysis.
        set "LOG_ARG="
    ) else (
        echo Log file: %LOG_PATH%
        set "LOG_ARG=--log "%LOG_PATH%""
    )
)

echo.
echo Press any key to start...
pause >nul
echo.

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --mods "%MODS_PATH%" --full --parallel --analyze-merged %LOG_ARG% --export "full_log_report.csv"

echo.
echo ====================================================================
echo  DONE! Report: %SCRIPT_DIR%full_log_report.csv
echo ====================================================================
pause
