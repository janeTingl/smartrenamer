"""
测试配置管理模块
"""
import pytest
from pathlib import Path
from smartrenamer.core.config import Config


class TestConfig:
    """测试 Config 类"""
    
    def test_create_default_config(self):
        """测试创建默认配置"""
        config = Config()
        
        assert config.tmdb_language == "zh-CN"
        assert config.create_backup is True
        assert config.preview_before_rename is True
        assert len(config.supported_extensions) > 0
    
    def test_config_validation_without_api_key(self):
        """测试没有 API Key 的配置验证"""
        config = Config()
        is_valid, error_msg = config.validate()
        
        assert not is_valid
        assert "API Key" in error_msg
    
    def test_config_validation_with_api_key(self):
        """测试有 API Key 的配置验证"""
        config = Config(tmdb_api_key="test_api_key_12345")
        is_valid, error_msg = config.validate()
        
        assert is_valid
        assert error_msg is None
    
    def test_config_update(self):
        """测试配置更新"""
        config = Config()
        config.update(theme="dark", auto_rename=True)
        
        assert config.theme == "dark"
        assert config.auto_rename is True
    
    def test_config_to_dict(self):
        """测试配置转换为字典"""
        config = Config(tmdb_api_key="test_key")
        data = config.to_dict()
        
        assert isinstance(data, dict)
        assert data["tmdb_api_key"] == "test_key"
        assert data["tmdb_language"] == "zh-CN"
    
    def test_supported_extensions(self):
        """测试支持的文件扩展名"""
        config = Config()
        
        assert ".mkv" in config.supported_extensions
        assert ".mp4" in config.supported_extensions
        assert ".avi" in config.supported_extensions
