"""
API 和第三方集成模块

负责与 TMDB 等外部 API 的交互
"""
from smartrenamer.api.tmdb_client import TMDBClient
from smartrenamer.api.tmdb_client_enhanced import (
    EnhancedTMDBClient,
    增强TMDB客户端,
    缓存管理器
)
from smartrenamer.api.factory import (
    TMDBClientFactory,
    get_tmdb_client,
    clear_tmdb_client,
    get_cache_stats
)

__all__ = [
    "TMDBClient",
    "EnhancedTMDBClient",
    "增强TMDB客户端",
    "缓存管理器",
    "TMDBClientFactory",
    "get_tmdb_client",
    "clear_tmdb_client",
    "get_cache_stats",
]
