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
from collections import OrderedDict
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from tmdbv3api import TMDb, Movie, TV, Season, Episode

# 配置日志
logger = logging.getLogger(__name__)


class 缓存管理器:
    """
    双层缓存管理器（内存 LRU + 磁盘缓存）
    """
    
    def __init__(
        self,
        缓存目录: Path,
        过期时间: int = 7,
        最大内存条目数: int = 1000
    ):
        """
        初始化缓存管理器
        
        Args:
            缓存目录: 缓存文件存储目录
            过期时间: 缓存过期时间（天），默认7天
            最大内存条目数: 内存缓存最大条目数
        """
        self.缓存目录 = 缓存目录
        self.过期时间 = timedelta(days=过期时间)
        self.最大内存条目数 = 最大内存条目数
        self.缓存目录.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存 (LRU)
        self._内存缓存: OrderedDict = OrderedDict()
        self._锁 = Lock()
        
        # 统计信息
        self._内存命中次数 = 0
        self._内存未命中次数 = 0
        self._磁盘命中次数 = 0
        self._磁盘未命中次数 = 0
    
    def _获取缓存路径(self, 键: str) -> Path:
        """获取缓存文件路径"""
        # 使用 hash 避免文件名过长或包含非法字符
        import hashlib
        键哈希 = hashlib.md5(键.encode()).hexdigest()
        return self.缓存目录 / f"{键哈希}.json"
    
    def _标准化键(self, 键: str) -> str:
        """
        标准化缓存键
        
        Args:
            键: 原始缓存键
            
        Returns:
            str: 标准化后的缓存键
        """
        # 转小写并去除多余空格
        return " ".join(键.lower().split())
    
    def 获取(self, 键: str) -> Optional[Any]:
        """
        从缓存中获取数据（先查内存，再查磁盘）
        
        Args:
            键: 缓存键
            
        Returns:
            Optional[Any]: 缓存的数据，如果不存在或过期则返回 None
        """
        键 = self._标准化键(键)
        
        # 1. 先查内存缓存
        with self._锁:
            if 键 in self._内存缓存:
                缓存项 = self._内存缓存[键]
                
                # 检查是否过期
                创建时间 = datetime.fromisoformat(缓存项['创建时间'])
                if datetime.now() - 创建时间 > self.过期时间:
                    logger.debug(f"内存缓存已过期: {键}")
                    del self._内存缓存[键]
                else:
                    # 移到末尾（LRU 更新）
                    self._内存缓存.move_to_end(键)
                    self._内存命中次数 += 1
                    logger.debug(f"内存缓存命中: {键}")
                    return 缓存项['数据']
            
            self._内存未命中次数 += 1
        
        # 2. 内存未命中，查磁盘缓存
        缓存路径 = self._获取缓存路径(键)
        
        if not 缓存路径.exists():
            self._磁盘未命中次数 += 1
            return None
        
        try:
            with open(缓存路径, 'r', encoding='utf-8') as f:
                缓存数据 = json.load(f)
            
            # 检查是否过期
            创建时间 = datetime.fromisoformat(缓存数据['创建时间'])
            if datetime.now() - 创建时间 > self.过期时间:
                logger.debug(f"磁盘缓存已过期: {键}")
                缓存路径.unlink()
                self._磁盘未命中次数 += 1
                return None
            
            # 从磁盘加载到内存
            with self._锁:
                self._内存缓存[键] = 缓存数据
                self._内存缓存.move_to_end(键)
                
                # LRU 淘汰
                while len(self._内存缓存) > self.最大内存条目数:
                    self._内存缓存.popitem(last=False)
            
            self._磁盘命中次数 += 1
            logger.debug(f"磁盘缓存命中: {键}")
            return 缓存数据['数据']
            
        except Exception as e:
            logger.warning(f"读取磁盘缓存失败: {e}")
            self._磁盘未命中次数 += 1
            return None
    
    def 设置(self, 键: str, 数据: Any) -> None:
        """
        保存数据到缓存（同时写入内存和磁盘）
        
        Args:
            键: 缓存键
            数据: 要缓存的数据
        """
        键 = self._标准化键(键)
        
        缓存数据 = {
            '创建时间': datetime.now().isoformat(),
            '数据': 数据
        }
        
        # 1. 写入内存缓存
        with self._锁:
            self._内存缓存[键] = 缓存数据
            self._内存缓存.move_to_end(键)
            
            # LRU 淘汰
            while len(self._内存缓存) > self.最大内存条目数:
                淘汰键, _ = self._内存缓存.popitem(last=False)
                logger.debug(f"LRU 淘汰: {淘汰键}")
        
        # 2. 写入磁盘缓存（异步，失败不影响内存）
        缓存路径 = self._获取缓存路径(键)
        
        try:
            with open(缓存路径, 'w', encoding='utf-8') as f:
                json.dump(缓存数据, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"保存到缓存: {键}")
            
        except Exception as e:
            logger.warning(f"写入磁盘缓存失败: {e}")
    
    def 清空(self) -> None:
        """清空所有缓存"""
        # 清空内存缓存
        with self._锁:
            self._内存缓存.clear()
            self._内存命中次数 = 0
            self._内存未命中次数 = 0
            self._磁盘命中次数 = 0
            self._磁盘未命中次数 = 0
        
        # 清空磁盘缓存
        for 缓存文件 in self.缓存目录.glob("*.json"):
            try:
                缓存文件.unlink()
            except Exception as e:
                logger.warning(f"删除缓存文件失败: {e}")
        
        logger.info("已清空所有缓存")
    
    def 获取统计信息(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            dict: 统计信息
        """
        with self._锁:
            总请求数 = (self._内存命中次数 + self._内存未命中次数 +
                      self._磁盘命中次数 + self._磁盘未命中次数)
            总命中数 = self._内存命中次数 + self._磁盘命中次数
            
            return {
                "memory_hits": self._内存命中次数,
                "memory_misses": self._内存未命中次数,
                "disk_hits": self._磁盘命中次数,
                "disk_misses": self._磁盘未命中次数,
                "total_requests": 总请求数,
                "total_hits": 总命中数,
                "hit_rate": 总命中数 / 总请求数 if 总请求数 > 0 else 0.0,
                "memory_entries": len(self._内存缓存),
                "max_memory_entries": self.最大内存条目数
            }


class 增强TMDB客户端:
    """
    增强版 TMDB API 客户端
    
    提供缓存、重试机制、并发控制和更丰富的功能
    """
    
    def __init__(
        self,
        api_key: str,
        language: str = "zh-CN",
        缓存目录: Optional[Path] = None,
        启用缓存: bool = True,
        最大重试次数: int = 3,
        重试延迟: float = 1.0,
        缓存过期天数: float = 7,
        最大缓存条目数: int = 1000,
        最大并发请求数: int = 5,
        请求超时: int = 30
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
            缓存过期天数: 缓存过期时间（天）
            最大缓存条目数: 内存缓存最大条目数
            最大并发请求数: 批量请求时的最大并发数
            请求超时: 请求超时时间（秒）
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
        self.最大并发请求数 = 最大并发请求数
        self.请求超时 = 请求超时
        
        # 初始化缓存
        self.启用缓存 = 启用缓存
        if 启用缓存:
            if 缓存目录 is None:
                缓存目录 = Path.home() / ".smartrenamer" / "cache" / "tmdb"
            self.缓存 = 缓存管理器(缓存目录, 过期时间=缓存过期天数, 最大内存条目数=最大缓存条目数)
        else:
            self.缓存 = None
        
        # 线程池（用于并发请求）
        self._线程池: Optional[ThreadPoolExecutor] = None
    
    def _获取线程池(self) -> ThreadPoolExecutor:
        """获取或创建线程池"""
        if self._线程池 is None:
            self._线程池 = ThreadPoolExecutor(max_workers=self.最大并发请求数)
        return self._线程池
    
    def _带重试执行(self, 函数, *args, **kwargs) -> Any:
        """
        带重试机制执行函数（支持指数退避）
        
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
                开始时间 = time.time()
                结果 = 函数(*args, **kwargs)
                耗时 = time.time() - 开始时间
                
                if 耗时 > self.请求超时 * 0.8:
                    logger.warning(f"API 请求耗时较长: {耗时:.2f}秒（接近超时阈值 {self.请求超时}秒）")
                
                return 结果
                
            except Exception as e:
                最后异常 = e
                退避时间 = self.重试延迟 * (2 ** 尝试次数)  # 指数退避：1s, 2s, 4s, 8s...
                
                logger.warning(
                    f"API 请求失败 (尝试 {尝试次数 + 1}/{self.最大重试次数}): {e}, "
                    f"将在 {退避时间:.1f}秒 后重试"
                )
                
                if 尝试次数 < self.最大重试次数 - 1:
                    time.sleep(退避时间)
        
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
    
    def 获取缓存统计(self) -> dict:
        """
        获取缓存统计信息
        
        Returns:
            dict: 缓存统计信息
        """
        if not self.启用缓存 or not self.缓存:
            return {
                "enabled": False,
                "memory_hits": 0,
                "memory_misses": 0,
                "disk_hits": 0,
                "disk_misses": 0,
                "total_requests": 0,
                "total_hits": 0,
                "hit_rate": 0.0,
                "memory_entries": 0,
                "max_memory_entries": 0
            }
        
        stats = self.缓存.获取统计信息()
        stats["enabled"] = True
        return stats
    
    def 批量搜索电影(
        self,
        标题列表: List[str],
        使用缓存: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量搜索电影（并发执行）
        
        Args:
            标题列表: 电影标题列表
            使用缓存: 是否使用缓存
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 标题到搜索结果的映射
        """
        结果字典 = {}
        线程池 = self._获取线程池()
        
        # 提交所有任务
        futures = {
            线程池.submit(self.搜索电影, 标题, None, 使用缓存): 标题
            for 标题 in 标题列表
        }
        
        # 收集结果
        for future in as_completed(futures):
            标题 = futures[future]
            try:
                结果字典[标题] = future.result()
            except Exception as e:
                logger.error(f"批量搜索电影 '{标题}' 失败: {e}")
                结果字典[标题] = []
        
        logger.info(f"批量搜索完成: {len(标题列表)} 个电影")
        return 结果字典
    
    def 批量搜索电视剧(
        self,
        标题列表: List[str],
        使用缓存: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        批量搜索电视剧（并发执行）
        
        Args:
            标题列表: 电视剧标题列表
            使用缓存: 是否使用缓存
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 标题到搜索结果的映射
        """
        结果字典 = {}
        线程池 = self._获取线程池()
        
        # 提交所有任务
        futures = {
            线程池.submit(self.搜索电视剧, 标题, None, 使用缓存): 标题
            for 标题 in 标题列表
        }
        
        # 收集结果
        for future in as_completed(futures):
            标题 = futures[future]
            try:
                结果字典[标题] = future.result()
            except Exception as e:
                logger.error(f"批量搜索电视剧 '{标题}' 失败: {e}")
                结果字典[标题] = []
        
        logger.info(f"批量搜索完成: {len(标题列表)} 个电视剧")
        return 结果字典
    
    def __del__(self):
        """析构函数，清理线程池"""
        if self._线程池 is not None:
            self._线程池.shutdown(wait=False)


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
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        return self.获取缓存统计()
    
    def batch_search_movies(
        self,
        titles: List[str],
        use_cache: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """批量搜索电影"""
        return self.批量搜索电影(标题列表=titles, 使用缓存=use_cache)
    
    def batch_search_tv(
        self,
        titles: List[str],
        use_cache: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """批量搜索电视剧"""
        return self.批量搜索电视剧(标题列表=titles, 使用缓存=use_cache)
