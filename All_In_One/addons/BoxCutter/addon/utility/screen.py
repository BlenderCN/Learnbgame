import bpy


def dpi():
    system = bpy.context.user_preferences.system
    return int(system.dpi * system.pixel_size)


def dpi_factor():
    return dpi() / 72


def tweak_distance(ot):
    return abs((ot.mouse - ot.last['mouse']).x) + abs((ot.mouse - ot.last['mouse']).y)
