"""
SmartRenamer - 智能媒体文件重命名工具

这是一个基于 TMDB API 的媒体文件智能重命名工具，
支持电影和电视剧文件的自动识别和规范化命名。
"""

__version__ = "0.1.0"
__author__ = "SmartRenamer Team"

from smartrenamer.core.models import MediaFile, MediaType, RenameRule
from smartrenamer.core.config import Config

__all__ = [
    "MediaFile",
    "MediaType",
    "RenameRule",
    "Config",
    "__version__",
]
