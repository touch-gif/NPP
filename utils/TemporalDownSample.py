import pandas as pd
import numpy as np
from constants import Path
import os
import rasterio


def temporalDownSample(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = df.sort_values('date').reset_index(drop=True)
    output_data = []
    grouped = df.groupby(pd.Grouper(key='date', freq='8D'))
    for window_start, group_df in grouped:
        if group_df.empty:
            continue
        sum_array = None
        valid_count = 0
        for path in group_df['path']:
            try:
                with rasterio.open(path) as ds:
                    arr = ds.read(1)
                if sum_array is None:
                    sum_array = np.zeros_like(arr, dtype=np.float64)
                    array_shape = arr.shape
                if arr.shape != array_shape:
                    print(f"形状不匹配文件被跳过: {path}")
                    continue  
                sum_array += arr
                valid_count += 1
            except Exception as e:
                print(f"加载文件失败 {path}: {str(e)}")
                continue
        if valid_count > 0:
            mean_array = (sum_array / valid_count).astype(np.float32)
            output_filename = os.path.join(Path.TEMPERATURE_8DAY_DOWNSAMPLE_DIR, f"8d_mean_{window_start.strftime('%Y-%m-%d')}.npy")
            np.save(output_filename, mean_array)

