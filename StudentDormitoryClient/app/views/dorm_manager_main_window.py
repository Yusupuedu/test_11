# StudentDorymitoryClient/app/views/dorm_manager_main_window.py

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QThread, QTimer

from ..api_client import ApiClient
from ..workers import ApiWorker
from .student_view_widget import StudentViewWidget


class DormManagerMainWindow(QMainWindow):
    def __init__(self, api_client: ApiClient, user_info: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_info = user_info

        self.thread = None
        self.worker = None
        self.is_busy = False
        self.profile_data = None

        self.setWindowTitle(f"宿管工作台 - 欢迎您, {self.user_info.get('username')}")
        self.setGeometry(100, 100, 1024, 768)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setStatusBar(QStatusBar(self))

        self._create_menus()
        QTimer.singleShot(50, self.load_profile)

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        file_menu.addSeparator()
        exit_action = QAction("退出系统", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        account_menu = menu_bar.addMenu("账户")

    def logout(self):
        self.close()

    def load_profile(self):
        self.start_api_task('get_my_profile', self.on_profile_loaded)

    def on_profile_loaded(self, is_success: bool, data: object):
        if is_success:
            self.profile_data = data
            self.statusBar().showMessage("个人信息加载成功！", 3000)
            self.setup_tabs()
        else:
            QMessageBox.critical(self, "加载失败", f"无法获取您的个人信息，无法继续操作。")

    def setup_tabs(self):
        manager_permissions = {'can_add': False, 'can_edit': True, 'can_delete': False}
        managed_building = self.profile_data.get('managed_building')

        if managed_building:
            filtered_api_client = self.api_client
            filtered_api_client.get_all_students = lambda: self.api_client.get_students_by_building(managed_building)

            self.student_view = StudentViewWidget(filtered_api_client, manager_permissions)
            self.student_view.status_message_signal.connect(self.statusBar().showMessage)
            self.tab_widget.addTab(self.student_view, f"{managed_building} - 学生信息")
        else:
            no_building_widget = QWidget()
            layout = QVBoxLayout(no_building_widget)
            layout.addWidget(QLabel("<h3>您当前未被分配管理的楼栋，请联系管理员。</h3>"))
            self.tab_widget.addTab(no_building_widget, "本楼学生信息")
            return

    def start_api_task(self, func_name, on_finished_slot, *args):
        if self.is_busy: return
        self.is_busy = True
        self.statusBar().showMessage(f"正在执行: {func_name}...", 0)
        self.thread = QThread()
        self.worker = ApiWorker(self.api_client, func_name, *args)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(on_finished_slot)
        self.worker.error.connect(lambda msg: QMessageBox.critical(self, "后台错误", msg))
        self.thread.finished.connect(self.on_task_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def on_task_finished(self):
        if self.worker: self.worker.deleteLater()
        if self.thread: self.thread.deleteLater()
        self.worker = None
        self.thread = None
        self.is_busy = False

    def closeEvent(self, event):
        if self.thread is not None and self.thread.isRunning():
            QMessageBox.warning(self, "操作正在进行", "有后台任务正在运行，请等待其完成后再关闭。")
            event.ignore()
        else:
            event.accept()