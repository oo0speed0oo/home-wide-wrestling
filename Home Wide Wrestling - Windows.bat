@echo off
rem Home Wide Wrestling (Windows, with Python)
rem Double-click this file to play.
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 is not installed. Get it from https://www.python.org/downloads/
    echo During the install, tick "Add python.exe to PATH". Then double-click this file again.
    pause
    exit /b
)

python -c "import pygame" >nul 2>nul
if errorlevel 1 (
    echo Installing pygame, one moment...
    python -m pip install pygame-ce
)

start "" pythonw game\main.py
