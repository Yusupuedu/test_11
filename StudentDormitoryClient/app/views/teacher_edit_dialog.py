# StudentDormitoryClient/app/views/teacher_edit_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
import random
import string

from ..api_client import ApiClient

class TeacherEditDialog(QDialog):
    def __init__(self, api_client: ApiClient, teacher_data: dict = None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.teacher_data = teacher_data
        self.is_edit_mode = teacher_data is not None # 如果传入了数据，则为编辑模式

        self._init_ui()
        self._setup_connections()

        if self.is_edit_mode:
            self.setWindowTitle("修改教师信息")
            self._populate_data()
        else:
            self.setWindowTitle("添加新教师")

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- 创建所有输入框 ---
        self.name_edit = QLineEdit()
        self.gender_edit = QLineEdit()
        self.age_edit = QLineEdit()
        self.teacher_id_edit = QLineEdit()
        self.department_edit = QLineEdit()
        self.title_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()

        form_layout.addRow("姓名:", self.name_edit)
        form_layout.addRow("性别:", self.gender_edit)
        form_layout.addRow("年龄:", self.age_edit)
        form_layout.addRow("教工号:", self.teacher_id_edit)
        form_layout.addRow("院系:", self.department_edit)
        form_layout.addRow("职称:", self.title_edit)
        form_layout.addRow("联系方式:", self.phone_edit)

        # 只有在添加模式下，才显示用户名和密码的设置
        if not self.is_edit_mode:
            self.username_label = QLabel("登录用户名:")
            self.password_label = QLabel("初始密码:")
            form_layout.addRow(self.username_label, self.username_edit)
            form_layout.addRow(self.password_label, self.password_edit)

        layout.addLayout(form_layout)

        # --- 密码生成按钮 ---
        if not self.is_edit_mode:
            password_layout = QHBoxLayout()
            password_layout.addStretch()
            self.generate_password_button = QPushButton("生成随机密码")
            password_layout.addWidget(self.generate_password_button)
            layout.addLayout(password_layout)

        # --- 保存和取消按钮 ---
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
        """在编辑模式下，用现有数据填充表单"""
        self.name_edit.setText(self.teacher_data.get('name', ''))
        self.gender_edit.setText(self.teacher_data.get('gender', ''))
        self.age_edit.setText(str(self.teacher_data.get('age', '')))
        self.teacher_id_edit.setText(self.teacher_data.get('teacher_id', ''))
        self.department_edit.setText(self.teacher_data.get('department', ''))
        self.title_edit.setText(self.teacher_data.get('title', ''))
        self.phone_edit.setText(self.teacher_data.get('phone', ''))

    def generate_random_password(self):
        """生成一个8位的随机密码"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(8))
        self.password_edit.setText(password)

    def handle_save(self):
        """处理保存逻辑"""
        # 1. 收集表单数据
        payload = {
            "name": self.name_edit.text().strip(),
            "gender": self.gender_edit.text().strip(),
            "age": int(self.age_edit.text()) if self.age_edit.text().isdigit() else None,
            "teacher_id": self.teacher_id_edit.text().strip(),
            "department": self.department_edit.text().strip(),
            "title": self.title_edit.text().strip(),
            "phone": self.phone_edit.text().strip()
        }

        # 2. 校验核心数据
        if not payload["name"] or not payload["teacher_id"]:
            QMessageBox.warning(self, "输入错误", "姓名和教工号不能为空！")
            return

        # 3. 根据模式调用不同的API方法
        if self.is_edit_mode:
            # --- 编辑模式 ---
            result = self.api_client.update_teacher(self.teacher_data['id'], payload)
        else:
            # --- 添加模式 ---
            # 额外添加用户名和密码
            payload['username'] = self.username_edit.text().strip()
            payload['password'] = self.password_edit.text()
            if not payload['username'] or not payload['password']:
                QMessageBox.warning(self, "输入错误", "登录用户名和初始密码不能为空！")
                return
            result = self.api_client.add_teacher(payload)

        # 4. 处理返回结果
        if result and 'id' in result:
            action = "更新" if self.is_edit_mode else "添加"
            QMessageBox.information(self, "成功", f"教师 '{payload['name']}' {action}成功！")
            self.accept()
        else:
            error_msg = result.get('error', '未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "操作失败", f"无法保存教师信息。\n错误: {error_msg}")