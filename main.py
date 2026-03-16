import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional, Callable
from PIL import Image
from llm_utils import get_client, analyze_secret, generate_content
from generators import VSCodeGenerator, CLIGenerator, ChatGenerator, ConfigGenerator, UIGenerator, AudioGenerator, PDFGenerator, WordGenerator, PPTGenerator
from generators.video_utils import create_pan_video


def add_image_noise(image, sigma=8.0, opacity=0.12):
    """Add subtle gaussian-like film grain to generated images."""
    noise = Image.effect_noise(image.size, sigma).convert("RGB")
    return Image.blend(image, noise, opacity)


def validate_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """验证配置字典的有效性"""
    errors = []

    required_keys = ["api_key", "base_url", "items"]
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required field: {key}")

    if not isinstance(config.get("items"), list):
        errors.append("'items' must be a list")

    if config.get("items"):
        for i, item in enumerate(config["items"]):
            if not isinstance(item, dict):
                errors.append(f"Item {i} must be a dictionary")
            else:
                if "secret" not in item:
                    errors.append(f"Item {i} missing 'secret' field")

    return len(errors) == 0, errors


def generate_from_config(
    config: Dict[str, Any],
    progress_callback: Optional[Callable[[int, str], None]] = None,
    output_dir: str = "output_universe"
) -> Dict[str, Any]:
    """
    程序化调用ShadowForge生成逻辑

    Args:
        config: 配置字典，包含api_key, base_url, items等
        progress_callback: 进度回调函数，接收(progress_percentage, status_message)
        output_dir: 输出目录

    Returns:
        {
            "success": bool,
            "output_files": List[str],
            "errors": List[str],
            "metadata": Dict[str, Any]
        }
    """
    result = {
        "success": False,
        "output_files": [],
        "errors": [],
        "metadata": {}
    }

    # 验证配置
    is_valid, validation_errors = validate_config(config)
    if not is_valid:
        result["errors"] = validation_errors
        return result

    # 提取配置
    api_key = config.get("api_key")
    base_url = config.get("base_url")
    items = config.get("items", [])
    add_noise = parse_bool(config.get("add_noise", False), default=False)

    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 初始化客户端和生成器
    try:
        client = get_client(api_key, base_url)
    except Exception as e:
        result["errors"].append(f"Failed to create LLM client: {str(e)}")
        return result

    # 初始化生成器
    vscode_gen = VSCodeGenerator()
    cli_gen = CLIGenerator()
    chat_gen = ChatGenerator()
    config_gen = ConfigGenerator()
    ui_gen = UIGenerator()
    audio_gen = AudioGenerator()
    pdf_gen = PDFGenerator()
    word_gen = WordGenerator()
    ppt_gen = PPTGenerator()

    total_items = len(items)
    output_files = []
    metadata = {
        "total_items": total_items,
        "successful": 0,
        "failed": 0,
        "items": []
    }

    # 处理每个item
    for i, item in enumerate(items):
        item_number = i + 1
        progress = int((i / total_items) * 100)

        try:
            secret = item.get("secret", "")
            secret_type = item.get("secret_type", "Generic Secret")
            modality = item.get("modality", "image").lower()

            if progress_callback:
                progress_callback(progress, f"Processing item {item_number}/{total_items}: {secret_type}")

            scene = item.get("scene", "")
            if scene:
                scene = scene.lower()
            else:
                scene = ""

            # 1. 分析 Secret -> Scenario
            if modality in ["audio", "pdf", "word", "ppt"]:
                scenario = modality
                scene_desc = f"Forced scenario: {scenario}"
            else:
                valid_scenes = ["ide", "cli", "chat", "config", "ui"]
                if scene and scene in valid_scenes:
                    scenario = scene
                    scene_desc = f"Specified scenario: {scenario}"
                else:
                    scenario = analyze_secret(client, secret_type)
                    scene_desc = f"Analyzed scenario: {scenario}"

            if progress_callback:
                progress_callback(progress, scene_desc)

            # 2. 生成内容
            secret_len = len(secret) if secret else 20
            content = generate_content(
                client, secret_type, scenario,
                secret_placeholder="SECRET_HERE",
                secret_len=secret_len,
                modality=modality
            )

            if not content:
                metadata["failed"] += 1
                metadata["items"].append({
                    "item_number": item_number,
                    "secret_type": secret_type,
                    "status": "failed",
                    "error": "Failed to generate content"
                })
                continue

            filename_base = f"leak_{item_number:02d}_{scenario}"
            output_path = None

            # 3. 根据场景生成文件
            if scenario == "ide":
                img = vscode_gen.generate_code_image(content, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                full_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(full_path)
                output_path = f"{filename_base}.png"  # 使用相对路径

            elif scenario == "cli":
                cmd = content.get("command", "")
                out = content.get("output", "")
                img = cli_gen.generate_cli_image(cmd, out, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                full_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(full_path)
                output_path = f"{filename_base}.png"  # 使用相对路径

            elif scenario == "chat":
                msgs = content.get("messages", [])
                img = chat_gen.generate_chat_image(msgs, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                full_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(full_path)
                output_path = f"{filename_base}.png"  # 使用相对路径

            elif scenario == "config":
                img = config_gen.generate_config_image(content, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                full_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(full_path)
                output_path = f"{filename_base}.png"  # 使用相对路径

            elif scenario == "ui":
                ui_type = content.get("type", "dashboard")
                ui_data = content.get("data", {})
                img = ui_gen.generate_ui_image(ui_type, ui_data, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                full_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(full_path)
                output_path = f"{filename_base}.png"  # 使用相对路径

            elif scenario == "audio":
                audio_path = os.path.join(output_dir, f"{filename_base}.mp3")
                result_path = audio_gen.generate_audio(content, audio_path, secret=secret)
                # 使用相对路径
                output_path = f"{filename_base}.mp3" if result_path else None

                if output_path and os.path.exists(audio_path):
                    if os.path.getsize(audio_path) < 100:
                        os.remove(audio_path)
                        output_path = None

            elif scenario == "pdf":
                full_path = os.path.join(output_dir, f"{filename_base}.pdf")
                pdf_gen.generate_pdf(content, full_path, secret=secret)
                output_path = f"{filename_base}.pdf"  # 使用相对路径

            elif scenario == "word":
                full_path = os.path.join(output_dir, f"{filename_base}.docx")
                word_gen.generate_docx(content, full_path, secret=secret)
                output_path = f"{filename_base}.docx"  # 使用相对路径

            elif scenario == "ppt":
                full_path = os.path.join(output_dir, f"{filename_base}.pptx")
                ppt_gen.generate_ppt(content, full_path, secret=secret)
                output_path = f"{filename_base}.pptx"  # 使用相对路径

            # 处理视频生成
            if output_path and "video" in modality and scenario in ["ide", "cli", "chat", "config", "ui"]:
                video_path = os.path.join(output_dir, f"{filename_base}.mp4")
                create_pan_video(os.path.join(output_dir, output_path), video_path)
                output_files.append(f"{filename_base}.mp4")  # 使用相对路径

                if "image" not in modality:
                    try:
                        os.remove(os.path.join(output_dir, output_path))
                    except OSError:
                        pass
                    output_path = f"{filename_base}.mp4"  # 使用相对路径
            elif output_path and "image" in modality:
                output_files.append(output_path)

            # 记录成功
            if output_path:
                metadata["successful"] += 1
                metadata["items"].append({
                    "item_number": item_number,
                    "secret_type": secret_type,
                    "scenario": scenario,
                    "modality": modality,
                    "output_path": output_path,
                    "status": "success"
                })

        except Exception as e:
            metadata["failed"] += 1
            metadata["items"].append({
                "item_number": item_number,
                "secret_type": item.get("secret_type", "Unknown"),
                "status": "failed",
                "error": str(e)
            })

    # 最终进度更新
    if progress_callback:
        final_message = f"Completed: {metadata['successful']}/{metadata['total_items']} successful, {metadata['failed']} failed"
        progress_callback(100, final_message)

    result["success"] = metadata["successful"] > 0
    result["output_files"] = output_files
    result["metadata"] = metadata

    return result


def load_config(config_path):
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing config file: {e}")
        sys.exit(1)

    required_keys = ["api_key", "base_url", "items"]
    missing = [k for k in required_keys if k not in config]
    if missing:
        print(f"Error: Missing required config fields: {', '.join(missing)}")
        sys.exit(1)

    if not isinstance(config.get("items"), list):
        print("Error: 'items' must be a JSON array.")
        sys.exit(1)

    return config


def parse_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "y", "on"}:
            return True
        if normalized in {"0", "false", "no", "n", "off"}:
            return False
    return default

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description="Generate multimodal secret leak scenarios.")
    parser.add_argument("--config", default="config/config.json", help="Path to config JSON file.")

    args = parser.parse_args()

    config = load_config(args.config)

    # 定义进度回调函数用于命令行输出
    def cli_progress_callback(progress: int, message: str):
        print(f"[{progress:3d}%] {message}")

    # 调用程序化生成函数
    result = generate_from_config(config, progress_callback=cli_progress_callback)

    # 输出结果摘要
    print("\n" + "="*50)
    print("Generation Summary")
    print("="*50)
    print(f"Total items: {result['metadata'].get('total_items', 0)}")
    print(f"Successful: {result['metadata'].get('successful', 0)}")
    print(f"Failed: {result['metadata'].get('failed', 0)}")

    if result['output_files']:
        print(f"\nOutput files ({len(result['output_files'])}):")
        for file_path in result['output_files']:
            print(f"  - {file_path}")

    if result['errors']:
        print(f"\nErrors ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    main()
