import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

class ChatGenerator:
    def __init__(self, font_name="DejaVu Sans", font_size=20):
        self.font_name = font_name
        self.font_size = font_size
        
        # Colors (Slack/Teams/Discord ish)
        self.bg_color = (255, 255, 255) # White background
        self.bubble_user_bg = (0, 122, 255) # Blue bubble (sender)
        self.bubble_user_fg = (255, 255, 255) # White text
        self.bubble_other_bg = (230, 230, 230) # Grey bubble (receiver)
        self.bubble_other_fg = (0, 0, 0) # Black text
        self.timestamp_color = (150, 150, 150)
        self.avatar_colors = [(100, 200, 100), (200, 100, 100), (100, 100, 200)]
        
        self.font_path = self._find_font(font_name)
        # Try to find a bold font for names
        self.font_bold_path = self._find_font(font_name, bold=True)

    def _find_font(self, font_name, bold=False):
        # Simplified lookup
        if bold:
            candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
            ]
        else:
            candidates = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
            ]
            
        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def draw_bubble(self, draw, x, y, width, height, color, is_right=False):
        radius = 15
        draw.rounded_rectangle([x, y, x + width, y + height], radius, fill=color)
        
        # Optional: Add a little tail
        if is_right:
            points = [(x + width, y + height - 20), (x + width + 10, y + height), (x + width - 10, y + height)]
        else:
            points = [(x, y + height - 20), (x - 10, y + height), (x + 10, y + height)]
        # draw.polygon(points, fill=color) # Skip tail for modern "rounded" look

    def generate_chat_image(self, messages, secret=None, secret_placeholder="SECRET_HERE"):
        """
        messages: list of dicts {'sender': 'Bob', 'text': '...', 'is_me': False}
        """
        
        # 1. Setup Fonts
        try:
            font = ImageFont.truetype(self.font_path, self.font_size) if self.font_path else ImageFont.load_default()
            font_bold = ImageFont.truetype(self.font_bold_path, self.font_size) if self.font_bold_path else font
            font_small = ImageFont.truetype(self.font_path, int(self.font_size * 0.8)) if self.font_path else font
        except:
            font = ImageFont.load_default()
            font_bold = font
            font_small = font
            
        # 2. Layout Calculation
        img_width = 800
        padding = 20
        bubble_padding = 15
        avatar_size = 50
        max_bubble_width = int(img_width * 0.65)
        
        y_cursor = padding
        
        layout_items = []
        
        for msg in messages:
            text = msg['text']
            if secret and secret_placeholder in text:
                text = text.replace(secret_placeholder, secret)
            
            # Wrap text
            # We need to wrap based on pixel width, but textwrap uses chars.
            # Simple approximation: char_width approx font_size / 2
            avg_char_width = self.font_size * 0.5
            chars_per_line = int(max_bubble_width / avg_char_width)
            wrapped_lines = textwrap.wrap(text, width=chars_per_line)
            
            # Measure actual dimensions
            bubble_w = 0
            bubble_h = 0
            line_height = int(self.font_size * 1.3)
            
            for line in wrapped_lines:
                try:
                    w = font.getlength(line)
                except:
                    w = font.getsize(line)[0]
                if w > bubble_w:
                    bubble_w = w
            
            bubble_w += bubble_padding * 2
            bubble_h = len(wrapped_lines) * line_height + bubble_padding * 2
            
            layout_items.append({
                'msg': msg,
                'wrapped_lines': wrapped_lines,
                'width': bubble_w,
                'height': bubble_h,
                'y': y_cursor
            })
            
            y_cursor += bubble_h + padding + 10 # +10 for name/spacing
            
        img_height = y_cursor + padding
        
        image = Image.new('RGB', (img_width, img_height), self.bg_color)
        draw = ImageDraw.Draw(image)
        
        # 3. Draw
        for item in layout_items:
            msg = item['msg']
            is_me = msg.get('is_me', False)
            y = item['y']
            w = item['width']
            h = item['height']
            
            if is_me:
                # Right aligned
                x = img_width - w - padding
                color = self.bubble_user_bg
                text_color = self.bubble_user_fg
                
                # Draw bubble
                self.draw_bubble(draw, x, y, w, h, color, is_right=True)
                
                # Draw Text
                text_y = y + bubble_padding
                for line in item['wrapped_lines']:
                    draw.text((x + bubble_padding, text_y), line, font=font, fill=text_color)
                    text_y += int(self.font_size * 1.3)
                    
            else:
                # Left aligned with Avatar
                avatar_x = padding
                bubble_x = padding + avatar_size + 10
                
                # Draw Avatar
                draw.ellipse([avatar_x, y, avatar_x + avatar_size, y + avatar_size], fill=self.avatar_colors[0])
                initial = msg['sender'][0]
                draw.text((avatar_x + 15, y + 10), initial, font=font_bold, fill=(255,255,255))
                
                # Draw Name
                draw.text((bubble_x, y - 20), msg['sender'], font=font_small, fill=(100, 100, 100))
                
                # Draw Bubble
                color = self.bubble_other_bg
                text_color = self.bubble_other_fg
                self.draw_bubble(draw, bubble_x, y, w, h, color, is_right=False)
                
                # Draw Text
                text_y = y + bubble_padding
                for line in item['wrapped_lines']:
                    draw.text((bubble_x + bubble_padding, text_y), line, font=font, fill=text_color)
                    text_y += int(self.font_size * 1.3)
        
        return image


