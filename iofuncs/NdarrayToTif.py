from rasterio.transform import from_origin
from rasterio.io import MemoryFile
import os
import rasterio
from rasterio import Affine
import numpy as np


def ndarrayWriteInMemTiffile(lon_arr, lat_arr, data ,nodata=-9999):
    x_tl = lon_arr[0]
    y_tl = lat_arr[0]
    pixel_width = lon_arr[1] - lon_arr[0]
    pixel_height = lat_arr[1] - lat_arr[0]
    transform = from_origin(x_tl, y_tl, pixel_width, -pixel_height)

    with MemoryFile() as memfile:
        with memfile.open(driver='GTiff', height=lat_arr.shape[0], width=lon_arr.shape[0], count=1,
                          dtype=data.dtype, transform=transform, crs='EPSG:4326', nodata=nodata) as dst:
            dst.write(data, 1)
        return memfile.read()


def ndarraySaveAsTiff(data:np.ndarray, folder_path:str, file_name:str,
                      lon_arr:np.ndarray, lat_arr:np.ndarray,
                      FILLVALUE:int|float=-9999):
    '''
    data:np.ndarray
    folder_path:folder to input,will be created if not exists
    file_name:file base name
    grid_info:[start_lon, end_lon, start_lat, end_lat, grid_size](grid:2d array like)
    return:None
    describe:save a ndarray into .tif file
    '''
    folder = os.path.exists(folder_path)
    if not folder:
        os.makedirs(folder_path)
    file = os.path.join(folder_path, file_name)
    height, width = data.shape
    count = 1
    dtype = data.dtype
    lon_arr = np.sort(lon_arr)
    lat_arr = np.sort(lat_arr)
    x_res = lon_arr[1] - lon_arr[0]
    y_res = lat_arr[1] - lat_arr[0]
    transform = Affine(x_res, 0, lon_arr[0], 0, -y_res, lat_arr[-1])
    with rasterio.open(
        file, 'w',
        driver='GTiff',
        height=height,
        width=width,
        count=count,
        dtype=dtype,
        crs='EPSG:4326',
        transform=transform,
        nodata=FILLVALUE,
        compress='LZW'
    ) as dst:
        dst.write(data, 1)
