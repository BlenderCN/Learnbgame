import bpy

import os

from yallah import YALLAH_FEATURES_DIR

print("Creating the Facial expressions (Shape Keys starting with 'fe_')")
fe_file = os.path.join(YALLAH_FEATURES_DIR, "FacialExpressions/FacialExpressionsMBLab1_6.json")
bpy.ops.object.create_shape_keys(shape_keys_filename=fe_file)
