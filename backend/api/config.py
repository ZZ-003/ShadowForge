from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.session import get_db
from models.user import User
from core.auth import get_current_active_user
from config.settings import settings

router = APIRouter(prefix="/config", tags=["configuration"])


# 请求/响应模型
class ConfigUpdate(BaseModel):
    llm_api_key: str
    llm_base_url: str
    llm_model: str = "qwen3.5-plus"


class ConfigResponse(BaseModel):
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    output_dir: str
    upload_dir: str


class LLMTestRequest(BaseModel):
    api_key: str
    base_url: str
    model: str = "qwen3.5-plus"


class LLMTestResponse(BaseModel):
    success: bool
    message: str
    response_time: float


@router.get("/", response_model=ConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_active_user)
):
    """获取系统配置"""
    return ConfigResponse(
        llm_api_key=settings.llm_api_key or "",
        llm_base_url=settings.llm_base_url or "",
        llm_model=settings.llm_model,
        output_dir=settings.output_dir,
        upload_dir=settings.upload_dir
    )


@router.put("/", response_model=ConfigResponse)
async def update_config(
    config_data: ConfigUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新系统配置"""
    # 检查用户权限（只有管理员可以更新全局配置）
    # 这里暂时允许所有用户更新，实际应用中应该检查权限

    # 更新配置
    settings.llm_api_key = config_data.llm_api_key
    settings.llm_base_url = config_data.llm_base_url
    settings.llm_model = config_data.llm_model

    # 注意：在实际应用中，应该将配置保存到数据库或配置文件
    # 这里只是更新内存中的设置

    return ConfigResponse(
        llm_api_key=settings.llm_api_key or "",
        llm_base_url=settings.llm_base_url or "",
        llm_model=settings.llm_model,
        output_dir=settings.output_dir,
        upload_dir=settings.upload_dir
    )


@router.post("/test-llm", response_model=LLMTestResponse)
async def test_llm_connection(
    test_data: LLMTestRequest,
    current_user: User = Depends(get_current_active_user)
):
    """测试LLM连接"""
    import time
    import httpx

    start_time = time.time()

    try:
        # 测试API连接
        headers = {
            "Authorization": f"Bearer {test_data.api_key}",
            "Content-Type": "application/json"
        }

        # 简单的ping请求
        payload = {
            "model": test_data.model,
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 10
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{test_data.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10.0
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                return LLMTestResponse(
                    success=True,
                    message="LLM connection successful",
                    response_time=response_time
                )
            else:
                return LLMTestResponse(
                    success=False,
                    message=f"LLM API returned status code: {response.status_code}",
                    response_time=response_time
                )

    except httpx.ConnectError:
        response_time = time.time() - start_time
        return LLMTestResponse(
            success=False,
            message="Connection failed. Please check the base URL.",
            response_time=response_time
        )
    except httpx.TimeoutException:
        response_time = time.time() - start_time
        return LLMTestResponse(
            success=False,
            message="Connection timeout. Please check your network.",
            response_time=response_time
        )
    except Exception as e:
        response_time = time.time() - start_time
        return LLMTestResponse(
            success=False,
            message=f"Error: {str(e)}",
            response_time=response_time
        )


@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取系统信息"""
    import platform
    import psutil
    import os

    # 获取系统信息
    system_info = {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

    # 获取内存信息
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total,
        "available": memory.available,
        "percent": memory.percent,
        "used": memory.used,
        "free": memory.free,
    }

    # 获取磁盘信息
    disk = psutil.disk_usage('/')
    disk_info = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }

    # 获取CPU信息
    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "cpu_percent": psutil.cpu_percent(interval=1),
    }

    return {
        "system": system_info,
        "memory": memory_info,
        "disk": disk_info,
        "cpu": cpu_info,
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
        }
    }