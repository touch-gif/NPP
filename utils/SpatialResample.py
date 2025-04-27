from osgeo import gdal, osr
import os
from pathlib import Path
from . Reprojection import ReProjection
import numpy as np
from functools import lru_cache
osr.DontUseExceptions() 


class UpSample(ReProjection):
    # 类级别缓存参考文件元数据
    _ref_cache = {}
    
    def __init__(self, data, projection=None, transform=None,
                ref_path:str=None, x_res=0.01, y_res=0.01,
                resample_alg='cubic'):
        super().__init__(data, projection, transform)
        self.x_res = x_res
        self.y_res = y_res
        self.resample_alg = resample_alg
        if ref_path:
            # 检查缓存是否存在
            if ref_path not in self._ref_cache:
                self._load_ref_metadata(ref_path)
            # 从缓存加载元数据
            meta = self._ref_cache[ref_path]
            self.__dict__.update(meta)
        else:
            self.output_bounds = None


    def _load_ref_metadata(self, ref_path):
        """加载参考文件元数据并缓存"""
        ref_ds = gdal.Open(ref_path)
        ref_proj = ref_ds.GetProjection()
        ref_geotrans = ref_ds.GetGeoTransform()
        ref_width = ref_ds.RasterXSize
        ref_height = ref_ds.RasterYSize
        
        meta = {
            'x_min': ref_geotrans[0],
            'y_max': ref_geotrans[3],
            'x_max': ref_geotrans[0] + ref_geotrans[1] * ref_width,
            'y_min': ref_geotrans[3] + ref_geotrans[5] * ref_height,
            'x_res': ref_geotrans[1],
            'y_res': abs(ref_geotrans[5]),
            'output_bounds': (
                ref_geotrans[0],
                ref_geotrans[3] + ref_geotrans[5] * ref_height,
                ref_geotrans[0] + ref_geotrans[1] * ref_width,
                ref_geotrans[3]
            )
        }
        self._ref_cache[ref_path] = meta

    # 单例模式内存数据集
    @lru_cache(maxsize=1)
    def _create_source_ds(self, shape, transform, projection):
        """缓存源数据集创建操作"""
        ds = gdal.GetDriverByName('MEM').Create('', shape[1], shape[0], 1, gdal.GDT_Float32)
        ds.SetProjection(projection)
        ds.SetGeoTransform(transform)
        return ds


    def resample(self):
        # 复用内存数据集
        source_ds = self._create_source_ds(
            self.array.shape, 
            self.transform,
            self.spatial_ref.ExportToWkt()
        )
        
        try:
            band = source_ds.GetRasterBand(1)
            band.WriteArray(self.array)
            band.FlushCache()

            # 固定参数预配置
            warp_opts = self._get_warp_options()
            
            # 执行重投影
            self.warped_ds = gdal.Warp('', source_ds, options=warp_opts)
        finally:
            band = None  # 释放波段引用


    @lru_cache(maxsize=1)
    def _get_warp_options(self):
        """缓存Warp配置参数"""
        return gdal.WarpOptions(
            format='MEM',
            outputBounds=self.output_bounds,
            outputType=gdal.GDT_Float32,
            cutlineDSName='xinjiang.json',
            xRes=self.x_res,
            yRes=self.y_res,
            srcNodata=-9999,
            multithread=True,
            warpMemoryLimit=6*1024*1024*1024,
            resampleAlg=self.resample_alg,
        )
    

    @property
    def resampled_data(self):
        if not hasattr(self, 'warped_ds'):
            raise RuntimeError("请先执行resample方法")
            
        self.warped_data = self.warped_ds.GetRasterBand(1).ReadAsArray()
        new_transform = self.warped_ds.GetGeoTransform()
        
        # 生成坐标数组
        cols = self.warped_data.shape[1]
        rows = self.warped_data.shape[0]
        self.lon_arr = np.arange(cols) * new_transform[1] + new_transform[0]
        self.lat_arr = np.arange(rows) * new_transform[5] + new_transform[3]
        return self.warped_data, self.lon_arr, self.lat_arr



if __name__ == "__main__":
    pass
        