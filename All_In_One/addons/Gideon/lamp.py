import bpy
from ctypes import *

def convert(bl_lamp_obj):
    lamp = bl_lamp_obj.data

    loc_v = (3*c_float)()
    loc_v[0] = bl_lamp_obj.location.x
    loc_v[1] = bl_lamp_obj.location.y
    loc_v[2] = bl_lamp_obj.location.z

    return {
        'location' : loc_v,
        'energy'   : lamp.energy,
        'color'    : lamp.color,
        'size'     : lamp.shadow_soft_size
        }
