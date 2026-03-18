from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database.session import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskModality(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"


class TaskScene(str, enum.Enum):
    IDE = "ide"
    CLI = "cli"
    CHAT = "chat"
    CONFIG = "config"
    UI = "ui"
    AUDIO = "audio"
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 任务配置
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    secret = Column(Text, nullable=False)
    secret_type = Column(String(50), nullable=False)
    modality = Column(Enum(TaskModality), nullable=False)
    scene = Column(Enum(TaskScene), nullable=True)

    # 任务状态
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)

    # 输出文件信息
    output_files = Column(JSON, nullable=True)  # 存储文件路径列表
    task_metadata = Column(JSON, nullable=True)  # 存储生成元数据

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status})>"


# 注意：需要在应用启动后设置关系
# from models.user import User
# User.tasks = relationship("Task", order_by=Task.id, back_populates="user")


# ============================================================================
# Pydantic 模型 - 用于批量操作的请求/响应
# ============================================================================

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class CommonTaskConfig(BaseModel):
    """公共任务配置"""
    name_prefix: str = ""
    secret_type: str
    modality: str
    scene: Optional[str] = None
    description: Optional[str] = None
    
    model_config = {
        "populate_by_name": True,  # 支持别名和原始字段名
        "arbitrary_types_allowed": True,
    }


class BatchTaskCreate(BaseModel):
    """批量创建任务请求"""
    secrets: List[str]
    common_config: CommonTaskConfig
    
    model_config = {
        "populate_by_name": True,  # 支持别名和原始字段名
        "arbitrary_types_allowed": True,
    }


class BatchTaskResult(BaseModel):
    """批量创建结果项"""
    success: bool
    task: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class BatchTaskResponse(BaseModel):
    """批量创建任务响应"""
    success_count: int
    failed_count: int
    results: List[BatchTaskResult]
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    task_ids: List[int]
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class BatchDeleteResponse(BaseModel):
    """批量删除响应"""
    success_count: int
    failed_count: int
    deleted_tasks: List[int]
    errors: List[str]
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }