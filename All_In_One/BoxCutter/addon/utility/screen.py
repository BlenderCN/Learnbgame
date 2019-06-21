import bpy

from . import addon


def dpi():
    system = bpy.context.preferences.system
    return int(system.dpi * system.pixel_size)


def dpi_factor():
    return dpi() / 72 if addon.preference().behavior.use_dpi_factor else 1


def tweak_distance(ot):
    return abs((ot.mouse['location'] - ot.last['mouse']).x) + abs((ot.mouse['location'] - ot.last['mouse']).y)
