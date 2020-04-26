import bpy


def get_dpi_factor():
    return get_dpi() / 72


def get_dpi():
    systemPreferences = bpy.context.user_preferences.system
    retinaFactor = getattr(systemPreferences, "pixel_size", 1)
    return int(systemPreferences.dpi * retinaFactor)
