from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import math
import geopandas as gpd
from staticmethod import maptoScence, scencetoMap
from shapely.geometry import mapping, Polygon, Point, box


class MapWindow(QWidget):
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
        
        self.animation = QPropertyAnimation(self.ui.frame_2, b"geometry")
        self.animation.setDuration(900)
        self.origingeometry = QRect(4,220,21,341)
        self.new_rect = QRect(-200,220,21,341)
        
        self.scence = MyScene()
        mapwidgets.graphicsView.setScene(self.scence)

        mapwidgets.pushButton_5.setEnabled(False)
        mapwidgets.pushButton_5.setVisible(False)
        mapwidgets.comboBox.editTextChanged.connect(self.locGraphics)

        mapwidgets.comboBox_4.editTextChanged.connect(self.provinceChangeActivate)
        mapwidgets.pushButton.clicked.connect(self.expendSearchFrame)
        mapwidgets.pushButton_2.clicked.connect(self.startRect)
        mapwidgets.pushButton_3.clicked.connect(self.startPolygon)
        mapwidgets.pushButton_7.clicked.connect(self.exit_application)
        mapwidgets.pushButton_8.clicked.connect(self.showMinimized)
        mapwidgets.pushButton_4.clicked.connect(self.hideBoxFrame)
        mapwidgets.pushButton_5.clicked.connect(self.showBoxFrame)
        mapwidgets.pushButton_6.clicked.connect(self.updateArea)
        self.setComboBox()
        # self.loadMap()
    def setComboBox(self):
        cuntrys = world_dataset['name']
        completer = QCompleter(cuntrys, mapwidgets.comboBox)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        mapwidgets.comboBox.setCompleter(completer)
    
    def locGraphics(self):
        text = mapwidgets.comboBox.currentText()
        if text == '中国':
            provinces = dataset['name']
            completer = QCompleter(provinces)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            mapwidgets.comboBox_4.setCompleter(completer)
        location = world_dataset.loc[world_dataset['name']
                                     == text]['geometry'].centroid
        if not location.empty:
            lon_ = location.x
            lat_ = location.y
            lon = lon_.iloc[0]
            lat = lat_.iloc[0]
            x_pos, y_pos = maptoScence(lon, lat)
            print(x_pos, y_pos)
            view_center_c = mapwidgets.graphicsView.mapToScene(
                mapwidgets.graphicsView.viewport().rect().center())
            offset_x = x_pos - view_center_c.x()
            offset_y = y_pos - view_center_c.y()

            view_center_t = QPointF(
                view_center_c.x() + offset_x, view_center_c.y() + offset_y)
            self.animateMove(view_center_c, view_center_t)
            mapwidgets.graphicsView.centerOn(view_center_t)
        else:
            return
    def updateArea(self):
        text = mapwidgets.comboBox_4.currentText()
        self.close()
        if text != '':
            gdf= dataset.loc[dataset['name']
                                        == text]
        self.update_area_signal.emit(gdf)
    def provinceChangeActivate(self):
        text = mapwidgets.comboBox_4.currentText()

        if text != '':
            location = dataset.loc[dataset['name']
                                        == text]['geometry'].centroid
        else:
            location = None
            return
        if not location.empty:
            lon_ = location.x
            lat_ = location.y
            lon = lon_.iloc[0]
            lat = lat_.iloc[0]
            x_pos, y_pos = maptoScence(lon, lat)
            view_center_c = mapwidgets.graphicsView.mapToScene(
                mapwidgets.graphicsView.viewport().rect().center())
            offset_x = x_pos - view_center_c.x()
            offset_y = y_pos - view_center_c.y()

            view_center_t = QPointF(
                view_center_c.x() + offset_x, view_center_c.y() + offset_y)
            self.animateMove(view_center_c, view_center_t)
            mapwidgets.graphicsView.centerOn(view_center_t)
            boundary = dataset.loc[dataset['name'] == text]['geometry'].bounds
            x_min, y_min = maptoScence(boundary.minx.iloc[0], boundary.miny.iloc[0])
            x_max, y_max = maptoScence(boundary.maxx.iloc[0], boundary.maxy.iloc[0])
            mapwidgets.graphicsView.autoScaleView(x_min, y_min, x_max, y_max)
            path = self.scence.addMultipolygonPath(
                    name=text, ds=dataset)
            self.scence.addBoundary(path=path, pen=QPen(Qt.blue, 1, Qt.DashLine))
        else:
            return
    
    def animateMove(self, current_center, target_center, duration=200, steps=1000):
        if steps <= 0:
            return
        x_diff = target_center.x() - current_center.x()
        y_diff = target_center.y() - current_center.y()
        move_diff = math.sqrt(x_diff**2 + y_diff**2)
        move_step = QPointF(x_diff / steps, y_diff / steps)
        if move_diff < 0.01:
            return
        new_center = current_center + move_step
        mapwidgets.graphicsView.centerOn(new_center)
        QTimer.singleShot(
            duration // steps, lambda: self.animateMove(new_center, target_center, duration, steps - 1))
    def expendSearchFrame(self):
        self.expandFlag += 1
        animation_group = QParallelAnimationGroup()

        width_animation = QPropertyAnimation(mapwidgets.frame_4, b"maximumWidth")
        # height_animation = QPropertyAnimation(mapwidgets.frame_4, b"maximumHeight")
        button = mapwidgets.pushButton
        current_color = button.palette().button().color()
        print(f"Current color: {current_color}")
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

    def startRect(self):
        button = mapwidgets.pushButton_2
        current_color = button.palette().button().color()
        if current_color == QColor('transparent'):
            mapwidgets.graphicsView.Rectable = True
            button.setStyleSheet('background-color: rgba(121, 115, 127, 55)')
        elif current_color == QColor(121, 115, 127, 55):
            mapwidgets.graphicsView.Rectable = False
            button.setStyleSheet('background-color: transparent')
    
    def startPolygon(self):
        button = mapwidgets.pushButton_3
        current_color = button.palette().button().color()
        if current_color == QColor('transparent'):
            self.scence.Polygonable = True
            button.setStyleSheet('background-color: rgba(121, 115, 127, 55)')
        elif current_color == QColor(121, 115, 127, 55):
            self.scence.Polygonable = False
            button.setStyleSheet('background-color: transparent')
    
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
    def exit_application(self):
        self.close()

    def hideBoxFrame(self):
        self.animation.setEndValue(self.new_rect)
        self.animation.start()
        self.animation.finished.connect(self.showButton)
    
    def showButton(self):
        mapwidgets.pushButton_5.setEnabled(True)
        mapwidgets.pushButton_5.setVisible(True)
    
    def showBoxFrame(self):
        self.animation.setEndValue(self.origingeometry)
        self.animation.start()
        self.animation.finished.connect(self.hideButton)
    
    def hideButton(self):
        mapwidgets.pushButton_5.setEnabled(False)
        mapwidgets.pushButton_5.setVisible(False)


class MapView(QGraphicsView):
    def __init__(self, parent=None):
        super(MapView, self).__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.ArrowCursor)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        self.rubberBandRect = None
        self.Rectable = False
        self.Polygonable = False
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.drag_start = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def receieveRectFlag(self, flag):
        if flag % 2 != 0:
            self.Rectable = True
        else:
            self.Rectable = False
    def receievePolygonFlag(self, flag):
        if flag % 2 != 0:
            self.Polygonable = True
        else:
            self.Polygonable = False
    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.scaleView(math.pow(2.0, event.angleDelta().y() / 240.0))
        else:
            scroll_direction = event.angleDelta().y()
            scroll_bar = self.verticalScrollBar()

            if scroll_direction > 0:
                scroll_bar.setValue(scroll_bar.value() -
                                    scroll_bar.singleStep())
            else:
                scroll_bar.setValue(scroll_bar.value() +
                                    scroll_bar.singleStep())

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(
            scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def autoScaleView(self, x_min, y_min, x_max, y_max):
        scene_rect = QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
        viewport_rect = self.viewport().rect()
        aspect_ratio = viewport_rect.width() / viewport_rect.height()
        scene_ratio = scene_rect.width() / scene_rect.height()
        if scene_ratio > aspect_ratio:
            target_scale_factor = -viewport_rect.width() / scene_rect.width()
        else:
            target_scale_factor = -viewport_rect.height() / scene_rect.height()

        # self.scaleView(target_scale_factor)
        self.animateScale(self.transform().m11(), target_scale_factor)

    def animateScale(self, current_scale, target_scale, duration=1000, steps=200):
        if steps <= 0:
            return
        scale_diff = target_scale - current_scale
        scale_step = scale_diff / (steps*30)
        if abs(scale_diff) < 0.01:
            return
        new_scale = 1 + scale_step
        self.scaleView(new_scale)
        QTimer.singleShot(5, lambda: self.animateScale(
            current_scale + scale_step, target_scale, duration, steps - 1))
    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton) & (self.Rectable):
            self.rubberBandRect = QRectF(event.pos(), QSizeF())
            self.viewport().setCursor(Qt.CrossCursor)
        elif event.button() == Qt.MiddleButton:           
            self.drag_start = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self.rubberBandRect is not None) & (self.Rectable):
            self.rubberBandRect.setBottomRight(event.pos())
            self.viewport().update()
        elif self.drag_start is not None:
            delta = self.drag_start - event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
            self.drag_start = event.pos()
        else:
            super().mousePressEvent(event)
        super(MapView, self).mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if self.rubberBandRect is not None and event.button() == Qt.LeftButton and self.Rectable:
            selectedItems = []
            for item in self.scene().items(self.rubberBandRect, Qt.IntersectsItemShape):
                if item not in selectedItems:
                    selectedItems.append(item)
            self.paintonScence()
            self.rubberBandRect = None
            self.viewport().setCursor(Qt.ArrowCursor)

        elif event.button() == Qt.MiddleButton:
            self.drag_start = None
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        if self.rubberBandRect:
            painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            painter.drawRect(self.rubberBandRect)
    
    def paintonScence(self):
        if self.rubberBandRect:
            topLeftScene = self.mapToScene(self.rubberBandRect.topLeft().toPoint())
            bottomRightScene = self.mapToScene(self.rubberBandRect.bottomRight().toPoint())
            scene_rect = QRectF(topLeftScene, bottomRightScene)
            # scene.addRect(scene_rect, QPen(Qt.blue, 2, Qt.DashLine))
            
            self.topLeftScene_x = topLeftScene.x()
            self.topLeftScene_y = topLeftScene.y()
            self.bottomRightScene_x = bottomRightScene.x()
            self.bottomRightScene_y = bottomRightScene.y()
    def returnRectPara(self):       
        return self.topLeftScene_x, self.topLeftScene_y, self.bottomRightScene_x, self.bottomRightScene_y


class MyScene(QGraphicsScene):
    polygon_finished_signal = Signal(Polygon)
    def __init__(self):
        global dataset, world_dataset
        super().__init__()
        world_dataset = gpd.read_file('world.json')
        dataset = gpd.read_file('cn.json')
        self.Rectable = False
        self.Polygonable = False
        self.RectActiveFlag = 0
        self.Polygon_list = []
        self.itemlist_polygon = []
        self.itemlist_point = []
        self.path_list = []
        self.setSceneRect(0, 0, 4800, 3200)
        self.pixmap = QPixmap("world.png").scaled(4800, 3200)
        self.pixmap_item = QGraphicsPixmapItem(self.pixmap)
        self.addItem(self.pixmap_item)
        self.path = QPainterPath()
        self.rubberBand = None
        self.epsilon = 50
        self.path_x = []
        self.path_y = []
        self.highlight_timers = []
        self.timer = QTimer()
        # self.timer.timeout.connect(self.toggleEllipse)
        self.ellipse = None
        self.lon_line = []
        self.lat_line = []
    def receieveRectFlag(self, flag):
        if flag % 2 != 0:
            self.Rectable = True
        else:
            self.Rectable = False
    def receievePolygonFlag(self, flag):
        if flag % 2 != 0:
            self.Polygonable = True
        else:
            self.Polygonable = False

    def mouseMoveEvent(self, event):
        lon = 23.91+0.083636*(float(event.scenePos().x())-2703)
        lat = 22.05-0.08913*(float(event.scenePos().y())-1294)
        point = Point(lon, lat)
        geometry = gpd.GeoSeries([point])
        points = gpd.GeoDataFrame(geometry=geometry, crs='EPSG:4326')
        world_result = gpd.sjoin(points, world_dataset, predicate='within')
        self.result = gpd.sjoin(points, dataset, predicate='within')
        if str(world_result['name']).splitlines()[0].split()[1] =='中国':     
            name_ = str(self.result['name']).splitlines()
            name_ = '中国' + name_[0].split()[1]
        else:
            name_ = str(world_result['name']).splitlines()
            name_ = name_[0].split()[1]
        point_ = str(self.result['geometry']).splitlines()
        point_ = point_[0].split()
        point_ = point_[2] + ',' + point_[3]
        
        lon_text = f'lon:{lon:.4f}'
        lat_text = f'lat:{lat:.4f}'
        name_text = name_
        pos = QCursor.pos()
        pos.setX(pos.x() + 10)
        pos.setY(pos.y() + 10)
        QToolTip.showText(pos, f'{lon_text}<br>{lat_text}<br>{name_text}')
    
    def mousePressEvent(self, event):
        if self.Polygonable:
            if event.button() == Qt.LeftButton:
                pos = event.scenePos()
                self.drawPath(pos)
            if event.button() == Qt.RightButton:
                if self.itemlist_polygon:
                    item_to_remove = self.itemlist_polygon[-1]
                    self.removeItem(item_to_remove)
                    self.itemlist_polygon.remove(item_to_remove)

    def drawPath(self, pos):
        print(111111)
        x = pos.x()
        y = pos.y()
        if self.path.elementCount() == 0:
            self.path.moveTo(x, y)
        else:
            self.path.lineTo(x, y)
        self.path_x.append(x)
        self.path_y.append(y)
        if len(self.path_list) > 0:
            start_point_x = self.path_x[0]
            start_point_y = self.path_y[0]
            ed_point_x = self.path_x[-1]
            ed_point_y = self.path_y[-1]
            distance = QLineF(start_point_x, start_point_y, ed_point_x, ed_point_y).length()
            if distance <= self.epsilon:
                self.path.lineTo(self.path_x[0], self.path_y[0])
                self.path_x[-1] = self.path_x[0]
                self.path_y[-1] = self.path_y[0]
                self.createPolygon()
        path_item = self.addPath(self.path, QPen(Qt.blue, 2, Qt.DashLine))
        self.path_list.append(path_item)
    def createPolygon(self):
        points = [(x, y) for x, y in zip(self.path_x, self.path_y)]
        polygon = Polygon(points)
        self.polygon_finished_signal.emit(polygon)
    def addPoint(self, pos):
        return
        point_ = self.addEllipse(pos.x(), pos.y(), 5, 5, QPen(Qt.red))
        self.itemlist_point.append(point_)

    def toggleEllipse(self):
        if self.ellipse in self.items():
            self.removeItem(self.ellipse)
        else:
            self.addItem(self.ellipse)

    def addMultipolygonPath(self, name, ds):
        coord_x = []
        coord_y = []
        path = QPainterPath()
        aa = ds.loc[ds['name'] == name]['geometry']
        for geom in aa:
            try:
                polygons = geom.geoms
                for polygon in polygons:
                    geom_dict = mapping(polygon)
                    for coords in geom_dict['coordinates']:
                        for coord in coords:
                            x, y = coord
                            x, y = maptoScence(x, y)
                            coord_x.append(x)
                            coord_y.append(y)
                            if path.elementCount() == 0:
                                path.moveTo(x, y)
                            else:
                                path.lineTo(x, y)
            except AttributeError:
                geom_dict = mapping(geom)
                for coords in geom_dict['coordinates']:
                    for coord in coords:
                        x, y = coord
                        x, y = maptoScence(x, y)
                        coord_x.append(x)
                        coord_y.append(y)
                        if path.elementCount() == 0:
                            path.moveTo(x, y)
                        else:
                            path.lineTo(x, y)
        self.path_list.append(path)
        return path

    def addBoundary(self, path, pen=QPen(Qt.blue)):
        self.addPath(path, pen=pen)

    def drawGrid(self, grid_spacing):
        self.path = self.path_list[0]
        bounding_rect = self.path.boundingRect()
        x_min, y_min = bounding_rect.left(), bounding_rect.top()
        x_max, y_max = bounding_rect.right(), bounding_rect.bottom()
        x = x_min
        print(x_min, y_min, x_max, y_max)
        while x <= x_max:
            
            line = QLineF(x, y_min, x, y_max)
            _ = self.addLine(line, pen=QPen(Qt.blue))
            self.lon_line.append(_)
            x += grid_spacing
        y = y_min
        while y <= y_max:
            line = QLineF(x_min, y, x_max, y)
            __ = self.addLine(line, pen=QPen(Qt.blue))
            self.lat_line.append(__)
            y += grid_spacing
    def clearFormerLine(self):
        for line in self.lon_line + self.lat_line:
            self.removeItem(line)
        self.lon_line = []
        self.lat_line = []

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1220, 940)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(9, 9, 1201, 921))
        self.frame.setStyleSheet(u"QFrame{background-color:white}\n"
"QWidget{\n"
"	color: rgb(0, 0, 0);\n"
"	font: 10pt \"Segoe UI\";\n"
"}")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setGeometry(QRect(0, 0, 1201, 50))
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
        self.pushButton_7.setGeometry(QRect(1160, 10, 31, 28))
        icon = QIcon()
        icon.addFile(u"../VisualEnvironment/icon/\u5173\u95ed.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_7.setIcon(icon)
        self.pushButton_8 = QPushButton(self.frame_5)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setGeometry(QRect(1130, 10, 31, 28))
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
        self.graphicsView = MapView(self.frame)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(2, 50, 1201, 871))
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(4, 220, 21, 341))
        self.frame_2.setStyleSheet(u"QPushButton{background-color:transparent;}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.pushButton = QPushButton(self.frame_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(-1, 41, 19, 29))
        icon2 = QIcon()
        icon2.addFile(u"../VisualEnvironment/icon/\u641c\u7d22.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon2)
        self.pushButton_2 = QPushButton(self.frame_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(-1, 117, 19, 29))
        icon3 = QIcon()
        icon3.addFile(u"../VisualEnvironment/icon/\u6846\u90091.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon3)
        self.pushButton_3 = QPushButton(self.frame_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(-1, 193, 19, 29))
        icon4 = QIcon()
        icon4.addFile(u"../VisualEnvironment/icon/\u591a\u8fb9\u5f62.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon4)
        self.pushButton_4 = QPushButton(self.frame_2)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(0, 310, 19, 29))
        icon5 = QIcon()
        icon5.addFile(u"../VisualEnvironment/icon/\u4e09\u89d2\u5f62\u5de6.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_4.setIcon(icon5)
        self.pushButton_5 = QPushButton(self.frame)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(0, 530, 21, 28))
        self.pushButton_5.setStyleSheet(u"QPushButton{background-color:transparent;}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}")
        icon6 = QIcon()
        icon6.addFile(u"../VisualEnvironment/icon/\u4e09\u89d2\u5f62-\u53f3.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_5.setIcon(icon6)
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(25, 220, 0, 111))
        self.frame_3.setMaximumSize(QSize(200, 16777215))
        self.frame_3.setMouseTracking(True)
        self.frame_3.setFocusPolicy(Qt.StrongFocus)
        self.frame_3.setAcceptDrops(True)
        self.frame_3.setInputMethodHints(Qt.ImhMultiLine)
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.layoutWidget = QWidget(self.frame_3)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 161, 101))
        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.comboBox_2 = QComboBox(self.layoutWidget)
        self.comboBox_2.setObjectName(u"comboBox_2")
        self.comboBox_2.setEditable(True)

        self.verticalLayout.addWidget(self.comboBox_2)

        self.comboBox_3 = QComboBox(self.layoutWidget)
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setEditable(True)

        self.verticalLayout.addWidget(self.comboBox_3)

        self.verticalLayoutWidget = QWidget(self.frame)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(19, 240, 161, 101))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.verticalLayoutWidget)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMaximumSize(QSize(0, 16777215))
        self.frame_4.setStyleSheet(u"")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.layoutWidget1 = QWidget(self.frame_4)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(20, 6, 121, 91))
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.comboBox = QComboBox(self.layoutWidget1)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setEditable(True)

        self.verticalLayout_3.addWidget(self.comboBox)

        self.comboBox_4 = QComboBox(self.layoutWidget1)
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setEditable(True)

        self.verticalLayout_3.addWidget(self.comboBox_4)

        self.pushButton_6 = QPushButton(self.layoutWidget1)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setStyleSheet(u"QPushButton{background-color:transparent;}\n"
"QPushButton:hover {\n"
"    background-color: rgba(121, 115, 127, 55);\n"
"}")

        self.verticalLayout_3.addWidget(self.pushButton_6)


        self.verticalLayout_2.addWidget(self.frame_4)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.label_2.setText("")
        self.label_3.setText(QCoreApplication.translate("Form", u"VisualData APP-UI for viusal data,based on Python.", None))
        self.pushButton.setText("")
        self.pushButton_2.setText("")
        self.pushButton_3.setText("")
        self.pushButton_4.setText("")
        self.pushButton_5.setText("")
        self.comboBox_2.setPlaceholderText("")
        self.pushButton_6.setText(QCoreApplication.translate("Form", u"\u786e\u5b9a", None))
    # retranslateUi





if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())