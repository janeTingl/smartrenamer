"""
TMDB API 客户端

提供与 TMDB API 交互的功能
"""
from typing import Optional, List, Dict, Any
from tmdbv3api import TMDb, Movie, TV


class TMDBClient:
    """
    TMDB API 客户端封装类
    
    简化 TMDB API 的调用
    """
    
    def __init__(self, api_key: str, language: str = "zh-CN"):
        """
        初始化 TMDB 客户端
        
        Args:
            api_key: TMDB API 密钥
            language: 语言设置，默认为简体中文
        """
        self.tmdb = TMDb()
        self.tmdb.api_key = api_key
        self.tmdb.language = language
        
        self.movie = Movie()
        self.tv = TV()
    
    def search_movie(self, title: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索电影
        
        Args:
            title: 电影标题
            year: 发行年份（可选）
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            results = self.movie.search(title)
            
            # 如果指定了年份，过滤结果
            if year and results:
                results = [
                    r for r in results
                    if r.get("release_date", "").startswith(str(year))
                ]
            
            return results
        except Exception as e:
            print(f"搜索电影失败: {e}")
            return []
    
    def search_tv(self, title: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        搜索电视剧
        
        Args:
            title: 电视剧标题
            year: 首播年份（可选）
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            results = self.tv.search(title)
            
            # 如果指定了年份，过滤结果
            if year and results:
                results = [
                    r for r in results
                    if r.get("first_air_date", "").startswith(str(year))
                ]
            
            return results
        except Exception as e:
            print(f"搜索电视剧失败: {e}")
            return []
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """
        获取电影详细信息
        
        Args:
            movie_id: 电影 ID
            
        Returns:
            Optional[Dict[str, Any]]: 电影详细信息
        """
        try:
            return self.movie.details(movie_id)
        except Exception as e:
            print(f"获取电影详情失败: {e}")
            return None
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict[str, Any]]:
        """
        获取电视剧详细信息
        
        Args:
            tv_id: 电视剧 ID
            
        Returns:
            Optional[Dict[str, Any]]: 电视剧详细信息
        """
        try:
            return self.tv.details(tv_id)
        except Exception as e:
            print(f"获取电视剧详情失败: {e}")
            return None
