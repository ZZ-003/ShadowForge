import cv2
import numpy as np
from PIL import Image

def create_pan_video(image_path, output_path, duration=10, fps=30):
    """
    Creates a video that pans/scrolls over a large image.
    If the image is taller than 1080p, it scrolls vertically.
    If it's wider than 1920p, it scales or scrolls? 
    For simplicity, we assume we want 1920x1080 output.
    """
    if not image_path or not output_path:
        return

    try:
        img_pil = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return

    img_w, img_h = img_pil.size
    
    # Use 2K output so text is easier to read than 1080p.
    target_w = 2560
    target_h = 1080

    # Fit image to target width first so code columns are preserved.
    scale = target_w / img_w
    new_w = target_w
    new_h = max(1, int(img_h * scale))
    img_resized = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if new_h <= target_h:
        # Do not zoom/crop short content; center it on a canvas so all code stays visible.
        final_img = Image.new("RGB", (target_w, target_h), (18, 18, 18))
        y_offset = (target_h - new_h) // 2
        final_img.paste(img_resized, (0, y_offset))
        max_scroll = 0
    else:
        # Tall image: keep full width and do vertical scroll only.
        final_img = img_resized
        max_scroll = final_img.height - target_h
        
    # Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    total_frames = duration * fps
    
    print(f"Generating video: {output_path}")
    print(f"Image size: {new_w}x{new_h}. Max scroll: {max_scroll}")
    
    for i in range(total_frames):
        t = i / total_frames
        
        if max_scroll > 0:
            # Scroll logic: Hold -> Scroll Down -> Hold
            # 0.0 - 0.2: Top
            # 0.2 - 0.8: Scroll
            # 0.8 - 1.0: Bottom
            
            if t < 0.2:
                y = 0
            elif t < 0.8:
                phase = (t - 0.2) / 0.6
                # Ease in out
                p = (1 - np.cos(phase * np.pi)) / 2
                y = int(p * max_scroll)
            else:
                y = max_scroll
        else:
            y = 0
            
        if max_scroll > 0:
            frame = final_img.crop((0, y, target_w, y + target_h))
        else:
            frame = final_img
        
        # Convert to BGR
        frame_np = np.array(frame)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        
        out.write(frame_bgr)
        
    out.release()
    print(f"Video saved to {output_path}")
