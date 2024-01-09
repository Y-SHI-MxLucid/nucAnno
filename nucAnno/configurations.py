import numpy as np

startIdx = 2  # 点标注层是从第几层开始的，影响产生最终总表和产生session数据的计算
# ——现在暂时没什么用处，因为程序会默认第0层是标注区域层，第1层是图像层，点标注层会固定从第2层开始。
# 但是不要动它。未来可能会加入额外的接口。


class LayoutConfig:
    text_size = 12  # 标注点label的大小
    text_translation = np.array([-8, 0])  # 标注点label相对于点中心的位移np.array([行位移, 列位移])
    default_color = 'red'  # 不使用randomColor时，标注点的默认颜色
    point_symbol = 'cross'  # 标注点的形状类型
    point_size = 8  # 标注点的大小
    sharpness = 1.0  # 点和label颜色的明艳度（同时影响饱和度和亮度）
    scaleF_XY = 1.75  # 图像的缩放倍数，用于从x_raw\y_raw换算导出表格里面的x, y值
    scaleF_Z = 100  # 图像的缩放倍数，用于从z_raw换算导出表格里面的z值
    marker_radius = 40  # 标注区域的半径
    excel_colors = ['#AAFAAA', '#78C878'] #生成excel表格里面各个组的颜色
