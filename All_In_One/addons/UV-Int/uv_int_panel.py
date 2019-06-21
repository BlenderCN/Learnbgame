# Nikita Akimov
# interplanety@interplanety.org

import bpy


class UV_int_panel(bpy.types.Panel):
    bl_idname = 'uv_int.panel'
    bl_label = 'UV-Int'
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'UV-Int'

    def draw(self, context):
        self.layout.operator('uv_int.separate_meshloops', icon = 'UNLINKED', text = 'Blast')
        self.layout.operator('uv_int.separate_meshloops_by_edge', icon = 'UNLINKED', text = 'Seam by edge')
        self.layout.operator('uv_int.weld_meshloops', icon = 'LINKED', text = 'Weld')


def register():
    bpy.utils.register_class(UV_int_panel)


def unregister():
    bpy.utils.unregister_class(UV_int_panel)
