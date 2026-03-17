from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import logging

from database.session import get_db
from models.task import (
    Task, TaskStatus, TaskModality, TaskScene,
    BatchTaskCreate, BatchTaskResponse, BatchTaskResult,
    BatchDeleteRequest, BatchDeleteResponse
)
from models.user import User
from core.auth import get_current_active_user
from core.task_runner import run_task_async
from core.file_manager import FileManager
import asyncio

# 添加日志记录器
logger = logging.getLogger(__name__)

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


# ============================================================================
# 批量操作 API 端点
# ============================================================================

@router.post("/batch", response_model=BatchTaskResponse)
async def create_tasks_batch(
    batch_data: BatchTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量创建任务"""
    logger.info(f"=== 批量创建任务开始 ===")
    logger.info(f"用户 ID: {current_user.id}")
    logger.info(f"秘密数量：{len(batch_data.secrets)}")
    logger.info(f"公共配置：{batch_data.common_config.dict()}")
    
    results = []
    success_count = 0
    failed_count = 0
    created_tasks = []
    
    # 第一阶段：创建所有任务记录（不提交）
    for i, secret in enumerate(batch_data.secrets):
        logger.debug(f"处理第 {i+1} 个秘密")
        # 跳过空秘密
        if not secret or not secret.strip():
            logger.warning(f"第 {i+1} 个秘密为空，跳过")
            results.append({
                "success": False,
                "task": None,
                "error": "Secret cannot be empty"
            })
            failed_count += 1
            continue
        
        # 生成任务名称
        name = f"{batch_data.common_config.name_prefix}{i + 1}"
        
        try:
            # 创建任务记录
            db_task = Task(
                user_id=current_user.id,
                name=name,
                description=batch_data.common_config.description,
                secret=secret.strip(),
                secret_type=batch_data.common_config.secret_type,
                modality=batch_data.common_config.modality,
                scene=batch_data.common_config.scene if batch_data.common_config.scene else None,
                status=TaskStatus.PENDING
            )
            
            db.add(db_task)
            created_tasks.append((db_task, i))
            logger.debug(f"成功创建任务记录：{name}")
            
        except Exception as e:
            logger.error(f"创建任务记录失败 (索引 {i}): {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            results.append({
                "success": False,
                "task": None,
                "error": str(e)
            })
            failed_count += 1
    
    # 提交所有任务到数据库
    if created_tasks:
        try:
            db.commit()
            logger.info(f"数据库提交成功，创建了 {len(created_tasks)} 个任务")
        except Exception as e:
            logger.error(f"数据库提交失败：{str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            raise
    
    # 第二阶段：为每个成功创建的任务添加后台任务
    # 注意：这里使用 task_id 而不是 db 会话，因为 background_tasks 会在当前请求结束后执行
    logger.info(f"开始处理 {len(created_tasks)} 个已创建的任务")
    for db_task, original_index in created_tasks:
        try:
            logger.debug(f"处理任务索引 {original_index}, 任务 ID: {db_task.id}")
            # 获取任务信息用于响应
            created_at_str = db_task.created_at.isoformat() if db_task.created_at else None
            
            results.insert(original_index, {
                "success": True,
                "task": {
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
                    "started_at": None,
                    "completed_at": None
                },
                "error": None
            })
            success_count += 1
            
            # 添加到后台任务队列 - 使用新的数据库会话
            logger.debug(f"添加后台任务：{db_task.id}")
            background_tasks.add_task(run_task_with_new_session, db_task.id)
            
        except Exception as e:
            logger.error(f"处理任务失败 (索引 {original_index}): {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            db.rollback()
            results.insert(original_index, {
                "success": False,
                "task": None,
                "error": str(e)
            })
            failed_count += 1
    
    logger.info(f"批量创建完成 - 成功：{success_count}, 失败：{failed_count}")
    
    return BatchTaskResponse(
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )


async def run_task_with_new_session(task_id: int):
    """使用新会话运行任务"""
    from database.session import SessionLocal
    from core.task_runner import run_task_async
    
    local_db = SessionLocal()
    try:
        await run_task_async(local_db, task_id)
    finally:
        local_db.close()


@router.post("/batch/delete", response_model=BatchDeleteResponse)
async def delete_tasks_batch(
    delete_request: BatchDeleteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量删除任务及其文件"""
    logger.info(f"=== 批量删除任务开始 ===")
    logger.info(f"用户 ID: {current_user.id}")
    logger.info(f"要删除的任务 ID: {delete_request.task_ids}")
    
    task_ids = delete_request.task_ids
    deleted_tasks = []
    errors = []
    
    try:
        for task_id in task_ids:
            try:
                logger.debug(f"处理任务 {task_id}")
                # 获取任务
                task = db.query(Task).filter(
                    Task.id == task_id,
                    Task.user_id == current_user.id
                ).first()
                
                if not task:
                    logger.warning(f"任务 {task_id} 不存在")
                    errors.append(f"Task {task_id} not found")
                    continue
                
                logger.debug(f"删除任务 {task_id} 的文件")
                # 删除任务文件（不立即提交，由外层统一提交）
                file_manager = FileManager(db)
                success, error_msg = file_manager.delete_task_files(task_id, int(current_user.id), commit=False)
                if not success:
                    logger.warning(f"删除任务 {task_id} 文件失败：{error_msg}")
                    errors.append(error_msg)
                    continue
                
                # 删除数据库记录
                logger.debug(f"删除任务 {task_id} 的数据库记录")
                db.delete(task)
                deleted_tasks.append(task_id)
                
            except Exception as e:
                logger.error(f"处理任务 {task_id} 时出错：{str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                errors.append(f"Task {task_id}: {str(e)}")
        
        # 提交所有变更
        logger.info(f"提交删除结果 - 成功：{len(deleted_tasks)}, 失败：{len(errors)}")
        db.commit()
        
        return BatchDeleteResponse(
            success_count=len(deleted_tasks),
            failed_count=len(errors),
            deleted_tasks=deleted_tasks,
            errors=errors
        )
    except Exception as e:
        logger.error(f"批量删除过程中发生未捕获的错误：{str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除失败：{str(e)}")