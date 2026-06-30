@echo off
title JARVIS Launcher
echo.
echo  =============================================
echo   JARVIS -- Starting local server...
echo  =============================================
echo.
python start_jarvis.py
if errorlevel 1 (
    echo.
    echo  Python not found. Trying py launcher...
    py start_jarvis.py
)
pause
