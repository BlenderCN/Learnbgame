# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/Ozbend_Engraving_Internal

import bpy


class EngravingInternalPanel(bpy.types.Panel):
    bl_idname = 'EngravingInternal.panel'
    bl_label = 'EngravingInternal'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        self.layout.operator('engravinginternal.start', icon='RENDER_REGION', text='Serial Engraving Internal')


def register():
    bpy.utils.register_class(EngravingInternalPanel)


def unregister():
    bpy.utils.unregister_class(EngravingInternalPanel)
