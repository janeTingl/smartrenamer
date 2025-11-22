"""
测试文件工具函数
"""
import pytest
from pathlib import Path
from smartrenamer.utils.file_utils import (
    is_supported_file,
    sanitize_filename,
    format_file_size,
    extract_info_from_filename,
)


class TestFileUtils:
    """测试文件工具函数"""
    
    def test_is_supported_file(self):
        """测试文件格式支持检查"""
        supported_exts = [".mkv", ".mp4", ".avi"]
        
        assert is_supported_file(Path("movie.mkv"), supported_exts)
        assert is_supported_file(Path("movie.mp4"), supported_exts)
        assert not is_supported_file(Path("movie.txt"), supported_exts)
    
    def test_sanitize_filename(self):
        """测试文件名清理"""
        # 测试移除非法字符
        result = sanitize_filename('movie<>:"/\\|?*.mkv')
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        
        # 测试清理多余空格
        result = sanitize_filename("movie   name.mkv")
        assert "   " not in result
    
    def test_format_file_size(self):
        """测试文件大小格式化"""
        assert "1.00 KB" in format_file_size(1024)
        assert "1.00 MB" in format_file_size(1024 * 1024)
        assert "1.00 GB" in format_file_size(1024 * 1024 * 1024)
    
    def test_extract_year_from_filename(self):
        """测试从文件名提取年份"""
        info = extract_info_from_filename("The.Matrix.1999.1080p.BluRay.mkv")
        assert info["year"] == 1999
    
    def test_extract_resolution_from_filename(self):
        """测试从文件名提取分辨率"""
        info = extract_info_from_filename("Movie.2020.1080p.WEB-DL.mkv")
        assert info["resolution"] == "1080P"
        
        info = extract_info_from_filename("Movie.2020.720p.mkv")
        assert info["resolution"] == "720P"
    
    def test_extract_source_from_filename(self):
        """测试从文件名提取来源"""
        info = extract_info_from_filename("Movie.2020.1080p.BluRay.mkv")
        assert info["source"] is not None
        
        info = extract_info_from_filename("Movie.2020.WEB-DL.mkv")
        assert info["source"] is not None
    
    def test_extract_season_episode_from_filename(self):
        """测试从文件名提取季集信息"""
        info = extract_info_from_filename("Show.S01E05.Episode.Name.mkv")
        assert info["season"] == 1
        assert info["episode"] == 5
        
        info = extract_info_from_filename("Show.s02e10.mkv")
        assert info["season"] == 2
        assert info["episode"] == 10
