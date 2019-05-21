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
This module implements ui functions used by other modules.
"""

import bpy


def update_all_views(area_types=None):
    """
    This method updates all areas, when no type is specified.
    When area_types is specified, then this function tag to
    redraw only areas with type specified in area_types.
    """
    # Force redraw of all Properties View in all screens
    if area_types is None:
        for screen in bpy.data.screens:
            for area in screen.areas:
                # Tag all area to redraw
                area.tag_redraw()
    else:
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type in area_types:
                    area.tag_redraw()


class VERSE_SCENE_NODES_list_item(bpy.types.PropertyGroup):
    """
    Group of properties with representation of Verse scene node
    """
    node_id = bpy.props.IntProperty(
        name="Node ID",
        description="ID of scene node",
        default=-1)
    data_node_id = bpy.props.IntProperty(
        name="Data Node ID",
        description="ID of node with scene data",
        default=-1)


def init_scene_properties():
    """
    Init properties in blender scene data type
    """
    bpy.types.Scene.verse_scenes = bpy.props.CollectionProperty(
        type=VERSE_SCENE_NODES_list_item,
        name="Verse Scenes",
        description="The list of verse scene nodes shared at Verse server"
    )
    bpy.types.Scene.cur_verse_scene_index = bpy.props.IntProperty(
        name="Index of current Verse scene",
        default=-1,
        min=-1,
        max=1000,
        description="The index of curently selected Verse scene node"
    )
    bpy.types.Scene.subscribed = bpy.props.BoolProperty(
        name="Subscribed to scene node",
        default=False,
        description="Is Blender subscribed to data of shared scene"
    )
    bpy.types.Scene.verse_node_id = bpy.props.IntProperty(
        name="ID of verse scene node",
        default=-1,
        description="The ID of the verse node representing current Blender scene"
    )
    bpy.types.Scene.verse_data_node_id = bpy.props.IntProperty(
        name="ID of verse scene data node",
        default=-1,
        description="The ID of the verse node representing current Blender scene data"
    )
    bpy.types.Scene.verse_server_hostname = bpy.props.StringProperty(
        name="Verse server hostname",
        default="",
        description="Hostname of Verse server, where this scene is shared"
    )
    bpy.types.Scene.verse_server_service = bpy.props.StringProperty(
        name="Verse server port (service)",
        default="",
        description="Port (service) of Verse server"
    )


def reset_scene_properties():
    """
    This method reset all properties. It is used, when Blender is disconnected
    from Verse server
    """
    scene = bpy.context.scene
    scene.verse_scenes.clear()
    scene.cur_verse_scene_index = -1
    scene.subscribed = False
    scene.verse_node_id = -1
    scene.verse_data_node_id = -1
    scene.verse_server_hostname = ""
    scene.verse_server_service = ""


class VERSE_AVATAR_NODES_list_item(bpy.types.PropertyGroup):
    """
    Group of properties with representation of Verse avatar node
    """
    node_id = bpy.props.IntProperty(
        name="Node ID",
        description="Node ID of avatar node",
        default=-1
    )


class VERSE_USER_NODES_list_item(bpy.types.PropertyGroup):
    """
    Group of properties with representation of Verse avatar node
    """
    node_id = bpy.props.IntProperty(
        name="Node ID",
        description="Node ID of user node",
        default=-1
    )


def init_avatar_properties():
    """
    Initialize properties used by this module
    """
    wm = bpy.types.WindowManager
    wm.verse_avatar_capture = bpy.props.BoolProperty(
        name="Avatar Capture",
        default=False,
        description="This is information about my view to 3D scene shared at Verse server"
    )
    wm.verse_avatars = bpy.props.CollectionProperty(
        type=VERSE_AVATAR_NODES_list_item,
        name="Verse Avatars",
        description="The list of verse avatar nodes representing Blender at Verse server"
    )
    wm.cur_verse_avatar_index = bpy.props.IntProperty(
        name="Index of current Verse avatar",
        default=-1,
        min=-1,
        max=1000,
        description="The index of currently selected Verse avatar node"
    )


def init_user_properties():
    """
    Initialize properties used for users
    """
    wm = bpy.types.WindowManager
    wm.verse_users = bpy.props.CollectionProperty(
        type=VERSE_USER_NODES_list_item,
        name="Verse Users",
        description="The list of verse user nodes representing valid users at Verse server"
    )
    wm.cur_verse_user_index = bpy.props.IntProperty(
        name="Index of current Verse user",
        default=-1,
        min=-1,
        max=1000,
        description="The index of currently selected Verse user node"
    )


def reset_avatar_properties():
    """
    Reset properties used by this module
    """
    wm = bpy.context.window_manager
    wm.verse_avatar_capture = False
    wm.verse_avatars.clear()
    wm.cur_verse_avatar_index = -1


def reset_user_properties():
    """
    Reset properties used by this module
    """
    wm = bpy.context.window_manager
    wm.verse_users.clear()
    wm.cur_verse_user_index = -1


class VERSE_OBJECT_NODES_list_item(bpy.types.PropertyGroup):
    """
    Group of properties with representation of Verse scene node
    """
    node_id = bpy.props.IntProperty(
        name="Node ID",
        description="ID of object node",
        default=-1
    )


def cb_set_obj_node_id(self, value):
    """
    Callback function for setting property value
    """
    self.verse_node_id_ = value
    return None


def cb_get_obj_node_id(self):
    """
    Callback function for getting property value.
    TODO: renaming object will reset verse_node_id and break sharing
    """
    if self.name != self.name_:
        self.name_ = self.name
        self.verse_node_id_ = -1
    return self.verse_node_id_


def init_object_properties():
    """
    Init properties related to Blender objects
    """
    bpy.types.Scene.verse_objects = bpy.props.CollectionProperty(
        type=VERSE_OBJECT_NODES_list_item,
        name="Verse Objects",
        description="The list of verse object nodes shared at Verse server"
    )
    bpy.types.Scene.cur_verse_object_index = bpy.props.IntProperty(
        name="Index of current Verse object",
        default=-1,
        min=-1,
        max=1000,
        description="The index of currently selected Verse object node"
    )
    bpy.types.Object.verse_node_id = bpy.props.IntProperty(
        name="ID of verse node",
        default=-1,
        description="The node ID representing this Object at Verse server"
        # TODO: use following callback function set=cb_set_obj_node_id,
        # TODO: use following callback function get=cb_get_obj_node_id
    )
    bpy.types.Object.verse_node_id_ = bpy.props.IntProperty(
        name="Hidden ID of verse node",
        default=-1,
        description="Hidden ID of verse node",
        options={'HIDDEN'}
    )
    bpy.types.Object.name_ = bpy.props.StringProperty(
        name="SecretName",
        default="",
        description="Expected name of object storing properties",
        options={'HIDDEN'}
    )
    bpy.types.Object.subscribed = bpy.props.BoolProperty(
        name="Subscribed to data of object node",
        default=False,
        description="Is Blender subscribed to data of mesh object"
    )


def reset_object_properties():
    """
    Reset properties related to Blender objects
    """
    scene = bpy.context.scene
    scene.verse_objects.clear()
    scene.cur_verse_object_index = -1
    # Mark all objects as unsubscribed
    for obj in bpy.data.objects:
        if hasattr(obj, 'subscribed') is True:
            obj.subscribed = False


# List of Blender classes in this submodule
classes = (
    VERSE_SCENE_NODES_list_item,
    VERSE_AVATAR_NODES_list_item,
    VERSE_OBJECT_NODES_list_item,
    VERSE_USER_NODES_list_item
)


def register():
    """
    This method register all methods of this submodule
    """
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    """
    This method unregister all methods of this submodule
    """
    for c in classes:
        bpy.utils.unregister_class(c)