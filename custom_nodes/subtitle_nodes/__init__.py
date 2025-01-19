from .add_subtitle_node import AddSubtitleNode
from .download_font_node import DownloadFontNode

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("请安装requests库以启用字体下载功能: pip install requests")
    REQUESTS_AVAILABLE = False

NODE_CLASS_MAPPINGS = {
    "AddSubtitleNode": AddSubtitleNode,
    "DownloadFontNode": DownloadFontNode if REQUESTS_AVAILABLE else None
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AddSubtitleNode": "Add Subtitle",
    "DownloadFontNode": "Download Font"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 