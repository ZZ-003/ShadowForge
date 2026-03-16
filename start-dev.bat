@echo off
chcp 65001 >nul
REM ShadowForge Development Environment Startup Script (Windows)

echo ========================================
echo ShadowForge Development Environment
echo ========================================

echo.
echo Checking dependencies...

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python first
    pause
    exit /b 1
)

REM Check Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found, please install Node.js first
    pause
    exit /b 1
)

REM Check npm
where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm not found, please install npm first
    pause
    exit /b 1
)

echo [OK] All dependencies found

echo.
echo Checking backend environment...
if not exist "backend\.env" (
    echo [WARN] Backend environment file not found
    echo Creating backend\.env from template...
    copy "backend\.env.example" "backend\.env"
    echo [INFO] Please edit backend\.env and add your LLM API key
    echo Press any key to continue...
    pause >nul
)

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Initializing database...
python -c "from database.session import init_db; init_db()"
if errorlevel 1 (
    echo [WARN] Database initialization failed, trying to recreate...
    del shadowforge.db 2>nul
    python -c "from database.session import init_db; init_db()"
    if errorlevel 1 (
        echo [ERROR] Database initialization failed
        pause
        exit /b 1
    )
)

echo.
echo Running seed data...
python seed_data.py
if errorlevel 1 (
    echo [WARN] Seed data failed, continuing...
)

cd ..

echo.
echo Installing frontend dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo Starting ShadowForge Services...
echo ========================================
echo.
echo Two windows will open:
echo 1. Backend service (http://localhost:8000)
echo 2. Frontend service (http://localhost:3000)
echo.
echo Keep both windows running
echo ========================================

REM Start backend service
start cmd /k "cd /d %cd%\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload && echo Backend service stopped && pause"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend service
start cmd /k "cd /d %cd%\frontend && npm run dev && echo Frontend service stopped && pause"

echo.
echo [SUCCESS] Services started!
echo.
echo Access the application at:
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this script...
pause >nul