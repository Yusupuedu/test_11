# StudentDorymitoryClient/app/views/dorm_room_view_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView, QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from .dorm_room_edit_dialog import DormRoomEditDialog

class DormRoomViewWidget(QWidget):
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
        top_layout = QHBoxLayout()
        self.building_selector = QComboBox()
        top_layout.addWidget(QLabel("筛选楼栋:"))
        top_layout.addWidget(self.building_selector)
        top_layout.addStretch()
        self.add_button = QPushButton("添加新房间", self)
        self.edit_button = QPushButton("修改房间信息", self)
        self.delete_button = QPushButton("删除房间", self)
        top_layout.addWidget(self.add_button)
        top_layout.addWidget(self.edit_button)
        top_layout.addWidget(self.delete_button)
        self.table_view = QTableView(self)
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.model.setHorizontalHeaderLabels(['ID', '房间号', '所属楼栋', '容量', '已住人数', '性别类型'])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table_view)

    def _setup_connections(self):
        self.building_selector.currentTextChanged.connect(self.on_building_selected)
        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self.handle_delete)

    def load_data(self):
        self.task_requested.emit('get_buildings', self.on_buildings_loaded, tuple())

    def on_buildings_loaded(self, is_success: bool, data: object):
        if is_success:
            self.initial_data_loaded = True
            current_selection = self.building_selector.currentText()
            self.building_selector.blockSignals(True)
            self.building_selector.clear()
            self.building_selector.addItem("所有楼栋")
            for building in data: self.building_selector.addItem(building['building_name'])
            index = self.building_selector.findText(current_selection)
            if index != -1: self.building_selector.setCurrentIndex(index)
            self.building_selector.blockSignals(False)
            if not current_selection or index == -1: self.on_building_selected(self.building_selector.currentText())
        else:
            self.on_task_error(f"无法加载楼栋列表: {data}")

    def on_building_selected(self, building_name):
        if not building_name: return
        param = (building_name,) if building_name != "所有楼栋" else tuple()
        self.task_requested.emit('get_rooms', self.on_rooms_loaded, param)

    def on_rooms_loaded(self, is_success: bool, data: object):
        if is_success:
            self.model.removeRows(0, self.model.rowCount())
            for item in data:
                row = [QStandardItem(str(item.get(k, ''))) for k in ['id', 'room_number', 'building_name', 'capacity', 'current_occupancy', 'gender_type']]
                self.model.appendRow(row)
        else:
            self.on_task_error(f"无法加载房间列表: {data}")

    def open_add_dialog(self):
        dialog = DormRoomEditDialog(self.api_client, parent=self)
        if dialog.exec(): self.on_building_selected(self.building_selector.currentText())

    def open_edit_dialog(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return QMessageBox.warning(self, "提示", "请先选择要修改的房间！")
        selected_row = selected_indexes[0].row()
        data = { 'id': int(self.model.item(selected_row, 0).text()), 'room_number': self.model.item(selected_row, 1).text(), 'building_name': self.model.item(selected_row, 2).text(), 'capacity': self.model.item(selected_row, 3).text(), 'gender_type': self.model.item(selected_row, 5).text() }
        dialog = DormRoomEditDialog(self.api_client, data, self)
        if dialog.exec(): self.on_building_selected(self.building_selector.currentText())

    def handle_delete(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return QMessageBox.warning(self, "提示", "请先选择要删除的房间！")
        selected_row = selected_indexes[0].row()
        building = self.model.item(selected_row, 2).text()
        room_num = self.model.item(selected_row, 1).text()
        obj_id = int(self.model.item(selected_row, 0).text())
        reply = QMessageBox.question(self, "确认删除", f"确定要删除 **{building}-{room_num}** 吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.task_requested.emit('delete_room', self.on_delete_finished, (obj_id,))

    def on_delete_finished(self, is_success: bool, data: object):
        if is_success:
            QTimer.singleShot(0, lambda: self.on_building_selected(self.building_selector.currentText()))
        else:
            self.on_task_error(f"删除失败: {data}")

    def set_buttons_enabled(self, enabled: bool):
        self.add_button.setEnabled(enabled)
        self.edit_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def on_task_error(self, error_msg: str):
        QMessageBox.critical(self, "错误", error_msg)