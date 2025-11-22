# SmartRenamer 项目架构文档

## 项目概述

SmartRenamer 是一个智能媒体文件重命名工具，基于 TMDB API 进行电影和电视剧文件的识别与重命名。

## 技术栈

- **语言**: Python 3.8+
- **GUI框架**: PySide6 (Qt for Python)
- **API客户端**: tmdbv3api
- **模板引擎**: Jinja2
- **图像处理**: Pillow
- **测试框架**: pytest

## 项目结构

```
smartrenamer/
├── src/smartrenamer/          # 主应用包
│   ├── __init__.py           # 包初始化，导出核心类
│   ├── main.py               # 应用程序入口点
│   │
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── models.py         # 数据模型 (MediaFile, RenameRule)
│   │   └── config.py         # 配置管理 (Config)
│   │
│   ├── api/                  # 外部API集成
│   │   ├── __init__.py
│   │   └── tmdb_client.py    # TMDB API客户端
│   │
│   ├── ui/                   # 用户界面 (PySide6)
│   │   └── __init__.py       # [待开发]
│   │
│   └── utils/                # 工具函数
│       ├── __init__.py
│       └── file_utils.py     # 文件处理工具
│
├── tests/                    # 单元测试
│   ├── test_models.py        # 数据模型测试
│   ├── test_config.py        # 配置管理测试
│   └── test_file_utils.py    # 工具函数测试
│
├── examples/                 # 使用示例
│   └── basic_usage.py        # 基本功能演示
│
├── requirements.txt          # 项目依赖
├── pyproject.toml           # 项目配置 (PEP 518)
├── setup.py                 # 安装脚本 (向后兼容)
├── .gitignore               # Git忽略规则
├── LICENSE                  # MIT许可证
└── README.md                # 项目说明文档
```

## 核心组件

### 1. 数据模型 (core/models.py)

#### MediaFile
表示一个媒体文件及其元数据：
- 文件基本信息（路径、大小、扩展名）
- 媒体类型（电影/电视剧）
- TMDB 元数据（标题、年份、ID等）
- 视频信息（分辨率、来源、编码）
- 重命名状态

#### MediaType
媒体类型枚举：
- `MOVIE`: 电影
- `TV_SHOW`: 电视剧
- `UNKNOWN`: 未知

#### RenameRule
重命名规则类：
- 使用 Jinja2 模板定义命名格式
- 支持自定义分隔符和选项
- 预定义默认规则（电影、电视剧）

### 2. 配置管理 (core/config.py)

#### Config
应用配置类，管理：
- TMDB API 设置
- 重命名选项
- 文件过滤规则
- UI 设置
- 高级选项

配置文件位置：`~/.smartrenamer/config.json`

### 3. API集成 (api/tmdb_client.py)

#### TMDBClient
TMDB API 客户端封装：
- 搜索电影和电视剧
- 获取详细信息
- 支持中文查询

### 4. 工具函数 (utils/file_utils.py)

提供文件处理相关的辅助功能：
- `is_supported_file()`: 检查文件格式
- `sanitize_filename()`: 清理文件名
- `format_file_size()`: 格式化文件大小
- `extract_info_from_filename()`: 从文件名提取信息

## 设计模式

### 数据类 (Dataclass)
使用 Python 的 `@dataclass` 装饰器定义数据模型，简化代码并提供自动生成的方法。

### 单例模式
配置管理使用全局单例模式，通过 `get_config()` 获取配置实例。

### 模板方法模式
`RenameRule.apply()` 方法使用 Jinja2 模板引擎，允许灵活的命名规则定义。

## 开发规范

### 代码风格
- 遵循 PEP 8 规范
- 所有注释和文档使用简体中文
- 类和函数都有完整的文档字符串

### 命名约定
- 类名：大驼峰 (PascalCase)
- 函数/变量：小写下划线 (snake_case)
- 常量：大写下划线 (UPPER_SNAKE_CASE)
- 私有方法：前缀单下划线 (_method)

### 测试规范
- 使用 pytest 框架
- 测试文件命名：`test_*.py`
- 测试类命名：`Test*`
- 测试函数命名：`test_*`
- 目标覆盖率：>80%

## 依赖管理

### 核心依赖
- `requests>=2.31.0`: HTTP 请求库
- `tmdbv3api>=1.9.0`: TMDB API 客户端
- `PySide6>=6.6.0`: Qt 图形界面框架
- `Jinja2>=3.1.2`: 模板引擎
- `Pillow>=10.1.0`: 图像处理库

### 开发依赖
- `pytest>=7.4.3`: 测试框架
- `pytest-cov>=4.1.0`: 测试覆盖率

## 安装方式

### 开发安装
```bash
pip install -e .
```

### 生产安装
```bash
pip install -r requirements.txt
python setup.py install
```

## 测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试
```bash
pytest tests/test_models.py
```

### 生成覆盖率报告
```bash
pytest --cov=smartrenamer --cov-report=html
```

## 未来规划

### 即将实现的功能
1. **GUI界面** (ui/)
   - 主窗口设计
   - 文件列表视图
   - 预览面板
   - 配置对话框

2. **批量处理**
   - 多文件同时处理
   - 进度显示
   - 错误处理

3. **高级功能**
   - 自定义模板编辑器
   - 历史记录和撤销
   - 文件移动功能
   - 日志系统

### 技术改进
- 异步 API 请求
- 本地缓存优化
- 插件系统
- 国际化支持

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交 Pull Request

## 版本历史

### v0.1.0 (当前版本)
- ✅ 项目初始化
- ✅ 核心数据模型
- ✅ 配置管理系统
- ✅ 文件工具函数
- ✅ TMDB API 集成
- ✅ 单元测试框架
- ✅ 完整文档

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
