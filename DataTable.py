from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from DataTable_ui import Ui_Form, Ui_Dialog
import polars as pl
import pandas as pd

class DataWidget(QWidget):
    def __init__(self, originaldata, cors, time_unit_):
        global dataviewwidgets, corssponding, time_unit
        super().__init__()
        corssponding = cors
        time_unit = time_unit_
        self.ui = Ui_Form()
        dataviewwidgets = self.ui
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        dataviewwidgets.closeAppBtn.clicked.connect(self.exit_application)
        dataviewwidgets.minimizeAppBtn.clicked.connect(self.showMinimized)
        dataviewwidgets.tableView.verticalHeader().setVisible(False)
        self.header = DataTableViewHeader(dataviewwidgets.tableView, originaldata)
        dataviewwidgets.tableView.setHorizontalHeader(self.header)
        dataviewmodel = PolarsModel(originaldata)
        self.header.setProxyModel(dataviewmodel)
        dataviewwidgets.tableView.setModel(dataviewmodel)
        dataviewwidgets.tableView.setCornerButtonEnabled(False)
        dataviewwidgets.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    def exit_application(self):
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
class DataTableViewHeader(QHeaderView):
    def __init__(self, parent, originaldata):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(False)
        self.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.data = originaldata
        self.originaldata = originaldata
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
    QMenu {
        background-color: black;
        color: white;
    }
    QMenu::item:selected {
        background-color: rgb(189, 147, 249);
        color: white;
    }
""")
        self.action_descending = QAction('Descending Order', self)
        self.action_ascending = QAction('Ascending Order', self)
        self.action_shuffle = QAction('Shuffle', self)
        self.action_to_datetime = QAction('toDateTime', self)
        self.action_reloading = QAction('Reloading', self)
        self.action_split = QAction('Split Date column', self)
        self.menu.addAction(self.action_descending)
        self.menu.addAction(self.action_ascending)
        self.menu.addAction(self.action_shuffle)
        self.menu.addAction(self.action_to_datetime)
        self.menu.addAction(self.action_reloading)
        self.menu.addAction(self.action_split)

        self.customContextMenuRequested.connect(self.showContextMenu)
        self.action_descending.triggered.connect(self.descendingOrder)
        self.action_ascending.triggered.connect(self.ascendingOrder)
        self.action_shuffle.triggered.connect(self.shuffle)
        self.action_to_datetime.triggered.connect(self.toDatetime)
        self.action_reloading.triggered.connect(self.reloading)
        self.action_split.triggered.connect(self.splitdatecolumn)

        self.current_column_name = None
    
    def perform_operation_in_thread(self, operation, *args):
        self.thread = QThread()
        self.worker = Worker(self.originaldata, self.current_column_name, operation, *args)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
    
    def on_operation_finished(self, result):
        new_model = PolarsModel(result)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)
    
    def setProxyModel(self, model):
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(model)
        dataviewwidgets.tableView.setModel(self.proxy_model)

    def showContextMenu(self, pos):
        index = self.logicalIndexAt(pos)
        self.current_column_name = self.model().headerData(index, Qt.Horizontal)
        if index >= 0:
            self.current_logical_index = index
            model = self.proxy_model.sourceModel()
            column_name = model.headerData(index, Qt.Horizontal)
            if column_name == 'time' or column_name == 'date':
                if not self.menu.actions().__contains__(self.action_to_datetime):
                    self.menu.addAction(self.action_to_datetime)
                    self.menu.addAction(self.action_split)
            else:
                if (self.menu.actions().__contains__(self.action_to_datetime)) or (self.menu.actions().__contains__(self.action_to_datetime)):
                    self.menu.removeAction(self.action_to_datetime)
                    self.menu.removeAction(self.action_split)

            self.menu.exec_(self.mapToGlobal(pos))

    def toDatetime(self):
        # Convert the 'time' column to datetime using Polars
        if time_unit == 's':
            self.data = self.data.with_columns(
                pl.col(corssponding).cast(pl.Int64).mul(1000).cast(pl.Datetime("ms")))
        elif time_unit == 'ms':
            self.data = self.data.with_columns(
                pl.col(corssponding).cast(pl.Int64).cast(pl.Datetime("ms")))
        elif isinstance(time_unit, str):
            if time_unit is not None:
                self.data = self.data.with_columns(pl.col(corssponding['time']).str.strptime(pl.Datetime, format=time_unit, strict=False))
            else:
                self.data = self.data.with_columns(pl.col(corssponding['time']).str.strptime(pl.Datetime))
        new_model = PolarsModel(self.data)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model) 
    
    def splitdatecolumn(self):
        # Split datetime into year, month, day, hour
        self.data = self.data.with_columns([
            pl.col(corssponding['time']).dt.year().alias("year"),
            pl.col(corssponding['time']).dt.month().alias("month"),
            pl.col(corssponding['time']).dt.day().alias("day"),
            pl.col(corssponding['time']).dt.hour().alias("hour")
        ]).drop(corssponding['time'])

        new_model = PolarsModel(self.data)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)
    
    def descendingOrder(self):
        # Sort by current column in descending order
        self.data = self.data.sort(self.current_column_name, descending=True)
        new_model = PolarsModel(self.data)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)

    def ascendingOrder(self):
        # Sort by current column in ascending order
        self.data = self.data.sort(self.current_column_name, descending=False)
        new_model = PolarsModel(self.data)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)
    def reloading(self):
        # Reload the original data
        self.data = self.originaldata
        new_model = PolarsModel(self.data)
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)
    
    def updataFromOtherClass(self, df):
        new_model = PolarsModel(df)
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(new_model)
        dataviewwidgets.tableView.setModel(self.proxy_model)   
        self.data = df
    def shuffle(self):
        class ShuffleDialog(QDialog):
            def __init__(self, parent, columnname):
                super(ShuffleDialog, self).__init__()
                self.columnname = columnname
                self.ui = Ui_Dialog()
                self.ui.setupUi(self)
                self.parent = parent
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.setContentsMargins(0, 0, 0, 0)
                self.setAttribute(Qt.WA_TranslucentBackground)

                self.ui.pushButton.clicked.connect(self.shuffle)
                self.ui.pushButton_2.clicked.connect(self.close)
                self.ui.lineEdit.setText(str(self.parent.data[self.columnname].min()))
                self.ui.lineEdit_2.setText(str(self.parent.data[self.columnname].max()))
            
            def close(self):
                super().close()
            
            def shuffle(self):
                start = self.ui.lineEdit.text()
                end = self.ui.lineEdit_2.text()
                try:
                    self.parent.data = self.parent.data.filter(
                        (pl.col(self.columnname) > float(start)) & 
                        (pl.col(self.columnname) < float(end))
                    )
                except ValueError:
                    self.parent.data = self.parent.data.filter(
                        (pl.col(self.columnname) > start) & 
                        (pl.col(self.columnname) < end)
                    )
                self.parent.proxy_model.setSourceModel(PolarsModel(self.parent.data))
                dataviewwidgets.tableView.setModel(self.parent.proxy_model)
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
        
        self.dialog = ShuffleDialog(parent=self, columnname=self.current_column_name)
        self.dialog.exec_()

class DataTableView(QTableView):
    def __init__(self, *args, **kwargs) -> None:
        super(DataTableView, self).__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableviewmenu = QMenu(self)
        self.action1 = QAction('copy', self)
        self.action2 = QAction('loc grid data', self)
        self.tableviewmenu.addAction(self.action1)
        self.tableviewmenu.addAction(self.action2)
        self.action1.triggered.connect(self.action_copy)
        self.action2.triggered.connect(self.action_loc_grid_data)
        self.customContextMenuRequested.connect(self.show_context_menu)
    def show_context_menu(self, pos):
        self.tableviewmenu.exec_(self.mapToGlobal(pos))
    def action_copy(self):
        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            print("菜单项1被点击，当前选中单元格的文本：", index.data())
    
    def action_loc_grid_data(self):
        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            print("菜单项2被点击，当前选中单元格的文本：", index.data())


    
    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     table_width = sum(self.columnWidth(i) for i in range(self.model().columnCount()))
    #     if table_width > self.viewport().width():
    #         self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    #     else:
    #         self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1] + 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(self._data.index[index.row()])
            else:
                return str(self._data.iloc[index.row(), index.column() - 1])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Index"
                else:
                    return str(self._data.columns[section - 1])
            elif orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

class PolarsModel(QAbstractTableModel):
    def __init__(self, data: pl.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.height

    def columnCount(self, parent=None):
        return self._data.width + 1

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(index.row())
            else:
                value = self._data[self._data.columns[index.column() - 1]][index.row()]
                return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Index"
                else:
                    return self._data.columns[section - 1]
            elif orientation == Qt.Vertical:
                return str(section)
        return None

class Worker(QObject):
    finished = Signal(pd.DataFrame)

    def __init__(self, data, column_name, operation, *args):
        super().__init__()
        self.data = data
        self.originaldata = data
        self.column_name = column_name
        self.operation = operation
        self.args = args

    def run(self):
        if self.operation == "ascending":
            result = self.data.sort_values(by=self.column_name)
        elif self.operation == "descending":
            result = self.data.sort_values(by=self.column_name, ascending=False)
        elif self.operation == "shuffle":
            start, end = self.args
            result = self.data.loc[(self.data[self.column_name] > int(start)) & (self.data[self.column_name] < int(end))]
        elif self.operation == "to_datetime":
            result = self.data.copy()
            result['time'] = pd.to_datetime(self.data['time'])
        elif self.operation == 'reloading':
            result = self.originaldata
        elif self.operation == 'splitdatacolumn':
            self.data['year'] = self.data['time'].dt.year
            self.data['month'] = self.data['time'].dt.month
            self.data['day'] = self.data['time'].dt.day
            self.data['hour'] = self.data['time'].dt.hour
            self.data.drop(columns=['time'], inplace=True)
            result = self.data
        
        self.finished.emit(result)