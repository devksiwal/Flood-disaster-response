#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "[NDMA] Launching Agentic AI Autonomous Flood Disaster Response System"
echo "=============================================================================="

# Backend setup
if [ ! -d "backend/.venv" ]; then
    echo "[1/3] Setting up Python virtual environment..."
    python3 -m venv backend/.venv
    source backend/.venv/bin/activate
    pip install -r backend/requirements.txt
else
    source backend/.venv/bin/activate
fi

# Frontend setup
if [ ! -d "frontend/node_modules" ]; then
    echo "[2/3] Installing Frontend Node dependencies..."
    cd frontend && npm install && cd ..
fi

echo "[3/3] Launching Backend and Frontend concurrently..."
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173"

(cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
