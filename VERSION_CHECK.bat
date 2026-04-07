@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - VERSION CHECK
color 0E

echo ====================================================================
echo   SIMS 4 MOD DETECTOR v6.2 - SCRIPT MOD VERSION CHECK
echo   Reads actual version strings from .ts4script and .package files
echo ====================================================================
echo.
echo Checks MCCC, UI Cheats Extension, Better BuildBuy, TOOL, 
echo WickedWhims, Basemental, Lot51 Core, and more against
echo minimum safe versions for the current game patch.
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
echo Press any key to start version check...
pause >nul
echo.

cd /d "%SCRIPT_DIR%"

REM Run with --fast but version detection still runs on its own
REM We use a small Python wrapper to run just the version check
python -c "import sys; sys.argv = ['mod_detector_v6.py']; from mod_detector_v6 import ModAnalyzer; a = ModAnalyzer(r'%MODS_PATH%'); a.scan_mods(); a.detect_broken_mods(); a.detect_mod_versions(); a.export_to_csv('version_check_report.csv')"

echo.
echo ====================================================================
echo  DONE! Report: %SCRIPT_DIR%version_check_report.csv
echo ====================================================================
echo.
pause
