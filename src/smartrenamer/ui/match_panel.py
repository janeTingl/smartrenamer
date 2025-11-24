"""
匹配识别面板

显示 TMDB 匹配结果并允许用户选择
"""
import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QTextEdit, QSplitter, QGroupBox,
    QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont
from smartrenamer.core import MediaFile, Matcher, MatchResult, get_config
from smartrenamer.api import get_tmdb_client, get_cache_stats
from smartrenamer.ui.widgets import ImageLabel


logger = logging.getLogger(__name__)


class MatchWorker(QThread):
    """匹配工作线程"""
    
    progress = Signal(int, int, str)  # current, total, message
    match_found = Signal(object, list)  # media_file, match_results
    error = Signal(str)
    finished = Signal()
    
    def __init__(self, files: List[MediaFile], matcher: Matcher):
        super().__init__()
        self.files = files
        self.matcher = matcher
        
    def run(self):
        """运行匹配"""
        try:
            total = len(self.files)
            for i, file in enumerate(self.files):
                self.progress.emit(i + 1, total, f"匹配 {file.original_name}...")
                
                # 执行匹配
                results = self.matcher.match(file)
                self.match_found.emit(file, results)
                
            self.finished.emit()
        except Exception as e:
            logger.error(f"匹配失败: {e}")
            self.error.emit(str(e))


class MatchPanel(QWidget):
    """匹配识别面板"""
    
    match_confirmed = Signal(object, object)  # media_file, match_result
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # 初始化 matcher（使用工厂模式）
        config = get_config()
        if not config.tmdb_api_key:
            logger.warning("TMDB API Key 未配置")
            self.matcher = None
        else:
            # 使用工厂模式获取共享的 TMDB 客户端
            self.matcher = Matcher()  # 不传入客户端，让它自动使用工厂
            logger.info("MatchPanel 使用共享 TMDB 客户端")
            
        self.current_file: Optional[MediaFile] = None
        self.current_matches: List[MatchResult] = []
        self.match_worker: Optional[MatchWorker] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 顶部工具栏
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)
        
        # 主内容区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：匹配结果列表
        left_panel = self._create_match_list_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：详情面板
        right_panel = self._create_detail_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # 底部按钮
        button_bar = self._create_button_bar()
        layout.addLayout(button_bar)
        
    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏"""
        toolbar = QHBoxLayout()
        
        self.file_label = QLabel("待匹配文件: -")
        self.file_label.setFont(QFont("Arial", 10, QFont.Bold))
        toolbar.addWidget(self.file_label)
        
        toolbar.addStretch()
        
        # 缓存统计标签
        self.cache_status_label = QLabel("缓存: -")
        self.cache_status_label.setStyleSheet("QLabel { color: gray; font-size: 9px; }")
        toolbar.addWidget(self.cache_status_label)
        
        self.auto_match_btn = QPushButton("自动匹配")
        self.auto_match_btn.clicked.connect(self._on_auto_match)
        self.auto_match_btn.setEnabled(False)
        toolbar.addWidget(self.auto_match_btn)
        
        return toolbar
        
    def _create_match_list_panel(self) -> QGroupBox:
        """创建匹配结果列表面板"""
        group = QGroupBox("匹配结果")
        layout = QVBoxLayout(group)
        
        self.match_list = QListWidget()
        self.match_list.itemClicked.connect(self._on_match_selected)
        layout.addWidget(self.match_list)
        
        return group
        
    def _create_detail_panel(self) -> QGroupBox:
        """创建详情面板"""
        group = QGroupBox("影视详情")
        layout = QHBoxLayout(group)
        
        # 左侧：海报
        self.poster_label = ImageLabel()
        layout.addWidget(self.poster_label)
        
        # 右侧：详细信息
        info_layout = QVBoxLayout()
        
        self.title_label = QLabel("标题: -")
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)
        
        self.year_label = QLabel("年份: -")
        info_layout.addWidget(self.year_label)
        
        self.type_label = QLabel("类型: -")
        info_layout.addWidget(self.type_label)
        
        self.score_label = QLabel("匹配度: -")
        info_layout.addWidget(self.score_label)
        
        self.reason_label = QLabel("匹配原因: -")
        self.reason_label.setWordWrap(True)
        info_layout.addWidget(self.reason_label)
        
        info_layout.addWidget(QLabel("简介:"))
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        self.overview_text.setMaximumHeight(150)
        info_layout.addWidget(self.overview_text)
        
        info_layout.addStretch()
        
        layout.addLayout(info_layout, 1)
        
        return group
        
    def _create_button_bar(self) -> QHBoxLayout:
        """创建按钮栏"""
        button_bar = QHBoxLayout()
        
        button_bar.addStretch()
        
        self.confirm_btn = QPushButton("确认选择")
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.confirm_btn.setEnabled(False)
        button_bar.addWidget(self.confirm_btn)
        
        self.skip_btn = QPushButton("跳过")
        self.skip_btn.clicked.connect(self._on_skip)
        self.skip_btn.setEnabled(False)
        button_bar.addWidget(self.skip_btn)
        
        return button_bar
        
    def set_files(self, files: List[MediaFile]):
        """设置要匹配的文件"""
        if not self.matcher:
            QMessageBox.warning(
                self,
                "警告",
                "TMDB API Key 未配置，无法进行匹配。\n请先在设置中配置 API Key。"
            )
            return
            
        if not files:
            return
            
        # 开始批量匹配
        self._start_batch_match(files)
        
    def _start_batch_match(self, files: List[MediaFile]):
        """开始批量匹配"""
        if self.match_worker and self.match_worker.isRunning():
            QMessageBox.warning(self, "警告", "匹配正在进行中，请等待完成")
            return
            
        # 创建进度对话框
        progress = QProgressDialog("正在匹配文件...", "取消", 0, len(files), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        
        # 创建工作线程
        self.match_worker = MatchWorker(files, self.matcher)
        self.match_worker.progress.connect(
            lambda cur, tot, msg: progress.setValue(cur) or progress.setLabelText(msg)
        )
        self.match_worker.match_found.connect(self._on_match_result)
        self.match_worker.error.connect(
            lambda err: QMessageBox.critical(self, "错误", f"匹配失败:\n{err}")
        )
        self.match_worker.finished.connect(progress.close)
        self.match_worker.finished.connect(
            lambda: logger.info("批量匹配完成")
        )
        
        # 连接取消按钮
        progress.canceled.connect(self.match_worker.terminate)
        
        self.match_worker.start()
        
    @Slot(object, list)
    def _on_match_result(self, media_file: MediaFile, results: List[MatchResult]):
        """匹配结果"""
        logger.info(f"文件 {media_file.original_name} 找到 {len(results)} 个匹配")
        
        # 更新缓存统计
        self._update_cache_status()
        
        # 如果有高置信度的自动确认匹配，直接应用
        if results and results[0].auto_confirm:
            logger.info(f"自动确认匹配: {results[0].title}")
            self.match_confirmed.emit(media_file, results[0])
            return
            
        # 否则显示给用户选择
        self._show_matches(media_file, results)
        
    def _show_matches(self, media_file: MediaFile, results: List[MatchResult]):
        """显示匹配结果"""
        self.current_file = media_file
        self.current_matches = results
        
        self.file_label.setText(f"待匹配文件: {media_file.original_name}")
        
        # 清空列表
        self.match_list.clear()
        
        # 添加匹配结果
        for result in results:
            item = QListWidgetItem(f"{result.title} ({result.year or '未知'})")
            item.setData(Qt.UserRole, result)
            self.match_list.addItem(item)
            
        # 如果有结果，选中第一个
        if results:
            self.match_list.setCurrentRow(0)
            self._display_match_detail(results[0])
            
        # 启用按钮
        self.auto_match_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
        
    @Slot(QListWidgetItem)
    def _on_match_selected(self, item: QListWidgetItem):
        """匹配项选中"""
        match_result = item.data(Qt.UserRole)
        if match_result:
            self._display_match_detail(match_result)
            self.confirm_btn.setEnabled(True)
            
    def _display_match_detail(self, result: MatchResult):
        """显示匹配详情"""
        self.title_label.setText(f"标题: {result.title}")
        self.year_label.setText(f"年份: {result.year or '未知'}")
        self.type_label.setText(f"类型: {'电影' if result.is_movie else '电视剧'}")
        self.score_label.setText(f"匹配度: {result.confidence:.2%}")
        self.reason_label.setText(f"匹配原因: {result.reason}")
        self.overview_text.setPlainText(result.metadata.get('overview', '暂无简介'))
        
        # TODO: 加载海报图片
        self.poster_label.clear_image()
        
    @Slot()
    def _on_auto_match(self):
        """自动匹配按钮点击"""
        if not self.current_matches:
            QMessageBox.information(self, "提示", "没有找到匹配结果")
            return
            
        # 选择第一个匹配
        self._confirm_match(self.current_matches[0])
        
    @Slot()
    def _on_confirm(self):
        """确认按钮点击"""
        current_item = self.match_list.currentItem()
        if not current_item:
            return
            
        match_result = current_item.data(Qt.UserRole)
        if match_result:
            self._confirm_match(match_result)
            
    def _confirm_match(self, result: MatchResult):
        """确认匹配"""
        if self.current_file:
            logger.info(f"确认匹配: {self.current_file.original_name} -> {result.title}")
            self.match_confirmed.emit(self.current_file, result)
            
            # 清空当前显示
            self._clear_display()
            
    @Slot()
    def _on_skip(self):
        """跳过按钮点击"""
        logger.info(f"跳过文件: {self.current_file.original_name if self.current_file else '未知'}")
        self._clear_display()
        
    def _clear_display(self):
        """清空显示"""
        self.current_file = None
        self.current_matches = []
        
        self.file_label.setText("待匹配文件: -")
        self.match_list.clear()
        
        self.title_label.setText("标题: -")
        self.year_label.setText("年份: -")
        self.type_label.setText("类型: -")
        self.score_label.setText("匹配度: -")
        self.reason_label.setText("匹配原因: -")
        self.overview_text.clear()
        self.poster_label.clear_image()
        
        self.confirm_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        self.auto_match_btn.setEnabled(False)
    
    def _update_cache_status(self):
        """更新缓存统计状态"""
        try:
            stats = get_cache_stats()
            
            if not stats.get("enabled", False):
                self.cache_status_label.setText("缓存: 禁用")
                return
            
            hit_rate = stats.get("hit_rate", 0.0) * 100
            total_hits = stats.get("total_hits", 0)
            total_requests = stats.get("total_requests", 0)
            
            if total_requests == 0:
                self.cache_status_label.setText("缓存: 无请求")
            else:
                status_text = f"缓存: {hit_rate:.0f}% 命中 ({total_hits}/{total_requests})"
                self.cache_status_label.setText(status_text)
                
                # 根据命中率设置颜色
                if hit_rate >= 80:
                    color = "green"
                elif hit_rate >= 50:
                    color = "orange"
                else:
                    color = "red"
                
                self.cache_status_label.setStyleSheet(
                    f"QLabel {{ color: {color}; font-size: 9px; font-weight: bold; }}"
                )
                
        except Exception as e:
            logger.warning(f"更新缓存状态失败: {e}")
            self.cache_status_label.setText("缓存: 未知")
