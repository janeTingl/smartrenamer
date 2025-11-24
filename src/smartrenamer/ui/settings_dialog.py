"""
设置对话框

配置应用程序设置
"""
import logging
from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QGroupBox, QComboBox,
    QCheckBox, QMessageBox, QFileDialog, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from smartrenamer.core import get_config, set_config, Config
from smartrenamer.ui.widgets import PathSelector
from smartrenamer.api import get_cache_stats


logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """设置对话框"""
    
    settings_saved = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config = get_config()
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 选项卡
        tabs = QTabWidget()
        
        # API 设置
        api_tab = self._create_api_tab()
        tabs.addTab(api_tab, "API 配置")
        
        # 路径设置
        path_tab = self._create_path_tab()
        tabs.addTab(path_tab, "路径配置")
        
        # 重命名设置
        rename_tab = self._create_rename_tab()
        tabs.addTab(rename_tab, "重命名选项")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def _create_api_tab(self) -> QWidget:
        """创建 API 设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # TMDB API 配置
        tmdb_group = QGroupBox("TMDB API 配置")
        tmdb_layout = QVBoxLayout(tmdb_group)
        
        # API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("API Key:"))
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("请输入 TMDB API Key")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        api_key_layout.addWidget(self.api_key_edit, 1)
        
        show_key_btn = QPushButton("显示")
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(
            lambda checked: self.api_key_edit.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        api_key_layout.addWidget(show_key_btn)
        
        tmdb_layout.addLayout(api_key_layout)
        
        # 语言
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("语言:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["zh-CN", "en-US", "ja-JP", "ko-KR"])
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        tmdb_layout.addLayout(lang_layout)
        
        # 说明
        help_label = QLabel(
            "提示: 请前往 https://www.themoviedb.org/settings/api 获取 API Key"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("QLabel { color: gray; }")
        tmdb_layout.addWidget(help_label)
        
        layout.addWidget(tmdb_group)
        
        # TMDB 缓存配置
        cache_group = QGroupBox("TMDB 缓存配置")
        cache_layout = QVBoxLayout(cache_group)
        
        # 启用缓存
        self.tmdb_cache_enabled = QCheckBox("启用 TMDB 缓存")
        self.tmdb_cache_enabled.setChecked(True)
        cache_layout.addWidget(self.tmdb_cache_enabled)
        
        # TTL
        ttl_layout = QHBoxLayout()
        ttl_layout.addWidget(QLabel("缓存有效期（小时）:"))
        self.tmdb_cache_ttl = QSpinBox()
        self.tmdb_cache_ttl.setRange(1, 720)  # 1小时 到 30天
        self.tmdb_cache_ttl.setValue(168)  # 默认 7 天
        self.tmdb_cache_ttl.setSuffix(" 小时")
        ttl_layout.addWidget(self.tmdb_cache_ttl)
        ttl_layout.addStretch()
        cache_layout.addLayout(ttl_layout)
        
        # 最大条目数
        entries_layout = QHBoxLayout()
        entries_layout.addWidget(QLabel("内存缓存容量:"))
        self.tmdb_cache_max_entries = QSpinBox()
        self.tmdb_cache_max_entries.setRange(100, 10000)
        self.tmdb_cache_max_entries.setValue(1000)
        self.tmdb_cache_max_entries.setSuffix(" 条")
        entries_layout.addWidget(self.tmdb_cache_max_entries)
        entries_layout.addStretch()
        cache_layout.addLayout(entries_layout)
        
        # 缓存统计
        stats_layout = QHBoxLayout()
        self.cache_stats_label = QLabel("缓存统计: 未加载")
        self.cache_stats_label.setStyleSheet("QLabel { color: gray; font-size: 10px; }")
        stats_layout.addWidget(self.cache_stats_label)
        
        refresh_stats_btn = QPushButton("刷新统计")
        refresh_stats_btn.clicked.connect(self._on_refresh_cache_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        clear_tmdb_cache_btn = QPushButton("清空 TMDB 缓存")
        clear_tmdb_cache_btn.clicked.connect(self._on_clear_tmdb_cache)
        stats_layout.addWidget(clear_tmdb_cache_btn)
        
        cache_layout.addLayout(stats_layout)
        
        layout.addWidget(cache_group)
        layout.addStretch()
        
        return widget
        
    def _create_path_tab(self) -> QWidget:
        """创建路径设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 默认扫描路径
        scan_group = QGroupBox("默认扫描路径")
        scan_layout = QVBoxLayout(scan_group)
        
        self.scan_path_selector = PathSelector("扫描路径:")
        scan_layout.addWidget(self.scan_path_selector)
        
        layout.addWidget(scan_group)
        
        # 缓存目录
        cache_group = QGroupBox("缓存配置")
        cache_layout = QVBoxLayout(cache_group)
        
        cache_path_layout = QHBoxLayout()
        cache_path_layout.addWidget(QLabel("缓存目录:"))
        self.cache_path_label = QLabel()
        self.cache_path_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; }")
        cache_path_layout.addWidget(self.cache_path_label, 1)
        cache_layout.addLayout(cache_path_layout)
        
        clear_cache_btn = QPushButton("清空缓存")
        clear_cache_btn.clicked.connect(self._on_clear_cache)
        cache_layout.addWidget(clear_cache_btn)
        
        layout.addWidget(cache_group)
        layout.addStretch()
        
        return widget
        
    def _create_rename_tab(self) -> QWidget:
        """创建重命名设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 重命名选项
        options_group = QGroupBox("重命名选项")
        options_layout = QVBoxLayout(options_group)
        
        self.backup_checkbox = QCheckBox("重命名前创建备份")
        options_layout.addWidget(self.backup_checkbox)
        
        self.preview_checkbox = QCheckBox("默认启用预览模式")
        options_layout.addWidget(self.preview_checkbox)
        
        self.auto_confirm_checkbox = QCheckBox("自动确认高置信度匹配")
        options_layout.addWidget(self.auto_confirm_checkbox)
        
        layout.addWidget(options_group)
        
        # 匹配设置
        match_group = QGroupBox("匹配设置")
        match_layout = QVBoxLayout(match_group)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("相似度阈值:"))
        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems(["0.5", "0.6", "0.7", "0.8", "0.9"])
        threshold_layout.addWidget(self.threshold_combo)
        threshold_layout.addStretch()
        match_layout.addLayout(threshold_layout)
        
        layout.addWidget(match_group)
        layout.addStretch()
        
        return widget
        
    def _load_settings(self):
        """加载设置"""
        # API 设置
        self.api_key_edit.setText(self.config.tmdb_api_key or "")
        
        lang_index = self.language_combo.findText(self.config.tmdb_language)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # TMDB 缓存配置
        self.tmdb_cache_enabled.setChecked(self.config.get("tmdb_cache_enabled", True))
        self.tmdb_cache_ttl.setValue(self.config.get("tmdb_cache_ttl_hours", 168))
        self.tmdb_cache_max_entries.setValue(self.config.get("tmdb_cache_max_entries", 1000))
        
        # 刷新缓存统计
        self._on_refresh_cache_stats()
            
        # 路径设置
        if self.config.scan_sources and len(self.config.scan_sources) > 0:
            self.scan_path_selector.set_path(Path(self.config.scan_sources[0]))
            
        cache_dir = self.config.get_cache_dir()
        self.cache_path_label.setText(str(cache_dir))
        
        # 重命名选项
        self.backup_checkbox.setChecked(self.config.get("create_backup", True))
        self.preview_checkbox.setChecked(self.config.get("preview_mode", True))
        self.auto_confirm_checkbox.setChecked(self.config.get("auto_confirm", True))
        
        threshold = str(self.config.get("similarity_threshold", 0.8))
        threshold_index = self.threshold_combo.findText(threshold)
        if threshold_index >= 0:
            self.threshold_combo.setCurrentIndex(threshold_index)
            
    def _on_save(self):
        """保存设置"""
        # API 设置
        api_key = self.api_key_edit.text().strip()
        if api_key:
            self.config.tmdb_api_key = api_key
        else:
            QMessageBox.warning(self, "警告", "TMDB API Key 不能为空")
            return
            
        self.config.tmdb_language = self.language_combo.currentText()
        
        # TMDB 缓存配置
        self.config.set("tmdb_cache_enabled", self.tmdb_cache_enabled.isChecked())
        self.config.set("tmdb_cache_ttl_hours", self.tmdb_cache_ttl.value())
        self.config.set("tmdb_cache_max_entries", self.tmdb_cache_max_entries.value())
        
        # 路径设置
        scan_path = self.scan_path_selector.get_path()
        if scan_path:
            self.config.scan_sources = [str(scan_path)]
            
        # 重命名选项
        self.config.set("create_backup", self.backup_checkbox.isChecked())
        self.config.set("preview_mode", self.preview_checkbox.isChecked())
        self.config.set("auto_confirm", self.auto_confirm_checkbox.isChecked())
        self.config.set("similarity_threshold", float(self.threshold_combo.currentText()))
        
        # 保存配置
        self.config.save()
        
        # 更新全局配置
        set_config(self.config)
        
        logger.info("设置已保存")
        self.settings_saved.emit()
        
        QMessageBox.information(self, "成功", "设置已保存")
        self.accept()
        
    def _on_clear_cache(self):
        """清空缓存"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空所有缓存吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cache_dir = self.config.get_cache_dir()
            
            # 删除缓存文件
            import shutil
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True)
                
            logger.info("缓存已清空")
            QMessageBox.information(self, "成功", "缓存已清空")
    
    def _on_clear_tmdb_cache(self):
        """清空 TMDB 缓存"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空 TMDB 缓存吗？这将清空所有电影和电视剧的查询缓存。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from smartrenamer.api import clear_tmdb_client
                
                # 清除客户端实例（这会触发缓存清空）
                clear_tmdb_client()
                
                # 删除 TMDB 缓存目录
                tmdb_cache_dir = self.config.get_cache_dir() / "tmdb"
                if tmdb_cache_dir.exists():
                    import shutil
                    shutil.rmtree(tmdb_cache_dir)
                    tmdb_cache_dir.mkdir(parents=True)
                
                logger.info("TMDB 缓存已清空")
                QMessageBox.information(self, "成功", "TMDB 缓存已清空")
                
                # 刷新统计
                self._on_refresh_cache_stats()
                
            except Exception as e:
                logger.error(f"清空 TMDB 缓存失败: {e}")
                QMessageBox.warning(self, "错误", f"清空缓存失败: {e}")
    
    def _on_refresh_cache_stats(self):
        """刷新缓存统计"""
        try:
            stats = get_cache_stats()
            
            if not stats.get("enabled", False):
                self.cache_stats_label.setText("缓存统计: 缓存未启用")
            else:
                hit_rate = stats.get("hit_rate", 0.0) * 100
                memory_hits = stats.get("memory_hits", 0)
                disk_hits = stats.get("disk_hits", 0)
                total_requests = stats.get("total_requests", 0)
                memory_entries = stats.get("memory_entries", 0)
                
                stats_text = (
                    f"缓存统计: 总请求 {total_requests} 次, "
                    f"命中率 {hit_rate:.1f}% "
                    f"(内存 {memory_hits}, 磁盘 {disk_hits}), "
                    f"内存条目 {memory_entries}"
                )
                self.cache_stats_label.setText(stats_text)
                
        except Exception as e:
            logger.warning(f"获取缓存统计失败: {e}")
            self.cache_stats_label.setText("缓存统计: 获取失败")
