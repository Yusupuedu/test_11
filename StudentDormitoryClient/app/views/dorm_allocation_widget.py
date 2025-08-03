# StudentDorymitoryClient/app/views/dorm_allocation_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView, QComboBox, QLabel, QSplitter
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class DormAllocationWidget(QWidget):
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
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("<h3>未分配宿舍学生</h3>"))
        self.students_table = QTableView()
        self.students_model = QStandardItemModel()
        self.students_table.setModel(self.students_model)
        self.students_model.setHorizontalHeaderLabels(['ID', '姓名', '性别', '院系', '班级'])
        left_layout.addWidget(self.students_table)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        building_layout = QHBoxLayout()
        building_layout.addWidget(QLabel("选择楼栋:"))
        self.building_selector = QComboBox()
        building_layout.addWidget(self.building_selector)
        right_layout.addLayout(building_layout)
        self.rooms_table = QTableView(self)
        self.rooms_model = QStandardItemModel()
        self.rooms_table.setModel(self.rooms_model)
        self.rooms_model.setHorizontalHeaderLabels(['ID', '房间号', '容量', '已住/容量', '性别类型'])
        right_layout.addWidget(self.rooms_table)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.allocate_button = QPushButton("执行分配", self)
        self.refresh_button = QPushButton("全部刷新", self)
        bottom_layout.addWidget(self.allocate_button)
        bottom_layout.addWidget(self.refresh_button)
        main_v_layout = QVBoxLayout()
        main_v_layout.addWidget(splitter)
        main_v_layout.addLayout(bottom_layout)
        main_layout.addLayout(main_v_layout)
        for table in [self.students_table, self.rooms_table]:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
            table.setSelectionMode(table.SelectionMode.SingleSelection)

    def _setup_connections(self):
        self.building_selector.currentTextChanged.connect(self.load_rooms)
        self.refresh_button.clicked.connect(self.refresh_all_data)
        self.allocate_button.clicked.connect(self.handle_allocation)

    def load_data(self):
        self.refresh_all_data()

    def refresh_all_data(self):
        if not self.initial_data_loaded:
            self.load_buildings()
        else:
            self.load_unallocated_students()
            self.load_rooms()

    def load_buildings(self):
        self.task_requested.emit('get_buildings', self.on_buildings_loaded, tuple())

    def on_buildings_loaded(self, is_success: bool, data: object):
        if is_success:
            current_selection = self.building_selector.currentText()
            self.building_selector.blockSignals(True)
            self.building_selector.clear()
            for building in data: self.building_selector.addItem(building['building_name'])
            index = self.building_selector.findText(current_selection)
            if index != -1: self.building_selector.setCurrentIndex(index)
            self.building_selector.blockSignals(False)
            QTimer.singleShot(0, self.load_unallocated_students)
        else:
            self.on_task_error(f"无法加载楼栋列表: {data}")

    def load_unallocated_students(self):
        self.task_requested.emit('get_unallocated_students', self.on_students_loaded, tuple())

    def on_students_loaded(self, is_success: bool, data: object):
        if is_success:
            self.students_model.removeRows(0, self.students_model.rowCount())
            for item in data:
                row = [QStandardItem(str(item.get(k, ''))) for k in ['id', 'name', 'gender', 'department', 'class_name']]
                self.students_model.appendRow(row)
            if not self.initial_data_loaded:
                self.initial_data_loaded = True
                QTimer.singleShot(0, self.load_rooms)
        else:
            self.on_task_error(f"无法加载学生列表: {data}")

    def load_rooms(self):
        building_name = self.building_selector.currentText()
        if not building_name: return
        self.task_requested.emit('get_rooms', self.on_rooms_loaded, (building_name,))

    def on_rooms_loaded(self, is_success: bool, data: object):
        if is_success:
            self.rooms_model.removeRows(0, self.rooms_model.rowCount())
            for item in data:
                occupancy_str = f"{item.get('current_occupancy', 0)} / {item.get('capacity', 0)}"
                row = [QStandardItem(str(item.get('id'))), QStandardItem(item.get('room_number')), QStandardItem(str(item.get('capacity'))), QStandardItem(occupancy_str), QStandardItem(item.get('gender_type'))]
                self.rooms_model.appendRow(row)
        else:
            self.on_task_error(f"无法加载房间列表: {data}")

    def handle_allocation(self):
        student_selection = self.students_table.selectionModel().selectedRows()
        room_selection = self.rooms_table.selectionModel().selectedRows()
        if not student_selection or not room_selection: return QMessageBox.warning(self, "提示", "请同时选择一名学生和一个房间。")
        student_id = int(self.students_model.item(student_selection[0].row(), 0).text())
        student_name = self.students_model.item(student_selection[0].row(), 1).text()
        room_id = int(self.rooms_model.item(room_selection[0].row(), 0).text())
        room_number = self.rooms_model.item(room_selection[0].row(), 1).text()
        reply = QMessageBox.question(self, "确认分配", f"确定要将 **{student_name}** 分配到 **{self.building_selector.currentText()}-{room_number}** 房间吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.task_requested.emit('allocate_dorm', self.on_allocation_finished, (student_id, room_id))

    def on_allocation_finished(self, is_success: bool, data: object):
        if is_success:
            QMessageBox.information(self, "成功", data.get("message", "分配成功！"))
            QTimer.singleShot(0, self.refresh_all_data)
        else:
            self.on_task_error(f"分配失败: {data}")

    def set_buttons_enabled(self, enabled: bool):
        self.allocate_button.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)

    def on_task_error(self, error_msg: str):
        QMessageBox.critical(self, "错误", error_msg)