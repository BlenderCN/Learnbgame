import bpy, ctypes

class BlenderSceneData(ctypes.Structure):
    __fields__ = [
        ('v_count', ctypes.c_int),
        ('vertices', ctypes.POINTER(ctypes.c_float)),
        ('vertex_norms', ctypes.POINTER(ctypes.c_float)),
        ('tri_count', ctypes.c_int),
        ('triangles', ctypes.POINTER(ctypes.c_int)),
        ('shaders', ctypes.POINTER(ctypes.c_int))
        ]


