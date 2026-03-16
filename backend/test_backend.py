#!/usr/bin/env python3
"""
测试后端启动的简单脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试导入主要模块
    from main import app
    print("✅ 成功导入FastAPI应用")
    
    # 测试数据库连接
    from database.session import init_db
    print("✅ 成功导入数据库模块")
    
    # 测试设置
    from config.settings import settings
    print(f"✅ 成功导入设置: {settings.app_name} v{settings.app_version}")
    
    # 测试模型导入
    from models.user import User
    from models.task import Task
    from models.template import Template
    print("✅ 成功导入所有模型")
    
    # 测试API路由导入
    from api import auth, tasks, templates, files, config
    print("✅ 成功导入所有API路由")
    
    print("\n🎉 所有导入测试通过！后端应该可以正常启动。")
    print(f"\n启动命令: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 其他错误: {e}")
    import traceback
    traceback.print_exc()