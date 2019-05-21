import bpy
import os


ADDON_ID = os.path.basename(os.path.dirname(os.path.abspath(__file__)))


def prefs():
    return bpy.context.user_preferences.addons[ADDON_ID].preferences