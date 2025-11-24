"""
存储管理器

统一管理不同的存储适配器
"""

import logging
from typing import Optional, Dict, Any

from .base import StorageAdapter, StorageType
from .local import LocalStorageAdapter
from .storage_115 import Storage115Adapter
from .storage_123 import Storage123Adapter

logger = logging.getLogger(__name__)


class StorageManager:
    """
    存储管理器
    
    负责创建和管理不同类型的存储适配器
    """
    
    def __init__(self):
        """初始化存储管理器"""
        self._适配器缓存: Dict[str, StorageAdapter] = {}
        self._当前适配器: Optional[StorageAdapter] = None
        self._当前类型: str = "local"
    
    def 创建适配器(self, 存储类型: str, 配置: Dict[str, Any]) -> Optional[StorageAdapter]:
        """
        创建存储适配器
        
        Args:
            存储类型: 存储类型（local, 115, 123）
            配置: 存储配置
            
        Returns:
            Optional[StorageAdapter]: 存储适配器实例
        """
        try:
            if 存储类型 == "local" or 存储类型 == StorageType.LOCAL.value:
                return LocalStorageAdapter(配置)
            elif 存储类型 == "115" or 存储类型 == StorageType.STORAGE_115.value:
                return Storage115Adapter(配置)
            elif 存储类型 == "123" or 存储类型 == StorageType.STORAGE_123.value:
                return Storage123Adapter(配置)
            else:
                logger.error(f"不支持的存储类型: {存储类型}")
                return None
        
        except Exception as e:
            logger.error(f"创建存储适配器失败: {e}")
            return None
    
    def 获取适配器(
        self,
        存储类型: str,
        配置: Optional[Dict[str, Any]] = None,
        强制创建: bool = False
    ) -> Optional[StorageAdapter]:
        """
        获取存储适配器（带缓存）
        
        Args:
            存储类型: 存储类型
            配置: 存储配置（如果为 None，则尝试使用缓存）
            强制创建: 是否强制创建新实例
            
        Returns:
            Optional[StorageAdapter]: 存储适配器实例
        """
        # 如果强制创建或缓存中不存在
        if 强制创建 or 存储类型 not in self._适配器缓存:
            if 配置 is None:
                logger.error(f"无法创建适配器 {存储类型}：缺少配置")
                return None
            
            适配器 = self.创建适配器(存储类型, 配置)
            if 适配器:
                # 尝试连接
                if 适配器.连接():
                    self._适配器缓存[存储类型] = 适配器
                    logger.info(f"存储适配器 {存储类型} 已创建并连接")
                else:
                    logger.error(f"存储适配器 {存储类型} 连接失败")
                    return None
            return 适配器
        
        # 返回缓存的适配器
        return self._适配器缓存[存储类型]
    
    def 切换适配器(
        self,
        存储类型: str,
        配置: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        切换当前使用的存储适配器
        
        Args:
            存储类型: 存储类型
            配置: 存储配置
            
        Returns:
            bool: 是否切换成功
        """
        try:
            适配器 = self.获取适配器(存储类型, 配置)
            if 适配器:
                self._当前适配器 = 适配器
                self._当前类型 = 存储类型
                logger.info(f"已切换到存储适配器: {存储类型}")
                return True
            else:
                logger.error(f"切换存储适配器失败: {存储类型}")
                return False
        
        except Exception as e:
            logger.error(f"切换存储适配器失败: {e}")
            return False
    
    def 获取当前适配器(self) -> Optional[StorageAdapter]:
        """
        获取当前使用的存储适配器
        
        Returns:
            Optional[StorageAdapter]: 当前适配器
        """
        return self._当前适配器
    
    def 获取当前类型(self) -> str:
        """
        获取当前存储类型
        
        Returns:
            str: 当前存储类型
        """
        return self._当前类型
    
    def 关闭所有适配器(self) -> None:
        """关闭所有存储适配器"""
        for 存储类型, 适配器 in self._适配器缓存.items():
            try:
                适配器.断开连接()
                logger.info(f"已关闭存储适配器: {存储类型}")
            except Exception as e:
                logger.error(f"关闭存储适配器失败 {存储类型}: {e}")
        
        self._适配器缓存.clear()
        self._当前适配器 = None
    
    def 移除适配器(self, 存储类型: str) -> None:
        """
        移除指定的存储适配器
        
        Args:
            存储类型: 存储类型
        """
        if 存储类型 in self._适配器缓存:
            try:
                适配器 = self._适配器缓存[存储类型]
                适配器.断开连接()
                del self._适配器缓存[存储类型]
                logger.info(f"已移除存储适配器: {存储类型}")
                
                # 如果移除的是当前适配器，清空当前适配器
                if self._当前适配器 == 适配器:
                    self._当前适配器 = None
            
            except Exception as e:
                logger.error(f"移除存储适配器失败 {存储类型}: {e}")
    
    def 列出可用适配器(self) -> list:
        """
        列出所有可用的存储适配器类型
        
        Returns:
            list: 存储类型列表
        """
        return ["local", "115", "123"]
    
    # 英文兼容接口
    def create_adapter(self, storage_type: str, config: Dict[str, Any]) -> Optional[StorageAdapter]:
        """创建适配器"""
        return self.创建适配器(storage_type, config)
    
    def get_adapter(
        self,
        storage_type: str,
        config: Optional[Dict[str, Any]] = None,
        force_create: bool = False
    ) -> Optional[StorageAdapter]:
        """获取适配器"""
        return self.获取适配器(storage_type, config, force_create)
    
    def switch_adapter(
        self,
        storage_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """切换适配器"""
        return self.切换适配器(storage_type, config)
    
    def get_current_adapter(self) -> Optional[StorageAdapter]:
        """获取当前适配器"""
        return self.获取当前适配器()
    
    def get_current_type(self) -> str:
        """获取当前类型"""
        return self.获取当前类型()
    
    def close_all_adapters(self) -> None:
        """关闭所有适配器"""
        return self.关闭所有适配器()
    
    def remove_adapter(self, storage_type: str) -> None:
        """移除适配器"""
        return self.移除适配器(storage_type)
    
    def list_available_adapters(self) -> list:
        """列出可用适配器"""
        return self.列出可用适配器()


# 全局存储管理器实例
_global_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """
    获取全局存储管理器实例
    
    Returns:
        StorageManager: 全局存储管理器对象
    """
    global _global_storage_manager
    if _global_storage_manager is None:
        _global_storage_manager = StorageManager()
    return _global_storage_manager


def set_storage_manager(manager: StorageManager) -> None:
    """
    设置全局存储管理器实例
    
    Args:
        manager: 存储管理器对象
    """
    global _global_storage_manager
    _global_storage_manager = manager
