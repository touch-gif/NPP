from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQtChart Pie Chart")
        self.setGeometry(100, 100, 1280, 600)

        self.show()

        self.create_piechart()

    def create_piechart(self):
        series = QPieSeries()
        series.append("Python", 80)
        series.append("C++", 70)
        series.append("Java", 50)
        series.append("C#", 40)
        series.append("PHP", 30)


        # adding slice

        slice0 = QPieSlice()
        slice0 = series.slices()[0]
        slice0.setLabelVisible(True)
        slice0.setBrush(Qt.green)

        slice1 = QPieSlice()
        slice1 = series.slices()[1]
        slice1.setLabelVisible(True)
        slice1.setExploded(True)
        slice0.setBrush(Qt.red)

        slice2 = QPieSlice()
        slice2 = series.slices()[2]
        slice2.setLabelVisible(True)

        slice3 = QPieSlice()
        slice3 = series.slices()[3]
        slice3.setLabelVisible(True)

        slice4 = QPieSlice()
        slice4 = series.slices()[4]
        slice4.setLabelVisible(True)


        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle("Pie Chart Example")

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(chartview)


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec_())
