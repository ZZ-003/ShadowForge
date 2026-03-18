import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.task import Task, TaskStatus
from config.settings import settings

# 导入 ShadowForge 适配器
from shadowforge_adapter import generate_from_config_safe, get_generate_from_config

# 延迟导入标志
HAS_SHADOWFORGE = False

# 初始化时检查是否可用
try:
    if get_generate_from_config() is not None:
        HAS_SHADOWFORGE = True
    else:
        print("Warning: ShadowForge modules not available")
except Exception as e:
    print(f"Warning: Error checking ShadowForge availability: {e}")
    HAS_SHADOWFORGE = False


class TaskRunner:
    """任务运行器，负责执行 ShadowForge 生成任务"""

    def __init__(self, db: Session, task_id: int):
        self.db = db
        self.task_id = task_id
        self.task = None
        self.output_dir = None

    async def run(self):
        """运行任务"""
        # 获取任务
        self.task = self.db.query(Task).filter(Task.id == self.task_id).first()
        if not self.task:
            raise ValueError(f"Task {self.task_id} not found")

        # 更新任务状态为运行中
        self.task.status = TaskStatus.RUNNING
        self.db.commit()

        try:
            # 创建用户输出目录
            user_output_dir = Path(settings.output_dir) / str(self.task.user_id)
            user_output_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir = str(user_output_dir)

            # 运行生成任务
            await self._run_generation()

            # 更新任务状态为完成
            self.task.status = TaskStatus.COMPLETED
            self.task.progress = 100
            self.task.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            # 更新任务状态为失败
            self.task.status = TaskStatus.FAILED
            self.task.error_message = str(e)
            print(f"Task {self.task_id} failed: {e}")

        finally:
            self.db.commit()

    async def _run_generation(self):
        """执行生成逻辑"""
        if not HAS_SHADOWFORGE:
            raise RuntimeError("ShadowForge modules not available")

        # 为每个任务创建独立的子目录，避免文件名冲突
        task_output_dir = os.path.join(self.output_dir, f"task_{self.task_id}")
        os.makedirs(task_output_dir, exist_ok=True)
        
        # 创建配置字典
        config = self._create_config_dict(task_output_dir)

        # 定义进度回调函数
        def progress_callback(progress: int, message: str):
            self.task.progress = progress
            self.db.commit()

        try:
            # 调用安全的 generate_from_config 函数
            result = generate_from_config_safe(
                config,
                progress_callback=progress_callback,
                output_dir=task_output_dir
            )

            # 更新任务结果
            if result["success"]:
                # 转换为绝对路径
                absolute_output_files = []
                for file_path in result["output_files"]:
                    if os.path.isabs(file_path):
                        absolute_output_files.append(file_path)
                    else:
                        absolute_output_files.append(os.path.join(task_output_dir, file_path))
                self.task.output_files = absolute_output_files
                self.task.task_metadata = result["metadata"]
            else:
                self.task.error_message = "; ".join(result["errors"])

        except Exception as e:
            # 更新任务状态为失败
            self.task.status = TaskStatus.FAILED
            self.task.error_message = str(e)
            raise

    def _create_config_dict(self, output_dir: str) -> Dict[str, Any]:
        """创建配置字典"""
        return {
            "api_key": settings.llm_api_key or "",
            "base_url": settings.llm_base_url or "",
            "output_dir": output_dir,
            "add_noise": False,
            "items": [
                {
                    "task_id": self.task_id,
                    "secret": self.task.secret,
                    "secret_type": self.task.secret_type,
                    "modality": self.task.modality.value,
                    "scene": self.task.scene.value if self.task.scene else None
                }
            ]
        }


async def run_task_async(db: Session, task_id: int):
    """异步运行任务"""
    runner = TaskRunner(db, task_id)
    await runner.run()


def run_task_sync(db: Session, task_id: int):
    """同步运行任务（用于测试）"""
    import asyncio
    asyncio.run(run_task_async(db, task_id))
