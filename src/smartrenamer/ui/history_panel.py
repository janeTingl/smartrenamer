"""
历史记录面板

显示重命名操作历史并支持撤销
"""
import logging
from typing import Optional, List
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from smartrenamer.core import Renamer, RenameHistory


logger = logging.getLogger(__name__)


class HistoryPanel(QWidget):
    """历史记录面板"""
    
    undo_requested = Signal(object)  # RenameHistory
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.renamer = Renamer(预览模式=False)
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._on_refresh)
        toolbar.addWidget(self.refresh_btn)
        
        toolbar.addStretch()
        
        self.undo_btn = QPushButton("撤销选中操作")
        self.undo_btn.clicked.connect(self._on_undo)
        self.undo_btn.setEnabled(False)
        toolbar.addWidget(self.undo_btn)
        
        self.clear_btn = QPushButton("清空历史")
        self.clear_btn.clicked.connect(self._on_clear_history)
        toolbar.addWidget(self.clear_btn)
        
        layout.addLayout(toolbar)
        
        # 历史记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "时间", "原文件名", "新文件名", "路径", "规则", "状态"
        ])
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # 调整列宽
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.history_table)
        
        # 加载历史记录
        self._load_history()
        
    def _load_history(self):
        """加载历史记录"""
        self.history_table.setRowCount(0)
        
        # 获取历史记录
        history_list = self.renamer.get_history()
        
        if not history_list:
            logger.info("没有历史记录")
            return
            
        # 按时间倒序排序
        history_list.sort(key=lambda h: h.timestamp, reverse=True)
        
        # 添加到表格
        for history in history_list[:100]:  # 最多显示100条
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # 时间
            time_str = history.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            self.history_table.setItem(row, 0, QTableWidgetItem(time_str))
            
            # 原文件名
            old_name_item = QTableWidgetItem(history.old_name)
            old_name_item.setData(Qt.UserRole, history)
            self.history_table.setItem(row, 1, old_name_item)
            
            # 新文件名
            self.history_table.setItem(row, 2, QTableWidgetItem(history.new_name))
            
            # 路径
            self.history_table.setItem(row, 3, QTableWidgetItem(str(history.old_path.parent)))
            
            # 规则
            self.history_table.setItem(row, 4, QTableWidgetItem(history.rule_name))
            
            # 状态
            status = "已撤销" if history.reverted else "已应用"
            self.history_table.setItem(row, 5, QTableWidgetItem(status))
            
        logger.info(f"加载了 {len(history_list)} 条历史记录")
        
    @Slot()
    def _on_refresh(self):
        """刷新按钮点击"""
        self._load_history()
        
    @Slot()
    def _on_selection_changed(self):
        """选择改变"""
        selected_items = self.history_table.selectedItems()
        if selected_items:
            history = selected_items[0].data(Qt.UserRole)
            # 只有未撤销的记录可以撤销
            self.undo_btn.setEnabled(history and not history.reverted)
        else:
            self.undo_btn.setEnabled(False)
            
    @Slot()
    def _on_undo(self):
        """撤销按钮点击"""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
            
        history = selected_items[0].data(Qt.UserRole)
        if not history:
            return
            
        # 确认撤销
        reply = QMessageBox.question(
            self,
            "确认撤销",
            f"确定要撤销重命名操作吗？\n\n"
            f"将会把文件:\n{history.new_name}\n\n"
            f"恢复为:\n{history.old_name}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 执行撤销
                success = self.renamer.undo_rename(history)
                
                if success:
                    logger.info(f"成功撤销: {history.new_name} -> {history.old_name}")
                    QMessageBox.information(self, "成功", "撤销成功")
                    self._load_history()
                    self.undo_requested.emit(history)
                else:
                    QMessageBox.warning(self, "失败", "撤销失败，文件可能已被移动或删除")
                    
            except Exception as e:
                logger.error(f"撤销失败: {e}")
                QMessageBox.critical(self, "错误", f"撤销失败:\n{str(e)}")
                
    @Slot()
    def _on_clear_history(self):
        """清空历史按钮点击"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空所有历史记录吗？\n注意：清空后将无法撤销之前的重命名操作。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.renamer.clear_history()
            self._load_history()
            logger.info("历史记录已清空")
            QMessageBox.information(self, "成功", "历史记录已清空")
            
    def refresh(self):
        """刷新历史记录"""
        self._load_history()
