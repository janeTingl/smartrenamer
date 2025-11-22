"""
增强版 TMDB API 客户端

提供缓存、重试机制和更丰富的 API 功能
"""
import time
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
from tmdbv3api import TMDb, Movie, TV, Season, Episode

# 配置日志
logger = logging.getLogger(__name__)


class 缓存管理器:
    """
    简单的文件缓存管理器
    """
    
    def __init__(self, 缓存目录: Path, 过期时间: int = 7):
        """
        初始化缓存管理器
        
        Args:
            缓存目录: 缓存文件存储目录
            过期时间: 缓存过期时间（天），默认7天
        """
        self.缓存目录 = 缓存目录
        self.过期时间 = timedelta(days=过期时间)
        self.缓存目录.mkdir(parents=True, exist_ok=True)
    
    def _获取缓存路径(self, 键: str) -> Path:
        """获取缓存文件路径"""
        # 使用 hash 避免文件名过长或包含非法字符
        import hashlib
        键哈希 = hashlib.md5(键.encode()).hexdigest()
        return self.缓存目录 / f"{键哈希}.json"
    
    def 获取(self, 键: str) -> Optional[Any]:
        """
        从缓存中获取数据
        
        Args:
            键: 缓存键
            
        Returns:
            Optional[Any]: 缓存的数据，如果不存在或过期则返回 None
        """
        缓存路径 = self._获取缓存路径(键)
        
        if not 缓存路径.exists():
            return None
        
        try:
            with open(缓存路径, 'r', encoding='utf-8') as f:
                缓存数据 = json.load(f)
            
            # 检查是否过期
            创建时间 = datetime.fromisoformat(缓存数据['创建时间'])
            if datetime.now() - 创建时间 > self.过期时间:
                logger.debug(f"缓存已过期: {键}")
                缓存路径.unlink()
                return None
            
            logger.debug(f"从缓存加载: {键}")
            return 缓存数据['数据']
            
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
    
    def 设置(self, 键: str, 数据: Any) -> None:
        """
        保存数据到缓存
        
        Args:
            键: 缓存键
            数据: 要缓存的数据
        """
        缓存路径 = self._获取缓存路径(键)
        
        try:
            缓存数据 = {
                '创建时间': datetime.now().isoformat(),
                '数据': 数据
            }
            
            with open(缓存路径, 'w', encoding='utf-8') as f:
                json.dump(缓存数据, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"保存到缓存: {键}")
            
        except Exception as e:
            logger.warning(f"写入缓存失败: {e}")
    
    def 清空(self) -> None:
        """清空所有缓存"""
        for 缓存文件 in self.缓存目录.glob("*.json"):
            try:
                缓存文件.unlink()
            except Exception as e:
                logger.warning(f"删除缓存文件失败: {e}")


class 增强TMDB客户端:
    """
    增强版 TMDB API 客户端
    
    提供缓存、重试机制和更丰富的功能
    """
    
    def __init__(
        self,
        api_key: str,
        language: str = "zh-CN",
        缓存目录: Optional[Path] = None,
        启用缓存: bool = True,
        最大重试次数: int = 3,
        重试延迟: float = 1.0
    ):
        """
        初始化增强版 TMDB 客户端
        
        Args:
            api_key: TMDB API 密钥
            language: 语言设置，默认为简体中文
            缓存目录: 缓存目录路径，默认为 ~/.smartrenamer/cache/tmdb
            启用缓存: 是否启用缓存
            最大重试次数: API 请求失败时的最大重试次数
            重试延迟: 重试之间的延迟时间（秒）
        """
        # 初始化 TMDB API
        self.tmdb = TMDb()
        self.tmdb.api_key = api_key
        self.tmdb.language = language
        
        self.movie = Movie()
        self.tv = TV()
        self.season = Season()
        self.episode = Episode()
        
        # 配置参数
        self.language = language
        self.最大重试次数 = 最大重试次数
        self.重试延迟 = 重试延迟
        
        # 初始化缓存
        self.启用缓存 = 启用缓存
        if 启用缓存:
            if 缓存目录 is None:
                缓存目录 = Path.home() / ".smartrenamer" / "cache" / "tmdb"
            self.缓存 = 缓存管理器(缓存目录)
        else:
            self.缓存 = None
    
    def _带重试执行(self, 函数, *args, **kwargs) -> Any:
        """
        带重试机制执行函数
        
        Args:
            函数: 要执行的函数
            *args, **kwargs: 函数参数
            
        Returns:
            Any: 函数返回值
            
        Raises:
            Exception: 所有重试都失败后抛出最后一个异常
        """
        最后异常 = None
        
        for 尝试次数 in range(self.最大重试次数):
            try:
                return 函数(*args, **kwargs)
            except Exception as e:
                最后异常 = e
                logger.warning(f"API 请求失败 (尝试 {尝试次数 + 1}/{self.最大重试次数}): {e}")
                
                if 尝试次数 < self.最大重试次数 - 1:
                    time.sleep(self.重试延迟 * (尝试次数 + 1))  # 指数退避
        
        logger.error(f"API 请求失败，已达最大重试次数: {最后异常}")
        raise 最后异常
    
    def 搜索电影(
        self,
        标题: str,
        年份: Optional[int] = None,
        使用缓存: bool = True
    ) -> List[Dict[str, Any]]:
        """
        搜索电影
        
        Args:
            标题: 电影标题
            年份: 发行年份（可选）
            使用缓存: 是否使用缓存
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 生成缓存键
        缓存键 = f"movie_search:{标题}:{年份}"
        
        # 尝试从缓存加载
        if self.启用缓存 and 使用缓存 and self.缓存:
            缓存结果 = self.缓存.获取(缓存键)
            if 缓存结果 is not None:
                return 缓存结果
        
        # 执行搜索
        try:
            结果 = self._带重试执行(self.movie.search, 标题)
            
            # 转换为字典列表
            结果列表 = [self._电影对象转字典(r) for r in 结果] if 结果 else []
            
            # 如果指定了年份，过滤结果
            if 年份 and 结果列表:
                结果列表 = [
                    r for r in 结果列表
                    if r.get("release_date", "").startswith(str(年份))
                ]
            
            # 保存到缓存
            if self.启用缓存 and self.缓存:
                self.缓存.设置(缓存键, 结果列表)
            
            logger.info(f"搜索电影 '{标题}' 找到 {len(结果列表)} 个结果")
            return 结果列表
            
        except Exception as e:
            logger.error(f"搜索电影失败: {e}")
            return []
    
    def 搜索电视剧(
        self,
        标题: str,
        年份: Optional[int] = None,
        使用缓存: bool = True
    ) -> List[Dict[str, Any]]:
        """
        搜索电视剧
        
        Args:
            标题: 电视剧标题
            年份: 首播年份（可选）
            使用缓存: 是否使用缓存
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 生成缓存键
        缓存键 = f"tv_search:{标题}:{年份}"
        
        # 尝试从缓存加载
        if self.启用缓存 and 使用缓存 and self.缓存:
            缓存结果 = self.缓存.获取(缓存键)
            if 缓存结果 is not None:
                return 缓存结果
        
        # 执行搜索
        try:
            结果 = self._带重试执行(self.tv.search, 标题)
            
            # 转换为字典列表
            结果列表 = [self._电视剧对象转字典(r) for r in 结果] if 结果 else []
            
            # 如果指定了年份，过滤结果
            if 年份 and 结果列表:
                结果列表 = [
                    r for r in 结果列表
                    if r.get("first_air_date", "").startswith(str(年份))
                ]
            
            # 保存到缓存
            if self.启用缓存 and self.缓存:
                self.缓存.设置(缓存键, 结果列表)
            
            logger.info(f"搜索电视剧 '{标题}' 找到 {len(结果列表)} 个结果")
            return 结果列表
            
        except Exception as e:
            logger.error(f"搜索电视剧失败: {e}")
            return []
    
    def 获取电影详情(
        self,
        电影id: int,
        使用缓存: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        获取电影详细信息
        
        Args:
            电影id: 电影 ID
            使用缓存: 是否使用缓存
            
        Returns:
            Optional[Dict[str, Any]]: 电影详细信息
        """
        # 生成缓存键
        缓存键 = f"movie_details:{电影id}"
        
        # 尝试从缓存加载
        if self.启用缓存 and 使用缓存 and self.缓存:
            缓存结果 = self.缓存.获取(缓存键)
            if 缓存结果 is not None:
                return 缓存结果
        
        # 获取详情
        try:
            详情 = self._带重试执行(self.movie.details, 电影id)
            详情字典 = self._电影对象转字典(详情) if 详情 else None
            
            # 保存到缓存
            if 详情字典 and self.启用缓存 and self.缓存:
                self.缓存.设置(缓存键, 详情字典)
            
            logger.info(f"获取电影详情: ID={电影id}")
            return 详情字典
            
        except Exception as e:
            logger.error(f"获取电影详情失败: {e}")
            return None
    
    def 获取电视剧详情(
        self,
        电视剧id: int,
        使用缓存: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        获取电视剧详细信息
        
        Args:
            电视剧id: 电视剧 ID
            使用缓存: 是否使用缓存
            
        Returns:
            Optional[Dict[str, Any]]: 电视剧详细信息
        """
        # 生成缓存键
        缓存键 = f"tv_details:{电视剧id}"
        
        # 尝试从缓存加载
        if self.启用缓存 and 使用缓存 and self.缓存:
            缓存结果 = self.缓存.获取(缓存键)
            if 缓存结果 is not None:
                return 缓存结果
        
        # 获取详情
        try:
            详情 = self._带重试执行(self.tv.details, 电视剧id)
            详情字典 = self._电视剧对象转字典(详情) if 详情 else None
            
            # 保存到缓存
            if 详情字典 and self.启用缓存 and self.缓存:
                self.缓存.设置(缓存键, 详情字典)
            
            logger.info(f"获取电视剧详情: ID={电视剧id}")
            return 详情字典
            
        except Exception as e:
            logger.error(f"获取电视剧详情失败: {e}")
            return None
    
    def 获取剧集详情(
        self,
        电视剧id: int,
        季数: int,
        集数: int,
        使用缓存: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        获取剧集详细信息
        
        Args:
            电视剧id: 电视剧 ID
            季数: 季数
            集数: 集数
            使用缓存: 是否使用缓存
            
        Returns:
            Optional[Dict[str, Any]]: 剧集详细信息
        """
        # 生成缓存键
        缓存键 = f"episode_details:{电视剧id}:{季数}:{集数}"
        
        # 尝试从缓存加载
        if self.启用缓存 and 使用缓存 and self.缓存:
            缓存结果 = self.缓存.获取(缓存键)
            if 缓存结果 is not None:
                return 缓存结果
        
        # 获取详情
        try:
            详情 = self._带重试执行(
                self.episode.details,
                电视剧id,
                季数,
                集数
            )
            详情字典 = self._剧集对象转字典(详情) if 详情 else None
            
            # 保存到缓存
            if 详情字典 and self.启用缓存 and self.缓存:
                self.缓存.设置(缓存键, 详情字典)
            
            logger.info(f"获取剧集详情: ID={电视剧id}, S{季数}E{集数}")
            return 详情字典
            
        except Exception as e:
            logger.error(f"获取剧集详情失败: {e}")
            return None
    
    def _电影对象转字典(self, 电影对象) -> Dict[str, Any]:
        """将 TMDB 电影对象转换为字典"""
        if hasattr(电影对象, '__dict__'):
            return dict(电影对象.__dict__)
        return dict(电影对象)
    
    def _电视剧对象转字典(self, 电视剧对象) -> Dict[str, Any]:
        """将 TMDB 电视剧对象转换为字典"""
        if hasattr(电视剧对象, '__dict__'):
            return dict(电视剧对象.__dict__)
        return dict(电视剧对象)
    
    def _剧集对象转字典(self, 剧集对象) -> Dict[str, Any]:
        """将 TMDB 剧集对象转换为字典"""
        if hasattr(剧集对象, '__dict__'):
            return dict(剧集对象.__dict__)
        return dict(剧集对象)
    
    def 清空缓存(self) -> None:
        """清空所有缓存"""
        if self.缓存:
            self.缓存.清空()
            logger.info("已清空 TMDB 缓存")


# 保持向后兼容的英文接口
class EnhancedTMDBClient(增强TMDB客户端):
    """
    增强版 TMDB 客户端（英文接口）
    """
    
    def search_movie(
        self,
        title: str,
        year: Optional[int] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """搜索电影"""
        return self.搜索电影(标题=title, 年份=year, 使用缓存=use_cache)
    
    def search_tv(
        self,
        title: str,
        year: Optional[int] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """搜索电视剧"""
        return self.搜索电视剧(标题=title, 年份=year, 使用缓存=use_cache)
    
    def get_movie_details(
        self,
        movie_id: int,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """获取电影详情"""
        return self.获取电影详情(电影id=movie_id, 使用缓存=use_cache)
    
    def get_tv_details(
        self,
        tv_id: int,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """获取电视剧详情"""
        return self.获取电视剧详情(电视剧id=tv_id, 使用缓存=use_cache)
    
    def get_episode_details(
        self,
        tv_id: int,
        season: int,
        episode: int,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """获取剧集详情"""
        return self.获取剧集详情(
            电视剧id=tv_id,
            季数=season,
            集数=episode,
            使用缓存=use_cache
        )
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.清空缓存()
