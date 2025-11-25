# SmartRenamer 资源文件

## 图标文件

本目录包含 SmartRenamer 的应用图标，用于不同平台的打包：

- `icon.ico` - Windows 图标文件（.ico 格式，多分辨率）
- `icon.icns` - macOS 图标文件（.icns 格式，多分辨率）
- `icon.png` - Linux 图标文件（.png 格式，建议 256x256 或 512x512）

## 创建图标

### 从 PNG 创建其他格式

如果你有一个高分辨率的 PNG 图标，可以使用以下工具转换：

#### 创建 Windows ICO

**使用 ImageMagick**:
```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

**使用在线工具**:
- https://convertio.co/png-ico/
- https://icoconvert.com/

#### 创建 macOS ICNS

**使用 iconutil (macOS)**:
```bash
# 1. 创建 iconset 目录
mkdir icon.iconset

# 2. 生成不同尺寸的图标
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png

# 3. 生成 icns 文件
iconutil -c icns icon.iconset -o icon.icns

# 4. 清理
rm -rf icon.iconset
```

**使用 png2icns (Linux/macOS)**:
```bash
png2icns icon.icns icon.png
```

## 图标设计建议

### 尺寸
- 源图像：至少 1024x1024 像素
- PNG：256x256 或 512x512
- 保持正方形比例

### 风格
- 简洁明了
- 易于识别
- 适合浅色和深色背景
- 避免过多细节（小尺寸时可能看不清）

### 颜色
- 使用品牌色
- 确保在不同背景下可见
- 考虑无障碍访问（色盲友好）

## 当前图标

当前的图标已通过 `generate_icons.py` 脚本自动生成，包含 "SR" 字母（SmartRenamer 的缩写）。

**特点**:
- 蓝色圆角矩形背景（#2980b9）
- 白色大号字母 "SR"
- 透明背景（RGBA 模式）
- 多尺寸支持（16x16 到 1024x1024）

### 重新生成图标

如果需要更新图标，可以运行项目根目录的脚本：

```bash
# 生成所有平台的图标文件
python3 generate_icons.py

# 验证图标兼容性
python3 test_icon_compat.py
```

### 自定义图标

如果需要设计自定义图标，建议的主题：
- 媒体文件 + 重命名
- 电影胶片 + 编辑图标
- 文件夹 + 标签
- 智能/AI 元素

设计完成后，替换 `generate_icons.py` 中的 `create_base_icon()` 函数即可。

## 许可证

图标应该是：
- 原创设计
- 使用开源/免费图标库（注明来源）
- 购买商业授权

推荐的免费图标资源：
- https://www.flaticon.com/
- https://icons8.com/
- https://fontawesome.com/
- https://www.iconfinder.com/
