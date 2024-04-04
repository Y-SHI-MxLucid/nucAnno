from functions import *
from autoAssign import *
from tabulous.widgets import SpreadSheet
from magicgui import magicgui
import os
import pathlib
import configurations

finalRes = pd.DataFrame()
datasheet = SpreadSheet()
viewer = napari.Viewer()
cachedImgPath = None
grpDict = {}
annoMap = None
knn_model = None

# 读入图像
@magicgui(
    target={'mode': 'rm'},
    call_button="Read Image"
)
def readImg(target: pathlib.Path):
    global cachedImgPath
    cachedImgPath = reader(viewer, targetFile=target)


# 自动计算标点
@magicgui(
    call_button="Assign Points",
)
def assignPoint(group_name: str, auto_assign: bool, dsCube_pixel_res = 25.0, x_pixel_res = 1.75*0.5, 
                y_pixel_res = 1.75*0.5, z_pixel_res = 100.0, random_color = True):
    global finalRes
    global grpDict
    global annoMap
    global knn_model
    grpDict = formatPoints(viewer, group_name, random_color, 
                           x_pixel_res, y_pixel_res, z_pixel_res, dsCube_pixel_res, auto_assign,
                           layout_config=configurations.LayoutConfig, grpDict = grpDict, 
                           annoMap = annoMap,knn_model = knn_model)
    finalRes = generateResTable(viewer, True, configurations.LayoutConfig, datasheet)
    updateShape(viewer, layout_config=configurations.LayoutConfig, datasheet=datasheet)
    


# 得到该层标注点的Feature
@magicgui(
    call_button="Get Feature"
)
def getSheet():
    linkFeatures(viewer, datasheet)


# 在可交互表格中更改Feature信息之后，按这个键改变点的标注状态
@magicgui(
    call_button="Update Feature"
)
def updateSheet(proof_read: bool):
    if not proof_read:
        linkFeatures(viewer, datasheet, update=True)
        global finalRes
        finalRes = generateResTable(viewer, True, configurations.LayoutConfig, datasheet)
    else:
        finalRes = linkFeatures(viewer, datasheet, update=True)


# 生成各个层的总体Feature数据，用于导出标注数据。如果点选getReviewer则同时产生一个Reviewer图层
@magicgui(
    call_button="Generate Result"
)
# def generateRes(getReviewer = True): 现在默认getReviewer，不提供选项
def generateRes():
    global finalRes
    global datasheet
    finalRes = generateResTable(viewer, True, configurations.LayoutConfig, datasheet)


# 保存结果到Excel文件
@magicgui(
    save_prefix={'mode': 'w'},
    call_button="Save Result"
)
def saveRes(save_prefix: pathlib.Path):
    prefix = str(save_prefix)
    '''
    if os.path.isdir(prefix):
        finalRes.to_excel('{}/results.xlsx'.format(prefix), index=False)
    else:
        if prefix.endswith('.xlsx'):
            finalRes.to_excel(prefix, index=False)
        else:
            finalRes.to_excel('{}.xlsx'.format(prefix), index=False)
    '''
    if os.path.isdir(prefix):
        fillExcel(finalRes, '{}/results.xlsx'.format(prefix), configurations.LayoutConfig)
    else:
        if prefix.endswith('.xlsx'):
            fillExcel(finalRes, prefix, configurations.LayoutConfig)
        else:
            fillExcel(finalRes, '{}.xlsx'.format(prefix), configurations.LayoutConfig)


# 保存当前Session
@magicgui(
    save_prefix={'mode': 'w'},
    call_button="Save Session"
)
def saveSession(save_prefix: pathlib.Path):
    prefix = str(save_prefix)
    if not prefix.endswith('.ncas'):  # ncas：Napari Clone Annotation Session
        prefix = '{}.ncas'.format(prefix)
    saveNprSession(viewer, cachedImgPath, configurations.startIdx, configurations.LayoutConfig, prefix)


# 读取已经保存的Session
@magicgui(
    load_path={'mode': 'r'},
    call_button="Load Session"
)
def loadSession(load_path: pathlib.Path, auto_image_load: bool):
    global grpDict
    global finalRes
    global cachedImgPath
    prefix = str(load_path)
    finalRes, cachedImgPath = loadNprSession(viewer, datasheet, prefix, auto_image_load)
    grpDict = getGroupDict(viewer)


# 保存标注结果到ImageJ ROI Zip
@magicgui(
    save_prefix={'mode': 'w'},
    roi_sample={'mode': 'r'},
    call_button="Save ROIZip"
)
def saveROIZip(save_prefix: pathlib.Path, roi_sample: pathlib.Path):
    prefix = str(save_prefix)
    if not prefix.endswith('.zip'):
        prefix = '{}.zip'.format(prefix)
    saveImageJROI(finalRes, roi_sample, prefix)


# 读入标注结果Excel表格并生成Reviewer图层
@magicgui(
    load_path={'mode': 'r'},
    call_button='Load Reviewer Layer'
)
def loadReviewer(load_path: pathlib.Path):
    global finalRes
    finalRes = generateResTable(viewer, True, configurations.LayoutConfig, datasheet, mode='file', loadSource=load_path)

# 重新整理各层的编号
@magicgui(
    call_button='Rearrange Group Idx'
)
def reArrangeLayer():
    global finalRes
    global datasheet
    global grpDict
    finalRes = reArrangeGrp(viewer, configurations.LayoutConfig, datasheet)
    finalRes = reArrangeGrp(viewer, configurations.LayoutConfig, datasheet)
    updateShape(viewer, layout_config=configurations.LayoutConfig, datasheet=datasheet)
    grpDict = getGroupDict(viewer)

# 生成自动分配标点脑区的KNN模型、读入映射到注释的JSON文件
@magicgui(
    anno_image_path={'mode': 'r'},
    anno_map_path={'mode': 'r'},
    call_button="Get Assigner Prepared"
)
def prepareAssigner(anno_image_path: pathlib.Path, anno_map_path: pathlib.Path, 
                    sampling_rate = 0.5, n_neighbors = 3, cpu_parallel = 4):
    global annoMap
    global knn_model
    annoImgPath = str(anno_image_path)
    annoMapPath = str(anno_map_path)
    annoMap, knn_model = get_Trained_Model(annoImgPath, annoMapPath, 
                                           spl_rate = sampling_rate, n_neighbors = n_neighbors, 
                                           cpu_parallel = cpu_parallel)
    

# 构建整个软件界面的Layout，加载各个gui要素
dsWidgetList = [
    (assignPoint, 'Assign Points'),
    (getSheet, 'Get Feature'),
    (updateSheet, 'Update Feature'),
    (generateRes, "Generate Result"),
    (saveROIZip, "Save Result to Image ROI"),
    (saveRes, "Save Result to Excel"),
    (saveSession, "Save Annotation Session"),
    (loadSession, "Load Annotation Session"),
    (loadReviewer, "Load Reviewer Layer"),
    (reArrangeLayer, "Rearrange Group Index"),
    (prepareAssigner, "Prepare Assigner Model")
]
addWidgets(datasheet, dsWidgetList)
mainWidgetList = [
    (readImg, 'Read In Images'),
    (datasheet, 'Interative Form')]
addElements(viewer.window, mainWidgetList)
