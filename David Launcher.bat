@echo off
setlocal

:: ============================================================================
:: David AI - Unified Launcher & Stopper (v7 - Corrected Working Directory)
:: This version forces the script to run from its own directory, which is
:: the definitive fix for all ".env file not found" errors.
:: ============================================================================

:: THE FIX: This command changes the current directory to the directory
:: where this batch file is located. This is the most important line.
cd /d %~dp0

:menu
cls
echo =========================================
echo  David AI - Control Panel
echo =========================================
echo.
echo  [1] Start David (Ollama + Chainlit UI)
echo  [2] Stop All Services
echo  [3] Exit
echo.
set /p choice="Enter your choice: "

if /i "%choice%"=="1" goto start_servers
if /i "%choice%"=="2" goto stop_servers
if /i "%choice%"=="3" goto :eof

echo Invalid choice.
pause
goto menu

:start_servers
echo.
echo Activating Python virtual environment...
call .venv\Scripts\activate

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt

echo Loading environment variables from .env file...
for /f "usebackq delims=" %%a in ("C:\David\.env") do (
    set "%%a"
)

if defined OLLAMA_MODEL (
    echo OLLAMA_MODEL is set to: %OLLAMA_MODEL%
) else (
    echo ERROR: OLLAMA_MODEL not found in .env file!
    pause
    goto :eof
)
echo.

echo Starting Ollama service in the background...
start "Ollama Server" /B ollama serve

echo Waiting 5 seconds for Ollama to initialize...
timeout /t 5 /nobreak >nul

echo Starting Chainlit UI on port 8002...
python -m chainlit run app.py -w --port 8002

echo.
echo Chainlit process has ended.
pause
goto :eof

:stop_servers
echo.
echo Stopping Chainlit UI (Port 8002)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002"') do (
    taskkill /PID %%a /F >nul
)

echo Stopping Ollama service...
taskkill /F /IM ollama.exe /T >nul

echo.
echo All services stopped.
pause
goto :eof
