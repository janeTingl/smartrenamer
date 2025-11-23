"""
批量重命名对话框

显示重命名进度和处理冲突
"""
import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QListWidget, QListWidgetItem, QWidget
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from smartrenamer.core import MediaFile, RenameRule, Renamer
from smartrenamer.ui.widgets import ProgressWidget


logger = logging.getLogger(__name__)


class RenameWorker(QThread):
    """重命名工作线程"""
    
    progress = Signal(int, int, str)  # current, total, message
    file_renamed = Signal(object, bool, str)  # media_file, success, message
    finished = Signal(dict)  # result summary
    
    def __init__(self, files: List[MediaFile], rule: RenameRule, preview_mode: bool = False):
        super().__init__()
        self.files = files
        self.rule = rule
        self.renamer = Renamer(预览模式=preview_mode, 创建备份=True)
        
    def run(self):
        """运行重命名"""
        try:
            total = len(self.files)
            success_count = 0
            failed_count = 0
            skipped_count = 0
            
            for i, file in enumerate(self.files):
                self.progress.emit(i + 1, total, f"重命名 {file.original_name}...")
                
                # 执行重命名
                success, new_name, error = self.renamer.rename_file(file, self.rule)
                
                if success:
                    success_count += 1
                    self.file_renamed.emit(file, True, f"成功: {new_name}")
                elif error:
                    failed_count += 1
                    self.file_renamed.emit(file, False, f"失败: {error}")
                else:
                    skipped_count += 1
                    self.file_renamed.emit(file, False, "已跳过")
                    
            # 发送汇总
            summary = {
                "total": total,
                "success": success_count,
                "failed": failed_count,
                "skipped": skipped_count
            }
            self.finished.emit(summary)
            
        except Exception as e:
            logger.error(f"批量重命名失败: {e}")


class RenameDialog(QDialog):
    """批量重命名对话框"""
    
    rename_completed = Signal(dict)  # 重命名完成信号
    
    def __init__(
        self,
        files: List[MediaFile],
        rule: RenameRule,
        preview_mode: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.files = files
        self.rule = rule
        self.preview_mode = preview_mode
        self.worker: Optional[RenameWorker] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("批量重命名" if not self.preview_mode else "预览重命名")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel(f"正在处理 {len(self.files)} 个文件...")
        title.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        layout.addWidget(title)
        
        # 进度显示
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # 日志列表
        layout.addWidget(QLabel("处理日志:"))
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def start(self):
        """开始重命名"""
        if self.worker and self.worker.isRunning():
            return
            
        # 创建工作线程
        self.worker = RenameWorker(self.files, self.rule, self.preview_mode)
        self.worker.progress.connect(self._on_progress)
        self.worker.file_renamed.connect(self._on_file_renamed)
        self.worker.finished.connect(self._on_finished)
        
        self.worker.start()
        
    @Slot(int, int, str)
    def _on_progress(self, current: int, total: int, message: str):
        """进度更新"""
        self.progress_widget.set_progress(current, total, message)
        
    @Slot(object, bool, str)
    def _on_file_renamed(self, media_file: MediaFile, success: bool, message: str):
        """文件重命名完成"""
        icon = "✓" if success else "✗"
        item = QListWidgetItem(f"{icon} {media_file.original_name}: {message}")
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()
        
    @Slot(dict)
    def _on_finished(self, summary: dict):
        """重命名完成"""
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        
        # 显示摘要
        total = summary["total"]
        success = summary["success"]
        failed = summary["failed"]
        skipped = summary["skipped"]
        
        summary_text = f"完成! 总计: {total}, 成功: {success}, 失败: {failed}, 跳过: {skipped}"
        self.progress_widget.set_message(summary_text)
        
        logger.info(summary_text)
        
        # 发送完成信号
        self.rename_completed.emit(summary)
        
        # 显示消息框
        if failed > 0:
            QMessageBox.warning(
                self,
                "完成",
                f"重命名完成，但有 {failed} 个文件失败。\n请查看日志了解详情。"
            )
        else:
            QMessageBox.information(
                self,
                "完成",
                f"重命名成功完成! 共处理 {success} 个文件。"
            )
            
    @Slot()
    def _on_cancel(self):
        """取消按钮点击"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认",
                "确定要取消重命名操作吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait()
                self.reject()
        else:
            self.reject()


class ConflictDialog(QDialog):
    """冲突处理对话框"""
    
    def __init__(self, file_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_path = file_path
        self.choice = None
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("文件冲突")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 消息
        message = QLabel(f"文件已存在:\n{self.file_path}\n\n请选择处理方式:")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # 按钮
        skip_btn = QPushButton("跳过此文件")
        skip_btn.clicked.connect(lambda: self._set_choice("skip"))
        layout.addWidget(skip_btn)
        
        overwrite_btn = QPushButton("覆盖")
        overwrite_btn.clicked.connect(lambda: self._set_choice("overwrite"))
        layout.addWidget(overwrite_btn)
        
        rename_btn = QPushButton("重命名（添加序号）")
        rename_btn.clicked.connect(lambda: self._set_choice("rename"))
        layout.addWidget(rename_btn)
        
        cancel_btn = QPushButton("取消全部操作")
        cancel_btn.clicked.connect(lambda: self._set_choice("cancel"))
        layout.addWidget(cancel_btn)
        
    def _set_choice(self, choice: str):
        """设置选择"""
        self.choice = choice
        self.accept()
        
    def get_choice(self) -> Optional[str]:
        """获取选择"""
        return self.choice
