from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys
import pandas as pd
import polars as pl
import geopandas as gpd
import re
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import traceback
from main_ui import Ui_MainWindow
from staticmethod import *
from HoverablePolygonItem import HoverablePolygonItem
from DataTable import DataWidget
from mapView import MapWindow
from workthread import *
from peichartitem import PieChartItem
from options import OptionsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui
        self.expandFlag = 0
        self.expandFlag_ = 0
        self.tableOnShow = False
        self.dragging = False
        self.standard = 420
        self.folder_path = 'exampledata'
        self.geo_data = gpd.read_file('cn.json')[8:12]
        polygons = self.geo_data.geometry.tolist()
        merged_geometry = gpd.GeoSeries(polygons).unary_union
        self.geo_data = gpd.GeoDataFrame(geometry=[merged_geometry], crs=self.geo_data.crs)
        title = "PyDracula - Modern GUI"
        description = "PyDracula APP - Theme with colors based on Dracula for Python."
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(
            "QMainWindow {background-color: #282a36; border: none;}")
        self.buttonFunctionsBind()
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.loadData()
        widgets.frame_6.setAttribute(Qt.WA_TranslucentBackground, True)
        widgets.frame_7.setMaximumHeight(200)
    
    def buttonFunctionsBind(self):
        '''bind functions to buttons'''
        widgets.pushButton.clicked.connect(self.expendStatisticsFrame)
        widgets.pushButton_2.clicked.connect(self.optionsWindow)
        widgets.pushButton_3.clicked.connect(self.changeFile)
        widgets.pushButton_4.clicked.connect(self.changeRegion)
        widgets.pushButton_7.clicked.connect(self.closeButton)
        widgets.pushButton_8.clicked.connect(self.showMinimized)
    # /////////////////////////////////////////////////////////////// 
    # make window moveable
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    # make window moveable
    # ///////////////////////////////////////////////////////////////
    # animation
    def setGraphicsView(self):
        self.statistics_scene = QGraphicsScene()
        self.pie_chart_over = PieChartItem(self.mean_count_data, 'over', start_angle=0, r=224, g=192, b=253, standard=self.standard)
        start_angle = self.pie_chart_over.returnStartAngle()
        self.pie_chart_less = PieChartItem(
                self.mean_count_data, 'less', 
                start_angle=start_angle, r=123, g=122, b=253, 
                standard=self.standard
            )
        self.statistics_scene.addItem(self.pie_chart_over)
        self.statistics_scene.addItem(self.pie_chart_less)
        widgets.graphicsView_2.setScene(self.statistics_scene)
        # try:
        #     self.pie_chart_over = PieChartItem(
        #         self.mean_count_data, 'over', 
        #         start_angle=0, r=224, g=192, b=253, 
        #         standard=self.standard
        #     )
        #     start_angle = self.pie_chart_over.returnStartAngle()
        #     self.pie_chart_less = PieChartItem(
        #         self.mean_count_data, 'less', 
        #         start_angle=start_angle, r=123, g=122, b=253, 
        #         standard=self.standard
        #     )
        # except Exception as e:
        #     print(f"Failed to create PieChartItem: {e}")
        #     return
        # self.statistics_scene.addItem(self.pie_chart_over)
        # self.statistics_scene.addItem(self.pie_chart_less)
        # widgets.graphicsView_2.setScene(self.statistics_scene)
        # item_rect = self.pie_chart_over.boundingRect()
        # widgets.graphicsView_2.resize(int(item_rect.width() + 10),
        #                               int(item_rect.height() + 10))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkHoverStatus)
        self.timer.start(100)


    def checkHoverStatus(self):
        if self.pie_chart_over.hover_on:
            region_indexs = self.pie_chart_over.corsindex
            for region_index in region_indexs:
                self.highlightPolygon(region_index)
        elif self.pie_chart_over.hover_on == False:
            region_indexs = self.pie_chart_over.corsindex
            for region_index in region_indexs:
                self.resetPolygon(region_index)
            self.pie_chart_over.hover_on = None
        
        if self.pie_chart_less.hover_on:
           region_indexs = self.pie_chart_less.corsindex
           for region_index in region_indexs:
               self.highlightPolygon(region_index)
        elif self.pie_chart_less.hover_on == False:
            region_indexs = self.pie_chart_less.corsindex
            for region_index in region_indexs:
                self.resetPolygon(region_index)
            self.pie_chart_less.hover_on = None
    
    def expendStatisticsFrame(self):
        animation_group = QParallelAnimationGroup()
        width_animation = QPropertyAnimation(widgets.frame_6, b"maximumWidth")
        if self.expandFlag % 2 == 0:
            width_animation.setStartValue(0)
            width_animation.setEndValue(400)
        else:
            width_animation.setStartValue(400)
            width_animation.setEndValue(0)
        animation_group.addAnimation(width_animation)
        # animation_group.addAnimation(height_animation)
        animation_group.start()
        animation_group.finished.connect(animation_group.deleteLater)
        self.expandFlag += 1
    
    def expendProgressBarFrame(self, flag):
        animation_group = QParallelAnimationGroup()
        width_animation = QPropertyAnimation(widgets.frame_7, b"maximumHeight")
        if flag % 2 == 0:
            width_animation.setStartValue(0)
            width_animation.setEndValue(200)
        else:
            width_animation.setStartValue(200)
            width_animation.setEndValue(0)
        animation_group.addAnimation(width_animation)
        # animation_group.addAnimation(height_animation)
        animation_group.start()
        animation_group.finished.connect(animation_group.deleteLater)

    # button functions
    def closeButton(self):
        QApplication.quit()
    
    def changeFile(self):
        self.folder_path = QFileDialog.getExistingDirectory(
            self, "选择文件夹", options=QFileDialog.ShowDirsOnly)
        if self.folder_path:
            try:
                data_Window.exit_application()
            except:
                pass
            self.loadData()
    
    def changeRegion(self):
        self.map_window = MapWindow()
        self.map_window.show()
        self.map_window.scence.polygon_finished_signal.connect(self.updateArea)
        self.map_window.update_area_signal.connect(self.updateArea)
    
    def optionsWindow(self):
        self.options_window = OptionsWindow()
        self.options_window.show()


    def updateArea(self, polygon_):
        try:
            data_Window.exit_application()
        except:
            pass
        try:
            self.map_window.exit_application()
        except:
            pass
        self.geo_data = polygon_
        self.loadData()
    # button functions
    # ///////////////////////////////////////////////////////////////    
    def saveUserColumns(self):
        latitude_col = self.line_edits[0].text()
        longitude_col = self.line_edits[1].text()
        time_col = self.line_edits[2].text()
        self.correspondingVariables['time'] = time_col
        self.correspondingVariables['lon'] = longitude_col
        self.correspondingVariables['lat'] = latitude_col
    # ///////////////////////////////////////////////////////////////
    def loadData(self):
        '''read csvs contained in a folder'''
        self.expendProgressBarFrame(flag=1)
        self.loadingDataThread = QThread()
        self.loadingDataWorker = LoadAndExamineDataThread(folder_path=self.folder_path)
        self.loadingDataWorker.moveToThread(self.loadingDataThread)
        self.loadingDataThread.started.connect(self.loadingDataWorker.startWorking)
        self.loadingDataWorker.data_ready_signal.connect(self.createDataViewInstance)
        self.loadingDataWorker.prompt_user_cols_signal.connect(self.promptUserToSetColumns)
        self.loadingDataWorker.prompt_user_format_signal.connect(self.promptUserToSetDateFormat)
        self.loadingDataWorker.auto_set_cols_signal.connect(self.createCorDict)
        self.loadingDataWorker.time_unit_signal.connect(self.setTimeUnit)
        self.loadingDataThread.start()
        self.loadingDataThread.finished.connect(self.threadStop)
    
    def setTimeUnit(self, unit):
        self.time_unit = unit
        self.loadingDataThread.quit()
    
    def threadStop(self):
        self.loadingDataThread.quit()

    def createCorDict(self, dict_):
        self.correspondingVariables = dict_
    
    def promptUserToSetDateFormat(self):
        date_string = self.data.head(10)[self.correspondingVariables['time']].iloc[0]
        self.dialog_dateformat = QDialog()
        layout = QVBoxLayout()
        label = QLabel('convert the follow string to format')
        label_2 = QLabel('eg 2020-01-01 00:00:00 to %Y-%m-%d %H:%M:%S')
        self.line_edit_for_dateformat = QLineEdit()
        self.line_edit_for_dateformat.setText(date_string)
        layout.addWidget(label)
        layout.addWidget(label_2)
        layout.addWidget(self.line_edit_for_dateformat)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.receieveDateFormat)
        layout.addWidget(save_button)
        self.dialog_dateformat.setLayout(layout)
        self.dialog_dateformat.exec_()

    def promptUserToSetColumns(self):
        '''turn to users to set columns corrsponding when failed to set automaticly'''
        self.line_edits= []
        dialog = QDialog()
        layout = QVBoxLayout()

        for col_name in ['latitude', 'longitude', 'time']:
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Enter column name for {col_name}")
            layout.addWidget(line_edit)
            self.line_edits.append(line_edit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.saveUserColumns)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()
    
    def receieveDateFormat(self):
        '''save users' settings'''
        self.customFormat = self.line_edit_for_dateformat.text()  
        self.time_unit = self.customFormat
        self.dialog_dateformat.accept()

    def createDataViewInstance(self, data):
        '''create the table view in the mainwindow'''
        global data_Window
        self.data = data
        main_window_pos = self.pos()
        main_window_size = self.size()
        data_Window = DataWidget(self.data, self.correspondingVariables, self.time_unit)
        new_window_pos = QPoint(main_window_pos.x() + main_window_size.width() - data_Window.width(),
                                main_window_pos.y())
        data_Window.ui.tableView.dataSignal.connect(self.highlightPolygon)
        data_Window.move(new_window_pos)
        data_Window.show()
        self.data_ = self.data.clone()
        self.setMapView()
    
    def setMapView(self):
        '''create the viuasl data map'''
        self.polygons = []
        self.scene = QGraphicsScene()
        try:
            area = self.geo_data['geometry']
        except:
            area = self.geo_data

        self.loadingPolygonsThread = QThread()
        self.loadingPolygonsWorker = MapPolygons(area=area, cellsize_lat=0.5, cellsize_lon=0.5,
                                                  correspondingVariables=self.correspondingVariables,
                                                  data=self.data_, data_view=data_Window.ui.tableView,
                                                  time_unit=self.time_unit, standard=self.standard)
        self.loadingPolygonsWorker.moveToThread(self.loadingPolygonsThread)
        self.loadingPolygonsThread.started.connect(self.loadingPolygonsWorker.polygonsWork)
        self.loadingPolygonsWorker.polygon_finished_signal.connect(self.createPolygonInstance)
        self.loadingPolygonsWorker.polygon_data_ready_signal.connect(self.createPolygonFromData)
        self.loadingPolygonsWorker.polygons_ready_signal.connect(self.finalAdjustMapView, Qt.ConnectionType.QueuedConnection)
        self.loadingPolygonsWorker.mean_count_signal.connect(self.receieveMeanCountData)
        self.loadingPolygonsWorker.progressbar_update_signal.connect(widgets.progressBar.setValue)
        self.loadingPolygonsThread.start()
        self.loadingPolygonsThread.finished.connect(self.threadStop)


    @Slot(dict)
    def createPolygonFromData(self, data_dict):
        qt_polygon = HoverablePolygonItem(
            polygon_points=data_dict['points'],
            index=data_dict['index'],
            df=data_dict['data'],
            datacol='xco2',
            polygon_centriod=data_dict['centriod'],
            data_view=data_Window.ui.tableView,
            cors=self.correspondingVariables,
            time_unit=self.time_unit
        )
        self.scene.addItem(qt_polygon)
        self.polygons.append(qt_polygon)


    def receieveMeanCountData(self, mean_count_data):
        self.mean_count_data = mean_count_data
        self.setGraphicsView()


    def createPolygonInstance(self, qt_polygon):
        self.scene.addItem(qt_polygon)
        self.polygons.append(qt_polygon)


    def finalAdjustMapView(self, concat_data):
        assert QThread.currentThread() == self.thread()
        self.concat_data = concat_data
        widgets.graphicsView.setScene(self.scene)
        widgets.graphicsView.centerOn(self.scene.sceneRect().center())
        widgets.graphicsView.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        widgets.graphicsView.viewport().update()   
        data_Window.header.updataFromOtherClass(pl.DataFrame(self.concat_data))
        self.expendProgressBarFrame(flag=0)
        self.loadingPolygonsThread.quit()
        self.loadingPolygonsThread.wait()


    def highlightPolygon(self, region_index):
        for qt_polygon in self.polygons:
            if qt_polygon.index == int(region_index):
                qt_polygon.highlight()
    
    def resetPolygon(self, region_index):
        for qt_polygon in self.polygons:
            if qt_polygon.index == int(region_index):
                qt_polygon.resetBrush()

        
class MyApp(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sys.excepthook = handle_exception

def handle_exception(exception_type, exception_value, exception_traceback):
    error_message = ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setWindowTitle("Error")
    error_box.setText("An error occurred:")
    error_box.setInformativeText(error_message)
    error_box.exec_()

if __name__ == "__main__":
    app = MyApp.instance()
    if app is None:
        app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
