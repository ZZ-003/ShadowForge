import os
from PIL import Image, ImageDraw, ImageFont

class UIGenerator:
    def __init__(self, font_name="DejaVu Sans", font_size=20):
        self.font_name = font_name
        self.font_size = font_size
        self.font_path = self._find_font(font_name)
        self.font_mono_path = self._find_font("DejaVu Sans Mono")
        
    def _find_font(self, font_name):
        candidates = [
            f"/usr/share/fonts/truetype/dejavu/{font_name.replace(' ', '')}.ttf",
            f"/usr/share/fonts/truetype/dejavu/{font_name.replace(' ', '')}-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
             "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        # Fallback search
        if "Mono" in font_name:
             return "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    def draw_browser_frame(self, draw, width, height, url="https://dashboard.example.com"):
        # Browser Chrome
        header_height = 80
        draw.rectangle([0, 0, width, header_height], fill=(240, 240, 240))
        
        # Buttons
        draw.ellipse([15, 15, 35, 35], fill=(255, 95, 87)) # Red
        draw.ellipse([45, 15, 65, 35], fill=(255, 189, 46)) # Yellow
        draw.ellipse([75, 15, 95, 35], fill=(40, 201, 64)) # Green
        
        # URL Bar
        draw.rounded_rectangle([120, 10, width - 20, 40], radius=5, fill=(255, 255, 255), outline=(200, 200, 200))
        
        try:
            font = ImageFont.truetype(self.font_path, 16)
        except:
            font = ImageFont.load_default()
            
        draw.text((135, 18), url, font=font, fill=(50, 50, 50))
        
        # Separator
        draw.line([0, header_height, width, header_height], fill=(200, 200, 200))
        
        return header_height

    def generate_ui_image(self, scenario_type, content_data, secret=None, secret_placeholder="SECRET_HERE"):
        """
        scenario_type: 'dashboard', 'console', 'json_viewer'
        """
        # Determine necessary width based on content
        base_width = 1000
        
        # Load fonts first to measure
        try:
            font_ui = ImageFont.truetype(self.font_path, self.font_size)
            font_mono = ImageFont.truetype(self.font_mono_path, 18) if self.font_mono_path else font_ui
            font_header = ImageFont.truetype(self.font_path, 30)
        except:
            font_ui = ImageFont.load_default()
            font_mono = font_ui
            font_header = font_ui

        # Measure content width
        max_content_width = 0
        
        if scenario_type == 'dashboard':
            if secret:
                try:
                    w = font_mono.getlength(secret)
                except:
                    w = font_mono.getsize(secret)[0]
                # Sidebar (200) + Padding (40) + Input Padding (20) + Text width
                max_content_width = 200 + 40 + 20 + w + 100 
                
        elif scenario_type == 'json_viewer':
            json_text = content_data.get('json_text', '{}')
            if secret and secret_placeholder in json_text:
                json_text = json_text.replace(secret_placeholder, secret)
            
            lines = json_text.split('\n')
            for line in lines:
                try:
                    w = font_mono.getlength(line)
                except:
                    w = font_mono.getsize(line)[0]
                if w > max_content_width:
                    max_content_width = w
            max_content_width += 40 # Padding
            
        elif scenario_type == 'console':
            logs = content_data.get('logs', [])
            for log in logs:
                text = log
                if secret and secret_placeholder in text:
                    text = text.replace(secret_placeholder, secret)
                try:
                    w = font_mono.getlength(text)
                except:
                    w = font_mono.getsize(text)[0]
                if w > max_content_width:
                    max_content_width = w
            max_content_width += 60 # Icon + Padding

        width = max(base_width, int(max_content_width))
        height = 800
        
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        y_offset = self.draw_browser_frame(draw, width, height, url=content_data.get('url', 'http://localhost:3000'))
        
        if scenario_type == 'dashboard':
            # Sidebar
            draw.rectangle([0, y_offset, 200, height], fill=(50, 60, 80))
            draw.text((20, y_offset + 30), "Overview", font=font_ui, fill=(200, 200, 200))
            draw.text((20, y_offset + 80), "Settings", font=font_ui, fill=(255, 255, 255)) # Active
            draw.text((20, y_offset + 130), "API Keys", font=font_ui, fill=(200, 200, 200))
            
            # Content Area
            content_x = 240
            content_y = y_offset + 40
            
            draw.text((content_x, content_y), "Project Settings", font=font_header, fill=(0, 0, 0))
            content_y += 60
            
            # Form Fields
            # Use content_data to customize if available, else default
            labels = content_data.get('labels', ["Project Name", "Environment", "Secret Key"])
            values = content_data.get('values', ["My Awesome Project", "Production", secret if secret else "SECRET_HERE"])
            
            for i, label in enumerate(labels):
                if i >= len(values): break
                draw.text((content_x, content_y), label, font=font_ui, fill=(100, 100, 100))
                content_y += 30
                
                # Input Box
                val = values[i]
                if secret and secret_placeholder in val:
                    val = val.replace(secret_placeholder, secret)
                    
                try:
                    val_w = font_mono.getlength(val)
                except:
                    val_w = font_mono.getsize(val)[0]
                
                input_width = max(500, val_w + 30)
                
                draw.rounded_rectangle([content_x, content_y, content_x + input_width, content_y + 40], radius=4, outline=(200, 200, 200))
                
                # Simple logic to bold secret or make it mono
                if secret and secret in val:
                     draw.text((content_x + 10, content_y + 10), val, font=font_mono, fill=(0, 0, 0))
                else:
                     draw.text((content_x + 10, content_y + 10), val, font=font_ui, fill=(0, 0, 0))
                     
                content_y += 70

        elif scenario_type == 'json_viewer':
             # Raw JSON response style
             content_x = 20
             content_y = y_offset + 20
             
             json_text = content_data.get('json_text', '{}')
             if secret and secret_placeholder in json_text:
                 json_text = json_text.replace(secret_placeholder, secret)
                 
             draw.text((content_x, content_y), json_text, font=font_mono, fill=(0, 0, 0))

        elif scenario_type == 'console':
            # DevTools Console
            console_y = height - 300
            
            # Main page content (blurred/empty)
            draw.text((50, y_offset + 50), "Loading application...", font=font_header, fill=(200, 200, 200))
            
            # Console Panel
            draw.rectangle([0, console_y, width, height], fill=(255, 255, 255))
            draw.line([0, console_y, width, console_y], fill=(200, 200, 200))
            
            # Tabs
            draw.text((20, console_y + 10), "Console", font=font_ui, fill=(0, 0, 0))
            draw.line([20, console_y + 35, 80, console_y + 35], fill=(0, 100, 255), width=2)
            
            # Logs
            log_y = console_y + 50
            logs = content_data.get('logs', [])
            
            for log in logs:
                text = log
                if secret and secret_placeholder in text:
                    text = text.replace(secret_placeholder, secret)
                
                if "Error" in text:
                    color = (255, 0, 0)
                    icon = "❌"
                elif "Warn" in text:
                    color = (200, 150, 0)
                    icon = "⚠️"
                else:
                    color = (50, 50, 50)
                    icon = ">"
                    
                draw.text((20, log_y), f"{icon} {text}", font=font_mono, fill=color)
                log_y += 25

        return image


