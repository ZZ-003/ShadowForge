import argparse
import json
import os
import sys
from PIL import Image
from llm_utils import get_client, analyze_secret, generate_content
from generators import VSCodeGenerator, CLIGenerator, ChatGenerator, ConfigGenerator, UIGenerator, AudioGenerator, PDFGenerator, WordGenerator, PPTGenerator
from generators.video_utils import create_pan_video


def add_image_noise(image, sigma=8.0, opacity=0.12):
    """Add subtle gaussian-like film grain to generated images."""
    noise = Image.effect_noise(image.size, sigma).convert("RGB")
    return Image.blend(image, noise, opacity)


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
    parser = argparse.ArgumentParser(description="Generate multimodal secret leak scenarios.")
    parser.add_argument("--config", default="config/config.json", help="Path to config JSON file.")
    
    args = parser.parse_args()

    config = load_config(args.config)
    api_key = config.get("api_key")
    base_url = config.get("base_url")
    output_dir = config.get("output_dir", "output_universe")
    add_noise = parse_bool(config.get("add_noise", False), default=False)
    items = config.get("items", [])
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    client = get_client(api_key, base_url)
    
    # Initialize generators
    vscode_gen = VSCodeGenerator()
    cli_gen = CLIGenerator()
    chat_gen = ChatGenerator()
    config_gen = ConfigGenerator()
    ui_gen = UIGenerator()
    audio_gen = AudioGenerator()
    pdf_gen = PDFGenerator()
    word_gen = WordGenerator()
    ppt_gen = PPTGenerator()
    
    for i, item in enumerate(items):
        secret = item.get("secret")
        secret_type = item.get("secret_type", "Generic Secret")
        modality = item.get("modality", "image").lower() # image, video, audio, pdf, word, ppt
        
        print(f"Processing item {i+1}/{len(items)}: {secret_type} ({modality})")
        
        scene = item.get("scene", "").lower()
        
        # 1. Analyze Secret -> Scenario
        # IMPORTANT: If modality is one of [audio, pdf, word, ppt], we should FORCE that scenario
        # instead of asking the LLM, because the user explicitly requested that file type.
        # The "analyze_secret" function currently returns 'ide', 'cli' etc. based on secret type,
        # which might mismatch the requested modality (e.g., user wants PDF, but LLM says "ide" is best for API key).
        
        if modality in ["audio", "pdf", "word", "ppt"]:
            scenario = modality
            print(f"  -> Forcing Scenario based on modality: {scenario}")
        else:
            valid_scenes = ["ide", "cli", "chat", "config", "ui"]
            if scene and scene in valid_scenes:
                scenario = scene
                print(f"  -> Using specified Scenario: {scenario}")
            else:
                if scene:
                    print(f"  -> Warning: Invalid scene '{scene}'. Falling back to analysis.")
                scenario = analyze_secret(client, secret_type)
                print(f"  -> Selected Scenario: {scenario}")
        
        # 2. Generate Content
        secret_len = len(secret) if secret else 20
        content = generate_content(client, secret_type, scenario, secret_placeholder="SECRET_HERE", secret_len=secret_len, modality=modality)
        if not content:
            print("  -> Failed to generate content. Skipping.")
            continue
            
        filename_base = f"leak_{i+1:02d}_{scenario}"
        
        # 3. Generate Asset based on Scenario
        try:
            if scenario == "ide":
                img = vscode_gen.generate_code_image(content, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(img_path)
            elif scenario == "cli":
                cmd = content.get("command", "")
                out = content.get("output", "")
                img = cli_gen.generate_cli_image(cmd, out, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(img_path)
            elif scenario == "chat":
                msgs = content.get("messages", [])
                img = chat_gen.generate_chat_image(msgs, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(img_path)
            elif scenario == "config":
                img = config_gen.generate_config_image(content, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(img_path)
            elif scenario == "ui":
                ui_type = content.get("type", "dashboard")
                ui_data = content.get("data", {})
                img = ui_gen.generate_ui_image(ui_type, ui_data, secret=secret)
                if add_noise:
                    img = add_image_noise(img)
                img_path = os.path.join(output_dir, f"{filename_base}.png")
                img.save(img_path)
                
            elif scenario == "audio":
                audio_path = os.path.join(output_dir, f"{filename_base}.mp3")
                final_path = audio_gen.generate_audio(content, audio_path, secret=secret)
                
                if final_path:
                    print(f"  -> Saved audio: {final_path}")
                    
                    # If we fell back to WAV, and the original path was MP3, 
                    # we should probably delete the empty MP3 if it was created (unlikely by us, but gTTS might have touched it)
                    if final_path != audio_path and os.path.exists(audio_path):
                        # Only delete if size is 0 or very small (indicating failure)
                        if os.path.getsize(audio_path) < 100:
                            os.remove(audio_path)
                else:
                    print("  -> Failed to generate audio")
                    
                continue 
                 
                
            elif scenario == "pdf":
                pdf_path = os.path.join(output_dir, f"{filename_base}.pdf")
                pdf_gen.generate_pdf(content, pdf_path, secret=secret)
                print(f"  -> Saved PDF: {pdf_path}")
                continue
                
            elif scenario == "word":
                word_path = os.path.join(output_dir, f"{filename_base}.docx")
                word_gen.generate_docx(content, word_path, secret=secret)
                print(f"  -> Saved Word Doc: {word_path}")
                continue
                
            elif scenario == "ppt":
                ppt_path = os.path.join(output_dir, f"{filename_base}.pptx")
                ppt_gen.generate_ppt(content, ppt_path, secret=secret)
                print(f"  -> Saved PPT: {ppt_path}")
                continue
                
            else:
                print(f"  -> Unknown scenario: {scenario}")
                continue

            # --- Image/Video Handling (for visual scenarios) ---
            
            # If the user requested "video", we ALWAYS generate a video from the image.
            # If the user requested "image", we save the image.
            # If the user requested both, we do both.
            
            # Note: "modality" variable contains what the user asked for (e.g. "image", "video").
            # "scenario" variable is what KIND of content it is (e.g. "ide", "cli").
            
            # We already saved the image to `img_path` above for visual scenarios.
            
            if "image" in modality:
                print(f"  -> Saved image: {img_path}")
            
            if "video" in modality:
                video_path = os.path.join(output_dir, f"{filename_base}.mp4")
                create_pan_video(img_path, video_path)
                print(f"  -> Saved video: {video_path}")
                
                # If video only, remove the intermediate image
                if "image" not in modality:
                    try:
                        os.remove(img_path)
                    except OSError as e:
                        print(f"  -> Warning: Could not remove intermediate image: {e}")
                        
        except Exception as e:
            print(f"  -> Error generating asset: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
