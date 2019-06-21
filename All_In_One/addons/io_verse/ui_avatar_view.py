# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


"""
This file contains classes for visualization of other user connected
to verse server in Blender UI (not 3D view). Visualization of other
avatars is implemented in file avatar_view.py.
"""

import bpy
from . import session
from . import ui
from . import avatar_view


class VerseAvatarStatus(bpy.types.Operator):
    """
    Status operator of Verse avatar
    """
    bl_idname = "view3d.verse_avatar"
    bl_label = "Capture"
    bl_description = "Capture camera position"
    last_activity = 'NONE'

    def __init__(self):
        """
        Constructor of this operator
        """
        self.avatar_view = None

    def modal(self, context, event):
        """
        This method is executed on events
        """
        return {'PASS_THROUGH'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and avatar_view.AvatarView.my_view() is not None:
            return True
        else:
            return False

    def execute(self, context):
        """
        This method is used, when this operator is executed
        """
        if context.area.type == 'VIEW_3D':
            if context.window_manager.verse_avatar_capture is False:
                context.window_manager.verse_avatar_capture = True
                # Force redraw (display bgl stuff)
                ui.update_all_views(('VIEW_3D',))
                return {'RUNNING_MODAL'}
            else:
                context.window_manager.verse_avatar_capture = False
                # Force redraw (not display bgl stuff)
                ui.update_all_views(('VIEW_3D',))
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "3D View not found, can't run Camera Capture")
            return {'CANCELLED'}

    def cancel(self, context):
        """
        This method is called, when operator is cancelled.
        """
        if context.window_manager.verse_avatar_capture is True:
            context.window_manager.verse_avatar_capture = False
            return {'CANCELLED'}


class VERSE_AVATAR_OT_show(bpy.types.Operator):
    """
    This operator show selected avatar
    """
    bl_idname = 'view3d.verse_avatar_show'
    bl_label = 'Show Avatar'

    def invoke(self, context, event):
        """
        Show avatar selected in list of avatars
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        avatar_item = wm.verse_avatars[wm.cur_verse_avatar_index]
        verse_avatar = vrs_session.avatars[avatar_item.node_id]
        verse_avatar.visualized = True
        avatar_view.update_3dview(verse_avatar)
        # TODO: subscribe to tag group
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and wm.cur_verse_avatar_index != -1:
            avatar_item = wm.verse_avatars[wm.cur_verse_avatar_index]
            vrs_session = session.VerseSession.instance()
            verse_avatar = vrs_session.avatars[avatar_item.node_id]
            if verse_avatar.visualized is False and verse_avatar.id != vrs_session.avatar_id:
                return True
            else:
                return False
        else:
            return False


class VERSE_AVATAR_OT_show_all(bpy.types.Operator):
    """
    This operator show all avatars
    """
    bl_idname = 'view3d.verse_avatar_show_all'
    bl_label = 'Show All Avatars'

    def invoke(self, context, event):
        """
        Show all avatars in list of avatars
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        for avatar_item in wm.verse_avatars:
            verse_avatar = vrs_session.avatars[avatar_item.node_id]
            verse_avatar.visualized = True
            # TODO: subscribe to unsubscribed tag groups
        ui.update_all_views(('VIEW_3D',))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True:
            return True
        else:
            return False


class VERSE_AVATAR_OT_hide(bpy.types.Operator):
    """
    This operator hide selected avatar
    """
    bl_idname = 'view3d.verse_avatar_hide'
    bl_label = 'Hide Avatar'

    def invoke(self, context, event):
        """
        Hide avatar selected in list of avatars
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        avatar_item = wm.verse_avatars[wm.cur_verse_avatar_index]
        verse_avatar = vrs_session.avatars[avatar_item.node_id]
        verse_avatar.visualized = False
        avatar_view.update_3dview(verse_avatar)
        # TODO: unsubscribe from tag group
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and wm.cur_verse_avatar_index != -1:
            avatar_item = wm.verse_avatars[wm.cur_verse_avatar_index]
            vrs_session = session.VerseSession.instance()
            verse_avatar = vrs_session.avatars[avatar_item.node_id]
            if verse_avatar.visualized is True and verse_avatar.id != vrs_session.avatar_id:
                return True
            else:
                return False
        else:
            return False


class VERSE_AVATAR_OT_hide_all(bpy.types.Operator):
    """
    This operator hide all avatars
    """
    bl_idname = 'view3d.verse_avatar_hide_all'
    bl_label = 'Hide All Avatars'

    def invoke(self, context, event):
        """
        Hide all avatars in list of avatars
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        for avatar_item in wm.verse_avatars:
            verse_avatar = vrs_session.avatars[avatar_item.node_id]
            verse_avatar.visualized = False
            # TODO: unsubscribe from all tag groups
        ui.update_all_views(('VIEW_3D',))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True:
            return True
        else:
            return False


class VERSE_AVATAR_MT_menu(bpy.types.Menu):
    """
    Menu for verse avatar list
    """
    bl_idname = 'view3d.verse_avatar_menu'
    bl_label = 'Verse Avatar Specials'

    def draw(self, context):
        """
        Draw menu
        """
        layout = self.layout
        layout.operator('view3d.verse_avatar_hide')
        layout.operator('view3d.verse_avatar_hide_all')
        layout.operator('view3d.verse_avatar_show')
        layout.operator('view3d.verse_avatar_show_all')

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        if avatar_view.AvatarView.my_view() is not None:
            return True
        else:
            return False


class VERSE_AVATAR_UL_slot(bpy.types.UIList):
    """
    A custom slot with information about Verse avatar node
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        vrs_session = session.VerseSession.instance()
        if vrs_session is not None:
            try:
                verse_avatar = vrs_session.avatars[item.node_id]
            except KeyError:
                return
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if verse_avatar.id == vrs_session.avatar_id:
                    layout.label('Me@' + verse_avatar.hostname, icon='ARMATURE_DATA')
                else:
                    layout.label(str(verse_avatar.username) + '@' + str(verse_avatar.hostname), icon='ARMATURE_DATA')
                    if context.scene.verse_node_id != -1 and \
                            context.scene.subscribed is True and \
                            context.scene.verse_node_id == verse_avatar.scene_node_id.value[0]:
                        if verse_avatar.visualized is True:
                            layout.operator('view3d.verse_avatar_hide', text='', icon='RESTRICT_VIEW_OFF')
                        else:
                            layout.operator('view3d.verse_avatar_show', text='', icon='RESTRICT_VIEW_ON')
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(verse_avatar.name)


class VerseAvatarPanel(bpy.types.Panel):
    """
    Panel with widgets
    """
    bl_idname = "view3d.verse_avatar_panel"
    bl_label = "Verse Avatar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        """
        Can be this panel visible
        """
        # Return true only in situation, when client is connected
        # to Verse server and it is subscribed to data of some scene
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False:
            return True
        else:
            return False

    def draw(self, context):
        """
        Define drawing of widgets
        """
        wm = context.window_manager
        layout = self.layout

        # Display connected avatars in current scene and
        # display menu to hide/display them in 3d
        row = layout.row()
        row.template_list(
            'VERSE_AVATAR_UL_slot',
            'verse_avatars_widget_id',
            wm,
            'verse_avatars',
            wm,
            'cur_verse_avatar_index',
            rows=3
        )

        col = row.column(align=True)
        col.menu('view3d.verse_avatar_menu', icon='DOWNARROW_HLT', text="")


classes = (
    VERSE_AVATAR_UL_slot,
    VerseAvatarPanel,
    VerseAvatarStatus,
    VERSE_AVATAR_OT_hide,
    VERSE_AVATAR_OT_hide_all,
    VERSE_AVATAR_OT_show,
    VERSE_AVATAR_OT_show_all,
    VERSE_AVATAR_MT_menu
)


def register():
    """
    Register classes with panel and initialize properties
    """
    for c in classes:
        bpy.utils.register_class(c)
    ui.init_avatar_properties()


def unregister():
    """
    Unregister classes with panel and reset properties
    """
    for c in classes:
        bpy.utils.unregister_class(c)
    ui.reset_avatar_properties()


if __name__ == '__main__':
    register()
