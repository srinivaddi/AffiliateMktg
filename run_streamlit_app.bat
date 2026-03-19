@echo off
REM Activate the virtual environment and run the Streamlit app

REM Change directory to the script location
cd /d %~dp0

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Run the Streamlit app
python -m streamlit run app.py

REM Pause to keep the command window open after execution
pause
