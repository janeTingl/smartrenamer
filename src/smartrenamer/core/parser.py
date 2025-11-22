"""
文件名解析器

智能解析各种命名格式的媒体文件名，提取标题、年份、分辨率等信息
"""
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from .models import MediaType


class 文件名解析器:
    """
    智能文件名解析器
    
    支持多种常见命名格式，提取电影和电视剧的元数据信息
    """
    
    # 常见的文件质量标识
    质量标识 = [
        r'2160p', r'4K', r'UHD',
        r'1080p', r'720p', r'480p', r'360p'
    ]
    
    # 常见的来源标识
    来源标识 = [
        r'BluRay', r'Blu-ray', r'BD', r'BDRip',
        r'WEB-DL', r'WEBDL', r'WEB', r'WEBRip',
        r'HDTV', r'DVDRip', r'DVD', r'CAM', r'TS'
    ]
    
    # 常见的编码格式
    编码格式 = [
        r'[Hh]\.?265', r'HEVC', r'[Xx]265',
        r'[Hh]\.?264', r'AVC', r'[Xx]264',
        r'XviD', r'DivX'
    ]
    
    # 季集格式模式
    季集模式列表 = [
        r'[Ss](\d{1,2})[Ee](\d{1,3})',  # S01E01
        r'[Ss](\d{1,2})\s*[Ee][Pp]?(\d{1,3})',  # S01 EP01 或 S01 E01
        r'(\d{1,2})[Xx](\d{1,3})',  # 1x01
        r'第\s*(\d{1,3})\s*季\s*第\s*(\d{1,3})\s*集',  # 第1季第1集
    ]
    
    # 需要清理的标识（常见的发布组、标签等）
    清理标识 = [
        r'\[.*?\]',  # [发布组]
        r'\(.*?\)',  # (标签)
        r'\{.*?\}',  # {标签}
        r'www\.[^\s]+',  # 网址
        r'[@#]\w+',  # @发布者 #标签
    ]
    
    def __init__(self, 自定义规则: Optional[List[str]] = None):
        """
        初始化解析器
        
        Args:
            自定义规则: 自定义的正则表达式规则列表
        """
        self.自定义规则 = 自定义规则 or []
        
    def 解析(self, 文件名: str) -> Dict[str, Any]:
        """
        解析文件名，提取所有可能的信息
        
        Args:
            文件名: 要解析的文件名（可以包含路径和扩展名）
            
        Returns:
            Dict[str, Any]: 解析结果字典，包含：
                - 媒体类型: MediaType
                - 标题: str
                - 年份: Optional[int]
                - 季数: Optional[int]
                - 集数: Optional[int]
                - 分辨率: Optional[str]
                - 来源: Optional[str]
                - 编码: Optional[str]
                - 原始名称: str
                - 清理后名称: str
        """
        # 移除路径和扩展名
        if isinstance(文件名, Path):
            文件名 = 文件名.stem
        else:
            文件名 = Path(文件名).stem
            
        原始名称 = 文件名
        
        # 初始化结果
        结果 = {
            "媒体类型": MediaType.UNKNOWN,
            "标题": "",
            "年份": None,
            "季数": None,
            "集数": None,
            "分辨率": None,
            "来源": None,
            "编码": None,
            "原始名称": 原始名称,
            "清理后名称": "",
        }
        
        # 提取季集信息，同时获取匹配位置
        季数, 集数, 季集位置 = self._提取季集带位置(文件名)
        if 季数 is not None and 集数 is not None:
            结果["季数"] = 季数
            结果["集数"] = 集数
            结果["媒体类型"] = MediaType.TV_SHOW
            结果["_季集位置"] = 季集位置  # 内部使用
        
        # 提取年份
        结果["年份"] = self._提取年份(文件名)
        
        # 提取质量信息
        结果["分辨率"] = self._提取分辨率(文件名)
        结果["来源"] = self._提取来源(文件名)
        结果["编码"] = self._提取编码(文件名)
        
        # 清理文件名并提取标题
        清理后名称 = self._清理文件名(文件名)
        结果["清理后名称"] = 清理后名称
        结果["标题"] = self._提取标题(文件名, 清理后名称, 结果)
        
        # 移除内部使用的键
        结果.pop("_季集位置", None)
        
        # 如果没有检测到季集信息，判断为电影
        if 结果["媒体类型"] == MediaType.UNKNOWN:
            结果["媒体类型"] = MediaType.MOVIE
            
        return 结果
    
    def _提取季集(self, 文本: str) -> Tuple[Optional[int], Optional[int]]:
        """
        提取季数和集数
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Tuple[Optional[int], Optional[int]]: (季数, 集数)
        """
        季数, 集数, _ = self._提取季集带位置(文本)
        return 季数, 集数
    
    def _提取季集带位置(self, 文本: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        提取季数、集数和匹配位置
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Tuple[Optional[int], Optional[int], Optional[int]]: (季数, 集数, 匹配位置)
        """
        for 模式 in self.季集模式列表:
            匹配 = re.search(模式, 文本, re.IGNORECASE)
            if 匹配:
                try:
                    季数 = int(匹配.group(1))
                    集数 = int(匹配.group(2))
                    位置 = 匹配.start()
                    return 季数, 集数, 位置
                except (ValueError, IndexError):
                    continue
        
        return None, None, None
    
    def _提取年份(self, 文本: str) -> Optional[int]:
        """
        提取年份信息
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Optional[int]: 年份
        """
        # 匹配 1900-2099 年份
        年份匹配列表 = re.findall(r'\b(19\d{2}|20\d{2})\b', 文本)
        
        if 年份匹配列表:
            # 返回第一个匹配的年份
            return int(年份匹配列表[0])
        
        return None
    
    def _提取分辨率(self, 文本: str) -> Optional[str]:
        """
        提取分辨率信息
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Optional[str]: 分辨率
        """
        for 模式 in self.质量标识:
            匹配 = re.search(模式, 文本, re.IGNORECASE)
            if 匹配:
                分辨率 = 匹配.group().upper()
                # 标准化某些格式
                if 分辨率 in ['UHD', '4K']:
                    return '2160p'
                return 分辨率
        
        return None
    
    def _提取来源(self, 文本: str) -> Optional[str]:
        """
        提取来源信息
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Optional[str]: 来源
        """
        for 模式 in self.来源标识:
            匹配 = re.search(模式, 文本, re.IGNORECASE)
            if 匹配:
                来源 = 匹配.group()
                # 标准化格式
                来源_大写 = 来源.upper()
                if 来源_大写 in ['BD', 'BDRIP']:
                    return 'BluRay'
                elif 来源_大写 in ['WEBDL', 'WEBRIP']:
                    return 'WEB-DL'
                return 来源
        
        return None
    
    def _提取编码(self, 文本: str) -> Optional[str]:
        """
        提取编码格式信息
        
        Args:
            文本: 要解析的文本
            
        Returns:
            Optional[str]: 编码格式
        """
        for 模式 in self.编码格式:
            匹配 = re.search(模式, 文本, re.IGNORECASE)
            if 匹配:
                编码 = 匹配.group()
                # 标准化格式
                编码_大写 = 编码.upper().replace('.', '')
                if 'H265' in 编码_大写 or 'HEVC' in 编码_大写 or 'X265' in 编码_大写:
                    return 'H265'
                elif 'H264' in 编码_大写 or 'AVC' in 编码_大写 or 'X264' in 编码_大写:
                    return 'H264'
                return 编码
        
        return None
    
    def _清理文件名(self, 文本: str) -> str:
        """
        清理文件名，移除标签、发布组等信息
        
        Args:
            文本: 要清理的文本
            
        Returns:
            str: 清理后的文本
        """
        清理后 = 文本
        
        # 移除常见标识
        for 模式 in self.清理标识:
            清理后 = re.sub(模式, ' ', 清理后)
        
        # 移除质量、来源、编码标识
        for 模式列表 in [self.质量标识, self.来源标识, self.编码格式]:
            for 模式 in 模式列表:
                清理后 = re.sub(模式, ' ', 清理后, flags=re.IGNORECASE)
        
        # 移除季集信息
        for 模式 in self.季集模式列表:
            清理后 = re.sub(模式, ' ', 清理后, flags=re.IGNORECASE)
        
        # 移除年份（会在标题提取时单独处理）
        # 清理后 = re.sub(r'\b(19|20)\d{2}\b', ' ', 清理后)
        
        # 标准化分隔符
        清理后 = re.sub(r'[._\-]+', ' ', 清理后)
        
        # 移除多余空格
        清理后 = re.sub(r'\s+', ' ', 清理后).strip()
        
        return 清理后
    
    def _提取标题(self, 原始文本: str, 清理后文本: str, 解析结果: Dict[str, Any]) -> str:
        """
        从清理后的文本中提取标题
        
        Args:
            原始文本: 原始文件名
            清理后文本: 清理后的文本
            解析结果: 之前的解析结果
            
        Returns:
            str: 提取的标题
        """
        标题 = 清理后文本
        
        # 对于电视剧，优先在季集位置截断
        if 解析结果.get("_季集位置") is not None:
            季集位置 = 解析结果["_季集位置"]
            # 从原始文本中截取季集之前的部分
            标题部分 = 原始文本[:季集位置]
            # 清理标题部分
            标题部分 = re.sub(r'[._\-]+', ' ', 标题部分)
            标题部分 = 标题部分.strip()
            if 标题部分:
                标题 = 标题部分
        # 如果有年份，截取年份之前的部分作为标题
        elif 解析结果["年份"]:
            年份位置 = 标题.find(str(解析结果["年份"]))
            if 年份位置 > 0:
                标题 = 标题[:年份位置]
        
        # 移除尾部的多余空格和标点
        标题 = 标题.strip(' -._')
        
        # 移除常见的无用词
        无用词列表 = ['HDR', 'HDR10', 'DTS', 'DD', 'AAC', 'AC3', '5.1', '7.1', 
                  'EXTENDED', 'UNRATED', 'DIRECTORS CUT', 'REMASTERED']
        for 无用词 in 无用词列表:
            标题 = re.sub(rf'\b{无用词}\b', '', 标题, flags=re.IGNORECASE)
        
        # 最终清理
        标题 = re.sub(r'\s+', ' ', 标题).strip()
        
        return 标题 if 标题 else "Unknown"


# 保持向后兼容的英文接口
class FileNameParser(文件名解析器):
    """
    文件名解析器（英文接口）
    
    提供与中文接口相同的功能
    """
    
    def __init__(self, custom_rules: Optional[List[str]] = None):
        super().__init__(自定义规则=custom_rules)
    
    def parse(self, filename: str) -> Dict[str, Any]:
        """
        解析文件名
        
        Args:
            filename: 文件名
            
        Returns:
            Dict[str, Any]: 解析结果，包含英文键名：
                - media_type
                - title
                - year
                - season
                - episode
                - resolution
                - source
                - codec
                - original_name
                - cleaned_name
        """
        结果 = self.解析(filename)
        
        # 转换为英文键名
        return {
            "media_type": 结果["媒体类型"],
            "title": 结果["标题"],
            "year": 结果["年份"],
            "season": 结果["季数"],
            "episode": 结果["集数"],
            "resolution": 结果["分辨率"],
            "source": 结果["来源"],
            "codec": 结果["编码"],
            "original_name": 结果["原始名称"],
            "cleaned_name": 结果["清理后名称"],
        }
