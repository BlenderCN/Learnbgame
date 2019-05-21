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
This module implements sharing Blender objects at Verse server
"""


import bpy
import verse as vrs
from . import session
from . import object3d
from . import mesh
from . import ui


class VerseObjectOtSubscribe(bpy.types.Operator):
    """
    This operator tries to subscribe to Blender Mesh object at Verse server.
    """
    bl_idname = 'object.mesh_object_subscribe'
    bl_label = "Subscribe"
    bl_description = "Subscribe to data of active Mesh Object at Verse server"

    def invoke(self, context, event):
        """
        This method will try to create new node representing Mesh Object
        at Verse server
        """
        # TODO: add something here
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.verse_node_id != -1:
            vrs_session = session.VerseSession.instance()
            try:
                node = vrs_session.nodes[context.active_object.verse_node_id]
            except KeyError:
                return False
            else:
                if node.subscribed is not True:
                    return True
                else:
                    return False
        else:
            return False


class VerseObjectOtShare(bpy.types.Operator):
    """
    This operator tries to share Blender Mesh object at Verse server.
    """
    bl_idname = 'object.mesh_object_share'
    bl_label = "Share at Verse"
    bl_description = "Share active Mesh Object at Verse server"

    def invoke(self, context, event):
        """
        This method will try to create new node representing Mesh Object
        at Verse server
        """
        vrs_session = session.VerseSession.instance()
        # Get node with scene data
        try:
            scene_data_node = vrs_session.nodes[context.scene.verse_data_node_id]
        except KeyError:
            return {'CANCELLED'}
        else:
            # Share active mesh object at Verse server
            object_node = object3d.VerseObject(
                session=vrs_session,
                parent=scene_data_node,
                obj=context.active_object
            )
            object_node.mesh_node = mesh.VerseMesh(
                session=vrs_session,
                parent=object_node,
                mesh=context.active_object.data,
                autosubscribe=True
            )
            object_node.lock()
            # TODO: lock mesh_node too
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.type == 'MESH' and \
                context.active_object.verse_node_id == -1:
            return True
        else:
            return False


class VerseObjectMtMenu(bpy.types.Menu):
    """
    Menu for object list
    """
    bl_idname = 'object.verse_object_menu'
    bl_label = 'Verse Object Specials'
    bl_description = 'Menu for list of Verse objects'

    def draw(self, context):
        """
        Draw menu
        """
        layout = self.layout
        layout.operator('object.mesh_object_subscribe')

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        scene = context.scene

        # Return true only in situation, when client is connected to Verse server
        if scene.cur_verse_object_index >= 0 and \
                len(scene.verse_objects) > 0:
            return True
        else:
            return False


class VerseObjectUlSlot(bpy.types.UIList):
    """
    A custom slot with information about Verse object node
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """
        This method draw one list item representing node
        """
        vrs_session = session.VerseSession.instance()
        if vrs_session is not None:
            try:
                verse_object = vrs_session.nodes[item.node_id]
            except KeyError:
                return
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                layout.label(verse_object.name, icon='OBJECT_DATA')
                # Owner
                if verse_object.user_id == vrs_session.user_id:
                    layout.label('Me')
                else:
                    layout.label(str(verse_object.owner.name))
                # Read permissions
                perm_str = ''
                if verse_object.can_read(vrs_session.user_id):
                    perm_str += 'r'
                else:
                    perm_str += '-'
                # Write permissions
                if verse_object.can_write(vrs_session.user_id):
                    perm_str += 'w'
                else:
                    perm_str += '-'
                # Locked/unlocked?
                if verse_object.locked is True:
                    layout.label(perm_str, icon='LOCKED')
                else:
                    layout.label(perm_str, icon='UNLOCKED')
                # Subscribed?
                if verse_object.mesh_node is not None:
                    layout.label('', icon='FILE_TICK')
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(verse_object.name)


class View3DPanelToolsVerseObject(bpy.types.Panel):
    """
    Panel with Verse tools for Mesh Object
    """
    bl_category = "Relations"
    bl_context = 'objectmode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Verse'

    @classmethod
    def poll(cls, context):
        """
        Can this panel visible
        """
        # Return true only in situation, when client is connected to Verse server
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.type == 'MESH':
            return True
        else:
            return False

    def draw(self, context):
        """
        Definition of panel layout
        """
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.mesh_object_share")
        col.operator("object.mesh_object_subscribe")


class VerseObjectPanel(bpy.types.Panel):
    """
    GUI of Blender objects shared at Verse server
    """
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_label = 'Verse Objects'
    bl_description = 'Panel with Blender objects shared at Verse server'

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
        This method draw panel of Verse scenes
        """
        scene = context.scene
        layout = self.layout

        row = layout.row()

        row.template_list(
            'VerseObjectUlSlot',
            'verse_objects_widget_id',
            scene,
            'verse_objects',
            scene,
            'cur_verse_object_index',
            rows=3
        )

        col = row.column(align=True)
        col.menu('object.verse_object_menu', icon='DOWNARROW_HLT', text="")


class VerseObjectOtAddWritePerm(bpy.types.Operator):
    """
    This operator tries to subscribe to Blender Mesh object at Verse server.
    """
    bl_idname = 'object.object_add_write_perm'
    bl_label = "Add Write Permission"
    bl_description = "Adds write permission to the user"

    def invoke(self, context, event):
        """
        This method will try to create new node representing Mesh Object
        at Verse server
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        user_item = wm.verse_users[wm.cur_verse_user_index]
        user_id = user_item.node_id
        obj_node = vrs_session.nodes[context.active_object.verse_node_id]
        vrs_session.send_node_perm(obj_node.prio, obj_node.id, user_id, vrs.PERM_NODE_WRITE | vrs.PERM_NODE_READ)
        mesh_node = obj_node.mesh_node
        vrs_session.send_node_perm(mesh_node.prio, mesh_node.id, user_id, vrs.PERM_NODE_WRITE | vrs.PERM_NODE_READ)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is owner of node representing object
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.verse_node_id != -1:
            vrs_session = session.VerseSession.instance()
            try:
                node = vrs_session.nodes[context.active_object.verse_node_id]
            except KeyError:
                return False
            else:
                return node.owned_by_me
        else:
            return False


class VerseObjectOtRemWritePerm(bpy.types.Operator):
    """
    This operator tries to subscribe to Blender Mesh object at Verse server.
    """
    bl_idname = 'object.object_rem_write_perm'
    bl_label = "Remove Write Permission"
    bl_description = "Removes write permission to the user"

    def invoke(self, context, event):
        """
        This method will try to create new node representing Mesh Object
        at Verse server
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        user_item = wm.verse_users[wm.cur_verse_user_index]
        user_id = user_item.node_id
        obj_node = vrs_session.nodes[context.active_object.verse_node_id]
        vrs_session.send_node_perm(obj_node.prio, obj_node.id, user_id, vrs.PERM_NODE_READ)
        mesh_node = obj_node.mesh_node
        vrs_session.send_node_perm(mesh_node.prio, mesh_node.id, user_id, vrs.PERM_NODE_READ)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is owner of node representing object
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.verse_node_id != -1:
            vrs_session = session.VerseSession.instance()
            try:
                node = vrs_session.nodes[context.active_object.verse_node_id]
            except KeyError:
                return False
            else:
                return node.owned_by_me
        else:
            return False


class VerseObjectOtSetOwner(bpy.types.Operator):
    """
    This operator tries to subscribe to Blender Mesh object at Verse server.
    """
    bl_idname = 'object.set_owner'
    bl_label = "Set Owner"
    bl_description = "Sets new owner of object"

    def invoke(self, context, event):
        """
        This method will try to create new node representing Mesh Object
        at Verse server
        """
        wm = context.window_manager
        vrs_session = session.VerseSession.instance()
        user_item = wm.verse_users[wm.cur_verse_user_index]
        user_id = user_item.node_id
        node = vrs_session.nodes[context.active_object.verse_node_id]
        vrs_session.send_node_owner(node.prio, node.id, user_id)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        # Return true only in situation, when client is owner of node representing object
        wm = context.window_manager
        if wm.verse_connected is True and \
                context.scene.subscribed is not False and \
                context.active_object is not None and \
                context.active_object.verse_node_id != -1:
            vrs_session = session.VerseSession.instance()
            try:
                node = vrs_session.nodes[context.active_object.verse_node_id]
            except KeyError:
                return False
            else:
                return node.owned_by_me
        else:
            return False


class VerseObjectPermMtMenu(bpy.types.Menu):
    """
    Menu for object list
    """
    bl_idname = 'object.verse_object_perm_menu'
    bl_label = 'Verse Object Permission Specials'
    bl_description = 'Menu for Verse objects permissions'

    def draw(self, context):
        """
        Draw menu
        """
        layout = self.layout
        layout.operator('object.object_add_write_perm')
        layout.operator('object.object_rem_write_perm')
        layout.operator('object.set_owner')

    @classmethod
    def poll(cls, context):
        """
        This class method is used, when Blender check, if this operator can be
        executed
        """
        wm = context.window_manager

        # Return true only in situation, when client is connected to Verse server
        if wm.cur_verse_user_index >= 0 and \
                len(wm.verse_user) > 0:
            return True
        else:
            return False


class VerseObjectPermUlSlot(bpy.types.UIList):
    """
    A custom slot with information about Verse object node
    """

    # TODO: highlight owner of the node

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        vrs_session = session.VerseSession.instance()
        if vrs_session is not None:
            try:
                verse_user = vrs_session.users[item.node_id]
            except KeyError:
                return
            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if verse_user.id == vrs_session.user_id:
                    layout.label('Me', icon='ARMATURE_DATA')
                else:
                    layout.label(str(verse_user.name), icon='ARMATURE_DATA')
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(verse_user.name)


class VerseObjectPermPanel(bpy.types.Panel):
    """
    GUI of Blender objects shared at Verse server
    """
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_label = 'Verse Permissions'
    bl_description = 'Panel with Verse access permissions of the object'

    @classmethod
    def poll(cls, context):
        """
        Can be this panel visible
        """
        # Return true only in situation, when client is connected
        # to Verse server and it is subscribed to data of some scene
        wm = context.window_manager
        obj = context.active_object
        if wm.verse_connected is True and \
                obj is not None and \
                obj.type == 'MESH' and \
                obj.verse_node_id != -1:
            return True
        else:
            return False

    def draw(self, context):
        """
        This method draw panel of Verse scenes
        """
        wm = context.window_manager
        layout = self.layout
        vrs_session = session.VerseSession.instance()
        node = vrs_session.nodes[context.active_object.verse_node_id]

        row = layout.row()
        row.active = node.owned_by_me

        row.template_list(
            'VerseObjectPermUlSlot',
            'verse_object_perms_widget_id',
            wm,
            'verse_users',
            wm,
            'cur_verse_user_index',
            rows=3
        )

        col = row.column(align=True)
        col.menu('object.verse_object_perm_menu', icon='DOWNARROW_HLT', text="")


# List of Blender classes in this submodule
classes = (
    VerseObjectOtShare,
    VerseObjectOtSubscribe,
    View3DPanelToolsVerseObject,
    VerseObjectPanel,
    VerseObjectUlSlot,
    VerseObjectMtMenu,
    VerseObjectPermUlSlot,
    VerseObjectPermPanel,
    VerseObjectOtAddWritePerm,
    VerseObjectOtRemWritePerm,
    VerseObjectOtSetOwner,
    VerseObjectPermMtMenu
)


def register():
    """
    This method register all methods of this submodule
    """
    for c in classes:
        bpy.utils.register_class(c)
    ui.init_object_properties()
    ui.init_user_properties()


def unregister():
    """
    This method unregister all methods of this submodule
    """
    for c in classes:
        bpy.utils.unregister_class(c)
    ui.reset_object_properties()
    ui.reset_user_properties()


if __name__ == '__main__':
    register()
