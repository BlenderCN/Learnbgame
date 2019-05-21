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
This module is used for handling session with Verse server. Blender
can be connected only to one Verse server. Thus there could be only
one session in one Blender instance.
"""

# Default FPS for timer operator
FPS = 15


import bpy
import verse as vrs
from .vrsent import vrsent
from . import ui


# VerseSession class
class VerseSession(vrsent.VerseSession):
    """
    Class Session for this Python client
    """
        
    # Blender could be connected only to one Verse server
    __instance = None

    @classmethod
    def instance(cls):
        """
        instance() -> object
        Class getter of instance
        """
        return cls.__instance

    def __init__(self, hostname, service, flag):
        """
        __init__(hostname, service, flag) -> None
        """
        # Call __init__ from parent class to connect to Verse server
        super(VerseSession, self).__init__(hostname, service, flag)
        self.__class__.__instance = self
        self.debug_print = True

    def __del__(self):
        """
        __del__() -> None
        """
        self.__class__.__instance = None

    def cb_receive_connect_terminate(self, error):
        """
        receive_connect_terminate(error) -> none
        """
        # Call parent method to print debug information
        super(VerseSession, self).cb_receive_connect_terminate(error)
        self.__class__.__instance = None
        # Clear dictionary of nodes
        self.nodes.clear()

        # Stop capturing of current view to 3D View
        # Save current context to 3d view, start capturing and
        # then restore original context
        if bpy.context.window_manager.verse_connected is True:
            original_type = bpy.context.area.type
            bpy.context.area.type = 'VIEW_3D'
            bpy.ops.view3d.verse_avatar()
            bpy.context.area.type = original_type

        # Reset all properties
        ui.reset_avatar_properties()
        ui.reset_scene_properties()
        ui.reset_object_properties()

        # Set Blender property
        bpy.context.window_manager.verse_connected = False

        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))

    def cb_receive_connect_accept(self, user_id, avatar_id):
        """
        _receive_connect_accept(self, user_id, avatar_id) -> None
        """
        super(VerseSession, self).cb_receive_connect_accept(user_id, avatar_id)

        # Set Blender property
        bpy.context.window_manager.verse_connected = True

        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))

    def cb_receive_user_authenticate(self, username, methods):
        """
        _receive_user_authenticate(self, username, methods) -> None
        """
        if username == '':
            bpy.ops.scene.verse_auth_dialog_operator('INVOKE_DEFAULT')
        else:
            if username == self.my_username:
                self.send_user_authenticate(self.my_username, vrs.UA_METHOD_PASSWORD, self.my_password)

    def cb_receive_node_create(self, node_id, parent_id, user_id, custom_type):
        """
        _receive_node_create(self, node_id, parent_id, user_id, type) -> None
        """
        return super(VerseSession, self).cb_receive_node_create(node_id, parent_id, user_id, custom_type)

    def cb_receive_node_destroy(self, node_id):
        """
        _receive_node_destroy(self, node_id) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_node_destroy(node_id)

    def cb_receive_node_link(self, parent_node_id, child_node_id):
        """
         _receive_node_link(self, parent_node_id, child_node_id) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_node_link(parent_node_id, child_node_id)

    def cb_receive_node_perm(self, node_id, user_id, perm):
        """
        _receive_node_perm(self, node_id, user_id, perm) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_node_perm(node_id, user_id, perm)

    def cb_receive_taggroup_create(self, node_id, taggroup_id, custom_type):
        """
        _receive_taggroup_create(self, node_id, taggroup_id, custom_type) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_taggroup_create(node_id, taggroup_id, custom_type)

    def cb_receive_taggroup_destroy(self, node_id, taggroup_id):
        """
        _receive_taggroup_destroy(self, node_id, taggroup_id) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_taggroup_destroy(node_id, taggroup_id)

    def cb_receive_tag_create(self, node_id, taggroup_id, tag_id, data_type, count, custom_type):
        """
        _receive_tag_create(self, node_id, taggroup_id, tag_id, data_type, count, custom_type) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_tag_create(node_id, taggroup_id, tag_id,
                                                               data_type, count, custom_type)

    def cb_receive_tag_destroy(self, node_id, taggroup_id, tag_id):
        """
        _receive_tag_destroy(self, node_id, taggroup_id, tag_id) -> None
        """
        # Call parent method to print debug information
        return super(VerseSession, self).cb_receive_tag_destroy(node_id, taggroup_id, tag_id)

    def cb_receive_tag_set_values(self, node_id, taggroup_id, tag_id, value):
        """
        Custom callback method that is called, when client received command tag set value
        """
        # Call parent method to print debug information and get modified tag
        return super(VerseSession, self).cb_receive_tag_set_values(node_id, taggroup_id, tag_id, value)


class ModalTimerOperator(bpy.types.Operator):
    """
    Operator which runs its self from a timer
    """
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        """
        This method is called periodically and it is used to call callback
        methods, when appropriate command is received.
        """
        if event.type == 'TIMER':
            vrs_session = VerseSession.instance()
            if vrs_session is not None:
                try:
                    vrs_session.callback_update()
                except vrs.VerseError:
                    del vrs_session
                    return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        """
        This method add timer
        """
        self._timer = context.window_manager.event_timer_add(1.0 / FPS, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        """
        This method remove timer
        """
        context.window_manager.event_timer_remove(self._timer)
        return None


# List of Blender classes in this submodule
classes = (
    ModalTimerOperator,
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
