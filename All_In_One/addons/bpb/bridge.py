__all__ = ['BPB']

import ctypes
import os
import sys

# The following is needed to prevent Panda from calling any Python functions.
os.environ['PANDA_INCOMPATIBLE_PYTHON'] = '1'

dir = os.path.dirname(__file__)
if not dir:
    dir = './'

if sys.platform == 'win32':
    cdll = ctypes.CDLL(os.path.join(dir, 'bpb.dll'))
else:
    cdll = ctypes.CDLL(os.path.join(dir, 'bpb.so'))

class BPB_context(ctypes.Structure):
    pass

class BPB_object(ctypes.Structure):
    pass

class BPB_object_data(ctypes.Structure):
    pass

class BPB_renderer(ctypes.Structure):
    pass

class BPB_render_desc(ctypes.Structure):
    _fields_ = [
        ('camera', ctypes.POINTER(BPB_object)),
        ('world', ctypes.POINTER(BPB_object)),
        ('width', ctypes.c_int),
        ('height', ctypes.c_int),
        ('region_x', ctypes.c_int),
        ('region_y', ctypes.c_int),
        ('region_width', ctypes.c_int),
        ('region_height', ctypes.c_int),
        ('file_name', ctypes.c_char_p),
    ]

# Just for convenient scoping
class BPB(object):
    context = BPB_context
    object = BPB_object
    object_data = BPB_object_data
    renderer = BPB_renderer
    render_desc = BPB_render_desc

    # Enum values for new_renderer
    RT_window = 1
    RT_gl_viewport = 2
    RT_texture = 3

    initialize = cdll.BPB_initialize
    initialize.restype = ctypes.POINTER(context)
    initialize.argtypes = [ctypes.c_int]

    new_object = cdll.BPB_new_object
    new_object.restype = ctypes.POINTER(object)
    new_object.argtypes = [ctypes.POINTER(context)]

    object_update = cdll.BPB_object_update
    object_update.restype = None
    object_update.argtypes = [ctypes.POINTER(object), ctypes.c_void_p]

    object_set_data = cdll.BPB_object_set_data
    object_set_data.restype = None
    object_set_data.argtypes = [ctypes.POINTER(object),
                                ctypes.POINTER(object_data)]

    new_object_data = cdll.BPB_new_object_data
    new_object_data.restype = ctypes.POINTER(object_data)
    new_object_data.argtypes = [ctypes.POINTER(context), ctypes.c_short]

    object_data_update = cdll.BPB_object_data_update
    object_data_update.restype = None
    object_data_update.argtypes = [ctypes.POINTER(object_data), ctypes.c_void_p]

    new_renderer = cdll.BPB_new_renderer
    new_renderer.restype = ctypes.POINTER(renderer)
    new_renderer.argtypes = [ctypes.c_int, ctypes.c_int]

    renderer_start = cdll.BPB_renderer_start
    renderer_start.restype = None
    renderer_start.argtypes = [ctypes.POINTER(renderer),
                               ctypes.POINTER(render_desc)]

    renderer_finish = cdll.BPB_renderer_finish
    renderer_finish.restype = None
    renderer_finish.argtypes = [ctypes.POINTER(renderer)]

if __name__ == '__main__':
    print(BPB.initialize(0))
