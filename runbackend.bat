@echo off
title MISSION MIRROR - Junior Astronaut Mission Trainer
cd /d "%~dp0"
echo ========================================================
echo   Launching MISSION MIRROR Server...
echo ========================================================
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server stopped with error code %ERRORLEVEL%.
    pause
)

