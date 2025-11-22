"""
增强版 TMDB 客户端测试
"""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from smartrenamer.api.tmdb_client_enhanced import (
    EnhancedTMDBClient,
    增强TMDB客户端,
    缓存管理器
)


class TestCacheManager:
    """缓存管理器测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.cache_dir = Path("/tmp/smartrenamer_test_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = 缓存管理器(self.cache_dir, 过期时间=1)
    
    def teardown_method(self):
        """每个测试后的清理"""
        self.cache.清空()
        if self.cache_dir.exists():
            self.cache_dir.rmdir()
    
    def test_设置和获取缓存(self):
        """测试设置和获取缓存"""
        测试数据 = {"title": "The Matrix", "year": 1999}
        self.cache.设置("test_key", 测试数据)
        
        结果 = self.cache.获取("test_key")
        assert 结果 == 测试数据
    
    def test_获取不存在的缓存(self):
        """测试获取不存在的缓存"""
        结果 = self.cache.获取("nonexistent_key")
        assert 结果 is None
    
    def test_清空缓存(self):
        """测试清空缓存"""
        self.cache.设置("key1", {"data": 1})
        self.cache.设置("key2", {"data": 2})
        
        self.cache.清空()
        
        assert self.cache.获取("key1") is None
        assert self.cache.获取("key2") is None


class TestEnhancedTMDBClient:
    """增强版 TMDB 客户端测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 使用模拟的 API key
        self.api_key = "test_api_key_123456"
        self.cache_dir = Path("/tmp/smartrenamer_test_tmdb_cache")
        
        # 使用 patch 来模拟 TMDB API
        self.tmdb_patcher = patch('smartrenamer.api.tmdb_client_enhanced.TMDb')
        self.movie_patcher = patch('smartrenamer.api.tmdb_client_enhanced.Movie')
        self.tv_patcher = patch('smartrenamer.api.tmdb_client_enhanced.TV')
        
        self.mock_tmdb = self.tmdb_patcher.start()
        self.mock_movie = self.movie_patcher.start()
        self.mock_tv = self.tv_patcher.start()
        
        # 创建客户端
        self.client = EnhancedTMDBClient(
            self.api_key,
            缓存目录=self.cache_dir,
            启用缓存=True
        )
    
    def teardown_method(self):
        """每个测试后的清理"""
        self.tmdb_patcher.stop()
        self.movie_patcher.stop()
        self.tv_patcher.stop()
        
        # 清理缓存
        if hasattr(self.client, '缓存') and self.client.缓存:
            self.client.清空缓存()
        if self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir, ignore_errors=True)
    
    def test_初始化(self):
        """测试客户端初始化"""
        assert self.client.启用缓存 is True
        assert self.client.最大重试次数 == 3
        assert self.client.language == "zh-CN"
    
    def test_搜索电影_无缓存(self):
        """测试搜索电影（无缓存）"""
        # 模拟搜索结果
        mock_result = Mock()
        mock_result.__dict__ = {
            "id": 603,
            "title": "黑客帝国",
            "original_title": "The Matrix",
            "release_date": "1999-03-31",
        }
        
        self.client.movie.search = Mock(return_value=[mock_result])
        
        results = self.client.search_movie("The Matrix", year=1999)
        
        assert len(results) > 0
        assert self.client.movie.search.called
    
    def test_搜索电影_使用缓存(self):
        """测试搜索电影（使用缓存）"""
        # 第一次搜索
        mock_result = Mock()
        mock_result.__dict__ = {"id": 603, "title": "The Matrix"}
        self.client.movie.search = Mock(return_value=[mock_result])
        
        results1 = self.client.search_movie("The Matrix")
        
        # 第二次搜索应该从缓存获取
        results2 = self.client.search_movie("The Matrix")
        
        # 验证只调用了一次 API
        assert self.client.movie.search.call_count == 1
    
    def test_搜索电视剧(self):
        """测试搜索电视剧"""
        mock_result = Mock()
        mock_result.__dict__ = {
            "id": 1396,
            "name": "绝命毒师",
            "original_name": "Breaking Bad",
            "first_air_date": "2008-01-20",
        }
        
        self.client.tv.search = Mock(return_value=[mock_result])
        
        results = self.client.search_tv("Breaking Bad", year=2008)
        
        assert len(results) > 0
        assert self.client.tv.search.called
    
    def test_获取电影详情(self):
        """测试获取电影详情"""
        mock_details = Mock()
        mock_details.__dict__ = {
            "id": 603,
            "title": "The Matrix",
            "overview": "A computer hacker learns...",
            "release_date": "1999-03-31",
        }
        
        self.client.movie.details = Mock(return_value=mock_details)
        
        details = self.client.get_movie_details(603)
        
        assert details is not None
        assert details["id"] == 603
        assert self.client.movie.details.called
    
    def test_获取电视剧详情(self):
        """测试获取电视剧详情"""
        mock_details = Mock()
        mock_details.__dict__ = {
            "id": 1396,
            "name": "Breaking Bad",
            "number_of_seasons": 5,
        }
        
        self.client.tv.details = Mock(return_value=mock_details)
        
        details = self.client.get_tv_details(1396)
        
        assert details is not None
        assert details["id"] == 1396
        assert self.client.tv.details.called
    
    def test_重试机制(self):
        """测试 API 请求重试机制"""
        # 模拟前两次失败，第三次成功
        mock_result = Mock()
        mock_result.__dict__ = {"id": 603, "title": "The Matrix"}
        
        self.client.movie.search = Mock(
            side_effect=[
                Exception("Network error"),
                Exception("Timeout"),
                [mock_result]
            ]
        )
        
        results = self.client.search_movie("The Matrix")
        
        # 应该重试并最终成功
        assert len(results) > 0
        assert self.client.movie.search.call_count == 3
    
    def test_重试失败(self):
        """测试所有重试都失败的情况"""
        self.client.movie.search = Mock(
            side_effect=Exception("Persistent error")
        )
        
        # 重试失败后应返回空列表而不是抛出异常
        results = self.client.search_movie("The Matrix")
        assert results == []
    
    def test_年份过滤_电影(self):
        """测试电影年份过滤"""
        mock_result1 = Mock()
        mock_result1.__dict__ = {"id": 1, "title": "Test 1", "release_date": "1999-01-01"}
        
        mock_result2 = Mock()
        mock_result2.__dict__ = {"id": 2, "title": "Test 2", "release_date": "2020-01-01"}
        
        mock_results = [mock_result1, mock_result2]
        
        self.client.movie.search = Mock(return_value=mock_results)
        
        results = self.client.search_movie("Test", year=1999)
        
        # 应该只返回 1999 年的结果
        assert len(results) == 1
        assert results[0]["release_date"].startswith("1999")
    
    def test_清空缓存(self):
        """测试清空缓存功能"""
        # 先添加一些缓存
        mock_result = Mock()
        mock_result.__dict__ = {"id": 603, "title": "The Matrix"}
        self.client.movie.search = Mock(return_value=[mock_result])
        
        self.client.search_movie("The Matrix")
        
        # 清空缓存
        self.client.clear_cache()
        
        # 再次搜索应该调用 API
        self.client.search_movie("The Matrix")
        assert self.client.movie.search.call_count == 2


class Test增强TMDB客户端:
    """测试中文接口"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.api_key = "test_api_key"
        self.cache_dir = Path("/tmp/smartrenamer_test_cn_cache")
        
        with patch('smartrenamer.api.tmdb_client_enhanced.TMDb'), \
             patch('smartrenamer.api.tmdb_client_enhanced.Movie'), \
             patch('smartrenamer.api.tmdb_client_enhanced.TV'):
            self.客户端 = 增强TMDB客户端(
                self.api_key,
                缓存目录=self.cache_dir,
                启用缓存=True
            )
    
    def teardown_method(self):
        """清理"""
        if hasattr(self.客户端, '缓存') and self.客户端.缓存:
            self.客户端.清空缓存()
        if self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir, ignore_errors=True)
    
    def test_中文接口_初始化(self):
        """测试中文接口初始化"""
        assert self.客户端.启用缓存 is True
        assert self.客户端.最大重试次数 == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
