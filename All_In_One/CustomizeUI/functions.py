import bpy,os

addon = os.path.basename(os.path.dirname(__file__))

def get_panel_classes():
    panels= []
    for pt in bpy.types.Panel.__subclasses__() :
        if hasattr(pt,"bl_space_type") :
            if pt.bl_space_type in ['VIEW_3D','PROPERTIES','NODE_EDITOR','SEQUENCE_EDITOR'] :
                panels.append(pt)

    return panels

def get_panel_id(pt) :
    if hasattr(pt,'bl_idname') :
        pt_id = pt.bl_idname
    else:
        pt_id = pt.__name__

    return pt_id

def hide_panels():
    customize_UI_prefs = bpy.context.user_preferences.addons[addon].preferences
    for pt in bpy.types.Panel.__subclasses__() :
        pt_id = get_panel_id(pt)

        #bpy.utils.register_class(pt)
        if customize_UI_prefs.panels.get(pt_id) ==0:
            if "bl_rna" in pt.__dict__:
                bpy.utils.unregister_class(pt)


def show_panels():
    customize_UI_prefs = bpy.context.user_preferences.addons[addon].preferences
    for pt in bpy.types.Panel.__subclasses__() :
        pt_id = get_panel_id(pt)

        #bpy.utils.register_class(pt)
        if customize_UI_prefs.panels.get(pt_id) ==0:
            bpy.utils.register_class(pt)

"""
from operators import *
from panels import *
from properties import *


def store_panels() :
    panels = []
    for pt in bpy.types.Panel.__subclasses__() :
        panels[pt.__name__] = bpy.props.BoolProperty()

    return panels
"""
