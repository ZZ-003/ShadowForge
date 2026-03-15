#!/bin/bash

# ShadowForge Development Environment Startup Script

set -e

echo "========================================"
echo "ShadowForge Development Environment"
echo "========================================"

# Check required commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "[ERROR] $1 not found, please install $1 first"
        exit 1
    fi
}

echo ""
echo "Checking dependencies..."

check_command python
check_command pip
check_command node
check_command npm

echo "[OK] All dependencies found"

# Check backend environment
echo ""
echo "Checking backend environment..."
cd backend
if [ ! -f ".env" ]; then
    echo "[WARN] Backend environment file not found"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "[INFO] Please edit backend/.env and add your LLM API key"
    echo "Press Enter to continue..."
    read
fi

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Initialize database
echo ""
echo "Initializing database..."
python -c "from database.session import init_db; init_db()" || {
    echo "[WARN] Database initialization failed, trying to recreate..."
    rm -f shadowforge.db
    python -c "from database.session import init_db; init_db()"
}

# Run seed data
echo ""
echo "Running seed data..."
python seed_data.py

cd ..

# Install frontend dependencies
echo ""
echo "Installing frontend dependencies..."
cd frontend
npm install

cd ..

echo ""
echo "========================================"
echo "Starting ShadowForge Services..."
echo "========================================"
echo ""
echo "Two services will start:"
echo "1. Backend service (http://localhost:8000)"
echo "2. Frontend service (http://localhost:3000)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Start services using tmux if available
if command -v tmux &> /dev/null; then
    echo ""
    echo "Starting services with tmux..."
    tmux new-session -d -s shadowforge "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    tmux split-window -h "cd frontend && npm run dev"
    tmux attach-session -t shadowforge
else
    echo ""
    echo "[INFO] tmux not found, starting backend in current terminal"
    echo "Please open a new terminal and run:"
    echo "cd frontend && npm run dev"
    echo ""
    echo "Starting backend service..."
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi