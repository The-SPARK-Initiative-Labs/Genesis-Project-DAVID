@echo off
setlocal

:: ============================================================================
:: David AI - Unified Launcher & Stopper (v4 - Diagnostic)
:: This version will keep the window open after a crash to display errors.
:: ============================================================================

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

echo Starting Ollama service in the background...
start "Ollama Server" /B ollama serve

echo Waiting 5 seconds for Ollama to initialize...
timeout /t 5 /nobreak >nul

echo Starting Chainlit UI on port 8002...
:: CRITICAL FIX: We run the command directly in this window and add a pause.
:: This will keep the window open if the python script crashes.
chainlit run app.py -w --port 8002

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
