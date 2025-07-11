from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy as np
from tqdm import tqdm
# from pyhdf.SD import SD
import re
import matplotlib.patches as patches
import numpy as np
from PIL import Image


class TilesConnectThread(QObject):
    data_ready_signal = Signal(np.ndarray)
    def  __init__(self, paths, output_path,
                  lonmin, lonmax, latmin, latmax)->None:
        super().__init__()
        self.paths = paths

    def retriveTilesInfomation(self) -> pd.DataFrame:
        '''return files infomation dataframe,[observation date,geometry horizental,
        geometry vertical,file path,product date]
            '''
        gpp_file_paths = self.paths
        file_paths = pd.DataFrame(gpp_file_paths, columns=['file_path'])
        result = file_paths['file_path'].str.split('.', expand=True)
        columns = ['_1', 'date', 'tail', '_2', '_3', '_4']
        result.columns = columns
        df = pd.DataFrame()
        df['horizental'] = result['tail'].str[1:3].astype(int)
        df['vertical'] = result['tail'].str[4:6].astype(int)
        df['year'] = result['date'].str[1:5].astype(int)
        df['day'] = result['date'].str[5:8].astype(int)
        df.dropna(inplace=True)
        df['path'] = file_paths['file_path']
        df['production_date'] = result['_3']
        df['observation_date'] = df.apply(lambda row: datetime(
            row['year'], 1, 1) + timedelta(row['day'] - 1), axis=1)
        df['observation_date'] = df['observation_date'].astype(str)
        df['observation_date'] = df['observation_date'].str[:10]
        result = df.groupby(['year', 'day', 'horizental', 'vertical']).apply(
            lambda x: x.loc[x['production_date'].idxmax()])
        result = df.reset_index(drop=True)
        result.drop(columns=['year', 'day'], inplace=True)
        result.drop(result[result['horizental'] == 15].index, inplace=True)
        return result

    def openFile(self, filepath: str,
             variable: str):
        hdf = SD(filepath)
        metadata = hdf.__getattr__('StructMetadata.0')
        gpp_dataset = hdf.select(variable)
        gpp_data = gpp_dataset.get()
        return gpp_data
    
    def createUnfilledMatrix(self, df):
        df['observation_date'] = pd.to_datetime(df['observation_date'])
        dfs = df.groupby(df['observation_date'])

        vs = df['vertical'].unique()
        total_vertical_grid = vs.max() - vs.min() + 1
        matrix_rows = total_vertical_grid*2400

        hs = df['horizental'].unique()
        total_horizental_grid = hs.max() - hs.min() + 1
        matrix_cols = total_horizental_grid*2400

        matrix = np.full((matrix_rows, matrix_cols), np.nan)
        return matrix, vs.min(), hs.min(), vs.max(), hs.max(),
    
    def retrieveProjection(self, LR_filepath: str,
                        variable: str):
        '''open h5 file,transform variable to array,
        retrieve projection and transform infomation'''
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
        proj = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} " \
            "+y_0={:0.4f} ".format('sinu',
                                projection_param[0],
                                projection_param[4],
                                projection_param[5],
                                projection_param[6],
                                projection_param[7])
        transform = [ul_pt[0], x_res, 0, ul_pt[1], 0, -y_res]
        LR_point = lr_pt
        return transform, proj, lr_pt
    
    def getOverAllTransform(self, df, vmax, hmax, unfilledMatrix):
        LR = df.loc[(df['vertical'] == vmax) & (df['horizental'] == hmax)]
        LR_transform, projection, lr_pt = self.retrieveProjection(LR_filepath=LR.iloc[0]['path'],
                                                                variable='Gpp_500m')
        rows, cols = unfilledMatrix.shape
        pixel_size_x = LR_transform[1]
        pixel_size_y = abs(LR_transform[5])
        lr_x, lr_y = lr_pt
        ul_x = lr_x - (cols * pixel_size_x)
        ul_y = lr_y + (rows * pixel_size_y)
        overall_transform = [ul_x, pixel_size_x, 0, ul_y, 0, -pixel_size_y]
        return overall_transform, projection
    
    def startWorking(self):
        file_info = self.retriveTilesInfomation()
        df = file_info.loc[file_info['observation_date'] == '2020-08-28']
        self.unfilledMatrix, vmin, hmin, vmax, hmax = self.createUnfilledMatrix(df)
        total = df.shape[0]
        for index, row in tqdm(df.iterrows(), total=total):
            path = row['path']
            v = row['vertical']
            h = row['horizental']
            matrix = self.openFile(filepath=path,
                                    variable='Gpp_500m')
            rows_index_range = ((v - vmin)*2400, (v+1 - vmin)*2400)
            cols_index_range = ((h - hmin)*2400, (h+1 - hmin)*2400)
            self.unfilledMatrix[rows_index_range[0]:rows_index_range[1],
                        cols_index_range[0]:cols_index_range[1]] = matrix
        self.data_ready_signal.emit(self.unfilledMatrix)


class TilesViewThread(QObject):
    request_draw_signal = Signal(list)
    def  __init__(self, paths)->None:
        super().__init__()
        self.paths = paths
    
    def retriveTilesInfomation(self) -> pd.DataFrame:
        '''return files infomation dataframe,[observation date,geometry horizental,
        geometry vertical,file path,product date]
            '''
        gpp_file_paths = self.paths
        file_paths = pd.DataFrame(gpp_file_paths, columns=['file_path'])
        result = file_paths['file_path'].str.split('.', expand=True)
        columns = ['_1', 'date', 'tail', '_2', '_3', '_4']
        result.columns = columns
        df = pd.DataFrame()
        df['horizental'] = result['tail'].str[1:3].astype(int)
        df['vertical'] = result['tail'].str[4:6].astype(int)
        df['year'] = result['date'].str[1:5].astype(int)
        df['day'] = result['date'].str[5:8].astype(int)
        df.dropna(inplace=True)
        df['path'] = file_paths['file_path']
        df['production_date'] = result['_3']
        df['observation_date'] = df.apply(lambda row: datetime(
            row['year'], 1, 1) + timedelta(row['day'] - 1), axis=1)
        df['observation_date'] = df['observation_date'].astype(str)
        df['observation_date'] = df['observation_date'].str[:10]
        result = df.groupby(['year', 'day', 'horizental', 'vertical']).apply(
            lambda x: x.loc[x['production_date'].idxmax()])
        result = df.reset_index(drop=True)
        result.drop(columns=['year', 'day'], inplace=True)
        # result.drop(result[result['horizental'] == 15].index, inplace=True)
        return result
    
    def getHV(self):
        df = self.retriveTilesInfomation()
        self.unique_combinations = df[['vertical', 'horizental']].drop_duplicates()
    
    def getPolygonData(self):
        """ Collect the data for the polygons without drawing them. """
        image_path = 'sinu_world.jpg'
        image = np.array(Image.open(image_path))  
        polygon_data = []
        pix = image.shape[0] / 18
        for v, h in zip(self.unique_combinations['vertical'],
                        self.unique_combinations['horizental']):
            polygon_data.append(((h) * pix, (v) * pix, pix, pix))
        return polygon_data
    
    def drawPolygons(self):
        image_path = 'sinu_world.jpg'
        image = np.array(Image.open(image_path))    
        ax = plt.gca()
        for h in self.hs:
            for v in self.vs:
                pix = image.shape[0]/18
                rect = patches.Rectangle(((h)*pix, (v)*pix),
                                        pix, pix,
                                        linewidth=1, edgecolor='r', facecolor='none')
                ax.add_patch(rect)
        
        plt.axis('off')
        plt.tight_layout()
        plt.draw()
        plt_image = np.frombuffer(plt.gcf().canvas.tostring_rgb(), dtype=np.uint8)
        plt_image = plt_image.reshape(plt.gcf().canvas.get_width_height()[::-1] + (3,))
        self.picture_finished_signal.emit(plt_image)
    
    def startWorking(self):
        self.getHV()
        polygon_data = self.getPolygonData()
        self.request_draw_signal.emit(polygon_data)
