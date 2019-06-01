import bpy

def system():
    _system = bpy.context.user_preferences.system
    return int(_system.dpi * _system.pixel_size)

def factor():
    return system() / 72
