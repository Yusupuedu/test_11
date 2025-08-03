# StudentDormitoryClient/app/views/ui_login_dialog.py

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_loginDialog(object):
    def setupUi(self, loginDialog):
        loginDialog.setObjectName("loginDialog")
        loginDialog.resize(450, 350)
        loginDialog.setWindowTitle("欢迎使用宿舍管理系统")

        self.verticalLayout = QtWidgets.QVBoxLayout(loginDialog)
        self.verticalLayout.setContentsMargins(30, 20, 30, 20)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")

        # 大标题
        self.titleLabel = QtWidgets.QLabel(parent=loginDialog)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setText("欢迎使用宿舍管理系统")
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)

        # 表单布局
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setVerticalSpacing(15)
        self.formLayout.setObjectName("formLayout")

        # 用户名
        self.label_user = QtWidgets.QLabel(parent=loginDialog)
        self.label_user.setText("用户名:")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_user)
        self.user_lineEdit = QtWidgets.QLineEdit(parent=loginDialog)
        self.user_lineEdit.setObjectName("user_lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.user_lineEdit)

        # 密码
        self.label_pwd = QtWidgets.QLabel(parent=loginDialog)
        self.label_pwd.setText("密  码:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_pwd)
        self.pwd_lineEdit = QtWidgets.QLineEdit(parent=loginDialog)
        self.pwd_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pwd_lineEdit.setObjectName("pwd_lineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.pwd_lineEdit)

        # 角色
        self.label_role = QtWidgets.QLabel(parent=loginDialog)
        self.label_role.setText("选择角色:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.label_role)
        self.role_comboBox = QtWidgets.QComboBox(parent=loginDialog)
        self.role_comboBox.setObjectName("role_comboBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.role_comboBox)

        self.verticalLayout.addLayout(self.formLayout)

        # 按钮布局
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.login_button = QtWidgets.QPushButton(parent=loginDialog)
        self.login_button.setText("登 录")
        self.login_button.setObjectName("login_button")
        self.horizontalLayout.addWidget(self.login_button)
        self.exit_button = QtWidgets.QPushButton(parent=loginDialog)
        self.exit_button.setText("退 出")
        self.exit_button.setObjectName("exit_button")
        self.horizontalLayout.addWidget(self.exit_button)
        self.verticalLayout.addLayout(self.horizontalLayout)

        QtCore.QMetaObject.connectSlotsByName(loginDialog)