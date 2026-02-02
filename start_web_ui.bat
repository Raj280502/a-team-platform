@echo off
echo ========================================
echo AI Code Factory - Web IDE Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install --quiet flask flask-cors flask-socketio python-socketio

echo.
echo ========================================
echo Starting Web UI Server...
echo ========================================
echo.
echo Open your browser at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.

python web_ui.py
