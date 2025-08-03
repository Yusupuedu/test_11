# StudentDormitoryClient/app/views/student_view_widget.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QMessageBox, QHeaderView
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from .student_edit_dialog import StudentEditDialog


class StudentViewWidget(QWidget):
    task_requested = pyqtSignal(str, object, tuple)
    status_message_signal = pyqtSignal(str, int)

    def __init__(self, api_client, permissions: dict, task_commander, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.permissions = permissions
        self.commander = task_commander
        self.initial_data_loaded = False

        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("刷新列表", self)
        self.add_student_button = QPushButton("添加学生", self)
        self.edit_student_button = QPushButton("修改信息", self)
        self.delete_student_button = QPushButton("删除学生", self)
        try:
            self.refresh_button.setIcon(QIcon("assets/icons/refresh-cw.svg"))
            self.add_student_button.setIcon(QIcon("assets/icons/plus-circle.svg"))
            self.edit_student_button.setIcon(QIcon("assets/icons/edit.svg"))
            self.delete_student_button.setIcon(QIcon("assets/icons/trash-2.svg"))
        except Exception as e:
            print(f"警告: 学生管理模块加载图标失败 - {e}")
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_student_button)
        button_layout.addWidget(self.edit_student_button)
        button_layout.addWidget(self.delete_student_button)
        button_layout.addStretch()
        self.table_view = QTableView(self)
        self.student_model = QStandardItemModel()
        self.table_view.setModel(self.student_model)
        headers = ['ID', '姓名', '性别', '年龄', '学号', '院系', '班级', '联系方式', '宿舍楼', '房间号']
        self.student_model.setHorizontalHeaderLabels(headers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setEditTriggers(self.table_view.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionBehavior(self.table_view.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(self.table_view.SelectionMode.SingleSelection)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table_view)
        self.add_student_button.setVisible(self.permissions.get('can_add', False))
        self.edit_student_button.setVisible(self.permissions.get('can_edit', False))
        self.delete_student_button.setVisible(self.permissions.get('can_delete', False))

    def _setup_connections(self):
        self.refresh_button.clicked.connect(self.load_data)
        self.add_student_button.clicked.connect(self.open_add_dialog)
        self.edit_student_button.clicked.connect(self.open_edit_dialog)
        self.delete_student_button.clicked.connect(self.handle_delete)

    def load_data(self):
        self.task_requested.emit('get_all_students', self.on_load_finished, tuple())

    def on_load_finished(self, is_success: bool, data: object):
        if is_success:
            self.initial_data_loaded = True
            self.student_model.removeRows(0, self.student_model.rowCount())
            for student in data:
                row = [QStandardItem(str(student.get(k, ''))) for k in
                       ['id', 'name', 'gender', 'age', 'student_id', 'department', 'class_name', 'phone',
                        'dormitory_building', 'dormitory_room']]
                self.student_model.appendRow(row)
            self.status_message_signal.emit(f"学生数据加载成功！共 {len(data)} 条记录。", 5000)
        else:
            self.on_task_error(f"无法加载学生列表: {data}")

    def open_add_dialog(self):
        dialog = StudentEditDialog(self.api_client, parent=self)
        if dialog.exec():
            self.load_data()

    def open_edit_dialog(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return
        selected_row = selected_indexes[0].row()
        data = {'id': int(self.student_model.item(selected_row, 0).text()),
                'name': self.student_model.item(selected_row, 1).text(),
                'gender': self.student_model.item(selected_row, 2).text(),
                'age': self.student_model.item(selected_row, 3).text(),
                'student_id': self.student_model.item(selected_row, 4).text(),
                'department': self.student_model.item(selected_row, 5).text(),
                'class_name': self.student_model.item(selected_row, 6).text(),
                'phone': self.student_model.item(selected_row, 7).text()}
        dialog = StudentEditDialog(self.api_client, data, self)
        if dialog.exec():
            self.load_data()

    def handle_delete(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes: return
        selected_row = selected_indexes[0].row()
        name = self.student_model.item(selected_row, 1).text()
        obj_id = int(self.student_model.item(selected_row, 0).text())
        reply = QMessageBox.question(self, "确认删除", f"您确定要删除学生 **{name}** 吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.task_requested.emit('delete_student', self.on_delete_finished, (obj_id,))

    def on_delete_finished(self, is_success: bool, data: object):
        if is_success:
            self.status_message_signal.emit("删除成功！正在刷新列表...", 3000)
            QTimer.singleShot(0, self.load_data)
        else:
            self.on_task_error(f"删除失败: {data}")

    def set_buttons_enabled(self, enabled: bool):
        self.refresh_button.setEnabled(enabled)
        if self.permissions.get('can_add', False): self.add_student_button.setEnabled(enabled)
        if self.permissions.get('can_edit', False): self.edit_student_button.setEnabled(enabled)
        if self.permissions.get('can_delete', False): self.delete_student_button.setEnabled(enabled)

    def on_task_error(self, error_msg: str):
        QMessageBox.critical(self, "错误", error_msg)