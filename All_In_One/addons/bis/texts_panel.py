# Nikita Akimov
# interplanety@interplanety.org

import bpy
from . import WebRequests


class BISTextsPanel(bpy.types.Panel):
    bl_idname = 'bis.texts_panel'
    bl_label = 'BIS'
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        if WebRequests.WebAuthVars.logged:
            if WebRequests.WebAuthVars.userProStatus:
                self.layout.prop(context.window_manager.bis_get_texts_info_from_storage_vars, 'searchFilter')
                self.layout.operator('bis.get_texts_info_from_storage', icon='VIEWZOOM', text=' Search')
                row = self.layout.row()
                row.operator('bis.get_texts_info_from_storage_prev_page', text='Prev')
                row.operator('bis.get_texts_info_from_storage_next_page', text='Next')
            else:
                self.layout.operator('bis.get_texts_info_from_storage', icon='FILE_REFRESH', text=' Get active palette')
            self.layout.separator()
            self.layout.separator()
            self.layout.prop(context.window_manager.bis_get_texts_info_from_storage_vars, 'items')
            self.layout.separator()
            self.layout.separator()
            self.layout.prop(context.scene.bis_add_text_to_storage_vars, 'tags')
            button = self.layout.operator('bis.add_text_to_storage', text='Save')
            button.showMessage = True
            button = self.layout.operator('bis.update_text_in_storage', text='Update')
            button.showMessage = True
            self.layout.separator()
            self.layout.separator()
            self.layout.operator('dialog.web_auth', icon='FILE_TICK', text='Sign out')
        else:
            self.layout.operator('dialog.web_auth', icon='WORLD', text='Sign in')


def register():
    bpy.utils.register_class(BISTextsPanel)


def unregister():
    bpy.utils.unregister_class(BISTextsPanel)
