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
This module implements sharing Blender scenes at Verse server
"""

import bpy
from . import session
from . import ui
from . import scene


class VERSE_SCENE_OT_share(bpy.types.Operator):
    """
    This operator starts to share current Blender scene at Verse server.
    """
    bl_idname = 'scene.blender_scene_share'
    bl_label = "Share at Verse"
    bl_description = "Share current Blender scene at Verse scene as new Verse scene node"

    def invoke(self, context, event):
        """
        Operator for subscribing to Verse scene node
        """
        vrs_session = session.VerseSession.instance()
        scene.VerseScene(session=vrs_session, name=(context.scene.name,))
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected == True and context.scene.verse_node_id == -1:
            return True
        else:
            return False


class VERSE_SCENE_OT_subscribe(bpy.types.Operator):
    """
    This operator subscribes to existing scene shared at Verse server.
    It will create new Blender scene in current .blend file.
    """
    bl_idname = 'scene.verse_scene_node_subscribe'
    bl_label = "Subscribe to Scene"
    bl_description = "Subscribe to verse scene node"

    def invoke(self, context, event):
        """
        Operator for subscribing to Verse scene node
        """
        vrs_session = session.VerseSession.instance()
        scene = context.scene
        scene_item = scene.verse_scenes[scene.cur_verse_scene_index]
        try:
            verse_scene_data = vrs_session.nodes[scene_item.data_node_id]
        except KeyError:
            return {'CANCELLED'}
        else:
            # Send node subscribe to the selected scene data node
            verse_scene_data.subscribe()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Allow this operator only in situation, when Blender is not subscribed
        # to any scene node
        wm = context.window_manager
        scene = context.scene
        if wm.verse_connected == True and scene.cur_verse_scene_index != -1:
            vrs_session = session.VerseSession.instance()
            for scene_item in scene.verse_scenes:
                try:
                    verse_scene_data = vrs_session.nodes[scene_item.data_node_id]
                except KeyError:
                    continue
                if verse_scene_data.subscribed is True:
                    return False
            return True
        else:
            return False


class VERSE_SCENE_OT_unsubscribe(bpy.types.Operator):
    """
    This operator unsubscribes from scene node.
    """
    bl_idname = 'scene.verse_scene_node_unsubscribe'
    bl_label = "Unsubscribe from Scene"
    bl_description = "Unsubscribe from Verse scene node"

    def invoke(self, context, event):
        """
        Operator for unsubscribing from Verse scene node
        """
        vrs_session = session.VerseSession.instance()
        scene = context.scene
        scene_item = scene.verse_scenes[scene.cur_verse_scene_index]
        try:
            verse_scene_data = vrs_session.nodes[scene_item.data_node_id]
        except KeyError:
            return {'CANCELLED'}
        else:
            # Send node unsubscribe to the selected scene data node
            verse_scene_data.unsubscribe()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Allow this operator only in situation, when scene with subscribed
        # data node is selected
        wm = context.window_manager
        scene = context.scene
        if wm.verse_connected is True and scene.cur_verse_scene_index != -1:
            scene_item = scene.verse_scenes[scene.cur_verse_scene_index]
            vrs_session = session.VerseSession.instance()
            try:
                verse_scene_data = vrs_session.nodes[scene_item.data_node_id]
            except KeyError:
                return False
            if verse_scene_data.subscribed is True:
                return True
            else:
                return False
        else:
            return False


class VERSE_SCENE_UL_slot(bpy.types.UIList):
    """
    A custom slot with information about Verse scene node
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        vrs_session = session.VerseSession.instance()
        if vrs_session is not None:
            try:
                verse_scene = vrs_session.nodes[item.node_id]
            except KeyError:
                return
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                layout.label(verse_scene.name, icon='SCENE_DATA')
                try:
                    verse_scene_data = vrs_session.nodes[item.data_node_id]
                except KeyError:
                    pass
                else:
                    if verse_scene_data.subscribed is True:
                        layout.label('', icon='FILE_TICK')
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(verse_scene.name)


class VERSE_SCENE_MT_menu(bpy.types.Menu):
    """
    Menu for scene list
    """
    bl_idname = 'scene.verse_scene_menu'
    bl_label = 'Verse Scene Specials'
    bl_description = 'Menu for list of Verse scenes'

    def draw(self, context):
        """
        Draw menu
        """
        layout = self.layout
        layout.operator('scene.blender_scene_share')
        layout.operator('scene.verse_scene_node_subscribe')
        layout.operator('scene.verse_scene_node_unsubscribe')

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        scene = context.scene

        # Return true only in situation, when client is connected to Verse server
        if scene.cur_verse_scene_index >= 0 and \
                len(scene.verse_scenes) > 0:
            return True
        else:
            return False


class VERSE_SCENE_panel(bpy.types.Panel):
    """
    GUI of Verse scene shared at Verse server
    """
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_label = 'Verse Scenes'
    bl_description = 'Panel with Verse scenes shared at Verse server'

    @classmethod
    def poll(cls, context):
        """
        Can be this panel visible?
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True:
            return True
        else:
            return False

    def draw(self, context):
        """
        This method draw panel of Verse scenes
        """
        scene = context.scene
        layout = self.layout

        row = layout.row()

        row.template_list('VERSE_SCENE_UL_slot',
            'verse_scenes_widget_id',
            scene,
            'verse_scenes',
            scene,
            'cur_verse_scene_index',
            rows=3)

        col = row.column(align=True)
        col.menu('scene.verse_scene_menu', icon='DOWNARROW_HLT', text="")


# List of Blender classes in this submodule
classes = (VERSE_SCENE_UL_slot,
    VERSE_SCENE_MT_menu,
    VERSE_SCENE_panel,
    VERSE_SCENE_OT_share,
    VERSE_SCENE_OT_subscribe,
    VERSE_SCENE_OT_unsubscribe
)


def register():
    """
    This method register all methods of this submodule
    """
    for c in classes:
        bpy.utils.register_class(c)
    ui.init_scene_properties()


def unregister():
    """
    This method unregister all methods of this submodule
    """
    for c in classes:
        bpy.utils.unregister_class(c)
    ui.reset_scene_properties()


if __name__ == '__main__':
    register()
