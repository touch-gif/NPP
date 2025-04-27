import netCDF4
import os
import re
import pandas as pd
import numpy as np


class Reader:
    """MODIS H4文件读取类
    
    功能：
    - 打开数据集
    - 获取投影信息、transform
    - 获取变量描述
    
    Attributes:
        proj (str): pro4字符串
        transfrom (list): [ul_pt[0], x_res, 0, ul_pt[1], 0, -y_res]
        var (np.ndarray): 变量数据
    """
    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            raise OSError("file doesnot exit")
        self.dataset = netCDF4.Dataset(self.path)


    def retrieveProjection(self):
        metadata = str(self.dataset)
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
        self.proj = "+proj={} +R={:0.4f} +lon_0={:0.4f} +lat_0={:0.4f} +x_0={:0.4f} " \
            "+y_0={:0.4f} ".format('sinu',
                                projection_param[0],
                                projection_param[4],
                                projection_param[5],
                                projection_param[6],
                                projection_param[7])
        self.transform = [ul_pt[0], x_res, 0, ul_pt[1], 0, -y_res]
        self.lr_pt = lr_pt


    def showVariables(self, file_path="hdf_file_describe.txt", dataset=None, indent=0):
        def write_info(dataset, file, indent_level):
            prefix = "  " * indent_level
            group_name = dataset.path if dataset.path != "/" else "Root"
            file.write(f"{prefix}Group: {group_name}\n")
            if dataset.variables:
                file.write(f"{prefix}  Variables:\n")
                for var_name, var in dataset.variables.items():
                    file.write(f"{prefix}    {var_name}: Shape={var.shape}, Dtype={var.dtype}\n")
                    if var.ncattrs():
                        file.write(f"{prefix}      Attributes:\n")
                        for attr in var.ncattrs():
                            file.write(f"{prefix}        {attr}: {var.getncattr(attr)}\n")

            if dataset.ncattrs():
                file.write(f"{prefix}  Global Attributes:\n")
                for attr in dataset.ncattrs():
                    file.write(f"{prefix}    {attr}: {dataset.getncattr(attr)}\n")

            if hasattr(dataset, 'groups') and dataset.groups:
                for group_name, group in dataset.groups.items():
                    write_info(group, file, indent_level + 1)
        absolute_file_path = os.path.abspath(file_path)
        with open(file_path, 'w') as f:
            target_dataset = dataset if dataset else self.dataset
            write_info(target_dataset, f, indent)
            print(f'variables file saved at: {absolute_file_path}')


    def read2DVariable(self, variable, print_detile=False, valid_range=[0, 100]):
        try:
            var_obj = self.dataset.variables[variable]
        except KeyError as e:
            print('variables not found:', e)
        # scale_factor = getattr(var_obj, "scale_factor", 1.0)  
        # add_offset = getattr(var_obj, "add_offset", 0.0)  
        # fill_value = getattr(var_obj, "_FillValue", None)  
        self.var = var_obj[:]
        # if fill_value is not None:
        #     self.var = np.ma.masked_equal(self.var, fill_value)
        
        if print_detile:
            if np.ma.is_masked(self.var):
                print("掩码数组（包含缺失值）")
                print(f"填充值: {self.var.fill_value}")
                print(f"掩码比例: {self.var.mask.mean() * 100:.2f}%")
            else:
                print("普通数组")
            print("前3行样例:")
            print(self.var[:3])
        self.var = np.ma.masked_outside(self.var, valid_range[0], valid_range[1])
        # self.var = self.var * scale_factor + add_offset

        return self.var


if __name__ == "__main__":
    h5reader = Reader(path='LAI\\Origin\\MCD15A2H.A2024329.h19v02.061.2024338044013.hdf')
    variable = "Lai_500m"
    h5reader.retrieveProjection()
    # h5reader.showVariables()
    h5reader.read2DVariable('Lai_500m')

