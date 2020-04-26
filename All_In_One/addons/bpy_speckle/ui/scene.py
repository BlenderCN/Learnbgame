import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

#from speckle import SpeckleAddon

#
#   SCENE_PT_speckle(bpy.types.Panel)
#

class SCENE_PT_speckle(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    #bl_idname = 'SCENE_PT_speckle'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_label = "Speckle Settings"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        label = row.label(text="Speckle global settings.")
        row = layout.row()
        row.prop(context.scene.speckle, "scale", text="Scale")
        row = layout.row()
        row.operator("scene.speckle_update", text='Update all')
        row.operator("scene.speckle_import_stream", text='Import stream')
