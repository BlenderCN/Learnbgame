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
This file contains methods and classes for visualization of other
users connected to Verse server. It visualize their position and
current view to active 3DView. Other Blender users sharing data at
Verse server can also see, where you are and what you do.
"""

import bpy
import bgl
import blf
import mathutils
import math
import verse as vrs
from .vrsent import vrsent
from . import ui
from bpy_extras.view3d_utils import location_3d_to_region_2d


TG_INFO_CT = 0
TAG_LOCATION_CT = 0
TAG_ROTATION_CT = 1
TAG_DISTANCE_CT = 2
TAG_PERSPECTIVE_CT = 3
TAG_WIDTH_CT = 4
TAG_HEIGHT_CT = 5
TAG_LENS_CT = 6
TAG_SCENE_CT = 7


def update_3dview(avatar_view):
    """
    This method updates all 3D View but not in case, when the avatar_view is equal to current view,
    because it would be useless.
    """
    # 3DView should be updated only in situation, when position/rotation/etc
    # of other avatar is changed
    if avatar_view != AvatarView.my_view():
        ui.update_all_views(('VIEW_3D',))


class BlenderUserNameTag(vrsent.verse_user.UserNameTag):
    """
    Custom VerseTag subclass for storing username
    """

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set.
        It should force to redraw all visible 3D views.
        """
        tag = super(BlenderUserNameTag, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        ui.update_all_views(('VIEW_3D',))
        return tag


class BlenderHostnameTag(vrsent.verse_avatar.HostnameTag):
    """
    Custom VerseTag subclass for storing hostname
    """

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set.
        It should force to redraw all visible 3D views.
        """
        tag = super(BlenderHostnameTag, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        ui.update_all_views(('VIEW_3D',))
        return tag


class AvatarLocation(vrsent.VerseTag):
    """Class representing location of avatar"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_LOCATION_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=3, custom_type=TAG_LOCATION_CT, value=(0.0, 0.0, 0.0)):
        """Constructor of AvatarLocation"""
        super(AvatarLocation, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                             count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarLocation, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarRotation(vrsent.VerseTag):
    """Class representing rotation of avatar"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_ROTATION_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=4, custom_type=TAG_ROTATION_CT, value=(0.0, 0.0, 0.0, 0.0)):
        """Constructor of AvatarRotation"""
        super(AvatarRotation, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                             count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarRotation, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarDistance(vrsent.VerseTag):
    """Class representing distance of avatar from center of rotation"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_DISTANCE_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=1, custom_type=TAG_DISTANCE_CT, value=(0.0,)):
        """Constructor of AvatarDistance"""
        super(AvatarDistance, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                             count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarDistance, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarPerspective(vrsent.VerseTag):
    """Class representing perspective of avatar"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_PERSPECTIVE_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_STRING8,
                 count=1, custom_type=TAG_PERSPECTIVE_CT, value=('PERSP',)):
        """Constructor of AvatarPerspective"""
        super(AvatarPerspective, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                                count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarPerspective, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarWidth(vrsent.VerseTag):
    """Class representing width of avatar view"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_WIDTH_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_UINT16,
                 count=1, custom_type=TAG_WIDTH_CT, value=(0,)):
        """Constructor of AvatarWidth"""
        super(AvatarWidth, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                          count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarWidth, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarHeight(vrsent.VerseTag):
    """Class representing height of avatar view"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_HEIGHT_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_UINT16,
                 count=1, custom_type=TAG_HEIGHT_CT, value=(0,)):
        """Constructor of AvatarHeight"""
        super(AvatarHeight, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                           count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarHeight, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarLens(vrsent.VerseTag):
    """Class representing lens of avatar view"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_LENS_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_REAL32,
                 count=1, custom_type=TAG_LENS_CT, value=(35.0,)):
        """Constructor of AvatarLens"""
        super(AvatarLens, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                         count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarLens, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarScene(vrsent.VerseTag):
    """Class representing scene id of avatar view"""
    node_custom_type = vrs.AVATAR_NODE_CT
    tg_custom_type = TG_INFO_CT
    custom_type = TAG_SCENE_CT

    def __init__(self, tg, tag_id=None, data_type=vrs.VALUE_TYPE_UINT32,
                 count=1, custom_type=TAG_SCENE_CT, value=(0,)):
        """Constructor of AvatarScene"""
        super(AvatarScene, self).__init__(tg=tg, tag_id=tag_id, data_type=data_type,
                                          count=count, custom_type=custom_type, value=value)

    @classmethod
    def cb_receive_tag_set_values(cls, session, node_id, tg_id, tag_id, value):
        """
        This method is called, when new value of verse tag was set
        """
        tag = super(AvatarScene, cls).cb_receive_tag_set_values(session, node_id, tg_id, tag_id, value)
        update_3dview(tag.tg.node)
        return tag


class AvatarView(vrsent.VerseAvatar):
    """
    Verse node with representation of avatar view to 3D View
    """

    # View of own avatar
    __my_view = None

    # Dictionary of other avatar views of other users
    __other_views = {}

    # This is specific custom_type of Avatar
    custom_type = vrs.AVATAR_NODE_CT

    @classmethod
    def my_view(cls):
        """
        Getter of class member __my_view
        """
        return cls.__my_view

    @classmethod
    def other_views(cls):
        """
        Getter of class member __other_views
        """
        return cls.__other_views

    def __init__(self, *args, **kwargs):
        """
        Constructor of AvatarView node
        """
        
        super(AvatarView, self).__init__(*args, **kwargs)
        
        wm = bpy.context.window_manager
        wm.verse_avatars.add()
        wm.verse_avatars[-1].node_id = self.id
        
        # Force redraw of 3D view
        ui.update_all_views(('VIEW_3D',))

        self.scene_node = None
        view_initialized = False
        self.visualized = True
        self.cur_area = None
        self.cur_space = None

        if self.id == self.session.avatar_id:
            # Initialize default values
            self.cur_screen = bpy.context.screen
            self.__class__.__my_view = self

            # Try to find current 3D view 
            for area in bpy.context.screen.areas.values():
                if area.type == 'VIEW_3D':
                    self.cur_area = area
                    for space in area.spaces.values():
                        if space.type == 'VIEW_3D':
                            self.cur_space = space
                            break
                    break

            if self.cur_area.type == 'VIEW_3D' and self.cur_space.type == 'VIEW_3D':
                view_initialized = True
                # Create tag group containing information about view
                self.view_tg = vrsent.VerseTagGroup(
                    node=self,
                    custom_type=TG_INFO_CT)
                # Create tags with data of view to 3D view
                # Location
                self.location = AvatarLocation(
                    tg=self.view_tg,
                    value=tuple(self.cur_space.region_3d.view_location))
                # Rotation
                self.rotation = AvatarRotation(
                    tg=self.view_tg,
                    value=tuple(self.cur_space.region_3d.view_rotation))
                # Distance
                self.distance = AvatarDistance(
                    tg=self.view_tg,
                    value=(self.cur_space.region_3d.view_distance,))
                # Perspective/Orthogonal
                self.perspective = AvatarPerspective(
                    tg=self.view_tg,
                    value=(self.cur_space.region_3d.view_perspective,))
                # Width
                self.width = AvatarWidth(
                    tg=self.view_tg,
                    value=(self.cur_area.width,))
                # Height
                self.height = AvatarHeight(
                    tg=self.view_tg,
                    value=(self.cur_area.height,))
                # Lens
                self.lens = AvatarLens(
                    tg=self.view_tg,
                    value=(self.cur_space.lens,))
                # Get current Scene ID
                if bpy.context.scene.verse_node_id != -1:
                    scene_node_id = bpy.context.scene.verse_node_id
                else:
                    scene_node_id = 0
                self.scene_node_id = AvatarScene(
                    tg=self.view_tg,
                    value=(scene_node_id,))
            
                # TODO: check following code (may be not needed anymore)
                original_type = bpy.context.area.type
                bpy.context.area.type = 'VIEW_3D'
                bpy.ops.view3d.verse_avatar()
                bpy.context.area.type = original_type
            else:
                # TODO: Add some assert, because this should not happen.
                pass
        else:
            self.__class__.__other_views[self.id] = self
        
        if view_initialized is False:
            # Create tag group containing information about view
            self.view_tg = vrsent.VerseTagGroup(
                node=self,
                custom_type=TG_INFO_CT)
            # Create tags with data of view to 3D view
            self.location = AvatarLocation(tg=self.view_tg)
            self.rotation = AvatarRotation(tg=self.view_tg)
            self.distance = AvatarDistance(tg=self.view_tg)
            self.perspective = AvatarPerspective(tg=self.view_tg)
            self.width = AvatarWidth(tg=self.view_tg)
            self.height = AvatarHeight(tg=self.view_tg)
            self.lens = AvatarLens(tg=self.view_tg)
            self.scene_node_id = AvatarScene(tg=self.view_tg)

    @classmethod
    def cb_receive_node_destroy(cls, session, node_id):
        """
        This method is called, when server destroyed avatar with node_id
        """
        # Remove item from collection of properties
        wm = bpy.context.window_manager
        index = 0
        for item in wm.verse_avatars:
            if item.node_id == node_id:
                wm.verse_avatars.remove(index)
                if wm.cur_verse_avatar_index >= index:
                    wm.cur_verse_avatar_index -= 1
                break
            index += 1
        cls.__other_views.pop(node_id)
        # Force redraw of 3D view
        ui.update_all_views(('VIEW_3D',))
        return super(AvatarView, cls).cb_receive_node_destroy(session, node_id)

    def update(self, context):
        """
        This method tries to update members according context
        """
        
        self.cur_screen = context.screen
        self.cur_area = context.area
        
        # Location of avatar
        if tuple(context.space_data.region_3d.view_location) != self.location.value:
            self.location.value = tuple(context.space_data.region_3d.view_location)
    
        # Rotation around location point
        if tuple(context.space_data.region_3d.view_rotation) != self.rotation.value:
            self.rotation.value = tuple(context.space_data.region_3d.view_rotation)
    
        # Distance from location point
        if context.space_data.region_3d.view_distance != self.distance.value[0]:
            self.distance.value = (context.space_data.region_3d.view_distance,)
        
        # Perspective/Orthogonal
        if context.space_data.region_3d.view_perspective != self.perspective.value[0]:
            self.perspective.value = (context.space_data.region_3d.view_perspective,)
        
        # Lens
        if context.space_data.lens != self.lens.value[0]:
            self.lens.value = (context.space_data.lens,)
                
        # Width
        if context.area.width != self.width.value[0]:
            self.width.value = (context.area.width,)
        
        # Height
        if context.area.height != self.height.value[0]:
            self.height.value = (context.area.height,)

    def draw(self, context):
        """
        Draw avatar view in given context
        """
        # TODO: Add this color to Add-on option
        color = (1.0, 1.0, 0.5, 1.0)
        alpha = 2.0 * math.atan((18.0 / 2.0) / self.lens.value[0])
        dist = 0.5 / (math.tan(alpha / 2.0))
        if self.height.value[0] == 0:
            width = 0.7
        else:
            width = self.width.value[0] / self.height.value[0]
                    
        points = dict()
        points['border'] = [None, None, None, None]
        points['center'] = [None]
        
        # Points of face
        points['right_eye'] = [
            mathutils.Vector((0.25, 0.25, self.distance.value[0] - dist)),
            mathutils.Vector((0.3, 0.25, self.distance.value[0] - dist)),
            mathutils.Vector((0.3, 0.0, self.distance.value[0] - dist)),
            mathutils.Vector((0.25, 0.0, self.distance.value[0] - dist)),
            mathutils.Vector((0.25, 0.25, self.distance.value[0] - dist))
        ]
        points['left_eye'] = [
            mathutils.Vector((-0.25, 0.25, self.distance.value[0] - dist)),
            mathutils.Vector((-0.3, 0.25, self.distance.value[0] - dist)),
            mathutils.Vector((-0.3, 0.0, self.distance.value[0] - dist)),
            mathutils.Vector((-0.25, 0.0, self.distance.value[0] - dist)),
            mathutils.Vector((-0.25, 0.25, self.distance.value[0] - dist))
        ]
        
        points['mouth'] = [
            mathutils.Vector((-0.40912365913391113, -0.11777058243751526, self.distance.value[0] - dist)),
            mathutils.Vector((-0.3441678285598755, -0.15873458981513977, self.distance.value[0] - dist)),
            mathutils.Vector((-0.2563667893409729, -0.1998385488986969, self.distance.value[0] - dist)),
            mathutils.Vector((-0.18191590905189514, -0.22385218739509583, self.distance.value[0] - dist)),
            mathutils.Vector((-0.10375960171222687, -0.23957833647727966, self.distance.value[0] - dist)),
            mathutils.Vector((0.0, -0.2464955747127533, self.distance.value[0] - dist)),
            mathutils.Vector((0.10375960171222687, -0.23957833647727966, self.distance.value[0] - dist)),
            mathutils.Vector((0.18191590905189514, -0.22385218739509583, self.distance.value[0] - dist)),
            mathutils.Vector((0.2563667893409729, -0.1998385488986969, self.distance.value[0] - dist)),
            mathutils.Vector((0.3441678285598755, -0.15873458981513977, self.distance.value[0] - dist)),
            mathutils.Vector((0.40912365913391113, -0.11777058243751526, self.distance.value[0] - dist))
        ]
                
        # Put border points of camera to basic position
        points['border'][0] = mathutils.Vector((
            -width / 2.0,
            -0.5,
            self.distance.value[0] - dist,
            1.0
        ))
        points['border'][1] = mathutils.Vector((
            width / 2.0,
            -0.5,
            self.distance.value[0] - dist,
            1.0
        ))
        points['border'][2] = mathutils.Vector((
            width / 2.0,
            0.5,
            self.distance.value[0] - dist,
            1.0
        ))
        points['border'][3] = mathutils.Vector((
            -width / 2.0,
            0.5,
            self.distance.value[0] - dist,
            1.0
        ))
        
        # Center of view
        points['center'][0] = mathutils.Vector((
            0.0,
            0.0,
            self.distance.value[0],
            1.0
        ))
        
        # Create transformation (rotation) matrix
        rot_matrix = mathutils.Quaternion(self.rotation.value).to_matrix().to_4x4()
        
        # Transform points in all point groups
        for point_group in points.values():
            for index in range(len(point_group)):
                # Rotate points
                point_group[index] = (rot_matrix * point_group[index]).to_3d()
                # Move points
                point_group[index] += mathutils.Vector(self.location.value)

        border = points['border']
        center = points['center']

        # Store glColor4f
        col_prev = bgl.Buffer(bgl.GL_FLOAT, [4])
        bgl.glGetFloatv(bgl.GL_COLOR, col_prev)

        bgl.glColor4f(color[0], color[1], color[2], color[3])

        # Draw username
        coord_2d = location_3d_to_region_2d(
            context.region,
            context.space_data.region_3d,
            center[0])

        # When coordinates are not outside window, then draw the name of avatar
        if coord_2d is not None:
            # TODO: add to Add-on options
            font_id, font_size, my_dpi = 0, 12, 72
            blf.size(font_id, font_size, my_dpi)
            blf.position(font_id, coord_2d[0] + 2, coord_2d[1] + 2, 0)
            blf.draw(font_id, str(self.username))

        # Get & convert the Perspective Matrix of the current view/region.
        persp_matrix = context.space_data.region_3d.perspective_matrix
        temp_mat = [persp_matrix[j][i] for i in range(4) for j in range(4)]
        persp_buff = bgl.Buffer(bgl.GL_FLOAT, 16, temp_mat)
    
        # Store previous OpenGL settings.
        # Store MatrixMode
        matrix_mode_prev = bgl.Buffer(bgl.GL_INT, [1])
        bgl.glGetIntegerv(bgl.GL_MATRIX_MODE, matrix_mode_prev)
        matrix_mode_prev = matrix_mode_prev[0]
    
        # Store projection matrix
        proj_matrix_prev = bgl.Buffer(bgl.GL_DOUBLE, [16])
        bgl.glGetFloatv(bgl.GL_PROJECTION_MATRIX, proj_matrix_prev)
    
        # Store Line width
        line_width_prev = bgl.Buffer(bgl.GL_FLOAT, [1])
        bgl.glGetFloatv(bgl.GL_LINE_WIDTH, line_width_prev)
        line_width_prev = line_width_prev[0]
    
        # Store GL_BLEND
        blend_prev = bgl.Buffer(bgl.GL_BYTE, [1])
        bgl.glGetFloatv(bgl.GL_BLEND, blend_prev)
        blend_prev = blend_prev[0]
        
        # Store GL_DEPTH_TEST
        depth_test_prev = bgl.Buffer(bgl.GL_BYTE, [1])
        bgl.glGetFloatv(bgl.GL_DEPTH_TEST, depth_test_prev)
        depth_test_prev = depth_test_prev[0]
            
        # Store GL_LINE_STIPPLE
        line_stipple_prev = bgl.Buffer(bgl.GL_BYTE, [1])
        bgl.glGetFloatv(bgl.GL_LINE_STIPPLE, line_stipple_prev)
        line_stipple_prev = line_stipple_prev[0]
        
        # Prepare for 3D drawing
        bgl.glLoadIdentity()
        bgl.glMatrixMode(bgl.GL_PROJECTION)
        bgl.glLoadMatrixf(persp_buff)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
                
        # Draw "Look At" point
        bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glColor4f(color[0], color[1], color[2], color[3])
        
        bgl.glVertex3f(
            self.location.value[0] + 0.1,
            self.location.value[1],
            self.location.value[2]
        )
        bgl.glVertex3f(
            self.location.value[0] - 0.1,
            self.location.value[1],
            self.location.value[2]
        )
        
        bgl.glVertex3f(
            self.location.value[0],
            self.location.value[1] + 0.1,
            self.location.value[2]
        )
        bgl.glVertex3f(
            self.location.value[0],
            self.location.value[1] - 0.1,
            self.location.value[2]
        )
        
        bgl.glVertex3f(
            self.location.value[0],
            self.location.value[1],
            self.location.value[2] + 0.1
        )
        bgl.glVertex3f(
            self.location.value[0],
            self.location.value[1],
            self.location.value[2] - 0.1
        )
        
        bgl.glEnd()

        # Draw border of camera
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex3f(border[0][0], border[0][1], border[0][2])
        bgl.glVertex3f(border[1][0], border[1][1], border[1][2])
        bgl.glVertex3f(border[2][0], border[2][1], border[2][2])
        bgl.glVertex3f(border[3][0], border[3][1], border[3][2])
        bgl.glVertex3f(border[0][0], border[0][1], border[0][2])
        bgl.glEnd()
        
        # Draw left eye
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for point in points['left_eye']:
            bgl.glVertex3f(point[0], point[1], point[2])
        bgl.glEnd()

        # Draw right eye
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for point in points['right_eye']:
            bgl.glVertex3f(point[0], point[1], point[2])
        bgl.glEnd()
        
        # Draw mouth
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for point in points['mouth']:
            bgl.glVertex3f(point[0], point[1], point[2])
        bgl.glEnd()
        
        # Draw dashed lines from center of "camera" to border of camera        
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(border[0][0], border[0][1], border[0][2])
        bgl.glVertex3f(center[0][0], center[0][1], center[0][2])
        bgl.glVertex3f(border[1][0], border[1][1], border[1][2])
        bgl.glVertex3f(center[0][0], center[0][1], center[0][2])
        bgl.glVertex3f(border[2][0], border[2][1], border[2][2])
        bgl.glVertex3f(center[0][0], center[0][1], center[0][2])
        bgl.glVertex3f(border[3][0], border[3][1], border[3][2])
        bgl.glVertex3f(center[0][0], center[0][1], center[0][2])
        bgl.glEnd()
        
        # Draw dashed line from Look At point and center of camera
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(
            self.location.value[0],
            self.location.value[1],
            self.location.value[2]
        )
        bgl.glVertex3f(center[0][0], center[0][1], center[0][2])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STIPPLE)

        # Restore previous OpenGL settings
        bgl.glLoadIdentity()
        bgl.glMatrixMode(matrix_mode_prev)
        bgl.glLoadMatrixf(proj_matrix_prev)
        bgl.glLineWidth(line_width_prev)
        if not blend_prev:
            bgl.glDisable(bgl.GL_BLEND)
        if not line_stipple_prev:
            bgl.glDisable(bgl.GL_LINE_STIPPLE)
        if not depth_test_prev:
            bgl.glDisable(bgl.GL_DEPTH_TEST)

        bgl.glColor4f(col_prev[0], col_prev[1], col_prev[2], col_prev[3])
