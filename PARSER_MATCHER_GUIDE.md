# 文件名解析与 TMDB 匹配模块使用指南

## 概述

SmartRenamer v0.3.0 新增了智能文件名解析和 TMDB 数据库匹配功能，能够自动识别媒体文件信息并与 TMDB 数据库进行精确匹配。

## 核心组件

### 1. 文件名解析器 (FileNameParser)

智能解析各种命名格式的媒体文件名，提取标题、年份、分辨率等信息。

#### 支持的格式

- **电影格式**：`Movie.Title.Year.Resolution.Source.Codec.ext`
- **电视剧格式**：`Show.Title.S01E01.Resolution.Source.ext`
- **中文格式**：`电影名.年份.分辨率.来源.ext`
- **多种分隔符**：`.`, `_`, `-`, 空格

#### 可提取的信息

- 媒体类型（电影/电视剧）
- 标题
- 年份
- 季数和集数（电视剧）
- 分辨率（720p, 1080p, 2160p/4K）
- 来源（BluRay, WEB-DL, HDTV 等）
- 编码格式（H264, H265 等）

#### 使用示例

```python
from smartrenamer.core import FileNameParser

# 创建解析器
parser = FileNameParser()

# 解析电影文件名
result = parser.parse("The.Matrix.1999.1080p.BluRay.x264.mkv")
print(f"标题: {result['title']}")      # The Matrix
print(f"年份: {result['year']}")       # 1999
print(f"分辨率: {result['resolution']}")  # 1080P
print(f"类型: {result['media_type']}")   # MediaType.MOVIE

# 解析电视剧文件名
result = parser.parse("Breaking.Bad.S01E01.Pilot.1080p.WEB-DL.mkv")
print(f"标题: {result['title']}")      # Breaking Bad
print(f"季数: {result['season']}")     # 1
print(f"集数: {result['episode']}")    # 1
print(f"类型: {result['media_type']}")   # MediaType.TV_SHOW
```

#### 中文接口

```python
from smartrenamer.core import 文件名解析器

解析器 = 文件名解析器()
结果 = 解析器.解析("让子弹飞.2010.1080p.BluRay.mkv")

print(f"标题: {结果['标题']}")    # 让子弹飞
print(f"年份: {结果['年份']}")    # 2010
```

### 2. 增强 TMDB 客户端 (EnhancedTMDBClient)

在原有 TMDB 客户端基础上增加了缓存、重试机制和更丰富的功能。

#### 主要特性

- **智能缓存**：自动缓存搜索结果，减少 API 调用
- **重试机制**：网络错误时自动重试，提高稳定性
- **年份过滤**：支持按年份过滤搜索结果
- **剧集信息**：支持获取电视剧剧集详细信息

#### 使用示例

```python
from smartrenamer.api import EnhancedTMDBClient

# 创建客户端
client = EnhancedTMDBClient(
    api_key="your_tmdb_api_key",
    启用缓存=True,
    最大重试次数=3
)

# 搜索电影
movies = client.search_movie("The Matrix", year=1999)
for movie in movies:
    print(f"{movie['title']} ({movie['release_date'][:4]})")

# 获取电影详情
details = client.get_movie_details(603)
print(f"标题: {details['title']}")
print(f"简介: {details['overview']}")

# 搜索电视剧
tv_shows = client.search_tv("Breaking Bad", year=2008)
for show in tv_shows:
    print(f"{show['name']} ({show['first_air_date'][:4]})")

# 获取剧集信息
episode = client.get_episode_details(
    tv_id=1396,
    season=1,
    episode=1
)
print(f"剧集标题: {episode['name']}")

# 清空缓存
client.clear_cache()
```

#### 缓存管理

缓存文件默认存储在 `~/.smartrenamer/cache/tmdb/` 目录下，默认过期时间为 7 天。

### 3. 智能匹配器 (Matcher)

将本地文件与 TMDB 数据库进行智能匹配，使用多条件匹配算法。

#### 匹配算法

- **标题相似度**：使用 SequenceMatcher 计算字符串相似度
- **年份匹配**：考虑年份误差（电影 ±1 年，电视剧 ±5 年）
- **综合评分**：电影（标题 70% + 年份 30%），电视剧（标题 75% + 年份 25%）
- **智能过滤**：自动过滤相似度低于阈值的结果

#### 使用示例

```python
from smartrenamer.core import Matcher, MediaFile
from smartrenamer.api import EnhancedTMDBClient
from pathlib import Path

# 创建组件
client = EnhancedTMDBClient("your_api_key")
matcher = Matcher(client)

# 方法 1: 直接匹配文件名
matches = matcher.match_file(
    "The.Matrix.1999.1080p.BluRay.mkv",
    max_results=5,
    auto_confirm=False  # 是否自动确认高相似度结果
)

# 查看匹配结果
for i, match in enumerate(matches, 1):
    print(f"{i}. {match.tmdb数据['title']}")
    print(f"   相似度: {match.相似度:.2%}")
    print(f"   原因: {match.匹配原因}")

# 方法 2: 匹配 MediaFile 对象
media_file = MediaFile(
    path=Path("/media/movies/Inception.2010.1080p.mkv"),
    original_name="Inception.2010.1080p.mkv",
    extension=".mkv"
)

matches = matcher.match_media_file(media_file, max_results=3)

if matches:
    # 应用最佳匹配到媒体文件
    best_match = matches[0]
    updated_file = matcher.apply_match_to_media_file(media_file, best_match)
    
    print(f"标题: {updated_file.title}")
    print(f"年份: {updated_file.year}")
    print(f"TMDB ID: {updated_file.tmdb_id}")
```

#### 匹配结果 (MatchResult)

```python
# 匹配结果包含
match.tmdb数据      # TMDB 原始数据
match.相似度        # 匹配相似度 (0-1)
match.媒体类型      # MediaType.MOVIE 或 MediaType.TV_SHOW
match.匹配原因      # 匹配原因说明

# 转换为字典
match_dict = match.to_dict()
```

### 4. 完整工作流程

```python
from smartrenamer.core import FileNameParser, Matcher, MediaFile
from smartrenamer.api import EnhancedTMDBClient
from pathlib import Path

# 1. 初始化组件
parser = FileNameParser()
client = EnhancedTMDBClient("your_api_key", 启用缓存=True)
matcher = Matcher(client, parser)

# 2. 创建媒体文件对象
file_path = Path("/media/movies/The.Matrix.1999.1080p.mkv")
media_file = MediaFile(
    path=file_path,
    original_name=file_path.name,
    extension=file_path.suffix
)

# 3. 解析文件名（可选，matcher 会自动解析）
parsed = parser.parse(file_path.name)
print(f"解析标题: {parsed['title']}")
print(f"解析年份: {parsed['year']}")

# 4. 匹配 TMDB 数据
matches = matcher.match_media_file(media_file, max_results=3)

if not matches:
    print("未找到匹配结果")
else:
    print(f"找到 {len(matches)} 个匹配:")
    
    for i, match in enumerate(matches, 1):
        tmdb_data = match.tmdb数据
        print(f"\n{i}. {tmdb_data.get('title', 'Unknown')}")
        print(f"   相似度: {match.相似度:.2%}")
        print(f"   TMDB ID: {tmdb_data.get('id')}")
        print(f"   发行日期: {tmdb_data.get('release_date', 'N/A')}")
        print(f"   原因: {match.匹配原因}")
    
    # 5. 应用最佳匹配
    best_match = matches[0]
    if best_match.相似度 >= 0.85:
        updated_file = matcher.apply_match_to_media_file(media_file, best_match)
        
        print(f"\n已应用匹配:")
        print(f"标题: {updated_file.title}")
        print(f"年份: {updated_file.year}")
        print(f"TMDB ID: {updated_file.tmdb_id}")
        
        # 6. 生成新文件名（使用重命名规则）
        from smartrenamer.core import DEFAULT_MOVIE_RULE
        new_name = DEFAULT_MOVIE_RULE.apply(updated_file)
        print(f"新文件名: {new_name}")
```

## 配置选项

### 解析器配置

```python
# 自定义解析规则
parser = FileNameParser(custom_rules=[
    r'Custom\.Pattern\.(\d{4})',  # 自定义正则表达式
])
```

### TMDB 客户端配置

```python
from pathlib import Path

client = EnhancedTMDBClient(
    api_key="your_api_key",
    language="zh-CN",              # 语言设置
    缓存目录=Path("~/my_cache"),     # 自定义缓存目录
    启用缓存=True,                   # 是否启用缓存
    最大重试次数=3,                  # API 失败重试次数
    重试延迟=1.0                     # 重试延迟（秒）
)
```

### 匹配器配置

```python
# 自定义相似度阈值
matcher.最小相似度 = 0.7   # 最低匹配相似度
matcher.高相似度 = 0.9     # 高相似度阈值（用于自动确认）
```

## 性能优化

### 缓存策略

1. **搜索结果缓存**：相同的搜索查询会自动从缓存读取
2. **详情缓存**：电影和电视剧详情会缓存 7 天
3. **手动清理**：`client.clear_cache()` 清空所有缓存

### 批量处理

```python
# 批量匹配多个文件
files = [
    "Movie1.2020.1080p.mkv",
    "Movie2.2021.720p.mkv",
    "Show.S01E01.1080p.mkv",
]

for filename in files:
    matches = matcher.match_file(filename, max_results=1, auto_confirm=True)
    if matches:
        print(f"{filename} -> {matches[0].tmdb数据['title']}")
```

## 错误处理

```python
try:
    matches = matcher.match_file("Unknown.Movie.mkv")
    if not matches:
        print("未找到匹配结果")
except Exception as e:
    print(f"匹配失败: {e}")
```

## 最佳实践

1. **启用缓存**：减少 API 调用次数
2. **设置重试**：提高网络不稳定时的成功率
3. **验证相似度**：相似度 < 0.85 时建议人工确认
4. **批量处理**：使用 `auto_confirm=True` 提高效率
5. **定期清理**：定期清理过期缓存释放空间

## 示例脚本

项目包含完整的示例脚本：

```bash
python examples/parser_and_matcher_example.py
```

设置 `TMDB_API_KEY` 环境变量以运行 TMDB 匹配示例：

```bash
export TMDB_API_KEY="your_api_key"
python examples/parser_and_matcher_example.py
```

## 测试

运行模块测试：

```bash
# 测试解析器
pytest tests/test_parser.py -v

# 测试 TMDB 客户端
pytest tests/test_tmdb_enhanced.py -v

# 测试匹配器
pytest tests/test_matcher.py -v

# 运行所有测试并查看覆盖率
pytest --cov=smartrenamer tests/ -v
```

## 技术细节

### 解析器算法

- 使用正则表达式匹配常见模式
- 支持多种季集格式（S01E01, 1x01, 第1季第1集）
- 智能清理标签和发布组信息
- 标准化质量和编码格式

### 匹配算法

- 使用 `difflib.SequenceMatcher` 计算字符串相似度
- 综合考虑标题和年份的匹配度
- 电影和电视剧使用不同的权重配置
- 自动过滤低相似度结果

### 缓存机制

- 使用 JSON 文件存储缓存
- 每个缓存项包含创建时间和数据
- 自动检查并删除过期缓存
- 使用 MD5 哈希避免文件名冲突

## 更新日志

**v0.3.0** (当前版本)
- ✅ 新增文件名智能解析器
- ✅ 新增增强版 TMDB 客户端
- ✅ 新增智能匹配引擎
- ✅ 支持缓存和重试机制
- ✅ 完整中文化支持
- ✅ 50+ 单元测试，覆盖率 80%+

## 下一步计划

- GUI 集成
- 批量重命名功能
- 更多匹配策略
- 支持更多视频平台
