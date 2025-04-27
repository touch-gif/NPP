from osgeo import gdal, osr
import numpy as np
from typing import Union, Tuple
osr.DontUseExceptions() 


class ReProjection:
    """地理数据重投影处理类
    
    功能：
    - 支持从NumPy数组或TIFF文件初始化
    - 执行坐标系统重投影(默认转至WGS84)
    - 获取重投影后的数据和地理坐标信息
    - 可视化结果
    
    Attributes:
        warped_data (np.ndarray): 重投影后的数据数组
        lon_arr (np.ndarray): 经度坐标数组
        lat_arr (np.ndarray): 纬度坐标数组
    """
    
    def __init__(self, data: Union[np.ndarray, str], 
                 projection: str = None, 
                 transform: Tuple[float] = None):
        """初始化投影转换器
        
        Args:
            data: 输入数据(NumPy数组或TIFF文件路径)
            projection: 坐标系统(Proj4/WKT格式)
            transform: 地理变换参数元组
        """
        self._validate_input(data, projection, transform)
        self._init_spatial_reference()
        self.driver = gdal.GetDriverByName('MEM')
        # import geopandas as gpd
        # china = gpd.read_file("X:\\Modern_GUI_PyDracula_PySide6_or_PyQt6-master\\cn.json")
        # xinjiang = china[china['name'].str.contains("新疆")]
        # xinjiang.to_file("xinjiang.json", driver='GeoJSON')


    def _validate_input(self, data, projection, transform):
        """验证输入数据有效性"""
        if isinstance(data, np.ndarray):
            self._init_from_array(data, projection, transform)
        elif isinstance(data, str):
            self._init_from_tif(data)
        else:
            raise ValueError("输入数据类型必须为np.ndarray或文件路径字符串")


    def _init_from_array(self, data: np.ndarray, projection: str, transform: tuple):
        """从NumPy数组初始化"""
        if not (projection and transform):
            raise ValueError("使用数组初始化时必须提供projection和transform参数")
            
        self.array = data
        self.rows, self.cols = data.shape
        self.projection = projection
        self.transform = transform
        self.spatial_ref = osr.SpatialReference()
        self._init_spatial_reference()


    def _init_from_tif(self, tif_path: str):
        """从TIFF文件初始化"""
        try:
            dataset = gdal.Open(tif_path, gdal.GA_ReadOnly)
            if dataset is None:
                raise RuntimeError(f"无法打开文件：{tif_path}")
                
            self.projection = dataset.GetProjection()
            self.transform = dataset.GetGeoTransform()
            band = dataset.GetRasterBand(1)
            self.array = band.ReadAsArray()
            self.rows, self.cols = self.array.shape
        finally:
            # 确保释放GDAL数据集资源
            if 'dataset' in locals():
                dataset = None


    def _init_spatial_reference(self):
        """初始化空间参考系统"""
        self.spatial_ref = osr.SpatialReference()
        # 处理EPSG代码
        if self.projection.strip().upper().startswith('EPSG:'):
            epsg_code = int(self.projection.split(':')[1])
            result = self.spatial_ref.ImportFromEPSG(epsg_code)
            if result != 0:
                raise ValueError(f"无效的EPSG代码:{epsg_code}")
            return
        # 尝试解析为WKT
        result = self.spatial_ref.ImportFromWkt(self.projection)
        if result == 0:
            return
        # 尝试解析为Proj4
        result = self.spatial_ref.ImportFromProj4(self.projection)
        if result == 0:
            return
        # 尝试其他解析方式，如ESRI WKT等
        result = self.spatial_ref.ImportFromESRI([self.projection])
        if result == 0:
            return
        # 全部失败则抛出异常
        raise ValueError(f"无法解析投影参数：{self.projection}")


    def reproject(self, target_srs: str = 'EPSG:4326',
                  fillvalue=-9999) -> None:
        """执行重投影操作
        
        Args:
            target_srs: 目标坐标系(默认为WGS84)
        """
        # 创建内存数据集
        source_ds = self.driver.Create('', self.cols, self.rows, 1, gdal.GDT_Float32)
        try:
            source_ds.SetProjection(self.spatial_ref.ExportToWkt())
            source_ds.SetGeoTransform(self.transform)
            band = source_ds.GetRasterBand(1)
            band.WriteArray(self.array)
            band.FlushCache()
            
            # 配置重投影参数
            warp_opts = gdal.WarpOptions(
                format='MEM',
                dstSRS=target_srs,
                outputType=gdal.GDT_Float32,
                multithread=True,
                warpMemoryLimit=6*1024*1024*1024,
                dstNodata=fillvalue,
                srcNodata=-9999,
                cutlineDSName='xinjiang.json',
                cropToCutline=True,
            )
            
            # 执行重投影
            self.warped_ds = gdal.Warp('', source_ds, options=warp_opts)
        finally:
            # 确保释放中间资源
            source_ds = None


    @property
    def reprojected_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """获取重投影后的数据及地理坐标"""
        if not hasattr(self, 'warped_ds'):
            raise RuntimeError("请先执行reproject方法")
            
        self.warped_data = self.warped_ds.GetRasterBand(1).ReadAsArray()
        new_transform = self.warped_ds.GetGeoTransform()
        
        # 生成坐标数组
        cols = self.warped_data.shape[1]
        rows = self.warped_data.shape[0]
        self.lon_arr = np.arange(cols) * new_transform[1] + new_transform[0]
        self.lat_arr = np.arange(rows) * new_transform[5] + new_transform[3]
        
        return self.warped_data, self.lon_arr, self.lat_arr


    def save_as_tif(self, output_path:str) -> None:
        if output_path:
            tiff_driver = gdal.GetDriverByName('GTiff')
            out_ds = tiff_driver.CreateCopy(output_path, self.warped_ds, options=['COMPRESS=LZW'])
            out_ds = None


    def visualize(self, data=None) -> None:
        """可视化重投影结果
        
        Args:
            **kwargs: 传递给MapPlot的可选参数
        """
        from utils import MapPlot
        
        # if not hasattr(self, 'warped_data'):
        #     self.reprojected_data
        try:
            if not isinstance(data, np.ndarray):
                data = self.warped_data
        except AttributeError:
            self.reprojected_data
            data = self.warped_data

        plotter = MapPlot.GeoPlotter(
            lon_arr=self.lon_arr,
            lat_arr=self.lat_arr,
            province='新疆维吾尔自治区',
        )
        plotter.plot(data=data, colorbar=False
                     , crop=False, scale=False)