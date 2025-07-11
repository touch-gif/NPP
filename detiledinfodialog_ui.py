# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'detiledinfodialog.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class Ui_detiledInfoDialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(956, 747)
        Dialog.setStyleSheet(u"QDialog {\n"
"                    border: 2px solid gray;\n"
"                    background-color: white; /* Set a background color */\n"
"                }")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(9, 9, 941, 731))
        self.frame.setStyleSheet(u"QFrame {\n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"QWidget{\n"
"	color: rgb(0, 0, 0);\n"
"	font: 10pt \"Segoe UI\";\n"
"}\n"
"")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setGeometry(QRect(0, 0, 941, 50))
        self.frame_5.setMaximumSize(QSize(16777215, 50))
        self.frame_5.setStyleSheet(u"QPushButton{background-color:transparent}\n"
"QFrame {\n"
"	background-color:white;\n"
"    border: 0px solid black;\n"
"    transition: margin-left 0.5s;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}\n"
"")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.pushButton_7 = QPushButton(self.frame_5)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setGeometry(QRect(1100, 10, 31, 28))
        icon = QIcon()
        icon.addFile(u"../VisualEnvironment/icon/\u5173\u95ed.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_7.setIcon(icon)
        self.pushButton_8 = QPushButton(self.frame_5)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(1070, 10, 31, 28))
        icon1 = QIcon()
        icon1.addFile(u"../VisualEnvironment/icon/\u6700\u5c0f\u5316.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_8.setIcon(icon1)
        self.label_2 = QLabel(self.frame_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(1, 4, 61, 41))
        self.label_2.setPixmap(QPixmap(u"../VisualEnvironment/icon/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_3 = QLabel(self.frame_5)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(71, 5, 701, 41))
        self.pushButton_10 = QPushButton(self.frame_5)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setGeometry(QRect(900, 10, 31, 28))
        self.pushButton_10.setIcon(icon)
        self.pushButton_9 = QPushButton(self.frame_5)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setGeometry(QRect(870, 10, 31, 28))
        self.pushButton_9.setIcon(icon1)
        self.scrollArea = QScrollArea(self.frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 50, 941, 681))
        self.scrollArea.setStyleSheet(u"QFrame{background-color:rgb(255, 255, 255);}")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 939, 679))
        self.frame_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(0, 0, 941, 681))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.tableView = QTableView(self.frame_2)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setGeometry(QRect(5, 1, 941, 681))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.label_2.setText("")
        self.label_3.setText(QCoreApplication.translate("Dialog", u"VisualData APP-UI for viusal data,based on Python.", None))
        self.pushButton_10.setText("")
        self.pushButton_9.setText("")
    # retranslateUi