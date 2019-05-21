# Nikita Akimov
# interplanety@interplanety.org

from bpy.types import Panel
from bpy.utils import register_class, unregister_class
from . import WebRequests


class BISMeshPanel(Panel):
    bl_idname = 'bis.mesh_panel'
    bl_label = 'BIS'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'BIS'

    def draw(self, context):
        if WebRequests.WebAuthVars.logged:
            if WebRequests.WebAuthVars.userProStatus:
                self.layout.prop(context.window_manager.bis_get_meshes_info_from_storage_vars, 'searchFilter')
                self.layout.operator('bis.get_meshes_info_from_storage', icon='VIEWZOOM', text=' Search')
                row = self.layout.row()
                row.operator('bis.get_meshes_info_from_storage_prev_page', text='Prev')
                row.operator('bis.get_meshes_info_from_storage_next_page', text='Next')
            else:
                self.layout.operator('bis.get_meshes_info_from_storage', icon='FILE_REFRESH', text=' Get active palette')
            self.layout.prop(context.window_manager.bis_get_meshes_info_from_storage_vars, 'updatePreviews')
            self.layout.separator()
            self.layout.separator()
            self.layout.template_icon_view(context.window_manager.bis_get_meshes_info_from_storage_vars, 'items', show_labels=True)
            self.layout.separator()
            self.layout.separator()
            self.layout.prop(context.window_manager.bis_add_mesh_to_storage_vars, 'name')
            self.layout.prop(context.window_manager.bis_add_mesh_to_storage_vars, 'tags')
            button = self.layout.operator('bis.add_mesh_to_storage', text='Save')
            button.show_message = True
            button = self.layout.operator('bis.update_mesh_in_storage', text='Update')
            button.show_message = True
            self.layout.separator()
            self.layout.separator()
            self.layout.operator('dialog.web_auth', icon='FILE_TICK', text='Sign out')
        else:
            self.layout.operator('dialog.web_auth', icon='WORLD', text='Sign in')


def register():
    register_class(BISMeshPanel)


def unregister():
    unregister_class(BISMeshPanel)
