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

### 当前版本 (v0.7.0)

- ✅ 完整的项目架构
- ✅ 核心数据模型（MediaFile, RenameRule）
- ✅ 配置管理系统
- ✅ 文件信息提取工具
- ✅ TMDB API 客户端封装
- ✅ 单元测试框架（125个测试，80%覆盖率）
- ✅ **媒体库扫描模块** (v0.2.0)
  - 🔍 递归目录扫描
  - 🎬 自动识别电影和电视剧
  - 💾 缓存机制
  - 🔄 增量更新
  - 🔎 快速搜索查询
- ✅ **文件名智能解析** (v0.3.0)
  - 📝 识别常见命名格式
  - 🎯 提取标题、年份、分辨率等信息
  - 📺 支持电视剧季集识别
  - 🌐 中英双语接口
- ✅ **增强 TMDB 客户端** (v0.3.0)
  - 💾 智能缓存系统
  - 🔄 API 重试机制
  - 📅 年份过滤支持
  - 📊 剧集详情获取
- ✅ **智能匹配引擎** (v0.3.0)
  - 🎯 多条件匹配算法
  - 📈 相似度计算
  - 🤖 自动确认高相似度匹配
  - 📋 多结果支持
- ✅ **Jinja2 高级重命名引擎** (v0.4.0)
  - 🎨 灵活的模板系统
  - 🛠️ 7个自定义过滤器
  - 📋 7个预定义模板
  - 👁️ 预览模式
  - 📦 批量重命名
  - ↩️ 撤销机制
  - 🔄 文件冲突处理
  - 📝 规则管理和持久化
- ✅ **扫描与内存优化** (v0.7.0 新增)
  - ⚡ 并行扫描引擎（多线程）
  - 🌊 流式批量处理
  - 💾 增量缓存系统
  - 📊 实时进度显示
  - 🚀 性能提升 30%+
  - 💨 内存优化 25%+

### 计划功能

- 🔄 多语言支持

## 技术栈

- **Python**: 3.8+
- **GUI 框架**: PySide6
- **API 客户端**: tmdbv3api
- **模板引擎**: Jinja2
- **图像处理**: Pillow
- **测试框架**: pytest

## 安装说明

SmartRenamer 提供多种安装方式，选择最适合您的方式：

### 方式 1: 下载可执行文件（推荐）⭐

最简单的方式是直接下载对应平台的可执行文件，无需安装 Python 环境。

#### Windows

从 [GitHub Releases](https://github.com/smartrenamer/smartrenamer/releases) 下载：
- `SmartRenamer-Windows-Setup.exe` - 安装程序（推荐）
- `SmartRenamer-Windows-Portable.zip` - 便携版

**安装程序使用**:
1. 双击运行 `SmartRenamer-Windows-Setup.exe`
2. 按照向导完成安装
3. 从开始菜单或桌面快捷方式启动

**便携版使用**:
1. 解压 ZIP 文件
2. 双击 `SmartRenamer.exe` 运行

#### macOS

从 [GitHub Releases](https://github.com/smartrenamer/smartrenamer/releases) 下载：
- `SmartRenamer-macOS.dmg` - DMG 镜像（支持 Intel 和 Apple Silicon）

**使用方法**:
1. 下载并打开 `.dmg` 文件
2. 将 SmartRenamer 拖到 Applications 文件夹
3. 首次运行可能需要在"系统偏好设置 > 安全性与隐私"中允许

#### Linux

从 [GitHub Releases](https://github.com/smartrenamer/smartrenamer/releases) 下载：
- `SmartRenamer-Linux-x86_64.AppImage` - AppImage 便携版

**使用方法**:
```bash
# 1. 下载 AppImage
wget https://github.com/smartrenamer/smartrenamer/releases/latest/download/SmartRenamer-Linux-x86_64.AppImage

# 2. 添加执行权限
chmod +x SmartRenamer-Linux-x86_64.AppImage

# 3. 运行
./SmartRenamer-Linux-x86_64.AppImage
```

### 方式 2: Docker（跨平台）🐳

使用 Docker 是最简单的跨平台方式，无需手动配置环境：

```bash
# 快速启动（自动配置）
./docker-quickstart.sh

# 或使用 Docker Compose
docker-compose up

# 或使用 Make
make gui
```

详细说明请参考 [Docker 使用指南](DOCKER_USAGE.md)

### 方式 3: Python 源码安装（开发者）

适合开发者或需要自定义的高级用户。

#### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

#### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/smartrenamer/smartrenamer.git
cd smartrenamer
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

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

#### 文件名解析示例

```python
from smartrenamer.core import FileNameParser

# 创建解析器
parser = FileNameParser()

# 解析电影文件名
result = parser.parse("The.Matrix.1999.1080p.BluRay.x264.mkv")
print(f"标题: {result['title']}")      # The Matrix
print(f"年份: {result['year']}")       # 1999
print(f"分辨率: {result['resolution']}")  # 1080P

# 解析电视剧文件名
result = parser.parse("Breaking.Bad.S01E01.1080p.mkv")
print(f"标题: {result['title']}")      # Breaking Bad
print(f"季集: S{result['season']:02d}E{result['episode']:02d}")  # S01E01
```

#### TMDB 匹配示例

```python
from smartrenamer.core import Matcher
from smartrenamer.api import EnhancedTMDBClient

# 创建客户端和匹配器
client = EnhancedTMDBClient("your_api_key", 启用缓存=True)
matcher = Matcher(client)

# 匹配文件
matches = matcher.match_file("The.Matrix.1999.1080p.mkv", max_results=3)

# 查看匹配结果
for i, match in enumerate(matches, 1):
    print(f"{i}. {match.tmdb数据['title']}")
    print(f"   相似度: {match.相似度:.2%}")
```

#### 完整工作流示例

```python
from smartrenamer.core import FileNameParser, Matcher, MediaFile
from smartrenamer.api import EnhancedTMDBClient
from pathlib import Path

# 初始化组件
parser = FileNameParser()
client = EnhancedTMDBClient("your_api_key")
matcher = Matcher(client, parser)

# 创建媒体文件
file_path = Path("/media/movies/Inception.2010.1080p.mkv")
media_file = MediaFile(
    path=file_path,
    original_name=file_path.name,
    extension=file_path.suffix
)

# 匹配 TMDB 数据
matches = matcher.match_media_file(media_file, max_results=1)

if matches:
    # 应用最佳匹配
    best_match = matches[0]
    updated_file = matcher.apply_match_to_media_file(media_file, best_match)
    
    print(f"标题: {updated_file.title}")
    print(f"年份: {updated_file.year}")
    print(f"TMDB ID: {updated_file.tmdb_id}")
```

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

### 打包和构建

如果需要构建可执行文件，请参考 [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)。

**快速构建**:
```bash
# 安装打包依赖
pip install pyinstaller

# 执行构建
pyinstaller --clean --noconfirm smartrenamer.spec

# macOS 平台测试
./test_macos_build.sh  # 仅限 macOS
```

**注意事项**:
- macOS 上已修复 PyInstaller 的 Qt 框架符号链接问题
- 详见 `docs/MACOS_PYINSTALLER_FIX.md`

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
