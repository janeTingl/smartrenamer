# 网盘存储快速参考

SmartRenamer v0.9.0 网盘存储集成功能快速参考。

## 快速开始

### 1. 本地存储

```python
from smartrenamer.storage import LocalStorageAdapter

适配器 = LocalStorageAdapter()
适配器.连接()

# 列出文件
文件列表 = 适配器.列出文件("/path/to/dir")
for 文件 in 文件列表:
    print(文件.名称, 文件.大小)
```

### 2. 115 网盘

```python
from smartrenamer.storage import Storage115Adapter

适配器 = Storage115Adapter({
    "cookie": "你的115cookie"
})

if 适配器.连接():
    # 列出根目录
    文件列表 = 适配器.列出文件("0")
    
    # 下载文件
    本地路径 = 适配器.读取文件("文件ID")
    
    # 重命名
    适配器.重命名文件("文件ID", "新文件名.mkv")
```

### 3. 123 网盘

```python
from smartrenamer.storage import Storage123Adapter

适配器 = Storage123Adapter({
    "access_token": "你的token",
    "refresh_token": "刷新token"
})

if 适配器.连接():
    # 列出根目录
    文件列表 = 适配器.列出文件("0")
    
    # 上传文件
    适配器.写入文件("/local/file.mkv", "目录ID")
```

### 4. 使用管理器

```python
from smartrenamer.storage import get_storage_manager

管理器 = get_storage_manager()

# 切换到 115
管理器.切换适配器("115", {"cookie": "..."})

# 获取当前适配器
适配器 = 管理器.获取当前适配器()

# 使用适配器
文件列表 = 适配器.列出文件("0")
```

## 常用操作

### 列出文件

```python
# 基本列出
文件列表 = 适配器.列出文件(路径)

# 递归列出
文件列表 = 适配器.列出文件(路径, 递归=True)

# 使用过滤器
def 只要视频(文件):
    return 文件.名称.endswith(('.mkv', '.mp4'))

文件列表 = 适配器.列出文件(路径, 过滤器=只要视频)

# 流式扫描
for 批次 in 适配器.列出文件迭代(路径, 批次大小=100):
    for 文件 in 批次:
        print(文件.名称)
```

### 文件操作

```python
# 获取文件信息
信息 = 适配器.获取文件信息(路径)

# 检查文件存在
if 适配器.文件存在(路径):
    print("文件存在")

# 下载文件
本地路径 = 适配器.读取文件(路径, 本地路径="/tmp/file")

# 上传文件
适配器.写入文件("/local/file", "目标路径")

# 重命名
适配器.重命名文件(源路径, 目标路径)

# 删除
适配器.删除文件(路径)

# 创建目录
适配器.创建目录(路径)
```

### 存储空间

```python
空间 = 适配器.获取存储空间信息()
print(f"总空间: {空间['总空间'] / (1024**3):.2f} GB")
print(f"已用: {空间['已用空间'] / (1024**3):.2f} GB")
print(f"剩余: {空间['剩余空间'] / (1024**3):.2f} GB")
print(f"使用率: {空间['使用率']:.2f}%")
```

## 配置管理

### 保存配置

```python
from smartrenamer.core import Config

config = Config.load()
config.storage_type = "115"
config.storage_configs["115"]["cookie"] = "你的cookie"
config.save()
```

### 读取配置

```python
from smartrenamer.core import get_config

config = get_config()
存储类型 = config.storage_type
网盘配置 = config.storage_configs["115"]
```

## 获取认证信息

### 115 网盘 Cookie

1. 登录 https://115.com
2. 打开开发者工具（F12）
3. Network 标签页
4. 找到任意请求到 webapi.115.com 的请求
5. 复制 Cookie 请求头

### 123 网盘 Token

1. 登录 https://www.123pan.com
2. 打开开发者工具（F12）
3. Network 标签页
4. 找到任意请求到 www.123pan.com/api 的请求
5. 复制 Authorization 请求头的 Bearer token

## API 参考

### StorageAdapter 接口

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `连接()` | 连接到存储 | bool |
| `断开连接()` | 断开连接 | None |
| `列出文件(路径, 递归, 过滤器)` | 列出文件 | List[StorageFile] |
| `列出文件迭代(路径, 递归, 过滤器, 批次大小)` | 流式列出 | Iterator[List[StorageFile]] |
| `获取文件信息(路径)` | 获取文件详情 | Optional[StorageFile] |
| `读取文件(路径, 本地路径)` | 读取文件 | Optional[Path] |
| `写入文件(本地路径, 目标路径)` | 写入文件 | bool |
| `删除文件(路径)` | 删除文件 | bool |
| `重命名文件(源路径, 目标路径)` | 重命名 | bool |
| `创建目录(路径)` | 创建目录 | bool |
| `文件存在(路径)` | 检查存在 | bool |
| `获取存储空间信息()` | 存储空间 | Dict[str, Any] |
| `获取类型()` | 存储类型 | StorageType |

### StorageFile 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `路径` | str | 文件路径 |
| `名称` | str | 文件名 |
| `大小` | int | 文件大小（字节）|
| `是否目录` | bool | 是否为目录 |
| `修改时间` | datetime | 修改时间 |
| `文件ID` | Optional[str] | 网盘文件 ID |
| `父目录ID` | Optional[str] | 父目录 ID |
| `哈希值` | Optional[str] | 文件哈希 |
| `缩略图URL` | Optional[str] | 缩略图 |
| `下载URL` | Optional[str] | 下载链接 |
| `扩展属性` | Optional[Dict] | 扩展属性 |

## 常见问题

### Q: Cookie/Token 过期怎么办？

**A**: 115 Cookie 需要重新获取；123 Token 会自动刷新，如果 refresh token 也过期则需重新获取。

### Q: 如何提高扫描速度？

**A**: 使用流式扫描（`列出文件迭代`）和文件过滤器，减少内存占用和 API 调用。

### Q: 支持哪些网盘？

**A**: 当前支持本地、115 网盘、123 网盘。更多网盘支持正在开发中。

### Q: 如何切换存储？

**A**: 使用 `StorageManager.切换适配器()` 方法。

### Q: 文件列表会缓存吗？

**A**: 是的，网盘文件列表会缓存 5 分钟。要强制刷新，删除缓存或等待过期。

## 更多信息

- 完整指南：[CLOUD_STORAGE_GUIDE.md](CLOUD_STORAGE_GUIDE.md)
- 实现报告：[CLOUD_STORAGE_IMPLEMENTATION_REPORT.md](CLOUD_STORAGE_IMPLEMENTATION_REPORT.md)
- 示例代码：[examples/storage_example.py](examples/storage_example.py)
- 测试代码：[tests/test_storage_adapters.py](tests/test_storage_adapters.py)

## 许可证

MIT License - SmartRenamer Project
