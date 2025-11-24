"""
本地文件系统存储适配器

提供本地文件系统的统一访问接口
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Iterator

from .base import StorageAdapter, StorageFile, StorageType

logger = logging.getLogger(__name__)


class LocalStorageAdapter(StorageAdapter):
    """
    本地文件系统适配器
    
    提供本地文件系统的统一访问接口
    """
    
    def __init__(self, 配置: Optional[Dict[str, Any]] = None):
        """
        初始化本地存储适配器
        
        Args:
            配置: 配置字典（本地存储可选）
        """
        super().__init__(配置 or {})
        self.根目录 = Path(self.配置.get("根目录", "/"))
    
    def 连接(self) -> bool:
        """
        连接到存储（本地存储始终可用）
        
        Returns:
            bool: 始终返回 True
        """
        self.已连接 = True
        logger.info("本地存储适配器已连接")
        return True
    
    def 断开连接(self) -> None:
        """断开连接（本地存储无需断开）"""
        self.已连接 = False
        logger.info("本地存储适配器已断开")
    
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
        文件列表 = []
        目录路径 = Path(路径)
        
        if not 目录路径.exists():
            logger.error(f"目录不存在: {路径}")
            return 文件列表
        
        if not 目录路径.is_dir():
            logger.error(f"路径不是目录: {路径}")
            return 文件列表
        
        try:
            if 递归:
                # 递归遍历
                for root, dirs, files in os.walk(目录路径):
                    root_path = Path(root)
                    
                    # 处理文件
                    for file in files:
                        file_path = root_path / file
                        存储文件 = self._路径转存储文件(file_path)
                        if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                            文件列表.append(存储文件)
                    
                    # 处理目录
                    for dir_name in dirs:
                        dir_path = root_path / dir_name
                        存储文件 = self._路径转存储文件(dir_path)
                        if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                            文件列表.append(存储文件)
            else:
                # 非递归遍历
                for entry in os.scandir(目录路径):
                    存储文件 = self._路径转存储文件(Path(entry.path))
                    if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                        文件列表.append(存储文件)
        
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
        
        return 文件列表
    
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
        目录路径 = Path(路径)
        
        if not 目录路径.exists() or not 目录路径.is_dir():
            return
        
        批次 = []
        
        try:
            if 递归:
                # 递归遍历
                for root, dirs, files in os.walk(目录路径):
                    root_path = Path(root)
                    
                    # 处理文件
                    for file in files:
                        file_path = root_path / file
                        存储文件 = self._路径转存储文件(file_path)
                        if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                            批次.append(存储文件)
                            
                            if len(批次) >= 批次大小:
                                yield 批次
                                批次 = []
                    
                    # 处理目录
                    for dir_name in dirs:
                        dir_path = root_path / dir_name
                        存储文件 = self._路径转存储文件(dir_path)
                        if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                            批次.append(存储文件)
                            
                            if len(批次) >= 批次大小:
                                yield 批次
                                批次 = []
            else:
                # 非递归遍历
                for entry in os.scandir(目录路径):
                    存储文件 = self._路径转存储文件(Path(entry.path))
                    if 存储文件 and (过滤器 is None or 过滤器(存储文件)):
                        批次.append(存储文件)
                        
                        if len(批次) >= 批次大小:
                            yield 批次
                            批次 = []
        
        except Exception as e:
            logger.error(f"流式列出文件失败: {e}")
        
        # 输出剩余的批次
        if 批次:
            yield 批次
    
    def 获取文件信息(self, 路径: str) -> Optional[StorageFile]:
        """
        获取文件信息
        
        Args:
            路径: 文件路径
            
        Returns:
            Optional[StorageFile]: 文件信息，不存在则返回 None
        """
        文件路径 = Path(路径)
        
        if not 文件路径.exists():
            return None
        
        return self._路径转存储文件(文件路径)
    
    def 读取文件(self, 路径: str, 本地路径: Optional[Path] = None) -> Optional[Path]:
        """
        读取文件内容（本地存储直接返回路径）
        
        Args:
            路径: 文件路径
            本地路径: 保存到本地的路径（对于本地存储，该参数会被忽略）
            
        Returns:
            Optional[Path]: 本地文件路径，失败则返回 None
        """
        文件路径 = Path(路径)
        
        if not 文件路径.exists() or not 文件路径.is_file():
            logger.error(f"文件不存在或不是文件: {路径}")
            return None
        
        # 如果指定了本地路径，复制文件
        if 本地路径 is not None:
            try:
                本地路径 = Path(本地路径)
                本地路径.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(文件路径, 本地路径)
                return 本地路径
            except Exception as e:
                logger.error(f"复制文件失败: {e}")
                return None
        
        # 否则直接返回原路径
        return 文件路径
    
    def 写入文件(self, 本地路径: Path, 目标路径: str) -> bool:
        """
        写入文件
        
        Args:
            本地路径: 本地文件路径
            目标路径: 目标存储路径
            
        Returns:
            bool: 是否写入成功
        """
        try:
            本地路径 = Path(本地路径)
            目标路径实例 = Path(目标路径)
            
            if not 本地路径.exists():
                logger.error(f"源文件不存在: {本地路径}")
                return False
            
            # 确保目标目录存在
            目标路径实例.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(本地路径, 目标路径实例)
            logger.info(f"写入文件成功: {目标路径}")
            return True
        
        except Exception as e:
            logger.error(f"写入文件失败: {e}")
            return False
    
    def 删除文件(self, 路径: str) -> bool:
        """
        删除文件
        
        Args:
            路径: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            文件路径 = Path(路径)
            
            if not 文件路径.exists():
                logger.warning(f"文件不存在: {路径}")
                return False
            
            if 文件路径.is_file():
                文件路径.unlink()
            elif 文件路径.is_dir():
                shutil.rmtree(文件路径)
            
            logger.info(f"删除文件成功: {路径}")
            return True
        
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    def 重命名文件(self, 源路径: str, 目标路径: str) -> bool:
        """
        重命名文件
        
        Args:
            源路径: 源文件路径
            目标路径: 目标文件路径
            
        Returns:
            bool: 是否重命名成功
        """
        try:
            源路径实例 = Path(源路径)
            目标路径实例 = Path(目标路径)
            
            if not 源路径实例.exists():
                logger.error(f"源文件不存在: {源路径}")
                return False
            
            # 确保目标目录存在
            目标路径实例.parent.mkdir(parents=True, exist_ok=True)
            
            # 重命名文件
            源路径实例.rename(目标路径实例)
            logger.info(f"重命名文件成功: {源路径} -> {目标路径}")
            return True
        
        except Exception as e:
            logger.error(f"重命名文件失败: {e}")
            return False
    
    def 创建目录(self, 路径: str) -> bool:
        """
        创建目录
        
        Args:
            路径: 目录路径
            
        Returns:
            bool: 是否创建成功
        """
        try:
            目录路径 = Path(路径)
            目录路径.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录成功: {路径}")
            return True
        
        except Exception as e:
            logger.error(f"创建目录失败: {e}")
            return False
    
    def 文件存在(self, 路径: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            路径: 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        return Path(路径).exists()
    
    def 获取存储空间信息(self) -> Dict[str, Any]:
        """
        获取存储空间信息
        
        Returns:
            Dict[str, Any]: 存储空间信息
        """
        try:
            stat = shutil.disk_usage(self.根目录)
            return {
                "总空间": stat.total,
                "已用空间": stat.used,
                "剩余空间": stat.free,
                "使用率": (stat.used / stat.total * 100) if stat.total > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取存储空间信息失败: {e}")
            return {
                "总空间": 0,
                "已用空间": 0,
                "剩余空间": 0,
                "使用率": 0
            }
    
    def 获取类型(self) -> StorageType:
        """
        获取存储类型
        
        Returns:
            StorageType: 本地存储类型
        """
        return StorageType.LOCAL
    
    def _路径转存储文件(self, 文件路径: Path) -> Optional[StorageFile]:
        """
        将本地路径转换为存储文件对象
        
        Args:
            文件路径: 本地文件路径
            
        Returns:
            Optional[StorageFile]: 存储文件对象
        """
        try:
            stat_info = 文件路径.stat()
            
            return StorageFile(
                路径=str(文件路径),
                名称=文件路径.name,
                大小=stat_info.st_size,
                是否目录=文件路径.is_dir(),
                修改时间=datetime.fromtimestamp(stat_info.st_mtime),
                文件ID=None,
                父目录ID=None,
                哈希值=None,
                缩略图URL=None,
                下载URL=None,
                扩展属性={
                    "创建时间": datetime.fromtimestamp(stat_info.st_ctime),
                    "访问时间": datetime.fromtimestamp(stat_info.st_atime),
                }
            )
        
        except Exception as e:
            logger.error(f"转换存储文件失败: {e}")
            return None
