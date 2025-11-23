"""
自定义 UI 控件和工具类
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QLabel, QProgressBar, QTextEdit, QTableWidget, 
    QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLineEdit, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from pathlib import Path
import logging


class LogWidget(QTextEdit):
    """日志显示控件"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(150)
        font = QFont("Monospace", 9)
        self.setFont(font)
        
    def append_log(self, level: str, message: str):
        """添加日志消息"""
        color_map = {
            "DEBUG": "gray",
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red",
            "SUCCESS": "green",
        }
        color = color_map.get(level.upper(), "black")
        self.append(f'<span style="color: {color};">[{level}] {message}</span>')


class MediaFileTableWidget(QTableWidget):
    """媒体文件列表控件"""
    
    file_selected = Signal(object)  # 当文件被选中时发出信号
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        # 设置列
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "文件名", "类型", "标题", "年份", "大小", "状态", "路径"
        ])
        
        # 设置表格属性
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        
        # 调整列宽
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        
        # 连接信号
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _on_selection_changed(self):
        """选择改变时"""
        selected_items = self.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            file_data = self.item(row, 0).data(Qt.UserRole)
            if file_data:
                self.file_selected.emit(file_data)
    
    def add_media_file(self, media_file):
        """添加媒体文件到列表"""
        row = self.rowCount()
        self.insertRow(row)
        
        # 文件名
        name_item = QTableWidgetItem(media_file.original_name)
        name_item.setData(Qt.UserRole, media_file)
        self.setItem(row, 0, name_item)
        
        # 类型
        type_text = "电影" if media_file.is_movie else ("电视剧" if media_file.is_tv_show else "未知")
        self.setItem(row, 1, QTableWidgetItem(type_text))
        
        # 标题
        self.setItem(row, 2, QTableWidgetItem(media_file.title or "-"))
        
        # 年份
        self.setItem(row, 3, QTableWidgetItem(str(media_file.year) if media_file.year else "-"))
        
        # 大小
        size_text = self._format_size(media_file.size)
        self.setItem(row, 4, QTableWidgetItem(size_text))
        
        # 状态
        status_map = {
            "pending": "待处理",
            "matched": "已匹配",
            "success": "成功",
            "failed": "失败"
        }
        status_text = status_map.get(media_file.rename_status, media_file.rename_status)
        self.setItem(row, 5, QTableWidgetItem(status_text))
        
        # 路径
        self.setItem(row, 6, QTableWidgetItem(str(media_file.path.parent)))
        
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "-"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{size:.2f} {units[unit_index]}"
    
    def get_selected_files(self) -> List:
        """获取选中的文件"""
        selected_files = []
        selected_rows = set()
        
        for item in self.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.add(row)
                file_data = self.item(row, 0).data(Qt.UserRole)
                if file_data:
                    selected_files.append(file_data)
                    
        return selected_files
    
    def clear_files(self):
        """清空文件列表"""
        self.setRowCount(0)
    
    def update_file_status(self, media_file, status: str):
        """更新文件状态"""
        for row in range(self.rowCount()):
            file_data = self.item(row, 0).data(Qt.UserRole)
            if file_data and file_data.path == media_file.path:
                status_map = {
                    "pending": "待处理",
                    "matched": "已匹配",
                    "success": "成功",
                    "failed": "失败"
                }
                status_text = status_map.get(status, status)
                self.setItem(row, 5, QTableWidgetItem(status_text))
                break


class ImageLabel(QLabel):
    """图片显示标签（用于海报等）"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(200, 300)
        self.setMaximumSize(300, 450)
        self.setScaledContents(False)
        self.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #ccc; }")
        self._default_text = "暂无海报"
        self.setText(self._default_text)
        
    def set_image(self, image_path: Optional[Path] = None, image_data: Optional[bytes] = None):
        """设置图片"""
        if image_path and image_path.exists():
            pixmap = QPixmap(str(image_path))
        elif image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
        else:
            self.setText(self._default_text)
            return
            
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setText(self._default_text)
    
    def clear_image(self):
        """清空图片"""
        self.clear()
        self.setText(self._default_text)


class PathSelector(QWidget):
    """路径选择控件"""
    
    path_changed = Signal(str)
    
    def __init__(self, label: str = "选择路径:", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui(label)
        
    def _setup_ui(self, label: str):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 标签
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # 路径输入框
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("请选择或输入路径...")
        layout.addWidget(self.path_edit, 1)
        
        # 浏览按钮
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self._on_browse)
        layout.addWidget(self.browse_btn)
        
    def _on_browse(self):
        """浏览按钮点击"""
        path = QFileDialog.getExistingDirectory(
            self,
            "选择目录",
            self.path_edit.text() or str(Path.home())
        )
        if path:
            self.path_edit.setText(path)
            self.path_changed.emit(path)
    
    def get_path(self) -> Optional[Path]:
        """获取路径"""
        path_text = self.path_edit.text().strip()
        if path_text:
            return Path(path_text)
        return None
    
    def set_path(self, path: Path):
        """设置路径"""
        self.path_edit.setText(str(path))


class ProgressWidget(QWidget):
    """进度显示控件"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 进度标签
        self.label = QLabel("准备中...")
        layout.addWidget(self.label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
    def set_progress(self, current: int, total: int, message: str = ""):
        """设置进度"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        if message:
            self.label.setText(message)
        else:
            self.label.setText(f"处理中: {current}/{total}")
    
    def set_message(self, message: str):
        """设置消息"""
        self.label.setText(message)
    
    def reset(self):
        """重置"""
        self.progress_bar.setValue(0)
        self.label.setText("准备中...")
