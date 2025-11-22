"""
核心数据模型

定义媒体文件和重命名规则的数据结构
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MediaType(Enum):
    """媒体类型枚举"""
    MOVIE = "movie"
    TV_SHOW = "tv_show"
    UNKNOWN = "unknown"


@dataclass
class MediaFile:
    """
    媒体文件数据模型
    
    表示一个需要重命名的媒体文件及其元数据
    """
    # 文件基本信息
    path: Path
    original_name: str
    extension: str
    size: int = 0
    
    # 媒体类型
    media_type: MediaType = MediaType.UNKNOWN
    
    # TMDB 元数据
    tmdb_id: Optional[int] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    year: Optional[int] = None
    
    # 电视剧特有字段
    season_number: Optional[int] = None
    episode_number: Optional[int] = None
    episode_title: Optional[str] = None
    
    # 额外信息
    resolution: Optional[str] = None  # 例如: 1080p, 4K
    source: Optional[str] = None  # 例如: BluRay, WEB-DL
    codec: Optional[str] = None  # 例如: H264, H265
    
    # 重命名结果
    new_name: Optional[str] = None
    rename_status: str = "pending"  # pending, success, failed
    error_message: Optional[str] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """初始化后处理"""
        if isinstance(self.path, str):
            self.path = Path(self.path)
        if not self.original_name:
            self.original_name = self.path.name
        if not self.extension:
            self.extension = self.path.suffix
    
    @property
    def is_movie(self) -> bool:
        """判断是否为电影"""
        return self.media_type == MediaType.MOVIE
    
    @property
    def is_tv_show(self) -> bool:
        """判断是否为电视剧"""
        return self.media_type == MediaType.TV_SHOW
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "path": str(self.path),
            "original_name": self.original_name,
            "extension": self.extension,
            "size": self.size,
            "media_type": self.media_type.value,
            "tmdb_id": self.tmdb_id,
            "title": self.title,
            "original_title": self.original_title,
            "year": self.year,
            "season_number": self.season_number,
            "episode_number": self.episode_number,
            "episode_title": self.episode_title,
            "resolution": self.resolution,
            "source": self.source,
            "codec": self.codec,
            "new_name": self.new_name,
            "rename_status": self.rename_status,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RenameRule:
    """
    重命名规则数据模型
    
    定义文件重命名的模板和规则
    """
    name: str
    description: str
    template: str
    media_type: MediaType
    
    # 规则选项
    use_original_title: bool = False
    include_year: bool = True
    include_quality: bool = True
    include_source: bool = True
    include_codec: bool = False
    
    # 格式选项
    separator: str = "."
    space_replacement: str = "."
    
    # 示例
    example: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.example:
            self.example = self._generate_example()
    
    def _generate_example(self) -> str:
        """生成示例文件名"""
        if self.media_type == MediaType.MOVIE:
            return "The.Matrix.1999.1080p.BluRay.x264.mkv"
        elif self.media_type == MediaType.TV_SHOW:
            return "Breaking.Bad.S01E01.Pilot.1080p.WEB-DL.x264.mkv"
        return "example.mkv"
    
    def apply(self, media_file: MediaFile) -> str:
        """
        应用规则到媒体文件
        
        Args:
            media_file: 媒体文件对象
            
        Returns:
            str: 新的文件名
        """
        from jinja2 import Template
        
        # 准备模板变量
        context = {
            "title": media_file.title or "Unknown",
            "original_title": media_file.original_title,
            "year": media_file.year,
            "season": media_file.season_number,
            "episode": media_file.episode_number,
            "episode_title": media_file.episode_title,
            "resolution": media_file.resolution,
            "source": media_file.source,
            "codec": media_file.codec,
            "separator": self.separator,
        }
        
        # 渲染模板
        template = Template(self.template)
        new_name = template.render(**context)
        
        # 替换空格
        if self.space_replacement:
            new_name = new_name.replace(" ", self.space_replacement)
        
        # 添加扩展名
        new_name += media_file.extension
        
        return new_name
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "media_type": self.media_type.value,
            "use_original_title": self.use_original_title,
            "include_year": self.include_year,
            "include_quality": self.include_quality,
            "include_source": self.include_source,
            "include_codec": self.include_codec,
            "separator": self.separator,
            "space_replacement": self.space_replacement,
            "example": self.example,
        }


# 预定义的重命名规则
DEFAULT_MOVIE_RULE = RenameRule(
    name="默认电影规则",
    description="标准电影文件命名格式",
    template="{{ title }}{{ separator }}{{ year }}{{ separator }}{{ resolution }}",
    media_type=MediaType.MOVIE,
)

DEFAULT_TV_RULE = RenameRule(
    name="默认电视剧规则",
    description="标准电视剧文件命名格式",
    template="{{ title }}{{ separator }}S{{ '%02d'|format(season) }}E{{ '%02d'|format(episode) }}{{ separator }}{{ episode_title }}{{ separator }}{{ resolution }}",
    media_type=MediaType.TV_SHOW,
)
