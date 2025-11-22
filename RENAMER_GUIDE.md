# SmartRenamer 重命名引擎使用指南

本指南介绍如何使用 SmartRenamer 的 Jinja2 高级重命名规则引擎。

## 目录

- [功能概述](#功能概述)
- [核心组件](#核心组件)
- [快速开始](#快速开始)
- [预定义模板](#预定义模板)
- [自定义过滤器](#自定义过滤器)
- [高级用法](#高级用法)
- [API 参考](#api-参考)

## 功能概述

重命名引擎提供以下核心功能：

1. **灵活的模板系统**：基于 Jinja2 模板引擎，支持变量替换、条件判断、循环和过滤器
2. **预定义模板库**：提供常用的电影和电视剧重命名模板
3. **自定义过滤器**：内置多个实用过滤器（填充、清理文件名、截断等）
4. **规则管理**：支持规则的添加、删除、保存和加载
5. **预览模式**：在实际重命名前预览结果
6. **批量处理**：支持批量重命名多个文件
7. **撤销机制**：记录重命名历史，支持撤销操作
8. **文件名冲突处理**：自动处理重复文件名

## 核心组件

### 1. Renamer / 重命名器

重命名执行引擎，负责实际的文件重命名操作。

```python
from smartrenamer.core import Renamer, 重命名器

# 创建重命名器（预览模式）
renamer = Renamer(预览模式=True, 创建备份=True)
# 或使用中文接口
重命名器实例 = 重命名器(预览模式=True, 创建备份=True)
```

**参数：**
- `预览模式` (bool): 是否启用预览模式，不实际执行重命名
- `创建备份` (bool): 是否记录重命名历史，用于撤销

### 2. RenameRuleManager / 重命名规则管理器

管理重命名规则，支持规则的验证、添加、删除和持久化。

```python
from smartrenamer.core import RenameRuleManager, 重命名规则管理器

# 创建规则管理器
manager = RenameRuleManager()
# 或使用中文接口
管理器 = 重命名规则管理器()
```

### 3. RenameRule

定义重命名规则的数据模型。

```python
from smartrenamer.core import RenameRule, MediaType

rule = RenameRule(
    name="我的规则",
    description="规则描述",
    template="{{ title }} ({{ year }})",
    media_type=MediaType.MOVIE,
)
```

## 快速开始

### 基本示例：重命名单个电影文件

```python
from pathlib import Path
from smartrenamer.core import (
    MediaFile,
    MediaType,
    RenameRule,
    Renamer,
)

# 1. 创建媒体文件对象
media_file = MediaFile(
    path=Path("/movies/movie.mkv"),
    original_name="movie.mkv",
    extension=".mkv",
    media_type=MediaType.MOVIE,
    title="黑客帝国",
    year=1999,
    resolution="1080p",
)

# 2. 创建重命名规则
rule = RenameRule(
    name="电影规则",
    description="标准电影命名",
    template="{{ title }} ({{ year }}) {{ resolution }}",
    media_type=MediaType.MOVIE,
)

# 3. 创建重命名器（预览模式）
renamer = Renamer(预览模式=True)

# 4. 生成新文件名
success, new_name, error = renamer.生成新文件名(media_file, rule)
if success:
    print(f"新文件名: {new_name}")
    # 输出: 新文件名: 黑客帝国 (1999) 1080p.mkv
```

### 使用预定义模板

```python
from smartrenamer.core import create_predefined_rule, 创建预定义规则

# 使用预定义的电影模板
rule = create_predefined_rule("电影-标准")

# 使用预定义的电视剧模板
tv_rule = create_predefined_rule("电视剧-带剧集名")
```

## 预定义模板

系统提供了 7 个预定义模板：

### 电影模板

#### 1. 电影-简洁
- **模板**: `{{ title|清理文件名 }} ({{ year }})`
- **示例**: `黑客帝国 (1999).mkv`
- **适用场景**: 个人收藏，简洁命名

#### 2. 电影-标准
- **模板**: `{{ title|清理文件名|replace(' ', '.') }}.{{ year }}.{{ resolution|默认值('Unknown') }}`
- **示例**: `黑客帝国.1999.1080p.mkv`
- **适用场景**: 标准化命名，包含关键信息

#### 3. 电影-完整
- **模板**: `{{ title|清理文件名|replace(' ', '.') }}.{{ year }}.{{ resolution|默认值('Unknown') }}.{{ source|默认值('') }}{% if codec %}.{{ codec }}{% endif %}`
- **示例**: `黑客帝国.1999.1080p.BluRay.H264.mkv`
- **适用场景**: 完整信息，便于筛选和管理

### 电视剧模板

#### 4. 电视剧-标准
- **模板**: `{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}`
- **示例**: `绝命毒师 S01E01.mkv`
- **适用场景**: 标准电视剧命名

#### 5. 电视剧-带剧集名
- **模板**: `{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}{% if episode_title %} {{ episode_title|清理文件名 }}{% endif %}`
- **示例**: `绝命毒师 S01E01 试播集.mkv`
- **适用场景**: 包含剧集标题，便于识别

#### 6. 电视剧-完整
- **模板**: `{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}{% if episode_title %} {{ episode_title|清理文件名 }}{% endif %} {{ resolution|默认值('Unknown') }}`
- **示例**: `绝命毒师 S01E01 试播集 1080p.mkv`
- **适用场景**: 完整信息命名

#### 7. 电视剧-分季目录
- **模板**: `{{ title|清理文件名 }}/Season {{ season|填充(2) }}/{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}`
- **示例**: `绝命毒师/Season 01/绝命毒师 S01E01.mkv`
- **适用场景**: 按季分目录整理

## 自定义过滤器

### 可用的过滤器列表

| 过滤器（中文） | 过滤器（英文） | 说明 | 示例 |
|---------------|---------------|------|------|
| `填充(width, fillchar)` | `pad(width, fillchar)` | 填充到指定宽度 | `{{ 1\|填充(2) }}` → `"01"` |
| `清理文件名` | `clean` | 清理非法文件名字符 | `{{ "file:name"\|清理文件名 }}` → `"filename"` |
| `截断(length, suffix)` | `truncate(length, suffix)` | 截断字符串 | `{{ title\|截断(10) }}` → `"很长的标题..."` |
| `大写首字母` | `capitalize` | 每个单词首字母大写 | `{{ "the matrix"\|大写首字母 }}` → `"The Matrix"` |
| `全大写` | `upper` | 转换为全大写 | `{{ title\|全大写 }}` |
| `全小写` | `lower` | 转换为全小写 | `{{ title\|全小写 }}` |
| `默认值(default)` | `default(default)` | 提供默认值 | `{{ year\|默认值(2024) }}` |

### 过滤器使用示例

```python
# 1. 填充数字（季集号）
template = "S{{ season|填充(2) }}E{{ episode|填充(2) }}"
# 输入: season=1, episode=5
# 输出: S01E05

# 2. 清理文件名
template = "{{ title|清理文件名 }}"
# 输入: title="Movie: Part 1"
# 输出: "Movie Part 1"

# 3. 截断长标题
template = "{{ title|截断(20) }}"
# 输入: title="这是一个非常非常长的电影标题"
# 输出: "这是一个非常非常长的..."

# 4. 组合使用多个过滤器
template = "{{ title|清理文件名|replace(' ', '.')|全大写 }}"
# 输入: title="The Matrix: Reloaded"
# 输出: "THE.MATRIX.RELOADED"

# 5. 条件和过滤器结合
template = "{{ title }}{% if episode_title %} - {{ episode_title|截断(30) }}{% endif %}"
```

### 可用的模板变量

| 变量 | 类型 | 说明 | 适用类型 |
|------|------|------|----------|
| `title` | str | 标题 | 电影、电视剧 |
| `original_title` | str | 原始标题 | 电影、电视剧 |
| `year` | int | 年份 | 电影、电视剧 |
| `season` | int | 季数 | 电视剧 |
| `episode` | int | 集数 | 电视剧 |
| `episode_title` | str | 剧集标题 | 电视剧 |
| `resolution` | str | 分辨率 (如 1080p) | 电影、电视剧 |
| `source` | str | 来源 (如 BluRay) | 电影、电视剧 |
| `codec` | str | 编码 (如 H264) | 电影、电视剧 |
| `separator` | str | 分隔符 | 电影、电视剧 |

## 高级用法

### 1. 批量重命名

```python
from smartrenamer.core import Renamer, create_predefined_rule

# 准备媒体文件列表
media_files = [
    # ... 多个 MediaFile 对象
]

# 创建规则
rule = create_predefined_rule("电影-标准")

# 创建重命名器（实际执行模式）
renamer = Renamer(预览模式=False, 创建备份=True)

# 批量重命名
result = renamer.批量重命名(media_files, rule)

print(f"总数: {result['总数']}")
print(f"成功: {result['成功']}")
print(f"失败: {result['失败']}")
print(f"跳过: {result['跳过']}")
```

### 2. 规则管理和持久化

```python
from pathlib import Path
from smartrenamer.core import RenameRuleManager, RenameRule, MediaType

# 创建管理器
manager = RenameRuleManager()

# 添加规则
rule1 = RenameRule(
    name="自定义规则1",
    description="我的规则",
    template="{{ title }} ({{ year }})",
    media_type=MediaType.MOVIE,
)
manager.添加规则(rule1)

# 保存到文件
rules_file = Path.home() / ".smartrenamer" / "rules.json"
manager.保存到文件(rules_file)

# 从文件加载
new_manager = RenameRuleManager()
new_manager.从文件加载(rules_file)
```

### 3. 撤销重命名

```python
from smartrenamer.core import Renamer

# 创建重命名器（启用备份）
renamer = Renamer(预览模式=False, 创建备份=True)

# 执行重命名
success, error = renamer.重命名文件(media_file, rule)

# 如果需要撤销
if success:
    # 撤销最后一次操作
    undo_success, undo_error = renamer.撤销重命名()
    if undo_success:
        print("撤销成功")
```

### 4. 处理电视剧分季目录

```python
from smartrenamer.core import MediaFile, MediaType, create_predefined_rule

# 创建电视剧文件
tv_file = MediaFile(
    path=Path("/shows/show.mkv"),
    original_name="show.mkv",
    extension=".mkv",
    media_type=MediaType.TV_SHOW,
    title="绝命毒师",
    season_number=1,
    episode_number=1,
)

# 使用分季目录模板
rule = create_predefined_rule("电视剧-分季目录")

renamer = Renamer(预览模式=False)
success, error = renamer.重命名文件(tv_file, rule)
# 结果: 绝命毒师/Season 01/绝命毒师 S01E01.mkv
```

### 5. 自定义复杂规则

```python
from smartrenamer.core import RenameRule, MediaType

# 创建复杂的自定义规则
complex_rule = RenameRule(
    name="复杂规则",
    description="根据分辨率和来源分类",
    template="""
    {%- if resolution == '2160p' -%}
        4K/
    {%- elif resolution == '1080p' -%}
        HD/
    {%- else -%}
        SD/
    {%- endif -%}
    {{ title|清理文件名 }} ({{ year }})
    {%- if source %} [{{ source }}]{% endif -%}
    """,
    media_type=MediaType.MOVIE,
)

# 使用规则
# 2160p 电影 -> 4K/电影名 (2024) [BluRay].mkv
# 1080p 电影 -> HD/电影名 (2024) [WEB-DL].mkv
# 其他     -> SD/电影名 (2024).mkv
```

### 6. 验证规则模板

```python
from smartrenamer.core import RenameRuleManager

manager = RenameRuleManager()

# 验证模板语法
templates = [
    "{{ title }} ({{ year }})",           # 有效
    "{{ title } ({{ year }})",            # 无效 - 语法错误
    "{{ title }} S{{ season|pad(2) }}E{{ episode|pad(2) }}",  # 有效
]

for template in templates:
    valid, error = manager.验证模板(template)
    if valid:
        print(f"✓ 模板有效: {template}")
    else:
        print(f"✗ 模板无效: {template}")
        print(f"  错误: {error}")
```

## API 参考

### Renamer / 重命名器

```python
class Renamer:
    def __init__(self, 预览模式: bool = True, 创建备份: bool = True)
    
    def 生成新文件名(self, 媒体文件: MediaFile, 规则: RenameRule) -> Tuple[bool, str, Optional[str]]
    def 重命名文件(self, 媒体文件: MediaFile, 规则: RenameRule) -> Tuple[bool, Optional[str]]
    def 批量重命名(self, 媒体文件列表: List[MediaFile], 规则: RenameRule) -> Dict[str, Any]
    def 撤销重命名(self, 历史索引: Optional[int] = None) -> Tuple[bool, Optional[str]]
    def 获取历史记录(self) -> List[RenameHistory]
    def 清空历史记录(self)
    def 保存历史到文件(self, 文件路径: Path) -> bool
    def 从文件加载历史(self, 文件路径: Path) -> bool
    
    # 英文别名
    generate_new_filename(...)
    rename_file(...)
    batch_rename(...)
    undo_rename(...)
    get_history(...)
    clear_history()
    save_history_to_file(...)
    load_history_from_file(...)
```

### RenameRuleManager / 重命名规则管理器

```python
class RenameRuleManager:
    def __init__(self)
    
    def 验证模板(self, 模板: str) -> Tuple[bool, Optional[str]]
    def 添加规则(self, 规则: RenameRule) -> bool
    def 移除规则(self, 规则名称: str) -> bool
    def 获取规则(self, 规则名称: str) -> Optional[RenameRule]
    def 获取所有规则(self) -> List[RenameRule]
    def 保存到文件(self, 文件路径: Path) -> bool
    def 从文件加载(self, 文件路径: Path) -> bool
    
    # 英文别名
    validate_template(...)
    add_rule(...)
    remove_rule(...)
    get_rule(...)
    get_all_rules()
    save_to_file(...)
    load_from_file(...)
```

### 工具函数

```python
def 创建预定义规则(模板名称: str) -> Optional[RenameRule]
def create_predefined_rule(template_name: str) -> Optional[RenameRule]

# 预定义模板字典
预定义模板: Dict[str, Dict[str, Any]]
PREDEFINED_TEMPLATES: Dict[str, Dict[str, Any]]
```

## 最佳实践

1. **先使用预览模式**：在实际重命名前，始终先在预览模式下测试规则
2. **启用备份**：启用 `创建备份=True` 以支持撤销操作
3. **验证模板**：使用 `验证模板()` 方法检查自定义模板的语法
4. **使用清理过滤器**：始终对用户输入的标题使用 `清理文件名` 过滤器
5. **提供默认值**：对可能为空的字段使用 `默认值()` 过滤器
6. **保存规则**：将常用的自定义规则保存到文件，便于重复使用
7. **处理冲突**：重命名器会自动处理文件名冲突，添加数字后缀

## 常见问题

### Q: 如何处理特殊字符？
A: 使用 `清理文件名` 过滤器自动移除非法字符：
```python
template = "{{ title|清理文件名 }} ({{ year }})"
```

### Q: 如何设置季集号格式？
A: 使用 `填充` 过滤器：
```python
template = "S{{ season|填充(2) }}E{{ episode|填充(2) }}"
# 输出: S01E01
```

### Q: 如何处理可能为空的字段？
A: 使用条件判断或 `默认值` 过滤器：
```python
# 方法1: 条件判断
template = "{{ title }}{% if resolution %} {{ resolution }}{% endif %}"

# 方法2: 默认值
template = "{{ title }} {{ resolution|默认值('Unknown') }}"
```

### Q: 如何创建分目录的命名规则？
A: 在模板中使用 `/` 分隔：
```python
template = "{{ title }}/Season {{ season|填充(2) }}/{{ title }} S{{ season|填充(2) }}E{{ episode|填充(2) }}"
```

## 示例代码

查看 `examples/renamer_example.py` 获取更多完整示例。

运行示例：
```bash
python examples/renamer_example.py
```

## 总结

SmartRenamer 的重命名引擎提供了强大而灵活的文件重命名功能：

- ✅ 基于 Jinja2 的模板系统
- ✅ 7 个预定义模板，涵盖常见场景
- ✅ 丰富的自定义过滤器
- ✅ 支持预览、批量处理和撤销
- ✅ 完整的中英双语接口
- ✅ 自动处理文件名冲突

通过组合使用这些功能，您可以轻松实现各种复杂的文件重命名需求。
