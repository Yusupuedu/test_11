# StudentDormitoryClient/app/views/admin_main_window.py

from PyQt6.QtWidgets import QMainWindow, QStatusBar, QApplication, QWidget, QHBoxLayout, QListWidget, QStackedWidget, \
    QListWidgetItem, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, QThread

from ..api_client import ApiClient
from ..workers import ApiWorker

from .student_view_widget import StudentViewWidget
from .teacher_view_widget import TeacherViewWidget
from .counselor_management_widget import CounselorViewWidget
from .dorm_manager_view_widget import DormManagerViewWidget
from .dorm_building_view_widget import DormBuildingViewWidget
from .dorm_room_view_widget import DormRoomViewWidget
from .dorm_allocation_widget import DormAllocationWidget


class AdminMainWindow(QMainWindow):
    def __init__(self, api_client: ApiClient, user_info: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_info = user_info

        self.thread = None
        self.worker = None
        self.is_busy = False

        self.setWindowTitle(f"管理员后台 - 欢迎您, {self.user_info.get('username')}")
        self.setGeometry(100, 100, 1280, 800)

        self._init_ui()
        self._create_menus()

        if self.stacked_widget.count() > 0:
            self.handle_tab_change(0)

    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)
        self.setStatusBar(QStatusBar(self))

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setStyleSheet("""
            QListWidget { background-color: #e8f4fd; border: none; font-size: 12pt; padding-top: 20px; }
            QListWidget::item { padding: 15px; border-bottom: 1px solid #d0e0f0; }
            QListWidget::item:hover { background-color: #d0e8f8; }
            QListWidget::item:selected { background-color: #4a90e2; color: white; font-weight: bold; }
        """)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.stacked_widget)

        self.add_module("宿舍分配管理", "assets/icons/users.svg", DormAllocationWidget)
        self.add_module("学生信息管理", "assets/icons/user.svg", StudentViewWidget)
        self.add_module("教师信息管理", "assets/icons/briefcase.svg", TeacherViewWidget)
        self.add_module("辅导员信息管理", "assets/icons/smile.svg", CounselorViewWidget)
        self.add_module("宿管信息管理", "assets/icons/key.svg", DormManagerViewWidget)
        self.add_module("宿舍楼信息管理", "assets/icons/home.svg", DormBuildingViewWidget)
        self.add_module("宿舍房间管理", "assets/icons/grid.svg", DormRoomViewWidget)

        self.nav_list.currentRowChanged.connect(self.handle_tab_change)

    def handle_tab_change(self, index):
        self.stacked_widget.setCurrentIndex(index)
        current_widget = self.stacked_widget.widget(index)
        if current_widget and hasattr(current_widget, 'initial_data_loaded') and not current_widget.initial_data_loaded:
            if hasattr(current_widget, 'load_data'):
                current_widget.load_data()
            elif hasattr(current_widget, 'refresh_all_data'):
                current_widget.refresh_all_data()

    def add_module(self, name, icon_path, widget_class):
        permissions = {'can_add': True, 'can_edit': True, 'can_delete': True}
        module_widget = widget_class(self.api_client, permissions, self)

        if hasattr(module_widget, 'task_requested'):
            module_widget.task_requested.connect(self.handle_task_request)
        if hasattr(module_widget, 'status_message_signal'):
            module_widget.status_message_signal.connect(self.statusBar().showMessage)

        self.stacked_widget.addWidget(module_widget)
        item = QListWidgetItem(name)
        try:
            item.setIcon(QIcon(icon_path))
            item.setSizeHint(QSize(40, 40))
        except Exception as e:
            print(f"加载图标失败: {icon_path} - {e}")
        self.nav_list.addItem(item)

    def handle_task_request(self, func_name, on_finished_slot, args):
        if self.is_busy:
            QMessageBox.warning(self, "请稍候", "另一个后台操作正在进行中。")
            return
        self.is_busy = True
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'set_buttons_enabled'):
            current_widget.set_buttons_enabled(False)
        self.statusBar().showMessage(f"正在执行: {func_name}...", 0)
        self.thread = QThread()
        self.worker = ApiWorker(self.api_client, func_name, *args)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(on_finished_slot)
        if hasattr(current_widget, 'on_task_error'):
            self.worker.error.connect(current_widget.on_task_error)
        self.thread.finished.connect(self.on_task_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def on_task_finished(self):
        if self.worker: self.worker.deleteLater()
        if self.thread: self.thread.deleteLater()
        self.worker = None
        self.thread = None
        self.is_busy = False
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'set_buttons_enabled'):
            current_widget.set_buttons_enabled(True)

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

        # 【核心修改】保留菜单占位符，但暂时不添加任何功能
        account_menu = menu_bar.addMenu("账户")
        # personal_info_action = QAction("个人信息中心", self)
        # personal_info_action.triggered.connect(self.open_personal_info)
        # account_menu.addAction(personal_info_action)

    def logout(self):
        self.close()

    def closeEvent(self, event):
        if self.is_busy:
            QMessageBox.warning(self, "操作正在进行", "有后台任务正在运行，请等待其完成后再关闭。")
            event.ignore()
        else:
            event.accept()