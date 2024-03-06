import napari
import numpy as np
import copy
# from napari.utils.notifications import show_info
import pandas as pd
import openpyxl  # 不用但必须得import
import xlsxwriter
from openpyxl.styles import PatternFill
#from openpyxl.styles.colors import RED, GREEN #AAFAAA #78C878
import skimage.io as io
from skimage.color import hsv2rgb
import pickle as pkl
import roiconvertor
from autoAssign import *

'''

'''

# ====主函数群部分====#
'''
说一点个人的想法：我觉得只有在layout脚本中才应该引入global变量，这里的所有函数都应该是通用的。这样后续维护会容易得多。
'''

# ====多用函数====#
def getCurrentLayer(viewer):  # 返回目前选取的图层信息
    name = viewer.layers.selection.active.name
    layer = viewer.layers.selection.active
    idx = viewer.layers.index(viewer.layers.selection.active)
    return name, idx, layer, layer.data


def updateLayer(layer):  # 刷新当前图层以正确显示标签和其他信息的更改
    if layer.visible == False:
        layer.visible = True
        layer.visible = False
    else:
        layer.visible = False
        layer.visible = True
    return


def decideColor(sharpness=1.0):
    hue = np.random.rand()  # 随机色调
    # sharpness是醒目的程度，也就是saturation/value值，越高颜色越鲜明
    rgb = (255 * hsv2rgb([[[hue, sharpness, sharpness]]])[0, 0, :]).astype('uint8')
    finalColor = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2]).upper()
    return finalColor

# 将图层特征表显示在交互式表格中，或根据表格修改的结果更新该图层的特征表
def linkFeatures(viewer, datasheet, update=False):
    _, _, layer, _ = getCurrentLayer(viewer)
    if not update:
        datasheet.data = layer.features
    else:
        layer.features = datasheet.data
        updateLayer(layer)
    return datasheet.data

# 向一个主widget(table)插入侧边widget
def addWidgets(table, widgetList):
    for widget in widgetList:
        table.add_side_widget(widget[0], name=widget[1])
    return


# 向主界面(napari.viewer.Window)插入侧边widget
def addElements(window, widgetList):
    for widget in widgetList:
        window.add_dock_widget(widget[0], name=widget[1])
    return

# 改变一个图层的位置
def moveLayer(viewer, layer, pos):
    swapL = copy.deepcopy(layer)
    viewer.layers.remove(layer)
    viewer.layers.insert(pos, swapL)

# 从已知图层列表中生成一个脑区名称和名称重复次数对应的词典
def getGroupDict(viewer, omit = None):
    
    grpDict = {}
    '''
    if not omit:
        lNs = [i.name for i in viewer.layers if i.name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points']]
    else:
        lNs = [i.name for i in viewer.layers if i.name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points', omit]]
    for name in lNs:
        grp = name[0: name.find('-')]
        if grp not in grpDict.keys():
            grpDict[grp] = 1
        else:
            grpDict[grp] = grpDict[grp] + 1
    '''
    for layer in viewer.layers:
        if layer.name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points', omit]:
            grp = layer.name[0: layer.name.find('-')]
            if grp not in grpDict.keys():
                grpDict[grp] = 1
            else:
                grpDict[grp] = grpDict[grp] + 1
    return grpDict


#====功能函数====#

def reader(viewer, targetFile, rgb=False):
    # 用于读入图像
    def resetContrast(layer):
        layer.contrast_limits = \
            [layer.data.min(), layer.data.max()]
        layer.gamma = 1
        layer.opacity = 1
        return

    imageStack = None
    if len(targetFile) > 1:  # 打开多个文件的情况
        fileList = [str(i) for i in targetFile]
        fileList.sort()
        testImg = io.imread(fileList[0], -1)
        testHeight, testWidth = testImg.shape
        testDtype = io.imread(fileList[0], -1).dtype
        testLayerNum = len(fileList)
        imageStack = np.zeros((testLayerNum, testHeight, testWidth), dtype=testDtype)
        for idx, file in enumerate(fileList):
            imageStack[idx, :, :] = io.imread(file)
    elif len(targetFile) == 1:  # 打开单个文件或Stack的情况
        imageStack = io.imread(str(targetFile[0]))
        if len(imageStack.shape) < 3:
            imageStack = np.expand_dims(imageStack, 0)

    viewer.add_shapes(name='Clone Marker')
    _ = viewer.add_image(imageStack, rgb=rgb, name='Image Stack')
    viewer.add_points(name='Reviewer')
    resetContrast(viewer.layers[-2])

    # return copy.deepcopy(imageStack)
    return


def formatPoints(viewer, groupName, randomColor, 
                 x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, autoAssign, 
                 layout_config, grpDict, annoMap, knn_model):
    # 用于给标记的点群赋予标签的主函数
    _, lidx, layer, data = getCurrentLayer(viewer)
    if not isinstance(layer, napari.layers.Points):
        print('It is not a point layer you selected')
        return
    if autoAssign:
        if not (annoMap and knn_model):
            print('Have not got annotation map and assigner model prepared. Use manaul.')
        else:
            groupName = get_Singlet_Assigned(x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, 
                                             offset = [0, 0, 0], coord = data[0:-1, :], 
                                             model = knn_model, annoMap = annoMap)
    groupMeta = copy.deepcopy(grpDict)
    if (layer.name.find('-') != -1 and layer.name[0: layer.name.find('-')] == groupName) or (not groupName):
        groupName = layer.name
    else:
        if groupName not in groupMeta.keys():
            groupMeta[groupName] = 1
            groupName = '{}-{}'.format(groupName, 1)
        else:
            groupMeta[groupName] = groupMeta[groupName] + 1
            groupName = '{}-{}'.format(groupName, groupMeta[groupName])


    try:
        prefix, idx = groupName.split('-')
    except ValueError:
        print('Failed to resolve group name, consider if you are providing names in good format.')
        return
    
    numPoints = data.shape[0] - 1
    realPointCoord = data[0:-1, 1:]
    refPointCoord = data[-1, 1:]
    pointDist = np.sqrt(np.sum(np.square(realPointCoord - refPointCoord), 1))
    pointIdx = np.argsort(pointDist)
    order = [0] * numPoints
    for i in range(numPoints):
        order[pointIdx[i]] = i + 1
    features = {
        '胞体编号': np.array(
            ['{}-{}-{:02d}-{:02d}'.format(prefix, int(idx), numPoints, order[i]) for i in range(numPoints)]),
        'x': data[0:-1, 2] * layout_config.scaleF_XY,
        'y': data[0:-1, 1] * layout_config.scaleF_XY,
        'z': data[0:-1, 0] * layout_config.scaleF_Z + 1,
        'Order': np.array(order),
        'x_raw': data[0:-1, 2],
        'y_raw': data[0:-1, 1],
        'z_raw': data[0:-1, 0],
        'Idx': np.array([int(idx)] * numPoints),
        'NumCell': np.array([numPoints] * numPoints),
        'Group': np.array([prefix] * numPoints), }

    # 随机决定标签颜色
    if randomColor:
        color = decideColor(sharpness=layout_config.sharpness)
    else:
        color = layout_config.default_color

    text = {
        'string': '{Group}-{Idx}-{NumCell:02d}-{Order:02d}',
        'size': layout_config.text_size,
        'color': color,
        'translation': layout_config.text_translation}

    layer.data = layer.data[0:-1, :]

    tempLayer = napari.layers.Points(
        data=copy.deepcopy(layer.data),
        features=features,
        text=text,
        symbol=layout_config.point_symbol,
        size=layout_config.point_size,
        face_color=color,
        name=groupName,
        visible=False)
    
    if lidx + 1 == len(viewer.layers):
        # print('A!')
        viewer.layers.remove(viewer.layers[lidx])
        viewer.layers.insert(-2, tempLayer)
    else:
        # print('B!', lidx, len(viewer.layers))
        viewer.layers.remove(viewer.layers[lidx])
        viewer.layers.insert(lidx, tempLayer)

    return groupMeta

def updateShape(viewer, layout_config, datasheet):
    posArray = np.asarray(datasheet.data[['z_raw', 'y_raw', 'x_raw']])
    markerLayer = viewer.layers[0]
    markerRadius = layout_config.marker_radius
    markerLayer.data = []
    for rIdx in range(posArray.shape[0]):
        shapeData = np.tile(posArray[rIdx, :], [4, 1])
        shapeData[0, 1] = shapeData[0, 1] - markerRadius
        shapeData[0, 2] = shapeData[0, 2] - markerRadius
        shapeData[1, 1] = shapeData[1, 1] - markerRadius
        shapeData[1, 2] = shapeData[1, 2] + markerRadius
        shapeData[2, 1] = shapeData[2, 1] + markerRadius
        shapeData[2, 2] = shapeData[2, 2] + markerRadius
        shapeData[3, 1] = shapeData[3, 1] + markerRadius
        shapeData[3, 2] = shapeData[3, 2] - markerRadius
        markerLayer.add_ellipses(copy.deepcopy(shapeData))
    updateLayer(markerLayer)
    return


# 产生标注结果的总表
# 有两种模式：mode=file时，接受前端传递的文件路径信息；mode=data时，接受后端传递的pandas表单信息，最后生成点标注层。
def generateResTable(viewer, getReviewer, layout_config, datasheet, mode = 'data', loadSource = None):
    if mode == 'file':
        datasheet.data = pd.read_excel(loadSource)
    elif mode == 'data':
        frameList = []
        for i in range(len(viewer.layers)):
            if viewer.layers[i].name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points']:
                frameList.append(copy.deepcopy(viewer.layers[i].features.sort_values(by=['Order'])))
        datasheet.data = pd.concat(frameList)
    else:
        print('Please provide valid mode type in [file, data]')
        return
    if getReviewer:
        getReviewerLayer(viewer, datasheet.data, layout_config=layout_config)
    return copy.deepcopy(datasheet.data)


# 保存当前的标注图层
def saveNprSession(viewer, cachedImgPath, startIdx, layout_config, savePrefix):
    frameList = []
    for i in range(len(viewer.layers)):
        if viewer.layers[i].name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points']:  # 排除Reviewer层
            frameList.append(copy.deepcopy(viewer.layers[i].features.sort_values(by=['Order'])))
    pointFrame = copy.deepcopy(pd.concat(frameList))  # 标注点层数据
    markerArray = viewer.layers[0].data  # 标注区域层（椭圆）数据
    imagePath = cachedImgPath  # 保存session时，软件中缓存的图像路径
    saveRes = [imagePath, pointFrame, markerArray, layout_config]  # 保存当前的外观设置
    with open('{}'.format(savePrefix), 'wb') as sessionf:
        pkl.dump(saveRes, sessionf)
    return


# 导入先前保存的标注图层
def loadNprSession(viewer, datasheet, loadPrefix, autoImgLoad):

    def retrievePrefix(name):  # 根据细胞名字读出其所在组别
        elements = name.split('-')
        prefix = '{}-{}'.format(elements[0], elements[1])
        return prefix

    def assignLayer(resFrame):  # 返回当前表单里面的组别编号的最大值 （注意这个编号是从1开始的）
        nameArray = list(resFrame['胞体编号'])
        indexArray = []
        knownPrefix = []
        currentIdx = 0
        for i in nameArray:
            prefix = retrievePrefix(i)
            if prefix in knownPrefix:
                indexArray.append(currentIdx)
            else:
                currentIdx = currentIdx + 1
                indexArray.append(currentIdx)
                knownPrefix.append(prefix)
        dupFrame = copy.deepcopy(resFrame)
        dupFrame['groupIdx'] = indexArray
        return dupFrame['groupIdx'], currentIdx

    def displayLayer(vieweR, layerFeature, name, layoutconfig):  # 将单独一组的特征表单转化为point图层
        color = decideColor(sharpness=layout_config.sharpness)
        posArray = np.asarray(layerFeature[['z_raw', 'y_raw', 'x_raw']])
        text = {
            'string': '{Group}-{Idx}-{NumCell:02d}-{Order:02d}',
            'size': layoutconfig.text_size,
            'color': color,
            'translation': layoutconfig.text_translation}

        vieweR.add_points(data=posArray,
                          features=layerFeature,
                          text=text,
                          symbol=layoutconfig.point_symbol,
                          size=layoutconfig.point_size,
                          face_color=color,
                          name=name,
                          visible=False)
        return

    with open(loadPrefix, 'rb') as sessionf:
        [imagePath, pointFrame, markerArray, layout_config] = pkl.load(sessionf)
    # viewer.layers = [] #不能这么做
    if autoImgLoad:  # 根据保存的缓存图像路径读入图像文件，若不自动加载图像，则只加载标注区域层和点标注层
        try:
            reader(viewer, imagePath, rgb=False)
            viewer.layers[0].add_ellipses(markerArray)
        except OSError:  # 路径不再有效的场合
            print('Loading image failed, try loading image by yourself.')
            viewer.add_shapes(name='Clone Marker')
            viewer.layers[0].add_ellipses(markerArray)
    else:
        viewer.add_shapes(name='Clone Marker')
        viewer.layers[0].add_ellipses(markerArray)

    indexSlice, maxIdx = assignLayer(pointFrame)
    # print(indexSlice)
    for layerIdx in range(1, maxIdx + 1):
        layerFrame = pointFrame[indexSlice == layerIdx]
        layerName = retrievePrefix(layerFrame.iloc[0, 0])
        displayLayer(viewer, layerFrame, layerName, layout_config)
    generateResTable(viewer, True, layout_config, datasheet, mode = 'data', loadSource = None)
    tempLayer = viewer.layers['Image Stack']
    viewer.layers.remove(viewer.layers['Image Stack'])
    viewer.layers.insert(len(viewer.layers) - 1, tempLayer)
    print('Loading Session Completed!')
    return


# 将标注结果保存为ImageJ ROISet Zip文件。既然现在可以在工具内校正，这个功能现在仅仅是用于数据的通用化。
def saveImageJROI(finalRes, roiSPLFPath, savePrefix):
    resTable = finalRes
    roiconvertor.generateROIZip(resTable, roiSPLFPath, savePrefix)
    return


# 生成一个Reviewer层。
def getReviewerLayer(viewer, res, layout_config):
    def assignColor(nameArray):
        colorArray = []
        knownPrefix = []
        currentColor = None
        for i in nameArray:
            elements = i.split('-')
            prefix = '{}-{}'.format(elements[0], elements[1])
            if prefix in knownPrefix:
                colorArray.append(currentColor)
            else:
                currentColor = decideColor(sharpness=layout_config.sharpness)
                colorArray.append(currentColor)
                knownPrefix.append(prefix)
        return colorArray

    colorList = assignColor(list(res['胞体编号']))
    posArray = np.asarray(res[['z_raw', 'y_raw', 'x_raw']])
    text = {
        'string': '{Group}-{Idx}-{NumCell:02d}-{Order:02d}',
        'size': layout_config.text_size,
        'color': colorList,
        'translation': layout_config.text_translation}
    
    # 如已有Reviewer图层则删除之
    lNs = [i.name for i in viewer.layers]
    
    if 'Reviewer' in lNs:
        viewer.layers.remove('Reviewer')
    
    viewer.add_points(
        data=posArray,
        features=res,
        text=text,
        symbol=layout_config.point_symbol,
        size=layout_config.point_size,
        face_color=colorList,
        name='Reviewer')
    return


# 赋予最终生成的表格颜色格式 
def fillExcel(dataframe, path, layout_config, sheetName = 'result'):
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet(sheetName)
        writer.sheets[sheetName] = worksheet
        format2choose = []
        for color in layout_config.excel_colors:
            format2choose.append(workbook.add_format({'bg_color': color}))
        blankF = workbook.add_format({'bg_color': '#FFFFFF'})
        groupName = list(dataframe['Group'])
        groupIdx = list(dataframe['Idx'])
        spName = ['{}-{}'.format(groupName[i], groupIdx[i]) for i in range(len(groupName))]
        color2Assign = []
        cachedName = ''
        cachedIdx = 0
        for name in spName:
            if name != cachedName:
                cachedName = name
                cachedIdx = cachedIdx + 1
            color2Assign.append(format2choose[cachedIdx % len(format2choose)])
        
        for ridx, colorF in enumerate(color2Assign):
            worksheet.set_row(ridx + 1, cell_format = colorF)
        #worksheet.set_column('L:Z', cell_format = blankF) 没什么用
        dataframe.to_excel(writer, sheet_name = sheetName, index = False)
    return

def reArrangeGrp(viewer, layout_config, datasheet):
    grpDict = getGroupDict(viewer)
    dynaDict = copy.deepcopy(grpDict)
    # print(viewer.layers)
    for lidx in range(len(viewer.layers)):
        if viewer.layers[lidx].name not in ['Reviewer', 'Clone Marker', 'Image Stack', 'Points']:
            grpName = viewer.layers[lidx].name[0: viewer.layers[lidx].name.find('-')]
            dynaDict[grpName] = dynaDict[grpName] - 1
            grpIdx = grpDict[grpName] - dynaDict[grpName]
            #print(viewer.layers[lidx].name)
            if '{}-{}'.format(grpName, int(grpIdx)) == viewer.layers[lidx].name:
                pass
            else:
                tempLayer = napari.layers.Points(data=viewer.layers[lidx].data,
                                                features=viewer.layers[lidx].features,
                                                text=viewer.layers[lidx].text,
                                                symbol=layout_config.point_symbol,
                                                size=layout_config.point_size,
                                                face_color=decideColor(sharpness=layout_config.sharpness),
                                                name = '{}-{}'.format(grpName, int(grpIdx)),
                                                visible = False)
                # tempLayer = copy.deepcopy(viewer.layers[lidx])
                numPoints = len(list(viewer.layers[lidx].features['Idx']))
                tempLayer.features['Idx'] = np.array([int(grpIdx)] * numPoints)
                tempLayer.features['胞体编号'] = np.array(
                ['{}-{}-{:02d}-{:02d}'.format(grpName, int(grpIdx), numPoints, list(viewer.layers[lidx].features['Order'])[i]) for i in range(numPoints)])
                viewer.layers.remove(viewer.layers[lidx])
                viewer.layers.insert(lidx, tempLayer)
    res = generateResTable(viewer, True, layout_config, datasheet)
    return res

