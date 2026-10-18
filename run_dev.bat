@echo off
TITLE NDMA Flood Disaster Response System - Development Launcher
echo ==============================================================================
echo [NDMA] Launching Agentic AI Autonomous Flood Disaster Response System
echo ==============================================================================

:: Check if virtualenv exists
if not exist "backend\.venv\Scripts\python.exe" (
    echo [1/3] Creating Python virtual environment...
    python -m venv backend\.venv
    call backend\.venv\Scripts\activate.bat
    echo [2/3] Installing Python backend dependencies...
    pip install -r backend\requirements.txt
) else (
    echo [1/3] Python virtual environment detected.
)

:: Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo [2/3] Installing Frontend Node dependencies...
    cd frontend
    call npm install
    cd ..
) else (
    echo [2/3] Frontend node modules detected.
)

echo [3/3] Launching Backend and Frontend servers concurrently...
echo ------------------------------------------------------------------------------
echo - FastAPI Backend: http://127.0.0.1:8000
echo - Swagger Docs:    http://127.0.0.1:8000/docs
echo - React Dashboard: http://localhost:5173
echo ------------------------------------------------------------------------------

start "NDMA-Backend" cmd /k "cd backend && .venv\Scripts\activate.bat && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
start "NDMA-Frontend" cmd /k "cd frontend && npm run dev"

echo System services launched in separate terminal windows.
pause
