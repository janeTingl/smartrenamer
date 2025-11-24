"""
存储适配器测试模块

测试本地和网盘存储适配器的功能
"""

import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from smartrenamer.storage import (
    StorageAdapter,
    StorageFile,
    StorageType,
    LocalStorageAdapter,
    Storage115Adapter,
    Storage123Adapter,
    StorageManager,
    get_storage_manager
)


class TestStorageFile:
    """StorageFile 测试类"""
    
    def test_创建存储文件(self):
        """测试创建存储文件对象"""
        文件 = StorageFile(
            路径="/test/file.txt",
            名称="file.txt",
            大小=1024,
            是否目录=False,
            修改时间=datetime.now(),
            文件ID="123",
            父目录ID="0"
        )
        
        assert 文件.路径 == "/test/file.txt"
        assert 文件.名称 == "file.txt"
        assert 文件.大小 == 1024
        assert not 文件.是否目录
        assert 文件.文件ID == "123"
    
    def test_英文接口(self):
        """测试英文兼容接口"""
        文件 = StorageFile(
            路径="/test/file.txt",
            名称="file.txt",
            大小=1024,
            是否目录=False,
            修改时间=datetime.now()
        )
        
        assert 文件.path == 文件.路径
        assert 文件.name == 文件.名称
        assert 文件.size == 文件.大小
        assert 文件.is_dir == 文件.是否目录


class TestLocalStorageAdapter:
    """本地存储适配器测试类"""
    
    def test_创建本地适配器(self):
        """测试创建本地存储适配器"""
        适配器 = LocalStorageAdapter()
        assert 适配器 is not None
        assert 适配器.获取类型() == StorageType.LOCAL
    
    def test_连接(self):
        """测试连接"""
        适配器 = LocalStorageAdapter()
        assert 适配器.连接()
        assert 适配器.已连接
    
    def test_列出文件(self, tmp_path):
        """测试列出文件"""
        # 创建测试文件
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        文件列表 = 适配器.列出文件(str(tmp_path))
        assert len(文件列表) == 3
        
        # 验证文件信息
        文件名列表 = [f.名称 for f in 文件列表]
        assert "file1.txt" in 文件名列表
        assert "file2.txt" in 文件名列表
        assert "subdir" in 文件名列表
    
    def test_列出文件_递归(self, tmp_path):
        """测试递归列出文件"""
        # 创建测试文件结构
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.txt").write_text("test")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        文件列表 = 适配器.列出文件(str(tmp_path), 递归=True)
        assert len(文件列表) >= 3  # 至少包含 file1.txt, subdir, file2.txt
    
    def test_列出文件_过滤器(self, tmp_path):
        """测试使用过滤器列出文件"""
        # 创建测试文件
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.log").write_text("test")
        (tmp_path / "file3.txt").write_text("test")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        # 只列出 .txt 文件
        def 过滤txt(f: StorageFile) -> bool:
            return f.名称.endswith(".txt")
        
        文件列表 = 适配器.列出文件(str(tmp_path), 过滤器=过滤txt)
        assert len(文件列表) == 2
        assert all(f.名称.endswith(".txt") for f in 文件列表)
    
    def test_获取文件信息(self, tmp_path):
        """测试获取文件信息"""
        测试文件 = tmp_path / "test.txt"
        测试文件.write_text("hello world")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        文件信息 = 适配器.获取文件信息(str(测试文件))
        assert 文件信息 is not None
        assert 文件信息.名称 == "test.txt"
        assert 文件信息.大小 == 11
        assert not 文件信息.是否目录
    
    def test_读取文件(self, tmp_path):
        """测试读取文件"""
        测试文件 = tmp_path / "test.txt"
        测试文件.write_text("hello world")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        读取路径 = 适配器.读取文件(str(测试文件))
        assert 读取路径 is not None
        assert 读取路径 == 测试文件
    
    def test_写入文件(self, tmp_path):
        """测试写入文件"""
        源文件 = tmp_path / "source.txt"
        源文件.write_text("hello world")
        
        目标文件 = tmp_path / "target.txt"
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        assert 适配器.写入文件(源文件, str(目标文件))
        assert 目标文件.exists()
        assert 目标文件.read_text() == "hello world"
    
    def test_删除文件(self, tmp_path):
        """测试删除文件"""
        测试文件 = tmp_path / "test.txt"
        测试文件.write_text("test")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        assert 适配器.删除文件(str(测试文件))
        assert not 测试文件.exists()
    
    def test_重命名文件(self, tmp_path):
        """测试重命名文件"""
        源文件 = tmp_path / "old.txt"
        源文件.write_text("test")
        
        目标文件 = tmp_path / "new.txt"
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        assert 适配器.重命名文件(str(源文件), str(目标文件))
        assert not 源文件.exists()
        assert 目标文件.exists()
    
    def test_创建目录(self, tmp_path):
        """测试创建目录"""
        新目录 = tmp_path / "newdir"
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        assert 适配器.创建目录(str(新目录))
        assert 新目录.exists()
        assert 新目录.is_dir()
    
    def test_文件存在(self, tmp_path):
        """测试检查文件存在"""
        测试文件 = tmp_path / "test.txt"
        测试文件.write_text("test")
        
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        assert 适配器.文件存在(str(测试文件))
        assert not 适配器.文件存在(str(tmp_path / "not_exist.txt"))
    
    def test_获取存储空间信息(self):
        """测试获取存储空间信息"""
        适配器 = LocalStorageAdapter()
        适配器.连接()
        
        空间信息 = 适配器.获取存储空间信息()
        assert "总空间" in 空间信息
        assert "已用空间" in 空间信息
        assert "剩余空间" in 空间信息
        assert "使用率" in 空间信息
        assert 空间信息["总空间"] > 0


class TestStorage115Adapter:
    """115 网盘适配器测试类（使用 Mock）"""
    
    def test_创建115适配器(self):
        """测试创建 115 网盘适配器"""
        适配器 = Storage115Adapter({"cookie": "test_cookie"})
        assert 适配器 is not None
        assert 适配器.获取类型() == StorageType.STORAGE_115
    
    @patch('smartrenamer.storage.storage_115.requests.Session')
    def test_连接成功(self, mock_session):
        """测试连接成功"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "state": True,
            "data": {
                "user_id": "123",
                "user_name": "test_user"
            }
        }
        mock_session.return_value.get.return_value = mock_response
        
        适配器 = Storage115Adapter({"cookie": "test_cookie"})
        assert 适配器.连接()
    
    @patch('smartrenamer.storage.storage_115.requests.Session')
    def test_连接失败(self, mock_session):
        """测试连接失败"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "state": False,
            "error": "invalid cookie"
        }
        mock_session.return_value.get.return_value = mock_response
        
        适配器 = Storage115Adapter({"cookie": "invalid_cookie"})
        assert not 适配器.连接()
    
    def test_未配置cookie(self):
        """测试未配置 cookie"""
        适配器 = Storage115Adapter({})
        assert not 适配器.连接()


class TestStorage123Adapter:
    """123 网盘适配器测试类（使用 Mock）"""
    
    def test_创建123适配器(self):
        """测试创建 123 网盘适配器"""
        适配器 = Storage123Adapter({"access_token": "test_token"})
        assert 适配器 is not None
        assert 适配器.获取类型() == StorageType.STORAGE_123
    
    @patch('smartrenamer.storage.storage_123.requests.Session')
    def test_连接成功(self, mock_session):
        """测试连接成功"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "nickname": "test_user"
            }
        }
        mock_session.return_value.get.return_value = mock_response
        
        适配器 = Storage123Adapter({"access_token": "test_token"})
        assert 适配器.连接()
    
    @patch('smartrenamer.storage.storage_123.requests.Session')
    def test_连接失败_token过期(self, mock_session):
        """测试 token 过期"""
        # Mock API 响应（token 失效）
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 401,
            "message": "token expired"
        }
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = mock_response
        
        适配器 = Storage123Adapter({
            "access_token": "expired_token",
            "refresh_token": "refresh_token"
        })
        assert not 适配器.连接()
    
    def test_未配置token(self):
        """测试未配置 token"""
        适配器 = Storage123Adapter({})
        assert not 适配器.连接()


class TestStorageManager:
    """存储管理器测试类"""
    
    def test_创建管理器(self):
        """测试创建存储管理器"""
        管理器 = StorageManager()
        assert 管理器 is not None
    
    def test_创建本地适配器(self):
        """测试创建本地适配器"""
        管理器 = StorageManager()
        适配器 = 管理器.创建适配器("local", {})
        assert 适配器 is not None
        assert isinstance(适配器, LocalStorageAdapter)
    
    def test_创建115适配器(self):
        """测试创建 115 适配器"""
        管理器 = StorageManager()
        适配器 = 管理器.创建适配器("115", {"cookie": "test"})
        assert 适配器 is not None
        assert isinstance(适配器, Storage115Adapter)
    
    def test_创建123适配器(self):
        """测试创建 123 适配器"""
        管理器 = StorageManager()
        适配器 = 管理器.创建适配器("123", {"access_token": "test"})
        assert 适配器 is not None
        assert isinstance(适配器, Storage123Adapter)
    
    def test_不支持的类型(self):
        """测试不支持的存储类型"""
        管理器 = StorageManager()
        适配器 = 管理器.创建适配器("unknown", {})
        assert 适配器 is None
    
    def test_获取适配器_带缓存(self):
        """测试获取适配器（带缓存）"""
        管理器 = StorageManager()
        
        # 第一次获取
        适配器1 = 管理器.获取适配器("local", {})
        assert 适配器1 is not None
        
        # 第二次获取（应该返回缓存的实例）
        适配器2 = 管理器.获取适配器("local")
        assert 适配器2 is 适配器1
    
    def test_切换适配器(self):
        """测试切换适配器"""
        管理器 = StorageManager()
        
        # 切换到本地适配器
        assert 管理器.切换适配器("local", {})
        assert 管理器.获取当前类型() == "local"
        assert isinstance(管理器.获取当前适配器(), LocalStorageAdapter)
    
    def test_列出可用适配器(self):
        """测试列出可用适配器"""
        管理器 = StorageManager()
        适配器列表 = 管理器.列出可用适配器()
        
        assert "local" in 适配器列表
        assert "115" in 适配器列表
        assert "123" in 适配器列表
    
    def test_关闭所有适配器(self):
        """测试关闭所有适配器"""
        管理器 = StorageManager()
        
        # 创建几个适配器
        管理器.获取适配器("local", {})
        
        # 关闭所有适配器
        管理器.关闭所有适配器()
        
        # 验证当前适配器为 None
        assert 管理器.获取当前适配器() is None
    
    def test_全局管理器(self):
        """测试全局管理器实例"""
        管理器 = get_storage_manager()
        assert 管理器 is not None
        assert isinstance(管理器, StorageManager)
        
        # 多次获取应该返回同一个实例
        管理器2 = get_storage_manager()
        assert 管理器 is 管理器2


class TestStorageIntegration:
    """存储集成测试"""
    
    def test_本地存储完整流程(self, tmp_path):
        """测试本地存储的完整操作流程"""
        # 创建管理器并切换到本地存储
        管理器 = StorageManager()
        assert 管理器.切换适配器("local", {})
        
        适配器 = 管理器.获取当前适配器()
        assert 适配器 is not None
        
        # 创建测试文件
        测试文件 = tmp_path / "test.txt"
        测试文件.write_text("hello")
        
        # 1. 列出文件
        文件列表 = 适配器.列出文件(str(tmp_path))
        assert len(文件列表) >= 1
        
        # 2. 获取文件信息
        文件信息 = 适配器.获取文件信息(str(测试文件))
        assert 文件信息 is not None
        assert 文件信息.名称 == "test.txt"
        
        # 3. 读取文件
        读取路径 = 适配器.读取文件(str(测试文件))
        assert 读取路径 == 测试文件
        
        # 4. 重命名文件
        新文件 = tmp_path / "renamed.txt"
        assert 适配器.重命名文件(str(测试文件), str(新文件))
        assert 新文件.exists()
        
        # 5. 删除文件
        assert 适配器.删除文件(str(新文件))
        assert not 新文件.exists()
        
        # 6. 获取存储空间信息
        空间信息 = 适配器.获取存储空间信息()
        assert 空间信息["总空间"] > 0
