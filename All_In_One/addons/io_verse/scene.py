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
import verse as vrs
from .vrsent import vrsent
from . import object3d
from . import mesh
from . import avatar_view
from . import ui


VERSE_SCENE_CT = 123
TG_INFO_CT = 0
TAG_SCENE_NAME_CT = 0

VERSE_SCENE_DATA_CT = 124


def cb_scene_update(context):
    """
    This function is used as callback function. It is called,
    when something is changed in the scene
    """

    wm = bpy.context.window_manager

    if wm.verse_connected is True:
        # Some following actions has to be checked regularly (selection)

        # TODO: check if scene was renamed and refactor following code

        edit_obj = bpy.context.edit_object

        # Is shared mesh object in edit mode?
        if edit_obj is not None and \
                edit_obj.type == 'MESH' and \
                edit_obj.verse_node_id != -1:
            # When shared mesh object is in edit mode, then check if there is
            # cached geometry
            vrs_obj = object3d.VerseObject.objects[edit_obj.verse_node_id]
            if vrs_obj.mesh_node is not None:
                vrs_obj.mesh_node.send_updates()
        else:
            for obj in bpy.data.objects:
                # Is object shared at verse server
                if obj.verse_node_id != -1:
                    # Was any object updated?
                    if obj.is_updated:
                        object3d.object_update(obj.verse_node_id)
                    # Check if object can be selected
                    vrs_obj = object3d.VerseObject.objects[obj.verse_node_id]
                    if obj.select is True:
                        # Check if current client has permission to selection
                        if vrs_obj.can_be_selected is False:
                            obj.select = False
                            obj.hide_select = True
                        # When object is selected and it is not locked, then try to
                        # lock this object
                        elif vrs_obj.locked is False:
                            vrs_obj.lock()
                            if vrs_obj.mesh_node is not None:
                                vrs_obj.mesh_node.lock()
                        # When client has permission to select, then it can not be
                        # locked by other client
                        elif vrs_obj.locked_by_me is False:
                            obj.select = False
                            obj.hide_select = True
                    # When object is not selected, but it is still locked,
                    # then unlock this node
                    elif vrs_obj.locked_by_me is True:
                        vrs_obj.unlock()
                        if vrs_obj.mesh_node is not None:
                            vrs_obj.mesh_node.unlock()


class VerseSceneData(vrsent.VerseNode):
    """
    Custom VerseNode subclass storing Blender data
    """

    custom_type = VERSE_SCENE_DATA_CT

    def __init__(self, session, node_id=None, parent=None, user_id=None,
                 custom_type=VERSE_SCENE_DATA_CT, autosubscribe=False):
        """
        Constructor of VerseSceneData
        """
        super(VerseSceneData, self).__init__(session, node_id, parent, user_id, custom_type)
        self.objects = {}
        self.meshes = {}
        self._autosubscribe = autosubscribe

    def _auto_subscribe(self):
        """
        User has to subscribe to this node manually, when it is node created by
        other Blender.
        """
        try:
            auto_subscribe = self._autosubscribe
        except AttributeError:
            auto_subscribe = False
        return auto_subscribe

    def subscribe(self):
        """
        This method is called, when Blender user wants to subscribe to the
        scene data shared at Verse server.
        """
        # Send subscribe command to Verse server
        subscribed = super(VerseSceneData, self).subscribe()
        if subscribed is True:
            # Save information about subscription to Blender scene too
            bpy.context.scene.subscribed = True
            # Save ID of scene node in current scene
            bpy.context.scene.verse_node_id = self.parent.id
            # Save node ID of data node in current scene
            bpy.context.scene.verse_data_node_id = self.id
            # Save hostname of server in current scene
            bpy.context.scene.verse_server_hostname = self.session.hostname
            # Save port (service) of server in current scene
            bpy.context.scene.verse_server_service = self.session.service
            # Store/share id of the verse_scene in the AvatarView
            avatar = avatar_view.AvatarView.my_view()
            avatar.scene_node_id.value = (self.parent.id,)
            # Add Blender callback function that sends scene updates to Verse server
            bpy.app.handlers.scene_update_post.append(cb_scene_update)
        # Force redraw of 3D view
        ui.update_all_views(('VIEW_3D',))
        return subscribed

    def unsubscribe(self):
        """
        This method is called, when Blender user wants to unsubscribe
        from scene data.
        """
        # Send unsubscribe command to Verse server
        subscribed = super(VerseSceneData, self).unsubscribe()
        if subscribed is False:
            # Save information about subscription to Blender scene too
            bpy.context.scene.subscribed = False
            # Reset id of the verse_scene in the AvatarView
            avatar = avatar_view.AvatarView.my_view()
            avatar.scene_node_id.value = (0,)
            # Remove Blender callback function
            bpy.app.handlers.scene_update_post.remove(cb_scene_update)
            # TODO: switch all shared data to right state
            # (nodes of objects, nodes of meshes, etc.) or destroy them
        # Force redraw of 3D view
        ui.update_all_views(('VIEW_3D',))
        return subscribed

    def __update_item_slot(self):
        """
        This method tries to update properties in slot of scene list
        """
        try:
            scene_node_id = self.parent.id
        except AttributeError:
            pass
        else:
            scene_item = None
            for _scene_item in bpy.context.scene.verse_scenes:
                if _scene_item.node_id == scene_node_id:
                    scene_item = _scene_item
                    break
            if scene_item is not None:
                # Add ID of this node to the corresponding group of properties
                scene_item.data_node_id = self.id

    @classmethod
    def cb_receive_node_create(cls, session, node_id, parent_id, user_id, custom_type):
        """
        When new node is created or verse server confirms creating of data node
        for current scene, than this callback method is called.
        """
        # Call parent class
        scene_data_node = super(VerseSceneData, cls).cb_receive_node_create(
            session=session,
            node_id=node_id,
            parent_id=parent_id,
            user_id=user_id,
            custom_type=custom_type)
        scene_data_node.__update_item_slot()
        return scene_data_node

    @classmethod
    def cb_receive_node_link(cls, session, parent_node_id, child_node_id):
        """
        When parent node of this type of node is changed at Verse server, then
        this callback method is called, when corresponding command is received.
        """
        # Call parent class
        scene_data_node = super(VerseSceneData, cls).cb_receive_node_link(
            session=session,
            parent_node_id=parent_node_id,
            child_node_id=child_node_id)
        scene_data_node.__update_item_slot()
        return scene_data_node


class VerseSceneName(vrsent.VerseTag):
    """
    Custom subclass of VerseTag representing name of scene
    """

    node_custom_type = VERSE_SCENE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_SCENE_NAME_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_STRING8, count=1,
                 custom_type=TAG_SCENE_NAME_CT, value=None):
        """
        Constructor of VerseSceneName
        """
        super(VerseSceneName, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                             count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when name of scene is set
        """
        tag = super(VerseSceneName, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        # Update name of scene, when name of current scene was changed by other Blender
        if node_id == bpy.context.scene.verse_node_id:
            try:
                verse_scene = session.nodes[node_id]
            except KeyError:
                pass
            else:
                bpy.context.scene.name = verse_scene.name
        # Update list of scenes shared at Verse server
        ui.update_all_views(('PROPERTIES',))
        return tag


class VerseScene(vrsent.VerseNode):
    """
    Custom subclass of VerseNode representing Blender scene
    """

    custom_type = VERSE_SCENE_CT

    scenes = {}

    def __init__(self, session, node_id=None, parent=None, user_id=None, custom_type=VERSE_SCENE_CT, name=None):
        """
        Constructor of VerseScene
        """
        # When parent is not specified, then set parent node as parent of scene nodes
        if parent is None:
            parent = session.nodes[vrs.SCENE_PARENT_NODE_ID]
        # Call parent init method
        super(VerseScene, self).__init__(session, node_id, parent, user_id, custom_type)

        # Create tag group and tag with name of scene
        self.tg_info = vrsent.VerseTagGroup(node=self, custom_type=TG_INFO_CT)
        if name is not None:
            self.tg_info.tag_name = VerseSceneName(tg=self.tg_info, value=name)
        else:
            self.tg_info.tag_name = VerseSceneName(tg=self.tg_info)

        if node_id is None:
            # Create node with data, when this node was created by this Blender
            self.data_node = VerseSceneData(session=session, parent=self, autosubscribe=True)
        else:
            self.data_node = None

    @classmethod
    def cb_receive_node_create(cls, session, node_id, parent_id, user_id, custom_type):
        """
        When new node is created or verse server confirms creating of node for current
        scene, than this callback method is called.
        """

        # Call parent class
        scene_node = super(VerseScene, cls).cb_receive_node_create(
            session=session,
            node_id=node_id,
            parent_id=parent_id,
            user_id=user_id,
            custom_type=custom_type)

        # Add the scene to the dictionary of scenes
        cls.scenes[node_id] = scene_node

        # Add this node to the list of scenes visualized in scene panel
        bpy.context.scene.verse_scenes.add()
        bpy.context.scene.verse_scenes[-1].node_id = node_id

        return scene_node

    @property
    def name(self):
        """
        Property of scene name
        """
        try:
            name = self.tg_info.tag_name.value
        except AttributeError:
            return ""
        else:
            try:
                return name[0]
            except TypeError:
                return ""
