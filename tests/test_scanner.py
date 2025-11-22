"""
测试文件扫描器
"""
import pytest
from pathlib import Path
from smartrenamer.core.scanner import FileScanner
from smartrenamer.core.models import MediaType


class TestFileScanner:
    """测试文件扫描器"""
    
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
        (tv_dir / "Game.of.Thrones.S03E09.1080p.BluRay.mkv").write_text("fake tv content" * 1000000)
        
        # 创建不支持的文件
        (tmp_path / "readme.txt").write_text("readme content")
        
        # 创建小文件（应该被跳过）
        (movie_dir / "small.mkv").write_text("small")
        
        # 创建应该排除的目录
        sample_dir = movie_dir / "Sample"
        sample_dir.mkdir()
        (sample_dir / "sample.mkv").write_text("sample content" * 1000000)
        
        return tmp_path
    
    def test_scanner_initialization(self):
        """测试扫描器初始化"""
        scanner = FileScanner()
        assert scanner.supported_extensions == FileScanner.DEFAULT_EXTENSIONS
        assert scanner.min_file_size == 10 * 1024 * 1024
    
    def test_scanner_custom_settings(self):
        """测试自定义扫描器设置"""
        custom_extensions = [".mkv", ".mp4"]
        custom_min_size = 5 * 1024 * 1024
        
        scanner = FileScanner(
            supported_extensions=custom_extensions,
            min_file_size=custom_min_size
        )
        
        assert scanner.supported_extensions == custom_extensions
        assert scanner.min_file_size == custom_min_size
    
    def test_scan_directory(self, temp_media_dir):
        """测试目录扫描"""
        scanner = FileScanner(min_file_size=1000)  # 降低最小文件大小限制
        media_files = scanner.scan(temp_media_dir)
        
        # 应该找到 4 个有效的媒体文件（不包括 sample 目录和小文件）
        assert len(media_files) == 4
        
        # 检查统计信息
        stats = scanner.get_statistics()
        assert stats["找到媒体文件数"] == 4
    
    def test_scan_movie_detection(self, temp_media_dir):
        """测试电影识别"""
        scanner = FileScanner(min_file_size=1000)
        media_files = scanner.scan(temp_media_dir / "movies")
        
        # 应该找到 2 个电影
        movies = [mf for mf in media_files if mf.media_type == MediaType.MOVIE]
        assert len(movies) == 2
        
        # 检查第一个电影的信息
        matrix = next((mf for mf in movies if "Matrix" in mf.title), None)
        assert matrix is not None
        assert matrix.year == 1999
        assert matrix.resolution == "1080P"
    
    def test_scan_tv_show_detection(self, temp_media_dir):
        """测试电视剧识别"""
        scanner = FileScanner(min_file_size=1000)
        media_files = scanner.scan(temp_media_dir / "tv_shows")
        
        # 应该找到 2 个电视剧
        tv_shows = [mf for mf in media_files if mf.media_type == MediaType.TV_SHOW]
        assert len(tv_shows) == 2
        
        # 检查季集信息
        breaking_bad = next((mf for mf in tv_shows if "Breaking" in mf.title), None)
        assert breaking_bad is not None
        assert breaking_bad.season_number == 1
        assert breaking_bad.episode_number == 1
    
    def test_exclude_directories(self, temp_media_dir):
        """测试排除目录功能"""
        scanner = FileScanner(min_file_size=1000)
        media_files = scanner.scan(temp_media_dir / "movies")
        
        # Sample 目录中的文件不应该被包含
        sample_files = [mf for mf in media_files if "Sample" in str(mf.path)]
        assert len(sample_files) == 0
    
    def test_file_size_filtering(self, temp_media_dir):
        """测试文件大小过滤"""
        # 使用较大的最小文件大小
        scanner = FileScanner(min_file_size=50 * 1024 * 1024)
        media_files = scanner.scan(temp_media_dir)
        
        # 所有文件都小于 50MB，应该找不到任何文件
        assert len(media_files) == 0
    
    def test_max_depth_limitation(self, temp_media_dir):
        """测试最大深度限制"""
        # 创建深层嵌套目录
        deep_dir = temp_media_dir / "level1" / "level2" / "level3"
        deep_dir.mkdir(parents=True)
        (deep_dir / "deep.movie.2020.mkv").write_text("deep content" * 1000000)
        
        # 限制深度为 1
        scanner = FileScanner(min_file_size=1000, max_depth=1)
        media_files = scanner.scan(temp_media_dir)
        
        # 深层文件不应该被找到
        deep_files = [mf for mf in media_files if "level3" in str(mf.path)]
        assert len(deep_files) == 0
    
    def test_progress_callback(self, temp_media_dir):
        """测试进度回调"""
        callback_calls = []
        
        def progress_callback(current_file, scanned, found):
            callback_calls.append({
                "file": current_file,
                "scanned": scanned,
                "found": found
            })
        
        scanner = FileScanner(min_file_size=1000)
        scanner.scan(temp_media_dir, progress_callback=progress_callback)
        
        # 应该有回调调用
        assert len(callback_calls) > 0
    
    def test_title_extraction(self, temp_media_dir):
        """测试标题提取"""
        scanner = FileScanner(min_file_size=1000)
        media_files = scanner.scan(temp_media_dir / "movies")
        
        # 检查标题提取
        for mf in media_files:
            assert mf.title is not None
            assert len(mf.title) > 0
            # 标题不应该包含年份、分辨率等信息
            assert "1080p" not in mf.title
            assert "720p" not in mf.title
    
    def test_scan_nonexistent_directory(self):
        """测试扫描不存在的目录"""
        scanner = FileScanner()
        
        with pytest.raises(FileNotFoundError):
            scanner.scan(Path("/nonexistent/path"))
