# StudentDormitoryClient/app/views/edit_student_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox
from ..api_client import ApiClient
from .ui_edit_student_dialog import Ui_Dialog as Ui_EditStudentDialog


class EditStudentDialog(QDialog, Ui_EditStudentDialog):
    """
    修改学生信息对话框的逻辑。
    """

    def __init__(self, api_client: ApiClient, student_data: dict, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.api_client = api_client
        self.student_data = student_data  # 保存传入的当前学生数据
        self.setWindowTitle("修改学生信息")

        self._populate_data()
        self._setup_connections()

    def _populate_data(self):
        """用传入的学生数据填充输入框。"""
        self.name_lineEdit.setText(self.student_data.get('name', ''))
        self.student_id_lineEdit.setText(self.student_data.get('student_id', ''))
        self.dorm_room_lineEdit.setText(self.student_data.get('dorm_room', ''))

    def _setup_connections(self):
        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def handle_save(self):
        """处理保存按钮点击事件。"""
        updated_data = {
            'name': self.name_lineEdit.text().strip(),
            'student_id': self.student_id_lineEdit.text().strip(),
            'dorm_room': self.dorm_room_lineEdit.text().strip()
        }

        if not all([updated_data['name'], updated_data['student_id']]):
            QMessageBox.warning(self, "输入错误", "姓名和学号不能为空！")
            return

        student_id_to_update = self.student_data['id']

        self.save_button.setEnabled(False)
        self.save_button.setText("保存中...")

        result = self.api_client.update_student(student_id_to_update, updated_data)

        self.save_button.setEnabled(True)
        self.save_button.setText("保存")

        if result and 'id' in result:
            QMessageBox.information(self, "成功", "学生信息更新成功！")
            self.accept()
        else:
            error_msg = result.get('error', '发生未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "更新失败", f"无法更新学生信息。\n错误: {error_msg}")
