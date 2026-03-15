#!/usr/bin/env python3
import sys
import os

print("=== 最小化后端测试 ===")

# 测试最基本的导入
modules_to_test = [
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "uvicorn",
    "jose",
    "passlib",
    "pydantic_settings",
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {module} 导入成功")
    except ImportError as e:
        print(f"✗ {module} 导入失败: {e}")

print("\n=== 测试完成 ===")