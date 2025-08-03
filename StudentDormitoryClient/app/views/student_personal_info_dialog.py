# StudentDormitoryClient/app/views/student_personal_info_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QTabWidget, QWidget

class StudentPersonalInfoDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.profile_data = None  # 用于存储从API获取的数据

        self.setWindowTitle("学生个人信息中心")
        self.setMinimumWidth(400)

        # --- 创建UI布局 ---
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.profile_tab = QWidget()
        self.password_tab = QWidget()

        self.tab_widget.addTab(self.profile_tab, "我的资料")
        self.tab_widget.addTab(self.password_tab, "修改密码")

        self._create_profile_tab()
        self._create_password_tab()

        # --- 启动时加载数据 ---
        self.load_profile()

    def _create_profile_tab(self):
        """创建“我的资料”标签页的内容"""
        layout = QVBoxLayout(self.profile_tab)
        self.profile_form_layout = QFormLayout()

        # 电话号码是唯一可编辑的字段
        self.phone_edit = QLineEdit()
        self.profile_form_layout.addRow("<b>联系电话:</b>", self.phone_edit)

        layout.addLayout(self.profile_form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        update_button = QPushButton("更新信息")
        update_button.clicked.connect(self.handle_profile_update)
        button_layout.addWidget(update_button)
        layout.addLayout(button_layout)

    def _create_password_tab(self):
        """创建“修改密码”标签页的内容"""
        layout = QFormLayout(self.password_tab)
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("旧密码:", self.old_password_edit)
        layout.addRow("新密码:", self.new_password_edit)
        layout.addRow("确认新密码:", self.confirm_password_edit)

        change_button = QPushButton("确认修改密码")
        change_button.clicked.connect(self.handle_password_change)
        layout.addRow("", change_button)

    def load_profile(self):
        """从API加载学生个人信息"""
        # 这是一个同步调用，因为对话框是模态的，可以接受短暂的阻塞
        result = self.api_client.get_my_profile()
        if 'error' in result:
            QMessageBox.critical(self, "错误", f"无法加载个人信息: {result['error']}")
            self.phone_edit.setEnabled(False) # 加载失败则禁用编辑
            return

        self.profile_data = result
        self.populate_profile_ui()

    def populate_profile_ui(self):
        """用加载好的数据填充UI"""
        # 清除旧的只读字段
        while self.profile_form_layout.rowCount() > 1:
            self.profile_form_layout.removeRow(0)

        # 学生需要显示的只读字段
        readonly_fields = [
            ("姓名", "name"), ("性别", "gender"), ("年龄", "age"),
            ("学号", "student_id"), ("院系", "department"), ("班级", "class_name")
        ]

        for label_text, key in reversed(readonly_fields):
            if key in self.profile_data and self.profile_data.get(key):
                field_label = QLabel(str(self.profile_data.get(key)))
                self.profile_form_layout.insertRow(0, f"<b>{label_text}:</b>", field_label)

        self.phone_edit.setText(self.profile_data.get('phone', ''))

    def handle_profile_update(self):
        """处理更新电话号码的逻辑"""
        new_phone = self.phone_edit.text().strip()
        result = self.api_client.update_my_profile({"phone": new_phone})

        if 'error' in result:
            QMessageBox.critical(self, "更新失败", result['error'])
        else:
            QMessageBox.information(self, "成功", "个人信息更新成功！")
            self.profile_data = result # 更新本地缓存的数据
            self.populate_profile_ui() # 刷新UI

    def handle_password_change(self):
        """处理修改密码的逻辑"""
        old_pass = self.old_password_edit.text()
        new_pass = self.new_password_edit.text()
        confirm_pass = self.confirm_password_edit.text()

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "错误", "两次输入的新密码不一致！")
            return
        if not new_pass:
            QMessageBox.warning(self, "错误", "新密码不能为空！")
            return

        result = self.api_client.change_my_password(old_pass, new_pass)
        if 'error' in result:
            QMessageBox.critical(self, "修改失败", result['error'])
        else:
            QMessageBox.information(self, "成功", "密码修改成功！请使用新密码重新登录。")
            self.accept() # 关闭对话框，并返回“成功”状态