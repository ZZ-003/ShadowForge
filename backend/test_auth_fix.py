#!/usr/bin/env python3
"""
测试修复后的认证功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.auth import get_password_hash, verify_password

def test_password_hashing():
    """测试密码哈希功能"""
    print("测试密码哈希功能...")
    
    # 测试短密码
    short_password = "password123"
    hashed_short = get_password_hash(short_password)
    print(f"短密码哈希成功: {hashed_short[:20]}...")
    assert verify_password(short_password, hashed_short), "短密码验证失败"
    print("短密码验证成功")
    
    # 测试长密码（超过72字节）
    long_password = "a" * 100  # 100个字符，UTF-8编码后100字节
    hashed_long = get_password_hash(long_password)
    print(f"长密码哈希成功: {hashed_long[:20]}...")
    assert verify_password(long_password, hashed_long), "长密码验证失败"
    print("长密码验证成功")
    
    # 测试包含特殊字符的密码
    special_password = "密码测试123!@#$%^&*()中文字符"
    hashed_special = get_password_hash(special_password)
    print(f"特殊字符密码哈希成功: {hashed_special[:20]}...")
    assert verify_password(special_password, hashed_special), "特殊字符密码验证失败"
    print("特殊字符密码验证成功")
    
    # 测试超长特殊字符密码
    very_long_special = "超长密码测试" * 20  # 超过72字节
    hashed_very_long = get_password_hash(very_long_special)
    print(f"超长特殊字符密码哈希成功: {hashed_very_long[:20]}...")
    assert verify_password(very_long_special, hashed_very_long), "超长特殊字符密码验证失败"
    print("超长特殊字符密码验证成功")
    
    print("所有测试通过！")

if __name__ == "__main__":
    try:
        test_password_hashing()
        print("\n✅ 认证功能修复测试成功！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)