"""
文件扫描模块

提供媒体文件的扫描和信息提取功能
"""
import os
import logging
from pathlib import Path
from typing import List, Optional, Callable
from datetime import datetime

from .models import MediaFile, MediaType
from ..utils.file_utils import (
    get_file_size,
    is_supported_file,
    extract_info_from_filename,
)


logger = logging.getLogger(__name__)


class FileScanner:
    """
    文件扫描器
    
    递归扫描指定目录，识别和提取媒体文件信息
    """
    
    # 默认支持的视频文件扩展名
    DEFAULT_EXTENSIONS = [
        ".mkv", ".mp4", ".avi", ".mov",
        ".wmv", ".flv", ".m4v", ".ts",
        ".mpg", ".mpeg", ".m2ts", ".webm"
    ]
    
    # 默认排除的目录名称
    DEFAULT_EXCLUDE_DIRS = [
        "Sample", "Samples", "sample", "samples",
        "Subs", "Subtitles", "subs", "subtitles",
        "Extras", "extras", "Featurettes", "featurettes",
        "@eaDir", ".AppleDouble", ".DS_Store"
    ]
    
    def __init__(
        self,
        supported_extensions: Optional[List[str]] = None,
        exclude_dirs: Optional[List[str]] = None,
        min_file_size: int = 10 * 1024 * 1024,  # 10 MB
        max_depth: Optional[int] = None,
    ):
        """
        初始化文件扫描器
        
        Args:
            supported_extensions: 支持的文件扩展名列表
            exclude_dirs: 要排除的目录名称列表
            min_file_size: 最小文件大小（字节）
            max_depth: 最大扫描深度，None 表示无限制
        """
        self.supported_extensions = supported_extensions or self.DEFAULT_EXTENSIONS
        self.exclude_dirs = exclude_dirs or self.DEFAULT_EXCLUDE_DIRS
        self.min_file_size = min_file_size
        self.max_depth = max_depth
        
        # 统计信息
        self.扫描文件总数 = 0
        self.找到媒体文件数 = 0
        self.跳过文件数 = 0
    
    def scan(
        self,
        directory: Path,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[MediaFile]:
        """
        扫描目录并返回媒体文件列表
        
        Args:
            directory: 要扫描的目录路径
            progress_callback: 进度回调函数(当前文件, 已扫描数, 找到数)
            
        Returns:
            List[MediaFile]: 找到的媒体文件列表
        """
        if isinstance(directory, str):
            directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"目录不存在: {directory}")
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if not directory.is_dir():
            logger.error(f"路径不是目录: {directory}")
            raise NotADirectoryError(f"路径不是目录: {directory}")
        
        # 重置统计信息
        self.扫描文件总数 = 0
        self.找到媒体文件数 = 0
        self.跳过文件数 = 0
        
        logger.info(f"开始扫描目录: {directory}")
        media_files = []
        
        # 递归扫描
        self._scan_recursive(
            directory,
            media_files,
            depth=0,
            progress_callback=progress_callback
        )
        
        logger.info(
            f"扫描完成: 总文件数={self.扫描文件总数}, "
            f"媒体文件数={self.找到媒体文件数}, "
            f"跳过文件数={self.跳过文件数}"
        )
        
        return media_files
    
    def _scan_recursive(
        self,
        directory: Path,
        media_files: List[MediaFile],
        depth: int,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> None:
        """
        递归扫描目录的内部实现
        
        Args:
            directory: 当前目录
            media_files: 媒体文件列表（输出）
            depth: 当前深度
            progress_callback: 进度回调函数
        """
        # 检查深度限制
        if self.max_depth is not None and depth > self.max_depth:
            return
        
        try:
            # 遍历目录内容
            for entry in os.scandir(directory):
                try:
                    # 处理子目录
                    if entry.is_dir(follow_symlinks=False):
                        # 检查是否应该排除该目录
                        if entry.name in self.exclude_dirs:
                            logger.debug(f"跳过排除目录: {entry.path}")
                            continue
                        
                        # 递归扫描子目录
                        self._scan_recursive(
                            Path(entry.path),
                            media_files,
                            depth + 1,
                            progress_callback
                        )
                    
                    # 处理文件
                    elif entry.is_file(follow_symlinks=False):
                        self.扫描文件总数 += 1
                        
                        # 调用进度回调
                        if progress_callback:
                            progress_callback(
                                entry.path,
                                self.扫描文件总数,
                                self.找到媒体文件数
                            )
                        
                        # 检查文件
                        media_file = self._process_file(Path(entry.path))
                        if media_file:
                            media_files.append(media_file)
                            self.找到媒体文件数 += 1
                        else:
                            self.跳过文件数 += 1
                
                except (PermissionError, OSError) as e:
                    logger.warning(f"无法访问: {entry.path}, 错误: {e}")
                    continue
        
        except (PermissionError, OSError) as e:
            logger.warning(f"无法扫描目录: {directory}, 错误: {e}")
    
    def _process_file(self, file_path: Path) -> Optional[MediaFile]:
        """
        处理单个文件，提取媒体信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[MediaFile]: 媒体文件对象，如果不是有效的媒体文件则返回 None
        """
        # 检查文件扩展名
        if not is_supported_file(file_path, self.supported_extensions):
            logger.debug(f"不支持的文件格式: {file_path}")
            return None
        
        # 获取文件大小
        file_size = get_file_size(file_path)
        
        # 检查文件大小
        if file_size < self.min_file_size:
            logger.debug(f"文件太小，跳过: {file_path} ({file_size} 字节)")
            return None
        
        # 提取文件信息
        filename = file_path.stem
        info = extract_info_from_filename(filename)
        
        # 判断媒体类型
        media_type = MediaType.UNKNOWN
        if info["season"] is not None and info["episode"] is not None:
            media_type = MediaType.TV_SHOW
        elif info["year"] is not None:
            media_type = MediaType.MOVIE
        
        # 提取标题（移除年份、分辨率等信息）
        title = self._extract_title(filename, info)
        
        # 获取文件修改时间
        try:
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        except:
            modified_time = datetime.now()
        
        # 创建媒体文件对象
        media_file = MediaFile(
            path=file_path,
            original_name=file_path.name,
            extension=file_path.suffix,
            size=file_size,
            media_type=media_type,
            title=title,
            year=info["year"],
            season_number=info["season"],
            episode_number=info["episode"],
            resolution=info["resolution"],
            source=info["source"],
            codec=info["codec"],
            metadata={
                "modified_time": modified_time.isoformat(),
                "scanned_at": datetime.now().isoformat(),
            }
        )
        
        logger.debug(f"找到媒体文件: {file_path.name} (类型: {media_type.value})")
        return media_file
    
    def _extract_title(self, filename: str, info: dict) -> str:
        """
        从文件名提取标题
        
        Args:
            filename: 文件名（不含扩展名）
            info: 提取的信息字典
            
        Returns:
            str: 提取的标题
        """
        import re
        
        title = filename
        
        # 移除年份
        if info["year"]:
            title = re.sub(rf'\b{info["year"]}\b', '', title)
        
        # 移除季集信息
        title = re.sub(r'[Ss]\d{1,2}[Ee]\d{1,2}', '', title)
        
        # 移除分辨率
        if info["resolution"]:
            title = re.sub(
                r'\b(2160p|4K|UHD|1080p|720p|480p)\b',
                '',
                title,
                flags=re.IGNORECASE
            )
        
        # 移除来源
        if info["source"]:
            title = re.sub(
                r'\b(BluRay|Blu-ray|BD|WEB-DL|WEBDL|WEB|HDTV|DVDRip)\b',
                '',
                title,
                flags=re.IGNORECASE
            )
        
        # 移除编码
        if info["codec"]:
            title = re.sub(
                r'\b([Hh]\.?265|HEVC|[Hh]\.?264|AVC|x264|x265)\b',
                '',
                title,
                flags=re.IGNORECASE
            )
        
        # 移除常见的标签
        title = re.sub(
            r'\b(PROPER|REPACK|EXTENDED|UNRATED|DIRECTORS.CUT|iNTERNAL)\b',
            '',
            title,
            flags=re.IGNORECASE
        )
        
        # 清理分隔符
        title = re.sub(r'[._\-]+', ' ', title)
        
        # 移除多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title or "Unknown"
    
    def get_statistics(self) -> dict:
        """
        获取扫描统计信息
        
        Returns:
            dict: 统计信息字典
        """
        return {
            "扫描文件总数": self.扫描文件总数,
            "找到媒体文件数": self.找到媒体文件数,
            "跳过文件数": self.跳过文件数,
        }
