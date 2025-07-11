from PySide6.QtCore import *
from PySide6.QtCore import QObject
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from random import randint
from shapely import geometry
from math import sin, cos, pi


class PieChartItem(QGraphicsPolygonItem):
    def __init__(self, data, description, start_angle, r, g, b,standard):
        super().__init__()
        self.data = data      
        self.total = self.data['over'] + self.data['less']
        self.start_angle = start_angle
        self.r = r
        self.g = g
        self.b = b
        self.description = description
        self.value = self.data[self.description]
        self.corsindex = self.data[f'{self.description}_index']
        self.percentage = (self.value / self.total)
        self.angle = int(self.percentage * 360)
        self.end_angle = self.start_angle + self.angle
        self.rect = QRectF(10, 0, 150, 150)
        self.center = self.rect.center()
        self.radius = min(self.rect.width(), self.rect.height()) / 2
        self.polygon_points = self.generatePolygonPoints(self.start_angle, self.end_angle, self.center, self.radius)
        self.setPolygon(QPolygonF(self.polygon_points))
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setBrush(QColor(self.r, self.g, self.b, 100))
        self.hover_on = None
        self.standard = standard
        self.hover_radius_increase = 2
        self.hover_pen = QPen(QColor(self.r, self.g, self.b), 2)
        self.original_pen = QPen(QColor(self.r, self.g, self.b))
        self.setPen(self.original_pen)
    def generatePolygonPoints(self, start_angle, end_angle, center, radius):
       points = []
       for angle in range(start_angle, end_angle):
           radian = angle * (pi / 180)
           x = center.x() + radius * cos(radian)
           y = center.y() + radius * sin(radian)
           points.append(QPointF(x, y))
       return points
    
    def hoverEnterEvent(self, event):
        self.setBrush(QColor(self.r, self.g, self.b, 255))
        self.text_item = QGraphicsTextItem()
        self.text_item.setParentItem(self)
        self.text_item.setFlag(QGraphicsTextItem.ItemIgnoresParentOpacity)
        if self.description == 'over':
            self.text_item.setPlainText(
                f'       {self.percentage*100:.2f}%\nexceed the standard\n       (>={self.standard})')
        else:
            self.text_item.setPlainText(
                f'       {self.percentage*100:.2f}%\nbe within the standard\n       (<{self.standard})')
        self.text_item.setPos(self.center.x()-80, self.center.y()-30)
        self.text_item.setZValue(1)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        self.text_item.show()
        self.hover_on = True
        
        new_radius = self.radius + self.hover_radius_increase
        self.polygon_points = self.generatePolygonPoints(self.start_angle, self.end_angle, self.center, new_radius)
        self.setPolygon(QPolygonF(self.polygon_points))
        self.setPen(self.hover_pen)
        
        print(self.hover_on)
    
    def hoverLeaveEvent(self, event):
        self.setBrush(QColor(self.r, self.g, self.b, 100))
        self.text_item.hide()
        self.hover_on = False
        self.polygon_points = self.generatePolygonPoints(self.start_angle, self.end_angle, self.center, self.radius)
        self.setPolygon(QPolygonF(self.polygon_points))
        self.setPen(self.original_pen)
    
    def returnStartAngle(self):
        return self.end_angle