import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import rasterio


def listFolderFiles(folder:str, len_:int=None)->list:
    '''
    folder:folder path
    return:file paths which contained in the folder
    describe:
    '''
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if isinstance(len_, int):
        files = files[:len_]
    return  files


def retriveTilesInfomation(folder_path) -> pd.DataFrame:
    '''return files infomation dataframe,[observation date,geometry horizental,
    geometry vertical,file path,product_id]
        '''
    file_paths = listFolderFiles(folder_path)
    pattern = r"""
    .*?                # 固定前缀
    (\d{4})            # 年份捕获组 (2024)
    (\d{3})            # 年积日捕获组 (321)
    \.h(\d+)v(\d+)     # 水平/垂直格网捕获组 (h15v01)
    \.061\.            # 固定版本号
    (\d{13,14})        # 制作编号捕获组 (2024337170114)
    \.hdf$             # 文件后缀
    """
    years = []
    days = []
    hs= []
    vs = []
    production = []
    for path in file_paths:
        match = re.search(pattern, path, re.VERBOSE)
        if match:
            year, doy, h, v, product_id = match.groups()
            years.append(int(year))
            days.append(int(doy))
            hs.append(int(h))
            vs.append(int(v))
            production.append(int(product_id))
    df = pd.DataFrame([file_paths, years, days, hs, vs, production]).T
    df.columns = ['path', 'year', 'day', 'horizental', 'vertical', 'production']
    df['observation_date'] = df.apply(lambda row: datetime(
        int(row['year']), 1, 1) + timedelta(int(row['day']) - 1), axis=1)
    df['observation_date'] = df['observation_date'].astype(str)
    df['observation_date'] = df['observation_date'].str[:10]
    result = df.groupby(['year', 'day', 'horizental', 'vertical']).apply(
        lambda x: x.loc[x['production'].idxmax()])
    result = df.reset_index(drop=True)
    # result.drop(result[result['h'] == 15].index, inplace=True)
    return result


def retriveFileInfomation(folder_path, pattern = r"\d{4}-\d{2}-\d{2}", path_name='path'):
    file_paths = listFolderFiles(folder_path)
    dates = []
    for file_path in file_paths:
        match = re.search(pattern, file_path)
        if match:
            date = match.group()
            dates.append(date)
    df = pd.DataFrame([file_paths, dates]).T
    df.columns = [path_name, 'date']
    df['date'] = pd.to_datetime(df['date'])
    return df


def readTifAsNdarray(path, mask_range=None, scaler=None):
    with rasterio.open(path) as ds:
        data = ds.read(1)
        data = np.ma.array(data)
        if scaler:
            data = data / scaler
        if mask_range:
            data = np.ma.masked_outside(data, mask_range[0], mask_range[1])
    return data


def loadNpyFile(path, mask_range=None):
    data = np.load(path, allow_pickle=True)
    if mask_range:
        return np.ma.masked_outside(data , mask_range[0], mask_range[1])
    else:
        return data