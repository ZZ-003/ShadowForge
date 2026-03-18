import os
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.session import get_db
from models.user import User
from core.auth import get_current_active_user
from core.file_manager import FileManager

router = APIRouter(prefix="/files", tags=["files"])


# 请求/响应模型
class FileInfo(BaseModel):
    path: str
    name: str
    size: int
    created: float
    modified: float
    type: str
    task_id: Optional[int] = None
    task_name: Optional[str] = None


class DownloadRequest(BaseModel):
    file_paths: List[str]


@router.get("/", response_model=List[FileInfo])
async def get_files(
    file_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户文件列表"""
    file_manager = FileManager(db)
    files = file_manager.get_user_files(current_user.id, file_type)
    return files


@router.get("/task/{task_id}", response_model=List[FileInfo])
async def get_task_files(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取任务文件列表"""
    file_manager = FileManager(db)
    file_paths = file_manager.get_task_files(task_id, current_user.id)

    files = []
    for file_path in file_paths:
        file_info = file_manager.get_file_info(file_path, current_user.id)
        files.append(file_info)

    return files


from typing import Optional
from fastapi import Query

@router.get("/preview")
async def preview_file(
    path: str = Query(..., description="File path to preview"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """预览文件"""
    file_manager = FileManager(db)

    # 验证文件访问权限 - 使用 int() 转换 user_id
    file_info = file_manager.get_file_info(path, int(current_user.id))

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    # 根据文件类型返回不同的响应
    file_type = file_info["type"]

    if file_type == "image":
        return FileResponse(
            path,
            media_type=f"image/{os.path.splitext(path)[1][1:]}",
            filename=os.path.basename(path)
        )
    elif file_type == "video":
        return FileResponse(
            path,
            media_type=f"video/{os.path.splitext(path)[1][1:]}",
            filename=os.path.basename(path),
            headers={"Accept-Ranges": "bytes"}
        )
    elif file_type == "audio":
        return FileResponse(
            path,
            media_type=f"audio/{os.path.splitext(path)[1][1:]}",
            filename=os.path.basename(path)
        )
    elif file_type == "pdf":
        return FileResponse(
            path,
            media_type="application/pdf",
            filename=os.path.basename(path)
        )
    else:
        # 对于其他文件类型，返回下载
        return FileResponse(
            path,
            media_type="application/octet-stream",
            filename=os.path.basename(path)
        )


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """下载单个文件"""
    file_manager = FileManager(db)

    # 验证文件访问权限
    file_manager.get_file_info(file_path, current_user.id)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(file_path)
    )


@router.post("/download/batch")
async def download_files_batch(
    download_request: DownloadRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量下载文件（打包为zip）"""
    file_manager = FileManager(db)

    # 创建下载压缩包
    zip_path = file_manager.create_download_archive(current_user.id, download_request.file_paths)

    try:
        # 返回文件流
        def iterfile():
            with open(zip_path, "rb") as f:
                yield from f

            # 清理临时文件
            temp_dir = os.path.dirname(zip_path)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        return StreamingResponse(
            iterfile(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=download_{current_user.id}.zip"
            }
        )
    except Exception as e:
        # 清理临时文件
        temp_dir = os.path.dirname(zip_path)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to download files: {str(e)}")


@router.delete("/{file_path:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除文件"""
    file_manager = FileManager(db)
    file_manager.delete_file(file_path, current_user.id)


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_files(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除任务所有文件"""
    file_manager = FileManager(db)
    file_manager.delete_task_files(task_id, current_user.id)