"""
智能匹配引擎

将本地媒体文件与 TMDB 数据库进行智能匹配
"""
import logging
from typing import Optional, List, Dict, Any, Tuple
from difflib import SequenceMatcher
from .models import MediaFile, MediaType
from .parser import 文件名解析器
from ..api.tmdb_client_enhanced import 增强TMDB客户端
from ..api.factory import get_tmdb_client
from .config import get_config

# 配置日志
logger = logging.getLogger(__name__)


class 匹配结果:
    """
    匹配结果数据类
    """
    
    def __init__(
        self,
        tmdb数据: Dict[str, Any],
        相似度: float,
        媒体类型: MediaType,
        匹配原因: str = ""
    ):
        """
        初始化匹配结果
        
        Args:
            tmdb数据: TMDB 数据
            相似度: 匹配相似度 (0-1)
            媒体类型: 媒体类型
            匹配原因: 匹配原因说明
        """
        self.tmdb数据 = tmdb数据
        self.相似度 = 相似度
        self.媒体类型 = 媒体类型
        self.匹配原因 = 匹配原因
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tmdb_data": self.tmdb数据,
            "similarity": self.相似度,
            "media_type": self.媒体类型.value,
            "match_reason": self.匹配原因,
        }
    
    def __repr__(self) -> str:
        标题 = self.tmdb数据.get('title') or self.tmdb数据.get('name', 'Unknown')
        return f"匹配结果(标题={标题}, 相似度={self.相似度:.2f}, 原因={self.匹配原因})"


class 智能匹配器:
    """
    智能匹配引擎
    
    使用多种策略将本地文件与 TMDB 数据进行匹配
    """
    
    # 相似度阈值
    最小相似度 = 0.6  # 最低匹配相似度
    高相似度 = 0.85  # 高相似度阈值，超过此值可以自动匹配
    
    def __init__(
        self,
        tmdb客户端: Optional[增强TMDB客户端] = None,
        解析器: Optional[文件名解析器] = None
    ):
        """
        初始化匹配器
        
        Args:
            tmdb客户端: TMDB 客户端实例（可选，如果为 None 则使用工厂创建）
            解析器: 文件名解析器实例（可选）
        """
        if tmdb客户端 is None:
            config = get_config()
            self.tmdb客户端 = get_tmdb_client(config)
            logger.info("使用工厂模式创建共享 TMDB 客户端")
        else:
            self.tmdb客户端 = tmdb客户端
        
        self.解析器 = 解析器 or 文件名解析器()
    
    def 匹配文件(
        self,
        文件路径: str,
        最大结果数: int = 5,
        自动确认: bool = False
    ) -> List[匹配结果]:
        """
        匹配单个文件
        
        Args:
            文件路径: 文件路径
            最大结果数: 返回的最大结果数
            自动确认: 如果相似度很高，是否自动确认第一个结果
            
        Returns:
            List[匹配结果]: 匹配结果列表，按相似度降序排列
        """
        # 解析文件名
        解析结果 = self.解析器.解析(文件路径)
        
        logger.info(f"解析文件: {文件路径}")
        logger.info(f"解析结果: 标题={解析结果['标题']}, 类型={解析结果['媒体类型'].value}")
        
        # 根据媒体类型进行匹配
        if 解析结果['媒体类型'] == MediaType.TV_SHOW:
            匹配列表 = self._匹配电视剧(解析结果, 最大结果数)
        else:
            匹配列表 = self._匹配电影(解析结果, 最大结果数)
        
        # 如果启用自动确认且第一个结果相似度很高
        if 自动确认 and 匹配列表 and 匹配列表[0].相似度 >= self.高相似度:
            logger.info(f"自动确认匹配: {匹配列表[0]}")
            return [匹配列表[0]]
        
        return 匹配列表
    
    def 匹配媒体文件(
        self,
        媒体文件: MediaFile,
        最大结果数: int = 5
    ) -> List[匹配结果]:
        """
        匹配 MediaFile 对象
        
        Args:
            媒体文件: MediaFile 对象
            最大结果数: 返回的最大结果数
            
        Returns:
            List[匹配结果]: 匹配结果列表
        """
        return self.匹配文件(str(媒体文件.path), 最大结果数)
    
    def _匹配电影(
        self,
        解析结果: Dict[str, Any],
        最大结果数: int
    ) -> List[匹配结果]:
        """
        匹配电影
        
        Args:
            解析结果: 文件名解析结果
            最大结果数: 最大结果数
            
        Returns:
            List[匹配结果]: 匹配结果列表
        """
        标题 = 解析结果['标题']
        年份 = 解析结果['年份']
        
        # 搜索电影
        搜索结果 = self.tmdb客户端.搜索电影(标题, 年份)
        
        if not 搜索结果:
            logger.warning(f"未找到电影: {标题}")
            return []
        
        # 计算相似度并排序
        匹配列表 = []
        for 结果 in 搜索结果[:最大结果数 * 2]:  # 多获取一些，后面筛选
            相似度, 原因 = self._计算电影相似度(解析结果, 结果)
            
            if 相似度 >= self.最小相似度:
                匹配 = 匹配结果(
                    tmdb数据=结果,
                    相似度=相似度,
                    媒体类型=MediaType.MOVIE,
                    匹配原因=原因
                )
                匹配列表.append(匹配)
        
        # 按相似度降序排序
        匹配列表.sort(key=lambda x: x.相似度, reverse=True)
        
        logger.info(f"找到 {len(匹配列表)} 个电影匹配结果")
        return 匹配列表[:最大结果数]
    
    def _匹配电视剧(
        self,
        解析结果: Dict[str, Any],
        最大结果数: int
    ) -> List[匹配结果]:
        """
        匹配电视剧
        
        Args:
            解析结果: 文件名解析结果
            最大结果数: 最大结果数
            
        Returns:
            List[匹配结果]: 匹配结果列表
        """
        标题 = 解析结果['标题']
        年份 = 解析结果['年份']
        
        # 搜索电视剧
        搜索结果 = self.tmdb客户端.搜索电视剧(标题, 年份)
        
        if not 搜索结果:
            logger.warning(f"未找到电视剧: {标题}")
            return []
        
        # 计算相似度并排序
        匹配列表 = []
        for 结果 in 搜索结果[:最大结果数 * 2]:
            相似度, 原因 = self._计算电视剧相似度(解析结果, 结果)
            
            if 相似度 >= self.最小相似度:
                匹配 = 匹配结果(
                    tmdb数据=结果,
                    相似度=相似度,
                    媒体类型=MediaType.TV_SHOW,
                    匹配原因=原因
                )
                匹配列表.append(匹配)
        
        # 按相似度降序排序
        匹配列表.sort(key=lambda x: x.相似度, reverse=True)
        
        logger.info(f"找到 {len(匹配列表)} 个电视剧匹配结果")
        return 匹配列表[:最大结果数]
    
    def _计算电影相似度(
        self,
        解析结果: Dict[str, Any],
        tmdb结果: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        计算电影匹配相似度
        
        Args:
            解析结果: 解析结果
            tmdb结果: TMDB 结果
            
        Returns:
            Tuple[float, str]: (相似度, 原因)
        """
        本地标题 = 解析结果['标题'].lower()
        本地年份 = 解析结果['年份']
        
        tmdb标题 = tmdb结果.get('title', '').lower()
        tmdb原始标题 = tmdb结果.get('original_title', '').lower()
        tmdb年份 = None
        
        # 提取 TMDB 年份
        发行日期 = tmdb结果.get('release_date', '')
        if 发行日期:
            try:
                tmdb年份 = int(发行日期[:4])
            except (ValueError, IndexError):
                pass
        
        # 计算标题相似度
        标题相似度 = max(
            self._字符串相似度(本地标题, tmdb标题),
            self._字符串相似度(本地标题, tmdb原始标题)
        )
        
        # 计算年份匹配度
        年份匹配度 = 0.0
        if 本地年份 and tmdb年份:
            if 本地年份 == tmdb年份:
                年份匹配度 = 1.0
            elif abs(本地年份 - tmdb年份) == 1:
                # 允许1年的误差
                年份匹配度 = 0.8
        elif not 本地年份:
            # 如果没有年份信息，给予中等匹配度
            年份匹配度 = 0.5
        
        # 综合相似度：标题占 70%，年份占 30%
        总相似度 = 标题相似度 * 0.7 + 年份匹配度 * 0.3
        
        # 生成匹配原因
        原因 = f"标题相似度: {标题相似度:.2f}"
        if 本地年份:
            原因 += f", 年份: {本地年份} vs {tmdb年份}"
        
        return 总相似度, 原因
    
    def _计算电视剧相似度(
        self,
        解析结果: Dict[str, Any],
        tmdb结果: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        计算电视剧匹配相似度
        
        Args:
            解析结果: 解析结果
            tmdb结果: TMDB 结果
            
        Returns:
            Tuple[float, str]: (相似度, 原因)
        """
        本地标题 = 解析结果['标题'].lower()
        本地年份 = 解析结果['年份']
        
        tmdb标题 = tmdb结果.get('name', '').lower()
        tmdb原始标题 = tmdb结果.get('original_name', '').lower()
        tmdb年份 = None
        
        # 提取 TMDB 年份
        首播日期 = tmdb结果.get('first_air_date', '')
        if 首播日期:
            try:
                tmdb年份 = int(首播日期[:4])
            except (ValueError, IndexError):
                pass
        
        # 计算标题相似度
        标题相似度 = max(
            self._字符串相似度(本地标题, tmdb标题),
            self._字符串相似度(本地标题, tmdb原始标题)
        )
        
        # 计算年份匹配度
        年份匹配度 = 0.0
        if 本地年份 and tmdb年份:
            # 电视剧可能跨越多年，放宽年份匹配
            年份差 = abs(本地年份 - tmdb年份)
            if 年份差 == 0:
                年份匹配度 = 1.0
            elif 年份差 <= 2:
                年份匹配度 = 0.8
            elif 年份差 <= 5:
                年份匹配度 = 0.5
        elif not 本地年份:
            年份匹配度 = 0.5
        
        # 综合相似度：标题占 75%，年份占 25%（电视剧年份不如电影重要）
        总相似度 = 标题相似度 * 0.75 + 年份匹配度 * 0.25
        
        # 生成匹配原因
        原因 = f"标题相似度: {标题相似度:.2f}"
        if 本地年份:
            原因 += f", 年份: {本地年份} vs {tmdb年份}"
        
        return 总相似度, 原因
    
    def _字符串相似度(self, 字符串1: str, 字符串2: str) -> float:
        """
        计算两个字符串的相似度
        
        Args:
            字符串1: 第一个字符串
            字符串2: 第二个字符串
            
        Returns:
            float: 相似度 (0-1)
        """
        if not 字符串1 or not 字符串2:
            return 0.0
        
        # 使用 SequenceMatcher 计算相似度
        return SequenceMatcher(None, 字符串1, 字符串2).ratio()
    
    def 应用匹配到媒体文件(
        self,
        媒体文件: MediaFile,
        匹配: 匹配结果
    ) -> MediaFile:
        """
        将匹配结果应用到 MediaFile 对象
        
        Args:
            媒体文件: MediaFile 对象
            匹配: 匹配结果
            
        Returns:
            MediaFile: 更新后的 MediaFile 对象
        """
        tmdb数据 = 匹配.tmdb数据
        
        # 更新媒体类型
        媒体文件.media_type = 匹配.媒体类型
        
        # 更新基本信息
        if 匹配.媒体类型 == MediaType.MOVIE:
            媒体文件.tmdb_id = tmdb数据.get('id')
            媒体文件.title = tmdb数据.get('title')
            媒体文件.original_title = tmdb数据.get('original_title')
            
            # 提取年份
            发行日期 = tmdb数据.get('release_date', '')
            if 发行日期:
                try:
                    媒体文件.year = int(发行日期[:4])
                except (ValueError, IndexError):
                    pass
        
        elif 匹配.媒体类型 == MediaType.TV_SHOW:
            媒体文件.tmdb_id = tmdb数据.get('id')
            媒体文件.title = tmdb数据.get('name')
            媒体文件.original_title = tmdb数据.get('original_name')
            
            # 提取年份
            首播日期 = tmdb数据.get('first_air_date', '')
            if 首播日期:
                try:
                    媒体文件.year = int(首播日期[:4])
                except (ValueError, IndexError):
                    pass
        
        # 保存匹配信息到元数据
        媒体文件.metadata['match_similarity'] = 匹配.相似度
        媒体文件.metadata['match_reason'] = 匹配.匹配原因
        媒体文件.metadata['tmdb_data'] = tmdb数据
        
        logger.info(f"已应用匹配: {媒体文件.title} (相似度: {匹配.相似度:.2f})")
        
        return 媒体文件


# 保持向后兼容的英文接口
class Matcher(智能匹配器):
    """
    智能匹配器（英文接口）
    """
    
    def match_file(
        self,
        file_path: str,
        max_results: int = 5,
        auto_confirm: bool = False
    ) -> List[匹配结果]:
        """匹配文件"""
        return self.匹配文件(
            文件路径=file_path,
            最大结果数=max_results,
            自动确认=auto_confirm
        )
    
    def match_media_file(
        self,
        media_file: MediaFile,
        max_results: int = 5
    ) -> List[匹配结果]:
        """匹配媒体文件"""
        return self.匹配媒体文件(媒体文件=media_file, 最大结果数=max_results)
    
    def apply_match_to_media_file(
        self,
        media_file: MediaFile,
        match: 匹配结果
    ) -> MediaFile:
        """应用匹配"""
        return self.应用匹配到媒体文件(媒体文件=media_file, 匹配=match)


# 导出别名
MatchResult = 匹配结果
