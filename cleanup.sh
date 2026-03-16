#!/bin/bash
echo "Cleaning up ShadowForge processes..."

# 终止Python进程
pkill -f "python.*uvicorn" 2>/dev/null
pkill -f "python.*celery" 2>/dev/null
pkill -f "python.*main:app" 2>/dev/null

# 停止Docker容器
docker-compose -f docker-compose.dev.yml down 2>/dev/null

# 清理数据库文件
rm -f backend/shadowforge.db 2>/dev/null
rm -f shadowforge.db 2>/dev/null

# 清理缓存文件
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "Cleanup completed!"