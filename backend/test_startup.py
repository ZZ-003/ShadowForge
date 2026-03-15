#!/usr/bin/env python3
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 后端启动测试 ===")

# 测试1: 导入设置
try:
    from config.settings import settings
    print("✓ 设置导入成功")
    print(f"  应用名称: {settings.app_name}")
    print(f"  数据库URL: {settings.database_url}")
except Exception as e:
    print(f"✗ 设置导入失败: {e}")
    sys.exit(1)

# 测试2: 导入数据库
try:
    from database.session import init_db, engine
    print("✓ 数据库模块导入成功")
except Exception as e:
    print(f"✗ 数据库模块导入失败: {e}")
    sys.exit(1)

# 测试3: 初始化数据库
try:
    print("正在初始化数据库...")
    init_db()
    print("✓ 数据库初始化成功")
except Exception as e:
    print(f"✗ 数据库初始化失败: {e}")
    sys.exit(1)

# 测试4: 导入API路由
try:
    from api import auth, tasks, templates, files, config
    print("✓ API路由导入成功")
except Exception as e:
    print(f"✗ API路由导入失败: {e}")
    sys.exit(1)

# 测试5: 创建FastAPI应用
try:
    from fastapi import FastAPI
    app = FastAPI(title=settings.app_name)
    print("✓ FastAPI应用创建成功")
except Exception as e:
    print(f"✗ FastAPI应用创建失败: {e}")
    sys.exit(1)

print("\n=== 所有测试通过 ===")
print("后端可以正常启动！")
print(f"API文档地址: http://localhost:8000/docs")