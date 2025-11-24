"""
TMDB 客户端工厂

提供单例模式的 TMDB 客户端，确保全局共用同一个实例
"""
import logging
from typing import Optional
from pathlib import Path
from threading import Lock

from smartrenamer.api.tmdb_client_enhanced import 增强TMDB客户端, EnhancedTMDBClient
from smartrenamer.core.config import Config, get_config


logger = logging.getLogger(__name__)


class TMDBClientFactory:
    """
    TMDB 客户端工厂
    
    使用单例模式确保全局只有一个 TMDB 客户端实例
    """
    
    _instance: Optional[增强TMDB客户端] = None
    _lock = Lock()
    _config_hash: Optional[str] = None
    
    @classmethod
    def get_client(cls, config: Optional[Config] = None, force_recreate: bool = False) -> 增强TMDB客户端:
        """
        获取 TMDB 客户端单例
        
        Args:
            config: 配置对象，如果为 None 则使用全局配置
            force_recreate: 是否强制重新创建客户端
            
        Returns:
            增强TMDB客户端: 客户端实例
        """
        if config is None:
            config = get_config()
        
        # 计算配置哈希，用于检测配置是否改变
        config_hash = cls._compute_config_hash(config)
        
        with cls._lock:
            # 如果配置改变或强制重建，重新创建客户端
            if force_recreate or cls._instance is None or cls._config_hash != config_hash:
                logger.info("创建新的 TMDB 客户端实例")
                cls._instance = cls._create_client(config)
                cls._config_hash = config_hash
            
            return cls._instance
    
    @classmethod
    def _create_client(cls, config: Config) -> 增强TMDB客户端:
        """
        创建 TMDB 客户端实例
        
        Args:
            config: 配置对象
            
        Returns:
            增强TMDB客户端: 新的客户端实例
        """
        # 获取缓存配置
        缓存目录 = config.get_cache_dir() / "tmdb"
        启用缓存 = config.get("tmdb_cache_enabled", True)
        缓存过期天数 = config.get("tmdb_cache_ttl_hours", 168) / 24  # 转换为天数
        最大重试次数 = 3
        重试延迟 = 1.0
        
        # 创建客户端实例
        客户端 = 增强TMDB客户端(
            api_key=config.tmdb_api_key,
            language=config.tmdb_language,
            缓存目录=缓存目录,
            启用缓存=启用缓存,
            最大重试次数=最大重试次数,
            重试延迟=重试延迟,
            缓存过期天数=缓存过期天数,
            最大缓存条目数=config.get("tmdb_cache_max_entries", 1000),
            最大并发请求数=config.get("max_concurrent_requests", 5),
            请求超时=config.get("request_timeout", 30)
        )
        
        logger.info(f"TMDB 客户端配置: 缓存={'启用' if 启用缓存 else '禁用'}, "
                   f"TTL={缓存过期天数:.1f}天, 并发={config.get('max_concurrent_requests', 5)}")
        
        return 客户端
    
    @classmethod
    def _compute_config_hash(cls, config: Config) -> str:
        """
        计算配置哈希值
        
        Args:
            config: 配置对象
            
        Returns:
            str: 配置哈希值
        """
        import hashlib
        
        # 选取影响客户端行为的关键配置项
        config_str = f"{config.tmdb_api_key}:{config.tmdb_language}:" \
                    f"{config.get('tmdb_cache_enabled')}:" \
                    f"{config.get('tmdb_cache_ttl_hours')}:" \
                    f"{config.get('tmdb_cache_max_entries')}:" \
                    f"{config.get('max_concurrent_requests')}:" \
                    f"{config.get('request_timeout')}"
        
        return hashlib.md5(config_str.encode()).hexdigest()
    
    @classmethod
    def clear_instance(cls):
        """清除客户端实例（主要用于测试）"""
        with cls._lock:
            if cls._instance:
                logger.info("清除 TMDB 客户端实例")
                cls._instance = None
                cls._config_hash = None
    
    @classmethod
    def get_cache_stats(cls) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        with cls._lock:
            if cls._instance is None:
                return {
                    "enabled": False,
                    "memory_hits": 0,
                    "memory_misses": 0,
                    "disk_hits": 0,
                    "disk_misses": 0,
                    "total_entries": 0
                }
            
            return cls._instance.获取缓存统计()


# 保持向后兼容的英文接口
def get_tmdb_client(config: Optional[Config] = None, force_recreate: bool = False) -> EnhancedTMDBClient:
    """
    获取 TMDB 客户端单例（英文接口）
    
    Args:
        config: 配置对象
        force_recreate: 是否强制重新创建
        
    Returns:
        EnhancedTMDBClient: 客户端实例
    """
    return TMDBClientFactory.get_client(config, force_recreate)


def clear_tmdb_client():
    """清除 TMDB 客户端实例"""
    TMDBClientFactory.clear_instance()


def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    return TMDBClientFactory.get_cache_stats()
