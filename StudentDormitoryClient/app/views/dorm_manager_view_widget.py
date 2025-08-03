# StudentDorymitoryClient/app/views/dorm_manager_view_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from .dorm_manager_edit_dialog import DormManagerEditDialog

class DormManagerViewWidget(QWidget):
    task_requested = pyqtSignal(str, object, tuple)
    status_message_signal = pyqtSignal(str, int)

    def __init__(self, api_client, permissions: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.permissions = permissions
        self.initial_data_loaded = False
        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("刷新列表", self)
        self.add_button = QPushButton("添加宿管", self)
        self.edit_button = QPushButton("修改信息", self)
        self.delete_button = QPushButton("删除宿管", self)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        self.table_view = QTableView(self)
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['ID', '姓名', '工号', '负责楼栋', '联系方式'])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_view)
        self.add_button.setVisible(self.permissions.get('can_add', False))
        self.edit_button.setVisible(self.permissions.get('can_edit', False))
        self.delete_button.setVisible(self.permissions.get('can_delete', False))

    def _setup_connections(self):
        self.refresh_button.clicked.connect(self.load_data)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self.handle_delete)

    def load_data(self):
        self.task_requested.emit('get_dorm_managers', self.on_load_finished, tuple())

    def on_load_finished(self, is_success: bool, data: object):
        if is_success:
            self.initial_data_loaded = True
            self.model.removeRows(0, self.model.rowCount())
            for item in data:
                row = [QStandardItem(str(item.get(k, ''))) for k in ['id', 'name', 'manager_id', 'managed_building', 'phone']]
                self.model.appendRow(row)
            self.status_message_signal.emit(f"宿管数据加载成功！共 {len(data)} 条记录。", 5000)
        else:
            self.on_task_error(f"无法加载宿管列表: {data}")

    def open_add_dialog(self):
        dialog = DormManagerEditDialog(self.api_client, parent=self)
        if dialog.exec(): self.load_data()

    def open_edit_dialog(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return QMessageBox.warning(self, "提示", "请先选择要修改的宿管！")
        selected_row = selected_indexes[0].row()
        data = { 'id': int(self.model.item(selected_row, 0).text()), 'name': self.model.item(selected_row, 1).text(), 'manager_id': self.model.item(selected_row, 2).text(), 'managed_building': self.model.item(selected_row, 3).text(), 'phone': self.model.item(selected_row, 4).text() }
        dialog = DormManagerEditDialog(self.api_client, data, self)
        if dialog.exec(): self.load_data()

    def handle_delete(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return QMessageBox.warning(self, "提示", "请先选择要删除的宿管！")
        selected_row = selected_indexes[0].row()
        name = self.model.item(selected_row, 1).text()
        obj_id = int(self.model.item(selected_row, 0).text())
        reply = QMessageBox.question(self, "确认删除", f"确定要删除宿管 **{name}** 吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.task_requested.emit('delete_dorm_manager', self.on_delete_finished, (obj_id,))

    def on_delete_finished(self, is_success: bool, data: object):
        if is_success:
            self.status_message_signal.emit("删除成功！正在刷新列表...", 3000)
            QTimer.singleShot(0, self.load_data)
        else:
            self.on_task_error(f"删除失败: {data}")

    def set_buttons_enabled(self, enabled: bool):
        self.refresh_button.setEnabled(enabled)
        if self.permissions.get('can_add', False): self.add_button.setEnabled(enabled)
        if self.permissions.get('can_edit', False): self.edit_button.setEnabled(enabled)
        if self.permissions.get('can_delete', False): self.delete_button.setEnabled(enabled)

    def on_task_error(self, error_msg: str):
        QMessageBox.critical(self, "错误", error_msg)