# ComfyUI Subtitle Nodes

一个用于 ComfyUI 的字幕添加插件，支持自动排版、多种字体和文字效果。

## 功能特点

- 支持中英文字幕
- 自动换行和排版
- 支持顶部/底部/居中对齐
- 支持字体下载和管理
- 支持文字特效（阴影、描边）
- 支持透明度调整
- 支持自定义行间距和边距

## 安装方法

1. 进入 ComfyUI 的 `custom_nodes` 目录
2. 克隆本仓库：
   ```bash
   git clone https://github.com/cenzijing/comfyui-subtitle.git
   ```
3. 安装依赖：
   ```bash
   pip install requests
   ```

## 使用方法

### 1. 添加字幕
1. 在节点列表中找到 "Add Subtitle" 节点
2. 连接图像输入
3. 输入要添加的文字
4. 选择字体和位置
5. 调整其他参数（大小、颜色、特效等）

### 2. 下载字体
1. 使用 "Download Font" 节点
2. 从列表中选择想要的字体
3. 选择字体样式
4. 运行节点下载字体

## 参数说明

### Add Subtitle 节点
- `text`: 要显示的文字
- `position`: 位置（顶部/底部/中间）
- `font_size`: 字体大小
- `margin`: 边距
- `max_width_ratio`: 最大宽度比例
- `line_spacing`: 行间距
- `color`: 文字颜色
- `enable_shadow`: 是否启用阴影
- `enable_outline`: 是否启用描边
- `opacity`: 透明度

### Download Font 节点
- `font_name`: 字体名称
- `font_style`: 字体样式

## 示例

[这里后续可以添加使用示例的截图]

## 许可证

MIT License