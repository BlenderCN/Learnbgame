bl_info = {
    "name": "Icons Preview",
    "author": "Christophe Seux",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "category": "Learnbgame"
}

import bpy
import os
from os.path import join,dirname,splitext
import bpy.utils.previews

def get_icons():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    icons_dir = join(dirname(__file__),'icons')
    for icon in os.listdir(icons_dir) :
        custom_icons.load(splitext(icon)[0].upper(), join(icons_dir, icon), 'IMAGE')


class Panel(bpy.types.Panel) :
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Icon Preview"
    bl_category = "Icon Preview"

    @staticmethod
    def draw(self, context):
        layout = self.layout
        BLayers = context.scene.BLayers
        scene = context.scene

        ob = context.object

        ids = [pic.icon_id for pic in custom_icons.values()]
        row = layout.row()
        row.prop(scene,"icon_change")
        row.label( icon_value = ids[scene.icon_change])


def register():
    get_icons()
    bpy.utils.register_module(__name__)
    bpy.types.Scene.icon_change = bpy.props.IntProperty()

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.previews.remove(custom_icons)
    del bpy.types.Scene.icon_change
