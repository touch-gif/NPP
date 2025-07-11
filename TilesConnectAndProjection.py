import pandas as pd
from datetime import datetime, timedelta
import os
import numpy as np
from tqdm import tqdm
# from pyhdf.SD import SD
import re
# from osgeo import gdal, osr


def listFilesFolder(folder_path) -> list:
    '''return files list'''
    gpp_file_paths = []
    npp_file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            try:
                if file[6] == '2':
                    gpp_file_paths.append(os.path.join(root, file))
                elif file[6] == '3':
                    npp_file_paths.append(os.path.join(root, file))
            except IndexError:
                pass
    return gpp_file_paths, npp_file_paths


def retriveTilesInfomation(folder_path) -> pd.DataFrame:
    '''return files infomation dataframe,[observation date,geometry horizental,
    geometry vertical,file path,product date]
        '''
    gpp_file_paths, npp_file_paths = listFilesFolder(folder_path)
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


def openFile(filepath: str,
             variable: str):
    hdf = SD(filepath)
    metadata = hdf.__getattr__('StructMetadata.0')
    gpp_dataset = hdf.select(variable)
    gpp_data = gpp_dataset.get()
    return gpp_data


def retrieveProjection(LR_filepath: str,
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


def createUnfilledMatrix(df):
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


def reprojection(data, projection, transform):
    driver = gdal.GetDriverByName('MEM')
    src_ds = driver.Create(
        "", data.shape[1], data.shape[0], 1, gdal.GDT_Int32)
    srs = osr.SpatialReference()
    srs.ImportFromProj4(projection)
    src_ds.SetProjection(srs.ExportToWkt())
    src_ds.SetGeoTransform(transform)
    src_ds.GetRasterBand(1).WriteArray(data)
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromEPSG(4326)
    dst_ds = gdal.Warp('', src_ds, dstSRS=dst_srs,
                       multithread=True,
                       format='MEM')
    dst_transform = dst_ds.GetGeoTransform()
    dst_band = dst_ds.GetRasterBand(1)

    data = dst_band.ReadAsArray()
    rows, cols = data.shape
    lon_arr = np.arange(cols) * dst_transform[1] + dst_transform[0]
    lat_arr = np.arange(rows) * dst_transform[5] + dst_transform[3]
    return data, lon_arr, lat_arr

def getOverAllTransform(df):
    LR = df.loc[(df['vertical'] == vmax) & (df['horizental'] == hmax)]
    LR_transform, projection, lr_pt = retrieveProjection(LR_filepath=LR.iloc[0]['path'],
                                                            variable='Gpp_500m')
    rows, cols = unfilledMatrix.shape
    pixel_size_x = LR_transform[1]
    pixel_size_y = abs(LR_transform[5])
    lr_x, lr_y = lr_pt
    ul_x = lr_x - (cols * pixel_size_x)
    ul_y = lr_y + (rows * pixel_size_y)
    overall_transform = [ul_x, pixel_size_x, 0, ul_y, 0, -pixel_size_y]
    return overall_transform, projection

if __name__ == '__main__':
    file_info = retriveTilesInfomation(folder_path='GPPTilesData\\Origin')
    df = file_info.loc[file_info['observation_date'] == '2020-08-28']
    unfilledMatrix, vmin, hmin, vmax, hmax = createUnfilledMatrix(df)
    total = df.shape[0]
    for index, row in tqdm(df.iterrows(), total=total):
        path = row['path']
        v = row['vertical']
        h = row['horizental']
        matrix = openFile(filepath=path,
                          variable='Gpp_500m')
        rows_index_range = ((v - vmin)*2400, (v+1 - vmin)*2400)
        cols_index_range = ((h - hmin)*2400, (h+1 - hmin)*2400)
        unfilledMatrix[rows_index_range[0]:rows_index_range[1],
                       cols_index_range[0]:cols_index_range[1]] = matrix
    
    overall_transform, projection = getOverAllTransform(df)
    z, lon_arr, lat_arr = reprojection(
        unfilledMatrix, projection, overall_transform)
    np.save('GPPTilesData\\GPP_2020-08-23.npy', z)
    