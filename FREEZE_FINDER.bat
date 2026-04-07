@echo off
chcp 65001 >nul
title Sims 4 Freeze Finder
echo ====================================================================
echo   SIMS 4 FREEZE FINDER - Binary Search Mod Isolator
echo   No more manual 50/50!
echo ====================================================================
echo.
echo Launching GUI...
python "%~dp0sims4_freeze_finder.py"
if errorlevel 1 (
    echo.
    echo ERROR: Make sure Python is installed and in your PATH.
    echo Download Python from: https://www.python.org/downloads/
    pause
)
