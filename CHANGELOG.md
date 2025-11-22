# 更新日志

本文档记录 SmartRenamer 项目的所有重要更改。

## [0.3.0] - 2024-11-22

### 新增功能

#### 文件名智能解析模块

- **FileNameParser (文件名解析器)**
  - 智能识别常见命名格式
  - 支持电影格式: `Movie.Title.Year.Resolution.Source.Codec`
  - 支持电视剧格式: `Show.Title.S01E01`, `Show.Title.1x01`, `第1季第1集`
  - 支持多种分隔符: `.`, `_`, `-`, 空格
  - 自动提取标题、年份、分辨率、来源、编码
  - 自动提取季数和集数（电视剧）
  - 智能清理标签和发布组信息
  - 支持中文和英文接口
  - 可扩展的自定义解析规则

#### 增强 TMDB 客户端

- **EnhancedTMDBClient (增强TMDB客户端)**
  - 基于原 TMDBClient 的增强版本
  - 智能缓存系统（7天过期）
  - API 请求重试机制（默认3次，指数退避）
  - 年份过滤支持
  - 电影搜索和详情获取
  - 电视剧搜索和详情获取
  - 剧集详情获取（支持指定季和集）
  - 缓存管理（手动清空、自动过期）
  - 完整的错误处理和日志记录

#### 智能匹配引擎

- **Matcher (智能匹配器)**
  - 将本地文件与 TMDB 数据智能匹配
  - 多条件匹配算法（标题 + 年份）
  - 字符串相似度计算（SequenceMatcher）
  - 电影匹配：标题 70% + 年份 30%
  - 电视剧匹配：标题 75% + 年份 25%
  - 可配置的相似度阈值（最小 60%，高 85%）
  - 自动确认高相似度匹配
  - 支持多个匹配结果返回
  - 匹配结果应用到 MediaFile
  - 详细的匹配原因说明

#### 缓存管理系统

- **缓存管理器**
  - JSON 文件缓存
  - 自动过期检测
  - MD5 哈希避免文件名冲突
  - 缓存目录: `~/.smartrenamer/cache/tmdb/`
  - 支持手动清空缓存

### 测试

- 新增 16 个 FileNameParser 测试用例
- 新增 14 个 EnhancedTMDBClient 测试用例
- 新增 20 个 Matcher 测试用例
- 总测试用例数: 95 个（全部通过 ✅）
- 整体覆盖率: 80%
- parser.py 覆盖率: 94%
- matcher.py 覆盖率: 87%
- tmdb_client_enhanced.py 覆盖率: 77%

### 文档

- 新增 `PARSER_MATCHER_GUIDE.md` 完整使用指南
- 新增 `examples/parser_and_matcher_example.py` 示例代码
- 更新 `README.md` 添加新功能说明

### 改进

- 完整中文化（代码、注释、变量名、函数名）
- 提供双语接口（中文和英文）
- 完善的错误处理和日志记录
- 高质量的测试覆盖

### 技术亮点

- 使用正则表达式进行复杂模式匹配
- difflib.SequenceMatcher 实现智能相似度计算
- 指数退避重试策略
- JSON 文件缓存机制
- 综合评分算法

---

## [0.2.0] - 2024-11-22

### 新增功能

#### 媒体库扫描模块

- **FileScanner (文件扫描器)**
  - 递归扫描指定目录
  - 支持 12 种常见视频格式 (.mkv, .mp4, .avi, .mov, .wmv, .flv, .m4v, .ts, .mpg, .mpeg, .m2ts, .webm)
  - 智能过滤和排除不相关文件
  - 自动排除 Sample、Subs、Extras 等目录
  - 可配置文件大小过滤（默认 10 MB）
  - 可限制最大扫描深度
  - 支持进度回调
  - 提供扫描统计信息

- **MediaLibrary (媒体库管理器)**
  - 多扫描源管理
  - 内存缓存和 JSON 文件缓存
  - 增量更新机制（检测新增和删除的文件）
  - 快速搜索功能（按标题、类型）
  - 自动索引构建
  - 统计信息收集
  - 缓存刷新和清除功能

- **智能信息提取**
  - 从文件名自动提取标题
  - 识别年份 (1900-2099)
  - 识别分辨率 (4K, 2160p, 1080p, 720p, 480p)
  - 识别来源 (BluRay, WEB-DL, HDTV, DVDRip)
  - 识别编码 (H.265, H.264, x264, x265)
  - 识别季集信息 (S01E01)
  - 自动区分电影和电视剧

- **配置系统集成**
  - Config 类新增 `scan_sources` 配置项
  - Config 类新增 `exclude_dirs` 配置项
  - Config 类新增 `max_scan_depth` 配置项

### 测试

- 新增 11 个 FileScanner 测试用例
- 新增 14 个 MediaLibrary 测试用例
- 总测试用例数: 45 个（全部通过）
- 代码覆盖率: 75%
- scanner.py 覆盖率: 89%
- library.py 覆盖率: 83%

### 文档

- 新增 `MEDIA_LIBRARY_GUIDE.md` 完整使用指南
- 新增 `examples/scan_library_example.py` 示例代码
- 更新 `README.md` 添加媒体库扫描功能说明
- 更新 `PROJECT_STATUS.md` 记录新版本信息

### 改进

- 完善了 file_utils.py 的信息提取功能
- 优化了文件名标题提取算法
- 改进了错误处理和日志记录

---

## [0.1.0] - 2024-11-22

### 项目初始化

#### 核心功能

- **数据模型**
  - MediaFile: 媒体文件数据类
  - MediaType: 媒体类型枚举 (MOVIE, TV_SHOW, UNKNOWN)
  - RenameRule: 重命名规则类（基于 Jinja2 模板）
  - 预定义的默认规则: DEFAULT_MOVIE_RULE, DEFAULT_TV_RULE

- **配置管理**
  - Config: 应用配置类
  - 支持 TMDB API 配置
  - 支持重命名选项配置
  - 支持文件过滤配置
  - 配置持久化到 ~/.smartrenamer/config.json
  - 配置验证功能

- **API 集成**
  - TMDBClient: TMDB API 客户端封装
  - 支持电影搜索
  - 支持电视剧搜索
  - 支持详细信息获取
  - 中文语言支持

- **工具函数**
  - 文件格式检查
  - 文件名清理
  - 文件大小格式化
  - 信息提取（年份、分辨率、来源、编码、季集）

#### 项目结构

- 完整的 src 布局项目结构
- 模块化设计（core, api, ui, utils）
- 符合 PEP 8 代码规范
- 完整的中文注释和文档

#### 测试

- 20 个单元测试用例（全部通过）
- 测试覆盖率: 63%
- pytest 测试框架
- pytest-cov 覆盖率报告

#### 文档

- README.md: 完整的项目说明（中文）
- ARCHITECTURE.md: 架构设计文档（中文）
- LICENSE: MIT 许可证
- .gitignore: 完善的忽略规则

#### 开发工具

- requirements.txt: 依赖管理
- pyproject.toml: 现代 Python 项目配置
- setup.py: 安装脚本
- 命令行入口: smartrenamer

---

## 语义化版本说明

- **主版本号**: 不兼容的 API 更改
- **次版本号**: 向后兼容的功能新增
- **修订号**: 向后兼容的问题修正

---

## 贡献指南

查看更新日志时请注意：
- [新增] 表示新功能
- [改进] 表示功能改进
- [修复] 表示问题修复
- [弃用] 表示即将移除的功能
- [移除] 表示已移除的功能
- [安全] 表示安全相关的修复

---

**注**: 所有日期均使用 ISO 8601 格式 (YYYY-MM-DD)
