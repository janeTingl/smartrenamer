"""
测试媒体库管理
"""
import pytest
from pathlib import Path
from smartrenamer.core.library import MediaLibrary
from smartrenamer.core.scanner import FileScanner
from smartrenamer.core.models import MediaType


class TestMediaLibrary:
    """测试媒体库管理器"""
    
    @pytest.fixture
    def temp_media_dir(self, tmp_path):
        """创建临时媒体目录"""
        # 创建电影文件
        movie_dir = tmp_path / "movies"
        movie_dir.mkdir()
        (movie_dir / "The.Matrix.1999.1080p.BluRay.mkv").write_text("fake movie content" * 1000000)
        (movie_dir / "Inception.2010.720p.WEB-DL.mp4").write_text("fake movie content" * 1000000)
        
        # 创建电视剧文件
        tv_dir = tmp_path / "tv_shows"
        tv_dir.mkdir()
        (tv_dir / "Breaking.Bad.S01E01.Pilot.1080p.mkv").write_text("fake tv content" * 1000000)
        
        return tmp_path
    
    @pytest.fixture
    def library(self, tmp_path):
        """创建媒体库实例"""
        cache_dir = tmp_path / "cache"
        return MediaLibrary(cache_dir=cache_dir, enable_cache=True)
    
    def test_library_initialization(self, library):
        """测试媒体库初始化"""
        assert library.enable_cache is True
        assert len(library.media_files) == 0
        assert len(library.scan_sources) == 0
    
    def test_add_scan_source(self, library, temp_media_dir):
        """测试添加扫描源"""
        library.add_scan_source(temp_media_dir / "movies")
        assert len(library.scan_sources) == 1
        assert temp_media_dir / "movies" in library.scan_sources
    
    def test_remove_scan_source(self, library, temp_media_dir):
        """测试移除扫描源"""
        movie_dir = temp_media_dir / "movies"
        library.add_scan_source(movie_dir)
        library.remove_scan_source(movie_dir)
        assert len(library.scan_sources) == 0
    
    def test_scan_library(self, library, temp_media_dir):
        """测试扫描媒体库"""
        library.add_scan_source(temp_media_dir)
        
        scanner = FileScanner(min_file_size=1000)
        count = library.scan(scanner)
        
        assert count == 3
        assert len(library.media_files) == 3
        assert library.last_scan_time is not None
    
    def test_get_movies(self, library, temp_media_dir):
        """测试获取电影列表"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        movies = library.get_movies()
        assert len(movies) == 2
        
        for movie in movies:
            assert movie.media_type == MediaType.MOVIE
    
    def test_get_tv_shows(self, library, temp_media_dir):
        """测试获取电视剧列表"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        tv_shows = library.get_tv_shows()
        assert len(tv_shows) == 1
        
        for tv_show in tv_shows:
            assert tv_show.media_type == MediaType.TV_SHOW
    
    def test_search_by_title(self, library, temp_media_dir):
        """测试按标题搜索"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        # 精确搜索
        results = library.search_by_title("Matrix")
        assert len(results) > 0
        
        # 模糊搜索
        results = library.search_by_title("break")
        assert len(results) > 0
    
    def test_get_statistics(self, library, temp_media_dir):
        """测试获取统计信息"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        stats = library.get_statistics()
        assert stats["总文件数"] == 3
        assert stats["电影数"] == 2
        assert stats["电视剧数"] == 1
        assert stats["扫描源数"] == 1
    
    def test_save_and_load_cache(self, library, temp_media_dir):
        """测试保存和加载缓存"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        # 保存缓存
        assert library.save_cache() is True
        
        # 创建新的库实例并加载缓存
        new_library = MediaLibrary(cache_dir=library.cache_dir, enable_cache=True)
        assert new_library.load_cache() is True
        
        # 验证数据一致性
        assert len(new_library.media_files) == len(library.media_files)
        assert len(new_library.scan_sources) == len(library.scan_sources)
    
    def test_refresh_library(self, library, temp_media_dir):
        """测试刷新媒体库"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        
        # 首次扫描
        count1 = library.scan(scanner)
        
        # 刷新
        count2 = library.refresh(scanner)
        
        assert count1 == count2
    
    def test_update_library(self, library, temp_media_dir):
        """测试增量更新"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        
        # 首次扫描
        library.scan(scanner)
        initial_count = len(library.media_files)
        
        # 添加新文件
        new_file = temp_media_dir / "movies" / "NewMovie.2023.1080p.mkv"
        new_file.write_text("new movie content" * 1000000)
        
        # 增量更新
        result = library.update(scanner)
        
        # 应该检测到新增文件
        assert result["added"] == 1
        assert len(library.media_files) == initial_count + 1
    
    def test_clear_library(self, library, temp_media_dir):
        """测试清空媒体库"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        library.clear()
        
        assert len(library.media_files) == 0
        assert len(library.scan_sources) == 0
        assert library.last_scan_time is None
    
    def test_clear_cache(self, library, temp_media_dir):
        """测试清除缓存"""
        library.add_scan_source(temp_media_dir)
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        # 保存缓存
        library.save_cache()
        cache_file = library.cache_dir / "media_library.json"
        assert cache_file.exists()
        
        # 清除缓存
        library.clear_cache()
        assert not cache_file.exists()
    
    def test_library_without_cache(self, tmp_path, temp_media_dir):
        """测试禁用缓存的媒体库"""
        library = MediaLibrary(enable_cache=False)
        library.add_scan_source(temp_media_dir)
        
        scanner = FileScanner(min_file_size=1000)
        library.scan(scanner)
        
        # 尝试保存缓存应该返回 False
        assert library.save_cache() is False
