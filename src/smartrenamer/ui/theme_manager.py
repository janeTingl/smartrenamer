"""
主题管理器

负责应用程序主题的加载和应用
"""
import logging
from pathlib import Path
from typing import Optional, Dict
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor


logger = logging.getLogger(__name__)


class ThemeManager:
    """主题管理器"""
    
    # 可用的主题
    AVAILABLE_THEMES = ["light", "dark"]
    
    # 主题显示名称
    THEME_NAMES = {
        "light": "亮色主题",
        "dark": "暗色主题"
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self._current_theme: Optional[str] = None
        self._theme_dir = self._get_theme_dir()
        
    def _get_theme_dir(self) -> Path:
        """获取主题目录路径"""
        # 尝试多个可能的路径
        possible_paths = [
            Path(__file__).parent.parent.parent.parent / "assets" / "themes",  # 开发环境
            Path(__file__).parent.parent / "assets" / "themes",  # 打包后
            Path.cwd() / "assets" / "themes",  # 当前目录
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        # 如果都不存在，返回第一个路径（会在后续创建）
        return possible_paths[0]
    
    def get_available_themes(self) -> list:
        """获取可用主题列表"""
        return self.AVAILABLE_THEMES.copy()
    
    def get_theme_display_name(self, theme_name: str) -> str:
        """获取主题显示名称"""
        return self.THEME_NAMES.get(theme_name, theme_name)
    
    def load_theme_stylesheet(self, theme_name: str) -> str:
        """
        加载主题样式表
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: 样式表内容
        """
        if theme_name not in self.AVAILABLE_THEMES:
            logger.warning(f"未知的主题: {theme_name}，使用 light 主题")
            theme_name = "light"
        
        qss_file = self._theme_dir / f"{theme_name}.qss"
        
        if not qss_file.exists():
            logger.warning(f"主题文件不存在: {qss_file}，使用内置主题")
            return self._get_builtin_stylesheet(theme_name)
        
        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"加载主题文件失败: {e}")
            return self._get_builtin_stylesheet(theme_name)
    
    def _get_builtin_stylesheet(self, theme_name: str) -> str:
        """
        获取内置样式表（作为备选）
        
        Args:
            theme_name: 主题名称
            
        Returns:
            str: 样式表内容
        """
        if theme_name == "dark":
            return """
                QMainWindow, QDialog, QWidget {
                    background-color: #2b2b2b;
                    color: #d4d4d4;
                }
                
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                }
                
                QMenuBar::item:selected {
                    background-color: #505050;
                }
                
                QMenu {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                }
                
                QMenu::item:selected {
                    background-color: #505050;
                }
                
                QToolBar {
                    background-color: #3c3c3c;
                    border: none;
                }
                
                QPushButton {
                    background-color: #505050;
                    color: #d4d4d4;
                    border: 1px solid #666666;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                
                QPushButton:hover {
                    background-color: #606060;
                }
                
                QPushButton:pressed {
                    background-color: #404040;
                }
                
                QLineEdit, QTextEdit, QPlainTextEdit {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    padding: 3px;
                }
                
                QTableWidget {
                    background-color: #2b2b2b;
                    alternate-background-color: #323232;
                    gridline-color: #555555;
                }
                
                QHeaderView::section {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #555555;
                }
                
                QTabBar::tab {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    padding: 5px 10px;
                }
                
                QTabBar::tab:selected {
                    background-color: #505050;
                }
                
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                
                QGroupBox::title {
                    color: #d4d4d4;
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
            """
        else:  # light theme
            return """
                QMainWindow, QDialog, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                
                QGroupBox::title {
                    color: #000000;
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
            """
    
    def apply_theme(self, app: QApplication, theme_name: str) -> bool:
        """
        应用主题到应用程序
        
        Args:
            app: QApplication 实例
            theme_name: 主题名称
            
        Returns:
            bool: 是否成功应用
        """
        if theme_name not in self.AVAILABLE_THEMES:
            logger.warning(f"未知的主题: {theme_name}")
            return False
        
        try:
            # 加载样式表
            stylesheet = self.load_theme_stylesheet(theme_name)
            app.setStyleSheet(stylesheet)
            
            # 设置调色板（作为补充）
            self._apply_palette(app, theme_name)
            
            self._current_theme = theme_name
            logger.info(f"已应用主题: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"应用主题失败: {e}")
            return False
    
    def _apply_palette(self, app: QApplication, theme_name: str):
        """
        应用调色板
        
        Args:
            app: QApplication 实例
            theme_name: 主题名称
        """
        palette = QPalette()
        
        if theme_name == "dark":
            # 暗色主题调色板
            palette.setColor(QPalette.Window, QColor(43, 43, 43))
            palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
            palette.setColor(QPalette.Base, QColor(60, 60, 60))
            palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ToolTipBase, QColor(212, 212, 212))
            palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
            palette.setColor(QPalette.Text, QColor(212, 212, 212))
            palette.setColor(QPalette.Button, QColor(80, 80, 80))
            palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        else:  # light theme
            # 亮色主题使用系统默认调色板
            palette = app.style().standardPalette()
        
        app.setPalette(palette)
    
    def get_current_theme(self) -> Optional[str]:
        """获取当前主题"""
        return self._current_theme


# 全局主题管理器实例
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """
    获取全局主题管理器实例
    
    Returns:
        ThemeManager: 主题管理器实例
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def apply_theme(app: QApplication, theme_name: str) -> bool:
    """
    应用主题（便捷函数）
    
    Args:
        app: QApplication 实例
        theme_name: 主题名称
        
    Returns:
        bool: 是否成功应用
    """
    return get_theme_manager().apply_theme(app, theme_name)
