"""
媒体库管理模块

提供媒体库的构建、缓存和查询功能
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Callable
from datetime import datetime

from .models import MediaFile, MediaType
from .scanner import FileScanner


logger = logging.getLogger(__name__)


class MediaLibrary:
    """
    媒体库管理器
    
    管理扫描结果，提供缓存、查询和更新功能
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True
    ):
        """
        初始化媒体库
        
        Args:
            cache_dir: 缓存目录，None 使用默认路径
            enable_cache: 是否启用缓存
        """
        self.enable_cache = enable_cache
        
        # 设置缓存目录
        if cache_dir is None:
            cache_dir = Path.home() / ".smartrenamer" / "cache"
        self.cache_dir = cache_dir
        
        # 确保缓存目录存在
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 媒体文件列表
        self.media_files: List[MediaFile] = []
        
        # 扫描源路径记录
        self.scan_sources: List[Path] = []
        
        # 最后扫描时间
        self.last_scan_time: Optional[datetime] = None
        
        # 索引（用于快速查询）
        self._title_index: Dict[str, List[MediaFile]] = {}
        self._type_index: Dict[MediaType, List[MediaFile]] = {}
    
    def add_scan_source(self, directory: Path) -> None:
        """
        添加扫描源
        
        Args:
            directory: 目录路径
        """
        if isinstance(directory, str):
            directory = Path(directory)
        
        if directory not in self.scan_sources:
            self.scan_sources.append(directory)
            logger.info(f"添加扫描源: {directory}")
    
    def remove_scan_source(self, directory: Path) -> None:
        """
        移除扫描源
        
        Args:
            directory: 目录路径
        """
        if isinstance(directory, str):
            directory = Path(directory)
        
        if directory in self.scan_sources:
            self.scan_sources.remove(directory)
            logger.info(f"移除扫描源: {directory}")
    
    def scan(
        self,
        scanner: Optional[FileScanner] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> int:
        """
        扫描所有配置的源目录
        
        Args:
            scanner: 文件扫描器，None 使用默认配置
            progress_callback: 进度回调函数
            
        Returns:
            int: 找到的媒体文件总数
        """
        if not self.scan_sources:
            logger.warning("没有配置扫描源")
            return 0
        
        # 创建扫描器
        if scanner is None:
            scanner = FileScanner()
        
        # 清空现有数据
        self.media_files = []
        
        # 扫描所有源
        for source in self.scan_sources:
            if not source.exists():
                logger.warning(f"扫描源不存在，跳过: {source}")
                continue
            
            logger.info(f"正在扫描: {source}")
            try:
                files = scanner.scan(source, progress_callback)
                self.media_files.extend(files)
                logger.info(f"从 {source} 找到 {len(files)} 个媒体文件")
            except Exception as e:
                logger.error(f"扫描 {source} 失败: {e}")
        
        # 更新扫描时间
        self.last_scan_time = datetime.now()
        
        # 重建索引
        self._rebuild_indexes()
        
        # 保存到缓存
        if self.enable_cache:
            self.save_cache()
        
        logger.info(f"扫描完成，共找到 {len(self.media_files)} 个媒体文件")
        return len(self.media_files)
    
    def refresh(
        self,
        scanner: Optional[FileScanner] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> int:
        """
        刷新媒体库（重新扫描）
        
        Args:
            scanner: 文件扫描器
            progress_callback: 进度回调函数
            
        Returns:
            int: 找到的媒体文件总数
        """
        logger.info("刷新媒体库...")
        return self.scan(scanner, progress_callback)
    
    def update(
        self,
        scanner: Optional[FileScanner] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, int]:
        """
        增量更新媒体库（检测新增和删除的文件）
        
        Args:
            scanner: 文件扫描器
            progress_callback: 进度回调函数
            
        Returns:
            Dict[str, int]: 更新统计 {"added": 新增数, "removed": 删除数}
        """
        logger.info("增量更新媒体库...")
        
        # 保存现有文件路径
        existing_paths = {mf.path for mf in self.media_files}
        
        # 扫描新文件
        if scanner is None:
            scanner = FileScanner()
        
        new_media_files = []
        for source in self.scan_sources:
            if not source.exists():
                continue
            try:
                files = scanner.scan(source, progress_callback)
                new_media_files.extend(files)
            except Exception as e:
                logger.error(f"扫描 {source} 失败: {e}")
        
        # 计算新增和删除
        new_paths = {mf.path for mf in new_media_files}
        
        added_paths = new_paths - existing_paths
        removed_paths = existing_paths - new_paths
        
        # 更新媒体文件列表
        self.media_files = [mf for mf in self.media_files if mf.path not in removed_paths]
        new_files = [mf for mf in new_media_files if mf.path in added_paths]
        self.media_files.extend(new_files)
        
        # 更新扫描时间
        self.last_scan_time = datetime.now()
        
        # 重建索引
        self._rebuild_indexes()
        
        # 保存缓存
        if self.enable_cache:
            self.save_cache()
        
        result = {
            "added": len(added_paths),
            "removed": len(removed_paths)
        }
        
        logger.info(f"更新完成: 新增 {result['added']} 个，删除 {result['removed']} 个")
        return result
    
    def _rebuild_indexes(self) -> None:
        """重建索引以加速查询"""
        # 清空索引
        self._title_index = {}
        self._type_index = {
            MediaType.MOVIE: [],
            MediaType.TV_SHOW: [],
            MediaType.UNKNOWN: []
        }
        
        # 构建索引
        for media_file in self.media_files:
            # 标题索引
            if media_file.title:
                title_lower = media_file.title.lower()
                if title_lower not in self._title_index:
                    self._title_index[title_lower] = []
                self._title_index[title_lower].append(media_file)
            
            # 类型索引
            self._type_index[media_file.media_type].append(media_file)
    
    def search_by_title(self, title: str) -> List[MediaFile]:
        """
        按标题搜索媒体文件
        
        Args:
            title: 标题关键词
            
        Returns:
            List[MediaFile]: 匹配的媒体文件列表
        """
        title_lower = title.lower()
        results = []
        
        # 精确匹配
        if title_lower in self._title_index:
            results.extend(self._title_index[title_lower])
        
        # 模糊匹配
        for indexed_title, files in self._title_index.items():
            if title_lower in indexed_title and indexed_title != title_lower:
                results.extend(files)
        
        return results
    
    def get_by_type(self, media_type: MediaType) -> List[MediaFile]:
        """
        按类型获取媒体文件
        
        Args:
            media_type: 媒体类型
            
        Returns:
            List[MediaFile]: 指定类型的媒体文件列表
        """
        return self._type_index.get(media_type, [])
    
    def get_movies(self) -> List[MediaFile]:
        """获取所有电影"""
        return self.get_by_type(MediaType.MOVIE)
    
    def get_tv_shows(self) -> List[MediaFile]:
        """获取所有电视剧"""
        return self.get_by_type(MediaType.TV_SHOW)
    
    def get_all(self) -> List[MediaFile]:
        """获取所有媒体文件"""
        return self.media_files.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取库统计信息
        
        Returns:
            Dict[str, int]: 统计信息
        """
        return {
            "总文件数": len(self.media_files),
            "电影数": len(self.get_movies()),
            "电视剧数": len(self.get_tv_shows()),
            "未知类型数": len(self.get_by_type(MediaType.UNKNOWN)),
            "扫描源数": len(self.scan_sources),
        }
    
    def save_cache(self, cache_file: Optional[Path] = None) -> bool:
        """
        保存媒体库到缓存文件
        
        Args:
            cache_file: 缓存文件路径，None 使用默认路径
            
        Returns:
            bool: 是否保存成功
        """
        if not self.enable_cache:
            return False
        
        if cache_file is None:
            cache_file = self.cache_dir / "media_library.json"
        
        try:
            data = {
                "version": "1.0",
                "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
                "scan_sources": [str(s) for s in self.scan_sources],
                "media_files": [mf.to_dict() for mf in self.media_files],
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"媒体库缓存已保存到: {cache_file}")
            return True
        
        except Exception as e:
            logger.error(f"保存媒体库缓存失败: {e}")
            return False
    
    def load_cache(self, cache_file: Optional[Path] = None) -> bool:
        """
        从缓存文件加载媒体库
        
        Args:
            cache_file: 缓存文件路径，None 使用默认路径
            
        Returns:
            bool: 是否加载成功
        """
        if not self.enable_cache:
            return False
        
        if cache_file is None:
            cache_file = self.cache_dir / "media_library.json"
        
        if not cache_file.exists():
            logger.warning(f"缓存文件不存在: {cache_file}")
            return False
        
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 恢复扫描源
            self.scan_sources = [Path(s) for s in data.get("scan_sources", [])]
            
            # 恢复扫描时间
            last_scan_str = data.get("last_scan_time")
            if last_scan_str:
                self.last_scan_time = datetime.fromisoformat(last_scan_str)
            
            # 恢复媒体文件
            self.media_files = []
            for mf_dict in data.get("media_files", []):
                # 转换字典为 MediaFile 对象
                media_file = self._dict_to_media_file(mf_dict)
                if media_file:
                    self.media_files.append(media_file)
            
            # 重建索引
            self._rebuild_indexes()
            
            logger.info(f"从缓存加载了 {len(self.media_files)} 个媒体文件")
            return True
        
        except Exception as e:
            logger.error(f"加载媒体库缓存失败: {e}")
            return False
    
    def _dict_to_media_file(self, data: dict) -> Optional[MediaFile]:
        """
        将字典转换为 MediaFile 对象
        
        Args:
            data: 字典数据
            
        Returns:
            Optional[MediaFile]: 媒体文件对象
        """
        try:
            # 转换媒体类型
            media_type_str = data.get("media_type", "unknown")
            media_type = MediaType(media_type_str)
            
            # 转换创建时间
            created_at_str = data.get("created_at")
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
            
            return MediaFile(
                path=Path(data["path"]),
                original_name=data["original_name"],
                extension=data["extension"],
                size=data.get("size", 0),
                media_type=media_type,
                tmdb_id=data.get("tmdb_id"),
                title=data.get("title"),
                original_title=data.get("original_title"),
                year=data.get("year"),
                season_number=data.get("season_number"),
                episode_number=data.get("episode_number"),
                episode_title=data.get("episode_title"),
                resolution=data.get("resolution"),
                source=data.get("source"),
                codec=data.get("codec"),
                new_name=data.get("new_name"),
                rename_status=data.get("rename_status", "pending"),
                error_message=data.get("error_message"),
                metadata=data.get("metadata", {}),
                created_at=created_at,
            )
        except Exception as e:
            logger.error(f"转换媒体文件数据失败: {e}")
            return None
    
    def clear(self) -> None:
        """清空媒体库"""
        self.media_files = []
        self.scan_sources = []
        self.last_scan_time = None
        self._rebuild_indexes()
        logger.info("媒体库已清空")
    
    def clear_cache(self) -> bool:
        """
        清除缓存文件
        
        Returns:
            bool: 是否成功
        """
        if not self.enable_cache:
            return False
        
        cache_file = self.cache_dir / "media_library.json"
        
        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.info("缓存文件已删除")
            return True
        except Exception as e:
            logger.error(f"删除缓存文件失败: {e}")
            return False
