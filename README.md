# SmartRenamer - 智能媒体文件重命名工具

SmartRenamer 是一个基于 TMDB API 的智能媒体文件重命名工具，支持电影和电视剧文件的自动识别和规范化命名。

## 项目概述

SmartRenamer 可以帮助您：

- 🎬 自动识别电影和电视剧文件
- 🔍 通过 TMDB API 获取准确的媒体信息
- ✨ 根据可自定义的规则重命名文件
- 🖥️ 提供友好的图形界面（开发中）
- 📊 批量处理大量媒体文件

## 功能特性

### 当前版本 (v0.2.0)

- ✅ 完整的项目架构
- ✅ 核心数据模型（MediaFile, RenameRule）
- ✅ 配置管理系统
- ✅ 文件信息提取工具
- ✅ TMDB API 客户端封装
- ✅ 单元测试框架
- ✅ **媒体库扫描模块** (新增)
  - 🔍 递归目录扫描
  - 🎬 自动识别电影和电视剧
  - 💾 缓存机制
  - 🔄 增量更新
  - 🔎 快速搜索查询

### 计划功能

- 🔄 图形用户界面（PySide6）
- 🔄 批量重命名功能
- 🔄 预览和撤销功能
- 🔄 多语言支持
- 🔄 自定义重命名模板

## 技术栈

- **Python**: 3.8+
- **GUI 框架**: PySide6
- **API 客户端**: tmdbv3api
- **模板引擎**: Jinja2
- **图像处理**: Pillow
- **测试框架**: pytest

## 安装说明

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd smartrenamer
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/macOS
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **开发模式安装**

```bash
pip install -e .
```

## 快速开始

### 1. 配置 TMDB API

SmartRenamer 需要 TMDB API Key 才能正常工作。

1. 访问 [TMDB 官网](https://www.themoviedb.org/) 注册账号
2. 在账号设置中申请 API Key
3. 创建配置文件 `~/.smartrenamer/config.json`：

```json
{
  "tmdb_api_key": "your_api_key_here",
  "tmdb_language": "zh-CN"
}
```

### 2. 运行应用

```bash
python src/smartrenamer/main.py
```

或者如果已安装：

```bash
smartrenamer
```

### 3. 使用示例

#### 基本重命名示例

```python
from smartrenamer import MediaFile, MediaType, Config

# 创建配置
config = Config(tmdb_api_key="your_api_key")

# 创建媒体文件对象
media_file = MediaFile(
    path="/path/to/movie.mkv",
    original_name="movie.mkv",
    extension=".mkv",
    media_type=MediaType.MOVIE,
    title="黑客帝国",
    year=1999,
    resolution="1080p",
)

# 应用重命名规则
from smartrenamer.core import DEFAULT_MOVIE_RULE
new_name = DEFAULT_MOVIE_RULE.apply(media_file)
print(f"新文件名: {new_name}")
```

#### 媒体库扫描示例

```python
from pathlib import Path
from smartrenamer import FileScanner, MediaLibrary

# 创建媒体库并添加扫描源
library = MediaLibrary(enable_cache=True)
library.add_scan_source(Path("/path/to/movies"))
library.add_scan_source(Path("/path/to/tv_shows"))

# 扫描媒体库
scanner = FileScanner()
total = library.scan(scanner)
print(f"找到 {total} 个媒体文件")

# 查询电影
movies = library.get_movies()
for movie in movies:
    print(f"{movie.title} ({movie.year})")

# 搜索
results = library.search_by_title("Matrix")
```

更多示例请查看 [MEDIA_LIBRARY_GUIDE.md](MEDIA_LIBRARY_GUIDE.md) 和 `examples/` 目录。

## 项目结构

```
smartrenamer/
├── src/
│   └── smartrenamer/
│       ├── __init__.py          # 主包初始化
│       ├── main.py              # 程序入口
│       ├── core/                # 核心业务逻辑
│       │   ├── __init__.py
│       │   ├── models.py        # 数据模型
│       │   └── config.py        # 配置管理
│       ├── api/                 # API 集成
│       │   ├── __init__.py
│       │   └── tmdb_client.py   # TMDB 客户端
│       ├── ui/                  # 用户界面
│       │   └── __init__.py
│       └── utils/               # 工具函数
│           ├── __init__.py
│           └── file_utils.py    # 文件工具
├── tests/                       # 单元测试
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_config.py
│   └── test_file_utils.py
├── requirements.txt             # 项目依赖
├── pyproject.toml              # 项目配置
├── setup.py                    # 安装脚本
├── .gitignore                  # Git 忽略规则
└── README.md                   # 项目说明
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 生成覆盖率报告
pytest --cov=smartrenamer --cov-report=html
```

### 代码风格

项目遵循 PEP 8 代码规范，所有注释和文档使用简体中文。

### 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m '添加某个特性'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 常见问题

### Q: 如何获取 TMDB API Key？

A: 访问 [TMDB 官网](https://www.themoviedb.org/)，注册账号后在账号设置的 API 部分申请。

### Q: 支持哪些视频格式？

A: 默认支持 .mkv, .mp4, .avi, .mov, .wmv, .flv, .m4v, .ts 等常见格式。

### Q: 如何自定义重命名规则？

A: 可以创建自定义的 `RenameRule` 对象，使用 Jinja2 模板语法定义命名格式。

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请提交 Issue。

---

**注意**: 当前版本为开发预览版，部分功能尚未完成。
