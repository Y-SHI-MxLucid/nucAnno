# %%
from registration_annotation import *
from convertJSONgraph import *
# %%
convertJSONgraph('annotation/anno.json', 'annotation/annoMap.json')
# %%
viewer, res_imgs = AIO_workflow('data/resampled_test_brain.tiff', 
                                'data/average_template_25.nrrd', 
                                'data/annotation_25.nrrd', 
                                'annotation/annoMap.json')
# %%
imsave('registeredAnno.tiff', res_imgs['Transformed Annotation'])