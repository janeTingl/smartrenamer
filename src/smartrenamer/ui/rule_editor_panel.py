"""
规则配置和预览面板

提供重命名规则的选择、编辑和预览功能
"""
import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QGroupBox, QListWidget, QListWidgetItem,
    QSplitter, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from smartrenamer.core import (
    RenameRule, MediaFile, Renamer, RenameRuleManager,
    create_predefined_rule, PREDEFINED_TEMPLATES
)


logger = logging.getLogger(__name__)


class RuleEditorPanel(QWidget):
    """规则配置和预览面板"""
    
    rule_changed = Signal(object)  # RenameRule
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.rule_manager = RenameRuleManager()
        self.renamer = Renamer(预览模式=True)
        self.current_rule: Optional[RenameRule] = None
        self.preview_files: List[MediaFile] = []
        
        self._setup_ui()
        self._load_rules()
        
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        
        # 主分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：规则选择和编辑
        top_panel = self._create_rule_editor()
        splitter.addWidget(top_panel)
        
        # 下半部分：预览
        bottom_panel = self._create_preview_panel()
        splitter.addWidget(bottom_panel)
        
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
    def _create_rule_editor(self) -> QWidget:
        """创建规则编辑器"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 左侧：规则列表
        left_panel = self._create_rule_list()
        layout.addWidget(left_panel)
        
        # 右侧：规则详情
        right_panel = self._create_rule_detail()
        layout.addWidget(right_panel, 1)
        
        return widget
        
    def _create_rule_list(self) -> QGroupBox:
        """创建规则列表"""
        group = QGroupBox("可用规则")
        layout = QVBoxLayout(group)
        
        # 规则列表
        self.rule_list = QListWidget()
        self.rule_list.itemClicked.connect(self._on_rule_selected)
        layout.addWidget(self.rule_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.new_rule_btn = QPushButton("新建")
        self.new_rule_btn.clicked.connect(self._on_new_rule)
        button_layout.addWidget(self.new_rule_btn)
        
        self.delete_rule_btn = QPushButton("删除")
        self.delete_rule_btn.clicked.connect(self._on_delete_rule)
        self.delete_rule_btn.setEnabled(False)
        button_layout.addWidget(self.delete_rule_btn)
        
        layout.addLayout(button_layout)
        
        return group
        
    def _create_rule_detail(self) -> QGroupBox:
        """创建规则详情"""
        group = QGroupBox("规则详情")
        layout = QVBoxLayout(group)
        
        # 规则名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("规则名称:"))
        self.rule_name_label = QLabel("-")
        self.rule_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_layout.addWidget(self.rule_name_label, 1)
        layout.addLayout(name_layout)
        
        # 规则描述
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.rule_desc_label = QLabel("-")
        self.rule_desc_label.setWordWrap(True)
        desc_layout.addWidget(self.rule_desc_label, 1)
        layout.addLayout(desc_layout)
        
        # 模板编辑器
        layout.addWidget(QLabel("Jinja2 模板:"))
        self.template_edit = QTextEdit()
        self.template_edit.setMaximumHeight(150)
        self.template_edit.textChanged.connect(self._on_template_changed)
        layout.addWidget(self.template_edit)
        
        # 示例
        layout.addWidget(QLabel("示例输出:"))
        self.example_label = QLabel("-")
        self.example_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; }")
        self.example_label.setWordWrap(True)
        layout.addWidget(self.example_label)
        
        # 保存按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_rule_btn = QPushButton("保存规则")
        self.save_rule_btn.clicked.connect(self._on_save_rule)
        self.save_rule_btn.setEnabled(False)
        button_layout.addWidget(self.save_rule_btn)
        
        layout.addLayout(button_layout)
        
        return group
        
    def _create_preview_panel(self) -> QGroupBox:
        """创建预览面板"""
        group = QGroupBox("预览")
        layout = QVBoxLayout(group)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("将当前规则应用到选中的文件进行预览"))
        toolbar.addStretch()
        
        self.refresh_preview_btn = QPushButton("刷新预览")
        self.refresh_preview_btn.clicked.connect(self._on_refresh_preview)
        toolbar.addWidget(self.refresh_preview_btn)
        
        layout.addLayout(toolbar)
        
        # 预览列表
        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)
        
        return group
        
    def _load_rules(self):
        """加载规则"""
        self.rule_list.clear()
        
        # 加载预定义规则
        for name in PREDEFINED_TEMPLATES.keys():
            rule = create_predefined_rule(name)
            item = QListWidgetItem(f"[预定义] {rule.name}")
            item.setData(Qt.UserRole, rule)
            self.rule_list.addItem(item)
            
        # 加载自定义规则
        custom_rules = self.rule_manager.获取所有规则()
        for rule in custom_rules:
            item = QListWidgetItem(f"[自定义] {rule.name}")
            item.setData(Qt.UserRole, rule)
            self.rule_list.addItem(item)
            
        logger.info(f"加载了 {self.rule_list.count()} 个规则")
        
    @Slot(QListWidgetItem)
    def _on_rule_selected(self, item: QListWidgetItem):
        """规则选中"""
        rule = item.data(Qt.UserRole)
        if rule:
            self._display_rule(rule)
            self.delete_rule_btn.setEnabled(not item.text().startswith("[预定义]"))
            
    def _display_rule(self, rule: RenameRule):
        """显示规则"""
        self.current_rule = rule
        
        self.rule_name_label.setText(rule.name)
        self.rule_desc_label.setText(rule.description)
        self.template_edit.setPlainText(rule.template)
        self.example_label.setText(rule.example or "-")
        
        self.save_rule_btn.setEnabled(False)
        
        # 发出信号
        self.rule_changed.emit(rule)
        
        # 刷新预览
        if self.preview_files:
            self._update_preview()
            
    @Slot()
    def _on_template_changed(self):
        """模板改变"""
        self.save_rule_btn.setEnabled(True)
        
        # 实时更新预览
        if self.preview_files and self.current_rule:
            self._update_preview()
            
    @Slot()
    def _on_new_rule(self):
        """新建规则"""
        name, ok = QInputDialog.getText(self, "新建规则", "请输入规则名称:")
        if not ok or not name:
            return
            
        desc, ok = QInputDialog.getText(self, "新建规则", "请输入规则描述:")
        if not ok:
            return
            
        # 创建新规则
        from smartrenamer.core import MediaType
        new_rule = RenameRule(
            name=name,
            description=desc or "自定义规则",
            template="{{ title }}",
            media_type=MediaType.MOVIE
        )
        
        # 保存规则
        self.rule_manager.save_rule(new_rule)
        
        # 重新加载规则列表
        self._load_rules()
        
        logger.info(f"创建新规则: {name}")
        
    @Slot()
    def _on_delete_rule(self):
        """删除规则"""
        current_item = self.rule_list.currentItem()
        if not current_item:
            return
            
        rule = current_item.data(Qt.UserRole)
        if not rule:
            return
            
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除规则 '{rule.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.rule_manager.delete_rule(rule.name)
            self._load_rules()
            logger.info(f"删除规则: {rule.name}")
            
    @Slot()
    def _on_save_rule(self):
        """保存规则"""
        if not self.current_rule:
            return
            
        # 更新模板
        self.current_rule.template = self.template_edit.toPlainText()
        
        # 保存
        self.rule_manager.save_rule(self.current_rule)
        
        self.save_rule_btn.setEnabled(False)
        
        QMessageBox.information(self, "成功", f"规则 '{self.current_rule.name}' 已保存")
        logger.info(f"保存规则: {self.current_rule.name}")
        
    @Slot()
    def _on_refresh_preview(self):
        """刷新预览"""
        self._update_preview()
        
    def set_preview_files(self, files: List[MediaFile]):
        """设置预览文件"""
        self.preview_files = files
        self._update_preview()
        
    def _update_preview(self):
        """更新预览"""
        self.preview_list.clear()
        
        if not self.current_rule or not self.preview_files:
            return
            
        # 使用当前编辑的模板创建临时规则
        temp_rule = RenameRule(
            name=self.current_rule.name,
            description=self.current_rule.description,
            template=self.template_edit.toPlainText(),
            media_type=self.current_rule.media_type
        )
        
        # 生成预览
        for file in self.preview_files[:10]:  # 最多预览10个文件
            try:
                success, new_name, error = self.renamer.generate_new_filename(file, temp_rule)
                if success:
                    item = QListWidgetItem(f"{file.original_name}\n  →  {new_name}")
                else:
                    item = QListWidgetItem(f"{file.original_name}\n  →  错误: {error}")
                self.preview_list.addItem(item)
            except Exception as e:
                item = QListWidgetItem(f"{file.original_name}\n  →  错误: {str(e)}")
                self.preview_list.addItem(item)
                
    def get_current_rule(self) -> Optional[RenameRule]:
        """获取当前规则"""
        return self.current_rule
