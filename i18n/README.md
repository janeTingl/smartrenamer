# SmartRenamer 国际化

本目录包含 SmartRenamer 的多语言翻译文件。

## 支持的语言

- **简体中文 (zh_CN)** - 默认语言
- **英文 (en_US)** - 英文翻译

## 文件格式

目前使用 JSON 格式存储翻译文本，便于维护和扩展。

每个语言的翻译文件命名规则：`{语言代码}.json`

## 使用方法

语言在应用启动时根据配置自动加载。您可以在设置对话框的"外观"选项卡中切换界面语言。

**注意**：语言切换需要重启应用才能完全生效。

## 添加新语言

1. 复制 `zh_CN.json` 作为模板
2. 重命名为新的语言代码（如 `ja_JP.json` 代表日语）
3. 翻译 JSON 文件中的所有文本
4. 在 `src/smartrenamer/ui/i18n_manager.py` 中添加新语言到 `AVAILABLE_LANGUAGES`

## 翻译文件结构

```json
{
  "app_name": "应用名称",
  "app_description": "应用描述",
  
  "menu": {
    "file": "文件菜单项",
    ...
  },
  
  "tabs": {
    "library": "标签页名称",
    ...
  },
  
  "toolbar": {
    "open_directory": "工具栏按钮",
    ...
  },
  
  "settings": {
    "title": "设置",
    ...
  },
  
  "dialogs": {
    "confirm": "对话框文本",
    ...
  },
  
  "messages": {
    "config_warning": "提示消息",
    ...
  }
}
```

## 技术细节

国际化管理由 `src/smartrenamer/ui/i18n_manager.py` 模块负责。

当前实现：
- 基于 JSON 的简单翻译
- 支持运行时切换（重启后生效）
- 自动检测系统语言

未来计划：
- 使用 Qt 官方的 `.ts/.qm` 文件格式
- 支持热切换（无需重启）
- 更多语言支持

## 贡献翻译

欢迎贡献新的语言翻译！请提交 Pull Request。

翻译指南：
1. 保持界面文本简洁
2. 使用本地化的日期和数字格式
3. 注意快捷键的提示文本
4. 测试所有界面元素的翻译效果
