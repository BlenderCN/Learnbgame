# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/blender-color-matching


import bpy


class ColorMatchPanel(bpy.types.Panel):
    bl_idname = 'colormatch.panel'
    bl_label = 'ColorMatch'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'ColorMatch'

    def draw(self, context):
        self.layout.prop(context.window_manager.colormatching_vars, 'source_color')
        self.layout.operator('colormatch.colormatch', text='Search NCS (NCl)').db = 'NCS'
        self.layout.operator('colormatch.colormatch', text='Search RAL Classic').db = 'RAL_C'
        self.layout.operator('colormatch.colormatch', text='Search RAL Design').db = 'RAL_D'
        self.layout.operator('colormatch.colormatch', text='Search RAL Effect').db = 'RAL_E'


def register():
    bpy.utils.register_class(ColorMatchPanel)


def unregister():
    bpy.utils.unregister_class(ColorMatchPanel)
