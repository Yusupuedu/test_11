# StudentDormitoryClient/app/views/dorm_room_edit_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox
from ..api_client import ApiClient

class DormRoomEditDialog(QDialog):
    def __init__(self, api_client: ApiClient, room_data: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.data = room_data
        self.is_edit_mode = room_data is not None

        self.all_buildings = [] # 用于存储所有楼栋名称

        self._init_ui()
        self._setup_connections()
        self.load_building_data_for_selector() # 启动时加载楼栋数据

        if self.is_edit_mode:
            self.setWindowTitle("修改房间信息")
            self._populate_data()
        else:
            self.setWindowTitle("添加新房间")

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.building_selector = QComboBox()
        self.room_number_edit = QLineEdit()
        self.capacity_edit = QLineEdit()
        self.gender_type_selector = QComboBox()
        self.gender_type_selector.addItems(["男", "女"])

        form_layout.addRow("所属楼栋:", self.building_selector)
        form_layout.addRow("房间号:", self.room_number_edit)
        form_layout.addRow("容量(床位数):", self.capacity_edit)
        form_layout.addRow("性别类型:", self.gender_type_selector)

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

    def load_building_data_for_selector(self):
        """加载楼栋列表到下拉框"""
        result = self.api_client.get_buildings()
        if isinstance(result, list):
            self.all_buildings = [b['building_name'] for b in result]
            self.building_selector.addItems(self.all_buildings)
        else:
            QMessageBox.critical(self, "错误", "无法加载宿舍楼列表，请稍后再试。")

    def _populate_data(self):
        """在编辑模式下，用现有数据填充表单"""
        self.room_number_edit.setText(self.data.get('room_number', ''))
        self.capacity_edit.setText(str(self.data.get('capacity', '')))

        building_name = self.data.get('building_name', '')
        if building_name in self.all_buildings:
            self.building_selector.setCurrentText(building_name)

        gender_type = self.data.get('gender_type', '')
        if gender_type in ["男", "女"]:
            self.gender_type_selector.setCurrentText(gender_type)

    def handle_save(self):
        capacity_text = self.capacity_edit.text().strip()
        if not all([self.room_number_edit.text().strip(), capacity_text, self.building_selector.currentText()]):
            QMessageBox.warning(self, "输入错误", "房间号、容量和所属楼栋均不能为空！")
            return
        if not capacity_text.isdigit():
            QMessageBox.warning(self, "输入错误", "容量必须是一个数字！")
            return

        payload = {
            "building_name": self.building_selector.currentText(),
            "room_number": self.room_number_edit.text().strip(),
            "capacity": int(capacity_text),
            "gender_type": self.gender_type_selector.currentText()
        }

        if self.is_edit_mode:
            result = self.api_client.update_room(self.data['id'], payload)
        else:
            result = self.api_client.add_room(payload)

        if result and 'id' in result:
            action = "更新" if self.is_edit_mode else "添加"
            QMessageBox.information(self, "成功", f"房间 '{payload['building_name']}-{payload['room_number']}' {action}成功！")
            self.accept()
        else:
            error_msg = result.get('error', '未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "操作失败", f"无法保存房间信息。\n错误: {error_msg}")