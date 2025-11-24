"""
存储适配器基类

定义统一的存储接口，支持本地和云端存储
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any, Iterator


class StorageType(Enum):
    """存储类型枚举"""
    LOCAL = "local"
    STORAGE_115 = "115"
    STORAGE_123 = "123"


@dataclass
class StorageFile:
    """
    存储文件信息
    
    统一表示本地文件和网盘文件的信息
    """
    # 基本信息
    路径: str  # 文件路径（本地路径或网盘路径）
    名称: str  # 文件名
    大小: int  # 文件大小（字节）
    是否目录: bool  # 是否为目录
    修改时间: datetime  # 最后修改时间
    
    # 扩展信息
    文件ID: Optional[str] = None  # 网盘文件 ID（本地为 None）
    父目录ID: Optional[str] = None  # 网盘父目录 ID
    哈希值: Optional[str] = None  # 文件哈希（用于去重）
    缩略图URL: Optional[str] = None  # 缩略图 URL
    下载URL: Optional[str] = None  # 下载 URL
    扩展属性: Optional[Dict[str, Any]] = None  # 其他扩展属性
    
    # 英文兼容接口
    @property
    def path(self) -> str:
        """路径"""
        return self.路径
    
    @property
    def name(self) -> str:
        """名称"""
        return self.名称
    
    @property
    def size(self) -> int:
        """大小"""
        return self.大小
    
    @property
    def is_dir(self) -> bool:
        """是否目录"""
        return self.是否目录
    
    @property
    def modified_time(self) -> datetime:
        """修改时间"""
        return self.修改时间
    
    @property
    def file_id(self) -> Optional[str]:
        """文件ID"""
        return self.文件ID
    
    @property
    def parent_id(self) -> Optional[str]:
        """父目录ID"""
        return self.父目录ID


class StorageAdapter(ABC):
    """
    存储适配器抽象基类
    
    定义统一的存储操作接口
    """
    
    def __init__(self, 配置: Dict[str, Any]):
        """
        初始化存储适配器
        
        Args:
            配置: 存储配置字典
        """
        self.配置 = 配置
        self.已连接 = False
    
    @abstractmethod
    def 连接(self) -> bool:
        """
        连接到存储
        
        Returns:
            bool: 是否连接成功
        """
        pass
    
    @abstractmethod
    def 断开连接(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def 列出文件(
        self,
        路径: str,
        递归: bool = False,
        过滤器: Optional[callable] = None
    ) -> List[StorageFile]:
        """
        列出目录中的文件
        
        Args:
            路径: 目录路径
            递归: 是否递归列出子目录
            过滤器: 文件过滤函数
            
        Returns:
            List[StorageFile]: 文件列表
        """
        pass
    
    @abstractmethod
    def 列出文件迭代(
        self,
        路径: str,
        递归: bool = False,
        过滤器: Optional[callable] = None,
        批次大小: int = 100
    ) -> Iterator[List[StorageFile]]:
        """
        流式列出目录中的文件（生成器）
        
        Args:
            路径: 目录路径
            递归: 是否递归列出子目录
            过滤器: 文件过滤函数
            批次大小: 每批返回的文件数
            
        Yields:
            List[StorageFile]: 批量文件列表
        """
        pass
    
    @abstractmethod
    def 获取文件信息(self, 路径: str) -> Optional[StorageFile]:
        """
        获取文件信息
        
        Args:
            路径: 文件路径
            
        Returns:
            Optional[StorageFile]: 文件信息，不存在则返回 None
        """
        pass
    
    @abstractmethod
    def 读取文件(self, 路径: str, 本地路径: Optional[Path] = None) -> Optional[Path]:
        """
        读取文件内容
        
        Args:
            路径: 文件路径
            本地路径: 保存到本地的路径（可选，如果为 None 则保存到临时目录）
            
        Returns:
            Optional[Path]: 本地文件路径，失败则返回 None
        """
        pass
    
    @abstractmethod
    def 写入文件(self, 本地路径: Path, 目标路径: str) -> bool:
        """
        写入文件
        
        Args:
            本地路径: 本地文件路径
            目标路径: 目标存储路径
            
        Returns:
            bool: 是否写入成功
        """
        pass
    
    @abstractmethod
    def 删除文件(self, 路径: str) -> bool:
        """
        删除文件
        
        Args:
            路径: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        pass
    
    @abstractmethod
    def 重命名文件(self, 源路径: str, 目标路径: str) -> bool:
        """
        重命名文件
        
        Args:
            源路径: 源文件路径
            目标路径: 目标文件路径
            
        Returns:
            bool: 是否重命名成功
        """
        pass
    
    @abstractmethod
    def 创建目录(self, 路径: str) -> bool:
        """
        创建目录
        
        Args:
            路径: 目录路径
            
        Returns:
            bool: 是否创建成功
        """
        pass
    
    @abstractmethod
    def 文件存在(self, 路径: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            路径: 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        pass
    
    @abstractmethod
    def 获取存储空间信息(self) -> Dict[str, Any]:
        """
        获取存储空间信息
        
        Returns:
            Dict[str, Any]: 存储空间信息（总空间、已用空间、剩余空间等）
        """
        pass
    
    def 获取类型(self) -> StorageType:
        """
        获取存储类型
        
        Returns:
            StorageType: 存储类型
        """
        return StorageType.LOCAL
    
    # 英文兼容接口
    def connect(self) -> bool:
        """连接到存储"""
        return self.连接()
    
    def disconnect(self) -> None:
        """断开连接"""
        return self.断开连接()
    
    def list_files(
        self,
        path: str,
        recursive: bool = False,
        filter_func: Optional[callable] = None
    ) -> List[StorageFile]:
        """列出文件"""
        return self.列出文件(path, recursive, filter_func)
    
    def list_files_iter(
        self,
        path: str,
        recursive: bool = False,
        filter_func: Optional[callable] = None,
        batch_size: int = 100
    ) -> Iterator[List[StorageFile]]:
        """流式列出文件"""
        return self.列出文件迭代(path, recursive, filter_func, batch_size)
    
    def get_file_info(self, path: str) -> Optional[StorageFile]:
        """获取文件信息"""
        return self.获取文件信息(path)
    
    def read_file(self, path: str, local_path: Optional[Path] = None) -> Optional[Path]:
        """读取文件"""
        return self.读取文件(path, local_path)
    
    def write_file(self, local_path: Path, target_path: str) -> bool:
        """写入文件"""
        return self.写入文件(local_path, target_path)
    
    def delete_file(self, path: str) -> bool:
        """删除文件"""
        return self.删除文件(path)
    
    def rename_file(self, source_path: str, target_path: str) -> bool:
        """重命名文件"""
        return self.重命名文件(source_path, target_path)
    
    def create_directory(self, path: str) -> bool:
        """创建目录"""
        return self.创建目录(path)
    
    def file_exists(self, path: str) -> bool:
        """文件存在"""
        return self.文件存在(path)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储空间信息"""
        return self.获取存储空间信息()
    
    def get_type(self) -> StorageType:
        """获取存储类型"""
        return self.获取类型()
