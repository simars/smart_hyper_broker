#!/bin/bash
set -e

echo "Starting Backend and Frontend locally..."

# Start backend in background
cd backend
make dev &
BACKEND_PID=$!
cd ..

# Start frontend in background
cd frontend
make dev &
FRONTEND_PID=$!
cd ..

function cleanup() {
    echo "Stopping local services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "Cleaned up."
}

trap cleanup EXIT INT TERM

echo "Services running. Press Ctrl+C to stop."
wait $BACKEND_PID
wait $FRONTEND_PID
