"""
配置管理模块

负责应用配置的加载、保存和管理
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Config:
    """
    应用配置类
    
    管理 SmartRenamer 的所有配置选项
    """
    # TMDB API 配置
    tmdb_api_key: str = ""
    tmdb_language: str = "zh-CN"
    
    # 重命名选项
    auto_rename: bool = False
    create_backup: bool = True
    preview_before_rename: bool = True
    rename_worker_count: int = 4  # 并行重命名工作线程数
    rename_io_batch: bool = True  # 启用分批重命名
    
    # 文件过滤
    supported_extensions: list = None
    min_file_size: int = 10 * 1024 * 1024  # 10 MB
    
    # 媒体库扫描配置
    scan_sources: list = None  # 扫描源目录列表
    exclude_dirs: list = None  # 排除的目录名称列表
    max_scan_depth: int = None  # 最大扫描深度，None 表示无限制
    
    # UI 设置
    theme: str = "light"
    window_width: int = 1200
    window_height: int = 800
    
    # 高级选项
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24 小时
    
    # TMDB 缓存配置
    tmdb_cache_enabled: bool = True
    tmdb_cache_ttl_hours: int = 168  # 7 天
    tmdb_cache_max_entries: int = 1000  # 内存缓存最大条目数
    
    # 日志设置
    log_level: str = "INFO"
    log_to_file: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        if self.supported_extensions is None:
            self.supported_extensions = [
                ".mkv", ".mp4", ".avi", ".mov",
                ".wmv", ".flv", ".m4v", ".ts"
            ]
        if self.scan_sources is None:
            self.scan_sources = []
        if self.exclude_dirs is None:
            self.exclude_dirs = [
                "Sample", "Samples", "sample", "samples",
                "Subs", "Subtitles", "subs", "subtitles",
                "Extras", "extras"
            ]
        # 设置默认 worker 数量为 CPU 核心数，最小为 1，最大为 8
        if self.rename_worker_count <= 0:
            cpu_count = os.cpu_count() or 4
            self.rename_worker_count = min(max(cpu_count, 1), 8)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
            
        Returns:
            Config: 配置对象
        """
        if config_path is None:
            config_path = cls.get_default_config_path()
        
        if not config_path.exists():
            # 如果配置文件不存在，返回默认配置
            return cls()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return cls()
    
    def save(self, config_path: Optional[Path] = None) -> bool:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径
            
        Returns:
            bool: 是否保存成功
        """
        if config_path is None:
            config_path = self.get_default_config_path()
        
        try:
            # 确保配置目录存在
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    @staticmethod
    def get_default_config_path() -> Path:
        """
        获取默认配置文件路径
        
        Returns:
            Path: 配置文件路径
        """
        # 使用用户主目录下的 .smartrenamer 目录
        config_dir = Path.home() / ".smartrenamer"
        return config_dir / "config.json"
    
    def get_cache_dir(self) -> Path:
        """
        获取缓存目录路径
        
        Returns:
            Path: 缓存目录路径
        """
        cache_dir = Path.home() / ".smartrenamer" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项名称
            default: 默认值
            
        Returns:
            Any: 配置项值
        """
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项名称
            value: 配置项值
        """
        setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    def update(self, **kwargs) -> None:
        """
        更新配置项
        
        Args:
            **kwargs: 要更新的配置项
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证配置的有效性
        
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误消息)
        """
        # 验证 TMDB API Key
        if not self.tmdb_api_key:
            return False, "TMDB API Key 未配置"
        
        # 验证支持的扩展名
        if not self.supported_extensions:
            return False, "未配置支持的文件扩展名"
        
        # 验证数值范围
        if self.min_file_size < 0:
            return False, "最小文件大小不能为负数"
        
        if self.max_concurrent_requests < 1:
            return False, "最大并发请求数必须大于 0"
        
        if self.request_timeout < 1:
            return False, "请求超时时间必须大于 0"
        
        return True, None


# 全局配置实例
_global_config: Optional[Config] = None


def get_config() -> Config:
    """
    获取全局配置实例
    
    Returns:
        Config: 全局配置对象
    """
    global _global_config
    if _global_config is None:
        _global_config = Config.load()
    return _global_config


def set_config(config: Config) -> None:
    """
    设置全局配置实例
    
    Args:
        config: 配置对象
    """
    global _global_config
    _global_config = config
