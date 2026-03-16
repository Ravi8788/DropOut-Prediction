@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment Python not found at .venv\Scripts\python.exe
    pause
    exit /b 1
)

echo Starting Dropout Prediction and Counseling Dashboard...
echo Open http://localhost:8501 in your browser.
".venv\Scripts\python.exe" -m streamlit run professional_demo.py --server.port 8501

if errorlevel 1 (
    echo.
    echo The app stopped with an error.
    pause
)