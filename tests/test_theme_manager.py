"""
主题管理器测试
"""
import os
# 必须在导入 Qt 之前设置
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import pytest
import sys
from PySide6.QtWidgets import QApplication
from smartrenamer.ui.theme_manager import ThemeManager, get_theme_manager, apply_theme


@pytest.fixture(scope="module")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def theme_manager():
    """主题管理器 fixture"""
    return ThemeManager()


def test_theme_manager_creation(theme_manager):
    """测试主题管理器创建"""
    assert theme_manager is not None
    assert theme_manager._current_theme is None


def test_get_available_themes(theme_manager):
    """测试获取可用主题列表"""
    themes = theme_manager.get_available_themes()
    assert "light" in themes
    assert "dark" in themes
    assert len(themes) >= 2


def test_get_theme_display_name(theme_manager):
    """测试获取主题显示名称"""
    assert theme_manager.get_theme_display_name("light") == "亮色主题"
    assert theme_manager.get_theme_display_name("dark") == "暗色主题"


def test_load_theme_stylesheet(theme_manager):
    """测试加载主题样式表"""
    light_qss = theme_manager.load_theme_stylesheet("light")
    assert light_qss is not None
    assert len(light_qss) > 0
    
    dark_qss = theme_manager.load_theme_stylesheet("dark")
    assert dark_qss is not None
    assert len(dark_qss) > 0
    
    # 验证内容不同
    assert light_qss != dark_qss


def test_load_unknown_theme(theme_manager):
    """测试加载未知主题"""
    qss = theme_manager.load_theme_stylesheet("unknown")
    # 应该回退到 light 主题
    assert qss is not None
    assert len(qss) > 0


def test_apply_theme(theme_manager, qapp):
    """测试应用主题"""
    # 应用亮色主题
    result = theme_manager.apply_theme(qapp, "light")
    assert result is True
    assert theme_manager.get_current_theme() == "light"
    
    # 应用暗色主题
    result = theme_manager.apply_theme(qapp, "dark")
    assert result is True
    assert theme_manager.get_current_theme() == "dark"


def test_apply_invalid_theme(theme_manager, qapp):
    """测试应用无效主题"""
    result = theme_manager.apply_theme(qapp, "invalid")
    assert result is False


def test_get_theme_manager():
    """测试获取全局主题管理器"""
    manager1 = get_theme_manager()
    manager2 = get_theme_manager()
    
    # 应该返回同一个实例
    assert manager1 is manager2


def test_apply_theme_convenience_function(qapp):
    """测试便捷函数"""
    result = apply_theme(qapp, "light")
    assert result is True
    
    result = apply_theme(qapp, "dark")
    assert result is True


def test_builtin_stylesheet(theme_manager):
    """测试内置样式表"""
    light_qss = theme_manager._get_builtin_stylesheet("light")
    assert light_qss is not None
    assert len(light_qss) > 0
    
    dark_qss = theme_manager._get_builtin_stylesheet("dark")
    assert dark_qss is not None
    assert len(dark_qss) > 0
    
    # 暗色主题应该包含暗色背景
    assert "#2b2b2b" in dark_qss or "background-color" in dark_qss
