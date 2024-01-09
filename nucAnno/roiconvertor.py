from roifile import ImagejRoi
# import pandas as pd
import numpy as np
import copy
import os
import zipfile
# from pathlib import Path


# ====主函数区====
# 主要函数，读入sample roi，读入结果表格，生成roiset zip文件
def generateROIZip(resTable, roiSPLFPath, writePrefix):
    roiSample = ImagejRoi.fromfile(roiSPLFPath)[0]
    colors = [[255, 255, 0, 0], [255, 0, 255, 0], [255, 0, 0, 255],
              [255, 255, 255, 0], [255, 255, 0, 255], [255, 0, 255, 255]]
    table = copy.deepcopy(resTable[['胞体编号', 'x_raw', 'y_raw', 'z_raw']])
    table['color'] = assignColors(list(table['胞体编号']), [bytes(i) for i in colors])
    roiList = convertROI(table, roiSample)
    write2File(writePrefix, roiList)
    return


# 给不同组别的细胞点赋予不同的颜色
def assignColors(nameList, colorPal):
    colorNum = len(colorPal)
    grpIdx = 0
    colorList = []
    nameCache = ''
    for name in nameList:
        prefix = name[0:(name[name.find('-') + 1:].find('-') + name.find('-') + 1)]
        if prefix != nameCache:
            grpIdx = grpIdx + 1
            nameCache = prefix
            colorList.append(colorPal[grpIdx % colorNum])
        else:
            colorList.append(colorPal[grpIdx % colorNum])
    return colorList


# 将表格中细胞位置转化为roi文件
def convertROI(resFrame, roiSample):
    roiListTest = []
    for i in range(len(resFrame)):
        name = resFrame.iloc[i, :]['胞体编号']
        coord = np.asarray([resFrame.iloc[i, 1:3]]).astype('float32')
        pos = resFrame.iloc[i, :]['z_raw'] + 1
        roi = copy.deepcopy(roiSample)
        roi.top = int(coord[0, 1])
        roi.bottom = int(coord[0, 1]) + 1
        roi.left = int(coord[0, 0])
        roi.right = int(coord[0, 0]) + 1
        roi.stroke_width = 2
        roi.position = int(pos)
        roi.stroke_color = resFrame.iloc[i, :]['color']
        roi.counter_positions = np.asarray([pos], dtype='uint32')
        roi.subpixel_coordinates = coord
        roi.name = name
        roiListTest.append(roi)
    return roiListTest


# 将roi list写入临时文件夹并打包为zip
def write2File(prefix, roiList):
    if not os.path.exists('.temp/'):
        os.mkdir('.temp/')
    else:
        for file in os.listdir('.temp/'):
            os.remove('.temp/{}'.format(file))

    zip_file = zipfile.ZipFile('{}'.format(prefix), 'w')

    for i in roiList:
        i.tofile('.temp/{:04d}-{:04d}-{:04d}.roi'.format(i.position, i.top, i.left))
        zip_file.write('.temp/{:04d}-{:04d}-{:04d}.roi'.format(i.position, i.top, i.left),
                       '{:04d}-{:04d}-{:04d}.roi'.format(i.position, i.top, i.left),
                       compress_type=zipfile.ZIP_STORED)
        os.remove('.temp/{:04d}-{:04d}-{:04d}.roi'.format(i.position, i.top, i.left))

    zip_file.close()


# 读入标注结果文件
def readFromFile(path):
    roiList = ImagejRoi.fromfile(path)
    propDict = {'胞体编号': [], 'x_raw': [], 'y_raw': [], 'z_raw': []}
    for roi in roiList:
        propDict['胞体编号'].append(roi.name)
        propDict['x_raw'].append(roi.left)
        propDict['y_raw'].append(roi.top)
        propDict['z_raw'].append(roi.top - 1)
    return propDict
