import math
import mathutils

# Blender uses M = Translation * Rotation * Scale
def inline_entity_matrix(exporter, obj):
    matrix = exporter.M_WORLD * obj.matrix_world
    exporter.w.write(":transform [" + ",".join([",".join(map(str, matrix[i])) for i in range(4)]) + "]")
