# 网盘存储集成使用指南

SmartRenamer v0.9.0 引入了网盘存储集成功能，支持直接在 115 网盘和 123 网盘中进行文件识别和重命名操作。

## 目录

- [功能概述](#功能概述)
- [支持的网盘](#支持的网盘)
- [存储适配器架构](#存储适配器架构)
- [配置网盘存储](#配置网盘存储)
- [115 网盘配置](#115-网盘配置)
- [123 网盘配置](#123-网盘配置)
- [使用网盘存储](#使用网盘存储)
- [API 使用示例](#api-使用示例)
- [限制和注意事项](#限制和注意事项)
- [常见问题](#常见问题)

## 功能概述

网盘存储集成功能提供了统一的存储抽象层，允许 SmartRenamer 无缝地在本地文件系统和多种网盘存储之间切换。主要功能包括：

- **统一接口**：通过 `StorageAdapter` 抽象基类提供一致的 API
- **多存储支持**：支持本地、115 网盘、123 网盘
- **缓存机制**：自动缓存文件列表和下载的文件，提高性能
- **流式处理**：支持大目录的流式扫描
- **配置管理**：集成到 Config 系统，持久化存储配置

## 支持的网盘

### 本地文件系统 (Local)
- 默认存储类型
- 直接访问本地文件
- 无需额外配置

### 115 网盘
- 支持文件列表、下载、上传、重命名、删除
- 需要提供 Cookie 进行认证
- 支持大文件和秒传
- 提供文件哈希和缩略图

### 123 网盘
- 支持文件列表、下载、上传、重命名、删除
- 使用 OAuth 2.0 token 认证
- 支持分片上传
- 自动刷新过期 token

## 存储适配器架构

### 核心组件

```
smartrenamer/storage/
├── __init__.py          # 模块导出
├── base.py              # StorageAdapter 抽象基类和 StorageFile 数据类
├── local.py             # 本地文件系统适配器
├── storage_115.py       # 115 网盘适配器
├── storage_123.py       # 123 网盘适配器
└── manager.py           # 存储管理器（管理多个适配器实例）
```

### StorageFile 数据类

统一表示本地和网盘文件：

```python
@dataclass
class StorageFile:
    路径: str                    # 文件路径（本地路径或网盘 ID）
    名称: str                    # 文件名
    大小: int                    # 文件大小（字节）
    是否目录: bool               # 是否为目录
    修改时间: datetime           # 最后修改时间
    文件ID: Optional[str]        # 网盘文件 ID
    父目录ID: Optional[str]      # 父目录 ID
    哈希值: Optional[str]        # 文件哈希
    缩略图URL: Optional[str]     # 缩略图 URL
    下载URL: Optional[str]       # 下载 URL
    扩展属性: Optional[Dict]     # 其他扩展属性
```

### StorageAdapter 接口

所有存储适配器都实现以下接口：

- `连接()` / `connect()` - 连接到存储
- `断开连接()` / `disconnect()` - 断开连接
- `列出文件()` / `list_files()` - 列出目录文件
- `列出文件迭代()` / `list_files_iter()` - 流式列出文件
- `获取文件信息()` / `get_file_info()` - 获取文件详情
- `读取文件()` / `read_file()` - 读取（下载）文件
- `写入文件()` / `write_file()` - 写入（上传）文件
- `删除文件()` / `delete_file()` - 删除文件
- `重命名文件()` / `rename_file()` - 重命名文件
- `创建目录()` / `create_directory()` - 创建目录
- `文件存在()` / `file_exists()` - 检查文件存在
- `获取存储空间信息()` / `get_storage_info()` - 获取空间使用情况

## 配置网盘存储

### 配置文件结构

网盘配置保存在 `~/.smartrenamer/config.json` 中：

```json
{
  "storage_type": "local",
  "storage_configs": {
    "local": {},
    "115": {
      "cookie": "你的115网盘cookie",
      "user_id": "用户ID",
      "缓存目录": "/path/to/cache"
    },
    "123": {
      "access_token": "你的访问令牌",
      "refresh_token": "刷新令牌",
      "缓存目录": "/path/to/cache"
    }
  }
}
```

### 通过 UI 配置

1. 打开 SmartRenamer
2. 点击菜单 **设置** → **偏好设置**（或按 `Ctrl+,`）
3. 选择 **存储配置** 选项卡
4. 选择存储类型：本地 / 115 / 123
5. 填写相应的认证信息
6. 点击 **测试连接** 验证配置
7. 点击 **保存** 应用配置

## 115 网盘配置

### 获取 Cookie

1. 使用浏览器登录 115 网盘（https://115.com）
2. 打开浏览器开发者工具（F12）
3. 切换到 **网络（Network）** 选项卡
4. 刷新页面或执行任意操作
5. 在请求列表中找到任意发送到 `webapi.115.com` 的请求
6. 查看 **请求头（Request Headers）**
7. 复制 **Cookie** 字段的完整值

Cookie 示例：
```
UID=123456_xxx; CID=xxx; SEID=xxx; ...
```

### 配置示例

```python
from smartrenamer.storage import Storage115Adapter

# 创建 115 适配器
适配器 = Storage115Adapter({
    "cookie": "你的完整cookie字符串",
    "user_id": "",  # 可选，连接时会自动获取
    "缓存目录": "/home/user/.smartrenamer/cache/115",
    "代理": {  # 可选
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080"
    }
})

# 连接
if 适配器.连接():
    print("115 网盘连接成功")
```

### 注意事项

- Cookie 具有时效性，过期后需要重新获取
- 请妥善保管 Cookie，不要泄露给他人
- 建议使用应用专用账号，避免主账号风险
- 部分操作可能受到 115 API 限流限制

## 123 网盘配置

### 获取 Access Token

123 网盘使用 OAuth 2.0 认证，获取 token 的方法：

**方法一：通过浏览器抓包**

1. 使用浏览器登录 123 网盘（https://www.123pan.com）
2. 打开浏览器开发者工具（F12）
3. 切换到 **网络（Network）** 选项卡
4. 刷新页面
5. 找到发送到 `www.123pan.com/api` 的请求
6. 查看 **请求头（Request Headers）**
7. 复制 **Authorization** 字段的 Bearer token

Token 示例：
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**方法二：使用官方 SDK**（如果可用）

参考 123 网盘官方文档获取 OAuth 授权。

### 配置示例

```python
from smartrenamer.storage import Storage123Adapter

# 创建 123 适配器
适配器 = Storage123Adapter({
    "access_token": "你的访问令牌",
    "refresh_token": "你的刷新令牌",
    "缓存目录": "/home/user/.smartrenamer/cache/123",
    "代理": {  # 可选
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080"
    }
})

# 连接
if 适配器.连接():
    print("123 网盘连接成功")
```

### 注意事项

- Access token 过期后会自动使用 refresh token 刷新
- 如果 refresh token 也过期，需要重新获取
- 建议定期备份 token 配置
- 大文件上传使用分片上传机制

## 使用网盘存储

### 在 UI 中使用

1. **选择存储类型**
   - 在媒体库面板顶部的工具栏中
   - 点击存储类型下拉菜单
   - 选择：本地 / 115 网盘 / 123 网盘

2. **浏览网盘文件**
   - 左侧文件树显示网盘目录结构
   - 双击文件夹展开查看子文件
   - 文件图标会显示网盘标识

3. **扫描网盘目录**
   - 选择要扫描的网盘目录
   - 点击 **扫描** 按钮
   - 等待扫描完成（网盘扫描可能较慢）

4. **识别和重命名**
   - 扫描完成后，文件列表显示在右侧
   - 选择文件进行 TMDB 匹配
   - 预览重命名结果
   - 点击 **批量重命名** 执行

5. **查看网盘状态**
   - 状态栏显示当前存储类型
   - 显示网盘连接状态（已连接/未连接）
   - 显示存储空间使用情况

### 快捷键

- `Ctrl+Shift+S` - 打开存储切换对话框
- `Alt+1` - 切换到本地存储
- `Alt+2` - 切换到 115 网盘
- `Alt+3` - 切换到 123 网盘

## API 使用示例

### 基本使用

```python
from smartrenamer.storage import StorageManager

# 创建存储管理器
管理器 = StorageManager()

# 切换到 115 网盘
if 管理器.切换适配器("115", {
    "cookie": "你的cookie"
}):
    # 获取当前适配器
    适配器 = 管理器.获取当前适配器()
    
    # 列出根目录文件
    文件列表 = 适配器.列出文件("0")  # "0" 是根目录 ID
    
    for 文件 in 文件列表:
        print(f"{文件.名称} - {文件.大小} 字节")
```

### 使用过滤器

```python
# 只列出视频文件
def 是视频文件(文件):
    视频扩展名 = [".mkv", ".mp4", ".avi", ".mov"]
    return any(文件.名称.endswith(ext) for ext in 视频扩展名)

文件列表 = 适配器.列出文件("0", 过滤器=是视频文件)
```

### 递归扫描

```python
# 递归列出所有文件
文件列表 = 适配器.列出文件("0", 递归=True)
```

### 流式扫描（推荐用于大目录）

```python
# 批量处理文件
for 批次文件 in 适配器.列出文件迭代("0", 递归=True, 批次大小=100):
    # 处理每批文件
    for 文件 in 批次文件:
        print(f"处理: {文件.名称}")
```

### 下载文件

```python
from pathlib import Path

# 下载到指定位置
本地路径 = 适配器.读取文件(
    "文件ID或路径",
    本地路径=Path("/tmp/downloaded_file.mkv")
)

if 本地路径:
    print(f"文件已下载到: {本地路径}")
```

### 上传文件

```python
from pathlib import Path

# 上传文件到网盘
成功 = 适配器.写入文件(
    Path("/local/file.mkv"),
    "目标目录ID"
)

if 成功:
    print("文件上传成功")
```

### 重命名文件

```python
# 重命名网盘文件
成功 = 适配器.重命名文件(
    "源文件ID",
    "新文件名.mkv"
)
```

### 获取存储空间

```python
空间信息 = 适配器.获取存储空间信息()
print(f"总空间: {空间信息['总空间'] / (1024**3):.2f} GB")
print(f"已用: {空间信息['已用空间'] / (1024**3):.2f} GB")
print(f"剩余: {空间信息['剩余空间'] / (1024**3):.2f} GB")
print(f"使用率: {空间信息['使用率']:.2f}%")
```

### 集成到扫描流程

```python
from smartrenamer.core import FileScanner
from smartrenamer.storage import get_storage_manager

# 获取存储管理器
管理器 = get_storage_manager()

# 切换到网盘存储
管理器.切换适配器("115", {"cookie": "..."})
适配器 = 管理器.获取当前适配器()

# 创建扫描器（如果需要，可以自定义扫描逻辑）
扫描器 = FileScanner()

# 使用适配器获取文件列表
文件列表 = 适配器.列出文件("0", 递归=True, 过滤器=lambda f: not f.是否目录)

# 转换为 MediaFile 对象并处理
# ...
```

## 限制和注意事项

### 通用限制

1. **网络依赖**：网盘操作需要稳定的网络连接
2. **速度限制**：网盘操作速度受网络带宽和 API 限流影响
3. **缓存机制**：文件列表会缓存 5 分钟，强制刷新需清除缓存
4. **并发限制**：避免同时执行大量网盘操作，可能触发 API 限流

### 115 网盘特定限制

1. **Cookie 有效期**：Cookie 可能在一段时间后失效，需重新获取
2. **API 限流**：频繁操作可能被限流，建议控制请求频率
3. **文件大小限制**：超大文件可能需要特殊处理
4. **路径映射**：115 使用文件 ID，路径到 ID 的映射需要维护

### 123 网盘特定限制

1. **Token 刷新**：Access token 过期后会自动刷新，但 refresh token 过期需手动更新
2. **分片上传**：大文件会自动分片上传，可能需要较长时间
3. **并发上传**：同时上传多个大文件可能导致失败
4. **文件命名**：某些特殊字符可能不被支持

### 安全建议

1. **配置加密**：敏感信息（Cookie、Token）应加密存储
2. **专用账号**：建议使用专用账号，避免主账号风险
3. **定期备份**：定期备份配置和重命名历史
4. **权限控制**：配置文件应设置适当的文件权限（如 chmod 600）

## 常见问题

### Q: 如何获取 115 网盘的 Cookie？

A: 参考 [115 网盘配置](#115-网盘配置) 章节，使用浏览器开发者工具抓取。

### Q: 123 网盘 token 过期怎么办？

A: 如果 refresh token 有效，会自动刷新 access token。如果都过期，需要重新获取。

### Q: 网盘扫描很慢怎么办？

A: 网盘扫描受网络速度影响，建议：
- 使用流式扫描（`列出文件迭代`）
- 启用缓存机制
- 避免频繁全盘扫描
- 使用过滤器减少文件数量

### Q: 重命名失败怎么办？

A: 检查以下几点：
- 网盘连接状态
- 目标文件名是否包含非法字符
- 是否有足够的权限
- 查看日志文件了解详细错误

### Q: 如何清除缓存？

A: 删除缓存目录：`~/.smartrenamer/cache/115` 或 `~/.smartrenamer/cache/123`

### Q: 可以同时使用多个网盘吗？

A: 可以配置多个网盘，但同一时间只能激活一个存储源。切换存储源会自动切换适配器。

### Q: 本地文件和网盘文件可以互相操作吗？

A: 不建议跨存储操作。如需迁移，建议先下载到本地，处理后再上传。

### Q: 网盘文件的元数据会保留吗？

A: 重命名会保留文件的修改时间、大小等基本元数据，但具体取决于网盘 API 的支持。

## 开发和扩展

### 添加新的网盘支持

如需支持其他网盘（如阿里云盘、百度网盘等），可以：

1. 继承 `StorageAdapter` 基类
2. 实现所有抽象方法
3. 在 `StorageManager` 中注册新的适配器类型
4. 更新配置模型
5. 添加单元测试
6. 更新文档

示例：

```python
from smartrenamer.storage.base import StorageAdapter, StorageFile, StorageType

class AliyunDriveAdapter(StorageAdapter):
    def 连接(self) -> bool:
        # 实现连接逻辑
        pass
    
    def 列出文件(self, 路径: str, 递归: bool = False, 过滤器=None):
        # 实现文件列表逻辑
        pass
    
    # 实现其他方法...
```

### 贡献代码

欢迎贡献网盘适配器实现！请遵循：

1. 代码风格符合 PEP 8
2. 提供完整的单元测试
3. 添加中文注释和文档
4. 提交 Pull Request

## 更新日志

### v0.9.0 (2024-01-XX)
- ✅ 初始版本
- ✅ 支持本地、115、123 网盘
- ✅ 统一存储适配器接口
- ✅ UI 集成和配置管理
- ✅ 缓存和流式扫描
- ✅ 完整的单元测试

## 许可证

本功能遵循 SmartRenamer 项目的 MIT 许可证。

## 联系和支持

如有问题或建议，请：

- 提交 Issue：https://github.com/your-repo/smartrenamer/issues
- 查看文档：https://smartrenamer.readthedocs.io
- 邮件联系：support@smartrenamer.com
