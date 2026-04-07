@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - MERGED PACKAGE ANALYSIS
color 0D

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - MERGED PACKAGE ANALYSIS
echo   Deep resource breakdown of large/merged .package files
echo ====================================================================
echo.
echo Analyzes every package over 100 MB: CAS parts, meshes, textures,
echo thumbnail bloat, and optimization suggestions.
echo.

set "MODS_PATH=%USERPROFILE%\Documents\Electronic Arts\The Sims 4\Mods"
set "SCRIPT_DIR=%~dp0"
REM  set "MODS_PATH=D:\Games\The Sims 4\Mods"

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo [ERROR] Python not found! & pause & exit /b 1 )
if not exist "%MODS_PATH%" ( echo [ERROR] Mods folder not found: %MODS_PATH% & pause & exit /b 1 )
if not exist "%SCRIPT_DIR%mod_detector_v6.py" ( echo [ERROR] mod_detector_v6.py not found! & pause & exit /b 1 )

echo Mods folder: %MODS_PATH%
echo.
echo Change the size threshold? (default 100 MB)
echo Press Enter for default, or type a number:
echo.
set /p "THRESHOLD=Threshold in MB [100]: "
if "%THRESHOLD%"=="" set "THRESHOLD=100"

echo.
echo Analyzing packages over %THRESHOLD% MB...
pause >nul
echo.

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --mods "%MODS_PATH%" --fast --parallel --analyze-merged --merged-threshold %THRESHOLD% --export "merged_analysis_report.csv"

echo.
echo DONE! Report: %SCRIPT_DIR%merged_analysis_report.csv
echo.
pause
