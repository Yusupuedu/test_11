# StudentDormitoryClient/app/views/add_student_dialog.py

from PyQt6.QtWidgets import QDialog, QMessageBox
from ..api_client import ApiClient
# 注意这里的导入方式，以避免命名冲突
from .ui_add_student_dialog import Ui_Dialog as Ui_AddStudentDialog


class AddStudentDialog(QDialog, Ui_AddStudentDialog):
    """
    添加新学生对话框的逻辑。
    """

    def __init__(self, api_client: ApiClient, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.api_client = api_client
        self.setWindowTitle("添加新学生")

        self.save_button.clicked.connect(self.handle_save)
        self.cancel_button.clicked.connect(self.reject)

    def handle_save(self):
        """处理保存按钮点击事件。"""
        name = self.name_lineEdit.text().strip()
        student_id = self.student_id_lineEdit.text().strip()
        dorm_room = self.dorm_room_lineEdit.text().strip()

        if not all([name, student_id]):
            QMessageBox.warning(self, "输入错误", "姓名和学号不能为空！")
            return

        # 禁用按钮并更改文本以提供反馈
        self.save_button.setEnabled(False)
        self.save_button.setText("保存中...")

        result = self.api_client.add_student(name, student_id, dorm_room)

        self.save_button.setEnabled(True)
        self.save_button.setText("保存")

        # 后端成功创建的标志是返回的字典中包含 'id' 键
        if result and 'id' in result:
            QMessageBox.information(self, "成功", f"学生 '{name}' 添加成功！")
            self.accept()
        else:
            # 如果失败，显示后端返回的具体错误信息
            error_msg = result.get('error', '发生未知错误') if result else '网络连接或服务器无响应'
            QMessageBox.critical(self, "添加失败", f"无法添加学生。\n错误: {error_msg}")