from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database.session import Base


class TemplateType(str, enum.Enum):
    SECRET_TYPE = "secret_type"
    SCENE = "scene"
    MODALITY = "modality"
    COMPLETE = "complete"


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 模板基本信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(Enum(TemplateType), nullable=False)
    is_public = Column(Boolean, default=False)

    # 模板配置
    config = Column(JSON, nullable=False)  # 存储模板配置

    # 使用统计
    usage_count = Column(Integer, default=0)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    user = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, type={self.template_type})>"


# 注意：需要在应用启动后设置关系
# from models.user import User
# User.templates = relationship("Template", order_by=Template.id, back_populates="user")