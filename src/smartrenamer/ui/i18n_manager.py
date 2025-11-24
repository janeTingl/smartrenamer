"""
国际化管理器

负责应用程序语言和翻译的管理
"""
import logging
from pathlib import Path
from typing import Optional, Dict
from PySide6.QtCore import QTranslator, QLocale, QCoreApplication
from PySide6.QtWidgets import QApplication


logger = logging.getLogger(__name__)


class I18nManager:
    """国际化管理器"""
    
    # 可用的语言
    AVAILABLE_LANGUAGES = {
        "zh_CN": "简体中文",
        "en_US": "English",
    }
    
    def __init__(self):
        """初始化国际化管理器"""
        self._current_language: Optional[str] = None
        self._translator: Optional[QTranslator] = None
        self._i18n_dir = self._get_i18n_dir()
        
    def _get_i18n_dir(self) -> Path:
        """获取国际化文件目录路径"""
        # 尝试多个可能的路径
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "i18n",  # 开发环境
            Path(__file__).parent.parent / "i18n",  # 打包后
            Path.cwd() / "i18n",  # 当前目录
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        # 如果都不存在，返回第一个路径
        return possible_paths[0]
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        return self.AVAILABLE_LANGUAGES.copy()
    
    def get_system_language(self) -> str:
        """获取系统语言"""
        locale = QLocale.system()
        locale_name = locale.name()  # 例如 "zh_CN"
        
        # 如果系统语言在支持列表中，返回它
        if locale_name in self.AVAILABLE_LANGUAGES:
            return locale_name
        
        # 尝试语言代码（忽略国家代码）
        lang_code = locale_name.split("_")[0]  # "zh"
        for key in self.AVAILABLE_LANGUAGES.keys():
            if key.startswith(lang_code):
                return key
        
        # 默认返回简体中文
        return "zh_CN"
    
    def load_translation(self, app: QApplication, language: str) -> bool:
        """
        加载翻译文件
        
        Args:
            app: QApplication 实例
            language: 语言代码（如 "zh_CN", "en_US"）
            
        Returns:
            bool: 是否成功加载
        """
        if language not in self.AVAILABLE_LANGUAGES:
            logger.warning(f"不支持的语言: {language}")
            return False
        
        try:
            # 移除旧的翻译器
            if self._translator is not None:
                app.removeTranslator(self._translator)
                self._translator = None
            
            # 如果是中文，不需要加载翻译文件（默认就是中文）
            if language == "zh_CN":
                self._current_language = language
                logger.info(f"使用默认中文")
                return True
            
            # 创建新的翻译器
            translator = QTranslator(app)
            
            # 加载翻译文件
            qm_file = self._i18n_dir / f"smartrenamer_{language}.qm"
            
            if not qm_file.exists():
                logger.warning(f"翻译文件不存在: {qm_file}，使用内置翻译")
                # 使用内置翻译
                return self._load_builtin_translation(app, language)
            
            if translator.load(str(qm_file)):
                app.installTranslator(translator)
                self._translator = translator
                self._current_language = language
                logger.info(f"已加载翻译: {language}")
                return True
            else:
                logger.error(f"加载翻译文件失败: {qm_file}")
                return False
                
        except Exception as e:
            logger.error(f"加载翻译失败: {e}")
            return False
    
    def _load_builtin_translation(self, app: QApplication, language: str) -> bool:
        """
        加载内置翻译（作为备选）
        
        Args:
            app: QApplication 实例
            language: 语言代码
            
        Returns:
            bool: 是否成功加载
        """
        # 这里可以定义一些关键的内置翻译
        # 目前我们只是标记语言已切换，实际文本仍使用默认（中文）
        self._current_language = language
        logger.info(f"使用内置翻译: {language}（功能受限）")
        return True
    
    def get_current_language(self) -> Optional[str]:
        """获取当前语言"""
        return self._current_language
    
    def get_current_language_name(self) -> str:
        """获取当前语言显示名称"""
        if self._current_language:
            return self.AVAILABLE_LANGUAGES.get(self._current_language, self._current_language)
        return "未设置"


# 全局国际化管理器实例
_i18n_manager: Optional[I18nManager] = None


def get_i18n_manager() -> I18nManager:
    """
    获取全局国际化管理器实例
    
    Returns:
        I18nManager: 国际化管理器实例
    """
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def load_translation(app: QApplication, language: str) -> bool:
    """
    加载翻译（便捷函数）
    
    Args:
        app: QApplication 实例
        language: 语言代码
        
    Returns:
        bool: 是否成功加载
    """
    return get_i18n_manager().load_translation(app, language)
