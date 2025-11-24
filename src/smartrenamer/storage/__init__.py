"""
网盘存储适配器模块

提供统一的存储抽象接口，支持本地文件系统和多种网盘存储
"""

from .base import StorageAdapter, StorageFile, StorageType
from .local import LocalStorageAdapter
from .storage_115 import Storage115Adapter
from .storage_123 import Storage123Adapter
from .manager import StorageManager, get_storage_manager, set_storage_manager

__all__ = [
    "StorageAdapter",
    "StorageFile",
    "StorageType",
    "LocalStorageAdapter",
    "Storage115Adapter",
    "Storage123Adapter",
    "StorageManager",
    "get_storage_manager",
    "set_storage_manager",
]
