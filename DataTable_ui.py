from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class DataTableView(QTableView):
    dataSignal = Signal(object)
    def __init__(self, *args, **kwargs) -> None:
        super(DataTableView, self).__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableviewmenu = QMenu(self)
        self.action1 = QAction('copy', self)
        self.action2 = QAction('Loc Grid Data', self)
        self.tableviewmenu.addAction(self.action1)
        self.tableviewmenu.addAction(self.action2)
        self.action1.triggered.connect(self.action_copy)
        self.action2.triggered.connect(self.action_loc_grid_data)
        self.customContextMenuRequested.connect(self.show_context_menu)
    def show_context_menu(self, pos):
        self.tableviewmenu.exec_(self.mapToGlobal(pos))
    def action_copy(self):
        clipboard = QApplication.clipboard()
        selected_data = []
        selected_indexes = self.selectedIndexes()        
        for index in selected_indexes:
            selected_data.append(index.data())
        clipboard.setText('\n'.join(selected_data))
    
    def action_loc_grid_data(self):
        selected_indexes = self.selectedIndexes()
        proxy_model = self.model()
        index_right_column = None
        for col in range(proxy_model.columnCount()):
            header_data = proxy_model.headerData(col, Qt.Horizontal)
            if header_data == 'rigion_index':
                index_right_column = col
                break
        
        if index_right_column is None:
            print("Column 'index_right' not found.")
            return
        selected_index = selected_indexes[0]
        row = selected_index.row()
        index_right_index = proxy_model.index(row, index_right_column)
        region_index = index_right_index.data()
        print(region_index)
        self.dataSignal.emit(region_index)
                


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(387, 268)
        Dialog.setStyleSheet(u"QDialog {\n"
"                    border: 2px solid gray;\n"
"                    background-color: white; /* Set a background color */\n"
"                }")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 10, 361, 251))
        self.frame.setStyleSheet(u"QFrame {\n"
"    background-color: rgb(33, 37, 43);\n"
"}\n"
"QLabel{ color: rgb(255, 255, 255); }\n"
"QLineEdit {\n"
"	background-color: rgb(33, 37, 43);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	padding-left: 10px;\n"
"	selection-color: rgb(255, 255, 255);\n"
"	selection-background-color: rgb(255, 121, 198);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"QPushButton {\n"
"	background-color: rgb(40, 44, 52);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"QPushButton:pressed {\n"
"	background-color: rgb(189, 147, 249);\n"
"}")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.frame)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(30, 20, 311, 151))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"QLabel{ color: rgb(255, 255, 255); }")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setStyleSheet(u"QLineEdit {\n"
"	background-color: rgb(33, 37, 43);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	padding-left: 10px;\n"
"	selection-color: rgb(255, 255, 255);\n"
"	selection-background-color: rgb(255, 121, 198);\n"
"}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}")

        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)

        self.layoutWidget1 = QWidget(self.frame)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(150, 190, 195, 30))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton = QPushButton(self.layoutWidget1)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.layoutWidget1)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Start", None))
        self.lineEdit.setText("")
        self.label_2.setText(QCoreApplication.translate("Dialog", u"End", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"confirm", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"cancel", None))
    # retranslateUi


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(983, 917)
        Form.setAutoFillBackground(False)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 0, 981, 901))
        self.frame.setStyleSheet(u"QFrame {\n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"QWidget{\n"
"	color: rgb(0, 0, 0);\n"
"	font: 10pt \"Segoe UI\";\n"
"}\n"
"")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setLineWidth(0)
        self.verticalLayoutWidget_3 = QWidget(self.frame)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 981, 771))
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.frame)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setGeometry(QRect(0, 0, 981, 901))
        self.scrollArea_2.setStyleSheet(u"QScrollArea{\n"
"    border:0px solid #838486;  \n"
"\n"
"}\n"
"")
        self.scrollArea_2.setLineWidth(0)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 981, 901))
        self.tableView = DataTableView(self.scrollAreaWidgetContents_3)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(0, 50, 981, 851))
        self.tableView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setShowGrid(True)
        self.contentTopBg = QFrame(self.scrollAreaWidgetContents_3)
        self.contentTopBg.setObjectName(u"contentTopBg")
        self.contentTopBg.setGeometry(QRect(0, 0, 991, 50))
        self.contentTopBg.setMinimumSize(QSize(0, 50))
        self.contentTopBg.setMaximumSize(QSize(16777215, 50))
        self.contentTopBg.setStyleSheet(u"QFrame{background-color:white;}")
        self.contentTopBg.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout = QHBoxLayout(self.contentTopBg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.rightButtons = QFrame(self.contentTopBg)
        self.rightButtons.setObjectName(u"rightButtons")
        self.rightButtons.setMinimumSize(QSize(0, 28))
        self.rightButtons.setStyleSheet(u"QPushButton{background-color:transparent}\n"
"QFrame {\n"
"	background-color:white;\n"
"    border: 0px solid black;\n"
"    transition: margin-left 0.5s;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}\n"
"")
        self.rightButtons.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_2 = QHBoxLayout(self.rightButtons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.leftBox = QFrame(self.rightButtons)
        self.leftBox.setObjectName(u"leftBox")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy)
        self.leftBox.setStyleSheet(u"")
        self.leftBox.setFrameShape(QFrame.NoFrame)
        self.progressBar = QProgressBar(self.leftBox)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(805, 9, 120, 31))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"                border: 0px solid grey;\n"
"                border-radius: 5px;\n"
"                text-align: center;\n"
"                background-color: rgb(255, 255, 255);\n"
"            }\n"
"QProgressBar::chunk {\n"
"                background-color: rgb(189, 147, 249);\n"
"            }")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.label_2 = QLabel(self.leftBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, 0, 61, 41))
        self.label_2.setPixmap(QPixmap(u"../VisualEnvironment/icon/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_3 = QLabel(self.leftBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(80, 10, 701, 41))

        self.horizontalLayout_2.addWidget(self.leftBox)

        self.minimizeAppBtn = QPushButton(self.rightButtons)
        self.minimizeAppBtn.setObjectName(u"minimizeAppBtn")
        self.minimizeAppBtn.setMinimumSize(QSize(28, 28))
        self.minimizeAppBtn.setMaximumSize(QSize(28, 28))
        self.minimizeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon = QIcon()
        icon.addFile(u"../VisualEnvironment/icon/\u6700\u5c0f\u5316.png", QSize(), QIcon.Normal, QIcon.Off)
        self.minimizeAppBtn.setIcon(icon)
        self.minimizeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.minimizeAppBtn)

        self.closeAppBtn = QPushButton(self.rightButtons)
        self.closeAppBtn.setObjectName(u"closeAppBtn")
        self.closeAppBtn.setMinimumSize(QSize(28, 28))
        self.closeAppBtn.setMaximumSize(QSize(28, 28))
        self.closeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u"../VisualEnvironment/icon/\u5173\u95ed.png", QSize(), QIcon.Normal, QIcon.Off)
        self.closeAppBtn.setIcon(icon1)
        self.closeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.closeAppBtn)


        self.horizontalLayout.addWidget(self.rightButtons)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
#if QT_CONFIG(whatsthis)
        Form.setWhatsThis(QCoreApplication.translate("Form", u"<html><head/><body><p><br/></p></body></html>", None))
#endif // QT_CONFIG(whatsthis)
        self.label_2.setText("")
        self.label_3.setText(QCoreApplication.translate("Form", u"VisualData APP-UI 编号: S202410255160.", None))
#if QT_CONFIG(tooltip)
        self.minimizeAppBtn.setToolTip(QCoreApplication.translate("Form", u"Minimize", None))
#endif // QT_CONFIG(tooltip)
        self.minimizeAppBtn.setText("")
#if QT_CONFIG(tooltip)
        self.closeAppBtn.setToolTip(QCoreApplication.translate("Form", u"Close", None))
#endif // QT_CONFIG(tooltip)
        self.closeAppBtn.setText("")
    # retranslateUi
