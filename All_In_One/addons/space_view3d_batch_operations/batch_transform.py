#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

#============================================================================#

import bpy

import math
import time
import json

from mathutils import Color, Vector, Euler, Quaternion, Matrix

try:
    import dairin0d
    dairin0d_location = ""
except ImportError:
    dairin0d_location = "."

exec("""
from {0}dairin0d.utils_math import matrix_compose, matrix_decompose, matrix_inverted_safe
from {0}dairin0d.utils_python import setattr_cmp, setitem_cmp
from {0}dairin0d.utils_view3d import SmartView3D
from {0}dairin0d.utils_blender import Selection
from {0}dairin0d.utils_userinput import KeyMapUtils
from {0}dairin0d.utils_ui import NestedLayout, tag_redraw, rv3d_from_region
from {0}dairin0d.bpy_inspect import prop, BlRna, BlEnums, bpy_struct
from {0}dairin0d.utils_accumulation import Aggregator, VectorAggregator
from {0}dairin0d.utils_addon import AddonManager, UIMonitor
""".format(dairin0d_location))

from .batch_common import (
    copyattrs, attrs_to_dict, dict_to_attrs, PatternRenamer,
    Pick_Base, LeftRightPanel, make_category,
    round_to_bool, is_visible, has_common_layers, idnames_separator,
)

addon = AddonManager()

"""
TODO:
* sync coordsystems/summaries/etc. between 3D views
* Pick transform? (respecting axis locks)
* \\ (batch) apply location/rotation/scale/etc. (in Object mode) -- the builtin Apply Object Transform operator already does that
* \\ (batch) change origin of geometry -- the builtin Set Origin operator already does that
* cursor/bookmark/etc. to active/min/max/center/mean/median? (in global or original coodinates)?
* Vector swizzle? (evaluate as python expression? e.g. w,x,y,z -> -w,0.5*z,y,2*x) (apply to summary or to each individual object?)
* Per-summary copy/paste (respecting uniformity locks) (option: using units or the raw values ?)
* Per-vector copy/paste (respecting uniformity locks) (option: using units or the raw values ?)
* Coordinate systems
    * \\ built-in coordinate systems should be not editable ?
    * "local grid" rendering (around object / cursor / etc.)
    * CAD-like guides?
      Guides can be used for snapping during transform, but normal snapping
      is ignored by the Knife tool. However, guides can be used to at least
      visually show where to move the knife
    * Bookmarks
* Other modes
* 3D cursor

* VIEW coordsystem:
    * this is better be independent for each 3D view, since manipulator/transform-orientation are per-3D-view anyway
    * should be able to optionally specify a camera (if not specified, then last active 3D region is used)

* make buttons to zero/reset objects' pos/rot/scale in current coordiante system
  also: make sure it's possibe to invoke it via a keyboard shortcut

Investigate:
* moth3r asks if it's possible to rotate/scale around different point than each object's origin
* Spatial queries? ("select all objects wich satisfy the following conditions")
* Manhattan distance as one of the coordsys Space options?

* "Transform box"? (for visual "box" transformation as seen in some other apps)

? "geometry" summary is too complicated to calculate in background (+ needs conversion to mesh anyway)
  but might be feasible as a on-request calculation

From http://wiki.blender.org/index.php/Dev:Doc/Quick_Hacks
- Use of 3d manipulator to move and scale Texture Space?

see also: http://modo.docs.thefoundry.co.uk/modo/601/help/pages/modotoolbox/ActionCenters.html
also: work plane?

See Modo's Absolute Scaling
https://www.youtube.com/watch?v=79BAHXLX9JQ
http://community.thefoundry.co.uk/discussion/topic.aspx?f=33&t=34229
see scale_in_modo.mov for ideas
fusion 360 has a lot of cool features (moth3r says it's the most user-friendly CAD)

\\ Ivan suggests to check the booleans addon (to test for possible conflicts)
\\ Ivan suggests to report blender bugs
Ivan asks to ignore modes that aren't implemented yet (right now it prints lots of errors)

documentation (Ivan suggests to use his taser model for illustrations)
(what's working, what's not)
(no need to explain what's not working)
(Ivan suggests to post on forum after he makes video tutorial)
"""

#============================================================================#
Category_Name = "Transform"
CATEGORY_NAME = Category_Name.upper()
category_name = Category_Name.lower()
Category_Name_Plural = "Transforms"
CATEGORY_NAME_PLURAL = Category_Name_Plural.upper()
category_name_plural = Category_Name_Plural.lower()
category_icon = 'MANIPUL'

#============================================================================#


# Particles are used in the following situations:
# - as subjects of transformation
# - as reference point(s) for cursor transformation
# Note: particles 'dragged' by Proportional Editing
# are a separate issue (they can come and go).
def gather_particles(**kwargs):
    context = kwargs.get("context", bpy.context)

    area_type = kwargs.get("area_type", context.area.type)

    scene = kwargs.get("scene", context.scene)

    space_data = kwargs.get("space_data", context.space_data)
    region_data = kwargs.get("region_data", context.region_data)

    particles = []
    pivots = {}
    normal_system = None

    active_element = None
    cursor_pos = None
    median = None

    if area_type == 'VIEW_3D':
        context_mode = kwargs.get("context_mode", context.mode)

        selected_objects = kwargs.get("selected_objects",
            context.selected_objects)

        active_object = kwargs.get("active_object",
            context.active_object)

        if context_mode == 'OBJECT':
            for obj in selected_objects:
                particle = View3D_Object(obj)
                particles.append(particle)

            if active_object:
                active_element = active_object.\
                    matrix_world.to_translation()

        # On Undo/Redo scene hash value is changed ->
        # -> the monitor tries to update the CSU ->
        # -> object.mode_set seem to somehow conflict
        # with Undo/Redo mechanisms.
        elif active_object and active_object.data and \
        (context_mode in {
        'EDIT_MESH', 'EDIT_METABALL',
        'EDIT_CURVE', 'EDIT_SURFACE',
        'EDIT_ARMATURE', 'POSE'}):

            m = active_object.matrix_world

            positions = []
            normal = Vector((0, 0, 0))

            if context_mode == 'EDIT_MESH':
                bm = bmesh.from_edit_mesh(active_object.data)

                if bm.select_history:
                    elem = bm.select_history[-1]
                    if isinstance(elem, bmesh.types.BMVert):
                        active_element = elem.co.copy()
                    else:
                        active_element = Vector()
                        for v in elem.verts:
                            active_element += v.co
                        active_element *= 1.0 / len(elem.verts)

                for v in bm.verts:
                    if v.select:
                        positions.append(v.co)
                        normal += v.normal

                # mimic Blender's behavior (as of now,
                # order of selection is ignored)
                if len(positions) == 2:
                    normal = positions[1] - positions[0]
                elif len(positions) == 3:
                    a = positions[0] - positions[1]
                    b = positions[2] - positions[1]
                    normal = a.cross(b)
            elif context_mode == 'EDIT_METABALL':
                active_elem = active_object.data.elements.active
                if active_elem:
                    active_element = active_elem.co.copy()
                    active_element = active_object.\
                        matrix_world * active_element

                # Currently there is no API for element.select
                #for element in active_object.data.elements:
                #    if element.select:
                #        positions.append(element.co)
            elif context_mode == 'EDIT_ARMATURE':
                # active bone seems to have the same pivot
                # as median of the selection
                '''
                active_bone = active_object.data.edit_bones.active
                if active_bone:
                    active_element = active_bone.head + \
                                     active_bone.tail
                    active_element = active_object.\
                        matrix_world * active_element
                '''

                for bone in active_object.data.edit_bones:
                    if bone.select_head:
                        positions.append(bone.head)
                    if bone.select_tail:
                        positions.append(bone.tail)
            elif context_mode == 'POSE':
                active_bone = active_object.data.bones.active
                if active_bone:
                    active_element = active_bone.\
                        matrix_local.translation.to_3d()
                    active_element = active_object.\
                        matrix_world * active_element

                # consider only topmost parents
                bones = set()
                for bone in active_object.data.bones:
                    if bone.select:
                        bones.add(bone)

                parents = set()
                for bone in bones:
                    if not set(bone.parent_recursive).intersection(bones):
                        parents.add(bone)

                for bone in parents:
                    positions.append(bone.matrix_local.translation.to_3d())
            else:
                for spline in active_object.data.splines:
                    for point in spline.bezier_points:
                        if point.select_control_point:
                            positions.append(point.co)
                        else:
                            if point.select_left_handle:
                                positions.append(point.handle_left)
                            if point.select_right_handle:
                                positions.append(point.handle_right)

                        n = None
                        nL = point.co - point.handle_left
                        nR = point.co - point.handle_right
                        #nL = point.handle_left.copy()
                        #nR = point.handle_right.copy()
                        if point.select_control_point:
                            n = nL + nR
                        elif point.select_left_handle or \
                             point.select_right_handle:
                            n = nL + nR
                        else:
                            if point.select_left_handle:
                                n = -nL
                            if point.select_right_handle:
                                n = nR

                        if n is not None:
                            if n.length_squared < epsilon:
                                n = -nL
                            normal += n.normalized()

                    for point in spline.points:
                        if point.select:
                            positions.append(point.co)

            if len(positions) != 0:
                if normal.length_squared < epsilon:
                    normal = Vector((0, 0, 1))
                normal.rotate(m)
                normal.normalize()

                if (1.0 - abs(normal.z)) < epsilon:
                    t1 = Vector((1, 0, 0))
                else:
                    t1 = Vector((0, 0, 1)).cross(normal)
                t2 = t1.cross(normal)
                normal_system = MatrixCompose(t1, t2, normal)

                median, bbox_center = calc_median_bbox_pivots(positions)
                median = m * median
                bbox_center = m * bbox_center

                # Currently I don't know how to get active mesh element
                if active_element is None:
                    if context_mode == 'EDIT_ARMATURE':
                        # Somewhy EDIT_ARMATURE has such behavior
                        active_element = bbox_center
                    else:
                        active_element = median
            else:
                if active_element is None:
                    active_element = active_object.\
                        matrix_world.to_translation()

                median = active_element
                bbox_center = active_element

                normal_system = active_object.matrix_world.to_3x3()
                normal_system.col[0].normalize()
                normal_system.col[1].normalize()
                normal_system.col[2].normalize()
        else:
            # paint/sculpt, etc.?
            particle = View3D_Object(active_object)
            particles.append(particle)

            if active_object:
                active_element = active_object.\
                    matrix_world.to_translation()

        cursor_pos = get_cursor_location(v3d=space_data)

    #elif area_type == 'IMAGE_EDITOR':
        # currently there is no way to get UV editor's
        # offset (and maybe some other parameters
        # required to implement these operators)
        #cursor_pos = space_data.uv_editor.cursor_location

    #elif area_type == 'EMPTY':
    #elif area_type == 'GRAPH_EDITOR':
    #elif area_type == 'OUTLINER':
    #elif area_type == 'PROPERTIES':
    #elif area_type == 'FILE_BROWSER':
    #elif area_type == 'INFO':
    #elif area_type == 'SEQUENCE_EDITOR':
    #elif area_type == 'TEXT_EDITOR':
    #elif area_type == 'AUDIO_WINDOW':
    #elif area_type == 'DOPESHEET_EDITOR':
    #elif area_type == 'NLA_EDITOR':
    #elif area_type == 'SCRIPTS_WINDOW':
    #elif area_type == 'TIMELINE':
    #elif area_type == 'NODE_EDITOR':
    #elif area_type == 'LOGIC_EDITOR':
    #elif area_type == 'CONSOLE':
    #elif area_type == 'USER_PREFERENCES':

    else:
        print("gather_particles() not implemented for '{}'".format(area_type))
        return None, None

    # 'INDIVIDUAL_ORIGINS' is not handled here

    if cursor_pos:
        pivots['CURSOR'] = cursor_pos.copy()

    if active_element:
        # in v3d: ACTIVE_ELEMENT
        pivots['ACTIVE'] = active_element.copy()

    if (len(particles) != 0) and (median is None):
        positions = (p.get_location() for p in particles)
        median, bbox_center = calc_median_bbox_pivots(positions)

    if median:
        # in v3d: MEDIAN_POINT, in UV editor: MEDIAN
        pivots['MEDIAN'] = median.copy()
        # in v3d: BOUNDING_BOX_CENTER, in UV editor: CENTER
        pivots['CENTER'] = bbox_center.copy()

    csu = CoordinateSystemUtility(scene, space_data, region_data, \
        pivots, normal_system)

    return particles, csu

def calc_median_bbox_pivots(positions):
    median = None # pos can be 3D or 2D
    bbox = [None, None]

    n = 0
    for pos in positions:
        extend_bbox(bbox, pos)
        try:
            median += pos
        except:
            median = pos.copy()
        n += 1

    median = median / n
    bbox_center = (Vector(bbox[0]) + Vector(bbox[1])) * 0.5

    return median, bbox_center

def extend_bbox(bbox, pos):
    try:
        bbox[0] = tuple(min(e0, e1) for e0, e1 in zip(bbox[0], pos))
        bbox[1] = tuple(max(e0, e1) for e0, e1 in zip(bbox[1], pos))
    except:
        bbox[0] = tuple(pos)
        bbox[1] = tuple(pos)


# ====== COORDINATE SYSTEM UTILITY ====== #
class CoordinateSystemUtility:
    pivot_name_map = {
        'CENTER':'CENTER',
        'BOUNDING_BOX_CENTER':'CENTER',
        'MEDIAN':'MEDIAN',
        'MEDIAN_POINT':'MEDIAN',
        'CURSOR':'CURSOR',
        'INDIVIDUAL_ORIGINS':'INDIVIDUAL',
        'ACTIVE_ELEMENT':'ACTIVE',
        'WORLD':'WORLD',
        'SURFACE':'SURFACE', # ?
        'BOOKMARK':'BOOKMARK',
    }
    pivot_v3d_map = {
        'CENTER':'BOUNDING_BOX_CENTER',
        'MEDIAN':'MEDIAN_POINT',
        'CURSOR':'CURSOR',
        'INDIVIDUAL':'INDIVIDUAL_ORIGINS',
        'ACTIVE':'ACTIVE_ELEMENT',
    }

    def __init__(self, scene, space_data, region_data, \
                 pivots, normal_system):
        self.space_data = space_data
        self.region_data = region_data

        if space_data.type == 'VIEW_3D':
            self.pivot_map_inv = self.pivot_v3d_map

        self.tou = TransformOrientationUtility(
            scene, space_data, region_data)
        self.tou.normal_system = normal_system

        self.pivots = pivots

        # Assigned by caller (for cursor or selection)
        self.source_pos = None
        self.source_rot = None
        self.source_scale = None

    def set_orientation(self, name):
        self.tou.set(name)

    def set_pivot(self, pivot):
        self.space_data.pivot_point = self.pivot_map_inv[pivot]

    def get_pivot_name(self, name=None, relative=None, raw=False):
        pivot = self.pivot_name_map[self.space_data.pivot_point]
        if raw:
            return pivot

        if not name:
            name = self.tou.get()

        if relative is None:
            settings = find_settings()
            tfm_opts = settings.transform_options
            relative = tfm_opts.use_relative_coords

        if relative:
            pivot = "RELATIVE"
        elif (name == 'GLOBAL') or (pivot == 'WORLD'):
            pivot = 'WORLD'
        elif (name == "Surface") or (pivot == 'SURFACE'):
            pivot = "SURFACE"

        return pivot

    def get_origin(self, name=None, relative=None, pivot=None):
        if not pivot:
            pivot = self.get_pivot_name(name, relative)

        if relative or (pivot == "RELATIVE"):
            # "relative" parameter overrides "pivot"
            return self.source_pos
        elif pivot == 'WORLD':
            return Vector()
        elif pivot == "SURFACE":
            runtime_settings = find_runtime_settings()
            return Vector(runtime_settings.surface_pos)
        else:
            if pivot == 'INDIVIDUAL':
                pivot = 'MEDIAN'

            #if pivot == 'ACTIVE':
            #    print(self.pivots)

            try:
                return self.pivots[pivot]
            except:
                return Vector()

    def get_matrix(self, name=None, relative=None, pivot=None):
        if not name:
            name = self.tou.get()

        matrix = self.tou.get_matrix(name)

        if isinstance(pivot, Vector):
            pos = pivot
        else:
            pos = self.get_origin(name, relative, pivot)

        return to_matrix4x4(matrix, pos)

# ====== TRANSFORM ORIENTATION UTILITIES ====== #
class TransformOrientationUtility:
    special_systems = {"Surface", "Scaled"}
    predefined_systems = {
        'GLOBAL', 'LOCAL', 'VIEW', 'NORMAL', 'GIMBAL',
        "Scaled", "Surface",
    }

    def __init__(self, scene, v3d, rv3d):
        self.scene = scene
        self.v3d = v3d
        self.rv3d = rv3d

        self.custom_systems = [item for item in scene.orientations \
            if item.name not in self.special_systems]

        self.is_custom = False
        self.custom_id = -1

        # This is calculated elsewhere
        self.normal_system = None

        self.set(v3d.transform_orientation)

    def get(self):
        return self.transform_orientation

    def get_title(self):
        if self.is_custom:
            return self.transform_orientation

        name = self.transform_orientation
        return name[:1].upper() + name[1:].lower()

    def set(self, name, set_v3d=True):
        if isinstance(name, int):
            n = len(self.custom_systems)
            if n == 0:
                # No custom systems, do nothing
                return

            increment = name

            if self.is_custom:
                # If already custom, switch to next custom system
                self.custom_id = (self.custom_id + increment) % n

            self.is_custom = True

            name = self.custom_systems[self.custom_id].name
        else:
            self.is_custom = name not in self.predefined_systems

            if self.is_custom:
                self.custom_id = next((i for i, v in \
                    enumerate(self.custom_systems) if v.name == name), -1)

            if name in self.special_systems:
                # Ensure such system exists
                self.get_custom(name)

        self.transform_orientation = name

        if set_v3d:
            self.v3d.transform_orientation = name

    def get_matrix(self, name=None):
        active_obj = self.scene.objects.active

        if not name:
            name = self.transform_orientation

        if self.is_custom:
            matrix = self.custom_systems[self.custom_id].matrix.copy()
        else:
            if (name == 'VIEW') and self.rv3d:
                matrix = self.rv3d.view_rotation.to_matrix()
            elif name == "Surface":
                matrix = self.get_custom(name).matrix.copy()
            elif (name == 'GLOBAL') or (not active_obj):
                matrix = Matrix().to_3x3()
            elif (name == 'NORMAL') and self.normal_system:
                matrix = self.normal_system.copy()
            else:
                matrix = active_obj.matrix_world.to_3x3()
                if name == "Scaled":
                    self.get_custom(name).matrix = matrix
                else: # 'LOCAL', 'GIMBAL', ['NORMAL'] for now
                    matrix[0].normalize()
                    matrix[1].normalize()
                    matrix[2].normalize()

        return matrix

    def get_custom(self, name):
        try:
            return self.scene.orientations[name]
        except:
            return create_transform_orientation(
                self.scene, name, Matrix())

# Is there a less cumbersome way to create transform orientation?
def create_transform_orientation(scene, name=None, matrix=None):
    active_obj = scene.objects.active
    prev_mode = None

    if active_obj:
        prev_mode = active_obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        bpy.ops.object.add()

    # ATTENTION! This uses context's scene
    bpy.ops.transform.create_orientation()

    tfm_orient = scene.orientations[-1]

    if name is not None:
        basename = name
        i = 1
        while name in scene.orientations:
            name = "%s.%03i" % (basename, i)
            i += 1
        tfm_orient.name = name

    if matrix:
        tfm_orient.matrix = matrix.to_3x3()

    if active_obj:
        bpy.ops.object.mode_set(mode=prev_mode)
    else:
        bpy.ops.object.delete()

    return tfm_orient

################################################################################################
################################################################################################
################################################################################################


def convert_obj_rotation(src_mode, q, aa, e, dst_mode, always4=False):
    if src_mode == dst_mode: # and coordsystem is 'BASIS'
        if src_mode == 'QUATERNION':
            R = Quaternion(q)
        elif src_mode == 'AXIS_ANGLE':
            R = Vector(aa)
        else:
            R = Euler(e)
    else:
        if src_mode == 'QUATERNION':
            R = Quaternion(q)
        elif src_mode == 'AXIS_ANGLE':
            R = Quaternion(aa[1:], aa[0])
        else:
            R = Euler(e).to_quaternion()
        
        if dst_mode == 'QUATERNION':
            pass # already quaternion
        elif dst_mode == 'AXIS_ANGLE':
            R = R.to_axis_angle()
            R = Vector((R[1], R[0].x, R[0].y, R[0].z))
        else:
            R = R.to_euler(dst_mode)
    
    if always4:
        if len(R) == 4: R = Vector(R)
        else: R = Vector((0.0, R[0], R[1], R[2]))
    
    return R

def apply_obj_rotation(obj, R, mode):
    if (len(R) == 4) and (mode not in ('QUATERNION', 'AXIS_ANGLE')): R = R[1:]
    
    if obj.rotation_mode == mode: # and coordsystem is 'BASIS'
        if mode == 'QUATERNION':
            obj.rotation_quaternion = Quaternion(R)
        elif mode == 'AXIS_ANGLE':
            obj.rotation_axis_angle = tuple(R)
        else:
            obj.rotation_euler = Euler(R)
    else:
        if mode == 'QUATERNION':
            R = Quaternion(R)
        elif mode == 'AXIS_ANGLE':
            R = Quaternion(R[1:], R[0])
        else:
            R = Euler(R).to_quaternion()
        
        if obj.rotation_mode == 'QUATERNION':
            obj.rotation_quaternion = R
        elif obj.rotation_mode == 'AXIS_ANGLE':
            R = R.to_axis_angle()
            R = Vector((R[1], R[0].x, R[0].y, R[0].z))
            obj.rotation_axis_angle = R
        else:
            R = R.to_euler(obj.rotation_mode)
            obj.rotation_euler = R

def get_vertex_pos(obj, i, undeformed=False):
    if (not obj) or (i < 0): return Vector()
    if obj.type == 'MESH':
        if (i >= len(obj.data.vertices)): return Vector()
        v = obj.data.vertices[i]
        return Vector(v.undeformed_co if undeformed else v.co)
    elif obj.type in ('CURVE', 'SURFACE'):
        for spline in obj.data.splines:
            points = (spline.bezier_points if spline.type == 'BEZIER' else spline.points)
            if i >= len(points):
                i -= len(points)
            else:
                return Vector(points[i].co)
        return Vector()
    elif obj.type == 'LATTICE':
        if (i >= len(obj.data.points)): return Vector()
        p = obj.data.points[i]
        return Vector(v.co if undeformed else v.co_deform)
    else:
        return Vector()

def get_world_matrix(obj, bone_name=""):
    if not obj: return Matrix()
    if bone_name:
        obj = obj.id_data # in case obj is a PoseBone
        if obj.type == 'ARMATURE':
            bone = obj.pose.bones.get(bone_name)
            if bone: return bone.matrix_world
    return obj.matrix_world # works for Object, PoseBone

def get_parent_matrix(obj):
    if not obj: return Matrix()
    parent = obj.parent
    if not parent: return Matrix()
    
    parent_type = getattr(obj, "parent_type", 'OBJECT')
    if parent_type == 'BONE': # NOT TESTED
        parent_bone = parent.pose.bones.get(obj.parent_bone)
        if not parent_bone: return parent.matrix_world
        return parent_bone.matrix_world
    elif parent_type == 'VERTEX': # NOT TESTED
        v = get_vertex_pos(parent, obj.parent_vertices[0])
        return Matrix.Translation(parent.matrix_world * v)
    elif parent_type == 'VERTEX_3': # NOT TESTED
        pm = parent.matrix_world
        v0 = pm * get_vertex_pos(parent, obj.parent_vertices[0])
        v1 = pm * get_vertex_pos(parent, obj.parent_vertices[1])
        v2 = pm * get_vertex_pos(parent, obj.parent_vertices[2])
        t = v0
        x = (v1 - v0).normalized()
        y = (v2 - v0).normalized()
        z = x.cross(y).normalized()
        return matrix_compose(x, y, z, t)
    else:
        # I don't know how CURVE and KEY are supposed to behave,
        # so for now I just treat them the same as OBJECT/ARMATURE
        # LATTICE isn't a rigid-body/affine transformation either
        return parent.matrix_world

def cam_proj_params(cam, scene):
    render = scene.render
    w = render.resolution_x * render.pixel_aspect_x
    h = render.resolution_y * render.pixel_aspect_y
    if cam.sensor_fit == 'HORIZONTAL':
        wh_norm = w
        sensor_size = cam.sensor_width
    elif cam.sensor_fit == 'VERTICAL':
        wh_norm = h
        sensor_size = cam.sensor_height
    else:
        wh_norm = max(w, h)
        sensor_size = cam.sensor_width
    w = w / wh_norm
    h = h / wh_norm
    
    if cam.type == 'ORTHO':
        persp = 0.0
        scale = cam.ortho_scale
        sx = w * scale
        sy = h * scale
        dx = cam.shift_x * scale
        dy = cam.shift_y * scale
        dz = scale
    else:
        persp = 1.0
        sx = w
        sy = h
        dx = cam.shift_x
        dy = cam.shift_y
        dz = cam.lens / sensor_size
    
    return (Vector((sx, sy, persp)), Vector((dx, dy, dz)))

class CoordSystemMatrix:
    def __init__(self, coordsys=None, sv=None):
        self.update(coordsys, sv)
    
    def update(self, coordsys, sv=None):
        if coordsys:
            aspect = coordsys.aspect_L
            self.L = (aspect.mode, aspect.obj_name, aspect.bone_name)
            aspect = coordsys.aspect_R
            self.R = (aspect.mode, aspect.obj_name, aspect.bone_name)
            aspect = coordsys.aspect_S
            self.S = (aspect.mode, aspect.obj_name, aspect.bone_name)
            self.extra_matrix = coordsys.extra_matrix
        else:
            self.L = ('GLOBAL', "", "")
            self.R = ('GLOBAL', "", "")
            self.S = ('GLOBAL', "", "")
            self.extra_matrix = Matrix()
        
        self.sv = sv
        self.vm, self.vp = self.calc_view_matrix()
        
        # Cached values are the same for any object/element
        self._cached_all = None
        self._cached_t = None
        self._cached_xyz = None
        self._cached_s = None
    
    # The "basis" location/rotation/scale can be used with objects and pose-bones
    # (they have the same the transform-related attributes, even locks!)
    # Meta-elements have pos/rot/scale too, but nothing more advanced.
    # However, meta-elements can also be coerced to the same behavior, to some extent
    
    def calc_view_matrix(self):
        if not self.sv: return (Matrix(), Vector((1,1,0)))
        m = matrix_compose(self.sv.right, self.sv.up, self.sv.forward, self.sv.viewpoint)
        m3 = m.to_3x3()
        s, d = self.sv.proj_params
        p = Vector((2.0/s.x, 2.0/s.y, s.z)).lerp(Vector((2.0*d.z/s.x, 2.0*d.z/s.y, s.z)), s.z)
        #x = m3 * Vector((0.5*s.x, 0, 0)).lerp(Vector((0.5*s.x/d.z, 0, 0)), s.z)
        #y = m3 * Vector((0, 0.5*s.y, 0)).lerp(Vector((0, 0.5*s.y/d.z, 0)), s.z)
        x = m3 * Vector((1, 0, 0))
        y = m3 * Vector((0, 1, 0))
        z = m3 * Vector((d.x, d.y, 1.0)).lerp(Vector((d.x/d.z, d.y/d.z, 1.0)), s.z)
        t = m.translation
        return (matrix_compose(x, y, -z, t), p)
    
    def calc_cam_matrix(self, context, cam_name):
        scene = context.scene
        cam_obj = scene.objects.get(cam_name, scene.camera)
        if (not cam_obj) or (not cam_obj.data): return (Matrix(), Vector((1,1,0)))
        m = Matrix(cam_obj.matrix_world)
        m.col[0] *= (1.0 / m.col[0].magnitude)
        m.col[1] *= (1.0 / m.col[1].magnitude)
        m.col[2] *= -(1.0 / m.col[2].magnitude)
        m3 = m.to_3x3()
        s, d = cam_proj_params(cam_obj.data, context.scene)
        p = Vector((2.0/s.x, 2.0/s.y, s.z)).lerp(Vector((2.0*d.z/s.x, 2.0*d.z/s.y, s.z)), s.z)
        #x = m3 * Vector((0.5*s.x, 0, 0)).lerp(Vector((0.5*s.x/d.z, 0, 0)), s.z)
        #y = m3 * Vector((0, 0.5*s.y, 0)).lerp(Vector((0, 0.5*s.y/d.z, 0)), s.z)
        x = m3 * Vector((1, 0, 0))
        y = m3 * Vector((0, 1, 0))
        z = m3 * Vector((d.x, d.y, 1.0)).lerp(Vector((d.x/d.z, d.y/d.z, 1.0)), s.z)
        t = m.translation
        return (matrix_compose(x, y, -z, t), p)
    
    def calc_active_matrix(self, context):
        # TODO: ACTIVE in edit/pose modes
        return get_world_matrix(context.active_object)
    
    _pivot_map = {
        'BOUNDING_BOX_CENTER':'CENTER',
        'CURSOR':'CURSOR',
        'INDIVIDUAL_ORIGINS':'LOCAL',
        'MEDIAN_POINT':'MEAN',
        'ACTIVE_ELEMENT':'ACTIVE',
    }
    def calc_matrix(self, context, obj):
        if self._cached_all: return self._cached_all
        
        persp = Vector((1,1,0))
        pm = None
        lm = None
        am = None
        
        L_mode = self.L[0]
        if L_mode == 'PIVOT': L_mode = self._pivot_map[self.sv.space_data.pivot_point]
        t = self._cached_t
        if not t:
            if L_mode == 'PARENT':
                if not pm: pm = get_parent_matrix(obj)
                t = pm.translation
            elif L_mode == 'LOCAL':
                if not lm: lm = get_world_matrix(obj)
                t = lm.translation
            elif L_mode == 'ACTIVE':
                if not am: am = self.calc_active_matrix(context)
                t = am.translation
                self._cached_t = t
            elif L_mode == 'CAMERA':
                cm, persp = self.calc_cam_matrix(context, self.L[1])
                t = cm.translation
                self._cached_t = t
            elif L_mode == 'VIEW':
                vm, persp = self.vm, self.vp
                t = vm.translation
                self._cached_t = t
            elif L_mode == 'OBJECT':
                _obj = (context.scene.objects.get(self.L[1]) if self.L[1] else context.active_object)
                om = get_world_matrix(_obj, self.L[2])
                t = om.translation
                self._cached_t = t
            #('SURFACE', "Surface", "Raycasted position", 'EDIT'),
            #('CURSOR', "Cursor", "3D cursor position", 'CURSOR'),
            #('BOOKMARK', "Bookmark", "Bookmark position", 'BOOKMARKS'),
            #('MEAN', "Average", "Average of selected items' positions", 'ROTATECENTER'),
            #('CENTER', "Center", "Center of selected items' positions", 'ROTATE'),
            #('MIN', "Min", "Minimum of selected items' positions", 'FRAME_PREV'),
            #('MAX', "Max", "Maximum of selected items' positions", 'FRAME_NEXT'),
            #('PIVOT', "Pivot", "Position of the transform manipulator", 'MANIPUL'),
            elif L_mode == 'CURSOR':
                t = (self.sv.space_data if self.sv else context.scene).cursor_location
                self._cached_t = t
            elif L_mode in ('MEAN', 'CENTER', 'MIN', 'MAX'):
                t = TransformAggregator.get_coord_summary(L_mode.lower())
                self._cached_t = t
            else: # GLOBAL, and fallback for some others
                t = Vector()
                self._cached_t = t
        
        R_mode = self.R[0]
        xyz = self._cached_xyz
        if not xyz:
            if R_mode == 'PARENT':
                if not pm: pm = get_parent_matrix(obj)
                xyz = pm.col[:3]
            elif R_mode == 'LOCAL':
                if not lm: lm = get_world_matrix(obj)
                xyz = lm.col[:3]
            elif R_mode == 'ACTIVE':
                if not am: am = self.calc_active_matrix(context)
                xyz = am.col[:3]
                self._cached_xyz = xyz
            elif R_mode == 'CAMERA':
                cm = self.calc_cam_matrix(context, self.R[1])[0]
                xyz = cm.col[:3]
                self._cached_xyz = xyz
            elif R_mode == 'VIEW':
                vm = self.vm
                xyz = vm.col[:3]
                self._cached_xyz = xyz
            elif R_mode == 'OBJECT':
                _obj = (context.scene.objects.get(self.R[1]) if self.R[1] else context.active_object)
                om = get_world_matrix(_obj, self.R[2])
                xyz = om.col[:3]
                self._cached_xyz = xyz
            #('SURFACE', "Surface", "Orientation aligned to the raycasted normal/tangents", 'EDIT'),
            #('NORMAL', "Normal", "Orientation aligned to the average of elements' normals or bones' Y-axes", 'SNAP_NORMAL'),
            #('GIMBAL', "Gimbal", "Orientation aligned to the Euler rotation axes", 'NDOF_DOM'),
            #('ORIENTATION', "Orientation", "Specified orientation", 'MANIPUL'),
            elif R_mode == 'NORMAL':
                nm = TransformAggregator.get_normal_summary("mean")
                xyz = nm.col[:3]
                self._cached_xyz = xyz
            else: # GLOBAL, and fallback for some others
                xyz = Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,1))
                self._cached_xyz = xyz
        
        S_mode = self.S[0]
        s = self._cached_s
        if not s:
            if S_mode == 'PARENT':
                if not pm: pm = get_parent_matrix(obj)
                s = pm.to_scale()
            elif S_mode == 'LOCAL':
                if not lm: lm = get_world_matrix(obj)
                s = lm.to_scale()
            elif S_mode == 'ACTIVE':
                if not am: am = self.calc_active_matrix(context)
                s = am.to_scale()
                self._cached_s = s
            elif S_mode == 'CAMERA':
                cm = self.calc_cam_matrix(context, self.S[1])[0]
                s = cm.to_scale()
                self._cached_s = s
            elif S_mode == 'VIEW':
                vm = self.vm
                s = vm.to_scale()
                self._cached_s = s
            elif S_mode == 'OBJECT':
                _obj = (context.scene.objects.get(self.S[1]) if self.S[1] else context.active_object)
                om = get_world_matrix(_obj, self.S[2])
                s = om.to_scale()
                self._cached_s = s
            #('RANGE', "Range", "Use bounding box dimensions as the scale of each axis", 'BBOX'),
            #('STDDEV', "Deviation", "Use standard deviation as the scale of the system", 'STICKY_UVS_DISABLE'),
            elif S_mode in ('RANGE', 'STDDEV'):
                s = TransformAggregator.get_coord_summary(S_mode.lower(), 1.0)
                self._cached_s = s
            else: # GLOBAL, and fallback for some others
                s = Vector((1,1,1))
                self._cached_s = s
        
        x = s.x * xyz[0].to_3d().normalized()
        y = s.y * xyz[1].to_3d().normalized()
        z = s.z * xyz[2].to_3d().normalized()
        final_matrix = matrix_compose(x, y, z, t) * self.extra_matrix
        res = (L_mode, R_mode, S_mode, final_matrix, persp)
        
        if self._cached_t and self._cached_xyz and self._cached_s:
            self._cached_all = res
        
        return res
    
    def get_LRS(self, context, obj, rotation_mode='QUATERNION', rotation4=False):
        L_mode, R_mode, S_mode, to_m, persp = self.calc_matrix(context, obj)
        in_m = matrix_inverted_safe(to_m) * get_world_matrix(obj)
        
        if L_mode == 'BASIS':
            L = Vector(obj.location)
        elif L_mode == 'LOCAL':
            L = Vector()
        else:
            L = in_m.translation
            if L_mode in ('CAMERA', 'VIEW'):
                inv_z = ((1.0 / abs(L.z)) if L.z != 0.0 else 1.0)
                L = Vector((L.x * persp.x, L.y * persp.y, -L.z)).lerp(
                    Vector((L.x * inv_z * persp.x, L.y * inv_z * persp.y, -L.z)), persp.z)
        
        if R_mode == 'BASIS':
            R = convert_obj_rotation(obj.rotation_mode, obj.rotation_quaternion,
                obj.rotation_axis_angle, obj.rotation_euler, rotation_mode, rotation4)
        elif R_mode == 'LOCAL':
            R = convert_obj_rotation('QUATERNION', Quaternion((1,0,0,0)),
                None, None, rotation_mode, rotation4)
        else:
            R = convert_obj_rotation('QUATERNION', in_m.to_quaternion(),
                None, None, rotation_mode, rotation4)
        
        if S_mode == 'BASIS':
            S = Vector(obj.scale)
        elif S_mode == 'LOCAL':
            S = Vector((1,1,1))
        else:
            S = in_m.to_scale()
        
        return (L, R, S)
    
    def set_LRS(self, context, obj, LRS, rotation_mode='QUATERNION'):
        L, R, S = LRS
        L_mode, R_mode, S_mode, to_m, persp = self.calc_matrix(context, obj)
        
        mL = (L is not None) and (L_mode != 'BASIS')
        mR = (R is not None) and (R_mode != 'BASIS')
        mS = (S is not None) and (S_mode != 'BASIS')
        
        if mL or mR or mS:
            in_m = matrix_inverted_safe(to_m) * get_world_matrix(obj)
            
            if not mL:
                in_L = in_m.to_translation()
            else:
                if L_mode in ('CAMERA', 'VIEW'):
                    L = Vector((L.x / persp.x, L.y / persp.y, -L.z)).lerp(
                        Vector((L.x * L.z / persp.x, L.y * L.z / persp.y, -L.z)), persp.z)
                in_L = Vector(L)
                L = None
            
            if not mR:
                in_R = in_m.to_quaternion()
                if not R: rotation_mode = obj.rotation_mode
            else:
                if rotation_mode == 'QUATERNION':
                    in_R = Quaternion(R)
                elif rotation_mode == 'AXIS_ANGLE':
                    in_R = Quaternion(R[1:], R[0])
                else:
                    if (len(R) == 4): R = R[1:]
                    in_R = Euler(R).to_quaternion()
                R = None
            
            if not mS:
                in_S = in_m.to_scale()
            else:
                in_S = Vector(S)
                S = None
            
            #print((in_L, in_R, in_S, mL, mR, mS))
            
            x, y, z = in_R.to_matrix().col
            in_m = matrix_compose(x*in_S.x, y*in_S.y, z*in_S.z, in_L)
            obj.matrix_world = to_m * in_m
            
            if (not mL) and (not L): L = Vector(obj.location)
            if (not mR) and (not R): R = convert_obj_rotation(obj.rotation_mode, obj.rotation_quaternion,
                obj.rotation_axis_angle, obj.rotation_euler, rotation_mode)
            if (not mS) and (not S): S = Vector(obj.scale)
        
        if L: obj.location = Vector(L)
        if R: apply_obj_rotation(obj, R, rotation_mode)
        if S: obj.scale = Vector(S)

#@addon.PropertyGroup
@addon.IDBlock(name="Coordsys", icon='MANIPUL', show_empty=False)
class CoordSystemPG:
    items_LRS = [
        ('BASIS', "Basis", "Raw position/rotation/scale", 'BLENDER'),
        ('GLOBAL', "Global", "Global (world) coordinate system", 'WORLD'),
        ('PARENT', "Parent", "Parent's coordinate system (coincides with Global if there is no parent)", 'GROUP_BONE'),
        ('LOCAL', "Local", "Local (individual) coordinate system", 'ROTATECOLLECTION'),
        ('ACTIVE', "Active", "Coordinate system of active object (coincides with Global if there is no active object)", 'ROTACTIVE'),
        ('OBJECT', "Object/bone", "Coordinate system of the specified object/bone", 'OBJECT_DATA'),
        ('CAMERA', "Camera", "Camera projection coordinate system", 'CAMERA_DATA'),
        ('VIEW', "View", "Viewport coordinate system", 'RESTRICT_VIEW_OFF'),
    ]
    items_L = items_LRS + [
        ('SURFACE', "Surface", "Raycasted position", 'EDIT'),
        ('CURSOR', "Cursor", "3D cursor position", 'CURSOR'),
        ('BOOKMARK', "Bookmark", "Bookmark position", 'BOOKMARKS'),
        ('MEAN', "Average", "Average of selected items' positions", 'ROTATECENTER'),
        ('CENTER', "Center", "Center of selected items' positions", 'ROTATE'),
        ('MIN', "Min", "Minimum of selected items' positions", 'FRAME_PREV'),
        ('MAX', "Max", "Maximum of selected items' positions", 'FRAME_NEXT'),
        ('PIVOT', "Pivot", "Position of the transform manipulator", 'MANIPUL'),
    ]
    items_R = items_LRS + [
        ('SURFACE', "Surface", "Orientation aligned to the raycasted normal/tangents", 'EDIT'),
        ('NORMAL', "Normal", "Orientation aligned to the average of elements' normals or bones' Y-axes", 'SNAP_NORMAL'),
        ('GIMBAL', "Gimbal", "Orientation aligned to the Euler rotation axes", 'NDOF_DOM'),
        ('ORIENTATION', "Orientation", "Specified orientation", 'MANIPUL'),
    ]
    items_S = items_LRS + [
        ('RANGE', "Range", "Use bounding box dimensions as the scale of each axis", 'BBOX'),
        ('STDDEV', "Deviation", "Use standard deviation as the scale of the system", 'STICKY_UVS_DISABLE'),
    ]
    
    icons_L = {item[0]:item[3] for item in items_L}
    icons_R = {item[0]:item[3] for item in items_R}
    icons_S = {item[0]:item[3] for item in items_S}
    
    icon_L = 'MAN_TRANS'
    icon_R = 'MAN_ROT'
    icon_S = 'MAN_SCALE'
    
    customizable_L = {'OBJECT', 'CAMERA', 'BOOKMARK'}
    customizable_R = {'OBJECT', 'CAMERA', 'ORIENTATION'}
    customizable_S = {'OBJECT', 'CAMERA'}
    
    def make_aspect(name, items):
        title = "{} type".format(name)
        @addon.PropertyGroup
        class CoordsystemAspect:
            mode = 'GLOBAL' | prop(title, title, items=items)
            obj_name = "" | prop() # object/orientation/bookmark name
            bone_name = "" | prop()
        CoordsystemAspect.__name__ += name
        return CoordsystemAspect | prop()
    
    aspect_L = make_aspect("Origin", items_L)
    aspect_R = make_aspect("Orientation", items_R)
    aspect_S = make_aspect("Scale", items_S)
    
    del make_aspect
    
    used_modes = property(lambda self: {self.aspect_L.mode, self.aspect_R.mode, self.aspect_S.mode})
    
    _view_dependent_modes = {'VIEW', 'CURSOR', 'PIVOT', 'ORIENTATION'}
    @property
    def is_view_dependent(self):
        return any(aspect.mode in self._view_dependent_modes
            for aspect in (self.aspect_L, self.aspect_R, self.aspect_S))
    
    def unique_key(self, view_key):
        if not self.is_view_dependent: view_key = None
        return (self.name, view_key)
    
    show_grid_xy = False | prop("Show grid XY plane", "Show grid XY")
    show_grid_xz = False | prop("Show grid XZ plane", "Show grid XZ")
    show_grid_yz = False | prop("Show grid YZ plane", "Show grid YZ")
    grid_size = 3.0 | prop("Grid size", "Grid size", min=0)
    
    extra_X = Vector((1, 0, 0)) | prop("X axis", "X axis")
    extra_Y = Vector((0, 1, 0)) | prop("Y axis", "Y axis")
    extra_Z = Vector((0, 0, 1)) | prop("Z axis", "Z axis")
    extra_T = Vector((0, 0, 0)) | prop("Translation", "Translation")
    
    @property
    def extra_matrix(self):
        return matrix_compose(self.extra_X, self.extra_Y, self.extra_Z, self.extra_T)
    
    def make_get_reset(axis_id):
        def get_reset(self):
            return BlRna.is_default(getattr(self, "extra_"+axis_id), self, "extra_"+axis_id)
        return get_reset
    def make_set_reset(axis_id):
        def set_reset(self, value):
            if value: setattr(self, "extra_"+axis_id, BlRna.get_default(self, "extra_"+axis_id))
        return set_reset
    reset_X = False | prop("Reset X", "Reset X", get=make_get_reset("X"), set=make_set_reset("X"))
    reset_Y = False | prop("Reset Y", "Reset Y", get=make_get_reset("Y"), set=make_set_reset("Y"))
    reset_Z = False | prop("Reset Z", "Reset Z", get=make_get_reset("Z"), set=make_set_reset("Z"))
    reset_T = False | prop("Reset T", "Reset T", get=make_get_reset("T"), set=make_set_reset("T"))
    
    def draw(self, layout):
        layout = NestedLayout(layout, addon.module_name+".coordsystem")
        
        with layout.column(True):
            self.draw_aspect(layout, "L")
            self.draw_aspect(layout, "R")
            self.draw_aspect(layout, "S")
        
        with layout.row(True):
            layout.prop(self, "show_grid_xy", text="", icon='AXIS_TOP', toggle=True)
            layout.prop(self, "show_grid_xz", text="", icon='AXIS_FRONT', toggle=True)
            layout.prop(self, "show_grid_yz", text="", icon='AXIS_SIDE', toggle=True)
            layout.prop(self, "grid_size")
        
        with layout.fold("Extra Matrix", folded=True): # folded by default
            with layout.column(True):
                self.draw_axis(layout, "X")
                self.draw_axis(layout, "Y")
                self.draw_axis(layout, "Z")
                self.draw_axis(layout, "T")
    
    def draw_axis(self, layout, axis_id):
        with layout.row(True):
            with layout.row(True)(scale_x=0.1, enabled=(not getattr(self, "reset_"+axis_id))):
                layout.prop(self, "reset_"+axis_id, text=axis_id, toggle=True)
            layout.prop(self, "extra_"+axis_id, text="")
    
    def draw_aspect(self, layout, aspect_id):
        aspect = getattr(self, "aspect_"+aspect_id)
        aspect_icon = getattr(self, "icon_"+aspect_id)
        aspect_icons = getattr(self, "icons_"+aspect_id)
        customizable = getattr(self, "customizable_"+aspect_id)
        
        with layout.row(True):
            is_customizable = (aspect.mode in customizable)
            
            op = layout.operator("view3d.coordsystem_pick_aspect", text="", icon=aspect_icon)
            op.aspect_id = aspect_id
            
            with layout.row(True)(enabled=is_customizable):
                if aspect.mode == 'OBJECT':
                    obj = bpy.data.objects.get(aspect.obj_name)
                    with layout.row(True)(alert=bool(aspect.obj_name and not obj)):
                        layout.prop(aspect, "obj_name", text="")
                    
                    if obj and (obj.type == 'ARMATURE'):
                        bone = (obj.data.edit_bones if (obj.mode == 'EDIT') else obj.data.bones).get(aspect.bone_name)
                        with layout.row(True)(alert=bool(aspect.bone_name and not bone)):
                            layout.prop(aspect, "bone_name", text="")
                else:
                    layout.prop(aspect, "obj_name", text="")
            
            with layout.row(True)(scale_x=0.16):
                layout.prop(aspect, "mode", text="", icon=aspect_icons[aspect.mode])

@addon.Operator(idname="view3d.coordsystem_pick_aspect", options={'INTERNAL', 'REGISTER'}, description=
"Click: Pick this aspect from active object")
def Operator_Coordsystem_Pick_Aspect(self, context, event, aspect_id=""):
    manager = get_coordsystem_manager(context)
    coordsys = manager.current
    if not coordsys: return {'CANCELLED'}
    
    aspect = getattr(coordsys, "aspect_"+aspect_id)
    if aspect.mode != 'OBJECT': return {'CANCELLED'}
    
    obj = context.active_object
    if obj:
        aspect.obj_name = obj.name
        if obj.type == 'ARMATURE':
            bone = (obj.data.edit_bones if (obj.mode == 'EDIT') else obj.data.bones).active
            aspect.bone_name = (bone.name if bone else "")
        else:
            aspect.bone_name = ""
    else:
        aspect.obj_name = ""
        aspect.bone_name = ""
    
    return {'FINISHED'}

@addon.Operator(idname="view3d.coordsystem_new", options={'INTERNAL', 'REGISTER'}, description="New coordsystem")
def Operator_Coordsystem_New(self, context, event):
    manager = get_coordsystem_manager(context)
    item = manager.coordsystems.new("Coordsys")
    manager.coordsystem.selector = item.name
    return {'FINISHED'}

@addon.Operator(idname="view3d.coordsystem_delete", options={'INTERNAL', 'REGISTER'}, description="Delete coordsystem")
def Operator_Coordsystem_Delete(self, context, event):
    manager = get_coordsystem_manager(context)
    manager.coordsystems.discard(manager.coordsystem.selector)
    if manager.coordsystems:
        manager.coordsystem.selector = manager.coordsystems[len(manager.coordsystems)-1].name
    return {'FINISHED'}

@addon.PropertyGroup
class CoordSystemManagerPG:
    defaults_initialized = False | prop()
    coordsystems = [CoordSystemPG] | prop() # IDBlocks
    coordsystem = CoordSystemPG | prop() # IDBlock selector
    current = property(lambda self: self.coordsystems.get(self.coordsystem.selector))
    
    def draw(self, layout):
        self.coordsystem.draw(layout)
        coordsys = self.current
        if coordsys: coordsys.draw(layout)
    
    def init_default_coordystems(self):
        if self.defaults_initialized: return
        
        for item in CoordSystemPG.items_LRS:
            if item[0] == 'OBJECT': continue
            coordsys = self.coordsystems.new(item[1])
            coordsys.aspect_L.mode = item[0]
            coordsys.aspect_R.mode = item[0]
            coordsys.aspect_S.mode = item[0]
        
        coordsys = self.coordsystems.new("Normal")
        coordsys.aspect_L.mode = 'MEAN'
        coordsys.aspect_R.mode = 'NORMAL'
        coordsys.aspect_S.mode = 'GLOBAL'
        
        coordsys = self.coordsystems.new("Manipulator")
        coordsys.aspect_L.mode = 'PIVOT'
        coordsys.aspect_R.mode = 'ORIENTATION'
        coordsys.aspect_S.mode = 'GLOBAL'
        
        self.coordsystem.selector = "Global"
        
        self.defaults_initialized = True
    
    @addon.load_post
    def load_post(): # We can't do this in register() because of the restricted context
        manager = get_coordsystem_manager(bpy.context)
        if not manager.coordsystem.is_bound:
            manager.coordsystem.bind(manager.coordsystems, new="view3d.coordsystem_new", delete="view3d.coordsystem_delete", reselect=True)
        manager.init_default_coordystems() # assignment to selector must be done AFTER the binding
    del load_post
    
    @addon.after_register
    def after_register(): # We can't do this in register() because of the restricted context
        manager = get_coordsystem_manager(bpy.context)
        if not manager.coordsystem.is_bound:
            manager.coordsystem.bind(manager.coordsystems, new="view3d.coordsystem_new", delete="view3d.coordsystem_delete", reselect=True)
        manager.init_default_coordystems() # assignment to selector must be done AFTER the binding
    del after_register

def get_coordsystem_manager(context=None):
    if context is None: context = bpy.context
    #return context.screen.coordsystem_manager
    return addon.internal.coordsystem_manager

# We need to store all coordsystems in one place, so each screen can't have an independent list of coordiante systems
#addon.type_extend("Screen", "coordsystem_manager", (CoordSystemManagerPG | prop()))
addon.Internal.coordsystem_manager = CoordSystemManagerPG | prop()

@LeftRightPanel(idname="VIEW3D_PT_coordsystem", space_type='VIEW_3D', category="Batch", label="Coordinate System")
class Panel_Coordsystem:
    def draw(self, context):
        layout = NestedLayout(self.layout)
        get_coordsystem_manager(context).draw(layout)

class TransformAggregator:
    def __init__(self, context, csm):
        self.csm = csm
        self.queries = set(("count", "same"))
        
        self.mode = context.mode
        self.is_pose = (self.mode == 'POSE')
        
        self.process_active = getattr(self, self.mode+"_process_active", self._dummy)
        self.process_selected = getattr(self, self.mode+"_process_selected", self._dummy)
        self.finish = getattr(self, self.mode+"_finish", self._dummy)
        
        self.store = getattr(self, self.mode+"_store", self._dummy)
        self.restore = getattr(self, self.mode+"_restore", self._dummy)
        self.lock = getattr(self, self.mode+"_lock", self._dummy)
        
        self.set_prop = getattr(self, self.mode+"_set_prop", self._set_prop)
        
        self.coord_summary = getattr(self, self.mode+"_coord_summary", self._coord_summary)
        self.normal_summary = getattr(self, self.mode+"_normal_summary", self._normal_summary)
    
    def _dummy(self, *args, **kwargs):
        pass
    
    def init(self):
        self.queries.discard("active")
        #self.queries.update(("min", "max", "center", "mean"))
        self.queries.update(("min", "max", "center", "range", "mean", "stddev"))
        #self.queries.update(("min", "max", "center", "range", "mean", "stddev", "median"))
        self.iter_count = None
        self.iter_index = None
        getattr(self, self.mode+"_init", self._dummy)()
    
    def modify_vector(self, vector, axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref):
        if uniformity == 'OFFSET':
            return vector + vector_delta
        elif uniformity == 'PROPORTIONAL':
            return Vector(vector_ref[i] + vector_scale[i] * (vector[i] - vector_ref[i])
                for i in range(len(vector_scale)))
        elif axis_index is None:
            return Vector(vector_new)
        else:
            vector = Vector(vector)
            vector[axis_index] = vector_new[axis_index]
            return vector
    
    def _set_prop(self, context, prop_name, value, avoid_errors=True):
        for obj, select_names in Selection():
            if (not avoid_errors) or hasattr(obj, prop_name):
                setattr(obj, prop_name, value)
    
    def _coord_summary(self, summary, dflt=0.0):
        return Vector((dflt,dflt,dflt))
    def _normal_summary(self, summary):
        return Matrix.Identity(3)
    
    # ===== OBJECT ===== #
    def OBJECT_store(self, context):
        self.stored = []
        for obj, select_names in Selection():
            obj_LRS = self.csm.get_LRS(context, obj, self.rotation_mode, True)
            
            params = dict(
                L = obj_LRS[0],
                R = obj_LRS[1],
                S = obj_LRS[2],
                M = Matrix(obj.matrix_world),
                location = Vector(obj.location),
                rotation_axis_angle = Vector(obj.rotation_axis_angle),
                rotation_euler = Vector(obj.rotation_euler),
                rotation_quaternion = Vector(obj.rotation_quaternion),
                scale = Vector(obj.scale),
                dimensions = (Vector(obj.dimensions) if not self.is_pose else None),
            )
            self.stored.append((obj, params))
    
    def OBJECT_restore(self, context, vector_name, axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref):
        for obj, params in self.stored:
            # Applying both matrix and loc/rot/scale is a necessary measure:
            # * world matrix does not seem to be immediately updated by the basis loc/rot/scale,
            #   so we need to memorize and restore its original value
            # * we need non-changed basis values to stay exactly as they were (e.g. eulers can be > 180)
            obj.matrix_world = params["M"]
            obj.location = params["location"]
            obj.rotation_axis_angle = params["rotation_axis_angle"]
            obj.rotation_euler = params["rotation_euler"]
            obj.rotation_quaternion = params["rotation_quaternion"]
            obj.scale = params["scale"]
            
            if vector_name == "location":
                L = self.modify_vector(params["L"], axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref)
                self.csm.set_LRS(context, obj, (L, None, None))
            elif vector_name == "rotation":
                R = self.modify_vector(params["R"], axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref)
                self.csm.set_LRS(context, obj, (None, R, None), self.rotation_mode)
            elif vector_name == "scale":
                S = self.modify_vector(params["S"], axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref)
                self.csm.set_LRS(context, obj, (None, None, S))
            elif (vector_name == "dimensions") and (not self.is_pose):
                # Important: use the copied data, not obj.dimensions directly (or there will be glitches)
                obj.dimensions = self.modify_vector(params["dimensions"], axis_index, uniformity, vector_new, vector_delta, vector_scale, vector_ref)
    
    def OBJECT_lock(self, context, vector_name, axis_index, value):
        for obj, select_names in Selection():
            if vector_name == "location":
                obj.lock_location[axis_index] = value
            elif vector_name == "rotation":
                if axis_index == -1: # not one of actual components
                    obj.lock_rotations_4d = value
                elif axis_index == 0:
                    obj.lock_rotation_w = value
                else:
                    obj.lock_rotation[axis_index-1] = value
            elif vector_name == "scale":
                obj.lock_scale[axis_index] = value
    
    def OBJECT_init(self):
        lock_queries = {"count", "same", "mean"}
        rotation_mode_queries = {"count", "same", "modes"}
        
        self.default_LRS = (Vector(), Quaternion((1,0,0,0)), Vector((1,1,1)))
        
        self.location = Vector()
        self.rotation = Vector.Fill(4)
        self.scale = Vector((1,1,1))
        self.dimensions = Vector()
        self.normal_matrix = Matrix.Identity(3)
        
        self.aggr_location = VectorAggregator(3, 'NUMBER', self.queries)
        self.aggr_location_lock = VectorAggregator(3, 'BOOL', lock_queries)
        
        self.aggr_rotation = VectorAggregator(4, 'NUMBER', self.queries)
        self.aggr_rotation_lock = VectorAggregator(4, 'BOOL', lock_queries)
        self.aggr_rotation_lock_4d = Aggregator('BOOL', lock_queries)
        self.aggr_rotation_mode = Aggregator('STRING', rotation_mode_queries)
        
        self.aggr_scale = VectorAggregator(3, 'NUMBER', self.queries)
        self.aggr_scale_lock = VectorAggregator(3, 'BOOL', lock_queries)
        
        self.aggr_dimensions = VectorAggregator(3, 'NUMBER', self.queries)
    
    def OBJECT_process_active(self, context, obj):
        obj_LRS = (self.csm.get_LRS(context, obj, self.last_rotation_mode, True) if obj else self.default_LRS)
        
        self.location = obj_LRS[0]
        self.rotation = obj_LRS[1]
        self.scale = obj_LRS[2]
        self.dimensions = (Vector(obj.dimensions) if obj and (not self.is_pose) else Vector())
        self.normal_matrix = obj.matrix_world.to_3x3()
    
    def OBJECT_process_selected(self, context, obj):
        obj_LRS = self.csm.get_LRS(context, obj, self.last_rotation_mode, True)
        
        self.aggr_location.add(obj_LRS[0])
        self.aggr_location_lock.add(obj.lock_location)
        
        self.aggr_rotation.add(obj_LRS[1])
        self.aggr_rotation_lock.add((obj.lock_rotation_w,
            obj.lock_rotation[0], obj.lock_rotation[1], obj.lock_rotation[2]))
        self.aggr_rotation_lock_4d.add(obj.lock_rotations_4d)
        self.aggr_rotation_mode.add(obj.rotation_mode)
        
        self.aggr_scale.add(obj_LRS[2])
        self.aggr_scale_lock.add(obj.lock_scale)
        
        if not self.is_pose: self.aggr_dimensions.add(obj.dimensions)
    
    last_rotation_mode = 'XYZ'
    def OBJECT_finish(self):
        cls = self.__class__
        if self.aggr_rotation_mode.modes:
            cls.last_rotation_mode = self.aggr_rotation_mode.modes[0]
        self.rotation_mode = self.last_rotation_mode # make sure we have a local copy
    
    def OBJECT_coord_summary(self, summary, dflt=0.0):
        if self.aggr_location.count == 0: return Vector((dflt,dflt,dflt))
        return Vector(getattr(self.aggr_location, summary))
    def OBJECT_normal_summary(self, summary):
        return self.normal_matrix
    # ====================================================================== #
    
    # Currently, POSE aggregate attributes are exactly the same as OBJECT's,
    # except for the dimensions, and child-bones' Location displayed as inactive.
    POSE_store = OBJECT_store
    POSE_restore = OBJECT_restore
    POSE_lock = OBJECT_lock
    POSE_init = OBJECT_init
    POSE_process_active = OBJECT_process_active
    POSE_process_selected = OBJECT_process_selected
    POSE_finish = OBJECT_finish
    # ====================================================================== #
    
    tfm_aggr_map = {}
    tfm_aggrs = []
    _global_aggr = None
    
    @classmethod
    def get_coord_summary(cls, summary, dflt=0.0):
        tfm_aggr = cls._global_aggr
        if not tfm_aggr: return Vector((dflt,dflt,dflt))
        return tfm_aggr.coord_summary(summary, dflt)
    @classmethod
    def get_normal_summary(cls, summary):
        tfm_aggr = cls._global_aggr
        if not tfm_aggr: return Matrix.Identity(3)
        return tfm_aggr.normal_summary(summary)
    
    @classmethod
    def iter_transforms(cls, category, coordsystem_manager):
        coordsys_name_default = coordsystem_manager.coordsystem.selector
        coordsystems = coordsystem_manager.coordsystems
        for transform in category.transforms:
            if not transform.is_v3d: continue
            coordsys_name = (transform.coordsystem_selector.selector
                if transform.use_pinned_coordsystem else coordsys_name_default)
            coordsys = coordsystems.get(coordsys_name)
            if coordsys: yield transform, coordsys
    
    @classmethod
    def job(cls, event, item):
        context = bpy.context
        if event == 1: # SELECTED
            for tfm_aggr in cls.tfm_aggrs:
                tfm_aggr.process_selected(context, item)
        elif event == 0: # ACTIVE
            for tfm_aggr in cls.tfm_aggrs:
                tfm_aggr.process_active(context, item)
        else: # RESET or FINISHED
            coordsystem_manager = get_coordsystem_manager(context)
            
            category = get_category()
            category.transforms_ensure_order(context.screen)
            
            if event == -1: # FINISHED
                for transform, coordsys in cls.iter_transforms(category, coordsystem_manager):
                    transformExt = addon[transform]
                    coordsys_key = coordsys.unique_key(transformExt)
                    tfm_aggr = cls.tfm_aggr_map.get(coordsys_key)
                    if tfm_aggr: # coordsystem might have changed in the meantime
                        tfm_aggr.finish()
                        # Don't interfere while user is changing some value
                        if not UIMonitor.user_interaction: transform.apply(tfm_aggr)
                cls._global_aggr = cls.tfm_aggr_map.get(("", None))
            else: # RESET
                cls.tfm_aggr_map = {}
                
                csm = CoordSystemMatrix(None)
                tfm_aggr = TransformAggregator(context, csm)
                cls.tfm_aggr_map[("", None)] = tfm_aggr
                
                for transform, coordsys in cls.iter_transforms(category, coordsystem_manager):
                    transformExt = addon[transform]
                    coordsys_key = coordsys.unique_key(transformExt)
                    tfm_aggr = cls.tfm_aggr_map.get(coordsys_key)
                    if tfm_aggr is None:
                        sv = None
                        if coordsys_key[1]:
                            sv = SmartView3D(use_camera_axes=True, **transform.ui_context)
                        csm = CoordSystemMatrix(coordsys, sv)
                        tfm_aggr = TransformAggregator(context, csm)
                        cls.tfm_aggr_map[coordsys_key] = tfm_aggr
                    tfm_aggr.queries.update(transform.summaries)
                
                cls.tfm_aggrs = list(cls.tfm_aggr_map.values())
                for tfm_aggr in cls.tfm_aggrs:
                    tfm_aggr.init()

addon.selection_job(TransformAggregator.job)

# Make sure UI Monitor is active (it is inactive if there are no callbacks)
@addon.ui_monitor
def ui_monitor(context, event, UIMonitor):
    if 'MOUSEMOVE' in event.type:
        if (context.area == 'VIEW_3D') and (context.region.type == 'WINDOW'):
            category = get_category()
            transform = category.find_transform(context.screen, context.area)
            if transform:
                transformExt = addon[transform]
                transformExt.window = context.window
                transformExt.screen = context.screen
                transformExt.space_data = context.space_data
                transformExt.region = context.region
                transformExt.region_data = context.region_data

def SummaryValuePG(default, representations, **kwargs):
    tooltip = "Click: independent, Shift+Click: offset, Alt+Click: proportional, Ctrl+Click or Shift+Alt+Click: equal"
    kwargs = dict(kwargs, description=(kwargs.get("description", "")+tooltip))
    if "update" not in kwargs: kwargs["update"] = True
    
    @addon.PropertyGroup
    class cls:
        value = default | -prop(**kwargs)
        
        def draw(self, layout, prop_name="value"):
            layout.prop(self, prop_name)
    
    def dummy_get(self):
        return default
    def dummy_set(self, value):
        pass
    cls.dummy = default | -prop(get=dummy_get, set=dummy_set, **dict(kwargs, name="--"))
    
    def _get(self):
        return self.value
    
    def _set(self, value):
        id_data = self.id_data
        path_parts = self.path_from_id().split(".")
        tfm_mode = id_data.path_resolve(".".join(path_parts[:-2]))
        
        if not UIMonitor.user_interaction:
            UIMonitor.user_interaction = True
            
            axis_name = path_parts[-1]
            axis_parts = axis_name.split("[")
            axis_name = axis_parts[0]
            summary_index = int(axis_parts[1].strip("[]"))
            
            vector_name = path_parts[-2]
            
            transform = id_data.path_resolve(".".join(path_parts[:-3]))
            
            # Ctrl+clicking on a numeric value makes it go into a "text editing mode"
            # no mater where the user clicked or if the property was dragged.
            if UIMonitor.ctrl or (UIMonitor.shift and UIMonitor.alt):
                uniformity = 'EQUAL'
            elif UIMonitor.shift:
                uniformity = 'OFFSET'
            elif UIMonitor.alt:
                uniformity = 'PROPORTIONAL'
            else:
                uniformity = 'INDEPENDENT'
            
            tfm_mode.begin(transform, vector_name, axis_name, summary_index, uniformity)
        
        tfm_mode.modify(value)
    
    for representation in representations:
        subtype = representation.get("subtype", 'NONE')
        setattr(cls, subtype.lower(), default | -prop(get=_get, set=_set, **dict(kwargs, **representation)))
    
    return cls

def LockPG(default_uniformity=False):
    @addon.PropertyGroup
    class cls:
        lock_uniformity = default_uniformity | -prop(update=True)
        lock_transformation = False | -prop(update=True)
        
        def _get(self):
            return self.lock_uniformity
        def _set(self, value):
            if UIMonitor.ctrl:
                id_data = self.id_data
                path_parts = self.path_from_id().split(".")
                tfm_mode = id_data.path_resolve(".".join(path_parts[:-2]))
                axis_name = path_parts[-1].split("_")[0]
                vector_name = path_parts[-2]
                tfm_mode.modify_lock(vector_name, axis_name, not self.lock_transformation)
            else:
                self.lock_uniformity = value
        value = False | -prop(get=_get, set=_set, description="Click: lock uniformity, Ctrl+Click: lock transformation")
    
    return cls

@addon.PropertyGroup
class Lock4dPG:
    lock_4d = False | -prop(update=True)
    
    def _get(self):
        return self.lock_4d
    def _set(self, value):
        id_data = self.id_data
        path_parts = self.path_from_id().split(".")
        tfm_mode = id_data.path_resolve(".".join(path_parts[:-2]))
        axis_name = path_parts[-1].split("_")[0]
        vector_name = path_parts[-2]
        tfm_mode.modify_lock(vector_name, axis_name, value)
    value = False | -prop(get=_get, set=_set, description="Click: enable/disable locking 4-component rotations as eulers")

@addon.PropertyGroup
class RotationModePG:
    items = [
        ('QUATERNION', "Quaternion (WXYZ)", "No Gimbal Lock"),
        ('XYZ', "XYZ Euler", "XYZ Rotation Order - prone to Gimbal Lock"),
        ('XZY', "XZY Euler", "XZY Rotation Order - prone to Gimbal Lock"),
        ('YXZ', "YXZ Euler", "YXZ Rotation Order - prone to Gimbal Lock"),
        ('YZX', "YZX Euler", "YZX Rotation Order - prone to Gimbal Lock"),
        ('ZXY', "ZXY Euler", "ZXY Rotation Order - prone to Gimbal Lock"),
        ('ZYX', "ZYX Euler", "ZYX Rotation Order - prone to Gimbal Lock"),
        ('AXIS_ANGLE', "Axis Angle", "Axis Angle (W+XYZ), defines a rotation around some axis defined by 3D-Vector"),
    ]
    mode = 'XYZ' | -prop(items=items, update=True)
    
    # Note: the Enum get/set methods must return ints instead of strings/sets
    def _get(self):
        for i, item in enumerate(self.items):
            if item[0] == self.mode: return i+1
    def _set(self, value):
        value = self.items[value-1][0]
        id_data = self.id_data
        path_parts = self.path_from_id().split(".")
        tfm_mode = id_data.path_resolve(".".join(path_parts[:-2]))
        tfm_mode.modify_prop("rotation_mode", value)
    value = 'XYZ' | -prop(items=items, get=_get, set=_set, description="Rotation mode")

def SummaryVectorPG(title, axes, is_rotation=False, folded=False):
    @addon.PropertyGroup
    class cls:
        def get_vector(self, si):
            return tuple(getattr(self, axis_name)[si].value for axis_name in self.axis_names)
        def set_vector(self, si, value):
            for i, axis_name in enumerate(self.axis_names):
                #getattr(self, axis_name)[si].value = value[i]
                setattr_cmp(getattr(self, axis_name)[si], "value", value[i], 1e-6)
        
        def _get_lock_uniformity(self):
            return tuple(getattr(self, axis_name+"_lock").lock_uniformity for axis_name in self.axis_names)
        def _set_lock_uniformity(self, value):
            for i, axis_name in enumerate(self.axis_names):
                #getattr(self, axis_name+"_lock").lock_uniformity = value[i]
                setattr_cmp(getattr(self, axis_name+"_lock"), "lock_uniformity", value[i])
        lock_uniformity = property(_get_lock_uniformity, _set_lock_uniformity)
        
        def _get_lock_transformation(self):
            return tuple(getattr(self, axis_name+"_lock").lock_transformation for axis_name in self.axis_names)
        def _set_lock_transformation(self, value):
            for i, axis_name in enumerate(self.axis_names):
                #getattr(self, axis_name+"_lock").lock_transformation = value[i]
                setattr_cmp(getattr(self, axis_name+"_lock"), "lock_transformation", value[i])
        lock_transformation = property(_get_lock_transformation, _set_lock_transformation)
        
        def match_summaries(self, summaries, axis=None):
            if axis is None:
                for axis_name in self.axis_names:
                    self.match_summaries(summaries, getattr(self, axis_name))
            elif len(axis) != len(summaries):
                axis.clear()
                for i in range(len(summaries)):
                    axis.add()
        
        def draw_axis(self, layout, summaries, axis_i, axis_id, prop_name="value", lock_enabled=True):
            axis = getattr(self, axis_id)
            axis_lock = getattr(self, axis_id+"_lock")
            
            self.match_summaries(summaries, axis)
            
            vector_same = self.get("vector:same")
            axis_same = (True if vector_same is None else vector_same[axis_i])
            lock_same = self.get("lock:same")
            lock_same = (True if lock_same is None else lock_same[axis_i])
            
            with layout.row(True):
                with layout.row(True)(alert=not axis_same, enabled=(prop_name != "dummy")):
                    for axis_item in axis:
                        axis_item.draw(layout, prop_name)
                
                with layout.row(True)(alert=not lock_same, active=lock_enabled):
                    icon = ('LOCKED' if axis_lock.lock_transformation else 'UNLOCKED')
                    layout.prop(axis_lock, "value", text="", icon=icon, toggle=True)
    
    axis_names = []
    axis_subtypes = []
    for axis in axes:
        name, default, default_uniformity, representations, kwargs = axis
        kwargs = dict({"name":name}, **kwargs)
        
        setattr(cls, name, [SummaryValuePG(default, representations, **kwargs)] | -prop())
        setattr(cls, name+"_lock", LockPG(default_uniformity) | -prop())
        
        axis_names.append(name)
        axis_subtypes.append(tuple(r["subtype"].lower() for r in representations))
    
    cls.axis_names = tuple(axis_names)
    cls.axis_subtypes = tuple(axis_subtypes)
    
    if is_rotation:
        cls.w4d_lock = Lock4dPG | -prop()
        cls.mode = RotationModePG | -prop()
    
    def draw(self, layout, summaries):
        with layout.row():
            with layout.fold(title, "row", folded):
                is_folded = layout.folded
        
        if (not is_folded) and summaries:
            with layout.column(True):
                if not is_rotation:
                    for i in range(len(self.axis_names)):
                        self.draw_axis(layout, summaries, i, self.axis_names[i], self.axis_subtypes[i][0])
                else:
                    rotation_mode = self.mode.mode
                    is_euler = (rotation_mode not in ('QUATERNION', 'AXIS_ANGLE'))
                    w4d_lock_same = self.get("w4d_lock:same", True)
                    mode_same = self.get("mode:same", True)
                    
                    if is_euler:
                        self.draw_axis(layout, summaries, 0, "w", "dummy", self.w4d_lock.lock_4d)
                        self.draw_axis(layout, summaries, 1, "x", "angle")
                        self.draw_axis(layout, summaries, 2, "y", "angle")
                        self.draw_axis(layout, summaries, 3, "z", "angle")
                    else:
                        if rotation_mode == 'QUATERNION':
                            self.draw_axis(layout, summaries, 0, "w", "none", self.w4d_lock.lock_4d)
                        else:
                            self.draw_axis(layout, summaries, 0, "w", "angle", self.w4d_lock.lock_4d)
                        self.draw_axis(layout, summaries, 1, "x", "none")
                        self.draw_axis(layout, summaries, 2, "y", "none")
                        self.draw_axis(layout, summaries, 3, "z", "none")
                    
                    with layout.row(True):
                        with layout.row(True)(alert=not mode_same):
                            layout.prop(self.mode, "value", text="")
                        with layout.row(True)(alert=not w4d_lock_same, active=(not is_euler), scale_x=0.1):
                            layout.prop(self.w4d_lock, "value", text="4L", toggle=True)
    
    cls.draw = draw
    
    return cls

def safe_vector(v, fallback):
    return tuple((fallback if vc is None else vc) for vc in v)

class BaseTransformPG:
    vector_names = tuple()
    
    def begin(self, transform, vector_name, axis_name, summary_index, uniformity):
        selfx = addon[self]
        tfm_aggr = getattr(selfx, "tfm_aggr", None)
        if tfm_aggr is None: return # no aggr yet, can't do anything
        
        context = bpy.context
        
        tfm_aggr.store(context)
        
        vector_aggr = getattr(tfm_aggr, "aggr_"+vector_name)
        
        summary = selfx.summaries[summary_index]
        summary_vector = selfx.summary_vectors[summary_index][vector_name]
        vector_prop = getattr(self, vector_name)
        axis_index = vector_prop.axis_names.index(axis_name)
        locks = tuple(getattr(vector_prop, axis_name+"_lock").lock_uniformity
            for axis_name in vector_prop.axis_names)
        
        if summary == "active":
            object_uniformity = transform.uniformity
            reference_vector = Vector.Fill(len(summary_vector))
        elif summary == "min":
            object_uniformity = 'PROPORTIONAL'
            reference_vector = Vector(safe_vector(vector_aggr.max, 0.0))
        elif summary == "max":
            object_uniformity = 'PROPORTIONAL'
            reference_vector = Vector(safe_vector(vector_aggr.min, 0.0))
        elif summary == "center":
            object_uniformity = 'OFFSET'
            reference_vector = Vector.Fill(len(summary_vector))
        elif summary == "range":
            object_uniformity = 'PROPORTIONAL'
            reference_vector = Vector(safe_vector(vector_aggr.center, 0.0))
        elif summary == "mean":
            object_uniformity = 'OFFSET'
            reference_vector = Vector.Fill(len(summary_vector))
        elif summary == "stddev":
            object_uniformity = 'PROPORTIONAL'
            reference_vector = Vector(safe_vector(vector_aggr.mean, 0.0))
        elif summary == "median":
            object_uniformity = 'OFFSET'
            reference_vector = Vector.Fill(len(summary_vector))
        
        selfx.vector_name = vector_name
        selfx.axis_name = axis_name
        selfx.axis_index = axis_index
        selfx.summary_index = summary_index
        selfx.summary = summary
        selfx.summary_vector = summary_vector
        selfx.vector_prop = vector_prop
        selfx.locks = locks
        selfx.vector_uniformity = uniformity
        selfx.object_uniformity = object_uniformity
        selfx.reference_vector = reference_vector
        
        #print((summary, uniformity, object_uniformity, locks, reference_vector))
        
        bpy.ops.ed.undo_push(message="Batch {}.{}".format(vector_name, axis_name))
    
    def modify(self, value):
        selfx = addon[self]
        tfm_aggr = getattr(selfx, "tfm_aggr", None)
        if tfm_aggr is None: return # no aggr yet, can't do anything
        
        context = bpy.context
        
        vector_old = selfx.summary_vector
        vector_ref = selfx.reference_vector
        
        axis_index = selfx.axis_index
        axis_old = vector_old[axis_index]
        axis_ref = vector_ref[axis_index]
        axis_new = value
        axis_delta = axis_new - axis_old
        axis_old_ref = axis_old - axis_ref
        axis_new_ref = axis_new - axis_ref
        axis_scale = (axis_new_ref / axis_old_ref if axis_old_ref != 0.0 else 0.0)
        
        #print("{} / {} = {}".format(axis_new_ref, axis_old_ref, axis_scale))
        
        locks = selfx.locks
        vector_uniformity = ('INDEPENDENT' if locks[axis_index] else selfx.vector_uniformity)
        
        vector_new = Vector(vector_old)
        if vector_uniformity == 'EQUAL':
            for i in range(len(vector_new)):
                if (not locks[i]) or (i == axis_index):
                    vector_new[i] = axis_new
        elif vector_uniformity == 'OFFSET':
            for i in range(len(vector_new)):
                if (not locks[i]) or (i == axis_index):
                    vector_new[i] += axis_delta
        elif vector_uniformity == 'PROPORTIONAL':
            for i in range(len(vector_new)):
                if (not locks[i]) or (i == axis_index):
                    vector_new[i] = vector_ref[i] + axis_scale * (vector_new[i] - vector_ref[i])
        else:
            vector_new[axis_index] = axis_new
        
        vector_delta = vector_new - vector_old
        vector_old_ref = vector_old - vector_ref
        vector_new_ref = vector_new - vector_ref
        vector_scale = Vector((vector_new_ref[i] / vector_old_ref[i] if vector_old_ref[i] != 0.0 else 0.0)
            for i in range(len(vector_new_ref)))
        
        #print(vector_new)
        #print((axis_old, axis_new, axis_delta, axis_scale))
        
        getattr(self, selfx.vector_name).set_vector(selfx.summary_index, vector_new)
        
        if vector_uniformity != 'INDEPENDENT': axis_index = None
        tfm_aggr.restore(context, selfx.vector_name, axis_index, selfx.object_uniformity, vector_new, vector_delta, vector_scale, vector_ref)
    
    def modify_lock(self, vector_name, axis_name, value):
        selfx = addon[self]
        tfm_aggr = getattr(selfx, "tfm_aggr", None)
        if tfm_aggr is None: return # no aggr yet, can't do anything
        
        context = bpy.context
        
        vector_prop = getattr(self, vector_name)
        try:
            axis_index = vector_prop.axis_names.index(axis_name)
        except ValueError:
            axis_index = -1
        
        bpy.ops.ed.undo_push(message="Batch {}.{} (un)lock".format(vector_name, axis_name))
        
        tfm_aggr.lock(context, vector_name, axis_index, value)
    
    def modify_prop(self, prop_name, value, avoid_errors=True):
        selfx = addon[self]
        tfm_aggr = getattr(selfx, "tfm_aggr", None)
        if tfm_aggr is None: return # no aggr yet, can't do anything
        
        context = bpy.context
        
        bpy.ops.ed.undo_push(message="Batch set {}".format(prop_name))
        
        tfm_aggr.set_prop(context, prop_name, value, avoid_errors)
    
    def apply(self, tfm_aggr, summaries):
        selfx = addon[self]
        selfx.tfm_aggr = tfm_aggr
        selfx.summaries = summaries
        selfx.summary_vectors = []
        
        for vector_name in self.vector_names:
            getattr(self, vector_name).match_summaries(summaries)
        
        for i, summary in enumerate(summaries):
            vectors = {}
            for vector_name in self.vector_names:
                if summary == 'active':
                    vector = getattr(tfm_aggr, vector_name)
                else:
                    vector_aggr = getattr(tfm_aggr, "aggr_"+vector_name)
                    vector = safe_vector(getattr(vector_aggr, summary), 0.0)
                
                getattr(self, vector_name).set_vector(i, vector)
                vectors[vector_name] = Vector(vector) # make sure it's a Vector
            
            selfx.summary_vectors.append(vectors)
        
        for vector_name in self.vector_names:
            aggr_name = "aggr_"+vector_name
            vector_prop = getattr(self, vector_name)
            vector_prop["vector:same"] = getattr(tfm_aggr, aggr_name).same
            
            aggr_lock_name = aggr_name+"_lock"
            if hasattr(tfm_aggr, aggr_lock_name):
                lock_aggr = getattr(tfm_aggr, aggr_lock_name)
                vector_prop.lock_transformation = safe_vector(lock_aggr.mean, False)
                vector_prop["lock:same"] = lock_aggr.same
        
        self.apply_special_cases(tfm_aggr)
    
    def apply_special_cases(self, tfm_aggr):
        pass
    
    def draw(self, layout, summaries):
        for vector_name in self.vector_names:
            getattr(self, vector_name).draw(layout, summaries)
        self.draw_special_cases(layout)
    
    def draw_special_cases(self, layout):
        pass

# Note: bpy properties only work when declared in the actually registered class, so I have to use mixins.
class BaseLRSTransformPG(BaseTransformPG):
    vector_names = ("location", "rotation", "scale")
    
    location = SummaryVectorPG("Location", [
        ("x", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=5)),
        ("y", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=5)),
        ("z", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=5)),
    ]) | prop()
    rotation = SummaryVectorPG("Rotation", [
        ("w", 0.0, True, [dict(subtype='NONE'), dict(name="\u03B1", subtype='ANGLE', unit='ROTATION')], dict(precision=3)),
        ("x", 0.0, False, [dict(subtype='NONE'), dict(subtype='ANGLE', unit='ROTATION')], dict(precision=3)),
        ("y", 0.0, False, [dict(subtype='NONE'), dict(subtype='ANGLE', unit='ROTATION')], dict(precision=3)),
        ("z", 0.0, False, [dict(subtype='NONE'), dict(subtype='ANGLE', unit='ROTATION')], dict(precision=3)),
    ], True) | prop()
    scale = SummaryVectorPG("Scale", [
        ("x", 0.0, False, [dict(subtype='NONE')], dict(precision=3)),
        ("y", 0.0, False, [dict(subtype='NONE')], dict(precision=3)),
        ("z", 0.0, False, [dict(subtype='NONE')], dict(precision=3)),
    ]) | prop()
    
    def apply_special_cases(self, tfm_aggr):
        #self.rotation.w4d_lock.lock_4d = round_to_bool(tfm_aggr.aggr_rotation_lock_4d.mean)
        setattr_cmp(self.rotation.w4d_lock, "lock_4d", round_to_bool(tfm_aggr.aggr_rotation_lock_4d.mean))
        self.rotation["w4d_lock:same"] = tfm_aggr.aggr_rotation_lock_4d.same
        
        if tfm_aggr.aggr_rotation_mode.modes:
            #self.rotation.mode.mode = tfm_aggr.aggr_rotation_mode.modes[0]
            setattr_cmp(self.rotation.mode, "mode", tfm_aggr.aggr_rotation_mode.modes[0])
        else:
            #self.rotation.mode.mode = 'XYZ'
            setattr_cmp(self.rotation.mode, "mode", 'XYZ')
        self.rotation["mode:same"] = tfm_aggr.aggr_rotation_mode.same

class BaseLRSDTransformPG(BaseLRSTransformPG):
    vector_names = ("location", "rotation", "scale", "dimensions")
    dimensions = SummaryVectorPG("Dimensions", [
        ("x", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=3, min=0)),
        ("y", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=3, min=0)),
        ("z", 0.0, False, [dict(subtype='DISTANCE', unit='LENGTH')], dict(precision=3, min=0)),
    ]) | prop()

@addon.PropertyGroup(mixins=BaseLRSDTransformPG)
class ObjectTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class MeshTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class CurveTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class MetaTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class LatticeTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseLRSTransformPG)
class PoseTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class BoneTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class GreaseTransformPG:
    pass

@addon.PropertyGroup(mixins=BaseTransformPG)
class CursorTransformPG:
    pass

@addon.Operator(idname="object.batch_{}_summary".format(category_name), options={'INTERNAL'}, description=
"Click: Summary menu")
def Operator_Summary(self, context, event, index=0, summary="", title=""):
    category = get_category()
    options = get_options()
    
    def draw_popup_menu(self, context):
        layout = NestedLayout(self.layout)
        
        transform = category.transforms[index]
        
        layout.operator("object.batch_{}_summary_copy".format(category_name), text="Copy", icon='COPYDOWN')
        layout.operator("object.batch_{}_summary_paste".format(category_name), text="Paste", icon='PASTEDOWN')
        layout.operator("object.batch_{}_summary_paste".format(category_name), text="+ Paste", icon='PASTEDOWN')
        layout.operator("object.batch_{}_summary_paste".format(category_name), text=" \u2013 Paste", icon='PASTEDOWN')
        layout.operator("object.batch_{}_summary_paste".format(category_name), text=" * Paste", icon='PASTEDOWN')
        layout.operator("object.batch_{}_summary_paste".format(category_name), text="\u00F7 Paste", icon='PASTEDOWN')
        
        #if summary == "active":
        #    layout.prop_menu_enum(transform, "uniformity")
    
    context.window_manager.popup_menu(draw_popup_menu, title="{}".format(title))

@addon.Operator(idname="object.batch_{}_summary_copy".format(category_name), options={'INTERNAL'}, description=
"Click: Copy")
def Operator_Summary_Copy(self, context, event):
    category = get_category()
    options = get_options()

@addon.Operator(idname="object.batch_{}_summary_paste".format(category_name), options={'INTERNAL'}, description=
"Click: Paste")
def Operator_Summary_Paste(self, context, event):
    category = get_category()
    options = get_options()

@addon.Operator(idname="object.batch_{}_property".format(category_name), options={'INTERNAL'}, description=
"Click: Property menu")
def Operator_Property(self, context, event, property_name=""):
    category = get_category()
    options = get_options()

# Should probably be stored in each Screen?
@addon.PropertyGroup
class ContextTransformPG:
    # Currently Blender doesn't support user-defined properties
    # for SpaceView3D -> we have to maintain a separate mapping.
    is_v3d = False | prop()
    index = 0 | prop()
    
    @property
    def ui_context(self):
        selfx = addon[self]
        
        area = getattr(selfx, "area", None)
        if (not area) or (not area.regions): return {}
        
        space_data = area.spaces.active
        if space_data.type != 'VIEW_3D': return {}
        
        region = getattr(selfx, "region", None)
        if not region:
            for _region in area.regions:
                if _region.type == 'WINDOW': region = _region
        region_data = getattr(selfx, "region_data", None) or rv3d_from_region(area, region)
        
        window = getattr(selfx, "window", None) or bpy.context.window
        screen = getattr(selfx, "screen", None) or bpy.context.screen
        
        return dict(window=window, screen=screen,
            area=area, space_data=space_data,
            region=region, region_data=region_data)
    
    # Summaries are stored here because they might be different for each 3D view
    summary_items = [
        ('active', "Active", "", 'ROTACTIVE'),
        ('min', "Min", "", 'MOVE_DOWN_VEC'),
        ('max', "Max", "", 'MOVE_UP_VEC'),
        ('center', "Center", "", 'ROTATE'),
        ('range', "Range", "", 'STICKY_UVS_VERT'),
        ('mean', "Mean", "", 'ROTATECENTER'),
        ('stddev', "StdDev", "", 'SMOOTHCURVE'),
        ('median', "Median", "", 'SORTSIZE'),
        #('mode', "Mode", "", 'GROUP_VERTEX'),
    ]
    summaries = {'active'} | prop("Summaries", items=summary_items)
    
    # This affects only the "active" summary, since all others
    # are mostly applicable only in one way
    uniformity_items = [
        ('EQUAL', "Equal", "", 'COLLAPSEMENU'), # COLLAPSEMENU LINKED
        ('OFFSET', "Offset", "", 'ZOOMIN'), # PLUS
        ('PROPORTIONAL', "Proportional", "", 'FULLSCREEN_ENTER'), # X CURVE_PATH
    ]
    uniformity_icons = {item[0]:item[3] for item in uniformity_items}
    uniformity = 'OFFSET' | prop("Batch modification", items=uniformity_items)
    
    use_pinned_coordsystem = False | prop()
    coordsystem_selector = CoordSystemPG | prop() # IDBlock selector
    
    @property
    def coordsystem(self):
        manager = get_coordsystem_manager(bpy.context)
        return manager.coordsystems.get(self.coordsystem_selector.selector)
    
    def draw_coordsystem_selector(self, layout):
        manager = get_coordsystem_manager(bpy.context)
        if not self.coordsystem_selector.is_bound:
            self.coordsystem_selector.bind(manager.coordsystems, rename=False)
        
        with layout.row(True):
            icon = ('PINNED' if self.use_pinned_coordsystem else 'UNPINNED')
            layout.prop(self, "use_pinned_coordsystem", text="", icon=icon, toggle=True)
            if self.use_pinned_coordsystem:
                self.coordsystem_selector.draw(layout)
            else:
                setattr_cmp(self.coordsystem_selector, "selector", manager.coordsystem.selector)
                with layout.row(True)(enabled=False):
                    self.coordsystem_selector.draw(layout)
    
    object = ObjectTransformPG | prop()
    mesh = MeshTransformPG | prop()
    curve = CurveTransformPG | prop()
    meta = MetaTransformPG | prop()
    lattice = LatticeTransformPG | prop()
    pose = PoseTransformPG | prop()
    bone = BoneTransformPG | prop()
    
    # Since Blender 2.73, grease pencil data is editable too
    grease = GreaseTransformPG | prop()
    
    # TODO: move this to a separate place
    # Cursor isn't aggregated, but it still might be useful
    # to see/manipulate it in non-global coordsystem
    cursor = CursorTransformPG | prop()
    
    def apply(self, tfm_aggr):
        summaries = [item[0] for item in self.summary_items if item[0] in self.summaries]
        
        mode = tfm_aggr.mode
        if mode.startswith('EDIT'):
            pass
        elif mode == 'POSE':
            #pass
            self.pose.apply(tfm_aggr, summaries)
        #else: # OBJECT and others
        elif mode == 'OBJECT':
            self.object.apply(tfm_aggr, summaries)
    
    def draw(self, layout):
        self.draw_coordsystem_selector(layout)
        
        with layout.row(True):
            for item in self.summary_items:
                if item[0] in self.summaries:
                    text = item[1]
                    if item[0] == 'active':
                        if self.uniformity == 'OFFSET': text = "+" + text
                        elif self.uniformity == 'PROPORTIONAL': text = "* " + text
                    op = layout.operator("object.batch_{}_summary".format(category_name), text=text)
                    op.index = self.index
                    op.summary = item[0]
                    op.title = item[1]
            
            if not self.summaries: layout.label(" ") # just to fill space
            
            with layout.row(True)(scale_x=1.0): # scale_x to prevent up/down arrows from appearing
                layout.prop_menu_enum(self, "summaries", text="", icon='DOTSDOWN')
        
        mode = bpy.context.mode
        if 'EDIT' in mode:
            pass
        elif mode == 'POSE':
            #pass
            self.pose.draw(layout, self.summaries)
        #else: # OBJECT and others
        elif mode == 'OBJECT':
            self.object.draw(layout, self.summaries)

@addon.PropertyGroup
class CategoryPG:
    transforms = [ContextTransformPG] | prop()
    
    selection_info = None
    
    def find_transform(self, screen, area):
        areas = screen.areas
        transforms = self.transforms
        is_v3d = (area.type == 'VIEW_3D')
        
        found = False
        searches = 2 # just to be sure there won't be an infinite loop
        while searches > 0:
            for i in range(len(areas)):
                if areas[i] != area: continue
                if i >= len(transforms): break
                transform = transforms[i]
                if transform.is_v3d != is_v3d: break
                transformExt = addon[transform]
                if not hasattr(transformExt, "area"): break
                if transformExt.area != area: break
                found = True
            if not found: self.transforms_ensure_order(screen)
            searches -= 1
        
        return (transform if found else None)
    
    def transforms_ensure_order(self, screen):
        areas = screen.areas
        transforms = self.transforms
        
        for i in range(len(areas)):
            area = areas[i]
            is_v3d = (area.type == 'VIEW_3D')
            
            while i < len(transforms):
                transform = transforms[i]
                transformExt = addon[transform]
                if not hasattr(transformExt, "area"):
                    transformExt.area = area # happens when .blend was loaded
                    break # (supposedly saved/loaded in the correct order)
                elif transformExt.area.regions:
                    break # area is valid
                transforms.remove(i) # remove invalid area's transform
            else:
                transform = transforms.add()
                transformExt = addon[transform]
                transformExt.area = area
            
            if transformExt.area != area:
                for j in range(i, len(transforms)):
                    transform = transforms[i]
                    transformExt = addon[transform]
                    if transformExt.area == area: break
                else: # not found
                    transform = transforms.add()
                    transformExt = addon[transform]
                    transformExt.area = area
                    j = len(transforms) - 1
                transform.is_v3d = is_v3d
                transform.index = i
                transforms.move(j, i)
            else:
                transform.is_v3d = is_v3d
                transform.index = i
        
        for i in range(len(transforms)-1, len(areas)-1, -1):
            transforms.remove(i) # remove extra transforms
    
    def draw(self, layout, context):
        layout = NestedLayout(layout, addon.module_name+".transform")
        
        transform = self.find_transform(context.screen, context.area)
        transform.draw(layout)

@addon.Menu(idname="OBJECT_MT_batch_{}_spatial_queries".format(category_name), label="Spatial queries", description="Spatial queries")
def Menu_Spatial_Queries(self, context):
    layout = NestedLayout(self.layout)
    layout.label("Distance 0D (to point)")
    layout.label("Distance 1D (to curve)")
    layout.label("Distance 2D (to surface)")
    layout.label("Distance 3D (to volume)")
    layout.label("Half-spaces")

@addon.Operator(idname="view3d.pick_{}".format(category_name_plural), options={'INTERNAL', 'REGISTER'}, description=
"Pick {}(s) from the object under mouse".format(Category_Name))
class Operator_Pick(Pick_Base):
    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT')
    
    def obj_to_info(self, obj):
        L, R, S = obj.matrix_world.decompose()
        L = "{:.5f}, {:.5f}, {:.5f}".format(*tuple(L))
        R = "{:.3f}, {:.3f}, {:.3f}".format(*tuple(math.degrees(axis) for axis in R.to_euler()))
        S = "{:.3f}, {:.3f}, {:.3f}".format(*tuple(S))
        return "Location: {}, Rotation: {}, Scale: {}".format(L, R, S)
    
    def on_confirm(self, context, obj):
        category = get_category()
        options = get_options()
        bpy.ops.ed.undo_push(message="Pick {}".format(Category_Name_Plural))
        #BatchOperations.copy(obj)
        self.report({'INFO'}, "{} copied".format(Category_Name_Plural))
        #BatchOperations.paste(options.iterate_objects(context), options.paste_mode)

# NOTE: only when 'REGISTER' is in bl_options and {'FINISHED'} is returned,
# the operator will be recorded in wm.operators and info reports

@addon.Operator(idname="object.batch_{}_copy".format(category_name), options={'INTERNAL'}, description=
"Click: Copy")
def Operator_Copy(self, context, event, object_name=""):
    active_obj = (bpy.data.objects.get(object_name) if object_name else context.object)
    if not active_obj: return
    category = get_category()
    options = get_options()
    # TODO ?

@addon.Operator(idname="object.batch_{}_paste".format(category_name), options={'INTERNAL', 'REGISTER'}, description=
"Click: Paste (+Ctrl: Override, +Shift: Add, +Alt: Filter)")
def Operator_Paste(self, context, event):
    category = get_category()
    options = get_options()
    # TODO ?
    return {'FINISHED'}

@addon.PropertyGroup
class CategoryOptionsPG:
    sync_3d_views = True | prop("Synchronize between 3D views")

@addon.Menu(idname="VIEW3D_MT_batch_{}_options".format(category_name_plural), label="Options", description="Options")
def Menu_Options(self, context):
    layout = NestedLayout(self.layout)
    options = get_options()
    layout.prop(options, "sync_3d_views", text="Sync 3D views")
    layout.label("Apply pos/rot/scale") # TODO
    layout.label("Set geometry origin") # TODO

@LeftRightPanel(idname="VIEW3D_PT_batch_{}".format(category_name_plural), space_type='VIEW_3D', category="Batch", label="Batch {}".format(Category_Name_Plural))
class Panel_Category:
    def draw(self, context):
        layout = NestedLayout(self.layout)
        category = get_category()
        options = get_options()
        transform = category.find_transform(context.screen, context.area)
        
        with layout.row():
            with layout.row(True):
                layout.menu("OBJECT_MT_batch_{}_spatial_queries".format(category_name), icon='BORDERMOVE', text="")
                layout.operator("view3d.pick_{}".format(category_name_plural), icon='EYEDROPPER', text="")
                layout.operator("object.batch_{}_copy".format(category_name), icon='COPYDOWN', text="")
                layout.operator("object.batch_{}_paste".format(category_name), icon='PASTEDOWN', text="")
            
            icon = transform.uniformity_icons[transform.uniformity]
            layout.prop_menu_enum(transform, "uniformity", text="", icon=icon)
            
            icon = 'SCRIPTWIN'
            layout.menu("VIEW3D_MT_batch_{}_options".format(category_name_plural), icon=icon, text="")
        
        category.draw(layout, context)

addon.type_extend("Screen", "batch_transforms", CategoryPG)
def get_category(context=None):
    if context is None: context = bpy.context
    return context.screen.batch_transforms

setattr(addon.Preferences, category_name_plural, CategoryOptionsPG | prop())
get_options = eval("lambda: addon.preferences.{}".format(category_name_plural))
