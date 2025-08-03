# StudentDorymitoryClient/app/views/student_main_window.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLabel, QStatusBar, QApplication, \
    QTabWidget, QTableView, QHeaderView, QMessageBox
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem
from PyQt6.QtCore import QThread, QTimer

from ..api_client import ApiClient
from ..workers import ApiWorker
# 【核心】导入新的、专为学生设计的个人信息对话框
from .student_personal_info_dialog import StudentPersonalInfoDialog


class StudentMainWindow(QMainWindow):
    def __init__(self, api_client: ApiClient, user_info: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_info = user_info

        self.thread = None
        self.worker = None
        self.is_busy = False
        self.profile_data = None
        self.roommates_data_loaded = False
        self.initial_data_loaded = False

        self.setWindowTitle(f"学生个人中心 - 欢迎您, {self.user_info.get('username')}")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.setStatusBar(QStatusBar(self))

        self._create_menus()

        self.profile_tab = QWidget()
        self.dorm_tab = QWidget()
        self.tab_widget.addTab(self.profile_tab, "我的资料")
        self.tab_widget.addTab(self.dorm_tab, "我的宿舍")

        self._init_profile_ui()
        self._init_dorm_ui()

        self.tab_widget.currentChanged.connect(self.handle_tab_change)

        QTimer.singleShot(50, self.load_all_data)

    def _create_menus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        file_menu.addSeparator()
        exit_action = QAction("退出系统", self)
        exit_action.triggered.connect(self.close)

        account_menu = menu_bar.addMenu("账户")
        self.personal_info_action = QAction("个人信息中心", self)
        self.personal_info_action.triggered.connect(self.open_personal_info)
        account_menu.addAction(self.personal_info_action)
        self.personal_info_action.setEnabled(False)

    def logout(self):
        self.close()

    def open_personal_info(self):
        """安全地打开个人信息对话框"""
        # 【核心】在打开对话框前，检查主窗口是否正忙
        if self.is_busy:
            QMessageBox.warning(self, "请稍候", "正在加载数据，请稍后再试。")
            return

        dialog = StudentPersonalInfoDialog(self.api_client, self)
        # .exec()会阻塞主窗口，直到对话框关闭，这是安全的
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 如果密码被修改，则关闭主窗口以强制重新登录
            self.logout()

    def _init_profile_ui(self):
        layout = QVBoxLayout(self.profile_tab)
        self.profile_form_layout = QFormLayout()
        layout.addLayout(self.profile_form_layout)
        layout.addStretch()

    def _init_dorm_ui(self):
        layout = QVBoxLayout(self.dorm_tab)
        self.dorm_info_label = QLabel("<b>宿舍信息:</b> 点击此标签页以加载...")
        self.roommates_table = QTableView()
        self.roommates_model = QStandardItemModel()
        self.roommates_table.setModel(self.roommates_model)
        self.roommates_model.setHorizontalHeaderLabels(['姓名', '院系', '班级', '联系方式'])
        self.roommates_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.dorm_info_label)
        layout.addWidget(QLabel("<b>我的室友:</b>"))
        layout.addWidget(self.roommates_table)

    def handle_tab_change(self, index):
        if index == 1 and not self.roommates_data_loaded:
            self.load_roommate_data()

    def load_all_data(self):
        self.start_api_task('get_my_profile', self.on_profile_loaded)

    def on_profile_loaded(self, is_success: bool, data: object):
        if is_success:
            self.profile_data = data
            self.update_profile_ui(data)
            self.personal_info_action.setEnabled(True)
            self.update_dorm_ui(data, [])
        else:
            QMessageBox.critical(self, "错误", f"无法加载个人信息: {data}")

    def load_roommate_data(self):
        self.start_api_task('get_my_roommates', self.on_roommates_loaded)

    def on_roommates_loaded(self, is_success: bool, data: object):
        if is_success:
            self.roommates_data_loaded = True
            self.update_roommates_table(data)
            self.statusBar().showMessage("室友信息加载完毕！", 3000)
        else:
            QMessageBox.critical(self, "错误", f"无法加载室友信息: {data}")

    def update_profile_ui(self, data):
        while self.profile_form_layout.rowCount() > 0: self.profile_form_layout.removeRow(0)
        fields = {"姓名": "name", "性别": "gender", "年龄": "age", "学号": "student_id", "院系": "department",
                  "班级": "class_name", "联系方式": "phone"}
        for label_text, key in fields.items():
            self.profile_form_layout.addRow(f"<b>{label_text}:</b>", QLabel(str(data.get(key, 'N/A'))))

    def update_dorm_ui(self, profile_data, roommates_data):
        building = profile_data.get('dormitory_building')
        room = profile_data.get('dormitory_room')
        if building and room:
            self.dorm_info_label.setText(f"<b>宿舍信息:</b> {building} - {room}号房间")
        else:
            self.dorm_info_label.setText("<b>宿舍信息:</b> 您当前暂未分配宿舍")
        self.update_roommates_table(roommates_data)

    def update_roommates_table(self, roommates_data):
        self.roommates_model.removeRows(0, self.roommates_model.rowCount())
        for roommate in roommates_data:
            row = [QStandardItem(roommate.get(k, '')) for k in ['name', 'department', 'class_name', 'phone']]
            self.roommates_model.appendRow(row)

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
            return
        event.accept()