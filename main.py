from constants import Path, BPLUT, factor
from iofuncs import funcs
import numpy as np
from utils import TemporalDownSample
import os
from tqdm.auto import tqdm
import logging
from utils import MapPlot
'''
Path: 文件路径
BPLUT: 各种类型植被呼吸参数:"SLA" eg: {
        "ENF": 14.1, "EBF": 25.9, "DNF": 15.5, "DBF": 21.8, "MF": 21.5,
        "CShrub": 9.0, "OShrub": 11.5, "WSavanna": 27.4, "Savanna": 27.1,
        "Grass": 37.5, "Crop": 30.4
    }
factor: 缩放参数
funcs: 文件读写函数
TemporalDownSample: 时间重采样函数
'''

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NPPCalculator:
    def __init__(self, land_type_path):
        self.param_types = ['SLA', 'froot_leaf_ratio', 'livewood_leaf_ratio',
                'leaf_mr_base', 'froot_mr_base', 'livewood_mr_base']
        self.land_type = funcs.readTifAsNdarray(land_type_path)
        self._load_parameters()
        self.max_mass_leaf = None
        self._validate_shapes()


    def _load_parameters(self):
        """加载所有需要的生物参数
        将_get_parameter(self, param_type):返回值赋予param变量 eg:
        leaf_mr_base = [[0.00604,...]](np.ndarray)
        """ 
        for param in self.param_types:
            setattr(self, param.lower(), self._get_parameter(param))


    def _get_parameter(self, param_type):
        """向量化参数获取
        将土地类型二维数据替换为生物参数矩阵 eg:
        [[1,...]] -> [[0.00604,...]] 1代表常绿针叶林
        """
        param_map = {}
        for land_code in range(17):
            land_type = BPLUT.LANDTYPE.get(land_code)
            param_value = BPLUT.BPLUT_TABLE[param_type].get(land_type, 0)
            param_map[land_code] = param_value
        
        return np.vectorize(param_map.get)(self.land_type).astype(np.float32)


    def _validate_shapes(self):
        """验证所有参数形状一致性"""
        base_shape = self.land_type.shape
        for param in self.param_types:
            param = param.lower()
            if getattr(self, param).shape != base_shape:
                raise ValueError(f"Parameter {param} shape mismatch")


    def calculate_rm(self, mass, base, tavg, q_10_mr=None):
        """计算维持呼吸
        Rm = mass * base * (Q\_10\_mr)^{(tavg-20)/10)}
        """
        q_10_mr = 2.0 if q_10_mr is None else q_10_mr
        return mass * base * np.power(q_10_mr, (tavg-20)/10)


    def process_dataset(self, result_df):
        """处理整个数据集"""
        # 第一阶段：计算最大叶生物量
        logger.info("Calculating maximum leaf mass...")
        with tqdm(total=len(result_df), desc="Phase 1/2") as pbar:
            for _, row in result_df.iterrows():
                self._update_max_mass_leaf(row)
                pbar.update(1)
        
        # 第二阶段：计算NPP
        logger.info("Calculating NPP...")
        with tqdm(total=len(result_df), desc="Phase 2/2") as pbar:
            for _, row in result_df.iterrows():
                self._process_row(row)
                pbar.update(1)


    def _update_max_mass_leaf(self, row):
        """更新最大叶生物量
        mass = \frac{lai}{SLA}
        """
        lai = funcs.readTifAsNdarray(
            path=row['lai'], 
            mask_range=(0, 20),
        )
        current_mass = lai / self.sla
        current_mass = np.nan_to_num(current_mass, nan=0, posinf=0, neginf=0)
        
        if self.max_mass_leaf is None:
            self.max_mass_leaf = current_mass
        else:
            np.maximum(self.max_mass_leaf, current_mass, out=self.max_mass_leaf)


    def _safe_divide(self, data, para):
        """确保para不为0"""
        assert para.any() != 0
        return data / para


    def _process_row(self, row):
        """处理单行数据"""
        try:
            #读取gpp数据
            gpp = funcs.readTifAsNdarray(
                path=row['gpp'],
                mask_range=[0, 10],
            )

            #读取lai数据
            lai = funcs.readTifAsNdarray(
                path=row['lai'],
                mask_range=(0, 20),
            )

            #读取温度数据 ℃
            temp = funcs.loadNpyFile(
                path=row['tem'],
                mask_range=(0, 1000)
            ) - 273.15

            # 生物量计算
            # mass_leaf = \frac{lai}{SLA}
            # mass_livewood = max_mass_leaf * livewood_leaf_ratio, 
            # mass_livewood生长较慢，随叶面积指数变化不敏感，用mass_leaf最大值估计mass_livewood
            # mass_fineroot = mass_leaf * froot_leaf_ratio
            mass_leaf = self._safe_divide(lai, self.sla)
            mass_livewood = self.max_mass_leaf * self.livewood_leaf_ratio
            mass_fineroot = mass_leaf * self.froot_leaf_ratio
            
            # 呼吸计算
            rm_leaf = self.calculate_rm(mass_leaf, self.leaf_mr_base, temp, 3.32-0.046*temp)
            rm_livewood = self.calculate_rm(mass_livewood, self.livewood_mr_base, temp)
            rm_fineroot = self.calculate_rm(mass_fineroot, self.froot_mr_base, temp)
            # 总呼吸消耗计算
            total_rm = rm_leaf + rm_livewood + rm_fineroot
            total_rm = total_rm * 8
            # NPP计算
            # 应用公式: NPP = 0.8 \times (GPP-total_rm)
            # GPP为8天数据, Rm * 8计算8天呼吸消耗, 再计算8天NPP
            # 取0和NPP的最大值
            print(total_rm.max())
            print(gpp.max())
            npp = np.clip(0.8 * (gpp - total_rm), 0, None)
            # 保存文件
            self._save_result(npp.filled(np.nan), row['date'])
            
        except Exception as e:
            logger.error(f"Error processing {row['date']}: {str(e)}")
            raise


    def _save_result(self, npp, date):
        """保存结果文件"""
        os.makedirs(Path.NPP_TEST_DIR, exist_ok=True) # 创建文件夹
        date_str = date.strftime('%Y-%m-%d') #数据日期
        output_path = os.path.join(Path.NPP_TEST_DIR, f'{date_str}.npy') #文件路径
        np.save(output_path, npp.astype(np.float32))
        logger.debug(f"Saved: {output_path}")


def main():
    calculator = NPPCalculator(Path.LANDTYPE_PATH) #初始化计算器, 加载土地类型, 土地类型对应参数
    lai_info = funcs.retriveFileInfomation(folder_path=Path.LAI_DOWNSAMPLE_DIR, path_name='lai') #获取lai文件路径及数据日期
    gpp_info = funcs.retriveFileInfomation(folder_path=Path.GPP_DOWNSAMPLE_DIR_VERSION_2, path_name='gpp') #获取gpp文件路径及数据日期
    
    if not os.path.exists(Path.TEMPERATURE_8DAY_DOWNSAMPLE_DIR):
        tem_info = funcs.retriveFileInfomation(Path.TEMPERATURE_DOWNSAMPLE_DIR) #获取tem(1day)文件路径及日期
        TemporalDownSample.temporalDownSample(tem_info, Path.TEMPERATURE_8DAY_DOWNSAMPLE_DIR) #将时间分辨率为1d的tem转为8day, 取均值
     
    tem_info = funcs.retriveFileInfomation(folder_path=Path.TEMPERATURE_8DAY_DOWNSAMPLE_DIR, path_name='tem') #获取tem(8day)文件路径及数据日期
    result_df = lai_info.merge(gpp_info, on='date').merge(tem_info, on='date') #按日期对齐文件路径
    calculator.process_dataset(result_df) #df行遍历, 读取数据并计算


if __name__ == "__main__":
    main()

    