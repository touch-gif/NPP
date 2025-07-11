# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main - ����zKOwFR.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from HoverablePolygonItem import ScaleableView

import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1404, 874)
        MainWindow.setMinimumSize(QSize(940, 560))
        self.styleSheet = QWidget(MainWindow)
        self.styleSheet.setObjectName(u"styleSheet")
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet(u"QWidget{\n"
"	color: rgb(171, 171, 171);\n"
"	font: 10pt \"Segoe UI\";\n"
"}")
        self.appMargins = QVBoxLayout(self.styleSheet)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName(u"appMargins")
        self.appMargins.setContentsMargins(10, 10, 10, 10)
        self.frame = QFrame(self.styleSheet)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QFrame{background-color:white}")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(3, 1, 1139, 80))
        self.frame_2.setMaximumSize(QSize(16777215, 80))
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.pushButton = QPushButton(self.frame_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(11, 10, 111, 60))
        self.pushButton.setMaximumSize(QSize(120, 60))
        font1 = QFont()
        font1.setFamily(u"Segoe UI")
        font1.setBold(False)
        font1.setItalic(False)
        font1.setWeight(50)
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: none;\n"
"    border-radius: 5px;\n"
"    font-size: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    color: rgb(0, 0, 0);\n"
"}")
        self.pushButton_2 = QPushButton(self.frame_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(669, 16, 461, 51))
        self.pushButton_2.setMaximumSize(QSize(16777215, 60))
        self.pushButton_2.setStyleSheet(u"QPushButton {\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: none;\n"
"    border-radius: 5px;\n"
"	font-size: 20px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}")
        icon = QIcon()
        icon.addFile(u"icon/\u8bbe\u7f6e.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setIconSize(QSize(50, 50))
        self.pushButton_2.setCheckable(False)
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(3, 88, 1139, 742))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setGeometry(QRect(1070, -10, 141, 761))
        self.frame_4.setStyleSheet(u"QPushButton{background-color:transparent}\n"
"QFrame {\n"
"    border: 0px solid black;\n"
"    transition: margin-left 0.5s;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}\n"
"")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.pushButton_3 = QPushButton(self.frame_4)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(0, 71, 171, 41))
        icon1 = QIcon()
        icon1.addFile(u"icon/\u66f4\u6362\u6587\u4ef6.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon1)
        self.pushButton_4 = QPushButton(self.frame_4)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(0, 260, 171, 51))
        icon2 = QIcon()
        icon2.addFile(u"icon/\u5730\u56fe.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_4.setIcon(icon2)
        self.pushButton_5 = QPushButton(self.frame_4)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(0, 440, 171, 41))
        icon3 = QIcon()
        icon3.addFile(u"icon/\u65e5\u671f\u8303\u56f4.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_5.setIcon(icon3)
        self.pushButton_6 = QPushButton(self.frame_4)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(10, 630, 98, 32))
        self.label = QLabel(self.frame_4)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 0, 2, 751))
        self.label.setMaximumSize(QSize(2, 16777215))
        self.label.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.graphicsView = ScaleableView(self.frame_3)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(0, 0, 1071, 741))
        self.graphicsView.setStyleSheet(u"QGraphicsView{border: none;}")

        self.appMargins.addWidget(self.frame)

        MainWindow.setCentralWidget(self.styleSheet)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"VisualData", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u9009\u9879", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"    \u66f4\u6362\u6587\u4ef6", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"    \u9009\u62e9\u5730\u70b9", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"    \u9009\u62e9\u65e5\u671f", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.label.setText("")
    # retranslateUi

