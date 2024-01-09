# %%
from skimage.io import imread, imsave
from skimage.transform import resize
from skimage.filters import meijering, gaussian
from skimage.morphology import dilation
import numpy as np
import nrrd
import copy
from tqdm import tqdm
import SimpleITK as sitk
import time
import json as js
import napari

# %%
def stripSuppress(Img, thres = 0.05, window = 5, pre_sigmas = [0.4], post_sigma = 0.5):

    vImg = np.zeros(Img.shape)
    for i in tqdm(range(Img.shape[0])):
        vImg[i, :, :] = meijering(Img[i, :, :], sigmas=pre_sigmas, black_ridges=False)
    vImg = gaussian(dilation(vImg), post_sigma, preserve_range=True)

    img = copy.deepcopy(Img)

    for zIdx in tqdm(range(Img.shape[0])):
        for rr in range(Img.shape[1]):
            for cc in range(Img.shape[2]):
                if vImg[zIdx, rr, cc] > thres:
                    rlb = (rr - window > 0) * (rr - window)
                    a = (rr + window) > Img.shape[1]
                    rhb = Img.shape[1] * (a) + (rr + window) * (not a)
                    clb = (cc - window > 0) * (cc - window)
                    b = (cc + window) > Img.shape[2]
                    chb = Img.shape[2] * (b) + (cc + window) * (not b)
                    img[zIdx, rr, cc] = np.min(Img[zIdx, rlb:rhb, clb:chb])

    return vImg, img

# %%
def regis_Flex(fixed, moving, method, lr=2.0, max_itr=50, silence=False):

    def command_iteration(method):
        if method.GetOptimizerIteration() == 0:
            print("Estimated Scales: ", method.GetOptimizerScales())
        print(
            f"{method.GetOptimizerIteration():3} "
            + f"= {method.GetMetricValue():7.5f} "
            + f": {method.GetOptimizerPosition()}"
        )
    
    # Set Registration
    R = sitk.ImageRegistrationMethod()
    R.SetMetricAsCorrelation()
    R.SetOptimizerAsRegularStepGradientDescent(
        learningRate=lr,
        minStep=1e-4,
        numberOfIterations=max_itr,
        gradientMagnitudeTolerance=1e-8,
    )
    R.SetOptimizerScalesFromIndexShift()
    if method == 'local':
        tx = sitk.CenteredTransformInitializer(
            fixed, moving, sitk.AffineTransform(fixed.GetDimension())
        )
    elif method == 'global':
        tx = sitk.CenteredTransformInitializer(
            fixed, moving, sitk.Similarity3DTransform()
        )
    R.SetInitialTransform(tx)
    R.SetInterpolator(sitk.sitkLinear)
    if not silence:
        R.AddCommand(sitk.sitkIterationEvent, lambda: command_iteration(R))

    outTx = R.Execute(fixed, moving)

    if not silence:
        print("-------")
        print(outTx)
        print(f"Optimizer stop condition: {R.GetOptimizerStopConditionDescription()}")
        print(f" Iteration: {R.GetOptimizerIteration()}")
        print(f" Metric value: {R.GetMetricValue()}")
    else:
        pass

    return outTx

# %%
def globalRegis(fixedImg, movingImg, silence=False, write2file=False, lr=2.0, max_itr=50):

    fixed = sitk.GetImageFromArray(np.ascontiguousarray((fixedImg / np.max(fixedImg)).astype('float32')))
    moving = sitk.GetImageFromArray(np.ascontiguousarray((movingImg / np.max(movingImg)).astype('float32')))

    outTx = regis_Flex(fixed, moving, method='global', silence=silence, lr=lr, max_itr=max_itr)
    if write2file:
        sitk.WriteTransform(outTx, 'global_res_{}.hdf5'.format(
            time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())))
    out = warp(fixedImg, movingImg, outTx)

    return {"fixed": fixedImg,
            "moving": movingImg,
            "res": out,
            "parameter":outTx}

# %%
def localRegis(fixedImg, movingImg, lr=2.0, max_itr=50):
        
    trsParaList = []
    for zIdx in tqdm(range(fixedImg.shape[0])):
        fixed = sitk.GetImageFromArray(np.ascontiguousarray(
            (fixedImg[zIdx, :, :] / np.max(fixedImg[zIdx, :, :])).astype('float32')))
        moving = sitk.GetImageFromArray(np.ascontiguousarray(
            (movingImg[zIdx, :, :] / np.max(movingImg[zIdx, :, :])).astype('float32')))
        trsParaList.append(regis_Flex(fixed, moving, method='local', silence=True, 
                                      lr=lr, max_itr=max_itr))

    tsfmImg = np.zeros(fixedImg.shape, dtype=fixedImg.dtype)
    for zIdx in range(fixedImg.shape[0]):
        tsfmImg[zIdx, :, :] = warp(fixedImg[zIdx, :, :], movingImg[zIdx, :, :], outTx=trsParaList[zIdx])

    return {"fixed": fixedImg,
            "moving": movingImg,
            "res": tsfmImg,
            "parameter":trsParaList}

# %%
def warp(fixedImg, movingImg, outTx, bgPixelVal = 0, itpltr = sitk.sitkLinear):

    fixed = sitk.GetImageFromArray(np.ascontiguousarray(fixedImg))
    moving = sitk.GetImageFromArray(np.ascontiguousarray(movingImg))

    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(itpltr)
    resampler.SetDefaultPixelValue(bgPixelVal)
    resampler.SetTransform(outTx)
    out = resampler.Execute(moving)

    return sitk.GetArrayFromImage(out)

# %%
def warpAnno(fixedImg, movingAnno, globalRRes, localRRes):

    globalTRes = warp(fixedImg, movingAnno, globalRRes['parameter'], itpltr=sitk.sitkNearestNeighbor)

    for zIdx in tqdm(range(fixedImg.shape[0])):
        globalTRes[zIdx, :, :] = warp(fixedImg[zIdx, :, :], globalTRes[zIdx, :, :], 
                                      outTx=localRRes['parameter'][zIdx],
                                      itpltr=sitk.sitkNearestNeighbor)
        
    return globalTRes

# %%
def assignBrainRegion(mapFile, annotation):

    with open(mapFile, 'r') as jf:
        annoMap = js.load(jf)
    default_baseNode = annoMap['base_node_list']
    atlas_dict = annoMap['brain_atlas_dict']
    for key in atlas_dict.keys():
        atlas_dict[key] = default_baseNode.index(atlas_dict[key]) + 1

    anno_limited = np.zeros(annotation.shape, dtype='uint8')
    for key in tqdm(atlas_dict.keys()):
        anno_limited[annotation == int(key)] = atlas_dict[key]

    return anno_limited

# %%
def AIO_workflow(resampledImgF, templateImgF, annotationImgF, annotationMapF, interactiveView=True):

    def readImg(imgF:str):
        if imgF.endswith('.nrrd'):
            img, info = nrrd.read(imgF)
        else:
            img = imread(imgF)
        return img
    
    print('Read Images Begin...')
    resampledImg = readImg(resampledImgF)
    templateImg = readImg(templateImgF)
    annotationImg = readImg(annotationImgF)
    print('Read Images Done.')
    print('Remove Bright Strip Begin...')
    v, fltImg = stripSuppress(resampledImg)
    print('Remove Bright Strip Done.')
    print('Global Registration Begin...')
    global_regis_res = globalRegis(fltImg, templateImg, silence=True)
    print('Global Registration Done.')
    print('Local Registration Begin...')
    local_regis_res = localRegis(fltImg, global_regis_res['res'])
    print('Local Registration Done.')
    print('Transform Annotation Map Begin...')
    tsfmTemp = local_regis_res['res']
    annotation = warpAnno(fltImg, annotationImg, global_regis_res, local_regis_res)
    anno_limited = assignBrainRegion(annotationMapF, annotation)

    if interactiveView:
        viewer = napari.Viewer()
        viewer.add_image(fltImg)
        viewer.add_image(tsfmTemp)
        viewer.add_image(anno_limited)
    
    return viewer, {'Filtered Image': fltImg, 'Transformed Template': tsfmTemp, 'Transformed Annotation': anno_limited}
