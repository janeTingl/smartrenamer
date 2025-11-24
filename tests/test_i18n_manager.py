"""
国际化管理器测试
"""
import os
# 必须在导入 Qt 之前设置
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import pytest
import sys
from PySide6.QtWidgets import QApplication
from smartrenamer.ui.i18n_manager import I18nManager, get_i18n_manager, load_translation


@pytest.fixture(scope="module")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def i18n_manager():
    """国际化管理器 fixture"""
    return I18nManager()


def test_i18n_manager_creation(i18n_manager):
    """测试国际化管理器创建"""
    assert i18n_manager is not None
    assert i18n_manager._current_language is None


def test_get_available_languages(i18n_manager):
    """测试获取可用语言列表"""
    languages = i18n_manager.get_available_languages()
    assert "zh_CN" in languages
    assert "en_US" in languages
    assert languages["zh_CN"] == "简体中文"
    assert languages["en_US"] == "English"


def test_get_system_language(i18n_manager):
    """测试获取系统语言"""
    lang = i18n_manager.get_system_language()
    assert lang in ["zh_CN", "en_US"]


def test_load_translation_chinese(i18n_manager, qapp):
    """测试加载中文翻译"""
    result = i18n_manager.load_translation(qapp, "zh_CN")
    assert result is True
    assert i18n_manager.get_current_language() == "zh_CN"


def test_load_translation_english(i18n_manager, qapp):
    """测试加载英文翻译"""
    # 英文翻译文件可能不存在，但应该能够加载（使用内置翻译）
    result = i18n_manager.load_translation(qapp, "en_US")
    assert result is True
    assert i18n_manager.get_current_language() == "en_US"


def test_load_invalid_language(i18n_manager, qapp):
    """测试加载无效语言"""
    result = i18n_manager.load_translation(qapp, "invalid")
    assert result is False


def test_get_current_language_name(i18n_manager, qapp):
    """测试获取当前语言显示名称"""
    i18n_manager.load_translation(qapp, "zh_CN")
    assert i18n_manager.get_current_language_name() == "简体中文"
    
    i18n_manager.load_translation(qapp, "en_US")
    assert i18n_manager.get_current_language_name() == "English"


def test_get_i18n_manager():
    """测试获取全局国际化管理器"""
    manager1 = get_i18n_manager()
    manager2 = get_i18n_manager()
    
    # 应该返回同一个实例
    assert manager1 is manager2


def test_load_translation_convenience_function(qapp):
    """测试便捷函数"""
    result = load_translation(qapp, "zh_CN")
    assert result is True
    
    result = load_translation(qapp, "en_US")
    assert result is True


def test_switch_language(i18n_manager, qapp):
    """测试切换语言"""
    # 先加载中文
    result = i18n_manager.load_translation(qapp, "zh_CN")
    assert result is True
    assert i18n_manager.get_current_language() == "zh_CN"
    
    # 再切换到英文
    result = i18n_manager.load_translation(qapp, "en_US")
    assert result is True
    assert i18n_manager.get_current_language() == "en_US"
    
    # 再切换回中文
    result = i18n_manager.load_translation(qapp, "zh_CN")
    assert result is True
    assert i18n_manager.get_current_language() == "zh_CN"
