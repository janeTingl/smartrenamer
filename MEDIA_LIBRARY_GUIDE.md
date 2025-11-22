# 媒体库扫描模块使用指南

## 概述

SmartRenamer 的媒体库扫描模块提供了强大的文件扫描和管理功能，支持：

- 🔍 递归目录扫描
- 🎬 自动识别电影和电视剧
- 📊 智能文件过滤
- 💾 缓存机制
- 🔎 快速搜索查询

## 核心组件

### 1. FileScanner - 文件扫描器

`FileScanner` 负责递归扫描目录并提取媒体文件信息。

#### 特性

- 支持常见视频格式（.mkv, .mp4, .avi, .mov 等）
- 智能排除无关目录（Sample, Subs, Extras 等）
- 可配置的文件大小过滤
- 可限制扫描深度
- 进度回调支持

#### 使用示例

```python
from pathlib import Path
from smartrenamer import FileScanner

# 创建扫描器
scanner = FileScanner(
    supported_extensions=[".mkv", ".mp4", ".avi"],  # 支持的格式
    min_file_size=10 * 1024 * 1024,  # 最小 10 MB
    max_depth=5  # 最大深度 5 层
)

# 扫描目录
media_files = scanner.scan(Path("/path/to/media"))

# 查看结果
for mf in media_files:
    print(f"{mf.title} - {mf.media_type.value}")

# 获取统计信息
stats = scanner.get_statistics()
print(f"扫描了 {stats['扫描文件总数']} 个文件")
print(f"找到 {stats['找到媒体文件数']} 个媒体文件")
```

#### 进度回调

```python
def progress_callback(current_file, scanned, found):
    print(f"正在处理: {current_file}")
    print(f"已扫描: {scanned}, 已找到: {found}")

media_files = scanner.scan(
    Path("/path/to/media"),
    progress_callback=progress_callback
)
```

### 2. MediaLibrary - 媒体库管理器

`MediaLibrary` 提供完整的媒体库管理功能，包括扫描、缓存、查询等。

#### 特性

- 多扫描源支持
- 内存和文件缓存
- 增量更新机制
- 快速搜索查询
- 自动索引构建

#### 使用示例

```python
from smartrenamer import MediaLibrary, FileScanner

# 创建媒体库
library = MediaLibrary(enable_cache=True)

# 添加扫描源
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

# 查询电视剧
tv_shows = library.get_tv_shows()
for show in tv_shows:
    print(f"{show.title} - S{show.season_number:02d}E{show.episode_number:02d}")

# 搜索
results = library.search_by_title("Matrix")
for result in results:
    print(f"{result.title} - {result.path}")
```

#### 缓存管理

```python
# 保存缓存
library.save_cache()

# 加载缓存
library = MediaLibrary(enable_cache=True)
if library.load_cache():
    print("缓存加载成功")
else:
    print("需要重新扫描")

# 清除缓存
library.clear_cache()
```

#### 增量更新

```python
# 执行增量更新（检测新增和删除的文件）
result = library.update(scanner)
print(f"新增: {result['added']} 个文件")
print(f"删除: {result['removed']} 个文件")
```

#### 统计信息

```python
stats = library.get_statistics()
print(f"总文件数: {stats['总文件数']}")
print(f"电影数: {stats['电影数']}")
print(f"电视剧数: {stats['电视剧数']}")
print(f"扫描源数: {stats['扫描源数']}")
```

### 3. 配置集成

媒体库扫描功能已集成到 `Config` 配置系统中。

```python
from smartrenamer import Config

# 创建配置
config = Config()

# 设置扫描源
config.scan_sources = [
    "/path/to/movies",
    "/path/to/tv_shows"
]

# 设置排除目录
config.exclude_dirs = [
    "Sample", "Samples",
    "Subs", "Subtitles",
    "Extras"
]

# 设置最大扫描深度
config.max_scan_depth = 5

# 保存配置
config.save()
```

## 文件信息提取

`FileScanner` 自动从文件名中提取以下信息：

### 电影信息

- **标题**: 自动清理年份、分辨率等标签
- **年份**: 识别 1900-2099 的年份
- **分辨率**: 4K, 2160p, 1080p, 720p, 480p
- **来源**: BluRay, WEB-DL, HDTV, DVDRip
- **编码**: H.265, H.264, x264, x265

示例文件名：
```
The.Matrix.1999.1080p.BluRay.x264.mkv
```

提取结果：
- 标题: "The Matrix"
- 年份: 1999
- 分辨率: "1080P"
- 来源: "BluRay"
- 编码: "x264"
- 媒体类型: MOVIE

### 电视剧信息

除了电影信息外，还包括：
- **季数**: S01, S02, ...
- **集数**: E01, E02, ...

示例文件名：
```
Breaking.Bad.S01E01.Pilot.1080p.WEB-DL.x264.mkv
```

提取结果：
- 标题: "Breaking Bad"
- 季数: 1
- 集数: 1
- 分辨率: "1080P"
- 来源: "WEB-DL"
- 编码: "x264"
- 媒体类型: TV_SHOW

## 性能优化

### 缓存机制

媒体库扫描结果会自动缓存到 JSON 文件，避免重复扫描：

```python
# 首次扫描（较慢）
library = MediaLibrary(enable_cache=True)
library.add_scan_source(Path("/large/media/folder"))
library.scan(scanner)  # 自动保存缓存

# 后续加载（很快）
library = MediaLibrary(enable_cache=True)
library.load_cache()  # 从缓存加载
```

### 增量更新

使用增量更新而不是完全重新扫描：

```python
# 只检测变化的文件
result = library.update(scanner)
```

### 扫描优化

```python
# 限制扫描深度
scanner = FileScanner(max_depth=3)

# 提高最小文件大小阈值
scanner = FileScanner(min_file_size=50 * 1024 * 1024)  # 50 MB

# 减少支持的格式
scanner = FileScanner(supported_extensions=[".mkv", ".mp4"])
```

## 错误处理

模块具有完善的错误处理机制：

```python
try:
    media_files = scanner.scan(Path("/path/to/media"))
except FileNotFoundError:
    print("目录不存在")
except NotADirectoryError:
    print("路径不是目录")
except PermissionError:
    print("没有访问权限")
```

## 日志记录

模块使用 Python logging 系统记录详细信息：

```python
import logging

# 配置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 扫描时会输出详细日志
scanner = FileScanner()
scanner.scan(Path("/path/to/media"))
```

## 最佳实践

1. **使用缓存**: 对于大型媒体库，始终启用缓存
2. **增量更新**: 定期使用 `update()` 而不是 `scan()`
3. **合理过滤**: 设置适当的 `min_file_size` 避免扫描小文件
4. **进度反馈**: 对大型目录使用进度回调提供用户反馈
5. **配置持久化**: 将扫描源保存到配置文件
6. **错误处理**: 适当处理扫描过程中的异常

## 完整示例

查看 `examples/scan_library_example.py` 获取完整的使用示例。

## API 参考

### FileScanner

#### 初始化参数
- `supported_extensions`: 支持的文件扩展名列表
- `exclude_dirs`: 排除的目录名称列表
- `min_file_size`: 最小文件大小（字节）
- `max_depth`: 最大扫描深度

#### 方法
- `scan(directory, progress_callback)`: 扫描目录
- `get_statistics()`: 获取扫描统计信息

### MediaLibrary

#### 初始化参数
- `cache_dir`: 缓存目录路径
- `enable_cache`: 是否启用缓存

#### 方法
- `add_scan_source(directory)`: 添加扫描源
- `remove_scan_source(directory)`: 移除扫描源
- `scan(scanner, progress_callback)`: 扫描所有源
- `refresh(scanner, progress_callback)`: 刷新媒体库
- `update(scanner, progress_callback)`: 增量更新
- `search_by_title(title)`: 按标题搜索
- `get_by_type(media_type)`: 按类型获取
- `get_movies()`: 获取所有电影
- `get_tv_shows()`: 获取所有电视剧
- `get_all()`: 获取所有媒体文件
- `get_statistics()`: 获取统计信息
- `save_cache()`: 保存缓存
- `load_cache()`: 加载缓存
- `clear()`: 清空媒体库
- `clear_cache()`: 清除缓存文件

## 常见问题

### Q: 扫描速度慢怎么办？

A: 
1. 启用缓存功能
2. 增加 `min_file_size` 过滤小文件
3. 使用 `max_depth` 限制扫描深度
4. 使用增量更新而不是完全扫描

### Q: 如何排除特定目录？

A: 
```python
scanner = FileScanner(
    exclude_dirs=["Sample", "Extras", "Deleted"]
)
```

### Q: 缓存保存在哪里？

A: 默认保存在 `~/.smartrenamer/cache/media_library.json`

### Q: 如何识别更多视频格式？

A:
```python
scanner = FileScanner(
    supported_extensions=[".mkv", ".mp4", ".avi", ".mov", ".webm"]
)
```

### Q: 扫描时如何显示进度？

A: 使用进度回调函数：
```python
def show_progress(file, scanned, found):
    print(f"进度: {scanned} 个文件, 找到: {found}")

scanner.scan(path, progress_callback=show_progress)
```

## 更新日志

### v0.2.0 (当前版本)
- ✅ 新增 FileScanner 文件扫描器
- ✅ 新增 MediaLibrary 媒体库管理器
- ✅ 支持电影和电视剧自动识别
- ✅ 实现缓存机制
- ✅ 实现增量更新
- ✅ 集成到配置系统
- ✅ 完整的单元测试（25 个测试用例）
- ✅ 测试覆盖率 75%+

---

**注意**: 本模块完全使用简体中文编写，包括代码注释、变量名和文档。
