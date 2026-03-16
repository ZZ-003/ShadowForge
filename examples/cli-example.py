#!/usr/bin/env python3
"""
ShadowForge 命令行工具使用示例
展示如何使用命令行工具生成多模态泄露场景
"""

import json
import os
import sys
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def create_sample_config():
    """创建示例配置文件"""
    print_section("1. 创建示例配置文件")

    config = {
        "api_key": "your-llm-api-key-here",  # 替换为您的API密钥
        "base_url": "https://api.deepseek.com",
        "output_dir": "example_output",
        "add_noise": False,
        "items": [
            {
                "secret": "sk-proj-test-1234567890abcdef",
                "secret_type": "OpenAI API Key",
                "modality": "image",
                "scene": "ide"
            },
            {
                "secret": "AKIAIOSFODNN7EXAMPLE",
                "secret_type": "AWS Access Key",
                "modality": "image",
                "scene": "cli"
            },
            {
                "secret": "postgresql://user:password@localhost:5432/db",
                "secret_type": "Database URL",
                "modality": "image",
                "scene": "config"
            },
            {
                "secret": "api_key_1234567890abcdef",
                "secret_type": "API Key",
                "modality": "image",
                "scene": "chat"
            },
            {
                "secret": "your-jwt-secret-key-2024",
                "secret_type": "JWT Secret",
                "modality": "image",
                "scene": "ui"
            },
            {
                "secret": "ghp_1234567890abcdef1234567890abcdef",
                "secret_type": "GitHub Token",
                "modality": "audio"
            },
            {
                "secret": "redis_password_secure_2024",
                "secret_type": "Redis Password",
                "modality": "video",
                "scene": "ide"
            }
        ]
    }

    # 创建输出目录
    os.makedirs("example_output", exist_ok=True)

    # 保存配置文件
    config_path = "example_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"[✓] 配置文件已创建: {config_path}")
    print(f"[✓] 输出目录已创建: example_output/")
    print("\n配置文件内容预览:")
    print(json.dumps(config, indent=2, ensure_ascii=False)[:500] + "...")

    return config_path

def run_generation(config_path):
    """运行生成任务"""
    print_section("2. 运行生成任务")

    try:
        # 导入主模块
        from main import generate_from_config

        # 读取配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        # 检查API密钥
        if config["api_key"] == "your-llm-api-key-here":
            print("[!] 警告: 请编辑配置文件，填入您的LLM API密钥")
            print("    当前使用测试配置，可能无法正常工作")
            print("    按 Enter 继续测试...")
            input()

        print(f"开始生成 {len(config['items'])} 个项目...")

        # 定义进度回调函数
        def progress_callback(progress, message):
            print(f"  [{progress:3d}%] {message}")

        # 运行生成
        start_time = time.time()
        result = generate_from_config(config, progress_callback, "example_output")
        elapsed_time = time.time() - start_time

        print(f"\n[✓] 生成完成，耗时: {elapsed_time:.1f}秒")

        # 显示结果
        print(f"  总项目数: {result['metadata'].get('total_items', 0)}")
        print(f"  成功: {result['metadata'].get('successful', 0)}")
        print(f"  失败: {result['metadata'].get('failed', 0)}")

        if result['output_files']:
            print(f"\n生成的文件 ({len(result['output_files'])}):")
            for file_path in result['output_files']:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                print(f"  - {os.path.basename(file_path)} ({file_size} bytes)")

        if result['errors']:
            print(f"\n错误 ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")

        return result

    except ImportError as e:
        print(f"[✗] 导入失败: {e}")
        print("请确保在项目根目录运行此脚本")
        return None
    except Exception as e:
        print(f"[✗] 生成失败: {e}")
        return None

def show_generated_files():
    """显示生成的文件"""
    print_section("3. 查看生成的文件")

    output_dir = "example_output"

    if not os.path.exists(output_dir):
        print(f"[!] 输出目录不存在: {output_dir}")
        return

    files = []
    for root, dirs, filenames in os.walk(output_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            files.append((filename, file_size, file_path))

    if not files:
        print("[!] 没有找到生成的文件")
        return

    print(f"找到 {len(files)} 个文件:")

    # 按文件类型分组
    file_types = {}
    for filename, size, path in files:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in file_types:
            file_types[ext] = []
        file_types[ext].append((filename, size, path))

    for ext, file_list in file_types.items():
        print(f"\n{ext.upper()} 文件 ({len(file_list)}):")
        for filename, size, path in file_list[:5]:  # 只显示前5个
            print(f"  - {filename} ({size} bytes)")

        if len(file_list) > 5:
            print(f"  ... 还有 {len(file_list) - 5} 个文件")

def show_usage_instructions():
    """显示使用说明"""
    print_section("4. 使用说明")

    print("命令行工具基本用法:")
    print("\n1. 准备配置文件:")
    print("   cp config/config_sample.json config/config.json")
    print("   # 编辑 config/config.json，填入您的API密钥")

    print("\n2. 运行生成:")
    print("   python main.py")
    print("   # 或指定配置文件")
    print("   python main.py --config example_config.json")

    print("\n3. 程序化调用 (Python代码):")
    print("   from main import generate_from_config")
    print("   ")
    print("   config = {")
    print("       'api_key': 'your-key',")
    print("       'base_url': 'https://api.deepseek.com',")
    print("       'items': [...]")
    print("   }")
    print("   ")
    print("   result = generate_from_config(config)")
    print("   print(result['output_files'])")

    print("\n4. 支持的模态:")
    print("   - image: 图片 (PNG)")
    print("   - video: 视频 (MP4)")
    print("   - audio: 音频 (MP3/WAV)")
    print("   - pdf: PDF文档")
    print("   - word: Word文档 (DOCX)")
    print("   - ppt: PowerPoint演示文稿 (PPTX)")

    print("\n5. 支持的场景:")
    print("   - ide: IDE代码编辑器")
    print("   - cli: 命令行终端")
    print("   - chat: 团队聊天")
    print("   - config: 配置文件")
    print("   - ui: Web UI仪表板")

def main():
    """主函数"""
    print("="*60)
    print("ShadowForge 命令行工具使用示例")
    print("="*60)
    print("\n这个示例展示如何使用命令行工具生成多模态泄露场景")
    print("="*60)

    try:
        # 1. 创建示例配置
        config_path = create_sample_config()

        # 询问是否运行生成
        run_now = input("\n是否运行生成？(y/n): ").lower().strip()
        if run_now == 'y':
            # 2. 运行生成
            result = run_generation(config_path)

            if result and result.get('success'):
                # 3. 显示生成的文件
                show_generated_files()

        # 4. 显示使用说明
        show_usage_instructions()

        print_section("示例完成")
        print("\n更多信息:")
        print("- 查看完整文档: README.md")
        print("- 访问Web应用: http://localhost:3000")
        print("- API文档: http://localhost:8000/docs")

    except KeyboardInterrupt:
        print("\n\n[!] 用户中断")
    except Exception as e:
        print(f"\n[✗] 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()