import os
from PIL import Image, ImageDraw, ImageFont

class ConfigGenerator:
    def __init__(self, font_name="DejaVu Sans Mono", font_size=22):
        self.font_name = font_name
        self.font_size = font_size
        self.font_path = self._find_font(font_name)
        
        # Color schemes for different editors/viewers
        self.themes = {
            'sublime': {
                'bg': (39, 40, 34),
                'fg': (248, 248, 242),
                'key': (102, 217, 239), # Blueish
                'val': (230, 219, 116), # Yellowish
                'comment': (117, 113, 94)
            },
            'vim': {
                'bg': (0, 0, 0),
                'fg': (200, 200, 200),
                'key': (130, 130, 255),
                'val': (255, 130, 130),
                'comment': (0, 150, 200) # Blue comments
            },
            'notepad': {
                'bg': (255, 255, 255),
                'fg': (0, 0, 0),
                'key': (0, 0, 0),
                'val': (0, 0, 0),
                'comment': (0, 128, 0)
            },
            'nano': {
                'bg': (20, 20, 20),
                'fg': (255, 255, 255),
                'key': (100, 255, 255), # Cyan
                'val': (255, 255, 255),
                'comment': (255, 255, 0) # Yellow title bar simulated?
            }
        }

    def _find_font(self, font_name):
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def generate_config_image(self, content, format_type='ini', theme_name='sublime', secret=None, secret_placeholder="SECRET_HERE"):
        """
        format_type: 'ini', 'yaml', 'xml', 'properties'
        """
        
        # 1. Prepare Content
        if secret and secret_placeholder in content:
            content = content.replace(secret_placeholder, secret)
            
        theme = self.themes.get(theme_name, self.themes['sublime'])
        
        try:
            font = ImageFont.truetype(self.font_path, self.font_size) if self.font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
            
        lines = content.split('\n')
        line_height = int(self.font_size * 1.5)
        
        # Measure width
        max_width = 0
        for line in lines:
            try:
                w = font.getlength(line)
            except:
                w = font.getsize(line)[0]
            if w > max_width:
                max_width = w
                
        padding = 40
        img_width = max(800, int(max_width + padding * 2))
        img_height = int(len(lines) * line_height + padding * 2)
        
        # Add a title bar for "Notepad" or "Vim" feel
        title_bar_height = 40 if theme_name in ['notepad', 'nano'] else 0
        img_height += title_bar_height
        
        image = Image.new('RGB', (img_width, img_height), theme['bg'])
        draw = ImageDraw.Draw(image)
        
        current_y = 0
        
        # Draw Title Bar
        if theme_name == 'notepad':
            draw.rectangle([0, 0, img_width, title_bar_height], fill=(240, 240, 240))
            draw.text((10, 10), "config.txt - Notepad", font=font, fill=(0, 0, 0))
            draw.line([0, title_bar_height, img_width, title_bar_height], fill=(200, 200, 200))
            current_y += title_bar_height + padding
        elif theme_name == 'nano':
            draw.rectangle([0, 0, img_width, title_bar_height], fill=(200, 200, 200))
            draw.text((img_width/2 - 50, 10), "GNU nano 5.4", font=font, fill=(0, 0, 0))
            current_y += title_bar_height + padding
        else:
            current_y += padding
            
        x_start = padding
        
        # Simple Syntax Highlighting Logic
        for line in lines:
            line_stripped = line.strip()
            
            # Comments
            if line_stripped.startswith('#') or line_stripped.startswith('//') or line_stripped.startswith(';'):
                draw.text((x_start, current_y), line, font=font, fill=theme['comment'])
            
            # Key-Value pairs
            elif '=' in line or ':' in line:
                # Naive split
                if '=' in line:
                    sep = '='
                else:
                    sep = ':'
                
                parts = line.split(sep, 1)
                key_part = parts[0]
                val_part = parts[1] if len(parts) > 1 else ""
                
                # Draw Key
                draw.text((x_start, current_y), key_part, font=font, fill=theme['key'])
                
                # Draw Separator
                try:
                    key_width = font.getlength(key_part)
                except:
                    key_width = font.getsize(key_part)[0]
                draw.text((x_start + key_width, current_y), sep, font=font, fill=theme['fg'])
                
                # Draw Value
                try:
                    sep_width = font.getlength(sep)
                except:
                    sep_width = font.getsize(sep)[0]
                draw.text((x_start + key_width + sep_width, current_y), val_part, font=font, fill=theme['val'])
                
            else:
                # Plain text / XML tags / Brackets
                draw.text((x_start, current_y), line, font=font, fill=theme['fg'])
                
            current_y += line_height
            
        # Nano Footer
        if theme_name == 'nano':
             footer_y = img_height - 60
             draw.rectangle([0, footer_y, img_width, img_height], fill=(200, 200, 200))
             draw.text((20, footer_y + 20), "^G Help  ^O Write Out  ^W Where Is", font=font, fill=(0, 0, 0))

        return image


