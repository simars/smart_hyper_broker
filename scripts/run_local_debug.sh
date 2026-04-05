#!/bin/bash
set -e

echo "Starting Backend and Frontend locally in DEBUG mode..."

# Start backend in background
cd backend
make dev-debug &
BACKEND_PID=$!
cd ..

# Start frontend in background
cd frontend
make dev-debug &
FRONTEND_PID=$!
cd ..

function cleanup() {
    echo "Stopping local debug services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "Cleaned up."
}

trap cleanup EXIT INT TERM

echo "Debug Services running (Backend: 5678, Frontend: inspector). Press Ctrl+C to stop."
wait $BACKEND_PID
wait $FRONTEND_PID
