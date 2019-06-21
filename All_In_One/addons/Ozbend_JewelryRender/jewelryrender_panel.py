# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_JewelryRender

import bpy


class JewelryRenderPanel(bpy.types.Panel):
    bl_idname = 'jewelryrender.panel'
    bl_label = 'JewelryRender'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        self.layout.operator('jewelryrender.start', icon='RENDER_REGION', text='Start Render')


def register():
    bpy.utils.register_class(JewelryRenderPanel)


def unregister():
    bpy.utils.unregister_class(JewelryRenderPanel)
