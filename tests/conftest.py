"""
pytest 配置文件

全局 fixture 和配置
"""
import os
import sys

# 必须在导入 Qt 之前设置
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import pytest


@pytest.fixture(scope="session")
def qapp():
    """创建 QApplication 实例（session 级别）"""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # 不关闭 app，因为可能有其他测试需要使用
