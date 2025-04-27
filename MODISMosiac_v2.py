import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

from utils import Reprojection
from iofuncs import H5FileReader, NdarrayToTif
from constants import Path
from iofuncs.funcs import retriveTilesInfomation


INPUT_DIR = Path.LAI_DOWNLOAD_DIR
OUTPUT_DIR = 'Lai_500m'
VAR = 'Lai_500m'
VALID_RANGE = (0, 200)
FILLVALUE = -9999
WORKERS = 4 


def create_unfilled_matrix(vmin: int, vmax: int, hmin: int, hmax: int) -> np.ndarray:
    """创建未填充矩阵"""
    rows = (vmax - vmin + 1) * 2400
    cols = (hmax - hmin + 1) * 2400
    return np.full((rows, cols), FILLVALUE, dtype=np.float32)


def get_overall_transform(matrix_shape: Tuple[int, int], transform: tuple, lr_pt: tuple) -> tuple:
    """计算整体投影变换参数"""
    rows, cols = matrix_shape
    pixel_size_x = transform[1]
    pixel_size_y = abs(transform[5])
    ul_x = lr_pt[0] - (cols * pixel_size_x)
    ul_y = lr_pt[1] + (rows * pixel_size_y)
    return (ul_x, pixel_size_x, 0, ul_y, 0, -pixel_size_y)


def process_single_date(date_group: Tuple[str, pd.DataFrame]) -> bool:
    """处理单个日期的数据"""
    date, df = date_group
    try:
        # 计算行列范围
        vmin, vmax = df['vertical'].min(), df['vertical'].max()
        hmin, hmax = df['horizental'].min(), df['horizental'].max()
        
        # 初始化矩阵
        matrix = create_unfilled_matrix(vmin, vmax, hmin, hmax)
        projection_info = {}

        # 遍历所有文件
        for _, row in df.iterrows():
            # 读取数据
            ds = H5FileReader.Reader(row['path'])
            ds.read2DVariable(VAR)
            data = ds.var.filled(FILLVALUE)
            
            # 计算偏移量
            v, h = row['vertical'], row['horizental']
            y_slice = slice((v - vmin)*2400, (v - vmin + 1)*2400)
            x_slice = slice((h - hmin)*2400, (h - hmin + 1)*2400)
            
            # 填充数据
            matrix[y_slice, x_slice] = data
            
            # 收集投影信息
            if v == vmax and h == hmax:
                ds.retrieveProjection()
                projection_info = {
                    'transform': ds.transform,
                    'proj': ds.proj,
                    'lr_pt': ds.lr_pt
                }

        # 执行重投影
        projector = Reprojection.ReProjection(
            data=matrix,
            projection=projection_info['proj'],
            transform=get_overall_transform(
                matrix.shape,
                projection_info['transform'],
                projection_info['lr_pt']
            )
        )
        projector.reproject()
        
        # 保存结果
        NdarrayToTif.ndarraySaveAsTiff(
            data=projector.reprojected_data[0],
            folder_path=OUTPUT_DIR,
            file_name=f'MOD_{VAR}_{date}.tif',
            lon_arr=projector.reprojected_data[1],
            lat_arr=projector.reprojected_data[2],
            FILLVALUE=FILLVALUE,
        )
        return True
    
    except Exception as e:
        print(f"Error processing {date}: {str(e)}")
        import traceback; traceback.print_exc()
        return False


if __name__ == "__main__":
    file_info = retriveTilesInfomation(INPUT_DIR)
    filtered = file_info[
        (file_info['year'] >= 2020) &
        (file_info['year'] < 2021) &
        (file_info['vertical'].between(3, 7)) &
        (file_info['horizental'].between(22, 27))
    ]
    daily_groups = list(filtered.groupby('observation_date'))
    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(process_single_date, group) for group in daily_groups]
        with tqdm(total=len(futures), desc="Processing Dates") as pbar:
            for future in as_completed(futures):
                future.result()
                pbar.update(1)