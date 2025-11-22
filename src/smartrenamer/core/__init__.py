"""
核心业务逻辑模块

包含媒体文件处理、重命名规则和配置管理等核心功能
"""
from smartrenamer.core.models import (
    MediaFile,
    MediaType,
    RenameRule,
    DEFAULT_MOVIE_RULE,
    DEFAULT_TV_RULE,
)
from smartrenamer.core.config import Config, get_config, set_config
from smartrenamer.core.scanner import FileScanner
from smartrenamer.core.library import MediaLibrary
from smartrenamer.core.parser import FileNameParser, 文件名解析器
from smartrenamer.core.matcher import Matcher, MatchResult, 智能匹配器, 匹配结果
from smartrenamer.core.renamer import (
    Renamer,
    重命名器,
    RenameRuleManager,
    重命名规则管理器,
    RenameHistory,
    重命名历史记录,
    create_predefined_rule,
    创建预定义规则,
    PREDEFINED_TEMPLATES,
    预定义模板,
)

__all__ = [
    "MediaFile",
    "MediaType",
    "RenameRule",
    "DEFAULT_MOVIE_RULE",
    "DEFAULT_TV_RULE",
    "Config",
    "get_config",
    "set_config",
    "FileScanner",
    "MediaLibrary",
    "FileNameParser",
    "文件名解析器",
    "Matcher",
    "MatchResult",
    "智能匹配器",
    "匹配结果",
    "Renamer",
    "重命名器",
    "RenameRuleManager",
    "重命名规则管理器",
    "RenameHistory",
    "重命名历史记录",
    "create_predefined_rule",
    "创建预定义规则",
    "PREDEFINED_TEMPLATES",
    "预定义模板",
]
