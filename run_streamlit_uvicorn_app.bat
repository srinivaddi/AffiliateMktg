@echo off
setlocal

REM Activate the virtual environment and run the Streamlit app
REM Change directory to the script location
cd /d %~dp0

REM Check if Ollama is running
tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul
IF %ERRORLEVEL% EQU 0 (
    echo Ollama is already running.
) ELSE (
    echo Ollama is not running. Starting Ollama...
    REM Replace with actual path to ollama.exe
    start /B "" "C:\Users\srvad\AppData\Local\Programs\Ollama\ollama app.exe"
    REM Wait for Ollama to initialize
    timeout /t 5 >nul

    REM Check again if Ollama started
    tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul
    IF %ERRORLEVEL% NEQ 0 (
        echo ❌ Ollama failed to start. Exiting script.
        REM Wait a 2 seconds after health check is checked
        timeout /t 4 >nul
        exit /b 1
    )
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Configuration
@REM set "UVICORN_CMD=uvicorn app_links:app --host 0.0.0.0 --port 8000 --reload --log-level info --access-log"
set "UVICORN_CMD=uvicorn affiliate_mktg.src.api.app_links:app --host 0.0.0.0 --port 8000 --reload --log-level info --access-log"
set "STREAMLIT_CMD=python -m streamlit run app.py"
set "API_URL=http://localhost:8000/health"

REM Check and stop existing Uvicorn process
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Uvicorn is already running with PID %%a
    echo Stopping Uvicorn...
    taskkill /PID %%a /F
    timeout /t 2 >nul
)

REM Start Uvicorn in a new terminal window
echo Starting Uvicorn server...
start "" cmd /k %UVICORN_CMD%

REM Wait a few seconds for Uvicorn to start
timeout /t 5 >nul

REM Check if API is reachable
echo Checking if API is reachable...
@REM powershell -NoExit -Command ^
@REM     "$response = Invoke-WebRequest -Uri '%API_URL%' -UseBasicParsing -TimeoutSec 15; ^
@REM     if ($response.StatusCode -eq 200) { ^
@REM         Write-Host '✅ Uvicorn API is running.' ^
@REM     } else { ^
@REM         Write-Host '❌ API responded with status code: ' $response.StatusCode ^
@REM     }" || echo ❌ Failed to reach API.

@REM start powershell -NoExit -File health_check.ps1
@REM for /f "delims=" %%i in ('powershell -ExecutionPolicy Bypass -File health_check.ps1') do echo %%i
@REM for /f "usebackq tokens=* delims=" %%a in (`powershell -ExecutionPolicy Bypass -File health_check.ps1`) do (
@REM     set "ps_output=%%a"
@REM     echo PowerShell Output: %%a
@REM )
for /f "usebackq tokens=* delims=" %%a in (`powershell -ExecutionPolicy Bypass -File "%~dp0healthcheck.ps1"`) do (
    set "ps_output=%%a"
    echo PowerShell Output: %%a
)

REM Wait a 2 seconds after health check is checked
timeout /t 2 >nul

REM Start Streamlit in a new terminal window
echo Starting Streamlit app...
start "" cmd /k %STREAMLIT_CMD%

REM Keep the command prompt open
echo All services started. Press any key to exit this window.

endlocal
exit
