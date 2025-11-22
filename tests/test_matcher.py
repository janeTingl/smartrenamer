"""
智能匹配器测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from smartrenamer.core.matcher import Matcher, 智能匹配器, MatchResult, 匹配结果
from smartrenamer.core.models import MediaFile, MediaType
from smartrenamer.core.parser import FileNameParser
from smartrenamer.api.tmdb_client_enhanced import EnhancedTMDBClient


class TestMatcher:
    """智能匹配器测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 创建模拟的 TMDB 客户端
        self.mock_client = Mock(spec=EnhancedTMDBClient)
        
        # 创建解析器
        self.parser = FileNameParser()
        
        # 创建匹配器
        self.matcher = Matcher(self.mock_client, self.parser)
    
    def test_初始化(self):
        """测试匹配器初始化"""
        assert self.matcher.tmdb客户端 == self.mock_client
        assert self.matcher.解析器 is not None
    
    def test_匹配电影_精确匹配(self):
        """测试电影精确匹配"""
        # 模拟 TMDB 搜索结果
        mock_results = [
            {
                "id": 603,
                "title": "The Matrix",
                "original_title": "The Matrix",
                "release_date": "1999-03-31",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        # 执行匹配
        matches = self.matcher.match_file("The.Matrix.1999.1080p.BluRay.mkv")
        
        # 验证结果
        assert len(matches) > 0
        assert matches[0].媒体类型 == MediaType.MOVIE
        assert matches[0].相似度 >= 0.9  # 应该是高相似度
        assert self.mock_client.搜索电影.called
    
    def test_匹配电影_模糊匹配(self):
        """测试电影模糊匹配"""
        mock_results = [
            {
                "id": 603,
                "title": "The Matrix",
                "original_title": "The Matrix",
                "release_date": "1999-03-31",
            },
            {
                "id": 604,
                "title": "The Matrix Reloaded",
                "original_title": "The Matrix Reloaded",
                "release_date": "2003-05-15",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file("Matrix.1999.1080p.mkv")
        
        # 应该找到多个匹配
        assert len(matches) > 0
        # 第一个应该是最相似的
        assert matches[0].tmdb数据["id"] == 603
    
    def test_匹配电影_年份过滤(self):
        """测试年份过滤功能"""
        mock_results = [
            {
                "id": 603,
                "title": "The Matrix",
                "release_date": "1999-03-31",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file("The.Matrix.1999.1080p.mkv")
        
        # 验证搜索时传入了年份
        self.mock_client.搜索电影.assert_called_once()
        # 检查调用参数
        call_args = self.mock_client.搜索电影.call_args
        # call_args[0] 是位置参数, call_args[1] 是关键字参数
        # 或者使用 call_args.args 和 call_args.kwargs
        if hasattr(call_args, 'kwargs'):
            # Python 3.8+
            assert call_args.args[1] == 1999 or call_args.kwargs.get('年份') == 1999
        else:
            # 检查位置参数
            assert len(call_args[0]) >= 2 and call_args[0][1] == 1999
    
    def test_匹配电视剧_S01E01(self):
        """测试电视剧匹配（S01E01 格式）"""
        mock_results = [
            {
                "id": 1396,
                "name": "Breaking Bad",
                "original_name": "Breaking Bad",
                "first_air_date": "2008-01-20",
            }
        ]
        self.mock_client.搜索电视剧 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file("Breaking.Bad.S01E01.1080p.mkv")
        
        assert len(matches) > 0
        assert matches[0].媒体类型 == MediaType.TV_SHOW
        assert self.mock_client.搜索电视剧.called
    
    def test_匹配电视剧_多个结果(self):
        """测试电视剧返回多个匹配结果"""
        mock_results = [
            {
                "id": 1396,
                "name": "Breaking Bad",
                "first_air_date": "2008-01-20",
            },
            {
                "id": 9999,
                "name": "Breaking Bad: The Movie",
                "first_air_date": "2010-01-01",
            }
        ]
        self.mock_client.搜索电视剧 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file("Breaking.Bad.S01E01.mkv", max_results=5)
        
        # 应该返回多个结果，按相似度排序
        assert len(matches) >= 1
        # 第一个应该是最相似的
        assert "Breaking Bad" in matches[0].tmdb数据["name"]
    
    def test_匹配_无结果(self):
        """测试匹配无结果的情况"""
        self.mock_client.搜索电影 = Mock(return_value=[])
        
        matches = self.matcher.match_file("Unknown.Movie.2099.mkv")
        
        assert len(matches) == 0
    
    def test_匹配_自动确认(self):
        """测试自动确认高相似度匹配"""
        mock_results = [
            {
                "id": 603,
                "title": "The Matrix",
                "original_title": "The Matrix",
                "release_date": "1999-03-31",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file(
            "The.Matrix.1999.1080p.mkv",
            auto_confirm=True
        )
        
        # 如果相似度很高，应该只返回一个结果
        assert len(matches) == 1
        assert matches[0].相似度 >= self.matcher.高相似度
    
    def test_匹配MediaFile对象(self):
        """测试匹配 MediaFile 对象"""
        media_file = MediaFile(
            path=Path("/media/movies/The.Matrix.1999.mkv"),
            original_name="The.Matrix.1999.mkv",
            extension=".mkv"
        )
        
        mock_results = [
            {
                "id": 603,
                "title": "The Matrix",
                "release_date": "1999-03-31",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_media_file(media_file)
        
        assert len(matches) > 0
        assert matches[0].媒体类型 == MediaType.MOVIE
    
    def test_应用匹配到媒体文件_电影(self):
        """测试将电影匹配结果应用到 MediaFile"""
        media_file = MediaFile(
            path=Path("/media/The.Matrix.mkv"),
            original_name="The.Matrix.mkv",
            extension=".mkv"
        )
        
        match = MatchResult(
            tmdb数据={
                "id": 603,
                "title": "The Matrix",
                "original_title": "The Matrix",
                "release_date": "1999-03-31",
            },
            相似度=0.95,
            媒体类型=MediaType.MOVIE,
            匹配原因="精确匹配"
        )
        
        updated_file = self.matcher.apply_match_to_media_file(media_file, match)
        
        assert updated_file.tmdb_id == 603
        assert updated_file.title == "The Matrix"
        assert updated_file.year == 1999
        assert updated_file.media_type == MediaType.MOVIE
        assert updated_file.metadata["match_similarity"] == 0.95
    
    def test_应用匹配到媒体文件_电视剧(self):
        """测试将电视剧匹配结果应用到 MediaFile"""
        media_file = MediaFile(
            path=Path("/media/Breaking.Bad.S01E01.mkv"),
            original_name="Breaking.Bad.S01E01.mkv",
            extension=".mkv"
        )
        
        match = MatchResult(
            tmdb数据={
                "id": 1396,
                "name": "Breaking Bad",
                "original_name": "Breaking Bad",
                "first_air_date": "2008-01-20",
            },
            相似度=0.92,
            媒体类型=MediaType.TV_SHOW,
            匹配原因="标题匹配"
        )
        
        updated_file = self.matcher.apply_match_to_media_file(media_file, match)
        
        assert updated_file.tmdb_id == 1396
        assert updated_file.title == "Breaking Bad"
        assert updated_file.year == 2008
        assert updated_file.media_type == MediaType.TV_SHOW
    
    def test_相似度计算_完全匹配(self):
        """测试相似度计算 - 完全匹配"""
        相似度 = self.matcher._字符串相似度("the matrix", "the matrix")
        assert 相似度 == 1.0
    
    def test_相似度计算_部分匹配(self):
        """测试相似度计算 - 部分匹配"""
        相似度 = self.matcher._字符串相似度("the matrix", "matrix")
        assert 0.5 < 相似度 < 1.0
    
    def test_相似度计算_不匹配(self):
        """测试相似度计算 - 不匹配"""
        相似度 = self.matcher._字符串相似度("the matrix", "inception")
        assert 相似度 < 0.5
    
    def test_相似度计算_空字符串(self):
        """测试相似度计算 - 空字符串"""
        相似度 = self.matcher._字符串相似度("", "test")
        assert 相似度 == 0.0
    
    def test_最小相似度过滤(self):
        """测试最小相似度过滤"""
        # 创建低相似度的结果
        mock_results = [
            {
                "id": 999,
                "title": "Completely Different Movie",
                "release_date": "2020-01-01",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        matches = self.matcher.match_file("The.Matrix.1999.mkv")
        
        # 低相似度的结果应该被过滤
        if len(matches) > 0:
            assert matches[0].相似度 >= self.matcher.最小相似度


class Test智能匹配器:
    """测试中文接口"""
    
    def setup_method(self):
        """设置"""
        self.mock_client = Mock(spec=EnhancedTMDBClient)
        self.匹配器 = 智能匹配器(self.mock_client)
    
    def test_中文接口_匹配电影(self):
        """测试中文接口匹配电影"""
        mock_results = [
            {
                "id": 1,
                "title": "让子弹飞",
                "release_date": "2010-12-16",
            }
        ]
        self.mock_client.搜索电影 = Mock(return_value=mock_results)
        
        匹配列表 = self.匹配器.匹配文件("让子弹飞.2010.1080p.mkv")
        
        assert len(匹配列表) > 0
        assert 匹配列表[0].媒体类型 == MediaType.MOVIE


class TestMatchResult:
    """匹配结果测试"""
    
    def test_匹配结果创建(self):
        """测试创建匹配结果"""
        result = MatchResult(
            tmdb数据={"id": 603, "title": "The Matrix"},
            相似度=0.95,
            媒体类型=MediaType.MOVIE,
            匹配原因="精确匹配"
        )
        
        assert result.tmdb数据["id"] == 603
        assert result.相似度 == 0.95
        assert result.媒体类型 == MediaType.MOVIE
    
    def test_匹配结果转字典(self):
        """测试匹配结果转换为字典"""
        result = MatchResult(
            tmdb数据={"id": 603, "title": "The Matrix"},
            相似度=0.95,
            媒体类型=MediaType.MOVIE,
            匹配原因="精确匹配"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["tmdb_data"]["id"] == 603
        assert result_dict["similarity"] == 0.95
        assert result_dict["media_type"] == "movie"
        assert result_dict["match_reason"] == "精确匹配"
    
    def test_匹配结果字符串表示(self):
        """测试匹配结果的字符串表示"""
        result = MatchResult(
            tmdb数据={"id": 603, "title": "The Matrix"},
            相似度=0.95,
            媒体类型=MediaType.MOVIE,
            匹配原因="精确匹配"
        )
        
        repr_str = repr(result)
        assert "The Matrix" in repr_str
        assert "0.95" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
