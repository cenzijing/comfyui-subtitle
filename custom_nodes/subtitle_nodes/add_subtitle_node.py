import torch
import numpy
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

class AddSubtitleNode:
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        self.available_fonts = self._get_available_fonts()
        
    def _get_available_fonts(self):
        fonts = []
        if os.path.exists(self.fonts_dir):
            for file in os.listdir(self.fonts_dir):
                if file.lower().endswith(('.ttf', '.otf')):
                    fonts.append(file)
        if not fonts:
            fonts = ["default"]
        return fonts
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"default": "在此输入文字"}),
                "font_name": ("STRING", {"default": "default"}),
                "font_size": ("INT", {"default": 40, "min": 1, "max": 500}),
                "position": (["top", "bottom", "center"],),  # 新增位置选择
                "margin": ("INT", {"default": 20, "min": 0, "max": 500}),  # 新增边距设置
                "max_width_ratio": ("FLOAT", {"default": 0.8, "min": 0.1, "max": 1.0, "step": 0.1}),  # 新增宽度比例
                "line_spacing": ("FLOAT", {"default": 1.2, "min": 1.0, "max": 3.0, "step": 0.1}),  # 新增行间距
                "color": ("STRING", {"default": "white"}),
                "enable_shadow": ("BOOLEAN", {"default": False}),
                "shadow_color": ("STRING", {"default": "black"}),
                "shadow_offset": ("INT", {"default": 2, "min": 0, "max": 20}),
                "enable_outline": ("BOOLEAN", {"default": False}),
                "outline_color": ("STRING", {"default": "black"}),
                "outline_width": ("INT", {"default": 2, "min": 1, "max": 10}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "add_subtitle"
    CATEGORY = "image/subtitle"

    def _get_font(self, font_name, font_size):
        if font_name == "default":
            return ImageFont.load_default()
        
        try:
            font_path = os.path.join(self.fonts_dir, font_name)
            return ImageFont.truetype(font_path, font_size)
        except:
            print(f"无法加载字体 {font_name}，使用默认字体")
            return ImageFont.load_default()

    def _calculate_text_size(self, draw, text, font, line_spacing):
        """计算多行文本的总宽度和高度"""
        lines = text.split('\n')
        max_width = max(draw.textlength(line, font=font) for line in lines)
        line_height = font.size * line_spacing
        total_height = line_height * len(lines)
        return max_width, total_height

    def _wrap_text(self, text, font, max_width, draw):
        """根据最大宽度对文本进行换行处理"""
        # 预处理文本，处理已有的换行符
        paragraphs = text.split('\n')
        wrapped_lines = []
        
        for paragraph in paragraphs:
            # 如果是空段落，添加空行
            if not paragraph:
                wrapped_lines.append('')
                continue
                
            # 处理单个段落
            line = ''
            for char in paragraph:
                # 测试添加新字符后的宽度
                test_line = line + char
                width = draw.textlength(test_line, font=font)
                
                if width <= max_width:
                    line = test_line
                else:
                    # 当前行已满，添加到结果中
                    if line:
                        wrapped_lines.append(line)
                    line = char
            
            # 添加最后一行
            if line:
                wrapped_lines.append(line)
        
        return '\n'.join(wrapped_lines)

    def _get_text_position(self, image_size, text_size, position, margin):
        """计算文本位置"""
        image_width, image_height = image_size
        text_width, text_height = text_size
        
        # 水平居中
        x = (image_width - text_width) / 2
        
        # 根据位置计算垂直位置
        if position == "top":
            y = margin
        elif position == "bottom":
            y = image_height - text_height - margin
        else:  # center
            y = (image_height - text_height) / 2
            
        return x, y

    def add_subtitle(self, image, text, font_name="default", font_size=40, 
                    position="bottom", margin=20, max_width_ratio=0.8, line_spacing=1.2,
                    color="white", enable_shadow=False, shadow_color="black", shadow_offset=2,
                    enable_outline=False, outline_color="black", outline_width=2,
                    opacity=1.0):
        # 将tensor转换为PIL图像
        if isinstance(image, torch.Tensor):
            image = image.cpu().numpy()
            image = (image * 255).astype('uint8')
            image = image[0]
            pil_image = Image.fromarray(image)
        else:
            pil_image = image

        # 创建RGBA模式的图像副本以支持透明度
        draw_image = pil_image.convert('RGBA')
        draw = ImageDraw.Draw(draw_image)

        # 获取字体
        font = self._get_font(font_name, font_size)

        # 计算最大文本宽度
        max_width = int(pil_image.width * max_width_ratio)
        
        # 对文本进行换行处理
        wrapped_text = self._wrap_text(text, font, max_width, draw)
        
        # 计算文本尺寸
        text_size = self._calculate_text_size(draw, wrapped_text, font, line_spacing)
        
        # 计算文本位置
        x, y = self._get_text_position(pil_image.size, text_size, position, margin)

        # 绘制带效果的文字
        self._draw_text_with_effects(
            draw, wrapped_text, (x, y), font, color,
            enable_shadow, shadow_color, shadow_offset,
            enable_outline, outline_color, outline_width,
            opacity, line_spacing
        )

        # 将图像转换回RGB模式
        draw_image = draw_image.convert('RGB')

        # 将PIL图像转换回tensor
        result = torch.from_numpy(numpy.array(draw_image).astype(numpy.float32) / 255.0)
        result = result.unsqueeze(0)

        return (result,)

    def _draw_text_with_effects(self, draw, text, position, font, color, 
                              enable_shadow, shadow_color, shadow_offset,
                              enable_outline, outline_color, outline_width,
                              opacity, line_spacing=1.2):
        x, y = position
        lines = text.split('\n')
        line_height = font.size * line_spacing
        
        def process_color(color, alpha):
            if isinstance(color, str):
                if color.startswith('#'):
                    color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                else:
                    try:
                        from PIL import ImageColor
                        color = ImageColor.getrgb(color)
                    except:
                        color = (255, 255, 255)
            return color + (int(255 * alpha),)

        for i, line in enumerate(lines):
            current_y = y + i * line_height
            
            # 处理阴影
            if enable_shadow:
                shadow_pos = (x + shadow_offset, current_y + shadow_offset)
                draw.text(shadow_pos, line, font=font, fill=process_color(shadow_color, opacity))

            # 处理描边
            if enable_outline:
                for offset_x in range(-outline_width, outline_width + 1):
                    for offset_y in range(-outline_width, outline_width + 1):
                        if offset_x == 0 and offset_y == 0:
                            continue
                        draw.text((x + offset_x, current_y + offset_y), line, 
                                font=font, fill=process_color(outline_color, opacity))

            # 绘制主要文本
            draw.text((x, current_y), line, font=font, fill=process_color(color, opacity)) 