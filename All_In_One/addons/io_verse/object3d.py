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
import bgl
import mathutils
import verse as vrs
from .vrsent import vrsent
from . import session as vrs_session
from . import ui
from bpy_extras.view3d_utils import location_3d_to_region_2d


VERSE_OBJECT_CT = 125
# Transformation
TG_TRANSFORM_CT = 0
TAG_POSITION_CT = 0
TAG_ROTATION_CT = 1
TAG_SCALE_CT = 2
# Info
TG_INFO_CT = 1
TAG_NAME_CT = 0
LAYER_BB_CT = 0


def update_3dview(node):
    """
    This method updates all 3D View but not in case, when object is selected/locked
    """
    # 3DView should be updated only in situation, when position/rotation/etc
    # of other objects is changed
    if node.obj.select is False:
        ui.update_all_views(('VIEW_3D',))


def object_update(node_id):
    """
    This function is called by Blender callback function, when
    shared object is changed by user.
    """
    # Send changed properties to Verse server
    session = vrs_session.VerseSession.instance()
    try:
        object_node = session.nodes[node_id]
    except KeyError:
        pass
    else:
        object_node.update()


class VerseObjectPosition(vrsent.VerseTag):
    """
    Custom VerseTag subclass representing Blender object position
    """

    node_custom_type = VERSE_OBJECT_CT
    tg_custom_type = TG_TRANSFORM_CT
    custom_type = TAG_POSITION_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32, count=3,
                 custom_type=TAG_POSITION_CT, value=None):
        """
        Constructor of VerseObjectPosition
        """
        super(VerseObjectPosition, self).__init__(tg, tag_id, data_type, count, custom_type, value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(VerseObjectPosition, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        # Update position of Blender object that are not locked by this client
        if tag.tg.node.locked_by_me is False:
            tag.tg.node.obj.location = mathutils.Vector(value)
        # Redraw all 3D views
        update_3dview(tag.tg.node)
        return tag


class VerseObjectRotation(vrsent.VerseTag):
    """
    Custom VerseTag subclass representing Blender object rotation
    """

    node_custom_type = VERSE_OBJECT_CT
    tg_custom_type = TG_TRANSFORM_CT
    custom_type = TAG_ROTATION_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=4, custom_type=TAG_ROTATION_CT, value=None):
        """
        Constructor of VerseObjectRotation
        """
        super(VerseObjectRotation, self).__init__(tg, tag_id, data_type, count, custom_type, value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(VerseObjectRotation, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        # Update rotation of Blender object that are not locked by this client
        if tag.tg.node.locked_by_me is False:
            # It is necessary to have right rotation_mode to set rotation using quaternion
            prev_rot_mode = tag.tg.node.obj.rotation_mode
            tag.tg.node.obj.rotation_mode = 'QUATERNION'
            tag.tg.node.obj.rotation_quaternion = mathutils.Quaternion(value)
            tag.tg.node.obj.rotation_mode = prev_rot_mode
        update_3dview(tag.tg.node)
        return tag


class VerseObjectScale(vrsent.VerseTag):
    """
    Custom VerseTag subclass representing Blender object scale
    """

    node_custom_type = VERSE_OBJECT_CT
    tg_custom_type = TG_TRANSFORM_CT
    custom_type = TAG_SCALE_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=3, custom_type=TAG_SCALE_CT, value=None):
        """
        Constructor of VerseObjectScale
        """
        super(VerseObjectScale, self).__init__(tg, tag_id, data_type, count, custom_type, value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(VerseObjectScale, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        # Update scale of Blender object that are not locked by this client
        if tag.tg.node.locked_by_me is False:
            tag.tg.node.obj.scale = mathutils.Vector(value)
        update_3dview(tag.tg.node)
        return tag


class VerseObjectBoundingBox(vrsent.VerseLayer):
    """
    Custom VerseLayer subclass representing Blender object bounding box
    """

    node_custom_type = VERSE_OBJECT_CT
    custom_type = LAYER_BB_CT

    def __init__(self, node, parent_layer=None, layer_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=3, custom_type=LAYER_BB_CT):
        """
        Constructor of VerseObjectBoundingBox
        """
        super(VerseObjectBoundingBox, self).__init__(node, parent_layer, layer_id, data_type, count, custom_type)

    @classmethod
    def cb_receive_layer_set_value(cls, session, node_id, layer_id, item_id, value):
        """
        This method is called, when new value of verse layer was set
        """
        layer = super(VerseObjectBoundingBox, cls).cb_receive_layer_set_value(
            session, node_id, layer_id, item_id, value)
        update_3dview(layer.node)
        return layer


class VerseObjectName(vrsent.VerseTag):
    """
    Custom VerseTag subclass representing name of Blender object name
    """

    node_custom_type = VERSE_OBJECT_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_NAME_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_STRING8,
                 count=1, custom_type=TAG_NAME_CT, value=None):
        """
        Constructor of VerseObjectName
        """
        super(VerseObjectName, self).__init__(tg, tag_id, data_type, count, custom_type, value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when name of object is set
        """
        tag = super(VerseObjectName, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        # Update name of object, when name of the object was changed by other Blender
        try:
            node = session.nodes[node_id]
        except KeyError:
            pass
        else:
            obj = node.obj
            if obj.name != value[0]:
                obj.name = value[0]
        # Update list of scenes shared at Verse server
        ui.update_all_views(('PROPERTIES',))
        return tag


class VerseObject(vrsent.VerseNode):
    """
    Custom VerseNode subclass representing Blender object
    """

    node_custom_type = VERSE_OBJECT_CT
    tg_custom_type = TG_TRANSFORM_CT
    custom_type = VERSE_OBJECT_CT

    objects = {}

    def __init__(self, session, node_id=None, parent=None, user_id=None, custom_type=VERSE_OBJECT_CT, obj=None):
        """
        Constructor of VerseObject
        """
        super(VerseObject, self).__init__(session, node_id, parent, user_id, custom_type)
        self.obj = obj
        self.transform = vrsent.VerseTagGroup(node=self, custom_type=TG_TRANSFORM_CT)
        self.info = vrsent.VerseTagGroup(node=self, custom_type=TG_INFO_CT)
        self.bb = VerseObjectBoundingBox(node=self)
        self.mesh_node = None
        self.icon_angle = 0.0
        if obj is not None:
            # Transformation
            self.transform.pos = VerseObjectPosition(
                tg=self.transform,
                value=tuple(obj.location))
            self.transform.rot = VerseObjectRotation(
                tg=self.transform,
                value=tuple(obj.matrix_local.to_quaternion().normalized()))
            self.transform.scale = VerseObjectScale(
                tg=self.transform,
                value=tuple(obj.scale))
            # Information
            self.info.name = VerseObjectName(
                tg=self.info,
                value=(str(obj.name),))
            # Bounding Box
            item_id = 0
            for bb_point in obj.bound_box:
                self.bb.items[item_id] = (bb_point[0], bb_point[1], bb_point[2])
                item_id += 1
            # Scene
            self.parent = session.nodes[bpy.context.scene.verse_data_node_id]
        else:
            self.transform.pos = VerseObjectPosition(tg=self.transform)
            self.transform.rot = VerseObjectRotation(tg=self.transform)
            self.transform.scale = VerseObjectScale(tg=self.transform)
            self.info.name = VerseObjectName(tg=self.info)

    @property
    def name(self):
        """
        Property of object name
        """
        try:
            name = self.info.name.value
        except AttributeError:
            return ""
        else:
            try:
                return name[0]
            except TypeError:
                return ""

    @property
    def can_be_selected(self):
        """
        :return: True, when current client can select object
        """
        if self.can_write(self.session.user_id) is True:
            return True
        else:
            return False

    @classmethod
    def cb_receive_node_create(cls, session, node_id, parent_id, user_id, custom_type):
        """
        When new object node is created or verse server, then this callback method is called.
        """
        # Call parent class
        object_node = super(VerseObject, cls).cb_receive_node_create(
            session=session,
            node_id=node_id,
            parent_id=parent_id,
            user_id=user_id,
            custom_type=custom_type)
        # Create binding between Blender object and node
        if object_node.obj is None:
            # Create Blender mesh
            mesh = bpy.data.meshes.new('Verse')
            # Create Blender object
            obj = bpy.data.objects.new('Verse', mesh)
            # Link Blender object to Blender scene
            bpy.context.scene.objects.link(obj)
            object_node.obj = obj
        object_node.obj.verse_node_id = node_id
        cls.objects[node_id] = object_node
        bpy.context.scene.verse_objects.add()
        bpy.context.scene.verse_objects[-1].node_id = node_id
        ui.update_all_views(('VIEW_3D',))
        return object_node

    @classmethod
    def cb_receive_node_lock(cls, session, node_id, avatar_id):
        """
        When some object is locked by other user, then it should not
        be selectable
        """
        object_node = super(VerseObject, cls).cb_receive_node_lock(session, node_id, avatar_id)
        if object_node.session.avatar_id != avatar_id:
            # Only in case, that two clients tried to select one object
            # at the same time and this client didn't win
            object_node.obj.select = False
            if object_node.obj == bpy.context.active_object:
                bpy.context.scene.objects.active = None
            object_node.obj.hide_select = True
        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))
        return object_node

    @classmethod
    def cb_receive_node_unlock(cls, session, node_id, avatar_id):
        """
        When some object was unlocked, then it should be able to select it again
        """
        object_node = super(VerseObject, cls).cb_receive_node_unlock(session, node_id, avatar_id)
        if object_node.session.avatar_id != avatar_id:
            object_node.obj.hide_select = False
        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))
        return object_node

    @classmethod
    def cb_receive_node_owner(cls, session, node_id, user_id):
        """
        """
        object_node = super(VerseObject, cls).cb_receive_node_owner(session, node_id, user_id)
        if object_node.can_read() is True:
            object_node.obj.hide_select = False
        else:
            object_node.obj.hide_select = True
        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))
        return object_node

    @classmethod
    def cb_receive_node_perm(cls, session, node_id, user_id, perm):
        """
        """
        object_node = super(VerseObject, cls).cb_receive_node_perm(session, node_id, user_id, perm)
        if object_node.can_write() is True:
            object_node.obj.hide_select = False
        else:
            object_node.obj.hide_select = True
        ui.update_all_views(('PROPERTIES', 'VIEW_3D'))
        return object_node

    def update(self):
        """
        This method tries to send fresh properties of mesh object to Verse server
        """

        # Position
        if self.transform.pos.value is not None and \
                self.transform.pos.value != tuple(self.obj.location):
            self.transform.pos.value = tuple(self.obj.location)

        # Rotation
        if self.transform.rot.value is not None and \
                self.transform.rot.value != tuple(self.obj.matrix_local.to_quaternion().normalized()):
            self.transform.rot.value = tuple(self.obj.matrix_local.to_quaternion().normalized())

        # Scale
        if self.transform.scale.value is not None and \
                self.transform.scale.value != tuple(self.obj.scale):
            self.transform.scale.value = tuple(self.obj.scale)

        # Bounding box
        item_id = 0
        for bb_point in self.obj.bound_box:
            try:
                if self.bb.items[item_id] != (bb_point[0], bb_point[1], bb_point[2]):
                    self.bb.items[item_id] = (bb_point[0], bb_point[1], bb_point[2])
            except KeyError:
                # Bounding box was not received yet
                break
            item_id += 1

    def draw(self, context):
        """
        Draw vector icon on position of shared object
        """

        if self.locked is True:
            # When object is locked by current client, then visualize it by green color.
            # Otherwise visualize it by red color
            if self.locked_by_me is True:
                color = (0.0, 1.0, 0.0, 1.0)
            else:
                color = (1.0, 0.0, 0.0, 1.0)
        else:
            color = (0.0, 1.0, 1.0, 1.0)

        # Store Line width
        line_width_prev = bgl.Buffer(bgl.GL_FLOAT, [1])
        bgl.glGetFloatv(bgl.GL_LINE_WIDTH, line_width_prev)
        line_width_prev = line_width_prev[0]

        # Store glColor4f
        col_prev = bgl.Buffer(bgl.GL_FLOAT, [4])
        bgl.glGetFloatv(bgl.GL_COLOR, col_prev)

        pos = self.transform.pos.value
        if pos is not None:
            new_pos = location_3d_to_region_2d(
                context.region,
                context.space_data.region_3d,
                pos)
        else:
            # When position of object is not set atm, then draw
            # icon with stipple line
            new_pos = mathutils.Vector((0.0, 0.0, 0.0, 1.0))
            bgl.glEnable(bgl.GL_LINE_STIPPLE)

        verts = (
            (0.20000000298023224, 0.0),
            (0.19318519532680511, 0.051763709634542465),
            (0.17320513725280762, 0.09999989718198776),
            (0.14142143726348877, 0.14142127335071564),
            (0.10000012069940567, 0.17320501804351807),
            (0.13000015914440155, 0.22516652941703796),
            (0.06729313731193542, 0.25114068388938904),
            (0.0, 0.2600000202655792),
            (-0.0672929584980011, 0.2511407434940338),
            (-0.1300000101327896, 0.22516663372516632),
            (-0.1000000014901161, 0.17320509254932404),
            (-0.1414213627576828, 0.1414213627576828),
            (-0.1732050925493240, 0.09999999403953552),
            (-0.1931851655244827, 0.05176381394267082),
            (-0.2000000029802322, 0.0),
            (-0.2600000202655792, 0.0),
            (-0.2511407434940338, -0.06729292124509811),
            (-0.2251666486263275, -0.12999996542930603),
            (-0.1838478147983551, -0.18384772539138794),
            (-0.1300000697374344, -0.22516658902168274),
            (-0.1000000461935997, -0.17320506274700165),
            (-0.0517638735473156, -0.19318515062332153),
            (0.0, -0.20000000298023224),
            (0.05176372453570366, -0.19318519532680511),
            (0.09999991953372955, -0.17320513725280762),
            (0.12999990582466125, -0.2251666933298111),
            (0.18384768068790436, -0.18384787440299988),
            (0.22516657412052155, -0.13000008463859558),
            (0.25114068388938904, -0.06729305535554886),
            (0.26000002026557920, 0.0)
        )

        bgl.glLineWidth(1)
        bgl.glColor4f(color[0], color[1], color[2], color[3])

        bgl.glPushMatrix()

        bgl.glTranslatef(new_pos[0], new_pos[1], 0)

        # TODO: Rotate this icon, when some other user change something (tranformation, mesh)
        # bgl.glRotatef(self.icon_angle, 0, 0, 1)

        # Draw icon
        bgl.glBegin(bgl.GL_LINE_LOOP)
        for vert in verts:
            bgl.glVertex2f(100.0 * vert[0], 100.0 * vert[1])
        bgl.glEnd()

        # When object is locked by someone else or it can not be selected, then draw cross over icon
        if self.locked is True and self.locked_by_me is False or \
                self.can_be_selected is False:
            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex2f(100.0 * verts[3][0], 100.0 * verts[3][1])
            bgl.glVertex2f(100.0 * verts[18][0], 100.0 * verts[18][1])
            bgl.glVertex2f(100.0 * verts[11][0], 100.0 * verts[11][1])
            bgl.glVertex2f(100.0 * verts[27][0], 100.0 * verts[27][1])
            bgl.glEnd()

        bgl.glPopMatrix()

        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glLineWidth(line_width_prev)
        bgl.glColor4f(col_prev[0], col_prev[1], col_prev[2], col_prev[3])

        # # Try to draw mesh IDs
        # if self.mesh_node is not None:
        #     self.mesh_node.draw_IDs(context, self.obj)