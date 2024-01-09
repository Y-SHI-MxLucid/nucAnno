# %%
from skimage.io import imread
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
import json as js
import copy
from collections import Counter

# %%
def generateAnnoMesh(annoImg, splSpace = 2):
    gridImg = np.zeros(annoImg.shape, dtype='uint8')
    for zIdx in range(gridImg.shape[0]):
        for yIdx in range(gridImg.shape[1]):
            for xIdx in range(gridImg.shape[2]):
                if not ((zIdx % splSpace) or (yIdx % splSpace) or 
                        (xIdx % splSpace)):
                    gridImg[zIdx, yIdx, xIdx] = 1
    sampledAnno = annoImg * gridImg
    return sampledAnno, gridImg

# %%
def rtrvPointCoord(datasheet, x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, 
                   offset = [0, 0, 0]):
    x_scale = x_pxlRes / dsCube_pxlRes
    y_scale = y_pxlRes / dsCube_pxlRes
    z_scale = z_pxlRes / dsCube_pxlRes
    x_pos_raw = np.asarray(datasheet['x_raw'])
    y_pos_raw = np.asarray(datasheet['y_raw'])
    z_pos_raw = np.asarray(datasheet['z_raw'])
    x_pos = (x_pos_raw + offset[2]) * x_scale
    y_pos = (y_pos_raw + offset[1]) * y_scale
    z_pos = (z_pos_raw + offset[0]) * z_scale
    return np.transpose(np.array([z_pos, y_pos, x_pos]))

# %%
def getSampleData(sampledAnno, gridImg):
    x_train = np.transpose(np.array(np.where(gridImg * sampledAnno > 0)))
    y_train = sampledAnno[np.where(gridImg * sampledAnno > 0)]
    return x_train, y_train

# %%
def KNN_model_trainer(x_train, y_train, n_neighbors = 3, parallel = None):
    model = KNeighborsClassifier(n_neighbors=n_neighbors, n_jobs=parallel)
    model.fit(x_train, y_train)
    return model

# %%
def AssignBrainRegion(datasheet, model, anno_map, x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, offset):
    datasheet_ = copy.deepcopy(datasheet)
    posArray = rtrvPointCoord(datasheet, x_pxlRes=x_pxlRes, y_pxlRes=y_pxlRes, z_pxlRes=z_pxlRes, 
                              dsCube_pxlRes=dsCube_pxlRes, offset=offset)
    posAnno = model.predict(posArray)
    baseNodeList = anno_map['base_node_list']
    grpList = []
    nameList = []
    for aIdx in range(posAnno.shape[0]):
        grpList.append(baseNodeList[posAnno[aIdx] - 1])
        nameList.append('{}-{}-{:02d}-{:02d}'.format(grpList[-1], datasheet['Idx'][aIdx], 
                                                     datasheet['NumCell'][aIdx], 
                                                     datasheet['Order'][aIdx]))
    datasheet_['胞体编号'] = nameList
    datasheet_['Group'] = grpList
    return datasheet_
# %%
def AIO_AssignerFlow(ds_source, annoImgPath, annoMapPath, x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes,
                     mode='data', spl_rate = 0.5, n_neighbors = 3, cpu_parallel = 4, offset = [0, 0, 0]):
    if mode == 'file':
        datasheet = pd.read_excel(ds_source)
    elif mode == 'data':
        datasheet = ds_source
    annoImg = imread(annoImgPath)
    with open(annoMapPath, 'r') as jf:
        annoMap = js.load(jf)
    
    sampledAnno, gridImg = generateAnnoMesh(annoImg, splSpace = int(1/spl_rate))
    x_train, y_train = getSampleData(sampledAnno, gridImg)
    knn_model = KNN_model_trainer(x_train, y_train, n_neighbors = n_neighbors, parallel = cpu_parallel)
    new_ds = AssignBrainRegion(datasheet, knn_model, annoMap, 
                               x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, offset)
    return new_ds

# %%
def get_Trained_Model(annoImgPath, annoMapPath, spl_rate = 0.5, n_neighbors = 3, cpu_parallel = 4):
    
    annoImg = imread(annoImgPath)
    with open(annoMapPath, 'r') as jf:
        annoMap = js.load(jf)
    
    sampledAnno, gridImg = generateAnnoMesh(annoImg, splSpace = int(1/spl_rate))
    x_train, y_train = getSampleData(sampledAnno, gridImg)
    knn_model = KNN_model_trainer(x_train, y_train, n_neighbors = n_neighbors, parallel = cpu_parallel)
    print('Trained Model Prepared. Enjoy!')
    return annoMap, knn_model

# %%
def get_Singlet_Assigned(x_pxlRes, y_pxlRes, z_pxlRes, dsCube_pxlRes, offset, coord, model, annoMap):
    # coord 即 format points 函数里面的 data
    x_scale = x_pxlRes / dsCube_pxlRes
    y_scale = y_pxlRes / dsCube_pxlRes
    z_scale = z_pxlRes / dsCube_pxlRes
    x_pos = (coord[:, 2] + offset[2]) * x_scale
    y_pos = (coord[:, 1] + offset[1]) * y_scale
    z_pos = (coord[:, 0] + offset[0]) * z_scale

    posAnno = model.predict(np.transpose(np.array([z_pos, y_pos, x_pos])))
    baseNodeList = annoMap['base_node_list']
    pointAnno = []
    for aIdx in range(posAnno.shape[0]):
        pointAnno.append(baseNodeList[posAnno[aIdx] - 1])
    name = Counter(pointAnno).most_common()[0][0]
    return name

