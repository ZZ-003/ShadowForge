@echo off
echo Cleaning up ShadowForge processes...

:: 终止Python进程
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM uvicorn.exe /T 2>nul
taskkill /F /IM celery.exe /T 2>nul

:: 停止Docker容器
docker-compose -f docker-compose.dev.yml down 2>nul

:: 清理数据库文件
del /Q backend\shadowforge.db 2>nul
del /Q shadowforge.db 2>nul

:: 清理缓存文件
rmdir /S /Q __pycache__ 2>nul
rmdir /S /Q backend\__pycache__ 2>nul
rmdir /S /Q generators\__pycache__ 2>nul

echo Cleanup completed!