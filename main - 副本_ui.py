# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main - 副本.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QMainWindow,
    QProgressBar, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

from HoverablePolygonItem import ScaleableView
from extendprogressbar import ExtendProgressBar
from hoverableexpandframe import HoverableExpandFrame
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1164, 905)
        MainWindow.setMinimumSize(QSize(940, 560))
        self.styleSheet = QWidget(MainWindow)
        self.styleSheet.setObjectName(u"styleSheet")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet(u"QWidget{\n"
"	color: rgb(0, 0, 0);\n"
"	font: 10pt \"Segoe UI\";\n"
"}")
        self.appMargins = QVBoxLayout(self.styleSheet)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName(u"appMargins")
        self.appMargins.setContentsMargins(10, 10, 10, 10)
        self.frame_5 = QFrame(self.styleSheet)
        self.frame_5.setObjectName(u"frame_5")
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
        icon.addFile(u"icon/\u5173\u95ed.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_7.setIcon(icon)
        self.pushButton_8 = QPushButton(self.frame_5)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(1070, 10, 31, 28))
        icon1 = QIcon()
        icon1.addFile(u"icon/\u6700\u5c0f\u5316.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_8.setIcon(icon1)
        self.label_2 = QLabel(self.frame_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(1, 4, 61, 41))
        self.label_2.setPixmap(QPixmap(u"icon/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_3 = QLabel(self.frame_5)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(71, 5, 701, 41))

        self.appMargins.addWidget(self.frame_5)

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
        self.pushButton.setGeometry(QRect(11, 10, 251, 60))
        self.pushButton.setMaximumSize(QSize(400, 60))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setBold(False)
        font1.setItalic(False)
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"    background-color: rgba(255, 255, 255, 0);\n"
"    border: none;\n"
"    border-radius: 5px;\n"
"    font-size: 50px;\n"
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
        icon2 = QIcon()
        icon2.addFile(u"icon/\u8bbe\u7f6e.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_2.setIcon(icon2)
        self.pushButton_2.setIconSize(QSize(50, 50))
        self.pushButton_2.setCheckable(False)
        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(0, 0, 20000, 2))
        self.label_4.setMinimumSize(QSize(20000, 2))
        self.label_4.setMaximumSize(QSize(20000, 2))
        self.label_4.setStyleSheet(u"QLabel{background-color:rgb(231, 231, 231)}")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(3, 88, 1139, 742))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.frame_4 = HoverableExpandFrame(self.frame_3)
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
        icon3 = QIcon()
        icon3.addFile(u"icon/\u66f4\u6362\u6587\u4ef6.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_3.setIcon(icon3)
        self.pushButton_4 = QPushButton(self.frame_4)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(0, 260, 171, 51))
        icon4 = QIcon()
        icon4.addFile(u"icon/\u5730\u56fe.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_4.setIcon(icon4)
        self.pushButton_5 = QPushButton(self.frame_4)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(0, 440, 171, 41))
        icon5 = QIcon()
        icon5.addFile(u"icon/\u65e5\u671f\u8303\u56f4.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_5.setIcon(icon5)
        self.label = QLabel(self.frame_4)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(0, 0, 2, 2000))
        self.label.setMinimumSize(QSize(0, 2000))
        self.label.setMaximumSize(QSize(2, 16777215))
        self.label.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.graphicsView = ScaleableView(self.frame_3)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(0, -30, 1071, 741))
        self.graphicsView.setStyleSheet(u"QGraphicsView{border: none;}")
        self.verticalLayoutWidget_3 = QWidget(self.frame_3)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 720, 1071, 21))
        self.verticalLayout_4 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_7 = QFrame(self.verticalLayoutWidget_3)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setMaximumSize(QSize(16777215, 0))
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.progressBar = ExtendProgressBar(self.frame_7)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(-3, 0, 1071, 23))
        self.progressBar.setStyleSheet(u"QProgressBar {border: 0px solid grey;\n"
"border-radius: 5px;\n"
"text-align: center;\n"
"background-color: white}")
        self.progressBar.setValue(0)
        self.progressBar.setTextDirection(QProgressBar.BottomToTop)

        self.verticalLayout_4.addWidget(self.frame_7)

        self.verticalLayoutWidget = QWidget(self.frame_3)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 550, 241, 171))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.verticalLayoutWidget)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayoutWidget_2 = QWidget(self.frame_6)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 241, 171))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.graphicsView_2 = ScaleableView(self.verticalLayoutWidget_2)
        self.graphicsView_2.setObjectName(u"graphicsView_2")
        self.graphicsView_2.setStyleSheet(u"QGraphicsView { border: none; }")

        self.verticalLayout_2.addWidget(self.graphicsView_2)


        self.verticalLayout.addWidget(self.frame_6)

        self.graphicsView.raise_()
        self.frame_4.raise_()
        self.verticalLayoutWidget_3.raise_()
        self.verticalLayoutWidget.raise_()

        self.appMargins.addWidget(self.frame)

        MainWindow.setCentralWidget(self.styleSheet)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.label_2.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"VisualData APP-UI for viusal data,based on Python.", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"VisualData", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u9009\u9879", None))
        self.label_4.setText("")
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"    \u66f4\u6362\u6587\u4ef6", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"    \u9009\u62e9\u5730\u70b9", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"    \u9009\u62e9\u65e5\u671f", None))
        self.label.setText("")
    # retranslateUi

