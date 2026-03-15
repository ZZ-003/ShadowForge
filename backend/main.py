import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from config.settings import settings
from database.session import init_db
from api import auth, tasks, templates, files, config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：确保目录存在并初始化数据库
    try:
        print("Creating directories...")
        os.makedirs(settings.output_dir, exist_ok=True)
        os.makedirs(settings.upload_dir, exist_ok=True)
        print("Directories created/verified.")
        
        print("Initializing database...")
        init_db()
        print("Database initialized.")
    except Exception as e:
        print(f"Error during startup: {e}")
        # 即使出错也要继续，避免app无法启动

    yield

    # 关闭时：清理资源
    print("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ShadowForge - 多模态敏感数据深度仿真引擎 API",
    lifespan=lifespan
)

# 配置CORS
# 解析逗号分隔的origins字符串为列表
cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保输出目录和上传目录存在
os.makedirs(settings.output_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)

# 挂载静态文件（用于文件访问）
app.mount("/static", StaticFiles(directory=settings.output_dir), name="static")

# 注册API路由
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(config.router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to ShadowForge API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "shadowforge-api"}


if __name__ == "__main__":
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )