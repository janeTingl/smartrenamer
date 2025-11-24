"""
日志面板

显示应用程序操作日志
"""
import logging
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Slot
from smartrenamer.ui.widgets import LogWidget


class LogPanel(QWidget):
    """日志面板"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_logging()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.clear_btn = QPushButton("清空日志")
        self.clear_btn.clicked.connect(self._on_clear)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 日志显示区域
        self.log_widget = LogWidget()
        layout.addWidget(self.log_widget)
        
    def _setup_logging(self):
        """设置日志处理器"""
        # 创建自定义日志处理器
        handler = QtLogHandler(self)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # 添加到根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
        
    @Slot()
    def _on_clear(self):
        """清空日志"""
        self.log_widget.clear()
        
    @Slot(str, str)
    def append_log(self, level: str, message: str):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_widget.append_log(level, f"{timestamp} - {message}")
    
    def clear(self):
        """清空日志（公共方法）"""
        self.log_widget.clear()


class QtLogHandler(logging.Handler):
    """Qt 日志处理器"""
    
    def __init__(self, log_panel: LogPanel):
        super().__init__()
        self.log_panel = log_panel
        
    def emit(self, record: logging.LogRecord):
        """发出日志记录"""
        msg = self.format(record)
        level = record.levelname
        
        # 在 GUI 线程中显示日志
        self.log_panel.append_log(level, msg)
