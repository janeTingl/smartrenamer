"""
媒体库浏览面板

提供文件夹树形浏览和媒体文件列表功能
"""
import logging
from typing import Optional, List
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QTreeWidget, QTreeWidgetItem, QPushButton, QLineEdit,
    QLabel, QComboBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from smartrenamer.core import FileScanner, MediaLibrary, MediaFile, MediaType
from smartrenamer.ui.widgets import MediaFileTableWidget


logger = logging.getLogger(__name__)


class ScanWorker(QThread):
    """扫描工作线程"""
    
    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(list)  # files
    error = Signal(str)
    
    def __init__(self, path: Path, scanner: FileScanner):
        super().__init__()
        self.path = path
        self.scanner = scanner
        
    def run(self):
        """运行扫描"""
        try:
            logger.info(f"开始扫描目录: {self.path}")
            files = self.scanner.scan(self.path)
            logger.info(f"扫描完成，共找到 {len(files)} 个文件")
            self.finished.emit(files)
        except Exception as e:
            logger.error(f"扫描失败: {e}")
            self.error.emit(str(e))


class MediaLibraryPanel(QWidget):
    """媒体库浏览面板"""
    
    files_selected = Signal(list)  # 当文件被选中时发出信号
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.scanner = FileScanner()
        self.library = MediaLibrary()
        self.current_files: List[MediaFile] = []
        self.scan_worker: Optional[ScanWorker] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)
        
        # 搜索栏
        search_bar = self._create_search_bar()
        layout.addLayout(search_bar)
        
        # 主内容区域：分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：文件夹树
        self.folder_tree = self._create_folder_tree()
        splitter.addWidget(self.folder_tree)
        
        # 右侧：文件列表
        self.file_table = MediaFileTableWidget()
        self.file_table.file_selected.connect(self._on_file_selected)
        splitter.addWidget(self.file_table)
        
        splitter.setSizes([200, 600])
        layout.addWidget(splitter)
        
        # 底部状态栏
        status_bar = self._create_status_bar()
        layout.addLayout(status_bar)
        
    def _create_toolbar(self) -> QHBoxLayout:
        """创建工具栏"""
        toolbar = QHBoxLayout()
        
        self.scan_btn = QPushButton("扫描目录")
        self.scan_btn.clicked.connect(self._on_scan)
        toolbar.addWidget(self.scan_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self._on_refresh)
        toolbar.addWidget(self.refresh_btn)
        
        toolbar.addStretch()
        
        self.match_btn = QPushButton("匹配选中文件")
        self.match_btn.clicked.connect(self._on_match_selected)
        self.match_btn.setEnabled(False)
        toolbar.addWidget(self.match_btn)
        
        return toolbar
        
    def _create_search_bar(self) -> QHBoxLayout:
        """创建搜索栏"""
        search_bar = QHBoxLayout()
        
        search_bar.addWidget(QLabel("搜索:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入标题、路径进行搜索...")
        self.search_edit.textChanged.connect(self._on_search)
        search_bar.addWidget(self.search_edit, 1)
        
        search_bar.addWidget(QLabel("类型:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部", "电影", "电视剧", "未知"])
        self.type_filter.currentTextChanged.connect(self._on_filter_changed)
        search_bar.addWidget(self.type_filter)
        
        return search_bar
        
    def _create_folder_tree(self) -> QTreeWidget:
        """创建文件夹树"""
        tree = QTreeWidget()
        tree.setHeaderLabel("文件夹")
        tree.itemClicked.connect(self._on_folder_clicked)
        return tree
        
    def _create_status_bar(self) -> QHBoxLayout:
        """创建状态栏"""
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        status_bar.addStretch()
        
        self.file_count_label = QLabel("文件: 0")
        status_bar.addWidget(self.file_count_label)
        
        return status_bar
        
    @Slot()
    def _on_scan(self):
        """扫描按钮点击"""
        # 选择目录
        path = QFileDialog.getExistingDirectory(
            self,
            "选择要扫描的目录",
            str(Path.home())
        )
        
        if not path:
            return
            
        self._start_scan(Path(path))
        
    def _start_scan(self, path: Path):
        """开始扫描"""
        if self.scan_worker and self.scan_worker.isRunning():
            QMessageBox.warning(self, "警告", "扫描正在进行中，请等待完成")
            return
            
        # 禁用按钮
        self.scan_btn.setEnabled(False)
        self.status_label.setText(f"正在扫描: {path}")
        
        # 创建工作线程
        self.scan_worker = ScanWorker(path, self.scanner)
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.error.connect(self._on_scan_error)
        self.scan_worker.start()
        
    @Slot(list)
    def _on_scan_finished(self, files: List[MediaFile]):
        """扫描完成"""
        self.current_files = files
        self._update_file_list(files)
        self._update_folder_tree(files)
        
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f"扫描完成，共找到 {len(files)} 个文件")
        self.file_count_label.setText(f"文件: {len(files)}")
        
        logger.info(f"扫描完成，共 {len(files)} 个文件")
        
    @Slot(str)
    def _on_scan_error(self, error: str):
        """扫描错误"""
        self.scan_btn.setEnabled(True)
        self.status_label.setText("扫描失败")
        
        QMessageBox.critical(self, "错误", f"扫描失败:\n{error}")
        
    @Slot()
    def _on_refresh(self):
        """刷新按钮点击"""
        self._update_file_list(self.current_files)
        self.status_label.setText("已刷新")
        
    @Slot()
    def _on_match_selected(self):
        """匹配选中文件按钮点击"""
        selected_files = self.file_table.get_selected_files()
        if selected_files:
            self.files_selected.emit(selected_files)
        else:
            QMessageBox.information(self, "提示", "请先选择要匹配的文件")
            
    @Slot(str)
    def _on_search(self, text: str):
        """搜索文本改变"""
        self._apply_filters()
        
    @Slot(str)
    def _on_filter_changed(self, text: str):
        """过滤器改变"""
        self._apply_filters()
        
    def _apply_filters(self):
        """应用过滤器"""
        search_text = self.search_edit.text().lower()
        type_filter = self.type_filter.currentText()
        
        filtered_files = []
        for file in self.current_files:
            # 类型过滤
            if type_filter != "全部":
                if type_filter == "电影" and not file.is_movie:
                    continue
                elif type_filter == "电视剧" and not file.is_tv_show:
                    continue
                elif type_filter == "未知" and file.media_type != MediaType.UNKNOWN:
                    continue
                    
            # 搜索过滤
            if search_text:
                if not any([
                    search_text in file.original_name.lower(),
                    search_text in (file.title or "").lower(),
                    search_text in str(file.path).lower()
                ]):
                    continue
                    
            filtered_files.append(file)
            
        self._update_file_list(filtered_files)
        self.file_count_label.setText(f"文件: {len(filtered_files)}/{len(self.current_files)}")
        
    def _update_file_list(self, files: List[MediaFile]):
        """更新文件列表"""
        self.file_table.clear_files()
        for file in files:
            self.file_table.add_media_file(file)
            
    def _update_folder_tree(self, files: List[MediaFile]):
        """更新文件夹树"""
        self.folder_tree.clear()
        
        # 按路径组织文件
        folders = {}
        for file in files:
            folder = file.path.parent
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(file)
            
        # 添加到树
        for folder, folder_files in sorted(folders.items()):
            item = QTreeWidgetItem(self.folder_tree)
            item.setText(0, f"{folder.name} ({len(folder_files)})")
            item.setData(0, Qt.UserRole, folder)
            
    @Slot(QTreeWidgetItem, int)
    def _on_folder_clicked(self, item: QTreeWidgetItem, column: int):
        """文件夹点击"""
        folder = item.data(0, Qt.UserRole)
        if folder:
            # 过滤显示该文件夹下的文件
            filtered_files = [f for f in self.current_files if f.path.parent == folder]
            self._update_file_list(filtered_files)
            self.file_count_label.setText(f"文件: {len(filtered_files)}/{len(self.current_files)}")
            
    @Slot(object)
    def _on_file_selected(self, media_file: MediaFile):
        """文件选中"""
        # 启用匹配按钮
        self.match_btn.setEnabled(True)
        
    def get_selected_files(self) -> List[MediaFile]:
        """获取选中的文件"""
        return self.file_table.get_selected_files()
    
    def get_all_files(self) -> List[MediaFile]:
        """获取所有文件"""
        return self.current_files
