# SmartRenamer 主题

本目录包含 SmartRenamer 的主题样式文件。

## 可用主题

### 亮色主题 (light.qss)
- 白色背景
- 深色文字
- 蓝色高亮
- 适合光线充足的环境

### 暗色主题 (dark.qss)
- 深色背景
- 浅色文字
- 蓝色高亮
- 适合低光环境，减少眼睛疲劳

## 使用方法

主题在应用启动时自动加载，您可以在设置对话框的"外观"选项卡中切换主题。

也可以通过菜单栏"视图 -> 主题"快速切换。

## 快捷键

- `Ctrl+Shift+L` - 切换到亮色主题
- `Ctrl+Shift+D` - 切换到暗色主题

## 自定义主题

您可以编辑现有的 `.qss` 文件来自定义主题样式。QSS（Qt Style Sheet）语法类似于 CSS。

参考文档：https://doc.qt.io/qt-6/stylesheet-reference.html

## 技术细节

主题文件使用 Qt Style Sheet (QSS) 格式，支持以下特性：

- 选择器（类、ID、属性）
- 伪状态（hover, pressed, disabled 等）
- 颜色、边框、边距、填充
- 字体样式
- 背景图片

主题管理由 `src/smartrenamer/ui/theme_manager.py` 模块负责。
