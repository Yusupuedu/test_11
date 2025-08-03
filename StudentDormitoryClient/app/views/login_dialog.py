# StudentDormitoryClient/app/views/login_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox
from ..api_client import ApiClient
from .ui_login_dialog import Ui_loginDialog

class LoginDialog(QDialog, Ui_loginDialog):
    def __init__(self, api_client: ApiClient, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setObjectName("loginDialog") # 设置对象名以匹配QSS

        self.api_client = api_client
        self.user_info = None

        # 【核心修改】包含全部五个角色的映射
        self.role_map = {
            "管理员": "admin",
            "宿管": "dorm_manager",
            "学生": "student",
            "教师": "teacher",
            "辅导员": "counselor"
        }

        self.role_comboBox.addItems(self.role_map.keys())
        self._setup_connections()

    def _setup_connections(self):
        self.login_button.clicked.connect(self.handle_login)
        self.exit_button.clicked.connect(self.reject)

    def handle_login(self):
        username = self.user_lineEdit.text().strip()
        password = self.pwd_lineEdit.text()
        selected_role_cn = self.role_comboBox.currentText()
        role_en = self.role_map.get(selected_role_cn)

        if not all([username, password, role_en]):
            QMessageBox.warning(self, "输入错误", "用户名、密码和角色均不能为空！")
            return

        self.login_button.setEnabled(False)
        self.login_button.setText("登录中...")

        result = self.api_client.login(username, password, role_en)

        self.login_button.setEnabled(True)
        self.login_button.setText("登 录")

        if result and 'user' in result:
            self.user_info = result['user']
            # 我们不再在这里显示成功消息，交给主程序处理
            self.accept()
        else:
            QMessageBox.critical(self, "登录失败", "用户名、密码或角色错误，请重试！")