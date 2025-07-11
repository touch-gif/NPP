from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import math
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from detiledinfodialog_ui import Ui_detiledInfoDialog
from DataTable import PandasModel
import os
import tempfile
import pandas as pd


class HoverablePolygonItem(QGraphicsPolygonItem):
    def __init__(self, polygon_points, index, df, datacol,
                 polygon_centriod, data_view, cors, time_unit):
        super().__init__()
        self.data_view = data_view
        self.polygon_points = polygon_points
        self.setPolygon(QPolygonF(self.polygon_points))
        
        self.index = index
        self.df = df
        self.time_unit = time_unit
        self.cors = cors
        
        self.count = self.df.shape[0]
        self.polygon_centriod = polygon_centriod     
        norm = mcolors.Normalize(vmin=self.df[datacol].min(), vmax=self.df[datacol].max())
        cmap = plt.cm.viridis
        self.mean = self.df[datacol].mean()
        color = cmap(norm(self.mean))     
        if self.count != 0:
            self.setAcceptHoverEvents(True)
            self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
            self.r, self.g, self.b, _ = [int(255 * c) for c in color]
            self.setBrush(QColor(self.r, self.g, self.b, 100))

        else:
            print('*******************************************************')
            self.r, self.g, self.b, _ = 158, 158 ,158 ,1
            self.setBrush(QColor(self.r, self.g, self.b, 100))

        self.original_pen = QPen(QColor(0, 0, 0))
        self.setPen(self.original_pen)
        self.hover_pen = QPen(QColor(0, 0, 0), 2)
    
    
    def hoverEnterEvent(self, event):
        if self.count != 0:
            self.setBrush(QColor(self.r, self.g, self.b, 255))
        self.setPen(self.hover_pen)
        self.text_item = QGraphicsTextItem()
        self.text_item.setParentItem(self)
        self.text_item.setFlag(QGraphicsTextItem.ItemIgnoresParentOpacity)
        currentindex = self.index
        self.text_item.setPlainText(
            f'mean: {self.mean:.2f}\ncount: {self.count}')
        center = self.polygon_centriod
        self.text_item.setPos(center.x*100, -(center.y)*100)
        self.text_item.setZValue(1)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.show()
    
    def hoverLeaveEvent(self, event):
        if self.count != 0:
            self.setBrush(QColor(self.r, self.g, self.b, 100))
            self.text_item.hide()
        self.setPen(self.original_pen)
    def highlight(self):
        if self.count != 0:
            self.setBrush(QColor(self.r, self.g, self.b, 255))
            self.setPen(self.hover_pen)
    def resetBrush(self):
        if self.count != 0:
            self.setBrush(QColor(self.r, self.g, self.b, 100))
            self.setPen(self.original_pen)
    def animateMove(self, current_center, target_center, duration=50, steps=1000):
        if steps <= 0:
            return
        x_diff = target_center.x() - current_center.x()
        y_diff = target_center.y() - current_center.y()
        move_diff = math.sqrt(x_diff**2 + y_diff**2)
        move_step = QPointF(x_diff / steps, y_diff / steps)
        if move_diff < 0.01:
            return
        new_center = current_center + move_step
        self.holderview.centerOn(new_center)
        QTimer.singleShot(
            duration // steps, lambda: self.animateMove(new_center, target_center, duration, steps - 1))

    def mousePressEvent(self, event):
        self.center = self.polygon_centriod
        if (event.button() == Qt.LeftButton) and self.count != 0:
            view = self.scene().views()[0]

            x_pos, y_pos = (self.center.x)*100, -(self.center.y)*100
            view_center = view.mapToScene(
                view.viewport().rect().center())
            offset_x = x_pos - view_center.x()
            offset_y = y_pos - view_center.y()
            view_center_c = view.mapToScene(
                view.viewport().rect().center())
            view_center_t = QPointF(
                view_center_c.x() + offset_x, view_center_c.y() + offset_y)
            self.animateMove(view_center_c, view_center_t)
            view.fitInView(self.boundingRect(), Qt.KeepAspectRatio)
            super().mousePressEvent(event)
        if (event.button() == Qt.RightButton):           
            super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        if self.count != 0:
            menu = QMenu()
            menu.setStyleSheet("""

""")
            action1 = menu.addAction('show detialed data')
            action2 = menu.addAction('show historical changes')     
            action3 = menu.addAction('loc digit data') 
            action = menu.exec_(event.screenPos())   
            if action == action1:
                self.showDetialedData()
            elif action == action2:
                self.showHistoricalChanges()
            elif action == action3:
                self.locDigitData()
        else:
            super().contextMenuEvent(event)
    
    def showDetialedData(self):      
        description = self.df.describe()
        class showDetialedDataDialog(QDialog):
            def __init__(self, parent):
                super(showDetialedDataDialog, self).__init__()
                self.ui = Ui_detiledInfoDialog()
                self.ui.setupUi(self)
                self.parent = parent
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.setContentsMargins(0, 0, 0, 0)
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.ui.pushButton_10.clicked.connect(self.closea)
                self.ui.pushButton_9.clicked.connect(self.showMinimized)
                self.proxy_model = QSortFilterProxyModel()
                new_model = PandasModel(description)
                self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                self.proxy_model.setSourceModel(new_model)
                self.ui.tableView.setModel(self.proxy_model)
            
            def closea(self):
                self.close()
            
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
        self.sddialog = showDetialedDataDialog(parent=self)
        self.sddialog.exec_()
   
    def locDigitData(self):
        selection_model = self.data_view.selectionModel()
        selection_model.clearSelection()

        proxy_model = self.data_view.model()
        index_right_column = None
        for col in range(proxy_model.columnCount()):
            header_data = proxy_model.headerData(col, Qt.Horizontal)
            if header_data == 'rigion_index':
                index_right_column = col
                break
        
        if index_right_column is None:
            print("Column 'index_right' not found.")
            return
        for row in range(proxy_model.rowCount()):
            index_right_index = proxy_model.index(row, index_right_column)
            if int(index_right_index.data()) == self.index:
                first_column_index = proxy_model.index(row, 0)
                last_column_index = proxy_model.index(row, proxy_model.columnCount() - 1)
                selection = QItemSelection(first_column_index, last_column_index)
                selection_model.select(selection, QItemSelectionModel.Select)
                self.data_view.scrollTo(first_column_index, QAbstractItemView.PositionAtCenter)

    def showHistoricalChanges(self):     
        self.dialog = QDialog()
        self.dialog.setGeometry(700, 700, 700, 700)
        layout = QVBoxLayout()  
        hbox = QHBoxLayout()     
        lineedit = QLineEdit('3')
        hbox.addWidget(lineedit)
        combobox = QComboBox()
        combobox.addItems(['ME', 'YE', 'DE']) 
        hbox.addWidget(combobox)
        lineedit.textChanged.connect(self.rePlot)
        combobox.currentTextChanged.connect(self.rePlot)
        layout.addLayout(hbox)
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)      
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)    
        self.dialog.setLayout(layout)
        self.rePlot()
        self.dialog.exec_()

    def rePlot(self):
        period = self.dialog.findChild(QLineEdit).text() + self.dialog.findChild(QComboBox).currentText()
        try:
            aggregated_data = self.resampleDate(self.df[['xco2', self.cors['time']]] , period)
            print(aggregated_data)
        except ValueError:
            print('rrrrr')
            return
        self.ax.clear()
        bars = self.ax.bar(aggregated_data[self.cors['time']].astype(str), aggregated_data['xco2'], color='skyblue')
        [tick.set_rotation(30) for tick in self.ax.get_xticklabels()]
        self.ax.set_xlabel('Time Period')
        self.ax.set_ylabel('Mean xCO2')
        for bar in bars:
            height = bar.get_height()
            label = self.ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom')
            label.set_rotation(90)
        canvas = FigureCanvas(self.fig)
        canvas.draw()
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.fig.savefig(temp_file.name)
        temp_file.close()
        image = QPixmap(temp_file.name)
        os.unlink(temp_file.name) 
        self.scene.clear()
        self.scene.addPixmap(image)
        self.view.setScene(self.scene)
    
    def resampleDate(self, df, period='3M'):
        if self.time_unit == 's':
            df[self.cors['time']] = pd.to_datetime(df[self.cors['time']], unit='s')
        elif self.time_unit == 'ms':
            df[self.cors['time']] = pd.to_datetime(df[self.cors['time']], unit='ms')
        elif isinstance(self.time_unit, str):
            df[self.cors['time']] = pd.to_datetime(df[self.cors['time']], format=self.time_unit)
        print(df)
        try:
            df.set_index(self.cors['time'], inplace=True)  # Set the time column as index
        except KeyError:
            pass
        df_resample = df.resample(period)
        df_mean_xco2 = df_resample['xco2'].mean().rename('xco2')
        ser = df_resample['xco2'].count().rename('sample_count_tccon')
        df_new = pd.concat([df_mean_xco2, ser], axis=1)
        df_new.reset_index(inplace=True)
        return df_new


class ScaleableView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.drag_start = None
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        self.rubberBandRect = None
        self.setCursor(Qt.ArrowCursor)
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.selectedItemIndex = []
        self.setAlignment(Qt.AlignCenter)
        # self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.mouse_pos_before_zoom = event.position()
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

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton) and (event.modifiers() == Qt.ControlModifier):
            self.rubberBandRect = QRectF(event.pos(), QSizeF())
            self.viewport().setCursor(Qt.CrossCursor)

        elif event.button() == Qt.MiddleButton:
            self.drag_start = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self.rubberBandRect is not None) & (event.modifiers() == Qt.ControlModifier):
            self.rubberBandRect.setBottomRight(event.pos())
            self.viewport().update()
        elif self.drag_start is not None:
            delta = self.drag_start - event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())
            self.drag_start = event.pos()
        # elif self.drag_start is None:
        #             # self.text_item.setPlainText(
        # #     f'mean: {self.mean}\ncount: {self.count}')
        # # center = self.polygon_centriod
        # # self.text_item.setPos(center.x*100, -(center.y)*100)
        # # self.text_item.setZValue(1)
        # # self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        # # self.text_item.show()
        #     mouse_pos = event.pos()
        #     scene_pos = self.mapToScene(mouse_pos)
        #     items = self.scene().items(scene_pos)
        #     for item in items:
        #         if isinstance(item, QGraphicsItem):
        #             text_item = QGraphicsTextItem(f"Text for item at {scene_pos.x()}, {scene_pos.y()}")
        #             text_item.setPos((item.polygon_centriod.x)*100, (item.polygon_centriod.y)*100)
        #             self.scene().addItem(text_item)
        else:
            super().mousePressEvent(event)
        super(ScaleableView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (self.rubberBandRect is not None):
            selected_items = self.items(
                self.rubberBandRect.toRect(), Qt.IntersectsItemShape)
            for item in selected_items:
                if isinstance(item, HoverablePolygonItem):
                    item.selected()

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


class MapPolygonItem(HoverablePolygonItem):
    def __init__(self, polygon_points, index, r, g, b, mean, geo_df, df, loncol, latcol, timecol):
        super().__init__(polygon_points, index, r, g, b, mean, geo_df, df, loncol, latcol, timecol)
