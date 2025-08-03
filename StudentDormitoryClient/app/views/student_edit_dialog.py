# StudentDorymitoryClient/app/views/student_edit_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
import random
import string

from ..api_client import ApiClient

class StudentEditDialog(QDialog):
    def __init__(self, api_client: ApiClient, student_data: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.data = student_data
        self.is_edit_mode = student_data is not None

        self._init_ui()
        self._setup_connections()

        if self.is_edit_mode:
            self.setWindowTitle("修改学生信息")
            self._populate_data()
        else:
            self.setWindowTitle("添加新学生")

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.gender_edit = QLineEdit()
        self.age_edit = QLineEdit()
        self.student_id_edit = QLineEdit()
        self.department_edit = QLineEdit()
        self.class_name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()

        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("性别:", self.gender_edit)
        form_layout.addRow("年龄:", self.age_edit)
        form_layout.addRow("学号:", self.student_id_edit)
        form_layout.addRow("院系:", self.department_edit)
        form_layout.addRow("班级:", self.class_name_edit)
        form_layout.addRow("联系方式:", self.phone_edit)

        if not self.is_edit_mode:
            form_layout.addRow("登录用户名:", self.username_edit)
            form_layout.addRow("初始密码:", self.password_edit)
            self.generate_password_button = QPushButton("生成随机密码")
            form_layout.addRow("", self.generate_password_button)

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
        if not self.is_edit_mode:
            self.generate_password_button.clicked.connect(self.generate_random_password)

    def _populate_data(self):
        self.name_edit.setText(self.data.get('name', ''))
        self.gender_edit.setText(self.data.get('gender', ''))
        self.age_edit.setText(str(self.data.get('age', '')))
        self.student_id_edit.setText(self.data.get('student_id', ''))
        self.department_edit.setText(self.data.get('department', ''))
        self.class_name_edit.setText(self.data.get('class_name', ''))
        self.phone_edit.setText(self.data.get('phone', ''))

    def generate_random_password(self):
        chars = string.ascii_letters + string.digits
        self.password_edit.setText(''.join(random.choice(chars) for _ in range(8)))

    def handle_save(self):
        payload = {
            "name": self.name_edit.text().strip(),
            "gender": self.gender_edit.text().strip(),
            "age": int(self.age_edit.text()) if self.age_edit.text().isdigit() else None,
            "student_id": self.student_id_edit.text().strip(),
            "department": self.department_edit.text().strip(),
            "class_name": self.class_name_edit.text().strip(),
            "phone": self.phone_edit.text().strip()
        }

        if not payload["name"] or not payload["student_id"]:
            QMessageBox.warning(self, "输入错误", "姓名和学号不能为空！")
            return

        if self.is_edit_mode:
            result = self.api_client.update_student(self.data['id'], payload)
        else:
            payload['username'] = self.username_edit.text().strip()
            payload['password'] = self.password_edit.text()
            if not payload['username'] or not payload['password']:
                QMessageBox.warning(self, "输入错误", "登录用户名和初始密码不能为空！")
                return
            result = self.api_client.add_student(payload)

        if result and 'id' in result:
            action = "更新" if self.is_edit_mode else "添加"
            QMessageBox.information(self, "成功", f"学生 '{payload['name']}' {action}成功！")
            self.accept()
        else:
            error_msg = result.get('error', '未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "操作失败", f"无法保存学生信息。\n错误: {error_msg}")