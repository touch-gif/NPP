from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import polars as pl
from staticmethod import *
from HoverablePolygonItem import HoverablePolygonItem
import re

class LoadAndExamineDataThread(QObject):
    data_ready_signal = Signal(pl.DataFrame)
    prompt_user_cols_signal = Signal()
    prompt_user_format_signal = Signal()
    auto_set_cols_signal = Signal(dict)
    time_unit_signal = Signal(str)
    def  __init__(self, folder_path:str)->None:
        super().__init__()
        self.folder_path = folder_path
    
    def loadData(self):
        '''read csvs contained in a folder'''
        files = listFilesFolder(folder_path=self.folder_path)
        dfs = []
        for file in files:
            df = pl.read_csv(file)
            dfs.append(df)
        self.data = pl.concat(dfs, how='vertical')
        cols = self.data.columns
        print(self.data)
        self.setCorrespondingVariables(cols)
        self.examDataFormat()
    
    def setCorrespondingVariables(self, cols):
        '''make columns correspond to lon,lat,time using re '''
        self.correspondingVariables = {}
        expected_cols = ['lat', 'lon', 'time', 'date']
        matched_cols = []
        for col in cols:
            for expected_col in expected_cols:
                if re.search(expected_col, col, re.IGNORECASE):
                    matched_cols.append(col)
                    expected_cols.remove(expected_col)
                    self.correspondingVariables[expected_col] = col
                    break
        if len(matched_cols) == 3:
            if 'date' in self.correspondingVariables.keys():
                self.correspondingVariables['time'] = self.correspondingVariables['date']
        else:
            self.promptUserToSetColumnsEmit()
        self.auto_set_cols_signal.emit(self.correspondingVariables)
    
    def promptUserToSetColumnsEmit(self):
        self.prompt_user_cols_signal.emit()
    
    def promptUserToSetDateFormatEmit(self):
        self.prompt_user_format_signal.emit()
    
    def startWorking(self):
        self.loadData()
        self.data_ready_signal.emit(self.data)
    
    def examDataFormat(self):
        lon_dtype = self.data[self.correspondingVariables['lon']].dtype
        lat_dtype = self.data[self.correspondingVariables['lat']].dtype
        if lon_dtype == lat_dtype == pl.Float64:
            pass
        else:
            print('wrong type')
            return

        time_dtype = self.data[self.correspondingVariables['time']].dtype
        if time_dtype in [pl.Float64, pl.Int64]:
            first_time_value = self.data[self.correspondingVariables['time']][0]
            if first_time_value > 172552605700:
                self.time_unit = 'ms'
            else:
                self.time_unit = 's'
        else:
            try:
                datetime_series = pl.Series(self.data.head(10)[self.correspondingVariables['time']]).str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S.%f")
                self.time_unit = "%Y-%m-%d %H:%M:%S.%f"
                if datetime_series.is_null().any():
                    raise ValueError
            except:
                try:
                    datetime_series = pl.Series(self.data.head(10)[self.correspondingVariables['time']]).str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S.%fZ")
                    self.time_unit = "%Y-%m-%dT%H:%M:%S.%fZ"
                except:
                    self.promptUserToSetDateFormatEmit()
        self.time_unit_signal.emit(self.time_unit)


class MapPolygons(QObject):
    progressbar_update_signal = Signal(int)
    polygon_finished_signal = Signal(HoverablePolygonItem)
    polygons_ready_signal = Signal(pd.DataFrame)
    mean_count_signal = Signal(dict)
    polygon_data_ready_signal = Signal(dict)
    def  __init__(self, area, cellsize_lat, cellsize_lon,
                   correspondingVariables, data, data_view,
                   time_unit, standard)->None:
        super().__init__()
        self.mean_count_data = {'over':0, 'less':0}
        self.area = area
        self.cellsize_lat = cellsize_lat
        self.cellsize_lon = cellsize_lon
        self.correspondingVariables = correspondingVariables
        self.data = data
        self.data_view = data_view
        self.time_unit = time_unit
        self.standard = standard
    
    def polygonsWork(self):
        
        self.mean_count_data['over_index'] = []
        self.mean_count_data['less_index'] = []
        geo_df = gridifyPolygon(area_=self.area, cellsize_lat=0.5, cellsize_lon=0.5)     
        polygon_data, concat_data = getPolygonsData(geo_df=geo_df,
                                       loncol=self.correspondingVariables['lon'],
                                       latcol=self.correspondingVariables['lat'],
                                       df=self.data.to_pandas(),signal=self.progressbar_update_signal)   
        datacol = 'xco2'
        for data_dict in polygon_data:
            mean = data_dict['data'][datacol].mean()
            self.polygon_data_ready_signal.emit(data_dict)
            if isinstance(mean, (int, float)):
                if mean >= self.standard:
                    self.mean_count_data['over'] += 1
                    self.mean_count_data['over_index'].append(data_dict['index'])
                else:
                    if (mean != 0) and (not np.isnan(mean)):
                        self.mean_count_data['less'] += 1
                        self.mean_count_data['less_index'].append(data_dict['index'])          
        self.mean_count_signal.emit(self.mean_count_data)
        self.polygons_ready_signal.emit(concat_data)
        
        