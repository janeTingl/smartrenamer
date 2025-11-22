"""
重命名引擎模块

基于 Jinja2 模板引擎实现灵活的文件重命名功能
"""
import re
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from jinja2 import Environment, Template, TemplateSyntaxError, UndefinedError
from jinja2.filters import FILTERS

from .models import MediaFile, MediaType, RenameRule


# 自定义 Jinja2 过滤器
def 填充(value: Any, width: int, fillchar: str = '0') -> str:
    """
    填充字符串到指定宽度
    
    Args:
        value: 要填充的值
        width: 目标宽度
        fillchar: 填充字符
    
    Returns:
        str: 填充后的字符串
    
    Examples:
        {{ 1|填充(2) }} -> "01"
        {{ 5|填充(3, '0') }} -> "005"
    """
    return str(value).zfill(width) if fillchar == '0' else str(value).rjust(width, fillchar)


def 清理文件名(value: str) -> str:
    r"""
    清理文件名中的非法字符
    
    Args:
        value: 原始文件名
    
    Returns:
        str: 清理后的文件名
    
    Examples:
        {{ title|清理文件名 }} -> 移除 < > : " / \ | ? *
    """
    # Windows 和 Unix 系统不允许的文件名字符
    illegal_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(illegal_chars, '', value)
    # 移除首尾空格
    cleaned = cleaned.strip()
    # 将多个空格替换为单个空格
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def 截断(value: str, length: int, suffix: str = '...') -> str:
    """
    截断字符串到指定长度
    
    Args:
        value: 原始字符串
        length: 最大长度
        suffix: 截断后缀
    
    Returns:
        str: 截断后的字符串
    
    Examples:
        {{ title|截断(10) }} -> "很长的标题..."
    """
    if len(value) <= length:
        return value
    return value[:length - len(suffix)] + suffix


def 大写首字母(value: str) -> str:
    """
    将每个单词的首字母大写
    
    Args:
        value: 原始字符串
    
    Returns:
        str: 首字母大写的字符串
    
    Examples:
        {{ "the matrix"|大写首字母 }} -> "The Matrix"
    """
    return value.title()


def 全大写(value: str) -> str:
    """
    转换为全大写
    
    Args:
        value: 原始字符串
    
    Returns:
        str: 全大写字符串
    """
    return value.upper()


def 全小写(value: str) -> str:
    """
    转换为全小写
    
    Args:
        value: 原始字符串
    
    Returns:
        str: 全小写字符串
    """
    return value.lower()


def 默认值(value: Any, default: Any = '') -> Any:
    """
    如果值为 None 或空，返回默认值
    
    Args:
        value: 原始值
        default: 默认值
    
    Returns:
        Any: 原始值或默认值
    
    Examples:
        {{ year|默认值(2024) }}
    """
    if value is None or value == '':
        return default
    return value


# 英文别名
pad = 填充
clean = 清理文件名
truncate = 截断
capitalize = 大写首字母
upper = 全大写
lower = 全小写
default = 默认值


# 预定义的重命名模板
预定义模板 = {
    "电影-简洁": {
        "名称": "电影-简洁",
        "描述": "简洁的电影文件名: 标题 (年份)",
        "模板": "{{ title|清理文件名 }} ({{ year }})",
        "媒体类型": MediaType.MOVIE,
        "示例": "黑客帝国 (1999).mkv",
    },
    "电影-标准": {
        "名称": "电影-标准",
        "描述": "标准电影文件名: 标题.年份.分辨率",
        "模板": "{{ title|清理文件名|replace(' ', '.') }}.{{ year }}.{{ resolution|默认值('Unknown') }}",
        "媒体类型": MediaType.MOVIE,
        "示例": "黑客帝国.1999.1080p.mkv",
    },
    "电影-完整": {
        "名称": "电影-完整",
        "描述": "完整电影文件名: 标题.年份.分辨率.来源.编码",
        "模板": "{{ title|清理文件名|replace(' ', '.') }}.{{ year }}.{{ resolution|默认值('Unknown') }}.{{ source|默认值('') }}{% if codec %}.{{ codec }}{% endif %}",
        "媒体类型": MediaType.MOVIE,
        "示例": "黑客帝国.1999.1080p.BluRay.H264.mkv",
    },
    "电视剧-标准": {
        "名称": "电视剧-标准",
        "描述": "标准电视剧文件名: 标题 S01E01",
        "模板": "{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}",
        "媒体类型": MediaType.TV_SHOW,
        "示例": "绝命毒师 S01E01.mkv",
    },
    "电视剧-带剧集名": {
        "名称": "电视剧-带剧集名",
        "描述": "电视剧文件名带剧集标题: 标题 S01E01 剧集名",
        "模板": "{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}{% if episode_title %} {{ episode_title|清理文件名 }}{% endif %}",
        "媒体类型": MediaType.TV_SHOW,
        "示例": "绝命毒师 S01E01 试播集.mkv",
    },
    "电视剧-完整": {
        "名称": "电视剧-完整",
        "描述": "完整电视剧文件名: 标题 S01E01 剧集名 分辨率",
        "模板": "{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}{% if episode_title %} {{ episode_title|清理文件名 }}{% endif %} {{ resolution|默认值('Unknown') }}",
        "媒体类型": MediaType.TV_SHOW,
        "示例": "绝命毒师 S01E01 试播集 1080p.mkv",
    },
    "电视剧-分季目录": {
        "名称": "电视剧-分季目录",
        "描述": "电视剧按季分目录: 标题/Season 01/标题 S01E01",
        "模板": "{{ title|清理文件名 }}/Season {{ season|填充(2) }}/{{ title|清理文件名 }} S{{ season|填充(2) }}E{{ episode|填充(2) }}",
        "媒体类型": MediaType.TV_SHOW,
        "示例": "绝命毒师/Season 01/绝命毒师 S01E01.mkv",
    },
}

# 英文别名
PREDEFINED_TEMPLATES = 预定义模板


@dataclass
class 重命名历史记录:
    """重命名历史记录"""
    原始路径: Path
    新路径: Path
    时间戳: datetime = field(default_factory=datetime.now)
    成功: bool = True
    错误信息: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "原始路径": str(self.原始路径),
            "新路径": str(self.新路径),
            "时间戳": self.时间戳.isoformat(),
            "成功": self.成功,
            "错误信息": self.错误信息,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "重命名历史记录":
        """从字典创建"""
        return cls(
            原始路径=Path(data["原始路径"]),
            新路径=Path(data["新路径"]),
            时间戳=datetime.fromisoformat(data["时间戳"]),
            成功=data["成功"],
            错误信息=data.get("错误信息"),
        )


# 英文别名
RenameHistory = 重命名历史记录


class 重命名规则管理器:
    """
    重命名规则管理器
    
    管理和验证重命名规则
    """
    
    def __init__(self):
        """初始化规则管理器"""
        self._规则列表: List[RenameRule] = []
        self._jinja_环境 = self._创建_jinja_环境()
    
    def _创建_jinja_环境(self) -> Environment:
        """创建 Jinja2 环境"""
        env = Environment(autoescape=False)
        
        # 注册自定义过滤器
        env.filters['填充'] = 填充
        env.filters['pad'] = pad
        env.filters['清理文件名'] = 清理文件名
        env.filters['clean'] = clean
        env.filters['截断'] = 截断
        env.filters['truncate'] = truncate
        env.filters['大写首字母'] = 大写首字母
        env.filters['capitalize'] = capitalize
        env.filters['全大写'] = 全大写
        env.filters['upper'] = upper
        env.filters['全小写'] = 全小写
        env.filters['lower'] = lower
        env.filters['默认值'] = 默认值
        env.filters['default'] = default
        
        return env
    
    def 验证模板(self, 模板: str) -> Tuple[bool, Optional[str]]:
        """
        验证模板语法
        
        Args:
            模板: Jinja2 模板字符串
        
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        try:
            self._jinja_环境.from_string(模板)
            return True, None
        except TemplateSyntaxError as e:
            return False, f"模板语法错误: {e}"
        except Exception as e:
            return False, f"模板验证失败: {e}"
    
    def 添加规则(self, 规则: RenameRule) -> bool:
        """
        添加重命名规则
        
        Args:
            规则: 重命名规则对象
        
        Returns:
            bool: 是否添加成功
        """
        # 验证模板
        有效, 错误 = self.验证模板(规则.template)
        if not 有效:
            raise ValueError(f"规则模板无效: {错误}")
        
        self._规则列表.append(规则)
        return True
    
    def 移除规则(self, 规则名称: str) -> bool:
        """
        移除重命名规则
        
        Args:
            规则名称: 规则名称
        
        Returns:
            bool: 是否移除成功
        """
        原始长度 = len(self._规则列表)
        self._规则列表 = [r for r in self._规则列表 if r.name != 规则名称]
        return len(self._规则列表) < 原始长度
    
    def 获取规则(self, 规则名称: str) -> Optional[RenameRule]:
        """
        获取指定名称的规则
        
        Args:
            规则名称: 规则名称
        
        Returns:
            Optional[RenameRule]: 规则对象，如果不存在返回 None
        """
        for 规则 in self._规则列表:
            if 规则.name == 规则名称:
                return 规则
        return None
    
    def 获取所有规则(self) -> List[RenameRule]:
        """获取所有规则"""
        return self._规则列表.copy()
    
    def 保存到文件(self, 文件路径: Path) -> bool:
        """
        保存规则到文件
        
        Args:
            文件路径: 保存路径
        
        Returns:
            bool: 是否保存成功
        """
        try:
            文件路径.parent.mkdir(parents=True, exist_ok=True)
            
            规则数据 = [规则.to_dict() for 规则 in self._规则列表]
            with open(文件路径, 'w', encoding='utf-8') as f:
                json.dump(规则数据, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存规则失败: {e}")
            return False
    
    def 从文件加载(self, 文件路径: Path) -> bool:
        """
        从文件加载规则
        
        Args:
            文件路径: 文件路径
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if not 文件路径.exists():
                return False
            
            with open(文件路径, 'r', encoding='utf-8') as f:
                规则数据 = json.load(f)
            
            self._规则列表 = []
            for 数据 in 规则数据:
                规则 = RenameRule(
                    name=数据['name'],
                    description=数据['description'],
                    template=数据['template'],
                    media_type=MediaType(数据['media_type']),
                    use_original_title=数据.get('use_original_title', False),
                    include_year=数据.get('include_year', True),
                    include_quality=数据.get('include_quality', True),
                    include_source=数据.get('include_source', True),
                    include_codec=数据.get('include_codec', False),
                    separator=数据.get('separator', '.'),
                    space_replacement=数据.get('space_replacement', '.'),
                )
                self._规则列表.append(规则)
            
            return True
        except Exception as e:
            print(f"加载规则失败: {e}")
            return False
    
    # 英文别名方法
    def validate_template(self, template: str) -> Tuple[bool, Optional[str]]:
        """验证模板（英文别名）"""
        return self.验证模板(template)
    
    def add_rule(self, rule: RenameRule) -> bool:
        """添加规则（英文别名）"""
        return self.添加规则(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """移除规则（英文别名）"""
        return self.移除规则(rule_name)
    
    def get_rule(self, rule_name: str) -> Optional[RenameRule]:
        """获取规则（英文别名）"""
        return self.获取规则(rule_name)
    
    def get_all_rules(self) -> List[RenameRule]:
        """获取所有规则（英文别名）"""
        return self.获取所有规则()
    
    def save_to_file(self, file_path: Path) -> bool:
        """保存到文件（英文别名）"""
        return self.保存到文件(file_path)
    
    def load_from_file(self, file_path: Path) -> bool:
        """从文件加载（英文别名）"""
        return self.从文件加载(file_path)


# 英文别名
RenameRuleManager = 重命名规则管理器


class 重命名器:
    """
    重命名执行引擎
    
    负责执行文件重命名操作，支持预览、批量处理、撤销等功能
    """
    
    def __init__(self, 预览模式: bool = True, 创建备份: bool = True):
        """
        初始化重命名器
        
        Args:
            预览模式: 是否启用预览模式（不实际执行重命名）
            创建备份: 是否创建备份（记录重命名历史）
        """
        self.预览模式 = 预览模式
        self.创建备份 = 创建备份
        self._历史记录: List[重命名历史记录] = []
        self._jinja_环境 = self._创建_jinja_环境()
    
    def _创建_jinja_环境(self) -> Environment:
        """创建 Jinja2 环境"""
        env = Environment(autoescape=False)
        
        # 注册自定义过滤器
        env.filters['填充'] = 填充
        env.filters['pad'] = pad
        env.filters['清理文件名'] = 清理文件名
        env.filters['clean'] = clean
        env.filters['截断'] = 截断
        env.filters['truncate'] = truncate
        env.filters['大写首字母'] = 大写首字母
        env.filters['capitalize'] = capitalize
        env.filters['全大写'] = 全大写
        env.filters['upper'] = upper
        env.filters['全小写'] = 全小写
        env.filters['lower'] = lower
        env.filters['默认值'] = 默认值
        env.filters['default'] = default
        
        return env
    
    def 生成新文件名(self, 媒体文件: MediaFile, 规则: RenameRule) -> Tuple[bool, str, Optional[str]]:
        """
        根据规则生成新文件名
        
        Args:
            媒体文件: 媒体文件对象
            规则: 重命名规则
        
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 新文件名, 错误信息)
        """
        try:
            # 准备模板变量
            上下文 = {
                "title": 媒体文件.title or "Unknown",
                "original_title": 媒体文件.original_title or 媒体文件.title or "Unknown",
                "year": 媒体文件.year,
                "season": 媒体文件.season_number,
                "episode": 媒体文件.episode_number,
                "episode_title": 媒体文件.episode_title or "",
                "resolution": 媒体文件.resolution or "",
                "source": 媒体文件.source or "",
                "codec": 媒体文件.codec or "",
                "separator": 规则.separator,
            }
            
            # 渲染模板
            模板 = self._jinja_环境.from_string(规则.template)
            新文件名 = 模板.render(**上下文)
            
            # 清理文件名（移除多余的分隔符和空格）
            新文件名 = re.sub(r'\.+', '.', 新文件名)  # 多个点替换为单个点
            新文件名 = re.sub(r'\s+', ' ', 新文件名)  # 多个空格替换为单个空格
            新文件名 = 新文件名.strip('. ')  # 移除首尾的点和空格
            
            # 添加扩展名
            if not 新文件名.endswith(媒体文件.extension):
                新文件名 += 媒体文件.extension
            
            return True, 新文件名, None
            
        except UndefinedError as e:
            return False, "", f"模板变量未定义: {e}"
        except Exception as e:
            return False, "", f"生成文件名失败: {e}"
    
    def 重命名文件(self, 媒体文件: MediaFile, 规则: RenameRule) -> Tuple[bool, Optional[str]]:
        """
        重命名单个文件
        
        Args:
            媒体文件: 媒体文件对象
            规则: 重命名规则
        
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        # 生成新文件名
        成功, 新文件名, 错误 = self.生成新文件名(媒体文件, 规则)
        if not 成功:
            return False, 错误
        
        # 构建新路径
        原始路径 = 媒体文件.path
        
        # 处理带目录的新文件名
        if '/' in 新文件名:
            新路径 = 原始路径.parent / 新文件名
        else:
            新路径 = 原始路径.parent / 新文件名
        
        # 预览模式：只更新 media_file 对象，不实际重命名
        if self.预览模式:
            媒体文件.new_name = 新文件名
            媒体文件.rename_status = "preview"
            return True, None
        
        # 检查文件是否存在
        if not 原始路径.exists():
            错误信息 = f"源文件不存在: {原始路径}"
            媒体文件.rename_status = "failed"
            媒体文件.error_message = 错误信息
            return False, 错误信息
        
        # 检查目标文件是否已存在
        if 新路径.exists() and 新路径 != 原始路径:
            # 处理文件名冲突：添加数字后缀
            基础名 = 新路径.stem
            扩展名 = 新路径.suffix
            父目录 = 新路径.parent
            计数 = 1
            
            while 新路径.exists():
                新文件名_无扩展名 = f"{基础名}_{计数}"
                新路径 = 父目录 / f"{新文件名_无扩展名}{扩展名}"
                计数 += 1
        
        # 创建目标目录（如果需要）
        新路径.parent.mkdir(parents=True, exist_ok=True)
        
        # 执行重命名
        try:
            原始路径.rename(新路径)
            
            # 更新媒体文件对象
            媒体文件.path = 新路径
            媒体文件.new_name = 新路径.name
            媒体文件.rename_status = "success"
            
            # 记录历史
            if self.创建备份:
                历史 = 重命名历史记录(
                    原始路径=原始路径,
                    新路径=新路径,
                    成功=True,
                )
                self._历史记录.append(历史)
            
            return True, None
            
        except Exception as e:
            错误信息 = f"重命名失败: {e}"
            媒体文件.rename_status = "failed"
            媒体文件.error_message = 错误信息
            
            # 记录失败历史
            if self.创建备份:
                历史 = 重命名历史记录(
                    原始路径=原始路径,
                    新路径=新路径,
                    成功=False,
                    错误信息=错误信息,
                )
                self._历史记录.append(历史)
            
            return False, 错误信息
    
    def 批量重命名(self, 媒体文件列表: List[MediaFile], 规则: RenameRule) -> Dict[str, Any]:
        """
        批量重命名文件
        
        Args:
            媒体文件列表: 媒体文件列表
            规则: 重命名规则
        
        Returns:
            Dict[str, Any]: 重命名结果统计
        """
        结果 = {
            "总数": len(媒体文件列表),
            "成功": 0,
            "失败": 0,
            "跳过": 0,
            "详情": [],
        }
        
        for 媒体文件 in 媒体文件列表:
            # 检查媒体类型是否匹配
            if 媒体文件.media_type != 规则.media_type and 规则.media_type != MediaType.UNKNOWN:
                结果["跳过"] += 1
                结果["详情"].append({
                    "文件": str(媒体文件.path),
                    "状态": "跳过",
                    "原因": f"媒体类型不匹配: {媒体文件.media_type.value} != {规则.media_type.value}",
                })
                continue
            
            成功, 错误 = self.重命名文件(媒体文件, 规则)
            
            if 成功:
                结果["成功"] += 1
                结果["详情"].append({
                    "文件": str(媒体文件.path),
                    "状态": "成功",
                    "新名称": 媒体文件.new_name,
                })
            else:
                结果["失败"] += 1
                结果["详情"].append({
                    "文件": str(媒体文件.path),
                    "状态": "失败",
                    "错误": 错误,
                })
        
        return 结果
    
    def 撤销重命名(self, 历史索引: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        撤销重命名操作
        
        Args:
            历史索引: 历史记录索引，None 表示撤销最后一次操作
        
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误信息)
        """
        if not self._历史记录:
            return False, "没有可撤销的操作"
        
        # 获取要撤销的历史记录
        if 历史索引 is None:
            历史 = self._历史记录[-1]
        else:
            if 历史索引 < 0 or 历史索引 >= len(self._历史记录):
                return False, "无效的历史索引"
            历史 = self._历史记录[历史索引]
        
        # 只能撤销成功的操作
        if not 历史.成功:
            return False, "该操作未成功，无法撤销"
        
        # 检查文件是否存在
        if not 历史.新路径.exists():
            return False, f"文件不存在: {历史.新路径}"
        
        # 检查原始路径是否已被占用
        if 历史.原始路径.exists():
            return False, f"原始路径已存在: {历史.原始路径}"
        
        try:
            # 执行撤销（将新路径改回原始路径）
            历史.新路径.rename(历史.原始路径)
            
            # 从历史记录中移除
            if 历史索引 is None:
                self._历史记录.pop()
            else:
                self._历史记录.pop(历史索引)
            
            return True, None
            
        except Exception as e:
            return False, f"撤销失败: {e}"
    
    def 获取历史记录(self) -> List[重命名历史记录]:
        """获取重命名历史记录"""
        return self._历史记录.copy()
    
    def 清空历史记录(self):
        """清空历史记录"""
        self._历史记录.clear()
    
    def 保存历史到文件(self, 文件路径: Path) -> bool:
        """
        保存历史记录到文件
        
        Args:
            文件路径: 保存路径
        
        Returns:
            bool: 是否保存成功
        """
        try:
            文件路径.parent.mkdir(parents=True, exist_ok=True)
            
            历史数据 = [历史.to_dict() for 历史 in self._历史记录]
            with open(文件路径, 'w', encoding='utf-8') as f:
                json.dump(历史数据, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return False
    
    def 从文件加载历史(self, 文件路径: Path) -> bool:
        """
        从文件加载历史记录
        
        Args:
            文件路径: 文件路径
        
        Returns:
            bool: 是否加载成功
        """
        try:
            if not 文件路径.exists():
                return False
            
            with open(文件路径, 'r', encoding='utf-8') as f:
                历史数据 = json.load(f)
            
            self._历史记录 = [重命名历史记录.from_dict(数据) for 数据 in 历史数据]
            
            return True
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return False
    
    # 英文别名方法
    def generate_new_filename(self, media_file: MediaFile, rule: RenameRule) -> Tuple[bool, str, Optional[str]]:
        """生成新文件名（英文别名）"""
        return self.生成新文件名(media_file, rule)
    
    def rename_file(self, media_file: MediaFile, rule: RenameRule) -> Tuple[bool, Optional[str]]:
        """重命名文件（英文别名）"""
        return self.重命名文件(media_file, rule)
    
    def batch_rename(self, media_files: List[MediaFile], rule: RenameRule) -> Dict[str, Any]:
        """批量重命名（英文别名）"""
        return self.批量重命名(media_files, rule)
    
    def undo_rename(self, history_index: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """撤销重命名（英文别名）"""
        return self.撤销重命名(history_index)
    
    def get_history(self) -> List[重命名历史记录]:
        """获取历史记录（英文别名）"""
        return self.获取历史记录()
    
    def clear_history(self):
        """清空历史记录（英文别名）"""
        return self.清空历史记录()
    
    def save_history_to_file(self, file_path: Path) -> bool:
        """保存历史到文件（英文别名）"""
        return self.保存历史到文件(file_path)
    
    def load_history_from_file(self, file_path: Path) -> bool:
        """从文件加载历史（英文别名）"""
        return self.从文件加载历史(file_path)


# 英文别名
Renamer = 重命名器


def 创建预定义规则(模板名称: str) -> Optional[RenameRule]:
    """
    根据预定义模板创建重命名规则
    
    Args:
        模板名称: 预定义模板名称
    
    Returns:
        Optional[RenameRule]: 规则对象，如果模板不存在返回 None
    """
    if 模板名称 not in 预定义模板:
        return None
    
    模板信息 = 预定义模板[模板名称]
    
    return RenameRule(
        name=模板信息["名称"],
        description=模板信息["描述"],
        template=模板信息["模板"],
        media_type=模板信息["媒体类型"],
        example=模板信息.get("示例"),
    )


# 英文别名
def create_predefined_rule(template_name: str) -> Optional[RenameRule]:
    """创建预定义规则（英文别名）"""
    return 创建预定义规则(template_name)
