# StudentDormitoryClient/app/views/dorm_building_edit_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout

class DormBuildingEditDialog(QDialog):
    def __init__(self, api_client, building_data: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.data = building_data
        self.is_edit_mode = building_data is not None

        self._init_ui()
        self._setup_connections()

        if self.is_edit_mode:
            self.setWindowTitle("修改宿舍楼信息")
            self._populate_data()
        else:
            self.setWindowTitle("添加新宿舍楼")

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.total_rooms_edit = QLineEdit()
        self.available_rooms_edit = QLineEdit()

        form_layout.addRow("楼栋名称:", self.name_edit)
        form_layout.addRow("总房间数:", self.total_rooms_edit)
        form_layout.addRow("可用房间数:", self.available_rooms_edit)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def _setup_connections(self):
        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def _populate_data(self):
        self.name_edit.setText(self.data.get('building_name', ''))
        self.total_rooms_edit.setText(str(self.data.get('total_rooms', '')))
        self.available_rooms_edit.setText(str(self.data.get('available_rooms', '')))

    def handle_save(self):
        building_name = self.name_edit.text().strip()
        if not building_name:
            QMessageBox.warning(self, "输入错误", "楼栋名称不能为空！")
            return

        payload = {"building_name": building_name}
        if self.total_rooms_edit.text().strip().isdigit():
            payload["total_rooms"] = int(self.total_rooms_edit.text().strip())
        if self.available_rooms_edit.text().strip().isdigit():
            payload["available_rooms"] = int(self.available_rooms_edit.text().strip())

        if self.is_edit_mode:
            result = self.api_client.update_building(self.data['id'], payload)
        else:
            result = self.api_client.add_building(payload)

        if result and 'id' in result:
            action = "更新" if self.is_edit_mode else "添加"
            QMessageBox.information(self, "成功", f"宿舍楼 '{building_name}' {action}成功！")
            self.accept()
        else:
            error_msg = result.get('error', '未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "操作失败", f"无法保存宿舍楼信息。\n错误: {error_msg}")