from osgeo import gdal, osr
import numpy as np
import os
import tempfile


class Mosaic:
    def __init__(self, input_files: list, batch_size=3):
        self.input_files = input_files
        self.batch_size = batch_size
        self.temp_dir = tempfile.TemporaryDirectory()
        self._validate_inputs()
        
        # 初始化基准参数
        self._init_base_parameters()


    def _validate_inputs(self):
        """验证输入文件有效性"""
        if not self.input_files:
            raise ValueError("输入文件列表不能为空")
            
        exts = {os.path.splitext(f)[1].lower() for f in self.input_files}
        if len(exts) > 1:
            raise ValueError(f"混合文件类型: {exts}")


    def _init_base_parameters(self):
        """从第一个文件获取基准参数"""
        sample_ds = gdal.Open(self.input_files[0])
        self.projection = sample_ds.GetProjection()
        self.geotransform = sample_ds.GetGeoTransform()
        self.dtype = gdal.GetDataTypeName(sample_ds.GetRasterBand(1).DataType)
        sample_ds = None


    def _create_temp_dataset(self, files):
        """创建内存中的临时数据集"""
        vrt_path = os.path.join(self.temp_dir.name, "temp.vrt")
        vrt_ds = gdal.BuildVRT(vrt_path, files)
        return vrt_ds


    def _process_batch(self, batch_files, output_path):
        """处理单个批次"""
        # 创建虚拟数据集
        vrt_ds = self._create_temp_dataset(batch_files)
        
        # 配置优化参数
        warp_options = gdal.WarpOptions(
            format="GTiff",
            # outputBounds=[73.0, 34.0, 96.0, 49.0],
            xRes=0.001,
            yRes=0.001,
            resampleAlg="cubic",
            dstNodata=0,
            multithread=True,
            warpMemoryLimit=6 * 1024*1024*1024  # 限制内存使用6GB
        )
        
        # 执行批处理
        batch_ds = gdal.Warp(output_path, vrt_ds, options=warp_options)
        batch_ds.FlushCache()
        return output_path


    def smart_mosaic(self, output_path):
        """智能分批拼接"""
        temp_results = []
        
        # 分批次处理
        for i in range(0, len(self.input_files), self.batch_size):
            batch_files = self.input_files[i:i+self.batch_size]
            temp_path = os.path.join(self.temp_dir.name, f"batch_{i//self.batch_size}.tif")
            self._process_batch(batch_files, temp_path)
            temp_results.append(temp_path)
            
            # 内存优化：每处理3个批次合并一次中间结果
            if len(temp_results) >= 3:
                merged_path = os.path.join(self.temp_dir.name, f"merged_{i}.tif")
                self._merge_intermediate(temp_results, merged_path)
                temp_results = [merged_path]

        # 合并最终中间结果
        self._merge_intermediate(temp_results, output_path)
        
        # 清理资源
        self.temp_dir.cleanup()
        return output_path


    def _merge_intermediate(self, input_paths, output_path):
        """合并中间结果"""
        if len(input_paths) == 1:
            os.rename(input_paths[0], output_path)
            return
        
        vrt_path = os.path.join(self.temp_dir.name, "merge.vrt")
        vrt_ds = gdal.BuildVRT(vrt_path, input_paths)
        
        warp_options = gdal.WarpOptions(
            format="GTiff",
            creationOptions=["BIGTIFF=YES", "TILED=YES", "COMPRESS=LZW"],
            multithread=True
        )
        
        merged_ds = gdal.Warp(output_path, vrt_ds, options=warp_options)
        merged_ds = None
        vrt_ds = None


if __name__ == "__main__":
    import sys
    sys.path.append('iofuncs')
    import funcs
    mosaic = Mosaic(
    input_files=funcs.listFolderFiles('test_tif_mosiac', len_=5),
    batch_size=3
    )
    mosaic.smart_mosaic("final_mosaic.tif")