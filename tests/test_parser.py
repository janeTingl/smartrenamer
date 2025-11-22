"""
文件名解析器测试
"""
import pytest
from pathlib import Path
from smartrenamer.core.parser import FileNameParser, 文件名解析器
from smartrenamer.core.models import MediaType


class TestFileNameParser:
    """文件名解析器测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.parser = FileNameParser()
    
    def test_解析电影_标准格式(self):
        """测试解析标准格式的电影文件名"""
        result = self.parser.parse("The.Matrix.1999.1080p.BluRay.x264.mkv")
        
        assert result["media_type"] == MediaType.MOVIE
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999
        assert result["resolution"] == "1080P"
        assert result["source"] == "BluRay"
        assert result["codec"] == "H264"
        assert result["season"] is None
        assert result["episode"] is None
    
    def test_解析电影_中文标题(self):
        """测试解析中文标题的电影"""
        result = self.parser.parse("让子弹飞.2010.1080p.WEB-DL.H265.mkv")
        
        assert result["media_type"] == MediaType.MOVIE
        assert result["title"] == "让子弹飞"
        assert result["year"] == 2010
        assert result["resolution"] == "1080P"
        assert result["source"] == "WEB-DL"
        assert result["codec"] == "H265"
    
    def test_解析电影_无年份(self):
        """测试解析无年份信息的电影"""
        result = self.parser.parse("Inception.1080p.BluRay.mkv")
        
        assert result["media_type"] == MediaType.MOVIE
        assert result["title"] == "Inception"
        assert result["year"] is None
        assert result["resolution"] == "1080P"
    
    def test_解析电影_4K格式(self):
        """测试解析 4K 格式的电影"""
        result = self.parser.parse("Avatar.2009.4K.UHD.BluRay.x265.mkv")
        
        assert result["media_type"] == MediaType.MOVIE
        assert result["title"] == "Avatar"
        assert result["year"] == 2009
        assert result["resolution"] == "2160p"  # 4K 应该被标准化为 2160p
        assert result["codec"] == "H265"
    
    def test_解析电视剧_S01E01格式(self):
        """测试解析 S01E01 格式的电视剧"""
        result = self.parser.parse("Breaking.Bad.S01E01.Pilot.1080p.WEB-DL.mkv")
        
        assert result["media_type"] == MediaType.TV_SHOW
        assert result["title"] == "Breaking Bad"
        assert result["season"] == 1
        assert result["episode"] == 1
        assert result["resolution"] == "1080P"
        assert result["source"] == "WEB-DL"
    
    def test_解析电视剧_1x01格式(self):
        """测试解析 1x01 格式的电视剧"""
        result = self.parser.parse("Game.of.Thrones.1x01.Winter.is.Coming.720p.mkv")
        
        assert result["media_type"] == MediaType.TV_SHOW
        assert result["title"] == "Game of Thrones"
        assert result["season"] == 1
        assert result["episode"] == 1
        assert result["resolution"] == "720P"
    
    def test_解析电视剧_中文季集(self):
        """测试解析中文季集格式"""
        result = self.parser.parse("权力的游戏.第1季第1集.1080p.mkv")
        
        assert result["media_type"] == MediaType.TV_SHOW
        assert result["title"] == "权力的游戏"
        assert result["season"] == 1
        assert result["episode"] == 1
    
    def test_解析电视剧_多集(self):
        """测试解析多位数的季集"""
        result = self.parser.parse("The.Walking.Dead.S10E15.1080p.WEB-DL.mkv")
        
        assert result["media_type"] == MediaType.TV_SHOW
        assert result["season"] == 10
        assert result["episode"] == 15
    
    def test_解析_带方括号标签(self):
        """测试解析带方括号标签的文件名"""
        result = self.parser.parse("[发布组]The.Matrix.1999.1080p.BluRay.mkv")
        
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999
    
    def test_解析_带圆括号(self):
        """测试解析带圆括号的文件名"""
        result = self.parser.parse("Inception (2010) 1080p BluRay.mkv")
        
        assert result["title"] == "Inception"
        assert result["year"] == 2010
    
    def test_解析_复杂文件名(self):
        """测试解析复杂的文件名"""
        result = self.parser.parse(
            "[字幕组]The.Dark.Knight.2008.EXTENDED.1080p.BluRay.x264.DTS-HD.mkv"
        )
        
        assert result["title"] == "The Dark Knight"
        assert result["year"] == 2008
        assert result["resolution"] == "1080P"
        assert result["codec"] == "H264"
    
    def test_解析_路径格式(self):
        """测试解析包含完整路径的文件名"""
        result = self.parser.parse(
            "/media/movies/The.Matrix.1999.1080p.BluRay.mkv"
        )
        
        assert result["title"] == "The Matrix"
        assert result["year"] == 1999
    
    def test_解析_Path对象(self):
        """测试解析 Path 对象"""
        path = Path("/media/movies/Inception.2010.1080p.mkv")
        result = self.parser.parse(path)
        
        assert result["title"] == "Inception"
        assert result["year"] == 2010
    
    def test_解析_空文件名(self):
        """测试解析空文件名"""
        result = self.parser.parse("")
        
        assert result["title"] == "Unknown"
        assert result["media_type"] in [MediaType.MOVIE, MediaType.UNKNOWN]


class Test文件名解析器:
    """测试中文接口"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.解析器 = 文件名解析器()
    
    def test_中文接口_解析电影(self):
        """测试中文接口解析电影"""
        结果 = self.解析器.解析("盗梦空间.2010.1080p.BluRay.mkv")
        
        assert 结果["媒体类型"] == MediaType.MOVIE
        assert 结果["标题"] == "盗梦空间"
        assert 结果["年份"] == 2010
        assert 结果["分辨率"] == "1080P"
    
    def test_中文接口_解析电视剧(self):
        """测试中文接口解析电视剧"""
        结果 = self.解析器.解析("权力的游戏.S01E01.1080p.mkv")
        
        assert 结果["媒体类型"] == MediaType.TV_SHOW
        assert 结果["季数"] == 1
        assert 结果["集数"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
