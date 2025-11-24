"""
批量重命名对话框

显示重命名进度和处理冲突
"""
import logging
import time
import queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox, QListWidget, QListWidgetItem, QWidget
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QMovie
from smartrenamer.core import MediaFile, RenameRule, Renamer, get_config
from smartrenamer.ui.widgets import ProgressWidget


logger = logging.getLogger(__name__)


class RenameWorker(QThread):
    """并行重命名工作线程"""
    
    progress = Signal(int, int, str, float)  # current, total, message, throughput
    file_renamed = Signal(object, bool, str)  # media_file, success, message
    finished = Signal(dict)  # result summary
    
    def __init__(self, files: List[MediaFile], rule: RenameRule, preview_mode: bool = False):
        super().__init__()
        self.files = files
        self.rule = rule
        self.preview_mode = preview_mode
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # 初始为运行状态
        
        # 从配置获取并行度
        config = get_config()
        self.worker_count = config.get("rename_worker_count", 4)
        self.enable_batch = config.get("rename_io_batch", True)
        
    def cancel(self):
        """取消任务（软取消：等待正在运行的任务完成）"""
        self._cancel_event.set()
        
    def pause(self):
        """暂停任务"""
        self._pause_event.clear()
        
    def resume(self):
        """恢复任务"""
        self._pause_event.set()
        
    def _rename_single_file(self, file: MediaFile) -> Tuple[MediaFile, bool, str]:
        """
        重命名单个文件（在线程池中执行）
        
        Args:
            file: 媒体文件
            
        Returns:
            Tuple[MediaFile, bool, str]: (文件, 是否成功, 消息)
        """
        # 每个 worker 线程持有独立的 Renamer 实例，避免 Jinja 环境共享
        renamer = Renamer(预览模式=self.preview_mode, 创建备份=True)
        
        try:
            # 检查是否暂停
            self._pause_event.wait()
            
            # 检查是否取消
            if self._cancel_event.is_set():
                return file, False, "已取消"
            
            # 执行重命名
            success, error = renamer.重命名文件(file, self.rule)
            
            if success:
                new_name = file.new_name or file.path.name
                return file, True, f"成功: {new_name}"
            else:
                return file, False, f"失败: {error}"
                
        except Exception as e:
            logger.error(f"重命名文件 {file.original_name} 时发生异常: {e}")
            return file, False, f"异常: {e}"
        
    def run(self):
        """运行并行重命名"""
        try:
            total = len(self.files)
            success_count = 0
            failed_count = 0
            skipped_count = 0
            
            start_time = time.time()
            completed = 0
            
            # 使用线程池执行并行重命名
            with ThreadPoolExecutor(max_workers=self.worker_count) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._rename_single_file, file): file
                    for file in self.files
                }
                
                # 处理完成的任务
                for future in as_completed(future_to_file):
                    if self._cancel_event.is_set():
                        # 取消所有未完成的任务
                        for f in future_to_file:
                            f.cancel()
                        break
                    
                    file, success, message = future.result()
                    completed += 1
                    
                    # 计算吞吐量（文件/秒）
                    elapsed = time.time() - start_time
                    throughput = completed / elapsed if elapsed > 0 else 0
                    
                    # 更新进度
                    self.progress.emit(completed, total, f"处理 {file.original_name}...", throughput)
                    
                    # 发送单个文件结果
                    if success:
                        success_count += 1
                        self.file_renamed.emit(file, True, message)
                    elif "已取消" in message or "已跳过" in message:
                        skipped_count += 1
                        self.file_renamed.emit(file, False, message)
                    else:
                        failed_count += 1
                        self.file_renamed.emit(file, False, message)
            
            # 发送汇总
            summary = {
                "total": total,
                "success": success_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "duration": time.time() - start_time,
                "cancelled": self._cancel_event.is_set()
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
        self.setMinimumSize(700, 600)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel(f"正在处理 {len(self.files)} 个文件...")
        title.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        layout.addWidget(title)
        
        # 进度显示
        self.progress_widget = ProgressWidget()
        layout.addWidget(self.progress_widget)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.throughput_label = QLabel("吞吐量: -- 文件/秒")
        self.throughput_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        stats_layout.addWidget(self.throughput_label)
        
        self.eta_label = QLabel("预计剩余: --")
        self.eta_label.setStyleSheet("QLabel { color: #666; font-size: 11px; }")
        stats_layout.addWidget(self.eta_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # 日志列表
        layout.addWidget(QLabel("处理日志:"))
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setCheckable(True)
        self.pause_btn.clicked.connect(self._on_pause)
        button_layout.addWidget(self.pause_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # 用于跟踪是否暂停
        self.is_paused = False
        
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
        
    @Slot(int, int, str, float)
    def _on_progress(self, current: int, total: int, message: str, throughput: float):
        """进度更新"""
        self.progress_widget.set_progress(current, total, message)
        
        # 更新吞吐量
        self.throughput_label.setText(f"吞吐量: {throughput:.2f} 文件/秒")
        
        # 计算并显示预计剩余时间
        if throughput > 0 and current < total:
            remaining_files = total - current
            eta_seconds = remaining_files / throughput
            if eta_seconds < 60:
                eta_str = f"{int(eta_seconds)} 秒"
            elif eta_seconds < 3600:
                eta_str = f"{int(eta_seconds / 60)} 分钟"
            else:
                eta_str = f"{eta_seconds / 3600:.1f} 小时"
            self.eta_label.setText(f"预计剩余: {eta_str}")
        else:
            self.eta_label.setText("预计剩余: --")
        
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
        self.pause_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        
        # 显示摘要
        total = summary["total"]
        success = summary["success"]
        failed = summary["failed"]
        skipped = summary["skipped"]
        duration = summary.get("duration", 0)
        cancelled = summary.get("cancelled", False)
        
        if cancelled:
            summary_text = f"已取消! 总计: {total}, 成功: {success}, 失败: {failed}, 跳过: {skipped}"
        else:
            summary_text = f"完成! 总计: {total}, 成功: {success}, 失败: {failed}, 跳过: {skipped}, 耗时: {duration:.1f}秒"
        
        self.progress_widget.set_message(summary_text)
        
        logger.info(summary_text)
        
        # 发送完成信号
        self.rename_completed.emit(summary)
        
        # 显示消息框
        if cancelled:
            QMessageBox.information(
                self,
                "已取消",
                f"操作已取消。已处理 {success} 个文件。"
            )
        elif failed > 0:
            QMessageBox.warning(
                self,
                "完成",
                f"重命名完成，但有 {failed} 个文件失败。\n请查看日志了解详情。"
            )
        else:
            QMessageBox.information(
                self,
                "完成",
                f"重命名成功完成! 共处理 {success} 个文件，耗时 {duration:.1f} 秒。"
            )
    
    @Slot()
    def _on_pause(self):
        """暂停/继续按钮点击"""
        if not self.worker or not self.worker.isRunning():
            return
            
        if self.is_paused:
            # 恢复
            self.worker.resume()
            self.pause_btn.setText("暂停")
            self.is_paused = False
            logger.info("重命名任务已恢复")
        else:
            # 暂停
            self.worker.pause()
            self.pause_btn.setText("继续")
            self.is_paused = True
            logger.info("重命名任务已暂停")
            
    @Slot()
    def _on_cancel(self):
        """取消按钮点击"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认",
                "确定要取消重命名操作吗？\n正在运行的任务将完成后再退出。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 软取消：设置取消标志，等待任务完成
                self.worker.cancel()
                self.cancel_btn.setEnabled(False)
                self.pause_btn.setEnabled(False)
                self.cancel_btn.setText("正在取消...")
                logger.info("正在取消重命名任务，等待正在运行的任务完成...")
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
