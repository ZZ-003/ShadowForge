@echo off
chcp 65001 >nul
echo ========================================
echo ShadowForge 简化启动脚本
echo ========================================

echo.
echo 步骤1: 检查Python环境
python --version
if errorlevel 1 (
    echo [ERROR] Python未找到或无法运行
    pause
    exit /b 1
)

echo.
echo 步骤2: 检查后端依赖
cd backend
echo 正在检查Python包...
python -c "import fastapi; print('✓ fastapi:', fastapi.__version__)"
python -c "import pydantic; print('✓ pydantic:', pydantic.__version__)"
python -c "import sqlalchemy; print('✓ sqlalchemy:', sqlalchemy.__version__)"
python -c "import uvicorn; print('✓ uvicorn:', uvicorn.__version__)"

echo.
echo 步骤3: 测试后端启动
echo 正在启动后端服务...
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 如果看到以上错误信息，请检查：
echo 1. Python环境是否正确
echo 2. 依赖是否安装完整
echo 3. 配置文件是否正确
echo.
pause