# %%
import napari
import numpy as np
# %%
viewer = napari.Viewer()
# %%
path = np.array([[1, 180, 40, 40], [1, 180, 50, 50], [1, 182, 55, 65], [1, 182, 55, 85],
                 [1, 184, 120, 130], [1, 184, 100, 120], [1, 186, 105, 115], [1, 186, 135, 15],
                 [1, 188, 201, 60], [1, 188, 180, 50], [1, 190, 155, 75], [1, 190, 145, 65],
                 [1, 192, 40, 40], [1, 192, 40, 100], [1, 194, 45, 105], [1, 194, 95, 115],]                   
                )
layer_t = viewer.add_tracks(path, name='tracks')
layer_p = viewer.add_shapes(
    path, shape_type='path', edge_width=1, edge_color=['red']
)