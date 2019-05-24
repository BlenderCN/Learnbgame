bl_info = {
    "name": "Rig UI",
    "author": "Christophe Seux",
    "version": (0, 1),
    "blender": (2, 77, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(op_material)
    imp.reload(op_picker)
    imp.reload(op_shape)
    imp.reload(properties)
    imp.reload(panels)

from .op_material import *
from .op_picker import *
from .op_shape import *
from .properties import *
from .panels import *

import bpy

def picker_icon(self, context):
    self.layout.operator("rigui.ui_draw",icon ='MOD_ARMATURE',text ="")

def register():

    bpy.types.Armature.UI = bpy.props.PointerProperty(type= bpy.types.PropertyGroup)
    bpy.utils.register_module(__name__)
    bpy.types.Object.UI = bpy.props.PointerProperty(type= ObjectUISettings)
    bpy.types.Scene.UI = bpy.props.PointerProperty(type= SceneUISettings)
    bpy.types.IMAGE_HT_header.prepend(picker_icon)



def unregister():
    del bpy.types.Armature.UI
    del bpy.types.Object.UI
    bpy.types.IMAGE_HT_header.remove(picker_icon)
    bpy.utils.unregister_module(__name__)
