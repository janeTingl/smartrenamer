"""
主窗口

SmartRenamer 的主应用程序窗口
"""
import logging
import sys
from typing import Optional, List
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
    QMessageBox, QFileDialog, QSplitter
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QKeySequence, QAction
from smartrenamer import __version__
from smartrenamer.core import (
    MediaFile, RenameRule, MatchResult, get_config, MediaType
)
from smartrenamer.ui.media_library_panel import MediaLibraryPanel
from smartrenamer.ui.match_panel import MatchPanel
from smartrenamer.ui.rule_editor_panel import RuleEditorPanel
from smartrenamer.ui.history_panel import HistoryPanel
from smartrenamer.ui.log_panel import LogPanel
from smartrenamer.ui.settings_dialog import SettingsDialog
from smartrenamer.ui.rename_dialog import RenameDialog


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        
        # 匹配后的文件缓存
        self.matched_files: List[MediaFile] = []
        
        self._setup_ui()
        self._create_menus()
        self._create_toolbar()
        self._create_statusbar()
        self._connect_signals()
        
        # 应用主题
        self._apply_theme()
        
        # 检查配置
        self._check_config()
        
        logger.info(f"SmartRenamer v{__version__} 启动")
        
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(f"SmartRenamer v{__version__} - 智能媒体文件重命名工具")
        self.setMinimumSize(1200, 800)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 主分割器（上下）
        main_splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：选项卡
        self.tab_widget = QTabWidget()
        
        # 媒体库浏览选项卡
        self.library_panel = MediaLibraryPanel()
        self.tab_widget.addTab(self.library_panel, "📁 媒体库")
        
        # 匹配识别选项卡
        self.match_panel = MatchPanel()
        self.tab_widget.addTab(self.match_panel, "🔍 匹配识别")
        
        # 规则配置选项卡
        self.rule_panel = RuleEditorPanel()
        self.tab_widget.addTab(self.rule_panel, "⚙️ 重命名规则")
        
        # 历史记录选项卡
        self.history_panel = HistoryPanel()
        self.tab_widget.addTab(self.history_panel, "📜 历史记录")
        
        main_splitter.addWidget(self.tab_widget)
        
        # 下半部分：日志面板
        self.log_panel = LogPanel()
        main_splitter.addWidget(self.log_panel)
        
        main_splitter.setSizes([600, 200])
        
        layout.addWidget(main_splitter)
        
    def _create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        open_action = QAction("打开目录(&O)...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._on_open_directory)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        settings_action = QAction("设置(&S)...", self)
        settings_action.setShortcut(QKeySequence.Preferences)
        settings_action.triggered.connect(self._on_settings)
        edit_menu.addAction(settings_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        match_action = QAction("匹配选中文件(&M)", self)
        match_action.setShortcut(QKeySequence("Ctrl+M"))
        match_action.triggered.connect(self._on_match_files)
        tools_menu.addAction(match_action)
        
        rename_action = QAction("批量重命名(&R)...", self)
        rename_action.setShortcut(QKeySequence("Ctrl+R"))
        rename_action.triggered.connect(self._on_batch_rename)
        tools_menu.addAction(rename_action)
        
        tools_menu.addSeparator()
        
        undo_action = QAction("撤销上次重命名(&U)", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self._on_undo_last)
        tools_menu.addAction(undo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 主题子菜单
        theme_menu = view_menu.addMenu("主题(&T)")
        
        light_theme_action = QAction("亮色主题(&L)", self)
        light_theme_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
        light_theme_action.triggered.connect(lambda: self._on_switch_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("暗色主题(&D)", self)
        dark_theme_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        dark_theme_action.triggered.connect(lambda: self._on_switch_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        view_menu.addSeparator()
        
        # 切换面板快捷键
        library_action = QAction("媒体库(&1)", self)
        library_action.setShortcut(QKeySequence("Ctrl+1"))
        library_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(library_action)
        
        match_action_view = QAction("匹配识别(&2)", self)
        match_action_view.setShortcut(QKeySequence("Ctrl+2"))
        match_action_view.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(match_action_view)
        
        rules_action = QAction("重命名规则(&3)", self)
        rules_action.setShortcut(QKeySequence("Ctrl+3"))
        rules_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(rules_action)
        
        history_action = QAction("历史记录(&4)", self)
        history_action.setShortcut(QKeySequence("Ctrl+4"))
        history_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        view_menu.addAction(history_action)
        
        view_menu.addSeparator()
        
        # 清空日志
        clear_log_action = QAction("清空日志(&C)", self)
        clear_log_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_log_action.triggered.connect(self._on_clear_log)
        view_menu.addAction(clear_log_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)...", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
        doc_action = QAction("使用文档(&D)", self)
        doc_action.triggered.connect(self._on_documentation)
        help_menu.addAction(doc_action)
        
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 打开目录
        open_btn = QAction("打开目录", self)
        open_btn.setToolTip("打开并扫描媒体目录")
        open_btn.triggered.connect(self._on_open_directory)
        toolbar.addAction(open_btn)
        
        toolbar.addSeparator()
        
        # 匹配
        match_btn = QAction("匹配", self)
        match_btn.setToolTip("匹配选中的文件")
        match_btn.triggered.connect(self._on_match_files)
        toolbar.addAction(match_btn)
        
        # 重命名
        rename_btn = QAction("重命名", self)
        rename_btn.setToolTip("批量重命名文件")
        rename_btn.triggered.connect(self._on_batch_rename)
        toolbar.addAction(rename_btn)
        
        toolbar.addSeparator()
        
        # 撤销
        undo_btn = QAction("撤销", self)
        undo_btn.setToolTip("撤销上次重命名")
        undo_btn.triggered.connect(self._on_undo_last)
        toolbar.addAction(undo_btn)
        
        toolbar.addSeparator()
        
        # 设置
        settings_btn = QAction("设置", self)
        settings_btn.setToolTip("打开设置")
        settings_btn.triggered.connect(self._on_settings)
        toolbar.addAction(settings_btn)
        
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("就绪")
        
    def _connect_signals(self):
        """连接信号"""
        # 媒体库面板
        self.library_panel.files_selected.connect(self._on_files_selected_for_match)
        
        # 匹配面板
        self.match_panel.match_confirmed.connect(self._on_match_confirmed)
        
        # 规则面板
        self.rule_panel.rule_changed.connect(self._on_rule_changed)
        
    def _check_config(self):
        """检查配置"""
        is_valid, error_msg = self.config.validate()
        if not is_valid:
            QMessageBox.warning(
                self,
                "配置警告",
                f"配置验证失败:\n{error_msg}\n\n"
                "请在设置中配置 TMDB API Key 后才能使用匹配功能。"
            )
            logger.warning(f"配置验证失败: {error_msg}")
        else:
            logger.info("配置验证通过")
            
    @Slot()
    def _on_open_directory(self):
        """打开目录"""
        # 切换到媒体库选项卡
        self.tab_widget.setCurrentWidget(self.library_panel)
        
        # 触发扫描
        self.library_panel._on_scan()
        
    @Slot(list)
    def _on_files_selected_for_match(self, files: List[MediaFile]):
        """文件被选中进行匹配"""
        logger.info(f"选中 {len(files)} 个文件进行匹配")
        
        # 切换到匹配选项卡
        self.tab_widget.setCurrentWidget(self.match_panel)
        
        # 开始匹配
        self.match_panel.set_files(files)
        
    @Slot(object, object)
    def _on_match_confirmed(self, media_file: MediaFile, match_result: MatchResult):
        """匹配确认"""
        logger.info(f"确认匹配: {media_file.original_name} -> {match_result.title}")
        
        # 更新媒体文件信息
        media_file.tmdb_id = match_result.tmdb_id
        media_file.title = match_result.title
        media_file.year = match_result.year
        media_file.media_type = MediaType.MOVIE if match_result.is_movie else MediaType.TV_SHOW
        
        # 从元数据中提取额外信息
        if "overview" in match_result.metadata:
            media_file.metadata["overview"] = match_result.metadata["overview"]
            
        # 添加到匹配文件列表
        if media_file not in self.matched_files:
            self.matched_files.append(media_file)
            
        # 更新文件状态
        media_file.rename_status = "matched"
        
        # 更新规则预览
        self._update_rule_preview()
        
        self.statusbar.showMessage(f"已匹配: {media_file.title}")
        
    @Slot()
    def _on_match_files(self):
        """匹配文件"""
        selected_files = self.library_panel.get_selected_files()
        
        if not selected_files:
            QMessageBox.information(
                self,
                "提示",
                "请先在媒体库中选择要匹配的文件"
            )
            return
            
        self._on_files_selected_for_match(selected_files)
        
    @Slot()
    def _on_batch_rename(self):
        """批量重命名"""
        # 获取当前规则
        current_rule = self.rule_panel.get_current_rule()
        if not current_rule:
            QMessageBox.warning(
                self,
                "警告",
                "请先在重命名规则选项卡中选择一个规则"
            )
            return
            
        # 获取要重命名的文件（优先使用已匹配的文件）
        files_to_rename = self.matched_files if self.matched_files else self.library_panel.get_selected_files()
        
        if not files_to_rename:
            QMessageBox.information(
                self,
                "提示",
                "请先选择要重命名的文件，或先进行文件匹配"
            )
            return
            
        # 确认
        reply = QMessageBox.question(
            self,
            "确认重命名",
            f"确定要使用规则 '{current_rule.name}' 重命名 {len(files_to_rename)} 个文件吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # 创建重命名对话框
        dialog = RenameDialog(
            files=files_to_rename,
            rule=current_rule,
            preview_mode=False,
            parent=self
        )
        dialog.rename_completed.connect(self._on_rename_completed)
        
        # 开始重命名
        dialog.start()
        dialog.exec()
        
    @Slot(dict)
    def _on_rename_completed(self, summary: dict):
        """重命名完成"""
        logger.info(f"重命名完成: {summary}")
        
        # 清空匹配文件列表
        self.matched_files.clear()
        
        # 刷新历史记录
        self.history_panel.refresh()
        
        # 更新状态栏
        self.statusbar.showMessage(
            f"重命名完成: 成功 {summary['success']}, 失败 {summary['failed']}"
        )
        
    @Slot()
    def _on_undo_last(self):
        """撤销上次重命名"""
        # 切换到历史记录选项卡
        self.tab_widget.setCurrentWidget(self.history_panel)
        
        # TODO: 自动选择最后一条记录并撤销
        QMessageBox.information(
            self,
            "提示",
            "请在历史记录选项卡中选择要撤销的操作"
        )
        
    @Slot(object)
    def _on_rule_changed(self, rule: RenameRule):
        """规则改变"""
        logger.info(f"规则改变: {rule.name}")
        self._update_rule_preview()
        
    def _update_rule_preview(self):
        """更新规则预览"""
        # 使用匹配的文件更新预览
        if self.matched_files:
            self.rule_panel.set_preview_files(self.matched_files)
            
    @Slot()
    def _on_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()
        
    @Slot()
    def _on_settings_saved(self):
        """设置已保存"""
        logger.info("设置已保存，重新加载配置")
        self.config = get_config()
        # 应用主题（如果改变了）
        self._apply_theme()
        self.statusbar.showMessage("设置已保存")
    
    def _apply_theme(self):
        """应用主题"""
        from smartrenamer.ui.theme_manager import apply_theme
        from PySide6.QtWidgets import QApplication
        
        theme = self.config.get("theme", "light")
        apply_theme(QApplication.instance(), theme)
        logger.info(f"应用主题: {theme}")
    
    @Slot(str)
    def _on_switch_theme(self, theme_name: str):
        """切换主题"""
        from smartrenamer.ui.theme_manager import apply_theme
        from PySide6.QtWidgets import QApplication
        
        # 保存主题设置
        self.config.set("theme", theme_name)
        self.config.save()
        
        # 应用主题
        apply_theme(QApplication.instance(), theme_name)
        
        logger.info(f"切换主题: {theme_name}")
        self.statusbar.showMessage(f"已切换到{theme_name}主题")
    
    @Slot()
    def _on_clear_log(self):
        """清空日志"""
        self.log_panel.clear()
        logger.info("日志已清空")
        self.statusbar.showMessage("日志已清空")
        
    @Slot()
    def _on_about(self):
        """关于"""
        QMessageBox.about(
            self,
            "关于 SmartRenamer",
            f"<h2>SmartRenamer v{__version__}</h2>"
            "<p>智能媒体文件重命名工具</p>"
            "<p>基于 TMDB API 的电影和电视剧文件智能识别与重命名</p>"
            "<p><b>功能特性:</b></p>"
            "<ul>"
            "<li>智能文件名解析</li>"
            "<li>TMDB 自动匹配</li>"
            "<li>灵活的重命名规则（Jinja2 模板）</li>"
            "<li>批量处理</li>"
            "<li>操作历史与撤销</li>"
            "</ul>"
            "<p><b>开发者:</b> SmartRenamer Team</p>"
            "<p><b>许可证:</b> MIT License</p>"
        )
        
    @Slot()
    def _on_documentation(self):
        """使用文档"""
        QMessageBox.information(
            self,
            "使用文档",
            "<h3>快速开始</h3>"
            "<ol>"
            "<li>在设置中配置 TMDB API Key</li>"
            "<li>在媒体库选项卡中扫描媒体目录</li>"
            "<li>选择文件并进行 TMDB 匹配</li>"
            "<li>在重命名规则选项卡中选择或创建规则</li>"
            "<li>预览并执行批量重命名</li>"
            "</ol>"
            "<p>详细文档请参考项目的 README.md 文件</p>"
        )
        
    def closeEvent(self, event):
        """关闭事件"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出 SmartRenamer 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("SmartRenamer 退出")
            event.accept()
        else:
            event.ignore()
