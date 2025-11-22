"""
UI 组件测试

测试 PySide6 GUI 组件的功能
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# 设置 Qt 为 offscreen 模式，以便在无头环境中运行
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from smartrenamer.core import MediaFile, MediaType, RenameRule, create_predefined_rule
from smartrenamer.ui.widgets import (
    LogWidget, MediaFileTableWidget, ImageLabel, PathSelector, ProgressWidget
)
from smartrenamer.ui.main_window import MainWindow
from smartrenamer.ui.media_library_panel import MediaLibraryPanel
from smartrenamer.ui.match_panel import MatchPanel
from smartrenamer.ui.rule_editor_panel import RuleEditorPanel
from smartrenamer.ui.history_panel import HistoryPanel
from smartrenamer.ui.settings_dialog import SettingsDialog


@pytest.fixture(scope="module")
def qapp():
    """创建 QApplication 实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    

@pytest.fixture
def sample_media_files():
    """示例媒体文件"""
    return [
        MediaFile(
            path=Path("/test/movies/The.Matrix.1999.1080p.mkv"),
            original_name="The.Matrix.1999.1080p.mkv",
            extension=".mkv",
            size=1024 * 1024 * 1024,
            media_type=MediaType.MOVIE,
            title="The Matrix",
            year=1999,
            resolution="1080p"
        ),
        MediaFile(
            path=Path("/test/tv/Breaking.Bad.S01E01.mkv"),
            original_name="Breaking.Bad.S01E01.mkv",
            extension=".mkv",
            size=512 * 1024 * 1024,
            media_type=MediaType.TV_SHOW,
            title="Breaking Bad",
            season_number=1,
            episode_number=1
        )
    ]


class TestLogWidget:
    """测试日志控件"""
    
    def test_create_log_widget(self, qapp):
        """测试创建日志控件"""
        widget = LogWidget()
        assert widget is not None
        assert widget.isReadOnly()
        
    def test_append_log(self, qapp):
        """测试添加日志"""
        widget = LogWidget()
        widget.append_log("INFO", "测试消息")
        assert "测试消息" in widget.toPlainText()


class TestMediaFileTableWidget:
    """测试媒体文件表格控件"""
    
    def test_create_table(self, qapp):
        """测试创建表格"""
        table = MediaFileTableWidget()
        assert table is not None
        assert table.columnCount() == 7
        
    def test_add_media_file(self, qapp, sample_media_files):
        """测试添加媒体文件"""
        table = MediaFileTableWidget()
        file = sample_media_files[0]
        
        table.add_media_file(file)
        assert table.rowCount() == 1
        assert table.item(0, 0).text() == file.original_name
        
    def test_get_selected_files(self, qapp, sample_media_files):
        """测试获取选中文件"""
        table = MediaFileTableWidget()
        for file in sample_media_files:
            table.add_media_file(file)
            
        # 选中第一行
        table.selectRow(0)
        selected = table.get_selected_files()
        assert len(selected) == 1
        assert selected[0].original_name == sample_media_files[0].original_name
        
    def test_clear_files(self, qapp, sample_media_files):
        """测试清空文件列表"""
        table = MediaFileTableWidget()
        for file in sample_media_files:
            table.add_media_file(file)
            
        assert table.rowCount() == 2
        table.clear_files()
        assert table.rowCount() == 0


class TestImageLabel:
    """测试图片标签控件"""
    
    def test_create_image_label(self, qapp):
        """测试创建图片标签"""
        label = ImageLabel()
        assert label is not None
        assert "暂无海报" in label.text()
        
    def test_clear_image(self, qapp):
        """测试清空图片"""
        label = ImageLabel()
        label.clear_image()
        assert "暂无海报" in label.text()


class TestPathSelector:
    """测试路径选择控件"""
    
    def test_create_path_selector(self, qapp):
        """测试创建路径选择器"""
        selector = PathSelector("测试路径:")
        assert selector is not None
        assert selector.label.text() == "测试路径:"
        
    def test_set_get_path(self, qapp):
        """测试设置和获取路径"""
        selector = PathSelector()
        test_path = Path("/test/path")
        
        selector.set_path(test_path)
        assert selector.get_path() == test_path


class TestProgressWidget:
    """测试进度控件"""
    
    def test_create_progress_widget(self, qapp):
        """测试创建进度控件"""
        widget = ProgressWidget()
        assert widget is not None
        
    def test_set_progress(self, qapp):
        """测试设置进度"""
        widget = ProgressWidget()
        widget.set_progress(50, 100, "测试进度")
        
        assert widget.progress_bar.value() == 50
        assert widget.progress_bar.maximum() == 100
        assert "测试进度" in widget.label.text()
        
    def test_reset(self, qapp):
        """测试重置"""
        widget = ProgressWidget()
        widget.set_progress(50, 100)
        widget.reset()
        
        assert widget.progress_bar.value() == 0


class TestMediaLibraryPanel:
    """测试媒体库面板"""
    
    def test_create_panel(self, qapp):
        """测试创建面板"""
        panel = MediaLibraryPanel()
        assert panel is not None
        assert panel.file_table is not None
        assert panel.folder_tree is not None
        
    def test_get_selected_files(self, qapp):
        """测试获取选中文件"""
        panel = MediaLibraryPanel()
        selected = panel.get_selected_files()
        assert isinstance(selected, list)


class TestMatchPanel:
    """测试匹配面板"""
    
    def test_create_panel(self, qapp):
        """测试创建面板"""
        panel = MatchPanel()
        assert panel is not None
        assert panel.match_list is not None
        assert panel.poster_label is not None


class TestRuleEditorPanel:
    """测试规则编辑器面板"""
    
    def test_create_panel(self, qapp):
        """测试创建面板"""
        panel = RuleEditorPanel()
        assert panel is not None
        assert panel.rule_list is not None
        assert panel.template_edit is not None
        
    def test_load_rules(self, qapp):
        """测试加载规则"""
        panel = RuleEditorPanel()
        # 应该至少有预定义规则
        assert panel.rule_list.count() > 0
        
    def test_get_current_rule(self, qapp):
        """测试获取当前规则"""
        panel = RuleEditorPanel()
        # 初始状态应该没有选中规则
        assert panel.get_current_rule() is None
        
        # 选择第一个规则
        panel.rule_list.setCurrentRow(0)
        panel._on_rule_selected(panel.rule_list.item(0))
        assert panel.get_current_rule() is not None


class TestHistoryPanel:
    """测试历史记录面板"""
    
    def test_create_panel(self, qapp):
        """测试创建面板"""
        panel = HistoryPanel()
        assert panel is not None
        assert panel.history_table is not None
        
    def test_refresh(self, qapp):
        """测试刷新"""
        panel = HistoryPanel()
        panel.refresh()
        # 应该不会抛出异常


class TestSettingsDialog:
    """测试设置对话框"""
    
    def test_create_dialog(self, qapp):
        """测试创建对话框"""
        dialog = SettingsDialog()
        assert dialog is not None
        assert dialog.api_key_edit is not None
        assert dialog.language_combo is not None


class TestMainWindow:
    """测试主窗口"""
    
    def test_create_main_window(self, qapp):
        """测试创建主窗口"""
        window = MainWindow()
        assert window is not None
        assert window.library_panel is not None
        assert window.match_panel is not None
        assert window.rule_panel is not None
        assert window.history_panel is not None
        assert window.log_panel is not None
        
    def test_tab_widget(self, qapp):
        """测试选项卡"""
        window = MainWindow()
        assert window.tab_widget.count() == 4
        
    def test_menus(self, qapp):
        """测试菜单"""
        window = MainWindow()
        menubar = window.menuBar()
        assert menubar is not None
        
        # 检查菜单项
        actions = menubar.actions()
        assert len(actions) >= 4  # 文件、编辑、工具、帮助
        
    def test_toolbar(self, qapp):
        """测试工具栏"""
        window = MainWindow()
        toolbars = window.findChildren(type(window.toolBar()))
        assert len(toolbars) > 0
        
    def test_statusbar(self, qapp):
        """测试状态栏"""
        window = MainWindow()
        assert window.statusbar is not None


class TestUIIntegration:
    """测试 UI 集成"""
    
    def test_file_selection_to_match(self, qapp, sample_media_files):
        """测试从文件选择到匹配的流程"""
        window = MainWindow()
        
        # 模拟文件选择
        window.library_panel.current_files = sample_media_files
        window.library_panel._update_file_list(sample_media_files)
        
        # 选择文件
        window.library_panel.file_table.selectRow(0)
        
        # 获取选中文件
        selected = window.library_panel.get_selected_files()
        assert len(selected) > 0
        
    def test_rule_selection(self, qapp):
        """测试规则选择"""
        window = MainWindow()
        
        # 选择第一个规则
        window.rule_panel.rule_list.setCurrentRow(0)
        window.rule_panel._on_rule_selected(window.rule_panel.rule_list.item(0))
        
        # 应该有当前规则
        current_rule = window.rule_panel.get_current_rule()
        assert current_rule is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
