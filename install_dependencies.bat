@echo off
title David AI - Dependency Installer

echo ===================================================
echo  Installing/Updating Python Packages for David AI
echo ===================================================
echo.

echo Activating Python virtual environment...
call .venv\Scripts\activate

echo.
echo Installing packages from requirements.txt...
pip install -r requirements.txt

echo.
echo ===================================================
echo  Installation complete!
echo ===================================================
echo.
pause
