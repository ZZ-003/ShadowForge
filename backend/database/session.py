from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    # 导入所有模型以确保它们被注册
    from models.user import User
    from models.task import Task
    from models.template import Template

    # 设置关系（避免循环导入）
    from sqlalchemy.orm import relationship

    # 设置User和Task的关系
    User.tasks = relationship("Task", order_by=Task.id, back_populates="user")
    Task.user = relationship("User", back_populates="tasks")

    # 设置User和Template的关系
    User.templates = relationship("Template", order_by=Template.id, back_populates="user")
    Template.user = relationship("User", back_populates="templates")

    # 创建所有表
    Base.metadata.create_all(bind=engine)