import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
import cartopy.crs as ccrs
from rasterio.features import rasterize
import geopandas as gpd
import regionmask
import numpy as np
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from geopy.distance import geodesic
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from rasterio.transform import Affine
font_set = FontProperties(fname="C:\\Windows\\Fonts\\simsun.ttc", size=14)


class GeoPlotter:
    def __init__(self, lon_arr:np.ndarray, lat_arr:np.ndarray, font_path="C:\\Windows\\Fonts\\simsun.ttc",
                base_map_path="X:\\Modern_GUI_PyDracula_PySide6_or_PyQt6-master\\cn.json",
                province=None):
        self.font_prop = FontProperties(fname=font_path, size=14)
        self.base_map = gpd.read_file(base_map_path)
        if province:
            self.base_map = self.base_map.loc[self.base_map['name']==province]
            if len(self.base_map) == 0:
                raise KeyError 
        self.fig = None
        self.ax = None
        self.norm = None
        self.cmap = None
        self.lon_arr = np.sort(lon_arr)
        self.lat_arr = np.sort(lat_arr)
        x_res = self.lon_arr[1] - self.lon_arr[0]
        y_res = self.lat_arr[1] - self.lat_arr[0]
        self.transform = Affine(x_res, 0, self.lon_arr[0], 0, -y_res, self.lat_arr[0])

    def _setup_figure(self, figsize=(10, 8)):
        # 创建图形和坐标系
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(projection=ccrs.PlateCarree())
        self.ax.set_xlim(int(self.lon_arr[0]), int(self.lon_arr[-1]))
        self.ax.set_ylim(int(self.lat_arr[0]), int(self.lat_arr[-1]))
        self.ax.gridlines(
            draw_labels=True, 
            linewidth=0.3, 
            color='gray', 
            alpha=0, 
            linestyle='--'
        )

    def _apply_mask(self, data):
        try:
            height, width = data.shape
        except ValueError:
            data = data[0]
            height, width = data.shape
        mask = rasterize(
            shapes=self.base_map.geometry,
            out_shape=(height, width),
            transform=self.transform,
            fill=np.nan,
            default_value=1,
            dtype=np.float32 
            )
        # latitudes = np.arange(10, 60, grid_size)
        # longitudes = np.arange(40, 160, grid_size)
        # lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
        
        # mask = regionmask.mask_geopandas(
        #     self.base_map, 
        #     lon_grid, 
        #     lat_grid
        # ).values
        
        # mask = np.where(np.isfinite(mask), 1, np.nan)
        return data * mask

    def _add_colorbar(self, label, position=None):
        # 添加颜色条
        if position:
            cax = self.fig.add_axes(position)
            cb = plt.colorbar(
                self.ax.images[0], 
                cax=cax, 
                orientation='vertical',
                shrink=0.65, pad=0.1
            )
            cb.set_label(label, fontproperties=self.font_prop)
        else:
            cb = plt.colorbar(self.ax.images[0], shrink=0.65, pad=0.1)
            cb.set_label(label, fontproperties=font_set)
        return cb

    def _add_inset_map(self, data, position):
        # 添加插画地图
        ax_inset = self.fig.add_axes(
            position, 
            projection=ccrs.PlateCarree()
        )
        ax_inset.set_extent([104.5, 125, 0, 26])
        ax_inset.coastlines(linewidth=0.5)
        ax_inset.imshow(
            data, 
            cmap=self.cmap,
            extent=[40, 160, 10, 60],
            alpha=0.8,
            norm=self.norm
        )
        self.base_map.boundary.plot(
            ax=ax_inset, 
            color='red', 
            linewidth=0.3
        )

    def _add_scalebar(self):
        # 添加比例尺
        center = (35, 105)
        end = geodesic(kilometers=500).destination(center, bearing=90)
        delta_lon = end.longitude - center[1]
        
        scalebar = AnchoredSizeBar(
            self.ax.transData,
            delta_lon,
            '500 公里',
            loc='upper left',
            pad=0.2,
            color='black',
            frameon=True,
            size_vertical=1,
            fontproperties=self.font_prop
        )
        self.ax.add_artist(scalebar)

    def _add_annotation(self, text_dict):
        # 添加文字标注
          
        for config in text_dict:
            self.ax.text(
                config['x'], config['y'],
                config['text'],
                fontdict={'fontsize': 22},
                fontproperties=self.font_prop
            )

    def plot(self, data, output_path=None, colors=None, 
            vmin=None, vmax=None, text_config=None,
            colorbar_label=r'$XCO_2 /\times 10^{-6}$',
            colorbar=True,
            crop=False,
            insert=False,
            scale=False,
            boundary=False):
        """
        主绘图函数
        
        参数：
        data: 输入数据矩阵
        output_path: 输出路径str或list
        colors: 颜色列表
        vmin/vmax: 颜色标准化范围
        text_config: 文字配置字典
        colorbar_label: 色条标签
        colorbar: 是否显示色条
        crop: 是否掩膜其他区域数据
        insert: 是否插入画中画
        """
        # 数据预处理
        if crop:
            processed_data = self._apply_mask(data)
        else:
            processed_data = data
        
        # 颜色标准化
        self.norm = Normalize(vmin=vmin, vmax=vmax)
        if colors is not None:
            self.cmap = LinearSegmentedColormap.from_list("custom", colors)
        else:
            self.cmap = 'viridis'
        
        # 创建基础图形
        self._setup_figure()
        
        # 绘制主图
        self.ax.matshow(
            processed_data,
            cmap=self.cmap,
            extent=[self.lon_arr[0], self.lon_arr[-1], self.lat_arr[0], self.lat_arr[-1]],
            norm=self.norm
        )
        if boundary:
            self.base_map.boundary.plot(
                ax=self.ax, 
                color='black', 
                linewidth=0.2
            )
        self.ax.text(
            x=0.05, y=0.05, 
            s='审图号:GS(2024) 0650',
            fontproperties=self.font_prop,
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'),
            transform=self.ax.transAxes
        )
        # 添加附加元素
        if text_config:
            self._add_annotation(text_config)
            
        if colorbar:
            self._add_colorbar(colorbar_label)
            if insert:
                self._add_inset_map(processed_data, [0.5497, 0.2602, 0.2, 0.2])
        if not colorbar:
            if insert:
                self._add_inset_map(processed_data, [0.7052, 0.1802, 0.25, 0.25])
        if scale:
            self._add_scalebar()
        
        # 保存输出
        self._save_output(output_path)
        
        plt.close()

    def _save_output(self, output_path):
        # 统一保存逻辑
        if isinstance(output_path, str):
            paths = [output_path]
        elif isinstance(output_path, list):
            paths = output_path
        else:
            plt.show()
            return
            
        for path in paths:
            self.fig.savefig(
                path,
                bbox_inches='tight',
                pad_inches=0.2,
                dpi=600,
                transparent=True
            )


def colorBarPlot(vmin, vmax, color:list, label:str, output_path:list|str):
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = LinearSegmentedColormap.from_list("custom_cmap", color)

    fig = plt.figure(figsize=(10, 3))  # 调整高度参数控制颜色条厚度
    fig.subplots_adjust(left=0.1, right=0.9, bottom=0.4, top=0.6)  # 调整空白区域
    cax = fig.add_axes([0.1, 0.4, 0.8, 0.2])  # [左, 下, 宽, 高] 调整高度参数控制颜色条厚度


    cb = plt.colorbar(
        cm.ScalarMappable(norm=norm, cmap=cmap),
        cax=cax,
        orientation='horizontal'
    )

    cb.set_label(label, fontsize=14, labelpad=10)
    cb.ax.tick_params(labelsize=12)

    # plt.axis('off')
    if isinstance(output_path, str):
            paths = [output_path]
    elif isinstance(output_path, list):
        paths = output_path
    else:
        raise ValueError("输出路径需要是字符串或列表")
        
    for path in paths:
        fig.savefig(
            path,
            bbox_inches='tight',
            pad_inches=0.2,
            dpi=600
            )

