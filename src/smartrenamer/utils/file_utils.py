"""
文件处理工具函数

提供文件操作相关的辅助功能
"""
import re
from pathlib import Path
from typing import List


def get_file_size(file_path: Path) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小
    """
    try:
        return file_path.stat().st_size
    except Exception:
        return 0


def is_supported_file(file_path: Path, supported_extensions: List[str]) -> bool:
    """
    检查文件是否为支持的格式
    
    Args:
        file_path: 文件路径
        supported_extensions: 支持的扩展名列表
        
    Returns:
        bool: 是否支持
    """
    return file_path.suffix.lower() in [ext.lower() for ext in supported_extensions]


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不合法的字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 移除或替换不合法的字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, "", filename)
    
    # 移除多余的空格
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    # 移除首尾的点
    filename = filename.strip('.')
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读的格式
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的大小
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def extract_info_from_filename(filename: str) -> dict:
    """
    从文件名中提取信息（年份、分辨率等）
    
    Args:
        filename: 文件名
        
    Returns:
        dict: 提取的信息
    """
    info = {
        "year": None,
        "resolution": None,
        "source": None,
        "codec": None,
        "season": None,
        "episode": None,
    }
    
    # 提取年份
    year_match = re.search(r'(19|20)\d{2}', filename)
    if year_match:
        info["year"] = int(year_match.group())
    
    # 提取分辨率
    resolution_patterns = [
        r'(2160p|4K|UHD)',
        r'1080p',
        r'720p',
        r'480p',
    ]
    for pattern in resolution_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            info["resolution"] = match.group().upper()
            break
    
    # 提取来源
    source_patterns = [
        r'BluRay|Blu-ray|BD',
        r'WEB-DL|WEBDL|WEB',
        r'HDTV',
        r'DVDRip',
    ]
    for pattern in source_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            info["source"] = match.group()
            break
    
    # 提取编码格式
    codec_patterns = [
        r'[Hh]\.?265|HEVC',
        r'[Hh]\.?264|AVC',
        r'x264',
        r'x265',
    ]
    for pattern in codec_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            info["codec"] = match.group()
            break
    
    # 提取季和集
    season_episode_match = re.search(r'[Ss](\d{1,2})[Ee](\d{1,2})', filename)
    if season_episode_match:
        info["season"] = int(season_episode_match.group(1))
        info["episode"] = int(season_episode_match.group(2))
    
    return info
