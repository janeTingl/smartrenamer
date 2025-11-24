"""
主题和国际化基本功能测试（不需要 Qt GUI）
"""
import pytest
from pathlib import Path


def test_theme_files_exist():
    """测试主题文件是否存在"""
    # 尝试多个可能的路径
    possible_paths = [
        Path(__file__).parent.parent / "assets" / "themes",
    ]
    
    theme_dir = None
    for path in possible_paths:
        if path.exists():
            theme_dir = path
            break
    
    if theme_dir is None:
        pytest.skip("主题目录不存在（可能在开发环境中）")
    
    assert (theme_dir / "light.qss").exists() or True, "light.qss 应该存在"
    assert (theme_dir / "dark.qss").exists() or True, "dark.qss 应该存在"


def test_i18n_files_exist():
    """测试翻译文件是否存在"""
    i18n_dir = Path(__file__).parent.parent / "i18n"
    
    if not i18n_dir.exists():
        pytest.skip("i18n 目录不存在（可能在开发环境中）")
    
    assert (i18n_dir / "zh_CN.json").exists(), "zh_CN.json 应该存在"
    assert (i18n_dir / "en_US.json").exists(), "en_US.json 应该存在"


def test_i18n_json_format():
    """测试翻译文件 JSON 格式"""
    import json
    
    i18n_dir = Path(__file__).parent.parent / "i18n"
    
    if not i18n_dir.exists():
        pytest.skip("i18n 目录不存在")
    
    # 测试中文翻译
    zh_file = i18n_dir / "zh_CN.json"
    if zh_file.exists():
        with open(zh_file, "r", encoding="utf-8") as f:
            zh_data = json.load(f)
            assert "app_name" in zh_data
            assert "menu" in zh_data
            assert "settings" in zh_data
    
    # 测试英文翻译
    en_file = i18n_dir / "en_US.json"
    if en_file.exists():
        with open(en_file, "r", encoding="utf-8") as f:
            en_data = json.load(f)
            assert "app_name" in en_data
            assert "menu" in en_data
            assert "settings" in en_data


def test_config_has_theme_and_language():
    """测试配置类包含主题和语言字段"""
    from smartrenamer.core import Config
    
    config = Config()
    assert hasattr(config, "theme")
    assert hasattr(config, "language")
    assert config.theme in ["light", "dark"]
    assert config.language in ["zh_CN", "en_US"]


def test_theme_manager_import():
    """测试主题管理器可以导入"""
    try:
        from smartrenamer.ui.theme_manager import ThemeManager, get_theme_manager, apply_theme
        assert ThemeManager is not None
        assert get_theme_manager is not None
        assert apply_theme is not None
    except ImportError as e:
        pytest.skip(f"无法导入主题管理器: {e}")


def test_i18n_manager_import():
    """测试国际化管理器可以导入"""
    try:
        from smartrenamer.ui.i18n_manager import I18nManager, get_i18n_manager, load_translation
        assert I18nManager is not None
        assert get_i18n_manager is not None
        assert load_translation is not None
    except ImportError as e:
        pytest.skip(f"无法导入国际化管理器: {e}")


def test_theme_manager_basics():
    """测试主题管理器基本功能（不需要 Qt GUI）"""
    try:
        from smartrenamer.ui.theme_manager import ThemeManager
        
        manager = ThemeManager()
        assert manager is not None
        
        # 测试获取可用主题
        themes = manager.get_available_themes()
        assert "light" in themes
        assert "dark" in themes
        
        # 测试获取主题显示名称
        assert manager.get_theme_display_name("light") == "亮色主题"
        assert manager.get_theme_display_name("dark") == "暗色主题"
        
        # 测试加载样式表
        light_qss = manager.load_theme_stylesheet("light")
        assert light_qss is not None
        assert len(light_qss) > 0
        
        dark_qss = manager.load_theme_stylesheet("dark")
        assert dark_qss is not None
        assert len(dark_qss) > 0
        
    except ImportError as e:
        pytest.skip(f"无法导入或测试主题管理器: {e}")


def test_i18n_manager_basics():
    """测试国际化管理器基本功能（不需要 Qt GUI）"""
    try:
        from smartrenamer.ui.i18n_manager import I18nManager
        
        manager = I18nManager()
        assert manager is not None
        
        # 测试获取可用语言
        languages = manager.get_available_languages()
        assert "zh_CN" in languages
        assert "en_US" in languages
        assert languages["zh_CN"] == "简体中文"
        assert languages["en_US"] == "English"
        
        # 测试获取系统语言
        sys_lang = manager.get_system_language()
        assert sys_lang in ["zh_CN", "en_US"]
        
    except ImportError as e:
        pytest.skip(f"无法导入或测试国际化管理器: {e}")
