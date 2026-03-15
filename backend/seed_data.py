"""
种子数据脚本
用于初始化预定义的模板数据
"""
from sqlalchemy.orm import Session
from models.template import Template, TemplateType
from models.user import User


PREDEFINED_TEMPLATES = [
    {
        "name": "OpenAI API Key - IDE场景",
        "description": "OpenAI API密钥在VS Code中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "OpenAI API Key",
            "modality": "image",
            "scene": "ide",
            "example_secret": "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
    },
    {
        "name": "AWS Access Key - CLI场景",
        "description": "AWS访问密钥在终端命令中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "AWS Access Key",
            "modality": "image",
            "scene": "cli",
            "example_secret": "AKIAIOSFODNN7EXAMPLE"
        }
    },
    {
        "name": "Database URL - 配置文件场景",
        "description": "数据库连接字符串在配置文件中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "Database URL",
            "modality": "image",
            "scene": "config",
            "example_secret": "postgresql://user:pass@host:5432/db"
        }
    },
    {
        "name": "API Key - 聊天场景",
        "description": "API密钥在团队聊天中意外分享的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "API Key",
            "modality": "image",
            "scene": "chat",
            "example_secret": "api_key_1234567890abcdef"
        }
    },
    {
        "name": "JWT Secret - UI仪表板场景",
        "description": "JWT密钥在开发工具仪表板中显示的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "JWT Secret",
            "modality": "image",
            "scene": "ui",
            "example_secret": "your-super-secret-jwt-key-2024"
        }
    },
    {
        "name": "API Token - 音频场景",
        "description": "API令牌在语音笔记中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "API Token",
            "modality": "audio",
            "scene": "audio",
            "example_secret": "ghp_1234567890abcdef1234567890abcdef"
        }
    },
    {
        "name": "Secret Key - PDF文档场景",
        "description": "秘密密钥在PDF文档中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "Secret Key",
            "modality": "pdf",
            "scene": "pdf",
            "example_secret": "sk_****************************"
        }
    },
    {
        "name": "Password - Word文档场景",
        "description": "密码在内部Word文档中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "Password",
            "modality": "word",
            "scene": "word",
            "example_secret": "SecurePass123!@#"
        }
    },
    {
        "name": "Client Secret - PPT演示场景",
        "description": "客户端密钥在PowerPoint演示文稿中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "Client Secret",
            "modality": "ppt",
            "scene": "ppt",
            "example_secret": "client_secret_abcdef1234567890"
        }
    },
    {
        "name": "Redis Password - 视频场景",
        "description": "Redis密码在代码编辑器滚动视频中泄露的场景",
        "template_type": TemplateType.COMPLETE,
        "is_public": True,
        "config": {
            "secret_type": "Redis Password",
            "modality": "video",
            "scene": "ide",
            "example_secret": "redis_secure_password_2024"
        }
    }
]


PREDEFINED_SECRET_TYPES = [
    {
        "name": "OpenAI API Key",
        "description": "OpenAI API密钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "OpenAI API Key"}
    },
    {
        "name": "AWS Access Key",
        "description": "AWS访问密钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "AWS Access Key"}
    },
    {
        "name": "GitHub Token",
        "description": "GitHub个人访问令牌",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "GitHub Token"}
    },
    {
        "name": "Database URL",
        "description": "数据库连接字符串",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "Database URL"}
    },
    {
        "name": "JWT Secret",
        "description": "JWT签名密钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "JWT Secret"}
    },
    {
        "name": "API Key",
        "description": "通用API密钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "API Key"}
    },
    {
        "name": "Password",
        "description": "用户密码",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "Password"}
    },
    {
        "name": "Client Secret",
        "description": "OAuth客户端密钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "Client Secret"}
    },
    {
        "name": "Private Key",
        "description": "SSH私钥或SSL私钥",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "Private Key"}
    },
    {
        "name": "Token",
        "description": "各种认证令牌",
        "template_type": TemplateType.SECRET_TYPE,
        "is_public": True,
        "config": {"value": "Token"}
    }
]


PREDEFINED_SCENES = [
    {
        "name": "IDE代码编辑器",
        "description": "在代码编辑器（如VS Code）中展示秘密",
        "template_type": TemplateType.SCENE,
        "is_public": True,
        "config": {"value": "ide"}
    },
    {
        "name": "CLI终端",
        "description": "在命令行终端中展示秘密",
        "template_type": TemplateType.SCENE,
        "is_public": True,
        "config": {"value": "cli"}
    },
    {
        "name": "团队聊天",
        "description": "在团队聊天工具中展示秘密",
        "template_type": TemplateType.SCENE,
        "is_public": True,
        "config": {"value": "chat"}
    },
    {
        "name": "配置文件",
        "description": "在配置文件中展示秘密",
        "template_type": TemplateType.SCENE,
        "is_public": True,
        "config": {"value": "config"}
    },
    {
        "name": "UI仪表板",
        "description": "在用户界面中展示秘密",
        "template_type": TemplateType.SCENE,
        "is_public": True,
        "config": {"value": "ui"}
    }
]


def seed_templates(db: Session, system_user_id: int = None):
    """初始化预定义模板"""
    templates = PREDEFINED_TEMPLATES + PREDEFINED_SECRET_TYPES + PREDEFINED_SCENES

    for template_data in templates:
        # 检查是否已存在
        existing = db.query(Template).filter(
            Template.name == template_data["name"]
        ).first()

        if existing:
            continue

        template = Template(
            user_id=system_user_id or 1,  # 使用系统用户ID
            **template_data
        )
        db.add(template)

    db.commit()
    print(f"已创建 {len(templates)} 个预定义模板")


def create_system_user(db: Session) -> User:
    """创建系统用户（用于管理公共模板）"""
    system_user = db.query(User).filter(
        User.username == "system"
    ).first()

    if not system_user:
        from core.auth import get_password_hash
        system_user = User(
            username="system",
            email="system@shadowforge.local",
            hashed_password=get_password_hash("system_password_change_me"),
            is_active=True,
            is_superuser=True
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
        print("已创建系统用户")

    return system_user


def run_seeding(db: Session):
    """运行所有种子数据初始化"""
    print("开始初始化种子数据...")

    # 创建系统用户
    system_user = create_system_user(db)

    # 初始化模板
    seed_templates(db, system_user.id)

    print("种子数据初始化完成！")
