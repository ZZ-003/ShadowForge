import os
from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.lexers import PythonLexer, JavaLexer, JavascriptLexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
from pygments import lex

class VSCodeGenerator:
    def __init__(self, font_name="DejaVu Sans Mono", font_size=24):
        self.font_name = font_name
        self.font_size = font_size
        # VSCode Dark+ background color approximation
        self.bg_color = (30, 30, 30) 
        self.line_number_bg = (30, 30, 30)
        self.line_number_fg = (133, 133, 133)
        self.font_path = self._find_font(font_name)

    def _find_font(self, font_name):
        # Simple lookup, falling back to basic locations
        common_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None 

    def generate_code_image(self, code_snippet, language="python", secret=None, secret_placeholder="SECRET_HERE"):
        """
        Generates an image of the code snippet.
        If secret is provided, it replaces the placeholder.
        """
        
        # 1. Prepare Code
        if secret and secret_placeholder in code_snippet:
            final_code = code_snippet.replace(secret_placeholder, secret)
        else:
            final_code = code_snippet

        # 2. Syntax Highlighting using Pygments
        try:
            style = get_style_by_name('monokai')
        except:
            style = get_style_by_name('colorful')

        lexer = PythonLexer()
        if language.lower() == 'java':
            lexer = JavaLexer()
        elif language.lower() == 'javascript':
            lexer = JavascriptLexer()

        tokens = lex(final_code, lexer)
        
        # Create Image
        lines = final_code.split('\n')
        line_height = int(self.font_size * 1.5)
        
        # Load font first to measure text
        try:
            font = ImageFont.truetype(self.font_path, self.font_size) if self.font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Calculate max width required
        max_line_width = 0
        for line in lines:
            try:
                width = font.getlength(line)
            except AttributeError:
                width = font.getsize(line)[0]
            if width > max_line_width:
                max_line_width = width
                
        # Add padding (gutter + left margin + right margin)
        gutter_width = 60
        x_padding = 40 # 20 left + 20 right
        
        # Ensure minimum width of 1200, but expand if needed
        img_width = max(1200, int(max_line_width + gutter_width + x_padding))
        img_height = max(600, len(lines) * line_height + 100)
        
        image = Image.new('RGB', (img_width, img_height), self.bg_color)
        draw = ImageDraw.Draw(image)

        # Draw UI Elements (Sidebar, Line numbers)
        draw.rectangle([(0, 0), (gutter_width, img_height)], fill=self.line_number_bg)
        
        # Draw Tokens
        x_start = gutter_width + 20
        y = 20
        
        cur_x = x_start
        cur_y = y
        line_num = 1
        
        # Draw first line number
        draw.text((10, cur_y), str(line_num), font=font, fill=self.line_number_fg)
        
        for token_type, value in tokens:
            # Get color from style
            token_style = style.style_for_token(token_type)
            color_hex = token_style.get('color')
            if color_hex:
                color = f"#{color_hex}"
            else:
                color = "#d4d4d4" # Default FG
                
            # Handle newlines
            if '\n' in value:
                parts = value.split('\n')
                for i, part in enumerate(parts):
                    # Draw part
                    draw.text((cur_x, cur_y), part, font=font, fill=color)
                    try:
                        cur_x += font.getlength(part)
                    except:
                        cur_x += font.getsize(part)[0]
                    
                    if i < len(parts) - 1:
                        # Newline
                        cur_y += line_height
                        cur_x = x_start
                        line_num += 1
                        draw.text((10, cur_y), str(line_num), font=font, fill=self.line_number_fg)
            else:
                draw.text((cur_x, cur_y), value, font=font, fill=color)
                try:
                    cur_x += font.getlength(value)
                except:
                    cur_x += font.getsize(value)[0]
        
        return image


