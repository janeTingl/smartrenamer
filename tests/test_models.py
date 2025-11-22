"""
测试核心数据模型
"""
import pytest
from pathlib import Path
from smartrenamer.core.models import MediaFile, MediaType, RenameRule, DEFAULT_MOVIE_RULE


class TestMediaFile:
    """测试 MediaFile 类"""
    
    def test_create_media_file(self):
        """测试创建媒体文件对象"""
        media_file = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
        )
        
        assert media_file.path == Path("/test/movie.mkv")
        assert media_file.original_name == "movie.mkv"
        assert media_file.extension == ".mkv"
        assert media_file.media_type == MediaType.UNKNOWN
    
    def test_media_file_with_metadata(self):
        """测试带元数据的媒体文件"""
        media_file = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="黑客帝国",
            year=1999,
            resolution="1080p",
        )
        
        assert media_file.is_movie
        assert not media_file.is_tv_show
        assert media_file.title == "黑客帝国"
        assert media_file.year == 1999
    
    def test_media_file_to_dict(self):
        """测试转换为字典"""
        media_file = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
        )
        
        data = media_file.to_dict()
        assert isinstance(data, dict)
        assert data["original_name"] == "movie.mkv"
        assert data["media_type"] == "unknown"


class TestRenameRule:
    """测试 RenameRule 类"""
    
    def test_default_movie_rule(self):
        """测试默认电影规则"""
        assert DEFAULT_MOVIE_RULE.name == "默认电影规则"
        assert DEFAULT_MOVIE_RULE.media_type == MediaType.MOVIE
        assert DEFAULT_MOVIE_RULE.example is not None
    
    def test_apply_rule_to_movie(self):
        """测试应用规则到电影文件"""
        media_file = MediaFile(
            path=Path("/test/movie.mkv"),
            original_name="movie.mkv",
            extension=".mkv",
            media_type=MediaType.MOVIE,
            title="黑客帝国",
            year=1999,
            resolution="1080p",
        )
        
        new_name = DEFAULT_MOVIE_RULE.apply(media_file)
        
        assert "黑客帝国" in new_name or "Matrix" in new_name
        assert "1999" in new_name
        assert "1080p" in new_name
        assert new_name.endswith(".mkv")
    
    def test_rename_rule_to_dict(self):
        """测试规则转换为字典"""
        data = DEFAULT_MOVIE_RULE.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "默认电影规则"
        assert data["media_type"] == "movie"


def test_media_type_enum():
    """测试媒体类型枚举"""
    assert MediaType.MOVIE.value == "movie"
    assert MediaType.TV_SHOW.value == "tv_show"
    assert MediaType.UNKNOWN.value == "unknown"
