#!/usr/bin/env python3
"""
ShadowForge API 使用示例
展示如何通过API创建和管理生成任务
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8000/api"
USERNAME = "testuser"
PASSWORD = "testpassword123"
EMAIL = "test@example.com"

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def register_user():
    """注册用户"""
    print_section("1. 用户注册")

    data = {
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code == 200:
            print(f"[✓] 用户注册成功: {USERNAME}")
            return True
        elif response.status_code == 400:
            print(f"[i] 用户已存在: {USERNAME}")
            return True
        else:
            print(f"[✗] 注册失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return False

def login_user():
    """用户登录"""
    print_section("2. 用户登录")

    # 使用表单数据登录
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"[✓] 登录成功")
            print(f"    Token: {access_token[:50]}...")
            return access_token
        else:
            print(f"[✗] 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return None

def get_current_user(token):
    """获取当前用户信息"""
    print_section("3. 获取用户信息")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"[✓] 用户信息:")
            print(f"    ID: {user_data['id']}")
            print(f"    用户名: {user_data['username']}")
            print(f"    邮箱: {user_data['email']}")
            return user_data
        else:
            print(f"[✗] 获取用户信息失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return None

def create_task(token):
    """创建生成任务"""
    print_section("4. 创建生成任务")

    headers = {"Authorization": f"Bearer {token}"}

    task_data = {
        "name": "API Key泄露场景示例",
        "description": "通过API创建的测试任务",
        "secret": "sk-proj-test-1234567890abcdef",
        "secret_type": "OpenAI API Key",
        "modality": "image",
        "scene": "ide"
    }

    try:
        response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
        if response.status_code == 201:
            task = response.json()
            print(f"[✓] 任务创建成功")
            print(f"    任务ID: {task['id']}")
            print(f"    任务名称: {task['name']}")
            print(f"    状态: {task['status']}")
            return task
        else:
            print(f"[✗] 创建任务失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return None

def list_tasks(token):
    """获取任务列表"""
    print_section("5. 获取任务列表")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"[✓] 找到 {len(tasks)} 个任务")

            for i, task in enumerate(tasks[:3], 1):  # 只显示前3个
                print(f"    {i}. {task['name']} (ID: {task['id']}, 状态: {task['status']})")

            if len(tasks) > 3:
                print(f"    ... 还有 {len(tasks) - 3} 个任务")

            return tasks
        else:
            print(f"[✗] 获取任务列表失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return []

def get_task_details(token, task_id):
    """获取任务详情"""
    print_section("6. 获取任务详情")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
        if response.status_code == 200:
            task = response.json()
            print(f"[✓] 任务详情:")
            print(f"    ID: {task['id']}")
            print(f"    名称: {task['name']}")
            print(f"    描述: {task['description']}")
            print(f"    秘密类型: {task['secret_type']}")
            print(f"    模态: {task['modality']}")
            print(f"    场景: {task['scene']}")
            print(f"    状态: {task['status']}")
            print(f"    进度: {task['progress']}%")
            print(f"    创建时间: {task['created_at']}")
            return task
        else:
            print(f"[✗] 获取任务详情失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return None

def run_task(token, task_id):
    """运行任务"""
    print_section("7. 运行任务")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(f"{BASE_URL}/tasks/{task_id}/run", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[✓] 任务已开始运行: {result['message']}")
            return True
        else:
            print(f"[✗] 运行任务失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[✗] 连接失败: {e}")
        return False

def monitor_task_progress(token, task_id, max_checks=10):
    """监控任务进度"""
    print_section("8. 监控任务进度")

    headers = {"Authorization": f"Bearer {token}"}

    print(f"监控任务 {task_id} 进度...")

    for i in range(max_checks):
        try:
            response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
            if response.status_code == 200:
                task = response.json()
                status = task['status']
                progress = task['progress']

                print(f"  检查 {i+1}/{max_checks}: 状态={status}, 进度={progress}%")

                if status in ['completed', 'failed', 'cancelled']:
                    print(f"[✓] 任务完成，最终状态: {status}")
                    if task.get('output_files'):
                        print(f"    输出文件: {task['output_files']}")
                    return True

                time.sleep(2)  # 等待2秒再检查
            else:
                print(f"[✗] 获取任务状态失败: {response.status_code}")
                break

        except Exception as e:
            print(f"[✗] 连接失败: {e}")
            break

    print("[i] 监控超时")
    return False

def main():
    """主函数"""
    print("="*60)
    print("ShadowForge API 使用示例")
    print("="*60)
    print("\n这个示例展示如何通过API使用ShadowForge")
    print("确保后端服务正在运行 (http://localhost:8000)")
    print("="*60)

    # 1. 注册用户
    if not register_user():
        print("[!] 用户注册失败，跳过后续步骤")
        return

    # 2. 用户登录
    token = login_user()
    if not token:
        print("[!] 登录失败，无法继续")
        return

    # 3. 获取用户信息
    user = get_current_user(token)
    if not user:
        print("[!] 获取用户信息失败")
        return

    # 4. 创建任务
    task = create_task(token)
    if not task:
        print("[!] 创建任务失败")
        return

    task_id = task['id']

    # 5. 获取任务列表
    tasks = list_tasks(token)

    # 6. 获取任务详情
    get_task_details(token, task_id)

    # 7. 运行任务
    if task['status'] in ['pending', 'failed']:
        run_task(token, task_id)

    # 8. 监控任务进度（可选）
    monitor = input("\n是否监控任务进度？(y/n): ").lower().strip()
    if monitor == 'y':
        monitor_task_progress(token, task_id)

    print_section("示例完成")
    print("\nAPI端点测试完成！")
    print("\n您还可以测试:")
    print("1. 更新任务: PUT /api/tasks/{id}")
    print("2. 删除任务: DELETE /api/tasks/{id}")
    print("3. 取消任务: POST /api/tasks/{id}/cancel")
    print("4. 获取模板: GET /api/templates")
    print("5. 获取文件: GET /api/files")

    print("\n访问以下地址获取完整API文档:")
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] 用户中断")
    except Exception as e:
        print(f"\n[✗] 发生错误: {e}")