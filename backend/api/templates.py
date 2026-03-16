from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.session import get_db
from models.template import Template, TemplateType
from models.user import User
from core.auth import get_current_active_user

router = APIRouter(prefix="/templates", tags=["templates"])


# 请求/响应模型
class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: TemplateType
    is_public: bool = False
    config: dict


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    config: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    template_type: TemplateType
    is_public: bool
    config: dict
    usage_count: int
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TemplateResponse])
async def get_templates(
    template_type: Optional[TemplateType] = None,
    is_public: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取模板列表"""
    query = db.query(Template).filter(
        (Template.user_id == current_user.id) | (Template.is_public == True)
    )

    if template_type:
        query = query.filter(Template.template_type == template_type)

    if is_public is not None:
        query = query.filter(Template.is_public == is_public)

    templates = query.order_by(Template.usage_count.desc(), Template.created_at.desc()).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取模板详情"""
    template = db.query(Template).filter(
        Template.id == template_id,
        (Template.user_id == current_user.id) | (Template.is_public == True)
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 增加使用计数
    template.usage_count += 1
    db.commit()

    return template


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新模板"""
    # 检查模板名称是否已存在
    existing_template = db.query(Template).filter(
        Template.name == template_data.name,
        Template.user_id == current_user.id
    ).first()

    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template name already exists"
        )

    # 创建模板
    db_template = Template(
        user_id=current_user.id,
        name=template_data.name,
        description=template_data.description,
        template_type=template_data.template_type,
        is_public=template_data.is_public,
        config=template_data.config
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新模板"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 更新字段
    if template_data.name is not None:
        # 检查新名称是否已存在
        if template_data.name != template.name:
            existing_template = db.query(Template).filter(
                Template.name == template_data.name,
                Template.user_id == current_user.id
            ).first()
            if existing_template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Template name already exists"
                )
        template.name = template_data.name

    if template_data.description is not None:
        template.description = template_data.description

    if template_data.is_public is not None:
        template.is_public = template_data.is_public

    if template_data.config is not None:
        template.config = template_data.config

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除模板"""
    template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()


@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
async def duplicate_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """复制模板"""
    source_template = db.query(Template).filter(
        Template.id == template_id,
        (Template.user_id == current_user.id) | (Template.is_public == True)
    ).first()

    if not source_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # 创建新模板名称
    new_name = f"{source_template.name} (Copy)"

    # 检查名称是否已存在
    counter = 1
    while True:
        existing_template = db.query(Template).filter(
            Template.name == new_name,
            Template.user_id == current_user.id
        ).first()
        if not existing_template:
            break
        counter += 1
        new_name = f"{source_template.name} (Copy {counter})"

    # 创建复制模板
    new_template = Template(
        user_id=current_user.id,
        name=new_name,
        description=source_template.description,
        template_type=source_template.template_type,
        is_public=False,  # 复制模板默认为私有
        config=source_template.config.copy()  # 深拷贝配置
    )

    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    return new_template