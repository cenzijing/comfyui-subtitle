import os
import json
import requests
from urllib.parse import quote
import time

class DownloadFontNode:
    def __init__(self):
        self.fonts_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        self.available_fonts = self._get_all_fonts_list()
        
        # 确保字体目录存在
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)

    def _get_chinese_fonts(self):
        """获取中文字体列表"""
        chinese_fonts = {
            # 思源系列
            "思源黑体": {
                "name": "Source Han Sans CN",
                "url": "https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf"
            },
            "思源宋体": {
                "name": "Source Han Serif CN",
                "url": "https://raw.githubusercontent.com/adobe-fonts/source-han-serif/release/OTF/SimplifiedChinese/SourceHanSerifSC-Regular.otf"
            },
            # Noto系列
            "Noto Sans SC": {
                "name": "Noto Sans SC",
                "url": "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/Chinese-Simplified/NotoSansCJKsc-Regular.otf"
            },
            "Noto Serif SC": {
                "name": "Noto Serif SC",
                "url": "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Serif/OTF/Chinese-Simplified/NotoSerifCJKsc-Regular.otf"
            },
            # 开源中文字体
            "霞鹜文楷": {
                "name": "LXGW WenKai",
                "url": "https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/dist/LXGWWenKai-Regular.ttf"
            },
            "更纱黑体": {
                "name": "Sarasa Gothic",
                "url": "https://raw.githubusercontent.com/be5invis/Sarasa-Gothic/main/dist/sarasa-gothic-sc-regular.ttf"
            },
            "文泉驿微米黑": {
                "name": "WenQuanYi Micro Hei",
                "url": "https://raw.githubusercontent.com/googlefonts/noto-cjk/main/Sans/OTF/Chinese-Simplified/NotoSansCJKsc-Regular.otf"
            }
        }
        return chinese_fonts

    def _get_english_fonts(self):
        """获取英文字体列表"""
        english_fonts = {
            # Google Fonts 基础字体
            "Roboto": {
                "name": "Roboto",
                "url": "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf"
            },
            "Open Sans": {
                "name": "Open Sans",
                "url": "https://raw.githubusercontent.com/googlefonts/opensans/main/fonts/ttf/OpenSans-Regular.ttf"
            },
            # 等宽字体
            "Fira Code": {
                "name": "Fira Code",
                "url": "https://raw.githubusercontent.com/tonsky/FiraCode/master/distr/ttf/FiraCode-Regular.ttf"
            },
            "JetBrains Mono": {
                "name": "JetBrains Mono",
                "url": "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/fonts/ttf/JetBrainsMono-Regular.ttf"
            },
            # 装饰字体
            "Dancing Script": {
                "name": "Dancing Script",
                "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/dancingscript/DancingScript-Regular.ttf"
            }
        }
        return english_fonts

    def _get_all_fonts_list(self):
        fonts = []
        
        # 添加中文字体
        chinese_fonts = self._get_chinese_fonts()
        fonts.extend([(name, name) for name in chinese_fonts.keys()])
        
        # 添加英文字体
        english_fonts = self._get_english_fonts()
        fonts.extend([(name, name) for name in english_fonts.keys()])
        
        # 按字体名称排序
        fonts.sort(key=lambda x: x[1])
        return fonts

    @classmethod
    def INPUT_TYPES(cls):
        instance = cls()
        return {
            "required": {
                "font_name": ([font[1] for font in instance.available_fonts],),
                "font_style": (["regular", "bold", "italic", "bolditalic"],),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "download_font"
    CATEGORY = "image/subtitle"
    OUTPUT_NODE = True

    def _download_font(self, font_name, style):
        # 获取字体信息
        chinese_fonts = self._get_chinese_fonts()
        english_fonts = self._get_english_fonts()
        
        font_info = None
        if font_name in chinese_fonts:
            font_info = chinese_fonts[font_name]
        elif font_name in english_fonts:
            font_info = english_fonts[font_name]
            
        if not font_info:
            return None, "字体未找到"
            
        try:
            # 下载字体文件
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(font_info["url"], headers=headers, stream=True, timeout=30)
            
            if response.status_code != 200:
                print(f"下载失败，状态码: {response.status_code}")
                return None, f"字体文件下载失败: HTTP {response.status_code}"
            
            # 生成文件名并保存
            safe_font_name = quote(font_name.replace(' ', '_'))
            file_name = f"{safe_font_name}_{style}.ttf"
            file_path = os.path.join(self.fonts_dir, file_name)
            
            total_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            if total_size == 0:
                os.remove(file_path)
                return None, "下载的文件大小为0"
                
            print(f"字体文件已保存: {file_path} ({total_size/1024:.1f}KB)")
            return file_name, "字体下载成功"
            
        except requests.exceptions.Timeout:
            return None, "下载超时"
        except requests.exceptions.ConnectionError:
            return None, "网络连接错误"
        except Exception as e:
            return None, f"下载出错: {str(e)}"

    def download_font(self, font_name, font_style):
        file_name, message = self._download_font(font_name, font_style)
        if file_name:
            print(f"字体下载成功: {file_name}")
            return (file_name,)
        else:
            print(f"字体下载失败: {message}")
            return ("default",) 