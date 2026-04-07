@echo off
chcp 65001 >nul
title Sims 4 Mod Detector v6.2 - GUI
set "SCRIPT_DIR=%~dp0"

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 ( echo [ERROR] Python not found! Install Python 3.10+ from python.org & pause & exit /b 1 )
if not exist "%SCRIPT_DIR%mod_detector_v6.py" ( echo [ERROR] mod_detector_v6.py not found! & pause & exit /b 1 )

cd /d "%SCRIPT_DIR%"
python mod_detector_v6.py --gui
