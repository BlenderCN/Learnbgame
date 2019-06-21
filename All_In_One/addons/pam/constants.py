"""Constants"""

#import mathutils

# config files with many hard-coded variables, used in
# in other parts of PAM, primarily in pam.py

# key-values for the mapping-procedure
MAP_euclid = 0
MAP_normal = 1
MAP_random = 2
MAP_top = 3
MAP_uv = 4
MAP_mask3D = 5

DIS_euclid = 0
DIS_euclidUV = 1
DIS_jumpUV = 2
DIS_UVjump = 3
DIS_normalUV = 4
DIS_UVnormal = 5

# length of a ray along a normal-vector.
# This is used for 1pam.map3dPointToUV() and
# pam.map3dPointTo3d() to map points along the normal between two layers
RAY_FAC = 0.3

INTERPOLATION_QUALITY = 10

# Number of subdivisions for the quadtree cache
# Use higher numbers if uv-maps have a lot of small polygons
CACHE_QUADTREE_DEPTH = 2

# Threshold when converting from uv to 3d
# For when points seem to be outside of the uv mesh due to floating point errors
UV_THRESHOLD = 1e-8

# Threshold for correcting points outside UV borders in grid
# as a fraction of UV grid size
# This means, the value is multiplied with uv grid size to determine if
# the deviation is small enough to be corrected
UV_GRID_THRESHOLD = 1e-3

#DEFAULT_LOCATION = mathutils.Vector((0.0, 0.0, 0.0))
#DEFAULT_SCALE = mathutils.Vector((1.0, 1.0, 1.0))
#DEFAULT_ROTATION = mathutils.Euler((0.0, 0.0, 0.0), "XYZ")

DEFAULT_RESOLUTION = 0.05
KERNEL_THRESHOLD = 0.05

# diameter of the paths
PATH_BEVEL_DEPTH = 0.005
