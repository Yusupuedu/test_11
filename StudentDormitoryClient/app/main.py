# StudentDormitoryClient/app/main.py

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from .api_client import ApiClient
from .views.login_dialog import LoginDialog
from .views.admin_main_window import AdminMainWindow
from .views.student_main_window import StudentMainWindow
from .views.dorm_manager_main_window import DormManagerMainWindow
from .views.teacher_main_window import TeacherMainWindow
from .views.counselor_main_window import CounselorMainWindow


def run():
    app = QApplication(sys.argv)

    try:
        with open("app/style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("警告: 未找到样式表文件 'app/style.qss'。")

    while True:
        api_client = ApiClient()
        login_dialog = LoginDialog(api_client=api_client)

        main_window = None

        if login_dialog.exec():
            user_info = login_dialog.user_info
            role = user_info.get('role')

            if role == 'admin':
                main_window = AdminMainWindow(api_client, user_info)
            elif role == 'student':
                main_window = StudentMainWindow(api_client, user_info)
            elif role == 'dorm_manager':
                main_window = DormManagerMainWindow(api_client, user_info)
            elif role == 'teacher':
                main_window = TeacherMainWindow(api_client, user_info)
            elif role == 'counselor':
                main_window = CounselorMainWindow(api_client, user_info)
            else:
                QMessageBox.critical(None, "角色错误", f"未知的用户角色 '{role}'。")
                sys.exit(1)

            main_window.show()
            app.exec()
        else:
            break