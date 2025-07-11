import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import mapping, Polygon, Point, box
from functools import partial
import warnings
warnings.simplefilter('ignore')

def scencetoMap(x ,y):
    lon = 23.91+0.083636*(x-2703)
    lat = 22.05-0.08913*(y-1294)
    return lon, lat


def maptoScence(lon ,lat):
    x = (lon - 23.91) / 0.083636 + 2703
    y = (lat - 22.05) / (-0.08913) + 1294
    return x, y


def listFilesFolder(folder_path):
    '''return paths of sub-files'''
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths


def gridifyPolygon(area_:Polygon, cellsize_lon, cellsize_lat) -> gpd.GeoDataFrame:
    '''create boxes as geodateframe'''
    def gridifyPolygon_(area, cellsize_lon, cellsize_lat):
        minx, miny, maxx, maxy = area.bounds
        cellsize_lon = float(cellsize_lon)
        cellsize_lat = float(cellsize_lat)  
        x_coords = np.arange(minx, maxx, cellsize_lon)
        y_coords = np.arange(miny, maxy, cellsize_lat)
        grid_polygon = []
        for x in x_coords:
            for y in y_coords:
                cell = box(x, y, x + cellsize_lon, y + cellsize_lat)
                intersection = area.intersection(cell)
                if not intersection.is_empty:
                    grid_polygon.append(intersection)

        return grid_polygon

    try:
        gridify_func = partial(gridifyPolygon_, cellsize_lon=cellsize_lon, cellsize_lat=cellsize_lat)
        flattened_polygons = list(map(gridify_func, area_))
        flattened_polygons = [geom for sublist in flattened_polygons for geom in sublist]
        geo = gpd.GeoDataFrame(geometry=flattened_polygons)
    except:
        flattened_polygons = gridifyPolygon_(area_, cellsize_lon=cellsize_lon, cellsize_lat=cellsize_lat)
        geo = gpd.GeoDataFrame(geometry=flattened_polygons)
    return geo

def getPolygonsData(geo_df:gpd.GeoDataFrame, loncol:str, latcol:str, df:pd.DataFrame, signal:Signal)->list:
    '''tanslate geodf boxes to points and add index,digital data'''
    polygons_data = []
    concat_data = pd.DataFrame()
    total_files = geo_df.shape[0] 
    for index, row in geo_df.iterrows():
        polygon = row['geometry']
        centriod = polygon.centroid
        polygon_points = []
        box_ = gpd.GeoDataFrame(geometry=[polygon])
        data_contained_df = bindDataToPolygon(df=df,
                                              box=box_,
                                              loncol=loncol,
                                              latcol=latcol,
                                              index=index)       
        if polygon.geom_type == 'Polygon':
            polygon_points = [QPointF(x*100, -y*100) for x, y in polygon.exterior.coords]
        elif polygon.geom_type == 'Point':
            polygon_points = [QPointF(polygon.x*100, -polygon.y*100)]
        elif polygon.geom_type == 'LineString':
            polygon_points = [QPointF(x*100, -y*100) for x, y in polygon.coords]
        elif polygon.geom_type == 'MultiLineString':
            for ea in polygon:
                polygon_points.extend([QPointF(x*100, -y*100) for x, y in ea.coords])
        elif polygon.geom_type == 'MultiPolygon':
            for ea in polygon.geoms:
                for x, y in ea.exterior.coords:
                    polygon_points.append(QPointF(x*100, -y*100))
        polygons_data.append({
            'points': polygon_points,
            'index': index,
            'data':data_contained_df,
            'centriod':centriod
        })
        progress = int((index + 1) / total_files * 100)
        signal.emit(progress)
        concat_data = pd.concat([concat_data, data_contained_df], axis=0)
    return polygons_data, concat_data


def bindDataToPolygon(df, box, loncol, latcol, index):
    '''contained in getPolygonsData,bind digital data to polygon'''
    geometry = gpd.points_from_xy(df[loncol], df[latcol])
    points = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    data_contained_df = gpd.sjoin(points, box, predicate='within')
    data_contained_df.drop(columns=['index_right', 'geometry'], inplace=True)
    data_contained_df.columns = df.columns
    data_contained_df['rigion_index'] = index
    return data_contained_df
