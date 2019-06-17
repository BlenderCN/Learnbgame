import bpy

def system():
    _system = bpy.context.preferences.system
    return int(_system.dpi * _system.pixel_size)

def factor():
    return system() / 72
