from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import math
import geopandas as gpd
import re
# from pyhdf.SD import SD
import os
from TilesConnectAndProjection import *
from TilesConnectThread import TilesViewThread
from PIL import Image
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import netCDF4


class OptionsWindow(QWidget):
    update_area_signal = Signal(gpd.GeoDataFrame)
    def __init__(self):
        super().__init__()
        global mapwidgets
        self.expandFlag = 0
        self.ui = Ui_Form()
        mapwidgets = self.ui
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)
        mapwidgets.comboBox.setEditable(True)
        mapwidgets.comboBox_5.setEditable(True)
        mapwidgets.pushButton_7.clicked.connect(self.exit_application)
        mapwidgets.pushButton_8.clicked.connect(self.showMinimized)
        mapwidgets.pushButton.clicked.connect(self.selectFolder)
        mapwidgets.pushButton_3.clicked.connect(self.selectFolder)
        mapwidgets.pushButton_4.clicked.connect(self.selectFolder_openNC)
        mapwidgets.comboBox_3.textActivated.connect(self.searchText)
        mapwidgets.comboBox_6.textActivated.connect(self.addVariable)
        mapwidgets.scrollAreaWidgetContents_2.setStyleSheet(u"QWidget{background-color:transparent}")
        self.scrollAreaWidgetContents_2_height = 0
        mapwidgets.scrollAreaWidgetContents_2.setMinimumHeight(self.scrollAreaWidgetContents_2_height)
        frameLayout = QVBoxLayout()
        mapwidgets.frame_3.setGeometry(0, 0 ,341, self.scrollAreaWidgetContents_2_height)
        mapwidgets.frame_3.setLayout(frameLayout)
        
        self.loadMap()
        # mapwidgets.pushButton_10.clicked.connect()
    
    def loadMap(self):
        self.scene = QGraphicsScene()
        pixmap = QPixmap('sinu_world.jpg')
        self.scene.addPixmap(pixmap)
        mapwidgets.graphicsView.setScene(self.scene)
        mapwidgets.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        try:
            if self.dragging:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    def exit_application(self):
        self.close()
    
    def selectFolder_openNC(self):
        self.folder_path_nc = QFileDialog.getExistingDirectory(
            self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if self.folder_path_nc:
            print("选择的文件夹路径为:", self.folder_path_nc)
        mapwidgets.lineEdit_4.setText(self.folder_path_nc)
        self.nc_paths = self.listFilesFolder(self.folder_path_nc)
        self.getVariablesInfomation()

    def getVariablesInfomation(self):
        file = self.nc_paths[0]
        ds = netCDF4.Dataset(file, 'r')
        variables = list(ds.variables.keys())
        mapwidgets.comboBox_6.addItems(variables)
        mapwidgets.comboBox_3.addItems(variables)
        for var in variables:
            var_name = var
            var_desc = ds[var_name]
            var_name_format = f'<font color="red" size="5">{var_name}</font>'
            mapwidgets.textEdit.append(var_name_format)

            var_desc_format = f'<font color="blue" size="3">{var_desc}</font>'
            mapwidgets.textEdit.append(var_desc_format)

    def searchText(self):
        query = mapwidgets.comboBox_3.currentText()
        
        print(query)
        cursor = mapwidgets.textEdit.textCursor()
        cursor.clearSelection()
        cursor.movePosition(QTextCursor.End)
        found = mapwidgets.textEdit.find(query)
        mapwidgets.comboBox.clearEditText()
        if found:
            print(1234)
            cursor = mapwidgets.textEdit.textCursor()
            cursor.select(QTextCursor.WordUnderCursor)
            format = cursor.charFormat()
            format.setBackground(Qt.yellow)
            cursor.mergeCharFormat(format)
            cursor.movePosition(QTextCursor.StartOfLine)
            mapwidgets.textEdit.setTextCursor(cursor)
            mapwidgets.textEdit.ensureCursorVisible()
        else:
            print(12)
    
    def addVariable(self):
        self.scrollAreaWidgetContents_2_height += 100
        mapwidgets.scrollAreaWidgetContents_2.setMinimumHeight(self.scrollAreaWidgetContents_2_height)
        mapwidgets.frame_3.setGeometry(0, 0 ,341, self.scrollAreaWidgetContents_2_height)
        var = mapwidgets.comboBox_6.currentText()
        widget = QWidget()
        layout = QHBoxLayout(widget)
        label = QLabel(var)
        button = QPushButton("按钮")
        layout.addWidget(label)
        layout.addWidget(button)
        mapwidgets.frame_3.layout().addWidget(widget)
        # button.clicked.connect(self.onButtonClicked)
    
    
    def selectFolder(self):
        self.folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if self.folder_path:
            print("选择的文件夹路径为:", self.folder_path)
        mapwidgets.lineEdit_3.setText(self.folder_path)
        mapwidgets.lineEdit.setText(self.folder_path)
        self.file_paths = self.listFilesFolder(self.folder_path)
        self.retrieveProjection()
        self.showTiles()
    
    def showTiles(self):
        self.tilesThread = QThread()
        self.tilesWorker = TilesViewThread(paths=self.file_paths)
        self.tilesWorker.moveToThread(self.tilesThread)
        self.tilesThread.started.connect(self.tilesWorker.startWorking)
        self.tilesThread.start()
        self.tilesWorker.request_draw_signal.connect(self.drawPolygons)
        self.tilesThread.finished.connect(self.threadStop)
    
    def drawPolygons(self, polygon_data):
        """ Draw the polygons based on the received data. """
        image_path = 'sinu_world.jpg'
        image = np.array(Image.open(image_path))  
        plt.imshow(image)  
        ax = plt.gca()

        for (x, y, width, height) in polygon_data:
            rect = patches.Rectangle((x, y), width, height,
                                     linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)

        # plt.axis('off')
        # plt.tight_layout()
        # plt.draw()
        # plt_image = np.frombuffer(plt.gcf().canvas.tostring_rgb(), dtype=np.uint8)
        # plt_image = plt_image.reshape(plt.gcf().canvas.get_width_height()[::-1] + (3,))
        # self.updateGraphicsView(plt_image)
        plt.axis('off')
        plt.savefig('draw.png')
        plt.tight_layout()
        self.updateGraphicsView()
    
    def threadStop(self):
        self.tilesThread.quit()
   
    def updateGraphicsView(self):
        self.scene.clear()
        pixmap = QPixmap('draw.png')
        self.scene.addPixmap(pixmap)
        self.scene.update()
        mapwidgets.graphicsView.setScene(self.scene)
        # mapwidgets.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        # height, width, channel = image.shape
        # bytes_per_line = channel * width
        # q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        # pixmap = QPixmap.fromImage(q_image)

        # self.scene.clear()
        # self.scene.addPixmap(pixmap)
        # mapwidgets.graphicsView.setScene(self.scene)
    
    def performTilesConnect(self):
        files = self.file_paths
        lonmin = float(mapwidgets.lineEdit_8.text())
        lonmax = float(mapwidgets.lineEdit_9.text())
        latmin = float(mapwidgets.lineEdit_10.text())
        latmax = float(mapwidgets.lineEdit_11.text())
        output_path = mapwidgets.lineEdit_7.text()
    
    def listFilesFolder(self, folder_path) -> list:
        '''return files list'''
        file_paths = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    
    def retrieveProjection(self):
        '''open h5 file,transform variable to array,
        retrieve projection and transform infomation'''
        LR_filepath = self.file_paths[0]
        hdf = SD(LR_filepath)
        metadata = hdf.__getattr__('StructMetadata.0')
        ul_pt = [float(x) for x in re.findall(
            r'UpperLeftPointMtrs=\((.*)\)', metadata)[0].split(',')]
        lr_pt = [float(x) for x in re.findall(
            r'LowerRightMtrs=\((.*)\)', metadata)[0].split(',')]
        col = int(re.findall(r'XDim=(.*?)\n', metadata)[0])
        row = int(re.findall(r'YDim=(.*?)\n', metadata)[0])
        x_res = (lr_pt[0] - ul_pt[0]) / col
        y_res = (ul_pt[1] - lr_pt[1]) / row
        projection_param = [float(_param) for _param in re.findall(
            r'ProjParams=\((.*?)\)', metadata)[0].split(',')]
        self.proj = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} " \
            "+y_0={:0.4f} ".format('sinu',
                                projection_param[0],
                                projection_param[4],
                                projection_param[5],
                                projection_param[6],
                                projection_param[7])
        self.transform = [ul_pt[0], x_res, 0, ul_pt[1], 0, -y_res]
        
        self.variable_names = self.retrieveVariablesNames(hdf)
        self.showInfomation(metadata)
        self.fixResampleComboBox()
        hdf.end()
        
    
    def retrieveVariablesNames(self, hdf):
        datasets = hdf.datasets()
        self.variable_names = []
        for dataset in datasets:
            self.variable_names.append(dataset)
        return self.variable_names
    
    def fixResampleComboBox(self):
        mapwidgets.comboBox.addItems(self.variable_names)
        mapwidgets.comboBox_5.addItems(self.variable_names)
        completer = QCompleter(self.variable_names, mapwidgets.comboBox)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        mapwidgets.comboBox.setCompleter(completer)
        mapwidgets.comboBox_5.setCompleter(completer)
   
    def showInfomation(self, string):
        mapwidgets.plainTextEdit.appendPlainText(string)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1246, 916)
        Form.setStyleSheet(u"QWidget{\n"
"	color: rgb(0, 0, 0);\n"
"	font: 10pt \"Segoe UI\";\n"
"}\n"
"QFrame{background-color:white;\n"
"}\n"
"QPushButton{background-color:transparent}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}")
        self.frame_5 = QFrame(Form)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setGeometry(QRect(0, 0, 1141, 50))
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
        icon.addFile(u"icon/\u5173\u95ed.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_7.setIcon(icon)
        self.pushButton_8 = QPushButton(self.frame_5)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(1070, 10, 31, 28))
        icon1 = QIcon()
        icon1.addFile(u"icon/\u6700\u5c0f\u5316.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_8.setIcon(icon1)
        self.label_2 = QLabel(self.frame_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(1, 4, 61, 41))
        self.label_2.setPixmap(QPixmap(u"icon/icon.png"))
        self.label_2.setScaledContents(True)
        self.label_3 = QLabel(self.frame_5)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(71, 5, 701, 41))
        self.scrollArea = QScrollArea(Form)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 50, 1141, 861))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, -572, 1118, 2000))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(1000, 2000))
        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, -10, 1141, 1391))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(0, 0, 161, 1331))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayoutWidget = QWidget(self.frame_2)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 160, 1243))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 400))
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_5)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 400))
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label_4)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 400))
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.label_7 = QLabel(self.frame)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(0, 408, 1121, 2))
        self.label_7.setMaximumSize(QSize(16777215, 2))
        self.label_7.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.layoutWidget_4 = QWidget(self.frame)
        self.layoutWidget_4.setObjectName(u"layoutWidget_4")
        self.layoutWidget_4.setGeometry(QRect(180, 760, 311, 31))
        self.horizontalLayout_2 = QHBoxLayout(self.layoutWidget_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.layoutWidget_4)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_2.addWidget(self.label_11)

        self.lineEdit_2 = QLineEdit(self.layoutWidget_4)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.pushButton_2 = QPushButton(self.layoutWidget_4)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMaximumSize(QSize(40, 16777215))
        icon2 = QIcon()
        icon2.addFile(u"icon/\u6587\u4ef6\u5939.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon2)

        self.horizontalLayout_2.addWidget(self.pushButton_2)

        self.plainTextEdit = QPlainTextEdit(self.frame)
        self.plainTextEdit.setObjectName(u"plainTextEdit")
        self.plainTextEdit.setGeometry(QRect(510, 420, 601, 371))
        self.plainTextEdit.setStyleSheet(u"QPlainTextEdit{ border: none; }")
        self.label_14 = QLabel(self.frame)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(0, 824, 2400, 2))
        self.label_14.setMaximumSize(QSize(16777215, 2))
        self.label_14.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.label_15 = QLabel(self.frame)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(490, 410, 2, 415))
        self.label_15.setMaximumSize(QSize(2, 16777215))
        self.label_15.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.label_38 = QLabel(self.frame)
        self.label_38.setObjectName(u"label_38")
        self.label_38.setGeometry(QRect(620, -10, 2, 420))
        self.label_38.setMaximumSize(QSize(2, 16777215))
        self.label_38.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.graphicsView = QGraphicsView(self.frame)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(630, 10, 481, 391))
        self.graphicsView.setStyleSheet(u"QGraphicsView{ border: none; }")
        self.pushButton_10 = QPushButton(self.frame)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setGeometry(QRect(450, 240, 93, 28))
        self.pushButton_11 = QPushButton(self.frame)
        self.pushButton_11.setObjectName(u"pushButton_11")
        self.pushButton_11.setGeometry(QRect(390, 790, 93, 30))
        self.layoutWidget = QWidget(self.frame)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(181, 430, 309, 306))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout.addWidget(self.label_8)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton = QPushButton(self.layoutWidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMaximumSize(QSize(40, 16777215))
        self.pushButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_13 = QLabel(self.layoutWidget)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_4.addWidget(self.label_13)

        self.comboBox_2 = QComboBox(self.layoutWidget)
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setStyleSheet(u"QComboBox{background-color:transparent}")

        self.horizontalLayout_4.addWidget(self.comboBox_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_12 = QLabel(self.layoutWidget)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_3.addWidget(self.label_12)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setStyleSheet(u"QComboBox{background-color:transparent}")
        self.comboBox.setEditable(True)

        self.horizontalLayout_3.addWidget(self.comboBox)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout_3.addLayout(self.verticalLayout_2)

        self.tableWidget = QTableWidget(self.layoutWidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setStyleSheet(u"QTableWidget{ border: none; }")

        self.verticalLayout_3.addWidget(self.tableWidget)

        self.layoutWidget1 = QWidget(self.frame)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(200, 70, 341, 109))
        self.verticalLayout_8 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_16 = QLabel(self.layoutWidget1)
        self.label_16.setObjectName(u"label_16")

        self.horizontalLayout_5.addWidget(self.label_16)

        self.lineEdit_3 = QLineEdit(self.layoutWidget1)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.horizontalLayout_5.addWidget(self.lineEdit_3)

        self.pushButton_3 = QPushButton(self.layoutWidget1)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMaximumSize(QSize(40, 16777215))
        self.pushButton_3.setIcon(icon2)

        self.horizontalLayout_5.addWidget(self.pushButton_3)


        self.verticalLayout_7.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_31 = QLabel(self.layoutWidget1)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(85, 0))

        self.horizontalLayout_11.addWidget(self.label_31)

        self.lineEdit_7 = QLineEdit(self.layoutWidget1)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.horizontalLayout_11.addWidget(self.lineEdit_7)

        self.pushButton_9 = QPushButton(self.layoutWidget1)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setMaximumSize(QSize(40, 16777215))
        self.pushButton_9.setIcon(icon2)

        self.horizontalLayout_11.addWidget(self.pushButton_9)


        self.verticalLayout_7.addLayout(self.horizontalLayout_11)


        self.verticalLayout_8.addLayout(self.verticalLayout_7)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_32 = QLabel(self.layoutWidget1)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_12.addWidget(self.label_32)

        self.comboBox_5 = QComboBox(self.layoutWidget1)
        self.comboBox_5.setObjectName(u"comboBox_5")
        self.comboBox_5.setStyleSheet(u"QComboBox{background-color:transparent}")
        self.comboBox_5.setEditable(True)

        self.horizontalLayout_12.addWidget(self.comboBox_5)


        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.label_39 = QLabel(self.frame)
        self.label_39.setObjectName(u"label_39")
        self.label_39.setGeometry(QRect(160, 0, 2, 1600))
        self.label_39.setMaximumSize(QSize(2, 16777215))
        self.label_39.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.label_18 = QLabel(self.frame)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setGeometry(QRect(1, 1240, 1121, 2))
        self.label_18.setMaximumSize(QSize(16777215, 2))
        self.label_18.setStyleSheet(u"QLabel{background-color:rgb(186, 186, 214)}")
        self.layoutWidget_2 = QWidget(self.frame)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(170, 840, 341, 109))
        self.verticalLayout_9 = QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_17 = QLabel(self.layoutWidget_2)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_6.addWidget(self.label_17)

        self.lineEdit_4 = QLineEdit(self.layoutWidget_2)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.horizontalLayout_6.addWidget(self.lineEdit_4)

        self.pushButton_4 = QPushButton(self.layoutWidget_2)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setMaximumSize(QSize(40, 16777215))
        self.pushButton_4.setIcon(icon2)

        self.horizontalLayout_6.addWidget(self.pushButton_4)


        self.verticalLayout_10.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_33 = QLabel(self.layoutWidget_2)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setMinimumSize(QSize(85, 0))

        self.horizontalLayout_13.addWidget(self.label_33)

        self.lineEdit_8 = QLineEdit(self.layoutWidget_2)
        self.lineEdit_8.setObjectName(u"lineEdit_8")

        self.horizontalLayout_13.addWidget(self.lineEdit_8)

        self.pushButton_12 = QPushButton(self.layoutWidget_2)
        self.pushButton_12.setObjectName(u"pushButton_12")
        self.pushButton_12.setMaximumSize(QSize(40, 16777215))
        self.pushButton_12.setIcon(icon2)

        self.horizontalLayout_13.addWidget(self.pushButton_12)


        self.verticalLayout_10.addLayout(self.horizontalLayout_13)


        self.verticalLayout_9.addLayout(self.verticalLayout_10)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_34 = QLabel(self.layoutWidget_2)
        self.label_34.setObjectName(u"label_34")

        self.horizontalLayout_14.addWidget(self.label_34)

        self.comboBox_6 = QComboBox(self.layoutWidget_2)
        self.comboBox_6.setObjectName(u"comboBox_6")
        self.comboBox_6.setStyleSheet(u"QComboBox{background-color:transparent}")
        self.comboBox_6.setEditable(True)

        self.horizontalLayout_14.addWidget(self.comboBox_6)


        self.verticalLayout_9.addLayout(self.horizontalLayout_14)

        self.comboBox_3 = QComboBox(self.frame)
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setGeometry(QRect(630, 840, 481, 22))
        self.comboBox_3.setStyleSheet(u"QComboBox{background-color:transparent}")
        self.textEdit = QTextEdit(self.frame)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(630, 860, 481, 371))
        self.scrollArea_2 = QScrollArea(self.frame)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setGeometry(QRect(170, 960, 341, 261))
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 318, 1000))
        self.scrollAreaWidgetContents_2.setMinimumSize(QSize(0, 1000))
        self.frame_3 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(0, 0, 341, 1001))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.label_2.setText("")
        self.label_3.setText(QCoreApplication.translate("Form", u"VisualData APP-UI for viusal data,based on Python.", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\u74e6\u7247\u62fc\u63a5", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u91cd\u6295\u5f71", None))
        self.label.setText(QCoreApplication.translate("Form", u"NC\u6587\u4ef6\u8bfb\u53d6", None))
        self.label_7.setText("")
        self.label_11.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u8def\u5f84", None))
        self.pushButton_2.setText("")
        self.label_14.setText("")
        self.label_15.setText("")
        self.label_38.setText("")
        self.pushButton_10.setText(QCoreApplication.translate("Form", u"\u6267\u884c", None))
        self.pushButton_11.setText(QCoreApplication.translate("Form", u"\u6267\u884c", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\u6587\u4ef6\u5939\u8def\u5f84", None))
        self.pushButton.setText("")
        self.label_13.setText(QCoreApplication.translate("Form", u"\u76ee\u6807\u6295\u5f71", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("Form", u"EPSG4326", None))

        self.label_12.setText(QCoreApplication.translate("Form", u"\u53d8\u91cf\u9009\u62e9", None))
        self.label_16.setText(QCoreApplication.translate("Form", u"\u6587\u4ef6\u5939\u8def\u5f84", None))
        self.pushButton_3.setText("")
        self.label_31.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u8def\u5f84", None))
        self.pushButton_9.setText("")
        self.label_32.setText(QCoreApplication.translate("Form", u"\u53d8\u91cf\u9009\u62e9", None))
        self.label_39.setText("")
        self.label_18.setText("")
        self.label_17.setText(QCoreApplication.translate("Form", u"\u6587\u4ef6\u5939\u8def\u5f84", None))
        self.pushButton_4.setText("")
        self.label_33.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u8def\u5f84", None))
        self.pushButton_12.setText("")
        self.label_34.setText(QCoreApplication.translate("Form", u"\u53d8\u91cf\u9009\u62e9", None))
    # retranslateUi





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = OptionsWindow()
    window.show()
    sys.exit(app.exec_())