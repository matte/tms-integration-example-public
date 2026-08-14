@echo off
rem Windows launcher for the TMS Gateway console (double-click, or run with arguments).
setlocal
set ROOT=%~dp0
set PY=%ROOT%.venv\Scripts\python.exe

if not exist "%PY%" (
    echo Creating the virtual environment in .venv ...
    py -3 -m venv "%ROOT%.venv" || python -m venv "%ROOT%.venv"
)

echo Installing dependencies ...
"%PY%" -m pip install --quiet --upgrade pip
"%PY%" -m pip install --quiet -r "%ROOT%requirements.txt"

"%PY%" -m tms_cli %*
endlocal
