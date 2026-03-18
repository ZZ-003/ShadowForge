import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.task import Task
from models.user import User
from config.settings import settings

logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器，负责处理生成的文件"""

    def __init__(self, db: Session):
        self.db = db
        self.base_output_dir = Path(settings.output_dir)

    def get_user_output_dir(self, user_id: int) -> Path:
        """获取用户输出目录"""
        user_dir = self.base_output_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_task_files(self, task_id: int, user_id: int) -> List[str]:
        """获取任务文件列表"""
        task = self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if not task.output_files:
            return []

        # 验证文件是否存在
        valid_files = []
        for file_path in task.output_files:
            if os.path.exists(file_path):
                valid_files.append(file_path)

        return valid_files

    def get_file_info(self, file_path: str, user_id: int) -> dict:
        """获取文件信息"""
        # 验证文件路径是否在用户目录下
        if not self._is_file_in_user_dir(file_path, user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        file_stat = os.stat(file_path)
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": file_stat.st_size,
            "created": file_stat.st_ctime,
            "modified": file_stat.st_mtime,
            "type": self._get_file_type(file_path)
        }

    def delete_file(self, file_path: str, user_id: int) -> bool:
        """删除文件"""
        # 验证文件路径是否在用户目录下
        if not self._is_file_in_user_dir(file_path, user_id):
            raise HTTPException(status_code=403, detail="Access denied")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        try:
            os.remove(file_path)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

    def delete_task_files(self, task_id: int, user_id: int, commit: bool = True) -> tuple[bool, Optional[str]]:
        """删除任务所有文件
        
        Args:
            task_id: 任务 ID
            user_id: 用户 ID
            commit: 是否立即提交数据库变更（批量操作时设为 False）
            
        Returns:
            (success, error_message) - success 表示是否成功，error_message 是错误信息（如果失败）
        """
        task = self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

        if not task:
            return False, f"Task {task_id} not found"

        if not task.output_files:
            return True, None

        success = True
        for file_path in task.output_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"删除文件 {file_path} 失败：{str(e)}")
                success = False

        # 清空任务的文件列表
        task.output_files = []
        
        if commit:
            self.db.commit()

        return success, None

    def get_user_files(self, user_id: int, file_type: Optional[str] = None) -> List[dict]:
        """获取用户所有文件（去重）"""
        user_tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.output_files.isnot(None)
        ).all()

        # 使用字典去重，key 为 file_path
        files_dict = {}
        for task in user_tasks:
            for file_path in task.output_files:
                if os.path.exists(file_path):
                    file_info = self.get_file_info(file_path, user_id)
                    if file_type and file_info["type"] != file_type:
                        continue
                    
                    # 如果文件已存在，更新 task_name 为最新任务的名称
                    if file_path in files_dict:
                        files_dict[file_path]["task_name"] = task.name
                        files_dict[file_path]["task_id"] = task.id
                    else:
                        file_info["task_id"] = task.id
                        file_info["task_name"] = task.name
                        files_dict[file_path] = file_info

        return list(files_dict.values())

    def create_download_archive(self, user_id: int, file_paths: List[str]) -> str:
        """创建下载压缩包"""
        import zipfile
        import tempfile

        # 验证所有文件都在用户目录下
        for file_path in file_paths:
            if not self._is_file_in_user_dir(file_path, user_id):
                raise HTTPException(status_code=403, detail="Access denied")

        # 创建临时zip文件
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, f"download_{user_id}.zip")

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)

            return zip_path
        except Exception as e:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(status_code=500, detail=f"Failed to create archive: {str(e)}")

    def _is_file_in_user_dir(self, file_path: str, user_id: int) -> bool:
        """检查文件是否在用户目录下"""
        try:
            file_path = Path(file_path).resolve()
            user_dir = self.get_user_output_dir(user_id).resolve()
            return str(file_path).startswith(str(user_dir))
        except:
            return False

    def _get_file_type(self, file_path: str) -> str:
        """获取文件类型"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return 'image'
        elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
            return 'audio'
        elif ext == '.pdf':
            return 'pdf'
        elif ext in ['.doc', '.docx']:
            return 'word'
        elif ext in ['.ppt', '.pptx']:
            return 'ppt'
        else:
            return 'other'