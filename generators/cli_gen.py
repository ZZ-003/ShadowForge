import os
from PIL import Image, ImageDraw, ImageFont

class CLIGenerator:
    def __init__(self, font_name="DejaVu Sans Mono", font_size=20):
        self.font_name = font_name
        self.font_size = font_size
        # Terminal colors
        self.bg_color = (0, 0, 0) # Pure black or very dark grey
        self.fg_color = (200, 200, 200) # Light grey text
        self.prompt_color = (0, 255, 0) # Green prompt
        self.path_color = (50, 150, 255) # Blue path
        self.error_color = (255, 80, 80) # Red for errors/secrets sometimes
        
        self.font_path = self._find_font(font_name)

    def _find_font(self, font_name):
        common_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def generate_cli_image(self, command, output, secret=None, secret_placeholder="SECRET_HERE"):
        """
        Generates a terminal screenshot.
        """
        
        # 1. Prepare Content
        if secret and secret_placeholder in command:
            command = command.replace(secret_placeholder, secret)
        if secret and secret_placeholder in output:
            output = output.replace(secret_placeholder, secret)
            
        # Construct the full text session
        # We simulate a prompt like: user@hostname:~/project$ command
        prompt_user = "user@devbox"
        prompt_path = "~/project"
        prompt_char = "$"
        
        # 2. Setup Font
        try:
            font = ImageFont.truetype(self.font_path, self.font_size) if self.font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        # 3. Calculate Dimensions
        # We need to measure various parts
        lines = []
        
        # Line 1: Prompt + Command
        # We'll handle coloring by drawing parts separately, but for size we treat it as one line
        full_command_line = f"{prompt_user}:{prompt_path}{prompt_char} {command}"
        lines.append(full_command_line)
        
        # Output lines
        output_lines = output.split('\n')
        lines.extend(output_lines)
        
        # Next prompt (empty)
        lines.append(f"{prompt_user}:{prompt_path}{prompt_char} \u2588") # \u2588 is block cursor
        
        line_height = int(self.font_size * 1.5)
        
        # Calculate max width
        max_width = 0
        for line in lines:
            try:
                w = font.getlength(line)
            except:
                w = font.getsize(line)[0]
            if w > max_width:
                max_width = w
                
        # Dimensions
        padding = 40
        img_width = max(1000, int(max_width + padding * 2))
        img_height = int(len(lines) * line_height + padding * 2)
        
        image = Image.new('RGB', (img_width, img_height), self.bg_color)
        draw = ImageDraw.Draw(image)
        
        # 4. Draw Content
        current_y = padding
        x = padding
        
        # Draw Command Line
        # user@devbox (Green)
        draw.text((x, current_y), f"{prompt_user}", font=font, fill=self.prompt_color)
        try:
            w = font.getlength(f"{prompt_user}")
        except:
            w = font.getsize(f"{prompt_user}")[0]
        x += w
        
        # : (Grey)
        draw.text((x, current_y), ":", font=font, fill=self.fg_color)
        try:
            w = font.getlength(":")
        except:
            w = font.getsize(":")[0]
        x += w
        
        # ~/project (Blue)
        draw.text((x, current_y), f"{prompt_path}", font=font, fill=self.path_color)
        try:
            w = font.getlength(f"{prompt_path}")
        except:
            w = font.getsize(f"{prompt_path}")[0]
        x += w
        
        # $ (Grey)
        draw.text((x, current_y), f"{prompt_char} ", font=font, fill=self.fg_color)
        try:
            w = font.getlength(f"{prompt_char} ")
        except:
            w = font.getsize(f"{prompt_char} ")[0]
        x += w
        
        # Command (White/Bright)
        draw.text((x, current_y), command, font=font, fill=(255, 255, 255))
        
        current_y += line_height
        
        # Draw Output
        for line in output_lines:
            draw.text((padding, current_y), line, font=font, fill=self.fg_color)
            current_y += line_height
            
        # Draw Final Prompt
        x = padding
        draw.text((x, current_y), f"{prompt_user}", font=font, fill=self.prompt_color)
        try:
            w = font.getlength(f"{prompt_user}")
        except:
            w = font.getsize(f"{prompt_user}")[0]
        x += w
        draw.text((x, current_y), ":", font=font, fill=self.fg_color)
        try:
            w = font.getlength(":")
        except:
            w = font.getsize(":")[0]
        x += w
        draw.text((x, current_y), f"{prompt_path}", font=font, fill=self.path_color)
        try:
            w = font.getlength(f"{prompt_path}")
        except:
            w = font.getsize(f"{prompt_path}")[0]
        x += w
        draw.text((x, current_y), f"{prompt_char} ", font=font, fill=self.fg_color)
        try:
            w = font.getlength(f"{prompt_char} ")
        except:
            w = font.getsize(f"{prompt_char} ")[0]
        x += w
        
        # Cursor
        draw.text((x, current_y), "\u2588", font=font, fill=(150, 150, 150))

        return image


