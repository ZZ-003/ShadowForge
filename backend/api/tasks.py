from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database.session import get_db
from models.task import Task, TaskStatus, TaskModality, TaskScene
from models.user import User
from core.auth import get_current_active_user
from core.task_runner import run_task_async
from core.file_manager import FileManager
import asyncio

router = APIRouter(prefix="/tasks", tags=["tasks"])


# 请求/响应模型
class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None
    secret: str
    secret_type: str
    modality: TaskModality
    scene: Optional[TaskScene] = None


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    secret: str
    secret_type: str
    modality: TaskModality
    scene: Optional[TaskScene]
    status: TaskStatus
    progress: int
    error_message: Optional[str]
    output_files: Optional[List[str]]
    task_metadata: Optional[Dict[str, Any]]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    # 手动创建响应字典列表以避免Pydantic验证问题
    task_responses = []
    for task in tasks:
        created_at_str = None
        started_at_str = None
        completed_at_str = None
        
        if task.created_at is not None:
            created_at_str = task.created_at.isoformat()
        if task.started_at is not None:
            started_at_str = task.started_at.isoformat()
        if task.completed_at is not None:
            completed_at_str = task.completed_at.isoformat()
        
        task_responses.append({
            "id": task.id,
            "user_id": task.user_id,
            "name": task.name,
            "description": task.description,
            "secret": task.secret,
            "secret_type": task.secret_type,
            "modality": task.modality,
            "scene": task.scene,
            "status": task.status,
            "progress": task.progress,
            "error_message": task.error_message,
            "output_files": task.output_files,
            "task_metadata": task.task_metadata,
            "created_at": created_at_str,
            "started_at": started_at_str,
            "completed_at": completed_at_str
        })
    
    return task_responses


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 手动创建响应字典以避免Pydantic验证问题
    created_at_str = None
    started_at_str = None
    completed_at_str = None
    
    if task.created_at is not None:
        created_at_str = task.created_at.isoformat()
    if task.started_at is not None:
        started_at_str = task.started_at.isoformat()
    if task.completed_at is not None:
        completed_at_str = task.completed_at.isoformat()
    
    return {
        "id": task.id,
        "user_id": task.user_id,
        "name": task.name,
        "description": task.description,
        "secret": task.secret,
        "secret_type": task.secret_type,
        "modality": task.modality,
        "scene": task.scene,
        "status": task.status,
        "progress": task.progress,
        "error_message": task.error_message,
        "output_files": task.output_files,
        "task_metadata": task.task_metadata,
        "created_at": created_at_str,
        "started_at": started_at_str,
        "completed_at": completed_at_str
    }


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新任务"""
    # 创建任务记录
    db_task = Task(
        user_id=current_user.id,
        name=task_data.name,
        description=task_data.description,
        secret=task_data.secret,
        secret_type=task_data.secret_type,
        modality=task_data.modality,
        scene=task_data.scene,
        status=TaskStatus.PENDING
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 在后台运行任务
    background_tasks.add_task(run_task_in_background, db, db_task.id)

    # 手动创建响应字典以避免Pydantic验证问题
    created_at_str = None
    started_at_str = None
    completed_at_str = None
    
    if db_task.created_at is not None:
        created_at_str = db_task.created_at.isoformat()
    if db_task.started_at is not None:
        started_at_str = db_task.started_at.isoformat()
    if db_task.completed_at is not None:
        completed_at_str = db_task.completed_at.isoformat()
    
    return {
        "id": db_task.id,
        "user_id": db_task.user_id,
        "name": db_task.name,
        "description": db_task.description,
        "secret": db_task.secret,
        "secret_type": db_task.secret_type,
        "modality": db_task.modality,
        "scene": db_task.scene,
        "status": db_task.status,
        "progress": db_task.progress,
        "error_message": db_task.error_message,
        "output_files": db_task.output_files,
        "task_metadata": db_task.task_metadata,
        "created_at": created_at_str,
        "started_at": started_at_str,
        "completed_at": completed_at_str
    }


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新任务"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 更新字段
    if task_data.name is not None:
        task.name = task_data.name
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status

    db.commit()
    db.refresh(task)

    # 手动创建响应字典以避免Pydantic验证问题
    created_at_str = None
    started_at_str = None
    completed_at_str = None
    
    if task.created_at is not None:
        created_at_str = task.created_at.isoformat()
    if task.started_at is not None:
        started_at_str = task.started_at.isoformat()
    if task.completed_at is not None:
        completed_at_str = task.completed_at.isoformat()
    
    return {
        "id": task.id,
        "user_id": task.user_id,
        "name": task.name,
        "description": task.description,
        "secret": task.secret,
        "secret_type": task.secret_type,
        "modality": task.modality,
        "scene": task.scene,
        "status": task.status,
        "progress": task.progress,
        "error_message": task.error_message,
        "output_files": task.output_files,
        "task_metadata": task.task_metadata,
        "created_at": created_at_str,
        "started_at": started_at_str,
        "completed_at": completed_at_str
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除任务及其所有文件"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 删除任务关联的所有文件
    file_manager = FileManager(db)
    file_manager.delete_task_files(task_id, current_user.id)

    # 删除数据库中的任务记录
    db.delete(task)
    db.commit()


@router.post("/{task_id}/run")
async def run_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """手动运行任务"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.PENDING, TaskStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot run task with status: {task.status}"
        )

    # 重置任务状态
    task.status = TaskStatus.PENDING
    task.progress = 0
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    db.commit()

    # 在后台运行任务
    asyncio.create_task(run_task_async(db, task_id))

    return {"message": "Task started"}


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消任务"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task with status: {task.status}"
        )

    task.status = TaskStatus.CANCELLED
    db.commit()

    return {"message": "Task cancelled"}


async def run_task_in_background(db: Session, task_id: int):
    """在后台运行任务"""
    # 创建新的数据库会话
    from database.session import SessionLocal
    local_db = SessionLocal()

    try:
        await run_task_async(local_db, task_id)
    finally:
        local_db.close()