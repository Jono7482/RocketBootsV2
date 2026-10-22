@echo off
title Rocket Boots
echo Launching Rocket Boots v0.5.0...
py -3.9 main.py
if errorlevel 1 (
    echo.
    echo Trying with default python...
    python main.py
)
pause
